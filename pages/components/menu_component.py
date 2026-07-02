from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_component import BaseComponent
from utils.logger import get_logger

logger = get_logger(__name__)


class MenuComponent(BaseComponent):
    """Represents the hamburger side menu on saucedemo.com."""

    ALL_ITEMS_LINK: str = "#inventory_sidebar_link"
    ABOUT_LINK: str = "#about_sidebar_link"
    LOGOUT_LINK: str = "#logout_sidebar_link"
    RESET_LINK: str = "#reset_sidebar_link"
    CLOSE_BUTTON: str = "#react-burger-cross-btn"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Click Logout")
    def click_logout(self) -> "MenuComponent":
        logger.debug("Clicking logout")
        self.click(self.LOGOUT_LINK)
        return self

    @allure.step("Click Reset App State")
    def click_reset_app_state(self) -> "MenuComponent":
        logger.debug("Clicking reset app state")
        self.click(self.RESET_LINK)
        return self

    @allure.step("Click All Items")
    def click_all_items(self) -> "MenuComponent":
        self.click(self.ALL_ITEMS_LINK)
        return self

    @allure.step("Close menu")
    def close(self) -> "MenuComponent":
        self.click(self.CLOSE_BUTTON)
        return self

    def is_menu_open(self) -> bool:
        return self.is_visible(self.LOGOUT_LINK)
