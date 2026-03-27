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

class Operation(Base):
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True)
    content_type=Column(String)
    topic = Column(String)
    item_type = Column(String)
    title = Column(String)
    explanation = Column(String)
    expression = Column(String)
    answer = Column(String)
    image = Column(String)
engine = create_engine("sqlite:///learning.db")



Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
def import_dictionary_words():
    session = Session()
    with open("flashcard_words_cleaned.csv", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        for row in reader:

            word = DictionaryWord(
                english=row["english"],
                german=row["german"],
                article=row["article_german"],
                meanings=row["meanings"],
                word_type=row["type"]
            )

            session.add(word)
    session.commit()

    print("dictionary imported")
def import_operations():
    session = Session()

    with open("operations.csv", encoding="utf-8-sig") as file:
     reader = csv.DictReader(file)

     for row in reader:
         operation = Operation(
         content_type=row["content_type"],
         topic=row["topic"],
         item_type=row["item_type"],
         title=row["title"],
         explanation=row["explanation"],
         expression=row["expression"],
         answer=row["answer"],
         image=row["image"]
         )

         session.add(operation)
     session.commit()
     session.close()
     print("operations imported")

if __name__ == "__main__":
 import_dictionary_words()
 import_operations()