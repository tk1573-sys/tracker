import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.ai import AIAction, AIMessage
from app.models.user import User
from app.schemas.ai import AIParsedIntent
from app.schemas.reminder import ReminderCreate
from app.schemas.task import TaskCreate
from app.services.reminders import create_reminder
from app.services.tasks import create_task


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

        lowered = normalized.lower()
        if lowered.startswith("remind me "):
            remainder = normalized[10:].strip()
            marker = re.search(r"\s+to\s+", remainder, flags=re.IGNORECASE)
            if marker:
                when_text = remainder[: marker.start()].strip()
                title = remainder[marker.end():].strip().rstrip(".")
            else:
                when_text = ""
                title = ""

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

        task_match = re.search(r"(create|add)\s+(a\s+)?task\s+(to\s+)?(?P<title>.+)", normalized, flags=re.IGNORECASE)
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
            clarification_message="I can help create tasks/reminders. Please use 'remind me ... to ...'.",
        )


def _parse_time_phrase(value: str, now: datetime) -> datetime | None:
    text = value.strip().lower()
    tomorrow = now + timedelta(days=1)

    tomorrow_match = re.search(r"tomorrow(?:\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?)?", text)
    if tomorrow_match:
        hour = int(tomorrow_match.group(1) or 9)
        minute = int(tomorrow_match.group(2) or 0)
        suffix = tomorrow_match.group(3)
        if suffix == "pm" and hour < 12:
            hour += 12
        if suffix == "am" and hour == 12:
            hour = 0
        return datetime(tomorrow.year, tomorrow.month, tomorrow.day, hour, minute, tzinfo=UTC)

    iso_match = re.search(r"(\d{4}-\d{2}-\d{2})(?:\s+at\s+(\d{1,2}):(\d{2}))?", text)
    if iso_match:
        parsed_date = datetime.strptime(iso_match.group(1), "%Y-%m-%d")
        hour = int(iso_match.group(2) or 9)
        minute = int(iso_match.group(3) or 0)
        return datetime(parsed_date.year, parsed_date.month, parsed_date.day, hour, minute, tzinfo=UTC)

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

    ai_message = AIMessage(user_id=user.id, mode_id=mode_id, role="user", content=message)
    db.add(ai_message)
    db.flush()

    created_task = None
    created_reminder = None

    if not parsed.needs_clarification and parsed.intent in {"create_task", "create_task_with_reminder"} and parsed.title:
        created_task = create_task(
            db,
            user_id=user.id,
            mode_id=mode_id,
            payload=TaskCreate(title=parsed.title, due_at=parsed.due_at, mode_id=mode_id),
            auto_commit=False,
        )
        if parsed.intent == "create_task_with_reminder" and parsed.remind_at:
            created_reminder = create_reminder(
                db,
                user_id=user.id,
                mode_id=mode_id,
                payload=ReminderCreate(task_id=created_task.id, remind_at=parsed.remind_at, mode_id=mode_id),
                auto_commit=False,
            )

    action = AIAction(
        user_id=user.id,
        ai_message_id=ai_message.id,
        intent=parsed.intent,
        payload=json.dumps(parsed.model_dump(mode="json"), default=str),
        created_entity_refs=json.dumps(
            {
                "task_id": getattr(created_task, "id", None),
                "reminder_id": getattr(created_reminder, "id", None),
            }
        ),
        confidence=parsed.confidence,
    )
    db.add(action)
    db.commit()

    if created_task is not None:
        db.refresh(created_task)
    if created_reminder is not None:
        db.refresh(created_reminder)

    return parsed, created_task, created_reminder
