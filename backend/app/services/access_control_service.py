from datetime import date

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AccessDeniedReason, EnrollmentStatus, StudentStatus
from app.repositories.access_log_repository import (
    AccessLogRepository,
    get_access_log_repository,
)
from app.repositories.enrollment_repository import (
    EnrollmentRepository,
    get_enrollment_repository,
)
from app.repositories.payment_repository import PaymentRepository, get_payment_repository
from app.repositories.student_repository import StudentRepository, get_student_repository
from app.schemas.access import AccessDecision
from app.schemas.enrollment import EnrollmentUpdate


class AccessControlService:
    def __init__(
        self,
        student_repository: StudentRepository,
        enrollment_repository: EnrollmentRepository,
        payment_repository: PaymentRepository,
        access_log_repository: AccessLogRepository,
    ) -> None:
        self._student_repository = student_repository
        self._enrollment_repository = enrollment_repository
        self._payment_repository = payment_repository
        self._access_log_repository = access_log_repository

    async def can_access_by_cpf(self, cpf: str, session: AsyncSession) -> AccessDecision:
        today = date.today()
        student = await self._student_repository.get_by_cpf(session, cpf)
        student_id = student.id if student is not None else None
        allowed = False
        reason: AccessDeniedReason | None

        try:
            if student is None:
                reason = AccessDeniedReason.STUDENT_NOT_FOUND
            elif student.status != StudentStatus.ACTIVE:
                reason = AccessDeniedReason.STUDENT_INACTIVE
            else:
                enrollment = await self._enrollment_repository.get_active_by_student_id(
                    session,
                    student.id,
                )
                if enrollment is None:
                    reason = AccessDeniedReason.NO_ACTIVE_ENROLLMENT
                elif enrollment.status != EnrollmentStatus.ACTIVE:
                    reason = AccessDeniedReason.NO_ACTIVE_ENROLLMENT
                elif enrollment.end_date < today:
                    await self._enrollment_repository.update(
                        session,
                        enrollment,
                        EnrollmentUpdate(status=EnrollmentStatus.EXPIRED),
                    )
                    reason = AccessDeniedReason.ENROLLMENT_EXPIRED
                else:
                    await self._payment_repository.mark_overdue_for_enrollment(
                        session,
                        enrollment_id=enrollment.id,
                        today=today,
                    )
                    has_overdue = await self._payment_repository.has_overdue_for_enrollment(
                        session,
                        enrollment.id,
                    )
                    if has_overdue:
                        reason = AccessDeniedReason.PAYMENT_OVERDUE
                    else:
                        allowed = True
                        reason = None

            await self._access_log_repository.create(
                session,
                student_id=student_id,
                cpf_attempted=cpf,
                allowed=allowed,
                reason=reason,
            )
            await session.commit()
            return AccessDecision(
                student_id=student_id,
                cpf_attempted=cpf,
                allowed=allowed,
                reason=reason,
            )
        except Exception:
            await session.rollback()
            raise

    async def can_access(self, session: AsyncSession, student_id: int) -> AccessDecision:
        student = await self._student_repository.get_by_id(session, student_id)
        if student is None:
            return await self._check_missing_student_by_id(session=session, student_id=student_id)
        return await self.can_access_by_cpf(cpf=student.cpf, session=session)

    async def _check_missing_student_by_id(
        self,
        *,
        session: AsyncSession,
        student_id: int,
    ) -> AccessDecision:
        cpf_attempted = str(student_id)
        reason = AccessDeniedReason.STUDENT_NOT_FOUND
        try:
            await self._access_log_repository.create(
                session,
                student_id=None,
                cpf_attempted=cpf_attempted,
                allowed=False,
                reason=reason,
            )
            await session.commit()
            return AccessDecision(
                student_id=None,
                cpf_attempted=cpf_attempted,
                allowed=False,
                reason=reason,
            )
        except Exception:
            await session.rollback()
            raise


def get_access_control_service(
    student_repository: StudentRepository = Depends(get_student_repository),
    enrollment_repository: EnrollmentRepository = Depends(get_enrollment_repository),
    payment_repository: PaymentRepository = Depends(get_payment_repository),
    access_log_repository: AccessLogRepository = Depends(get_access_log_repository),
) -> AccessControlService:
    return AccessControlService(
        student_repository=student_repository,
        enrollment_repository=enrollment_repository,
        payment_repository=payment_repository,
        access_log_repository=access_log_repository,
    )
