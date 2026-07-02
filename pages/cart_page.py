from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.components.header_component import HeaderComponent
from utils.logger import get_logger

logger = get_logger(__name__)


class CartPage(BasePage):
    """Page object for the saucedemo.com shopping cart screen."""

    CART_ITEMS: str = ".cart_item"
    CART_ITEM_NAMES: str = ".inventory_item_name"
    CART_ITEM_PRICES: str = ".inventory_item_price"
    REMOVE_BUTTON: str = "[data-test^='remove']"
    CONTINUE_SHOPPING_BTN: str = "[data-test='continue-shopping']"
    CHECKOUT_BTN: str = "[data-test='checkout']"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = HeaderComponent(page)

    @allure.step("Get cart item count")
    def get_cart_item_count(self) -> int:
        return self.count(self.CART_ITEMS)

    @allure.step("Get cart item names")
    def get_cart_item_names(self) -> list[str]:
        return [n.strip() for n in self.get_all_texts(self.CART_ITEM_NAMES)]

    @allure.step("Get cart item prices")
    def get_cart_item_prices(self) -> list[str]:
        return [p.strip() for p in self.get_all_texts(self.CART_ITEM_PRICES)]

    def is_cart_empty(self) -> bool:
        return self.count(self.CART_ITEMS) == 0

    @allure.step("Remove item from cart: {name}")
    def remove_item_by_name(self, name: str) -> "CartPage":
        logger.debug(f"Removing from cart: {name}")
        item = self.page.locator(self.CART_ITEMS).filter(has_text=name)
        item.locator(self.REMOVE_BUTTON).click()
        return self

    @allure.step("Click Continue Shopping")
    def click_continue_shopping(self) -> "CartPage":
        self.click(self.CONTINUE_SHOPPING_BTN)
        return self

    @allure.step("Click Checkout")
    def click_checkout(self) -> "CartPage":
        logger.debug("Proceeding to checkout")
        self.click(self.CHECKOUT_BTN)
        return self
