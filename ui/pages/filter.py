from __future__ import annotations

from urllib.parse import urlencode

from nicegui import ui

from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header


def _build_filter_page(
    subject: Subject,
    topic: Topic,
    filters,
    mode: str,
    header_title: str,
    header_subtitle: str,
    button_label: str,
    button_icon: str,
) -> tuple[dict[str, str], dict[str, ui.select]]:
    """Shared skeleton for quiz/learn filter pages. Returns (selected, widgets)."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)

    selected: dict[str, str] = {fd.name: fd.default for fd in filters}

    def _start() -> None:
        base = f"/{subject.url_slug}/{topic.name.lower()}/{mode}"
        if selected:
            base += "?" + urlencode(selected)
        ui.navigate.to(base)

    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    widgets: dict[str, ui.select] = {}

    with ui.element("div").classes("page-content1"):
        _build_page_header(
            back_dest, f"Back to {topic.name}",
            header_title, header_subtitle,
        )

        with ui.element("div").classes("mode-card").style(
            "width:800px;margin:0 auto;"
        ):
            for fd in filters:
                if not fd.options:
                    continue
                pretty_name = fd.name.replace("_", " ").title()
                sel = ui.select(
                    options=fd.options_map,
                    value=selected[fd.name],
                    label=pretty_name,
                    on_change=lambda e, fn=fd.name: selected.update({fn: e.value}),
                ).props("outlined rounded color=purple").style(
                    "width:90%;font-size:16px;margin-top:12px;"
                )
                widgets[fd.name] = sel

            ui.button(button_label, on_click=_start) \
                .props("rounded size=lg unelevated flat no-caps") \
                .classes("btn-svg-icon start-quiz-btn") \
                .style(
                    f"--icon: url('/images/icons/{button_icon}');"
                    "font-weight:700;font-size:18px;"
                    "padding:12px 40px;margin-top:24px;"
                )

    return selected, widgets


def build_quiz_filter_page(subject: Subject, topic: Topic) -> None:
    """Render the filter-selection page shown before starting a quiz."""
    filters = topic.quiz_filter_definitions()

    selected, widgets = _build_filter_page(
        subject, topic, filters,
        mode="quiz",
        header_title=f"  {topic.name} Quiz",
        header_subtitle="Choose your settings",
        button_label="Start Quiz ",
        button_icon="rocket.svg",
    )

    # Quiz-specific: conditional visibility for "row" select
    if "row" in widgets:
        def _update_visibility() -> None:
            show_row = (selected.get("operation") == "mul"
                        and selected.get("difficulty") == "easy")
            widgets["row"].set_visibility(show_row)

        # Re-wire on_change to also update visibility
        for name, sel in widgets.items():
            sel.on_value_change(lambda e, fn=name: (
                selected.update({fn: e.value}),
                _update_visibility(),
            ))

        _update_visibility()


def build_learn_filter_page(subject: Subject, topic: Topic) -> None:
    """Render the filter-selection page shown before starting learning."""
    filters = topic.learn_filter_definitions()

    _build_filter_page(
        subject, topic, filters,
        mode="learn",
        header_title=f"  {topic.name} Learning",
        header_subtitle="Choose your topic",
        button_label="Start Learning",
        button_icon="read.svg",
    )
