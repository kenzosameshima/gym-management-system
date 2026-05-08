import structlog
from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApplicationError
from app.repositories.health_repository import HealthRepository, get_health_repository
from app.schemas.health import ReadyHealthResponse

logger = structlog.get_logger(__name__)


class HealthService:
    def __init__(self, repository: HealthRepository) -> None:
        self._repository = repository

    async def check_readiness(self, session: AsyncSession) -> ReadyHealthResponse:
        try:
            is_connected = await self._repository.ping_database(session)
        except Exception as exc:
            logger.exception("database_connection_failed")
            raise ApplicationError(
                code="DATABASE_UNAVAILABLE",
                message="Database connection is unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ) from exc

        if not is_connected:
            logger.error("database_connection_invalid")
            raise ApplicationError(
                code="DATABASE_UNAVAILABLE",
                message="Database connection is unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        logger.info("database_connection_ok")
        return ReadyHealthResponse(status="ready", database="connected")


def get_health_service(
    repository: HealthRepository = Depends(get_health_repository),
) -> HealthService:
    return HealthService(repository=repository)
