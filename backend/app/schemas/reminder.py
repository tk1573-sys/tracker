from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.reminder import ReminderPriority
from app.schemas.common import Pagination


class ReminderBase(BaseModel):
    title: str = Field(min_length=1, max_length=140)
    description: str | None = Field(default=None, max_length=3000)
    remind_at: datetime
    is_completed: bool = False
    priority: ReminderPriority = ReminderPriority.medium


class ReminderCreate(ReminderBase):
    pass


class ReminderUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=140)
    description: str | None = Field(default=None, max_length=3000)
    remind_at: datetime | None = None
    is_completed: bool | None = None
    priority: ReminderPriority | None = None


class ReminderRead(ReminderBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class ReminderList(BaseModel):
    pagination: Pagination
    items: list[ReminderRead]
