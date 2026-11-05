# -*- coding: utf-8 -*-
"""Test integracyjny: bot przechodzi całą kampanię bez okna (SDL dummy).

Uruchom:  python tests/bot_kampania.py
"""
import os
import random
import sys
import tempfile

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["APPDATA"] = tempfile.mkdtemp()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from kronika import data  # noqa: E402
from kronika.app import App  # noqa: E402
from kronika.modals import Dialogue, Quiz, Info  # noqa: E402
from kronika.battle import Battle, resolve  # noqa: E402
from kronika.mapview import MapScene  # noqa: E402
from kronika.scenes import (ChronicleScene, VictoryScene, EndingScene, DefeatScene, TechScene,  # noqa: E402
                            ArmyScene, MenuScene, ChapterSelectScene)
from kronika.world import N  # noqa: E402


def bot_map(app, ms):
    w = ms.w
    # 1) technologie potrzebne do celów i budynków
    wanted = []
    for o in w.ch["objectives"]:
        if o[0] == "tech":
            wanted.append(o[1])
        if o[0] == "build" and data.BUILDINGS[o[1]].get("req"):
            wanted.append(data.BUILDINGS[o[1]]["req"])
    wanted += ["radlo", "grod_walowy", "druzyna", "denar", "kusza", "rycerze", "trojpolowka", "prawo_magd"]

    def need(t, acc):
        for r in data.TECHS[t]["req"]:
            need(r, acc)
        if t not in acc:
            acc.append(t)
    order = []
    for t in wanted:
        if data.TECHS[t]["epoch"] <= w.epoch:
            need(t, order)
    for t in order:
        if t not in w.techs and t not in w.tech_locked and all(r in w.techs for r in data.TECHS[t]["req"]) \
                and w.has(w.tech_cost(t)):
            ts = TechScene(app, ms)
            app.push(ts)
            ts.riddle(t)
            return True
    # 2) budowa
    plan = []
    for o in w.ch["objectives"]:
        if o[0] == "build" and w.count(o[1]) < o[2]:
            plan.append(o[1])
    for o in w.ch["objectives"]:
        if o[0] == "res":
            plan.append({"food": "pole", "silver": "targ", "wood": "drwal", "stone": "kamieniolom"}[o[1]])
    if w.ch.get("siege_turn"):
        plan.insert(0, "palisada")
    prod = {"food": "pole", "silver": "targ", "wood": "drwal", "stone": "kamieniolom"}
    for kind in list(plan):
        for k, v in w.build_cost(kind).items():
            if w.res[k] < v and w.count(prod[k]) < 3:
                plan.insert(0, prod[k])
    if w.count("koszary") == 0:
        plan.insert(0, "koszary")
    for kind in ["kamieniolom", "drwal", "pole", "targ"]:
        if w.count(kind) < 2:
            plan.append(kind)
    plan += ["pole", "drwal", "targ", "kamieniolom"]
    if w.res["food"] < 10:
        plan.insert(0, "pole")
    if w.res["wood"] < 10:
        plan.insert(0, "drwal")
    built = getattr(ms, "_bot_built", (0, 0))
    if built[0] != w.turn:
        built = (w.turn, 0)
    for kind in plan:
        if built[1] >= 3:
            break
        cells = sorted(w.territory, key=lambda p: abs(p[0] - w.cap[0]) + abs(p[1] - w.cap[1]))
        for pos in cells:
            ok, _ = w.can_build(kind, pos)
            if ok:
                ms.sel = pos
                ms.build(kind)
                ms._bot_built = (w.turn, built[1] + 1)
                return True
    # 3) werbunek
    if w.recruit_slots() > 0:
        for cid in sorted(w.available_cards(), key=lambda c: -data.CARDS[c]["power"]):
            if w.has(data.CARDS[cid]["cost"]) and len(w.deck) < 14:
                a = ArmyScene(app, ms)
                app.push(a)
                a.recruit(cid)
                app.pop()
                return True
    # 4) zagony, wyprawy i bitwa finałowa
    if w.raids and w.res["food"] >= 3:
        ms.intercept(tuple(w.raids[0]["pos"]))
        return True
    for pos, c in w.camps.items():
        if not c["beaten"] and w.res["food"] >= 4 and len(w.deck) >= 8:
            ms.attack_camp(pos)
            return True
    if w.final_available() and not ms.final_lock and (len(w.deck) >= 9 or w.turn > w.max_turns - 4):
        ms.final_battle()
        return True
    ms.end_turn()
    return True


