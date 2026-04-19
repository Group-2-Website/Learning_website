from __future__ import annotations
import random
from collections import defaultdict
from html import escape
from urllib.parse import quote_plus

from Database.Learning import DictionaryWord, Session
from models.learning_card import LearningStep
from models.quiz_card import QuizCard
from models.subject import Subject
from models.topic import Topic


class BaseVocabTopic(Topic):
    source_col: str = ""
    target_col: str = ""
    _cards: list[dict[str, str]] | None = None

    _session_key: tuple[str, str] | None = None  # (topic, direction)
    _session_pool: list[dict[str, str]] = []

    def _load_flashcards(self) -> list[dict[str, str]]:
        if self._cards is not None:
            return self._cards

        session = Session()
        try:
            rows = session.query(DictionaryWord).all()
        finally:
            session.close()

        cards: list[dict[str, str]] = []
        for row in rows:
            entry = {
                "english": (row.english or "").strip(),
                "german": (row.german or "").strip(),
                "french": (row.french or "").strip(),
                "article_german": (row.article_german or "").strip(),
                "article_french": (row.article_french or "").strip(),
                "type": (row.word_type or "").strip(),
                "topic": (row.topic or "").strip(),
            }
            if entry.get(self.source_col, "") and entry.get(self.target_col, ""):
                cards.append(entry)

        self._cards = cards
        return self._cards

    def _cards_for_topic(self, selected_topic: str) -> list[dict[str, str]]:
        cards = self._load_flashcards()
        if selected_topic == "all":
            return cards
        filtered = [r for r in cards if r.get("topic", "") == selected_topic]
        return filtered or cards

    @staticmethod
    def _is_noun(entry: dict[str, str]) -> bool:
        t = entry.get("type", "").strip().lower()
        return t in {"noun", "nomen", "substantiv"}

    @staticmethod
    def _article_key_for_lang(lang: str) -> str:
        return f"article_{lang}"

    def _term_with_article_if_needed(self, entry: dict[str, str], lang: str) -> str:
        word = entry.get(lang, "").strip()
        if not word or not self._is_noun(entry):
            return word

        article = entry.get(self._article_key_for_lang(lang), "").strip()
        if not article:
            return word

        # Avoid duplicate article if the word already starts with it.
        w = word.lower()
        a = article.lower()
        if w.startswith(a + " "):
            return word
        return f"{article} {word}"

    @staticmethod
    def _normalize_answer(text: str) -> str:
        return " ".join(text.strip().lower().split())

    @staticmethod
    def _tts_lang_for_col(col: str) -> str:
        mapping = {
            "german": "de",
            "french": "fr",
            "english": "en",
        }
        return mapping.get(col, "en")

    def _tts_url(self, text: str, lang_col: str) -> str:
        cleaned = text.strip()
        if not cleaned:
            return ""
        lang = self._tts_lang_for_col(lang_col)
        return f"/api/tts?text={quote_plus(cleaned)}&lang={quote_plus(lang)}"

    @staticmethod
    def _inline_audio_button(audio_url: str, label: str = "Listen") -> str:
        if not audio_url:
            return ""
        safe_url = escape(audio_url, quote=True)
        safe_label = escape(label)
        return (
            f'<button class="audio-btn" data-audio-url="{safe_url}" '
            f'style="padding:4px 10px;border:none;border-radius:999px;'
            f'background:#f3e8ff;color:#4A3F55;font-weight:700;cursor:pointer;">'
            f'{safe_label}</button>'
        )

    def quiz_filter_definitions(self) -> dict[str, list[tuple[str, str]]]:
        topics = sorted(
            {
                row.get("topic", "").strip()
                for row in self._load_flashcards()
                if row.get("topic", "").strip()
            }
        )
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

    def _next_vocab_round(self, filters: dict[str, str]) -> tuple[str, str, str, str]:
        effective = self.sanitize_quiz_filters(filters or {})
        direction = effective["translate_from"]
        selected_topic = effective["topic"]

        key = (selected_topic, direction)
        if self._session_key != key or not self._session_pool:
            self._session_key = key
            self._session_pool = self._cards_for_topic(selected_topic).copy()
            random.shuffle(self._session_pool)

        if not self._session_pool:
            return "No words available.", "N/A", "", self.source_col

        entry = self._session_pool.pop()
        word_type = entry.get("type", "").strip()
        type_suffix = f" ({word_type})" if word_type else ""

        if direction == self.source_col:
            prompt_term = self._term_with_article_if_needed(entry, self.source_col)
            answer = self._term_with_article_if_needed(entry, self.target_col)
            prompt_lang_col = self.source_col
        else:
            prompt_term = self._term_with_article_if_needed(entry, self.target_col)
            answer = self._term_with_article_if_needed(entry, self.source_col)
            prompt_lang_col = self.target_col

        question = f"Translate: {prompt_term}{type_suffix}"
        return question, answer, prompt_term, prompt_lang_col

    def generate_question(self, filters: dict[str, str] | None = None) -> tuple[str, str]:
        question, answer, _, _ = self._next_vocab_round(filters or {})
        return question, answer

    def get_question(self, filters: dict[str, str] | None = None) -> QuizCard:
        question, answer, prompt_term, prompt_lang_col = self._next_vocab_round(filters or {})
        return QuizCard(
            question=question,
            correct_answer=answer,
            topic=self.name,
            audio_url=self._tts_url(prompt_term, prompt_lang_col),
        )

    def check_answer(self, user: str, correct: str) -> tuple[bool, str]:
        if not user.strip():
            return False, "Please enter an answer."

        u = self._normalize_answer(user)
        c = self._normalize_answer(correct)

        if u == c:
            return True, ""

        # If expected answer has article + noun and user typed only noun.
        parts = c.split(" ", 1)
        if len(parts) == 2 and u == parts[1]:
            return False, "Bitte gib bei Nomen auch den Artikel an."

        return False, ""

    # From here it's about Learning
    def _learning_label(self, entry: dict[str, str]) -> str:
        left = self._term_with_article_if_needed(entry, self.source_col)
        right = self._term_with_article_if_needed(entry, self.target_col)
        word_type = (entry.get("type") or "").strip()
        suffix = f" ({word_type})" if word_type else ""
        return f"{left} -> {right}{suffix}"

    def learning_steps(self) -> list[LearningStep]:
        cards = self._load_flashcards()

        # 1) Sort by topic, then alphabetically by source_col
        cards_sorted = sorted(
            cards,
            key=lambda c: (
                (c.get("topic") or "zzz").lower(),
                (c.get(self.source_col) or "").lower(),
            ),
        )

        # 2) Group by topic
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for entry in cards_sorted:
            group = (entry.get("topic") or "General").strip() or "General"
            grouped[group].append(entry)

        # 3) One LearningStep card per topic with a table view
        steps: list[LearningStep] = []
        for topic_name in sorted(grouped.keys(), key=lambda s: s.lower()):
            rows_html = "".join(
                "<tr>"
                f"<td style='padding:8px 10px;border-bottom:1px solid #eee;'>{escape(self._term_with_article_if_needed(e, self.source_col))}</td>"
                f"<td style='padding:8px 10px;border-bottom:1px solid #eee;'>{escape(self._term_with_article_if_needed(e, self.target_col))}</td>"
                f"<td style='padding:8px 10px;border-bottom:1px solid #eee;'>{escape((e.get('type') or '').strip())}</td>"
                f"<td style='padding:8px 10px;border-bottom:1px solid #eee;'>"
                f"<div style='display:flex;gap:6px;flex-wrap:wrap;'>"
                f"{self._inline_audio_button(self._tts_url(self._term_with_article_if_needed(e, self.source_col), self.source_col), label=self._tts_lang_for_col(self.source_col).upper())}"
                f"{self._inline_audio_button(self._tts_url(self._term_with_article_if_needed(e, self.target_col), self.target_col), label=self._tts_lang_for_col(self.target_col).upper())}"
                f"</div>"
                f"</td>"
                "</tr>"
                for e in grouped[topic_name]
            )

            table_html = (
                "<div style='max-height:320px;overflow:auto;width:100%;'>"
                "<table style='width:100%;border-collapse:collapse;font-size:17px;text-align:left;'>"
                "<thead>"
                "<tr style='background:#f6f2ff;'>"
                f"<th style='padding:10px;border-bottom:2px solid #ddd;'>{escape(self.source_col.title())}</th>"
                f"<th style='padding:10px;border-bottom:2px solid #ddd;'>{escape(self.target_col.title())}</th>"
                "<th style='padding:10px;border-bottom:2px solid #ddd;'>Type</th>"
                "<th style='padding:10px;border-bottom:2px solid #ddd;'>Audio</th>"
                "</tr>"
                "</thead>"
                f"<tbody>{rows_html}</tbody>"
                "</table>"
                "</div>"
            )

            steps.append(
                LearningStep(
                    title=f"Topic: {topic_name}",
                    main_text=table_html,
                    secondary_text="",
                    hint_text="",
                )
            )

        return steps


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
