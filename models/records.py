from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class VocabularyWord:
    english: str = ""
    german: str = ""
    french: str = ""
    meanings: str = ""
    topic: str = ""
    word_type: str = ""
    article_german: str = ""
    article_french: str = ""


@dataclass(frozen=True)
class MathLearningEntry:
    title: str = ""
    explanation: str = ""
    expression: str = ""
    answer: str = ""
    image: str = ""
    topic: str = ""


@dataclass(frozen=True)
class ScienceQuestion:
    question: str = ""
    source: str = ""
    options: list[str] = field(default_factory=list)
    correct_answer: str = ""


@dataclass(frozen=True)
class QuizAttemptRecord:
    score: int = 0
    attempts: int = 0
    hints_used: int = 0
    filters: str | None = None
    created_at: datetime | None = None

