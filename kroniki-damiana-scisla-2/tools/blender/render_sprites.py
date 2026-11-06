# -*- coding: utf-8 -*-
"""Blender: modeluje i renderuje grafikę 3D gry „Kroniki Damiana Ścisła II: Rzeczpospolita”.

Tak jak w klasycznych strategiach z lat 90. (np. Age of Empires II) grafika jest
prerenderowanym 3D: modele low-poly budowane są tu z prymitywów Blendera,
oświetlane słońcem i renderowane silnikiem Cycles kamerą ortograficzną w rzucie
izometrycznym 2:1. Wynik – przezroczyste PNG – trafia do assets/3d/ i gra wczytuje
je zamiast grafiki pikselowej (klawisz G w grze przełącza styl).

Uruchomienie (Blender jako moduł Pythona):
    pip install bpy                 # Blender 5.x, Python 3.13
    python tools/blender/render_sprites.py [--only nazwa] [--samples 32]
albo w zainstalowanym Blenderze:
    blender -b -P tools/blender/render_sprites.py
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "assets", "3d"))
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ONLY = ARGS[ARGS.index("--only") + 1] if "--only" in ARGS else None
SAMPLES = int(ARGS[ARGS.index("--samples") + 1]) if "--samples" in ARGS else 32

SQ2 = math.sqrt(2)
PPU_ISO = 64 / SQ2   # piksele na jednostkę: kafel 1x1 = romb 64x32 px
PPU_BLD = PPU_ISO * 1.18  # budynki lekko wystają poza kafel, jak w klasycznych strategiach

FACTION = {
    "pl": {"tunic": (190, 40, 44), "trim": (235, 235, 235), "shield": (235, 235, 235), "emb": (190, 40, 44)},
    "cz": {"tunic": (200, 170, 60), "trim": (60, 60, 60), "shield": (200, 40, 40), "emb": (240, 240, 240)},
    "kz": {"tunic": (235, 235, 230), "trim": (190, 30, 30), "shield": (235, 235, 230), "emb": (190, 30, 30)},
    "en": {"tunic": (110, 90, 64), "trim": (70, 56, 40), "shield": (90, 70, 50), "emb": (60, 50, 40)},
    "mg": {"tunic": (150, 100, 50), "trim": (90, 60, 30), "shield": (120, 80, 40), "emb": (200, 170, 90)},
    "tz": {"tunic": (238, 238, 232), "trim": (20, 20, 20), "shield": (238, 238, 232), "emb": (20, 20, 20)},
    "lt": {"tunic": (150, 30, 40), "trim": (60, 120, 70), "shield": (150, 30, 40), "emb": (240, 240, 240)},
    "ru": {"tunic": (60, 110, 70), "trim": (180, 40, 40), "shield": (180, 40, 40), "emb": (230, 200, 80)},
    "sv": {"tunic": (50, 80, 160), "trim": (230, 200, 60), "shield": (50, 80, 160), "emb": (230, 200, 60)},
    "tr": {"tunic": (170, 40, 40), "trim": (240, 240, 230), "shield": (60, 120, 70), "emb": (240, 220, 120)},
    "rs": {"tunic": (40, 90, 60), "trim": (180, 40, 40), "shield": (40, 90, 60), "emb": (230, 230, 230)},
    "au": {"tunic": (235, 235, 228), "trim": (180, 40, 40), "shield": (235, 235, 228), "emb": (40, 40, 40)},
}
SKIN = (232, 186, 150)
STEEL = (170, 176, 186)
WOOD = (150, 108, 64)
DWOOD = (100, 70, 42)
THATCH = (196, 164, 92)
STONE = (168, 164, 154)
RED_ROOF = (170, 64, 48)
WHITE = (226, 222, 210)
GOLD = (232, 196, 70)


# ------------------------------------------------------------------ scena
def lin(c):
    return tuple((v / 255.0) ** 2.2 for v in c[:3]) + (1.0,)


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    try:
        sc.cycles.use_denoising = True
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        sc.cycles.use_denoising = False
    sc.cycles.max_bounces = 4
    sc.render.film_transparent = True
    sc.render.filter_size = 0.7
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("Swiat")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = lin((150, 160, 185))
    bg.inputs[1].default_value = 0.9
    sun = bpy.data.lights.new("Slonce", "SUN")
    sun.energy = 3.6
    sun.angle = math.radians(6)
    so = bpy.data.objects.new("Slonce", sun)
    sc.collection.objects.link(so)
    so.rotation_euler = Vector((-0.45, -0.8, 1.0)).to_track_quat("Z", "Y").to_euler()
    cam = bpy.data.cameras.new("Kamera")
    co = bpy.data.objects.new("Kamera", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    gen = bpy.data.collections.new("GEN")
    sc.collection.children.link(gen)
    return sc


def gen_coll():
    return bpy.data.collections["GEN"]


def reset():
    for o in list(gen_coll().objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        if m.users == 0:
            bpy.data.meshes.remove(m)


_mats = {}


def mat(col, rough=0.85, metal=0.0, emit=0.0, alpha=1.0):
    key = (tuple(col), rough, metal, emit, alpha)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new("M%d" % len(_mats))
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = lin(col)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = lin(col)
        p.inputs["Emission Strength"].default_value = emit
    if alpha < 1:
        p.inputs["Alpha"].default_value = alpha
    _mats[key] = m
    return m


def noise_mat(c1, c2, scale=18.0, seed=0, rough=0.9, bump=0.25, detail=6.0, kind="noise", c3=None, ramp_pos=None):
    """Materiał proceduralny: szum/fale mapowane na rampę kolorów (+ wypukłość)."""
    key = ("n", c1, c2, c3, scale, seed, rough, bump, detail, kind, ramp_pos)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new("N%d" % len(_mats))
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (seed * 3.17, seed * 1.91, seed * 0.73)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    if kind == "wave":
        tx = nt.nodes.new("ShaderNodeTexWave")
        tx.inputs["Scale"].default_value = scale
        tx.inputs["Distortion"].default_value = 1.5
        out = tx.outputs["Fac"]
    else:
        tx = nt.nodes.new("ShaderNodeTexNoise")
        tx.inputs["Scale"].default_value = scale
        tx.inputs["Detail"].default_value = detail
        out = tx.outputs["Fac"]
    nt.links.new(mp.outputs["Vector"], tx.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    lo, hi = ramp_pos or (0.35, 0.65)
    els[0].position, els[1].position = lo, hi
    els[0].color, els[1].color = lin(c1), lin(c2)
    if c3:
        e = els.new((lo + hi) / 2)
        e.color = lin(c3)
        ramp.color_ramp.interpolation = "CONSTANT"
    nt.links.new(out, ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    if bump:
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        nt.links.new(out, bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    _mats[key] = m
    return m


def _fin(o, m, smooth=False):
    for c in o.users_collection:
        c.objects.unlink(o)
    gen_coll().objects.link(o)
    o.data.materials.clear()
    o.data.materials.append(m)
    if smooth:
        for poly in o.data.polygons:
            poly.use_smooth = True
    return o


def box(x, y, z, sx, sy, sz, m, rz=0.0, rx=0.0, ry=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z + sz / 2), rotation=(rx, ry, rz))
    o = bpy.context.active_object
    o.scale = (sx, sy, sz)
    return _fin(o, m)


def cyl(x, y, z, r, h, m, v=12, rot=(0, 0, 0), center=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=h,
                                        location=(x, y, z if center else z + h / 2), rotation=rot)
    return _fin(bpy.context.active_object, m)


def cone(x, y, z, r1, r2, h, m, v=12, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=v, radius1=r1, radius2=r2, depth=h, location=(x, y, z + h / 2), rotation=rot)
    return _fin(bpy.context.active_object, m)


def sph(x, y, z, r, m, sub=2, scale=(1, 1, 1), smooth=False):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=(x, y, z))
    o = bpy.context.active_object
    o.scale = scale
    return _fin(o, m, smooth)


def rod(a, b, r, m, v=8):
    """Walec między punktami a i b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=d.length, location=(a + b) / 2)
    o = bpy.context.active_object
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return _fin(o, m)


def mesh(verts, faces, m, name="P"):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    gen_coll().objects.link(o)
    o.data.materials.append(m)
    return o


def gable(x, y, z, w, d, h, m, over=0.04, axis="x"):
    """Dach dwuspadowy nad prostokątem w x d (kalenica wzdłuż osi)."""
    w2, d2 = w / 2 + over, d / 2 + over
    if axis == "x":
        v = [(x - w2, y - d2, z), (x + w2, y - d2, z), (x + w2, y + d2, z), (x - w2, y + d2, z),
             (x - w2, y, z + h), (x + w2, y, z + h)]
    else:
        v = [(x - w2, y - d2, z), (x + w2, y - d2, z), (x + w2, y + d2, z), (x - w2, y + d2, z),
             (x, y - d2, z + h), (x, y + d2, z + h)]
        v = [v[1], v[2], v[3], v[0], v[4], v[5]]
    f = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
    return mesh(v, f, m, "Dach")


def pyramid(x, y, z, w, h, m):
    return cone(x, y, z, w * 0.72, 0, h, m, v=4, rot=(0, 0, math.pi / 4))


ANIM = {"walk": None, "wave": 0, "mill": 0.0}   # parametry klatek animacji


