# Technical Guide — playwright-python-pytest Framework

This document is the complete engineering reference for the framework. It covers architecture, design decisions, fixture strategy, and step-by-step guides for every contribution pattern.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: TEST LAYER                                          │
│   Gherkin .feature files — business-readable test intent     │
│   pytest-bdd step definitions — Python implementation        │
├─────────────────────────────────────────────────────────────┤
│ LAYER 2: PAGE OBJECT LAYER                                   │
│   BasePage — all atomic Playwright actions                   │
│   BaseComponent — reusable UI elements (header, menu)        │
│   7 Page Objects — one per application screen               │
├─────────────────────────────────────────────────────────────┤
│ LAYER 3: DATABASE LAYER                                      │
│   DBClient — SQLAlchemy engine, session factory              │
│   Query modules — typed SQL helpers per domain               │
│   Setup helpers — test data insert utilities                 │
│   Health check — verify DB before suite starts               │
├─────────────────────────────────────────────────────────────┤
│ LAYER 4: BROWSER MANAGEMENT LAYER                            │
│   PlaywrightManager — via conftest.py session fixtures       │
│   Storage state — authenticated session reuse                │
│   Dual contexts — authenticated vs unauthenticated           │
├─────────────────────────────────────────────────────────────┤
│ LAYER 5: CONFIGURATION LAYER                                 │
│   ConfigLoader — typed access, zero os.getenv() in tests     │
│   Per-environment YAML — local, ci, staging, qa              │
│   Secrets — environment variables only, never committed       │
├─────────────────────────────────────────────────────────────┤
│ LAYER 6: UTILITY LAYER                                       │
│   Logger — structured JSON output                            │
│   ScreenshotUtil — auto-capture on failure                   │
│   NetworkInterceptor — Playwright route mocking              │
│   TestDataProvider — YAML + Faker integration                │
├─────────────────────────────────────────────────────────────┤
│ LAYER 7: REPORTING LAYER                                     │
│   allure-pytest — Gherkin step capture + @allure.step        │
│   categories.json — product defect vs test defect            │
│   executor.json — CI build traceability                      │
│   GitHub Pages — live hosted report URL                      │
├─────────────────────────────────────────────────────────────┤
│ LAYER 8: EXCEPTION LAYER                                     │
│   6 custom exception classes                                 │
│   Meaningful messages with context (test, browser, URL)      │
└─────────────────────────────────────────────────────────────┘
```

---

## Design Decisions

### 1. Playwright sync_api over asyncio

Playwright for Python supports both sync and async APIs. The sync API was chosen because:
- pytest fixtures are synchronous by default — mixing async fixtures with sync ones creates complexity
- Sync code is easier to read, debug, and trace through in CI logs
- There is no UI automation benefit to async — browser actions are inherently sequential

### 2. Fluent/Chainable Page Object Interface

Every Page Object implements two method levels:

**Atomic methods** — return `self`, enable chaining:
```python
def enter_username(self, username: str) -> "LoginPage":
    self.fill(self.USERNAME_INPUT, username)
    return self
```

**Workflow methods** — chain atomics, used in step definitions:
```python
def login_as(self, username: str, password: str) -> "LoginPage":
    return self.enter_username(username).enter_password(password).click_login()
```

Step definitions call workflow methods — one readable line per business action:
```python
@when("they login with valid credentials")
def login(login_page: LoginPage, config: ConfigLoader) -> None:
    login_page.login_as(config.get_test_username(), config.get_test_password())
