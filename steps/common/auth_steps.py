"""Shared authentication step definitions reused across multiple feature areas."""
from __future__ import annotations

import allure
import pytest
from pytest_bdd import given, when, then

from config.config_loader import ConfigLoader
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@given('"{username}" is logged in')
@allure.step('Given "{username}" is logged in')
def user_is_logged_in(login_page: LoginPage, inventory_page: InventoryPage, username: str) -> None:
    login_page.open().login_as(username, "secret_sauce")
    inventory_page.expect_url("**/inventory.html")


@given("the user is logged in with valid credentials")
@allure.step("Given the user is logged in with valid credentials")
def logged_in_standard_user(
    login_page: LoginPage, inventory_page: InventoryPage, config: ConfigLoader
) -> None:
    login_page.open().login_as(config.get_test_username(), config.get_test_password())
    inventory_page.expect_url("**/inventory.html")
