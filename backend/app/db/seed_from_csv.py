from pathlib import Path

from app.db.importers import import_csv_data
from app.db.session import SessionLocal


def seed_from_csv(raw_data_dir: Path | None = None) -> None:
    with SessionLocal() as db:
        summary = import_csv_data(db, raw_data_dir=raw_data_dir) if raw_data_dir else import_csv_data(db)
        print(summary)


if __name__ == "__main__":
    seed_from_csv()
