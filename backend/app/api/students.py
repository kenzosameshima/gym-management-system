from fastapi import APIRouter, Depends, Query, status

from app.auth.permissions import require_roles
from app.core.enums import UserRole
from app.database.session import AsyncSessionDependency
from app.models.student import Student
from app.schemas.pagination import Page
from app.schemas.student import StudentCreate, StudentRead, StudentUpdate
from app.services.student_service import StudentService, get_student_service

router = APIRouter(prefix="/api/students", tags=["students"])


@router.post(
    "",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create student",
    description="Creates an active or inactive student after validating CPF and email uniqueness.",
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST))],
)
async def create_student(
    payload: StudentCreate,
    session: AsyncSessionDependency,
    service: StudentService = Depends(get_student_service),
) -> Student:
    return await service.create_student(session=session, payload=payload)


@router.get(
    "",
    response_model=Page[StudentRead],
    status_code=status.HTTP_200_OK,
    summary="List students",
    description=(
        "Returns a paginated student list with optional CPF, email, and name search " "filters."
    ),
    dependencies=[
        Depends(require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.INSTRUCTOR))
    ],
)
async def list_students(
    session: AsyncSessionDependency,
    limit: int = Query(default=20, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, min_length=1),
    cpf: str | None = Query(default=None, min_length=11, max_length=14),
    email: str | None = Query(default=None, min_length=3, max_length=320),
    name: str | None = Query(default=None, min_length=1, max_length=255),
    service: StudentService = Depends(get_student_service),
) -> Page[StudentRead]:
    return await service.list_students(
        session=session,
        limit=limit,
        offset=offset,
        search=search,
        cpf=cpf,
        email=email,
        name=name,
    )


@router.get(
    "/{student_id}",
    response_model=StudentRead,
    status_code=status.HTTP_200_OK,
    summary="Get student",
    description="Returns one student by id.",
    dependencies=[
        Depends(require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.INSTRUCTOR))
    ],
)
async def get_student(
    student_id: int,
    session: AsyncSessionDependency,
    service: StudentService = Depends(get_student_service),
) -> Student:
    return await service.get_student(session=session, student_id=student_id)


@router.put(
    "/{student_id}",
    response_model=StudentRead,
    status_code=status.HTTP_200_OK,
    summary="Update student",
    description="Updates student data after validating CPF and email uniqueness.",
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST))],
)
async def update_student(
    student_id: int,
    payload: StudentUpdate,
    session: AsyncSessionDependency,
    service: StudentService = Depends(get_student_service),
) -> Student:
    return await service.update_student(session=session, student_id=student_id, payload=payload)


@router.delete(
    "/{student_id}",
    response_model=StudentRead,
    status_code=status.HTTP_200_OK,
    summary="Deactivate student",
    description="Soft deletes a student by changing status to INACTIVE.",
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST))],
)
async def delete_student(
    student_id: int,
    session: AsyncSessionDependency,
    service: StudentService = Depends(get_student_service),
) -> Student:
    return await service.delete_student(session=session, student_id=student_id)
