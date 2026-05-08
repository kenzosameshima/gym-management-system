from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.database.session import AsyncSessionDependency
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: UserCreate,
    session: AsyncSessionDependency,
    service: AuthService = Depends(get_auth_service),
) -> User:
    return await service.register(session=session, payload=payload)


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
