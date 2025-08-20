import datetime as dt
from typing import Any, Dict, Iterable, Optional
from sibi_dst.utils import Logger
import numpy as np
import pandas as pd
import dask.dataframe as dd


# ---------------- Vectorized helpers (used by Dask map_partitions) ----------------

def _to_np_days(series: pd.Series) -> np.ndarray:
    """Coerce to numpy datetime64[D] with NaT-safe conversion."""
    # Use pandas for robust parsing, then cast to date-days
    s = pd.to_datetime(series, errors="coerce")
    # Convert to numpy datetime64[D] (day precision)
    return s.values.astype("datetime64[D]")


def _vectorized_busday_count(
        part: pd.DataFrame,
        begin_col: str,
        end_col: str,
        holidays: Iterable[str],
        weekmask: Optional[str],
        inclusive: bool,
) -> pd.Series:
    start = _to_np_days(part[begin_col])  # numpy datetime64[D]
    end = _to_np_days(part[end_col])  # numpy datetime64[D]

    kwargs: Dict[str, Any] = {}
    if holidays:
        kwargs["holidays"] = np.array(list(holidays), dtype="datetime64[D]")
    if weekmask:
        kwargs["weekmask"] = weekmask

    end_adj = end
    if inclusive:
        with np.errstate(invalid="ignore"):
            end_adj = end + np.timedelta64(1, "D")

    valid = (~pd.isna(start)) & (~pd.isna(end))  # numpy bool mask
    result = np.full(part.shape[0], np.nan, dtype="float64")
    if valid.any():
        counts = np.busday_count(
            start[valid].astype("datetime64[D]"),
            end_adj[valid].astype("datetime64[D]"),
            **kwargs,
        ).astype("float64")
        result[valid] = counts

    return pd.Series(result, index=part.index)


def _vectorized_busday_offset(
        part: pd.DataFrame,
        start_col: str,
        n_days_col: str,
        holidays: Iterable[str],
        weekmask: Optional[str],
        roll: str,
) -> pd.Series:
    start = _to_np_days(part[start_col])  # numpy datetime64[D]
    n_days = pd.to_numeric(part[n_days_col], errors="coerce").to_numpy()  # numpy float -> cast later

    kwargs: Dict[str, Any] = {"roll": roll}
    if holidays:
        kwargs["holidays"] = np.array(list(holidays), dtype="datetime64[D]")
    if weekmask:
        kwargs["weekmask"] = weekmask

    valid = (~pd.isna(start)) & (~pd.isna(n_days))  # numpy bool mask
    out = np.full(part.shape[0], np.datetime64("NaT", "ns"), dtype="datetime64[ns]")
    if valid.any():
        offs = np.busday_offset(
            start[valid].astype("datetime64[D]"),
            n_days[valid].astype("int64"),
            **kwargs,
        ).astype("datetime64[ns]")
        out[valid] = offs

    return pd.Series(out, index=part.index)


# ---------------- BusinessDays ----------------

