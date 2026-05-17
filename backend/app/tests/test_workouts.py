from itertools import count

from httpx import AsyncClient

from app.tests.test_students_plans import auth_headers, student_payload

_student_sequence = count(1)


def workout_plan_payload(student_id: int, instructor_id: int) -> dict[str, int | str]:
    return {
        "student_id": student_id,
        "instructor_id": instructor_id,
        "goal": "Hypertrophy",
        "notes": "Three sessions per week",
    }


def exercise_payload(name: str = "Bench press") -> dict[str, int | str]:
    return {
        "name": name,
        "muscle_group": "Chest",
        "sets": 4,
        "repetitions": 10,
        "load": "40.00",
        "notes": "Controlled tempo",
    }


async def auth_headers_and_user_id(client: AsyncClient, role: str) -> tuple[dict[str, str], int]:
    headers = await auth_headers(client, role=role)
    me_response = await client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    return headers, int(me_response.json()["id"])


async def create_student(
    client: AsyncClient,
    headers: dict[str, str],
    *,
    active: bool = True,
) -> int:
    sequence = next(_student_sequence)
    response = await client.post(
        "/api/students",
        json=student_payload(
            cpf=f"{sequence:011d}",
            email=f"student-{sequence}@example.com",
            status="ACTIVE" if active else "INACTIVE",
        ),
        headers=headers,
    )
    assert response.status_code == 201
    return int(response.json()["id"])


async def create_workout_plan(
    client: AsyncClient,
    headers: dict[str, str],
    *,
    student_id: int,
    instructor_id: int,
) -> int:
    response = await client.post(
        "/api/workout-plans",
        json=workout_plan_payload(student_id, instructor_id),
        headers=headers,
    )
    assert response.status_code == 201
    return int(response.json()["id"])


async def create_exercise(
    client: AsyncClient,
    headers: dict[str, str],
    workout_plan_id: int,
) -> int:
    response = await client.post(
        f"/api/workout-plans/{workout_plan_id}/exercises",
        json=exercise_payload(),
        headers=headers,
    )
    assert response.status_code == 201
    return int(response.json()["id"])


