from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Any, Optional, ClassVar, Generator, Type, Dict

from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
    ConfigDict,
)
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import url as sqlalchemy_url
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool, StaticPool

# Restoring the original intended imports
from sibi_dst.utils import Logger
from ._model_builder import SQLModelModelBuilder


class SQLModelConnectionConfig(BaseModel):
    """
    A thread-safe, registry-backed SQLAlchemy connection manager.

    This class encapsulates database connection configuration and provides robust,
    shared resource management. It is designed to be instantiated multiple times
    with the same connection parameters, where it will safely share a single
    underlying database engine and connection pool.

    Key Features:
      - Shared Engine & Pool: Reuses a single SQLAlchemy Engine for identical
        database URLs and pool settings, improving application performance.
      - Reference Counting: Safely manages the lifecycle of the shared engine,
        disposing of it only when the last user has closed its connection config.
      - Per-Engine Connection Tracking: Monitors active connections for each
        engine individually.
      - Dynamic ORM Model Building: If a table name is provided, it can
        dynamically generate a SQLAlchemy ORM model for that table.
      - Integrated Session Management: Provides a pre-configured session factory
        for convenient database interactions.

    Attributes:
        connection_url (str): The database URL (e.g., "postgresql://u:p@h/d").
        table (Optional[str]): If provided, an ORM model will be built for this table.
        model (Optional[Any]): The dynamically generated ORM model class.
        engine (Optional[Engine]): The underlying SQLAlchemy engine.
        logger (Logger): The logger instance.
        debug (bool): If True, sets logger to DEBUG level.
        session_factory (Optional[sessionmaker]): A factory for creating Session objects.
    """
    # --- Public Configuration ---
    connection_url: str
    table: Optional[str] = None
    debug: bool = False

    # --- Pool Configuration ---
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 300
    pool_pre_ping: bool = True
    poolclass: Type[QueuePool] = QueuePool

    # --- Internal & Runtime State ---
    model: Optional[Type[Any]] = None
    engine: Optional[Engine] = None
    logger: Optional[Logger] = None
    session_factory: Optional[sessionmaker] = None

    # --- Private State ---
    _engine_key_instance: tuple = ()

    # --- Class-level Shared Resources ---
    # Registry stores engine wrappers with metadata like ref_count.
    # Format: { engine_key: {'engine': Engine, 'ref_count': int, 'active_connections': int} }
    _engine_registry: ClassVar[Dict[tuple, Dict[str, Any]]] = {}
    _registry_lock: ClassVar[threading.Lock] = threading.Lock()

    # Pydantic v2 configuration
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    @field_validator("pool_size", "max_overflow", "pool_timeout", "pool_recycle")
    @classmethod
    def _validate_pool_params(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Pool parameters must be non-negative")
        return v

    @model_validator(mode="after")
    def _init_all(self) -> SQLModelConnectionConfig:
        """
        Orchestrates the initialization process after Pydantic validation.
        This method sets up the logger, engine, validates the connection,
        builds the ORM model, and creates the session factory.
        """
        self._init_logger()

        # The engine key is generated and stored on the instance to ensure
        # that even if public attributes are changed later, this instance
        # can always find its original engine in the registry.
        self._engine_key_instance = self._get_engine_key()

        self._init_engine()
        self._validate_conn()
        self._build_model()

        if self.engine:
            self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

        return self

    def _init_logger(self) -> None:
        """Initializes the logger for this instance."""
        if self.logger is None:
            self.logger = Logger.default_logger(logger_name=self.__class__.__name__)
        # Assuming the Logger has a set_level method that accepts standard logging levels
        log_level = Logger.DEBUG if self.debug else Logger.INFO
        self.logger.set_level(log_level)

    def _get_engine_key(self) -> tuple:
        """
        Generates a unique, normalized key for an engine configuration.
        This key is used as the dictionary key in the shared _engine_registry.
        It intentionally excludes instance-specific details like `table` to
        ensure proper engine sharing.
        """
        parsed = sqlalchemy_url.make_url(self.connection_url)
        # Exclude pooling from the query params as they are handled separately
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
        """
        Initializes the SQLAlchemy Engine.
        If an identical engine already exists in the registry, it is reused
        and its reference count is incremented. Otherwise, a new engine
        is created and added to the registry.
        """
        with self._registry_lock:
            engine_wrapper = self._engine_registry.get(self._engine_key_instance)

            if engine_wrapper:
                # --- Reuse existing engine ---
                self.engine = engine_wrapper['engine']
                engine_wrapper['ref_count'] += 1
                self.logger.debug(
                    f"Reusing engine. Ref count: {engine_wrapper['ref_count']}. Key: {self._engine_key_instance}")
            else:
                # --- Create new engine ---
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

                    # Store the new engine and its metadata in the registry
                    self._engine_registry[self._engine_key_instance] = {
                        'engine': new_engine,
                        'ref_count': 1,
                        'active_connections': 0
                    }
                except Exception as e:
                    self.logger.error(f"Failed to create engine: {e}")
                    raise SQLAlchemyError(f"Engine creation failed: {e}") from e

    def _attach_events(self) -> None:
        """Attaches checkout/checkin events to the engine for connection tracking."""
        if self.engine:
            event.listen(self.engine, "checkout", self._on_checkout)
            event.listen(self.engine, "checkin", self._on_checkin)

    def _on_checkout(self, *args) -> None:
        """Event listener for when a connection is checked out from the pool."""
        with self._registry_lock:
            wrapper = self._engine_registry.get(self._engine_key_instance)
            if wrapper:
                wrapper['active_connections'] += 1
        self.logger.debug(f"Connection checked out. Active: {self.active_connections}")

    def _on_checkin(self, *args) -> None:
        """Event listener for when a connection is returned to the pool."""
        with self._registry_lock:
            wrapper = self._engine_registry.get(self._engine_key_instance)
            if wrapper:
                wrapper['active_connections'] = max(0, wrapper['active_connections'] - 1)
        self.logger.debug(f"Connection checked in. Active: {self.active_connections}")

    @property
    def active_connections(self) -> int:
        """Returns the number of active connections for this instance's engine."""
        with self._registry_lock:
            wrapper = self._engine_registry.get(self._engine_key_instance)
            return wrapper['active_connections'] if wrapper else 0

    def _validate_conn(self) -> None:
        """Tests the database connection by executing a simple query."""
        try:
            with self.managed_connection() as conn:
                conn.execute(text("SELECT 1"))
            self.logger.debug("Database connection validated successfully.")
        except OperationalError as e:
            self.logger.error(f"Database connection failed: {e}")
            # This will be caught by Pydantic and raised as a ValidationError
            raise ValueError(f"DB connection failed: {e}") from e

    @contextmanager
    def managed_connection(self) -> Generator[Any, None, None]:
        """Provides a single database connection from the engine pool."""
        if not self.engine:
            raise RuntimeError("Engine not initialized. Cannot get a connection.")
        conn = self.engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    def get_session(self) -> Session:
        """Returns a new SQLAlchemy Session from the session factory."""
        if not self.session_factory:
            raise RuntimeError("Session factory not initialized. Cannot get a session.")
        return self.session_factory()

    def _build_model(self) -> None:
        """
        Dynamically builds and assigns an ORM model if `self.table` is set.
        Uses SqlAlchemyModelBuilder to reflect the table schema from the database.
        """
        if not self.table or not self.engine:
            return
        try:
            builder = SQLModelModelBuilder(self.engine, self.table)
            self.model = builder.build_model()
            self.logger.debug(f"Successfully built ORM model for table: {self.table}")
        except Exception as e:
            self.logger.error(f"Failed to build ORM model for table '{self.table}': {e}")
            # Propagate as a ValueError to be caught by Pydantic validation
            raise ValueError(f"Model construction failed for table '{self.table}': {e}") from e

    def close(self) -> None:
        """
        Decrements the engine's reference count and disposes of the engine
        if the count reaches zero. This is the primary method for releasing
        resources managed by this configuration object.
        """
        with self._registry_lock:
            key = self._engine_key_instance
            engine_wrapper = self._engine_registry.get(key)

            if not engine_wrapper:
                self.logger.warning("Attempted to close a config whose engine is not in the registry.")
                return

            engine_wrapper['ref_count'] -= 1
            self.logger.debug(f"Closing config. Ref count is now {engine_wrapper['ref_count']} for key {key}.")

            if engine_wrapper['ref_count'] <= 0:
                self.logger.debug(f"Disposing engine as reference count is zero. Key: {key}")
                engine_wrapper['engine'].dispose()
                del self._engine_registry[key]

    def dispose_idle_connections(self) -> int:
        """
        Closes and discards idle connections in this engine's connection pool.

        This is a pool-level operation that affects only the connections held
        by the pool, not those active at the database level.

        Returns:
            int: The number of connections disposed of.
        """
        if not self.engine:
            self.logger.warning("Cannot dispose idle connections: engine not initialized.")
            return 0

        pool = self.engine.pool
        if isinstance(pool, QueuePool):
            # The pool.dispose() method checks in all connections and clears the pool.
            # The number of checked-in connections is the number of idle connections.
            count = pool.checkedin()
            pool.dispose()
            self.logger.debug(f"Disposed {count} idle connections from the pool.")
            return count

        self.logger.warning(f"Idle connection disposal not applicable for pool type: {type(pool).__name__}")
        return 0

    def terminate_idle_connections(self, idle_seconds: int = 300) -> int:
        """
        Terminates idle connections at the database server level.

        This is an administrative database operation that forcibly closes
        backend processes. Use with caution. Support is dialect-specific.

        Args:
            idle_seconds (int): The minimum idle time in seconds for a
                                connection to be terminated.

        Returns:
            int: The number of connections terminated.
        """
        if not self.engine:
            self.logger.warning("Cannot terminate connections: engine not initialized.")
            return 0

        terminated_count = 0
        dialect = self.engine.dialect.name

        with self.managed_connection() as conn:
            try:
                if dialect == 'postgresql':
                    query = text(
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE state = 'idle' "
                        "AND (now() - query_start) > INTERVAL ':idle_seconds seconds' "
                        "AND pid <> pg_backend_pid()"
                    )
                    res = conn.execute(query, {"idle_seconds": idle_seconds})
                    terminated_count = res.rowcount if res.rowcount is not None else 0

                elif dialect == 'mysql':
                    process_list = conn.execute(text("SHOW PROCESSLIST"))
                    for row in process_list:
                        # Pylint compatible attribute access
                        if getattr(row, 'Command', '') == 'Sleep' and getattr(row, 'Time', 0) > idle_seconds:
                            conn.execute(text(f"KILL {getattr(row, 'Id')}"))
                            terminated_count += 1
                else:
                    self.logger.warning(f"Idle connection termination is not supported for dialect: {dialect}")
            except SQLAlchemyError as e:
                self.logger.error(f"Error terminating idle connections for dialect {dialect}: {e}")

        if terminated_count > 0:
            self.logger.debug(f"Terminated {terminated_count} idle connections on the database server.")
        return terminated_count

