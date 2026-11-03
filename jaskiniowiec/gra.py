"""DAMIAN JASKINIOWIEC: OGIEŃ PIERWSZY
Platformówka edukacyjna o paleolicie. Uruchom: python gra.py
"""
import json
import math
import os
import random
import sys

os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
import pygame  # noqa: E402

import grafika as G  # noqa: E402
import poziomy as P  # noqa: E402
from dzwiek import Audio  # noqa: E402

W, H = G.W, G.H
SW, SH = W * 2, H * 2
T = G.T
FPS = 60
DT = 1 / FPS

GRAV = 1000
JUMP_V = 352
MAXFALL = 430
RUN = 118
TITLE = "Damian Jaskiniowiec: Ogień Pierwszy"


_FONTS = {}


def font(size):
    if size not in _FONTS:
        _FONTS[size] = pygame.font.Font(None, size)
    return _FONTS[size]


def approach(v, target, d):
    if v < target:
        return min(v + d, target)
    return max(v - d, target)


def overlap(a, b):
    return a.x < b.x + b.w and a.x + a.w > b.x and a.y < b.y + b.h and a.y + a.h > b.y


class Box:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2


class Body(Box):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False


# ======================================================================= wejście
class Input:
    KEYS = {
        'left': (pygame.K_LEFT, pygame.K_a),
        'right': (pygame.K_RIGHT, pygame.K_d),
        'up': (pygame.K_UP, pygame.K_w),
        'down': (pygame.K_DOWN, pygame.K_s),
        'jump': (pygame.K_SPACE, pygame.K_UP, pygame.K_w),
        'attack': (pygame.K_x, pygame.K_j, pygame.K_LCTRL),
        'throw': (pygame.K_c, pygame.K_k),
        'interact': (pygame.K_e, pygame.K_RETURN, pygame.K_KP_ENTER),
        'confirm': (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_e),
        'pause': (pygame.K_ESCAPE, pygame.K_p),
        'reset': (pygame.K_r,),
        'mute': (pygame.K_m,),
        'menu_up': (pygame.K_UP, pygame.K_w),
        'menu_down': (pygame.K_DOWN, pygame.K_s),
        'n1': (pygame.K_1, pygame.K_KP1),
        'n2': (pygame.K_2, pygame.K_KP2),
        'n3': (pygame.K_3, pygame.K_KP3),
        'full': (pygame.K_F11,),
    }
    PAD = {0: ('jump', 'confirm'), 1: ('throw', 'pause_b'), 2: ('attack',), 3: ('interact',),
           7: ('pause',), 6: ('pause',)}

    def __init__(self):
        self.pressed = set()
        self.keyheld = set()
        self.padheld = set()
        self.joys = []
        self.typed = []

    def scan_joys(self):
        try:
            pygame.joystick.init()
            self.joys = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        except Exception:
            self.joys = []

    def begin(self):
        self.pressed = set()

    def event(self, e):
        if e.type == pygame.KEYDOWN:
            for name, keys in self.KEYS.items():
                if e.key in keys:
                    self.pressed.add(name)
        elif e.type == pygame.JOYBUTTONDOWN:
            for n in self.PAD.get(e.button, ()):
                self.pressed.add(n)
            if e.button in (1,):
                self.pressed.add('back')
        elif e.type == pygame.JOYHATMOTION:
            hx, hy = e.value
            if hy == 1:
                self.pressed.add('menu_up')
            if hy == -1:
                self.pressed.add('menu_down')
        elif e.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
            self.scan_joys()

    def held(self, name):
        k = pygame.key.get_pressed()
        for key in self.KEYS.get(name, ()):
            if k[key]:
                return True
        for j in self.joys:
            try:
                ax = j.get_axis(0) if j.get_numaxes() > 0 else 0
                ay = j.get_axis(1) if j.get_numaxes() > 1 else 0
                hx, hy = j.get_hat(0) if j.get_numhats() > 0 else (0, 0)
                if name == 'left' and (ax < -0.4 or hx < 0):
                    return True
                if name == 'right' and (ax > 0.4 or hx > 0):
                    return True
                if name == 'down' and (ay > 0.5 or hy < 0):
                    return True
                if name == 'jump' and j.get_numbuttons() > 0 and j.get_button(0):
                    return True
            except Exception:
                pass
        return False

    def hit(self, name):
        return name in self.pressed


# ======================================================================= grafika (cache)
class Art:
    def __init__(self):
        d = {}
        for pose, n in (('idle', 4), ('walk', 4), ('jump', 1), ('fall', 1), ('hurt', 1)):
            for f in range(n):
                d[(pose, f)] = G.draw_damian(pose, f)
        self.damian = d
        self.club = G.make_club()
        self.boar = [G.draw_boar(f) for f in range(4)]
        self.boar_hurt = G.draw_boar(0, True)
        self.wolf = [G.draw_wolf(f) for f in range(4)]
        self.wolf_hurt = G.draw_wolf(0, True)
        self.bat = [G.draw_bat(f) for f in range(4)]
        self.bat_hang = G.draw_bat_hang()
        self.lion = {'run': [G.draw_lion(f, 'run') for f in range(4)],
                     'roar': G.draw_lion(0, 'roar'), 'stun': G.draw_lion(0, 'stun'),
                     'idle': G.draw_lion(0, 'idle')}
        self.mammoth = [G.draw_mammoth(f) for f in range(8)]
        self.items = {k: G.draw_item(k) for k in 'bmfh'}
        self.stone = G.draw_item('stone')
        self.heart = G.draw_heart_icon(True)
        self.heart_empty = G.draw_heart_icon(False)
        self.boulder = G.with_outline(G.draw_boulder())
        self.torch = [G.draw_torch(True, f) for f in range(4)]
        self.torch_off = G.draw_torch(False, 0)
        self.runes = {(s, l): G.draw_rune(s, l) for s in range(4) for l in (False, True)}
        self.hint = G.draw_hint_stone()
        self.stal = {False: G.draw_stalactite(False), True: G.draw_stalactite(True)}
        self.lights = {r: G.make_light(r, (6, 4, 14), 255) for r in (26, 40, 64, 70, 76, 88, 96)}
        self.glow = G.make_glow(60, (255, 150, 60))
        self.glow_small = G.make_glow(24, (255, 200, 120))
        self.kid_cache = {}

    def kid(self, k, frame, happy):
        key = (k['name'], frame % 4 if happy else 0, happy)
        if key not in self.kid_cache:
            self.kid_cache[key] = G.draw_kid(k['hair'], k['tunic'], k['girl'], frame, happy)
        return self.kid_cache[key]


def compose_damian(art, pose, f, attack_k=None, walk_t=0.0):
    """Skleja Damiana z maczugą. Zwraca (powierzchnia patrząca w prawo, punkt stóp)."""
    body = art.damian[(pose, f)]
    canvas = pygame.Surface((60, 50), pygame.SRCALPHA)
    bx, by = 18, 15
    hand = (bx + 17, by + 19)
    if attack_k is not None:
        ang = 100 - 230 * min(1, attack_k * 1.6)
    else:
        ang = -18 + (math.sin(walk_t * 1.5) * 5 if pose == 'walk' else 0)
    rimg, piv = G.rot_pivot(art.club, (5, 19), ang)
    canvas.blit(body, (bx, by))
    canvas.blit(rimg, (hand[0] - piv.x, hand[1] - piv.y))
    if attack_k is not None and 0.15 < attack_k < 0.75:
        pygame.draw.arc(canvas, (255, 255, 255), (hand[0] - 20, hand[1] - 22, 40, 40), -1.2, 1.3, 2)
    return canvas, (bx + 12, by + 31)


# ======================================================================= byty
class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max', 'col', 'size', 'grav')

    def __init__(self, x, y, vx, vy, life, col, size=2, grav=300):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life = self.max = life
        self.col, self.size, self.grav = col, size, grav


class Item(Box):
    def __init__(self, x, y, kind):
        super().__init__(x + 2, y + 2, 12, 12)
        self.kind = kind
        self.t = random.random() * 6
        self.taken = False


