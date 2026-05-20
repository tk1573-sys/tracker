from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.execution import Milestone, Project
from app.models.reminder import Reminder
from app.models.schedule import Schedule
from app.models.task import Task
from app.schemas.command_center import (
    CommandCenterAISuggestion,
    CommandCenterDeadlineItem,
    CommandCenterFocusBlockItem,
    CommandCenterOverdueFocus,
    CommandCenterOverdueItem,
    CommandCenterPriorityTask,
    CommandCenterProductivitySummary,
    CommandCenterStreakSummary,
    CommandCenterTodayOverview,
)


def _completion_score(db: Session, *, user_id: int, mode_id: int, now: datetime) -> float:
    today = now.date()
    completed = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status == "completed",
            Task.completed_at.is_not(None),
            func.date(Task.completed_at) == today,
        )
    ) or 0
    assigned = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.due_at.is_not(None),
            func.date(Task.due_at) == today,
        )
    ) or 0
    return round((float(completed) / float(assigned) * 100.0), 2) if assigned else 0.0


def get_today_overview(db: Session, *, user_id: int, mode_id: int) -> CommandCenterTodayOverview:
    now = datetime.now(UTC)
    today = now.date()
    due_today = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status != "completed",
            Task.due_at.is_not(None),
            func.date(Task.due_at) == today,
        )
    ) or 0
    overdue = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status != "completed",
            Task.due_at.is_not(None),
            Task.due_at < now,
        )
    ) or 0
    reminders_today = db.scalar(
        select(func.count(Reminder.id)).where(
            Reminder.user_id == user_id,
            Reminder.mode_id == mode_id,
            Reminder.remind_at >= datetime.combine(today, datetime.min.time(), tzinfo=UTC),
            Reminder.remind_at <= datetime.combine(today, datetime.max.time(), tzinfo=UTC),
        )
    ) or 0
    focus_blocks = db.scalar(
        select(func.count(Schedule.id)).where(
            Schedule.user_id == user_id,
            Schedule.mode_id == mode_id,
            Schedule.start_at >= datetime.combine(today, datetime.min.time(), tzinfo=UTC),
            Schedule.start_at <= datetime.combine(today, datetime.max.time(), tzinfo=UTC),
        )
    ) or 0
    return CommandCenterTodayOverview(
        due_today=int(due_today),
        overdue=int(overdue),
        reminders_today=int(reminders_today),
        planned_focus_blocks=int(focus_blocks),
        completion_score=_completion_score(db, user_id=user_id, mode_id=mode_id, now=now),
    )


def get_overdue_focus(db: Session, *, user_id: int, mode_id: int, limit: int = 5) -> CommandCenterOverdueFocus:
    now = datetime.now(UTC)
    overdue_tasks = db.scalars(
        select(Task)
        .where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status != "completed",
            Task.due_at.is_not(None),
            Task.due_at < now,
        )
        .order_by(Task.due_at.asc())
        .limit(limit)
    ).all()
    items = [
        CommandCenterOverdueItem(
            task_id=task.id,
            title=task.title,
            priority=task.priority,
            overdue_hours=round(max((now - task.due_at).total_seconds(), 0.0) / 3600.0, 2) if task.due_at else 0.0,
            recovery_recommended=bool(task.due_at and (now - task.due_at) >= timedelta(hours=24)),
        )
        for task in overdue_tasks
    ]
    total = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status != "completed",
            Task.due_at.is_not(None),
            Task.due_at < now,
        )
    ) or 0
    return CommandCenterOverdueFocus(total_overdue=int(total), items=items)


def get_priority_tasks(db: Session, *, user_id: int, mode_id: int, limit: int = 10) -> list[CommandCenterPriorityTask]:
    tasks = db.scalars(
        select(Task)
        .where(Task.user_id == user_id, Task.mode_id == mode_id, Task.status != "completed")
        .order_by(
            (Task.priority == "high").desc(),
            (Task.priority == "medium").desc(),
            Task.due_at.asc().nulls_last(),
            Task.created_at.asc(),
        )
        .limit(limit)
    ).all()
    return [
        CommandCenterPriorityTask(task_id=task.id, title=task.title, priority=task.priority, due_at=task.due_at)
        for task in tasks
    ]


def get_ai_suggestions(db: Session, *, user_id: int, mode_id: int) -> list[CommandCenterAISuggestion]:
    now = datetime.now(UTC)
    suggestions: list[CommandCenterAISuggestion] = []
    overdue_count = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status != "completed",
            Task.due_at.is_not(None),
            Task.due_at < now,
        )
    ) or 0
    high_priority_due_soon = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status != "completed",
            Task.priority == "high",
            Task.due_at.is_not(None),
            Task.due_at <= now + timedelta(hours=24),
        )
    ) or 0

    if overdue_count:
        suggestions.append(
            CommandCenterAISuggestion(
                suggestion="Run missed-task recovery flow for overdue items",
                reason=f"{int(overdue_count)} task(s) are overdue",
                priority="high",
            )
        )
    if high_priority_due_soon:
        suggestions.append(
            CommandCenterAISuggestion(
                suggestion="Create additional focus block for high-priority tasks",
                reason=f"{int(high_priority_due_soon)} high-priority task(s) due in 24h",
                priority="high",
            )
        )
    if not suggestions:
        suggestions.append(
            CommandCenterAISuggestion(
                suggestion="Maintain momentum with one deep-work focus block",
                reason="Execution flow is stable today",
                priority="medium",
            )
        )
    return suggestions


