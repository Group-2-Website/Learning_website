from __future__ import annotations
from nicegui import ui
from models.subject import Subject
from models.topic import Topic
from ui.pages.common import _build_page_header


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
                        ("#34303b", True), # (color, selected)
                        ("#4361ee", False),
                        ("#6BBFFF", False),
                        ("#38b031", False),
                        ("#7EC88A", False),
                        ("#31b09f", False),
                        ("#f72585", False),
                        ("#D67AB1", False),
                        ("#FF8C69", False),
                        ("#f4a261", False),
                        ("#FFAD05", False),
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
                "gap:40px;width:min(95vw,1400px);"
            ):
                for i in range(3):
                    ui.html(
                        '<div class="paint-card"'
                        'style="background:#fff;border-radius:32px;border:3px solid #60435f99;'
                        'box-shadow:0 8px 24px rgba(96,67,95,0.8);display:flex;flex-direction:column;gap:10px;">'
                        f'<div class="paint-instruction" data-paint-instruction="{i}" '
                        'style="padding:10px;font-weight:800;text-align:center;color:#60435F;font-size:30px;">'
                        '</div>'
                        '<div class="paint-area" '
                        'style="position:relative;height:600px;background:#fff;'
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

              // Keep the original instruction text from the topic HTML (e.g. "Paint 2/3").
              const pageInstruction = page.firstElementChild ? page.firstElementChild.textContent.trim() : '';
              if (instructions[index] && pageInstruction) {
                instructions[index].textContent = pageInstruction;
              }

              const target = page.querySelector('[data-target-num][data-target-den]') || page; slot.dataset.bound = 'true';
              const cloned = target.cloneNode(true); cloned.querySelectorAll('img').forEach(function (img) { img.style.width = 'min(92%,720px)'; img.style.maxWidth = '720px'; img.style.height = 'auto'; });
              slot.appendChild(cloned);

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
