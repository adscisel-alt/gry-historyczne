"""Stałe konfiguracyjne: rozdzielczość, paleta sepii, układ ekranu."""
import os
import sys

TYTUL = "Listopad 1918 — Pocztówki z niepodległości"
W, H = 1280, 720          # wewnętrzna rozdzielczość (skalowana do okna)
SCENA_H = 560             # wysokość obszaru lokacji
PANEL_Y = SCENA_H         # dolny panel: komunikaty + ekwipunek
FPS = 60

# Paleta sepii: od ciemnego brązu do kremowego papieru.
SEPIA_CIEMNA = (34, 23, 15)
SEPIA_JASNA = (243, 230, 202)


def sep(v):
    """Ton sepii dla jasności v (0–255). Zawsze r >= g >= b."""
    v = max(0, min(255, int(v)))
    t = v / 255.0
    return tuple(int(a + (b - a) * t) for a, b in zip(SEPIA_CIEMNA, SEPIA_JASNA))


def sepa(v, alpha):
    return sep(v) + (int(alpha),)


PAPIER = sep(225)
PAPIER_CIEMNY = sep(190)
ATRAMENT = sep(25)
ATRAMENT_JASNY = sep(80)
CZERWIEN_STEMPLA = (150, 52, 38)     # jedyny „kolor” poza sepią: stemple
FIOLET = (112, 62, 150)              # kaptur Damiana Ściseła — archiwisty spoza czasu
FIOLET_JASNY = (160, 112, 196)


def zasob(*czesci):
    """Ścieżka do zasobów — działa także po spakowaniu PyInstallerem."""
    baza = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(baza, *czesci)


def katalog_zapisu():
    baza = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".config")
    sciezka = os.path.join(baza, "Listopad1918")
    try:
        os.makedirs(sciezka, exist_ok=True)
    except OSError:
        sciezka = os.path.abspath(".")
    return sciezka
