from pydantic import BaseModel

from app.schemas.tracker import TrackerSummary


class DashboardToday(BaseModel):
    due_tasks: int
    overdue_tasks: int
    upcoming_reminders: int
    pending_follow_ups: int


class DashboardProductivity(BaseModel):
    completion_rate_today: float
    focus_blocks_today: int
    streak_days: int


class DashboardJournal(BaseModel):
    recent_mood_avg: float | None
    recent_entries: int


class DashboardResponse(BaseModel):
    mode_id: int
    today: DashboardToday
    productivity: DashboardProductivity
    journal: DashboardJournal
    trackers: TrackerSummary
