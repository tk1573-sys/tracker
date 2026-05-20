from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.reminder import FollowUp, FollowUpRule, Reminder
from app.models.task import Task
from app.schemas.reminder import ReminderCreate
from app.services.common import commit_or_rollback, ensure_task_access, flush_or_rollback, resolve_mode_id, scoped_by_user_mode

MAX_FOLLOW_UP_DELAY_MINUTES = 48 * 60


def create_default_follow_up_rule(db: Session, user_id: int, mode_id: int, *, auto_commit: bool = True) -> FollowUpRule:
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
    if auto_commit:
        commit_or_rollback(db)
        db.refresh(rule)
    else:
        flush_or_rollback(db)
    return rule


def create_reminder(
    db: Session,
    user_id: int,
    payload: ReminderCreate,
    mode_id: int,
    *,
    auto_commit: bool = True,
) -> Reminder:
    resolved_mode_id = resolve_mode_id(db, user_id=user_id, requested_mode_id=payload.mode_id, fallback_mode_id=mode_id)
    if payload.task_id is not None:
        ensure_task_access(db, user_id=user_id, task_id=payload.task_id, mode_id=resolved_mode_id)

    reminder = Reminder(
        user_id=user_id,
        task_id=payload.task_id,
        mode_id=resolved_mode_id,
        remind_at=payload.remind_at,
        channel=payload.channel,
    )
    db.add(reminder)
    create_default_follow_up_rule(db, user_id=user_id, mode_id=resolved_mode_id, auto_commit=False)
    if auto_commit:
        commit_or_rollback(db)
        db.refresh(reminder)
    else:
        flush_or_rollback(db)
    return reminder


def list_reminders(db: Session, user_id: int, mode_id: int | None, include_all_modes: bool) -> list[Reminder]:
    stmt = select(Reminder).order_by(Reminder.remind_at.asc())
    stmt = scoped_by_user_mode(stmt, Reminder, user_id=user_id, mode_id=mode_id, include_all_modes=include_all_modes)
    return db.scalars(stmt).all()


def process_due_reminders(db: Session, now: datetime | None = None) -> int:
    now = now or datetime.now(UTC)
    due = db.scalars(select(Reminder).where(and_(Reminder.status == "pending", Reminder.remind_at <= now))).all()
    for reminder in due:
        reminder.status = "sent"
        db.add(reminder)
    if due:
        commit_or_rollback(db)
    return len(due)


def process_follow_ups(db: Session, now: datetime | None = None) -> int:
    now = now or datetime.now(UTC)
    created_count = 0
    rule_cache: dict[tuple[int, int], FollowUpRule | None] = {}

    overdue_tasks = db.scalars(
        select(Task).where(
            Task.status != "completed",
            Task.due_at.is_not(None),
            Task.due_at < now,
        )
    ).all()

    for task in overdue_tasks:
        rule_key = (task.user_id, task.mode_id)
        if rule_key not in rule_cache:
            rule_cache[rule_key] = db.scalar(
                select(FollowUpRule).where(
                    FollowUpRule.user_id == task.user_id,
                    FollowUpRule.mode_id == task.mode_id,
                    FollowUpRule.trigger_type == "task_overdue",
                    FollowUpRule.active.is_(True),
                )
            )
        rule = rule_cache[rule_key]
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

        backoff_minutes = min(rule.delay_minutes * (2**retry_count), MAX_FOLLOW_UP_DELAY_MINUTES)
        follow_up = FollowUp(
            task_id=task.id,
            scheduled_at=now + timedelta(minutes=backoff_minutes),
            status="pending",
            retry_count=retry_count,
        )
        db.add(follow_up)
        created_count += 1

    due_followups = db.scalars(select(FollowUp).where(FollowUp.status == "pending", FollowUp.scheduled_at <= now)).all()
    for follow_up in due_followups:
        follow_up.status = "sent"
        follow_up.sent_at = now
        follow_up.retry_count = follow_up.retry_count + 1
        db.add(follow_up)
    if created_count or due_followups:
        commit_or_rollback(db)
    return created_count + len(due_followups)
