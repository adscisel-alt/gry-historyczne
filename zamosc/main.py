"""Jan Zamoyski i Miasto Idealne — edukacyjna gra strategiczna (Python + Pygame).

Uruchom:  python main.py
Opcje:    --zrzuty KATALOG   zapisuje automatyczne zrzuty ekranu i kończy działanie
"""
import json
import math
import os
import random
import sys

if "--zrzuty" in sys.argv:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

import dane as D

SZER, WYS = 640, 360
KAF = 16
VIEW = pygame.Rect(0, 18, 448, 320)
PANEL = pygame.Rect(448, 18, 192, 320)
DZIEN_SEK = 4.0
TYTUL = "Jan Zamoyski i Miasto Idealne"

# kolory interfejsu
C_TEKST = (48, 30, 22)
C_JASNY = (250, 240, 210)
C_ZLOTY = (244, 200, 72)
C_CZERW = (170, 40, 44)
C_ZIELONY = (40, 120, 50)
C_SZARY = (120, 110, 100)


def sciezka(*czesci):
    baza = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(baza, *czesci)


def plik_zapisu():
    baza = os.environ.get("APPDATA") or os.path.expanduser("~")
    katalog = os.path.join(baza, "ZamoscGra")
    try:
        os.makedirs(katalog, exist_ok=True)
    except OSError:
        katalog = baza
    return os.path.join(katalog, "zapis.json")


# ====================================================================== stan gry
class Stan:
    def __init__(self):
        self.rozdzial = 1
        self.zasoby = {"zloto": 150, "drewno": 50, "kamien": 20, "cegla": 0}
        self.ludnosc = 8.0
        self.pw = 0
        self.budynki = []  # dict(typ, x, y, postep, wariant)
        self.flagi = []
        self.ekwipunek = ["kompas", "sakiewka", "prowiant"]
        self.karty = list(D.KARTY_STARTOWE)
        self.przeczytane = []
        self.zagadki = []  # rozwiązane zagadki "npc:indeks"
        self.dzien = 0
        self.prowiant = 0
        self.bohater = [D.START[0] * KAF + 8, D.START[1] * KAF + 12]

    def do_json(self):
        return dict(self.__dict__)

    @classmethod
    def z_json(cls, d):
        s = cls()
        for k, v in d.items():
            setattr(s, k, v)
        return s


# ====================================================================== pomocnicze
def zawijaj(tekst, czcionka, szer):
    linie = []
    for akapit in tekst.split("\n"):
        if not akapit:
            linie.append("")
            continue
        slowa, biez = akapit.split(" "), ""
        for s in slowa:
            proba = (biez + " " + s).strip()
            if czcionka.size(proba)[0] <= szer:
                biez = proba
            else:
                if biez:
                    linie.append(biez)
                biez = s
        linie.append(biez)
    return linie


