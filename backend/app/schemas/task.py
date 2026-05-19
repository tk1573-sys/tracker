from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

TaskPriority = Literal["low", "medium", "high"]
TaskStatus = Literal["pending", "in_progress", "completed", "cancelled"]


class SubtaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    due_at: datetime | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class SubtaskRead(BaseModel):
    id: int
    task_id: int
    title: str
    status: str
    due_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    notes: str | None = Field(default=None, max_length=5000)
    priority: TaskPriority = "medium"
    due_at: datetime | None = None
    mode_id: int | None = None
    category_id: int | None = None
    subtasks: list[SubtaskCreate] = Field(default_factory=list)

    model_config = ConfigDict(str_strip_whitespace=True)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    notes: str | None = Field(default=None, max_length=5000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_at: datetime | None = None
    mode_id: int | None = None
    category_id: int | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="after")
    def ensure_non_empty_update(self) -> "TaskUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class TaskRead(BaseModel):
    id: int
    user_id: int
    mode_id: int
    category_id: int | None
    title: str
    notes: str | None
    status: str
    priority: str
    due_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    subtasks: list[SubtaskRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
