from __future__ import annotations
from dataclasses import dataclass


@dataclass
class VocabCard:
    """A single vocabulary flashcard loaded from the dictionary database."""
    english: str = ""
    german: str = ""
    article: str = ""
    meanings: str = ""
    word_type: str = ""
    topic: str = ""
