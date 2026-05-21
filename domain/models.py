"""Domain and ORM models.

We use SQLModel to map domain objects to a SQLite database.

Tables:
- DictionaryWord: Language learning vocabulary (English, German, French)
- MathSubject: Lookup table for math subjects (operations, fractions)
- MathContent: Math learning content (questions, explanations, examples)
- ScienceSubject: Lookup table for science subjects (biology, geography)
- ScienceQuiz: Science quiz questions (multiple choice)
"""

from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class DictionaryWord(SQLModel, table=True):
    __tablename__ = "dictionary_words"

    id: Optional[int] = Field(default=None, primary_key=True)
    english: Optional[str] = None
    german: Optional[str] = None
    article_german: Optional[str] = None
    french: Optional[str] = None
    article_french: Optional[str] = None
    meanings: Optional[str] = None
    word_type: Optional[str] = None
    topic: Optional[str] = None


class MathSubject(SQLModel, table=True):
    __tablename__ = "math_subject"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    # Relationships
    contents: list["MathContent"] = Relationship(
        back_populates="subject",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class MathContent(SQLModel, table=True):
    __tablename__ = "math_content"

    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="math_subject.id")
    
    # Content fields
    content_type: Optional[str] = None
    topic: Optional[str] = None
    item_type: Optional[str] = None
    title: Optional[str] = None
    explanation: Optional[str] = None
    expression: Optional[str] = None
    answer: Optional[str] = None
    image: Optional[str] = None

    # Relationships
    subject: "MathSubject" = Relationship(back_populates="contents")


class ScienceSubject(SQLModel, table=True):
    __tablename__ = "science_subject"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    # Relationships
    quizzes: list["ScienceQuiz"] = Relationship(
        back_populates="subject",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class ScienceQuiz(SQLModel, table=True):
    __tablename__ = "science_quiz"

    id: Optional[int] = Field(default=None, primary_key=True)
    subject_id: int = Field(foreign_key="science_subject.id")
    source: str
    question: str
    option_a: str
    option_b: str
    option_c: str
    correct_answer: str

    # Relationships
    subject: "ScienceSubject" = Relationship(back_populates="quizzes")
