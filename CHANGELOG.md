# Changelog

All notable changes to this project are documented here.

The format follows Keep a Changelog conventions, and versions use semantic versioning style.

## [0.8.0-beta] - 2026-05-08

### Added
- Operational dashboard cards and charts.
- Frontend filtering, sortable tables, pagination controls, and notifications.
- Access-control session history and improved workout workflow usability.

### Changed
- Improved responsive frontend layout and route-level frontend usability.
- Added minimal backend filters needed by operational screens.

## [0.7.0-beta] - 2026-05-08

### Added
- React Router frontend integration.
- JWT login, protected routes, role-aware navigation, and typed API modules.
- Core frontend pages for students, plans, enrollments, payments, access control, workouts, and reports.

## [0.6.0-alpha] - 2026-05-08

### Added
- Reporting and analytics layer.
- Active students, defaulters, plan usage, revenue, daily access, and workout summary reports.
- Reporting-specific schemas, tests, authorization, and indexes.

## [0.5.0-alpha] - 2026-05-08

### Added
- Workout plans, exercises, and exercise progress.
- Instructor workflow permissions and workout-domain tests.

## [0.4.0-alpha] - 2026-05-08

### Added
- Enrollments, payments, and access-control checks.
- Payment delinquency handling and access logs.

## [0.3.0-alpha] - 2026-05-08

### Added
- Student and plan CRUD APIs.
- Soft-delete behavior and role-aware access.

## [0.2.0-alpha] - 2026-05-08

### Added
- JWT authentication, user registration, login, and role foundations.
- Password hashing and authenticated current-user endpoint.

## [0.1.0-alpha] - 2026-05-08

### Added
- Initial FastAPI, PostgreSQL, SQLAlchemy async, Alembic, React/Vite, and Docker Compose foundation.
- Health checks, structured logging, and baseline quality tooling.
