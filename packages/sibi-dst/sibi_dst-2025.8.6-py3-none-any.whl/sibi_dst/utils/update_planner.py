import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Union, Tuple, Set, Iterator, ClassVar

import pandas as pd

from sibi_dst.utils import ManagedResource
from . import FileAgeChecker


class UpdatePlanner(ManagedResource):
    """
    Scans date-partitioned storage and builds an 'update plan' for dates that need processing.
    Produces a Pandas DataFrame plan; it does *not* load data frames, so Dask-vs-Pandas
    concerns do not apply here.
    """

    DEFAULT_PRIORITY_MAP: ClassVar[Dict[str, int]] = {
        "file_is_recent": 0,
        "missing_ignored": 0,
        "overwrite_forced": 1,
        "create_missing": 2,
        "missing_in_history": 3,
        "stale_in_history": 4,
    }

    DEFAULT_MAX_AGE_MINUTES: int = 1440
    DEFAULT_HISTORY_DAYS_THRESHOLD: int = 30

    def __init__(
        self,
        parquet_storage_path: str,
        parquet_filename: str,
        description: str = "Update Planner",
        reference_date: Union[str, dt.date, None] = None,
        history_days_threshold: int = DEFAULT_HISTORY_DAYS_THRESHOLD,
        max_age_minutes: int = DEFAULT_MAX_AGE_MINUTES,
        overwrite: bool = False,
        ignore_missing: bool = False,
        custom_priority_map: Optional[Dict[str, int]] = None,
        reverse_order: bool = False,
        show_progress: bool = False,
        skipped: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Public-ish attributes
        self.description = description
        self.data_path = self._ensure_trailing_slash(parquet_storage_path)
        self.filename = parquet_filename
        self.reverse_order = reverse_order
        self.show_progress = show_progress
        self.overwrite = overwrite
        self.ignore_missing = ignore_missing
        self.history_days_threshold = history_days_threshold
        self.max_age_minutes = max_age_minutes
        self.priority_map = custom_priority_map or self.DEFAULT_PRIORITY_MAP
        self.skipped = set(skipped or [])

        # Execution knobs from kwargs (fed by upstream config)
        self.max_threads: int = int(kwargs.get("max_threads", 3))
        self.timeout: float = float(kwargs.get("timeout", 30.0))

        # Date window
        self.start_date = kwargs.get("parquet_start_date")
        self.end_date = kwargs.get("parquet_end_date")

        # Reference "today"
        if reference_date is None:
            self.reference_date = dt.date.today()
        else:
            self.reference_date = pd.to_datetime(reference_date).date()

        # Helpers & state
        self.age_checker = FileAgeChecker(debug=self.debug, logger=self.logger)
        self.plan: pd.DataFrame = pd.DataFrame()
        self.df_req: pd.DataFrame = pd.DataFrame()

        # internal run flag to print once per run if caller reuses instance
        self._printed_this_run: bool = False

    # --------------------- public helpers ---------------------
    def has_plan(self) -> bool:
        """Safe truthiness for plan existence."""
        return isinstance(self.plan, pd.DataFrame) and not self.plan.empty

    def required_count(self) -> int:
        return 0 if not isinstance(self.df_req, pd.DataFrame) else len(self.df_req)

    # --------------------- core API ---------------------
    def generate_plan(
        self,
        start: Union[str, dt.date, None] = None,
        end: Union[str, dt.date, None] = None,
        freq: str = "D",
    ) -> pd.DataFrame:
        """
        Build a plan for [start, end]. Returns rows that require update (df_req).
        """
        start = start or self.start_date
        end = end or self.end_date
        sd = pd.to_datetime(start).date()
        ed = pd.to_datetime(end).date()
        if sd > ed:
            raise ValueError(f"Start date ({sd}) must be on or before end date ({ed}).")

        self.logger.info(f"Generating update plan for {self.description} from {sd} to {ed}")
        self._generate_plan(sd, ed, freq=freq)
        self.logger.info(
            f"Plan built for {self.description}: {len(self.plan)} dates evaluated, "
            f"{len(self.df_req)} require update"
        )
        return self.df_req

    def show_update_plan(self) -> None:
        """Pretty-print the current plan once per run."""
        if not self.has_plan():
            self.logger.info("No update plan to show.")
            return
        if self._printed_this_run:
            return

        try:
            from rich.console import Console
            from rich.table import Table
        except Exception:
            # Fallback: plain text
            self.logger.info(f"Update Plan (plain list):\n{self.plan.to_string(index=False)}")
            self._printed_this_run = True
            return

        table = Table(
            title=f"Update Plan for {self.data_path}",
            show_header=True,
            header_style="bold magenta",
        )
        for column in self.plan.columns:
            table.add_column(column, justify="left")

        for _, row in self.plan.iterrows():
            table.add_row(*(str(row[col]) for col in self.plan.columns))

        console = Console()
        with console.capture() as capture:
            console.print(table)
        self.logger.info(f"Full Update Plan:\n{capture.get().strip()}", extra={"date_of_update": self.reference_date.strftime('%Y-%m-%d'), "dataclass": self.description,"action_module_name": "update_plan"})
        self._printed_this_run = True

    def get_tasks_by_priority(self) -> Iterator[Tuple[int, List[dt.date]]]:
        """
        Yield (priority, [dates...]) batches, smallest priority first.
        """
        if not self.has_plan():
            return
        req = self.plan[self.plan["update_required"]]
        if req.empty:
            return
        for priority in sorted(req["update_priority"].unique()):
            dates_df = req[req["update_priority"] == priority]
            # sort within group
            dates_df = dates_df.sort_values(by="date", ascending=not self.reverse_order)
            dates = dates_df["date"].tolist()
            if dates:
                yield int(priority), dates

    # --------------------- internals ---------------------
    @staticmethod
    def _ensure_trailing_slash(path: str) -> str:
        return path.rstrip("/") + "/"

    def _generate_plan(self, start: dt.date, end: dt.date, freq: str = "D") -> None:
        """
        Populate self.plan with all dates and self.df_req with the subset to update.
        """
        dates = pd.date_range(start=start, end=end, freq=freq).date.tolist()
        history_start = self.reference_date - dt.timedelta(days=self.history_days_threshold)
        rows: List[Dict] = []

        # bound threads
        max_workers = max(1, int(self.max_threads))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._get_file_status, d): d for d in dates}
            iterator = as_completed(futures)
            if self.show_progress:
                try:
                    from tqdm import tqdm
                    iterator = tqdm(
                        iterator, total=len(futures),
                        desc=f"Scanning dates for {self.description}",
                        unit="date", leave=False
                    )
                except Exception:
                    pass  # no tqdm → proceed without progress bar

            for future in iterator:
                d = futures[future]
                try:
                    exists, age = future.result(timeout=self.timeout)
                    rows.append(self._make_row(d, history_start, exists, age))
                except Exception as exc:
                    self.logger.error(f"Error processing date {d}: {exc}")
                    rows.append(self._make_row(d, history_start, False, None))

        df = pd.DataFrame(rows)
        # consistent types
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["update_priority"] = df["update_priority"].astype(int)

        df = df.sort_values(
            by=["update_priority", "date"],
            ascending=[True, not self.reverse_order],
            kind="mergesort",  # stable
        ).reset_index(drop=True)

        self.plan = df
        self.df_req = df[df["update_required"]].copy()
        self._printed_this_run = False

    def _get_file_status(self, date: dt.date) -> Tuple[bool, Optional[float]]:
        """
        Check file existence and age for the given date.
        """
        just_path = f"{self.data_path}{date.year}/{date.month:02d}/{date.day:02d}/"
        if just_path in self.skipped:
            self.logger.debug(f"Skipping {date}: path in skipped list.")
            return False, None

        path = f"{just_path}{self.filename}"
        try:
            exists = self.fs.exists(path)
            age = self.age_checker.get_file_or_dir_age_minutes(path, self.fs) if exists else None
            return bool(exists), age
        except Exception as e:
            self.logger.warning(f"exists/age check failed for {path}: {e}")
            return False, None

    def _make_row(
        self,
        date: dt.date,
        history_start: dt.date,
        file_exists: bool,
        file_age: Optional[float],
    ) -> Dict:
        """
        Build a single plan row based on flags and thresholds.
        """
        within_history = history_start <= date <= self.reference_date
        update_required = False

        # 1) Overwrite forces update
        if self.overwrite:
            category = "overwrite_forced"
            update_required = True
        # 2) Inside history window
        elif within_history:
            if not file_exists:
                category = "missing_in_history"
                update_required = True
            elif file_age is not None and file_age > self.max_age_minutes:
                category = "stale_in_history"
                update_required = True
            else:
                category = "file_is_recent"
        # 3) Outside history, missing file (and not ignoring)
        elif not file_exists and not self.ignore_missing:
            category = "create_missing"
            update_required = True
        # 4) Everything else
        else:
            category = "missing_ignored" if not file_exists else "file_is_recent"

        return {
            "date": date,
            "file_exists": bool(file_exists),
            "file_age_minutes": file_age,
            "update_category": category,
            "update_priority": self.priority_map.get(category, 99),
            "update_required": bool(update_required),
            "description": self.description,
        }

    def exclude_dates(self, dates: Set[dt.date]) -> None:
        """
        Exclude specific dates from the update plan.
        """
        if not isinstance(dates, set):
            raise ValueError("dates must be a set[date].")
        if not self.has_plan():
            self.logger.info("No update plan to modify. Call generate_plan() first.")
            return

        before = len(self.plan)
        self.plan = self.plan[~self.plan["date"].isin(dates)]
        self.df_req = self.plan[self.plan["update_required"]].copy()
        self.logger.info(
            f"Excluded {len(dates)} dates from the update plan (from {before} to {len(self.plan)} rows)."
        )