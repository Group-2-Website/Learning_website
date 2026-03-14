from __future__ import annotations

from models.subject import Subject
from models.topic import Topic


class GermanEnglish(Topic):
    name = "German-English"

class Language(Subject):
    name = "Language"
    url_slug = "language"
    topics: list[Topic] = [
        GermanEnglish(),
    ]