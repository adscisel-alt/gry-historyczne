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
    for pts in (cfg.get("river", []), cfg.get("river2", [])):
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


DIFF = {
    0: {"name": "Łatwy", "desc": "dla młodszych (10–11 lat): więcej zasobów i tur, słabsi wrogowie, zawsze podpowiedź",
        "res": 1.35, "turns": 6, "enemy": 0.8, "hidden": 0.0, "raid": 1.5, "hints": 1},
    1: {"name": "Normalny", "desc": "zrównoważona rozgrywka", "res": 1.0, "turns": 0, "enemy": 1.0, "hidden": 0.3,
        "raid": 1.0, "hints": 0},
    2: {"name": "Trudny", "desc": "dla starszych (13–14 lat): mniej zasobów, silniejsi wrogowie, częstsze zagony",
        "res": 0.85, "turns": -4, "enemy": 1.15, "hidden": 0.5, "raid": 0.7, "hints": 0},
}


class World:
    def __init__(self, chapter_idx, techs=(), diff=1):
        self.ch = data.CHAPTERS[chapter_idx]
        self.diff = diff               # 0 – łatwy, 1 – normalny, 2 – trudny
        self.deserted = None
        self.idx = chapter_idx
        self.epoch = self.ch["epoch"]
        cfg = self.ch["map"]
        self.terr, self.var, self.river = generate_map(cfg)
        mult = DIFF[diff]["res"]
        self.res = {k: int(round(v * mult)) for k, v in self.ch["start_res"].items()}
        self.turn = 1
        self.max_turns = self.ch["turns"] + DIFF[diff]["turns"]
        if self.ch.get("siege_turn"):
            self.max_turns = max(self.max_turns, self.ch["siege_turn"] + 2)
        self.buildings = {}            # (x,y) -> typ
        self.cap = tuple(cfg["capital"])
        self.buildings[self.cap] = "grod"
        self.techs = set(t for t in techs if data.TECHS[t]["epoch"] <= self.epoch)
        self.camps = {}
        for (pos, cid, name, deck) in cfg.get("camps", []):
            fac = data.CARDS[deck[0]]["faction"]
            self.camps[tuple(pos)] = {"id": cid, "name": name, "deck": deck, "faction": fac, "beaten": False}
        self.landmarks = {tuple(p): (n, t) for (p, n, t) in cfg.get("landmarks", [])}
        self.deck = list(self.ch["start_deck"])
        self.recruited_this_turn = 0
        self.tech_locked = set()       # zagadki zablokowane do następnej tury
        self.done = set()              # zrealizowane cele (indeksy)
        self.final_won = False
        self.morale_bonus = 0
        self.stats = {"quiz_ok": 0, "quiz_all": 0, "battles": 0}
        self.raids = []
        self.extra = {}
        self.dirty = True
        self.update_territory()

    # ------------------------------------------------------------ zapis gry
    def to_dict(self):
        return {
            "idx": self.idx, "res": self.res, "turn": self.turn,
            "buildings": [[x, y, b] for (x, y), b in self.buildings.items()],
            "techs": sorted(self.techs), "beaten": [c["id"] for c in self.camps.values() if c["beaten"]],
            "deck": self.deck, "recruited": self.recruited_this_turn, "locked": sorted(self.tech_locked),
            "done": sorted(self.done), "final_won": self.final_won, "morale": self.morale_bonus, "stats": self.stats,
            "extra": getattr(self, "extra", {}), "diff": self.diff, "raids": getattr(self, "raids", []),
        }

    @classmethod
    def from_dict(cls, d):
        w = cls(d["idx"], diff=d.get("diff", 1))
        w.res = dict(d["res"])
        w.raids = d.get("raids", [])
        w.turn = d["turn"]
        w.buildings = {(x, y): b for x, y, b in d["buildings"]}
        w.techs = set(d["techs"])
        for c in w.camps.values():
            c["beaten"] = c["id"] in d["beaten"]
        w.deck = list(d["deck"])
        w.recruited_this_turn = d.get("recruited", 0)
        w.tech_locked = set(d.get("locked", []))
        w.done = set(d.get("done", []))
        w.final_won = d.get("final_won", False)
        w.morale_bonus = d.get("morale", 0)
        w.stats = d.get("stats", w.stats)
        w.extra = d.get("extra", {})
        w.update_territory()
        return w

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
        if data.TECH_FX.get("cheap") in self.techs:
            return {k: max(1, int(math.ceil(v * 0.75))) for k, v in c.items()}
        return dict(c)

    def building_prod(self, b):
        p = dict(data.BUILDINGS[b]["prod"]) if b != "grod" else {"food": 2, "wood": 2, "silver": 1}
        for tech, per_building in data.TECH_FX.get("prod", {}).items():
            if tech in self.techs:
                for k, v in per_building.get(b, {}).items():
                    p[k] = p.get(k, 0) + v
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
            return False, "Poza granicami państwa."
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
        for tech, v in data.TECH_FX.get("morale", {}).items():
            if tech in self.techs:
                m += v
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

    def upkeep(self):
        """Utrzymanie wojska: każda karta ponad podstawową talię zjada 1 żywności na turę."""
        free = len(self.ch["start_deck"]) + (2 if self.diff == 0 else 0)
        return max(0, len(self.deck) - free)

    def end_turn(self):
        prod = self.production()
        prod["food"] -= self.upkeep()
        self.deserted = None
        for k, v in prod.items():
            self.res[k] += v
        if self.res["food"] < 0:
            self.res["food"] = 0
            extra = [c for c in self.deck if data.CARDS[c].get("cost")]
            if extra and len(self.deck) > len(self.ch["start_deck"]):
                lost = extra[-1]
                self.deck.remove(lost)
                self.deserted = data.CARDS[lost]["name"]
        self.turn += 1
        self.recruited_this_turn = 0
        self.tech_locked.clear()
        self.dirty = True
        return prod

    def apply(self, eff, halve_bad=False):
        msgs = []
        for k, v in eff.items():
            if k in self.res:
                if v < 0 and halve_bad and data.TECH_FX.get("halve_bad") in self.techs:
                    v = -((-v) // 2)
                self.res[k] = max(0, self.res[k] + v)
            elif k == "card":
                self.deck.append(v)
                msgs.append("Nowa karta: " + data.CARDS[v]["name"])
            elif k == "morale":
                self.morale_bonus += v
            elif k == "beat_camp":
                for c in self.camps.values():
                    if c["id"] == v:
                        c["beaten"] = True
                self.dirty = True
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


# ---------------------------------------------------------------- zagony
def _cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def raid_config(w):
    return data.RAIDS.get(w.idx)


def raid_due(w):
    cfg = raid_config(w)
    if not cfg or w.final_won:
        return False
    every = max(2, int(round(cfg["every"] * DIFF[w.diff]["raid"])))
    return w.turn >= cfg["start"] and (w.turn - cfg["start"]) % every == 0 and len(w.raids) < 2


def spawn_raid(w):
    cfg = raid_config(w)
    origins = [p for p, c in w.camps.items() if not c["beaten"]]
    if not origins:
        edge = [(x, y) for x in range(N) for y in range(N) if (x in (0, N - 1) or y in (0, N - 1))
                and w.terr[y][x] != "water"]
        edge.sort(key=lambda p: -_cheb(p, w.cap))
        origins = edge[:6]
    start = origins[w.turn % len(origins)]
    r = {"pos": list(start), "name": cfg["name"], "faction": cfg["faction"], "unit": cfg["unit"],
         "deck": list(cfg["deck"]), "id": w.turn}
    w.raids.append(r)
    return r


def raid_step(w, pos):
    """Krok w stronę grodu, omijając wodę."""
    best, bd = None, None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == dy == 0:
                continue
            x, y = pos[0] + dx, pos[1] + dy
            if not (0 <= x < N and 0 <= y < N) or w.terr[y][x] == "water":
                continue
            d = math.hypot(x - w.cap[0], y - w.cap[1])
            if bd is None or d < bd:
                best, bd = (x, y), d
    return best or tuple(pos)


def move_raids(w):
    """Przesuwa zagony o 2 pola. Zwraca listę zdarzeń: (rodzaj, zagon, dodatkowe)."""
    events = []
    for r in list(w.raids):
        for _ in range(2):
            pos = tuple(r["pos"])
            # obrona: palisada lub zamek obok
            guard = [p for p, b in w.buildings.items() if b in ("palisada", "zamek") and _cheb(p, pos) <= 1]
            if guard:
                w.raids.remove(r)
                events.append(("repelled", r, data.BUILDINGS[w.buildings[guard[0]]]["name"]))
                break
            if _cheb(pos, w.cap) <= 1:
                w.raids.remove(r)
                events.append(("siege", r, None))
                break
            nxt = raid_step(w, pos)
            r["pos"] = list(nxt)
            b = w.buildings.get(nxt)
            if b and b not in ("grod", "palisada", "zamek"):
                del w.buildings[nxt]
                w.update_territory()
                events.append(("burned", r, data.BUILDINGS[b]["name"]))
                break
    w.dirty = True
    return events


def raid_eta(w, r):
    return max(1, (_cheb(r["pos"], w.cap) - 1 + 1) // 2)
