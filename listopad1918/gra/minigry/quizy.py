"""Rozdział 7: quiz o prawach wyborczych kobiet i finałowe dopasowanie „kto co wniósł”."""
import random

import pygame

from ..config import sep, FIOLET, CZERWIEN_STEMPLA
from .. import grafika as G
from .. import ui
from ..dane import minigry_dane as MD
from ..dane import postacie as P
from .baza import Minigra


class PrawaKobiet(Minigra):
    gid = "prawa_kobiet"
    tytul = "Zebranie Ligi Kobiet — 28 XI 1918"
    instrukcja = "Zofia Moraczewska sprawdza, czy uważałeś. Odpowiedz poprawnie na co najmniej %d z %d pytań." % (
        MD.QUIZ_KOBIET_PROG, len(MD.QUIZ_KOBIET))

    def __init__(self, app):
        super().__init__(app)
        self.reset()
        self.b_znowu = ui.Przycisk((490, 590, 300, 50), "Jeszcze raz", self.reset)

    def reset(self):
        self.pytanie = 0
        self.dobre = 0
        self.przegrana = False
        self.komunikat = ""

    def odpowiedz(self, i):
        if self.przegrana or self.pytanie >= len(MD.QUIZ_KOBIET):
            return
        _, opcje, dobra = MD.QUIZ_KOBIET[self.pytanie]
        if i == dobra:
            self.dobre += 1
            self.info("Zgadza się! " + opcje[dobra] + ".")
        else:
            self.info("Niestety. Poprawnie: " + opcje[dobra] + ".", False)
        self.pytanie += 1
        if self.pytanie >= len(MD.QUIZ_KOBIET):
            if self.dobre >= MD.QUIZ_KOBIET_PROG:
                self.wygraj()
            else:
                self.przegrana = True
                self.info("Wynik %d/%d. Zajrzyj do dziennika (zakładka „Prawa kobiet”) i spróbuj jeszcze raz." % (
                    self.dobre, len(MD.QUIZ_KOBIET)), False)

    def rect_odp(self, i):
        return pygame.Rect(320, 330 + i * 76, 820, 64)

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

    def rysuj_gre(self, s):
        mysz = self.app.mysz()
        s.blit(G.portret("moraczewska", 170), (80, 150))
        G.tekst(s, "Wynik: %d" % self.dobre, (110, 380), 20, 30, "plakat")
        if not self.przegrana and self.pytanie < len(MD.QUIZ_KOBIET):
            pyt, opcje, _ = MD.QUIZ_KOBIET[self.pytanie]
            G.tekst(s, "Pytanie %d / %d" % (self.pytanie + 1, len(MD.QUIZ_KOBIET)), (320, 150), 16, 70)
            ui.akapit(s, pyt, (320, 180, 880, 120), 28, 25, "reka")
            for i, o in enumerate(opcje):
                r = self.rect_odp(i)
                G.przycisk(s, r, "%d. %s" % (i + 1, o), r.collidepoint(mysz), 21)
        if self.przegrana:
            self.b_znowu.rysuj(s, mysz)


class Wklady(Minigra):
    gid = "wklady"
    tytul = "Album Damiana: kto co wniósł?"
    instrukcja = ("Każdy wniósł do niepodległości co innego. Kliknij osobę po lewej, a potem jej wkład po prawej. "
                  "Gdy połączysz wszystkie pary, album będzie kompletny.")
    ton_tla = 210

    def __init__(self, app):
        super().__init__(app)
        self.osoby = [p for p, _ in MD.WKLADY]
        self.wklady = [w for _, w in MD.WKLADY]
        random.Random(1918).shuffle(self.wklady)
        self.pary = {}
        self.wybrana = None
        self.poprawne = dict(MD.WKLADY)

    @staticmethod
    def nazwa(pid):
        return "Rada Regencyjna" if pid == "rada" else P.imie(pid)

    def polacz(self, osoba, wklad):
        if self.poprawne[osoba] == wklad:
            self.pary[osoba] = wklad
            self.wybrana = None
            self.info("Tak! %s — %s." % (self.nazwa(osoba), wklad.lower()))
            if len(self.pary) == len(self.osoby):
                self.wygraj()
            return True
        self.info("To raczej nie %s. Pomyśl, gdzie spotkałeś tę osobę." % self.nazwa(osoba), False)
        return False

    def rect_osoby(self, i):
        return pygame.Rect(40, 125 + i * 66, 420, 60)

    def rect_wkladu(self, i):
        return pygame.Rect(640, 125 + i * 66, 600, 60)

    def klik(self, poz):
        for i, o in enumerate(self.osoby):
            if self.rect_osoby(i).collidepoint(poz) and o not in self.pary:
                self.wybrana = o
                self.app.dzwieki.graj("klik")
                return
        if self.wybrana:
            for i, w in enumerate(self.wklady):
                if self.rect_wkladu(i).collidepoint(poz) and w not in self.pary.values():
                    self.polacz(self.wybrana, w)
                    return

    def rysuj_gre(self, s):
        mysz = self.app.mysz()
        for i, o in enumerate(self.osoby):
            r = self.rect_osoby(i)
            G.przycisk(s, r, "", r.collidepoint(mysz) or o == self.wybrana, 18, o in self.pary)
            if o == self.wybrana:
                pygame.draw.rect(s, FIOLET, r, 3, border_radius=4)
            s.blit(G.portret("kakowski" if o == "rada" else o, 46), (r.x + 8, r.y + 3))
            G.tekst(s, self.nazwa(o), (r.x + 66, r.y + 18), 19, 25, "plakat")
        for i, w in enumerate(self.wklady):
            r = self.rect_wkladu(i)
            uzyty = w in self.pary.values()
            G.przycisk(s, r, "", r.collidepoint(mysz), 18, uzyty)
            ui.akapit(s, w, (r.x + 14, r.y + 8, r.w - 28, r.h), 18, 25, odstep=0)
        for o, w in self.pary.items():
            a = self.rect_osoby(self.osoby.index(o)).midright
            b = self.rect_wkladu(self.wklady.index(w)).midleft
            pygame.draw.line(s, FIOLET, a, b, 3)
