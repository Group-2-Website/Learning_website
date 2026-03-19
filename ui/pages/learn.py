from __future__ import annotations

from nicegui import ui

from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header


def build_learn_page(subject: Subject, topic: Topic) -> None:
    """Render the learning/explanation page for any topic."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)
    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    quiz_dest = f"/{subject.url_slug}/{topic.name.lower()}/quiz"
    with ui.element("div").classes("page-content"):
        _build_page_header(
            back_dest, f"Back to {topic.name}",
            f"Learn how to deal with {topic.name}", ""
        )

        steps = topic.learning_steps()
        if steps:
            with ui.element("div").style(
                "display:grid;grid-template-columns:repeat(2,1fr);gap:16px;"
            ):
                for i, (title, explanation, expression, answer) in enumerate(steps, start=1):
                    visual = topic.step_visual_html(i - 1)
                    with ui.element("div").classes("mode-card").style("gap:8px;"):
                        if visual:
                            ui.html(visual)
                        ui.html(
                            f'<strong>{title}</strong>'
                        )
                        ui.label(explanation).style(
                            "margin-top:4px;color:#555;font-size:14px;line-height:1.6;text-align:center;"
                        )
                        if expression:
                            ui.label(f"Expression: {expression}").style(
                                "margin-top:4px;color:#333;font-size:13px;line-height:1.4;text-align:center;"
                            )
                        if answer:
                            ui.label(f"Answer: {answer}").style(
                                "margin-top:2px;color:#1a7f37;font-size:13px;line-height:1.4;text-align:center;"
                            )

        ui.button("Ready? Take the Quiz →", on_click=lambda d=quiz_dest: ui.navigate.to(d)) \
            .props("rounded") \
            .style(
                "background:linear-gradient(135deg,#60435F,#D67AB5);color:#f3f1f1;"
                "font-weight:700;margin-top:24px;"
            )
