"""Auto-backup utility for raw CSV data files."""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from scripts.utilities.logger import get_logger

logger = get_logger(__name__)
_BASE = Path(__file__).resolve().parents[2]


def backup_raw_data(dest_dir: Optional[Path] = None) -> Path:
    """Copy all raw CSVs to a timestamped backup folder.

    Args:
        dest_dir: Destination parent directory. Defaults to data/exports/backups/.

    Returns:
        Path to the created backup directory.
    """
    if dest_dir is None:
        dest_dir = _BASE / "data" / "exports" / "backups"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = dest_dir / f"backup_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)

    raw_dir = _BASE / "data" / "raw"
    count = 0
    for csv_file in raw_dir.glob("*.csv"):
        shutil.copy2(csv_file, backup_path / csv_file.name)
        count += 1

    logger.info("Backed up %d CSV files to %s", count, backup_path)
    return backup_path
