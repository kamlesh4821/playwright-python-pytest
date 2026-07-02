"""Step definitions for the product catalog feature."""
from __future__ import annotations

import re

import allure
from pytest_bdd import given, when, then, parsers

from pages.inventory_page import InventoryPage
from pages.product_detail_page import ProductDetailPage
from utils.test_data_provider import TestDataProvider


@then(parsers.parse("the catalog should display {count:d} products"))
@allure.step("Then the catalog should display {count} products")
def catalog_shows_n_products(inventory_page: InventoryPage, count: int) -> None:
    assert inventory_page.get_product_count() == count


@then("all product names should be visible")
@allure.step("Then all product names should be visible")
def all_product_names_visible(inventory_page: InventoryPage) -> None:
    data = TestDataProvider.load("products.yaml")
    expected: list[str] = data["names"]
    actual = inventory_page.get_all_product_names()
    for name in expected:
        assert name in actual, f"Product '{name}' not found in catalog"


@then("all product prices should be correctly formatted")
@allure.step("Then all product prices should be correctly formatted")
def all_prices_formatted(inventory_page: InventoryPage) -> None:
    prices = inventory_page.get_all_product_prices()
    for price in prices:
        assert re.match(r"^\$\d+\.\d{2}$", price), f"Price '{price}' is not formatted correctly"


@when(parsers.parse('they click on product "{name}"'))
@allure.step('When they click on product "{name}"')
def click_product(inventory_page: InventoryPage, name: str) -> None:
    inventory_page.click_product_by_name(name)


@then("the product detail page should be displayed")
@allure.step("Then the product detail page should be displayed")
def product_detail_shown(product_detail_page: ProductDetailPage) -> None:
    product_detail_page.expect_url("**/inventory-item.html*")


@then("the cart badge should not be visible")
@allure.step("Then the cart badge should not be visible")
def cart_badge_not_visible(inventory_page: InventoryPage) -> None:
    assert not inventory_page.header.is_cart_badge_visible()
