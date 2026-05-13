from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.models.user import User, UserAuditLog


class UserRepository:
    async def get_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        return await session.get(User, user_id)

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def has_active_role(self, session: AsyncSession, role: UserRole) -> bool:
        return await self.count_active_role(session, role) > 0

    async def count_active_role(self, session: AsyncSession, role: UserRole) -> int:
        statement = select(func.count()).select_from(User).where(
            User.role == role,
            User.is_active.is_(True),
        )
        result = await session.execute(statement)
        return result.scalar_one()

    async def list(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        role: UserRole | None = None,
        is_active: bool | None = True,
    ) -> tuple[Sequence[User], int]:
        statement = select(User)
        if role is not None:
            statement = statement.where(User.role == role)
        if is_active is not None:
            statement = statement.where(User.is_active.is_(is_active))

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
        must_change_password: bool = False,
    ) -> User:
        user = User(
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            role=role,
            must_change_password=must_change_password,
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    async def create_audit_log(
        self,
        session: AsyncSession,
        *,
        actor_user_id: int | None,
        target_user_id: int | None,
        action: str,
        details: str | None = None,
    ) -> UserAuditLog:
        log = UserAuditLog(
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            action=action,
            details=details,
        )
        session.add(log)
        await session.flush()
        await session.refresh(log)
        return log

    async def list_audit_logs(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        target_user_id: int | None = None,
    ) -> tuple[Sequence[UserAuditLog], int]:
        statement = select(UserAuditLog)
        if target_user_id is not None:
            statement = statement.where(UserAuditLog.target_user_id == target_user_id)

        total_result = await session.execute(select(func.count()).select_from(statement.subquery()))
        result = await session.execute(
            statement.order_by(UserAuditLog.created_at.desc(), UserAuditLog.id.desc())
            .limit(limit)
            .offset(offset),
        )
        return result.scalars().all(), total_result.scalar_one()

    async def update(
        self,
        session: AsyncSession,
        user: User,
        values: dict[str, object],
    ) -> User:
        for field, value in values.items():
            setattr(user, field, value)
        await session.flush()
        await session.refresh(user)
        return user


def get_user_repository() -> UserRepository:
    return UserRepository()
