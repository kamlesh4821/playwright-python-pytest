"""Step definitions for database validation scenarios."""
from __future__ import annotations

import allure
from pytest_bdd import then, parsers
from sqlalchemy.orm import Session

from db.queries.order_queries import OrderQueries
from db.queries.user_queries import UserQueries


@then(parsers.parse('an order should exist in the database for "{username}"'))
@allure.step('Then an order should exist in the database for "{username}"')
def order_exists_in_db(db_session: Session, username: str) -> None:
    assert OrderQueries.order_exists_for_user(db_session, username), (
        f"No order found in database for user '{username}'"
    )


@then(parsers.parse('the user "{username}" should exist in the database'))
@allure.step('Then the user "{username}" should exist in the database')
def user_exists_in_db(db_session: Session, username: str) -> None:
    assert UserQueries.user_exists(db_session, username), (
        f"User '{username}' not found in database"
    )
