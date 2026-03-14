from __future__ import annotations


class Topic:
    """Base class for a single topic within a subject (e.g. Fractions)."""
    name: str = ""
    icon: str = ""
    has_learning: bool = True
    has_painting: bool = False

    def generate_question(self) -> tuple[str, str]:
        """Return (question_text, correct_answer) as strings."""
        raise NotImplementedError

    def learning_steps(self) -> list[tuple[str, str]]:
        """Return a list of (title, explanation) tuples."""
        return []

    def learn_page_subtitle(self) -> str:
        """Subtitle shown at the top of the learn page."""
        return f"Step-by-step guide to {self.name}."

    def paint_page_subtitle(self) -> str:
        """Subtitle shown at the top of the draw page."""
        return f"Draw your understanding of {self.name}!"

    def step_visual_html(self, step_index: int) -> str:
        """Optional: return inline HTML/SVG shown next to each learning step."""
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
