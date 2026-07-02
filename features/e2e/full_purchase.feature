@e2e
Feature: Full Purchase Journey — End to End
  As an automation engineer
  I want a single tagged E2E scenario covering the complete purchase flow
  So that the most critical user journey is verified on every commit

  @smoke @e2e
  Scenario: Standard user completes a full purchase from login to confirmation
    Given the user is logged in with valid credentials
    When they add "Sauce Labs Backpack" to the cart
    And they open the cart
    And they proceed to checkout
    And they fill in checkout info as "Test" "User" "12345"
    And they finish the order
    Then the order should be confirmed
