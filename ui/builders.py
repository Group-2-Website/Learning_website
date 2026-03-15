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
        margin: 20px;
        
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
        font-size: 30px;
        font-weight: 700;
        color: #D67AB5;
        text-align: center;
        padding: 10px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
      }

      .subject-circle-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 14px;
      }

      .subject-icon {
        width: 72px;
        height: 72px;
        object-fit: contain;
      }

      .subject-label {
        line-height: 1.2;
        max-width: 250px;
      }


      .page-content {
        max-width: 900px;  /* ← max width of content on all pages  */
        margin: 50px ; /* ← top gap from topbar on all pages   */
        padding: 0 px;   /* ← left/right edge gap on all pages   */
      }


      .page-content1 {
        max-width: 900px;  /* ← max width of content on all pages  */
        margin: 40px auto; /* ← top gap from topbar on all pages   */
        padding: 0 px;   /* ← left/right edge gap on all pages   */
      }

      .page-title {
        font-size: 38px;
        font-weight: 1000;
        color: #60435F;
        margin-bottom: 8px;
        text-shadow: 2px 2px 0px #c7c5c1;
      }

      .page-subtitle {
        color: #734962;
        font-size: 26px;
        font-weight: 600;
        margin-bottom: 36px;
        text-shadow: 2px 2px 0px #c7c5c1;
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
    
      
      .btn-svg-icon .q-btn__content::before {
         content: '';
         width:26px;
         height:26px;
         flex:0026px;
         margin:3px;
         background-image: var(--icon);
         background-repeat: no-repeat;
         background-position: center;
         background-size: contain;
         }
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
        background: rgba(255,255,255,0.35);
        z-index: 0;
        pointer-events: none;
      }}
    </style>
    """)
def paint_body_html() -> None:
    ui.add_body_html("""
        <script>
        (function () {
          window.__kidslearnPaintColor = window.__kidslearnPaintColor || '#FF8C69';

          const selectPaletteButton = function (button) {
            document.querySelectorAll('[data-paint-color]').forEach(function (item) {
              item.dataset.selected = 'false';
              item.style.border = '2px solid #d1d5db';
            });
            button.dataset.selected = 'true';
            button.style.border = '3px solid #60435F';
          };

          if (!window.__kidslearnPaletteBound) {
            window.__kidslearnPaletteBound = true;
            document.addEventListener('click', function (event) {
              const palette = event.target.closest('[data-paint-color]');
              if (!palette) return;
              window.__kidslearnPaintColor = palette.dataset.paintColor;
              selectPaletteButton(palette);
            });
          }

          const mountVisualTargets = function () {
            const source = document.getElementById('paint-visual-source');
            if (!source) return;
            const pages = source.querySelectorAll('.paint-page');
            const slots = document.querySelectorAll('.paint-target-slot');
            const instructions = document.querySelectorAll('[data-paint-instruction]');

            slots.forEach(function (slot, index) {
              if (slot.dataset.bound === 'true') return;
              const page = pages[index];
              if (!page) return;

              // Keep the original instruction text from the topic HTML (e.g. "Page 2: Paint 2/3").
              const pageInstruction = page.firstElementChild ? page.firstElementChild.textContent.trim() : '';
              if (instructions[index] && pageInstruction) {
                instructions[index].textContent = pageInstruction;
              }

              const target = page.querySelector('[data-target-num][data-target-den]') || page;
              slot.dataset.bound = 'true';
              slot.appendChild(target.cloneNode(true));

              const meta = target.querySelector('[data-target-num][data-target-den]') || target;
              if (instructions[index] && !pageInstruction && meta && meta.dataset.targetNum && meta.dataset.targetDen) {
                instructions[index].textContent = 'Paint ' + meta.dataset.targetNum + '/' + meta.dataset.targetDen;
              }
            });
          };

          const bindPaletteDrag = function () {
            const palette = document.getElementById('paint-palette');
            const handle = document.getElementById('paint-palette-handle');
            if (!palette || !handle || palette.dataset.dragBound === 'true') return;
            palette.dataset.dragBound = 'true';

            let dragging = false;
            let offsetX = 0;
            let offsetY = 0;

            const clamp = function (value, min, max) {
              return Math.min(Math.max(value, min), max);
            };

            const setPalettePosition = function (left, top) {
              const rect = palette.getBoundingClientRect();
              const maxLeft = Math.max(0, window.innerWidth - rect.width);
              const maxTop = Math.max(0, window.innerHeight - rect.height);
              palette.style.left = clamp(left, 0, maxLeft) + 'px';
              palette.style.top = clamp(top, 0, maxTop) + 'px';
              palette.style.right = 'auto';
              palette.style.transform = 'none';
            };

            handle.addEventListener('pointerdown', function (event) {
              const rect = palette.getBoundingClientRect();
              dragging = true;
              offsetX = event.clientX - rect.left;
              offsetY = event.clientY - rect.top;
              handle.style.cursor = 'grabbing';
              handle.setPointerCapture(event.pointerId);
              event.preventDefault();
            });

            handle.addEventListener('pointermove', function (event) {
              if (!dragging) return;
              setPalettePosition(event.clientX - offsetX, event.clientY - offsetY);
            });

            const stopDragging = function (event) {
              if (!dragging) return;
              dragging = false;
              handle.style.cursor = 'grab';
              if (event && handle.hasPointerCapture(event.pointerId)) {
                handle.releasePointerCapture(event.pointerId);
              }
            };

            handle.addEventListener('pointerup', stopDragging);
            handle.addEventListener('pointercancel', stopDragging);
            window.addEventListener('resize', function () {
              if (!palette.style.left || !palette.style.top) return;
              setPalettePosition(parseFloat(palette.style.left), parseFloat(palette.style.top));
            });
          };

          const pointFromEvent = function (canvas, event) {
            const rect = canvas.getBoundingClientRect();
            const width = rect.width || 1;
            const height = rect.height || 1;
            const scaleX = canvas.width / width;
            const scaleY = canvas.height / height;
            return {
              x: (event.clientX - rect.left) * scaleX,
              y: (event.clientY - rect.top) * scaleY,
            };
          };

          const bindCanvases = function () {
            document.querySelectorAll('.paint-canvas').forEach(function (canvas) {
              if (canvas.dataset.bound === 'true') return;
              canvas.dataset.bound = 'true';

              const ctx = canvas.getContext('2d');
              if (!ctx) return;

              // Keep canvas transparent so the target circle remains visible underneath.
              ctx.clearRect(0, 0, canvas.width, canvas.height);
              ctx.lineCap = 'round';
              ctx.lineJoin = 'round';

              let drawing = false;

              canvas.addEventListener('pointerdown', function (event) {
                drawing = true;
                canvas.setPointerCapture(event.pointerId);
                const p = pointFromEvent(canvas, event);
                const pressure = event.pressure && event.pressure > 0 ? event.pressure : 0.5;
                ctx.lineWidth = 4 + (pressure * 8);
                ctx.strokeStyle = window.__kidslearnPaintColor;
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p.x + 0.01, p.y + 0.01);
                ctx.stroke();
              });

              canvas.addEventListener('pointermove', function (event) {
                if (!drawing) return;
                const p = pointFromEvent(canvas, event);
                const pressure = event.pressure && event.pressure > 0 ? event.pressure : 0.5;
                ctx.lineWidth = 4 + (pressure * 8);
                ctx.strokeStyle = window.__kidslearnPaintColor;
                ctx.lineTo(p.x, p.y);
                ctx.stroke();
              });

              const stopDrawing = function (event) {
                if (!drawing) return;
                drawing = false;
                ctx.closePath();
                if (event && canvas.hasPointerCapture(event.pointerId)) {
                  canvas.releasePointerCapture(event.pointerId);
                }
              };

              canvas.addEventListener('pointerup', stopDrawing);
              canvas.addEventListener('pointercancel', stopDrawing);
              canvas.addEventListener('pointerleave', stopDrawing);
            });
          };

          mountVisualTargets();
          bindCanvases();
          bindPaletteDrag();
          requestAnimationFrame(function () {
            mountVisualTargets();
            bindCanvases();
            bindPaletteDrag();
          });
          setTimeout(function () {
            mountVisualTargets();
            bindCanvases();
            bindPaletteDrag();
          }, 100);
        })();
        </script>
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
    with (ui.element("div").classes("page-content1")):
        ui.label("Choose a subject to start your learning adventure.").classes("text-body1")
        with ui.element("div").style(
            "display:flex;flex-wrap:wrap;justify-content:center;margin-top:70px;"
        ):
            for subject in SUBJECTS:
                dest = f"/{subject.url_slug}"
                with ui.element("div").classes("circle-wrapper").on(
                    "click", lambda d=dest: ui.navigate.to(d)
                ):
                 with ui.element("div").classes("circle-outer"):
                     with ui.element("div").classes("circle-inner"):
                        with ui.element("div").classes("subject-circle-content"):
                            ui.label(subject.name).classes("text-center subject-label")
                            ui.image(subject.icon).classes("subject-icon")



