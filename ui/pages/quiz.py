from __future__ import annotations

from nicegui import ui

from models.quiz_card import QuizCard
from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header, audio_button_html, add_audio_player_script


def _quiz_button(label: str, on_click, *, bg: str, color: str, extra_classes: str = "", extra_style: str = "") -> None:
    btn = ui.button(label, on_click=on_click).props("rounded")
    if extra_classes:
        btn.classes(extra_classes)
    btn.style(f"background:{bg};color:{color};font-weight:700;{extra_style}")


def build_quiz_page(subject: Subject, topic: Topic, initial_filters: dict[str, str] | None = None) -> None:
    """Render the interactive quiz page for any topic."""
    feedback_seconds = 1.4
    url = topic.page_background_image()
    if url:
        _apply_bg(url)

    _quiz_type_filter = (initial_filters or {}).get("quiz_type", "")
    is_mc = (getattr(topic, "quiz_mode", "text") == "multiple_choice"
             or _quiz_type_filter == "article")

    active_filters = topic.sanitize_quiz_filters(initial_filters or {})
    num_questions = topic.get_num_questions(active_filters)

    # ── Unified question generator ──────────────────────────────────────
    def _generate_question(filters) -> QuizCard:
        """Return a QuizCard regardless of quiz mode."""
        return topic.get_question(filters)

    card = _generate_question(active_filters)

    state = {
        "card":     card,
        "score":    0,
        "attempts": 0,
        "checked":  False,
        "filters":  dict(active_filters),
        "asked":    0,
        "num_questions": num_questions,
        "feedback_token": 0,
        "selected_option": "",
        "hint_revealed": 0,
    }

    visual_holder: list = []
    answer_input_holder: list = []
    mc_buttons_holder: list = []
    audio_btn_holder: list = []

    def _update_audio_button() -> None:
        """Show or hide the audio button based on the current question's audio_url."""
        if not audio_btn_holder:
            return
        container = audio_btn_holder[0]
        container.clear()
        html = audio_button_html(state["card"].audio_url)
        if html:
            with container:
                ui.html(html, sanitize=False)

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

    # ── User-input helpers ──────────────────────────────────────────────
    def _get_user_answer() -> str:
        if is_mc:
            return state["selected_option"]
        return answer_input_holder[0].value.strip()

    def _select_option(option_text: str) -> None:
        if state["checked"]:
            return
        state["selected_option"] = option_text
        check_answer()

    def _rebuild_mc_buttons() -> None:
        if not mc_buttons_holder:
            return
        container = mc_buttons_holder[0]
        container.clear()
        colors = [
            ("#D1FAE5", "#A7F3D0"),  # light green
            ("#FEF9C3", "#FDE68A"),  # light yellow
            ("#FFE4E6", "#FECDD3"),  # light pink
        ]
        with container:
            for i, opt in enumerate(state["card"].options):
                c1, c2 = colors[i % len(colors)]
                ui.button(
                    opt,
                    on_click=lambda o=opt: _select_option(o)
                ).props("unelevated no-caps").style(
                    f"width:100%;font-size:28px;font-weight:900;color:#4A3F55 !important;"
                    f"padding:22px 48px;border-radius:25px;border:none;"
                    f"background:linear-gradient(135deg,{c1},{c2}) !important;"
                    f"box-shadow:0 10px 0 rgba(0,0,0,0.12);"
                    f"transition:all 0.15s ease;"
                ).classes("mc-btn")

    def _reset_input() -> None:
        """Clear the answer area after advancing to a new question."""
        state["checked"] = False
        state["selected_option"] = ""
        if is_mc:
            _rebuild_mc_buttons()
        else:
            answer_input_holder[0].value = ""
            answer_input_holder[0].run_method("focus")

    # ── Core quiz logic ─────────────────────────────────────────────────
    def check_answer():
        if state["checked"]:
            return

        is_correct, error = topic.check_answer(_get_user_answer(), state["card"].correct_answer)

        if error:
            show_feedback(error, "quiz-feedback-wrong")
            return

        state["checked"] = True
        state["attempts"] += 1
        if is_correct:
            state["score"] += 1
            show_feedback("Correct! ", "quiz-feedback-correct")
        else:
            show_feedback(f"Oops! The answer was {state['card'].correct_answer}", "quiz-feedback-wrong")
        score_label.text = f"Score: {state['score']} / {state['attempts']}"
        ui.timer(feedback_seconds, _advance, once=True)

    def show_hint():
        answer = state["card"].correct_answer
        revealed = state["hint_revealed"]
        if revealed >= len(answer):
            show_feedback(f" Hint: {answer}", "quiz-feedback-hint")
            return
        revealed += 1
        state["hint_revealed"] = revealed
        hint_text = answer[:revealed] + " _" * (len(answer) - revealed)
        show_feedback(f" Hint: {hint_text}  ({len(answer)} character )", "quiz-feedback-hint")

    def _advance():
        """Load a new question."""
        state["asked"] += 1
        if state["asked"] >= state["num_questions"]:
            finish_quiz()
            return

        state["card"] = _generate_question(state["filters"])
        state["hint_revealed"] = 0
        question_label.text = state["card"].question
        type_hint_label.text = state["card"].type_hint
        _update_audio_button()
        _reset_input()

        if visual_holder:
            visual_holder[0].content = topic.question_visual_html(state["card"].question)

    def next_question():
        state["checked"] = True
        _advance()

    def finish_quiz():
        check_answer()
        dest = (
            f"/{subject.url_slug}/{topic.name.lower()}/results"
            f"?score={state['score']}&attempts={state['attempts']}"
        )
        ui.navigate.to(dest)

    _quiz_title = "Choose the correct Article" if _quiz_type_filter == "article" else f"  {topic.name} Quiz"
    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    with ui.element("div").classes("page-content1"):
        _build_page_header(back_dest, f"Back to {topic.name}", _quiz_title, "")

        with ui.element("div").classes("mode-card").style("max-width:900px;margin:0;"):
            score_label = ui.label("Score: 0").style(
                "color:#D67AB5;font-weight:700;font-size:15px;"
            )

            question_label = ui.label(state["card"].question).classes("quiz-question")

            type_hint_label = ui.label(state["card"].type_hint).style(
                "font-size:18px;color:#D67AB5;font-weight:600;text-align:center;width:100%;"
            )

            # ── Audio listen button ─────────────────────────────────────
            audio_btn_holder.append(
                ui.element("div").style("display:flex;justify-content:center;margin:6px 0;")
            )
            _update_audio_button()

            initial_visual = topic.question_visual_html(state["card"].question)
            if initial_visual:
                visual_holder.append(ui.html(initial_visual, sanitize=False))

            if is_mc:
                mc_buttons_holder.append(
                    ui.column().style("gap:20px;width:100%;max-width:760px;")
                )
                _rebuild_mc_buttons()
            else:
                answer_input_holder.append(
                    ui.input(placeholder="Your Answer")
                    .props("outlined rounded")
                    .style("width:260px;font-size:18px;")
                    .on("keydown.enter", check_answer)
                )

            feedback_label = ui.label("").classes("quiz-feedback-wrong")

            with ui.row().style("gap:12px;flex-wrap:wrap;justify-content:center;"):
                if not is_mc:
                    _quiz_button("Submit ", check_answer,
                                 bg="linear-gradient(135deg,#60435F,#D67AB5)", color="white")
                _quiz_button("Skip ", next_question,
                             bg="#f3e8ff", color="#60435F")
                _quiz_button("   Hint", show_hint,
                             bg="#fffbe6", color="#b45309",
                             extra_classes="btn-svg-icon",
                             extra_style="--icon: url('/images/icons/machine-learning.svg');")
                _quiz_button("Finish Quiz", finish_quiz,
                             bg="#fee2e2", color="#7f1d1d")

        add_audio_player_script()
        ui.add_head_html("""
        <style>
        .mc-btn:hover {
            transform: translateY(-4px) scale(1.03);
            box-shadow: 0 12px 0 rgba(0,0,0,0.18);
        }
        .mc-btn:active {
            transform: translateY(3px) scale(0.97);
            box-shadow: 0 4px 0 rgba(0,0,0,0.12);
        }
        </style>
        """)


