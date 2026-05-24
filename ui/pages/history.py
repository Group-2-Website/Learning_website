from __future__ import annotations

from nicegui import ui

from core.records import QuizAttemptRecord
from core.subject import Subject
from core.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header


def build_quiz_history_page(subject: Subject, topic: Topic, limit: int = 50) -> None:
    """Standalone page listing previous quiz attempts (score & mistakes)."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)

    back_dest = f"/{subject.url_slug}/{topic.name.lower()}/filter"

    try:
        attempts: list[QuizAttemptRecord] = topic.list_quiz_attempts(
            subject_name=subject.name,
            limit=limit,
        )
    except Exception as exc:  # pragma: no cover
        print(f"[history] could not load quiz history: {exc}")
        attempts = []

    with ui.element("div").classes("page-content1"):
        _build_page_header(
            back_dest, "Back to Filters",
            f"  {topic.name} — Previous Attempts",
            "Your past scores and mistakes",
        )

        with ui.element("div").classes("mode-card").style(
            "width:800px;margin:0 auto;"
        ):
            if not attempts:
                ui.label(
                    "No quiz attempts yet — finish a quiz to see your history here."
                ).style("color:#7a6b86;font-size:16px;")
                return

            rows = [
                {
                    "when": a.created_at.strftime("%Y-%m-%d %H:%M"),
                    "score": f"{a.score} / {a.attempts}",
                    "hints": a.hints_used,
                    "percent": (
                        f"{round((a.score / a.attempts) * 100)}%" if a.attempts else "—"
                    ),
                }
                for a in attempts
            ]
            columns = [
                {"name": "when", "label": "Date", "field": "when", "align": "left"},
                {"name": "score", "label": "Score", "field": "score", "align": "center"},
                {"name": "hints", "label": "Hints used", "field": "hints", "align": "center"},
                {"name": "percent", "label": "%", "field": "percent", "align": "center"},
            ]
            ui.table(columns=columns, rows=rows, row_key="when").props(
                "flat bordered"
            ).style("width:100%;background:white;border-radius:12px;")


