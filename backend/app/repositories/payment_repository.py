from collections.abc import Sequence
from datetime import date

from sqlalchemy import Select, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PaymentStatus
from app.models.enrollment import Enrollment
from app.models.payment import Payment
from app.models.student import Student
from app.schemas.payment import PaymentUpdate


class PaymentRepository:
    async def list(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        enrollment_id: int | None = None,
        status: PaymentStatus | None = None,
        student_search: str | None = None,
    ) -> tuple[Sequence[Payment], int]:
        statement = self._filtered_statement(
            enrollment_id=enrollment_id,
            status=status,
            student_search=student_search,
        )
        total_result = await session.execute(select(func.count()).select_from(statement.subquery()))
        result = await session.execute(statement.order_by(Payment.id).limit(limit).offset(offset))
        return result.scalars().all(), total_result.scalar_one()

    async def get_by_id(self, session: AsyncSession, payment_id: int) -> Payment | None:
        return await session.get(Payment, payment_id)

    async def create(self, session: AsyncSession, payment: Payment) -> Payment:
        session.add(payment)
        await session.flush()
        await session.refresh(payment)
        return payment

    async def update(
        self,
        session: AsyncSession,
        payment: Payment,
        payload: PaymentUpdate,
    ) -> Payment:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(payment, field, value)
        await session.flush()
        await session.refresh(payment)
        return payment

    async def has_overdue_for_student(self, session: AsyncSession, student_id: int) -> bool:
        result = await session.execute(
            select(Payment.id)
            .join(Enrollment, Payment.enrollment_id == Enrollment.id)
            .where(Enrollment.student_id == student_id, Payment.status == PaymentStatus.OVERDUE)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def has_overdue_for_enrollment(
        self,
        session: AsyncSession,
        enrollment_id: int,
    ) -> bool:
        result = await session.execute(
            select(Payment.id)
            .where(
                Payment.enrollment_id == enrollment_id,
                Payment.status == PaymentStatus.OVERDUE,
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def mark_overdue_for_student(
        self,
        session: AsyncSession,
        *,
        student_id: int,
        today: date,
    ) -> None:
        enrollment_ids = select(Enrollment.id).where(Enrollment.student_id == student_id)
        await session.execute(
            update(Payment)
            .where(
                Payment.enrollment_id.in_(enrollment_ids),
                Payment.status == PaymentStatus.PENDING,
                Payment.due_date < today,
            )
            .values(status=PaymentStatus.OVERDUE)
        )

    async def mark_overdue_for_enrollment(
        self,
        session: AsyncSession,
        *,
        enrollment_id: int,
        today: date,
    ) -> None:
        await session.execute(
            update(Payment)
            .where(
                Payment.enrollment_id == enrollment_id,
                Payment.status == PaymentStatus.PENDING,
                Payment.due_date < today,
            )
            .values(status=PaymentStatus.OVERDUE)
        )

    def _filtered_statement(
        self,
        *,
        enrollment_id: int | None,
        status: PaymentStatus | None,
        student_search: str | None,
    ) -> Select[tuple[Payment]]:
        statement = select(Payment)
        if enrollment_id is not None:
            statement = statement.where(Payment.enrollment_id == enrollment_id)
        if status is not None:
            statement = statement.where(Payment.status == status)
        if student_search:
            term = f"%{student_search}%"
            statement = (
                statement.join(Enrollment, Enrollment.id == Payment.enrollment_id)
                .join(Student, Student.id == Enrollment.student_id)
                .where(
                    or_(
                        Student.name.ilike(term),
                        Student.cpf.ilike(term),
                        Student.email.ilike(term),
                    )
                )
            )
        return statement


def get_payment_repository() -> PaymentRepository:
    return PaymentRepository()
