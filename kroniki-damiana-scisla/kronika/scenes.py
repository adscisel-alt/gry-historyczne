# -*- coding: utf-8 -*-
"""Menu, wybór rozdziału, kronika, drzewko technologii, wojsko, galeria postaci, zakończenia."""
import math
import pygame

from . import data, gfx, ui, audio, storage, export
from .modals import Scene, Dialogue, Quiz, Info, TextInput, W, H, dim
from .world import World


def help_text():
    return ("JAK GRAĆ\n"
            "• Jesteś Damianem Ścisłem – kronikarzem i doradcą. Nie dowodzisz armią, lecz radzisz władcy.\n"
            "• Kliknij kafel w granicach księstwa (złota linia), by coś zbudować. Budynki co turę dają zasoby: "
            "żywność, drewno, kamień i srebro. Każdy budynek poszerza granice.\n"
            "• Technologie (T): wybierz odkrycie, zapłać i rozwiąż zagadkę historyczną. Zła odpowiedź? Spróbuj w następnej turze.\n"
            "• Wojsko (W): w Dworze drużyny werbujesz nowe karty do talii bitewnej.\n"
            "• Bitwa: wróg odsłania kartę, ty doradzasz, którą wystawić. Piechota ▶ Jazda ▶ Strzelcy ▶ Piechota (+3). "
            "Przed bitwą pytanie z epoki – dobra odpowiedź daje premię.\n"
            "• Zdarzenia losowe: zaraza, najazd, poselstwo, jarmark... Wybieraj mądrze!\n"
            "• Sterowanie: mysz, strzałki/WASD lub prawy przycisk – przesuwanie mapy, C – wróć do grodu, "
            "Spacja – koniec tury, G – grafika 3D/pikselowa, M – muzyka, F11 – pełny ekran.")


class MenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        from .mapview import MapRenderer
        self.world = World(0)
        for (pos, b) in [((12, 16), "pole"), ((16, 18), "targ"), ((13, 19), "kosciol"), ((15, 15), "koszary")]:
            if self.world.terr[pos[1]][pos[0]] != "water":
                self.world.buildings[pos] = b
        self.world.update_territory()
        self.r = MapRenderer(self.world)
        self.t = 0
        from .mapview import MapScene
        items = []
        if MapScene.has_save():
            items.append(("Kontynuuj", self.cont, 22, (70, 100, 50)))
        items += [("Kampania", self.campaign, 22, None), ("Postacie historyczne", self.gallery, 18, None),
                  ("Dziennik nauki", self.journal, 18, (100, 50, 140)), ("Jak grać", self.help, 18, None)]
        if not storage.WEB:
            items.append(("Wyjście", self.app.quit, 18, (90, 60, 40)))
        y0 = 316
        self.buttons = [ui.Button((80, y0 + i * 56, 300, 46), lab, cb, sz, color=col) for i, (lab, cb, sz, col) in enumerate(items)]
        audio.start_music("music")

    def campaign(self):
        self.app.push(ChapterSelectScene(self.app))

    def cont(self):
        from .mapview import MapScene
        try:
            self.app.replace(MapScene.load_game(self.app))
        except Exception:
            storage.delete("gra")
            self.app.push(Info(self.app, "Zapis uszkodzony", "Nie udało się wczytać zapisu. Zacznij rozdział od nowa."))

    def journal(self):
        self.app.push(JournalScene(self.app))

    def gallery(self):
        self.app.push(GalleryScene(self.app))

    def help(self):
        self.app.push(Info(self.app, "Jak grać", help_text(), wide=True))

    def update(self, dt):
        self.t += dt
        self.r.tick(dt)

    def draw(self, surf):
        cx = 560 + math.sin(self.t * 0.05) * 160
        surf.blit(self.r.surf, (-cx, -330 + math.cos(self.t * 0.04) * 40))
        dim(surf, 90)
        title = pygame.Rect(40, 60, 700, 240)
        surf.blit(gfx.panel(title.w, title.h, 21), title.topleft)
        ui.draw_text(surf, "Kroniki Damiana Ścisła", (title.centerx, title.y + 30), 50, ui.RED, True, center=True, shadow=(200, 170, 110))
        ui.draw_text(surf, "Doradca książąt i królów • 966–1410", (title.centerx, title.y + 100), 22, ui.INK, True, center=True)
        ui.draw_text(surf, "Strategia turowa z dziejów Polski: od grodu Polan po pola Grunwaldu.",
                     (title.centerx, title.y + 146), 16, ui.INK_SOFT, center=True)
        ui.draw_text(surf, "6 rozdziałów • 4 epoki • 20 technologii • 12 postaci", (title.centerx, title.y + 176), 15, ui.PURPLE, True, center=True)
        tk = gfx.hero_figure(7)
        bob = int(math.sin(self.t * 2) * 4)
        surf.blit(tk, (W - tk.get_width() - 120, H - tk.get_height() - 30 + bob))
        bub = pygame.Rect(W - 520, 90, 360, 120)
        surf.blit(gfx.panel(bub.w, bub.h, 8), bub.topleft)
        ui.draw_text(surf, "Witaj, czytelniku! Jestem Damian Ściseł. Pomożesz mi doradzać władcom przez pięć wieków historii?",
                     (bub.x + 18, bub.y + 16), 15, ui.INK, width=bub.w - 36)
        for b in self.buttons:
            b.draw(surf)
        ui.draw_text(surf, "G – grafika 3D/pikselowa   M – muzyka   F11 – pełny ekran", (20, H - 28), 13, ui.CREAM, shadow=(0, 0, 0))


class ChapterSelectScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.rects = []
        for i in range(6):
            col, row = i % 3, i // 3
            self.rects.append(pygame.Rect(60 + col * 395, 120 + row * 270, 370, 250))
        self.buttons = [ui.Button((W - 220, H - 62, 190, 44), "◀ Wróć", self.app.pop, key=pygame.K_ESCAPE)]
        self.hover = -1

    def handle(self, ev):
        if super().handle(ev):
            return True
        if ev.type == pygame.MOUSEMOTION:
            self.hover = next((i for i, r in enumerate(self.rects) if r.collidepoint(ev.pos)), -1)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(ev.pos) and i <= self.app.save.get("unlocked", 0):
                    audio.play("click")
                    self.app.push(ChronicleScene(self.app, i))
        return True

    def draw(self, surf):
        surf.blit(gfx.parchment(W, H, 77, dark=True), (0, 0))
        ui.draw_text(surf, "Kampania: Kronika czterech epok", (W // 2, 36), 32, ui.GOLD, True, center=True)
        unl = self.app.save.get("unlocked", 0)
        done = set(self.app.save.get("completed", []))
        for i, r in enumerate(self.rects):
            ch = data.CHAPTERS[i]
            ep = data.EPOCHS[ch["epoch"]]
            rr = r.move(0, -6) if i == self.hover and i <= unl else r
            surf.blit(gfx.panel(rr.w, rr.h, 30 + i), rr.topleft)
            pygame.draw.rect(surf, ep["color"], (rr.x + 8, rr.y + 8, rr.w - 16, 30))
            ui.draw_text(surf, ep["name"], (rr.x + 18, rr.y + 13), 15, ui.CREAM, True)
            ui.draw_text(surf, ch["year"], (rr.right - 18 - ui.font(15, True).size(ch["year"])[0], rr.y + 13), 15, ui.CREAM, True)
            ui.draw_text(surf, ch["title"], (rr.x + 18, rr.y + 50), 18, ui.RED, True, width=rr.w - 36)
            ui.draw_text(surf, ch["place"], (rr.x + 18, rr.y + 104), 16, ui.INK, True)
            chars = []
            for w, _ in ch["dialogue_start"]:
                if w != "damian" and w not in chars:
                    chars.append(w)
            for k, w in enumerate(chars[:3]):
                surf.blit(gfx.portrait(data.CHARACTERS[w]["p"], 2), (rr.x + 18 + k * 72, rr.y + 136))
            if i > unl:
                s = pygame.Surface(rr.size, pygame.SRCALPHA)
                s.fill((30, 20, 10, 170))
                surf.blit(s, rr.topleft)
                surf.blit(gfx.icon("lock", 5), (rr.centerx - 30, rr.centery - 30))
            elif i in done:
                surf.blit(gfx.icon("star", 4), (rr.right - 66, rr.bottom - 66))
                ui.draw_text(surf, "Ukończony", (rr.right - 100, rr.bottom - 92), 13, ui.GREEN, True)
        for b in self.buttons:
            b.draw(surf)


class ChronicleScene(Scene):
    """Intro rozdziału: epicka kronika pisana na pergaminie."""

    def __init__(self, app, idx):
        super().__init__(app)
        self.idx = idx
        self.ch = data.CHAPTERS[idx]
        self.text = "\n\n".join(self.ch["chronicle"])
        audio.start_music(f"music_{self.ch['epoch']}")
        self.chars = 0.0
        self.t = 0
        self.buttons = [ui.Button((W - 300, H - 78, 250, 48), "Rozpocznij rozdział ▶", self.go, 18),
                        ui.Button((50, H - 78, 160, 48), "◀ Wróć", self.app.pop, 16)]

    def go(self):
        if self.chars < len(self.text):
            self.chars = 10 ** 6
            return
        from .mapview import MapScene
        self.app.replace(MapScene(self.app, self.idx), keep_menu=True)

    def handle(self, ev):
        if super().handle(ev):
            return True
        if (ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_RETURN)) or \
                (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1):
            self.go()
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.app.pop()
        return True

    def update(self, dt):
        self.t += dt
        self.chars += dt * 75

    def draw(self, surf):
        surf.blit(gfx.parchment(W, H, 200 + self.idx), (0, 0))
        gfx.frame(surf, pygame.Rect(16, 16, W - 32, H - 32), width=4)
        ep = data.EPOCHS[self.ch["epoch"]]
        ui.draw_text(surf, f"{ep['name']} • {self.ch['place']} • {self.ch['year']}", (W // 2, 40), 17, ui.INK_SOFT, True, center=True)
        ui.draw_text(surf, self.ch["title"], (W // 2, 66), 34, ui.RED, True, center=True)
        # inicjał
        ini = pygame.Rect(60, 130, 96, 96)
        pygame.draw.rect(surf, (150, 40, 36), ini)
        pygame.draw.rect(surf, ui.GOLD, ini, 4)
        for k in range(6):
            pygame.draw.circle(surf, ui.GOLD, (ini.x + 10 + k * 15, ini.bottom - 8), 2)
        ui.draw_text(surf, self.text[0], (ini.centerx, ini.y + 10), 64, ui.GOLD, True, center=True)
        shown = self.text[1: int(self.chars)]
        y = 132
        paras = shown.split("\n\n")
        for k, para in enumerate(paras):
            width = 760 if k == 0 else 860
            x = 180 if k == 0 else 60
            y = ui.draw_text(surf, para, (x, y), 18, ui.INK, width=width, line_h=26) + 14
            if k == 0:
                y = max(y, 240)
        if int(self.chars) >= len(self.text):
            ws = []
            for w_, _ in self.ch["dialogue_start"]:
                if w_ != "damian" and w_ not in ws:
                    ws.append(w_)
            ui.draw_text(surf, "W tym rozdziale spotkasz:", (60, 528), 15, ui.INK_SOFT, True)
            for k, w_ in enumerate(ws):
                c = data.CHARACTERS[w_]
                surf.blit(gfx.portrait(c["p"], 2), (60 + k * 150, 552))
                ui.draw_text(surf, c["name"], (130 + k * 150, 560), 13, ui.INK, True, width=80)
        tk = gfx.hero_figure(6)
        surf.blit(tk, (W - tk.get_width() - 60, 150 + int(math.sin(self.t * 2) * 3)))
        ui.draw_text(surf, "Spisał Damian Ściseł, kronikarz", (W - 210, 400), 14, ui.PURPLE, True, center=True)
        for b in self.buttons:
            b.draw(surf)


class TechScene(Scene):
    def __init__(self, app, mapscene):
        super().__init__(app)
        self.ms = mapscene
        self.w = mapscene.w
        self.nodes = {}
        cols = {0: [], 1: [], 2: [], 3: []}
        for tid, t in data.TECHS.items():
            cols[t["epoch"]].append(tid)
        for e, ids in cols.items():
            for j, tid in enumerate(ids):
                self.nodes[tid] = pygame.Rect(40 + e * 310, 130 + j * 106, 250, 84)
        self.buttons = [ui.Button((W - 210, H - 60, 180, 44), "◀ Mapa", self.app.pop, key=pygame.K_ESCAPE)]
        self.hover = None

    def state(self, tid):
        t = data.TECHS[tid]
        if tid in self.w.techs:
            return "owned"
        if t["epoch"] > self.w.epoch:
            return "epoch"
        if any(r not in self.w.techs for r in t["req"]):
            return "req"
        return "open"

    def handle(self, ev):
        if super().handle(ev):
            return True
        if ev.type == pygame.MOUSEMOTION:
            self.hover = next((k for k, r in self.nodes.items() if r.collidepoint(ev.pos)), None)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for tid, r in self.nodes.items():
                if r.collidepoint(ev.pos):
                    audio.play("click")
                    self.open(tid)
        return True

    def open(self, tid):
        t = data.TECHS[tid]
        st = self.state(tid)
        img = gfx.icon("tech", 6)
        if st == "owned":
            self.app.push(Info(self.app, t["name"] + " ✓", "Ciekawostka: " + t["fact"] + "\n\nEfekt: " + t["effect"], img))
            return
        cost = self.w.tech_cost(tid)
        txt = f"Efekt: {t['effect']}\nKoszt: {ui.cost_str(cost)}\n\n"
        btns = [("Zamknij", None)]
        if st == "epoch":
            txt += f"Ta wiedza należy do epoki: {data.EPOCHS[t['epoch']]['name']}. Jeszcze na nią za wcześnie!"
        elif st == "req":
            txt += "Najpierw trzeba poznać: " + ", ".join(data.TECHS[r]["name"] for r in t["req"] if r not in self.w.techs) + "."
        elif tid in self.w.tech_locked:
            txt += "Mnisi wciąż szukają w księgach. Spróbuj w następnej turze."
        elif not self.w.has(cost):
            txt += "Brakuje zasobów. Rozbuduj gospodarkę i wróć!"
        else:
            txt += "Aby zdobyć tę wiedzę, rozwiąż zagadkę historyczną. Zapłacisz tylko przy dobrej odpowiedzi."
            btns = [("Zamknij", None), ("Rozwiąż zagadkę", lambda: self.riddle(tid))]
        self.app.push(Info(self.app, t["name"], txt, img, buttons=btns))

    def riddle(self, tid):
        t = data.TECHS[tid]
        hints = 1 if self.w.count("kosciol") else 0

        def res(good):
            w = self.w
            w.stats["quiz_all"] += 1
            if good:
                w.stats["quiz_ok"] += 1
                w.pay(w.tech_cost(tid))
                w.techs.add(tid)
                audio.play("fanfare")
                self.ms.after_change()
                self.app.push(Info(self.app, "Odkrycie: " + t["name"], "Ciekawostka: " + t["fact"] + "\n\nEfekt: " + t["effect"],
                                   gfx.icon("star", 6)))
            else:
                w.tech_locked.add(tid)
        self.app.push(Quiz(self.app, "Zagadka: " + t["name"], t["q"], t["a"], t["ok"], res, hints))

    def draw(self, surf):
        surf.blit(gfx.parchment(W, H, 55), (0, 0))
        gfx.frame(surf, pygame.Rect(8, 8, W - 16, H - 16))
        ui.draw_text(surf, "Drzewko technologii", (W // 2, 24), 30, ui.RED, True, center=True)
        r = self.w.res
        ui.draw_text(surf, "Zasoby: " + "  ".join(f"{data.RES_NAMES[k]} {r[k]}" for k in data.RES_ORDER),
                     (W // 2, 64), 15, ui.INK, True, center=True)
        for e in range(4):
            ep = data.EPOCHS[e]
            x = 40 + e * 310
            pygame.draw.rect(surf, ep["color"], (x, 94, 250, 28))
            ui.draw_text(surf, ep["name"], (x + 125, 98), 15, ui.CREAM, True, center=True)
        for tid, rr in self.nodes.items():
            for req in data.TECHS[tid]["req"]:
                a = self.nodes[req]
                col = (90, 150, 70) if req in self.w.techs else (150, 130, 100)
                if a.x == rr.x:
                    pygame.draw.line(surf, col, (a.x - 10, a.centery), (a.x - 10, rr.centery), 3)
                    pygame.draw.line(surf, col, (a.x - 10, a.centery), (a.x, a.centery), 3)
                    pygame.draw.line(surf, col, (a.x - 10, rr.centery), (rr.x, rr.centery), 3)
                else:
                    mx = a.right + 14 + (rr.y - 130) // 106 * 7
                    pygame.draw.lines(surf, col, False, [(a.right, a.centery), (mx, a.centery), (mx, rr.centery), (rr.x, rr.centery)], 3)
        for tid, rr in self.nodes.items():
            t = data.TECHS[tid]
            st = self.state(tid)
            base = {"owned": (190, 220, 150), "open": (248, 236, 200), "req": (210, 200, 180), "epoch": (170, 164, 150)}[st]
            if tid == self.hover:
                base = gfx.shade(base, 1.06)
            pygame.draw.rect(surf, base, rr)
            pygame.draw.rect(surf, (90, 60, 30) if st != "open" else (180, 120, 30), rr, 3 if st == "open" else 2)
            ui.draw_text(surf, t["name"], (rr.x + 12, rr.y + 8), 16, ui.INK if st != "epoch" else (110, 100, 90), True)
            if st == "owned":
                surf.blit(gfx.icon("check", 2), (rr.right - 32, rr.y + 8))
                ui.draw_text(surf, t["effect"], (rr.x + 12, rr.y + 32), 11, ui.INK_SOFT, width=rr.w - 20)
            elif st == "epoch":
                surf.blit(gfx.icon("lock", 2), (rr.right - 32, rr.y + 8))
                ui.draw_text(surf, "Przyszła epoka", (rr.x + 12, rr.y + 34), 13, (110, 100, 90))
            else:
                ui.draw_cost(surf, self.w.tech_cost(tid), (rr.x + 10, rr.y + 50), self.w.res, 14)
                if tid in self.w.tech_locked:
                    ui.draw_text(surf, "(następna tura)", (rr.x + 12, rr.y + 32), 12, ui.RED)
                elif st == "req":
                    ui.draw_text(surf, "Wymaga wcześniejszej wiedzy", (rr.x + 12, rr.y + 32), 12, ui.INK_SOFT)
                else:
                    ui.draw_text(surf, "Kliknij, by zbadać!", (rr.x + 12, rr.y + 32), 12, (160, 100, 20), True)
        ui.draw_text(surf, "Każda technologia kryje ciekawostkę. Kościół i szkoła pomagają w zagadkach.", (40, H - 50), 14, ui.INK_SOFT)
        for b in self.buttons:
            b.draw(surf)


class ArmyScene(Scene):
    def __init__(self, app, mapscene):
        super().__init__(app)
        self.ms = mapscene
        self.w = mapscene.w
        self.make()

    def make(self):
        self.buttons = [ui.Button((W - 210, H - 60, 180, 44), "◀ Mapa", self.app.pop, key=pygame.K_ESCAPE)]
        for i, cid in enumerate(self.w.available_cards()):
            c = data.CARDS[cid]
            r = self.row(i)
            ok = self.w.recruit_slots() > 0 and self.w.has(c["cost"])
            self.buttons.append(ui.Button((r.right - 100, r.y + 10, 92, 32), "Werbuj", lambda cid=cid: self.recruit(cid), 14, enabled=ok))

    def row(self, i):
        return pygame.Rect(40 + (i // 5) * 410, 340 + (i % 5) * 62, 400, 56)

    def recruit(self, cid):
        c = data.CARDS[cid]
        self.w.pay(c["cost"])
        self.w.deck.append(cid)
        self.w.recruited_this_turn += 1
        audio.play("build")
        self.ms.after_change()
        self.make()

    def draw(self, surf):
        surf.blit(gfx.parchment(W, H, 66), (0, 0))
        gfx.frame(surf, pygame.Rect(8, 8, W - 16, H - 16))
        ui.draw_text(surf, "Wojsko księcia", (W // 2, 22), 30, ui.RED, True, center=True)
        slots = self.w.recruit_slots()
        ui.draw_text(surf, f"Werbunki w tej turze: {max(0, slots)} (po jednym na każdy Dwór drużyny)", (W // 2, 62), 15,
                     ui.INK if slots > 0 else ui.RED, True, center=True)
        ui.draw_text(surf, f"Twoja talia bitewna ({len(self.w.deck)} kart):", (40, 92), 16, ui.INK, True)
        up = self.w.upkeep()
        ui.draw_text(surf, f"Utrzymanie: {up} żywności na turę (każdy oddział ponad {len(self.w.deck) - up} kosztuje 1 żywności)",
                     (W - 40 - ui.font(14, True).size(f"Utrzymanie: {up} żywności na turę (każdy oddział ponad {len(self.w.deck) - up} kosztuje 1 żywności)")[0], 94),
                     14, ui.RED if up else ui.INK_SOFT, True)
        counts = {}
        for cid in self.w.deck:
            counts[cid] = counts.get(cid, 0) + 1
        x = 40
        for cid, n in counts.items():
            img = pygame.transform.scale(gfx.card_face(cid), (84, 118))
            surf.blit(img, (x, 120))
            ui.draw_text(surf, data.CARDS[cid]["name"], (x + 42, 242), 11, ui.INK, True, center=True, width=90)
            ui.draw_text(surf, f"×{n}  siła {data.CARDS[cid]['power']}", (x + 42, 274), 12, ui.INK_SOFT, True, center=True)
            x += 100
        ui.draw_text(surf, "Werbunek (koszt w zasobach):", (40, 310), 16, ui.INK, True)
        for i, cid in enumerate(self.w.available_cards()):
            c = data.CARDS[cid]
            r = self.row(i)
            pygame.draw.rect(surf, (240, 228, 196), r)
            pygame.draw.rect(surf, (140, 100, 60), r, 1)
            surf.blit(pygame.transform.scale(gfx.card_face(cid), (36, 50)), (r.x + 4, r.y + 3))
            ui.draw_text(surf, f"{c['name']}", (r.x + 48, r.y + 5), 14, ui.INK, True)
            ui.draw_text(surf, f"{data.CARD_TYPES[c['type']]['name']} • siła {c['power']}", (r.x + 48, r.y + 25), 12, ui.INK_SOFT)
            ui.draw_cost(surf, c["cost"], (r.x + 170, r.y + 24), self.w.res, 12)
        if self.w.count("koszary") == 0:
            ui.draw_text(surf, "Zbuduj Dwór drużyny, aby werbować!", (W // 2, 660), 18, ui.RED, True, center=True)
        tri = pygame.Rect(880, 330, 360, 210)
        surf.blit(gfx.panel(tri.w, tri.h, 12), tri.topleft)
        ui.draw_text(surf, "Rada Damiana o bitwach", (tri.x + 20, tri.y + 16), 16, ui.PURPLE, True)
        ui.draw_text(surf, "Piechota z włóczniami zatrzymuje jazdę. Jazda dopada strzelców. Strzelcy razią piechotę. "
                           "Mądry doradca ma w talii wszystkiego po trochu!", (tri.x + 20, tri.y + 46), 14, ui.INK, width=tri.w - 40)
        for b in self.buttons:
            b.draw(surf)


class GalleryScene(Scene):
    def __init__(self, app, highlight=()):
        super().__init__(app)
        self.ids = list(data.CHARACTERS.keys())
        self.hl = set(highlight)
        self.rects = [pygame.Rect(48 + (i % 6) * 200, 110 + (i // 6) * 250, 180, 230) for i in range(len(self.ids))]
        self.buttons = [ui.Button((W - 210, H - 60, 180, 44), "◀ Wróć", self.app.pop, key=pygame.K_ESCAPE),
                        ui.Button((40, H - 60, 260, 44), "Damian Ściseł", self.hero_info, 16, color=(100, 50, 140))]

    def hero_info(self):
        self.app.push(Info(self.app, "Damian Ściseł – kronikarz",
                           "Wędrowny kronikarz w fioletowym kapturze. Doradza władcom od Mieszka po Jagiełłę, "
                           "zapisuje wszystko gęsim piórem i twierdzi, że dobra rada jest warta więcej niż sto toporów.\n\n"
                           "Ulubione powiedzenie: „Historia to nie tylko daty – to ludzie, decyzje i ich skutki.”",
                           gfx.hero_figure(4)))

    def handle(self, ev):
        if super().handle(ev):
            return True
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for cid, r in zip(self.ids, self.rects):
                if r.collidepoint(ev.pos):
                    c = data.CHARACTERS[cid]
                    audio.play("click")
                    self.app.push(Info(self.app, f"{c['name']} ({c['years']})",
                                       f"{c['title']}\n\n{c['bio']}\n\nCiekawostka: {c['fact']}", gfx.portrait(c["p"], 5)))
        return True

    def draw(self, surf):
        surf.blit(gfx.parchment(W, H, 88, dark=True), (0, 0))
        ui.draw_text(surf, "Postacie historyczne", (W // 2, 30), 32, ui.GOLD, True, center=True)
        ui.draw_text(surf, "Kliknij portret, by przeczytać życiorys i ciekawostkę.", (W // 2, 72), 15, ui.CREAM, center=True)
        mp = pygame.mouse.get_pos()
        for cid, r in zip(self.ids, self.rects):
            c = data.CHARACTERS[cid]
            rr = r.move(0, -4) if r.collidepoint(mp) else r
            surf.blit(gfx.panel(rr.w, rr.h, 40), rr.topleft)
            if cid in self.hl:
                pygame.draw.rect(surf, ui.GOLD, rr, 4)
            surf.blit(gfx.portrait(c["p"], 4), (rr.centerx - 64, rr.y + 14))
            ui.draw_text(surf, c["name"], (rr.centerx, rr.y + 150), 15, ui.INK, True, center=True, width=rr.w - 16)
            ui.draw_text(surf, c["years"], (rr.centerx, rr.y + 196), 12, ui.INK_SOFT, center=True)
        for b in self.buttons:
            b.draw(surf)


class VictoryScene(Scene):
    def __init__(self, app, world):
        super().__init__(app)
        self.w = world
        idx = world.idx
        s = app.save
        s["unlocked"] = max(s.get("unlocked", 0), min(5, idx + 1))
        comp = set(s.get("completed", []))
        comp.add(idx)
        s["completed"] = sorted(comp)
        s["techs"] = sorted(set(s.get("techs", [])) | world.techs)
        sc = s.setdefault("scores", {})
        stars = 1 + (world.turn <= world.max_turns * 0.75) + (world.stats["quiz_all"] > 0 and world.stats["quiz_ok"] / world.stats["quiz_all"] >= 0.75)
        self.stars = stars
        sc[str(idx)] = max(sc.get(str(idx), 0), stars)
        app.write_save()
        last = idx == 5
        btns = [ui.Button((W // 2 + 20, H - 90, 300, 50), "Zakończenie kroniki ▶" if last else "Następny rozdział ▶", self.next, 18),
                ui.Button((W // 2 - 320, H - 90, 300, 50), "Menu główne", self.menu, 18)]
        self.buttons = btns
        self.t = 0

    def next(self):
        if self.w.idx == 5:
            self.app.replace(EndingScene(self.app))
        else:
            self.app.replace(ChronicleScene(self.app, self.w.idx + 1), keep_menu=True)

    def menu(self):
        self.app.replace(MenuScene(self.app))

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        surf.blit(gfx.parchment(W, H, 99), (0, 0))
        gfx.frame(surf, pygame.Rect(16, 16, W - 32, H - 32), width=4)
        ui.draw_text(surf, "Rozdział ukończony!", (W // 2, 50), 38, ui.GREEN, True, center=True)
        ui.draw_text(surf, self.w.ch["title"], (W // 2, 104), 22, ui.RED, True, center=True)
        for k in range(3):
            ic = gfx.icon("star", 6) if k < self.stars else gfx.icon("lock", 6)
            surf.blit(ic, (W // 2 - 120 + k * 84, 150 + int(math.sin(self.t * 3 + k) * 4)))
        ui.draw_text(surf, self.w.ch["victory"], (150, 260), 19, ui.INK, width=W - 300, line_h=28)
        st = self.w.stats
        ui.draw_text(surf, f"Tury: {self.w.turn}/{self.w.max_turns}   •   Trafne odpowiedzi: {st['quiz_ok']}/{st['quiz_all']}   •   "
                           f"Bitwy: {st['battles']}   •   Technologie: {len(self.w.techs)}/20",
                     (W // 2, 480), 16, ui.INK_SOFT, True, center=True)
        ui.draw_text(surf, "Gwiazdki: ukończenie • szybkie tempo (≤75% tur) • mądrość (≥75% trafnych odpowiedzi)",
                     (W // 2, 512), 13, ui.INK_SOFT, center=True)
        for b in self.buttons:
            b.draw(surf)


class DefeatScene(Scene):
    def __init__(self, app, idx, text):
        super().__init__(app)
        self.idx, self.text = idx, text
        audio.play("bad")
        self.buttons = [ui.Button((W // 2 + 20, H - 120, 260, 50), "Spróbuj ponownie", self.retry, 18),
                        ui.Button((W // 2 - 280, H - 120, 260, 50), "Menu główne", lambda: self.app.replace(MenuScene(self.app)), 18)]

    def retry(self):
        from .mapview import MapScene
        self.app.replace(MapScene(self.app, self.idx), keep_menu=True)

    def draw(self, surf):
        surf.blit(gfx.parchment(W, H, 13, dark=True), (0, 0))
        ui.draw_text(surf, "Kronika urwana...", (W // 2, 160), 40, ui.GOLD, True, center=True)
        ui.draw_text(surf, self.text, (240, 260), 20, ui.CREAM, width=W - 480, line_h=30)
        tk = gfx.hero_figure(4)
        surf.blit(tk, (W // 2 - tk.get_width() // 2, 380))
        for b in self.buttons:
            b.draw(surf)


class EndingScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.t = 0
        self.buttons = [ui.Button((W // 2 - 150, H - 80, 300, 50), "Menu główne", lambda: self.app.replace(MenuScene(self.app)), 18)]
        audio.play("fanfare")

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        surf.blit(gfx.parchment(W, H, 123), (0, 0))
        gfx.frame(surf, pygame.Rect(16, 16, W - 32, H - 32), width=4)
        ui.draw_text(surf, "Explicit – koniec kroniki", (W // 2, 44), 34, ui.RED, True, center=True)
        y = 110
        for p in data.ENDING:
            y = ui.draw_text(surf, p, (120, y), 19, ui.INK, width=760, line_h=28) + 16
        tk = gfx.hero_figure(6)
        surf.blit(tk, (W - tk.get_width() - 90, 150 + int(math.sin(self.t * 2) * 4)))
        sc = self.app.save.get("scores", {})
        stars = sum(sc.values())
        ui.draw_text(surf, f"Zdobyte gwiazdki: {stars}/18", (W // 2, H - 130), 22, ui.PURPLE, True, center=True)
        for b in self.buttons:
            b.draw(surf)


# ---------------------------------------------------------------- dziennik nauki, dyplom, CSV
def journal_stats(save):
    j = save.get("dziennik", [])
    ok = sum(1 for e in j if e["ok"])
    return j, ok, len(j)


def make_diploma(save):
    """Dyplom do druku (A4 poziomo, 1754 x 1240 px ≈ 150 dpi)."""
    Wd, Hd = 1754, 1240
    s = gfx.parchment(Wd, Hd, 314).copy()
    gfx.frame(s, pygame.Rect(30, 30, Wd - 60, Hd - 60), width=8)
    gfx.frame(s, pygame.Rect(60, 60, Wd - 120, Hd - 120), width=3)
    j, ok, n = journal_stats(save)
    done = len(save.get("completed", []))
    stars = sum(save.get("scores", {}).values())
    name = save.get("imie") or "Dzielny Kronikarz"
    ui.draw_text(s, "DYPLOM KRONIKARZA", (Wd // 2, 120), 84, ui.RED, True, center=True, shadow=(200, 170, 110))
    ui.draw_text(s, "„Kroniki Damiana Ścisła” – Polska 966–1410", (Wd // 2, 240), 34, ui.INK_SOFT, True, center=True)
    ui.draw_text(s, "Niniejszym zaświadcza się, że", (Wd // 2, 340), 34, ui.INK, center=True)
    ui.draw_text(s, name, (Wd // 2, 400), 76, ui.PURPLE, True, center=True)
    pygame.draw.line(s, ui.INK_SOFT, (Wd // 2 - 450, 500), (Wd // 2 + 450, 500), 3)
    txt = (f"jako doradca książąt i królów przeprowadził(a) księstwo przez dzieje Polski. "
           f"Ukończone rozdziały kampanii: {done} z {len(data.CHAPTERS)}. Zdobyte gwiazdki: {stars}. "
           f"Trafne odpowiedzi na pytania z historii: {ok} z {n}.")
    ui.draw_text(s, txt, (300, 540), 34, ui.INK, width=Wd - 600, line_h=48)
    import time
    ui.draw_text(s, "Data: " + time.strftime("%d.%m.%Y"), (200, Hd - 220), 30, ui.INK)
    ui.draw_text(s, "Damian Ściseł, kronikarz", (Wd - 620, Hd - 220), 30, ui.INK, True)
    pygame.draw.line(s, ui.INK_SOFT, (Wd - 640, Hd - 230), (Wd - 200, Hd - 230), 2)
    tk = gfx.hero_figure(9)
    s.blit(tk, (Wd - tk.get_width() - 120, 560))
    for k in range(min(stars, 18)):
        s.blit(gfx.icon("star", 4), (200 + k * 60, Hd - 330))
    sx, sy = Wd // 2, Hd - 200
    pygame.draw.circle(s, (170, 40, 36), (sx, sy), 70)
    pygame.draw.circle(s, ui.GOLD, (sx, sy), 60, 4)
    ui.draw_text(s, "966", (sx, sy - 28), 36, ui.GOLD, True, center=True)
    ui.draw_text(s, "1410", (sx, sy + 12), 26, ui.GOLD, True, center=True)
    return s


def journal_csv(save):
    import csv
    import io
    out = io.StringIO()
    w = csv.writer(out, delimiter=";")
    w.writerow(["Imię", "Data", "Rozdział", "Rodzaj", "Pytanie", "Poprawna odpowiedź", "Wynik"])
    name = save.get("imie", "")
    for e in save.get("dziennik", []):
        r = e.get("r", -1)
        rozd = data.CHAPTERS[r]["title"] if 0 <= r < len(data.CHAPTERS) else "-"
        w.writerow([name, e["t"], rozd, e.get("k", ""), e["q"], e["a"], "dobrze" if e["ok"] else "źle"])
    return ("\ufeff" + out.getvalue()).encode("utf-8")


class JournalScene(Scene):
    """„Czego się nauczyłem” – podsumowanie odpowiedzi, błędy do powtórki, dyplom, eksport dla nauczyciela."""

    def __init__(self, app):
        super().__init__(app)
        self.page = 0
        self.make()

    def make(self):
        self.buttons = [
            ui.Button((W - 220, H - 62, 190, 44), "◀ Wróć", self.app.pop, key=pygame.K_ESCAPE),
            ui.Button((40, H - 62, 250, 44), "Imię na dyplom", self.ask_name, 16, color=(100, 50, 140)),
            ui.Button((300, H - 62, 230, 44), "Dyplom (PNG)", self.diploma, 16),
            ui.Button((540, H - 62, 300, 44), "Wyniki dla nauczyciela (CSV)", self.csv, 15),
        ]
        if len(self.mistakes()) > 8:
            self.buttons.append(ui.Button((W - 420, H - 62, 180, 44), "Dalej ▶", self.next_page, 15))

    def next_page(self):
        self.page = (self.page + 1) % max(1, (len(self.mistakes()) + 7) // 8)

    def mistakes(self):
        seen, out = set(), []
        for e in reversed(self.app.save.get("dziennik", [])):
            if not e["ok"] and e["q"] not in seen:
                seen.add(e["q"])
                out.append(e)
        return out

    def ask_name(self):
        def ok(v):
            self.app.save["imie"] = v
            self.app.write_save()
        self.app.push(TextInput(self.app, "Imię na dyplom", "Wpisz imię i nazwisko, które pojawi się na dyplomie:",
                                self.app.save.get("imie", ""), ok))

    def diploma(self):
        import io
        buf = io.BytesIO()
        pygame.image.save(make_diploma(self.app.save), buf, "dyplom.png")
        msg = export.offer("dyplom_kronikarza.png", buf.getvalue(), "image/png")
        self.app.push(Info(self.app, "Dyplom gotowy", msg + "\n\nWydrukuj go poziomo na kartce A4."))

    def csv(self):
        msg = export.offer("wyniki_kroniki.csv", journal_csv(self.app.save), "text/csv")
        self.app.push(Info(self.app, "Wyniki dla nauczyciela", msg + "\n\nPlik otworzysz w Excelu lub Arkuszach Google "
                           "(rozdzielone średnikami): data, rozdział, pytanie, poprawna odpowiedź i wynik."))

    def draw(self, surf):
        surf.blit(gfx.parchment(W, H, 919), (0, 0))
        gfx.frame(surf, pygame.Rect(8, 8, W - 16, H - 16))
        ui.draw_text(surf, "Dziennik nauki – czego się nauczyłem", (W // 2, 22), 30, ui.RED, True, center=True)
        j, ok, n = journal_stats(self.app.save)
        pct = int(100 * ok / n) if n else 0
        name = self.app.save.get("imie") or "(nie podano imienia)"
        ui.draw_text(surf, f"Gracz: {name}   •   Odpowiedzi: {n}   •   Trafne: {ok} ({pct}%)   •   "
                           f"Ukończone rozdziały: {len(self.app.save.get('completed', []))}/{len(data.CHAPTERS)}",
                     (W // 2, 66), 16, ui.INK, True, center=True)
        # pasek wyników wg rozdziałów
        x = 60
        for i, ch in enumerate(data.CHAPTERS):
            es = [e for e in j if e.get("r") == i]
            good = sum(1 for e in es if e["ok"])
            r = pygame.Rect(x, 100, 180, 54)
            pygame.draw.rect(surf, (240, 228, 196), r)
            pygame.draw.rect(surf, data.EPOCHS[ch["epoch"]]["color"], r, 3)
            ui.draw_text(surf, f"{ch['place']} {ch['year']}", (r.x + 8, r.y + 6), 12, ui.INK, True)
            if es:
                pygame.draw.rect(surf, (80, 150, 70), (r.x + 8, r.y + 32, int(124 * good / len(es)), 12))
                pygame.draw.rect(surf, ui.INK_SOFT, (r.x + 8, r.y + 32, 124, 12), 1)
                ui.draw_text(surf, f"{good}/{len(es)}", (r.right - 8 - ui.font(12, True).size(f"{good}/{len(es)}")[0], r.y + 30), 12, ui.INK, True)
            else:
                ui.draw_text(surf, "brak odpowiedzi", (r.x + 8, r.y + 28), 12, ui.INK_SOFT)
            x += 196
        ms = self.mistakes()
        ui.draw_text(surf, "Do powtórki – pytania, na które padła zła odpowiedź (z poprawną odpowiedzią):",
                     (60, 176), 17, ui.PURPLE, True)
        if not ms:
            ui.draw_text(surf, "Brak błędów do powtórki. Brawo! (Albo jeszcze nie było pytań – zagraj rozdział.)",
                         (60, 214), 16, ui.GREEN, True)
        y = 210
        for e in ms[self.page * 8:(self.page + 1) * 8]:
            yy = ui.draw_text(surf, "• " + e["q"], (60, y), 15, ui.INK, True, width=W - 140)
            yy = ui.draw_text(surf, "→ " + e["a"], (84, yy), 15, ui.GREEN, width=W - 160)
            y = yy + 6
            if y > H - 100:
                break
        for b in self.buttons:
            b.draw(surf)
