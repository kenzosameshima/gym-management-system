from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ExerciseStatus
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.workout_plan import WorkoutPlan


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workout_plan_id: Mapped[int] = mapped_column(
        ForeignKey("workout_plans.id"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    muscle_group: Mapped[str] = mapped_column(String(100), nullable=False)
    sets: Mapped[int] = mapped_column(nullable=False)
    repetitions: Mapped[int] = mapped_column(nullable=False)
    load: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ExerciseStatus] = mapped_column(
        Enum(ExerciseStatus, native_enum=False, length=20),
        nullable=False,
        default=ExerciseStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    workout_plan: Mapped["WorkoutPlan"] = relationship()
