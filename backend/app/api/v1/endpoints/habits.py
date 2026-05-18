from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.habit import HabitFrequency
from app.models.user import User
from app.repositories.habits import HabitRepository
from app.schemas.habit import HabitCreate, HabitList, HabitRead, HabitUpdate
from app.services.habits import HabitService

router = APIRouter(prefix="/habits", tags=["habits"])


def get_service(db: Session) -> HabitService:
    return HabitService(HabitRepository(db))


@router.post("", response_model=HabitRead, status_code=status.HTTP_201_CREATED)
def create_habit(payload: HabitCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).create(current_user.id, payload)


@router.get("", response_model=HabitList)
def list_habits(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    frequency: HabitFrequency | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_service(db).list(current_user.id, page, size, frequency, is_active)


@router.get("/{habit_id}", response_model=HabitRead)
def get_habit(habit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).get(current_user.id, habit_id)


@router.patch("/{habit_id}", response_model=HabitRead)
def update_habit(habit_id: int, payload: HabitUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).update(current_user.id, habit_id, payload)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_service(db).delete(current_user.id, habit_id)
