from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_mode_id, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleRead
from app.services.schedules import create_schedule, list_schedules

router = APIRouter()


@router.get("", response_model=list[ScheduleRead])
def get_schedules(
    include_all_modes: bool = Query(default=False),
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ScheduleRead]:
    return list_schedules(db, user_id=current_user.id, mode_id=active_mode_id, include_all_modes=include_all_modes)


@router.post("", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
def add_schedule(
    payload: ScheduleCreate,
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScheduleRead:
    return create_schedule(db, user_id=current_user.id, payload=payload, mode_id=active_mode_id)
