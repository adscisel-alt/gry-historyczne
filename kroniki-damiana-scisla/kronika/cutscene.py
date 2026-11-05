# -*- coding: utf-8 -*-
"""Przerywniki filmowe: sceny wyrenderowane w Blenderze, powolny najazd kamery i napisy narratora."""
import pygame

from . import gfx, ui, audio
from .modals import Scene, W, H

CUTSCENES = {
    0: [("cut_wichman_1", "Rok 967. Na skraju puszczy staje wojsko Mieszka, a obok – czeska jazda, dar księcia Bolesława. "
                          "Gdzieś za drzewami Wichman prowadzi Wolinian..."),],
    1: [("cut_legnica_1", "Wieczór. Niebo czerwone od łun. Mongolskie zagony okrążają gród, a obrońcy liczą strzały w kołczanach."),],
    3: [("cut_plowce_1", "27 września 1331 roku. Mgła wisi nad Kujawami. Z bieli wyłaniają się chorągwie Zakonu – "
                         "a rycerstwo Łokietka już pochyla kopie."),],
    5: [("cut_grunwald_2", "15 lipca 1410 roku. Dwie wielkie armie stoją naprzeciw siebie od świtu. Upał. Cisza przed burzą."),
        ("cut_grunwald_1", "Heroldowie wbijają w ziemię dwa nagie miecze: „Na pomoc, byście nie kryli się w lasach!” "
                           "Król odpowiada spokojnie: „Mieczów mamy dość, ale i te przyjmuję”.")],
    7: [("cut_glogow_1", "Rok 1109. Cesarska wieża oblężnicza toczy się ku wałom Głogowa. Łucznicy na murach czekają na rozkaz."),],
}


def has_cutscene(idx):
    return any(gfx.asset(img) for img, _ in CUTSCENES.get(idx, []))


class Cutscene(Scene):
    def __init__(self, app, idx, on_done):
        super().__init__(app)
        self.slides = [(gfx.asset(img), txt) for img, txt in CUTSCENES.get(idx, []) if gfx.asset(img)]
        self.on_done = on_done
        self.i = 0
        self.t = 0.0
        self.chars = 0.0
        audio.play("drum")

    def next(self):
        if self.chars < len(self.slides[self.i][1]):
            self.chars = 10 ** 6
            return
        self.i += 1
        self.t = 0.0
        self.chars = 0.0
        if self.i >= len(self.slides):
            self.finish()

    def finish(self):
        self.app.pop()
        self.on_done()

    def handle(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.finish()
        elif (ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_RETURN)) or \
                (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1):
            self.next()
        return True

    def update(self, dt):
        self.t += dt
        self.chars += dt * 45

    def draw(self, surf):
        surf.fill((0, 0, 0))
        if not self.slides:
            return
        img, txt = self.slides[self.i]
        # powolny najazd kamery (efekt Kena Burnsa)
        z = min(1.0, self.t / 12.0)
        iw, ih = img.get_size()
        cw, ch = int(iw * (1 - 0.12 * z)), int(ih * (1 - 0.12 * z))
        cx, cy = (iw - cw) // 2, int((ih - ch) * 0.4)
        view = pygame.transform.scale(img.subsurface((cx, cy, cw, ch)), (W, H - 120))
        surf.blit(view, (0, 60))
        fade = max(0, 255 - int(self.t * 400))
        if fade:
            f = pygame.Surface((W, H), pygame.SRCALPHA)
            f.fill((0, 0, 0, fade))
            surf.blit(f, (0, 0))
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, W, 60))
        pygame.draw.rect(surf, (0, 0, 0), (0, H - 120, W, 120))
        ui.draw_text(surf, txt[: int(self.chars)], (120, H - 104), 19, ui.CREAM, width=W - 240, line_h=27)
        ui.draw_text(surf, "Spacja – dalej   •   Esc – pomiń", (W - 20 - 260, 22), 13, (160, 150, 130))
        ui.draw_text(surf, f"{self.i + 1}/{len(self.slides)}", (40, 22), 13, (160, 150, 130), True)
