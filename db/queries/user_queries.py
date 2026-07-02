from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from utils.logger import get_logger

logger = get_logger(__name__)


class UserQueries:
    """Raw SQL query helpers for the users table."""

    @staticmethod
    def get_user_by_username(session: Session, username: str) -> Optional[dict]:
        """Return user record dict or None if not found."""
        result = session.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": username},
        ).fetchone()
        if result is None:
            return None
        return dict(result._mapping)

    @staticmethod
    def user_exists(session: Session, username: str) -> bool:
        result = session.execute(
            text("SELECT 1 FROM users WHERE username = :username LIMIT 1"),
            {"username": username},
        ).fetchone()
        return result is not None

    @staticmethod
    def insert_user(
        session: Session,
        username: str,
        email: str,
        user_type: str = "standard",
    ) -> int:
        """Insert a test user and return the generated ID."""
        result = session.execute(
            text(
                "INSERT INTO users (username, email, user_type) "
                "VALUES (:username, :email, :user_type) RETURNING id"
            ),
            {"username": username, "email": email, "user_type": user_type},
        )
        user_id: int = result.fetchone()[0]  # type: ignore[index]
        logger.debug(f"Inserted user: {username} (id={user_id})")
        return user_id
