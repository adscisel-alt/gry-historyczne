"""Mapa Europy 1914 i 1920 dla animowanej podróży między kampaniami.

Źródło granic: projekt „historical-basemaps” (A. Ourednik), licencja GPL-3.0:
https://github.com/aourednik/historical-basemaps — plik licencji kopiowany jest do godot/dane/.
Skrypt przycina mapy do Europy, upraszcza kształty i zapisuje godot/dane/mapa_europy.json.

Uruchom:  pip install shapely && python narzedzia/eksportuj_mape_europy.py
"""
import json
import math
import os
import urllib.request

from shapely.geometry import Polygon, box, shape
from shapely.validation import make_valid

TU = os.path.dirname(os.path.abspath(__file__))
CEL = os.path.join(TU, "..", "godot", "dane")
BAZA = "https://raw.githubusercontent.com/aourednik/historical-basemaps/master/"
LON0, LON1, LAT0, LAT1 = -10.5, 40.0, 40.0, 61.0
KOS = math.cos(math.radians(51))
W = (LON1 - LON0) * KOS
H = LAT1 - LAT0

POLSKIE = {
    "German Empire": "Cesarstwo Niemieckie", "Austro-Hungarian Empire": "Austro-Węgry",
    "Russian Empire": "Imperium Rosyjskie", "France": "Francja", "Switzerland": "Szwajcaria",
    "United Kingdom of Great Britain and Ireland": "Wielka Brytania", "Kingdom of Italy": "Włochy",
    "Italy": "Włochy", "Spain": "Hiszpania", "Sweden": "Szwecja", "Norway": "Norwegia", "Poland": "Polska",
    "Germany": "Niemcy", "Czechoslovakia": "Czechosłowacja", "Austria": "Austria", "Hungary": "Węgry",
    "Romania": "Rumunia", "Lithuania": "Litwa", "Latvia": "Łotwa", "Estonia": "Estonia", "Finland": "Finlandia",
    "Grand Duchy of Finland": "Finlandia", "USSR": "Rosja Radziecka", "Yugoslavia": "Jugosławia",
    "Denmark": "Dania", "Netherlands": "Holandia", "Belgium": "Belgia", "Ottoman Empire": "Turcja",
    "Ottoman Sultanate": "Turcja", "Bulgaria": "Bułgaria", "Greece": "Grecja", "Serbia": "Serbia",
    "Portugal": "Portugalia", "East Prussia": "Prusy Wschodnie (Niemcy)", "Ukraine": "Ukraina",
    "White Russia": "Białoruś",
}
POKAZ_NAZWE = {"Cesarstwo Niemieckie", "Austro-Węgry", "Imperium Rosyjskie", "Francja", "Wielka Brytania",
               "Włochy", "Polska", "Niemcy", "Czechosłowacja", "Hiszpania", "Szwecja", "Rumunia",
               "Rosja Radziecka", "Litwa", "Austria", "Węgry", "Jugosławia", "Norwegia", "Finlandia", "Turcja"}

# ręcznie ustawione miejsca podpisów, żeby nie zasłaniały miast
ETYKIETY = {"Poland": (19.2, 51.15), "Russian Empire": (33.0, 56.0), "German Empire": (10.6, 51.4),
            "USSR": (34.0, 56.5), "Austro-Hungarian Empire": (19.5, 47.6)}

MIASTA = {"Warszawa": (21.01, 52.23), "Londyn": (-0.13, 51.51), "Lozanna": (6.63, 46.52), "Paryż": (2.35, 48.86),
          "Piotrogród": (30.31, 59.94), "Sztokholm": (18.07, 59.33), "Poznań": (16.93, 52.41),
          "Gdańsk": (18.65, 54.35), "Kraków": (19.94, 50.06), "Berlin": (13.40, 52.52), "Wiedeń": (16.37, 48.21),
          "Wersal": (2.13, 48.80), "Bergen": (5.32, 60.39)}


def rzut(lon, lat):
    return [round((lon - LON0) * KOS / W, 4), round((LAT1 - lat) / H, 4)]


def wielokaty(g):
    g = make_valid(g)
    if g.geom_type == "Polygon":
        return [g]
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"] + \
        [q for p in getattr(g, "geoms", []) if p.geom_type == "MultiPolygon" for q in p.geoms]


def epoka(rok):
    sciezka = os.path.join(TU, "..", "build", "world_%d.geojson" % rok)
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    if not os.path.exists(sciezka):
        urllib.request.urlretrieve(BAZA + "geojson/world_%d.geojson" % rok, sciezka)
    d = json.load(open(sciezka, encoding="utf-8"))
    ramka = box(LON0 - 1, LAT0 - 1, LON1 + 1, LAT1 + 1)
    kraje = []
    widziane = set()
    cechy = sorted(d["features"], key=lambda f: -make_valid(shape(f["geometry"])).area)
    for f in cechy:
        nazwa = f["properties"].get("NAME") or ""
        try:
            g = make_valid(shape(f["geometry"])).intersection(ramka)
        except Exception:
            continue
        if g.is_empty:
            continue
        czesci = []
        najw = None
        for p in wielokaty(g):
            p = p.simplify(0.06, preserve_topology=True)
            if p.is_empty or p.area < 0.04:
                continue
            ring = list(p.exterior.coords)[:-1]
            if len(ring) < 3 or not Polygon(ring).is_valid:
                continue
            czesci.append([rzut(x, y) for x, y in ring])
            if najw is None or p.area > najw.area:
                najw = p
        if not czesci:
            continue
        pl = POLSKIE.get(nazwa, nazwa)
        etyk = None
        if pl in POKAZ_NAZWE and najw is not None and pl not in widziane:
            widziane.add(pl)
            rp = najw.representative_point()
            etyk = rzut(*ETYKIETY.get(nazwa, (rp.x, rp.y)))
        kraje.append({"n": nazwa, "pl": pl, "czesci": czesci, "etykieta": etyk})
    return kraje


def main():
    os.makedirs(CEL, exist_ok=True)
    wynik = {"proporcja": round(W / H, 4), "1914": epoka(1914), "1920": epoka(1920),
             "miasta": {k: rzut(*v) for k, v in MIASTA.items()},
             "zrodlo": "Granice: historical-basemaps (A. Ourednik), licencja GPL-3.0, uproszczone"}
    with open(os.path.join(CEL, "mapa_europy.json"), "w", encoding="utf-8") as f:
        json.dump(wynik, f, ensure_ascii=False, separators=(",", ":"))
    lic = os.path.join(TU, "..", "build", "LICENSE-historical-basemaps.txt")
    if not os.path.exists(lic):
        urllib.request.urlretrieve(BAZA + "LICENSE", lic)
    with open(lic, encoding="utf-8") as zr, open(os.path.join(CEL, "LICENSE-mapa-europy-GPL3.txt"), "w",
                                                 encoding="utf-8") as do:
        do.write("Dane granic w mapa_europy.json pochodzą z projektu historical-basemaps\n"
                 "(https://github.com/aourednik/historical-basemaps) i są udostępniane na licencji GPL-3.0.\n\n")
        do.write(zr.read())
    pkt = sum(len(c) for e in ("1914", "1920") for k in wynik[e] for c in k["czesci"])
    print("Zapisano mapa_europy.json:", len(wynik["1914"]), "+", len(wynik["1920"]), "krajów,", pkt, "punktów")


if __name__ == "__main__":
    main()
