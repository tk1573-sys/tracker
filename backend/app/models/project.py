from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import utcnow


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mode_id: Mapped[int] = mapped_column(ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    user: Mapped["User"] = relationship(back_populates="projects")
    mode: Mapped["Mode"] = relationship(back_populates="projects")
    phases: Mapped[list["ExecutionPhase"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    task_links: Mapped[list["ProjectTaskLink"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    goal_links: Mapped[list["ProjectGoalLink"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ExecutionPhase(Base):
    __tablename__ = "execution_phases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="phases")


class ProjectTaskLink(Base):
    __tablename__ = "project_task_links"
    __table_args__ = (UniqueConstraint("project_id", "task_id", name="uq_project_task_links"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)

    project: Mapped["Project"] = relationship(back_populates="task_links")
    task: Mapped["Task"] = relationship(back_populates="project_links")


class ProjectGoalLink(Base):
    __tablename__ = "project_goal_links"
    __table_args__ = (UniqueConstraint("project_id", "goal_id", name="uq_project_goal_links"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"), nullable=False, index=True)

    project: Mapped["Project"] = relationship(back_populates="goal_links")
    goal: Mapped["Goal"] = relationship(back_populates="project_links")
