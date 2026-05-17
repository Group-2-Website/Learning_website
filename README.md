# 🐹 KidsLearn – Interactive Learning Website for Kids

![Home Page](docs/images/splash-screen.png)

---

## Problem

Children often need additional practice outside of school to strengthen their skills in subjects such as vocabulary, mathematics, languages, and science. Traditional worksheets or homework exercises can be repetitive and do not provide immediate feedback or progress tracking.

Parents also want simple ways to support their children's learning and understand their progress. However, it can be difficult to monitor learning results or provide structured practice at home.

This project aims to provide a simple interactive learning platform where children can practice educational exercises and receive immediate feedback while parents can observe their learning progress.


---

### Scenario

KidsLearn is a browser-based learning application designed for children practising school subjects at home.

The application allows users to:
- select a subject (Math, Science, or Language) from the home page
- choose a topic within that subject (e.g. Fractions, Biology, German Vocabulary)
- step through step-by-step learning cards with images and explanations
- take interactive quizzes with real-time feedback and a final score
- listen to word pronunciation during language learning (text-to-speech)
- explore creative painting activities linked to Math and Science topics

---

##  User Stories

### 1. Choose a Subject
**As a child, I want to choose a learning subject so that I can practise specific subjects.**

- **Inputs:** subject selection
- **Outputs:** list of available subjects (Math, Science, Language)

---

### 2. Select a Topic
**As a child, I want to select a topic within a subject so that I can focus on specific skills.**

- **Inputs:** topic selection
- **Outputs:** list of topics for that subject

---

### 3. Answer Quiz Questions
**As a child, I want to answer questions in quizzes and receive immediate feedback so that I know if my answer is correct.**

- **Inputs:** quiz answer (text or multiple-choice selection)
- **Outputs:** answer correctness feedback, updated score

---

### 4. Track Score
**As a child, I want to see my score update as I answer questions so that I can track how well I'm doing.**

- **Inputs:** each submitted answer
- **Outputs:** live score counter, final results page

---

### 5. Step Through Learning Cards
**As a child, I want to read step-by-step explanations before taking a quiz so that I can prepare.**

- **Inputs:** topic selection → Learn mode
- **Outputs:** learning cards with text, images, and hints

---

### 6. Hear Word Pronunciation
**As a child, I want to hear words pronounced out loud during language learning so that I can learn correct pronunciation.**

- **Inputs:** vocabulary word displayed on a learning card
- **Outputs:** audio playback via text-to-speech (gTTS)

---

### 7. Explore Painting Activities
**As a child, I want to explore painting activities linked to Math and Science topics so that I can be creative while learning.**

- **Inputs:** topic selection → Paint mode
- **Outputs:** interactive drawing canvas with subject-themed pages

---

### 8. Consistent Study Material
**As a parent, I want the vocabulary words and learning steps to remain the same every time my child uses the app, so that I can follow along and support them with what they are studying.**

- **Inputs:** child navigates to a learning or vocabulary topic
- **Outputs:** the same learning cards and vocabulary words are always available across sessions, with no missing or changing study content

---
##  Use Cases

![Use Case Diagram](docs/images/use-case-diagram.png)

### Main Use Cases
- Browse Subjects (Learner)
- Select a Topic (Learner)
- Take a Quiz (Learner) — includes optional filter selection, answering questions, and viewing results
- Learn a Topic Step by Step (Learner) — available for Math and Language topics
- Listen to Word Pronunciation (Learner) — during Language learning cards
- View Visual Learning Aids (Learner) — illustrations and diagrams shown during Math learning cards
- Paint / Draw (Learner) — available for Math and Science topics

### Actors
- **Learner** – child user who browses subjects, takes quizzes, and steps through learning cards

---

##  Architecture

### 3-Tier Layered Architecture

The project is structured as three distinct tiers, each with a single, well-defined responsibility:

| Tier | Location | Responsibility |
|---|---|---|
| **Presentation** | `ui/pages/*.py` | Render NiceGUI widgets and handle user events (button clicks, answer submission, page navigation) |
| **Domain / Business Logic** | `subjects/`, `models/` | Quiz generation, answer checking, filter sanitisation, and shared data types (`QuizCard`, `LearningStep`, `Subject`, `Topic`) |
| **Persistence** | `Database/Learning.py` | ORM entity definitions, SQLAlchemy engine and session factory, CSV seeding |

This is a **3-tier layered architecture**, not MVC. MVC does not apply here because NiceGUI is a server-driven framework where the server owns all UI state and pushes updates to a thin browser client. There is no separate Controller layer — each `build_*_page()` function in `ui/pages/` co-locates widget rendering with its event-handling closures (e.g. `check_answer()`, `_advance()`, `finish_quiz()`) as a direct consequence of how NiceGUI works. Separating them into distinct Controller classes would contradict the framework's design without any practical benefit.

