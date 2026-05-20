from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ReminderCreate(BaseModel):
    remind_at: datetime
    task_id: int | None = None
    mode_id: int | None = None
    channel: Literal["in_app", "email"] = "in_app"


class ReminderRead(BaseModel):
    id: int
    user_id: int
    task_id: int | None
    mode_id: int
    remind_at: datetime
    channel: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class FollowUpRuleRead(BaseModel):
    id: int
    mode_id: int
    trigger_type: str
    delay_minutes: int
    max_retries: int
    active: bool

    model_config = ConfigDict(from_attributes=True)
