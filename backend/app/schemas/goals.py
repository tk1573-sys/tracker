from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MilestoneCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    due_at: datetime | None = None
    weight: int = Field(default=1, ge=1, le=10)


class MilestoneUpdate(BaseModel):
    status: Literal["pending", "in_progress", "completed"] | None = None
    completion_score: float | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def ensure_non_empty(self) -> "MilestoneUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class MilestoneRead(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    due_at: datetime | None
    status: str
    weight: int
    completion_score: float
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ExecutionPhaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    sequence_index: int = Field(default=1, ge=1)
    start_at: datetime | None = None
    end_at: datetime | None = None


class ExecutionPhaseRead(BaseModel):
    id: int
    project_id: int
    name: str
    sequence_index: int
    status: str
    start_at: datetime | None
    end_at: datetime | None
    progress_percent: float

    model_config = ConfigDict(from_attributes=True)


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    project_id: int | None = None
    target_date: datetime | None = None
    mode_id: int | None = None


class GoalUpdate(BaseModel):
    status: Literal["active", "on_hold", "completed", "archived"] | None = None
    completion_score: float | None = Field(default=None, ge=0, le=100)
    progress_percent: float | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def ensure_non_empty(self) -> "GoalUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class GoalRead(BaseModel):
    id: int
    user_id: int
    mode_id: int
    project_id: int | None
    title: str
    description: str | None
    status: str
    target_date: datetime | None
    progress_percent: float
    completion_score: float
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    deadline: datetime | None = None
    mode_id: int | None = None
    milestones: list[MilestoneCreate] = Field(default_factory=list)
    phases: list[ExecutionPhaseCreate] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    status: Literal["active", "on_hold", "completed", "archived"] | None = None
    completion_score: float | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def ensure_non_empty(self) -> "ProjectUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class ProjectRead(BaseModel):
    id: int
    user_id: int
    mode_id: int
    title: str
    description: str | None
    status: str
    deadline: datetime | None
    completion_score: float
    created_at: datetime
    completed_at: datetime | None
    milestones: list[MilestoneRead] = Field(default_factory=list)
    phases: list[ExecutionPhaseRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class WorkflowPlanRead(BaseModel):
    project: ProjectRead
    goal: GoalRead | None = None
    linked_task_id: int | None = None
    reminder_ids: list[int] = Field(default_factory=list)
    schedule_ids: list[int] = Field(default_factory=list)
