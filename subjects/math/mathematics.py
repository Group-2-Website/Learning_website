from __future__ import annotations

import re

from sqlalchemy import func, inspect

from Database.Learning import Fraction as DBFraction
from Database.Learning import Operation as DBOperation
from Database.Learning import Session
from models.subject import Subject
from models.topic import Topic

_TABLE_MODEL_MAP = {
    "operations": DBOperation,
    "fractions": DBFraction,
}
_TABLE_CANDIDATES = ("operations", "fractions")


def load_steps_from_db(
    topic_name: str | None = None,
    table: str | None = None,
) -> list[dict[str, str]]:
    """Load learning steps from the database via SQLAlchemy."""
    session = Session()
    try:
        model = None
        if table and table in _TABLE_MODEL_MAP:
            model = _TABLE_MODEL_MAP[table]
        else:
            engine = session.get_bind()
            inspector = inspect(engine)
            existing = set(inspector.get_table_names())
            for candidate in _TABLE_CANDIDATES:
                if candidate in existing and candidate in _TABLE_MODEL_MAP:
                    model = _TABLE_MODEL_MAP[candidate]
                    break

        if model is None:
            return []

        query = session.query(model)
        if topic_name:
            query = query.filter(func.lower(model.topic) == topic_name.lower())
        rows = query.order_by(model.id).all()

        if not rows and topic_name:
            rows = session.query(model).order_by(model.id).all()

        columns = [
            "content_type",
            "topic",
            "item_type",
            "title",
            "explanation",
            "expression",
            "answer",
            "image",
        ]
        return [{col: getattr(row, col, "") or "" for col in columns} for row in rows]
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

_COMMON_OPERATION_FILTER: list[tuple[str, str]] = [
    ("all", "All operations"),
    ("add_sub", "Addition + Subtraction"),
    ("mul_div", "Multiplication + Division"),
    ("add", "Addition only"),
    ("sub", "Subtraction only"),
    ("mul", "Multiplication only"),
    ("div", "Division only"),
]

_COMMON_DIFFICULTY_FILTER: list[tuple[str, str]] = [
    ("mixed", "Mixed"),
    ("easy", "Easy"),
    ("medium", "Medium"),
    ("hard", "Hard"),
]

_COMMON_QUESTION_COUNT_FILTER: list[tuple[str, str]] = [
    (str(n), f"{n} questions") for n in [5, 10, 15, 20]
]


class MathTopic(Topic):
    """Shared base for Math topics: provides common operation/difficulty filters."""

    def quiz_filter_definitions(self) -> dict[str, list[tuple[str, str]]]:
        return {
            "operation": _COMMON_OPERATION_FILTER,
            "difficulty": _COMMON_DIFFICULTY_FILTER,
            "number of questions": _COMMON_QUESTION_COUNT_FILTER,
        }

    def default_quiz_filters(self) -> dict[str, str]:
        return {"operation": "all", "difficulty": "mixed", "number of questions": "10"}


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