class BusinessDays:
    """
    Business day calculations with custom holidays and optional weekmask.

    Features
    - Scalar helpers:
        - get_business_days_count(begin, end, inclusive=False) -> int
        - add_business_days(start_date, n_days, roll='forward') -> np.datetime64
    - Dask DataFrame helpers (vectorized via map_partitions):
        - calc_business_days_from_df(df, begin_col, end_col, result_col='business_days', inclusive=False)
        - calc_sla_end_date(df, start_date_col, n_days_col, result_col='sla_end_date', roll='forward')

    Parameters
    ----------
    holiday_list : dict[str, list[str]] | Iterable[str]
        Either a mapping of year -> [YYYY-MM-DD, ...] or a flat iterable of YYYY-MM-DD strings.
    logger : Any
        Logger with .debug/.info/.warning/.error.
    weekmask : str | None
        A numpy business day weekmask like '1111100' (Mon–Fri). None means default Mon–Fri.
        Examples:
            '1111100' -> Mon-Fri
            '1111110' -> Mon-Sat
    """

    def __init__(
            self,
            holiday_list: Dict[str, list[str]] | Iterable[str],
            debug: bool = False,
            logger: Optional[Logger] = None,
            weekmask: Optional[str] = None,
    ) -> None:
        self.debug = debug
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.weekmask = weekmask

        # Normalize holidays to a flat, sorted tuple of 'YYYY-MM-DD'
        if isinstance(holiday_list, dict):
            flat = [d for _, days in sorted(holiday_list.items()) for d in days]
        else:
            flat = list(holiday_list)
        # Deduplicate while preserving order
        seen = set()
        flat_unique = []
        for d in flat:
            if d not in seen:
                seen.add(d)
                flat_unique.append(d)
        self.holidays: tuple[str, ...] = tuple(flat_unique)

    # -------- Scalar API --------

    def get_business_days_count(
            self,
            begin_date: str | dt.date | pd.Timestamp,
            end_date: str | dt.date | pd.Timestamp,
            *,
            inclusive: bool = False,
    ) -> int:
        """Business days between two dates. If inclusive=True, include the end date."""
        b = pd.to_datetime(begin_date).date()
        e = pd.to_datetime(end_date).date()

        kwargs: Dict[str, Any] = {}
        if self.holidays:
            kwargs["holidays"] = np.array(self.holidays, dtype="datetime64[D]")
        if self.weekmask:
            kwargs["weekmask"] = self.weekmask

        if inclusive:
            e_np = np.datetime64(e) + np.timedelta64(1, "D")
        else:
            e_np = np.datetime64(e)

        val = int(np.busday_count(np.datetime64(b), e_np, **kwargs))
        return val

    def add_business_days(
            self,
            start_date: str | dt.date | pd.Timestamp,
            n_days: int,
            *,
            roll: str = "forward",
    ) -> np.datetime64:
        """
        Add (or subtract) business days to a date. Returns numpy datetime64[D].
        roll: {'forward','backward','following','preceding','modifiedfollowing',
               'modifiedpreceding','nat'}
        """
        s = pd.to_datetime(start_date).date()
        kwargs: Dict[str, Any] = {"roll": roll}
        if self.holidays:
            kwargs["holidays"] = np.array(self.holidays, dtype="datetime64[D]")
        if self.weekmask:
            kwargs["weekmask"] = self.weekmask

        return np.busday_offset(np.datetime64(s), int(n_days), **kwargs)

    # -------- Dask API --------

    def calc_business_days_from_df(
            self,
            df: dd.DataFrame,
            begin_date_col: str,
            end_date_col: str,
            result_col: str = "business_days",
            *,
            inclusive: bool = False,
    ) -> dd.DataFrame:
        """
        Vectorized business-day difference between two date columns.
        Produces float64 (NaN where either side is missing).
        """
        missing = {begin_date_col, end_date_col} - set(df.columns)
        if missing:
            self.logger.error(f"Missing columns: {missing}")
            raise ValueError("Required columns are missing from DataFrame")

        return df.assign(
            **{
                result_col: df.map_partitions(
                    _vectorized_busday_count,
                    begin_col=begin_date_col,
                    end_col=end_date_col,
                    holidays=self.holidays,
                    weekmask=self.weekmask,
                    inclusive=inclusive,
                    meta=(result_col, "f8"),
                )
            }
        )

    def calc_sla_end_date(
            self,
            df: dd.DataFrame,
            start_date_col: str,
            n_days_col: str,
            result_col: str = "sla_end_date",
            *,
            roll: str = "forward",
    ) -> dd.DataFrame:
        """
        Vectorized business-day offset for SLA end date.
        Produces datetime64[ns] with NaT where invalid.
        """
        missing = {start_date_col, n_days_col} - set(df.columns)
        if missing:
            self.logger.error(f"Missing columns: {missing}")
            raise ValueError("Required columns are missing from DataFrame")

        return df.assign(
            **{
                result_col: df.map_partitions(
                    _vectorized_busday_offset,
                    start_col=start_date_col,
                    n_days_col=n_days_col,
                    holidays=self.holidays,
                    weekmask=self.weekmask,
                    roll=roll,
                    meta=(result_col, "datetime64[ns]"),
                )
            }
        )
