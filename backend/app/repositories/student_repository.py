from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


class StudentRepository:
    async def list(self, session: AsyncSession) -> Sequence[Student]:
        result = await session.execute(select(Student).order_by(Student.id))
        return result.scalars().all()

    async def get_by_id(self, session: AsyncSession, student_id: int) -> Student | None:
        return await session.get(Student, student_id)

    async def get_by_cpf(self, session: AsyncSession, cpf: str) -> Student | None:
        result = await session.execute(select(Student).where(Student.cpf == cpf))
        return result.scalar_one_or_none()

    async def get_by_email(self, session: AsyncSession, email: str) -> Student | None:
        result = await session.execute(select(Student).where(Student.email == email))
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, payload: StudentCreate) -> Student:
        student = Student(**payload.model_dump())
        session.add(student)
        await session.flush()
        await session.refresh(student)
        return student

    async def update(
        self,
        session: AsyncSession,
        student: Student,
        payload: StudentUpdate,
    ) -> Student:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(student, field, value)
        await session.flush()
        await session.refresh(student)
        return student


def get_student_repository() -> StudentRepository:
    return StudentRepository()
