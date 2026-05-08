import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

os.environ["APP_NAME"] = "Gym Management System API"
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "false"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["SECRET_KEY"] = "testing-secret-key-with-enough-length"
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://gym_user:gym_password@127.0.0.1:5432/gym_management",
    ),
)
os.environ["BACKEND_CORS_ORIGINS"] = "http://localhost:3000"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

from app.database.base import Base
from app.database.session import AsyncSessionFactory, engine
from app.main import app
from app.models.access_log import AccessLog
from app.models.enrollment import Enrollment
from app.models.exercise import Exercise
from app.models.exercise_progress import ExerciseProgress
from app.models.payment import Payment
from app.models.plan import Plan
from app.models.student import Student
from app.models.user import User
from app.models.workout_plan import WorkoutPlan


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest.fixture(autouse=True)
async def clean_database() -> AsyncGenerator[None, None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionFactory() as session:
        await session.execute(delete(ExerciseProgress))
        await session.execute(delete(Exercise))
        await session.execute(delete(WorkoutPlan))
        await session.execute(delete(AccessLog))
        await session.execute(delete(Payment))
        await session.execute(delete(Enrollment))
        await session.execute(delete(Plan))
        await session.execute(delete(Student))
        await session.execute(delete(User))
        await session.commit()

    yield

    async with AsyncSessionFactory() as session:
        await session.execute(delete(ExerciseProgress))
        await session.execute(delete(Exercise))
        await session.execute(delete(WorkoutPlan))
        await session.execute(delete(AccessLog))
        await session.execute(delete(Payment))
        await session.execute(delete(Enrollment))
        await session.execute(delete(Plan))
        await session.execute(delete(Student))
        await session.execute(delete(User))
        await session.commit()
