from types import SimpleNamespace

from sqlalchemy import select

from app.core.enums import UserRole
from app.database.session import AsyncSessionFactory
from app.models.plan import Plan
from app.models.user import User
from app.services.bootstrap_service import seed_default_plans, seed_initial_admin


def initial_admin_settings(
    *,
    email: str | None = "seed-admin@example.com",
    full_name: str | None = "Seed Admin",
    password: str | None = "seed-strong-password",
) -> SimpleNamespace:
    return SimpleNamespace(
        INITIAL_ADMIN_EMAIL=email,
        INITIAL_ADMIN_FULL_NAME=full_name,
        INITIAL_ADMIN_PASSWORD=password,
        SEED_DEFAULT_PLANS=False,
    )


async def user_count() -> int:
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(User))
        return len(result.scalars().all())


async def get_user_by_email(email: str) -> User | None:
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


async def plan_names() -> list[str]:
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Plan).order_by(Plan.name))
        return [plan.name for plan in result.scalars().all()]


async def test_seed_initial_admin_creates_first_admin() -> None:
    await seed_initial_admin(initial_admin_settings(), AsyncSessionFactory)

    user = await get_user_by_email("seed-admin@example.com")

    assert user is not None
    assert user.full_name == "Seed Admin"
    assert user.role == UserRole.ADMIN
    assert user.is_active is True


async def test_seed_initial_admin_is_idempotent_when_admin_exists() -> None:
    await seed_initial_admin(initial_admin_settings(), AsyncSessionFactory)
    await seed_initial_admin(
        initial_admin_settings(email="second-admin@example.com"),
        AsyncSessionFactory,
    )

    assert await user_count() == 1
    assert await get_user_by_email("second-admin@example.com") is None


async def test_seed_initial_admin_skips_when_settings_are_missing() -> None:
    await seed_initial_admin(initial_admin_settings(password=None), AsyncSessionFactory)

    assert await user_count() == 0


async def test_seed_default_plans_creates_initial_plans_when_enabled() -> None:
    settings = initial_admin_settings()
    settings.SEED_DEFAULT_PLANS = True

    await seed_default_plans(settings, AsyncSessionFactory)

    assert await plan_names() == ["Anual", "Mensal", "Semestral", "Trimestral"]


async def test_seed_default_plans_is_idempotent() -> None:
    settings = initial_admin_settings()
    settings.SEED_DEFAULT_PLANS = True

    await seed_default_plans(settings, AsyncSessionFactory)
    await seed_default_plans(settings, AsyncSessionFactory)

    assert await plan_names() == ["Anual", "Mensal", "Semestral", "Trimestral"]


async def test_seed_default_plans_skips_when_disabled() -> None:
    await seed_default_plans(initial_admin_settings(), AsyncSessionFactory)

    assert await plan_names() == []
