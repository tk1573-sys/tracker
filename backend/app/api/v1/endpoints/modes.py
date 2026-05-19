from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.mode import ModeActivate, ModeRead
from app.services.modes import activate_mode, ensure_default_modes, list_modes

router = APIRouter()


@router.get("", response_model=list[ModeRead])
def get_modes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ModeRead]:
    ensure_default_modes(db, current_user.id)
    return list_modes(db, current_user.id)


@router.post("/activate", response_model=ModeRead)
def set_active_mode(payload: ModeActivate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ModeRead:
    mode = activate_mode(db, current_user.id, payload.mode_id)
    if not mode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mode not found")
    return mode
