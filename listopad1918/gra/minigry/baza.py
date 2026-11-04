"""Wspólna baza minigier: tło, tytuł, instrukcja, przycisk powrotu, ekran sukcesu."""
import pygame

from ..config import W, H, sep, CZERWIEN_STEMPLA
from .. import grafika as G
from .. import ui
from ..sceny import Scena


class Minigra(Scena):
    gid = ""
    tytul = ""
    instrukcja = ""
    ton_tla = 190

    def __init__(self, app):
        super().__init__(app)
        self.wygrana = False
        self.komunikat = ""
        self.komunikat_dobry = True
        self.przycisk_wroc = ui.Przycisk((W - 170, 18, 150, 44), "Wróć", self.anuluj, 18)

    # --------------------------------------------------------- logika wspólna
    def wygraj(self):
        if not self.wygrana:
            self.wygrana = True
            self.czas_wygranej = self.czas
            self.app.dzwieki.graj("sukces")

    def zakoncz(self):
        self.app.zdejmij(self)
        self.app.na_poczatek(self.app.gra.wygrana_minigry(self.gid))

    def anuluj(self):
        self.app.zdejmij(self)

    def info(self, tekst, dobry=True):
        self.komunikat = tekst
        self.komunikat_dobry = dobry
        self.app.dzwieki.graj("klik" if dobry else "blad")

    # --------------------------------------------------------- zdarzenia
    def zdarzenie(self, e):
        if self.wygrana:
            if ((e.type == pygame.MOUSEBUTTONDOWN and e.button == 1) or
                    (e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN))) and self.czas - self.czas_wygranej > 0.4:
                self.zakoncz()
            return
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.anuluj()
            return
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.przycisk_wroc.klik(e.pos):
                return
            self.klik(e.pos)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
            self.klik_prawy(e.pos)
        elif e.type == pygame.KEYDOWN:
            self.klawisz(e.key)

    def klik(self, poz):
        pass

    def klik_prawy(self, poz):
        pass

    def klawisz(self, k):
        pass

    # --------------------------------------------------------- rysowanie
    def rysuj(self, s):
        s.blit(G.papier(W, H, self.ton_tla, seed=len(self.gid) * 13 + 1), (0, 0))
        G.tekst(s, self.tytul, (40, 18), 30, 25, "plakat")
        ui.akapit(s, self.instrukcja, (40, 60, 1060, 60), 17, 55, odstep=1)
        self.rysuj_gre(s)
        if self.komunikat:
            r = pygame.Rect(40, H - 54, W - 80, 40)
            pygame.draw.rect(s, sep(235), r, border_radius=6)
            pygame.draw.rect(s, sep(60) if self.komunikat_dobry else CZERWIEN_STEMPLA, r, 2, border_radius=6)
            ui.akapit(s, self.komunikat, (r.x + 14, r.y + 9, r.w - 28, 30), 17, 25, odstep=0)
        self.przycisk_wroc.rysuj(s, self.app.mysz())
        if self.wygrana:
            ui.przyciemnij(s, 120)
            ui.karta(s, (390, 230, 500, 240), 235)
            G.tekst(s, "Udało się!", (640, 300), 44, 25, "plakat", srodek=True)
            G.stempel_okragly(s, (640, 390), "ZALICZONE", 54)
            G.tekst(s, "▸ kliknij, aby wrócić do pocztówki", (640, 445), 16, 80, "reka", srodek=True)

    def rysuj_gre(self, s):
        pass
