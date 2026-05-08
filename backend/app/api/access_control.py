from fastapi import APIRouter, Depends, status

from app.auth.permissions import require_roles
from app.core.enums import UserRole
from app.database.session import AsyncSessionDependency
from app.schemas.access import AccessCheckRequest, AccessDecision
from app.services.access_control_service import (
    AccessControlService,
    get_access_control_service,
)

router = APIRouter(prefix="/api/access-control", tags=["access control"])


@router.post(
    "/check",
    response_model=AccessDecision,
    status_code=status.HTTP_200_OK,
    summary="Check student access by CPF",
    description=(
        "Delegates access calculation and audit logging to AccessControlService."
    ),
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST))],
)
async def check_access(
    payload: AccessCheckRequest,
    session: AsyncSessionDependency,
    service: AccessControlService = Depends(get_access_control_service),
) -> AccessDecision:
    return await service.can_access_by_cpf(cpf=payload.cpf, session=session)


@router.post(
    "/{student_id}/check",
    response_model=AccessDecision,
    status_code=status.HTTP_200_OK,
    summary="Check student access by id",
    description="Compatibility endpoint that delegates access calculation to AccessControlService.",
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST))],
)
async def check_access_by_id(
    student_id: int,
    session: AsyncSessionDependency,
    service: AccessControlService = Depends(get_access_control_service),
) -> AccessDecision:
    return await service.can_access(session=session, student_id=student_id)
