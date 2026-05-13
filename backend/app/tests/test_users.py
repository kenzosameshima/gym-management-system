from httpx import AsyncClient

from app.tests.test_students_plans import auth_headers
from app.tests.test_workouts import create_student, create_workout_plan


def user_payload(
    email: str = "staff@example.com",
    full_name: str = "Staff User",
    password: str = "strong-password",
    role: str = "RECEPTIONIST",
) -> dict[str, str]:
    return {
        "email": email,
        "full_name": full_name,
        "password": password,
        "role": role,
    }


async def test_admin_can_create_list_and_get_user(client: AsyncClient) -> None:
    headers = await auth_headers(client)

    create_response = await client.post("/api/users", json=user_payload(), headers=headers)
    user_id = create_response.json()["id"]
    list_response = await client.get("/api/users?role=RECEPTIONIST", headers=headers)
    get_response = await client.get(f"/api/users/{user_id}", headers=headers)

    assert create_response.status_code == 201
    assert create_response.json()["email"] == "staff@example.com"
    assert create_response.json()["is_active"] is True
    assert create_response.json()["must_change_password"] is True
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert get_response.status_code == 200
    assert get_response.json()["id"] == user_id


async def test_admin_can_update_user_and_password(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    create_response = await client.post("/api/users", json=user_payload(), headers=headers)
    user_id = create_response.json()["id"]

    update_response = await client.put(
        f"/api/users/{user_id}",
        json={
            "email": "updated-staff@example.com",
            "full_name": "Updated Staff",
            "password": "new-strong-password",
            "role": "INSTRUCTOR",
        },
        headers=headers,
    )
    old_login_response = await client.post(
        "/api/auth/login",
        json={"email": "updated-staff@example.com", "password": "strong-password"},
    )
    new_login_response = await client.post(
        "/api/auth/login",
        json={"email": "updated-staff@example.com", "password": "new-strong-password"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Updated Staff"
    assert update_response.json()["role"] == "INSTRUCTOR"
    assert old_login_response.status_code == 401
    assert new_login_response.status_code == 200


async def test_admin_can_reset_user_password_and_audit_event(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    create_response = await client.post("/api/users", json=user_payload(), headers=headers)
    user_id = create_response.json()["id"]

    reset_response = await client.post(
        f"/api/users/{user_id}/reset-password",
        json={"temporary_password": "temporary-password"},
        headers=headers,
    )
    old_login_response = await client.post(
        "/api/auth/login",
        json={"email": "staff@example.com", "password": "strong-password"},
    )
    new_login_response = await client.post(
        "/api/auth/login",
        json={"email": "staff@example.com", "password": "temporary-password"},
    )
    audit_response = await client.get(f"/api/users/audit?target_user_id={user_id}", headers=headers)

    assert reset_response.status_code == 200
    assert reset_response.json()["must_change_password"] is True
    assert old_login_response.status_code == 401
    assert new_login_response.status_code == 200
    assert audit_response.status_code == 200
    assert any(item["action"] == "PASSWORD_RESET" for item in audit_response.json()["items"])


async def test_admin_soft_deletes_user(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    create_response = await client.post("/api/users", json=user_payload(), headers=headers)
    user_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/users/{user_id}", headers=headers)
    active_list_response = await client.get("/api/users", headers=headers)
    inactive_list_response = await client.get("/api/users?is_active=false", headers=headers)
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "staff@example.com", "password": "strong-password"},
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["is_active"] is False
    assert active_list_response.json()["total"] == 1
    assert inactive_list_response.json()["total"] == 1
    assert login_response.status_code == 401


async def test_block_duplicate_user_email(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    first_response = await client.post("/api/users", json=user_payload(), headers=headers)
    second_response = await client.post("/api/users", json=user_payload(), headers=headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"


async def test_non_admin_cannot_manage_users(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    receptionist_headers = await auth_headers(client, role="RECEPTIONIST")
    create_response = await client.post("/api/users", json=user_payload(), headers=admin_headers)
    user_id = create_response.json()["id"]

    receptionist_create_response = await client.post(
        "/api/users",
        json=user_payload(email="blocked@example.com"),
        headers=receptionist_headers,
    )
    receptionist_update_response = await client.put(
        f"/api/users/{user_id}",
        json={"full_name": "Blocked"},
        headers=receptionist_headers,
    )
    receptionist_delete_response = await client.delete(
        f"/api/users/{user_id}",
        headers=receptionist_headers,
    )
    receptionist_audit_response = await client.get("/api/users/audit", headers=receptionist_headers)
    receptionist_reset_response = await client.post(
        f"/api/users/{user_id}/reset-password",
        json={"temporary_password": "temporary-password"},
        headers=receptionist_headers,
    )

    assert create_response.status_code == 201
    assert receptionist_create_response.status_code == 403
    assert receptionist_update_response.status_code == 403
    assert receptionist_delete_response.status_code == 403
    assert receptionist_audit_response.status_code == 403
    assert receptionist_reset_response.status_code == 403


async def test_admin_cannot_deactivate_self(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    me_response = await client.get("/api/auth/me", headers=headers)
    user_id = me_response.json()["id"]

    update_response = await client.put(
        f"/api/users/{user_id}",
        json={"is_active": False},
        headers=headers,
    )
    delete_response = await client.delete(f"/api/users/{user_id}", headers=headers)

    assert update_response.status_code == 409
    assert update_response.json()["error"]["code"] == "CANNOT_DISABLE_CURRENT_USER"
    assert delete_response.status_code == 409
    assert delete_response.json()["error"]["code"] == "CANNOT_DELETE_CURRENT_USER"


async def test_block_deactivating_instructor_with_active_workout_plans(
    client: AsyncClient,
) -> None:
    admin_headers = await auth_headers(client)
    instructor_response = await client.post(
        "/api/users",
        json=user_payload(email="trainer@example.com", role="INSTRUCTOR"),
        headers=admin_headers,
    )
    instructor_id = instructor_response.json()["id"]
    student_id = await create_student(client, admin_headers)
    workout_plan_id = await create_workout_plan(
        client,
        admin_headers,
        student_id=student_id,
        instructor_id=instructor_id,
    )

    deactivate_response = await client.delete(f"/api/users/{instructor_id}", headers=admin_headers)
    demote_response = await client.put(
        f"/api/users/{instructor_id}",
        json={"role": "RECEPTIONIST"},
        headers=admin_headers,
    )

    assert instructor_response.status_code == 201
    assert workout_plan_id > 0
    assert deactivate_response.status_code == 409
    assert deactivate_response.json()["error"]["code"] == "INSTRUCTOR_HAS_ACTIVE_WORKOUT_PLANS"
    assert demote_response.status_code == 409
    assert demote_response.json()["error"]["code"] == "INSTRUCTOR_HAS_ACTIVE_WORKOUT_PLANS"
