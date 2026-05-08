# Gym Management System

Base full-stack foundation for a future gym management platform. The current foundation includes infrastructure, observability, PostgreSQL connectivity, code quality, and initial JWT authentication with user roles.

## Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy 2 async, AsyncPG, Alembic, Pydantic Settings, Structlog
- Auth: JWT, passlib/bcrypt password hashing, role-based access foundations
- Frontend: React 18, TypeScript, Vite, Axios
- Infra: Docker, Docker Compose, PostgreSQL 16, Nginx
- Quality: Ruff, Black, MyPy, Pytest, Pre-commit

## Architecture

The backend follows a strict layered flow:

```text
API Layer
Service Layer
Repository Layer
Database Layer
```

Routes do not access the database directly. Configuration, logging, middleware, global exception handling, and domain enums live in `backend/app/core`.

## Folder Structure

```text
backend/app/api          FastAPI routers
backend/app/core         config, logging, middleware, exceptions, domain enums
backend/app/database     async engine, sessions, declarative base
backend/app/repositories data access boundaries
backend/app/services     application orchestration
backend/app/schemas      Pydantic response/request schemas
frontend/src             React application source
docs/architecture        architecture notes
```

## Run

```bash
docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432

Development frontend with Vite hot reload:

```bash
docker compose --profile dev up frontend-dev
```

## Environment

Backend variables are documented in `backend/.env.example`:

- `APP_NAME`
- `APP_ENV`
- `DEBUG`
- `LOG_LEVEL`
- `SECRET_KEY`
- `DATABASE_URL`
- `BACKEND_CORS_ORIGINS`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

Frontend variables are documented in `frontend/.env.example`:

- `VITE_API_URL`

For real deployments, create non-versioned `.env` files and replace all development credentials and secrets.

## Useful Commands

On Unix-like shells with `make` installed:

```bash
make up
make down
make logs
make backend
make frontend
make test
make lint
make format
```

On Windows PowerShell without `make`, use the equivalent Docker Compose commands:

```powershell
docker compose up --build
docker compose down
docker compose logs -f
docker compose up --build backend
docker compose up --build frontend
docker compose run --rm backend pytest
docker compose run --rm backend ruff check .
docker compose run --rm backend mypy app
docker compose run --rm frontend-dev sh -c "npm install && npm run lint"
docker compose run --rm backend ruff check . --fix
docker compose run --rm backend black .
```

## Health Checks

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

Expected responses:

```json
{"status":"alive"}
```

```json
{"status":"ready","database":"connected"}
```

The readiness endpoint validates a real async PostgreSQL connection.

## Authentication

Available authentication endpoints:

```bash
POST /api/auth/register
POST /api/auth/login
GET /api/auth/me
```

Register example:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","full_name":"Admin User","password":"strong-password","role":"ADMIN"}'
```

