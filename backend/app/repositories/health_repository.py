from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class HealthRepository:
    async def ping_database(self, session: AsyncSession) -> bool:
        result = await session.execute(text("SELECT 1"))
        return bool(result.scalar_one() == 1)


def get_health_repository() -> HealthRepository:
    return HealthRepository()
