"""Logika gry niezależna od grafiki: stan, warunki, efekty, dialogi, zapis.

Dzięki temu cała rozgrywka może być testowana automatycznie bez okna.
"""
import json
import os

from .dane import rozdzialy as R
from .dane import dialogi as D
from .dane import fakty as F
from .dane import postacie as P
from .dane import minigry_dane as MD


class Zdarzenie:
    """Zdarzenia dla warstwy prezentacji (sceny)."""
    IDZ = "idz"
    DIALOG = "dialog"
    MINIGRA = "minigra"
    DAMIAN = "damian"
    MOW = "mow"
    MIT = "mit"
    KONIEC_ROZDZIALU = "koniec_rozdzialu"
    PRZEDMIOT = "przedmiot"
    FAKT = "fakt"


class Stan:
    def __init__(self):
        self.flagi = set()
        self.ekwipunek = []
        self.fakty = []          # kolejność odkrycia
        self.mity = {}           # id -> True/False (czy odpowiedź była poprawna) albo None (oczekuje)
        self.poznani = []
        self.rozdzial = 0        # indeks w R.ROZDZIALY
        self.lokacja = R.ROZDZIALY[0]["start"]
        self.napiecie = 0
        self.ukonczona = False

    # ------------------------------------------------------------- warunki
    def warunek(self, w):
        neg = w.startswith("!")
        if neg:
            w = w[1:]
        if w.startswith("napiecie>="):
            wynik = self.napiecie >= int(w.split(">=")[1])
        else:
            rodzaj, _, arg = w.partition(":")
            if rodzaj == "flag":
                wynik = arg in self.flagi
            elif rodzaj == "ma":
                wynik = arg in self.ekwipunek
            elif rodzaj == "fakt":
                wynik = arg in self.fakty
            elif rodzaj == "poznal":
                wynik = arg in self.poznani
            else:
                raise ValueError("Nieznany warunek: %r" % w)
        return (not wynik) if neg else wynik

    def warunki(self, lista):
        return all(self.warunek(w) for w in (lista or []))

    # ------------------------------------------------------------- efekty
    def efekt(self, e):
        """Wykonuje efekt i zwraca listę zdarzeń dla prezentacji."""
        rodzaj, _, arg = e.partition(":")
        zd = []
        if rodzaj == "flag":
            self.flagi.add(arg)
        elif rodzaj == "unflag":
            self.flagi.discard(arg)
        elif rodzaj == "daj":
            if arg not in self.ekwipunek:
                self.ekwipunek.append(arg)
                zd.append((Zdarzenie.PRZEDMIOT, arg))
        elif rodzaj == "zabierz":
            if arg in self.ekwipunek:
                self.ekwipunek.remove(arg)
        elif rodzaj == "fakt":
            if arg not in self.fakty:
                self.fakty.append(arg)
                zd.append((Zdarzenie.FAKT, arg))
        elif rodzaj == "mit":
            if arg not in self.mity:
                self.mity[arg] = None
                zd.append((Zdarzenie.MIT, arg))
        elif rodzaj == "poznaj":
            if arg not in self.poznani:
                self.poznani.append(arg)
        elif rodzaj == "idz":
            self.lokacja = arg
            zd.append((Zdarzenie.IDZ, arg))
        elif rodzaj == "dialog":
            zd.append((Zdarzenie.DIALOG, arg))
        elif rodzaj == "minigra":
            zd.append((Zdarzenie.MINIGRA, arg))
        elif rodzaj == "damian":
            zd.append((Zdarzenie.DAMIAN, arg))
        elif rodzaj == "napiecie":
            if arg.startswith("+"):
                self.napiecie += int(arg[1:])
            else:
                self.napiecie = int(arg)
        elif rodzaj == "koniec_rozdzialu":
            zd.append((Zdarzenie.KONIEC_ROZDZIALU, R.ROZDZIALY[self.rozdzial]["id"]))
        else:
            raise ValueError("Nieznany efekt: %r" % e)
        return zd

    def efekty(self, lista):
        zd = []
        for e in lista or []:
            zd.extend(self.efekt(e))
        return zd

    # ------------------------------------------------------------- mity
    def odpowiedz_mit(self, mid, indeks):
        mit = F.MITY[mid]
        dobrze = indeks == mit["dobra"]
        self.mity[mid] = dobrze
        if mit.get("fakt") and mit["fakt"] not in self.fakty:
            self.fakty.append(mit["fakt"])
        return dobrze

    # ------------------------------------------------------------- rozdziały
    def nastepny_rozdzial(self):
        """Przechodzi do kolejnego rozdziału; zwraca False, gdy to był ostatni."""
        self.flagi.add("ukonczono_" + R.ROZDZIALY[self.rozdzial]["id"])
        if self.rozdzial + 1 >= len(R.ROZDZIALY):
            self.ukonczona = True
            return False
        self.rozdzial += 1
        self.lokacja = R.ROZDZIALY[self.rozdzial]["start"]
        self.napiecie = 0
        return True

    # ------------------------------------------------------------- zapis
    def do_slownika(self):
        return {
            "flagi": sorted(self.flagi), "ekwipunek": self.ekwipunek, "fakty": self.fakty,
            "mity": self.mity, "poznani": self.poznani, "rozdzial": self.rozdzial,
            "lokacja": self.lokacja, "ukonczona": self.ukonczona,
        }

    @classmethod
    def ze_slownika(cls, d):
        s = cls()
        s.flagi = set(d.get("flagi", []))
        s.ekwipunek = list(d.get("ekwipunek", []))
        s.fakty = list(d.get("fakty", []))
        s.mity = dict(d.get("mity", {}))
        s.poznani = list(d.get("poznani", []))
        s.rozdzial = int(d.get("rozdzial", 0))
        s.lokacja = d.get("lokacja", R.ROZDZIALY[s.rozdzial]["start"])
        s.ukonczona = bool(d.get("ukonczona", False))
        return s

    def zapisz(self, sciezka):
        with open(sciezka, "w", encoding="utf-8") as f:
            json.dump(self.do_slownika(), f, ensure_ascii=False, indent=1)

    @classmethod
    def wczytaj(cls, sciezka):
        if not os.path.exists(sciezka):
            return None
        try:
            with open(sciezka, encoding="utf-8") as f:
                return cls.ze_slownika(json.load(f))
        except (OSError, ValueError):
            return None


