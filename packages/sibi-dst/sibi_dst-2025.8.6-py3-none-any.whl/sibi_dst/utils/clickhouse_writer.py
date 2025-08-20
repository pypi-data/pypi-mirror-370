from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import ClassVar, Dict, Optional, Any, Iterable, Tuple

import pandas as pd
import dask.dataframe as dd
import clickhouse_connect

from . import ManagedResource


class ClickHouseWriter(ManagedResource):
    """
    Write a Dask DataFrame to ClickHouse with:
      - Safe Dask checks (no df.empty)
      - Nullable dtype mapping
      - Optional overwrite (drop + recreate)
      - Partitioned, batched inserts
      - Per-thread clients to avoid session conflicts
    """

    # Default dtype mapping (pandas/dask → ClickHouse)
    DTYPE_MAP: ClassVar[Dict[str, str]] = {
        "int64": "Int64",
        "Int64": "Int64",  # pandas nullable Int64
        "int32": "Int32",
        "Int32": "Int32",
        "float64": "Float64",
        "Float64": "Float64",
        "float32": "Float32",
        "bool": "UInt8",
        "boolean": "UInt8",
        "object": "String",
        "string": "String",
        "category": "String",
        "datetime64[ns]": "DateTime",
        "datetime64[ns, UTC]": "DateTime",
    }

    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 8123,
        database: str = "sibi_data",
        user: str = "default",
        password: str = "",
        table: str = "test_sibi_table",
        order_by: str = "id",
        engine: Optional[str] = None,  # e.g. "ENGINE MergeTree ORDER BY (`id`)"
        max_workers: int = 4,
        insert_chunksize: int = 50_000,
        overwrite: bool = False,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.host = host
        self.port = int(port)
        self.database = database
        self.user = user
        self.password = password
        self.table = table
        self.order_by = order_by
        self.engine = engine  # if None → default MergeTree ORDER BY
        self.max_workers = int(max_workers)
        self.insert_chunksize = int(insert_chunksize)
        self.overwrite = bool(overwrite)

        # one client per thread to avoid session contention
        self._tlocal = threading.local()

    # ------------- public -------------

    def save_to_clickhouse(self, df: dd.DataFrame, *, overwrite: Optional[bool] = None) -> None:
        """
        Persist a Dask DataFrame into ClickHouse.

        Args:
            df: Dask DataFrame
            overwrite: Optional override for dropping/recreating table
        """
        if not isinstance(df, dd.DataFrame):
            raise TypeError("ClickHouseWriter.save_to_clickhouse expects a dask.dataframe.DataFrame.")

        # small, cheap check: head(1) to detect empty
        head = df.head(1, npartitions=-1, compute=True)
        if head.empty:
            self.logger.info("Dask DataFrame appears empty (head(1) returned 0 rows). Nothing to write.")
            return

        # lazily fill missing values per-partition (no global compute)
        df = df.map_partitions(type(self)._fill_missing_partition, meta=df._meta)

        # (re)create table
        ow = self.overwrite if overwrite is None else bool(overwrite)
        dtypes = df._meta_nonempty.dtypes  # metadata-only types (no compute)
        schema_sql = self._generate_clickhouse_schema(dtypes)
        engine_sql = self._default_engine_sql() if not self.engine else self.engine

        if ow:
            self._command(f"DROP TABLE IF EXISTS {self._ident(self.table)}")
            self.logger.info(f"Dropped table {self.table} (overwrite=True)")

        create_sql = f"CREATE TABLE IF NOT EXISTS {self._ident(self.table)} ({schema_sql}) {engine_sql};"
        self._command(create_sql)
        self.logger.info(f"Ensured table {self.table} exists")

        # write partitions concurrently
        parts = list(df.to_delayed())
        if not parts:
            self.logger.info("No partitions to write.")
            return

        self.logger.info(f"Writing {len(parts)} partitions to ClickHouse (max_workers={self.max_workers})")
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(self._write_one_partition, part, idx): idx for idx, part in enumerate(parts)}
            for fut in as_completed(futures):
                idx = futures[fut]
                try:
                    fut.result()
                except Exception as e:
                    self.logger.error(f"Partition {idx} failed: {e}", exc_info=self.debug)
                    raise

        self.logger.info(f"Completed writing {len(parts)} partitions to {self.table}")

    # ------------- schema & types -------------

    def _generate_clickhouse_schema(self, dask_dtypes: pd.Series) -> str:
        cols: Iterable[Tuple[str, Any]] = dask_dtypes.items()
        pieces = []
        for col, dtype in cols:
            ch_type = self._map_dtype(dtype)
            # Use Nullable for non-numeric/string columns that may carry NaN/None,
            # and for datetimes to be safe with missing values.
            if self._should_mark_nullable(dtype):
                ch_type = f"Nullable({ch_type})"
            pieces.append(f"{self._ident(col)} {ch_type}")
        return ", ".join(pieces)

    def _map_dtype(self, dtype: Any) -> str:
        # Handle pandas extension dtypes explicitly
        if isinstance(dtype, pd.Int64Dtype):
            return "Int64"
        if isinstance(dtype, pd.Int32Dtype):
            return "Int32"
        if isinstance(dtype, pd.BooleanDtype):
            return "UInt8"
        if isinstance(dtype, pd.Float64Dtype):
            return "Float64"
        if isinstance(dtype, pd.StringDtype):
            return "String"
        if "datetime64" in str(dtype):
            return "DateTime"

        return self.DTYPE_MAP.get(str(dtype), "String")

    def _should_mark_nullable(self, dtype: Any) -> bool:
        s = str(dtype)
        if isinstance(dtype, (pd.StringDtype, pd.BooleanDtype, pd.Int64Dtype, pd.Int32Dtype, pd.Float64Dtype)):
            return True
        if "datetime64" in s:
            return True
        # object/category almost always nullable
        if s in ("object", "category", "string"):
            return True
        return False

    def _default_engine_sql(self) -> str:
        # minimal MergeTree clause; quote order_by safely
        ob = self.order_by if self.order_by.startswith("(") else f"(`{self.order_by}`)"
        return f"ENGINE = MergeTree ORDER BY {ob}"

    # ------------- partition write -------------

    def _write_one_partition(self, part, index: int) -> None:
        # Compute partition → pandas
        pdf: pd.DataFrame = part.compute()
        if pdf.empty:
            self.logger.debug(f"Partition {index} empty; skipping")
            return

        # Ensure column ordering is stable
        cols = list(pdf.columns)

        # Split into batches (to avoid giant single insert)
        for start in range(0, len(pdf), self.insert_chunksize):
            batch = pdf.iloc[start:start + self.insert_chunksize]
            if batch.empty:
                continue
            self._insert_df(cols, batch)

        self.logger.debug(f"Partition {index} inserted ({len(pdf)} rows)")

    def _insert_df(self, cols: Iterable[str], df: pd.DataFrame) -> None:
        client = self._get_client()
        # clickhouse-connect supports insert_df
        client.insert_df(self.table, df[cols], settings={"async_insert": 1, "wait_end_of_query": 1})

    # ------------- missing values (lazy) -------------

    @staticmethod
    def _fill_missing_partition(pdf: pd.DataFrame) -> pd.DataFrame:
        # (unchanged body)
        for col in pdf.columns:
            s = pdf[col]
            if pd.api.types.is_integer_dtype(s.dtype):
                if pd.api.types.is_extension_array_dtype(s.dtype):
                    pdf[col] = s.fillna(pd.NA)
                else:
                    pdf[col] = s.fillna(0)
            elif pd.api.types.is_bool_dtype(s.dtype):
                pdf[col] = s.fillna(pd.NA)
            elif pd.api.types.is_float_dtype(s.dtype):
                pdf[col] = s.fillna(0.0)
            elif pd.api.types.is_datetime64_any_dtype(s.dtype):
                pass
            else:
                pdf[col] = s.fillna("")
        return pdf

    # ------------- low-level helpers -------------

    def _get_client(self):
        cli = getattr(self._tlocal, "client", None)
        if cli is not None:
            return cli
        cli = clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            database=self.database,
            username=self.user,  # clickhouse-connect uses 'username'
            password=self.password,
        )
        self._tlocal.client = cli
        return cli

    def _command(self, sql: str) -> None:
        client = self._get_client()
        client.command(sql)

    @staticmethod
    def _ident(name: str) -> str:
        # minimal identifier quoting
        if name.startswith("`") and name.endswith("`"):
            return name
        return f"`{name}`"

    # ------------- context cleanup -------------

    def _cleanup(self):
        # close client in this thread (the manager calls _cleanup in the owning thread)
        cli = getattr(self._tlocal, "client", None)
        try:
            if cli is not None:
                cli.close()
        except Exception:
            pass
        finally:
            if hasattr(self._tlocal, "client"):
                delattr(self._tlocal, "client")

