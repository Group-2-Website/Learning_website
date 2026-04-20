"""Paint page – builds the UI layout and palette; canvas JS lives in static/js/paint_canvas.js."""
from __future__ import annotations

from nicegui import ui

from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _build_page_header

# ── Palette colours (hex, default-selected) ──────────────────────────────────
PALETTE_COLORS: list[tuple[str, bool]] = [
    ("#2F2A3A", True),   # Dark outline
    ("#4F7BFF", False),  # Primary blue
    ("#7ED3FF", False),  # Light sky blue
    ("#4CD137", False),  # Bright green
    ("#9BE7A1", False),  # Soft mint
    ("#38C9B9", False),  # Teal
    ("#b00b10", False),  # Red
    ("#FF4FA3", False),  # Strong pink
    ("#E6A6D7", False),  # Pastel pink
    ("#FF9A5A", False),  # Warm orange
    ("#FFC27A", False),  # Soft peach
    ("#FFD84D", False),  # Yellow
    ("#FFFFFF", False),  # White
]


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

    with ui.element("div").classes("page-content"):
        _build_page_header(back_dest, "Back ", "", "")

        with ui.element("div").style(
            "display:flex;flex-direction:column;gap:14px;align-items:flex-start;"
        ):
            _inject_visual_source(topic)
            _build_palette()
            _build_card_grid(base_url, active_indices, detail_mode)

    # Topic-specific body HTML (e.g. fraction visuals)
    body_html = topic.paint_body_html()
    if body_html:
        ui.add_body_html(body_html)

    # Canvas interaction script
    ui.add_body_html('<script src="/static/js/paint_canvas.js"></script>')


def _normalise_page_index(raw: int | str | None) -> int | None:
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _inject_visual_source(topic: Topic) -> None:
    """Hidden container whose children are relocated by JS into card slots."""
    visual = topic.paint_visual_html()
    if visual:
        ui.html(
            f'<div id="paint-visual-source" style="display:none;">{visual}</div>'
        )


def _build_palette() -> None:
    with ui.element("div").props("id=paint-palette").style(
        "position:fixed;right:24px;top:50%;transform:translateY(-50%);"
        "display:flex;flex-direction:column;gap:10px;align-items:center;"
        "padding:10px 12px;background:#f3f1f1;border-radius:14px;"
        "box-shadow:0 6px 16px rgba(96,67,95,0.2);z-index:50;"
    ):
        # Drag handle
        ui.html(
            '<div id="paint-palette-handle" '
            'style="font-size:14px;font-weight:700;color:#60435F;cursor:grab;'
            'user-select:none;padding:2px 8px;border-radius:10px;background:#f3f1f8;">'
            "Move</div>"
        )
        with ui.element("div").style(
            "display:flex;flex-direction:column;gap:10px;align-items:center;"
        ):
            _build_color_buttons()
            _build_eraser_button()
            _build_fill_button()
            _build_brush_buttons()


def _build_color_buttons() -> None:
    for color, selected in PALETTE_COLORS:
        border = "3px solid #60435F" if selected else "2px solid #d1d5db"
        sel = "true" if selected else "false"
        ui.html(
            f'<button type="button" data-paint-color="{color}" data-selected="{sel}" '
            f'style="width:38px;height:38px;border-radius:999px;border:{border};'
            f'background:{color};cursor:pointer;"></button>'
        )


def _build_eraser_button() -> None:
    ui.html(
        '<button type="button" data-paint-color="__eraser__" data-selected="false" title="Eraser" '
        'style="width:38px;height:38px;border-radius:999px;border:2px solid #d1d5db;'
        'background:linear-gradient(135deg,#ffffff,#ececec);cursor:pointer;'
        'display:flex;align-items:center;justify-content:center;color:#60435F;'
        'font-size:11px;font-weight:900;">ER</button>'
    )


def _build_fill_button() -> None:
    ui.html(
        '<div style="width:100%;height:1px;background:#d8d2d2;"></div>'
        '<button type="button" id="paint-fill-btn" data-fill-active="false" title="Fill" '
        'style="width:38px;height:38px;border-radius:999px;border:2px solid #d1d5db;'
        'background:linear-gradient(135deg,#e0f2fe,#bae6fd);cursor:pointer;'
        'display:flex;align-items:center;justify-content:center;color:#60435F;'
        'font-size:18px;font-weight:900;">\U0001FAA3</button>'
    )


