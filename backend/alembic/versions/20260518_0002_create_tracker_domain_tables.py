"""create tracker domain tables

Revision ID: 20260518_0002
Revises: 20260518_0001
Create Date: 2026-05-18 00:15:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260518_0002"
down_revision = "20260518_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_categories_id", "categories", ["id"], unique=False)
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)

    op.create_table(
        "payment_methods",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_payment_methods_id", "payment_methods", ["id"], unique=False)
    op.create_index("ix_payment_methods_name", "payment_methods", ["name"], unique=True)

    op.create_table(
        "habits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_habits_id", "habits", ["id"], unique=False)
    op.create_index("ix_habits_name", "habits", ["name"], unique=True)

    op.create_table(
        "resolutions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("metric_target", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("current_value", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_resolutions_id", "resolutions", ["id"], unique=False)
    op.create_index("ix_resolutions_status", "resolutions", ["status"], unique=False)
    op.create_index("ix_resolutions_start_date", "resolutions", ["start_date"], unique=False)
    op.create_index("ix_resolutions_target_date", "resolutions", ["target_date"], unique=False)
    op.create_index("ix_resolutions_title", "resolutions", ["title"], unique=False)

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("entry", sa.Text(), nullable=False),
        sa.Column("mood", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_journal_entries_id", "journal_entries", ["id"], unique=False)
    op.create_index("ix_journal_entries_entry_date", "journal_entries", ["entry_date"], unique=False)

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("transaction_type", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("payment_method_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["payment_method_id"], ["payment_methods.id"]),
    )
    op.create_index("ix_transactions_id", "transactions", ["id"], unique=False)
    op.create_index("ix_transactions_transaction_date", "transactions", ["transaction_date"], unique=False)
    op.create_index("ix_transactions_transaction_type", "transactions", ["transaction_type"], unique=False)
    op.create_index("ix_transactions_category_id", "transactions", ["category_id"], unique=False)
    op.create_index("ix_transactions_payment_method_id", "transactions", ["payment_method_id"], unique=False)

    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("monthly_budget", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.UniqueConstraint("category_id"),
    )
    op.create_index("ix_budgets_id", "budgets", ["id"], unique=False)
    op.create_index("ix_budgets_category_id", "budgets", ["category_id"], unique=True)

    op.create_table(
        "habit_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("habit_id", sa.Integer(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("done", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["habit_id"], ["habits.id"]),
        sa.UniqueConstraint("habit_id", "entry_date", name="uq_habit_entries_habit_date"),
    )
    op.create_index("ix_habit_entries_id", "habit_entries", ["id"], unique=False)
    op.create_index("ix_habit_entries_habit_id", "habit_entries", ["habit_id"], unique=False)
    op.create_index("ix_habit_entries_entry_date", "habit_entries", ["entry_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_habit_entries_entry_date", table_name="habit_entries")
    op.drop_index("ix_habit_entries_habit_id", table_name="habit_entries")
    op.drop_index("ix_habit_entries_id", table_name="habit_entries")
    op.drop_table("habit_entries")

    op.drop_index("ix_budgets_category_id", table_name="budgets")
    op.drop_index("ix_budgets_id", table_name="budgets")
    op.drop_table("budgets")

    op.drop_index("ix_transactions_payment_method_id", table_name="transactions")
    op.drop_index("ix_transactions_category_id", table_name="transactions")
    op.drop_index("ix_transactions_transaction_type", table_name="transactions")
    op.drop_index("ix_transactions_transaction_date", table_name="transactions")
    op.drop_index("ix_transactions_id", table_name="transactions")
    op.drop_table("transactions")

    op.drop_index("ix_journal_entries_entry_date", table_name="journal_entries")
    op.drop_index("ix_journal_entries_id", table_name="journal_entries")
    op.drop_table("journal_entries")

    op.drop_index("ix_resolutions_title", table_name="resolutions")
    op.drop_index("ix_resolutions_target_date", table_name="resolutions")
    op.drop_index("ix_resolutions_start_date", table_name="resolutions")
    op.drop_index("ix_resolutions_status", table_name="resolutions")
    op.drop_index("ix_resolutions_id", table_name="resolutions")
    op.drop_table("resolutions")

    op.drop_index("ix_habits_name", table_name="habits")
    op.drop_index("ix_habits_id", table_name="habits")
    op.drop_table("habits")

    op.drop_index("ix_payment_methods_name", table_name="payment_methods")
    op.drop_index("ix_payment_methods_id", table_name="payment_methods")
    op.drop_table("payment_methods")

    op.drop_index("ix_categories_name", table_name="categories")
    op.drop_index("ix_categories_id", table_name="categories")
    op.drop_table("categories")
