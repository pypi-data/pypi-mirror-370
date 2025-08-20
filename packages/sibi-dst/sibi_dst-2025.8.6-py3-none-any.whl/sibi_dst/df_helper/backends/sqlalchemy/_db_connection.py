
from __future__ import annotations
import os
import threading
from contextlib import contextmanager
from typing import Any, Optional, ClassVar, Generator, Type, Dict

from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import url as sqlalchemy_url
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool, StaticPool, Pool

from sibi_dst.utils import Logger
from ._sql_model_builder import SqlAlchemyModelBuilder

_ENGINE_REGISTRY_LOCK = threading.RLock()
_ENGINE_REGISTRY: Dict[tuple, Dict[str, Any]] = {}


class SqlAlchemyConnectionConfig(BaseModel):
    """
    Thread-safe, registry-backed SQLAlchemy connection manager.
    """

    # --- Public Configuration ---
    connection_url: str
    table: Optional[str] = None
    debug: bool = False

    # --- Pool Configuration ---
    pool_size: int = int(os.environ.get("DB_POOL_SIZE", 5))
    max_overflow: int = int(os.environ.get("DB_MAX_OVERFLOW", 10))
    pool_timeout: int = int(os.environ.get("DB_POOL_TIMEOUT", 30))
    pool_recycle: int = int(os.environ.get("DB_POOL_RECYCLE", 1800))
    pool_pre_ping: bool = True
    poolclass: Type[Pool] = QueuePool

    # --- Internal & Runtime State (normal fields; Pydantic allowed) ---
    model: Optional[Type[Any]] = None
    engine: Optional[Engine] = None
    logger: Optional[Logger] = None
    _own_logger: bool = False
    session_factory: Optional[sessionmaker] = None

    # --- Private State (plain Python values only) ---
    _engine_key_instance: tuple = ()
    _closed: bool = False  # prevent double-closing
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __enter__(self) -> "SqlAlchemyConnectionConfig":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    @field_validator("pool_size", "max_overflow", "pool_timeout", "pool_recycle")
    @classmethod
    def _validate_pool_params(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Pool parameters must be non-negative")
        return v

    @model_validator(mode="after")
    def _init_all(self) -> "SqlAlchemyConnectionConfig":
        self._init_logger()
        self._engine_key_instance = self._get_engine_key()
        self._init_engine()
        self._validate_conn()
        self._build_model()
        if self.engine:
            self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        return self

    def _init_logger(self) -> None:
        if self.logger is None:
            self._own_logger = True
            self.logger = Logger.default_logger(logger_name=self.__class__.__name__)
            self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)

    def _get_engine_key(self) -> tuple:
        parsed = sqlalchemy_url.make_url(self.connection_url)
        query = {k: v for k, v in parsed.query.items() if not k.startswith("pool_")}
        normalized_url = parsed.set(query=query)
        key_parts = [str(normalized_url)]
        if self.poolclass not in (NullPool, StaticPool):
            key_parts += [
                self.pool_size, self.max_overflow, self.pool_timeout,
                self.pool_recycle, self.pool_pre_ping
            ]
        return tuple(key_parts)

    def _init_engine(self) -> None:
        with _ENGINE_REGISTRY_LOCK:
            wrapper = _ENGINE_REGISTRY.get(self._engine_key_instance)
            if wrapper:
                self.engine = wrapper["engine"]
                wrapper["ref_count"] += 1
                if self.debug:
                    self.logger.debug(f"Reusing engine. Ref count: {wrapper['ref_count']}.")
            else:
                if self.debug:
                    self.logger.debug(f"Creating new engine for key: {self._engine_key_instance}")
                try:
                    new_engine = create_engine(
                        self.connection_url,
                        pool_size=self.pool_size,
                        max_overflow=self.max_overflow,
                        pool_timeout=self.pool_timeout,
                        pool_recycle=self.pool_recycle,
                        pool_pre_ping=self.pool_pre_ping,
                        poolclass=self.poolclass,
                    )
                    self.engine = new_engine
                    self._attach_events()
                    _ENGINE_REGISTRY[self._engine_key_instance] = {
                        "engine": new_engine,
                        "ref_count": 1,
                        "active_connections": 0,
                    }
                except Exception as e:
                    self.logger.error(f"Failed to create engine: {e}")
                    raise SQLAlchemyError(f"Engine creation failed: {e}") from e

    def close(self) -> None:
        if self._closed:
            if self.debug:
                self.logger.debug("Attempted to close an already-closed config instance.")
            return

        with _ENGINE_REGISTRY_LOCK:
            key = self._engine_key_instance
            wrapper = _ENGINE_REGISTRY.get(key)
            if not wrapper:
                self.logger.warning("Attempted to close a config whose engine is not in the registry.")
            else:
                wrapper["ref_count"] -= 1
                if self.debug:
                    self.logger.debug(f"Closing connection. Ref count now {wrapper['ref_count']}.")
                if wrapper["ref_count"] <= 0:
                    if self.debug:
                        self.logger.debug(f"Disposing engine as reference count is zero. Key: {key}")
                    try:
                        wrapper["engine"].dispose()
                    finally:
                        del _ENGINE_REGISTRY[key]
        self._closed = True

    def _attach_events(self) -> None:
        if not self.engine:
            return
        event.listen(self.engine, "checkout", self._on_checkout)
        event.listen(self.engine, "checkin", self._on_checkin)

    def _on_checkout(self, *args) -> None:
        with _ENGINE_REGISTRY_LOCK:
            wrapper = _ENGINE_REGISTRY.get(self._engine_key_instance)
            if wrapper:
                wrapper["active_connections"] += 1

    def _on_checkin(self, *args) -> None:
        with _ENGINE_REGISTRY_LOCK:
            wrapper = _ENGINE_REGISTRY.get(self._engine_key_instance)
            if wrapper:
                wrapper["active_connections"] = max(0, wrapper["active_connections"] - 1)

    @property
    def active_connections(self) -> int:
        with _ENGINE_REGISTRY_LOCK:
            wrapper = _ENGINE_REGISTRY.get(self._engine_key_instance)
            return wrapper["active_connections"] if wrapper else 0

    def _validate_conn(self) -> None:
        try:
            with self.managed_connection() as conn:
                conn.execute(text("SELECT 1"))
            if self.debug:
                self.logger.debug("Database connection validated successfully.")
        except OperationalError as e:
            self.logger.error(f"Database connection failed: {e}")
            raise ValueError(f"DB connection failed: {e}") from e

    @contextmanager
    def managed_connection(self) -> Generator[Any, None, None]:
        if not self.engine:
            raise RuntimeError("Engine not initialized. Cannot get a connection.")
        conn = self.engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    def get_session(self) -> Session:
        if not self.session_factory:
            raise RuntimeError("Session factory not initialized. Cannot get a session.")
        return self.session_factory()

    def _build_model(self) -> None:
        if not self.table or not self.engine:
            return
        try:
            builder = SqlAlchemyModelBuilder(self.engine, self.table)
            self.model = builder.build_model()
            if self.debug:
                self.logger.debug(f"Successfully built ORM model for table: {self.table}")
        except Exception as e:
            self.logger.error(f"Failed to build ORM model for table '{self.table}': {e}")
            raise ValueError(f"Model construction failed for table '{self.table}': {e}") from e

