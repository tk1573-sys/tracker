from pydantic import BaseModel


class TrackerSummary(BaseModel):
    total_habits: int
    completed_habit_logs_today: int
    finance_income_month: float
    finance_expense_month: float
    avg_steps_7d: float | None
    avg_sleep_7d: float | None
