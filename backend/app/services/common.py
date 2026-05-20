from __future__ import annotations

from typing import Any, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.models.category import Category
from app.models.mode import Mode
from app.models.task import Task

ModelT = TypeVar("ModelT")


def commit_or_rollback(db: Session) -> None:
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def flush_or_rollback(db: Session) -> None:
    try:
        db.flush()
    except Exception:
        db.rollback()
        raise


def scoped_by_user_mode(
    stmt: Select[tuple[ModelT]],
    model: type[ModelT],
    *,
    user_id: int,
    mode_id: int | None,
    include_all_modes: bool,
) -> Select[tuple[ModelT]]:
    stmt = stmt.where(getattr(model, "user_id") == user_id)
    if not include_all_modes and mode_id is not None and hasattr(model, "mode_id"):
        stmt = stmt.where(getattr(model, "mode_id") == mode_id)
    return stmt


def resolve_mode_id(db: Session, *, user_id: int, requested_mode_id: int | None, fallback_mode_id: int) -> int:
    mode_id = requested_mode_id or fallback_mode_id
    mode = db.scalar(select(Mode).where(Mode.id == mode_id, Mode.user_id == user_id))
    if mode is None:
        raise NotFoundError("Mode not found", code="mode_not_found")
    return mode.id


def ensure_task_access(db: Session, *, user_id: int, task_id: int, mode_id: int | None = None) -> Task:
    task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    if task is None:
        raise NotFoundError("Task not found", code="task_not_found")
    if mode_id is not None and task.mode_id != mode_id:
        raise ValidationError("Task does not belong to the selected mode", code="task_mode_mismatch")
    return task


def ensure_category_access(db: Session, *, user_id: int, category_id: int, mode_id: int) -> Category:
    category = db.scalar(select(Category).where(Category.id == category_id, Category.user_id == user_id))
    if category is None:
        raise NotFoundError("Category not found", code="category_not_found")
    if category.mode_id is not None and category.mode_id != mode_id:
        raise ValidationError("Category does not belong to the selected mode", code="category_mode_mismatch")
    return category
