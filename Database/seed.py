import csv
import os

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from Database.db import Base, db


_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_DATABASE_DIR = os.path.join(_PROJECT_ROOT, "Database")
_CSV_DIR = os.path.join(_DATABASE_DIR, "csv")


class ContentMixin:
    content_type = Column(String)
    topic = Column(String)
    item_type = Column(String)
    title = Column(String)
    explanation = Column(String)
    expression = Column(String)
    answer = Column(String)
    image = Column(String)


class DictionaryWord(Base):
    __tablename__ = "dictionary_words"

    id = Column(Integer, primary_key=True)
    english = Column(String)
    german = Column(String)
    article_german = Column(String)
    french = Column(String)
    article_french = Column(String)
    meanings = Column(String)
    word_type = Column(String)
    topic = Column(String)


class MathSubject(Base):
    """Lookup table for math subjects (operations / fractions)."""

    __tablename__ = "math_subject"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    contents = relationship(
        "MathContent", back_populates="subject", cascade="all, delete-orphan"
    )


class MathContent(ContentMixin, Base):
    __tablename__ = "math_content"

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("math_subject.id"), nullable=False)

    subject = relationship("MathSubject", back_populates="contents")


class ScienceSubject(Base):
    """Lookup table for science subjects (biology / geography)."""

    __tablename__ = "science_subject"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    quizzes = relationship(
        "ScienceQuiz", back_populates="subject", cascade="all, delete-orphan"
    )


class ScienceQuiz(Base):
    __tablename__ = "science_quiz"

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("science_subject.id"), nullable=False)
    source= Column(String, nullable=False)
    question = Column(String, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)

    subject = relationship("ScienceSubject", back_populates="quizzes")


# Create tables for the models declared above.
db.init_schema()


def _get_or_create(session, model, **fields):
    """Return an existing row matching *fields* or create one."""
    instance = session.query(model).filter_by(**fields).first()
    if instance is None:
        instance = model(**fields)
        session.add(instance)
        session.flush()
    return instance


def read_csv_rows(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    for encoding in ("utf-8-sig", "cp1252"):
        try:
            with open(file_path, encoding=encoding) as file:
                return list(csv.DictReader(file))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV file: {file_path}")


def import_dictionary_words():
    with db.session_scope() as session:
        rows = read_csv_rows(os.path.join(_CSV_DIR, "flashcard_words_cleaned.csv"))
        # Keep import idempotent across repeated runs.
        session.query(DictionaryWord).delete()
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


def _import_math_subject(subject_name: str, csv_filename: str) -> None:
    with db.session_scope() as session:
        rows = read_csv_rows(os.path.join(_CSV_DIR, csv_filename))
        subject_row = _get_or_create(session, MathSubject, name=subject_name)
        # Idempotent: wipe existing rows for this subject only.
        session.query(MathContent).filter_by(subject_id=subject_row.id).delete()
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


def import_operations():
    _import_math_subject("operations", "operations.csv")


def import_fractions():
    _import_math_subject("fractions", "fractions_learning.csv")


def import_grouped_quiz_csvs(subject_name: str, files: list[str]) -> None:
    with db.session_scope() as session:
        subject_row = _get_or_create(session, ScienceSubject, name=subject_name)
        for filename in files:
            file_path = os.path.join(_CSV_DIR, filename)
            source_csv = os.path.splitext(filename)[0].strip().lower()
            reader_rows = read_csv_rows(file_path)
            # Replace only rows for this source CSV to keep grouped imports repeatable.
            session.query(ScienceQuiz).filter_by(
                subject_id=subject_row.id, source=source_csv
            ).delete()
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


def import_biology():
    import_grouped_quiz_csvs(
        "biology",
        [
            "animals.csv",
            "plant.csv",
            "human_body.csv",
        ],
    )


def import_geography():
    import_grouped_quiz_csvs(
        "geography",
        [
            "continants.csv",
            "countries.csv",
            "water in the earth.csv",
        ],
    )


if __name__ == "__main__":
    import_dictionary_words()
    import_operations()
    import_fractions()
    import_biology()
    import_geography()
