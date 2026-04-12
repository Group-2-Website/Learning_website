from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class QuizCard:
    """A single multiple-choice quiz question.

    *question*        – the question text (always shown).
    *options*         – list of answer choices (e.g. 3 options for MC).
    *correct_answer*  – the correct answer string.
    *topic*           – optional topic tag for filtering.
    """
    question: str = ""
    options: list[str] = field(default_factory=list)
    correct_answer: str = ""
    topic: str = ""

