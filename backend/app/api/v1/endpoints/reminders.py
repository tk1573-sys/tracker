from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.reminder import ReminderPriority
from app.models.user import User
from app.repositories.reminders import ReminderRepository
from app.schemas.reminder import ReminderCreate, ReminderList, ReminderRead, ReminderUpdate
from app.services.reminders import ReminderService

router = APIRouter(prefix="/reminders", tags=["reminders"])


def get_service(db: Session) -> ReminderService:
    return ReminderService(ReminderRepository(db))


@router.post("", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
def create_reminder(payload: ReminderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).create(current_user.id, payload)


@router.get("", response_model=ReminderList)
def list_reminders(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    is_completed: bool | None = Query(default=None),
    priority: ReminderPriority | None = Query(default=None),
    due_before: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_service(db).list(current_user.id, page, size, is_completed, priority, due_before)


@router.get("/{reminder_id}", response_model=ReminderRead)
def get_reminder(reminder_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).get(current_user.id, reminder_id)


@router.patch("/{reminder_id}", response_model=ReminderRead)
def update_reminder(
    reminder_id: int,
    payload: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_service(db).update(current_user.id, reminder_id, payload)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_service(db).delete(current_user.id, reminder_id)
