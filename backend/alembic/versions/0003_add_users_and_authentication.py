"""Add users, roles, and team assignments tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="EMPLOYEE"),
        sa.Column("team", sa.String(100)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "role IN ('EMPLOYEE', 'MANAGER', 'ADMIN')",
            name="ck_users_role"
        ),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_role", "users", ["role"])

    op.create_table(
        "team_assignments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("manager_id", sa.Uuid(), nullable=False, index=True),
        sa.Column("employee_id", sa.Uuid(), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["manager_id"],
            ["users.id"],
            name="fk_team_assignments_manager"
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"],
            ["users.id"],
            name="fk_team_assignments_employee"
        ),
        sa.UniqueConstraint(
            "manager_id",
            "employee_id",
            name="uq_team_assignments_manager_employee"
        ),
    )

    op.add_column(
        "project_updates",
        sa.Column("user_id", sa.Uuid(), nullable=True, index=True)
    )
    op.create_foreign_key(
        "fk_project_updates_user",
        "project_updates",
        "users",
        ["user_id"],
        ["id"]
    )
    op.create_index(
        "ix_project_updates_user_start_week",
        "project_updates",
        ["user_id", "start_of_week"]
    )


def downgrade() -> None:
    op.drop_index("ix_project_updates_user_start_week", table_name="project_updates")
    op.drop_constraint("fk_project_updates_user", "project_updates", type_="foreignkey")
    op.drop_column("project_updates", "user_id")

    op.drop_table("team_assignments")
    op.drop_table("users")
