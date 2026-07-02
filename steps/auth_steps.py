"""Step definitions for the login and authentication feature."""
from __future__ import annotations

import allure
import pytest
from pytest_bdd import given, when, then, parsers

from config.config_loader import ConfigLoader
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


@given("the login page is open")
@allure.step("Given the login page is open")
def login_page_open(login_page: LoginPage) -> None:
    login_page.open()


@when(parsers.parse('they enter username "{username}"'))
@allure.step('When they enter username "{username}"')
def enter_username(login_page: LoginPage, username: str) -> None:
    login_page.enter_username(username)


@when(parsers.parse('they enter password "{password}"'))
@allure.step('When they enter password')
def enter_password(login_page: LoginPage, password: str) -> None:
    login_page.enter_password(password)


@when("they click the Login button")
@allure.step("When they click the Login button")
def click_login(login_page: LoginPage) -> None:
    login_page.click_login()


@when(parsers.parse('they login as "{username}" with password "{password}"'))
@allure.step('When they login as "{username}"')
def login_as(login_page: LoginPage, username: str, password: str) -> None:
    login_page.login_as(username, password)


@then("they should be on the inventory page")
@allure.step("Then they should be on the inventory page")
def on_inventory_page(inventory_page: InventoryPage) -> None:
    inventory_page.expect_url("**/inventory.html")


@then(parsers.parse('the error message should contain "{expected_text}"'))
@allure.step('Then the error message should contain "{expected_text}"')
def error_contains(login_page: LoginPage, expected_text: str) -> None:
    assert expected_text in login_page.get_error_message()


@then("the error message should be visible")
@allure.step("Then the error message should be visible")
def error_visible(login_page: LoginPage) -> None:
    assert login_page.is_error_visible()


@then("the error message should disappear")
@allure.step("Then the error message should disappear")
def error_disappears(login_page: LoginPage) -> None:
    login_page.close_error()
    login_page.expect_hidden(LoginPage.ERROR_CONTAINER)
