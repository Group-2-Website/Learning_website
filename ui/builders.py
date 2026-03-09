from __future__ import annotations

from nicegui import ui

from models.subject import Subject
from models.topic import Topic


def build_topbar():
    """Render the shared top navigation bar."""
    with ui.element("div").classes("topbar w-full"):
        with ui.element("div").classes("wrap h-full flex items-center px-8"):
            with ui.element("div").classes("logo-box"):
                with ui.element("div").classes("logo-squares"):
                    ui.element("div").classes("sq1")
                    ui.element("div").classes("sq2")
                    ui.element("div").classes("sq3")
                    ui.element("div").classes("sq4")
                with ui.element("div").style("cursor:pointer;").on("click", lambda: ui.navigate.to("/")):
                    ui.label("KidsLearn").classes("brand-title")
                    ui.label("Learning with fun").classes("brand-sub")


def add_global_css():
    ui.add_head_html("""
    <style>

      body {
        background: linear-gradient(180deg, #eef8ff 0%, #fdf6ff 100%);
        background: #e0e0e047;
      }

      .topbar {
        background: linear-gradient(90deg,#FF8A8A,#FFB6C1,#FFD6A5,#BDE0FE,#A8E6CF);
        height: 250px;
        width: 110vw;
        margin-left: calc(-1 * var(--nicegui-default-padding));
        margin-right: calc(-1 * var(--nicegui-default-padding));
        margin-top: calc(-1 * var(--nicegui-default-padding));
        box-sizing: border-box;
        padding-left: var(--nicegui-default-padding);
        padding-right: var(--nicegui-default-padding);
      }

      .wrap {
        padding: 0 40px;
      }

      .logo-box {
        display:flex;
        align-items:center;
        gap:12px;
        color:white;
      }

      .logo-squares {
        width:100px;
        height:100px;
        display:grid;
        grid-template-columns:repeat(2, 47px);
        grid-template-rows:repeat(2, 47px);
        gap:6px;
      }

      .sq1 { background:#22c55e; border-radius:4px; }
      .sq2 { background:#f97316; border-radius:4px; }
      .sq3 { background:#60a5fa; border-radius:4px; }
      .sq4 { background:#ec4899; border-radius:4px; }

      .brand-title {
        font-weight:800;
        font-size:60px;
        line-height:1.1;
        white-space:pre-line;
      }
      .text-body1 {
        color:#60435F;
        font-weight:950;
        font-size:34px;
        margin-top:2px;
      }
      .brand-sub {
        color:#32a852;
        font-weight:700;
        margin-top:0.5px;
        font-size:20.5px;
      }

      /* ── Shared subject / topic circles ── */
      .circle-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 14px;
      }

      .circle-outer {
        width: 330px;
        height: 330px;
        border-radius: 50%;
        background: linear-gradient(150deg, #FF8A8A, #f3f1f1);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: transform .2s ease, box-shadow .2s ease;
        box-shadow: 0 4px 14px rgba(96,67,95,0.18);
      }

      .circle-outer:hover {
        transform: scale(1.07);
        box-shadow: 0 8px 28px rgba(96,67,95,0.28);
      }

      .circle-inner {
        width: 255px;
        height: 255px;
        border-radius: 50%;
        border: 5px solid white;
        background: #f3f1f1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        font-weight: 700;
        color: #D67AB5;
        text-align: center;
        padding: 10px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
      }

      /* ── Page layout ── */
      .page-content {
        max-width: 900px;  /* ← max width of content on all pages  */
        margin: 40px auto; /* ← top gap from topbar on all pages   */
        padding: 0 px;   /* ← left/right edge gap on all pages   */
      }

      .page-title {
        font-size: 38px;
        font-weight: 800;
        color: #60435F;
        margin-bottom: 8px;
      }

      .page-subtitle {
        color: #734962;
        font-size: 22px;
        margin-bottom: 36px;
      }

      /* ── Mode cards (Quiz / Learning) ── */
      .mode-grid {
        display: flex;
        gap: 28px;
        flex-wrap: wrap;
        margin-top: 32px;
      }

      .mode-card {
        flex: 1;
        min-width: 600px;
        min-height:300px;
        background: #f3f1f1;
        border-radius: 35px;
        border: 2px solid #60435f99;
        padding: 36px 24px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 14px;
        cursor: pointer;
        box-shadow: 0 4px 14px rgba(96,67,95,0.10);
        transition: transform .18s ease, box-shadow .18s ease;
      }

      .mode-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(96,67,95,0.20);
      }

      .mode-icon { font-size: 48px; }

      .mode-title {
        font-size: 20px;
        font-weight: 800;
        color: #60435F;
      }

      .mode-desc {
        font-size: 13px;
        color: #888;
        text-align: center;
      }

      /* ── Learning steps ── */
      .step-number {
        display: inline-block;
        background: linear-gradient(135deg,#60435F,#D67AB5);
        color: #f3f1f1;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        line-height: 28px;
        text-align: center;
        font-weight: 700;
        margin-right: 10px;
        font-size: 14px;
      }

      /* ── Quiz ── */
      .quiz-question {
        font-size: 36px;
        font-weight: 800;
        color: #60435F;
        text-align: center;
      }

      .quiz-feedback-correct {
        color: #22c55e;
        font-weight: 700;
        font-size: 18px;
      }

      .quiz-feedback-wrong {
        color: #ef4444;
        font-weight: 700;
        font-size: 18px;
      }

      .back-btn {
        display: inline-flex;
        align-items: center;
        gap: 1px;
        color: #D67AB5;
        font-weight: 700;
        cursor: pointer;
        font-size: 20px;
        margin-bottom: 2px;
      }

      .back-btn:hover { text-decoration: underline; }
    </style>
    """)


