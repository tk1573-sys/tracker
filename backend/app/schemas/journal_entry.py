from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Pagination


class JournalEntryBase(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    content: str = Field(min_length=1, max_length=10000)
    mood: int | None = Field(default=None, ge=1, le=10)
    entry_date: date


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    content: str | None = Field(default=None, min_length=1, max_length=10000)
    mood: int | None = Field(default=None, ge=1, le=10)
    entry_date: date | None = None


class JournalEntryRead(JournalEntryBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class JournalEntryList(BaseModel):
    pagination: Pagination
    items: list[JournalEntryRead]
