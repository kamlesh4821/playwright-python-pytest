from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class CheckoutOverviewPage(BasePage):
    """Page object for checkout step two — order review screen."""

    CART_ITEMS: str = ".cart_item"
    ITEM_NAMES: str = ".inventory_item_name"
    ITEM_PRICES: str = ".inventory_item_price"
    ITEM_TOTAL: str = ".summary_subtotal_label"
    TAX_LABEL: str = ".summary_tax_label"
    TOTAL_LABEL: str = ".summary_total_label"
    FINISH_BUTTON: str = "[data-test='finish']"
    CANCEL_BUTTON: str = "[data-test='cancel']"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @allure.step("Get item names on overview")
    def get_item_names(self) -> list[str]:
        return [n.strip() for n in self.get_all_texts(self.ITEM_NAMES)]

    @allure.step("Get item total")
    def get_item_total(self) -> str:
        return self.get_text(self.ITEM_TOTAL)

    @allure.step("Get tax amount")
    def get_tax(self) -> str:
        return self.get_text(self.TAX_LABEL)

    @allure.step("Get grand total")
    def get_total(self) -> str:
        return self.get_text(self.TOTAL_LABEL)

    def get_total_as_float(self) -> float:
        raw = self.get_total().replace("Total:", "").replace("$", "").strip()
        return float(raw)

    def get_item_total_as_float(self) -> float:
        raw = self.get_item_total().replace("Item total:", "").replace("$", "").strip()
        return float(raw)

    def get_tax_as_float(self) -> float:
        raw = self.get_tax().replace("Tax:", "").replace("$", "").strip()
        return float(raw)

    @allure.step("Click Finish — place order")
    def click_finish(self) -> "CheckoutOverviewPage":
        logger.debug("Clicking Finish to place order")
        self.click(self.FINISH_BUTTON)
        return self

    @allure.step("Click Cancel on overview")
    def click_cancel(self) -> "CheckoutOverviewPage":
        self.click(self.CANCEL_BUTTON)
        return self
