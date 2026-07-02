@cart
Feature: Cart Management
  As an automation engineer
  I want to verify cart add, remove, and validation behavior
  So that any cart regression is caught before it impacts the checkout flow

  Background:
    Given the user is logged in with valid credentials

  @smoke @cart
  Scenario: Adding one item increments cart badge to 1
    When they add "Sauce Labs Backpack" to the cart
    Then the cart badge should show 1

  @regression @cart
  Scenario: Adding two items increments badge to 2
    When they add "Sauce Labs Backpack" to the cart
    And they add "Sauce Labs Bike Light" to the cart
    Then the cart badge should show 2

  @smoke @cart
  Scenario: Cart page shows correct item details
    When they add "Sauce Labs Backpack" to the cart
    And they open the cart
    Then the cart should contain "Sauce Labs Backpack"

  @regression @cart
  Scenario: Removing item from cart updates badge
    When they add "Sauce Labs Backpack" to the cart
    And they add "Sauce Labs Bike Light" to the cart
    And they open the cart
    And they remove "Sauce Labs Bike Light" from the cart
    Then the cart badge should show 1

  @regression @cart
  Scenario: Removing last item results in empty cart
    When they add "Sauce Labs Backpack" to the cart
    And they open the cart
    And they remove "Sauce Labs Backpack" from the cart
    Then the cart should be empty
