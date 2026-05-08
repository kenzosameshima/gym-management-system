from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise import Exercise
from app.models.exercise_progress import ExerciseProgress
from app.models.workout_plan import WorkoutPlan
from app.schemas.workout import (
    ExerciseCreate,
    ExerciseProgressCreate,
    ExerciseUpdate,
    WorkoutPlanCreate,
    WorkoutPlanUpdate,
)


class WorkoutPlanRepository:
    async def list(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        student_id: int | None = None,
    ) -> tuple[Sequence[WorkoutPlan], int]:
        statement = self._filtered_statement(student_id=student_id)
        total_result = await session.execute(select(func.count()).select_from(statement.subquery()))
        result = await session.execute(
            statement.order_by(WorkoutPlan.id).limit(limit).offset(offset)
        )
        return result.scalars().all(), total_result.scalar_one()

    async def get_by_id(
        self,
        session: AsyncSession,
        workout_plan_id: int,
    ) -> WorkoutPlan | None:
        return await session.get(WorkoutPlan, workout_plan_id)

    async def create(self, session: AsyncSession, payload: WorkoutPlanCreate) -> WorkoutPlan:
        workout_plan = WorkoutPlan(**payload.model_dump())
        session.add(workout_plan)
        await session.flush()
        await session.refresh(workout_plan)
        return workout_plan

    async def update(
        self,
        session: AsyncSession,
        workout_plan: WorkoutPlan,
        payload: WorkoutPlanUpdate,
    ) -> WorkoutPlan:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(workout_plan, field, value)
        await session.flush()
        await session.refresh(workout_plan)
        return workout_plan

    def _filtered_statement(self, *, student_id: int | None) -> Select[tuple[WorkoutPlan]]:
        statement = select(WorkoutPlan)
        if student_id is not None:
            statement = statement.where(WorkoutPlan.student_id == student_id)
        return statement


class ExerciseRepository:
    async def list_by_workout_plan(
        self,
        session: AsyncSession,
        workout_plan_id: int,
    ) -> Sequence[Exercise]:
        result = await session.execute(
            select(Exercise)
            .where(Exercise.workout_plan_id == workout_plan_id)
            .order_by(Exercise.id)
        )
        return result.scalars().all()

    async def get_by_id(self, session: AsyncSession, exercise_id: int) -> Exercise | None:
        return await session.get(Exercise, exercise_id)

    async def create(
        self,
        session: AsyncSession,
        workout_plan_id: int,
        payload: ExerciseCreate,
    ) -> Exercise:
        exercise = Exercise(workout_plan_id=workout_plan_id, **payload.model_dump())
        session.add(exercise)
        await session.flush()
        await session.refresh(exercise)
        return exercise

    async def update(
        self,
        session: AsyncSession,
        exercise: Exercise,
        payload: ExerciseUpdate,
    ) -> Exercise:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(exercise, field, value)
        await session.flush()
        await session.refresh(exercise)
        return exercise


class ExerciseProgressRepository:
    async def create(
        self,
        session: AsyncSession,
        payload: ExerciseProgressCreate,
    ) -> ExerciseProgress:
        exercise_progress = ExerciseProgress(**payload.model_dump())
        session.add(exercise_progress)
        await session.flush()
        await session.refresh(exercise_progress)
        return exercise_progress

    async def list_by_student(
        self,
        session: AsyncSession,
        student_id: int,
    ) -> Sequence[ExerciseProgress]:
        result = await session.execute(
            select(ExerciseProgress)
            .where(ExerciseProgress.student_id == student_id)
            .order_by(ExerciseProgress.recorded_at, ExerciseProgress.id)
        )
        return result.scalars().all()

    async def list_by_student_and_exercise(
        self,
        session: AsyncSession,
        *,
        student_id: int,
        exercise_id: int,
    ) -> Sequence[ExerciseProgress]:
        result = await session.execute(
            select(ExerciseProgress)
            .where(
                ExerciseProgress.student_id == student_id,
                ExerciseProgress.exercise_id == exercise_id,
            )
            .order_by(ExerciseProgress.recorded_at, ExerciseProgress.id)
        )
        return result.scalars().all()


def get_workout_plan_repository() -> WorkoutPlanRepository:
    return WorkoutPlanRepository()


def get_exercise_repository() -> ExerciseRepository:
    return ExerciseRepository()


def get_exercise_progress_repository() -> ExerciseProgressRepository:
    return ExerciseProgressRepository()
