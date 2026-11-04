"""Wspólne elementy interfejsu: przyciski, teksty z zawijaniem, dźwięki proceduralne."""
import array
import math
import random

import pygame

from .config import sep, FIOLET
from . import czcionki
from . import grafika as G


class Przycisk:
    def __init__(self, rect, napis, akcja=None, rozmiar=20, wylaczony=False):
        self.rect = pygame.Rect(rect)
        self.napis = napis
        self.akcja = akcja
        self.rozmiar = rozmiar
        self.wylaczony = wylaczony

    def rysuj(self, s, mysz):
        G.przycisk(s, self.rect, self.napis, self.rect.collidepoint(mysz) and not self.wylaczony,
                   self.rozmiar, self.wylaczony)

    def klik(self, poz):
        if self.rect.collidepoint(poz) and not self.wylaczony:
            if self.akcja:
                self.akcja()
            return True
        return False


def akapit(s, tekst, rect, rozmiar=20, v=25, czcionka="szeryf", odstep=4, kolor=None, wysrodkuj=False):
    """Rysuje zawinięty tekst; zwraca wysokość."""
    f = czcionki.f(czcionka, rozmiar)
    x, y, w, h = rect
    wiersze = czcionki.zawin(tekst, f, w)
    lh = f.get_linesize() + odstep
    for i, wr in enumerate(wiersze):
        obraz = f.render(wr, True, kolor or sep(v))
        if wysrodkuj:
            s.blit(obraz, (x + (w - obraz.get_width()) // 2, y + i * lh))
        else:
            s.blit(obraz, (x, y + i * lh))
    return len(wiersze) * lh


def wysokosc_akapitu(tekst, szer, rozmiar=20, czcionka="szeryf", odstep=4):
    f = czcionki.f(czcionka, rozmiar)
    return len(czcionki.zawin(tekst, f, szer)) * (f.get_linesize() + odstep)


def przyciemnij(s, alfa=150):
    w = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    w.fill((20, 12, 6, alfa))
    s.blit(w, (0, 0))


def karta(s, rect, ton=228, stempel=None):
    pygame.draw.rect(s, (15, 9, 5), pygame.Rect(rect).move(8, 8))
    G.ramka_pocztowki(s, rect, ton, True, stempel)


def etykieta_fiolet(s, napis, poz, rozmiar=16):
    f = czcionki.f("plakat", rozmiar)
    o = f.render(napis, True, (250, 240, 255))
    r = o.get_rect(topleft=poz).inflate(16, 8)
    pygame.draw.rect(s, FIOLET, r, border_radius=6)
    s.blit(o, o.get_rect(center=r.center))
    return r


# ------------------------------------------------------------------ dźwięki
class Dzwieki:
    """Proste efekty generowane w locie (bez plików)."""

    def __init__(self):
        self.ok = False
        self.bank = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(22050, -16, 1, 512)
            self.ok = pygame.mixer.get_init() is not None
        except pygame.error:
            self.ok = False
        if self.ok:
            try:
                self.bank = {
                    "klik": self._ton([(880, 0.03)], 0.25),
                    "maszyna": self._szum(0.025, 0.3),
                    "stempel": self._szum(0.09, 0.5, niski=True),
                    "sukces": self._ton([(523, 0.12), (659, 0.12), (784, 0.22)], 0.3),
                    "blad": self._ton([(220, 0.12), (180, 0.2)], 0.3),
                    "kartka": self._szum(0.12, 0.18),
                }
            except Exception:
                self.ok = False

    def _ton(self, nuty, glosnosc):
        sr = 22050
        a = array.array("h")
        for f, t in nuty:
            n = int(sr * t)
            for i in range(n):
                obw = min(1.0, i / 200) * max(0.0, 1 - i / n)
                a.append(int(32767 * glosnosc * obw * math.sin(2 * math.pi * f * i / sr)))
        return pygame.mixer.Sound(buffer=a.tobytes())

    def _szum(self, t, glosnosc, niski=False):
        sr = 22050
        rng = random.Random(4)
        a = array.array("h")
        n = int(sr * t)
        prev = 0.0
        for i in range(n):
            v = rng.uniform(-1, 1)
            if niski:
                prev = prev * 0.9 + v * 0.1
                v = prev * 3
            a.append(int(32767 * glosnosc * max(0.0, 1 - i / n) * max(-1, min(1, v))))
        return pygame.mixer.Sound(buffer=a.tobytes())

    def graj(self, nazwa):
        if self.ok and nazwa in self.bank:
            try:
                self.bank[nazwa].play()
            except pygame.error:
                pass
