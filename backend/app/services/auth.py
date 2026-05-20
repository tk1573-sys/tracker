from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import UserCreate
from app.services.common import commit_or_rollback, flush_or_rollback
from app.services.modes import ensure_default_modes


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, payload: UserCreate) -> User:
    try:
        user = User(email=payload.email, hashed_password=get_password_hash(payload.password))
        db.add(user)
        flush_or_rollback(db)
        ensure_default_modes(db, user.id, auto_commit=False)
        commit_or_rollback(db)
        db.refresh(user)
        return user
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Email already registered", code="email_conflict") from exc
