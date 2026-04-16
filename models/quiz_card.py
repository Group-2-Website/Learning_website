from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class QuizCard:
    question: str = ""
    options: list[str] = field(default_factory=list)
    correct_answer: str = ""
    topic: str = ""
    audio_url: str = ""
    type_hint: str = ""

