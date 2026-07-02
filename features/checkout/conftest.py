"""Fixtures for the checkout feature area — cart pre-populated with one item."""
from __future__ import annotations

import pytest

from pages.inventory_page import InventoryPage


@pytest.fixture(autouse=False)
def cart_with_item(inventory_page: InventoryPage) -> None:
    """Pre-populate the cart with Sauce Labs Backpack before checkout tests."""
    inventory_page.add_item_to_cart("Sauce Labs Backpack")
    inventory_page.header.go_to_cart()