```

### 3. Authenticated Storage State

Login happens once per xdist worker using Playwright's storage state:
```
Session start → login once → save {cookies, localStorage} to memory
Every test    → new BrowserContext(storage_state=saved_state) → instantly authenticated
Login tests   → new BrowserContext() with NO state → clean unauthenticated
```

Result: 60 scenarios → 1 UI login per worker. Without this, it would be 60 UI logins — unnecessary and slow.

### 4. Database Transaction Rollback

The `db_session` fixture wraps each test in a SQLAlchemy nested transaction (savepoint). Any INSERT/UPDATE done during the test is rolled back at test end — no explicit cleanup code needed anywhere.

**Important caveat:** if the application writes to the DB through the UI (server-side write triggered by browser action), that write is outside the SQLAlchemy session transaction and will NOT roll back automatically. Those cases require explicit API or direct SQL cleanup — documented in the step definition's docstring.

### 5. ConfigLoader as Single Seam

`os.getenv()` is never called outside `ConfigLoader`. This ensures:
- One place to change how config is loaded
- Type safety — `get_timeout() -> int` vs a raw string from `os.getenv()`
- Easy to mock in tests if needed in the future

---

## Fixture Scope Strategy

| Fixture | Scope | Reason |
|---|---|---|
| `playwright_instance` | session | One Playwright process per run |
| `browser` | session | One Browser per xdist worker, reused |
| `config` | session | Read config files once |
| `db_client` | session | One connection pool per session |
| `authenticated_storage_state` | session | Login once, reuse everywhere |
| `authenticated_context` | function | Fresh context per scenario (isolation) |
| `unauthenticated_context` | function | Clean context for auth tests only |
| `page` | function | Fresh Page per scenario |
| `db_session` | function | Transaction rolled back after test |
| All page object fixtures | function | Typed view of current page state |

---

## How to Add a New Page Object — Step by Step

**1. Create the file:**
```
pages/my_new_page.py
```

**2. Define locators as class-level constants:**
```python
class MyNewPage(BasePage):
    MAIN_BUTTON: str = "#main-btn"
    INPUT_FIELD: str = "[data-test='input']"
    SUCCESS_MSG: str = ".success-message"
```

**3. Implement atomic methods (return self):**
```python
@allure.step("Click main button")
def click_main_button(self) -> "MyNewPage":
    logger.debug("Clicking main button")
    self.click(self.MAIN_BUTTON)
    return self
```

**4. Implement workflow methods:**
```python
@allure.step("Submit form with value: {value}")
def submit_form(self, value: str) -> "MyNewPage":
    return self.fill(self.INPUT_FIELD, value).click_main_button()
```

**5. Add to pages/__init__.py:**
```python
from .my_new_page import MyNewPage
```

**6. Add fixture to root conftest.py:**
```python
@pytest.fixture
def my_new_page(page: Page) -> MyNewPage:
    return MyNewPage(page)
```

---

## How to Write a New BDD Feature — Step by Step

**1. Create the feature directory:**
```
features/my_area/
features/my_area/conftest.py      (even if empty)
features/my_area/my_feature.feature
```

**2. Write the feature file:**
```gherkin
@my_area
Feature: My Feature Name
  As an automation engineer
  I want to verify X behavior
  So that regressions are caught automatically

  @smoke @my_area
  Scenario: Happy path scenario name
    Given the user is logged in with valid credentials
    When they do some action
    Then the expected result should be visible
```

**3. Create step definitions:**
```
steps/my_area_steps.py
```

**4. Register new markers in pytest.ini:**
```ini
markers =
    my_area: description of the new area
```

---

## How to Add a DB Validation Step — Step by Step

**1. Add a query method to db/queries/:**
```python
@staticmethod
def get_record_by_id(session: Session, record_id: int) -> Optional[dict]:
    result = session.execute(
        text("SELECT * FROM my_table WHERE id = :id"),
        {"id": record_id},
    ).fetchone()
    return dict(result._mapping) if result else None
```

**2. Add a step definition to steps/db_steps.py:**
```python
@then(parsers.parse('a record should exist with id {record_id:d}'))
@allure.step("Then a record should exist with id {record_id}")
def record_exists(db_session: Session, record_id: int) -> None:
    result = MyQueries.get_record_by_id(db_session, record_id)
    assert result is not None, f"Record {record_id} not found in database"
```

**3. Add the step to your feature file:**
```gherkin
Then a record should exist with id 123
```

The `db_session` fixture is automatically available — no additional import needed in the step file.

---

## Configuration Guide

### Environment selection

Set `ENV` to load the matching YAML config:
```bash
ENV=local pytest      # loads config/local.yaml
ENV=ci pytest         # loads config/ci.yaml
ENV=staging pytest    # loads config/staging.yaml
ENV=qa pytest         # loads config/qa.yaml
```

### Adding a new config key

1. Add the key to each YAML file
2. Add a typed getter method to `ConfigLoader`:
```python
def get_my_new_setting(self) -> str:
    return str(self._config["my_new_setting"])
