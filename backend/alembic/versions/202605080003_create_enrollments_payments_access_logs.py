"""create enrollments payments and access logs

Revision ID: 202605080003
Revises: 202605080002
Create Date: 2026-05-08 00:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202605080003"
down_revision: str | None = "202605080002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())
    existing_columns = {
        table_name: {column["name"] for column in inspector.get_columns(table_name)}
        for table_name in existing_tables
    }

    op.execute("UPDATE students SET status = 'INACTIVE' WHERE status = 'DEFAULTER'")

    if "enrollments" not in existing_tables:
        op.create_table(
            "enrollments",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("student_id", sa.Integer(), nullable=False),
            sa.Column("plan_id", sa.Integer(), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("end_date", sa.Date(), nullable=False),
            sa.Column(
                "status",
                sa.Enum("ACTIVE", "EXPIRED", "CANCELLED", native_enum=False, length=20),
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
            sa.ForeignKeyConstraint(["plan_id"], ["plans.id"]),
            sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_enrollments_id"), "enrollments", ["id"], unique=False)
        op.create_index(
            op.f("ix_enrollments_plan_id"),
            "enrollments",
            ["plan_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_enrollments_student_id"),
            "enrollments",
            ["student_id"],
            unique=False,
        )

    if "payments" not in existing_tables:
        op.create_table(
            "payments",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("enrollment_id", sa.Integer(), nullable=False),
            sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column("due_date", sa.Date(), nullable=False),
            sa.Column("payment_date", sa.Date(), nullable=True),
            sa.Column(
                "status",
                sa.Enum("PENDING", "PAID", "OVERDUE", native_enum=False, length=20),
                nullable=False,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["enrollment_id"], ["enrollments.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_payments_id"), "payments", ["id"], unique=False)
        op.create_index(
            op.f("ix_payments_enrollment_id"),
            "payments",
            ["enrollment_id"],
            unique=False,
        )

    if "access_logs" not in existing_tables:
        op.create_table(
            "access_logs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("student_id", sa.Integer(), nullable=True),
            sa.Column("cpf_attempted", sa.String(length=14), nullable=False),
            sa.Column(
                "accessed_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("allowed", sa.Boolean(), nullable=False),
            sa.Column(
                "reason",
                sa.Enum(
                    "STUDENT_NOT_FOUND",
                    "STUDENT_INACTIVE",
                    "NO_ACTIVE_ENROLLMENT",
                    "ENROLLMENT_EXPIRED",
                    "PAYMENT_OVERDUE",
                    native_enum=False,
                    length=40,
                ),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_access_logs_id"), "access_logs", ["id"], unique=False)
        op.create_index(
            op.f("ix_access_logs_cpf_attempted"),
            "access_logs",
            ["cpf_attempted"],
            unique=False,
        )
        op.create_index(
            op.f("ix_access_logs_student_id"),
            "access_logs",
            ["student_id"],
            unique=False,
        )
    else:
        if "cpf_attempted" not in existing_columns["access_logs"]:
            op.add_column(
                "access_logs",
                sa.Column("cpf_attempted", sa.String(length=14), nullable=True),
            )
            op.execute(
                "UPDATE access_logs SET cpf_attempted = CAST(student_id AS VARCHAR) "
                "WHERE cpf_attempted IS NULL"
            )
            op.alter_column("access_logs", "cpf_attempted", nullable=False)
            op.create_index(
                op.f("ix_access_logs_cpf_attempted"),
                "access_logs",
                ["cpf_attempted"],
                unique=False,
            )
        op.alter_column("access_logs", "student_id", nullable=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_access_logs_cpf_attempted"), table_name="access_logs")
    op.drop_index(op.f("ix_access_logs_student_id"), table_name="access_logs")
    op.drop_index(op.f("ix_access_logs_id"), table_name="access_logs")
    op.drop_table("access_logs")
    op.drop_index(op.f("ix_payments_enrollment_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_id"), table_name="payments")
    op.drop_table("payments")
    op.drop_index(op.f("ix_enrollments_student_id"), table_name="enrollments")
    op.drop_index(op.f("ix_enrollments_plan_id"), table_name="enrollments")
    op.drop_index(op.f("ix_enrollments_id"), table_name="enrollments")
    op.drop_table("enrollments")
