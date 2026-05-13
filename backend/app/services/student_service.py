from fastapi import Depends, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import EnrollmentStatus, FinancialStatus, PaymentStatus, StudentStatus
from app.core.exceptions import ApplicationError
from app.models.enrollment import Enrollment
from app.models.payment import Payment
from app.models.student import Student
from app.repositories.student_repository import StudentRepository, get_student_repository
from app.schemas.pagination import Page
from app.schemas.student import StudentCreate, StudentRead, StudentSearchResult, StudentUpdate


class StudentService:
    def __init__(self, repository: StudentRepository) -> None:
        self._repository = repository

    async def list_students(
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
    ) -> Page[StudentRead]:
        students, total = await self._repository.list(
            session,
            limit=limit,
            offset=offset,
            search=search,
            cpf=cpf,
            email=email,
            name=name,
            status=status,
        )
        student_items = list(students)
        return Page[StudentRead](
            items=await self._to_student_reads(session, student_items),
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_student(self, session: AsyncSession, student_id: int) -> StudentRead:
        student = await self._get_student_model(session, student_id)
        return (await self._to_student_reads(session, [student]))[0]

    async def search_students(
        self,
        session: AsyncSession,
        *,
        query: str,
        limit: int,
    ) -> list[StudentSearchResult]:
        students = list(await self._repository.search(session, query=query.strip(), limit=limit))
        student_reads = await self._to_student_reads(session, students)
        return [
            StudentSearchResult(
                id=student.id,
                name=student.name,
                cpf=student.cpf,
                phone=student.phone,
                email=student.email,
                status=student.status,
                financial_status=student.financial_status,
            )
            for student in student_reads
        ]

    async def _get_student_model(self, session: AsyncSession, student_id: int) -> Student:
        student = await self._repository.get_by_id(session, student_id)
        if student is None:
            raise self._not_found_error()
        return student

    async def create_student(self, session: AsyncSession, payload: StudentCreate) -> StudentRead:
        await self._ensure_unique_cpf(session, payload.cpf)
        await self._ensure_unique_email(session, payload.email)
        student = await self._repository.create(session, payload)
        await session.commit()
        await session.refresh(student)
        return (await self._to_student_reads(session, [student]))[0]

    async def update_student(
        self,
        session: AsyncSession,
        student_id: int,
        payload: StudentUpdate,
    ) -> StudentRead:
        student = await self._get_student_model(session, student_id)
        if payload.cpf is not None and payload.cpf != student.cpf:
            await self._ensure_unique_cpf(session, payload.cpf)
        if payload.email is not None and payload.email != student.email:
            await self._ensure_unique_email(session, payload.email)

        updated_student = await self._repository.update(session, student, payload)
        await session.commit()
        await session.refresh(updated_student)
        return (await self._to_student_reads(session, [updated_student]))[0]

    async def delete_student(self, session: AsyncSession, student_id: int) -> StudentRead:
        student = await self._get_student_model(session, student_id)
        updated_student = await self._repository.update(
            session,
            student,
            StudentUpdate(status=StudentStatus.INACTIVE),
        )
        await session.commit()
        await session.refresh(updated_student)
        return (await self._to_student_reads(session, [updated_student]))[0]

    async def _to_student_reads(
        self,
        session: AsyncSession,
        students: list[Student],
    ) -> list[StudentRead]:
        financial_statuses = await self._financial_statuses_by_student_id(session, students)
        return [
            StudentRead.model_validate(
                {
                    "id": student.id,
                    "name": student.name,
                    "cpf": student.cpf,
                    "birth_date": student.birth_date,
                    "phone": student.phone,
                    "email": student.email,
                    "address": student.address,
                    "status": student.status,
                    "financial_status": financial_statuses.get(
                        student.id,
                        FinancialStatus.INACTIVE
                        if student.status == StudentStatus.INACTIVE
                        else FinancialStatus.NO_ACTIVE_ENROLLMENT,
                    ),
                    "created_at": student.created_at,
                    "updated_at": student.updated_at,
                }
            )
            for student in students
        ]

    async def _financial_statuses_by_student_id(
        self,
        session: AsyncSession,
        students: list[Student],
    ) -> dict[int, FinancialStatus]:
        active_student_ids = [
            student.id for student in students if student.status == StudentStatus.ACTIVE
        ]
        statuses = {
            student.id: FinancialStatus.INACTIVE
            for student in students
            if student.status == StudentStatus.INACTIVE
        }
        if not active_student_ids:
            return statuses

        overdue_count = func.sum(case((Payment.status == PaymentStatus.OVERDUE, 1), else_=0))
        result = await session.execute(
            select(
                Enrollment.student_id,
                func.coalesce(overdue_count, 0).label("overdue_payments"),
            )
            .outerjoin(Payment, Payment.enrollment_id == Enrollment.id)
            .where(
                Enrollment.student_id.in_(active_student_ids),
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
            .group_by(Enrollment.student_id)
        )
        for row in result.all():
            statuses[row.student_id] = (
                FinancialStatus.DEFAULTER
                if row.overdue_payments > 0
                else FinancialStatus.IN_GOOD_STANDING
            )

        for student_id in active_student_ids:
            statuses.setdefault(student_id, FinancialStatus.NO_ACTIVE_ENROLLMENT)
        return statuses

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
