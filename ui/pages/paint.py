"""Paint page – builds the UI layout and palette; canvas JS lives in static/js/paint_canvas.js.

Edge compatibility: NiceGUI's ui.html() passes content through Vue/Quasar's hydration
pipeline. Edge drops or mis-renders complex inner HTML during hydration. All substantial
HTML blocks (cards, palette, visual source) are therefore built as plain Python strings
and injected via ui.add_body_html(), completely bypassing Vue. Only structural skeleton
divs (safe because they carry no inner content) are built with ui.element().
"""
from __future__ import annotations

from nicegui import ui

from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _build_page_header

PALETTE_COLOR_GROUPS: list[list[tuple[str, bool]]] = [
    [("#FFFFFF", False), ("#FFFAF0", False), ("#FFDDE1", False), ("#E6A6D7", False)],  # Whites
    [("#FF4FA3", False), ("#EC4899", False)],  # Pinks
    [("#D4AAFF", False), ("#A855F7", False), ("#7C3AED", False)],  # Violets
    [("#FFF0A0", False), ("#FFD84D", False), ("#F59E0B", False)],  # Yellows
    [("#FFC27A", False), ("#FF9A5A", False)],  # Oranges
    [("#C7E9FF", False), ("#4F7BFF", False), ("#1D4ED8", False), ("#B5EAD7", False), ("#38C9B9", False)],  # Blues
    [("#9BE7A1", False), ("#4CD137", False), ("#10B981", False), ("#15803D", False)],  # Greens
    [("#D3D3D3", False), ("#374151", False)],  # Greys
    [("#b00b10", False)],  # Reds
    [("#92400E", False), ("#78350F", False)],  # Browns
    [("#2F2A3A", True), ("#000000", False)],  # Blacks
]
PALETTE_COLORS: list[tuple[str, bool]] = [c for g in PALETTE_COLOR_GROUPS for c in g]


def build_paint_page(
    subject: Subject,
    topic: Topic,
    page_index: int | str | None = None,
) -> None:
    normalized = _normalise_page_index(page_index)
    base_url = f"/{subject.url_slug}/{topic.name.lower()}/paint"
    back_dest = base_url if normalized is not None else f"/{subject.url_slug}/{topic.name.lower()}"
    active_indices = [normalized - 1] if normalized in (1, 2, 3) else list(range(3))
    detail_mode = normalized in (1, 2, 3)

    # Build only the page skeleton via NiceGUI/Vue — empty anchor divs only.
    # All real HTML is injected via add_body_html() to bypass Edge's Vue
    # hydration pipeline, which silently drops complex ui.html() content.
    with ui.element("div").classes("page-content"):
        _build_page_header(back_dest, "Back ", "", "")
        ui.element("div").props("id=paint-palette-anchor")  # palette mounts here
        ui.element("div").props("id=paint-grid-anchor")     # card grid mounts here

    # ── Hidden visual source (data store for JS) ─────────────────────────────
    visual = topic.paint_visual_html()
    if visual:
        ui.add_body_html(
            '<div id="paint-visual-source" style="display:none !important;'
            'visibility:hidden;position:absolute;width:0;height:0;overflow:hidden;">'
            f'{visual}</div>'
        )

    # ── Palette (detail mode only) ───────────────────────────────────────────
    if detail_mode:
        ui.add_body_html(_build_palette_html())

    # ── Card grid ────────────────────────────────────────────────────────────
    ui.add_body_html(_build_card_grid_html(base_url, active_indices, detail_mode))

    # ── Extra topic body HTML ─────────────────────────────────────────────────
    body_html = topic.paint_body_html()
    if body_html:
        ui.add_body_html(body_html)

    # ── Mount script: move elements into anchors, then load paint_canvas.js ──
    # HTML injected by add_body_html lands at the end of <body>. This inline
    # script moves each piece into its anchor div (preserving layout position)
    # and then dynamically loads paint_canvas.js only after Vue has flushed.
    palette_needed = "true" if detail_mode else "false"
    ui.add_body_html(f"""
<script>
(function () {{
  var paletteNeeded = {palette_needed};

  function mountAll() {{
    // Move palette into its layout anchor
    if (paletteNeeded) {{
      var paletteAnchor = document.getElementById('paint-palette-anchor');
      var palette       = document.getElementById('paint-palette');
      if (paletteAnchor && palette && !paletteAnchor.contains(palette)) {{
        paletteAnchor.appendChild(palette);
      }}
    }}

    // Move card grid into its layout anchor
    var gridAnchor = document.getElementById('paint-grid-anchor');
    var grid       = document.getElementById('paint-grid-root');
    if (gridAnchor && grid && !gridAnchor.contains(grid)) {{
      gridAnchor.appendChild(grid);
    }}

    // Load paint_canvas.js once (idempotent guard)
    if (!document.querySelector('script[data-paint-canvas]')) {{
      var s = document.createElement('script');
      s.src = '/static/js/paint_canvas.js';
      s.setAttribute('data-paint-canvas', '1');
      s.onload = function () {{
        // Extra 300 ms pass for Edge's slower Vue/Quasar hydration
        setTimeout(function () {{
          if (typeof window.__paintSetup === 'function') window.__paintSetup();
        }}, 300);
      }};
      document.body.appendChild(s);
    }}
  }}

  // rAF after DOMContentLoaded lets Vue flush its render queue first
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', function () {{
      requestAnimationFrame(mountAll);
    }});
  }} else {{
    requestAnimationFrame(mountAll);
  }}
}})();
</script>
""")


