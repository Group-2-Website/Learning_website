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
      .text-body1 {         
        color:#D67AB1;
        font-weight:700;
        margin-top:2px;
      }
      .brand-sub {
        color:#F2CEE6;
        font-weight:700;
        margin-top:2px;
      }
      .math-circle-wrapper {
        display:flex;
        justify-content:center;
        margin-top:80px;
      }
    
    .math-circle-outer {
      width:220px;
      height:220px;
      border-radius:50%;
      background:linear-gradient(135deg,#60435F,#ffb3d9);
      display:flex;
      align-items:center;
      justify-content:center;
      cursor:pointer;
      transition:transform .2s ease;
      }
    
    .math-circle-outer:hover{
      transform:scale(1.05);
      }
    
    .math-circle-middle{
      width:170px;
      height:170px;
      border-radius:50%;
      background:white;
      display:flex;
      align-items:center;
      justify-content:center;
      box-shadow:0 6px 18px rgba(0,0,0,0.12);
     }
    
    .math-circle-inner{
      width:130px;
      height:130px;
      border-radius:50%;
      background:#fff4fb;
      display:flex;
      align-items:center;
      justify-content:center;
      font-size:38px;
      font-weight:700;
      color:#D67AB1;
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


    with ui.element("div").classes("math-circle-wrapper"):
        with ui.element("div").classes("math-circle-outer"):
            with ui.element("div").classes("math-circle-middle"):
                with ui.element("div").classes("math-circle-inner"):
                    ui.label("Math").classes("text-center")

ui.run(title="E-learning for kids", port=8081, reload=True)