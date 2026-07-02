from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class CheckoutAddressPage(BasePage):
    """Page object for checkout step one — personal information form."""

    FIRST_NAME_INPUT: str = "[data-test='firstName']"
    LAST_NAME_INPUT: str = "[data-test='lastName']"
    POSTAL_CODE_INPUT: str = "[data-test='postalCode']"
    CONTINUE_BUTTON: str = "[data-test='continue']"
    CANCEL_BUTTON: str = "[data-test='cancel']"
    ERROR_CONTAINER: str = "[data-test='error']"
    ERROR_CLOSE_BUTTON: str = ".error-button"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Enter first name: {first_name}")
    def enter_first_name(self, first_name: str) -> "CheckoutAddressPage":
        self.fill(self.FIRST_NAME_INPUT, first_name)
        return self

    @allure.step("Enter last name: {last_name}")
    def enter_last_name(self, last_name: str) -> "CheckoutAddressPage":
        self.fill(self.LAST_NAME_INPUT, last_name)
        return self

    @allure.step("Enter postal code: {postal_code}")
    def enter_postal_code(self, postal_code: str) -> "CheckoutAddressPage":
        self.fill(self.POSTAL_CODE_INPUT, postal_code)
        return self

    @allure.step("Fill checkout info: {first_name} {last_name}")
    def fill_info(
        self, first_name: str, last_name: str, postal_code: str
    ) -> "CheckoutAddressPage":
        """Workflow method: fill all fields in one call."""
        return (
            self.enter_first_name(first_name)
                .enter_last_name(last_name)
                .enter_postal_code(postal_code)
        )

    @allure.step("Click Continue")
    def click_continue(self) -> "CheckoutAddressPage":
        self.click(self.CONTINUE_BUTTON)
        return self

    @allure.step("Click Cancel")
    def click_cancel(self) -> "CheckoutAddressPage":
        self.click(self.CANCEL_BUTTON)
        return self

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_CONTAINER)

    def is_error_visible(self) -> bool:
        return self.is_visible(self.ERROR_CONTAINER)

    @allure.step("Close error message")
    def close_error(self) -> "CheckoutAddressPage":
        self.click(self.ERROR_CLOSE_BUTTON)
        return self
