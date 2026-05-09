# Changelog

All notable changes to this project are documented here.

The format follows Keep a Changelog conventions, and versions use semantic versioning style.

## [v1.0.0] - Unreleased

### Added
- Stable MVP release candidate documentation, including contributor guidance, agent guidance, and v1.0.0 release notes.
- Full-stack operational coverage for authentication, students, plans, enrollments, payments, access control, workouts, reports, and dashboard workflows.

### Changed
- Aligned backend OpenAPI metadata and frontend/backend package metadata with the upcoming `1.0.0` release.
- Updated Docker Compose backend startup to run Uvicorn without development reload by default.
- Refreshed README and architecture documentation for release-candidate accuracy.

### Security
- Documented production secret, CORS, token-storage, npm audit, and sensitive-data handling notes for the MVP.

## [v0.9.0-rc1] - 2026-05-08

### Added
- Release-candidate hardening for validation, authentication edge cases, duplicate payment processing, and workout progress integrity.
- Production environment examples and Docker production install support.

### Changed
- Improved API error handling, request logging, frontend lazy loading, and session cleanup behavior.
- Tightened production CORS and secret validation.

## [v0.8.0-beta] - 2026-05-08

### Added
- Operational dashboard cards and charts.
- Frontend filtering, sortable tables, pagination controls, and notifications.
- Access-control session history and improved workout workflow usability.

### Changed
- Improved responsive frontend layout and route-level frontend usability.
- Added minimal backend filters needed by operational screens.

## [v0.7.0-beta] - 2026-05-08

### Added
- React Router frontend integration.
- JWT login, protected routes, role-aware navigation, and typed API modules.
- Core frontend pages for students, plans, enrollments, payments, access control, workouts, and reports.

## [v0.6.0-alpha] - 2026-05-08

### Added
- Reporting and analytics layer.
- Active students, defaulters, plan usage, revenue, daily access, and workout summary reports.
- Reporting-specific schemas, tests, authorization, and indexes.

## [v0.5.0-alpha] - 2026-05-08

### Added
- Workout plans, exercises, and exercise progress.
- Instructor workflow permissions and workout-domain tests.

## [v0.4.0-alpha] - 2026-05-08

### Added
- Enrollments, payments, and access-control checks.
- Payment delinquency handling and access logs.

## [v0.3.0-alpha] - 2026-05-08

### Added
- Student and plan CRUD APIs.
- Soft-delete behavior and role-aware access.

## [v0.2.0-alpha] - 2026-05-08

### Added
- JWT authentication, user registration, login, and role foundations.
- Password hashing and authenticated current-user endpoint.

## [v0.1.0-alpha] - 2026-05-08

### Added
- Initial FastAPI, PostgreSQL, SQLAlchemy async, Alembic, React/Vite, and Docker Compose foundation.
- Health checks, structured logging, and baseline quality tooling.
