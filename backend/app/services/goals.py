from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.execution import ExecutionPhase, Goal, Milestone, Project
from app.models.mode import Mode
from app.schemas.goals import (
    ExecutionPhaseCreate,
    GoalCreate,
    GoalUpdate,
    MilestoneCreate,
    MilestoneUpdate,
    ProjectCreate,
    ProjectUpdate,
)
from app.schemas.reminder import ReminderCreate
from app.schemas.schedule import ScheduleCreate
from app.schemas.task import SubtaskCreate, TaskCreate
from app.services.common import commit_or_rollback, ensure_project_access, flush_or_rollback, resolve_mode_id
from app.services.reminders import create_reminder
from app.services.schedules import create_schedule
from app.services.tasks import create_task


def _project_completion_score(project: Project) -> float:
    if not project.milestones:
        return 0.0
    total_weight = sum(max(milestone.weight, 1) for milestone in project.milestones)
    completed_weight = sum(max(milestone.weight, 1) for milestone in project.milestones if milestone.status == "completed")
    weighted_scores = sum(
        max(milestone.weight, 1) * (100.0 if milestone.status == "completed" and milestone.completion_score <= 0 else milestone.completion_score)
        for milestone in project.milestones
    )
    progress = (completed_weight / total_weight) * 100 if total_weight else 0.0
    quality = weighted_scores / total_weight if total_weight else 0.0
    return round((progress * 0.6) + (quality * 0.4), 2)


def _sync_project_state(project: Project, now: datetime) -> None:
    score = _project_completion_score(project)
    project.completion_score = score
    if score >= 100 and project.status != "completed":
        project.status = "completed"
        project.completed_at = now
    elif score < 100 and project.status == "completed":
        project.status = "active"
        project.completed_at = None


def _sync_goal_state(goal: Goal, project: Project | None, now: datetime) -> None:
    if project is not None:
        goal.progress_percent = project.completion_score
        goal.completion_score = project.completion_score
    if goal.completion_score >= 100 and goal.status != "completed":
        goal.status = "completed"
        goal.completed_at = now
    elif goal.completion_score < 100 and goal.status == "completed":
        goal.status = "active"
        goal.completed_at = None


def refresh_project_progress(db: Session, project_id: int, user_id: int) -> Project | None:
    project = db.scalar(
        select(Project)
        .options(selectinload(Project.milestones), selectinload(Project.goals))
        .where(Project.id == project_id, Project.user_id == user_id)
    )
    if not project:
        return None
    now = datetime.now(UTC)
    _sync_project_state(project, now)
    for goal in project.goals:
        _sync_goal_state(goal, project, now)
        db.add(goal)
    db.add(project)
    flush_or_rollback(db)
    return project


def create_project(
    db: Session,
    *,
    user_id: int,
    mode_id: int,
    payload: ProjectCreate,
    auto_commit: bool = True,
) -> Project:
    resolved_mode_id = resolve_mode_id(db, user_id=user_id, requested_mode_id=payload.mode_id, fallback_mode_id=mode_id)
    project = Project(
        user_id=user_id,
        mode_id=resolved_mode_id,
        title=payload.title,
        description=payload.description,
        deadline=payload.deadline,
    )
    db.add(project)
    flush_or_rollback(db)

    for milestone_payload in payload.milestones:
        db.add(
            Milestone(
                project_id=project.id,
                title=milestone_payload.title,
                description=milestone_payload.description,
                due_at=milestone_payload.due_at,
                weight=milestone_payload.weight,
            )
        )

    for phase_payload in payload.phases:
        db.add(
            ExecutionPhase(
                project_id=project.id,
                name=phase_payload.name,
                sequence_index=phase_payload.sequence_index,
                start_at=phase_payload.start_at,
                end_at=phase_payload.end_at,
            )
        )

    flush_or_rollback(db)
    refresh_project_progress(db, project.id, user_id)
    if auto_commit:
        commit_or_rollback(db)
        db.refresh(project)
    return project