class Enemy(Body):
    score = 100
    max_hp = 1

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.hp = self.max_hp
        self.alive = True
        self.dying = False
        self.flash = 0
        self.facing = -1
        self.t = random.random()
        self.stunnable = False

    def hit(self, lvl, dmg, from_x):
        if not self.alive or self.dying:
            return False
        self.hp -= dmg
        self.flash = 0.25
        lvl.game.audio.play('hit')
        lvl.burst(self.cx, self.cy, (255, 240, 200), 6)
        if self.hp <= 0:
            self.dying = True
            self.vy = -230
            self.vx = 60 if self.cx > from_x else -60
            lvl.add_score(self.score, self.cx, self.y)
        else:
            self.vx = 140 if self.cx > from_x else -140
            self.knock = 0.2
        return True

    def update_dying(self, lvl, dt):
        self.vy += GRAV * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.y > lvl.h * T + 60:
            self.alive = False

    def hurts(self):
        return not self.dying

    def edge_ahead(self, lvl):
        tx = int((self.x + self.w + 1) // T) if self.vx > 0 else int((self.x - 1) // T)
        ty = int((self.y + self.h + 2) // T)
        return not (lvl.solid(tx, ty) or lvl.char(tx, ty) == '=')


class Walker(Enemy):
    speed = 45
    max_hp = 2

    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.vx = -self.speed
        self.knock = 0
        self.mode_t = 0

    def update(self, lvl, dt):
        if self.dying:
            return self.update_dying(lvl, dt)
        self.t += dt
        self.flash = max(0, self.flash - dt)
        if self.knock > 0:
            self.knock -= dt
            self.vx *= 0.9
        else:
            self.think(lvl, dt)
        self.vy = min(self.vy + GRAV * dt, MAXFALL)
        if lvl.move_x(self, self.vx * dt):
            self.vx = -self.vx
        res = lvl.move_y(self, self.vy * dt)
        self.on_ground = res == 'down'
        if res:
            self.vy = 0
        if self.on_ground and self.knock <= 0 and self.edge_ahead(lvl):
            self.vx = -self.vx
        if self.vx:
            self.facing = 1 if self.vx > 0 else -1
        if self.y > lvl.h * T + 40:
            self.alive = False

    def think(self, lvl, dt):
        sp = self.speed
        self.vx = sp if self.vx >= 0 else -sp


class Boar(Walker):
    speed = 42
    max_hp = 2
    score = 150

    def __init__(self, x, y):
        super().__init__(x, y + T - 15, 24, 15)
        self.charge = 0

    def think(self, lvl, dt):
        p = lvl.player
        d = 1 if self.vx >= 0 else -1
        if self.charge > 0:
            self.charge -= dt
            self.vx = d * 115
            return
        if abs(p.cy - self.cy) < 24 and 0 < (p.cx - self.cx) * d < 110 and random.random() < 0.03:
            self.charge = 0.9
            lvl.burst(self.cx - d * 10, self.y + self.h, (200, 180, 150), 4)
        self.vx = d * self.speed

    def draw(self, s, cam, art):
        img = art.boar_hurt if self.flash > 0 else art.boar[int(self.t * (14 if self.charge > 0 else 8)) % 4]
        if self.facing < 0:
            img = pygame.transform.flip(img, True, False)
        if self.dying:
            img = pygame.transform.flip(img, False, True)
        s.blit(img, (self.cx - img.get_width() / 2 - cam[0], self.y + self.h - img.get_height() + 1 - cam[1]))


class Wolf(Walker):
    speed = 58
    max_hp = 2
    score = 200

    def __init__(self, x, y):
        super().__init__(x, y + T - 15, 24, 15)

    def think(self, lvl, dt):
        p = lvl.player
        dx = p.cx - self.cx
        if abs(dx) < 140 and abs(p.cy - self.cy) < 40:
            want = 1 if dx > 0 else -1
            self.vx = approach(self.vx, want * 125, 400 * dt)
            if self.on_ground and random.random() < 0.01 and abs(dx) < 70:
                self.vy = -260
        else:
            d = 1 if self.vx >= 0 else -1
            self.vx = d * self.speed
        if self.on_ground and self.edge_ahead(lvl) and abs(self.vx) > 0:
            self.vx = -self.vx * 0.5

    def draw(self, s, cam, art):
        img = art.wolf_hurt if self.flash > 0 else art.wolf[int(self.t * 12) % 4]
        if self.facing < 0:
            img = pygame.transform.flip(img, True, False)
        if self.dying:
            img = pygame.transform.flip(img, False, True)
        s.blit(img, (self.cx - img.get_width() / 2 - cam[0], self.y + self.h - img.get_height() + 1 - cam[1]))


class Bat(Enemy):
    max_hp = 1
    score = 120

    def __init__(self, x, y):
        super().__init__(x + 4, y, 12, 8)
        self.home = (x + 4, y)
        self.awake = False
        self.base_y = y

    def update(self, lvl, dt):
        if self.dying:
            return self.update_dying(lvl, dt)
        self.t += dt
        p = lvl.player
        if not self.awake:
            if abs(p.cx - self.cx) < 100 and p.y > self.y:
                self.awake = True
                lvl.game.audio.play('talk')
            return
        tx = p.cx + math.sin(self.t * 1.3) * 40
        ty = p.cy - 24 + math.sin(self.t * 3) * 22
        self.vx = approach(self.vx, max(-90, min(90, (tx - self.cx) * 1.5)), 220 * dt)
        self.vy = approach(self.vy, max(-80, min(80, (ty - self.cy) * 1.5)), 220 * dt)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.facing = 1 if self.vx > 0 else -1

    def draw(self, s, cam, art):
        if self.awake or self.dying:
            img = art.bat[int(self.t * 14) % 4]
            if self.dying:
                img = pygame.transform.flip(img, False, True)
        else:
            img = art.bat_hang
        s.blit(img, (self.cx - img.get_width() / 2 - cam[0], self.cy - img.get_height() / 2 - cam[1]))


class Falling(Enemy):
    """Sopel / stalaktyt: spada, gdy gracz przechodzi pod spodem."""
    max_hp = 99

    def __init__(self, x, y, ice, armed=True):
        super().__init__(x + 3, y, 10, 15)
        self.ice = ice
        self.state = 'hang' if armed else 'fall'
        self.timer = 0
        self.home = (self.x, self.y)
        self.respawn = armed

    def hit(self, lvl, dmg, from_x):
        return False

    def hurts(self):
        return self.state == 'fall'

    def update(self, lvl, dt):
        p = lvl.player
        if self.state == 'hang':
            if abs(p.cx - self.cx) < 18 and p.y > self.y:
                self.state = 'shake'
                self.timer = 0.45
                lvl.game.audio.play('crack')
        elif self.state == 'shake':
            self.timer -= dt
            if self.timer <= 0:
                self.state = 'fall'
        elif self.state == 'fall':
            self.vy = min(self.vy + GRAV * dt, 520)
            if lvl.move_y(self, self.vy * dt):
                self.state = 'broken'
                self.timer = 3.5
                lvl.burst(self.cx, self.y + self.h, (200, 230, 250) if self.ice else (150, 130, 110), 10)
                lvl.game.audio.play('crack')
            if self.y > lvl.h * T:
                self.state = 'broken'
                self.timer = 3.5
        elif self.state == 'broken':
            self.timer -= dt
            if self.timer <= 0:
                if self.respawn:
                    self.x, self.y = self.home
                    self.vy = 0
                    self.state = 'hang'
                else:
                    self.alive = False

    def draw(self, s, cam, art):
        if self.state == 'broken':
            return
        ox = math.sin(pygame.time.get_ticks() * 0.08) * 1.2 if self.state == 'shake' else 0
        s.blit(art.stal[self.ice], (self.x - 1 + ox - cam[0], self.y - 1 - cam[1]))


class Lion(Enemy):
    max_hp = 5
    score = 2000

    def __init__(self, x, y):
        super().__init__(x - 16, y + T - 28, 46, 28)
        self.state = 'sleep'
        self.timer = 0
        self.facing = -1
        self.arena_x = x - 25 * T
        self.flee = False
        self.hits_taken = 0

    def hurts(self):
        return self.state not in ('stun', 'sleep', 'flee') and not self.dying

    def hit(self, lvl, dmg, from_x):
        if self.state != 'stun':
            if self.state != 'sleep':
                lvl.game.audio.play('hit')
            return self.state != 'sleep'
        self.hp -= 1
        self.flash = 0.3
        lvl.game.audio.play('hit')
        lvl.burst(self.cx, self.cy, (255, 220, 160), 12)
        lvl.shake = 0.2
        if self.hp <= 0:
            self.state = 'flee'
            self.timer = 1.4
            lvl.boss_defeated()
        else:
            self.state = 'recover'
            self.timer = 0.6
            self.vx = 160 if self.cx > from_x else -160
            self.vy = -200
        return True

    def update(self, lvl, dt):
        self.t += dt
        self.flash = max(0, self.flash - dt)
        p = lvl.player
        st = self.state
        self.timer -= dt
        if st == 'sleep':
            if p.x > self.arena_x and p.on_ground:
                self.state = 'roar'
                self.timer = 1.4
                lvl.boss_start()
            return
        if st == 'roar':
            self.vx = 0
            self.facing = 1 if p.cx > self.cx else -1
            if self.timer <= 0:
                self.state = 'run'
                self.timer = 6
        elif st == 'run':
            sp = 175 + (self.max_hp - self.hp) * 15
            self.vx = approach(self.vx, self.facing * sp, 500 * dt)
            if self.on_ground and p.y + p.h < self.y and abs(p.cx - self.cx) < 90 and random.random() < 0.02:
                self.vy = -300
        elif st == 'stun':
            self.vx = approach(self.vx, 0, 600 * dt)
            if self.timer <= 0:
                self.state = 'roar'
                self.timer = 1.0
                lvl.roar_rocks(2)
        elif st == 'recover':
            self.vx = approach(self.vx, 0, 300 * dt)
            if self.timer <= 0:
                self.state = 'roar'
                self.timer = 1.2
                lvl.roar_rocks(3 + self.max_hp - self.hp)
        elif st == 'flee':
            if self.timer > 0:
                self.vx = 0
            else:
                self.facing = 1
                self.vx = 220
                self.x += self.vx * dt
                self.y = min(self.y, lvl.h * T)
                if self.x > lvl.w * T + 80:
                    self.alive = False
                return
        self.vy = min(self.vy + GRAV * dt, MAXFALL)
        if lvl.move_x(self, self.vx * dt):
            if st == 'run' and abs(self.vx) < 40:
                self.facing = -self.facing
            elif st == 'run':
                self.state = 'stun'
                self.timer = 2.4
                lvl.shake = 0.35
                lvl.game.audio.play('stomp')
                lvl.burst(self.cx + self.facing * 24, self.cy, (200, 180, 150), 14)
                lvl.roar_rocks(1)
                lvl.float_text("Oszołomiony! Uderz!", self.cx, self.y - 10, (255, 230, 120))
            self.vx = 0
        res = lvl.move_y(self, self.vy * dt)
        self.on_ground = res == 'down'
        if res:
            self.vy = 0
        if self.x < self.arena_x - T:
            self.x = self.arena_x - T
            if self.state == 'run':
                self.facing = 1
        if self.y > lvl.h * T:
            self.x, self.y, self.vy = self.arena_x + 20 * T, 8 * T, 0

    def draw(self, s, cam, art):
        st = self.state
        if st == 'run' or (st == 'flee' and self.timer <= 0):
            img = art.lion['run'][int(self.t * 12) % 4]
        elif st in ('roar',):
            img = art.lion['roar']
        elif st in ('stun', 'recover'):
            img = art.lion['stun']
        else:
            img = art.lion['idle']
        if self.facing < 0:
            img = pygame.transform.flip(img, True, False)
        if self.flash > 0 and int(self.flash * 20) % 2:
            img = img.copy()
            img.fill((120, 60, 60, 0), special_flags=pygame.BLEND_RGBA_ADD)
        x = self.cx - img.get_width() / 2 - cam[0]
        y = self.y + self.h - img.get_height() + 1 - cam[1]
        if st == 'roar':
            x += random.uniform(-1, 1)
        s.blit(img, (x, y))
        if st == 'stun':
            for i in range(3):
                a = self.t * 5 + i * 2.1
                sx = self.cx + self.facing * 14 + math.cos(a) * 12 - cam[0]
                sy = self.y - 4 + math.sin(a) * 4 - cam[1]
                pygame.draw.circle(s, (255, 240, 100), (int(sx), int(sy)), 2)
        if st == 'sleep':
            z = int(self.t * 2) % 3
            f = font(14)
            s.blit(f.render("z" * (z + 1), True, (255, 255, 255)), (self.cx + 10 - cam[0], self.y - 12 - cam[1]))


class Mammoth(Body):
    def __init__(self, x, y):
        super().__init__(x, y + T - 38, 46, 38)
        self.vx = 32
        self.t = 0
        self.last_dx = 0

    def update(self, lvl, dt):
        self.t += dt
        self.vy = min(self.vy + GRAV * dt, MAXFALL)
        x0 = self.x
        if lvl.move_x(self, self.vx * dt):
            self.vx = -self.vx
        self.last_dx = self.x - x0
        if lvl.move_y(self, self.vy * dt):
            self.vy = 0

    def draw(self, s, cam, art):
        img = art.mammoth[int(self.t * 6) % 8]
        if self.vx < 0:
            img = pygame.transform.flip(img, True, False)
        s.blit(img, (self.cx - img.get_width() / 2 - cam[0], self.y + self.h - img.get_height() + 2 - cam[1]))


class Kid(Box):
    def __init__(self, x, y, info):
        super().__init__(x + 2, y + T - 18, 12, 18)
        self.info = info
        self.state = 'wait'
        self.t = random.random() * 3
        self.alpha = 255
        self.facing = -1

    def update(self, lvl, dt):
        self.t += dt
        p = lvl.player
        if self.state == 'wait':
            self.facing = 1 if p.cx > self.cx else -1
        elif self.state == 'happy':
            self.timer -= dt
            if self.timer <= 0:
                self.state = 'home'
                self.timer = 1.6
        elif self.state == 'home':
            self.timer -= dt
            self.facing = -1
            self.x -= 70 * dt
            self.alpha = max(0, int(255 * self.timer / 1.6))
            if random.random() < 0.4:
                lvl.particles.append(Particle(self.cx, self.cy, random.uniform(-20, 20), random.uniform(-40, -10),
                                              0.7, (255, 240, 140), 2, 0))
            if self.timer <= 0:
                self.state = 'gone'

    def draw(self, s, cam, art):
        if self.state == 'gone':
            return
        happy = self.state != 'wait'
        img = art.kid(self.info, int(self.t * 10), happy)
        if self.facing < 0:
            img = pygame.transform.flip(img, True, False)
        if self.alpha < 255:
            img = img.copy()
            img.set_alpha(self.alpha)
        s.blit(img, (self.cx - img.get_width() / 2 - cam[0], self.y + self.h - img.get_height() + 1 - cam[1]))
        if self.state == 'wait':
            by = self.y - 14 + math.sin(self.t * 4) * 2 - cam[1]
            bx = self.cx - cam[0]
            pygame.draw.circle(s, (255, 255, 255), (int(bx), int(by)), 6)
            pygame.draw.circle(s, G.OUT, (int(bx), int(by)), 6, 1)
            pygame.draw.polygon(s, (255, 255, 255), [(bx - 2, by + 4), (bx + 2, by + 4), (bx - 3, by + 9)])
            f = font(15)
            q = f.render("?", True, (200, 60, 40))
            s.blit(q, (bx - q.get_width() / 2, by - q.get_height() / 2 + 1))


class Boulder(Body):
    def __init__(self, x, y):
        super().__init__(x, y, 16, 16)
        self.home = (x, y)
        self.roll = 0
        self.locked = False

    def update(self, lvl, dt):
        self.vy = min(self.vy + GRAV * dt, MAXFALL)
        res = lvl.move_y(self, self.vy * dt)
        self.on_ground = res == 'down'
        if res:
            if self.vy > 200:
                lvl.game.audio.play('stomp')
                lvl.shake = 0.12
            self.vy = 0
        if self.vx:
            old = self.x
            if lvl.move_x(self, self.vx * dt):
                self.vx = 0
            self.roll += (self.x - old) * 7
            if self.on_ground:
                under = lvl.char(int(self.cx // T), int((self.y + self.h + 1) // T))
                self.vx = approach(self.vx, 0, (35 if under == 'i' else 170) * dt)
        if self.y > lvl.h * T + 20:
            self.reset()

    def reset(self):
        self.x, self.y = self.home
        self.vx = self.vy = 0
        self.locked = False

    def draw(self, s, cam, art):
        img = pygame.transform.rotate(art.boulder, -self.roll)
        s.blit(img, (self.cx - img.get_width() / 2 - cam[0], self.cy - img.get_height() / 2 - cam[1]))


class Stone(Body):
    def __init__(self, x, y, d):
        super().__init__(x, y, 6, 6)
        self.vx = 270 * d
        self.vy = -90
        self.alive = True

    def update(self, lvl, dt):
        self.vy += 500 * dt
        if lvl.move_x(self, self.vx * dt) or lvl.move_y(self, self.vy * dt):
            self.alive = False
            lvl.burst(self.cx, self.cy, (170, 170, 180), 4)
        for e in lvl.enemies:
            if e.alive and not e.dying and overlap(self, e) and not isinstance(e, Falling):
                if e.hit(lvl, 1, self.cx - self.vx):
                    self.alive = False
                    return
        for r in lvl.runes:
            if overlap(self, r):
                lvl.hit_rune(r)
                self.alive = False
                return
        if self.y > lvl.h * T:
            self.alive = False


class Player(Body):
    def __init__(self, x, y):
        super().__init__(x + 2, y + T - 26, 12, 26)
        self.facing = 1
        self.hp = 3
        self.max_hp = 3
        self.inv = 0
        self.attack = 0
        self.throw_cd = 0
        self.jbuf = 0
        self.coyote = 0
        self.drop = 0
        self.knock = 0
        self.ride = None
        self.t = 0
        self.walk_t = 0
        self.hit_done = set()
        self.pushing = False


# ======================================================================= poziom
class Level:
    def __init__(self, game, idx):
        self.game = game
        self.idx = idx
        self.data = P.LEVELS[idx]
        self.theme = self.data['theme']
        rows = self.data['map']
        self.h = len(rows)
        self.w = len(rows[0])
        self.grid = [list(r) for r in rows]
        self.items, self.enemies, self.kids, self.boulders = [], [], [], []
        self.torches, self.hints, self.runes, self.plates = [], [], [], []
        self.mammoths, self.stones, self.particles, self.eyes = [], [], [], []
        self.floats = []
        self.painting = None
        self.exit = None
        self.lion = None
        self.door_open = False
        self.door_amt = 0.0
        self.gate_open = False
        self.gate_amt = 0.0
        self.shake = 0
        self.time = 0
        self.rune_pos = 0
        self.boss_active = False
        self.exit_msg_cd = 0
        self.banner = 3.5
        start = (2 * T, 10 * T)
        kid_spots = []
        hint_spots = []
        for ty, row in enumerate(self.grid):
            for tx, c in enumerate(row):
                x, y = tx * T, ty * T
                keep = False
                if c in '#=^~iDG':
                    keep = True
                elif c == 'P':
                    start = (x, y)
                elif c in 'bmfh':
                    self.items.append(Item(x, y, c))
                elif c == 'z':
                    self.enemies.append(Boar(x, y))
                elif c == 'w':
                    self.enemies.append(Wolf(x, y))
                elif c == 'v':
                    self.enemies.append(Bat(x, y))
                elif c == 'k':
                    self.enemies.append(Falling(x, y, self.theme == 'ice'))
                elif c == 'L':
                    self.lion = Lion(x, y)
                    self.enemies.append(self.lion)
                elif c == 'M':
                    self.mammoths.append(Mammoth(x, y))
                elif c == 'B':
                    self.boulders.append(Boulder(x, y))
                elif c == 'p':
                    self.plates.append(Box(x + 1, y + 10, 14, 6))
                elif c == 'T':
                    t = Box(x + 2, y - 8, 12, 24)
                    t.lit = False
                    self.torches.append(t)
                elif c == 'K':
                    kid_spots.append((x, y))
                elif c == '?':
                    hint_spots.append((x, y))
                elif c == 'E':
                    self.exit = Box(x - 2, y + T - 46, 36, 46)
                elif c == 'X':
                    self.painting = Box(x - 14, y, 44, 26)
                elif c in '1234':
                    r = Box(x, y - 4, 16, 20)
                    r.num = int(c)
                    r.lit = False
                    r.cd = 0
                    self.runes.append(r)
                elif c == 'O':
                    e = Box(x, y, 16, 8)
                    e.state = 'wait'
                    e.t = 0
                    self.eyes.append(e)
                if not keep:
                    row[tx] = '.'
        kid_spots.sort()
        for (x, y), info in zip(kid_spots, self.data['kids']):
            self.kids.append(Kid(x, y, info))
        hint_spots.sort()
        for i, (x, y) in enumerate(hint_spots):
            hb = Box(x, y - 2, 16, 18)
            hb.text = self.data['hints'][i] if i < len(self.data['hints']) else ""
            self.hints.append(hb)
        self.start = start
        self.player = Player(*start)
        self.checkpoint = (self.player.x, self.player.y)
        self.cam = [0.0, 0.0]
        self.look = 0
        self.tiles = G.make_tiles(self.theme, seed=idx + 3)
        self.sky, self.layers = G.make_background(self.theme)
        self.dark = G.THEMES[self.theme]['dark']
        self.bake()
        self.weather = []
        rnd = random.Random(idx)
        for _ in range(70 if self.theme == 'ice' else 30):
            self.weather.append([rnd.random() * W, rnd.random() * H, rnd.random()])
        self.snap_camera()

    # ------------------------------------------------------------------ mapa
    def char(self, tx, ty):
        if 0 <= tx < self.w and 0 <= ty < self.h:
            return self.grid[ty][tx]
        return '.'

    def solid(self, tx, ty):
        if tx < 0 or tx >= self.w:
            return True
        if ty < 0 or ty >= self.h:
            return False
        c = self.grid[ty][tx]
        if c in '#i':
            return True
        if c == 'D':
            return self.door_amt < 0.8
        if c == 'G':
            return self.gate_amt < 0.8
        return False

    def move_x(self, b, dx):
        if dx == 0:
            return False
        b.x += dx
        y0 = int(b.y // T)
        y1 = int((b.y + b.h - 0.01) // T)
        if dx > 0:
            tx = int((b.x + b.w - 0.01) // T)
            for ty in range(y0, y1 + 1):
                if self.solid(tx, ty):
                    b.x = tx * T - b.w
                    return True
        else:
            tx = int(b.x // T)
            for ty in range(y0, y1 + 1):
                if self.solid(tx, ty):
                    b.x = (tx + 1) * T
                    return True
        return False

    def move_y(self, b, dy, drop=False):
        if dy == 0:
            return None
        old_bottom = b.y + b.h
        b.y += dy
        x0 = int(b.x // T)
        x1 = int((b.x + b.w - 0.01) // T)
        if dy > 0:
            ty = int((b.y + b.h - 0.01) // T)
            for tx in range(x0, x1 + 1):
                if self.solid(tx, ty) or (not drop and self.char(tx, ty) == '=' and old_bottom <= ty * T + 0.5):
                    b.y = ty * T - b.h
                    return 'down'
        else:
            ty = int(b.y // T)
            for tx in range(x0, x1 + 1):
                if self.solid(tx, ty):
                    b.y = (ty + 1) * T
                    return 'up'
        return None

    def bake(self):
        th = self.tiles
        s = pygame.Surface((self.w * T, self.h * T), pygame.SRCALPHA)
        rnd = random.Random(self.idx * 17 + 1)

        def ground(c):
            return c in '#'

        for ty in range(self.h):
            for tx in range(self.w):
                c = self.grid[ty][tx]
                x, y = tx * T, ty * T
                if c == '#':
                    above = self.char(tx, ty - 1) if ty > 0 else '#'
                    if not ground(above) and above not in 'i':
                        s.blit(rnd.choice(th['top']), (x, y))
                        if above == '.' and ty > 0:
                            d = G.decor_for(self.theme, rnd)
                            if d:
                                s.blit(d, (x, y - 10))
                    else:
                        s.blit(th['fill'][(tx * 7 + ty * 3) % 4], (x, y))
                    if tx > 0 and not ground(self.char(tx - 1, ty)) and self.char(tx - 1, ty) != 'i':
                        pygame.draw.line(s, G.mix(G.THEMES[self.theme]['dirt2'], (0, 0, 0), 0.4), (x, y), (x, y + T - 1))
                    if tx < self.w - 1 and not ground(self.char(tx + 1, ty)) and self.char(tx + 1, ty) != 'i':
                        pygame.draw.line(s, G.mix(G.THEMES[self.theme]['dirt2'], (0, 0, 0), 0.4), (x + T - 1, y), (x + T - 1, y + T - 1))
                    if ty < self.h - 1 and self.char(tx, ty + 1) == '.':
                        pygame.draw.line(s, G.OUT, (x, y + T - 1), (x + T - 1, y + T - 1))
                elif c == 'i':
                    s.blit(th['ice'], (x, y))
                elif c == '=':
                    s.blit(th['plat'], (x, y))
                elif c == '^':
                    s.blit(th['spike'], (x, y))
        self.surf = s

    # ------------------------------------------------------------------ pomocnicze
    def burst(self, x, y, col, n, speed=90):
        for _ in range(n):
            a = random.random() * math.tau
            v = random.uniform(0.3, 1) * speed
            self.particles.append(Particle(x, y, math.cos(a) * v, math.sin(a) * v - 40,
                                           random.uniform(0.3, 0.7), col, random.choice((1, 2, 2))))

    def float_text(self, text, x, y, col=(255, 255, 255), life=1.6):
        self.floats.append([text, x, y, life, life, col])

    def add_score(self, n, x, y):
        self.game.score += n
        self.float_text("+%d" % n, x, y, (255, 240, 120), 1.0)

    def snap_camera(self):
        p = self.player
        self.cam[0] = max(0, min(self.w * T - W, p.cx - W / 2))
        self.cam[1] = max(0, min(self.h * T - H, p.cy - H / 2 - 10))

    def boss_start(self):
        self.boss_active = True
        self.game.audio.play('roar')
        self.game.audio.play_music('boss')
        self.shake = 0.8
        self.float_text("LEW JASKINIOWY!", self.lion.cx, self.lion.y - 20, (255, 120, 80), 2.5)
        self.roar_rocks(3)

    def boss_defeated(self):
        self.game.audio.play('roar')
        self.shake = 0.6
        self.gate_open = True
        self.game.audio.play('door')
        self.float_text("Lew ucieka w góry!", self.lion.cx, self.lion.y - 20, (255, 230, 120), 2.5)
        self.game.audio.play_music(self.data['music'])

    def roar_rocks(self, n):
        if not self.lion:
            return
        ax = self.lion.arena_x + 4 * T
        for _ in range(n):
            x = random.uniform(ax, ax + 26 * T)
            f = Falling(x, self.cam[1] - 20, False, armed=False)
            f.vy = random.uniform(0, 80)
            self.enemies.append(f)

    def hit_rune(self, r):
        order = self.data.get('rune_order')
        if not order or self.gate_open or r.cd > 0 or r.lit:
            return
        r.cd = 0.4
        if order[self.rune_pos] == r.num:
            r.lit = True
            self.rune_pos += 1
            self.game.audio.play('rune')
            self.burst(r.cx, r.y, (255, 190, 80), 10)
            if self.rune_pos >= len(order):
                self.gate_open = True
                self.game.audio.play('door')
                self.shake = 0.5
                self.float_text("Brama się otwiera!", r.cx, r.y - 20, (255, 230, 120), 2.2)
        else:
            self.game.audio.play('wrong')
            self.game.audio.play('growl')
            self.shake = 0.3
            for q in self.runes:
                q.lit = False
            self.rune_pos = 0
            self.float_text("Zła kolejność... coś się zbudziło!", r.cx, r.y - 20, (255, 140, 120), 2.2)
            b = Bat(r.x, r.y - 70)
            b.awake = True
            self.enemies.append(b)

    def kids_taught(self):
        return sum(1 for k in self.kids if k.state != 'wait')

    # ------------------------------------------------------------------ gracz
    def hurt_player(self, from_x, dmg=1):
        p = self.player
        if p.inv > 0:
            return
        p.hp -= dmg
        p.inv = 1.4
        p.knock = 0.28
        p.vx = -150 if from_x > p.cx else 150
        p.vy = -230
        self.shake = 0.25
        self.game.audio.play('hurt')
        self.burst(p.cx, p.cy, (255, 120, 120), 8)
        if p.hp <= 0:
            self.lose_life()

    def lose_life(self, reason=None):
        g = self.game
        g.lives -= 1
        if g.lives < 0:
            g.game_over()
            return
        p = self.player
        p.hp = p.max_hp
        p.x, p.y = self.checkpoint
        p.vx = p.vy = 0
        p.inv = 2.0
        p.knock = 0
        p.ride = None
        for b in self.boulders:
            b.reset()
        self.snap_camera()
        self.float_text(reason or "Ała! Jeszcze raz...", p.cx, p.y - 10, (255, 200, 200))

    def fall_hazard(self, reason, splash=False):
        """Wpadnięcie do wody/przepaści – zabiera serce i wraca do punktu kontrolnego."""
        p = self.player
        if splash:
            self.game.audio.play('splash')
            self.burst(p.cx, p.y + p.h, G.THEMES[self.theme]['water'], 16, 140)
        else:
            self.game.audio.play('hurt')
        p.hp -= 1
        if p.hp <= 0:
            self.lose_life(reason)
            return
        p.x, p.y = self.checkpoint
        p.vx = p.vy = 0
        p.inv = 1.5
        p.ride = None
        self.snap_camera()
        self.float_text(reason, p.cx, p.y - 10, (200, 230, 255))

    def update_player(self, inp, dt):
        p = self.player
        p.t += dt
        p.inv = max(0, p.inv - dt)
        p.throw_cd = max(0, p.throw_cd - dt)
        p.drop = max(0, p.drop - dt)
        dirx = (1 if inp.held('right') else 0) - (1 if inp.held('left') else 0)
        under = self.char(int(p.cx // T), int((p.y + p.h + 1) // T))
        on_ice = p.on_ground and under == 'i'
        if p.knock > 0:
            p.knock -= dt
            dirx = 0
            acc = 200
        elif dirx:
            acc = (300 if on_ice else 1300) if p.on_ground else 800
        else:
            acc = (110 if on_ice else 1500) if p.on_ground else 350
        target = dirx * RUN
        if p.pushing:
            target = dirx * 46
        p.vx = approach(p.vx, target, acc * dt)
        if dirx and p.attack <= 0:
            p.facing = dirx
        # skok
        if inp.hit('jump'):
            p.jbuf = 0.13
        p.jbuf -= dt
        p.coyote -= dt
        if p.on_ground:
            p.coyote = 0.1
        if p.jbuf > 0 and p.coyote > 0:
            if inp.held('down') and under == '=':
                p.drop = 0.25
            else:
                p.vy = -JUMP_V
                self.game.audio.play('jump')
                self.burst(p.cx, p.y + p.h, (220, 210, 190), 4, 40)
            p.jbuf = 0
            p.coyote = 0
            p.ride = None
        g = GRAV if (inp.held('jump') and p.vy < 0) else GRAV * 1.85
        p.vy = min(p.vy + g * dt, MAXFALL)
        # atak
        if inp.hit('attack') and p.attack <= 0:
            p.attack = 0.3
            p.hit_done = set()
            self.game.audio.play('swing')
        if p.attack > 0:
            p.attack -= dt
            if 0.06 < (0.3 - p.attack) < 0.22:
                hb = Box(p.x + p.w if p.facing > 0 else p.x - 22, p.y - 4, 22, 28)
                for e in self.enemies:
                    if e.alive and id(e) not in p.hit_done and overlap(hb, e) and not isinstance(e, Falling):
                        if e.hit(self, 1, p.cx):
                            p.hit_done.add(id(e))
                for r in self.runes:
                    if id(r) not in p.hit_done and overlap(hb, r):
                        p.hit_done.add(id(r))
                        self.hit_rune(r)
        if inp.hit('throw') and p.throw_cd <= 0:
            if self.game.flint > 0:
                self.game.flint -= 1
                p.throw_cd = 0.35
                self.stones.append(Stone(p.cx + p.facing * 6, p.y + 8, p.facing))
                self.game.audio.play('throw')
            else:
                self.float_text("Brak krzemieni!", p.cx, p.y - 8, (220, 220, 220), 0.9)
                p.throw_cd = 0.5
        # jazda na mamucie
        if p.ride:
            self.move_x(p, p.ride.last_dx)
            p.y = p.ride.y - p.h
        # ruch poziomy
        dx = p.vx * dt
        if self.move_x(p, dx):
            p.vx = 0
        p.pushing = False
        for b in self.boulders:
            if not overlap(p, b):
                continue
            same = abs((p.y + p.h) - (b.y + b.h)) < 14
            if p.cx < b.cx:
                p.x = b.x - p.w
                if same and dx > 0 and not b.locked:
                    b.vx = max(b.vx, 48)
                    p.pushing = True
            else:
                p.x = b.x + b.w
                if same and dx < 0 and not b.locked:
                    b.vx = min(b.vx, -48)
                    p.pushing = True
        # ruch pionowy
        was_ground = p.on_ground
        old_bottom = p.y + p.h
        vy_before = p.vy
        p.on_ground = False
        res = self.move_y(p, p.vy * dt, p.drop > 0)
        if res == 'down':
            p.on_ground = True
            p.vy = 0
        elif res == 'up':
            p.vy = 0
        if p.vy >= 0:
            for b in self.boulders:
                if overlap(p, b) and old_bottom <= b.y + 3:
                    p.y = b.y - p.h
                    p.vy = 0
                    p.on_ground = True
        p.ride = None
        if vy_before >= 0:
            for m in self.mammoths:
                if p.x + p.w > m.x + 4 and p.x < m.x + m.w - 4 and old_bottom <= m.y + 4 and p.y + p.h >= m.y - 1:
                    p.y = m.y - p.h
                    p.vy = 0
                    p.on_ground = True
                    p.ride = m
        if p.on_ground and not was_ground and vy_before > 300:
            self.burst(p.cx, p.y + p.h, (220, 210, 190), 5, 50)
        if p.on_ground and abs(p.vx) > 10:
            p.walk_t += dt * abs(p.vx) / 12
        # zagrożenia
        cx0 = int(p.x // T)
        cx1 = int((p.x + p.w - 0.01) // T)
        for ty in range(int(p.y // T), int((p.y + p.h - 0.01) // T) + 1):
            for tx in range(cx0, cx1 + 1):
                c = self.char(tx, ty)
                if c == '~' and p.y + p.h > ty * T + 6:
                    self.fall_hazard("Plusk! Woda jest lodowata...", True)
                    return
                if c == '^' and p.y + p.h > ty * T + 8:
                    self.hurt_player(p.cx + p.facing)
                    p.vy = -300
        if p.y > self.h * T + 20:
            self.fall_hazard("Przepaść! Uważaj na krok...")
            return
        # wrogowie
        for e in self.enemies:
            if not e.alive or not e.hurts():
                continue
            hb = Box(e.x + 2, e.y + 2, e.w - 4, e.h - 2)
            if overlap(p, hb):
                stompable = not isinstance(e, (Falling, Lion))
                if stompable and vy_before > 60 and old_bottom <= e.y + 8:
                    e.hit(self, 1, p.cx)
                    p.vy = -280
                    self.game.audio.play('stomp')
                else:
                    self.hurt_player(e.cx)
        if self.lion and self.lion.state == 'stun' and vy_before > 60 and overlap(p, self.lion) \
                and old_bottom <= self.lion.y + 10:
            self.lion.hit(self, 1, p.cx)
            p.vy = -320

    # ------------------------------------------------------------------ aktualizacja
    def update(self, inp, dt):
        self.time += dt
        self.banner = max(0, self.banner - dt)
        self.shake = max(0, self.shake - dt)
        self.exit_msg_cd = max(0, self.exit_msg_cd - dt)
        if inp.hit('reset') and self.boulders:
            for b in self.boulders:
                self.burst(b.cx, b.cy, (200, 200, 200), 8)
                b.reset()
            self.float_text("Głazy wróciły na miejsce", self.player.cx, self.player.y - 10)
        for m in self.mammoths:
            m.update(self, dt)
        for b in self.boulders:
            b.update(self, dt)
        self.update_player(inp, dt)
        if self.game.state != 'play':
            return
        p = self.player
        for e in self.enemies:
            if e.alive and (abs(e.cx - p.cx) < W * 0.9 or isinstance(e, (Lion, Falling))):
                e.update(self, dt)
        self.enemies = [e for e in self.enemies if e.alive]
        for s in self.stones:
            s.update(self, dt)
        self.stones = [s for s in self.stones if s.alive]
        for k in self.kids:
            k.update(self, dt)
        for r in self.runes:
            r.cd = max(0, r.cd - dt)
        # przedmioty
        for it in self.items:
            if not it.taken and overlap(p, it):
                it.taken = True
                g = self.game
                if it.kind == 'b':
                    self.add_score(10, it.cx, it.y)
                elif it.kind == 'm':
                    self.add_score(50, it.cx, it.y)
                elif it.kind == 'f':
                    g.flint += 1
                    self.float_text("+1 krzemień", it.cx, it.y, (220, 220, 240), 1.0)
                elif it.kind == 'h':
                    if p.hp < p.max_hp:
                        p.hp += 1
                        self.float_text("+1 serce", it.cx, it.y, (255, 140, 160), 1.0)
                    else:
                        g.lives += 1
                        self.float_text("+1 życie!", it.cx, it.y, (255, 140, 160), 1.2)
                        g.audio.play('life')
                g.audio.play('collect')
                self.burst(it.cx, it.cy, (255, 250, 200), 6, 60)
        # płyty i wrota
        pressed = False
        for pl in self.plates:
            for b in self.boulders:
                if not b.locked and b.on_ground and abs(b.cx - pl.cx) < 5 and abs(b.y + b.h - pl.y - pl.h) < 3:
                    b.x = pl.cx - b.w / 2
                    b.vx = 0
                    b.locked = True
                    self.burst(b.cx, b.y + b.h, (230, 220, 200), 10)
                    self.float_text("Klik!", b.cx, b.y - 6, (255, 240, 180), 1.0)
            if overlap(pl, p) or any(overlap(pl, b) for b in self.boulders):
                pressed = True
        if pressed and not self.door_open:
            self.door_open = True
            self.game.audio.play('door')
            self.shake = 0.3
        elif not pressed and self.door_open:
            blocked = False
            for ty in range(self.h):
                for tx in range(self.w):
                    if self.grid[ty][tx] == 'D' and overlap(p, Box(tx * T, ty * T, T, T)):
                        blocked = True
            if not blocked:
                self.door_open = False
                self.game.audio.play('door')
        self.door_amt = approach(self.door_amt, 1 if self.door_open else 0, dt * 1.6)
        self.gate_amt = approach(self.gate_amt, 1 if self.gate_open else 0, dt * 1.2)
        # pochodnie
        for t in self.torches:
            if not t.lit and overlap(p, Box(t.x - 4, t.y, t.w + 8, t.h + 8)):
                t.lit = True
                self.checkpoint = (t.x, t.y + t.h - p.h)
                self.game.audio.play('torch')
                self.burst(t.cx, t.y + 4, (255, 180, 60), 14)
                self.float_text("Punkt kontrolny!", t.cx, t.y - 6, (255, 210, 120))
        # oczy w ciemności
        for e in self.eyes:
            e.t += dt
            if e.state == 'wait' and p.cx > e.x - 170:
                e.state = 'show'
                e.t = 0
                self.game.audio.play('growl')
                self.float_text("Coś cię obserwuje...", p.cx, p.y - 14, (255, 220, 120), 2.4)
                self.shake = 0.15
            elif e.state == 'show' and e.t > 2.6:
                e.state = 'gone'
        # interakcje
        near = self.near_interactive()
        if inp.hit('interact') and near:
            kind, obj = near
            if kind == 'kid':
                self.game.open_dialog(obj)
            elif kind == 'hint':
                self.game.open_message(obj.text, title="Wyryte na kamieniu")
            elif kind == 'paint':
                self.game.open_message("Na skale ktoś namalował cztery znaki, jeden po drugim. "
                                       "Może to kolejność, w jakiej trzeba uderzyć runiczne kamienie?",
                                       title="Malowidło naskalne", image=self.painting_img())
        # wyjście
        if self.exit and overlap(p, self.exit):
            need = len(self.kids)
            have = self.kids_taught()
            if have >= need and (not self.lion or not self.lion.alive or self.lion.state == 'flee'):
                self.game.level_clear()
                return
            elif self.exit_msg_cd <= 0:
                self.exit_msg_cd = 2.5
                if have < need:
                    self.float_text("Nie wrócę bez dzieci! (%d/%d)" % (have, need), p.cx, p.y - 12, (255, 220, 160), 2.2)
                else:
                    self.float_text("Najpierw przegoń lwa!", p.cx, p.y - 12, (255, 220, 160), 2.2)
        # cząsteczki
        for pt in self.particles:
            pt.life -= dt
            pt.vy += pt.grav * dt
            pt.x += pt.vx * dt
            pt.y += pt.vy * dt
        self.particles = [pt for pt in self.particles if pt.life > 0]
        for f in self.floats:
            f[3] -= dt
            f[2] -= 18 * dt
        self.floats = [f for f in self.floats if f[3] > 0]
        # pogoda
        for wp in self.weather:
            if self.theme == 'ice':
                wp[1] += (20 + wp[2] * 30) * dt
                wp[0] += math.sin(self.time + wp[2] * 9) * 12 * dt - 10 * dt
            elif self.theme == 'lair':
                wp[1] -= (10 + wp[2] * 20) * dt
                wp[0] += math.sin(self.time * 2 + wp[2] * 9) * 10 * dt
            else:
                wp[1] += (4 + wp[2] * 6) * dt
                wp[0] += math.sin(self.time + wp[2] * 9) * 6 * dt
            wp[0] %= W
            wp[1] %= H
        # kamera
        self.look = approach(self.look, p.facing * 34, 80 * dt)
        tx = p.cx - W / 2 + self.look
        ty = p.cy - H / 2 - 10
        self.cam[0] += (tx - self.cam[0]) * min(1, dt * 6)
        self.cam[1] += (ty - self.cam[1]) * min(1, dt * 5)
        self.cam[0] = max(0, min(self.w * T - W, self.cam[0]))
        self.cam[1] = max(0, min(self.h * T - H, self.cam[1]))

    def painting_img(self):
        order = self.data.get('rune_order') or [1, 2, 3, 4]
        return G.draw_painting([n - 1 for n in order])

    def near_interactive(self):
        p = self.player
        zone = Box(p.x - 10, p.y - 6, p.w + 20, p.h + 12)
        for k in self.kids:
            if k.state == 'wait' and overlap(zone, k):
                return ('kid', k)
        for h in self.hints:
            if overlap(zone, h):
                return ('hint', h)
        if self.painting and abs(self.painting.cx - p.cx) < 30:
            return ('paint', self.painting)
        return None

    # ------------------------------------------------------------------ rysowanie
    def draw(self, s, art):
        sx = random.uniform(-3, 3) * min(1, self.shake * 4) if self.shake > 0 else 0
        sy = random.uniform(-2, 2) * min(1, self.shake * 4) if self.shake > 0 else 0
        cam = (int(self.cam[0] + sx), int(self.cam[1] + sy))
        s.blit(self.sky, (0, 0))
        for layer, f, y in self.layers:
            lw = layer.get_width()
            off = -((cam[0] * f + (self.time * 4 if f < 0.1 else 0)) % lw)
            ly = y - cam[1] * f * 0.5
            s.blit(layer, (off, ly))
            if off + lw < W:
                s.blit(layer, (off + lw, ly))
        s.blit(self.surf, (0, 0), pygame.Rect(cam[0], cam[1], W, H))
        frame = int(self.time * 6)
        tx0 = max(0, cam[0] // T)
        tx1 = min(self.w, (cam[0] + W) // T + 2)
        ty0 = max(0, cam[1] // T)
        ty1 = min(self.h, (cam[1] + H) // T + 2)
        th = self.tiles
        for ty in range(ty0, ty1):
            for tx in range(tx0, tx1):
                c = self.grid[ty][tx]
                x, y = tx * T - cam[0], ty * T - cam[1]
                if c == '~':
                    if self.char(tx, ty - 1) == '~':
                        s.blit(th['water_fill'], (x, y))
                    else:
                        s.blit(th['water'][(frame + tx) % 4], (x, y))
                elif c == 'D':
                    off = int(self.door_amt * T * 3)
                    clip = s.get_clip()
                    s.set_clip(pygame.Rect(x, y, T, T))
                    s.blit(th['door'], (x, y - off))
                    s.set_clip(clip)
                elif c == 'G':
                    off = int(self.gate_amt * T * 3)
                    clip = s.get_clip()
                    s.set_clip(pygame.Rect(x, y, T, T))
                    s.blit(th['gate'], (x, y - off))
                    s.set_clip(clip)
        for pl in self.plates:
            pressed = self.door_open
            s.blit(th['plate_down' if pressed else 'plate'], (pl.x - 1 - cam[0], pl.y - 10 - cam[1]))
        if self.painting:
            img = self.painting_img()
            s.blit(img, (self.painting.x - cam[0], self.painting.y - cam[1]))
        for h in self.hints:
            s.blit(art.hint, (h.x - 1 - cam[0], h.y + 1 - cam[1]))
        if self.exit:
            img = G.draw_exit(self.theme) if not hasattr(self, '_exit_img') else self._exit_img
            self._exit_img = img
            s.blit(img, (self.exit.x - cam[0], self.exit.y - cam[1]))
        for t in self.torches:
            img = art.torch[frame % 4] if t.lit else art.torch_off
            s.blit(img, (t.x - 1 - cam[0], t.y - 1 - cam[1]))
        for r in self.runes:
            s.blit(art.runes[(r.num - 1, r.lit)], (r.x - 1 - cam[0], r.y - 1 - cam[1]))
        for it in self.items:
            if not it.taken:
                bob = math.sin(self.time * 3 + it.t) * 1.5
                s.blit(art.items[it.kind], (it.x - 2 - cam[0], it.y - 2 + bob - cam[1]))
        for b in self.boulders:
            b.draw(s, cam, art)
        for m in self.mammoths:
            m.draw(s, cam, art)
        for k in self.kids:
            k.draw(s, cam, art)
        for e in self.enemies:
            if abs(e.cx - cam[0] - W / 2) < W:
                e.draw(s, cam, art)
        self.draw_player(s, cam, art)
        for st in self.stones:
            s.blit(art.stone, (st.x - 3 - cam[0], st.y - 3 - cam[1]))
        for pt in self.particles:
            a = pt.life / pt.max
            col = pt.col
            pygame.draw.rect(s, col, (int(pt.x - cam[0]), int(pt.y - cam[1]), pt.size, pt.size))
        # pogoda (przed ciemnością w jaskini)
        if self.theme in ('ice', 'valley', 'cave'):
            for wp in self.weather:
                if self.theme == 'ice':
                    sz = 1 if wp[2] < 0.6 else 2
                    pygame.draw.rect(s, (255, 255, 255), (int(wp[0]), int(wp[1]), sz, sz))
                elif self.theme == 'cave':
                    s.set_at((int(wp[0]), int(wp[1])), (120, 110, 100))
                else:
                    if wp[2] < 0.3:
                        s.set_at((int(wp[0]), int(wp[1])), (255, 255, 220))
        if self.dark:
            self.draw_darkness(s, cam, art)
        if self.theme == 'lair':
            for wp in self.weather:
                c = (255, int(120 + wp[2] * 100), 60)
                pygame.draw.rect(s, c, (int(wp[0]), int(wp[1]), 1 + (wp[2] > 0.7), 1 + (wp[2] > 0.7)))
        for e in self.eyes:
            if e.state == 'show':
                a = min(1, e.t * 2, (2.6 - e.t) * 2)
                blink = (e.t % 1.1) < 0.12
                if a > 0 and not blink:
                    col = (int(255 * a), int(230 * a), int(60 * a))
                    for ox in (0, 9):
                        pygame.draw.rect(s, col, (e.x + ox - cam[0], e.y - cam[1], 4, 2))
                        pygame.draw.rect(s, (int(255 * a), int(255 * a), int(200 * a)),
                                         (e.x + ox + 1 - cam[0], e.y - cam[1], 1, 1))

    def draw_player(self, s, cam, art):
        p = self.player
        if p.inv > 0 and int(p.inv * 14) % 2 and p.knock <= 0:
            return
        if p.knock > 0:
            pose, f = 'hurt', 0
        elif not p.on_ground:
            pose, f = ('jump', 0) if p.vy < 0 else ('fall', 0)
        elif abs(p.vx) > 12:
            pose, f = 'walk', int(p.walk_t) % 4
        else:
            pose, f = 'idle', int(p.t * 3) % 4
        k = (1 - p.attack / 0.3) if p.attack > 0 else None
        canvas, foot = compose_damian(art, pose, f, k, p.walk_t)
        if p.facing < 0:
            canvas = pygame.transform.flip(canvas, True, False)
        fx = foot[0] if p.facing > 0 else canvas.get_width() - foot[0]
        s.blit(canvas, (p.cx - fx - cam[0], p.y + p.h - foot[1] - cam[1] + 1))

    def draw_darkness(self, s, cam, art):
        dark = pygame.Surface((W, H), pygame.SRCALPHA)
        dark.fill((6, 4, 14, self.dark))
        p = self.player
        fl = int(self.time * 12) % 2
        L = art.lights

        def light(x, y, r):
            img = L[r]
            dark.blit(img, (x - r - cam[0], y - r - cam[1]), special_flags=pygame.BLEND_RGBA_MIN)

        light(p.cx, p.cy, 70 if fl else 76)
        for t in self.torches:
            if t.lit:
                light(t.cx, t.y + 4, 96 if fl else 88)
        for k in self.kids:
            if k.state != 'gone':
                light(k.cx, k.cy, 26)
        for r in self.runes:
            light(r.cx, r.cy, 40 if r.lit else 26)
        if self.exit:
            light(self.exit.cx, self.exit.cy, 40)
        if self.painting:
            light(self.painting.cx, self.painting.cy, 40)
        for h in self.hints:
            light(h.cx, h.cy, 26)
        if self.lion and self.boss_active:
            light(self.lion.cx, self.lion.cy, 64)
        s.blit(dark, (0, 0))
        for t in self.torches:
            if t.lit:
                s.blit(art.glow, (t.cx - 60 - cam[0], t.y + 4 - 60 - cam[1]), special_flags=pygame.BLEND_RGB_ADD)
        s.blit(art.glow_small, (p.cx - 24 - cam[0], p.cy - 24 - cam[1]), special_flags=pygame.BLEND_RGB_ADD)


# ======================================================================= gra
def save_path():
    base = os.getenv('APPDATA') or os.path.expanduser('~')
    d = os.path.join(base, 'DamianJaskiniowiec')
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return os.path.join(d, 'zapis.json')


class Game:
    def __init__(self, screen=None):
        self.audio = Audio()
        pygame.display.set_caption(TITLE)
        try:
            pygame.display.set_icon(G.make_icon())
        except Exception:
            pass
        if screen is None:
            screen = pygame.display.set_mode((SW, SH), pygame.SCALED | pygame.RESIZABLE)
        self.screen = screen
        self.world = pygame.Surface((W, H))
        self.art = Art()
        self.inp = Input()
        self.inp.scan_joys()
        self.f_big = pygame.font.Font(None, 72)
        self.f_mid = pygame.font.Font(None, 40)
        self.f_txt = pygame.font.Font(None, 30)
        self.f_small = pygame.font.Font(None, 24)
        self.state = 'title'
        self.level = None
        self.score = 0
        self.lives = 3
        self.flint = 0
        self.menu = 0
        self.t = 0
        self.story = []
        self.story_i = 0
        self.story_t = 0
        self.after_story = None
        self.dialog = None
        self.message = None
        self.clear_t = 0
        self.save = self.load_save()
        self.running = True
        self.title_level = None
        self.audio.play_music('adventure')
        self.sprites_for_story = {
            'damian_idle': self.art.damian[('idle', 0)],
            'kids': [self.art.kid(k, 0, True) for L in P.LEVELS for k in L['kids']],
        }

    # ------------------------------------------------------------------ zapis
    def load_save(self):
        try:
            with open(save_path(), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def write_save(self):
        try:
            with open(save_path(), 'w', encoding='utf-8') as f:
                json.dump(self.save, f)
        except Exception:
            pass

    # ------------------------------------------------------------------ przejścia
    def new_game(self):
        self.score = 0
        self.lives = 3
        self.flint = 0
        self.start_story(P.STORY_INTRO, lambda: self.start_level(0))

    def continue_game(self):
        s = self.save
        self.score = s.get('score', 0)
        self.lives = max(3, s.get('lives', 3))
        self.flint = s.get('flint', 0)
        self.start_level(s.get('level', 0))

    def start_story(self, slides, after):
        self.story = slides
        self.story_i = 0
        self.story_t = 0
        self.after_story = after
        self.state = 'story'

    def start_level(self, idx):
        self.level = Level(self, idx)
        self.state = 'play'
        self.audio.play_music(self.level.data['music'])

    def level_clear(self):
        self.state = 'clear'
        self.clear_t = 0
        self.audio.play('correct')
        L = self.level
        bonus = int(max(0, 300 - L.time) * 5)
        self.clear_bonus = bonus
        self.score += bonus
        nxt = L.idx + 1
        if nxt < len(P.LEVELS):
            self.save = {'level': nxt, 'score': self.score, 'lives': self.lives, 'flint': self.flint}
            self.write_save()

    def after_clear(self):
        idx = self.level.idx
        if idx + 1 < len(P.LEVELS):
            self.start_story(P.STORY_BETWEEN[idx], lambda: self.start_level(idx + 1))
        else:
            self.save = {}
            self.write_save()
            self.audio.play_music('adventure')
            self.start_story(P.STORY_END, self.to_credits)

    def to_credits(self):
        self.state = 'credits'
        self.t = 0

    def game_over(self):
        self.state = 'gameover'
        self.t = 0
        self.audio.play('wrong')
        self.audio.stop_music()

    def open_dialog(self, kid):
        self.state = 'dialog'
        self.dialog = dict(kid=kid, phase='hello', sel=0, wrong=set(), t=0)
        self.audio.play('talk')

    def open_message(self, text, title="", image=None):
        self.state = 'message'
        self.message = dict(text=text, title=title, image=image, t=0)
        self.audio.play('talk')

    # ------------------------------------------------------------------ pętla
    def run(self):
        clock = pygame.time.Clock()
        acc = 0
        while self.running:
            ms = clock.tick(FPS)
            acc = min(acc + ms / 1000, 0.1)
            self.inp.begin()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                self.inp.event(e)
            if self.inp.hit('full'):
                try:
                    pygame.display.toggle_fullscreen()
                except Exception:
                    pass
            if self.inp.hit('mute'):
                self.audio.toggle_mute()
            steps = 0
            while acc >= DT and steps < 4:
                self.update(DT)
                self.inp.pressed = set()
                acc -= DT
                steps += 1
            self.render()
            pygame.display.flip()
        pygame.quit()

    def update(self, dt):
        self.t += dt
        inp = self.inp
        st = self.state
        if st == 'title':
            n = len(self.title_items())
            if inp.hit('menu_up'):
                self.menu = (self.menu - 1) % n
                self.audio.play('talk')
            if inp.hit('menu_down'):
                self.menu = (self.menu + 1) % n
                self.audio.play('talk')
            if inp.hit('confirm') or inp.hit('interact'):
                items = self.title_items()
                act = items[self.menu][1]
                self.audio.play('collect')
                act()
            if inp.hit('pause'):
                self.running = False
        elif st == 'controls':
            if inp.hit('confirm') or inp.hit('pause') or inp.hit('back'):
                self.state = 'title'
        elif st == 'story':
            self.story_t += dt
            if inp.hit('confirm') or inp.hit('interact'):
                text = self.story[self.story_i][1]
                if self.story_t * 45 < len(text):
                    self.story_t = 999
                else:
                    self.story_i += 1
                    self.story_t = 0
                    self.audio.play('talk')
                    if self.story_i >= len(self.story):
                        self.after_story()
            if inp.hit('pause'):
                self.after_story()
        elif st == 'play':
            if inp.hit('pause'):
                self.state = 'pause'
                self.menu = 0
                return
            self.level.update(inp, dt)
        elif st == 'pause':
            if inp.hit('menu_up') or inp.hit('menu_down'):
                self.menu = 1 - self.menu
            if inp.hit('pause'):
                self.state = 'play'
            elif inp.hit('confirm'):
                if self.menu == 0:
                    self.state = 'play'
                else:
                    self.state = 'title'
                    self.menu = 0
                    self.save = self.load_save()
                    self.audio.play_music('adventure')
        elif st == 'dialog':
            self.update_dialog(dt)
        elif st == 'message':
            self.message['t'] += dt
            if self.message['t'] > 0.25 and (inp.hit('confirm') or inp.hit('pause') or inp.hit('interact')):
                self.state = 'play'
        elif st == 'clear':
            self.clear_t += dt
            if self.clear_t > 1.0 and (inp.hit('confirm') or inp.hit('interact')):
                self.after_clear()
        elif st == 'gameover':
            if self.t > 1.0 and (inp.hit('confirm') or inp.hit('interact')):
                self.state = 'title'
                self.menu = 0
                self.save = self.load_save()
                self.audio.play_music('adventure')
        elif st == 'credits':
            if self.t > 1.5 and (inp.hit('confirm') or inp.hit('pause')):
                self.state = 'title'
                self.menu = 0
                self.save = self.load_save()

    def title_items(self):
        items = []
        if self.save.get('level'):
            items.append(("Kontynuuj: " + P.LEVELS[self.save['level']]['name'], self.continue_game))
        items.append(("Nowa gra", self.new_game))
        items.append(("Sterowanie", lambda: setattr(self, 'state', 'controls')))
        items.append(("Wyjście", lambda: setattr(self, 'running', False)))
        return items

    def update_dialog(self, dt):
        d = self.dialog
        inp = self.inp
        d['t'] += dt
        kid = d['kid']
        info = kid.info
        if d['phase'] == 'question':
            n = len(info['a'])
            if inp.hit('menu_up'):
                d['sel'] = (d['sel'] - 1) % n
                self.audio.play('talk')
            if inp.hit('menu_down'):
                d['sel'] = (d['sel'] + 1) % n
                self.audio.play('talk')
            for i, k in enumerate(('n1', 'n2', 'n3')):
                if inp.hit(k) and i < n:
                    d['sel'] = i
                    self.answer(i)
                    return
            if d['t'] > 0.3 and (inp.hit('confirm')):
                self.answer(d['sel'])
            return
        if d['t'] < 0.25:
            return
        if inp.hit('confirm') or inp.hit('interact'):
            if d['phase'] == 'hello':
                d['phase'] = 'question'
                d['t'] = 0
                d['sel'] = 0
            elif d['phase'] == 'wrong':
                d['phase'] = 'question'
                d['t'] = 0
            elif d['phase'] == 'right':
                kid.state = 'happy'
                kid.timer = 1.0
                L = self.level
                pts = 500 if not d['wrong'] else 250
                L.add_score(pts, kid.cx, kid.y - 10)
                L.float_text("Dzieci: %d/%d" % (L.kids_taught(), len(L.kids)), kid.cx, kid.y - 26, (160, 255, 160), 2.2)
                L.burst(kid.cx, kid.cy, (255, 240, 140), 18)
                self.state = 'play'
                self.audio.play('life')

    def answer(self, i):
        d = self.dialog
        info = d['kid'].info
        if i in d['wrong']:
            return
        d['t'] = 0
        if i == info['ok']:
            d['phase'] = 'right'
            self.audio.play('correct')
        else:
            d['wrong'].add(i)
            d['phase'] = 'wrong'
            self.audio.play('wrong')

    # ------------------------------------------------------------------ rysowanie
    def text(self, font, txt, pos, col=(255, 255, 255), center=False, shadow=True, surf=None):
        surf = surf or self.screen
        img = font.render(txt, True, col)
        x, y = pos
        if center:
            x -= img.get_width() / 2
        if shadow:
            sh = font.render(txt, True, (20, 12, 10))
            for ox, oy in ((2, 2), (-1, 1), (1, -1), (2, 0), (0, 2)):
                surf.blit(sh, (x + ox, y + oy))
        surf.blit(img, (x, y))
        return img.get_width()

    def wrap(self, font, txt, width):
        words = txt.split(' ')
        lines, cur = [], ''
        for w in words:
            test = (cur + ' ' + w).strip()
            if font.size(test)[0] > width and cur:
                lines.append(cur)
                cur = w
            else:
                cur = test
        if cur:
            lines.append(cur)
        return lines

    def panel(self, rect, alpha=225):
        r = pygame.Rect(rect)
        s = pygame.Surface(r.size, pygame.SRCALPHA)
        s.fill((40, 26, 20, alpha))
        pygame.draw.rect(s, (214, 170, 100), s.get_rect(), 3, border_radius=10)
        pygame.draw.rect(s, (120, 80, 46), s.get_rect().inflate(-8, -8), 1, border_radius=8)
        self.screen.blit(s, r.topleft)

    def render(self):
        st = self.state
        if st in ('title', 'controls'):
            self.render_title()
        elif st == 'story':
            self.render_story()
        elif st == 'credits':
            self.render_credits()
        else:
            self.level.draw(self.world, self.art)
            pygame.transform.scale(self.world, (SW, SH), self.screen)
            self.render_world_text()
            self.render_hud()
            if st == 'dialog':
                self.render_dialog()
            elif st == 'message':
                self.render_message()
            elif st == 'pause':
                self.render_pause()
            elif st == 'clear':
                self.render_clear()
            elif st == 'gameover':
                self.render_gameover()

    def render_world_text(self):
        L = self.level
        cam = L.cam
        for text, x, y, life, mx, col in L.floats:
            a = min(1, life / 0.4)
            img = self.f_small.render(text, True, col)
            sh = self.f_small.render(text, True, (20, 12, 10))
            img.set_alpha(int(255 * a))
            sh.set_alpha(int(255 * a))
            px = (x - cam[0]) * 2 - img.get_width() / 2
            py = (y - cam[1]) * 2 - 20
            self.screen.blit(sh, (px + 2, py + 2))
            self.screen.blit(img, (px, py))
        if self.state == 'play':
            near = L.near_interactive()
            if near:
                kind, obj = near
                label = {'kid': "E – porozmawiaj", 'hint': "E – czytaj", 'paint': "E – obejrzyj"}[kind]
                p = L.player
                self.text(self.f_small, label, ((p.cx - cam[0]) * 2, (p.y - cam[1]) * 2 - 44),
                          (255, 240, 180), center=True)

    def render_hud(self):
        L = self.level
        p = L.player
        sc = self.screen
        for i in range(p.max_hp):
            img = self.art.heart if i < p.hp else self.art.heart_empty
            sc.blit(pygame.transform.scale(img, (26, 24)), (16 + i * 30, 14))
        head = pygame.transform.scale(self.art.damian[('idle', 0)].subsurface((4, 0, 18, 14)), (36, 28))
        sc.blit(head, (16, 44))
        self.text(self.f_txt, "x %d" % max(0, self.lives), (56, 50))
        fl = pygame.transform.scale(self.art.items['f'], (28, 28))
        sc.blit(fl, (110, 46))
        self.text(self.f_txt, "x %d" % self.flint, (142, 50))
        kidimg = pygame.transform.scale(self.art.kid(P.LEVELS[0]['kids'][0], 0, True), (24, 32))
        sc.blit(kidimg, (SW - 170, 12))
        self.text(self.f_txt, "%d / %d" % (L.kids_taught(), len(L.kids)), (SW - 140, 20),
                  (160, 255, 160) if L.kids_taught() == len(L.kids) else (255, 255, 255))
        self.text(self.f_txt, "%07d" % self.score, (SW / 2, 14), (255, 230, 120), center=True)
        if L.banner > 0:
            a = min(1, L.banner, (3.5 - L.banner) * 3)
            img = pygame.Surface((SW, 120), pygame.SRCALPHA)
            img.fill((0, 0, 0, int(140 * a)))
            sc.blit(img, (0, 170))
            sub = self.f_mid.render(L.data['subtitle'], True, (230, 200, 140))
            ttl = self.f_big.render(L.data['name'], True, (255, 255, 255))
            sub.set_alpha(int(255 * a))
            ttl.set_alpha(int(255 * a))
            sc.blit(sub, (SW / 2 - sub.get_width() / 2, 180))
            sc.blit(ttl, (SW / 2 - ttl.get_width() / 2, 218))
            info = self.f_small.render("Odnajdź dzieci (%d) i naucz je przetrwania!" % len(L.kids), True, (255, 240, 200))
            info.set_alpha(int(255 * a))
            sc.blit(info, (SW / 2 - info.get_width() / 2, 268))
        if L.lion and L.boss_active and L.lion.state != 'flee':
            self.text(self.f_small, "LEW JASKINIOWY", (SW / 2, SH - 52), (255, 200, 160), center=True)
            pygame.draw.rect(sc, (30, 16, 12), (SW / 2 - 152, SH - 28, 304, 16))
            w = int(300 * L.lion.hp / L.lion.max_hp)
            pygame.draw.rect(sc, (220, 80, 50), (SW / 2 - 150, SH - 26, w, 12))
        if self.audio.muted:
            self.text(self.f_small, "dźwięk wył. (M)", (SW - 170, SH - 30), (200, 200, 200))

    def render_dialog(self):
        d = self.dialog
        info = d['kid'].info
        sc = self.screen
        top = 300
        self.panel((20, top, SW - 40, SH - top - 16))
        frame = pygame.Rect(40, top + 22, 130, 150)
        pygame.draw.rect(sc, (70, 46, 30), frame, border_radius=8)
        pygame.draw.rect(sc, (214, 170, 100), frame, 2, border_radius=8)
        happy = d['phase'] == 'right'
        img = self.art.kid(info, int(self.t * 8), happy)
        img = pygame.transform.scale(img, (img.get_width() * 6, img.get_height() * 6))
        sc.blit(img, (frame.centerx - img.get_width() / 2, frame.bottom - img.get_height() - 4))
        self.text(self.f_txt, info['name'], (frame.centerx, frame.bottom + 4), (255, 230, 140), center=True)
        x0 = 196
        width = SW - x0 - 50
        ph = d['phase']
        if ph == 'hello':
            lines = self.wrap(self.f_txt, info['hello'], width)
            shown = int(d['t'] * 60)
            y = top + 26
            cnt = 0
            for ln in lines:
                part = ln[:max(0, shown - cnt)]
                cnt += len(ln)
                self.text(self.f_txt, part, (x0, y), shadow=False)
                y += 30
            self.text(self.f_small, "Damian: Spokojnie, %s. Najpierw lekcja przetrwania!" % info['name'],
                      (x0, SH - 70), (255, 220, 150), shadow=False)
            self.text(self.f_small, "[Enter]", (SW - 110, SH - 46), (200, 180, 140), shadow=False)
        elif ph in ('question', 'wrong'):
            lines = self.wrap(self.f_txt, info['q'], width)
            y = top + 22
            for ln in lines:
                self.text(self.f_txt, ln, (x0, y), (255, 240, 200), shadow=False)
                y += 30
            y += 8
            for i, a in enumerate(info['a']):
                sel = i == d['sel']
                bad = i in d['wrong']
                col = (130, 110, 100) if bad else ((255, 220, 100) if sel else (240, 230, 220))
                r = pygame.Rect(x0 - 8, y - 4, width, 32)
                if sel and not bad:
                    pygame.draw.rect(sc, (90, 60, 36), r, border_radius=6)
                txt = "%d. %s" % (i + 1, a)
                self.text(self.f_txt, txt, (x0, y), col, shadow=False)
                if bad:
                    wdt = self.f_txt.size(txt)[0]
                    pygame.draw.line(sc, (200, 70, 60), (x0, y + 11), (x0 + wdt, y + 11), 3)
                y += 36
            if ph == 'wrong':
                self.text(self.f_small, "%s: Hmm... chyba nie. Spróbuj jeszcze raz!" % info['name'],
                          (x0, SH - 52), (255, 160, 140), shadow=False)
            else:
                self.text(self.f_small, "Wybierz: strzałki + Enter lub klawisze 1-3", (x0, SH - 52),
                          (200, 180, 140), shadow=False)
        elif ph == 'right':
            self.text(self.f_mid, "Brawo! Dobra odpowiedź!", (x0, top + 22), (140, 255, 140), shadow=False)
            lines = self.wrap(self.f_txt, info['why'], width)
            y = top + 70
            for ln in lines:
                self.text(self.f_txt, ln, (x0, y), shadow=False)
                y += 30
            self.text(self.f_small, "%s: Dziękuję! Biegnę do obozu!" % info['name'], (x0, SH - 52),
                      (255, 220, 150), shadow=False)
            self.text(self.f_small, "[Enter]", (SW - 110, SH - 46), (200, 180, 140), shadow=False)

    def render_message(self):
        m = self.message
        img = m['image']
        h = 200 + (img.get_height() * 5 + 20 if img else 0)
        top = (SH - h) // 2
        self.panel((120, top, SW - 240, h))
        y = top + 20
        self.text(self.f_mid, m['title'], (SW / 2, y), (255, 220, 140), center=True)
        y += 50
        if img:
            big = pygame.transform.scale(img, (img.get_width() * 5, img.get_height() * 5))
            self.screen.blit(big, (SW / 2 - big.get_width() / 2, y))
            y += big.get_height() + 16
        for ln in self.wrap(self.f_txt, m['text'], SW - 320):
            self.text(self.f_txt, ln, (SW / 2, y), center=True, shadow=False)
            y += 30
        self.text(self.f_small, "[Enter]", (SW / 2, top + h - 34), (200, 180, 140), center=True, shadow=False)

    def render_pause(self):
        s = pygame.Surface((SW, SH), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))
        self.text(self.f_big, "PAUZA", (SW / 2, 150), center=True)
        for i, t in enumerate(("Wróć do gry", "Wyjdź do menu (postęp do początku poziomu)")):
            col = (255, 220, 100) if i == self.menu else (230, 230, 230)
            self.text(self.f_mid, ("> " if i == self.menu else "") + t, (SW / 2, 260 + i * 50), col, center=True)
        self.text(self.f_small, "R – ustaw głazy od nowa  ·  M – dźwięk  ·  F11 – pełny ekran", (SW / 2, SH - 60),
                  (200, 200, 200), center=True)

    def render_clear(self):
        L = self.level
        s = pygame.Surface((SW, SH), pygame.SRCALPHA)
        s.fill((0, 0, 0, min(170, int(self.clear_t * 300))))
        self.screen.blit(s, (0, 0))
        self.text(self.f_big, "Rozdział ukończony!", (SW / 2, 120), (255, 220, 120), center=True)
        self.text(self.f_mid, L.data['name'], (SW / 2, 190), center=True)
        lines = ["Dzieci nauczone: %d / %d" % (L.kids_taught(), len(L.kids)),
                 "Czas: %d:%02d" % (int(L.time) // 60, int(L.time) % 60),
                 "Premia za czas: %d" % self.clear_bonus,
                 "Wynik: %d" % self.score]
        for i, ln in enumerate(lines):
            self.text(self.f_txt, ln, (SW / 2, 260 + i * 36), center=True)
        if self.clear_t > 1.0:
            self.text(self.f_small, "[Enter] – dalej", (SW / 2, SH - 70), (200, 200, 200), center=True)

    def render_gameover(self):
        s = pygame.Surface((SW, SH), pygame.SRCALPHA)
        s.fill((20, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        self.text(self.f_big, "KONIEC PRZYGODY", (SW / 2, 180), (255, 120, 100), center=True)
        self.text(self.f_txt, "Ogień zgasł... ale nauczyciel nigdy się nie poddaje!", (SW / 2, 260), center=True)
        self.text(self.f_txt, "Wynik: %d" % self.score, (SW / 2, 300), center=True)
        self.text(self.f_small, "[Enter] – menu (możesz kontynuować od ostatniego rozdziału)", (SW / 2, SH - 80),
                  (200, 200, 200), center=True)

    def render_title(self):
        if self.title_level is None:
            self.title_level = Level(self, 0)
            self.title_level.banner = 0
        L = self.title_level
        L.time += 1 / FPS
        L.cam[0] = (self.t * 30) % (L.w * T - W)
        L.cam[1] = L.h * T - H
        L.player.x = -100
        L.draw(self.world, self.art)
        sc = self.screen
        pygame.transform.scale(self.world, (SW, SH), sc)
        s = pygame.Surface((SW, SH), pygame.SRCALPHA)
        s.fill((20, 10, 6, 110))
        sc.blit(s, (0, 0))
        bob = math.sin(self.t * 2) * 4
        self.text(self.f_big, "DAMIAN JASKINIOWIEC", (SW / 2, 54 + bob), (255, 214, 110), center=True)
        self.text(self.f_mid, "~ Ogień Pierwszy ~", (SW / 2, 118 + bob), (255, 160, 90), center=True)
        dam, _ = compose_damian(self.art, 'walk', int(self.t * 8) % 4, None, self.t * 8)
        big = pygame.transform.scale(dam, (dam.get_width() * 5, dam.get_height() * 5))
        sc.blit(big, (20, 150))
        for i, k in enumerate(P.LEVELS[0]['kids'] + P.LEVELS[1]['kids'][:1]):
            img = self.art.kid(k, int(self.t * 10) + i, True)
            img = pygame.transform.scale(img, (img.get_width() * 4, img.get_height() * 4))
            sc.blit(img, (SW - 330 + i * 62, 330 + (i % 2) * 6))
        if self.state == 'controls':
            self.panel((250, 170, SW - 500, 330))
            rows = [("Strzałki / A, D", "chodzenie"), ("Spacja / W / ↑", "skok (przytrzymaj = wyżej)"),
                    ("↓ + skok", "zeskok z kłody"), ("X / J / Ctrl", "maczuga"), ("C / K", "rzut krzemieniem"),
                    ("E / Enter", "rozmowa, czytanie"), ("R", "ustaw głazy od nowa"),
                    ("Esc", "pauza"), ("F11 / M", "pełny ekran / dźwięk")]
            for i, (a, b) in enumerate(rows):
                self.text(self.f_small, a, (280, 190 + i * 30), (255, 220, 140), shadow=False)
                self.text(self.f_small, b, (480, 190 + i * 30), shadow=False)
            self.text(self.f_small, "Działa też pad (A – skok, X – maczuga, B – rzut, Y – rozmowa)",
                      (SW / 2, 468), (200, 200, 200), center=True, shadow=False)
            return
        items = self.title_items()
        if self.menu >= len(items):
            self.menu = 0
        for i, (label, _) in enumerate(items):
            sel = i == self.menu
            col = (255, 220, 100) if sel else (240, 230, 220)
            self.text(self.f_mid, ("> " if sel else "") + label + (" <" if sel else ""),
                      (SW / 2, 220 + i * 48), col, center=True)
        self.text(self.f_small, "Gra edukacyjna o paleolicie · Szkoła Mentis", (SW / 2, SH - 34),
                  (230, 210, 180), center=True)

    def render_story(self):
        name, text = self.story[self.story_i]
        img = G.story_scene(name, self.t, self.sprites_for_story)
        self.screen.fill(img.get_at((0, H - 1)))
        self.screen.blit(pygame.transform.scale(img, (SW, SH)), (0, -100))
        self.panel((40, SH - 170, SW - 80, 150), 235)
        shown = int(self.story_t * 45)
        y = SH - 150
        cnt = 0
        for ln in self.wrap(self.f_txt, text, SW - 140):
            part = ln[:max(0, shown - cnt)]
            cnt += len(ln) + 1
            self.text(self.f_txt, part, (70, y), shadow=False)
            y += 32
        self.text(self.f_small, "[Enter] dalej · [Esc] pomiń", (SW - 290, SH - 48), (200, 180, 140), shadow=False)

    def render_credits(self):
        sc = self.screen
        img = G.story_scene('end', self.t, self.sprites_for_story)
        pygame.transform.scale(img, (SW, SH), sc)
        s = pygame.Surface((SW, SH), pygame.SRCALPHA)
        s.fill((0, 0, 0, 120))
        sc.blit(s, (0, 0))
        self.text(self.f_big, "KONIEC", (SW / 2, 90), (255, 220, 120), center=True)
        lines = ["Damian odnalazł wszystkie dzieci i odzyskał Ogień Pierwszy.",
                 "Wynik końcowy: %d" % self.score, "",
                 "Gra edukacyjna o paleolicie dla Szkoły Mentis",
                 "Grafika, muzyka i dźwięki wygenerowane w kodzie gry.",
                 "", "[Enter] – menu główne"]
        for i, ln in enumerate(lines):
            self.text(self.f_txt, ln, (SW / 2, 190 + i * 38), center=True)


def main():
    pygame.init()
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
