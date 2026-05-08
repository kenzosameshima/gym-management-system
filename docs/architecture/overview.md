# Architecture Overview

The project uses a layered FastAPI backend and a React frontend.

Backend flow:

```text
API Layer
↓
Service Layer
↓
Repository Layer
↓
Database Layer
```

Current responsibilities:

- API layer receives HTTP input, applies authentication/authorization dependencies, and returns response models.
- Service layer owns business rules, transaction boundaries, and error mapping.
- Repository layer owns persistence operations and query composition, but does not decide business transactions.
- Database layer owns async SQLAlchemy engine and session factory.
- Core modules own configuration, domain enums, logging, middleware, and exception handling.

Domain enums are centralized in `backend/app/core/enums.py`.

Student status represents only cadastral state:

- `ACTIVE`
- `INACTIVE`

Delinquency is derived from payments, not stored on the student. Payment statuses are:

- `PENDING`
- `PAID`
- `OVERDUE`

Plan statuses are:

- `ACTIVE`
- `INACTIVE`

Enrollment statuses are:

- `ACTIVE`
- `EXPIRED`
- `CANCELLED`

Access control is calculated by `AccessControlService`. Access is allowed only when the student exists, is active, has an active non-expired enrollment, and the active enrollment has no overdue payment. Every access attempt creates an `AccessLog`, including nonexistent CPF attempts, with `cpf_attempted`, `student_id` when known, timestamp, allowed flag, and denial reason.

Workout domain is split into workout plans, exercises, and exercise progress:

- `WorkoutPlan` links one active student to one active instructor user.
- `Exercise` belongs to a workout plan and is soft-deleted with `INACTIVE` status.
- `ExerciseProgress` is append-only history for student progress on an exercise.

Workout plan and exercise writes are restricted to `ADMIN` and `INSTRUCTOR`. `RECEPTIONIST` can read workout data but cannot create or edit it.

Reports are implemented as a dedicated analytics layer:

- API: `backend/app/api/reports.py`
- Service: `backend/app/services/report_service.py`
- Repository: `backend/app/repositories/report_repository.py`
- Schemas: `backend/app/schemas/reports.py`

Reports are read-only. Aggregated queries stay out of CRUD services. `ReportRepository` uses SQL aggregates, joins, and grouping for active students, defaulters, plan usage, revenue, daily access, and workout summaries. Financial delinquency is derived from `Payment.status = OVERDUE`.

Revenue reports use `Payment.due_date` for optional `start_date` and `end_date` filters. Invalid ranges return 422. Reporting access is role-protected: `ADMIN` can access all reports, `RECEPTIONIST` can access management and financial reports, and `INSTRUCTOR` can access workout summary only.

Reporting indexes are maintained through Alembic for payment status/date, access timestamps, and exercise progress timestamps, while existing indexes on students and enrollment relationships are reused.

Frontend integration is organized as a routed React application:

- `frontend/src/api` contains typed Axios wrappers for auth, students, plans, enrollments, payments, access control, workouts, and reports.
- `frontend/src/contexts/AuthContext.tsx` owns JWT token state, localStorage persistence, `/api/auth/me` hydration, and logout.
- `frontend/src/routes` owns protected routes and role gates.
- `frontend/src/layouts/AppLayout.tsx` provides the authenticated shell and navigation.
- `frontend/src/pages` contains the first operational screens for dashboard, CRUD workflows, access checks, workouts, and reports.

The frontend stores the access token in localStorage for this phase and attaches it through the shared Axios client. Navigation is role-aware and hides inaccessible areas, but backend authorization remains the source of truth.

Known frontend limitations:

- Refresh tokens are not implemented because the backend does not expose them.
- Reporting uses simple tables and stat cards, not charts or exports.
- Access log history is not displayed because there is no backend list endpoint for recent access attempts.
- Relationship selection is ID-based in the first integration pass.
