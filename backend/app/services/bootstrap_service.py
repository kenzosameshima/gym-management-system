from collections.abc import Callable
from decimal import Decimal
from typing import Protocol

import structlog
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.auth.password import hash_password
from app.core.enums import UserRole
from app.database.session import AsyncSessionFactory
from app.repositories.plan_repository import PlanRepository
from app.repositories.user_repository import UserRepository
from app.schemas.plan import PlanCreate
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService

logger = structlog.get_logger(__name__)


class InitialAdminSettings(Protocol):
    INITIAL_ADMIN_EMAIL: EmailStr | str | None
    INITIAL_ADMIN_FULL_NAME: str | None
    INITIAL_ADMIN_PASSWORD: str | None
    SEED_DEFAULT_PLANS: bool


DEFAULT_PLAN_SEEDS = (
    PlanCreate(name="Mensal", price=Decimal("99.90"), duration_days=30),
    PlanCreate(name="Trimestral", price=Decimal("269.90"), duration_days=90),
    PlanCreate(name="Semestral", price=Decimal("499.90"), duration_days=180),
    PlanCreate(name="Anual", price=Decimal("899.90"), duration_days=365),
)


async def seed_initial_admin(
    settings: InitialAdminSettings,
    session_factory: Callable[[], AsyncSession] | async_sessionmaker[AsyncSession] = (
        AsyncSessionFactory
    ),
) -> None:
    """Create the first admin from environment settings when no active admin exists."""
    repository = UserRepository()
    async with session_factory() as session:
        if await repository.has_active_role(session, UserRole.ADMIN):
            logger.info("initial_admin_seed_skipped", reason="active_admin_exists")
            return

        if (
            settings.INITIAL_ADMIN_EMAIL is None
            or settings.INITIAL_ADMIN_FULL_NAME is None
            or settings.INITIAL_ADMIN_PASSWORD is None
        ):
            logger.warning("initial_admin_seed_skipped", reason="missing_initial_admin_settings")
            return

        existing_user = await repository.get_by_email(session, str(settings.INITIAL_ADMIN_EMAIL))
        if existing_user is not None:
            await repository.update(
                session,
                existing_user,
                {
                    "full_name": settings.INITIAL_ADMIN_FULL_NAME,
                    "password_hash": hash_password(settings.INITIAL_ADMIN_PASSWORD),
                    "role": UserRole.ADMIN,
                    "is_active": True,
                    "must_change_password": False,
                },
            )
            await session.commit()
            logger.info(
                "initial_admin_seed_reactivated",
                email=str(settings.INITIAL_ADMIN_EMAIL),
            )
            return

        await AuthService(repository).register(
            session=session,
            payload=UserCreate(
                email=settings.INITIAL_ADMIN_EMAIL,
                full_name=settings.INITIAL_ADMIN_FULL_NAME,
                password=settings.INITIAL_ADMIN_PASSWORD,
                role=UserRole.ADMIN,
            ),
        )
        logger.info("initial_admin_seed_created", email=str(settings.INITIAL_ADMIN_EMAIL))


async def seed_default_plans(
    settings: InitialAdminSettings,
    session_factory: Callable[[], AsyncSession] | async_sessionmaker[AsyncSession] = (
        AsyncSessionFactory
    ),
) -> None:
    if not settings.SEED_DEFAULT_PLANS:
        logger.info("default_plans_seed_skipped", reason="disabled")
        return

    repository = PlanRepository()
    created_count = 0
    async with session_factory() as session:
        for payload in DEFAULT_PLAN_SEEDS:
            if await repository.get_by_name(session, payload.name) is not None:
                continue
            await repository.create(session, payload)
            created_count += 1
        await session.commit()
    logger.info("default_plans_seed_completed", created_count=created_count)