Login example:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"strong-password"}'
```

Authenticated user example:

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

Supported roles:

- `ADMIN`
- `RECEPTIONIST`
- `INSTRUCTOR`

User responses never expose `password_hash`.

## Students

All student endpoints require JWT authentication.

```bash
POST /api/students
GET /api/students
GET /api/students/{student_id}
PUT /api/students/{student_id}
DELETE /api/students/{student_id}
```

Permissions:

- `ADMIN`: full access
- `RECEPTIONIST`: full access
- `INSTRUCTOR`: read-only access to `GET /api/students` and `GET /api/students/{student_id}`

Student rules:

- `cpf` is required, unique, and must contain 11 digits or use `000.000.000-00`.
- `email` is required, valid, and unique.
- `birth_date` cannot be in the future.
- `status` represents only the cadastral state of the student: `ACTIVE` or `INACTIVE`.
- `DELETE` performs a soft delete by setting `status` to `INACTIVE`.
- Delinquency is never persisted as `Student.status`; it is derived from payment state.

## Plans

All plan endpoints require JWT authentication.

```bash
POST /api/plans
GET /api/plans
GET /api/plans/{plan_id}
PUT /api/plans/{plan_id}
DELETE /api/plans/{plan_id}
```

Permissions:

- `ADMIN`: full access
- `RECEPTIONIST`: full access
- `INSTRUCTOR`: no access to plan endpoints

Plan rules:

- `name` is required and unique.
- `price` must be greater than zero.
- `duration_days` must be greater than zero.
- `status` can be `ACTIVE` or `INACTIVE`.
- `DELETE` performs a soft delete by setting `status` to `INACTIVE`.

## Enrollments, Payments, And Access Control

Enrollment status values:

- `ACTIVE`
- `EXPIRED`
- `CANCELLED`

Payment status values:

- `PENDING`
- `PAID`
- `OVERDUE`

Financial delinquency is derived from payments. A student is considered blocked for payment reasons only when the active enrollment has an overdue payment, including pending payments whose due date has passed and are normalized to `OVERDUE`.

Access control is calculated by `AccessControlService`. The API layer only receives input and delegates the decision. Access is allowed only when:

- the student exists;
- `Student.status` is `ACTIVE`;
- the student has an active enrollment;
- the enrollment has not expired;
- the active enrollment has no overdue payment.

Every access check creates an `AccessLog`, including failed checks for nonexistent CPF values. Access logs store `cpf_attempted`, `student_id` when known, `accessed_at`, `allowed`, and the denial reason when access is blocked.

## Workout Domain

Workout planning endpoints:

```bash
POST /api/workout-plans
GET /api/workout-plans
GET /api/workout-plans/{id}
GET /api/workout-plans/student/{student_id}
PUT /api/workout-plans/{id}
DELETE /api/workout-plans/{id}
POST /api/workout-plans/{id}/exercises
GET /api/workout-plans/{id}/exercises
PUT /api/exercises/{id}
DELETE /api/exercises/{id}
POST /api/exercise-progress
GET /api/exercise-progress/student/{student_id}
GET /api/exercise-progress/student/{student_id}/exercise/{exercise_id}
```

Permissions:

- `ADMIN`: full access.
- `INSTRUCTOR`: create and edit workout plans, exercises, and progress records.
- `RECEPTIONIST`: read-only access.

Workout rules:

- Workout plans require an existing active student and an active instructor user.
- Workout plan and exercise soft deletes set `status` to `INACTIVE`.
- Exercises cannot be created in inactive workout plans.
- Exercise progress is historical; every record is appended and never overwrites prior progress.

## Reports And Analytics

Report endpoints are backend-only in this phase:

```bash
GET /api/reports/students/active
GET /api/reports/students/defaulters
GET /api/reports/plans/most-used
GET /api/reports/revenue/summary
GET /api/reports/access/daily
GET /api/reports/workouts/summary
```

Reports are read-only. Routes delegate to `ReportService`, and reporting SQL stays in
`ReportRepository` instead of CRUD repositories or services.

Permissions:

- `ADMIN`: all reports.
- `RECEPTIONIST`: active students, defaulters, most-used plans, revenue summary, and daily access.
- `INSTRUCTOR`: workout summary only.

Report rules:

- Active students are students with `Student.status = ACTIVE`.
- Defaulters are derived from `Payment.status = OVERDUE`; delinquency is not stored on `Student.status`.
- Most-used plans count enrollments grouped by plan.
- Revenue summary uses `Payment.due_date` for date filtering.
- `expected_revenue` is the sum of `PENDING`, `PAID`, and `OVERDUE` payments in the period.
- `received_revenue` is the sum of `PAID` payments in the period.
- `overdue_revenue` is the sum of `OVERDUE` payments in the period.
- `pending_revenue` is the sum of `PENDING` payments in the period.
- Daily access groups `AccessLog.accessed_at` by day and counts allowed and blocked attempts.
- Temporal filters are optional `start_date` and `end_date`; when both are present, `start_date` must be less than or equal to `end_date`.
- Reporting indexes exist for payment status and due date, access timestamps, and exercise progress timestamps. Existing student, enrollment, and exercise relationship indexes are reused.

## Alembic

Migrations are configured for SQLAlchemy async and read `DATABASE_URL` from environment settings.

The backend container runs `alembic upgrade head` before starting Uvicorn.

Example:

```bash
docker compose run --rm backend alembic revision --autogenerate -m "message"
docker compose run --rm backend alembic upgrade head
```

## Logging

Backend logs are structured JSON via Structlog and include timestamp, level, service, module, and message fields. HTTP request middleware logs method, path, status code, and request duration.

## Security Notes

`npm audit` currently reports two moderate vulnerabilities from `esbuild <=0.24.2`, pulled transitively by Vite. The advisory affects the Vite development server behavior. The production frontend image builds static assets and serves them with Nginx, so this issue is not part of the runtime container surface.

`npm audit fix` does not resolve it without `--force`; npm proposes upgrading to Vite 8, which is a breaking major upgrade. Do not run `npm audit fix --force` automatically. Revisit this when planning a controlled frontend tooling upgrade.

## Troubleshooting

- If backend readiness fails, confirm PostgreSQL is healthy with `docker compose ps`.
- If the frontend cannot reach the API, confirm `VITE_API_URL` points to `http://localhost:8000`.
- If dependencies are stale, rebuild with `docker compose build --no-cache`.
- If PostgreSQL data must be reset during development, run `docker compose down -v`.
- If `make` is unavailable on Windows, use the PowerShell Docker Compose equivalents listed above.
