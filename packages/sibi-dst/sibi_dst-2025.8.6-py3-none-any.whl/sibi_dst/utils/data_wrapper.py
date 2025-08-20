import datetime
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Type, Any, Dict, Optional, Union, List, ClassVar

import pandas as pd
from tqdm import tqdm

from . import ManagedResource
from .parquet_saver import ParquetSaver


class DataWrapper(ManagedResource):
    DEFAULT_PRIORITY_MAP: ClassVar[Dict[str, int]] = {
        "overwrite": 1,
        "missing_in_history": 2,
        "existing_but_stale": 3,
        "missing_outside_history": 4,
        "file_is_recent": 0,
    }
    DEFAULT_MAX_AGE_MINUTES: int = 1440
    DEFAULT_HISTORY_DAYS_THRESHOLD: int = 30

    def __init__(
        self,
        dataclass: Type,
        date_field: str,
        data_path: str,
        parquet_filename: str,
        class_params: Optional[Dict] = None,
        load_params: Optional[Dict] = None,
        show_progress: bool = False,
        timeout: float = 30,
        max_threads: int = 3,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.dataclass = dataclass
        self.date_field = date_field
        self.data_path = self._ensure_forward_slash(data_path)
        self.parquet_filename = parquet_filename
        if self.fs is None:
            raise ValueError("DataWrapper requires a File system (fs) to be provided.")
        self.show_progress = show_progress
        self.timeout = timeout
        self.max_threads = max_threads
        self.class_params = class_params or {
            "debug": self.debug,
            "logger": self.logger,
            "fs": self.fs,
            "verbose": self.verbose,
        }
        self.load_params = load_params or {}

        self._lock = threading.Lock()
        self.processed_dates: List[datetime.date] = []
        self.benchmarks: Dict[datetime.date, Dict[str, float]] = {}
        self.mmanifest = kwargs.get("mmanifest", None)
        self.update_planner = kwargs.get("update_planner", None)

        # --- NEW: stop gate tripped during cleanup/interrupt to block further scheduling/retries
        self._stop_event = threading.Event()
        self.extra_logger = {"action_module_name": "data_wrapper", "dataclass": self.dataclass.__name__}

    # ensure manifest is saved on context exit
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mmanifest:
            self.mmanifest.save()
        super().__exit__(exc_type, exc_val, exc_tb)
        return False

    # --- NEW: trip stop gate during class-specific cleanup (close/aclose/finalizer path)
    def _cleanup(self) -> None:
        self._stop_event.set()

    @staticmethod
    def _convert_to_date(date: Union[datetime.date, str]) -> datetime.date:
        if isinstance(date, datetime.date):
            return date
        try:
            return pd.to_datetime(date).date()
        except ValueError as e:
            raise ValueError(f"Error converting {date} to datetime: {e}")

    @staticmethod
    def _ensure_forward_slash(path: str) -> str:
        return path.rstrip("/") + "/"

    def process(
        self,
        max_retries: int = 3,
        backoff_base: float = 2.0,
        backoff_jitter: float = 0.1,
        backoff_max: float = 60.0,
    ):
        """
        Execute the update plan with concurrency, retries and exponential backoff.
        Stops scheduling immediately if closed or interrupted (Ctrl-C).
        """
        overall_start = time.perf_counter()
        tasks = list(self.update_planner.get_tasks_by_priority())
        if not tasks:
            self.logger.info("No updates required based on the current plan.")
            return

        if self.update_planner.show_progress:
            self.update_planner.show_update_plan()

        try:
            for priority, dates in tasks:
                if self._stop_event.is_set():
                    break
                self._execute_task_batch(priority, dates, max_retries, backoff_base, backoff_jitter, backoff_max)
        except KeyboardInterrupt:
            self.logger.warning("KeyboardInterrupt received — stopping scheduling and shutting down.")
            self._stop_event.set()
            raise
        finally:
            total_time = time.perf_counter() - overall_start
            if self.processed_dates:
                count = len(self.processed_dates)
                self.logger.info(f"Processed {count} dates in {total_time:.1f}s (avg {total_time / count:.1f}s/date)")
                if self.update_planner.show_progress:
                    self.show_benchmark_summary()

    def _execute_task_batch(
        self,
        priority: int,
        dates: List[datetime.date],
        max_retries: int,
        backoff_base: float,
        backoff_jitter: float,
        backoff_max: float,
    ):
        desc = f"Processing {self.dataclass.__name__}, priority: {priority}"
        max_thr = min(len(dates), self.max_threads)
        self.logger.info(f"Executing {len(dates)} tasks with priority {priority} using {max_thr} threads.", extra=self.extra_logger)

        # Use explicit try/finally so we can request cancel of queued tasks on teardown
        executor = ThreadPoolExecutor(max_workers=max_thr, thread_name_prefix="datawrapper")
        try:
            futures = {}
            for date in dates:
                if self._stop_event.is_set():
                    break
                try:
                    fut = executor.submit(
                        self._process_date_with_retry, date, max_retries, backoff_base, backoff_jitter, backoff_max
                    )
                    futures[fut] = date
                except RuntimeError as e:
                    # tolerate race: executor shutting down
                    if "cannot schedule new futures after shutdown" in str(e).lower():
                        self.logger.warning("Executor is shutting down; halting new submissions for this batch.")
                        break
                    raise

            iterator = as_completed(futures)
            if self.show_progress:
                iterator = tqdm(iterator, total=len(futures), desc=desc)

            for future in iterator:
                try:
                    future.result(timeout=self.timeout)
                except Exception as e:
                    self.logger.error(f"Permanent failure for {futures[future]}: {e}", extra=self.extra_logger)
        finally:
            # Python 3.9+: cancel_futures prevents queued tasks from starting
            executor.shutdown(wait=True, cancel_futures=True)

    def _process_date_with_retry(
        self,
        date: datetime.date,
        max_retries: int,
        backoff_base: float,
        backoff_jitter: float,
        backoff_max: float,
    ):
        for attempt in range(max_retries):
            # --- NEW: bail out quickly if shutdown/interrupt began
            if self._stop_event.is_set():
                raise RuntimeError("shutting_down")

            try:
                self._process_single_date(date)
                return
            except Exception as e:
                if attempt < max_retries - 1 and not self._stop_event.is_set():
                    base_delay = min(backoff_base ** attempt, backoff_max)
                    delay = base_delay * (1 + random.uniform(0.0, max(0.0, backoff_jitter)))
                    self.logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {date}: {e} (sleep {delay:.2f}s)"
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(f"Failed processing {date} after {max_retries} attempts.", extra=self.extra_logger)
                    raise

    def _process_single_date(self, date: datetime.date):
        path = f"{self.data_path}{date.year}/{date.month:02d}/{date.day:02d}/"
        self.logger.debug(f"Processing date {date.isoformat()} for {path}")
        if path in self.update_planner.skipped and self.update_planner.ignore_missing:
            self.logger.debug(f"Skipping {date} as it exists in the skipped list")
            return
        full_path = f"{path}{self.parquet_filename}"

        overall_start = time.perf_counter()
        try:
            load_start = time.perf_counter()
            date_filter = {f"{self.date_field}__date": {date.isoformat()}}
            self.logger.debug(f"Loading data for {date} with filter: {date_filter}")

            local_load_params = self.load_params.copy()
            local_load_params.update(date_filter)

            with self.dataclass(**self.class_params) as local_class_instance:
                df = local_class_instance.load(**local_load_params)  # expected to be Dask
                load_time = time.perf_counter() - load_start

                if hasattr(local_class_instance, "total_records"):
                    total_records = int(local_class_instance.total_records)
                    self.logger.debug(f"Total records loaded: {total_records}")

                    if total_records == 0:
                        if self.mmanifest:
                            self.mmanifest.record(full_path=path)
                        self.logger.info(f"No data found for {full_path}. Logged to missing manifest.")
                        return

                    if total_records < 0:
                        self.logger.warning(f"Negative record count ({total_records}) for {full_path}.")
                        return

                save_start = time.perf_counter()
                parquet_params = {
                    "df_result": df,
                    "parquet_storage_path": path,
                    "fs": self.fs,
                    "logger": self.logger,
                    "debug": self.debug,
                }
                with ParquetSaver(**parquet_params) as ps:
                    ps.save_to_parquet(self.parquet_filename, overwrite=True)
                save_time = time.perf_counter() - save_start

                total_time = time.perf_counter() - overall_start
                self.benchmarks[date] = {
                    "load_duration": load_time,
                    "save_duration": save_time,
                    "total_duration": total_time,
                }
                self._log_success(date, total_time, full_path)

        except Exception as e:
            self._log_failure(date, e)
            raise

    def _log_success(self, date: datetime.date, duration: float, path: str):
        self.logger.info(f"Completed {date} in {duration:.1f}s | Saved to {path}", extra=self.extra_logger)
        self.processed_dates.append(date)

    def _log_failure(self, date: datetime.date, error: Exception):
        self.logger.error(f"Failed processing {date}: {error}", extra=self.extra_logger)

    def show_benchmark_summary(self):
        if not self.benchmarks:
            self.logger.info("No benchmarking data to show", extra=self.extra_logger)
            return
        df_bench = pd.DataFrame.from_records([{"date": d, **m} for d, m in self.benchmarks.items()])
        df_bench = df_bench.set_index("date").sort_index(ascending=not self.update_planner.reverse_order)
        self.logger.info(f"Benchmark Summary:\n {self.dataclass.__name__}\n" + df_bench.to_string(), extra=self.extra_logger)

# import datetime
# import threading
# import time
# import random
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from typing import Type, Any, Dict, Optional, Union, List, ClassVar
#
# import dask.dataframe as dd
# import pandas as pd
# from tqdm import tqdm
#
# from . import ManagedResource
# from .parquet_saver import ParquetSaver
#
#
# class DataWrapper(ManagedResource):
#     DEFAULT_PRIORITY_MAP: ClassVar[Dict[str, int]] = {
#         "overwrite": 1,
#         "missing_in_history": 2,
#         "existing_but_stale": 3,
#         "missing_outside_history": 4,
#         "file_is_recent": 0,
#     }
#     DEFAULT_MAX_AGE_MINUTES: int = 1440
#     DEFAULT_HISTORY_DAYS_THRESHOLD: int = 30
#
#     def __init__(
#         self,
#         dataclass: Type,
#         date_field: str,
#         data_path: str,
#         parquet_filename: str,
#         class_params: Optional[Dict] = None,
#         load_params: Optional[Dict] = None,
#         show_progress: bool = False,
#         timeout: float = 30,
#         max_threads: int = 3,
#         **kwargs: Any,
#     ):
#         super().__init__(**kwargs)
#         self.dataclass = dataclass
#         self.date_field = date_field
#         self.data_path = self._ensure_forward_slash(data_path)
#         self.parquet_filename = parquet_filename
#         if self.fs is None:
#             raise ValueError("DataWrapper requires a File system (fs) to be provided.")
#         self.show_progress = show_progress
#         self.timeout = timeout
#         self.max_threads = max_threads
#         self.class_params = class_params or {
#             "debug": self.debug,
#             "logger": self.logger,
#             "fs": self.fs,
#             "verbose": self.verbose,
#         }
#         self.load_params = load_params or {}
#
#         self._lock = threading.Lock()
#         self.processed_dates: List[datetime.date] = []
#         self.benchmarks: Dict[datetime.date, Dict[str, float]] = {}
#         self.mmanifest = kwargs.get("mmanifest", None)
#         self.update_planner = kwargs.get("update_planner", None)
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self.mmanifest:
#             self.mmanifest.save()
#         super().__exit__(exc_type, exc_val, exc_tb)
#         return False
#
#     @staticmethod
#     def _convert_to_date(date: Union[datetime.date, str]) -> datetime.date:
#         if isinstance(date, datetime.date):
#             return date
#         try:
#             return pd.to_datetime(date).date()
#         except ValueError as e:
#             raise ValueError(f"Error converting {date} to datetime: {e}")
#
#     @staticmethod
#     def _ensure_forward_slash(path: str) -> str:
#         return path.rstrip("/") + "/"
#
#     def process(
#         self,
#         max_retries: int = 3,
#         backoff_base: float = 2.0,
#         backoff_jitter: float = 0.1,
#         backoff_max: float = 60.0,
#     ):
#         """
#         Execute the update plan with concurrency, retries and exponential backoff.
#
#         Args:
#             max_retries: attempts per date.
#             backoff_base: base for exponential backoff (delay = base**attempt).
#             backoff_jitter: multiplicative jitter factor in [0, backoff_jitter].
#             backoff_max: maximum backoff seconds per attempt (before jitter).
#         """
#         overall_start = time.perf_counter()
#         tasks = list(self.update_planner.get_tasks_by_priority())
#         if not tasks:
#             self.logger.info("No updates required based on the current plan.")
#             return
#
#         if self.update_planner.show_progress:
#             self.update_planner.show_update_plan()
#
#         for priority, dates in tasks:
#             self._execute_task_batch(priority, dates, max_retries, backoff_base, backoff_jitter, backoff_max)
#
#         total_time = time.perf_counter() - overall_start
#         if self.processed_dates:
#             count = len(self.processed_dates)
#             self.logger.info(f"Processed {count} dates in {total_time:.1f}s (avg {total_time / count:.1f}s/date)")
#             if self.update_planner.show_progress:
#                 self.show_benchmark_summary()
#
#     def _execute_task_batch(
#         self,
#         priority: int,
#         dates: List[datetime.date],
#         max_retries: int,
#         backoff_base: float,
#         backoff_jitter: float,
#         backoff_max: float,
#     ):
#         desc = f"Processing {self.dataclass.__name__}, priority: {priority}"
#         max_thr = min(len(dates), self.max_threads)
#         self.logger.info(f"Executing {len(dates)} tasks with priority {priority} using {max_thr} threads.")
#
#         with ThreadPoolExecutor(max_workers=max_thr) as executor:
#             futures = {
#                 executor.submit(
#                     self._process_date_with_retry, date, max_retries, backoff_base, backoff_jitter, backoff_max
#                 ): date
#                 for date in dates
#             }
#             iterator = as_completed(futures)
#             if self.show_progress:
#                 iterator = tqdm(iterator, total=len(futures), desc=desc)
#
#             for future in iterator:
#                 try:
#                     future.result(timeout=self.timeout)
#                 except Exception as e:
#                     self.logger.error(f"Permanent failure for {futures[future]}: {e}")
#
#     def _process_date_with_retry(
#         self,
#         date: datetime.date,
#         max_retries: int,
#         backoff_base: float,
#         backoff_jitter: float,
#         backoff_max: float,
#     ):
#         for attempt in range(max_retries):
#             try:
#                 self._process_single_date(date)
#                 return
#             except Exception as e:
#                 if attempt < max_retries - 1:
#                     base_delay = min(backoff_base ** attempt, backoff_max)
#                     delay = base_delay * (1 + random.uniform(0.0, max(0.0, backoff_jitter)))
#                     self.logger.warning(
#                         f"Retry {attempt + 1}/{max_retries} for {date}: {e} (sleep {delay:.2f}s)"
#                     )
#                     time.sleep(delay)
#                 else:
#                     self.logger.error(f"Failed processing {date} after {max_retries} attempts.")
#
#     def _process_single_date(self, date: datetime.date):
#         path = f"{self.data_path}{date.year}/{date.month:02d}/{date.day:02d}/"
#         self.logger.debug(f"Processing date {date.isoformat()} for {path}")
#         if path in self.update_planner.skipped and self.update_planner.ignore_missing:
#             self.logger.debug(f"Skipping {date} as it exists in the skipped list")
#             return
#         full_path = f"{path}{self.parquet_filename}"
#
#         overall_start = time.perf_counter()
#         try:
#             load_start = time.perf_counter()
#             date_filter = {f"{self.date_field}__date": {date.isoformat()}}
#             self.logger.debug(f"Loading data for {date} with filter: {date_filter}")
#
#             local_load_params = self.load_params.copy()
#             local_load_params.update(date_filter)
#
#             with self.dataclass(**self.class_params) as local_class_instance:
#                 df = local_class_instance.load(**local_load_params)  # expected to be Dask
#                 load_time = time.perf_counter() - load_start
#
#                 if hasattr(local_class_instance, "total_records"):
#                     total_records = int(local_class_instance.total_records)
#                     self.logger.debug(f"Total records loaded: {total_records}")
#
#                     if total_records == 0:
#                         if self.mmanifest:
#                             self.mmanifest.record(full_path=path)
#                         self.logger.info(f"No data found for {full_path}. Logged to missing manifest.")
#                         return
#
#                     if total_records < 0:
#                         self.logger.warning(f"Negative record count ({total_records}) for {full_path}.")
#                         return
#
#                 save_start = time.perf_counter()
#                 parquet_params = {
#                     "df_result": df,
#                     "parquet_storage_path": path,
#                     "fs": self.fs,
#                     "logger": self.logger,
#                     "debug": self.debug,
#                 }
#                 with ParquetSaver(**parquet_params) as ps:
#                     ps.save_to_parquet(self.parquet_filename, overwrite=True)
#                 save_time = time.perf_counter() - save_start
#
#                 total_time = time.perf_counter() - overall_start
#                 self.benchmarks[date] = {
#                     "load_duration": load_time,
#                     "save_duration": save_time,
#                     "total_duration": total_time,
#                 }
#                 self._log_success(date, total_time, full_path)
#
#         except Exception as e:
#             self._log_failure(date, e)
#             raise
#
#     def _log_success(self, date: datetime.date, duration: float, path: str):
#         self.logger.info(f"Completed {date} in {duration:.1f}s | Saved to {path}")
#         self.processed_dates.append(date)
#
#     def _log_failure(self, date: datetime.date, error: Exception):
#         self.logger.error(f"Failed processing {date}: {error}")
#
#     def show_benchmark_summary(self):
#         if not self.benchmarks:
#             self.logger.info("No benchmarking data to show")
#             return
#         df_bench = pd.DataFrame.from_records([{"date": d, **m} for d, m in self.benchmarks.items()])
#         df_bench = df_bench.set_index("date").sort_index(ascending=not self.update_planner.reverse_order)
#         self.logger.info(f"Benchmark Summary:\n {self.dataclass.__name__}\n" + df_bench.to_string())
#
