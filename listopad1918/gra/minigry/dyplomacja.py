"""Rozdział 6: dyplomacja z paskami poparcia Francji, Anglii i USA."""
import pygame

from ..config import sep, FIOLET, CZERWIEN_STEMPLA
from .. import grafika as G
from .. import ui
from ..dane import minigry_dane as MD
from ..dane import postacie as P
from .baza import Minigra


class Dyplomacja(Minigra):
    gid = "dyplomacja"
    tytul = "Salon dyplomatyczny — Paryż, listopad 1918"
    instrukcja = ("Odpowiadaj dyplomatom. Każda odpowiedź zmienia poparcie trzech mocarstw. Na koniec każde musi mieć "
                  "co najmniej %d%%. Argumenty z rozmów z Dmowskim i z depeszy Paderewskiego bardzo pomagają!" % MD.DYPLOMACJA_PROG)
    ton_tla = 200

    def __init__(self, app):
        super().__init__(app)
        self.reset()
        self.b_znowu = ui.Przycisk((490, 590, 300, 50), "Spróbuj jeszcze raz", self.reset)

    def reset(self):
        self.paski = dict(MD.DYPLOMACJA_START)
        self.wyswietlane = {k: float(v) for k, v in self.paski.items()}
        self.runda = 0
        self.ostatnie = None
        self.przegrana = False
        self.komunikat = ""

    def odpowiedz(self, i):
        if self.runda >= len(MD.DYPLOMACJA_RUNDY) or self.przegrana:
            return
        tekst, zmiany = MD.DYPLOMACJA_RUNDY[self.runda]["odpowiedzi"][i]
        for p, d in zmiany.items():
            self.paski[p] = max(0, min(100, self.paski[p] + d))
        self.ostatnie = zmiany
        opis = ", ".join("%s %+d" % (p, d) for p, d in zmiany.items() if d)
        self.info("Reakcja: " + (opis or "bez zmian"), sum(zmiany.values()) >= 0)
        self.runda += 1
        if self.runda >= len(MD.DYPLOMACJA_RUNDY):
            if MD.dyplomacja_wygrana(self.paski):
                self.wygraj()
            else:
                self.przegrana = True
                slabe = [p for p, v in self.paski.items() if v < MD.DYPLOMACJA_PROG]
                self.info("Za słabe poparcie: %s. Dyplomacja to cierpliwość — spróbuj jeszcze raz." % ", ".join(slabe), False)

    def rect_odp(self, i):
        return pygame.Rect(320, 380 + i * 72, 920, 64)

    def klik(self, poz):
        if self.przegrana:
            self.b_znowu.klik(poz)
            return
        for i in range(3):
            if self.rect_odp(i).collidepoint(poz):
                self.odpowiedz(i)
                return

    def klawisz(self, k):
        if pygame.K_1 <= k <= pygame.K_3:
            self.odpowiedz(k - pygame.K_1)

    def aktualizuj(self, dt):
        super().aktualizuj(dt)
        for k in self.wyswietlane:
            self.wyswietlane[k] += (self.paski[k] - self.wyswietlane[k]) * min(1, dt * 5)

    def rysuj_gre(self, s):
        mysz = self.app.mysz()
        for i, p in enumerate(MD.PANSTWA):
            x = 60 + i * 400
            G.tekst(s, p, (x, 125), 20, 25, "plakat")
            pygame.draw.rect(s, sep(170), (x, 152, 340, 28), border_radius=6)
            v = self.wyswietlane[p]
            pygame.draw.rect(s, FIOLET if v >= MD.DYPLOMACJA_PROG else sep(70), (x, 152, int(340 * v / 100), 28), border_radius=6)
            px = x + int(340 * MD.DYPLOMACJA_PROG / 100)
            pygame.draw.line(s, CZERWIEN_STEMPLA, (px, 146), (px, 186), 3)
            G.tekst(s, "%d%%" % round(v), (x + 350, 154), 18, 25, "plakat")
        if self.runda < len(MD.DYPLOMACJA_RUNDY) and not self.przegrana:
            r = MD.DYPLOMACJA_RUNDY[self.runda]
            s.blit(G.portret(r["kto"], 150), (60, 210))
            G.tekst(s, P.imie(r["kto"]), (135, 400), 16, 40, "plakat", srodek=True)
            G.tekst(s, "Runda %d / %d" % (self.runda + 1, len(MD.DYPLOMACJA_RUNDY)), (320, 210), 16, 70)
            ui.akapit(s, "„" + r["pytanie"] + "”", (320, 240, 900, 120), 26, 25, "reka")
            for i, (tekst, _) in enumerate(r["odpowiedzi"]):
                rr = self.rect_odp(i)
                G.przycisk(s, rr, "", rr.collidepoint(mysz))
                ui.akapit(s, "%d. %s" % (i + 1, tekst), (rr.x + 14, rr.y + 10, rr.w - 28, rr.h), 18, 25, odstep=0)
        if self.przegrana:
            self.b_znowu.rysuj(s, mysz)
