"""Proceduralna grafika gry: wszystkie sprite'y, kafelki i tła rysowane w kodzie."""
import math
import random
import pygame

T = 16
W, H = 480, 270

OUT = (34, 22, 18)

# ----------------------------------------------------------------- pomocnicze

def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def with_outline(surf, color=OUT):
    """Dodaje 1-pikselowy kontur w stylu kreskówki."""
    w, h = surf.get_size()
    mask = pygame.mask.from_surface(surf)
    sil = mask.to_surface(setcolor=color + (255,), unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    for ox, oy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        out.blit(sil, (ox, oy))
    out.blit(surf, (1, 1))
    return out


def rot_pivot(img, pivot, angle):
    """Obraca obraz wokół punktu pivot (w układzie obrazka). Zwraca (obraz, przesunięcie pivotu)."""
    w, h = img.get_size()
    center = pygame.math.Vector2(w / 2, h / 2)
    off = pygame.math.Vector2(pivot) - center
    rimg = pygame.transform.rotate(img, angle)
    roff = off.rotate(-angle)
    rc = pygame.math.Vector2(rimg.get_size()) / 2
    return rimg, rc + roff


def vgrad(w, h, top, bottom):
    s = pygame.Surface((w, h))
    for y in range(h):
        pygame.draw.line(s, mix(top, bottom, y / max(1, h - 1)), (0, y), (w, y))
    return s


# ----------------------------------------------------------------- postaci

SKIN = (244, 194, 150)
SKIN_D = (212, 150, 110)
HAIR = (250, 212, 96)
HAIR_D = (204, 158, 56)
FUR = (224, 138, 54)
FUR_D = (170, 94, 36)
SPOT = (106, 58, 24)
BOOT = (128, 84, 48)
BOOT_D = (92, 58, 32)


def make_club():
    s = pygame.Surface((9, 20), pygame.SRCALPHA)
    pygame.draw.rect(s, (120, 74, 38), (3, 7, 3, 13))
    pygame.draw.ellipse(s, (150, 96, 50), (0, 0, 9, 11))
    pygame.draw.ellipse(s, (176, 118, 64), (1, 1, 5, 6))
    for p in ((2, 7), (6, 4), (4, 2)):
        s.set_at(p, (96, 58, 28))
    return with_outline(s)


def draw_damian(pose, frame):
    """Damian – jaskiniowiec w skórze, blond czupryna. Zwraca powierzchnię 24x32 (patrzy w prawo)."""
    s = pygame.Surface((22, 30), pygame.SRCALPHA)
    bob = 0
    lf, rf = 0, 0
    if pose == 'walk':
        ph = frame % 4
        lf, rf = [(-3, 2), (0, 0), (3, -2), (0, 0)][ph]
        bob = [0, -1, 0, -1][ph]
    elif pose == 'idle':
        bob = 0 if (frame // 2) % 2 == 0 else -1 if frame % 4 == 1 else 0
    elif pose in ('jump', 'fall'):
        lf, rf = -2, 3
    y0 = 1 + bob
    # nogi
    if pose in ('jump', 'fall'):
        pygame.draw.rect(s, SKIN_D, (6, 22 + y0 - 2, 4, 5))
        pygame.draw.rect(s, SKIN, (12, 21 + y0 - 2, 4, 5))
        pygame.draw.rect(s, BOOT, (5, 25 + y0 - 2, 6, 3))
        pygame.draw.rect(s, BOOT, (12, 24 + y0 - 2, 6, 3))
    else:
        pygame.draw.rect(s, SKIN_D, (7 + lf, 22, 4, 5))
        pygame.draw.rect(s, SKIN, (12 + rf, 22, 4, 5))
        pygame.draw.rect(s, BOOT_D, (6 + lf, 26, 6, 3))
        pygame.draw.rect(s, BOOT, (11 + rf, 26, 6, 3))
    # tył ręki
    pygame.draw.rect(s, SKIN_D, (5, 13 + y0, 3, 7))
    # tunika ze skóry
    pts = [(7, 11 + y0), (15, 11 + y0), (17, 21 + y0), (5, 21 + y0)]
    pygame.draw.polygon(s, FUR, pts)
    for i in range(5, 18, 3):
        pygame.draw.polygon(s, FUR, [(i, 21 + y0), (i + 3, 21 + y0), (i + 1, 23 + y0)])
    pygame.draw.line(s, FUR_D, (8, 11 + y0), (15, 18 + y0), 2)
    for p in ((9, 16), (13, 19), (7, 19), (12, 14), (15, 20)):
        pygame.draw.rect(s, SPOT, (p[0], p[1] + y0, 2, 2))
    # szyja + ramię odkryte
    pygame.draw.rect(s, SKIN, (9, 9 + y0, 4, 3))
    pygame.draw.rect(s, SKIN, (6, 11 + y0, 3, 3))
    # głowa
    pygame.draw.ellipse(s, SKIN, (6, 1 + y0, 12, 11))
    pygame.draw.rect(s, SKIN_D, (7, 9 + y0, 9, 2))  # zarost
    s.set_at((15, 6 + y0), (30, 24, 24))
    s.set_at((15, 5 + y0), (30, 24, 24))
    s.set_at((12, 6 + y0), (30, 24, 24))
    s.set_at((12, 5 + y0), (30, 24, 24))
    pygame.draw.line(s, HAIR_D, (11, 3 + y0), (16, 3 + y0))
    s.set_at((18, 7 + y0), SKIN)
    s.set_at((17, 7 + y0), SKIN_D)
    pygame.draw.line(s, (150, 70, 60), (13, 9 + y0), (16, 9 + y0))
    # czupryna blond
    pygame.draw.ellipse(s, HAIR, (4, -1 + y0, 14, 7))
    pygame.draw.rect(s, HAIR, (4, 2 + y0, 4, 7))
    for x, yy in ((4, 0), (7, -1), (10, -2), (13, -1), (16, 0), (3, 3), (3, 6)):
        pygame.draw.rect(s, HAIR, (x, yy + y0, 3, 3))
    for x, yy in ((6, 1), (9, 0), (12, 1), (5, 5)):
        s.set_at((x, yy + y0), HAIR_D)
    pygame.draw.rect(s, (230, 70, 60), (5, 3 + y0, 12, 1))  # opaska
    # przednia ręka (trzyma maczugę)
    pygame.draw.line(s, SKIN, (14, 12 + y0), (16, 18 + y0), 3)
    pygame.draw.rect(s, SKIN_D, (15, 17 + y0, 3, 3))
    if pose == 'hurt':
        s.fill((255, 120, 120, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return with_outline(s)


def draw_kid(hair, tunic, girl, frame, happy=False):
    s = pygame.Surface((14, 19), pygame.SRCALPHA)
    bob = -1 if (frame // 8) % 2 and happy else 0
    lf = [0, 1, 0, -1][frame % 4] if happy else 0
    pygame.draw.rect(s, SKIN_D, (4 + lf, 14, 3, 4))
    pygame.draw.rect(s, SKIN, (8 - lf, 14, 3, 4))
    pygame.draw.rect(s, BOOT, (3 + lf, 17, 4, 2))
    pygame.draw.rect(s, BOOT, (8 - lf, 17, 4, 2))
    pygame.draw.polygon(s, tunic, [(4, 8 + bob), (10, 8 + bob), (12, 15 + bob), (2, 15 + bob)])
    d = mix(tunic, (0, 0, 0), 0.35)
    pygame.draw.rect(s, d, (5, 11 + bob, 1, 1))
    pygame.draw.rect(s, d, (8, 13 + bob, 1, 1))
    if happy:
        pygame.draw.line(s, SKIN, (3, 9 + bob), (0, 5 + bob), 2)
        pygame.draw.line(s, SKIN, (10, 9 + bob), (13, 5 + bob), 2)
    else:
        pygame.draw.rect(s, SKIN, (2, 9 + bob, 2, 4))
        pygame.draw.rect(s, SKIN, (10, 9 + bob, 2, 4))
    pygame.draw.ellipse(s, SKIN, (3, 1 + bob, 9, 8))
    s.set_at((6, 4 + bob), (30, 24, 24))
    s.set_at((9, 4 + bob), (30, 24, 24))
    if happy:
        pygame.draw.line(s, (160, 60, 60), (6, 6 + bob), (9, 6 + bob))
    else:
        s.set_at((7, 7 + bob), (160, 60, 60))
        s.set_at((8, 7 + bob), (160, 60, 60))
    pygame.draw.ellipse(s, hair, (2, 0 + bob, 11, 4))
    pygame.draw.rect(s, hair, (2, 1 + bob, 2, 4))
    if girl:
        pygame.draw.rect(s, hair, (11, 1 + bob, 2, 7))
        pygame.draw.circle(s, hair, (12, 8 + bob), 2)
        s.set_at((12, 3 + bob), (230, 80, 120))
    return with_outline(s)


def draw_boar(frame, hurt=False):
    s = pygame.Surface((26, 17), pygame.SRCALPHA)
    body = (126, 82, 54)
    dark = (84, 52, 34)
    lf = [0, 1, 0, -1][frame % 4]
    for x, o in ((5, lf), (9, -lf), (16, lf), (20, -lf)):
        pygame.draw.rect(s, dark, (x + o, 11, 3, 5))
    pygame.draw.ellipse(s, body, (2, 3, 20, 12))
    for x in range(4, 18, 3):
        pygame.draw.line(s, dark, (x, 3), (x + 1, 1))
    pygame.draw.ellipse(s, body, (15, 5, 10, 9))
    pygame.draw.rect(s, (220, 150, 140), (22, 9, 4, 3))
    s.set_at((19, 7), (20, 10, 10))
    pygame.draw.line(s, (250, 246, 230), (21, 12), (23, 8))
    pygame.draw.polygon(s, dark, [(16, 5), (18, 1), (19, 6)])
    pygame.draw.line(s, dark, (2, 6), (0, 4))
    if hurt:
        s.fill((120, 60, 60, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return with_outline(s)


def draw_wolf(frame, hurt=False):
    s = pygame.Surface((28, 17), pygame.SRCALPHA)
    body = (150, 152, 160)
    dark = (96, 98, 110)
    light = (210, 212, 216)
    lf = [0, 2, 0, -2][frame % 4]
    for x, o in ((5, lf), (8, -lf), (18, lf), (21, -lf)):
        pygame.draw.rect(s, dark, (x + o, 10, 2, 6))
    pygame.draw.ellipse(s, body, (3, 4, 20, 9))
    pygame.draw.ellipse(s, light, (8, 8, 12, 5))
    pygame.draw.polygon(s, body, [(4, 6), (0, 2), (1, 7)])
    pygame.draw.ellipse(s, body, (18, 2, 8, 7))
    pygame.draw.polygon(s, body, [(23, 5), (28, 7), (23, 8)])
    pygame.draw.polygon(s, dark, [(19, 3), (20, 0), (22, 3)])
    pygame.draw.polygon(s, dark, [(22, 3), (23, 0), (24, 3)])
    s.set_at((23, 4), (250, 220, 60))
    s.set_at((27, 7), (20, 20, 20))
    if hurt:
        s.fill((120, 60, 60, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return with_outline(s)


def draw_bat(frame):
    s = pygame.Surface((18, 10), pygame.SRCALPHA)
    c = (72, 54, 86)
    w = [0, 3, 5, 3][frame % 4]
    pygame.draw.ellipse(s, c, (6, 2, 6, 6))
    pygame.draw.polygon(s, c, [(7, 4), (0, 1 + w), (3, 6 + w // 2)])
    pygame.draw.polygon(s, c, [(11, 4), (18, 1 + w), (15, 6 + w // 2)])
    pygame.draw.polygon(s, c, [(7, 3), (7, 0), (9, 2)])
    pygame.draw.polygon(s, c, [(11, 3), (11, 0), (9, 2)])
    s.set_at((8, 4), (255, 70, 70))
    s.set_at((10, 4), (255, 70, 70))
    return with_outline(s)


def draw_bat_hang():
    s = pygame.Surface((8, 11), pygame.SRCALPHA)
    c = (72, 54, 86)
    pygame.draw.ellipse(s, c, (0, 1, 8, 10))
    pygame.draw.line(s, c, (3, 0), (3, 2))
    pygame.draw.line(s, c, (5, 0), (5, 2))
    return with_outline(s)


def draw_lion(frame, mode='run'):
    s = pygame.Surface((54, 32), pygame.SRCALPHA)
    body = (206, 166, 104)
    dark = (154, 112, 62)
    mane = (150, 98, 50)
    lf = [0, 3, 0, -3][frame % 4] if mode == 'run' else 0
    for x, o in ((8, lf), (14, -lf), (34, lf), (40, -lf)):
        pygame.draw.rect(s, dark, (x + o, 20, 5, 11))
        pygame.draw.rect(s, body, (x + o - 1, 28, 7, 3))
    pygame.draw.ellipse(s, body, (4, 8, 40, 18))
    pygame.draw.ellipse(s, mix(body, (255, 240, 220), 0.4), (12, 16, 26, 9))
    tail = [(5, 12), (0, 8), (1, 3)]
    pygame.draw.lines(s, dark, False, tail, 2)
    pygame.draw.circle(s, mane, (1, 3), 2)
    pygame.draw.ellipse(s, mane, (34, 2, 16, 20))
    pygame.draw.ellipse(s, body, (39, 6, 14, 13))
    pygame.draw.polygon(s, mane, [(39, 6), (41, 1), (44, 5)])
    if mode == 'stun':
        pygame.draw.line(s, (40, 20, 10), (45, 9), (48, 12))
        pygame.draw.line(s, (40, 20, 10), (48, 9), (45, 12))
    else:
        pygame.draw.rect(s, (255, 230, 80), (46, 9, 3, 2))
        s.set_at((47, 9), (20, 10, 10))
    pygame.draw.rect(s, (90, 50, 40), (51, 13, 2, 2))
    if mode in ('roar', 'run'):
        pygame.draw.polygon(s, (120, 30, 30), [(44, 16), (53, 15), (52, 19)])
        s.set_at((50, 16), (255, 255, 255))
        s.set_at((46, 17), (255, 255, 255))
    return with_outline(s)


def draw_mammoth(frame):
    s = pygame.Surface((50, 40), pygame.SRCALPHA)
    fur = (120, 76, 44)
    dark = (82, 50, 28)
    lf = [0, 1, 0, -1][(frame // 2) % 4]
    for x, o in ((8, lf), (16, -lf), (30, lf), (37, -lf)):
        pygame.draw.rect(s, dark, (x + o, 27, 7, 12))
    pygame.draw.ellipse(s, fur, (2, 6, 42, 28))
    pygame.draw.ellipse(s, fur, (14, 0, 22, 18))
    for x in range(4, 42, 3):
        pygame.draw.line(s, dark, (x, 24), (x + 1, 32))
    pygame.draw.ellipse(s, fur, (34, 8, 14, 16))
    pygame.draw.lines(s, fur, False, [(44, 20), (47, 28), (46, 35), (43, 37)], 4)
    pygame.draw.arc(s, (248, 240, 220), (34, 18, 16, 16), math.pi * 1.0, math.pi * 1.9, 2)
    s.set_at((42, 13), (20, 10, 10))
    pygame.draw.line(s, dark, (2, 16), (0, 22), 2)
    return with_outline(s)


def draw_stalactite(ice=False):
    s = pygame.Surface((10, 16), pygame.SRCALPHA)
    if ice:
        c, d = (190, 230, 250), (120, 180, 220)
    else:
        c, d = (130, 112, 100), (90, 76, 70)
    pygame.draw.polygon(s, c, [(0, 0), (10, 0), (5, 15)])
    pygame.draw.line(s, d, (6, 1), (5, 12))
    if ice:
        pygame.draw.line(s, (250, 255, 255), (3, 1), (5, 9))
    return with_outline(s)


# ----------------------------------------------------------------- przedmioty

def draw_item(kind, frame=0):
    s = pygame.Surface((12, 12), pygame.SRCALPHA)
    if kind == 'b':  # jagody
        pygame.draw.ellipse(s, (70, 150, 60), (1, 0, 8, 4))
        for p in ((3, 6), (7, 6), (5, 9), (8, 9), (2, 9)):
            pygame.draw.circle(s, (120, 60, 160), p, 2)
            s.set_at((p[0] - 1, p[1] - 1), (210, 170, 240))
    elif kind == 'm':  # udziec
        pygame.draw.line(s, (245, 240, 225), (2, 10), (5, 7), 2)
        pygame.draw.circle(s, (245, 240, 225), (2, 10), 1)
        pygame.draw.ellipse(s, (176, 78, 50), (4, 1, 8, 8))
        pygame.draw.ellipse(s, (220, 120, 80), (6, 2, 4, 3))
    elif kind == 'f':  # krzemień
        pygame.draw.polygon(s, (78, 80, 96), [(2, 9), (5, 2), (10, 4), (9, 10)])
        pygame.draw.line(s, (200, 205, 220), (5, 2), (10, 4))
        pygame.draw.line(s, (130, 134, 150), (4, 8), (7, 5))
    elif kind == 'h':  # serce – zioło życia
        pygame.draw.circle(s, (230, 50, 70), (4, 5), 3)
        pygame.draw.circle(s, (230, 50, 70), (8, 5), 3)
        pygame.draw.polygon(s, (230, 50, 70), [(1, 6), (11, 6), (6, 11)])
        s.set_at((3, 4), (255, 200, 200))
    elif kind == 'stone':
        pygame.draw.circle(s, (110, 110, 124), (6, 6), 3)
        s.set_at((5, 5), (190, 190, 205))
    return with_outline(s)


def draw_heart_icon(full=True):
    s = pygame.Surface((11, 10), pygame.SRCALPHA)
    c = (232, 52, 72) if full else (70, 50, 60)
    pygame.draw.circle(s, c, (3, 3), 3)
    pygame.draw.circle(s, c, (7, 3), 3)
    pygame.draw.polygon(s, c, [(0, 4), (10, 4), (5, 9)])
    if full:
        s.set_at((2, 2), (255, 210, 210))
    return with_outline(s)


def draw_boulder():
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(s, (128, 120, 112), (8, 8), 8)
    pygame.draw.circle(s, (160, 152, 140), (6, 6), 4)
    pygame.draw.circle(s, (96, 90, 84), (11, 11), 2)
    s.set_at((4, 10), (96, 90, 84))
    return s


def draw_torch(lit, frame):
    s = pygame.Surface((12, 24), pygame.SRCALPHA)
    pygame.draw.rect(s, (110, 70, 38), (5, 9, 3, 15))
    pygame.draw.rect(s, (80, 50, 30), (3, 8, 7, 3))
    if lit:
        fl = [0, 1, 0, -1][frame % 4]
        pygame.draw.ellipse(s, (240, 90, 30), (2 + fl // 2, 0, 8, 10))
        pygame.draw.ellipse(s, (255, 190, 60), (3 + fl, 3, 5, 6))
        pygame.draw.ellipse(s, (255, 250, 200), (5, 5, 2, 3))
    return with_outline(s)


def draw_exit(theme):
    """Wejście do jaskini/szałas z kości mamuta (32x48)."""
    s = pygame.Surface((36, 46), pygame.SRCALPHA)
    if theme in ('cave', 'lair'):
        pygame.draw.ellipse(s, (96, 84, 80), (0, 0, 36, 56))
        pygame.draw.ellipse(s, (10, 6, 12), (6, 8, 24, 48))
    else:
        pygame.draw.polygon(s, (150, 104, 62), [(18, 0), (0, 46), (36, 46)])
        pygame.draw.polygon(s, (120, 80, 46), [(18, 4), (4, 46), (32, 46)])
        for i in range(6):
            y = 10 + i * 6
            pygame.draw.arc(s, (240, 232, 210), (8 - i, y, 20 + i * 2, 10), 0, math.pi, 2)
        pygame.draw.polygon(s, (20, 12, 10), [(18, 24), (11, 46), (25, 46)])
    return s


def draw_rune(sym, lit):
    s = pygame.Surface((16, 20), pygame.SRCALPHA)
    base = (120, 112, 104) if not lit else (150, 120, 90)
    pygame.draw.rect(s, base, (0, 2, 16, 18), border_radius=4)
    pygame.draw.rect(s, mix(base, (255, 255, 255), 0.2), (2, 3, 12, 2))
    col = (255, 170, 60) if lit else (60, 50, 46)
    draw_symbol(s, sym, 8, 12, 5, col)
    return with_outline(s)


def draw_symbol(surf, sym, cx, cy, r, col):
    """0=żubr 1=koń 2=dłoń 3=słońce – motywy jak w sztuce jaskiniowej."""
    if sym == 0:
        pygame.draw.ellipse(surf, col, (cx - r, cy - r // 2, r * 2, r + 1))
        pygame.draw.circle(surf, col, (cx - r // 2, cy - r // 2), max(1, r // 2))
        pygame.draw.line(surf, col, (cx + r - 1, cy), (cx + r + 1, cy - r // 2))
        pygame.draw.line(surf, col, (cx - r + 1, cy + r // 2), (cx - r + 1, cy + r))
        pygame.draw.line(surf, col, (cx + r - 2, cy + r // 2), (cx + r - 2, cy + r))
    elif sym == 1:
        pygame.draw.ellipse(surf, col, (cx - r, cy - r // 3, r * 2 - 2, r - 1))
        pygame.draw.line(surf, col, (cx + r - 3, cy), (cx + r, cy - r), 2)
        pygame.draw.line(surf, col, (cx + r, cy - r), (cx + r + 1, cy - r + 2), 2)
        pygame.draw.line(surf, col, (cx - r + 1, cy + r // 2), (cx - r, cy + r))
        pygame.draw.line(surf, col, (cx + r - 3, cy + r // 2), (cx + r - 3, cy + r))
    elif sym == 2:
        pygame.draw.ellipse(surf, col, (cx - r + 1, cy - 1, r * 2 - 2, r + 1))
        for i in range(4):
            x = cx - r + 2 + i * (r * 2 - 3) // 3
            pygame.draw.line(surf, col, (x, cy), (x, cy - r))
        pygame.draw.line(surf, col, (cx - r + 1, cy + 1), (cx - r - 1, cy - 2))
    else:
        pygame.draw.circle(surf, col, (cx, cy), max(2, r // 2 + 1))
        for i in range(8):
            a = i * math.pi / 4
            pygame.draw.line(surf, col, (cx + math.cos(a) * (r // 2 + 2), cy + math.sin(a) * (r // 2 + 2)),
                             (cx + math.cos(a) * (r + 1), cy + math.sin(a) * (r + 1)))


def draw_painting(order):
    """Malowidło naskalne z kolejnością symboli."""
    s = pygame.Surface((44, 26), pygame.SRCALPHA)
    pygame.draw.rect(s, (150, 120, 96), (0, 0, 44, 26), border_radius=3)
    pygame.draw.rect(s, (170, 140, 110), (2, 2, 40, 22), border_radius=3)
    for i, sym in enumerate(order):
        draw_symbol(s, sym, 7 + i * 10, 13, 4, (150, 40, 30))
    return with_outline(s)


def draw_hint_stone():
    s = pygame.Surface((16, 18), pygame.SRCALPHA)
    pygame.draw.polygon(s, (128, 122, 116), [(2, 18), (0, 6), (4, 0), (12, 0), (16, 6), (14, 18)])
    pygame.draw.polygon(s, (150, 144, 136), [(3, 16), (2, 6), (5, 2), (8, 2), (6, 16)])
    for y in (6, 9, 12):
        pygame.draw.line(s, (80, 70, 64), (5, y), (11, y))
    s.set_at((8, 4), (80, 70, 64))
    return with_outline(s)


# ----------------------------------------------------------------- motywy / kafelki

THEMES = {
    'valley': dict(top=(88, 178, 64), top2=(140, 214, 90), dirt=(132, 88, 54), dirt2=(104, 66, 40),
                   stone=(156, 132, 104), plat=(150, 100, 56), spike=(232, 228, 214), water=(60, 130, 210),
                   dark=0),
    'ice': dict(top=(236, 244, 252), top2=(255, 255, 255), dirt=(108, 130, 160), dirt2=(84, 104, 136),
                stone=(160, 186, 214), plat=(130, 100, 70), spike=(200, 236, 255), water=(40, 90, 160),
                dark=0),
    'cave': dict(top=(120, 104, 96), top2=(150, 132, 120), dirt=(84, 70, 66), dirt2=(64, 52, 50),
                 stone=(110, 96, 90), plat=(120, 86, 56), spike=(186, 176, 160), water=(40, 70, 120),
                 dark=222),
    'lair': dict(top=(150, 92, 70), top2=(186, 120, 86), dirt=(96, 56, 50), dirt2=(72, 40, 40),
                 stone=(130, 90, 80), plat=(120, 80, 50), spike=(240, 226, 206), water=(160, 50, 30),
                 dark=150),
}


def make_tiles(theme, seed=1):
    th = THEMES[theme]
    rnd = random.Random(seed)
    tiles = {}

    def dirt_tile():
        s = pygame.Surface((T, T))
        s.fill(th['dirt'])
        for _ in range(10):
            x, y = rnd.randrange(T), rnd.randrange(T)
            pygame.draw.rect(s, th['dirt2'], (x, y, 2, 1))
        for _ in range(2):
            x, y = rnd.randrange(1, T - 4), rnd.randrange(1, T - 3)
            pygame.draw.ellipse(s, th['stone'], (x, y, 4, 3))
        return s

    tiles['fill'] = [dirt_tile() for _ in range(4)]
    tops = []
    for _ in range(3):
        s = dirt_tile()
        pygame.draw.rect(s, th['top'], (0, 0, T, 5))
        for x in range(0, T, 2):
            hgt = rnd.randint(4, 7)
            pygame.draw.line(s, th['top'], (x, 0), (x, hgt))
        pygame.draw.line(s, th['top2'], (0, 0), (T, 0))
        pygame.draw.line(s, th['top2'], (0, 1), (T, 1))
        tops.append(s)
    tiles['top'] = tops
    # platforma (kłoda)
    p = pygame.Surface((T, T), pygame.SRCALPHA)
    pygame.draw.rect(p, th['plat'], (0, 1, T, 6))
    pygame.draw.line(p, mix(th['plat'], (255, 255, 255), 0.3), (0, 2), (T, 2))
    pygame.draw.line(p, mix(th['plat'], (0, 0, 0), 0.4), (0, 6), (T, 6))
    pygame.draw.line(p, mix(th['plat'], (0, 0, 0), 0.4), (5, 3), (9, 3))
    pygame.draw.line(p, OUT, (0, 0), (T, 0))
    pygame.draw.line(p, OUT, (0, 7), (T, 7))
    tiles['plat'] = p
    # kolce (zaostrzone kości/kamienie)
    sp = pygame.Surface((T, T), pygame.SRCALPHA)
    for i in range(3):
        x = i * 5 + 1
        pygame.draw.polygon(sp, th['spike'], [(x, T), (x + 2, 5), (x + 5, T)])
        pygame.draw.polygon(sp, OUT, [(x, T), (x + 2, 5), (x + 5, T)], 1)
    tiles['spike'] = sp
    # lód
    ic = pygame.Surface((T, T))
    ic.fill((150, 210, 240))
    pygame.draw.line(ic, (230, 250, 255), (2, 3), (8, 3))
    pygame.draw.line(ic, (230, 250, 255), (3, 9), (5, 7))
    pygame.draw.line(ic, (110, 170, 210), (0, T - 1), (T, T - 1))
    pygame.draw.rect(ic, (90, 150, 200), (0, 0, T, T), 1)
    tiles['ice'] = ic
    # woda (klatki animacji)
    water = []
    for f in range(4):
        w = pygame.Surface((T, T), pygame.SRCALPHA)
        w.fill(th['water'] + (210,))
        for x in range(T):
            y = int(2 + math.sin((x + f * 4) / T * math.pi * 2) * 1.5)
            pygame.draw.line(w, mix(th['water'], (255, 255, 255), 0.5) + (255,), (x, y), (x, y + 1))
        water.append(w)
    tiles['water'] = water
    wfill = pygame.Surface((T, T), pygame.SRCALPHA)
    wfill.fill(mix(th['water'], (0, 0, 30), 0.3) + (220,))
    tiles['water_fill'] = wfill
    # wrota / brama
    d = pygame.Surface((T, T))
    d.fill((120, 110, 100))
    pygame.draw.rect(d, (150, 140, 128), (1, 1, T - 2, T - 2))
    pygame.draw.line(d, (90, 80, 74), (0, T - 1), (T, T - 1))
    pygame.draw.circle(d, (90, 80, 74), (8, 8), 3, 1)
    tiles['door'] = d
    g = pygame.Surface((T, T), pygame.SRCALPHA)
    for x in (2, 7, 12):
        pygame.draw.rect(g, (236, 228, 204), (x, 0, 3, T))
        pygame.draw.rect(g, OUT, (x, 0, 3, T), 1)
    pygame.draw.rect(g, (150, 100, 60), (0, 6, T, 3))
    tiles['gate'] = g
    for name, h in (('plate', 4), ('plate_down', 2)):
        pl = pygame.Surface((T, T), pygame.SRCALPHA)
        pygame.draw.rect(pl, (170, 160, 140), (1, T - h, T - 2, h))
        pygame.draw.rect(pl, OUT, (1, T - h, T - 2, h), 1)
        draw_symbol(pl, 2, 8, T - 8, 3, (200, 80, 50)) if name == 'plate' else None
        tiles[name] = pl
    return tiles


def decor_for(theme, rnd):
    """Losowa dekoracja na wierzchu gruntu."""
    s = pygame.Surface((T, 10), pygame.SRCALPHA)
    k = rnd.random()
    if theme == 'valley':
        if k < 0.35:
            for i in range(3):
                x = rnd.randrange(2, 14)
                pygame.draw.line(s, (60, 140, 50), (x, 10), (x + rnd.choice((-2, 2)), 4))
        elif k < 0.5:
            x = rnd.randrange(3, 12)
            pygame.draw.line(s, (60, 140, 50), (x, 10), (x, 5))
            pygame.draw.circle(s, rnd.choice([(250, 220, 60), (240, 110, 140), (250, 250, 250)]), (x, 4), 2)
        elif k < 0.58:
            pygame.draw.ellipse(s, (150, 140, 130), (3, 5, 9, 5))
        else:
            return None
    elif theme == 'ice':
        if k < 0.3:
            pygame.draw.ellipse(s, (255, 255, 255), (1, 6, 14, 6))
        elif k < 0.38:
            x = rnd.randrange(3, 12)
            pygame.draw.line(s, (90, 70, 50), (x, 10), (x, 3))
            pygame.draw.line(s, (90, 70, 50), (x, 6), (x + 3, 3))
        else:
            return None
    elif theme in ('cave', 'lair'):
        if k < 0.25:
            x = rnd.randrange(3, 10)
            pygame.draw.polygon(s, (120, 104, 96), [(x, 10), (x + 3, 2), (x + 6, 10)])
        elif k < 0.37:
            pygame.draw.line(s, (236, 228, 204), (3, 9), (12, 7), 2)
            pygame.draw.circle(s, (236, 228, 204), (3, 9), 2)
            pygame.draw.circle(s, (236, 228, 204), (12, 7), 2)
        elif k < 0.42 and theme == 'cave':
            pygame.draw.circle(s, (120, 240, 200), (8, 8), 2)  # świecący grzyb
            pygame.draw.line(s, (200, 200, 180), (8, 10), (8, 8))
        else:
            return None
    return s


# ----------------------------------------------------------------- tła

def _ridge(width, base, amps, rnd):
    phases = [rnd.random() * math.tau for _ in amps]
    pts = []
    for x in range(0, width + 1, 2):
        y = base
        for i, a in enumerate(amps):
            k = i + 1
            y += a * math.sin(math.tau * k * x / width + phases[i])
        pts.append((x, int(y)))
    return pts


def layer_mountains(width, base, amps, color, snow=None, seed=1, height=H):
    rnd = random.Random(seed)
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    pts = _ridge(width, base, amps, rnd)
    pygame.draw.polygon(s, color, pts + [(width, height), (0, height)])
    if snow:
        for i in range(len(pts) - 1):
            x, y = pts[i]
            if y < base - sum(amps) * 0.35:
                pygame.draw.line(s, snow, (x, y), (x, y + 4 + (base - y) // 8), 2)
    return s


def layer_trees(width, base, color, seed=2, kind='pine', height=H):
    rnd = random.Random(seed)
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    pts = _ridge(width, base, [6, 3], rnd)
    pygame.draw.polygon(s, color, pts + [(width, height), (0, height)])
    x = 0
    while x < width - 10:
        y = pts[min(len(pts) - 1, x // 2)][1]
        h = rnd.randint(18, 34)
        if kind == 'pine':
            for i in range(3):
                ww = 12 - i * 3
                pygame.draw.polygon(s, color, [(x - ww, y - i * h // 4), (x, y - h + i * 2 - 2), (x + ww, y - i * h // 4)])
        elif kind == 'snowpine':
            for i in range(3):
                ww = 12 - i * 3
                pygame.draw.polygon(s, color, [(x - ww, y - i * h // 4), (x, y - h + i * 2 - 2), (x + ww, y - i * h // 4)])
                pygame.draw.line(s, (240, 248, 255), (x - ww + 2, y - i * h // 4 - 1), (x, y - h + i * 2), 1)
        else:  # skały
            pygame.draw.polygon(s, color, [(x - 8, y), (x - 3, y - h // 2), (x + 4, y - h // 2 - 4), (x + 9, y)])
        x += rnd.randint(10, 26)
    return s


def layer_cave(width, color, seed=3, height=H):
    rnd = random.Random(seed)
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    top = _ridge(width, 30, [10, 6, 3], rnd)
    pygame.draw.polygon(s, color, top + [(width, 0), (0, 0)])
    bot = _ridge(width, height - 40, [12, 5, 3], rnd)
    pygame.draw.polygon(s, color, bot + [(width, height), (0, height)])
    x = 0
    while x < width - 8:
        y = top[x // 2][1]
        h = rnd.randint(10, 46)
        pygame.draw.polygon(s, color, [(x - 5, y - 2), (x, y + h), (x + 5, y - 2)])
        if rnd.random() < 0.35:
            x2 = x + rnd.randint(4, 14)
            if x2 < width:
                yb = bot[min(len(bot) - 1, x2 // 2)][1]
                pygame.draw.polygon(s, color, [(x2 - 6, yb + 2), (x2, yb - h // 2), (x2 + 6, yb + 2)])
        x += rnd.randint(14, 40)
    return s


def make_background(theme):
    """Zwraca (niebo, [ (warstwa, współczynnik_paralaksy, y) ])."""
    layers = []
    if theme == 'valley':
        sky = vgrad(W, H, (96, 166, 236), (214, 236, 246))
        pygame.draw.circle(sky, (255, 246, 190), (390, 52), 22)
        pygame.draw.circle(sky, (255, 252, 230), (390, 52), 16)
        clouds = pygame.Surface((W * 2, 120), pygame.SRCALPHA)
        rnd = random.Random(5)
        for _ in range(9):
            x, y = rnd.randrange(0, W * 2 - 60), rnd.randrange(10, 80)
            for i in range(4):
                pygame.draw.ellipse(clouds, (255, 255, 255, 220), (x + i * 12, y - (i % 2) * 6, 30, 16))
        layers.append((clouds, 0.08, 0))
        layers.append((layer_mountains(W * 2, 150, [26, 14, 8], (134, 150, 196), (240, 246, 255), 7), 0.18, 0))
        layers.append((layer_mountains(W * 2, 190, [14, 8, 5], (106, 156, 120), None, 8), 0.32, 0))
        layers.append((layer_trees(W * 2, 214, (62, 120, 74), 9, 'pine'), 0.55, 0))
    elif theme == 'ice':
        sky = vgrad(W, H, (140, 172, 214), (228, 236, 246))
        layers.append((layer_mountains(W * 2, 140, [34, 16, 9], (190, 206, 230), (255, 255, 255), 11), 0.15, 0))
        layers.append((layer_mountains(W * 2, 185, [18, 10, 4], (150, 176, 208), (246, 250, 255), 12), 0.3, 0))
        layers.append((layer_trees(W * 2, 215, (84, 116, 128), 13, 'snowpine'), 0.55, 0))
    elif theme == 'cave':
        sky = vgrad(W, H, (34, 26, 32), (52, 40, 42))
        layers.append((layer_cave(W * 2, (46, 36, 40), 21), 0.25, 0))
        far = layer_cave(W * 2, (60, 46, 48), 22)
        # malowidła naskalne w tle
        rnd = random.Random(23)
        for _ in range(7):
            x, y = rnd.randrange(40, W * 2 - 40), rnd.randrange(80, 150)
            draw_symbol(far, rnd.randrange(4), x, y, 7, (120, 50, 40, 255))
        layers.append((far, 0.5, 0))
    else:  # lair
        sky = vgrad(W, H, (54, 26, 58), (236, 128, 70))
        pygame.draw.circle(sky, (255, 150, 90), (120, 150), 40)
        pygame.draw.circle(sky, (255, 190, 120), (120, 150), 30)
        layers.append((layer_mountains(W * 2, 150, [34, 18, 7], (90, 46, 76), (200, 140, 160), 31), 0.15, 0))
        layers.append((layer_mountains(W * 2, 190, [20, 9, 5], (66, 34, 54), None, 32), 0.3, 0))
        layers.append((layer_trees(W * 2, 218, (44, 24, 38), 33, 'rock'), 0.55, 0))
    return sky, layers


# ----------------------------------------------------------------- światło

def make_light(radius, dark_rgb, alpha_max):
    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    s.fill(dark_rgb + (alpha_max,))
    for r in range(radius, 0, -2):
        a = int(alpha_max * (r / radius) ** 1.6)
        pygame.draw.circle(s, dark_rgb + (a,), (radius, radius), r)
    return s


def make_glow(radius, color):
    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -2):
        t = 1 - r / radius
        pygame.draw.circle(s, tuple(int(c * t * 0.5) for c in color), (radius, radius), r)
    return s


# ----------------------------------------------------------------- sceny fabularne

def _hut(s, x, y, sc=1.0):
    w = int(46 * sc)
    h = int(36 * sc)
    pygame.draw.polygon(s, (110, 74, 46), [(x, y), (x - w // 2, y + h), (x + w // 2, y + h)])
    for i in range(5):
        yy = y + 6 + i * int(6 * sc)
        pygame.draw.arc(s, (230, 222, 200), (x - 6 - i * 3, yy, 12 + i * 6, 8), 0, math.pi, 2)
    pygame.draw.polygon(s, (24, 14, 12), [(x, y + h // 2), (x - 7, y + h), (x + 7, y + h)])


def _fire(s, x, y, t, big=1.0):
    pygame.draw.line(s, (100, 60, 30), (x - 10, y + 2), (x + 10, y - 2), 3)
    pygame.draw.line(s, (100, 60, 30), (x - 10, y - 2), (x + 10, y + 2), 3)
    for i in range(3):
        fl = math.sin(t * 9 + i * 2) * 2
        hh = (16 - i * 4) * big
        ww = (12 - i * 3) * big
        col = [(230, 80, 30), (255, 170, 50), (255, 245, 190)][i]
        pygame.draw.ellipse(s, col, (x - ww / 2 + fl / 2, y - hh, ww, hh + 2))


def story_scene(name, t, sprites):
    """Rysuje ilustrację do planszy fabularnej (480x270)."""
    night = name in ('camp', 'dark', 'tracks', 'promise')
    if name == 'end':
        s = vgrad(W, H, (40, 30, 70), (230, 140, 90))
    elif night:
        s = vgrad(W, H, (10, 12, 34), (40, 46, 84))
    elif name == 'painting':
        s = vgrad(W, H, (52, 40, 40), (70, 54, 50))
    else:
        s = vgrad(W, H, (96, 166, 236), (214, 236, 246))
    rnd = random.Random(4)
    if night or name == 'end':
        for _ in range(70):
            x, y = rnd.randrange(W), rnd.randrange(150)
            if (x * 7 + int(t * 3)) % 11:
                s.set_at((x, y), (255, 255, 230))
        pygame.draw.circle(s, (240, 240, 220), (400, 112), 14)
        pygame.draw.circle(s, mix((10, 12, 34), (40, 46, 84), 0.45), (406, 108), 12)
    if name == 'painting':
        pygame.draw.ellipse(s, (150, 120, 96), (40, 30, 400, 200))
        pygame.draw.ellipse(s, (172, 140, 110), (56, 42, 368, 176))
        lion = pygame.transform.scale(draw_lion(1), (170, 100))
        red = lion.copy()
        red.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        red.fill((150, 40, 30, 0), special_flags=pygame.BLEND_RGBA_ADD)
        s.blit(red, (150, 80))
        _fire(s, 330, 120, t * 0.3, 0.8)
        for i in range(5):
            kid = pygame.transform.scale(draw_kid((0, 0, 0), (0, 0, 0), i % 2, 0), (20, 28))
            kid.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
            kid.fill((60, 30, 26, 0), special_flags=pygame.BLEND_RGBA_ADD)
            s.blit(kid, (100 + i * 18, 170))
        return s
    pygame.draw.rect(s, (40, 50, 60) if night else (88, 160, 70), (0, 210, W, 60))
    if name in ('tracks',):
        pygame.draw.rect(s, (200, 210, 230), (0, 210, W, 60))
        for i in range(9):
            x = 40 + i * 50
            y = 232 + (i % 2) * 14
            pygame.draw.ellipse(s, (120, 130, 160), (x, y, 14, 10))
            for j in range(4):
                pygame.draw.circle(s, (120, 130, 160), (x + 2 + j * 4, y - 3), 2)
    if name in ('camp', 'dark', 'promise', 'end'):
        _hut(s, 90, 168)
        _hut(s, 390, 172, 0.9)
        if name in ('camp', 'end', 'promise'):
            fx = 240
            glow = make_glow(90, (255, 160, 60))
            s.blit(glow, (fx - 90, 200 - 90), special_flags=pygame.BLEND_RGB_ADD)
            _fire(s, fx, 214, t, 1.6 if name != 'promise' else 0.6)
        else:
            pygame.draw.line(s, (60, 40, 30), (230, 216), (250, 212), 3)
            pygame.draw.line(s, (60, 40, 30), (230, 212), (250, 216), 3)
            if int(t * 1.5) % 3 != 2:
                for ex in (300, 312):
                    pygame.draw.rect(s, (255, 220, 60), (ex, 160, 4, 2))
    dam = pygame.transform.scale(sprites['damian_idle'], (48, 64))
    kids = sprites['kids']
    if name in ('camp', 'end'):
        s.blit(dam, (170, 150))
        for i, k in enumerate(kids[:6 if name == 'end' else 4]):
            kk = pygame.transform.scale(k, (28, 38))
            s.blit(kk, (262 + (i % 3) * 30, 175 + (i // 3) * 8))
    elif name == 'promise':
        s.blit(dam, (216, 150))
    elif name == 'tracks':
        s.blit(pygame.transform.flip(dam, True, False), (40, 150))
    if night and name != 'end':
        dark = pygame.Surface((W, H), pygame.SRCALPHA)
        dark.fill((0, 0, 30, 70))
        s.blit(dark, (0, 0))
    return s


def make_icon():
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.circle(s, (240, 150, 60), (32, 32), 31)
    pygame.draw.circle(s, (70, 40, 30), (32, 32), 31, 3)
    d = pygame.transform.scale(draw_damian('idle', 0), (40, 52))
    s.blit(d, (12, 6))
    return s
