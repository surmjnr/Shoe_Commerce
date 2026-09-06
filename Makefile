.PHONY: help up down build migrate createsuperuser test lint format

help:
	@echo "Shoe Store - Available commands:"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make build           - Build Docker images"
	@echo "  make migrate         - Run Django migrations"
	@echo "  make createsuperuser - Create admin user"
	@echo "  make test            - Run all tests"
	@echo "  make lint            - Run linters"
	@echo "  make format          - Format code"

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

migrate:
	docker compose exec backend python manage.py migrate

createsuperuser:
	docker compose exec backend python manage.py createsuperuser

test:
	docker compose exec backend pytest
	cd frontend && npm test -- --run

lint:
	docker compose exec backend ruff check .
	cd frontend && npm run lint

format:
	docker compose exec backend black . && docker compose exec backend isort .
	cd frontend && npm run format
