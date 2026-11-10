"""Mapy basenu Morza Śródziemnego (753 p.n.e. – 500 n.e.) do animowanych map imperium między rozdziałami.

Źródło granic: projekt „historical-basemaps” (A. Ourednik), licencja GPL-3.0:
https://github.com/aourednik/historical-basemaps — plik licencji kopiowany jest do godot/dane/.
Skrypt przycina mapy do basenu Morza Śródziemnego, upraszcza kształty i zapisuje godot/dane/mapa_imperium.json.

Uruchom:  pip install shapely && python narzedzia/eksportuj_mape.py
"""
import json
import math
import os
import urllib.request

from shapely.geometry import Polygon, box, shape
from shapely.validation import make_valid

TU = os.path.dirname(os.path.abspath(__file__))
CEL = os.path.join(TU, "..", "godot", "dane")
BUILD = os.path.join(TU, "..", "build")
BAZA = "https://raw.githubusercontent.com/aourednik/historical-basemaps/master/"
LON0, LON1, LAT0, LAT1 = -11.0, 46.0, 27.5, 56.5
KOS = math.cos(math.radians(42))
W = (LON1 - LON0) * KOS
H = LAT1 - LAT0

# epoka mapy -> plik historical-basemaps
EPOKI = {"-700": "bc700", "-400": "bc400", "-200": "bc200", "-100": "bc100", "-1": "bc1",
         "100": "100", "200": "200", "300": "300", "400": "400", "500": "500"}

POLSKIE = {
    "Rome": "Rzym", "Roman Republic": "Republika Rzymska", "Roman Empire": "Cesarstwo Rzymskie",
    "Rome (Maximian)": "Rzym (Maksymian)", "Rome (Diocletianus)": "Rzym (Dioklecjan)",
    "Rome (Constantinus)": "Rzym (Konstancjusz)", "Rome (Galerius)": "Rzym (Galeriusz)",
    "Western Roman Empire": "Cesarstwo Zachodnie", "Eastern Roman Empire": "Cesarstwo Wschodnie",
    "Carthaginian Empire": "Kartagina", "Carthage": "Kartagina", "Achaemenid Empire": "Persja",
    "Persia": "Persja", "Sasanian Empire": "Persja Sasanidów", "Parthian Empire": "Partia",
    "Seleucid Kingdom": "Państwo Seleucydów", "Ptolemaic Kingdom": "Egipt Ptolemeuszy",
    "Macedon and Hellenic League": "Macedonia", "Greek city-states": "Grecy", "Greek colonies": "Grecy",
    "Celts": "Celtowie", "Hallstatt culture": "Celtowie", "Urnfield cultures": "ludy Italii i Europy",
    "Scythians": "Scytowie", "Sarmates": "Sarmaci", "Dacians": "Dakowie", "Dacia": "Dacja",
    "Numidia": "Numidia", "Mauretania": "Mauretania", "Kingdom of Syphax": "Numidia",
    "Hunnic Empire": "Hunowie", "Visigoths": "Wizygoci", "Ostrogoths": "Ostrogoci", "Vandals": "Wandalowie",
    "Franks": "Frankowie", "Burgundians": "Burgundowie", "Saxons": "Sasi", "Suebi": "Swebowie",
    "Anglo-Saxons": "Anglosasi", "Alans": "Alanowie", "Armenia": "Armenia", "Thrace": "Tracja",
    "Illyrians": "Ilirowie", "Berbers": "Berberowie", "Celtiberians": "Celtyberowie", "Assyria": "Asyria",
    "Arabs": "Arabowie", "Nabatean Kingdom": "Nabatejczycy", "Bosporan Kingdom": "Królestwo Bosporańskie",
    "Odrysian Kingdom": "Tracja", "Judea": "Judea", "Phrygians": "Frygowie", "Urartu": "Urartu",
}
POKAZ_NAZWE = {"Rzym", "Republika Rzymska", "Cesarstwo Rzymskie", "Cesarstwo Zachodnie", "Cesarstwo Wschodnie",
               "Kartagina", "Persja", "Persja Sasanidów", "Partia", "Państwo Seleucydów", "Egipt Ptolemeuszy",
               "Macedonia", "Celtowie", "Dakowie", "Dacja", "Numidia", "Hunowie", "Wizygoci", "Ostrogoci",
               "Wandalowie", "Frankowie", "Sarmaci", "Scytowie", "Rzym (Maksymian)", "Rzym (Dioklecjan)",
               "Rzym (Konstancjusz)", "Rzym (Galeriusz)", "Grecy", "Tracja", "Mauretania", "Berberowie"}

# ręcznie ustawione podpisy (lon, lat), żeby nie zasłaniały miast
ETYKIETY = {"Roman Empire": (24.0, 44.5), "Western Roman Empire": (4.0, 45.0), "Eastern Roman Empire": (29.0, 39.0),
            "Roman Republic": (14.0, 44.2), "Carthaginian Empire": (4.5, 35.5), "Rome": (13.5, 43.5)}

