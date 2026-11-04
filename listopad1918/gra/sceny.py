"""Sceny gry: menu, karty rozdziałów, lokacje, dialogi, Damian, mity, dziennik, zakończenie."""
import math
import random

import pygame

from .config import W, H, SCENA_H, PANEL_Y, sep, FIOLET, CZERWIEN_STEMPLA, TYTUL
from . import czcionki
from . import grafika as G
from . import ui
from .stan import Zdarzenie
from .dane import rozdzialy as R
from .dane import postacie as P
from .dane import fakty as F

STOPA_Y = 548     # linia, na której stoją postacie


class Scena:
    modalna = False

    def __init__(self, app):
        self.app = app
        self.czas = 0.0

    def zdarzenie(self, e):
        pass

    def aktualizuj(self, dt):
        self.czas += dt

    def rysuj(self, s):
        pass

    def zamknij(self):
        self.app.zdejmij(self)


# ====================================================================== MENU
class Menu(Scena):
    def __init__(self, app):
        super().__init__(app)
        self.przyciski = []
        opcje = [("Nowa gra", self.nowa)]
        if app.jest_zapis():
            opcje.append(("Kontynuuj", self.kontynuuj))
        opcje += [("Pełny ekran (F11)", app.przelacz_ekran), ("Wyjście", app.wyjdz)]
        for i, (napis, akcja) in enumerate(opcje):
            self.przyciski.append(ui.Przycisk((490, 318 + i * 58, 300, 48), napis, akcja))
        rng = random.Random(1918)
        self.postacie = list(P.HISTORYCZNE)
        rng.shuffle(self.postacie)

    def nowa(self):
        self.app.nowa_gra()

    def kontynuuj(self):
        self.app.kontynuuj()

    def zdarzenie(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for p in self.przyciski:
                if p.klik(e.pos):
                    self.app.dzwieki.graj("klik")
                    return
        if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
            self.nowa()

    def rysuj(self, s):
        s.blit(G.papier(W, H, 200, seed=77), (0, 0))
        # kolaż sylwetek-wycinanek
        for i, pid in enumerate(self.postacie):
            syl = G.sylwetka(pid, 0.55)
            x = 40 + i * 80
            y = H - syl.get_height() + 20 + int(math.sin(self.czas * 0.8 + i) * 4)
            s.blit(syl, (x, y))
        ui.karta(s, (300, 50, 680, 250), 232)
        G.stempel_okragly(s, (930, 250), "WARSZAWA 1918", 44)
        G.tekst(s, "LISTOPAD 1918", (640, 120), 64, 25, "plakat", srodek=True)
        G.tekst(s, "Pocztówki z niepodległości", (640, 180), 30, 50, "reka", srodek=True)
        G.tekst(s, "przygodówka w 7 rozdziałach • 31 X – 28 XI 1918", (640, 230), 18, 70, "szeryf", srodek=True)
        G.tekst(s, "Gra edukacyjna dla 11–15 lat. Janek i Damian Ściseł to postacie fikcyjne.", (640, 270), 15, 90, srodek=True)
        mysz = self.app.mysz()
        for p in self.przyciski:
            p.rysuj(s, mysz)
        # Damian w rogu
        syl = G.sylwetka("damian", 0.8)
        s.blit(syl, (W - syl.get_width() - 20, 360))


# ====================================================================== KARTA ROZDZIAŁU
class KartaRozdzialu(Scena):
    def __init__(self, app):
        super().__init__(app)
        self.r = app.gra.rozdzial

    def zdarzenie(self, e):
        if (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1) or (e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE)):
            if self.czas > 0.4:
                self.app.dzwieki.graj("kartka")
                self.app.rozpocznij_lokacje()

    def rysuj(self, s):
        s.blit(G.papier(W, H, 175, seed=5), (0, 0))
        ui.karta(s, (140, 60, 1000, 600), 230, stempel=self.r["stempel"])
        G.tekst(s, "ROZDZIAŁ %d z 7" % self.r["numer"], (640, 120), 26, 60, "plakat", srodek=True)
        G.tekst(s, self.r["tytul"], (640, 180), 54, 20, "reka", srodek=True)
        G.tekst(s, self.r["daty"] + "  •  " + self.r["miejsce"], (640, 240), 22, 60, srodek=True)
        pygame.draw.line(s, sep(120), (260, 275), (1020, 275), 2)
        s.blit(G.portret("damian", 140), (200, 310))
        ui.etykieta_fiolet(s, "Damian Ściseł, archiwista", (190, 490))
        ui.akapit(s, self.r["intro"], (380, 310, 690, 300), 21, 30)
        if int(self.czas * 2) % 2 == 0:
            G.tekst(s, "kliknij, aby wejść do pocztówki", (640, 625), 18, 80, "reka", srodek=True)


