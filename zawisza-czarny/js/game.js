'use strict';
/* =====================================================================
   GAME — stan gry, menedżer scen, warstwa strategiczna (dni, Mrok,
   zasoby, poczet), dialogi, ekwipunek, Kronika, zapis gry.
   ===================================================================== */
const G = (() => {
  const W = 1280, H = 720, TAU = Math.PI * 2;
  const $ = s => document.querySelector(s);
  const cv = $('#cv'), g = cv.getContext('2d');
  let S = null, scene = null, T = 0, last = 0, scale = 1;
  const RANKS = [[0, 'Paź'], [10, 'Giermek'], [25, 'Rycerz'], [45, 'Mistrz wiedzy'], [70, 'Kronikarz Królestwa']];
  const SAVE = 'zawisza_czarny_save', CKPT = 'zawisza_czarny_ckpt';

  function fresh() {
    return { day: 1, gold: 15, honor: 10, wiedza: 0, hp: 100, mrok: 10, chapter: 1, artifacts: [], inv: ['ziola', 'chleb', 'chleb'],
      eq: { weapon: 'miecz', armor: 'kolczuga', shield: null, helm: null }, army: { piechur: 0, kusznik: 0, rycerz: 0 },
      facts: [], flags: {}, joust: 0, loc: null, asked: [] };
  }
  const store = { get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { } } };
  function save() { store.set(SAVE, S); }

  /* ---------- skalowanie i wejście ---------- */
  function fit() { const st = $('#stage'); scale = Math.min(innerWidth / W, innerHeight / H); st.style.transform = `scale(${scale})`; st.style.left = ((innerWidth - W * scale) / 2) + 'px'; st.style.top = ((innerHeight - H * scale) / 2) + 'px'; }
  function pos(e) { const r = cv.getBoundingClientRect(); return { x: (e.clientX - r.left) / r.width * W, y: (e.clientY - r.top) / r.height * H }; }
  cv.addEventListener('pointerdown', e => { Snd.init(); const p = pos(e); scene && scene.click && scene.click(p.x, p.y); });
  cv.addEventListener('pointermove', e => { const p = pos(e); scene && scene.move && scene.move(p.x, p.y); });
  document.addEventListener('pointerdown', () => Snd.init(), { once: true });
  addEventListener('keydown', e => {
    if (e.key === ' ' && scene && scene.key) e.preventDefault();
    if (scene && scene.key) scene.key(e.key);
    if (!S || !$('#hud') || $('#hud').classList.contains('hidden') || !$('#modal').classList.contains('hidden') || !$('#dialog').classList.contains('hidden')) { if (e.key === 'Escape') closeModal(); return; }
    const k = e.key.toLowerCase(); if (k === 'e') openInv(); if (k === 'k') openCodex(); if (k === 'p') openArmy();
  });
  addEventListener('resize', fit);
  function setScene(sc) { if (scene && scene.onExit) scene.onExit(); scene = sc; }
  function loop(ts) { const dt = Math.min(0.05, (ts - last) / 1000 || 0); last = ts; T += dt; if (scene && scene.draw) { g.save(); scene.draw(g, dt, T); g.restore(); } requestAnimationFrame(loop); }

  /* ---------- pomocnicze UI ---------- */
  function el(tag, cls, html) { const e = document.createElement(tag); if (cls) e.className = cls; if (html !== undefined) e.innerHTML = html; return e; }
  function btn(html, fn, cls = '') { const b = el('button', 'btn ' + cls, html); b.onclick = e => { e.stopPropagation(); Snd.sfx('click'); fn(); }; return b; }
  function ico(id, sz = 28) { return `<img class="ico" src="${Art.iconURL(id)}" width="${sz}" height="${sz}" alt="">`; }
  function toast(html, cls = '') { const box = $('#toasts'); while (box.children.length >= 4) box.firstChild.remove(); const t = el('div', 'toast ' + cls, html); box.appendChild(t); setTimeout(() => t.classList.add('out'), 2600); setTimeout(() => t.remove(), 3200); }
  function modal(content, cls = '') { const m = $('#modal'); m.innerHTML = ''; const box = el('div', 'box ' + cls); if (typeof content === 'string') box.innerHTML = content; else box.appendChild(content); m.appendChild(box); m.classList.remove('hidden'); return box; }
  function closeModal() { $('#modal').classList.add('hidden'); $('#modal').innerHTML = ''; }
  function rank() { let r = RANKS[0][1]; RANKS.forEach(([v, n]) => { if (S.wiedza >= v) r = n; }); return r; }
  const NAMES = { gold: ['zloto', 'zł'], honor: ['honor', 'honoru'], wiedza: ['wiedza', 'wiedzy'], hp: ['zdrowie', 'zdrowia'], mrok: ['mrok', 'Mroku'] };

  /* ---------- stan i efekty ---------- */
  function has(id) { return S.inv.includes(id) || Object.values(S.eq).includes(id); }
  function give(id, quiet) { S.inv.push(id); if (!quiet) toast(`${ico(id)} Otrzymujesz: <b>${D.ITEMS[id].name}</b>`, 'gold'); hud(); }
  function take(id) { const i = S.inv.indexOf(id); if (i >= 0) S.inv.splice(i, 1); hud(); }
  function fact(id) { if (!id || S.facts.includes(id)) return; S.facts.push(id); S.wiedza += 1; toast(`${ico('wiedza')} Nowa karta w Kronice: <b>${D.FACTS[id].t}</b> <small>(+1 wiedzy)</small>`, 'know'); Snd.sfx('page'); hud(); }
  function apply(fx, silent) {
    if (!fx) return;
    for (const k in fx) {
      const v = fx[k]; if (!v) continue;
      if (k === 'day') { advance(v); continue; }
      S[k] = (S[k] || 0) + v;
      if (k === 'hp') S.hp = Math.max(1, Math.min(100, S.hp));
      if (k === 'mrok') S.mrok = Math.max(0, Math.min(100, S.mrok));
      if (k === 'gold') S.gold = Math.max(0, S.gold);
      if (!silent && NAMES[k]) toast(`${ico(NAMES[k][0])} ${v > 0 ? '+' : ''}${v} ${NAMES[k][1]}`, (k === 'mrok' ? v < 0 : v > 0) ? 'good' : 'bad');
      if (k === 'gold' && v > 0) Snd.sfx('coin');
    }
    hud(); checkMrok();
  }
  function addArmy(a) { for (const k in a) { S.army[k] += a[k]; toast(`${ico('poczet')} Do pocztu dołącza: ${D.ARMY[k].name} ×${a[k]}`, 'good'); } hud(); }
  function armyCount() { return S.army.piechur + S.army.kusznik + S.army.rycerz; }
  function attack() { return Object.values(S.eq).reduce((a, id) => a + ((id && D.ITEMS[id].atk) || 0), 0); }
  function defense() { return Object.values(S.eq).reduce((a, id) => a + ((id && D.ITEMS[id].def) || 0), 0); }
  function joustBonus() { return S.joust + (S.eq.shield ? 1 : 0) + (has('kopia') ? 1 : 0); }
  function fight(base) { const d = Math.max(3, base - defense() * 3); S.hp -= d; if (S.hp <= 0) { S.hp = 25; S.gold = Math.floor(S.gold / 2); toast('Tracisz przytomność… Mnisi opatrują twoje rany. (połowa złota przepadła)', 'bad'); } else toast(`${ico('zdrowie')} −${d} zdrowia (obrona zbroi: ${defense()})`, 'bad'); Snd.sfx('clash'); hud(); }
  function advance(n = 1) {
    S.day += n; const add = 4 * n; S.mrok = Math.min(100, S.mrok + add); S.hp = Math.min(100, S.hp + 2 * n);
    toast(`${ico('dzien')} Mija dzień (${S.day}). Mrok gęstnieje: +${add}`, 'bad');
    if (S.mrok >= 70 && !S.flags.warn70) { S.flags.warn70 = true; setTimeout(() => toast('Mrok sięga już dachów kościołów! Spiesz się!', 'bad'), 600); }
    hud(); checkMrok(); save();
  }
  function checkMrok() { if (S.mrok >= 100 && !S.flags.dead) { S.flags.dead = true; setTimeout(gameOver, 400); } }

  /* ---------- HUD ---------- */
  function hud() {
    if (!S) return; const h = $('#hud');
    const art = D.ARTIFACTS.map(a => `<span class="art ${S.artifacts.includes(a) ? 'on' : ''}" title="${D.ITEMS[a].name}">${ico(a, 30)}</span>`).join('');
    h.querySelector('.stats').innerHTML =
      `<span title="Dzień">${ico('dzien')}<b>Dzień ${S.day}</b></span>` +
      `<span title="Złoto">${ico('zloto')}<b>${S.gold}</b></span>` +
      `<span title="Honor">${ico('honor')}<b>${S.honor}</b></span>` +
      `<span title="Wiedza — ranga">${ico('wiedza')}<b>${S.wiedza}</b><small>${rank()}</small></span>` +
      `<span title="Zdrowie">${ico('zdrowie')}<i class="bar"><i style="width:${S.hp}%"></i></i></span>` +
      `<span title="Mrok — gdy osiągnie 100, miasto przepadnie" class="mrokw">${ico('mrok')}<i class="bar mrok"><i style="width:${S.mrok}%"></i></i><b>${S.mrok}</b></span>` +
      `<span title="Poczet">${ico('poczet')}<b>${armyCount()}</b></span>`;
    h.querySelector('.arts').innerHTML = art;
    const c = D.CHAPTERS[Math.min(5, S.chapter)];
    h.querySelector('.goal').innerHTML = `<b>Rozdział ${c.n}: ${c.title}</b> — ${S.chapter === 1 && S.flags.audiencja ? 'Odnajdź na Rynku kupcową Agnieszkę.' : c.goal}`;
    $('#fogov').style.opacity = Math.max(0, (S.mrok - 20) / 110);
  }
  function showHUD(v) { $('#hud').classList.toggle('hidden', !v); }

  /* ---------- DIALOGI ---------- */
  let dlg = null;
  function dialog(who, node, onEnd) {
    const tree = D.DLG[who]; dlg = { who, tree, onEnd };
    $('#locpanel').classList.add('hidden');
    showNode(node || tree.start(S));
  }
  function showNode(id) {
    const n = dlg.tree[id]; if (!n) return endDialog();
    if (n.fact) fact(n.fact); if (n.item && !has(n.item)) give(n.item); if (n.fx) apply(n.fx); if (n.flag) S.flags[n.flag] = true;
    if (n.on) { const o = n.on; if (o.fact) fact(o.fact); if (o.flag) S.flags[o.flag] = true; if (o.giveOnce && !has(o.giveOnce)) give(o.giveOnce); if (o.flagOnce && !S.flags[o.flagOnce]) { S.flags[o.flagOnce] = true; if (o.army) addArmy(o.army); } }
    const d = $('#dialog'); d.classList.remove('hidden');
    const sp = D.CH[n.s] || D.CH.kronika;
    const pc = d.querySelector('canvas'); const pg = pc.getContext('2d'); pg.clearRect(0, 0, 220, 260); pg.drawImage(Art.portrait(n.s), 0, 0);
    d.querySelector('.dname').innerHTML = `${sp.name}<small>${sp.role}</small>`;
    const text = typeof n.t === 'function' ? n.t(S) : n.t;
    const tx = d.querySelector('.dtext'); tx.textContent = ''; let i = 0; clearInterval(dlg.tw);
    dlg.tw = setInterval(() => { i += 2; tx.textContent = text.slice(0, i); if (i >= text.length) clearInterval(dlg.tw); }, 16);
    tx.onclick = () => { clearInterval(dlg.tw); tx.textContent = text; };
    const box = d.querySelector('.dchoices'); box.innerHTML = '';
    let ch = (n.c || []).filter(c => !c.cond || c.cond(S));
    if (!n.c) ch = [{ t: n.next ? 'Dalej ▸' : 'Zakończ rozmowę', to: n.next, end: !n.next }];
    ch.forEach((c, k) => box.appendChild(btn(`<span class="num">${k + 1}</span> ${c.t}`, () => choose(c), 'choice')));
    Snd.sfx('page');
  }
  function choose(c) {
    clearInterval(dlg.tw);
    if (c.ok === true) { apply({ wiedza: 3, honor: 1 }, true); toast(`${ico('wiedza')} Dobra odpowiedź! +3 wiedzy, +1 honoru`, 'know'); Snd.sfx('good'); }
    if (c.ok === false) { toast('Niestety, to nie tak…', 'bad'); Snd.sfx('bad'); }
    if (c.fx) apply(c.fx); if (c.fact) fact(c.fact); if (c.item && !has(c.item)) give(c.item); if (c.take) take(c.take); if (c.flag) S.flags[c.flag] = true;
    save();
    if (c.act) { const who = dlg.who; endDialog(true); runAct(c.act, who); return; }
    if (c.end || !c.to) return endDialog();
    showNode(c.to);
  }
  function endDialog(silent) {
    if (!dlg) return; clearInterval(dlg.tw); $('#dialog').classList.add('hidden'); const cb = dlg.onEnd; dlg = null; hud(); save();
    if (cb) cb(); else if (!silent && scene && scene.isLoc) locPanel();
    if (S && S.flags.audiencja && !S.flags.ch1card) { S.flags.ch1card = true; setTimeout(() => toast('Na mapie otworzyły się nowe miejsca: Rynek i Kazimierz.', 'gold'), 300); }
  }
  /* ---------- akcje z dialogów ---------- */
  function runAct(a, who) {
    if (a === 'quiz') return quiz();
    if (a === 'shop') return shop();
    if (a === 'recruit') return recruit();
    if (a === 'waga') return mini(MG.waga((win, r) => { back(); if (r && r.quit) return locPanel(); if (win) { apply({ wiedza: r.mistakes ? 2 : 4 }); artifact('pieczec'); dialog('agnieszka', 'wygrana', () => chapterCard()); } }));
    if (a === 'joust') return mini(MG.joust((win) => { back(); if (win) { apply({ honor: 5 }); artifact('ostroga'); dialog('jasko', 'wygrana', () => chapterCard()); } else { apply({ hp: -20, honor: -1 }); modal(`<h2>Spadasz z konia!</h2><p>Rycerz Kruka śmieje się spod hełmu. Tłum gwiżdże. Odpocznij, potrenuj w szrankach albo kup lepszy sprzęt u kowala — i spróbuj ponownie.</p><p class="hint">Wskazówka: tarcza z herbem, kopia turniejowa i trening dają premię do gonitwy (szersze pola trafienia).</p>`).appendChild(btn('Dalej', () => { closeModal(); locPanel(); })); } }, joustBonus()));
    if (a === 'timeline') return mini(MG.timeline((win, r) => { back(); if (r && r.quit) return locPanel(); apply({ wiedza: Math.max(2, 6 - r.mistakes) }); artifact('przywilej'); dialog('stanislaw', 'wygrana', () => chapterCard()); }));
    if (a === 'hejnal') return mini(MG.hejnal((win, r) => { back(); if (r && r.quit) return locPanel(); if (win) { apply({ wiedza: 3, mrok: -4 }); artifact('wlocznia'); dialog('wojciech', 'wygrana', () => chapterCard()); } else { apply({ hp: -10 }); modal(`<h2>Kruki wróciły</h2><p>Fałszywe nuty rozwścieczyły ptaki. Wojciech chowa trąbkę. — Spróbujmy jeszcze raz, rycerzu. Hejnał trzeba zagrać czysto.</p>`).appendChild(btn('Dalej', () => { closeModal(); locPanel(); })); } }));
    if (a === 'battle') return mini(MG.battle((win, r) => {
      back();
      if (win) { const lost = r.lost || 0; ['piechur', 'kusznik', 'rycerz'].forEach(k => S.army[k] = 0); apply({ honor: 5 }); artifact('szczerbiec', ending); }
      else { apply({ hp: -30, mrok: 6 }); modal(`<h2>Odwrót!</h2><p>Ludzie Komtura wypchnęli was z jaskini. Mrok gęstnieje. Wróć do Kazimierza, zwerbuj więcej ludzi, kup lepszy sprzęt — i spróbuj znowu.</p><p class="hint">Wskazówki: kusznicy strzelają z daleka; rycerze są najwytrzymalsi; „Cios Zawiszy” zadaje podwójne obrażenia; więcej wiedzy = więcej rozkazów na turę; honor 30+ wzmacnia twoich ludzi.</p>`).appendChild(btn('Dalej', () => { closeModal(); locPanel(); })); }
    }));
  }
  function mini(sc) { $('#locpanel').classList.add('hidden'); showHUD(false); setScene(Object.assign(sc, { isMini: true })); }
  function back() { showHUD(true); enterLoc(S.loc, true); }
  function artifact(id, after) {
    if (S.artifacts.includes(id)) return;
    S.artifacts.push(id); S.flags[id] = true; give(id, true); S.chapter = Math.min(6, S.chapter + 1);
    S.mrok = Math.max(0, S.mrok - 12);
    Snd.sfx('fanfare');
    modal(`<div class="artbox"><img src="${Art.iconURL(id)}" width="96" height="96"><h2>${D.ITEMS[id].name}</h2><p>${D.ITEMS[id].desc}</p><p class="good">Skarb odzyskany! Mrok cofa się: −12. (${S.artifacts.length}/5)</p></div>`, 'center').appendChild(btn('Dalej', () => { closeModal(); if (after) after(); }, 'gold'));
    hud(); save(); if (S.chapter <= 5) store.set(CKPT, S);
  }
  function chapterCard() {
    if (S.chapter > 5) return locPanel();
    const c = D.CHAPTERS[S.chapter];
    const b = modal(`<div class="chap"><small>Rozdział ${c.n}</small><h1>${c.title}</h1><p class="where">${c.where}</p><p>${c.goal}</p></div>`, 'center');
    b.appendChild(btn('Ruszaj', () => { closeModal(); locPanel(); }, 'gold')); Snd.sfx('bell');
  }

  /* ---------- ekwipunek ---------- */
  function openInv() {
    if (!S) return; const b = modal('', 'wide'); b.innerHTML = `<h2>Ekwipunek</h2>`;
    const wrap = el('div', 'inv'); b.appendChild(wrap);
    const left = el('div', 'eqcol'); wrap.appendChild(left);
    const SL = { weapon: 'Broń', armor: 'Zbroja', shield: 'Tarcza', helm: 'Hełm' };
    left.innerHTML = `<div class="hero"></div>`;
    const hc = document.createElement('canvas'); hc.width = 200; hc.height = 230; const hg = hc.getContext('2d'); hg.drawImage(Art.bg('kazimierz'), 500, 200, 400, 460, 0, 0, 200, 230); hg.fillStyle = 'rgba(0,0,0,.4)'; hg.fillRect(0, 0, 200, 230); Art.drawKnight(hg, 100, 222, 1.0, { wind: 0 }); left.querySelector('.hero').appendChild(hc);
    Object.keys(SL).forEach(sl => { const id = S.eq[sl]; const r = el('div', 'slot', `<span>${SL[sl]}</span>${id ? ico(id, 40) + `<b>${D.ITEMS[id].name}</b>` : '<i>— puste —</i>'}`); if (id && id !== 'miecz') r.appendChild(btn('Zdejmij', () => { S.eq[sl] = null; S.inv.push(id); openInv(); hud(); }, 'small ghost')); left.appendChild(r); });
    left.appendChild(el('div', 'statline', `Atak: <b>${3 + attack()}</b> · Obrona: <b>${defense()}</b> · Gonitwa: <b>+${joustBonus()}</b>`));
    const rcol = el('div', 'rcol'); wrap.appendChild(rcol); const right = el('div', 'grid'); rcol.appendChild(right);
    const counts = {}; S.inv.forEach(i => counts[i] = (counts[i] || 0) + 1);
    const info = el('div', 'iteminfo', '<p class="hint">Kliknij przedmiot, by zobaczyć opis.</p>');
    Object.keys(counts).forEach(id => {
      const it = D.ITEMS[id]; const c = el('div', 'cell' + (it.art ? ' art' : ''), `${ico(id, 54)}${counts[id] > 1 ? `<em>${counts[id]}</em>` : ''}`); c.title = it.name;
      c.onclick = () => {
        info.innerHTML = `<h3>${ico(id, 34)} ${it.name}</h3><p>${it.desc}</p>${it.atk ? `<p>Atak +${it.atk}</p>` : ''}${it.def ? `<p>Obrona +${it.def}</p>` : ''}${it.joust ? `<p>Gonitwa +${it.joust}</p>` : ''}`;
        if (it.slot) info.appendChild(btn('Załóż', () => { const old = S.eq[it.slot]; S.eq[it.slot] = id; take(id); if (old) S.inv.push(old); Snd.sfx('clash'); openInv(); hud(); }, 'gold'));
        if (it.use) info.appendChild(btn('Użyj', () => { take(id); if (it.use === 'hp') { apply({ hp: it.val }); Snd.sfx('heal'); } else { apply({ mrok: -it.val }); } openInv(); }, 'gold'));
      };
      right.appendChild(c);
    });
    if (!S.inv.length) right.appendChild(el('p', 'hint', 'Plecak jest pusty.'));
    rcol.appendChild(info);
    b.appendChild(btn('Zamknij [Esc]', closeModal, 'ghost'));
  }
  /* ---------- Kronika ---------- */
  function openCodex() {
    if (!S) return; const ids = Object.keys(D.FACTS);
    const b = modal(`<h2>Kronika brata Mikołaja <small>${S.facts.length}/${ids.length} kart · Wiedza: ${S.wiedza} · Ranga: ${rank()}</small></h2><p class="hint">FAKT — tak było naprawdę. LEGENDA — opowieść przekazywana przez wieki. FIKCJA — wymyślone na potrzeby gry.</p>`, 'wide');
    const list = el('div', 'codex'); b.appendChild(list);
    ids.forEach(id => { const f = D.FACTS[id]; const on = S.facts.includes(id); list.appendChild(el('div', 'card ' + (on ? f.tag.toLowerCase() : 'locked'), on ? `<span class="tag">${f.tag}</span><h4>${f.t}</h4><p>${f.x}</p>` : `<span class="tag">???</span><h4>Nieodkryta karta</h4><p>Rozmawiaj, odpowiadaj i odkrywaj, by ją zapisać.</p>`)); });
    b.appendChild(btn('Zamknij [Esc]', closeModal, 'ghost'));
  }
  function openArmy() {
    if (!S) return;
    const b = modal(`<h2>Poczet Zawiszy</h2><p class="hint">Poczet to oddział, który rycerz prowadził na wojnę: giermkowie, kusznicy, piechurzy i inni rycerze. Werbujesz go u kowala Bartosza na Kazimierzu. Przyda się w ostatecznej bitwie.</p>`);
    const t = el('div', 'armylist'); b.appendChild(t);
    Object.keys(D.ARMY).forEach(k => t.appendChild(el('div', 'arow', `<b>${D.ARMY[k].name}</b> ×${S.army[k]}<small>${D.ARMY[k].desc}</small>`)));
    b.appendChild(el('p', 'statline', `Rozkazy w bitwie: <b>${Math.min(4, 2 + Math.floor(S.wiedza / 20))}</b> na turę (więcej wiedzy = więcej rozkazów: +1 za każde 20 pkt).`));
    b.appendChild(btn('Zamknij [Esc]', closeModal, 'ghost'));
  }
  /* ---------- sklep i werbunek ---------- */
  function shop() {
    const b = modal(`<h2>Kuźnia Bartosza <small>${ico('zloto', 22)} ${S.gold} zł</small></h2>`, 'wide'); const list = el('div', 'shop'); b.appendChild(list);
    ['zbroja', 'tarcza', 'helm', 'kopia', 'ziola', 'chleb', 'pochodnia'].forEach(id => {
      const it = D.ITEMS[id]; const owned = (it.slot || id === 'kopia') && has(id);
      const r = el('div', 'srow', `${ico(id, 48)}<div><b>${it.name}</b><small>${it.desc}</small></div>`);
      r.appendChild(owned ? el('span', 'owned', 'Masz') : btn(`${it.price} zł`, () => { if (S.gold < it.price) { toast('Za mało złota!', 'bad'); Snd.sfx('bad'); return; } S.gold -= it.price; give(id); Snd.sfx('coin'); if (it.slot && !S.eq[it.slot] || (it.slot === 'armor' && S.eq.armor === 'kolczuga')) { const old = S.eq[it.slot]; S.eq[it.slot] = id; take(id); if (old) S.inv.push(old); toast(`Zakładasz: ${it.name}`, 'good'); } hud(); save(); shop(); }, S.gold >= it.price ? 'gold' : 'ghost'));
      list.appendChild(r);
    });
    b.appendChild(btn('Wróć', () => { closeModal(); locPanel(); }, 'ghost'));
  }
  function recruit() {
    const b = modal(`<h2>Werbunek do pocztu <small>${ico('zloto', 22)} ${S.gold} zł · ${ico('honor', 22)} ${S.honor}</small></h2><p class="hint">Rycerz płacił swoim ludziom żołd. Dobry dowódca zna mocne strony każdego wojownika.</p>`, 'wide'); const list = el('div', 'shop'); b.appendChild(list);
    Object.keys(D.ARMY).forEach(k => {
      const a = D.ARMY[k]; const lock = a.honor && S.honor < a.honor;
      const r = el('div', 'srow', `${ico(k === 'kusznik' ? 'kopia' : k === 'rycerz' ? 'helm' : 'poczet', 48)}<div><b>${a.name}</b> <em>(masz: ${S.army[k]})</em><small>${a.desc} — ${a.hp}♥ · atak ${a.atk} · zasięg ${a.rng}</small></div>`);
      r.appendChild(lock ? el('span', 'owned', `Honor ${a.honor}+`) : btn(`${a.price} zł`, () => { if (S.gold < a.price) { toast('Za mało złota!', 'bad'); Snd.sfx('bad'); return; } S.gold -= a.price; S.army[k]++; Snd.sfx('clash'); hud(); save(); recruit(); }, S.gold >= a.price ? 'gold' : 'ghost'));
      list.appendChild(r);
    });
    if (!S.facts.includes('kusza')) fact('kusza');
    b.appendChild(btn('Wróć', () => { closeModal(); locPanel(); }, 'ghost'));
  }
  /* ---------- próba wiedzy ---------- */
  function pickQ(n) { let pool = D.QUIZ.map((q, i) => i).filter(i => !S.asked.includes(i)); if (pool.length < n) { S.asked = []; pool = D.QUIZ.map((q, i) => i); } pool.sort(() => Math.random() - 0.5); const out = pool.slice(0, n); S.asked.push(...out); return out.map(i => D.QUIZ[i]); }
  function quiz() {
    const qs = pickQ(3); let i = 0, good = 0; S.flags['quiz' + S.chapter] = true;
    const step = () => {
      if (i >= qs.length) { const b = modal(`<h2>Próba zakończona</h2><p>Poprawne odpowiedzi: <b>${good}/3</b>.</p><p>Brat Mikołaj kiwa głową. — ${good === 3 ? 'Mądrość godna rycerza!' : good ? 'Nieźle, ale kroniki trzeba czytać pilniej.' : 'Hmm… Zajrzyj do Kroniki, rycerzu.'}</p>`); b.appendChild(btn('Dalej', () => { closeModal(); locPanel(); }, 'gold')); return; }
      const q = qs[i]; const b = modal(`<h2>Próba wiedzy ${i + 1}/3</h2><p class="q">${q.q}</p>`); const box = el('div', 'answers'); b.appendChild(box);
      q.a.forEach((a, k) => box.appendChild(btn(a, () => {
        box.querySelectorAll('button').forEach((x, j) => { x.disabled = true; if (j === q.ok) x.classList.add('right'); else if (j === k) x.classList.add('wrong'); });
        if (k === q.ok) { good++; apply({ wiedza: 3, gold: 2 }, true); toast(`${ico('wiedza')} Dobrze! +3 wiedzy, +2 zł`, 'know'); Snd.sfx('good'); } else Snd.sfx('bad');
        fact(q.f); i++; b.appendChild(btn('Dalej ▸', step, 'gold'));
      }, 'answer')));
    };
    step();
  }
  /* ---------- zdarzenia w drodze ---------- */
  function event(after) {
    const pool = D.EVENTS.filter(e => !S.flags['ev_' + e.id] || e.quiz || e.id === 'zbojcy' || e.id === 'kruki');
    const ev = pool[Math.floor(Math.random() * pool.length)]; S.flags['ev_' + ev.id] = true;
    const b = modal(`<h2>W drodze…</h2><p>${ev.t}</p>`); if (ev.fact) fact(ev.fact); Snd.sfx(ev.id === 'kruki' || ev.id === 'szpieg' ? 'raven' : 'page');
    if (ev.quiz) {
      const q = pickQ(1)[0]; b.appendChild(el('p', 'q', q.q)); const box = el('div', 'answers'); b.appendChild(box);
      q.a.forEach((a, k) => box.appendChild(btn(a, () => { box.querySelectorAll('button').forEach((x, j) => { x.disabled = true; if (j === q.ok) x.classList.add('right'); else if (j === k) x.classList.add('wrong'); }); if (k === q.ok) { apply({ wiedza: 3, gold: 3 }); b.appendChild(el('p', 'good', 'Żak wygrał zakład i dzieli się z tobą wygraną!')); } else b.appendChild(el('p', 'bad', 'Żak drapie się w głowę. — Chyba jednak przegrałem…')); fact(q.f); b.appendChild(btn('Dalej', () => { closeModal(); after(); }, 'gold')); }, 'answer')));
      return;
    }
    const box = el('div', 'answers'); b.appendChild(box);
    ev.c.filter(c => !c.cond || c.cond(S)).forEach(c => box.appendChild(btn(c.t, () => {
      if (c.take) take(c.take); if (c.fight) fight(c.fight); apply(c.fx); if (c.army) addArmy(c.army); if (c.give) c.give.forEach(i => give(i, true));
      box.remove(); b.appendChild(el('p', 'res', c.r)); b.appendChild(btn('Dalej', () => { closeModal(); after(); }, 'gold')); save();
    }, 'answer')));
  }

  /* ---------- SCENA: tytuł ---------- */
  function titleScene() {
    showHUD(false); $('#locpanel').classList.add('hidden'); $('#title').classList.remove('hidden');
    const has = store.get(SAVE); $('#bCont').classList.toggle('hidden', !has || has.flags.dead || has.flags.won);
    const embers = []; for (let i = 0; i < 60; i++) embers.push({ x: Math.random() * W, y: Math.random() * H, v: 20 + Math.random() * 40, s: 1 + Math.random() * 2 });
    const rv = []; for (let i = 0; i < 7; i++) rv.push({ x: Math.random() * W, y: 80 + Math.random() * 200, v: 40 + Math.random() * 50, s: 0.6 + Math.random() * 0.6 });
    Snd.music('title');
    setScene({
      draw(g, dt, T) {
        g.drawImage(Art.bg('title'), 0, 0);
        rv.forEach(r => { r.x += r.v * dt; if (r.x > W + 40) { r.x = -40; r.y = 80 + Math.random() * 200; } Art.raven(g, r.x, r.y + Math.sin(T + r.v) * 10, r.s, T * 9 + r.v); });
        Art.drawKnight(g, 250, 640, 2.4, { wind: Math.sin(T * 1.3) * 6 + 6 });
        embers.forEach(e => { e.y -= e.v * dt; e.x += Math.sin(T + e.v) * 0.4; if (e.y < -10) { e.y = H + 10; e.x = Math.random() * W; } g.fillStyle = `rgba(255,${140 + (e.v * 2 | 0)},60,${0.5 + Math.sin(T * 3 + e.v) * 0.3})`; g.fillRect(e.x, e.y, e.s, e.s); });
      },
    });
  }
  function startNew() { S = fresh(); store.set(SAVE, S); store.set(CKPT, S); $('#title').classList.add('hidden'); intro(); }
  function cont() { S = store.get(SAVE); if (!S) return startNew(); $('#title').classList.add('hidden'); showHUD(true); hud(); mapScene(); }
  function intro() {
    let i = 0; const pages = [
      'Rok Pański 1409. Królestwo Polskie szykuje się do wielkiej wojny z Zakonem Krzyżackim.',
      'Nad Krakowem zawisł Mrok. Świece gasną same, kruki o zielonych oczach obsiadają dachy, a ze skarbca na Wawelu zniknęło pięć skarbów Królestwa.',
      'Król Władysław Jagiełło wzywa najwierniejszego ze swoich rycerzy — Zawiszę Czarnego z Garbowa, herbu Sulima.',
    ];
    setScene({ draw(g, dt, T) { g.drawImage(Art.bg('wawel'), 0, 0); g.fillStyle = 'rgba(0,0,0,.55)'; g.fillRect(0, 0, W, H); Art.drawKnight(g, 640, 660, 2, { wind: Math.sin(T) * 5 + 5 }); } });
    const show = () => { const b = modal(`<p class="introtext">${pages[i]}</p>`, 'center intro'); b.appendChild(btn(i < pages.length - 1 ? 'Dalej ▸' : 'Na Wawel!', () => { i++; if (i < pages.length) show(); else { closeModal(); fact('zawisza'); showHUD(true); hud(); enterLoc('wawel', true); setTimeout(() => modal(`<div class="chap"><small>Rozdział I</small><h1>${D.CHAPTERS[1].title}</h1><p class="where">${D.CHAPTERS[1].where}</p><p>${D.CHAPTERS[1].goal}</p></div>`, 'center').appendChild(btn('Ruszaj', closeModal, 'gold')), 200); } }, 'gold')); };
    show(); Snd.sfx('bell');
  }

  /* ---------- SCENA: mapa strategiczna ---------- */
  const MARK = { wawel: 'pieczec', rynek: 'zloto', kazimierz: 'zbroja', turniej: 'kopia', akademia: 'wiedza', mariacki: 'list', smocza: 'mrok' };
  function unlocked(id) { const L = D.LOC[id]; return S.chapter >= L.ch && (!L.flag || S.flags[L.flag]); }
  function target(id) { const L = D.LOC[id]; return L.ch === Math.min(5, S.chapter) && unlocked(id) && !(S.chapter === 1 && !S.flags.audiencja && id !== 'wawel') && !(S.chapter === 1 && S.flags.audiencja && id !== 'rynek'); }
  function mapScene() {
    S.loc = null; save(); showHUD(true); hud(); $('#locpanel').classList.add('hidden');
    let hover = null; const fog = []; for (let i = 0; i < 40; i++) fog.push({ x: Math.random() * W, y: Math.random() * H, r: 80 + Math.random() * 160, v: 6 + Math.random() * 14 });
    Snd.music('map');
    setScene({
      draw(g, dt, T) {
        g.drawImage(Art.bg('map'), 0, 0);
        // Mrok — mgła na mapie
        const m = S.mrok / 100;
        fog.forEach(f => { f.x += f.v * dt; if (f.x - f.r > W) f.x = -f.r; const gr = g.createRadialGradient(f.x, f.y, 0, f.x, f.y, f.r); gr.addColorStop(0, `rgba(10,20,16,${0.18 + m * 0.4})`); gr.addColorStop(1, 'rgba(10,20,16,0)'); g.fillStyle = gr; g.fillRect(f.x - f.r, f.y - f.r, f.r * 2, f.r * 2); });
        const gr = g.createRadialGradient(W / 2, H / 2, 200 - m * 150, W / 2, H / 2, 760 - m * 300); gr.addColorStop(0, 'rgba(4,10,8,0)'); gr.addColorStop(1, `rgba(4,10,8,${0.4 + m * 0.5})`); g.fillStyle = gr; g.fillRect(0, 0, W, H);
        for (const id in D.LOC) {
          const L = D.LOC[id], on = unlocked(id), tg = target(id), hv = hover === id;
          const r = hv ? 34 : 30;
          if (tg) { g.save(); g.globalCompositeOperation = 'lighter'; Art.glow(g, L.x, L.y, 60 + Math.sin(T * 3) * 10, '#ffc860', 0.45); g.restore(); }
          g.fillStyle = on ? '#3a0c0c' : '#1a1616'; g.beginPath(); g.arc(L.x, L.y, r, 0, TAU); g.fill();
          g.lineWidth = 4; g.strokeStyle = on ? '#c9a24a' : '#4a4440'; g.stroke();
          g.save(); g.beginPath(); g.arc(L.x, L.y, r - 4, 0, TAU); g.clip(); g.globalAlpha = on ? 1 : 0.3; g.drawImage(Art.icon(MARK[id]), L.x - r + 4, L.y - r + 4, (r - 4) * 2, (r - 4) * 2); g.restore();
          if (!on) { g.strokeStyle = '#8a8070'; g.lineWidth = 3; g.beginPath(); g.moveTo(L.x - 14, L.y - 14); g.lineTo(L.x + 14, L.y + 14); g.moveTo(L.x + 14, L.y - 14); g.lineTo(L.x - 14, L.y + 14); g.stroke(); }
          if (S.loc === id) { }
          g.font = `${hv ? 'bold ' : ''}17px Cinzel, Georgia, serif`; g.textAlign = 'center';
          const lw = g.measureText(L.name).width + 16; g.fillStyle = 'rgba(20,12,8,.78)'; g.fillRect(L.x - lw / 2, L.y + r + 6, lw, 24);
          g.fillStyle = on ? (tg ? '#ffd870' : '#efe2c4') : '#8a8070'; g.fillText(L.name, L.x, L.y + r + 24);
        }
        if (hover) { const L = D.LOC[hover]; const on = unlocked(hover); const tip = on ? L.desc + (hover === S.lastLoc ? '' : '  (podróż: 1 dzień)') : 'Zamknięte — odblokujesz w dalszym rozdziale.'; g.font = '16px Spectral, Georgia, serif'; const w = g.measureText(tip).width + 24; const x = Math.min(W - w - 10, Math.max(10, L.x - w / 2)); g.fillStyle = 'rgba(20,12,8,.9)'; g.fillRect(x, L.y - 76, w, 30); g.strokeStyle = '#c9a24a'; g.strokeRect(x, L.y - 76, w, 30); g.fillStyle = '#efe2c4'; g.textAlign = 'left'; g.fillText(tip, x + 12, L.y - 56); }
        g.font = 'italic 16px Spectral, Georgia, serif'; g.textAlign = 'center'; const ht = 'Kliknij miejsce na mapie, by tam wyruszyć. Złote światło wskazuje cel rozdziału.'; const hw = g.measureText(ht).width + 30; g.fillStyle = 'rgba(20,12,8,.8)'; g.fillRect(W / 2 - hw / 2, H - 38, hw, 28); g.fillStyle = '#efe2c4'; g.fillText(ht, W / 2, H - 18);
      },
      move(x, y) { hover = null; for (const id in D.LOC) { const L = D.LOC[id]; if (Math.hypot(x - L.x, y - L.y) < 36) hover = id; } cv.style.cursor = hover ? 'pointer' : 'default'; },
      click(x, y) { this.move(x, y); if (!hover) return; if (!$('#modal').classList.contains('hidden')) return; if (!unlocked(hover)) { toast('To miejsce jest jeszcze zamknięte.', 'bad'); Snd.sfx('bad'); return; } travel(hover); },
    });
  }
  function travel(id) {
    cv.style.cursor = 'default';
    if (S.lastLoc === id) return enterLoc(id);
    advance(1); if (S.flags.dead) return;
    S.lastLoc = id;
    if (Math.random() < 0.38 && S.flags.audiencja) event(() => enterLoc(id)); else enterLoc(id);
  }

  /* ---------- SCENA: lokacja ---------- */
  const POS = { wawel: [[640, 'jagiello'], [880, 'mikolaj']], rynek: [[820, 'agnieszka']], kazimierz: [[790, 'bartosz']], turniej: [[860, 'jasko']], akademia: [[820, 'stanislaw']], mariacki: [[780, 'wojciech']], smocza: [[860, 'komtur']] };
  function enterLoc(id, noMusic) {
    S.loc = id; S.lastLoc = id; save(); showHUD(true); hud(); const L = D.LOC[id];
    if (!noMusic) Snd.music('loc'); else Snd.music('loc');
    if (id === 'turniej' && S.flags.ostroga) { }
    const motes = []; for (let i = 0; i < 40; i++) motes.push({ x: Math.random() * W, y: Math.random() * H, v: 6 + Math.random() * 20, a: Math.random() * TAU });
    const rv = []; const nR = { rynek: 3, wawel: 4, mariacki: 6, turniej: 2 }[id] || 0; for (let i = 0; i < nR; i++) rv.push({ x: Math.random() * W, y: 60 + Math.random() * 220, v: 40 + Math.random() * 60, s: 0.5 + Math.random() * 0.5 });
    setScene({
      isLoc: true,
      draw(g, dt, T) {
        g.drawImage(Art.bg(L.bg), 0, 0);
        rv.forEach(r => { r.x += r.v * dt; if (r.x > W + 40) { r.x = -40; r.y = 60 + Math.random() * 220; } Art.raven(g, r.x, r.y + Math.sin(T + r.v) * 8, r.s, T * 9 + r.v); });
        (POS[id] || []).forEach(([x, who]) => { if (who === 'komtur' && S.flags.szczerbiec) return; Art.drawNPC(g, x, 620, 1.75, who, T); });
        if (id === 'turniej' && !S.flags.ostroga) Art.drawNPC(g, 1110, 600, 1.3, 'kruk', T);
        Art.drawKnight(g, 330, 640, 1.9, { wind: Math.sin(T * 1.2) * 4 + 4 });
        motes.forEach(m => { m.y -= m.v * dt * 0.3; m.x += Math.sin(T * 0.5 + m.a) * 0.3; if (m.y < 0) m.y = H; const c = id === 'kazimierz' ? `rgba(255,150,60,${0.4 + Math.sin(T * 4 + m.a) * 0.3})` : id === 'smocza' ? 'rgba(106,240,176,.35)' : 'rgba(230,220,200,.18)'; g.fillStyle = c; g.fillRect(m.x, m.y, 2, 2); });
        const fogA = S.mrok / 100 * 0.35; g.fillStyle = `rgba(6,14,12,${fogA})`; g.fillRect(0, 0, W, H);
        g.font = '30px Cinzel, Georgia, serif'; g.textAlign = 'left'; g.fillStyle = 'rgba(0,0,0,.6)'; g.fillText(L.name, 32, 162); g.fillStyle = '#efe2c4'; g.fillText(L.name, 30, 160);
      },
    });
    locPanel();
  }
  function locPanel() {
    if (!S || !S.loc) return; const id = S.loc, L = D.LOC[id]; const p = $('#locpanel'); p.innerHTML = ''; p.classList.remove('hidden');
    p.appendChild(el('h3', '', L.name)); p.appendChild(el('p', 'desc', L.desc));
    const add = (h, fn, cls) => p.appendChild(btn(h, fn, cls));
    (POS[id] || []).forEach(([, who]) => { if (who === 'komtur' && S.flags.szczerbiec) return; const main = (id === 'wawel' && who === 'jagiello' && (!S.flags.audiencja || (S.chapter === 5 && !S.flags.straz))) || (D.LOC[id].ch === S.chapter && id !== 'wawel' && id !== 'kazimierz'); add(`Rozmawiaj: ${D.CH[who].name}`, () => dialog(who), main ? 'gold pulse' : ''); });
    if (id === 'wawel' && S.flags.audiencja) add('Odpocznij w zamku (1 dzień, +40 zdrowia)', () => { advance(1); apply({ hp: 40 }); Snd.sfx('heal'); });
    if (id === 'rynek' && S.flags.audiencja) add('Strzeż straganów nocą (1 dzień, zarobek)', () => { advance(1); if (S.flags.dead) return; if (Math.random() < 0.55) { apply({ gold: 8 }); toast('Noc minęła spokojnie. Kupcy płacą za straż.', 'good'); } else { fight(16); apply({ gold: 12, honor: 1 }); toast('Złodzieje w kapturach! Przegnałeś ich.', 'good'); } });
    if (id === 'kazimierz') { add('Kuźnia: kup sprzęt', shop); add('Werbuj ludzi do pocztu', recruit); add('Karczma: odpoczynek (2 zł, 1 dzień, +50 zdrowia)', () => { if (S.gold < 2) return toast('Za mało złota!', 'bad'); S.gold -= 2; advance(1); apply({ hp: 50 }); Snd.sfx('heal'); }); }
    if (id === 'turniej' && S.chapter >= 2) add(`Trenuj gonitwę (1 dzień) — poziom ${S.joust}/3`, () => { if (S.joust >= 3) return toast('Lepiej już nie wytrenujesz konia.', 'bad'); advance(1); S.joust++; Snd.sfx('gallop'); toast(`Trening! Gonitwa +1 (poziom ${S.joust}/3)`, 'good'); fact('giermek'); hud(); locPanel(); });
    if (id === 'akademia' && S.chapter >= 3) add('Studiuj w bibliotece (1 dzień, +2 wiedzy, nowa karta)', () => { advance(1); if (S.flags.dead) return; apply({ wiedza: 2 }); const left = Object.keys(D.FACTS).filter(f => !S.facts.includes(f) && f !== 'fikcja'); if (left.length) fact(left[Math.floor(Math.random() * left.length)]); });
    if (id === 'mariacki' && !S.flags['modl' + S.chapter]) add('Zapal świecę w kościele (1 dzień, −7 Mroku, raz na rozdział)', () => { S.flags['modl' + S.chapter] = true; advance(1); apply({ mrok: -7, hp: 15 }); Snd.sfx('bell'); locPanel(); });
    add('◂ Wróć na mapę Krakowa', mapScene, 'ghost');
  }

  /* ---------- zakończenia ---------- */
  function ending() {
    S.flags.won = true; save(); showHUD(false); $('#locpanel').classList.add('hidden'); Snd.music('end');
    const doves = []; for (let i = 0; i < 12; i++) doves.push({ x: Math.random() * W, y: 100 + Math.random() * 250, v: 30 + Math.random() * 40, s: 0.4 + Math.random() * 0.4 });
    setScene({ draw(g, dt, T) { g.drawImage(Art.bg('koniec'), 0, 0); doves.forEach(d => { d.x += d.v * dt; if (d.x > W + 30) d.x = -30; Art.raven(g, d.x, d.y + Math.sin(T + d.v) * 6, d.s, T * 8 + d.v, '#f4ece0'); }); Art.drawKnight(g, 640, 690, 2.1, { wind: Math.sin(T) * 4 + 4 }); } });
    ['grunwald', 'perpignan', 'golubac'].forEach(f => fact(f));
    let i = 0;
    const page = () => {
      if (i < D.EPILOG.length) { const b = modal(`<p class="introtext">${D.EPILOG[i]}</p>`, 'center intro'); b.appendChild(btn('Dalej ▸', () => { i++; page(); }, 'gold')); return; }
      const score = S.wiedza * 2 + S.honor * 2 + Math.max(0, 100 - S.mrok) + Math.max(0, 60 - S.day) * 2;
      const b = modal(`<div class="cert"><small>Kronika Królestwa poświadcza, że</small><h1>Zawisza Czarny z Garbowa</h1><p>odzyskał pięć skarbów Królestwa i rozproszył Mrok nad Krakowem w ciągu <b>${S.day}</b> ${S.day === 1 ? 'dnia' : 'dni'}.</p>
        <div class="certstats"><span>${ico('wiedza')} Wiedza: <b>${S.wiedza}</b> (${rank()})</span><span>${ico('honor')} Honor: <b>${S.honor}</b></span><span>${ico('mrok')} Mrok na końcu: <b>${S.mrok}</b></span><span>Karty Kroniki: <b>${S.facts.length}/${Object.keys(D.FACTS).length}</b></span></div>
        <h2>Wynik: ${score}</h2><p class="hint">Polegać jak na Zawiszy — teraz już wiesz dlaczego.</p></div>`, 'center wide');
      b.appendChild(btn('Otwórz Kronikę', openCodex, 'ghost')); b.appendChild(btn('Zagraj ponownie', () => { closeModal(); startNew(); }, 'gold'));
    };
    setTimeout(page, 1200);
  }
  function gameOver() {
    showHUD(false); $('#locpanel').classList.add('hidden'); $('#dialog').classList.add('hidden'); Snd.stopMusic(); Snd.sfx('dark');
    setScene({ draw(g, dt, T) { g.drawImage(Art.bg('title'), 0, 0); g.fillStyle = `rgba(4,12,10,${Math.min(0.85, 0.5 + T * 0.02)})`; g.fillRect(0, 0, W, H); for (let i = 0; i < 20; i++) Art.raven(g, (i * 97 + T * 60) % (W + 80) - 40, 100 + (i * 53) % 400, 0.9, T * 9 + i); } });
    const ck = store.get(CKPT);
    const b = modal(`<h1 class="dark">Mrok pochłonął Kraków</h1><p>Ostatnie świece zgasły. Kruki zamilkły, bo nie było już kogo straszyć. Komtur zasiadł w ciemności na Wawelu…</p><p class="hint">Mrok rośnie z każdym dniem (+4). Zmniejszają go: odzyskane skarby (−12), świeca w kościele Mariackim, pochodnie i schwytanie szpiega. Nie trać dni na zbędne podróże!</p>`, 'center');
    if (ck) b.appendChild(btn('Wróć do początku rozdziału', () => { S = ck; S.flags.dead = false; S.mrok = Math.min(S.mrok, 60); closeModal(); store.set(SAVE, S); showHUD(true); hud(); mapScene(); }, 'gold'));
    b.appendChild(btn('Nowa gra', () => { closeModal(); startNew(); }, 'ghost'));
  }
  function help() {
    modal(`<h2>Jak grać</h2><ul class="help">
      <li><b>Cel:</b> odzyskaj 5 skarbów Królestwa, zanim <b>Mrok</b> osiągnie 100.</li>
      <li><b>Mapa:</b> każda podróż do innego miejsca to 1 dzień, a każdy dzień to +4 Mroku. Planuj trasę! Złote światło pokazuje cel rozdziału.</li>
      <li><b>Dialogi:</b> wybieraj odpowiedzi — dobre odpowiedzi dają <b>wiedzę</b>, szlachetne czyny dają <b>honor</b>.</li>
      <li><b>Kronika [K]:</b> zbieraj karty wiedzy o średniowieczu, turniejach i historii Krakowa.</li>
      <li><b>Ekwipunek [E]:</b> zakładaj zbroję, tarczę i hełm, używaj ziół i pochodni.</li>
      <li><b>Poczet [P]:</b> werbuj ludzi u kowala na Kazimierzu — przydadzą się w ostatniej bitwie.</li>
      <li><b>Minigry:</b> waga kupiecka, gonitwa rycerska, zamek dziejów, hejnał i bitwa taktyczna.</li>
      <li>Wiedza zwiększa liczbę rozkazów w bitwie, honor wzmacnia twoich ludzi.</li></ul>`, 'center').appendChild(btn('Rozumiem', closeModal, 'gold'));
  }

  /* ---------- start ---------- */
  function boot() {
    fit(); requestAnimationFrame(loop);
    $('#bNew').onclick = () => { Snd.init(); Snd.sfx('click'); startNew(); };
    $('#bCont').onclick = () => { Snd.init(); Snd.sfx('click'); cont(); };
    $('#bHelp').onclick = () => { Snd.init(); help(); };
    $('#hInv').onclick = () => openInv(); $('#hCod').onclick = () => openCodex(); $('#hArmy').onclick = () => openArmy(); $('#hHelp').onclick = help;
    $('#hSnd').onclick = () => { const on = Snd.toggle(); $('#hSnd').textContent = on ? 'Dźwięk: wł.' : 'Dźwięk: wył.'; };
    $('#hMenu').onclick = () => { save(); closeModal(); $('#dialog').classList.add('hidden'); titleScene(); };
    const bar = $('#loadbar i');
    Art.preload((k, name) => { bar.style.width = (k * 100) + '%'; $('#loadtxt').textContent = 'Maluję: ' + ({ title: 'tytuł', map: 'mapę Krakowa', wawel: 'Wawel', rynek: 'Rynek', kazimierz: 'kuźnię', turniej: 'szranki', akademia: 'Akademię', mariacki: 'Mariacki', smocza: 'Smoczą Jamę', bitwa: 'pole bitwy', koniec: 'świt' }[name] || name) + '…'; })
      .then(() => { $('#loading').classList.add('hidden'); titleScene(); });
  }
  return { boot, has, take, armyCount, attack, defense, S: () => S, _debug: { scene: () => scene, get S() { return S; }, set S(v) { S = v; }, enterLoc, mapScene, runAct, dialog, ending, gameOver, openInv, openCodex, chapterCard, hud } };
})();
window.addEventListener('load', () => G.boot());
