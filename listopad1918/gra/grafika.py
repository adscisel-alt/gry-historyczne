"""Proceduralna grafika w stylu pocztówek i fotografii z 1918 r.

Wszystko jest generowane kodem: tła lokacji, papierowe sylwetki-wycinanki,
ikony przedmiotów, ziarno filmu, winieta, ramki pocztówek i elementy UI.
Tła są po narysowaniu „tonowane” (skala szarości × kolor sepii), więc
zawsze zachowują ciepłą, brązową tonację.
"""
import math
import random

import pygame

from .config import W, SCENA_H, sep, sepa, FIOLET, FIOLET_JASNY, CZERWIEN_STEMPLA, PAPIER
from . import czcionki
from .dane import fakty as F
from .dane import postacie as P

_cache = {}

TON_SEPII = (255, 228, 186)   # mnożnik tonowania


# ============================================================ narzędzia podstawowe
def lerp(a, b, t):
    return a + (b - a) * t


def gradient(s, rect, v1, v2, poziomy=False):
    x, y, w, h = rect
    n = w if poziomy else h
    for i in range(max(1, n)):
        c = sep(lerp(v1, v2, i / max(1, n - 1)))
        if poziomy:
            pygame.draw.line(s, c, (x + i, y), (x + i, y + h - 1))
        else:
            pygame.draw.line(s, c, (x, y + i), (x + w - 1, y + i))


def tonuj(s):
    """Szarość × kolor sepii — gwarantuje jednolitą tonację całego obrazu."""
    try:
        g = pygame.transform.grayscale(s)
    except AttributeError:  # starsze pygame
        g = s.copy()
    g.fill(TON_SEPII, special_flags=pygame.BLEND_RGB_MULT)
    return g


