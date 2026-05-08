"""add reporting indexes

Revision ID: 202605080005
Revises: 202605080004
Create Date: 2026-05-08 01:35:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202605080005"
down_revision: str | None = "202605080004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing_indexes = {
        table_name: {index["name"] for index in inspector.get_indexes(table_name)}
        for table_name in inspector.get_table_names()
    }

    _create_index_if_missing(existing_indexes, "payments", "ix_payments_status", ["status"])
    _create_index_if_missing(existing_indexes, "payments", "ix_payments_due_date", ["due_date"])
    _create_index_if_missing(
        existing_indexes,
        "access_logs",
        "ix_access_logs_accessed_at",
        ["accessed_at"],
    )
    _create_index_if_missing(
        existing_indexes,
        "exercise_progress",
        "ix_exercise_progress_recorded_at",
        ["recorded_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_exercise_progress_recorded_at", table_name="exercise_progress")
    op.drop_index("ix_access_logs_accessed_at", table_name="access_logs")
    op.drop_index("ix_payments_due_date", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")


def _create_index_if_missing(
    existing_indexes: dict[str, set[str]],
    table_name: str,
    index_name: str,
    columns: list[str],
) -> None:
    if index_name not in existing_indexes.get(table_name, set()):
        op.create_index(index_name, table_name, columns, unique=False)
