"""Data Access Object classes.
Wraps ORM queries behind class methods so consumers don't open sessions or write filters directly.
The layer between raw database access and the rest of the app.
"""
from __future__ import annotations

from sqlalchemy import func

from Database.db import Database, db
from Database.seed import (
    DictionaryWord,
    MathContent,
    MathSubject,
    ScienceQuiz,
    ScienceSubject,
)


class BaseDAO:
    """Holds the `Database` instance shared by all DAOs."""

    def __init__(self, database: Database = db) -> None:
        self.db = database


class MathContentDAO(BaseDAO):
    """Read access to math learning content."""

    def list_steps(
        self, subject_name: str, topic_name: str | None = None
    ) -> list[MathContent]:
        """Return MathContent rows for a subject (and optional topic), ordered by id."""
        with self.db.session_scope() as session:
            query = (
                session.query(MathContent)
                .join(MathSubject, MathContent.subject)
                .filter(func.lower(MathSubject.name) == subject_name.lower())
            )
            if topic_name:
                query = query.filter(
                    func.lower(MathContent.topic) == topic_name.lower()
                )
            rows = query.order_by(MathContent.id).all()
            session.expunge_all()
            return rows


class ScienceQuizDAO(BaseDAO):
    """Read access to science quiz questions."""

    def list_questions(self, subject_name: str, source: str) -> list[ScienceQuiz]:
        """Return all quiz rows for a (subject, source) pair."""
        with self.db.session_scope() as session:
            rows = (
                session.query(ScienceQuiz)
                .join(ScienceSubject, ScienceQuiz.subject)
                .filter(
                    func.lower(ScienceSubject.name) == subject_name.lower(),
                    func.lower(ScienceQuiz.source) == source.lower(),
                )
                .all()
            )
            session.expunge_all()
            return rows


class DictionaryWordDAO(BaseDAO):
    """Read access to dictionary words."""

    def list_by_topic(self, topic: str) -> list[DictionaryWord]:
        """Return words for *topic*; pass 'all' (or empty) for every word."""
        with self.db.session_scope() as session:
            query = session.query(DictionaryWord)
            if topic and topic != "all":
                query = query.filter(DictionaryWord.topic == topic)
            rows = query.all()
            session.expunge_all()
            return rows

    def list_topics(self) -> list[str]:
        """Return distinct non-empty topic strings, sorted."""
        with self.db.session_scope() as session:
            rows = (
                session.query(DictionaryWord.topic)
                .filter(DictionaryWord.topic.isnot(None), DictionaryWord.topic != "")
                .distinct()
                .all()
            )
            return sorted(t[0] for t in rows)

    def list_for_learning(
        self, topic_filter: str, limit: int
    ) -> list[DictionaryWord]:
        """Return up to *limit* words (with non-empty meanings) for the given topic."""
        with self.db.session_scope() as session:
            query = session.query(DictionaryWord).filter(
                DictionaryWord.meanings.isnot(None),
                DictionaryWord.meanings != "",
            )
            if topic_filter:
                query = query.filter(DictionaryWord.topic == topic_filter)
            rows = (
                query.order_by(DictionaryWord.id).limit(limit).all()
            )
            session.expunge_all()
            return rows
