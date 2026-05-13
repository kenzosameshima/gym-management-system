# Final Presentation

## 1. System Overview

Gym Management System is a full-stack web application for gym operations. It replaces spreadsheet and paper workflows with authenticated staff access, role-based screens, student management, memberships, payments, check-in by CPF, workout sheets, reports, and a dashboard.

## 2. Default Demo Login

Local Docker startup creates the first admin when no active admin exists.

- Email: `admin@example.com`
- Password: `strong-password`

These credentials are development/demo placeholders only.

## 3. User Profiles

- Admin: lands on the dashboard and manages the whole system, including staff and plans.
- Receptionist: lands on students and handles front-desk operations.
- Instructor: lands on workouts and handles training workflows.

## 4. Demonstration Script

1. Open `http://localhost:3000`.
2. Sign in with `admin@example.com` / `strong-password`.
3. Show the role-aware dashboard.
4. Open **Equipe** and create a receptionist or instructor with a temporary password.
5. Log out and sign in with the created user to show mandatory password change.
6. Return as admin and show password reset and recent audit events.
7. Open **Planos** and show default plans seeded locally: Mensal, Trimestral, Semestral, Anual.
8. Create or review a student in **Alunos**.
9. Create an enrollment in **Matrículas**.
10. Confirm the generated pending payment in **Pagamentos**.
11. Mark the payment as paid.
12. Use **Check-in** to validate access by CPF.
13. Create a workout plan in **Treinos** and add exercises.
14. Record exercise progress.
15. Show **Relatórios** and explain that reports are role-aware.

## 5. Main Screens

- Login
- Mandatory password change
- Dashboard
- Equipe
- Alunos
- Planos
- Matrículas
- Pagamentos
- Check-in
- Treinos
- Relatórios

## 6. Requirement Coverage

- Authentication and role authorization: implemented.
- Initial admin seed: implemented.
- Staff CRUD and audit: implemented.
- Temporary password and reset flow: implemented.
- Student registration: implemented.
- Plan management and optional default seed: implemented.
- Student enrollment: implemented.
- Payment tracking and delinquency: implemented as derived financial status.
- Access control: implemented through CPF checks and access logs.
- Workout sheet: implemented through workout plans, exercises, and progress.
- Workout transfer between instructors: implemented.
- Reports and dashboard indicators: implemented.

## 7. Technical Summary

- Frontend: React, TypeScript, Vite, Axios.
- Backend: FastAPI, SQLAlchemy async, Pydantic, Alembic.
- Database: PostgreSQL.
- Infrastructure: Docker Compose.
- Authentication: JWT bearer tokens.
- Authorization: backend role dependencies.
- Quality: Pytest, Ruff, MyPy, TypeScript build checks.

## 8. Validation Commands

```bash
docker compose run --rm backend pytest
docker compose run --rm backend ruff check .
docker compose run --rm backend mypy app
docker compose run --rm frontend-dev npm run build
docker compose run --rm frontend-dev npm run lint
docker compose up --build -d
docker compose ps
```

## 9. Known Limitations

- Payment gateway integration is not included.
- Email-based password reset links are not included; admin sets temporary passwords manually.
- Real turnstile or hardware integration is not included.
- Advanced exports such as PDF and CSV are not included.
- Refresh tokens are not included; expired JWT sessions require login again.
