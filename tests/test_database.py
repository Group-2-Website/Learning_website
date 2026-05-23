from sqlmodel import select

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


def _build_quiz(subject, topic, question, options, correct):
    return ScienceQuiz(
        subject_id=subject.id,
        topic_id=topic.id,
        question=question,
        options=[
            ScienceQuizOption(label=label, text=text, is_correct=(text == correct))
            for label, text in zip("ABC", options)
        ],
    )


def test_saving_science_quiz_persists(db):  # TC_004
    subject = ScienceSubject(name="biology")
    db.add(subject)
    db.commit()
    db.refresh(subject)

    topic = ScienceTopicRow(subject_id=subject.id, name="animals")
    db.add(topic)
    db.commit()
    db.refresh(topic)

    db.add_all([
        _build_quiz(subject, topic, "Which animal lays eggs?",
                    ["Frog", "Dog", "Cat"], correct="Frog"),
        _build_quiz(subject, topic, "Which animal can fly?",
                    ["Ostrich", "Eagle", "Penguin"], correct="Eagle"),
    ])
    db.commit()

    rows = db.exec(
        select(ScienceQuiz)
        .join(ScienceTopicRow, ScienceQuiz.topic_id == ScienceTopicRow.id)
        .where(ScienceTopicRow.name == "animals")
    ).all()

    assert len(rows) == 2
    assert {
        next((opt.text for opt in r.options if opt.is_correct), "")
        for r in rows
    } == {"Frog", "Eagle"}


def test_dictionary_word_stores_translations(db):
    topic = DictionaryTopic(name="Time")
    word_type = WordType(name="noun")
    der = Article(language="de", text="der")
    le = Article(language="fr", text="le")
    db.add_all([topic, word_type, der, le])
    db.commit()

    db.add(DictionaryWord(
        english="evening",
        german="Abend",
        french="soir",
        meanings="evening",
        topic_id=topic.id,
        word_type_id=word_type.id,
        article_german_id=der.id,
        article_french_id=le.id,
    ))
    db.commit()

    word = db.exec(select(DictionaryWord).where(DictionaryWord.english == "evening")).one()

    assert word.german == "Abend"
    assert word.article_german_obj
    assert word.article_german_obj.text == "der"
    assert word.french == "soir"
    assert word.article_french_obj
    assert word.article_french_obj.text == "le"
    assert word.topic_obj
    assert word.topic_obj.name == "Time"
    assert word.word_type_obj
    assert word.word_type_obj.name == "noun"


def test_math_subject_contents_relationship(db):  # TC_005
    subject = MathSubject(name="fractions")
    db.add(subject)
    db.commit()
    db.refresh(subject)

    t_add = MathTopic(subject_id=subject.id, name="addition")
    t_sub = MathTopic(subject_id=subject.id, name="subtraction")
    db.add_all([t_add, t_sub])
    db.commit()

    db.add_all([
        MathContent(subject_id=subject.id, topic_id=t_add.id, content_type="learn",
                    item_type="example", title="Add fractions", explanation="1/2 + 1/2 = 1"),
        MathContent(subject_id=subject.id, topic_id=t_sub.id, content_type="learn",
                    item_type="example", title="Subtract fractions", explanation="1 - 1/2 = 1/2"),
    ])
    db.commit()
    db.refresh(subject)

    assert len(subject.contents) == 2
    assert {
        c.topic_obj.name
        for c in subject.contents
        if c.topic_obj is not None
    } == {"addition", "subtraction"}


def test_deleting_science_subject_cascades_to_quizzes(db):
    subject = ScienceSubject(name="biology")
    db.add(subject)
    db.commit()
    db.refresh(subject)

    topic = ScienceTopicRow(subject_id=subject.id, name="animals")
    db.add(topic)
    db.commit()
    db.refresh(topic)

    db.add_all([
        _build_quiz(subject, topic, "Which animal lays eggs?",
                    ["Frog", "Dog", "Cat"], correct="Frog"),
        _build_quiz(subject, topic, "Which animal can fly?",
                    ["Ostrich", "Eagle", "Penguin"], correct="Eagle"),
    ])
    db.commit()

    db.delete(subject)
    db.commit()

    # Both the quizzes and their options should be gone (cascade).
    assert db.exec(select(ScienceQuiz)).all() == []
    assert db.exec(select(ScienceQuizOption)).all() == []
