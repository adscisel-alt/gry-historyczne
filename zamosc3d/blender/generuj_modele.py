"""Blender: generuje wszystkie modele 3D gry „Jan Zamoyski i Miasto Idealne 3D”.

Uruchom (z katalogu zamosc3d):
    blender -b -P blender/generuj_modele.py
Opcje po „--”:
    --bez-renderow   tylko modele .glb (bez portretów, miniatur i tła)

Wynik:
    godot/modele/*.glb      — budynki, drzewa, postacie, mury, rusztowanie...
    godot/ui/portret_*.png  — portrety postaci do dialogów (render Cycles)
    godot/ui/miniatura_*.png— miniatury budynków do menu budowy
    godot/ui/tlo_tytul.png  — panorama Rynku Wielkiego na ekran tytułowy

Układ współrzędnych: 1 pole mapy = 2 m. Model stoi na z=0, środek podstawy w (0,0).
Fasada (front) jest zwrócona na -Y (w Godocie: na +Z, czyli na południe).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

TU = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.join(TU, "..", "godot")
MODELE = os.path.join(GODOT, "modele")
UI = os.path.join(GODOT, "ui")
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDERY = "--bez-renderow" not in ARGS

# ----------------------------------------------------------------- kolory (sRGB)
TYNK = (236, 224, 192)
TYNK_C = (206, 190, 156)
BIEL = (246, 242, 232)
DACH = (172, 62, 42)
DACH_C = (130, 44, 34)
DREWNO = (128, 84, 48)
DREWNO_J = (176, 128, 80)
DREWNO_C = (88, 56, 32)
CEGLA = (164, 70, 50)
CEGLA_J = (198, 104, 72)
KAMIEN = (150, 150, 158)
KAMIEN_C = (104, 104, 114)
OKNO = (38, 50, 80)
ZLOTO = (232, 182, 58)
ZIELEN = (70, 130, 64)
ZIELEN_C = (40, 96, 52)
LISCIE = (66, 132, 62)
CZERWONY = (176, 36, 44)
GRANAT = (40, 56, 120)
CZARNY = (26, 20, 24)
ROZ = (228, 152, 140)
SKORA = (240, 196, 150)

_mat = {}


def lin(c):
    return tuple((v / 255) ** 2.2 for v in c)


def mat(kolor, emisja=0.0, metal=0.0, szorstkosc=0.85):
    klucz = (kolor, emisja, metal)
    if klucz in _mat:
        return _mat[klucz]
    m = bpy.data.materials.new("m_%02x%02x%02x" % kolor)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*lin(kolor), 1)
    p.inputs["Roughness"].default_value = szorstkosc
    p.inputs["Metallic"].default_value = metal
    if emisja:
        p.inputs["Emission Color"].default_value = (*lin(kolor), 1)
        p.inputs["Emission Strength"].default_value = emisja
    _mat[klucz] = m
    return m


def _nadaj(obj, kolor, **kw):
    obj.data.materials.clear()
    obj.data.materials.append(mat(kolor, **kw))
    return obj


def box(x, y, z0, sx, sy, sz, kolor, rot=(0, 0, 0), **kw):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z0 + sz / 2), rotation=rot)
    o = bpy.context.active_object
    o.scale = (sx, sy, sz)
    return _nadaj(o, kolor, **kw)


def cyl(x, y, z0, r, h, kolor, v=12, rot=(0, 0, 0), **kw):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=h, location=(x, y, z0 + h / 2), rotation=rot)
    return _nadaj(bpy.context.active_object, kolor, **kw)


def walec_lezacy(x, y, z, r, dl, kolor, os_="x", v=10):
    rot = (0, math.pi / 2, 0) if os_ == "x" else (math.pi / 2, 0, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=dl, location=(x, y, z), rotation=rot)
    return _nadaj(bpy.context.active_object, kolor)


def stozek(x, y, z0, r1, r2, h, kolor, v=12, rot=(0, 0, 0), **kw):
    bpy.ops.mesh.primitive_cone_add(vertices=v, radius1=r1, radius2=r2, depth=h, location=(x, y, z0 + h / 2),
                                    rotation=rot)
    return _nadaj(bpy.context.active_object, kolor, **kw)


def kula(x, y, z, r, kolor, seg=10, ringi=7, skala=(1, 1, 1), **kw):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=ringi, radius=r, location=(x, y, z))
    o = bpy.context.active_object
    o.scale = skala
    return _nadaj(o, kolor, **kw)


def ikosfera(x, y, z, r, kolor, skala=(1, 1, 1), pod=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=pod, radius=r, location=(x, y, z))
    o = bpy.context.active_object
    o.scale = skala
    return _nadaj(o, kolor)


def siatka(nazwa, verts, faces, kolor):
    me = bpy.data.meshes.new(nazwa)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(nazwa, me)
    bpy.context.collection.objects.link(o)
    return _nadaj(o, kolor)


def dach_dwuspadowy(x, y, z0, sx, sy, h, kolor, wzdluz="x", biodrowy=0.0):
    """Dach z kalenicą wzdłuż osi X (lub Y). biodrowy>0 skraca kalenicę (dach czterospadowy)."""
    if wzdluz == "x":
        a, b = sx / 2, sy / 2
        k = max(0.0, a - biodrowy)
        v = [(-a, -b, 0), (a, -b, 0), (a, b, 0), (-a, b, 0), (-k, 0, h), (k, 0, h)]
        f = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
    else:
        a, b = sx / 2, sy / 2
        k = max(0.0, b - biodrowy)
        v = [(-a, -b, 0), (a, -b, 0), (a, b, 0), (-a, b, 0), (0, -k, h), (0, k, h)]
        f = [(1, 2, 5, 4), (3, 0, 4, 5), (0, 1, 4), (2, 3, 5), (0, 3, 2, 1)]
    o = siatka("dach", [(vx + x, vy + y, vz + z0) for vx, vy, vz in v], f, kolor)
    return o


def graniastoslup(punkty, z0, h, kolor):
    n = len(punkty)
    v = [(px, py, z0) for px, py in punkty] + [(px, py, z0 + h) for px, py in punkty]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        f.append((i, j, n + j, n + i))
    return siatka("gr", v, f, kolor)


def okna_rzad(xs, y_front, z0, w, h, kolor=OKNO, rama=BIEL):
    for x in xs:
        box(x, y_front - 0.02, z0 - 0.06, w + 0.12, 0.05, h + 0.12, rama)
        box(x, y_front - 0.05, z0, w, 0.05, h, kolor)


def attyka(x, y_front, z0, szer, kolor=TYNK_C, glebokosc=0.25, h=0.5, odstep=0.7):
    box(x, y_front + glebokosc / 2, z0, szer, glebokosc, h, kolor)
    n = max(2, int(szer / odstep))
    for i in range(n + 1):
        px = x - szer / 2 + i * szer / n
        box(px, y_front + glebokosc / 2, z0 + h, 0.14, 0.14, 0.32, kolor)
        kula(px, y_front + glebokosc / 2, z0 + h + 0.38, 0.07, ZLOTO, seg=6, ringi=4, metal=0.6)


def czysc():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mat.clear()


def scal(nazwa):
    obiekty = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in obiekty:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obiekty[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if len(obiekty) > 1:
        bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = nazwa
    o.data.name = nazwa
    bpy.ops.object.shade_flat()
    return o


def eksportuj(nazwa):
    scal(nazwa)
    sciezka = os.path.join(MODELE, nazwa + ".glb")
    bpy.ops.export_scene.gltf(filepath=sciezka, export_format="GLB", use_selection=False, export_apply=True,
                              export_yup=True)
    print("model:", nazwa)


# ================================================================= BUDYNKI
def m_dom(ox=0, oy=0):
    box(ox, oy, 0, 1.6, 1.5, 1.2, TYNK)
    for sx in (-0.78, 0.78):
        for sy in (-0.73, 0.73):
            box(ox + sx, oy + sy, 0, 0.1, 0.1, 1.2, DREWNO)
    box(ox, oy - 0.73, 0.55, 1.6, 0.08, 0.08, DREWNO)
    dach_dwuspadowy(ox, oy, 1.2, 1.95, 1.85, 1.0, DACH)
    box(ox, oy - 0.76, 0, 0.36, 0.05, 0.72, DREWNO_C)
    okna_rzad([ox - 0.5, ox + 0.5], oy - 0.75, 0.55, 0.26, 0.3)
    box(ox + 0.45, oy + 0.3, 1.5, 0.22, 0.22, 0.9, CEGLA)


def m_kamienica(kolor, ox=0, oy=0):
    ciemny = tuple(int(c * .8) for c in kolor)
    yf = oy - 1.7
    # parter cofnięty za podcieniami
    box(ox, oy + 0.35, 0, 3.6, 2.7, 1.35, ciemny)
    # piętra
    box(ox, oy, 1.35, 3.6, 3.4, 2.0, kolor)
    box(ox, yf + 0.04, 1.3, 3.7, 0.12, 0.12, BIEL)
    box(ox, yf + 0.04, 3.3, 3.7, 0.14, 0.14, BIEL)
    # arkady podcieni
    for px in (-1.7, -0.57, 0.57, 1.7):
        box(ox + px, yf + 0.2, 0, 0.26, 0.4, 1.35, kolor)
    for px in (-1.13, 0, 1.13):
        box(ox + px, yf + 0.2, 1.05, 0.88, 0.4, 0.3, kolor)
        box(ox + px - 0.36, yf + 0.2, 0.9, 0.18, 0.4, 0.18, kolor)
        box(ox + px + 0.36, yf + 0.2, 0.9, 0.18, 0.4, 0.18, kolor)
    box(ox, oy - 0.95, 0, 0.5, 0.05, 1.0, DREWNO_C)
    okna_rzad([ox - 1.1, ox, ox + 1.1], yf, 1.65, 0.42, 0.62)
    okna_rzad([ox - 1.1, ox, ox + 1.1], yf, 2.5, 0.42, 0.55)
    # ornament
    for px in (-1.6, -0.55, 0.55, 1.6):
        box(ox + px, yf - 0.03, 2.35, 0.1, 0.05, 0.1, ZLOTO)
    box(ox, oy, 3.4, 3.4, 3.2, 0.05, DACH_C)
    attyka(ox, yf, 3.44, 3.7, kolor=TYNK_C)


def m_tartak():
    for sx in (-1.4, 1.4):
        for sy in (-1.0, 1.0):
            box(sx, sy, 0, 0.16, 0.16, 1.6, DREWNO)
    dach_dwuspadowy(0, 0, 1.6, 3.4, 2.6, 0.9, DREWNO_C)
    box(0, 0, 0.6, 2.2, 0.8, 0.1, DREWNO_J)
    for sy in (-0.3, 0.3):
        box(-1.0, sy, 0, 0.12, 0.12, 0.6, DREWNO)
        box(1.0, sy, 0, 0.12, 0.12, 0.6, DREWNO)
    walec_lezacy(0, 0, 0.88, 0.17, 2.0, DREWNO_J)
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.45, depth=0.04, location=(0.3, 0, 0.9),
                                        rotation=(math.pi / 2, 0, 0))
    _nadaj(bpy.context.active_object, KAMIEN, metal=0.7, szorstkosc=0.3)
    for i, (dy, dz) in enumerate([(-0.25, 0.18), (0.25, 0.18), (0, 0.5), (-0.5, 0.18), (0.5, 0.18)]):
        walec_lezacy(0.2, 1.55 + dy, dz, 0.18, 2.2, DREWNO_J if i % 2 else DREWNO)


def m_kamieniolom():
    cyl(0, 0, -0.05, 1.7, 0.08, KAMIEN_C, v=10)
    for (x, y, s, r) in [(-0.8, 0.5, 0.9, 0.3), (0.6, 0.7, 1.1, -0.4), (0.2, -0.3, 0.6, 0.9), (-0.9, -0.6, 0.5, 0.2)]:
        ikosfera(x, y, s * 0.45, s * 0.7, KAMIEN, skala=(1.2, 1, 0.8))
        bpy.context.active_object.rotation_euler = (0, 0, r)
    for (x, y, z) in [(1.1, -0.9, 0), (1.5, -0.4, 0), (1.3, -0.65, 0.35)]:
        box(x, y, z, 0.5, 0.35, 0.35, (184, 184, 190))
    walec_lezacy(-0.2, -1.2, 0.1, 0.04, 1.0, DREWNO, os_="x")
    box(0.32, -1.2, 0.02, 0.1, 0.4, 0.12, KAMIEN_C, metal=0.6)


def m_cegielnia():
    kula(-0.4, 0.2, 0, 1.2, CEGLA, seg=12, ringi=8, skala=(1, 1, 0.9))
    box(-0.4, -0.95, 0, 0.6, 0.3, 0.7, CZARNY)
    box(-0.4, -1.0, 0.05, 0.45, 0.2, 0.45, (255, 140, 40), emisja=3.0)
    cyl(0.1, 0.6, 0, 0.25, 3.0, CEGLA_J, v=8)
    for i in range(3):
        for j in range(3 - i):
            box(1.15, -0.8 + j * 0.42 + i * 0.21, i * 0.22, 0.6, 0.38, 0.2, CEGLA_J if (i + j) % 2 else CEGLA)
    box(1.2, 0.8, 0, 0.9, 0.7, 0.05, DREWNO_J)
    for sx in (-0.3, 0.3):
        box(1.2 + sx, 0.8, 0.05, 0.25, 0.5, 0.12, (150, 110, 80))


def m_kram():
    for sx in (-0.75, 0.75):
        for sy in (-0.55, 0.55):
            box(sx, sy, 0, 0.08, 0.08, 1.4, DREWNO)
    box(0, -0.1, 0.7, 1.6, 0.9, 0.08, DREWNO_J)
    box(0, -0.1, 0, 1.5, 0.8, 0.7, DREWNO)
    for i in range(6):
        box(-0.68 + i * 0.27, -0.05, 1.4, 0.27, 1.4, 0.08, CZERWONY if i % 2 else BIEL, rot=(0.2, 0, 0))
    for i, k in enumerate([(230, 180, 60), (120, 180, 70), (200, 80, 60), (240, 140, 40)]):
        kula(-0.5 + i * 0.33, -0.25, 0.86, 0.11, k, seg=6, ringi=4)


def m_palac():
    box(0, 0, 0, 5.6, 3.2, 2.8, TYNK)
    box(0, -1.62, 1.35, 5.7, 0.12, 0.12, TYNK_C)
    dach_dwuspadowy(0, 0, 2.8, 5.9, 3.5, 1.4, DACH, biodrowy=1.2)
    box(0, -0.15, 0, 1.8, 3.2, 3.4, BIEL)
    attyka(0, -1.75, 3.4, 1.9, kolor=TYNK_C)
    box(0, -1.78, 0, 0.7, 0.1, 1.2, DREWNO_C)
    cyl(0, -1.78, 1.0, 0.35, 0.1, DREWNO_C, rot=(math.pi / 2, 0, 0))
    cyl(0, -1.8, 2.6, 0.3, 0.05, CZERWONY, v=12, rot=(math.pi / 2, 0, 0))
    box(0, -1.84, 2.48, 0.08, 0.05, 0.28, BIEL)
    for row in (0.5, 1.75):
        okna_rzad([-2.3, -1.6, -0.9, 0.9, 1.6, 2.3], -1.6, row, 0.36, 0.62)
    okna_rzad([-0.45, 0.45], -1.75, 1.75, 0.3, 0.62)
    for sx in (-2.85, 2.85):
        box(sx, 0, 0, 0.12, 3.25, 2.8, TYNK_C)


def m_ratusz():
    box(0, 0.2, 0, 3.6, 3.0, 2.6, ROZ)
    box(0, -1.32, 1.25, 3.7, 0.12, 0.12, BIEL)
    attyka(0, -1.3, 2.6, 3.7, kolor=TYNK_C)
    box(0, 0.2, 2.6, 3.4, 2.8, 0.05, DACH_C)
    okna_rzad([-1.2, 1.2], -1.3, 0.45, 0.4, 0.6)
    okna_rzad([-1.2, -0.4, 0.4, 1.2], -1.3, 1.6, 0.36, 0.6)
    # wieża
    box(0, 0.6, 2.6, 1.1, 1.1, 3.4, ROZ)
    box(0, 0.6, 6.0, 1.25, 1.25, 0.15, TYNK_C)
    cyl(0, 0.03, 4.6, 0.32, 0.06, BIEL, v=16, rot=(math.pi / 2, 0, 0))
    box(0, -0.02, 4.75, 0.04, 0.03, 0.22, CZARNY)
    okna_rzad([0], 0.05, 3.3, 0.3, 0.6)
    box(0, 0.6, 6.15, 0.8, 0.8, 0.7, DACH)
    stozek(0, 0.6, 6.85, 0.5, 0.0, 0.9, DACH, v=8)
    cyl(0, 0.6, 7.75, 0.04, 0.4, ZLOTO, metal=0.6)
    kula(0, 0.6, 8.15, 0.09, ZLOTO, metal=0.6)
    # wachlarzowe schody
    for i, r in enumerate((1.5, 1.2, 0.9, 0.6)):
        cyl(0, -1.3, i * 0.18, r, 0.18, KAMIEN if i % 2 else (176, 176, 180), v=20)
    box(0, -1.32, 0.72, 0.6, 0.06, 1.0, DREWNO_C)


def m_kolegiata():
    box(0, 0.3, 0, 3.0, 5.0, 3.2, BIEL)
    dach_dwuspadowy(0, 0.3, 3.2, 3.3, 5.2, 1.7, (110, 116, 124), wzdluz="y")
    # fasada ze szczytem
    yf = -2.25
    box(0, yf, 0, 3.4, 0.3, 3.6, TYNK)
    v = [(-1.7, yf - 0.15, 3.6), (1.7, yf - 0.15, 3.6), (0, yf - 0.15, 5.3),
         (-1.7, yf + 0.15, 3.6), (1.7, yf + 0.15, 3.6), (0, yf + 0.15, 5.3)]
    siatka("szczyt", v, [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], TYNK)
    for sx in (-1.25, 1.25):
        cyl(sx, yf, 3.75, 0.22, 0.32, TYNK_C, v=10, rot=(math.pi / 2, 0, 0))
    cyl(0, yf - 0.16, 4.15, 0.32, 0.05, OKNO, v=12, rot=(math.pi / 2, 0, 0))
    box(0, yf, 5.3, 0.08, 0.08, 0.6, ZLOTO, metal=0.6)
    box(0, yf, 5.6, 0.36, 0.08, 0.08, ZLOTO, metal=0.6)
    box(0, yf - 0.16, 0, 0.8, 0.06, 1.6, DREWNO_C)
    cyl(0, yf - 0.16, 1.4, 0.4, 0.06, DREWNO_C, v=12, rot=(math.pi / 2, 0, 0))
    for sx in (-1.0, 1.0):
        okna_rzad([sx], yf - 0.15, 1.6, 0.35, 1.0)
    for sy in (-0.8, 0.6, 2.0):
        for sx in (-1.52, 1.52):
            box(sx, sy, 1.2, 0.05, 0.4, 1.2, OKNO)
    # dzwonnica
    box(1.85, 2.2, 0, 1.0, 1.0, 5.2, TYNK)
    box(1.85, 2.2, 5.2, 1.15, 1.15, 0.12, TYNK_C)
    stozek(1.85, 2.2, 5.32, 0.75, 0.0, 1.3, (90, 120, 124), v=4, rot=(0, 0, math.pi / 4))
    kula(1.85, 2.2, 6.7, 0.08, ZLOTO, metal=0.6)
    box(1.85, 1.68, 4.0, 0.36, 0.05, 0.6, OKNO)


def m_akademia():
    box(0, 0, 0, 5.6, 3.0, 3.0, (238, 214, 150))
    box(0, -1.52, 1.45, 5.7, 0.12, 0.12, BIEL)
    box(0, 0, 3.0, 5.4, 2.8, 0.05, DACH_C)
    attyka(0, -1.5, 3.0, 5.7, kolor=TYNK_C, odstep=0.8)
    for row in (0.55, 1.95):
        okna_rzad([-2.3, -1.55, -0.8, 0.8, 1.55, 2.3], -1.5, row, 0.36, 0.7)
    box(0, -1.55, 0, 1.2, 0.12, 1.5, BIEL)
    box(0, -1.62, 0, 0.6, 0.06, 1.1, DREWNO_C)
    cyl(0, -1.62, 0.95, 0.3, 0.06, DREWNO_C, v=12, rot=(math.pi / 2, 0, 0))
    box(0, -1.6, 2.0, 0.7, 0.06, 0.5, BIEL)  # otwarta księga
    box(0, -1.63, 2.02, 0.04, 0.03, 0.46, CZERWONY)
    for sx in (-2.85, 2.85):
        box(sx, 0, 0, 0.12, 3.05, 3.0, TYNK_C)


def m_bastion():
    pkt = [(0, -1.95), (1.85, -0.6), (1.4, 1.6), (-1.4, 1.6), (-1.85, -0.6)]
    graniastoslup(pkt, 0, 1.1, CEGLA)
    wew = [(x * 0.85, y * 0.85) for x, y in pkt]
    graniastoslup(wew, 1.1, 0.25, ZIELEN)
    for x, y in pkt:
        box(x * 0.93, y * 0.93, 1.1, 0.3, 0.3, 0.35, CEGLA_J)
    box(0, -0.2, 1.35, 0.5, 0.6, 0.2, DREWNO)
    walec_lezacy(0, -0.65, 1.62, 0.1, 1.0, (60, 60, 66), os_="y")
    for sx in (-0.28, 0.28):
        walec_lezacy(sx, -0.25, 1.45, 0.16, 0.06, DREWNO_C, os_="x")
    for i in range(3):
        kula(0.6 + i * 0.18, 0.3, 1.43, 0.08, CZARNY, seg=6, ringi=4)


def m_brama():
    for sx in (-1.25, 1.25):
        box(sx, 0, 0, 1.3, 1.6, 2.2, CEGLA)
    box(0, 0, 2.0, 3.8, 1.6, 1.0, CEGLA)
    box(0, -0.82, 2.0, 1.2, 0.08, 0.14, KAMIEN)
    for sx in (-0.6, 0.6):
        box(sx, -0.82, 0, 0.14, 0.08, 2.0, KAMIEN)
    box(0, 0, 3.0, 3.9, 1.7, 0.12, TYNK_C)
    attyka(0, -0.85, 3.12, 3.9, kolor=TYNK_C)
    cyl(0, -0.84, 2.45, 0.28, 0.05, BIEL, v=12, rot=(math.pi / 2, 0, 0))
    cyl(0, -0.87, 2.45, 0.16, 0.03, CZERWONY, v=8, rot=(math.pi / 2, 0, 0))
    for i in range(5):  # brona
        box(-0.4 + i * 0.2, 0, 1.3, 0.04, 0.04, 0.7, (60, 60, 66))


def m_mur():
    box(0, 0, 0, 1.0, 0.9, 1.2, CEGLA)
    box(0, 0, 1.2, 1.0, 0.5, 0.25, CEGLA_J)


def m_rusztowanie():
    for sx in (-0.95, 0, 0.95):
        for sy in (-0.95, 0.95):
            box(sx, sy, 0, 0.07, 0.07, 2.0, DREWNO_J)
    for z in (0.65, 1.3, 1.95):
        for sy in (-0.95, 0.95):
            box(0, sy, z, 1.95, 0.06, 0.06, DREWNO)
        box(0, -0.95, z - 0.03, 1.95, 0.35, 0.04, DREWNO_J)


def m_drzewo(wariant):
    cyl(0, 0, 0, 0.13, 1.0, DREWNO_C, v=6)
    if wariant == 2:
        for i, (r, z) in enumerate([(0.85, 0.6), (0.65, 1.3), (0.42, 1.9)]):
            stozek(0, 0, z, r, 0.02, 1.0, ZIELEN_C if i % 2 else (52, 110, 62), v=7)
    else:
        ikosfera(0, 0, 1.45, 0.75, LISCIE, skala=(1, 1, 0.9))
        ikosfera(0.35, 0.2, 1.85, 0.48, (90, 156, 76))
        ikosfera(-0.3, -0.25, 1.15, 0.45, ZIELEN_C)
        if wariant == 1:
            for (x, y, z) in [(0.5, -0.4, 1.4), (-0.4, -0.55, 1.6), (0.1, -0.7, 1.15), (0.6, 0.3, 1.1)]:
                kula(x, y, z, 0.08, (210, 50, 50), seg=6, ringi=4)


def m_skala():
    ikosfera(0, 0, 0.35, 0.6, KAMIEN, skala=(1.2, 1, 0.75))
    ikosfera(0.55, 0.35, 0.22, 0.38, KAMIEN_C, skala=(1, 1.1, 0.8))
    ikosfera(-0.45, 0.45, 0.18, 0.3, (176, 176, 182))


def m_strzalka():
    walec_lezacy(0, -0.2, 0, 0.08, 0.7, ZLOTO, os_="y", v=8)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.22, radius2=0, depth=0.4, location=(0, 0.35, 0),
                                    rotation=(-math.pi / 2, 0, 0))
    _nadaj(bpy.context.active_object, (255, 210, 70), emisja=0.6)


def m_znacznik():
    bpy.ops.mesh.primitive_torus_add(major_radius=0.9, minor_radius=0.07, major_segments=24, minor_segments=6,
                                     location=(0, 0, 0.05))
    _nadaj(bpy.context.active_object, (255, 214, 80), emisja=1.5)


# ================================================================= POSTACIE
POSTACIE = {
    "zamoyski": dict(plaszcz=GRANAT, szata=CZERWONY, pas=ZLOTO, buty=(220, 170, 40), wlosy=(70, 40, 24),
                     czapka="kolpak", czapka_kol=CZERWONY, broda=True, trzyma="kompas", skora=SKORA),
    "morando": dict(plaszcz=(44, 44, 52), szata=(130, 100, 60), pas=(120, 90, 50), buty=(40, 30, 30),
                    wlosy=(50, 36, 30), czapka="beret", czapka_kol=(24, 24, 30), broda=True, trzyma="plan",
                    skora=(232, 186, 140)),
    "szymonowic": dict(plaszcz=(44, 104, 70), szata=(196, 186, 150), pas=(90, 60, 30), buty=(60, 40, 30),
                       wlosy=(130, 90, 50), czapka="biret", czapka_kol=(40, 40, 50), broda=False, trzyma="ksiega",
                       skora=(240, 200, 160)),
    "hagop": dict(plaszcz=(140, 50, 110), szata=(220, 170, 60), pas=(60, 40, 90), buty=(110, 40, 30),
                  wlosy=(30, 24, 20), czapka="futrzana", czapka_kol=(80, 54, 34), broda=True, trzyma="waga",
                  skora=(214, 164, 118)),
}


def m_postac(p, ox=0, oy=0):
    # buty i nogi
    for sx in (-0.11, 0.11):
        box(ox + sx, oy - 0.03, 0, 0.14, 0.24, 0.14, p["buty"])
    # szata (kontusz) — stożek ścięty
    stozek(ox, oy, 0.1, 0.33, 0.22, 0.85, p["plaszcz"], v=10)
    box(ox, oy - 0.25, 0.12, 0.16, 0.06, 0.82, p["szata"], rot=(-0.12, 0, 0))
    cyl(ox, oy, 0.82, 0.235, 0.09, p["pas"], v=10)
    cyl(ox, oy, 0.9, 0.22, 0.38, p["plaszcz"], v=10)
    box(ox, oy - 0.2, 0.9, 0.12, 0.06, 0.38, p["szata"])
    for z in (1.0, 1.1, 1.2):
        kula(ox, oy - 0.235, z, 0.025, ZLOTO, seg=4, ringi=3)
    # ręce
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.07, depth=0.5,
                                            location=(ox + sx * 0.3, oy - 0.06, 1.0), rotation=(0.25, -sx * 0.18, 0))
        _nadaj(bpy.context.active_object, p["plaszcz"])
        kula(ox + sx * 0.33, oy - 0.16, 0.75, 0.07, p["skora"], seg=6, ringi=4)
    # głowa
    cyl(ox, oy, 1.25, 0.08, 0.08, p["skora"], v=8)
    kula(ox, oy, 1.45, 0.19, p["skora"], seg=10, ringi=8, skala=(1, 0.95, 1.05))
    for sx in (-0.07, 0.07):
        box(ox + sx, oy - 0.175, 1.47, 0.04, 0.02, 0.04, CZARNY)
    box(ox, oy - 0.19, 1.41, 0.04, 0.04, 0.06, tuple(int(c * .85) for c in p["skora"]))
    if p["broda"]:
        box(ox, oy - 0.17, 1.36, 0.2, 0.04, 0.035, p["wlosy"])
        box(ox, oy - 0.14, 1.28, 0.12, 0.08, 0.08, p["wlosy"])
    # nakrycie głowy
    c = p["czapka_kol"]
    if p["czapka"] == "kolpak":
        cyl(ox, oy, 1.56, 0.21, 0.1, (110, 74, 42), v=12)
        stozek(ox, oy + 0.02, 1.64, 0.18, 0.15, 0.2, c, v=10)
        kula(ox + 0.1, oy - 0.17, 1.64, 0.04, ZLOTO, seg=6, ringi=4, metal=0.5)
        stozek(ox + 0.12, oy - 0.12, 1.66, 0.03, 0.005, 0.35, BIEL, v=5, rot=(0.25, 0.3, 0))
    elif p["czapka"] == "beret":
        cyl(ox, oy, 1.56, 0.24, 0.1, c, v=12)
        kula(ox, oy, 1.64, 0.2, c, seg=10, ringi=5, skala=(1.1, 1.1, 0.35))
    elif p["czapka"] == "biret":
        box(ox, oy, 1.56, 0.36, 0.36, 0.14, c)
        kula(ox, oy, 1.72, 0.05, CZERWONY, seg=6, ringi=4)
        box(ox, oy + 0.05, 1.3, 0.38, 0.25, 0.2, p["wlosy"])
    elif p["czapka"] == "futrzana":
        cyl(ox, oy, 1.55, 0.23, 0.32, c, v=10)
        cyl(ox, oy, 1.55, 0.24, 0.06, tuple(int(v * .7) for v in c), v=10)
    # przedmiot w dłoni
    hx, hy, hz = ox + 0.36, oy - 0.25, 0.78
    t = p["trzyma"]
    if t == "kompas":
        cyl(hx, hy, hz, 0.11, 0.04, ZLOTO, v=14, metal=0.6, szorstkosc=0.3)
        cyl(hx, hy, hz + 0.04, 0.085, 0.01, BIEL, v=14)
        box(hx, hy - 0.03, hz + 0.05, 0.02, 0.07, 0.01, CZERWONY)
    elif t == "plan":
        walec_lezacy(hx, hy, hz + 0.05, 0.05, 0.45, (240, 228, 196), os_="x", v=8)
    elif t == "ksiega":
        box(hx, hy, hz - 0.05, 0.08, 0.22, 0.28, (120, 40, 40))
    elif t == "waga":
        cyl(hx, hy, hz, 0.015, 0.35, ZLOTO, v=6, metal=0.5)
        box(hx, hy, hz + 0.33, 0.4, 0.02, 0.02, ZLOTO, metal=0.5)
        for sx in (-0.18, 0.18):
            cyl(hx + sx, hy, hz + 0.15, 0.07, 0.02, ZLOTO, v=8, metal=0.5)


# ================================================================= RENDERY (Cycles)
def przygotuj_render(w, h, przezroczyste=True, probki=24):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = probki
    sc.cycles.use_denoising = False  # nie każda kompilacja Blendera ma OpenImageDenoise
    sc.cycles.filter_width = 1.5
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = przezroczyste
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if przezroczyste else "RGB"


def swiat(kolor, sila=1.0):
    w = bpy.data.worlds.new("swiat")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*lin(kolor), 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = sila
    bpy.context.scene.world = w


def slonce(rot=(0.9, 0.2, -0.6), energia=3.5, kolor=(255, 246, 228)):
    l = bpy.data.lights.new("slonce", "SUN")
    l.energy = energia
    l.color = lin(kolor)
    l.angle = 0.1
    o = bpy.data.objects.new("slonce", l)
    o.rotation_euler = rot
    bpy.context.collection.objects.link(o)


def kamera(poz, cel, orto=None, obiektyw=50):
    c = bpy.data.cameras.new("kam")
    if orto:
        c.type = "ORTHO"
        c.ortho_scale = orto
    else:
        c.lens = obiektyw
    o = bpy.data.objects.new("kam", c)
    bpy.context.collection.objects.link(o)
    o.location = poz
    kier = Vector(cel) - Vector(poz)
    o.rotation_euler = kier.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = o


def renderuj(sciezka):
    bpy.context.scene.render.filepath = sciezka
    bpy.ops.render.render(write_still=True)
    print("render:", os.path.basename(sciezka))


def miniatura(nazwa):
    obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    xs = [(obj.matrix_world @ Vector(v)) for v in obj.bound_box]
    srodek = sum(xs, Vector()) / 8
    rozmiar = max((max(v[i] for v in xs) - min(v[i] for v in xs)) for i in range(3))
    przygotuj_render(160, 160, True, 48)
    swiat((200, 210, 230), 0.9)
    slonce()
    d = rozmiar * 2.2
    kamera((srodek.x + d * .55, srodek.y - d, srodek.z + d * .65), srodek, orto=rozmiar * 1.45)
    renderuj(os.path.join(UI, "miniatura_%s.png" % nazwa))


def portret(nazwa):
    przygotuj_render(256, 256, False, 96)
    tlo = {"zamoyski": (200, 170, 120), "morando": (160, 170, 190), "szymonowic": (170, 196, 160),
           "hagop": (210, 170, 190)}[nazwa]
    box(0, 1.5, -1, 6, 0.1, 6, tlo)
    swiat((235, 225, 210), 0.8)
    slonce(rot=(1.0, 0.1, -0.5), energia=3.0)
    kamera((0.55, -2.1, 1.62), (0, 0, 1.38), obiektyw=85)
    renderuj(os.path.join(UI, "portret_%s.png" % nazwa))


def panorama():
    """Panorama Rynku Wielkiego o zachodzie słońca — tło ekranu tytułowego."""
    czysc()
    box(0, 4, -0.1, 80, 60, 0.1, (88, 150, 70))
    box(0, 3, -0.05, 14, 12, 0.06, (178, 166, 150))
    kolory = [(232, 140, 140), (240, 200, 96), (120, 168, 208), (140, 196, 140), (232, 156, 88)]
    for i, x in enumerate([-12, -8, -4, 4, 8, 12, 16, -16]):
        m_kamienica(kolory[i % 5], ox=x, oy=11)
    m_ratusz_przes(0, 9.6)
    for i, x in enumerate([-14, 14]):
        m_kamienica(kolory[(i + 2) % 5], ox=x, oy=4)
    for (x, y, w) in [(-20, 16, 0), (21, 18, 2), (-24, 8, 1), (25, 10, 0), (-7, 20, 2), (6, 22, 0)]:
        m_drzewo_przes(w, x, y)
    for i, (n, x) in enumerate([("zamoyski", -1.2), ("morando", 0.3), ("hagop", 3.4), ("szymonowic", -3.5)]):
        m_postac(POSTACIE[n], ox=x, oy=-2.5 + (i % 2) * 0.4)
    for (x, y) in [(-5.5, 3), (5.2, 4.4)]:
        przesun(m_kram, x, y)
    przygotuj_render(1280, 720, False, 128)
    swiat((250, 190, 150), 0.9)
    slonce(rot=(1.25, 0.15, -0.9), energia=3.2, kolor=(255, 214, 170))
    kamera((3.5, -11.0, 2.4), (0.2, 6, 3.4), obiektyw=30)
    renderuj(os.path.join(UI, "tlo_tytul.png"))


def przesun(fn, x, y, *a):
    przed = set(bpy.context.scene.objects)
    fn(*a)
    for o in bpy.context.scene.objects:
        if o not in przed:
            o.location.x += x
            o.location.y += y


def m_ratusz_przes(x, y):
    przesun(m_ratusz, x, y)


def m_drzewo_przes(w, x, y):
    przesun(m_drzewo, x, y, w)


# ================================================================= MAIN
def main():
    os.makedirs(MODELE, exist_ok=True)
    os.makedirs(UI, exist_ok=True)
    budynki = {
        "dom": m_dom, "tartak": m_tartak, "kamieniolom": m_kamieniolom, "cegielnia": m_cegielnia,
        "kram": m_kram, "palac": m_palac, "ratusz": m_ratusz, "kolegiata": m_kolegiata,
        "akademia": m_akademia, "bastion": m_bastion, "brama": m_brama,
    }
    kolory = [(232, 140, 140), (240, 200, 96), (120, 168, 208), (140, 196, 140), (232, 156, 88)]
    for i, k in enumerate(kolory):
        budynki["kamienica_%d" % i] = (lambda k=k: m_kamienica(k))
    for nazwa, fn in budynki.items():
        czysc()
        fn()
        eksportuj(nazwa)
        if RENDERY and (not nazwa.startswith("kamienica_") or nazwa == "kamienica_1"):
            miniatura("kamienica" if nazwa == "kamienica_1" else nazwa)
    inne = {"mur": m_mur, "rusztowanie": m_rusztowanie, "skala": m_skala, "strzalka": m_strzalka,
            "znacznik": m_znacznik}
    for w in range(3):
        inne["drzewo_%d" % w] = (lambda w=w: m_drzewo(w))
    for nazwa, fn in inne.items():
        czysc()
        fn()
        eksportuj(nazwa)
    for nazwa, p in POSTACIE.items():
        czysc()
        m_postac(p)
        eksportuj("postac_" + nazwa)
        if RENDERY:
            portret(nazwa)
    if RENDERY:
        panorama()
    print("GOTOWE")


main()
