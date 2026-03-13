from __future__ import annotations

from nicegui import ui

from models.subject import Subject
from models.topic import Topic
from subjects import SUBJECTS
from ui.builders import (add_global_css, build_topbar, build_home_page,
                         build_subject_topics_page, build_topic_mode_page,
                         build_quiz_page, build_learn_page, _apply_bg, _build_page_header)


@ui.page('/')
def home():
    add_global_css()
    build_topbar()
    build_home_page()



def _register_subject(subject):
    slug = subject.url_slug

    @ui.page(f'/{slug}')
    def subject_page(_s=subject):
        add_global_css()
        build_topbar()
        build_subject_topics_page(_s)

    for topic in subject.topics:
        _register_topic(subject, topic)


def _register_topic(subject, topic):
    slug       = subject.url_slug
    topic_slug = topic.name.lower()

    @ui.page(f'/{slug}/{topic_slug}')
    def topic_mode_page(_s=subject, _t=topic):
        add_global_css()
        build_topbar()
        build_topic_mode_page(_s, _t)

    @ui.page(f'/{slug}/{topic_slug}/quiz')
    def topic_quiz_page(_s=subject, _t=topic):
        add_global_css()
        build_topbar()
        build_quiz_page(_s, _t)

    @ui.page(f'/{slug}/{topic_slug}/results')
    def topic_results_page(score: int = 0, attempts: int = 0, _s=subject, _t=topic):
        add_global_css()
        build_topbar()
        build_quiz_results_page(_s, _t, score, attempts)

    if topic.has_learning:
        @ui.page(f'/{slug}/{topic_slug}/learn')
        def topic_learn_page(_s=subject, _t=topic):
            add_global_css()
            build_topbar()
            build_learn_page(_s, _t)


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
        _build_page_header(back_dest, f"Back to {topic.name}", f"📝  Quiz Results", "")

        with ui.element("div").classes("mode-card").style(
            "max-width:520px;margin:40px auto;gap:18px;align-items:center;"
        ):
            ui.label(msg).style(
                f"font-size:24px;font-weight:800;color:{color};text-align:center;"
            )
            ui.label(f"Your score: {score} / {attempts}").style(
                "font-size:36px;font-weight:800;color:#f97316;"
            )
            ui.label(f"{pct}%").style(
                f"font-size:48px;font-weight:900;color:{color};"
            )

            with ui.row().style("gap:16px;flex-wrap:wrap;justify-content:center;margin-top:12px;"):
                ui.button("🔄  Try Again", on_click=lambda: ui.navigate.to(quiz_dest)) \
                    .props("rounded") \
                    .style(
                        "background:linear-gradient(135deg,#60435F,#D67AB5);"
                        "color:white;font-weight:700;font-size:15px;"
                    )
                ui.button("🏠  Back to Topic", on_click=lambda: ui.navigate.to(back_dest)) \
                    .props("rounded") \
                    .style(
                        "background:#f3e8ff;color:#60435F;font-weight:700;font-size:15px;"
                    )
