from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CSVBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)


class TransactionCSVRow(CSVBaseModel):
    date: date_type = Field(alias="Date")
    category: str = Field(alias="Category", min_length=1)
    amount: Decimal = Field(alias="Amount")
    transaction_type: str = Field(alias="Type", min_length=1)
    payment_method: str | None = Field(alias="Payment Method", default=None)
    notes: str | None = Field(alias="Notes", default=None)


class HabitCSVRow(CSVBaseModel):
    date: date_type = Field(alias="Date")
    habit: str = Field(alias="Habit", min_length=1)
    done: str = Field(alias="Done")
    notes: str | None = Field(alias="Notes", default=None)

    @field_validator("done")
    @classmethod
    def validate_done(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"yes", "no"}:
            raise ValueError("Done must be Yes or No")
        return normalized


class ResolutionCSVRow(CSVBaseModel):
    resolution: str = Field(alias="Resolution", min_length=1)
    start_date: date_type = Field(alias="StartDate")
    target_date: date_type = Field(alias="TargetDate")
    metric_target: Decimal = Field(alias="MetricTarget")
    current_value: Decimal = Field(alias="CurrentValue")
    status: str = Field(alias="Status", min_length=1)
    notes: str | None = Field(alias="Notes", default=None)


class BudgetCSVRow(CSVBaseModel):
    category: str = Field(alias="Category", min_length=1)
    monthly_budget: Decimal = Field(alias="MonthlyBudget")


class JournalCSVRow(CSVBaseModel):
    date: date_type = Field(alias="Date")
    title: str = Field(alias="Title", min_length=1)
    entry: str = Field(alias="Entry", min_length=1)
    mood: int | None = Field(alias="Mood", default=None)

    @field_validator("mood")
    @classmethod
    def validate_mood(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value < 1 or value > 5:
            raise ValueError("Mood must be between 1 and 5")
        return value
