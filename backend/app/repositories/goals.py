from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.goal import Goal, GoalStatus


class GoalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict) -> Goal:
        item = Goal(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, user_id: int, item_id: int) -> Goal | None:
        return self.db.scalar(select(Goal).where(Goal.id == item_id, Goal.user_id == user_id))

    def list(
        self, user_id: int, page: int, size: int, status: GoalStatus | None = None, due_before: date | None = None
    ) -> tuple[list[Goal], int]:
        stmt = select(Goal).where(Goal.user_id == user_id)
        count_stmt = select(func.count(Goal.id)).where(Goal.user_id == user_id)

        if status is not None:
            stmt = stmt.where(Goal.status == status)
            count_stmt = count_stmt.where(Goal.status == status)
        if due_before:
            stmt = stmt.where(Goal.due_date <= due_before)
            count_stmt = count_stmt.where(Goal.due_date <= due_before)

        stmt = stmt.order_by(Goal.created_at.desc()).offset((page - 1) * size).limit(size)
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt).all())
        return items, total

    def update(self, item: Goal, updates: dict) -> Goal:
        for field, value in updates.items():
            setattr(item, field, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: Goal) -> None:
        self.db.delete(item)
        self.db.commit()
