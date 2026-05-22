from sqlmodel import select

from domain.models import DictionaryWord, MathContent, MathSubject, ScienceQuiz, ScienceSubject


def test_saving_science_quiz_persists(db):  # TC_004
    subject = ScienceSubject(name="biology")
    db.add(subject)
    db.commit()
    db.refresh(subject)

    db.add_all([
        ScienceQuiz(
            subject_id=subject.id, source="animals",
            question="Which animal lays eggs?",
            option_a="Frog", option_b="Dog", option_c="Cat",
            correct_answer="Frog",
        ),
        ScienceQuiz(
            subject_id=subject.id, source="animals",
            question="Which animal can fly?",
            option_a="Ostrich", option_b="Eagle", option_c="Penguin",
            correct_answer="Eagle",
        ),
    ])
    db.commit()

    rows = db.exec(select(ScienceQuiz).where(ScienceQuiz.source == "animals")).all()

    assert len(rows) == 2
    assert {r.correct_answer for r in rows} == {"Frog", "Eagle"}


def test_dictionary_word_stores_translations(db):
    db.add(DictionaryWord(
        english="evening",
        german="Abend",
        article_german="der",
        french="soir",
        article_french="le",
        meanings="evening",
        word_type="noun",
        topic="Time",
    ))
    db.commit()

    word = db.exec(select(DictionaryWord).where(DictionaryWord.english == "evening")).one()

    assert word.german == "Abend"
    assert word.article_german == "der"
    assert word.french == "soir"
    assert word.article_french == "le"


def test_math_subject_contents_relationship(db):  # TC_005
    subject = MathSubject(name="fractions")
    db.add(subject)
    db.commit()
    db.refresh(subject)

    db.add_all([
        MathContent(subject_id=subject.id, content_type="learn", topic="addition",
                    item_type="example", title="Add fractions", explanation="1/2 + 1/2 = 1"),
        MathContent(subject_id=subject.id, content_type="learn", topic="subtraction",
                    item_type="example", title="Subtract fractions", explanation="1 - 1/2 = 1/2"),
    ])
    db.commit()
    db.refresh(subject)

    assert len(subject.contents) == 2
    assert {c.topic for c in subject.contents} == {"addition", "subtraction"}


def test_deleting_science_subject_cascades_to_quizzes(db):
    subject = ScienceSubject(name="biology")
    db.add(subject)
    db.commit()
    db.refresh(subject)

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

    db.delete(subject)
    db.commit()

    remaining = db.exec(select(ScienceQuiz)).all()
    assert remaining == []
