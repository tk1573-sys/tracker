from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubtaskCreate(BaseModel):
    title: str
    due_at: datetime | None = None


class SubtaskRead(BaseModel):
    id: int
    task_id: int
    title: str
    status: str
    due_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    title: str
    notes: str | None = None
    priority: str = "medium"
    due_at: datetime | None = None
    mode_id: int | None = None
    category_id: int | None = None
    subtasks: list[SubtaskCreate] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: str | None = None
    notes: str | None = None
    status: str | None = None
    priority: str | None = None
    due_at: datetime | None = None
    mode_id: int | None = None
    category_id: int | None = None


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
