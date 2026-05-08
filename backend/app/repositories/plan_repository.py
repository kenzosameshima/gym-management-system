from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanUpdate


class PlanRepository:
    async def list(self, session: AsyncSession) -> Sequence[Plan]:
        result = await session.execute(select(Plan).order_by(Plan.id))
        return result.scalars().all()

    async def get_by_id(self, session: AsyncSession, plan_id: int) -> Plan | None:
        return await session.get(Plan, plan_id)

    async def get_by_name(self, session: AsyncSession, name: str) -> Plan | None:
        result = await session.execute(select(Plan).where(Plan.name == name))
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, payload: PlanCreate) -> Plan:
        plan = Plan(**payload.model_dump())
        session.add(plan)
        await session.flush()
        await session.refresh(plan)
        return plan

    async def update(self, session: AsyncSession, plan: Plan, payload: PlanUpdate) -> Plan:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(plan, field, value)
        await session.flush()
        await session.refresh(plan)
        return plan


def get_plan_repository() -> PlanRepository:
    return PlanRepository()
