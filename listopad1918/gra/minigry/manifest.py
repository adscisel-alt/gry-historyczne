"""Rozdział 3: ułożenie manifestu lubelskiego w kaszcie zecerskiej."""
import random

import pygame

from ..config import sep, FIOLET, CZERWIEN_STEMPLA
from .. import grafika as G
from .. import ui
from ..dane import minigry_dane as MD
from .baza import Minigra


class Manifest(Minigra):
    gid = "manifest"
    tytul = "Kaszta zecerska: manifest lubelski"
    instrukcja = ("Kliknij fragment, a potem miejsce w manifeście. Kolejność: kto ogłasza → ustrój → prawa obywateli → praca → "
                  "ziemia → wezwanie. Dwa fałszywe zdania wrzuć do pieca (prawy klik na fragmencie).")
    ton_tla = 175

    def __init__(self, app):
        super().__init__(app)
        self.fragmenty = list(range(len(MD.MANIFEST_FRAGMENTY)))
        random.Random(7).shuffle(self.fragmenty)
        self.sloty = [None] * len(MD.MANIFEST_SEKCJE)
        self.spalone = []
        self.wybrany = None
        self.przycisk = ui.Przycisk((900, 600, 330, 50), "Sprawdź i drukuj", self.sprawdz)
        self.zle_sloty = set()

    # ------------------------------------------------ API logiki
    def wolne(self):
        return [f for f in self.fragmenty if f not in self.sloty and f not in self.spalone]

    def poloz(self, frag, slot):
        if frag in self.sloty:
            self.sloty[self.sloty.index(frag)] = None
        if frag in self.spalone:
            self.spalone.remove(frag)
        self.sloty[slot] = frag
        self.zle_sloty.discard(slot)
        self.wybrany = None

    def spal(self, frag):
        if frag in self.sloty:
            self.sloty[self.sloty.index(frag)] = None
        if frag not in self.spalone:
            self.spalone.append(frag)
        self.wybrany = None
        if MD.MANIFEST_FRAGMENTY[frag][1] is None:
            self.info("Do pieca! Tego na pewno nie było w manifeście.")
        else:
            self.info("Hola! To zdanie było w manifeście. Wyciągnij je z popiołu (kliknij w piecu).", False)

    def sprawdz(self):
        self.zle_sloty = {i for i, f in enumerate(self.sloty) if f is None or MD.MANIFEST_FRAGMENTY[f][1] != i}
        if not self.zle_sloty:
            self.app.dzwieki.graj("stempel")
            self.wygraj()
            return True
        self.info("Coś się nie zgadza w %d miejscach. Sprawdź zaznaczone na czerwono." % len(self.zle_sloty), False)
        return False

    # ------------------------------------------------ UI
    def rect_fragmentu(self, i):
        return pygame.Rect(40, 132 + i * 56, 560, 52)

    def rect_slotu(self, i):
        return pygame.Rect(650, 135 + i * 76, 590, 68)

    PIEC = pygame.Rect(40, 590, 560, 70)

    def klik(self, poz):
        if self.przycisk.klik(poz):
            return
        for i, f in enumerate(self.wolne()):
            if self.rect_fragmentu(i).collidepoint(poz):
                self.wybrany = f
                self.app.dzwieki.graj("klik")
                return
        for i in range(len(self.sloty)):
            if self.rect_slotu(i).collidepoint(poz):
                if self.wybrany is not None:
                    self.poloz(self.wybrany, i)
                elif self.sloty[i] is not None:
                    self.wybrany = self.sloty[i]
                    self.sloty[i] = None
                return
        if self.PIEC.collidepoint(poz):
            if self.wybrany is not None:
                self.spal(self.wybrany)
            elif self.spalone:
                self.spalone.pop()

    def klik_prawy(self, poz):
        for i, f in enumerate(self.wolne()):
            if self.rect_fragmentu(i).collidepoint(poz):
                self.spal(f)
                return

    def rysuj_gre(self, s):
        mysz = self.app.mysz()
        G.tekst(s, "Rozsypane fragmenty:", (40, 112), 16, 40, "plakat")
        for i, f in enumerate(self.wolne()):
            r = self.rect_fragmentu(i)
            G.przycisk(s, r, "", f == self.wybrany or r.collidepoint(mysz))
            if f == self.wybrany:
                pygame.draw.rect(s, FIOLET, r, 3, border_radius=4)
            ui.akapit(s, MD.MANIFEST_FRAGMENTY[f][0], (r.x + 10, r.y + 6, r.w - 20, r.h), 15, 25, "maszyna", 0)
        pygame.draw.rect(s, sep(40), self.PIEC, border_radius=8)
        G.tekst(s, "PIEC  (spalone: %d)" % len(self.spalone), self.PIEC.center, 20, 230, "plakat", srodek=True)
        for i, sek in enumerate(MD.MANIFEST_SEKCJE):
            r = self.rect_slotu(i)
            pygame.draw.rect(s, sep(232), r, border_radius=4)
            pygame.draw.rect(s, CZERWIEN_STEMPLA if i in self.zle_sloty else sep(90), r, 3 if i in self.zle_sloty else 1, border_radius=4)
            G.tekst(s, "%d. %s" % (i + 1, sek), (r.x + 8, r.y + 3), 13, 90, "plakat")
            if self.sloty[i] is not None:
                ui.akapit(s, MD.MANIFEST_FRAGMENTY[self.sloty[i]][0], (r.x + 10, r.y + 20, r.w - 20, r.h), 14, 20, "maszyna", 0)
        self.przycisk.rysuj(s, mysz)
