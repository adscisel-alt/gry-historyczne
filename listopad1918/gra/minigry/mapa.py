"""Rozdział 1: mapa trzech zaborów — przypisz miasta do zaborów."""
import random

import pygame

from ..config import sep, FIOLET
from .. import grafika as G
from ..dane import fakty as F
from .baza import Minigra

MAPA_RECT = (40, 130, 760, 520)


class MapaZaborow(Minigra):
    gid = "mapa_zaborow"
    tytul = "Mapa trzech zaborów"
    instrukcja = ("Ktoś zerwał nazwy miast. Kliknij miasto na liście, a potem zabór na mapie, w którym leżało w 1914 r. "
                  "Pamiętaj: Rosja na wschodzie, Prusy na zachodzie i północy, Austria na południu.")

    def __init__(self, app):
        super().__init__(app)
        self.miasta = list(F.MIASTA)
        random.Random(31).shuffle(self.miasta)
        self.umieszczone = []
        self.wybrane = None
        self.bledy = 0
        x, y, w, h = MAPA_RECT
        self.sx = w / (27.4 - 13.8)
        self.sy = h / (55.6 - 48.1)
        self.wielokaty = {k: [F.rzut(lon, lat, x, y, self.sx, self.sy) for lon, lat in z["punkty"]]
                          for k, z in F.ZABORY.items()}

    def rect_miasta(self, i):
        return pygame.Rect(840, 140 + i * 54, 240, 46)

    def zabor_w_punkcie(self, poz):
        for k, pts in self.wielokaty.items():
            if F.punkt_w_wielokacie(poz[0], poz[1], pts):
                return k
        return None

    def umiesc(self, miasto, zabor):
        """API logiki (używane też przez testy). Zwraca True przy poprawnym przypisaniu."""
        if miasto in self.umieszczone:
            return True
        poprawny = F.MIASTA[miasto][1]
        if zabor == poprawny:
            self.umieszczone.append(miasto)
            self.wybrane = None
            self.info("Dobrze! %s leżał w zaborze %s." % (miasto, F.ZABORY[zabor]["nazwa"].split()[1]))
            if len(self.umieszczone) == len(self.miasta):
                self.wygraj()
            return True
        self.bledy += 1
        podp = {"rosyjski": "Pomyśl o carskiej Rosji…", "pruski": "Pomyśl o królestwie Prus…", "austriacki": "Pomyśl o cesarstwie Austrii…"}
        self.info("Nie tym razem. %s — %s" % (miasto, podp[poprawny]), False)
        return False

    def klik(self, poz):
        for i, m in enumerate(self.miasta):
            if self.rect_miasta(i).collidepoint(poz) and m not in self.umieszczone:
                self.wybrane = m
                self.app.dzwieki.graj("klik")
                return
        if self.wybrane:
            z = self.zabor_w_punkcie(poz)
            if z:
                self.umiesc(self.wybrane, z)

    def rysuj_gre(self, s):
        G.mapa(s, MAPA_RECT, 222, nazwy=True, miasta=True, podpisy_miast=True, rozmieszczone=self.umieszczone)
        mysz = self.app.mysz()
        if self.wybrane:
            z = self.zabor_w_punkcie(mysz)
            if z:
                pygame.draw.polygon(s, FIOLET, self.wielokaty[z], 4)
        for i, m in enumerate(self.miasta):
            r = self.rect_miasta(i)
            gotowe = m in self.umieszczone
            G.przycisk(s, r, ("✔ " if gotowe else "") + m, m == self.wybrane or r.collidepoint(mysz), 20, gotowe)
            if m == self.wybrane:
                pygame.draw.rect(s, FIOLET, r, 3, border_radius=4)
        G.tekst(s, "Błędy: %d" % self.bledy, (1100, 150), 18, 60)
