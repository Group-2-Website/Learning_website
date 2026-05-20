"""Database facade: owns the engine, provides session management.

The rest of the app should not call `create_engine` or `sessionmaker` directly.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session as OrmSession, sessionmaker


_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_DATABASE_DIR = os.path.join(_PROJECT_ROOT, "Database")
_DATABASE_PATH = os.path.join(_DATABASE_DIR, "learning.db")


class Base(DeclarativeBase):
    """Base class shared by all ORM models."""

class Database:
    """Base class holding the SQLAlchemy engine and session factory."""

    def __init__(self, url: str | None = None) -> None:
        self._url = url or f"sqlite:///{_DATABASE_PATH}"
        self._engine: Engine = create_engine(self._url)
        self._session_factory = sessionmaker(bind=self._engine)

    @property
    def engine(self) -> Engine:
        return self._engine

    def init_schema(self) -> None:
        """Create all tables defined on `Base.metadata`."""
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session_scope(self) -> Iterator[OrmSession]:
        """Transactional session: commits on success, rolls back on error."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Module-level instance, used by seed.py and dao.py.
db = Database()
