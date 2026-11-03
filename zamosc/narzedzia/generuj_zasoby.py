"""Generator zasobów gry „Jan Zamoyski i Miasto Idealne”.

Tworzy WSZYSTKIE grafiki (pixel art w stylu 16-bit) i dźwięki gry
wyłącznie z kodu — bez zewnętrznych plików. Uruchom:

    python narzedzia/generuj_zasoby.py

Wynik trafia do katalogów assets/gfx (PNG) i assets/sfx (WAV),
a ikona programu do assets/ikona.ico.
"""
import math
import os
import random
import struct
import sys
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

KATALOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GFX = os.path.join(KATALOG, "assets", "gfx")
SFX = os.path.join(KATALOG, "assets", "sfx")

# ----------------------------------------------------------------- paleta
OUT = (24, 16, 28)
TRAWA = [(64, 124, 56), (80, 146, 64), (100, 166, 74), (128, 188, 92)]
LISCIE = [(30, 82, 50), (44, 108, 58), (66, 138, 66), (104, 170, 84)]
PIEN = [(78, 48, 30), (110, 72, 42)]
WODA = [(32, 72, 150), (44, 100, 186), (72, 136, 214), (150, 196, 240)]
SKALA = [(72, 72, 86), (106, 106, 118), (142, 142, 152), (186, 186, 194)]
DROGA = [(140, 106, 70), (170, 134, 90), (196, 164, 116)]
BRUK = [(118, 108, 100), (152, 140, 126), (184, 172, 154), (206, 196, 178)]
BAGNO = [(74, 100, 58), (92, 120, 66), (50, 92, 110), (128, 150, 80)]
CEGLA = [(120, 44, 36), (162, 66, 46), (196, 100, 66), (222, 140, 96)]
TYNK = [(176, 160, 128), (212, 196, 160), (236, 224, 192), (250, 244, 224)]
DACH = [(110, 36, 32), (150, 52, 38), (190, 82, 52), (220, 120, 76)]
DREWNO = [(92, 58, 34), (130, 86, 50), (168, 120, 72), (200, 158, 104)]
ZLOTO = [(150, 100, 24), (204, 150, 40), (244, 200, 72), (255, 240, 160)]
PERG = [(150, 116, 74), (198, 168, 120), (228, 208, 164), (244, 232, 200)]
OKNO = [(30, 40, 70), (70, 110, 160), (160, 200, 230)]
CZERWONY = [(110, 20, 32), (170, 34, 44), (214, 64, 64)]
GRANAT = [(22, 30, 70), (40, 56, 120), (70, 92, 160)]
BIEL = (248, 244, 232)


