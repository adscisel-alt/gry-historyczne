"""Rozdział 5: wskazywanie sprzeczności w relacjach świadków (z dowodem z ekwipunku)."""
import pygame

from ..config import sep, FIOLET
from .. import grafika as G
from .. import ui
from ..dane import minigry_dane as MD
from ..dane import rozdzialy as R
from ..dane import postacie as P
from .baza import Minigra


class Swiadkowie(Minigra):
    gid = "swiadkowie"
    tytul = "Redakcja „Kuriera”: kto mówi nieprawdę?"
    instrukcja = ("Przeczytaj zeznania. Kliknij to, które jest sprzeczne z faktami, a potem przedmiot z torby, który to udowadnia. "
                  "Damian powtarza: plotka to nie dowód!")

    def __init__(self, app):
        super().__init__(app)
        self.runda = 0
        self.wskazane = None
        self.po_rundzie = False

    @property
    def dane_rundy(self):
        return MD.SWIADKOWIE_RUNDY[self.runda]

    def wskaz(self, i):
        self.wskazane = i
        self.app.dzwieki.graj("klik")
        if i != self.dane_rundy["falszywe"]:
            self.info("Hmm, to zeznanie zgadza się z tym, co wiemy. Szukaj dalej.", False)
            self.wskazane = None
            return False
        self.info("Dobrze — to brzmi podejrzanie. Teraz pokaż dowód z torby.")
        return True

    def pokaz_dowod(self, przedmiot):
        if self.wskazane is None:
            self.info("Najpierw wskaż fałszywe zeznanie.", False)
            return False
        if przedmiot == self.dane_rundy["dowod"]:
            self.po_rundzie = True
            self.info(self.dane_rundy["wyjasnienie"])
            self.app.dzwieki.graj("stempel")
            return True
        self.info("%s niczego tu nie dowodzi. Poszukaj innego dowodu." % R.PRZEDMIOTY[przedmiot]["nazwa"], False)
        return False

    def nastepna(self):
        self.po_rundzie = False
        self.wskazane = None
        self.runda += 1
        self.komunikat = ""
        if self.runda >= len(MD.SWIADKOWIE_RUNDY):
            self.runda = len(MD.SWIADKOWIE_RUNDY) - 1
            self.wygraj()

    def rect_zeznania(self, i):
        return pygame.Rect(40, 170 + i * 120, 820, 108)

    def rect_przedmiotu(self, i):
        return pygame.Rect(900 + (i % 3) * 112, 200 + (i // 3) * 112, 100, 100)

    def klik(self, poz):
        if self.po_rundzie:
            self.nastepna()
            return
        for i in range(3):
            if self.rect_zeznania(i).collidepoint(poz):
                self.wskaz(i)
                return
        for i, p in enumerate(self.app.gra.stan.ekwipunek):
            if self.rect_przedmiotu(i).collidepoint(poz):
                self.pokaz_dowod(p)
                return

    def rysuj_gre(self, s):
        mysz = self.app.mysz()
        d = self.dane_rundy
        G.tekst(s, "Runda %d / %d — %s" % (self.runda + 1, len(MD.SWIADKOWIE_RUNDY), d["pytanie"]), (40, 125), 22, 25, "plakat")
        for i, (kto, tekst) in enumerate(d["zeznania"]):
            r = self.rect_zeznania(i)
            G.przycisk(s, r, "", r.collidepoint(mysz) or self.wskazane == i)
            if self.wskazane == i:
                pygame.draw.rect(s, FIOLET, r, 4, border_radius=4)
            s.blit(G.portret(kto, 76), (r.x + 10, r.y + 8))
            G.tekst(s, P.imie(kto), (r.x + 100, r.y + 8), 16, 50, "plakat")
            ui.akapit(s, "„" + tekst + "”", (r.x + 100, r.y + 32, r.w - 120, 80), 18, 25, "reka", 0)
        G.tekst(s, "Twoja torba (dowody):", (900, 170), 16, 40, "plakat")
        for i, p in enumerate(self.app.gra.stan.ekwipunek):
            r = self.rect_przedmiotu(i)
            pygame.draw.rect(s, sep(215 if r.collidepoint(mysz) else 195), r, border_radius=6)
            pygame.draw.rect(s, sep(90), r, 2, border_radius=6)
            ik = G.ikona(p, 54)
            s.blit(ik, ik.get_rect(center=(r.centerx, r.centery - 10)))
            ui.akapit(s, R.PRZEDMIOTY[p]["nazwa"], (r.x + 4, r.y + 68, r.w - 8, 30), 11, 30, odstep=-2, wysrodkuj=True)
        if self.po_rundzie:
            G.tekst(s, "▸ kliknij, aby przejść dalej", (640, 620), 18, 60, "reka", srodek=True)
