from __future__ import annotations

from nicegui import ui

from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header


def build_quiz_page(subject: Subject, topic: Topic, initial_filters: dict[str, str] | None = None) -> None:
    """Render the interactive quiz page for any topic."""
    feedback_seconds = 1.4
    url = topic.page_background_image()
    if url:
        _apply_bg(url)

    is_mc = getattr(topic, "quiz_mode", "text") == "multiple_choice"

    active_filters = topic.sanitize_quiz_filters(initial_filters or topic.default_quiz_filters())
    num_questions = int(active_filters.get("number of questions", 10))

    # ── Generate the first question ─────────────────────────────────────
    if is_mc:
        question_text, options, correct_answer = topic.generate_mc_question(active_filters)
    else:
        question_text, correct_answer = topic.generate_question(active_filters)
        options = []

    state = {
        "question": question_text,
        "answer":   correct_answer,
        "options":  list(options),
        "score":    0,
        "attempts": 0,
        "checked":  False,
        "filters":  dict(active_filters),
        "asked":    0,
        "num_questions": num_questions,
        "feedback_token": 0,
        "selected_option": "",
    }

    visual_holder: list = []
    answer_input_holder: list = []
    mc_buttons_holder: list = []       # holds the container for MC option buttons

    def show_feedback(message: str, style_class: str) -> None:
        """Show feedback briefly and clear it after a short delay."""
        state["feedback_token"] += 1
        token = state["feedback_token"]
        feedback_label.text = message
        feedback_label.classes(replace=style_class)

        def clear_feedback_if_latest() -> None:
            if state["feedback_token"] == token:
                feedback_label.text = ""

        ui.timer(feedback_seconds, clear_feedback_if_latest, once=True)

    # ── Multiple-choice helpers ─────────────────────────────────────────
    def _select_option(option_text: str) -> None:
        """Called when a user clicks an MC option button."""
        if state["checked"]:
            return
        state["selected_option"] = option_text
        check_answer()

    def _rebuild_mc_buttons() -> None:
        """Re-render the multiple-choice option buttons inside their container."""
        if not mc_buttons_holder:
            return
        container = mc_buttons_holder[0]
        container.clear()
        with container:
            for opt in state["options"]:
                ui.button(opt, on_click=lambda o=opt: _select_option(o)) \
                    .props("rounded outline") \
                    .style(
                    "width:100%;text-align:left;font-size:16px;font-weight:600;"
                    "color:#60435F;border:2px solid #D67AB5;background:white;"
                )

    # ── Core quiz logic ─────────────────────────────────────────────────
    def check_answer():
        if state["checked"]:
            return

        if is_mc:
            user = state["selected_option"]
        else:
            user = answer_input_holder[0].value.strip()

        is_correct, error = topic.check_answer(user, state["answer"])

        if error:
            show_feedback(error, "quiz-feedback-wrong")
            return

        state["checked"] = True
        state["attempts"] += 1
        if is_correct:
            state["score"] += 1
            show_feedback("Correct! ", "quiz-feedback-correct")
        else:
            show_feedback(f"Oops! The answer was {state['answer']}", "quiz-feedback-wrong")
        score_label.text = f"Score: {state['score']} / {state['attempts']}"
        ui.timer(feedback_seconds, _advance, once=True)

    def show_hint():
        show_feedback(f" Hint: the answer is {state['answer']}", "quiz-feedback-wrong")

    def _advance():
        """Load a new question without checking."""
        state["asked"] += 1
        if state["asked"] >= state["num_questions"]:
            finish_quiz()
            return

        if is_mc:
            state["question"], state["options"], state["answer"] = topic.generate_mc_question(state["filters"])
        else:
            state["question"], state["answer"] = topic.generate_question(state["filters"])
            state["options"] = []

        state["checked"] = False
        state["selected_option"] = ""
        question_label.text = state["question"]

        if is_mc:
            _rebuild_mc_buttons()
        else:
            answer_input_holder[0].value = ""
            answer_input_holder[0].run_method("focus")

        if visual_holder:
            visual_holder[0].content = topic.question_visual_html(state["question"])

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
            score_label = ui.label("Score: 0").style(
                "color:#D67AB5;font-weight:700;font-size:15px;"
            )

            question_label = ui.label(state["question"]).classes("quiz-question")

            initial_visual = topic.question_visual_html(state["question"])
            if initial_visual:
                visual_holder.append(ui.html(initial_visual))

            if is_mc:
                # ── Multiple-choice option buttons ──────────────────────
                mc_container = ui.column().style("gap:10px;width:100%;max-width:420px;")
                mc_buttons_holder.append(mc_container)
                _rebuild_mc_buttons()
            else:
                # ── Text input ──────────────────────────────────────────
                answer_input = (
                    ui.input(placeholder="Your Answer")
                    .props("outlined rounded")
                    .style("width:260px;font-size:18px;")
                    .on("keydown.enter", check_answer)
                )
                answer_input_holder.append(answer_input)

            feedback_label = ui.label("").classes("quiz-feedback-wrong")

            with ui.row().style("gap:12px;flex-wrap:wrap;justify-content:center;"):
                if not is_mc:
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
