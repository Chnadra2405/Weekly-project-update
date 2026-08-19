"""Convert project updates to weekly direct persistence."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("project_updates", sa.Column("start_of_week", mssql.DATE(), nullable=True))
    op.add_column("project_updates", sa.Column("end_of_week", mssql.DATE(), nullable=True))
    op.execute(
        "UPDATE project_updates "
        "SET start_of_week = reporting_month, end_of_week = DATEADD(day, 6, reporting_month)"
    )
    op.alter_column("project_updates", "start_of_week", existing_type=mssql.DATE(), nullable=False)
    op.alter_column("project_updates", "end_of_week", existing_type=mssql.DATE(), nullable=False)

    op.drop_table("attachments")
    op.drop_index("ix_project_updates_employee_month", table_name="project_updates")
    op.drop_constraint("ck_project_updates_terminal_fields", "project_updates", type_="check")
    op.drop_constraint("ck_project_updates_status", "project_updates", type_="check")
    op.drop_constraint("ck_project_updates_month_first_day", "project_updates", type_="check")
    op.drop_column("project_updates", "employee_name")
    op.drop_column("project_updates", "employee_email")
    op.drop_column("project_updates", "reporting_month")
    op.drop_column("project_updates", "delivery_status", mssql_drop_default=True)
    op.drop_column("project_updates", "smtp_message_id")
    op.drop_column("project_updates", "failure_code")
    op.drop_column("project_updates", "failure_detail")
    op.drop_column("project_updates", "sent_at")

    op.create_check_constraint(
        "ck_project_updates_seven_day_week",
        "project_updates",
        "end_of_week = DATEADD(day, 6, start_of_week)",
    )
    op.create_index("ix_project_updates_start_of_week", "project_updates", ["start_of_week"])


def downgrade() -> None:
    raise RuntimeError("Migration 0002 permanently removes legacy project update data and cannot be downgraded.")