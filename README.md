# 🐹 KidsLearn – Interactive Learning Website for Kids

![Home Page](docs/images/splash-screen.png)

---
## Application Requirements

### Problem

Children often need additional practice outside of school to strengthen their skills in subjects such as vocabulary, mathematics, languages, and science. Traditional worksheets or homework exercises can be repetitive and do not provide immediate feedback.

This project aims to provide a simple interactive learning platform where children can practice educational exercises and receive immediate feedback while parents can observe their learning progress.

---

### Scenario

KidsLearn is a browser-based learning application designed for children practising school subjects at home.

The application allows users to:
- select a subject (Math, Science, or Language) from the home page
- choose a topic within that subject (e.g. Fractions, Biology, German Vocabulary)
- step through learning cards with images and explanations
- take interactive quizzes with real-time feedback and a final score
- listen to word pronunciation during language learning (text-to-speech)
- explore creative painting activities linked to Math and Science topics

---

##  User Stories

### 1. View a List of Subjects
**As a child, I want to see available learning subjects so I can choose one to practise.**

- **Inputs:** none
- **Outputs:** list of available subjects (Math, Science, Language)

---

### 2. Select a Subject
**As a child, I want to select a subject so that I can see its available topics.**

- **Inputs:** selected subject  
- **Outputs:** list of topics for that subject

---

### 3. Select a Topic
**As a child, I want to select a topic within a subject so that I can focus on specific skills.**

- **Inputs:** topic selection
- **Outputs:** mode options for that topic (Quiz, Learn, Paint)

---

### 4. Answer Quiz Questions
**As a child, I want to answer questions in quizzes and receive immediate feedback so that I know if my answer is correct.**

- **Inputs:** quiz answer (text or multiple-choice selection)
- **Outputs:** answer correctness feedback, updated score

---

### 5. View Quiz Results
**As a child, I want to see my results after finishing a quiz so that I 
know how well I did.**

- **Inputs:** completed quiz answers
- **Outputs:** results page with final score

---

### 6. Browse Learning Cards
**As a child, I want to browse learning cards for a topic so that I 
can study before taking a quiz.**

- **Inputs:** topic selection → Learn mode
- **Outputs:** learning cards with text, visuals, and audio

---

### 7. Hear Word Pronunciation
**As a child, I want to hear words pronounced out loud during language learning so that I can learn correct pronunciation.**

- **Inputs:** vocabulary word displayed on a learning card
- **Outputs:** audio playback via text-to-speech (gTTS)

---

### 8. Explore Painting Activities
**As a child, I want to explore painting activities linked to Math and Science topics so that I can be creative while learning.**

- **Inputs:** topic selection → Paint mode
- **Outputs:** interactive drawing canvas with subject-themed pages

---

### 9. Consistent Study Material
**As a parent, I want the vocabulary words and learning steps to remain the same every time my child uses the app, so that I can follow along and support them with what they are studying.**

- **Inputs:** child navigates to a learning or vocabulary topic
- **Outputs:** the same learning cards and vocabulary words are always available across sessions, with no missing or changing study content

---

### 10. Set Quiz Filters
**As a child, I want to set filters before starting a quiz so that I can practise a specific topic and question type.**

- **Inputs:** selected filter options (topic, quiz type, translate direction)
- **Outputs:** filtered quiz session with relevant questions only

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
### Wireframes / Mockups

![Wireframes – Home/Transactions](docs/images/mockup1.png)
<img src="docs/images/mockup2.png" style="max-width: 65%; height: auto;">

---

##  Architecture

### 3-Tier Layered Architecture

![Architecture](docs/images/archi.png)

TThe project is structured as three distinct tiers, each with a single, well-defined responsibility:

| Tier | Location | Responsibility |
|---|---|---|
| **Presentation** | `ui/pages/*.py` | Render NiceGUI widgets and handle user events (button clicks, answer submission, page navigation) |
| **Domain / Business Logic** | `subjects/`, `models/` | Quiz generation, answer checking, filter sanitisation, and shared data types (`QuizCard`, `LearningStep`, `Subject`, `Topic`) |
| **Persistence** | `Database/Learning.py` | ORM entity definitions, SQLAlchemy engine and session factory, CSV seeding |

