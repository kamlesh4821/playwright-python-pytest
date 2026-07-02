from __future__ import annotations

from db.db_client import DBClient
from exceptions.database_exception import DatabaseException
from utils.logger import get_logger

logger = get_logger(__name__)


def verify_db_connection(db_client: DBClient) -> None:
    """Verify the database is reachable before the test suite starts.

    Raises DatabaseException with a clear, actionable message if unreachable.
    Called once per session from conftest.py.
    """
    if not db_client.ping():
        raise DatabaseException(
            "Cannot connect to PostgreSQL. "
            "Ensure docker-compose is running: 'make db-up'. "
            "Check DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD in your .env file."
        )
    logger.debug("Database health check passed.")
