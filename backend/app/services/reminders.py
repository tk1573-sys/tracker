from datetime import datetime

from app.core.errors import NotFoundError
from app.models.reminder import ReminderPriority
from app.repositories.reminders import ReminderRepository
from app.schemas.common import Pagination
from app.schemas.reminder import ReminderCreate, ReminderList, ReminderUpdate


class ReminderService:
    def __init__(self, repository: ReminderRepository) -> None:
        self.repository = repository

    def create(self, user_id: int, payload: ReminderCreate):
        data = payload.model_dump()
        data["user_id"] = user_id
        return self.repository.create(data)

    def get(self, user_id: int, item_id: int):
        item = self.repository.get(user_id, item_id)
        if not item:
            raise NotFoundError("Reminder not found")
        return item

    def list(
        self,
        user_id: int,
        page: int,
        size: int,
        is_completed: bool | None,
        priority: ReminderPriority | None,
        due_before: datetime | None,
    ) -> ReminderList:
        items, total = self.repository.list(user_id, page, size, is_completed, priority, due_before)
        return ReminderList(pagination=Pagination(page=page, size=size, total=total), items=items)

    def update(self, user_id: int, item_id: int, payload: ReminderUpdate):
        item = self.get(user_id, item_id)
        return self.repository.update(item, payload.model_dump(exclude_unset=True))

    def delete(self, user_id: int, item_id: int) -> None:
        item = self.get(user_id, item_id)
        self.repository.delete(item)
