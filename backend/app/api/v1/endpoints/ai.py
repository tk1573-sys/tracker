from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_active_mode_id, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import AICommandRequest, AICommandResponse
from app.schemas.reminder import ReminderRead
from app.schemas.task import TaskRead
from app.services.ai import execute_ai_command

router = APIRouter()


@router.post("/command", response_model=AICommandResponse)
def ai_command(
    payload: AICommandRequest,
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AICommandResponse:
    mode_id = payload.mode_id or active_mode_id
    parsed, created_task, created_reminder = execute_ai_command(
        db,
        user=current_user,
        mode_id=mode_id,
        message=payload.message,
    )

    task_read = TaskRead.model_validate(created_task) if created_task else None
    reminder_read = ReminderRead.model_validate(created_reminder) if created_reminder else None

    if parsed.needs_clarification:
        msg = parsed.clarification_message or "Need more details."
    elif created_task and created_reminder:
        msg = "Created task and reminder successfully."
    elif created_task:
        msg = "Created task successfully."
    else:
        msg = "Command processed."

    return AICommandResponse(parsed=parsed, created_task=task_read, created_reminder=reminder_read, message=msg)
