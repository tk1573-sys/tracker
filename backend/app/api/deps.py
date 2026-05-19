from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_subject_from_token
from app.db.session import get_db
from app.models.mode import Mode
from app.models.user import User
from app.services.modes import ensure_default_modes, get_active_mode

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    subject = get_subject_from_token(token)
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.scalar(select(User).where(User.email == subject))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_active_mode_id(
    x_mode_id: int | None = Header(default=None, alias="X-Mode-Id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> int:
    ensure_default_modes(db, current_user.id)

    if x_mode_id is not None:
        mode = db.scalar(select(Mode).where(Mode.id == x_mode_id, Mode.user_id == current_user.id))
        if not mode:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mode not found")
        return mode.id

    active_mode = get_active_mode(db, current_user.id)
    if not active_mode:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No mode configured")
    return active_mode.id