Each tier depends only on the tier below it: the presentation tier calls into the domain tier; the domain tier calls into the persistence tier. No layer knows about the layer above it.


### Design Decisions
- **3-Tier Layered Architecture:** Separating `ui/pages/` (presentation), `subjects/` + `models/` (domain logic), and `Database/` (persistence) keeps each tier independently testable and replaceable. Logic-based topic tests (e.g. `Fractions`, `Operation`) require no database; database tests require no UI.
- **Template Method Pattern:** The `Topic` base class defines the algorithm skeleton — `get_question()` is the fixed entry point that dispatches to either `generate_question()` (logic-based) or `_load_question_from_db()` (database-backed) depending on `quiz_source`, and `check_answer()`, `learning_steps()`, and `quiz_filter_definitions()` are override hooks. Subclasses (e.g. `Fraction`, `Operation`, `Biology`) override only the hooks relevant to them. `Subject` provides a parallel structure for subject-level attributes (`name`, `url_slug`, `icon`, `topics`).
- **Facade Pattern (database):** `Database/Learning.py` encapsulates all SQLAlchemy engine creation, table definitions, session management, and CSV seeding. The rest of the application interacts only with simple session queries.

### Why not MVC?

MVC assumes a clear separation between a passive View (renders state), a Controller (handles input), and a Model (owns data). NiceGUI collapses the View and Controller into one: the server owns all UI state and pushes DOM updates to a thin browser client, so widgets and their event callbacks are defined together in the same function. Pulling `check_answer()` or `_advance()` out of the page builder and into a separate Controller class would add indirection with no real benefit — the framework's design already enforces a single point of responsibility per page.

A 3-tier model fits the actual boundary that matters here: *what the user sees* (NiceGUI widgets), *what the app knows* (domain logic), and *where data lives* (SQLite via SQLAlchemy).

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

The application uses **SQLAlchemy** (with `DeclarativeBase`) as its ORM and stores all persistent data in a local **SQLite** file at `Database/learning.db`. The engine, session factory, ORM models, and CSV seeding logic all live in `Database/seed.py` — subject modules import `Session` and the model classes from there and never touch raw SQL.

### Entities
- `DictionaryWord`
- `MathContent`
- `ScienceQuiz`

### Mappings

| ORM Class        | Table              | Seeded From                                                                                      |
|------------------|--------------------|--------------------------------------------------------------------------------------------------|
| `DictionaryWord` | `dictionary_words` | `flashcard_words_cleaned.csv`                                                                    |
| `MathContent`    | `math_content`     | `operations.csv`, `fractions_learning.csv`                                                       |
| `ScienceQuiz`    | `science_quiz`     | `animals.csv`, `plant.csv`, `human_body.csv`, `continants.csv`, `countries.csv`, `water in the earth.csv` |

### Relationships
- No foreign-key relationships — all three tables are independent
- `MathContent` uses `subject` (`"operations"` or `"fractions"`) to distinguish Math topics within a single table
- `ScienceQuiz` uses `subject` (`"biology"` or `"geography"`) and `source` (e.g. `"animals"`, `"plant"`, `"human_body"`, `"continants"`, `"countries"`, `"water in the earth"`) to distinguish Science topics and categories within a single table

### ER Diagram

<img src="docs/images/ERD.png" style="max-width: 80%; height: auto;">

---

### How Each Subject Queries the Database

**Science** — filters `science_quiz` by `subject` and `source`, retrieves all matching rows, and picks one at random per question, shuffling its three answer options each time.

**Language** — loads the full filtered word list from `dictionary_words` into memory once per quiz session and pops one word per question, avoiding repeated database hits. The pool is rebuilt only when the filter combination (topic, direction, quiz type) changes. Article quizzes narrow the pool to nouns only. Learning cards query words with a non-empty `meanings` field, ordered by `id`, limited to 50 rows.

**Math** — queries `math_content` by `subject` and optional `topic`, mapping rows directly to `LearningStep` objects. Math quiz questions are generated in code and never read from the database.

### Seeding / Importing Data

Running `python Database/seed.py` populates all tables from the CSV files in `Database/csv/`. Each import is **idempotent** — existing rows for that subject are deleted before re-inserting, so re-running is safe.

---

