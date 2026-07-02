@catalog
Feature: Product Catalog Browsing
  As an automation engineer
  I want to verify the product catalog displays correctly
  So that any regression in catalog rendering is caught automatically

  Background:
    Given the user is logged in with valid credentials

  @smoke @catalog
  Scenario: Inventory page displays exactly 6 products
    Then the catalog should display 6 products

  @smoke @catalog
  Scenario: All product names are visible
    Then all product names should be visible

  @regression @catalog
  Scenario: All product prices are correctly formatted
    Then all product prices should be correctly formatted

  @regression @catalog
  Scenario: Cart badge is absent on initial page load
    Then the cart badge should not be visible

  @regression @catalog
  Scenario: Clicking a product name navigates to detail page
    When they click on product "Sauce Labs Backpack"
    Then the product detail page should be displayed