def flag(x, y, z, h, c1, c2=None, size=0.22):
    """Flaga z dwóch segmentów; ANIM['wave'] wygina ją (klatki powiewania)."""
    cyl(x, y, z, 0.015, h, mat((80, 58, 34)), v=6)
    bend = (0.0, 0.35) if ANIM["wave"] == 0 else (0.3, -0.25)
    half = size / 2
    for j, c in enumerate([c1, c2] if c2 else [c1]):
        zz = z + h - size * 0.62 - j * size * 0.3
        a1, a2 = bend
        p0 = (x, y + 0.01)
        p1 = (p0[0] + math.sin(a1) * half, p0[1] + math.cos(a1) * half)
        box((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, zz, 0.012, half, size * 0.3, mat(c, 0.7), rz=-a1)
        p2 = (p1[0] + math.sin(a2) * half, p1[1] + math.cos(a2) * half)
        box((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, zz, 0.012, half, size * 0.3, mat(c, 0.7), rz=-a2)


def gold_cross(x, y, z, s=1.0):
    g = mat(GOLD, 0.3, 0.8)
    box(x, y, z, 0.025 * s, 0.025 * s, 0.16 * s, g)
    box(x, y, z + 0.09 * s, 0.025 * s, 0.1 * s, 0.025 * s, g)


def merlons(x0, y0, x1, y1, z, m, n=5, s=0.05):
    for i in range(n):
        t = i / (n - 1)
        box(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z, s, s, s * 0.9, m)


def stakes_ring(half, h, m, gap=None, spacing=0.07):
    pts = []
    k = int(2 * half / spacing)
    for i in range(k):
        t = -half + i * spacing
        pts += [(t, -half), (half, t), (-t, half), (-half, -t)]
    for (x, y) in pts:
        if gap and abs(x - gap[0]) < 0.09 and abs(y - gap[1]) < 0.09:
            continue
        hh = h * random.uniform(0.9, 1.05)
        cyl(x, y, 0, 0.032, hh, m, v=6)
        cone(x, y, hh, 0.032, 0, 0.06, m, v=6)


# ------------------------------------------------------------------ kamery i render
def cam_ortho(W, H, ax, ay, ppu, rot_deg):
    sc = bpy.context.scene
    co = sc.camera
    co.data.type = "ORTHO"
    rot = Euler([math.radians(a) for a in rot_deg])
    co.rotation_euler = rot
    co.location = rot.to_matrix() @ Vector((0, 0, 40))
    co.data.clip_end = 100
    mx = max(W, H)
    co.data.ortho_scale = mx / ppu
    co.data.shift_x = (W / 2 - ax) / mx
    co.data.shift_y = (ay - H / 2) / mx
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.resolution_percentage = 100


def render(name, W, H, ax, ay, ppu=PPU_ISO, rot=(60, 0, 45), transparent=True):
    if ONLY and not name.startswith(ONLY):
        return
    sc = bpy.context.scene
    cam_ortho(W, H, ax, ay, ppu, rot)
    sc.render.film_transparent = transparent
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("  ✓", name, flush=True)


# ------------------------------------------------------------------ teren
TERRAIN = {
    "grass": ((78, 132, 52), (110, 162, 70)),
    "forest": ((46, 90, 40), (74, 118, 52)),
    "hills": ((118, 112, 82), (150, 140, 100)),
    "water": ((40, 80, 140), (78, 128, 186)),
    "marsh": ((76, 104, 64), (104, 126, 76)),
    "field": ((150, 126, 66), (204, 178, 94)),
    "road": ((146, 122, 86), (182, 160, 114)),
}


def terrain_tile(kind, variant, frame):
    reset()
    c1, c2 = TERRAIN[kind]
    seed = variant * 7 + frame * 0.37
    if kind == "field":
        m = noise_mat((150, 120, 60), (214, 186, 96), scale=6, seed=variant, kind="wave", bump=0.4)
    elif kind == "water":
        m = noise_mat(c1, c2, scale=9, seed=seed, rough=0.12, bump=0.15, detail=3, ramp_pos=(0.45, 0.7))
    elif kind == "marsh":
        m = noise_mat(c1, (60, 100, 140), scale=7, seed=seed, bump=0.2, c3=c2, ramp_pos=(0.4, 0.62))
    else:
        m = noise_mat(c1, c2, scale=22 if kind != "road" else 14, seed=seed, bump=0.35)
    bpy.ops.mesh.primitive_plane_add(size=1.06, location=(0, 0, 0))
    o = _fin(bpy.context.active_object, m)
    if kind == "hills":
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=8)
        bpy.ops.object.mode_set(mode="OBJECT")
        r = random.Random(variant)
        cx, cy = r.uniform(-0.15, 0.15), r.uniform(-0.15, 0.15)
        for v in o.data.vertices:
            d = math.hypot(v.co.x - cx, v.co.y - cy)
            edge = min(0.53 - abs(v.co.x), 0.53 - abs(v.co.y)) * 4
            v.co.z = max(0, 0.09 * math.cos(min(d, 0.5) * math.pi)) * min(1, max(0, edge))
        for p in o.data.polygons:
            p.use_smooth = True
    render(f"tile_{kind}_{variant}_{frame}", 64, 32, 32, 16)


# ------------------------------------------------------------------ obiekty terenu
def tree(variant):
    reset()
    r = random.Random(variant * 13 + 1)
    trunk = mat((92, 62, 36))
    if variant % 3 == 0:
        cyl(0, 0, 0, 0.035, 0.25, trunk, v=6)
        greens = [(34, 84, 46), (44, 100, 54), (38, 92, 50)]
        z = 0.14
        for i, (rr, h) in enumerate([(0.27, 0.36), (0.21, 0.32), (0.14, 0.3)]):
            cone(0, 0, z, rr * r.uniform(0.9, 1.1), 0, h, mat(greens[i]), v=7)
            z += h * 0.6
    else:
        cyl(0, 0, 0, 0.04, 0.38, trunk, v=6)
        g = [(62, 120, 50), (52, 104, 44), (78, 140, 58)]
        for k in range(3):
            sph(r.uniform(-0.09, 0.09), r.uniform(-0.09, 0.09), 0.48 + r.uniform(0, 0.16),
                r.uniform(0.16, 0.22), mat(g[k]), sub=1)
    render(f"tree_{variant}", 32, 52, 16, 48)


def rocks(variant):
    reset()
    r = random.Random(variant * 31 + 5)
    for _ in range(3):
        c = r.choice([(120, 116, 108), (136, 132, 122), (104, 100, 94)])
        sph(r.uniform(-0.25, 0.25), r.uniform(-0.25, 0.25), 0.02, r.uniform(0.08, 0.15), mat(c, 0.95), sub=1,
            scale=(1, r.uniform(0.8, 1.3), r.uniform(0.6, 0.9)))
    render(f"rocks_{variant}", 48, 32, 24, 22)


def reeds(variant):
    reset()
    r = random.Random(variant + 99)
    g, b = mat((110, 130, 60)), mat((120, 80, 40))
    for _ in range(9):
        x, y, h = r.uniform(-0.25, 0.25), r.uniform(-0.25, 0.25), r.uniform(0.15, 0.3)
        cyl(x, y, 0, 0.008, h, g, v=4)
        cyl(x, y, h, 0.018, 0.05, b, v=5)
    render(f"reeds_{variant}", 32, 24, 16, 18)


# ------------------------------------------------------------------ budynki
def castle(big=False):
    st, st2 = mat(STONE, 0.9), mat((150, 146, 136), 0.9)
    roof = mat(RED_ROOF, 0.7)
    h = 0.3 if not big else 0.36
    hf = 0.42
    for (x, y, sx, sy) in [(0, -hf, 2 * hf, 0.07), (0, hf, 2 * hf, 0.07), (-hf, 0, 0.07, 2 * hf), (hf, 0, 0.07, 2 * hf)]:
        box(x, y, 0, sx, sy, h, st)
    for (x0, y0, x1, y1) in [(-hf, -hf, hf, -hf), (hf, -hf, hf, hf)]:
        merlons(x0, y0, x1, y1, h, st, n=7)
    box(hf + 0.01, 0, 0, 0.03, 0.14, 0.18, mat((50, 36, 26)))  # brama
    for (x, y) in [(-hf, -hf), (hf, -hf), (hf, hf), (-hf, hf)]:
        cyl(x, y, 0, 0.1, h + 0.22, st2, v=10)
        cone(x, y, h + 0.22, 0.12, 0, 0.22, roof, v=10)
    kh = 0.78 if not big else 0.9
    box(-0.04, 0.04, 0, 0.3, 0.3, kh, st2)
    merlons(-0.19, -0.11, 0.11, -0.11, kh, st2, n=4)
    merlons(0.11, -0.11, 0.11, 0.19, kh, st2, n=4)
    for z in (0.35, 0.55):
        box(0.115, 0.04, z, 0.01, 0.04, 0.07, mat((30, 24, 20)))
    flag(-0.04, 0.04, kh, 0.3, (235, 235, 235), (200, 30, 40))


def b_grod(epoch):
    reset()
    random.seed(1)
    if epoch <= 1:
        stakes_ring(0.44, 0.3, mat((126, 88, 50)), gap=(0.44, 0.0))
        box(0, 0.02, 0, 0.5, 0.32, 0.2, mat(WOOD))
        gable(0, 0.02, 0.2, 0.5, 0.32, 0.2, mat(THATCH, 0.95))
        box(0.251, 0.02, 0, 0.01, 0.08, 0.13, mat((50, 34, 20)))
        if epoch == 1:
            box(0.18, -0.24, 0, 0.14, 0.14, 0.52, mat(WHITE))
            pyramid(0.18, -0.24, 0.52, 0.17, 0.24, mat(RED_ROOF, 0.7))
            gold_cross(0.18, -0.24, 0.76, 0.8)
        flag(-0.25, 0.25, 0, 0.75, (235, 235, 235), (200, 30, 40))
    else:
        castle()
    render(f"building_grod_{min(epoch, 2)}" + ("_f1" if ANIM["wave"] else ""), 80, 112, 40, 96, ppu=PPU_BLD)


def b_simple(kind):
    reset()
    random.seed(kind)
    if kind == "pole":
        box(0, 0, 0, 0.92, 0.92, 0.025, noise_mat((150, 120, 60), (220, 190, 96), scale=5, seed=2, kind="wave", bump=0.5))
        wheat = mat((226, 200, 100))
        r = random.Random(4)
        for _ in range(40):
            x, y = r.uniform(-0.42, 0.42), r.uniform(-0.42, 0.42)
            cyl(x, y, 0.02, 0.012, r.uniform(0.06, 0.1), wheat, v=4)
        cone(0.28, 0.28, 0.02, 0.1, 0.0, 0.2, mat((212, 180, 80)), v=8)
        cone(0.12, 0.33, 0.02, 0.08, 0.0, 0.16, mat((200, 170, 76)), v=8)
    elif kind == "drwal":
        box(-0.12, 0.1, 0, 0.32, 0.26, 0.18, mat(WOOD))
        gable(-0.12, 0.1, 0.18, 0.32, 0.26, 0.14, mat(THATCH, 0.95))
        logm = mat((120, 80, 44))
        for i, (n, z) in enumerate([(3, 0.04), (2, 0.11), (1, 0.18)]):
            for j in range(n):
                y = -0.2 + j * 0.08 + i * 0.04
                cyl(0.2, y, z, 0.04, 0.36, logm, v=8, rot=(0, math.pi / 2, 0), center=True)
        cyl(-0.25, -0.25, 0, 0.06, 0.08, mat((110, 76, 42)), v=8)
        rod((-0.25, -0.25, 0.08), (-0.2, -0.2, 0.22), 0.012, mat((120, 90, 50)))
    elif kind == "kamieniolom":
        r = random.Random(7)
        for _ in range(7):
            s = r.uniform(0.1, 0.18)
            box(r.uniform(-0.3, 0.3), r.uniform(-0.3, 0.3), r.choice([0, 0, 0.08]), s, s * r.uniform(0.8, 1.3), s * 0.8,
                mat(r.choice([STONE, (150, 146, 136), (130, 126, 118)]), 0.95), rz=r.uniform(0, 1))
        w = mat((110, 80, 50))
        rod((-0.35, 0.3, 0), (-0.2, 0.15, 0.8), 0.022, w)
        rod((-0.2, 0.15, 0.8), (0.15, -0.05, 0.62), 0.016, w)
        rod((0.15, -0.05, 0.62), (0.15, -0.05, 0.3), 0.006, mat((60, 60, 60)))
        box(0.15, -0.05, 0.22, 0.09, 0.09, 0.08, mat(STONE))
    elif kind == "targ":
        aw = [((200, 50, 50), WHITE), ((60, 80, 170), (230, 200, 80)), ((60, 140, 70), WHITE)]
        for i, (x, y) in enumerate([(-0.2, 0.2), (0.2, 0.2), (0.0, -0.2)]):
            for (dx, dy) in [(-0.1, -0.08), (0.1, -0.08), (-0.1, 0.08), (0.1, 0.08)]:
                cyl(x + dx, y + dy, 0, 0.01, 0.24, mat(DWOOD), v=5)
            box(x, y, 0.08, 0.22, 0.16, 0.05, mat(WOOD))
            a, b = aw[i]
            for k in range(4):
                box(x - 0.09 + k * 0.06, y, 0.24, 0.06, 0.22, 0.015, mat(a if k % 2 == 0 else b, 0.8))
            for k in range(3):
                sph(x - 0.06 + k * 0.06, y, 0.15, 0.025, mat([(230, 80, 60), (240, 200, 60), (120, 200, 90)][k]), sub=1)
        cyl(0, 0, 0, 0.07, 0.08, mat(STONE), v=10)
        cyl(0, 0, 0.08, 0.055, 0.005, mat((50, 90, 150), 0.2), v=10)
    elif kind == "koszary":
        box(-0.05, 0.05, 0, 0.6, 0.3, 0.2, mat(DWOOD))
        gable(-0.05, 0.05, 0.2, 0.6, 0.3, 0.16, mat((120, 90, 60)))
        box(0.251, 0.05, 0, 0.01, 0.08, 0.13, mat((40, 30, 20)))
        for k in range(3):
            rod((0.15 + k * 0.08, -0.3, 0), (0.12 + k * 0.08, -0.25, 0.55), 0.01, mat((100, 70, 40)))
            cone(0.12 + k * 0.08, -0.25, 0.55, 0.015, 0, 0.05, mat(STEEL, 0.4, 0.8), v=4)
        flag(-0.33, -0.25, 0, 0.85, (200, 30, 40), (235, 235, 235))
    elif kind == "palisada":
        random.seed(5)
        stakes_ring(0.4, 0.32, mat((130, 92, 52)), gap=(0.4, 0.0))
        box(0.4, 0.0, 0, 0.14, 0.14, 0.5, mat(WOOD))
        pyramid(0.4, 0.0, 0.5, 0.18, 0.16, mat(THATCH, 0.95))
    elif kind == "kosciol":
        box(0.06, 0.06, 0, 0.5, 0.26, 0.3, mat(WHITE))
        gable(0.06, 0.06, 0.3, 0.5, 0.26, 0.2, mat(RED_ROOF, 0.7))
        for xx in (-0.05, 0.12):
            box(xx, -0.071, 0.12, 0.04, 0.01, 0.1, mat((60, 60, 90), 0.2))
        box(-0.25, 0.06, 0, 0.17, 0.17, 0.62, mat(WHITE))
        pyramid(-0.25, 0.06, 0.62, 0.2, 0.32, mat(RED_ROOF, 0.7))
        gold_cross(-0.25, 0.06, 0.94)
        box(0.312, 0.06, 0, 0.01, 0.08, 0.14, mat((80, 50, 30)))
    elif kind == "mlyn":
        box(-0.08, -0.05, 0, 0.36, 0.34, 0.28, mat(WOOD))
        pyramid(-0.08, -0.05, 0.28, 0.44, 0.24, mat(THATCH, 0.95))
        box(0.0, 0.3, 0, 0.9, 0.16, 0.02, mat((60, 110, 170), 0.15))
        cyl(0.02, 0.2, 0.22, 0.2, 0.05, mat((90, 64, 40)), v=16, rot=(math.pi / 2, 0, 0), center=True)
        for k in range(8):
            a = k * math.pi / 4 + ANIM["mill"]
            box(0.02 + math.cos(a) * 0.17, 0.2, 0.22 + math.sin(a) * 0.17 - 0.03, 0.06, 0.07, 0.06, mat((120, 86, 50)), ry=-a)
    elif kind == "zupa":
        w = mat((110, 76, 40))
        for (x, y) in [(-0.35, -0.1), (-0.05, -0.1), (-0.35, 0.15), (-0.05, 0.15)]:
            rod((x, y, 0), (-0.2, 0.02, 0.75), 0.018, w)
        cyl(-0.2, 0.02, 0.75, 0.09, 0.03, mat((80, 60, 40)), v=12, rot=(math.pi / 2, 0, 0), center=True)
        box(0.22, 0.15, 0, 0.26, 0.22, 0.16, mat(WOOD))
        gable(0.22, 0.15, 0.16, 0.26, 0.22, 0.12, mat(THATCH, 0.95))
        salt = mat((244, 244, 248), 0.5)
        for (x, y, s) in [(0.2, -0.22, 0.1), (0.05, -0.32, 0.08), (0.33, -0.1, 0.07)]:
            cone(x, y, 0, s, 0, s * 1.3, salt, v=8)
    elif kind == "zamek":
        castle(big=True)
    suffix = ""
    if kind == "mlyn" and ANIM["mill"]:
        suffix = "_f%d" % round(ANIM["mill"] / (math.pi / 16))
    elif ANIM["wave"]:
        suffix = "_f1"
    render(f"building_{kind}{suffix}", 80, 112, 40, 96, ppu=PPU_BLD)


def b_camp(fac):
    reset()
    if fac == "mg":
        for (x, y) in [(-0.2, 0.18), (0.18, 0.15), (0.0, -0.2)]:
            cyl(x, y, 0, 0.14, 0.13, mat((210, 190, 150)), v=12)
            sph(x, y, 0.13, 0.14, mat((196, 176, 136)), sub=2, scale=(1, 1, 0.6), smooth=True)
            box(x + 0.135, y, 0, 0.01, 0.06, 0.09, mat((60, 40, 30)))
        flag(0.3, -0.3, 0, 0.8, (60, 40, 30), (220, 220, 200))
    else:
        col = (232, 230, 222) if fac == "tz" else (140, 110, 80)
        for (x, y) in [(-0.2, 0.18), (0.18, 0.15), (0.0, -0.2)]:
            cone(x, y, 0, 0.16, 0, 0.3, mat(col), v=6)
        if fac == "tz":
            cyl(0.3, -0.3, 0, 0.015, 0.8, mat((80, 58, 34)), v=6)
            box(0.3, -0.18, 0.55, 0.012, 0.22, 0.2, mat((240, 240, 240)))
            box(0.3, -0.18, 0.55, 0.014, 0.04, 0.2, mat((20, 20, 20)))
            box(0.3, -0.18, 0.63, 0.014, 0.18, 0.04, mat((20, 20, 20)))
        else:
            flag(0.3, -0.3, 0, 0.8, (60, 60, 60), (160, 40, 40))
    for k in range(3):
        a = k * 2.1
        rod((0.25 + math.cos(a) * 0.05, -0.05 + math.sin(a) * 0.05, 0.0), (0.25, -0.05, 0.06), 0.012, mat((90, 60, 30)))
    sph(0.25, -0.05, 0.05, 0.035, mat((250, 150, 40), emit=6.0), sub=1)
    render(f"camp_{fac}" + ("_f1" if ANIM["wave"] else ""), 80, 112, 40, 96, ppu=PPU_BLD)


def b_landmark():
    reset()
    box(0, 0, 0, 0.12, 0.1, 0.42, mat((130, 126, 116), 0.95), rz=0.3)
    box(0.1, -0.1, 0, 0.08, 0.07, 0.22, mat((120, 116, 108), 0.95), rz=-0.2)
    sph(0, 0, 0.75, 0.08, mat(GOLD, 0.3, 0.6, emit=1.5), sub=0, scale=(1, 1, 1.5))
    render("landmark", 80, 112, 40, 96, ppu=PPU_BLD)


# ------------------------------------------------------------------ jednostki (widok 3/4, zwrot w prawo)
UNIT_ROT = (80, 0, 32)
UNIT_PPU = 64


def hat(fac, kind, z0):
    """Nakrycia głowy XV–XVIII w. zależne od frakcji i rodzaju oddziału."""
    z = z0 + 0.84
    steel = mat(STEEL, 0.35, 0.85)
    black = mat((30, 30, 32), 0.8)
    if kind == "hussar":
        sph(0, 0, z0 + 0.82, 0.12, steel, sub=2, scale=(1, 1, 0.75), smooth=True)
        box(-0.07, 0, z0 + 0.72, 0.06, 0.22, 0.1, steel)
        rod((0.1, 0, z0 + 0.86), (0.12, 0, z0 + 0.72), 0.008, steel)
        return
    if fac == "tz" or kind in ("knight", "knight_t", "knight_w"):
        cyl(0, 0, z0 + 0.72, 0.115, 0.17, steel, v=12)
        box(0.11, 0, z0 + 0.8, 0.012, 0.12, 0.018, mat((20, 20, 20)))
        return
    if kind == "scythe":
        cyl(0, 0, z - 0.02, 0.17, 0.015, black, v=16)
        cyl(0, 0, z - 0.02, 0.1, 0.07, black, v=12)
        for k, c in enumerate([(200, 40, 40), (60, 120, 200), (240, 200, 60)]):
            rod((0, 0.06 - k * 0.04, z + 0.04), (-0.12, 0.08 - k * 0.04, z + 0.16), 0.008, mat(c))
        return
    if fac == "mg":
        cyl(0, 0, z, 0.115, 0.07, mat((110, 80, 50)), v=10)
        cone(0, 0, z + 0.06, 0.08, 0.0, 0.08, mat((150, 100, 50)), v=8)
    elif fac == "ru":
        cyl(0, 0, z - 0.02, 0.1, 0.16, mat((170, 40, 40)), v=12)
        cyl(0, 0, z - 0.03, 0.115, 0.05, mat((90, 60, 40), 1.0), v=12)
    elif fac == "sv":
        cyl(0, 0, z - 0.02, 0.2, 0.015, black, v=18)
        cyl(0, 0, z - 0.02, 0.1, 0.11, black, v=12)
    elif fac == "tr":
        sph(0, 0, z + 0.02, 0.13, mat((240, 238, 228), 0.9), sub=2, scale=(1, 1, 0.75), smooth=True)
        cone(0, 0, z + 0.06, 0.05, 0.0, 0.08, mat((170, 40, 40)), v=8)
    elif fac in ("rs", "au"):
        cone(0, 0, z - 0.02, 0.19, 0.13, 0.07, black, v=3)
    elif fac == "en":
        cone(0, 0, z - 0.01, 0.11, 0.0, 0.15, steel, v=10)
    else:   # pl, lt, cz – kołpak z piórem
        cyl(0, 0, z - 0.02, 0.112, 0.08, mat((90, 62, 40), 1.0), v=12)
        cyl(0, 0, z + 0.05, 0.095, 0.04, mat(FACTION[fac]["tunic"]), v=12)
        rod((-0.02, 0.06, z + 0.04), (-0.12, 0.08, z + 0.22), 0.01, mat((245, 245, 240)))


def hussar_model():
    """Husarz: koń w czapraku, zbroja, skóra lamparta, skrzydła i kopia z proporcem."""
    leopard = noise_mat((205, 140, 60), (60, 40, 20), scale=30, seed=5, bump=0.1, c3=(205, 140, 60), ramp_pos=(0.55, 0.62))
    horse((80, 60, 50), (160, 30, 40))
    human("pl", "hussar", z0=0.42, legs=False, weapon=False)
    steel = mat(STEEL, 0.3, 0.85)
    box(0.05, 0, 0.42 + 0.36, 0.2, 0.28, 0.22, steel)
    sph(-0.08, 0, 0.42 + 0.55, 0.17, leopard, sub=2, scale=(0.6, 1.2, 1.3), smooth=True)
    white = mat((248, 248, 245), 0.6)
    for y in (-0.07, 0.07):
        prev = None
        for t in range(9):
            a = t / 8
            x = -0.14 - 0.12 * math.sin(a * 1.6)
            z = 0.42 + 0.55 + a * 0.75
            if prev:
                rod(prev, (x, y, z), 0.012, mat((120, 90, 50)))
            box(x - 0.03, y, z, 0.07, 0.012, 0.035, white, ry=-0.4)
            prev = (x, y, z)
    rod((-0.3, 0.2, 0.85), (1.15, 0.2, 1.2), 0.02, mat((200, 170, 120)))
    box(0.95, 0.2, 1.16, 0.18, 0.01, 0.05, mat((235, 235, 235)))
    box(0.95, 0.2, 1.11, 0.18, 0.01, 0.05, mat((200, 30, 40)))


def human(fac, kind, z0=0.0, legs=True, weapon=True):
    t = FACTION[fac]
    tun = mat(t["tunic"] if kind != "scythe" else (226, 220, 204))
    if legs:
        ph = ANIM["walk"]
        for j, y in enumerate((-0.06, 0.06)):
            sw = 0.0 if ph is None else math.sin(ph * math.pi / 2 + j * math.pi) * 0.12
            rod((0, y, z0 + 0.32), (sw, y, z0 + 0.0), 0.05, mat((70, 56, 44)), v=8)
    cone(0, 0, z0 + 0.3, 0.15, 0.12, 0.36, tun, v=10)
    box(0, 0, z0 + 0.34, 0.27, 0.27, 0.035, mat(t["trim"]))
    if fac in ("tz", "kz"):
        e = mat(t["emb"])
        box(0.14, 0, z0 + 0.42, 0.01, 0.04, 0.18, e)
        box(0.14, 0, z0 + 0.5, 0.01, 0.13, 0.04, e)
    for y in (-0.17, 0.17):
        rod((0, y, z0 + 0.64), (0.06, y * 1.05, z0 + 0.38), 0.04, tun)
        sph(0.06, y * 1.05, z0 + 0.37, 0.04, mat(SKIN), sub=1)
    head = mat(SKIN, 0.7)
    sph(0, 0, z0 + 0.79, 0.1, head, sub=2, smooth=True)
    sph(0.085, -0.035, z0 + 0.81, 0.012, mat((30, 20, 20)), sub=1)
    sph(0.085, 0.035, z0 + 0.81, 0.012, mat((30, 20, 20)), sub=1)
    steel = mat(STEEL, 0.35, 0.85)
    hat(fac, kind, z0)
    if not weapon:
        return
    wood = mat((120, 90, 50))
    if kind in ("spear", "sword", "xbow") or kind.startswith("knight") or kind in ("horse_lt",):
        sh = cyl(0.13, -0.19, z0 + 0.48, 0.15, 0.03, mat(t["shield"], 0.6), v=14, rot=(0, math.pi / 2, 0), center=True)
        cyl(0.15, -0.19, z0 + 0.48, 0.06, 0.02, mat(t["emb"], 0.6), v=10, rot=(0, math.pi / 2, 0), center=True)
    if kind == "spear":
        rod((0.08, 0.19, z0 + 0.0), (0.08, 0.19, z0 + 1.28), 0.016, wood)
        cone(0.08, 0.19, z0 + 1.28, 0.03, 0, 0.09, steel, v=4)
    elif kind == "pike":
        rod((-0.15, 0.19, z0 + 0.1), (0.4, 0.19, z0 + 1.6), 0.016, wood)
        cone(0.4, 0.19, z0 + 1.6, 0.03, 0, 0.09, steel, v=4, rot=(0, 0.35, 0))
    elif kind == "sword":
        rod((0.08, 0.19, z0 + 0.38), (0.26, 0.19, z0 + 0.82), 0.018, steel)
        box(0.09, 0.19, z0 + 0.38, 0.03, 0.1, 0.02, mat((140, 100, 40)))
    elif kind == "bow":
        bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.014, location=(0.16, 0.12, z0 + 0.55),
                                         rotation=(math.pi / 2, 0, 0))
        o = _fin(bpy.context.active_object, mat((120, 80, 40)))
        o.scale = (0.28, 1, 1)
        box(-0.15, 0.0, z0 + 0.4, 0.07, 0.07, 0.3, mat((110, 74, 40)))
    elif kind == "xbow":
        box(0.2, 0.19, z0 + 0.46, 0.4, 0.04, 0.04, wood)
        box(0.36, 0.19, z0 + 0.46, 0.03, 0.34, 0.02, mat((80, 60, 40)))
    elif kind == "musket":
        rod((0.12, 0.18, z0 + 0.45), (-0.22, 0.18, z0 + 1.1), 0.02, mat((40, 40, 44), 0.4, 0.8))
        rod((0.18, 0.18, z0 + 0.36), (0.08, 0.18, z0 + 0.55), 0.035, wood)
        box(-0.05, -0.15, z0 + 0.36, 0.06, 0.04, 0.08, mat((110, 80, 40)))
    elif kind == "scythe":
        rod((0.1, 0.19, z0 + 0.0), (0.1, 0.19, z0 + 1.1), 0.017, wood)
        box(0.1, 0.19, z0 + 1.08, 0.05, 0.01, 0.42, mat((200, 205, 215), 0.3, 0.9), ry=0.05)