MIASTA = {
    "Rzym": (12.49, 41.89), "Kartagina": (10.32, 36.85), "Kanny": (16.13, 41.31), "Zama": (9.3, 36.1),
    "Alezja": (4.5, 47.54), "Rubikon": (12.4, 44.06), "Bizancjum": (28.97, 41.01),
    "Konstantynopol": (28.97, 41.01), "Ateny": (23.73, 37.98), "Aleksandria": (29.92, 31.2),
    "Londinium": (-0.1, 51.51), "Lutecja": (2.35, 48.86), "Mediolan": (9.19, 45.46), "Rawenna": (12.2, 44.42),
    "Sarmizegetusa": (23.31, 45.62), "Las Teutoburski": (8.13, 52.41), "Pola Katalaunijskie": (4.36, 48.96),
    "Syrakuzy": (15.29, 37.08), "Nowa Kartagina": (-0.98, 37.6), "Massalia": (5.37, 43.3),
    "Akcjum": (20.77, 38.95), "Jerozolima": (35.21, 31.77), "Antiochia": (36.16, 36.2), "Kalisia": (18.09, 51.76),
    "Carnuntum": (16.86, 48.11), "Akwileja": (13.37, 45.77), "Saguntum": (-0.27, 39.68), "Troja": (26.24, 39.96),
    "Weje": (12.39, 42.02), "Alba Longa": (12.66, 41.75), "Brundyzjum": (17.94, 40.64), "Kapua": (14.25, 41.08),
    "Neapol": (14.25, 40.85), "Tarent": (17.24, 40.47), "Farsalos": (22.38, 39.3), "Most Mulwijski": (12.47, 41.94),
    "Trewir": (6.64, 49.75), "Eburacum": (-1.08, 53.96), "Ktezyfon": (44.58, 33.09), "Hippona": (7.75, 36.88),
}


def rzut(lon, lat):
    return [round((lon - LON0) * KOS / W, 4), round((LAT1 - lat) / H, 4)]


def wielokaty(g):
    g = make_valid(g)
    if g.geom_type == "Polygon":
        return [g]
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"] + \
        [q for p in getattr(g, "geoms", []) if p.geom_type == "MultiPolygon" for q in p.geoms]


def epoka(plik):
    sciezka = os.path.join(BUILD, "world_%s.geojson" % plik)
    os.makedirs(BUILD, exist_ok=True)
    if not os.path.exists(sciezka):
        urllib.request.urlretrieve(BAZA + "geojson/world_%s.geojson" % plik, sciezka)
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
        rzymski = "Rom" in nazwa
        for p in wielokaty(g):
            p = p.simplify(0.05 if not rzymski else 0.02, preserve_topology=True)
            if p.is_empty or (p.area < 0.04 and not rzymski) or p.area < 0.0005:
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
        if pl in POKAZ_NAZWE and najw is not None and pl not in widziane and (najw.area > 1.5 or rzymski):
            widziane.add(pl)
            rp = najw.representative_point()
            etyk = rzut(*ETYKIETY.get(nazwa, (rp.x, rp.y)))
        kraje.append({"n": nazwa, "pl": pl, "czesci": czesci, "etykieta": etyk,
                      "rzym": 2 if nazwa == "Eastern Roman Empire" else (1 if rzymski else 0)})
    return kraje


def main():
    os.makedirs(CEL, exist_ok=True)
    wynik = {"proporcja": round(W / H, 4), "epoki": {}, "miasta": {k: rzut(*v) for k, v in MIASTA.items()},
             "zrodlo": "Granice: historical-basemaps (A. Ourednik), licencja GPL-3.0, uproszczone"}
    for klucz, plik in EPOKI.items():
        wynik["epoki"][klucz] = epoka(plik)
    with open(os.path.join(CEL, "mapa_imperium.json"), "w", encoding="utf-8") as f:
        json.dump(wynik, f, ensure_ascii=False, separators=(",", ":"))
    lic = os.path.join(BUILD, "LICENSE-historical-basemaps.txt")
    if not os.path.exists(lic):
        urllib.request.urlretrieve(BAZA + "LICENSE", lic)
    with open(lic, encoding="utf-8") as zr, open(os.path.join(CEL, "LICENSE-mapa-imperium-GPL3.txt"), "w",
                                                 encoding="utf-8") as do:
        do.write("Dane granic w mapa_imperium.json pochodzą z projektu historical-basemaps\n"
                 "(https://github.com/aourednik/historical-basemaps) i są udostępniane na licencji GPL-3.0.\n\n")
        do.write(zr.read())
    pkt = sum(len(c) for e in wynik["epoki"].values() for k in e for c in k["czesci"])
    rozm = os.path.getsize(os.path.join(CEL, "mapa_imperium.json")) // 1024
    print("Zapisano mapa_imperium.json:", len(wynik["epoki"]), "epok,", pkt, "punktów,", rozm, "KB")


if __name__ == "__main__":
    main()
