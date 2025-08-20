# sibi_dst/periods.py
from __future__ import annotations
import datetime as dt
from typing import Dict, Tuple

# Map all user-facing labels to canonical keys your orchestrators expect.
CANON: Dict[str, str] = {
    "ytd": "ytd",
    "itd": "itd",
    "current_month": "current_month",
    "today": "today",
    "custom": "custom",  # generic custom range
    # labels that imply a date RANGE
    "last_3_days": "custom",
    "last_7_days": "custom",
    "last_14_days": "custom",
}

def normalize_period(user_period: str) -> str:
    """
    Normalize a user-facing period label to your canonical key.
    Raises ValueError with allowed labels if unsupported.
    """
    try:
        return CANON[user_period]
    except KeyError:
        allowed = ", ".join(sorted(CANON))
        raise ValueError(f"Unsupported period '{user_period}'. Allowed: {allowed}")

def compute_range_days(label: str, *, today: dt.date | None = None) -> Tuple[dt.date, dt.date]:
    """
    Convert 'last_N_days' label to an inclusive (start_date, end_date).
    Example: last_3_days with today=2025-08-11 -> (2025-08-08, 2025-08-11)
    """
    today = today or dt.date.today()
    try:
        # label format: 'last_<N>_days'
        days = int(label.split("_")[1])
    except Exception as e:
        raise ValueError(f"Invalid range label '{label}'. Expected 'last_<N>_days'.") from e
    start = today - dt.timedelta(days=days)
    return (start, today)