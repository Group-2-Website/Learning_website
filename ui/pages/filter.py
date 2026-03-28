from __future__ import annotations

from urllib.parse import urlencode

from nicegui import ui

from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header


def build_quiz_filter_page(subject: Subject, topic: Topic) -> None:
    """Render the filter-selection page shown before starting a quiz."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)

    filter_definitions = topic.quiz_filter_definitions()
    defaults = topic.default_quiz_filters()
    selected: dict[str, str] = {
        name: defaults.get(name, options[0][0])
        for name, options in filter_definitions.items()
    }

    def _start_quiz() -> None:
        base = f"/{subject.url_slug}/{topic.name.lower()}/quiz"
        if selected:
            base += "?" + urlencode(selected)
        ui.navigate.to(base)

    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    with ui.element("div").classes("page-content1"):
        _build_page_header(
            back_dest, f"Back to {topic.name}",
            f"  {topic.name} Quiz", "Choose your settings",
        )

        with ui.element("div").classes("mode-card").style(
            "width:800px;margin:0 auto;"
        ):
            conditional_selects: dict[str, ui.select] = {}

            def _on_change(filter_name: str, value) -> None:
                selected[filter_name] = value
                _update_visibility()

            def _update_visibility() -> None:
                show_row = (selected.get("operation") == "mul"
                            and selected.get("difficulty") == "easy")
                if "row" in conditional_selects:
                    conditional_selects["row"].set_visibility(show_row)

            for filter_name, options in filter_definitions.items():
                if not options:
                    continue
                pretty_name = filter_name.replace("_", " ").title()
                options_map = {value: label for value, label in options}
                sel = ui.select(
                    options=options_map,
                    value=selected[filter_name],
                    label=pretty_name,
                    on_change=lambda e, fn=filter_name: _on_change(fn, e.value),
                ).props("outlined rounded color=purple").style(
                    "width:90%;font-size:16px;margin-top:12px;"
                )
                if filter_name == "row":
                    conditional_selects["row"] = sel

            _update_visibility()

            ui.button("Start Quiz ", on_click=_start_quiz) \
                .props("rounded size=lg") \
                .classes("btn-svg-icon") \
                .style( "--icon: url('/images/icons/rocket.svg');font-weight:700;")\
                .style(

                        "background:linear-gradient(135deg,#60435F,#D67AB5);"
                        "color:white;font-weight:700;font-size:18px;"
                        "padding:12px 40px;margin-top:24px;"
                    )