### 1. Browser-based App (NiceGUI)

NiceGUI runs a **server-side Python process** that owns all UI state and pushes DOM updates to a lightweight browser client over a WebSocket. There is no separate JavaScript framework — every widget, event handler, and page route is declared in Python.

#### Page Registration & Routing

Routes are registered at startup in `ui/pages/__init__.py`. The `register_subject()` function iterates over every `Subject` in `SUBJECTS` and calls `@ui.page(...)` decorators at runtime — see the [Routing](#routing) table in Architecture for the full list of URL patterns. Each page function calls `_setup_page()` first, which injects global CSS (`add_global_css()`) and renders the shared top navigation bar (`build_topbar()`).

#### Shared Top Bar & Global CSS

`ui/pages/common.py` is the single source of truth for all shared visual elements:

| Helper | Purpose |
|---|---|
| `build_topbar()` | Renders the colourful `KidsLearn` brand bar with the four coloured squares and a home-navigation click handler |
| `add_global_css()` | Injects one `<style>` block with every CSS class used across all pages (circles, cards, quiz feedback, stars, etc.) |
| `_apply_bg(url)` | Injects a per-page background image with a semi-transparent white overlay so text always remains readable |
| `_build_page_header(...)` | Renders the back button + page title + subtitle row reused on every detail page |

#### State Management in Closures

NiceGUI does not provide a built-in reactive state store. State is managed with a plain Python **`dict` inside a closure**. The quiz page is the primary example:

```python
state = {"card": ..., "score": 0, "attempts": 0, "checked": False, ...}
```

All event handlers (`check_answer`, `_advance`, `show_hint`, `next_question`) close over `state` and mutate it directly. Widget references (`score_label`, `question_label`, `feedback_label`) are also captured in the closure so handlers can update them without re-rendering the entire page.

#### Audio Playback

Audio is handled entirely in the browser. `audio_button_html()` generates an HTML `<button>` element with a `data-audio-url` attribute. `add_audio_player_script()` injects a single delegated `click` listener on `document` that creates an `Audio` object and calls `.play()` — stopping any currently playing audio first. This avoids multiple simultaneous playback streams.

#### Static Files

`main.py` mounts two static file directories before `ui.run()`:

```python
app.add_static_files('/images', 'images')   # subject icons, backgrounds
app.add_static_files('/static', 'static')   # favicon, paint_canvas.js
```

All image `src` and audio `href` values in the UI use these URL prefixes.

#### Entry Point

```python
# main.py
tts.init()                          # pre-warm the TTS cache
for _subject in SUBJECTS:
    register_subject(_subject)      # dynamic route registration
ui.run(title="E-learning for kids", port=8082, reload=True, favicon='static/favicon.png')
```

---

### 2. Data Validation

The application validates all user input to ensure data integrity and a smooth user experience. These checks prevent crashes and guide the user to provide correct input.

#### Quiz Answer Validation

Every quiz topic validates the child's answer before accepting it:

- **Empty input** — if the answer field is left blank, the user sees `"Please enter an answer."` instead of the quiz proceeding with an empty value.
- **Operations (integers only)** — the answer must be a whole number. If the child types letters or a decimal, the message `"Only integer numbers allowed!"` is shown.
- **Fractions** — the answer is accepted in multiple equivalent forms (`3/4`, `0.75`, `6/8`). If the format is unrecognisable the message `"Enter a number or fraction (e.g. 3/4 or 0.5)"` is shown. A denominator of zero is explicitly rejected.
- **Language (translate)** — answers are compared case-insensitively and articles (`der/die/das`, `le/la/l'/les`) can be omitted or included. If the article is present but wrong, targeted feedback is given (e.g. `"Wrong article! The correct article is: die"`). For German nouns the app additionally checks capitalisation and returns `"Almost! German nouns must be capitalized: …"`.
- **Language (article quiz)** — the selected article is matched case-insensitively against the correct one.

#### API / TTS Endpoint Validation

- The `/api/tts` endpoint rejects requests with a missing or empty `text` parameter with `HTTP 400 – Missing 'text' parameter`.
- Unsupported language codes are silently normalised to `"en"` rather than causing a server error.

#### Internal / Data-Parsing Validation

- **Token parsing** — helper functions that convert expression tokens (e.g. `"3/4"`, `"6"`) to numbers return `None` on any `ValueError` or `ZeroDivisionError`, so a bad database value never crashes a page.
- **Expression parsing** — `parse_binary_expression()` returns `None` for any string that does not match the expected `left op right` pattern, allowing the UI to fall back to a plain text display safely.
- **Unknown subject names** — `load_steps_from_db()` checks whether the requested subject exists in its lookup table and returns an empty list if not, avoiding a database query against a non-existent table.
- **Page index normalisation** — the paint page index (URL parameter) is converted to an integer via a dedicated helper; any non-numeric or `None` value returns `None` gracefully instead of raising an exception.

#### Database Validation

- **File existence** — `read_csv_rows()` raises a clear `FileNotFoundError` with the full path before attempting to open the file.
- **Encoding fallback** — CSV files are tried first with `utf-8-sig`; if that fails with `UnicodeDecodeError` the reader retries with `cp1252`, and only raises an error when all encodings are exhausted.
- **Transaction safety** — all database import functions (`import_dictionary_words`, `import_operations`, `import_fractions`, `import_grouped_quiz_csvs`) wrap their work in `try/except/finally` blocks: any exception triggers `session.rollback()` so the database is never left in a partial state, and `session.close()` runs unconditionally in every `finally` clause.

---

### 3. Database Management

All relevant data is managed via SQLAlchemy ORM. This includes dictionary words, math content, and science quiz questions.

#### Schema & ORM Setup (`Database/seed.py`)

All SQLAlchemy artefacts live in a single file:

| Component | Detail |
|---|---|
| `Base` | `DeclarativeBase` subclass — the metadata registry for all tables |
| `engine` | `create_engine(f"sqlite:///{_DATABASE_PATH}")` — single file at `Database/learning.db` |
| `Session` | `sessionmaker(bind=engine)` — called as `Session()` to open a new session per query |
| `Base.metadata.create_all(engine)` | Runs at import time — creates missing tables without dropping existing ones |

Paths are resolved relative to `seed.py`'s own directory (`__file__`), so the app works regardless of the working directory at launch.

#### Session Lifecycle

Every database function follows the same pattern, with no shared or long-lived sessions:

```python
session = Session()
try:
    # ... queries / adds ...
    session.commit()
except Exception:
    session.rollback()   # never leave a partial write
    raise
finally:
    session.close()      # always release the connection
```

Objects that must outlive the session (e.g. quiz question data) are detached with `session.expunge_all()` before the session closes.

#### Idempotent CSV Seeding

Running `python Database/seed.py` calls five import functions (`import_dictionary_words`, `import_operations`, `import_fractions`, `import_biology`, `import_geography`). Each deletes only its own rows before re-inserting, so re-running never corrupts other subjects' data.

#### CSV Reading

`read_csv_rows(file_path)` handles encoding automatically (tries `utf-8-sig`, falls back to `cp1252`) and raises a clear `FileNotFoundError` if the file is missing.

---

## Implementation


### Technology

- **Python 3.x**
- **NiceGUI** — browser-based UI framework
- **SQLAlchemy** — ORM for the SQLite database
- **SQLite** — local database (`learning.db`)
- Environment: macOS / GitHub Codespaces

---

### Libraries Used

- **nicegui** – browser-based UI framework
- **sqlalchemy** – ORM and database toolkit
- **gtts** – text-to-speech audio generation
- **pytest** – testing

---

### Repository Structure

```
Learning_website/
├── main.py
├── requirements.txt
├── README.md
│
├── Database/
│   ├── seed.py
│   ├── learning.db
│   └── csv/
│
├── docs/images/
│
├── images/
│   └── icons/
│
├── static/
│   ├── favicon.png
│   └── js/
│       └── paint_canvas.js
│
├── models/
│   ├── subject.py
│   ├── topic.py
│   ├── learning_card.py
│   └── quiz_card.py
│
├── subjects/
│   ├── __init__.py
│   ├── math/
│   ├── science/
│   └── language/
│
├── tests/
│   └── test_mathematics.py
│
└── ui/
    ├── __init__.py
    └── pages/  (common, home, subject, topic, filter, quiz, quiz_results, learn, paint)
```

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

