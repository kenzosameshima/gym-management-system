from httpx import AsyncClient

from app.database.session import AsyncSessionFactory
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


def student_payload(
    cpf: str = "12345678901",
    email: str = "student@example.com",
    status: str = "ACTIVE",
) -> dict[str, str]:
    return {
        "name": "Student One",
        "cpf": cpf,
        "birth_date": "2000-01-01",
        "phone": "+5511999999999",
        "email": email,
        "address": "Main Street",
        "status": status,
    }


def plan_payload(name: str = "Monthly Plan", price: str = "99.90") -> dict[str, str | int]:
    return {
        "name": name,
        "price": price,
        "duration_days": 30,
        "status": "ACTIVE",
    }


async def auth_headers(client: AsyncClient, role: str = "ADMIN") -> dict[str, str]:
    email = f"{role.lower()}@example.com"
    password = "strong-password"
    await create_auth_user(email=email, password=password, role=role)

    login_response = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def create_auth_user(
    *,
    email: str,
    password: str = "strong-password",
    role: str = "ADMIN",
    full_name: str | None = None,
) -> None:
    async with AsyncSessionFactory() as session:
        repository = UserRepository()
        if await repository.get_by_email(session, email) is not None:
            return
        await AuthService(repository).register(
            session=session,
            payload=UserCreate(
                email=email,
                full_name=full_name or f"{role.title()} User",
                password=password,
                role=role,
            ),
        )


async def test_create_student_authenticated(client: AsyncClient) -> None:
    response = await client.post(
        "/api/students",
        json=student_payload(),
        headers=await auth_headers(client),
    )

    assert response.status_code == 201
    assert response.json()["cpf"] == "12345678901"


async def test_create_student_normalizes_formatted_cpf(client: AsyncClient) -> None:
    response = await client.post(
        "/api/students",
        json=student_payload(cpf="123.456.789-01"),
        headers=await auth_headers(client),
    )

    assert response.status_code == 201
    assert response.json()["cpf"] == "12345678901"


async def test_block_student_with_unreasonable_birth_date(client: AsyncClient) -> None:
    payload = student_payload()
    payload["birth_date"] = "1800-01-01"

    response = await client.post(
        "/api/students",
        json=payload,
        headers=await auth_headers(client),
    )

    assert response.status_code == 422


