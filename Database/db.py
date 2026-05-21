from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.engine import Engine


_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_DATABASE_DIR = os.path.join(_PROJECT_ROOT, "Database")
_DATABASE_PATH = os.path.join(_DATABASE_DIR, "learning.db")


class Database:
    """Base class holding the SQLModel engine and session factory."""

    def __init__(self, url: str | None = None) -> None:
        self._url = url or f"sqlite:///{_DATABASE_PATH}"
        # Add check_same_thread=False for NiceGUI threading compatibility
        self._engine: Engine = create_engine(
            self._url,
            connect_args={"check_same_thread": False}
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    def init_schema(self) -> None:
        """Create all tables that don't exist yet (safe to call multiple times)."""
        SQLModel.metadata.create_all(self._engine)

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        """Transactional session: commits on success, rolls back on error."""
        session = Session(self._engine)
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
