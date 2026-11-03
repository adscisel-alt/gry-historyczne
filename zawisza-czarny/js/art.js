'use strict';
/* =====================================================================
   ART — proceduralne „malowane” grafiki: tła, sprite'y, portrety, ikony.
   Wszystko rysowane pędzlem (setki półprzezroczystych pociągnięć),
   generowane raz przy starcie i trzymane w pamięci podręcznej.
   ===================================================================== */
const Art = (() => {
  let R = Math.random;
  function seed(a) { R = function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  const rnd = (a, b) => a + (b - a) * R();
  const pick = a => a[Math.floor(R() * a.length)];
  const cl = v => Math.max(0, Math.min(255, v | 0));
  const TAU = Math.PI * 2;
  function hx(h) { if (Array.isArray(h)) return h; h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]; }
  const rgb = (c, a = 1) => { c = hx(c); return `rgba(${cl(c[0])},${cl(c[1])},${cl(c[2])},${a})`; };
  function jc(h, j = 14) { const c = hx(h); const d = rnd(-j, j); return rgb([c[0] + d + rnd(-j / 2, j / 2), c[1] + d + rnd(-j / 2, j / 2), c[2] + d + rnd(-j / 2, j / 2)]); }
  function mix(a, b, t) { a = hx(a); b = hx(b); return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; }
  function gradAt(st, t) { t = Math.max(0, Math.min(1, t)); const n = st.length - 1; const i = Math.min(n - 1, Math.floor(t * n)); return mix(st[i], st[i + 1], t * n - i); }
  function cv(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }

  /* ---------- pędzel ---------- */
  function stroke(g, x, y, len, w, ang, col, a) {
    g.save(); g.translate(x, y); g.rotate(ang); g.globalAlpha = a; g.fillStyle = col;
    g.beginPath(); g.ellipse(0, 0, len / 2, w / 2, 0, 0, TAU); g.fill();
    g.globalAlpha = a * 0.55; g.strokeStyle = col; g.lineWidth = Math.max(0.8, w / 7);
    for (let i = 0; i < 3; i++) {
      const o = (R() - 0.5) * w;
      g.beginPath(); g.moveTo(-len / 2, o); g.quadraticCurveTo(0, o + (R() - 0.5) * w * 0.6, len / 2, o + (R() - 0.5) * w * 0.3); g.stroke();
    }
    g.restore();
  }
  const poly = pts => g => { g.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]); g.closePath(); };
  const rectP = (x, y, w, h) => g => g.rect(x, y, w, h);
  const ellP = (x, y, rx, ry) => g => g.ellipse(x, y, rx, ry, 0, 0, TAU);
  function bbox(pts) { let a = 1e9, b = 1e9, c = -1e9, d = -1e9; pts.forEach(p => { a = Math.min(a, p[0]); b = Math.min(b, p[1]); c = Math.max(c, p[0]); d = Math.max(d, p[1]); }); return [a - 4, b - 4, c - a + 8, d - b + 8]; }

  /* Zamalowuje kształt: kolor bazowy + wiele pociągnięć pędzla wewnątrz (clip) */
  function paint(g, path, col, o = {}) {
    const W = g.canvas.width, H = g.canvas.height;
    g.save(); g.beginPath(); path(g); g.clip();
    const [bx, by, bw, bh] = o.box || [0, 0, W, H];
    g.globalAlpha = o.ba ?? 1;
    if (o.grad) { const gr = g.createLinearGradient(0, by, 0, by + bh); o.grad.forEach((c, i) => gr.addColorStop(i / (o.grad.length - 1), rgb(c))); g.fillStyle = gr; }
    else g.fillStyle = rgb(col);
    g.fillRect(bx, by, bw, bh);
    g.globalAlpha = 1;
    const L = o.len || 30, Wd = o.w || 8;
    const n = o.n ?? Math.min(2200, (bw * bh) / L / Wd * 0.9);
    const cols = o.cols || [col];
    for (let i = 0; i < n; i++) {
      const x = bx + R() * bw, y = by + R() * bh;
      const c = (o.grad && !o.cols) ? gradAt(o.grad, (y - by) / bh) : pick(cols);
      stroke(g, x, y, rnd(0.6, 1.4) * L, rnd(0.6, 1.3) * Wd, (o.ang || 0) + rnd(-1, 1) * (o.aj ?? 0.3), jc(c, o.j ?? 14), o.a ?? 0.35);
    }
    if (o.shade) { const gr = g.createLinearGradient(0, by, 0, by + bh); gr.addColorStop(0, `rgba(0,0,0,${o.shade[0]})`); gr.addColorStop(1, `rgba(0,0,0,${o.shade[1]})`); g.fillStyle = gr; g.fillRect(bx, by, bw, bh); }
    if (o.light) { const [lx, ly, lr, lc, la] = o.light; const gr = g.createRadialGradient(lx, ly, 0, lx, ly, lr); gr.addColorStop(0, rgb(lc, la)); gr.addColorStop(1, rgb(lc, 0)); g.fillStyle = gr; g.fillRect(bx, by, bw, bh); }
    g.restore();
    if (o.edge) { g.save(); g.beginPath(); path(g); g.strokeStyle = o.edge; g.lineWidth = o.ew || 2; g.globalAlpha = 0.55; g.stroke(); g.restore(); }
  }
  function paintPoly(g, pts, col, o = {}) { paint(g, poly(pts), col, Object.assign({ box: bbox(pts) }, o)); }

  function glow(g, x, y, r, col, a) { const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, rgb(col, a)); gr.addColorStop(1, rgb(col, 0)); g.fillStyle = gr; g.fillRect(x - r, y - r, r * 2, r * 2); }
  function sky(g, W, H, stops, h) { paint(g, rectP(0, 0, W, h || H), stops[0], { box: [0, 0, W, h || H], grad: stops, len: 90, w: 16, aj: 0.06, a: 0.22 }); }
  function clouds(g, n, box, cols, a = 0.22) {
    for (let k = 0; k < n; k++) {
      const cx = box[0] + R() * box[2], cy = box[1] + R() * box[3], sz = rnd(40, 140);
      for (let i = 0; i < 26; i++) stroke(g, cx + rnd(-sz, sz), cy + rnd(-sz * 0.25, sz * 0.25), rnd(50, 130), rnd(10, 26), rnd(-0.12, 0.12), jc(pick(cols), 10), a * rnd(0.5, 1));
    }
  }
  function fog(g, y, h, col, a, n = 70, W = 1280) { for (let i = 0; i < n; i++) stroke(g, rnd(-100, W + 100), y + rnd(0, h), rnd(160, 360), rnd(18, 46), rnd(-0.04, 0.04), jc(col, 8), a * rnd(0.5, 1)); }
  function moon(g, x, y, r, col, halo) {
    glow(g, x, y, r * 3.2, halo || col, 0.35);
    paint(g, ellP(x, y, r, r), col, { box: [x - r, y - r, r * 2, r * 2], len: 14, w: 6, aj: 3, a: 0.3, cols: [col, mix(col, '#806050', 0.3), mix(col, '#ffffff', 0.2)] });
    g.save(); g.globalAlpha = 0.15; g.fillStyle = '#5a3a30'; g.beginPath(); g.arc(x - r * 0.3, y - r * 0.2, r * 0.25, 0, TAU); g.arc(x + r * 0.25, y + r * 0.3, r * 0.18, 0, TAU); g.fill(); g.restore();
  }
  function stars(g, n, box, a = 0.7) { for (let i = 0; i < n; i++) { g.fillStyle = `rgba(255,240,220,${rnd(0.2, a)})`; g.fillRect(box[0] + R() * box[2], box[1] + R() * box[3], rnd(1, 2.2), rnd(1, 2.2)); } }
  function raven(g, x, y, s, flap, col = '#0b0809') {
    g.save(); g.translate(x, y); g.scale(s, s); g.fillStyle = col;
    const f = Math.sin(flap) * 8;
    g.beginPath(); g.moveTo(-22, -4 - f); g.quadraticCurveTo(-10, -6 - f * 0.6, -2, 0); g.quadraticCurveTo(0, -3, 2, 0); g.quadraticCurveTo(10, -6 - f * 0.6, 22, -4 - f); g.quadraticCurveTo(10, 2, 3, 4); g.lineTo(0, 7); g.lineTo(-3, 4); g.quadraticCurveTo(-10, 2, -22, -4 - f); g.fill();
    g.restore();
  }
  function ravens(g, n, box) { for (let i = 0; i < n; i++) raven(g, box[0] + R() * box[2], box[1] + R() * box[3], rnd(0.5, 1.2), rnd(0, 6)); }
  function window_(g, x, y, w, h, lit, warm = '#f0b04a') {
    g.save();
    g.beginPath(); g.moveTo(x, y + h); g.lineTo(x, y + w * 0.5); g.quadraticCurveTo(x + w / 2, y - w * 0.4, x + w, y + w * 0.5); g.lineTo(x + w, y + h); g.closePath();
    if (lit) { g.fillStyle = rgb(warm); g.fill(); g.globalCompositeOperation = 'lighter'; glow(g, x + w / 2, y + h / 2, Math.max(w, h) * 1.8, warm, 0.25); }
    else { g.fillStyle = 'rgba(12,8,10,0.85)'; g.fill(); }
    g.restore();
  }
  function vignette(g, W, H, a = 0.75, col = '#000') { const gr = g.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.95); gr.addColorStop(0, rgb(col, 0)); gr.addColorStop(1, rgb(col, a)); g.fillStyle = gr; g.fillRect(0, 0, W, H); }
  let grainPat = null;
  function grain(g, W, H, a = 0.07) {
    if (!grainPat) { const c = cv(160, 160), x = c.getContext('2d'); const d = x.createImageData(160, 160); for (let i = 0; i < d.data.length; i += 4) { const v = Math.random() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); grainPat = c; }
    g.save(); g.globalAlpha = a; g.globalCompositeOperation = 'overlay'; g.fillStyle = g.createPattern(grainPat, 'repeat'); g.fillRect(0, 0, W, H);
    g.globalCompositeOperation = 'source-over'; g.globalAlpha = 0.035; g.strokeStyle = '#fff'; g.lineWidth = 1;
    for (let i = -H; i < W; i += 5) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i + H, H); g.stroke(); }
    g.restore();
  }
  function finish(g, W, H, v = 0.75) { grain(g, W, H); vignette(g, W, H, v); }

  /* ---------- architektura ---------- */
  function house(g, x, base, w, h, o = {}) {
    const rh = o.roof ?? w * 0.8;
    paintPoly(g, [[x, base], [x, base - h], [x + w / 2, base - h - rh], [x + w, base - h], [x + w, base]], o.col || '#3a2e32', { len: 12, w: 5, ang: Math.PI / 2, aj: 0.25, a: 0.3, shade: o.shade || [0.1, 0.45] });
    paintPoly(g, [[x - 3, base - h + 3], [x + w / 2, base - h - rh - 2], [x + w + 3, base - h + 3], [x + w / 2, base - h - rh + 8]], o.roofCol || '#24191a', { len: 12, w: 4, ang: 0.9, a: 0.35 });
    const rows = Math.max(1, Math.floor(h / 34)), cols = Math.max(1, Math.floor(w / 26));
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const ww = Math.min(10, w / cols * 0.4), wx = x + (c + 0.5) * w / cols - ww / 2, wy = base - h + 12 + r * 34;
      if (wy + 16 < base - 6) window_(g, wx, wy, ww, 16, R() < (o.lit ?? 0.25), o.warm);
    }
    if (o.door) paintPoly(g, [[x + w / 2 - 7, base], [x + w / 2 - 7, base - 18], [x + w / 2, base - 24], [x + w / 2 + 7, base - 18], [x + w / 2 + 7, base]], '#120c0c', { a: 0.2 });
  }
  function crenels(g, x, y, w, col, step = 12) { g.fillStyle = rgb(col); for (let i = x; i < x + w - 4; i += step) g.fillRect(i, y - 7, step * 0.55, 8); }
  function tower(g, x, base, w, h, o = {}) {
    const col = o.col || '#3b3135';
    paintPoly(g, [[x, base], [x, base - h], [x + w, base - h], [x + w, base]], col, { len: 10, w: 5, ang: Math.PI / 2, aj: 0.2, a: 0.3, shade: [0, 0.4] });
    if (o.spire !== false) {
      const sh = o.spire || w * 1.5;
      paintPoly(g, [[x - 4, base - h], [x + w / 2, base - h - sh], [x + w + 4, base - h]], o.roofCol || '#22181a', { len: 10, w: 4, ang: 1.2, a: 0.35 });
      if (o.pin) { [[x - 2, 0.38], [x + w + 2, 0.38]].forEach(([px, k]) => paintPoly(g, [[px - 4, base - h], [px, base - h - sh * k], [px + 4, base - h]], o.roofCol || '#22181a', { a: 0.3 })); }
    } else crenels(g, x - 2, base - h, w + 4, col);
    for (let i = 0; i < (o.slits ?? 2); i++) window_(g, x + w / 2 - 3, base - h + 18 + i * 40, 6, 16, R() < (o.lit ?? 0.3));
  }
  function wawelCastle(g, cx, base, k, col, lit = 0.3, roofCol) {
    // mury z basztami, katedra z wieżami, pałac
    const c2 = col, r2 = roofCol || mix(col, '#000', 0.25);
    paintPoly(g, [[cx - 300 * k, base], [cx - 300 * k, base - 40 * k], [cx + 320 * k, base - 40 * k], [cx + 320 * k, base]], c2, { len: 12, w: 5, a: 0.3, shade: [0, 0.4] });
    crenels(g, cx - 300 * k, base - 40 * k, 620 * k, c2, 12 * k);
    tower(g, cx - 300 * k, base, 34 * k, 95 * k, { col: c2, roofCol: r2, spire: 52 * k, lit });
    tower(g, cx - 140 * k, base, 30 * k, 80 * k, { col: c2, roofCol: r2, spire: false, lit });
    tower(g, cx + 286 * k, base, 36 * k, 110 * k, { col: c2, roofCol: r2, spire: 60 * k, lit });
    // katedra
    paintPoly(g, [[cx - 70 * k, base - 30 * k], [cx - 70 * k, base - 110 * k], [cx + 90 * k, base - 110 * k], [cx + 90 * k, base - 30 * k]], c2, { len: 10, w: 5, a: 0.3, shade: [0, 0.35] });
    paintPoly(g, [[cx - 76 * k, base - 108 * k], [cx + 10 * k, base - 168 * k], [cx + 96 * k, base - 108 * k]], r2, { a: 0.35, ang: 0.6 });
    tower(g, cx - 104 * k, base - 30 * k, 34 * k, 150 * k, { col: c2, roofCol: r2, spire: 80 * k, pin: true, lit });
    tower(g, cx + 92 * k, base - 30 * k, 30 * k, 120 * k, { col: c2, roofCol: r2, spire: 64 * k, lit });
    for (let i = 0; i < 4; i++) window_(g, cx - 50 * k + i * 36 * k, base - 96 * k, 12 * k, 38 * k, R() < lit, '#e0a050');
    // pałac
    paintPoly(g, [[cx + 140 * k, base - 30 * k], [cx + 140 * k, base - 100 * k], [cx + 270 * k, base - 100 * k], [cx + 270 * k, base - 30 * k]], c2, { len: 10, w: 5, a: 0.3, shade: [0, 0.35] });
    paintPoly(g, [[cx + 134 * k, base - 98 * k], [cx + 205 * k, base - 140 * k], [cx + 276 * k, base - 98 * k]], r2, { a: 0.35 });
    for (let r = 0; r < 2; r++) for (let i = 0; i < 4; i++) window_(g, cx + 152 * k + i * 30 * k, base - 88 * k + r * 30 * k, 9 * k, 16 * k, R() < lit);
  }
  function mariacki(g, x, base, k, col, roofCol, lit = 0.4, crownCol = '#c9a24a') {
    // korpus kościoła
    paintPoly(g, [[x - 40 * k, base], [x - 40 * k, base - 170 * k], [x + 330 * k, base - 170 * k], [x + 330 * k, base]], col, { len: 12, w: 6, ang: Math.PI / 2, a: 0.3, shade: [0.05, 0.5] });
    paintPoly(g, [[x - 44 * k, base - 168 * k], [x + 145 * k, base - 290 * k], [x + 334 * k, base - 168 * k]], roofCol, { a: 0.35, ang: 0.5 });
    for (let i = 0; i < 4; i++) window_(g, x + 150 * k + i * 44 * k, base - 150 * k, 16 * k, 90 * k, R() < lit, '#d0603a');
    // wyższa wieża — hejnalica
    const tw = 74 * k, th = 430 * k;
    paintPoly(g, [[x, base], [x, base - th], [x + tw, base - th], [x + tw, base]], col, { len: 10, w: 5, ang: Math.PI / 2, aj: 0.2, a: 0.3, shade: [0, 0.45] });
    for (let i = 0; i < 4; i++) window_(g, x + tw / 2 - 8 * k, base - th + 40 * k + i * 80 * k, 16 * k, 40 * k, i === 0 ? true : R() < lit * 0.4);
    // hełm z koroną i wieżyczkami
    const sh = 200 * k;
    paintPoly(g, [[x - 2 * k, base - th], [x + tw / 2, base - th - sh], [x + tw + 2 * k, base - th]], roofCol, { a: 0.35, ang: 1.3 });
    [-8, 8, 24, 50, 66, 82].forEach((ox, i) => { const px = x + ox * k; const ph = (i % 2 ? 46 : 62) * k; paintPoly(g, [[px - 5 * k, base - th + 4], [px, base - th - ph], [px + 5 * k, base - th + 4]], roofCol, { a: 0.3 }); });
    g.save(); g.strokeStyle = rgb(crownCol); g.lineWidth = 4 * k; g.beginPath(); g.moveTo(x + tw * 0.32, base - th - sh * 0.62); g.lineTo(x + tw * 0.68, base - th - sh * 0.62); g.stroke();
    for (let i = 0; i < 5; i++) { g.beginPath(); g.moveTo(x + tw * (0.32 + i * 0.09), base - th - sh * 0.62); g.lineTo(x + tw * (0.32 + i * 0.09), base - th - sh * 0.62 - 9 * k); g.stroke(); }
    g.restore();
    // niższa wieża — dzwonnica
    const bx = x + 250 * k, bw = 66 * k, bh = 340 * k;
    paintPoly(g, [[bx, base], [bx, base - bh], [bx + bw, base - bh], [bx + bw, base]], col, { len: 10, w: 5, ang: Math.PI / 2, aj: 0.2, a: 0.3, shade: [0, 0.45] });
    for (let i = 0; i < 3; i++) window_(g, bx + bw / 2 - 7 * k, base - bh + 30 * k + i * 80 * k, 14 * k, 36 * k, R() < lit * 0.3);
    g.save(); g.beginPath(); g.moveTo(bx - 3 * k, base - bh); g.quadraticCurveTo(bx + bw / 2, base - bh - 90 * k, bx + bw + 3 * k, base - bh); g.closePath(); g.restore();
    paint(g, gg => { gg.moveTo(bx - 3 * k, base - bh); gg.quadraticCurveTo(bx + bw / 2, base - bh - 80 * k, bx + bw + 3 * k, base - bh); gg.closePath(); }, roofCol, { box: [bx - 6, base - bh - 90 * k, bw + 12, 92 * k], a: 0.35 });
    paintPoly(g, [[bx + bw / 2 - 4 * k, base - bh - 50 * k], [bx + bw / 2, base - bh - 110 * k], [bx + bw / 2 + 4 * k, base - bh - 50 * k]], roofCol, { a: 0.3 });
  }
  function sukiennice(g, x, base, w, k, col, roofCol, lit = 0.3) {
    const h = 110 * k;
    paintPoly(g, [[x, base], [x, base - h], [x + w, base - h], [x + w, base]], col, { len: 12, w: 5, ang: Math.PI / 2, aj: 0.2, a: 0.3, shade: [0, 0.5] });
    paintPoly(g, [[x - 6, base - h + 2], [x + 20 * k, base - h - 70 * k], [x + w - 20 * k, base - h - 70 * k], [x + w + 6, base - h + 2]], roofCol, { a: 0.35, ang: 0.2 });
    const n = Math.floor(w / (46 * k));
    for (let i = 0; i < n; i++) { const ax = x + 12 * k + i * (w - 24 * k) / n; g.save(); g.fillStyle = 'rgba(10,6,8,.85)'; g.beginPath(); g.moveTo(ax, base); g.lineTo(ax, base - 40 * k); g.quadraticCurveTo(ax + 15 * k, base - 64 * k, ax + 30 * k, base - 40 * k); g.lineTo(ax + 30 * k, base); g.fill(); if (R() < lit) { g.globalCompositeOperation = 'lighter'; glow(g, ax + 15 * k, base - 22 * k, 40 * k, '#e09a40', 0.35); } g.restore(); }
    for (let i = 0; i < n; i++) window_(g, x + 22 * k + i * (w - 24 * k) / n, base - h + 16 * k, 10 * k, 22 * k, R() < lit * 0.6);
    tower(g, x - 8 * k, base - h + 10, 20 * k, 26 * k, { col, roofCol, spire: 40 * k, slits: 0 });
    tower(g, x + w - 12 * k, base - h + 10, 20 * k, 26 * k, { col, roofCol, spire: 40 * k, slits: 0 });
  }
  function krakowSkyline(g, base, col, lit = 0.25, k = 1) {
    paintPoly(g, [[0, base + 40], [40, base - 30 * k], [140, base - 70 * k], [420, base - 74 * k], [520, base - 20 * k], [580, base + 40]], mix(col, '#000', 0.1), { a: 0.3 });
    wawelCastle(g, 280, base - 66 * k, 0.55 * k, col, lit);
    for (let i = 0; i < 14; i++) house(g, 560 + i * 52, base + 6, 44 + R() * 14, 50 + R() * 60, { col, roofCol: mix(col, '#000', 0.2), lit, roof: 40 });
    mariacki(g, 820, base, 0.42 * k, col, mix(col, '#000', 0.2), lit);
    sukiennice(g, 620, base, 170, 0.5, col, mix(col, '#000', 0.2), lit * 0.5);
  }
  function torch(g, x, y, s = 1) {
    g.fillStyle = '#2a1a10'; g.fillRect(x - 3 * s, y, 6 * s, 26 * s);
    g.save(); g.globalCompositeOperation = 'lighter'; glow(g, x, y - 4 * s, 90 * s, '#ff9a3a', 0.4); glow(g, x, y - 6 * s, 20 * s, '#ffe08a', 0.8); g.restore();
  }

  /* =================== TŁA =================== */
  const BG = {};
  BG.title = (g, W, H) => {
    sky(g, W, H, ['#0d0507', '#2a080c', '#6a1612', '#b4482a', '#d77a3a']);
    moon(g, 900, 210, 92, '#e9c8a0', '#b3302a');
    clouds(g, 36, [0, 40, W, 330], ['#14070a', '#3a0e12', '#5a1c18'], 0.24);
    stars(g, 60, [0, 0, W, 200], 0.5);
    krakowSkyline(g, 600, '#170a0d', 0.22);
    fog(g, 560, 120, '#d0806a', 0.07, 80);
    paintPoly(g, [[0, H], [0, 600], [130, 560], [300, 575], [470, 630], [560, H]], '#0a0607', { cols: ['#0a0607', '#1b1012', '#261818'], len: 22, w: 8, ang: -0.2, a: 0.4 });
    ravens(g, 16, [460, 80, 760, 300]);
    finish(g, W, H, 0.8);
  };
  BG.map = (g, W, H) => {
    paint(g, rectP(0, 0, W, H), '#b89a6a', { cols: ['#c4a876', '#a98a5c', '#cbb183', '#9c7f55'], len: 46, w: 18, aj: 3, a: 0.22 });
    for (let i = 0; i < 16; i++) glow(g, rnd(0, W), rnd(0, H), rnd(40, 140), '#6a4a28', 0.12);
    // Błonia i lasy
    paint(g, ellP(250, 300, 210, 160), '#7a7a48', { box: [40, 140, 420, 320], ba: 0.45, cols: ['#7a7a48', '#6a7040', '#8a8650'], len: 26, w: 10, a: 0.25 });
    [[90, 120], [1150, 160], [1180, 380], [120, 520], [980, 120], [60, 300]].forEach(([fx, fy]) => { for (let i = 0; i < 40; i++) { const tx = fx + rnd(-80, 80), ty = fy + rnd(-50, 50); g.fillStyle = jc('#3f4a28', 16); g.beginPath(); g.arc(tx, ty, rnd(6, 11), 0, TAU); g.fill(); g.fillStyle = 'rgba(30,20,10,.5)'; g.fillRect(tx - 1, ty + 6, 2, 5); } });
    // Wisła
    const river = [[0, 575], [140, 600], [300, 655], [430, 668], [560, 640], [650, 640], [760, 668], [900, 700], [1060, 665], [1180, 620], [1280, 600]];
    const old = [[640, 640], [690, 575], [800, 520], [930, 525], [1030, 590], [1080, 655]];
    function riverDraw(pts, w) { for (let i = 0; i < pts.length - 1; i++) { const [x1, y1] = pts[i], [x2, y2] = pts[i + 1]; const steps = 18; for (let s = 0; s < steps; s++) { const t = s / steps; stroke(g, x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, w * 1.6, w, Math.atan2(y2 - y1, x2 - x1), jc(pick(['#4f6a74', '#5d7880', '#405a64']), 10), 0.45); } } }
    riverDraw(river, 34); riverDraw(old, 18);
    // drogi
    g.save(); g.strokeStyle = 'rgba(90,60,30,.55)'; g.lineWidth = 4; g.setLineDash([10, 6]);
    [[[650, 300], [600, 470], [570, 520]], [[650, 300], [800, 560]], [[650, 300], [380, 300], [250, 300]], [[650, 300], [700, 60]], [[650, 300], [1000, 250], [1280, 260]]].forEach(p => { g.beginPath(); g.moveTo(p[0][0], p[0][1]); p.slice(1).forEach(q => g.lineTo(q[0], q[1])); g.stroke(); });
    g.restore();
    // mury miejskie
    g.save(); g.strokeStyle = '#5b4632'; g.lineWidth = 9; g.beginPath(); g.ellipse(650, 290, 215, 170, 0, 0, TAU); g.stroke();
    g.strokeStyle = 'rgba(40,28,18,.6)'; g.lineWidth = 2; g.stroke();
    for (let a = 0; a < TAU; a += TAU / 22) { const tx = 650 + Math.cos(a) * 215, ty = 290 + Math.sin(a) * 170; g.fillStyle = '#4a3828'; g.beginPath(); g.arc(tx, ty, 8, 0, TAU); g.fill(); g.fillStyle = '#7a3a26'; g.beginPath(); g.moveTo(tx - 8, ty - 2); g.lineTo(tx, ty - 14); g.lineTo(tx + 8, ty - 2); g.fill(); }
    g.restore();
    // zabudowa wewnątrz murów
    for (let i = 0; i < 160; i++) { const a = R() * TAU, r = Math.sqrt(R()); const bx = 650 + Math.cos(a) * 195 * r, by = 290 + Math.sin(a) * 152 * r; if (Math.abs(bx - 650) < 46 && Math.abs(by - 300) < 40) continue; g.fillStyle = jc('#7a3c28', 18); g.beginPath(); g.moveTo(bx - 7, by); g.lineTo(bx, by - 9); g.lineTo(bx + 7, by); g.fill(); g.fillStyle = jc('#9a8060', 10); g.fillRect(bx - 6, by, 12, 7); }
    // Rynek — plac
    paint(g, rectP(606, 262, 88, 78), '#cdb68c', { box: [606, 262, 88, 78], len: 10, w: 4, a: 0.3 });
    // Kazimierz
    g.save(); g.strokeStyle = '#5b4632'; g.lineWidth = 6; g.beginPath(); g.ellipse(830, 600, 95, 55, 0.1, 0, TAU); g.stroke(); g.restore();
    for (let i = 0; i < 50; i++) { const a = R() * TAU, r = Math.sqrt(R()); const bx = 830 + Math.cos(a) * 85 * r, by = 600 + Math.sin(a) * 45 * r; g.fillStyle = jc('#7a3c28', 18); g.beginPath(); g.moveTo(bx - 6, by); g.lineTo(bx, by - 8); g.lineTo(bx + 6, by); g.fill(); g.fillStyle = jc('#9a8060', 10); g.fillRect(bx - 5, by, 10, 6); }
    // Wzgórze wawelskie
    paint(g, ellP(560, 545, 85, 55), '#6d6a40', { box: [470, 485, 180, 120], cols: ['#6d6a40', '#5a5a34', '#7a7448'], len: 14, w: 6, a: 0.35, edge: '#3a3020' });
    wawelCastle(g, 556, 548, 0.2, '#6a5040', 0, '#7a3020');
    // kartusz
    g.save(); g.translate(860, 0); g.fillStyle = 'rgba(200,170,120,.85)'; g.fillRect(40, 100, 360, 92); g.strokeStyle = '#5a3a20'; g.lineWidth = 3; g.strokeRect(40, 100, 360, 92); g.strokeRect(48, 108, 344, 76);
    g.fillStyle = '#3a2210'; g.font = 'bold 40px Georgia, serif'; g.textAlign = 'center'; g.fillText('CRACOVIA', 220, 152); g.font = 'italic 18px Georgia, serif'; g.fillText('Anno Domini MCCCCIX', 220, 176); g.restore();
    // róża wiatrów
    g.save(); g.translate(1170, 520); g.strokeStyle = '#4a3018'; g.fillStyle = '#4a3018'; g.lineWidth = 2; g.beginPath(); g.arc(0, 0, 46, 0, TAU); g.stroke();
    for (let i = 0; i < 4; i++) { g.rotate(Math.PI / 2); g.beginPath(); g.moveTo(0, -58); g.lineTo(8, 0); g.lineTo(-8, 0); g.closePath(); g.fill(); }
    g.font = 'bold 18px Georgia'; g.textAlign = 'center'; g.fillText('N', 0, -64); g.restore();
    g.save(); g.fillStyle = 'rgba(40,40,60,.7)'; g.font = 'italic 22px Georgia'; g.fillText('Vistula', 230, 640); g.fillText('Vistula', 1180, 590); g.restore();
    g.save(); g.fillStyle = 'rgba(60,40,20,.55)'; g.font = 'italic 16px Georgia'; g.fillText('Błonia', 205, 255); g.restore();
    grain(g, W, H, 0.09); vignette(g, W, H, 0.85, '#2a1608');
  };
  BG.wawel = (g, W, H) => {
    sky(g, W, H, ['#120e1c', '#2c1a33', '#5d2a37', '#a2452f', '#d07a3c'], 470);
    clouds(g, 30, [0, 30, W, 330], ['#1c1224', '#40202c', '#6a2c2a'], 0.25);
    glow(g, 1000, 460, 260, '#ff8a3a', 0.25);
    paintPoly(g, [[0, 470], [200, 420], [420, 450], [700, 410], [1000, 440], [1280, 400], [1280, 520], [0, 520]], '#2a1c24', { a: 0.3, shade: [0, 0.3] });
    paintPoly(g, [[120, 720], [210, 470], [300, 430], [930, 430], [1030, 480], [1110, 720]], '#2a2a1c', { cols: ['#2a2a1c', '#3a3424', '#1e2016', '#4a3a2a'], len: 20, w: 8, ang: -0.6, aj: 0.6, a: 0.4, shade: [0, 0.55] });
    wawelCastle(g, 620, 440, 1.05, '#4a3a3c', 0.35, '#2a1a1c');
    // Smocza Jama
    g.save(); g.fillStyle = '#060405'; g.beginPath(); g.moveTo(230, 690); g.quadraticCurveTo(270, 600, 330, 690); g.fill(); glow(g, 280, 670, 60, '#4aa070', 0.18); g.restore();
    paintPoly(g, [[0, 650], [W, 640], [W, H], [0, H]], '#1a2028', { cols: ['#1a2028', '#28303a', '#3a2c2a'], len: 70, w: 8, aj: 0.05, a: 0.4 });
    for (let i = 0; i < 70; i++) stroke(g, rnd(700, 1280), rnd(655, 715), rnd(30, 90), 3, 0, jc('#e08a40', 20), 0.25);
    fog(g, 600, 90, '#c9a0a0', 0.07, 60);
    ravens(g, 10, [300, 120, 700, 220]);
    finish(g, W, H);
  };
  BG.rynek = (g, W, H) => {
    sky(g, W, H, ['#05060c', '#0e1220', '#1c1a2a', '#3a2430'], 480);
    stars(g, 120, [0, 0, W, 300]);
    moon(g, 210, 120, 46, '#d8d0c0', '#6a7090');
    clouds(g, 20, [0, 40, W, 260], ['#0c0e18', '#1a1a28', '#2a2030'], 0.25);
    for (let i = 0; i < 6; i++) house(g, i * 58 - 20, 480, 54, 120 + R() * 50, { col: '#2e2428', roofCol: '#1a1214', lit: 0.3, roof: 44 });
    for (let i = 0; i < 6; i++) house(g, 1060 + i * 52, 480, 50, 110 + R() * 60, { col: '#2e2428', roofCol: '#1a1214', lit: 0.3, roof: 44 });
    mariacki(g, 820, 480, 0.62, '#3a2422', '#1c1012', 0.35);
    sukiennice(g, 270, 480, 470, 1, '#4a3632', '#24181a', 0.4);
    // bruk z perspektywą
    paintPoly(g, [[0, 480], [W, 480], [W, H], [0, H]], '#2a2426', { cols: ['#2a2426', '#3a3234', '#1e1a1c', '#4a3a36'], len: 18, w: 7, aj: 0.2, a: 0.4, shade: [0.3, 0] });
    g.save(); g.strokeStyle = 'rgba(0,0,0,.25)'; g.lineWidth = 1.5; for (let i = 0; i < 18; i++) { const y = 485 + Math.pow(i / 18, 1.6) * 235; g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); } g.restore();
    torch(g, 250, 420); torch(g, 770, 420); torch(g, 1080, 430);
    g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 250, 560, 160, '#ff8a3a', 0.12); glow(g, 770, 560, 160, '#ff8a3a', 0.12); g.restore();
    // studnia i kram
    paintPoly(g, [[560, 560], [560, 520], [620, 520], [620, 560]], '#3a3034', { a: 0.3 });
    fog(g, 470, 140, '#9aa0b8', 0.06, 70);
    ravens(g, 9, [800, 60, 280, 200]);
    finish(g, W, H);
  };
  BG.mariacki = (g, W, H) => {
    sky(g, W, H, ['#03060a', '#0a1420', '#16202c', '#2a2430']);
    moon(g, 1080, 150, 60, '#c8d4dc', '#405870');
    clouds(g, 34, [0, 20, W, 400], ['#0a1018', '#1a2430', '#26303c'], 0.28);
    for (let i = 0; i < 4; i++) house(g, i * 62 - 10, 720, 60, 220 + R() * 80, { col: '#241c20', roofCol: '#140e10', lit: 0.25, roof: 50 });
    for (let i = 0; i < 4; i++) house(g, 1040 + i * 64, 720, 62, 200 + R() * 80, { col: '#241c20', roofCol: '#140e10', lit: 0.25, roof: 50 });
    mariacki(g, 330, 760, 1.05, '#3e2622', '#1a0e10', 0.35);
    g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 369, 760 - 452 * 1.05 + 40, 80, '#ffb050', 0.35); g.restore();
    for (let i = 0; i < 26; i++) raven(g, 300 + rnd(-140, 180) + (i % 2) * 60, rnd(40, 330), rnd(0.6, 1.3), rnd(0, 6));
    fog(g, 560, 160, '#8090a8', 0.07, 80);
    finish(g, W, H, 0.8);
  };
  BG.akademia = (g, W, H) => {
    paint(g, rectP(0, 0, W, H), '#2a1e1a', { cols: ['#2a1e1a', '#3a2a22', '#1e1612', '#4a3428'], len: 26, w: 10, aj: 1.5, a: 0.3, shade: [0.35, 0.2] });
    // sklepienie
    g.save(); g.strokeStyle = 'rgba(80,60,48,.8)'; g.lineWidth = 10; for (let i = 0; i < 5; i++) { g.beginPath(); g.moveTo(i * 320, 0); g.quadraticCurveTo(i * 320 + 160, 180, i * 320 + 320, 0); g.stroke(); } g.restore();
    // okno gotyckie z księżycem
    const wx = 520, wy = 90, ww = 240, wh = 330;
    g.save(); g.beginPath(); g.moveTo(wx, wy + wh); g.lineTo(wx, wy + 110); g.quadraticCurveTo(wx + ww / 2, wy - 80, wx + ww, wy + 110); g.lineTo(wx + ww, wy + wh); g.closePath(); g.clip();
    sky(g, W, H, ['#0c1a2c', '#1c2c44', '#2a3a50'], 500); moon(g, wx + 150, wy + 120, 34, '#dfe6ee', '#6a88aa'); stars(g, 40, [wx, wy, ww, wh]); g.restore();
    g.save(); g.strokeStyle = '#1a1210'; g.lineWidth = 10; g.beginPath(); g.moveTo(wx, wy + wh); g.lineTo(wx, wy + 110); g.quadraticCurveTo(wx + ww / 2, wy - 80, wx + ww, wy + 110); g.lineTo(wx + ww, wy + wh); g.stroke();
    g.lineWidth = 6; g.beginPath(); g.moveTo(wx + ww / 2, wy + 20); g.lineTo(wx + ww / 2, wy + wh); g.moveTo(wx, wy + 200); g.lineTo(wx + ww, wy + 200); g.stroke(); g.restore();
    g.save(); g.globalCompositeOperation = 'lighter'; glow(g, wx + ww / 2, wy + wh + 120, 300, '#4a6a9a', 0.12); g.restore();
    // regały
    function shelf(x, w) {
      paintPoly(g, [[x, 120], [x + w, 120], [x + w, 600], [x, 600]], '#24160f', { a: 0.3, shade: [0, 0.3] });
      for (let r = 0; r < 6; r++) { const y = 150 + r * 76; g.fillStyle = '#140c08'; g.fillRect(x, y + 60, w, 10); let bx = x + 8; while (bx < x + w - 14) { const bw = rnd(10, 22), bh = rnd(38, 58); g.fillStyle = jc(pick(['#5a1a14', '#2a3a24', '#4a3020', '#6a5030', '#1e2a3a', '#3a1a2a']), 14); g.fillRect(bx, y + 60 - bh, bw - 2, bh); g.fillStyle = 'rgba(200,160,80,.35)'; g.fillRect(bx + 2, y + 66 - bh, bw - 6, 3); bx += bw; } }
    }
    shelf(30, 380); shelf(870, 380);
    // posadzka szachownica
    for (let r = 0; r < 6; r++) for (let c = -6; c < 20; c++) { const y0 = 600 + Math.pow(r / 6, 1.4) * 120, y1 = 600 + Math.pow((r + 1) / 6, 1.4) * 120; const sx = (y) => 640 + (c * 80 - 640) * (0.7 + (y - 600) / 400); g.fillStyle = (r + c) % 2 ? '#3a2a20' : '#5a4430'; g.beginPath(); g.moveTo(sx(y0), y0); g.lineTo(sx(y0) + 80 * (0.7 + (y0 - 600) / 400), y0); g.lineTo(sx(y1) + 80 * (0.7 + (y1 - 600) / 400), y1); g.lineTo(sx(y1), y1); g.fill(); }
    // pulpit z księgą
    paintPoly(g, [[600, 600], [615, 470], [665, 470], [680, 600]], '#2a1a10', { a: 0.3 });
    paintPoly(g, [[560, 475], [720, 475], [700, 445], [580, 445]], '#e8dcc0', { a: 0.25, cols: ['#e8dcc0', '#d0c0a0'] });
    g.save(); g.strokeStyle = 'rgba(60,40,20,.5)'; g.lineWidth = 1; for (let i = 0; i < 6; i++) { g.beginPath(); g.moveTo(590, 452 + i * 4); g.lineTo(635, 452 + i * 4); g.moveTo(645, 452 + i * 4); g.lineTo(690, 452 + i * 4); g.stroke(); } g.restore();
    // świece
    [[430, 520], [850, 520], [560, 440], [720, 440]].forEach(([x, y]) => { g.fillStyle = '#e8dcc0'; g.fillRect(x - 4, y, 8, 30); g.save(); g.globalCompositeOperation = 'lighter'; glow(g, x, y - 6, 120, '#ffa040', 0.3); glow(g, x, y - 6, 12, '#fff0b0', 0.9); g.restore(); });
    finish(g, W, H, 0.85);
  };
  BG.turniej = (g, W, H) => {
    sky(g, W, H, ['#2a2a36', '#4a4652', '#6a6266', '#8a7a6e'], 400);
    clouds(g, 40, [0, 0, W, 360], ['#2a2a34', '#4a4650', '#5a5258', '#3a3640'], 0.3);
    paintPoly(g, [[0, 400], [300, 370], [640, 385], [1000, 365], [1280, 380], [1280, 420], [0, 420]], '#3a3a3c', { a: 0.3 });
    wawelCastle(g, 1020, 380, 0.3, '#3a3438', 0.2);
    paintPoly(g, [[0, 400], [W, 400], [W, H], [0, H]], '#3e4228', { cols: ['#3e4228', '#4a4a2c', '#2e3220', '#5a4a30'], len: 30, w: 8, aj: 0.15, a: 0.35, shade: [0, 0.35] });
    // trybuna
    paintPoly(g, [[120, 410], [120, 300], [620, 300], [620, 410]], '#3a2a20', { a: 0.3 });
    paintPoly(g, [[100, 300], [370, 240], [640, 300]], '#6a1a1a', { a: 0.35 });
    for (let i = 0; i < 9; i++) { g.fillStyle = i % 2 ? '#c9a24a' : '#7a1a1a'; g.beginPath(); g.moveTo(110 + i * 58, 300); g.lineTo(140 + i * 58, 300); g.lineTo(125 + i * 58, 318); g.fill(); }
    for (let i = 0; i < 110; i++) { const px = rnd(135, 605), py = rnd(330, 400); g.fillStyle = jc(pick(['#5a2a20', '#2a3a4a', '#6a5a30', '#3a2a3a', '#4a4a4a']), 20); g.beginPath(); g.ellipse(px, py, 7, 10, 0, 0, TAU); g.fill(); g.fillStyle = jc('#d0a080', 10); g.beginPath(); g.arc(px, py - 12, 5, 0, TAU); g.fill(); }
    // namioty
    function tent(x, y, s, c1, c2) { for (let i = 0; i < 6; i++) { g.fillStyle = i % 2 ? c1 : c2; g.beginPath(); g.moveTo(x, y - 90 * s); g.lineTo(x - 60 * s + i * 20 * s, y); g.lineTo(x - 40 * s + i * 20 * s, y); g.fill(); } g.strokeStyle = '#2a1a10'; g.lineWidth = 3; g.beginPath(); g.moveTo(x, y - 90 * s); g.lineTo(x, y - 130 * s); g.stroke(); g.fillStyle = c2; g.beginPath(); g.moveTo(x, y - 130 * s); g.lineTo(x + 30 * s, y - 122 * s); g.lineTo(x, y - 114 * s); g.fill(); }
    tent(760, 420, 1, '#c9a24a', '#7a1a1a'); tent(900, 410, 0.85, '#1a1a1a', '#5a2a6a'); tent(1180, 430, 1.1, '#e0d8c0', '#2a4a7a');
    // szranki
    paintPoly(g, [[60, 520], [1220, 520], [1220, 540], [60, 540]], '#5a3a20', { a: 0.3 });
    for (let x = 60; x <= 1220; x += 58) { g.fillStyle = '#3a2210'; g.fillRect(x - 4, 500, 8, 70); }
    g.fillStyle = '#6a4424'; g.fillRect(60, 500, 1160, 8);
    // błoto i ślady
    for (let i = 0; i < 120; i++) stroke(g, rnd(0, W), rnd(560, 720), rnd(20, 60), rnd(4, 10), rnd(-0.2, 0.2), jc('#2a2014', 10), 0.3);
    fog(g, 380, 80, '#a0a0a8', 0.05, 40);
    ravens(g, 6, [700, 40, 400, 160]);
    finish(g, W, H, 0.7);
  };
  BG.kazimierz = (g, W, H) => {
    paint(g, rectP(0, 0, W, H), '#1e1614', { cols: ['#1e1614', '#2a1e1a', '#14100e', '#3a2a22'], len: 30, w: 12, aj: 1.5, a: 0.3 });
    // belki
    for (let i = 0; i < 6; i++) paintPoly(g, [[i * 230 - 20, 0], [i * 230 + 20, 0], [i * 230 + 20, 70], [i * 230 - 20, 70]], '#140c08', { a: 0.3 });
    paintPoly(g, [[0, 60], [W, 60], [W, 90], [0, 90]], '#1a100a', { a: 0.3 });
    // drzwi na noc
    g.save(); g.beginPath(); g.rect(80, 200, 200, 360); g.clip(); sky(g, W, H, ['#0a1020', '#1a2438', '#2a3040'], 600); house(g, 90, 560, 90, 150, { col: '#1a1820', roofCol: '#0e0c10', lit: 0.8, roof: 50 }); house(g, 190, 560, 90, 190, { col: '#1a1820', roofCol: '#0e0c10', lit: 0.6, roof: 50 }); fog(g, 420, 140, '#8090a8', 0.1, 20); g.restore();
    g.strokeStyle = '#120a06'; g.lineWidth = 16; g.strokeRect(80, 200, 200, 360);
    // palenisko
    paintPoly(g, [[820, 600], [820, 330], [1200, 330], [1200, 600]], '#3a2a24', { cols: ['#3a2a24', '#4a3a30', '#2a1e1a'], a: 0.35, shade: [0, 0.3] });
    paintPoly(g, [[860, 330], [900, 60], [1120, 60], [1160, 330]], '#2a1e1a', { a: 0.35 });
    g.save(); g.fillStyle = '#120806'; g.beginPath(); g.moveTo(880, 600); g.lineTo(880, 460); g.quadraticCurveTo(1010, 380, 1140, 460); g.lineTo(1140, 600); g.fill();
    g.globalCompositeOperation = 'lighter'; for (let i = 0; i < 90; i++) stroke(g, rnd(900, 1120), rnd(510, 600), rnd(10, 30), rnd(6, 14), -Math.PI / 2 + rnd(-0.4, 0.4), jc(pick(['#ff6a1a', '#ffa03a', '#ffd070']), 20), 0.4);
    glow(g, 1010, 540, 420, '#ff6a20', 0.3); glow(g, 1010, 560, 120, '#ffd080', 0.5); g.restore();
    // kowadło
    paintPoly(g, [[520, 600], [540, 540], [500, 520], [470, 500], [700, 500], [720, 520], [660, 540], [680, 600]], '#22201e', { a: 0.3, light: [600, 500, 200, '#ff8a40', 0.25] });
    g.fillStyle = 'rgba(255,140,60,.5)'; g.fillRect(470, 498, 230, 3);
    // narzędzia na ścianie
    g.save(); g.strokeStyle = '#0c0806'; g.lineWidth = 6; [[380, 160], [430, 150], [480, 170], [540, 150]].forEach(([x, y]) => { g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 120); g.stroke(); g.fillStyle = '#0c0806'; g.fillRect(x - 14, y + 110, 28, 16); }); g.restore();
    // zbroja na stojaku
    drawKnight(g, 700, 470, 0.95, { stand: true, closed: true });
    // posadzka
    paintPoly(g, [[0, 600], [W, 600], [W, H], [0, H]], '#1a1210', { cols: ['#1a1210', '#2a1e18', '#120c0a'], len: 40, w: 10, aj: 0.1, a: 0.35, light: [1010, 600, 500, '#ff7a30', 0.18] });
    for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(255,${120 + rnd(0, 100) | 0},40,${rnd(0.3, 0.9)})`; g.fillRect(rnd(880, 1140), rnd(200, 460), 2, 2); }
    finish(g, W, H, 0.8);
  };
  BG.smocza = (g, W, H) => {
    paint(g, rectP(0, 0, W, H), '#0e1214', { cols: ['#0e1214', '#1a2024', '#0a0c0e', '#22282a'], len: 34, w: 14, aj: 2, a: 0.35 });
    g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 760, 380, 420, '#2aa070', 0.18); glow(g, 760, 400, 140, '#6af0b0', 0.12); g.restore();
    // głąb jaskini
    paint(g, ellP(760, 380, 260, 170), '#05080a', { box: [500, 210, 520, 340], a: 0.3, cols: ['#05080a', '#0a1814', '#0e2a20'] });
    // stalaktyty
    for (let i = 0; i < 22; i++) { const x = rnd(0, W), w = rnd(20, 60), h = rnd(60, 200); paintPoly(g, [[x - w / 2, 0], [x + w / 2, 0], [x + rnd(-6, 6), h]], '#161c1e', { a: 0.35, cols: ['#161c1e', '#22292c', '#0c1012'] }); }
    for (let i = 0; i < 14; i++) { const x = rnd(0, W), w = rnd(30, 80), h = rnd(40, 130); paintPoly(g, [[x - w / 2, 640], [x + w / 2, 640], [x + rnd(-6, 6), 640 - h]], '#141a1c', { a: 0.35 }); }
    // szkielet smoka (legenda!)
    g.save(); g.strokeStyle = 'rgba(190,190,170,.25)'; g.lineWidth = 6; g.beginPath(); g.moveTo(560, 470); g.quadraticCurveTo(760, 380, 980, 460); g.stroke();
    for (let i = 0; i < 9; i++) { const t = i / 8, x = 590 + t * 360, y = 455 - Math.sin(t * Math.PI) * 60; g.lineWidth = 4; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x - 30, y + 60, x - 6, y + 100); g.stroke(); }
    g.restore();
    // posadzka
    paintPoly(g, [[0, 600], [W, 590], [W, H], [0, H]], '#121618', { cols: ['#121618', '#1e2426', '#0a0c0e'], len: 50, w: 10, aj: 0.1, a: 0.35 });
    torch(g, 200, 300, 1.2); torch(g, 1080, 300, 1.2);
    // chorągiew Komtura
    g.fillStyle = '#2a1a10'; g.fillRect(380, 120, 5, 260); paintPoly(g, [[385, 130], [470, 130], [470, 290], [428, 260], [385, 290]], '#0c0a0c', { a: 0.3 });
    g.strokeStyle = 'rgba(160,150,150,.6)'; g.lineWidth = 7; g.beginPath(); g.moveTo(428, 155); g.lineTo(428, 240); g.moveTo(400, 185); g.lineTo(456, 185); g.stroke();
    fog(g, 540, 160, '#4a8a70', 0.06, 70);
    finish(g, W, H, 0.85);
  };
  BG.koniec = (g, W, H) => {
    sky(g, W, H, ['#2a3658', '#6a5a78', '#c88a6a', '#f2c27a', '#f8e0a0']);
    g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 640, 560, 520, '#ffd890', 0.45); g.restore();
    paint(g, ellP(640, 560, 80, 80), '#fff0c8', { box: [560, 480, 160, 160], a: 0.2 });
    clouds(g, 26, [0, 60, W, 300], ['#e8b090', '#c88a7a', '#f0d0a0'], 0.22);
    krakowSkyline(g, 620, '#4a3440', 0.5);
    fog(g, 560, 160, '#ffe0c0', 0.1, 80);
    for (let i = 0; i < 12; i++) raven(g, rnd(300, 1000), rnd(120, 360), rnd(0.4, 0.8), rnd(0, 6), '#f4ece0');
    finish(g, W, H, 0.5);
  };
  BG.bitwa = (g, W, H) => { BG.smocza(g, W, H); g.fillStyle = 'rgba(0,0,0,.35)'; g.fillRect(0, 0, W, H); };

  /* =================== POSTACIE =================== */
  function limb(g, pts, w, col, hl) { g.save(); g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = col; g.lineWidth = w; g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); pts.slice(1).forEach(p => g.lineTo(p[0], p[1])); g.stroke(); if (hl) { g.strokeStyle = hl; g.lineWidth = w * 0.25; g.globalAlpha = 0.6; g.beginPath(); g.moveTo(pts[0][0] - w * 0.2, pts[0][1]); pts.slice(1).forEach(p => g.lineTo(p[0] - w * 0.2, p[1])); g.stroke(); } g.restore(); }
  function lin(g, x0, y0, x1, y1, stops) { const gr = g.createLinearGradient(x0, y0, x1, y1); stops.forEach((c, i) => gr.addColorStop(i / (stops.length - 1), c)); return gr; }
  function sulimaArms(g, x, y, w, h) {
    // herb Sulima: górne pole złote z połową czarnego orła, dolne czerwone z trzema srebrnymi kamieniami
    g.save(); g.beginPath(); g.moveTo(x - w / 2, y - h / 2); g.lineTo(x + w / 2, y - h / 2); g.lineTo(x + w / 2, y + h * 0.15); g.quadraticCurveTo(x + w / 2, y + h * 0.45, x, y + h / 2); g.quadraticCurveTo(x - w / 2, y + h * 0.45, x - w / 2, y + h * 0.15); g.closePath(); g.clip();
    g.fillStyle = '#c9a032'; g.fillRect(x - w / 2, y - h / 2, w, h / 2); g.fillStyle = '#9a1a18'; g.fillRect(x - w / 2, y, w, h / 2);
    g.fillStyle = '#111'; const s = w / 40; g.beginPath();
    g.moveTo(x - 16 * s, y); g.lineTo(x - 18 * s, y - 10 * s); g.lineTo(x - 10 * s, y - 6 * s); g.lineTo(x - 8 * s, y - 14 * s); g.lineTo(x - 3 * s, y - 8 * s); g.lineTo(x, y - 17 * s); g.lineTo(x + 3 * s, y - 8 * s); g.lineTo(x + 8 * s, y - 14 * s); g.lineTo(x + 10 * s, y - 6 * s); g.lineTo(x + 18 * s, y - 10 * s); g.lineTo(x + 16 * s, y); g.closePath(); g.fill();
    g.fillStyle = '#d8d8d8'; [[-9, 9], [9, 9], [0, 19]].forEach(([dx, dy]) => { g.beginPath(); g.arc(x + dx * s, y + dy * s, 4.2 * s, 0, TAU); g.fill(); });
    g.restore();
    g.save(); g.strokeStyle = 'rgba(0,0,0,.6)'; g.lineWidth = Math.max(1, w / 30); g.beginPath(); g.moveTo(x - w / 2, y - h / 2); g.lineTo(x + w / 2, y - h / 2); g.lineTo(x + w / 2, y + h * 0.15); g.quadraticCurveTo(x + w / 2, y + h * 0.45, x, y + h / 2); g.quadraticCurveTo(x - w / 2, y + h * 0.45, x - w / 2, y + h * 0.15); g.closePath(); g.stroke(); g.restore();
  }
  function drawKnight(g, x, y, s, o = {}) {
    const A = o.armor || '#1c1e24', AH = o.hl || '#7a8290', cape = o.cape || '#3c0b0e';
    const armG = (x0, x1) => lin(g, x0, 0, x1, 0, [mix(A, '#000', 0.3).map ? rgb(mix(A, '#000', 0.3)) : A, rgb(mix(A, AH, 0.55)), rgb(A)]);
    g.save(); g.translate(x, y); g.scale(s, s);
    if (!o.stand) { g.fillStyle = 'rgba(0,0,0,.4)'; g.beginPath(); g.ellipse(0, 0, 44, 8, 0, 0, TAU); g.fill(); }
    if (o.stand) { g.fillStyle = '#1a100a'; g.fillRect(-3, -190, 6, 190); g.fillRect(-30, -6, 60, 6); }
    if (!o.stand) { g.fillStyle = lin(g, -40, 0, 40, 0, [rgb(mix(cape, '#000', 0.5)), rgb(cape), rgb(mix(cape, '#000', 0.4))]); g.beginPath(); g.moveTo(-26, -150); g.bezierCurveTo(-52 - (o.wind || 0), -100, -58 - (o.wind || 0), -40, -50 - (o.wind || 0) * 1.4, -4); g.lineTo(50 - (o.wind || 0) * 0.6, -4); g.bezierCurveTo(56, -40, 50, -100, 26, -150); g.closePath(); g.fill(); g.strokeStyle = 'rgba(0,0,0,.35)'; g.lineWidth = 2; for (let i = -2; i <= 2; i++) { g.beginPath(); g.moveTo(i * 10, -140); g.quadraticCurveTo(i * 14, -60, i * 18, -6); g.stroke(); } }
    // nogi
    [-1, 1].forEach(sd => { g.fillStyle = armG(sd * 4, sd * 18); g.beginPath(); g.moveTo(sd * 3, -88); g.lineTo(sd * 18, -88); g.lineTo(sd * 17, -50); g.lineTo(sd * 15, -8); g.lineTo(sd * 5, -8); g.lineTo(sd * 5, -50); g.closePath(); g.fill(); g.fillStyle = rgb(mix(A, AH, 0.6)); g.beginPath(); g.ellipse(sd * 11, -50, 7, 6, 0, 0, TAU); g.fill(); g.fillStyle = rgb(A); g.beginPath(); g.ellipse(sd * 12, -5, 11, 5, 0, 0, TAU); g.fill(); });
    // tors i jupon z herbem
    if (o.stand) { g.fillStyle = armG(-24, 24); g.beginPath(); g.moveTo(-23, -152); g.lineTo(23, -152); g.lineTo(26, -80); g.lineTo(-26, -80); g.closePath(); g.fill(); g.strokeStyle = rgb(AH, 0.5); g.lineWidth = 2; g.beginPath(); g.moveTo(0, -150); g.lineTo(0, -84); g.stroke(); }
    else if (o.jupon === false) { g.fillStyle = armG(-24, 24); g.beginPath(); g.moveTo(-23, -152); g.lineTo(23, -152); g.lineTo(28, -70); g.lineTo(-28, -70); g.closePath(); g.fill(); if (o.crest === 'kruk') { g.fillStyle = '#4a2a5a'; g.fillRect(-22, -130, 44, 50); raven(g, 0, -106, 0.8, 1.2, '#0a0a0a'); } }
    else {
      g.save(); g.beginPath(); g.moveTo(-23, -152); g.lineTo(23, -152); g.lineTo(30, -68); g.lineTo(-30, -68); g.closePath(); g.clip();
      g.fillStyle = '#c9a032'; g.fillRect(-32, -155, 64, 46); g.fillStyle = '#8e1816'; g.fillRect(-32, -109, 64, 45);
      sulimaArms(g, 0, -112, 38, 70);
      g.fillStyle = lin(g, -30, 0, 30, 0, ['rgba(0,0,0,.45)', 'rgba(0,0,0,0)', 'rgba(0,0,0,.5)']); g.fillRect(-32, -160, 64, 100); g.restore();
    }
    g.fillStyle = '#b08a2a'; g.fillRect(-27, -76, 54, 5); g.fillStyle = '#e0c060'; g.fillRect(-4, -77, 8, 7);
    // ramiona
    [-1, 1].forEach(sd => { limb(g, [[sd * 25, -142], [sd * 31, -116], [sd * 8, -103]], 11, rgb(mix(A, AH, 0.25)), rgb(AH)); g.fillStyle = lin(g, sd * 15, -150, sd * 37, -130, [rgb(mix(A, AH, 0.6)), rgb(A)]); g.beginPath(); g.ellipse(sd * 26, -143, 12, 9, sd * 0.3, 0, TAU); g.fill(); });
    // miecz — atrybut Zawiszy
    if (!o.stand && o.sword !== false) {
      g.fillStyle = lin(g, -4, 0, 4, 0, ['#8a929a', '#eef2f4', '#6a727a']); g.beginPath(); g.moveTo(-3.5, -98); g.lineTo(3.5, -98); g.lineTo(2.5, -16); g.lineTo(0, -6); g.lineTo(-2.5, -16); g.closePath(); g.fill();
      g.strokeStyle = 'rgba(60,70,80,.6)'; g.lineWidth = 1; g.beginPath(); g.moveTo(0, -96); g.lineTo(0, -24); g.stroke();
      g.fillStyle = '#6a5020'; g.fillRect(-18, -101, 36, 5); g.fillStyle = '#c9a24a'; g.fillRect(-18, -101, 36, 2);
      g.fillStyle = '#2a1a10'; g.fillRect(-2.5, -116, 5, 16);
      g.fillStyle = rgb(mix(A, AH, 0.3)); g.beginPath(); g.ellipse(-4, -105, 6, 5, 0, 0, TAU); g.ellipse(4, -109, 6, 5, 0, 0, TAU); g.fill();
      g.fillStyle = '#c9a24a'; g.beginPath(); g.arc(0, -119, 4.5, 0, TAU); g.fill();
    }
    // kolczy kaptur (czepiec)
    g.fillStyle = '#4a4e56'; g.beginPath(); g.ellipse(0, -154, 15, 8, 0, 0, TAU); g.fill();
    g.fillStyle = 'rgba(160,170,180,.35)'; for (let i = -12; i <= 12; i += 3) for (let j = -158; j <= -150; j += 3) g.fillRect(i, j, 1.2, 1.2);
    // głowa
    if (!o.stand && !o.closed) {
      g.fillStyle = '#c99a7a'; g.beginPath(); g.ellipse(0, -167, 9.5, 11.5, 0, 0, TAU); g.fill();
      g.fillStyle = 'rgba(0,0,0,.25)'; g.beginPath(); g.ellipse(3, -165, 6, 10, 0, 0, TAU); g.fill();
      g.fillStyle = '#120c0a'; g.fillRect(-5.5, -170, 3, 2); g.fillRect(2.5, -170, 3, 2);
      g.strokeStyle = '#140c0a'; g.lineWidth = 1.6; g.beginPath(); g.moveTo(-7, -173); g.lineTo(-2, -172); g.moveTo(2, -172); g.lineTo(7, -173); g.stroke();
      g.fillStyle = '#100a08'; g.beginPath(); g.moveTo(-7, -160); g.quadraticCurveTo(0, -164, 7, -160); g.quadraticCurveTo(0, -161, -7, -160); g.fill(); g.lineWidth = 2.2; g.beginPath(); g.moveTo(-6, -161); g.quadraticCurveTo(0, -165, 6, -161); g.stroke();
    }
    // basinet
    g.fillStyle = lin(g, -14, 0, 14, 0, [rgb(mix(A, AH, 0.75)), rgb(mix(A, AH, 0.3)), rgb(A)]);
    g.beginPath(); g.moveTo(-12, -160); g.bezierCurveTo(-14, -182, -6, -194, 0, -202); g.bezierCurveTo(6, -194, 14, -182, 12, -160);
    if (!o.closed && !o.stand) { g.lineTo(9, -172); g.quadraticCurveTo(0, -178, -9, -172); }
    g.closePath(); g.fill();
    if (o.closed || o.stand) { g.fillStyle = lin(g, -12, 0, 12, 0, [rgb(mix(A, AH, 0.5)), rgb(A)]); g.beginPath(); g.moveTo(-11, -176); g.quadraticCurveTo(0, -178, 11, -176); g.lineTo(3, -158); g.lineTo(0, -152); g.lineTo(-3, -158); g.closePath(); g.fill(); g.fillStyle = '#000'; g.fillRect(-8, -172, 16, 2); for (let i = -2; i <= 2; i++) g.fillRect(i * 3 - 0.6, -164, 1.2, 1.2); }
    if (o.plume) { g.fillStyle = o.plume; g.beginPath(); g.moveTo(0, -200); g.quadraticCurveTo(-30, -230, -40, -200); g.quadraticCurveTo(-20, -215, 0, -196); g.fill(); }
    if (o.crest === 'kruk') { raven(g, 0, -208, 0.9, 1.2, '#050505'); }
    g.restore();
  }

  const SPEC = {
    zawisza: { skin: '#c99a7a', hair: '#141010', beard: 'mustache', cloth: '#1c1e24', hat: 'none', bg: '#3a0c10', armor: true },
    jagiello: { skin: '#cfa284', hair: '#6a5038', beard: 'mustache', cloth: '#7a1414', hat: 'crown', bg: '#2a1a30', ermine: true },
    mikolaj: { skin: '#c8a080', hair: '#888078', beard: 'short', cloth: '#4a3424', hat: 'hood', bg: '#2a2016' },
    agnieszka: { skin: '#e0b898', hair: '#5a3a22', beard: 'none', cloth: '#2e4a34', hat: 'wimple', bg: '#1e2a24', female: true },
    jasko: { skin: '#d8ac8a', hair: '#8a5a2a', beard: 'none', cloth: '#a01a1a', hat: 'chaperon', bg: '#2a2a3a', herald: true },
    stanislaw: { skin: '#d0a888', hair: '#c8c4bc', beard: 'long', cloth: '#7a1a1a', hat: 'biret', bg: '#2a1a14', fur: true },
    wojciech: { skin: '#dcb090', hair: '#a06a30', beard: 'none', cloth: '#2a3a5a', hat: 'cap', bg: '#141c2a', trumpet: true },
    bartosz: { skin: '#b88a6a', hair: '#3a2416', beard: 'full', cloth: '#5a3a22', hat: 'bald', bg: '#3a1a0a', apron: true },
    kruk: { skin: '#000', hair: '#000', beard: 'none', cloth: '#2a2430', hat: 'greathelm', bg: '#1a1420' },
    komtur: { skin: '#b8b0a8', hair: '#000', beard: 'none', cloth: '#0c0a0e', hat: 'blackhood', bg: '#0a1410', eyes: true },
    kronika: { skin: '#000', hat: 'book', bg: '#2a1e14' },
  };
  function face(g, cx, cy, p, k = 1) {
    g.fillStyle = lin(g, cx - 44 * k, 0, cx + 44 * k, 0, [rgb(mix(p.skin, '#fff', 0.15)), rgb(p.skin), rgb(mix(p.skin, '#000', 0.35))]);
    g.beginPath(); g.ellipse(cx, cy, 40 * k, 50 * k, 0, 0, TAU); g.fill();
    // oczy
    [-1, 1].forEach(sd => { g.fillStyle = '#efe6dc'; g.beginPath(); g.ellipse(cx + sd * 15 * k, cy - 6 * k, 7 * k, 4 * k, 0, 0, TAU); g.fill(); g.fillStyle = p.eyes ? '#9af0c0' : '#2a1a10'; g.beginPath(); g.arc(cx + sd * 15 * k, cy - 6 * k, 3.4 * k, 0, TAU); g.fill(); g.strokeStyle = rgb(mix(p.hair, '#000', 0.3)); g.lineWidth = 3.4 * k; g.beginPath(); g.moveTo(cx + sd * 7 * k, cy - 15 * k); g.lineTo(cx + sd * 23 * k, cy - (p.female ? 18 : 14) * k); g.stroke(); });
    g.strokeStyle = rgb(mix(p.skin, '#000', 0.4)); g.lineWidth = 2.4 * k; g.beginPath(); g.moveTo(cx - 2 * k, cy - 4 * k); g.lineTo(cx - 5 * k, cy + 12 * k); g.lineTo(cx + 3 * k, cy + 14 * k); g.stroke();
    g.strokeStyle = rgb(mix(p.skin, '#600', 0.4)); g.lineWidth = 2.6 * k; g.beginPath(); g.moveTo(cx - 9 * k, cy + 26 * k); g.quadraticCurveTo(cx, cy + 28 * k, cx + 9 * k, cy + 26 * k); g.stroke();
    g.fillStyle = 'rgba(0,0,0,.18)'; g.beginPath(); g.ellipse(cx + 18 * k, cy + 8 * k, 16 * k, 30 * k, 0, 0, TAU); g.fill();
  }
  function portrait(id) {
    const p = SPEC[id] || SPEC.kronika; seed(id.length * 977 + id.charCodeAt(0));
    const c = cv(220, 260), g = c.getContext('2d');
    paint(g, rectP(0, 0, 220, 260), p.bg, { cols: [p.bg, mix(p.bg, '#000', 0.4), mix(p.bg, '#806040', 0.2)], len: 30, w: 12, aj: 2, a: 0.35 });
    glow(g, 70, 70, 160, mix(p.bg, '#ffb070', 0.5), 0.25);
    if (id === 'kronika') { paintPoly(g, [[30, 200], [110, 180], [190, 200], [190, 80], [110, 60], [30, 80]], '#e8d8b0', { a: 0.25 }); g.strokeStyle = '#4a2a10'; g.lineWidth = 3; g.beginPath(); g.moveTo(110, 60); g.lineTo(110, 180); g.stroke(); g.lineWidth = 1.5; for (let i = 0; i < 7; i++) { g.beginPath(); g.moveTo(42, 100 + i * 12); g.lineTo(100, 96 + i * 12); g.moveTo(120, 96 + i * 12); g.lineTo(178, 100 + i * 12); g.stroke(); } g.fillStyle = '#8a1a14'; g.font = 'bold 30px Georgia'; g.fillText('K', 48, 100); vignette(g, 220, 260, 0.6); return c; }
    const cx = 110, cy = 120;
    // ramiona
    const sh = g2 => { g2.moveTo(10, 260); g2.quadraticCurveTo(20, 190, 70, 182); g2.lineTo(150, 182); g2.quadraticCurveTo(200, 190, 210, 260); g2.closePath(); };
    paint(g, sh, p.cloth, { box: [0, 170, 220, 90], cols: [p.cloth, mix(p.cloth, '#000', 0.3), mix(p.cloth, '#fff', 0.12)], len: 22, w: 8, aj: 1, a: 0.35, shade: [0, 0.3] });
    if (p.armor) { g.fillStyle = lin(g, 20, 0, 200, 0, ['#0e0f12', '#5a626e', '#1c1e24']); g.beginPath(); g.ellipse(46, 214, 46, 30, -0.3, 0, TAU); g.ellipse(174, 214, 46, 30, 0.3, 0, TAU); g.fill(); g.fillStyle = '#4a4e56'; g.beginPath(); g.ellipse(cx, 184, 52, 22, 0, 0, TAU); g.fill(); g.fillStyle = 'rgba(170,180,190,.35)'; for (let i = 64; i < 158; i += 4) for (let j = 168; j < 200; j += 4) g.fillRect(i, j, 1.6, 1.6); sulimaArms(g, cx, 236, 46, 56); }
    if (p.ermine) { g.fillStyle = '#efe8dc'; g.beginPath(); g.ellipse(cx, 196, 80, 22, 0, 0, TAU); g.fill(); g.fillStyle = '#111'; for (let i = 0; i < 12; i++) g.fillRect(40 + i * 12, 190 + (i % 2) * 8, 3, 6); }
    if (p.fur) { g.fillStyle = '#7a6a58'; g.beginPath(); g.ellipse(cx, 192, 70, 18, 0, 0, TAU); g.fill(); }
    if (p.herald) { g.fillStyle = '#e8e0d0'; g.fillRect(cx, 182, 100, 40); g.fillRect(0, 222, cx, 40); g.fillStyle = '#c9a24a'; g.font = 'bold 22px Georgia'; g.fillText('✠', cx + 10, 212); }
    if (p.apron) { g.fillStyle = '#3a2416'; g.fillRect(cx - 50, 196, 100, 70); g.strokeStyle = '#1a0e08'; g.lineWidth = 4; g.beginPath(); g.moveTo(cx - 50, 196); g.lineTo(cx - 70, 180); g.moveTo(cx + 50, 196); g.lineTo(cx + 70, 180); g.stroke(); }
    // szyja
    g.fillStyle = rgb(mix(p.skin, '#000', 0.25)); if (p.skin !== '#000') g.fillRect(cx - 18, 150, 36, 38);
    // tył kaptura / włosy
    if (p.hat === 'hood' || p.hat === 'blackhood') { g.fillStyle = rgb(p.hat === 'hood' ? p.cloth : '#0a080c'); g.beginPath(); g.ellipse(cx, cy - 4, 62, 76, 0, 0, TAU); g.fill(); }
    if (p.hat === 'wimple') { g.fillStyle = '#e8e2d6'; g.beginPath(); g.ellipse(cx, cy + 6, 58, 74, 0, 0, TAU); g.fill(); g.fillRect(cx - 50, 150, 100, 40); }
    if (['none', 'crown', 'chaperon', 'cap', 'biret'].includes(p.hat)) { g.fillStyle = rgb(p.hair); g.beginPath(); g.ellipse(cx, cy - 18, 46, 46, 0, Math.PI, TAU); g.fill(); if (id === 'zawisza' || id === 'jagiello' || id === 'stanislaw') { g.fillRect(cx - 46, cy - 18, 14, id === 'jagiello' ? 80 : 56); g.fillRect(cx + 32, cy - 18, 14, id === 'jagiello' ? 80 : 56); } }
    if (p.hat === 'greathelm') {
      g.fillStyle = lin(g, 50, 0, 170, 0, ['#0c0b0e', '#5a5462', '#1a181e']); g.beginPath(); g.moveTo(58, 190); g.lineTo(56, 70); g.quadraticCurveTo(cx, 30, 164, 70); g.lineTo(162, 190); g.closePath(); g.fill();
      g.fillStyle = '#000'; g.fillRect(64, 108, 92, 7); g.fillRect(cx - 3, 115, 6, 60); for (let i = 0; i < 5; i++) for (let j = 0; j < 3; j++) g.fillRect(74 + i * 6 + (j % 2) * 3, 135 + j * 8, 3, 3);
      raven(g, cx, 34, 2.2, 1.2, '#050505');
    } else if (p.skin !== '#000') face(g, cx, cy, p);
    // brody
    g.fillStyle = rgb(p.hair);
    if (p.beard === 'mustache') { g.beginPath(); g.moveTo(cx - 24, cy + 30); g.quadraticCurveTo(cx, cy + 14, cx + 24, cy + 30); g.quadraticCurveTo(cx, cy + 22, cx - 24, cy + 30); g.fill(); }
    if (p.beard === 'short') { g.globalAlpha = 0.8; g.beginPath(); g.ellipse(cx, cy + 36, 32, 22, 0, 0, Math.PI); g.fill(); g.globalAlpha = 1; }
    if (p.beard === 'long') { g.beginPath(); g.moveTo(cx - 36, cy + 14); g.quadraticCurveTo(cx - 30, cy + 90, cx, cy + 110); g.quadraticCurveTo(cx + 30, cy + 90, cx + 36, cy + 14); g.quadraticCurveTo(cx, cy + 36, cx - 36, cy + 14); g.fill(); g.strokeStyle = 'rgba(0,0,0,.2)'; g.lineWidth = 1.5; for (let i = -3; i <= 3; i++) { g.beginPath(); g.moveTo(cx + i * 8, cy + 36); g.lineTo(cx + i * 6, cy + 96); g.stroke(); } }
    if (p.beard === 'full') { g.beginPath(); g.moveTo(cx - 40, cy); g.quadraticCurveTo(cx - 44, cy + 80, cx, cy + 92); g.quadraticCurveTo(cx + 44, cy + 80, cx + 40, cy); g.quadraticCurveTo(cx + 30, cy + 40, cx, cy + 34); g.quadraticCurveTo(cx - 30, cy + 40, cx - 40, cy); g.fill(); g.fillStyle = rgb(mix(p.skin, '#600', 0.4)); g.fillRect(cx - 8, cy + 26, 16, 3); }
    // nakrycia głowy
    if (p.hat === 'crown') { g.fillStyle = lin(g, 60, 0, 160, 0, ['#8a6a20', '#f0d070', '#9a7a28']); g.beginPath(); g.moveTo(66, 82); g.lineTo(66, 54); g.lineTo(80, 70); g.lineTo(93, 40); g.lineTo(cx, 64); g.lineTo(127, 40); g.lineTo(140, 70); g.lineTo(154, 54); g.lineTo(154, 82); g.closePath(); g.fill(); [[86, 76, '#c02020'], [cx, 76, '#2050c0'], [134, 76, '#20a040']].forEach(([x, y, c2]) => { g.fillStyle = c2; g.beginPath(); g.arc(x, y, 4, 0, TAU); g.fill(); }); }
    if (p.hat === 'hood') { g.fillStyle = rgb(mix(p.cloth, '#000', 0.15)); g.beginPath(); g.moveTo(52, 190); g.quadraticCurveTo(44, 40, cx, 42); g.quadraticCurveTo(176, 40, 168, 190); g.lineTo(152, 190); g.quadraticCurveTo(160, 64, cx, 64); g.quadraticCurveTo(60, 64, 68, 190); g.fill(); }
    if (p.hat === 'blackhood') { g.fillStyle = '#060508'; g.beginPath(); g.moveTo(40, 200); g.quadraticCurveTo(36, 20, cx, 26); g.quadraticCurveTo(184, 20, 180, 200); g.lineTo(160, 200); g.quadraticCurveTo(164, 76, cx, 84); g.quadraticCurveTo(56, 76, 60, 200); g.fill(); g.fillStyle = 'rgba(0,0,0,.55)'; g.beginPath(); g.ellipse(cx, cy - 10, 44, 30, 0, 0, TAU); g.fill(); g.save(); g.globalCompositeOperation = 'lighter'; glow(g, cx - 15, cy - 6, 18, '#6af0b0', 0.6); glow(g, cx + 15, cy - 6, 18, '#6af0b0', 0.6); g.restore(); g.strokeStyle = 'rgba(150,140,140,.5)'; g.lineWidth = 8; g.beginPath(); g.moveTo(cx, 200); g.lineTo(cx, 258); g.moveTo(cx - 30, 222); g.lineTo(cx + 30, 222); g.stroke(); }
    if (p.hat === 'wimple') { g.fillStyle = '#f2ece2'; g.beginPath(); g.moveTo(58, 120); g.quadraticCurveTo(60, 50, cx, 54); g.quadraticCurveTo(160, 50, 162, 120); g.quadraticCurveTo(150, 76, cx, 74); g.quadraticCurveTo(70, 76, 58, 120); g.fill(); g.strokeStyle = 'rgba(0,0,0,.12)'; g.lineWidth = 2; g.beginPath(); g.moveTo(70, 160); g.quadraticCurveTo(cx, 190, 150, 160); g.stroke(); }
    if (p.hat === 'chaperon') { g.fillStyle = '#8a1414'; g.beginPath(); g.ellipse(cx, 70, 60, 22, -0.1, 0, TAU); g.fill(); g.beginPath(); g.moveTo(150, 66); g.quadraticCurveTo(200, 80, 190, 150); g.lineTo(176, 150); g.quadraticCurveTo(180, 96, 140, 80); g.fill(); }
    if (p.hat === 'biret') { g.fillStyle = '#8a1414'; g.beginPath(); g.ellipse(cx, 72, 52, 16, 0, 0, TAU); g.fill(); g.beginPath(); g.ellipse(cx, 60, 44, 22, 0, Math.PI, TAU); g.fill(); g.fillStyle = '#5a0a0a'; g.fillRect(cx - 2, 34, 4, 8); }
    if (p.hat === 'cap') { g.fillStyle = '#1e2a46'; g.beginPath(); g.ellipse(cx, 72, 50, 30, 0, Math.PI, TAU); g.fill(); g.fillRect(60, 70, 100, 8); }
    if (p.trumpet) { g.strokeStyle = '#d0a840'; g.lineWidth = 7; g.beginPath(); g.moveTo(30, 250); g.lineTo(150, 200); g.stroke(); g.fillStyle = '#e0b850'; g.beginPath(); g.moveTo(150, 200); g.lineTo(196, 172); g.lineTo(206, 200); g.closePath(); g.fill(); }
    vignette(g, 220, 260, 0.55);
    return c;
  }
  const NPCB = {
    jagiello: { robe: '#7a1414', ermine: true }, mikolaj: { robe: '#4a3424', hood: true },
    agnieszka: { robe: '#2e4a34', wimple: true }, jasko: { robe: '#a01a1a', herald: true },
    stanislaw: { robe: '#7a1a1a', biret: true }, wojciech: { robe: '#2a3a5a', trumpet: true },
    bartosz: { robe: '#4a3020', apron: true, bald: true }, komtur: { robe: '#0a080c', black: true },
  };
  function drawNPC(g, x, y, s, id, t = 0) {
    const sp = SPEC[id], b = NPCB[id]; if (!sp || !b) return;
    if (id === 'kruk') return drawKnight(g, x, y, s, { armor: '#24202a', hl: '#6a6278', cape: '#141016', closed: true, jupon: false, crest: 'kruk' });
    g.save(); g.translate(x, y); g.scale(s, s);
    g.fillStyle = 'rgba(0,0,0,.4)'; g.beginPath(); g.ellipse(0, 0, 40, 8, 0, 0, TAU); g.fill();
    const sw = Math.sin(t * 1.5) * 1.5;
    const k = b.black ? 1.18 : 1;
    g.scale(k, k);
    g.fillStyle = lin(g, -30, 0, 30, 0, [rgb(mix(b.robe, '#000', 0.45)), rgb(mix(b.robe, '#fff', 0.08)), rgb(mix(b.robe, '#000', 0.5))]);
    g.beginPath(); g.moveTo(-30 - sw, -2); g.lineTo(-22, -128); g.quadraticCurveTo(0, -140, 22, -128); g.lineTo(30 + sw, -2); g.closePath(); g.fill();
    g.strokeStyle = 'rgba(0,0,0,.3)'; g.lineWidth = 1.5; for (let i = -2; i <= 2; i++) { g.beginPath(); g.moveTo(i * 6, -110); g.lineTo(i * 11, -4); g.stroke(); }
    if (b.ermine) { g.fillStyle = '#ece4d6'; g.beginPath(); g.moveTo(-26, -128); g.quadraticCurveTo(0, -116, 26, -128); g.lineTo(24, -112); g.quadraticCurveTo(0, -102, -24, -112); g.fill(); g.fillStyle = '#111'; for (let i = -3; i <= 3; i++) g.fillRect(i * 6, -116, 2, 4); }
    if (b.herald) { g.fillStyle = '#e8e0d0'; g.fillRect(0, -126, 22, 48); g.fillRect(-22, -78, 22, 50); g.fillStyle = '#c9a24a'; g.fillRect(-2, -128, 4, 100); }
    if (b.apron) { g.fillStyle = '#2a1a10'; g.fillRect(-18, -100, 36, 92); }
    if (b.black) { g.strokeStyle = 'rgba(140,130,130,.5)'; g.lineWidth = 4; g.beginPath(); g.moveTo(0, -110); g.lineTo(0, -70); g.moveTo(-14, -96); g.lineTo(14, -96); g.stroke(); }
    if (b.biret) { g.fillStyle = '#6a5a48'; g.beginPath(); g.ellipse(0, -126, 24, 7, 0, 0, TAU); g.fill(); }
    // ręce
    limb(g, [[-22, -122], [-28, -90], [-14, -74]], 9, rgb(mix(b.robe, '#000', 0.2)));
    limb(g, [[22, -122], [28, -90], [14, -74]], 9, rgb(mix(b.robe, '#000', 0.2)));
    g.fillStyle = b.black ? '#9a9088' : rgb(sp.skin); g.beginPath(); g.arc(-12, -73, 4.5, 0, TAU); g.arc(12, -73, 4.5, 0, TAU); g.fill();
    if (b.trumpet) { g.strokeStyle = '#d0a840'; g.lineWidth = 3; g.beginPath(); g.moveTo(-12, -74); g.lineTo(30, -100); g.stroke(); g.fillStyle = '#e0b850'; g.beginPath(); g.moveTo(30, -100); g.lineTo(44, -112); g.lineTo(46, -98); g.fill(); }
    if (b.apron) { g.fillStyle = '#2a2a2a'; g.fillRect(14, -90, 4, 22); g.fillRect(8, -94, 16, 8); }
    if (id === 'mikolaj') { g.fillStyle = '#5a1a14'; g.fillRect(-10, -86, 20, 16); g.fillStyle = '#c9a24a'; g.fillRect(-1, -86, 2, 16); }
    if (id === 'stanislaw') { g.fillStyle = '#e8dcc0'; g.fillRect(-8, -84, 16, 20); }
    if (id === 'agnieszka') { g.fillStyle = '#6a4a2a'; g.beginPath(); g.ellipse(18, -70, 9, 7, 0, 0, TAU); g.fill(); }
    // głowa
    const hy = -146;
    if (b.hood || b.black) { g.fillStyle = b.black ? '#060508' : rgb(mix(b.robe, '#000', 0.15)); g.beginPath(); g.ellipse(0, hy, 17, 21, 0, 0, TAU); g.fill(); g.fillStyle = b.black ? '#000' : rgb(sp.skin); g.beginPath(); g.ellipse(0, hy + 3, 10, 13, 0, 0, TAU); g.fill(); if (!b.black) { g.fillStyle = '#1a100a'; g.fillRect(-5, hy, 2.5, 2); g.fillRect(2.5, hy, 2.5, 2); g.fillStyle = rgb(sp.hair); g.beginPath(); g.ellipse(0, hy + 12, 8, 5, 0, 0, Math.PI); g.fill(); } if (b.black) { g.save(); g.globalCompositeOperation = 'lighter'; glow(g, -4, hy, 6, '#6af0b0', 0.9); glow(g, 4, hy, 6, '#6af0b0', 0.9); g.restore(); } }
    else {
      if (b.wimple) { g.fillStyle = '#ece6da'; g.beginPath(); g.ellipse(0, hy + 2, 15, 19, 0, 0, TAU); g.fill(); }
      g.fillStyle = rgb(sp.skin); g.beginPath(); g.ellipse(0, hy, 10, 12.5, 0, 0, TAU); g.fill();
      g.fillStyle = 'rgba(0,0,0,.2)'; g.beginPath(); g.ellipse(3, hy + 2, 6, 11, 0, 0, TAU); g.fill();
      g.fillStyle = '#1a100a'; g.fillRect(-5, hy - 2, 2.5, 2); g.fillRect(2.5, hy - 2, 2.5, 2);
      g.fillStyle = rgb(sp.hair);
      if (!b.bald && !b.wimple) { g.beginPath(); g.ellipse(0, hy - 6, 11, 8, 0, Math.PI, TAU); g.fill(); }
      if (sp.beard === 'long') { g.beginPath(); g.moveTo(-9, hy + 4); g.quadraticCurveTo(0, hy + 36, 9, hy + 4); g.fill(); }
      if (sp.beard === 'full') { g.beginPath(); g.moveTo(-10, hy); g.quadraticCurveTo(0, hy + 26, 10, hy); g.quadraticCurveTo(0, hy + 8, -10, hy); g.fill(); }
      if (sp.beard === 'mustache') { g.fillRect(-6, hy + 5, 12, 2.5); }
      if (sp.beard === 'short') { g.beginPath(); g.ellipse(0, hy + 8, 9, 6, 0, 0, Math.PI); g.fill(); }
      if (b.ermine) { g.fillStyle = '#e0b850'; g.beginPath(); g.moveTo(-11, hy - 8); g.lineTo(-11, hy - 18); g.lineTo(-6, hy - 13); g.lineTo(0, hy - 21); g.lineTo(6, hy - 13); g.lineTo(11, hy - 18); g.lineTo(11, hy - 8); g.fill(); }
      if (b.biret) { g.fillStyle = '#8a1414'; g.beginPath(); g.ellipse(0, hy - 9, 13, 6, 0, 0, TAU); g.fill(); }
      if (b.herald) { g.fillStyle = '#8a1414'; g.beginPath(); g.ellipse(0, hy - 10, 15, 6, -0.1, 0, TAU); g.fill(); }
      if (b.trumpet) { g.fillStyle = '#1e2a46'; g.beginPath(); g.ellipse(0, hy - 8, 12, 7, 0, Math.PI, TAU); g.fill(); }
    }
    g.restore();
  }
  /* jeździec w gonitwie (widok z boku) */
  function drawRider(g, x, y, s, o, t) {
    g.save(); g.translate(x, y); g.scale(s * o.dir, s);
    const bob = Math.sin(t * 16) * 3, ph = t * 16;
    // nogi konia
    const legs = [[-34, 0], [-24, 1.5], [26, 3], [36, 4.5]];
    legs.forEach(([lx, off]) => { const a = Math.sin(ph + off) * 0.6; g.save(); g.translate(lx, -50 + bob); g.rotate(a); g.fillStyle = '#2a1e18'; g.fillRect(-4, 0, 8, 26); g.translate(0, 26); g.rotate(-Math.abs(a) * 0.8); g.fillRect(-3.5, 0, 7, 24); g.fillStyle = '#111'; g.fillRect(-4.5, 22, 9, 5); g.restore(); });
    // ogon
    g.strokeStyle = '#1a120e'; g.lineWidth = 6; g.beginPath(); g.moveTo(-52, -76 + bob); g.quadraticCurveTo(-74, -60 + Math.sin(ph) * 6, -70, -36); g.stroke();
    // tułów i szyja
    g.fillStyle = '#3a2a22'; g.beginPath(); g.ellipse(0, -72 + bob, 54, 24, 0, 0, TAU); g.fill();
    g.beginPath(); g.moveTo(34, -86 + bob); g.lineTo(62, -122 + bob); g.lineTo(78, -118 + bob); g.lineTo(56, -70 + bob); g.fill();
    g.beginPath(); g.ellipse(80, -118 + bob, 18, 9, 0.5, 0, TAU); g.fill();
    g.fillStyle = '#8a8e96'; g.beginPath(); g.ellipse(82, -118 + bob, 14, 6, 0.5, 0, TAU); g.fill();
    // kropierz (kapa)
    g.fillStyle = o.cap1; g.beginPath(); g.moveTo(-56, -84 + bob); g.lineTo(50, -92 + bob); g.lineTo(70, -116 + bob); g.lineTo(78, -104 + bob); g.lineTo(58, -40 + bob); g.lineTo(-58, -38 + bob); g.closePath(); g.fill();
    g.fillStyle = o.cap2; for (let i = 0; i < 5; i++) { g.beginPath(); g.moveTo(-50 + i * 24, -38 + bob); g.lineTo(-38 + i * 24, -84 + bob); g.lineTo(-28 + i * 24, -84 + bob); g.lineTo(-40 + i * 24, -38 + bob); g.fill(); }
    // jeździec
    g.fillStyle = o.armor; g.fillRect(-12, -126 + bob, 24, 42); g.fillRect(-8, -92 + bob, 14, 32);
    if (o.arms) sulimaArms(g, 14, -110 + bob, 22, 28); else { g.fillStyle = o.cap2; g.beginPath(); g.moveTo(4, -124 + bob); g.lineTo(26, -124 + bob); g.lineTo(26, -104 + bob); g.lineTo(15, -94 + bob); g.lineTo(4, -104 + bob); g.fill(); raven(g, 15, -110 + bob, 0.4, 1.2, '#000'); }
    // hełm żabi pysk
    g.fillStyle = lin(g, -12, 0, 12, 0, ['#2a2c30', '#9aa0a8', '#3a3c40']); g.beginPath(); g.moveTo(-11, -126 + bob); g.lineTo(-12, -150 + bob); g.quadraticCurveTo(0, -160 + bob, 12, -150 + bob); g.lineTo(14, -140 + bob); g.lineTo(11, -126 + bob); g.closePath(); g.fill();
    g.fillStyle = '#000'; g.fillRect(2, -146 + bob, 12, 2.5);
    if (o.plume) { g.fillStyle = o.plume; g.beginPath(); g.moveTo(-4, -156 + bob); g.quadraticCurveTo(-30, -176 + bob + Math.sin(ph) * 3, -46, -150 + bob); g.quadraticCurveTo(-24, -160 + bob, -4, -152 + bob); g.fill(); }
    // kopia
    const L = o.broken ? 70 : 190;
    g.save(); g.translate(0, -112 + bob); g.rotate(-0.05);
    g.fillStyle = lin(g, 0, -4, 0, 4, ['#e8d8b0', '#a08050', '#6a5030']); g.beginPath(); g.moveTo(-36, -3); g.lineTo(L, -2); g.lineTo(L, 2); g.lineTo(-36, 4); g.fill();
    if (!o.broken) { g.fillStyle = '#9aa0a8'; g.beginPath(); g.moveTo(L, -4); g.lineTo(L + 12, 0); g.lineTo(L, 4); g.fill(); }
    else { g.fillStyle = '#e8d8b0'; g.beginPath(); g.moveTo(L, -3); g.lineTo(L + 8, -6); g.lineTo(L + 5, 0); g.lineTo(L + 10, 4); g.lineTo(L, 3); g.fill(); }
    g.fillStyle = '#5a5e66'; g.beginPath(); g.moveTo(10, 0); g.lineTo(28, -12); g.lineTo(28, 12); g.closePath(); g.fill();
    g.restore();
    g.restore();
  }
  /* jednostki bitewne (widok z boku) */
  const UNIT = {
    piechur: { body: '#8e1816', trim: '#c9a032', helm: '#6a6e76', w: 'spear' },
    kusznik: { body: '#6a4a20', trim: '#c9a032', helm: '#5a5e66', w: 'xbow' },
    rycerz: { body: '#c9a032', trim: '#8e1816', helm: '#8a929c', w: 'sword', shield: true },
    zawisza: { body: '#1c1e24', trim: '#c9a032', helm: '#2a2c32', w: 'bigsword', shield: true, big: true },
    najemnik: { body: '#2a2a30', trim: '#4a3a5a', helm: '#3a3a40', w: 'axe' },
    wrogkusznik: { body: '#262028', trim: '#3a3040', helm: '#33303a', w: 'xbow' },
    czarnyrycerz: { body: '#141218', trim: '#5a4a6a', helm: '#24222a', w: 'sword', shield: true },
    komtur: { body: '#060508', trim: '#6af0b0', helm: '#0a080c', w: 'bigsword', big: true, cloak: true },
  };
  function drawUnit(g, x, y, s, type, dir, t, hit) {
    const u = UNIT[type]; g.save(); g.translate(x, y); g.scale(s * dir * (u.big ? 1.25 : 1), s * (u.big ? 1.25 : 1));
    const b = Math.sin(t * 4 + x) * 1.2;
    g.fillStyle = 'rgba(0,0,0,.4)'; g.beginPath(); g.ellipse(0, 0, 18, 4, 0, 0, TAU); g.fill();
    if (u.cloak) { g.fillStyle = '#050406'; g.beginPath(); g.moveTo(-6, -44); g.quadraticCurveTo(-26, -20, -22, 0); g.lineTo(14, 0); g.quadraticCurveTo(8, -20, 6, -44); g.fill(); }
    g.fillStyle = '#1a1614'; g.fillRect(-6, -20, 5, 20); g.fillRect(2, -20, 5, 20);
    g.fillStyle = u.body; g.beginPath(); g.moveTo(-9, -46 + b); g.lineTo(9, -46 + b); g.lineTo(11, -16); g.lineTo(-11, -16); g.closePath(); g.fill();
    g.fillStyle = u.trim; g.fillRect(-10, -22, 21, 3);
    g.fillStyle = hit ? '#fff' : (type === 'komtur' ? '#000' : '#c99a7a'); g.beginPath(); g.arc(1, -52 + b, 6, 0, TAU); g.fill();
    g.fillStyle = u.helm; g.beginPath(); g.moveTo(-7, -52 + b); g.quadraticCurveTo(0, -66 + b, 8, -52 + b); g.lineTo(8, -50 + b); g.lineTo(-7, -50 + b); g.fill();
    if (type === 'komtur') { g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 4, -53 + b, 5, '#6af0b0', 1); g.restore(); }
    if (type === 'zawisza') { g.fillStyle = '#8e1816'; g.beginPath(); g.moveTo(-8, -44); g.quadraticCurveTo(-20, -20, -16, -2); g.lineTo(-8, -4); g.fill(); }
    g.strokeStyle = '#3a2a1a'; g.lineWidth = 2.4; g.lineCap = 'round';
    if (u.w === 'spear') { g.beginPath(); g.moveTo(-4, -20); g.lineTo(26, -50 + b); g.stroke(); g.fillStyle = '#c8ccd2'; g.beginPath(); g.moveTo(26, -50 + b); g.lineTo(33, -58 + b); g.lineTo(28, -48 + b); g.fill(); }
    if (u.w === 'xbow') { g.beginPath(); g.moveTo(2, -34); g.lineTo(22, -36); g.stroke(); g.strokeStyle = '#5a4a3a'; g.beginPath(); g.moveTo(20, -44); g.quadraticCurveTo(26, -36, 20, -28); g.stroke(); }
    if (u.w === 'axe') { g.beginPath(); g.moveTo(4, -30); g.lineTo(18, -52 + b); g.stroke(); g.fillStyle = '#8a8e96'; g.beginPath(); g.moveTo(16, -54 + b); g.quadraticCurveTo(26, -52 + b, 24, -42 + b); g.lineTo(18, -48 + b); g.fill(); }
    if (u.w === 'sword' || u.w === 'bigsword') { g.strokeStyle = '#dfe4ea'; g.lineWidth = u.w === 'bigsword' ? 3 : 2.2; g.beginPath(); g.moveTo(8, -32); g.lineTo(26, -58 + b); g.stroke(); g.strokeStyle = '#c9a24a'; g.lineWidth = 2; g.beginPath(); g.moveTo(4, -36); g.lineTo(12, -28); g.stroke(); }
    if (u.shield) { if (type === 'zawisza') sulimaArms(g, -4, -32, 14, 18); else { g.fillStyle = u.trim; g.beginPath(); g.moveTo(-12, -42); g.lineTo(2, -42); g.lineTo(2, -28); g.lineTo(-5, -22); g.lineTo(-12, -28); g.fill(); } }
    g.restore();
  }

  /* =================== IKONY =================== */
  const ICON = {};
  function iconBase(g, glowCol) { const gr = g.createRadialGradient(32, 30, 4, 32, 32, 44); gr.addColorStop(0, rgb(mix(glowCol || '#3a2a20', '#000', 0.1))); gr.addColorStop(1, '#0e0a08'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); }
  const IC = {
    miecz: g => { g.translate(32, 32); g.rotate(-Math.PI / 4); g.fillStyle = lin(g, -3, 0, 3, 0, ['#8a929a', '#f4f6f8', '#6a727a']); g.beginPath(); g.moveTo(-3, -6); g.lineTo(3, -6); g.lineTo(2, 22); g.lineTo(0, 27); g.lineTo(-2, 22); g.fill(); g.fillStyle = '#c9a24a'; g.fillRect(-11, -9, 22, 4); g.fillStyle = '#3a2210'; g.fillRect(-2, -20, 4, 11); g.fillStyle = '#e0c060'; g.beginPath(); g.arc(0, -22, 3.5, 0, TAU); g.fill(); },
    szczerbiec: g => { g.translate(32, 32); g.rotate(-Math.PI / 4); g.fillStyle = lin(g, -3, 0, 3, 0, ['#9aa2aa', '#ffffff', '#7a828a']); g.beginPath(); g.moveTo(-3, -4); g.lineTo(3, -4); g.lineTo(2, 22); g.lineTo(0, 27); g.lineTo(-2, 22); g.fill(); g.fillStyle = '#0e0a08'; g.beginPath(); g.moveTo(3, 4); g.lineTo(0.5, 7); g.lineTo(3, 9); g.fill(); g.fillStyle = lin(g, -12, 0, 12, 0, ['#9a7a28', '#ffe080', '#9a7a28']); g.fillRect(-12, -8, 24, 5); g.fillRect(-2.5, -20, 5, 12); g.beginPath(); g.arc(0, -22, 5, 0, TAU); g.fill(); g.fillStyle = '#c02020'; g.beginPath(); g.arc(0, -22, 2, 0, TAU); g.fill(); g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 0, 0, 30, '#ffd070', 0.25); g.restore(); },
    kolczuga: g => { g.fillStyle = '#5a5e66'; g.beginPath(); g.moveTo(14, 16); g.lineTo(24, 10); g.lineTo(40, 10); g.lineTo(50, 16); g.lineTo(54, 34); g.lineTo(46, 36); g.lineTo(46, 54); g.lineTo(18, 54); g.lineTo(18, 36); g.lineTo(10, 34); g.closePath(); g.fill(); g.fillStyle = 'rgba(200,210,220,.5)'; for (let i = 14; i < 52; i += 3) for (let j = 12; j < 54; j += 3) if ((i + j) % 2) g.fillRect(i, j, 1.4, 1.4); g.fillStyle = '#0e0a08'; g.beginPath(); g.ellipse(32, 12, 7, 4, 0, 0, TAU); g.fill(); },
    zbroja: g => { g.fillStyle = lin(g, 12, 0, 52, 0, ['#0c0d10', '#6a7280', '#14161a']); g.beginPath(); g.moveTo(16, 14); g.lineTo(26, 10); g.lineTo(38, 10); g.lineTo(48, 14); g.lineTo(50, 40); g.lineTo(32, 56); g.lineTo(14, 40); g.closePath(); g.fill(); g.strokeStyle = 'rgba(180,190,200,.6)'; g.lineWidth = 1.5; g.beginPath(); g.moveTo(32, 12); g.lineTo(32, 52); g.moveTo(18, 30); g.quadraticCurveTo(32, 36, 46, 30); g.stroke(); g.fillStyle = '#c9a24a'; g.fillRect(16, 40, 32, 3); },
    tarcza: g => { sulimaArms(g, 32, 33, 40, 48); },
    helm: g => { g.fillStyle = lin(g, 14, 0, 50, 0, ['#2a2c32', '#b0b6be', '#3a3c42']); g.beginPath(); g.moveTo(16, 48); g.bezierCurveTo(14, 26, 24, 14, 32, 6); g.bezierCurveTo(40, 14, 50, 26, 48, 48); g.closePath(); g.fill(); g.fillStyle = '#4a4e56'; g.beginPath(); g.moveTo(18, 30); g.quadraticCurveTo(32, 26, 46, 30); g.lineTo(36, 52); g.lineTo(32, 58); g.lineTo(28, 52); g.closePath(); g.fill(); g.fillStyle = '#000'; g.fillRect(22, 33, 20, 2.5); },
    kopia: g => { g.translate(32, 32); g.rotate(-Math.PI / 4); g.fillStyle = lin(g, 0, -4, 0, 4, ['#e8d8b0', '#a08050']); g.fillRect(-28, -2.5, 54, 5); g.fillStyle = '#8a8e96'; g.beginPath(); g.moveTo(-16, 0); g.lineTo(-4, -8); g.lineTo(-4, 8); g.fill(); g.fillStyle = '#c8ccd2'; g.beginPath(); g.moveTo(26, -4); g.lineTo(31, -4); g.lineTo(29, 0); g.lineTo(31, 4); g.lineTo(26, 4); g.fill(); },
    ziola: g => { g.strokeStyle = '#3a5a2a'; g.lineWidth = 2; for (let i = 0; i < 7; i++) { const a = -Math.PI / 2 + (i - 3) * 0.25; g.beginPath(); g.moveTo(32, 54); g.quadraticCurveTo(32 + Math.cos(a) * 10, 40, 32 + Math.cos(a) * 22, 54 + Math.sin(a) * 40); g.stroke(); g.fillStyle = i % 2 ? '#6a9a4a' : '#8aba5a'; g.beginPath(); g.ellipse(32 + Math.cos(a) * 22, 54 + Math.sin(a) * 40, 5, 3, a, 0, TAU); g.fill(); } g.fillStyle = '#8a1a14'; g.fillRect(26, 46, 12, 5); g.fillStyle = '#b07ad0'; g.beginPath(); g.arc(24, 18, 3, 0, TAU); g.arc(40, 16, 3, 0, TAU); g.fill(); },
    chleb: g => { g.fillStyle = lin(g, 0, 18, 0, 50, ['#d8a050', '#8a5420']); g.beginPath(); g.ellipse(32, 36, 22, 14, 0, 0, TAU); g.fill(); g.strokeStyle = '#6a3a10'; g.lineWidth = 2; for (let i = -1; i <= 1; i++) { g.beginPath(); g.moveTo(26 + i * 10, 26); g.lineTo(34 + i * 10, 40); g.stroke(); } },
    pochodnia: g => { g.fillStyle = '#4a2a14'; g.save(); g.translate(32, 36); g.rotate(0.2); g.fillRect(-3, -6, 6, 30); g.fillStyle = '#2a1a10'; g.fillRect(-5, -10, 10, 8); g.restore(); g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 31, 20, 26, '#ff8a2a', 0.8); glow(g, 31, 22, 9, '#fff0a0', 1); g.restore(); },
    list: g => { g.fillStyle = '#e8dcbc'; g.fillRect(14, 16, 36, 34); g.fillStyle = '#c8b890'; g.beginPath(); g.ellipse(14, 33, 4, 17, 0, 0, TAU); g.ellipse(50, 33, 4, 17, 0, 0, TAU); g.fill(); g.strokeStyle = 'rgba(60,40,20,.5)'; g.lineWidth = 1; for (let i = 0; i < 5; i++) { g.beginPath(); g.moveTo(20, 22 + i * 5); g.lineTo(44, 22 + i * 5); g.stroke(); } g.fillStyle = '#9a1a14'; g.beginPath(); g.arc(32, 48, 6, 0, TAU); g.fill(); g.fillStyle = '#c03020'; g.fillRect(29, 52, 2, 8); g.fillRect(33, 52, 2, 8); },
    pieczec: g => { g.fillStyle = lin(g, 12, 0, 52, 0, ['#8a6a20', '#f0d070', '#8a6a20']); g.beginPath(); g.arc(32, 32, 22, 0, TAU); g.fill(); g.strokeStyle = '#6a4a10'; g.lineWidth = 2; g.beginPath(); g.arc(32, 32, 18, 0, TAU); g.stroke(); g.fillStyle = '#6a4a10'; g.fillRect(25, 26, 14, 14); g.fillRect(28, 20, 8, 6); g.beginPath(); g.moveTo(26, 20); g.lineTo(28, 15); g.lineTo(32, 19); g.lineTo(36, 15); g.lineTo(38, 20); g.fill(); g.fillRect(22, 40, 20, 3); },
    ostroga: g => { g.strokeStyle = lin(g, 10, 0, 50, 0, ['#9a7a28', '#ffe080', '#9a7a28']); g.lineWidth = 5; g.beginPath(); g.arc(28, 30, 15, Math.PI * 0.3, Math.PI * 1.7, true); g.stroke(); g.lineWidth = 3; g.beginPath(); g.moveTo(42, 30); g.lineTo(52, 30); g.stroke(); g.fillStyle = '#ffd860'; for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4; g.beginPath(); g.moveTo(54, 30); g.lineTo(54 + Math.cos(a) * 7, 30 + Math.sin(a) * 7); g.lineTo(54 + Math.cos(a + 0.3) * 3, 30 + Math.sin(a + 0.3) * 3); g.fill(); } },
    przywilej: g => { g.fillStyle = '#ecdcb4'; g.fillRect(12, 10, 40, 40); g.strokeStyle = 'rgba(60,30,10,.55)'; g.lineWidth = 1; for (let i = 0; i < 7; i++) { g.beginPath(); g.moveTo(16, 16 + i * 4.5); g.lineTo(48, 16 + i * 4.5); g.stroke(); } g.fillStyle = '#8a1a14'; g.font = 'bold 10px Georgia'; g.fillText('MCD', 22, 14); g.strokeStyle = '#c9a24a'; g.lineWidth = 1.5; g.beginPath(); g.moveTo(26, 50); g.lineTo(24, 58); g.moveTo(38, 50); g.lineTo(40, 58); g.stroke(); g.fillStyle = '#b08a2a'; g.beginPath(); g.arc(32, 54, 7, 0, TAU); g.fill(); },
    wlocznia: g => { g.translate(32, 32); g.rotate(-Math.PI / 4); g.fillStyle = '#5a3a1a'; g.fillRect(-28, -2, 40, 4); g.fillStyle = lin(g, 0, -6, 0, 6, ['#6a6e76', '#d8dce2', '#5a5e66']); g.beginPath(); g.moveTo(10, -6); g.lineTo(30, 0); g.lineTo(10, 6); g.closePath(); g.fill(); g.fillStyle = '#e0c060'; g.fillRect(8, -7, 6, 14); g.fillStyle = '#c0a040'; g.fillRect(14, -2, 10, 4); },
    zloto: g => { [[22, 40], [40, 42], [31, 26]].forEach(([x, y]) => { g.fillStyle = lin(g, x - 10, 0, x + 10, 0, ['#9a7a28', '#ffe080', '#9a7a28']); g.beginPath(); g.ellipse(x, y, 12, 12, 0, 0, TAU); g.fill(); g.strokeStyle = '#7a5a18'; g.lineWidth = 1.5; g.beginPath(); g.arc(x, y, 8, 0, TAU); g.stroke(); }); },
    honor: g => { g.fillStyle = lin(g, 16, 0, 48, 0, ['#8a6a20', '#f0d070', '#8a6a20']); g.beginPath(); g.moveTo(32, 8); g.lineTo(38, 24); g.lineTo(56, 24); g.lineTo(42, 34); g.lineTo(48, 52); g.lineTo(32, 42); g.lineTo(16, 52); g.lineTo(22, 34); g.lineTo(8, 24); g.lineTo(26, 24); g.closePath(); g.fill(); },
    wiedza: g => { g.fillStyle = '#5a1a14'; g.fillRect(12, 16, 40, 34); g.fillStyle = '#e8dcbc'; g.fillRect(15, 18, 16, 28); g.fillRect(33, 18, 16, 28); g.strokeStyle = 'rgba(60,30,10,.5)'; for (let i = 0; i < 5; i++) { g.beginPath(); g.moveTo(17, 23 + i * 5); g.lineTo(29, 23 + i * 5); g.moveTo(35, 23 + i * 5); g.lineTo(47, 23 + i * 5); g.stroke(); } },
    zdrowie: g => { g.fillStyle = '#b01a1a'; g.beginPath(); g.moveTo(32, 52); g.bezierCurveTo(4, 32, 14, 8, 32, 22); g.bezierCurveTo(50, 8, 60, 32, 32, 52); g.fill(); g.fillStyle = 'rgba(255,255,255,.3)'; g.beginPath(); g.ellipse(22, 24, 5, 3, -0.6, 0, TAU); g.fill(); },
    mrok: g => { g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 32, 32, 26, '#6af0b0', 0.4); g.restore(); g.fillStyle = '#0a0a0c'; g.beginPath(); g.ellipse(32, 32, 22, 12, 0, 0, TAU); g.fill(); g.fillStyle = '#6af0b0'; g.beginPath(); g.ellipse(32, 32, 5, 9, 0, 0, TAU); g.fill(); },
    poczet: g => { g.fillStyle = '#8e1816'; g.fillRect(30, 8, 3, 48); g.fillStyle = '#c9a032'; g.beginPath(); g.moveTo(33, 10); g.lineTo(54, 16); g.lineTo(33, 24); g.fill(); g.fillStyle = '#8a929c'; g.beginPath(); g.moveTo(10, 50); g.bezierCurveTo(10, 34, 18, 28, 22, 22); g.bezierCurveTo(26, 28, 32, 34, 32, 50); g.fill(); },
    dzien: g => { g.save(); g.globalCompositeOperation = 'lighter'; glow(g, 32, 32, 26, '#ffb050', 0.4); g.restore(); g.fillStyle = '#e8c070'; g.beginPath(); g.arc(32, 32, 14, 0, TAU); g.fill(); g.fillStyle = '#0e0a08'; g.beginPath(); g.arc(38, 28, 12, 0, TAU); g.fill(); },
  };
  const iconGlow = { pieczec: '#6a5020', ostroga: '#6a5020', przywilej: '#5a3a20', wlocznia: '#3a3a5a', szczerbiec: '#7a5a20' };
  function icon(id) { if (ICON[id]) return ICON[id]; const c = cv(64, 64), g = c.getContext('2d'); iconBase(g, iconGlow[id]); g.save(); (IC[id] || IC.list)(g); g.restore(); g.strokeStyle = 'rgba(201,162,74,.35)'; g.lineWidth = 2; g.strokeRect(1, 1, 62, 62); ICON[id] = c; return c; }
  const URL_ = {};
  function iconURL(id) { return URL_[id] || (URL_[id] = icon(id).toDataURL()); }

  /* =================== CACHE =================== */
  const cache = {}, pcache = {};
  const ORDER = ['title', 'map', 'wawel', 'rynek', 'kazimierz', 'turniej', 'akademia', 'mariacki', 'smocza', 'bitwa', 'koniec'];
  function build(name) { seed(name.split('').reduce((a, c) => a * 31 + c.charCodeAt(0), 7) >>> 0); const c = cv(1280, 720), g = c.getContext('2d'); BG[name](g, 1280, 720); cache[name] = c; return c; }
  function bg(name) { return cache[name] || build(name); }
  function preload(onStep) {
    return new Promise(res => { let i = 0; const next = () => { if (i >= ORDER.length) { Object.keys(SPEC).forEach(k => pcache[k] = portrait(k)); res(); return; } build(ORDER[i]); i++; onStep && onStep(i / ORDER.length, ORDER[i - 1]); setTimeout(next, 10); }; next(); });
  }
  function getPortrait(id) { return pcache[id] || (pcache[id] = portrait(id)); }
  return { bg, preload, portrait: getPortrait, icon, iconURL, drawKnight, drawNPC, drawRider, drawUnit, raven, glow, rgb, mix, sulimaArms, stroke };
})();
