from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.health_entries import HealthEntryRepository
from app.schemas.health_entry import HealthEntryCreate, HealthEntryList, HealthEntryRead, HealthEntryUpdate
from app.services.health_entries import HealthEntryService

router = APIRouter(prefix="/health/records", tags=["health"])


def get_service(db: Session) -> HealthEntryService:
    return HealthEntryService(HealthEntryRepository(db))


@router.post("", response_model=HealthEntryRead, status_code=status.HTTP_201_CREATED)
def create_health_record(payload: HealthEntryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).create(current_user.id, payload)


@router.get("", response_model=HealthEntryList)
def list_health_records(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    metric_type: str | None = Query(default=None),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_service(db).list(current_user.id, page, size, metric_type, start_date, end_date)


@router.get("/{record_id}", response_model=HealthEntryRead)
def get_health_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).get(current_user.id, record_id)


@router.patch("/{record_id}", response_model=HealthEntryRead)
def update_health_record(
    record_id: int,
    payload: HealthEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_service(db).update(current_user.id, record_id, payload)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_health_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_service(db).delete(current_user.id, record_id)
