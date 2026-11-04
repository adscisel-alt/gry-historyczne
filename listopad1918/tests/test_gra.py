"""Testy automatyczne gry „Listopad 1918”.

Uruchomienie:  python -m pytest -q tests      (albo: python tests/test_gra.py)
Testy działają bez okna (SDL_VIDEODRIVER=dummy).
"""
import os
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from gra import automat  # noqa: E402
from gra.stan import Gra, Stan, Zdarzenie  # noqa: E402
from gra.dane import rozdzialy as R, dialogi as D, postacie as P, fakty as F, minigry_dane as MD  # noqa: E402

pygame.init()
pygame.display.set_mode((1280, 720))

PRZYKLADOWE_WARUNKI = ("flag:", "!flag:", "ma:", "!ma:", "fakt:", "!fakt:", "napiecie>=")
EFEKTY = ("flag", "unflag", "daj", "zabierz", "fakt", "mit", "poznaj", "idz", "dialog", "minigra", "damian", "napiecie", "koniec_rozdzialu")


# ====================================================================== dane
def test_liczby_tresci():
    assert len(R.ROZDZIALY) == 7
    assert len(R.LOKACJE) == 14
    assert len(P.HISTORYCZNE) == 12
    assert len(F.MITY) == 10
    assert len(MD.WYGRANA) == 8
    for r in R.ROZDZIALY:
        lok = [l for l in R.LOKACJE.values() if l["rozdzial"] == r["id"]]
        assert len(lok) == 2, r["id"]
        assert r["start"] in R.LOKACJE


def test_biogramy_kompletne():
    for pid, p in P.HISTORYCZNE.items():
        for pole in ("imie", "lata", "rola", "biogram", "wklad", "wyglad"):
            assert p.get(pole), (pid, pole)
        assert len(p["biogram"]) > 150, pid
    assert "fikcyjna" in P.FIKCYJNE["janek"]["rola"]


def test_fakty_maja_daty_i_zrodla():
    for fid, f in F.FAKTY.items():
        assert f["data"] and f["tekst"] and f["zrodlo"], fid
    for mid, m in F.MITY.items():
        assert len(m["opcje"]) == 3 and 0 <= m["dobra"] < 3, mid
        assert m["fakt"] is None or m["fakt"] in F.FAKTY, mid


def _sprawdz_efekty(lista, ctx):
    for e in lista or []:
        rodzaj, _, arg = e.partition(":")
        assert rodzaj in EFEKTY, (ctx, e)
        if rodzaj in ("daj", "zabierz"):
            assert arg in R.PRZEDMIOTY, (ctx, e)
        elif rodzaj == "fakt":
            assert arg in F.FAKTY, (ctx, e)
        elif rodzaj == "mit":
            assert arg in F.MITY, (ctx, e)
        elif rodzaj == "idz":
            assert arg in R.LOKACJE, (ctx, e)
        elif rodzaj == "dialog":
            assert arg in D.DIALOGI, (ctx, e)
        elif rodzaj == "minigra":
            assert arg in MD.WYGRANA, (ctx, e)


def _sprawdz_warunki(lista, ctx):
    for w in lista or []:
        assert w.startswith(PRZYKLADOWE_WARUNKI), (ctx, w)
        if w.lstrip("!").startswith("ma:"):
            assert w.split(":")[1] in R.PRZEDMIOTY, (ctx, w)


def test_spojnosc_lokacji_i_hotspotow():
    for lid, l in R.LOKACJE.items():
        ids = [h["id"] for h in l["hotspoty"]]
        assert len(ids) == len(set(ids)), lid
        for h in l["hotspoty"]:
            ctx = "%s/%s" % (lid, h["id"])
            assert "rect" in h or "postac" in h, ctx
            if "postac" in h:
                assert h["postac"] in P.wszystkie(), ctx
            if "rect" in h:
                x, y, w, hh = h["rect"]
                assert 0 <= x and x + w <= 1280 and 0 <= y and y + hh <= 560, ctx
            _sprawdz_warunki(h.get("widoczny"), ctx)
            for a in h.get("akcje", []) + [a for lst in h.get("uzyj", {}).values() for a in lst]:
                _sprawdz_warunki(a.get("gdy"), ctx)
                _sprawdz_efekty(a.get("efekty"), ctx)
            for p in h.get("uzyj", {}):
                assert p in R.PRZEDMIOTY, ctx


def test_spojnosc_dialogow():
    for did, d in D.DIALOGI.items():
        w = d["wezly"]
        assert d["start"] in w, did
        for nid, n in w.items():
            ctx = "%s/%s" % (did, nid)
            assert n["kto"] in P.wszystkie(), ctx
            _sprawdz_efekty(n.get("efekty"), ctx)
            cele = [o["dalej"] for o in n.get("opcje", [])] + [n.get("dalej", "koniec")] + [j["dalej"] for j in n.get("jesli", [])]
            for c in cele:
                assert c == "koniec" or c in w, (ctx, c)
            for o in n.get("opcje", []):
                _sprawdz_efekty(o.get("efekty"), ctx)
                _sprawdz_warunki(o.get("gdy"), ctx)


