import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.ai import AIAction, AIMessage
from app.models.user import User
from app.schemas.ai import AIParsedIntent
from app.schemas.reminder import ReminderCreate
from app.schemas.task import TaskCreate
from app.services.common import commit_or_rollback, flush_or_rollback, resolve_mode_id
from app.services.reminders import create_reminder
from app.services.tasks import create_task

logger = get_logger(__name__)

REMINDER_COMMAND_PATTERN = re.compile(r"^remind me\s+(?P<when>.+?)\s+to\s+(?P<title>.+)$", re.IGNORECASE)
TASK_COMMAND_PATTERN = re.compile(r"^(?:create|add)(?:\s+a)?\s+task(?:\s+to)?\s+(?P<title>.+)$", re.IGNORECASE)
RELATIVE_TIME_PATTERN = re.compile(r"^in\s+(?P<amount>\d+)\s+(?P<unit>minute|minutes|hour|hours)$", re.IGNORECASE)
DAY_TIME_PATTERN = re.compile(
    r"^(?P<day>today|tomorrow)(?:\s+at\s+(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<suffix>am|pm)?)?$",
    re.IGNORECASE,
)
DATE_TIME_PATTERN = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})(?:\s+at\s+(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<suffix>am|pm)?)?$",
    re.IGNORECASE,
)


class AIProviderAdapter:
    def parse(self, text: str, now: datetime) -> AIParsedIntent:
        raise NotImplementedError


@dataclass
class RuleBasedAIProvider(AIProviderAdapter):
    def parse(self, text: str, now: datetime) -> AIParsedIntent:
        normalized = text.strip()
        if not normalized:
            return AIParsedIntent(
                intent="unknown",
                confidence=0.0,
                needs_clarification=True,
                clarification_message="Please enter a command.",
            )

        remind_match = REMINDER_COMMAND_PATTERN.search(normalized)
        if remind_match:
            when_text = remind_match.group("when").strip()
            title = remind_match.group("title").strip().rstrip(".")
            if not title:
                return AIParsedIntent(
                    intent="create_task_with_reminder",
                    confidence=0.5,
                    needs_clarification=True,
                    clarification_message="Please include what I should remind you about.",
                )
            remind_at = _parse_time_phrase(when_text, now)
            if remind_at is None:
                return AIParsedIntent(
                    intent="create_task_with_reminder",
                    title=title,
                    confidence=0.65,
                    needs_clarification=True,
                    clarification_message="I understood the task, but not the reminder time.",
                )
            return AIParsedIntent(
                intent="create_task_with_reminder",
                title=title,
                remind_at=remind_at,
                due_at=remind_at,
                confidence=0.9,
            )

        task_match = TASK_COMMAND_PATTERN.search(normalized)
        if task_match:
            return AIParsedIntent(
                intent="create_task",
                title=task_match.group("title").strip().rstrip("."),
                confidence=0.8,
            )

        return AIParsedIntent(
            intent="unknown",
            confidence=0.4,
            needs_clarification=True,
            clarification_message="I can help create tasks and reminders. Please use 'remind me ... to ...'.",
        )


def _apply_time(hour: int, minute: int, suffix: str | None) -> tuple[int, int]:
    normalized_hour = hour
    if suffix == "pm" and normalized_hour < 12:
        normalized_hour += 12
    if suffix == "am" and normalized_hour == 12:
        normalized_hour = 0
    if normalized_hour > 23 or minute > 59:
        raise ValueError("Invalid time")
    return normalized_hour, minute


def _parse_time_phrase(value: str, now: datetime) -> datetime | None:
    text = value.strip().lower()

    relative_match = RELATIVE_TIME_PATTERN.search(text)
    if relative_match:
        amount = int(relative_match.group("amount"))
        unit = relative_match.group("unit")
        delta = timedelta(hours=amount) if "hour" in unit else timedelta(minutes=amount)
        return now + delta

    day_match = DAY_TIME_PATTERN.search(text)
    if day_match:
        day_offset = 1 if day_match.group("day").lower() == "tomorrow" else 0
        target_day = now + timedelta(days=day_offset)
        hour = int(day_match.group("hour") or 9)
        minute = int(day_match.group("minute") or 0)
        try:
            hour, minute = _apply_time(hour, minute, day_match.group("suffix"))
        except ValueError:
            return None
        parsed = datetime(target_day.year, target_day.month, target_day.day, hour, minute, tzinfo=UTC)
        return parsed if parsed > now else None

    date_match = DATE_TIME_PATTERN.search(text)
    if date_match:
        parsed_date = datetime.strptime(date_match.group("date"), "%Y-%m-%d")
        hour = int(date_match.group("hour") or 9)
        minute = int(date_match.group("minute") or 0)
        try:
            hour, minute = _apply_time(hour, minute, date_match.group("suffix"))
        except ValueError:
            return None
        parsed = datetime(parsed_date.year, parsed_date.month, parsed_date.day, hour, minute, tzinfo=UTC)
        return parsed if parsed > now else None

    return None


def execute_ai_command(
    db: Session,
    *,
    user: User,
    mode_id: int,
    message: str,
    provider: AIProviderAdapter | None = None,
) -> tuple[AIParsedIntent, object | None, object | None]:
    now = datetime.now(UTC)
    parser = provider or RuleBasedAIProvider()
    parsed = parser.parse(message, now)
    resolved_mode_id = resolve_mode_id(db, user_id=user.id, requested_mode_id=mode_id, fallback_mode_id=mode_id)

    ai_message = AIMessage(user_id=user.id, mode_id=resolved_mode_id, role="user", content=message)
    db.add(ai_message)
    flush_or_rollback(db)

    created_task = None
    created_reminder = None

    try:
        if not parsed.needs_clarification and parsed.intent in {"create_task", "create_task_with_reminder"} and parsed.title:
            created_task = create_task(
                db,
                user_id=user.id,
                mode_id=resolved_mode_id,
                payload=TaskCreate(title=parsed.title, due_at=parsed.due_at, mode_id=resolved_mode_id),
                auto_commit=False,
            )
            if parsed.intent == "create_task_with_reminder" and parsed.remind_at:
                created_reminder = create_reminder(
                    db,
                    user_id=user.id,
                    mode_id=resolved_mode_id,
                    payload=ReminderCreate(task_id=created_task.id, remind_at=parsed.remind_at, mode_id=resolved_mode_id),
                    auto_commit=False,
                )

        action = AIAction(
            user_id=user.id,
            ai_message_id=ai_message.id,
            intent=parsed.intent,
            payload=json.dumps(parsed.model_dump(mode="json")),
            created_entity_refs=json.dumps(
                {
                    "task_id": getattr(created_task, "id", None),
                    "reminder_id": getattr(created_reminder, "id", None),
                }
            ),
            confidence=parsed.confidence,
        )
        db.add(action)
        commit_or_rollback(db)
    except Exception:
        db.rollback()
        logger.exception(
            "ai_command_failed",
            extra={"event": "ai_command_failed", "user_id": user.id, "mode_id": resolved_mode_id, "intent": parsed.intent},
        )
        raise

    if created_task is not None:
        db.refresh(created_task)
    if created_reminder is not None:
        db.refresh(created_reminder)

    logger.info(
        "ai_command_processed",
        extra={
            "event": "ai_command_processed",
            "user_id": user.id,
            "mode_id": resolved_mode_id,
            "intent": parsed.intent,
            "needs_clarification": parsed.needs_clarification,
        },
    )
    return parsed, created_task, created_reminder
