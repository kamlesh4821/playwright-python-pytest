@checkout
Feature: Checkout Flow
  As an automation engineer
  I want to verify the complete checkout process
  So that any regression in the purchase path is detected immediately

  Background:
    Given the user is logged in with valid credentials
    And they add "Sauce Labs Backpack" to the cart
    And they open the cart
    And they proceed to checkout

  @smoke @checkout
  Scenario: Valid personal info advances to order review
    When they fill in checkout info as "Test" "User" "12345"
    Then the cart should contain "Sauce Labs Backpack"

  @regression @negative @checkout
  Scenario Outline: Blank required field shows validation error
    When they submit empty checkout form
    Then the checkout error should contain "<error_text>"

    Examples:
      | error_text           |
      | First Name is required |
      | Last Name is required  |
      | Postal Code is required |

  @smoke @checkout
  Scenario: Order totals are calculated correctly on review page
    When they fill in checkout info as "Test" "User" "12345"
    Then totals should be calculated correctly

  @smoke @checkout
  Scenario: Completing checkout reaches confirmation page
    When they fill in checkout info as "Test" "User" "12345"
    And they finish the order
    Then the order should be confirmed
