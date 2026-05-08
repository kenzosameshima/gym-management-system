from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.api.access_control import router as access_control_router
from app.api.auth import router as auth_router
from app.api.enrollments import router as enrollments_router
from app.api.health import router as health_router
from app.api.payments import router as payments_router
from app.api.plans import router as plans_router
from app.api.students import router as students_router
from app.api.workouts import router as workouts_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import register_middlewares

settings = get_settings()
configure_logging(settings)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("application_startup", app_name=settings.APP_NAME, app_env=settings.APP_ENV)
    yield
    logger.info("application_shutdown", app_name=settings.APP_NAME, app_env=settings.APP_ENV)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    register_middlewares(app, settings)
    register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(students_router)
    app.include_router(plans_router)
    app.include_router(enrollments_router)
    app.include_router(payments_router)
    app.include_router(access_control_router)
    app.include_router(workouts_router)
    app.include_router(health_router)

    return app


app = create_app()
