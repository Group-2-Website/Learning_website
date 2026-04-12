from __future__ import annotations
from models.learning_card import LearningStep
from models.quiz_card import QuizCard


class Topic:
    """Base class for a single topic within a subject (e.g. Fractions)."""
    name: str = ""
    has_learning: bool = True
    has_painting: bool = False
    quiz_mode: str = "text"  # "text" (type answer) or "multiple_choice" (select from options)
    quiz_source: str = "logic"  # "logic" = generate_question, "database" = _load_question_from_db

    # ── Public quiz entry points (factory dispatch) ─────────────────────

    def get_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        """Single public entry point for obtaining a quiz question.

        Dispatches to ``generate_question`` (code-logic) or
        ``_load_question_from_db`` (database-backed) based on *quiz_source*.
        """
        if self.quiz_source == "database":
            card = self._load_question_from_db(filters)
            return card.question, card.correct_answer
        return self.generate_question(filters)

    def get_mc_question(self, filters: dict[str, str] | None = None) -> tuple[str, list[str], str]:
        """Single public entry point for obtaining a multiple-choice quiz question."""
        if self.quiz_source == "database":
            card = self._load_question_from_db(filters)
            return card.question, card.options, card.correct_answer
        return self.generate_mc_question(filters)

    # ── Override points ─────────────────────────────────────────────────

    def generate_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        """Return (question_text, correct_answer) as strings.

        Override this in logic-based topics (quiz_source="logic").
        """
        raise NotImplementedError

    def generate_mc_question(self, filters: dict[str, str] | None = None) -> tuple[str, list[str], str]:
        """Return (question_text, [option_a, option_b, option_c], correct_answer).

        Only used when ``quiz_mode == "multiple_choice"``.
        Default implementation wraps ``generate_question`` with empty choices.
        """
        q, a = self.generate_question(filters)
        return q, [], a

    def _load_question_from_db(self, filters: dict[str, str] | None = None) -> QuizCard:
        """Load a QuizCard from a topic-specific data source.

        Override this in database-backed topics (quiz_source="database").
        Each topic should query its own dedicated table.
        Must return a ``QuizCard`` instance.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} has quiz_source='database' "
            f"but does not override _load_question_from_db()"
        )

    def quiz_filter_definitions(self) -> dict[str, list[tuple[str, str]]]:
        """Optional quiz filters: {filter_name: [(value, label), ...]} for UI menus."""
        return {}

    def default_quiz_filters(self) -> dict[str, str]:
        """Default selected filter values for this topic."""
        return {}

    def sanitize_quiz_filters(self, selected: dict[str, str]) -> dict[str, str]:
        """Validate and normalize filter selections against quiz_filter_definitions."""
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
        """Return a list of LearningStep objects."""
        return []

    def learn_page_subtitle(self) -> str:
        """Subtitle shown at the top of the learn page."""
        return f"Step-by-step guide to {self.name}."

    def paint_page_subtitle(self) -> str:
        """Subtitle shown at the top of the draw page."""
        return f"Draw your understanding of {self.name}!"

    def step_visual_html(self, step_index: int) -> str:
        """Optional: return inline HTML/SVG shown next to each learning step."""
        images = getattr(self, "_step_images", [])
        if step_index < len(images) and images[step_index]:
            src = f"/images/icons/{images[step_index]}"
            return (
                f'<div style="display:flex;justify-content:center;margin:12px 0;">'
                f'<img src="{src}" alt="" style="max-width:500px;max-height:150px;" />'
                f'</div>'
            )
        return ""

    def question_visual_html(self, question: str) -> str:
        """Optional: return inline HTML/SVG visualising the current quiz question."""
        return ""

    def paint_visual_html(self) -> str:
        """Optional: return inline HTML/SVG shown on the draw page."""
        return ""

    def paint_body_html(self) -> str:
        """Optional: return body-level HTML (e.g. scripts) needed by the draw page."""
        return ""

    def page_background_image(self) -> str:
        """Optional: return a URL for a semi-transparent background image on learn/quiz pages."""
        return ""

    def check_answer(self, user: str, correct: str) -> tuple[bool, str]:
        """Default answer checking: case-insensitive text match with empty-input validation."""
        if not user.strip():
            return False, "Please enter an answer."
        return user.strip().lower() == correct.strip().lower(), ""