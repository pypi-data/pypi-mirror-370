import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union, Tuple, Callable

import dask.dataframe as dd
import pandas as pd
from sqlalchemy import func, cast
from sqlalchemy.sql.sqltypes import Date, Time

from sibi_dst.utils import Logger


# -------------------- Deferred filter expression AST --------------------
class Expr:
    def mask(self, df: dd.DataFrame) -> dd.Series:
        raise NotImplementedError

    def to_parquet_filters(self) -> List[Union[Tuple[str, str, Any], List[Tuple[str, str, Any]]]]:
        # By default, nothing to push down
        return []

    def __and__(self, other: "Expr") -> "Expr": return And(self, other)
    def __or__(self, other: "Expr") -> "Expr":  return Or(self, other)
    def __invert__(self) -> "Expr":            return Not(self)


@dataclass(frozen=True)
class TrueExpr(Expr):
    """Matches all rows; useful as a neutral starting point."""
    def mask(self, df: dd.DataFrame) -> dd.Series:
        return df.map_partitions(lambda p: pd.Series(True, index=p.index),
                                 meta=pd.Series(dtype=bool))


@dataclass(frozen=True)
class ColOp(Expr):
    field: str
    casting: Optional[str]
    op: str
    value: Any
    handler: "FilterHandler"   # reuse your parsing + Dask ops

    def mask(self, df: dd.DataFrame) -> dd.Series:
        col = self.handler._get_dask_column(df, self.field, self.casting)
        val = self.handler._parse_filter_value(self.casting, self.value)
        return self.handler._apply_operation_dask(col, self.op, val)

    def to_parquet_filters(self):
        # Only basic comparisons can be pushed down
        if self.op not in {"exact", "gt", "gte", "lt", "lte", "in", "range"}:
            return []
        val = self.handler._parse_filter_value(self.casting, self.value)
        if self.casting == "date":
            if self.op == "range" and isinstance(val, (list, tuple)) and len(val) == 2:
                lo, hi = pd.Timestamp(val[0]), pd.Timestamp(val[1])
                return [(self.field, ">=", lo), (self.field, "<=", hi)]
            if isinstance(val, list):
                val = [pd.Timestamp(v) for v in val]
            else:
                val = pd.Timestamp(val)
        if self.op == "exact": return [(self.field, "=", val)]
        if self.op in {"gt","gte","lt","lte"}:
            sym = {"gt": ">", "gte": ">=", "lt": "<", "lte": "<="}[self.op]
            return [(self.field, sym, val)]
        if self.op == "in":   return [(self.field, "in", list(val) if not isinstance(val, list) else val)]
        if self.op == "range":
            lo, hi = val
            return [(self.field, ">=", lo), (self.field, "<=", hi)]
        return []


@dataclass(frozen=True)
class And(Expr):
    left: Expr; right: Expr
    def mask(self, df: dd.DataFrame) -> dd.Series: return self.left.mask(df) & self.right.mask(df)
    def to_parquet_filters(self):
        # AND = concatenate both sides' AND-terms
        return [*self.left.to_parquet_filters(), *self.right.to_parquet_filters()]


@dataclass(frozen=True)
class Or(Expr):
    left: Expr; right: Expr
    def mask(self, df: dd.DataFrame) -> dd.Series: return self.left.mask(df) | self.right.mask(df)
    def to_parquet_filters(self):
        # OR must be returned as list-of-lists; if either side has non-pushdown, defer to mask
        lf, rf = self.left.to_parquet_filters(), self.right.to_parquet_filters()
        if not lf or not rf:
            return []
        return [lf, rf]


@dataclass(frozen=True)
class Not(Expr):
    inner: Expr
    def mask(self, df: dd.DataFrame) -> dd.Series: return ~self.inner.mask(df)
    def to_parquet_filters(self): return []


