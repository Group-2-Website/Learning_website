import pytest
from subjects.math.fraction_topic import Fractions
from subjects.math.operations import Operation, token_to_int
from subjects.math.mathematics import Math


class TestFractionsCheckAnswer:
    def setup_method(self):
        self.fractions = Fractions()

    def test_correct_simplified(self):
        ok, _ = self.fractions.check_answer("1/2", "1/2")
        assert ok

    def test_equivalent_fraction_accepted(self):
        ok, _ = self.fractions.check_answer("2/4", "1/2")
        assert ok

    def test_decimal_accepted(self):
        ok, _ = self.fractions.check_answer("0.5", "1/2")
        assert ok

    def test_wrong_answer(self):
        ok, _ = self.fractions.check_answer("3/4", "1/2")
        assert not ok

    def test_empty_answer(self):
        ok, msg = self.fractions.check_answer("", "1/2")
        assert not ok
        assert "enter" in msg.lower()

    def test_invalid_string_rejected(self):
        ok, msg = self.fractions.check_answer("abc", "1/2")
        assert not ok
        assert msg



class TestFractionsGenerateQuestion:
    def setup_method(self):
        self.fractions = Fractions()

    def test_returns_question_and_answer(self):
        q, a = self.fractions.generate_question()
        assert "=" in q
        assert a

    def test_answer_is_valid_fraction_or_int(self):
        from fractions import Fraction
        for _ in range(20):
            _, a = self.fractions.generate_question()
            # should parse without error
            Fraction(a)

    @pytest.mark.parametrize("op_filter", ["add", "sub", "mul", "div"])
    def test_question_contains_expected_operator(self, op_filter):
        op_map = {"add": "+", "sub": "-", "mul": "×", "div": "÷"}
        q, _ = self.fractions.generate_question({"operation": op_filter})
        assert op_map[op_filter] in q



class TestOperationCheckAnswer:
    def setup_method(self):
        self.ops = Operation()

    def test_correct_integer(self):
        ok, _ = self.ops.check_answer("7", "7")
        assert ok

    def test_wrong_integer(self):
        ok, _ = self.ops.check_answer("5", "7")
        assert not ok

    def test_empty_answer(self):
        ok, msg = self.ops.check_answer("", "7")
        assert not ok
        assert msg

    def test_non_integer_rejected(self):
        ok, msg = self.ops.check_answer("1/2", "7")
        assert not ok
        assert msg



class TestTokenToInt:
    def test_plain_number(self):
        assert token_to_int("12") == 12

    def test_with_parentheses(self):
        assert token_to_int("(5)") == 5

    def test_empty_returns_none(self):
        assert token_to_int("") is None

    def test_fraction_string_returns_none(self):
        assert token_to_int("1/2") is None

    def test_text_returns_none(self):
        assert token_to_int("abc") is None



class TestMathSubject:
    def test_has_two_topics(self):
        assert len(Math.topics) == 2

    def test_topic_names(self):
        names = {t.name for t in Math.topics}
        assert names == {"Fractions", "Operations"}
