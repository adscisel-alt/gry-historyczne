"""Eksportuje treść gry (zamosc/dane.py) do godot/dane/dane.json.

Wersja 2D i 3D korzystają z tej samej fabuły, zagadek i Księgi Wiedzy.
Uruchom:  python zamosc3d/narzedzia/eksportuj_dane.py
"""
import json
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TU, "..", "..", "zamosc"))
import dane as D  # noqa: E402


def klucz(k):
    return "%s:%d" % k


wynik = dict(
    mapa_w=D.MAPA_W, mapa_h=D.MAPA_H,
    mapa=["".join(w) for w in D.zbuduj_mape()],
    bastiony=D.BASTIONY, dzialki=D.DZIALKI, bramy=D.BRAMY, rynek=D.RYNEK, start=D.START,
    npc=D.NPC, budynki=D.BUDYNKI, dostepne={str(k): v for k, v in D.DOSTEPNE.items()},
    zasoby_nazwy=D.ZASOBY_NAZWY, przedmioty=D.PRZEDMIOTY,
    wiedza={k: list(v) for k, v in D.WIEDZA.items()}, wiedza_kolejnosc=list(D.WIEDZA),
    karty_startowe=D.KARTY_STARTOWE, karta_budynku=D.KARTA_BUDYNKU, rangi=D.RANGI,
    quiz_glowny={klucz(k): v for k, v in D.QUIZ_GLOWNY.items()}, zagadki=D.ZAGADKI,
    rozdzialy={str(k): v for k, v in D.ROZDZIALY.items()},
    rozmowy={klucz(k): v for k, v in D.ROZMOWY.items()}, luzne=D.LUZNE,
    nazwy_postaci=D.NAZWY_POSTACI, pomoc=D.POMOC,
)
cel = os.path.join(TU, "..", "godot", "dane", "dane.json")
with open(cel, "w", encoding="utf-8") as f:
    json.dump(wynik, f, ensure_ascii=False, indent=1)
print("Zapisano", os.path.normpath(cel))
