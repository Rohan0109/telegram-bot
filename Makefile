.PHONY: install dev test lint format run migrate

install:
	python -m pip install -e .[dev]

dev:
	uvicorn app.main:app --reload --app-dir src

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir src

migrate:
	alembic upgrade head
