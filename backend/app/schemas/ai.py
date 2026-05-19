from datetime import datetime

from pydantic import BaseModel

from app.schemas.reminder import ReminderRead
from app.schemas.task import TaskRead


class AICommandRequest(BaseModel):
    message: str
    mode_id: int | None = None


class AIParsedIntent(BaseModel):
    intent: str
    title: str | None = None
    due_at: datetime | None = None
    remind_at: datetime | None = None
    confidence: float
    needs_clarification: bool = False
    clarification_message: str | None = None


class AICommandResponse(BaseModel):
    parsed: AIParsedIntent
    created_task: TaskRead | None = None
    created_reminder: ReminderRead | None = None
    message: str
