from subjects.math.mathematics import Fractions, Operation, Math


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


class TestFractionsGenerateQuestion:
    def setup_method(self):
        self.fractions = Fractions()

    def test_returns_question_and_answer(self):
        q, a = self.fractions.generate_question()
        assert "=" in q
        assert a  # non-empty answer


class TestOperationCheckAnswer:
    def setup_method(self):
        self.ops = Operation()

    def test_correct_integer(self):
        ok, _ = self.ops.check_answer("7", "7")
        assert ok

    def test_wrong_integer(self):
        ok, _ = self.ops.check_answer("5", "7")
        assert not ok


class TestMathSubject:
    def test_has_two_topics(self):
        assert len(Math.topics) == 2

    def test_topic_names(self):
        names = {t.name for t in Math.topics}
        assert names == {"Fractions", "Operations"}
