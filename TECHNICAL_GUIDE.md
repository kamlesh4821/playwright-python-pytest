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

## Design Patterns

The framework uses 16 design patterns across its 8 layers. Each pattern was chosen for a specific engineering reason — not for complexity.

---

### 1. Page Object Model (POM)

Each application screen has a dedicated Python class. Tests interact with the page through the class, never with raw Playwright locators directly.

**Location:** `pages/login_page.py`, `pages/inventory_page.py`, `pages/cart_page.py` (7 page classes total)

**Why used:** Locators and screen interactions live in one place. When the UI changes, only the Page Object changes — not every test that uses it. Eliminates duplication across the suite.

---

### 2. Fluent Interface / Method Chaining

Methods return `self` so multiple calls can be chained on a single line, reading like a natural sentence.

**Location:** All Page Object classes

```python
# pages/login_page.py
def enter_username(self, username: str) -> "LoginPage":
    self.fill(self.USERNAME_INPUT, username)
    return self   # ← returns self for chaining

def login_as(self, username: str, password: str) -> "LoginPage":
    return (
        self.enter_username(username)
            .enter_password(password)
            .click_login()
    )
```

**Why used:** Step definitions become one clean, readable line per business action instead of three separate calls. Matches the way humans describe behaviour naturally.

---

### 3. Template Method Pattern

A base class defines the structure of operations. Subclasses inherit and extend without rewriting the base logic.

**Location:** `pages/base_page.py` → all 7 page subclasses

```python
# BasePage defines ALL common actions once
class BasePage:
    def click(self, selector): ...
    def fill(self, selector, value): ...
    def expect_visible(self, selector): ...

# LoginPage inherits and adds screen-specific behaviour
class LoginPage(BasePage):
    def login_as(self, username, password): ...
```

**Why used:** Every Page Object gets 15+ Playwright actions for free. Adding a new utility method to `BasePage` makes it available to all 7 page objects instantly.

---

### 4. Composite Pattern

Complex objects are built by composing simpler ones. A page is composed of reusable components.

**Location:** `pages/inventory_page.py`, `pages/components/`

```python
class InventoryPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = HeaderComponent(page)   # ← composed
        self.menu   = MenuComponent(page)     # ← composed

# Used as:
inventory_page.header.get_cart_badge_count()
inventory_page.menu.click_logout()
```

**Why used:** The header (cart badge) and hamburger menu appear on multiple pages. Without components, their locators and methods would be duplicated in every Page Object that needs them.

---

### 5. Facade Pattern

A simplified interface hides complex underlying operations. The client sees only the simple version.

**Location:** All Page Object workflow methods

```python
# Step definition sees a simple, clean interface:
login_page.login_as("standard_user", "secret_sauce")

# Behind the Facade — fully hidden from the step:
# page.goto(base_url)
# page.locator("#user-name").fill("standard_user")
# page.locator("#password").fill("secret_sauce")
# page.locator("#login-button").click()
# page.wait_for_url("**/inventory.html")
```

**Why used:** Step definitions stay clean and business-readable. All Playwright complexity is hidden inside Page Objects. A new engineer reads a step and understands it without knowing Playwright.

---

### 6. Decorator Pattern

Behaviour is added to a function by wrapping it — without modifying the original code.

**Location:** Throughout `pages/`, `conftest.py`, `steps/`

```python
# Allure step reporting added via decorator:
@allure.step("Enter username: {username}")
def enter_username(self, username: str) -> "LoginPage":
    self.fill(self.USERNAME_INPUT, username)
    return self

# Fixture scope declared via decorator:
@pytest.fixture(scope="session")
def config() -> ConfigLoader:
    return ConfigLoader()

# Test categorisation via decorator:
@pytest.mark.smoke
@pytest.mark.auth
```

**Why used:** Reporting, fixture lifecycle, and test tagging are all added without changing core logic. The `@allure.step` decorator passes return values through transparently, so fluent chaining is completely unaffected.

---

### 7. Dependency Injection (DI)

Objects receive their dependencies from the outside rather than creating them themselves. In pytest this happens via fixture injection.

**Location:** `conftest.py` + all step definition files

```python
# Step receives page objects injected — never creates them:
@when("they login with valid credentials")
def login(login_page: LoginPage, config: ConfigLoader) -> None:
    login_page.login_as(config.get_test_username(), config.get_test_password())

# Fixture chain resolved automatically by pytest:
# config → authenticated_storage_state → authenticated_context → page → login_page
```

