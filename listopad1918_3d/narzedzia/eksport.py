"""Eksport treści i grafik z wersji 2D (listopad1918/) do projektu Godot 3D.

Jedno źródło prawdy: fabuła, dialogi, fakty i mity są w listopad1918/gra/dane.
Uruchom po każdej zmianie treści:  python narzedzia/eksport.py
"""
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
TUTAJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(TUTAJ), "listopad1918"))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from gra import grafika as G  # noqa: E402
from gra import automat  # noqa: E402
from gra.config import sep  # noqa: E402
from gra.dane import rozdzialy as R, dialogi as D, postacie as P, fakty as F, minigry_dane as MD  # noqa: E402

SKALA = 1.6  # rozdzielczość wycinanek


def zapisz_png(s, *sciezka):
    p = os.path.join(TUTAJ, "zasoby", *sciezka)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    pygame.image.save(s, p)


def main():
    meta = {}
    for pid in P.wszystkie():
        syl = G.sylwetka(pid, SKALA)
        zapisz_png(syl, "postacie", pid + ".png")
        zapisz_png(G.portret(pid, 200), "portrety", pid + ".png")
        h_fig = int(300 * P.wszystkie()[pid]["wyglad"].get("wzrost", 1.0) * SKALA)
        # stopy: na dole figury (top 40 + h - 4) + margines wycinanki
        pad = syl.get_height() - (h_fig + 40)
        meta[pid] = {"w": syl.get_width(), "h": syl.get_height(), "stopa_px": syl.get_height() - (pad // 2 + 36 + h_fig),
                     "wzrost_px": h_fig}
    for p in list(R.PRZEDMIOTY) + ["gazeta"]:
        zapisz_png(G.ikona(p, 96), "ikony", p + ".png")
    zapisz_png(G.papier(512, 512, 226, seed=3), "ui", "papier.png")
    zapisz_png(G.papier(512, 512, 200, seed=8), "ui", "papier_ciemny.png")
    s = pygame.Surface((1024, 640))
    G.mapa(s, (0, 0, 1024, 640), 222)
    zapisz_png(s, "ui", "mapa.png")
    s = pygame.Surface((256, 160), pygame.SRCALPHA)
    G.strzalka_wyjscia(s, (0, 0, 256, 160), 0.0)
    zapisz_png(s, "ui", "wyjscie.png")
    s = pygame.Surface((520, 600), pygame.SRCALPHA)
    G.ramka_sztalugi(s, (0, 0, 520, 600))
    zapisz_png(s, "ui", "sztaluga.png")

    dane = {
        "rozdzialy": R.ROZDZIALY,
        "lokacje": R.LOKACJE,
        "przedmioty": R.PRZEDMIOTY,
        "dialogi": D.DIALOGI,
        "postacie": P.wszystkie(),
        "historyczne": list(P.HISTORYCZNE),
        "fakty": F.FAKTY,
        "mity": F.MITY,
        "prawa_kobiet": F.PRAWA_KOBIET,
        "zabory": F.ZABORY,
        "miasta": F.MIASTA,
        "minigry": {
            "wygrana": MD.WYGRANA,
            "manifest_sekcje": MD.MANIFEST_SEKCJE,
            "manifest_fragmenty": MD.MANIFEST_FRAGMENTY,
            "koszary_punkty": MD.KOSZARY_PUNKTY,
            "koszary_wskazowki": MD.KOSZARY_WSKAZOWKI,
            "koszary_rozwiazanie": MD.KOSZARY_ROZWIAZANIE,
            "lista_powitalna": MD.LISTA_POWITALNA,
            "zasady_przepustek": MD.ZASADY_PRZEPUSTEK,
            "przepustki": MD.PRZEPUSTKI,
            "przepustki_prog": MD.PRZEPUSTKI_PROG,
            "swiadkowie": MD.SWIADKOWIE_RUNDY,
            "panstwa": MD.PANSTWA,
            "dyplomacja_start": MD.DYPLOMACJA_START,
            "dyplomacja_prog": MD.DYPLOMACJA_PROG,
            "dyplomacja_rundy": MD.DYPLOMACJA_RUNDY,
            "quiz_kobiet": MD.QUIZ_KOBIET,
            "quiz_kobiet_prog": MD.QUIZ_KOBIET_PROG,
            "wklady": MD.WKLADY,
        },
        "solucja": automat.SOLUCJA,
        "grafika": {"skala_postaci": SKALA, "postacie": meta},
    }
    with open(os.path.join(TUTAJ, "dane", "gra.json"), "w", encoding="utf-8") as f:
        json.dump(dane, f, ensure_ascii=False, indent=1)
    print("Wyeksportowano: dane/gra.json, %d postaci, %d ikon." % (len(meta), len(R.PRZEDMIOTY) + 1))


if __name__ == "__main__":
    main()
