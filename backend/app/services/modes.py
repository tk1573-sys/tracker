from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.mode import Mode
from app.services.common import commit_or_rollback, flush_or_rollback


def ensure_default_modes(db: Session, user_id: int, *, auto_commit: bool = True) -> None:
    existing = db.scalars(select(Mode).where(Mode.user_id == user_id)).all()
    if existing:
        return

    modes = [
        Mode(user_id=user_id, name="personal", is_active_default=True),
        Mode(user_id=user_id, name="work", is_active_default=False),
        Mode(user_id=user_id, name="academic", is_active_default=False),
    ]
    db.add_all(modes)
    flush_or_rollback(db)

    defaults_by_mode = {
        "personal": ["life", "wellness", "family"],
        "work": ["project", "meeting", "deep-work"],
        "academic": ["study", "assignment", "exam"],
    }

    for mode in modes:
        for name in defaults_by_mode.get(mode.name, []):
            db.add(Category(user_id=user_id, mode_id=mode.id, name=name, type="task"))

    if auto_commit:
        commit_or_rollback(db)


def list_modes(db: Session, user_id: int) -> list[Mode]:
    return db.scalars(select(Mode).where(Mode.user_id == user_id).order_by(Mode.id.asc())).all()


def get_active_mode(db: Session, user_id: int) -> Mode | None:
    active = db.scalar(select(Mode).where(Mode.user_id == user_id, Mode.is_active_default.is_(True)))
    if active:
        return active
    return db.scalar(select(Mode).where(Mode.user_id == user_id).order_by(Mode.id.asc()))


def activate_mode(db: Session, user_id: int, mode_id: int) -> Mode | None:
    mode = db.scalar(select(Mode).where(Mode.id == mode_id, Mode.user_id == user_id))
    if not mode:
        return None

    db.execute(update(Mode).where(Mode.user_id == user_id).values(is_active_default=False))
    mode.is_active_default = True
    db.add(mode)
    commit_or_rollback(db)
    db.refresh(mode)
    return mode