Each tier depends only on the tier below it: the presentation tier calls into the domain tier; the domain tier calls into the persistence tier. No layer knows about the layer above it.

### Design Decisions
- **3-Tier Layered Architecture:** Separating `ui/pages/` (presentation), `subjects/` + `models/` (domain logic), and `Database/` (persistence) keeps each tier independently testable and replaceable. Logic-based topic tests (e.g. `Fractions`, `Operation`) require no database; database tests require no UI.
- **Template Method Pattern:** The `Topic` base class defines the algorithm skeleton — `get_question()` is the fixed entry point that dispatches to either `generate_question()` (logic-based) or `_load_question_from_db()` (database-backed) depending on `quiz_source`, and `check_answer()`, `learning_steps()`, and `quiz_filter_definitions()` are override hooks. Subclasses (e.g. `Fraction`, `Operation`, `Biology`) override only the hooks relevant to them. `Subject` provides a parallel structure for subject-level attributes (`name`, `url_slug`, `icon`, `topics`).
- **Facade Pattern (database):** `Database/Learning.py` encapsulates all SQLAlchemy engine creation, table definitions, session management, and CSV seeding. The rest of the application interacts only with simple session queries.

### Routing

Routes are generated automatically at startup. For every `Subject` registered in `subjects/__init__.py`, the app registers:

| URL pattern                 | Page                            |
|-----------------------------|---------------------------------|
| `/`                         | Home — subject selector         |
| `/{subject}`                | Topic selector for a subject    |
| `/{subject}/{topic}`        | Mode selector (Quiz / Learn)    |
| `/{subject}/{topic}/quiz`   | Interactive quiz                |
| `/{subject}/{topic}/learn`  | Step-by-step learning page      |
| `/{subject}/{topic}/paint`  | Creative painting activity      |

### Adding a New Subject

1. Create a new folder under `subjects/` (e.g. `subjects/science/`).
2. Define `Topic` subclasses (implement `generate_question`, optionally `learning_steps` / `learn_page_image`).
3. Define a `Subject` subclass with `name`, `icon`, `url_slug`, and `topics`.
4. Register the subject in `subjects/__init__.py` by adding it to the `SUBJECTS` list.

All pages and routes are created automatically — no changes to `main.py` needed.

### Current Subjects & Topics

| Subject  | Topic                     | Quiz | Learning | Painting |
|----------|---------------------------|------|----------|----------|
| Math     | Operations                | ✅   | ✅       | ✅       |
| Math     | Fractions                 | ✅   | ✅       | ✅       |
| Science  | Biology                   | ✅   | ❌       | ✅       |
| Science  | Geography                 | ✅   | ❌       | ✅       |
| Language | German–English Vocabulary | ✅   | ✅       | ❌       |

---

## Database and ORM

The application uses **SQLAlchemy** (with `DeclarativeBase`) as its ORM and stores all persistent data in a local **SQLite** file at `Database/learning.db`. All entity definitions, the engine, the session factory, and the CSV seeding logic live in a single Facade module — `Database/Learning.py` — so the rest of the application never touches raw SQL or SQLAlchemy internals directly.

### Entities / Tables

The database contains **three tables**. Two of them consolidate what were originally separate per-subject tables into a single unified table with a discriminator `subject` column, reducing duplication and making it trivial to add new subjects later.

- **`dictionary_words`** — multilingual vocabulary (English / German / French) used for Language learning and quizzes. Seeded from `Database/csv/flashcard_words_cleaned.csv`.
- **`math_content`** — unified table for all Math learning-card content. The `subject` column discriminates between `"operations"` and `"fractions"`. Seeded from `operations.csv` and `fractions_learning.csv`.
- **`science_quiz`** — unified table for all Science multiple-choice quiz questions. The `subject` column discriminates between `"biology"` and `"geography"`; `source_csv` identifies the category within each subject. Seeded from `animals.csv`, `plant.csv`, `human_body.csv`, `continants.csv`, `countries.csv`, and `water in the earth.csv`.

All three tables are independent (no foreign-key relationships between them). Each is populated from its own set of CSV files and queried directly by the relevant subject module.

### ER Diagram

<img src="docs/images/ERD.png" style="max-width: 80%; height: auto;">

---

### Session Management

`Database/Learning.py` creates a single `engine` and `Session` factory at import time:

```python
engine = create_engine(f"sqlite:///{_DATABASE_PATH}")
Base.metadata.create_all(engine)   # creates tables if they don't exist
Session = sessionmaker(bind=engine)
```

Every query in the application opens a fresh session, performs the query, and closes the session in a `finally` block — ensuring connections are never leaked.

---

### Seeding / Importing Data

Running `python Database/Learning.py` directly populates all tables from the CSV files in `Database/csv/`. Each import function is **idempotent**: it deletes the existing rows for its subject before inserting new ones, so re-running the script is safe.