def horse(col, cloth=None, cross=None):
    hm = mat(col, 0.8)
    sph(0, 0, 0.58, 0.2, hm, sub=2, scale=(2.3, 0.95, 1.0), smooth=True)
    rod((0.36, 0, 0.62), (0.55, 0, 0.92), 0.08, hm)
    box(0.62, 0, 0.84, 0.22, 0.1, 0.1, hm, ry=0.5)
    ph = ANIM["walk"]
    for j, (x, y) in enumerate([(0.3, -0.09), (0.3, 0.09), (-0.3, -0.09), (-0.3, 0.09)]):
        sw = 0.0 if ph is None else math.sin(ph * math.pi / 2 + (j in (1, 2)) * math.pi) * 0.14
        rod((x, y, 0.46), (x + sw, y, 0.0), 0.04, mat(tuple(int(c * 0.75) for c in col)), v=8)
    rod((-0.44, 0, 0.66), (-0.56, 0, 0.36), 0.045, mat((60, 40, 30)))
    sph(0.66, 0.05, 0.92, 0.015, mat((10, 10, 10)), sub=1)
    if cloth:
        sph(0, 0, 0.52, 0.205, mat(cloth, 0.8), sub=2, scale=(2.35, 1.0, 0.9), smooth=True)
        if cross:
            box(0.0, -0.205, 0.45, 0.06, 0.012, 0.22, mat(cross))
            box(0.0, -0.205, 0.53, 0.2, 0.012, 0.06, mat(cross))