def _apply_bg(url: str) -> None:
    """Inject a semi-transparent background image for any page."""
    ui.add_head_html(f"""
    <style>
      body {{
        background-image: url('{url}') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
      }}
      body::before {{
        content: '';
        position: fixed;
        inset: 0;
        background: rgba(255,255,255,0.85);
        z-index: 0;
        pointer-events: none;
      }}
    </style>
    """)


def _build_page_header(back_dest: str, back_label: str, title: str, subtitle: str) -> None:
    """Render the shared back-button + page title + subtitle header."""
    with ui.element("div").classes("back-btn").on("click", lambda d=back_dest: ui.navigate.to(d)):
        ui.label(f"← {back_label}")
    ui.label(title).classes("page-title")
    if subtitle:
        ui.label(subtitle).classes("page-subtitle")


def build_home_page() -> None:
    """Render the home / subject-selection page."""
    _apply_bg('/images/Home_page.png')
    from subjects import SUBJECTS
    with ui.element("div").classes("page-content"):
        ui.label("Choose a subject to start your learning adventure.").classes("text-body1")
        with ui.element("div").style(
            "display:flex;flex-wrap:wrap;justify-content:center;margin-top:90px;"
        ):
            for subject in SUBJECTS:
                dest = f"/{subject.url_slug}"
                with ui.element("div").classes("circle-wrapper").on(
                    "click", lambda d=dest: ui.navigate.to(d)
                ):
                    with ui.element("div").classes("circle-outer"):
                        with ui.element("div").classes("circle-middle"):
                            with ui.element("div").classes("circle-inner"):
                                ui.label(subject.name).classes("text-center")


def build_subject_topics_page(subject: Subject) -> None:
    """Render the topic-selection page for any subject."""
    with ui.element("div").classes("page-content"):
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
                        with ui.element("div").classes("circle-middle"):
                            with ui.element("div").classes("circle-inner"):
                                ui.label(topic.name)