```bash
cd Database
python seed.py
# dictionary imported
# operations imported into math_content
# fractions imported into math_content
# biology imported into science_quiz
# geography imported into science_quiz
```

## Technology

- **Python 3.x**
- **NiceGUI** — browser-based UI framework
- **SQLAlchemy** — ORM for the SQLite database
- **SQLite** — local database (`learning.db`)
- Environment: macOS / GitHub Codespaces

---

##  Repository Structure

```
Learning_website/
├── main.py                          # App entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
│
├── Database/                        # Database models, data files, and SQLite DB
│   ├── Learning.py                  # SQLAlchemy models and CSV import logic
│   ├── flashcard_words_cleaned.csv  # Vocabulary source data
│   ├── operations.csv               # Additional learning operations data
│   └── learning.db                  # SQLite database file
│
├── images/                          # Backgrounds, icons and other images
│   └── icons/
├── models/                          # Core subject/topic data models
│   ├── subject.py
│   └── topic.py
│
├── subjects/                        # Subject definitions and content
│   ├── __init__.py                  # Registers available subjects
│   ├── language/
│   │   └── GermanEnglish.py         # Language subject content
│   └── math/
│       └── mathematics.py           # Math subject content
│
└── ui/                              # NiceGUI page builders and shared UI code
    └── pages/
        ├── __init__.py              # Registers subject with topics, called from main
        ├── common.py                # Shared styling, topbar, and common UI helpers
        ├── home.py                  # Home page
        ├── learn.py                 # Learning mode page
        ├── paint.py                 # Drawing/paint page 
        ├── quiz.py                  # Quiz page
        ├── quiz_results.py          # Quiz results page
        ├── subject.py               # Subject page (e.g. Math)
        └── topic.py                 # Topic page (e.g Math > Fractions)
```

---


## ✅ Data Validation

The application validates all user input to ensure data integrity and a smooth user experience. These checks prevent crashes and guide the user to provide correct input.

### Quiz Answer Validation

Every quiz topic validates the child's answer before accepting it:

- **Empty input** — if the answer field is left blank, the user sees `"Please enter an answer."` instead of the quiz proceeding with an empty value.
- **Operations (integers only)** — the answer must be a whole number. If the child types letters or a decimal, the message `"Only integer numbers allowed!"` is shown.
- **Fractions** — the answer is accepted in multiple equivalent forms (`3/4`, `0.75`, `6/8`). If the format is unrecognisable the message `"Enter a number or fraction (e.g. 3/4 or 0.5)"` is shown. A denominator of zero is explicitly rejected.
- **Language (translate)** — answers are compared case-insensitively and articles (`der/die/das`, `le/la/l'/les`) can be omitted or included. If the article is present but wrong, targeted feedback is given (e.g. `"Wrong article! The correct article is: die"`). For German nouns the app additionally checks capitalisation and returns `"Almost! German nouns must be capitalized: …"`.
- **Language (article quiz)** — the selected article is matched case-insensitively against the correct one.

### API / TTS Endpoint Validation

- The `/api/tts` endpoint rejects requests with a missing or empty `text` parameter with `HTTP 400 – Missing 'text' parameter`.
- Unsupported language codes are silently normalised to `"en"` rather than causing a server error.

### Internal / Data-Parsing Validation

- **Token parsing** — helper functions that convert expression tokens (e.g. `"3/4"`, `"6"`) to numbers return `None` on any `ValueError` or `ZeroDivisionError`, so a bad database value never crashes a page.
- **Expression parsing** — `parse_binary_expression()` returns `None` for any string that does not match the expected `left op right` pattern, allowing the UI to fall back to a plain text display safely.
- **Unknown subject names** — `load_steps_from_db()` checks whether the requested subject exists in its lookup table and returns an empty list if not, avoiding a database query against a non-existent table.
- **Page index normalisation** — the paint page index (URL parameter) is converted to an integer via a dedicated helper; any non-numeric or `None` value returns `None` gracefully instead of raising an exception.

### Database Validation

- **File existence** — `read_csv_rows()` raises a clear `FileNotFoundError` with the full path before attempting to open the file.
- **Encoding fallback** — CSV files are tried first with `utf-8-sig`; if that fails with `UnicodeDecodeError` the reader retries with `cp1252`, and only raises an error when all encodings are exhausted.
- **Transaction safety** — all database import functions (`import_dictionary_words`, `import_operations`, `import_fractions`, `import_grouped_quiz_csvs`) wrap their work in `try/except/finally` blocks: any exception triggers `session.rollback()` so the database is never left in a partial state, and `session.close()` runs unconditionally in every `finally` clause.

---

## How to Run

### Project Setup

1. Create and activate a virtual environment:
   - **macOS/Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Windows:**
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate
     ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Populate the vocabulary database:
   ```bash
   cd Database
   python seed.py
   ```

### Launch

```bash
python main.py
```

The app will be available at **http://localhost:8081**.
