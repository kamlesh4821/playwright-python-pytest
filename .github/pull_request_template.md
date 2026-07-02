## Summary
<!-- What does this PR do? One paragraph. -->

## Type of change
- [ ] New test scenario(s)
- [ ] New page object / component
- [ ] Framework enhancement
- [ ] Bug fix
- [ ] Documentation update
- [ ] Dependency update

## Checklist — do not merge without completing
- [ ] `make lint` passes with zero violations
- [ ] `make type-check` passes with zero errors
- [ ] `make test-smoke` passes locally
- [ ] All locators defined as class-level constants (no inline selectors)
- [ ] All new Page Object methods have `@allure.step` and type hints
- [ ] All new fixtures have docstrings with scope and purpose
- [ ] No `os.getenv()` calls outside `ConfigLoader`
- [ ] No hardcoded URLs, credentials, or timeouts
- [ ] No `time.sleep()` in any test or page object code
- [ ] `requirements.txt` updated if new packages added (with exact pinned version)
- [ ] Feature file or test file added/updated to cover the change

## Screenshots / evidence (if UI change)
<!-- Paste screenshot or Allure step evidence -->

## Notes for reviewer
<!-- Anything the reviewer should pay special attention to -->
