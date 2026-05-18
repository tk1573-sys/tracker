from datetime import datetime

from app.core.errors import NotFoundError
from app.repositories.health_entries import HealthEntryRepository
from app.schemas.common import Pagination
from app.schemas.health_entry import HealthEntryCreate, HealthEntryList, HealthEntryUpdate


class HealthEntryService:
    def __init__(self, repository: HealthEntryRepository) -> None:
        self.repository = repository

    def create(self, user_id: int, payload: HealthEntryCreate):
        data = payload.model_dump()
        data["user_id"] = user_id
        return self.repository.create(data)

    def get(self, user_id: int, item_id: int):
        item = self.repository.get(user_id, item_id)
        if not item:
            raise NotFoundError("Health record not found")
        return item

    def list(
        self,
        user_id: int,
        page: int,
        size: int,
        metric_type: str | None,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> HealthEntryList:
        items, total = self.repository.list(user_id, page, size, metric_type, start_date, end_date)
        return HealthEntryList(pagination=Pagination(page=page, size=size, total=total), items=items)

    def update(self, user_id: int, item_id: int, payload: HealthEntryUpdate):
        item = self.get(user_id, item_id)
        return self.repository.update(item, payload.model_dump(exclude_unset=True))

    def delete(self, user_id: int, item_id: int) -> None:
        item = self.get(user_id, item_id)
        self.repository.delete(item)
