from __future__ import annotations

import datetime
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import ExitStack
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Tuple

from sibi_dst.utils import ManagedResource


@dataclass(slots=True)
class _RetryCfg:
    attempts: int = 3
    backoff_base: float = 2.0
    backoff_max: float = 60.0
    jitter: float = 0.15


_ORCHESTRATOR_KEYS = {
    "retry_attempts",
    "backoff_base",
    "backoff_max",
    "backoff_jitter",
    "update_timeout_seconds",  # accepted but unused in pure-threads version
    "max_workers",
    "priority_fn",
    "artifact_class_kwargs",
}


def _default_artifact_kwargs(resource: ManagedResource) -> Dict[str, Any]:
    return {
        "logger": resource.logger,
        "debug": resource.debug,
        "fs": resource.fs,
        "verbose": resource.verbose,
    }


class ArtifactUpdaterMultiWrapperThreaded(ManagedResource):
    """
    Backward-compatible threaded orchestrator with shutdown-aware scheduling.
    """

    def __init__(
        self,
        wrapped_classes: Dict[str, Sequence[Type]],
        *,
        max_workers: int = 4,
        retry_attempts: int = 3,
        backoff_base: float = 2.0,
        backoff_max: float = 60.0,
        backoff_jitter: float = 0.15,
        priority_fn: Optional[Callable[[Type], int]] = None,
        artifact_class_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.wrapped_classes = wrapped_classes
        self.max_workers = int(max_workers)
        self.priority_fn = priority_fn
        self._retry = _RetryCfg(
            attempts=int(retry_attempts),
            backoff_base=float(backoff_base),
            backoff_max=float(backoff_max),
            jitter=float(backoff_jitter),
        )
        self.artifact_class_kwargs = {
            **_default_artifact_kwargs(self),
            **(artifact_class_kwargs or {}),
        }
        self.completion_secs: Dict[str, float] = {}
        self.failed: List[str] = []

        # NEW: stop gate — tripped on cleanup / Ctrl-C to stop scheduling & retries
        self._stop_event = threading.Event()

    # Trip the stop gate when this wrapper is closed
    def _cleanup(self) -> None:
        self._stop_event.set()

    def _classes_for(self, period: str) -> List[Type]:
        try:
            classes = list(self.wrapped_classes[period])
        except KeyError:
            raise ValueError(f"Unsupported period '{period}'.")
        if not classes:
            raise ValueError(f"No artifact classes configured for period '{period}'.")
        if self.priority_fn:
            try:
                classes.sort(key=self.priority_fn)
            except Exception as e:
                self.logger.warning(f"priority_fn failed; using listed order: {e}")
        return classes

    @staticmethod
    def _split_kwargs(raw: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        orch: Dict[str, Any] = {}
        art: Dict[str, Any] = {}
        for k, v in raw.items():
            if k in _ORCHESTRATOR_KEYS:
                orch[k] = v
            else:
                art[k] = v
        return orch, art

    def _run_one(self, cls: Type, period: str, artifact_kwargs: Dict[str, Any]) -> str:
        name = cls.__name__
        start = time.monotonic()
        for attempt in range(1, self._retry.attempts + 1):
            if self._stop_event.is_set() or self.closed:
                raise RuntimeError("shutting_down")
            try:
                with ExitStack() as stack:
                    inst = cls(**self.artifact_class_kwargs)
                    inst = stack.enter_context(inst)
                    inst.update_parquet(period=period, **artifact_kwargs)
                self.completion_secs[name] = time.monotonic() - start
                return name
            except Exception as e:
                if attempt < self._retry.attempts and not self._stop_event.is_set():
                    # interruptible backoff sleep
                    delay = min(self._retry.backoff_base ** (attempt - 1), self._retry.backoff_max)
                    delay *= 1 + random.uniform(0, self._retry.jitter)
                    end = time.monotonic() + delay
                    while not self._stop_event.is_set() and time.monotonic() < end:
                        time.sleep(min(0.1, end - time.monotonic()))
                    continue
                raise RuntimeError(f"{name} failed after {self._retry.attempts} attempts: {e}") from e

    def update_data(self, period: str, **kwargs: Any) -> None:
        # Split kwargs to preserve backward compatibility
        _, artifact_kwargs = self._split_kwargs(kwargs)

        self.completion_secs.clear()
        self.failed.clear()

        classes = self._classes_for(period)

        executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="artifact-updater")
        try:
            fut2name: Dict[Any, str] = {}
            for cls in classes:
                if self._stop_event.is_set() or self.closed:
                    break
                try:
                    fut = executor.submit(self._run_one, cls, period, dict(artifact_kwargs))
                except RuntimeError as e:
                    if "cannot schedule new futures after shutdown" in str(e).lower():
                        self.logger.warning("Executor shutting down; halting new submissions.")
                        break
                    raise
                fut2name[fut] = cls.__name__

            for fut in as_completed(fut2name):
                name = fut2name[fut]
                try:
                    fut.result()
                    self.logger.info(f"✅ {name} ({period}) in {self.completion_secs[name]:.2f}s")
                except Exception as e:
                    self.failed.append(name)
                    self.logger.error(f"✖️  {name} permanently failed: {e}")
        except KeyboardInterrupt:
            self.logger.warning("KeyboardInterrupt — stopping scheduling and shutting down.")
            self._stop_event.set()
            raise
        finally:
            # Ensure queued-but-not-started tasks are canceled
            executor.shutdown(wait=True, cancel_futures=True)

        self.logger.info(
            f"Artifacts processed: total={len(classes)}, "
            f"completed={len(self.completion_secs)}, failed={len(self.failed)}",
            extra={
                "date_of_update": time.strftime('%Y-%m-%d'),
                "start_time": time.strftime('%H:%M:%S'),
                "period": period,
            },
        )

    def get_update_status(self) -> Dict[str, Any]:
        done = set(self.completion_secs)
        fail = set(self.failed)
        all_names = {c.__name__ for v in self.wrapped_classes.values() for c in v}
        return {
            "total": len(all_names),
            "completed": sorted(done),
            "failed": sorted(fail),
            "pending": sorted(all_names - done - fail),
            "completion_times": dict(self.completion_secs),
        }