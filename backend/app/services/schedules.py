from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate
from app.services.common import commit_or_rollback, ensure_task_access, flush_or_rollback, resolve_mode_id, scoped_by_user_mode


def create_schedule(
    db: Session,
    user_id: int,
    payload: ScheduleCreate,
    mode_id: int,
    *,
    auto_commit: bool = True,
) -> Schedule:
    resolved_mode_id = resolve_mode_id(db, user_id=user_id, requested_mode_id=payload.mode_id, fallback_mode_id=mode_id)
    if payload.linked_task_id is not None:
        ensure_task_access(db, user_id=user_id, task_id=payload.linked_task_id, mode_id=resolved_mode_id)
    schedule = Schedule(
        user_id=user_id,
        mode_id=resolved_mode_id,
        title=payload.title,
        start_at=payload.start_at,
        end_at=payload.end_at,
        linked_task_id=payload.linked_task_id,
    )
    db.add(schedule)
    if auto_commit:
        commit_or_rollback(db)
        db.refresh(schedule)
    else:
        flush_or_rollback(db)
    return schedule


def list_schedules(db: Session, user_id: int, mode_id: int | None, include_all_modes: bool) -> list[Schedule]:
    stmt = select(Schedule).order_by(Schedule.start_at.asc())
    stmt = scoped_by_user_mode(stmt, Schedule, user_id=user_id, mode_id=mode_id, include_all_modes=include_all_modes)
    return db.scalars(stmt).all()
