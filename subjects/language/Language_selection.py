from __future__ import annotations
import random
from urllib.parse import quote

from models.subject import Subject
from models.topic import Topic, FilterOption, FilterDefinition
from models.quiz_card import QuizCard
from models.learning_card import LearningStep
from Database.Learning import DictionaryWord, Session


class BaseVocabTopic(Topic):
    source_col: str = ""
    target_col: str = ""
    quiz_source: str = "database"
    article_col: str = ""          # e.g. "article_german", "article_french"
    learn_topic_filter: str = ""   # DB topic to filter learning cards by
    learn_subtitle: str = "20 nouns with their articles and meanings"
    tts_lang: str = ""             # gTTS language code, e.g. "de", "fr"
    learn_limit: int = 20          # max number of learning steps to show

    def __init__(self) -> None:
        self._session_key: tuple | None = None
        self._session_pool: list[DictionaryWord] = []
        self._last_word_type: str = ""
        self._last_direction: str = ""
        self._last_quiz_type: str = "translate"

    # ── helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _load_words(selected_topic: str) -> list[DictionaryWord]:
        session = Session()
        try:
            query = session.query(DictionaryWord)
            if selected_topic and selected_topic != "all":
                query = query.filter(DictionaryWord.topic == selected_topic)
            rows = query.all()
            session.expunge_all()
            return rows
        finally:
            session.close()

    def _build_audio_url(self, text: str) -> str:
        """Return a /api/tts URL for *text* using this topic's tts_lang."""
        return self._build_audio_url_for_lang(text, self.tts_lang)

    def _build_audio_url_for_lang(self, text: str, lang: str) -> str:
        """Return a /api/tts URL for *text* in the given *lang*, or '' if empty."""
        if not lang or not text:
            return ""
        return f"/api/tts?text={quote(text)}&lang={lang}"


    # ── learning steps ───────────────────────────────────────────────

    def learning_steps(self) -> list[LearningStep]:
        """Return noun learning steps with article + word → English meaning and audio."""
        session = Session()
        try:
            query = (
                session.query(DictionaryWord)
                .filter(
                    DictionaryWord.word_type == "noun",
                    DictionaryWord.meanings.isnot(None),
                    DictionaryWord.meanings != "",
                )
            )
            if self.learn_topic_filter:
                query = query.filter(DictionaryWord.topic == self.learn_topic_filter)
            nouns = query.order_by(DictionaryWord.id).limit(self.learn_limit).all()
            session.expunge_all()
        finally:
            session.close()

        steps: list[LearningStep] = []
        for word in nouns:
            article = (getattr(word, self.article_col, "") or "").strip()
            foreign_word = (getattr(word, self.source_col, "") or "").strip()
            meanings = (word.meanings or "").strip()
            word_type = (word.word_type or "").strip()

            if article:
                title = f"{article.capitalize()} {foreign_word.capitalize()}"
            else:
                title = foreign_word.capitalize()

            # Build the pronunciation audio URL for the foreign word (with article)
            if article and article.endswith("'"):
                # French elision: l' + effort → "l'effort" (no space)
                spoken_text = f"{article}{foreign_word}"
            elif article:
                spoken_text = f"{article} {foreign_word}"
            else:
                spoken_text = foreign_word
            audio_url = self._build_audio_url(spoken_text)

            main_text = word_type if word_type else ""
            secondary = f"Meaning: {meanings}" if meanings else ""

            steps.append(LearningStep(
                title=title,
                main_text=main_text,
                secondary_text=secondary,
                audio_url=audio_url,
            ))

        return steps if steps else [LearningStep(title="No nouns found in database.")]

    def learn_page_subtitle(self) -> str:
        return f"Let's learn about {self.learn_topic_filter}!"

    @staticmethod
    def _load_topics() -> list[str]:
        session = Session()
        try:
            rows = (
                session.query(DictionaryWord.topic)
                .filter(DictionaryWord.topic.isnot(None), DictionaryWord.topic != "")
                .distinct()
                .all()
            )
            return sorted(t[0] for t in rows)
        finally:
            session.close()

    def learn_filter_definitions(self) -> list[FilterDefinition]:
        topics = self._load_topics()
        return [
            FilterDefinition(
                "topic",
                [FilterOption(t, t) for t in topics],
                default=self.learn_topic_filter or "",
            ),
        ]

    def apply_learn_filters(self, filters: dict[str, str]) -> None:
        topic_val = filters.get("topic", "")
        if topic_val:
            self.learn_topic_filter = topic_val

    def quiz_filter_definitions(self) -> list[FilterDefinition]:
        topics = self._load_topics()
        return [
            FilterDefinition(
                "quiz_type",
                [
                    FilterOption("translate", "Translate words"),
                    FilterOption("article", "Choose the correct Article"),
                ],
                default="translate",
            ),
            FilterDefinition(
                "translate_from",
                [
                    FilterOption(self.source_col, f"From {self.source_col.title()} to {self.target_col.title()}"),
                    FilterOption(self.target_col, f"From {self.target_col.title()} to {self.source_col.title()}"),
                ],
                default=self.source_col,
            ),
            FilterDefinition(
                "topic",
                [FilterOption("all", "All topics")] + [FilterOption(t, t) for t in topics],
                default="all",
            ),
        ]

    def sanitize_quiz_filters(self, selected: dict[str, str]) -> dict[str, str]:
        cleaned = super().sanitize_quiz_filters(selected)
        chosen_topic = cleaned.get("topic", "all")
        words = self._load_words(chosen_topic)
        if cleaned.get("quiz_type") == "article":
            words = [w for w in words if (w.word_type or "").strip().lower() == "noun"]
        cleaned["number of questions"] = str(len(words))
        return cleaned

    def _load_question_from_db(self, filters: dict[str, str] | None = None) -> QuizCard:
        effective = self.sanitize_quiz_filters(filters or {})
        quiz_type = effective.get("quiz_type", "translate")
        direction = effective["translate_from"]
        selected_topic = effective["topic"]

        key = (selected_topic, direction, quiz_type)
        if self._session_key != key or not self._session_pool:
            self._session_key = key
            words = self._load_words(selected_topic)
            if quiz_type == "article":
                # Only nouns have articles
                words = [w for w in words if (w.word_type or "").strip().lower() == "noun"]
            self._session_pool = words.copy()
            random.shuffle(self._session_pool)

        if not self._session_pool:
            return QuizCard(question="No words available.", correct_answer="")

        entry = self._session_pool.pop()

        word_type = (entry.word_type or "").strip()
        self._last_word_type = word_type.lower()
        self._last_direction = direction
        self._last_quiz_type = quiz_type

        # ── Article quiz mode ───────────────────────────────────────
        if quiz_type == "article":
            article = (getattr(entry, self.article_col, "") or "").strip()
            source_word = (getattr(entry, self.source_col, "") or "").strip()
            english_word = (getattr(entry, self.target_col, "") or "").strip()
            audio_url = self._build_audio_url(f"{article} {source_word}" if article else source_word)

            # Determine article options based on language
            if self.source_col == "german":
                options = ["der", "die", "das"]
            else:
                options = ["le", "la", "l'", "les"]

            return QuizCard(
                question=f"Choose the correct Article for:\n{source_word.capitalize()}\n({english_word})",
                correct_answer=article.lower(),
                options=options,
                audio_url=audio_url,
            )

        # ── Normal translate mode ───────────────────────────────────
        type_suffix = f' ({word_type})' if word_type else ""

        source_val = getattr(entry, self.source_col, "") or ""
        target_val = getattr(entry, self.target_col, "") or ""
        article = (getattr(entry, self.article_col, "") or "").strip()
        is_noun = self._last_word_type == "noun"

        if direction == self.source_col:
            # Showing source (e.g. German) → answer in target (e.g. English)
            if is_noun and article:
                question = f'Translate:\n{article} {source_val}'
            else:
                question = f'Translate:\n{source_val}'
            answer = target_val
            spoken = f"{article} {source_val}" if is_noun and article else source_val
            audio_lang = self.tts_lang
        else:
            # Showing target (e.g. English) → answer in source (e.g. German)
            question = f'Translate:\n{target_val}'
            if is_noun and article:
                answer = f"{article} {source_val}"
            else:
                answer = source_val
            spoken = target_val
            audio_lang = "en" if self.target_col == "english" else self.tts_lang

        audio_url = self._build_audio_url_for_lang(spoken, audio_lang)

        return QuizCard(
            question=question,
            correct_answer=answer,
            audio_url=audio_url,
            type_hint=type_suffix,
        )

    def check_answer(self, user: str, correct: str) -> tuple[bool, str]:
        if not user.strip():
            return False, "Please enter an answer."

        user_stripped = user.strip()
        correct_stripped = correct.strip()

        # ── Article quiz: simple case-insensitive match ─────────────
        if self._last_quiz_type == "article":
            return user_stripped.lower() == correct_stripped.lower(), ""

        # ── Translate quiz: accept with or without article ──────────
        # Strip known articles from both user and correct for comparison
        german_articles = {"der", "die", "das"}
        french_articles = {"le", "la", "l'", "les", "un", "une"}
        all_articles = german_articles | french_articles

        def strip_article(text: str) -> str:
            lower = text.lower()
            for art in sorted(all_articles, key=len, reverse=True):
                prefix = art if art.endswith("'") else art + " "
                if lower.startswith(prefix):
                    return text[len(prefix):].strip()
            return text

        user_bare = strip_article(user_stripped)
        correct_bare = strip_article(correct_stripped)

        # When the answer is a German noun, require proper capitalization
        answer_is_german = (
            self._last_direction == self.target_col
            and self.source_col == "german"
        )
        if answer_is_german and self._last_word_type == "noun":
            # Compare bare words (without article)
            words_match = user_bare.lower() == correct_bare.lower()
            # Check capitalization of the bare noun
            capitalized = user_bare[0:1].isupper() if user_bare else False
            if words_match and not capitalized:
                return False, f"Almost! German nouns must be capitalized: {correct_stripped}"
            return words_match and capitalized, ""

        # General case: accept with or without article
        if user_stripped.lower() == correct_stripped.lower():
            return True, ""
        if user_bare.lower() == correct_bare.lower():
            return True, ""
        return False, ""


class GermanEnglish(BaseVocabTopic):
    name = "German-English"
    source_col = "german"
    target_col = "english"
    article_col = "article_german"
    tts_lang = "de"
    learn_topic_filter = "People & Professions"
    learn_subtitle = "Let's learn about People & Professions!"

    def page_background_image(self) -> str:
        return "/images/Alphabet.png"


class FrenchEnglish(BaseVocabTopic):
    name = "French-English"
    source_col = "french"
    target_col = "english"
    article_col = "article_french"
    tts_lang = "fr"
    learn_topic_filter = "Work & Education"
    learn_subtitle = "Let's learn about Work & Education!"

    def page_background_image(self) -> str:
        return "/images/Alphabet.png"


class Language(Subject):
    name = "Language"
    url_slug = "language"
    icon = "/images/icons/stack-of-books.svg"
    topics: list[Topic] = [GermanEnglish(), FrenchEnglish()]

    def page_background_image(self) -> str:
        return "/images/Language.jpg"
