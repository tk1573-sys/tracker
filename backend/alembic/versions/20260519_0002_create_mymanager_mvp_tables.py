"""create mymanager mvp tables

Revision ID: 20260519_0002
Revises: 20260518_0001
Create Date: 2026-05-19 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260519_0002"
down_revision = "20260518_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "modes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("is_active_default", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.UniqueConstraint("user_id", "name", name="uq_modes_user_name"),
    )
    op.create_index("ix_modes_id", "modes", ["id"], unique=False)
    op.create_index("ix_modes_user_id", "modes", ["user_id"], unique=False)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.UniqueConstraint("user_id", "mode_id", "name", "type", name="uq_categories_scope"),
    )
    op.create_index("ix_categories_id", "categories", ["id"], unique=False)
    op.create_index("ix_categories_user_id", "categories", ["user_id"], unique=False)
    op.create_index("ix_categories_mode_id", "categories", ["mode_id"], unique=False)

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("priority", sa.String(length=30), nullable=False, server_default="medium"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tasks_id", "tasks", ["id"], unique=False)
    op.create_index("ix_tasks_user_id", "tasks", ["user_id"], unique=False)
    op.create_index("ix_tasks_mode_id", "tasks", ["mode_id"], unique=False)
    op.create_index("ix_tasks_category_id", "tasks", ["category_id"], unique=False)

    op.create_table(
        "subtasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_subtasks_id", "subtasks", ["id"], unique=False)
    op.create_index("ix_subtasks_task_id", "subtasks", ["task_id"], unique=False)

    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("channel", sa.String(length=30), nullable=False, server_default="in_app"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reminders_id", "reminders", ["id"], unique=False)
    op.create_index("ix_reminders_user_id", "reminders", ["user_id"], unique=False)
    op.create_index("ix_reminders_task_id", "reminders", ["task_id"], unique=False)
    op.create_index("ix_reminders_mode_id", "reminders", ["mode_id"], unique=False)
    op.create_index("ix_reminders_remind_at", "reminders", ["remind_at"], unique=False)

    op.create_table(
        "follow_up_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("trigger_type", sa.String(length=30), nullable=False, server_default="task_overdue"),
        sa.Column("delay_minutes", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )
    op.create_index("ix_follow_up_rules_id", "follow_up_rules", ["id"], unique=False)
    op.create_index("ix_follow_up_rules_user_id", "follow_up_rules", ["user_id"], unique=False)
    op.create_index("ix_follow_up_rules_mode_id", "follow_up_rules", ["mode_id"], unique=False)

    op.create_table(
        "follow_ups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reminder_id", sa.Integer(), sa.ForeignKey("reminders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_follow_ups_id", "follow_ups", ["id"], unique=False)
    op.create_index("ix_follow_ups_reminder_id", "follow_ups", ["reminder_id"], unique=False)
    op.create_index("ix_follow_ups_task_id", "follow_ups", ["task_id"], unique=False)
    op.create_index("ix_follow_ups_scheduled_at", "follow_ups", ["scheduled_at"], unique=False)

    op.create_table(
        "schedules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("linked_task_id", sa.Integer(), sa.ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_schedules_id", "schedules", ["id"], unique=False)
    op.create_index("ix_schedules_user_id", "schedules", ["user_id"], unique=False)
    op.create_index("ix_schedules_mode_id", "schedules", ["mode_id"], unique=False)
    op.create_index("ix_schedules_linked_task_id", "schedules", ["linked_task_id"], unique=False)

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("mood_score", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tags", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_journal_entries_id", "journal_entries", ["id"], unique=False)
    op.create_index("ix_journal_entries_user_id", "journal_entries", ["user_id"], unique=False)
    op.create_index("ix_journal_entries_mode_id", "journal_entries", ["mode_id"], unique=False)

    op.create_table(
        "habits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
    )
    op.create_index("ix_habits_id", "habits", ["id"], unique=False)
    op.create_index("ix_habits_user_id", "habits", ["user_id"], unique=False)
    op.create_index("ix_habits_mode_id", "habits", ["mode_id"], unique=False)

    op.create_table(
        "habit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("habit_id", sa.Integer(), sa.ForeignKey("habits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("log_date", sa.Date(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )
    op.create_index("ix_habit_logs_id", "habit_logs", ["id"], unique=False)
    op.create_index("ix_habit_logs_habit_id", "habit_logs", ["habit_id"], unique=False)
    op.create_index("ix_habit_logs_log_date", "habit_logs", ["log_date"], unique=False)

    op.create_table(
        "finance_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("record_type", sa.String(length=20), nullable=False, server_default="expense"),
        sa.Column("category", sa.String(length=100), nullable=True),
    )
    op.create_index("ix_finance_records_id", "finance_records", ["id"], unique=False)
    op.create_index("ix_finance_records_user_id", "finance_records", ["user_id"], unique=False)
    op.create_index("ix_finance_records_mode_id", "finance_records", ["mode_id"], unique=False)
    op.create_index("ix_finance_records_record_date", "finance_records", ["record_date"], unique=False)

    op.create_table(
        "health_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("steps", sa.Integer(), nullable=True),
        sa.Column("sleep_hours", sa.Float(), nullable=True),
        sa.Column("water_liters", sa.Float(), nullable=True),
        sa.Column("mood_score", sa.Integer(), nullable=True),
    )
    op.create_index("ix_health_records_id", "health_records", ["id"], unique=False)
    op.create_index("ix_health_records_user_id", "health_records", ["user_id"], unique=False)
    op.create_index("ix_health_records_mode_id", "health_records", ["mode_id"], unique=False)
    op.create_index("ix_health_records_record_date", "health_records", ["record_date"], unique=False)

    op.create_table(
        "analytics_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("metric_key", sa.String(length=100), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
    )
    op.create_index("ix_analytics_snapshots_id", "analytics_snapshots", ["id"], unique=False)
    op.create_index("ix_analytics_snapshots_user_id", "analytics_snapshots", ["user_id"], unique=False)
    op.create_index("ix_analytics_snapshots_mode_id", "analytics_snapshots", ["mode_id"], unique=False)

    op.create_table(
        "ai_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ai_messages_id", "ai_messages", ["id"], unique=False)
    op.create_index("ix_ai_messages_user_id", "ai_messages", ["user_id"], unique=False)
    op.create_index("ix_ai_messages_mode_id", "ai_messages", ["mode_id"], unique=False)

    op.create_table(
        "ai_actions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ai_message_id", sa.Integer(), sa.ForeignKey("ai_messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("intent", sa.String(length=50), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("created_entity_refs", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ai_actions_id", "ai_actions", ["id"], unique=False)
    op.create_index("ix_ai_actions_user_id", "ai_actions", ["user_id"], unique=False)
    op.create_index("ix_ai_actions_ai_message_id", "ai_actions", ["ai_message_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_actions_ai_message_id", table_name="ai_actions")
    op.drop_index("ix_ai_actions_user_id", table_name="ai_actions")
    op.drop_index("ix_ai_actions_id", table_name="ai_actions")
    op.drop_table("ai_actions")

    op.drop_index("ix_ai_messages_mode_id", table_name="ai_messages")
    op.drop_index("ix_ai_messages_user_id", table_name="ai_messages")
    op.drop_index("ix_ai_messages_id", table_name="ai_messages")
    op.drop_table("ai_messages")

    op.drop_index("ix_analytics_snapshots_mode_id", table_name="analytics_snapshots")
    op.drop_index("ix_analytics_snapshots_user_id", table_name="analytics_snapshots")
    op.drop_index("ix_analytics_snapshots_id", table_name="analytics_snapshots")
    op.drop_table("analytics_snapshots")

    op.drop_index("ix_health_records_record_date", table_name="health_records")
    op.drop_index("ix_health_records_mode_id", table_name="health_records")
    op.drop_index("ix_health_records_user_id", table_name="health_records")
    op.drop_index("ix_health_records_id", table_name="health_records")
    op.drop_table("health_records")

    op.drop_index("ix_finance_records_record_date", table_name="finance_records")
    op.drop_index("ix_finance_records_mode_id", table_name="finance_records")
    op.drop_index("ix_finance_records_user_id", table_name="finance_records")
    op.drop_index("ix_finance_records_id", table_name="finance_records")
    op.drop_table("finance_records")

    op.drop_index("ix_habit_logs_log_date", table_name="habit_logs")
    op.drop_index("ix_habit_logs_habit_id", table_name="habit_logs")
    op.drop_index("ix_habit_logs_id", table_name="habit_logs")
    op.drop_table("habit_logs")

    op.drop_index("ix_habits_mode_id", table_name="habits")
    op.drop_index("ix_habits_user_id", table_name="habits")
    op.drop_index("ix_habits_id", table_name="habits")
    op.drop_table("habits")

    op.drop_index("ix_journal_entries_mode_id", table_name="journal_entries")
    op.drop_index("ix_journal_entries_user_id", table_name="journal_entries")
    op.drop_index("ix_journal_entries_id", table_name="journal_entries")
    op.drop_table("journal_entries")

    op.drop_index("ix_schedules_linked_task_id", table_name="schedules")
    op.drop_index("ix_schedules_mode_id", table_name="schedules")
    op.drop_index("ix_schedules_user_id", table_name="schedules")
    op.drop_index("ix_schedules_id", table_name="schedules")
    op.drop_table("schedules")

    op.drop_index("ix_follow_ups_scheduled_at", table_name="follow_ups")
    op.drop_index("ix_follow_ups_task_id", table_name="follow_ups")
    op.drop_index("ix_follow_ups_reminder_id", table_name="follow_ups")
    op.drop_index("ix_follow_ups_id", table_name="follow_ups")
    op.drop_table("follow_ups")

    op.drop_index("ix_follow_up_rules_mode_id", table_name="follow_up_rules")
    op.drop_index("ix_follow_up_rules_user_id", table_name="follow_up_rules")
    op.drop_index("ix_follow_up_rules_id", table_name="follow_up_rules")
    op.drop_table("follow_up_rules")

    op.drop_index("ix_reminders_remind_at", table_name="reminders")
    op.drop_index("ix_reminders_mode_id", table_name="reminders")
    op.drop_index("ix_reminders_task_id", table_name="reminders")
    op.drop_index("ix_reminders_user_id", table_name="reminders")
    op.drop_index("ix_reminders_id", table_name="reminders")
    op.drop_table("reminders")

    op.drop_index("ix_subtasks_task_id", table_name="subtasks")
    op.drop_index("ix_subtasks_id", table_name="subtasks")
    op.drop_table("subtasks")

    op.drop_index("ix_tasks_category_id", table_name="tasks")
    op.drop_index("ix_tasks_mode_id", table_name="tasks")
    op.drop_index("ix_tasks_user_id", table_name="tasks")
    op.drop_index("ix_tasks_id", table_name="tasks")
    op.drop_table("tasks")

    op.drop_index("ix_categories_mode_id", table_name="categories")
    op.drop_index("ix_categories_user_id", table_name="categories")
    op.drop_index("ix_categories_id", table_name="categories")
    op.drop_table("categories")

    op.drop_index("ix_modes_user_id", table_name="modes")
    op.drop_index("ix_modes_id", table_name="modes")
    op.drop_table("modes")
