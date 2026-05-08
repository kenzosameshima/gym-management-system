"""create students and plans

Revision ID: 202605080002
Revises: 202605080001
Create Date: 2026-05-08 00:02:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202605080002"
down_revision: str | None = "202605080001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    if "students" not in existing_tables:
        op.create_table(
            "students",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("cpf", sa.String(length=14), nullable=False),
            sa.Column("birth_date", sa.Date(), nullable=False),
            sa.Column("phone", sa.String(length=32), nullable=True),
            sa.Column("email", sa.String(length=320), nullable=False),
            sa.Column("address", sa.Text(), nullable=True),
            sa.Column(
                "status",
                sa.Enum("ACTIVE", "INACTIVE", native_enum=False, length=20),
                nullable=False,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_students_cpf"), "students", ["cpf"], unique=True)
        op.create_index(op.f("ix_students_email"), "students", ["email"], unique=True)
        op.create_index(op.f("ix_students_id"), "students", ["id"], unique=False)

    if "plans" not in existing_tables:
        op.create_table(
            "plans",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column("duration_days", sa.Integer(), nullable=False),
            sa.Column(
                "status",
                sa.Enum("ACTIVE", "INACTIVE", native_enum=False, length=20),
                nullable=False,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_plans_id"), "plans", ["id"], unique=False)
        op.create_index(op.f("ix_plans_name"), "plans", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_plans_name"), table_name="plans")
    op.drop_index(op.f("ix_plans_id"), table_name="plans")
    op.drop_table("plans")
    op.drop_index(op.f("ix_students_id"), table_name="students")
    op.drop_index(op.f("ix_students_email"), table_name="students")
    op.drop_index(op.f("ix_students_cpf"), table_name="students")
    op.drop_table("students")
