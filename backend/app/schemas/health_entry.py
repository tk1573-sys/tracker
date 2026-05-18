from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Pagination


class HealthEntryBase(BaseModel):
    metric_type: str = Field(min_length=1, max_length=80)
    value: float
    unit: str = Field(min_length=1, max_length=30)
    notes: str | None = Field(default=None, max_length=2000)
    recorded_at: datetime


class HealthEntryCreate(HealthEntryBase):
    pass


class HealthEntryUpdate(BaseModel):
    metric_type: str | None = Field(default=None, min_length=1, max_length=80)
    value: float | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    notes: str | None = Field(default=None, max_length=2000)
    recorded_at: datetime | None = None


class HealthEntryRead(HealthEntryBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class HealthEntryList(BaseModel):
    pagination: Pagination
    items: list[HealthEntryRead]
