from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_active_mode_id, get_current_user
from app.db.session import get_db
from app.models.task import Subtask
from app.models.user import User
from app.schemas.task import SubtaskRead, TaskCreate, TaskRead, TaskUpdate
from app.services.tasks import create_task, list_subtasks, list_tasks, update_task

router = APIRouter()


@router.get("", response_model=list[TaskRead])
def get_tasks(
    include_all_modes: bool = Query(default=False),
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TaskRead]:
    tasks = list_tasks(db, current_user.id, active_mode_id, include_all_modes)
    task_ids = [task.id for task in tasks]
    subtasks = list_subtasks(db, task_ids)
    subtasks_by_task: dict[int, list[Subtask]] = {}
    for subtask in subtasks:
        subtasks_by_task.setdefault(subtask.task_id, []).append(subtask)

    response: list[TaskRead] = []
    for task in tasks:
        record = TaskRead.model_validate(task)
        record.subtasks = [SubtaskRead.model_validate(sub) for sub in subtasks_by_task.get(task.id, [])]
        response.append(record)
    return response


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def add_task(
    payload: TaskCreate,
    active_mode_id: int = Depends(get_active_mode_id),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = create_task(db, user_id=current_user.id, payload=payload, mode_id=active_mode_id)
    record = TaskRead.model_validate(task)
    record.subtasks = []
    return record


@router.patch("/{task_id}", response_model=TaskRead)
def patch_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskRead:
    task = update_task(db, user_id=current_user.id, task_id=task_id, payload=payload)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    record = TaskRead.model_validate(task)
    record.subtasks = []
    return record
