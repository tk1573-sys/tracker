from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScheduleCreate(BaseModel):
    title: str
    start_at: datetime
    end_at: datetime
    linked_task_id: int | None = None
    mode_id: int | None = None


class ScheduleRead(BaseModel):
    id: int
    user_id: int
    mode_id: int
    title: str
    start_at: datetime
    end_at: datetime
    linked_task_id: int | None

    model_config = ConfigDict(from_attributes=True)
