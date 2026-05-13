"""add user security fields and audit

Revision ID: 202605130001
Revises: 202605100001
Create Date: 2026-05-13 00:01:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202605130001"
down_revision: str | None = "202605100001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    user_columns = {column["name"] for column in inspector.get_columns("users")}

    if "must_change_password" not in user_columns:
        op.add_column(
            "users",
            sa.Column(
                "must_change_password",
                sa.Boolean(),
                server_default=sa.false(),
                nullable=False,
            ),
        )
        op.alter_column("users", "must_change_password", server_default=None)

    if "last_login_at" not in user_columns:
        op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))

    if "user_audit_logs" in inspector.get_table_names():
        return

    op.create_table(
        "user_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("target_user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("details", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_audit_logs_action"), "user_audit_logs", ["action"])
    op.create_index(op.f("ix_user_audit_logs_actor_user_id"), "user_audit_logs", ["actor_user_id"])
    op.create_index(op.f("ix_user_audit_logs_id"), "user_audit_logs", ["id"])
    op.create_index(op.f("ix_user_audit_logs_target_user_id"), "user_audit_logs", ["target_user_id"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "user_audit_logs" in inspector.get_table_names():
        op.drop_index(op.f("ix_user_audit_logs_target_user_id"), table_name="user_audit_logs")
        op.drop_index(op.f("ix_user_audit_logs_id"), table_name="user_audit_logs")
        op.drop_index(op.f("ix_user_audit_logs_actor_user_id"), table_name="user_audit_logs")
        op.drop_index(op.f("ix_user_audit_logs_action"), table_name="user_audit_logs")
        op.drop_table("user_audit_logs")

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "last_login_at" in user_columns:
        op.drop_column("users", "last_login_at")
    if "must_change_password" in user_columns:
        op.drop_column("users", "must_change_password")
