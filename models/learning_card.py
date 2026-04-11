from __future__ import annotations
from dataclasses import dataclass


@dataclass
class LearningCard:
    """A single card in a topic's learning sequence."""
    title: str = ""
    image: str = ""
    paragraph: str = ""
    detail: str = ""
    note: str = ""
