"""Create project update and attachment tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "project_updates",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("employee_name", sa.Unicode(200), nullable=False),
        sa.Column("employee_email", sa.String(320), nullable=False),
        sa.Column("reporting_month", mssql.DATE(), nullable=False),
        sa.Column("team_project", sa.Unicode(300), nullable=False),
        sa.Column("achievements", mssql.NVARCHAR(None), nullable=False),
        sa.Column("initiatives", mssql.NVARCHAR(None), nullable=False),
        sa.Column("next_weeks_plan", mssql.NVARCHAR(None), nullable=False),
        sa.Column("delivery_status", sa.String(16), nullable=False, server_default="PENDING"),
        sa.Column("smtp_message_id", sa.String(255)),
        sa.Column("failure_code", sa.String(64)),
        sa.Column("failure_detail", sa.String(1000)),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("delivery_status IN ('PENDING','SENT','FAILED')", name="ck_project_updates_status"),
        sa.CheckConstraint("DAY(reporting_month) = 1", name="ck_project_updates_month_first_day"),
        sa.CheckConstraint(
            "(delivery_status = 'PENDING' AND smtp_message_id IS NULL AND failure_code IS NULL AND failure_detail IS NULL AND sent_at IS NULL) OR "
            "(delivery_status = 'SENT' AND smtp_message_id IS NOT NULL AND failure_code IS NULL AND failure_detail IS NULL AND sent_at IS NOT NULL) OR "
            "(delivery_status = 'FAILED' AND smtp_message_id IS NULL AND failure_code IS NOT NULL AND failure_detail IS NOT NULL AND sent_at IS NULL)",
            name="ck_project_updates_terminal_fields",
        ),
    )
    op.create_index("uq_project_updates_idempotency_key", "project_updates", ["idempotency_key"], unique=True)
    op.create_index("ix_project_updates_employee_month", "project_updates", ["employee_email", "reporting_month"])
    op.create_index("ix_project_updates_created_at", "project_updates", ["created_at"])
    op.create_table(
        "attachments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "project_update_id",
            sa.Uuid(),
            sa.ForeignKey("project_updates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(24), nullable=False),
        sa.Column("original_filename", sa.Unicode(255), nullable=False),
        sa.Column("stored_relative_path", sa.Unicode(500), nullable=False),
        sa.Column("media_type", sa.String(127), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("kind IN ('REFERENCE_EMAIL','IMAGE')", name="ck_attachments_kind"),
        sa.CheckConstraint("size_bytes > 0 AND size_bytes <= 10485760", name="ck_attachments_size"),
        sa.UniqueConstraint("project_update_id", "kind", name="uq_attachments_update_kind"),
    )
    op.create_index("ix_attachments_project_update_id", "attachments", ["project_update_id"])


def downgrade() -> None:
    op.drop_table("attachments")
    op.drop_table("project_updates")