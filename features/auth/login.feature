@auth
Feature: Login and Authentication
  As an automation engineer
  I want to verify all login and authentication flows on saucedemo.com
  So that any regression in authentication is caught before it blocks downstream tests

  Background:
    Given the login page is open

  @smoke @auth
  Scenario: Successful login with standard_user
    When they login as "standard_user" with password "secret_sauce"
    Then they should be on the inventory page

  @regression @negative @auth
  Scenario: Locked out user cannot login
    When they login as "locked_out_user" with password "secret_sauce"
    Then the error message should contain "Sorry, this user has been locked out"
    And the error message should be visible

  @regression @negative @auth
  Scenario Outline: Invalid credentials show error
    When they login as "<username>" with password "<password>"
    Then the error message should contain "Username and password do not match"

    Examples:
      | username     | password      |
      | invalid_user | wrong_pass    |
      | wrong_user   | secret_sauce  |

  @regression @negative @auth
  Scenario: Empty username shows validation error
    When they enter password "secret_sauce"
    And they click the Login button
    Then the error message should contain "Username is required"

  @regression @negative @auth
  Scenario: Empty password shows validation error
    When they enter username "standard_user"
    And they click the Login button
    Then the error message should contain "Password is required"

  @regression @auth
  Scenario: Error message can be dismissed
    When they login as "invalid_user" with password "wrong_pass"
    Then the error message should be visible
    And the error message should disappear