def unit(kind, fac, walk=None):
    reset()
    ANIM["walk"] = walk
    if kind == "hussar":
        hussar_model()
    elif kind in ("spear", "sword", "pike", "bow", "xbow", "musket", "scythe"):
        human(fac, kind)
    elif kind in ("horse", "horse_lt", "horse_mg", "knight", "knight_t", "knight_w"):
        col = {"horse": (110, 76, 46), "horse_lt": (70, 50, 40), "horse_mg": (150, 120, 80)}.get(kind, (90, 70, 60))
        cloth = {"knight": (190, 40, 44), "knight_t": (238, 238, 232), "knight_w": (235, 235, 230)}.get(kind)
        cross = {"knight_t": (20, 20, 20), "knight_w": (190, 30, 30)}.get(kind)
        horse(col, cloth, cross)
        human("mg" if kind == "horse_mg" else ("lt" if kind == "horse_lt" else fac), kind, z0=0.42, legs=False,
              weapon=kind == "horse_mg")
        if kind != "horse_mg":
            rod((-0.3, 0.2, 0.85), (1.0, 0.2, 1.15), 0.018, mat((130, 100, 60)))
            cone(1.0, 0.2, 1.15, 0.03, 0, 0.1, mat(STEEL, 0.4, 0.8), v=4, rot=(0, math.radians(77), 0))
            t = FACTION["lt" if kind == "horse_lt" else fac]
            if kind != "horse":
                cyl(0.13, -0.19, 0.9, 0.14, 0.03, mat(t["shield"], 0.6), v=14, rot=(0, math.pi / 2, 0), center=True)
                cyl(0.15, -0.19, 0.9, 0.055, 0.02, mat(t["emb"], 0.6), v=10, rot=(0, math.pi / 2, 0), center=True)
        else:
            bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.014, location=(0.2, 0.12, 0.95),
                                             rotation=(math.pi / 2, 0, 0))
            o = _fin(bpy.context.active_object, mat((120, 80, 40)))
            o.scale = (0.28, 1, 1)
    elif kind == "cannon":
        w = mat((120, 84, 50))
        box(0, 0, 0.12, 0.7, 0.24, 0.08, w)
        for y in (-0.16, 0.16):
            cyl(-0.12, y, 0.14, 0.14, 0.04, mat((80, 60, 40)), v=12, rot=(math.pi / 2, 0, 0), center=True)
        rod((-0.2, 0, 0.3), (0.5, 0, 0.46), 0.09, mat((70, 72, 78), 0.4, 0.8), v=12)
        cyl(0.5, 0, 0.46, 0.06, 0.02, mat((20, 20, 20)), v=12, rot=(0, math.radians(77), 0), center=True)
    elif kind == "wagon":
        box(0, 0, 0.2, 0.8, 0.36, 0.16, mat((130, 92, 52)))
        for x in (-0.25, 0.25):
            for y in (-0.2, 0.2):
                cyl(x, y, 0.13, 0.13, 0.03, mat((70, 50, 30)), v=12, rot=(math.pi / 2, 0, 0), center=True)
        cyl(0, 0, 0.36, 0.18, 0.78, mat((226, 220, 200)), v=16, rot=(0, math.pi / 2, 0), center=True)
    elif kind == "smoke":
        r = random.Random(3)
        for _ in range(7):
            sph(r.uniform(-0.3, 0.3), r.uniform(-0.2, 0.2), r.uniform(0.2, 0.6), r.uniform(0.14, 0.24),
                mat((190, 190, 180), 1.0, alpha=0.75), sub=2, smooth=True)
    suffix = "" if walk is None else f"_w{walk}"
    render(f"unit_{kind}_{fac}{suffix}", 96, 88, 40, 82, ppu=UNIT_PPU, rot=UNIT_ROT)
    ANIM["walk"] = None


# ------------------------------------------------------------------ ARCHITEKTURA EPOK (część II)
EP = {   # ściany, dach, detale, akcent
    0: {"wall": (234, 226, 206), "roof": (172, 66, 48), "det": (205, 192, 168), "acc": (190, 160, 70)},   # renesans
    1: {"wall": (232, 206, 160), "roof": (170, 70, 50), "det": (200, 170, 130), "acc": (150, 60, 50)},    # manieryzm, Zamość
    2: {"wall": (226, 186, 120), "roof": (80, 104, 96), "det": (240, 232, 214), "acc": (90, 150, 128)},   # barok, miedziane hełmy
    3: {"wall": (238, 228, 186), "roof": (118, 120, 128), "det": (248, 246, 238), "acc": (210, 200, 160)},  # klasycyzm
}


def hip(x, y, z, w, d, h, m, over=0.03):
    """Dach czterospadowy nad prostokątem w x d."""
    w2, d2 = w / 2 + over, d / 2 + over
    if w >= d:
        r = w2 - d2 * 0.9
        v = [(x - w2, y - d2, z), (x + w2, y - d2, z), (x + w2, y + d2, z), (x - w2, y + d2, z), (x - r, y, z + h), (x + r, y, z + h)]
        f = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
    else:
        r = d2 - w2 * 0.9
        v = [(x - w2, y - d2, z), (x + w2, y - d2, z), (x + w2, y + d2, z), (x - w2, y + d2, z), (x, y - r, z + h), (x, y + r, z + h)]
        f = [(0, 1, 4), (2, 3, 5), (1, 2, 5, 4), (3, 0, 4, 5), (0, 3, 2, 1)]
    return mesh(v, f, m, "Dach4")


def windows(x, y, z, w, d, h, floors=2, per=3, col=(60, 70, 90)):
    """Okna na dwóch widocznych ścianach (+x i -y)."""
    m = mat(col, 0.2)
    for fl in range(floors):
        zz = z + h * (fl + 0.35) / floors
        for k in range(per):
            t = (k + 0.5) / per
            box(x - w / 2 + w * t, y - d / 2 - 0.004, zz, w / per * 0.35, 0.01, h / floors * 0.38, m)
            box(x + w / 2 + 0.004, y - d / 2 + d * t, zz, 0.01, d / per * 0.35, h / floors * 0.38, m)


def attic(x, y, z, w, d, m, n=6):
    """Polska attyka renesansowa: grzebień ze sterczynkami nad gzymsem."""
    for (x0, y0, x1, y1) in [(-w / 2, -d / 2, w / 2, -d / 2), (w / 2, -d / 2, w / 2, d / 2)]:
        box(x + (x0 + x1) / 2, y + (y0 + y1) / 2, z, abs(x1 - x0) + 0.02, abs(y1 - y0) + 0.02, 0.06, m)
        for k in range(n):
            t = k / (n - 1)
            px, py = x + x0 + (x1 - x0) * t, y + y0 + (y1 - y0) * t
            cone(px, py, z + 0.06, 0.018, 0.0, 0.06, m, v=4)


def helmet(x, y, z, r, m):
    """Barokowy hełm wieży: cebula + latarnia + iglica."""
    sph(x, y, z + r * 0.6, r, m, sub=2, scale=(1, 1, 0.8), smooth=True)
    cyl(x, y, z + r * 1.3, r * 0.35, r * 0.6, m, v=10)
    sph(x, y, z + r * 2.0, r * 0.45, m, sub=2, smooth=True)
    cone(x, y, z + r * 2.3, r * 0.12, 0, r * 1.2, mat(GOLD, 0.3, 0.8), v=6)


def dome(x, y, z, r, m, lantern=True):
    sph(x, y, z, r, m, sub=3, scale=(1, 1, 0.85), smooth=True)
    if lantern:
        cyl(x, y, z + r * 0.8, r * 0.25, r * 0.4, mat((240, 236, 226)), v=10)
        sph(x, y, z + r * 1.25, r * 0.28, m, sub=2, smooth=True)


def portico(x, y, z, w, h, cols=4, face="y"):
    """Klasycystyczny portyk: kolumny i trójkątny fronton na ścianie -y."""
    white = mat((248, 246, 238), 0.6)
    for k in range(cols):
        cx = x - w / 2 + w * (k + 0.5) / cols
        cyl(cx, y - 0.06, z, 0.025, h, white, v=10)
    box(x, y - 0.06, z + h, w + 0.04, 0.12, 0.04, white)
    mesh([(x - w / 2 - 0.02, y - 0.12, z + h + 0.04), (x + w / 2 + 0.02, y - 0.12, z + h + 0.04), (x, y - 0.12, z + h + 0.16),
          (x - w / 2 - 0.02, y, z + h + 0.04), (x + w / 2 + 0.02, y, z + h + 0.04), (x, y, z + h + 0.16)],
         [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], white, "Fronton")


def styled_block(x, y, w, d, h, ep, floors=2, wall=None, roof="hip"):
    e = EP[ep]
    box(x, y, 0, w, d, h, mat(wall or e["wall"]))
    windows(x, y, 0, w, d, h, floors, max(2, int(w / 0.12)))
    box(x, y, h, w + 0.03, d + 0.03, 0.025, mat(e["det"]))
    if ep == 0:
        attic(x, y, h + 0.025, w, d, mat(e["wall"]))
        hip(x, y, h + 0.025, w * 0.9, d * 0.9, 0.12, mat(e["roof"], 0.7))
    elif ep == 1:
        attic(x, y, h + 0.025, w, d, mat(e["det"]), n=5)
        hip(x, y, h + 0.025, w, d, 0.16, mat(e["roof"], 0.7))
    elif ep == 2:   # dach mansardowy
        hip(x, y, h + 0.025, w + 0.04, d + 0.04, 0.09, mat(e["roof"], 0.6), over=0.0)
        hip(x, y, h + 0.115, w * 0.7, d * 0.7, 0.08, mat(e["roof"], 0.6), over=0.0)
    else:
        hip(x, y, h + 0.025, w, d, 0.07, mat(e["roof"], 0.6))
        for k in range(int(w / 0.08)):   # balustrada
            cyl(x - w / 2 + 0.04 + k * 0.08, y - d / 2, h + 0.025, 0.008, 0.05, mat(e["det"]), v=6)


