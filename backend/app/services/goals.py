from datetime import date

from app.core.errors import NotFoundError
from app.models.goal import GoalStatus
from app.repositories.goals import GoalRepository
from app.schemas.common import Pagination
from app.schemas.goal import GoalCreate, GoalList, GoalUpdate


class GoalService:
    def __init__(self, repository: GoalRepository) -> None:
        self.repository = repository

    def create(self, user_id: int, payload: GoalCreate):
        data = payload.model_dump()
        data["user_id"] = user_id
        return self.repository.create(data)

    def get(self, user_id: int, item_id: int):
        item = self.repository.get(user_id, item_id)
        if not item:
            raise NotFoundError("Goal not found")
        return item

    def list(self, user_id: int, page: int, size: int, status: GoalStatus | None, due_before: date | None) -> GoalList:
        items, total = self.repository.list(user_id, page, size, status, due_before)
        return GoalList(pagination=Pagination(page=page, size=size, total=total), items=items)

    def update(self, user_id: int, item_id: int, payload: GoalUpdate):
        item = self.get(user_id, item_id)
        updates = payload.model_dump(exclude_unset=True)
        target_value = updates.get("target_value")
        current_value = updates.get("current_value")
        if target_value is not None and current_value is not None and current_value > target_value:
            raise ValueError("current_value cannot exceed target_value")
        return self.repository.update(item, updates)

    def delete(self, user_id: int, item_id: int) -> None:
        item = self.get(user_id, item_id)
        self.repository.delete(item)
