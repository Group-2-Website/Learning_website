from __future__ import annotations
from nicegui import ui
from models.subject import Subject
from ui.pages.common import _apply_bg, _build_page_header


def build_subject_page(subject: Subject) -> None:
    """Render the subject page, where you can choose a topic of the subject"""
    url = subject.page_background_image()
    if url:
        _apply_bg(url)
    with ui.element("div").classes("page-content1"):
        _build_page_header("/", "Back", subject.name, "Pick a topic to practise.")

        with ui.element("div").style(
            "display:flex;flex-wrap:wrap;gap:36px;justify-content:center;margin-top:20px;"
        ):
            for topic in subject.topics:
                slug = topic.name.lower()
                dest = f"/{subject.url_slug}/{slug}"
                with ui.element("div").classes("circle-wrapper").on(
                    "click", lambda d=dest: ui.navigate.to(d)
                ):
                    with ui.element("div").classes("circle-outer"):
                        with ui.element("div").classes("circle-inner"):
                            ui.label(topic.name).classes("text-center")
