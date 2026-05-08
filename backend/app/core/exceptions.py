import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class ErrorPayload(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorPayload


class ApplicationError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def build_error_response(
    code: str,
    message: str,
    status_code: int,
) -> JSONResponse:
    payload = ErrorResponse(error=ErrorPayload(code=code, message=message))
    return JSONResponse(status_code=status_code, content=payload.model_dump())


async def application_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, ApplicationError):
        return await unhandled_exception_handler(request, exc)

    logger.warning(
        "application_error",
        path=request.url.path,
        code=exc.code,
        status_code=exc.status_code,
    )
    return build_error_response(exc.code, exc.message, exc.status_code)


async def validation_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.warning(
        "request_validation_error",
        path=request.url.path,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
    return build_error_response(
        "VALIDATION_ERROR",
        "Invalid request payload.",
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    return build_error_response(
        "INTERNAL_SERVER_ERROR",
        "An unexpected error occurred.",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
