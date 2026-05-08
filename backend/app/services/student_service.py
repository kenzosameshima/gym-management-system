from collections.abc import Sequence

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApplicationError
from app.models.student import Student, StudentStatus
from app.repositories.student_repository import StudentRepository, get_student_repository
from app.schemas.student import StudentCreate, StudentUpdate


class StudentService:
    def __init__(self, repository: StudentRepository) -> None:
        self._repository = repository

    async def list_students(self, session: AsyncSession) -> Sequence[Student]:
        return await self._repository.list(session)

    async def get_student(self, session: AsyncSession, student_id: int) -> Student:
        student = await self._repository.get_by_id(session, student_id)
        if student is None:
            raise self._not_found_error()
        return student

    async def create_student(self, session: AsyncSession, payload: StudentCreate) -> Student:
        await self._ensure_unique_cpf(session, payload.cpf)
        await self._ensure_unique_email(session, payload.email)
        student = await self._repository.create(session, payload)
        await session.commit()
        await session.refresh(student)
        return student

    async def update_student(
        self,
        session: AsyncSession,
        student_id: int,
        payload: StudentUpdate,
    ) -> Student:
        student = await self.get_student(session, student_id)
        if payload.cpf is not None and payload.cpf != student.cpf:
            await self._ensure_unique_cpf(session, payload.cpf)
        if payload.email is not None and payload.email != student.email:
            await self._ensure_unique_email(session, payload.email)

        updated_student = await self._repository.update(session, student, payload)
        await session.commit()
        await session.refresh(updated_student)
        return updated_student

    async def delete_student(self, session: AsyncSession, student_id: int) -> Student:
        student = await self.get_student(session, student_id)
        updated_student = await self._repository.update(
            session,
            student,
            StudentUpdate(status=StudentStatus.INACTIVE),
        )
        await session.commit()
        await session.refresh(updated_student)
        return updated_student

    async def _ensure_unique_cpf(self, session: AsyncSession, cpf: str) -> None:
        if await self._repository.get_by_cpf(session, cpf) is not None:
            raise ApplicationError(
                code="CPF_ALREADY_REGISTERED",
                message="CPF is already registered.",
                status_code=status.HTTP_409_CONFLICT,
            )

    async def _ensure_unique_email(self, session: AsyncSession, email: str) -> None:
        if await self._repository.get_by_email(session, email) is not None:
            raise ApplicationError(
                code="STUDENT_EMAIL_ALREADY_REGISTERED",
                message="Student email is already registered.",
                status_code=status.HTTP_409_CONFLICT,
            )

    @staticmethod
    def _not_found_error() -> ApplicationError:
        return ApplicationError(
            code="STUDENT_NOT_FOUND",
            message="Student was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


def get_student_service(
    repository: StudentRepository = Depends(get_student_repository),
) -> StudentService:
    return StudentService(repository=repository)
