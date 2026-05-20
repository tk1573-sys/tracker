from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.task import Subtask, Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.common import (
    commit_or_rollback,
    ensure_category_access,
    flush_or_rollback,
    resolve_mode_id,
    scoped_by_user_mode,
)

UPDATABLE_TASK_FIELDS = {"title", "notes", "status", "priority", "due_at", "mode_id", "category_id"}


def create_task(
    db: Session,
    user_id: int,
    payload: TaskCreate,
    mode_id: int,
    *,
    auto_commit: bool = True,
) -> Task:
    resolved_mode_id = resolve_mode_id(db, user_id=user_id, requested_mode_id=payload.mode_id, fallback_mode_id=mode_id)
    if payload.category_id is not None:
        ensure_category_access(db, user_id=user_id, category_id=payload.category_id, mode_id=resolved_mode_id)

    task = Task(
        user_id=user_id,
        mode_id=resolved_mode_id,
        category_id=payload.category_id,
        title=payload.title,
        notes=payload.notes,
        priority=payload.priority,
        due_at=payload.due_at,
    )
    db.add(task)
    flush_or_rollback(db)

    for subtask in payload.subtasks:
        db.add(Subtask(task_id=task.id, title=subtask.title, due_at=subtask.due_at))

    if auto_commit:
        commit_or_rollback(db)
        db.refresh(task)
    else:
        flush_or_rollback(db)
    return task


def list_tasks(db: Session, user_id: int, mode_id: int | None, include_all_modes: bool) -> list[Task]:
    stmt = select(Task).options(selectinload(Task.subtasks)).order_by(Task.created_at.desc())
    stmt = scoped_by_user_mode(stmt, Task, user_id=user_id, mode_id=mode_id, include_all_modes=include_all_modes)
    return db.scalars(stmt).all()


def update_task(
    db: Session,
    user_id: int,
    task_id: int,
    payload: TaskUpdate,
    *,
    auto_commit: bool = True,
) -> Task | None:
    task = db.scalar(select(Task).options(selectinload(Task.subtasks)).where(Task.id == task_id, Task.user_id == user_id))
    if not task:
        return None

    data = payload.model_dump(exclude_unset=True)
    if "mode_id" in data:
        data["mode_id"] = resolve_mode_id(
            db,
            user_id=user_id,
            requested_mode_id=data["mode_id"],
            fallback_mode_id=task.mode_id,
        )
    effective_mode_id = data.get("mode_id", task.mode_id)
    effective_category_id = data["category_id"] if "category_id" in data else task.category_id
    if effective_category_id is not None:
        ensure_category_access(db, user_id=user_id, category_id=effective_category_id, mode_id=effective_mode_id)
    for key, value in data.items():
        if key in UPDATABLE_TASK_FIELDS:
            setattr(task, key, value)

    if task.status == "completed" and task.completed_at is None:
        task.completed_at = datetime.now(UTC)
    elif task.status != "completed":
        task.completed_at = None

    db.add(task)
    if auto_commit:
        commit_or_rollback(db)
        db.refresh(task)
    return task
