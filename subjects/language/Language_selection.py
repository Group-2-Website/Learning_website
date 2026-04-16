from __future__ import annotations
import csv
import random
from pathlib import Path
from models.subject import Subject
from models.topic import Topic


class BaseVocabTopic(Topic):
    csv_path = Path("Database/csv/flashcard_words_cleaned.csv")
    source_col: str = ""
    target_col: str = ""
    _cards: list[dict[str, str]] | None = None

    _session_key: tuple[str, str] | None = None  # (topic, direction)
    _session_pool: list[dict[str, str]] = []

    def _load_flashcards(self) -> list[dict[str, str]]:
        if self._cards is not None:
            return self._cards
        with self.csv_path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self._cards = [
            r for r in rows
            if r.get(self.source_col, "").strip() and r.get(self.target_col, "").strip()
        ]
        return self._cards

    def _cards_for_topic(self, selected_topic: str) -> list[dict[str, str]]:
        cards = self._load_flashcards()
        if selected_topic == "all":
            return cards
        filtered = [r for r in cards if r.get("topic", "").strip() == selected_topic]
        return filtered or cards

    def quiz_filter_definitions(self) -> dict[str, list[tuple[str, str]]]:
        topics = sorted({
            row.get("topic", "").strip()
            for row in self._load_flashcards()
            if row.get("topic", "").strip()
        })
        return {
            "translate_from": [
                (self.source_col, f"From {self.source_col.title()} to {self.target_col.title()}"),
                (self.target_col, f"From {self.target_col.title()} to {self.source_col.title()}"),
            ],
            "topic": [("all", "All topics")] + [(t, t) for t in topics],
        }

    def default_quiz_filters(self) -> dict[str, str]:
        return {
            "translate_from": self.source_col,
            "topic": "all",
        }

    def sanitize_quiz_filters(self, selected: dict[str, str]) -> dict[str, str]:
        cleaned = super().sanitize_quiz_filters(selected)
        chosen_topic = cleaned.get("topic", "all")
        cards = self._cards_for_topic(chosen_topic)
        cleaned["number of questions"] = str(len(cards))
        return cleaned

    def generate_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        effective = self.sanitize_quiz_filters(filters or {})
        direction = effective["translate_from"]
        selected_topic = effective["topic"]

        key = (selected_topic, direction)
        if self._session_key != key or not self._session_pool:
            self._session_key = key
            self._session_pool = self._cards_for_topic(selected_topic).copy()
            random.shuffle(self._session_pool)

        entry = self._session_pool.pop()

        word_type = entry.get("type", "").strip()
        type_suffix = f' ({word_type})' if word_type else ""

        if direction == self.source_col:
            question = f'Translate: {entry[self.source_col]}{type_suffix}'
            answer = entry[self.target_col]
        else:
            question = f'Translate: {entry[self.target_col]}{type_suffix}'
            answer = entry[self.source_col]
        return question, answer

    def check_answer(self, user: str, correct: str) -> tuple[bool, str]:
        if not user.strip():
            return False, "Please enter an answer."
        return user.strip() == correct.strip(), ""


class GermanEnglish(BaseVocabTopic):
    name = "German-English"
    source_col = "german"
    target_col = "english"

    def page_background_image(self) -> str:
        return "/images/Alphabet.png"


class FrenchEnglish(BaseVocabTopic):
    name = "French-English"
    source_col = "french"
    target_col = "english"

    def page_background_image(self) -> str:
        return "/images/Alphabet.png"


class Language(Subject):
    name = "Language"
    url_slug = "language"
    icon = "/images/icons/stack-of-books.svg"
    topics: list[Topic] = [GermanEnglish(), FrenchEnglish()]

    def page_background_image(self) -> str:
        return "/images/Alphabet.png"
