from datetime import UTC, date, datetime
from decimal import Decimal

from httpx import AsyncClient

from app.core.enums import PaymentStatus
from app.database.session import AsyncSessionFactory
from app.models.access_log import AccessLog
from app.models.payment import Payment
from app.tests.test_students_plans import auth_headers, plan_payload, student_payload
from app.tests.test_workouts import exercise_payload, workout_plan_payload


async def create_student(
    client: AsyncClient,
    headers: dict[str, str],
    *,
    cpf: str = "12345678901",
    email: str = "student@example.com",
    status: str = "ACTIVE",
) -> int:
    response = await client.post(
        "/api/students",
        json=student_payload(cpf=cpf, email=email, status=status),
        headers=headers,
    )
    assert response.status_code == 201
    return int(response.json()["id"])


async def create_plan(
    client: AsyncClient,
    headers: dict[str, str],
    *,
    name: str = "Monthly Plan",
    price: str = "100.00",
) -> int:
    response = await client.post(
        "/api/plans",
        json=plan_payload(name=name, price=price),
        headers=headers,
    )
    assert response.status_code == 201
    return int(response.json()["id"])


async def create_enrollment(
    client: AsyncClient,
    headers: dict[str, str],
    *,
    student_id: int,
    plan_id: int,
    start_date: str = "2026-05-01",
    first_payment_due_date: str | None = None,
) -> int:
    payload: dict[str, int | str] = {
        "student_id": student_id,
        "plan_id": plan_id,
        "start_date": start_date,
    }
    if first_payment_due_date is not None:
        payload["first_payment_due_date"] = first_payment_due_date
    response = await client.post("/api/enrollments", json=payload, headers=headers)
    assert response.status_code == 201
    return int(response.json()["id"])


async def latest_payment_id(client: AsyncClient, headers: dict[str, str]) -> int:
    response = await client.get("/api/payments", headers=headers)
    assert response.status_code == 200
    return int(response.json()["items"][-1]["id"])


async def create_overdue_payment(
    *,
    enrollment_id: int,
    amount: str,
    due_date: date,
) -> None:
    async with AsyncSessionFactory() as session:
        session.add(
            Payment(
                enrollment_id=enrollment_id,
                amount=Decimal(amount),
                due_date=due_date,
                status=PaymentStatus.OVERDUE,
            )
        )
        await session.commit()


async def auth_headers_and_user_id(client: AsyncClient, role: str) -> tuple[dict[str, str], int]:
    headers = await auth_headers(client, role=role)
    response = await client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    return headers, int(response.json()["id"])


