from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate


def create_schedule(db: Session, user_id: int, payload: ScheduleCreate, mode_id: int) -> Schedule:
    schedule = Schedule(
        user_id=user_id,
        mode_id=payload.mode_id or mode_id,
        title=payload.title,
        start_at=payload.start_at,
        end_at=payload.end_at,
        linked_task_id=payload.linked_task_id,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def list_schedules(db: Session, user_id: int, mode_id: int | None, include_all_modes: bool) -> list[Schedule]:
    stmt = select(Schedule).where(Schedule.user_id == user_id).order_by(Schedule.start_at.asc())
    if not include_all_modes and mode_id is not None:
        stmt = stmt.where(Schedule.mode_id == mode_id)
    return db.scalars(stmt).all()
