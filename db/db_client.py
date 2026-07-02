from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from exceptions.database_exception import DatabaseException
from utils.logger import get_logger

logger = get_logger(__name__)


class DBClient:
    """SQLAlchemy database client with connection pooling.

    Scope: session — one instance per test session.
    Use the db_session fixture for per-test transaction isolation.
    """

    def __init__(self, db_url: str) -> None:
        try:
            self._engine = create_engine(
                db_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                echo=False,
            )
            self._session_factory = sessionmaker(bind=self._engine)
            logger.debug(f"DB engine created: {db_url.split('@')[-1]}")
        except Exception as exc:
            raise DatabaseException(f"Failed to create DB engine: {exc}") from exc

    def get_session(self) -> Session:
        return self._session_factory()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Context manager that commits on success and rolls back on failure."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as exc:
            session.rollback()
            raise DatabaseException(f"DB session error: {exc}") from exc
        finally:
            session.close()

    def ping(self) -> bool:
        """Return True if the database is reachable."""
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def dispose(self) -> None:
        self._engine.dispose()
        logger.debug("DB engine disposed.")
