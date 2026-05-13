from collections.abc import Callable

from fastapi import Depends, status

from app.auth.dependencies import get_current_user
from app.core.enums import UserRole
from app.core.exceptions import ApplicationError
from app.models.user import User


def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ApplicationError(
                code="FORBIDDEN",
                message="Insufficient permissions.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        if current_user.must_change_password:
            raise ApplicationError(
                code="PASSWORD_CHANGE_REQUIRED",
                message="Password change is required before accessing this resource.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return current_user

    return dependency
