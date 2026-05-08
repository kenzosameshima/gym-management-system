import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

os.environ.setdefault("APP_NAME", "Gym Management System API")
os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("SECRET_KEY", "testing-secret-key-with-enough-length")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://gym_user:gym_password@postgres:5432/gym_management",
)
os.environ.setdefault("BACKEND_CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from app.database.base import Base
from app.database.session import AsyncSessionFactory, engine
from app.main import app
from app.models.plan import Plan
from app.models.student import Student
from app.models.user import User


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest.fixture(autouse=True)
async def clean_database() -> AsyncGenerator[None, None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionFactory() as session:
        await session.execute(delete(Plan))
        await session.execute(delete(Student))
        await session.execute(delete(User))
        await session.commit()

    yield

    async with AsyncSessionFactory() as session:
        await session.execute(delete(Plan))
        await session.execute(delete(Student))
        await session.execute(delete(User))
        await session.commit()
