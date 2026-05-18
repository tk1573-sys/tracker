from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.habit import Habit, HabitFrequency


class HabitRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict) -> Habit:
        item = Habit(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, user_id: int, item_id: int) -> Habit | None:
        return self.db.scalar(select(Habit).where(Habit.id == item_id, Habit.user_id == user_id))

    def list(
        self, user_id: int, page: int, size: int, frequency: HabitFrequency | None = None, is_active: bool | None = None
    ) -> tuple[list[Habit], int]:
        stmt = select(Habit).where(Habit.user_id == user_id)
        count_stmt = select(func.count(Habit.id)).where(Habit.user_id == user_id)

        if frequency is not None:
            stmt = stmt.where(Habit.frequency == frequency)
            count_stmt = count_stmt.where(Habit.frequency == frequency)
        if is_active is not None:
            stmt = stmt.where(Habit.is_active == is_active)
            count_stmt = count_stmt.where(Habit.is_active == is_active)

        stmt = stmt.order_by(Habit.created_at.desc()).offset((page - 1) * size).limit(size)
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt).all())
        return items, total

    def update(self, item: Habit, updates: dict) -> Habit:
        for field, value in updates.items():
            setattr(item, field, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: Habit) -> None:
        self.db.delete(item)
        self.db.commit()
