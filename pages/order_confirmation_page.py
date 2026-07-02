from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.components.header_component import HeaderComponent
from utils.logger import get_logger

logger = get_logger(__name__)


class OrderConfirmationPage(BasePage):
    """Page object for the saucedemo.com order confirmation screen."""

    HEADER_TEXT: str = ".complete-header"
    CONFIRMATION_MESSAGE: str = ".complete-text"
    PONY_EXPRESS_IMAGE: str = ".pony_express"
    BACK_HOME_BUTTON: str = "[data-test='back-to-products']"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = HeaderComponent(page)

    @allure.step("Get confirmation header text")
    def get_header_text(self) -> str:
        return self.get_text(self.HEADER_TEXT)

    @allure.step("Get confirmation message")
    def get_confirmation_message(self) -> str:
        return self.get_text(self.CONFIRMATION_MESSAGE)

    def is_pony_express_image_visible(self) -> bool:
        return self.is_visible(self.PONY_EXPRESS_IMAGE)

    @allure.step("Click Back Home")
    def click_back_home(self) -> "OrderConfirmationPage":
        logger.debug("Clicking Back Home")
        self.click(self.BACK_HOME_BUTTON)
        return self
