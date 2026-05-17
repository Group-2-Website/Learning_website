(function () {
  'use strict';

  /* ── Constants ── */
  const ERASER_TOKEN = '__eraser__';
  const COLOR_KEY   = 'kidslearn-paint-color';
  const BRUSH_KEY   = 'kidslearn-brush-size';

  /* ── Edge / browser detection ── */
  var isEdge = /Edg\//.test(navigator.userAgent);

  /* ── Safe localStorage wrapper (throws in Edge InPrivate mode) ── */
  var _ls = {
    get: function (k) { try { return localStorage.getItem(k); } catch (_) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (_) {} },
  };

  /* ── Persisted state ── */
  var savedColor = _ls.get(COLOR_KEY);
  var savedBrush = Number(_ls.get(BRUSH_KEY));
  window.__paintColor = savedColor || window.__paintColor || '#2F2A3A';
  window.__brushSize  = savedBrush > 0 ? savedBrush : (window.__brushSize || 12);
  window.__fillMode   = false;

  function getPaintPages() {
    var src = document.getElementById('paint-visual-source');
    return src ? src.querySelectorAll('.paint-page') : [];
  }

  function hexToRgb(hex) {
    hex = hex.replace('#', '');
    if (hex.length === 3) hex = hex[0]+hex[0]+hex[1]+hex[1]+hex[2]+hex[2];
    return {
      r: parseInt(hex.substring(0, 2), 16),
      g: parseInt(hex.substring(2, 4), 16),
      b: parseInt(hex.substring(4, 6), 16),
    };
  }

  function clamp(v, lo, hi) { return Math.min(Math.max(v, lo), hi); }

  function pointFromEvent(canvas, e) {
    var r = canvas.getBoundingClientRect();
    return {
      x: (e.clientX - r.left) * canvas.width  / (r.width  || 1),
      y: (e.clientY - r.top)  * canvas.height / (r.height || 1),
    };
  }

  /* ── FIX 1: Safe Element.closest() for Edge + SVG child targets ──
     Edge can surface SVG sub-elements (path, circle, etc.) as e.target,
     which may not have .closest() at all if they are raw SVGElement nodes
     without the full Element interface. Always walk up manually as a fallback. */
  function safeClosest(el, selector) {
    if (!el) return null;
    try {
      if (typeof el.closest === 'function') return el.closest(selector);
    } catch (_) { /* fall through */ }
    var node = el;
    while (node && node !== document) {
      try {
        if (node.matches && node.matches(selector)) return node;
      } catch (_) { /* keep walking */ }
      node = node.parentElement || node.parentNode;
    }
    return null;
  }

  /* ── Palette selection ── */
  function selectPaletteBtn(btn) {
    document.querySelectorAll('[data-paint-color]').forEach(function (b) {
      b.dataset.selected = 'false';
      b.style.border = '2px solid #d1d5db';
    });
    btn.dataset.selected = 'true';
    btn.style.border = '3px solid #60435F';
  }

  function syncPalette() {
    var matched = false;
    document.querySelectorAll('[data-paint-color]').forEach(function (b) {
      if (b.dataset.paintColor === window.__paintColor) { selectPaletteBtn(b); matched = true; }
    });
    if (!matched) {
      var fb = document.querySelector('[data-paint-color][data-selected="true"]') ||
               document.querySelector('[data-paint-color]');
      if (!fb) return;
      window.__paintColor = fb.dataset.paintColor;
      _ls.set(COLOR_KEY, window.__paintColor);
      selectPaletteBtn(fb);
    }
  }

  /* ── Brush selection ── */
  function selectBrushBtn(btn) {
    document.querySelectorAll('[data-brush-size]').forEach(function (b) {
      b.dataset.brushSelected = 'false';
      b.style.border = '2px solid #d1d5db';
    });
    btn.dataset.brushSelected = 'true';
    btn.style.border = '3px solid #60435F';
  }

  function syncBrush() {
    var matched = false;
    document.querySelectorAll('[data-brush-size]').forEach(function (b) {
      if (Number(b.dataset.brushSize) === Number(window.__brushSize)) { selectBrushBtn(b); matched = true; }
    });
    if (!matched) {
      var fb = document.querySelector('[data-brush-size][data-brush-selected="true"]') ||
               document.querySelector('[data-brush-size]');
      if (!fb) return;
      window.__brushSize = Number(fb.dataset.brushSize);
      _ls.set(BRUSH_KEY, String(window.__brushSize));
      selectBrushBtn(fb);
    }
  }

  /* ── Global click handler (palette / brush / fill toggle) ── */
  if (!window.__paintClickBound) {
    window.__paintClickBound = true;
    document.addEventListener('click', function (e) {
      var palBtn = safeClosest(e.target, '[data-paint-color]');
      if (palBtn) {
        window.__paintColor = palBtn.dataset.paintColor;
        _ls.set(COLOR_KEY, window.__paintColor);
        selectPaletteBtn(palBtn);
      }

      var brBtn = safeClosest(e.target, '[data-brush-size]');
      if (brBtn) {
        window.__brushSize = Number(brBtn.dataset.brushSize);
        _ls.set(BRUSH_KEY, String(window.__brushSize));
        selectBrushBtn(brBtn);
      }

      var fillBtn = safeClosest(e.target, '#paint-fill-btn');
      if (fillBtn) {
        window.__fillMode = !window.__fillMode;
        fillBtn.dataset.fillActive = window.__fillMode ? 'true' : 'false';
        fillBtn.style.border = window.__fillMode ? '3px solid #60435F' : '2px solid #d1d5db';
        fillBtn.style.background = window.__fillMode
          ? 'linear-gradient(135deg,#60435F,#D67AB5)' : 'linear-gradient(135deg,#e0f2fe,#bae6fd)';
        fillBtn.style.color = window.__fillMode ? '#fff' : '#60435F';
        document.querySelectorAll('.paint-canvas').forEach(function (c) {
          if (c.dataset.bound === 'true' && document.querySelectorAll('.paint-canvas').length === 1)
            c.style.cursor = window.__fillMode ? 'cell' : 'crosshair';
        });
      }

      var hintBtn = safeClosest(e.target, '.paint-hint-btn');
      if (hintBtn) {
        var idx = hintBtn.dataset.hintIndex;
        var ov = document.querySelector('[data-hint-overlay="' + idx + '"]');
        if (ov) ov.style.display = ov.style.display === 'flex' ? 'none' : 'flex';
      }
    });
  }

  function mountVisualTargets() {
    var pages = getPaintPages();
    if (!pages.length) return;
    var isOverview = document.querySelectorAll('.paint-canvas').length > 1;

    document.querySelectorAll('.paint-target-slot').forEach(function (slot) {
      if (slot.dataset.bound === 'true') return;
      var i = Number(slot.dataset.paintSlot || '0');
      var page = pages[i];
      if (!page) return;

      var instr = document.querySelector('[data-paint-instruction="' + i + '"]');
      var txt = page.firstElementChild ? page.firstElementChild.textContent.trim() : '';
      if (instr && txt) instr.textContent = txt;

      slot.dataset.bound = 'true';
      var target = page.querySelector('[data-target-num][data-target-den]') || page;
      var cloned = target.cloneNode(true);
      if (isOverview) cloned.style.transform = 'translateX(18px)';
      cloned.querySelectorAll('img').forEach(function (img) {
        img.style.width = 'min(90%,720px)';
        img.style.maxWidth = '680px';
        img.style.height = 'auto';
      });
      slot.appendChild(cloned);

      var meta = target.querySelector('[data-target-num][data-target-den]') || target;
      if (instr && !txt && meta && meta.dataset.targetNum && meta.dataset.targetDen)
        instr.textContent = 'Paint ' + meta.dataset.targetNum + '/' + meta.dataset.targetDen;
    });
  }

  function mountHints() {
    var pages = getPaintPages();
    if (!pages.length) return;
    document.querySelectorAll('[data-hint-overlay]').forEach(function (ov) {
      if (ov.dataset.hintBound === 'true') return;
      var page = pages[Number(ov.dataset.hintOverlay || '0')];
      if (!page) return;
      var hint = page.querySelector('.paint-hint');
      if (!hint) return;
      ov.dataset.hintBound = 'true';
      var cl = hint.cloneNode(true);
      cl.style.display = 'block';
      ov.appendChild(cl);
    });
  }

  function mountColorKeys() {
    var pages = getPaintPages();
    if (!pages.length) return;
    if (document.querySelectorAll('.paint-canvas').length !== 1) return;

    document.querySelectorAll('[data-color-key-overlay]').forEach(function (ov) {
      if (ov.dataset.colorKeyBound === 'true') return;
      var page = pages[Number(ov.dataset.colorKeyOverlay || '0')];
      if (!page) return;
      var ck = page.querySelector('.paint-color-key-wrapper');
      if (!ck) return;
      ov.dataset.colorKeyBound = 'true';
      var cl = ck.cloneNode(true);
      cl.style.display = 'block';
      ov.appendChild(cl);
      ov.style.display = 'flex';
    });
  }

  function bindPaintAreaOpen() {
    var areas = document.querySelectorAll('.paint-area[data-open-paint-url]');
    if (areas.length <= 1) return;
    areas.forEach(function (a) {
      if (a.dataset.openBound === 'true') return;
      a.dataset.openBound = 'true';
      a.addEventListener('click', function () {
        if (a.dataset.openPaintUrl) window.location.href = a.dataset.openPaintUrl;
      });
    });
  }

  function bindPaletteDrag() {
    var palette = document.getElementById('paint-palette');
    var handle  = document.getElementById('paint-palette-handle');
    if (!palette || !handle || palette.dataset.dragBound === 'true') return;
    palette.dataset.dragBound = 'true';

    var dragging = false, offX = 0, offY = 0;

    function setPos(left, top) {
      var r = palette.getBoundingClientRect();
      palette.style.left  = clamp(left, 0, Math.max(0, innerWidth  - r.width))  + 'px';
      palette.style.top   = clamp(top, 210, Math.max(210, innerHeight - r.height)) + 'px';
      palette.style.right = 'auto';
      palette.style.transform = 'none';
    }

    handle.addEventListener('pointerdown', function (e) {
      var r = palette.getBoundingClientRect();
      dragging = true; offX = e.clientX - r.left; offY = e.clientY - r.top;
      handle.style.cursor = 'grabbing';
      handle.setPointerCapture(e.pointerId);
      e.preventDefault();
    });
    handle.addEventListener('pointermove', function (e) {
      if (!dragging) return;
      e.preventDefault();
      setPos(e.clientX - offX, e.clientY - offY);
    });

    function stopDrag(e) {
      if (!dragging) return;
      dragging = false;
      handle.style.cursor = 'grab';
      if (e && handle.hasPointerCapture(e.pointerId)) handle.releasePointerCapture(e.pointerId);
    }
    handle.addEventListener('pointerup', stopDrag);
    handle.addEventListener('pointercancel', stopDrag);
    window.addEventListener('resize', function () {
      if (palette.style.left && palette.style.top) setPos(parseFloat(palette.style.left), parseFloat(palette.style.top));
    });
  }

  /* ── Stroke style (brush / eraser) ──────────────────────────────────────
     applyStrokeOnCtx works on any context — used for both the stroke
     offscreen canvas (brush/eraser) and baked-canvas erasing.

     ERASER on un-baked canvas: uses destination-out on the *stroke layer*
     (strokeCanvas), which is separate from the main canvas. The main canvas
     only contains user strokes, not the background image. So destination-out
     correctly punches holes through painted pixels revealing the image below,
     without ever touching the image itself. The image stays visible because
     the slot div (z-index 1) is still visible through the now-transparent hole.

     ERASER on baked canvas (after fill): restores the saved background
     texture using the __baseBg pattern as before. */
  function applyStrokeOnCtx(targetCtx, e, canvas) {
    var pressure = (e.pressure > 0) ? e.pressure : 0.5;
    targetCtx.lineWidth = Number(window.__brushSize) * (0.6 + pressure);

    if (window.__paintColor === ERASER_TOKEN) {
      if (canvas.dataset.imageBaked === 'true' && canvas.__baseBg) {
        targetCtx.globalCompositeOperation = 'source-over';
        if (!canvas.__baseBgPattern) canvas.__baseBgPattern = targetCtx.createPattern(canvas.__baseBg, 'no-repeat');
        targetCtx.strokeStyle = canvas.__baseBgPattern;
      } else {
        /* Erase on the stroke layer: punch through to transparent */
        targetCtx.globalCompositeOperation = 'destination-out';
        targetCtx.strokeStyle = 'rgba(0,0,0,1)';
      }
    } else {
      targetCtx.globalCompositeOperation = 'source-over';
      targetCtx.strokeStyle = window.__paintColor;
    }
  }

  /* Keep old name as alias so fillOnCanvas's eraser path still works */
  function applyStroke(ctx, e, canvas) { applyStrokeOnCtx(ctx, e, canvas); }

  /* ── Flood fill ── */
  function floodFill(ctx, sx, sy, color, w, h) {
    var imgData = ctx.getImageData(0, 0, w, h);
    var d = imgData.data;
    sx = Math.round(sx); sy = Math.round(sy);
    if (sx < 0 || sx >= w || sy < 0 || sy >= h) return;

    var si = (sy * w + sx) * 4;
    var sR = d[si], sG = d[si+1], sB = d[si+2], sA = d[si+3];
    var fill = hexToRgb(color);
    if (sR === fill.r && sG === fill.g && sB === fill.b && sA === 255) return;

    var tol = 40;
    function match(i) {
      return Math.abs(d[i]-sR)<=tol && Math.abs(d[i+1]-sG)<=tol && Math.abs(d[i+2]-sB)<=tol && Math.abs(d[i+3]-sA)<=tol;
    }

    var stack = [[sx, sy]], visited = new Uint8Array(w * h);
    while (stack.length) {
      var p = stack.pop(), x = p[0], y = p[1], pi = y * w + x;
      if (x < 0 || x >= w || y < 0 || y >= h || visited[pi]) continue;
      var idx = pi * 4;
      if (!match(idx)) continue;
      visited[pi] = 1;
      d[idx] = fill.r; d[idx+1] = fill.g; d[idx+2] = fill.b; d[idx+3] = 255;
      stack.push([x+1,y],[x-1,y],[x,y+1],[x,y-1]);
    }
    ctx.putImageData(imgData, 0, 0);
  }

  /* FIX 3: willReadFrequently so Edge doesn't GPU-optimise the canvas and
     break getImageData() used by flood fill. */
  function get2dCtx(canvas) {
    return canvas.getContext('2d', { willReadFrequently: true });
  }

  function fillOnCanvas(canvas, px, py, fillColor) {
    var w = canvas.width, h = canvas.height;
    var area = safeClosest(canvas, '.paint-area');
    var slot = area ? area.querySelector('.paint-target-slot') : null;

    /* After bake: work directly on the main canvas (image already composited) */
    if (canvas.dataset.imageBaked === 'true') {
      var off = document.createElement('canvas'); off.width = w; off.height = h;
      var oc = get2dCtx(off);
      oc.drawImage(canvas, 0, 0);
      floodFill(oc, px, py, fillColor, w, h);
      var c = get2dCtx(canvas);
      c.globalCompositeOperation = 'source-over';
      c.clearRect(0, 0, w, h);
      c.drawImage(off, 0, 0);
      return;
    }

    /* First fill: bake the background image + existing brush strokes into
       the main canvas, then flood-fill. The stroke canvas is also merged in
       so any brush strokes drawn before the fill are preserved. */
    function doFill(bgImg, dx, dy, dw, dh) {
      var off = document.createElement('canvas'); off.width = w; off.height = h;
      var oc = get2dCtx(off);
      oc.fillStyle = '#FFFFFF'; oc.fillRect(0, 0, w, h);
      if (bgImg && dw && dh) oc.drawImage(bgImg, dx, dy, dw, dh);

      /* Save background (image only, before strokes) for eraser restore */
      var bg = document.createElement('canvas'); bg.width = w; bg.height = h;
      get2dCtx(bg).drawImage(off, 0, 0);
      canvas.__baseBg = bg;

      /* Merge existing brush strokes on top of the background */
      oc.drawImage(canvas, 0, 0);

      floodFill(oc, px, py, fillColor, w, h);

      var c = get2dCtx(canvas);
      c.globalCompositeOperation = 'source-over';
      c.clearRect(0, 0, w, h);
      c.drawImage(off, 0, 0);
      if (slot) slot.style.display = 'none';
      canvas.dataset.imageBaked = 'true';
    }

    if (!slot) { doFill(null, 0, 0, 0, 0); return; }

    /* Try <img> */
    var imgEl = slot.querySelector('img');
    if (imgEl && imgEl.complete && (imgEl.naturalWidth || imgEl.width)) {
      var ar = area.getBoundingClientRect(), ir = imgEl.getBoundingClientRect();
      var sx = w / (ar.width||1), sy = h / (ar.height||1);
      doFill(imgEl, (ir.left-ar.left)*sx, (ir.top-ar.top)*sy, ir.width*sx, ir.height*sy);
      return;
    }

    /* Try <svg> — FIX 4: Edge canvas-taint workaround */
    var svgEl = slot.querySelector('svg');
    if (svgEl) {
      var ar2 = area.getBoundingClientRect(), sr2 = svgEl.getBoundingClientRect();
      var sx2 = w/(ar2.width||1), sy2 = h/(ar2.height||1);
      var dxS = (sr2.left-ar2.left)*sx2, dyS = (sr2.top-ar2.top)*sy2, dwS = sr2.width*sx2, dhS = sr2.height*sy2;

      var clone = svgEl.cloneNode(true);
      if (!clone.getAttribute('width') && dwS) clone.setAttribute('width', Math.round(dwS));
      if (!clone.getAttribute('height') && dhS) clone.setAttribute('height', Math.round(dhS));

      /* Use plain 'image/svg+xml' — Edge rejects the charset parameter */
      var blob = new Blob([new XMLSerializer().serializeToString(clone)], {type: 'image/svg+xml'});
      var url = URL.createObjectURL(blob);
      var tmp = new Image();
      tmp.crossOrigin = 'anonymous';
      tmp.onload = function () {
        var off = document.createElement('canvas'); off.width = w; off.height = h;
        var oc = get2dCtx(off);
        oc.fillStyle = '#FFFFFF'; oc.fillRect(0, 0, w, h);
        oc.drawImage(tmp, dxS, dyS, dwS, dhS);

        var bg = document.createElement('canvas'); bg.width = w; bg.height = h;
        get2dCtx(bg).drawImage(off, 0, 0);
        canvas.__baseBg = bg;

        oc.drawImage(canvas, 0, 0);
        floodFill(oc, px, py, fillColor, w, h);
        var c = get2dCtx(canvas);
        c.globalCompositeOperation = 'source-over';
        c.clearRect(0, 0, w, h);
        c.drawImage(off, 0, 0);
        if (slot) slot.style.display = 'none';
        canvas.dataset.imageBaked = 'true';
        URL.revokeObjectURL(url);
      };
      tmp.onerror = function () { URL.revokeObjectURL(url); doFill(null,0,0,0,0); };
      tmp.src = url;
      return;
    }

    doFill(null, 0, 0, 0, 0);
  }

  /* ── Bind drawing canvases ── */
  function bindCanvases() {
    var canvases = document.querySelectorAll('.paint-canvas');
    var isOverview = canvases.length > 1;

    canvases.forEach(function (canvas) {
      if (canvas.dataset.bound === 'true') return;
      canvas.dataset.bound = 'true';

      if (isOverview) { canvas.style.pointerEvents = 'none'; return; }

      /* Prevent page scroll while drawing on both Edge and Safari iOS. */
      canvas.style.touchAction = 'none';

      var ctx = get2dCtx(canvas);
      if (!ctx) return;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      /* ── Two-layer architecture ──────────────────────────────────────────
         The slot image sits under the canvas (z-index 1 vs 2). The canvas
         must stay transparent so the image shows through.

         strokeCanvas (offscreen): holds only user brush strokes.
         main canvas: always = composite of strokeCanvas, kept in sync.
         eraser: uses destination-out on strokeCanvas → punches holes back to
                 transparent → image below shows through. Works from first use.

         After fill bake: image is merged into main canvas, slot hidden.
         Strokes then go directly to main canvas. Eraser restores via __baseBg.
      ── */
      var strokeCanvas = document.createElement('canvas');
      strokeCanvas.width  = canvas.width;
      strokeCanvas.height = canvas.height;
      var sCtx = get2dCtx(strokeCanvas);
      sCtx.lineCap  = 'round';
      sCtx.lineJoin = 'round';

      function activeCtx() {
        return canvas.dataset.imageBaked === 'true' ? ctx : sCtx;
      }

      function syncToMain() {
        if (canvas.dataset.imageBaked === 'true') return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(strokeCanvas, 0, 0);
      }

      /* drawing flag + last point for path continuity */
      var drawing = false;
      var lastPt  = null;

      function startStroke(pt, pressure) {
        drawing = true;
        lastPt  = pt;
        var ac = activeCtx();
        applyStrokeOnCtx(ac, { pressure: pressure }, canvas);
        ac.beginPath();
        ac.moveTo(pt.x, pt.y);
        /* tiny stub so a tap/dot is always visible */
        ac.lineTo(pt.x + 0.01, pt.y + 0.01);
        ac.stroke();
        syncToMain();
      }

      function continueStroke(pt, pressure) {
        if (!drawing || !lastPt) return;
        var ac = activeCtx();
        applyStrokeOnCtx(ac, { pressure: pressure }, canvas);
        /* lineTo continues the open path — no beginPath here */
        ac.lineTo(pt.x, pt.y);
        ac.stroke();
        lastPt = pt;
        syncToMain();
      }

      function endStroke() {
        if (!drawing) return;
        drawing = false;
        lastPt  = null;
        activeCtx().closePath();
      }

      /* ── Use pointer events when available (Chrome, Edge, modern Safari) ──
         Safari fires BOTH pointer and touch events. We suppress the touch
         events when pointer events are working by checking pointerType.
         The `usingPointer` flag is set on pointerdown and cleared on pointerup
         so touch events are ignored for that gesture. */
      var usingPointer = false;

      canvas.addEventListener('pointerdown', function (e) {
        e.preventDefault();
        usingPointer = true;
        var p = pointFromEvent(canvas, e);
        if (window.__fillMode) {
          fillOnCanvas(canvas, p.x, p.y,
            window.__paintColor === ERASER_TOKEN ? '#FFFFFF' : window.__paintColor);
          return;
        }
        if (canvas.setPointerCapture) canvas.setPointerCapture(e.pointerId);
        startStroke(p, e.pressure);
      });

      canvas.addEventListener('pointermove', function (e) {
        if (!drawing) return;
        e.preventDefault();
        continueStroke(pointFromEvent(canvas, e), e.pressure);
      });

      canvas.addEventListener('pointerup', function (e) {
        usingPointer = false;
        endStroke();
        if (canvas.hasPointerCapture && canvas.hasPointerCapture(e.pointerId))
          canvas.releasePointerCapture(e.pointerId);
      });
      canvas.addEventListener('pointercancel', function (e) {
        usingPointer = false;
        endStroke();
      });

      /* ── Touch fallback (older Safari iOS, or when pointer events absent) ── */
      canvas.addEventListener('touchstart', function (e) {
        if (usingPointer) return; /* pointer events already handling this */
        e.preventDefault();
        var t = e.touches[0];
        var p = pointFromEvent(canvas, t);
        if (window.__fillMode) {
          fillOnCanvas(canvas, p.x, p.y,
            window.__paintColor === ERASER_TOKEN ? '#FFFFFF' : window.__paintColor);
          return;
        }
        startStroke(p, 0.5);
      }, { passive: false });

      canvas.addEventListener('touchmove', function (e) {
        if (usingPointer || !drawing) return;
        e.preventDefault();
        continueStroke(pointFromEvent(canvas, e.touches[0]), 0.5);
      }, { passive: false });

      canvas.addEventListener('touchend', function () {
        if (usingPointer) return;
        endStroke();
      });
    });
  }

  function setup() {
    syncPalette();
    syncBrush();
    mountVisualTargets();
    mountHints();
    mountColorKeys();
    bindPaletteDrag();
    bindPaintAreaOpen();
    bindCanvases();
  }

  window.__paintSetup = setup;

  setup();
  requestAnimationFrame(setup);
  setTimeout(setup, 100);
})();
