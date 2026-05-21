"""Data Access Object classes.
Wraps ORM queries behind class methods so consumers don't open sessions or write filters directly.
The layer between raw database access and the rest of the app.
"""
from __future__ import annotations

from sqlmodel import select, func

from Database.db import Database, db
from domain.models import (
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
                select(MathContent)
                .join(MathSubject, MathContent.subject_id == MathSubject.id)
                .where(func.lower(MathSubject.name) == subject_name.lower())
            )
            if topic_name:
                query = query.where(
                    func.lower(MathContent.topic) == topic_name.lower()
                )
            query = query.order_by(MathContent.id)
            rows = list(session.exec(query).all())
            session.expunge_all()
            return rows


class ScienceQuizDAO(BaseDAO):
    """Read access to science quiz questions."""

    def list_questions(self, subject_name: str, source: str) -> list[ScienceQuiz]:
        """Return all quiz rows for a (subject, source) pair."""
        with self.db.session_scope() as session:
            query = (
                select(ScienceQuiz)
                .join(ScienceSubject, ScienceQuiz.subject_id == ScienceSubject.id)
                .where(
                    func.lower(ScienceSubject.name) == subject_name.lower(),
                    func.lower(ScienceQuiz.source) == source.lower(),
                )
            )
            rows = list(session.exec(query).all())
            session.expunge_all()
            return rows


class DictionaryWordDAO(BaseDAO):
    """Read access to dictionary words."""

    def list_by_topic(self, topic: str) -> list[DictionaryWord]:
        """Return words for *topic*; pass 'all' (or empty) for every word."""
        with self.db.session_scope() as session:
            query = select(DictionaryWord)
            if topic and topic != "all":
                query = query.where(DictionaryWord.topic == topic)
            rows = list(session.exec(query).all())
            session.expunge_all()
            return rows

    def list_topics(self) -> list[str]:
        """Return distinct non-empty topic strings, sorted."""
        with self.db.session_scope() as session:
            query = (
                select(DictionaryWord.topic)
                .where(DictionaryWord.topic.isnot(None), DictionaryWord.topic != "")
                .distinct()
            )
            rows = session.exec(query).all()
            return sorted(t for t in rows)

    def list_for_learning(
        self, topic_filter: str, limit: int
    ) -> list[DictionaryWord]:
        """Return up to *limit* words (with non-empty meanings) for the given topic."""
        with self.db.session_scope() as session:
            query = select(DictionaryWord).where(
                DictionaryWord.meanings.isnot(None),
                DictionaryWord.meanings != "",
            )
            if topic_filter:
                query = query.where(DictionaryWord.topic == topic_filter)
            query = query.order_by(DictionaryWord.id).limit(limit)
            rows = list(session.exec(query).all())
            session.expunge_all()
            return rows
