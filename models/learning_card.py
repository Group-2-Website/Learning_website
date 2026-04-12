from __future__ import annotations
from dataclasses import dataclass


@dataclass
class LearningStep:
    """A single step in a topic's learning sequence.

    *main_text* is the primary content (always shown).
    *secondary_text* and *hint_text* are optional supporting paragraphs.
    """
    title: str = ""
    image: str = ""
    main_text: str = ""
    secondary_text: str = ""
    hint_text: str = ""


# Keep the old name available for backwards compatibility.
LearningCard = LearningStep
