"""Step definitions for cart management feature."""
from __future__ import annotations

import allure
from pytest_bdd import given, when, then, parsers

from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage


@when(parsers.parse('they add "{item}" to the cart'))
@allure.step('When they add "{item}" to the cart')
def add_item_to_cart(inventory_page: InventoryPage, item: str) -> None:
    inventory_page.add_item_to_cart(item)


@then(parsers.parse("the cart badge should show {count:d}"))
@allure.step("Then the cart badge should show {count}")
def cart_badge_shows(inventory_page: InventoryPage, count: int) -> None:
    assert inventory_page.header.get_cart_badge_count() == count


@then(parsers.parse('the cart should contain "{item}"'))
@allure.step('Then the cart should contain "{item}"')
def cart_contains_item(cart_page: CartPage, item: str) -> None:
    assert item in cart_page.get_cart_item_names()


@then("the cart should be empty")
@allure.step("Then the cart should be empty")
def cart_is_empty(cart_page: CartPage) -> None:
    assert cart_page.is_cart_empty()


@when(parsers.parse('they remove "{item}" from the cart'))
@allure.step('When they remove "{item}" from the cart')
def remove_item(cart_page: CartPage, item: str) -> None:
    cart_page.remove_item_by_name(item)


@when("they proceed to checkout")
@allure.step("When they proceed to checkout")
def proceed_to_checkout(cart_page: CartPage) -> None:
    cart_page.click_checkout()
