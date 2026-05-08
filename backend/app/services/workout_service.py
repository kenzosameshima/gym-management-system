from collections.abc import Sequence

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ExerciseStatus, StudentStatus, UserRole, WorkoutPlanStatus
from app.core.exceptions import ApplicationError
from app.models.exercise import Exercise
from app.models.exercise_progress import ExerciseProgress
from app.models.workout_plan import WorkoutPlan
from app.repositories.student_repository import StudentRepository, get_student_repository
from app.repositories.user_repository import UserRepository, get_user_repository
from app.repositories.workout_repository import (
    ExerciseProgressRepository,
    ExerciseRepository,
    WorkoutPlanRepository,
    get_exercise_progress_repository,
    get_exercise_repository,
    get_workout_plan_repository,
)
from app.schemas.pagination import Page
from app.schemas.workout import (
    ExerciseCreate,
    ExerciseProgressCreate,
    ExerciseUpdate,
    WorkoutPlanCreate,
    WorkoutPlanRead,
    WorkoutPlanUpdate,
)


class WorkoutPlanService:
    def __init__(
        self,
        repository: WorkoutPlanRepository,
        student_repository: StudentRepository,
        user_repository: UserRepository,
    ) -> None:
        self._repository = repository
        self._student_repository = student_repository
        self._user_repository = user_repository

    async def list_workout_plans(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        student_id: int | None = None,
    ) -> Page[WorkoutPlanRead]:
        workout_plans, total = await self._repository.list(
            session,
            limit=limit,
            offset=offset,
            student_id=student_id,
        )
        return Page[WorkoutPlanRead](
            items=list(workout_plans),
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_workout_plan(
        self,
        session: AsyncSession,
        workout_plan_id: int,
    ) -> WorkoutPlan:
        workout_plan = await self._repository.get_by_id(session, workout_plan_id)
        if workout_plan is None:
            raise self._not_found_error()
        return workout_plan

    async def create_workout_plan(
        self,
        session: AsyncSession,
        payload: WorkoutPlanCreate,
    ) -> WorkoutPlan:
        await self._ensure_active_student(session, payload.student_id)
        await self._ensure_instructor(session, payload.instructor_id)
        try:
            workout_plan = await self._repository.create(session, payload)
            await session.commit()
            await session.refresh(workout_plan)
            return workout_plan
        except Exception:
            await session.rollback()
            raise

    async def update_workout_plan(
        self,
        session: AsyncSession,
        workout_plan_id: int,
        payload: WorkoutPlanUpdate,
    ) -> WorkoutPlan:
        workout_plan = await self.get_workout_plan(session, workout_plan_id)
        if payload.student_id is not None:
            await self._ensure_active_student(session, payload.student_id)
        if payload.instructor_id is not None:
            await self._ensure_instructor(session, payload.instructor_id)
        try:
            updated_workout_plan = await self._repository.update(session, workout_plan, payload)
            await session.commit()
            await session.refresh(updated_workout_plan)
            return updated_workout_plan
        except Exception:
            await session.rollback()
            raise

    async def delete_workout_plan(
        self,
        session: AsyncSession,
        workout_plan_id: int,
    ) -> WorkoutPlan:
        return await self.update_workout_plan(
            session,
            workout_plan_id,
            WorkoutPlanUpdate(status=WorkoutPlanStatus.INACTIVE),
        )

    async def _ensure_active_student(self, session: AsyncSession, student_id: int) -> None:
        student = await self._student_repository.get_by_id(session, student_id)
        if student is None:
            raise ApplicationError("STUDENT_NOT_FOUND", "Student was not found.", 404)
        if student.status != StudentStatus.ACTIVE:
            raise ApplicationError("STUDENT_INACTIVE", "Student is inactive.", 409)

    async def _ensure_instructor(self, session: AsyncSession, instructor_id: int) -> None:
        instructor = await self._user_repository.get_by_id(session, instructor_id)
        if instructor is None or not instructor.is_active:
            raise ApplicationError("INSTRUCTOR_NOT_FOUND", "Instructor was not found.", 404)
        if instructor.role != UserRole.INSTRUCTOR:
            raise ApplicationError("USER_IS_NOT_INSTRUCTOR", "User is not an instructor.", 409)

    @staticmethod
    def _not_found_error() -> ApplicationError:
        return ApplicationError(
            code="WORKOUT_PLAN_NOT_FOUND",
            message="Workout plan was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ExerciseService:
    def __init__(
        self,
        repository: ExerciseRepository,
        workout_plan_repository: WorkoutPlanRepository,
    ) -> None:
        self._repository = repository
        self._workout_plan_repository = workout_plan_repository

    async def list_exercises(
        self,
        session: AsyncSession,
        workout_plan_id: int,
    ) -> Sequence[Exercise]:
        await self._ensure_workout_plan_exists(session, workout_plan_id)
        return await self._repository.list_by_workout_plan(session, workout_plan_id)

    async def create_exercise(
        self,
        session: AsyncSession,
        workout_plan_id: int,
        payload: ExerciseCreate,
    ) -> Exercise:
        await self._ensure_active_workout_plan(session, workout_plan_id)
        try:
            exercise = await self._repository.create(session, workout_plan_id, payload)
            await session.commit()
            await session.refresh(exercise)
            return exercise
        except Exception:
            await session.rollback()
            raise

    async def update_exercise(
        self,
        session: AsyncSession,
        exercise_id: int,
        payload: ExerciseUpdate,
    ) -> Exercise:
        exercise = await self.get_exercise(session, exercise_id)
        try:
            updated_exercise = await self._repository.update(session, exercise, payload)
            await session.commit()
            await session.refresh(updated_exercise)
            return updated_exercise
        except Exception:
            await session.rollback()
            raise

    async def delete_exercise(self, session: AsyncSession, exercise_id: int) -> Exercise:
        return await self.update_exercise(
            session,
            exercise_id,
            ExerciseUpdate(status=ExerciseStatus.INACTIVE),
        )

    async def get_exercise(self, session: AsyncSession, exercise_id: int) -> Exercise:
        exercise = await self._repository.get_by_id(session, exercise_id)
        if exercise is None:
            raise ApplicationError("EXERCISE_NOT_FOUND", "Exercise was not found.", 404)
        return exercise

    async def _ensure_workout_plan_exists(
        self,
        session: AsyncSession,
        workout_plan_id: int,
    ) -> WorkoutPlan:
        workout_plan = await self._workout_plan_repository.get_by_id(session, workout_plan_id)
        if workout_plan is None:
            raise ApplicationError(
                "WORKOUT_PLAN_NOT_FOUND",
                "Workout plan was not found.",
                404,
            )
        return workout_plan

    async def _ensure_active_workout_plan(
        self,
        session: AsyncSession,
        workout_plan_id: int,
    ) -> WorkoutPlan:
        workout_plan = await self._ensure_workout_plan_exists(session, workout_plan_id)
        if workout_plan.status != WorkoutPlanStatus.ACTIVE:
            raise ApplicationError(
                "WORKOUT_PLAN_INACTIVE",
                "Workout plan is inactive.",
                status.HTTP_409_CONFLICT,
            )
        return workout_plan


class ExerciseProgressService:
    def __init__(
        self,
        repository: ExerciseProgressRepository,
        student_repository: StudentRepository,
        exercise_repository: ExerciseRepository,
    ) -> None:
        self._repository = repository
        self._student_repository = student_repository
        self._exercise_repository = exercise_repository

    async def create_exercise_progress(
        self,
        session: AsyncSession,
        payload: ExerciseProgressCreate,
    ) -> ExerciseProgress:
        await self._ensure_active_student(session, payload.student_id)
        await self._ensure_exercise_exists(session, payload.exercise_id)
        try:
            exercise_progress = await self._repository.create(session, payload)
            await session.commit()
            await session.refresh(exercise_progress)
            return exercise_progress
        except Exception:
            await session.rollback()
            raise

    async def list_by_student(
        self,
        session: AsyncSession,
        student_id: int,
    ) -> Sequence[ExerciseProgress]:
        return await self._repository.list_by_student(session, student_id)

    async def list_by_student_and_exercise(
        self,
        session: AsyncSession,
        *,
        student_id: int,
        exercise_id: int,
    ) -> Sequence[ExerciseProgress]:
        return await self._repository.list_by_student_and_exercise(
            session,
            student_id=student_id,
            exercise_id=exercise_id,
        )

    async def _ensure_active_student(self, session: AsyncSession, student_id: int) -> None:
        student = await self._student_repository.get_by_id(session, student_id)
        if student is None:
            raise ApplicationError("STUDENT_NOT_FOUND", "Student was not found.", 404)
        if student.status != StudentStatus.ACTIVE:
            raise ApplicationError("STUDENT_INACTIVE", "Student is inactive.", 409)

    async def _ensure_exercise_exists(self, session: AsyncSession, exercise_id: int) -> None:
        exercise = await self._exercise_repository.get_by_id(session, exercise_id)
        if exercise is None:
            raise ApplicationError("EXERCISE_NOT_FOUND", "Exercise was not found.", 404)


def get_workout_plan_service(
    repository: WorkoutPlanRepository = Depends(get_workout_plan_repository),
    student_repository: StudentRepository = Depends(get_student_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> WorkoutPlanService:
    return WorkoutPlanService(
        repository=repository,
        student_repository=student_repository,
        user_repository=user_repository,
    )


def get_exercise_service(
    repository: ExerciseRepository = Depends(get_exercise_repository),
    workout_plan_repository: WorkoutPlanRepository = Depends(get_workout_plan_repository),
) -> ExerciseService:
    return ExerciseService(
        repository=repository,
        workout_plan_repository=workout_plan_repository,
    )


def get_exercise_progress_service(
    repository: ExerciseProgressRepository = Depends(get_exercise_progress_repository),
    student_repository: StudentRepository = Depends(get_student_repository),
    exercise_repository: ExerciseRepository = Depends(get_exercise_repository),
) -> ExerciseProgressService:
    return ExerciseProgressService(
        repository=repository,
        student_repository=student_repository,
        exercise_repository=exercise_repository,
    )
