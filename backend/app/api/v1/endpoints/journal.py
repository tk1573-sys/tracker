from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.journal_entries import JournalEntryRepository
from app.schemas.journal_entry import JournalEntryCreate, JournalEntryList, JournalEntryRead, JournalEntryUpdate
from app.services.journal_entries import JournalEntryService

router = APIRouter(prefix="/journal", tags=["journal"])


def get_service(db: Session) -> JournalEntryService:
    return JournalEntryService(JournalEntryRepository(db))


@router.post("", response_model=JournalEntryRead, status_code=status.HTTP_201_CREATED)
def create_journal_entry(payload: JournalEntryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).create(current_user.id, payload)


@router.get("", response_model=JournalEntryList)
def list_journal_entries(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    entry_date: date | None = Query(default=None),
    mood: int | None = Query(default=None, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_service(db).list(current_user.id, page, size, entry_date, mood)


@router.get("/{entry_id}", response_model=JournalEntryRead)
def get_journal_entry(entry_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_service(db).get(current_user.id, entry_id)


@router.patch("/{entry_id}", response_model=JournalEntryRead)
def update_journal_entry(
    entry_id: int,
    payload: JournalEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_service(db).update(current_user.id, entry_id, payload)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_entry(entry_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_service(db).delete(current_user.id, entry_id)
