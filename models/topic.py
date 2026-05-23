from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from models.learning_card import LearningStep
from models.quiz_card import QuizCard
from Database import dao as dao_module

if TYPE_CHECKING:
    from models.records import QuizAttemptRecord


@dataclass
class FilterOption:
    """A single selectable option inside a filter dropdown."""
    value: str
    label: str


@dataclass
class FilterDefinition:
    """A named filter with its available options and a default selection."""
    name: str
    options: list[FilterOption] = field(default_factory=list)
    default: str = ""

    def __post_init__(self) -> None:
        if not self.default and self.options:
            self.default = self.options[0].value

    @property
    def options_map(self) -> dict[str, str]:
        """Return {value: label} dict suitable for ui.select."""
        return {opt.value: opt.label for opt in self.options}

    @property
    def valid_values(self) -> set[str]:
        return {opt.value for opt in self.options}

    def sanitize(self, value: str | None) -> str:
        """Return *value* if valid, else the default."""
        if value in self.valid_values:
            return value
        return self.default


class Topic:
    """Base class for a single topic within a subject (e.g. Fractions)."""
    name: str = ""
    has_learning: bool = True
    has_painting: bool = False
    quiz_mode: str = "text"  # "text" (type answer) or "multiple_choice" (select from options)
    quiz_source: str = "logic"  # "logic" = generate_question, "database" = _load_question_from_db
    learn_subtitle: str = ""

    def get_question(self, filters: dict[str, str] | None = None) -> QuizCard:
        """Single public entry point for obtaining a quiz question.

        Dispatches to ``generate_question`` (code-logic) or
        ``_load_question_from_db`` (database-backed) based on *quiz_source*.

        Always returns a ``QuizCard`` — never a raw tuple.
        """
        if self.quiz_source == "database":
            card = self._load_question_from_db(filters)
            if card is None:
                return QuizCard(question="No question available.", correct_answer="N/A", topic=self.name)
            return card
        q, a = self.generate_question(filters)
        return QuizCard(question=q, correct_answer=a, topic=self.name)


    # Override hooks (return simple tuples)

    def generate_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        """Return ``(question_text, correct_answer)`` as plain strings.

        Override this in logic-based topics (quiz_source="logic").
        """
        raise NotImplementedError


    def _load_question_from_db(self, filters: dict[str, str] | None = None) -> QuizCard | None:

        raise NotImplementedError(
            f"{self.__class__.__name__} has quiz_source='database' "
            f"but does not override _load_question_from_db()"
        )

    def quiz_filter_definitions(self) -> list[FilterDefinition]:
        """Return filter definitions for the quiz settings page."""
        return []

    def update_filter_visibility(self, selected: dict[str, str], widgets: dict) -> None:
        """Update widget visibility based on current filter selections.
        Override in subclasses for topic-specific visibility rules."""
        pass

    def learn_filter_definitions(self) -> list[FilterDefinition]:
        """Return filter definitions for the learn settings page."""
        return []

    def sanitize_quiz_filters(self, selected: dict[str, str]) -> dict[str, str]:
        """Validate and normalize filter selections against quiz_filter_definitions."""
        cleaned: dict[str, str] = {}
        for fd in self.quiz_filter_definitions():
            cleaned[fd.name] = fd.sanitize(selected.get(fd.name))
        return cleaned

    def get_num_questions(self, filters: dict[str, str]) -> int:
        """Return the number of questions for a quiz session."""

        return int(filters.get("number of questions", 10))

    def record_quiz_attempt(
        self,
        subject_name: str,
        score: int,
        attempts: int,
        hints_used: int = 0,
        filters: dict[str, str] | None = None,
    ) -> None:
        """Persist one completed quiz run for this topic."""

        dao_module.QuizAttemptDAO().record(
            subject=subject_name,
            topic=self.name,
            score=score,
            attempts=attempts,
            hints_used=hints_used,
            filters=filters,
        )

    def list_quiz_attempts(self, subject_name: str, limit: int = 20) -> list["QuizAttemptRecord"]:
        """Return recent quiz attempts for this topic, newest first."""

        return dao_module.QuizAttemptDAO().list_for(
            subject=subject_name,
            topic=self.name,
            limit=limit,
        )


    def apply_learn_filters(self, filters: dict[str, str]) -> None:
        """Apply learn filters before learning_steps() is called."""
        pass

    def learning_steps(self) -> list[LearningStep]:
        """Return a list of LearningStep objects."""
        return []

    def learn_page_subtitle(self) -> str:
        """Subtitle shown at the top of the learn page."""
        return self.learn_subtitle or f"Explore and learn about {self.name}!"

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