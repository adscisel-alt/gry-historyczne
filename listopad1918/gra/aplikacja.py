"""Główna pętla, stos scen, kolejka zdarzeń logiki, zapis i efekty ekranu (ziarno filmu)."""
import collections
import os
import random

import pygame

from .config import W, H, FPS, TYTUL, sep, katalog_zapisu
from . import grafika as G
from . import czcionki
from . import ui
from . import sceny
from .minigry import REJESTR
from .stan import Gra, Stan, Zdarzenie
from .dane import fakty as F
from .dane import rozdzialy as R


class Aplikacja:
    def __init__(self, okno=True, sciezka_zapisu=None):
        pygame.init()
        pygame.display.set_caption(TYTUL)
        self.ekran = None
        if okno:
            try:
                self.ekran = pygame.display.set_mode((W, H), pygame.SCALED | pygame.RESIZABLE)
            except pygame.error:
                self.ekran = pygame.display.set_mode((W, H))
            try:
                pygame.display.set_icon(G.ikona("orzelek", 32))
            except pygame.error:
                pass
        self.plotno = pygame.Surface((W, H))
        self.zegar = pygame.time.Clock()
        self.dzwieki = ui.Dzwieki()
        self.sciezka_zapisu = sciezka_zapisu or os.path.join(katalog_zapisu(), "zapis.json")
        self.gra = Gra()
        self.stos = []
        self.kolejka = collections.deque()
        self.toasty = []
        self.dziala = True
        self.czas = 0.0
        self.rng = random.Random()
        self._mysz = (0, 0)
        self.ustaw_baze(sceny.Menu(self))

    # ------------------------------------------------------------ stos scen
    @property
    def gora(self):
        return self.stos[-1] if self.stos else None

    def ustaw_baze(self, scena):
        self.stos = [scena]

    def wloz(self, scena):
        self.stos.append(scena)

    def zdejmij(self, scena):
        if scena in self.stos:
            self.stos.remove(scena)

    def lokacja(self):
        for s in self.stos:
            if isinstance(s, sceny.Lokacja):
                return s
        return None

    def mysz(self):
        return self._mysz

    # ------------------------------------------------------------ przebieg gry
    def jest_zapis(self):
        return os.path.exists(self.sciezka_zapisu)

    def zapisz(self):
        try:
            self.gra.stan.zapisz(self.sciezka_zapisu)
        except OSError:
            pass

    def nowa_gra(self):
        self.gra = Gra()
        self.kolejka.clear()
        self.ustaw_baze(sceny.KartaRozdzialu(self))

    def kontynuuj(self):
        st = Stan.wczytaj(self.sciezka_zapisu)
        if st is None:
            return self.nowa_gra()
        self.gra = Gra(st)
        self.kolejka.clear()
        if st.ukonczona:
            self.ustaw_baze(sceny.Zakonczenie(self))
        else:
            self.ustaw_baze(sceny.KartaRozdzialu(self))

    def rozpocznij_lokacje(self):
        self.gra.stan.lokacja = self.gra.rozdzial["start"] if self.gra.stan.lokacja not in R.LOKACJE else self.gra.stan.lokacja
        if R.LOKACJE[self.gra.stan.lokacja]["rozdzial"] != self.gra.rozdzial["id"]:
            self.gra.stan.lokacja = self.gra.rozdzial["start"]
        self.ustaw_baze(sceny.Lokacja(self))
        self.zapisz()

    def nastepny_rozdzial(self):
        if self.gra.stan.nastepny_rozdzial():
            self.zapisz()
            self.ustaw_baze(sceny.KartaRozdzialu(self))
        else:
            self.zapisz()
            self.ustaw_baze(sceny.Zakonczenie(self))

    def do_menu(self):
        if self.lokacja():
            self.zapisz()
        self.kolejka.clear()
        self.ustaw_baze(sceny.Menu(self))

    def otworz_dziennik(self):
        if not isinstance(self.gora, sceny.Dziennik):
            self.wloz(sceny.Dziennik(self))

    def przelacz_ekran(self):
        try:
            pygame.display.toggle_fullscreen()
        except pygame.error:
            pass

    def wyjdz(self):
        self.dziala = False

    # ------------------------------------------------------------ zdarzenia logiki
    def obsluz(self, zdarzenia):
        self.kolejka.extend(zdarzenia)
        self.przetworz_kolejke()

    def na_poczatek(self, zdarzenia):
        for z in reversed(list(zdarzenia)):
            self.kolejka.appendleft(z)
        self.przetworz_kolejke()

    def przetworz_kolejke(self):
        """Wykonuje zdarzenia po kolei; zatrzymuje się, gdy otwarta jest nakładka (dialog, minigra…)."""
        while self.kolejka and isinstance(self.gora, sceny.Lokacja):
            rodzaj, arg = self.kolejka.popleft()
            lok = self.gora
            if rodzaj == Zdarzenie.MOW:
                lok.komunikat(arg)
            elif rodzaj in (Zdarzenie.FAKT, Zdarzenie.PRZEDMIOT):
                self.toast(rodzaj, arg)
            elif rodzaj == Zdarzenie.IDZ:
                lok.ustaw(arg)
                self.dzwieki.graj("kartka")
                self.zapisz()
            elif rodzaj == Zdarzenie.DIALOG:
                self.wloz(sceny.RozmowaScena(self, arg))
            elif rodzaj == Zdarzenie.MINIGRA:
                self.wloz(REJESTR[arg](self))
            elif rodzaj == Zdarzenie.DAMIAN:
                self.wloz(sceny.DamianScena(self, arg))
            elif rodzaj == Zdarzenie.MIT:
                self.wloz(sceny.MitScena(self, arg))
            elif rodzaj == Zdarzenie.KONIEC_ROZDZIALU:
                self.wloz(sceny.Podsumowanie(self))

    def toast(self, rodzaj, arg):
        if rodzaj == Zdarzenie.FAKT:
            tekst = "Nowy fakt w dzienniku: " + F.FAKTY[arg]["data"]
        else:
            tekst = "Do torby: " + R.PRZEDMIOTY[arg]["nazwa"]
            self.dzwieki.graj("kartka")
        self.toasty.append([tekst, 3.0])

    # ------------------------------------------------------------ pętla
    def klatka(self, dt, zdarzenia=()):
        """Jedna klatka gry: zdarzenia → aktualizacja → rysowanie (używane też przez testy)."""
        for e in zdarzenia:
            if e.type == pygame.QUIT:
                self.dziala = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                self.przelacz_ekran()
            elif e.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                self._mysz = e.pos
                if e.type != pygame.MOUSEMOTION and self.gora:
                    self.gora.zdarzenie(e)
            elif self.gora:
                self.gora.zdarzenie(e)
        self.czas += dt
        for s in list(self.stos):
            s.aktualizuj(dt) if s is self.gora or isinstance(s, sceny.Lokacja) else None
        self.przetworz_kolejke()
        for t in self.toasty:
            t[1] -= dt
        self.toasty = [t for t in self.toasty if t[1] > 0]
        self.rysuj()

    def rysuj(self):
        s = self.plotno
        # narysuj od ostatniej niemodalnej sceny
        start = 0
        for i, sc in enumerate(self.stos):
            if not sc.modalna:
                start = i
        for sc in self.stos[start:]:
            sc.rysuj(s)
        # toasty
        for i, (tekst, t) in enumerate(self.toasty[-4:]):
            f = czcionki.f("plakat", 16)
            o = f.render(tekst, True, sep(25))
            r = o.get_rect(topright=(W - 24, 70 + i * 40)).inflate(20, 10)
            pygame.draw.rect(s, sep(238), r, border_radius=5)
            pygame.draw.rect(s, sep(60), r, 2, border_radius=5)
            s.blit(o, o.get_rect(center=r.center))
        # ziarno filmu i migotanie
        G.naloz_kafel(s, G.kafel_szumu(256, 22, 2 + int(self.czas * 24) % 3), self.rng.randint(0, 255), self.rng.randint(0, 255))
        if self.rng.random() < 0.04:
            x = self.rng.randint(0, W)
            pygame.draw.line(s, sep(235), (x, 0), (x + self.rng.randint(-4, 4), H), 1)
        if self.ekran is not None:
            self.ekran.blit(s, (0, 0))
            pygame.display.flip()

    def uruchom(self):
        while self.dziala:
            dt = min(0.05, self.zegar.tick(FPS) / 1000.0)
            self.klatka(dt, pygame.event.get())
        if self.lokacja():
            self.zapisz()
        pygame.quit()