**Why used:** Tests never create or destroy browsers, DB connections, or config objects. They just declare what they need. This makes tests isolated, parallelisable, and easy to maintain.

---

### 8. Factory Method Pattern

A method (or fixture) whose sole job is to create and return an object, hiding creation logic from the caller.

**Location:** `conftest.py` — all page object and infrastructure fixtures

```python
@pytest.fixture
def login_page(unauthenticated_page: Page) -> LoginPage:
    return LoginPage(unauthenticated_page)    # ← factory

@pytest.fixture
def inventory_page(page: Page) -> InventoryPage:
    return InventoryPage(page)                # ← factory

@pytest.fixture(scope="session")
def db_client(config: ConfigLoader) -> DBClient:
    return DBClient(config.get_db_url())      # ← factory
```

**Why used:** Step definitions and tests never call constructors directly. The factory decides what to create and handles cleanup automatically after the test finishes.

---

### 9. Repository Pattern

Database access logic lives in dedicated repository classes. No raw SQL is written outside them.

**Location:** `db/queries/user_queries.py`, `db/queries/order_queries.py`

```python
# Step definition calls the repository — never writes SQL directly:
@then('an order should exist for "{username}"')
def order_exists(db_session: Session, username: str) -> None:
    assert OrderQueries.order_exists_for_user(db_session, username)

# SQL is centralised in the repository:
@staticmethod
def order_exists_for_user(session, username):
    result = session.execute(
        text("SELECT 1 FROM orders o JOIN users u ON o.user_id = u.id "
             "WHERE u.username = :username LIMIT 1"),
        {"username": username},
    ).fetchone()
    return result is not None
```

**Why used:** SQL queries are centralised and reusable. If the DB schema changes, only the query file changes — not every step definition that validates data.

---

### 10. Strategy Pattern

A behaviour is selected at runtime by configuration. The calling code does not change — only the strategy does.

**Location:** `conftest.py` — browser launch strategy

```python
match browser_type:
    case "firefox":
        b = playwright_instance.firefox.launch(**launch_options)
    case "webkit":
        b = playwright_instance.webkit.launch(**launch_options)
    case _:
        b = playwright_instance.chromium.launch(**launch_options)
```

```bash
# The caller just sets an environment variable — no code changes:
BROWSER=firefox pytest
BROWSER=webkit  pytest
```

**Why used:** The entire test suite switches browsers with a single environment variable. CI can run a matrix of three browsers using the same unchanged suite.

---

### 11. Context Manager Pattern

A resource is acquired at entry and guaranteed to be released at exit — even when an exception occurs — using Python's `with` statement.

**Location:** `utils/network_interceptor.py`, `db/db_client.py`

```python
# NetworkInterceptor — route is always cleaned up after the block
@contextmanager
def mock_response(self, url_pattern, status=500):
    self._page.route(url_pattern, handler)
    yield                             # ← test runs here
    self._page.unroute(url_pattern)   # ← always cleaned up

# Usage:
with interceptor.mock_response("/api/catalog", status=500):
    inventory_page.navigate()
    assert error_message.is_visible()
# route automatically removed — no manual cleanup
```

**Why used:** Network intercepts and DB sessions are guaranteed to clean up after themselves regardless of test outcome. No dangling routes or unclosed connections.

---

### 12. Observer Pattern

An observer watches for an event and reacts when it fires — without being explicitly called by the code that triggers the event.

**Location:** `conftest.py` — autouse screenshot fixture

```python
@pytest.fixture(autouse=True)
def capture_on_failure(request):
    yield
    # Observes every test outcome automatically — no call needed in tests
    if request.node.rep_call.failed:
        page = request.node.funcargs.get("page")
        if page:
            ScreenshotUtil.capture_on_failure(page, request.node.name)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
```

**Why used:** Every failing test automatically gets a screenshot in the Allure report — with zero code in the test itself. Engineers never call `take_screenshot()` anywhere. The observer handles it silently on every failure.

---

### 13. Adapter Pattern

Converts one interface into another that the client expects. Wraps an incompatible interface to make it compatible.

**Location:** `config/config_loader.py`

```python
# Raw YAML values are untyped strings:
# action_timeout_ms: "10000"
# headless: "false"

# ConfigLoader adapts them to typed Python:
def get_action_timeout(self) -> int:      # str → int
    return int(self._config.get("action_timeout_ms", 10000))

def is_headless(self) -> bool:            # str → bool, with env var override
    env_val = os.getenv("HEADLESS")
    if env_val:
        return env_val.lower() == "true"
    return bool(self._config.get("headless", True))
```

