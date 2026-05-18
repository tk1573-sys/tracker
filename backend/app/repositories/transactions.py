from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType


class TransactionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: dict) -> Transaction:
        item = Transaction(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get(self, user_id: int, item_id: int) -> Transaction | None:
        return self.db.scalar(select(Transaction).where(Transaction.id == item_id, Transaction.user_id == user_id))

    def list(
        self,
        user_id: int,
        page: int,
        size: int,
        tx_type: TransactionType | None = None,
        category: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[list[Transaction], int]:
        stmt = select(Transaction).where(Transaction.user_id == user_id)
        count_stmt = select(func.count(Transaction.id)).where(Transaction.user_id == user_id)

        if tx_type is not None:
            stmt = stmt.where(Transaction.type == tx_type)
            count_stmt = count_stmt.where(Transaction.type == tx_type)
        if category:
            stmt = stmt.where(Transaction.category == category)
            count_stmt = count_stmt.where(Transaction.category == category)
        if start_date:
            stmt = stmt.where(Transaction.occurred_at >= start_date)
            count_stmt = count_stmt.where(Transaction.occurred_at >= start_date)
        if end_date:
            stmt = stmt.where(Transaction.occurred_at <= end_date)
            count_stmt = count_stmt.where(Transaction.occurred_at <= end_date)

        stmt = stmt.order_by(Transaction.occurred_at.desc()).offset((page - 1) * size).limit(size)
        total = self.db.scalar(count_stmt) or 0
        items = list(self.db.scalars(stmt).all())
        return items, total

    def update(self, item: Transaction, updates: dict) -> Transaction:
        for field, value in updates.items():
            setattr(item, field, value)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: Transaction) -> None:
        self.db.delete(item)
        self.db.commit()
