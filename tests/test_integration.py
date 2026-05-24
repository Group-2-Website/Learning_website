from database.dao import DictionaryWordDAO, MathContentDAO, ScienceQuizDAO
from core.quiz_card import QuizCard
from subjects.science.science import Biology


class TestMathContentDAO:
    def test_list_steps_returns_seeded_rows(self, database, seeded_math):
        dao = MathContentDAO(database)
        rows = dao.list_steps("fractions")
        assert len(rows) == 2

    def test_list_steps_filters_by_topic(self, database, seeded_math):
        dao = MathContentDAO(database)
        rows = dao.list_steps("fractions", topic_name="add")
        assert len(rows) == 1
        assert rows[0].topic == "add"

    def test_list_steps_unknown_subject_returns_empty(self, database, seeded_math):
        dao = MathContentDAO(database)
        rows = dao.list_steps("unknown")
        assert rows == []


class TestScienceQuizDAO:
    def test_list_questions_returns_seeded_rows(self, database, seeded_science):
        dao = ScienceQuizDAO(database)
        rows = dao.list_questions("biology", "animals")
        assert len(rows) == 2

    def test_list_questions_filters_by_source(self, database, seeded_science):
        dao = ScienceQuizDAO(database)
        rows = dao.list_questions("biology", "plants")
        assert rows == []

    def test_list_questions_unknown_subject_returns_empty(self, database, seeded_science):
        dao = ScienceQuizDAO(database)
        rows = dao.list_questions("chemistry", "atoms")
        assert rows == []


class TestDictionaryWordDAO:
    def test_list_by_topic_returns_only_matching_words(self, database, seeded_dictionary):
        dao = DictionaryWordDAO(database)
        rows = dao.list_by_topic("food")
        assert len(rows) == 2
        assert all(w.topic == "food" for w in rows)

    def test_list_by_topic_all_returns_every_word(self, database, seeded_dictionary):
        dao = DictionaryWordDAO(database)
        rows = dao.list_by_topic("all")
        assert len(rows) == 3

    def test_list_topics_returns_distinct_sorted_topics(self, database, seeded_dictionary):
        dao = DictionaryWordDAO(database)
        topics = dao.list_topics()
        assert topics == ["animals", "food"]

    def test_list_for_learning_respects_limit(self, database, seeded_dictionary):
        dao = DictionaryWordDAO(database)
        rows = dao.list_for_learning("food", limit=1)
        assert len(rows) == 1


class TestScienceQuizEndToEnd:
    # monkeypatch: built-in pytest fixture that temporarily swaps an object for the test, then restores it.
    def test_quiz_returns_card_from_seeded_data(self, database, seeded_science, monkeypatch):
        monkeypatch.setattr("subjects.science.science.ScienceQuizDAO", lambda: ScienceQuizDAO(database))

        card = Biology().get_question({"category": "animals"})

        assert isinstance(card, QuizCard)
        assert card.topic == "Biology"
        assert card.correct_answer in {"Frog", "Eagle"}

    def test_quiz_card_has_three_options(self, database, seeded_science, monkeypatch):
        monkeypatch.setattr("subjects.science.science.ScienceQuizDAO", lambda: ScienceQuizDAO(database))

        card = Biology().get_question({"category": "animals"})

        assert len(card.options) == 3

    def test_quiz_returns_fallback_when_db_is_empty(self, database, monkeypatch):
        monkeypatch.setattr("subjects.science.science.ScienceQuizDAO", lambda: ScienceQuizDAO(database))

        card = Biology().get_question({"category": "animals"})

        assert card.question == "No question available."
