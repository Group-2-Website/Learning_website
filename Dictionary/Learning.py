import csv
import sqlite3

# open database
db = sqlite3.connect("learning.db")
db.execute("""
CREATE TABLE IF NOT EXISTS flashcard_words(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    english TEXT,
    german TEXT,
    article TEXT,
    meanings TEXT,
    type TEXT
)
""")

with open("flashcard_words_cleaned.csv", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    print(reader.fieldnames)
    for row in reader:
        db.execute("""
            INSERT INTO flashcard_words (english, german, article, meanings, type)
            VALUES (?, ?, ?, ?, ?)
        """, (
            row["english"],
            row["german"],
            row["article"],
            row["meanings"],
            row["type"]
        ))

db.commit()
db.close()

print("flashcard_words imported")
