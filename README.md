# Gym Management System

Base full-stack foundation for a future gym management platform. Phase 1 focuses on architecture, infrastructure, observability, PostgreSQL connectivity, and code quality only.

## Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy 2 async, AsyncPG, Alembic, Pydantic Settings, Structlog
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

## Alembic

Migrations are configured for SQLAlchemy async and read `DATABASE_URL` from environment settings.

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
