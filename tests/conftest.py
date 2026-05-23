import pytest
from sqlmodel import Session, SQLModel

from Database.db import Database
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


def _make_quiz(subject, topic, question, options, correct):
    """Helper: build a ScienceQuiz with its three options + is_correct flag."""
    return ScienceQuiz(
        subject_id=subject.id,
        topic_id=topic.id,
        question=question,
        options=[
            ScienceQuizOption(label=label, text=text, is_correct=(text == correct))
            for label, text in zip("ABC", options)
        ],
    )


@pytest.fixture
def seeded_math(db):
    subject = MathSubject(name="fractions")
    db.add(subject)
    db.flush()
    t_add = MathTopic(subject_id=subject.id, name="add")
    t_mul = MathTopic(subject_id=subject.id, name="mul")
    db.add_all([t_add, t_mul])
    db.flush()
    db.add_all([
        MathContent(subject_id=subject.id, topic_id=t_add.id, content_type="learn",
                    item_type="example", title="Adding fractions",
                    explanation="1/2 + 1/4 = 3/4", expression="1/2 + 1/4", answer="3/4"),
        MathContent(subject_id=subject.id, topic_id=t_mul.id, content_type="learn",
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
    topic = ScienceTopicRow(subject_id=subject.id, name="animals")
    db.add(topic)
    db.flush()
    db.add_all([
        _make_quiz(subject, topic, "Which animal lays eggs?",
                   ["Frog", "Dog", "Cat"], correct="Frog"),
        _make_quiz(subject, topic, "Which animal can fly?",
                   ["Ostrich", "Eagle", "Penguin"], correct="Eagle"),
    ])
    db.commit()
    return db


@pytest.fixture
def seeded_dictionary(db):
    # Create the lookup rows up-front, then reference them by FK on each word.
    food = DictionaryTopic(name="food")
    animals = DictionaryTopic(name="animals")
    db.add_all([food, animals])
    db.flush()
    db.add_all([
        DictionaryWord(english="apple", german="Apfel", french="pomme",
                       meanings="a fruit", topic_id=food.id),
        DictionaryWord(english="bread", german="Brot", french="pain",
                       meanings="baked food", topic_id=food.id),
        DictionaryWord(english="cat", german="Katze", french="chat",
                       meanings="a pet", topic_id=animals.id),
    ])
    db.commit()
    return db
