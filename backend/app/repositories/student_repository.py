from collections.abc import Sequence

from sqlalchemy import Select, String, cast, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import StudentStatus
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


class StudentRepository:
    async def list(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        search: str | None = None,
        cpf: str | None = None,
        email: str | None = None,
        name: str | None = None,
        status: StudentStatus | None = None,
    ) -> tuple[Sequence[Student], int]:
        statement = self._filtered_statement(
            search=search,
            cpf=cpf,
            email=email,
            name=name,
            status=status,
        )
        total_result = await session.execute(select(func.count()).select_from(statement.subquery()))
        result = await session.execute(statement.order_by(Student.id).limit(limit).offset(offset))
        return result.scalars().all(), total_result.scalar_one()

    async def get_by_id(self, session: AsyncSession, student_id: int) -> Student | None:
        return await session.get(Student, student_id)

    async def get_by_cpf(self, session: AsyncSession, cpf: str) -> Student | None:
        result = await session.execute(select(Student).where(Student.cpf == cpf))
        return result.scalar_one_or_none()

    async def get_by_email(self, session: AsyncSession, email: str) -> Student | None:
        result = await session.execute(select(Student).where(Student.email == email))
        return result.scalar_one_or_none()

    async def search(self, session: AsyncSession, *, query: str, limit: int) -> Sequence[Student]:
        term = f"%{query}%"
        enrollment_match = exists(
            select(Enrollment.id).where(
                Enrollment.student_id == Student.id,
                cast(Enrollment.id, String).ilike(term),
            )
        )
        statement = (
            select(Student)
            .where(
                or_(
                    Student.name.ilike(term),
                    Student.cpf.ilike(term),
                    Student.phone.ilike(term),
                    Student.email.ilike(term),
                    enrollment_match,
                )
            )
            .order_by(Student.name, Student.id)
            .limit(limit)
        )
        result = await session.execute(statement)
        return result.scalars().all()

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

    def _filtered_statement(
        self,
        *,
        search: str | None,
        cpf: str | None,
        email: str | None,
        name: str | None,
        status: StudentStatus | None,
    ) -> Select[tuple[Student]]:
        statement = select(Student)
        if search:
            term = f"%{search}%"
            statement = statement.where(
                or_(
                    Student.name.ilike(term),
                    Student.cpf.ilike(term),
                    Student.email.ilike(term),
                )
            )
        if cpf:
            statement = statement.where(Student.cpf == cpf)
        if email:
            statement = statement.where(Student.email == email)
        if name:
            statement = statement.where(Student.name.ilike(f"%{name}%"))
        if status is not None:
            statement = statement.where(Student.status == status)
        return statement


def get_student_repository() -> StudentRepository:
    return StudentRepository()
