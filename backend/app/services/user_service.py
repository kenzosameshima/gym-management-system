from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserRole
from app.core.exceptions import ApplicationError
from app.models.user import User
from app.repositories.user_repository import UserRepository, get_user_repository
from app.schemas.pagination import Page
from app.schemas.user import UserRead


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def get_active_user_by_id(self, session: AsyncSession, user_id: int) -> User:
        user = await self._repository.get_by_id(session, user_id)
        if user is None or not user.is_active:
            raise ApplicationError(
                code="UNAUTHORIZED",
                message="Invalid authentication credentials.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        return user

    async def list_users(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        role: UserRole | None,
    ) -> Page[UserRead]:
        users, total = await self._repository.list(
            session,
            limit=limit,
            offset=offset,
            role=role,
        )
        return Page[UserRead](
            items=list(users),
            total=total,
            limit=limit,
            offset=offset,
        )


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository=repository)
