#!/usr/bin/env python3
"""Personal Analytics Platform — CLI entry point.

Usage:
    python main.py                   # Generate Excel workbook
    python main.py --backup          # Backup raw CSVs before generating
    python main.py --insights        # Print AI-ready insights to stdout
    python main.py --help            # Show help
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(_BASE))

from scripts.utilities.config_loader import get_app_config
from scripts.utilities.data_loader import load_all
from scripts.utilities.logger import get_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Personal Analytics Platform — Excel Dashboard Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--backup", action="store_true", help="Backup raw CSVs before generating")
    parser.add_argument("--insights", action="store_true", help="Print analytics insights to stdout")
    parser.add_argument("--output", type=str, default=None, help="Override output .xlsx path")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = get_app_config()
    log_file = cfg.get("app", {}).get("log_file", "logs/app.log")
    logger = get_logger("main", log_file=log_file, level=args.log_level)

    logger.info("Personal Analytics Platform v%s starting", cfg.get("app", {}).get("version", "2.0.0"))

    if args.backup:
        from scripts.automation.backup import backup_raw_data
        backup_raw_data()

    logger.info("Loading data from data/raw/...")
    data = load_all()
    for name, df in data.items():
        logger.info("  %-20s %d rows", name, len(df))

    if args.insights:
        from scripts.ai.insights import InsightsEngine
        engine = InsightsEngine(data)
        print("\n=== FINANCE INSIGHTS ===")
        print(engine.spending_summary())
        print("\n=== HABIT INSIGHTS ===")
        print(engine.habit_summary())
        print("\n=== JOURNAL INSIGHTS ===")
        print(engine.journal_sentiment())

    from pathlib import Path as _Path
    from scripts.generators.excel_workbook import TrackerWorkbookGenerator
    output_path = _Path(args.output) if args.output else None
    gen = TrackerWorkbookGenerator(data, output_path=output_path)
    out = gen.generate()
    logger.info("Done! Workbook: %s", out)
    print(f"\n✅  Workbook generated: {out}")


if __name__ == "__main__":
    main()
