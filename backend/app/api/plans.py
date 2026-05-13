from fastapi import APIRouter, Depends, Query, status

from app.auth.permissions import require_roles
from app.core.enums import PlanStatus, UserRole
from app.database.session import AsyncSessionDependency
from app.models.plan import Plan
from app.schemas.pagination import Page
from app.schemas.plan import PlanCreate, PlanRead, PlanUpdate
from app.services.plan_service import PlanService, get_plan_service

router = APIRouter(prefix="/api/plans", tags=["plans"])

PLAN_READ_ROLES = (UserRole.ADMIN, UserRole.RECEPTIONIST)
PLAN_WRITE_ROLES = (UserRole.ADMIN,)


@router.post(
    "",
    response_model=PlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create plan",
    description="Creates a gym plan after validating unique plan name.",
    dependencies=[Depends(require_roles(*PLAN_WRITE_ROLES))],
)
async def create_plan(
    payload: PlanCreate,
    session: AsyncSessionDependency,
    service: PlanService = Depends(get_plan_service),
) -> Plan:
    return await service.create_plan(session=session, payload=payload)


@router.get(
    "",
    response_model=Page[PlanRead],
    status_code=status.HTTP_200_OK,
    summary="List plans",
    description="Returns a paginated plan list with optional name filtering.",
    dependencies=[Depends(require_roles(*PLAN_READ_ROLES))],
)
async def list_plans(
    session: AsyncSessionDependency,
    limit: int = Query(default=20, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
    name: str | None = Query(default=None, min_length=1, max_length=255),
    plan_status: PlanStatus | None = Query(default=None, alias="status"),
    service: PlanService = Depends(get_plan_service),
) -> Page[PlanRead]:
    return await service.list_plans(
        session=session,
        limit=limit,
        offset=offset,
        name=name,
        status=plan_status,
    )


@router.get(
    "/{plan_id}",
    response_model=PlanRead,
    status_code=status.HTTP_200_OK,
    summary="Get plan",
    description="Returns one plan by id.",
    dependencies=[Depends(require_roles(*PLAN_READ_ROLES))],
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
    summary="Update plan",
    description="Updates plan data after validating unique plan name.",
    dependencies=[Depends(require_roles(*PLAN_WRITE_ROLES))],
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
    summary="Deactivate plan",
    description="Soft deletes a plan by changing status to INACTIVE.",
    dependencies=[Depends(require_roles(*PLAN_WRITE_ROLES))],
)
async def delete_plan(
    plan_id: int,
    session: AsyncSessionDependency,
    service: PlanService = Depends(get_plan_service),
) -> Plan:
    return await service.delete_plan(session=session, plan_id=plan_id)
