"""Step definitions for the checkout flow."""
from __future__ import annotations

import allure
import pytest
from pytest_bdd import given, when, then, parsers

from pages.checkout_address_page import CheckoutAddressPage
from pages.checkout_overview_page import CheckoutOverviewPage
from pages.order_confirmation_page import OrderConfirmationPage


@when(parsers.parse('they fill in checkout info as "{first}" "{last}" "{postal}"'))
@allure.step("When they fill in checkout info")
def fill_checkout_info(
    checkout_address_page: CheckoutAddressPage,
    first: str,
    last: str,
    postal: str,
) -> None:
    checkout_address_page.fill_info(first, last, postal).click_continue()


@when("they submit empty checkout form")
@allure.step("When they submit empty checkout form")
def submit_empty_form(checkout_address_page: CheckoutAddressPage) -> None:
    checkout_address_page.click_continue()


@when("they finish the order")
@allure.step("When they finish the order")
def finish_order(checkout_overview_page: CheckoutOverviewPage) -> None:
    checkout_overview_page.click_finish()


@then("the order should be confirmed")
@allure.step("Then the order should be confirmed")
def order_confirmed(order_confirmation_page: OrderConfirmationPage) -> None:
    order_confirmation_page.expect_url("**/checkout-complete.html")
    assert "Thank you" in order_confirmation_page.get_header_text()


@then(parsers.parse('the checkout error should contain "{text}"'))
@allure.step('Then the checkout error should contain "{text}"')
def checkout_error_contains(checkout_address_page: CheckoutAddressPage, text: str) -> None:
    assert text in checkout_address_page.get_error_message()


@then("totals should be calculated correctly")
@allure.step("Then totals should be calculated correctly")
def totals_correct(checkout_overview_page: CheckoutOverviewPage) -> None:
    item_total = checkout_overview_page.get_item_total_as_float()
    tax = checkout_overview_page.get_tax_as_float()
    grand_total = checkout_overview_page.get_total_as_float()
    assert abs(grand_total - (item_total + tax)) < 0.01
