# -*- coding: utf-8 -*-
"""Główna pętla gry i stos scen."""
import json
import os
import sys

import pygame

from . import audio, gfx, ui, storage
from .modals import W, H

TITLE = "Kroniki Damiana Ścisła – Doradca książąt 966–1410"


WEB = sys.platform == "emscripten"


class App:
    def __init__(self, headless=False):
        pygame.init()
        audio.init()
        flags = 0 if (headless or WEB) else pygame.SCALED | pygame.RESIZABLE
        pygame.display.set_caption(TITLE)
        try:
            ic = gfx.portrait({"hair": (222, 184, 96), "beard": None, "head": "hood", "cloth": (110, 50, 150), "bg": (60, 50, 80)}, 1)
            pygame.display.set_icon(ic)
        except Exception:
            pass
        self.screen = pygame.display.set_mode((W, H), flags)
        self.clock = pygame.time.Clock()
        self.stack = []
        self.running = True
        self.save = self.load_save()
        if self.save.get("styl"):
            gfx.set_style(self.save["styl"])

    # ------------------------------------------------------------ zapis
    def load_save(self):
        return storage.load("postep", None) or {"unlocked": 0, "completed": [], "techs": [], "scores": {}}

    def write_save(self):
        storage.save("postep", self.save)

    # ------------------------------------------------------------ sceny
    def push(self, s):
        self.stack.append(s)

    def pop(self):
        if self.stack:
            self.stack.pop()
        if not self.stack:
            from .scenes import MenuScene
            self.stack.append(MenuScene(self))

    def replace(self, s, keep_menu=False):
        self.stack = [s]

    def top(self):
        return self.stack[-1] if self.stack else None

    def quit(self):
        self.running = False

    def draw(self):
        start = 0
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i].opaque:
                start = i
                break
        for s in self.stack[start:]:
            s.draw(self.screen)

    def run(self):
        import asyncio
        asyncio.run(self.run_async())

    async def run_async(self):
        import asyncio
        from .scenes import MenuScene
        self.push(MenuScene(self))
        while self.running:
            dt = min(0.05, self.clock.tick(60) / 1000)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11 and not WEB:
                    pygame.display.toggle_fullscreen()
                    continue
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_g:
                    self.save["styl"] = gfx.toggle_style()
                    self.write_save()
                    for s in self.stack:
                        if hasattr(s, "r") and hasattr(s.r, "w"):
                            s.r.w.dirty = True
                    continue
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_m and not isinstance(self.top(), type(None)):
                    audio.toggle_music()
                    continue
                if self.top():
                    self.top().handle(ev)
            for s in list(self.stack):
                if s is self.top() or not s.opaque:
                    s.update(dt)
            # scena mapy aktualizuje się też pod oknami (animacje), ale kolejkę zdarzeń przetwarza tylko na wierzchu
            for s in self.stack[:-1]:
                if hasattr(s, "r") and hasattr(s.r, "tick"):
                    s.r.tick(dt)
            self.draw()
            pygame.display.flip()
            await asyncio.sleep(0)
        if not WEB:
            pygame.quit()


def screenshots(outdir):
    """Tryb demonstracyjny: przechodzi przez kluczowe ekrany i zapisuje zrzuty PNG."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import random
    random.seed(7)
    os.makedirs(outdir, exist_ok=True)
    app = App(headless=True)
    app.save = {"unlocked": 5, "completed": [0, 1, 2], "techs": [], "scores": {}}
    from .scenes import MenuScene, ChronicleScene, TechScene, GalleryScene, ChapterSelectScene, ArmyScene
    from .mapview import MapScene
    from .battle import Battle
    from .modals import Dialogue
    from . import data

    def shot(name, steps=30):
        for _ in range(steps):
            for s in list(app.stack):
                s.update(1 / 30)
        app.draw()
        pygame.image.save(app.screen, os.path.join(outdir, name))
        if sys.stdout:
            print("zapisano", name)

    app.stack = [MenuScene(app)]
    shot("01_menu.png", 60)
    app.stack = [ChapterSelectScene(app)]
    shot("02_kampania.png", 2)
    app.stack = [ChronicleScene(app, 0)]
    shot("03_kronika.png", 400)
    ms = MapScene(app, 0)
    ms.queue.clear()
    w = ms.w
    w.techs |= {"radlo", "pismo"}
    cx, cy = w.cap
    placed = 0
    for (dx, dy) in [(2, 0), (-2, 1), (1, 2), (-1, -2), (2, 2), (-2, -1), (0, 3), (3, -1), (-3, 0), (1, -3)]:
        p = (cx + dx, cy + dy)
        t = w.terr[p[1]][p[0]]
        kind = {"grass": "pole", "field": "pole", "forest": "drwal", "hills": "kamieniolom", "road": "targ"}.get(t)
        if kind and p not in w.buildings:
            w.buildings[p] = kind
            placed += 1
    w.buildings[(cx + 1, cy - 1)] = "kosciol"
    w.buildings[(cx - 1, cy + 1)] = "koszary"
    w.update_territory()
    w.turn = 7
    w.refresh_objectives()
    ms.sel = (cx + 2, cy + 2)
    ms.after_change()
    tc = __import__("kronika.mapview", fromlist=["tile_center"]).tile_center(cx, cy)
    ms.cam = [tc[0] - 470, tc[1] - 330]
    app.stack = [ms]
    shot("04_mapa.png", 10)
    app.stack = [ms, Dialogue(app, [{"who": "dobrawa", "text": data.CHAPTERS[0]["dialogue_start"][1][1]}], w)]
    shot("05_dialog.png", 200)
    app.stack = [ms, TechScene(app, ms)]
    shot("06_technologie.png", 2)
    b = Battle(app, w, "Bitwa z Wichmanem (967)", data.CHAPTERS[0]["final"]["deck"], 24, False, "forest", ["czesi", "czesi"], "")
    b.buttons = []
    b.after_question(True)
    b.hover = 1
    app.stack = [ms, b]
    shot("07_bitwa.png", 2)
    app.stack = [GalleryScene(app)]
    shot("08_postacie.png", 2)
    # mapa z epoki zamków
    ms2 = MapScene(app, 3)
    ms2.queue.clear()
    app.stack = [ms2]
    shot("09_mapa_plowce.png", 5)
    app.stack = [ms2, ArmyScene(app, ms2)]
    shot("10_wojsko.png", 2)
    pygame.quit()


def main():
    if "--screenshots" in sys.argv:
        i = sys.argv.index("--screenshots")
        out = sys.argv[i + 1] if len(sys.argv) > i + 1 else "zrzuty"
        screenshots(out)
        return
    App().run()
