# Contributing to playwright-python-pytest

## Branch Naming

```
feature/short-description     # new feature or test scenario
fix/short-description         # bug fix
chore/short-description       # dependency update, config change
docs/short-description        # documentation only
```

## Commit Message Format (Conventional Commits via commitizen)

```
type(scope): short description

feat(cart): add remove item automation scenario
fix(login): correct error message locator
chore(deps): upgrade playwright to 1.62.0
docs(readme): update installation steps
```

Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`

## How to Add a New Page Object

1. Create `pages/new_page.py` extending `BasePage`
2. Define all locators as class-level string constants
3. Implement atomic methods returning `self` (fluent chaining)
4. Implement workflow methods that chain atomic methods
5. Add `@allure.step` to every user-action method
6. Add type hints to every method parameter and return value
7. Add `from pages.new_page import NewPage` to `pages/__init__.py`
8. Add a function-scoped fixture in root `conftest.py`

## How to Add a New BDD Feature

1. Create `features/<area>/<feature>.feature`
2. Create `features/<area>/conftest.py` (even if empty — for fixture scoping)
3. Create `steps/<area>_steps.py` with `@given`, `@when`, `@then` definitions
4. Register any new pytest markers in `pytest.ini` under `[markers]`
5. Follow the tag convention: `@smoke`, `@regression`, `@negative`, `@e2e`

## How to Add a DB Validation Step

1. Add a query method to the relevant class in `db/queries/`
2. Add a step definition to `steps/db_steps.py`
3. Write the Gherkin step in the feature file as a `Then` step
4. The `db_session` fixture is auto-available — no extra setup needed

## PR Checklist

Before opening a pull request:

- [ ] `make lint` passes — zero violations
- [ ] `make type-check` passes — zero mypy errors
- [ ] `make test-smoke` passes locally
- [ ] All locators are class-level constants
- [ ] All new methods have `@allure.step` and type hints
- [ ] All new fixtures have docstrings
- [ ] No `os.getenv()` outside `ConfigLoader`
- [ ] No hardcoded credentials, URLs, or timeouts
- [ ] No `time.sleep()` anywhere

## Code Review Expectations

- PR author merges after approval — not the reviewer
- At least one approval required (`CODEOWNERS` enforces this)
- Framework-core changes (`conftest.py`, `base_page.py`, `db_client.py`) require the framework lead's review
- Failing CI pipeline blocks merge — no exceptions
