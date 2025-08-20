import datetime
import itertools
import dask.dataframe as dd
import pandas as pd
from sqlalchemy import func, cast
from sqlalchemy.sql.sqltypes import Date, Time
from sibi_dst.v2.utils import Logger
import typing


class FilterHandler:
    """
    Handles the application of filters to data sources with support for SQLAlchemy, SQLModel, and Dask backends.

    This class abstracts the process of applying filters to various backends, specifically
    SQLAlchemy/SQLModel queries and Dask DataFrames. It supports multiple filtering operations,
    including exact matches, comparisons, and string-related operations such as contains and regex.
    """

    def __init__(self, backend, logger=None, debug=False):
        """
        Initialize the FilterHandler.

        Args:
            backend: The backend to use ('sqlalchemy', 'sqlmodel', or 'dask').
            logger: Optional logger for debugging purposes.
        """
        self.backend = backend
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.logger.set_level(Logger.DEBUG if debug else Logger.INFO)
        self.backend_methods = self._get_backend_methods(backend)

    def apply_filters(self, query_or_df, model=None, filters=None):
        """
        Apply filters to the data source based on the backend.

        Args:
            query_or_df: A SQLAlchemy/SQLModel query or Dask DataFrame.
            model: SQLAlchemy/SQLModel model (required for SQLAlchemy/SQLModel backend).
            filters: Dictionary of filters.

        Returns:
            Filtered query or DataFrame.
        """
        filters = filters or {}
        for key, value in filters.items():
            field_name, casting, operation = self._parse_filter_key(key)
            parsed_value = self._parse_filter_value(casting, value)
            # For both SQLAlchemy and SQLModel, use the same backend methods.
            if self.backend in ("sqlalchemy", "sqlmodel"):
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
        """
        Convert filter value to an appropriate type based on the casting (e.g., date).
        """
        if casting == "date":
            if isinstance(value, str):
                return pd.Timestamp(value)  # Convert to datetime64[ns]
            if isinstance(value, list):
                return [pd.Timestamp(v) for v in value]
        elif casting == "time" and isinstance(value, str):
            parsed = datetime.time.fromisoformat(value)
            self.logger.debug(f"Parsed value (time): {parsed}")
            return parsed
        return value

    @staticmethod
    def _get_backend_methods(backend):
        if backend in ("sqlalchemy", "sqlmodel"):
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
        """
        Retrieve and cast a column for SQLAlchemy/SQLModel based on the field name and casting.

        Args:
            field_name: The name of the field/column.
            model: The SQLAlchemy/SQLModel model.
            casting: The casting type ('date', 'time', etc.).

        Returns:
            The SQLAlchemy column object, optionally cast or transformed.
        """
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
        """
        Retrieve and optionally cast a column for Dask based on the field name and casting.

        Args:
            df: The Dask DataFrame.
            field_name: The name of the field/column.
            casting: The casting type ('date', 'time', etc.).

        Returns:
            The Dask Series, optionally cast or transformed.
        """
        column = dd.to_datetime(df[field_name], errors="coerce") if casting in FilterHandler._dt_operators() else df[field_name]
        if casting == "date":
            column = column.dt.floor("D")
        elif casting in FilterHandler._date_operators():
            column = getattr(column.dt, casting)
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
            "in": lambda col, val: col.isin(val),
            "range": lambda col, val: (col >= val[0]) & (col <= val[1]),
            "contains": lambda col, val: col.str.contains(val, regex=True),
            "startswith": lambda col, val: col.str.startswith(val),
            "endswith": lambda col, val: col.str.endswith(val),
            "isnull": lambda col, val: col.isnull() if val else col.notnull(),
            "not_exact": lambda col, val: col != val,
            "not_contains": lambda col, val: ~col.str.contains(val, regex=True),
            "not_in": lambda col, val: ~col.isin(val),
            "regex": lambda col, val: col.str.contains(val, regex=True),
            "icontains": lambda col, val: col.str.contains(val, case=False, regex=True),
            "istartswith": lambda col, val: col.str.startswith(val, case=False),
            "iendswith": lambda col, val: col.str.endswith(val, case=False),
            "iexact": lambda col, val: col.str.contains(f"^{val}$", case=False, regex=True),
            "iregex": lambda col, val: col.str.contains(val, case=False, regex=True),
        }

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