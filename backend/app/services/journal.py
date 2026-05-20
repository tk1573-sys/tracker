from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry
from app.schemas.journal import JournalEntryCreate
from app.services.common import commit_or_rollback, resolve_mode_id, scoped_by_user_mode


def create_journal_entry(db: Session, user_id: int, payload: JournalEntryCreate, mode_id: int) -> JournalEntry:
    resolved_mode_id = resolve_mode_id(db, user_id=user_id, requested_mode_id=payload.mode_id, fallback_mode_id=mode_id)
    entry = JournalEntry(
        user_id=user_id,
        mode_id=resolved_mode_id,
        entry_date=payload.entry_date or date.today(),
        mood_score=payload.mood_score,
        content=payload.content,
        tags=payload.tags,
    )
    db.add(entry)
    commit_or_rollback(db)
    db.refresh(entry)
    return entry


def list_journal_entries(db: Session, user_id: int, mode_id: int | None, include_all_modes: bool) -> list[JournalEntry]:
    stmt = select(JournalEntry).order_by(JournalEntry.entry_date.desc(), JournalEntry.id.desc())
    stmt = scoped_by_user_mode(stmt, JournalEntry, user_id=user_id, mode_id=mode_id, include_all_modes=include_all_modes)
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
