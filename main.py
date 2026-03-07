from __future__ import annotations
from nicegui import ui


def add_global_css():

    ui.add_head_html("""
    <style> 
      body {
        background: linear-gradient(180deg, #eef8ff 0%, #fdf6ff 100%);
      }

      .topbar {
        background: linear-gradient(98deg,#60435F,#60435F,#60435F,#D67AB1,#E2A3C7,#FDF7FA);
        height: 120px;
      }

      .wrap {
        max-width: 1300px;
        margin: 0 auto;
      }

      .logo-box {
        display:flex;
        align-items:center;
        gap:12px;
        color:white;
      }

      .logo-squares {
        width:40px;
        height:40px;
        display:grid;
        grid-template-columns:repeat(2, 18px);
        gap:4px;
      }

      .sq1 { background:#22c55e; border-radius:4px; }
      .sq2 { background:#f97316; border-radius:4px; }
      .sq3 { background:#60a5fa; border-radius:4px; }
      .sq4 { background:#ec4899; border-radius:4px; }

      .brand-title {
        font-weight:800;
        font-size:26px;
        line-height:1.1;
        white-space:pre-line;
      }

      .brand-sub {
        color:#F2CEE6;
        font-weight:700;
        margin-top:2px;
      }
</style>)
""")


@ui.page('/')
def home():
    add_global_css()
    with ui.element("div").classes("topbar w-full"):
        with ui.element("div").classes("wrap h-full flex items-center px-8"):
            with ui.element("div").classes("logo-box"):
                with ui.element("div").classes("logo-squares"):
                    ui.element("div").classes("sq1")
                    ui.element("div").classes("sq2")
                    ui.element("div").classes("sq3")
                    ui.element("div").classes("sq4")
                with ui.element("div"):
                    ui.label("KidsLearn").classes("brand-title")
                    ui.label("Learning with fun").classes("brand-sub")

    ui.label(
        'Choose a subject to start your learning adventure.'
    ).classes('text-body1')

    with ui.row().classes('justify-center gap-4 mt-8'):

        ui.button('Vocabulary').classes('text-lg bg-blue-500 text-white p-4 rounded-xl')
        ui.button('French').classes('text-lg bg-purple-500 text-white p-4 rounded-xl')
        ui.button('Math').classes('text-lg bg-orange-500 text-white p-4 rounded-xl')
        ui.button('Science').classes('text-lg bg-green-500 text-white p-4 rounded-xl')


ui.run(title="E-learning for kids", port=8081, reload=True)