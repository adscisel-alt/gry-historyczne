# -*- coding: utf-8 -*-
"""Grafika: kafle izometryczne, budynki, jednostki, portrety, UI.

Dwa style:
- „3d” (domyślny) – sprite'y prerenderowane w Blenderze (tools/blender/render_sprites.py),
  wczytywane z assets/3d/, jak w klasycznych strategiach z lat 90.,
- „pixel” – grafika rysowana kodem w połowie rozdzielczości i powiększana x2.
Klawisz G w grze przełącza styl. Gdy brak pliku 3D, używany jest styl pikselowy.
"""
import math
import os
import random
import sys
import pygame

_ASSET_DIR = os.path.join(getattr(sys, "_MEIPASS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")),
                          "assets", "3d")
_style = ["3d" if os.path.isdir(_ASSET_DIR) else "pixel"]
_assets = {}


def style():
    return _style[0]


def set_style(st):
    _style[0] = st if (st != "3d" or os.path.isdir(_ASSET_DIR)) else "pixel"
    _cache.clear()


def toggle_style():
    set_style("pixel" if _style[0] == "3d" else "3d")
    return _style[0]


def asset(name):
    """Wczytuje render 3D (PNG) albo zwraca None, gdy styl pikselowy lub brak pliku."""
    if _style[0] != "3d":
        return None
    if name not in _assets:
        path = os.path.join(_ASSET_DIR, name + ".png")
        try:
            img = pygame.image.load(path)
            _assets[name] = img.convert_alpha() if pygame.display.get_surface() else img
        except Exception:
            _assets[name] = None
    return _assets[name]

TW, TH = 64, 32          # rozmiar kafla po powiększeniu
HTW, HTH = 32, 16        # rozmiar kafla w pół-rozdzielczości

_cache = {}


def cached(fn):
    def wrap(*args, **kw):
        key = (fn.__name__,) + tuple(repr(a) for a in args) + tuple(sorted((k, repr(v)) for k, v in kw.items()))
        if key not in _cache:
            _cache[key] = fn(*args, **kw)
        return _cache[key]
    return wrap


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3])


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(min(3, len(a))))


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def up(surf, k=2):
    return pygame.transform.scale(surf, (surf.get_width() * k, surf.get_height() * k))


