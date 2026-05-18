from datetime import date

from app.core.errors import NotFoundError
from app.repositories.journal_entries import JournalEntryRepository
from app.schemas.common import Pagination
from app.schemas.journal_entry import JournalEntryCreate, JournalEntryList, JournalEntryUpdate


class JournalEntryService:
    def __init__(self, repository: JournalEntryRepository) -> None:
        self.repository = repository

    def create(self, user_id: int, payload: JournalEntryCreate):
        data = payload.model_dump()
        data["user_id"] = user_id
        return self.repository.create(data)

    def get(self, user_id: int, item_id: int):
        item = self.repository.get(user_id, item_id)
        if not item:
            raise NotFoundError("Journal entry not found")
        return item

    def list(self, user_id: int, page: int, size: int, entry_date: date | None, mood: int | None) -> JournalEntryList:
        items, total = self.repository.list(user_id, page, size, entry_date, mood)
        return JournalEntryList(pagination=Pagination(page=page, size=size, total=total), items=items)

    def update(self, user_id: int, item_id: int, payload: JournalEntryUpdate):
        item = self.get(user_id, item_id)
        return self.repository.update(item, payload.model_dump(exclude_unset=True))

    def delete(self, user_id: int, item_id: int) -> None:
        item = self.get(user_id, item_id)
        self.repository.delete(item)
