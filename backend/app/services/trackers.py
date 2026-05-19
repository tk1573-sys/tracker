from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.tracker import FinanceRecord, Habit, HabitLog, HealthRecord
from app.schemas.tracker import TrackerSummary


def get_tracker_summary(db: Session, user_id: int, mode_id: int) -> TrackerSummary:
    today = datetime.now(UTC).date()
    month_start = today.replace(day=1)
    week_start = today.fromordinal(today.toordinal() - 6)

    total_habits = db.scalar(select(func.count(Habit.id)).where(Habit.user_id == user_id, Habit.mode_id == mode_id)) or 0

    completed_habit_logs_today = db.scalar(
        select(func.count(HabitLog.id))
        .join(Habit, Habit.id == HabitLog.habit_id)
        .where(Habit.user_id == user_id, Habit.mode_id == mode_id, HabitLog.log_date == today, HabitLog.completed.is_(True))
    ) or 0

    income = db.scalar(
        select(func.coalesce(func.sum(FinanceRecord.amount), 0.0)).where(
            FinanceRecord.user_id == user_id,
            FinanceRecord.mode_id == mode_id,
            FinanceRecord.record_date >= month_start,
            FinanceRecord.record_type == "income",
        )
    ) or 0.0

    expense = db.scalar(
        select(func.coalesce(func.sum(FinanceRecord.amount), 0.0)).where(
            FinanceRecord.user_id == user_id,
            FinanceRecord.mode_id == mode_id,
            FinanceRecord.record_date >= month_start,
            FinanceRecord.record_type == "expense",
        )
    ) or 0.0

    avg_steps = db.scalar(
        select(func.avg(HealthRecord.steps)).where(
            HealthRecord.user_id == user_id,
            HealthRecord.mode_id == mode_id,
            HealthRecord.record_date >= week_start,
            HealthRecord.steps.is_not(None),
        )
    )

    avg_sleep = db.scalar(
        select(func.avg(HealthRecord.sleep_hours)).where(
            HealthRecord.user_id == user_id,
            HealthRecord.mode_id == mode_id,
            HealthRecord.record_date >= week_start,
            HealthRecord.sleep_hours.is_not(None),
        )
    )

    return TrackerSummary(
        total_habits=int(total_habits),
        completed_habit_logs_today=int(completed_habit_logs_today),
        finance_income_month=float(income),
        finance_expense_month=float(expense),
        avg_steps_7d=round(float(avg_steps), 2) if avg_steps is not None else None,
        avg_sleep_7d=round(float(avg_sleep), 2) if avg_sleep is not None else None,
    )
