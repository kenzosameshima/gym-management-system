from collections.abc import Sequence

from fastapi import APIRouter, Depends, status

from app.auth.permissions import require_roles
from app.database.session import AsyncSessionDependency
from app.models.plan import Plan
from app.models.user import UserRole
from app.schemas.plan import PlanCreate, PlanRead, PlanUpdate
from app.services.plan_service import PlanService, get_plan_service

router = APIRouter(prefix="/api/plans", tags=["plans"])

PLAN_MANAGEMENT_ROLES = (UserRole.ADMIN, UserRole.RECEPTIONIST)


@router.post(
    "",
    response_model=PlanRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(*PLAN_MANAGEMENT_ROLES))],
)
async def create_plan(
    payload: PlanCreate,
    session: AsyncSessionDependency,
    service: PlanService = Depends(get_plan_service),
) -> Plan:
    return await service.create_plan(session=session, payload=payload)


@router.get(
    "",
    response_model=list[PlanRead],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*PLAN_MANAGEMENT_ROLES))],
)
async def list_plans(
    session: AsyncSessionDependency,
    service: PlanService = Depends(get_plan_service),
) -> Sequence[Plan]:
    return await service.list_plans(session=session)


@router.get(
    "/{plan_id}",
    response_model=PlanRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*PLAN_MANAGEMENT_ROLES))],
)
async def get_plan(
    plan_id: int,
    session: AsyncSessionDependency,
    service: PlanService = Depends(get_plan_service),
) -> Plan:
    return await service.get_plan(session=session, plan_id=plan_id)


@router.put(
    "/{plan_id}",
    response_model=PlanRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*PLAN_MANAGEMENT_ROLES))],
)
async def update_plan(
    plan_id: int,
    payload: PlanUpdate,
    session: AsyncSessionDependency,
    service: PlanService = Depends(get_plan_service),
) -> Plan:
    return await service.update_plan(session=session, plan_id=plan_id, payload=payload)


@router.delete(
    "/{plan_id}",
    response_model=PlanRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(*PLAN_MANAGEMENT_ROLES))],
)
async def delete_plan(
    plan_id: int,
    session: AsyncSessionDependency,
    service: PlanService = Depends(get_plan_service),
) -> Plan:
    return await service.delete_plan(session=session, plan_id=plan_id)
