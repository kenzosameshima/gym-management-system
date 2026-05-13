from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.core.exceptions import ApplicationError
from app.database.session import AsyncSessionDependency
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserPasswordChange, UserRead
from app.services.auth_service import AuthService, get_auth_service
from app.services.user_service import UserService, get_user_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_410_GONE,
)
async def register() -> None:
    raise ApplicationError(
        code="PUBLIC_REGISTRATION_DISABLED",
        message=(
            "Public registration is disabled. "
            "Administrators must manage users through /api/users."
        ),
        status_code=status.HTTP_410_GONE,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    payload: LoginRequest,
    session: AsyncSessionDependency,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await service.login(session=session, payload=payload)


@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post(
    "/change-password",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def change_password(
    payload: UserPasswordChange,
    session: AsyncSessionDependency,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> User:
    return await service.change_password(
        session=session,
        current_user=current_user,
        payload=payload,
    )
