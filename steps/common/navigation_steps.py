"""Shared navigation step definitions."""
from __future__ import annotations

import allure
from pytest_bdd import given, when, then

from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage


@when("they navigate to the catalog")
@allure.step("When they navigate to the catalog")
def navigate_to_catalog(inventory_page: InventoryPage, config) -> None:  # type: ignore[no-untyped-def]
    inventory_page.navigate(config.get_base_url() + "/inventory.html")


@when("they open the cart")
@allure.step("When they open the cart")
def open_cart(inventory_page: InventoryPage) -> None:
    inventory_page.header.go_to_cart()
