from __future__ import annotations

import allure
from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.components.header_component import HeaderComponent
from utils.logger import get_logger

logger = get_logger(__name__)


class ProductDetailPage(BasePage):
    """Page object for the saucedemo.com product detail screen."""

    PRODUCT_NAME: str = ".inventory_details_name"
    PRODUCT_DESCRIPTION: str = ".inventory_details_desc"
    PRODUCT_PRICE: str = ".inventory_details_price"
    PRODUCT_IMAGE: str = ".inventory_details_img"
    ADD_TO_CART_BUTTON: str = "button[data-test^='add-to-cart'], button[data-test^='remove']"
    BACK_BUTTON: str = "[data-test='back-to-products']"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.header = HeaderComponent(page)

    @allure.step("Get product name")
    def get_product_name(self) -> str:
        return self.get_text(self.PRODUCT_NAME)

    @allure.step("Get product description")
    def get_product_description(self) -> str:
        return self.get_text(self.PRODUCT_DESCRIPTION)

    @allure.step("Get product price")
    def get_product_price(self) -> str:
        return self.get_text(self.PRODUCT_PRICE)

    def get_product_image_src(self) -> str:
        return self.get_attribute(self.PRODUCT_IMAGE, "src") or ""

    def get_button_text(self) -> str:
        return self.get_text(self.ADD_TO_CART_BUTTON)

    @allure.step("Click Add to Cart on detail page")
    def click_add_to_cart(self) -> "ProductDetailPage":
        logger.debug("Clicking Add to Cart on detail page")
        self.click(self.ADD_TO_CART_BUTTON)
        return self

    @allure.step("Click Remove on detail page")
    def click_remove(self) -> "ProductDetailPage":
        logger.debug("Clicking Remove on detail page")
        self.click(self.ADD_TO_CART_BUTTON)
        return self

    @allure.step("Click Back to Products")
    def click_back_to_products(self) -> "ProductDetailPage":
        logger.debug("Navigating back to products")
        self.click(self.BACK_BUTTON)
        return self
