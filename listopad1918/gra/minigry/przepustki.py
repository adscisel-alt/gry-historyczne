"""Rozdział 4: weryfikacja przepustek na peron Dworca Wiedeńskiego."""
import pygame

from ..config import sep, CZERWIEN_STEMPLA
from .. import grafika as G
from .. import ui
from ..dane import minigry_dane as MD
from .baza import Minigra


class Przepustki(Minigra):
    gid = "przepustki"
    tytul = "Bramka na peron — 10 XI 1918, godz. 6.40"
    instrukcja = ("Sprawdź każdą przepustkę z zasadami komendanta Koca i listą powitalną. Przepuść albo zatrzymaj. "
                  "Musisz ocenić poprawnie co najmniej %d z %d dokumentów." % (MD.PRZEPUSTKI_PROG, len(MD.PRZEPUSTKI)))

    def __init__(self, app):
        super().__init__(app)
        self.reset()
        self.b_tak = ui.Przycisk((500, 560, 200, 56), "Przepuść ✔", lambda: self.decyzja(True), 22)
        self.b_nie = ui.Przycisk((720, 560, 200, 56), "Zatrzymaj ✖", lambda: self.decyzja(False), 22)
        self.b_znowu = ui.Przycisk((560, 560, 300, 56), "Jeszcze raz", self.reset, 22)

    def reset(self):
        self.indeks = 0
        self.poprawne = 0
        self.koniec = False
        self.komunikat = ""

    @property
    def dokument(self):
        return MD.PRZEPUSTKI[self.indeks] if self.indeks < len(MD.PRZEPUSTKI) else None

    def decyzja(self, przepusc):
        doc = self.dokument
        if doc is None:
            return
        wazna = MD.przepustka_wazna(doc)
        if przepusc == wazna:
            self.poprawne += 1
            self.info("Dobrze! " + ("Przepustka w porządku." if wazna else "Zatrzymana: " + MD.powod_odrzucenia(doc) + "."))
        else:
            self.info("Ups! " + ("Ta przepustka była dobra." if wazna else "Trzeba było zatrzymać: " + MD.powod_odrzucenia(doc) + "."), False)
        self.app.dzwieki.graj("stempel")
        self.indeks += 1
        if self.indeks >= len(MD.PRZEPUSTKI):
            if self.poprawne >= MD.PRZEPUSTKI_PROG:
                self.wygraj()
            else:
                self.koniec = True
                self.info("Wynik %d/%d — za mało. Koc wzdycha i podaje ci stos jeszcze raz." % (self.poprawne, len(MD.PRZEPUSTKI)), False)

    def klik(self, poz):
        if self.koniec:
            self.b_znowu.klik(poz)
        else:
            self.b_tak.klik(poz) or self.b_nie.klik(poz)

    def klawisz(self, k):
        if not self.koniec and k in (pygame.K_t, pygame.K_LEFT):
            self.decyzja(True)
        elif not self.koniec and k in (pygame.K_n, pygame.K_RIGHT):
            self.decyzja(False)

    def rysuj_gre(self, s):
        mysz = self.app.mysz()
        # zasady
        ui.karta(s, (40, 130, 360, 250), 230)
        G.tekst(s, "Zasady komendanta Koca", (60, 145), 18, 25, "plakat")
        for i, z in enumerate(MD.ZASADY_PRZEPUSTEK):
            G.tekst(s, "• " + z, (60, 180 + i * 34), 17, 30)
        ui.karta(s, (40, 400, 360, 250), 225)
        G.tekst(s, "Lista powitalna", (60, 415), 18, 25, "plakat")
        for i, n in enumerate(MD.LISTA_POWITALNA):
            G.tekst(s, n, (70 + (i % 2) * 160, 450 + (i // 2) * 34), 18, 30, "reka")
        G.tekst(s, "Dokument %d / %d     Poprawnie: %d" % (min(self.indeks + 1, len(MD.PRZEPUSTKI)), len(MD.PRZEPUSTKI), self.poprawne),
                (500, 130), 18, 50)
        doc = self.dokument
        if doc:
            nazwisko, data, pieczec, podpis = doc
            ui.karta(s, (500, 165, 600, 370), 238)
            G.tekst(s, "PRZEPUSTKA NA PERON", (800, 200), 26, 25, "plakat", srodek=True)
            G.tekst(s, "Dworzec Wiedeński — powitanie", (800, 232), 16, 70, srodek=True)
            G.tekst(s, "Nazwisko:", (540, 280), 18, 60)
            G.tekst(s, nazwisko, (680, 274), 26, 25, "reka")
            G.tekst(s, "Data:", (540, 330), 18, 60)
            G.tekst(s, data, (680, 324), 26, 25, "reka")
            G.tekst(s, "Podpis:", (540, 380), 18, 60)
            if podpis:
                pts = [(690 + i * 12, 392 + (8 if i % 2 else -6)) for i in range(12)]
                pygame.draw.lines(s, sep(30), False, pts, 2)
            else:
                G.tekst(s, "……………………", (680, 380), 18, 120)
            kolor = CZERWIEN_STEMPLA if pieczec != "Generalgouvernement" else sep(40)
            G.stempel_okragly(s, (980, 440), pieczec.upper()[:16], 62, kolor)
        if self.koniec:
            self.b_znowu.rysuj(s, mysz)
        elif doc:
            self.b_tak.rysuj(s, mysz)
            self.b_nie.rysuj(s, mysz)
            G.tekst(s, "klawisze: T = przepuść, N = zatrzymaj", (940, 575), 14, 90)
