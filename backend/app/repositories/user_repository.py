from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.models.user import User


class UserRepository:
    async def get_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        return await session.get(User, user_id)

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def list(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        role: UserRole | None = None,
        active_only: bool = True,
    ) -> tuple[Sequence[User], int]:
        statement = select(User)
        if role is not None:
            statement = statement.where(User.role == role)
        if active_only:
            statement = statement.where(User.is_active.is_(True))

        total_result = await session.execute(select(func.count()).select_from(statement.subquery()))
        result = await session.execute(
            statement.order_by(User.full_name).limit(limit).offset(offset),
        )
        return result.scalars().all(), total_result.scalar_one()

    async def create(
        self,
        session: AsyncSession,
        email: str,
        full_name: str,
        password_hash: str,
        role: UserRole,
    ) -> User:
        user = User(
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            role=role,
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user


def get_user_repository() -> UserRepository:
    return UserRepository()
