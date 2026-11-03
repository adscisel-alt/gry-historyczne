# -*- coding: utf-8 -*-
"""Okna nakładane: dialogi z postaciami, decyzje, zagadki, informacje."""
import random
import pygame

from . import data, gfx, ui, audio

W, H = 1280, 720


def who_info(who):
    if who == "tomek":
        return data.TOMEK
    return data.CHARACTERS.get(who)


class Scene:
    opaque = True

    def __init__(self, app):
        self.app = app
        self.buttons = []

    def handle(self, ev):
        for b in list(self.buttons):
            if b.handle(ev):
                return True
        return False

    def update(self, dt):
        pass

    def draw(self, surf):
        pass


def dim(surf, a=150):
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    s.fill((10, 6, 4, a))
    surf.blit(s, (0, 0))


class Dialogue(Scene):
    """Kolejka wypowiedzi. Element: dict(who, text) albo dict(decision) z wyborami."""
    opaque = False

    def __init__(self, app, items, world=None, on_done=None):
        super().__init__(app)
        self.items = list(items)
        self.world = world
        self.on_done = on_done
        self.i = 0
        self.chars = 0.0
        self.result = None
        self._setup()

    def cur(self):
        return self.items[self.i]

    def _setup(self):
        self.chars = 0.0
        self.buttons = []
        it = self.cur()
        box = pygame.Rect(140, 420, 1000, 270)
        if self.result is None and it.get("choices"):
            y = box.bottom - 30 - 44 * len(it["choices"])
            for k, (label, eff, res) in enumerate(it["choices"]):
                self.buttons.append(ui.Button((box.x + 200, y + k * 44, box.w - 230, 38), label,
                                              lambda k=k: self.choose(k), size=16))
        else:
            self.buttons.append(ui.Button((box.right - 190, box.bottom - 56, 160, 40), "Dalej ▶", self.next, key=pygame.K_SPACE))

    def choose(self, k):
        label, eff, res = self.cur()["choices"][k]
        if self.world is not None:
            if "battle" in eff or "quiz" in eff:
                self.app.pop()
                cb = self.cur().get("special")
                if cb:
                    cb(eff)
                return
            msgs = self.world.apply(eff, halve_bad=True)
            if msgs:
                res = (res + " " + " ".join(msgs)).strip()
        self.result = res or "Tak się stało."
        audio.play("good")
        self._setup()

    def next(self):
        if self.chars < len(self.text()):
            self.chars = 10 ** 6
            return
        self.result = None
        self.i += 1
        if self.i >= len(self.items):
            self.app.pop()
            if self.on_done:
                self.on_done()
            return
        self._setup()

    def text(self):
        if self.result is not None:
            return self.result
        return self.cur()["text"]

    def handle(self, ev):
        if super().handle(ev):
            return True
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and not self.cur().get("choices"):
            self.next()
        elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN,) and not (self.cur().get("choices") and self.result is None):
            self.next()
        return True

    def update(self, dt):
        self.chars += dt * 90

    def draw(self, surf):
        dim(surf, 110)
        it = self.cur()
        box = pygame.Rect(140, 420, 1000, 270)
        surf.blit(gfx.panel(box.w, box.h, 7), box.topleft)
        who = "tomek" if self.result is not None else it.get("who")
        info = who_info(who) if who else None
        tx = box.x + 30
        if info:
            pr = gfx.portrait(info["p"], 4)
            surf.blit(pr, (box.x + 24, box.y - 60))
            pygame.draw.rect(surf, (60, 36, 18), (box.x + 24, box.y - 60, 128, 128), 3)
            ui.draw_text(surf, info["name"], (box.x + 88, box.y + 74), 18, ui.INK, True, center=True)
            ui.draw_text(surf, info["title"], (box.x + 88, box.y + 98), 13, ui.INK_SOFT, center=True)
            tx = box.x + 180
        elif it.get("icon") is not None:
            surf.blit(it["icon"], (box.x + 50, box.y + 30))
            tx = box.x + 180
        title = it.get("title")
        y = box.y + 22
        if title and self.result is None:
            ui.draw_text(surf, title, (tx, y), 22, ui.RED, True)
            y += 34
        t = self.text()[: int(self.chars)]
        ui.draw_text(surf, t, (tx, y), 18, ui.INK, width=box.right - tx - 30)
        for b in self.buttons:
            b.draw(surf)


