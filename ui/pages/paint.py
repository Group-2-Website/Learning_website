from __future__ import annotations
from nicegui import ui
from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _build_page_header


def build_paint_page(subject: Subject, topic: Topic, page_index: int | str | None = None) -> None:
    normalized_page_index: int | None = None
    if page_index is not None:
        try:
            normalized_page_index = int(page_index)
        except (TypeError, ValueError):
            normalized_page_index = None

    base_paint_dest = f"/{subject.url_slug}/{topic.name.lower()}/paint"
    back_dest = base_paint_dest if normalized_page_index is not None else f"/{subject.url_slug}/{topic.name.lower()}"
    active_indices = [normalized_page_index - 1] if normalized_page_index in (1, 2, 3) else list(range(3))
    detail_mode = normalized_page_index in (1, 2, 3)

    with ui.element("div").classes("page-content"):
        _build_page_header(
            back_dest, f"Back ",
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
                    'user-select:none;padding:2px 8px;border-radius:10px;background:#f3f1f8;">'
                    'Move</div>'
                )
                with ui.element("div").style("display:flex;flex-direction:column;gap:10px;align-items:center;"):
                    palette_colors = [
                        ("#2F2A3A", True),  # Dark outline
                        # Blues
                        ("#4F7BFF", False),  # Primary blue
                        ("#7ED3FF", False),  # Light sky blue
                        # Greens (shapes)
                        ("#4CD137", False),  # Bright green
                        ("#9BE7A1", False),  # Soft mint
                        # Teal (accent)
                        ("#38C9B9", False),
                        #red
                        ("#b00b10", False),  # Bright red
                        # Pinks / Purples
                        ("#FF4FA3", False),  # Strong pink
                        ("#E6A6D7", False),  # Soft pastel pink
                        # Oranges
                        ("#FF9A5A", False),  # Warm orange
                        ("#FFC27A", False),  # Soft peach
                        # Yellow
                        ("#FFD84D", False),  # Bright cartoon yellow
                        # White
                        ("#FFFFFF", False),
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

                    ui.html(
                        '<button type="button" data-paint-color="__eraser__" data-selected="false" '
                        'title="Eraser" '
                        'style="width:38px;height:38px;border-radius:999px;border:2px solid #d1d5db;'
                        'background:linear-gradient(135deg,#ffffff,#ececec);cursor:pointer;'
                        'display:flex;align-items:center;justify-content:center;color:#60435F;'
                        'font-size:11px;font-weight:900;">ER</button>'
                    )

                    ui.html(
                        '<div style="width:100%;height:1px;background:#d8d2d2;"></div>'
                        '<div style="font-size:13px;font-weight:800;color:#60435F;text-align:center;">Brush</div>'
                        '<div style="display:flex;gap:8px;justify-content:center;">'
                        '<button type="button" data-brush-size="6" data-brush-selected="false" '
                        'style="width:30px;height:30px;border-radius:999px;border:2px solid #d1d5db;background:#ffffff;cursor:pointer;display:flex;align-items:center;justify-content:center;">'
                        '<span style="width:6px;height:6px;border-radius:999px;background:#60435F;display:block;"></span>'
                        '</button>'
                        '<button type="button" data-brush-size="12" data-brush-selected="true" '
                        'style="width:34px;height:34px;border-radius:999px;border:3px solid #60435F;background:#ffffff;cursor:pointer;display:flex;align-items:center;justify-content:center;">'
                        '<span style="width:10px;height:10px;border-radius:999px;background:#60435F;display:block;"></span>'
                        '</button>'
                        '<button type="button" data-brush-size="20" data-brush-selected="false" '
                        'style="width:40px;height:40px;border-radius:999px;border:2px solid #d1d5db;background:#ffffff;cursor:pointer;display:flex;align-items:center;justify-content:center;">'
                        '<span style="width:14px;height:14px;border-radius:999px;background:#60435F;display:block;"></span>'
                        '</button>'
                        '</div>'
                    )

            grid_columns = "1" if detail_mode else "3"
            with ui.element("div").style(
                f"display:grid;grid-template-columns:repeat({grid_columns},minmax(220px,1fr));"
                "gap:40px;width:min(95vw,1400px);"
            ):
                for i in active_indices:
                    open_url = f"{base_paint_dest}/{i + 1}"
                    area_style = (
                        "position:relative;height:650px;background:#fff;"
                        "border-radius:18px;overflow:hidden;"
                    )
                    if not detail_mode:
                        area_style += "cursor:pointer;"

                    overview_note = ""
                    if not detail_mode:
                        overview_note = (
                            '<div style="text-align:center;padding:0 10px 10px 10px;">'
                            '<span style="font-weight:700;color:#60435F;font-size:15px;">'
                            'Tap the paint area to continue on a full page'
                            '</span>'
                            '</div>'
                        )

                    ui.html(
                        '<div class="paint-card"'
                        'style="background:#fff;border-radius:32px;border:3px solid #60435f99;'
                        'box-shadow:0 8px 24px rgba(96,67,95,0.8);display:flex;flex-direction:column;gap:10px;">'
                        f'<div class="paint-instruction" data-paint-instruction="{i}" '
                        'style="padding:10px;font-weight:600;text-align:center;color:#60435F;font-size:20px;">'
                        '</div>'
                        f'<div class="paint-area" data-open-paint-url="{open_url}" '
                        f'style="{area_style}">'
                        f'<div class="paint-target-slot" data-paint-slot="{i}" '
                        'style="position:absolute;inset:0;display:flex;justify-content:center;align-items:center;'
                        'pointer-events:none;z-index:1;"></div>'
                        '<canvas class="paint-canvas"  width="1000" height="600" '
                        'style="position:absolute;inset:0;display:block;width:100%;height:100%;'
                        f'background:transparent;touch-action:none;cursor:{"crosshair" if detail_mode else "pointer"};z-index:2;">'
                        '</canvas>'
                        f'<div class="paint-color-key-area" data-color-key-overlay="{i}" '
                        'style="display:none;position:absolute;left:12px;top:50%;transform:translateY(-50%);'
                        'z-index:10;pointer-events:auto;">'
                        '</div>'
                        '</div>'
                        '<div style="text-align:center;padding:8px 10px;">'
                        f'<button type="button" class="paint-hint-btn" data-hint-index="{i}" '
                        'style="padding:8px 22px;border-radius:18px;border:2.5px solid #60435F;'
                        'background:linear-gradient(135deg,#ede9fe,#fce7f3);color:#60435F;'
                        'font-weight:800;font-size:16px;cursor:pointer;'
                        'transition:transform 0.15s,box-shadow 0.15s;"'
                        ' onmouseover="this.style.transform=\'scale(1.06)\';this.style.boxShadow=\'0 4px 12px rgba(96,67,95,0.3)\'"'
                        ' onmouseout="this.style.transform=\'scale(1)\';this.style.boxShadow=\'none\'"'
                        '><img src="/images/icons/machine-learning.svg" style="width:22px;height:22px;vertical-align:middle;margin-right:6px;">Hint</button>'
                        '</div>'
                        f'{overview_note}'
                        f'<div class="paint-hint-area" data-hint-overlay="{i}" '
                        'style="display:none;justify-content:center;align-items:center;'
                        'padding:12px 0 16px 0;">'
                        '</div>'
                        '</div>'
                    )
                paint_body_html()


    body_html = topic.paint_body_html()
    if body_html:
        ui.add_body_html(body_html)


def paint_body_html() -> None:
    ui.add_body_html("""
        <script>
        (function () {
          const ERASER_COLOR_TOKEN = '__eraser__';
          const PAINT_COLOR_KEY = 'kidslearn-paint-color';
          const BRUSH_SIZE_KEY = 'kidslearn-brush-size';
          const savedColor = localStorage.getItem(PAINT_COLOR_KEY);
          const savedBrushSize = Number(localStorage.getItem(BRUSH_SIZE_KEY));
          window.__kidslearnPaintColor = savedColor || window.__kidslearnPaintColor || '#2F2A3A';
          window.__kidslearnBrushSize = savedBrushSize > 0 ? savedBrushSize : (window.__kidslearnBrushSize || 12);

          const getPaintPages = function () {
            const source = document.getElementById('paint-visual-source');
            return source ? source.querySelectorAll('.paint-page') : [];
          };

          const selectPaletteButton = function (button) {
            document.querySelectorAll('[data-paint-color]').forEach(function (item) {
              item.dataset.selected = 'false';
              item.style.border = '2px solid #d1d5db';
            });
            button.dataset.selected = 'true';
            button.style.border = '3px solid #60435F';
          };

          const syncPaletteSelection = function () {
            let matched = false;
            document.querySelectorAll('[data-paint-color]').forEach(function (item) {
              if (item.dataset.paintColor === window.__kidslearnPaintColor) {
                selectPaletteButton(item);
                matched = true;
              }
            });

            if (!matched) {
              const fallback = document.querySelector('[data-paint-color][data-selected="true"]') ||
                               document.querySelector('[data-paint-color]');
              if (!fallback) return;
              window.__kidslearnPaintColor = fallback.dataset.paintColor;
              localStorage.setItem(PAINT_COLOR_KEY, window.__kidslearnPaintColor);
              selectPaletteButton(fallback);
            }
          };

          const selectBrushButton = function (button) {
            document.querySelectorAll('[data-brush-size]').forEach(function (item) {
              item.dataset.brushSelected = 'false';
              item.style.border = '2px solid #d1d5db';
            });
            button.dataset.brushSelected = 'true';
            button.style.border = '3px solid #60435F';
          };

          const syncBrushSelection = function () {
            let matched = false;
            document.querySelectorAll('[data-brush-size]').forEach(function (item) {
              if (Number(item.dataset.brushSize) === Number(window.__kidslearnBrushSize)) {
                selectBrushButton(item);
                matched = true;
              }
            });

            if (!matched) {
              const fallback = document.querySelector('[data-brush-size][data-brush-selected="true"]') ||
                               document.querySelector('[data-brush-size]');
              if (!fallback) return;
              window.__kidslearnBrushSize = Number(fallback.dataset.brushSize);
              localStorage.setItem(BRUSH_SIZE_KEY, String(window.__kidslearnBrushSize));
              selectBrushButton(fallback);
            }
          };

          if (!window.__kidslearnPaletteBound) {
            window.__kidslearnPaletteBound = true;
            document.addEventListener('click', function (event) {
              const palette = event.target.closest('[data-paint-color]');
              if (palette) {
                window.__kidslearnPaintColor = palette.dataset.paintColor;
                localStorage.setItem(PAINT_COLOR_KEY, window.__kidslearnPaintColor);
                selectPaletteButton(palette);
              }

              const brush = event.target.closest('[data-brush-size]');
              if (brush) {
                window.__kidslearnBrushSize = Number(brush.dataset.brushSize);
                localStorage.setItem(BRUSH_SIZE_KEY, String(window.__kidslearnBrushSize));
                selectBrushButton(brush);
              }
            });
          }

          const bindPaintAreaOpen = function () {
            const areas = document.querySelectorAll('.paint-area[data-open-paint-url]');
            if (areas.length <= 1) return;

            areas.forEach(function (area) {
              if (area.dataset.openBound === 'true') return;
              area.dataset.openBound = 'true';
              area.addEventListener('click', function () {
                const dest = area.dataset.openPaintUrl;
                if (dest) window.location.href = dest;
              });
            });
          };

          const mountVisualTargets = function () {
            const pages = getPaintPages();
            if (!pages.length) return;

            const isOverviewMode = document.querySelectorAll('.paint-canvas').length > 1;

            document.querySelectorAll('.paint-target-slot').forEach(function (slot) {
              if (slot.dataset.bound === 'true') return;

              const slotIndex = Number(slot.dataset.paintSlot || '0');
              const page = pages[slotIndex];
              if (!page) return;

              const instruction = document.querySelector('[data-paint-instruction="' + slotIndex + '"]');
              const pageInstruction = page.firstElementChild ? page.firstElementChild.textContent.trim() : '';
              if (instruction && pageInstruction) {
                instruction.textContent = pageInstruction;
              }

              slot.dataset.bound = 'true';
              const target = page.querySelector('[data-target-num][data-target-den]') || page;
              const cloned = target.cloneNode(true);
              if (isOverviewMode) {
                cloned.style.transform = 'translateX(18px)';
              }
              cloned.querySelectorAll('img').forEach(function (img) {
                img.style.width = 'min(92%,720px)';
                img.style.maxWidth = '720px';
                img.style.height = 'auto';
              });
              slot.appendChild(cloned);

              const meta = target.querySelector('[data-target-num][data-target-den]') || target;
              if (instruction && !pageInstruction && meta && meta.dataset.targetNum && meta.dataset.targetDen) {
                instruction.textContent = 'Paint ' + meta.dataset.targetNum + '/' + meta.dataset.targetDen;
              }
            });
          };

          const mountHints = function () {
            const pages = getPaintPages();
            if (!pages.length) return;

            document.querySelectorAll('[data-hint-overlay]').forEach(function (overlay) {
              if (overlay.dataset.hintBound === 'true') return;

              const slotIndex = Number(overlay.dataset.hintOverlay || '0');
              const page = pages[slotIndex];
              if (!page) return;

              const hint = page.querySelector('.paint-hint');
              if (!hint) return;

              overlay.dataset.hintBound = 'true';
              const cloned = hint.cloneNode(true);
              cloned.style.display = 'block';
              overlay.appendChild(cloned);
            });
          };

          const mountColorKeys = function () {
            const pages = getPaintPages();
            if (!pages.length) return;

            const canvases = document.querySelectorAll('.paint-canvas');
            const isDetailMode = canvases.length === 1;
            if (!isDetailMode) return;

            document.querySelectorAll('[data-color-key-overlay]').forEach(function (overlay) {
              if (overlay.dataset.colorKeyBound === 'true') return;

              const slotIndex = Number(overlay.dataset.colorKeyOverlay || '0');
              const page = pages[slotIndex];
              if (!page) return;

              const colorKey = page.querySelector('.paint-color-key-wrapper');
              if (!colorKey) return;

              overlay.dataset.colorKeyBound = 'true';
              const cloned = colorKey.cloneNode(true);
              cloned.style.display = 'block';
              overlay.appendChild(cloned);
              overlay.style.display = 'flex';
            });
          };

          if (!window.__kidslearnHintBound) {
            window.__kidslearnHintBound = true;
            document.addEventListener('click', function (event) {
              const btn = event.target.closest('.paint-hint-btn');
              if (!btn) return;

              const idx = btn.dataset.hintIndex;
              const overlay = document.querySelector('[data-hint-overlay="' + idx + '"]');
              if (!overlay) return;

              overlay.style.display = overlay.style.display === 'flex' ? 'none' : 'flex';
            });
          }

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

          const applyStrokeStyle = function (ctx, event) {
            const pressure = event.pressure && event.pressure > 0 ? event.pressure : 0.5;
            ctx.lineWidth = Number(window.__kidslearnBrushSize) * (0.6 + pressure);
            if (window.__kidslearnPaintColor === ERASER_COLOR_TOKEN) {
              ctx.globalCompositeOperation = 'destination-out';
              ctx.strokeStyle = 'rgba(0,0,0,1)';
            } else {
              ctx.globalCompositeOperation = 'source-over';
              ctx.strokeStyle = window.__kidslearnPaintColor;
            }
          };

          const bindCanvases = function () {
            const canvases = document.querySelectorAll('.paint-canvas');
            const isOverview = canvases.length > 1;

            canvases.forEach(function (canvas) {
              if (canvas.dataset.bound === 'true') return;
              canvas.dataset.bound = 'true';

              if (isOverview) {
                // On overview cards the paint area navigates to the dedicated page.
                canvas.style.pointerEvents = 'none';
                return;
              }

              const ctx = canvas.getContext('2d');
              if (!ctx) return;

              ctx.clearRect(0, 0, canvas.width, canvas.height);
              ctx.lineCap = 'round';
              ctx.lineJoin = 'round';

              let drawing = false;

              canvas.addEventListener('pointerdown', function (event) {
                drawing = true;
                canvas.setPointerCapture(event.pointerId);
                const p = pointFromEvent(canvas, event);
                applyStrokeStyle(ctx, event);
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p.x + 0.01, p.y + 0.01);
                ctx.stroke();
              });

              canvas.addEventListener('pointermove', function (event) {
                if (!drawing) return;
                const p = pointFromEvent(canvas, event);
                applyStrokeStyle(ctx, event);
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

          const runSetup = function () {
            syncPaletteSelection();
            syncBrushSelection();
            mountVisualTargets();
            mountHints();
            mountColorKeys();
            bindPaletteDrag();
            bindPaintAreaOpen();
            bindCanvases();
          };

          runSetup();
          requestAnimationFrame(runSetup);
          setTimeout(runSetup, 100);
        })();
        </script>
        """)