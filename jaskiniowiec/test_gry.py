"""Szybki test dymny: python test_gry.py (działa bez okna i dźwięku)."""
import os
import sys

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pygame  # noqa: E402

pygame.init()
import gra  # noqa: E402
import poziomy as P  # noqa: E402

T = gra.T


class FakeInput:
    def __init__(self):
        self.h, self.p = set(), set()

    def held(self, n):
        return n in self.h

    def hit(self, n):
        return n in self.p


g = gra.Game(pygame.display.set_mode((gra.SW, gra.SH)))
inp = FakeInput()


def step(L, held=(), press=(), n=1):
    for _ in range(n):
        inp.h, inp.p = set(held), set(press)
        press = ()
        L.update(inp, gra.DT)
    return g.state


for i, lv in enumerate(P.LEVELS):
    rows = lv['map']
    assert all(len(r) == len(rows[0]) for r in rows), lv['name']
    assert sum(r.count('K') for r in rows) == len(lv['kids']), lv['name']
    assert sum(r.count('?') for r in rows) == len(lv['hints']), lv['name']
    g.start_level(i)
    step(g.level, n=120)
    g.render()

# głaz -> płyta -> wrota (poziom 1)
g.start_level(0)
L = g.level
L.enemies = []
b = L.boulders[0]
L.player.x, L.player.y = b.x - 14, b.y + 16 - 26
for _ in range(2000):
    step(L, held={'right'})
    if L.door_open:
        break
assert L.door_open, "wrota się nie otworzyły"

# runy (poziom 3)
g.start_level(2)
L = g.level
L.enemies = []
runes = {r.num: r for r in L.runes}
for n in L.data['rune_order']:
    r = runes[n]
    L.player.x, L.player.y = r.x - 14, r.y + 20 - 26
    step(L, n=10)
    L.player.facing = 1
    step(L, press={'attack'})
    step(L, n=30)
assert L.gate_open, "brama run zamknięta"

# lew (poziom 4)
g.start_level(3)
L = g.level
lion = L.lion
L.enemies = [lion]
p = L.player
p.x, p.y = 62 * T, 13 * T - 10
step(L, n=40)
for _ in range(60 * 90):
    p.inv = 5
    g.lives = 9
    if lion.state == 'stun' and lion.timer < 2.0:
        p.x = lion.x + lion.w + 2 if lion.facing > 0 else lion.x - p.w - 2
        p.y = lion.y + lion.h - p.h
        p.facing = 1 if lion.cx > p.cx else -1
        step(L, press={'attack'})
        step(L, n=20)
    else:
        p.x, p.y, p.vy = 66 * T, 11 * T - 26, 0
        step(L)
    if lion.state == 'flee':
        break
assert lion.state == 'flee', "lew nie został przegoniony"
print("OK – wszystkie testy przeszły")
pygame.quit()
