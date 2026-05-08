from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import EnrollmentStatus
from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentUpdate


class EnrollmentRepository:
    async def list(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        student_id: int | None = None,
        plan_id: int | None = None,
        status: EnrollmentStatus | None = None,
    ) -> tuple[Sequence[Enrollment], int]:
        statement = self._filtered_statement(student_id=student_id, plan_id=plan_id, status=status)
        total_result = await session.execute(select(func.count()).select_from(statement.subquery()))
        result = await session.execute(
            statement.order_by(Enrollment.id).limit(limit).offset(offset)
        )
        return result.scalars().all(), total_result.scalar_one()

    async def get_by_id(self, session: AsyncSession, enrollment_id: int) -> Enrollment | None:
        return await session.get(Enrollment, enrollment_id)

    async def get_active_by_student_id(
        self,
        session: AsyncSession,
        student_id: int,
    ) -> Enrollment | None:
        result = await session.execute(
            select(Enrollment)
            .where(
                Enrollment.student_id == student_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
            .order_by(Enrollment.end_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, enrollment: Enrollment) -> Enrollment:
        session.add(enrollment)
        await session.flush()
        await session.refresh(enrollment)
        return enrollment

    async def update(
        self,
        session: AsyncSession,
        enrollment: Enrollment,
        payload: EnrollmentUpdate,
    ) -> Enrollment:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(enrollment, field, value)
        await session.flush()
        await session.refresh(enrollment)
        return enrollment

    def _filtered_statement(
        self,
        *,
        student_id: int | None,
        plan_id: int | None,
        status: EnrollmentStatus | None,
    ) -> Select[tuple[Enrollment]]:
        statement = select(Enrollment)
        if student_id is not None:
            statement = statement.where(Enrollment.student_id == student_id)
        if plan_id is not None:
            statement = statement.where(Enrollment.plan_id == plan_id)
        if status is not None:
            statement = statement.where(Enrollment.status == status)
        return statement


def get_enrollment_repository() -> EnrollmentRepository:
    return EnrollmentRepository()
