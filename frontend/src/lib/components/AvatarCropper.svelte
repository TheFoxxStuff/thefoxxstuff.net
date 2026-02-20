<script>
  import { onMount, onDestroy } from 'svelte';
  import { X, Check, ZoomIn, ZoomOut } from 'lucide-svelte';

  let { file, onconfirm, oncancel } = $props();

  // ── Canvas ref ──────────────────────────────────────────────────────
  let canvas   = $state(null);
  let ctx      = null;
  let img      = null;

  // ── State (plain JS, не $state — рисуем через requestAnimationFrame) ─
  let imgW = 0, imgH = 0;
  let offsetX = 0, offsetY = 0;   // смещение центра изображения от центра canvas
  let scale   = 1;
  const SIZE  = 268;               // диаметр круга в px

  // ── Drag ─────────────────────────────────────────────────────────────
  let pointers = {};               // pointerId → {x, y}
  let lastDist = 0;                // для pinch-zoom
  let isDragging = false;
  let dragStartX = 0, dragStartY = 0;
  let dragStartOX = 0, dragStartOY = 0;

  // ── Slider ───────────────────────────────────────────────────────────
  let sliderVal = $state(0.5);    // 0..1 → minScale..maxScale
  let uploading = $state(false);

  // ── Scale bounds ─────────────────────────────────────────────────────
  function minScale() {
    if (!imgW || !imgH) return 1;
    // Минимум: изображение целиком закрывает круг
    return Math.max(SIZE / imgW, SIZE / imgH);
  }
  function maxScale() { return minScale() * 5; }
  function sliderToScale(v) { return minScale() + v * (maxScale() - minScale()); }
  function scaleToSlider(s) { return (s - minScale()) / (maxScale() - minScale()); }

  // ── Clamp offset ─────────────────────────────────────────────────────
  // Изображение ВСЕГДА покрывает круг — не даём ему сдвинуться так
  // чтобы края изображения оказались внутри круга.
  function clampOffset(ox, oy, s) {
    const hw = (imgW * s) / 2;  // полуширина изображения
    const hh = (imgH * s) / 2;  // полувысота изображения
    const r  = SIZE / 2;         // радиус круга
    // Максимальный сдвиг центра изображения от центра canvas:
    // hw - r (если изображение шире круга, его центр может сместиться на hw-r)
    const maxOX = Math.max(0, hw - r);
    const maxOY = Math.max(0, hh - r);
    return {
      ox: Math.max(-maxOX, Math.min(maxOX, ox)),
      oy: Math.max(-maxOY, Math.min(maxOY, oy)),
    };
  }

  // ── Draw ─────────────────────────────────────────────────────────────
  function draw() {
    if (!ctx || !img || !canvas) return;
    const C = SIZE;
    ctx.clearRect(0, 0, C, C);

    // Изображение: рисуем по центру + offset
    const iw = imgW * scale;
    const ih = imgH * scale;
    const ix = C / 2 - iw / 2 + offsetX;
    const iy = C / 2 - ih / 2 + offsetY;
    ctx.drawImage(img, ix, iy, iw, ih);

    // Тёмная маска вне круга
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, C, C);
    ctx.arc(C / 2, C / 2, C / 2, 0, Math.PI * 2, true); // вырезаем круг
    ctx.fillStyle = 'rgba(0,0,0,0.55)';
    ctx.fill('evenodd');
    ctx.restore();

    // Кольцо
    ctx.save();
    ctx.beginPath();
    ctx.arc(C / 2, C / 2, C / 2 - 1, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();
  }

  // ── Init ─────────────────────────────────────────────────────────────
  onMount(() => {
    ctx = canvas.getContext('2d');
    img = new window.Image();
    img.onload = () => {
      imgW = img.naturalWidth;
      imgH = img.naturalHeight;
      scale = minScale();          // начальный scale: изображение вписывается в круг
      offsetX = 0;
      offsetY = 0;
      sliderVal = 0;               // слайдер в минимуме
      draw();
    };
    img.src = URL.createObjectURL(file);
  });

  onDestroy(() => {
    if (img?.src?.startsWith('blob:')) URL.revokeObjectURL(img.src);
  });

  // ── Zoom ─────────────────────────────────────────────────────────────
  function setScale(newScale) {
    const s = Math.max(minScale(), Math.min(maxScale(), newScale));
    const clamped = clampOffset(offsetX, offsetY, s);
    scale   = s;
    offsetX = clamped.ox;
    offsetY = clamped.oy;
    sliderVal = scaleToSlider(s);
    draw();
  }

  function onSlider(e) {
    setScale(sliderToScale(parseFloat(e.target.value)));
  }

  function onWheel(e) {
    e.preventDefault();
    setScale(scale * (e.deltaY < 0 ? 1.08 : 0.93));
  }

  // ── Pointer events (mouse + touch + pinch) ───────────────────────────
  function onPointerDown(e) {
    e.preventDefault();
    canvas.setPointerCapture(e.pointerId);
    pointers[e.pointerId] = { x: e.clientX, y: e.clientY };

    const pts = Object.values(pointers);
    if (pts.length === 1) {
      isDragging  = true;
      dragStartX  = e.clientX;
      dragStartY  = e.clientY;
      dragStartOX = offsetX;
      dragStartOY = offsetY;
    } else if (pts.length === 2) {
      isDragging = false;
      lastDist = Math.hypot(pts[1].x - pts[0].x, pts[1].y - pts[0].y);
    }
  }

  function onPointerMove(e) {
    if (!pointers[e.pointerId]) return;
    pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
    const pts = Object.values(pointers);

    if (pts.length === 2) {
      // Pinch zoom
      const dist = Math.hypot(pts[1].x - pts[0].x, pts[1].y - pts[0].y);
      setScale(scale * (dist / lastDist));
      lastDist = dist;
    } else if (isDragging && pts.length === 1) {
      // Pan
      const dx = e.clientX - dragStartX;
      const dy = e.clientY - dragStartY;
      const clamped = clampOffset(dragStartOX + dx, dragStartOY + dy, scale);
      offsetX = clamped.ox;
      offsetY = clamped.oy;
      draw();
    }
  }

  function onPointerUp(e) {
    delete pointers[e.pointerId];
    if (Object.keys(pointers).length === 0) isDragging = false;
  }

  // ── Crop & upload ─────────────────────────────────────────────────────
  // Вычисляем crop в координатах ОРИГИНАЛЬНОГО изображения
  function getCropRect() {
    const C   = SIZE;
    const iw  = imgW * scale;
    const ih  = imgH * scale;
    const ix  = C / 2 - iw / 2 + offsetX;  // left edge of image in canvas coords
    const iy  = C / 2 - ih / 2 + offsetY;  // top  edge of image in canvas coords

    // Пересечение круга (0..SIZE) с изображением (ix..ix+iw, iy..iy+ih)
    const cropLeft   = Math.max(0, -ix);         // в canvas px
    const cropTop    = Math.max(0, -iy);
    const cropRight  = Math.min(iw, C - ix);
    const cropBottom = Math.min(ih, C - iy);

    // В оригинальных пикселях
    const sx = Math.round(cropLeft   / scale);
    const sy = Math.round(cropTop    / scale);
    const sw = Math.round((cropRight - cropLeft)  / scale);
    const sh = Math.round((cropBottom - cropTop)  / scale);

    // API ожидает квадратный кроп (cx, cy, size) — берём min стороны
    // Центрируем квадрат внутри прямоугольника
    const cs = Math.min(sw, sh, imgW - sx, imgH - sy);
    const cx = sx + Math.round((sw - cs) / 2);
    const cy = sy + Math.round((sh - cs) / 2);

    return { cx: Math.max(0, cx), cy: Math.max(0, cy), cs: Math.max(1, cs) };
  }

  async function confirm() {
    uploading = true;
    try {
      const { cx, cy, cs } = getCropRect();
      await onconfirm(file, cx, cy, cs);
    } finally {
      uploading = false;
    }
  }
