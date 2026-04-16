from __future__ import annotations
from dataclasses import dataclass


@dataclass
class LearningStep:
    title: str = ""
    image: str = ""
    main_text: str = ""
    secondary_text: str = ""
    hint_text: str = ""
    audio_url: str = ""


# Keep the old name available for backwards compatibility.
LearningCard = LearningStep
