from datetime import datetime

from pydantic import BaseModel


class CommandCenterTodayOverview(BaseModel):
    due_today: int
    overdue: int
    reminders_today: int
    planned_focus_blocks: int
    completion_score: float


class CommandCenterOverdueItem(BaseModel):
    task_id: int
    title: str
    priority: str
    overdue_hours: float
    recovery_recommended: bool


class CommandCenterOverdueFocus(BaseModel):
    total_overdue: int
    items: list[CommandCenterOverdueItem]


class CommandCenterPriorityTask(BaseModel):
    task_id: int
    title: str
    priority: str
    due_at: datetime | None


class CommandCenterAISuggestion(BaseModel):
    suggestion: str
    reason: str
    priority: str


class CommandCenterProductivitySummary(BaseModel):
    completion_scoring: float
    focus_scoring: float
    consistency_metric: float
    execution_velocity: float
    burnout_risk: str


class CommandCenterStreakSummary(BaseModel):
    current_streak_days: int
    longest_streak_days: int
    active_today: bool


class CommandCenterDeadlineItem(BaseModel):
    entity_type: str
    entity_id: int
    title: str
    due_at: datetime
    priority: str


class CommandCenterFocusBlockItem(BaseModel):
    schedule_id: int
    title: str
    start_at: datetime
    end_at: datetime
    linked_task_id: int | None
