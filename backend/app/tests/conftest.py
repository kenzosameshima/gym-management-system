import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

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

from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