**Why used:** Page objects and fixtures call `config.is_headless()` and get a proper Python `bool`. They never deal with YAML parsing, string-to-bool conversion, or env var precedence. All that complexity is isolated in one class.

---

### 14. Null Object Pattern

Instead of returning `None` and forcing every caller to check for it, a harmless no-op is returned so the caller works identically regardless of whether the resource exists.

**Location:** `conftest.py` — `db_client` and `db_session` fixtures

```python
@pytest.fixture(scope="session")
def db_client(config):
    try:
        client = DBClient(config.get_db_url())
        yield client
    except Exception:
        yield None   # ← Null Object — safe, no crash

@pytest.fixture
def db_session(db_client):
    if db_client is None:
        yield None   # ← tests without DB run unaffected
        return
    session = db_client.get_session()
    ...
```

**Why used:** Running the UI suite locally without Docker/PostgreSQL does not crash every test. Only DB-specific step definitions would fail — which is the correct, honest behaviour.

---

### 15. Layered Architecture Pattern

The system is divided into distinct layers, each with a single responsibility. Each layer only talks to the layer directly below it — no layer skipping.

**Location:** Entire framework structure

```
Test Layer        → calls Step Definitions only
Step Definitions  → calls Page Objects and DB Queries only
Page Objects      → calls BasePage (Playwright) only
BasePage          → calls Playwright sync_api only
Config Layer      → read by all layers via ConfigLoader only
Utils Layer       → used by Page Objects and Fixtures
DB Layer          → called by Step Definitions only
Exception Layer   → raised by any layer, caught at the top
```

**Why used:** Changing one layer does not cascade through the entire codebase. Swapping the browser automation library (e.g., Playwright → Selenium) would touch only `BasePage` and `conftest.py` — feature files, step definitions, and DB code are completely untouched.

---

### 16. BDD Pattern (Behaviour Driven Development)

Tests are expressed in plain business language (Gherkin) that non-technical stakeholders can read and verify. Python step bindings connect Gherkin to executable code.

**Location:** `features/` (Gherkin) + `steps/` (Python bindings)

```gherkin
# features/auth/login.feature — readable by anyone
@smoke @auth
Scenario: Successful login with standard_user
  When they login as "standard_user" with password "secret_sauce"
  Then they should be on the inventory page
```

```python
# steps/auth_steps.py — Python binding
@when(parsers.parse('they login as "{username}" with password "{password}"'))
def login_as(login_page: LoginPage, username: str, password: str) -> None:
    login_page.login_as(username, password)
```

**Why used:** Feature files act as living documentation. A product manager, QA lead, or business analyst can read them and verify what is being tested — without knowing Python. Allure renders these Gherkin steps directly in the HTML report, giving stakeholders a readable audit trail of every test run.

---

### Pattern Summary

| # | Pattern | Primary Location | Purpose |
|---|---|---|---|
| 1 | Page Object Model | `pages/` | Screen-level abstraction |
| 2 | Fluent Interface | All page objects | Readable method chaining |
| 3 | Template Method | `BasePage` → subclasses | Shared action library |
| 4 | Composite | Pages + Components | Reusable UI elements |
| 5 | Facade | Page Object workflow methods | Simple interface over Playwright |
| 6 | Decorator | `@allure.step`, `@pytest.fixture` | Add behaviour without changing code |
| 7 | Dependency Injection | `conftest.py` fixtures | Decouple tests from object creation |
| 8 | Factory Method | `conftest.py` fixture factories | Controlled, automatic object creation |
| 9 | Repository | `db/queries/` | Centralise all SQL access |
| 10 | Strategy | Browser selection in `conftest.py` | Runtime behaviour switching |
| 11 | Context Manager | `NetworkInterceptor`, DB sessions | Guaranteed resource cleanup |
| 12 | Observer | Autouse screenshot fixture | React to test events silently |
| 13 | Adapter | `ConfigLoader` | Convert YAML + env vars to typed Python |
| 14 | Null Object | `db_client` / `db_session` fixtures | Safe no-op when resource unavailable |
| 15 | Layered Architecture | Entire framework | Separation of concerns across 8 layers |
| 16 | BDD | `features/` + `steps/` | Business-readable test intent |

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
