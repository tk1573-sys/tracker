from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_active_mode_id, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import get_dashboard

router = APIRouter()


@router.get("", response_model=DashboardResponse)
def dashboard(
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    return get_dashboard(db, user_id=current_user.id, mode_id=active_mode_id)
