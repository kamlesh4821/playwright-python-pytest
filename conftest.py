"""Root conftest.py — all core session and function-scoped fixtures.

Fixture scope strategy (non-negotiable):
  session  → playwright_instance, browser, config, db_client, authenticated_storage_state
  function → authenticated_context, unauthenticated_context, page, db_session
  function → all page object fixtures (typed views of the current page)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Generator, Optional

import allure
import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)
from sqlalchemy.orm import Session

from config.config_loader import ConfigLoader
from db.db_client import DBClient
from pages.cart_page import CartPage
from pages.checkout_address_page import CheckoutAddressPage
from pages.checkout_overview_page import CheckoutOverviewPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from pages.order_confirmation_page import OrderConfirmationPage
from pages.product_detail_page import ProductDetailPage
from utils.logger import get_logger
from utils.screenshot_util import ScreenshotUtil

logger = get_logger(__name__)


# ── Configuration ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def config() -> ConfigLoader:
    """Session-scoped config loader — read config files once per run."""
    return ConfigLoader()


# ── Playwright browser lifecycle ───────────────────────────────────────────────

@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """One Playwright process per test session."""
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, config: ConfigLoader) -> Generator[Browser, None, None]:
    """One Browser per xdist worker, reused across tests."""
    browser_type = config.get_browser()
    launch_options = {
        "headless": config.is_headless(),
        "args": config.get_browser_args(),
    }
    logger.debug(f"Launching browser: {browser_type} headless={config.is_headless()}")
    match browser_type:
        case "firefox":
            b = playwright_instance.firefox.launch(**launch_options)
        case "webkit":
            b = playwright_instance.webkit.launch(**launch_options)
        case _:
            b = playwright_instance.chromium.launch(**launch_options)
    yield b
    b.close()


# ── Storage state — authenticated session reuse ────────────────────────────────

@pytest.fixture(scope="session")
def authenticated_storage_state(
    browser: Browser, config: ConfigLoader
) -> dict:
    """Login once per session. Save cookies + localStorage for reuse.

    All tests that need an authenticated state load this saved state
    instead of going through the login UI — eliminates redundant logins.
    """
    context = browser.new_context(
        base_url=config.get_base_url(),
        viewport={"width": 1280, "height": 720},
    )
    context.set_default_timeout(config.get_action_timeout())
    context.set_default_navigation_timeout(config.get_navigation_timeout())

    page = context.new_page()
    page.goto(config.get_base_url())
    page.fill("#user-name", config.get_test_username())
    page.fill("#password", config.get_test_password())
    page.click("#login-button")
    page.wait_for_url("**/inventory.html")

    state = context.storage_state()
    context.close()
    logger.debug("Authenticated storage state captured.")
    return state


# ── Browser contexts — fresh per scenario ─────────────────────────────────────

@pytest.fixture
def authenticated_context(
    browser: Browser, config: ConfigLoader, authenticated_storage_state: dict
) -> Generator[BrowserContext, None, None]:
    """Function-scoped authenticated context. Loads saved session state.

    Used by all tests that require a logged-in state (catalog, cart, checkout).
    """
    context = browser.new_context(
        storage_state=authenticated_storage_state,
        base_url=config.get_base_url(),
        viewport={"width": 1280, "height": 720},
        record_video_dir="reports/videos" if config.get_video_on_failure() else None,
    )
    context.set_default_timeout(config.get_action_timeout())
    context.set_default_navigation_timeout(config.get_navigation_timeout())
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context
    context.tracing.stop()
    context.close()


@pytest.fixture
def unauthenticated_context(
    browser: Browser, config: ConfigLoader
) -> Generator[BrowserContext, None, None]:
    """Function-scoped clean context — no auth state.

    Used exclusively by login and authentication tests.
    """
    context = browser.new_context(
        base_url=config.get_base_url(),
        viewport={"width": 1280, "height": 720},
    )
    context.set_default_timeout(config.get_action_timeout())
    context.set_default_navigation_timeout(config.get_navigation_timeout())
    yield context
    context.close()


# ── Page fixture ───────────────────────────────────────────────────────────────

@pytest.fixture
def page(authenticated_context: BrowserContext) -> Generator[Page, None, None]:
    """Default page fixture — uses authenticated context.

    Login-area tests override this by requesting unauthenticated_context explicitly.
    """
    p = authenticated_context.new_page()
    yield p
    p.close()


@pytest.fixture
def unauthenticated_page(
    unauthenticated_context: BrowserContext,
) -> Generator[Page, None, None]:
    """Page fixture without authentication — for login tests."""
    p = unauthenticated_context.new_page()
    yield p
    p.close()


# ── Screenshot on failure — autouse ───────────────────────────────────────────

@pytest.fixture(autouse=True)
def capture_on_failure(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """Automatically capture screenshot and attach to Allure on any test failure."""
    yield
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        page_fixture: Optional[Page] = request.node.funcargs.get("page") or \
                                        request.node.funcargs.get("unauthenticated_page")
        if page_fixture:
            ScreenshotUtil.capture_on_failure(page_fixture, request.node.name)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Generator:
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# ── Database fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def db_client(config: ConfigLoader) -> Generator[DBClient, None, None]:
    """Session-scoped DB client with connection pool.

    Skipped gracefully if DB config is not provided.
    """
    try:
        client = DBClient(config.get_db_url())
        yield client
        client.dispose()
    except Exception:
        yield None  # type: ignore[misc]


@pytest.fixture
def db_session(db_client: Optional[DBClient]) -> Generator[Optional[Session], None, None]:
    """Function-scoped DB session. Automatically rolled back after each test.

    Any INSERT/UPDATE inside a test is rolled back — no cleanup code needed.
    Note: Application-triggered DB writes (via UI) are outside this transaction.
    """
    if db_client is None:
        yield None
        return
    session = db_client.get_session()
    session.begin_nested()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ── Allure environment properties ──────────────────────────────────────────────

def pytest_configure(config: pytest.Config) -> None:
    """Write Allure environment.properties before the test run starts."""
    import playwright
    results_dir = Path("allure-results")
    results_dir.mkdir(exist_ok=True)
    env_props = results_dir / "environment.properties"
    env_vars = {
        "BASE_URL": os.getenv("BASE_URL", "https://www.saucedemo.com"),
        "BROWSER": os.getenv("BROWSER", "chromium"),
        "ENV": os.getenv("ENV", "local"),
        "PYTHON_VERSION": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
        "PLAYWRIGHT_VERSION": playwright.__version__,
    }
    with open(env_props, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")


# ── Page object fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def login_page(unauthenticated_page: Page) -> LoginPage:
    """LoginPage wrapping the unauthenticated page."""
    return LoginPage(unauthenticated_page)


@pytest.fixture
def inventory_page(page: Page) -> InventoryPage:
    """InventoryPage wrapping the authenticated page."""
    return InventoryPage(page)


@pytest.fixture
def product_detail_page(page: Page) -> ProductDetailPage:
    return ProductDetailPage(page)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture
def checkout_address_page(page: Page) -> CheckoutAddressPage:
    return CheckoutAddressPage(page)


@pytest.fixture
def checkout_overview_page(page: Page) -> CheckoutOverviewPage:
    return CheckoutOverviewPage(page)


@pytest.fixture
def order_confirmation_page(page: Page) -> OrderConfirmationPage:
    return OrderConfirmationPage(page)
