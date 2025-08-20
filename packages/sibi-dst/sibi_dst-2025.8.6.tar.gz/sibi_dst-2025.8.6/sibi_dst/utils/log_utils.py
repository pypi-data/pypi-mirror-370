from __future__ import annotations

import logging
import os
import sys
import time
from contextlib import contextmanager, nullcontext
from logging import LoggerAdapter
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any

# OpenTelemetry (optional)
try:
    from opentelemetry import trace
    from opentelemetry._logs import set_logger_provider, get_logger_provider
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import Tracer as OTelTracer
    _OTEL_AVAILABLE = True
except Exception:
    # OTel is optional; keep class working without it
    LoggerProvider = TracerProvider = OTelTracer = object  # type: ignore
    LoggingHandler = object  # type: ignore
    _OTEL_AVAILABLE = False


class Logger:
    """
    Process-safe logger with optional OpenTelemetry integration.

    Backward-compatible surface:
      - Logger.default_logger(...)
      - .debug/.info/.warning/.error/.critical
      - .set_level(level), .shutdown()
      - .bind(**extra) -> LoggerAdapter, .bound(**extra) ctx manager
      - .start_span(name, attributes=None), .trace_function(span_name=None)
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    # prevent attaching duplicate handlers per (logger_name, file_path) in process
    _handler_keys_attached: set[tuple[str, str]] = set()
    _otel_initialized_names: set[str] = set()

    def __init__(
        self,
        log_dir: str,
        logger_name: str,
        log_file: str,
        log_level: int = logging.DEBUG,
        enable_otel: bool = False,
        otel_service_name: Optional[str] = None,
        otel_stream_name: Optional[str] = None,
        otel_endpoint: str = "0.0.0.0:4317",
        otel_insecure: bool = False,
    ):
        self.log_dir = log_dir
        self.logger_name = logger_name
        self.log_file = log_file
        self.log_level = log_level

        self.enable_otel = bool(enable_otel and _OTEL_AVAILABLE)
        self.otel_service_name = (otel_service_name or logger_name).strip() or "app"
        self.otel_stream_name = (otel_stream_name or "").strip() or None
        self.otel_endpoint = otel_endpoint
        self.otel_insecure = otel_insecure

        self.logger_provider: Optional[LoggerProvider] = None
        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer: Optional[OTelTracer] = None

        self._core_logger: logging.Logger = logging.getLogger(self.logger_name)
        self._core_logger.setLevel(self.log_level)
        self._core_logger.propagate = False

        # public handle (may be adapter)
        self.logger: logging.Logger | LoggerAdapter = self._core_logger

        self._setup_standard_handlers()
        if self.enable_otel:
            self._setup_otel_if_needed()

        # expose adapter with default extras if OTel stream requested
        if self.enable_otel and self.otel_stream_name:
            attributes = {
                "log_stream": self.otel_stream_name,
                "log_service_name": self.otel_service_name,
                "logger_name": self.logger_name,
            }
            self.logger = LoggerAdapter(self._core_logger, extra=attributes)

    # -------------------------
    # Public API
    # -------------------------

    @classmethod
    def default_logger(
        cls,
        log_dir: str = "./logs/",
        logger_name: Optional[str] = None,
        log_file: Optional[str] = None,
        log_level: int = logging.INFO,
        enable_otel: bool = False,
        otel_service_name: Optional[str] = None,
        otel_stream_name: Optional[str] = None,
        otel_endpoint: str = "0.0.0.0:4317",
        otel_insecure: bool = False,
    ) -> "Logger":
        try:
            frame = sys._getframe(1)
            caller_name = frame.f_globals.get("__name__", "default_logger")
        except Exception:
            caller_name = "default_logger"

        logger_name = logger_name or caller_name
        log_file = log_file or logger_name

        return cls(
            log_dir=log_dir,
            logger_name=logger_name,
            log_file=log_file,
            log_level=log_level,
            enable_otel=enable_otel,
            otel_service_name=otel_service_name,
            otel_stream_name=otel_stream_name,
            otel_endpoint=otel_endpoint,
            otel_insecure=otel_insecure,
        )

    def shutdown(self):
        """Flush/close OTel providers and Python logging handlers."""
        try:
            if self.enable_otel:
                if isinstance(self.logger_provider, LoggerProvider):
                    try:
                        self._core_logger.info("Flushing OpenTelemetry logs...")
                        self.logger_provider.force_flush()
                    except Exception:
                        pass
                    try:
                        self._core_logger.info("Shutting down OpenTelemetry logs...")
                        self.logger_provider.shutdown()
                    except Exception:
                        pass

                if isinstance(self.tracer_provider, TracerProvider):
                    try:
                        self._core_logger.info("Flushing OpenTelemetry traces...")
                        self.tracer_provider.force_flush()
                    except Exception:
                        pass
                    try:
                        self._core_logger.info("Shutting down OpenTelemetry traces...")
                        self.tracer_provider.shutdown()
                    except Exception:
                        pass
        finally:
            # Close our handlers explicitly to release file descriptors
            for h in list(self._core_logger.handlers):
                try:
                    h.flush()
                except Exception:
                    pass
                try:
                    h.close()
                except Exception:
                    pass
                try:
                    self._core_logger.removeHandler(h)
                except Exception:
                    pass
            logging.shutdown()

    def set_level(self, level: int):
        self._core_logger.setLevel(level)

    # passthrough convenience
    def _log(self, level: int, msg: str, *args, **kwargs):
        extra = kwargs.pop("extra", None)
        if extra is not None:
            if isinstance(self.logger, LoggerAdapter):
                merged = {**self.logger.extra, **extra}
                LoggerAdapter(self.logger.logger, merged).log(level, msg, *args, **kwargs)
            else:
                LoggerAdapter(self.logger, extra).log(level, msg, *args, **kwargs)
        else:
            self.logger.log(level, msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs): self._log(logging.DEBUG, msg, *args, **kwargs)
    def info(self, msg: str, *args, **kwargs): self._log(logging.INFO, msg, *args, **kwargs)
    def warning(self, msg: str, *args, **kwargs): self._log(logging.WARNING, msg, *args, **kwargs)
    def error(self, msg: str, *args, **kwargs): self._log(logging.ERROR, msg, *args, **kwargs)
    def critical(self, msg: str, *args, **kwargs): self._log(logging.CRITICAL, msg, *args, **kwargs)

    def bind(self, **extra: Any) -> LoggerAdapter:
        if isinstance(self.logger, LoggerAdapter):
            merged = {**self.logger.extra, **extra}
            return LoggerAdapter(self.logger.logger, merged)
        return LoggerAdapter(self.logger, extra)

    @contextmanager
    def bound(self, **extra: Any):
        adapter = self.bind(**extra)
        yield adapter

    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        if not (self.enable_otel and _OTEL_AVAILABLE and self.tracer):
            # keep API but no-op cleanly
            self.warning("Tracing is disabled or not initialized. Cannot start span.")
            return nullcontext()

        cm = self.tracer.start_as_current_span(name)

        class _SpanCtx:
            def __enter__(_self):
                span = cm.__enter__()
                if attributes:
                    for k, v in attributes.items():
                        try:
                            span.set_attribute(k, v)
                        except Exception:
                            pass
                return span

            def __exit__(_self, exc_type, exc, tb):
                return cm.__exit__(exc_type, exc, tb)

        return _SpanCtx()

    def trace_function(self, span_name: Optional[str] = None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                name = span_name or func.__name__
                with self.start_span(name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    # -------------------------
    # Internal setup
    # -------------------------

    def _setup_standard_handlers(self):
        os.makedirs(self.log_dir, exist_ok=True)
        calling_script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        log_file_path = os.path.join(self.log_dir, f"{self.log_file}_{calling_script}.log")
        key = (self.logger_name, os.path.abspath(log_file_path))

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        formatter.converter = time.gmtime  # UTC timestamps

        # attach once per process for this logger/file combo
        if key not in self._handler_keys_attached:
            file_handler = RotatingFileHandler(
                log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5, delay=True
            )
            file_handler.setFormatter(formatter)
            self._core_logger.addHandler(file_handler)

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self._core_logger.addHandler(console_handler)

            self._handler_keys_attached.add(key)

    def _normalize_otlp_endpoint(self, ep: str) -> str:
        if "://" not in ep:
            ep = ("http://" if self.otel_insecure else "https://") + ep
        return ep

    def _setup_otel_if_needed(self):
        """
        Initialize OTel once per logger_name within the process to avoid
        clobbering providers (important under reloaders).
        """
        if not _OTEL_AVAILABLE:
            self._core_logger.warning("OpenTelemetry not available — skipping OTel setup.")
            return
        if self.logger_name in self._otel_initialized_names:
            # already initialized for this logger name in this process
            self.tracer = trace.get_tracer(self.logger_name)
            return

        # Create resources
        resource_attrs = {
            "service.name": self.otel_service_name,
            "logger.name": self.logger_name,
        }
        if self.otel_stream_name:
            resource_attrs["log.stream"] = self.otel_stream_name
        resource = Resource.create(resource_attrs)

        # Respect any existing providers to avoid breaking apps that configured OTel elsewhere
        existing_lp = None
        try:
            existing_lp = get_logger_provider()
        except Exception:
            pass

        if not isinstance(existing_lp, LoggerProvider):
            self.logger_provider = LoggerProvider(resource=resource)
            set_logger_provider(self.logger_provider)
        else:
            # reuse existing; don’t overwrite global provider
            self.logger_provider = existing_lp  # type: ignore

        existing_tp = None
        try:
            existing_tp = trace.get_tracer_provider()
        except Exception:
            pass

        if not isinstance(existing_tp, TracerProvider):
            self.tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self.tracer_provider)
        else:
            self.tracer_provider = existing_tp  # type: ignore

        endpoint = self._normalize_otlp_endpoint(self.otel_endpoint)

        # Logs exporter + processor (only if we created our own provider)
        if isinstance(self.logger_provider, LoggerProvider):
            try:
                log_exporter = OTLPLogExporter(endpoint=endpoint, insecure=self.otel_insecure)
                self.logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
            except Exception as e:
                self._core_logger.warning(f"Failed to attach OTel log exporter: {e}")

        # Traces exporter + processor (only if we created our own provider)
        if isinstance(self.tracer_provider, TracerProvider):
            try:
                span_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=self.otel_insecure)
                self.tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
            except Exception as e:
                self._core_logger.warning(f"Failed to attach OTel span exporter: {e}")

        # Attach OTel LoggingHandler once
        if not any(type(h).__name__ == "LoggingHandler" for h in self._core_logger.handlers):
            try:
                otel_handler = LoggingHandler(level=logging.NOTSET, logger_provider=self.logger_provider)  # type: ignore
                self._core_logger.addHandler(otel_handler)
            except Exception as e:
                self._core_logger.warning(f"Failed to attach OTel logging handler: {e}")

        # Tracer handle
        try:
            self.tracer = trace.get_tracer(self.logger_name)
        except Exception:
            self.tracer = None

        self._otel_initialized_names.add(self.logger_name)
        self._core_logger.info("OpenTelemetry logging/tracing initialized.")

# from __future__ import annotations
#
# import logging
# import os
# import sys
# import time
# from contextlib import contextmanager
# from logging import LoggerAdapter
# from logging.handlers import RotatingFileHandler
# from typing import Optional, Dict, Any
#
# # OpenTelemetry imports
# from opentelemetry import trace
# from opentelemetry._logs import set_logger_provider
# from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
# from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
# from opentelemetry.sdk.resources import Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.trace import Tracer as OTelTracer
#
#
# class Logger:
#     """
#     Handles the creation and management of logging, with optional OpenTelemetry integration.
#     """
#
#     DEBUG = logging.DEBUG
#     INFO = logging.INFO
#     WARNING = logging.WARNING
#     ERROR = logging.ERROR
#     CRITICAL = logging.CRITICAL
#
#     def __init__(
#         self,
#         log_dir: str,
#         logger_name: str,
#         log_file: str,
#         log_level: int = logging.DEBUG,
#         enable_otel: bool = False,
#         otel_service_name: Optional[str] = None,
#         otel_stream_name: Optional[str] = None,
#         otel_endpoint: str = "0.0.0.0:4317",
#         otel_insecure: bool = False,
#     ):
#         self.log_dir = log_dir
#         self.logger_name = logger_name
#         self.log_file = log_file
#         self.log_level = log_level
#
#         self.enable_otel = enable_otel
#         self.otel_service_name = (otel_service_name or logger_name).strip() or "app"
#         self.otel_stream_name = (otel_stream_name or "").strip() or None
#         self.otel_endpoint = otel_endpoint
#         self.otel_insecure = otel_insecure
#
#         self.logger_provider: Optional[LoggerProvider] = None
#         self.tracer_provider: Optional[TracerProvider] = None
#         self.tracer: Optional[OTelTracer] = None
#
#         # Internal logger vs public (adapter) logger
#         self._core_logger: logging.Logger = logging.getLogger(self.logger_name)
#         self.logger: logging.Logger | LoggerAdapter = self._core_logger
#
#         self._setup()
#
#     # -------------------------
#     # Public API
#     # -------------------------
#
#     @classmethod
#     def default_logger(
#         cls,
#         log_dir: str = "./logs/",
#         logger_name: Optional[str] = None,
#         log_file: Optional[str] = None,
#         log_level: int = logging.INFO,
#         enable_otel: bool = False,
#         otel_service_name: Optional[str] = None,
#         otel_stream_name: Optional[str] = None,
#         otel_endpoint: str = "0.0.0.0:4317",
#         otel_insecure: bool = False,
#     ) -> "Logger":
#         try:
#             frame = sys._getframe(1)
#             caller_name = frame.f_globals.get("__name__", "default_logger")
#         except (AttributeError, ValueError):
#             caller_name = "default_logger"
#
#         logger_name = logger_name or caller_name
#         log_file = log_file or logger_name
#
#         return cls(
#             log_dir=log_dir,
#             logger_name=logger_name,
#             log_file=log_file,
#             log_level=log_level,
#             enable_otel=enable_otel,
#             otel_service_name=otel_service_name,
#             otel_stream_name=otel_stream_name,
#             otel_endpoint=otel_endpoint,
#             otel_insecure=otel_insecure,
#         )
#
#     def shutdown(self):
#         """Flush and shut down logging and tracing providers, then Python logging."""
#         try:
#             if self.enable_otel:
#                 if self.logger_provider:
#                     try:
#                         self._core_logger.info("Flushing OpenTelemetry logs...")
#                         self.logger_provider.force_flush()
#                     except Exception:
#                         pass
#                     try:
#                         self._core_logger.info("Shutting down OpenTelemetry logs...")
#                         self.logger_provider.shutdown()
#                     except Exception:
#                         pass
#
#                 if self.tracer_provider:
#                     try:
#                         self._core_logger.info("Flushing OpenTelemetry traces...")
#                         self.tracer_provider.force_flush()
#                     except Exception:
#                         pass
#                     try:
#                         self._core_logger.info("Shutting down OpenTelemetry traces...")
#                         self.tracer_provider.shutdown()
#                     except Exception:
#                         pass
#         finally:
#             logging.shutdown()
#
#     def set_level(self, level: int):
#         """Set the logging level for the logger."""
#         self._core_logger.setLevel(level)
#
#     # passthrough convenience methods
#     def _log(self, level: int, msg: str, *args, **kwargs):
#         extra = kwargs.pop("extra", None)
#         if extra is not None:
#             # Always emit via an adapter so extras survive to OTel attributes
#             if isinstance(self.logger, LoggerAdapter):
#                 merged = {**self.logger.extra, **extra}
#                 LoggerAdapter(self.logger.logger, merged).log(level, msg, *args, **kwargs)
#             else:
#                 LoggerAdapter(self.logger, extra).log(level, msg, *args, **kwargs)
#         else:
#             self.logger.log(level, msg, *args, **kwargs)
#
#     def debug(self, msg: str, *args, **kwargs):
#         self._log(logging.DEBUG, msg, *args, **kwargs)
#
#     def info(self, msg: str, *args, **kwargs):
#         self._log(logging.INFO, msg, *args, **kwargs)
#
#     def warning(self, msg: str, *args, **kwargs):
#         self._log(logging.WARNING, msg, *args, **kwargs)
#
#     def error(self, msg: str, *args, **kwargs):
#         self._log(logging.ERROR, msg, *args, **kwargs)
#
#     def critical(self, msg: str, *args, **kwargs):
#         self._log(logging.CRITICAL, msg, *args, **kwargs)
#
#
#     def bind(self, **extra: Any) -> LoggerAdapter:
#         """
#         Return a new LoggerAdapter bound with extra context, merging with existing extras if present.
#         Example:
#             api_log = logger.bind(component="api", request_id=req.id)
#             api_log.info("processing")
#         """
#         if isinstance(self.logger, LoggerAdapter):
#             merged = {**self.logger.extra, **extra}
#             return LoggerAdapter(self.logger.logger, merged)
#         return LoggerAdapter(self.logger, extra)
#
#     @contextmanager
#     def bound(self, **extra: Any):
#         """
#         Context manager that yields a bound adapter for temporary context.
#         Example:
#             with logger.bound(order_id=oid) as log:
#                 log.info("starting")
#                 ...
#         """
#         adapter = self.bind(**extra)
#         try:
#             yield adapter
#         finally:
#             # nothing to clean up; adapter is ephemeral
#             pass
#
#     def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
#         """
#         Start a span as a context manager.
#
#         Usage:
#             with logger.start_span("my-task", {"key": "value"}) as span:
#                 ...
#         """
#         if not self.enable_otel or not self.tracer:
#             self.warning("Tracing is disabled or not initialized. Cannot start span.")
#             from contextlib import nullcontext
#             return nullcontext()
#
#         cm = self.tracer.start_as_current_span(name)
#
#         class _SpanCtx:
#             def __enter__(_self):
#                 span = cm.__enter__()
#                 if attributes:
#                     for k, v in attributes.items():
#                         try:
#                             span.set_attribute(k, v)
#                         except Exception:
#                             pass
#                 return span
#
#             def __exit__(_self, exc_type, exc, tb):
#                 return cm.__exit__(exc_type, exc, tb)
#
#         return _SpanCtx()
#
#     def trace_function(self, span_name: Optional[str] = None):
#         """Decorator to trace a function with an optional custom span name."""
#         def decorator(func):
#             def wrapper(*args, **kwargs):
#                 name = span_name or func.__name__
#                 with self.start_span(name):
#                     return func(*args, **kwargs)
#             return wrapper
#         return decorator
#
#     # -------------------------
#     # Internal setup
#     # -------------------------
#
#     def _setup(self):
#         """Set up core logger, handlers, and optional OTel."""
#         # Configure base logger
#         self._core_logger = logging.getLogger(self.logger_name)
#         self._core_logger.setLevel(self.log_level)
#         self._core_logger.propagate = False
#
#         # Standard (file + console) handlers
#         self._setup_standard_handlers()
#
#         # OTel handlers (logs + traces)
#         if self.enable_otel:
#             self._setup_otel_handler()
#
#         # Public-facing logger (optionally wrapped with adapter extras)
#         if self.enable_otel and self.otel_stream_name:
#             attributes = {
#                 "log_stream": self.otel_stream_name,
#                 "log_service_name": self.otel_service_name,
#                 "logger_name": self.logger_name,
#             }
#             self.logger = LoggerAdapter(self._core_logger, extra=attributes)
#         else:
#             self.logger = self._core_logger
#
#     def _setup_standard_handlers(self):
#         """Sets up file and console handlers with deduping."""
#         os.makedirs(self.log_dir, exist_ok=True)
#         calling_script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
#         log_file_path = os.path.join(self.log_dir, f"{self.log_file}_{calling_script}.log")
#
#         formatter = logging.Formatter(
#             "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
#             datefmt="%Y-%m-%d %H:%M:%S",
#         )
#         formatter.converter = time.gmtime  # UTC timestamps
#
#         # File handler (dedupe by filename)
#         if not any(
#             isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", "") == os.path.abspath(log_file_path)
#             for h in self._core_logger.handlers
#         ):
#             file_handler = RotatingFileHandler(
#                 log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5, delay=True
#             )
#             file_handler.setFormatter(formatter)
#             self._core_logger.addHandler(file_handler)
#
#         # Console handler (dedupe by stream)
#         if not any(
#             isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stdout
#             for h in self._core_logger.handlers
#         ):
#             console_handler = logging.StreamHandler(sys.stdout)
#             console_handler.setFormatter(formatter)
#             self._core_logger.addHandler(console_handler)
#
#     def _normalize_otlp_endpoint(self, ep: str) -> str:
#         """Ensure OTLP gRPC endpoint has a scheme."""
#         if "://" not in ep:
#             ep = ("http://" if self.otel_insecure else "https://") + ep
#         return ep
#
#     def _setup_otel_handler(self):
#         """
#         Configure OpenTelemetry providers, exporters, and attach a LoggingHandler.
#         - service.name: used by most backends (incl. OpenObserve) to group streams/services.
#         - log.stream: extra attribute you can filter on in the backend.
#         """
#         resource_attrs = {
#             "service.name": self.otel_service_name,
#             "logger.name": self.logger_name,
#         }
#         if self.otel_stream_name:
#             resource_attrs["log.stream"] = self.otel_stream_name
#
#         resource = Resource.create(resource_attrs)
#
#         # Logs provider
#         self.logger_provider = LoggerProvider(resource=resource)
#         set_logger_provider(self.logger_provider)
#
#         # Traces provider
#         self.tracer_provider = TracerProvider(resource=resource)
#         trace.set_tracer_provider(self.tracer_provider)
#
#         endpoint = self._normalize_otlp_endpoint(self.otel_endpoint)
#
#         # Logs exporter + processor
#         log_exporter = OTLPLogExporter(endpoint=endpoint, insecure=self.otel_insecure)
#         self.logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
#
#         # Traces exporter + processor
#         span_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=self.otel_insecure)
#         self.tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
#         self.tracer = trace.get_tracer(self.logger_name, tracer_provider=self.tracer_provider)
#
#         # Attach OTel LoggingHandler once
#         if not any(type(h).__name__ == "LoggingHandler" for h in self._core_logger.handlers):
#             otel_handler = LoggingHandler(level=logging.NOTSET, logger_provider=self.logger_provider)
#             self._core_logger.addHandler(otel_handler)
#
#         self._core_logger.info("OpenTelemetry logging and tracing enabled and attached.")
#
