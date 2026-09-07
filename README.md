# Telegram Bot API

A production-oriented FastAPI foundation for a Telegram bot and research-paper ingestion platform.

The project currently provides a typed arXiv metadata ingestion slice behind an asynchronous FastAPI API. It fetches paper metadata from arXiv and exposes it for inspection through Swagger. PostgreSQL persistence and scheduled daily ingestion are the next pipeline stages.

## Current Pipeline

```mermaid
flowchart LR
    A[arXiv API] --> B[ArxivClient]
    B --> C[Ingestion Preview API]
    C --> D[FastAPI /docs]
    C -. next .-> E[PostgreSQL]
    E -. next .-> F[Daily Scheduler]
```

### Available endpoint

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Check API availability |
| `GET` | `/api/v1/ingestion/preview` | Fetch arXiv paper metadata without storing it |

Example request:

```text
http://localhost:8000/api/v1/ingestion/preview?query=cat:cs.AI&max_results=5
```

The preview response includes:

- Stable arXiv ID
- Title and abstract
- Authors
- Published and updated timestamps
- PDF URL

## Quick Start

Requires Python 3.12 or newer.

### 1. Create the environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 2. Start the API

```powershell
uvicorn app.main:app --reload --app-dir src
```

Open the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/api/v1/health`

### 3. Try arXiv ingestion

From Swagger, open `GET /api/v1/ingestion/preview`, enter:

```text
query: cat:cs.AI
max_results: 5
```

Or call it directly:

```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/ingestion/preview?query=cat:cs.AI&max_results=5"
```

## Docker

The compose setup starts the API and PostgreSQL services:

```powershell
docker compose up --build
```

The API is available at `http://localhost:8000`.

## Configuration

Configuration is read from environment variables or an optional `.env` file.

| Variable | Default | Description |
| --- | --- | --- |
| `APP_NAME` | `Telegram Bot API` | FastAPI application name |
| `APP_ENV` | `development` | Runtime environment name |
| `DEBUG` | `false` | Enable FastAPI debug mode |
| `API_V1_PREFIX` | `/api/v1` | Versioned API prefix |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/telegram_bot` | Async SQLAlchemy database URL |

## Project Layout

```text
src/app/
  api/              FastAPI routers and versioned endpoints
  core/             Settings and logging
  domain/           Typed domain models and ports
  infrastructure/   External integrations, including arXiv
  repositories/     Persistence abstractions
  services/         Application use cases
  db.py             Async SQLAlchemy session factory
  main.py           FastAPI application factory
alembic/            Database migration configuration
tests/              Automated tests
```

## Development Checks

Run the focused checks before submitting changes:

```powershell
python -m pytest
ruff check .
```

## Roadmap

- [x] FastAPI foundation and health endpoint
- [x] arXiv Atom feed client
- [x] Typed ingestion service with update and skip behavior
- [x] Read-only FastAPI preview endpoint
- [ ] PostgreSQL paper repository and Alembic migration
- [ ] Daily scheduled ingestion job
- [ ] PDF download and document processing
- [ ] Search and retrieval for Telegram users

## Design Principles

- Keep HTTP handling in routers and business behavior in services.
- Depend on domain ports so external sources and persistence can change independently.
- Use asynchronous FastAPI, HTTPX, and SQLAlchemy APIs.
- Add database changes through Alembic migrations.
- Keep secrets and environment-specific settings out of source control.

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