```
3. Access via `config.get_my_new_setting()` in fixtures or page objects

### Secrets

Never hardcode secrets. Use `${ENV_VAR}` placeholder in YAML:
```yaml
my_api_key: ${MY_API_KEY}
```
Set the env var in `.env` locally, GitHub Secrets in CI.

---

## Allure Reporting Guide

### Decorator reference

```python
@allure.title("Human-readable test title")
@allure.description("What this test verifies")
@allure.severity(allure.severity_level.BLOCKER)  # BLOCKER, CRITICAL, NORMAL, MINOR
@allure.tag("smoke", "auth")
@allure.step("Action description: {param}")
@allure.issue("JIRA-123", "Link to known bug")
```

### Report anatomy

- **Overview** — pass/fail summary, trend graph
- **Suites** — organized by feature file
- **Behaviors** — organized by Gherkin feature/scenario text
- **Timeline** — parallel execution visualization
- **Graphs** — severity, status, duration distribution

### Generating the report locally

```bash
make report
```

This copies `categories.json` to `allure-results/`, generates the report, and opens it in the browser.

---

## Parallel Execution Guide

Tests run in parallel via pytest-xdist:
```bash
pytest -n 4    # 4 parallel workers
```

**Why it's safe in this framework:**
- Each xdist worker gets its own `Playwright` + `Browser` instance (session-scoped fixtures are per-worker in xdist)
- Each test gets a fresh `BrowserContext` + `Page` (function-scoped)
- Each test gets a fresh `db_session` with its own transaction (rolled back after test)
- Storage state is read-only — workers load it but never write back to it

**Do not** share any of these objects across tests: Page, BrowserContext, db_session.

---

## CI/CD Pipeline Walkthrough

The pipeline in `.github/workflows/ci.yml` runs these steps:

1. **Checkout** — get the code
2. **Python setup** — install the declared Python version
3. **pip cache** — skip re-downloading packages when `requirements.txt` hasn't changed
4. **pip install** — install all runtime dependencies
5. **Browser binary cache** — skip re-downloading 300MB browsers on repeat runs
6. **playwright install** — install browsers + Linux system deps (`--with-deps`)
7. **Allure CLI** — install via npm (Node.js pre-installed on ubuntu-latest)
8. **Run tests** — headless, with selected tags, writing to `allure-results/`
9. **Allure report** — runs `if: always()` so you get a report even when tests fail
10. **GitHub Pages** — publish report to live URL
11. **Upload artifacts** — report zip + logs retained for 30 days
12. **Teams notification** — posts failure card to Teams channel (only on failure)

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ConfigException: ENV_VAR not set` | Missing `.env` entry | Add the key to `.env` |
| `DatabaseException: Cannot connect` | Docker not running | `make db-up` |
| `TimeoutError` on page load | Slow CI / wrong URL | Increase `navigation_timeout_ms` in ci.yaml |
| Allure report is empty | `--alluredir` not set | Check `pytest.ini` addopts |
| mypy errors on new file | Missing type hints | Add return type and parameter types |
| Screenshot not in report | `capture_on_failure` fixture missing | Ensure `conftest.py` autouse fixture is active |
| Flaky parallel tests | Shared state between workers | Check fixture scoping — nothing mutable at session scope should be shared |

---

## FAQ

**Q: Can I add a test without a Gherkin feature file?**
A: No. All tests in this framework use pytest-bdd and require `.feature` files. Plain pytest test functions are not used.

**Q: Where do I put test utility functions that don't fit page objects?**
A: In `utils/`. If they're test-data related, `TestDataProvider`. If they're assertion helpers, consider `pytest-check` built-in support.

**Q: How do I run a single scenario?**
A: `pytest features/auth/login.feature::test_login_as -v`

**Q: How do I add a new environment (e.g., prod-like)?**
A: Create `config/prod.yaml`, add the env var values, and run with `ENV=prod pytest`.

**Q: My pre-commit hook is blocking my commit. What do I do?**
A: Fix the reported issue — the hook is blocking for a real reason. Run `make lint` and `make type-check` first to see full output.

**Q: How do I temporarily disable a scenario without deleting it?**
A: Use `@pytest.mark.skip` in the step definition, or the Gherkin `@skip` tag if supported. Do not comment out feature file content.
