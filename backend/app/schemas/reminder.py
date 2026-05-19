from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ReminderChannel = Literal["in_app", "email", "sms"]

class ReminderCreate(BaseModel):
    remind_at: datetime
    task_id: int | None = None
    mode_id: int | None = None
    channel: ReminderChannel = "in_app"

    model_config = ConfigDict(str_strip_whitespace=True)


class ReminderRead(BaseModel):
    id: int
    user_id: int
    task_id: int | None
    mode_id: int
    remind_at: datetime
    channel: ReminderChannel
    status: str

    model_config = ConfigDict(from_attributes=True)


class FollowUpRuleRead(BaseModel):
    id: int
    mode_id: int
    trigger_type: str
    delay_minutes: int = Field(ge=1)
    max_retries: int = Field(ge=0)
    active: bool

    model_config = ConfigDict(from_attributes=True)
