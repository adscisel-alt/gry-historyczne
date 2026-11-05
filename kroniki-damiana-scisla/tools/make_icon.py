# -*- coding: utf-8 -*-
"""Generuje assets/icon.ico (portret Damiana Ścisła) – ICO z osadzonymi PNG."""
import io
import os
import struct
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))
from kronika import gfx, data  # noqa: E402

pngs = []
for size in (256, 64, 48, 32, 16):
    k = max(1, size // 32)
    s = gfx.portrait(data.HERO["p"], k)
    s = pygame.transform.scale(s, (size, size))
    buf = io.BytesIO()
    pygame.image.save(s, buf, "png")
    pngs.append((size, buf.getvalue()))
out = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
with open(out, "wb") as f:
    f.write(struct.pack("<HHH", 0, 1, len(pngs)))
    offset = 6 + 16 * len(pngs)
    for size, png in pngs:
        f.write(struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(png), offset))
        offset += len(png)
    for _, png in pngs:
        f.write(png)
print("zapisano", out)