def list_projects(db: Session, *, user_id: int, mode_id: int | None, include_all_modes: bool) -> list[Project]:
    stmt = (
        select(Project)
        .options(selectinload(Project.milestones), selectinload(Project.phases))
        .where(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
    )
    if not include_all_modes and mode_id is not None:
        stmt = stmt.where(Project.mode_id == mode_id)
    return db.scalars(stmt).all()


def update_project(
    db: Session,
    *,
    user_id: int,
    project_id: int,
    payload: ProjectUpdate,
) -> Project | None:
    project = db.scalar(
        select(Project)
        .options(selectinload(Project.milestones), selectinload(Project.goals))
        .where(Project.id == project_id, Project.user_id == user_id)
    )
    if not project:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    refresh_project_progress(db, project.id, user_id)
    commit_or_rollback(db)
    db.refresh(project)
    return project


def add_milestone(
    db: Session,
    *,
    user_id: int,
    project_id: int,
    payload: MilestoneCreate,
) -> Milestone | None:
    project = ensure_project_access(db, user_id=user_id, project_id=project_id)
    milestone = Milestone(
        project_id=project.id,
        title=payload.title,
        description=payload.description,
        due_at=payload.due_at,
        weight=payload.weight,
    )
    db.add(milestone)
    flush_or_rollback(db)
    refresh_project_progress(db, project.id, user_id)
    commit_or_rollback(db)
    db.refresh(milestone)
    return milestone


def update_milestone(
    db: Session,
    *,
    user_id: int,
    milestone_id: int,
    payload: MilestoneUpdate,
) -> Milestone | None:
    milestone = db.scalar(
        select(Milestone).join(Project, Milestone.project_id == Project.id).where(Milestone.id == milestone_id, Project.user_id == user_id)
    )
    if not milestone:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(milestone, key, value)
    if milestone.status == "completed":
        if milestone.completion_score <= 0:
            milestone.completion_score = 100.0
        milestone.completed_at = milestone.completed_at or datetime.now(UTC)
    elif milestone.status != "completed":
        milestone.completed_at = None
    db.add(milestone)
    refresh_project_progress(db, milestone.project_id, user_id)
    commit_or_rollback(db)
    db.refresh(milestone)
    return milestone


def add_execution_phase(
    db: Session,
    *,
    user_id: int,
    project_id: int,
    payload: ExecutionPhaseCreate,
) -> ExecutionPhase | None:
    project = ensure_project_access(db, user_id=user_id, project_id=project_id)
    phase = ExecutionPhase(
        project_id=project.id,
        name=payload.name,
        sequence_index=payload.sequence_index,
        start_at=payload.start_at,
        end_at=payload.end_at,
    )
    db.add(phase)
    commit_or_rollback(db)
    db.refresh(phase)
    return phase


def create_goal(
    db: Session,
    *,
    user_id: int,
    mode_id: int,
    payload: GoalCreate,
) -> Goal:
    resolved_mode_id = resolve_mode_id(db, user_id=user_id, requested_mode_id=payload.mode_id, fallback_mode_id=mode_id)
    if payload.project_id is not None:
        ensure_project_access(db, user_id=user_id, project_id=payload.project_id, mode_id=resolved_mode_id)
    goal = Goal(
        user_id=user_id,
        mode_id=resolved_mode_id,
        project_id=payload.project_id,
        title=payload.title,
        description=payload.description,
        target_date=payload.target_date,
    )
    db.add(goal)
    if payload.project_id is not None:
        refresh_project_progress(db, payload.project_id, user_id)
    commit_or_rollback(db)
    db.refresh(goal)
    return goal


def list_goals(db: Session, *, user_id: int, mode_id: int | None, include_all_modes: bool) -> list[Goal]:
    stmt = select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc())
    if not include_all_modes and mode_id is not None:
        stmt = stmt.where(Goal.mode_id == mode_id)
    return db.scalars(stmt).all()


def update_goal(db: Session, *, user_id: int, goal_id: int, payload: GoalUpdate) -> Goal | None:
    goal = db.scalar(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id))
    if not goal:
        return None
    now = datetime.now(UTC)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, key, value)
    if goal.project_id:
        project = refresh_project_progress(db, goal.project_id, user_id)
        _sync_goal_state(goal, project, now)
    else:
        _sync_goal_state(goal, None, now)
    db.add(goal)
    commit_or_rollback(db)
    db.refresh(goal)
    return goal


