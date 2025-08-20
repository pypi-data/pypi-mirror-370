import warnings
from typing import Union, List, Dict, Tuple, Iterable

import dask.dataframe as dd
import pandas as pd

from .log_utils import Logger

warnings.filterwarnings("ignore", message="Sorting a Dask DataFrame is expensive and may not be efficient")


class DfUtils:
    """
    Utilities that work with both pandas and Dask DataFrames, with Dask-first behavior.
    """

    def __init__(self, logger=None, *, debug: bool = False):
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.debug = debug

    # -------------------------
    # helpers
    # -------------------------
    @staticmethod
    def _is_dask(obj) -> bool:
        return isinstance(obj, (dd.DataFrame, dd.Series))

    @classmethod
    def compute_to_list(cls, series):
        return series.compute().tolist() if hasattr(series, "compute") else series.tolist()

    def _astype_safe(self, df, col: str, dtype) -> None:
        """
        Cast a single column in-place; handles Dask meta generation implicitly by letting Dask infer.
        """
        if col not in df.columns:
            return
        if self._is_dask(df):
            df[col] = df[col].astype(dtype)
        else:
            df[col] = df[col].astype(dtype)

    def _df_len_zero(self, df) -> bool:
        """
        Dask-safe emptiness check (avoids df.empty with Dask).
        """
        if self._is_dask(df):
            try:
                # Much faster than materializing the whole df
                n = df.map_partitions(len).sum().compute()
                return int(n) == 0
            except Exception as e:
                self.logger.error(f"Error computing Dask length: {e}")
                return False
        return df.empty

    # -------------------------
    # public API
    # -------------------------
    def extract_unique_values(self, df, *columns):
        result: Dict[str, List] = {}
        for col in columns:
            if col not in df.columns:
                result[col] = []
                continue
            vals = df[col].dropna()
            # Prefer drop_duplicates over unique() for Dask robustness
            if self._is_dask(vals):
                vals = vals.drop_duplicates().compute()
            else:
                vals = vals.drop_duplicates()
            result[col] = vals.tolist()
        return result

    def align_and_merge_by_type(self, df_left, df_right, type_mapping: Dict[str, Iterable[Tuple[str, str]]], how='left'):
        """
        Align dtypes for pairs of columns then merge on aligned pairs.
        type_mapping example:
        {
          'integer': [('customer_id','temp1'), ('product_type_id','temp2')],
          'string':  [('group2','temp4')],
          'datetime':[('ts','ts2')],
          'boolean':[('is_ok','flag')]
        }
        """
        dtype_map = {
            'integer': 'int64',
            'float': 'float64',
            'string': 'string',
            'datetime': 'datetime64[ns]',
            'boolean': 'bool',
        }

        # Cast columns as requested
        for target_type, pairs in (type_mapping or {}).items():
            if target_type not in dtype_map:
                self.logger.error(f"Unsupported type: {target_type}")
                continue
            for left_col, right_col in pairs:
                if left_col in df_left.columns:
                    self._astype_safe(df_left, left_col, dtype_map[target_type])
                if right_col in df_right.columns:
                    self._astype_safe(df_right, right_col, dtype_map[target_type])

        all_pairs = [p for pairs in (type_mapping or {}).values() for p in pairs]
        left_keys = [p[0] for p in all_pairs]
        right_keys = [p[1] for p in all_pairs]

        # Dask merge works fine if both are Dask; if mixed, coerce right to Dask for scalability.
        if self._is_dask(df_left) and not self._is_dask(df_right):
            df_right = dd.from_pandas(df_right, npartitions=max(1, df_left.npartitions))
        if self._is_dask(df_right) and not self._is_dask(df_left):
            df_left = dd.from_pandas(df_left, npartitions=max(1, df_right.npartitions))

        return df_left.merge(df_right, how=how, left_on=left_keys, right_on=right_keys)

    def exclude_from_dataframe(self, df, conditions: List[Tuple[str, str, object]]):
        """
        Filter rows out based on combined conditions (AND). Returns df[~combined].
        conditions: list of (column, operator, value)
        operators supported: ==, !=, <, <=, >, >=
        """
        import operator
        ops = {"==": operator.eq, "!=": operator.ne, "<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}

        if not conditions:
            return df

        missing = [c for c, _, _ in conditions if c not in df.columns]
        if missing:
            self.logger.debug(f"Missing columns in DataFrame: {', '.join(missing)}")
            return df

        combined = None
        for col, op, val in conditions:
            if op not in ops:
                raise ValueError(f"Unsupported operator: {op}")
            cond = ops[op](df[col], val)
            combined = cond if combined is None else (combined & cond)

        if combined is None:
            return df
        return df[~combined]

    # ---- numeric/boolean casting
    @staticmethod
    def _transform_column(series, fill_value, dtype):
        return pd.to_numeric(series, errors="coerce").fillna(fill_value).astype(dtype)

    def transform_numeric_columns(self, df: Union[pd.DataFrame, dd.DataFrame], columns: List[str], fill_value=0, dtype=int):
        if not columns:
            self.logger.warning("No columns specified.")
            return df
        columns = [c for c in columns if c in df.columns]
        for col in columns:
            if self._is_dask(df):
                df[col] = df[col].map_partitions(self._transform_column, fill_value, dtype, meta=(col, dtype))
            else:
                df[col] = self._transform_column(df[col], fill_value, dtype)
        return df

    # kept for backward-compat
    def transform_numeric_cols(self, df, columns, fill_value=0, dtype=int):
        return self.transform_numeric_columns(df, columns, fill_value=fill_value, dtype=dtype)

    def transform_boolean_columns(self, df: Union[pd.DataFrame, dd.DataFrame], columns: List[str], fill_value=0):
        return self.transform_numeric_columns(df, columns, fill_value=fill_value, dtype=bool)

    # ---- duplicate handling
    def eval_duplicate_removal(self, df, duplicate_expr, sort_field: str | None = None, keep='last', debug=False):
        """
        Drop duplicates. For Dask, uses its shuffle-based drop_duplicates.
        If sort_field is provided, we avoid global sorts for Dask.
        """
        if duplicate_expr is None:
            return df

        if debug:
            try:
                dups = df[df.duplicated(subset=duplicate_expr)]
                # Do not .compute() here; just log that duplicates exist in Dask
                self.logger.debug(f"Duplicate rows based on {duplicate_expr}: (preview only)")
                if not self._is_dask(dups):
                    self.logger.debug(f"\n{dups}")
            except Exception:
                pass

        if sort_field:
            if self._is_dask(df):
                self.logger.warning("Sorting a Dask DataFrame is expensive; skipping global sort.")
            else:
                df = df.sort_values(sort_field)

        if self._is_dask(df):
            # Let Dask handle the global de-dup with a shuffle under the hood
            df = df.drop_duplicates(subset=duplicate_expr, keep=keep)
        else:
            df = df.drop_duplicates(subset=duplicate_expr, keep=keep)
        return df

    def load_latest(self, df, duplicate_expr, sort_field=None, debug=False):
        return self.eval_duplicate_removal(df, duplicate_expr, sort_field=sort_field, keep='last', debug=debug)

    def load_earliest(self, df, duplicate_expr, sort_field=None, debug=False):
        return self.eval_duplicate_removal(df, duplicate_expr, sort_field=sort_field, keep='first', debug=debug)

    # ---- totals
    def add_df_totals(self, df):
        """
        Adds totals; for Dask, this computes to pandas (be careful with large frames).
        """
        if self._is_dask(df):
            self.logger.warning("add_df_totals will compute to pandas; may be large.")
            col_totals = df.sum(numeric_only=True).compute()
            row_totals = df.sum(axis=1, numeric_only=True).compute()
            pdf = df.compute()
            pdf.loc['Total'] = col_totals
            pdf['Total'] = row_totals
            return pdf
        else:
            df.loc['Total'] = df.sum(numeric_only=True)
            df['Total'] = df.sum(axis=1, numeric_only=True)
            return df

    # ---- summarization / resampling
    def summarise_data(self, df, summary_column, values_column, rule='D', agg_func='count'):
        """
        For pandas: pivot+resample on DatetimeIndex.
        For Dask: create time bins and aggregate in Dask, then (optionally) pivot in pandas.
        """
        # pandas path
        if not self._is_dask(df):
            idx = df.index
            if not isinstance(idx, pd.DatetimeIndex):
                self.logger.warning("Index is not DatetimeIndex; converting from current index.")
                df = df.copy()
                df.index = pd.to_datetime(idx, errors="coerce")
            pivot = df.pivot_table(index=df.index, columns=summary_column, values=values_column, aggfunc=agg_func).fillna(0)
            return pivot.resample(rule).sum()

        # Dask path
        # 1) Build a datetime column from index (no global sort)
        ddf = df
        ddf = ddf.assign(_ts_bin=dd.to_datetime(ddf.index, errors="coerce"))

        # 2) Bucket to rule using floor; do it per partition
        def _floor_partition(pdf: pd.DataFrame, col: str, rule: str) -> pd.DataFrame:
            out = pdf.copy()
            out[col] = pd.to_datetime(out[col], errors="coerce")
            out['_bin'] = out[col].dt.floor(rule)
            return out

        ddf = ddf.map_partitions(_floor_partition, col="_ts_bin", rule=rule, meta=dd.utils.make_meta(ddf))

        # 3) Group in Dask on ['_bin', summary_column] and aggregate
        grouped = ddf.groupby(['_bin', summary_column])[values_column].agg(agg_func).reset_index()

        # 4) If you need a pivoted result, compute to pandas then pivot (Dask pivot_table is not generally supported)
        gpdf = grouped.compute()
        pivot = gpdf.pivot_table(index="_bin", columns=summary_column, values=values_column, aggfunc='sum').fillna(0)

        # 5) Ensure regular resample (already bucketed; resampling is now cheap in pandas)
        pivot.index = pd.to_datetime(pivot.index)
        return pivot.asfreq(rule, fill_value=0)