from __future__ import annotations

import re

from database.dao import MathContentDAO
from core.learning_card import LearningStep
from core.subject import Subject
from core.topic import Topic, FilterOption, FilterDefinition

_VALID_SUBJECTS = {"operations", "fractions"}


def load_steps_from_db(
    subject_name: str,
    topic_name: str | None = None,
) -> list[LearningStep]:

    if subject_name.lower() not in _VALID_SUBJECTS:
        print(f"[DEBUG] Unknown subject: {subject_name}")
        return []

    try:
        rows = MathContentDAO().list_steps(subject_name, topic_name)
    except Exception as e:
        print(f"[DEBUG] DB error: {e}")
        return []

    return [
        LearningStep(
            title=row.title or "",
            image=row.image or "",
            main_text=row.explanation or "",
            secondary_text=row.expression or "",
            hint_text=row.answer or "",
        )
        for row in rows
    ]





def parse_binary_expression(expression: str) -> tuple[str, str, str] | None:
    """Parse expressions like '2/3 + 1/3', '6 / 2'."""
    token = r"[-+]?\(?\d+(?:/\d+)?\)?"
    match = re.match(rf"^\s*({token})\s*([+\-*/×÷−])\s*({token})\s*$", expression or "")
    if not match:
        return None
    left, op, right = match.groups()
    op_normalized = {"*": "×", "/": "÷", "-": "−"}.get(op, op)
    return left.strip(), op_normalized, right.strip()


# Shared operation/difficulty filter data used by all math topics
OPERATION_GROUPS: dict[str, list[str]] = {
    "all": ["+", "-", "×", "÷"],
    "add_sub": ["+", "-"],
    "mul_div": ["×", "÷"],
    "add": ["+"],
    "sub": ["-"],
    "mul": ["×"],
    "div": ["÷"],
}

_COMMON_OPERATION_FILTER: list[FilterOption] = [
    FilterOption("all", "All operations"),
    FilterOption("add_sub", "Addition + Subtraction"),
    FilterOption("mul_div", "Multiplication + Division"),
    FilterOption("add", "Addition only"),
    FilterOption("sub", "Subtraction only"),
    FilterOption("mul", "Multiplication only"),
    FilterOption("div", "Division only"),
]

_COMMON_DIFFICULTY_FILTER: list[FilterOption] = [
    FilterOption("mixed", "Mixed"),
    FilterOption("easy", "Easy"),
    FilterOption("medium", "Medium"),
    FilterOption("hard", "Hard"),
]

_COMMON_QUESTION_COUNT_FILTER: list[FilterOption] = [
    FilterOption(str(n), f"{n} questions") for n in [5, 10, 15, 20]
]


class MathTopic(Topic):
    """Shared base for Math topics: provides common operation/difficulty filters."""

    def quiz_filter_definitions(self) -> list[FilterDefinition]:
        return [
            FilterDefinition("operation", _COMMON_OPERATION_FILTER, default="all"),
            FilterDefinition("difficulty", _COMMON_DIFFICULTY_FILTER, default="mixed"),
            FilterDefinition("number of questions", _COMMON_QUESTION_COUNT_FILTER, default="10"),
        ]


from subjects.math.operations import Operation
from subjects.math.fraction_topic import Fractions


class Math(Subject):
    name: str = "Math"
    url_slug: str = "math"
    icon: str = "/images/icons/notebook.svg"
    topics: list[Topic] = [
        Operation(),
        Fractions(),

    ]

    def page_background_image(self) -> str:
        return "/images/operation.jpg"


