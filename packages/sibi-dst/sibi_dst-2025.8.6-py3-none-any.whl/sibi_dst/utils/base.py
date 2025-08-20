import abc
import threading
import weakref
from typing import Self, Optional, Callable

import fsspec

from sibi_dst.utils import Logger


class ManagedResource(abc.ABC):
    """
    Boilerplate ABC for components that manage a logger and an optional fsspec filesystem,
    with sync/async lifecycle helpers, lazy FS creation via an optional factory, and
    configurable cleanup-error logging.
    """

    def __init__(
        self,
        *,
        verbose: bool = False,
        debug: bool = False,
        log_cleanup_errors: bool = True,
        logger: Optional[Logger] = None,
        fs: Optional[fsspec.AbstractFileSystem] = None,
        fs_factory: Optional[Callable[[], fsspec.AbstractFileSystem]] = None,
        **_: object,
    ) -> None:
        # ---- Declared upfront for type checkers
        self.logger: Logger
        self.fs: Optional[fsspec.AbstractFileSystem] = None
        self._fs_factory: Optional[Callable[[], fsspec.AbstractFileSystem]] = None
        self._owns_logger: bool = False
        self._owns_fs: bool = False
        self._is_closed: bool = False
        self._closing: bool = False
        self._close_lock = threading.RLock()

        self.verbose = verbose
        self.debug = debug
        self._log_cleanup_errors = log_cleanup_errors

        # ---- Logger ownership
        if logger is None:
            self.logger = Logger.default_logger(logger_name=self.__class__.__name__)
            self._owns_logger = True
            level = Logger.DEBUG if self.debug else (Logger.INFO if self.verbose else Logger.WARNING)
            self.logger.set_level(level)
        else:
            self.logger = logger
            self._owns_logger = False  # do not mutate external logger

        # ---- FS ownership & lazy creation
        if fs is not None:
            self.fs = fs
            self._owns_fs = False
            self._fs_factory = None
        elif fs_factory is not None:
            # Lazy: don't create until first use
            self._fs_factory = fs_factory
            self._owns_fs = True  # we will own it *if* created
            self.fs = None
        else:
            self.fs = None
            self._owns_fs = False
            self._fs_factory = None

        # Register a GC-time finalizer that does not capture self
        self_ref = weakref.ref(self)
        self._finalizer = weakref.finalize(self, self._finalize_static, self_ref)

        if self.debug:
            try:
                self.logger.debug("Component %s initialized. %s", self.__class__.__name__, repr(self))
            except Exception:
                pass

    # ---------- Introspection ----------
    @property
    def is_closed(self) -> bool:
        return self._is_closed

    @property
    def closed(self) -> bool:  # alias
        return self._is_closed

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        logger_status = "own" if self._owns_logger else "external"
        if self.fs is None and self._fs_factory is not None:
            fs_status = "own(lazy)"
        elif self.fs is None:
            fs_status = "none"
        else:
            fs_status = "own" if self._owns_fs else "external"
        return (f"<{class_name} debug={self.debug} verbose={self.verbose} "
                f"log_cleanup_errors={self._log_cleanup_errors} "
                f"logger={logger_status} fs={fs_status}>")

    # ---------- Subclass hooks ----------
    def _cleanup(self) -> None:
        """Sync cleanup for resources created BY THE SUBCLASS."""
        return

    async def _acleanup(self) -> None:
        """Async cleanup for resources created BY THE SUBCLASS."""
        return

    # ---------- FS helpers ----------
    def _ensure_fs(self) -> Optional[fsspec.AbstractFileSystem]:
        """Create the FS lazily if a factory was provided. Return fs (or None)."""
        if self.fs is None and self._fs_factory is not None:
            created = self._fs_factory()
            if not isinstance(created, fsspec.AbstractFileSystem):
                raise TypeError(f"fs_factory() must return fsspec.AbstractFileSystem, got {type(created)!r}")
            self.fs = created
            # _owns_fs already True when factory is present
        return self.fs

    def require_fs(self) -> fsspec.AbstractFileSystem:
        """Return a filesystem or raise if not configured/creatable."""
        fs = self._ensure_fs()
        if fs is None:
            raise RuntimeError(
                f"{self.__class__.__name__}: filesystem is required but not configured"
            )
        return fs

    # ---------- Shared shutdown helpers (no logging; safe for late shutdown) ----------
    def _release_owned_fs(self) -> None:
        if self._owns_fs:
            # ensure creation state is respected even if never used
            _ = self.fs or None  # no-op; if never created, nothing to close
            if self.fs is not None:
                close = getattr(self.fs, "close", None)
                try:
                    if callable(close):
                        close()
                finally:
                    self.fs = None

    def _shutdown_logger(self) -> None:
        if self._owns_logger:
            try:
                self.logger.shutdown()
            except Exception:
                pass

    def _shutdown_owned_resources(self) -> None:
        self._release_owned_fs()
        self._shutdown_logger()

    # ---------- Public lifecycle (sync) ----------
    def close(self) -> None:
        with self._close_lock:
            if self._is_closed or self._closing:
                return
            self._closing = True

        try:
            self._cleanup()
        except Exception:
            # Only include traceback when debug=True
            if self._log_cleanup_errors:
                try:
                    self.logger.error(
                        "Error during %s._cleanup()", self.__class__.__name__,
                        exc_info=self.debug
                    )
                except Exception:
                    pass
            raise
        finally:
            with self._close_lock:
                self._is_closed = True
                self._closing = False
            self._shutdown_owned_resources()
            if self.debug:
                try:
                    self.logger.debug("Component %s closed.", self.__class__.__name__)
                except Exception:
                    pass

    # ---------- Public lifecycle (async) ----------
    async def aclose(self) -> None:
        with self._close_lock:
            if self._is_closed or self._closing:
                return
            self._closing = True

        try:
            await self._acleanup()
        except Exception:
            # Only include traceback when debug=True
            if self._log_cleanup_errors:
                try:
                    self.logger.error(
                        "Error during %s._acleanup()", self.__class__.__name__,
                        exc_info=self.debug
                    )
                except Exception:
                    pass
            raise
        finally:
            with self._close_lock:
                self._is_closed = True
                self._closing = False
            self._shutdown_owned_resources()
            if self.debug:
                try:
                    self.logger.debug("Async component %s closed.", self.__class__.__name__)
                except Exception:
                    pass

    # ---------- Context managers ----------
    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.close()
        return False  # propagate exceptions

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        await self.aclose()
        return False

    # ---------- Finalizer ( at Garbage Collection-time absolutely silent) ----------
    @staticmethod
    def _finalize_static(ref: "weakref.ReferenceType[ManagedResource]") -> None:
        obj = ref()
        if obj is None:
            return
        # No logging here; interpreter may be tearing down.
        # Best-effort silent cleanup; avoid locks and context managers.
        try:
            if not obj._is_closed:
                try:
                    obj._cleanup()
                except Exception:
                    pass
                obj._is_closed = True
                try:
                    obj._shutdown_owned_resources()
                except Exception:
                    pass
        except Exception:
            # do not show anything at garbage collection time
            pass

