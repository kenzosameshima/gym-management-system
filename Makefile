COMPOSE=docker compose

.PHONY: up down logs backend frontend test lint format

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

backend:
	$(COMPOSE) up --build backend

frontend:
	$(COMPOSE) up --build frontend

test:
	$(COMPOSE) run --rm backend pytest

lint:
	$(COMPOSE) run --rm backend ruff check .
	$(COMPOSE) run --rm backend mypy app
	$(COMPOSE) run --rm frontend-dev sh -c "npm install && npm run lint"

format:
	$(COMPOSE) run --rm backend ruff check . --fix
	$(COMPOSE) run --rm backend black .
