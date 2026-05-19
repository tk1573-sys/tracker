"""Optional local bootstrap utility for development databases."""

from app.db.base import Base
from app.db.session import engine
from app.models import (  # noqa: F401
    AIAction,
    AIMessage,
    AnalyticsSnapshot,
    Category,
    FinanceRecord,
    FollowUp,
    FollowUpRule,
    Habit,
    HabitLog,
    HealthRecord,
    JournalEntry,
    Mode,
    Reminder,
    Schedule,
    Subtask,
    Task,
    User,
)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
