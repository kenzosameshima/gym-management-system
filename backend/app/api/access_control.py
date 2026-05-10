from fastapi import APIRouter, Depends, Query, status

from app.auth.permissions import require_roles
from app.core.enums import UserRole
from app.database.session import AsyncSessionDependency
from app.schemas.access import AccessCheckRequest, AccessDecision, AccessLogRead
from app.schemas.pagination import Page
from app.services.access_control_service import (
    AccessControlService,
    get_access_control_service,
)

router = APIRouter(prefix="/api/access-control", tags=["access control"])
access_logs_router = APIRouter(prefix="/api/access", tags=["access control"])

ACCESS_MANAGEMENT_ROLES = (UserRole.ADMIN, UserRole.RECEPTIONIST)


@router.post(
    "/check",
    response_model=AccessDecision,
    status_code=status.HTTP_200_OK,
    summary="Check student access by CPF",
    description=(
        "Delegates access calculation and audit logging to AccessControlService."
    ),
    dependencies=[Depends(require_roles(*ACCESS_MANAGEMENT_ROLES))],
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
    dependencies=[Depends(require_roles(*ACCESS_MANAGEMENT_ROLES))],
)
async def check_access_by_id(
    student_id: int,
    session: AsyncSessionDependency,
    service: AccessControlService = Depends(get_access_control_service),
) -> AccessDecision:
    return await service.can_access(session=session, student_id=student_id)


@access_logs_router.get(
    "/logs",
    response_model=Page[AccessLogRead],
    status_code=status.HTTP_200_OK,
    summary="List access logs",
    description="Returns paginated access-check audit logs, newest first.",
    dependencies=[Depends(require_roles(*ACCESS_MANAGEMENT_ROLES))],
)
async def list_access_logs(
    session: AsyncSessionDependency,
    limit: int = Query(default=20, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
    service: AccessControlService = Depends(get_access_control_service),
) -> Page[AccessLogRead]:
    return await service.list_access_logs(
        session=session,
        limit=limit,
        offset=offset,
    )
