from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.reminder import Reminder, ReminderPriority


class ReminderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict) -> Reminder:
        item = Reminder(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, user_id: int, item_id: int) -> Reminder | None:
        return self.db.scalar(select(Reminder).where(Reminder.id == item_id, Reminder.user_id == user_id))

    def list(
        self,
        user_id: int,
        page: int,
        size: int,
        is_completed: bool | None = None,
        priority: ReminderPriority | None = None,
        due_before: datetime | None = None,
    ) -> tuple[list[Reminder], int]:
        stmt = select(Reminder).where(Reminder.user_id == user_id)
        count_stmt = select(func.count(Reminder.id)).where(Reminder.user_id == user_id)

        if is_completed is not None:
            stmt = stmt.where(Reminder.is_completed == is_completed)
            count_stmt = count_stmt.where(Reminder.is_completed == is_completed)
        if priority is not None:
            stmt = stmt.where(Reminder.priority == priority)
            count_stmt = count_stmt.where(Reminder.priority == priority)
        if due_before:
            stmt = stmt.where(Reminder.remind_at <= due_before)
            count_stmt = count_stmt.where(Reminder.remind_at <= due_before)

        stmt = stmt.order_by(Reminder.remind_at.asc()).offset((page - 1) * size).limit(size)
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt).all())
        return items, total

    def update(self, item: Reminder, updates: dict) -> Reminder:
        for field, value in updates.items():
            setattr(item, field, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: Reminder) -> None:
        self.db.delete(item)
        self.db.commit()