def build_topic_mode_page(subject: Subject, topic: Topic) -> None:
    """Render the mode-selection page (Quiz / Learning) for any topic."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)
    with ui.element("div").classes("page-content"):
        _build_page_header(
            f"/{subject.url_slug}", f"Back to {subject.name}",
            f"{topic.icon}  {topic.name}", "What would you like to do?"
        )

        with ui.element("div").classes("mode-grid"):
            quiz_dest = f"/{subject.url_slug}/{topic.name.lower()}/quiz"
            with ui.element("div").classes("mode-card").on(
                "click", lambda d=quiz_dest: ui.navigate.to(d)
            ):
                ui.label("📝").classes("mode-icon")
                ui.label("Quiz").classes("mode-title")
                ui.label("Answer questions and test yourself!").classes("mode-desc")

            if topic.has_learning:
                learn_dest = f"/{subject.url_slug}/{topic.name.lower()}/learn"
                with ui.element("div").classes("mode-card").on(
                    "click", lambda d=learn_dest: ui.navigate.to(d)
                ):
                    ui.label("📖").classes("mode-icon")
                    ui.label("Learning").classes("mode-title")
                    ui.label("Read step-by-step explanations.").classes("mode-desc")


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
            f"📖  Learn {topic.name}", topic.learn_page_subtitle()
        )

        steps = topic.learning_steps()
        if steps:
            ui.label("What each part means:").style(
                "font-weight:800;font-size:18px;color:#60435F;margin-bottom:16px;"
            )
            with ui.element("div").style(
                "display:grid;grid-template-columns:repeat(3,1fr);gap:16px;"
            ):
                for i, (title, explanation) in enumerate(steps, start=1):
                    visual = topic.step_visual_html(i - 1)
                    with ui.element("div").classes("mode-card").style("gap:8px;"):
                        if visual:
                            ui.html(visual)
                        ui.html(
                            f'<span class="step-number">{i}</span>'
                            f'<strong>{title}</strong>'
                        )
                        ui.label(explanation).style(
                            "margin-top:4px;color:#555;font-size:14px;line-height:1.6;text-align:center;"
                        )

        ui.button("Ready? Take the Quiz →", on_click=lambda d=quiz_dest: ui.navigate.to(d)) \
            .props("rounded") \
            .style(
                "background:linear-gradient(135deg,#60435F,#D67AB5);color:#f3f1f1;"
                "font-weight:700;margin-top:24px;"
            )


def build_quiz_page(subject: Subject, topic: Topic) -> None:
    """Render the interactive quiz page for any topic."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)
    question_text, correct_answer = topic.generate_question()
    state = {
        "question": question_text,
        "answer":   correct_answer,
        "score":    0,
        "attempts": 0,
        "checked":  False,
    }

    visual_holder: list = []
    answer_input_holder: list = []

    def check_answer():
        if state["checked"]:
            return
        user = answer_input_holder[0].value.strip()
        is_correct, error = topic.check_answer(user, state["answer"])

        if error:
            feedback_label.text = error
            feedback_label.classes(replace="quiz-feedback-wrong")
            return  # invalid input — let the user fix it, don't count

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

    def show_hint():
        feedback_label.text = f"💡  Hint: the answer is {state['answer']}"
        feedback_label.classes(replace="quiz-feedback-wrong")

    def _advance():
        """Load a new question without checking."""
        state["question"], state["answer"] = topic.generate_question()
        state["checked"] = False
        question_label.text = state["question"]
        feedback_label.text = ""
        answer_input_holder[0].value = ""
        answer_input_holder[0].run_method("focus")
        if visual_holder:
            visual_holder[0].content = topic.question_visual_html(state["question"])

    def next_question():
        """Check current answer then advance."""
        check_answer()
        _advance()

    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    with ui.element("div").classes("page-content"):
        _build_page_header(back_dest, f"Back to {topic.name}", f"📝  {topic.name} Quiz", "")

        with ui.element("div").classes("mode-card").style("max-width:560px;margin:0;"):
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

            with ui.row().style("gap:12px;flex-wrap:wrap;justify-content:center;"):
                ui.button("Check ✓", on_click=check_answer) \
                    .props("rounded") \
                    .style("background:linear-gradient(135deg,#60435F,#D67AB5);color:white;font-weight:700;")
                ui.button("Next →", on_click=next_question) \
                    .props("rounded") \
                    .style("background:#f3e8ff;color:#60435F;font-weight:700;")
                ui.button("💡 Hint", on_click=show_hint) \
                    .props("rounded") \
                    .style("background:#fffbe6;color:#b45309;font-weight:700;")

            feedback_label = ui.label("")