class Quiz(Scene):
    """Zagadka historyczna z 4 odpowiedziami."""
    opaque = False

    def __init__(self, app, title, q, answers, ok, on_result, hints=0, explain=None):
        super().__init__(app)
        self.title, self.q = title, q
        order = list(range(len(answers)))
        random.shuffle(order)
        self.answers = [answers[i] for i in order]
        self.ok = order.index(ok)
        self.on_result = on_result
        self.explain = explain
        self.chosen = None
        self.removed = set()
        wrong = [i for i in range(len(self.answers)) if i != self.ok]
        random.shuffle(wrong)
        for i in wrong[:hints]:
            self.removed.add(i)
        self.box = pygame.Rect(190, 110, 900, 500)
        self._mk()

    def _mk(self):
        self.buttons = []
        b = self.box
        y0 = b.y + 210
        for i, a in enumerate(self.answers):
            col = (120, 78, 40)
            en = self.chosen is None and i not in self.removed
            if self.chosen is not None:
                col = (50, 130, 60) if i == self.ok else ((170, 50, 40) if i == self.chosen else (120, 112, 100))
            lab = ("ABCD"[i] + ")  " + a) if i not in self.removed else "— (mnisi skreślili tę odpowiedź) —"
            self.buttons.append(ui.Button((b.x + 60, y0 + i * 52, b.w - 120, 44), lab, lambda i=i: self.pick(i),
                                          size=16, enabled=en or self.chosen is not None, color=col))
        if self.chosen is not None:
            self.buttons.append(ui.Button((b.centerx - 90, b.bottom - 54, 180, 40), "Dalej ▶", self.done, key=pygame.K_SPACE))

    def pick(self, i):
        if self.chosen is not None:
            return
        self.chosen = i
        audio.play("good" if i == self.ok else "bad")
        self._mk()

    def done(self):
        self.app.pop()
        self.on_result(self.chosen == self.ok)

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN and self.chosen is None and ev.unicode and ev.unicode.lower() in "abcd1234":
            k = "abcd1234".index(ev.unicode.lower()) % 4
            if k not in self.removed and k < len(self.answers):
                self.pick(k)
                return True
        super().handle(ev)
        return True

    def draw(self, surf):
        dim(surf, 150)
        b = self.box
        surf.blit(gfx.panel(b.w, b.h, 11), b.topleft)
        surf.blit(gfx.icon("chronicle", 4), (b.x + 30, b.y + 26))
        ui.draw_text(surf, self.title, (b.x + 100, b.y + 28), 24, ui.PURPLE, True)
        ui.draw_text(surf, self.q, (b.x + 100, b.y + 72), 21, ui.INK, True, width=b.w - 150)
        if self.removed:
            ui.draw_text(surf, "Podpowiedź uczonych: jedna błędna odpowiedź skreślona.", (b.x + 100, b.y + 172), 14, ui.INK_SOFT)
        for bt in self.buttons:
            bt.draw(surf)
        if self.chosen is not None:
            good = self.chosen == self.ok
            msg = "Brawo! Dobra odpowiedź." if good else "Niestety. Poprawna odpowiedź: " + self.answers[self.ok]
            if self.explain and not good:
                msg += " " + self.explain
            ui.draw_text(surf, msg, (b.x + 60, b.bottom - 100), 16, ui.GREEN if good else ui.RED, True, width=b.w - 320)


class Info(Scene):
    opaque = False

    def __init__(self, app, title, text, image=None, buttons=None, on_close=None, wide=False):
        super().__init__(app)
        self.title, self.text, self.image = title, text, image
        self.on_close = on_close
        bw = 900 if wide else 760
        th = ui.text_height(text, 17, bw - (260 if image else 80))
        bh = max(280, min(640, th + 170), (image.get_height() + 150) if image else 0)
        self.box = pygame.Rect((W - bw) // 2, (H - bh) // 2, bw, bh)
        b = self.box
        self.buttons = []
        specs = buttons or [("Zamknij", None)]
        x = b.right - 30
        for label, cb in reversed(specs):
            wbt = max(150, ui.font(17, True).size(label)[0] + 40)
            x -= wbt
            self.buttons.append(ui.Button((x, b.bottom - 58, wbt, 40), label, lambda cb=cb: self.close(cb)))
            x -= 12

    def close(self, cb):
        self.app.pop()
        if cb:
            cb()
        elif self.on_close:
            self.on_close()

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.close(None)
            return True
        super().handle(ev)
        return True

    def draw(self, surf):
        dim(surf, 140)
        b = self.box
        surf.blit(gfx.panel(b.w, b.h, 5), b.topleft)
        x = b.x + 40
        if self.image:
            surf.blit(self.image, (b.x + 34, b.y + 70))
            x = b.x + 60 + self.image.get_width()
        ui.draw_text(surf, self.title, (b.x + 40, b.y + 24), 24, ui.RED, True)
        ui.draw_text(surf, self.text, (x, b.y + 74), 17, ui.INK, width=b.right - x - 40)
        for bt in self.buttons:
            bt.draw(surf)