def nowa(w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    return s


def px(s, x, y, c):
    if 0 <= x < s.get_width() and 0 <= y < s.get_height():
        s.set_at((x, y), c)


def prost(s, x, y, w, h, c):
    pygame.draw.rect(s, c, (x, y, w, h))


def jasniej(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def dither(s, x, y, w, h, c1, c2):
    for j in range(h):
        for i in range(w):
            px(s, x + i, y + j, c1 if (i + j) % 2 == 0 else c2)


def obrys(s, kolor=OUT):
    """Dodaje ciemny kontur wokół nieprzezroczystych pikseli (typowe dla 16-bit)."""
    w, h = s.get_size()
    maska = [[s.get_at((x, y)).a > 0 for x in range(w)] for y in range(h)]
    for y in range(h):
        for x in range(w):
            if maska[y][x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and maska[ny][nx]:
                    s.set_at((x, y), kolor)
                    break
    return s


def zapisz(s, nazwa):
    pygame.image.save(s, os.path.join(GFX, nazwa + ".png"))


# ================================================================ KAFELKI
def kafel_trawa(ziarno):
    r = random.Random(ziarno)
    s = nowa(16, 16)
    s.fill(TRAWA[1])
    for _ in range(18):
        px(s, r.randrange(16), r.randrange(16), TRAWA[0])
    for _ in range(10):
        x, y = r.randrange(16), r.randrange(1, 16)
        px(s, x, y, TRAWA[2])
        px(s, x, y - 1, TRAWA[3])
    if ziarno == 3:  # kwiatki
        for _ in range(3):
            x, y = r.randrange(1, 15), r.randrange(1, 15)
            px(s, x, y, (240, 220, 90) if r.random() < .5 else (236, 236, 250))
    return s


def drzewo(wariant):
    r = random.Random(100 + wariant)
    s = nowa(16, 24)
    prost(s, 7, 16, 3, 7, PIEN[0])
    prost(s, 8, 16, 1, 7, PIEN[1])
    if wariant == 2:  # świerk
        for i, (y, w) in enumerate([(2, 2), (5, 6), (8, 8), (11, 12), (14, 14)]):
            prost(s, 8 - w // 2, y, w, 4, LISCIE[1])
            prost(s, 8 - w // 2, y + 3, w, 1, LISCIE[0])
            prost(s, 8 - w // 2 + 1, y, max(1, w // 3), 1, LISCIE[2])
    else:
        pygame.draw.circle(s, LISCIE[0], (8, 10), 7)
        pygame.draw.circle(s, LISCIE[1], (8, 9), 6)
        pygame.draw.circle(s, LISCIE[2], (7, 7), 4)
        for _ in range(8):
            px(s, r.randrange(3, 13), r.randrange(4, 15), LISCIE[0])
        for _ in range(5):
            px(s, r.randrange(4, 10), r.randrange(4, 9), LISCIE[3])
        if wariant == 1:
            for _ in range(4):
                px(s, r.randrange(4, 13), r.randrange(5, 14), (200, 50, 50))
    return obrys(s)


def kafel_skala():
    s = kafel_trawa(7)
    for (x, y, rr) in [(5, 9, 5), (11, 6, 4), (11, 12, 3)]:
        pygame.draw.circle(s, SKALA[0], (x, y + 1), rr)
        pygame.draw.circle(s, SKALA[1], (x, y), rr)
        pygame.draw.circle(s, SKALA[2], (x - 1, y - 1), max(1, rr - 2))
        px(s, x - 2, y - 2, SKALA[3])
    return s


def kafel_woda(klatka):
    s = nowa(16, 16)
    s.fill(WODA[1])
    r = random.Random(5)
    for _ in range(14):
        px(s, r.randrange(16), r.randrange(16), WODA[0])
    for i in range(3):
        y = (i * 6 + klatka * 3) % 16
        x = (i * 5 + klatka * 2) % 12
        prost(s, x, y, 4, 1, WODA[2])
        px(s, x + 1, y - 1 if y > 0 else y, WODA[3])
    return s


def kafel_bagno():
    s = nowa(16, 16)
    s.fill(BAGNO[1])
    r = random.Random(9)
    for _ in range(20):
        px(s, r.randrange(16), r.randrange(16), BAGNO[0])
    pygame.draw.ellipse(s, BAGNO[2], (3, 6, 7, 4))
    pygame.draw.ellipse(s, BAGNO[2], (9, 11, 5, 3))
    px(s, 5, 7, WODA[3])
    for x in (2, 11, 13):  # trzciny
        prost(s, x, 2, 1, 5, BAGNO[3])
        prost(s, x, 1, 1, 2, DREWNO[0])
    return s


def kafel_droga():
    s = nowa(16, 16)
    s.fill(DROGA[1])
    r = random.Random(11)
    for _ in range(16):
        px(s, r.randrange(16), r.randrange(16), DROGA[0])
    for _ in range(8):
        px(s, r.randrange(16), r.randrange(16), DROGA[2])
    return s


def kafel_bruk():
    s = nowa(16, 16)
    s.fill(BRUK[0])
    for j in range(4):
        for i in range(4):
            ox = (j % 2) * 2
            x, y = i * 4 + ox, j * 4
            prost(s, x % 16, y, 3, 3, BRUK[1])
            px(s, x % 16, y, BRUK[2])
            if (i + j) % 3 == 0:
                px(s, (x + 1) % 16, y + 1, BRUK[3])
    return s


def kafel_most():
    s = kafel_woda(0)
    prost(s, 0, 1, 16, 14, DREWNO[1])
    for y in range(1, 15, 3):
        prost(s, 0, y, 16, 1, DREWNO[0])
        prost(s, 0, y + 1, 16, 1, DREWNO[2])
    prost(s, 0, 0, 16, 1, DREWNO[0])
    prost(s, 0, 15, 16, 1, DREWNO[0])
    return s


def rusztowanie():
    s = nowa(16, 16)
    for x in (1, 8, 14):
        prost(s, x, 0, 1, 16, DREWNO[2])
    for y in (3, 9, 15):
        prost(s, 0, y, 16, 1, DREWNO[1])
    pygame.draw.line(s, DREWNO[0], (1, 15), (8, 3))
    pygame.draw.line(s, DREWNO[0], (8, 15), (14, 9))
    return s


# ================================================================ BUDYNKI
def okno(s, x, y, w=3, h=4):
    prost(s, x, y, w, h, OKNO[0])
    prost(s, x, y, w, 1, OKNO[1])
    px(s, x, y + 1, OKNO[2])


def luk(s, x, y, w, h, c):
    prost(s, x, y + w // 2, w, h - w // 2, c)
    pygame.draw.ellipse(s, c, (x, y, w, w))


def dom():
    s = nowa(16, 26)
    prost(s, 2, 14, 12, 11, TYNK[2])
    prost(s, 2, 14, 12, 1, TYNK[1])
    for y in range(16, 25, 3):
        prost(s, 2, y, 12, 1, TYNK[1])
    prost(s, 2, 14, 1, 11, DREWNO[1])
    prost(s, 13, 14, 1, 11, DREWNO[1])
    prost(s, 7, 18, 3, 7, DREWNO[0])
    px(s, 9, 21, ZLOTO[2])
    okno(s, 3, 17, 3, 3)
    okno(s, 11, 17, 2, 3)
    for i in range(9):  # dach dwuspadowy z gontu
        prost(s, 7 - i, 5 + i, 2 + 2 * i, 1, DACH[1] if i % 2 else DACH[2])
    prost(s, 0, 14, 16, 1, DACH[0])
    prost(s, 11, 4, 2, 5, CEGLA[1])
    px(s, 11, 4, CEGLA[2])
    return obrys(s)


def kamienica(kolor, ziarno):
    r = random.Random(ziarno)
    s = nowa(32, 46)
    ciemny, jasny = jasniej(kolor, .72), jasniej(kolor, 1.15)
    # fasada
    prost(s, 1, 12, 30, 33, kolor)
    prost(s, 1, 12, 30, 1, jasny)
    prost(s, 1, 30, 30, 2, TYNK[3])
    # attyka
    prost(s, 0, 9, 32, 4, TYNK[2])
    prost(s, 0, 12, 32, 1, TYNK[1])
    for x in range(1, 31, 5):
        prost(s, x, 6, 2, 3, TYNK[2])
        px(s, x, 5, ZLOTO[2])
        prost(s, x + 2, 10, 2, 2, ciemny)
    # okna piętra
    for x in (4, 13, 22):
        okno(s, x + 1, 16, 4, 6)
        prost(s, x, 15, 6, 1, TYNK[3])
        prost(s, x, 22, 6, 1, TYNK[1])
        okno(s, x + 1, 25, 4, 4)
    # ornamenty
    for x in range(2, 30, 4):
        px(s, x, 14, ciemny)
    # podcienia (arkady)
    prost(s, 1, 32, 30, 13, ciemny)
    for x in (2, 12, 22):
        luk(s, x, 33, 8, 12, OUT)
        luk(s, x + 1, 34, 6, 11, (52, 40, 44))
    prost(s, 0, 44, 32, 2, BRUK[1])
    if r.random() < .6:
        prost(s, 14, 37, 4, 8, DREWNO[1])
    return obrys(s)


def tartak():
    s = nowa(32, 36)
    prost(s, 2, 16, 22, 18, DREWNO[2])
    for y in range(16, 34, 3):
        prost(s, 2, y, 22, 1, DREWNO[1])
    for i in range(10):
        prost(s, 12 - i, 6 + i, 2 + i * 2 + 2, 1, DREWNO[0] if i % 2 else DREWNO[1])
    prost(s, 8, 24, 8, 10, OUT)
    pygame.draw.circle(s, SKALA[2], (12, 28), 4)
    pygame.draw.circle(s, SKALA[3], (12, 28), 2)
    for i in range(3):  # stos bali
        for j in range(3 - i):
            x, y = 23 + j * 3 + i, 30 - i * 3
            pygame.draw.circle(s, DREWNO[1], (x, y), 2)
            px(s, x, y, DREWNO[3])
    return obrys(s)


def kamieniolom():
    s = nowa(32, 34)
    pygame.draw.ellipse(s, SKALA[0], (1, 10, 30, 23))
    pygame.draw.ellipse(s, SKALA[1], (3, 10, 26, 18))
    pygame.draw.ellipse(s, SKALA[0], (8, 16, 14, 9))
    for (x, y) in [(5, 24), (22, 22), (12, 27)]:
        prost(s, x, y, 6, 4, SKALA[2])
        prost(s, x, y, 6, 1, SKALA[3])
    pygame.draw.line(s, DREWNO[1], (20, 8), (26, 20), 2)  # kilof
    pygame.draw.line(s, SKALA[3], (17, 10), (24, 6), 2)
    return obrys(s)


def cegielnia():
    s = nowa(32, 40)
    pygame.draw.ellipse(s, CEGLA[1], (2, 18, 20, 20))
    pygame.draw.ellipse(s, CEGLA[2], (4, 18, 16, 14))
    prost(s, 9, 28, 6, 8, OUT)
    prost(s, 10, 30, 4, 6, (240, 140, 40))
    prost(s, 11, 33, 2, 3, (255, 220, 120))
    prost(s, 14, 4, 4, 18, CEGLA[0])
    prost(s, 15, 4, 1, 18, CEGLA[2])
    for i, (x, y) in enumerate([(16, 1), (19, 0), (13, 0)]):
        pygame.draw.circle(s, (200, 200, 208), (x, y + 2), 2)
    for j in range(3):
        for i in range(3):
            prost(s, 22 + i * 3, 33 - j * 3, 3, 2, CEGLA[2 if (i + j) % 2 else 1])
    return obrys(s)


def kram():
    s = nowa(16, 22)
    prost(s, 2, 12, 12, 8, DREWNO[2])
    prost(s, 2, 12, 12, 1, DREWNO[3])
    prost(s, 2, 6, 1, 14, DREWNO[0])
    prost(s, 13, 6, 1, 14, DREWNO[0])
    for i in range(7):
        prost(s, 1 + i * 2, 4, 2, 4, CZERWONY[1] if i % 2 else BIEL)
    prost(s, 1, 8, 14, 1, CZERWONY[0])
    for x, c in [(4, (230, 180, 60)), (7, (120, 180, 70)), (10, (200, 80, 60))]:
        pygame.draw.circle(s, c, (x, 12), 2)
    return obrys(s)


def palac():
    s = nowa(48, 50)
    prost(s, 1, 22, 46, 26, TYNK[2])
    prost(s, 1, 22, 46, 1, TYNK[3])
    prost(s, 1, 34, 46, 1, TYNK[1])
    for i in range(12):  # dach
        prost(s, 1 + i // 3, 10 + i, 46 - 2 * (i // 3), 1, DACH[2] if i % 3 == 0 else DACH[1])
    prost(s, 0, 21, 48, 2, DACH[0])
    # ryzalit środkowy z attyką
    prost(s, 17, 14, 14, 34, TYNK[3])
    prost(s, 16, 12, 16, 3, TYNK[2])
    for x in range(17, 31, 4):
        prost(s, x, 9, 2, 3, TYNK[3])
        px(s, x, 8, ZLOTO[2])
    luk(s, 21, 36, 6, 12, DREWNO[0])
    px(s, 24, 42, ZLOTO[2])
    pygame.draw.circle(s, CZERWONY[1], (24, 19), 3)  # herb Jelita
    px(s, 24, 19, BIEL)
    for x in (3, 9, 35, 41):
        okno(s, x, 25, 4, 6)
        okno(s, x, 38, 4, 6)
    okno(s, 19, 25, 3, 6)
    okno(s, 26, 25, 3, 6)
    prost(s, 0, 47, 48, 3, SKALA[1])
    return obrys(s)


def ratusz():
    s = nowa(32, 78)
    # wieża
    prost(s, 12, 14, 8, 36, (226, 150, 140))
    prost(s, 12, 14, 1, 36, (190, 110, 104))
    for y in (20, 30, 40):
        okno(s, 14, y, 4, 5)
    prost(s, 11, 12, 10, 2, TYNK[2])
    prost(s, 13, 6, 6, 6, DACH[1])  # hełm
    prost(s, 14, 3, 4, 3, DACH[2])
    prost(s, 15, 0, 2, 3, ZLOTO[2])
    pygame.draw.circle(s, BIEL, (16, 26), 2)  # zegar
    px(s, 16, 25, OUT)
    # korpus
    prost(s, 1, 44, 30, 24, (232, 160, 150))
    prost(s, 1, 44, 30, 1, (246, 196, 186))
    prost(s, 0, 40, 32, 5, TYNK[2])
    for x in range(1, 31, 5):
        prost(s, x, 37, 2, 3, TYNK[2])
        px(s, x, 36, ZLOTO[2])
    for x in (4, 13, 22):
        okno(s, x + 1, 48, 4, 6)
    # wachlarzowe schody
    for i in range(5):
        prost(s, 10 - i * 2, 62 + i * 3, 12 + i * 4, 3, SKALA[2] if i % 2 else SKALA[1])
    luk(s, 13, 56, 6, 7, DREWNO[0])
    return obrys(s)


def kolegiata():
    s = nowa(32, 66)
    prost(s, 3, 26, 26, 38, TYNK[3])
    prost(s, 3, 26, 26, 1, BIEL)
    # szczyt fasady z wolutami
    for i in range(14):
        prost(s, 3 + i, 26 - i, 26 - 2 * i, 1, TYNK[2])
    prost(s, 8, 18, 16, 1, TYNK[1])
    pygame.draw.circle(s, OKNO[1], (16, 20), 3)
    pygame.draw.circle(s, OKNO[2], (16, 20), 1)
    prost(s, 15, 6, 2, 7, ZLOTO[2])  # krzyż
    prost(s, 13, 8, 6, 2, ZLOTO[2])
    # dzwonnica boczna
    prost(s, 25, 14, 6, 50, TYNK[2])
    prost(s, 24, 10, 8, 4, (90, 110, 120))
    px(s, 28, 8, ZLOTO[2])
    okno(s, 26, 20, 4, 6)
    for x in (6, 20):
        luk(s, x, 32, 5, 14, OKNO[0])
        px(s, x + 2, 34, OKNO[2])
    luk(s, 12, 48, 8, 16, DREWNO[0])
    prost(s, 15, 50, 2, 14, DREWNO[1])
    prost(s, 2, 63, 30, 3, SKALA[1])
    return obrys(s)


def akademia():
    s = nowa(48, 48)
    prost(s, 1, 16, 46, 30, (236, 210, 150))
    prost(s, 1, 16, 46, 1, TYNK[3])
    prost(s, 0, 12, 48, 5, TYNK[2])
    for x in range(1, 47, 5):
        prost(s, x, 8, 2, 4, TYNK[2])
        px(s, x, 7, ZLOTO[2])
    for row in (20, 32):
        for x in range(4, 46, 7):
            okno(s, x, row, 4, 6)
    luk(s, 20, 34, 8, 12, DREWNO[0])
    prost(s, 18, 30, 12, 2, TYNK[3])
    # księga nad wejściem
    prost(s, 21, 26, 6, 4, BIEL)
    prost(s, 24, 26, 1, 4, OUT)
    prost(s, 0, 45, 48, 3, SKALA[1])
    return obrys(s)


def bastion():
    s = nowa(34, 36)
    pts = [(17, 2), (32, 12), (28, 32), (6, 32), (2, 12)]
    pygame.draw.polygon(s, CEGLA[1], [(x, y + 2) for x, y in pts])
    pygame.draw.polygon(s, TRAWA[1], [(17, 4), (29, 12), (26, 26), (8, 26), (5, 12)])
    for y in range(28, 34, 2):
        pygame.draw.line(s, CEGLA[0], (6, y), (28, y))
    pygame.draw.line(s, CEGLA[3], (2, 14), (17, 4))
    # armata
    prost(s, 12, 14, 10, 3, SKALA[0])
    prost(s, 20, 13, 3, 5, SKALA[0])
    pygame.draw.circle(s, DREWNO[0], (14, 18), 2)
    pygame.draw.circle(s, DREWNO[0], (19, 18), 2)
    for (x, y) in [(9, 22), (11, 23), (10, 21)]:
        px(s, x, y, OUT)
    return obrys(s)


def brama():
    s = nowa(32, 44)
    prost(s, 1, 14, 30, 28, CEGLA[1])
    for y in range(16, 42, 4):
        for x in range(1 + (y // 4 % 2) * 3, 31, 6):
            prost(s, x, y, 5, 1, CEGLA[0])
    prost(s, 0, 10, 32, 5, TYNK[2])
    for x in range(1, 31, 5):
        prost(s, x, 6, 2, 4, TYNK[2])
        px(s, x, 5, ZLOTO[2])
    luk(s, 9, 22, 14, 20, OUT)
    luk(s, 10, 23, 12, 19, (60, 46, 40))
    for x in range(11, 22, 3):  # krata (brona)
        prost(s, x, 25, 1, 10, SKALA[1])
    pygame.draw.circle(s, TYNK[3], (16, 17), 3)
    px(s, 16, 17, CZERWONY[1])
    return obrys(s)


def rynek_tile():
    return kafel_bruk()


def studnia():
    s = nowa(16, 20)
    pygame.draw.ellipse(s, SKALA[1], (2, 10, 12, 8))
    pygame.draw.ellipse(s, WODA[1], (4, 11, 8, 4))
    prost(s, 3, 3, 1, 10, DREWNO[1])
    prost(s, 12, 3, 1, 10, DREWNO[1])
    prost(s, 2, 2, 12, 2, DACH[1])
    return obrys(s)


# ================================================================ POSTACIE
POSTACIE = {
    # Jan Zamoyski — szlachcic, kanclerz i hetman: kołpak z piórem czapli,
    # czerwony żupan, granatowy kontusz, złoty pas, żółte buty, kompas w dłoni.
    "zamoyski": dict(skora=(240, 196, 150), wlosy=(70, 40, 24), plaszcz=GRANAT,
                     szata=CZERWONY, pas=ZLOTO[2], buty=(220, 170, 40),
                     czapka="kolpak", czapka_kol=CZERWONY[1], broda=True,
                     trzyma="kompas"),
    # Bernardo Morando — architekt z Padwy: czarny beret, ciemna toga, plan miasta
    "morando": dict(skora=(232, 186, 140), wlosy=(50, 36, 30), plaszcz=[(30, 30, 36), (54, 54, 64), (84, 84, 96)],
                    szata=[(90, 70, 40), (130, 100, 60), (170, 140, 90)], pas=(120, 90, 50),
                    buty=(40, 30, 30), czapka="beret", czapka_kol=(20, 20, 26), broda=True,
                    trzyma="plan"),
    # Szymon Szymonowic — poeta i uczony: zielona szata, księga
    "szymonowic": dict(skora=(240, 200, 160), wlosy=(130, 90, 50), plaszcz=[(30, 70, 50), (44, 104, 70), (80, 140, 96)],
                       szata=[(150, 140, 110), (196, 186, 150), (230, 220, 190)], pas=(90, 60, 30),
                       buty=(60, 40, 30), czapka="biret", czapka_kol=(40, 40, 50), broda=False,
                       trzyma="ksiega"),
    # Hagop — kupiec ormiański (postać fikcyjna): wysoka futrzana czapa, szkarłatna szata, waga
    "hagop": dict(skora=(214, 164, 118), wlosy=(30, 24, 20), plaszcz=[(100, 30, 80), (140, 50, 110), (180, 90, 150)],
                  szata=[(180, 130, 40), (220, 170, 60), (244, 210, 110)], pas=(60, 40, 90),
                  buty=(110, 40, 30), czapka="futrzana", czapka_kol=(70, 46, 30), broda=True,
                  trzyma="waga"),
}


def postac(p, kierunek, klatka):
    """Rysuje postać 16x24 (+margines na kontur). kierunek: dol/gora/prawo."""
    s = nowa(18, 26)
    o = 1  # margines
    sk, sk2 = p["skora"], jasniej(p["skora"], .82)
    pl, sz = p["plaszcz"], p["szata"]
    # nogi i buty
    kroki = [(0, 0), (1, -1)] if klatka else [(0, 0), (0, 0)]
    if kierunek == "prawo":
        lx = [6, 9] if klatka == 0 else [5, 10]
        for x in lx:
            prost(s, o + x, o + 19, 2, 3, jasniej(sz[0], .8))
            prost(s, o + x, o + 21, 3, 2, p["buty"])
    else:
        dy = kroki[1][1] if klatka else 0
        prost(s, o + 5, o + 19 + dy, 2, 3, jasniej(sz[0], .8))
        prost(s, o + 9, o + 19 - dy, 2, 3, jasniej(sz[0], .8))
        prost(s, o + 4, o + 21 + dy, 3, 2, p["buty"])
        prost(s, o + 9, o + 21 - dy, 3, 2, p["buty"])
    # tułów: szata (żupan) + płaszcz (kontusz)
    if kierunek == "prawo":
        prost(s, o + 4, o + 10, 8, 10, pl[1])
        prost(s, o + 9, o + 10, 3, 10, sz[1])
        prost(s, o + 4, o + 15, 8, 1, p["pas"])
        prost(s, o + 6, o + 11, 3, 6, pl[0])  # ramię
        prost(s, o + 7, o + 17, 2, 2, sk)
    else:
        prost(s, o + 3, o + 10, 10, 10, pl[1])
        prost(s, o + 3, o + 10, 1, 10, pl[0])
        if kierunek == "dol":
            prost(s, o + 6, o + 10, 4, 10, sz[1])
            prost(s, o + 7, o + 10, 1, 10, sz[2])
            for y in range(11, 15, 2):
                px(s, o + 8, o + y, ZLOTO[2])  # guziki
        else:
            prost(s, o + 7, o + 10, 2, 10, pl[0])
        prost(s, o + 3, o + 15, 10, 1, p["pas"])
        prost(s, o + 1, o + 11, 2, 6, pl[0])
        prost(s, o + 13, o + 11, 2, 6, pl[0])
        prost(s, o + 1, o + 17, 2, 2, sk)
        prost(s, o + 13, o + 17, 2, 2, sk)
    # głowa
    if kierunek == "prawo":
        prost(s, o + 5, o + 3, 7, 7, sk)
        px(s, o + 12, o + 6, sk)
        px(s, o + 10, o + 5, OUT)
        prost(s, o + 5, o + 3, 2, 6, p["wlosy"])
        if p["broda"]:
            prost(s, o + 8, o + 7, 4, 1, p["wlosy"])
            prost(s, o + 8, o + 8, 3, 2, p["wlosy"])
        prost(s, o + 6, o + 9, 5, 1, sk2)
    elif kierunek == "dol":
        prost(s, o + 4, o + 3, 8, 7, sk)
        px(s, o + 6, o + 5, OUT)
        px(s, o + 9, o + 5, OUT)
        px(s, o + 4, o + 6, sk2)
        px(s, o + 11, o + 6, sk2)
        if p["broda"]:
            prost(s, o + 5, o + 7, 6, 1, p["wlosy"])  # wąsy
            prost(s, o + 6, o + 8, 4, 2, p["wlosy"])
        else:
            px(s, o + 7, o + 7, sk2)
            px(s, o + 8, o + 7, sk2)
    else:
        prost(s, o + 4, o + 3, 8, 7, sk)
        prost(s, o + 4, o + 3, 8, 3, p["wlosy"])
        prost(s, o + 5, o + 9, 6, 1, sk2)
    # nakrycie głowy
    c = p["czapka_kol"]
    w0 = 4 if kierunek != "prawo" else 5
    if p["czapka"] == "kolpak":
        prost(s, o + w0 - 1, o + 3, 10 if kierunek != "prawo" else 8, 2, (96, 64, 36))  # futro
        prost(s, o + w0, o + 0, 8 if kierunek != "prawo" else 6, 3, c)
        px(s, o + w0 + 1, o + 0, jasniej(c, 1.3))
        # pióro czapli + złota zapona
        px(s, o + w0 + 6, o + 2, ZLOTO[2])
        prost(s, o + w0 + 6, o - 1, 1, 3, BIEL)
        px(s, o + w0 + 7, o - 1, BIEL)
    elif p["czapka"] == "beret":
        prost(s, o + w0 - 1, o + 1, 10 if kierunek != "prawo" else 9, 3, c)
        prost(s, o + w0, o + 0, 7, 1, c)
    elif p["czapka"] == "biret":
        prost(s, o + w0, o + 0, 8 if kierunek != "prawo" else 7, 4, c)
        px(s, o + w0 + 3, o - 1, (200, 60, 60))
    elif p["czapka"] == "futrzana":
        prost(s, o + w0 - 1, o - 1, 10 if kierunek != "prawo" else 8, 5, c)
        for i in range(0, 9, 2):
            px(s, o + w0 - 1 + i, o - 1, jasniej(c, 1.4))
        prost(s, o + w0, o + 3, 8 if kierunek != "prawo" else 6, 1, jasniej(c, .7))
    # przedmiot w dłoni
    if kierunek == "dol":
        hx, hy = o + 13, o + 16
        t = p["trzyma"]
        if t == "kompas":
            pygame.draw.circle(s, ZLOTO[1], (hx + 2, hy + 1), 3)
            pygame.draw.circle(s, BIEL, (hx + 2, hy + 1), 2)
            px(s, hx + 2, hy, CZERWONY[2])
            px(s, hx + 2, hy + 2, GRANAT[1])
        elif t == "plan":
            prost(s, hx, hy - 3, 4, 7, PERG[3])
            prost(s, hx, hy - 3, 4, 1, PERG[1])
            px(s, hx + 1, hy, GRANAT[1])
            px(s, hx + 2, hy + 1, GRANAT[1])
        elif t == "ksiega":
            prost(s, hx - 1, hy - 1, 5, 6, (120, 40, 40))
            prost(s, hx - 1, hy - 1, 1, 6, ZLOTO[2])
        elif t == "waga":
            prost(s, hx + 2, hy - 4, 1, 6, ZLOTO[1])
            prost(s, hx - 1, hy - 4, 7, 1, ZLOTO[2])
            prost(s, hx - 1, hy - 2, 2, 1, ZLOTO[1])
            prost(s, hx + 4, hy - 2, 2, 1, ZLOTO[1])
    return obrys(s)


def portret(p):
    """Popiersie 32x32 do okna dialogu."""
    s = nowa(32, 32)
    tlo = jasniej(p["plaszcz"][2], 1.1)
    prost(s, 0, 0, 32, 32, PERG[1])
    dither(s, 0, 0, 32, 32, PERG[1], jasniej(tlo, .9))
    sk, sk2 = p["skora"], jasniej(p["skora"], .8)
    # ramiona
    prost(s, 3, 24, 26, 8, p["plaszcz"][1])
    prost(s, 3, 24, 26, 1, p["plaszcz"][2])
    prost(s, 12, 24, 8, 8, p["szata"][1])
    prost(s, 15, 24, 2, 8, p["szata"][2])
    for y in (26, 29):
        px(s, 16, y, ZLOTO[2])
    # szyja + głowa
    prost(s, 13, 21, 6, 4, sk2)
    prost(s, 9, 8, 14, 15, sk)
    prost(s, 9, 8, 1, 15, sk2)
    prost(s, 22, 8, 1, 15, sk2)
    prost(s, 8, 13, 1, 4, sk2)
    prost(s, 23, 13, 1, 4, sk2)
    # oczy, brwi, nos
    for x in (12, 18):
        prost(s, x, 13, 3, 2, BIEL)
        px(s, x + 1, 13, OUT)
        px(s, x + 1, 14, OUT)
        prost(s, x, 11, 3, 1, p["wlosy"])
    prost(s, 15, 15, 2, 3, sk2)
    if p["broda"]:
        prost(s, 11, 18, 10, 2, p["wlosy"])  # wąsy
        prost(s, 10, 19, 2, 2, p["wlosy"])
        prost(s, 20, 19, 2, 2, p["wlosy"])
        prost(s, 13, 20, 6, 4, p["wlosy"])
        px(s, 15, 20, CZERWONY[0])
    else:
        prost(s, 14, 19, 4, 1, CZERWONY[0])
    c = p["czapka_kol"]
    if p["czapka"] == "kolpak":
        prost(s, 9, 2, 14, 6, c)
        prost(s, 10, 1, 12, 1, c)
        prost(s, 11, 3, 3, 1, jasniej(c, 1.3))
        prost(s, 7, 7, 18, 3, (110, 74, 42))
        dither(s, 7, 7, 18, 3, (110, 74, 42), (140, 100, 60))
        pygame.draw.circle(s, ZLOTO[2], (21, 6), 2)
        px(s, 21, 6, CZERWONY[2])
        for i in range(6):
            px(s, 22 + i // 2, 5 - i, BIEL)
            px(s, 23 + i // 2, 5 - i, BIEL)
    elif p["czapka"] == "beret":
        prost(s, 7, 4, 18, 5, c)
        prost(s, 9, 3, 14, 1, c)
        prost(s, 8, 8, 16, 1, jasniej(c, 1.8))
    elif p["czapka"] == "biret":
        prost(s, 8, 2, 16, 7, c)
        prost(s, 15, 0, 2, 2, (200, 60, 60))
        prost(s, 9, 9, 3, 6, p["wlosy"])
        prost(s, 20, 9, 3, 6, p["wlosy"])
    elif p["czapka"] == "futrzana":
        prost(s, 7, 0, 18, 9, c)
        dither(s, 7, 0, 18, 9, c, jasniej(c, 1.3))
        prost(s, 7, 8, 18, 1, jasniej(c, .7))
    return s


# ================================================================ IKONY
def ikona(nazwa):
    s = nowa(16, 16)
    if nazwa == "zloto":
        pygame.draw.circle(s, ZLOTO[1], (8, 8), 6)
        pygame.draw.circle(s, ZLOTO[2], (7, 7), 5)
        prost(s, 6, 5, 3, 5, ZLOTO[1])
        px(s, 5, 5, ZLOTO[3])
    elif nazwa == "drewno":
        for y in (5, 10):
            prost(s, 2, y, 12, 4, DREWNO[1])
            prost(s, 2, y, 12, 1, DREWNO[2])
            pygame.draw.circle(s, DREWNO[3], (13, y + 2), 2)
            px(s, 13, y + 2, DREWNO[1])
    elif nazwa == "kamien":
        pygame.draw.ellipse(s, SKALA[1], (2, 5, 12, 9))
        pygame.draw.ellipse(s, SKALA[2], (3, 5, 8, 5))
        px(s, 5, 6, SKALA[3])
    elif nazwa == "cegla":
        for (x, y) in [(2, 9), (8, 9), (5, 5)]:
            prost(s, x, y, 6, 4, CEGLA[2])
            prost(s, x, y, 6, 1, CEGLA[3])
            prost(s, x, y + 3, 6, 1, CEGLA[0])
    elif nazwa == "ludnosc":
        pygame.draw.circle(s, (240, 196, 150), (8, 5), 3)
        prost(s, 4, 9, 8, 6, CZERWONY[1])
        prost(s, 5, 2, 6, 2, (96, 64, 36))
    elif nazwa == "wiedza":
        prost(s, 2, 4, 12, 9, BIEL)
        prost(s, 7, 4, 2, 9, PERG[1])
        prost(s, 2, 12, 12, 2, (120, 40, 40))
        for y in (6, 8, 10):
            prost(s, 3, y, 3, 1, PERG[0])
            prost(s, 10, y, 3, 1, PERG[0])
        px(s, 12, 2, ZLOTO[3])
        px(s, 13, 1, ZLOTO[2])
    elif nazwa == "dzien":
        pygame.draw.circle(s, ZLOTO[2], (8, 8), 4)
        for a in range(8):
            ang = a * math.pi / 4
            px(s, int(8 + 6 * math.cos(ang)), int(8 + 6 * math.sin(ang)), ZLOTO[3])
    elif nazwa == "robotnicy":
        pygame.draw.line(s, DREWNO[1], (3, 13), (11, 5), 2)
        prost(s, 9, 2, 5, 4, SKALA[1])
    # --------------- przedmioty ekwipunku
    elif nazwa == "kompas":
        pygame.draw.circle(s, ZLOTO[1], (8, 8), 7)
        pygame.draw.circle(s, ZLOTO[2], (8, 8), 6)
        pygame.draw.circle(s, BIEL, (8, 8), 5)
        pygame.draw.polygon(s, CZERWONY[1], [(8, 3), (10, 8), (6, 8)])
        pygame.draw.polygon(s, GRANAT[1], [(8, 13), (10, 8), (6, 8)])
        px(s, 8, 8, ZLOTO[0])
        px(s, 8, 0, ZLOTO[2])
    elif nazwa == "plan":
        prost(s, 1, 2, 14, 12, PERG[2])
        prost(s, 1, 2, 2, 12, PERG[1])
        prost(s, 13, 2, 2, 12, PERG[1])
        pts = [(8, 4), (12, 6), (11, 11), (5, 11), (4, 6)]
        pygame.draw.polygon(s, GRANAT[1], pts, 1)
        prost(s, 7, 7, 3, 3, CEGLA[1])
    elif nazwa == "sakiewka":
        pygame.draw.circle(s, DREWNO[2], (8, 10), 5)
        prost(s, 6, 3, 5, 3, DREWNO[2])
        prost(s, 5, 5, 7, 1, DREWNO[0])
        pygame.draw.circle(s, ZLOTO[2], (8, 10), 2)
    elif nazwa == "przywilej":
        prost(s, 2, 2, 12, 11, PERG[3])
        prost(s, 2, 2, 12, 1, PERG[1])
        for y in (4, 6, 8):
            prost(s, 4, y, 8, 1, PERG[0])
        pygame.draw.circle(s, CZERWONY[1], (10, 12), 3)
        px(s, 10, 12, CZERWONY[2])
        prost(s, 8, 14, 1, 2, CZERWONY[1])
    elif nazwa == "cyrkiel":
        pygame.draw.line(s, SKALA[2], (8, 2), (3, 14), 2)
        pygame.draw.line(s, SKALA[2], (8, 2), (13, 14), 2)
        pygame.draw.circle(s, ZLOTO[2], (8, 3), 2)
        pygame.draw.line(s, SKALA[1], (5, 9), (11, 9))
    elif nazwa == "waga":
        prost(s, 7, 2, 2, 12, ZLOTO[1])
        prost(s, 2, 4, 12, 1, ZLOTO[2])
        pygame.draw.polygon(s, ZLOTO[2], [(1, 9), (5, 9), (3, 6)])
        pygame.draw.polygon(s, ZLOTO[2], [(11, 9), (15, 9), (13, 6)])
        prost(s, 5, 13, 6, 2, ZLOTO[1])
    elif nazwa == "pioro":
        pygame.draw.line(s, BIEL, (12, 1), (4, 13), 3)
        pygame.draw.line(s, PERG[1], (12, 1), (4, 13), 1)
        pygame.draw.line(s, OUT, (4, 13), (2, 15))
        prost(s, 10, 12, 4, 3, OUT)
    elif nazwa == "ksiega":
        prost(s, 3, 2, 10, 12, (120, 40, 40))
        prost(s, 3, 2, 2, 12, (80, 24, 24))
        prost(s, 12, 3, 1, 10, PERG[3])
        pygame.draw.circle(s, ZLOTO[2], (9, 8), 2)
    elif nazwa == "klucze":
        for dx in (0, 4):
            pygame.draw.circle(s, ZLOTO[2], (5 + dx, 4), 2, 1)
            prost(s, 5 + dx, 6, 1, 8, ZLOTO[1])
            prost(s, 6 + dx, 11, 2, 1, ZLOTO[1])
            prost(s, 6 + dx, 13, 2, 1, ZLOTO[1])
    elif nazwa == "chleb":
        pygame.draw.ellipse(s, DREWNO[2], (2, 6, 12, 7))
        pygame.draw.ellipse(s, DREWNO[3], (3, 6, 8, 4))
        for x in (5, 8, 11):
            px(s, x, 8, DREWNO[1])
    elif nazwa == "rozbiorka":
        pygame.draw.line(s, DREWNO[1], (3, 14), (11, 6), 2)
        pygame.draw.polygon(s, SKALA[2], [(8, 3), (14, 9), (12, 11), (6, 5)])
    elif nazwa == "pomoc":
        pygame.draw.circle(s, GRANAT[1], (8, 8), 7)
        f = pygame.font.Font(None, 16)
        t = f.render("?", False, BIEL)
        s.blit(t, (8 - t.get_width() // 2, 8 - t.get_height() // 2 + 1))
    elif nazwa == "menu":
        for y in (4, 8, 12):
            prost(s, 3, y, 10, 2, PERG[3])
    return obrys(s) if nazwa not in ("pomoc",) else s


# ================================================================ UI
def ramka_panel():
    s = nowa(24, 24)
    prost(s, 0, 0, 24, 24, DREWNO[0])
    prost(s, 1, 1, 22, 22, DREWNO[1])
    prost(s, 1, 1, 22, 1, DREWNO[2])
    prost(s, 3, 3, 18, 18, PERG[1])
    prost(s, 4, 4, 16, 16, PERG[2])
    for (x, y) in [(0, 0), (20, 0), (0, 20), (20, 20)]:
        prost(s, x + 1, y + 1, 3, 3, ZLOTO[2])
        px(s, x + 1, y + 1, ZLOTO[3])
        px(s, x + 3, y + 3, ZLOTO[1])
    return s


def ramka_ciemna():
    s = nowa(24, 24)
    prost(s, 0, 0, 24, 24, OUT)
    prost(s, 1, 1, 22, 22, (70, 46, 34))
    prost(s, 2, 2, 20, 20, (46, 30, 26))
    for (x, y) in [(0, 0), (20, 0), (0, 20), (20, 20)]:
        prost(s, x + 1, y + 1, 3, 3, ZLOTO[1])
        px(s, x + 1, y + 1, ZLOTO[3])
    return s


def przycisk(stan):
    s = nowa(12, 12)
    baza = {"norm": DREWNO[2], "hover": DREWNO[3], "wcisk": DREWNO[1], "wyb": ZLOTO[2]}[stan]
    prost(s, 0, 0, 12, 12, OUT)
    prost(s, 1, 1, 10, 10, baza)
    prost(s, 1, 1, 10, 1, jasniej(baza, 1.2))
    prost(s, 1, 10, 10, 1, jasniej(baza, .7))
    return s


def roza_wiatrow():
    s = nowa(56, 56)
    pygame.draw.circle(s, OUT, (28, 28), 27)
    pygame.draw.circle(s, ZLOTO[1], (28, 28), 26)
    pygame.draw.circle(s, ZLOTO[2], (28, 28), 24)
    pygame.draw.circle(s, PERG[3], (28, 28), 21)
    for i in range(16):
        a = i * math.pi / 8
        r1 = 21 if i % 4 == 0 else 19 if i % 2 == 0 else 20
        x1, y1 = 28 + r1 * math.cos(a), 28 + r1 * math.sin(a)
        x2, y2 = 28 + 17 * math.cos(a), 28 + 17 * math.sin(a)
        pygame.draw.line(s, PERG[0], (x1, y1), (x2, y2))
    for i in range(4):  # gwiazda
        a = i * math.pi / 2 - math.pi / 2
        p1 = (28 + 15 * math.cos(a), 28 + 15 * math.sin(a))
        p2 = (28 + 3 * math.cos(a + math.pi / 4), 28 + 3 * math.sin(a + math.pi / 4))
        p3 = (28 + 3 * math.cos(a - math.pi / 4), 28 + 3 * math.sin(a - math.pi / 4))
        pygame.draw.polygon(s, PERG[1], [p1, p2, (28, 28), p3])
    f = pygame.font.Font(None, 14)
    for lit, (x, y) in [("N", (28, 4)), ("S", (28, 52)), ("W", (4, 28)), ("E", (52, 28))]:
        t = f.render(lit, False, CZERWONY[0] if lit == "N" else OUT)
        s.blit(t, (x - t.get_width() // 2, y - t.get_height() // 2 + 1))
    return s


def dymek_e():
    s = nowa(12, 13)
    prost(s, 0, 0, 12, 10, OUT)
    prost(s, 1, 1, 10, 8, BIEL)
    pygame.draw.polygon(s, OUT, [(4, 9), (8, 9), (6, 12)])
    f = pygame.font.Font(None, 12)
    t = f.render("E", False, CZERWONY[0])
    s.blit(t, (6 - t.get_width() // 2, 1))
    return s


def wykrzyknik():
    s = nowa(8, 12)
    prost(s, 2, 0, 4, 7, ZLOTO[2])
    prost(s, 2, 9, 4, 3, ZLOTO[2])
    return obrys(s)


# ================================================================ TŁA
def niebo(s, gora, dol, h):
    """Gradient z ditheringiem — typowy dla 16-bitowych konsol."""
    pasy = 12
    for i in range(pasy):
        t = i / (pasy - 1)
        c = tuple(int(gora[k] + (dol[k] - gora[k]) * t) for k in range(3))
        c2 = tuple(int(gora[k] + (dol[k] - gora[k]) * min(1, t + 1 / pasy)) for k in range(3))
        y0 = int(h * i / pasy)
        y1 = int(h * (i + 1) / pasy)
        prost(s, 0, y0, s.get_width(), y1 - y0, c)
        for x in range(0, s.get_width(), 2):
            px(s, x + (y1 % 2), y1 - 1, c2)


def wzgorza(s, y, kolor, ziarno, amp=14):
    r = random.Random(ziarno)
    faza = r.random() * 6
    for x in range(s.get_width()):
        h = y + int(amp * math.sin(x / 60 + faza) + amp / 2 * math.sin(x / 23 + faza * 2))
        prost(s, x, h, 1, s.get_height() - h, kolor)


def chmury(s, ziarno, kolor=(250, 244, 236)):
    r = random.Random(ziarno)
    for _ in range(5):
        x, y = r.randrange(0, 600), r.randrange(20, 100)
        for i in range(5):
            pygame.draw.ellipse(s, kolor, (x + i * 10, y - (i % 2) * 4, 24, 10))


def blit2(s, spr, x, y, skala=2):
    s.blit(pygame.transform.scale(spr, (spr.get_width() * skala, spr.get_height() * skala)), (x, y))


def tlo_tytul(spr):
    s = pygame.Surface((640, 360))
    niebo(s, (60, 70, 140), (250, 170, 110), 250)
    pygame.draw.circle(s, (255, 224, 150), (500, 190), 40)
    pygame.draw.circle(s, (255, 240, 190), (500, 190), 32)
    chmury(s, 3, (250, 200, 170))
    wzgorza(s, 220, (90, 90, 130), 1, 18)
    wzgorza(s, 245, (60, 100, 80), 2, 10)
    # panorama Rynku Wielkiego
    kol = [(232, 140, 140), (240, 200, 96), (120, 168, 208), (140, 196, 140), (232, 156, 88)]
    for i, x in enumerate([0, 64, 128, 384, 448, 512, 576]):
        blit2(s, spr["kamienica_%d" % (i % 5)], x, 268)
    blit2(s, spr["ratusz"], 256, 204)
    prost(s, 0, 356, 640, 4, BRUK[1])
    return s


def tlo_rozdzial(n, spr):
    s = pygame.Surface((640, 360))
    if n == 1:  # pola nad Topornicą, wytyczanie miasta
        niebo(s, (90, 150, 220), (210, 230, 240), 220)
        chmury(s, 1)
        wzgorza(s, 200, (100, 140, 90), 4, 12)
        prost(s, 0, 240, 640, 120, TRAWA[1])
        for i in range(6):
            blit2(s, spr["drzewo_%d" % (i % 3)], 20 + i * 36, 180 + (i % 2) * 8)
        for x in range(260, 620, 40):  # paliki mierniczych ze sznurem
            prost(s, x, 270, 3, 18, DREWNO[1])
            px(s, x + 1, 269, CZERWONY[1])
        pygame.draw.line(s, PERG[3], (261, 274), (621, 274))
        blit2(s, spr["namiot"], 120, 250)
        blit2(s, spr["postac_zamoyski_dol_0"], 340, 270, 3)
        blit2(s, spr["postac_morando_dol_0"], 400, 270, 3)
    elif n == 2:  # Rynek Wielki
        niebo(s, (80, 140, 220), (200, 220, 240), 200)
        chmury(s, 2)
        prost(s, 0, 300, 640, 60, BRUK[1])
        for x in range(0, 640, 16):
            for y in range(300, 360, 16):
                s.blit(spr["bruk"], (x, y))
        for i, x in enumerate(range(0, 640, 64)):
            if 224 <= x <= 352:
                continue
            blit2(s, spr["kamienica_%d" % (i % 5)], x, 208)
        blit2(s, spr["ratusz"], 256, 148)
        blit2(s, spr["kram"], 120, 300)
        blit2(s, spr["kram"], 480, 300)
        blit2(s, spr["postac_hagop_dol_0"], 540, 300)
    elif n == 3:  # Akademia i Kolegiata
        niebo(s, (120, 110, 190), (240, 200, 160), 220)
        chmury(s, 5, (250, 230, 220))
        wzgorza(s, 230, (110, 120, 110), 6, 8)
        prost(s, 0, 300, 640, 60, BRUK[2])
        for x in range(0, 640, 16):
            for y in range(300, 360, 16):
                s.blit(spr["bruk"], (x, y))
        blit2(s, spr["akademia"], 40, 206)
        blit2(s, spr["kolegiata"], 300, 172)
        blit2(s, spr["akademia"], 420, 206)
        blit2(s, spr["postac_szymonowic_dol_0"], 220, 290)
    else:  # Twierdza o zmierzchu
        niebo(s, (40, 40, 90), (230, 120, 90), 230)
        pygame.draw.circle(s, (255, 200, 140), (120, 210), 30)
        wzgorza(s, 220, (70, 60, 90), 7, 10)
        prost(s, 0, 290, 640, 70, TRAWA[0])
        prost(s, 0, 320, 640, 40, WODA[1])
        for x in range(0, 640, 16):
            s.blit(spr["woda_0"], (x, 330))
            s.blit(spr["woda_0"], (x, 346))
        prost(s, 0, 262, 640, 30, CEGLA[1])
        for y in range(264, 292, 4):
            for x in range((y // 4 % 2) * 6, 640, 12):
                prost(s, x, y, 10, 1, CEGLA[0])
        for x in (60, 360):
            blit2(s, spr["bastion"], x, 222)
        blit2(s, spr["brama"], 220, 204)
        blit2(s, spr["brama"], 500, 204)
    return s


def tlo_koniec(spr):
    s = pygame.Surface((640, 360))
    niebo(s, (20, 24, 70), (120, 60, 120), 260)
    r = random.Random(4)
    for _ in range(70):
        px(s, r.randrange(640), r.randrange(200), (250, 250, 220))
    for (x, y, c) in [(120, 80, (240, 90, 90)), (300, 50, (250, 220, 90)), (480, 90, (120, 200, 250))]:
        for i in range(16):  # fajerwerki
            a = i * math.pi / 8
            pygame.draw.line(s, c, (x + 6 * math.cos(a), y + 6 * math.sin(a)),
                             (x + 22 * math.cos(a), y + 22 * math.sin(a)))
    prost(s, 0, 300, 640, 60, BRUK[1])
    for i, x in enumerate(range(0, 640, 64)):
        if 224 <= x <= 352:
            continue
        blit2(s, spr["kamienica_%d" % ((i + 2) % 5)], x, 208)
    blit2(s, spr["ratusz"], 256, 148)
    return s


def namiot():
    s = nowa(32, 24)
    pygame.draw.polygon(s, BIEL, [(16, 0), (31, 22), (1, 22)])
    pygame.draw.polygon(s, CZERWONY[1], [(16, 0), (20, 22), (12, 22)])
    pygame.draw.polygon(s, OUT, [(16, 8), (19, 22), (13, 22)])
    px(s, 16, 0, ZLOTO[2])
    return obrys(s)


# ================================================================ DŹWIĘKI
CZESTO = 22050


def zapisz_wav(nazwa, probki):
    with wave.open(os.path.join(SFX, nazwa + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(CZESTO)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 30000)) for v in probki))


def ton(f, dl, ksztalt="sin", glosnosc=.5, atak=.005, zanik=None):
    n = int(dl * CZESTO)
    out = []
    for i in range(n):
        t = i / CZESTO
        if ksztalt == "sin":
            v = math.sin(2 * math.pi * f * t)
        elif ksztalt == "kw":
            v = 1 if math.sin(2 * math.pi * f * t) > 0 else -1
            v *= .5
        elif ksztalt == "troj":
            v = 2 * abs(2 * (f * t % 1) - 1) - 1
        else:
            v = 0
        env = min(1, t / atak) if atak else 1
        env *= math.exp(-t * (zanik if zanik else 3 / dl))
        out.append(v * env * glosnosc)
    return out


def szum(dl, glosnosc=.5, zanik=20, filtr=.5, ziarno=1):
    r = random.Random(ziarno)
    n = int(dl * CZESTO)
    out, prev = [], 0
    for i in range(n):
        v = r.uniform(-1, 1)
        prev = prev + filtr * (v - prev)
        out.append(prev * glosnosc * math.exp(-i / CZESTO * zanik))
    return out


def miks(*sciezki):
    n = max(len(x) for x in sciezki)
    return [sum(x[i] if i < len(x) else 0 for x in sciezki) for i in range(n)]


def sekwencja(nuty, ksztalt="sin", glosnosc=.4):
    out = []
    for f, dl in nuty:
        out += ton(f, dl, ksztalt, glosnosc) if f else [0] * int(dl * CZESTO)
    return out


def lutnia(f, dl, glosnosc=.35, ziarno=0):
    """Szarpana struna (algorytm Karplusa-Stronga) — brzmi jak renesansowa lutnia."""
    r = random.Random(ziarno + int(f))
    n = int(dl * CZESTO)
    okres = max(2, int(CZESTO / f))
    bufor = [r.uniform(-1, 1) for _ in range(okres)]
    out = []
    for i in range(n):
        v = bufor[i % okres]
        nast = bufor[(i + 1) % okres]
        bufor[i % okres] = .996 * .5 * (v + nast)
        out.append(v * glosnosc)
    return out


NUTY = {}
for i, nazwa in enumerate(["C", "Cis", "D", "Dis", "E", "F", "Fis", "G", "Gis", "A", "B", "H"]):
    for okt in range(2, 7):
        NUTY[f"{nazwa}{okt}"] = 440 * 2 ** ((i - 9 + (okt - 4) * 12) / 12)


def muzyka():
    """Pogodna galiarda w metrum 3/4 — melodia + bas na „lutni”."""
    tempo = .25  # ósemka
    melodia = (
        "D5:2 F5:1 E5:1 D5:2 | A4:2 C5:2 D5:2 | F5:2 G5:1 F5:1 E5:2 | D5:4 A4:2 | "
        "D5:2 F5:1 G5:1 A5:2 | G5:2 F5:2 E5:2 | F5:2 E5:1 D5:1 C5:2 | D5:6 | "
        "A5:2 G5:1 F5:1 G5:2 | A5:2 F5:2 D5:2 | C5:2 D5:1 E5:1 F5:2 | E5:4 C5:2 | "
        "D5:2 F5:1 E5:1 D5:2 | C5:2 A4:2 C5:2 | D5:2 E5:2 C5:2 | D5:6"
    )
    bas = ["D3", "F3", "D3", "A2", "D3", "C3", "F3", "D3", "F3", "D3", "C3", "A2", "D3", "F3", "A2", "D3"]
    nuty = [t for t in melodia.replace("|", " ").split() if t]
    dl = sum(int(t.split(":")[1]) for t in nuty) * tempo
    n = int(dl * CZESTO) + CZESTO
    out = [0.0] * n
    pos = 0
    for k, t in enumerate(nuty):
        nazwa, d = t.split(":")
        d = int(d) * tempo
        prob = lutnia(NUTY[nazwa], d + .4, .30, k)
        for i, v in enumerate(prob):
            if pos + i < n:
                out[pos + i] += v
        pos += int(d * CZESTO)
    takt = 6 * tempo
    for k, b in enumerate(bas):
        for j in range(3):  # bas na każdą ćwierćnutę: mocna + 2 słabe (akord)
            f = NUTY[b] * (1 if j == 0 else 1.5)
            prob = lutnia(f, takt / 3 + .3, .22 if j == 0 else .12, k * 3 + j)
            start = int((k * takt + j * takt / 3) * CZESTO)
            for i, v in enumerate(prob):
                if start + i < n:
                    out[start + i] += v
    calosc = int(16 * takt * CZESTO)
    out = out[:calosc]
    # płynne zapętlenie
    for i in range(400):
        out[i] *= i / 400
        out[-1 - i] *= i / 400
    return out


def generuj_dzwieki():
    zapisz_wav("klik", ton(1200, .05, "kw", .25, zanik=60))
    zapisz_wav("buduj", miks(szum(.12, .6, 30, .35, 1),
                             [0] * int(.16 * CZESTO) + szum(.12, .6, 30, .35, 2),
                             [0] * int(.32 * CZESTO) + szum(.14, .7, 25, .35, 3)))
    zapisz_wav("gotowe", sekwencja([(NUTY["G4"], .09), (NUTY["C5"], .09), (NUTY["E5"], .09), (NUTY["G5"], .25)], "troj", .45))
    zapisz_wav("moneta", miks(ton(1568, .08, "kw", .2, zanik=30), [0] * int(.07 * CZESTO) + ton(2093, .2, "kw", .2, zanik=18)))
    zapisz_wav("dobrze", sekwencja([(NUTY["C5"], .1), (NUTY["E5"], .1), (NUTY["G5"], .1), (NUTY["C6"], .3)], "sin", .5))
    zapisz_wav("zle", sekwencja([(NUTY["E3"], .18), (NUTY["C3"], .3)], "troj", .45))
    zapisz_wav("strona", szum(.25, .35, 12, .15, 7))
    zapisz_wav("przedmiot", miks(*[[0] * int(i * .06 * CZESTO) + ton(f, .3, "sin", .3, zanik=10)
                                   for i, f in enumerate([NUTY["E5"], NUTY["A5"], NUTY["C6"], NUTY["E6"]])]))
    fanfara = []
    for f, d in [("C4", .15), ("C4", .15), ("C4", .15), ("G4", .45), ("E4", .15), ("G4", .15), ("C5", .7)]:
        fanfara += miks(ton(NUTY[f], d, "kw", .22, .01, zanik=2), ton(NUTY[f] * 2, d, "troj", .12, .01, zanik=2))
    zapisz_wav("fanfara", fanfara)
    zapisz_wav("blad", ton(180, .15, "kw", .2, zanik=15))
    zapisz_wav("rozmowa", sekwencja([(NUTY["A4"], .05), (NUTY["D5"], .08)], "troj", .3))
    zapisz_wav("muzyka", muzyka())


# ================================================================ IKONA .ICO
def zapisz_ico(surf, sciezka):
    """Plik .ico z osadzonym PNG (format akceptowany przez Windows Vista+)."""
    tmp = sciezka + ".png"
    pygame.image.save(surf, tmp)
    with open(tmp, "rb") as f:
        dane = f.read()
    os.remove(tmp)
    w, h = surf.get_size()
    naglowek = struct.pack("<HHH", 0, 1, 1)
    wpis = struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, 1, 32, len(dane), 6 + 16)
    with open(sciezka, "wb") as f:
        f.write(naglowek + wpis + dane)


# ================================================================ MAIN
def main():
    pygame.init()
    os.makedirs(GFX, exist_ok=True)
    os.makedirs(SFX, exist_ok=True)
    spr = {}
    for i in range(4):
        spr["trawa_%d" % i] = kafel_trawa(i)
    for i in range(3):
        spr["drzewo_%d" % i] = drzewo(i)
    spr["skala"] = kafel_skala()
    spr["woda_0"] = kafel_woda(0)
    spr["woda_1"] = kafel_woda(1)
    spr["bagno"] = kafel_bagno()
    spr["droga"] = kafel_droga()
    spr["bruk"] = kafel_bruk()
    spr["most"] = kafel_most()
    spr["rusztowanie"] = rusztowanie()
    spr["dom"] = dom()
    kolory = [(232, 140, 140), (240, 200, 96), (120, 168, 208), (140, 196, 140), (232, 156, 88)]
    for i, k in enumerate(kolory):
        spr["kamienica_%d" % i] = kamienica(k, i)
    spr["tartak"] = tartak()
    spr["kamieniolom"] = kamieniolom()
    spr["cegielnia"] = cegielnia()
    spr["kram"] = kram()
    spr["palac"] = palac()
    spr["ratusz"] = ratusz()
    spr["kolegiata"] = kolegiata()
    spr["akademia"] = akademia()
    spr["bastion"] = bastion()
    spr["brama"] = brama()
    spr["studnia"] = studnia()
    spr["namiot"] = namiot()
    for nazwa, p in POSTACIE.items():
        for k in ("dol", "gora", "prawo"):
            for kl in (0, 1):
                spr[f"postac_{nazwa}_{k}_{kl}"] = postac(p, k, kl)
        spr[f"portret_{nazwa}"] = portret(p)
    for n in ["zloto", "drewno", "kamien", "cegla", "ludnosc", "wiedza", "dzien", "robotnicy",
              "kompas", "plan", "sakiewka", "przywilej", "cyrkiel", "waga", "pioro", "ksiega",
              "klucze", "chleb", "rozbiorka", "pomoc", "menu"]:
        spr["ikona_" + n] = ikona(n)
    spr["ui_panel"] = ramka_panel()
    spr["ui_ciemny"] = ramka_ciemna()
    for st in ("norm", "hover", "wcisk", "wyb"):
        spr["ui_przycisk_" + st] = przycisk(st)
    spr["ui_roza"] = roza_wiatrow()
    spr["ui_e"] = dymek_e()
    spr["ui_wykrzyknik"] = wykrzyknik()
    for k, v in spr.items():
        zapisz(v, k)
    zapisz(tlo_tytul(spr), "tlo_tytul")
    for n in range(1, 5):
        zapisz(tlo_rozdzial(n, spr), "tlo_rozdzial_%d" % n)
    zapisz(tlo_koniec(spr), "tlo_koniec")
    ik = pygame.transform.scale(spr["ikona_kompas"], (64, 64))
    zapisz_ico(ik, os.path.join(KATALOG, "assets", "ikona.ico"))
    pygame.image.save(ik, os.path.join(KATALOG, "assets", "ikona.png"))
    print("Grafiki:", len(spr) + 6)
    if "--bez-dzwiekow" not in sys.argv:
        generuj_dzwieki()
        print("Dźwięki: gotowe")


if __name__ == "__main__":
    main()
