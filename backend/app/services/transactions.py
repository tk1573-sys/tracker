from datetime import datetime

from app.core.errors import NotFoundError
from app.models.transaction import TransactionType
from app.repositories.transactions import TransactionRepository
from app.schemas.common import Pagination
from app.schemas.transaction import TransactionCreate, TransactionList, TransactionUpdate


class TransactionService:
    def __init__(self, repository: TransactionRepository) -> None:
        self.repository = repository

    def create(self, user_id: int, payload: TransactionCreate):
        data = payload.model_dump()
        data["user_id"] = user_id
        return self.repository.create(data)

    def get(self, user_id: int, item_id: int):
        item = self.repository.get(user_id, item_id)
        if not item:
            raise NotFoundError("Transaction not found")
        return item

    def list(
        self,
        user_id: int,
        page: int,
        size: int,
        tx_type: TransactionType | None,
        category: str | None,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> TransactionList:
        items, total = self.repository.list(user_id, page, size, tx_type, category, start_date, end_date)
        return TransactionList(pagination=Pagination(page=page, size=size, total=total), items=items)

    def update(self, user_id: int, item_id: int, payload: TransactionUpdate):
        item = self.get(user_id, item_id)
        return self.repository.update(item, payload.model_dump(exclude_unset=True))

    def delete(self, user_id: int, item_id: int) -> None:
        item = self.get(user_id, item_id)
        self.repository.delete(item)