class Rozmowa:
    """Przebieg jednego drzewka dialogowego."""

    def __init__(self, stan, did):
        self.stan = stan
        self.did = did
        self.dane = D.DIALOGI[did]
        self.zdarzenia = []
        self.wezel_id = None
        self.przejdz(self.dane["start"])

    @property
    def wezel(self):
        return self.dane["wezly"][self.wezel_id]

    @property
    def zakonczona(self):
        return self.wezel_id == "koniec"

    def przejdz(self, wid):
        for _ in range(20):  # zabezpieczenie przed pętlą przekierowań
            if wid == "koniec":
                self.wezel_id = "koniec"
                return
            w = self.dane["wezly"][wid]
            przekierowanie = None
            for j in w.get("jesli", []):
                if self.stan.warunki(j["gdy"]):
                    przekierowanie = j["dalej"]
                    break
            if przekierowanie:
                wid = przekierowanie
                continue
            self.wezel_id = wid
            kto = w.get("kto")
            if kto in P.HISTORYCZNE:
                self.stan.efekt("poznaj:" + kto)
            self.zdarzenia.extend(self.stan.efekty(w.get("efekty")))
            return
        raise RuntimeError("Zapętlone przekierowania w dialogu " + self.did)

    def opcje(self):
        if self.zakonczona:
            return []
        return [o for o in self.wezel.get("opcje", []) if self.stan.warunki(o.get("gdy"))]

    def wybierz(self, i):
        o = self.opcje()[i]
        self.zdarzenia.extend(self.stan.efekty(o.get("efekty")))
        self.przejdz(o["dalej"])

    def dalej(self):
        """Dla węzła bez opcji: przejście dalej."""
        if self.opcje():
            return
        self.przejdz(self.wezel.get("dalej", "koniec"))

    def odbierz_zdarzenia(self):
        z, self.zdarzenia = self.zdarzenia, []
        return z


class Gra:
    """Fasada logiki: interakcje z hotspotami i wyniki minigier."""

    def __init__(self, stan=None):
        self.stan = stan or Stan()

    @property
    def lokacja(self):
        return R.LOKACJE[self.stan.lokacja]

    @property
    def rozdzial(self):
        return R.ROZDZIALY[self.stan.rozdzial]

    def hotspoty(self):
        return [h for h in self.lokacja["hotspoty"] if self.stan.warunki(h.get("widoczny"))]

    def hotspot(self, hid):
        for h in self.hotspoty():
            if h["id"] == hid:
                return h
        raise KeyError("Brak widocznego hotspotu %s w %s" % (hid, self.stan.lokacja))

    def _wykonaj(self, akcje):
        for a in akcje:
            if self.stan.warunki(a.get("gdy")):
                zd = []
                if a.get("mow"):
                    zd.append((Zdarzenie.MOW, a["mow"]))
                zd.extend(self.stan.efekty(a.get("efekty")))
                return zd
        return []

    def kliknij(self, hid):
        h = self.hotspot(hid)
        zd = self._wykonaj(h.get("akcje", []))
        if not zd:
            zd = [(Zdarzenie.MOW, h.get("patrz", "Nic ciekawego."))]
        return zd

    def patrz(self, hid):
        return self.hotspot(hid).get("patrz", "")

    def uzyj(self, przedmiot, hid):
        h = self.hotspot(hid)
        if przedmiot not in self.stan.ekwipunek:
            return [(Zdarzenie.MOW, "Nie mam tego przy sobie.")]
        akcje = h.get("uzyj", {}).get(przedmiot)
        if akcje:
            zd = self._wykonaj(akcje)
            if zd:
                return zd
        nazwa = R.PRZEDMIOTY[przedmiot]["nazwa"]
        return [(Zdarzenie.MOW, "%s i %s? To chyba nie tak." % (nazwa, h["nazwa"]))]

    def wygrana_minigry(self, gid):
        return self.stan.efekty(MD.WYGRANA[gid])

    def rozmowa(self, did):
        return Rozmowa(self.stan, did)