# ====================================================================== LOKACJA
class Lokacja(Scena):
    PREDKOSC = 380

    def __init__(self, app):
        super().__init__(app)
        self.komunikat_tekst = ""
        self.komunikat_t = 0.0
        self.wybrany = None
        self.janek_x = 140.0
        self.cel_x = None
        self.oczekuje = None
        self.przyciski = [
            ui.Przycisk((1040, PANEL_Y + 20, 220, 50), "Dziennik [J]", app.otworz_dziennik),
            ui.Przycisk((1040, PANEL_Y + 86, 220, 50), "Menu [Esc]", app.do_menu),
        ]
        self.ustaw(app.gra.stan.lokacja)

    # ---------------------------------------------------------- dane
    def ustaw(self, lid):
        self.lid = lid
        self.dane = R.LOKACJE[lid]
        self.tlo = G.tlo(self.dane["tlo"])
        self.janek_x = 140.0
        self.cel_x = None
        self.oczekuje = None
        self.wejscie_t = 0.0

    def rect_hotspotu(self, h):
        if "postac" in h:
            syl = G.sylwetka(h["postac"])
            w, hh = syl.get_size()
            return pygame.Rect(h["x"] - w // 2 + 14, STOPA_Y - hh + 50, w - 28, hh - 50)
        return pygame.Rect(h["rect"])

    def widoczne(self):
        return self.app.gra.hotspoty()

    def hotspot_pod(self, poz):
        hs = self.widoczne()
        # postacie i wyjścia mają pierwszeństwo przed tłem
        for h in sorted(hs, key=lambda h: 0 if ("postac" in h or h.get("wyjscie")) else 1):
            if self.rect_hotspotu(h).collidepoint(poz):
                return h
        return None

    def komunikat(self, tekst):
        self.komunikat_tekst = tekst
        self.komunikat_t = 0.0

    # ---------------------------------------------------------- akcje
    def aktywuj(self, hid, przedmiot=None):
        """Natychmiastowe wykonanie akcji (także dla automatycznych testów)."""
        gra = self.app.gra
        if przedmiot:
            zd = gra.uzyj(przedmiot, hid)
            self.wybrany = None
        else:
            zd = gra.kliknij(hid)
        self.app.dzwieki.graj("klik")
        self.app.obsluz(zd)

    def zdarzenie(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_j:
                self.app.otworz_dziennik()
            elif e.key == pygame.K_ESCAPE:
                if self.wybrany:
                    self.wybrany = None
                else:
                    self.app.do_menu()
            return
        if e.type != pygame.MOUSEBUTTONDOWN:
            return
        poz = e.pos
        if poz[1] >= PANEL_Y:
            if e.button == 1:
                for p in self.przyciski:
                    if p.klik(poz):
                        return
                i = self.slot_pod(poz)
                if i is not None:
                    eq = self.app.gra.stan.ekwipunek
                    if i < len(eq):
                        self.wybrany = None if self.wybrany == eq[i] else eq[i]
                        self.app.dzwieki.graj("klik")
            elif e.button == 3:
                i = self.slot_pod(poz)
                eq = self.app.gra.stan.ekwipunek
                if i is not None and i < len(eq):
                    p = R.PRZEDMIOTY[eq[i]]
                    self.komunikat(p["nazwa"] + ": " + p["opis"])
            return
        h = self.hotspot_pod(poz)
        if e.button == 3:
            if self.wybrany:
                self.wybrany = None
            elif h:
                self.komunikat(h.get("patrz", h["nazwa"]))
            return
        if e.button != 1:
            return
        if h:
            r = self.rect_hotspotu(h)
            if "postac" in h:
                cel = r.centerx - 120 if r.centerx > self.janek_x else r.centerx + 120
            else:
                cel = r.centerx
            self.cel_x = max(70, min(W - 70, cel))
            self.oczekuje = (h["id"], self.wybrany)
        else:
            self.cel_x = max(70, min(W - 70, poz[0]))
            self.oczekuje = None

    def slot_pod(self, poz):
        for i in range(10):
            if self.rect_slotu(i).collidepoint(poz):
                return i
        return None

    def rect_slotu(self, i):
        return pygame.Rect(420 + (i % 5) * 120, PANEL_Y + 14 + (i // 5) * 70, 110, 64)

    def aktualizuj(self, dt):
        super().aktualizuj(dt)
        self.komunikat_t += dt
        self.wejscie_t += dt
        if self.cel_x is not None:
            d = self.cel_x - self.janek_x
            krok = self.PREDKOSC * dt
            if abs(d) <= krok:
                self.janek_x = self.cel_x
                self.cel_x = None
                if self.oczekuje:
                    hid, przedmiot = self.oczekuje
                    self.oczekuje = None
                    if any(h["id"] == hid for h in self.widoczne()):
                        self.aktywuj(hid, przedmiot)
            else:
                self.janek_x += krok if d > 0 else -krok

    # ---------------------------------------------------------- rysowanie
    def rysuj(self, s):
        s.blit(self.tlo, (0, 0))
        mysz = self.app.mysz()
        pod = self.hotspot_pod(mysz) if mysz[1] < PANEL_Y else None
        hs = self.widoczne()
        for h in hs:
            if "przedmiot" in h and "postac" not in h:
                r = self.rect_hotspotu(h)
                ik = G.ikona(h["przedmiot"], 56)
                s.blit(ik, ik.get_rect(center=(r.centerx, r.centery + math.sin(self.czas * 3) * 3)))
        for h in sorted([h for h in hs if "postac" in h], key=lambda h: h["x"]):
            syl = G.sylwetka(h["postac"])
            if h.get("ramka"):
                G.ramka_sztalugi(s, (h["x"] - 130, 110, 260, 300))
            oddech = int(math.sin(self.czas * 1.6 + h["x"]) * 2)
            s.blit(syl, (h["x"] - syl.get_width() // 2, STOPA_Y - syl.get_height() + 12 + oddech))
        # Janek
        janek = G.sylwetka("janek")
        idzie = self.cel_x is not None
        podskok = abs(math.sin(self.czas * 12)) * 6 if idzie else 0
        obraz = janek
        if self.cel_x is not None and self.cel_x < self.janek_x:
            obraz = pygame.transform.flip(janek, True, False)
        s.blit(obraz, (self.janek_x - janek.get_width() // 2, STOPA_Y - janek.get_height() + 12 - podskok))
        for h in hs:
            if h.get("wyjscie"):
                G.strzalka_wyjscia(s, self.rect_hotspotu(h), self.czas)
        if pod:
            r = self.rect_hotspotu(pod)
            if "postac" not in pod and not pod.get("wyjscie"):
                ramka = pygame.Surface(r.size, pygame.SRCALPHA)
                pygame.draw.rect(ramka, (255, 245, 220, 40), ramka.get_rect(), border_radius=8)
                pygame.draw.rect(ramka, (255, 245, 220, 140), ramka.get_rect(), 2, border_radius=8)
                s.blit(ramka, r)
            napis = pod["nazwa"]
            if self.wybrany:
                napis = "Użyj: %s → %s" % (R.PRZEDMIOTY[self.wybrany]["nazwa"], pod["nazwa"])
            f = czcionki.f("plakat", 18)
            o = f.render(napis, True, sep(20))
            rr = o.get_rect(midbottom=(max(o.get_width() // 2 + 20, min(W - o.get_width() // 2 - 20, mysz[0])), max(40, mysz[1] - 18)))
            pygame.draw.rect(s, sep(235), rr.inflate(16, 8), border_radius=4)
            pygame.draw.rect(s, sep(60), rr.inflate(16, 8), 2, border_radius=4)
            s.blit(o, rr)
        # podpis pocztówki
        rozdz = self.app.gra.rozdzial
        podpis = "%s  •  %s" % (self.dane["nazwa"], self.dane["data"])
        f = czcionki.f("reka", 20)
        o = f.render(podpis, True, sep(25))
        rr = pygame.Rect(40, 12, o.get_width() + 30, 34)
        pygame.draw.rect(s, sep(232), rr, border_radius=3)
        pygame.draw.rect(s, sep(90), rr, 1, border_radius=3)
        s.blit(o, (55, 16))
        ui.etykieta_fiolet(s, "Rozdział %d: %s" % (rozdz["numer"], rozdz["tytul"]), (rr.right + 12, 16), 14)
        if self.wejscie_t < 0.5:
            przes = pygame.Surface((W, SCENA_H), pygame.SRCALPHA)
            przes.fill((20, 12, 6, int(255 * (1 - self.wejscie_t / 0.5))))
            s.blit(przes, (0, 0))
        self.rysuj_panel(s, mysz)

    def rysuj_panel(self, s, mysz):
        s.blit(G.papier(W, H - PANEL_Y, 205, seed=12), (0, PANEL_Y))
        pygame.draw.line(s, sep(40), (0, PANEL_Y), (W, PANEL_Y), 4)
        # komunikat
        tekst = self.komunikat_tekst
        widoczne = tekst[: int(self.komunikat_t * 70)] if tekst else ""
        rect = (24, PANEL_Y + 14, 370, 130)
        if widoczne:
            kto, sep_, reszta = widoczne.partition(": ")
            if sep_ and len(kto) < 28:
                G.tekst(s, kto, (24, PANEL_Y + 10), 17, 60, "plakat")
                ui.akapit(s, reszta, (24, PANEL_Y + 34, 370, 120), 17, 25, odstep=1)
            else:
                G.tekst(s, "Janek", (24, PANEL_Y + 10), 17, 60, "plakat")
                ui.akapit(s, widoczne, (24, PANEL_Y + 34, 370, 120), 17, 25, odstep=1)
        else:
            ui.akapit(s, "Lewy przycisk: działaj • prawy: oglądaj. Kliknij przedmiot w torbie, a potem cel, by go użyć.",
                      rect, 16, 90)
        # ekwipunek
        eq = self.app.gra.stan.ekwipunek
        for i in range(10):
            r = self.rect_slotu(i)
            pygame.draw.rect(s, sep(185), r, border_radius=6)
            pygame.draw.rect(s, sep(120), r, 2, border_radius=6)
            if i < len(eq):
                if eq[i] == self.wybrany:
                    pygame.draw.rect(s, FIOLET, r, 4, border_radius=6)
                ik = G.ikona(eq[i], 44)
                s.blit(ik, ik.get_rect(center=(r.centerx, r.centery - 6)))
                nazwa = R.PRZEDMIOTY[eq[i]]["nazwa"]
                f = czcionki.f("szeryf", 11)
                o = f.render(nazwa if f.size(nazwa)[0] < 104 else nazwa[:16] + "…", True, sep(30))
                s.blit(o, o.get_rect(midbottom=(r.centerx, r.bottom - 2)))
        for p in self.przyciski:
            p.rysuj(s, mysz)
        if self.wybrany:
            ik = G.ikona(self.wybrany, 40)
            s.blit(ik, (mysz[0] + 12, mysz[1] + 12))


# ====================================================================== DIALOG
class RozmowaScena(Scena):
    modalna = True

    def __init__(self, app, did):
        super().__init__(app)
        self.rozmowa = app.gra.rozmowa(did)
        self.t_tekst = 0.0
        self.zebrane = []
        self._nowy_wezel()

    def _nowy_wezel(self):
        self.t_tekst = 0.0
        self.zebrane.extend(self.rozmowa.odbierz_zdarzenia())
        for rodzaj, arg in self.zebrane:
            if rodzaj in (Zdarzenie.FAKT, Zdarzenie.PRZEDMIOT):
                self.app.toast(rodzaj, arg)
        self.zebrane = [z for z in self.zebrane if z[0] not in (Zdarzenie.FAKT, Zdarzenie.PRZEDMIOT)]
        if self.rozmowa.zakonczona:
            self.app.zdejmij(self)
            self.app.na_poczatek(self.zebrane)

    def pelny_tekst(self):
        return self.t_tekst * 90 >= len(self.rozmowa.wezel["tekst"])

    def wybierz(self, i):
        self.app.dzwieki.graj("klik")
        self.rozmowa.wybierz(i)
        self._nowy_wezel()

    def dalej(self):
        self.rozmowa.dalej()
        self._nowy_wezel()

    def rect_opcji(self, i):
        return pygame.Rect(260, 560 + i * 36, 980, 32)

    def zdarzenie(self, e):
        if self.rozmowa.zakonczona:
            return
        opcje = self.rozmowa.opcje()
        if e.type == pygame.KEYDOWN:
            if pygame.K_1 <= e.key <= pygame.K_9 and self.pelny_tekst():
                i = e.key - pygame.K_1
                if i < len(opcje):
                    self.wybierz(i)
            elif e.key in (pygame.K_SPACE, pygame.K_RETURN):
                if not self.pelny_tekst():
                    self.t_tekst = 999
                elif not opcje:
                    self.dalej()
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if not self.pelny_tekst():
                self.t_tekst = 999
                return
            if opcje:
                for i in range(len(opcje)):
                    if self.rect_opcji(i).collidepoint(e.pos):
                        self.wybierz(i)
                        return
            else:
                self.dalej()

    def aktualizuj(self, dt):
        super().aktualizuj(dt)
        przed = int(self.t_tekst * 90)
        self.t_tekst += dt
        if int(self.t_tekst * 90) // 6 > przed // 6 and not self.pelny_tekst():
            self.app.dzwieki.graj("maszyna")

    def rysuj(self, s):
        if self.rozmowa.zakonczona:
            return
        ui.przyciemnij(s, 120)
        w = self.rozmowa.wezel
        kto = w.get("kto", "janek")
        pygame.draw.rect(s, (15, 9, 5), (28, 368, 1232, 344))
        s.blit(G.papier(1224, 336, 228, seed=21), (24, 364))
        pygame.draw.rect(s, sep(50), (24, 364, 1224, 336), 3)
        s.blit(G.portret(kto, 180), (50, 390))
        imie = P.wszystkie()[kto]["imie"]
        if kto == "damian":
            ui.etykieta_fiolet(s, imie, (52, 615), 16)
        else:
            G.tekst(s, imie, (140, 630), 17, 40, "plakat", srodek=True)
        if kto in P.HISTORYCZNE:
            G.tekst(s, P.HISTORYCZNE[kto]["lata"], (140, 655), 15, 80, srodek=True)
        tekst = w["tekst"][: int(self.t_tekst * 90)]
        ui.akapit(s, tekst, (260, 388, 970, 170), 21, 22, "szeryf", 3)
        if self.pelny_tekst():
            opcje = self.rozmowa.opcje()
            mysz = self.app.mysz()
            for i, o in enumerate(opcje):
                r = self.rect_opcji(i)
                hover = r.collidepoint(mysz)
                if hover:
                    pygame.draw.rect(s, sep(205), r, border_radius=4)
                G.tekst(s, "%d. %s" % (i + 1, o["tekst"]), (r.x + 8, r.y + 4), 19, 20 if hover else 55, "szeryf")
            if not opcje:
                G.tekst(s, "▸ kliknij lub naciśnij spację", (1000, 670), 16, 90, "reka")


# ====================================================================== DAMIAN (narrator)
class DamianScena(Scena):
    modalna = True

    def __init__(self, app, tekst):
        super().__init__(app)
        self.tekst = tekst

    def zdarzenie(self, e):
        if ((e.type == pygame.MOUSEBUTTONDOWN and e.button == 1) or
                (e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE))) and self.czas > 0.25:
            self.zamknij()

    def rysuj(self, s):
        ui.przyciemnij(s, 110)
        h = max(200, ui.wysokosc_akapitu(self.tekst, 760, 21) + 90)
        y = 150
        ui.karta(s, (190, y, 900, h), 232)
        s.blit(G.portret("damian", 130), (220, y + 30))
        ui.etykieta_fiolet(s, "Damian Ściseł weryfikuje", (380, y + 26), 15)
        ui.akapit(s, self.tekst, (380, y + 66, 680, h - 80), 21, 25)
        G.tekst(s, "▸ dalej", (1000, y + h - 34), 16, 90, "reka")


# ====================================================================== MIT CZY FAKT
class MitScena(Scena):
    modalna = True

    def __init__(self, app, mid):
        super().__init__(app)
        self.mid = mid
        self.mit = F.MITY[mid]
        self.odpowiedz = None
        self.dobrze = None

    def rect_opcji(self, i):
        return pygame.Rect(230, 330 + i * 70, 820, 60)

    def wybierz(self, i):
        self.odpowiedz = i
        self.dobrze = self.app.gra.stan.odpowiedz_mit(self.mid, i)
        self.app.dzwieki.graj("stempel" if self.dobrze else "blad")

    def zdarzenie(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.odpowiedz is None:
                for i in range(3):
                    if self.rect_opcji(i).collidepoint(e.pos):
                        self.wybierz(i)
                        return
            elif self.czas > 0.3:
                self.zamknij()
        elif e.type == pygame.KEYDOWN:
            if self.odpowiedz is None and pygame.K_1 <= e.key <= pygame.K_3:
                self.wybierz(e.key - pygame.K_1)
            elif self.odpowiedz is not None and e.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.zamknij()

    def rysuj(self, s):
        ui.przyciemnij(s, 150)
        ui.karta(s, (160, 60, 960, 600), 232)
        nr = list(F.MITY).index(self.mid) + 1
        ui.etykieta_fiolet(s, "Damian sprawdza mit nr %d z 10" % nr, (200, 90), 16)
        G.tekst(s, "MIT CZY FAKT?", (640, 150), 34, 30, "plakat", srodek=True)
        ui.akapit(s, "„" + self.mit["mit"] + "”", (240, 185, 800, 120), 24, 30, "reka", wysrodkuj=True)
        mysz = self.app.mysz()
        if self.odpowiedz is None:
            G.tekst(s, "Co naprawdę się wydarzyło?", (640, 305), 18, 70, srodek=True)
            for i, o in enumerate(self.mit["opcje"]):
                r = self.rect_opcji(i)
                G.przycisk(s, r, "", r.collidepoint(mysz))
                ui.akapit(s, "%d. %s" % (i + 1, o), (r.x + 14, r.y + 8, r.w - 28, r.h), 18, 25)
        else:
            dobra = self.mit["opcje"][self.mit["dobra"]]
            ui.akapit(s, "Prawda: " + dobra, (240, 320, 800, 80), 21, 20, "plakat")
            ui.akapit(s, self.mit["wyjasnienie"], (240, 400, 800, 160), 19, 35)
            if self.mit.get("fakt"):
                ui.akapit(s, "Źródło: " + F.FAKTY[self.mit["fakt"]]["zrodlo"], (240, 560, 800, 60), 15, 80)
            napis = "OBALONY!" if self.dobrze else "SPRAWDŹ JESZCZE RAZ"
            G.stempel_okragly(s, (990, 505), napis, 62, CZERWIEN_STEMPLA if self.dobrze else sep(60))
            G.tekst(s, "▸ kliknij, aby zapisać w dzienniku", (900, 620), 16, 90, "reka")


# ====================================================================== PODSUMOWANIE ROZDZIAŁU
class Podsumowanie(Scena):
    modalna = True

    def __init__(self, app):
        super().__init__(app)
        self.r = app.gra.rozdzial

    def zdarzenie(self, e):
        if ((e.type == pygame.MOUSEBUTTONDOWN and e.button == 1) or
                (e.type == pygame.KEYDOWN and e.key in (pygame.K_SPACE, pygame.K_RETURN))) and self.czas > 0.4:
            self.app.zdejmij(self)
            self.app.nastepny_rozdzial()

    def rysuj(self, s):
        ui.przyciemnij(s, 170)
        ui.karta(s, (240, 120, 800, 460), 232, stempel="ZWERYFIKOWANO")
        G.tekst(s, "Rozdział %d ukończony" % self.r["numer"], (640, 190), 36, 25, "plakat", srodek=True)
        G.tekst(s, self.r["tytul"], (640, 240), 28, 50, "reka", srodek=True)
        ui.akapit(s, self.r["podsumowanie"], (300, 290, 680, 120), 22, 30, wysrodkuj=True)
        st = self.app.gra.stan
        G.tekst(s, "Fakty w dzienniku: %d / %d     Mity obalone: %d / %d     Poznane postacie: %d / 12" % (
            len(st.fakty), len(F.FAKTY), sum(1 for v in st.mity.values() if v), len(F.MITY), len(st.poznani)),
            (640, 450), 18, 60, srodek=True)
        G.tekst(s, "Gra zapisana automatycznie. ▸ kliknij", (640, 530), 16, 90, "reka", srodek=True)


# ====================================================================== DZIENNIK
class Dziennik(Scena):
    modalna = True
    ZAKLADKI = ["Fakty", "Mity", "Postacie", "Mapa zaborów", "Prawa kobiet"]

    def __init__(self, app):
        super().__init__(app)
        self.zakladka = 0
        self.strona = 0

    def rect_zakladki(self, i):
        return pygame.Rect(90 + i * 190, 40, 180, 44)

    def zdarzenie(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_j):
                self.zamknij()
            elif e.key == pygame.K_RIGHT:
                self.strona += 1
            elif e.key == pygame.K_LEFT:
                self.strona = max(0, self.strona - 1)
            elif e.key == pygame.K_TAB:
                self.zakladka = (self.zakladka + 1) % len(self.ZAKLADKI)
                self.strona = 0
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i in range(len(self.ZAKLADKI)):
                if self.rect_zakladki(i).collidepoint(e.pos):
                    self.zakladka, self.strona = i, 0
                    self.app.dzwieki.graj("kartka")
                    return
            if pygame.Rect(1080, 40, 120, 44).collidepoint(e.pos):
                self.zamknij()
            elif pygame.Rect(1060, 640, 140, 40).collidepoint(e.pos):
                self.strona += 1
                self.app.dzwieki.graj("kartka")
            elif pygame.Rect(80, 640, 140, 40).collidepoint(e.pos):
                self.strona = max(0, self.strona - 1)
                self.app.dzwieki.graj("kartka")

    def rysuj(self, s):
        ui.przyciemnij(s, 190)
        pygame.draw.rect(s, sep(60), (50, 70, 1180, 630), border_radius=10)
        s.blit(G.papier(1160, 610, 230, seed=33), (60, 80))
        pygame.draw.line(s, sep(150), (640, 100), (640, 680), 2)
        mysz = self.app.mysz()
        for i, n in enumerate(self.ZAKLADKI):
            G.przycisk(s, self.rect_zakladki(i), n, i == self.zakladka or self.rect_zakladki(i).collidepoint(mysz), 18)
        G.przycisk(s, (1080, 40, 120, 44), "Zamknij", pygame.Rect(1080, 40, 120, 44).collidepoint(mysz), 18)
        G.tekst(s, "Dziennik Janka", (640, 18), 18, 225, "reka", srodek=True)
        elementy = [self._fakty, self._mity, self._postacie, self._mapa, self._kobiety][self.zakladka]()
        # elementy: lista funkcji rysujących w kolumnie (zwracają wysokość) -> paginacja na dwie kolumny
        strony = self._paginuj(elementy)
        self.strona = min(self.strona, max(0, len(strony) - 1))
        if strony:
            for k, kolumna in enumerate(strony[self.strona]):
                x = 90 if k == 0 else 670
                y = 105
                for fn, wys in kolumna:
                    fn(s, x, y)
                    y += wys + 14
        if len(strony) > 1:
            G.tekst(s, "strona %d / %d" % (self.strona + 1, len(strony)), (640, 660), 16, 80, srodek=True)
            if self.strona > 0:
                G.przycisk(s, (80, 640, 140, 40), "◂ wstecz", False, 16)
            if self.strona < len(strony) - 1:
                G.przycisk(s, (1060, 640, 140, 40), "dalej ▸", False, 16)

    def _paginuj(self, elementy, wys_kol=520):
        strony, biez, kol, y = [], [], [], 0
        for el in elementy:
            if y + el[1] > wys_kol and kol:
                biez.append(kol)
                kol, y = [], 0
                if len(biez) == 2:
                    strony.append(biez)
                    biez = []
            kol.append(el)
            y += el[1] + 14
        if kol:
            biez.append(kol)
        if biez:
            strony.append(biez)
        return strony

    def _fakty(self):
        st = self.app.gra.stan
        if not st.fakty:
            return [(lambda s, x, y: ui.akapit(s, "Jeszcze pusto. Klikaj, oglądaj i rozmawiaj — fakty same tu trafią.", (x, y, 520, 80), 19, 60), 60)]
        el = []
        for fid in st.fakty:
            fk = F.FAKTY[fid]
            h = ui.wysokosc_akapitu(fk["tekst"], 520, 17, odstep=1) + ui.wysokosc_akapitu(fk["zrodlo"], 520, 14, odstep=0) + 26

            def rys(s, x, y, fk=fk):
                G.tekst(s, fk["data"], (x, y), 18, 25, "plakat")
                hh = ui.akapit(s, fk["tekst"], (x, y + 24, 520, 200), 17, 30, odstep=1)
                ui.akapit(s, "Źródło: " + fk["zrodlo"], (x, y + 24 + hh, 520, 60), 14, 90, odstep=0)
            el.append((rys, h))
        return el

    def _mity(self):
        st = self.app.gra.stan
        el = []
        for mid, m in F.MITY.items():
            if mid in st.mity:
                prawda = m["opcje"][m["dobra"]]
                h = ui.wysokosc_akapitu("MIT: " + m["mit"], 520, 17, odstep=1) + ui.wysokosc_akapitu("PRAWDA: " + prawda, 520, 16, odstep=1) + 8

                def rys(s, x, y, m=m, prawda=prawda, ok=st.mity[mid]):
                    hh = ui.akapit(s, "MIT: " + m["mit"], (x, y, 520, 200), 17, 70, "reka", odstep=1)
                    ui.akapit(s, ("✔ " if ok else "") + "PRAWDA: " + prawda, (x, y + hh, 520, 200), 16, 25, odstep=1)
                el.append((rys, h))
            else:
                el.append((lambda s, x, y: G.tekst(s, "??? — mit jeszcze nie sprawdzony", (x, y), 17, 120, "reka"), 24))
        return el

    def _postacie(self):
        st = self.app.gra.stan
        el = []
        for pid, p in P.HISTORYCZNE.items():
            if pid in st.poznani:
                h = max(130, ui.wysokosc_akapitu(p["biogram"], 420, 14, odstep=0) + ui.wysokosc_akapitu(p["rola"], 420, 14, "reka", 0) + 28)

                def rys(s, x, y, pid=pid, p=p):
                    s.blit(G.portret(pid, 96), (x, y))
                    G.tekst(s, "%s (%s)" % (p["imie"], p["lata"]), (x + 110, y), 17, 20, "plakat")
                    hr = ui.akapit(s, p["rola"], (x + 110, y + 22, 420, 40), 14, 60, "reka", odstep=0)
                    ui.akapit(s, p["biogram"], (x + 110, y + 26 + hr, 420, 300), 14, 30, odstep=0)
                el.append((rys, h))
            else:
                el.append((lambda s, x, y: G.tekst(s, "??? — postać jeszcze niepoznana", (x, y + 10), 17, 120, "reka"), 40))
        return el

    def _mapa(self):
        def rys(s, x, y):
            G.mapa(s, (x + 20, y, 1040, 470), 222)
            G.tekst(s, "Ziemie polskie pod zaborami (uproszczenie, granice z 1914 r.)", (x + 540, y + 488), 16, 70, "reka", srodek=True)
        return [(rys, 10)]

    def _kobiety(self):
        pk = F.PRAWA_KOBIET
        el = [(lambda s, x, y: G.tekst(s, pk["tytul"], (x, y), 22, 20, "plakat"), 30)]
        for a in pk["akapity"]:
            el.append((lambda s, x, y, a=a: ui.akapit(s, a, (x, y, 520, 300), 16, 30, odstep=1), ui.wysokosc_akapitu(a, 520, 16, odstep=1)))

        def wykres(s, x, y):
            G.tekst(s, "Od kiedy kobiety głosują?", (x, y), 18, 25, "plakat")
            for i, (kraj, rok) in enumerate(pk["porownanie"]):
                yy = y + 30 + i * 34
                dl = int((rok - 1880) * 3.6)
                kolor = sep(70) if kraj != "Polska" else FIOLET
                pygame.draw.rect(s, kolor, (x + 230, yy, dl, 22))
                G.tekst(s, kraj, (x, yy), 15, 30)
                G.tekst(s, str(rok), (x + 236 + dl, yy + 1), 15, 30, "plakat")
            ui.akapit(s, "Źródło: " + pk["zrodlo"], (x, y + 280, 520, 60), 13, 90)
        el.append((wykres, 330))
        return el


# ====================================================================== ZAKOŃCZENIE
class Zakonczenie(Scena):
    def __init__(self, app):
        super().__init__(app)
        self.przyciski = [ui.Przycisk((380, 640, 240, 50), "Dziennik", app.otworz_dziennik),
                          ui.Przycisk((660, 640, 240, 50), "Menu główne", app.do_menu)]

    def zdarzenie(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for p in self.przyciski:
                p.klik(e.pos)

    def rysuj(self, s):
        s.blit(G.papier(W, H, 180, seed=99), (0, 0))
        ui.karta(s, (60, 30, 1160, 590), 232, stempel="28 XI 1918")
        G.tekst(s, "Album skończony", (640, 80), 44, 25, "plakat", srodek=True)
        for i, pid in enumerate(P.HISTORYCZNE):
            x = 110 + (i % 6) * 180
            y = 120 + (i // 6) * 170
            s.blit(G.portret(pid, 100), (x + 20, y))
            ui.akapit(s, P.HISTORYCZNE[pid]["imie"], (x - 10, y + 122, 160, 40), 13, 30, "plakat", odstep=0, wysrodkuj=True)
        st = self.app.gra.stan
        tekst = ("Janek przeszedł przez cały listopad 1918 roku. Widział, że niepodległość nie spadła z nieba "
                 "jednego dnia: Witos przejął Galicję, Rada Regencyjna przygotowała urzędy, Daszyński spisał reformy, "
                 "Piłsudski zbudował wojsko i władzę, Dmowski i Paderewski zdobywali sojuszników, Korfanty upominał się "
                 "o zabór pruski, a kobiety wywalczyły prawo głosu. Każdy wniósł co innego — i często się kłócili. "
                 "Tak też buduje się państwo.")
        ui.akapit(s, tekst, (140, 470, 1000, 120), 18, 30, wysrodkuj=True)
        G.tekst(s, "Fakty: %d/%d   •   Mity obalone za pierwszym razem: %d/%d   •   Postacie: %d/12" % (
            len(st.fakty), len(F.FAKTY), sum(1 for v in st.mity.values() if v), len(F.MITY), len(st.poznani)),
            (640, 600), 17, 60, srodek=True)
        mysz = self.app.mysz()
        for p in self.przyciski:
            p.rysuj(s, mysz)
        ui.etykieta_fiolet(s, "Damian: „Sprawdzaj źródła. Zawsze.”", (935, 652), 14)
