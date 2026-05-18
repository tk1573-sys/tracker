from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry


class JournalEntryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict) -> JournalEntry:
        item = JournalEntry(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, user_id: int, item_id: int) -> JournalEntry | None:
        return self.db.scalar(select(JournalEntry).where(JournalEntry.id == item_id, JournalEntry.user_id == user_id))

    def list(
        self, user_id: int, page: int, size: int, entry_date: date | None = None, mood: int | None = None
    ) -> tuple[list[JournalEntry], int]:
        stmt = select(JournalEntry).where(JournalEntry.user_id == user_id)
        count_stmt = select(func.count(JournalEntry.id)).where(JournalEntry.user_id == user_id)

        if entry_date:
            stmt = stmt.where(JournalEntry.entry_date == entry_date)
            count_stmt = count_stmt.where(JournalEntry.entry_date == entry_date)
        if mood is not None:
            stmt = stmt.where(JournalEntry.mood == mood)
            count_stmt = count_stmt.where(JournalEntry.mood == mood)

        stmt = stmt.order_by(JournalEntry.entry_date.desc()).offset((page - 1) * size).limit(size)
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt).all())
        return items, total

    def update(self, item: JournalEntry, updates: dict) -> JournalEntry:
        for field, value in updates.items():
            setattr(item, field, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: JournalEntry) -> None:
        self.db.delete(item)
        self.db.commit()