async def test_block_student_with_duplicate_cpf(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    first_response = await client.post("/api/students", json=student_payload(), headers=headers)
    second_response = await client.post(
        "/api/students",
        json=student_payload(email="other@example.com"),
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "CPF_ALREADY_REGISTERED"


async def test_block_student_with_duplicate_email(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    first_response = await client.post("/api/students", json=student_payload(), headers=headers)
    second_response = await client.post(
        "/api/students",
        json=student_payload(cpf="98765432100"),
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "STUDENT_EMAIL_ALREADY_REGISTERED"


async def test_list_students_authenticated(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    create_response = await client.post("/api/students", json=student_payload(), headers=headers)
    response = await client.get("/api/students", headers=headers)

    assert create_response.status_code == 201
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert len(response.json()["items"]) == 1


async def test_receptionist_can_manage_students(client: AsyncClient) -> None:
    headers = await auth_headers(client, role="RECEPTIONIST")
    create_response = await client.post("/api/students", json=student_payload(), headers=headers)
    student_id = create_response.json()["id"]

    update_response = await client.put(
        f"/api/students/{student_id}",
        json={"phone": "+5511888888888"},
        headers=headers,
    )
    delete_response = await client.delete(f"/api/students/{student_id}", headers=headers)

    assert create_response.status_code == 201
    assert update_response.status_code == 200
    assert update_response.json()["phone"] == "+5511888888888"
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "INACTIVE"


async def test_instructor_can_read_but_not_manage_students(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers = await auth_headers(client, role="INSTRUCTOR")
    create_response = await client.post(
        "/api/students",
        json=student_payload(),
        headers=admin_headers,
    )
    student_id = create_response.json()["id"]

    list_response = await client.get("/api/students", headers=instructor_headers)
    get_response = await client.get(f"/api/students/{student_id}", headers=instructor_headers)
    update_response = await client.put(
        f"/api/students/{student_id}",
        json={"phone": "+5511888888888"},
        headers=instructor_headers,
    )
    delete_response = await client.delete(
        f"/api/students/{student_id}",
        headers=instructor_headers,
    )

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert update_response.status_code == 403
    assert delete_response.status_code == 403


async def test_soft_delete_student(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    create_response = await client.post("/api/students", json=student_payload(), headers=headers)
    student_id = create_response.json()["id"]

    response = await client.delete(f"/api/students/{student_id}", headers=headers)

    assert create_response.status_code == 201
    assert response.status_code == 200
    assert response.json()["status"] == "INACTIVE"


async def test_student_status_rejects_defaulter(client: AsyncClient) -> None:
    response = await client.post(
        "/api/students",
        json=student_payload(status="DEFAULTER"),
        headers=await auth_headers(client),
    )

    assert response.status_code == 422


async def test_create_plan_authenticated(client: AsyncClient) -> None:
    response = await client.post(
        "/api/plans",
        json=plan_payload(),
        headers=await auth_headers(client),
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Monthly Plan"


async def test_block_plan_with_duplicate_name(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    first_response = await client.post("/api/plans", json=plan_payload(), headers=headers)
    second_response = await client.post(
        "/api/plans",
        json=plan_payload(price="120.00"),
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "PLAN_NAME_ALREADY_REGISTERED"


async def test_block_plan_with_invalid_price(client: AsyncClient) -> None:
    response = await client.post(
        "/api/plans",
        json=plan_payload(price="0.00"),
        headers=await auth_headers(client),
    )

    assert response.status_code == 422


async def test_list_plans_authenticated(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    create_response = await client.post("/api/plans", json=plan_payload(), headers=headers)
    response = await client.get("/api/plans", headers=headers)

    assert create_response.status_code == 201
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert len(response.json()["items"]) == 1


async def test_receptionist_can_read_but_not_manage_plans(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    receptionist_headers = await auth_headers(client, role="RECEPTIONIST")
    create_response = await client.post("/api/plans", json=plan_payload(), headers=admin_headers)
    plan_id = create_response.json()["id"]

    list_response = await client.get("/api/plans", headers=receptionist_headers)
    update_response = await client.put(
        f"/api/plans/{plan_id}",
        json={"price": "120.00"},
        headers=receptionist_headers,
    )
    delete_response = await client.delete(f"/api/plans/{plan_id}", headers=receptionist_headers)

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert update_response.status_code == 403
    assert delete_response.status_code == 403


async def test_filter_students_by_cpf_email_and_name(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    await client.post("/api/students", json=student_payload(), headers=headers)

    cpf_response = await client.get("/api/students?cpf=12345678901", headers=headers)
    email_response = await client.get("/api/students?email=student@example.com", headers=headers)
    name_response = await client.get("/api/students?name=Student", headers=headers)

    assert cpf_response.status_code == 200
    assert cpf_response.json()["total"] == 1
    assert email_response.json()["total"] == 1
    assert name_response.json()["total"] == 1


async def test_search_students_by_phone_email_name_cpf_and_enrollment(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    student_response = await client.post("/api/students", json=student_payload(), headers=headers)
    plan_response = await client.post("/api/plans", json=plan_payload(), headers=headers)
    enrollment_response = await client.post(
        "/api/enrollments",
        json={
            "student_id": student_response.json()["id"],
            "plan_id": plan_response.json()["id"],
            "start_date": "2026-05-01",
            "end_date": "2026-05-31",
            "status": "ACTIVE",
        },
        headers=headers,
    )

    name_response = await client.get("/api/students/search?q=Student", headers=headers)
    cpf_response = await client.get("/api/students/search?q=12345678901", headers=headers)
    phone_response = await client.get("/api/students/search?q=999999999", headers=headers)
    email_response = await client.get("/api/students/search?q=student@example.com", headers=headers)
    enrollment_search_response = await client.get(
        f"/api/students/search?q={enrollment_response.json()['id']}",
        headers=headers,
    )

    assert enrollment_response.status_code == 201
    for response in [
        name_response,
        cpf_response,
        phone_response,
        email_response,
        enrollment_search_response,
    ]:
        assert response.status_code == 200
        assert response.json()[0]["name"] == "Student One"
        assert response.json()[0]["financial_status"] == "IN_GOOD_STANDING"


async def test_filter_students_by_status(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    await client.post("/api/students", json=student_payload(), headers=headers)
    await client.post(
        "/api/students",
        json=student_payload(cpf="98765432100", email="inactive@example.com", status="INACTIVE"),
        headers=headers,
    )

    response = await client.get("/api/students?status=INACTIVE", headers=headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["status"] == "INACTIVE"


async def test_filter_plans_by_status(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    active_response = await client.post("/api/plans", json=plan_payload(), headers=headers)
    inactive_response = await client.post(
        "/api/plans",
        json={**plan_payload(name="Inactive Plan"), "status": "INACTIVE"},
        headers=headers,
    )

    response = await client.get("/api/plans?status=INACTIVE", headers=headers)

    assert active_response.status_code == 201
    assert inactive_response.status_code == 201
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["status"] == "INACTIVE"


async def test_soft_delete_plan(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    create_response = await client.post("/api/plans", json=plan_payload(), headers=headers)
    plan_id = create_response.json()["id"]

    response = await client.delete(f"/api/plans/{plan_id}", headers=headers)

    assert create_response.status_code == 201
    assert response.status_code == 200
    assert response.json()["status"] == "INACTIVE"


async def test_block_access_without_jwt(client: AsyncClient) -> None:
    students_response = await client.get("/api/students")
    plans_response = await client.get("/api/plans")

    assert students_response.status_code == 401
    assert plans_response.status_code == 401


async def test_instructor_cannot_create_student_or_plan(client: AsyncClient) -> None:
    headers = await auth_headers(client, role="INSTRUCTOR")

    student_response = await client.post("/api/students", json=student_payload(), headers=headers)
    plan_response = await client.post("/api/plans", json=plan_payload(), headers=headers)
    plans_read_response = await client.get("/api/plans", headers=headers)

    assert student_response.status_code == 403
    assert plan_response.status_code == 403
    assert plans_read_response.status_code == 403
