import csv
import os
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


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


engine = create_engine(f"sqlite:///{os.path.join(_PROJECT_ROOT, 'Database', 'learning.db')}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


_DB_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_csv(csv_filename: str, subject_tag: str) -> None:
    """Import a CSV file into *learning_steps* with the given *subject_tag*."""
    csv_path = os.path.join(_DB_DIR, csv_filename)
    session = Session()
    try:
        with open(csv_path, encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            rows = [
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
                for row in reader
                if row.get("content_type") and row.get("title")
            ]
            session.add_all(rows)
        session.commit()
        print(f"{subject_tag} imported ({len(rows)} rows)")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def import_dictionary_words():
    session = Session()
    try:
        with open(os.path.join(_DB_DIR, "csv/flashcard_words_cleaned.csv"), encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
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
                for row in reader
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
    _import_csv("csv/operations.csv", "operations")


def import_fractions():
    _import_csv("csv/fractions_learning.csv", "fractions")


if __name__ == "__main__":
    import_dictionary_words()
    import_operations()
    import_fractions()
