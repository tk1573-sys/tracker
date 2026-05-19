from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry
from app.models.reminder import FollowUp, Reminder
from app.models.schedule import Schedule
from app.models.task import Task
from app.schemas.dashboard import DashboardJournal, DashboardProductivity, DashboardResponse, DashboardToday
from app.services.journal import get_recent_mood_average
from app.services.trackers import get_tracker_summary


def get_dashboard(db: Session, user_id: int, mode_id: int) -> DashboardResponse:
    now = datetime.now(UTC)
    today = now.date()

    due_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status != "completed",
            Task.due_at.is_not(None),
            func.date(Task.due_at) == today,
        )
    ) or 0

    overdue_tasks = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status != "completed",
            Task.due_at.is_not(None),
            Task.due_at < now,
        )
    ) or 0

    upcoming_reminders = db.scalar(
        select(func.count(Reminder.id)).where(
            Reminder.user_id == user_id,
            Reminder.mode_id == mode_id,
            Reminder.status == "pending",
            Reminder.remind_at >= now,
        )
    ) or 0

    pending_followups = db.scalar(
        select(func.count(FollowUp.id))
        .join(Task, Task.id == FollowUp.task_id, isouter=True)
        .where(
            FollowUp.status == "pending",
            or_(Task.user_id == user_id, FollowUp.task_id.is_(None)),
            or_(Task.mode_id == mode_id, FollowUp.task_id.is_(None)),
        )
    ) or 0

    completed_today = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.status == "completed",
            Task.completed_at.is_not(None),
            func.date(Task.completed_at) == today,
        )
    ) or 0

    total_today = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.mode_id == mode_id,
            Task.due_at.is_not(None),
            func.date(Task.due_at) == today,
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

    streak_days = 0
    day_cursor = today
    while True:
        has_completed = db.scalar(
            select(func.count(Task.id)).where(
                Task.user_id == user_id,
                Task.mode_id == mode_id,
                Task.status == "completed",
                Task.completed_at.is_not(None),
                func.date(Task.completed_at) == day_cursor,
            )
        )
        if not has_completed:
            break
        streak_days += 1
        day_cursor = day_cursor.fromordinal(day_cursor.toordinal() - 1)

    recent_entries = db.scalar(
        select(func.count(JournalEntry.id)).where(
            JournalEntry.user_id == user_id,
            JournalEntry.mode_id == mode_id,
        )
    ) or 0

    completion_rate = float(completed_today / total_today * 100) if total_today else 0.0

    return DashboardResponse(
        mode_id=mode_id,
        today=DashboardToday(
            due_tasks=int(due_tasks),
            overdue_tasks=int(overdue_tasks),
            upcoming_reminders=int(upcoming_reminders),
            pending_follow_ups=int(pending_followups),
        ),
        productivity=DashboardProductivity(
            completion_rate_today=round(completion_rate, 2),
            focus_blocks_today=int(focus_blocks),
            streak_days=streak_days,
        ),
        journal=DashboardJournal(
            recent_mood_avg=get_recent_mood_average(db, user_id=user_id, mode_id=mode_id),
            recent_entries=int(recent_entries),
        ),
        trackers=get_tracker_summary(db, user_id=user_id, mode_id=mode_id),
    )