async def test_create_workout_plan_for_active_student(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    student_id = await create_student(client, admin_headers)

    response = await client.post(
        "/api/workout-plans",
        json=workout_plan_payload(student_id, instructor_id),
        headers=instructor_headers,
    )

    assert response.status_code == 201
    assert response.json()["student_id"] == student_id
    assert response.json()["instructor_id"] == instructor_id
    assert response.json()["status"] == "ACTIVE"


async def test_block_workout_plan_for_inactive_student(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    student_id = await create_student(client, admin_headers, active=False)

    response = await client.post(
        "/api/workout-plans",
        json=workout_plan_payload(student_id, instructor_id),
        headers=instructor_headers,
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "STUDENT_INACTIVE"


async def test_create_exercise_in_active_workout_plan(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    student_id = await create_student(client, admin_headers)
    workout_plan_id = await create_workout_plan(
        client,
        instructor_headers,
        student_id=student_id,
        instructor_id=instructor_id,
    )

    response = await client.post(
        f"/api/workout-plans/{workout_plan_id}/exercises",
        json=exercise_payload(),
        headers=instructor_headers,
    )

    assert response.status_code == 201
    assert response.json()["workout_plan_id"] == workout_plan_id
    assert response.json()["status"] == "ACTIVE"


async def test_block_exercise_in_inactive_workout_plan(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    student_id = await create_student(client, admin_headers)
    workout_plan_id = await create_workout_plan(
        client,
        instructor_headers,
        student_id=student_id,
        instructor_id=instructor_id,
    )
    delete_response = await client.delete(
        f"/api/workout-plans/{workout_plan_id}",
        headers=instructor_headers,
    )

    response = await client.post(
        f"/api/workout-plans/{workout_plan_id}/exercises",
        json=exercise_payload(),
        headers=instructor_headers,
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "INACTIVE"
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "WORKOUT_PLAN_INACTIVE"


async def test_register_exercise_progress(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    student_id = await create_student(client, admin_headers)
    workout_plan_id = await create_workout_plan(
        client,
        instructor_headers,
        student_id=student_id,
        instructor_id=instructor_id,
    )
    exercise_id = await create_exercise(client, instructor_headers, workout_plan_id)

    response = await client.post(
        "/api/exercise-progress",
        json={
            "student_id": student_id,
            "exercise_id": exercise_id,
            "load": "42.50",
            "repetitions": 11,
            "notes": "Progressive overload",
        },
        headers=instructor_headers,
    )

    assert response.status_code == 201
    assert response.json()["student_id"] == student_id
    assert response.json()["exercise_id"] == exercise_id
    assert response.json()["load"] == "42.50"
    assert response.json()["repetitions"] == 11


async def test_block_progress_when_exercise_belongs_to_another_student(
    client: AsyncClient,
) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    first_student_id = await create_student(client, admin_headers)
    second_student_id = await create_student(client, admin_headers)
    workout_plan_id = await create_workout_plan(
        client,
        instructor_headers,
        student_id=first_student_id,
        instructor_id=instructor_id,
    )
    exercise_id = await create_exercise(client, instructor_headers, workout_plan_id)

    response = await client.post(
        "/api/exercise-progress",
        json={
            "student_id": second_student_id,
            "exercise_id": exercise_id,
            "load": "42.50",
            "repetitions": 11,
        },
        headers=instructor_headers,
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EXERCISE_STUDENT_MISMATCH"


async def test_block_progress_for_exercise_in_inactive_workout_plan(
    client: AsyncClient,
) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    student_id = await create_student(client, admin_headers)
    workout_plan_id = await create_workout_plan(
        client,
        instructor_headers,
        student_id=student_id,
        instructor_id=instructor_id,
    )
    exercise_id = await create_exercise(client, instructor_headers, workout_plan_id)
    delete_response = await client.delete(
        f"/api/workout-plans/{workout_plan_id}",
        headers=instructor_headers,
    )

    response = await client.post(
        "/api/exercise-progress",
        json={
            "student_id": student_id,
            "exercise_id": exercise_id,
            "load": "42.50",
            "repetitions": 11,
        },
        headers=instructor_headers,
    )

    assert delete_response.status_code == 200
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "WORKOUT_PLAN_INACTIVE"


async def test_block_progress_for_inactive_exercise(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    student_id = await create_student(client, admin_headers)
    workout_plan_id = await create_workout_plan(
        client,
        instructor_headers,
        student_id=student_id,
        instructor_id=instructor_id,
    )
    exercise_id = await create_exercise(client, instructor_headers, workout_plan_id)
    delete_response = await client.delete(
        f"/api/exercises/{exercise_id}",
        headers=instructor_headers,
    )

    response = await client.post(
        "/api/exercise-progress",
        json={
            "student_id": student_id,
            "exercise_id": exercise_id,
            "load": "42.50",
            "repetitions": 11,
        },
        headers=instructor_headers,
    )

    assert delete_response.status_code == 200
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EXERCISE_INACTIVE"


async def test_list_exercise_progress_by_student_preserves_history(
    client: AsyncClient,
) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    student_id = await create_student(client, admin_headers)
    workout_plan_id = await create_workout_plan(
        client,
        instructor_headers,
        student_id=student_id,
        instructor_id=instructor_id,
    )
    exercise_id = await create_exercise(client, instructor_headers, workout_plan_id)

    first_response = await client.post(
        "/api/exercise-progress",
        json={
            "student_id": student_id,
            "exercise_id": exercise_id,
            "load": "40.00",
            "repetitions": 10,
        },
        headers=instructor_headers,
    )
    second_response = await client.post(
        "/api/exercise-progress",
        json={
            "student_id": student_id,
            "exercise_id": exercise_id,
            "load": "45.00",
            "repetitions": 8,
        },
        headers=instructor_headers,
    )
    list_response = await client.get(
        f"/api/exercise-progress/student/{student_id}",
        headers=admin_headers,
    )
    filtered_response = await client.get(
        f"/api/exercise-progress/student/{student_id}/exercise/{exercise_id}",
        headers=admin_headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2
    assert filtered_response.status_code == 200
    assert [item["load"] for item in filtered_response.json()] == ["40.00", "45.00"]


async def test_instructor_can_create_and_edit_workout_domain(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    student_id = await create_student(client, admin_headers)

    create_plan_response = await client.post(
        "/api/workout-plans",
        json=workout_plan_payload(student_id, instructor_id),
        headers=instructor_headers,
    )
    workout_plan_id = create_plan_response.json()["id"]
    update_plan_response = await client.put(
        f"/api/workout-plans/{workout_plan_id}",
        json={"goal": "Strength"},
        headers=instructor_headers,
    )
    create_exercise_response = await client.post(
        f"/api/workout-plans/{workout_plan_id}/exercises",
        json=exercise_payload(),
        headers=instructor_headers,
    )
    exercise_id = create_exercise_response.json()["id"]
    update_exercise_response = await client.put(
        f"/api/exercises/{exercise_id}",
        json={"sets": 5},
        headers=instructor_headers,
    )

    assert create_plan_response.status_code == 201
    assert update_plan_response.status_code == 200
    assert update_plan_response.json()["goal"] == "Strength"
    assert create_exercise_response.status_code == 201
    assert update_exercise_response.status_code == 200
    assert update_exercise_response.json()["sets"] == 5


async def test_receptionist_cannot_access_workout_domain(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    receptionist_headers = await auth_headers(client, role="RECEPTIONIST")
    student_id = await create_student(client, admin_headers)
    workout_plan_id = await create_workout_plan(
        client,
        instructor_headers,
        student_id=student_id,
        instructor_id=instructor_id,
    )

    create_response = await client.post(
        "/api/workout-plans",
        json=workout_plan_payload(student_id, instructor_id),
        headers=receptionist_headers,
    )
    update_response = await client.put(
        f"/api/workout-plans/{workout_plan_id}",
        json={"goal": "Strength"},
        headers=receptionist_headers,
    )
    read_response = await client.get(
        f"/api/workout-plans/{workout_plan_id}",
        headers=receptionist_headers,
    )

    assert create_response.status_code == 403
    assert update_response.status_code == 403
    assert read_response.status_code == 403


async def test_only_admin_can_list_system_users(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    instructor_headers = await auth_headers(client, role="INSTRUCTOR")
    receptionist_headers = await auth_headers(client, role="RECEPTIONIST")

    admin_response = await client.get("/api/users", headers=admin_headers)
    instructor_response = await client.get("/api/users", headers=instructor_headers)
    receptionist_response = await client.get("/api/users", headers=receptionist_headers)

    assert admin_response.status_code == 200
    assert instructor_response.status_code == 403
    assert receptionist_response.status_code == 403


async def test_admin_can_transfer_active_workout_plans_between_instructors(
    client: AsyncClient,
) -> None:
    admin_headers = await auth_headers(client)
    _, first_instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")
    second_instructor_response = await client.post(
        "/api/users",
        json={
            "email": "second-instructor@example.com",
            "full_name": "Second Instructor",
            "password": "strong-password",
            "role": "INSTRUCTOR",
        },
        headers=admin_headers,
    )
    second_instructor_id = second_instructor_response.json()["id"]
    student_id = await create_student(client, admin_headers)
    workout_plan_id = await create_workout_plan(
        client,
        admin_headers,
        student_id=student_id,
        instructor_id=first_instructor_id,
    )

    transfer_response = await client.post(
        "/api/workout-plans/transfer",
        json={
            "from_instructor_id": first_instructor_id,
            "to_instructor_id": second_instructor_id,
            "status": "ACTIVE",
        },
        headers=admin_headers,
    )
    get_response = await client.get(
        f"/api/workout-plans/{workout_plan_id}",
        headers=admin_headers,
    )

    assert second_instructor_response.status_code == 201
    assert transfer_response.status_code == 200
    assert transfer_response.json()["transferred_count"] == 1
    assert get_response.json()["instructor_id"] == second_instructor_id


async def test_block_transfer_to_same_instructor(client: AsyncClient) -> None:
    admin_headers = await auth_headers(client)
    _, instructor_id = await auth_headers_and_user_id(client, "INSTRUCTOR")

    response = await client.post(
        "/api/workout-plans/transfer",
        json={
            "from_instructor_id": instructor_id,
            "to_instructor_id": instructor_id,
            "status": "ACTIVE",
        },
        headers=admin_headers,
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "SAME_INSTRUCTOR_TRANSFER"
