from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_component import BaseComponent
from utils.logger import get_logger

logger = get_logger(__name__)


class HeaderComponent(BaseComponent):
    """Represents the top navigation header present on all authenticated pages."""

    CART_ICON: str = ".shopping_cart_link"
    CART_BADGE: str = ".shopping_cart_badge"
    BURGER_MENU: str = "#react-burger-menu-btn"
    APP_LOGO: str = ".app_logo"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Get cart badge count")
    def get_cart_badge_count(self) -> int:
        if self.is_hidden(self.CART_BADGE):
            return 0
        return int(self.get_text(self.CART_BADGE))

    def is_cart_badge_visible(self) -> bool:
        return self.is_visible(self.CART_BADGE)

    @allure.step("Navigate to cart")
    def go_to_cart(self) -> "HeaderComponent":
        logger.debug("Clicking cart icon")
        self.click(self.CART_ICON)
        return self

    @allure.step("Open hamburger menu")
    def open_menu(self) -> "HeaderComponent":
        logger.debug("Opening hamburger menu")
        self.click(self.BURGER_MENU)
        return self
