from __future__ import annotations

import re

from sqlalchemy import func

from Database.Learning import Operation as OperationRow, Fraction as FractionRow, Session
from models.learning_card import LearningStep
from models.subject import Subject
from models.topic import Topic, FilterOption, FilterDefinition

_SUBJECT_MODEL_MAP = {
    "operations": OperationRow,
    "fractions": FractionRow,
}


def load_steps_from_db(
    subject_name: str,
    topic_name: str | None = None,
) -> list[LearningStep]:
    """Load learning steps from the dedicated table for *subject_name*.

    *topic_name* optionally filters within that subject.
    """
    model = _SUBJECT_MODEL_MAP.get(subject_name.lower())
    if model is None:
        print(f"[DEBUG] Unknown subject: {subject_name}")
        return []

    session = Session()
    try:
        query = session.query(model)
        if topic_name:
            query = query.filter(
                func.lower(model.topic) == topic_name.lower()
            )
        rows = query.order_by(model.id).all()

        return [
            LearningStep(
                title=getattr(row, "title", "") or "",
                image=getattr(row, "image", "") or "",
                main_text=getattr(row, "explanation", "") or "",
                secondary_text=getattr(row, "expression", "") or "",
                hint_text=getattr(row, "answer", "") or "",
            )
            for row in rows
        ]
    except Exception as e:
        print(f"[DEBUG] DB error: {e}")
        return []
    finally:
        session.close()





def parse_binary_expression(expression: str) -> tuple[str, str, str] | None:
    """Parse expressions like '2/3 + 1/3', '6 / 2'."""
    token = r"[-+]?\(?\d+(?:/\d+)?\)?"
    match = re.match(rf"^\s*({token})\s*([+\-*/×÷−])\s*({token})\s*$", expression or "")
    if not match:
        return None
    left, op, right = match.groups()
    op_normalized = {"*": "×", "/": "÷", "-": "−"}.get(op, op)
    return left.strip(), op_normalized, right.strip()


# ── Shared operation/difficulty filter data used by all math topics ──────────
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
    name = "Math"
    url_slug = "math"
    icon = "/images/icons/notebook.svg"
    topics: list[Topic] = [
        Operation(),
        Fractions(),

    ]

    def page_background_image(self) -> str:
        return "/images/operation.jpg"



