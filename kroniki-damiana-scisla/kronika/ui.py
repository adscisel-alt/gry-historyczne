# -*- coding: utf-8 -*-
"""Czcionki, zawijanie tekstu, przyciski."""
import os
import sys
import pygame

from . import gfx

INK = (52, 34, 20)
INK_SOFT = (96, 70, 46)
GOLD = (236, 200, 96)
CREAM = (246, 234, 204)
RED = (170, 40, 36)
GREEN = (50, 120, 50)
PURPLE = (112, 52, 156)


def resource_path(*parts):
    base = getattr(sys, "_MEIPASS", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    return os.path.join(base, *parts)


_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
        path = resource_path("assets", "fonts", name)
        try:
            _fonts[key] = pygame.font.Font(path, size)
        except Exception:
            _fonts[key] = pygame.font.Font(None, int(size * 1.3))
    return _fonts[key]


def wrap(text, f, width):
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            t = (cur + " " + w).strip()
            if f.size(t)[0] <= width:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def draw_text(surf, text, pos, size=18, color=INK, bold=False, width=None, center=False, line_h=None, shadow=None):
    f = font(size, bold)
    lines = wrap(text, f, width) if width else [text]
    x, y = pos
    lh = line_h or int(f.get_linesize() * 1.02)
    for ln in lines:
        img = f.render(ln, True, color)
        dx = x - img.get_width() // 2 if center else x
        if shadow:
            surf.blit(f.render(ln, True, shadow), (dx + 2, y + 2))
        surf.blit(img, (dx, y))
        y += lh
    return y


def text_height(text, size, width, bold=False):
    f = font(size, bold)
    return len(wrap(text, f, width)) * int(f.get_linesize() * 1.02)


class Button:
    def __init__(self, rect, label, cb=None, size=18, enabled=True, tip=None, icon=None, color=None, key=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.cb = cb
        self.size = size
        self.enabled = enabled
        self.tip = tip
        self.icon = icon
        self.color = color or (120, 78, 40)
        self.key = key
        self.hover = False

    def draw(self, surf):
        r = self.rect
        base = self.color if self.enabled else (120, 112, 100)
        if self.hover and self.enabled:
            base = gfx.shade(base, 1.25)
        pygame.draw.rect(surf, gfx.shade(base, 0.55), r.move(0, 3))
        pygame.draw.rect(surf, base, r)
        pygame.draw.rect(surf, gfx.shade(base, 1.35), (r.x + 2, r.y + 2, r.w - 4, 2))
        pygame.draw.rect(surf, (40, 26, 14), r, 2)
        f = font(self.size, True)
        col = CREAM if self.enabled else (200, 194, 180)
        img = f.render(self.label, True, col)
        x = r.centerx - img.get_width() // 2
        if self.icon is not None:
            ic = self.icon
            x += ic.get_width() // 2 + 3
            surf.blit(ic, (x - ic.get_width() - 6, r.centery - ic.get_height() // 2))
        surf.blit(f.render(self.label, True, (30, 20, 10)), (x + 1, r.centery - img.get_height() // 2 + 1))
        surf.blit(img, (x, r.centery - img.get_height() // 2))

    def handle(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.rect.collidepoint(ev.pos):
            if self.enabled and self.cb:
                from . import audio
                audio.play("click")
                self.cb()
            return True
        elif ev.type == pygame.KEYDOWN and self.key is not None and ev.key == self.key and self.enabled and self.cb:
            self.cb()
            return True
        return False


def cost_str(cost):
    from .data import RES_NAMES
    if not cost:
        return "za darmo"
    return ", ".join(f"{v} {RES_NAMES[k].lower()}" for k, v in cost.items())


def draw_cost(surf, cost, pos, have=None, size=16):
    x, y = pos
    for k, v in cost.items():
        ic = gfx.icon(k, 2)
        surf.blit(ic, (x, y))
        col = INK if (have is None or have.get(k, 0) >= v) else RED
        img = font(size, True).render(str(v), True, col)
        surf.blit(img, (x + 26, y + 2))
        x += 30 + img.get_width() + 8
    return x
