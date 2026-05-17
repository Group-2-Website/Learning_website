import csv
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_DATABASE_DIR = os.path.join(_PROJECT_ROOT, "Database")
_CSV_DIR = os.path.join(_DATABASE_DIR, "csv")
_DATABASE_PATH = os.path.join(_DATABASE_DIR, "learning.db")


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


class MathContent(ContentMixin, Base):

    __tablename__ = "math_content"

    id = Column(Integer, primary_key=True)
    subject = Column(String)   # "operations" or "fractions"


class ScienceQuiz(Base):

    __tablename__ = "science_quiz"

    id = Column(Integer, primary_key=True)
    subject = Column(String, nullable=False)   # "biology" or "geography"
    source= Column(String, nullable=False)
    question = Column(String, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)


engine = create_engine(f"sqlite:///{_DATABASE_PATH}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


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
    session = Session()
    try:
        rows = read_csv_rows(os.path.join(_CSV_DIR, "flashcard_words_cleaned.csv"))
        # Keep import idempotent across repeated runs.
        session.query(DictionaryWord).delete()
        words = [
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
        ]
        session.add_all(words)
        session.commit()
        print("dictionary imported")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def import_operations():
    session = Session()
    try:
        rows = read_csv_rows(os.path.join(_CSV_DIR, "operations.csv"))
        # Keep import idempotent across repeated runs.
        session.query(MathContent).filter_by(subject="operations").delete()
        operations = [
            MathContent(
                subject="operations",
                content_type=row["content_type"],
                topic=row["topic"],
                item_type=row["item_type"],
                title=row["title"],
                explanation=row["explanation"],
                expression=row["expression"],
                answer=row["answer"],
                image=row["image"],
            )
            for row in rows
        ]
        session.add_all(operations)
        session.commit()
        print("operations imported into math_content")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def import_fractions():
    session = Session()
    try:
        rows = read_csv_rows(os.path.join(_CSV_DIR, "fractions_learning.csv"))
        # Keep import idempotent across repeated runs.
        session.query(MathContent).filter_by(subject="fractions").delete()
        fractions = [
            MathContent(
                subject="fractions",
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
        ]
        session.add_all(fractions)
        session.commit()
        print("fractions imported into math_content")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def import_grouped_quiz_csvs(subject_name: str, files: list[str]) -> None:

    session = Session()
    try:
        for filename in files:
            file_path = os.path.join(_CSV_DIR, filename)
            source_csv = os.path.splitext(filename)[0].strip().lower()
            reader_rows = read_csv_rows(file_path)
            # Replace only rows for this source CSV to keep grouped imports repeatable.
            session.query(ScienceQuiz).filter_by(
                subject=subject_name, source=source_csv
            ).delete()
            rows = [
                ScienceQuiz(
                    subject=subject_name,
                    source=source_csv,
                    question=row["Question"],
                    option_a=row["Option A"],
                    option_b=row["Option B"],
                    option_c=row["Option C"],
                    correct_answer=row["Correct Answer"],
                )
                for row in reader_rows
            ]
            session.add_all(rows)

        session.commit()
        print(f"{subject_name} imported into science_quiz")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


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
