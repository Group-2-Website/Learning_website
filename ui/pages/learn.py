from __future__ import annotations
from nicegui import ui
from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header, audio_button_html, add_audio_player_script


def build_learn_page(subject: Subject, topic: Topic) -> None:
    """Render the learning/b page for any topic."""
    url = topic.page_background_image()
    if url:
        _apply_bg(url)
    back_dest = f"/{subject.url_slug}/{topic.name.lower()}"
    quiz_filter_dest = f"/{subject.url_slug}/{topic.name.lower()}/filter"
    with ui.element("div").classes("page-content"):
        _build_page_header(
            back_dest, f"Back to {topic.name}",
            topic.learn_page_subtitle(), ""
        )

        ui.html('<div class="learn-overlay" id="learn-overlay"></div>', sanitize=False)

        cards = topic.learning_steps()
        if cards:
            with ui.element("div").style(
                "display:grid;grid-template-columns:repeat(2,1fr);gap:60px;"
            ):
                for i, card in enumerate(cards, start=1):
                    visual = topic.step_visual_html(i - 1)
                    with ui.element("div").classes("mode-card").style("gap:26px;"):
                        ui.html(
                            f'<strong style="font-size:24px;">{card.title}</strong>',
                            sanitize=False
                        )
                        if visual:
                            ui.html(visual, sanitize=False)

                        if card.main_text:
                            text = card.main_text.strip()
                            if text.startswith("<"):
                                ui.html(text, sanitize=False)  # z.B. table, ul, custom html
                            else:
                                ui.html(
                                    f'<p style="margin:6px 0;font-size:20px;font-weight:700;'
                                    f'color:#7B2D8E;text-align:center;line-height:1.6;">'
                                    f'{text}</p>',
                                    sanitize=False
                                )

                        if card.secondary_text:
                            ui.html(
                                f'<p style="margin:6px 0;font-size:20px;font-weight:700;'
                                f'color:#E8820C;text-align:center;line-height:1.4;">'
                                f'{card.secondary_text}</p>',
                                sanitize=False
                            )
                        if card.audio_url:
                            ui.html(
                                f'<div style="display:flex;justify-content:center;">'
                                f'{audio_button_html(card.audio_url, size="large")}'
                                f'</div>',sanitize=False
                            )
                        if card.hint_text:
                            ui.label(f"Answer: {card.hint_text}").style(
                                "margin-top:2px;color:#1a7f37;font-size:15px;line-height:1.4;text-align:center;"
                            )


        add_audio_player_script()

        ui.add_body_html("""
        <script>

        /* ── card expand / collapse ── */
        (function(){
          const overlay = document.getElementById('learn-overlay');
          function closeExpanded(){
            document.querySelectorAll('.mode-card.expanded').forEach(function(c){
              c.classList.remove('expanded');
              var btn=c.querySelector('.learn-close-btn'); if(btn) btn.remove();
            });
            overlay.classList.remove('show');
          }
          document.addEventListener('click', function(e){
            if(e.target.closest('.audio-btn')) return;
            if(e.target.closest('.learn-close-btn')){ closeExpanded(); return; }
            var card = e.target.closest('.mode-card');
            if(card && !card.classList.contains('expanded')){
              card.style.position='relative';
              card.classList.add('expanded');
              var btn=document.createElement('button');
              btn.className='learn-close-btn'; btn.innerHTML='&times;'; btn.a='Close';
              card.prepend(btn);
              overlay.classList.add('show');
              return;
            }
            if(overlay.classList.contains('show')) closeExpanded();
          });
        })();
        </script>
        """)

        ui.button("Ready? Take the Quiz →", on_click=lambda d=quiz_filter_dest: ui.navigate.to(d)) \
            .props("rounded") \
            .style(
                "background:linear-gradient(135deg,#60435F,#D67AB5);color:#f3f1f1;"
                "font-weight:700;margin-top:24px;"
            )
