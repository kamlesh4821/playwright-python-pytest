from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    """Page object for the saucedemo.com login screen."""

    USERNAME_INPUT: str = "#user-name"
    PASSWORD_INPUT: str = "#password"
    LOGIN_BUTTON: str = "#login-button"
    ERROR_CONTAINER: str = "[data-test='error']"
    ERROR_CLOSE_BUTTON: str = ".error-button"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Open login page")
    def open(self) -> "LoginPage":
        logger.debug("Opening login page")
        self.page.goto("https://www.saucedemo.com")
        self.wait_for_visible(self.USERNAME_INPUT)
        return self

    @allure.step("Enter username: {username}")
    def enter_username(self, username: str) -> "LoginPage":
        logger.debug(f"Entering username: {username}")
        self.fill(self.USERNAME_INPUT, username)
        return self

    @allure.step("Enter password")
    def enter_password(self, password: str) -> "LoginPage":
        logger.debug("Entering password")
        self.fill(self.PASSWORD_INPUT, password)
        return self

    @allure.step("Click Login button")
    def click_login(self) -> "LoginPage":
        logger.debug("Clicking login button")
        self.click(self.LOGIN_BUTTON)
        return self

    @allure.step("Login as: {username}")
    def login_as(self, username: str, password: str) -> "LoginPage":
        """Workflow method: complete login in one call."""
        return (
            self.enter_username(username)
                .enter_password(password)
                .click_login()
        )

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_CONTAINER)

    def is_error_visible(self) -> bool:
        return self.is_visible(self.ERROR_CONTAINER)

    @allure.step("Dismiss error message")
    def close_error(self) -> "LoginPage":
        self.click(self.ERROR_CLOSE_BUTTON)
        return self
