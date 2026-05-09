# Contributing

## Setup

1. Install Docker and Docker Compose.
2. Review `backend/.env.example`, `backend/.env.production.example`, `frontend/.env.example`, and `frontend/.env.production.example`.
3. Start the stack:

```bash
docker compose up --build
```

4. Open the frontend at http://localhost:3000 and the backend docs at http://localhost:8000/docs.

For Vite hot reload:

```bash
docker compose --profile dev up frontend-dev
```

## Branch Naming

Use short, scoped names:

- `feature/<short-description>`
- `fix/<short-description>`
- `docs/<short-description>`
- `release/<version>`

## Commit Messages

Use concise imperative messages with an optional scope:

- `fix: prevent duplicate paid payment processing`
- `docs: update v1.0.0 release notes`
- `backend: add enrollment validation test`

## Validation Before PR Or Commit

Run:

```bash
docker compose run --rm backend pytest
docker compose run --rm backend ruff check .
docker compose run --rm backend mypy app
docker compose run --rm frontend-dev npm run build
docker compose run --rm frontend-dev npm run lint
```

For release validation, also run:

```bash
docker compose up --build -d
docker compose ps
```

## Coding Standards

- Preserve the backend API/service/repository/database layering.
- Keep business rules in services, not routers.
- Keep database access in repositories.
- Keep Pydantic schemas explicit and typed.
- Preserve async patterns throughout backend code.
- Keep frontend API calls in `frontend/src/api` and shared domain types in `frontend/src/types`.
- Reuse existing page utilities and shared components before adding new abstractions.

## Documentation Expectations

- Update `README.md` for user-facing setup, routes, or operational behavior changes.
- Update `docs/architecture/overview.md` for architecture or domain-rule changes.
- Update `CHANGELOG.md` for release-relevant changes.
- Add release notes under `docs/releases/` for release preparation work.

## Security Notes

- Do not commit real `.env` files, credentials, JWTs, database dumps, or personal data.
- Production `SECRET_KEY` must be unique and at least 32 characters.
- Production CORS must use explicit origins.
- Never expose `password_hash` in API responses.
- Do not log passwords or bearer tokens.
- Do not run `npm audit fix --force` without planning the Vite major upgrade.

## Adding Migrations

Create migrations through the backend container:

```bash
docker compose run --rm backend alembic revision --autogenerate -m "describe change"
docker compose run --rm backend alembic upgrade head
```

Review generated migrations before committing. Ensure migration order is correct, constraints match service-layer rules, and downgrades are present when practical.

## Adding Frontend Pages Or Components

- Add routes in `frontend/src/routes/AppRoutes.tsx`.
- Protect pages with `ProtectedRoute` or `RoleRoute` as appropriate.
- Put page components in `frontend/src/pages`.
- Put shared reusable components in `frontend/src/components`.
- Add or update typed API functions in `frontend/src/api`.
- Ensure loading, empty, error, unauthorized, and no-data states render cleanly.
