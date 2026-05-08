"""create workout domain

Revision ID: 202605080004
Revises: 202605080003
Create Date: 2026-05-08 01:10:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "202605080004"
down_revision: str | None = "202605080003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing_tables = set(inspector.get_table_names())

    if "workout_plans" not in existing_tables:
        op.create_table(
            "workout_plans",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("student_id", sa.Integer(), nullable=False),
            sa.Column("instructor_id", sa.Integer(), nullable=False),
            sa.Column("goal", sa.String(length=255), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
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
            sa.ForeignKeyConstraint(["instructor_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_workout_plans_id"), "workout_plans", ["id"], unique=False)
        op.create_index(
            op.f("ix_workout_plans_instructor_id"),
            "workout_plans",
            ["instructor_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_workout_plans_student_id"),
            "workout_plans",
            ["student_id"],
            unique=False,
        )

    if "exercises" not in existing_tables:
        op.create_table(
            "exercises",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("workout_plan_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("muscle_group", sa.String(length=100), nullable=False),
            sa.Column("sets", sa.Integer(), nullable=False),
            sa.Column("repetitions", sa.Integer(), nullable=False),
            sa.Column("load", sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
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
            sa.ForeignKeyConstraint(["workout_plan_id"], ["workout_plans.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_exercises_id"), "exercises", ["id"], unique=False)
        op.create_index(
            op.f("ix_exercises_workout_plan_id"),
            "exercises",
            ["workout_plan_id"],
            unique=False,
        )

    if "exercise_progress" not in existing_tables:
        op.create_table(
            "exercise_progress",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("student_id", sa.Integer(), nullable=False),
            sa.Column("exercise_id", sa.Integer(), nullable=False),
            sa.Column("load", sa.Numeric(precision=10, scale=2), nullable=True),
            sa.Column("repetitions", sa.Integer(), nullable=False),
            sa.Column(
                "recorded_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"]),
            sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_exercise_progress_exercise_id"),
            "exercise_progress",
            ["exercise_id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_exercise_progress_id"),
            "exercise_progress",
            ["id"],
            unique=False,
        )
        op.create_index(
            op.f("ix_exercise_progress_student_id"),
            "exercise_progress",
            ["student_id"],
            unique=False,
        )


def downgrade() -> None:
    op.drop_index(op.f("ix_exercise_progress_student_id"), table_name="exercise_progress")
    op.drop_index(op.f("ix_exercise_progress_id"), table_name="exercise_progress")
    op.drop_index(op.f("ix_exercise_progress_exercise_id"), table_name="exercise_progress")
    op.drop_table("exercise_progress")
    op.drop_index(op.f("ix_exercises_workout_plan_id"), table_name="exercises")
    op.drop_index(op.f("ix_exercises_id"), table_name="exercises")
    op.drop_table("exercises")
    op.drop_index(op.f("ix_workout_plans_student_id"), table_name="workout_plans")
    op.drop_index(op.f("ix_workout_plans_instructor_id"), table_name="workout_plans")
    op.drop_index(op.f("ix_workout_plans_id"), table_name="workout_plans")
    op.drop_table("workout_plans")
