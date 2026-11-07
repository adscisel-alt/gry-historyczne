"""Ikony interfejsu (pixel art 16×16) i dźwięki gry „Roman Dmowski. Droga do Wersalu 3D”.

Korzysta z generatora wersji 2D Zamościa (zamosc/narzedzia/generuj_zasoby.py).
Uruchom:  python narzedzia/generuj_ikony_i_dzwieki.py
"""
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TU, "..", "..", "zamosc", "narzedzia"))
import generuj_zasoby as G  # noqa: E402
import pygame  # noqa: E402

UI = os.path.join(TU, "..", "godot", "ui")
AUDIO = os.path.join(TU, "..", "godot", "audio")


def nowa_ikona(rysuj):
    s = G.nowa(16, 16)
    rysuj(s)
    return G.obrys(s)


def poparcie(s):
    G.prost(s, 3, 1, 1, 14, G.DREWNO[1])
    G.prost(s, 4, 2, 10, 4, G.BIEL)
    G.prost(s, 4, 6, 10, 4, (210, 40, 52))
    G.px(s, 2, 1, G.ZLOTO[2])


def prasa(s):
    G.prost(s, 2, 2, 12, 12, (236, 232, 220))
    G.prost(s, 3, 3, 10, 2, (40, 40, 44))
    for y in (7, 9, 11):
        G.prost(s, 3, y, 4, 1, G.PERG[0])
        G.prost(s, 9, y, 4, 1, G.PERG[0])
    G.prost(s, 3, 6, 4, 1, (120, 30, 40))


def ochotnicy(s):
    G.prost(s, 4, 6, 8, 6, (112, 146, 186))          # mundur
    pygame.draw.circle(s, (240, 196, 150), (8, 5), 3)
    G.prost(s, 4, 1, 8, 3, (112, 146, 186))          # rogatywka
    G.prost(s, 3, 3, 10, 1, (40, 30, 24))
    G.prost(s, 7, 8, 2, 1, G.ZLOTO[2])


def teczka(s):
    G.prost(s, 2, 5, 12, 9, (110, 64, 34))
    G.prost(s, 2, 5, 12, 1, (150, 96, 54))
    G.prost(s, 6, 2, 4, 3, (80, 46, 26))
    G.prost(s, 7, 3, 2, 1, (0, 0, 0, 0))
    G.prost(s, 7, 8, 2, 2, G.ZLOTO[2])


def paczka(s):
    G.prost(s, 2, 4, 12, 10, (170, 130, 80))
    G.prost(s, 2, 4, 12, 1, (200, 160, 104))
    G.prost(s, 7, 4, 2, 10, (230, 220, 190))
    G.prost(s, 2, 8, 12, 1, (230, 220, 190))


def legitymacja(s):
    G.prost(s, 1, 3, 14, 10, (200, 40, 50))
    G.prost(s, 2, 4, 5, 6, (236, 226, 200))
    pygame.draw.circle(s, (240, 196, 150), (4, 6), 1)
    for y in (5, 7, 9):
        G.prost(s, 8, y, 6, 1, (250, 236, 200))


def odznaka(s):
    pygame.draw.polygon(s, (112, 146, 186), [(8, 1), (14, 6), (11, 14), (5, 14), (2, 6)])
    pygame.draw.circle(s, G.ZLOTO[2], (8, 8), 3)
    G.px(s, 8, 8, G.BIEL)


def telegram(s):
    G.prost(s, 2, 2, 12, 12, (240, 228, 196))
    G.prost(s, 2, 2, 12, 2, (210, 160, 60))
    for y in (6, 8, 10, 12):
        G.prost(s, 4, y, 8, 1, (60, 60, 70))


def dokument(s):
    G.prost(s, 3, 1, 10, 14, G.BIEL)
    G.prost(s, 5, 3, 6, 2, (40, 56, 120))
    for y in (7, 9, 11):
        G.prost(s, 5, y, 6, 1, G.PERG[0])
    pygame.draw.circle(s, (40, 56, 120), (11, 13), 2)


