"""Data Access Object classes.
Wraps ORM queries behind class methods so consumers don't open sessions or write filters directly.
The layer between raw database access and the rest of the app.
"""
from __future__ import annotations

from sqlmodel import select, func

from Database.db import Database, db
from domain.models import (
    MathContent,
    MathSubject,
    MathTopic,
    QuizSubject,
    QuizTopic,
    ScienceQuiz,
    ScienceSubject,
    ScienceTopicRow,
    DictionaryWord,
    QuizAttempt,
)
from models.records import (
    MathLearningEntry,
    QuizAttemptRecord,
    ScienceQuestion,
    VocabularyWord,
)


class BaseDAO:
    """Holds the `Database` instance shared by all DAOs."""

    def __init__(self, database: Database = db) -> None:
        self.db = database


class MathContentDAO(BaseDAO):
    """Read access to math learning content."""

    def list_steps(
        self, subject_name: str, topic_name: str | None = None
    ) -> list[MathLearningEntry]:
        """Return math learning entries for a subject (and optional topic), ordered by id."""
        with self.db.session_scope() as session:
            query = (
                select(MathContent)
                .join(MathSubject, MathContent.subject_id == MathSubject.id)
                .where(func.lower(MathSubject.name) == subject_name.lower())
            )
            if topic_name:
                query = (
                    query.join(MathTopic, MathContent.topic_id == MathTopic.id)
                    .where(func.lower(MathTopic.name) == topic_name.lower())
                )
            query = query.order_by(MathContent.id)
            rows = list(session.exec(query).all())
            return [
                MathLearningEntry(
                    title=row.title or "",
                    explanation=row.explanation or "",
                    expression=row.expression or "",
                    answer=row.answer or "",
                    image=row.image or "",
                    topic=row.topic_obj.name if row.topic_obj else "",
                )
                for row in rows
            ]


class ScienceQuizDAO(BaseDAO):
    """Read access to science quiz questions."""

    def list_questions(self, subject_name: str, source: str) -> list[ScienceQuestion]:
        """Return all quiz rows for a (subject, source) pair.

        ``source`` matches against ``ScienceTopicRow.name``.
        """
        with self.db.session_scope() as session:
            query = (
                select(ScienceQuiz)
                .join(ScienceSubject, ScienceQuiz.subject_id == ScienceSubject.id)
                .join(ScienceTopicRow, ScienceQuiz.topic_id == ScienceTopicRow.id)
                .where(
                    func.lower(ScienceSubject.name) == subject_name.lower(),
                    func.lower(ScienceTopicRow.name) == source.lower(),
                )
            )
            rows = list(session.exec(query).all())
            return [
                ScienceQuestion(
                    question=row.question,
                    source=row.topic_obj.name if row.topic_obj else "",
                    options=[opt.text for opt in row.options],
                    correct_answer=next(
                        (opt.text for opt in row.options if opt.is_correct),
                        "",
                    ),
                )
                for row in rows
            ]


class DictionaryWordDAO(BaseDAO):
    """Read access to dictionary words."""

    @staticmethod
    def _to_word(row: DictionaryWord) -> VocabularyWord:
        return VocabularyWord(
            english=row.english or "",
            german=row.german or "",
            french=row.french or "",
            meanings=row.meanings or "",
            topic=row.topic_obj.name if row.topic_obj else "",
            word_type=row.word_type_obj.name if row.word_type_obj else "",
            article_german=row.article_german_obj.text if row.article_german_obj else "",
            article_french=row.article_french_obj.text if row.article_french_obj else "",
        )

    def list_by_topic(self, topic: str) -> list[VocabularyWord]:
        """Return words for *topic*; pass 'all' (or empty) for every word."""
        from domain.models import DictionaryTopic
        with self.db.session_scope() as session:
            query = select(DictionaryWord)
            if topic and topic != "all":
                query = query.join(
                    DictionaryTopic, DictionaryWord.topic_id == DictionaryTopic.id
                ).where(DictionaryTopic.name == topic)
            rows = list(session.exec(query).all())
            return [self._to_word(row) for row in rows]

    def list_topics(self) -> list[str]:
        """Return distinct non-empty topic strings, sorted."""
        from domain.models import DictionaryTopic
        with self.db.session_scope() as session:
            query = select(DictionaryTopic.name).where(
                DictionaryTopic.name.isnot(None), DictionaryTopic.name != ""
            )
            rows = session.exec(query).all()
            return sorted(rows)

    def list_for_learning(
        self, topic_filter: str, limit: int
    ) -> list[VocabularyWord]:
        """Return up to *limit* words (with non-empty meanings) for the given topic."""
        from domain.models import DictionaryTopic
        with self.db.session_scope() as session:
            query = (
                select(DictionaryWord)
                .where(
                    DictionaryWord.meanings.isnot(None),
                    DictionaryWord.meanings != "",
                )
            )
            if topic_filter:
                query = query.join(
                    DictionaryTopic, DictionaryWord.topic_id == DictionaryTopic.id
                ).where(DictionaryTopic.name == topic_filter)
            query = query.order_by(DictionaryWord.id).limit(limit)
            rows = list(session.exec(query).all())
            return [self._to_word(row) for row in rows]


