from __future__ import annotations

import time
from typing import Any, Dict, Tuple, Type

import dask
import dask.dataframe as dd
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import select, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import TimeoutError as SASQLTimeoutError, OperationalError
from sqlalchemy.orm import declarative_base

from sibi_dst.utils import ManagedResource
from sibi_dst.df_helper.core import FilterHandler
from ._db_gatekeeper import DBGatekeeper


class SQLAlchemyDask(ManagedResource):
    """
    Loads data from a database into a Dask DataFrame using a memory-safe,
    non-parallel, paginated approach (LIMIT/OFFSET).
    """

    _SQLALCHEMY_TO_DASK_DTYPE: Dict[str, str] = {
        "INTEGER": "Int64",
        "SMALLINT": "Int64",
        "BIGINT": "Int64",
        "FLOAT": "float64",
        "NUMERIC": "float64",
        "BOOLEAN": "bool",
        "VARCHAR": "object",
        "TEXT": "object",
        "DATE": "datetime64[ns]",
        "DATETIME": "datetime64[ns]",
        "TIMESTAMP": "datetime64[ns]",
        "TIME": "object",
        "UUID": "object",
    }

    def __init__(
        self,
        model: Type[declarative_base()],
        filters: Dict[str, Any],
        engine: Engine,
        chunk_size: int = 1000,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.model = model
        self.filters = filters or {}
        self.engine = engine
        self.chunk_size = int(chunk_size)
        self.filter_handler_cls = FilterHandler
        self.total_records: int = -1  # -1 indicates failure/unknown
        self._sem = DBGatekeeper.get(str(engine.url), max_concurrency=self._safe_cap())

    def _safe_cap(self) -> int:
        """
        Calculate a safe concurrency cap for DB work based on the engine's pool.

        Returns: max(1, pool_size + max_overflow - 1)
        - Works across SQLAlchemy 1.4/2.x
        - Tolerates pools that expose size/max_overflow as methods or attrs
        - Allows explicit override via self.db_gatekeeper_cap (if you pass it)
        """
        # optional explicit override
        explicit = getattr(self, "db_gatekeeper_cap", None)
        if isinstance(explicit, int) and explicit > 0:
            return explicit

        pool = getattr(self.engine, "pool", None)

        def _to_int(val, default):
            if val is None:
                return default
            if callable(val):
                try:
                    return int(val())  # e.g., pool.size()
                except Exception:
                    return default
            try:
                return int(val)
            except Exception:
                return default

        # size: QueuePool.size() -> int
        size_candidate = getattr(pool, "size", None)  # method on QueuePool
        pool_size = _to_int(size_candidate, 5)

        # max_overflow: prefer attribute; fall back to private _max_overflow; avoid 'overflow()' (method)
        max_overflow_attr = (
                getattr(pool, "max_overflow", None) or  # SQLAlchemy 2.x QueuePool
                getattr(pool, "_max_overflow", None)  # private fallback
        )
        max_overflow = _to_int(max_overflow_attr, 10)

        cap = max(1, pool_size + max_overflow - 1)
        self.logger.debug(f"Using a Cap of {cap} from pool size of {pool_size} and max overflow of {max_overflow}.")
        return max(1, cap)

    # ---------- meta ----------
    @classmethod
    def infer_meta_from_model(cls, model: Type[declarative_base()]) -> Dict[str, str]:
        mapper = inspect(model)
        dtypes: Dict[str, str] = {}
        for column in mapper.columns:
            dtype_str = str(column.type).upper().split("(")[0]
            dtype = cls._SQLALCHEMY_TO_DASK_DTYPE.get(dtype_str, "object")
            dtypes[column.name] = dtype
        return dtypes

    def read_frame(self, fillna_value=None) -> Tuple[int, dd.DataFrame]:
        # Base selectable
        query = select(self.model)
        if self.filters:
            query = self.filter_handler_cls(
                backend="sqlalchemy", logger=self.logger, debug=self.debug
            ).apply_filters(query, model=self.model, filters=self.filters)
        else:
            query = query.limit(self.chunk_size)

        # Meta dataframe (stable column order & dtypes)
        ordered_columns = [c.name for c in self.model.__table__.columns]
        meta_dtypes = self.infer_meta_from_model(self.model)
        meta_df = pd.DataFrame(columns=ordered_columns).astype(meta_dtypes)

        # Count with retry/backoff
        retry_attempts = 3
        backoff = 0.5
        total = 0

        for attempt in range(retry_attempts):
            try:
                with self._sem:
                    with self.engine.connect() as connection:
                        count_q = sa.select(sa.func.count()).select_from(query.alias())
                        total = connection.execute(count_q).scalar_one()
                    break
            except SASQLTimeoutError:
                if attempt < retry_attempts - 1:
                    self.logger.warning(f"Connection pool limit reached. Retrying in {backoff} seconds...")
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    self.total_records = -1
                    self.logger.error("Failed to get a connection from the pool after retries.", exc_info=True)
                    return self.total_records, dd.from_pandas(meta_df, npartitions=1)
            except OperationalError as oe:
                if "timeout" in str(oe).lower() and attempt < retry_attempts - 1:
                    self.logger.warning("Operational timeout, retrying…", exc_info=self.debug)
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                self.total_records = -1
                self.logger.error("OperationalError during count.", exc_info=True)
                return self.total_records, dd.from_pandas(meta_df, npartitions=1)
            except Exception as e:
                self.total_records = -1
                self.logger.error(f"Unexpected error during count: {e}", exc_info=True)
                return self.total_records, dd.from_pandas(meta_df, npartitions=1)

        self.total_records = int(total)
        if total == 0:
            self.logger.warning("Query returned 0 records.")
            super().close()
            return self.total_records, dd.from_pandas(meta_df, npartitions=1)

        self.logger.debug(f"Total records to fetch: {total}. Chunk size: {self.chunk_size}.")

        @dask.delayed
        def get_chunk(sql_query, chunk_offset):
            with self._sem:  # <<< cap concurrent DB fetches
                paginated = sql_query.limit(self.chunk_size).offset(chunk_offset)
                df = pd.read_sql(paginated, self.engine)
                if fillna_value is not None:
                    df = df.fillna(fillna_value)
                return df[ordered_columns].astype(meta_dtypes)

        offsets = range(0, total, self.chunk_size)
        delayed_chunks = [get_chunk(query, off) for off in offsets]
        ddf = dd.from_delayed(delayed_chunks, meta=meta_df)
        self.logger.debug(f"Created Dask DataFrame with {ddf.npartitions} partitions.")
        return self.total_records, ddf

