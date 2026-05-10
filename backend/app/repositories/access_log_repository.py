from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AccessDeniedReason
from app.models.access_log import AccessLog


class AccessLogRepository:
    async def create(
        self,
        session: AsyncSession,
        *,
        student_id: int | None,
        cpf_attempted: str,
        allowed: bool,
        reason: AccessDeniedReason | None,
    ) -> AccessLog:
        access_log = AccessLog(
            student_id=student_id,
            cpf_attempted=cpf_attempted,
            allowed=allowed,
            reason=reason,
        )
        session.add(access_log)
        await session.flush()
        await session.refresh(access_log)
        return access_log

    async def list(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[AccessLog], int]:
        total = await session.scalar(select(func.count()).select_from(AccessLog))
        result = await session.execute(
            select(AccessLog)
            .order_by(AccessLog.accessed_at.desc(), AccessLog.id.desc())
            .limit(limit)
            .offset(offset),
        )
        return list(result.scalars().all()), total or 0


def get_access_log_repository() -> AccessLogRepository:
    return AccessLogRepository()
