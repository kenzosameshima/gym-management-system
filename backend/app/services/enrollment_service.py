from datetime import timedelta

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import EnrollmentStatus, PaymentStatus, PlanStatus, StudentStatus
from app.core.exceptions import ApplicationError
from app.models.enrollment import Enrollment
from app.models.payment import Payment
from app.repositories.enrollment_repository import (
    EnrollmentRepository,
    get_enrollment_repository,
)
from app.repositories.payment_repository import PaymentRepository, get_payment_repository
from app.repositories.plan_repository import PlanRepository, get_plan_repository
from app.repositories.student_repository import StudentRepository, get_student_repository
from app.schemas.enrollment import EnrollmentCreate, EnrollmentRead, EnrollmentUpdate
from app.schemas.pagination import Page


class EnrollmentService:
    def __init__(
        self,
        repository: EnrollmentRepository,
        student_repository: StudentRepository,
        plan_repository: PlanRepository,
        payment_repository: PaymentRepository,
    ) -> None:
        self._repository = repository
        self._student_repository = student_repository
        self._plan_repository = plan_repository
        self._payment_repository = payment_repository

    async def list_enrollments(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        student_id: int | None = None,
        plan_id: int | None = None,
        status: EnrollmentStatus | None = None,
        student_search: str | None = None,
    ) -> Page[EnrollmentRead]:
        enrollments, total = await self._repository.list(
            session,
            limit=limit,
            offset=offset,
            student_id=student_id,
            plan_id=plan_id,
            status=status,
            student_search=student_search,
        )
        return Page[EnrollmentRead](
            items=list(enrollments),
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_enrollment(self, session: AsyncSession, enrollment_id: int) -> Enrollment:
        enrollment = await self._repository.get_by_id(session, enrollment_id)
        if enrollment is None:
            raise self._not_found_error()
        return enrollment

    async def create_enrollment(
        self,
        session: AsyncSession,
        payload: EnrollmentCreate,
    ) -> Enrollment:
        student = await self._student_repository.get_by_id(session, payload.student_id)
        if student is None:
            raise ApplicationError("STUDENT_NOT_FOUND", "Student was not found.", 404)
        if student.status != StudentStatus.ACTIVE:
            raise ApplicationError("STUDENT_INACTIVE", "Student is inactive.", 409)

        plan = await self._plan_repository.get_by_id(session, payload.plan_id)
        if plan is None:
            raise ApplicationError("PLAN_NOT_FOUND", "Plan was not found.", 404)
        if plan.status != PlanStatus.ACTIVE:
            raise ApplicationError("PLAN_INACTIVE", "Plan is inactive.", 409)

        active_enrollment = await self._repository.get_active_by_student_id(
            session,
            payload.student_id,
        )
        if active_enrollment is not None and active_enrollment.end_date >= payload.start_date:
            raise ApplicationError(
                "ACTIVE_ENROLLMENT_ALREADY_EXISTS",
                "Student already has an active enrollment.",
                status.HTTP_409_CONFLICT,
            )

        end_date = payload.start_date + timedelta(days=plan.duration_days)
        enrollment = Enrollment(
            student_id=payload.student_id,
            plan_id=payload.plan_id,
            start_date=payload.start_date,
            end_date=end_date,
            status=EnrollmentStatus.ACTIVE,
        )

        try:
            # Transaction boundary: enrollment and first payment are persisted atomically.
            if active_enrollment is not None:
                await self._repository.update(
                    session,
                    active_enrollment,
                    EnrollmentUpdate(status=EnrollmentStatus.EXPIRED),
                )
            created_enrollment = await self._repository.create(session, enrollment)
            first_payment = Payment(
                enrollment_id=created_enrollment.id,
                amount=plan.price,
                due_date=payload.first_payment_due_date or payload.start_date,
                status=PaymentStatus.PENDING,
            )
            await self._payment_repository.create(session, first_payment)
            await session.commit()
            await session.refresh(created_enrollment)
            return created_enrollment
        except Exception:
            await session.rollback()
            raise

    async def update_enrollment(
        self,
        session: AsyncSession,
        enrollment_id: int,
        payload: EnrollmentUpdate,
    ) -> Enrollment:
        enrollment = await self.get_enrollment(session, enrollment_id)
        updated_enrollment = await self._repository.update(session, enrollment, payload)
        await session.commit()
        await session.refresh(updated_enrollment)
        return updated_enrollment

    async def cancel_enrollment(self, session: AsyncSession, enrollment_id: int) -> Enrollment:
        return await self.update_enrollment(
            session,
            enrollment_id,
            EnrollmentUpdate(status=EnrollmentStatus.CANCELLED),
        )

    @staticmethod
    def _not_found_error() -> ApplicationError:
        return ApplicationError(
            code="ENROLLMENT_NOT_FOUND",
            message="Enrollment was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


def get_enrollment_service(
    repository: EnrollmentRepository = Depends(get_enrollment_repository),
    student_repository: StudentRepository = Depends(get_student_repository),
    plan_repository: PlanRepository = Depends(get_plan_repository),
    payment_repository: PaymentRepository = Depends(get_payment_repository),
) -> EnrollmentService:
    return EnrollmentService(
        repository=repository,
        student_repository=student_repository,
        plan_repository=plan_repository,
        payment_repository=payment_repository,
    )