</script>

<!-- Modal overlay -->
<div class="overlay" role="dialog" aria-modal="true">
  <div class="modal">

    <div class="header">
      <span class="title">Crop avatar</span>
      <button class="close-btn" onclick={oncancel}><X size={18}/></button>
    </div>

    <!-- Canvas -->
    <div class="canvas-wrap">
      <canvas
        bind:this={canvas}
        width={SIZE}
        height={SIZE}
        style="width:{SIZE}px;height:{SIZE}px;border-radius:50%;display:block;cursor:grab;touch-action:none;"
        onpointerdown={onPointerDown}
        onpointermove={onPointerMove}
        onpointerup={onPointerUp}
        onpointercancel={onPointerUp}
        onwheel={onWheel}
      ></canvas>
    </div>

    <!-- Zoom slider -->
    <div class="zoom-row">
      <button class="zoom-btn" onclick={() => setScale(scale / 1.15)}><ZoomOut size={16}/></button>
      <input
        type="range" min="0" max="1" step="0.001"
        value={sliderVal}
        oninput={onSlider}
        class="slider"
      />
      <button class="zoom-btn" onclick={() => setScale(scale * 1.15)}><ZoomIn size={16}/></button>
    </div>

    <p class="hint">Drag to position · Scroll or pinch to zoom</p>

    <div class="footer">
      <button class="btn-cancel" onclick={oncancel}>Cancel</button>
      <button class="btn-apply" onclick={confirm} disabled={uploading}>
        <Check size={15}/>
        {uploading ? 'Uploading…' : 'Apply'}
      </button>
    </div>

  </div>
