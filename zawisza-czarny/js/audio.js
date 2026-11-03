'use strict';
/* =====================================================================
   AUDIO — wszystkie dźwięki i muzyka syntezowane w Web Audio API
   (bez plików zewnętrznych): lutnia, burdon, dzwony, trąbka hejnału,
   szczęk stali, kruki, galop, bębny bitewne.
   ===================================================================== */
const Snd = (() => {
  let ctx = null, master, musicBus, sfxBus, verb, on = true, mus = null, timer = null, drone = null;
  const NOTE = { C: 0, 'C#': 1, D: 2, 'D#': 3, Eb: 3, E: 4, F: 5, 'F#': 6, G: 7, 'G#': 8, A: 9, Bb: 10, B: 11 };
  function freq(n) { const m = n.match(/^([A-G][#b]?)(\d)$/); if (!m) return 0; const midi = (parseInt(m[2]) + 1) * 12 + NOTE[m[1]]; return 440 * Math.pow(2, (midi - 69) / 12); }
  function init() {
    if (ctx) { if (ctx.state === 'suspended') ctx.resume(); return; }
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
    ctx = new AC(); master = ctx.createGain(); master.gain.value = on ? 0.8 : 0; master.connect(ctx.destination);
    musicBus = ctx.createGain(); musicBus.gain.value = 0.32; musicBus.connect(master);
    sfxBus = ctx.createGain(); sfxBus.gain.value = 0.75; sfxBus.connect(master);
    verb = ctx.createConvolver(); const len = ctx.sampleRate * 2.6, b = ctx.createBuffer(2, len, ctx.sampleRate);
    for (let c = 0; c < 2; c++) { const d = b.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.6); }
    verb.buffer = b; const vg = ctx.createGain(); vg.gain.value = 0.35; verb.connect(vg); vg.connect(master);
  }
  let noiseBuf = null;
  function noise() { if (!noiseBuf) { noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate); const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; } const s = ctx.createBufferSource(); s.buffer = noiseBuf; return s; }
  function env(g, t, a, peak, dur, rel) { g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.setValueAtTime(peak, t + Math.max(a, dur - rel)); g.gain.exponentialRampToValueAtTime(0.0001, t + dur); }
  function tone(f, dur, o = {}) {
    if (!ctx) return; const t = o.when ?? ctx.currentTime;
    const osc = ctx.createOscillator(); osc.type = o.type || 'triangle'; osc.frequency.setValueAtTime(f, t);
    if (o.slide) osc.frequency.exponentialRampToValueAtTime(o.slide, t + dur);
    if (o.detune) osc.detune.value = o.detune;
    const g = ctx.createGain(); env(g, t, o.a ?? 0.005, o.vol ?? 0.2, dur, o.r ?? dur * 0.9);
    let node = osc;
    if (o.lp) { const f2 = ctx.createBiquadFilter(); f2.type = 'lowpass'; f2.frequency.value = o.lp; f2.Q.value = o.q ?? 0.7; node.connect(f2); node = f2; }
    if (o.bp) { const f2 = ctx.createBiquadFilter(); f2.type = 'bandpass'; f2.frequency.value = o.bp; f2.Q.value = o.q ?? 2; node.connect(f2); node = f2; }
    node.connect(g); g.connect(o.bus || sfxBus); if (o.rev) g.connect(verb);
    osc.start(t); osc.stop(t + dur + 0.05);
  }
  function nz(dur, o = {}) {
    if (!ctx) return; const t = o.when ?? ctx.currentTime; const s = noise(); const f = ctx.createBiquadFilter(); f.type = o.ft || 'bandpass'; f.frequency.setValueAtTime(o.f || 1000, t); if (o.fs) f.frequency.exponentialRampToValueAtTime(o.fs, t + dur); f.Q.value = o.q ?? 1;
    const g = ctx.createGain(); env(g, t, o.a ?? 0.003, o.vol ?? 0.2, dur, o.r ?? dur * 0.9);
    s.connect(f); f.connect(g); g.connect(o.bus || sfxBus); if (o.rev) g.connect(verb); s.start(t, Math.random()); s.stop(t + dur + 0.05);
  }
  /* --- instrumenty muzyczne --- */
  function lute(f, t, v = 0.16) { tone(f, 1.4, { when: t, type: 'triangle', vol: v, a: 0.004, r: 1.35, lp: 2200, bus: musicBus, rev: true }); tone(f * 2, 0.5, { when: t, type: 'sine', vol: v * 0.25, r: 0.48, bus: musicBus }); }
  function bassN(f, t, v = 0.12) { tone(f, 2.6, { when: t, type: 'sawtooth', vol: v, a: 0.3, r: 1.6, lp: 380, bus: musicBus, rev: true }); }
  function bell(f, t, v = 0.12) { [1, 2.76, 5.4, 0.5].forEach((m, i) => tone(f * m, 3.5 - i * 0.6, { when: t, type: 'sine', vol: v / (i + 1), a: 0.002, r: 3, bus: musicBus, rev: true })); }
  function horn(f, t, v = 0.14, d = 0.9) { tone(f, d, { when: t, type: 'sawtooth', vol: v, a: 0.05, r: 0.25, lp: 1600, q: 2, bus: musicBus, rev: true }); }
  function drum(t, v = 0.5, low = true) { tone(low ? 70 : 140, 0.35, { when: t, type: 'sine', vol: v, slide: low ? 40 : 90, r: 0.3, bus: musicBus }); nz(0.12, { when: t, f: 900, vol: v * 0.3, bus: musicBus }); }
  function voice(f, t, v = 0.05) { tone(f, 3, { when: t, type: 'sawtooth', vol: v, a: 0.8, r: 1.5, bp: 700, q: 4, bus: musicBus, rev: true }); tone(f * 1.005, 3, { when: t, type: 'sawtooth', vol: v, a: 0.8, r: 1.5, bp: 1100, q: 5, bus: musicBus, rev: true }); }

  const THEMES = {
    title: { bpm: 56, tracks: [
      { i: 'lute', s: 'D4 . . A3 . . D4 E4 F4 . . E4 D4 . . . C4 . . A3 . . C4 D4 E4 . . D4 C4 . A3 . D4 . . A3 . . D4 E4 F4 . G4 F4 E4 . D4 . C4 . E4 . D4 . C4 . A3 . . . . . . .' },
      { i: 'bass', s: 'D2 . . . . . . . . . . . . . . . C2 . . . . . . . . . . . . . . . Bb1 . . . . . . . . . . . . . . . A1 . . . . . . . . . . . . . . .' },
      { i: 'bell', s: 'D3 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .' },
      { i: 'voice', s: 'A3 . . . . . . . . . . . . . . . G3 . . . . . . . . . . . . . . . F3 . . . . . . . . . . . . . . . E3 . . . . . . . . . . . . . . .' }] },
    map: { bpm: 74, tracks: [
      { i: 'lute', s: 'D4 . F4 G4 A4 . . . G4 F4 E4 . D4 . . . C4 . D4 E4 F4 . E4 D4 C4 . A3 . . . . . D4 . F4 G4 A4 . C5 . A4 G4 F4 . G4 . . . A4 G4 F4 E4 D4 . C4 . D4 . . . . . . .' },
      { i: 'bass', s: 'D2 . . . . . . . . . . . . . . . C2 . . . . . . . . . . . . . . . F2 . . . . . . . . . . . . . . . A1 . . . . . . . D2 . . . . . . .' },
      { i: 'drumsoft', s: 'x . . . . . . . x . . . . . . . x . . . . . . . x . . . . . . .' }] },
    loc: { bpm: 60, tracks: [
      { i: 'lute', s: 'A3 . . . C4 . . . D4 . . . . . . . E4 . . . D4 . C4 . A3 . . . . . . . F3 . . . A3 . . . C4 . . . . . . . B3 . . . G3 . . . A3 . . . . . . .' },
      { i: 'bass', s: 'A1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . F1 . . . . . . . . . . . . . . . E1 . . . . . . . . . . . . . . .' },
      { i: 'voice', s: 'E3 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . C3 . . . . . . . . . . . . . . . B2 . . . . . . . . . . . . . . .' }] },
    battle: { bpm: 112, tracks: [
      { i: 'drum', s: 'x . x . X . . . x . x . X . x x x . x . X . . . x . x x X . X .' },
      { i: 'horn', s: 'D3 . . . D3 . F3 . E3 . . . C3 . . . D3 . . . D3 . F3 . A3 . G3 . F3 . E3 .' },
      { i: 'bass', s: 'D2 . . . . . . . C2 . . . . . . . Bb1 . . . . . . . A1 . . . . . . .' }] },
    joust: { bpm: 128, tracks: [
      { i: 'drum', s: 'x . . x x . . . x . . x X . . .' },
      { i: 'horn', s: 'D4 . A3 . D4 . F4 . E4 . D4 . A3 . . . D4 . A3 . D4 . F4 . G4 . F4 . E4 . D4 .' }] },
    end: { bpm: 80, tracks: [
      { i: 'lute', s: 'D4 . F#4 . A4 . . . G4 . F#4 . E4 . D4 . A4 . B4 . C5 . B4 . A4 . G4 . F#4 . . . G4 . A4 . B4 . A4 . G4 . F#4 . E4 . . . D4 . E4 . F#4 . E4 . D4 . . . . . . .' },
      { i: 'bass', s: 'D2 . . . . . . . . . . . . . . . A1 . . . . . . . . . . . . . . . G1 . . . . . . . . . . . . . . . A1 . . . . . . . D2 . . . . . . .' },
      { i: 'bell', s: 'D4 . . . . . . . . . . . . . . . A4 . . . . . . . . . . . . . . .' }] },
  };
  Object.values(THEMES).forEach(th => th.tracks.forEach(tr => tr.seq = tr.s.split(/\s+/)));
  function play(inst, tok, t) {
    if (tok === '.' || tok === '-') return;
    if (inst === 'drum') return drum(t, tok === 'X' ? 0.55 : 0.35, tok !== 'X');
    if (inst === 'drumsoft') return drum(t, 0.12, true);
    const f = freq(tok); if (!f) return;
    if (inst === 'lute') lute(f, t); else if (inst === 'bass') bassN(f, t); else if (inst === 'bell') bell(f, t); else if (inst === 'horn') horn(f, t); else if (inst === 'voice') voice(f, t);
  }
  function sched() {
    if (!mus || !ctx) return;
    const step = 60 / mus.th.bpm / 2;
    while (mus.next < ctx.currentTime + 0.3) {
      mus.th.tracks.forEach(tr => play(tr.i, tr.seq[mus.step % tr.seq.length], mus.next));
      mus.next += step; mus.step++;
    }
  }
  function music(name) {
    if (!ctx) { pending = name; return; }
    if (mus && mus.name === name) return;
    stopMusic(); const th = THEMES[name]; if (!th) return;
    mus = { name, th, step: 0, next: ctx.currentTime + 0.15 }; timer = setInterval(sched, 90);
    startDrone(name === 'battle' ? 73.4 : name === 'end' ? 73.4 : 55);
  }
  let pending = null;
  function startDrone(f) {
    stopDrone(); if (!ctx) return;
    const g = ctx.createGain(); g.gain.setValueAtTime(0.0001, ctx.currentTime); g.gain.exponentialRampToValueAtTime(0.05, ctx.currentTime + 3);
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 260;
    const o1 = ctx.createOscillator(), o2 = ctx.createOscillator(); o1.type = o2.type = 'sawtooth'; o1.frequency.value = f; o2.frequency.value = f * 1.5; o2.detune.value = 6;
    const lfo = ctx.createOscillator(), lg = ctx.createGain(); lfo.frequency.value = 0.07; lg.gain.value = 90; lfo.connect(lg); lg.connect(lp.frequency);
    o1.connect(lp); o2.connect(lp); lp.connect(g); g.connect(musicBus); o1.start(); o2.start(); lfo.start();
    // wiatr
    const w = noise(); w.loop = true; const wf = ctx.createBiquadFilter(); wf.type = 'bandpass'; wf.frequency.value = 500; wf.Q.value = 0.6; const wg = ctx.createGain(); wg.gain.value = 0.025;
    const l2 = ctx.createOscillator(), l2g = ctx.createGain(); l2.frequency.value = 0.11; l2g.gain.value = 300; l2.connect(l2g); l2g.connect(wf.frequency);
    w.connect(wf); wf.connect(wg); wg.connect(musicBus); w.start(); l2.start();
    drone = { g, nodes: [o1, o2, lfo, w, l2] };
  }
  function stopDrone() { if (!drone) return; const d = drone; drone = null; d.g.gain.setTargetAtTime(0.0001, ctx.currentTime, 0.5); setTimeout(() => d.nodes.forEach(n => { try { n.stop(); } catch (e) { } }), 2000); }
  function stopMusic() { if (timer) clearInterval(timer); timer = null; mus = null; stopDrone(); }

  /* --- efekty --- */
  const S = {
    click() { tone(660, 0.06, { type: 'square', vol: 0.05, lp: 2000 }); },
    page() { nz(0.25, { f: 3000, fs: 1200, vol: 0.12, q: 0.5 }); },
    coin() { tone(1320, 0.12, { type: 'square', vol: 0.06, lp: 4000 }); tone(1760, 0.3, { type: 'square', vol: 0.05, when: ctx.currentTime + 0.07, lp: 4000 }); },
    clash() { nz(0.3, { f: 3500, vol: 0.35, q: 3, rev: true }); [1870, 2630, 3410].forEach(f => tone(f, 0.6, { type: 'sine', vol: 0.06, r: 0.55, rev: true })); },
    hit() { nz(0.18, { f: 300, vol: 0.4, ft: 'lowpass' }); tone(90, 0.2, { type: 'sine', vol: 0.3, slide: 50 }); },
    raven() { for (let i = 0; i < 2; i++) { const t = ctx.currentTime + i * 0.22; tone(520, 0.16, { when: t, type: 'sawtooth', vol: 0.08, slide: 380, bp: 1300, q: 3 }); nz(0.15, { when: t, f: 1500, vol: 0.06, q: 4 }); } },
    bell() { bell(196, ctx.currentTime, 0.15); },
    fanfare() { const t = ctx.currentTime; [['D4', 0], ['F#4', 0.18], ['A4', 0.36], ['D5', 0.54]].forEach(([n, d]) => horn(freq(n), t + d, 0.12, d === 0.54 ? 1.2 : 0.3)); },
    fail() { const t = ctx.currentTime; horn(freq('A3'), t, 0.1, 0.4); horn(freq('F3'), t + 0.3, 0.1, 0.4); horn(freq('D3'), t + 0.6, 0.1, 1); },
    good() { tone(880, 0.15, { type: 'triangle', vol: 0.12 }); tone(1320, 0.3, { type: 'triangle', vol: 0.1, when: ctx.currentTime + 0.1, rev: true }); },
    bad() { tone(200, 0.3, { type: 'sawtooth', vol: 0.08, lp: 600, slide: 140 }); },
    gallop() { const t = ctx.currentTime; for (let i = 0; i < 4; i++) nz(0.06, { when: t + i * 0.09 + (i > 1 ? 0.05 : 0), f: 200, vol: 0.25, ft: 'lowpass' }); },
    crowd() { nz(1.6, { f: 800, vol: 0.12, q: 0.4, a: 0.3, r: 1 }); },
    trumpet(n) { const f = typeof n === 'number' ? n : freq(n); tone(f, 0.55, { type: 'sawtooth', vol: 0.14, a: 0.03, r: 0.2, lp: 2400, q: 3, rev: true }); tone(f * 2, 0.55, { type: 'square', vol: 0.025, a: 0.03, r: 0.2, lp: 3000 }); },
    hejnal() { const t = ctx.currentTime; ['F4', 'F4', 'A4', 'A4', 'C5', 'A4', 'F4', 'A4', 'C5', 'D5'].forEach((n, i) => horn(freq(n), t + i * 0.32, 0.13, 0.34)); },
    whoosh() { nz(0.35, { f: 400, fs: 2400, vol: 0.12, q: 1 }); },
    heal() { [523, 659, 784].forEach((f, i) => tone(f, 0.5, { when: ctx.currentTime + i * 0.08, type: 'sine', vol: 0.08, rev: true })); },
    dark() { tone(55, 2, { type: 'sawtooth', vol: 0.12, lp: 200, a: 0.3, rev: true }); },
  };
  function sfx(name, arg) { if (!ctx || !on) return; try { S[name](arg); } catch (e) { } }
  function toggle() { on = !on; if (master) master.gain.setTargetAtTime(on ? 0.8 : 0, ctx.currentTime, 0.05); return on; }
  function unlock() { init(); if (pending) { const p = pending; pending = null; music(p); } }
  return { init: unlock, music, stopMusic, sfx, toggle, get on() { return on; } };
})();
