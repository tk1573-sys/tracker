from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.goal import GoalStatus
from app.schemas.common import Pagination


class GoalBase(BaseModel):
    title: str = Field(min_length=1, max_length=140)
    description: str | None = Field(default=None, max_length=4000)
    target_value: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    current_value: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    due_date: date | None = None
    status: GoalStatus = GoalStatus.active


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=140)
    description: str | None = Field(default=None, max_length=4000)
    target_value: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    current_value: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    due_date: date | None = None
    status: GoalStatus | None = None


class GoalRead(GoalBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class GoalList(BaseModel):
    pagination: Pagination
    items: list[GoalRead]
