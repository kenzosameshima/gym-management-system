from datetime import timedelta

from fastapi import Depends, status
from sqlalchemy import select
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
            items=await self._to_enrollment_reads(session, list(enrollments)),
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_enrollment(self, session: AsyncSession, enrollment_id: int) -> EnrollmentRead:
        enrollment = await self._get_enrollment_model(session, enrollment_id)
        return (await self._to_enrollment_reads(session, [enrollment]))[0]

    async def _get_enrollment_model(
        self,
        session: AsyncSession,
        enrollment_id: int,
    ) -> Enrollment:
        enrollment = await self._repository.get_by_id(session, enrollment_id)
        if enrollment is None:
            raise self._not_found_error()
        return enrollment

    async def create_enrollment(
        self,
        session: AsyncSession,
        payload: EnrollmentCreate,
    ) -> EnrollmentRead:
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
            return (await self._to_enrollment_reads(session, [created_enrollment]))[0]
        except Exception:
            await session.rollback()
            raise

    async def update_enrollment(
        self,
        session: AsyncSession,
        enrollment_id: int,
        payload: EnrollmentUpdate,
    ) -> EnrollmentRead:
        enrollment = await self._get_enrollment_model(session, enrollment_id)
        updated_enrollment = await self._repository.update(session, enrollment, payload)
        await session.commit()
        await session.refresh(updated_enrollment)
        return (await self._to_enrollment_reads(session, [updated_enrollment]))[0]

    async def cancel_enrollment(self, session: AsyncSession, enrollment_id: int) -> EnrollmentRead:
        return await self.update_enrollment(
            session,
            enrollment_id,
            EnrollmentUpdate(status=EnrollmentStatus.CANCELLED),
        )

    async def _to_enrollment_reads(
        self,
        session: AsyncSession,
        enrollments: list[Enrollment],
    ) -> list[EnrollmentRead]:
        payment_statuses = await self._payment_statuses_by_enrollment_id(session, enrollments)
        return [
            EnrollmentRead.model_validate(
                {
                    "id": enrollment.id,
                    "student_id": enrollment.student_id,
                    "plan_id": enrollment.plan_id,
                    "start_date": enrollment.start_date,
                    "end_date": enrollment.end_date,
                    "status": enrollment.status,
                    "payment_status": payment_statuses.get(enrollment.id),
                    "created_at": enrollment.created_at,
                    "updated_at": enrollment.updated_at,
                }
            )
            for enrollment in enrollments
        ]

    async def _payment_statuses_by_enrollment_id(
        self,
        session: AsyncSession,
        enrollments: list[Enrollment],
    ) -> dict[int, PaymentStatus]:
        enrollment_ids = [enrollment.id for enrollment in enrollments]
        if not enrollment_ids:
            return {}

        result = await session.execute(
            select(Payment.enrollment_id, Payment.status).where(
                Payment.enrollment_id.in_(enrollment_ids),
            )
        )
        statuses_by_enrollment_id: dict[int, list[PaymentStatus]] = {}
        for row in result.all():
            statuses_by_enrollment_id.setdefault(row.enrollment_id, []).append(row.status)

        payment_statuses: dict[int, PaymentStatus] = {}
        for enrollment_id, statuses in statuses_by_enrollment_id.items():
            if PaymentStatus.OVERDUE in statuses:
                payment_statuses[enrollment_id] = PaymentStatus.OVERDUE
            elif PaymentStatus.PENDING in statuses:
                payment_statuses[enrollment_id] = PaymentStatus.PENDING
            else:
                payment_statuses[enrollment_id] = PaymentStatus.PAID
        return payment_statuses

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
