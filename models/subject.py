from __future__ import annotations

from models.topic import Topic


class Subject:
    """Base class for a subject (e.g. Math, Science, Language)."""
    name: str = ""
    url_slug: str = ""
    topics: list[Topic] = []

    def page_background_image(self) -> str:
        """Optional: return a URL for a semi-transparent background image on learn/quiz pages."""
        return ""
