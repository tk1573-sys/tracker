from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import utcnow


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    mode_id: Mapped[int] = mapped_column(ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False, index=True)
    remind_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(30), nullable=False, default="in_app")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class FollowUpRule(Base):
    __tablename__ = "follow_up_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mode_id: Mapped[int] = mapped_column(ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False, index=True)
    trigger_type: Mapped[str] = mapped_column(String(30), nullable=False, default="task_overdue")
    delay_minutes: Mapped[int] = mapped_column(nullable=False, default=60)
    max_retries: Mapped[int] = mapped_column(nullable=False, default=3)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reminder_id: Mapped[int | None] = mapped_column(ForeignKey("reminders.id", ondelete="SET NULL"), nullable=True, index=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    retry_count: Mapped[int] = mapped_column(nullable=False, default=0)
