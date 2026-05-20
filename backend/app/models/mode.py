from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Mode(Base):
    __tablename__ = "modes"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_modes_user_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user: Mapped["User"] = relationship(back_populates="modes")
    categories: Mapped[list["Category"]] = relationship(back_populates="mode")
    tasks: Mapped[list["Task"]] = relationship(back_populates="mode")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="mode")
    follow_up_rules: Mapped[list["FollowUpRule"]] = relationship(back_populates="mode")
    schedules: Mapped[list["Schedule"]] = relationship(back_populates="mode")
    journal_entries: Mapped[list["JournalEntry"]] = relationship(back_populates="mode")
    ai_messages: Mapped[list["AIMessage"]] = relationship(back_populates="mode")
    goals: Mapped[list["Goal"]] = relationship(back_populates="mode")
    projects: Mapped[list["Project"]] = relationship(back_populates="mode")
