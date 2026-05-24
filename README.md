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
- review previous quiz attempts for any topic (date, score, hints used, percentage) to track progress over time
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

### 11. View Previous Quiz Attempts
**As a child (or parent), I want to see my previous quiz attempts for a topic so that I can track my progress and spot the topics where I needed the most help.**

- **Inputs:** click the **"View previous attempts"** button on the quiz filter page
- **Outputs:** history page listing each finished quiz with date, score, hints used and percentage

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
- View Previous Quiz Attempts (Learner) — opens a history page listing each past attempt for the current topic with date, score, and number of hints used

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

The project is structured as three distinct tiers, each with a single, well-defined responsibility:

| Tier | Location | Responsibility |
|---|---|---|
| **Presentation** | `ui/pages/*.py` | Render NiceGUI widgets and handle user events (button clicks, answer submission, page navigation) |
| **Persistence** | `database/db.py`, `database/seed.py`, `database/dao.py` | `database` facade owning the SQLModel engine and `session_scope()` (`db.py`), idempotent CSV importers (`seed.py`), DAO classes that encapsulate every query against the normalised SQLite schema (`dao.py`) |

Each tier depends only on the tier below it: the presentation tier calls into the domain tier; the domain tier calls into the persistence tier. No layer knows about the layer above it.

#### Quiz history flow

All content (math steps, science questions, dictionary words) and quiz history follow the same layered flow: `ui → topic → DAO → DB`. The page never calls a DAO or opens a session directly — it calls `Topic.record_quiz_attempt(...)` and `Topic.list_quiz_attempts(...)`, which delegate to `QuizAttemptDAO`. If per-subject history rules are ever needed, the `Topic` layer is the right place to add them.


### Design Decisions
- **Template Method Pattern:** The `Topic` base class defines the algorithm skeleton — `get_question()` is the fixed entry point that dispatches to either `generate_question()` (logic-based) or `_load_question_from_db()` (database-backed) depending on `quiz_source`, and `check_answer()`, `learning_steps()`, and `quiz_filter_definitions()` are override hooks. Subclasses (e.g. `Fraction`, `Operation`, `Biology`) override only the hooks relevant to them. `Subject` provides a parallel structure for subject-level attributes (`name`, `url_slug`, `icon`, `topics`).
- **Facade Pattern (database):** `database/db.py` exposes a `Database` class that owns the SQLModel engine and provides a transactional `session_scope()` context manager. The rest of the application calls DAO classes and never opens a session directly.
- **Data Access Object (DAO) Pattern:** Every query lives in a DAO class in `database/dao.py`. Subject modules call DAO methods with plain Python arguments and receive ready-to-use app-facing records (`VocabularyWord`, `ScienceQuestion`, `MathLearningEntry`, `QuizAttemptRecord`) rather than live ORM rows — they never see `select(...)`, `join(...)`, or session objects. This keeps UI code detached from session lifetime and makes it easier to change the storage layer later.
- **Normalised relational schema:** Categorical fields that recur across rows (topic names, word types, articles, science-quiz categories) live in dedicated lookup tables and are referenced by foreign key; multiple-choice options live in a child table rather than as repeating columns. Every parent → child relationship has `cascade="all, delete-orphan"` so removing a subject cleanly removes its dependent rows.

### Relationship to MVC

Our 3-tier layout maps closely onto **MVC**: the **persistence** tier corresponds to the Model, and the **domain logic** tier corresponds to the Controller (generating questions, checking answers, handling filters). The difference is that we did not introduce a separate Controller class per page. Because each NiceGUI page is small and its event handlers only update widgets on that same page, the widget definitions and their callbacks are kept together in one page function.

The benefit is fewer files and less indirection. The drawback is that a page's UI cannot be replaced without also touching its handlers. For a project of this size we considered that an acceptable compromise.

### Routing

Routes are generated automatically at startup. For every `Subject` registered in `subjects/__init__.py`, the app registers:

| URL pattern                 | Page                            |
|-----------------------------|---------------------------------|
| `/`                         | Home — subject selector         |
| `/{subject}`                | Topic selector for a subject    |
| `/{subject}/{topic}`        | Mode selector (Quiz / Learn)    |
| `/{subject}/{topic}/filter` | Pre-quiz filter selection + "View previous attempts" link |
| `/{subject}/{topic}/quiz`   | Interactive quiz                |
| `/{subject}/{topic}/results`| Quiz results (score, stars)     |
| `/{subject}/{topic}/history`| Previous quiz attempts for the topic (score & hints used) |
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
| Language | French–English Vocabulary | ✅   | ✅       | ❌       |

---

## Database and ORM

The application uses **SQLModel** (a thin wrapper around SQLAlchemy + Pydantic) as its ORM and stores all persistent data in a local **SQLite** file at `database/learning.db`. Responsibilities are split across four files:

