from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine


_DATABASE_PATH = Path(__file__).resolve().parent / "learning.db"


def _default_database_url() -> str:
    return f"sqlite:///{_DATABASE_PATH}"


def _is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite:")


def _sqlite_connect_args(url: str) -> dict[str, Any]:
    if not _is_sqlite_url(url):
        return {}
    # check_same_thread=False is required for NiceGUI's threaded request handling.
    return {"check_same_thread": False}


def _ensure_parent_dir(url: str) -> None:
    if not url.startswith("sqlite:///"):
        return
    db_path = Path(url.removeprefix("sqlite:///"))
    if db_path == Path(":memory:"):
        return
    db_path.parent.mkdir(parents=True, exist_ok=True)


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    if engine.dialect.name != "sqlite":
        return

    # SQLite ignores FOREIGN KEY constraints unless explicitly enabled,
    # so turn them on for every new connection. Without this, FK columns
    # (e.g. quiz_attempt.topic_id) would silently accept invalid values.
    @event.listens_for(engine, "connect")
    def _enable_sqlite_fks(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()


class Database:
    """Owns the SQLModel engine and hands out transactional sessions."""

    def __init__(self, url: str | None = None) -> None:
        self._url = url or _default_database_url()
        _ensure_parent_dir(self._url)
        connect_args = _sqlite_connect_args(self._url)
        self._engine = create_engine(
            self._url,
            connect_args=connect_args,
        )
        _enable_sqlite_foreign_keys(self._engine)

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def url(self) -> str:
        return self._url

    def init_schema(self) -> None:
        """Create any tables that don't exist yet (safe to call multiple times)."""
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
