from __future__ import annotations

from nicegui import ui

from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header


def build_quiz_results_page(subject: Subject, topic: Topic, score: int, attempts: int) -> None:
    """Render the quiz results page."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)

    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    quiz_dest = f"/{subject.url_slug}/{topic.name.lower()}/quiz"

    pct = round((score / attempts) * 100) if attempts > 0 else 0

    if pct == 100:
        msg, color = "Perfect score! Amazing!", "#22c55e"
    elif pct >= 70:
        msg, color = "Great job! Keep it up!", "#f97316"
    elif pct >= 40:
        msg, color = "Good effort! Keep practising.", "#60a5fa"
    else:
        msg, color = "Keep going — practice makes perfect!", "#ec4899"

    with ui.element("div").classes("page-content1"):
        _build_page_header(back_dest, f"Back to {topic.name}", f" Quiz Results", "")



        with ui.element("div").classes("mode-card").style(
            "max-width:520px;margin:40px auto;gap:18px;align-items:center;"
        ):
            ui.label(msg).style(
                f"font-size:24px;font-weight:800;color:#f97316;text-align:center;"
            )
            ui.label(f"Your score: {score} / {attempts}").style(
                "font-size:36px;font-weight:800;color:#60435F;"
            )
            ui.label(f"{pct}%").style(
                f"font-size:48px;font-weight:900;color:#60435F;"
            )

            with ui.row().style("gap:16px;flex-wrap:wrap;justify-content:center;margin-top:12px;"):
                ui.button("🔄  Try Again", on_click=lambda: ui.navigate.to(quiz_dest)) \
                    .props("rounded") \
                    .style(
                        "background:linear-gradient(135deg,#60435F,#D67AB5);"
                        "color:white;font-weight:700;font-size:15px;"
                    )
                ui.button("Back to Topic", on_click=lambda: ui.navigate.to(back_dest)) \
                    .props("rounded") \
                    .classes("btn-svg-icon") \
                    .style(
                        "--icon: url('/images/icons/daycare.svg'); background:#f3e8ff;color:#60435F;font-weight:700;font-size:15px;"
                    )
