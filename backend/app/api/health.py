from fastapi import APIRouter, Depends, status

from app.database.session import AsyncSessionDependency
from app.schemas.health import LiveHealthResponse, ReadyHealthResponse
from app.services.health_service import HealthService, get_health_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/live",
    response_model=LiveHealthResponse,
    status_code=status.HTTP_200_OK,
)
async def live() -> LiveHealthResponse:
    return LiveHealthResponse(status="alive")


@router.get(
    "/ready",
    response_model=ReadyHealthResponse,
    status_code=status.HTTP_200_OK,
)
async def ready(
    session: AsyncSessionDependency,
    service: HealthService = Depends(get_health_service),
) -> ReadyHealthResponse:
    return await service.check_readiness(session=session)
