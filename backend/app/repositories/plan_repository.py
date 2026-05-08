from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PlanStatus
from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanUpdate


class PlanRepository:
    async def list(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        name: str | None = None,
        status: PlanStatus | None = None,
    ) -> tuple[Sequence[Plan], int]:
        statement = self._filtered_statement(name=name, status=status)
        total_result = await session.execute(select(func.count()).select_from(statement.subquery()))
        result = await session.execute(statement.order_by(Plan.id).limit(limit).offset(offset))
        return result.scalars().all(), total_result.scalar_one()

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

    def _filtered_statement(
        self,
        *,
        name: str | None,
        status: PlanStatus | None,
    ) -> Select[tuple[Plan]]:
        statement = select(Plan)
        if name:
            statement = statement.where(Plan.name.ilike(f"%{name}%"))
        if status is not None:
            statement = statement.where(Plan.status == status)
        return statement


def get_plan_repository() -> PlanRepository:
    return PlanRepository()
