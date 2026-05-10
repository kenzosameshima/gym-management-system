# Requirements

## Functional Requirements

- RF01 - The system must allow authenticated staff to register students with name, CPF, birth date, phone, email, address, and cadastral status.
- RF02 - The system must allow staff to edit, list, search, and deactivate students.
- RF03 - The system must display each student's derived financial status without storing delinquency as the cadastral status.
- RF04 - The system must allow staff to register, edit, list, and deactivate gym plans with name, price, duration, and status.
- RF05 - The system must allow staff to enroll active students in active plans with start date and calculated end date.
- RF06 - The system must create an initial pending payment when an enrollment is created.
- RF07 - The system must display payment status in enrollment listings.
- RF08 - The system must allow staff to register, list, update, and mark payments as paid or overdue.
- RF09 - The system must block duplicate processing of already paid payments.
- RF10 - The system must allow staff to check gym access by CPF.
- RF11 - The system must allow access only for active students with active, non-expired enrollments and no overdue payments.
- RF12 - The system must log every access attempt, including attempts for unknown CPF values.
- RF13 - The system must allow instructors to create workout plans for students.
- RF14 - The system must allow instructors to register exercises with name, muscle group, sets, repetitions, load, and notes.
- RF15 - The system must allow instructors to record exercise progress history.
- RF16 - The system must provide reports for active students, defaulters, most-used plans, revenue, daily access, and workout summary.
- RF17 - The system must provide a dashboard with active students, defaulters, expected revenue, access frequency, plan usage, and workout indicators.
- RF18 - The system must enforce role-based access for administrators, receptionists, and instructors.

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
