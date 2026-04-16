from __future__ import annotations

from models.learning_card import LearningStep
from models.quiz_card import QuizCard


class Topic:
    """Base class for a single topic within a subject (e.g. Fractions)."""

    name: str = ""
    has_learning: bool = True
    has_painting: bool = False
    quiz_mode: str = "text"
    quiz_source: str = "logic"
    learn_subtitle: str = ""

    def get_question(self, filters: dict[str, str] | None = None) -> QuizCard:
        """Return a QuizCard for text-entry topics."""
        if self.quiz_source == "database":
            card = self._load_question_from_db(filters)
            if card is None:
                return QuizCard(question="No question available.", correct_answer="N/A", topic=self.name)
            return card
        question, answer = self.generate_question(filters)
        return QuizCard(question=question, correct_answer=answer, topic=self.name)

    def get_mc_question(self, filters: dict[str, str] | None = None) -> QuizCard:
        """Return a QuizCard for multiple-choice topics."""
        if self.quiz_source == "database":
            card = self._load_question_from_db(filters)
            if card is None:
                return QuizCard(question="No question available.", correct_answer="N/A", topic=self.name)
            return card
        question, options, answer = self.generate_mc_question(filters)
        return QuizCard(question=question, options=options, correct_answer=answer, topic=self.name)

    def generate_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        """Return ``(question_text, correct_answer)`` for logic-backed topics."""
        raise NotImplementedError

    def generate_mc_question(self, filters: dict[str, str] | None = None) -> tuple[str, list[str], str]:
        """Return ``(question_text, [options], correct_answer)``."""
        question, answer = self.generate_question(filters)
        return question, [], answer

    def _load_question_from_db(self, filters: dict[str, str] | None = None) -> QuizCard | None:
        """Return a QuizCard for database-backed topics."""
        raise NotImplementedError(
            f"{self.__class__.__name__} has quiz_source='database' "
            f"but does not override _load_question_from_db()"
        )

    def quiz_filter_definitions(self) -> dict[str, list[tuple[str, str]]]:
        return {}

    def default_quiz_filters(self) -> dict[str, str]:
        return {}

    def sanitize_quiz_filters(self, selected: dict[str, str]) -> dict[str, str]:
        definitions = self.quiz_filter_definitions()
        defaults = self.default_quiz_filters()
        cleaned: dict[str, str] = {}
        for filter_name, options in definitions.items():
            valid_values = {value for value, _ in options}
            fallback = defaults.get(filter_name, options[0][0])
            value = selected.get(filter_name, fallback)
            cleaned[filter_name] = value if value in valid_values else fallback
        return cleaned

    def learning_steps(self) -> list[LearningStep]:
        return []

    def learn_page_subtitle(self) -> str:
        return self.learn_subtitle or f"Explore and learn about {self.name}!"

    def paint_page_subtitle(self) -> str:
        return f"Draw your understanding of {self.name}!"

    def step_visual_html(self, step_index: int) -> str:
        images = getattr(self, "_step_images", [])
        if step_index < len(images) and images[step_index]:
            src = f"/images/icons/{images[step_index]}"
            return (
                f'<div style="display:flex;justify-content:center;margin:12px 0;">'
                f'<img src="{src}" alt="" style="max-width:500px;max-height:150px;" />'
                f"</div>"
            )
        return ""

    def question_visual_html(self, question: str) -> str:
        return ""

    def paint_visual_html(self) -> str:
        return ""

    def paint_body_html(self) -> str:
        return ""

    def page_background_image(self) -> str:
        return ""

    def check_answer(self, user: str, correct: str) -> tuple[bool, str]:
        if not user.strip():
            return False, "Please enter an answer."
        return user.strip().lower() == correct.strip().lower(), ""
