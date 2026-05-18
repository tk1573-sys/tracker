from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLEnum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GoalStatus(str, Enum):
    active = "active"
    completed = "completed"
    paused = "paused"
    cancelled = "cancelled"


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(140), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    current_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    status: Mapped[GoalStatus] = mapped_column(SQLEnum(GoalStatus), nullable=False, default=GoalStatus.active, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False
    )