def step(app, stats):
    top = app.top()
    if isinstance(top, Dialogue):
        it = top.cur()
        if it.get("choices") and top.result is None:
            top.choose(random.randrange(len(it["choices"])))
        else:
            top.chars = 10 ** 6
            top.next()
    elif isinstance(top, Quiz):
        k = top.ok if random.random() < 0.8 else (top.ok + 1) % len(top.answers)
        if k in top.removed:
            k = top.ok
        top.pick(k)
        top.done()
    elif isinstance(top, Info):
        top.close(None)
    elif isinstance(top, TechScene):
        app.pop()
    elif isinstance(top, Battle):
        if top.phase == "intro":
            top.start_question()
        elif top.phase == "choose":
            free = [t for t in top.tactics if t not in top.used_tactics]
            if free and random.random() < 0.3:
                top.use_tactic(free[0])
                return True
            if top.phase != "choose":
                return True
            best = max(range(len(top.hand)), key=lambda i: (lambda r: r[3] - r[2])(resolve(top.hand[i], top.ecard, top.bonus, top.terrain, top.rmods)))
            top.play(best)
        elif top.phase == "resolve":
            top.apply_result()
        elif top.phase == "end":
            stats["battles"] += 1
            stats["won"] += bool(top.result)
            top.finish()
    elif isinstance(top, MapScene):
        top.update(0.016)
        if app.top() is top:
            bot_map(app, top)
    elif isinstance(top, ChronicleScene):
        top.chars = 10 ** 6
        top.go()
    elif isinstance(top, VictoryScene):
        print("  wygrany rozdział", top.w.idx, "tura", top.w.turn, "res", top.w.res, "talia", len(top.w.deck),
              "utrzymanie", top.w.upkeep(), flush=True)
        stats["chapters"].append((top.w.idx, top.w.turn, top.stars))
        top.next()
    elif isinstance(top, DefeatScene):
        stats["defeats"] += 1
        print("  porażka:", top.idx, top.text[:50], flush=True)
        top.retry()
    elif isinstance(top, (MenuScene, ChapterSelectScene)):
        if stats.get("bonus"):
            return False
        app.replace(ChronicleScene(app, 0))
    elif isinstance(top, EndingScene):
        return False
    # rysowanie co jakiś czas – wyłapuje błędy w kodzie rysującym
    stats["n"] += 1
    if stats["n"] % 20 == 0:
        app.draw()
    return True


def run(seed):
    random.seed(seed)
    app = App(headless=True)
    app.save = {"unlocked": 0, "completed": [], "techs": [], "scores": {}, "trudnosc": int(os.environ.get("TRUDNOSC", "1"))}
    app.stack = [MenuScene(app)]
    stats = {"n": 0, "battles": 0, "won": 0, "defeats": 0, "chapters": []}
    for i in range(200000):
        if not step(app, stats):
            break
        if i % 3000 == 0 and i:
            t = app.top()
            print("  ...", i, type(t).__name__, getattr(getattr(t, "w", None), "idx", ""), getattr(getattr(t, "w", None), "turn", ""), flush=True)
        if stats["defeats"] > 12:
            raise SystemExit("Za dużo porażek – balans?")
    else:
        raise SystemExit("Bot utknął: " + type(app.top()).__name__)
    assert isinstance(app.top(), EndingScene)
    assert app.save["completed"] == [0, 1, 2, 3, 4, 5]
    # rozdziały dodatkowe
    stats["bonus"] = True
    for idx in (6, 7, 8):
        app.stack = [ChronicleScene(app, idx)]
        for i in range(200000):
            if not step(app, stats):
                break
            if stats["defeats"] > 12:
                raise SystemExit("Za dużo porażek – balans?")
    print(f"seed {seed}: rozdziały (idx, tura, gwiazdki) {stats['chapters']}, bitwy {stats['won']}/{stats['battles']}, porażki misji {stats['defeats']}")
    assert app.save["completed"] == list(range(9)), app.save["completed"]


if __name__ == "__main__":
    for s in range(int(sys.argv[1]) if len(sys.argv) > 1 else 3):
        run(s)
    print("OK – kampania przechodzi od początku do końca.")
