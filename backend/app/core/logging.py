import logging
import sys
from typing import Any

import structlog
from structlog.processors import CallsiteParameter

from app.core.config import Settings


def add_service_name(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    event_dict["service"] = "backend"
    return event_dict


def configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.LOG_LEVEL.upper(),
    )

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        add_service_name,
        structlog.processors.TimeStamper(fmt="iso", key="timestamp", utc=True),
        structlog.stdlib.add_log_level,
        structlog.processors.CallsiteParameterAdder(
            parameters=[CallsiteParameter.MODULE],
        ),
        structlog.processors.EventRenamer("message"),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
