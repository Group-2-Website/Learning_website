from fractions import Fraction

from models.quiz_card import QuizCard
from models.topic import FilterDefinition, FilterOption
from subjects.math.fraction_topic import Fractions
from ui.pages.quiz_results import calculate_quiz_result
from subjects.math.operations import Operation


class TestOperationAnswerCheck:
    def setup_method(self):
        self.op = Operation()

    def test_correct_integer_accepted(self):
        ok, _ = self.op.check_answer("7", "7")
        assert ok

    def test_wrong_integer_rejected(self):
        ok, _ = self.op.check_answer("5", "7")
        assert not ok

    def test_non_integer_rejected(self):
        ok, msg = self.op.check_answer("1/2", "7")
        assert not ok
        assert msg

    def test_empty_answer_rejected(self):
        ok, msg = self.op.check_answer("", "7")
        assert not ok
        assert msg


class TestFractionAnswerCheck:
    def setup_method(self):
        self.fractions = Fractions()

    def test_correct_simplified_accepted(self):
        ok, _ = self.fractions.check_answer("1/2", "1/2")
        assert ok

    def test_equivalent_fraction_accepted(self):  # TC_003
        ok, _ = self.fractions.check_answer("2/4", "1/2")
        assert ok

    def test_decimal_accepted(self):
        ok, _ = self.fractions.check_answer("0.5", "1/2")
        assert ok

    def test_wrong_answer_rejected(self):
        ok, _ = self.fractions.check_answer("3/4", "1/2")
        assert not ok


class TestFractionQuestionGeneration:
    def setup_method(self):
        self.fractions = Fractions()

    def test_returns_question_and_answer(self):
        q, a = self.fractions.generate_question()
        assert "=" in q
        assert a

    def test_answer_is_valid_fraction(self):
        for _ in range(20):
            _, a = self.fractions.generate_question()
            Fraction(a)  # must not raise

    def test_add_filter_produces_plus_sign(self):
        q, _ = self.fractions.generate_question({"operation": "add"})
        assert "+" in q

    def test_div_filter_produces_div_sign(self):
        q, _ = self.fractions.generate_question({"operation": "div"})
        assert "÷" in q


class TestFilterDefinition:
    def setup_method(self):
        self.options = [
            FilterOption("easy", "Easy"),
            FilterOption("medium", "Medium"),
            FilterOption("hard", "Hard"),
        ]
        self.fd = FilterDefinition("difficulty", self.options, default="easy")

    def test_valid_value_passes_through(self):
        assert self.fd.sanitize("medium") == "medium"

    def test_invalid_value_falls_back_to_default(self):
        assert self.fd.sanitize("unknown") == "easy"

    def test_options_map_returns_value_label_dict(self):
        expected = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}
        assert self.fd.options_map == expected

    def test_default_taken_from_first_option_when_not_set(self):
        fd = FilterDefinition("level", self.options)
        assert fd.default == "easy"


class TestTopicGetQuestion:
    def setup_method(self):
        self.topic = Operation()

    def test_returns_quiz_card_instance(self):
        card = self.topic.get_question()
        assert isinstance(card, QuizCard)

    def test_quiz_card_topic_matches_name(self):
        card = self.topic.get_question()
        assert card.topic == "Operations"

    def test_quiz_card_question_contains_equals(self):
        card = self.topic.get_question()
        assert "=" in card.question

    def test_quiz_card_correct_answer_is_set(self):
        card = self.topic.get_question()
        assert card.correct_answer != ""


# 6. Quiz result calculation

class TestQuizResultCalculation:
    def test_perfect_score_gives_100_percent_and_5_stars(self):  # TC_001
        pct, stars, msg, _ = calculate_quiz_result(10, 10)
        assert pct == 100
        assert stars == 5.0
        assert msg == "Perfect score! Amazing!"

    def test_above_70_percent_gives_great_job_message(self):  # TC_002
        pct, _, msg, _ = calculate_quiz_result(7, 10)
        assert pct == 70
        assert msg == "Great job! Keep it up!"

    def test_between_40_and_70_gives_good_effort_message(self):
        pct, _, msg, _ = calculate_quiz_result(5, 10)
        assert pct == 50
        assert msg == "Good effort! Keep practising."

    def test_below_40_percent_gives_keep_going_message(self):
        pct, _, msg, _ = calculate_quiz_result(3, 10)
        assert pct == 30
        assert msg == "Keep going — practice makes perfect!"

    def test_zero_attempts_returns_zero_percent_without_crash(self):
        pct, stars, _, _ = calculate_quiz_result(0, 0)
        assert pct == 0
        assert stars == 0.0


class TestTopicQuizAttemptDelegation:
    def setup_method(self):
        self.topic = Operation()

    def test_record_quiz_attempt_delegates_to_quiz_attempt_dao(self, monkeypatch):
        captured = {}

        class _FakeQuizAttemptDAO:
            def record(self, **kwargs):
                captured.update(kwargs)

        monkeypatch.setattr("Database.dao.QuizAttemptDAO", _FakeQuizAttemptDAO)

        self.topic.record_quiz_attempt(
            subject_name="Math",
            score=7,
            attempts=10,
            hints_used=2,
            filters={"difficulty": "easy"},
        )

        assert captured == {
            "subject": "Math",
            "topic": "Operations",
            "score": 7,
            "attempts": 10,
            "hints_used": 2,
            "filters": {"difficulty": "easy"},
        }

    def test_list_quiz_attempts_delegates_to_quiz_attempt_dao(self, monkeypatch):
        expected = ["attempt-1", "attempt-2"]

        class _FakeQuizAttemptDAO:
            def list_for(self, **kwargs):
                assert kwargs == {"subject": "Math", "topic": "Operations", "limit": 5}
                return expected

        monkeypatch.setattr("Database.dao.QuizAttemptDAO", _FakeQuizAttemptDAO)

        rows = self.topic.list_quiz_attempts(subject_name="Math", limit=5)

        assert rows == expected