| File | Role |
|---|---|
| `database/db.py` | `Database` facade — builds the SQLModel engine, exposes `init_schema()` and a transactional `session_scope()` context manager, ensures the SQLite database directory exists, and registers a SQLite `connect` listener that runs `PRAGMA foreign_keys = ON` so FK constraints are actually enforced. |
| `domain/models.py` | SQLModel ORM model classes (see [Entities](#entities) below) |
| `database/seed.py` | CSV import functions (idempotent). Populates content tables and the lookup tables they reference. |
| `database/dao.py` | `MathContentDAO`, `ScienceQuizDAO`, `DictionaryWordDAO`, `QuizAttemptDAO` — encapsulate every query and map ORM rows to plain app-facing data records. |


### Entities

**Content (seeded from CSV):**
- `DictionaryWord` — vocabulary row; translations (`english` / `german` / `french`) and `meanings` are stored as flat columns
- `DictionaryTopic` *(lookup)* — distinct word topics (e.g. *Time*, *Food & Drinks*)
- `WordType` *(lookup)* — distinct word types (e.g. *noun*, *verb*)
- `Article` *(lookup)* — grammatical articles, scoped by `language` (`"de"` → der/die/das, `"fr"` → le/la/l'/les)
- `MathSubject` *(lookup)* — *operations*, *fractions*
- `MathTopic` *(lookup)* — topics within a math subject (e.g. *intro*, *addition*)
- `MathContent` — a single learning step (title, explanation, expression, answer, image)
- `ScienceSubject` *(lookup)* — *biology*, *geography*
- `ScienceTopicRow` *(lookup)* — quiz categories within a science subject (e.g. *animals*, *countries*); named `ScienceTopicRow` to avoid colliding with the UI-level `ScienceTopic` class
- `ScienceQuiz` — a single multiple-choice question (text only)
- `ScienceQuizOption` — one row per answer option (`label` = A/B/C, `text`, `is_correct`)

**Runtime / quiz history:**
- `QuizSubject` *(lookup)* — distinct subject names referenced by quiz attempts
- `QuizTopic` *(lookup)* — topic name within a `QuizSubject`
- `QuizAttempt` — one row per finished quiz session: `topic_id`, `score`, `attempts`, `hints_used`, `filters` JSON, `created_at` timestamp. The subject is reachable through `topic.subject`.

### Mappings

| ORM Class           | Table                 | Seeded From                                                                                              |
|---------------------|-----------------------|----------------------------------------------------------------------------------------------------------|
| `DictionaryWord`    | `dictionary_words`    | `flashcard_words_cleaned.csv`                                                                            |
| `DictionaryTopic`   | `dictionary_topic`    | distinct `topic` values from `flashcard_words_cleaned.csv`                                               |
| `WordType`          | `word_type`           | distinct `type` values from `flashcard_words_cleaned.csv`                                                |
| `Article`           | `article`             | distinct `article_german` / `article_french` values from `flashcard_words_cleaned.csv`                   |
| `MathSubject`       | `math_subject`        | populated implicitly when math content is imported                                                       |
| `MathTopic`         | `math_topic`          | distinct `topic` values from `operations.csv` / `fractions_learning.csv`                                 |
| `MathContent`       | `math_content`        | `operations.csv`, `fractions_learning.csv`                                                               |
| `ScienceSubject`    | `science_subject`     | populated implicitly when science content is imported                                                    |
| `ScienceTopicRow`   | `science_topic`       | one row per source CSV filename (e.g. `animals`, `countries`)                                            |
| `ScienceQuiz`       | `science_quiz`        | `animals.csv`, `plant.csv`, `human_body.csv`, `continants.csv`, `countries.csv`, `water in the earth.csv` |
| `ScienceQuizOption` | `science_quiz_option` | three rows per CSV question (`Option A/B/C`), with `is_correct` set from `Correct Answer`                |
| `QuizSubject`       | `quiz_subject`        | populated at runtime — first time a quiz is finished for a subject                                       |
| `QuizTopic`         | `quiz_topic`          | populated at runtime — first time a quiz is finished for a (subject, topic) pair                         |
| `QuizAttempt`       | `quiz_attempt`        | written at runtime by `QuizAttemptDAO.record()` when the user finishes a quiz                            |

### Relationships

- `MathSubject` ⇄ `MathTopic` ⇄ `MathContent` — chained one-to-many via `MathContent.subject_id` / `MathContent.topic_id`, cascade delete.
- `ScienceSubject` ⇄ `ScienceTopicRow` ⇄ `ScienceQuiz` ⇄ `ScienceQuizOption` — chained one-to-many with cascade delete at every step; each quiz owns its three answer-option rows.
- `DictionaryWord` ⇄ `{DictionaryTopic, WordType, Article (×2)}` — many-to-one for each lookup (all four FKs nullable).
- `QuizSubject` ⇄ `QuizTopic` ⇄ `QuizAttempt` — one-to-many at each step, cascade delete.
- Every lookup table carries a `UniqueConstraint` on its natural key (`(subject_id, name)` for the topic tables, `(language, text)` for `Article`, `(quiz_id, label)` for `ScienceQuizOption`) so a duplicate insert raises an error instead of silently splitting data.


### ER Diagram

<img src="docs/images/ERD.png" style="max-width: 90%; height: auto;">

---

### How Each Subject Queries the Database

All queries go through a DAO in `database/dao.py`. Subject modules never open a session themselves.

**Science** — calls `ScienceQuizDAO().list_questions(subject_name, source)` which joins `science_quiz → science_subject` and `science_quiz → science_topic`, filters by both names (case-insensitive), and maps the result to `ScienceQuestion` records. The subject module picks one record at random, shuffles its option texts, and uses the option flagged `is_correct=True` as the expected answer.

**Language** — calls `DictionaryWordDAO.list_by_topic()`, `list_topics()`, and `list_for_learning()`. Queries that filter by topic join through the `dictionary_topic` lookup and map each result to a `VocabularyWord` record containing the resolved topic / word-type / article text. Article quizzes narrow the in-memory pool to nouns only. Learning cards use `list_for_learning(topic, limit=50)`.

**Math** — calls `MathContentDAO().list_steps(subject_name, topic_name)` which joins `math_content → math_subject` and (when a topic is requested) `math_content → math_topic`, filtering both by name (case-insensitive), then maps rows to `MathLearningEntry` records. The subject module converts those records to `LearningStep` objects for the UI. Math quiz questions are generated in code and never read from the database.

**Quiz history (all subjects)** — when the user finishes any quiz, `ui/pages/quiz.py` calls `Topic.record_quiz_attempt(...)`. That topic-level method delegates to `QuizAttemptDAO().record(subject, topic, score, attempts, hints_used, filters)`. The DAO uses `_get_or_create_subject` / `_get_or_create_topic` helpers to upsert the lookup rows in `quiz_subject` / `quiz_topic`, then inserts a `QuizAttempt` row containing `topic_id`, the score, the number of attempted questions, the count of questions on which the **Hint** button was pressed at least once (`hints_used`), the filter selections (JSON-encoded), and a UTC timestamp. The history page (`ui/pages/history.py`) calls `Topic.list_quiz_attempts(...)`, which delegates to `QuizAttemptDAO().list_for(subject, topic, limit=50)` and returns the most recent attempts newest-first.

### Seeding / Importing Data

Running `python -m database.seed` populates all tables from the CSV files in `seed-data/csv/`. Each import is **idempotent** — existing rows for that subject are deleted before re-inserting, so re-running is safe. Lookup rows are inserted on first encounter with `_get_or_create(...)`, keeping the seeding logic straightforward and easy to follow.

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
def main():
    db.init_schema()                # create any missing tables (incl. quiz_attempt)
    tts.init()                      # pre-warm the TTS cache
    for _subject in SUBJECTS:
        register_subject(_subject)  # dynamic route registration
    app.add_static_files('/images', 'images')
    app.add_static_files('/static', 'static')
    ui.run(title="E-learning for kids", port=8082, reload=False, favicon='static/favicon.png')


# NiceGUI's auto-reload spawns a child with __name__ == "__mp_main__",
# so we accept both names here.
if __name__ in {"__main__", "__mp_main__"}:
    main()
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
- **Transaction safety** — `DataSeeder.seed()` is called inside a single `db.session_scope()` block in `__main__`, which commits on success and rolls back + re-raises on any exception, so the database is never left in a partial state.

---

### 3. Database Management

All relevant data is managed via SQLAlchemy / SQLModel ORM. This includes dictionary words, math content, science quiz questions, and runtime quiz-attempt history. For the full schema, file responsibilities, and seeding details see the [Database and ORM](#database-and-orm) section above.

Paths are resolved relative to `db.py`'s own directory (`__file__`), so the app works regardless of the working directory at launch.

#### Session Lifecycle

DAO methods and importers use the `session_scope()` context manager — no manual `try/except/finally`, no shared or long-lived sessions:

```python
with db.session_scope() as session:
    rows = list(session.exec(select(MathContent)).all())
    # commit on clean exit, rollback + re-raise on exception, close always
```

Objects that must outlive the session are usually mapped inside the DAO to plain frozen dataclass records before the scope exits, so UI code never depends on detached ORM instances.


---

## Implementation


### Technology

- **Python 3.x**
- **NiceGUI** — browser-based UI framework
- **SQLModel** — ORM (built on SQLAlchemy + Pydantic) for the SQLite database
- **SQLite** — local database (`learning.db`)
- Environment: macOS / Windows / GitHub Codespaces

---

### Libraries Used

- **nicegui** – browser-based UI framework
- **sqlmodel** – ORM (wraps SQLAlchemy + Pydantic)
- **sqlalchemy** – underlying engine / session / query machinery used by SQLModel
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
├── database/
│   ├── db.py
│   ├── seed.py
│   ├── dao.py
│   ├── learning.db
│   └── csv/
│
├── domain/
│   └── models.py        ← SQLModel ORM entities
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
├── core/
│   ├── subject.py
│   ├── topic.py
│   ├── records.py
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
│   ├── conftest.py
│   ├── test_unit.py
│   ├── test_integration.py
│   └── test_database.py
│
└── ui/
    ├── __init__.py
    └── pages/  (common, home, subject, topic, filter, quiz, quiz_results, history, learn, paint)
```

---


## How to Run

### 1. Project Setup

- Python 3.x is required
- Create and activate a virtual environment:
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
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Configuration

No configuration is required. The application has no `.env` file, no environment variables, and no command-line flags. The following values are resolved automatically from the project layout:

| Setting | Value | Where it is set |
|---|---|---|
| Database file | `database/learning.db` | `database/db.py` — derived from `__file__` so it works from any working directory |
| HTTP port | `8082` | `main.py` → `ui.run(port=8082, ...)` |
| Static mounts | `/images` and `/static` | `main.py` → `app.add_static_files(...)` |
| TTS audio cache | `subjects/language/audio_cache/` | `subjects/language/tts.py` |
| Page title / favicon | `"E-learning for kids"` / `static/favicon.png` | `main.py` → `ui.run(...)` |

To change the port or any of the above, edit the corresponding call directly in `main.py`.

### 3. Database Setup

Seed the database with all CSV data (dictionary words, math content, science quizzes). Run from the project root so the `Database` package is importable:

```bash
python -m database.seed
```

This is **idempotent** — safe to re-run at any time.

### 4. Launch

```bash
python main.py
```

The app will be available at **http://localhost:8082**.

### 5. Usage

Select a subject:
1. Open the home page and choose a subject (Math, Science, or Language).
2. Select a topic within that subject.
3. Choose a mode — **Quiz**, **Learn**, or **Paint**.

**Quiz mode:**
1. (Optional) Set filters — topic category, question type, or translation direction.
2. (Optional) Click **"View previous attempts"** on the filter page to see past scores and how often you used hints for that topic.
3. Answer each question and receive immediate feedback.
4. View your final score on the results page — the attempt is automatically saved to the database (`quiz_attempt` table) and will appear in the history.

**Learn mode:**
1. (Optional) Set filters to narrow the study content.
2. Step through learning cards with images and explanations.
3. For Language cards, press the speaker button to hear word pronunciation.

**Paint mode:**
1. Browse subject-themed painting pages.
2. Use the canvas to draw and colour freely.

---

## Testing

Run the full test suite from the project root:

```bash
python -m pytest tests/ -v
```

The suite contains **42 automated tests** split into unit tests (`tests/test_unit.py`), database tests (`tests/test_database.py`), and integration tests (`tests/test_integration.py`). Database tests use an in-memory SQLite database via the `db` pytest fixture in `tests/conftest.py`, so they require no setup.

### Test Cases

This section documents **15 representative test cases** across four categories.
Cases TC_001–TC_012 correspond to automated pytest tests (6 unit, 3 database, 3 integration).
Cases TC_013–TC_015 are manual UI tests that cannot be fully automated without a browser testing framework.

#### Unit Tests

##### TC_001 — Perfect score gives 100 % and 5 stars

| Field | Value |
|---|---|
| **Test Case ID** | TC_001 |
| **Title** | Perfect score gives 100 % and 5 stars |
| **Description** | Verify that `calculate_quiz_result` returns 100 %, 5.0 stars and the "Perfect score!" message when every question is answered correctly. |
| **Preconditions** | `ui/pages/quiz_results.py` is importable; no database required. |
| **Test Data** | `score = 10`, `attempts = 10` |
| **Expected Result** | `pct == 100`, `stars == 5.0`, `message == "Perfect score! Amazing!"` |
| **Actual Result** | `pct == 100`, `stars == 5.0`, `message == "Perfect score! Amazing!"` |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_unit.py :: TestQuizResultCalculation :: test_perfect_score_gives_100_percent_and_5_stars` |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Import `calculate_quiz_result` from `ui.pages.quiz_results` | — |
| 2 | Call `calculate_quiz_result(score, attempts)` | `score=10`, `attempts=10` |
| 3 | Assert returned percentage equals 100 | `pct == 100` |
| 4 | Assert returned stars equals 5.0 | `stars == 5.0` |
| 5 | Assert returned message equals "Perfect score! Amazing!" | `message == "Perfect score! Amazing!"` |

##### TC_002 — Score of 70 % or higher gives "Great job!" message

| Field | Value |
|---|---|
| **Test Case ID** | TC_002 |
| **Title** | Score of 70 % or higher gives "Great job!" message |
| **Description** | Verify that a score of exactly 70 % (the lower bound of the bracket) triggers the "Great job! Keep it up!" feedback message and the correct percentage. The branch in `calculate_quiz_result` is `pct >= 70`, so 70 is inclusive. |
| **Preconditions** | `ui/pages/quiz_results.py` is importable; no database required. |
| **Test Data** | `score = 7`, `attempts = 10` |
| **Expected Result** | `pct == 70`, `message == "Great job! Keep it up!"` |
| **Actual Result** | `pct == 70`, `message == "Great job! Keep it up!"` |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_unit.py :: TestQuizResultCalculation :: test_above_70_percent_gives_great_job_message` |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Import `calculate_quiz_result` from `ui.pages.quiz_results` | — |
| 2 | Call `calculate_quiz_result(score, attempts)` | `score=7`, `attempts=10` |
| 3 | Assert returned percentage equals 70 | `pct == 70` |
| 4 | Assert returned message equals "Great job! Keep it up!" | `message == "Great job! Keep it up!"` |

##### TC_003 — Equivalent fraction accepted as correct answer

| Field | Value |
|---|---|
| **Test Case ID** | TC_003 |
| **Title** | Equivalent fraction accepted as correct answer |
| **Description** | Verify that `Fractions.check_answer` accepts a mathematically equivalent fraction (e.g. `2/4` when the correct answer is `1/2`) and marks it as correct. |
| **Preconditions** | `subjects/math/fraction_topic.py` is importable; no database required. |
| **Test Data** | `user_answer = "2/4"`, `correct_answer = "1/2"` |
| **Expected Result** | `ok == True` |
| **Actual Result** | `ok == True` |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_unit.py :: TestFractionAnswerCheck :: test_equivalent_fraction_accepted`. The companion test `test_decimal_accepted` also verifies that the decimal form `0.5` is accepted as equivalent to `1/2`. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Instantiate `Fractions()` | — |
| 2 | Call `fractions.check_answer(user_answer, correct_answer)` | `"2/4"`, `"1/2"` |
| 3 | Assert the first return value (ok) is `True` | `ok == True` |

##### TC_004 — Operations quiz rejects a non-integer answer

| Field | Value |
|---|---|
| **Test Case ID** | TC_004 |
| **Title** | Operations quiz rejects a non-integer answer |
| **Description** | Verify that `Operation.check_answer` rejects a fractional input (e.g. `"1/2"`) when an integer answer is expected and returns a non-empty error message to display to the user. |
| **Preconditions** | `subjects/math/operations.py` is importable; no database required. |
| **Test Data** | `user_answer = "1/2"`, `correct_answer = "7"` |
| **Expected Result** | `ok == False`; `msg` is a non-empty string (the "Only integer numbers allowed!" feedback). |
| **Actual Result** | `ok == False`; `msg` was non-empty. |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_unit.py :: TestOperationAnswerCheck :: test_non_integer_rejected`. The companion test `test_empty_answer_rejected` covers the empty-input path. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Instantiate `Operation()` | — |
| 2 | Call `op.check_answer(user_answer, correct_answer)` | `"1/2"`, `"7"` |
| 3 | Assert the first return value (ok) is `False` | `ok == False` |
| 4 | Assert the second return value (msg) is non-empty | `bool(msg) == True` |

##### TC_005 — Decimal form accepted as equivalent to a fraction

| Field | Value |
|---|---|
| **Test Case ID** | TC_005 |
| **Title** | Decimal form accepted as equivalent to a fraction |
| **Description** | Verify that `Fractions.check_answer` accepts a decimal answer (`"0.5"`) when the correct answer is the fractional form `"1/2"`. This ensures children who type either notation are not penalised. |
| **Preconditions** | `subjects/math/fraction_topic.py` is importable; no database required. |
| **Test Data** | `user_answer = "0.5"`, `correct_answer = "1/2"` |
| **Expected Result** | `ok == True` |
| **Actual Result** | `ok == True` |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_unit.py :: TestFractionAnswerCheck :: test_decimal_accepted`. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Instantiate `Fractions()` | — |
| 2 | Call `fractions.check_answer(user_answer, correct_answer)` | `"0.5"`, `"1/2"` |
| 3 | Assert the first return value (ok) is `True` | `ok == True` |

##### TC_006 — Fraction division filter produces the `÷` operator

| Field | Value |
|---|---|
| **Test Case ID** | TC_006 |
| **Title** | Fraction division filter produces the `÷` operator |
| **Description** | Verify that calling `Fractions.generate_question({"operation": "div"})` produces a question string containing the `÷` symbol, confirming that the operation filter is respected when generating quiz questions. |
| **Preconditions** | `subjects/math/fraction_topic.py` is importable; no database required. |
| **Test Data** | Filter `{"operation": "div"}` |
| **Expected Result** | `"÷"` appears in the generated question string. |
| **Actual Result** | `"÷"` was present in the generated question. |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_unit.py :: TestFractionQuestionGeneration :: test_div_filter_produces_div_sign`. The companion test `test_add_filter_produces_plus_sign` checks the `+` operator path. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Instantiate `Fractions()` | — |
| 2 | Call `fractions.generate_question({"operation": "div"})` | — |
| 3 | Assert `"÷"` is a substring of the returned question | `"÷" in q` |

#### DB Tests

##### TC_007 — Seeded science quiz questions are queryable from the database

| Field | Value |
|---|---|
| **Test Case ID** | TC_007 |
| **Title** | Seeded science quiz questions are queryable from the database |
| **Description** | Verify that science quiz questions inserted by the seeder (mimicked here by the test fixture) can be retrieved correctly. In the real application all quiz content enters the database through CSV seeding — there is no user-facing "save question" flow. The test also exercises the normalized schema: each quiz row owns three `ScienceQuizOption` children and the correct answer is the option flagged `is_correct=True`. |
| **Preconditions** | In-memory SQLite database created via the `db` pytest fixture; `ScienceSubject`, `ScienceTopicRow`, `ScienceQuiz` and `ScienceQuizOption` models importable. The fixture inserts two animal quiz rows (each with three option children) to simulate a seeded dataset. |
| **Test Data** | Subject `name="biology"`, topic `name="animals"`, two quiz rows whose correct options are `"Frog"` and `"Eagle"` |
| **Expected Result** | Query filtered through the `science_topic` lookup table by `name="animals"` returns 2 rows; the set of texts from options flagged `is_correct=True` equals `{"Frog", "Eagle"}`. |
| **Actual Result** | Query returned 2 rows; correct-option texts matched expected set. |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_database.py :: test_saving_science_quiz_persists`. The test fixture directly inserts rows the same way the `DataSeeder` does at application startup. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Obtain a fresh in-memory DB session via the `db` fixture | — |
| 2 | Insert a `ScienceSubject` (simulating the seeder creating the subject) | `name="biology"` |
| 3 | Insert a `ScienceTopicRow` (lookup row replacing the old free-string `source`) | `name="animals"` |
| 4 | Insert two `ScienceQuiz` rows, each with three `ScienceQuizOption` children flagged with `is_correct` | correct options `"Frog"`, `"Eagle"` |
| 5 | Commit the session | — |
| 6 | Query `ScienceQuiz` joined to `ScienceTopicRow` filtered by `name="animals"` | — |
| 7 | Assert row count equals 2 | `len(rows) == 2` |
| 8 | Assert the set of texts from `is_correct=True` options matches expected | `{"Frog", "Eagle"}` |

##### TC_008 — Math subject–contents ORM relationship is navigable

| Field | Value |
|---|---|
| **Test Case ID** | TC_008 |
| **Title** | Math subject–contents ORM relationship is navigable |
| **Description** | Verify that `MathContent` rows linked to a `MathSubject` are accessible through the ORM relationship attribute `subject.contents`, and that each content row remains linked to the correct `MathTopic` through `content.topic_obj`. |
| **Preconditions** | In-memory SQLite database; `MathSubject`, `MathTopic` and `MathContent` models importable. |
| **Test Data** | Subject `name="fractions"`, two `MathTopic` rows (`"addition"`, `"subtraction"`), one `MathContent` row per topic |
| **Expected Result** | `len(subject.contents) == 2`; the set `{c.topic_obj.name for c in subject.contents}` equals `{"addition", "subtraction"}`. |
| **Actual Result** | `len(subject.contents) == 2`; topic lookup names matched. |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_database.py :: test_math_subject_contents_relationship` |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Create a `MathSubject`, commit and refresh to obtain its `id` | `name="fractions"` |
| 2 | Insert two `MathTopic` rows under that subject | `"addition"`, `"subtraction"` |
| 3 | Add one `MathContent` row per topic, referencing both `subject_id` and `topic_id` | — |
| 4 | Commit the session and refresh the subject | — |
| 5 | Access `subject.contents` | — |
| 6 | Assert length equals 2 | `len(subject.contents) == 2` |
| 7 | Assert `{c.topic_obj.name for c in subject.contents}` matches | `{"addition", "subtraction"}` |

##### TC_009 — Deleting a science subject cascades to its quizzes

| Field | Value |
|---|---|
| **Test Case ID** | TC_009 |
| **Title** | Deleting a science subject cascades to its quizzes |
| **Description** | Verify that removing a `ScienceSubject` row also deletes every `ScienceQuiz` row linked to it via `subject_id` **and** every `ScienceQuizOption` linked to those quizzes, leaving no orphaned rows. This protects referential integrity when a subject is removed during re-seeding and exercises the chained `cascade="all, delete-orphan"` configuration on the options child table. |
| **Preconditions** | In-memory SQLite database via the `db` fixture; `ScienceSubject`, `ScienceTopicRow`, `ScienceQuiz` and `ScienceQuizOption` models importable. |
| **Test Data** | One `ScienceSubject` (`name="biology"`) with one `ScienceTopicRow` (`name="animals"`) and two `ScienceQuiz` children, each owning three option rows. |
| **Expected Result** | After `db.delete(subject)` and commit, both `select(ScienceQuiz).all()` and `select(ScienceQuizOption).all()` return empty lists. |
| **Actual Result** | All quizzes and their options were removed. |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_database.py :: test_deleting_science_subject_cascades_to_quizzes`. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Obtain a fresh in-memory DB session via the `db` fixture | — |
| 2 | Insert a `ScienceSubject` and commit | `name="biology"` |
| 3 | Insert a `ScienceTopicRow` under that subject and commit | `name="animals"` |
| 4 | Insert two `ScienceQuiz` rows (each with three `ScienceQuizOption` children) and commit | — |
| 5 | Delete the subject and commit | `db.delete(subject)` |
| 6 | Query all rows from `ScienceQuiz` and `ScienceQuizOption` | — |
| 7 | Assert both result lists are empty | `quizzes == []`, `options == []` |

#### Integration Tests

##### TC_010 — MathContentDAO returns learning steps for a seeded subject

| Field | Value |
|---|---|
| **Test Case ID** | TC_010 |
| **Title** | MathContentDAO returns learning steps for a seeded subject |
| **Description** | Verify that the `MathContentDAO.list_steps()` query correctly retrieves rows for a subject seeded into the in-memory database. This exercises the join between `math_content` and `math_subject` and confirms that DAO → DB → ORM wiring works end-to-end. |
| **Preconditions** | In-memory SQLite database created via the `database` fixture and pre-populated by the `seeded_math` fixture with two `MathContent` rows under the `"fractions"` subject. |
| **Test Data** | Subject `name="fractions"`, two seeded learning rows (`topic="add"`, `topic="mul"`). |
| **Expected Result** | `dao.list_steps("fractions")` returns 2 rows. |
| **Actual Result** | DAO returned 2 rows. |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_integration.py :: TestMathContentDAO :: test_list_steps_returns_seeded_rows`. The companion test `test_list_steps_filters_by_topic` further verifies the `topic_name` filter, and `test_list_steps_unknown_subject_returns_empty` covers the empty-result path. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Obtain a fresh in-memory `Database` via the `database` fixture | — |
| 2 | Trigger the `seeded_math` fixture to insert 2 `MathContent` rows | subject `"fractions"`, topics `"add"`, `"mul"` |
| 3 | Instantiate `MathContentDAO(database)` | — |
| 4 | Call `dao.list_steps("fractions")` | — |
| 5 | Assert the returned list has length 2 | `len(rows) == 2` |

##### TC_011 — ScienceQuizDAO filters questions by source category

| Field | Value |
|---|---|
| **Test Case ID** | TC_011 |
| **Title** | ScienceQuizDAO filters questions by source category |
| **Description** | Verify that `ScienceQuizDAO.list_questions(subject, source)` returns only quizzes whose related `ScienceTopicRow.name` matches the given category. Querying for an unseeded source (e.g. `"plants"`) must return an empty list — not raise or return unrelated rows. Internally the DAO now joins `science_quiz → science_topic` and filters by the lookup table's `name`. |
| **Preconditions** | In-memory SQLite database; `seeded_science` fixture inserts two `ScienceQuiz` rows under subject `"biology"` and topic `"animals"`. |
| **Test Data** | Subject `name="biology"`, requested `source="plants"` (no matching rows). |
| **Expected Result** | `dao.list_questions("biology", "plants")` returns an empty list. |
| **Actual Result** | DAO returned `[]`. |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_integration.py :: TestScienceQuizDAO :: test_list_questions_filters_by_source`. Companion tests verify that `source="animals"` returns 2 rows and that an unknown subject also returns `[]`. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Obtain a fresh in-memory `Database` via the `database` fixture | — |
| 2 | Trigger the `seeded_science` fixture (inserts 2 `animals` rows for `biology`) | — |
| 3 | Instantiate `ScienceQuizDAO(database)` | — |
| 4 | Call `dao.list_questions("biology", "plants")` | — |
| 5 | Assert the returned list is empty | `rows == []` |

##### TC_012 — Biology topic builds a quiz card from seeded database rows

| Field | Value |
|---|---|
| **Test Case ID** | TC_012 |
| **Title** | Biology topic builds a quiz card from seeded database rows |
| **Description** | End-to-end check that the `Biology` topic (`subjects/science/science.py`) reads a random question from the database via `ScienceQuizDAO`, packages it as a `QuizCard`, and exposes one of the seeded correct answers. The DAO is rebound to the in-memory test database with `monkeypatch`. |
| **Preconditions** | In-memory database seeded with two `animals` quizzes whose correct answers are `"Frog"` and `"Eagle"`. `monkeypatch` replaces `subjects.science.science.ScienceQuizDAO` with one bound to the test database. |
| **Test Data** | Filter `{"category": "animals"}`. |
| **Expected Result** | Returned object is a `QuizCard` with `topic == "Biology"` and `correct_answer` in `{"Frog", "Eagle"}`. |
| **Actual Result** | Returned `QuizCard` with topic `"Biology"` and a correct answer drawn from the seeded set. |
| **Status** | Pass |
| **Comments** | Automated in `tests/test_integration.py :: TestScienceQuizEndToEnd :: test_quiz_returns_card_from_seeded_data`. Companion tests verify the card always has 3 options and that an empty database returns a graceful `"No question available."` fallback. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Obtain a fresh in-memory `Database` and trigger `seeded_science` | — |
| 2 | Monkeypatch `subjects.science.science.ScienceQuizDAO` to use the test DB | — |
| 3 | Call `Biology().get_question({"category": "animals"})` | — |
| 4 | Assert the result is a `QuizCard` | `isinstance(card, QuizCard)` |
| 5 | Assert `card.topic == "Biology"` | — |
| 6 | Assert `card.correct_answer in {"Frog", "Eagle"}` | — |

#### Manual / UI Tests

> These tests require a running application (`python main.py`) and a web browser. They cannot be fully automated without a browser testing framework such as Playwright or Selenium.

##### TC_013 — User navigates to a subject and sees the topic list

| Field | Value |
|---|---|
| **Test Case ID** | TC_013 |
| **Title** | User navigates to a subject and sees the topic list |
| **Description** | Verify that clicking a subject card on the home page loads the subject page and displays all available topics for that subject. |
| **Preconditions** | Application is running (`python main.py`); database is seeded; browser is open at `http://localhost:8082`. |
| **Test Data** | Subject: **Mathematics** |
| **Expected Result** | Subject page loads and shows topic cards (e.g. "Operations", "Fractions"). |
| **Actual Result** | Subject page loaded and displayed topic cards correctly. |
| **Status** | Pass |
| **Comments** | No issues found. Navigation is handled by NiceGUI router in `ui/pages/subject.py`. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Open a browser and navigate to the application home page | `http://localhost:8082` |
| 2 | Observe the subject cards displayed on screen | — |
| 3 | Click the **Mathematics** subject card | — |
| 4 | Verify the subject page loads without errors | — |
| 5 | Verify at least two topic cards are visible (e.g. "Operations", "Fractions") | — |

##### TC_014 — User completes a quiz and sees the results screen with stars

| Field | Value |
|---|---|
| **Test Case ID** | TC_014 |
| **Title** | User completes a quiz and sees the results screen with stars |
| **Description** | Verify that after answering all questions in a quiz, the application navigates to the results page and displays the score, star rating, and a feedback message. |
| **Preconditions** | Application is running; database is seeded; user is on a topic page that has quiz questions. |
| **Test Data** | Subject: **Mathematics**, Topic: **Operations**, answers: all correct |
| **Expected Result** | Results page displays percentage score, star icons (0–5), and an appropriate feedback message (e.g. "Great job! Keep it up!"). |
| **Actual Result** | Results page displayed correctly with score, stars, and feedback message. |
| **Status** | Pass |
| **Comments** | Star rating logic is unit-tested in TC_001 and TC_002. This test validates the end-to-end rendering in the UI. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Navigate to **Mathematics → Operations → Quiz** | `http://localhost:8082` |
| 2 | Answer each question presented and click **Submit** | Correct answers |
| 3 | After the last question, observe the page transition | — |
| 4 | Verify the results page shows a numeric score (e.g. "Your score: 8 / 10") | — |
| 5 | Verify star icons are rendered corresponding to the score | — |
| 6 | Verify a feedback message is displayed | e.g. "Great job! Keep it up!" |

##### TC_015 — Difficulty filter limits questions to the selected level

| Field | Value |
|---|---|
| **Test Case ID** | TC_015 |
| **Title** | Difficulty filter limits questions to the selected level |
| **Description** | Verify that changing the difficulty filter on a math topic page causes all subsequent questions to match the selected difficulty level (e.g. only easy multiplications with small numbers). |
| **Preconditions** | Application is running; user is on the **Operations** topic page; default difficulty is "easy". |
| **Test Data** | Topic: **Operations**, filter change from `easy` → `hard` |
| **Expected Result** | After selecting "hard", generated questions use larger numbers / more complex operations consistent with the hard difficulty definition. |
| **Actual Result** | Questions changed to use larger operands after switching to "hard". |
| **Status** | Pass |
| **Comments** | Filter sanitisation is unit-tested by `TestFilterDefinition` in `tests/test_unit.py`. This test validates the filter is applied end-to-end in the UI. |

**Test Steps**

| Step | Action | Value |
|---|---|---|
| 1 | Navigate to **Mathematics → Operations** topic page | `http://localhost:8082` |
| 2 | Observe the default difficulty filter value | `easy` |
| 3 | Note the style of question displayed (small numbers, simple ops) | — |
| 4 | Change the difficulty dropdown to **Hard** | `hard` |
| 5 | Request a new question (click **Next** or refresh question) | — |
| 6 | Verify the new question uses larger numbers or harder operations | — |

---

## 🤝 Contributing

Work was distributed across the team using a **GitHub Project Board**, where every task was tracked as an issue and moved through the *Todo → In Progress → Done* columns. This kept responsibilities transparent and made it easy to see who was working on what at any time.

Project board: <https://github.com/orgs/Group-2-Website/projects/3/views/1>
