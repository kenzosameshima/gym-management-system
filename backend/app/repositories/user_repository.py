from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


class UserRepository:
    async def get_by_id(self, session: AsyncSession, user_id: int) -> User | None:
        return await session.get(User, user_id)

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

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
