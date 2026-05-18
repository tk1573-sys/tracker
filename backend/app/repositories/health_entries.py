from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.health_entry import HealthEntry


class HealthEntryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict) -> HealthEntry:
        item = HealthEntry(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, user_id: int, item_id: int) -> HealthEntry | None:
        return self.db.scalar(select(HealthEntry).where(HealthEntry.id == item_id, HealthEntry.user_id == user_id))

    def list(
        self,
        user_id: int,
        page: int,
        size: int,
        metric_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[list[HealthEntry], int]:
        stmt = select(HealthEntry).where(HealthEntry.user_id == user_id)
        count_stmt = select(func.count(HealthEntry.id)).where(HealthEntry.user_id == user_id)

        if metric_type:
            stmt = stmt.where(HealthEntry.metric_type == metric_type)
            count_stmt = count_stmt.where(HealthEntry.metric_type == metric_type)
        if start_date:
            stmt = stmt.where(HealthEntry.recorded_at >= start_date)
            count_stmt = count_stmt.where(HealthEntry.recorded_at >= start_date)
        if end_date:
            stmt = stmt.where(HealthEntry.recorded_at <= end_date)
            count_stmt = count_stmt.where(HealthEntry.recorded_at <= end_date)

        stmt = stmt.order_by(HealthEntry.recorded_at.desc()).offset((page - 1) * size).limit(size)
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt).all())
        return items, total

    def update(self, item: HealthEntry, updates: dict) -> HealthEntry:
        for field, value in updates.items():
            setattr(item, field, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: HealthEntry) -> None:
        self.db.delete(item)
        self.db.commit()
