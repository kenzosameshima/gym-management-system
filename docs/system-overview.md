The current structure of `gym-management-system` is organized as a full-stack application with a FastAPI backend, React frontend, and PostgreSQL managed through Docker Compose.

## Overview

```text
gym-management-system/
├── backend/
├── frontend/
├── docs/
├── docker-compose.yml
├── Makefile
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── AGENTS.md
```

## Backend

The backend is located in `backend/` and follows a layered architecture:

```text
API Layer
Service Layer
Repository Layer
Database Layer
```

Main structure:

```text
backend/
├── app/
│   ├── api/
│   ├── auth/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── tests/
│   └── main.py
├── alembic/
├── alembic.ini
├── pyproject.toml
└── Dockerfile
```

Responsibilities:

- `app/api`: defines HTTP endpoints.
- `app/services`: contains business rules.
- `app/repositories`: handles queries and persistence.
- `app/models`: SQLAlchemy models.
- `app/schemas`: Pydantic input/output schemas.
- `app/auth`: JWT, password hashing, current user handling, and role permissions.
- `app/core`: configuration, enums, logging, middleware, and exceptions.
- `app/database`: engine, sessions, and declarative base.
- `app/tests`: automated tests.
- `alembic`: database migrations.

Main backend domains:

```text
auth
users
students
plans
enrollments
payments
access control
workouts
reports
health
```

## Frontend

The frontend is located in `frontend/` and uses React, TypeScript, Vite, and Axios.

```text
frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── contexts/
│   ├── hooks/
│   ├── layouts/
│   ├── pages/
│   ├── routes/
│   ├── styles/
│   ├── types/
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── vite.config.ts
├── tsconfig.json
├── nginx.conf
└── Dockerfile
```

Responsibilities:

- `src/api`: Axios clients used to consume backend APIs.
- `src/pages`: main system pages.
- `src/components`: reusable UI components such as tables, charts, cards, and state components.
- `src/contexts`: authentication context.
- `src/routes`: protected routes and role-based route handling.
- `src/layouts`: authenticated layout and navigation.
- `src/types`: TypeScript domain types.
- `src/styles`: global CSS styles.

Main frontend routes:

```text
/login
/dashboard
/students
/plans
/enrollments
/payments
/access-control
/workouts
/reports
```

## Database

The database uses PostgreSQL. Main entities:

```text
users
students
plans
enrollments
payments
access_logs
workout_plans
exercises
exercise_progress
```

Main relationships:

- `students` have `enrollments`.
- `plans` are linked to `enrollments`.
- `enrollments` generate `payments`.
- `access_logs` register CPF-based access attempts.
- `users` with the `INSTRUCTOR` role can be linked to `workout_plans`.
- `workout_plans` contain `exercises`.
- `exercises` have historical records in `exercise_progress`.

## Documentation

The `docs/` directory contains technical and academic documentation:

```text
docs/
├── architecture/
│   └── overview.md
├── releases/
│   └── v1.0.0.md
├── security-notes.md
├── requirements.md
└── presentation.md
```

Contents include:

- architecture description;
- use-case diagram;
- ER diagram;
- architecture diagram;
- functional and non-functional requirements;
- presentation script;
- release notes;
- security notes.

## Infrastructure

The project runs through Docker Compose:

```text
docker-compose.yml
```

Services:

```text
postgres
backend
frontend
frontend-dev
```

Main ports:

```text
Frontend: http://localhost:3000
Backend: http://localhost:8000
Swagger: http://localhost:8000/docs
PostgreSQL: localhost:5432
```

## Core Rules

- Students have a cadastral status: `ACTIVE` or `INACTIVE`.
- Delinquency is not stored directly on students; it is derived from payments and exposed as financial status.
- Enrollments have the statuses: `ACTIVE`, `EXPIRED`, `CANCELLED`.
- Payments have the statuses: `PENDING`, `PAID`, `OVERDUE`.
- Access control grants entry only if:
  - the student exists;
  - the student is active;
  - the student has an active enrollment;
  - the enrollment is not expired;
  - there are no overdue payments.
- Every access attempt generates an `AccessLog`, including attempts with nonexistent CPFs.
- Access logs can be queried by `ADMIN` and `RECEPTIONIST`.
- Instructors can manage workout plans, exercises, and exercise progress tracking.
- The reporting layer is read-only and separated from CRUD services.
- The dashboard consumes report endpoints instead of using a single dashboard endpoint.
