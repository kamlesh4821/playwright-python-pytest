from __future__ import annotations

from sqlalchemy.orm import Session

from db.queries.user_queries import UserQueries
from utils.logger import get_logger
from utils.test_data_provider import TestDataProvider

logger = get_logger(__name__)


class DBSetupHelper:
    """Convenience methods for test data setup.

    All operations run within the test's db_session fixture,
    which automatically rolls back after each test.
    No explicit cleanup needed.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def ensure_user_exists(self, username: str, user_type: str = "standard") -> int:
        """Insert a test user if they don't exist. Return the user ID."""
        if UserQueries.user_exists(self._session, username):
            user = UserQueries.get_user_by_username(self._session, username)
            return int(user["id"])  # type: ignore[index]
        email = TestDataProvider.random_email()
        return UserQueries.insert_user(
            self._session, username=username, email=email, user_type=user_type
        )
