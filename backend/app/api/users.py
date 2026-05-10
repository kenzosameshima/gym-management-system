from fastapi import APIRouter, Depends, Query, status

from app.auth.permissions import require_roles
from app.core.enums import UserRole
from app.database.session import AsyncSessionDependency
from app.schemas.pagination import Page
from app.schemas.user import UserRead
from app.services.user_service import UserService, get_user_service

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get(
    "",
    response_model=Page[UserRead],
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="Returns active users with optional role filtering.",
    dependencies=[
        Depends(require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.INSTRUCTOR))
    ],
)
async def list_users(
    session: AsyncSessionDependency,
    limit: int = Query(default=20, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
    role: UserRole | None = Query(default=None),
    service: UserService = Depends(get_user_service),
) -> Page[UserRead]:
    return await service.list_users(
        session=session,
        limit=limit,
        offset=offset,
        role=role,
    )
