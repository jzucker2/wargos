.PHONY: help build run run-gunicorn test ci-test ci-lint format-lint check clean docker-build docker-run docker-stop docker-logs

# Python trees used by format, lint, and CI (single source of truth for paths)
PY_SRCS := app/ tests/

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker image
	docker build -t wargos .

run: ## Run the application locally with Gunicorn
	./scripts/run_gunicorn.sh

run-uvicorn: ## Run the application locally with Uvicorn (development)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-gunicorn: ## Run the application with Gunicorn (production-like)
	./scripts/run_gunicorn.sh

test: ## Run all tests (same command as the GitHub Actions test workflow)
	pytest tests/ -v

ci-test: test ## Alias for CI/docs — identical to `make test`

test-coverage: ## Run tests with coverage report
	pytest tests/ --cov=app --cov-report=term-missing

test-file: ## Run specific test file (FILE=path/to/test.py)
	@if [ -z "$(FILE)" ]; then \
		echo "Error: FILE parameter is required. Usage: make test-file FILE=tests/test_basic.py"; \
		exit 1; \
	fi
	pytest $(FILE) -v

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov

docker-build: ## Build Docker image
	docker build -t wargos .

docker-run: ## Run with Docker Compose
	docker compose up -d

docker-stop: ## Stop Docker Compose services
	docker compose down

docker-logs: ## Show Docker Compose logs
	docker compose logs -f

docker-clean: ## Clean up Docker resources
	docker compose down -v
	docker system prune -f

install: ## Install Python dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt

test-docker: ## Run tests in Docker container
	docker build -t wargos .
	docker run --rm wargos pytest

format: ## Apply Black formatting (modifies files)
	black $(PY_SRCS) --line-length=79

lint: ## Run Flake8 only (no Black)
	flake8 $(PY_SRCS)

# Definitive lint gate for CI and pre-commit: no file writes, must match remote tree
ci-lint: ## Black --check + Flake8 (same as GitHub Actions lint job and pre-commit)
	black --check $(PY_SRCS) --line-length=79
	flake8 $(PY_SRCS)

check: ci-lint ## Same as ci-lint (verify formatting + lint)

format-lint: format ci-lint ## Format with Black, then run the definitive lint gate

lint-fix: ## Auto-fix linting issues where possible
	black $(PY_SRCS) --line-length=79
	autopep8 --in-place --recursive --aggressive --aggressive $(PY_SRCS)

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit hooks on all files
	pre-commit run --all-files

ci-check: pre-commit-run ci-test ## Pre-commit (incl. ci-lint) + unit tests (matches automation intent)
