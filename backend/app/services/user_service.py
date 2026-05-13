from fastapi import Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.password import hash_password, verify_password
from app.core.enums import UserRole, WorkoutPlanStatus
from app.core.exceptions import ApplicationError
from app.models.user import User
from app.models.workout_plan import WorkoutPlan
from app.repositories.user_repository import UserRepository, get_user_repository
from app.schemas.pagination import Page
from app.schemas.user import (
    UserAuditLogRead,
    UserCreate,
    UserPasswordChange,
    UserPasswordReset,
    UserRead,
    UserUpdate,
)


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
        is_active: bool | None,
    ) -> Page[UserRead]:
        users, total = await self._repository.list(
            session,
            limit=limit,
            offset=offset,
            role=role,
            is_active=is_active,
        )
        return Page[UserRead](
            items=list(users),
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_user(self, session: AsyncSession, user_id: int) -> User:
        return await self._get_user_model(session, user_id)

    async def list_audit_logs(
        self,
        session: AsyncSession,
        *,
        limit: int,
        offset: int,
        target_user_id: int | None,
    ) -> Page[UserAuditLogRead]:
        logs, total = await self._repository.list_audit_logs(
            session,
            limit=limit,
            offset=offset,
            target_user_id=target_user_id,
        )
        return Page[UserAuditLogRead](
            items=list(logs),
            total=total,
            limit=limit,
            offset=offset,
        )

    async def create_user(
        self,
        session: AsyncSession,
        payload: UserCreate,
        *,
        current_user_id: int,
    ) -> User:
        await self._ensure_unique_email(session, payload.email)
        user = await self._repository.create(
            session=session,
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
            role=payload.role,
            must_change_password=True,
        )
        await self._repository.create_audit_log(
            session,
            actor_user_id=current_user_id,
            target_user_id=user.id,
            action="USER_CREATED",
            details=f"role={user.role.value}; temporary_password=true",
        )
        await session.commit()
        await session.refresh(user)
        return user

    async def update_user(
        self,
        session: AsyncSession,
        user_id: int,
        payload: UserUpdate,
        *,
        current_user_id: int,
    ) -> User:
        user = await self._get_user_model(session, user_id)
        if payload.email is not None and payload.email != user.email:
            await self._ensure_unique_email(session, payload.email)

        values = payload.model_dump(exclude_unset=True, exclude={"password"})
        if payload.password is not None:
            values["password_hash"] = hash_password(payload.password)

        if self._would_disable_current_admin(user, values, current_user_id):
            raise ApplicationError(
                code="CANNOT_DISABLE_CURRENT_USER",
                message="Current administrator cannot be deactivated or demoted.",
                status_code=status.HTTP_409_CONFLICT,
            )

        if await self._would_disable_last_active_admin(session, user, values):
            raise ApplicationError(
                code="CANNOT_DISABLE_LAST_ADMIN",
                message="The last active administrator cannot be deactivated or demoted.",
                status_code=status.HTTP_409_CONFLICT,
            )

        if await self._would_disable_instructor_with_active_workouts(session, user, values):
            raise ApplicationError(
                code="INSTRUCTOR_HAS_ACTIVE_WORKOUT_PLANS",
                message="Instructor has active workout plans and cannot be deactivated or demoted.",
                status_code=status.HTTP_409_CONFLICT,
            )

        updated_user = await self._repository.update(session, user, values)
        await self._repository.create_audit_log(
            session,
            actor_user_id=current_user_id,
            target_user_id=updated_user.id,
            action="USER_UPDATED",
            details="; ".join(sorted(values.keys())),
        )
        await session.commit()
        await session.refresh(updated_user)
        return updated_user

    async def delete_user(
        self,
        session: AsyncSession,
        user_id: int,
        *,
        current_user_id: int,
    ) -> User:
        user = await self._get_user_model(session, user_id)
        if user.id == current_user_id:
            raise ApplicationError(
                code="CANNOT_DELETE_CURRENT_USER",
                message="Current administrator cannot be deactivated.",
                status_code=status.HTTP_409_CONFLICT,
            )
        if await self._would_disable_last_active_admin(
            session,
            user,
            {"is_active": False},
        ):
            raise ApplicationError(
                code="CANNOT_DISABLE_LAST_ADMIN",
                message="The last active administrator cannot be deactivated.",
                status_code=status.HTTP_409_CONFLICT,
            )
        if await self._active_workout_plan_count(session, user.id) > 0:
            raise ApplicationError(
                code="INSTRUCTOR_HAS_ACTIVE_WORKOUT_PLANS",
                message="Instructor has active workout plans and cannot be deactivated.",
                status_code=status.HTTP_409_CONFLICT,
            )

        updated_user = await self._repository.update(session, user, {"is_active": False})
        await self._repository.create_audit_log(
            session,
            actor_user_id=current_user_id,
            target_user_id=updated_user.id,
            action="USER_DEACTIVATED",
        )
        await session.commit()
        await session.refresh(updated_user)
        return updated_user

    async def reset_password(
        self,
        session: AsyncSession,
        user_id: int,
        payload: UserPasswordReset,
        *,
        current_user_id: int,
    ) -> User:
        user = await self._get_user_model(session, user_id)
        updated_user = await self._repository.update(
            session,
            user,
            {
                "password_hash": hash_password(payload.temporary_password),
                "must_change_password": True,
            },
        )
        await self._repository.create_audit_log(
            session,
            actor_user_id=current_user_id,
            target_user_id=updated_user.id,
            action="PASSWORD_RESET",
            details="temporary_password=true",
        )
        await session.commit()
        await session.refresh(updated_user)
        return updated_user

    async def change_password(
        self,
        session: AsyncSession,
        *,
        current_user: User,
        payload: UserPasswordChange,
    ) -> User:
        if not verify_password(payload.current_password, current_user.password_hash):
            raise ApplicationError(
                code="INVALID_CURRENT_PASSWORD",
                message="Current password is invalid.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        if payload.current_password == payload.new_password:
            raise ApplicationError(
                code="PASSWORD_REUSE_NOT_ALLOWED",
                message="New password must be different from the current password.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        updated_user = await self._repository.update(
            session,
            current_user,
            {
                "password_hash": hash_password(payload.new_password),
                "must_change_password": False,
            },
        )
        await self._repository.create_audit_log(
            session,
            actor_user_id=current_user.id,
            target_user_id=current_user.id,
            action="PASSWORD_CHANGED",
        )
        await session.commit()
        await session.refresh(updated_user)
        return updated_user

    async def _get_user_model(self, session: AsyncSession, user_id: int) -> User:
        user = await self._repository.get_by_id(session, user_id)
        if user is None:
            raise ApplicationError(
                code="USER_NOT_FOUND",
                message="User was not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return user

    async def _ensure_unique_email(self, session: AsyncSession, email: str) -> None:
        if await self._repository.get_by_email(session, email) is not None:
            raise ApplicationError(
                code="EMAIL_ALREADY_REGISTERED",
                message="Email is already registered.",
                status_code=status.HTTP_409_CONFLICT,
            )

    async def _would_disable_instructor_with_active_workouts(
        self,
        session: AsyncSession,
        user: User,
        values: dict[str, object],
    ) -> bool:
        if user.role != UserRole.INSTRUCTOR:
            return False

        next_role = values.get("role", user.role)
        next_is_active = values.get("is_active", user.is_active)
        keeps_instructor_active = next_role == UserRole.INSTRUCTOR and next_is_active is True
        active_workout_plan_count = await self._active_workout_plan_count(session, user.id)
        return not keeps_instructor_active and active_workout_plan_count > 0

    async def _active_workout_plan_count(self, session: AsyncSession, instructor_id: int) -> int:
        result = await session.execute(
            select(func.count())
            .select_from(WorkoutPlan)
            .where(
                WorkoutPlan.instructor_id == instructor_id,
                WorkoutPlan.status == WorkoutPlanStatus.ACTIVE,
            )
        )
        return result.scalar_one()

    async def _would_disable_last_active_admin(
        self,
        session: AsyncSession,
        user: User,
        values: dict[str, object],
    ) -> bool:
        if user.role != UserRole.ADMIN or not user.is_active:
            return False
        next_role = values.get("role", user.role)
        next_is_active = values.get("is_active", user.is_active)
        keeps_admin_active = next_role == UserRole.ADMIN and next_is_active is True
        if keeps_admin_active:
            return False
        return await self._repository.count_active_role(session, UserRole.ADMIN) <= 1

    @staticmethod
    def _would_disable_current_admin(
        user: User,
        values: dict[str, object],
        current_user_id: int,
    ) -> bool:
        if user.id != current_user_id:
            return False
        next_role = values.get("role", user.role)
        next_is_active = values.get("is_active", user.is_active)
        return next_role != UserRole.ADMIN or next_is_active is False


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository=repository)
