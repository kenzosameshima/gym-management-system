from collections.abc import Sequence

from fastapi import APIRouter, Depends, status

from app.auth.permissions import require_roles
from app.database.session import AsyncSessionDependency
from app.models.student import Student
from app.models.user import UserRole
from app.schemas.student import StudentCreate, StudentRead, StudentUpdate
from app.services.student_service import StudentService, get_student_service

router = APIRouter(prefix="/api/students", tags=["students"])


@router.post(
    "",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
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
    response_model=list[StudentRead],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.INSTRUCTOR))
    ],
)
async def list_students(
    session: AsyncSessionDependency,
    service: StudentService = Depends(get_student_service),
) -> Sequence[Student]:
    return await service.list_students(session=session)


@router.get(
    "/{student_id}",
    response_model=StudentRead,
    status_code=status.HTTP_200_OK,
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
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST))],
)
async def delete_student(
    student_id: int,
    session: AsyncSessionDependency,
    service: StudentService = Depends(get_student_service),
) -> Student:
    return await service.delete_student(session=session, student_id=student_id)
