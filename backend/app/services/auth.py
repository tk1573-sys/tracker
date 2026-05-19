from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import UserCreate
from app.services.modes import ensure_default_modes


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, payload: UserCreate) -> User:
    user = User(email=payload.email, hashed_password=get_password_hash(payload.password))
    try:
        db.add(user)
        db.flush()
        ensure_default_modes(db, user.id, auto_commit=False)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise
