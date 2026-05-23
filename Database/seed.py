from __future__ import annotations

import csv
import os

from sqlmodel import Session, select, delete

from Database.db import db
from domain.models import (
    Article,
    DictionaryTopic,
    DictionaryWord,
    MathContent,
    MathSubject,
    MathTopic,
    ScienceQuiz,
    ScienceQuizOption,
    ScienceSubject,
    ScienceTopicRow,
    WordType,
)


_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_DATABASE_DIR = os.path.join(_PROJECT_ROOT, "Database")
_CSV_DIR = os.path.join(_DATABASE_DIR, "csv")


def _get_or_create(session: Session, model, **fields):
    """Return an existing row matching *fields* or create one."""
    statement = select(model).filter_by(**fields)
    instance = session.exec(statement).first()
    if instance is None:
        instance = model(**fields)
        session.add(instance)
        session.flush()
    return instance

def read_csv_rows(file_path: str) -> list[dict]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    # Try UTF-8 BOM first, then fall back to Windows cp1252 for CSV exports
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            with open(file_path, encoding=encoding) as file:
                return list(csv.DictReader(file))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV file: {file_path}")


class DataSeeder:

    def seed(self, session: Session) -> None:
        """Import all content from CSV files."""
        self._seed_dictionary_words(session)
        self._seed_math_subject(session, "operations", "operations.csv")
        self._seed_math_subject(session, "fractions", "fractions_learning.csv")
        self._seed_science_subject(session, "biology", ["animals.csv", "plant.csv", "human_body.csv"])
        self._seed_science_subject(session, "geography", ["continants.csv", "countries.csv", "water in the earth.csv"])

    # Dictionary
    def _seed_dictionary_words(self, session: Session) -> None:
        rows = read_csv_rows(os.path.join(_CSV_DIR, "flashcard_words_cleaned.csv"))
        # Keep import idempotent across repeated runs.
        session.exec(delete(DictionaryWord))

        def _maybe(value: str | None) -> str:
            return (value or "").strip()

        for row in rows:
            topic_name = _maybe(row.get("topic"))
            type_name = _maybe(row.get("type"))
            de_text = _maybe(row.get("article_german"))
            fr_text = _maybe(row.get("article_french"))

            session.add(DictionaryWord(
                english=row.get("english"),
                german=row.get("german"),
                french=row.get("french"),
                meanings=row.get("meanings"),
                topic_id=_get_or_create(session, DictionaryTopic, name=topic_name).id if topic_name else None,
                word_type_id=_get_or_create(session, WordType, name=type_name).id if type_name else None,
                article_german_id=_get_or_create(session, Article, language="de", text=de_text).id if de_text else None,
                article_french_id=_get_or_create(session, Article, language="fr", text=fr_text).id if fr_text else None,
            ))
        print("dictionary imported")

    # Math
    def _seed_math_subject(self, session: Session, subject_name: str, csv_filename: str) -> None:
        rows = read_csv_rows(os.path.join(_CSV_DIR, csv_filename))
        subject_row = _get_or_create(session, MathSubject, name=subject_name)
        # Idempotent: wipe existing content/topics for this subject only.
        session.exec(delete(MathContent).where(MathContent.subject_id == subject_row.id))
        session.exec(delete(MathTopic).where(MathTopic.subject_id == subject_row.id))

        for row in rows:
            topic_name = (row.get("topic") or "").strip()
            topic_row = (
                _get_or_create(session, MathTopic, subject_id=subject_row.id, name=topic_name)
                if topic_name else None
            )
            session.add(MathContent(
                subject_id=subject_row.id,
                topic_id=topic_row.id if topic_row else None,
                content_type=row.get("content_type"),
                item_type=row.get("item_type"),
                title=row.get("title"),
                explanation=row.get("explanation"),
                expression=row.get("expression", ""),
                answer=row.get("answer", ""),
                image=row.get("image", ""),
            ))
        print(f"{subject_name} imported into math_content")

    # Science
    def _seed_science_subject(self, session: Session, subject_name: str, files: list[str]) -> None:
        subject_row = _get_or_create(session, ScienceSubject, name=subject_name)

        for filename in files:
            file_path = os.path.join(_CSV_DIR, filename)
            topic_name = os.path.splitext(filename)[0].strip().lower()
            reader_rows = read_csv_rows(file_path)

            topic_row = _get_or_create(
                session, ScienceTopicRow,
                subject_id=subject_row.id, name=topic_name,
            )
            # Replace only rows for this topic to keep grouped imports repeatable.
            existing_quizzes = session.exec(
                select(ScienceQuiz).where(ScienceQuiz.topic_id == topic_row.id)
            ).all()
            for q in existing_quizzes:
                session.delete(q)
            session.flush()

            for row in reader_rows:
                correct = (row.get("Correct Answer") or "").strip()
                texts = {
                    "A": row.get("Option A", ""),
                    "B": row.get("Option B", ""),
                    "C": row.get("Option C", ""),
                }
                quiz = ScienceQuiz(
                    subject_id=subject_row.id,
                    topic_id=topic_row.id,
                    question=row["Question"],
                    options=[
                        ScienceQuizOption(
                            label=label, text=text,
                            is_correct=(text.strip() == correct),
                        )
                        for label, text in texts.items()
                    ],
                )
                session.add(quiz)
        print(f"{subject_name} imported into science_quiz")


if __name__ == "__main__":
    db.init_schema()
    with db.session_scope() as session:
        DataSeeder().seed(session)