def zmiekcz(s, stopien=2):
    w, h = s.get_size()
    m = pygame.transform.smoothscale(s, (max(1, w // stopien), max(1, h // stopien)))
    return pygame.transform.smoothscale(m, (w, h))


def kafel_szumu(rozmiar=256, sila=26, seed=1):
    klucz = ("szum", rozmiar, sila, seed)
    if klucz in _cache:
        return _cache[klucz]
    rng = random.Random(seed)
    s = pygame.Surface((rozmiar, rozmiar), pygame.SRCALPHA)
    s.lock()
    for y in range(rozmiar):
        for x in range(rozmiar):
            v = rng.randint(0, 255)
            a = rng.randint(0, sila)
            s.set_at((x, y), (v, v, v, a))
    s.unlock()
    _cache[klucz] = s
    return s


def naloz_kafel(cel, kafel, dx=0, dy=0):
    w, h = cel.get_size()
    kw, kh = kafel.get_size()
    for y in range(-kh + (dy % kh), h, kh):
        for x in range(-kw + (dx % kw), w, kw):
            cel.blit(kafel, (x, y))


def winieta(w, h, sila=170):
    klucz = ("winieta", w, h, sila)
    if klucz in _cache:
        return _cache[klucz]
    mw, mh = 96, 54
    m = pygame.Surface((mw, mh), pygame.SRCALPHA)
    for y in range(mh):
        for x in range(mw):
            dx = (x - mw / 2) / (mw / 2)
            dy = (y - mh / 2) / (mh / 2)
            d = math.sqrt(dx * dx * 0.9 + dy * dy * 1.1)
            a = max(0.0, min(1.0, (d - 0.55) / 0.75)) ** 1.6
            m.set_at((x, y), (30, 18, 8, int(a * sila)))
    s = pygame.transform.smoothscale(m, (w, h))
    _cache[klucz] = s
    return s


def papier(w, h, ton=226, seed=3, wlokna=True):
    """Tekstura starego papieru."""
    klucz = ("papier", w, h, ton, seed, wlokna)
    if klucz in _cache:
        return _cache[klucz]
    rng = random.Random(seed)
    s = pygame.Surface((w, h))
    s.fill(sep(ton))
    # plamy
    for _ in range(max(4, w * h // 9000)):
        r = rng.randint(10, 60)
        x, y = rng.randint(0, w), rng.randint(0, h)
        pl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(pl, sepa(ton - rng.randint(8, 22), rng.randint(15, 40)), pl.get_rect())
        s.blit(pl, (x - r, y - r))
    if wlokna:
        for _ in range(max(10, w * h // 2500)):
            x, y = rng.randint(0, w), rng.randint(0, h)
            dl = rng.randint(3, 14)
            k = rng.uniform(0, math.pi)
            pygame.draw.line(s, sep(ton - rng.randint(10, 30)), (x, y),
                             (x + int(math.cos(k) * dl), y + int(math.sin(k) * dl)))
    naloz_kafel(s, kafel_szumu(128, 30, seed + 7))
    _cache[klucz] = s
    return s


def rysy(s, rng, n=6):
    """Zarysowania kliszy."""
    w, h = s.get_size()
    for _ in range(n):
        x = rng.randint(0, w)
        y0 = rng.randint(0, h // 2)
        dl = rng.randint(h // 4, h)
        pygame.draw.line(s, sep(rng.choice([235, 245, 60])), (x, y0), (x + rng.randint(-6, 6), min(h, y0 + dl)), 1)
    for _ in range(n * 6):
        x, y = rng.randint(0, w), rng.randint(0, h)
        pygame.draw.circle(s, sep(rng.choice([240, 40])), (x, y), rng.randint(1, 2))


def fotoroki(s, rozmiar=34):
    """Narożniki fotograficzne jak w albumie."""
    w, h = s.get_size()
    c = sep(28)
    pygame.draw.polygon(s, c, [(0, 0), (rozmiar, 0), (0, rozmiar)])
    pygame.draw.polygon(s, c, [(w, 0), (w - rozmiar, 0), (w, rozmiar)])
    pygame.draw.polygon(s, c, [(0, h), (rozmiar, h), (0, h - rozmiar)])
    pygame.draw.polygon(s, c, [(w, h), (w - rozmiar, h), (w, h - rozmiar)])


def tekst(s, napis, poz, rozmiar=18, v=30, czcionka="szeryf", srodek=False, kolor=None):
    f = czcionki.f(czcionka, rozmiar)
    obraz = f.render(napis, True, kolor or sep(v))
    r = obraz.get_rect()
    if srodek:
        r.center = poz
    else:
        r.topleft = poz
    s.blit(obraz, r)
    return r


# ============================================================ prymitywy scenerii
def chmury(s, rng, y0, y1, n=7, v=235):
    for _ in range(n):
        cx = rng.randint(-50, W + 50)
        cy = rng.randint(y0, y1)
        for _ in range(rng.randint(4, 8)):
            r = rng.randint(18, 50)
            pl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(pl, sepa(v, 90), pl.get_rect())
            s.blit(pl, (cx + rng.randint(-70, 70) - r, cy + rng.randint(-15, 15) - r))


def kamienica(s, x, w, h, ziemia, rng, v=150, dach="spadzisty"):
    top = ziemia - h
    pygame.draw.rect(s, sep(v), (x, top, w, h))
    pygame.draw.rect(s, sep(v - 30), (x, top, w, h), 2)
    # gzyms
    pygame.draw.rect(s, sep(v + 25), (x - 4, top - 6, w + 8, 8))
    # okna
    kolumny = max(2, w // 38)
    rzedy = max(2, (h - 40) // 52)
    ow = int(w / kolumny * 0.5)
    for r in range(rzedy):
        for k in range(kolumny):
            ox = x + int((k + 0.25) * w / kolumny)
            oy = top + 20 + r * 52
            if oy + 34 > ziemia - 10:
                continue
            ciemne = rng.random() < 0.75
            pygame.draw.rect(s, sep(55 if ciemne else 215), (ox, oy, ow, 32))
            pygame.draw.line(s, sep(v + 20), (ox + ow // 2, oy), (ox + ow // 2, oy + 32), 2)
            pygame.draw.rect(s, sep(v + 30), (ox - 2, oy + 32, ow + 4, 4))
    # dach
    if dach == "spadzisty":
        pygame.draw.polygon(s, sep(v - 50), [(x - 6, top - 6), (x + w + 6, top - 6), (x + w - 20, top - 40), (x + 20, top - 40)])
        for _ in range(rng.randint(1, 3)):
            kx = rng.randint(x + 25, x + w - 30)
            pygame.draw.rect(s, sep(v - 60), (kx, top - 58, 12, 22))
    elif dach == "attyka":
        for i in range(x, x + w, 18):
            pygame.draw.rect(s, sep(v + 10), (i, top - 22, 10, 16))
    # drzwi
    pygame.draw.rect(s, sep(40), (x + w // 2 - 14, ziemia - 46, 28, 46))
    pygame.draw.ellipse(s, sep(40), (x + w // 2 - 14, ziemia - 58, 28, 24))


def bruk(s, y, rng, v=120, do=SCENA_H):
    pygame.draw.rect(s, sep(v), (0, y, W, do - y))
    wiersz = 0
    yy = y
    while yy < do:
        wys = 6 + wiersz * 1.6
        szer = 14 + wiersz * 4
        off = (wiersz % 2) * szer / 2
        xx = -off
        while xx < W:
            pygame.draw.ellipse(s, sep(v + rng.randint(-25, 22)), (xx + 1, yy + 1, szer - 2, wys - 1))
            xx += szer
        yy += wys
        wiersz += 1


def latarnia(s, x, ziemia, wys=230, swieci=False):
    pygame.draw.rect(s, sep(35), (x - 3, ziemia - wys, 6, wys))
    pygame.draw.rect(s, sep(35), (x - 9, ziemia - 12, 18, 12))
    pygame.draw.polygon(s, sep(35), [(x - 14, ziemia - wys), (x + 14, ziemia - wys), (x + 9, ziemia - wys - 30), (x - 9, ziemia - wys - 30)])
    pygame.draw.polygon(s, sep(240 if swieci else 190), [(x - 10, ziemia - wys - 2), (x + 10, ziemia - wys - 2), (x + 7, ziemia - wys - 26), (x - 7, ziemia - wys - 26)])
    pygame.draw.polygon(s, sep(30), [(x - 16, ziemia - wys - 30), (x + 16, ziemia - wys - 30), (x, ziemia - wys - 44)])
    if swieci:
        pl = pygame.Surface((240, 240), pygame.SRCALPHA)
        for r in range(120, 0, -8):
            pygame.draw.circle(pl, sepa(250, 7), (120, 120), r)
        s.blit(pl, (x - 120, ziemia - wys - 135))


def drzewo(s, x, ziemia, h, rng, v=70):
    pygame.draw.polygon(s, sep(v - 30), [(x - 7, ziemia), (x + 7, ziemia), (x + 4, ziemia - h * 0.55), (x - 4, ziemia - h * 0.55)])
    for _ in range(14):
        r = rng.randint(int(h * 0.12), int(h * 0.22))
        cx = x + rng.randint(-int(h * 0.25), int(h * 0.25))
        cy = ziemia - h * 0.6 + rng.randint(-int(h * 0.3), int(h * 0.15))
        pygame.draw.circle(s, sep(v + rng.randint(-15, 20)), (int(cx), int(cy)), r)


def tlum(s, rng, n, ziemia, wys=(50, 80), v=(50, 90), x0=0, x1=W):
    for _ in range(n):
        x = rng.randint(x0, x1)
        h = rng.randint(*wys)
        c = sep(rng.randint(*v))
        pygame.draw.ellipse(s, c, (x - h * 0.16, ziemia - h, h * 0.32, h * 0.3))
        pygame.draw.polygon(s, c, [(x - h * 0.2, ziemia), (x + h * 0.2, ziemia), (x + h * 0.14, ziemia - h * 0.72), (x - h * 0.14, ziemia - h * 0.72)])
        if rng.random() < 0.6:
            pygame.draw.ellipse(s, c, (x - h * 0.2, ziemia - h - 3, h * 0.4, h * 0.1))
            pygame.draw.rect(s, c, (x - h * 0.12, ziemia - h - h * 0.12, h * 0.24, h * 0.12))


def flaga_pl(s, x, y, w=60, h=38, maszt=True):
    if maszt:
        pygame.draw.line(s, sep(40), (x, y - 10), (x, y + h + 120), 3)
    fala = [(x + i, y + int(math.sin(i / 9) * 3)) for i in range(0, w + 1, 4)]
    gora = fala + [(px, py + h // 2) for px, py in reversed(fala)]
    dol = [(px, py + h // 2) for px, py in fala] + [(px, py + h) for px, py in reversed(fala)]
    pygame.draw.polygon(s, sep(245), gora)
    pygame.draw.polygon(s, sep(95), dol)  # czerwień w sepii = średni ton
    pygame.draw.lines(s, sep(60), False, fala, 1)


def wnetrze(s, sciana=150, podloga=95, lamperia=True, horyzont=420):
    gradient(s, (0, 0, W, horyzont), sciana + 15, sciana - 20)
    if lamperia:
        pygame.draw.rect(s, sep(sciana - 45), (0, horyzont - 110, W, 110))
        for x in range(0, W, 80):
            pygame.draw.rect(s, sep(sciana - 30), (x + 10, horyzont - 98, 60, 86), 2)
        pygame.draw.rect(s, sep(sciana - 10), (0, horyzont - 116, W, 8))
    # podłoga w perspektywie
    gradient(s, (0, horyzont, W, SCENA_H - horyzont), podloga, podloga - 35)
    for i in range(-20, 21):
        x0 = W / 2 + i * 40
        x1 = W / 2 + i * 120
        pygame.draw.line(s, sep(podloga - 30), (x0, horyzont), (x1, SCENA_H), 1)
    for k in range(1, 8):
        y = horyzont + (SCENA_H - horyzont) * (k / 8) ** 1.4
        pygame.draw.line(s, sep(podloga - 25), (0, y), (W, y), 1)


def okno(s, rect, widok_v=210, szprosy=True, noc=False):
    x, y, w, h = rect
    pygame.draw.rect(s, sep(60), (x - 8, y - 8, w + 16, h + 16))
    gradient(s, rect, 60 if noc else widok_v, (90 if noc else widok_v - 30))
    if szprosy:
        pygame.draw.line(s, sep(70), (x + w // 2, y), (x + w // 2, y + h), 5)
        pygame.draw.line(s, sep(70), (x, y + h // 3), (x + w, y + h // 3), 5)
    pygame.draw.rect(s, sep(200), (x - 12, y + h + 6, w + 24, 8))


def drzwi(s, rect, v=70):
    x, y, w, h = rect
    pygame.draw.rect(s, sep(v), rect)
    pygame.draw.rect(s, sep(v - 30), rect, 4)
    pygame.draw.rect(s, sep(v + 20), (x + 12, y + 14, w - 24, h // 2 - 24), 3)
    pygame.draw.rect(s, sep(v + 20), (x + 12, y + h // 2 + 4, w - 24, h // 2 - 22), 3)
    pygame.draw.circle(s, sep(210), (x + w - 18, y + h // 2), 5)


def regal(s, rect, rng, v=80):
    x, y, w, h = rect
    pygame.draw.rect(s, sep(v), rect)
    polki = max(2, h // 70)
    for p in range(polki):
        py = y + 8 + p * (h - 10) // polki
        xx = x + 6
        while xx < x + w - 14:
            bw = rng.randint(8, 22)
            bh = rng.randint(38, 58)
            pygame.draw.rect(s, sep(rng.randint(60, 200)), (xx, py + (62 - bh), bw, bh))
            xx += bw + rng.randint(0, 3)
        pygame.draw.rect(s, sep(v - 30), (x, py + 62, w, 6))
    pygame.draw.rect(s, sep(v - 40), rect, 4)


def biurko(s, rect, v=75):
    x, y, w, h = rect
    pygame.draw.rect(s, sep(v + 20), (x - 10, y, w + 20, 14))
    pygame.draw.rect(s, sep(v), (x, y + 14, w, h - 14))
    pygame.draw.rect(s, sep(v - 25), (x + 10, y + 26, w // 3, h // 3), 2)
    pygame.draw.rect(s, sep(v - 25), (x + w - w // 3 - 10, y + 26, w // 3, h // 3), 2)


def zyrandol(s, x, y, v=200):
    pygame.draw.line(s, sep(60), (x, 0), (x, y), 2)
    pygame.draw.ellipse(s, sep(v - 60), (x - 70, y, 140, 26))
    for i in range(-3, 4):
        px = x + i * 20
        pygame.draw.line(s, sep(v - 60), (x, y + 10), (px, y + 36), 2)
        pygame.draw.circle(s, sep(245), (px, y + 40), 6)
    pl = pygame.Surface((300, 200), pygame.SRCALPHA)
    for r in range(140, 0, -10):
        pygame.draw.ellipse(pl, sepa(250, 6), (150 - r, 100 - r * 0.6, r * 2, r * 1.2))
    s.blit(pl, (x - 150, y - 60))


def plakat(s, rect, rng, napis="", v=215):
    x, y, w, h = rect
    pygame.draw.rect(s, sep(v), rect)
    pygame.draw.rect(s, sep(v - 60), rect, 2)
    if napis:
        tekst(s, napis, (x + w // 2, y + 24), min(26, max(12, w // 9)), 35, "plakat", srodek=True)
    for i in range(5):
        ly = y + 50 + i * ((h - 60) // 6)
        pygame.draw.line(s, sep(v - 70), (x + 10, ly), (x + w - 10 - rng.randint(0, w // 3), ly), 2)


def lokomotywa(s, x, ziemia, v=40):
    pygame.draw.rect(s, sep(v), (x, ziemia - 150, 300, 110))
    pygame.draw.rect(s, sep(v + 15), (x + 210, ziemia - 210, 90, 170))
    pygame.draw.rect(s, sep(200), (x + 225, ziemia - 195, 30, 30))
    pygame.draw.rect(s, sep(v), (x + 40, ziemia - 220, 34, 70))
    pygame.draw.ellipse(s, sep(v - 10), (x + 30, ziemia - 232, 54, 16))
    for i, r in enumerate((44, 44, 44)):
        cx = x + 60 + i * 90
        pygame.draw.circle(s, sep(25), (cx, ziemia - 40), r)
        pygame.draw.circle(s, sep(90), (cx, ziemia - 40), r - 8, 3)
        pygame.draw.circle(s, sep(90), (cx, ziemia - 40), 6)
    pygame.draw.line(s, sep(120), (x + 60, ziemia - 40), (x + 240, ziemia - 40), 5)
    # para
    rng = random.Random(x)
    for i in range(16):
        r = 20 + i * 6
        pl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(pl, sepa(235, 70 - i * 3), (r, r), r)
        s.blit(pl, (x + 57 - r + i * 14 + rng.randint(-8, 8), ziemia - 250 - r - i * 14))


def mapa(s, rect, ton_tla=215, nazwy=True, miasta=True, podpisy_miast=True, rozmieszczone=None):
    """Mapa trzech zaborów — używana na ścianie archiwum, w minigrze i w dzienniku."""
    x, y, w, h = rect
    pygame.draw.rect(s, sep(ton_tla), rect)
    sx = w / (27.4 - 13.8)
    sy = h / (55.6 - 48.1)
    for z in F.ZABORY.values():
        pts = [F.rzut(lon, lat, x, y, sx, sy) for lon, lat in z["punkty"]]
        pygame.draw.polygon(s, sep(z["ton"]), pts)
        pygame.draw.polygon(s, sep(40), pts, 2)
    if nazwy and w > 300:
        for klucz, (lon, lat) in {"rosyjski": (23.6, 53.0), "pruski": (16.2, 53.6), "austriacki": (22.6, 49.55)}.items():
            px, py = F.rzut(lon, lat, x, y, sx, sy)
            tekst(s, F.ZABORY[klucz]["nazwa"].upper(), (px, py), max(11, w // 45), 25, "plakat", srodek=True)
    if miasta:
        for nazwa, ((lon, lat), _) in F.MIASTA.items():
            if rozmieszczone is not None and nazwa not in rozmieszczone:
                continue
            px, py = F.rzut(lon, lat, x, y, sx, sy)
            pygame.draw.circle(s, sep(20), (int(px), int(py)), max(3, w // 120))
            if podpisy_miast and w > 300:
                tekst(s, nazwa, (px + 7, py - 8), max(11, w // 50), 15)
    pygame.draw.rect(s, sep(40), rect, 3)
    return sx, sy


# ============================================================ tła lokacji
def _tlo_archiwum(s, rng):
    wnetrze(s, 95, 70, horyzont=430)
    regal(s, (20, 40, 240, 390), rng, 60)
    regal(s, (1010, 260, 250, 170), rng, 60)
    # półka z lupą
    pygame.draw.rect(s, sep(70), (280, 262, 130, 10))
    # mapa na ścianie
    pygame.draw.rect(s, sep(45), (1030, 80, 220, 170))
    mapa(s, (1040, 90, 200, 150), 200, nazwy=False, podpisy_miast=False)
    # biurko + szuflady
    pygame.draw.rect(s, sep(85), (480, 300, 260, 140))
    for i in range(3):
        pygame.draw.rect(s, sep(110), (520, 312 + i * 34, 180, 28))
        pygame.draw.rect(s, sep(200), (600, 322 + i * 34, 20, 6))
    pygame.draw.rect(s, sep(120), (470, 290, 280, 14))
    # stereoskop na statywie
    pygame.draw.line(s, sep(50), (815, 440), (815, 330), 6)
    pygame.draw.line(s, sep(50), (815, 440), (780, 470), 5)
    pygame.draw.line(s, sep(50), (815, 440), (850, 470), 5)
    pygame.draw.rect(s, sep(90), (770, 270, 90, 60), border_radius=10)
    pygame.draw.circle(s, sep(30), (795, 300), 14)
    pygame.draw.circle(s, sep(30), (835, 300), 14)
    pygame.draw.rect(s, sep(210), (860, 260, 20, 80))
    # lampa i snop światła
    pygame.draw.polygon(s, sep(60), [(600, 230), (660, 230), (645, 200), (615, 200)])
    pygame.draw.line(s, sep(60), (630, 230), (630, 290), 4)
    pl = pygame.Surface((W, SCENA_H), pygame.SRCALPHA)
    pygame.draw.polygon(pl, sepa(250, 40), [(605, 230), (655, 230), (900, 540), (360, 540)])
    s.blit(pl, (0, 0))
    # stosy teczek
    for i in range(5):
        pygame.draw.rect(s, sep(150 + i * 10), (300, 400 - i * 14, 140, 14))
        pygame.draw.rect(s, sep(90), (300, 400 - i * 14, 140, 14), 1)
    tekst(s, "ARCHIWUM", (140, 470), 22, 200, "plakat", srodek=True)


def _tlo_krakow(s, rng):
    gradient(s, (0, 0, W, 420), 225, 185)
    chmury(s, rng, 20, 140)
    for i in range(6):
        kamienica(s, 360 + i * 105, 100, 230 + rng.randint(-20, 40), 420, rng, 150 + rng.randint(-15, 15))
    # Kościół Mariacki — dwie nierówne wieże
    pygame.draw.rect(s, sep(95), (1000, 120, 220, 300))
    pygame.draw.polygon(s, sep(75), [(990, 120), (1230, 120), (1110, 40)])
    pygame.draw.rect(s, sep(88), (1010, 40, 70, 380))     # wyższa
    pygame.draw.polygon(s, sep(60), [(1005, 40), (1085, 40), (1045, -40)])
    for dx in (1005, 1080):
        pygame.draw.polygon(s, sep(60), [(dx - 6, 44), (dx + 6, 44), (dx, 10)])
    pygame.draw.rect(s, sep(88), (1150, 70, 66, 350))     # niższa
    pygame.draw.ellipse(s, sep(60), (1150, 40, 66, 60))
    pygame.draw.rect(s, sep(60), (1180, 14, 6, 30))
    for wx in (1030, 1170):
        for wy in range(110, 380, 60):
            pygame.draw.rect(s, sep(40), (wx, wy, 24, 40))
            pygame.draw.ellipse(s, sep(40), (wx, wy - 10, 24, 20))
    pygame.draw.rect(s, sep(45), (1095, 200, 50, 140))
    pygame.draw.ellipse(s, sep(45), (1095, 180, 50, 50))
    # Sukiennice
    pygame.draw.rect(s, sep(185), (40, 230, 330, 190))
    pygame.draw.polygon(s, sep(110), [(40, 230), (370, 230), (350, 200), (60, 200)])
    for i in range(40, 370, 22):
        pygame.draw.polygon(s, sep(200), [(i, 200), (i + 12, 200), (i + 6, 172)])
    for i in range(6):
        ax = 55 + i * 52
        pygame.draw.rect(s, sep(55), (ax, 330, 38, 90))
        pygame.draw.ellipse(s, sep(55), (ax, 312, 38, 40))
    flaga_pl(s, 205, 150, 70, 40)
    bruk(s, 420, rng, 135)
    # słup ogłoszeniowy
    pygame.draw.rect(s, sep(160), (440, 180, 90, 300))
    pygame.draw.ellipse(s, sep(110), (432, 168, 106, 26))
    pygame.draw.polygon(s, sep(90), [(436, 176), (534, 176), (485, 140)])
    for i, py in enumerate((200, 280, 360)):
        plakat(s, (450, py, 70, 70), rng, "", 215 - i * 15)
    pygame.draw.rect(s, sep(110), (440, 470, 90, 10))
    # ławka
    pygame.draw.rect(s, sep(80), (580, 470, 160, 12))
    pygame.draw.rect(s, sep(80), (590, 482, 10, 30))
    pygame.draw.rect(s, sep(80), (720, 482, 10, 30))
    tlum(s, rng, 22, 425, (40, 60), (50, 100), 330, 980)
    latarnia(s, 940, 470, 200)


def _tlo_harcowka(s, rng):
    wnetrze(s, 165, 110)
    for x in range(0, W, 26):
        pygame.draw.line(s, sep(150), (x, 0), (x, 300), 1)
    okno(s, (560, 70, 200, 170), 220)
    # hak
    pygame.draw.rect(s, sep(60), (350, 210, 30, 8))
    pygame.draw.line(s, sep(60), (365, 218), (365, 236), 3)
    # stół
    biurko(s, (480, 370, 180, 80), 95)
    for i in range(3):
        pygame.draw.rect(s, sep(225 - i * 10), (500 + i * 40, 352 - i * 3, 60, 18))
    # proporzec z lilijką
    pygame.draw.line(s, sep(50), (1010, 70), (1010, 300), 4)
    pygame.draw.polygon(s, sep(220), [(1012, 80), (1160, 130), (1012, 200)])
    cx, cy = 1060, 140
    pygame.draw.polygon(s, sep(70), [(cx, cy - 35), (cx - 8, cy - 5), (cx, cy + 25), (cx + 8, cy - 5)])
    pygame.draw.ellipse(s, sep(70), (cx - 28, cy - 15, 22, 30))
    pygame.draw.ellipse(s, sep(70), (cx + 6, cy - 15, 22, 30))
    pygame.draw.rect(s, sep(70), (cx - 22, cy + 8, 44, 6))
    # tablica z węzłami
    pygame.draw.rect(s, sep(90), (150, 90, 160, 110))
    for i in range(3):
        pygame.draw.circle(s, sep(220), (185 + i * 45, 145), 12, 3)
    tekst(s, "WĘZŁY", (230, 100), 16, 220, "plakat", srodek=True)
    drzwi(s, (1160, 300, 100, 210), 80)
    # ławki
    pygame.draw.rect(s, sep(80), (120, 440, 260, 16))
    pygame.draw.rect(s, sep(80), (820, 440, 260, 16))
    plakat(s, (800, 90, 140, 170), rng, "CZUWAJ!", 220)


def _tlo_palac(s, rng):
    wnetrze(s, 185, 120, horyzont=430)
    for x in (80, 400, 880, 1200):
        pygame.draw.rect(s, sep(205), (x - 20, 0, 40, 330))
        pygame.draw.rect(s, sep(165), (x - 26, 300, 52, 20))
    okno(s, (130, 60, 180, 230), 225)
    okno(s, (950, 60, 180, 230), 225)
    # jaśniejszy prostokąt po portrecie
    pygame.draw.rect(s, sep(208), (570, 70, 140, 130))
    pygame.draw.line(s, sep(120), (640, 40), (600, 70), 1)
    pygame.draw.line(s, sep(120), (640, 40), (680, 70), 1)
    pygame.draw.circle(s, sep(90), (640, 40), 4)
    zyrandol(s, 640, 220)
    # dywan
    pygame.draw.polygon(s, sep(95), [(380, 440), (900, 440), (1050, 560), (230, 560)])
    pygame.draw.polygon(s, sep(130), [(410, 450), (870, 450), (1000, 552), (280, 552)], 3)
    # stół obrad
    pygame.draw.rect(s, sep(70), (520, 370, 400, 22))
    pygame.draw.rect(s, sep(60), (540, 392, 12, 60))
    pygame.draw.rect(s, sep(60), (890, 392, 12, 60))
    for i in range(6):
        pygame.draw.rect(s, sep(235), (560 + i * 55, 362, 34, 10))
    drzwi(s, (1150, 260, 110, 250), 90)


def _tlo_lublin_palac(s, rng):
    wnetrze(s, 120, 80)
    okno(s, (90, 70, 180, 230), noc=True)
    for i in range(5):
        pygame.draw.circle(s, sep(240), (110 + i * 35, 230 + (i % 2) * 20), 3)
    regal(s, (330, 90, 200, 260), rng, 70)
    pygame.draw.rect(s, sep(75), (560, 380, 300, 20))
    for i in range(8):
        pygame.draw.rect(s, sep(230), (580 + i * 32 + rng.randint(-4, 4), 372, 26, 10))
    for cx in (600, 830):
        pygame.draw.rect(s, sep(235), (cx, 340, 8, 32))
        pl = pygame.Surface((160, 160), pygame.SRCALPHA)
        for r in range(80, 0, -8):
            pygame.draw.circle(pl, sepa(250, 9), (80, 80), r)
        s.blit(pl, (cx - 76, 260))
        pygame.draw.ellipse(s, sep(250), (cx, 330, 8, 12))
    plakat(s, (900, 80, 180, 220), rng, "REPUBLIKA", 220)
    drzwi(s, (1160, 300, 100, 210), 70)


def _tlo_drukarnia(s, rng):
    pygame.draw.rect(s, sep(110), (0, 0, W, 430))
    for y in range(0, 430, 22):
        off = 0 if (y // 22) % 2 else 30
        for x in range(-off, W, 60):
            pygame.draw.rect(s, sep(100 + rng.randint(-12, 12)), (x + 1, y + 1, 58, 20))
    gradient(s, (0, 430, W, 130), 80, 55)
    plakat(s, (60, 80, 90, 130), rng, "MĄKA", 200)
    plakat(s, (160, 100, 90, 120), rng, "NAFTA", 210)
    # sznurek z odbitkami
    pygame.draw.line(s, sep(60), (300, 60), (1100, 80), 2)
    for i in range(9):
        px = 320 + i * 85
        py = 60 + i * 2
        pygame.draw.rect(s, sep(230), (px, py, 50, 70))
        for k in range(5):
            pygame.draw.line(s, sep(150), (px + 6, py + 12 + k * 11), (px + 44, py + 12 + k * 11), 1)
    # kaszta
    pygame.draw.rect(s, sep(80), (300, 270, 260, 140))
    for r in range(4):
        for k in range(8):
            pygame.draw.rect(s, sep(50 + rng.randint(0, 30)), (308 + k * 31, 278 + r * 32, 27, 27))
    pygame.draw.rect(s, sep(70), (310, 410, 14, 60))
    pygame.draw.rect(s, sep(70), (536, 410, 14, 60))
    # prasa
    pygame.draw.rect(s, sep(45), (600, 220, 180, 210))
    pygame.draw.rect(s, sep(60), (590, 200, 200, 30))
    pygame.draw.rect(s, sep(90), (620, 300, 140, 20))
    pygame.draw.circle(s, sep(35), (800, 300), 70, 8)
    for k in range(8):
        a = k * math.pi / 4
        pygame.draw.line(s, sep(35), (800, 300), (800 + math.cos(a) * 66, 300 + math.sin(a) * 66), 4)
    pygame.draw.rect(s, sep(40), (590, 430, 200, 40))
    drzwi(s, (30, 330, 90, 180), 70)
    latarnia_wn = pygame.Surface((300, 300), pygame.SRCALPHA)
    for r in range(150, 0, -10):
        pygame.draw.circle(latarnia_wn, sepa(250, 5), (150, 150), r)
    s.blit(latarnia_wn, (550, 50))


def _tlo_wagon(s, rng):
    gradient(s, (0, 0, W, SCENA_H), 120, 70)
    for x in range(0, W, 40):
        pygame.draw.line(s, sep(100), (x, 0), (x, 360), 1)
    for wx in (120, 540, 900):
        okno(s, (wx, 90, 190, 170), noc=True, szprosy=False)
        # nocny krajobraz
        pygame.draw.polygon(s, sep(40), [(wx, 220), (wx + 60, 200), (wx + 120, 215), (wx + 190, 195), (wx + 190, 260), (wx, 260)])
        pygame.draw.circle(s, sep(235), (wx + 150, 120), 14)
        for _ in range(6):
            pygame.draw.circle(s, sep(220), (wx + rng.randint(5, 185), 100 + rng.randint(0, 70)), 1)
    # półki bagażowe
    pygame.draw.rect(s, sep(55), (0, 40, W, 10))
    for x in range(0, W, 24):
        pygame.draw.line(s, sep(55), (x, 50), (x + 10, 70), 1)
    pygame.draw.rect(s, sep(55), (0, 70, W, 4))
    pygame.draw.rect(s, sep(200), (150, 20, 120, 20))
    # ławki
    for bx in (60, 360):
        pygame.draw.rect(s, sep(85), (bx, 300, 250, 120))
        pygame.draw.rect(s, sep(100), (bx, 400, 260, 40))
        for k in range(10):
            pygame.draw.line(s, sep(70), (bx + k * 25, 300), (bx + k * 25, 420), 1)
    gradient(s, (0, 440, W, 120), 60, 40)
    drzwi(s, (1160, 160, 100, 340), 75)
    tekst(s, "WARSZAWA →", (1160, 130), 18, 230, "plakat")


def _tlo_dworzec(s, rng):
    gradient(s, (0, 0, W, 420), 205, 160)
    # stalowe łuki
    for i in range(7):
        cx = i * 220
        pygame.draw.arc(s, sep(60), (cx - 220, -120, 440, 360), 0, math.pi, 6)
    for x in range(0, W, 110):
        pygame.draw.line(s, sep(90), (x, 0), (x, 120), 1)
    for x in range(0, W, 220):
        pygame.draw.rect(s, sep(55), (x - 8, 100, 16, 330))
    # zegar
    pygame.draw.circle(s, sep(230), (660, 80), 56)
    pygame.draw.circle(s, sep(40), (660, 80), 56, 5)
    for k in range(12):
        a = k * math.pi / 6
        pygame.draw.line(s, sep(40), (660 + math.cos(a) * 44, 80 + math.sin(a) * 44), (660 + math.cos(a) * 50, 80 + math.sin(a) * 50), 3)
    pygame.draw.line(s, sep(30), (660, 80), (660, 38), 4)
    pygame.draw.line(s, sep(30), (660, 80), (632, 80), 5)
    lokomotywa(s, -40, 430)
    pygame.draw.rect(s, sep(100), (0, 430, W, 130))
    pygame.draw.rect(s, sep(200), (0, 430, W, 6))
    # bramka
    pygame.draw.rect(s, sep(55), (340, 210, 12, 290))
    pygame.draw.rect(s, sep(55), (490, 210, 12, 290))
    pygame.draw.rect(s, sep(55), (340, 210, 162, 26))
    tekst(s, "PERRON", (421, 214), 18, 230, "plakat", srodek=False)
    for x in range(352, 490, 16):
        pygame.draw.line(s, sep(70), (x, 330), (x, 500), 3)
    pygame.draw.line(s, sep(70), (352, 330), (490, 330), 4)
    tlum(s, rng, 30, 440, (55, 85), (40, 85), 540, 1270)
    flaga_pl(s, 1180, 170, 60, 36)


def _tlo_koszary(s, rng):
    gradient(s, (0, 0, W, 420), 80, 115)
    for _ in range(70):
        pygame.draw.circle(s, sep(230), (rng.randint(0, W), rng.randint(0, 200)), 1)
    pygame.draw.circle(s, sep(235), (180, 80), 32)
    # mury koszar
    pygame.draw.rect(s, sep(95), (0, 140, W, 290))
    for y in range(140, 430, 18):
        off = 0 if (y // 18) % 2 else 22
        for x in range(-off, W, 44):
            pygame.draw.rect(s, sep(85 + rng.randint(-10, 10)), (x + 1, y + 1, 42, 16))
    for x in range(40, W, 140):
        if 600 < x < 860:
            continue
        pygame.draw.rect(s, sep(45), (x, 190, 50, 70))
        pygame.draw.ellipse(s, sep(45), (x, 172, 50, 40))
        if rng.random() < 0.4:
            pygame.draw.rect(s, sep(220), (x + 6, 200, 38, 54))
    # brama
    pygame.draw.rect(s, sep(60), (620, 70, 220, 360))
    pygame.draw.rect(s, sep(35), (650, 170, 160, 260))
    pygame.draw.ellipse(s, sep(35), (650, 110, 160, 120))
    for x in range(660, 810, 20):
        pygame.draw.line(s, sep(70), (x, 160), (x, 430), 3)
    # niemiecki orzeł + kartka
    pygame.draw.polygon(s, sep(40), [(730, 80), (700, 100), (715, 125), (745, 125), (760, 100)])
    pygame.draw.rect(s, sep(230), (690, 128, 80, 24))
    tekst(s, "Wojsko Polskie", (730, 140), 12, 30, "szeryf", srodek=True)
    bruk(s, 430, rng, 90)
    # budka wartownika
    pygame.draw.polygon(s, sep(210), [(1010, 430), (1080, 430), (1080, 260), (1045, 230), (1010, 260)])
    for k in range(4):
        pygame.draw.polygon(s, sep(60), [(1010, 290 + k * 40), (1080, 290 + k * 40), (1080, 305 + k * 40), (1010, 305 + k * 40)])
    # stół sztabowy
    pygame.draw.rect(s, sep(75), (430, 360, 230, 16))
    pygame.draw.rect(s, sep(230), (450, 344, 190, 22))
    pygame.draw.rect(s, sep(60), (440, 376, 10, 80))
    pygame.draw.rect(s, sep(60), (640, 376, 10, 80))
    latarnia(s, 900, 470, 220, swieci=True)
    latarnia(s, 120, 470, 220, swieci=True)


def _tlo_plac_saski(s, rng):
    gradient(s, (0, 0, W, 420), 220, 180)
    chmury(s, rng, 10, 100, 5)
    # Pałac Saski z kolumnadą
    pygame.draw.rect(s, sep(175), (40, 100, 660, 320))
    pygame.draw.rect(s, sep(200), (240, 150, 260, 270))
    for i in range(9):
        cx = 255 + i * 30
        pygame.draw.rect(s, sep(225), (cx, 175, 16, 245))
        pygame.draw.rect(s, sep(210), (cx - 3, 168, 22, 10))
    pygame.draw.rect(s, sep(190), (230, 140, 280, 34))
    for k in range(2):
        for i in range(6):
            pygame.draw.rect(s, sep(70), (60 + i * 30 + k * 470, 150, 18, 34))
            pygame.draw.rect(s, sep(70), (60 + i * 30 + k * 470, 230, 18, 34))
    pygame.draw.rect(s, sep(150), (36, 92, 668, 12))
    flaga_pl(s, 370, 40, 70, 40)
    for x in (780, 900, 1020, 1150):
        drzewo(s, x, 420, 260, rng, 85)
    bruk(s, 420, rng, 140)
    latarnia(s, 740, 470, 220)
    tlum(s, rng, 26, 425, (40, 65), (60, 110), 0, W)


def _tlo_paryz_biuro(s, rng):
    wnetrze(s, 175, 105)
    okno(s, (80, 40, 230, 260), 225)
    # wieża Eiffla
    bx, by = 195, 290
    pygame.draw.polygon(s, sep(60), [(bx - 60, by), (bx - 8, by - 230), (bx + 8, by - 230), (bx + 60, by)], 0)
    pygame.draw.polygon(s, sep(215), [(bx - 30, by), (bx, by - 60), (bx + 30, by)])
    for k in range(1, 6):
        yy = by - k * 40
        pygame.draw.line(s, sep(215), (bx - 55 + k * 9, yy), (bx + 55 - k * 9, yy), 1)
    pygame.draw.line(s, sep(60), (bx, by - 230), (bx, by - 250), 2)
    regal(s, (360, 60, 220, 300), rng, 75)
    biurko(s, (370, 380, 300, 70), 70)
    for i in range(4):
        pygame.draw.rect(s, sep(215 - i * 12), (400 + i * 50, 366 - i * 2, 70, 16))
    # telegraf
    pygame.draw.rect(s, sep(60), (660, 360, 120, 60))
    pygame.draw.rect(s, sep(80), (650, 420, 140, 12))
    pygame.draw.circle(s, sep(200), (690, 350), 18)
    pygame.draw.circle(s, sep(40), (690, 350), 18, 3)
    pygame.draw.line(s, sep(40), (720, 360), (760, 330), 4)
    pygame.draw.rect(s, sep(230), (760, 330, 30, 80))
    # sztaluga
    pygame.draw.line(s, sep(60), (880, 520), (940, 120), 6)
    pygame.draw.line(s, sep(60), (1000, 520), (940, 120), 6)
    pygame.draw.line(s, sep(60), (940, 520), (940, 120), 5)
    drzwi(s, (1160, 300, 100, 210), 85)
    tekst(s, "COMITÉ NATIONAL POLONAIS", (640, 20), 20, 60, "plakat", srodek=True)


def _tlo_salon(s, rng):
    wnetrze(s, 200, 130, horyzont=440)
    for x in (300, 980):
        pygame.draw.rect(s, sep(160), (x - 70, 60, 140, 260))
        pygame.draw.rect(s, sep(230), (x - 56, 74, 112, 232))
        pygame.draw.rect(s, sep(130), (x - 70, 60, 140, 260), 6)
    zyrandol(s, 640, 160)
    # flagi: Francja, Wielka Brytania, USA (w tonach sepii)
    fx, fy = 50, 50
    for i, v in enumerate((70, 240, 110)):
        pygame.draw.rect(s, sep(v), (fx + i * 22, fy, 22, 44))
    ux, uy = 50, 110
    pygame.draw.rect(s, sep(70), (ux, uy, 66, 44))
    pygame.draw.line(s, sep(240), (ux, uy), (ux + 66, uy + 44), 8)
    pygame.draw.line(s, sep(240), (ux + 66, uy), (ux, uy + 44), 8)
    pygame.draw.line(s, sep(110), (ux, uy), (ux + 66, uy + 44), 3)
    pygame.draw.line(s, sep(110), (ux + 66, uy), (ux, uy + 44), 3)
    pygame.draw.rect(s, sep(240), (ux + 26, uy, 14, 44))
    pygame.draw.rect(s, sep(240), (ux, uy + 16, 66, 12))
    pygame.draw.rect(s, sep(110), (ux + 29, uy, 8, 44))
    pygame.draw.rect(s, sep(110), (ux, uy + 19, 66, 6))
    sx, sy = 50, 170
    for k in range(7):
        pygame.draw.rect(s, sep(110 if k % 2 == 0 else 240), (sx, sy + k * 6, 66, 6))
    pygame.draw.rect(s, sep(70), (sx, sy, 28, 24))
    for k in range(6):
        pygame.draw.circle(s, sep(240), (sx + 5 + (k % 3) * 9, sy + 6 + (k // 3) * 10), 2)
    for i in range(3):
        pygame.draw.line(s, sep(50), (48, 50 + i * 60), (48, 260), 2)
    # okrągły stół
    pygame.draw.ellipse(s, sep(80), (430, 420, 420, 70))
    pygame.draw.ellipse(s, sep(110), (440, 410, 400, 60))
    pygame.draw.rect(s, sep(70), (625, 470, 30, 70))
    for i in range(4):
        pygame.draw.rect(s, sep(235), (500 + i * 70, 425, 44, 14))


def _tlo_poznan(s, rng):
    gradient(s, (0, 0, W, 420), 215, 180)
    chmury(s, rng, 10, 90, 4)
    # Hotel Bazar
    pygame.draw.rect(s, sep(165), (620, 110, 640, 310))
    for k in range(4):
        for i in range(10):
            pygame.draw.rect(s, sep(60), (650 + i * 60, 150 + k * 65, 28, 44))
            pygame.draw.rect(s, sep(200), (646 + i * 60, 194 + k * 65, 36, 5))
    pygame.draw.rect(s, sep(130), (612, 100, 656, 14))
    tekst(s, "BAZAR", (940, 118), 22, 230, "plakat", srodek=True)
    pygame.draw.rect(s, sep(230), (900, 40, 300, 60))
    pygame.draw.rect(s, sep(60), (900, 40, 300, 60), 3)
    tekst(s, "KÖNIGLICHE POLIZEI", (1050, 58), 18, 30, "plakat", srodek=True)
    tekst(s, "jeszcze", (1150, 76), 14, 90, "reka")
    for i in range(3):
        kamienica(s, 20 + i * 200, 190, 250 + i * 20, 420, rng, 140 + i * 10)
    flaga_pl(s, 760, 40, 60, 34)
    bruk(s, 420, rng, 125)
    # tory i tramwaj
    pygame.draw.line(s, sep(60), (0, 500), (W, 500), 3)
    pygame.draw.line(s, sep(60), (0, 530), (W, 530), 3)
    pygame.draw.rect(s, sep(200), (40, 330, 300, 140), border_radius=12)
    pygame.draw.rect(s, sep(70), (40, 330, 300, 140), 4, border_radius=12)
    for i in range(5):
        pygame.draw.rect(s, sep(60), (56 + i * 56, 350, 44, 50))
    pygame.draw.line(s, sep(40), (190, 330), (230, 260), 3)
    pygame.draw.line(s, sep(40), (0, 260), (W, 255), 1)
    tekst(s, "6", (300, 410), 26, 30, "plakat", srodek=True)
    # kiosk
    pygame.draw.rect(s, sep(120), (480, 290, 120, 190))
    pygame.draw.polygon(s, sep(70), [(470, 290), (610, 290), (540, 250)])
    for i in range(3):
        pygame.draw.rect(s, sep(230 - i * 15), (490 + i * 36, 320, 30, 44))
    tlum(s, rng, 14, 425, (45, 65), (50, 100), 360, 1250)


def _tlo_lokal(s, rng):
    wnetrze(s, 190, 115)
    okno(s, (900, 60, 220, 240), 230)
    pygame.draw.rect(s, sep(220), (150, 70, 220, 280))
    pygame.draw.rect(s, sep(80), (150, 70, 220, 280), 3)
    tekst(s, "OBYWATELKI!", (260, 100), 24, 30, "plakat", srodek=True)
    tekst(s, "WASZ GŁOS", (260, 140), 22, 40, "plakat", srodek=True)
    tekst(s, "MA WAGĘ", (260, 170), 22, 40, "plakat", srodek=True)
    # waga szalkowa
    pygame.draw.line(s, sep(40), (260, 200), (260, 300), 4)
    pygame.draw.line(s, sep(40), (200, 230), (320, 230), 3)
    for xx in (200, 320):
        pygame.draw.arc(s, sep(40), (xx - 25, 240, 50, 30), math.pi, 2 * math.pi, 3)
        pygame.draw.line(s, sep(40), (xx, 230), (xx - 22, 254), 1)
        pygame.draw.line(s, sep(40), (xx, 230), (xx + 22, 254), 1)
    pygame.draw.rect(s, sep(40), (230, 300, 60, 10))
    tekst(s, "Liga Kobiet", (260, 320), 18, 60, "reka", srodek=True)
    # urna
    pygame.draw.rect(s, sep(95), (440, 360, 110, 100))
    pygame.draw.rect(s, sep(130), (430, 345, 130, 20))
    pygame.draw.rect(s, sep(30), (470, 351, 50, 6))
    pygame.draw.rect(s, sep(70), (450, 460, 90, 10))
    # stół i krzesła
    pygame.draw.rect(s, sep(80), (600, 400, 360, 18))
    for i in range(5):
        pygame.draw.rect(s, sep(230), (620 + i * 66, 390, 40, 12))
    pygame.draw.rect(s, sep(70), (610, 418, 10, 70))
    pygame.draw.rect(s, sep(70), (940, 418, 10, 70))
    plakat(s, (420, 80, 150, 190), rng, "28 XI 1918", 225)
    zyrandol(s, 760, 120)


TLA = {
    "archiwum": _tlo_archiwum, "krakow": _tlo_krakow, "harcowka": _tlo_harcowka, "palac_wnetrze": _tlo_palac,
    "lublin_palac": _tlo_lublin_palac, "drukarnia": _tlo_drukarnia, "wagon": _tlo_wagon, "dworzec": _tlo_dworzec,
    "koszary": _tlo_koszary, "plac_saski": _tlo_plac_saski, "paryz_biuro": _tlo_paryz_biuro, "salon": _tlo_salon,
    "poznan": _tlo_poznan, "lokal": _tlo_lokal,
}


def tlo(klucz):
    """Gotowe tło lokacji 1280×560: rysunek → zmiękczenie → tonowanie → ziarno, rysy, winieta, narożniki."""
    if ("tlo", klucz) in _cache:
        return _cache[("tlo", klucz)]
    rng = random.Random(sum(map(ord, klucz)))
    s = pygame.Surface((W, SCENA_H))
    s.fill(sep(150))
    TLA[klucz](s, rng)
    s = zmiekcz(s, 2)
    rysy(s, rng, 5)
    naloz_kafel(s, kafel_szumu(256, 34, 11))
    s.blit(winieta(W, SCENA_H, 150), (0, 0))
    s = tonuj(s)
    fotoroki(s)
    _cache[("tlo", klucz)] = s
    return s


# ============================================================ sylwetki-wycinanki
def _figura(wyglad, skala=1.0):
    """Rysuje postać w widoku z przodu na przezroczystej powierzchni."""
    h = int(300 * wyglad.get("wzrost", 1.0) * skala)
    w = int(h * 0.55)
    s = pygame.Surface((w, h + 40), pygame.SRCALPHA)
    cx = w // 2
    top = 40
    glowa_r = int(h * 0.075)
    gy = top + int(h * 0.1)
    ramie_y = gy + glowa_r + int(h * 0.04)
    fiolet = wyglad.get("fiolet")
    pv = wyglad.get("plaszcz", 60)
    c_plaszcz = FIOLET if fiolet else sep(pv)
    c_ciemny = sep(max(0, pv - 35))
    c_twarz = sep(205)
    dol = top + h - 4
    szer_ram = int(h * 0.17)
    # nogi / suknia / sutanna
    if wyglad.get("suknia") or wyglad.get("sutanna") or fiolet:
        pygame.draw.polygon(s, c_plaszcz if not wyglad.get("sutanna") else sep(30),
                            [(cx - szer_ram, ramie_y + 10), (cx + szer_ram, ramie_y + 10), (cx + int(szer_ram * 1.5), dol), (cx - int(szer_ram * 1.5), dol)])
        pygame.draw.ellipse(s, sep(25), (cx - szer_ram, dol - 6, szer_ram * 2, 12))
    else:
        nog_w = int(h * 0.055)
        pygame.draw.rect(s, sep(max(0, pv - 45)), (cx - nog_w - 3, int(top + h * 0.62), nog_w, int(h * 0.36)))
        pygame.draw.rect(s, sep(max(0, pv - 45)), (cx + 3, int(top + h * 0.62), nog_w, int(h * 0.36)))
        pygame.draw.ellipse(s, sep(20), (cx - nog_w - 10, dol - 8, nog_w + 12, 12))
        pygame.draw.ellipse(s, sep(20), (cx + 1, dol - 8, nog_w + 12, 12))
    # tułów / płaszcz
    dl_plaszcza = 0.72 if wyglad.get("sukmana") else 0.66
    if not (wyglad.get("suknia") or wyglad.get("sutanna") or fiolet):
        pygame.draw.polygon(s, c_plaszcz, [(cx - szer_ram, ramie_y), (cx + szer_ram, ramie_y),
                                           (cx + int(szer_ram * 1.15), int(top + h * dl_plaszcza)),
                                           (cx - int(szer_ram * 1.15), int(top + h * dl_plaszcza))])
        pygame.draw.line(s, c_ciemny, (cx, ramie_y + 8), (cx, int(top + h * dl_plaszcza)), 2)
        for k in range(4):
            pygame.draw.circle(s, c_ciemny, (cx + 6, ramie_y + 20 + k * int(h * 0.07)), 3)
    elif wyglad.get("suknia"):
        pygame.draw.polygon(s, c_plaszcz, [(cx - szer_ram + 6, ramie_y), (cx + szer_ram - 6, ramie_y),
                                           (cx + szer_ram - 2, int(top + h * 0.42)), (cx - szer_ram + 2, int(top + h * 0.42))])
        pygame.draw.line(s, c_ciemny, (cx - szer_ram, int(top + h * 0.42)), (cx + szer_ram, int(top + h * 0.42)), 3)
    if wyglad.get("sukmana"):
        pygame.draw.line(s, sep(40), (cx - szer_ram, ramie_y + 4), (cx - int(szer_ram * 1.1), int(top + h * 0.72)), 3)
        pygame.draw.line(s, sep(40), (cx + szer_ram, ramie_y + 4), (cx + int(szer_ram * 1.1), int(top + h * 0.72)), 3)
    if wyglad.get("fartuch"):
        pygame.draw.rect(s, sep(220), (cx - szer_ram + 8, ramie_y + 30, szer_ram * 2 - 16, int(h * 0.45)))
    # ręce
    rek_w = int(h * 0.05)
    for strona in (-1, 1):
        x0 = cx + strona * szer_ram
        pts = [(x0, ramie_y + 2), (x0 + strona * rek_w, ramie_y + 8),
               (x0 + strona * (rek_w + 4), int(top + h * 0.5)), (x0 + strona * 2, int(top + h * 0.5))]
        pygame.draw.polygon(s, c_plaszcz if not wyglad.get("sutanna") else sep(30), pts)
        pygame.draw.circle(s, c_twarz, (x0 + strona * (rek_w // 2 + 2), int(top + h * 0.52)), int(rek_w * 0.55))
    # chusta harcerska
    if wyglad.get("chusta"):
        pygame.draw.polygon(s, sep(235), [(cx - 18, ramie_y), (cx + 18, ramie_y), (cx, ramie_y + 34)])
        pygame.draw.circle(s, sep(60), (cx, ramie_y + 12), 4)
    if wyglad.get("krzyz"):
        pygame.draw.line(s, sep(230), (cx, ramie_y + 30), (cx, ramie_y + 60), 4)
        pygame.draw.line(s, sep(230), (cx - 10, ramie_y + 40), (cx + 10, ramie_y + 40), 4)
        pygame.draw.line(s, sep(200), (cx - 14, ramie_y), (cx, ramie_y + 30), 1)
        pygame.draw.line(s, sep(200), (cx + 14, ramie_y), (cx, ramie_y + 30), 1)
    # szyja i głowa
    pygame.draw.rect(s, c_twarz, (cx - glowa_r // 3, gy + glowa_r - 4, glowa_r * 2 // 3, 12))
    pygame.draw.ellipse(s, c_twarz, (cx - glowa_r, gy - glowa_r, glowa_r * 2, int(glowa_r * 2.25)))
    fr = wyglad.get("fryzura")
    if fr == "grzywa":
        pygame.draw.ellipse(s, sep(170), (cx - glowa_r - 12, gy - glowa_r - 14, glowa_r * 2 + 24, glowa_r * 2))
        pygame.draw.ellipse(s, c_twarz, (cx - glowa_r + 4, gy - glowa_r + 8, glowa_r * 2 - 8, int(glowa_r * 2.05)))
    elif fr != "lysy" and not wyglad.get("czapka"):
        pygame.draw.ellipse(s, sep(60), (cx - glowa_r, gy - glowa_r - 2, glowa_r * 2, glowa_r))
    # oczy i brwi
    oy = gy + 2
    for strona in (-1, 1):
        pygame.draw.circle(s, sep(25), (cx + strona * glowa_r // 2.4, oy), max(2, glowa_r // 7))
        pygame.draw.line(s, sep(50), (cx + strona * glowa_r // 1.6, oy - glowa_r // 3), (cx + strona * glowa_r // 6, oy - glowa_r // 3 - 1), 2)
    pygame.draw.line(s, sep(150), (cx, oy + 2), (cx - 2, oy + glowa_r // 2), 2)
    if wyglad.get("binokle"):
        for strona in (-1, 1):
            pygame.draw.circle(s, sep(30), (int(cx + strona * glowa_r / 2.4), oy), glowa_r // 3, 2)
        pygame.draw.line(s, sep(30), (cx - 3, oy), (cx + 3, oy), 2)
    zar = wyglad.get("zarost")
    my = gy + int(glowa_r * 0.62)
    if zar == "sumiaste":
        pygame.draw.polygon(s, sep(70), [(cx, my - 4), (cx - glowa_r, my + 8), (cx - glowa_r // 2, my + 2), (cx, my + 2),
                                         (cx + glowa_r // 2, my + 2), (cx + glowa_r, my + 8)])
    elif zar == "wasik":
        pygame.draw.rect(s, sep(50), (cx - glowa_r // 2, my - 2, glowa_r, 4))
    elif zar == "broda":
        pygame.draw.polygon(s, sep(70), [(cx - glowa_r, gy + 4), (cx + glowa_r, gy + 4), (cx + glowa_r // 2, gy + glowa_r * 2), (cx, gy + int(glowa_r * 2.4)), (cx - glowa_r // 2, gy + glowa_r * 2)])
        pygame.draw.ellipse(s, c_twarz, (cx - glowa_r // 2, gy + 2, glowa_r, glowa_r // 2 + 4))
        pygame.draw.rect(s, sep(60), (cx - glowa_r // 2, my - 2, glowa_r, 4))
    elif zar == "broda_mala":
        pygame.draw.polygon(s, sep(80), [(cx - glowa_r // 2, my + 4), (cx + glowa_r // 2, my + 4), (cx, gy + int(glowa_r * 1.9))])
        pygame.draw.rect(s, sep(70), (cx - glowa_r // 2, my - 3, glowa_r, 4))
    # nakrycia głowy
    cz = wyglad.get("czapka")
    gt = gy - glowa_r
    if cz == "maciejowka":
        pygame.draw.rect(s, sep(55), (cx - glowa_r - 2, gt - 12, glowa_r * 2 + 4, glowa_r))
        pygame.draw.polygon(s, sep(35), [(cx - glowa_r, gt + 2), (cx + glowa_r + 8, gt + 2), (cx + glowa_r, gt + 10), (cx - glowa_r, gt + 10)])
        pygame.draw.rect(s, sep(200), (cx - 3, gt - 6, 6, 8))
    elif cz == "harcerski":
        pygame.draw.ellipse(s, sep(95), (cx - glowa_r - 16, gt + 4, glowa_r * 2 + 32, 12))
        pygame.draw.polygon(s, sep(95), [(cx - glowa_r + 2, gt + 8), (cx + glowa_r - 2, gt + 8), (cx + glowa_r - 6, gt - 18), (cx, gt - 12), (cx - glowa_r + 6, gt - 18)])
        pygame.draw.rect(s, sep(45), (cx - glowa_r + 2, gt, glowa_r * 2 - 4, 6))
    elif cz == "melonik":
        pygame.draw.ellipse(s, sep(25), (cx - glowa_r - 8, gt + 4, glowa_r * 2 + 16, 10))
        pygame.draw.ellipse(s, sep(25), (cx - glowa_r + 2, gt - 18, glowa_r * 2 - 4, glowa_r * 2))
    elif cz == "cylinder":
        pygame.draw.ellipse(s, sep(20), (cx - glowa_r - 10, gt + 4, glowa_r * 2 + 20, 10))
        pygame.draw.rect(s, sep(20), (cx - glowa_r + 2, gt - 36, glowa_r * 2 - 4, 44))
        pygame.draw.rect(s, sep(90), (cx - glowa_r + 2, gt - 2, glowa_r * 2 - 4, 4))
    elif cz == "kapelusz":
        pygame.draw.ellipse(s, sep(45), (cx - glowa_r - 14, gt + 2, glowa_r * 2 + 28, 12))
        pygame.draw.rect(s, sep(45), (cx - glowa_r + 2, gt - 16, glowa_r * 2 - 4, 22), border_radius=6)
    elif cz == "chlopski":
        pygame.draw.ellipse(s, sep(40), (cx - glowa_r - 18, gt + 2, glowa_r * 2 + 36, 14))
        pygame.draw.rect(s, sep(40), (cx - glowa_r + 4, gt - 12, glowa_r * 2 - 8, 18))
        pygame.draw.rect(s, sep(200), (cx - glowa_r + 4, gt, glowa_r * 2 - 8, 4))
    elif cz == "biretta":
        pygame.draw.rect(s, sep(30), (cx - glowa_r + 2, gt - 10, glowa_r * 2 - 4, 16))
        pygame.draw.circle(s, sep(30), (cx, gt - 14), 5)
    elif cz == "wojskowa":
        pygame.draw.polygon(s, sep(60), [(cx - glowa_r - 4, gt - 14), (cx + glowa_r + 4, gt - 14), (cx + glowa_r, gt + 4), (cx - glowa_r, gt + 4)])
        pygame.draw.rect(s, sep(30), (cx - glowa_r, gt + 2, glowa_r * 2 + 6, 6))
        pygame.draw.rect(s, sep(210), (cx - 3, gt - 10, 6, 8))
    elif cz == "pikielhauba":
        pygame.draw.ellipse(s, sep(45), (cx - glowa_r - 2, gt - 12, glowa_r * 2 + 4, glowa_r + 10))
        pygame.draw.polygon(s, sep(45), [(cx - 4, gt - 10), (cx + 4, gt - 10), (cx, gt - 30)])
        pygame.draw.rect(s, sep(35), (cx - glowa_r - 6, gt + 2, glowa_r * 2 + 12, 5))
        pygame.draw.circle(s, sep(190), (cx + glowa_r - 6, gt), 5)   # kokarda Rady Żołnierskiej
    elif cz == "kaszkiet":
        pygame.draw.ellipse(s, sep(70), (cx - glowa_r - 6, gt - 10, glowa_r * 2 + 12, glowa_r))
        pygame.draw.polygon(s, sep(40), [(cx - glowa_r, gt + 6), (cx + glowa_r + 10, gt + 6), (cx + glowa_r, gt + 12), (cx - glowa_r, gt + 12)])
    elif cz == "studencka":
        pygame.draw.rect(s, sep(210), (cx - glowa_r - 2, gt - 10, glowa_r * 2 + 4, 14))
        pygame.draw.rect(s, sep(40), (cx - glowa_r - 2, gt + 2, glowa_r * 2 + 10, 6))
    elif cz == "damski":
        pygame.draw.ellipse(s, sep(60), (cx - glowa_r - 22, gt + 2, glowa_r * 2 + 44, 14))
        pygame.draw.ellipse(s, sep(60), (cx - glowa_r + 2, gt - 16, glowa_r * 2 - 4, 26))
        pygame.draw.circle(s, sep(220), (cx + glowa_r, gt - 4), 7)
        pygame.draw.ellipse(s, sep(55), (cx - glowa_r - 2, gy - 4, 10, glowa_r * 2))
        pygame.draw.ellipse(s, sep(55), (cx + glowa_r - 8, gy - 4, 10, glowa_r * 2))
    elif cz == "chusta_glowa":
        pygame.draw.polygon(s, sep(170), [(cx - glowa_r - 6, gy + glowa_r), (cx - glowa_r, gt - 4), (cx + glowa_r, gt - 4), (cx + glowa_r + 6, gy + glowa_r), (cx, gy + int(glowa_r * 1.4))])
        pygame.draw.ellipse(s, c_twarz, (cx - glowa_r + 4, gt + 4, glowa_r * 2 - 8, int(glowa_r * 1.9)))
        pygame.draw.circle(s, sep(25), (int(cx - glowa_r / 2.4), oy), max(2, glowa_r // 7))
        pygame.draw.circle(s, sep(25), (int(cx + glowa_r / 2.4), oy), max(2, glowa_r // 7))
    elif cz == "kaptur":
        pygame.draw.ellipse(s, FIOLET, (cx - glowa_r - 12, gt - 20, glowa_r * 2 + 24, glowa_r * 2 + 34))
        pygame.draw.polygon(s, FIOLET, [(cx - glowa_r - 12, gy), (cx + glowa_r + 12, gy),
                                        (cx + glowa_r + 22, gy + glowa_r + 18), (cx - glowa_r - 22, gy + glowa_r + 18)])
        pygame.draw.ellipse(s, (70, 36, 98), (cx - glowa_r + 1, gt + 2, glowa_r * 2 - 2, int(glowa_r * 2.15)))
        pygame.draw.ellipse(s, sep(165), (cx - glowa_r + 5, gt + 8, glowa_r * 2 - 10, int(glowa_r * 1.95)))
        for strona in (-1, 1):
            pygame.draw.circle(s, sep(25), (int(cx + strona * glowa_r / 2.6), oy + 2), max(2, glowa_r // 7))
            pygame.draw.circle(s, sep(40), (int(cx + strona * glowa_r / 2.6), oy + 2), glowa_r // 3, 1)  # okulary archiwisty
        pygame.draw.arc(s, sep(60), (cx - 8, oy + 8, 16, 10), math.pi, 2 * math.pi, 2)
        pygame.draw.arc(s, FIOLET_JASNY, (cx - glowa_r - 6, gt - 14, glowa_r * 2 + 12, glowa_r * 2 + 24), 0.3, math.pi - 0.3, 2)
    # akcesoria
    if wyglad.get("szabla"):
        pygame.draw.line(s, sep(30), (cx - szer_ram - 6, int(top + h * 0.5)), (cx - szer_ram - 22, int(top + h * 0.9)), 4)
        pygame.draw.line(s, sep(200), (cx - szer_ram - 12, int(top + h * 0.5)), (cx - szer_ram, int(top + h * 0.5)), 3)
    if wyglad.get("laska"):
        pygame.draw.line(s, sep(35), (cx + szer_ram + 10, int(top + h * 0.52)), (cx + szer_ram + 18, dol), 4)
        pygame.draw.circle(s, sep(200), (cx + szer_ram + 10, int(top + h * 0.52)), 5)
    if wyglad.get("teczka"):
        pygame.draw.rect(s, sep(45), (cx + szer_ram - 4, int(top + h * 0.53), 34, 26), border_radius=3)
        pygame.draw.rect(s, sep(200), (cx + szer_ram + 10, int(top + h * 0.53) + 10, 6, 4))
    if fiolet:
        pygame.draw.rect(s, sep(225), (cx - 20, int(top + h * 0.42), 40, 30))          # album
        pygame.draw.rect(s, sep(60), (cx - 20, int(top + h * 0.42), 40, 30), 2)
        pygame.draw.line(s, FIOLET_JASNY, (cx - szer_ram, ramie_y + 10), (cx - int(szer_ram * 1.4), dol - 4), 2)
        pygame.draw.line(s, FIOLET_JASNY, (cx + szer_ram, ramie_y + 10), (cx + int(szer_ram * 1.4), dol - 4), 2)
    return s


def wycinanka(obraz, grubosc=4, cien=(6, 6), kolor_brzegu=None):
    """Efekt papierowej wycinanki: kremowy brzeg + cień pod spodem."""
    kolor_brzegu = kolor_brzegu or sep(238)
    w, h = obraz.get_size()
    pad = grubosc + max(cien) + 2
    s = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    maska = pygame.mask.from_surface(obraz, 10)
    brzeg = maska.to_surface(setcolor=kolor_brzegu, unsetcolor=(0, 0, 0, 0))
    cien_s = maska.to_surface(setcolor=(20, 12, 6, 110), unsetcolor=(0, 0, 0, 0))
    for dx in range(-grubosc, grubosc + 1, 2):
        for dy in range(-grubosc, grubosc + 1, 2):
            if dx * dx + dy * dy <= grubosc * grubosc + 1:
                s.blit(cien_s, (pad + dx + cien[0], pad + dy + cien[1]))
    for dx in range(-grubosc, grubosc + 1):
        for dy in range(-grubosc, grubosc + 1):
            if dx * dx + dy * dy <= grubosc * grubosc:
                s.blit(brzeg, (pad + dx, pad + dy))
    s.blit(obraz, (pad, pad))
    return s


def sylwetka(pid, skala=1.0):
    klucz = ("syl", pid, skala)
    if klucz not in _cache:
        wyglad = P.wszystkie()[pid]["wyglad"]
        _cache[klucz] = wycinanka(_figura(wyglad, skala))
    return _cache[klucz]


def portret(pid, rozmiar=150):
    """Portret w owalnym medalionie (do dialogów)."""
    klucz = ("portret", pid, rozmiar)
    if klucz in _cache:
        return _cache[klucz]
    fig = _figura(P.wszystkie()[pid]["wyglad"], 1.6)
    fw, fh = fig.get_size()
    s = pygame.Surface((rozmiar, int(rozmiar * 1.2)), pygame.SRCALPHA)
    tlo_m = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(tlo_m, sep(205), tlo_m.get_rect())
    s.blit(tlo_m, (0, 0))
    wyc = fig.subsurface((0, 0, fw, int(fh * 0.5))).copy()
    sk = rozmiar * 1.1 / fw
    wyc = pygame.transform.smoothscale(wyc, (int(fw * sk), int(fh * 0.5 * sk)))
    maska = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(maska, (255, 255, 255, 255), maska.get_rect())
    warstwa = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    warstwa.blit(wyc, ((rozmiar - wyc.get_width()) // 2, 4))
    warstwa.blit(maska, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(warstwa, (0, 0))
    pygame.draw.ellipse(s, FIOLET if pid == "damian" else sep(60), s.get_rect(), 5)
    pygame.draw.ellipse(s, sep(235), s.get_rect().inflate(-10, -10), 2)
    _cache[klucz] = s
    return s


# ============================================================ ikony przedmiotów
def _ikona(klucz, r):
    s = pygame.Surface((r, r), pygame.SRCALPHA)
    c = r // 2
    jas, ciem = sep(232), sep(40)
    if klucz == "lupa":
        pygame.draw.circle(s, sep(150), (c - 6, c - 6), r // 3)
        pygame.draw.circle(s, sep(225), (c - 6, c - 6), r // 3 - 5)
        pygame.draw.line(s, ciem, (c + 6, c + 6), (r - 6, r - 6), 8)
    elif klucz in ("pocztowka_krakow",):
        pygame.draw.rect(s, jas, (6, 14, r - 12, r - 28))
        pygame.draw.rect(s, ciem, (6, 14, r - 12, r - 28), 2)
        pygame.draw.rect(s, sep(120), (12, 20, r // 2 - 8, r - 40))
        pygame.draw.rect(s, CZERWIEN_STEMPLA, (r - 22, 20, 12, 14), 2)
    elif klucz == "orzelek":
        pygame.draw.polygon(s, sep(215), [(c, 8), (c + 8, 18), (r - 6, 14), (c + 10, c + 6), (c + 6, r - 8), (c, r - 14),
                                          (c - 6, r - 8), (c - 10, c + 6), (6, 14), (c - 8, 18)])
        pygame.draw.polygon(s, ciem, [(c, 8), (c + 8, 18), (r - 6, 14), (c + 10, c + 6), (c + 6, r - 8), (c, r - 14),
                                      (c - 6, r - 8), (c - 10, c + 6), (6, 14), (c - 8, 18)], 2)
        pygame.draw.polygon(s, sep(180), [(c - 4, 4), (c + 4, 4), (c + 5, 10), (c - 5, 10)])
    elif klucz == "opaska":
        pygame.draw.rect(s, sep(245), (6, c - 12, r - 12, 12))
        pygame.draw.rect(s, sep(95), (6, c, r - 12, 12))
        pygame.draw.rect(s, ciem, (6, c - 12, r - 12, 24), 2)
    elif klucz in ("meldunek", "depesza"):
        pygame.draw.rect(s, jas, (6, 14, r - 12, r - 28))
        pygame.draw.polygon(s, ciem, [(6, 14), (c, c + 2), (r - 6, 14)], 2)
        pygame.draw.rect(s, ciem, (6, 14, r - 12, r - 28), 2)
        if klucz == "meldunek":
            pygame.draw.circle(s, CZERWIEN_STEMPLA, (c, c + 2), 7)
        else:
            tekst(s, "TEL", (c, r - 20), 12, 30, "plakat", srodek=True)
    elif klucz in ("odpis_oredzia", "dekret", "odbitka_manifestu"):
        pygame.draw.rect(s, jas, (12, 6, r - 24, r - 12))
        pygame.draw.rect(s, ciem, (12, 6, r - 24, r - 12), 2)
        for k in range(5):
            pygame.draw.line(s, sep(110), (18, 16 + k * 8), (r - 18, 16 + k * 8), 2)
        if klucz != "odbitka_manifestu":
            pygame.draw.circle(s, CZERWIEN_STEMPLA, (r - 22, r - 16), 7, 2)
        else:
            pygame.draw.ellipse(s, sep(60), (16, r - 22, 16, 10))
    elif klucz == "rozklad_jazdy":
        pygame.draw.rect(s, sep(210), (8, 16, r - 16, r - 32))
        pygame.draw.rect(s, ciem, (8, 16, r - 16, r - 32), 2)
        tekst(s, "10 XI", (c, c - 6), 13, 30, "plakat", srodek=True)
        tekst(s, "7.00", (c, c + 8), 12, 30, "szeryf", srodek=True)
    elif klucz == "plan_koszar":
        pygame.draw.rect(s, sep(215), (6, 10, r - 12, r - 20))
        for k in range(5):
            pygame.draw.circle(s, ciem, (14 + k * (r - 28) // 4, c + int(math.sin(k) * 10)), 4)
        pygame.draw.rect(s, ciem, (6, 10, r - 12, r - 20), 2)
    elif klucz in ("kurier", "gazeta"):
        pygame.draw.rect(s, jas, (6, 10, r - 12, r - 20))
        pygame.draw.rect(s, ciem, (6, 10, r - 12, r - 20), 2)
        pygame.draw.rect(s, sep(60), (10, 14, r - 20, 8))
        for k in range(4):
            pygame.draw.line(s, sep(120), (10, 28 + k * 7), (c - 3, 28 + k * 7), 2)
            pygame.draw.line(s, sep(120), (c + 3, 28 + k * 7), (r - 10, 28 + k * 7), 2)
    else:
        pygame.draw.circle(s, jas, (c, c), c - 4)
        pygame.draw.circle(s, ciem, (c, c), c - 4, 2)
    return s


def ikona(klucz, r=56):
    k = ("ikona", klucz, r)
    if k not in _cache:
        _cache[k] = wycinanka(_ikona(klucz, r), 2, (3, 3))
    return _cache[k]


# ============================================================ UI
def ramka_pocztowki(s, rect, ton=228, zabki=True, stempel=None):
    """Kremowa ramka pocztówki z ząbkowanym brzegiem i (opcjonalnie) stemplem."""
    x, y, w, h = rect
    s.blit(papier(w, h, ton, seed=w + h), (x, y))
    if zabki:
        krok = 14
        for i in range(x, x + w, krok):
            pygame.draw.circle(s, sep(35), (i + krok // 2, y), 4)
            pygame.draw.circle(s, sep(35), (i + krok // 2, y + h), 4)
        for j in range(y, y + h, krok):
            pygame.draw.circle(s, sep(35), (x, j + krok // 2), 4)
            pygame.draw.circle(s, sep(35), (x + w, j + krok // 2), 4)
    pygame.draw.rect(s, sep(ton - 70), (x + 8, y + 8, w - 16, h - 16), 1)
    if stempel:
        stempel_okragly(s, (x + w - 70, y + 62), stempel)


def stempel_okragly(s, srodek, napis, r=46, kolor=CZERWIEN_STEMPLA):
    warstwa = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
    c = (r + 4, r + 4)
    k = kolor + (170,)
    pygame.draw.circle(warstwa, k, c, r, 3)
    pygame.draw.circle(warstwa, k, c, r - 8, 1)
    f = czcionki.f("plakat", 13)
    obraz = f.render(napis, True, kolor)
    obraz.set_alpha(190)
    warstwa.blit(obraz, obraz.get_rect(center=c))
    warstwa = pygame.transform.rotate(warstwa, -14)
    s.blit(warstwa, warstwa.get_rect(center=srodek))


def przycisk(s, rect, napis, aktywny=False, rozmiar=20, wylaczony=False):
    x, y, w, h = rect
    ton = 238 if aktywny else 218
    if wylaczony:
        ton = 175
    pygame.draw.rect(s, sep(30), (x + 4, y + 4, w, h), border_radius=4)
    s.blit(papier(w, h, ton, seed=w * 3 + h), (x, y))
    pygame.draw.rect(s, sep(60 if not aktywny else 25), rect, 2, border_radius=4)
    tekst(s, napis, (x + w // 2, y + h // 2), rozmiar, 90 if wylaczony else 25, "plakat", srodek=True)


def strzalka_wyjscia(s, rect, faza=0.0):
    x, y, w, h = rect
    cx, cy = x + w // 2, y + h // 2
    ob = pygame.Surface((w, h), pygame.SRCALPHA)
    ramka_pocztowki(ob, (8, 12, w - 16, h - 24), 232, zabki=False)
    pygame.draw.polygon(ob, sep(40), [(w // 2 - 18, h // 2 - 14), (w // 2 + 10, h // 2 - 14), (w // 2 + 10, h // 2 - 26),
                                      (w // 2 + 32, h // 2), (w // 2 + 10, h // 2 + 26), (w // 2 + 10, h // 2 + 14), (w // 2 - 18, h // 2 + 14)])
    ob = pygame.transform.rotate(ob, math.sin(faza * 2) * 4)
    s.blit(ob, ob.get_rect(center=(cx, cy + math.sin(faza * 3) * 4)))


def ramka_sztalugi(s, rect):
    """Wielka pocztówka na sztaludze (Paderewski z Nowego Jorku)."""
    x, y, w, h = rect
    ramka_pocztowki(s, rect, 215, zabki=True)
    gradient(s, (x + 14, y + 40, w - 28, h - 60), 200, 160)
    for i in range(6):
        bx = x + 20 + i * (w - 40) // 6
        bh = 40 + (i * 37) % 70
        pygame.draw.rect(s, sep(110), (bx, y + h - 20 - bh, (w - 40) // 6 - 4, bh))
    tekst(s, "New York, November 1918", (x + w // 2, y + 22), 16, 40, "reka", srodek=True)
