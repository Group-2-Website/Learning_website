import csv
import os

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_DATABASE_DIR = os.path.join(_PROJECT_ROOT, "Database")
_CSV_DIR = os.path.join(_DATABASE_DIR, "csv")
_DATABASE_PATH = os.path.join(_DATABASE_DIR, "learning.db")


class LearningStepRow(Base):
    __tablename__ = "learning_steps"

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    content_type = Column(String)
    topic = Column(String)
    item_type = Column(String)
    title = Column(String)
    explanation = Column(String)
    expression = Column(String)
    answer = Column(String)
    image = Column(String)


Operation = LearningStepRow
Fraction = LearningStepRow


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


class Biology(Base):
    __tablename__ = "biology"

    id = Column(Integer, primary_key=True)
    source_csv = Column(String, nullable=False)
    question = Column(String, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)


class Geography(Base):
    __tablename__ = "geography"

    id = Column(Integer, primary_key=True)
    source_csv = Column(String, nullable=False)
    question = Column(String, nullable=False)
    option_a = Column(String, nullable=False)
    option_b = Column(String, nullable=False)
    option_c = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)


engine = create_engine(f"sqlite:///{_DATABASE_PATH}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def read_csv_rows(file_path: str) -> list[dict[str, str]]:
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            with open(file_path, encoding=encoding, newline="") as file:
                return list(csv.DictReader(file))
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(
        "utf-8",
        b"",
        0,
        1,
        f"Could not decode CSV file: {file_path}",
    )


def _import_learning_steps(csv_filename: str, subject_tag: str) -> None:
    csv_path = os.path.join(_CSV_DIR, csv_filename)
    session = Session()
    try:
        rows = read_csv_rows(csv_path)
        session.add_all(
            LearningStepRow(
                subject=subject_tag,
                content_type=row.get("content_type", ""),
                topic=row.get("topic", ""),
                item_type=row.get("item_type", ""),
                title=row.get("title", ""),
                explanation=row.get("explanation", ""),
                expression=row.get("expression", ""),
                answer=row.get("answer", ""),
                image=row.get("image", ""),
            )
            for row in rows
            if row.get("content_type") and row.get("title")
        )
        session.commit()
        print(f"{subject_tag} imported")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def import_dictionary_words() -> None:
    session = Session()
    try:
        rows = read_csv_rows(os.path.join(_CSV_DIR, "flashcard_words_cleaned.csv"))
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
        session.commit()
        print("dictionary imported")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def import_operations() -> None:
    _import_learning_steps("operations.csv", "operations")


def import_fractions() -> None:
    _import_learning_steps("fractions_learning.csv", "fractions")


def import_grouped_quiz_csvs(model, files: list[str]) -> None:
    session = Session()
    try:
        for filename in files:
            file_path = os.path.join(_CSV_DIR, filename)
            source_csv = os.path.splitext(filename)[0].strip().lower()
            rows = read_csv_rows(file_path)
            session.add_all(
                model(
                    source_csv=source_csv,
                    question=row["Question"],
                    option_a=row["Option A"],
                    option_b=row["Option B"],
                    option_c=row["Option C"],
                    correct_answer=row["Correct Answer"],
                )
                for row in rows
            )
        session.commit()
        print(f"{model.__tablename__} imported")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def import_biology() -> None:
    import_grouped_quiz_csvs(
        Biology,
        ["animals.csv", "plant.csv", "human_body.csv"],
    )


def import_geography() -> None:
    import_grouped_quiz_csvs(
        Geography,
        ["continants.csv", "countries.csv", "water in the earth.csv"],
    )


if __name__ == "__main__":
    import_dictionary_words()
    import_operations()
    import_fractions()
    import_biology()
    import_geography()
