from __future__ import annotations

import datetime as dt
import re
from typing import Callable, Union


class DateUtils:
    """
    Period resolution & normalization for ETL artifacts.

    Canonical periods:
      - 'today'
      - 'current_month'
      - 'ytd'
      - 'itd'
      - 'custom'  (requires 'start_on' and 'end_on')

    Extras:
      - Register named periods at runtime (register_period)
      - Register regex-based periods (register_pattern)
      - Recognize explicit windows: 'YYYY-MM-DD..YYYY-MM-DD'
      - Accept 'last_N_days' and 'last_N_hours' via default patterns

    All dynamic/custom outputs standardize on:
      - date windows: 'start_on' / 'end_on' (YYYY-MM-DD or date-like)
      - time windows: 'start_ts' / 'end_ts' (ISO datetimes)
    """

    # ---- Dynamic registries ----
    _PERIOD_FUNCTIONS: Dict[str, Callable[[], Tuple[dt.date, dt.date]]] = {}
    _PERIOD_PATTERNS: List[Tuple[re.Pattern[str], Callable[[re.Match[str], dt.datetime], Dict[str, Any]]]] = []

    _LAST_N_DAYS_RE = re.compile(r"^last_(\d+)_days$")
    _WINDOW_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})$")

    # ---------------- Core coercion helpers ----------------

    @staticmethod
    def _ensure_date(value: Union[str, dt.date, dt.datetime, pd.Timestamp]) -> dt.date:
        """Ensure the input is converted to a datetime.date."""
        if isinstance(value, dt.date) and not isinstance(value, dt.datetime):
            return value
        if isinstance(value, dt.datetime):
            return value.date()
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime().date()
        if isinstance(value, str):
            # Try pandas parser first (robust), then ISO date
            try:
                return pd.to_datetime(value, errors="raise").date()  # type: ignore[return-value]
            except Exception:
                pass
            try:
                return dt.date.fromisoformat(value)
            except Exception:
                pass
        raise ValueError(f"Unsupported date format: {value!r}")

    # Public alias (used by others)
    ensure_date = _ensure_date

    @staticmethod
    def _ensure_datetime(
        value: Union[str, dt.date, dt.datetime, pd.Timestamp],
        tz: dt.tzinfo = dt.timezone.utc,
    ) -> dt.datetime:
        """Convert input to timezone-aware datetime (defaults to UTC)."""
        if isinstance(value, dt.datetime):
            return value if value.tzinfo else value.replace(tzinfo=tz)
        if isinstance(value, dt.date):
            return dt.datetime(value.year, value.month, value.day, tzinfo=tz)
        if isinstance(value, pd.Timestamp):
            dtt = value.to_pydatetime()
            return dtt if dtt.tzinfo else dtt.replace(tzinfo=tz)
        if isinstance(value, str):
            ts = pd.to_datetime(value, errors="raise", utc=False)
            dtt = ts.to_pydatetime()
            return dtt if getattr(dtt, "tzinfo", None) else dtt.replace(tzinfo=tz)
        raise ValueError(f"Unsupported datetime format: {value!r}")

    # ---------------- Week / Month / Quarter helpers ----------------

    @classmethod
    def calc_week_range(cls, reference_date: Union[str, dt.date, dt.datetime, pd.Timestamp]) -> Tuple[dt.date, dt.date]:
        """Start (Mon) and end (Sun) for the week containing reference_date."""
        ref = cls._ensure_date(reference_date)
        start = ref - dt.timedelta(days=ref.weekday())
        end = start + dt.timedelta(days=6)
        return start, end

    @staticmethod
    def get_year_timerange(year: int) -> Tuple[dt.date, dt.date]:
        return dt.date(year, 1, 1), dt.date(year, 12, 31)

    @classmethod
    def get_first_day_of_the_quarter(cls, reference_date: Union[str, dt.date, dt.datetime, pd.Timestamp]) -> dt.date:
        ref = cls._ensure_date(reference_date)
        quarter = (ref.month - 1) // 3 + 1
        return dt.date(ref.year, 3 * quarter - 2, 1)

    @classmethod
    def get_last_day_of_the_quarter(cls, reference_date: Union[str, dt.date, dt.datetime, pd.Timestamp]) -> dt.date:
        ref = cls._ensure_date(reference_date)
        quarter = (ref.month - 1) // 3 + 1
        first_day_next_q = dt.date(ref.year, 3 * quarter + 1, 1)
        return first_day_next_q - dt.timedelta(days=1)

    @classmethod
    def get_month_range(cls, n: int = 0) -> Tuple[dt.date, dt.date]:
        """
        Range for current month (n=0) or +/- n months relative to today.
        If n == 0, end is today. Otherwise end is calendar month end.
        """
        today = dt.date.today()
        target_month = (today.month - 1 + n) % 12 + 1
        target_year = today.year + (today.month - 1 + n) // 12
        start = dt.date(target_year, target_month, 1)
        if n == 0:
            return start, today
        next_month = (target_month % 12) + 1
        next_year = target_year + (target_month == 12)
        end = dt.date(next_year, next_month, 1) - dt.timedelta(days=1)
        return start, end

    # ---------------- Period registration ----------------

    @classmethod
    def register_period(cls, name: str, func: Callable[[], Tuple[dt.date, dt.date]]) -> None:
        """
        Dynamically register a new named period.
        The callable must return (start_date, end_date) as datetime.date values.
        """
        cls._PERIOD_FUNCTIONS[name] = func

    @classmethod
    def register_pattern(
        cls,
        pattern: str | re.Pattern[str],
        resolver: Callable[[re.Match[str], dt.datetime], Dict[str, Any]],
    ) -> None:
        """
        Register a regex-based dynamic period.

        The resolver receives:
          - match: regex match object
          - now:   timezone-aware datetime (UTC by default)

        It must return a dict with optional keys:
          - 'canonical'           : str (defaults to 'custom')
          - 'start_on'/'end_on'   : ISO date strings (YYYY-MM-DD) OR
          - 'start_ts'/'end_ts'   : ISO datetime strings
          - any additional per-period params
        """
        compiled = re.compile(pattern) if isinstance(pattern, str) else pattern
        cls._PERIOD_PATTERNS.append((compiled, resolver))

    # ---------------- Default named periods ----------------

    @classmethod
    def _get_default_periods(cls) -> Dict[str, Callable[[], Tuple[dt.date, dt.date]]]:
        today = dt.date.today
        return {
            "today": lambda: (today(), today()),
            "yesterday": lambda: (today() - dt.timedelta(days=1), today() - dt.timedelta(days=1)),
            "current_week": lambda: cls.calc_week_range(today()),
            "last_week": lambda: cls.calc_week_range(today() - dt.timedelta(days=7)),
            "current_month": lambda: cls.get_month_range(n=0),
            "last_month": lambda: cls.get_month_range(n=-1),
            "current_year": lambda: cls.get_year_timerange(today().year),
            "last_year": lambda: cls.get_year_timerange(today().year - 1),
            "current_quarter": lambda: (
                cls.get_first_day_of_the_quarter(today()),
                cls.get_last_day_of_the_quarter(today()),
            ),
            "ytd": lambda: (dt.date(today().year, 1, 1), today()),
            "itd": lambda: (dt.date(1900, 1, 1), today()),
        }

    @classmethod
    def period_keys(cls) -> Iterable[str]:
        """List available named periods (defaults + registered)."""
        d = dict(cls._get_default_periods())
        d.update(cls._PERIOD_FUNCTIONS)
        return d.keys()

    # ---------------- Flexible resolver ----------------

    @classmethod
    def resolve_period(
        cls,
        period: Optional[str] = None,
        *,
        now: Optional[dt.datetime] = None,
        tz: dt.tzinfo = dt.timezone.utc,
        **overrides: Any,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Resolve a period into (canonical_key, params).

        Priority:
          1) exact named period (default + registered)
          2) registered regex patterns (e.g., 'last_7_days', 'last_36_hours')
          3) explicit window 'YYYY-MM-DD..YYYY-MM-DD'
          4) fallback: pass the period verbatim with just overrides

        Returns:
          - canonical_key: e.g., 'today', 'current_month', or 'custom'
          - params: dict containing computed keys and merged overrides
        """
        key = (period or "today").strip()
        now = (now or dt.datetime.now(tz)).astimezone(tz)

        # 1) named periods
        period_functions = cls._get_default_periods()
        period_functions.update(cls._PERIOD_FUNCTIONS)
        if key in period_functions:
            start, end = period_functions[key]()
            params = {"start_on": start.isoformat(), "end_on": end.isoformat()}
            params.update(overrides)
            return key, params

        # 2) regex patterns (user-registered)
        for patt, resolver in cls._PERIOD_PATTERNS:
            m = patt.fullmatch(key)
            if m:
                out = resolver(m, now)
                canonical = out.get("canonical", "custom")
                params = {k: v for k, v in out.items() if k != "canonical"}
                params.update(overrides)
                return canonical, params

        # 2b) default 'last_N_days'
        m = cls._LAST_N_DAYS_RE.match(key)
        if m:
            days = int(m.group(1))
            end = now.date()
            start = (now - dt.timedelta(days=days)).date()
            params = {"start_on": start.isoformat(), "end_on": end.isoformat()}
            params.update(overrides)
            return "custom", params

        # 3) explicit date window: YYYY-MM-DD..YYYY-MM-DD
        m2 = cls._WINDOW_RE.fullmatch(key)
        if m2:
            start_on, end_on = m2.group(1), m2.group(2)
            params = {"start_on": start_on, "end_on": end_on}
            params.update(overrides)
            return "custom", params

        # 4) fallback (unknown key)
        return key, dict(overrides)

    # ---------------- Backward-compatible API ----------------

    @classmethod
    def parse_period(cls, **kwargs: Any) -> Tuple[dt.date, dt.date]:
        """
        Return (start_date, end_date) as datetime.date.

        Accepts:
          - period='today' | 'current_month' | 'last_7_days' | 'YYYY-MM-DD..YYYY-MM-DD' | ...
          - optional overrides (e.g., start_on/end_on for 'custom')
        """
        period = kwargs.setdefault("period", "today")

        # Try named periods first
        period_functions = cls._get_default_periods()
        period_functions.update(cls._PERIOD_FUNCTIONS)
        if period in period_functions:
            return period_functions[period]()

        # Otherwise, resolve and coerce
        canonical, params = cls.resolve_period(period, **kwargs)

        if "start_on" in params and "end_on" in params:
            start = cls._ensure_date(params["start_on"])
            end = cls._ensure_date(params["end_on"])
            return start, end

        if "start_ts" in params and "end_ts" in params:
            sdt = cls._ensure_datetime(params["start_ts"]).date()
            edt = cls._ensure_datetime(params["end_ts"]).date()
            return sdt, edt

        raise ValueError(
            f"Could not derive date range from period '{period}' (canonical='{canonical}'). "
            f"Params: {params}"
        )


# ---------------- Default dynamic patterns registration ----------------

def _register_default_patterns() -> None:
    """
    Register common dynamic patterns:
      - last_{n}_hours  (ISO datetimes; useful for freshness windows)
    """

    def last_x_hours(match: re.Match[str], now: dt.datetime) -> Dict[str, Any]:
        hours = int(match.group(1))
        end_ts = now
        start_ts = now - dt.timedelta(hours=hours)
        return {
            "canonical": "custom",
            "start_ts": start_ts.isoformat(),
            "end_ts": end_ts.isoformat(),
            # Sensible default that callers can override:
            "max_age_minutes": max(15, min(hours * 10, 240)),
        }

    DateUtils.register_pattern(r"last_(\d+)_hours", last_x_hours)


# Register defaults at import time
_register_default_patterns()

# from __future__ import annotations
#
# import datetime
# from typing import Union, Tuple, Callable, Dict, Optional
#
# import fsspec
# import numpy as np
# import pandas as pd
# import dask.dataframe as dd
# from .log_utils import Logger
#
#
# class DateUtils:
#     """
#     Utility class for date-related operations.
#
#     The DateUtils class provides a variety of operations to manipulate and retrieve
#     information about dates, such as calculating week ranges, determining start or
#     end dates for specific periods (quarters, months, years), and dynamically
#     registering custom time period functions. It also supports parsing specific
#     periods for date range computations and ensuring the input date is correctly
#     converted to the desired format.
#
#     :ivar logger: Logger instance used for logging messages. Defaults to the logger
#                   for the current class if not provided.
#     :type logger: Logger
#
#     :ivar _PERIOD_FUNCTIONS: Stores dynamically registered period functions that
#                              return start and end dates.
#     :type _PERIOD_FUNCTIONS: Dict[str, Callable[[], Tuple[datetime.date, datetime.date]]]
#     """
#     _PERIOD_FUNCTIONS: Dict[str, Callable[[], Tuple[datetime.date, datetime.date]]] = {}
#
#     def __init__(self, logger=None, debug=False):
#         self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
#         self.debug = debug
#
#     @classmethod
#     def _ensure_date(cls, value: Union[str, datetime.date, datetime.datetime, pd.Timestamp]) -> datetime.date:
#         """
#         Ensure the input is converted to a datetime.date object.
#         """
#         if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
#             return value
#         elif isinstance(value, datetime.datetime):
#             return value.date()
#         elif isinstance(value, pd.Timestamp):
#             return value.to_pydatetime().date()
#         elif isinstance(value, str):
#             for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
#                 try:
#                     return datetime.datetime.strptime(value, fmt).date()
#                 except ValueError:
#                     continue
#         raise ValueError(f"Unsupported date format: {value}")
#
#     # Public alias to access _ensure_date from other classes
#     ensure_date = _ensure_date
#
#     @classmethod
#     def calc_week_range(cls, reference_date: Union[str, datetime.date, datetime.datetime, pd.Timestamp]) -> Tuple[
#         datetime.date, datetime.date]:
#         """
#         Calculate the start and end of the week for a given reference date.
#         """
#         reference_date = cls._ensure_date(reference_date)
#         start = reference_date - datetime.timedelta(days=reference_date.weekday())
#         end = start + datetime.timedelta(days=6)
#         return start, end
#
#     @staticmethod
#     def get_year_timerange(year: int) -> Tuple[datetime.date, datetime.date]:
#         """
#         Get the start and end dates for a given year.
#         """
#         return datetime.date(year, 1, 1), datetime.date(year, 12, 31)
#
#     @classmethod
#     def get_first_day_of_the_quarter(cls, reference_date: Union[
#         str, datetime.date, datetime.datetime, pd.Timestamp]) -> datetime.date:
#         """
#         Get the first day of the quarter for a given date.
#         """
#         reference_date = cls._ensure_date(reference_date)
#         quarter = (reference_date.month - 1) // 3 + 1
#         return datetime.date(reference_date.year, 3 * quarter - 2, 1)
#
#     @classmethod
#     def get_last_day_of_the_quarter(cls, reference_date: Union[
#         str, datetime.date, datetime.datetime, pd.Timestamp]) -> datetime.date:
#         """
#         Get the last day of the quarter for a given date.
#         """
#         reference_date = cls._ensure_date(reference_date)
#         quarter = (reference_date.month - 1) // 3 + 1
#         first_day_of_next_quarter = datetime.date(reference_date.year, 3 * quarter + 1, 1)
#         return first_day_of_next_quarter - datetime.timedelta(days=1)
#
#     @classmethod
#     def get_month_range(cls, n: int = 0) -> Tuple[datetime.date, datetime.date]:
#         """
#         Get the date range for the current month or the month `n` months in the past or future.
#         """
#         today = datetime.date.today()
#         target_month = (today.month - 1 + n) % 12 + 1
#         target_year = today.year + (today.month - 1 + n) // 12
#         start = datetime.date(target_year, target_month, 1)
#         if n == 0:
#             return start, today
#         next_month = (target_month % 12) + 1
#         next_year = target_year + (target_month == 12)
#         end = datetime.date(next_year, next_month, 1) - datetime.timedelta(days=1)
#         return start, end
#
#     @classmethod
#     def register_period(cls, name: str, func: Callable[[], Tuple[datetime.date, datetime.date]]):
#         """
#         Dynamically register a new period function.
#         """
#         cls._PERIOD_FUNCTIONS[name] = func
#
#     @classmethod
#     def parse_period(cls, **kwargs) -> Tuple[datetime.date, datetime.date]:
#         """
#         Parse the period keyword to determine the start and end date for date range operations.
#         """
#         period = kwargs.setdefault('period', 'today')
#         period_functions = cls._get_default_periods()
#         period_functions.update(cls._PERIOD_FUNCTIONS)
#         if period not in period_functions:
#             raise ValueError(f"Unknown period '{period}'. Available periods: {list(period_functions.keys())}")
#         return period_functions[period]()
#
#     @classmethod
#     def _get_default_periods(cls) -> Dict[str, Callable[[], Tuple[datetime.date, datetime.date]]]:
#         """
#         Get default period functions.
#         """
#         today = datetime.date.today
#         return {
#             'today': lambda: (today(), today()),
#             'yesterday': lambda: (today() - datetime.timedelta(days=1), today() - datetime.timedelta(days=1)),
#             'current_week': lambda: cls.calc_week_range(today()),
#             'last_week': lambda: cls.calc_week_range(today() - datetime.timedelta(days=7)),
#             'current_month': lambda: cls.get_month_range(n=0),
#             'last_month': lambda: cls.get_month_range(n=-1),
#             'current_year': lambda: cls.get_year_timerange(today().year),
#             'last_year': lambda: cls.get_year_timerange(today().year - 1),
#             'current_quarter': lambda: (
#                 cls.get_first_day_of_the_quarter(today()), cls.get_last_day_of_the_quarter(today())),
#             'ytd': lambda: (datetime.date(today().year, 1, 1), today()),
#         }
#
#
# class FileAgeChecker:
#     def __init__(self, debug=False, logger=None):
#         self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
#         self.logger.set_level(Logger.DEBUG if debug else Logger.INFO)
#     def is_file_older_than(
#             self,
#             file_path: str,
#             max_age_minutes: int,
#             fs: Optional[fsspec.AbstractFileSystem] = None,
#             ignore_missing: bool = False,
#             verbose: bool = False,
#     ) -> bool:
#         """
#         Check if a file or directory is older than the specified max_age_minutes.
#
#         :param file_path: Path to the file or directory.
#         :param max_age_minutes: Maximum allowed age in minutes.
#         :param fs: Filesystem object. Defaults to local filesystem.
#         :param ignore_missing: Treat missing paths as not old if True.
#         :param verbose: Enable detailed logging.
#         :return: True if older than max_age_minutes, False otherwise.
#         """
#         fs = fs or fsspec.filesystem("file")
#         self.logger.debug(f"Checking age for {file_path}...")
#
#         try:
#             if not fs.exists(file_path):
#                 self.logger.debug(f"Path not found: {file_path}.")
#                 return not ignore_missing
#
#             if fs.isdir(file_path):
#                 self.logger.debug(f"Found directory: {file_path}")
#                 age = self._get_directory_age_minutes(file_path, fs, verbose)
#             elif fs.isfile(file_path):
#                 age = self._get_file_age_minutes(file_path, fs, verbose)
#             else:
#                 self.logger.warning(f"Path {file_path} is neither file nor directory.")
#                 return True
#
#             return age > max_age_minutes
#
#         except Exception as e:
#             self.logger.warning(f"Error checking {file_path}: {str(e)}")
#             return True
#
#     def get_file_or_dir_age_minutes(
#             self,
#             file_path: str,
#             fs: Optional[fsspec.AbstractFileSystem] = None,
#     ) -> float:
#         """
#         Get age of file/directory in minutes. Returns infinity for errors/missing paths.
#
#         :param file_path: Path to check.
#         :param fs: Filesystem object. Defaults to local filesystem.
#         :return: Age in minutes or infinity if unavailable.
#         """
#         fs = fs or fsspec.filesystem("file")
#         try:
#             if not fs.exists(file_path):
#                 self.logger.debug(f"Path not found: {file_path}")
#                 return float("inf")
#
#             if fs.isdir(file_path):
#                 return self._get_directory_age_minutes(file_path, fs, verbose=False)
#             if fs.isfile(file_path):
#                 return self._get_file_age_minutes(file_path, fs, verbose=False)
#
#             self.logger.warning(f"Invalid path type: {file_path}")
#             return float("inf")
#
#         except Exception as e:
#             self.logger.warning(f"Error getting age for {file_path}: {str(e)}")
#             return float("inf")
#
#     def _get_directory_age_minutes(
#             self,
#             dir_path: str,
#             fs: fsspec.AbstractFileSystem,
#             verbose: bool,
#     ) -> float:
#         """Calculate age of oldest file in directory."""
#         try:
#             all_files = fs.ls(dir_path)
#         except Exception as e:
#             self.logger.warning(f"Error listing {dir_path}: {str(e)}")
#             return float("inf")
#
#         if not all_files:
#             self.logger.debug(f"Empty directory: {dir_path}")
#             return float("inf")
#
#         modification_times = []
#         for file in all_files:
#             try:
#                 info = fs.info(file)
#                 mod_time = self._get_modification_time(info, file)
#                 modification_times.append(mod_time)
#             except Exception as e:
#                 self.logger.warning(f"Skipping {file}: {str(e)}")
#
#         if not modification_times:
#             self.logger.warning(f"No valid files in {dir_path}")
#             return float("inf")
#
#         oldest = min(modification_times)
#         age = (datetime.datetime.now(datetime.timezone.utc) - oldest).total_seconds() / 60
#         self.logger.debug(f"Oldest in {dir_path}: {age:.2f} minutes")
#
#         return age
#
#     def _get_file_age_minutes(
#             self,
#             file_path: str,
#             fs: fsspec.AbstractFileSystem,
#             verbose: bool,
#     ) -> float:
#         """Calculate file age in minutes."""
#         try:
#             info = fs.info(file_path)
#             mod_time = self._get_modification_time(info, file_path)
#             age = (datetime.datetime.now(datetime.timezone.utc) - mod_time).total_seconds() / 60
#
#             if verbose:
#                 self.logger.debug(f"{file_path} info: {info}")
#                 self.logger.debug(f"File age: {age:.2f} minutes")
#
#             return age
#
#         except Exception as e:
#             self.logger.warning(f"Error processing {file_path}: {str(e)}")
#             return float("inf")
#
#     def _get_modification_time(self, info: Dict, file_path: str) -> datetime.datetime:
#         """Extract modification time from filesystem info with timezone awareness."""
#         try:
#             if "LastModified" in info:  # S3-like
#                 lm = info["LastModified"]
#                 return lm if isinstance(lm, datetime.datetime) else datetime.datetime.fromisoformat(
#                     lm[:-1]).astimezone()
#
#             if "mtime" in info:  # Local filesystem
#                 return datetime.datetime.fromtimestamp(info["mtime"], tz=datetime.timezone.utc)
#
#             if "modified" in info:  # FTP/SSH
#                 return datetime.datetime.strptime(
#                     info["modified"], "%Y-%m-%d %H:%M:%S"
#                 ).replace(tzinfo=datetime.timezone.utc)
#
#             raise KeyError("No valid modification time key found")
#
#         except (KeyError, ValueError) as e:
#             self.logger.warning(f"Invalid mod time for {file_path}: {str(e)}")
#             raise ValueError(f"Unsupported modification time format for {file_path}") from e
#
#
# # --- Vectorized Helper Functions ---
#
# def _vectorized_busday_count(partition, begin_col, end_col, holidays):
#     """
#     Calculates the number of business days between a start and end date.
#     """
#     # Extract the raw columns
#     start_dates_raw = partition[begin_col]
#     end_dates_raw = partition[end_col]
#
#
#     start_dates = pd.to_datetime(start_dates_raw, errors='coerce')
#     end_dates = pd.to_datetime(end_dates_raw, errors='coerce')
#
#     # Initialize the result Series with NaN, as the output is a number
#     result = pd.Series(np.nan, index=partition.index)
#
#     # Create a mask for rows where both start and end dates are valid
#     valid_mask = pd.notna(start_dates) & pd.notna(end_dates)
#
#     # Perform the vectorized calculation only on the valid subset
#     # Convert to NumPy arrays of date type for the calculation
#     result.loc[valid_mask] = np.busday_count(
#         start_dates[valid_mask].values.astype('datetime64[D]'),
#         end_dates[valid_mask].values.astype('datetime64[D]'),
#         holidays=holidays
#     )
#
#     return result
#
#
# def _vectorized_sla_end_date(partition, start_col, n_days_col, holidays):
#     """
#     Calculates the end date of an SLA, skipping weekends and holidays.
#     """
#     # Extract the relevant columns as pandas Series
#     start_dates_raw = partition[start_col]
#     sla_days = partition[n_days_col]
#
#
#     start_dates = pd.to_datetime(start_dates_raw, errors='coerce')
#
#     # Initialize the result Series with NaT (Not a Time)
#     result = pd.Series(pd.NaT, index=partition.index, dtype='datetime64[ns]')
#
#     # Create a mask for rows that have valid start dates and SLA days
#     valid_mask = pd.notna(start_dates) & pd.notna(sla_days)
#
#     # Perform the vectorized calculation only on the valid subset
#     # Note: np.busday_offset requires a NumPy array, so we use .values
#     result.loc[valid_mask] = np.busday_offset(
#         start_dates[valid_mask].values.astype('datetime64[D]'),  # Convert to numpy array of dates
#         sla_days[valid_mask].astype(int),  # Ensure days are integers
#         roll='forward',
#         holidays=holidays
#     )
#
#     return result
#
#
# # --- Refactored BusinessDays Class ---
#
# class BusinessDays:
#     """
#     Business days calculations with a custom holiday list.
#     Supports scalar and efficient, vectorized Dask DataFrame operations.
#     """
#
#     def __init__(self, holiday_list: dict[str, list[str]], logger) -> None:
#         self.logger = logger
#         self.HOLIDAY_LIST = holiday_list
#
#         # Flatten and store as tuple for determinism
#         bd_holidays = [day for year in self.HOLIDAY_LIST for day in self.HOLIDAY_LIST[year]]
#         self.holidays = tuple(bd_holidays)
#
#     def get_business_days_count(
#             self,
#             begin_date: str | datetime.date | pd.Timestamp,
#             end_date: str | datetime.date | pd.Timestamp,
#     ) -> int:
#         """Scalar method to count business days between two dates."""
#         begin = pd.to_datetime(begin_date)
#         end = pd.to_datetime(end_date)
#         return int(np.busday_count(begin.date(), end.date(), holidays=list(self.holidays)))
#
#     def calc_business_days_from_df(
#             self,
#             df: dd.DataFrame,
#             begin_date_col: str,
#             end_date_col: str,
#             result_col: str = "business_days",
#     ) -> dd.DataFrame:
#         """Calculates business days between two columns in a Dask DataFrame."""
#         missing = {begin_date_col, end_date_col} - set(df.columns)
#         if missing:
#             self.logger.error(f"Missing columns: {missing}")
#             raise ValueError("Required columns are missing from DataFrame")
#
#         return df.assign(
#             **{result_col: df.map_partitions(
#                 _vectorized_busday_count,
#                 begin_col=begin_date_col,
#                 end_col=end_date_col,
#                 holidays=list(self.holidays),
#                 meta=(result_col, 'f8')  # f8 is float64
#             )}
#         )
#
#     def add_business_days(
#             self,
#             start_date: str | datetime.date | pd.Timestamp,
#             n_days: int,
#     ) -> np.datetime64:
#         """Scalar method to add N business days to a start date."""
#         start = pd.to_datetime(start_date)
#         return np.busday_offset(
#             start.date(),
#             n_days,
#             roll='forward',
#             holidays=list(self.holidays),
#         )
#
#     def calc_sla_end_date(
#             self,
#             df: dd.DataFrame,
#             start_date_col: str,
#             n_days_col: str,
#             result_col: str = "sla_end_date",
#     ) -> dd.DataFrame:
#         """Calculates an SLA end date column for a Dask DataFrame."""
#         missing = {start_date_col, n_days_col} - set(df.columns)
#         if missing:
#             self.logger.error(f"Missing columns: {missing}")
#             raise ValueError("Required columns are missing from DataFrame")
#
#         return df.assign(
#             **{result_col: df.map_partitions(
#                 _vectorized_sla_end_date,
#                 start_col=start_date_col,
#                 n_days_col=n_days_col,
#                 holidays=list(self.holidays),
#                 meta=(result_col, 'datetime64[ns]')
#             )}
#         )
#
# # Class enhancements
# # DateUtils.register_period('next_week', lambda: (datetime.date.today() + datetime.timedelta(days=7),
# #                                                 datetime.date.today() + datetime.timedelta(days=13)))
# # start, end = DateUtils.parse_period(period='next_week')
# # print(f"Next Week: {start} to {end}")
