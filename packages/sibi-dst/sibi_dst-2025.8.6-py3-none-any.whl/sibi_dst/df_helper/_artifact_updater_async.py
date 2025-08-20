from __future__ import annotations

import asyncio
import datetime
import random
import time
from contextlib import ExitStack
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Type

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
    "update_timeout_seconds",
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


class ArtifactUpdaterMultiWrapperAsync(ManagedResource):
    """
    Backward-compatible async orchestrator with shutdown-aware scheduling.
    """

    def __init__(
        self,
        wrapped_classes: Dict[str, Sequence[Type]],
        *,
        max_workers: int = 3,
        retry_attempts: int = 3,
        update_timeout_seconds: int = 600,
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
        self.update_timeout_seconds = int(update_timeout_seconds)
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

        # NEW: async stop gate — tripped on cleanup/cancel
        self._stop = asyncio.Event()

    # Trip stop gate on close paths
    def _cleanup(self) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(self._stop.set)
        except RuntimeError:
            self._stop.set()

    async def _acleanup(self) -> None:
        self._stop.set()

    # ---- internals -----------------------------------------------------------

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

    async def _run_one(self, cls: Type, period: str, sem: asyncio.Semaphore, artifact_kwargs: Dict[str, Any]) -> None:
        name = cls.__name__
        if self._stop.is_set() or self.closed:
            raise asyncio.CancelledError()

        self.logger.info(f"Running {name} with period '{period}'", extra={"artifact": name, "period": period})
        async with sem:
            loop = asyncio.get_running_loop()
            start = loop.time()
            for attempt in range(1, self._retry.attempts + 1):
                if self._stop.is_set() or self.closed:
                    raise asyncio.CancelledError()
                try:
                    def _sync_block() -> None:
                        with ExitStack() as stack:
                            inst = cls(**self.artifact_class_kwargs)
                            inst = stack.enter_context(inst)
                            inst.update_parquet(period=period, **artifact_kwargs)

                    await asyncio.wait_for(asyncio.to_thread(_sync_block), timeout=self.update_timeout_seconds)
                    dt_secs = loop.time() - start
                    self.completion_secs[name] = dt_secs
                    self.logger.info(f"✅ {name} ({period}) in {dt_secs:.2f}s")
                    return

                except asyncio.TimeoutError:
                    self.logger.warning(f"Timeout in {name} attempt {attempt}/{self._retry.attempts}")
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    self.logger.error(
                        f"{name} attempt {attempt}/{self._retry.attempts} failed: {e}",
                        exc_info=self.debug,
                    )

                if attempt < self._retry.attempts and not self._stop.is_set():
                    delay = min(self._retry.backoff_base ** (attempt - 1), self._retry.backoff_max)
                    delay *= 1 + random.uniform(0, self._retry.jitter)
                    try:
                        await asyncio.sleep(delay)
                    except asyncio.CancelledError:
                        raise

            self.failed.append(name)
            self.logger.error(f"✖️  {name} permanently failed")

    # ---- public API ----------------------------------------------------------

    async def update_data(self, period: str, **kwargs: Any) -> None:
        """
        Backward-compatible:
          - Accepts orchestrator knobs in kwargs (we consume them).
          - Forwards only artifact-friendly kwargs to update_parquet.
        """
        _, artifact_kwargs = self._split_kwargs(kwargs)

        self.completion_secs.clear()
        self.failed.clear()

        classes = self._classes_for(period)
        self.logger.info(
            f"Starting update of {len(classes)} artifacts for period '{period}'",
            extra={
                "action_module_name": self.__class__.__name__,
                "date_of_update": time.strftime('%Y-%m-%d'),
                "start_time": time.strftime('%H:%M:%S'),
                "period": period,
            },
        )

        sem = asyncio.Semaphore(self.max_workers)
        tasks = [asyncio.create_task(self._run_one(cls, period, sem, dict(artifact_kwargs))) for cls in classes]

        try:
            for t in asyncio.as_completed(tasks):
                if self._stop.is_set():
                    break
                await t
        except (asyncio.CancelledError, KeyboardInterrupt):
            self._stop.set()
            for t in tasks:
                t.cancel()
            raise
        finally:
            # Drain/cancel everything deterministically
            for t in tasks:
                if not t.done():
                    t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

            self.logger.info(
                f"Update completed for period: {period}",
                extra={
                    "action_module_name": self.__class__.__name__,
                    "date_of_update": datetime.date.today().strftime('%Y-%m-%d'),
                    "end_time": datetime.datetime.now().strftime('%H:%M:%S'),
                    "period": period,
                },
            )
            self.logger.info(
                f"Artifacts processed: total={len(classes)}, "
                f"completed={len(self.completion_secs)}, failed={len(self.failed)}"
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