from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware

from app.auth.jwt import decode_access_token
from app.core.config import Settings

logger = structlog.get_logger(__name__)


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    started_at = perf_counter()
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    user_id = _user_id_from_request(request)
    response = await call_next(request)
    duration_ms = round((perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "http_request",
        request_id=request_id,
        http_method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        user_id=user_id,
    )
    return response


def _user_id_from_request(request: Request) -> int | None:
    authorization = request.headers.get("Authorization")
    if authorization is None or not authorization.startswith("Bearer "):
        return None
    subject = decode_access_token(authorization.removeprefix("Bearer ").strip())
    if subject is None:
        return None
    try:
        return int(subject)
    except ValueError:
        return None


def register_middlewares(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    app.middleware("http")(request_logging_middleware)
