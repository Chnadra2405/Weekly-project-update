"""New roles, approval status, and delegation."""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def _column_exists(table: str, column: str) -> bool:
    conn = op.get_bind()
    return bool(conn.execute(
        sa.text("SELECT COUNT(*) FROM sys.columns WHERE object_id=OBJECT_ID(:t) AND name=:c"),
        {"t": table, "c": column},
    ).scalar())


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    return bool(conn.execute(
        sa.text("SELECT COUNT(*) FROM sys.tables WHERE name=:t"), {"t": table}
    ).scalar())


def _check_exists(name: str, table: str) -> bool:
    conn = op.get_bind()
    return bool(conn.execute(
        sa.text("SELECT COUNT(*) FROM sys.check_constraints WHERE name=:n AND parent_object_id=OBJECT_ID(:t)"),
        {"n": name, "t": table},
    ).scalar())


def _fk_exists(name: str) -> bool:
    conn = op.get_bind()
    return bool(conn.execute(
        sa.text("SELECT COUNT(*) FROM sys.foreign_keys WHERE name=:n"), {"n": name}
    ).scalar())


def _index_exists(name: str) -> bool:
    conn = op.get_bind()
    return bool(conn.execute(
        sa.text("SELECT COUNT(*) FROM sys.indexes WHERE name=:n"), {"n": name}
    ).scalar())


def upgrade() -> None:
    # 1. Drop old role constraint first so UPDATE can use new values
    if _check_exists("ck_users_role", "users"):
        op.drop_constraint("ck_users_role", "users", type_="check")

    # 2. Migrate existing role values
    op.execute("UPDATE users SET role='TEAM_LEAD'    WHERE role='EMPLOYEE'")
    op.execute("UPDATE users SET role='TEAM_MANAGER' WHERE role='MANAGER'")
    op.execute("UPDATE users SET role='APP_ADMIN'    WHERE role='ADMIN'")

    # 3. New role constraint
    op.create_check_constraint(
        "ck_users_role", "users",
        "role IN ('APP_ADMIN', 'DU_HEAD', 'TEAM_MANAGER', 'TEAM_LEAD')",
    )

    # 4. Approval fields on project_updates (idempotent)
    if not _column_exists("project_updates", "approval_status"):
        op.add_column("project_updates", sa.Column("approval_status", sa.String(20), nullable=False, server_default="DRAFT"))
    if not _column_exists("project_updates", "approved_by_id"):
        op.add_column("project_updates", sa.Column("approved_by_id", sa.Uuid(), nullable=True))
    if not _fk_exists("fk_project_updates_approved_by"):
        op.create_foreign_key("fk_project_updates_approved_by", "project_updates", "users", ["approved_by_id"], ["id"])
    if not _column_exists("project_updates", "approved_at"):
        op.add_column("project_updates", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    if not _check_exists("ck_project_updates_approval_status", "project_updates"):
        op.create_check_constraint("ck_project_updates_approval_status", "project_updates", "approval_status IN ('DRAFT','APPROVED')")

    # 5. Delegations table (idempotent)
    if not _table_exists("delegations"):
        op.create_table(
            "delegations",
            sa.Column("id", sa.Uuid(), primary_key=True),
            sa.Column("manager_id", sa.Uuid(), nullable=False),
            sa.Column("delegate_id", sa.Uuid(), nullable=False),
            sa.Column("created_by_id", sa.Uuid(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["manager_id"], ["users.id"], name="fk_delegations_manager"),
            sa.ForeignKeyConstraint(["delegate_id"], ["users.id"], name="fk_delegations_delegate"),
            sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], name="fk_delegations_created_by"),
        )
    if not _index_exists("ix_delegations_manager_id"):
        op.create_index("ix_delegations_manager_id", "delegations", ["manager_id"])
    if not _index_exists("ix_delegations_delegate_id"):
        op.create_index("ix_delegations_delegate_id", "delegations", ["delegate_id"])
    if not _index_exists("ix_delegations_is_active"):
        op.create_index("ix_delegations_is_active", "delegations", ["is_active"])


def downgrade() -> None:
    if _table_exists("delegations"):
        op.drop_table("delegations")
    if _check_exists("ck_project_updates_approval_status", "project_updates"):
        op.drop_constraint("ck_project_updates_approval_status", "project_updates", type_="check")
    if _fk_exists("fk_project_updates_approved_by"):
        op.drop_constraint("fk_project_updates_approved_by", "project_updates", type_="foreignkey")
    if _column_exists("project_updates", "approved_at"):
        op.drop_column("project_updates", "approved_at")
    if _column_exists("project_updates", "approved_by_id"):
        op.drop_column("project_updates", "approved_by_id")
    if _column_exists("project_updates", "approval_status"):
        op.drop_column("project_updates", "approval_status")
    if _check_exists("ck_users_role", "users"):
        op.drop_constraint("ck_users_role", "users", type_="check")
    op.create_check_constraint("ck_users_role", "users", "role IN ('EMPLOYEE','MANAGER','ADMIN')")
    op.execute("UPDATE users SET role='EMPLOYEE' WHERE role='TEAM_LEAD'")
    op.execute("UPDATE users SET role='MANAGER'  WHERE role='TEAM_MANAGER'")
    op.execute("UPDATE users SET role='ADMIN'    WHERE role='APP_ADMIN'")
    op.execute("UPDATE users SET role='EMPLOYEE' WHERE role='DU_HEAD'")
