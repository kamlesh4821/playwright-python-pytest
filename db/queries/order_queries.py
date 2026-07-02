from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from utils.logger import get_logger

logger = get_logger(__name__)


class OrderQueries:
    """Raw SQL query helpers for the orders and order_items tables."""

    @staticmethod
    def get_latest_order_for_user(session: Session, username: str) -> Optional[dict]:
        """Return the most recent order for a user or None."""
        result = session.execute(
            text(
                "SELECT o.* FROM orders o "
                "JOIN users u ON o.user_id = u.id "
                "WHERE u.username = :username "
                "ORDER BY o.created_at DESC LIMIT 1"
            ),
            {"username": username},
        ).fetchone()
        if result is None:
            return None
        return dict(result._mapping)

    @staticmethod
    def order_exists_for_user(session: Session, username: str) -> bool:
        result = session.execute(
            text(
                "SELECT 1 FROM orders o "
                "JOIN users u ON o.user_id = u.id "
                "WHERE u.username = :username LIMIT 1"
            ),
            {"username": username},
        ).fetchone()
        return result is not None

    @staticmethod
    def get_order_items(session: Session, order_id: int) -> list[dict]:
        results = session.execute(
            text("SELECT * FROM order_items WHERE order_id = :order_id"),
            {"order_id": order_id},
        ).fetchall()
        return [dict(row._mapping) for row in results]
