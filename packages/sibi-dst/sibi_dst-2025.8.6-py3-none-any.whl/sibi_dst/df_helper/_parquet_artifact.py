from __future__ import annotations

import datetime as dt
import threading
from functools import cached_property
from typing import Any, Dict, Type, TypeVar

from sibi_dst.utils import DataWrapper, DateUtils, UpdatePlanner, ManagedResource
from sibi_dst.utils import MissingManifestManager, Logger

T = TypeVar("T")


class ParquetArtifact(ManagedResource):
    """
    Orchestrates a single dataset:
      - Builds/uses MissingManifestManager
      - Plans work with UpdatePlanner
      - Executes with DataWrapper (threaded) saving Dask → Parquet
      - Prevents duplicate concurrent runs per (storage_path, filename)
      - Forwards retry/backoff knobs to DataWrapper.process()
    """

    _global_lock = threading.RLock()
    _active_runs: set[tuple[str, str]] = set()

    def __init__(self, **kwargs: Any):
        # Merge defaults from ManagedResource and caller kwargs
        self.all_kwargs: Dict[str, Any] = {**kwargs}
        super().__init__(**self.all_kwargs)

        # Persist the minimal config we depend on frequently
        self._lock = threading.RLock()

        # Required knobs
        self._storage_path: str = self.all_kwargs["parquet_storage_path"]
        self._parquet_filename: str = self.all_kwargs["parquet_filename"]
        self._data_wrapper_class = self.all_kwargs.get("data_wrapper_class")

    # ---------- helpers ----------
    def _invalidate_cached(self, *names: str) -> None:
        for n in names:
            self.__dict__.pop(n, None)

    def _build_manifest_path(self) -> str:
        base = f"{self._storage_path}".rstrip("/") + "/"
        return f"{base}_manifests/missing.parquet"

    # ---------- lazy members ----------
    @cached_property
    def mmanifest(self) -> MissingManifestManager:
        self.logger.info("Initializing MissingManifestManager...")
        manifest_path = self._build_manifest_path()

        # ensure manifest directory exists
        manifest_dir = manifest_path.rsplit("/", 1)[0] if "/" in manifest_path else manifest_path
        self.ensure_directory_exists(manifest_dir)

        mgr = MissingManifestManager(
            fs=self.fs,
            manifest_path=manifest_path,
            clear_existing=self.all_kwargs.get("overwrite", False),
            debug=self.debug,
            logger=self.logger,
            overwrite=self.all_kwargs.get("overwrite", False),
        )

        if not mgr._safe_exists(mgr.manifest_path):
            self.logger.info(f"Creating new manifest at {mgr.manifest_path}")
            mgr.save()
        else:
            self.logger.info(f"Manifest already exists at {mgr.manifest_path}")

        return mgr

    @cached_property
    def update_planner(self) -> UpdatePlanner:
        self.logger.info("Initializing UpdatePlanner...")
        skipped_files = self.mmanifest.load_existing() or []

        cfg = {
            **self.all_kwargs,
            "fs": self.fs,
            "debug": self.debug,
            "logger": self.logger,
            "description": getattr(self._data_wrapper_class, "__name__", "DataWrapper"),
            "skipped": list(skipped_files),
            "mmanifest": self.mmanifest,
        }
        return UpdatePlanner(**cfg)

    @cached_property
    def data_wrapper(self) -> DataWrapper:
        self.logger.info("Initializing DataWrapper...")

        # Ensure the planner has a plan
        if getattr(self.update_planner, "plan", None) is None:
            self.update_planner.generate_plan()

        class_params = {
            "debug": self.debug,
            "logger": self.logger,
            "fs": self.fs,
            "verbose": self.verbose,
        }

        cfg = {
            "data_path": self._storage_path,
            "parquet_filename": self._parquet_filename,
            "fs": self.fs,
            "debug": self.debug,
            "logger": self.logger,
            "verbose": self.verbose,
            "dataclass": self._data_wrapper_class,
            "class_params": class_params,
            "load_params": self.all_kwargs.get("load_params", {}) or {},
            "mmanifest": self.mmanifest,
            "update_planner": self.update_planner,
            "date_field": self.all_kwargs.get("date_field"),
            # pipeline execution knobs
            "show_progress": bool(self.all_kwargs.get("show_progress", False)),
            "timeout": float(self.all_kwargs.get("timeout", 30.0)),
            "max_threads": int(self.all_kwargs.get("max_threads", 3)),
        }
        return DataWrapper(**cfg)

    # ---------- public API ----------
    def load(self, **kwargs: Any):
        """
        Direct load using the configured data_wrapper_class (no planner/manifest round-trip).
        Expected to return a Dask DataFrame from the loader.
        """
        self.logger.info(f"Loading data from {self._storage_path}")

        if not self._data_wrapper_class:
            raise ValueError("data_wrapper_class is not configured.")

        params = {
            "backend": "parquet",
            "fs": self.fs,
            "logger": self.logger,
            "debug": self.debug,
            "parquet_storage_path": self._storage_path,
            "parquet_filename": self._parquet_filename,
            "parquet_start_date": self.all_kwargs.get("parquet_start_date"),
            "parquet_end_date": self.all_kwargs.get("parquet_end_date"),
            **(self.all_kwargs.get("class_params") or {}),
        }

        cls = self._data_wrapper_class
        with cls(**params) as instance:
            return instance.load(**kwargs)

    def generate_parquet(self, **kwargs: Any) -> None:
        """
        Generate or update Parquet according to the plan.
        - Merges runtime kwargs
        - Invalidates dependent caches
        - Guards against duplicate concurrent runs
        - Forwards retry/backoff to DataWrapper.process()
        """
        # Merge and invalidate caches that depend on runtime changes
        self.all_kwargs.update(kwargs)
        self._invalidate_cached("update_planner", "data_wrapper")
        if "overwrite" in kwargs:
            self._invalidate_cached("mmanifest")

        # Global de-dupe guard
        key = (self._storage_path, self._parquet_filename)
        with ParquetArtifact._global_lock:
            if key in ParquetArtifact._active_runs:
                self.logger.info(
                    f"Run already in progress for {key}; skipping this invocation."
                )
                return
            ParquetArtifact._active_runs.add(key)

        try:
            self.ensure_directory_exists(self._storage_path)

            self.update_planner.generate_plan()
            plan = getattr(self.update_planner, "plan", None)
            if plan is None or (hasattr(plan, "empty") and plan.empty):
                # Planning uses Pandas; this is safe to check.
                self.logger.info("No updates needed. Skipping Parquet generation.")
                return

            # Print plan once per run
            if (
                getattr(self.update_planner, "show_progress", False)
                and not getattr(self.update_planner, "_printed_this_run", False)
            ):
                self.update_planner.show_update_plan()
                setattr(self.update_planner, "_printed_this_run", True)

            # ---- forward retry/backoff knobs to DataWrapper.process() ----
            dw_retry_kwargs = {
                k: self.all_kwargs[k]
                for k in ("max_retries", "backoff_base", "backoff_jitter", "backoff_max")
                if k in self.all_kwargs
            }

            with self._lock:
                dw = self.data_wrapper  # single cached_property access
                if hasattr(dw, "process"):
                    dw.process(**dw_retry_kwargs)
                    if getattr(self.update_planner, "show_progress", False) and hasattr(
                        dw, "show_benchmark_summary"
                    ):
                        dw.show_benchmark_summary()

        finally:
            with ParquetArtifact._global_lock:
                ParquetArtifact._active_runs.discard(key)

    def update_parquet(self, period: str = "today", **kwargs: Any) -> None:
        """
        High-level entry point to update Parquet for a given period:
          - 'today', 'yesterday', 'last_7_days', etc. via DateUtils.parse_period
          - 'ytd'
          - 'itd' (requires history_begins_on)
          - 'custom' (requires start_on / end_on)
        Also accepts retry/backoff knobs which flow to DataWrapper.process().
        """
        final_kwargs = {**self.all_kwargs, **kwargs}

        def itd_config():
            start_date = final_kwargs.get("history_begins_on")
            if not start_date:
                raise ValueError(
                    "For period 'itd', 'history_begins_on' must be configured."
                )
            return {
                "parquet_start_date": start_date,
                "parquet_end_date": dt.date.today(),
            }

        def ytd_config():
            return {
                "parquet_start_date": dt.date(dt.date.today().year, 1, 1),
                "parquet_end_date": dt.date.today(),
            }

        def custom_config():
            """
                Prepare parameters for 'custom' period execution, ensuring `start_on` and `end_on`
                are provided (with backward compatibility for `start_date`/`end_date` aliases).
                """
            # Backward compatibility: normalize aliases
            alias_map = {
                "start_on": ("start_date", "start"),
                "end_on": ("end_date", "end"),
            }
            normalized_kwargs = dict(kwargs)  # shallow copy so we don't mutate original
            for target, aliases in alias_map.items():
                if target not in normalized_kwargs:
                    for alias in aliases:
                        if alias in normalized_kwargs:
                            normalized_kwargs[target] = normalized_kwargs[alias]
                            break

            # Validation
            missing = [k for k in ("start_on", "end_on") if k not in normalized_kwargs]
            if missing:
                raise ValueError(
                    f"For period 'custom', the following required parameters are missing: {', '.join(missing)}"
                )

            return {
                "parquet_start_date": normalized_kwargs["start_on"],
                "parquet_end_date": normalized_kwargs["end_on"],
            }

        if period == "itd":
            period_params = itd_config()
        elif period == "ytd":
            period_params = ytd_config()
        elif period == "custom":
            period_params = custom_config()
        else:
            start_date, end_date = DateUtils.parse_period(period=period)
            period_params = {
                "parquet_start_date": start_date,
                "parquet_end_date": end_date,
            }

        final_kwargs.update(period_params)
        self.logger.debug(
            f"kwargs passed to update_parquet/generate_parquet: {final_kwargs}"
        )

        # Delegate to generator (handles cache invalidation + forwarding knobs)
        self.generate_parquet(**final_kwargs)

    # ---------- utils ----------
    def ensure_directory_exists(self, path: str) -> None:
        """Ensure the directory exists across fsspec backends."""
        with self._lock:
            if not self.fs.exists(path):
                self.logger.info(f"Creating directory: {path}")
                try:
                    self.fs.makedirs(path, exist_ok=True)
                except TypeError:
                    try:
                        self.fs.makedirs(path)
                    except FileExistsError:
                        pass

    def _cleanup(self):
        """Clean up resources upon exit."""
        try:
            if "mmanifest" in self.__dict__ and getattr(
                self.mmanifest, "_new_records", None
            ):
                if self.mmanifest._new_records:
                    self.mmanifest.save()
            if "data_wrapper" in self.__dict__ and hasattr(self.data_wrapper, "close"):
                self.data_wrapper.close()
        except Exception as e:
            self.logger.warning(f"Error during resource cleanup: {e}")