async def test_active_students_report_returns_only_active_students(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    active_student_id = await create_student(client, headers)
    await create_student(
        client,
        headers,
        cpf="98765432100",
        email="inactive@example.com",
        status="INACTIVE",
    )

    response = await client.get("/api/reports/students/active", headers=headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["students"][0]["id"] == active_student_id
    assert response.json()["students"][0]["status"] == "ACTIVE"


async def test_defaulters_report_returns_overdue_students_and_sums_amount(
    client: AsyncClient,
) -> None:
    headers = await auth_headers(client)
    overdue_student_id = await create_student(client, headers)
    clean_student_id = await create_student(
        client,
        headers,
        cpf="98765432100",
        email="clean@example.com",
    )
    plan_id = await create_plan(client, headers, price="150.00")
    clean_plan_id = await create_plan(client, headers, name="Clean Plan", price="80.00")
    overdue_enrollment_id = await create_enrollment(
        client,
        headers,
        student_id=overdue_student_id,
        plan_id=plan_id,
        first_payment_due_date="2026-05-10",
    )
    overdue_payment_id = await latest_payment_id(client, headers)
    await client.put(
        f"/api/payments/{overdue_payment_id}",
        json={"status": "OVERDUE"},
        headers=headers,
    )
    await create_overdue_payment(
        enrollment_id=overdue_enrollment_id,
        amount="50.00",
        due_date=date(2026, 5, 20),
    )
    await create_enrollment(
        client,
        headers,
        student_id=clean_student_id,
        plan_id=clean_plan_id,
        first_payment_due_date="2026-05-10",
    )

    response = await client.get("/api/reports/students/defaulters", headers=headers)

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["students"][0]["student_id"] == overdue_student_id
    assert response.json()["students"][0]["overdue_amount"] == "200.00"
    assert response.json()["students"][0]["overdue_payments"] == 2


async def test_most_used_plans_counts_and_orders_descending(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    plan_a_id = await create_plan(client, headers, name="Plan A")
    plan_b_id = await create_plan(client, headers, name="Plan B")
    first_student_id = await create_student(client, headers)
    second_student_id = await create_student(
        client,
        headers,
        cpf="98765432100",
        email="second@example.com",
    )
    third_student_id = await create_student(
        client,
        headers,
        cpf="11122233344",
        email="third@example.com",
    )
    await create_enrollment(client, headers, student_id=first_student_id, plan_id=plan_a_id)
    await create_enrollment(client, headers, student_id=second_student_id, plan_id=plan_a_id)
    await create_enrollment(client, headers, student_id=third_student_id, plan_id=plan_b_id)

    response = await client.get("/api/reports/plans/most-used", headers=headers)

    assert response.status_code == 200
    assert response.json()["plans"][0] == {
        "plan_id": plan_a_id,
        "plan_name": "Plan A",
        "enrollments_count": 2,
    }
    assert response.json()["plans"][1] == {
        "plan_id": plan_b_id,
        "plan_name": "Plan B",
        "enrollments_count": 1,
    }


async def test_revenue_summary_calculates_totals_and_respects_date_filter(
    client: AsyncClient,
) -> None:
    headers = await auth_headers(client)
    plan_id = await create_plan(client, headers, price="100.00")
    student_one_id = await create_student(client, headers)
    student_two_id = await create_student(
        client,
        headers,
        cpf="98765432100",
        email="two@example.com",
    )
    student_three_id = await create_student(
        client,
        headers,
        cpf="11122233344",
        email="three@example.com",
    )
    student_four_id = await create_student(
        client,
        headers,
        cpf="55566677788",
        email="four@example.com",
    )

    await create_enrollment(
        client,
        headers,
        student_id=student_one_id,
        plan_id=plan_id,
        first_payment_due_date="2026-05-05",
    )
    paid_payment_id = await latest_payment_id(client, headers)
    await client.put(f"/api/payments/{paid_payment_id}", json={"status": "PAID"}, headers=headers)
    await create_enrollment(
        client,
        headers,
        student_id=student_two_id,
        plan_id=plan_id,
        first_payment_due_date="2026-05-10",
    )
    overdue_payment_id = await latest_payment_id(client, headers)
    await client.put(
        f"/api/payments/{overdue_payment_id}",
        json={"status": "OVERDUE"},
        headers=headers,
    )
    await create_enrollment(
        client,
        headers,
        student_id=student_three_id,
        plan_id=plan_id,
        first_payment_due_date="2026-05-15",
    )
    await create_enrollment(
        client,
        headers,
        student_id=student_four_id,
        plan_id=plan_id,
        first_payment_due_date="2026-06-15",
    )

    response = await client.get(
        "/api/reports/revenue/summary?start_date=2026-05-01&end_date=2026-05-31",
        headers=headers,
    )
    invalid_response = await client.get(
        "/api/reports/revenue/summary?start_date=2026-06-01&end_date=2026-05-01",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "expected_revenue": "300.00",
        "received_revenue": "100.00",
        "overdue_revenue": "100.00",
        "pending_revenue": "100.00",
    }
    assert invalid_response.status_code == 422


async def test_daily_access_report_groups_counts_and_respects_filter(
    client: AsyncClient,
) -> None:
    headers = await auth_headers(client)
    async with AsyncSessionFactory() as session:
        session.add_all(
            [
                AccessLog(
                    student_id=None,
                    cpf_attempted="11111111111",
                    accessed_at=datetime(2026, 5, 1, 10, tzinfo=UTC),
                    allowed=True,
                    reason=None,
                ),
                AccessLog(
                    student_id=None,
                    cpf_attempted="22222222222",
                    accessed_at=datetime(2026, 5, 1, 11, tzinfo=UTC),
                    allowed=False,
                    reason=None,
                ),
                AccessLog(
                    student_id=None,
                    cpf_attempted="33333333333",
                    accessed_at=datetime(2026, 5, 2, 10, tzinfo=UTC),
                    allowed=True,
                    reason=None,
                ),
            ]
        )
        await session.commit()

    response = await client.get(
        "/api/reports/access/daily?start_date=2026-05-01&end_date=2026-05-01",
        headers=headers,
    )
    invalid_response = await client.get(
        "/api/reports/access/daily?start_date=2026-05-02&end_date=2026-05-01",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["days"] == [
        {
            "date": "2026-05-01",
            "total_attempts": 2,
            "allowed_count": 1,
            "blocked_count": 1,
        }
    ]
    assert invalid_response.status_code == 422


async def test_workout_summary_counts_domain_records(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    student_id = await create_student(client, admin_headers)
    workout_response = await client.post(
        "/api/workout-plans",
        json=workout_plan_payload(student_id, instructor_id),
        headers=instructor_headers,
    )
    workout_plan_id = workout_response.json()["id"]
    exercise_response = await client.post(
        f"/api/workout-plans/{workout_plan_id}/exercises",
        json=exercise_payload(),
        headers=instructor_headers,
    )
    exercise_id = exercise_response.json()["id"]
    progress_response = await client.post(
        "/api/exercise-progress",
        json={"student_id": student_id, "exercise_id": exercise_id, "repetitions": 10},
        headers=instructor_headers,
    )
    inactive_response = await client.delete(
        f"/api/workout-plans/{workout_plan_id}",
        headers=instructor_headers,
    )

    response = await client.get("/api/reports/workouts/summary", headers=instructor_headers)

    assert workout_response.status_code == 201
    assert exercise_response.status_code == 201
    assert progress_response.status_code == 201
    assert inactive_response.status_code == 200
    assert response.status_code == 200
    assert response.json() == {
        "active_workout_plans": 0,
        "inactive_workout_plans": 1,
        "total_exercises": 1,
        "exercise_progress_records": 1,
    }


async def test_report_permissions(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    receptionist_headers = await auth_headers(client, role="RECEPTIONIST")
    instructor_headers = await auth_headers(client, role="INSTRUCTOR")

    unauthenticated_response = await client.get("/api/reports/students/active")
    instructor_financial_response = await client.get(
        "/api/reports/revenue/summary",
        headers=instructor_headers,
    )
    receptionist_workout_response = await client.get(
        "/api/reports/workouts/summary",
        headers=receptionist_headers,
    )
    instructor_workout_response = await client.get(
        "/api/reports/workouts/summary",
        headers=instructor_headers,
    )
    admin_financial_response = await client.get(
        "/api/reports/revenue/summary",
        headers=admin_headers,
    )

    assert unauthenticated_response.status_code == 401
    assert instructor_financial_response.status_code == 403
    assert receptionist_workout_response.status_code == 403
    assert instructor_workout_response.status_code == 200
    assert admin_financial_response.status_code == 200
