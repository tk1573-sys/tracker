from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScheduleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    start_at: datetime
    end_at: datetime
    linked_task_id: int | None = None
    mode_id: int | None = None

    @model_validator(mode="after")
    def validate_window(self) -> "ScheduleCreate":
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self


class ScheduleRead(BaseModel):
    id: int
    user_id: int
    mode_id: int
    title: str
    start_at: datetime
    end_at: datetime
    linked_task_id: int | None

    model_config = ConfigDict(from_attributes=True)
