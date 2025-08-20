from __future__ import annotations

from typing import Union, List, Dict, Any, Iterable

import dask.dataframe as dd
import pandas as pd

from .log_utils import Logger


class DataUtils:
    """
    Helpers for transforming columns, safe emptiness checks, datetime coercion,
    and joining lookup data for Pandas or Dask DataFrames.
    """

    def __init__(self, logger: Logger | None = None, **kwargs: Any) -> None:
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.debug: bool = bool(kwargs.get("debug", False))

    # ---------- numeric / boolean transforms ----------

    @staticmethod
    def _transform_column_pandas(series: pd.Series, fill_value: Any, dtype: type) -> pd.Series:
        return pd.to_numeric(series, errors="coerce").fillna(fill_value).astype(dtype)

    def transform_numeric_columns(
        self,
        df: Union[pd.DataFrame, dd.DataFrame],
        columns: List[str],
        fill_value: Any = 0,
        dtype: type = int,
    ) -> Union[pd.DataFrame, dd.DataFrame]:
        """
        Convert selected columns to numeric → fillna → cast dtype.
        Works for Pandas and Dask (partition-wise).
        """
        if not columns:
            self.logger.warning("No columns specified for transform_numeric_columns.")
            return df

        cols = [c for c in columns if c in df.columns]
        if not cols:
            self.logger.warning("None of the requested columns exist in the DataFrame.")
            return df

        if isinstance(df, pd.DataFrame):
            for col in cols:
                df[col] = self._transform_column_pandas(df[col], fill_value, dtype)
            return df

        # Dask path
        for col in cols:
            df[col] = df[col].map_partitions(
                self._transform_column_pandas,
                fill_value,
                dtype,
                meta=(col, dtype),
            )
        return df

    def transform_boolean_columns(
        self,
        df: Union[pd.DataFrame, dd.DataFrame],
        columns: List[str],
        fill_value: Any = 0,
    ) -> Union[pd.DataFrame, dd.DataFrame]:
        """Convenience wrapper: cast to boolean via numeric→fillna→astype(bool)."""
        return self.transform_numeric_columns(df, columns, fill_value=fill_value, dtype=bool)

    # ---------- lookup merge ----------

    def merge_lookup_data(
        self,
        classname,
        df: Union[pd.DataFrame, dd.DataFrame],
        **kwargs: Any,
    ) -> Union[pd.DataFrame, dd.DataFrame]:
        """
        Merge lookup data for ids present in `source_col`.

        Required kwargs:
            - source_col
            - lookup_col
            - lookup_description_col
            - source_description_alias

        Optional kwargs:
            - fillna_source_description_alias: bool = False
            - fieldnames: tuple[str, str] = (lookup_col, lookup_description_col)
            - column_names: list[str] = ['temp_join_col', source_description_alias]
            - any other filters passed to `classname.load(...)`
        """
        # Early outs for emptiness and required args
        if self.is_dataframe_empty(df):
            self.logger.debug("merge_lookup_data: input DataFrame empty — nothing to merge.")
            return df

        required = ["source_col", "lookup_col", "lookup_description_col", "source_description_alias"]
        missing = [k for k in required if k not in kwargs]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

        source_col = kwargs.pop("source_col")
        lookup_col = kwargs.pop("lookup_col")
        lookup_description_col = kwargs.pop("lookup_description_col")
        source_description_alias = kwargs.pop("source_description_alias")

        fillna_alias = bool(kwargs.pop("fillna_source_description_alias", False))
        fieldnames = kwargs.pop("fieldnames", (lookup_col, lookup_description_col))
        column_names = kwargs.pop("column_names", ["temp_join_col", source_description_alias])

        if source_col not in df.columns:
            self.logger.debug(f"merge_lookup_data: '{source_col}' not found in frame — skipping merge.")
            return df

        # Collect ids safely
        try:
            ids_series = df[source_col].dropna()
            if isinstance(df, dd.DataFrame):
                # Dask: unique() is lazy → compute smallish result
                ids = ids_series.unique().compute()
            else:
                ids = ids_series.unique()
            ids = sorted(ids.tolist() if not isinstance(ids, list) else ids)
        except Exception as e:
            self.logger.error(f"merge_lookup_data: failed extracting ids from '{source_col}': {e}")
            return df

        if not ids:
            self.logger.debug(f"merge_lookup_data: no ids found in '{source_col}'.")
            return df

        # Load lookup data (expected to be small after filtering)
        load_kwargs = {
            **kwargs,
            "fieldnames": fieldnames,
            "column_names": column_names,
            f"{lookup_col}__in": ids,
        }

        lookup_instance = classname(debug=self.debug, logger=self.logger)
        result = lookup_instance.load(**load_kwargs)

        # If lookup returns Dask, compute to pandas (broadcastable) or keep small Dask?
        if isinstance(result, dd.DataFrame):
            # we expect this to be small after filtering by ids; materialize
            result = result.compute()

        if not isinstance(result, pd.DataFrame):
            raise TypeError("merge_lookup_data: lookup 'load' must return a pandas or dask DataFrame.")

        if result.empty:
            self.logger.debug("merge_lookup_data: lookup returned 0 rows — nothing to merge.")
            return df

        # Determine join key in the lookup result
        temp_join_col = "temp_join_col" if "temp_join_col" in column_names else lookup_col

        # Perform merge (Dask can merge with a small pandas right side)
        merged = df.merge(result, how="left", left_on=source_col, right_on=temp_join_col)

        if fillna_alias and source_description_alias in merged.columns:
            if isinstance(merged, dd.DataFrame):
                merged[source_description_alias] = merged[source_description_alias].fillna("")
            else:
                merged[source_description_alias] = merged[source_description_alias].fillna("")

        # Drop helper join column if present
        merged = merged.drop(columns="temp_join_col", errors="ignore")
        return merged

    # ---------- emptiness & datetime ----------

    def is_dataframe_empty(self, df: Union[pd.DataFrame, dd.DataFrame]) -> bool:
        """
        Safe emptiness check. For Dask, uses head(1) to avoid full compute.
        """
        if isinstance(df, dd.DataFrame):
            try:
                head = df.head(1, npartitions=-1, compute=True)
                return head.empty
            except Exception as e:
                self.logger.error(f"is_dataframe_empty: Dask head() failed: {e}")
                return False
        if isinstance(df, pd.DataFrame):
            return df.empty
        self.logger.error("is_dataframe_empty: input must be a pandas or dask DataFrame.")
        return False

    @staticmethod
    def convert_to_datetime_dask(df: dd.DataFrame, date_fields: Iterable[str]) -> dd.DataFrame:
        """
        Partition-wise datetime coercion with errors='coerce'.
        """
        for col in date_fields:
            if col in df.columns:
                df[col] = df[col].map_partitions(
                    pd.to_datetime, errors="coerce", meta=(col, "datetime64[ns]")
                )
        return df