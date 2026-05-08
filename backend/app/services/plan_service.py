from collections.abc import Sequence

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApplicationError
from app.models.plan import Plan, PlanStatus
from app.repositories.plan_repository import PlanRepository, get_plan_repository
from app.schemas.plan import PlanCreate, PlanUpdate


class PlanService:
    def __init__(self, repository: PlanRepository) -> None:
        self._repository = repository

    async def list_plans(self, session: AsyncSession) -> Sequence[Plan]:
        return await self._repository.list(session)

    async def get_plan(self, session: AsyncSession, plan_id: int) -> Plan:
        plan = await self._repository.get_by_id(session, plan_id)
        if plan is None:
            raise self._not_found_error()
        return plan

    async def create_plan(self, session: AsyncSession, payload: PlanCreate) -> Plan:
        await self._ensure_unique_name(session, payload.name)
        plan = await self._repository.create(session, payload)
        await session.commit()
        await session.refresh(plan)
        return plan

    async def update_plan(self, session: AsyncSession, plan_id: int, payload: PlanUpdate) -> Plan:
        plan = await self.get_plan(session, plan_id)
        if payload.name is not None and payload.name != plan.name:
            await self._ensure_unique_name(session, payload.name)

        updated_plan = await self._repository.update(session, plan, payload)
        await session.commit()
        await session.refresh(updated_plan)
        return updated_plan

    async def delete_plan(self, session: AsyncSession, plan_id: int) -> Plan:
        plan = await self.get_plan(session, plan_id)
        updated_plan = await self._repository.update(
            session,
            plan,
            PlanUpdate(status=PlanStatus.INACTIVE),
        )
        await session.commit()
        await session.refresh(updated_plan)
        return updated_plan

    async def _ensure_unique_name(self, session: AsyncSession, name: str) -> None:
        if await self._repository.get_by_name(session, name) is not None:
            raise ApplicationError(
                code="PLAN_NAME_ALREADY_REGISTERED",
                message="Plan name is already registered.",
                status_code=status.HTTP_409_CONFLICT,
            )

    @staticmethod
    def _not_found_error() -> ApplicationError:
        return ApplicationError(
            code="PLAN_NOT_FOUND",
            message="Plan was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


def get_plan_service(
    repository: PlanRepository = Depends(get_plan_repository),
) -> PlanService:
    return PlanService(repository=repository)
