from __future__ import annotations

from abc import ABC, abstractmethod

from models.topic import Topic


class Subject(ABC):
    """Base class for a subject (e.g. Math, Science, Language)."""
    name: str = ""
    url_slug: str = ""
    icon: str = ""

    topics: list[Topic] = []

    @abstractmethod
    def page_background_image(self) -> str:
        """Return a URL for a semi-transparent background image on learn/quiz pages."""
        ...
