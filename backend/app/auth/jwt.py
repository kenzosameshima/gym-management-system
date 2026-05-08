from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.config import get_settings


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {"sub": subject, "exp": expires_at}
    return str(jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM))


def decode_access_token(token: str) -> str | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None

    subject = payload.get("sub")
    if not isinstance(subject, str):
        return None
    return subject
