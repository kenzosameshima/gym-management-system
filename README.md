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

Routes do not access the database directly. Configuration, logging, middleware, and global exception handling live in `backend/app/core`.

## Folder Structure

```text
backend/app/api          FastAPI routers
backend/app/core         config, logging, middleware, exceptions
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
- `DELETE` performs a soft delete by setting `status` to `INACTIVE`.

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
- `DELETE` performs a soft delete by setting `status` to `INACTIVE`.

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
