from collections.abc import Sequence

from fastapi import APIRouter, Depends, Query, status

from app.auth.permissions import require_roles
from app.core.enums import UserRole, WorkoutPlanStatus
from app.database.session import AsyncSessionDependency
from app.models.exercise import Exercise
from app.models.exercise_progress import ExerciseProgress
from app.models.workout_plan import WorkoutPlan
from app.schemas.pagination import Page
from app.schemas.workout import (
    ExerciseCreate,
    ExerciseProgressCreate,
    ExerciseProgressRead,
    ExerciseRead,
    ExerciseUpdate,
    WorkoutPlanCreate,
    WorkoutPlanRead,
    WorkoutPlanTransfer,
    WorkoutPlanTransferResult,
    WorkoutPlanUpdate,
)
from app.services.workout_service import (
    ExerciseProgressService,
    ExerciseService,
    WorkoutPlanService,
    get_exercise_progress_service,
    get_exercise_service,
    get_workout_plan_service,
)

router = APIRouter(tags=["workouts"])

WORKOUT_READ_ROLES = (UserRole.ADMIN, UserRole.INSTRUCTOR)
WORKOUT_WRITE_ROLES = (UserRole.ADMIN, UserRole.INSTRUCTOR)
WORKOUT_ADMIN_ROLES = (UserRole.ADMIN,)


@router.post(
    "/api/workout-plans",
    response_model=WorkoutPlanRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(*WORKOUT_WRITE_ROLES))],
)
async def create_workout_plan(
    payload: WorkoutPlanCreate,
    session: AsyncSessionDependency,
    service: WorkoutPlanService = Depends(get_workout_plan_service),
) -> WorkoutPlan:
    return await service.create_workout_plan(session=session, payload=payload)


@router.get(
    "/api/workout-plans",
    response_model=Page[WorkoutPlanRead],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_READ_ROLES))],
)
async def list_workout_plans(
    session: AsyncSessionDependency,
    limit: int = Query(default=20, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
    student_search: str | None = Query(default=None, min_length=1, max_length=320),
    instructor_search: str | None = Query(default=None, min_length=1, max_length=320),
    workout_status: WorkoutPlanStatus | None = Query(default=None, alias="status"),
    service: WorkoutPlanService = Depends(get_workout_plan_service),
) -> Page[WorkoutPlanRead]:
    return await service.list_workout_plans(
        session=session,
        limit=limit,
        offset=offset,
        student_search=student_search,
        instructor_search=instructor_search,
        status=workout_status,
    )


@router.get(
    "/api/workout-plans/student/{student_id}",
    response_model=Page[WorkoutPlanRead],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_READ_ROLES))],
)
async def list_workout_plans_by_student(
    student_id: int,
    session: AsyncSessionDependency,
    limit: int = Query(default=20, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
    service: WorkoutPlanService = Depends(get_workout_plan_service),
) -> Page[WorkoutPlanRead]:
    return await service.list_workout_plans(
        session=session,
        limit=limit,
        offset=offset,
        student_id=student_id,
    )


@router.get(
    "/api/workout-plans/{workout_plan_id}",
    response_model=WorkoutPlanRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_READ_ROLES))],
)
async def get_workout_plan(
    workout_plan_id: int,
    session: AsyncSessionDependency,
    service: WorkoutPlanService = Depends(get_workout_plan_service),
) -> WorkoutPlan:
    return await service.get_workout_plan(session=session, workout_plan_id=workout_plan_id)


@router.put(
    "/api/workout-plans/{workout_plan_id}",
    response_model=WorkoutPlanRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_WRITE_ROLES))],
)
async def update_workout_plan(
    workout_plan_id: int,
    payload: WorkoutPlanUpdate,
    session: AsyncSessionDependency,
    service: WorkoutPlanService = Depends(get_workout_plan_service),
) -> WorkoutPlan:
    return await service.update_workout_plan(
        session=session,
        workout_plan_id=workout_plan_id,
        payload=payload,
    )


