from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.models.goal import GoalStatus
from app.models.user import User
from app.repositories.goals import GoalRepository
from app.schemas.goal import GoalCreate, GoalList, GoalRead, GoalUpdate
from app.services.goals import GoalService

router = APIRouter(prefix="/goals", tags=["goals"])


def get_service(db: Session) -> GoalService:
    return GoalService(GoalRepository(db))


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.target_value is not None and payload.current_value is not None and payload.current_value > payload.target_value:
        raise AppError("current_value cannot exceed target_value", status_code=422)
    return get_service(db).create(current_user.id, payload)


@router.get("", response_model=GoalList)
def list_goals(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    status_filter: GoalStatus | None = Query(default=None, alias="status"),
    due_before: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_service(db).list(current_user.id, page, size, status_filter, due_before)


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(goal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).get(current_user.id, goal_id)


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(goal_id: int, payload: GoalUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return get_service(db).update(current_user.id, goal_id, payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=422) from exc


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_service(db).delete(current_user.id, goal_id)
