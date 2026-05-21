from __future__ import annotations

import csv
import os

from sqlmodel import Session, select, delete

from Database.db import db
from domain.models import (
    DictionaryWord,
    MathContent,
    MathSubject,
    ScienceQuiz,
    ScienceSubject,
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

    for encoding in ("utf-8-sig", "cp1252"):
        try:
            with open(file_path, encoding=encoding) as file:
                return list(csv.DictReader(file))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV file: {file_path}")


class DataSeeder:

    def seed(self, session: Session) -> None:
        """Import all content from CSV files"""
        self._seed_dictionary_words(session)
        self._seed_math_subject(session, "operations", "operations.csv")
        self._seed_math_subject(session, "fractions", "fractions_learning.csv")
        self._seed_science_subject(session, "biology", ["animals.csv", "plant.csv", "human_body.csv"])
        self._seed_science_subject(session, "geography", ["continants.csv", "countries.csv", "water in the earth.csv"])

    def _seed_dictionary_words(self, session: Session) -> None:
        rows = read_csv_rows(os.path.join(_CSV_DIR, "flashcard_words_cleaned.csv"))
        # Keep import idempotent across repeated runs.
        session.exec(delete(DictionaryWord))
        session.add_all(
            DictionaryWord(
                english=row["english"],
                german=row["german"],
                article_german=row["article_german"],
                french=row["french"],
                article_french=row["article_french"],
                meanings=row["meanings"],
                word_type=row["type"],
                topic=row.get("topic", ""),
            )
            for row in rows
        )
        print("dictionary imported")

    def _seed_math_subject(self, session: Session, subject_name: str, csv_filename: str) -> None:
        rows = read_csv_rows(os.path.join(_CSV_DIR, csv_filename))
        subject_row = _get_or_create(session, MathSubject, name=subject_name)
        # Idempotent: wipe existing rows for this subject only.
        session.exec(delete(MathContent).where(MathContent.subject_id == subject_row.id))
        session.add_all(
            MathContent(
                subject=subject_row,
                content_type=row["content_type"],
                topic=row["topic"],
                item_type=row["item_type"],
                title=row["title"],
                explanation=row["explanation"],
                expression=row.get("expression", ""),
                answer=row.get("answer", ""),
                image=row.get("image", ""),
            )
            for row in rows
        )
        print(f"{subject_name} imported into math_content")

    def _seed_science_subject(self, session: Session, subject_name: str, files: list[str]) -> None:
        subject_row = _get_or_create(session, ScienceSubject, name=subject_name)
        for filename in files:
            file_path = os.path.join(_CSV_DIR, filename)
            source_csv = os.path.splitext(filename)[0].strip().lower()
            reader_rows = read_csv_rows(file_path)
            # Replace only rows for this source CSV to keep grouped imports repeatable.
            session.exec(
                delete(ScienceQuiz).where(
                    ScienceQuiz.subject_id == subject_row.id,
                    ScienceQuiz.source == source_csv,
                )
            )
            session.add_all(
                ScienceQuiz(
                    subject=subject_row,
                    source=source_csv,
                    question=row["Question"],
                    option_a=row["Option A"],
                    option_b=row["Option B"],
                    option_c=row["Option C"],
                    correct_answer=row["Correct Answer"],
                )
                for row in reader_rows
            )
        print(f"{subject_name} imported into science_quiz")


if __name__ == "__main__":
    db.init_schema()
    with db.session_scope() as session:
        DataSeeder().seed(session)