def b_grod2(ep):
    """Siedziba władcy w czterech stylach: zamek renesansowy, ratusz z wieżą, pałac barokowy, pałac klasycystyczny."""
    reset()
    random.seed(ep)
    e = EP[ep]
    if ep == 0:     # zamek renesansowy z krużgankami (jak Wawel)
        for (x, y, w, d) in [(-0.05, 0.25, 0.7, 0.22), (0.25, -0.05, 0.22, 0.5), (-0.33, -0.05, 0.14, 0.5)]:
            styled_block(x, y, w, d, 0.32, 0, floors=2)
        for k in range(5):   # arkady krużganków od dziedzińca
            box(-0.25 + k * 0.1, 0.14 - 0.002, 0.03, 0.05, 0.01, 0.12, mat((70, 60, 55)))
        box(0.27, -0.33, 0, 0.17, 0.17, 0.55, mat(e["wall"]))
        attic(0.27, -0.33, 0.55, 0.17, 0.17, mat(e["wall"]), n=4)
        dome(0.27, -0.33, 0.6, 0.08, mat(GOLD, 0.3, 0.8))
        flag(-0.33, 0.2, 0.32, 0.4, (235, 235, 235), (200, 30, 40))
    elif ep == 1:   # ratusz z wieżą (jak w Zamościu)
        styled_block(0, 0.05, 0.6, 0.36, 0.34, 1, floors=2, wall=(236, 196, 150))
        box(0, -0.12, 0, 0.14, 0.14, 0.9, mat((236, 196, 150)))
        windows(0, -0.12, 0.34, 0.14, 0.14, 0.5, 2, 1)
        attic(0, -0.12, 0.9, 0.14, 0.14, mat(e["det"]), n=3)
        cone(0, -0.12, 0.96, 0.1, 0.0, 0.32, mat(e["roof"], 0.6), v=8)
        for k in range(4):   # wachlarzowe schody
            box(0, -0.26 - k * 0.04, 0, 0.3 - k * 0.04, 0.05, 0.12 - k * 0.03, mat((200, 190, 175)))
        flag(0, -0.12, 1.25, 0.18, (235, 235, 235), (200, 30, 40), size=0.16)
    elif ep == 2:   # pałac barokowy (jak Wilanów)
        styled_block(0.02, 0.12, 0.62, 0.24, 0.3, 2, floors=2)
        for x in (-0.24, 0.28):
            styled_block(x, -0.18, 0.14, 0.38, 0.26, 2, floors=2)
            box(x, -0.36, 0, 0.16, 0.16, 0.42, mat(e["wall"]))
            helmet(x, -0.36, 0.42, 0.09, mat(e["acc"], 0.5, 0.3))
        box(0.02, -0.01, 0, 0.18, 0.04, 0.34, mat(e["det"]))
        flag(0.02, 0.12, 0.42, 0.35, (235, 235, 235), (200, 30, 40))
    else:           # pałac klasycystyczny (jak Łazienki) nad stawem
        box(0.0, -0.33, 0, 0.9, 0.24, 0.015, mat((70, 120, 170), 0.1))
        styled_block(0, 0.05, 0.56, 0.34, 0.32, 3, floors=2)
        portico(0, -0.12, 0, 0.32, 0.3, cols=6)
        for k in range(5):
            cyl(-0.22 + k * 0.11, -0.12, 0.42, 0.018, 0.08, mat((240, 238, 230)), v=8)
        flag(0, 0.12, 0.4, 0.35, (235, 235, 235), (200, 30, 40))
    suffix = "_f1" if ANIM["wave"] else ""
    render(f"building_grod_{ep}{suffix}", 80, 112, 40, 96, ppu=PPU_BLD)


def b_epoch(kind, ep):
    """Budynki zależne od epoki."""
    reset()
    random.seed(kind + str(ep))
    e = EP[ep]
    if kind == "pole":      # folwark: dwór z gankiem, stodoła, pola
        box(0, 0, 0, 0.9, 0.9, 0.02, noise_mat((150, 120, 60), (220, 190, 96), scale=5, seed=2, kind="wave", bump=0.5))
        dworek_wall = (240, 236, 226) if ep < 3 else (238, 228, 186)
        box(-0.15, 0.12, 0.02, 0.4, 0.24, 0.16, mat(dworek_wall))
        windows(-0.15, 0.12, 0.02, 0.4, 0.24, 0.16, 1, 4)
        roofc = (90, 70, 55) if ep < 2 else ((80, 104, 96) if ep == 2 else (118, 120, 128))
        hip(-0.15, 0.12, 0.18, 0.4, 0.24, 0.17, mat(roofc, 0.8), over=0.04)
        portico(-0.15, 0.0, 0.02, 0.12, 0.13, cols=2)
        box(0.25, 0.25, 0.02, 0.26, 0.18, 0.15, mat(WOOD))
        gable(0.25, 0.25, 0.17, 0.26, 0.18, 0.12, mat(THATCH, 0.95))
        for _ in range(3):
            cone(random.uniform(0.1, 0.38), random.uniform(-0.38, -0.1), 0.02, 0.07, 0, 0.16, mat((212, 180, 80)), v=8)
    elif kind == "targ":    # kamienice z rynkiem
        pastel = [(232, 200, 150), (200, 220, 200), (230, 190, 190), (220, 210, 160)]
        for k in range(3):
            x = -0.26 + k * 0.17
            col = pastel[(k + ep) % 4] if ep in (1, 2) else e["wall"]
            box(x, 0.12, 0, 0.16, 0.32, 0.42, mat(col))
            windows(x, 0.12, 0, 0.16, 0.32, 0.42, 3, 2)
            if ep == 0:
                attic(x, 0.12, 0.42, 0.16, 0.32, mat(col), n=3)
                gable(x, 0.12, 0.42, 0.14, 0.3, 0.1, mat(e["roof"], 0.7), axis="y")
            elif ep == 1:
                for a in range(2):
                    box(x - 0.04 + a * 0.08, -0.04 - 0.002, 0, 0.05, 0.01, 0.12, mat((70, 60, 55)))
                attic(x, 0.12, 0.42, 0.16, 0.32, mat(e["det"]), n=3)
                gable(x, 0.12, 0.42, 0.14, 0.3, 0.12, mat(e["roof"], 0.7), axis="y")
            elif ep == 2:
                box(x, -0.04, 0.42, 0.1, 0.02, 0.12, mat(col))
                sph(x, -0.04, 0.56, 0.035, mat(e["det"]), sub=1)
                hip(x, 0.12, 0.42, 0.16, 0.32, 0.1, mat(e["roof"], 0.6))
            else:
                portico(x, -0.04, 0.27, 0.12, 0.12, cols=2)
                hip(x, 0.12, 0.42, 0.16, 0.32, 0.06, mat(e["roof"], 0.6))
        box(0.27, -0.1, 0, 0.12, 0.22, 0.12, mat(WOOD))
        for k in range(3):
            sph(0.27 - 0.04 + k * 0.04, -0.22, 0.14, 0.025, mat([(230, 80, 60), (240, 200, 60), (120, 200, 90)][k]), sub=1)
    elif kind == "koszary":
        styled_block(-0.02, 0.08, 0.7, 0.26, 0.3, ep, floors=2)
        box(-0.02, -0.06, 0, 0.1, 0.02, 0.14, mat((60, 45, 35)))
        if ep >= 2:
            portico(-0.02, -0.05, 0, 0.24, 0.26, cols=4)
        for k in range(3):
            cyl(0.2 + k * 0.06, -0.3, 0, 0.012, 0.36, mat((100, 70, 40)), v=6)
        flag(-0.32, -0.28, 0, 0.8, (200, 30, 40), (235, 235, 235))
    elif kind == "kosciol":  # kolegium i drukarnia
        if ep == 0:   # kaplica ze złotą kopułą (jak Kaplica Zygmuntowska)
            styled_block(0.15, 0.12, 0.34, 0.3, 0.26, 0, floors=1)
            box(-0.18, 0.0, 0, 0.26, 0.26, 0.34, mat(e["wall"]))
            windows(-0.18, 0.0, 0, 0.26, 0.26, 0.34, 1, 2)
            cyl(-0.18, 0.0, 0.34, 0.11, 0.08, mat(e["wall"]), v=16)
            dome(-0.18, 0.0, 0.42, 0.12, mat(GOLD, 0.25, 0.85))
        elif ep == 1:
            styled_block(0.12, 0.1, 0.4, 0.3, 0.3, 1, floors=1)
            box(-0.2, -0.05, 0, 0.16, 0.16, 0.7, mat(e["wall"]))
            attic(-0.2, -0.05, 0.7, 0.16, 0.16, mat(e["det"]), n=3)
            cone(-0.2, -0.05, 0.76, 0.09, 0, 0.35, mat(e["roof"], 0.6), v=8)
        elif ep == 2:  # barokowa fasada z dwiema wieżami
            box(0.08, 0.15, 0, 0.36, 0.42, 0.34, mat(e["wall"]))
            gable(0.08, 0.15, 0.34, 0.36, 0.42, 0.18, mat(e["roof"], 0.6), axis="y")
            for x in (-0.07, 0.23):
                box(x, -0.08, 0, 0.12, 0.12, 0.56, mat(e["wall"]))
                helmet(x, -0.08, 0.56, 0.07, mat(e["acc"], 0.5, 0.3))
            box(0.08, -0.08, 0.3, 0.18, 0.03, 0.12, mat(e["det"]))
            sph(0.08, -0.08, 0.44, 0.04, mat(e["det"]), sub=1)
        else:          # klasycystyczny kościół z portykiem i kopułą
            box(0, 0.1, 0, 0.44, 0.44, 0.34, mat(e["wall"]))
            portico(0, -0.12, 0, 0.3, 0.3, cols=4)
            cyl(0, 0.1, 0.34, 0.15, 0.1, mat(e["wall"]), v=20)
            dome(0, 0.1, 0.44, 0.16, mat((110, 130, 128), 0.5, 0.3))
        gold_cross(-0.18 if ep == 0 else 0, 0.0, 0.62 if ep == 0 else 0.0, 0.6) if ep == 0 else None
    elif kind == "zamek":   # twierdza bastionowa
        brick = mat((170, 90, 60), 0.9) if ep < 2 else noise_mat((80, 120, 60), (110, 150, 80), scale=10, seed=4)
        pts = []
        for k in range(10):
            a = k * math.tau / 10 + math.pi / 10
            r = 0.48 if k % 2 == 0 else 0.3
            pts.append((math.cos(a) * r, math.sin(a) * r))
        v = [(x, y, 0) for x, y in pts] + [(x * 0.88, y * 0.88, 0.16) for x, y in pts]
        n = len(pts)
        f = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)] + [tuple(range(n, 2 * n))]
        mesh(v, f, brick, "Bastiony")
        box(0, 0, 0.16, 0.6, 0.6, 0.004, mat((150, 130, 100)))
        styled_block(0.02, 0.05, 0.3, 0.2, 0.22, ep, floors=1)
        for k in range(5):
            a = k * math.tau / 5 + math.pi / 10
            x, y = math.cos(a) * 0.4, math.sin(a) * 0.4
            rod((x, y, 0.2), (x * 1.18, y * 1.18, 0.22), 0.025, mat((40, 40, 44), 0.3, 0.8))
        flag(0.02, 0.05, 0.22, 0.4, (235, 235, 235), (200, 30, 40))
    elif kind == "palisada":    # szańce z działami
        earth = noise_mat((100, 120, 60), (130, 110, 70), scale=12, seed=6)
        for (x, y, w, d) in [(0, -0.36, 0.8, 0.14), (0.36, 0, 0.14, 0.8), (0, 0.36, 0.8, 0.14), (-0.36, 0, 0.14, 0.8)]:
            box(x, y, 0, w, d, 0.14, earth)
        for k in range(6):
            a = k * math.tau / 6
            cyl(math.cos(a) * 0.36, math.sin(a) * 0.36, 0.14, 0.04, 0.08, mat((130, 100, 60)), v=8)
        for (x, y, rz) in [(0.1, -0.43, -math.pi / 2), (0.43, 0.08, 0)]:
            rod((x, y, 0.18), (x + math.cos(rz) * 0.18, y + math.sin(rz) * 0.18, 0.2), 0.035, mat((50, 50, 54), 0.3, 0.8))
        flag(-0.3, -0.3, 0.14, 0.5, (235, 235, 235), (200, 30, 40), size=0.16)
    elif kind == "zupa":    # żupa i huta: szyb, piec z kominem, hałda
        w = mat((110, 76, 40))
        for (x, y) in [(-0.35, -0.1), (-0.05, -0.1), (-0.35, 0.15), (-0.05, 0.15)]:
            rod((x, y, 0), (-0.2, 0.02, 0.75), 0.018, w)
        cyl(-0.2, 0.02, 0.75, 0.09, 0.03, mat((80, 60, 40)), v=12, rot=(math.pi / 2, 0, 0), center=True)
        box(0.2, 0.15, 0, 0.3, 0.24, 0.2, mat((170, 100, 70)))
        cyl(0.3, 0.2, 0, 0.05, 0.75, mat((150, 80, 60)), v=8)
        sph(0.3, 0.2, 0.82, 0.06, mat((180, 180, 175), 1.0, alpha=0.7), sub=2)
        salt = mat((244, 244, 248), 0.5)
        for (x, y, s_) in [(0.2, -0.22, 0.1), (0.05, -0.32, 0.08)]:
            cone(x, y, 0, s_, 0, s_ * 1.3, salt, v=8)
    suffix = "_f1" if ANIM["wave"] and kind in ("koszary", "zamek") else ""
    render(f"building_{kind}_e{ep}{suffix}", 80, 112, 40, 96, ppu=PPU_BLD)


