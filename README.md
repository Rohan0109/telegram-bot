# Telegram Bot API

A production-oriented FastAPI foundation for a Telegram bot platform. The HTTP API is intentionally small at the start, with boundaries ready for bot handlers, application services, repositories, and persistence to grow independently.

## Structure

```text
src/app/
  api/              HTTP routers and versioned endpoints
  core/             Settings and cross-cutting concerns
  domain/           Domain models and business rules
  repositories/     Persistence interfaces and implementations
  services/         Application use cases
  db.py             Async SQLAlchemy session factory
  main.py           FastAPI application factory and entry point
alembic/            Database migration configuration
 tests/             Automated tests
```

## Local setup

Requires Python 3.12+.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
Copy-Item .env.example .env
pytest
ruff check .
uvicorn app.main:app --reload --app-dir src
```

The API is available at `http://localhost:8000`. OpenAPI documentation is at `/docs`, and the health endpoint is `/api/v1/health`.

## Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

## Development principles

- Keep request handling in API routers and business behavior in services.
- Depend on repository abstractions from services so persistence can change without rewriting use cases.
- Add database changes through Alembic migrations.
- Keep configuration in environment variables and never commit `.env`.
