from datetime import date, timedelta

from httpx import AsyncClient
from sqlalchemy import select

from app.core.enums import AccessDeniedReason
from app.database.session import AsyncSessionFactory
from app.models.access_log import AccessLog
from app.tests.test_students_plans import auth_headers, plan_payload, student_payload


async def create_student_and_plan(client: AsyncClient, headers: dict[str, str]) -> tuple[int, int]:
    student_response = await client.post(
        "/api/students",
        json=student_payload(),
        headers=headers,
    )
    plan_response = await client.post(
        "/api/plans",
        json=plan_payload(),
        headers=headers,
    )
    assert student_response.status_code == 201
    assert plan_response.status_code == 201
    return student_response.json()["id"], plan_response.json()["id"]


async def latest_access_log() -> AccessLog:
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(AccessLog).order_by(AccessLog.id.desc()).limit(1))
        access_log = result.scalar_one()
        return access_log


async def assert_latest_access_log(
    *,
    student_id: int | None,
    cpf_attempted: str,
    allowed: bool,
    reason: AccessDeniedReason | None,
) -> None:
    access_log = await latest_access_log()
    assert access_log.student_id == student_id
    assert access_log.cpf_attempted == cpf_attempted
    assert access_log.allowed is allowed
    assert access_log.reason == reason


async def test_create_enrollment_generates_initial_payment(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    student_id, plan_id = await create_student_and_plan(client, headers)

    enrollment_response = await client.post(
        "/api/enrollments",
        json={
            "student_id": student_id,
            "plan_id": plan_id,
            "start_date": "2026-05-08",
        },
        headers=headers,
    )
    payments_response = await client.get("/api/payments", headers=headers)

    assert enrollment_response.status_code == 201
    assert enrollment_response.json()["status"] == "ACTIVE"
    assert payments_response.status_code == 200
    assert payments_response.json()["total"] == 1
    assert payments_response.json()["items"][0]["status"] == "PENDING"
    assert payments_response.json()["items"][0]["amount"] == "99.90"


async def test_access_allowed_with_active_enrollment_and_no_overdue_payments(
    client: AsyncClient,
) -> None:
    headers = await auth_headers(client)
    student_id, plan_id = await create_student_and_plan(client, headers)
    enrollment_response = await client.post(
        "/api/enrollments",
        json={
            "student_id": student_id,
            "plan_id": plan_id,
            "start_date": date.today().isoformat(),
        },
        headers=headers,
    )
    payment_id = (await client.get("/api/payments", headers=headers)).json()["items"][0]["id"]
    payment_response = await client.patch(f"/api/payments/{payment_id}/pay", headers=headers)

    response = await client.post(
        "/api/access-control/check",
        json={"cpf": "12345678901"},
        headers=headers,
    )

    assert enrollment_response.status_code == 201
    assert payment_response.status_code == 200
    assert response.status_code == 200
    assert response.json() == {
        "student_id": student_id,
        "cpf_attempted": "12345678901",
        "allowed": True,
        "reason": None,
    }
    await assert_latest_access_log(
        student_id=student_id,
        cpf_attempted="12345678901",
        allowed=True,
        reason=None,
    )


async def test_access_denied_when_payment_is_overdue(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    student_id, plan_id = await create_student_and_plan(client, headers)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    enrollment_response = await client.post(
        "/api/enrollments",
        json={
            "student_id": student_id,
            "plan_id": plan_id,
            "start_date": date.today().isoformat(),
            "first_payment_due_date": yesterday,
        },
        headers=headers,
    )
    payment_id = (await client.get("/api/payments", headers=headers)).json()["items"][0]["id"]

    access_response = await client.post(
        "/api/access-control/check",
        json={"cpf": "12345678901"},
        headers=headers,
    )
    payment_response = await client.get(f"/api/payments/{payment_id}", headers=headers)

    assert enrollment_response.status_code == 201
    assert access_response.status_code == 200
    assert access_response.json()["allowed"] is False
    assert access_response.json()["reason"] == AccessDeniedReason.PAYMENT_OVERDUE
    assert payment_response.json()["status"] == "OVERDUE"
    await assert_latest_access_log(
        student_id=student_id,
        cpf_attempted="12345678901",
        allowed=False,
        reason=AccessDeniedReason.PAYMENT_OVERDUE,
    )


async def test_cannot_create_second_active_enrollment(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    student_id, plan_id = await create_student_and_plan(client, headers)
    payload = {
        "student_id": student_id,
        "plan_id": plan_id,
        "start_date": "2026-05-08",
    }

    first_response = await client.post("/api/enrollments", json=payload, headers=headers)
    second_response = await client.post("/api/enrollments", json=payload, headers=headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["error"]["code"] == "ACTIVE_ENROLLMENT_ALREADY_EXISTS"


async def test_access_denied_for_missing_student_generates_log(client: AsyncClient) -> None:
    headers = await auth_headers(client)

    response = await client.post(
        "/api/access-control/check",
        json={"cpf": "00000000000"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "student_id": None,
        "cpf_attempted": "00000000000",
        "allowed": False,
        "reason": AccessDeniedReason.STUDENT_NOT_FOUND,
    }
    await assert_latest_access_log(
        student_id=None,
        cpf_attempted="00000000000",
        allowed=False,
        reason=AccessDeniedReason.STUDENT_NOT_FOUND,
    )


async def test_access_denied_for_inactive_student_generates_log(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    student_response = await client.post(
        "/api/students",
        json=student_payload(status="INACTIVE"),
        headers=headers,
    )

    response = await client.post(
        "/api/access-control/check",
        json={"cpf": "12345678901"},
        headers=headers,
    )

    assert student_response.status_code == 201
    assert response.status_code == 200
    assert response.json()["allowed"] is False
    assert response.json()["reason"] == AccessDeniedReason.STUDENT_INACTIVE
    await assert_latest_access_log(
        student_id=student_response.json()["id"],
        cpf_attempted="12345678901",
        allowed=False,
        reason=AccessDeniedReason.STUDENT_INACTIVE,
    )


async def test_access_denied_without_active_enrollment_generates_log(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    student_response = await client.post("/api/students", json=student_payload(), headers=headers)

    response = await client.post(
        "/api/access-control/check",
        json={"cpf": "12345678901"},
        headers=headers,
    )

    assert student_response.status_code == 201
    assert response.status_code == 200
    assert response.json()["allowed"] is False
    assert response.json()["reason"] == AccessDeniedReason.NO_ACTIVE_ENROLLMENT
    await assert_latest_access_log(
        student_id=student_response.json()["id"],
        cpf_attempted="12345678901",
        allowed=False,
        reason=AccessDeniedReason.NO_ACTIVE_ENROLLMENT,
    )


async def test_access_denied_for_expired_enrollment_generates_log(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    student_id, plan_id = await create_student_and_plan(client, headers)
    enrollment_response = await client.post(
        "/api/enrollments",
        json={
            "student_id": student_id,
            "plan_id": plan_id,
            "start_date": (date.today() - timedelta(days=31)).isoformat(),
        },
        headers=headers,
    )

    response = await client.post(
        "/api/access-control/check",
        json={"cpf": "12345678901"},
        headers=headers,
    )

    assert enrollment_response.status_code == 201
    assert response.status_code == 200
    assert response.json()["allowed"] is False
    assert response.json()["reason"] == AccessDeniedReason.ENROLLMENT_EXPIRED
    await assert_latest_access_log(
        student_id=student_id,
        cpf_attempted="12345678901",
        allowed=False,
        reason=AccessDeniedReason.ENROLLMENT_EXPIRED,
    )
