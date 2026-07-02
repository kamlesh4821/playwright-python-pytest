# Changelog

All notable changes to this framework are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version follows [Semantic Versioning](https://semver.org/).

---

## [0.1.0] — 2026-07-02

### Added
- Initial framework scaffold — complete production-ready structure
- Playwright 1.61.0 (sync_api) browser automation
- pytest-bdd 8.1.0 Gherkin BDD layer with feature files for auth, catalog, cart, checkout, and E2E
- Allure reporting with categories.json failure classification and GitHub Pages deployment
- Page Object Model — BasePage, BaseComponent, 7 page objects (Login, Inventory, ProductDetail, Cart, CheckoutAddress, CheckoutOverview, OrderConfirmation)
- Component layer — HeaderComponent, MenuComponent
- Fluent/chainable Page Object interface — atomic methods return `self`
- Authenticated storage state — login once per session, reuse across all tests
- Database layer — PostgreSQL + SQLAlchemy 2.0.51 + alembic 1.18.5
- DB transaction rollback fixture — zero cleanup code per test
- Custom exception hierarchy — 6 exception classes
- Structured JSON logging via python-json-logger
- Screenshot-on-failure autouse fixture
- Network interceptor utility for Playwright route mocking
- Multi-level conftest.py — session and function-scoped fixtures
- Shared steps in steps/common/ — reusable across feature areas
- Multi-environment config — local.yaml, ci.yaml, staging.yaml, qa.yaml
- ConfigLoader — single typed access point, no os.getenv() in test code
- GitHub Actions CI pipeline with pip cache, browser binary cache, Allure report, GitHub Pages, Teams notification
- Makefile with standardised commands
- Docker Compose for local PostgreSQL
- Pre-commit hooks — ruff, black, mypy, bandit, detect-secrets
- Dependabot for automated dependency updates
- CODEOWNERS file for required review enforcement
- PR template with engineering checklist
