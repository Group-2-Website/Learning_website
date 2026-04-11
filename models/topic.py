from __future__ import annotations
from models.learning_card import LearningCard


class Topic:
    """Base class for a single topic within a subject (e.g. Fractions)."""
    name: str = ""
    has_learning: bool = True
    has_painting: bool = False

    def generate_question(
        self, filters: dict[str, str] | None = None
    ) -> tuple[str, str] | tuple[str, str, list[str]]:
        """Return (question_text, correct_answer) or include answer options for multiple-choice topics."""
        raise NotImplementedError

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

    def learning_cards(self) -> list[LearningCard]:
        """Return a list of LearningCard objects."""
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
