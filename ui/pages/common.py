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
    <link rel="icon" type="image/png" href="/static/favicon.png">
    <link rel="shortcut icon" type="image/png" href="/static/favicon.png">
    <link rel="apple-touch-icon" href="/static/favicon.png">
    <link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@800&display=swap" rel="stylesheet">
    <style>

      body {
        background: linear-gradient(180deg, #eef8ff 0%, #fdf6ff 100%);
        background: #e0e0e047;
      }

      .topbar {
        background: linear-gradient(90deg,#FF8A8A,#FFB6C1,#FFD6A5,#BDE0FE,#A8E6CF);
        height: 210px;
        width: 110vw;
        margin-left: calc(-1 * var(--nicegui-default-padding));
        margin-right: calc(-1 * var(--nicegui-default-padding));
        margin-top: calc(-2* var(--nicegui-default-padding));
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
        display: block;
        font-family: 'Baloo 2', cursive;
        font-size: clamp(38px, 6vw, 70px);
        font-weight: 800;
        max-width: 115%;
        color: #ffb4a2;
        text-shadow:
            -2px -2px 0 #ffffff,
            2px 2px 0 #f28482,
            4px 4px 0 #e76f51,
            6px 6px 14px rgba(0,0,0,0.2);
        line-height: 1.3;
        letter-spacing: 2px;
        overflow: hidden;
        white-space: nowrap;
        animation: shine 3s ease-in-out infinite;
        transform: translateZ(0);
      }
      @keyframes shine {
        0% { filter: brightness(1); }
        50% { filter: brightness(1.15); }
        100% { filter: brightness(1); }
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
        margin: 25px;
        
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
        max-width: 1200px;  /* ← max width of content on all pages  */
        margin: 35px auto; /* ← top gap from topbar on all pages   */
        padding: 0 px;   /* ← left/right edge gap on all pages   */
      }

      .page-title {
        font-size: 38px;
        font-weight: 1000;
        color: #4A2D5F;
        margin-bottom: 16px;
        text-shadow: 2px 2px 0px #c7c5c1;
      }

      .page-subtitle {
        color: #2F855A;
        font-size: 26px;
        font-weight: 600;
        margin-bottom: 36px;
        text-shadow: 0 2px 6px rgba(0,0,0,0.2);
      }

      /* ── Mode cards (Quiz / Learning) ── */
      .mode-grid {
        display: flex;
        gap: 28px;
        flex-wrap: wrap;
        margin-top: 46px;
      }

      .mode-card {
        flex: 1;
        min-width: 600px;
        min-height:300px;
        max-width: 90%;
        background: #f3f1f1;
        border-radius: 35px;
        border: 2px solid #60435f99;
        padding: 36px 24px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 14px;
        position: relative;
        cursor: pointer;
        box-shadow: 0 4px 14px rgba(96,67,95,0.10);
        transition: transform .18s ease, box-shadow .18s ease;
      }
      .mode-card::after {
          content: "";
          position: absolute;
          top: -60px;
          right: -70px;
          width: 160px;
          height: 160px;
          background: url("/images/cute-star.png") no-repeat center;
          background-size: contain;
          pointer-events: none; /
        }

      .mode-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(96,67,95,0.20);
      }

      .mode-card.expanded {
        position:fixed !important;top:50%;left:50%;
        transform:translate(-50%,-50%) !important;
        width:85vw;max-height:90vh;overflow:auto;
        z-index:9999;min-width:0;
        box-shadow:0 12px 40px rgba(96,67,95,0.35);
      }
      .mode-card.expanded:hover { transform:translate(-50%,-50%) !important; }

      .learn-overlay {
        display:none;position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:9998;
      }
      .learn-overlay.show { display:block; }

      .learn-close-btn {
        position:absolute;top:12px;right:18px;z-index:10000;
        background:#60435F;color:white;border:none;border-radius:50%;
        width:36px;height:36px;font-size:20px;font-weight:800;
        cursor:pointer;line-height:36px;text-align:center;
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
        white-space: pre-line;
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

      .quiz-feedback-hint {
        color: #b45309;
        font-weight: 700;
        font-size: 18px;
      }

      .back-btn {
        display: inline-flex;
        align-items: center;
        gap: 1px;
        color: #C084FC;
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

      .start-quiz-btn.q-btn,
      .start-quiz-btn.q-btn.bg-primary,
      .start-quiz-btn.q-btn[class*="bg-"] {
         background: linear-gradient(135deg, #FF9A9E, #FAD0C4) !important;
         background-color: transparent !important;
         color: #4A3F55 !important;
         border: none !important;
         border-radius: 20px !important;
         transition: transform 0.2s ease, box-shadow 0.2s ease !important;
      }
      .start-quiz-btn.q-btn:hover {
         transform: scale(1.05) !important;
         box-shadow: 0 6px 18px rgba(255, 154, 158, 0.4) !important;
      }
      .start-quiz-btn .q-focus-helper {
         display: none !important;
      }
         
    .stars-title {
      font-size: 34px;
      font-weight: 900;
      color: #4b1d4d;
      margin-bottom: 10px;
    }

    /* Banner */
    .stars-banner {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 14px;
      
      background: linear-gradient(180deg, #d1bad9, #b08ebf);
      padding: 20px 40px;
      border-radius: 60px;
      box-shadow: 0 8px 0 #8d60a1;
    }

    /* Star base */
    .star {
      width: 40px;
      height: 40px;
      background: #d1d5db;
      clip-path: polygon(
        50% 0%, 61% 35%, 98% 35%,
        68% 57%, 79% 91%, 50% 70%,
        21% 91%, 32% 57%, 2% 35%, 39% 35%
      );
    }
    
    /* Filled star */
    .star.filled {
      background: #facc15;
      box-shadow: 0 0 10px #facc15;
      animation: pop 0.4s ease;
    }

    /* Half-filled star */
    .star.half {
      background: linear-gradient(90deg, #facc15 50%, #d1d5db 50%);
      animation: pop 0.4s ease;
    }
    
    /* Animation */
    @keyframes pop {
      0% { transform: scale(0.5); }
      70% { transform: scale(1.2); }
      100% { transform: scale(1); }
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
        background-position: center top 50px !important;
        background-attachment: fixed !important;
      }}
      body::before {{
        content: '';
        position: fixed;
        inset: 0;
        background: rgba(255,255,255,0.55);
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

def audio_button_html(audio_url: str, *, size: str = "normal") -> str:
    if not audio_url:
        return ""

    font = "16px" if size == "normal" else "18px"
    pad = "6px 14px" if size == "normal" else "8px 18px"
    icon = "20px" if size == "normal" else "24px"

    return (
        f'<button class="audio-btn" data-audio-url="{audio_url}"'
        f' style="'
        f' background:linear-gradient(135deg,#FF9A9E,#FAD0C4);'
        f' border:none;'
        f' cursor:pointer;'
        f' color:#4A3F55;'
        f' font-size:{font};'
        f' padding:{pad};'
        f' border-radius:999px;'
        f' display:inline-flex;'
        f' align-items:center;'
        f' gap:8px;'
        f' box-shadow:0 4px 10px rgba(0,0,0,0.1);'
        f' transition:all 0.25s ease;'
        f' font-weight:600;'
        f' "'
        f' onmouseover="this.style.transform=\'scale(1.05)\';this.style.boxShadow=\'0 6px 14px rgba(0,0,0,0.15)\'"'
        f' onmouseout="this.style.transform=\'scale(1)\';this.style.boxShadow=\'0 4px 10px rgba(0,0,0,0.1)\'"'
        f' title="Listen to pronunciation"'
        f'>'

        f'<span style="'
        f' display:flex;align-items:center;justify-content:center;'
        f' width:{icon};height:{icon};'
        f' background:white;border-radius:50%;'
        f' padding:4px;'
        f' ">'
        f'<img src="/images/icons/high-volume.svg"'
        f' style="width:100%;height:100%;object-fit:contain;" />'
        f'</span>'

        f' Listen'
        f'</button>'
    )


def add_audio_player_script() -> None:
    """Inject the shared JS that makes every .audio-btn play its audio."""
    ui.add_body_html("""
    <script>
    (function(){
      if(window.__audioPlayerReady) return;
      window.__audioPlayerReady = true;
      var currentAudio = null;
      document.addEventListener('click', function(e){
        var btn = e.target.closest('.audio-btn');
        if(!btn) return;
        e.stopPropagation();
        var url = btn.getAttribute('data-audio-url');
        if(!url) return;
        if(currentAudio){ currentAudio.pause(); currentAudio = null; }
        currentAudio = new Audio(url);
        currentAudio.play();
      });
    })();
    </script>
    """)