def b_camp2(fac):
    """Obozy wrogów części II: Szwedzi, Moskwa, Rosja XVIII w."""
    reset()
    col, fc1, fc2 = {"sv": ((70, 100, 170), (60, 90, 170), (240, 200, 60)),
                     "ru": ((90, 130, 90), (170, 40, 40), (230, 200, 80)),
                     "rs": ((236, 234, 226), (240, 240, 240), (60, 90, 170))}[fac]
    for (x, y) in [(-0.2, 0.18), (0.18, 0.15), (0.0, -0.2)]:
        cone(x, y, 0, 0.16, 0, 0.3, mat(col), v=6)
    flag(0.3, -0.3, 0, 0.8, fc1, fc2)
    rod((0.25, -0.05, 0.0), (0.25, -0.05, 0.06), 0.012, mat((90, 60, 30)))
    sph(0.25, -0.05, 0.05, 0.035, mat((250, 150, 40), emit=6.0), sub=1)
    render(f"camp_{fac}" + ("_f1" if ANIM["wave"] else ""), 80, 112, 40, 96, ppu=PPU_BLD)


# ------------------------------------------------------------------ klatki animacji
WALKERS = [("spear", "pl"), ("bow", "pl"), ("horse", "pl"), ("spear", "en"), ("horse_mg", "mg"), ("knight_t", "tz"),
           ("knight", "en"), ("pike", "en")]


def animations():
    for kind, fac in WALKERS:
        for ph in range(4):
            unit(kind, fac, ph)
    for k in (1, 2, 3):                       # koło młyna: 4 klatki (0 = statyczny render)
        ANIM["mill"] = k * math.pi / 16
        b_simple("mlyn")
    ANIM["mill"] = 0.0
    ANIM["wave"] = 1                          # druga klatka powiewających flag
    for e in range(3):
        b_grod(e)
    for k in ("koszary", "zamek"):
        b_simple(k)
    for f in ("en", "mg", "tz"):
        b_camp(f)
    ANIM["wave"] = 0


# ------------------------------------------------------------------ Damian Ściseł
def hero():
    reset()
    robe, robe_d = mat((112, 52, 156), 0.85), mat((82, 36, 118), 0.85)
    cone(0, 0, 0, 0.34, 0.18, 0.95, robe, v=16)
    rod((0, -0.17, 0.05), (0, -0.115, 0.9), 0.012, mat(GOLD, 0.4, 0.6))
    cyl(0, 0, 0.48, 0.262, 0.045, mat((90, 60, 30)), v=16)
    box(0.16, -0.21, 0.36, 0.12, 0.06, 0.12, mat((130, 90, 50)))
    for x in (-0.09, 0.09):
        sph(x, -0.06, 0.0, 0.07, mat((70, 50, 30)), sub=1, scale=(1, 1.4, 0.6))
    # ramiona i dłonie
    rod((-0.2, 0, 0.88), (-0.3, -0.12, 0.6), 0.07, robe)
    rod((0.2, 0, 0.88), (0.28, -0.14, 0.72), 0.07, robe)
    sph(-0.3, -0.15, 0.58, 0.045, mat(SKIN), sub=1)
    sph(0.28, -0.18, 0.72, 0.045, mat(SKIN), sub=1)
    # księga i pióro
    box(-0.32, -0.2, 0.46, 0.2, 0.05, 0.26, mat((140, 40, 40)), rz=0.3)
    box(-0.31, -0.228, 0.48, 0.17, 0.01, 0.22, mat((236, 222, 180)), rz=0.3)
    rod((0.28, -0.2, 0.7), (0.36, -0.25, 1.0), 0.012, mat((250, 250, 250), 0.6))
    # kaptur, twarz, blond grzywka
    sph(0, 0.02, 1.12, 0.2, robe_d, sub=3, scale=(1, 1, 1.12), smooth=True)
    cone(0, 0.12, 1.22, 0.09, 0.0, 0.2, robe_d, v=10, rot=(-0.7, 0, 0))
    sph(0, -0.07, 1.1, 0.135, mat(SKIN, 0.7), sub=3, smooth=True)
    sph(0, -0.11, 1.17, 0.125, mat((222, 184, 96), 0.8), sub=2, scale=(1.08, 0.75, 0.5), smooth=True)
    for x in (-0.05, 0.05):
        sph(x, -0.195, 1.11, 0.018, mat((30, 30, 50)), sub=1)
    box(0, -0.2, 1.03, 0.06, 0.01, 0.015, mat((170, 90, 80)))
    sph(0, -0.21, 1.075, 0.02, mat((222, 170, 140)), sub=1)
    # obrzeże kaptura
    bpy.ops.mesh.primitive_torus_add(major_radius=0.155, minor_radius=0.035, location=(0, -0.1, 1.11),
                                     rotation=(math.pi / 2, 0, 0))
    o = _fin(bpy.context.active_object, robe)
    o.scale = (1, 1.15, 1)
    render("hero", 154, 252, 77, 246, ppu=150, rot=(84, 0, 18))


# ------------------------------------------------------------------ portrety (popiersia)
def bust(p):
    reset()
    skin, hair = mat(SKIN, 0.65), mat(p["hair"], 0.8)
    cloth = mat(p["cloth"], 0.8)
    head = p["head"]
    female = head in ("veil", "crown_veil") or (head == "crown_s" and not p.get("beard") and p["hair"][0] > 180)
    # ramiona i szyja
    sph(0, 0, 0.0, 0.42, cloth, sub=3, scale=(1.25, 0.7, 0.55), smooth=True)
    if head == "mitre":
        for x in (-0.12, 0.12):
            box(x, -0.27, -0.2, 0.04, 0.01, 0.4, mat(GOLD, 0.4, 0.6))
    cyl(0, 0, 0.12, 0.09, 0.2, skin, v=16)
    # głowa
    sph(0, 0, 0.5, 0.2, skin, sub=3, scale=(0.92, 0.95, 1.12), smooth=True)
    for x in (-0.185, 0.185):
        sph(x, 0.0, 0.5, 0.045, skin, sub=2, scale=(0.5, 1, 1), smooth=True)
    cone(0, -0.19, 0.46, 0.035, 0.0, 0.07, mat((222, 170, 140), 0.6), v=8, rot=(math.radians(-80), 0, 0))
    for x in (-0.072, 0.072):
        sph(x, -0.165, 0.535, 0.03, mat((245, 245, 245), 0.3), sub=2, smooth=True)
        sph(x, -0.19, 0.535, 0.015, mat((40, 30, 30), 0.3), sub=2, smooth=True)
        box(x, -0.18, 0.585, 0.07, 0.02, 0.016, mat(tuple(int(c * 0.8) for c in p["hair"])))
    box(0, -0.185, 0.39, 0.075, 0.02, 0.018, mat((170, 90, 80), 0.5))
    for x in (-0.11, 0.11):
        sph(x, -0.16, 0.45, 0.03, mat((240, 160, 140), 0.7), sub=1, scale=(1, 0.4, 0.8))
    # włosy
    covered = head in ("hood", "veil", "crown_veil", "mitre", "helmet", "habit", "veil_dark")
    if head == "wig":
        hair = mat((236, 236, 232), 0.9)
    if not covered:
        sph(0, 0.03, 0.6, 0.21, hair, sub=3, scale=(0.98, 0.98, 0.72), smooth=True)
        sph(0, 0.09, 0.5, 0.2, hair, sub=3, scale=(0.97, 0.75, 1.0), smooth=True)
        if female or head == "crown_s":
            sph(0, 0.08, 0.32, 0.2, hair, sub=3, scale=(1.05, 0.7, 1.3), smooth=True)
    b = p.get("beard")
    if b in ("full", "long"):
        sph(0, -0.09, 0.37 if b == "full" else 0.3, 0.16, hair, sub=3, scale=(1.0, 0.8, 0.9 if b == "full" else 1.4), smooth=True)
        box(0, -0.185, 0.39, 0.075, 0.03, 0.018, mat((150, 80, 70), 0.5))
    elif b == "short":
        sph(0, -0.08, 0.38, 0.15, hair, sub=3, scale=(1.0, 0.85, 0.7), smooth=True)
        box(0, -0.2, 0.39, 0.075, 0.03, 0.018, mat((150, 80, 70), 0.5))
    elif b == "mustache":
        for x in (-0.05, 0.05):
            sph(x, -0.19, 0.415, 0.03, hair, sub=2, scale=(1.6, 0.7, 0.6), smooth=True)
    elif b == "mustache_big":
        for x in (-0.07, 0.07):
            sph(x, -0.185, 0.4, 0.04, hair, sub=2, scale=(1.9, 0.7, 0.8), smooth=True)
            sph(x * 1.6, -0.17, 0.36, 0.025, hair, sub=2, scale=(1, 0.7, 1.6), smooth=True)
    # nakrycia głowy
    gold = mat(GOLD, 0.3, 0.8)
    if head in ("crown_b", "crown_s", "crown_veil"):
        r = 0.2 if head == "crown_b" else 0.17
        z = 0.66 if head != "crown_veil" else 0.7
        cyl(0, 0.0, z, r, 0.07 if head == "crown_b" else 0.05, gold, v=20)
        n = 8 if head == "crown_b" else 6
        for k in range(n):
            a = k * math.tau / n
            cone(math.cos(a) * r * 0.95, math.sin(a) * r * 0.95, z + 0.06, 0.035, 0.0, 0.09 if head == "crown_b" else 0.06, gold, v=6)
        sph(0, -r, z + 0.035, 0.022, mat((200, 30, 40), 0.2), sub=1)
    if head == "circlet":
        bpy.ops.mesh.primitive_torus_add(major_radius=0.19, minor_radius=0.012, location=(0, 0, 0.62))
        _fin(bpy.context.active_object, gold)
    if head in ("veil", "crown_veil"):
        white = mat((238, 236, 228), 0.9)
        sph(0, 0.1, 0.55, 0.24, white, sub=3, scale=(1.05, 0.85, 1.1), smooth=True)
        cyl(0, 0.12, 0.05, 0.25, 0.45, white, v=20)
        sph(0, -0.02, 0.66, 0.2, white, sub=3, scale=(1.05, 0.9, 0.45), smooth=True)
    if head == "mitre":
        white = mat((240, 238, 230), 0.7)
        cone(0, 0, 0.62, 0.2, 0.06, 0.4, white, v=4, rot=(0, 0, math.pi / 4))
        box(0, -0.13, 0.62, 0.03, 0.01, 0.36, gold)
        cyl(0, 0, 0.62, 0.2, 0.04, gold, v=20)
    if head == "helmet":
        steel = mat(STEEL, 0.3, 0.85)
        cone(0, 0, 0.56, 0.22, 0.0, 0.32, steel, v=16)
        box(0, -0.205, 0.42, 0.03, 0.02, 0.18, steel)
        sph(0, 0.05, 0.42, 0.2, mat((150, 156, 166), 0.5, 0.7), sub=2, scale=(1.05, 0.9, 0.8))
    if head == "hood":
        robe_d = mat(tuple(int(c * 0.75) for c in p["cloth"]), 0.85)
        sph(0, 0.06, 0.53, 0.25, robe_d, sub=3, scale=(1, 0.95, 1.15), smooth=True)
        cone(0, 0.18, 0.66, 0.1, 0.0, 0.22, robe_d, v=10, rot=(-0.7, 0, 0))
        bpy.ops.mesh.primitive_torus_add(major_radius=0.19, minor_radius=0.04, location=(0, -0.1, 0.51),
                                         rotation=(math.pi / 2, 0, 0))
        o = _fin(bpy.context.active_object, cloth)
        o.scale = (1, 1.2, 1)
        sph(0, -0.12, 0.62, 0.15, hair, sub=2, scale=(1.05, 0.6, 0.4), smooth=True)
    if head == "fur":
        cyl(0, 0, 0.6, 0.215, 0.12, mat((100, 70, 44), 1.0), v=20)
        sph(0, 0, 0.72, 0.17, mat((40, 110, 70), 0.8), sub=2, scale=(1, 1, 0.6), smooth=True)
    if head == "kolpak":          # kołpak futrzany z piórem i klejnotem
        cyl(0, 0.0, 0.6, 0.215, 0.13, mat((95, 65, 42), 1.0), v=20)
        sph(0, 0.02, 0.74, 0.18, cloth, sub=2, scale=(1, 1, 0.55), smooth=True)
        sph(0, -0.2, 0.68, 0.03, mat((200, 30, 40), 0.2), sub=1)
        rod((0.0, -0.18, 0.7), (-0.06, -0.1, 0.98), 0.02, mat((248, 248, 245), 0.7))
    if head == "beret":           # renesansowy beret
        cyl(0, 0.02, 0.66, 0.24, 0.05, mat((30, 30, 34), 0.9), v=24)
        sph(0, 0.02, 0.7, 0.2, mat((30, 30, 34), 0.9), sub=2, scale=(1, 1, 0.3), smooth=True)
        sph(0, 0.06, 0.5, 0.2, hair, sub=3, scale=(1.1, 0.8, 1.05), smooth=True)
    if head == "wig":             # peruka pudrowana
        for x in (-0.17, 0.17):
            for z in (0.48, 0.56):
                sph(x, 0.02, z, 0.05, hair, sub=2, smooth=True)
        box(0, 0.2, 0.42, 0.04, 0.03, 0.12, mat((30, 30, 30)))
    if head == "rogatywka":       # konfederatka
        cyl(0, 0, 0.6, 0.215, 0.07, mat((70, 50, 35), 1.0), v=20)
        box(0, 0, 0.67, 0.34, 0.34, 0.1, cloth, rz=math.pi / 4)
        sph(0, -0.2, 0.64, 0.025, mat(GOLD, 0.3, 0.8), sub=1)
    if head == "habit":           # biały habit paulina
        white = mat((236, 234, 226), 0.9)
        sph(0, 0.06, 0.53, 0.25, white, sub=3, scale=(1, 0.95, 1.15), smooth=True)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.19, minor_radius=0.04, location=(0, -0.1, 0.51),
                                         rotation=(math.pi / 2, 0, 0))
        o = _fin(bpy.context.active_object, white)
        o.scale = (1, 1.2, 1)
    if head == "kapelusz":        # kapelusz krakowski z piórami
        black = mat((30, 30, 32), 0.8)
        cyl(0, 0, 0.62, 0.3, 0.02, black, v=24)
        cyl(0, 0, 0.62, 0.17, 0.1, black, v=20)
        for k, c in enumerate([(200, 40, 40), (60, 120, 200), (240, 200, 60)]):
            rod((0.1, 0.05 - k * 0.04, 0.68), (0.2, 0.08 - k * 0.04, 0.9), 0.012, mat(c))
    if head == "collar":          # koloratka i czarna sutanna
        box(0, -0.12, 0.2, 0.12, 0.02, 0.04, mat((245, 245, 245)))
    if head == "veil_dark":       # czepiec renesansowej królowej
        dark = mat((40, 30, 30), 0.8)
        sph(0, 0.06, 0.55, 0.23, dark, sub=3, scale=(1, 0.95, 1.05), smooth=True)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.02, location=(0, -0.09, 0.55),
                                         rotation=(math.pi / 2, 0, 0))
        _fin(bpy.context.active_object, mat((240, 236, 220), 0.3, 0.2))