@router.delete(
    "/api/workout-plans/{workout_plan_id}",
    response_model=WorkoutPlanRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_WRITE_ROLES))],
)
async def delete_workout_plan(
    workout_plan_id: int,
    session: AsyncSessionDependency,
    service: WorkoutPlanService = Depends(get_workout_plan_service),
) -> WorkoutPlan:
    return await service.delete_workout_plan(session=session, workout_plan_id=workout_plan_id)


@router.post(
    "/api/workout-plans/transfer",
    response_model=WorkoutPlanTransferResult,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_ADMIN_ROLES))],
)
async def transfer_workout_plans(
    payload: WorkoutPlanTransfer,
    session: AsyncSessionDependency,
    service: WorkoutPlanService = Depends(get_workout_plan_service),
) -> WorkoutPlanTransferResult:
    return await service.transfer_workout_plans(session=session, payload=payload)


@router.post(
    "/api/workout-plans/{workout_plan_id}/exercises",
    response_model=ExerciseRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(*WORKOUT_WRITE_ROLES))],
)
async def create_exercise(
    workout_plan_id: int,
    payload: ExerciseCreate,
    session: AsyncSessionDependency,
    service: ExerciseService = Depends(get_exercise_service),
) -> Exercise:
    return await service.create_exercise(
        session=session,
        workout_plan_id=workout_plan_id,
        payload=payload,
    )


@router.get(
    "/api/workout-plans/{workout_plan_id}/exercises",
    response_model=list[ExerciseRead],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_READ_ROLES))],
)
async def list_exercises(
    workout_plan_id: int,
    session: AsyncSessionDependency,
    service: ExerciseService = Depends(get_exercise_service),
) -> Sequence[Exercise]:
    return await service.list_exercises(session=session, workout_plan_id=workout_plan_id)


@router.put(
    "/api/exercises/{exercise_id}",
    response_model=ExerciseRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_WRITE_ROLES))],
)
async def update_exercise(
    exercise_id: int,
    payload: ExerciseUpdate,
    session: AsyncSessionDependency,
    service: ExerciseService = Depends(get_exercise_service),
) -> Exercise:
    return await service.update_exercise(session=session, exercise_id=exercise_id, payload=payload)


@router.delete(
    "/api/exercises/{exercise_id}",
    response_model=ExerciseRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_WRITE_ROLES))],
)
async def delete_exercise(
    exercise_id: int,
    session: AsyncSessionDependency,
    service: ExerciseService = Depends(get_exercise_service),
) -> Exercise:
    return await service.delete_exercise(session=session, exercise_id=exercise_id)


@router.post(
    "/api/exercise-progress",
    response_model=ExerciseProgressRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(*WORKOUT_WRITE_ROLES))],
)
async def create_exercise_progress(
    payload: ExerciseProgressCreate,
    session: AsyncSessionDependency,
    service: ExerciseProgressService = Depends(get_exercise_progress_service),
) -> ExerciseProgress:
    return await service.create_exercise_progress(session=session, payload=payload)


@router.get(
    "/api/exercise-progress/student/{student_id}",
    response_model=list[ExerciseProgressRead],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_READ_ROLES))],
)
async def list_exercise_progress_by_student(
    student_id: int,
    session: AsyncSessionDependency,
    service: ExerciseProgressService = Depends(get_exercise_progress_service),
) -> Sequence[ExerciseProgress]:
    return await service.list_by_student(session=session, student_id=student_id)


@router.get(
    "/api/exercise-progress/student/{student_id}/exercise/{exercise_id}",
    response_model=list[ExerciseProgressRead],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*WORKOUT_READ_ROLES))],
)
async def list_exercise_progress_by_student_and_exercise(
    student_id: int,
    exercise_id: int,
    session: AsyncSessionDependency,
    service: ExerciseProgressService = Depends(get_exercise_progress_service),
) -> Sequence[ExerciseProgress]:
    return await service.list_by_student_and_exercise(
        session=session,
        student_id=student_id,
        exercise_id=exercise_id,
    )
