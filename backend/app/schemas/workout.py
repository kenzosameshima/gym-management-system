from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ExerciseStatus, WorkoutPlanStatus


class WorkoutPlanCreate(BaseModel):
    student_id: int = Field(gt=0)
    instructor_id: int = Field(gt=0)
    goal: str = Field(min_length=1, max_length=255)
    notes: str | None = None
    status: WorkoutPlanStatus = WorkoutPlanStatus.ACTIVE


class WorkoutPlanUpdate(BaseModel):
    student_id: int | None = Field(default=None, gt=0)
    instructor_id: int | None = Field(default=None, gt=0)
    goal: str | None = Field(default=None, min_length=1, max_length=255)
    notes: str | None = None
    status: WorkoutPlanStatus | None = None


class WorkoutPlanTransfer(BaseModel):
    from_instructor_id: int = Field(gt=0)
    to_instructor_id: int = Field(gt=0)
    status: WorkoutPlanStatus = WorkoutPlanStatus.ACTIVE


class WorkoutPlanTransferResult(BaseModel):
    from_instructor_id: int
    to_instructor_id: int
    transferred_count: int


class WorkoutPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    instructor_id: int
    goal: str
    notes: str | None
    status: WorkoutPlanStatus
    created_at: datetime
    updated_at: datetime


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    muscle_group: str = Field(min_length=1, max_length=100)
    sets: int = Field(gt=0)
    repetitions: int = Field(gt=0)
    load: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    notes: str | None = None
    status: ExerciseStatus = ExerciseStatus.ACTIVE


class ExerciseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    muscle_group: str | None = Field(default=None, min_length=1, max_length=100)
    sets: int | None = Field(default=None, gt=0)
    repetitions: int | None = Field(default=None, gt=0)
    load: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    notes: str | None = None
    status: ExerciseStatus | None = None


class ExerciseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workout_plan_id: int
    name: str
    muscle_group: str
    sets: int
    repetitions: int
    load: Decimal | None
    notes: str | None
    status: ExerciseStatus
    created_at: datetime
    updated_at: datetime


class ExerciseProgressCreate(BaseModel):
    student_id: int = Field(gt=0)
    exercise_id: int = Field(gt=0)
    load: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    repetitions: int = Field(gt=0)
    notes: str | None = None


class ExerciseProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    exercise_id: int
    load: Decimal | None
    repetitions: int
    recorded_at: datetime
    notes: str | None
