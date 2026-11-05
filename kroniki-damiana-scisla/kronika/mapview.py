# -*- coding: utf-8 -*-
"""Widok mapy izometrycznej 30x30 z panelem doradcy."""
import random
import pygame

from . import data, gfx, ui, audio, storage
from .gfx import TW, TH
from .world import N, World, raid_due, spawn_raid, move_raids, raid_eta
from .modals import Scene, Dialogue, Quiz, Info, W, H
from .battle import Battle

VIEW = pygame.Rect(0, 44, 980, 676)
PANEL = pygame.Rect(980, 44, 300, 676)
OX = N * TW // 2 + 32
OY = 90
MAP_W, MAP_H = N * TW + 64, N * TH + 140

TERR_NAMES = {"grass": "Łąka", "forest": "Las", "hills": "Wzgórza", "water": "Woda", "marsh": "Mokradła",
              "field": "Pole", "road": "Trakt"}


def tile_center(x, y):
    return OX + (x - y) * TW // 2, OY + (x + y) * TH // 2 + TH // 2


class MapRenderer:
    """Rysuje mapę świata na dużej powierzchni (używane też w menu jako tło)."""

    def __init__(self, world):
        self.w = world
        self.surf = pygame.Surface((MAP_W, MAP_H))
        self.frame = 0
        self.timer = 0
        self.render()

    def render(self):
        w = self.w
        s = self.surf
        s.fill((24, 30, 20))
        for y in range(N):
            for x in range(N):
                cx, cy = tile_center(x, y)
                t = w.terr[y][x]
                s.blit(gfx.tile(t, w.var[y][x], self.frame % 3 if t == "water" else 0), (cx - TW // 2, cy - TH // 2))
        # granica księstwa
        gold = (250, 220, 110)
        for (x, y) in w.territory:
            cx, cy = tile_center(x, y)
            top, right, bot, left = (cx, cy - TH // 2), (cx + TW // 2, cy), (cx, cy + TH // 2), (cx - TW // 2, cy)
            if (x, y - 1) not in w.territory:
                pygame.draw.line(s, gold, top, right, 2)
            if (x + 1, y) not in w.territory:
                pygame.draw.line(s, gold, right, bot, 2)
            if (x, y + 1) not in w.territory:
                pygame.draw.line(s, gold, bot, left, 2)
            if (x - 1, y) not in w.territory:
                pygame.draw.line(s, gold, left, top, 2)
        # obiekty w kolejności głębokości
        order = sorted(((x, y) for y in range(N) for x in range(N)), key=lambda p: (p[0] + p[1], p[0]))
        for (x, y) in order:
            cx, cy = tile_center(x, y)
            pos = (x, y)
            t = w.terr[y][x]
            v = w.var[y][x]
            if pos in w.buildings:
                b = w.buildings[pos]
                img = gfx.building(b, w.epoch if b == "grod" else 0, self.frame % 2)
                s.blit(img, (cx - img.get_width() // 2, cy - (gfx.BUILD_H - gfx.HTH // 2) * 2))
                if b == "grod":
                    for k, (ux, uy) in enumerate([(-40, 18), (-26, 24), (30, 20)]):
                        u = gfx.unit_big(["spear", "bow", "horse"][k], "pl", 1)
                        s.blit(pygame.transform.scale(u, (36, 33)), (cx + ux - 18, cy + uy - 30))
                    tk = pygame.transform.scale(gfx.hero_figure(1), (26, 42))
                    s.blit(tk, (cx + 6, cy + 10 - 42))
                continue
            if pos in w.camps:
                c = w.camps[pos]
                if not c["beaten"]:
                    img = gfx.camp(c["faction"], self.frame % 2)
                    s.blit(img, (cx - img.get_width() // 2, cy - (gfx.BUILD_H - gfx.HTH // 2) * 2))
                else:
                    img = gfx.building("pole", 0)
                    pygame.draw.line(s, (70, 50, 30), (cx, cy), (cx, cy - 26), 2)
                    pygame.draw.polygon(s, (230, 230, 230), [(cx + 1, cy - 26), (cx + 16, cy - 22), (cx + 1, cy - 18)])
                    pygame.draw.polygon(s, (200, 30, 40), [(cx + 1, cy - 22), (cx + 16, cy - 22), (cx + 1, cy - 18)])
                continue
            if pos in w.landmarks:
                img = gfx.landmark(self.frame % 2)
                s.blit(img, (cx - img.get_width() // 2, cy - (gfx.BUILD_H - gfx.HTH // 2) * 2))
                continue
            if t == "forest":
                for k, (dx, dy) in enumerate([(-12, -3), (10, -1), (-1, 6)][: 2 + v % 2]):
                    img = gfx.tree((v + k) % 6)
                    s.blit(img, (cx + dx - 16, cy + dy - 48))
            elif t == "hills":
                img = gfx.rocks(v)
                s.blit(img, (cx - 24, cy - 22))
            elif t == "marsh" and v % 2 == 0:
                img = gfx.reeds(v)
                s.blit(img, (cx - 16, cy - 18))
            elif t == "grass" and v == 3 and (x * 7 + y) % 5 == 0:
                img = gfx.tree(1 + (x % 2))
                s.blit(img, (cx - 16, cy - 48))
        w.dirty = False

    def tick(self, dt):
        self.timer += dt
        if self.timer > 0.5:
            self.timer = 0
            self.frame += 1
            self.w.dirty = True
        if self.w.dirty:
            self.render()


class MapScene(Scene):
    def __init__(self, app, chapter_idx, world=None):
        super().__init__(app)
        self.w = world or World(chapter_idx, app.save.get("techs", []), app.save.get("trudnosc", 1))
        app.chapter = self.w.idx
        self.ch = self.w.ch
        self.r = MapRenderer(self.w)
        cx, cy = tile_center(*self.w.cap)
        self.cam = [cx - VIEW.w // 2, cy - VIEW.h // 2]
        self.hover = None
        self.sel = self.w.cap
        self.queue = []
        self.floats = []
        self.drag = None
        self.finished = False
        self.final_lock = False
        self.tip_text = ""
        self.t = 0
        self.make_buttons()
        self.update_tip()
        audio.start_music(f"music_{self.w.epoch}")
        if world is None:
            self.queue.append(lambda: self.app.push(Dialogue(self.app, [{"who": w, "text": t} for w, t in self.ch["dialogue_start"]], self.w)))
        else:
            self.floats.append(["Wczytano zapis – tura %d" % self.w.turn, VIEW.centerx, VIEW.y + 60, (255, 240, 160), 0])

    # ------------------------------------------------------------ współrzędne
    def screen_to_tile(self, pos):
        mx, my = pos
        if not VIEW.collidepoint(pos):
            return None
        px_ = mx - VIEW.x + self.cam[0] - OX
        py_ = my - VIEW.y + self.cam[1] - OY
        fx = (py_ / (TH / 2) + px_ / (TW / 2)) / 2
        fy = (py_ / (TH / 2) - px_ / (TW / 2)) / 2
        x, y = int(fx // 1), int(fy // 1)
        if 0 <= x < N and 0 <= y < N:
            return (x, y)
        return None

    def tile_screen(self, x, y):
        cx, cy = tile_center(x, y)
        return cx - self.cam[0] + VIEW.x, cy - self.cam[1] + VIEW.y

    # ------------------------------------------------------------ panel
    def make_buttons(self):
        self.buttons = []
        p = PANEL
        bw = (p.w - 30) // 2
        y = p.bottom - 150
        self.buttons.append(ui.Button((p.x + 10, y, bw, 38), "Technologie", self.open_tech, 15, icon=gfx.icon("tech", 2), key=pygame.K_t))
        self.buttons.append(ui.Button((p.x + 20 + bw, y, bw, 38), "Wojsko", self.open_army, 15, icon=gfx.icon("army", 2), key=pygame.K_w))
        self.buttons.append(ui.Button((p.x + 10, y + 46, bw, 38), "Postacie", self.open_gallery, 15, icon=gfx.icon("chronicle", 2), key=pygame.K_k))
        self.buttons.append(ui.Button((p.x + 20 + bw, y + 46, bw, 38), "Menu", self.pause, 15, key=pygame.K_ESCAPE))
        self.buttons.append(ui.Button((p.x + 10, y + 92, p.w - 20, 46), "Koniec tury ▶", self.end_turn, 19,
                                      icon=gfx.icon("turn", 2), color=(70, 100, 50), key=pygame.K_SPACE))
        if self.w.final_available() and not self.final_lock:
            self.buttons.append(ui.Button((p.x + 10, y - 52, p.w - 20, 44), "⚔ Rada wojenna!", self.final_battle, 17, color=(150, 40, 36)))
        self.make_tile_buttons()

    def make_tile_buttons(self):
        self.tile_buttons = []
        if self.sel is None:
            return
        pos = self.sel
        x, y = pos
        p = PANEL
        y0 = 360
        if self.raid_at(pos):
            self.tile_buttons.append(ui.Button((p.x + 10, y0 + 40, p.w - 20, 40), "Przechwyć zagon (−3 żywności)",
                                               lambda: self.intercept(pos), 15, color=(150, 40, 36),
                                               enabled=self.w.res["food"] >= 3))
            return
        if pos in self.w.camps and not self.w.camps[pos]["beaten"]:
            self.tile_buttons.append(ui.Button((p.x + 10, y0 + 40, p.w - 20, 40), "Doradź wyprawę (−4 żywności)",
                                               lambda: self.attack_camp(pos), 15, color=(150, 40, 36),
                                               enabled=self.w.res["food"] >= 4))
            return
        if pos in self.w.landmarks:
            n, t = self.w.landmarks[pos]
            self.tile_buttons.append(ui.Button((p.x + 10, y0 + 40, p.w - 20, 38), "Przeczytaj w kronice",
                                               lambda: self.app.push(Info(self.app, n, t, gfx.landmark(0))), 15))
            return
        if pos in self.w.buildings or pos not in self.w.territory or self.w.terr[y][x] == "water":
            return
        t = self.w.terr[y][x]
        k = 0
        for kind, b in data.BUILDINGS.items():
            if t not in b["terrain"]:
                continue
            if b.get("req") and data.TECHS[b["req"]]["epoch"] > self.w.epoch:
                continue
            ok, why = self.w.can_build(kind, pos)
            bt = ui.Button((p.x + 10, y0 + 30 + k * 34, p.w - 20, 30), b["name"], lambda kind=kind: self.build(kind), 14, enabled=ok)
            bt.kind = kind
            bt.why = why
            bt.align = "left"
            self.tile_buttons.append(bt)
            k += 1
            if k >= 6:
                break

    def build(self, kind):
        if self.sel is None:
            return
        ok, why = self.w.can_build(kind, self.sel)
        if not ok:
            return
        self.w.build(kind, self.sel)
        audio.play("build")
        sx, sy = self.tile_screen(*self.sel)
        self.floats.append([data.BUILDINGS[kind]["name"] + "!", sx, sy - 60, (255, 240, 160), 0])
        self.after_change()

    def after_change(self):
        self.w.refresh_objectives()
        self.update_tip()
        self.make_buttons()

    # ------------------------------------------------------------ akcje
    def open_tech(self):
        from .scenes import TechScene
        self.app.push(TechScene(self.app, self))

    def open_army(self):
        from .scenes import ArmyScene
        self.app.push(ArmyScene(self.app, self))

    def open_gallery(self):
        from .scenes import GalleryScene
        self.app.push(GalleryScene(self.app, highlight=self.chapter_chars()))

    def chapter_chars(self):
        ws = set()
        for w, _ in self.ch["dialogue_start"]:
            ws.add(w)
        for v in self.ch["scripted"].values():
            if v[0] != "decision":
                ws.add(v[0])
        ws.discard("damian")
        return ws

    def save_game(self):
        storage.save("gra", self.w.to_dict())

    @staticmethod
    def has_save():
        return storage.load("gra") is not None

    @classmethod
    def load_game(cls, app):
        d = storage.load("gra")
        return cls(app, d["idx"], World.from_dict(d))

    def pause(self):
        def to_menu():
            self.save_game()
            from .scenes import MenuScene
            self.app.replace(MenuScene(self.app))
        from .scenes import help_text
        self.app.push(Info(self.app, "Przerwa w kronice",
                           "Gra zapisuje się sama na początku każdej tury, a „Menu główne” zapisuje bieżący stan. "
                           "Wrócisz przyciskiem „Kontynuuj” w menu.\n\n" + help_text(),
                           buttons=[("Zapisz i wyjdź do menu", to_menu), ("Wróć do gry", None)], wide=True))

    def attack_camp(self, pos):
        c = self.w.camps[pos]
        self.w.res["food"] -= 4

        def done(won):
            if won:
                c["beaten"] = True
                self.w.res["silver"] += 8
                self.w.res["wood"] += 4
                self.say("damian", f"{c['name']} rozbity! Łupy: 8 srebra i 4 drewna. Trakt znów bezpieczny.")
            else:
                self.say("damian", "Wycofaliśmy się. Wzmocnij wojsko (Wojsko → werbunek) lub zbadaj nowe technologie i spróbuj ponownie.")
            self.w.dirty = True
            self.after_change()
        self.app.push(Battle(self.app, self.w, c["name"], c["deck"], self.camp_morale(c), False,
                             "forest" if self.w.terr[pos[1]][pos[0]] == "forest" else "field",
                             intro=f"Wojsko księcia wyrusza na {c['name'].lower()}. Kronikarz jedzie z tyłu, na najspokojniejszym koniu w stajni.",
                             on_end=done))

    def raid_at(self, pos):
        for r in self.w.raids:
            if tuple(r["pos"]) == tuple(pos):
                return r
        return None

    def raid_battle(self, r, at_gates=False):
        w = self.w

        def done(won):
            if r in w.raids:
                w.raids.remove(r)
            if won:
                w.res["silver"] += 5
                self.say("damian", f"{r['name']} rozbity! Łupy: 5 srebra. Okoliczne wsie odetchnęły.")
            elif at_gates:
                lost_f, lost_s = w.res["food"] * 2 // 5, w.res["silver"] * 2 // 5
                w.res["food"] -= lost_f
                w.res["silver"] -= lost_s
                self.say("damian", f"{r['name']} złupił podgrodzie: −{lost_f} żywności, −{lost_s} srebra. "
                                   "Zagon odjechał z łupami...")
            else:
                self.say("damian", "Nie udało się przechwycić zagonu – wróg wciąż idzie na gród!")
                w.raids.append(r) if r not in w.raids else None
            w.dirty = True
            self.after_change()
        name = r["name"] + (" pod grodem!" if at_gates else " – przechwycenie")
        intro = ("Zagon dotarł pod gród! Bramy zamknięte, na wałach łucznicy." if at_gates else
                 "Konni gońcy wskazali drogę zagonu. Zastawiamy zasadzkę na trakcie.")
        self.app.push(Battle(self.app, w, name, r["deck"], 10 + 3 * len(r["deck"]) + 2 * w.epoch, at_gates,
                             "grod" if at_gates else "field", intro=intro, on_end=done))

    def intercept(self, pos):
        r = self.raid_at(pos)
        if r and self.w.res["food"] >= 3:
            self.w.res["food"] -= 3
            if r in self.w.raids:
                self.w.raids.remove(r)
            self.raid_battle(r)

    def camp_morale(self, c):
        return 14 + 3 * len(c["deck"]) + 2 * self.w.epoch

    def final_battle(self, forced=False):
        f = self.ch["final"]

        def done(won):
            if won:
                self.w.final_won = True
                self.after_change()
            else:
                if self.ch.get("siege_turn"):
                    self.defeat("Gród padł... Ale kronika jeszcze się nie skończyła – spróbuj ponownie!")
                    return
                self.final_lock = True
                self.say("damian", "Bitwa przegrana, ale wojna trwa. Wojsko musi odpocząć do następnej tury. Zwerbuj posiłki!")
                self.make_buttons()
        self.app.push(Battle(self.app, self.w, f["name"], f["deck"], f["enemy_morale"], f["defense"], f["terrain"],
                             f.get("allies", []), f["intro"], done, siege=bool(self.ch.get("siege_turn"))))

    def say(self, who, text):
        self.app.push(Dialogue(self.app, [{"who": who, "text": text}], self.w))

    def end_turn(self):
        if self.app.top() is not self or self.queue:
            return
        prod = self.w.end_turn()
        self.final_lock = False
        audio.play("coin")
        y = VIEW.y + 30
        for k in data.RES_ORDER:
            if prod[k]:
                self.floats.append([f"+{prod[k]} {data.RES_NAMES[k]}", 120 + data.RES_ORDER.index(k) * 150, y, (255, 240, 160), 0])
        w = self.w
        if self.w.upkeep():
            self.floats.append([f"−{self.w.upkeep()} żywności (utrzymanie wojska)", VIEW.centerx, VIEW.y + 60, (255, 190, 160), 0])
        if w.deserted:
            self.queue.append(lambda d=w.deserted: self.say("damian",
                f"Pusty spichlerz! Oddział „{d}” rozszedł się do domów. Wojsko trzeba żywić – zbuduj więcej pól."))
        for kind, r, extra in move_raids(w):
            if kind == "burned":
                self.queue.append(lambda r=r, e=extra: self.say("damian", f"{r['name']} spalił: {e}! Zagony trzeba przechwytywać, "
                                                                        "zanim dotrą do naszych ziem – albo chronić je palisadą."))
            elif kind == "repelled":
                self.queue.append(lambda r=r, e=extra: self.say("damian", f"{r['name']} rozbił się o nasze umocnienia ({e}). "
                                                                        "Mur nie śpi, nie je i nie dezerteruje!"))
            elif kind == "siege":
                self.queue.append(lambda r=r: self.raid_battle(r, at_gates=True))
        if raid_due(w):
            r = spawn_raid(w)
            self.queue.append(lambda r=r: self.app.push(Dialogue(self.app, [{"who": "damian", "title": "Zagon wroga!",
                "text": f"Zwiadowcy donoszą: {r['name']} wyruszył w stronę grodu! Dotrze za ok. {raid_eta(w, r)} tur. "
                        "Kliknij go na mapie i doradź przechwycenie – albo postaw palisadę na jego drodze."}], w)))
            audio.play("drum")
        self.after_change()
        self.save_game()
        if w.turn > w.max_turns and not w.complete():
            self.defeat("Czas minął! Kronika urywa się w pół zdania... Spróbuj jeszcze raz – tym razem z lepszym planem.")
            return
        sc = self.ch["scripted"].get(w.turn)
        if sc:
            if sc[0] == "decision":
                self.queue.append(lambda sc=sc: self.app.push(Dialogue(self.app, [{"who": "damian", "title": "Decyzja", "text": sc[1], "choices": sc[2]}], w,
                                                                       on_done=self.after_change)))
            else:
                self.queue.append(lambda sc=sc: self.say(sc[0], sc[1]))
        st = self.ch.get("siege_turn")
        if st and w.turn == st and not w.final_won:
            self.queue.append(lambda: self.app.push(Dialogue(self.app, [{"who": "damian", "title": "Oblężenie!", "text":
                "Na horyzoncie dymy i tumany kurzu. Mongołowie otaczają gród! Na mury, wszyscy na mury!"}], w,
                on_done=lambda: self.final_battle(True))))
            audio.play("drum")
        elif not sc and w.turn > 2 and random.random() < 0.33:
            self.queue.append(self.random_event)

    def random_event(self):
        ev = random.choice(data.EVENTS)
        w = self.w

        def special(eff):
            if "battle" in eff:
                def done(won):
                    if won:
                        w.res["silver"] += 6
                        self.say("damian", "Łupieżcy przegnani! Zostawili w popłochu 6 srebra.")
                    else:
                        w.res["food"] = max(0, w.res["food"] - 6)
                        self.say("damian", "Łupieżcy zabrali 6 żywności. Trzeba wzmocnić wojsko.")
                    self.after_change()
                self.app.push(Battle(self.app, w, "Najazd łupieżców", eff["battle"], 16, True, "field",
                                     intro="Banda łupieżców pod grodem! Szybka potyczka – pokażmy im drogę do domu.", on_end=done))
            elif "quiz" in eff:
                q, ans, ok = data.pick_question(w.epoch, self.app.used_q)

                def res(good):
                    w.stats["quiz_all"] += 1
                    if good:
                        w.stats["quiz_ok"] += 1
                        w.res["silver"] += eff["quiz"]
                        self.say("damian", f"Żak oddał {eff['quiz']} srebra i odszedł, mrucząc coś o przemądrzałych kronikarzach.")
                    else:
                        self.say("damian", "Żak się zaśmiał i poszedł dalej. Ale przynajmniej czegoś się nauczyliśmy!")
                    self.after_change()
                from .world import DIFF
                hints = (1 if w.count("kosciol") else 0) + DIFF[w.diff]["hints"]
                self.app.push(Quiz(self.app, "Zakład z żakiem", q, ans, ok, res, hints))
        item = {"who": None, "icon": gfx.event_icon(ev["icon"]), "title": ev["title"], "text": ev["text"],
                "choices": ev["choices"], "special": special}
        self.app.push(Dialogue(self.app, [item], w, on_done=self.after_change))

    def defeat(self, text):
        from .scenes import DefeatScene
        storage.delete("gra")
        self.finished = True
        self.app.replace(DefeatScene(self.app, self.w.idx, text))

    # ------------------------------------------------------------ porady
    def update_tip(self):
        w = self.w
        tips = []
        if w.res["food"] < 6:
            tips.append("Spichlerz pustoszeje! Zbuduj pola uprawne – głodny lud nie pracuje.")
        if w.upkeep() and w.production()["food"] - w.upkeep() < 0:
            tips.append(f"Wojsko zjada {w.upkeep()} żywności na turę, a pola dają za mało! Zbuduj pola albo młyn, "
                        "bo oddziały zaczną dezerterować.")
        if w.count("pole") == 0:
            tips.append("Zacznij od pól: kliknij łąkę w granicach księstwa (złota linia) i wybierz „Pole uprawne”.")
        elif w.count("drwal") == 0:
            tips.append("Drewno przyda się do wszystkiego. Kliknij las w granicach i postaw obóz drwali.")
        if not tips:
            for i, o in enumerate(self.ch["objectives"]):
                if i in w.done:
                    continue
                if o[0] == "tech":
                    t = data.TECHS[o[1]]
                    miss = [data.TECHS[r]["name"] for r in t["req"] if r not in w.techs]
                    tips.append(f"Otwórz Technologie (T) i rozwiąż zagadkę: {t['name']}." + (f" Najpierw: {', '.join(miss)}." if miss else ""))
                elif o[0] == "build":
                    b = data.BUILDINGS[o[1]]
                    if b.get("req") and b["req"] not in w.techs:
                        tips.append(f"„{b['name']}” wymaga technologii: {data.TECHS[b['req']]['name']}.")
                    else:
                        lack = [k for k, v in w.build_cost(o[1]).items() if w.res[k] < v]
                        src = {"food": "Pole uprawne", "wood": "Obóz drwali (w lesie)", "stone": "Kamieniołom (na wzgórzach)", "silver": "Targ"}
                        if lack:
                            tips.append(f"Na „{b['name']}” brakuje: {', '.join(data.RES_NAMES[k].lower() for k in lack)}. "
                                        f"Zbuduj: {', '.join(src[k] for k in lack)}.")
                        else:
                            tips.append(f"Zbuduj: {b['name']}. {b['desc']}")
                elif o[0] == "res":
                    tips.append(f"Potrzeba więcej: {data.RES_NAMES[o[1]]}. Każdy budynek to inwestycja – zwraca się co turę!")
                elif o[0] == "camp":
                    tips.append("Kliknij obóz wroga na mapie i doradź wyprawę. Zabierz silną talię!")
                elif o[0] == "final":
                    if w.final_available():
                        tips.append("Wszystko gotowe! Zwołaj radę wojenną – przycisk w panelu po prawej.")
                    else:
                        tips.append("Wykonaj wcześniejsze zadania, a potem zwołamy radę wojenną.")
                break
        if w.raids:
            r = w.raids[0]
            tips.insert(0, f"{r['name']} idzie na gród (za ok. {raid_eta(w, r)} tur)! Kliknij go i doradź przechwycenie "
                           "albo postaw palisadę na jego drodze.")
        if self.ch.get("siege_turn") and not w.final_won:
            left = self.ch["siege_turn"] - w.turn
            tips.insert(0, f"Do oblężenia zostało tur: {left}! Palisady i zapasy – szybko!")
        if not tips:
            tips.append(random.choice([
                "Ekonomia w pigułce: gdy czegoś brakuje, a chętnych wielu – cena rośnie.",
                "Budynek to inwestycja: płacisz raz, a zyskujesz co turę.",
                "Kronikarz radzi: zapasy na czarną godzinę to nie skąpstwo, to rozsądek.",
            ]))
        self.tip_text = tips[0]

    # ------------------------------------------------------------ pętla
    def handle(self, ev):
        for b in self.buttons + self.tile_buttons:
            if b.handle(ev):
                return True
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.screen_to_tile(ev.pos)
            if self.drag:
                self.cam[0] -= ev.rel[0]
                self.cam[1] -= ev.rel[1]
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 1:
                t = self.screen_to_tile(ev.pos)
                if t:
                    self.sel = t
                    audio.play("click")
                    self.make_buttons()
            elif ev.button in (2, 3):
                self.drag = True
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button in (2, 3):
            self.drag = None
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_c:
            cx, cy = tile_center(*self.w.cap)
            self.cam = [cx - VIEW.w // 2, cy - VIEW.h // 2]
        return False

    def update(self, dt):
        self.t += dt
        self.r.tick(dt)
        keys = pygame.key.get_pressed()
        sp = 520 * dt
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.cam[0] -= sp
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.cam[0] += sp
        if keys[pygame.K_UP]:
            self.cam[1] -= sp
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.cam[1] += sp
        self.cam[0] = max(-200, min(MAP_W - VIEW.w + 200, self.cam[0]))
        self.cam[1] = max(-150, min(MAP_H - VIEW.h + 150, self.cam[1]))
        for f in self.floats:
            f[4] += dt
            f[2] -= dt * 30
        self.floats = [f for f in self.floats if f[4] < 2]
        if self.app.top() is self:
            if self.queue:
                self.queue.pop(0)()
            elif self.w.complete() and not self.finished:
                self.finished = True
                self.victory()

    def victory(self):
        from .scenes import VictoryScene
        storage.delete("gra")
        audio.play("fanfare")
        self.app.replace(VictoryScene(self.app, self.w))

    # ------------------------------------------------------------ rysowanie
    def draw(self, surf):
        surf.fill((20, 24, 18))
        surf.set_clip(VIEW)
        surf.blit(self.r.surf, (VIEW.x - int(self.cam[0]), VIEW.y - int(self.cam[1])))
        # migotanie wody
        rnd = random.Random(int(self.t * 3))
        for _ in range(14):
            x, y = rnd.randrange(N), rnd.randrange(N)
            if self.w.terr[y][x] == "water":
                sx, sy = self.tile_screen(x, y)
                pygame.draw.line(surf, (200, 230, 255), (sx - 6 + rnd.randint(-8, 8), sy), (sx + 2, sy), 2)
        if self.hover:
            sx, sy = self.tile_screen(*self.hover)
            surf.blit(gfx.tile_fill((255, 255, 255, 50)), (sx - TW // 2, sy - TH // 2))
            surf.blit(gfx.tile_outline((255, 250, 200), 1), (sx - TW // 2, sy - TH // 2))
        if self.sel:
            sx, sy = self.tile_screen(*self.sel)
            a = 120 + int(80 * abs(((self.t * 2) % 2) - 1))
            surf.blit(gfx.tile_outline((255, 220, 80, a), 3), (sx - TW // 2, sy - TH // 2))
        self.draw_raids(surf)
        for f in self.floats:
            ui.draw_text(surf, f[0], (int(f[1]), int(f[2])), 18, f[3], True, center=True, shadow=(0, 0, 0))
        surf.set_clip(None)
        self.draw_top(surf)
        self.draw_panel(surf)
        self.draw_tip(surf)

    def draw_raids(self, surf):
        import math
        for r in self.w.raids:
            sx, sy = self.tile_screen(*r["pos"])
            cx, cy = self.tile_screen(*self.w.cap)
            # przerywana linia ku grodowi
            dist = math.hypot(cx - sx, cy - sy) or 1
            for k in range(0, int(dist), 14):
                t = k / dist
                pygame.draw.circle(surf, (220, 60, 50), (int(sx + (cx - sx) * t), int(sy + (cy - sy) * t)), 2)
            pulse = 2 + int(2 * abs(math.sin(self.t * 4)))
            pygame.draw.ellipse(surf, (220, 40, 40), (sx - 26, sy - 10, 52, 22), pulse)
            u = gfx.unit_big(r["unit"], r["faction"], 2)
            u = pygame.transform.flip(u, sx > cx, False)
            bob = int(abs(math.sin(self.t * 6)) * 3)
            for k, (dx, dy) in enumerate([(-14, -4), (8, 2)]):
                surf.blit(u, (sx + dx - u.get_width() // 2, sy + dy - u.get_height() + 6 - (bob if k == 0 else 3 - bob)))
            ui.draw_text(surf, r["name"], (sx, sy + 12), 12, (255, 220, 200), True, center=True, shadow=(0, 0, 0))

    def draw_top(self, surf):
        surf.blit(gfx.panel(W, 44, 2, dark=True), (0, 0))
        prod = self.w.production()
        prod["food"] -= self.w.upkeep()
        x = 16
        for k in data.RES_ORDER:
            surf.blit(gfx.icon(k, 2), (x, 10))
            ui.draw_text(surf, str(self.w.res[k]), (x + 30, 10), 19, ui.CREAM, True)
            col = (170, 220, 140) if prod[k] >= 0 else (240, 120, 100)
            ui.draw_text(surf, f"{prod[k]:+d}", (x + 30 + ui.font(19, True).size(str(self.w.res[k]))[0] + 6, 14), 14, col, True)
            x += 150
        surf.blit(gfx.icon("turn", 2), (x + 10, 10))
        ui.draw_text(surf, f"Tura {self.w.turn}/{self.w.max_turns}", (x + 40, 11), 18, ui.GOLD, True)
        ep = data.EPOCHS[self.w.epoch]
        ui.draw_text(surf, f"{ep['name']} • {self.ch['place']} {self.ch['year']}", (W - 16 - ui.font(15, True).size(f"{ep['name']} • {self.ch['place']} {self.ch['year']}")[0], 13), 15, ui.CREAM, True)

    def draw_panel(self, surf):
        p = PANEL
        surf.blit(gfx.panel(p.w, p.h, 3), p.topleft)
        ui.draw_text(surf, self.ch["title"], (p.x + 16, p.y + 12), 16, ui.RED, True, width=p.w - 30)
        y = p.y + 58
        ui.draw_text(surf, "Zadania kroniki:", (p.x + 16, y), 14, ui.INK_SOFT, True)
        y += 22
        fi = self.w.final_index()
        for i in range(len(self.ch["objectives"])):
            ok, label = self.w.objective_state(i)
            ok = ok or i in self.w.done
            if ok:
                surf.blit(gfx.icon("check", 1), (p.x + 14, y + 3))
            else:
                pygame.draw.rect(surf, ui.INK_SOFT, (p.x + 14, y + 3, 11, 11), 1)
            col = ui.GREEN if ok else (ui.INK if not (i == fi and not self.w.final_available()) else (140, 120, 100))
            y = ui.draw_text(surf, label, (p.x + 32, y), 13, col, ok, width=p.w - 46)
            y += 2
        # info o polu
        pygame.draw.line(surf, (150, 110, 70), (p.x + 14, 300), (p.right - 14, 300))
        if self.sel:
            x, yy = self.sel
            t = self.w.terr[yy][x]
            pos = self.sel
            rr = self.raid_at(pos)
            if rr:
                ui.draw_text(surf, rr["name"], (p.x + 16, 308), 17, ui.RED, True)
                ui.draw_text(surf, f"Siła: {len(rr['deck'])} oddziały • pod grodem za ok. {raid_eta(self.w, rr)} tur",
                             (p.x + 16, 334), 13, ui.INK, width=p.w - 32)
            elif pos in self.w.buildings:
                b = self.w.buildings[pos]
                name = "Siedziba władcy" if b == "grod" else data.BUILDINGS[b]["name"]
                ui.draw_text(surf, name, (p.x + 16, 308), 17, ui.INK, True)
                prod = self.w.building_prod(b)
                ps = ", ".join(f"+{v} {data.RES_NAMES[k].lower()}" for k, v in prod.items() if v) or "brak produkcji"
                yy2 = ui.draw_text(surf, "Na turę: " + ps, (p.x + 16, 332), 13, ui.INK_SOFT, width=p.w - 32)
                desc = "Serce księstwa. Tu zasiada władca, a kronikarz ma swój kąt przy piecu." if b == "grod" else data.BUILDINGS[b]["desc"]
                ui.draw_text(surf, desc, (p.x + 16, yy2 + 6), 13, ui.INK, width=p.w - 32)
            elif pos in self.w.camps:
                c = self.w.camps[pos]
                ui.draw_text(surf, c["name"], (p.x + 16, 308), 17, ui.RED, True)
                ui.draw_text(surf, "Rozbity!" if c["beaten"] else f"Siła wroga: {len(c['deck'])} oddziałów", (p.x + 16, 334), 14, ui.INK)
            elif pos in self.w.landmarks:
                ui.draw_text(surf, self.w.landmarks[pos][0], (p.x + 16, 308), 17, ui.PURPLE, True)
                ui.draw_text(surf, "Miejsce historyczne", (p.x + 16, 334), 13, ui.INK_SOFT)
            else:
                ui.draw_text(surf, TERR_NAMES[t], (p.x + 16, 308), 17, ui.INK, True)
                if t == "water":
                    ui.draw_text(surf, "Ryby, łodzie i... nic do budowania.", (p.x + 16, 334), 13, ui.INK_SOFT)
                elif pos not in self.w.territory:
                    ui.draw_text(surf, "Poza granicami. Buduj bliżej grodu, by poszerzyć ziemie.", (p.x + 16, 334), 13, ui.INK_SOFT, width=p.w - 32)
                else:
                    ui.draw_text(surf, "Co tu zbudować?", (p.x + 16, 334), 13, ui.INK_SOFT)
        mpos = pygame.mouse.get_pos()
        for b in self.tile_buttons:
            if hasattr(b, "kind"):
                self.draw_build_btn(surf, b)
            else:
                b.draw(surf)
        for b in self.buttons:
            b.draw(surf)
        for b in self.tile_buttons:
            if hasattr(b, "kind") and b.rect.collidepoint(mpos):
                self.draw_build_tip(surf, b)

    def draw_build_btn(self, surf, b):
        r = b.rect
        base = (236, 220, 180) if b.enabled else (205, 196, 178)
        if b.hover and b.enabled:
            base = (250, 238, 200)
        pygame.draw.rect(surf, base, r)
        pygame.draw.rect(surf, (120, 86, 50), r, 1)
        ui.draw_text(surf, b.label, (r.x + 6, r.y + 6), 13, ui.INK if b.enabled else (130, 116, 100), True)
        cost = self.w.build_cost(b.kind)
        x = r.right - 6
        for k, v in reversed(list(cost.items())):
            img = ui.font(12, True).render(str(v), True, ui.INK if self.w.res[k] >= v else ui.RED)
            x -= img.get_width()
            surf.blit(img, (x, r.y + 8))
            x -= 18
            surf.blit(gfx.icon(k, 1), (x, r.y + 9))
            x -= 4

    def draw_build_tip(self, surf, b):
        d = data.BUILDINGS[b.kind]
        text = d["desc"] + ("\nKażdy kolejny taki budynek kosztuje o 25% więcej." if self.w.count(b.kind) else "") + ("" if b.enabled else "\n⚠ " + b.why)
        h = ui.text_height(text, 13, 300) + 16
        r = pygame.Rect(PANEL.x - 330, b.rect.y - 4, 320, h)
        pygame.draw.rect(surf, (40, 28, 18), r)
        pygame.draw.rect(surf, ui.GOLD, r, 1)
        ui.draw_text(surf, text, (r.x + 10, r.y + 8), 13, ui.CREAM, width=300)

    def draw_tip(self, surf):
        r = pygame.Rect(10, H - 74, VIEW.w - 20, 64)
        s = pygame.Surface(r.size, pygame.SRCALPHA)
        s.fill((30, 20, 12, 215))
        surf.blit(s, r.topleft)
        pygame.draw.rect(surf, ui.GOLD, r, 1)
        surf.blit(pygame.transform.scale(gfx.portrait(data.HERO["p"], 2), (54, 54)), (r.x + 5, r.y + 5))
        ui.draw_text(surf, "Damian radzi:", (r.x + 68, r.y + 6), 13, (210, 170, 240), True)
        ui.draw_text(surf, self.tip_text, (r.x + 68, r.y + 25), 14, ui.CREAM, width=r.w - 80)
