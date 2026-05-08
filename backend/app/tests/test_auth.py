from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "email": "admin@example.com",
    "full_name": "Admin User",
    "password": "strong-password",
    "role": "ADMIN",
}


async def test_register_user(client: AsyncClient) -> None:
    response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == REGISTER_PAYLOAD["email"]
    assert data["full_name"] == REGISTER_PAYLOAD["full_name"]
    assert data["role"] == "ADMIN"
    assert "password_hash" not in data


async def test_block_duplicate_email(client: AsyncClient) -> None:
    first_response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    second_response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


async def test_login_with_valid_credentials(client: AsyncClient) -> None:
    register_response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post(
        "/api/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )

    assert register_response.status_code == 201
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"]


async def test_login_with_invalid_password(client: AsyncClient) -> None:
    register_response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post(
        "/api/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": "wrong-password",
        },
    )

    assert register_response.status_code == 201
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_me_with_valid_token(client: AsyncClient) -> None:
    register_response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
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

    assert register_response.status_code == 201
    assert login_response.status_code == 200
    assert response.status_code == 200
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]


async def test_block_me_without_token(client: AsyncClient) -> None:
    response = await client.get("/api/auth/me")

    assert response.status_code == 401