</div>

<style>
  .overlay {
    position: fixed; inset: 0; z-index: 10001;
    background: rgba(0,0,0,0.8);
    backdrop-filter: blur(10px);
    display: flex; align-items: center; justify-content: center;
    padding: 16px;
  }
  .modal {
    background: #111;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 24px;
    width: 100%; max-width: 340px;
    display: flex; flex-direction: column; gap: 18px;
  }
  .header {
    display: flex; align-items: center; justify-content: space-between;
  }
  .title {
    font-family: DrukWideCyr, sans-serif;
    font-size: 18px; letter-spacing: 0.04em; color: #fff;
  }
  .close-btn {
    width: 32px; height: 32px; border-radius: 8px;
    background: rgba(255,255,255,0.07); border: none;
    color: rgba(255,255,255,0.5); cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: background .12s, color .12s;
  }
  .close-btn:hover { background: rgba(255,255,255,0.12); color: #fff; }

  .canvas-wrap {
    display: flex; justify-content: center;
    /* Clip на случай если браузер не клипает canvas с border-radius */
    border-radius: 50%;
    overflow: hidden;
    width: fit-content;
    margin: 0 auto;
  }

  .zoom-row {
    display: flex; align-items: center; gap: 12px;
  }
  .zoom-btn {
    width: 34px; height: 34px; border-radius: 8px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.5); cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: background .12s, color .12s; flex-shrink: 0;
  }
  .zoom-btn:hover { background: rgba(255,255,255,0.12); color: #fff; }
  .slider { flex: 1; accent-color: #4ade80; cursor: pointer; }

  .hint {
    font-size: 11px; color: rgba(255,255,255,0.25);
    text-align: center; margin: -6px 0;
  }

  .footer { display: flex; gap: 8px; }
  .btn-cancel, .btn-apply {
    flex: 1; display: inline-flex; align-items: center; justify-content: center;
    gap: 6px; padding: 11px 16px; border-radius: 10px;
    font-size: 14px; font-weight: 500; cursor: pointer; border: none;
    font-family: inherit; transition: background .12s, opacity .12s;
  }
  .btn-cancel {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.6);
  }
  .btn-cancel:hover { background: rgba(255,255,255,0.12); color: #fff; }
  .btn-apply { background: #4ade80; color: #0a0a0a; font-weight: 600; }
  .btn-apply:hover { background: #6ee7a0; }
  .btn-apply:disabled { opacity: 0.45; cursor: not-allowed; }
</style>
