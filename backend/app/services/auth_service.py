from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.auth.password import hash_password, verify_password
from app.core.exceptions import ApplicationError
from app.models.user import User
from app.repositories.user_repository import UserRepository, get_user_repository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def register(self, session: AsyncSession, payload: UserCreate) -> User:
        existing_user = await self._repository.get_by_email(session, payload.email)
        if existing_user is not None:
            raise ApplicationError(
                code="EMAIL_ALREADY_REGISTERED",
                message="Email is already registered.",
                status_code=status.HTTP_409_CONFLICT,
            )

        user = await self._repository.create(
            session=session,
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
            role=payload.role,
        )
        await session.commit()
        await session.refresh(user)
        return user

    async def login(self, session: AsyncSession, payload: LoginRequest) -> TokenResponse:
        user = await self._repository.get_by_email(session, payload.email)
        if user is None or not user.is_active:
            raise self._invalid_credentials_error()

        if not verify_password(payload.password, user.password_hash):
            raise self._invalid_credentials_error()

        return TokenResponse(access_token=create_access_token(subject=str(user.id)))

    @staticmethod
    def _invalid_credentials_error() -> ApplicationError:
        return ApplicationError(
            code="INVALID_CREDENTIALS",
            message="Invalid email or password.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository=repository)