def build_subject_topics_page(subject: Subject) -> None:
    """Render the topic-selection page for any subject."""
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


def build_topic_mode_page(subject: Subject, topic: Topic) -> None:
    """Render the mode-selection page (Quiz / Learning) for any topic."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)
    with ui.element("div").classes("page-content1"):
        _build_page_header(
            f"/{subject.url_slug}", f"Back to {subject.name}",
            f"{topic.icon}  {topic.name}", "What would you like to do?"
        )

        with ui.element("div").classes("mode-grid"):
            quiz_dest = f"/{subject.url_slug}/{topic.name.lower()}/quiz"
            with ui.element("div").classes("mode-card").on(
                "click", lambda d=quiz_dest: ui.navigate.to(d)
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
                    ui.html('<img src="/images/icons/colored-pencils.svg" style="width:80px;height:80px;object-fit:contain;">')
                    ui.label("Painting").classes("mode-title")
                    ui.label("Paint your understanding!").classes("mode-desc")

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
            f"Learn how to deal with {topic.name}", ""
        )

        steps = topic.learning_steps()
        if steps:
            with ui.element("div").style(
                "display:grid;grid-template-columns:repeat(2,1fr);gap:16px;"
            ):
                for i, (title, explanation) in enumerate(steps, start=1):
                    visual = topic.step_visual_html(i - 1)
                    with ui.element("div").classes("mode-card").style("gap:8px;"):
                        if visual:
                            ui.html(visual)
                        ui.html(
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

def build_paint_page(subject: Subject, topic: Topic) -> None:
    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    with ui.element("div").classes("page-content"):
        _build_page_header(
            back_dest, f"Back to {topic.name}",
            "", ""
        )

        with ui.element("div").style("display:flex;flex-direction:column;gap:14px;align-items:flex-start;"):
            visual = topic.paint_visual_html()
            if visual:
                # Keep the generated target circles off-screen; JS places each one into its card slot.
                ui.html(
                    '<div id="paint-visual-source" style="display:none;">'
                    f'{visual}'
                    '</div>'
                )

            # Floating palette starts on the right and can be dragged with the handle.
            with ui.element("div").props("id=paint-palette").style(
                "position:fixed;right:24px;top:50%;transform:translateY(-50%);"
                "display:flex;flex-direction:column;gap:10px;align-items:center;"
                "padding:10px 12px;background:#f3f1f1;border-radius:14px;"
                "box-shadow:0 6px 16px rgba(96,67,95,0.2);z-index:50;"
            ):
                ui.html(
                    '<div id="paint-palette-handle" '
                    'style="font-size:14px;font-weight:700;color:#60435F;cursor:grab;'
                    'user-select:none;padding:2px 8px;border-radius:10px;background:#ede9fe;">'
                    'Move</div>'
                )
                with ui.element("div").style("display:flex;flex-direction:column;gap:10px;"):
                    palette_colors = [
                        ("#FF8C69", True),  # (color, selected)
                        ("#7EC88A", False),
                        ("#6BBFFF", False),
                        ("#FFAD05", False),
                        ("#D67AB1", False),
                        ("#fff", False),
                    ]
                    for color, selected in palette_colors:
                        border = "3px solid #60435F" if selected else "2px solid #d1d5db"
                        selected_attr = "true" if selected else "false"
                        ui.html(
                            f'<button type="button" data-paint-color="{color}" '
                            f'data-selected="{selected_attr}" '
                            f'style="width:38px;height:38px;border-radius:999px;'
                            f'border:{border};background:{color};cursor:pointer;"></button>'
                        )

            with ui.element("div").style(
                "display:grid;grid-template-columns:repeat(3,minmax(220px,1fr));"
                "gap:60px;width:min(95vw,1400px);"
            ):
                for i in range(3):
                    ui.html(
                        '<div class="paint-card"'
                        'style="padding:80px;background:#fff;border-radius:32px;border:3px solid #60435f99;'
                        'box-shadow:0 8px 24px rgba(96,67,95,0.8);display:flex;flex-direction:column;gap:10px;">'
                        f'<div class="paint-instruction" data-paint-instruction="{i}" '
            
                        'style="font-weight:800;text-align:center;color:#60435F;font-size:20px;">'
                        '</div>'
                        '<div class="paint-area" '
                        'style="position:relative;height:400px;background:#fff;'
                        'border-radius:18px;overflow:hidden;">'
                        f'<div class="paint-target-slot" data-paint-slot="{i}" '
                        'style="position:absolute;inset:0;display:flex;justify-content:center;align-items:center;'
                        'pointer-events:none;z-index:1;"></div>'
                        '<canvas class="paint-canvas"  width="1000" height="600" '
                        'style="position:absolute;inset:0;display:block;width:100%;height:100%;'
                        'background:transparent;touch-action:none;cursor:crosshair;z-index:2;">'
                        '</canvas>'
                        '</div>'
                        '</div>'
                    )
                paint_body_html()


    body_html = topic.paint_body_html()
    if body_html:
        ui.add_body_html(body_html)

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
        ui.timer(1.0, _advance, once=True)

    def show_hint():
        feedback_label.text = f" Hint: the answer is {state['answer']}"
        feedback_label.classes(replace="quiz-feedback-wrong")

    def _advance():
        """Load a new question without checking."""
        state["question"], state["answer"] = topic.generate_question()
        state["checked"] = False
        question_label.text = state["question"]
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
        score   = state["score"]
        attempts = state["attempts"]
        dest = (
            f"/{subject.url_slug}/{topic.name.lower()}/results"
            f"?score={score}&attempts={attempts}"
        )
        ui.navigate.to(dest)

    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    with ui.element("div").classes("page-content1"):
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


def build_quiz_results_page(subject: Subject, topic: Topic, score: int, attempts: int) -> None:
    """Render the quiz results page."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)

    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    quiz_dest = f"/{subject.url_slug}/{topic.name.lower()}/quiz"

    pct = round((score / attempts) * 100) if attempts > 0 else 0

    if pct == 100:
        msg, color = "Perfect score! Amazing!", "#22c55e"
    elif pct >= 70:
        msg, color = "Great job! Keep it up!", "#f97316"
    elif pct >= 40:
        msg, color = "Good effort! Keep practising.", "#60a5fa"
    else:
        msg, color = "Keep going — practice makes perfect!", "#ec4899"

    with ui.element("div").classes("page-content1"):
        _build_page_header(back_dest, f"Back to {topic.name}", f"📝  Quiz Results", "")

        with ui.element("div").classes("mode-card").style(
            "max-width:520px;margin:40px auto;gap:18px;align-items:center;"
        ):
            ui.label(msg).style(
                f"font-size:24px;font-weight:800;color:#f97316;text-align:center;"
            )
            ui.label(f"Your score: {score} / {attempts}").style(
                "font-size:36px;font-weight:800;color:#60435F;"
            )
            ui.label(f"{pct}%").style(
                f"font-size:48px;font-weight:900;color:#60435F;"
            )

            with ui.row().style("gap:16px;flex-wrap:wrap;justify-content:center;margin-top:12px;"):
                ui.button("🔄  Try Again", on_click=lambda: ui.navigate.to(quiz_dest)) \
                    .props("rounded") \
                    .style(
                        "background:linear-gradient(135deg,#60435F,#D67AB5);"
                        "color:white;font-weight:700;font-size:15px;"
                    )
                ui.button("Back to Topic", on_click=lambda: ui.navigate.to(back_dest)) \
                    .props("rounded") \
                    .classes("btn-svg-icon") \
                    .style(
                        "--icon: url('/images/icons/daycare.svg'); background:#f3e8ff;color:#60435F;font-weight:700;font-size:15px;"
                    )
