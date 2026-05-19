from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry
from app.schemas.journal import JournalEntryCreate
from app.services.common import apply_mode_scope


def create_journal_entry(db: Session, user_id: int, payload: JournalEntryCreate, mode_id: int) -> JournalEntry:
    entry = JournalEntry(
        user_id=user_id,
        mode_id=payload.mode_id or mode_id,
        entry_date=payload.entry_date or date.today(),
        mood_score=payload.mood_score,
        content=payload.content,
        tags=payload.tags,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_journal_entries(db: Session, user_id: int, mode_id: int | None, include_all_modes: bool) -> list[JournalEntry]:
    stmt = select(JournalEntry).where(JournalEntry.user_id == user_id).order_by(JournalEntry.entry_date.desc(), JournalEntry.id.desc())
    stmt = apply_mode_scope(stmt, mode_column=JournalEntry.mode_id, mode_id=mode_id, include_all_modes=include_all_modes)
    return db.scalars(stmt).all()


def get_recent_mood_average(db: Session, user_id: int, mode_id: int) -> float | None:
    since = (datetime.now(UTC) - timedelta(days=7)).date()
    entries = db.scalars(
        select(JournalEntry).where(
            JournalEntry.user_id == user_id,
            JournalEntry.mode_id == mode_id,
            JournalEntry.entry_date >= since,
            JournalEntry.mood_score.is_not(None),
        )
    ).all()
    if not entries:
        return None
    return round(sum(entry.mood_score for entry in entries if entry.mood_score is not None) / len(entries), 2)