def kierunek_slownie(dx, dy):
    if abs(dx) < 1 and abs(dy) < 1:
        return "tutaj"
    kat = math.degrees(math.atan2(-dy, dx)) % 360
    nazwy = ["na wschód", "na północny wschód", "na północ", "na północny zachód",
             "na zachód", "na południowy zachód", "na południe", "na południowy wschód"]
    return nazwy[int((kat + 22.5) // 45) % 8]


class Dialog:
    """Rozmowa: lista kwestii (mówca, tekst), opcjonalna zagadka i akcja na końcu."""

    def __init__(self, kwestie, zagadka=None, na_koniec=None, na_dobrze=None):
        self.kwestie = list(kwestie)
        self.i = 0
        self.znaki = 0.0
        self.zagadka = zagadka
        self.na_koniec = na_koniec
        self.na_dobrze = na_dobrze
        self.tryb = "tekst"
        self.odp = None
        self.zle = set()
        self.proby = 0
        if zagadka:
            o = [zagadka["poprawna"]] + list(zagadka["zle"])
            random.shuffle(o)
            self.odp = o

    def biezaca(self):
        return self.kwestie[self.i] if self.i < len(self.kwestie) else ("narrator", "")


# ====================================================================== gra
class Gra:
    def __init__(self, zrzuty=None):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        self.zrzuty = zrzuty
        flagi = 0 if zrzuty else pygame.SCALED | pygame.RESIZABLE
        pygame.display.set_caption(TYTUL)
        try:
            pygame.display.set_icon(pygame.image.load(sciezka("assets", "ikona.png")))
        except pygame.error:
            pass
        self.okno = pygame.display.set_mode((SZER, WYS), flagi)
        self.ekran = self.okno if not zrzuty else pygame.Surface((SZER, WYS))
        self.zegar = pygame.time.Clock()
        self.f = pygame.font.Font(None, 14)
        self.fm = pygame.font.Font(None, 12)
        self.fd = pygame.font.Font(None, 18)
        self.fduza = pygame.font.Font(None, 36)
        self.fogromna = pygame.font.Font(None, 44)
        self.wczytaj_zasoby()
        self.mapa0 = D.zbuduj_mape()
        self.muzyka_on = True
        self.scena = "tytul"
        self.stan = Stan()
        self.nakladka = None
        self.dialog = None
        self.wybrany = None
        self.rozbiorka = False
        self.kompas = False
        self.przyciski = []
        self.t = 0.0
        self.toasty = []
        self.napisy = []
        self.czastki = []
        self.wybrana_karta = None
        self.wybrany_przedm = None
        self.info_budynek = None
        self.intro_znaki = 0.0
        self.anim = 0.0
        self.kier = "dol"
        self.idzie = False
        self.zegar_dnia = 0.0
        self.najechany = None
        self.przesun_ksiegi = 0
        self.mysz = (0, 0)
        self.odbuduj_swiat()
        if not zrzuty:
            self.graj_muzyke()

    # ------------------------------------------------------------ zasoby
    def wczytaj_zasoby(self):
        self.g = {}
        katalog = sciezka("assets", "gfx")
        for plik in os.listdir(katalog):
            if plik.endswith(".png"):
                obraz = pygame.image.load(os.path.join(katalog, plik))
                self.g[plik[:-4]] = obraz.convert_alpha() if not self.zrzuty else obraz
        self.d = {}
        try:
            for plik in os.listdir(sciezka("assets", "sfx")):
                if plik.endswith(".wav") and plik != "muzyka.wav":
                    self.d[plik[:-4]] = pygame.mixer.Sound(sciezka("assets", "sfx", plik))
        except pygame.error:
            self.d = {}
        for k, v in self.d.items():
            v.set_volume(.35 if k == "moneta" else .6)

    def dzwiek(self, nazwa):
        if nazwa in self.d:
            self.d[nazwa].play()

    def graj_muzyke(self):
        try:
            pygame.mixer.music.load(sciezka("assets", "sfx", "muzyka.wav"))
            pygame.mixer.music.set_volume(.35)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    # ------------------------------------------------------------ świat
    def odbuduj_swiat(self):
        self.mapa = [wiersz[:] for wiersz in self.mapa0]
        if self.gotowy("rynek"):
            x0, y0, w, h = D.RYNEK
            for y in range(y0, y0 + h):
                for x in range(x0, x0 + w):
                    self.mapa[y][x] = "B"
        self.zajete = {}
        for i, b in enumerate(self.stan.budynki):
            if b["typ"] == "rynek":
                continue
            d = D.BUDYNKI[b["typ"]]
            for y in range(b["y"], b["y"] + d["h"]):
                for x in range(b["x"], b["x"] + d["w"]):
                    self.zajete[(x, y)] = i
        self.teren = [self.renderuj_teren(k) for k in (0, 1)]

    def renderuj_teren(self, klatka):
        s = pygame.Surface((D.MAPA_W * KAF, D.MAPA_H * KAF))
        r = random.Random(7)
        drzewa = []
        for y in range(D.MAPA_H):
            for x in range(D.MAPA_W):
                c = self.mapa[y][x]
                px, py = x * KAF, y * KAF
                s.blit(self.g["trawa_%d" % r.choice([0, 0, 0, 1, 1, 2, 3])], (px, py))
                if c == "~":
                    s.blit(self.g["woda_%d" % klatka], (px, py))
                elif c == "#":
                    s.blit(self.g["most"], (px, py))
                elif c == '"':
                    s.blit(self.g["bagno"], (px, py))
                elif c == "=":
                    s.blit(self.g["droga"], (px, py))
                elif c == "B":
                    s.blit(self.g["bruk"], (px, py))
                elif c == "R":
                    s.blit(self.g["skala"], (px, py))
                elif c == "T":
                    drzewa.append((px, py, r.randrange(3)))
                if c == "~":  # jasny brzeg
                    for dx, dy, rr in ((-1, 0, (0, 0, 1, 16)), (1, 0, (15, 0, 1, 16))):
                        nx = x + dx
                        if 0 <= nx < D.MAPA_W and self.mapa[y][nx] not in "~#":
                            pygame.draw.rect(s, (150, 196, 240), (px + rr[0], py + rr[1], rr[2], rr[3]))
        for px, py, v in drzewa:
            s.blit(self.g["drzewo_%d" % v], (px - 1, py - 9))
        return s

    def gotowy(self, typ):
        return any(b["typ"] == typ and b["postep"] >= D.BUDYNKI[typ]["czas"] for b in self.stan.budynki)

    def ile_gotowych(self, typ, warunek=None):
        n = 0
        for b in self.stan.budynki:
            if b["typ"] == typ and b["postep"] >= D.BUDYNKI[typ]["czas"]:
                if warunek is None or warunek(b):
                    n += 1
        return n

    def przy_rynku(self, b):
        x0, y0, w, h = D.RYNEK
        d = D.BUDYNKI[b["typ"]]
        bx0, by0, bx1, by1 = b["x"], b["y"], b["x"] + d["w"], b["y"] + d["h"]
        rozszerz = pygame.Rect(x0 - 1, y0 - 1, w + 2, h + 2)
        return rozszerz.colliderect(pygame.Rect(bx0, by0, bx1 - bx0, by1 - by0))

    def teren_w(self, x, y):
        if 0 <= x < D.MAPA_W and 0 <= y < D.MAPA_H:
            return self.mapa[y][x]
        return None

    def dzialki_typu(self, typ):
        return [(x, y) for t, x, y in D.DZIALKI if t == typ]

    def dzialka_zajeta(self, typ, x, y):
        return any(b["typ"] == typ and b["x"] == x and b["y"] == y for b in self.stan.budynki)

    def zarezerwowane(self):
        rez = set()
        for typ, x, y in D.DZIALKI:
            if typ in ("ratusz",):
                continue
            if self.dzialka_zajeta(typ, x, y):
                continue
            d = D.BUDYNKI[typ]
            for yy in range(y, y + d["h"]):
                for xx in range(x, x + d["w"]):
                    rez.add((xx, yy))
        return rez

    def koszt(self, typ):
        k = dict(D.BUDYNKI[typ]["koszt"])
        if "cyrkiel" in self.stan.ekwipunek:
            k = {a: int(math.ceil(v * .85)) for a, v in k.items()}
        return k

    def stac(self, typ):
        return all(self.stan.zasoby.get(a, 0) >= v for a, v in self.koszt(typ).items())

    def moze_budowac(self, typ, tx, ty):
        d = D.BUDYNKI[typ]
        if d.get("min_pw", 0) > self.stan.pw:
            return False, "Potrzeba %d Punktów Wiedzy!" % d["min_pw"]
        if d.get("zabytek"):
            if typ == "ratusz" and not self.gotowy("rynek"):
                return False, "Najpierw wybrukuj Rynek Wielki."
            if (tx, ty) not in self.dzialki_typu(typ):
                return False, "Plan Morando wskazuje inne miejsce — użyj kompasu (K)!"
            if self.dzialka_zajeta(typ, tx, ty):
                return False, "Ta działka jest już zabudowana."
            if typ in ("palac", "rynek", "ratusz", "kolegiata", "akademia") and \
                    any(b["typ"] == typ for b in self.stan.budynki):
                return False, "Ta budowla już powstaje."
            for y in range(ty, ty + d["h"]):
                for x in range(tx, tx + d["w"]):
                    if (x, y) in self.zajete:
                        return False, "Coś stoi na działce — rozbierz to."
            if not self.stac(typ):
                return False, "Brakuje surowców."
            return True, ""
        rez = self.zarezerwowane()
        sasiedzi = set()
        for y in range(ty, ty + d["h"]):
            for x in range(tx, tx + d["w"]):
                c = self.teren_w(x, y)
                if c is None:
                    return False, "Poza mapą."
                if (x, y) in self.zajete:
                    return False, "Tu już coś stoi."
                if (x, y) in rez:
                    return False, "To działka z planu Morando — zostaw ją."
                if typ == "kram":
                    if c != "B":
                        return False, "Kram stawiaj na bruku Rynku Wielkiego."
                elif c != ".":
                    return False, "Tu nie można budować (droga, woda, las lub skały)."
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        sasiedzi.add(self.teren_w(x + dx, y + dy))
        w = d.get("wymog")
        if w == "las" and "T" not in sasiedzi:
            return False, "Tartak musi stać tuż przy lesie."
        if w == "skala" and "R" not in sasiedzi:
            return False, "Kamieniołom musi stać tuż przy skałach."
        if w == "woda" and "~" not in sasiedzi and '"' not in sasiedzi:
            return False, "Cegielnia musi stać przy wodzie lub bagnie."
        if not self.stac(typ):
            return False, "Brakuje surowców."
        return True, ""

    def postaw(self, typ, tx, ty):
        for a, v in self.koszt(typ).items():
            self.stan.zasoby[a] -= v
        self.stan.budynki.append(dict(typ=typ, x=tx, y=ty, postep=0, wariant=random.randrange(5)))
        self.odbuduj_swiat()
        self.dzwiek("buduj")
        d = D.BUDYNKI[typ]
        for _ in range(12):
            self.czastka(tx * KAF + d["w"] * 8, ty * KAF + d["h"] * 8, (196, 170, 130))

    # ------------------------------------------------------------ ekonomia
    def pojemnosc(self):
        p = 10
        for b in self.stan.budynki:
            if b["postep"] >= D.BUDYNKI[b["typ"]]["czas"]:
                p += D.BUDYNKI[b["typ"]].get("mieszk", 0)
        return p

    def potrzebni(self):
        return sum(D.BUDYNKI[b["typ"]].get("rob", 0) for b in self.stan.budynki
                   if b["postep"] >= D.BUDYNKI[b["typ"]]["czas"])

    def wydajnosc(self):
        p = self.potrzebni()
        return 1.0 if p == 0 else min(1.0, self.stan.ludnosc / p)

    def nowy_dzien(self):
        s = self.stan
        s.dzien += 1
        wyd = self.wydajnosc() * (2 if s.prowiant > 0 else 1)
        if s.prowiant > 0:
            s.prowiant -= 1
        handel = 0
        for b in s.budynki:
            d = D.BUDYNKI[b["typ"]]
            if b["postep"] < d["czas"]:
                b["postep"] += 1
                if b["postep"] >= d["czas"]:
                    self.ukonczono(b)
                continue
            for zas, ile in d.get("prod", {}).items():
                ile_r = ile if zas == "pw" else int(round(ile * wyd))
                if zas == "pw":
                    s.pw += ile_r
                else:
                    s.zasoby[zas] += ile_r
                if ile_r:
                    self.napis(b["x"] * KAF + d["w"] * 8, b["y"] * KAF, "+%d %s" % (ile_r, D.ZASOBY_NAZWY[zas]),
                               (255, 250, 220))
            handel += d.get("handel", 0)
        if "waga" in s.ekwipunek:
            handel = int(handel * 1.5)
        podatek = s.ludnosc * .5
        if "przywilej" in s.ekwipunek:
            podatek *= 1.25
        dochod = int(podatek) + handel
        s.zasoby["zloto"] += dochod
        if "ksiega" in s.ekwipunek:
            s.pw += 1
        cap = self.pojemnosc()
        if s.ludnosc < cap:
            s.ludnosc = min(cap, s.ludnosc + 2)
        elif s.ludnosc > cap:
            s.ludnosc = cap
        if dochod:
            self.dzwiek("moneta")
        self.ostatni_dochod = dochod

    def ukonczono(self, b):
        d = D.BUDYNKI[b["typ"]]
        self.odbuduj_swiat()
        self.dzwiek("gotowe")
        for _ in range(20):
            self.czastka(b["x"] * KAF + d["w"] * 8, b["y"] * KAF + d["h"] * 8, (250, 230, 160))
        self.toast("Ukończono: " + d["nazwa"] + "!")
        if d.get("zabytek"):
            self.stan.pw += 5
            self.napis(b["x"] * KAF + d["w"] * 8, b["y"] * KAF - 8, "+5 PW", C_ZLOTY)
        karta = D.KARTA_BUDYNKU.get(b["typ"])
        if karta:
            self.odkryj(karta)

    def odkryj(self, karta):
        if karta not in self.stan.karty:
            self.stan.karty.append(karta)
            self.toast("Nowa karta w Księdze Wiedzy: " + D.WIEDZA[karta][0] + " (L)")
            self.dzwiek("strona")

    def daj_przedmiot(self, p):
        self.stan.ekwipunek.append(p)
        self.toast("Nowy przedmiot: " + D.PRZEDMIOTY[p]["nazwa"] + " (I)")
        self.dzwiek("przedmiot")

    # ------------------------------------------------------------ cele
    def stan_celu(self, cel):
        _, typ, par, ile = cel
        if typ == "rozmowa":
            return (1 if "rozm_%s_%d" % (par, ile) in self.stan.flagi else 0), 1
        if typ == "buduj":
            return min(ile, self.ile_gotowych(par)), ile
        if typ == "przy_rynku":
            return min(ile, self.ile_gotowych(par, self.przy_rynku)), ile
        if typ == "wiedza":
            return min(ile, self.stan.pw), ile
        return 0, 1

    def cele(self):
        return D.ROZDZIALY[self.stan.rozdzial]["cele"]

    def rozdzial_ukonczony(self):
        return all(a >= b for a, b in (self.stan_celu(c) for c in self.cele()))

    def cel_kompasu(self):
        """Zwraca (punkt w pikselach mapy lub None, opis) dla pierwszego niewykonanego celu."""
        for c in self.cele():
            a, b = self.stan_celu(c)
            if a >= b:
                continue
            _, typ, par, ile = c
            if typ == "rozmowa":
                x, y = D.NPC[par]["poz"]
                return (x * KAF + 8, y * KAF + 8), D.NPC[par]["imie"]
            if typ == "przy_rynku" or par == "kram":
                x0, y0, w, h = D.RYNEK
                return ((x0 + w / 2) * KAF, (y0 + h / 2) * KAF), "Rynek Wielki"
            if typ == "buduj" and D.BUDYNKI[par].get("zabytek"):
                hx, hy = self.stan.bohater
                wolne = [(x, y) for x, y in self.dzialki_typu(par) if not self.dzialka_zajeta(par, x, y)]
                if not wolne:
                    continue
                d = D.BUDYNKI[par]
                x, y = min(wolne, key=lambda p: (p[0] * KAF - hx) ** 2 + (p[1] * KAF - hy) ** 2)
                return ((x + d["w"] / 2) * KAF, (y + d["h"] / 2) * KAF), D.BUDYNKI[par]["nazwa"]
            if typ == "buduj" and par in ("tartak", "kamieniolom", "cegielnia"):
                znak = {"tartak": "T", "kamieniolom": "R", "cegielnia": "~"}[par]
                hx, hy = self.stan.bohater
                najl = None
                for y in range(D.MAPA_H):
                    for x in range(D.MAPA_W):
                        if self.mapa[y][x] == znak:
                            dd = (x * KAF - hx) ** 2 + (y * KAF - hy) ** 2
                            if najl is None or dd < najl[0]:
                                najl = (dd, x, y)
                if najl:
                    nazwa = {"T": "las", "R": "skały", "~": "rzeka"}[znak]
                    return (najl[1] * KAF + 8, najl[2] * KAF + 8), nazwa
            if typ == "wiedza":
                return None, "Czytaj Księgę (L) i rozwiązuj zagadki"
            if par == "dom":
                return None, "Domy stawiaj na wolnej trawie"
        return None, "Wszystkie cele wykonane!"

    # ------------------------------------------------------------ rozmowy
    def rozmawiaj(self, npc):
        rozd = self.stan.rozdzial
        flaga = "rozm_%s_%d" % (npc, rozd)
        klucz = (npc, rozd)
        self.dzwiek("rozmowa")
        if klucz in D.ROZMOWY and flaga not in self.stan.flagi:
            r = D.ROZMOWY[klucz]
            q = D.QUIZ_GLOWNY.get(klucz)

            def koniec():
                self.stan.flagi.append(flaga)
                self.daj_przedmiot(r["nagroda"])
                for k in r["karty"]:
                    self.odkryj(k)

            self.otworz_dialog(Dialog(r["kwestie"], q, koniec, lambda pierwsza: self.pw_za_zagadke(pierwsza, 5)))
            return
        # zagadka dodatkowa
        pula = D.ZAGADKI.get(npc, [])
        wolne = [i for i in range(len(pula)) if "%s:%d" % (npc, i) not in self.stan.zagadki]
        if wolne:
            i = wolne[0]
            kw = [(npc, "Mam dla ciebie zagadkę! Za dobrą odpowiedź dostaniesz Punkty Wiedzy.")]

            def dobrze(pierwsza, i=i):
                self.stan.zagadki.append("%s:%d" % (npc, i))
                self.pw_za_zagadke(pierwsza, 3)

            self.otworz_dialog(Dialog(kw, pula[i], None, dobrze))
            return
        kw = list(D.LUZNE[npc])
        if klucz in D.ROZMOWY:
            kw += D.ROZMOWY[klucz]["po"]
        self.otworz_dialog(Dialog(kw))

    def pw_za_zagadke(self, pierwsza, ile):
        zysk = ile if pierwsza else max(1, ile // 2)
        self.stan.pw += zysk
        hx, hy = self.stan.bohater
        self.napis(hx, hy - 20, "+%d PW" % zysk, C_ZLOTY)

    def otworz_dialog(self, dlg):
        self.dialog = dlg
        self.nakladka = "dialog"

    def dalej_dialog(self):
        dl = self.dialog
        if dl.tryb == "tekst":
            _, tekst = dl.biezaca()
            if dl.znaki < len(tekst):
                dl.znaki = len(tekst)
                return
            dl.i += 1
            dl.znaki = 0
            if dl.i >= len(dl.kwestie):
                if dl.zagadka:
                    dl.tryb = "zagadka"
                else:
                    self.zamknij_dialog()
        elif dl.tryb == "wynik":
            self.zamknij_dialog()

    def odpowiedz(self, idx):
        dl = self.dialog
        if idx in dl.zle:
            return
        if dl.odp[idx] == dl.zagadka["poprawna"]:
            self.dzwiek("dobrze")
            dl.tryb = "wynik"
            if dl.na_dobrze:
                dl.na_dobrze(dl.proby == 0)
        else:
            self.dzwiek("zle")
            dl.zle.add(idx)
            dl.proby += 1

    def zamknij_dialog(self):
        dl = self.dialog
        self.dialog = None
        self.nakladka = None
        if dl and dl.na_koniec:
            dl.na_koniec()

    # ------------------------------------------------------------ efekty
    def toast(self, tekst):
        self.toasty.append([tekst, 3.5])

    def napis(self, x, y, tekst, kolor):
        self.napisy.append([x, y, tekst, kolor, 1.6])

    def czastka(self, x, y, kolor):
        self.czastki.append([x, y, random.uniform(-30, 30), random.uniform(-50, -10), random.uniform(.4, .9), kolor])

    # ------------------------------------------------------------ sceny
    def nowa_gra(self):
        self.stan = Stan()
        self.odbuduj_swiat()
        self.zacznij_rozdzial()

    def zacznij_rozdzial(self):
        self.scena = "intro"
        self.intro_znaki = 0
        self.wybrany = None
        self.rozbiorka = False
        self.zapisz()

    def wejdz_do_gry(self):
        self.scena = "gra"
        self.zegar_dnia = 0
        if self.stan.rozdzial == 1 and "powitanie" not in self.stan.flagi:
            self.stan.flagi.append("powitanie")
            self.otworz_dialog(Dialog([
                ("zamoyski", "Oto miejsce na nasze miasto! Muszę odnaleźć architekta Morando."),
                ("narrator", "Chodź strzałkami lub WASD. Podejdź do Morando (wykrzyknik nad głową) i wciśnij E."),
                ("narrator", "Kompas (K) wskaże ci kierunek do celu. Cele rozdziału widzisz po prawej stronie."),
            ]))

    def zakoncz_rozdzial(self):
        r = D.ROZDZIALY[self.stan.rozdzial]
        self.dzwiek("fanfara")

        def dalej():
            self.daj_przedmiot(r["nagroda"])
            for k in r["karty"]:
                self.odkryj(k)
            if self.stan.rozdzial >= 4:
                self.odkryj("unesco")
                self.scena = "koniec"
                self.zapisz()
            else:
                self.stan.rozdzial += 1
                self.zacznij_rozdzial()

        self.otworz_dialog(Dialog(r["koniec"], na_koniec=dalej))

    def zapisz(self):
        if self.zrzuty:
            return
        try:
            with open(plik_zapisu(), "w", encoding="utf-8") as f:
                json.dump(self.stan.do_json(), f, ensure_ascii=False)
        except OSError:
            pass

    def wczytaj(self):
        try:
            with open(plik_zapisu(), encoding="utf-8") as f:
                self.stan = Stan.z_json(json.load(f))
            self.odbuduj_swiat()
            self.zacznij_rozdzial() if self.stan.rozdzial <= 4 else None
            return True
        except (OSError, ValueError):
            return False

    # ------------------------------------------------------------ sterowanie
    def uzyj_przedmiotu(self, p):
        u = D.PRZEDMIOTY[p]["uzycie"]
        if u == "kompas":
            self.kompas = not self.kompas
            self.nakladka = None
            self.dzwiek("klik")
        elif u == "plan":
            self.nakladka = "plan"
            self.dzwiek("strona")
        elif u == "zuzyj":
            self.stan.ekwipunek.remove(p)
            if p == "sakiewka":
                self.stan.zasoby["zloto"] += 60
                self.toast("+60 zł do skarbca!")
                self.dzwiek("moneta")
            elif p == "prowiant":
                self.stan.prowiant += 6
                self.toast("Robotnicy pracują podwójnie przez 6 dni!")
                self.dzwiek("przedmiot")
            self.wybrany_przedm = None

    def npc_obok(self):
        hx, hy = self.stan.bohater
        for k, n in D.NPC.items():
            x, y = n["poz"][0] * KAF + 8, n["poz"][1] * KAF + 12
            if (x - hx) ** 2 + (y - hy) ** 2 < 26 ** 2:
                return k
        return None

    def kamera(self):
        hx, hy = self.stan.bohater
        cx = max(0, min(D.MAPA_W * KAF - VIEW.w, int(hx - VIEW.w / 2)))
        cy = max(0, min(D.MAPA_H * KAF - VIEW.h, int(hy - VIEW.h / 2)))
        return cx, cy

    def kafel_pod_mysza(self):
        mx, my = self.mysz
        if not VIEW.collidepoint(mx, my):
            return None
        cx, cy = self.kamera()
        return (mx - VIEW.x + cx) // KAF, (my - VIEW.y + cy) // KAF

    def pozycja_ducha(self):
        k = self.kafel_pod_mysza()
        if k is None or not self.wybrany:
            return None
        d = D.BUDYNKI[self.wybrany]
        tx, ty = k[0] - (d["w"] - 1) // 2, k[1] - (d["h"] - 1) // 2
        if d.get("zabytek"):  # przyciąganie do działki z planu
            for x, y in self.dzialki_typu(self.wybrany):
                if x - 1 <= k[0] <= x + d["w"] and y - 1 <= k[1] <= y + d["h"]:
                    return x, y
        return tx, ty

    def klawisz(self, e):
        k = e.key
        if k == pygame.K_F11:
            pygame.display.toggle_fullscreen()
            return
        if k == pygame.K_m:
            self.muzyka_on = not self.muzyka_on
            if self.muzyka_on:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()
            return
        if self.scena == "tytul":
            if k in (pygame.K_RETURN, pygame.K_SPACE):
                self.nowa_gra()
            return
        if self.scena == "intro":
            if k in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self.klik_intro()
            return
        if self.scena == "koniec":
            return
        if self.nakladka == "dialog":
            if k in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                self.dalej_dialog()
            elif self.dialog.tryb == "zagadka" and k in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.odpowiedz(k - pygame.K_1)
            return
        if k == pygame.K_ESCAPE:
            if self.nakladka:
                self.nakladka = None
            elif self.wybrany or self.rozbiorka:
                self.wybrany, self.rozbiorka = None, False
            else:
                self.nakladka = "menu"
            return
        if self.nakladka in ("menu", "pomoc") and k not in (pygame.K_i, pygame.K_l, pygame.K_h):
            return
        if k == pygame.K_i:
            self.przelacz("ekwipunek")
        elif k == pygame.K_l:
            self.przelacz("ksiega")
        elif k == pygame.K_h:
            self.przelacz("pomoc")
        elif k == pygame.K_k and not self.nakladka:
            self.uzyj_przedmiotu("kompas")
        elif k in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN) and not self.nakladka:
            n = self.npc_obok()
            if n:
                self.rozmawiaj(n)

    def przelacz(self, co):
        self.nakladka = None if self.nakladka == co else co
        self.dzwiek("strona" if co == "ksiega" else "klik")

    def klik_intro(self):
        tekst = D.ROZDZIALY[self.stan.rozdzial]["wstep"]
        if self.intro_znaki < len(tekst):
            self.intro_znaki = len(tekst)
        else:
            self.dzwiek("klik")
            self.wejdz_do_gry()

    def klik(self, e):
        pos = e.pos
        if e.button == 3:
            self.wybrany, self.rozbiorka = None, False
            return
        if e.button == 4 and self.nakladka == "ksiega":
            self.przesun_ksiegi = max(0, self.przesun_ksiegi - 1)
            return
        if e.button == 5 and self.nakladka == "ksiega":
            self.przesun_ksiegi += 1
            return
        if e.button != 1:
            return
        for rect, akcja in reversed(self.przyciski):
            if rect.collidepoint(pos):
                akcja()
                return
        if self.scena == "intro":
            self.klik_intro()
            return
        if self.scena != "gra":
            return
        if self.nakladka == "dialog":
            if self.dialog.tryb != "zagadka":
                self.dalej_dialog()
            return
        if self.nakladka:
            return
        if not VIEW.collidepoint(pos):
            return
        if self.wybrany:
            p = self.pozycja_ducha()
            if p:
                ok, msg = self.moze_budowac(self.wybrany, *p)
                if ok:
                    self.postaw(self.wybrany, *p)
                    if D.BUDYNKI[self.wybrany].get("zabytek") or not self.stac(self.wybrany):
                        self.wybrany = None
                else:
                    self.toast(msg)
                    self.dzwiek("blad")
            return
        k = self.kafel_pod_mysza()
        if self.rozbiorka and k:
            i = self.zajete.get(tuple(k))
            if i is not None:
                b = self.stan.budynki[i]
                if D.BUDYNKI[b["typ"]].get("zabytek"):
                    self.toast("Zabytków z planu Morando nie wolno burzyć!")
                    self.dzwiek("blad")
                    return
                for a, v in D.BUDYNKI[b["typ"]]["koszt"].items():
                    self.stan.zasoby[a] += v // 2
                self.stan.budynki.pop(i)
                self.odbuduj_swiat()
                self.dzwiek("buduj")
                self.toast("Rozebrano — odzyskano połowę surowców.")
            return
        # klik na postać obok
        n = self.npc_obok()
        if n and k and tuple(k) in [D.NPC[n]["poz"], (D.NPC[n]["poz"][0], D.NPC[n]["poz"][1] - 1)]:
            self.rozmawiaj(n)
            return
        if k:
            i = self.zajete.get(tuple(k))
            self.info_budynek = self.stan.budynki[i] if i is not None else None

    # ------------------------------------------------------------ aktualizacja
    def aktualizuj(self, dt):
        self.t += dt
        for t in self.toasty:
            t[1] -= dt
        self.toasty = [t for t in self.toasty if t[1] > 0][-4:]
        for n in self.napisy:
            n[1] -= 14 * dt
            n[4] -= dt
        self.napisy = [n for n in self.napisy if n[4] > 0]
        for c in self.czastki:
            c[0] += c[2] * dt
            c[1] += c[3] * dt
            c[3] += 80 * dt
            c[4] -= dt
        self.czastki = [c for c in self.czastki if c[4] > 0]
        if self.scena == "intro":
            self.intro_znaki += 60 * dt
        if self.scena != "gra":
            return
        if self.nakladka == "dialog":
            self.dialog.znaki += 55 * dt
            return
        if self.nakladka:
            return
        # ruch bohatera
        klaw = pygame.key.get_pressed()
        dx = (klaw[pygame.K_RIGHT] or klaw[pygame.K_d]) - (klaw[pygame.K_LEFT] or klaw[pygame.K_a])
        dy = (klaw[pygame.K_DOWN] or klaw[pygame.K_s]) - (klaw[pygame.K_UP] or klaw[pygame.K_w])
        self.idzie = bool(dx or dy)
        if self.idzie:
            if dx > 0:
                self.kier = "prawo"
            elif dx < 0:
                self.kier = "lewo"
            elif dy > 0:
                self.kier = "dol"
            else:
                self.kier = "gora"
            v = 72 * dt / (1.41 if dx and dy else 1)
            hx, hy = self.stan.bohater
            nx = hx + dx * v
            if self.przechodnie(nx, hy):
                hx = nx
            ny = hy + dy * v
            if self.przechodnie(hx, ny):
                hy = ny
            self.stan.bohater = [hx, hy]
            self.anim += dt
        # dzień targowy
        self.zegar_dnia += dt
        if self.zegar_dnia >= DZIEN_SEK:
            self.zegar_dnia -= DZIEN_SEK
            self.nowy_dzien()
        if self.rozdzial_ukonczony():
            self.zakoncz_rozdzial()

    def przechodnie(self, x, y):
        if not (4 <= x < D.MAPA_W * KAF - 4 and 8 <= y < D.MAPA_H * KAF - 2):
            return False
        return self.teren_w(int(x // KAF), int(y // KAF)) != "~"

    # ====================================================================== RYSOWANIE
    def ramka(self, rect, styl="ui_panel"):
        src = self.g[styl]
        r = pygame.Rect(rect)
        b = 8
        s = src.get_width()
        # środek
        srodek = src.subsurface((b, b, s - 2 * b, s - 2 * b))
        self.ekran.blit(pygame.transform.scale(srodek, (max(1, r.w - 2 * b), max(1, r.h - 2 * b))), (r.x + b, r.y + b))
        for (sx, sy, dx, dy, w, h) in [
            (b, 0, r.x + b, r.y, r.w - 2 * b, b), (b, s - b, r.x + b, r.bottom - b, r.w - 2 * b, b),
            (0, b, r.x, r.y + b, b, r.h - 2 * b), (s - b, b, r.right - b, r.y + b, b, r.h - 2 * b)]:
            if w > 0 and h > 0:
                kawal = src.subsurface((sx, sy, b if sx in (0, s - b) else s - 2 * b, b if sy in (0, s - b) else s - 2 * b))
                self.ekran.blit(pygame.transform.scale(kawal, (w, h)), (dx, dy))
        for (sx, sy, dx, dy) in [(0, 0, r.x, r.y), (s - b, 0, r.right - b, r.y),
                                 (0, s - b, r.x, r.bottom - b), (s - b, s - b, r.right - b, r.bottom - b)]:
            self.ekran.blit(src.subsurface((sx, sy, b, b)), (dx, dy))

    def tekst(self, t, x, y, kolor=C_TEKST, f=None, cien=None, srodek=False):
        f = f or self.f
        obraz = f.render(t, False, kolor)
        if srodek:
            x -= obraz.get_width() // 2
        if cien:
            self.ekran.blit(f.render(t, False, cien), (x + 1, y + 1))
        self.ekran.blit(obraz, (x, y))
        return obraz.get_width()

    def przycisk(self, rect, napis, akcja, ikona=None, aktywny=True, wybrany=False, f=None):
        r = pygame.Rect(rect)
        hover = r.collidepoint(self.mysz)
        stan = "wyb" if wybrany else ("hover" if hover and aktywny else "norm")
        src = self.g["ui_przycisk_" + stan]
        s = pygame.transform.scale(src.subsurface((3, 3, 6, 6)), (r.w - 6, r.h - 6))
        pygame.draw.rect(self.ekran, (24, 16, 28), r)
        self.ekran.blit(s, (r.x + 3, r.y + 3))
        pygame.draw.rect(self.ekran, (24, 16, 28), r, 1)
        pygame.draw.line(self.ekran, (255, 230, 180), (r.x + 1, r.y + 1), (r.right - 2, r.y + 1))
        x = r.x + 4
        if ikona:
            self.ekran.blit(self.g[ikona], (x, r.centery - 8))
            x += 18
        if napis:
            f = f or self.f
            kol = C_TEKST if aktywny else C_SZARY
            if ikona:
                self.tekst(napis, x, r.centery - f.get_height() // 2 + 1, kol, f)
            else:
                self.tekst(napis, r.centerx, r.centery - f.get_height() // 2 + 1, kol, f, srodek=True)
        if aktywny:
            self.przyciski.append((r, akcja))
        return hover

    def rysuj(self):
        self.przyciski = []
        self.mysz = pygame.mouse.get_pos() if not self.zrzuty else self.mysz
        e = self.ekran
        if self.scena == "tytul":
            self.rysuj_tytul()
        elif self.scena == "intro":
            self.rysuj_intro()
        elif self.scena == "koniec":
            self.rysuj_koniec()
        else:
            e.fill((24, 16, 28))
            self.rysuj_swiat()
            self.rysuj_gorny_pasek()
            self.rysuj_panel()
            self.rysuj_dolny_pasek()
            if self.nakladka == "dialog":
                self.rysuj_dialog()
            elif self.nakladka == "ekwipunek":
                self.rysuj_ekwipunek()
            elif self.nakladka == "ksiega":
                self.rysuj_ksiege()
            elif self.nakladka == "plan":
                self.rysuj_plan()
            elif self.nakladka == "menu":
                self.rysuj_menu()
            elif self.nakladka == "pomoc":
                self.rysuj_pomoc()
        if self.nakladka == "pomoc" and self.scena == "tytul":
            self.rysuj_pomoc()

    # ------------------------------------------------------------ świat
    def rysuj_swiat(self):
        e = self.ekran
        cx, cy = self.kamera()
        e.set_clip(VIEW)
        klatka = int(self.t * 2) % 2
        e.blit(self.teren[klatka], (VIEW.x - cx, VIEW.y - cy))
        ox, oy = VIEW.x - cx, VIEW.y - cy

        # mury między gotowymi bastionami/bramami
        if self.stan.rozdzial >= 4:
            self.rysuj_mury(ox, oy)
        # kompas: działki z planu
        if self.kompas:
            dost = D.DOSTEPNE[self.stan.rozdzial]
            for typ, x, y in D.DZIALKI:
                if typ not in dost or self.dzialka_zajeta(typ, x, y):
                    continue
                d = D.BUDYNKI[typ]
                r = pygame.Rect(ox + x * KAF, oy + y * KAF, d["w"] * KAF, d["h"] * KAF)
                kol = (255, 220, 90) if int(self.t * 3) % 2 else (200, 150, 40)
                self.przerywany(r, kol)
                self.tekst(d["nazwa"] if typ != "brama" else self.nazwa_bramy(x, y), r.centerx, r.y + 2,
                           C_JASNY, self.fm, cien=(24, 16, 28), srodek=True)
        # obiekty sortowane po y
        obiekty = []
        for b in self.stan.budynki:
            d = D.BUDYNKI[b["typ"]]
            if b["typ"] == "rynek":
                if b["postep"] < d["czas"]:
                    for yy in range(d["h"]):
                        for xx in range(d["w"]):
                            if (xx + yy) % 2 == 0 or yy * d["w"] + xx < b["postep"] * 12:
                                e.blit(self.g["bruk"], (ox + (b["x"] + xx) * KAF, oy + (b["y"] + yy) * KAF))
                continue
            obiekty.append(((b["y"] + d["h"]) * KAF, "b", b))
        for k, n in D.NPC.items():
            obiekty.append((n["poz"][1] * KAF + 14, "n", k))
        obiekty.append((self.stan.bohater[1] + 2, "h", None))
        obiekty.sort(key=lambda o: o[0])
        for _, rodzaj, ob in obiekty:
            if rodzaj == "b":
                self.rysuj_budynek(ob, ox, oy)
            elif rodzaj == "n":
                self.rysuj_npc(ob, ox, oy)
            else:
                self.rysuj_bohatera(ox, oy)
        # duch budowy
        if self.wybrany:
            p = self.pozycja_ducha()
            if p:
                ok, _ = self.moze_budowac(self.wybrany, *p)
                d = D.BUDYNKI[self.wybrany]
                r = pygame.Rect(ox + p[0] * KAF, oy + p[1] * KAF, d["w"] * KAF, d["h"] * KAF)
                warstwa = pygame.Surface(r.size, pygame.SRCALPHA)
                warstwa.fill((80, 220, 80, 90) if ok else (230, 60, 60, 90))
                e.blit(warstwa, r)
                if self.wybrany != "rynek":
                    spr = self.sprite_budynku(self.wybrany, 0).copy()
                    spr.set_alpha(150)
                    e.blit(spr, (r.centerx - spr.get_width() // 2, r.bottom - spr.get_height()))
                pygame.draw.rect(e, (255, 255, 255) if ok else (255, 90, 90), r, 1)
        if self.rozbiorka:
            k = self.kafel_pod_mysza()
            if k:
                pygame.draw.rect(e, (255, 80, 60), (ox + k[0] * KAF, oy + k[1] * KAF, KAF, KAF), 1)
        # efekty
        for c in self.czastki:
            pygame.draw.rect(e, c[5], (ox + c[0], oy + c[1], 2, 2))
        for n in self.napisy:
            self.tekst(n[2], ox + n[0], oy + n[1], n[3], self.fm, cien=(24, 16, 28), srodek=True)
        if self.kompas:
            self.rysuj_kompas(ox, oy)
        # toasty
        for i, (t, czas) in enumerate(self.toasty):
            w = self.f.size(t)[0] + 16
            r = pygame.Rect(VIEW.centerx - w // 2, VIEW.y + 6 + i * 20, w, 18)
            pygame.draw.rect(e, (24, 16, 28), r)
            pygame.draw.rect(e, C_ZLOTY, r, 1)
            self.tekst(t, r.centerx, r.y + 4, C_JASNY, srodek=True)
        e.set_clip(None)

    def nazwa_bramy(self, x, y):
        for n, bx, by in D.BRAMY:
            if (bx, by) == (x, y):
                return n
        return "Brama"

    def przerywany(self, r, kol):
        for x in range(r.x, r.right, 4):
            pygame.draw.line(self.ekran, kol, (x, r.y), (min(x + 2, r.right - 1), r.y))
            pygame.draw.line(self.ekran, kol, (x, r.bottom - 1), (min(x + 2, r.right - 1), r.bottom - 1))
        for y in range(r.y, r.bottom, 4):
            pygame.draw.line(self.ekran, kol, (r.x, y), (r.x, min(y + 2, r.bottom - 1)))
            pygame.draw.line(self.ekran, kol, (r.right - 1, y), (r.right - 1, min(y + 2, r.bottom - 1)))

    def rysuj_mury(self, ox, oy):
        punkty = []
        for i, (x, y) in enumerate(D.BASTIONY):
            gotowy = any(b["typ"] == "bastion" and b["x"] == x - 1 and b["y"] == y - 1 and
                         b["postep"] >= D.BUDYNKI["bastion"]["czas"] for b in self.stan.budynki)
            punkty.append(((ox + x * KAF, oy + y * KAF), gotowy))
        for i in range(7):
            (a, ga), (b, gb) = punkty[i], punkty[(i + 1) % 7]
            if ga and gb:
                pygame.draw.line(self.ekran, (24, 16, 28), a, b, 7)
                pygame.draw.line(self.ekran, (162, 66, 46), a, b, 5)
                pygame.draw.line(self.ekran, (222, 140, 96), (a[0], a[1] - 2), (b[0], b[1] - 2), 1)
            else:
                dl = math.dist(a, b)
                for s in range(0, int(dl), 8):
                    t0, t1 = s / dl, min(1, (s + 4) / dl)
                    pygame.draw.line(self.ekran, (240, 230, 200),
                                     (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                                     (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1), 1)

    def sprite_budynku(self, typ, wariant):
        if typ == "kamienica":
            return self.g["kamienica_%d" % (wariant % 5)]
        return self.g[typ]

    def rysuj_budynek(self, b, ox, oy):
        d = D.BUDYNKI[b["typ"]]
        x, y = ox + b["x"] * KAF, oy + b["y"] * KAF
        w, h = d["w"] * KAF, d["h"] * KAF
        if b["postep"] < d["czas"]:
            # plac budowy z rusztowaniem
            pygame.draw.rect(self.ekran, (150, 120, 80), (x, y, w, h))
            spr = self.sprite_budynku(b["typ"], b["wariant"])
            frac = b["postep"] / d["czas"]
            if frac > 0:
                hh = int(spr.get_height() * frac)
                cz = spr.subsurface((0, spr.get_height() - hh, spr.get_width(), hh))
                self.ekran.blit(cz, (x + w // 2 - spr.get_width() // 2, y + h - hh))
            for yy in range(0, h, KAF):
                for xx in range(0, w, KAF):
                    self.ekran.blit(self.g["rusztowanie"], (x + xx, y + yy))
            pasek = pygame.Rect(x + 2, y + h - 4, w - 4, 3)
            pygame.draw.rect(self.ekran, (24, 16, 28), pasek)
            pygame.draw.rect(self.ekran, C_ZLOTY, (pasek.x, pasek.y, int(pasek.w * frac), 3))
            return
        spr = self.sprite_budynku(b["typ"], b["wariant"])
        self.ekran.blit(spr, (x + w // 2 - spr.get_width() // 2, y + h - spr.get_height() + 1))
        if b is self.info_budynek:
            pygame.draw.rect(self.ekran, C_ZLOTY, (x, y, w, h), 1)

    def rysuj_npc(self, k, ox, oy):
        n = D.NPC[k]
        x, y = ox + n["poz"][0] * KAF, oy + n["poz"][1] * KAF
        kl = int(self.t * 1.5 + hash(k) % 3) % 2
        spr = self.g["postac_%s_dol_%d" % (k, 0)]
        dy = -1 if kl else 0
        self.ekran.blit(spr, (x - 1, y - 10 + dy))
        flaga = "rozm_%s_%d" % (k, self.stan.rozdzial)
        if (k, self.stan.rozdzial) in D.ROZMOWY and flaga not in self.stan.flagi:
            self.ekran.blit(self.g["ui_wykrzyknik"], (x + 4, y - 24 + int(math.sin(self.t * 5) * 2)))
        if self.npc_obok() == k and not self.nakladka:
            self.ekran.blit(self.g["ui_e"], (x + 12, y - 20))

    def rysuj_bohatera(self, ox, oy):
        hx, hy = self.stan.bohater
        k = self.kier
        kl = int(self.anim * 7) % 2 if self.idzie else 0
        nazwa = "prawo" if k in ("prawo", "lewo") else k
        spr = self.g["postac_zamoyski_%s_%d" % (nazwa, kl)]
        if k == "lewo":
            spr = pygame.transform.flip(spr, True, False)
        pygame.draw.ellipse(self.ekran, (40, 70, 40), (ox + hx - 6, oy + hy - 1, 12, 4))
        self.ekran.blit(spr, (ox + hx - 9, oy + hy - 24))

    def rysuj_kompas(self, ox, oy):
        e = self.ekran
        rx, ry = VIEW.x + 6, VIEW.y + VIEW.h - 66
        e.blit(self.g["ui_roza"], (rx, ry))
        cel, opis = self.cel_kompasu()
        c = (rx + 28, ry + 28)
        hx, hy = self.stan.bohater
        if cel:
            dx, dy = cel[0] - hx, cel[1] - hy
            kat = math.atan2(dy, dx)
            kroki = int(math.hypot(dx, dy) / KAF)
            kier = kierunek_slownie(dx, dy) if kroki > 0 else "tutaj"
            linia = "%s — %s, %d kroków" % (opis, kier, kroki) if kroki > 0 else opis + " — jesteś na miejscu!"
            # znacznik celu na mapie
            pulse = 3 + int(abs(math.sin(self.t * 4)) * 3)
            pygame.draw.circle(e, (255, 230, 80), (int(ox + cel[0]), int(oy + cel[1])), 6 + pulse, 1)
        else:
            kat = -math.pi / 2 + math.sin(self.t * 2) * .15
            linia = opis
        dl = 17
        szpic = (c[0] + dl * math.cos(kat), c[1] + dl * math.sin(kat))
        ogon = (c[0] - dl * .7 * math.cos(kat), c[1] - dl * .7 * math.sin(kat))
        prost = (math.cos(kat + math.pi / 2) * 3, math.sin(kat + math.pi / 2) * 3)
        pygame.draw.polygon(e, (200, 40, 44), [szpic, (c[0] + prost[0], c[1] + prost[1]), (c[0] - prost[0], c[1] - prost[1])])
        pygame.draw.polygon(e, (40, 56, 120), [ogon, (c[0] + prost[0], c[1] + prost[1]), (c[0] - prost[0], c[1] - prost[1])])
        pygame.draw.circle(e, (244, 200, 72), c, 2)
        w = self.f.size(linia)[0] + 10
        r = pygame.Rect(rx + 58, ry + 38, w, 17)
        pygame.draw.rect(e, (24, 16, 28), r)
        pygame.draw.rect(e, C_ZLOTY, r, 1)
        self.tekst(linia, r.x + 5, r.y + 4, C_JASNY)

    # ------------------------------------------------------------ paski i panel
    def rysuj_gorny_pasek(self):
        e = self.ekran
        pygame.draw.rect(e, (46, 30, 26), (0, 0, SZER, 18))
        pygame.draw.line(e, (244, 200, 72), (0, 17), (SZER, 17))
        s = self.stan
        x = 4
        pozycje = [("ikona_zloto", "%d" % s.zasoby["zloto"], "Złoto"),
                   ("ikona_drewno", "%d" % s.zasoby["drewno"], "Drewno"),
                   ("ikona_kamien", "%d" % s.zasoby["kamien"], "Kamień"),
                   ("ikona_cegla", "%d" % s.zasoby["cegla"], "Cegła"),
                   ("ikona_ludnosc", "%d/%d" % (s.ludnosc, self.pojemnosc()), "Mieszczanie"),
                   ("ikona_robotnicy", "%d%%" % int(self.wydajnosc() * 100), "Praca"),
                   ("ikona_wiedza", "%d PW" % s.pw, "Wiedza")]
        for ik, war, _ in pozycje:
            e.blit(self.g[ik], (x, 1))
            x += 18
            x += self.tekst(war, x, 4, C_JASNY) + 10
        r = D.ROZDZIALY[s.rozdzial]
        self.tekst("%s · %s" % (r["lata"], "Rozdział %d/4" % s.rozdzial), SZER - 4 - self.f.size(
            "%s · Rozdział %d/4" % (r["lata"], s.rozdzial))[0], 4, C_ZLOTY)

    def rysuj_panel(self):
        e = self.ekran
        self.ramka(PANEL)
        s = self.stan
        r = D.ROZDZIALY[s.rozdzial]
        x0 = PANEL.x + 8
        self.tekst("Cele rozdziału", x0, PANEL.y + 7, C_CZERW, self.f)
        y = PANEL.y + 21
        for c in self.cele():
            a, b = self.stan_celu(c)
            gotowe = a >= b
            pygame.draw.rect(e, C_TEKST, (x0, y + 1, 8, 8), 1)
            if gotowe:
                pygame.draw.line(e, C_ZIELONY, (x0 + 1, y + 4), (x0 + 3, y + 7), 2)
                pygame.draw.line(e, C_ZIELONY, (x0 + 3, y + 7), (x0 + 8, y), 2)
            opis = c[0] + ("" if b == 1 else " (%d/%d)" % (a, b))
            for i, linia in enumerate(zawijaj(opis, self.fm, 164)):
                self.tekst(linia, x0 + 12, y + 1, C_ZIELONY if gotowe else C_TEKST, self.fm)
                y += 10
            y += 2
        # budowa
        yb = PANEL.y + 128
        pygame.draw.line(e, (196, 168, 120), (x0, yb - 4), (PANEL.right - 8, yb - 4))
        self.tekst("Budowa", x0, yb, C_CZERW)
        dost = D.DOSTEPNE[s.rozdzial]
        self.najechany = None
        for i, typ in enumerate(dost):
            kx, ky = x0 + (i % 4) * 44, yb + 13 + (i // 4) * 30
            rect = pygame.Rect(kx, ky, 42, 28)
            d = D.BUDYNKI[typ]
            zablok = d.get("min_pw", 0) > s.pw
            hover = rect.collidepoint(self.mysz)
            if hover:
                self.najechany = typ
            wyb = self.wybrany == typ
            pygame.draw.rect(e, (24, 16, 28), rect)
            pygame.draw.rect(e, C_ZLOTY if wyb else ((228, 208, 164) if hover else (200, 172, 124)), rect.inflate(-2, -2))
            spr = self.g["bruk"] if typ == "rynek" else self.sprite_budynku(typ, 1)
            sk = min(24 / spr.get_height(), 38 / spr.get_width(), 1.0)
            mini = pygame.transform.scale(spr, (max(1, int(spr.get_width() * sk)), max(1, int(spr.get_height() * sk))))
            e.blit(mini, (rect.centerx - mini.get_width() // 2, rect.bottom - 2 - mini.get_height()))
            if not self.stac(typ) or zablok:
                zas = pygame.Surface((40, 26), pygame.SRCALPHA)
                zas.fill((60, 40, 30, 110))
                e.blit(zas, (rect.x + 1, rect.y + 1))
            if d.get("zabytek") and all(self.dzialka_zajeta(typ, x, y) for x, y in self.dzialki_typu(typ)):
                pygame.draw.line(e, C_ZIELONY, (rect.right - 9, rect.y + 5), (rect.right - 6, rect.y + 8), 2)
                pygame.draw.line(e, C_ZIELONY, (rect.right - 6, rect.y + 8), (rect.right - 2, rect.y + 2), 2)

            def wybierz(t=typ):
                self.wybrany = None if self.wybrany == t else t
                self.rozbiorka = False
                self.info_budynek = None
                self.dzwiek("klik")
            self.przyciski.append((rect, wybierz))
        # info
        yi = PANEL.y + 262
        pygame.draw.line(e, (196, 168, 120), (x0, yi - 3), (PANEL.right - 8, yi - 3))
        typ = self.najechany or self.wybrany
        if typ:
            d = D.BUDYNKI[typ]
            self.tekst(d["nazwa"], x0, yi, C_CZERW)
            xk = x0
            for a, v in self.koszt(typ).items():
                ma = s.zasoby.get(a, 0) >= v
                e.blit(self.g["ikona_" + a], (xk, yi + 11))
                xk += 16
                xk += self.tekst(str(v), xk, yi + 15, C_TEKST if ma else C_CZERW, self.fm) + 5
            for i, linia in enumerate(zawijaj(d["opis"], self.fm, 176)[:3]):
                self.tekst(linia, x0, yi + 29 + i * 10, C_TEKST, self.fm)
        elif self.info_budynek:
            b = self.info_budynek
            d = D.BUDYNKI[b["typ"]]
            self.tekst(d["nazwa"], x0, yi, C_CZERW)
            stan = "W budowie (%d/%d dni)" % (b["postep"], d["czas"]) if b["postep"] < d["czas"] else "Gotowe"
            self.tekst(stan, x0, yi + 12, C_TEKST, self.fm)
            for i, linia in enumerate(zawijaj(d["opis"], self.fm, 176)[:3]):
                self.tekst(linia, x0, yi + 24 + i * 10, C_TEKST, self.fm)
        else:
            for i, linia in enumerate(zawijaj("Wskaż budynek, aby zobaczyć koszt. Kliknij, a potem kliknij na mapie. "
                                               "Prawy przycisk anuluje.", self.fm, 176)):
                self.tekst(linia, x0, yi + 2 + i * 10, C_SZARY, self.fm)

    def rysuj_dolny_pasek(self):
        e = self.ekran
        y = 338
        pygame.draw.rect(e, (46, 30, 26), (0, y, SZER, 22))
        pygame.draw.line(e, (244, 200, 72), (0, y), (SZER, y))
        przyc = [("Ekwipunek", "ikona_sakiewka", lambda: self.przelacz("ekwipunek"), self.nakladka == "ekwipunek"),
                 ("Księga", "ikona_wiedza", lambda: self.przelacz("ksiega"), self.nakladka == "ksiega"),
                 ("Kompas", "ikona_kompas", lambda: self.uzyj_przedmiotu("kompas"), self.kompas),
                 ("Rozbiórka", "ikona_rozbiorka", self.przelacz_rozbiorke, self.rozbiorka),
                 ("Pomoc", "ikona_pomoc", lambda: self.przelacz("pomoc"), self.nakladka == "pomoc"),
                 ("Menu", "ikona_menu", lambda: self.przelacz("menu"), self.nakladka == "menu")]
        x = 3
        for napis, ik, akcja, wyb in przyc:
            w = self.fm.size(napis)[0] + 26
            self.przycisk((x, y + 2, w, 19), napis, akcja, ik, wybrany=wyb, f=self.fm)
            x += w + 3
        # dzień targowy
        bx = x + 6
        e.blit(self.g["ikona_dzien"], (bx, y + 3))
        pr = pygame.Rect(bx + 18, y + 8, 60, 7)
        pygame.draw.rect(e, (24, 16, 28), pr)
        pygame.draw.rect(e, C_ZLOTY, (pr.x + 1, pr.y + 1, int((pr.w - 2) * self.zegar_dnia / DZIEN_SEK), pr.h - 2))
        self.tekst("Dzień %d" % self.stan.dzien, pr.right + 5, y + 6, C_JASNY, self.fm)
        rang = D.ranga(self.stan.pw)
        self.tekst(rang, SZER - 5 - self.fm.size(rang)[0], y + 6, C_ZLOTY, self.fm)

    def przelacz_rozbiorke(self):
        self.rozbiorka = not self.rozbiorka
        self.wybrany = None
        self.dzwiek("klik")

    # ------------------------------------------------------------ nakładki
    def przyciemnij(self, alfa=140):
        s = pygame.Surface((SZER, WYS), pygame.SRCALPHA)
        s.fill((10, 6, 14, alfa))
        self.ekran.blit(s, (0, 0))

    def rysuj_dialog(self):
        dl = self.dialog
        e = self.ekran
        r = pygame.Rect(6, 226, 628, 108)
        if dl.tryb == "zagadka" or dl.tryb == "wynik":
            r = pygame.Rect(6, 150, 628, 184)
        self.ramka(r)
        if dl.tryb == "tekst":
            mowca, tekst = dl.biezaca()
        else:
            mowca = dl.kwestie[-1][0] if dl.kwestie else "narrator"
            tekst = ""
        port = "portret_" + mowca
        tx = r.x + 14
        if port in self.g:
            pr = pygame.Rect(r.x + 12, r.y + 12, 68, 68)
            pygame.draw.rect(e, (24, 16, 28), pr)
            e.blit(pygame.transform.scale(self.g[port], (64, 64)), (pr.x + 2, pr.y + 2))
            tx = pr.right + 10
        else:
            e.blit(pygame.transform.scale(self.g["ikona_ksiega"], (32, 32)), (r.x + 14, r.y + 14))
            tx = r.x + 56
        imie = D.NAZWY_POSTACI.get(mowca, mowca)
        self.tekst(imie, tx, r.y + 12, C_CZERW, self.fd)
        szer = r.right - tx - 14
        if dl.tryb == "tekst":
            widoczny = tekst[:int(dl.znaki)]
            for i, linia in enumerate(zawijaj(widoczny, self.f, szer)):
                self.tekst(linia, tx, r.y + 32 + i * 13)
            if dl.znaki >= len(tekst) and int(self.t * 2) % 2:
                self.tekst("dalej » (Spacja / klik)", r.right - 14 - self.fm.size("dalej » (Spacja / klik)")[0],
                           r.bottom - 16, C_SZARY, self.fm)
        else:
            q = dl.zagadka
            self.tekst("ZAGADKA", tx + self.fd.size(imie)[0] + 10, r.y + 14, C_ZIELONY, self.f)
            linie = zawijaj(q["pytanie"], self.f, szer)
            for i, linia in enumerate(linie):
                self.tekst(linia, tx, r.y + 32 + i * 13)
            y = r.y + 36 + len(linie) * 13
            if dl.tryb == "zagadka":
                for i, o in enumerate(dl.odp):
                    br = pygame.Rect(tx, y + i * 24, szer, 20)
                    zle = i in dl.zle
                    self.przycisk(br, "%d. %s" % (i + 1, o), lambda i=i: self.odpowiedz(i), aktywny=not zle)
                    if zle:
                        pygame.draw.line(e, C_CZERW, (br.x + 6, br.centery), (br.right - 6, br.centery), 2)
                if dl.zle:
                    self.tekst("Nie tym razem — spróbuj jeszcze raz!", tx, y + 74, C_CZERW, self.fm)
            else:
                self.tekst("Brawo! Dobra odpowiedź: " + q["poprawna"], tx, y, C_ZIELONY)
                for i, linia in enumerate(zawijaj(q["wyjasnienie"], self.f, szer)):
                    self.tekst(linia, tx, y + 16 + i * 13)
                self.przycisk((r.right - 110, r.bottom - 30, 96, 20), "Dalej", self.zamknij_dialog)

    def okienko(self, tytul, w=420, h=260):
        self.przyciemnij()
        r = pygame.Rect((SZER - w) // 2, (WYS - h) // 2, w, h)
        self.ramka(r)
        self.tekst(tytul, r.centerx, r.y + 9, C_CZERW, self.fd, srodek=True)
        self.przycisk((r.right - 26, r.y + 7, 18, 16), "x", lambda: setattr(self, "nakladka", None))
        return r

    def rysuj_ekwipunek(self):
        r = self.okienko("Ekwipunek Jana Zamoyskiego", 440, 250)
        e = self.ekran
        sloty = 10
        for i in range(sloty):
            sr = pygame.Rect(r.x + 16 + (i % 5) * 44, r.y + 34 + (i // 5) * 44, 40, 40)
            pygame.draw.rect(e, (24, 16, 28), sr)
            pygame.draw.rect(e, (120, 86, 54), sr.inflate(-2, -2))
            pygame.draw.rect(e, (90, 62, 40), sr.inflate(-6, -6))
            if i < len(self.stan.ekwipunek):
                p = self.stan.ekwipunek[i]
                e.blit(pygame.transform.scale(self.g["ikona_" + D.PRZEDMIOTY[p]["ikona"]], (32, 32)), (sr.x + 4, sr.y + 4))
                if self.wybrany_przedm == i:
                    pygame.draw.rect(e, C_ZLOTY, sr, 2)

                def wybierz(i=i):
                    self.wybrany_przedm = i
                    self.dzwiek("klik")
                self.przyciski.append((sr, wybierz))
        ox = r.x + 248
        if self.wybrany_przedm is not None and self.wybrany_przedm < len(self.stan.ekwipunek):
            p = self.stan.ekwipunek[self.wybrany_przedm]
            d = D.PRZEDMIOTY[p]
            e.blit(pygame.transform.scale(self.g["ikona_" + d["ikona"]], (48, 48)), (ox + 64, r.y + 30))
            for i, linia in enumerate(zawijaj(d["nazwa"], self.f, 176)):
                self.tekst(linia, ox + 88, r.y + 84 + i * 13, C_CZERW, srodek=True)
            for i, linia in enumerate(zawijaj(d["opis"], self.fm, 176)):
                self.tekst(linia, ox, r.y + 104 + i * 11, C_TEKST, self.fm)
            if d["uzycie"]:
                self.przycisk((ox + 40, r.bottom - 32, 96, 20), "Użyj", lambda: self.uzyj_przedmiotu(p))
        else:
            for i, linia in enumerate(zawijaj("Kliknij przedmiot, aby przeczytać jego opis. Nowe przedmioty "
                                               "zdobywasz za rozmowy i ukończone rozdziały.", self.fm, 176)):
                self.tekst(linia, ox, r.y + 40 + i * 11, C_SZARY, self.fm)
        self.tekst("Punkty Wiedzy: %d   ·   Ranga: %s" % (self.stan.pw, D.ranga(self.stan.pw)),
                   r.x + 16, r.bottom - 40, C_TEKST)
        self.tekst("Karty Księgi: %d/%d przeczytanych" % (len(self.stan.przeczytane), len(D.WIEDZA)),
                   r.x + 16, r.bottom - 24, C_TEKST, self.fm)

    def rysuj_ksiege(self):
        r = self.okienko("Księga Wiedzy", 520, 290)
        e = self.ekran
        klucze = [k for k in D.WIEDZA if k in self.stan.karty]
        ukryte = len(D.WIEDZA) - len(klucze)
        widoczne = 15
        self.przesun_ksiegi = min(self.przesun_ksiegi, max(0, len(klucze) - widoczne))
        lista = klucze[self.przesun_ksiegi:self.przesun_ksiegi + widoczne]
        for i, k in enumerate(lista):
            br = pygame.Rect(r.x + 12, r.y + 30 + i * 16, 170, 15)
            nowa = k not in self.stan.przeczytane

            def czytaj(k=k):
                self.wybrana_karta = k
                self.dzwiek("strona")
                if k not in self.stan.przeczytane:
                    self.stan.przeczytane.append(k)
                    zysk = 3 if "pioro" in self.stan.ekwipunek else 2
                    self.stan.pw += zysk
                    self.toast("+%d PW za przeczytanie karty!" % zysk)
            hover = br.collidepoint(self.mysz)
            if self.wybrana_karta == k or hover:
                pygame.draw.rect(e, (244, 232, 200) if hover else (250, 220, 140), br)
            tytul = D.WIEDZA[k][0]
            if self.fm.size(tytul)[0] > 150:
                while self.fm.size(tytul + "…")[0] > 150:
                    tytul = tytul[:-1]
                tytul += "…"
            self.tekst(tytul, br.x + 4, br.y + 3, C_TEKST, self.fm)
            if nowa:
                self.tekst("nowa!", br.right - 28, br.y + 3, C_CZERW, self.fm)
            self.przyciski.append((br, czytaj))
        if len(klucze) > widoczne:
            self.przycisk((r.x + 12, r.bottom - 22, 40, 16), "w górę", lambda: setattr(self, "przesun_ksiegi",
                                                                                   max(0, self.przesun_ksiegi - 3)), f=self.fm)
            self.przycisk((r.x + 56, r.bottom - 22, 40, 16), "w dół", lambda: setattr(self, "przesun_ksiegi",
                                                                                   self.przesun_ksiegi + 3), f=self.fm)
        if ukryte:
            self.tekst("Do odkrycia: %d" % ukryte, r.x + 104, r.bottom - 19, C_SZARY, self.fm)
        pygame.draw.line(e, (196, 168, 120), (r.x + 190, r.y + 30), (r.x + 190, r.bottom - 12))
        tx = r.x + 200
        if self.wybrana_karta:
            t, opis = D.WIEDZA[self.wybrana_karta]
            self.tekst(t, tx, r.y + 32, C_CZERW, self.fd)
            for i, linia in enumerate(zawijaj(opis, self.f, r.right - tx - 14)):
                self.tekst(linia, tx, r.y + 54 + i * 14)
        else:
            for i, linia in enumerate(zawijaj("Wybierz kartę z listy. Każda nowo przeczytana karta daje Punkty "
                                               "Wiedzy! Nowe karty odkrywasz, budując zabytki i rozmawiając "
                                               "z postaciami.", self.f, r.right - tx - 14)):
                self.tekst(linia, tx, r.y + 40 + i * 14, C_SZARY)

    def rysuj_plan(self):
        r = self.okienko("Plan miasta Bernarda Morando", 500, 270)
        e = self.ekran
        sk = 0.5
        mini = pygame.transform.scale(self.teren[0], (int(D.MAPA_W * KAF * sk), int(D.MAPA_H * KAF * sk)))
        # sepia
        sep = pygame.Surface(mini.get_size(), pygame.SRCALPHA)
        sep.fill((240, 210, 150, 120))
        mini.blit(sep, (0, 0))
        mx, my = r.x + 12, r.y + 30
        e.blit(mini, (mx, my))
        pygame.draw.rect(e, (24, 16, 28), (mx, my, mini.get_width(), mini.get_height()), 1)
        pk = [(mx + x * KAF * sk, my + y * KAF * sk) for x, y in D.BASTIONY]
        pygame.draw.polygon(e, (120, 50, 40), pk, 2)
        for typ, x, y in D.DZIALKI:
            d = D.BUDYNKI[typ]
            rr = pygame.Rect(mx + x * KAF * sk, my + y * KAF * sk, d["w"] * KAF * sk, d["h"] * KAF * sk)
            gotowe = self.dzialka_zajeta(typ, x, y)
            pygame.draw.rect(e, (40, 56, 120) if not gotowe else (40, 120, 50), rr, 1 if typ == "rynek" else 0)
        for et, x, y in [("głowa", 8.5, 8.6), ("płuco", 14, 5.6), ("płuco", 13.6, 16.2), ("kręgosłup", 13, 11.4),
                         ("serce", 21.6, 15.2)]:
            self.tekst(et, mx + x * KAF * sk, my + y * KAF * sk, C_CZERW, self.fm, cien=(250, 240, 210))
        hx, hy = self.stan.bohater
        pygame.draw.circle(e, (230, 40, 40), (int(mx + hx * sk), int(my + hy * sk)), 3)
        tx = mx + mini.get_width() + 10
        tekst = ("Plan Zamościa przypomina człowieka: pałac to głowa, główna ulica to kręgosłup, "
                 "a Akademia i Kolegiata to płuca. Rynek jest sercem handlu.\n\n"
                 "Granatowe pola: do zbudowania.\nZielone: zbudowane.\nCzerwona kropka: Ty.\n"
                 "Linia: wały między 7 bastionami.")
        for i, linia in enumerate(zawijaj(tekst, self.fm, r.right - tx - 10)):
            self.tekst(linia, tx, r.y + 34 + i * 11, C_TEKST, self.fm)
        self.tekst("N", mx + mini.get_width() - 24, my + 4, C_CZERW, self.f)

    def rysuj_menu(self):
        r = self.okienko("Menu", 240, 190)
        opcje = [("Wróć do gry", lambda: setattr(self, "nakladka", None)),
                 ("Zapisz grę", self.zapisz_menu),
                 ("Muzyka: " + ("wł." if self.muzyka_on else "wył."), self.przelacz_muzyke),
                 ("Menu główne", self.do_tytulu),
                 ("Wyjście z gry", self.wyjdz)]
        for i, (n, a) in enumerate(opcje):
            self.przycisk((r.x + 30, r.y + 34 + i * 29, r.w - 60, 23), n, a)

    def zapisz_menu(self):
        self.zapisz()
        self.toast("Gra zapisana!")
        self.nakladka = None

    def przelacz_muzyke(self):
        self.muzyka_on = not self.muzyka_on
        (pygame.mixer.music.unpause if self.muzyka_on else pygame.mixer.music.pause)()

    def do_tytulu(self):
        self.zapisz()
        self.nakladka = None
        self.scena = "tytul"

    def wyjdz(self):
        self.zapisz()
        pygame.quit()
        sys.exit()

    def rysuj_pomoc(self):
        r = self.okienko("Pomoc", 440, 270)
        for i, linia in enumerate(D.POMOC):
            gl = linia.isupper()
            self.tekst(linia, r.x + 18, r.y + 32 + i * 14, C_CZERW if gl else C_TEKST, self.f)

    # ------------------------------------------------------------ ekrany
    def rysuj_tytul(self):
        e = self.ekran
        e.blit(self.g["tlo_tytul"], (0, 0))
        tyt1, tyt2 = "Jan Zamoyski", "i Miasto Idealne"
        for t, y, f in [(tyt1, 22, self.fogromna), (tyt2, 56, self.fduza)]:
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (2, 2)):
                self.tekst(t, SZER // 2 + dx, y + dy, (24, 16, 28), f, srodek=True)
            self.tekst(t, SZER // 2, y, C_ZLOTY, f, srodek=True)
        self.tekst("Strategia edukacyjna · Zamość, XVI wiek", SZER // 2, 88, C_JASNY, self.f,
                   cien=(24, 16, 28), srodek=True)
        e.blit(pygame.transform.scale(self.g["postac_zamoyski_dol_%d" % (int(self.t * 2) % 2)], (54, 78)), (130, 110))
        e.blit(pygame.transform.scale(self.g["ikona_kompas"], (32, 32)), (98, 150 + int(math.sin(self.t * 3) * 3)))
        r = pygame.Rect(SZER // 2 - 90, 110, 180, 132)
        self.ramka(r)
        ma_zapis = os.path.exists(plik_zapisu())
        opcje = [("Nowa gra", self.nowa_gra, True), ("Kontynuuj", self.wczytaj, ma_zapis),
                 ("Jak grać?", lambda: setattr(self, "nakladka", "pomoc" if self.nakladka != "pomoc" else None), True),
                 ("Wyjście", self.wyjdz, True)]
        for i, (n, a, akt) in enumerate(opcje):
            self.przycisk((r.x + 18, r.y + 14 + i * 27, r.w - 36, 22), n, a, aktywny=akt)
        self.tekst("Dla graczy w wieku 10–12 lat · Python + Pygame", SZER // 2, WYS - 14, C_JASNY, self.fm,
                   cien=(24, 16, 28), srodek=True)

    def rysuj_intro(self):
        e = self.ekran
        r = D.ROZDZIALY[self.stan.rozdzial]
        e.blit(self.g["tlo_rozdzial_%d" % self.stan.rozdzial], (0, 0))
        okno = pygame.Rect(60, 14, 520, 196)
        self.ramka(okno)
        self.tekst(r["tytul"], okno.centerx, okno.y + 12, C_CZERW, self.fduza if self.fduza.size(r["tytul"])[0] < 480
                   else self.fd, srodek=True)
        self.tekst(r["lata"], okno.centerx, okno.y + 40, C_TEKST, self.f, srodek=True)
        widoczny = r["wstep"][:int(self.intro_znaki)]
        for i, linia in enumerate(zawijaj(widoczny, self.f, okno.w - 40)):
            self.tekst(linia, okno.x + 20, okno.y + 58 + i * 13)
        if self.intro_znaki >= len(r["wstep"]) and int(self.t * 2) % 2:
            self.tekst("Kliknij lub wciśnij Spację, aby zacząć", okno.centerx, okno.bottom - 16, C_SZARY, self.fm,
                       srodek=True)

    def rysuj_koniec(self):
        e = self.ekran
        e.blit(self.g["tlo_koniec"], (0, 0))
        r = pygame.Rect(90, 16, 460, 200)
        self.ramka(r)
        self.tekst("Zamość — Perła Renesansu", r.centerx, r.y + 12, C_CZERW, self.fduza, srodek=True)
        s = self.stan
        linie = [
            "Brawo! Razem z Janem Zamoyskim zbudowałeś miasto idealne.",
            "Zamoyski zmarł w 1605 r., ale jego miasto przetrwało wieki.",
            "W 1992 r. Stare Miasto w Zamościu wpisano na listę UNESCO.",
            "",
            "Budowli: %d   ·   Mieszczan: %d   ·   Dni budowy: %d" % (len(s.budynki), s.ludnosc, s.dzien),
            "Punkty Wiedzy: %d   ·   Karty Księgi: %d/%d" % (s.pw, len(s.przeczytane), len(D.WIEDZA)),
            "Twoja ranga: %s" % D.ranga(s.pw),
        ]
        for i, l in enumerate(linie):
            self.tekst(l, r.centerx, r.y + 48 + i * 15, C_CZERW if l.startswith("Twoja") else C_TEKST,
                       self.f, srodek=True)
        self.przycisk((r.centerx - 70, r.bottom - 30, 140, 20), "Menu główne", self.do_tytulu)

    # ====================================================================== pętla
    def petla(self):
        while True:
            dt = min(self.zegar.tick(60) / 1000, .05)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.wyjdz()
                elif e.type == pygame.KEYDOWN:
                    self.klawisz(e)
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self.mysz = e.pos
                    self.klik(e)
                elif e.type == pygame.MOUSEWHEEL and self.nakladka == "ksiega":
                    self.przesun_ksiegi = max(0, self.przesun_ksiegi - e.y)
            self.aktualizuj(dt)
            self.rysuj()
            pygame.display.flip()


# ====================================================================== zrzuty ekranu
def zrob_zrzuty(katalog):
    os.makedirs(katalog, exist_ok=True)
    g = Gra(zrzuty=katalog)
    random.seed(3)

    def zapisz(nazwa, kroki=1):
        for _ in range(kroki):
            g.aktualizuj(1 / 30)
            g.rysuj()
        pygame.image.save(pygame.transform.scale(g.ekran, (SZER * 2, WYS * 2)), os.path.join(katalog, nazwa + ".png"))
        print("zapisano", nazwa)

    g.mysz = (320, 180)
    zapisz("01_tytul")
    g.nowa_gra()
    g.intro_znaki = 9999
    zapisz("02_rozdzial1")
    # Rozdział 2, miasto w budowie
    s = g.stan
    s.rozdzial = 2
    s.flagi = ["powitanie", "rozm_morando_1"]
    s.ekwipunek = ["kompas", "prowiant", "plan", "przywilej"]
    s.karty += ["morando", "miasto_idealne", "palac", "lokacja", "magdeburskie", "rynek"]
    s.przeczytane = ["zamoyski", "kompas", "renesans", "morando", "palac"]
    s.pw = 34
    s.dzien = 41
    s.zasoby = {"zloto": 212, "drewno": 96, "kamien": 58, "cegla": 31}
    s.ludnosc = 46
    bud = [("palac", 10, 10, 9), ("tartak", 6, 3, 9), ("kamieniolom", 5, 20, 9), ("rynek", 20, 9, 9),
           ("dom", 9, 13, 9), ("dom", 10, 13, 9), ("dom", 11, 15, 9), ("dom", 9, 15, 9), ("dom", 17, 14, 9),
           ("dom", 18, 6, 9), ("cegielnia", 32, 6, 9), ("kamienica", 26, 9, 9), ("kamienica", 26, 11, 9),
           ("kamienica", 20, 7, 9), ("kamienica", 24, 7, 1), ("kram", 21, 12, 9), ("kram", 24, 13, 9),
           ("ratusz", 22, 9, 2)]
    s.budynki = [dict(typ=t, x=x, y=y, postep=p, wariant=i) for i, (t, x, y, p) in enumerate(bud)]
    s.bohater = [20 * KAF, 14 * KAF]
    g.odbuduj_swiat()
    g.scena = "gra"
    g.kompas = True
    g.kier = "prawo"
    g.zegar_dnia = 2.5
    g.wybrany = "kamienica"
    g.mysz = (330, 120)
    g.toast("Ukończono: Kamienica!")
    zapisz("03_rozgrywka_kompas", 3)
    g.wybrany = None
    g.kompas = False
    g.rozmawiaj("hagop")
    for _ in range(3):
        g.dialog.znaki = 999
        g.dalej_dialog()
    g.dialog.znaki = 999
    zapisz("04_dialog", 2)
    g.dalej_dialog()
    zapisz("05_zagadka")
    g.zamknij_dialog()
    g.nakladka = "ekwipunek"
    g.wybrany_przedm = 0
    zapisz("06_ekwipunek")
    g.nakladka = "ksiega"
    g.wybrana_karta = "miasto_idealne"
    zapisz("07_ksiega")
    g.nakladka = "plan"
    zapisz("08_plan")
    # Rozdział 4 — twierdza
    g.nakladka = None
    s.rozdzial = 4
    s.pw = 112
    for i, (x, y) in enumerate(D.BASTIONY[:6]):
        s.budynki.append(dict(typ="bastion", x=x - 1, y=y - 1, postep=3 if i < 5 else 1, wariant=0))
    s.budynki.append(dict(typ="brama", x=19, y=3, postep=3, wariant=0))
    s.budynki += [dict(typ="akademia", x=14, y=7, postep=5, wariant=0), dict(typ="kolegiata", x=14, y=13, postep=5,
                                                                            wariant=0)]
    for b in s.budynki:
        if b["typ"] == "ratusz" or b["typ"] == "kamienica":
            b["postep"] = 9
    s.flagi.append("rozm_morando_4")
    s.bohater = [16 * KAF, 5 * KAF]
    g.odbuduj_swiat()
    g.kompas = True
    zapisz("09_twierdza", 3)
    g.kompas = False
    g.scena = "intro"
    g.intro_znaki = 9999
    zapisz("10_rozdzial4")
    g.scena = "koniec"
    s.przeczytane = list(D.WIEDZA)[:17]
    zapisz("11_koniec")
    pygame.quit()


if __name__ == "__main__":
    if "--zrzuty" in sys.argv:
        zrob_zrzuty(sys.argv[sys.argv.index("--zrzuty") + 1])
    else:
        Gra().petla()
