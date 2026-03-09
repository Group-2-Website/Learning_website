from __future__ import annotations

from models.topic import Topic


class Subject:
    """Base class for a subject (e.g. Math, Science, Language)."""
    name: str = ""
    url_slug: str = ""
    topics: list[Topic] = []
