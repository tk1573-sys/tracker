from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_mode_id, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.journal import JournalEntryCreate, JournalEntryRead
from app.services.journal import create_journal_entry, list_journal_entries

router = APIRouter()


@router.get("", response_model=list[JournalEntryRead])
def get_journal_entries(
    include_all_modes: bool = Query(default=False),
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[JournalEntryRead]:
    return list_journal_entries(db, user_id=current_user.id, mode_id=active_mode_id, include_all_modes=include_all_modes)


@router.post("", response_model=JournalEntryRead, status_code=status.HTTP_201_CREATED)
def add_journal_entry(
    payload: JournalEntryCreate,
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JournalEntryRead:
    return create_journal_entry(db, user_id=current_user.id, payload=payload, mode_id=active_mode_id)