def S(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def rect(s, x, y, w, h, c):
    s.fill(c, (x, y, w, h))


def px(s, x, y, c):
    if 0 <= x < s.get_width() and 0 <= y < s.get_height():
        s.set_at((int(x), int(y)), c)


def line(s, c, a, b, w=1):
    pygame.draw.line(s, c, a, b, w)


def poly(s, c, pts):
    pygame.draw.polygon(s, c, [(round(x), round(y)) for x, y in pts])


# ------------------------------------------------------------------ TEREN
PAL = {
    "grass": [(86, 140, 58), (96, 152, 64), (78, 128, 52), (104, 160, 70)],
    "forest": [(58, 104, 46), (66, 116, 50), (52, 94, 42), (72, 120, 54)],
    "hills": [(132, 126, 92), (146, 138, 100), (120, 114, 86), (110, 120, 80)],
    "water": [(48, 92, 156), (54, 100, 166), (44, 84, 146), (60, 110, 172)],
    "marsh": [(90, 118, 70), (76, 104, 72), (66, 98, 96), (100, 124, 76)],
    "field": [(170, 150, 80), (184, 162, 88), (150, 128, 70), (196, 174, 96)],
    "road": [(160, 136, 96), (172, 148, 104), (146, 124, 88), (180, 158, 112)],
}


def in_diamond(px_, py_, w=HTW, h=HTH):
    return abs(px_ + 0.5 - w / 2) / (w / 2) + abs(py_ + 0.5 - h / 2) / (h / 2)


@cached
def tile(kind, variant=0, frame=0):
    a = asset(f"tile_{kind}_{variant % 4}_{frame % 3 if kind == 'water' else 0}")
    if a:
        return a
    r = random.Random(f"{kind}-{variant}")
    s = S(HTW, HTH)
    pal = PAL[kind]
    for y in range(HTH):
        for x in range(HTW):
            d = in_diamond(x, y)
            if d > 1.0:
                continue
            c = pal[r.randrange(len(pal))] if r.random() < 0.55 else pal[0]
            if kind == "field":
                c = pal[3] if ((x // 2 + y) % 4 in (0, 1)) else pal[2]
                if r.random() < 0.2:
                    c = pal[1]
            if kind == "water":
                wave = (x + y * 2 + frame * 3) % 11
                if wave == 0 and r.random() < 0.7:
                    c = (120, 170, 220)
            if kind == "marsh" and r.random() < 0.18:
                c = (70, 110, 150)
            if kind == "road" and r.random() < 0.08:
                c = (120, 110, 90)
            if d > 0.86:
                c = shade(c, 0.86)
            px(s, x, y, c)
    return up(s)


def tile_outline(color=(255, 240, 160), width=2):
    s = S(TW, TH)
    pts = [(TW // 2, 0), (TW - 1, TH // 2), (TW // 2, TH - 1), (0, TH // 2)]
    pygame.draw.polygon(s, color, pts, width)
    return s


def tile_fill(color):
    s = S(TW, TH)
    pts = [(TW // 2, 0), (TW - 1, TH // 2), (TW // 2, TH - 1), (0, TH // 2)]
    pygame.draw.polygon(s, color, pts)
    return s


# ------------------------------------------------------------------ OBIEKTY TERENU
@cached
def tree(variant):
    a = asset(f"tree_{variant % 6}")
    if a:
        return a
    r = random.Random(variant * 7919 + 13)
    s = S(16, 26)
    trunk = (92, 62, 36)
    if variant % 3 == 0:   # sosna/świerk
        rect(s, 7, 19, 2, 6, trunk)
        greens = [(34, 84, 46), (44, 100, 54), (28, 70, 40)]
        for i, (w, y) in enumerate([(12, 15), (10, 11), (8, 7), (5, 3)]):
            poly(s, greens[i % 2], [(8 - w / 2, y + 6), (8 + w / 2, y + 6), (8, y)])
            for _ in range(5):
                px(s, 8 + r.randint(-w // 3, w // 3), y + r.randint(2, 5), greens[2])
    else:                  # liściaste – dąb, lipa
        rect(s, 7, 17, 2, 8, trunk)
        px(s, 6, 24, trunk); px(s, 9, 24, trunk)
        base = [(62, 120, 50), (52, 104, 44), (78, 140, 58), (44, 92, 40)]
        for _ in range(70):
            a = r.random() * math.tau
            rr = r.random() ** 0.5 * 6.5
            x, y = 8 + math.cos(a) * rr, 11 + math.sin(a) * rr * 0.9
            c = base[2] if y < 9 and x < 9 else base[r.randrange(2)]
            if y > 14:
                c = base[3]
            rect(s, int(x), int(y), 2, 2, c)
    return up(s)


@cached
def rocks(variant):
    a = asset(f"rocks_{variant % 4}")
    if a:
        return a
    r = random.Random(variant * 31 + 5)
    s = S(24, 16)
    for _ in range(3):
        x, y = r.randint(3, 15), r.randint(5, 10)
        w, h = r.randint(4, 7), r.randint(3, 5)
        poly(s, (110, 106, 98), [(x, y + h), (x + w, y + h), (x + w - 1, y + 1), (x + w // 2, y - 1), (x + 1, y + 1)])
        line(s, (150, 146, 136), (x + 1, y + 1), (x + w // 2, y - 1))
        line(s, (80, 76, 70), (x, y + h), (x + w, y + h))
    # pagórek
    return up(s)


@cached
def reeds(variant):
    a = asset(f"reeds_{variant % 2}")
    if a:
        return a
    r = random.Random(variant + 99)
    s = S(16, 12)
    for _ in range(7):
        x = r.randint(2, 13)
        h = r.randint(4, 8)
        line(s, (110, 130, 60), (x, 11), (x, 11 - h))
        px(s, x, 11 - h, (120, 80, 40))
    return up(s)


# ------------------------------------------------------------------ BUDYNKI (bryły izometryczne)
def box(s, cx, cy, hw, h, wall, roof=None, kind="flat", rh=0, planks=False):
    L, B, R, T = (cx - hw, cy), (cx, cy + hw / 2), (cx + hw, cy), (cx, cy - hw / 2)

    def upv(p, d):
        return (p[0], p[1] - d)

    lw, rw = shade(wall, 0.72), wall
    poly(s, lw, [L, B, upv(B, h), upv(L, h)])
    poly(s, rw, [B, R, upv(R, h), upv(B, h)])
    if planks:
        for k in range(2, int(h), 2):
            line(s, shade(lw, 0.85), upv(L, k), upv(B, k))
            line(s, shade(rw, 0.85), upv(B, k), upv(R, k))
    line(s, shade(wall, 0.55), B, upv(B, h))
    roof = roof or shade(wall, 1.15)
    if kind == "flat":
        poly(s, roof, [upv(L, h), upv(B, h), upv(R, h), upv(T, h)])
    elif kind == "pyramid":
        A = (cx, cy - h - rh)
        poly(s, shade(roof, 1.1), [upv(T, h), upv(R, h), A])
        poly(s, shade(roof, 0.75), [upv(L, h), upv(B, h), A])
        poly(s, roof, [upv(B, h), upv(R, h), A])
    elif kind == "gable":
        P1 = ((L[0] + T[0]) / 2, (L[1] + T[1]) / 2 - h - rh)
        P2 = ((B[0] + R[0]) / 2, (B[1] + R[1]) / 2 - h - rh)
        poly(s, shade(roof, 1.15), [upv(T, h), upv(R, h), P2, P1])
        poly(s, rw, [upv(B, h), upv(R, h), P2])
        poly(s, shade(roof, 0.85), [upv(L, h), upv(B, h), P2, P1])
        for k in range(1, 4):
            t = k / 4
            a = lerp(upv(L, h), P1, t)
            b = lerp(upv(B, h), P2, t)
            line(s, shade(roof, 0.7), a, b)
    elif kind == "merlons":
        poly(s, roof, [upv(L, h), upv(B, h), upv(R, h), upv(T, h)])
        for t in [0.0, 0.33, 0.66, 1.0]:
            p = lerp(upv(L, h), upv(B, h), t)
            rect(s, int(p[0]) - 1, int(p[1]) - 3, 2, 3, lw)
            p = lerp(upv(B, h), upv(R, h), t)
            rect(s, int(p[0]) - 1, int(p[1]) - 3, 2, 3, rw)
    return L, B, R, T


def face_pt(cx, cy, hw, side, u, v):
    """Punkt na ścianie: side 'l' (lewa) lub 'r' (prawa), u wzdłuż, v wysokość."""
    L, B, R = (cx - hw, cy), (cx, cy + hw / 2), (cx + hw, cy)
    a, b = (L, B) if side == "l" else (B, R)
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u - v)


def stakes(s, cx, cy, hw, h, col=(120, 84, 48), gap=None, front=None):
    pts = []
    corners = [(cx, cy - hw / 2), (cx + hw, cy), (cx, cy + hw / 2), (cx - hw, cy), (cx, cy - hw / 2)]
    for i in range(4):
        a, b = corners[i], corners[i + 1]
        n = int(hw / 1.5)
        for k in range(n):
            t = k / n
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    sel = sorted(pts, key=lambda p: p[1])
    if front is not None:
        sel = [p for p in sel if (p[1] >= cy) == front]
    for (x, y) in sel:
        if gap and abs(x - gap[0]) < 3 and abs(y - gap[1]) < 3:
            continue
        rect(s, int(x), int(y - h), 2, h, col)
        px(s, int(x), int(y - h - 1), shade(col, 1.3))
        px(s, int(x) + 1, int(y - h), shade(col, 0.7))


def cross(s, x, y, c=(230, 200, 80)):
    rect(s, x, y, 1, 5, c)
    rect(s, x - 1, y + 1, 3, 1, c)


def flag(s, x, y, c, c2=None, frame=0, pole_h=10):
    line(s, (70, 50, 30), (x, y), (x, y - pole_h))
    off = (frame % 2)
    poly(s, c, [(x + 1, y - pole_h), (x + 7, y - pole_h + 1 + off), (x + 1, y - pole_h + 4)])
    if c2:
        poly(s, c2, [(x + 1, y - pole_h + 2), (x + 6, y - pole_h + 3 + off), (x + 1, y - pole_h + 4)])


WOOD = (150, 108, 64)
THATCH = (196, 164, 92)
STONE = (168, 164, 154)
RED_ROOF = (170, 64, 48)
WHITE = (226, 222, 210)

BUILD_H = 56  # wysokość płótna budynku (pół-rozdzielczość)


def _canvas():
    s = S(HTW + 8, BUILD_H)
    cx, cy = (HTW + 8) // 2, BUILD_H - HTH // 2
    return s, cx, cy


@cached
def building(kind, epoch=0, frame=0):
    a = asset(f"building_grod_{min(epoch, 2)}" if kind == "grod" else f"building_{kind}")
    if a:
        return a
    s, cx, cy = _canvas()
    if kind == "grod":
        if epoch <= 1:
            stakes(s, cx, cy, 15, 6, front=False)
            box(s, cx, cy - 1, 8, 6, WOOD, THATCH, "gable", 6, planks=True)
            if epoch == 1:
                box(s, cx + 7, cy - 3, 3, 12, WHITE, RED_ROOF, "pyramid", 6)
                cross(s, cx + 7, cy - 26)
            p = face_pt(cx, cy - 1, 8, "r", 0.5, 0)
            rect(s, int(p[0]) - 1, int(p[1]) - 4, 2, 4, (50, 34, 20))
            stakes(s, cx, cy, 15, 6, front=True, gap=(cx, cy + 7))
            flag(s, cx - 2, cy - 13, (230, 230, 230), (200, 30, 40), frame, 12)
        else:
            box(s, cx, cy, 14, 4, shade(STONE, 0.9), shade(STONE, 0.8), "flat")
            box(s, cx, cy - 4, 7, 16, STONE, shade(STONE, 1.1), "merlons")
            for (tx, ty) in [(cx - 12, cy), (cx + 12, cy), (cx, cy + 6)]:
                box(s, tx, ty, 3, 12, STONE, RED_ROOF, "pyramid", 6)
            p = face_pt(cx, cy - 4, 7, "r", 0.3, 8)
            rect(s, int(p[0]), int(p[1]), 1, 3, (40, 30, 30))
            p = face_pt(cx, cy - 4, 7, "l", 0.6, 9)
            rect(s, int(p[0]), int(p[1]), 1, 3, (40, 30, 30))
            flag(s, cx, cy - 24, (230, 230, 230), (200, 30, 40), frame, 10)
    elif kind == "pole":
        r = random.Random(4)
        pts = [(cx - 13, cy), (cx, cy + 6.5), (cx + 13, cy), (cx, cy - 6.5)]
        poly(s, (176, 150, 70), pts)
        for k in range(-6, 7, 2):
            a = (cx - 13 + 6.5 + k, cy - 3.25 + k / 2)
            line(s, (214, 186, 92), (a[0] - 6, a[1] + 3), (a[0] + 6, a[1] - 3))
        for _ in range(14):
            x, y = cx + r.randint(-9, 9), cy + r.randint(-3, 3)
            line(s, (226, 200, 100), (x, y), (x, y - 2))
        # snopek
        poly(s, (212, 180, 80), [(cx + 4, cy + 2), (cx + 8, cy + 2), (cx + 6, cy - 4)])
        line(s, (150, 110, 50), (cx + 4, cy), (cx + 8, cy))
    elif kind == "drwal":
        box(s, cx - 3, cy, 5, 5, WOOD, THATCH, "gable", 4, planks=True)
        for i in range(3):
            for j in range(3 - i):
                x, y = cx + 5 + j * 3 + i * 1.5, cy + 3 - i * 2.5
                pygame.draw.circle(s, (120, 80, 44), (int(x), int(y)), 2)
                px(s, int(x), int(y), (200, 160, 110))
        rect(s, cx + 1, cy + 4, 3, 2, (110, 74, 40))
        line(s, (160, 160, 170), (cx + 2, cy + 3), (cx + 4, cy))
    elif kind == "kamieniolom":
        for (dx, dy, hw, h) in [(-6, -1, 4, 4), (4, -2, 3, 5), (-1, 3, 4, 3), (7, 3, 2, 2)]:
            box(s, cx + dx, cy + dy, hw, h, STONE, shade(STONE, 1.15))
        line(s, (110, 80, 50), (cx - 10, cy + 2), (cx - 4, cy - 16), 2)
        line(s, (110, 80, 50), (cx - 4, cy - 16), (cx + 4, cy - 10))
        line(s, (60, 60, 60), (cx + 4, cy - 10), (cx + 4, cy - 4))
    elif kind == "targ":
        awn = [((200, 50, 50), WHITE), ((60, 80, 170), (230, 200, 80)), ((60, 140, 70), WHITE)]
        for i, (dx, dy) in enumerate([(-7, -2), (6, -2), (0, 3)]):
            x, y = cx + dx, cy + dy
            box(s, x, y, 4, 3, WOOD, WOOD)
            a, b = awn[i]
            poly(s, a, [(x - 5, y - 4), (x, y - 1.5), (x + 5, y - 4), (x, y - 8)])
            line(s, b, (x - 2, y - 3), (x + 2, y - 6))
            line(s, b, (x + 1, y - 2), (x + 4, y - 4.5))
            for k in range(3):
                px(s, x - 2 + k * 2, y - 1, [(230, 80, 60), (240, 200, 60), (120, 200, 90)][k])
    elif kind == "koszary":
        box(s, cx - 1, cy, 9, 6, WOOD, (120, 90, 60), "gable", 5, planks=True)
        p = face_pt(cx - 1, cy, 9, "r", 0.5, 0)
        rect(s, int(p[0]) - 1, int(p[1]) - 4, 2, 4, (40, 30, 20))
        for k in range(3):
            x = cx + 8 + k * 2
            line(s, (100, 70, 40), (x, cy + 4), (x, cy - 6))
            px(s, x, cy - 7, (200, 200, 210))
        flag(s, cx - 10, cy + 2, (200, 30, 40), (230, 230, 230), frame, 18)
    elif kind == "palisada":
        stakes(s, cx, cy, 13, 7, (130, 92, 52), front=False)
        box(s, cx + 6, cy + 3, 3, 12, WOOD, THATCH, "pyramid", 4, planks=True)
        stakes(s, cx, cy, 13, 7, (130, 92, 52), front=True, gap=(cx + 6, cy + 3))
    elif kind == "kosciol":
        box(s, cx + 2, cy, 7, 8, WHITE, RED_ROOF, "gable", 6)
        for u in (0.3, 0.6):
            p = face_pt(cx + 2, cy, 7, "l", u, 6)
            rect(s, int(p[0]), int(p[1]), 1, 3, (60, 60, 90))
        box(s, cx - 6, cy + 2, 3, 15, WHITE, RED_ROOF, "pyramid", 8)
        cross(s, cx - 6, cy - 28)
        p = face_pt(cx - 6, cy + 2, 3, "r", 0.5, 0)
        rect(s, int(p[0]) - 1, int(p[1]) - 4, 2, 4, (80, 50, 30))
    elif kind == "mlyn":
        box(s, cx - 3, cy, 7, 7, WOOD, THATCH, "pyramid", 6, planks=True)
        wx, wy = cx + 7, cy - 3
        pygame.draw.circle(s, (90, 64, 40), (wx, wy), 6, 2)
        for k in range(6):
            a = k * math.pi / 3 + frame * 0.3
            line(s, (120, 86, 50), (wx, wy), (wx + math.cos(a) * 6, wy + math.sin(a) * 6))
        rect(s, wx - 1, wy + 5, 3, 2, (90, 140, 200))
    elif kind == "zupa":
        box(s, cx + 5, cy + 1, 5, 4, WOOD, THATCH, "gable", 4, planks=True)
        # szyb
        line(s, (110, 76, 40), (cx - 9, cy + 3), (cx - 5, cy - 18), 2)
        line(s, (110, 76, 40), (cx - 1, cy + 3), (cx - 5, cy - 18), 2)
        line(s, (110, 76, 40), (cx - 7, cy - 7), (cx - 3, cy - 7))
        pygame.draw.circle(s, (80, 60, 40), (cx - 5, cy - 18), 2)
        for (dx, dy) in [(-10, 6), (1, 7)]:
            poly(s, (240, 240, 245), [(cx + dx - 3, cy + dy), (cx + dx + 3, cy + dy), (cx + dx, cy + dy - 4)])
            px(s, cx + dx + 1, cy + dy - 2, (200, 200, 210))
    elif kind == "zamek":
        box(s, cx, cy, 13, 9, STONE, shade(STONE, 1.1), "merlons")
        box(s, cx, cy - 9, 6, 12, shade(STONE, 1.05), shade(STONE, 1.15), "merlons")
        for (tx, ty) in [(cx - 12, cy), (cx + 12, cy)]:
            box(s, tx, ty, 3, 15, STONE, RED_ROOF, "pyramid", 7)
        p = face_pt(cx, cy, 13, "r", 0.35, 0)
        rect(s, int(p[0]) - 1, int(p[1]) - 6, 3, 6, (50, 36, 26))
        flag(s, cx, cy - 27, (230, 230, 230), (200, 30, 40), frame, 10)
    return up(s)


@cached
def camp(faction, frame=0):
    a = asset(f"camp_{faction}")
    if a:
        return a
    s, cx, cy = _canvas()
    if faction == "mg":
        cols = [(200, 180, 140), (180, 160, 120)]
        for (dx, dy) in [(-7, -2), (6, -1), (0, 4)]:
            x, y = cx + dx, cy + dy
            pygame.draw.ellipse(s, cols[0], (x - 5, y - 6, 10, 9))
            rect(s, x - 5, y - 2, 10, 3, cols[0])
            line(s, (120, 90, 60), (x - 5, y - 1), (x + 5, y - 1))
            rect(s, x - 1, y - 2, 2, 3, (60, 40, 30))
        flag(s, cx + 11, cy + 4, (60, 40, 30), (220, 220, 200), frame, 18)
    else:
        if faction == "tz":
            col, fc, fc2 = (230, 228, 220), (240, 240, 240), (20, 20, 20)
        else:
            col, fc, fc2 = (140, 110, 80), (60, 60, 60), (160, 40, 40)
        for (dx, dy) in [(-7, -2), (6, -1), (0, 4)]:
            x, y = cx + dx, cy + dy
            poly(s, shade(col, 0.8), [(x - 6, y + 2), (x, y + 4), (x, y - 8)])
            poly(s, col, [(x, y + 4), (x + 6, y + 2), (x, y - 8)])
            line(s, shade(col, 0.5), (x, y + 4), (x, y - 1))
        flag(s, cx + 11, cy + 4, fc, fc2, frame, 18)
        if faction == "tz":
            rect(s, cx + 13, cy - 13, 1, 3, (20, 20, 20))
    # ognisko
    rect(s, cx - 1, cy + 8, 3, 1, (90, 60, 30))
    px(s, cx, cy + 7, (250, 180, 60) if frame % 2 else (240, 120, 40))
    return up(s)


@cached
def landmark(frame=0):
    a = asset("landmark")
    if a:
        return a
    s, cx, cy = _canvas()
    poly(s, (130, 126, 116), [(cx - 3, cy + 2), (cx + 3, cy + 2), (cx + 2, cy - 10), (cx - 2, cy - 11)])
    line(s, (170, 166, 156), (cx - 2, cy - 10), (cx - 3, cy + 2))
    for k in range(3):
        px(s, cx - 1 + k, cy - 6 + k, (200, 180, 60))
    yy = cy - 18 + (frame % 2)
    poly(s, (250, 220, 90), [(cx, yy - 4), (cx + 2, yy), (cx, yy + 4), (cx - 2, yy)])
    px(s, cx, yy, (255, 255, 220))
    return up(s)


# ------------------------------------------------------------------ JEDNOSTKI
FACTION = {
    "pl": {"tunic": (190, 40, 44), "trim": (235, 235, 235), "shield": (235, 235, 235), "emb": (190, 40, 44)},
    "cz": {"tunic": (200, 170, 60), "trim": (60, 60, 60), "shield": (200, 40, 40), "emb": (240, 240, 240)},
    "kz": {"tunic": (235, 235, 230), "trim": (190, 30, 30), "shield": (235, 235, 230), "emb": (190, 30, 30)},
    "en": {"tunic": (110, 90, 64), "trim": (70, 56, 40), "shield": (90, 70, 50), "emb": (60, 50, 40)},
    "mg": {"tunic": (150, 100, 50), "trim": (90, 60, 30), "shield": (120, 80, 40), "emb": (200, 170, 90)},
    "tz": {"tunic": (238, 238, 232), "trim": (20, 20, 20), "shield": (238, 238, 232), "emb": (20, 20, 20)},
    "lt": {"tunic": (150, 30, 40), "trim": (60, 120, 70), "shield": (150, 30, 40), "emb": (240, 240, 240)},
}
SKIN = (232, 186, 150)
STEEL = (170, 176, 186)


def _foot(s, f, x, y):
    t = FACTION[f]
    rect(s, x + 1, y + 10, 1, 4, (60, 50, 40))
    rect(s, x + 4, y + 10, 1, 4, (60, 50, 40))
    rect(s, x, y + 4, 6, 7, t["tunic"])
    rect(s, x, y + 9, 6, 1, t["trim"])
    if f == "tz" or f == "kz":
        rect(s, x + 2, y + 5, 2, 4, t["emb"]); rect(s, x + 1, y + 6, 4, 1, t["emb"])
    rect(s, x + 1, y, 4, 4, SKIN)
    px(s, x + 3, y + 1, (40, 30, 30))


def _helmet(s, f, x, y):
    if f == "mg":
        rect(s, x, y - 1, 6, 2, (110, 80, 50)); rect(s, x + 2, y - 3, 2, 2, (90, 60, 30))
    elif f == "tz":
        rect(s, x, y - 1, 6, 4, STEEL); rect(s, x + 2, y + 1, 3, 1, (30, 30, 30))
    else:
        rect(s, x + 1, y - 1, 4, 2, STEEL); px(s, x + 2, y - 2, STEEL); px(s, x + 3, y - 2, STEEL)


def _shield(s, f, x, y):
    t = FACTION[f]
    rect(s, x, y, 4, 5, t["shield"])
    rect(s, x + 1, y + 1, 2, 3, t["emb"])
    px(s, x + 1, y + 5, t["shield"]); px(s, x + 2, y + 5, t["shield"])


def _horse(s, x, y, col=(110, 76, 46)):
    rect(s, x + 2, y + 4, 12, 5, col)
    rect(s, x + 13, y + 1, 3, 5, col)
    rect(s, x + 15, y + 2, 2, 2, col)
    px(s, x + 15, y + 2, (20, 20, 20))
    for lx in (x + 3, x + 5, x + 11, x + 13):
        rect(s, lx, y + 9, 1, 4, shade(col, 0.7))
    rect(s, x, y + 4, 2, 4, shade(col, 0.6))
    rect(s, x + 13, y + 1, 1, 3, shade(col, 0.6))


@cached
def unit(kind, faction="pl"):
    s = S(24, 22)
    t = FACTION.get(faction, FACTION["pl"])
    if kind in ("spear", "sword", "pike", "bow", "xbow"):
        x, y = 8, 6
        _foot(s, faction, x, y)
        _helmet(s, faction, x, y)
        if kind == "spear":
            line(s, (120, 90, 50), (x + 8, y + 15), (x + 8, y - 5)); rect(s, x + 7, y - 7, 3, 2, STEEL)
            _shield(s, faction, x - 3, y + 4)
        elif kind == "pike":
            line(s, (120, 90, 50), (x + 8, y + 15), (x + 10, y - 6)); rect(s, x + 10, y - 7, 1, 2, STEEL)
            rect(s, x + 6, y + 5, 2, 2, SKIN)
        elif kind == "sword":
            line(s, STEEL, (x + 7, y + 6), (x + 11, y - 1), 1); rect(s, x + 6, y + 6, 2, 1, (120, 90, 40))
            _shield(s, faction, x - 3, y + 4)
            rect(s, x, y + 3, 6, 2, STEEL)
        elif kind == "bow":
            pygame.draw.arc(s, (120, 80, 40), (x + 5, y - 1, 6, 14), -1.4, 1.4, 1)
            line(s, (220, 220, 220), (x + 9, y), (x + 9, y + 12))
            rect(s, x - 2, y + 4, 2, 6, (120, 80, 40))
        elif kind == "xbow":
            line(s, (110, 74, 40), (x + 2, y + 6), (x + 12, y + 5), 1)
            line(s, (80, 60, 40), (x + 10, y + 2), (x + 10, y + 9))
            _shield(s, faction, x - 3, y + 4)
    elif kind in ("horse", "horse_lt", "horse_mg", "knight", "knight_t", "knight_w"):
        hc = {"horse": (110, 76, 46), "horse_lt": (70, 50, 40), "horse_mg": (150, 120, 80),
              "knight": (220, 220, 220), "knight_t": (238, 238, 232), "knight_w": (235, 235, 230)}[kind]
        _horse(s, 3, 7, hc if not kind.startswith("knight") else (90, 70, 60))
        if kind.startswith("knight"):
            rect(s, 4, 10, 11, 4, hc)  # kropierz
            if kind == "knight_t":
                rect(s, 9, 10, 1, 4, (20, 20, 20)); rect(s, 8, 11, 3, 1, (20, 20, 20))
            elif kind == "knight_w":
                rect(s, 9, 10, 1, 4, (190, 30, 30)); rect(s, 8, 11, 3, 1, (190, 30, 30))
            else:
                rect(s, 6, 11, 7, 2, (190, 40, 44))
        rx, ry = 7, 0
        rect(s, rx, ry + 4, 5, 6, t["tunic"])
        rect(s, rx + 1, ry, 4, 4, SKIN if not kind.startswith("knight") else STEEL)
        if kind.startswith("knight"):
            rect(s, rx + 2, ry + 1, 3, 1, (30, 30, 30))
            px(s, rx + 3, ry - 1, (200, 40, 40) if kind == "knight" else (240, 240, 240))
        else:
            _helmet(s, "mg" if kind == "horse_mg" else faction, rx, ry)
        if kind == "horse_mg":
            pygame.draw.arc(s, (120, 80, 40), (rx + 4, ry, 5, 10), -1.4, 1.4, 1)
        else:
            line(s, (130, 100, 60), (rx - 4, ry + 8), (rx + 16, ry + 2))
            rect(s, rx + 15, ry + 1, 2, 2, STEEL)
            if kind == "horse_lt":
                _shield(s, "lt", rx - 2, ry + 4)
    elif kind == "cannon":
        rect(s, 3, 13, 15, 3, (120, 84, 50))
        pygame.draw.circle(s, (80, 60, 40), (6, 17), 3)
        pygame.draw.circle(s, (80, 60, 40), (15, 17), 3)
        poly(s, (70, 72, 78), [(4, 12), (19, 7), (21, 10), (6, 15)])
        line(s, (120, 124, 130), (6, 12), (19, 8))
        rect(s, 20, 7, 2, 4, (40, 40, 44))
    elif kind == "wagon":
        rect(s, 3, 9, 17, 6, (130, 92, 52))
        pygame.draw.ellipse(s, (226, 220, 200), (3, 3, 17, 10))
        rect(s, 3, 8, 17, 2, (226, 220, 200))
        pygame.draw.circle(s, (70, 50, 30), (6, 16), 3, 1)
        pygame.draw.circle(s, (70, 50, 30), (17, 16), 3, 1)
    elif kind == "smoke":
        for (x, y, r) in [(7, 12, 5), (13, 10, 6), (17, 14, 4), (10, 7, 4)]:
            pygame.draw.circle(s, (170, 170, 160, 220), (x, y), r)
            pygame.draw.circle(s, (200, 200, 190, 220), (x - 1, y - 1), max(1, r - 2))
    return s  # zwracane w pół-rozdzielczości; skaluj ręcznie


def unit_big(kind, faction, k):
    a = asset(f"unit_{kind}_{faction}")
    if a:
        return pygame.transform.smoothscale(a, (24 * k, 22 * k))
    return pygame.transform.scale(unit(kind, faction), (24 * k, 22 * k))


# ------------------------------------------------------------------ PORTRETY
def _ellipse(s, c, r):
    pygame.draw.ellipse(s, c, r)


@cached
def portrait(p, k=4):
    s = S(32, 32)
    bg = p["bg"]
    for y in range(32):
        rect(s, 0, y, 32, 1, mix(shade(bg, 1.25), shade(bg, 0.6), y / 31))
    cloth = p["cloth"]
    hair = p["hair"]
    head = p["head"]
    skin = SKIN
    if head == "veil" or head == "crown_veil":
        _ellipse(s, (236, 234, 226), (6, 4, 20, 30))
    if head == "hood":
        _ellipse(s, shade(cloth, 0.8), (5, 3, 22, 30))
    # ramiona
    _ellipse(s, cloth, (3, 24, 26, 14))
    rect(s, 3, 29, 26, 3, cloth)
    line(s, shade(cloth, 0.7), (16, 26), (16, 31))
    if head == "mitre":
        line(s, (220, 190, 80), (12, 25), (12, 31)); line(s, (220, 190, 80), (20, 25), (20, 31))
    if head == "hood":
        rect(s, 13, 25, 6, 2, (230, 220, 190))
    # szyja + głowa
    rect(s, 14, 21, 4, 5, shade(skin, 0.85))
    _ellipse(s, skin, (10, 8, 12, 15))
    # włosy
    if head not in ("hood", "veil", "crown_veil", "mitre", "helmet"):
        _ellipse(s, hair, (9, 6, 14, 7))
        rect(s, 9, 9, 2, 6, hair); rect(s, 21, 9, 2, 6, hair)
    elif head == "helmet":
        rect(s, 9, 11, 2, 5, hair); rect(s, 21, 11, 2, 5, hair)
    if head in ("crown_s",) and not p.get("beard"):
        rect(s, 9, 10, 2, 10, hair); rect(s, 21, 10, 2, 10, hair)
    # oczy, brwi, nos, usta
    for ex in (13, 18):
        rect(s, ex, 14, 2, 1, (250, 250, 250)); px(s, ex + (1 if ex == 13 else 0), 14, (40, 30, 30))
        rect(s, ex, 12, 2, 1, shade(hair, 0.8))
    px(s, 16, 16, shade(skin, 0.8)); px(s, 16, 17, shade(skin, 0.75))
    rect(s, 15, 19, 3, 1, (170, 90, 80))
    px(s, 12, 17, (240, 160, 140)); px(s, 20, 17, (240, 160, 140))
    b = p.get("beard")
    if b == "full" or b == "long":
        poly(s, hair, [(10, 15), (22, 15), (21, 21 if b == "full" else 26), (16, 23 if b == "full" else 28), (11, 21 if b == "full" else 26)])
        rect(s, 14, 18, 5, 1, hair)
        rect(s, 15, 19, 3, 1, (150, 80, 70))
        _ellipse(s, skin, (12, 13, 8, 4))
        for ex in (13, 18):
            rect(s, ex, 14, 2, 1, (250, 250, 250)); px(s, ex + (1 if ex == 13 else 0), 14, (40, 30, 30))
        px(s, 16, 16, shade(skin, 0.8))
    elif b == "short":
        poly(s, hair, [(11, 18), (21, 18), (20, 22), (16, 23), (12, 22)])
        rect(s, 15, 19, 3, 1, (150, 80, 70))
    elif b == "mustache":
        rect(s, 13, 18, 7, 1, hair); px(s, 12, 19, hair); px(s, 20, 19, hair)
    # nakrycia głowy
    gold, gd = (232, 196, 70), (180, 140, 40)
    if head == "crown_b":
        rect(s, 10, 6, 12, 3, gold)
        for x in (10, 13, 16, 19, 21):
            rect(s, x, 3, 1, 3, gold); px(s, x, 2, gold)
        px(s, 13, 7, (200, 30, 40)); px(s, 18, 7, (40, 90, 200)); line(s, gd, (10, 8), (21, 8))
    elif head == "crown_s":
        rect(s, 11, 6, 10, 2, gold)
        for x in (11, 14, 17, 20):
            px(s, x, 5, gold); px(s, x, 4, gold)
        px(s, 16, 6, (200, 30, 40))
    elif head == "crown_veil":
        rect(s, 11, 5, 10, 2, gold)
        for x in (11, 14, 17, 20):
            px(s, x, 4, gold)
    elif head == "circlet":
        rect(s, 10, 8, 12, 1, gold); px(s, 16, 7, gold)
    elif head == "veil":
        rect(s, 10, 6, 12, 2, (236, 234, 226))
    elif head == "mitre":
        poly(s, (240, 238, 230), [(10, 9), (22, 9), (21, 1), (16, -1), (11, 1)])
        line(s, gold, (16, 0), (16, 9)); line(s, gold, (10, 8), (22, 8))
    elif head == "helmet":
        poly(s, STEEL, [(9, 12), (23, 12), (22, 6), (16, 2), (10, 6)])
        rect(s, 15, 10, 2, 7, STEEL)
        line(s, (230, 234, 240), (12, 6), (16, 3))
    elif head == "hood":
        poly(s, cloth, [(8, 13), (10, 6), (16, 2), (22, 6), (24, 13), (22, 9), (16, 6), (10, 9)])
        rect(s, 8, 12, 3, 12, cloth); rect(s, 21, 12, 3, 12, cloth)
        line(s, shade(cloth, 1.3), (11, 6), (16, 3))
        rect(s, 11, 9, 10, 2, hair)
    elif head == "fur":
        rect(s, 9, 5, 14, 4, (100, 70, 44))
        rect(s, 11, 2, 10, 4, (40, 110, 70))
        for x in range(9, 23, 2):
            px(s, x, 5, (130, 96, 60))
    return pygame.transform.scale(s, (32 * k, 32 * k))


@cached
def hero_figure(k=4):
    """Pełna postać Damiana Ścisła – kronikarza w fioletowym kapturze."""
    a = asset("hero")
    if a:
        return pygame.transform.smoothscale(a, (22 * k, 36 * k))
    s = S(22, 36)
    robe, robe_d = (112, 52, 156), (82, 36, 118)
    # płaszcz
    poly(s, robe_d, [(5, 14), (17, 14), (19, 34), (3, 34)])
    poly(s, robe, [(6, 13), (16, 13), (17, 33), (5, 33)])
    line(s, (200, 170, 70), (11, 15), (11, 33))
    rect(s, 5, 22, 12, 1, (90, 60, 30))  # pas
    rect(s, 13, 22, 3, 3, (130, 90, 50))  # sakwa
    rect(s, 6, 34, 4, 2, (70, 50, 30)); rect(s, 12, 34, 4, 2, (70, 50, 30))
    # kaptur i twarz
    _ellipse(s, robe_d, (5, 2, 12, 13))
    _ellipse(s, SKIN, (7, 5, 8, 8))
    rect(s, 7, 5, 8, 2, (222, 184, 96))
    px(s, 9, 8, (30, 20, 20)); px(s, 12, 8, (30, 20, 20))
    rect(s, 10, 11, 2, 1, (170, 90, 80))
    poly(s, robe, [(5, 9), (8, 3), (11, 1), (15, 3), (17, 9), (15, 5), (11, 3), (7, 5)])
    px(s, 11, 0, robe)
    # księga i pióro
    rect(s, 1, 17, 6, 7, (140, 40, 40)); rect(s, 2, 18, 4, 5, (236, 222, 180)); line(s, (140, 40, 40), (4, 18), (4, 22))
    line(s, (240, 240, 240), (18, 12), (21, 6), 1); line(s, (250, 250, 250), (19, 11), (21, 8))
    rect(s, 16, 15, 3, 3, SKIN)
    return pygame.transform.scale(s, (22 * k, 36 * k))


# ------------------------------------------------------------------ IKONY
@cached
def icon(name, k=2):
    s = S(12, 12)
    if name == "food":
        poly(s, (220, 180, 80), [(2, 11), (6, 2), (10, 11)])
        for y in range(3, 10, 2):
            px(s, 5, y, (180, 140, 50)); px(s, 7, y + 1, (180, 140, 50))
        rect(s, 3, 8, 7, 1, (140, 100, 40))
    elif name == "wood":
        rect(s, 1, 4, 10, 4, (140, 96, 52)); pygame.draw.circle(s, (200, 160, 110), (10, 6), 2)
        rect(s, 2, 8, 9, 3, (120, 80, 44)); pygame.draw.circle(s, (190, 150, 100), (10, 9), 2)
        line(s, (100, 66, 36), (2, 5), (8, 5))
    elif name == "stone":
        poly(s, (150, 146, 136), [(1, 11), (3, 5), (7, 3), (11, 6), (11, 11)])
        line(s, (200, 196, 186), (3, 5), (7, 3)); line(s, (100, 96, 90), (1, 11), (11, 11))
        line(s, (110, 106, 100), (6, 6), (5, 10))
    elif name == "silver":
        pygame.draw.circle(s, (210, 214, 224), (6, 6), 5)
        pygame.draw.circle(s, (160, 164, 176), (6, 6), 5, 1)
        rect(s, 5, 4, 2, 4, (150, 154, 166)); px(s, 4, 4, (250, 250, 255))
    elif name == "turn":
        poly(s, (220, 200, 140), [(2, 1), (10, 1), (6, 6)]); poly(s, (220, 200, 140), [(2, 11), (10, 11), (6, 6)])
        rect(s, 1, 0, 10, 1, (120, 80, 40)); rect(s, 1, 11, 10, 1, (120, 80, 40))
        poly(s, (200, 160, 60), [(4, 10), (8, 10), (6, 8)])
    elif name == "tech":
        rect(s, 1, 2, 10, 8, (140, 40, 40)); rect(s, 2, 3, 8, 6, (236, 222, 180)); line(s, (140, 40, 40), (6, 3), (6, 8))
    elif name == "army":
        line(s, (200, 200, 210), (2, 10), (10, 2), 2); line(s, (200, 200, 210), (2, 2), (10, 10), 2)
        rect(s, 1, 9, 3, 2, (130, 90, 40)); rect(s, 8, 9, 3, 2, (130, 90, 40))
    elif name == "chronicle":
        rect(s, 2, 1, 8, 10, (90, 50, 130)); rect(s, 3, 2, 6, 8, (236, 222, 180))
        line(s, (60, 40, 30), (4, 4), (8, 4)); line(s, (60, 40, 30), (4, 6), (8, 6))
    elif name == "star":
        poly(s, (240, 200, 60), [(6, 0), (8, 4), (12, 4), (9, 7), (10, 11), (6, 9), (2, 11), (3, 7), (0, 4), (4, 4)])
    elif name == "check":
        line(s, (60, 170, 70), (1, 6), (4, 10), 2); line(s, (60, 170, 70), (4, 10), (11, 1), 2)
    elif name == "lock":
        rect(s, 2, 5, 8, 6, (160, 130, 60)); pygame.draw.arc(s, (120, 120, 120), (3, 0, 6, 10), 0, math.pi, 2)
    elif name == "shield":
        poly(s, (190, 40, 44), [(1, 1), (11, 1), (11, 6), (6, 11), (1, 6)])
        poly(s, (235, 235, 235), [(6, 1), (11, 1), (11, 6), (6, 11)])
    return pygame.transform.scale(s, (12 * k, 12 * k))


@cached
def event_icon(name):
    s = S(24, 24)
    if name == "plague":
        pygame.draw.circle(s, (120, 170, 90), (12, 12), 9)
        for a in range(8):
            x, y = 12 + math.cos(a * 0.785) * 10, 12 + math.sin(a * 0.785) * 10
            pygame.draw.circle(s, (90, 140, 70), (int(x), int(y)), 2)
        px(s, 9, 10, (30, 40, 20)); px(s, 14, 10, (30, 40, 20)); line(s, (30, 40, 20), (9, 15), (14, 15))
    elif name == "raid":
        line(s, (200, 200, 210), (3, 21), (20, 4), 3); line(s, (200, 200, 210), (3, 4), (20, 21), 3)
        rect(s, 2, 18, 5, 3, (140, 90, 40)); rect(s, 17, 18, 5, 3, (140, 90, 40))
    elif name == "envoy":
        rect(s, 4, 3, 16, 18, (236, 222, 180)); rect(s, 3, 2, 18, 3, (200, 180, 140)); rect(s, 3, 19, 18, 3, (200, 180, 140))
        for y in (8, 11, 14):
            line(s, (90, 70, 50), (7, y), (17, y))
        pygame.draw.circle(s, (180, 30, 30), (16, 18), 3)
    elif name == "sun":
        pygame.draw.circle(s, (250, 200, 60), (12, 12), 6)
        for a in range(8):
            x, y = 12 + math.cos(a * 0.785) * 10, 12 + math.sin(a * 0.785) * 10
            line(s, (250, 170, 40), (12 + math.cos(a * 0.785) * 7, 12 + math.sin(a * 0.785) * 7), (x, y), 2)
    elif name == "market":
        rect(s, 4, 12, 16, 9, (150, 108, 64))
        poly(s, (200, 50, 50), [(2, 12), (22, 12), (18, 4), (6, 4)])
        line(s, (240, 240, 240), (9, 4), (8, 12)); line(s, (240, 240, 240), (15, 4), (16, 12))
    elif name == "fire":
        poly(s, (240, 90, 30), [(5, 22), (19, 22), (20, 12), (15, 2), (13, 9), (9, 5), (4, 14)])
        poly(s, (250, 200, 60), [(9, 22), (16, 22), (16, 15), (13, 9), (10, 14)])
    elif name == "wheat":
        for x in (7, 12, 17):
            line(s, (200, 170, 70), (12, 22), (x, 6), 1)
            for y in range(6, 14, 2):
                px(s, x - 1, y, (230, 196, 80)); px(s, x + 1, y + 1, (230, 196, 80))
    elif name == "comet":
        pygame.draw.circle(s, (250, 250, 210), (17, 7), 3)
        for k in range(10):
            pygame.draw.circle(s, (180, 200, 250), (15 - k, 9 + k), max(1, 3 - k // 4))
    elif name == "scholar":
        rect(s, 3, 6, 18, 13, (90, 50, 130)); rect(s, 4, 7, 7, 11, (236, 222, 180)); rect(s, 13, 7, 7, 11, (236, 222, 180))
        for y in (10, 13):
            line(s, (60, 40, 30), (5, y), (9, y)); line(s, (60, 40, 30), (14, y), (18, y))
    elif name == "amber":
        poly(s, (230, 150, 40), [(12, 3), (19, 9), (16, 20), (8, 20), (5, 9)])
        poly(s, (250, 200, 90), [(12, 3), (15, 9), (12, 14), (9, 9)])
    return pygame.transform.scale(s, (72, 72))


# ------------------------------------------------------------------ UI
@cached
def parchment(w, h, seed=1, dark=False):
    r = random.Random(seed)
    hw, hh = max(1, w // 2), max(1, h // 2)
    s = pygame.Surface((hw, hh))
    base = (60, 44, 32) if dark else (234, 216, 172)
    s.fill(base)
    n = hw * hh // 6
    for _ in range(n):
        x, y = r.randrange(hw), r.randrange(hh)
        f = r.uniform(0.92, 1.05)
        px(s, x, y, shade(base, f))
    # winieta
    for i in range(6):
        c = shade(base, 0.96 - i * 0.03) if not dark else shade(base, 0.9 - i * 0.04)
        pygame.draw.rect(s, c, (i, i, hw - 2 * i, hh - 2 * i), 1)
    return pygame.transform.scale(s, (w, h))


def frame(surf, r, col=(92, 58, 30), gold=(206, 168, 80), width=3):
    pygame.draw.rect(surf, col, r, width)
    pygame.draw.rect(surf, gold, r.inflate(-2 * width - 2, -2 * width - 2), 1)
    for (x, y) in [(r.left, r.top), (r.right - 8, r.top), (r.left, r.bottom - 8), (r.right - 8, r.bottom - 8)]:
        pygame.draw.rect(surf, gold, (x, y, 8, 8))
        pygame.draw.rect(surf, col, (x + 2, y + 2, 4, 4))


def panel(w, h, seed=1, dark=False):
    s = parchment(w, h, seed, dark).copy()
    frame(s, s.get_rect())
    return s


@cached
def card_face(card_id, w=120, h=168):
    from . import data
    c = data.CARDS[card_id]
    ct = data.CARD_TYPES[c["type"]]
    s = parchment(w, h, sum(map(ord, card_id))).copy()
    pygame.draw.rect(s, ct["color"], (6, 6, w - 12, 22))
    art = pygame.Rect(10, 32, w - 20, 74)
    sky = mix((150, 180, 210), ct["color"], 0.25)
    for y in range(art.h):
        pygame.draw.line(s, mix(sky, (110, 140, 80), y / art.h), (art.x, art.y + y), (art.right - 1, art.y + y))
    pygame.draw.rect(s, (110, 140, 80), (art.x, art.bottom - 14, art.w, 14))
    u = unit_big(c["unit"], c["faction"], 3)
    s.blit(u, (art.centerx - u.get_width() // 2, art.bottom - u.get_height() - 2))
    pygame.draw.rect(s, (60, 40, 20), art, 2)
    frame(s, s.get_rect(), col=shade(ct["color"], 0.6))
    return s
