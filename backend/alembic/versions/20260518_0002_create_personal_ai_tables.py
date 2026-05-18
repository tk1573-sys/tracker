"""create personal ai life os tables

Revision ID: 20260518_0002
Revises: 20260518_0001
Create Date: 2026-05-18 11:35:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260518_0002"
down_revision = "20260518_0001"
branch_labels = None
depends_on = None

transaction_type_enum = sa.Enum("income", "expense", name="transactiontype")
habit_frequency_enum = sa.Enum("daily", "weekly", "monthly", name="habitfrequency")
goals_status_enum = sa.Enum("active", "completed", "paused", "cancelled", name="goalstatus")
reminder_priority_enum = sa.Enum("low", "medium", "high", name="reminderpriority")


def upgrade() -> None:
    bind = op.get_bind()
    transaction_type_enum.create(bind, checkfirst=True)
    habit_frequency_enum.create(bind, checkfirst=True)
    goals_status_enum.create(bind, checkfirst=True)
    reminder_priority_enum.create(bind, checkfirst=True)

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("type", transaction_type_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_transactions_id", "transactions", ["id"], unique=False)
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"], unique=False)
    op.create_index("ix_transactions_category", "transactions", ["category"], unique=False)
    op.create_index("ix_transactions_type", "transactions", ["type"], unique=False)
    op.create_index("ix_transactions_occurred_at", "transactions", ["occurred_at"], unique=False)

    op.create_table(
        "habits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("frequency", habit_frequency_enum, nullable=False),
        sa.Column("target_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_habits_id", "habits", ["id"], unique=False)
    op.create_index("ix_habits_user_id", "habits", ["user_id"], unique=False)
    op.create_index("ix_habits_name", "habits", ["name"], unique=False)
    op.create_index("ix_habits_frequency", "habits", ["frequency"], unique=False)

    op.create_table(
        "health_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric_type", sa.String(length=80), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=30), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_health_entries_id", "health_entries", ["id"], unique=False)
    op.create_index("ix_health_entries_user_id", "health_entries", ["user_id"], unique=False)
    op.create_index("ix_health_entries_metric_type", "health_entries", ["metric_type"], unique=False)
    op.create_index("ix_health_entries_recorded_at", "health_entries", ["recorded_at"], unique=False)

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("mood", sa.Integer(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_journal_entries_id", "journal_entries", ["id"], unique=False)
    op.create_index("ix_journal_entries_user_id", "journal_entries", ["user_id"], unique=False)
    op.create_index("ix_journal_entries_entry_date", "journal_entries", ["entry_date"], unique=False)

    op.create_table(
        "goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("current_value", sa.Numeric(12, 2), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", goals_status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_goals_id", "goals", ["id"], unique=False)
    op.create_index("ix_goals_user_id", "goals", ["user_id"], unique=False)
    op.create_index("ix_goals_title", "goals", ["title"], unique=False)
    op.create_index("ix_goals_status", "goals", ["status"], unique=False)
    op.create_index("ix_goals_due_date", "goals", ["due_date"], unique=False)

    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("priority", reminder_priority_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reminders_id", "reminders", ["id"], unique=False)
    op.create_index("ix_reminders_user_id", "reminders", ["user_id"], unique=False)
    op.create_index("ix_reminders_is_completed", "reminders", ["is_completed"], unique=False)
    op.create_index("ix_reminders_remind_at", "reminders", ["remind_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_reminders_remind_at", table_name="reminders")
    op.drop_index("ix_reminders_is_completed", table_name="reminders")
    op.drop_index("ix_reminders_user_id", table_name="reminders")
    op.drop_index("ix_reminders_id", table_name="reminders")
    op.drop_table("reminders")

    op.drop_index("ix_goals_due_date", table_name="goals")
    op.drop_index("ix_goals_status", table_name="goals")
    op.drop_index("ix_goals_title", table_name="goals")
    op.drop_index("ix_goals_user_id", table_name="goals")
    op.drop_index("ix_goals_id", table_name="goals")
    op.drop_table("goals")

    op.drop_index("ix_journal_entries_entry_date", table_name="journal_entries")
    op.drop_index("ix_journal_entries_user_id", table_name="journal_entries")
    op.drop_index("ix_journal_entries_id", table_name="journal_entries")
    op.drop_table("journal_entries")

    op.drop_index("ix_health_entries_recorded_at", table_name="health_entries")
    op.drop_index("ix_health_entries_metric_type", table_name="health_entries")
    op.drop_index("ix_health_entries_user_id", table_name="health_entries")
    op.drop_index("ix_health_entries_id", table_name="health_entries")
    op.drop_table("health_entries")

    op.drop_index("ix_habits_frequency", table_name="habits")
    op.drop_index("ix_habits_name", table_name="habits")
    op.drop_index("ix_habits_user_id", table_name="habits")
    op.drop_index("ix_habits_id", table_name="habits")
    op.drop_table("habits")

    op.drop_index("ix_transactions_occurred_at", table_name="transactions")
    op.drop_index("ix_transactions_type", table_name="transactions")
    op.drop_index("ix_transactions_category", table_name="transactions")
    op.drop_index("ix_transactions_user_id", table_name="transactions")
    op.drop_index("ix_transactions_id", table_name="transactions")
    op.drop_table("transactions")

    bind = op.get_bind()
    reminder_priority_enum.drop(bind, checkfirst=True)
    goals_status_enum.drop(bind, checkfirst=True)
    habit_frequency_enum.drop(bind, checkfirst=True)
    transaction_type_enum.drop(bind, checkfirst=True)
