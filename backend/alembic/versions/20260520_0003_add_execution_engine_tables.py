"""add execution engine tables

Revision ID: 20260520_0003
Revises: 20260519_0002
Create Date: 2026-05-20 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260520_0003"
down_revision = "20260519_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="active"),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completion_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_projects_id", "projects", ["id"], unique=False)
    op.create_index("ix_projects_user_id", "projects", ["user_id"], unique=False)
    op.create_index("ix_projects_mode_id", "projects", ["mode_id"], unique=False)

    op.create_table(
        "goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mode_id", sa.Integer(), sa.ForeignKey("modes.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="active"),
        sa.Column("target_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("progress_percent", sa.Float(), nullable=False, server_default="0"),
        sa.Column("completion_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_goals_id", "goals", ["id"], unique=False)
    op.create_index("ix_goals_user_id", "goals", ["user_id"], unique=False)
    op.create_index("ix_goals_mode_id", "goals", ["mode_id"], unique=False)
    op.create_index("ix_goals_project_id", "goals", ["project_id"], unique=False)

    op.create_table(
        "milestones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("weight", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("completion_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_milestones_id", "milestones", ["id"], unique=False)
    op.create_index("ix_milestones_project_id", "milestones", ["project_id"], unique=False)

    op.create_table(
        "execution_phases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("sequence_index", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("progress_percent", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_index("ix_execution_phases_id", "execution_phases", ["id"], unique=False)
    op.create_index("ix_execution_phases_project_id", "execution_phases", ["project_id"], unique=False)

    op.add_column("tasks", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_tasks_project_id_projects",
        "tasks",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_tasks_project_id", "tasks", ["project_id"], unique=False)

    op.add_column("follow_ups", sa.Column("escalation_level", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("follow_ups", sa.Column("priority", sa.String(length=30), nullable=False, server_default="medium"))
    op.add_column("follow_ups", sa.Column("reason", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("follow_ups", "reason")
    op.drop_column("follow_ups", "priority")
    op.drop_column("follow_ups", "escalation_level")

    op.drop_index("ix_tasks_project_id", table_name="tasks")
    op.drop_constraint("fk_tasks_project_id_projects", "tasks", type_="foreignkey")
    op.drop_column("tasks", "project_id")

    op.drop_index("ix_execution_phases_project_id", table_name="execution_phases")
    op.drop_index("ix_execution_phases_id", table_name="execution_phases")
    op.drop_table("execution_phases")

    op.drop_index("ix_milestones_project_id", table_name="milestones")
    op.drop_index("ix_milestones_id", table_name="milestones")
    op.drop_table("milestones")

    op.drop_index("ix_goals_project_id", table_name="goals")
    op.drop_index("ix_goals_mode_id", table_name="goals")
    op.drop_index("ix_goals_user_id", table_name="goals")
    op.drop_index("ix_goals_id", table_name="goals")
    op.drop_table("goals")

    op.drop_index("ix_projects_mode_id", table_name="projects")
    op.drop_index("ix_projects_user_id", table_name="projects")
    op.drop_index("ix_projects_id", table_name="projects")
    op.drop_table("projects")
