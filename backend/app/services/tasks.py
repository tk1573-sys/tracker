from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Subtask, Task
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(
    db: Session,
    user_id: int,
    payload: TaskCreate,
    mode_id: int,
    *,
    auto_commit: bool = True,
) -> Task:
    task = Task(
        user_id=user_id,
        mode_id=payload.mode_id or mode_id,
        category_id=payload.category_id,
        title=payload.title,
        notes=payload.notes,
        priority=payload.priority,
        due_at=payload.due_at,
    )
    db.add(task)
    db.flush()

    for subtask in payload.subtasks:
        db.add(Subtask(task_id=task.id, title=subtask.title, due_at=subtask.due_at))

    if auto_commit:
        db.commit()
        db.refresh(task)
    return task


def list_tasks(db: Session, user_id: int, mode_id: int | None, include_all_modes: bool) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    if not include_all_modes and mode_id is not None:
        stmt = stmt.where(Task.mode_id == mode_id)
    return db.scalars(stmt).all()


def update_task(db: Session, user_id: int, task_id: int, payload: TaskUpdate) -> Task | None:
    task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    if not task:
        return None

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(task, key, value)

    if task.status == "completed" and task.completed_at is None:
        task.completed_at = datetime.now(UTC)
    elif task.status != "completed":
        task.completed_at = None

    db.add(task)
    if auto_commit:
        db.commit()
        db.refresh(task)
    return task


def list_subtasks(db: Session, task_ids: list[int]) -> list[Subtask]:
    if not task_ids:
        return []
    return db.scalars(select(Subtask).where(Subtask.task_id.in_(task_ids))).all()
