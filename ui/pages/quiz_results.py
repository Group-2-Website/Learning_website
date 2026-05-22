from __future__ import annotations
from nicegui import ui
from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header


def calculate_quiz_result(score: int, attempts: int) -> tuple[int, float, str, str]:
    """Return (percentage, stars, message, color) for a quiz result.

    Stars range from 0–5 in 0.5 increments.
    """
    pct = round((score / attempts) * 100) if attempts > 0 else 0
    stars = round(pct / 20 * 2) / 2  # 0–5 stars in 0.5 steps

    if pct == 100:
        msg, color = "Perfect score! Amazing!", "#bde0c9"
    elif pct >= 70:
        msg, color = "Great job! Keep it up!", "#b9bd60"
    elif pct >= 40:
        msg, color = "Good effort! Keep practising.", "#f28a7a"
    else:
        msg, color = "Keep going — practice makes perfect!", "#fc4900"

    return pct, stars, msg, color


def build_quiz_results_page(subject: Subject, topic: Topic, score: int, attempts: int) -> None:
    """Render the quiz results page."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)

    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    quiz_dest = f"/{subject.url_slug}/{topic.name.lower()}/quiz"

    pct, stars, msg, color = calculate_quiz_result(score, attempts)

    with ui.element("div").classes("page-content1"):
        _build_page_header(back_dest, f"Back to {topic.name}", f" Quiz Results", "")



        with ui.element("div").classes("mode-card").style(
            "width:800px;margin:40px auto;gap:18px;align-items:center;"
        ):
            with ui.column().classes("items-center").style("margin-top:20px;"):
                ui.label(f"YOU WON {stars} STAR(S)").classes("stars-title")

                with ui.element("div").classes("stars-banner"):
                    full = int(stars)
                    has_half = (stars - full) >= 0.5
                    for i in range(5):
                        if i < full:
                            star_class = "star filled"
                        elif i == full and has_half:
                            star_class = "star half"
                        else:
                            star_class = "star"
                        ui.element("div").classes(star_class).style(f"animation-delay:{i * 0.1}s")

            ui.label(msg).style(
                f"font-size:24px;font-weight:800;color:{color};text-align:center;"
            )
            ui.label(f"Your score: {score} / {attempts}").style(
                "font-size:36px;font-weight:800;color:#60435F;"
            )
            ui.label(f"{pct}%").style(
                f"font-size:48px;font-weight:900;color:#60435F;"
            )

            with ui.row().style("gap:18px;flex-wrap:wrap;justify-content:center;margin-top:8px;"):
                ui.button("Try Again", on_click=lambda: ui.navigate.to(quiz_dest)) \
                    .props('rounded flat color="" icon="replay"') \
                    .style(
                    "background:#bb93c4 !important;"
                    "color:white !important;font-weight:700;font-size:15px;"
                )
                ui.button("   Back to Topic", on_click=lambda: ui.navigate.to(back_dest)) \
                    .props('rounded flat color=""') \
                    .classes("btn-svg-icon") \
                    .style(
                    "--icon: url('/images/icons/home.svg'); background:#bb93c4 !important;color:white !important;font-weight:700;font-size:15px;justify-content:center;"
                )