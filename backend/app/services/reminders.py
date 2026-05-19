from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.reminder import FollowUp, FollowUpRule, Reminder
from app.models.task import Task
from app.schemas.reminder import ReminderCreate


def create_default_follow_up_rule(db: Session, user_id: int, mode_id: int) -> FollowUpRule:
    existing = db.scalar(
        select(FollowUpRule).where(
            FollowUpRule.user_id == user_id,
            FollowUpRule.mode_id == mode_id,
            FollowUpRule.trigger_type == "task_overdue",
        )
    )
    if existing:
        return existing

    rule = FollowUpRule(
        user_id=user_id,
        mode_id=mode_id,
        trigger_type="task_overdue",
        delay_minutes=60,
        max_retries=3,
        active=True,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def create_reminder(
    db: Session,
    user_id: int,
    payload: ReminderCreate,
    mode_id: int,
    *,
    auto_commit: bool = True,
) -> Reminder:
    reminder = Reminder(
        user_id=user_id,
        task_id=payload.task_id,
        mode_id=payload.mode_id or mode_id,
        remind_at=payload.remind_at,
        channel=payload.channel,
    )
    db.add(reminder)
    if auto_commit:
        db.commit()
        db.refresh(reminder)
    else:
        db.flush()
    return reminder


def list_reminders(db: Session, user_id: int, mode_id: int | None, include_all_modes: bool) -> list[Reminder]:
    stmt = select(Reminder).where(Reminder.user_id == user_id).order_by(Reminder.remind_at.asc())
    if not include_all_modes and mode_id is not None:
        stmt = stmt.where(Reminder.mode_id == mode_id)
    return db.scalars(stmt).all()


def process_due_reminders(db: Session, now: datetime | None = None) -> int:
    now = now or datetime.now(UTC)
    due = db.scalars(select(Reminder).where(and_(Reminder.status == "pending", Reminder.remind_at <= now))).all()
    for reminder in due:
        reminder.status = "sent"
        db.add(reminder)
    db.commit()
    return len(due)


def process_follow_ups(db: Session, now: datetime | None = None) -> int:
    now = now or datetime.now(UTC)
    count = 0

    overdue_tasks = db.scalars(
        select(Task).where(
            Task.status != "completed",
            Task.due_at.is_not(None),
            Task.due_at < now,
        )
    ).all()

    for task in overdue_tasks:
        rule = db.scalar(
            select(FollowUpRule).where(
                FollowUpRule.user_id == task.user_id,
                FollowUpRule.mode_id == task.mode_id,
                FollowUpRule.trigger_type == "task_overdue",
                FollowUpRule.active.is_(True),
            )
        )
        if not rule:
            continue

        existing_pending = db.scalar(
            select(FollowUp).where(
                FollowUp.task_id == task.id,
                FollowUp.status == "pending",
            )
        )
        if existing_pending:
            continue

        retry_count = db.scalar(
            select(FollowUp.retry_count)
            .where(FollowUp.task_id == task.id)
            .order_by(FollowUp.id.desc())
            .limit(1)
        )
        retry_count = retry_count or 0
        if retry_count >= rule.max_retries:
            continue

        backoff_minutes = rule.delay_minutes * (2 ** retry_count)
        follow_up = FollowUp(
            task_id=task.id,
            scheduled_at=now + timedelta(minutes=backoff_minutes),
            status="pending",
            retry_count=retry_count,
        )
        db.add(follow_up)
        count += 1

    db.commit()

    due_followups = db.scalars(select(FollowUp).where(FollowUp.status == "pending", FollowUp.scheduled_at <= now)).all()
    for follow_up in due_followups:
        follow_up.status = "sent"
        follow_up.sent_at = now
        follow_up.retry_count = follow_up.retry_count + 1
        db.add(follow_up)
    db.commit()
    return count + len(due_followups)