# -------------------- Filter handler --------------------
class FilterHandler:
    """
    Handles the application of filters to SQLAlchemy and Dask backends.
    Also compiles dicts into deferred expressions (Expr) and can split
    pushdown-friendly predicates from residual ones.
    """
    def __init__(self, backend, logger=None, debug=False):
        self.backend = backend
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.logger.set_level(Logger.DEBUG if debug else Logger.INFO)
        self.backend_methods = self._get_backend_methods(backend)

    # --------- NEW: pushdown helpers ---------
    def _pushdown_ops(self) -> set[str]:
        """Ops that can be translated to PyArrow parquet filters."""
        return {"exact", "gt", "gte", "lt", "lte", "in", "range"}

    def to_parquet_filters(self, filters: Optional[Dict[str, Any]] = None
                           ) -> List[Tuple[str, str, Any]]:
        """
        Convert a subset of filters into PyArrow parquet filters (AND semantics).
        Unsupported ops are skipped here and should be applied later as a Dask mask.
        """
        filters = filters or {}
        out: List[Tuple[str, str, Any]] = []

        for key, value in filters.items():
            field, casting, op = self._parse_filter_key(key)
            if op not in self._pushdown_ops():
                continue

            val = self._parse_filter_value(casting, value)

            # Normalize dates to Timestamp for Arrow
            if casting == "date":
                if op == "range" and isinstance(val, (list, tuple)) and len(val) == 2:
                    lo, hi = pd.Timestamp(val[0]), pd.Timestamp(val[1])
                    out.extend([(field, ">=", lo), (field, "<=", hi)])
                    continue
                if isinstance(val, list):
                    val = [pd.Timestamp(v) for v in val]
                else:
                    val = pd.Timestamp(val)

            if op == "exact":
                out.append((field, "=", val))
            elif op in {"gt", "gte", "lt", "lte"}:
                sym = {"gt": ">", "gte": ">=", "lt": "<", "lte": "<="}[op]
                out.append((field, sym, val))
            elif op == "in":
                out.append((field, "in", list(val) if not isinstance(val, list) else val))
            elif op == "range":
                lo, hi = val
                out.extend([(field, ">=", lo), (field, "<=", hi)])

        return out

    def split_pushdown_and_residual(self, filters: Dict[str, Any]
                                    ) -> Tuple[List[Tuple[str, str, Any]], Dict[str, Any]]:
        """
        Split input filter dict into:
          - parquet_filters: list of (col, op, val) tuples for dd.read_parquet(..., filters=...)
          - residual_filters: dict to be applied later via a Dask boolean mask
        """
        push_keys = set()
        for key in filters.keys():
            _, casting, op = self._parse_filter_key(key)
            if op in self._pushdown_ops():
                push_keys.add(key)

        pushdown_subset = {k: filters[k] for k in push_keys}
        parquet_filters = self.to_parquet_filters(pushdown_subset)
        residual_filters = {k: v for k, v in filters.items() if k not in push_keys}
        return parquet_filters, residual_filters

    # --------- Expression compiler / mask builder ---------
    def compile_filters(self, filters: Optional[Dict[str, Any]] = None) -> Expr:
        """
        Compile a dict into a deferred expression tree (no df required).
        Supports boolean forms: {"$and": [...]}, {"$or": [...]}, {"$not": {...}}.
        Default combination for plain dicts: AND of all terms.
        """
        filters = filters or {}
        if not filters:
            return TrueExpr()

        # boolean forms
        if "$and" in filters:
            expr = TrueExpr()
            for sub in filters["$and"]:
                expr = expr & self.compile_filters(sub)
            return expr

        if "$or" in filters:
            subs = [self.compile_filters(sub) for sub in filters["$or"]]
            if not subs: return TrueExpr()
            expr = subs[0]
            for s in subs[1:]:
                expr = expr | s
            return expr

        if "$not" in filters:
            return ~self.compile_filters(filters["$not"])

        # plain dict => AND across keys
        expr: Expr = TrueExpr()
        for key, value in filters.items():
            field, casting, op = self._parse_filter_key(key)
            expr = expr & ColOp(field=field, casting=casting, op=op, value=value, handler=self)
        return expr

    def build_mask_fn(self, filters: Optional[Dict[str, Any]] = None) -> Callable[[dd.DataFrame], dd.Series]:
        """Return a callable (df -> boolean mask) without touching df now."""
        expr = self.compile_filters(filters)
        def _fn(df: dd.DataFrame) -> dd.Series:
            return expr.mask(df)
        return _fn

    # --------- Existing “apply now” API (kept as-is) ---------
    def apply_filters(self, query_or_df, model=None, filters=None):
        filters = filters or {}
        for key, value in filters.items():
            field_name, casting, operation = self._parse_filter_key(key)
            parsed_value = self._parse_filter_value(casting, value)
            if self.backend == "sqlalchemy":
                column = self.backend_methods["get_column"](field_name, model, casting)
                condition = self.backend_methods["apply_operation"](column, operation, parsed_value)
                query_or_df = self.backend_methods["apply_condition"](query_or_df, condition)
            elif self.backend == "dask":
                column = self.backend_methods["get_column"](query_or_df, field_name, casting)
                condition = self.backend_methods["apply_operation"](column, operation, parsed_value)
                query_or_df = self.backend_methods["apply_condition"](query_or_df, condition)
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")
        return query_or_df

    # --------- Parsing & backend plumbing (unchanged) ---------
    @staticmethod
    def _parse_filter_key(key):
        parts = key.split("__")
        field_name = parts[0]
        casting = None
        operation = "exact"

        if len(parts) == 3:
            _, casting, operation = parts
        elif len(parts) == 2:
            if parts[1] in FilterHandler._comparison_operators():
                operation = parts[1]
            elif parts[1] in FilterHandler._dt_operators() + FilterHandler._date_operators():
                casting = parts[1]

        return field_name, casting, operation

    def _parse_filter_value(self, casting, value):
        if casting == "date":
            if isinstance(value, str):
                return pd.Timestamp(value)
            if isinstance(value, list):
                return [pd.Timestamp(v) for v in value]
        elif casting == "time":
            # convert to seconds since midnight
            if isinstance(value, list):
                return [self._time_to_seconds(v) for v in value]
            return self._time_to_seconds(value)
        return value

    @staticmethod
    def _get_backend_methods(backend):
        if backend == "sqlalchemy":
            return {
                "get_column": FilterHandler._get_sqlalchemy_column,
                "apply_operation": FilterHandler._apply_operation_sqlalchemy,
                "apply_condition": lambda query, condition: query.filter(condition),
            }
        elif backend == "dask":
            return {
                "get_column": FilterHandler._get_dask_column,
                "apply_operation": FilterHandler._apply_operation_dask,
                "apply_condition": lambda df, condition: df[condition],
            }
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    @staticmethod
    def _get_sqlalchemy_column(field_name, model, casting):
        column = getattr(model, field_name, None)
        if not column:
            raise AttributeError(f"Field '{field_name}' not found in model '{model.__name__}'")

        if casting == "date":
            column = cast(column, Date)
        elif casting == "time":
            column = cast(column, Time)
        elif casting in FilterHandler._date_operators():
            column = func.extract(casting, column)

        return column

    @staticmethod
    def _get_dask_column(df, field_name, casting):
        needs_dt = casting in (FilterHandler._dt_operators() + FilterHandler._date_operators())
        column = dd.to_datetime(df[field_name], errors="coerce") if needs_dt else df[field_name]

        if needs_dt:
            column = FilterHandler._strip_tz(column)

        if casting == "date":
            column = column.dt.floor("D")
        elif casting == "time":
            # compare as "seconds since midnight"
            column = (column.dt.hour * 3600 + column.dt.minute * 60 + column.dt.second)
        elif casting in FilterHandler._date_operators():
            attr = "weekday" if casting == "week_day" else casting
            column = getattr(column.dt, attr)

        return column

    @staticmethod
    def _apply_operation_sqlalchemy(column, operation, value):
        operation_map = FilterHandler._operation_map_sqlalchemy()
        if operation not in operation_map:
            raise ValueError(f"Unsupported operation: {operation}")
        return operation_map[operation](column, value)

    @staticmethod
    def _apply_operation_dask(column, operation, value):
        operation_map = FilterHandler._operation_map_dask()
        if operation not in operation_map:
            raise ValueError(f"Unsupported operation: {operation}")
        return operation_map[operation](column, value)

    @staticmethod
    def _operation_map_sqlalchemy():
        return {
            "exact": lambda col, val: col == val,
            "gt": lambda col, val: col > val,
            "gte": lambda col, val: col >= val,
            "lt": lambda col, val: col < val,
            "lte": lambda col, val: col <= val,
            "in": lambda col, val: col.in_(val),
            "range": lambda col, val: col.between(val[0], val[1]),
            "contains": lambda col, val: col.like(f"%{val}%"),
            "startswith": lambda col, val: col.like(f"{val}%"),
            "endswith": lambda col, val: col.like(f"%{val}"),
            "isnull": lambda col, val: col.is_(None) if val else col.isnot(None),
            "not_exact": lambda col, val: col != val,
            "not_contains": lambda col, val: ~col.like(f"%{val}%"),
            "not_in": lambda col, val: ~col.in_(val),
            "regex": lambda col, val: col.op("~")(val),
            "icontains": lambda col, val: col.ilike(f"%{val}%"),
            "istartswith": lambda col, val: col.ilike(f"{val}%"),
            "iendswith": lambda col, val: col.ilike(f"%{val}"),
            "iexact": lambda col, val: col.ilike(val),
            "iregex": lambda col, val: col.op("~*")(val),
        }

    @staticmethod
    def _operation_map_dask():
        return {
            "exact": lambda col, val: col == val,
            "gt": lambda col, val: col > val,
            "gte": lambda col, val: col >= val,
            "lt": lambda col, val: col < val,
            "lte": lambda col, val: col <= val,

            # type-safe "in" and "not_in"
            "in": lambda col, val: FilterHandler._align_in_types(col, val)[0].isin(
                FilterHandler._align_in_types(col, val)[1]),
            "not_in": lambda col, val: ~FilterHandler._align_in_types(col, val)[0].isin(
                FilterHandler._align_in_types(col, val)[1]),

            "range": lambda col, val: (col >= val[0]) & (col <= val[1]),

            # robust string ops (dtype-agnostic)
            "contains": lambda col, val: FilterHandler._as_str(col).str.contains(val, regex=True, na=False),
            "startswith": lambda col, val: FilterHandler._as_str(col).str.startswith(val, na=False),
            "endswith": lambda col, val: FilterHandler._as_str(col).str.endswith(val, na=False),
            "not_contains": lambda col, val: ~FilterHandler._as_str(col).str.contains(val, regex=True, na=False),
            "regex": lambda col, val: FilterHandler._as_str(col).str.contains(val, regex=True, na=False),
            "icontains": lambda col, val: FilterHandler._as_str(col).str.contains(val, case=False, regex=True, na=False),
            "istartswith": lambda col, val: FilterHandler._as_str(col).str.lower().str.startswith(str(val).lower(), na=False),
            "iendswith": lambda col, val: FilterHandler._as_str(col).str.lower().str.endswith(str(val).lower(), na=False),
            "iexact": lambda col, val: FilterHandler._as_str(col).str.lower() == str(val).lower(),
            "iregex": lambda col, val: FilterHandler._as_str(col).str.contains(val, case=False, regex=True, na=False),

            "isnull": lambda col, val: col.isnull() if val else col.notnull(),
            "not_exact": lambda col, val: col != val,
        }

    @staticmethod
    def _as_str(col):
        return col.astype("string").fillna("")

    @staticmethod
    def _strip_tz(col):
        import pandas as pd
        def _part(s: pd.Series) -> pd.Series:
            try:
                return s.dt.tz_convert("UTC").dt.tz_localize(None)
            except Exception:
                try:
                    return s.dt.tz_localize(None)
                except Exception:
                    return s
        return col.map_partitions(_part, meta=col._meta)

    @staticmethod
    def _time_to_seconds(t):
        if isinstance(t, str):
            t = datetime.time.fromisoformat(t)
        return t.hour * 3600 + t.minute * 60 + t.second

    @staticmethod
    def _dt_operators():
        return ["date", "time"]

    @staticmethod
    def _date_operators():
        return ["year", "month", "day", "hour", "minute", "second", "week_day"]

    @staticmethod
    def _comparison_operators():
        return [
            "gte", "lte", "gt", "lt", "exact", "in", "range",
            "contains", "startswith", "endswith", "isnull",
            "not_exact", "not_contains", "not_in",
            "regex", "icontains", "istartswith", "iendswith",
            "iexact", "iregex"
        ]

    @staticmethod
    def _align_in_types(col, val):
        # normalize val to a list
        if isinstance(val, (set, tuple)):
            vals = list(val)
        elif isinstance(val, list):
            vals = val
        else:
            vals = [val]

        kind = getattr(getattr(col, "dtype", None), "kind", None)
        if kind in ("i", "u"):  # integer
            def to_ints(xs):
                out = []
                for x in xs:
                    try:
                        out.append(int(x))
                    except Exception:
                        return None
                return out
            ints = to_ints(vals)
            if ints is not None:
                return col.astype("Int64"), ints

        if kind in ("f",):  # float
            def to_floats(xs):
                out = []
                for x in xs:
                    try:
                        out.append(float(x))
                    except Exception:
                        return None
                return out
            flts = to_floats(vals)
            if flts is not None:
                return col.astype("float64"), flts

        return FilterHandler._as_str(col), [str(x) for x in vals]