IKONY = {"poparcie": poparcie, "prasa": prasa, "ochotnicy": ochotnicy, "teczka": teczka, "paczka": paczka,
         "legitymacja": legitymacja, "odznaka": odznaka, "telegram": telegram, "dokument": dokument}
Z_ZAMOSCIA = {"fundusze": "zloto", "dzialacze": "ludnosc", "wiedza": "wiedza", "dzien": "dzien",
              "robotnicy": "robotnicy", "kompas": "kompas", "sakiewka": "sakiewka", "mapa": "plan",
              "nota": "przywilej", "pioro": "pioro", "rozbiorka": "rozbiorka", "pomoc": "pomoc", "menu": "menu",
              "ksiega": "ksiega"}


def muzyka():
    """Marsz w metrum 2/4 — melodia na „lutni” i miarowy bas."""
    tempo = .2
    melodia = ("G4:2 H4:1 D5:1 G5:2 D5:2 | E5:2 C5:2 A4:4 | H4:2 D5:1 G5:1 Fis5:2 E5:2 | D5:6 D5:2 | "
               "E5:2 E5:1 Fis5:1 G5:2 E5:2 | D5:2 H4:2 G4:4 | A4:2 H4:2 C5:2 E5:2 | D5:6 R:2 | "
               "G5:2 Fis5:1 E5:1 D5:2 H4:2 | C5:2 E5:2 A4:4 | D5:2 C5:1 H4:1 A4:2 D5:2 | G4:6 R:2")
    nuty = [t for t in melodia.replace("|", " ").split() if t]
    dl = sum(int(t.split(":")[1]) for t in nuty) * tempo
    n = int(dl * G.CZESTO) + G.CZESTO
    out = [0.0] * n
    pos = 0
    for k, t in enumerate(nuty):
        nazwa, d = t.split(":")
        d = int(d) * tempo
        if nazwa != "R":
            for i, v in enumerate(G.lutnia(G.NUTY[nazwa], d + .3, .3, k)):
                if pos + i < n:
                    out[pos + i] += v
        pos += int(d * G.CZESTO)
    bas = ["G2", "D3", "C3", "D3", "G2", "D3", "D3", "D3", "C3", "G2", "A2", "D3", "G2", "C3", "D3", "G2"]
    takt = 8 * tempo
    for k, b in enumerate(bas[: int(dl / takt)]):
        for j in range(4):
            f = G.NUTY[b] * (1 if j % 2 == 0 else 1.5)
            start = int((k * takt + j * takt / 4) * G.CZESTO)
            for i, v in enumerate(G.lutnia(f, takt / 4 + .2, .2 if j % 2 == 0 else .1, k * 4 + j)):
                if start + i < n:
                    out[start + i] += v
    out = out[: int(dl * G.CZESTO)]
    for i in range(400):
        out[i] *= i / 400
        out[-1 - i] *= i / 400
    return out


def main():
    pygame.init()
    os.makedirs(UI, exist_ok=True)
    os.makedirs(AUDIO, exist_ok=True)
    for nazwa, fn in IKONY.items():
        pygame.image.save(nowa_ikona(fn), os.path.join(UI, "ikona_%s.png" % nazwa))
    for nazwa, zrodlo in Z_ZAMOSCIA.items():
        pygame.image.save(G.ikona(zrodlo), os.path.join(UI, "ikona_%s.png" % nazwa))
    pygame.image.save(G.roza_wiatrow(), os.path.join(UI, "roza.png"))
    ik = pygame.transform.scale(nowa_ikona(teczka), (64, 64))
    pygame.image.save(ik, os.path.join(TU, "..", "godot", "icon.png"))
    G.SFX = AUDIO
    G.generuj_dzwieki()
    G.zapisz_wav("muzyka", muzyka())
    print("Ikony i dźwięki: gotowe")


if __name__ == "__main__":
    main()
