from datetime import date

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PaymentStatus
from app.core.exceptions import ApplicationError
from app.models.payment import Payment
from app.repositories.enrollment_repository import (
    EnrollmentRepository,
    get_enrollment_repository,
)
from app.repositories.payment_repository import PaymentRepository, get_payment_repository
from app.schemas.pagination import Page
from app.schemas.payment import PaymentCreate, PaymentRead, PaymentUpdate


class PaymentService:
    def __init__(
        self,
        repository: PaymentRepository,
        enrollment_repository: EnrollmentRepository,
    ) -> None:
        self._repository = repository
        self._enrollment_repository = enrollment_repository

    async def list_payments(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        enrollment_id: int | None = None,
        status_filter: PaymentStatus | None = None,
    ) -> Page[PaymentRead]:
        payments, total = await self._repository.list(
            session,
            limit=limit,
            offset=offset,
            enrollment_id=enrollment_id,
            status=status_filter,
        )
        return Page[PaymentRead](items=list(payments), total=total, limit=limit, offset=offset)

    async def get_payment(self, session: AsyncSession, payment_id: int) -> Payment:
        payment = await self._repository.get_by_id(session, payment_id)
        if payment is None:
            raise self._not_found_error()
        return payment

    async def create_payment(self, session: AsyncSession, payload: PaymentCreate) -> Payment:
        enrollment = await self._enrollment_repository.get_by_id(session, payload.enrollment_id)
        if enrollment is None:
            raise ApplicationError("ENROLLMENT_NOT_FOUND", "Enrollment was not found.", 404)
        payment = Payment(**payload.model_dump())
        try:
            created_payment = await self._repository.create(session, payment)
            await session.commit()
            await session.refresh(created_payment)
            return created_payment
        except Exception:
            await session.rollback()
            raise

    async def update_payment(
        self,
        session: AsyncSession,
        payment_id: int,
        payload: PaymentUpdate,
    ) -> Payment:
        payment = await self.get_payment(session, payment_id)
        try:
            updated_payment = await self._repository.update(session, payment, payload)
            await session.commit()
            await session.refresh(updated_payment)
            return updated_payment
        except Exception:
            await session.rollback()
            raise

    async def mark_payment_paid(self, session: AsyncSession, payment_id: int) -> Payment:
        return await self.update_payment(
            session,
            payment_id,
            PaymentUpdate(status=PaymentStatus.PAID, payment_date=date.today()),
        )

    @staticmethod
    def _not_found_error() -> ApplicationError:
        return ApplicationError(
            code="PAYMENT_NOT_FOUND",
            message="Payment was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


def get_payment_service(
    repository: PaymentRepository = Depends(get_payment_repository),
    enrollment_repository: EnrollmentRepository = Depends(get_enrollment_repository),
) -> PaymentService:
    return PaymentService(repository=repository, enrollment_repository=enrollment_repository)
