from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DictionaryTopic(SQLModel, table=True):
    __tablename__ = "dictionary_topic"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)


class WordType(SQLModel, table=True):
    __tablename__ = "word_type"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)


class Article(SQLModel, table=True):
    """A grammatical article scoped to a language ("de" → der/die/das, "fr" → le/la/l'…)."""

    __tablename__ = "article"
    __table_args__ = (UniqueConstraint("language", "text", name="uq_article_lang_text"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    language: str = Field()   # e.g. "de", "fr"
    text: str


class DictionaryWord(SQLModel, table=True):
    __tablename__ = "dictionary_words"

    id: Optional[int] = Field(default=None, primary_key=True)

    # languages side-by-side and there is no plan to add more languages, so a
    # full Word/Language/Translation split would only add joins for no gain.
    english: Optional[str] = None
    german: Optional[str] = None
    french: Optional[str] = None
    meanings: Optional[str] = None

    # Normalised foreign keys (all nullable: legacy rows / partial data).
    word_type_id: Optional[int] = Field(default=None, foreign_key="word_type.id")
    topic_id: Optional[int] = Field(default=None, foreign_key="dictionary_topic.id")
    article_german_id: Optional[int] = Field(default=None, foreign_key="article.id")
    article_french_id: Optional[int] = Field(default=None, foreign_key="article.id")

    word_type_obj: Optional["WordType"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DictionaryWord.word_type_id"},
    )
    topic_obj: Optional["DictionaryTopic"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DictionaryWord.topic_id"},
    )
    article_german_obj: Optional["Article"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DictionaryWord.article_german_id"},
    )
    article_french_obj: Optional["Article"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "DictionaryWord.article_french_id"},
    )

# Math


class MathSubject(SQLModel, table=True):
    __tablename__ = "math_subject"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    topics: list["MathTopic"] = Relationship(
        back_populates="subject",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    contents: list["MathContent"] = Relationship(
        back_populates="subject",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class MathTopic(SQLModel, table=True):
    """A topic within a math subject (e.g. ``addition`` under ``operations``)."""

    __tablename__ = "math_topic"
    __table_args__ = (UniqueConstraint("subject_id", "name", name="uq_math_topic_subject_name"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="math_subject.id")
    name: str = Field()

    subject: "MathSubject" = Relationship(back_populates="topics")
    contents: list["MathContent"] = Relationship(
        back_populates="topic_obj",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class MathContent(SQLModel, table=True):
    __tablename__ = "math_content"

    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="math_subject.id")
    topic_id: Optional[int] = Field(default=None, foreign_key="math_topic.id")

    # Free-form content fields. ``content_type`` / ``item_type`` are kept as
    # strings — they only take ~3 distinct values
    content_type: Optional[str] = None
    item_type: Optional[str] = None
    title: Optional[str] = None
    explanation: Optional[str] = None
    expression: Optional[str] = None
    answer: Optional[str] = None
    image: Optional[str] = None

    subject: "MathSubject" = Relationship(back_populates="contents")
    topic_obj: Optional["MathTopic"] = Relationship(back_populates="contents")

# Science


class ScienceSubject(SQLModel, table=True):
    __tablename__ = "science_subject"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    topics: list["ScienceTopicRow"] = Relationship(
        back_populates="subject",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    quizzes: list["ScienceQuiz"] = Relationship(
        back_populates="subject",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ScienceTopicRow(SQLModel, table=True):
    """A grouping of science quiz questions (e.g. ``animals`` under ``biology``).

    Named ``ScienceTopicRow`` to avoid colliding with the UI-level
    ``subjects.science.science.ScienceTopic`` class.
    """

    __tablename__ = "science_topic"
    __table_args__ = (UniqueConstraint("subject_id", "name", name="uq_science_topic_subject_name"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="science_subject.id")
    name: str = Field()

    subject: "ScienceSubject" = Relationship(back_populates="topics")
    quizzes: list["ScienceQuiz"] = Relationship(
        back_populates="topic_obj",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ScienceQuiz(SQLModel, table=True):
    __tablename__ = "science_quiz"

    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="science_subject.id")
    topic_id: int = Field(foreign_key="science_topic.id")
    question: str

    subject: "ScienceSubject" = Relationship(back_populates="quizzes")
    topic_obj: "ScienceTopicRow" = Relationship(back_populates="quizzes")
    options: list["ScienceQuizOption"] = Relationship(
        back_populates="quiz",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "order_by": "ScienceQuizOption.label",
        },
    )

class ScienceQuizOption(SQLModel, table=True):
    __tablename__ = "science_quiz_option"
    __table_args__ = (UniqueConstraint("quiz_id", "label", name="uq_science_option_quiz_label"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="science_quiz.id")
    label: str  # "A", "B", "C"
    text: str
    is_correct: bool = False

    quiz: "ScienceQuiz" = Relationship(back_populates="options")


# Quiz attempt history


class QuizSubject(SQLModel, table=True):
    """Lookup table: distinct subject names referenced by quiz attempts."""
    __tablename__ = "quiz_subject"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    topics: list["QuizTopic"] = Relationship(
        back_populates="subject",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class QuizTopic(SQLModel, table=True):
    """Lookup table: a topic within a subject (unique per subject)."""
    __tablename__ = "quiz_topic"
    __table_args__ = (
        UniqueConstraint("subject_id", "name", name="uq_quiz_topic_subject_name"),
        {"sqlite_autoincrement": True},
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="quiz_subject.id")
    name: str = Field()

    subject: "QuizSubject" = Relationship(back_populates="topics")
    attempts: list["QuizAttempt"] = Relationship(
        back_populates="topic",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class QuizAttempt(SQLModel, table=True):
    """A finished quiz session: stores score, mistakes and the filters used.

    Only ``topic_id`` is stored — the subject is derivable through
    ``topic.subject`` (3NF: no transitive dependencies).
    """

    __tablename__ = "quiz_attempt"

    id: Optional[int] = Field(default=None, primary_key=True)
    topic_id: int = Field(foreign_key="quiz_topic.id")
    score: int = 0
    attempts: int = 0
    hints_used: int = 0
    filters: Optional[str] = None  # JSON-encoded filter selections
    created_at: datetime = Field(default_factory=_utcnow)

    topic: "QuizTopic" = Relationship(back_populates="attempts")
