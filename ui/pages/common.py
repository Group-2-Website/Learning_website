from __future__ import annotations
from nicegui import ui


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
        color: #eb4034;
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


def _build_page_header(back_dest: str, back_label: str, title: str, subtitle: str) -> None:
    """Render the shared back-button + page title + subtitle header."""
    with ui.element("div").classes("back-btn").on("click", lambda d=back_dest: ui.navigate.to(d)):
        ui.label(f"← {back_label}")
    ui.label(title).classes("page-title")
    if subtitle:
        ui.label(subtitle).classes("page-subtitle")