def _build_brush_buttons() -> None:
    sizes = [(6, False, 30), (12, True, 34), (20, False, 40)]
    dots = [6, 10, 14]
    btns = ""
    for (sz, sel, dim), dot in zip(sizes, dots):
        border = "3px solid #60435F" if sel else "2px solid #d1d5db"
        btns += (
            f'<button type="button" data-brush-size="{sz}" '
            f'data-brush-selected="{"true" if sel else "false"}" '
            f'style="width:{dim}px;height:{dim}px;border-radius:999px;border:{border};'
            f'background:#ffffff;cursor:pointer;display:flex;align-items:center;justify-content:center;">'
            f'<span style="width:{dot}px;height:{dot}px;border-radius:999px;background:#60435F;display:block;"></span>'
            "</button>"
        )
    ui.html(
        '<div style="width:100%;height:1px;background:#d8d2d2;"></div>'
        '<div style="font-size:13px;font-weight:800;color:#60435F;text-align:center;">Brush</div>'
        f'<div style="display:flex;gap:8px;justify-content:center;">{btns}</div>'
    )


def _build_card_grid(base_url: str, indices: list[int], detail_mode: bool) -> None:
    cols = "1" if detail_mode else "3"
    with ui.element("div").style(
        f"display:grid;grid-template-columns:repeat({cols},minmax(220px,1fr));"
        "gap:40px;width:min(95vw,1400px);"
    ):
        for i in indices:
            _build_paint_card(base_url, i, detail_mode)


def _build_paint_card(base_url: str, index: int, detail_mode: bool) -> None:
    open_url = f"{base_url}/{index + 1}"
    cursor = "crosshair" if detail_mode else "pointer"
    extra_style = "" if detail_mode else "cursor:pointer;"

    overview_note = ""
    if not detail_mode:
        overview_note = (
            '<div style="text-align:center;padding:0 10px 10px 10px;">'
            '<span style="font-weight:700;color:#60435F;font-size:15px;">'
            "Tap the paint area to continue on a full page</span></div>"
        )

    ui.html(
        '<div class="paint-card" '
        'style="background:#fff;border-radius:32px;border:3px solid #60435f99;'
        'box-shadow:0 8px 24px rgba(96,67,95,0.8);display:flex;flex-direction:column;gap:10px;">'
        # Instruction
        f'<div class="paint-instruction" data-paint-instruction="{index}" '
        'style="padding:10px;font-weight:600;text-align:center;color:#60435F;font-size:20px;"></div>'
        # Paint area
        f'<div class="paint-area" data-open-paint-url="{open_url}" '
        f'style="position:relative;height:650px;background:#fff;border-radius:18px;overflow:hidden;{extra_style}">'
        f'<div class="paint-target-slot" data-paint-slot="{index}" '
        'style="position:absolute;inset:0;display:flex;justify-content:center;align-items:center;'
        'pointer-events:none;z-index:1;"></div>'
        f'<canvas class="paint-canvas" width="1000" height="600" '
        'style="position:absolute;inset:0;display:block;width:100%;height:100%;'
        f'background:transparent;touch-action:none;cursor:{cursor};z-index:2;"></canvas>'
        f'<div class="paint-color-key-area" data-color-key-overlay="{index}" '
        'style="display:none;position:absolute;left:12px;top:50%;transform:translateY(-50%);'
        'z-index:10;pointer-events:auto;"></div>'
        "</div>"
        # Hint button
        '<div style="text-align:center;padding:8px 10px;">'
        f'<button type="button" class="paint-hint-btn" data-hint-index="{index}" '
        'style="padding:8px 22px;border-radius:18px;border:2.5px solid #60435F;'
        'background:linear-gradient(135deg,#ede9fe,#fce7f3);color:#60435F;'
        'font-weight:800;font-size:16px;cursor:pointer;transition:transform .15s,box-shadow .15s;" '
        "onmouseover=\"this.style.transform='scale(1.06)';this.style.boxShadow='0 4px 12px rgba(96,67,95,0.3)'\" "
        "onmouseout=\"this.style.transform='scale(1)';this.style.boxShadow='none'\">"
        '<img src="/images/icons/machine-learning.svg" '
        'style="width:22px;height:22px;vertical-align:middle;margin-right:6px;">Hint</button></div>'
        # Overview note + hint overlay
        f"{overview_note}"
        f'<div class="paint-hint-area" data-hint-overlay="{index}" '
        'style="display:none;justify-content:center;align-items:center;padding:12px 0 16px 0;"></div>'
        "</div>"
    )
