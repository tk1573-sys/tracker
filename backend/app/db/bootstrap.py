"""Optional local bootstrap utility for development databases."""

from app.db.base import Base
from app.db.session import engine
from app.models import (  # noqa: F401
    goal,
    habit,
    health_entry,
    journal_entry,
    reminder,
    transaction,
    user,
)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
