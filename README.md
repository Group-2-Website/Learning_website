# KidsLearn — Interactive Learning Website for Kids

## 📝 Application Overview

---

## Problem

Children often need additional practice outside of school to strengthen their skills in subjects such as vocabulary, mathematics, languages, and science. Traditional worksheets or homework exercises can be repetitive and do not provide immediate feedback or progress tracking.

Parents also want simple ways to support their children's learning and understand their progress. However, it can be difficult to monitor learning results or provide structured practice at home.

This project aims to provide a simple interactive learning platform where children can practice educational exercises and receive immediate feedback while parents can observe their learning progress.

---

## Scenario

KidsLearn is a browser-based learning application designed for children practicing school subjects at home.

A child opens the application in the browser and is presented with a home page showing available subjects. They select a subject (e.g. Math), then pick a topic (e.g. Fractions), and choose between **Quiz** mode (interactive Q&A with immediate feedback) or **Learning** mode (step-by-step explanations with illustrations). The child enters answers and instantly sees whether they are correct, along with a running score.

The application also includes a database layer for storing vocabulary/flashcard data. Parents can later review stored results to understand the child's learning progress.

---

## User Stories

1. As a child, I want to choose a learning subject (e.g. Math) so that I can practice different subjects.
2. As a child, I want to select a topic within a subject (e.g. Fractions) so that I can focus on specific skills.
3. As a child, I want to answer questions and receive immediate feedback so that I know if my answer is correct.
4. As a child, I want to see my score update as I answer questions so that I can track how well I'm doing.
5. As a child, I want to read step-by-step explanations before taking a quiz so that I can prepare.
6. As a child, I want the exercises to be simple and interactive so that learning feels engaging and fun.
7. As a child, I want to continue practising with new questions so that I can improve my knowledge.
8. As a parent, I want the system to store vocabulary data so that it can be used for future exercises.
9. As a parent, I want the exercises to be simple and child-friendly so that my child can learn independently.

---

## Technology

- **Python 3.x**
- **NiceGUI** — browser-based UI framework
- **SQLAlchemy** — ORM for the SQLite database
- **SQLite** — local database (`learning.db`)
- Environment: macOS / GitHub Codespaces

---

## 📂 Repository Structure

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

## Application Architecture

### Routing

Routes are generated automatically at startup. For every `Subject` registered in `subjects/__init__.py`, `main.py` registers:

| URL pattern                | Page                         |
|----------------------------|------------------------------|
| `/`                        | Home — subject selector      |
| `/{subject}`               | Topic selector for a subject |
| `/{subject}/{topic}`       | Mode selector (Quiz / Learn) |
| `/{subject}/{topic}/quiz`  | Interactive quiz             |
| `/{subject}/{topic}/learn` | Step-by-step learning page   |
| `/{subject}/{topic}/paint` | Having fun with paintin      |

### Adding a New Subject

1. Create a new folder under `subjects/` (e.g. `subjects/science/`).
2. Define `Topic` subclasses (implement `generate_question`, optionally `learning_steps` / `learn_page_image`).
3. Define a `Subject` subclass with `name`, `icon`, `url_slug`, and `topics`.
4. Register the subject in `subjects/__init__.py` by adding it to the `SUBJECTS` list.

All pages and routes are created automatically — no changes to `main.py` needed.

---

## Current Subjects & Topics

TODO: updating is required after the last version of the code.
| Subject | Topic      | Quiz | Learning |
|---------|------------|------|----------|
| Math    | Fractions  | ✅   | ✅       |

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
   python Learning.py
   ```

### Launch

```bash
python main.py
```

The app will be available at **http://localhost:8081**.
