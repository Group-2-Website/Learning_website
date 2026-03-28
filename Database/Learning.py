import csv
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


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
    article = Column(String)
    meanings = Column(String)
    word_type = Column(String)


class Operation(ContentMixin, Base):
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True)


class Fraction(ContentMixin, Base):
    __tablename__ = "fractions"

    id = Column(Integer, primary_key=True)


engine = create_engine(f"sqlite:///{os.path.join(_PROJECT_ROOT, 'Database', 'learning.db')}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def import_dictionary_words():
    session = Session()
    try:
        with open("flashcard_words_cleaned.csv", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            words = [
                DictionaryWord(
                    english=row["english"],
                    german=row["german"],
                    article=row["article_german"],
                    meanings=row["meanings"],
                    word_type=row["type"],
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
    session = Session()
    try:
        with open("operations.csv", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            operations = [
                Operation(
                    content_type=row["content_type"],
                    topic=row["topic"],
                    item_type=row["item_type"],
                    title=row["title"],
                    explanation=row["explanation"],
                    expression=row["expression"],
                    answer=row["answer"],
                    image=row["image"],
                )
                for row in reader
            ]
            session.add_all(operations)
        session.commit()
        print("operations imported")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def import_fractions():
    session = Session()
    try:
        with open("fractions_learning.csv", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            fractions = [
                Fraction(
                    content_type=row["content_type"],
                    topic=row["topic"],
                    item_type=row["item_type"],
                    title=row["title"],
                    explanation=row["explanation"],
                    expression=row.get("expression", ""),
                    answer=row.get("answer", ""),
                    image="",
                )
                for row in reader
            ]
            session.add_all(fractions)
        session.commit()
        print("fractions imported")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import_dictionary_words()
    import_operations()
    import_fractions()