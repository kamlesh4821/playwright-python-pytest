from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.components.header_component import HeaderComponent
from pages.components.menu_component import MenuComponent
from utils.logger import get_logger

logger = get_logger(__name__)


class InventoryPage(BasePage):
    """Page object for the saucedemo.com product inventory screen."""

    PRODUCT_ITEMS: str = ".inventory_item"
    PRODUCT_NAMES: str = ".inventory_item_name"
    PRODUCT_PRICES: str = ".inventory_item_price"
    PRODUCT_IMAGES: str = ".inventory_item_img img"
    SORT_DROPDOWN: str = ".product_sort_container"
    ADD_TO_CART_BTN: str = "[data-test^='add-to-cart']"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = HeaderComponent(page)
        self.menu = MenuComponent(page)

    @allure.step("Get product count")
    def get_product_count(self) -> int:
        return self.count(self.PRODUCT_ITEMS)

    @allure.step("Get all product names")
    def get_all_product_names(self) -> list[str]:
        return [n.strip() for n in self.get_all_texts(self.PRODUCT_NAMES)]

    @allure.step("Get all product prices")
    def get_all_product_prices(self) -> list[str]:
        return [p.strip() for p in self.get_all_texts(self.PRODUCT_PRICES)]

    def get_all_product_prices_as_float(self) -> list[float]:
        return [float(p.lstrip("$")) for p in self.get_all_product_prices()]

    @allure.step("Click product by name: {name}")
    def click_product_by_name(self, name: str) -> "InventoryPage":
        logger.debug(f"Clicking product: {name}")
        self.page.locator(self.PRODUCT_NAMES, has_text=name).click()
        return self

    @allure.step("Click product image: {name}")
    def click_product_image_by_name(self, name: str) -> "InventoryPage":
        item = self.page.locator(self.PRODUCT_ITEMS).filter(has_text=name)
        item.locator("img").click()
        return self

    @allure.step("Add item to cart: {item_name}")
    def add_item_to_cart(self, item_name: str) -> "InventoryPage":
        logger.debug(f"Adding to cart: {item_name}")
        item = self.page.locator(self.PRODUCT_ITEMS).filter(has_text=item_name)
        item.locator("button").click()
        return self

    @allure.step("Add multiple items to cart: {item_names}")
    def add_items_to_cart(self, item_names: list[str]) -> "InventoryPage":
        for name in item_names:
            self.add_item_to_cart(name)
        return self

    @allure.step("Select sort option: {option_text}")
    def select_sort_option(self, option_text: str) -> "InventoryPage":
        logger.debug(f"Selecting sort: {option_text}")
        self.page.locator(self.SORT_DROPDOWN).select_option(label=option_text)
        return self

    def get_current_sort_option(self) -> str:
        return str(self.page.locator(self.SORT_DROPDOWN).input_value())
