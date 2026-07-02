.PHONY: install install-browsers install-browsers-ci pre-commit-setup \
        db-up db-down test test-smoke test-regression test-browser \
        report lint format type-check security clean

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

install-browsers:
	playwright install chromium firefox webkit

install-browsers-ci:
	playwright install --with-deps chromium

pre-commit-setup:
	pre-commit install
	detect-secrets scan > .secrets.baseline

db-up:
	docker-compose up -d postgres
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 3
	alembic upgrade head

db-down:
	docker-compose down

test:
	pytest --alluredir=allure-results

test-smoke:
	pytest -m smoke --alluredir=allure-results

test-regression:
	pytest -m regression --alluredir=allure-results -n $(PARALLEL_WORKERS)

BROWSER ?= chromium
test-browser:
	BROWSER=$(BROWSER) pytest -m smoke --alluredir=allure-results

PARALLEL_WORKERS ?= 4

report:
	@cp allure-config/categories.json allure-results/ 2>/dev/null || true
	allure generate allure-results --clean -o allure-report
	allure open allure-report

lint:
	ruff check .
	black --check .

format:
	black .
	ruff check --fix .

type-check:
	mypy pages/ db/ utils/ config/ exceptions/ --ignore-missing-imports

security:
	bandit -r pages/ db/ utils/ config/ exceptions/ steps/ -x db/migrations/

clean:
	rm -rf allure-results/ allure-report/ .pytest_cache/ htmlcov/ coverage.xml
	rm -rf reports/screenshots/* reports/videos/* reports/traces/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
