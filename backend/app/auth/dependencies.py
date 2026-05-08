from typing import Annotated

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt import decode_access_token
from app.core.exceptions import ApplicationError
from app.database.session import AsyncSessionDependency
from app.models.user import User
from app.services.user_service import UserService, get_user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    session: AsyncSessionDependency,
    token: Annotated[str, Depends(oauth2_scheme)],
    service: UserService = Depends(get_user_service),
) -> User:
    subject = decode_access_token(token)
    if subject is None:
        raise ApplicationError(
            code="UNAUTHORIZED",
            message="Invalid authentication credentials.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise ApplicationError(
            code="UNAUTHORIZED",
            message="Invalid authentication credentials.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from exc

    return await service.get_active_user_by_id(session=session, user_id=user_id)