def portraits():
    sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..")))
    from kronika import data as gdata
    people = dict(gdata.CHARACTERS)
    people["damian"] = gdata.HERO
    for cid, c in people.items():
        bust(c["p"])
        render(f"portrait_{cid}", 128, 128, 64, 124, ppu=126, rot=(86, 0, 12))


# ------------------------------------------------------------------ tła bitew
def battle_bg(kind):
    reset()
    sc = bpy.context.scene
    world = sc.world
    nt = world.node_tree
    for n in list(nt.nodes):
        if n.type not in ("BACKGROUND", "OUTPUT_WORLD"):
            nt.nodes.remove(n)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    top, hor = ((70, 40, 40), (200, 120, 80)) if kind == "grod" else ((70, 120, 190), (220, 214, 180))
    ramp.color_ramp.elements[0].color = lin(hor)
    ramp.color_ramp.elements[1].color = lin(top)
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[1].position = 0.6
    nt.links.new(tc.outputs["Window"], sep.inputs[0])
    nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
    bg = nt.nodes["Background"]
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs[1].default_value = 1.0
    # teren
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 20, 0))
    g = _fin(bpy.context.active_object, noise_mat((70, 110, 50), (104, 146, 66), scale=3, seed=1, bump=0.3))
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=60)
    bpy.ops.object.mode_set(mode="OBJECT")
    for v in g.data.vertices:
        y = v.co.y + 20
        if y > 6:
            v.co.z = (math.sin(v.co.x / 4.0) * 1.2 + math.sin(v.co.x / 9.0 + 1) * 2.0 + 1.5) * min(1, (y - 6) / 14)
    for p in g.data.polygons:
        p.use_smooth = True
    r = random.Random(len(kind))
    n = 90 if kind == "forest" else 45
    pine = [mat((34, 84, 46)), mat((44, 100, 54))]
    leaf = [mat((62, 120, 50)), mat((52, 104, 44))]
    for _ in range(n):
        x, y = r.uniform(-34, 34), r.uniform(16, 40) if kind != "forest" else r.uniform(11, 34)
        if abs(x) < 6 and y < 22:
            continue
        s = r.uniform(0.8, 1.5)
        zb = (math.sin(x / 4.0) * 1.2 + math.sin(x / 9.0 + 1) * 2.0 + 1.5) * min(1, max(0, (y - 6) / 14))
        cyl(x, y, zb, 0.08 * s, 0.6 * s, mat((92, 62, 36)), v=6)
        if r.random() < 0.5:
            cone(x, y, zb + 0.35 * s, 0.6 * s, 0, 1.6 * s, r.choice(pine), v=7)
        else:
            sph(x, y, zb + 1.0 * s, 0.6 * s, r.choice(leaf), sub=1)
    if kind == "grod":
        wall = mat((126, 88, 50))
        for i in range(34):
            x = -13 + i * 0.32
            h = 3.4 + (i % 2) * 0.3
            cyl(x, 2.0, -0.5, 0.17, h, wall, v=7)
            cone(x, 2.0, h - 0.5, 0.17, 0, 0.4, wall, v=7)
        box(-3.0, 2.2, -0.5, 1.6, 1.6, 5.5, mat(WOOD))
        pyramid(-3.0, 2.2, 5.0, 2.2, 1.5, mat(THATCH, 0.95))
    sc.render.film_transparent = False
    co = sc.camera
    co.data.type = "PERSP"
    co.data.lens = 30
    co.data.shift_x = co.data.shift_y = 0
    co.location = (0, -12, 2.4)
    co.rotation_euler = (math.radians(86), 0, 0)
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    name = f"battle_{kind}"
    if not ONLY or name.startswith(ONLY):
        _render_jpg(name)
    # przywróć jednolite tło świata dla kolejnych renderów
    for n in list(nt.nodes):
        if n.type not in ("BACKGROUND", "OUTPUT_WORLD"):
            nt.nodes.remove(n)
    bg.inputs[0].default_value = lin((150, 160, 185))
    bg.inputs[1].default_value = 0.9
    sc.render.film_transparent = True


# ------------------------------------------------------------------ przerywniki filmowe
def _sky(top, hor):
    nt = bpy.context.scene.world.node_tree
    for n in list(nt.nodes):
        if n.type not in ("BACKGROUND", "OUTPUT_WORLD"):
            nt.nodes.remove(n)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = lin(hor)
    ramp.color_ramp.elements[1].color = lin(top)
    ramp.color_ramp.elements[1].position = 0.65
    nt.links.new(tc.outputs["Window"], sep.inputs[0])
    nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
    bg = nt.nodes["Background"]
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs[1].default_value = 1.0


def _reset_world():
    nt = bpy.context.scene.world.node_tree
    for n in list(nt.nodes):
        if n.type not in ("BACKGROUND", "OUTPUT_WORLD"):
            nt.nodes.remove(n)
    bg = nt.nodes["Background"]
    bg.inputs[0].default_value = lin((150, 160, 185))
    bg.inputs[1].default_value = 0.9


def place(fn, x, y, rz=0.0, sc=1.0, z=0.0):
    """Buduje obiekt funkcją fn w początku układu i przenosi go na miejsce."""
    before = set(gen_coll().objects)
    fn()
    new = [o for o in gen_coll().objects if o not in before]
    bpy.context.view_layer.update()     # przelicz macierze (skala ustawiona po utworzeniu obiektu)
    from mathutils import Matrix
    m = Matrix.Translation((x, y, z)) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Scale(sc, 4)
    for o in new:
        o.matrix_world = m @ o.matrix_world


def _ground(c1=(70, 110, 50), c2=(104, 146, 66), hills=True):
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 30, 0))
    g = _fin(bpy.context.active_object, noise_mat(c1, c2, scale=4, seed=3, bump=0.3))
    if hills:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=50)
        bpy.ops.object.mode_set(mode="OBJECT")
        for v in g.data.vertices:
            yy = v.co.y + 30
            if yy > 18:
                v.co.z = (math.sin(v.co.x / 5.0) * 1.5 + math.sin(v.co.x / 11.0 + 2) * 2.5 + 2.0) * min(1, (yy - 18) / 20)
        for p in g.data.polygons:
            p.use_smooth = True


def _forest(n, ymin, ymax, seed=1, xr=40):
    r = random.Random(seed)
    for _ in range(n):
        x, y = r.uniform(-xr, xr), r.uniform(ymin, ymax)
        s_ = r.uniform(1.2, 2.2)
        cyl(x, y, 0, 0.08 * s_, 0.6 * s_, mat((92, 62, 36)), v=6)
        if r.random() < 0.6:
            cone(x, y, 0.35 * s_, 0.6 * s_, 0, 1.6 * s_, mat(r.choice([(34, 84, 46), (44, 100, 54)])), v=7)
        else:
            sph(x, y, 1.0 * s_, 0.6 * s_, mat(r.choice([(62, 120, 50), (52, 104, 44)])), sub=1)


def _army(kind, fac, x0, y0, cols, rows, dx=0.9, dy=1.1, face=0.0, seed=0, banner=None):
    r = random.Random(seed)
    for i in range(cols):
        for j in range(rows):
            x = x0 + i * dx + r.uniform(-0.15, 0.15)
            y = y0 + j * dy + r.uniform(-0.15, 0.15)
            if kind in ("horse", "knight", "knight_t", "horse_mg", "horse_lt"):
                place(lambda: (horse((110, 76, 46) if kind == "horse" else (90, 70, 60),
                                     {"knight": (190, 40, 44), "knight_t": (238, 238, 232)}.get(kind),
                                     {"knight_t": (20, 20, 20)}.get(kind)),
                               human("mg" if kind == "horse_mg" else fac, kind, z0=0.42, legs=False, weapon=False),
                               rod((-0.3, 0.2, 0.85), (1.0, 0.2, 1.3), 0.018, mat((130, 100, 60)))),
                      x, y, face)
            else:
                place(lambda: human(fac, kind), x, y, face)
    if banner:
        c1, c2, cross = banner
        cyl(x0 + cols * dx / 2, y0 - 0.5, 0, 0.03, 3.2, mat((80, 58, 34)), v=6)
        box(x0 + cols * dx / 2 + 0.45, y0 - 0.5, 2.3, 0.9, 0.02, 0.8, mat(c1, 0.7))
        if c2:
            box(x0 + cols * dx / 2 + 0.45, y0 - 0.49, 2.3, 0.9, 0.02, 0.4, mat(c2, 0.7))
        if cross:
            box(x0 + cols * dx / 2 + 0.45, y0 - 0.52, 2.35, 0.12, 0.02, 0.7, mat(cross))
            box(x0 + cols * dx / 2 + 0.45, y0 - 0.52, 2.62, 0.6, 0.02, 0.12, mat(cross))


