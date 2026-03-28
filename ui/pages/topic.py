from __future__ import annotations
from nicegui import ui
from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header


def build_topic_mode_page(subject: Subject, topic: Topic) -> None:
    """Render the mode-selection page (Quiz / Learning) for any topic."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)
    with ui.element("div").classes("page-content1"):
        _build_page_header(
            f"/{subject.url_slug}", f"Back to {subject.name}",
            f"  {topic.name}", "What would you like to do?"
        )

        with ui.element("div").classes("mode-grid"):
            quiz_filter_dest = f"/{subject.url_slug}/{topic.name.lower()}/filter"
            with ui.element("div").classes("mode-card").on(
                "click", lambda d=quiz_filter_dest: ui.navigate.to(d)
            ):
                ui.html('<img src="/images/icons/test.svg" style="width:80px;height:80px;object-fit:contain;">')
                ui.label("Quiz").classes("mode-title")
                ui.label("Answer questions and test yourself!").classes("mode-desc")

            if topic.has_learning:
                learn_dest = f"/{subject.url_slug}/{topic.name.lower()}/learn"
                with ui.element("div").classes("mode-card").on(
                    "click", lambda d=learn_dest: ui.navigate.to(d)
                ):
                    ui.html('<img src="/images/icons/read.svg" style="width:80px;height:80px;object-fit:contain;">')
                    ui.label("Learning").classes("mode-title")
                    ui.label("Read step-by-step explanations.").classes("mode-desc")
            if topic.has_painting:
                draw_dest = f"/{subject.url_slug}/{topic.name.lower()}/paint"
                with ui.element("div").classes("mode-card").on(
                    "click", lambda d=draw_dest: ui.navigate.to(d)
                ):
                    ui.html('<img src="/images/icons/paint-palette.svg" style="width:80px;height:80px;object-fit:contain;">')
                    ui.label("Painting").classes("mode-title")
                    ui.label("Paint your understanding!").classes("mode-desc")
