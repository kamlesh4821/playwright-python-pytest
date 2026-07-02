from __future__ import annotations

from typing import Optional

import allure
from playwright.sync_api import Locator, Page, expect

from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    """Base class for all page objects.

    Provides atomic Playwright actions with Allure step reporting.
    All methods return self (or a typed subclass) to enable fluent chaining.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    @allure.step("Navigate to: {url}")
    def navigate(self, url: str) -> "BasePage":
        logger.debug(f"Navigating to: {url}")
        self.page.goto(url)
        return self

    @allure.step("Click: {selector}")
    def click(self, selector: str) -> "BasePage":
        logger.debug(f"Clicking: {selector}")
        self.page.locator(selector).click()
        return self

    @allure.step("Fill field: {selector}")
    def fill(self, selector: str, value: str) -> "BasePage":
        logger.debug(f"Filling {selector}")
        self.page.locator(selector).fill(value)
        return self

    @allure.step("Clear and fill: {selector}")
    def clear_and_fill(self, selector: str, value: str) -> "BasePage":
        self.page.locator(selector).clear()
        self.page.locator(selector).fill(value)
        return self

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def get_all_texts(self, selector: str) -> list[str]:
        return self.page.locator(selector).all_inner_texts()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def is_hidden(self, selector: str) -> bool:
        return self.page.locator(selector).is_hidden()

    def is_enabled(self, selector: str) -> bool:
        return self.page.locator(selector).is_enabled()

    def count(self, selector: str) -> int:
        return self.page.locator(selector).count()

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        return self.page.locator(selector).get_attribute(attribute)

    def wait_for_url(self, url_pattern: str) -> "BasePage":
        self.page.wait_for_url(url_pattern)
        return self

    def wait_for_visible(self, selector: str, timeout: Optional[int] = None) -> Locator:
        locator = self.page.locator(selector)
        kwargs = {"state": "visible"}
        if timeout:
            kwargs["timeout"] = timeout  # type: ignore[assignment]
        locator.wait_for(**kwargs)
        return locator

    def get_current_url(self) -> str:
        return self.page.url

    def get_title(self) -> str:
        return self.page.title()

    def take_screenshot(self, name: Optional[str] = None) -> bytes:
        return self.page.screenshot(path=name, full_page=True)

    def expect_visible(self, selector: str) -> None:
        expect(self.page.locator(selector)).to_be_visible()

    def expect_hidden(self, selector: str) -> None:
        expect(self.page.locator(selector)).to_be_hidden()

    def expect_text(self, selector: str, text: str) -> None:
        expect(self.page.locator(selector)).to_contain_text(text)

    def expect_url(self, pattern: str) -> None:
        expect(self.page).to_have_url(pattern)