def resolve_suggested_mode_id(db: Session, *, user_id: int, fallback_mode_id: int, suggested_mode_name: str | None) -> int:
    if not suggested_mode_name:
        return fallback_mode_id
    mode = db.scalar(select(Mode).where(Mode.user_id == user_id, Mode.name == suggested_mode_name))
    return mode.id if mode else fallback_mode_id


def build_execution_workflow(
    db: Session,
    *,
    user_id: int,
    mode_id: int,
    project_title: str,
    deadline: datetime | None,
    suggested_mode_name: str | None = None,
    auto_commit: bool = True,
) -> tuple[Project, Goal, int | None, list[int], list[int]]:
    workflow_mode_id = resolve_suggested_mode_id(
        db,
        user_id=user_id,
        fallback_mode_id=mode_id,
        suggested_mode_name=suggested_mode_name,
    )
    now = datetime.now(UTC)
    deadline = deadline or (now + timedelta(days=7))
    milestone_1_due = now + timedelta(days=2)
    milestone_2_due = now + timedelta(days=4)

    project = create_project(
        db,
        user_id=user_id,
        mode_id=workflow_mode_id,
        payload=ProjectCreate(
            title=project_title,
            description="AI-generated execution workflow project",
            deadline=deadline,
            milestones=[
                MilestoneCreate(title="Draft outline and resources", due_at=milestone_1_due, weight=2),
                MilestoneCreate(title="Complete first draft", due_at=milestone_2_due, weight=3),
                MilestoneCreate(title="Review and final submission", due_at=deadline, weight=5),
            ],
            phases=[
                ExecutionPhaseCreate(name="Planning", sequence_index=1, start_at=now, end_at=milestone_1_due),
                ExecutionPhaseCreate(name="Execution", sequence_index=2, start_at=milestone_1_due, end_at=milestone_2_due),
                ExecutionPhaseCreate(name="Finalization", sequence_index=3, start_at=milestone_2_due, end_at=deadline),
            ],
            mode_id=workflow_mode_id,
        ),
        auto_commit=False,
    )

    goal = Goal(
        user_id=user_id,
        mode_id=workflow_mode_id,
        project_id=project.id,
        title=f"Complete {project_title}",
        description="AI-generated execution goal",
        target_date=deadline,
    )
    db.add(goal)
    flush_or_rollback(db)

    task = create_task(
        db,
        user_id=user_id,
        mode_id=workflow_mode_id,
        payload=TaskCreate(
            title=f"Execute project: {project_title}",
            due_at=deadline,
            mode_id=workflow_mode_id,
            project_id=project.id,
            priority="high",
            subtasks=[
                SubtaskCreate(title="Prepare structure and references", due_at=milestone_1_due),
                SubtaskCreate(title="Write complete draft", due_at=milestone_2_due),
                SubtaskCreate(title="Edit, proofread, and submit", due_at=deadline),
            ],
        ),
        auto_commit=False,
    )

    reminder_ids: list[int] = []
    for offset_hours in (24, 72):
        reminder_time = max(now + timedelta(hours=2), deadline - timedelta(hours=offset_hours))
        reminder = create_reminder(
            db,
            user_id=user_id,
            mode_id=workflow_mode_id,
            payload=ReminderCreate(
                task_id=task.id,
                remind_at=reminder_time,
                mode_id=workflow_mode_id,
            ),
            auto_commit=False,
        )
        reminder_ids.append(reminder.id)

    schedule_ids: list[int] = []
    block_start = now + timedelta(hours=1)
    for index in range(3):
        schedule = create_schedule(
            db,
            user_id=user_id,
            mode_id=workflow_mode_id,
            payload=ScheduleCreate(
                title=f"Focus Block {index + 1}: {project_title}",
                start_at=block_start + timedelta(days=index),
                end_at=block_start + timedelta(days=index, hours=2),
                linked_task_id=task.id,
                mode_id=workflow_mode_id,
            ),
            auto_commit=False,
        )
        schedule_ids.append(schedule.id)

    refresh_project_progress(db, project.id, user_id)
    if auto_commit:
        commit_or_rollback(db)
        db.refresh(project)
        db.refresh(goal)
    else:
        flush_or_rollback(db)
    return project, goal, task.id if task else None, reminder_ids, schedule_ids
