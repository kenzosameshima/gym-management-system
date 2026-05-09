# AGENTS.md

Persistent instructions for AI agents and contributors working on this project.

## Project Overview

Gym Management System is a v1.0.0 MVP full-stack application for gym operations: auth, students, plans, enrollments, payments, access control, workouts, reports, and dashboard UX.

## Architecture Rules

- Keep the backend layered: API -> service -> repository -> database.
- API routers must not query the database directly.
- Services own business rules, transaction boundaries, and domain errors.
- Repositories own SQLAlchemy query composition and persistence details.
- Backend authorization is the source of truth; frontend role checks are only UX.
- Do not rewrite working architecture during release-prep work.

## Backend Conventions

- Use async FastAPI, SQLAlchemy async sessions, and Pydantic schemas.
- Keep enums centralized in `backend/app/core/enums.py`.
- Keep routes under `/api` except health checks.
- Use dependency-based JWT auth and role checks.
- Do not expose `password_hash`, bearer tokens, or secrets in responses/logs.
- Add Alembic migrations for schema changes and keep downgrade functions when practical.

## Frontend Conventions

- Use React, TypeScript, Vite, React Router, Axios, and existing shared components.
- Put typed HTTP calls in `frontend/src/api`.
- Put domain types in `frontend/src/types`.
- Keep protected and role-gated routing in `frontend/src/routes`.
- Keep token cleanup behavior centralized in auth/http-client code.
- Handle loading, empty, error, and unauthorized states on operational pages.

## Domain Invariants

- Students and plans are soft-deleted by setting `INACTIVE`.
- `Student.status` is only cadastral state; delinquency is derived from payments.
- Enrollments require active students and active plans.
- Access is allowed only for active students with active non-expired enrollments and no overdue payment.
- Every access check creates an access log.
- Paid payments cannot be paid again.
- Workout plans require active students and active instructor users.
- Exercise progress is append-only.

## Role Permissions

- `ADMIN`: full access to all MVP domains and reports.
- `RECEPTIONIST`: students, plans, enrollments, payments, access control, management/financial/access reports, dashboard, and read-only workouts.
- `INSTRUCTOR`: read-only students, workout management, workout summary report, and instructor dashboard metrics.

## Validation Commands

Run before release or PR handoff:

```bash
docker compose run --rm backend pytest
docker compose run --rm backend ruff check .
docker compose run --rm backend mypy app
docker compose run --rm frontend-dev npm run build
docker compose run --rm frontend-dev npm run lint
docker compose up --build -d
docker compose ps
```

Use `docker compose down -v` only when local PostgreSQL data can be discarded.

## Commit And Release Conventions

- Use concise imperative commits, for example `docs: prepare v1.0.0 release notes`.
- Keep release changes scoped and avoid unrelated refactors.
- Keep `CHANGELOG.md` updated using semantic version labels.
- `v1.0.0` stays unreleased until final validation passes and the tag is created.

## Restrictions

- Do not add payment gateways, refresh tokens, realtime websockets, mobile apps, CI/CD, Kubernetes, Redis, email notifications, or hardware/catraca integrations in this MVP release phase.
- Do not run destructive commands or reset volumes without explicit approval.
- Do not commit real `.env` files, secrets, tokens, database dumps, or personal data.

## Known Limitations

- No real payment gateway, refresh-token flow, email notifications, CSV/PDF exports, hardware integration, or mobile app.
- Frontend stores the MVP JWT in `localStorage`.
- Some relationship selection remains ID-based.
- Vite/esbuild development-server advisory remains documented until a controlled tooling upgrade.
