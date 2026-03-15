from __future__ import annotations

from typing import Any

from nicegui import ui

from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header


def build_quiz_page(subject: Subject, topic: Topic) -> None:
    """Render the interactive quiz page for any topic."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)

    filter_definitions = topic.quiz_filter_definitions()
    active_filters = topic.sanitize_quiz_filters(topic.default_quiz_filters())

    question_text, correct_answer = topic.generate_question(active_filters)
    state = {
        "question": question_text,
        "answer":   correct_answer,
        "score":    0,
        "attempts": 0,
        "checked":  False,
        "filters": dict(active_filters),
    }

    visual_holder: list = []
    answer_input_holder: list = []
    filter_buttons: dict[str, Any] = {}

    def _label_for(filter_name: str, value: str) -> str:
        options = filter_definitions.get(filter_name, [])
        for option_value, option_label in options:
            if option_value == value:
                return option_label
        return value

    def check_answer():
        if state["checked"]:
            return
        user = answer_input_holder[0].value.strip()
        is_correct, error = topic.check_answer(user, state["answer"])

        if error:
            feedback_label.text = error
            feedback_label.classes(replace="quiz-feedback-wrong")
            return  # invalid input - let the user fix it, don't count

        state["checked"] = True
        state["attempts"] += 1
        if is_correct:
            state["score"] += 1
            feedback_label.text = "Correct!"
            feedback_label.classes(replace="quiz-feedback-correct")
        else:
            feedback_label.text = f"Oops! The answer was {state['answer']}"
            feedback_label.classes(replace="quiz-feedback-wrong")
        score_label.text = f"Score: {state['score']} / {state['attempts']}"
        ui.timer(2.0, _advance, once=True)

    def show_hint():
        feedback_label.text = f" Hint: the answer is {state['answer']}"
        feedback_label.classes(replace="quiz-feedback-wrong")

    def _advance():
        """Load a new question without checking."""
        state["question"], state["answer"] = topic.generate_question(state["filters"])
        state["checked"] = False
        question_label.text = state["question"]
        answer_input_holder[0].value = ""
        answer_input_holder[0].run_method("focus")
        if visual_holder:
            visual_holder[0].content = topic.question_visual_html(state["question"])

    def apply_filter(filter_name: str, value: str) -> None:
        selected = dict(state["filters"])
        selected[filter_name] = value
        state["filters"] = topic.sanitize_quiz_filters(selected)

        if filter_name in filter_buttons:
            pretty_name = filter_name.replace("_", " ").title()
            selected_label = _label_for(filter_name, state["filters"][filter_name])
            filter_buttons[filter_name].text = f"{pretty_name}: {selected_label}"

        selected_text = ", ".join(
            f"{name.replace('_', ' ').title()}: {_label_for(name, value)}"
            for name, value in state["filters"].items()
        )
        feedback_label.text = f"Filters: {selected_text}"
        feedback_label.classes(replace="quiz-feedback-wrong")
        _advance()

    def next_question():
        """Check current answer then advance."""
        check_answer()
        _advance()

    def finish_quiz():
        check_answer()
        score = state["score"]
        attempts = state["attempts"]
        dest = (
            f"/{subject.url_slug}/{topic.name.lower()}/results"
            f"?score={score}&attempts={attempts}"
        )
        ui.navigate.to(dest)

    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    with ui.element("div").classes("page-content1"):
        _build_page_header(back_dest, f"Back to {topic.name}", f"  {topic.name} Quiz", "")

        with ui.element("div").classes("mode-card").style("max-width:560px;margin:0;"):
            if filter_definitions:
                with ui.row().style("gap:8px;align-items:center;justify-content:center;flex-wrap:wrap;"):
                    for filter_name, options in filter_definitions.items():
                        if not options:
                            continue
                        pretty_name = filter_name.replace("_", " ").title()
                        current_value = state["filters"].get(filter_name, options[0][0])
                        button = ui.button(f"{pretty_name}: {_label_for(filter_name, current_value)}").props("rounded outline")
                        filter_buttons[filter_name] = button
                        with button:
                            with ui.menu():
                                for option_value, option_label in options:
                                    ui.menu_item(
                                        option_label,
                                        on_click=lambda fn=filter_name, ov=option_value: apply_filter(fn, ov),
                                    )

            score_label = ui.label("Score: 0").style(
                "color:#D67AB5;font-weight:700;font-size:15px;"
            )

            question_label = ui.label(state["question"]).classes("quiz-question")

            initial_visual = topic.question_visual_html(state["question"])
            if initial_visual:
                visual_holder.append(ui.html(initial_visual))

            answer_input = (
                ui.input(placeholder="Your Answer")
                .props("outlined rounded")
                .style("width:260px;font-size:18px;")
                .on("keydown.enter", next_question)
            )
            answer_input_holder.append(answer_input)

            feedback_label = ui.label("").classes("quiz-feedback-wrong")

            with ui.row().style("gap:12px;flex-wrap:wrap;justify-content:center;"):
                ui.button("Submit ✓", on_click=check_answer) \
                    .props("rounded") \
                    .style("background:linear-gradient(135deg,#60435F,#D67AB5);color:white;font-weight:700;")
                ui.button("Skip →", on_click=next_question) \
                    .props("rounded") \
                    .style("background:#f3e8ff;color:#60435F;font-weight:700;")
                ui.button("   Hint", on_click=show_hint) \
                    .props("rounded") \
                    .classes("btn-svg-icon") \
                    .style("--icon: url('/images/icons/machine-learning.svg');background:#fffbe6;color:#b45309;font-weight:700;")
                ui.button("Finish Quiz", on_click=finish_quiz) \
                    .props("rounded") \
                    .style("background:#fee2e2;color:#7f1d1d;font-weight:700;")
