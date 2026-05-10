# Final Presentation

## 1. System Overview

Gym Management System is a web application for replacing paper and spreadsheet controls in a gym. It supports administrative operations, access control, workout sheets, payments, reports, and a dashboard.

## 2. User Profiles

- Admin: full system access.
- Receptionist: students, plans, enrollments, payments, access control, reports, and read-only workout data.
- Instructor: students in read-only mode, workout plans, exercises, exercise progress, and workout reports.

## 3. Demonstration Script

1. Open the application at `http://localhost:3000`.
2. Sign in with an admin user.
3. Create a plan in `Plans`.
4. Create a student in `Students`, including phone and address.
5. Confirm the student's cadastral status and financial status in the table.
6. Create an enrollment in `Enrollments` by selecting the student and plan by name.
7. Confirm the enrollment payment status in the enrollment table.
8. Open `Payments` and confirm the generated pending payment.
9. Mark the payment as paid.
10. Open `Access Control` and check access by CPF.
11. Create an instructor user through the API or use an existing instructor.
12. Open `Workouts`, create a workout plan for the student, and add exercises with sets, repetitions, load, and notes.
13. Record exercise progress.
14. Open `Reports` and show active students, defaulters, most-used plans, revenue, daily access, and workout summary.
15. Open `Dashboard` and show active students, defaulters, expected revenue, access frequency, plan usage, and workout indicators.

## 4. Main Screens

- Login
- Dashboard
- Students
- Plans
- Enrollments
- Payments
- Access Control
- Workouts
- Reports

## 5. Requirement Coverage

- Student registration: implemented.
- Plan management: implemented.
- Student enrollment: implemented.
- Payment tracking and delinquency: implemented as derived financial status.
- Access control: implemented through CPF checks and access logs.
- Workout sheet: implemented through workout plans and exercises.
- Basic reports: implemented.
- Dashboard indicators: implemented.

## 6. Technical Summary

- Frontend: React, TypeScript, Vite, Axios.
- Backend: FastAPI, SQLAlchemy async, Pydantic, Alembic.
- Database: PostgreSQL.
- Infrastructure: Docker Compose.
- Authentication: JWT bearer tokens.
- Authorization: role-based backend dependencies.

## 7. Validation Commands

```bash
docker compose run --rm backend pytest
docker compose run --rm backend ruff check .
docker compose run --rm backend mypy app
docker compose run --rm frontend-dev npm run build
docker compose run --rm frontend-dev npm run lint
docker compose up --build -d
docker compose ps
```

## 8. Known Limitations

- Payment gateway integration is not included.
- Email notifications are not included.
- Real turnstile or hardware integration is not included.
- Advanced exports such as PDF and CSV are not included.
- Physical evolution charts can be expanded from exercise progress history in a future iteration.
