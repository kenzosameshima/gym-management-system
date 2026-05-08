# Architecture Overview

The project starts with a layered backend and a minimal React frontend.

Backend flow:

```text
API Layer
↓
Service Layer
↓
Repository Layer
↓
Database Layer
```

Current Phase 1 responsibilities:

- API layer exposes health endpoints only.
- Service layer owns readiness orchestration and error mapping.
- Repository layer owns database connectivity checks.
- Database layer owns async SQLAlchemy engine and session factory.
- Core modules own configuration, logging, middleware, and exception handling.

No gym domain models, migrations, authentication flows, CRUDs, or dashboards are included in this phase.