def test_wszystkie_postacie_historyczne_wystepuja():
    w_grze = {h["postac"] for l in R.LOKACJE.values() for h in l["hotspoty"] if "postac" in h}
    w_dialogach = {n["kto"] for d in D.DIALOGI.values() for n in d["wezly"].values()}
    assert set(P.HISTORYCZNE) <= (w_grze | w_dialogach)


def test_mapa_zaborow_miasta_w_swoich_zaborach():
    for nazwa, ((lon, lat), zabor) in F.MIASTA.items():
        trafienia = [k for k, z in F.ZABORY.items() if F.punkt_w_wielokacie(lon, lat, z["punkty"])]
        assert trafienia == [zabor], (nazwa, trafienia)


# ====================================================================== zagadki
def test_zagadka_koszar_ma_jedno_rozwiazanie():
    import itertools
    poprawne = [p for p in itertools.permutations(MD.KOSZARY_PUNKTY) if not MD.sprawdz_koszary(list(p))]
    assert poprawne == [tuple(MD.KOSZARY_ROZWIAZANIE)]


def test_manifest_i_przepustki():
    sekcje = [i for _, i in MD.MANIFEST_FRAGMENTY if i is not None]
    assert sorted(sekcje) == list(range(len(MD.MANIFEST_SEKCJE)))
    assert sum(1 for _, i in MD.MANIFEST_FRAGMENTY if i is None) == 2
    wazne = [MD.przepustka_wazna(d) for d in MD.PRZEPUSTKI]
    assert 2 <= sum(wazne) <= len(wazne) - 2
    for d in MD.PRZEPUSTKI:
        assert MD.przepustka_wazna(d) == (MD.powod_odrzucenia(d) == "")


def test_dyplomacja_wygrywalna_i_przegrywalna():
    _, najl = automat.symuluj_najlepsza_dyplomacje()
    assert MD.dyplomacja_wygrana(najl)
    najgorsze = [min(range(3), key=lambda i: sum(r["odpowiedzi"][i][1].values())) for r in MD.DYPLOMACJA_RUNDY]
    assert not MD.dyplomacja_wygrana(MD.symuluj_dyplomacje(najgorsze))


# ====================================================================== logika
def test_przejscie_calej_gry_logika():
    gra, log = automat.przejdz_gre()
    assert gra.stan.ukonczona, log[-10:]
    assert set(gra.stan.fakty) == set(F.FAKTY)
    assert set(gra.stan.mity) == set(F.MITY)
    assert set(gra.stan.poznani) == set(P.HISTORYCZNE)
    for r in R.ROZDZIALY:
        assert "ukonczono_" + r["id"] in gra.stan.flagi


def test_napiecie_i_przewijanie_rozbrajania():
    st = Stan()
    g = Gra(st)
    r = g.rozmowa("d_otto")
    r.wybierz(1)                    # krzyk
    r.wybierz(1)                    # jeszcze głośniej -> przewinięcie
    assert r.wezel["kto"] == "damian"
    assert st.napiecie == 0
    r.dalej()
    assert r.wezel_id == "a"


def test_zapis_i_odczyt():
    gra, _ = automat.przejdz_gre()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "z.json")
        gra.stan.zapisz(p)
        st = Stan.wczytaj(p)
    assert st.fakty == gra.stan.fakty and st.ukonczona


# ====================================================================== grafika
def test_tla_w_sepii():
    from gra import grafika as G
    for klucz in G.TLA:
        s = G.tlo(klucz)
        assert s.get_size() == (1280, 560)
        for x in range(40, 1240, 97):
            for y in range(40, 520, 61):
                r, g, b, *_ = s.get_at((x, y))
                assert r >= g >= b, (klucz, x, y, (r, g, b))


def test_sylwetki_ikony_portrety():
    from gra import grafika as G
    for pid in P.wszystkie():
        assert G.sylwetka(pid).get_height() > 150
        assert G.portret(pid, 100).get_width() == 100
    for p in list(R.PRZEDMIOTY) + ["gazeta"]:
        assert G.ikona(p).get_width() > 40


# ====================================================================== pełne przejście przez UI
def _klik(app, poz=(640, 360)):
    e1 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=poz, button=1)
    app.klatka(0.5, [e1])


