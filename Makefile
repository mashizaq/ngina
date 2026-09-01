# Makefile for ngina project

.PHONY: help install test lint build docker-build docker-up docker-down clean

help:
	@echo "ngina CI/CD Helper Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install all dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-python      - Run Python tests only"
	@echo "  make test-node        - Run Node.js tests only"
	@echo "  make test-integration - Run integration tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             - Lint all code"
	@echo "  make lint-python      - Lint Python code"
	@echo "  make lint-node        - Lint TypeScript code"
	@echo "  make format           - Format code (Python)"
	@echo "  make format-fix       - Fix code formatting and imports"
	@echo ""
	@echo "Building:"
	@echo "  make build            - Build all services"
	@echo "  make build-python     - Build Python service"
	@echo "  make build-node       - Build Node.js service"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-up        - Start Docker Compose services"
	@echo "  make docker-down      - Stop Docker Compose services"
	@echo "  make docker-logs      - View Docker Compose logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Clean build artifacts"
	@echo ""

install:
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 isort pylint
	cd src/backend && npm install

test: test-python test-node

test-python:
	pytest tests/ -v --cov=app --cov-report=html

test-node:
	cd src/backend && npm test

test-integration:
	pytest tests/integration/ -v

lint: lint-python lint-node

lint-python:
	flake8 app.py --count --show-source --statistics
	black --check app.py
	isort --check-only app.py

lint-node:
	cd src/backend && npm run lint

format:
	black app.py
	isort app.py

format-fix: format lint-node-fix

lint-node-fix:
	cd src/backend && npm run lint:fix

build: build-python build-node

build-python:
	# No build step for Flask app, just verify syntax
	python -m py_compile app.py

build-node:
	cd src/backend && npm run build

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
	@echo "Services started. Check logs with 'make docker-logs'"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell-python:
	docker-compose exec ngina-api /bin/bash

docker-shell-node:
	docker-compose exec node-publisher /bin/sh

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage dist build *.egg-info
	cd src/backend && rm -rf dist node_modules .jest_cache coverage 2>/dev/null || true

ci-check: lint test
	@echo "✅ All CI checks passed locally!"

.DEFAULT_GOAL := help
