from __future__ import annotations
from nicegui import ui
from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _apply_bg, _build_page_header


def build_learn_page(subject: Subject, topic: Topic) -> None:
    """Render the learning/b page for any topic."""
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

        ui.html('<div class="learn-overlay" id="learn-overlay"></div>')

        cards = topic.learning_cards()
        if cards:
            with ui.element("div").style(
                "display:grid;grid-template-columns:repeat(2,1fr);gap:60px;"
            ):
                for i, card in enumerate(cards, start=1):
                    visual = topic.step_visual_html(i - 1)
                    with ui.element("div").classes("mode-card").style("gap:26px;"):
                        ui.html(
                            f'<strong>{card.title}</strong>'
                        )
                        if visual:
                            ui.html(visual)

                        ui.label(card.paragraph).style(
                            "margin-top:.5px;color:#555;font-size:18px;line-height:1.6;text-align:center;"
                        )
                        if card.detail:
                            ui.label(f" {card.detail}").style(
                                "margin-top:4px;color:#333;font-size:15px;line-height:1.4;text-align:center;"
                            )
                        if card.note:
                            ui.label(card.note).style(
                                "margin-top:2px;color:#1a7f37;font-size:15px;line-height:1.4;text-align:center;"
                            )

        ui.add_body_html("""
        <script>
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

        ui.button("Ready? Take the Quiz →", on_click=lambda d=quiz_dest: ui.navigate.to(d)) \
            .props("rounded") \
            .style(
                "background:linear-gradient(135deg,#60435F,#D67AB5);color:#f3f1f1;"
                "font-weight:700;margin-top:24px;"
            )