def _rozwiaz_minigre(app, mg):
    from gra.minigry import (MapaZaborow, Manifest, Przepustki, KolejnoscKoszar, Swiadkowie, Dyplomacja,
                             PrawaKobiet, Wklady)
    if isinstance(mg, MapaZaborow):
        assert not mg.umiesc("Kraków", "pruski")
        for m in list(mg.miasta):
            mg.umiesc(m, F.MIASTA[m][1])
    elif isinstance(mg, Manifest):
        assert not mg.sprawdz()
        for f, (_, sek) in enumerate(MD.MANIFEST_FRAGMENTY):
            if sek is None:
                mg.spal(f)
            else:
                mg.poloz(f, sek)
        assert mg.sprawdz()
    elif isinstance(mg, Przepustki):
        for d in MD.PRZEPUSTKI:
            mg.decyzja(MD.przepustka_wazna(d))
    elif isinstance(mg, KolejnoscKoszar):
        for p in reversed(MD.KOSZARY_PUNKTY):
            mg.dodaj(p)
        assert not mg.sprawdz() and mg.napiecie == 1
        mg.plan = []
        for p in MD.KOSZARY_ROZWIAZANIE:
            mg.dodaj(p)
        mg.sprawdz()
    elif isinstance(mg, Swiadkowie):
        for runda in MD.SWIADKOWIE_RUNDY:
            assert mg.wskaz(runda["falszywe"])
            assert mg.pokaz_dowod(runda["dowod"])
            mg.nastepna()
    elif isinstance(mg, Dyplomacja):
        wybory, _ = automat.symuluj_najlepsza_dyplomacje()
        for w in wybory:
            mg.odpowiedz(w)
    elif isinstance(mg, PrawaKobiet):
        for _, _, dobra in MD.QUIZ_KOBIET:
            mg.odpowiedz(dobra)
    elif isinstance(mg, Wklady):
        for o, w in MD.WKLADY:
            mg.polacz(o, w)
    app.klatka(0.1)
    assert mg.wygrana, type(mg).__name__
    app.klatka(1.0)
    _klik(app)


def test_pelne_przejscie_przez_interfejs():
    """Gra przechodzona przez prawdziwe sceny: karty, lokacje, dialogi, minigry, mity, dziennik."""
    from gra.aplikacja import Aplikacja
    from gra import sceny
    from gra.minigry.baza import Minigra

    with tempfile.TemporaryDirectory() as d:
        app = Aplikacja(okno=False, sciezka_zapisu=os.path.join(d, "zapis.json"))
        app.klatka(0.1)
        app.nowa_gra()
        odwiedzone_lokacje = set()
        minigry = set()
        kroki = list(automat.SOLUCJA)
        for _ in range(3000):
            app.klatka(0.6)
            top = app.gora
            if isinstance(top, sceny.Zakonczenie):
                break
            if isinstance(top, (sceny.KartaRozdzialu, sceny.DamianScena, sceny.Podsumowanie)):
                _klik(app)
            elif isinstance(top, sceny.MitScena):
                top.wybierz(top.mit["dobra"])
                app.klatka(0.5)
                _klik(app)
            elif isinstance(top, sceny.RozmowaScena):
                r = top.rozmowa
                opcje = r.opcje()
                top.t_tekst = 999
                odw = getattr(top, "_odw", set())
                odw.add(r.wezel_id)
                top._odw = odw
                if opcje:
                    wybor = next((i for i, o in enumerate(opcje) if o["dalej"] not in odw), len(opcje) - 1)
                    top.wybierz(wybor)
                else:
                    top.dalej()
            elif isinstance(top, Minigra):
                minigry.add(top.gid)
                _rozwiaz_minigre(app, top)
            elif isinstance(top, sceny.Lokacja):
                odwiedzone_lokacje.add(top.lid)
                if not kroki:
                    break
                krok = kroki.pop(0)
                if krok[0] == "klik":
                    top.aktywuj(krok[1])
                else:
                    top.aktywuj(krok[2], przedmiot=krok[1])
                # sprawdzamy też dziennik w trakcie gry
                if len(kroki) % 17 == 0:
                    app.otworz_dziennik()
                    dz = app.gora
                    for z in range(len(sceny.Dziennik.ZAKLADKI)):
                        dz.zakladka = z
                        app.klatka(0.1)
                    dz.zamknij()
        assert isinstance(app.gora, sceny.Zakonczenie), type(app.gora)
        assert app.gra.stan.ukonczona
        assert odwiedzone_lokacje == set(R.LOKACJE)
        assert minigry == set(MD.WYGRANA)
        assert os.path.exists(app.sciezka_zapisu)
        app.otworz_dziennik()
        app.klatka(0.1)


def test_menu_kontynuuj():
    from gra.aplikacja import Aplikacja
    from gra import sceny
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "zapis.json")
        st = Stan()
        st.rozdzial = 3
        st.lokacja = "wagon"
        st.zapisz(p)
        app = Aplikacja(okno=False, sciezka_zapisu=p)
        app.ustaw_baze(sceny.Menu(app))
        app.klatka(0.1)
        app.kontynuuj()
        app.klatka(1.0)
        _klik(app)
        assert isinstance(app.gora, sceny.Lokacja) and app.gora.lid == "wagon"
        # klik myszą w hotspot -> Janek idzie i wykonuje akcję
        lok = app.gora
        h = lok.app.gra.hotspot("okno_wagon")
        _klik(app, lok.rect_hotspotu(h).center)
        for _ in range(20):
            app.klatka(0.1)
        assert "magdeburg" in app.gra.stan.fakty


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
