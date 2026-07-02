# playwright-python-pytest

Production-ready UI test automation framework for [saucedemo.com](https://www.saucedemo.com) built with **Python**, **Playwright**, **pytest-bdd**, and **Allure** reporting.

---

## Technology Stack

| Component | Technology | Version |
|---|---|---|
| Language | Python | 3.13 |
| Browser automation | Playwright (sync_api) | 1.61.0 |
| Test runner | pytest | 9.0.2 |
| BDD layer | pytest-bdd (Gherkin) | 8.1.0 |
| Reporting | Allure | 2.16.0 |
| Database | PostgreSQL + SQLAlchemy | 2.0.51 |
| Parallel execution | pytest-xdist | 3.8.0 |
| Linter | ruff | 0.15.20 |
| Formatter | black | 26.5.1 |
| Type checker | mypy | 2.1.0 |

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.13+ | [python.org](https://python.org) |
| Java | 11+ | Required for Allure CLI report generation |
| Node.js | 18+ | Required for Allure CLI installation |
| Docker Desktop | Latest | Required for local PostgreSQL database |
| Git | Any | Version control |

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/kamlesh4821/playwright-python-pytest.git
cd playwright-python-pytest

# 2. Copy environment template and configure
cp .env.example .env
# Edit .env with your values

# 3. Install all dependencies
make install

# 4. Install Playwright browser binaries
make install-browsers

# 5. Start the local database
make db-up

# 6. (Optional) Install pre-commit hooks
make pre-commit-setup
```

---

## Quick Start

```bash
# Run smoke tests (fastest — under 5 minutes)
make test-smoke

# View the Allure report
make report
```

---

## Running Tests

```bash
# All tests
make test

# Smoke tests only
make test-smoke

# Full regression suite (parallel)
make test-regression

# Specific browser
make test-browser BROWSER=firefox

# Specific tags
pytest -m "smoke and auth" --alluredir=allure-results

# Specific environment
ENV=staging make test-smoke
```

---

## Key Commands

| Command | Description |
|---|---|
| `make install` | Install all Python dependencies |
| `make install-browsers` | Download Playwright browser binaries |
| `make db-up` | Start PostgreSQL via Docker |
| `make db-down` | Stop PostgreSQL |
| `make test` | Run all tests |
| `make test-smoke` | Run @smoke tagged scenarios |
| `make test-regression` | Run @regression suite (parallel) |
| `make report` | Generate and open Allure HTML report |
| `make lint` | Run ruff + black check |
| `make format` | Auto-format code with black + ruff |
| `make type-check` | Run mypy type checking |
| `make security` | Run bandit security scan |
| `make clean` | Remove all generated output |

---

## Test Tags

| Tag | Purpose | Run frequency |
|---|---|---|
| `@smoke` | Critical path — must pass on every commit | Every push |
| `@regression` | Full suite | Scheduled / manual |
| `@negative` | Error and edge case scenarios | Part of regression |
| `@e2e` | Full end-to-end purchase journey | Part of smoke |
| `@auth` | Authentication scenarios | Part of smoke |
| `@catalog` | Product catalog browsing | Part of regression |
| `@cart` | Cart management | Part of regression |
| `@checkout` | Checkout flow | Part of smoke |

---

## Live Report

Test results are published to GitHub Pages after every CI run:

**[https://kamlesh4821.github.io/playwright-python-pytest](https://kamlesh4821.github.io/playwright-python-pytest)**

---

## Project Structure

```
playwright-python-pytest/
├── features/          # Gherkin .feature files
├── pages/             # Page Object Model
├── steps/             # pytest-bdd step definitions
├── db/                # Database layer (SQLAlchemy + alembic)
├── config/            # YAML environment configs + ConfigLoader
├── utils/             # Logger, screenshot, network interceptor
├── exceptions/        # Custom exception hierarchy
├── testdata/          # YAML test data files
└── allure-config/     # Allure categories and executor config
```

For full architecture details, design decisions, and engineering guides:
**[TECHNICAL_GUIDE.md](TECHNICAL_GUIDE.md)**

For contribution guidelines:
**[CONTRIBUTING.md](CONTRIBUTING.md)**
