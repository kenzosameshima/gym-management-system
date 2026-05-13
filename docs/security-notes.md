# Security Notes

## Authentication And Accounts

- Public registration is disabled: `POST /api/auth/register` returns `410 PUBLIC_REGISTRATION_DISABLED`.
- The first administrator is seeded on startup when no active admin exists and `INITIAL_ADMIN_*` is configured.
- Local Docker defaults:
  - Admin email: `admin@example.com`
  - Admin password: `strong-password`
- Staff users are created by an administrator through `/api/users` or the **Equipe** screen.
- Users created by admin receive a temporary password and are marked with `must_change_password=true`.
- On first login, users with a temporary password are redirected to `/change-password` and blocked from role-protected endpoints until they change the password.
- Password hashes are stored server-side and are never returned by API responses.
- `last_login_at` is recorded after successful login.

## Authorization

Backend role checks are the source of truth. Frontend navigation only hides unavailable areas for usability.

- `ADMIN`: management, operations, team administration, plans, workouts, reports.
- `RECEPTIONIST`: students, enrollments, payments, check-in/access control, plan consultation, management reports.
- `INSTRUCTOR`: workout plans, exercises, progress tracking, read-only student context, workout reports.

Implemented protections:

- Admin cannot deactivate or demote their own account.
- The last active admin cannot be deactivated or demoted.
- Instructors with active workout plans cannot be deactivated or demoted until active plans are transferred.
- Receptionists and instructors cannot manage staff users.
- Instructors cannot access plan management or operational financial endpoints.
- Receptionists cannot access workout-domain endpoints.

## Password Reset

Administrators can reset a staff user's password by defining a new temporary password.

This operation:

- does not require knowing the user's current password;
- sets `must_change_password=true`;
- requires the user to change the password on next login;
- records a `PASSWORD_RESET` event in user audit logs.

## Auditing

Staff administration events are persisted in `user_audit_logs`.

Current audited events:

- `USER_CREATED`
- `USER_UPDATED`
- `USER_DEACTIVATED`
- `PASSWORD_RESET`
- `PASSWORD_CHANGED`

The **Equipe** screen displays recent audit events. The backend endpoint is admin-only:

```text
GET /api/users/audit
```

## Tokens And Frontend Storage

- The backend uses JWT bearer tokens.
- The frontend stores the access token in `localStorage` under `gym_management_access_token`.
- There is no refresh-token flow in this MVP; expired sessions require login again.
- For production, consider an HttpOnly cookie or refresh-token session design.

## Production Configuration

Do not deploy with development values.

Required production hardening:

- replace `SECRET_KEY`;
- replace database credentials;
- configure explicit CORS origins;
- set `APP_ENV=production`;
- set `DEBUG=false`;
- do not use the demo admin password;
- use a unique temporary password for first deployment;
- rotate any exposed credentials immediately.

The settings layer rejects wildcard CORS origins in production.

## Frontend npm audit

`npm audit` reports two moderate vulnerabilities:

- Package: `esbuild <=0.24.2`
- Path: transitive dependency through `vite <=6.4.1`
- Advisory: `GHSA-67mh-4wv8-2f99`
- Proposed npm fix: `npm audit fix --force`
- Impact of proposed fix: installs Vite 8, a breaking major upgrade

This affects Vite development server behavior. The production frontend image builds static assets and serves them through Nginx, so this is not part of the runtime production container surface.

`npm audit fix` was executed without `--force` and did not resolve the issue. Do not run `--force` automatically; handle the Vite major upgrade as a planned tooling task.
