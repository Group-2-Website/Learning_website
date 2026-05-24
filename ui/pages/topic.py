from __future__ import annotations
from nicegui import ui
from core.subject import Subject
from core.topic import Topic
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
            if topic.has_learning:
                if topic.learn_filter_definitions():
                    learn_dest = f"/{subject.url_slug}/{topic.name.lower()}/learn-filter"
                else:
                    learn_dest = f"/{subject.url_slug}/{topic.name.lower()}/learn"
                with ui.element("div").classes("mode-card").on(
                        "click", lambda d=learn_dest: ui.navigate.to(d)
                ):
                    ui.image('/images/icons/read.svg').style('width:80px;height:80px;object-fit:contain;')
                    ui.label("Learning").classes("mode-title")
                    ui.label("Explore and learn at your own pace!").classes("mode-desc")

            quiz_filter_dest = f"/{subject.url_slug}/{topic.name.lower()}/filter"
            with ui.element("div").classes("mode-card").on(
                "click", lambda d=quiz_filter_dest: ui.navigate.to(d)
            ):
                ui.image('/images/icons/test.svg').style('width:80px;height:80px;object-fit:contain;')
                ui.label("Quiz").classes("mode-title")
                ui.label("Answer questions and test yourself!").classes("mode-desc")

            if topic.has_painting:
                draw_dest = f"/{subject.url_slug}/{topic.name.lower()}/paint"
                with ui.element("div").classes("mode-card").on(
                    "click", lambda d=draw_dest: ui.navigate.to(d)
                ):
                    ui.image('/images/icons/paint-palette.svg').style('width:80px;height:80px;object-fit:contain;')
                    ui.label("Painting").classes("mode-title")
                    ui.label("Get creative and draw what you learned!").classes("mode-desc")
