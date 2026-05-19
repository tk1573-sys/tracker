from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class JournalEntryCreate(BaseModel):
    content: str
    mood_score: int | None = Field(default=None, ge=1, le=5)
    tags: str | None = None
    entry_date: date | None = None
    mode_id: int | None = None


class JournalEntryRead(BaseModel):
    id: int
    user_id: int
    mode_id: int
    entry_date: date
    mood_score: int | None
    content: str
    tags: str | None

    model_config = ConfigDict(from_attributes=True)
