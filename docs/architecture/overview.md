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
