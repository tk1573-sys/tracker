from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_mode_id, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.reminder import ReminderCreate, ReminderRead
from app.services.reminders import create_default_follow_up_rule, create_reminder, list_reminders

router = APIRouter()


@router.get("", response_model=list[ReminderRead])
def get_reminders(
    include_all_modes: bool = Query(default=False),
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReminderRead]:
    return list_reminders(db, user_id=current_user.id, mode_id=active_mode_id, include_all_modes=include_all_modes)


@router.post("", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
def add_reminder(
    payload: ReminderCreate,
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReminderRead:
    reminder = create_reminder(db, user_id=current_user.id, payload=payload, mode_id=active_mode_id)
    create_default_follow_up_rule(db, user_id=current_user.id, mode_id=reminder.mode_id)
    return reminder
