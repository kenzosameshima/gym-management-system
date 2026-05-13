# Requirements

## Functional Requirements

- RF01 - The system must allow authenticated staff to register students with name, CPF, birth date, phone, email, address, and cadastral status.
- RF02 - The system must allow authorized staff to edit, list, search, and deactivate students.
- RF03 - The system must display each student's derived financial status without storing delinquency as cadastral status.
- RF04 - The system must allow administrators to register, edit, list, and deactivate gym plans.
- RF05 - The system must allow receptionists to consult active and inactive plans without changing them.
- RF06 - The system must allow authorized staff to enroll active students in active plans with start date and calculated end date.
- RF07 - The system must create an initial pending payment when an enrollment is created.
- RF08 - The system must display payment status in enrollment listings.
- RF09 - The system must allow authorized staff to register, list, update, and mark payments as paid or overdue.
- RF10 - The system must block duplicate processing of already paid payments.
- RF11 - The system must allow reception/management staff to check gym access by CPF.
- RF12 - The system must allow access only for active students with active, non-expired enrollments and no overdue payments.
- RF13 - The system must log every access attempt, including attempts for unknown CPF values.
- RF14 - The system must allow instructors and administrators to create workout plans for students.
- RF15 - The system must allow instructors and administrators to register exercises with name, muscle group, sets, repetitions, load, and notes.
- RF16 - The system must allow instructors and administrators to record exercise progress history.
- RF17 - The system must allow administrators to transfer active workout plans between active instructors.
- RF18 - The system must provide reports for active students, defaulters, most-used plans, revenue, daily access, and workout summary.
- RF19 - The system must provide a role-aware dashboard.
- RF20 - The system must enforce role-based access for administrators, receptionists, and instructors.
- RF21 - The system must provide a Team screen for administrators to create, edit, deactivate, reactivate, and filter staff users.
- RF22 - The system must create staff users with temporary passwords and require password change on first login.
- RF23 - The system must allow administrators to reset staff passwords without knowing the current password.
- RF24 - The system must prevent an administrator from deactivating or demoting their own account.
- RF25 - The system must prevent deactivation or demotion of the last active administrator.
- RF26 - The system must audit staff administration events.
- RF27 - The system must optionally seed default plans: Mensal, Trimestral, Semestral, and Anual.

## Role Requirements

- Admin:
  - lands on `/dashboard` after login;
  - manages staff, students, plans, enrollments, payments, access control, workouts, transfers, reports, and dashboard.
- Instructor:
  - lands on `/workouts` after login;
  - manages workout plans, exercises, and progress;
  - reads student context;
  - accesses workout reports only.
- Receptionist:
  - lands on `/students` after login;
  - manages students, enrollments, payments, and check-in/access control;
  - consults plans;
  - accesses management/financial reports.

## Non-Functional Requirements

- RNF01 - The backend must expose a documented REST API.
- RNF02 - Protected endpoints must require JWT bearer authentication.
- RNF03 - Authorization must be enforced on the backend, not only hidden in the frontend.
- RNF04 - The application must run locally through Docker Compose.
- RNF05 - The database schema must be managed through Alembic migrations.
- RNF06 - The backend must validate required fields and reject invalid CPF, email, date, price, and duration values.
- RNF07 - Passwords must be stored as hashes and never returned by API responses.
- RNF08 - API errors must return structured, sanitized responses.
- RNF09 - The frontend must provide loading, empty, and error states for operational screens.
- RNF10 - The application must include automated backend tests and frontend TypeScript build checks.
- RNF11 - The dashboard and reports must use backend report endpoints as the source of truth.
- RNF12 - The application must be usable on desktop and tablet-sized screens.
- RNF13 - Startup seeds must be idempotent.
- RNF14 - Staff administration must record audit events.
- RNF15 - Development credentials must be documented as non-production placeholders.