def _normalise_page_index(raw: int | str | None) -> int | None:
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


# ── Pure-string HTML builders (no NiceGUI elements) ──────────────────────────

def _build_palette_html() -> str:
    return (
        '<div id="paint-palette" '
        'style="position:fixed;right:24px;top:50%;transform:translateY(-50%);'
        'display:flex;flex-direction:column;gap:8px;align-items:center;'
        'padding:10px 12px;background:#f3f1f1;border-radius:14px;'
        'box-shadow:0 6px 16px rgba(96,67,95,0.2);z-index:50;'
        'max-height:calc(100vh - 230px);overflow-y:auto;">'
        '<div id="paint-palette-handle" '
        'style="font-size:14px;font-weight:700;color:#60435F;cursor:grab;'
        'user-select:none;padding:2px 8px;border-radius:10px;background:#f3f1f8;">Move</div>'
        '<div style="display:flex;flex-direction:column;gap:8px;align-items:center;">'
        + _build_color_buttons_html()
        + _build_eraser_button_html()
        + _build_fill_button_html()
        + _build_brush_buttons_html()
        + '</div></div>'
    )


def _build_color_buttons_html() -> str:
    btns = ""
    for color, selected in PALETTE_COLORS:
        border = "3px solid #60435F" if selected else "2px solid #d1d5db"
        sel = "true" if selected else "false"
        btns += (
            f'<button type="button" data-paint-color="{color}" data-selected="{sel}" '
            f'style="width:32px;height:32px;border-radius:999px;border:{border};'
            f'background:{color};cursor:pointer;"></button>'
        )
    return f'<div style="display:grid;grid-template-columns:repeat(3,32px);gap:6px;">{btns}</div>'


def _build_eraser_button_html() -> str:
    return (
        '<button type="button" data-paint-color="__eraser__" data-selected="false" title="Eraser" '
        'style="width:36px;height:36px;border-radius:999px;border:2px solid #d1d5db;'
        'background:linear-gradient(135deg,#ffffff,#ececec);cursor:pointer;'
        'display:flex;align-items:center;justify-content:center;color:#60435F;'
        'font-size:11px;font-weight:900;">ER</button>'
    )


def _build_fill_button_html() -> str:
    return (
        '<button type="button" id="paint-fill-btn" data-fill-active="false" title="Fill" '
        'style="width:36px;height:36px;border-radius:999px;border:2px solid #d1d5db;'
        'background:linear-gradient(135deg,#e0f2fe,#bae6fd);cursor:pointer;'
        'display:flex;align-items:center;justify-content:center;color:#60435F;'
        'font-size:18px;font-weight:900;">\U0001FAA3</button>'
    )


