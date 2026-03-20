from __future__ import annotations

from models.subject import Subject
from models.topic import Topic


class GermanEnglish(Topic):
    name = "German-English"

    def page_background_image(self) -> str:
        return "/images/Alphabet.png"

class FrenchEnglish(Topic):
    name = "French-English"

    def page_background_image(self) -> str:
        return "/images/Alphabet.png"


class Language(Subject):
    name = "Language"
    url_slug = "language"
    icon = "/images/icons/stack-of-books.svg"
    topics: list[Topic] = [
        GermanEnglish(),
        FrenchEnglish(),
    ]
    def page_background_image(self) -> str:
        return "/images/Alphabet.png"
