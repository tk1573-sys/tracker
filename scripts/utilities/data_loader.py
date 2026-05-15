"""Data loading and validation helpers for all tracker CSV files."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from scripts.utilities.logger import get_logger

logger = get_logger(__name__)

_BASE = Path(__file__).resolve().parents[2]
_RAW = _BASE / "data" / "raw"


def _parse(filename: str, parse_dates: Optional[list] = None) -> pd.DataFrame:
    path = _RAW / filename
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    df = pd.read_csv(path, parse_dates=parse_dates or [])
    logger.debug("Loaded %s (%d rows)", filename, len(df))
    return df


def load_all() -> Dict[str, pd.DataFrame]:
    """Load all tracker CSV files and return a dict of DataFrames.

    Returns:
        Dictionary with keys: transactions, habits, resolutions,
        budget, journal, health, food.
    """
    return {
        "transactions": _parse("tracker_transactions.csv", ["Date"]),
        "habits": _parse("tracker_habits.csv", ["Date"]),
        "resolutions": _parse("tracker_resolutions.csv", ["StartDate", "TargetDate"]),
        "budget": _parse("tracker_budget.csv"),
        "journal": _parse("tracker_journal.csv", ["Date"]),
        "health": _parse("tracker_health.csv", ["Date"]),
        "food": _parse("tracker_food.csv", ["Date"]),
    }