def get_productivity_summary(db: Session, *, user_id: int, mode_id: int) -> CommandCenterProductivitySummary:
    now = datetime.now(UTC)
    completion_scoring = _completion_score(db, user_id=user_id, mode_id=mode_id, now=now)
    recent_window_start = now - timedelta(days=7)
    completed_7d = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status == "completed",
            Task.completed_at.is_not(None),
            Task.completed_at >= recent_window_start,
        )
    ) or 0
    focus_blocks_7d = db.scalar(
        select(func.count(Schedule.id)).where(
            Schedule.user_id == user_id,
            Schedule.mode_id == mode_id,
            Schedule.start_at >= recent_window_start,
        )
    ) or 0
    due_7d = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.due_at.is_not(None),
            Task.due_at >= recent_window_start,
            Task.due_at <= now,
        )
    ) or 0

    focus_scoring = round(min(float(focus_blocks_7d) * 12.5, 100.0), 2)
    consistency_metric = round((float(completed_7d) / float(due_7d) * 100.0), 2) if due_7d else completion_scoring
    execution_velocity = round(float(completed_7d) / 7.0, 2)
    burnout_risk = "low"
    if focus_blocks_7d >= 18 and completion_scoring < 40:
        burnout_risk = "high"
    elif focus_blocks_7d >= 12 and completion_scoring < 60:
        burnout_risk = "medium"

    return CommandCenterProductivitySummary(
        completion_scoring=completion_scoring,
        focus_scoring=focus_scoring,
        consistency_metric=consistency_metric,
        execution_velocity=execution_velocity,
        burnout_risk=burnout_risk,
    )


def get_streak_summary(db: Session, *, user_id: int, mode_id: int) -> CommandCenterStreakSummary:
    today = datetime.now(UTC).date()
    completed_dates = [
        datetime.fromisoformat(str(value)).date()
        for value in db.scalars(
            select(func.date(Task.completed_at))
            .where(
                Task.user_id == user_id,
                Task.mode_id == mode_id,
                Task.status == "completed",
                Task.completed_at.is_not(None),
            )
            .group_by(func.date(Task.completed_at))
            .order_by(func.date(Task.completed_at).desc())
        ).all()
    ]
    current = 0
    cursor = today
    for completed_day in completed_dates:
        if completed_day != cursor:
            break
        current += 1
        cursor = cursor.fromordinal(cursor.toordinal() - 1)

    longest = 0
    running = 0
    previous = None
    for completed_day in sorted(completed_dates):
        if previous and completed_day.toordinal() == previous.toordinal() + 1:
            running += 1
        else:
            running = 1
        longest = max(longest, running)
        previous = completed_day
    return CommandCenterStreakSummary(
        current_streak_days=current,
        longest_streak_days=longest,
        active_today=today in completed_dates,
    )


def get_upcoming_deadlines(db: Session, *, user_id: int, mode_id: int, days: int = 7) -> list[CommandCenterDeadlineItem]:
    now = datetime.now(UTC)
    horizon = now + timedelta(days=days)
    tasks = db.scalars(
        select(Task).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status != "completed",
            Task.due_at.is_not(None),
            Task.due_at >= now,
            Task.due_at <= horizon,
        )
    ).all()
    milestones = db.scalars(
        select(Milestone)
        .join(Milestone.project)
        .where(
            Project.user_id == user_id,
            Project.mode_id == mode_id,
            Milestone.status != "completed",
            Milestone.due_at.is_not(None),
            Milestone.due_at >= now,
            Milestone.due_at <= horizon,
        )
    ).all()
    items = [
        CommandCenterDeadlineItem(
            entity_type="task",
            entity_id=task.id,
            title=task.title,
            due_at=task.due_at,
            priority=task.priority,
        )
        for task in tasks
        if task.due_at is not None
    ]
    items.extend(
        CommandCenterDeadlineItem(
            entity_type="milestone",
            entity_id=milestone.id,
            title=milestone.title,
            due_at=milestone.due_at,
            priority="high" if milestone.weight >= 3 else "medium",
        )
        for milestone in milestones
        if milestone.due_at is not None
    )
    return sorted(items, key=lambda item: item.due_at)


def get_focus_blocks(db: Session, *, user_id: int, mode_id: int) -> list[CommandCenterFocusBlockItem]:
    today = datetime.now(UTC).date()
    blocks = db.scalars(
        select(Schedule).where(
            Schedule.user_id == user_id,
            Schedule.mode_id == mode_id,
            Schedule.start_at >= datetime.combine(today, datetime.min.time(), tzinfo=UTC),
            Schedule.start_at <= datetime.combine(today, datetime.max.time(), tzinfo=UTC),
        )
    ).all()
    return [
        CommandCenterFocusBlockItem(
            schedule_id=block.id,
            title=block.title,
            start_at=block.start_at,
            end_at=block.end_at,
            linked_task_id=block.linked_task_id,
        )
        for block in sorted(blocks, key=lambda item: item.start_at)
    ]
