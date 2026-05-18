from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Budget, Category, Habit, HabitEntry, JournalEntry, PaymentMethod, Resolution, Transaction
from app.schemas.csv_import import BudgetCSVRow, HabitCSVRow, JournalCSVRow, ResolutionCSVRow, TransactionCSVRow


DEFAULT_RAW_DATA_DIR = Path(__file__).resolve().parents[4] / "data" / "raw"


@dataclass(slots=True)
class CSVImportSummary:
    transactions: int = 0
    habits: int = 0
    habit_entries: int = 0
    resolutions: int = 0
    budgets: int = 0
    journal_entries: int = 0
    categories: int = 0
    payment_methods: int = 0


def _read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _clear_existing_data(db: Session) -> None:
    db.execute(delete(HabitEntry))
    db.execute(delete(Transaction))
    db.execute(delete(Budget))
    db.execute(delete(JournalEntry))
    db.execute(delete(Resolution))
    db.execute(delete(Habit))
    db.execute(delete(PaymentMethod))
    db.execute(delete(Category))


def import_csv_data(
    db: Session,
    raw_data_dir: Path = DEFAULT_RAW_DATA_DIR,
    *,
    replace_existing: bool = True,
) -> CSVImportSummary:
    if replace_existing:
        _clear_existing_data(db)

    summary = CSVImportSummary()

    category_cache = {row.name: row for row in db.scalars(select(Category)).all()}
    payment_method_cache = {row.name: row for row in db.scalars(select(PaymentMethod)).all()}
    habit_cache = {row.name: row for row in db.scalars(select(Habit)).all()}

    transaction_rows = [TransactionCSVRow.model_validate(row) for row in _read_rows(raw_data_dir / "tracker_transactions.csv")]
    for row in transaction_rows:
        category = category_cache.get(row.category)
        if category is None:
            category = Category(name=row.category)
            db.add(category)
            db.flush()
            category_cache[category.name] = category
            summary.categories += 1

        payment_method = None
        if row.payment_method:
            payment_method = payment_method_cache.get(row.payment_method)
            if payment_method is None:
                payment_method = PaymentMethod(name=row.payment_method)
                db.add(payment_method)
                db.flush()
                payment_method_cache[payment_method.name] = payment_method
                summary.payment_methods += 1

        db.add(
            Transaction(
                transaction_date=row.date,
                amount=row.amount,
                transaction_type=row.transaction_type,
                notes=row.notes,
                category_id=category.id,
                payment_method_id=payment_method.id if payment_method else None,
            )
        )
        summary.transactions += 1

    budget_rows = [BudgetCSVRow.model_validate(row) for row in _read_rows(raw_data_dir / "tracker_budget.csv")]
    for row in budget_rows:
        category = category_cache.get(row.category)
        if category is None:
            category = Category(name=row.category)
            db.add(category)
            db.flush()
            category_cache[category.name] = category
            summary.categories += 1

        db.add(Budget(category_id=category.id, monthly_budget=row.monthly_budget))
        summary.budgets += 1

    habit_rows = [HabitCSVRow.model_validate(row) for row in _read_rows(raw_data_dir / "tracker_habits.csv")]
    for row in habit_rows:
        habit = habit_cache.get(row.habit)
        if habit is None:
            habit = Habit(name=row.habit)
            db.add(habit)
            db.flush()
            habit_cache[habit.name] = habit
            summary.habits += 1

        db.add(HabitEntry(habit_id=habit.id, entry_date=row.date, done=row.done == "yes", notes=row.notes))
        summary.habit_entries += 1

    resolution_rows = [ResolutionCSVRow.model_validate(row) for row in _read_rows(raw_data_dir / "tracker_resolutions.csv")]
    for row in resolution_rows:
        db.add(
            Resolution(
                title=row.resolution,
                start_date=row.start_date,
                target_date=row.target_date,
                metric_target=row.metric_target,
                current_value=row.current_value,
                status=row.status,
                notes=row.notes,
            )
        )
        summary.resolutions += 1

    journal_rows = [JournalCSVRow.model_validate(row) for row in _read_rows(raw_data_dir / "tracker_journal.csv")]
    for row in journal_rows:
        db.add(JournalEntry(entry_date=row.date, title=row.title, entry=row.entry, mood=row.mood))
        summary.journal_entries += 1

    db.commit()
    return summary