class QuizAttemptDAO(BaseDAO):
    """Read/write access to quiz attempt history (score & mistakes).

    Normalised across three tables:
      - quiz_subject  (lookup: subject name)
      - quiz_topic    (lookup: topic name within a subject)
      - quiz_attempt  (one row per finished quiz session; subject reachable
                       via ``topic.subject`` — no redundant subject_id stored)
    """

    @staticmethod
    def _get_or_create_subject(session, name: str) -> QuizSubject:
        row = session.exec(
            select(QuizSubject).where(func.lower(QuizSubject.name) == name.lower())
        ).first()
        if row is None:
            row = QuizSubject(name=name)
            session.add(row)
            session.flush()
        return row

    @staticmethod
    def _get_or_create_topic(session, subject_id: int, name: str) -> QuizTopic:
        row = session.exec(
            select(QuizTopic).where(
                QuizTopic.subject_id == subject_id,
                func.lower(QuizTopic.name) == name.lower(),
            )
        ).first()
        if row is None:
            row = QuizTopic(subject_id=subject_id, name=name)
            session.add(row)
            session.flush()
        return row

    def record(
        self,
        subject: str,
        topic: str,
        score: int,
        attempts: int,
        hints_used: int = 0,
        filters: dict[str, str] | None = None,
    ) -> QuizAttemptRecord:
        """Persist a finished quiz session and return the saved record."""
        # We are using json format to store the selected filters of the saved quiz attempt
        import json

        with self.db.session_scope() as session:
            subj_row = self._get_or_create_subject(session, subject)
            topic_row = self._get_or_create_topic(session, subj_row.id, topic)
            row = QuizAttempt(
                topic_id=topic_row.id,
                score=score,
                attempts=attempts,
                hints_used=max(0, hints_used),
                filters=json.dumps(filters) if filters else None,
            )
            session.add(row)
            session.flush()
            session.refresh(row)
            return QuizAttemptRecord(
                score=row.score,
                attempts=row.attempts,
                hints_used=row.hints_used,
                filters=row.filters,
                created_at=row.created_at,
            )

    def list_for(
        self, subject: str, topic: str, limit: int = 20
    ) -> list[QuizAttemptRecord]:
        """Return the most recent attempts for a (subject, topic), newest first."""
        with self.db.session_scope() as session:
            query = (
                select(QuizAttempt)
                .join(QuizTopic, QuizAttempt.topic_id == QuizTopic.id)
                .join(QuizSubject, QuizTopic.subject_id == QuizSubject.id)
                .where(
                    func.lower(QuizSubject.name) == subject.lower(),
                    func.lower(QuizTopic.name) == topic.lower(),
                )
                .order_by(QuizAttempt.created_at.desc())
                .limit(limit)
            )
            rows = list(session.exec(query).all())
            return [
                QuizAttemptRecord(
                    score=row.score,
                    attempts=row.attempts,
                    hints_used=row.hints_used,
                    filters=row.filters,
                    created_at=row.created_at,
                )
                for row in rows
            ]