def _build_brush_buttons_html() -> str:
    sizes = [(6, False, 28), (12, True, 32), (20, False, 38)]
    dots  = [6, 10, 14]
    btns  = ""
    for (sz, sel, dim), dot in zip(sizes, dots):
        border = "3px solid #60435F" if sel else "2px solid #d1d5db"
        btns += (
            f'<button type="button" data-brush-size="{sz}" '
            f'data-brush-selected="{"true" if sel else "false"}" '
            f'style="width:{dim}px;height:{dim}px;border-radius:999px;border:{border};'
            f'background:#ffffff;cursor:pointer;display:flex;align-items:center;justify-content:center;">'
            f'<span style="width:{dot}px;height:{dot}px;border-radius:999px;'
            f'background:#60435F;display:block;"></span>'
            '</button>'
        )
    return (
        '<div style="font-size:12px;font-weight:800;color:#60435F;text-align:center;">Brush</div>'
        f'<div style="display:flex;gap:6px;justify-content:center;">{btns}</div>'
    )


def _build_card_grid_html(base_url: str, indices: list[int], detail_mode: bool) -> str:
    cols  = "1" if detail_mode else "3"
    width = "min(72vw,1000px)" if detail_mode else "min(95vw,1400px)"
    cards = "".join(_build_paint_card_html(base_url, i, detail_mode) for i in indices)
    return (
        '<div id="paint-grid-root" '
        f'style="display:grid;grid-template-columns:repeat({cols},minmax(220px,1fr));'
        f'gap:40px;width:{width};">'
        + cards
        + '</div>'
    )


def _build_paint_card_html(base_url: str, index: int, detail_mode: bool) -> str:
    open_url    = f"{base_url}/{index + 1}"
    cursor      = "crosshair" if detail_mode else "pointer"
    extra_style = "" if detail_mode else "cursor:pointer;"

    overview_note = ""
    if not detail_mode:
        overview_note = (
            '<div style="text-align:center;padding:0 10px 10px 10px;">'
            '<span style="font-weight:700;color:#60435F;font-size:15px;">'
            "Tap the paint area to continue on a full page</span></div>"
        )

    return (
        '<div class="paint-card" '
        'style="background:#fff;border-radius:32px;border:3px solid #60435f99;'
        'box-shadow:0 8px 24px rgba(96,67,95,0.8);display:flex;flex-direction:column;gap:10px;">'
        f'<div class="paint-instruction" data-paint-instruction="{index}" '
        'style="padding:10px;font-weight:600;text-align:center;color:#60435F;font-size:20px;"></div>'
        '<div style="display:flex;flex-direction:row;align-items:center;gap:10px;">'
        f'<div class="paint-color-key-area" data-color-key-overlay="{index}" '
        'style="display:none;flex-direction:column;gap:6px;padding:8px 10px;'
        'background:#f3f1f1;border-radius:12px;'
        'box-shadow:0 4px 12px rgba(96,67,95,0.15);min-width:60px;'
        'max-height:600px;overflow-y:auto;flex-shrink:0;"></div>'
        f'<div class="paint-area" data-open-paint-url="{open_url}" '
        f'style="position:relative;flex:1;height:650px;background:#fff;'
        f'border-radius:18px;overflow:hidden;{extra_style}">'
        f'<div class="paint-target-slot" data-paint-slot="{index}" '
        'style="position:absolute;inset:0;display:flex;justify-content:center;align-items:center;'
        'pointer-events:none;z-index:1;"></div>'
        f'<canvas class="paint-canvas" width="1000" height="600" '
        'style="position:absolute;inset:0;display:block;width:100%;height:100%;'
        f'background:transparent;touch-action:none;cursor:{cursor};z-index:2;"></canvas>'
        "</div>"
        "</div>"
        '<div style="text-align:center;padding:8px 10px;">'
        f'<button type="button" class="paint-hint-btn" data-hint-index="{index}" '
        'style="padding:8px 22px;border-radius:18px;border:2.5px solid #60435F;'
        'background:linear-gradient(135deg,#ede9fe,#fce7f3);color:#60435F;'
        'font-weight:800;font-size:16px;cursor:pointer;transition:transform .15s,box-shadow .15s;" '
        "onmouseover=\"this.style.transform='scale(1.06)';this.style.boxShadow='0 4px 12px rgba(96,67,95,0.3)'\" "
        "onmouseout=\"this.style.transform='scale(1)';this.style.boxShadow='none'\">"
        '<img src="/images/icons/machine-learning.svg" '
        'style="width:22px;height:22px;vertical-align:middle;margin-right:6px;">Hint</button></div>'
        f"{overview_note}"
        f'<div class="paint-hint-area" data-hint-overlay="{index}" '
        'style="display:none;justify-content:center;align-items:center;padding:12px 0 16px 0;"></div>'
        "</div>"
    )