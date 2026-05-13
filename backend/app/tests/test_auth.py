from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from jose import jwt

from app.core.config import get_settings
from app.tests.test_students_plans import auth_headers, create_auth_user, student_payload
from app.tests.test_users import user_payload

REGISTER_PAYLOAD = {
    "email": "admin@example.com",
    "full_name": "Admin User",
    "password": "strong-password",
    "role": "ADMIN",
}


async def test_public_register_is_disabled(client: AsyncClient) -> None:
    response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 410
    assert response.json()["error"]["code"] == "PUBLIC_REGISTRATION_DISABLED"


async def test_login_with_valid_credentials(client: AsyncClient) -> None:
    await create_auth_user(
        email=REGISTER_PAYLOAD["email"],
        full_name=REGISTER_PAYLOAD["full_name"],
        password=REGISTER_PAYLOAD["password"],
        role=REGISTER_PAYLOAD["role"],
    )
    response = await client.post(
        "/api/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"]


async def test_login_with_invalid_password(client: AsyncClient) -> None:
    await create_auth_user(
        email=REGISTER_PAYLOAD["email"],
        full_name=REGISTER_PAYLOAD["full_name"],
        password=REGISTER_PAYLOAD["password"],
        role=REGISTER_PAYLOAD["role"],
    )
    response = await client.post(
        "/api/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_me_with_valid_token(client: AsyncClient) -> None:
    await create_auth_user(
        email=REGISTER_PAYLOAD["email"],
        full_name=REGISTER_PAYLOAD["full_name"],
        password=REGISTER_PAYLOAD["password"],
        role=REGISTER_PAYLOAD["role"],
    )
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert login_response.status_code == 200
    assert response.status_code == 200
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]
    assert response.json()["last_login_at"] is not None


async def test_user_with_temporary_password_must_change_password(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    create_response = await client.post(
        "/api/users",
        json=user_payload(email="temporary@example.com"),
        headers=admin_headers,
    )
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "temporary@example.com", "password": "strong-password"},
    )
    token_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    blocked_response = await client.post(
        "/api/students",
        json=student_payload(),
        headers=token_headers,
    )
    change_response = await client.post(
        "/api/auth/change-password",
        json={
            "current_password": "strong-password",
            "new_password": "new-strong-password",
        },
        headers=token_headers,
    )
    allowed_response = await client.post(
        "/api/students",
        json=student_payload(),
        headers=token_headers,
    )

    assert create_response.status_code == 201
    assert create_response.json()["must_change_password"] is True
    assert login_response.status_code == 200
    assert blocked_response.status_code == 403
    assert blocked_response.json()["error"]["code"] == "PASSWORD_CHANGE_REQUIRED"
    assert change_response.status_code == 200
    assert change_response.json()["must_change_password"] is False
    assert allowed_response.status_code == 201


async def test_block_me_without_token(client: AsyncClient) -> None:
    response = await client.get("/api/auth/me")

    assert response.status_code == 401


async def test_block_me_with_expired_token(client: AsyncClient) -> None:
    settings = get_settings()
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_block_me_with_malformed_token(client: AsyncClient) -> None:
    response = await client.get("/api/auth/me", headers={"Authorization": "Bearer malformed"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_block_me_with_invalid_signature(client: AsyncClient) -> None:
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        "wrong-secret-key-with-enough-length",
        algorithm="HS256",
    )

    response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
