from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_active_mode_id, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.tracker import TrackerSummary
from app.services.trackers import get_tracker_summary

router = APIRouter()


@router.get("/summary", response_model=TrackerSummary)
def tracker_summary(
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TrackerSummary:
    return get_tracker_summary(db, user_id=current_user.id, mode_id=active_mode_id)
