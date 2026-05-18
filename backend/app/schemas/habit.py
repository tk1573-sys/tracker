from pydantic import BaseModel, ConfigDict, Field

from app.models.habit import HabitFrequency
from app.schemas.common import Pagination


class HabitBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    frequency: HabitFrequency
    target_count: int = Field(default=1, ge=1, le=1000)
    streak: int = Field(default=0, ge=0)
    is_active: bool = True
    notes: str | None = Field(default=None, max_length=2000)


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    frequency: HabitFrequency | None = None
    target_count: int | None = Field(default=None, ge=1, le=1000)
    streak: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    notes: str | None = Field(default=None, max_length=2000)


class HabitRead(HabitBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class HabitList(BaseModel):
    pagination: Pagination
    items: list[HabitRead]