def _render_jpg(name):
    """Duże kadry (tła bitew, przerywniki) zapisujemy jako JPG – są kilka razy mniejsze niż PNG."""
    sc = bpy.context.scene
    st = sc.render.image_settings
    st.file_format, st.color_mode, st.quality = "JPEG", "RGB", 88
    sc.render.filepath = os.path.join(OUT, name + ".jpg")
    bpy.ops.render.render(write_still=True)
    st.file_format, st.color_mode = "PNG", "RGBA"
    print("  ✓", name, flush=True)


def _shot(name, cam_loc, cam_rot, lens=35, W=1280, H=720):
    sc = bpy.context.scene
    co = sc.camera
    co.data.type = "PERSP"
    co.data.lens = lens
    co.data.shift_x = co.data.shift_y = 0
    co.location = cam_loc
    co.rotation_euler = [math.radians(a) for a in cam_rot]
    sc.render.film_transparent = False
    sc.render.resolution_x, sc.render.resolution_y = W, H
    if not ONLY or name.startswith(ONLY):
        _render_jpg(name)
    sc.render.film_transparent = True


def _tent(x, y, c1, c2, s_=1.0):
    cyl(x, y, 0, 1.3 * s_, 1.4 * s_, mat(c1), v=16)
    cone(x, y, 1.4 * s_, 1.45 * s_, 0, 1.6 * s_, mat(c2), v=16)
    cyl(x, y, 3.0 * s_, 0.03, 1.0, mat((80, 58, 34)), v=6)
    box(x + 0.3, y, 3.6 * s_, 0.6, 0.02, 0.35, mat((200, 30, 40)))


def _hussars(x0, y0, cols, rows, face, seed):
    r = random.Random(seed)
    for i in range(cols):
        for j in range(rows):
            place(hussar_model, x0 + i * 1.3 + r.uniform(-.2, .2), y0 + j * 1.5 + r.uniform(-.2, .2), face)


def _cannon(x, y, rz, sc=1.4):
    def mk():
        w = mat((120, 84, 50))
        box(0, 0, 0.12, 0.7, 0.24, 0.08, w)
        for yy in (-0.16, 0.16):
            cyl(-0.12, yy, 0.14, 0.14, 0.04, mat((80, 60, 40)), v=12, rot=(math.pi / 2, 0, 0), center=True)
        rod((-0.2, 0, 0.3), (0.5, 0, 0.46), 0.09, mat((70, 72, 78), 0.4, 0.8), v=12)
    place(mk, x, y, rz, sc)


def _wall_ring(cx, cy, rx, ry, h, m, n=46):
    for i in range(n):
        a = i / n * math.tau
        x, y = cx + math.cos(a) * rx, cy + math.sin(a) * ry
        cyl(x, y, 0, 0.18, h, m, v=7)
        cone(x, y, h, 0.18, 0, 0.35, m, v=7)


def _church_tower(x, y, h, wall, roof):
    box(x, y, 0, 1.6, 1.6, h, mat(wall))
    for k in range(int(h / 1.4)):
        box(x, y - 0.81, 0.8 + k * 1.4, 0.35, 0.02, 0.6, mat((60, 60, 80), 0.2))
    helmet(x, y, h, 0.8, mat(roof, 0.5, 0.3))


def cutscenes():
    brick = mat((170, 90, 60), 0.9)
    # Świecino 1462: tabor i rycerze zakonu
    reset(); _sky((90, 130, 180), (230, 215, 175)); _ground(); _forest(70, 20, 70, seed=21)
    for k in range(9):
        place(lambda: unit_body_wagon(), -6 + k * 1.5, 5, math.radians(5), 1.6)
    _army("musket", "pl", -6, 6.5, 9, 1, 1.5, 1, face=math.radians(-90), seed=22)
    _army("knight_t", "tz", -6, 15, 8, 2, 1.4, 1.5, face=math.radians(-90), seed=23, banner=((240, 240, 240), None, (20, 20, 20)))
    _shot("cut_swiecino_1", (0, -6, 3.0), (78, 0, 0), lens=30)
    # Wielkie Łuki 1580: płonące drewniane mury
    reset(); _sky((60, 40, 50), (230, 130, 70)); _ground((70, 90, 50), (100, 120, 60))
    wood = mat((126, 88, 50))
    _wall_ring(0, 16, 6, 3, 2.6, wood)
    for (x, y) in [(-3, 14), (2, 14.5), (4, 17)]:
        for j in range(5):
            sph(x + j * 0.3, y, 2.5 + j * 1.6, 0.7 + j * 0.35, mat((60, 55, 55), 1.0, alpha=0.6), sub=2, smooth=True)
        sph(x, y - 0.3, 2.4, 0.5, mat((250, 140, 40), emit=8.0), sub=2, smooth=True)
    _army("pike", "cz", -7, 4, 10, 2, 0.9, 1.1, face=math.radians(80), seed=24)
    _cannon(5, 5, math.radians(80)); _cannon(7, 6, math.radians(80))
    _shot("cut_luki_1", (0, -6, 2.2), (82, 0, 0), lens=30)
    # Warka 1656: Szwedzi przy przeprawie przez Pilicę
    reset(); _sky((110, 150, 200), (235, 220, 180)); _ground(); _forest(90, 6, 60, seed=25)
    box(0, 12, 0.01, 80, 4, 0.02, mat((60, 110, 170), 0.1))
    _army("musket", "sv", -6, 11, 10, 2, 0.9, 1.0, face=math.radians(-90), seed=26, banner=((50, 80, 160), (230, 200, 60), None))
    _hussars(-9, 3, 5, 1, math.radians(15), 27)
    _shot("cut_warka_1", (-2, -7, 2.8), (80, 0, -8), lens=30)
    # Wiedeń 1683: szarża husarii ku obozowi tureckiemu
    reset(); _sky((90, 140, 200), (240, 220, 170)); _ground()
    for k in range(18):
        x, y = -14 + (k % 9) * 3.4, 22 + (k // 9) * 4
        cyl(x, y, 0, 1.0, 1.0, mat((236, 232, 220)), v=12)
        cone(x, y, 1.0, 1.05, 0, 1.0, mat([(170, 40, 40), (60, 120, 70)][k % 2]), v=12)
    _hussars(-8, 4, 8, 2, math.radians(70), 28)
    _army("musket", "tr", -6, 15, 10, 1, 1.2, 1, face=math.radians(-90), seed=29)
    _shot("cut_wieden_1", (-3, -4, 3.2), (80, 0, -14), lens=28)
    reset(); _sky((120, 150, 200), (240, 225, 180)); _ground()
    _tent(0, 9, (236, 232, 220), (170, 40, 40), 1.6)
    for k, c in enumerate([(170, 40, 40), (60, 120, 70), (240, 200, 60)]):
        cyl(-2.5 + k * 2.5, 6, 0, 0.04, 3.5, mat((120, 90, 50)), v=6)
        box(-2.5 + k * 2.5 + 0.5, 6, 2.6, 1.0, 0.03, 0.8, mat(c))
    _hussars(-6, 2.5, 4, 1, math.radians(60), 30)
    _shot("cut_wieden_2", (0, -5, 2.2), (82, 0, 0), lens=30)
    # Jasna Góra 1771: klasztor zimą i rosyjskie armaty
    reset(); _sky((150, 160, 180), (225, 228, 235)); _ground((225, 228, 232), (245, 246, 248))
    box(0, 18, 0, 8, 5, 2.4, mat((220, 214, 196))); hip(0, 18, 2.4, 8, 5, 1.2, mat((150, 60, 50)))
    _church_tower(0, 15, 9, (230, 224, 206), (90, 150, 128))
    for k in range(4):
        _cannon(-6 + k * 3.5, 6, math.radians(85))
    _army("musket", "rs", -8, 3.5, 12, 1, 1.4, 1, face=math.radians(85), seed=31)
    _shot("cut_jasna_1", (0, -6, 2.4), (80, 0, 0), lens=28)
    # Racławice 1794: kosynierzy biegną na armaty
    reset(); _sky((110, 150, 200), (235, 225, 190)); _ground()
    for k in range(4):
        _cannon(-4 + k * 2.6, 14, math.radians(-90))
    _army("musket", "rs", -6, 16, 10, 1, 1.2, 1, face=math.radians(-90), seed=32)
    _army("scythe", "pl", -7, 3, 12, 3, 1.0, 1.2, face=math.radians(80), seed=33)
    _shot("cut_raclawice_1", (0, -6, 2.0), (82, 0, 0), lens=30)
    # Olsztyn 1521: ceglany zamek zimą
    reset(); _sky((140, 150, 175), (220, 224, 232)); _ground((225, 228, 232), (245, 246, 248))
    box(0, 16, 0, 9, 3, 4.5, brick); gable(0, 16, 4.5, 9, 3, 2.0, mat((150, 60, 50)))
    cyl(4.2, 14.5, 0, 1.2, 8, brick, v=16); cone(4.2, 14.5, 8, 1.3, 0, 2.4, mat((150, 60, 50)), v=16)
    for k in range(8):
        box(-4 + k * 1.1, 14.4, 2.0, 0.4, 0.05, 0.9, mat((50, 50, 60), 0.2))
    _army("knight_t", "tz", -6, 6, 8, 1, 1.5, 1, face=math.radians(80), seed=34)
    _shot("cut_olsztyn_1", (-1, -5, 2.6), (80, 0, -6), lens=30)
    # Kłuszyn 1610: szarża husarii
    reset(); _sky((180, 170, 160), (245, 220, 170)); _ground(); _forest(60, 25, 70, seed=35)
    for k in range(10):
        box(-12 + k * 2.6, 9, 0, 2.0, 0.08, 0.7, mat((120, 90, 60)))
    _hussars(-9, 3, 8, 2, math.radians(15), 36)
    _army("musket", "ru", -8, 14, 12, 1, 1.3, 1, face=math.radians(-90), seed=37)
    _shot("cut_kluszyn_1", (-2, -5, 2.6), (80, 0, -10), lens=28)
    _reset_world()


def unit_body_wagon():
    box(0, 0, 0.2, 0.8, 0.36, 0.16, mat((130, 92, 52)))
    for x in (-0.25, 0.25):
        for y in (-0.2, 0.2):
            cyl(x, y, 0.13, 0.13, 0.03, mat((70, 50, 30)), v=12, rot=(math.pi / 2, 0, 0), center=True)
    box(0, 0, 0.36, 0.8, 0.3, 0.25, mat((150, 110, 70)))


# ------------------------------------------------------------------ główny program
def needed_units():
    """Pary (rodzaj, frakcja) używane w treści gry – tylko te renderujemy."""
    sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..")))
    from kronika import data as gdata
    pairs = {(c["unit"], c["faction"]) for c in gdata.CARDS.values()}
    pairs |= {(r["unit"], r["faction"]) for r in gdata.RAIDS.values()}
    pairs |= {(k, "pl") for k in ("pike", "musket", "horse", "hussar")}
    return sorted(pairs), sorted({(r["unit"], r["faction"]) for r in gdata.RAIDS.values()})


def main():
    """Część II: nowe budynki epok, jednostki, portrety i przerywniki.
    Kafle terenu, drzewa, skały, tła bitew i postać Damiana pochodzą z części I (assets/3d)."""
    os.makedirs(OUT, exist_ok=True)
    setup_scene()
    print("Renderowanie do", OUT)
    units, walkers = needed_units()
    for ep in range(4):
        b_grod2(ep)
        for k in ["pole", "targ", "koszary", "kosciol", "zamek", "palisada", "zupa"]:
            b_epoch(k, ep)
    ANIM["wave"] = 1
    for ep in range(4):
        b_grod2(ep)
        b_epoch("koszary", ep)
        b_epoch("zamek", ep)
    for f in ["sv", "ru", "rs"]:
        b_camp2(f)
    ANIM["wave"] = 0
    for f in ["sv", "ru", "rs"]:
        b_camp2(f)
    for kind, fac in units:
        unit(kind, fac)
    for kind, fac in walkers + [("pike", "pl"), ("musket", "pl"), ("hussar", "pl")]:
        for ph in range(4):
            unit(kind, fac, ph)
    portraits()
    cutscenes()
    print("Gotowe.")


if __name__ == "__main__":
    main()
