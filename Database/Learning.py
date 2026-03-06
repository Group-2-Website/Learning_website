import csv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class DictionaryWord(Base):
    __tablename__ = "dictionary_words"

    id = Column(Integer, primary_key=True)
    english = Column(String)
    german = Column(String)
    article = Column(String)
    meanings = Column(String)
    word_type = Column(String)
engine = create_engine("sqlite:///learning.db")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


with open("flashcard_words_cleaned.csv", encoding="utf-8-sig") as file:

    reader = csv.DictReader(file)

    for row in reader:

        word = DictionaryWord(
            english=row["english"],
            german=row["german"],
            article=row["article"],
            meanings=row["meanings"],
            word_type=row["type"]
        )

        session.add(word)


session.commit()

print("dictionary imported")