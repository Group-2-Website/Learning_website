import pytest
from sqlmodel import Session, SQLModel

from Database.db import Database
from domain.models import DictionaryWord, MathContent, MathSubject, ScienceQuiz, ScienceSubject


@pytest.fixture(scope="function")
def database():
    db = Database("sqlite:///:memory:")
    SQLModel.metadata.create_all(db.engine)
    yield db
    SQLModel.metadata.drop_all(db.engine)


@pytest.fixture(scope="function")
def db(database):
    with Session(database.engine) as session:
        yield session


@pytest.fixture
def seeded_math(db):
    subject = MathSubject(name="fractions")
    db.add(subject)
    db.flush()
    db.add_all([
        MathContent(subject_id=subject.id, content_type="learn", topic="add",
                    item_type="example", title="Adding fractions",
                    explanation="1/2 + 1/4 = 3/4", expression="1/2 + 1/4", answer="3/4"),
        MathContent(subject_id=subject.id, content_type="learn", topic="mul",
                    item_type="example", title="Multiplying fractions",
                    explanation="1/2 × 1/2 = 1/4", expression="1/2 * 1/2", answer="1/4"),
    ])
    db.commit()
    return db


@pytest.fixture
def seeded_science(db):
    subject = ScienceSubject(name="biology")
    db.add(subject)
    db.flush()
    db.add_all([
        ScienceQuiz(subject_id=subject.id, source="animals",
                    question="Which animal lays eggs?",
                    option_a="Frog", option_b="Dog", option_c="Cat",
                    correct_answer="Frog"),
        ScienceQuiz(subject_id=subject.id, source="animals",
                    question="Which animal can fly?",
                    option_a="Ostrich", option_b="Eagle", option_c="Penguin",
                    correct_answer="Eagle"),
    ])
    db.commit()
    return db


@pytest.fixture
def seeded_dictionary(db):
    db.add_all([
        DictionaryWord(english="apple", german="Apfel", french="pomme",
                       meanings="a fruit", topic="food"),
        DictionaryWord(english="bread", german="Brot", french="pain",
                       meanings="baked food", topic="food"),
        DictionaryWord(english="cat", german="Katze", french="chat",
                       meanings="a pet", topic="animals"),
    ])
    db.commit()
    return db



