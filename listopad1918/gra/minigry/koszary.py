"""Rozdział 5: kolejność przejmowania punktów w mieście (zagadka logiczna z napięciem)."""
import random

import pygame

from ..config import sep, FIOLET, CZERWIEN_STEMPLA
from .. import grafika as G
from .. import ui
from ..dane import minigry_dane as MD
from .baza import Minigra

POZYCJE_NA_PLANIE = {
    "Telegraf": (190, 260), "Magazyn broni": (330, 420), "Dworzec": (120, 470),
    "Koszary Mirowskie": (280, 330), "Cytadela": (420, 170),
}


class KolejnoscKoszar(Minigra):
    gid = "kolejnosc_koszar"
    tytul = "Plan akcji POW — noc z 10 na 11 listopada"
    instrukcja = ("Ułóż kolejność przejmowania pięciu punktów tak, by spełnić wszystkie wskazówki. Kliknij punkt, by dodać go "
                  "do planu; kliknij pozycję w planie, by ją usunąć. Każda błędna próba podnosi napięcie!")
    ton_tla = 165
    MAX_NAPIECIE = 3

    def __init__(self, app):
        super().__init__(app)
        self.punkty = list(MD.KOSZARY_PUNKTY)
        random.Random(11).shuffle(self.punkty)
        self.plan = []
        self.napiecie = 0
        self.zlamane = []
        self.przycisk = ui.Przycisk((700, 590, 300, 50), "Zatwierdź plan", self.sprawdz)

    def dodaj(self, punkt):
        if punkt not in self.plan and len(self.plan) < 5:
            self.plan.append(punkt)
            self.app.dzwieki.graj("klik")

    def usun(self, i):
        if i < len(self.plan):
            self.plan.pop(i)

    def sprawdz(self):
        if len(self.plan) < 5:
            self.info("Plan musi mieć wszystkie pięć punktów.", False)
            return False
        self.zlamane = MD.sprawdz_koszary(self.plan)
        if not self.zlamane:
            self.wygraj()
            return True
        self.napiecie += 1
        if self.napiecie >= self.MAX_NAPIECIE:
            self.napiecie = 0
            self.plan = []
            self.zlamane = []
            self.info("Damian: STOP, przewijam! Za dużo nerwów, ktoś mógłby zacząć strzelać. Ułóż plan od nowa — spokojnie.", False)
        else:
            self.info("Wskazówki złamane: %s. Napięcie rośnie…" % ", ".join(str(z) for z in self.zlamane), False)
        return False

    def rect_punktu(self, i):
        return pygame.Rect(560, 140 + i * 60, 300, 50)

    def rect_planu(self, i):
        return pygame.Rect(900, 140 + i * 60, 340, 50)

    def klik(self, poz):
        if self.przycisk.klik(poz):
            return
        for i, p in enumerate(self.punkty):
            if self.rect_punktu(i).collidepoint(poz):
                self.dodaj(p)
                return
        for i in range(len(self.plan)):
            if self.rect_planu(i).collidepoint(poz):
                self.usun(i)
                return

    def rysuj_gre(self, s):
        mysz = self.app.mysz()
        # szkic planu miasta
        ui.karta(s, (40, 130, 480, 420), 222)
        pygame.draw.line(s, sep(130), (470, 140), (380, 540), 22)   # Wisła
        G.tekst(s, "Wisła", (430, 300), 16, 230, "reka")
        for a, b in (((80, 300), (460, 300)), ((250, 150), (250, 540)), ((80, 450), (400, 450))):
            pygame.draw.line(s, sep(170), a, b, 6)
        for nazwa, (x, y) in POZYCJE_NA_PLANIE.items():
            nr = self.plan.index(nazwa) + 1 if nazwa in self.plan else None
            pygame.draw.circle(s, FIOLET if nr else sep(40), (x, y), 16)
            G.tekst(s, str(nr) if nr else "?", (x, y), 16, 240, "plakat", srodek=True)
            G.tekst(s, nazwa, (x + 20, y - 10), 14, 25, "plakat")
        # wskazówki
        G.tekst(s, "Wskazówki na marginesie:", (40, 560), 16, 30, "plakat")
        for i, w in enumerate(MD.KOSZARY_WSKAZOWKI):
            zl = (i + 1) in self.zlamane
            G.tekst(s, w, (40 + (i % 2) * 0, 582 + i * 20), 15, 25, "reka", kolor=CZERWIEN_STEMPLA if zl else None)
        # punkty i plan
        G.tekst(s, "Punkty w mieście", (560, 112), 16, 40, "plakat")
        for i, p in enumerate(self.punkty):
            r = self.rect_punktu(i)
            G.przycisk(s, r, p, r.collidepoint(mysz), 19, p in self.plan)
        G.tekst(s, "Twój plan", (900, 112), 16, 40, "plakat")
        for i in range(5):
            r = self.rect_planu(i)
            pygame.draw.rect(s, sep(225), r, border_radius=4)
            pygame.draw.rect(s, sep(90), r, 1, border_radius=4)
            G.tekst(s, "%d." % (i + 1), (r.x + 10, r.y + 13), 20, 60, "plakat")
            if i < len(self.plan):
                G.tekst(s, self.plan[i], (r.x + 50, r.y + 13), 20, 20, "plakat")
        # pasek napięcia
        G.tekst(s, "NAPIĘCIE", (560, 455), 16, 30, "plakat")
        for k in range(self.MAX_NAPIECIE):
            kolor = CZERWIEN_STEMPLA if k < self.napiecie else sep(200)
            pygame.draw.rect(s, kolor, (660 + k * 70, 452, 60, 24), border_radius=4)
        self.przycisk.rysuj(s, mysz)
