# -*- coding: utf-8 -*-
"""Stan rozgrywki: mapa 30x30, zasoby, budynki, technologie, cele misji."""
import math
import random

from . import data

N = 30


def _noise(seed, scale=5):
    r = random.Random(seed)
    g = [[r.random() for _ in range(N // scale + 3)] for _ in range(N // scale + 3)]

    def at(x, y):
        fx, fy = x / scale, y / scale
        ix, iy = int(fx), int(fy)
        tx, ty = fx - ix, fy - iy
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = g[iy][ix] * (1 - tx) + g[iy][ix + 1] * tx
        b = g[iy + 1][ix] * (1 - tx) + g[iy + 1][ix + 1] * tx
        return a * (1 - ty) + b * ty
    return [[at(x, y) * 0.75 + r.random() * 0.25 for x in range(N)] for y in range(N)]


def _line(a, b):
    (x0, y0), (x1, y1) = a, b
    pts = []
    steps = max(abs(x1 - x0), abs(y1 - y0)) * 2 + 1
    last = None
    for i in range(steps + 1):
        t = i / steps
        p = (round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t))
        if last and p[0] != last[0] and p[1] != last[1]:
            pts.append((p[0], last[1]))  # spójność 4-kierunkowa
        if p != last:
            pts.append(p)
        last = p
    return pts


def generate_map(cfg):
    r = random.Random(cfg["seed"])
    terr = [["grass"] * N for _ in range(N)]
    nf = _noise(cfg["seed"] + 1)
    nh = _noise(cfg["seed"] + 2, 4)
    flat_f = sorted(v for row in nf for v in row)
    flat_h = sorted(v for row in nh for v in row)
    tf = flat_f[int(len(flat_f) * (1 - cfg["forest"]))]
    th = flat_h[int(len(flat_h) * (1 - cfg["hills"]))]
    for y in range(N):
        for x in range(N):
            if nh[y][x] >= th:
                terr[y][x] = "hills"
            elif nf[y][x] >= tf:
                terr[y][x] = "forest"
    river = set()
    pts = cfg.get("river", [])
    for i in range(len(pts) - 1):
        for (x, y) in _line(pts[i], pts[i + 1]):
            if 0 <= x < N and 0 <= y < N:
                river.add((x, y))
    for (lx, ly, lr) in cfg.get("lakes", []):
        for y in range(N):
            for x in range(N):
                d = math.hypot(x - lx, (y - ly) * 1.1)
                if d <= lr + 0.3:
                    terr[y][x] = "water"
                elif d <= lr + 1.3 and terr[y][x] != "hills" and r.random() < 0.6:
                    terr[y][x] = "marsh"
    for (x, y) in river:
        terr[y][x] = "water"
    cx, cy = cfg["capital"]
    # okolica stolicy
    for y in range(N):
        for x in range(N):
            d = max(abs(x - cx), abs(y - cy))
            if d <= 1 and terr[y][x] != "water":
                terr[y][x] = "grass"
            elif d <= 3 and terr[y][x] == "grass" and r.random() < 0.35:
                terr[y][x] = "field"
    terr[cy][cx] = "grass"

    def ensure(kind, count, rad):
        cells = [(x, y) for y in range(cy - rad, cy + rad + 1) for x in range(cx - rad, cx + rad + 1)
                 if 0 <= x < N and 0 <= y < N and max(abs(x - cx), abs(y - cy)) >= 2]
        have = sum(1 for (x, y) in cells if terr[y][x] == kind)
        r.shuffle(cells)
        for (x, y) in cells:
            if have >= count:
                break
            if terr[y][x] in ("grass", "field"):
                terr[y][x] = kind
                have += 1
    ensure("forest", 6, 4)
    ensure("hills", 4, 4)
    # drogi do obozów i zabytków
    targets = [c[0] for c in cfg.get("camps", [])] + [l[0] for l in cfg.get("landmarks", [])]
    for t in targets:
        for (x, y) in _line((cx, cy), t)[2:-1]:
            if terr[y][x] in ("grass", "field", "forest", "marsh"):
                terr[y][x] = "road"
    for (pos, *_rest) in cfg.get("camps", []) + cfg.get("landmarks", []):
        x, y = pos
        if terr[y][x] == "water":
            terr[y][x] = "grass"
    variants = [[r.randrange(4) for _ in range(N)] for _ in range(N)]
    return terr, variants, river


class World:
    def __init__(self, chapter_idx, techs=()):
        self.ch = data.CHAPTERS[chapter_idx]
        self.idx = chapter_idx
        self.epoch = self.ch["epoch"]
        cfg = self.ch["map"]
        self.terr, self.var, self.river = generate_map(cfg)
        self.res = dict(self.ch["start_res"])
        self.turn = 1
        self.max_turns = self.ch["turns"]
        self.buildings = {}            # (x,y) -> typ
        self.cap = tuple(cfg["capital"])
        self.buildings[self.cap] = "grod"
        self.techs = set(t for t in techs if data.TECHS[t]["epoch"] <= self.epoch)
        self.camps = {}
        for (pos, cid, name, deck) in cfg.get("camps", []):
            fac = "mg" if cid == "zwiad" else ("tz" if any(c.endswith("_z") for c in deck) else "en")
            self.camps[tuple(pos)] = {"id": cid, "name": name, "deck": deck, "faction": fac, "beaten": False}
        self.landmarks = {tuple(p): (n, t) for (p, n, t) in cfg.get("landmarks", [])}
        self.deck = list(self.ch["start_deck"])
        self.recruited_this_turn = 0
        self.tech_locked = set()       # zagadki zablokowane do następnej tury
        self.done = set()              # zrealizowane cele (indeksy)
        self.final_won = False
        self.morale_bonus = 0
        self.stats = {"quiz_ok": 0, "quiz_all": 0, "battles": 0}
        self.dirty = True
        self.update_territory()

    # ------------------------------------------------------------ terytorium
    def update_territory(self):
        t = set()
        for (x, y), b in self.buildings.items():
            rad = 4 if b == "grod" else data.BUILDINGS.get(b, {}).get("radius", 2)
            for yy in range(y - rad, y + rad + 1):
                for xx in range(x - rad, x + rad + 1):
                    if 0 <= xx < N and 0 <= yy < N and abs(xx - x) + abs(yy - y) <= rad + 1:
                        t.add((xx, yy))
        self.territory = t
        self.dirty = True

    def near_water(self, x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                xx, yy = x + dx, y + dy
                if 0 <= xx < N and 0 <= yy < N and self.terr[yy][xx] == "water":
                    return True
        return False

    # ------------------------------------------------------------ ekonomia
    def has(self, cost):
        return all(self.res.get(k, 0) >= v for k, v in (cost or {}).items())

    def pay(self, cost):
        for k, v in (cost or {}).items():
            self.res[k] -= v

    def tech_cost(self, tid):
        c = data.TECHS[tid]["cost"]
        if "akademia" in self.techs:
            return {k: max(1, int(math.ceil(v * 0.75))) for k, v in c.items()}
        return dict(c)

    def building_prod(self, b):
        p = dict(data.BUILDINGS[b]["prod"]) if b != "grod" else {"food": 2, "wood": 2, "silver": 1}
        if b == "pole":
            p["food"] += ("radlo" in self.techs) + ("trojpolowka" in self.techs)
        if b == "targ":
            p["silver"] += ("denar" in self.techs) + 2 * ("prawo_magd" in self.techs)
        if b == "kamieniolom" and "cegla" in self.techs:
            p["stone"] += 1
        return p

    def production(self):
        tot = {k: 0 for k in data.RES_ORDER}
        for b in self.buildings.values():
            for k, v in self.building_prod(b).items():
                tot[k] += v
        return tot

    def build_cost(self, kind):
        """Każdy kolejny budynek tego samego typu jest o 25% droższy (lepsze miejsca już zajęte!)."""
        n = self.count(kind)
        return {k: int(math.ceil(v * (1 + 0.25 * n))) for k, v in data.BUILDINGS[kind]["cost"].items()}

    def can_build(self, kind, pos):
        """Zwraca (ok, powód)."""
        b = data.BUILDINGS[kind]
        x, y = pos
        if pos in self.buildings or pos in self.camps or pos in self.landmarks:
            return False, "Pole zajęte."
        if pos not in self.territory:
            return False, "Poza granicami księstwa."
        if b.get("req") and b["req"] not in self.techs:
            return False, "Wymaga technologii: " + data.TECHS[b["req"]]["name"]
        if self.terr[y][x] not in b["terrain"]:
            names = {"grass": "łąka", "field": "pole", "forest": "las", "hills": "wzgórza", "road": "droga", "marsh": "mokradła"}
            return False, "Teren: " + ", ".join(names[t] for t in b["terrain"])
        if b.get("near_water") and not self.near_water(x, y):
            return False, "Musi stać przy wodzie."
        if not self.has(self.build_cost(kind)):
            return False, "Brak zasobów."
        return True, ""

    def build(self, kind, pos):
        self.pay(self.build_cost(kind))
        self.buildings[pos] = kind
        self.update_territory()

    def count(self, kind):
        return sum(1 for b in self.buildings.values() if b == kind)

    def defense_bonus(self, defense_battle):
        m = 0
        if "grod_walowy" in self.techs:
            m += 2
        if "most" in self.techs:
            m += 3
        if defense_battle:
            m += self.count("palisada") * data.BUILDINGS["palisada"]["defense"]
            m += self.count("zamek") * data.BUILDINGS["zamek"]["defense"]
        return m + self.morale_bonus

    def available_cards(self):
        out = []
        for cid, c in data.CARDS.items():
            if c.get("cost") is None or c.get("faction") not in ("pl", "lt"):
                continue
            if c.get("req") and c["req"] not in self.techs:
                continue
            out.append(cid)
        return out

    def recruit_slots(self):
        return self.count("koszary") - self.recruited_this_turn

    def end_turn(self):
        prod = self.production()
        for k, v in prod.items():
            self.res[k] += v
        self.turn += 1
        self.recruited_this_turn = 0
        self.tech_locked.clear()
        self.dirty = True
        return prod

    def apply(self, eff, halve_bad=False):
        msgs = []
        for k, v in eff.items():
            if k in self.res:
                if v < 0 and halve_bad and "statut" in self.techs:
                    v = -((-v) // 2)
                self.res[k] = max(0, self.res[k] + v)
            elif k == "card":
                self.deck.append(v)
                msgs.append("Nowa karta: " + data.CARDS[v]["name"])
            elif k == "morale":
                self.morale_bonus += v
        return msgs

    # ------------------------------------------------------------ cele
    def objective_state(self, i):
        o = self.ch["objectives"][i]
        k = o[0]
        if k == "build":
            have = self.count(o[1])
            return have >= o[2], f"Zbuduj: {data.BUILDINGS[o[1]]['name']} ({min(have, o[2])}/{o[2]})"
        if k == "res":
            have = self.res[o[1]]
            return have >= o[2], f"Zgromadź: {data.RES_NAMES[o[1]]} ({min(have, o[2])}/{o[2]})"
        if k == "tech":
            return o[1] in self.techs, f"Odkryj: {data.TECHS[o[1]]['name']}"
        if k == "camp":
            c = next(c for c in self.camps.values() if c["id"] == o[1])
            return c["beaten"], f"Rozbij: {c['name']}"
        if k == "final":
            return self.final_won, "Bitwa: " + self.ch["final"]["name"]
        return False, "?"

    def refresh_objectives(self):
        for i in range(len(self.ch["objectives"])):
            if i not in self.done and self.objective_state(i)[0]:
                self.done.add(i)

    def final_index(self):
        for i, o in enumerate(self.ch["objectives"]):
            if o[0] == "final":
                return i
        return None

    def final_available(self):
        fi = self.final_index()
        if fi is None or self.final_won:
            return False
        return all(i in self.done for i in range(fi))

    def complete(self):
        if self.ch.get("siege_turn") and self.final_won:
            return True
        return len(self.done) == len(self.ch["objectives"])
