from fastapi import APIRouter, Depends, Query, status

from app.auth.dependencies import get_current_user
from app.auth.permissions import require_roles
from app.core.enums import UserRole
from app.database.session import AsyncSessionDependency
from app.models.user import User
from app.schemas.pagination import Page
from app.schemas.user import UserAuditLogRead, UserCreate, UserPasswordReset, UserRead, UserUpdate
from app.services.user_service import UserService, get_user_service

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get(
    "",
    response_model=Page[UserRead],
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="Returns users with optional role and active-status filtering.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def list_users(
    session: AsyncSessionDependency,
    limit: int = Query(default=20, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
    role: UserRole | None = Query(default=None),
    is_active: bool | None = Query(default=True),
    service: UserService = Depends(get_user_service),
) -> Page[UserRead]:
    return await service.list_users(
        session=session,
        limit=limit,
        offset=offset,
        role=role,
        is_active=is_active,
    )


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Creates an active system user. Only administrators can create staff users.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def create_user(
    payload: UserCreate,
    session: AsyncSessionDependency,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> User:
    return await service.create_user(
        session=session,
        payload=payload,
        current_user_id=current_user.id,
    )


@router.get(
    "/audit",
    response_model=Page[UserAuditLogRead],
    status_code=status.HTTP_200_OK,
    summary="List user audit logs",
    description="Returns audit events for staff user administration.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def list_user_audit_logs(
    session: AsyncSessionDependency,
    limit: int = Query(default=20, gt=0, le=100),
    offset: int = Query(default=0, ge=0),
    target_user_id: int | None = Query(default=None),
    service: UserService = Depends(get_user_service),
) -> Page[UserAuditLogRead]:
    return await service.list_audit_logs(
        session=session,
        limit=limit,
        offset=offset,
        target_user_id=target_user_id,
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Get user",
    description="Returns one system user by id.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def get_user(
    user_id: int,
    session: AsyncSessionDependency,
    service: UserService = Depends(get_user_service),
) -> User:
    return await service.get_user(session=session, user_id=user_id)


@router.put(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Updates system user data, role, password, or active status.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSessionDependency,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> User:
    return await service.update_user(
        session=session,
        user_id=user_id,
        payload=payload,
        current_user_id=current_user.id,
    )


@router.post(
    "/{user_id}/reset-password",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Reset user password",
    description="Sets a temporary password and requires the user to change it on next login.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def reset_user_password(
    user_id: int,
    payload: UserPasswordReset,
    session: AsyncSessionDependency,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> User:
    return await service.reset_password(
        session=session,
        user_id=user_id,
        payload=payload,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Deactivate user",
    description="Soft deletes a system user by setting is_active to false.",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def delete_user(
    user_id: int,
    session: AsyncSessionDependency,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> User:
    return await service.delete_user(
        session=session,
        user_id=user_id,
        current_user_id=current_user.id,
    )
