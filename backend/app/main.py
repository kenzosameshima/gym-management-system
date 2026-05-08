from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.api.health import router as health_router
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
    app.include_router(health_router)

    return app


app = create_app()
