from app.core.errors import NotFoundError
from app.models.habit import HabitFrequency
from app.repositories.habits import HabitRepository
from app.schemas.common import Pagination
from app.schemas.habit import HabitCreate, HabitList, HabitUpdate


class HabitService:
    def __init__(self, repository: HabitRepository) -> None:
        self.repository = repository

    def create(self, user_id: int, payload: HabitCreate):
        data = payload.model_dump()
        data["user_id"] = user_id
        return self.repository.create(data)

    def get(self, user_id: int, item_id: int):
        item = self.repository.get(user_id, item_id)
        if not item:
            raise NotFoundError("Habit not found")
        return item

    def list(self, user_id: int, page: int, size: int, frequency: HabitFrequency | None, is_active: bool | None) -> HabitList:
        items, total = self.repository.list(user_id, page, size, frequency, is_active)
        return HabitList(pagination=Pagination(page=page, size=size, total=total), items=items)

    def update(self, user_id: int, item_id: int, payload: HabitUpdate):
        item = self.get(user_id, item_id)
        return self.repository.update(item, payload.model_dump(exclude_unset=True))

    def delete(self, user_id: int, item_id: int) -> None:
        item = self.get(user_id, item_id)
        self.repository.delete(item)
