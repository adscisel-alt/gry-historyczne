'use strict';
/* =====================================================================
   MINIGRY — każda przejmuje płótno i panel #mg, a na końcu woła done(win).
   1) Waga kupiecka   2) Gonitwa na kopie   3) Zamek dziejów (oś czasu)
   4) Hejnał (pamięć dźwięków)   5) Bitwa w Smoczej Jamie (strategia)
   ===================================================================== */
const MG = (() => {
  const W = 1280, H = 720, TAU = Math.PI * 2;
  const $ = s => document.querySelector(s);
  function panel(html) { const p = $('#mg'); p.innerHTML = html; p.classList.remove('hidden'); return p; }
  function hidePanel() { $('#mg').classList.add('hidden'); $('#mg').innerHTML = ''; }
  function txt(g, s, x, y, size = 22, col = '#f0e2c0', align = 'center', font = 'Cinzel, Georgia, serif') { g.font = `${size}px ${font}`; g.textAlign = align; g.fillStyle = 'rgba(0,0,0,.7)'; g.fillText(s, x + 2, y + 2); g.fillStyle = col; g.fillText(s, x, y); }
  function plate(g, x, y, w, h, a = 0.75) { g.fillStyle = `rgba(14,10,8,${a})`; g.fillRect(x, y, w, h); g.strokeStyle = 'rgba(201,162,74,.7)'; g.lineWidth = 2; g.strokeRect(x + 0.5, y + 0.5, w - 1, h - 1); }
  const parts = [];
  function burst(x, y, col, n = 20, sp = 260) { for (let i = 0; i < n; i++) { const a = Math.random() * TAU, v = Math.random() * sp; parts.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 80, life: 0.6 + Math.random() * 0.6, col, s: 2 + Math.random() * 4 }); } }
  function drawParts(g, dt) { for (let i = parts.length - 1; i >= 0; i--) { const p = parts[i]; p.life -= dt; if (p.life <= 0) { parts.splice(i, 1); continue; } p.vy += 400 * dt; p.x += p.vx * dt; p.y += p.vy * dt; g.globalAlpha = Math.min(1, p.life * 2); g.fillStyle = p.col; g.fillRect(p.x, p.y, p.s, p.s); } g.globalAlpha = 1; }
  const floats = [];
  function floatTxt(s, x, y, col = '#ffd870') { floats.push({ s, x, y, life: 1.4, col }); }
  function drawFloats(g, dt) { for (let i = floats.length - 1; i >= 0; i--) { const f = floats[i]; f.life -= dt; f.y -= 40 * dt; if (f.life <= 0) { floats.splice(i, 1); continue; } g.globalAlpha = Math.min(1, f.life); txt(g, f.s, f.x, f.y, 26, f.col); } g.globalAlpha = 1; }

  /* ================= 1. WAGA KUPIECKA ================= */
  function waga(done) {
    const labels = []; while (labels.length < 3) { const v = 4 + Math.floor(Math.random() * 8); if (!labels.includes(v)) labels.push(v); }
    const secret = Math.floor(Math.random() * 3);
    const sacks = labels.map((l, i) => ({ label: l, real: i === secret ? l + 3 : l, x: 190 + i * 150, y: 545, measured: null }));
    const weights = [1, 2, 4, 8].map((v, i) => ({ v, x: 830 + i * 90, y: 560, on: false }));
    let cur = null, ang = 0, mistakes = 0, finished = false, msg = 'Kliknij worek, aby położyć go na lewej szali.';
    const panelEl = panel(`<div class="mgbar"><div class="mgtxt"><b>Waga kupiecka</b> — połóż worek na lewej szali, a odważniki (w grzywnach) na prawej, aż waga się wyrówna. Znajdź worek, który waży INACZEJ, niż na nim napisano.</div><div class="mgbtns"><button id="wgCut" class="btn" disabled>Rozetnij wybrany worek</button><button id="wgQuit" class="btn ghost">Odejdź</button></div></div>`);
    $('#wgQuit').onclick = () => end(false, true);
    $('#wgCut').onclick = () => { if (!cur) return; if (cur.real !== cur.label) { finished = true; Snd.sfx('fanfare'); burst(640, 300, '#ffd870', 60); msg = 'W worku błyszczy złota pieczęć!'; setTimeout(() => end(true), 1600); } else { mistakes++; Snd.sfx('bad'); msg = 'Tylko sól… Ten worek waży tyle, ile napisano. Szukaj dalej!'; cur.measured = cur.real; } };
    function sumR() { return weights.filter(w => w.on).reduce((a, w) => a + w.v, 0); }
    function end(win, quit) { hidePanel(); done(win, { mistakes, quit }); }
    return {
      draw(g, dt, T) {
        g.drawImage(Art.bg('rynek'), 0, 0); g.fillStyle = 'rgba(0,0,0,.45)'; g.fillRect(0, 0, W, H);
        const L = cur ? cur.real : 0, Rr = sumR(); const target = Math.max(-0.35, Math.min(0.35, (Rr - L) * 0.05)); ang += (target - ang) * Math.min(1, dt * 5);
        const cx = 640, cy = 220;
        g.fillStyle = '#3a2a1a'; g.fillRect(cx - 8, cy, 16, 280); g.fillRect(cx - 80, 495, 160, 16);
        g.save(); g.translate(cx, cy); g.rotate(ang); g.fillStyle = '#6a4a24'; g.fillRect(-260, -6, 520, 12); g.fillStyle = '#c9a24a'; g.beginPath(); g.arc(0, 0, 12, 0, TAU); g.fill(); g.restore();
        const lx = cx - Math.cos(ang) * 250, ly = cy - Math.sin(ang) * 250, rx = cx + Math.cos(ang) * 250, ry = cy + Math.sin(ang) * 250;
        [[lx, ly], [rx, ry]].forEach(([px, py]) => { g.strokeStyle = '#8a7a5a'; g.lineWidth = 2; g.beginPath(); g.moveTo(px, py); g.lineTo(px - 60, py + 110); g.moveTo(px, py); g.lineTo(px + 60, py + 110); g.stroke(); g.fillStyle = '#8a6a3a'; g.beginPath(); g.ellipse(px, py + 112, 70, 12, 0, 0, TAU); g.fill(); });
        if (cur) drawSack(g, lx, ly + 72, cur, true);
        let ox = -45; weights.filter(w => w.on).forEach(w => { drawWeight(g, rx + ox, ry + 104, w.v); ox += 30; });
        const bal = cur && L === Rr;
        txt(g, cur ? (bal ? `RÓWNOWAGA: ${L} grzywien` : (Rr > L ? 'Odważniki są cięższe' : 'Worek jest cięższy')) : 'Lewa szala pusta', 640, 140, 24, bal ? '#9af0a0' : '#f0e2c0');
        if (bal && cur.measured === null) { cur.measured = L; Snd.sfx('good'); if (L !== cur.label) msg = `Worek z napisem „${cur.label}” waży ${L} grzywien! Coś w nim jest… Rozetnij go!`; else msg = 'Ten worek waży tyle, ile napisano. Sprawdź następny.'; }
        $('#wgCut').disabled = !cur || finished;
        sacks.forEach(s => { if (s !== cur) drawSack(g, s.x, s.y, s, false); });
        weights.forEach(w => { if (!w.on) drawWeight(g, w.x, w.y, w.v, true); });
        plate(g, 160, 40, 960, 54); txt(g, msg, 640, 75, 20, '#f0e2c0', 'center', 'Spectral, Georgia, serif');
        txt(g, '1 grzywna ≈ 200 g srebra', 980, 600, 16, '#c9a24a');
        drawParts(g, dt);
      },
      click(x, y) {
        if (finished) return;
        for (const s of sacks) if (Math.hypot(x - s.x, y - s.y + 30) < 55 && s !== cur) { cur = s; weights.forEach(w => w.on = false); Snd.sfx('hit'); msg = `Worek z napisem „${s.label} grzywien” na szali. Dokładaj odważniki.`; return; }
        for (const w of weights) { if (!w.on && Math.hypot(x - w.x, y - w.y + 20) < 34) { if (!cur) { msg = 'Najpierw połóż worek na lewej szali.'; return; } w.on = true; Snd.sfx('coin'); return; } }
        if (x > 830 && y < 470 && y > 230) { const on = weights.filter(w => w.on); if (on.length) { on[on.length - 1].on = false; Snd.sfx('click'); } }
      },
      onExit() { hidePanel(); }, _sacks: sacks,
    };
    function drawSack(g, x, y, s, onPan) {
      g.fillStyle = '#8a7048'; g.beginPath(); g.moveTo(x - 40, y); g.quadraticCurveTo(x - 50, y - 60, x - 18, y - 74); g.lineTo(x + 18, y - 74); g.quadraticCurveTo(x + 50, y - 60, x + 40, y); g.closePath(); g.fill();
      g.fillStyle = '#6a5030'; g.fillRect(x - 20, y - 84, 40, 12); g.strokeStyle = '#3a2a14'; g.lineWidth = 2; g.stroke();
      txt(g, String(s.label), x, y - 28, 26, '#2a1a0a', 'center', 'Georgia, serif');
      if (s.measured !== null) txt(g, s.measured === s.label ? '✓' : '!', x + 34, y - 64, 22, s.measured === s.label ? '#9af0a0' : '#ff8a6a');
      if (!onPan && cur === s) { g.strokeStyle = '#ffd870'; g.strokeRect(x - 46, y - 90, 92, 96); }
    }
    function drawWeight(g, x, y, v, label) { const w = 16 + v * 2.2, h = 14 + v * 2.2; g.fillStyle = '#4a4a50'; g.beginPath(); g.moveTo(x - w / 2, y); g.lineTo(x - w / 2 + 4, y - h); g.lineTo(x + w / 2 - 4, y - h); g.lineTo(x + w / 2, y); g.closePath(); g.fill(); g.fillStyle = '#6a6a70'; g.fillRect(x - 5, y - h - 6, 10, 6); txt(g, String(v), x, y - 4, 13, '#f0e2c0', 'center', 'Georgia'); }
  }

  /* ================= 2. GONITWA ================= */
  function joust(done, bonus) {
    let pass = 0, pPts = 0, ePts = 0, phase = 'intro', t = 0, aimT = 0, aimLock = null, strikeRes = null, res = '', resT = 0, broken = [false, false];
    const zones = () => ({ helm: 0.07 + bonus * 0.01, shield: 0.2 + bonus * 0.03, window: 0.09 + bonus * 0.015 });
    const DUR = 3.2;
    panel(`<div class="mgbar"><div class="mgtxt"><b>Gonitwa — 3 przejazdy</b>. 1) Gdy celownik jest na <b>hełmie</b> (2 pkt) lub <b>tarczy</b> (1 pkt) — kliknij lub naciśnij SPACJĘ. 2) Gdy rycerze się zbliżą i pasek trafi w <b>złote pole</b> — kliknij ponownie, by uderzyć. Hełm + idealne uderzenie = rywal spada z konia!</div><div class="mgbtns"><span id="jsc"></span><button id="jQuit" class="btn ghost">Poddaj się</button></div></div>`);
    $('#jQuit').onclick = () => { hidePanel(); done(false); };
    Snd.music('joust');
    function startPass() { pass++; phase = 'aim'; t = 0; aimLock = null; strikeRes = null; broken = [false, false]; Snd.sfx('gallop'); }
    function input() {
      if (phase === 'intro' || phase === 'result') { if (phase === 'result' && resT < 0.8) return; if (checkEnd()) return; startPass(); return; }
      if (phase === 'aim') { const z = zones(); const pos = Math.sin(aimT * 3.1) * 0.5 + 0.5; const d = Math.abs(pos - 0.25); aimLock = d < z.helm ? 'helm' : (Math.abs(pos - 0.62) < z.shield ? 'tarcza' : 'pudło'); phase = 'strike'; Snd.sfx('click'); return; }
      if (phase === 'strike') { resolve(t); }
    }
    function resolve(tt) {
      const z = zones(); const k = tt / DUR; const d = Math.abs(k - 0.82);
      const timing = d < z.window * 0.35 ? 'idealnie' : (d < z.window ? 'dobrze' : (k < 0.82 ? 'za wcześnie' : 'za późno'));
      let p = 0, txtR = '';
      if (aimLock === 'pudło' || timing === 'za wcześnie' || timing === 'za późno') txtR = `Pudło! (${aimLock === 'pudło' ? 'zły cel' : timing})`;
      else if (aimLock === 'helm' && timing === 'idealnie') { p = 99; txtR = 'TRAFIENIE W HEŁM! Rycerz Kruka spada z siodła!'; }
      else if (aimLock === 'helm') { p = 2; txtR = 'Trafienie w hełm! Kopia pęka! +2'; }
      else { p = timing === 'idealnie' ? 2 : 1; txtR = `Trafienie w tarczę (${timing})! Kopia pęka! +${p}`; }
      if (p) { broken[0] = true; Snd.sfx('clash'); burst(640, 330, '#e8d8b0', 40); } else Snd.sfx('whoosh');
      // przeciwnik
      const r = Math.random(); let e = 0;
      const def = G.defense();
      if (r < 0.05 && !G.S().eq.shield) { e = 99; } else if (r < 0.22 - def * 0.02) e = 2; else if (r < 0.58 - def * 0.05) e = 1;
      if (e) { broken[1] = true; setTimeout(() => Snd.sfx('hit'), 120); }
      const eTxt = e === 99 ? 'Kruk trafił cię w hełm — spadasz z konia!' : e ? `Kruk trafia w twoją tarczę: +${e} dla niego` : 'Kopia Kruka ześlizguje się po twojej zbroi.';
      if (p === 99) pPts = 99; else pPts += p; if (e === 99 && p !== 99) ePts = 99; else if (e !== 99) ePts += e;
      res = txtR + '\n' + eTxt; phase = 'result'; resT = 0; t = tt;
      if (p) Snd.sfx('crowd');
    }
    function checkEnd() {
      if (pPts >= 99 || ePts >= 99 || (pass >= 3 && pPts !== ePts)) { const win = pPts >= 99 || (ePts < 99 && pPts > ePts); phase = 'end'; setTimeout(() => { hidePanel(); done(win); }, 300); return true; }
      return false;
    }
    return {
      draw(g, dt, T) {
        g.drawImage(Art.bg('turniej'), 0, 0);
        if (phase === 'aim' || phase === 'strike') { t += dt; aimT += dt; if (phase === 'aim' && t > DUR * 0.62) { aimLock = 'pudło'; phase = 'strike'; } if (t > DUR) resolve(DUR + 1); }
        if (phase === 'result') resT += dt;
        const k = (phase === 'aim' || phase === 'strike') ? t / DUR : (phase === 'result' ? Math.min(1.2, t / DUR + resT * 0.25) : 0);
        const px = 80 + k * 640, ex = 1200 - k * 640;
        Art.drawRider(g, ex, 540, 1.05, { dir: -1, cap1: '#1a1620', cap2: '#4a2a5a', armor: '#24202a', plume: '#2a2a2a', broken: broken[1] }, T);
        Art.drawRider(g, px, 600, 1.15, { dir: 1, cap1: '#c9a032', cap2: '#8e1816', armor: '#1c1e24', arms: true, plume: '#8e1816', broken: broken[0] }, T + 0.3);
        // celownik
        if (phase === 'aim' || phase === 'strike') {
          const z = zones(); plate(g, 1040, 110, 200, 300);
          g.save(); g.translate(1140, 160);
          g.fillStyle = '#24202a'; g.beginPath(); g.moveTo(-28, 0); g.lineTo(-30, -40); g.quadraticCurveTo(0, -56, 30, -40); g.lineTo(28, 0); g.fill(); g.fillStyle = '#000'; g.fillRect(-20, -28, 40, 4);
          g.fillStyle = '#4a2a5a'; g.beginPath(); g.moveTo(-50, 30); g.lineTo(50, 30); g.lineTo(50, 120); g.quadraticCurveTo(50, 200, 0, 220); g.quadraticCurveTo(-50, 200, -50, 120); g.fill(); Art.raven(g, 0, 110, 1.6, 1.2, '#000');
          const top = -56, span = 290; const yHelm = top + span * 0.25, yShield = top + span * 0.62;
          g.fillStyle = 'rgba(255,216,112,.25)'; g.fillRect(-90, yHelm - span * z.helm, 180, span * z.helm * 2);
          g.fillStyle = 'rgba(154,240,160,.15)'; g.fillRect(-90, yShield - span * z.shield, 180, span * z.shield * 2);
          const pos = aimLock ? null : Math.sin(aimT * 3.1) * 0.5 + 0.5;
          if (pos !== null) { const yy = top + span * pos; g.strokeStyle = '#ff5a3a'; g.lineWidth = 3; g.beginPath(); g.moveTo(-90, yy); g.lineTo(90, yy); g.stroke(); g.beginPath(); g.arc(0, yy, 12, 0, TAU); g.stroke(); }
          g.restore();
          txt(g, aimLock ? `Cel: ${aimLock.toUpperCase()}` : 'CELUJ!', 1140, 440, 22, aimLock ? '#ffd870' : '#ff8a6a');
          if (phase === 'strike') { plate(g, 340, 70, 600, 46); const z2 = zones(); const wx = 350 + 580 * 0.82; g.fillStyle = 'rgba(255,216,112,.35)'; g.fillRect(wx - 580 * z2.window, 76, 580 * z2.window * 2, 34); g.fillStyle = 'rgba(255,216,112,.8)'; g.fillRect(wx - 580 * z2.window * 0.35, 76, 580 * z2.window * 0.7, 34); g.fillStyle = '#fff'; g.fillRect(350 + 580 * Math.min(1, t / DUR) - 2, 72, 4, 42); txt(g, 'UDERZ!', 640, 150, 26, '#ffd870'); }
        }
        txt(g, `Przejazd ${Math.max(1, pass)}/3`, 640, 44, 28, '#f0e2c0');
        txt(g, `Zawisza: ${pPts >= 99 ? 'ZWYCIĘSTWO' : pPts}`, 200, 44, 24, '#ffd870'); txt(g, `Rycerz Kruka: ${ePts >= 99 ? 'ZWYCIĘSTWO' : ePts}`, 1080, 44, 24, '#c8a8e8');
        if (phase === 'intro') { plate(g, 300, 230, 680, 150, 0.85); txt(g, 'Herold unosi chorągiew…', 640, 280, 30); txt(g, 'Kliknij lub naciśnij SPACJĘ, by ruszyć', 640, 330, 22, '#c9a24a', 'center', 'Spectral, Georgia'); }
        if (phase === 'result') { plate(g, 240, 200, 800, 130, 0.85); res.split('\n').forEach((l, i) => txt(g, l, 640, 248 + i * 40, 22, i ? '#c8a8e8' : '#ffd870', 'center', 'Spectral, Georgia')); if (resT > 0.8) txt(g, 'Kliknij, by kontynuować', 640, 316, 16, '#c9a24a', 'center', 'Spectral, Georgia'); }
        drawParts(g, dt);
        const sc = $('#jsc'); if (sc) sc.textContent = `Premia sprzętu i treningu: +${bonus}`;
      },
      click() { input(); }, key(k) { if (k === ' ' || k === 'Enter') input(); },
      onExit() { hidePanel(); },
    };
  }

  /* ================= 3. ZAMEK DZIEJÓW ================= */
  function timeline(done) {
    const EV = [
      { yr: 966, t: 'Chrzest Mieszka I' }, { yr: 1000, t: 'Zjazd gnieźnieński — Otton III daje Chrobremu Włócznię' },
      { yr: 1257, t: 'Lokacja Krakowa na prawie magdeburskim' }, { yr: 1320, t: 'Koronacja Łokietka na Wawelu' },
      { yr: 1364, t: 'Kazimierz Wielki zakłada Akademię' }, { yr: 1385, t: 'Unia w Krewie' }, { yr: 1400, t: 'Jagiełło odnawia Akademię' }];
    const cards = EV.map(e => Object.assign({}, e)).sort(() => Math.random() - 0.5);
    cards.forEach((c, i) => { c.x = 70 + (i % 4) * 290; c.y = 380 + Math.floor(i / 4) * 140; c.placed = false; c.shake = 0; });
    let next = 0, mistakes = 0, over = false, hint = 'Klikaj karty od NAJWCZEŚNIEJSZEGO wydarzenia do najpóźniejszego.';
    panel(`<div class="mgbar"><div class="mgtxt"><b>Zamek dziejów</b> — ułóż wydarzenia w kolejności, w jakiej się wydarzyły. Każda dobra karta przekręca jeden bolec zamka.</div><div class="mgbtns"><button id="tlQuit" class="btn ghost">Odejdź</button></div></div>`);
    $('#tlQuit').onclick = () => { hidePanel(); done(false, { quit: true }); };
    return {
      draw(g, dt, T) {
        g.drawImage(Art.bg('akademia'), 0, 0); g.fillStyle = 'rgba(0,0,0,.55)'; g.fillRect(0, 0, W, H);
        // skrzynia
        g.fillStyle = '#3a2210'; g.fillRect(500, 150, 280, 130); g.fillStyle = '#5a3a1a'; g.fillRect(490, 120, 300, 40); g.strokeStyle = '#c9a24a'; g.lineWidth = 4; g.strokeRect(500, 150, 280, 130);
        for (let i = 0; i < EV.length; i++) { const on = i < next; g.fillStyle = on ? '#ffd870' : '#2a1a10'; g.beginPath(); g.arc(560 + i * 27, 215, 9, 0, TAU); g.fill(); g.strokeStyle = '#c9a24a'; g.lineWidth = 2; g.stroke(); }
        // oś
        g.strokeStyle = '#c9a24a'; g.lineWidth = 3; g.beginPath(); g.moveTo(60, 320); g.lineTo(1220, 320); g.stroke();
        EV.forEach((e, i) => { const x = 110 + i * 175; g.fillStyle = '#c9a24a'; g.beginPath(); g.arc(x, 320, 6, 0, TAU); g.fill(); if (i < next) { txt(g, String(e.yr), x, 306, 22, '#ffd870'); } });
        plate(g, 160, 40, 960, 54); txt(g, hint, 640, 75, 20, '#f0e2c0', 'center', 'Spectral, Georgia, serif');
        cards.forEach(c => {
          if (c.placed) return; c.shake = Math.max(0, c.shake - dt * 3);
          const ox = Math.sin(c.shake * 40) * 8 * c.shake;
          g.fillStyle = '#e8dcbc'; g.fillRect(c.x + ox, c.y, 260, 110); g.strokeStyle = '#6a4a20'; g.lineWidth = 3; g.strokeRect(c.x + ox, c.y, 260, 110);
          g.fillStyle = '#2a1a0a'; g.font = '19px Spectral, Georgia'; g.textAlign = 'left';
          wrap(g, c.t, c.x + 14 + ox, c.y + 34, 232, 24);
        });
        drawParts(g, dt);
      },
      click(x, y) {
        if (over) return;
        for (const c of cards) if (!c.placed && x > c.x && x < c.x + 260 && y > c.y && y < c.y + 110) {
          if (c.yr === EV[next].yr) {
            c.placed = true; next++; Snd.sfx('good'); burst(110 + (next - 1) * 175, 320, '#ffd870', 16, 160); hint = `${c.yr} — ${c.t}`;
            if (next === EV.length) { over = true; Snd.sfx('fanfare'); hint = 'Zamek szczęka — skrzynia otwarta!'; burst(640, 200, '#ffd870', 60); setTimeout(() => { hidePanel(); done(true, { mistakes }); }, 1500); }
          } else { c.shake = 1; mistakes++; Snd.sfx('bad'); hint = 'Zamek zgrzyta… To wydarzenie było później. Szukaj wcześniejszego!'; }
          return;
        }
      },
      onExit() { hidePanel(); },
    };
  }
  function wrap(g, s, x, y, w, lh) { const words = s.split(' '); let line = ''; for (const wd of words) { const tst = line + wd + ' '; if (g.measureText(tst).width > w && line) { g.fillText(line, x, y); line = wd + ' '; y += lh; } else line = tst; } g.fillText(line, x, y); }

  /* ================= 4. HEJNAŁ ================= */
  function hejnal(done) {
    const NOTES = ['F4', 'A4', 'C5', 'D5', 'F5'];
    const COLS = ['#c9a24a', '#8e1816', '#2a6a9a', '#3a8a4a', '#9a5ac0'];
    const seq = []; for (let i = 0; i < 7; i++) seq.push(Math.floor(Math.random() * 5));
    let lastK = -1, len = 3, phase = 'intro', idx = 0, showT = 0, lit = -1, litT = 0, lives = 3, msg = 'Kliknij, aby Wojciech zagrał pierwszą frazę.', ravens = [];
    for (let i = 0; i < 18; i++) ravens.push({ x: 300 + Math.random() * 300, y: 60 + Math.random() * 300, a: Math.random() * TAU, r: 30 + Math.random() * 80, s: 0.6 + Math.random() * 0.6 });
    panel(`<div class="mgbar"><div class="mgtxt"><b>Hejnał</b> — posłuchaj dźwięków trąbki i zapamiętaj, które okna wieży się zapalają. Potem powtórz je, klikając okna (lub klawisze 1–5). Fraz: 3, coraz dłuższych.</div><div class="mgbtns"><span id="hjl"></span><button id="hjQuit" class="btn ghost">Odejdź</button></div></div>`);
    $('#hjQuit').onclick = () => { hidePanel(); done(false, { quit: true }); };
    const win = i => ({ x: 760 + i * 92, y: 470 });
    function play(i) { lit = i; litT = 0.45; Snd.sfx('trumpet', NOTES[i]); }
    function input(i) {
      if (phase !== 'input') return; play(i);
      if (i === seq[idx]) { idx++; if (idx >= len) { if (len >= 5) { phase = 'win'; msg = 'Hejnał rozbrzmiewa nad Krakowem! Kruki uciekają!'; setTimeout(() => Snd.sfx('hejnal'), 500); ravens.forEach(r => r.flee = true); setTimeout(() => { hidePanel(); done(true, { lives }); }, 4200); } else { phase = 'wait'; msg = 'Dobrze! Następna fraza będzie dłuższa…'; setTimeout(() => { len++; startShow(); }, 1100); } } }
      else { lives--; Snd.sfx('raven'); msg = lives > 0 ? `Fałszywa nuta! Kruki skrzeczą. (pozostało prób: ${lives}) Posłuchaj jeszcze raz.` : 'Kruki rzucają się na wieżę! Musisz się wycofać.'; phase = 'wait'; ravens.forEach(r => r.r *= 0.7); if (lives <= 0) setTimeout(() => { hidePanel(); done(false); }, 1800); else setTimeout(startShow, 1400); }
    }
    function startShow() { phase = 'show'; idx = 0; showT = -0.4; lastK = -1; msg = 'Słuchaj…'; }
    return {
      draw(g, dt, T) {
        g.drawImage(Art.bg('mariacki'), 0, 0);
        ravens.forEach(r => { r.a += dt * (r.flee ? 2 : 1.2); if (r.flee) { r.x += dt * 300; r.y -= dt * 160; } Art.raven(g, r.x + Math.cos(r.a) * r.r, r.y + Math.sin(r.a) * r.r * 0.4, r.s, T * 10 + r.a); });
        if (phase === 'show') { showT += dt; const k = Math.floor(showT / 0.7); if (showT > 0 && k < len && k !== lastK) { lastK = k; play(seq[k]); } if (k >= len) { phase = 'input'; idx = 0; msg = 'Teraz ty! Powtórz melodię.'; } }
        litT -= dt; if (litT <= 0) lit = -1;
        plate(g, 720, 380, 480, 180, 0.8);
        for (let i = 0; i < 5; i++) { const p = win(i); const on = lit === i; g.fillStyle = on ? COLS[i] : '#1a1214'; g.beginPath(); g.moveTo(p.x - 30, p.y + 50); g.lineTo(p.x - 30, p.y - 20); g.quadraticCurveTo(p.x, p.y - 64, p.x + 30, p.y - 20); g.lineTo(p.x + 30, p.y + 50); g.closePath(); g.fill(); g.strokeStyle = COLS[i]; g.lineWidth = 3; g.stroke(); if (on) { g.save(); g.globalCompositeOperation = 'lighter'; Art.glow(g, p.x, p.y, 90, COLS[i], 0.5); g.restore(); } txt(g, String(i + 1), p.x, p.y + 76, 18, '#c9a24a'); }
        plate(g, 160, 40, 960, 54); txt(g, msg, 640, 75, 20, '#f0e2c0', 'center', 'Spectral, Georgia, serif');
        txt(g, `Fraza ${len - 2}/3`, 960, 420, 22, '#ffd870');
        const l = $('#hjl'); if (l) l.textContent = 'Próby: ' + '♥'.repeat(Math.max(0, lives));
        if (phase === 'intro') { plate(g, 760, 180, 420, 80, 0.85); txt(g, 'Kliknij, by zacząć', 970, 230, 26); }
      },
      click(x, y) { if (phase === 'intro') { startShow(); return; } for (let i = 0; i < 5; i++) { const p = win(i); if (Math.abs(x - p.x) < 34 && y > p.y - 60 && y < p.y + 54) input(i); } },
      key(k) { const n = parseInt(k); if (n >= 1 && n <= 5) input(n - 1); if (phase === 'intro' && (k === ' ' || k === 'Enter')) startShow(); },
      onExit() { hidePanel(); },
    };
  }

  /* ================= 5. BITWA W SMOCZEJ JAMIE ================= */
  function battle(done) {
    const S = G.S(); const COLS = 8, LANES = 3, X0 = 150, CW = 132, Y0 = 330, LH = 120;
    const mrokBonus = S.mrok >= 60 ? 1 : 0;
    const honorBonus = S.honor >= 30 ? 1 : 0;
    const orders = Math.min(4, 2 + Math.floor(S.wiedza / 20));
    const res = { piechur: S.army.piechur, kusznik: S.army.kusznik, rycerz: S.army.rycerz };
    const STAT = {
      piechur: { hp: 6, atk: 2, rng: 1, max: 6 }, kusznik: { hp: 4, atk: 2, rng: 3, max: 2 }, rycerz: { hp: 10, atk: 3, rng: 1, max: 6 },
      zawisza: { hp: 14 + G.defense() * 3, atk: 3 + G.attack(), rng: 1, max: 6 },
      najemnik: { hp: 5, atk: 2, rng: 1 }, wrogkusznik: { hp: 3, atk: 2, rng: 3, min: 5 }, czarnyrycerz: { hp: 9, atk: 3, rng: 1 }, komtur: { hp: 22, atk: 4, rng: 1 },
    };
    const units = []; let uid = 0;
    function add(type, side, lane, col) { const st = STAT[type]; const u = { id: uid++, type, side, lane, col, hp: st.hp, maxhp: st.hp, atk: st.atk + (side === 'p' ? honorBonus : mrokBonus), rng: st.rng, dx: X0 + col * CW, hit: 0, dead: false }; units.push(u); return u; }
    const hero = add('zawisza', 'p', 1, 1); hero.atk = STAT.zawisza.atk + honorBonus;
    const WAVES = { 1: [['najemnik', 0], ['najemnik', 2]], 2: [['najemnik', 1]], 3: [['wrogkusznik', 0], ['najemnik', 2]], 5: [['czarnyrycerz', 1], ['najemnik', 0], ['najemnik', 2]], 7: [['wrogkusznik', 2], ['czarnyrycerz', 0], ['najemnik', 1]], 9: [['komtur', 1], ['czarnyrycerz', 0], ['czarnyrycerz', 2]] };
    let turn = 0, ord = orders, sel = null, gate = 12, busy = false, log = 'Twoja tura. Wybierz jednostkę z odwodu i kliknij tor (rząd), by ją wystawić.', over = false, strikeUsed = false, komturSeen = false;
    const queue = [];
    function spawn() { (WAVES[turn] || []).forEach(w => queue.push(w)); for (let i = 0; i < queue.length; i++) { const [t, l] = queue[i]; if (at(l, 7)) continue; add(t, 'e', l, 7); queue.splice(i--, 1); if (t === 'komtur') { komturSeen = true; Snd.sfx('dark'); } } }
    function at(l, c) { return units.find(u => !u.dead && u.lane === l && u.col === c); }
    function ui() {
      const p = panel(`<div class="mgbar battle">
        <div class="bres">${['piechur', 'kusznik', 'rycerz'].map(k => `<button class="btn unit ${sel === k ? 'sel' : ''}" data-u="${k}" ${res[k] && ord && !busy ? '' : 'disabled'}>${D.ARMY[k].name}<small>odwód: ${res[k]} · ${STAT[k].hp}♥ ${STAT[k].atk}⚔ zasięg ${STAT[k].rng}</small></button>`).join('')}</div>
        <div class="bres">
          <button class="btn" id="bStrike" ${ord && !strikeUsed && !busy ? '' : 'disabled'}>Cios Zawiszy<small>2× obrażenia, zasięg 2 (1 rozkaz)</small></button>
          <button class="btn" id="bUp" ${ord && !busy && hero.lane > 0 && !at(hero.lane - 1, hero.col) ? '' : 'disabled'}>Zawisza ▲<small>zmień tor (1 rozkaz)</small></button>
          <button class="btn" id="bDown" ${ord && !busy && hero.lane < 2 && !at(hero.lane + 1, hero.col) ? '' : 'disabled'}>Zawisza ▼<small>zmień tor (1 rozkaz)</small></button>
          <button class="btn" id="bHeal" ${G.has('ziola') && !busy ? '' : 'disabled'}>Zioła<small>+8♥ Zawiszy (bez rozkazu)</small></button>
          <button class="btn gold" id="bEnd" ${busy ? 'disabled' : ''}>Koniec tury ▸</button>
        </div></div>`);
      p.querySelectorAll('[data-u]').forEach(b => b.onclick = () => { sel = sel === b.dataset.u ? null : b.dataset.u; Snd.sfx('click'); ui(); });
      $('#bEnd').onclick = endTurn;
      $('#bStrike').onclick = () => { const tg = units.filter(u => !u.dead && u.side === 'e' && u.lane === hero.lane && u.col > hero.col && u.col - hero.col <= 2).sort((a, b) => a.col - b.col)[0]; if (!tg) { log = 'Brak wroga w zasięgu 2 pól przed Zawiszą.'; return; } ord--; strikeUsed = true; dmg(tg, hero.atk * 2, hero); Snd.sfx('clash'); log = 'Cios Zawiszy! Miecz tnie ciemność.'; ui(); };
      $('#bUp').onclick = () => { ord--; hero.lane--; Snd.sfx('whoosh'); ui(); };
      $('#bDown').onclick = () => { ord--; hero.lane++; Snd.sfx('whoosh'); ui(); };
      $('#bHeal').onclick = () => { G.take('ziola'); hero.hp = Math.min(hero.maxhp, hero.hp + 8); Snd.sfx('heal'); floatTxt('+8', hero.dx, Y0 + hero.lane * LH - 70, '#9af0a0'); ui(); };
    }
    function dmg(u, n, src) { u.hp -= n; u.hit = 0.3; floatTxt('-' + n, u.dx, Y0 + u.lane * LH - 70, u.side === 'p' ? '#ff8a6a' : '#ffd870'); burst(u.dx, Y0 + u.lane * LH - 30, u.side === 'p' ? '#c03020' : '#6af0b0', 10, 140); if (u.hp <= 0) { u.dead = true; if (u.type === 'komtur') win(); if (u === hero) lose('Zawisza pada na kolana…'); } }
    function act(u) {
      if (u.dead || over) return;
      const dir = u.side === 'p' ? 1 : -1;
      let target = null; for (let r = 1; r <= u.rng; r++) { const o = at(u.lane, u.col + dir * r); if (o && o.side !== u.side) { target = o; break; } if (o && o.side === u.side && u.rng === 1) break; }
      if (target) { dmg(target, u.atk, u); Snd.sfx(u.rng > 1 ? 'whoosh' : 'hit'); return; }
      const nc = u.col + dir; const st = STAT[u.type];
      if (u.side === 'p' && nc > st.max) return; if (u.side === 'e' && st.min && u.col <= st.min) return;
      if (u.side === 'e' && nc < 0) { gate -= u.atk + 1; u.dead = true; Snd.sfx('hit'); floatTxt(`Brama −${u.atk + 1}`, 90, Y0 + u.lane * LH - 60, '#ff8a6a'); if (gate <= 0) lose('Ludzie Komtura przedarli się przez wasze szeregi!'); return; }
      if (nc > 7) return;
      if (!at(u.lane, nc)) u.col = nc;
    }
    function endTurn() {
      if (busy || over) return; busy = true; sel = null; ui();
      const pq = units.filter(u => !u.dead && u.side === 'p').sort((a, b) => b.col - a.col);
      const eq = () => units.filter(u => !u.dead && u.side === 'e').sort((a, b) => a.col - b.col);
      let i = 0; const steps = [...pq.map(u => () => act(u)), () => { eq().forEach((u, k) => setTimeout(() => act(u), k * 140)); }];
      const run = () => { if (over) return; if (i < steps.length) { steps[i++](); setTimeout(run, 170); } else setTimeout(() => { if (over) return; turn++; spawn(); ord = orders; strikeUsed = false; busy = false; log = turn >= 9 && komturSeen ? 'Komtur wyszedł z ciemności! Pokonaj go!' : `Tura ${turn}. Wróg nadciąga z głębi jaskini.`; if (turn > 9 && !queue.length && !units.some(u => !u.dead && u.side === 'e')) win(); ui(); }, 700); };
      run();
    }
    function win() { if (over) return; over = true; Snd.sfx('fanfare'); log = 'Czarny Komtur pada! Szczerbiec lśni w ciemności!'; setTimeout(() => { hidePanel(); done(true, { lost: lostCount() }); }, 2200); }
    function lose(why) { if (over) return; over = true; Snd.sfx('fail'); log = why; setTimeout(() => { hidePanel(); done(false); }, 2200); }
    function lostCount() { return units.filter(u => u.side === 'p' && u.dead && u !== hero).length; }
    turn = 1; spawn(); ui();
    Snd.music('battle');
    return {
      draw(g, dt, T) {
        g.drawImage(Art.bg('bitwa'), 0, 0);
        for (let l = 0; l < LANES; l++) for (let c = 0; c < COLS; c++) { const x = X0 + c * CW - CW / 2, y = Y0 + l * LH - LH + 20; g.fillStyle = (l + c) % 2 ? 'rgba(255,255,255,.04)' : 'rgba(0,0,0,.15)'; g.fillRect(x, y, CW, LH); if (sel && c === 0) { g.fillStyle = at(l, 0) ? 'rgba(255,80,60,.15)' : 'rgba(255,216,112,.18)'; g.fillRect(x, y, CW, LH); } }
        g.strokeStyle = 'rgba(201,162,74,.35)'; g.lineWidth = 1; for (let l = 0; l <= LANES; l++) { g.beginPath(); g.moveTo(X0 - CW / 2, Y0 + l * LH - LH + 20); g.lineTo(X0 + COLS * CW - CW / 2, Y0 + l * LH - LH + 20); g.stroke(); }
        // brama
        g.fillStyle = '#2a1a10'; g.fillRect(30, 230, 40, 380); g.strokeStyle = '#c9a24a'; g.strokeRect(30, 230, 40, 380); txt(g, 'Wyjście', 50, 222, 16, '#c9a24a');
        for (let i = 0; i < 12; i++) { g.fillStyle = i < gate ? '#c9a24a' : '#3a2a1a'; g.fillRect(36, 600 - i * 30, 28, 24); }
        units.filter(u => !u.dead).sort((a, b) => a.lane - b.lane).forEach(u => {
          const tx = X0 + u.col * CW; u.dx += (tx - u.dx) * Math.min(1, dt * 8); u.hit = Math.max(0, u.hit - dt);
          const y = Y0 + u.lane * LH;
          Art.drawUnit(g, u.dx + (u.hit ? Math.sin(T * 60) * 3 : 0), y, 1.35, u.type, u.side === 'p' ? 1 : -1, T, u.hit > 0.15);
          const bw = 50; g.fillStyle = 'rgba(0,0,0,.6)'; g.fillRect(u.dx - bw / 2, y - 100, bw, 6); g.fillStyle = u.side === 'p' ? '#c9a24a' : '#6af0b0'; g.fillRect(u.dx - bw / 2, y - 100, bw * Math.max(0, u.hp / u.maxhp), 6);
          if (u === hero || u.type === 'komtur') txt(g, u === hero ? 'Zawisza' : 'Komtur', u.dx, y - 108, 14, u === hero ? '#ffd870' : '#6af0b0');
        });
        plate(g, 140, 16, 1000, 70); txt(g, log, 640, 46, 19, '#f0e2c0', 'center', 'Spectral, Georgia');
        txt(g, `Tura ${turn}   ·   Rozkazy: ${ord}/${orders}   ·   Brama: ${Math.max(0, gate)}`, 640, 74, 16, '#c9a24a', 'center', 'Spectral, Georgia');
        if (mrokBonus) txt(g, 'Mrok ≥ 60: wrogowie +1 ataku', 1120, 110, 14, '#6af0b0', 'right', 'Spectral, Georgia');
        if (honorBonus) txt(g, 'Honor ≥ 30: twoi ludzie +1 ataku', 160, 110, 14, '#ffd870', 'left', 'Spectral, Georgia');
        drawParts(g, dt); drawFloats(g, dt);
      },
      click(x, y) {
        if (!sel || busy || over) return;
        const l = Math.floor((y - (Y0 - LH + 20)) / LH); if (l < 0 || l > 2) return;
        if (at(l, 0)) { log = 'To pole jest zajęte. Wybierz inny tor.'; return; }
        add(sel, 'p', l, 0); res[sel]--; ord--; Snd.sfx('clash'); log = `${D.ARMY[sel].name} staje do walki!`; if (!res[sel] || !ord) sel = null; ui();
      },
      key(k) { if (k === 'Enter') endTurn(); },
      onExit() { hidePanel(); Snd.music('loc'); },
      result() { return units; },
    };
  }

  return { waga, joust, timeline, hejnal, battle };
})();
