from __future__ import annotations
from typing import cast, Any
from nicegui import ui
from ui.pages.common import _apply_bg


def build_home_page() -> None:
    """Render the home / subject-selection page."""
    _apply_bg('/images/Home-p.png')
    from subjects import SUBJECTS
    with (ui.element("div").classes("page-content1")):
        ui.label("Choose a subject to start your learning adventure.").classes("text-body1")
        with ui.element("div").style(
            "display:flex;flex-wrap:wrap;justify-content:center;margin-top:70px;"
        ):
            for subject in SUBJECTS:
                dest = f"/{subject.url_slug}"
                card = ui.element("div").classes("circle-wrapper")
                cast(Any, card).on("click", lambda d=dest: ui.navigate.to(d))
                with card:
                 with ui.element("div").classes("circle-outer"):
                     with ui.element("div").classes("circle-inner"):
                        with ui.element("div").classes("subject-circle-content"):
                            ui.label(subject.name).classes("text-center subject-label")
                            ui.image(subject.icon).classes("subject-icon")
