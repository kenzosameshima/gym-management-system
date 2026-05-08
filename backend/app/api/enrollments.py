from fastapi import APIRouter, Depends, Query, status

from app.auth.permissions import require_roles
from app.core.enums import EnrollmentStatus, UserRole
from app.database.session import AsyncSessionDependency
from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate, EnrollmentRead, EnrollmentUpdate
from app.schemas.pagination import Page
from app.services.enrollment_service import EnrollmentService, get_enrollment_service

router = APIRouter(prefix="/api/enrollments", tags=["enrollments"])

ENROLLMENT_MANAGEMENT_ROLES = (UserRole.ADMIN, UserRole.RECEPTIONIST)


@router.post(
    "",
    response_model=EnrollmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create enrollment",
    description=("Creates an active enrollment and its first pending payment in one transaction."),
    dependencies=[Depends(require_roles(*ENROLLMENT_MANAGEMENT_ROLES))],
)
async def create_enrollment(
    payload: EnrollmentCreate,
    session: AsyncSessionDependency,
    service: EnrollmentService = Depends(get_enrollment_service),
) -> Enrollment:
    return await service.create_enrollment(session=session, payload=payload)


@router.get(
    "",
    response_model=Page[EnrollmentRead],
    status_code=status.HTTP_200_OK,
    summary="List enrollments",
    description=(
        "Returns a paginated enrollment list with optional student, plan, and status " "filters."
    ),
    dependencies=[Depends(require_roles(*ENROLLMENT_MANAGEMENT_ROLES))],
)
async def list_enrollments(
    session: AsyncSessionDependency,
    limit: int = Query(default=20, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
    student_id: int | None = Query(default=None, gt=0),
    plan_id: int | None = Query(default=None, gt=0),
    enrollment_status: EnrollmentStatus | None = Query(default=None, alias="status"),
    service: EnrollmentService = Depends(get_enrollment_service),
) -> Page[EnrollmentRead]:
    return await service.list_enrollments(
        session=session,
        limit=limit,
        offset=offset,
        student_id=student_id,
        plan_id=plan_id,
        status=enrollment_status,
    )


@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentRead,
    status_code=status.HTTP_200_OK,
    summary="Get enrollment",
    description="Returns one enrollment by id.",
    dependencies=[Depends(require_roles(*ENROLLMENT_MANAGEMENT_ROLES))],
)
async def get_enrollment(
    enrollment_id: int,
    session: AsyncSessionDependency,
    service: EnrollmentService = Depends(get_enrollment_service),
) -> Enrollment:
    return await service.get_enrollment(session=session, enrollment_id=enrollment_id)


@router.put(
    "/{enrollment_id}",
    response_model=EnrollmentRead,
    status_code=status.HTTP_200_OK,
    summary="Update enrollment",
    description="Updates enrollment dates or status.",
    dependencies=[Depends(require_roles(*ENROLLMENT_MANAGEMENT_ROLES))],
)
async def update_enrollment(
    enrollment_id: int,
    payload: EnrollmentUpdate,
    session: AsyncSessionDependency,
    service: EnrollmentService = Depends(get_enrollment_service),
) -> Enrollment:
    return await service.update_enrollment(
        session=session,
        enrollment_id=enrollment_id,
        payload=payload,
    )


@router.delete(
    "/{enrollment_id}",
    response_model=EnrollmentRead,
    status_code=status.HTTP_200_OK,
    summary="Cancel enrollment",
    description="Soft deletes an enrollment by changing status to CANCELLED.",
    dependencies=[Depends(require_roles(*ENROLLMENT_MANAGEMENT_ROLES))],
)
async def cancel_enrollment(
    enrollment_id: int,
    session: AsyncSessionDependency,
    service: EnrollmentService = Depends(get_enrollment_service),
) -> Enrollment:
    return await service.cancel_enrollment(session=session, enrollment_id=enrollment_id)
