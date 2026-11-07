"""Blender: generuje modele 3D gry „Roman Dmowski. Droga do Wersalu 3D”.

Uruchom (z katalogu dmowski3d):
    blender -b -P blender/generuj_modele.py
Opcje po „--”:
    --bez-renderow   tylko modele .glb (bez portretów, miniatur i tła)

Wynik: godot/modele/*.glb, godot/ui/portret_*.png, godot/ui/miniatura_*.png, godot/ui/tlo_tytul.png
Układ: 1 pole mapy = 2 m, model stoi na z=0, środek podstawy w (0,0), front na -Y.
Narzędzia pomocnicze (box, cyl, dach...) są takie same jak w zamosc3d/blender/generuj_modele.py.
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


def przesun(fn, x, y, *a):
    przed = set(bpy.context.scene.objects)
    fn(*a)
    for o in bpy.context.scene.objects:
        if o not in przed:
            o.location.x += x
            o.location.y += y



# ================================================================= KOLORY 1914–1919
SZARY = (96, 96, 104)
GRAFIT = (54, 54, 62)
BLEKIT = (112, 146, 186)
FELDGRAU = (118, 118, 104)
KREM = (232, 214, 172)
LUPEK = (92, 104, 118)
PIASEK = (190, 166, 120)
WORKI = (176, 156, 112)
CZERWONY_FL = (210, 40, 52)


def flaga(x, y, z0, h=2.2, kolory=(BIEL, CZERWONY_FL), szer=0.7):
    cyl(x, y, z0, 0.035, h, (90, 70, 50), v=6)
    box(x + szer / 2 + 0.03, y, z0 + h - 0.22, szer, 0.03, 0.22, kolory[0])
    box(x + szer / 2 + 0.03, y, z0 + h - 0.44, szer, 0.03, 0.22, kolory[1])


def flaga_fr(x, y, z0, h=2.2):
    cyl(x, y, z0, 0.035, h, (90, 70, 50), v=6)
    for i, k in enumerate([(40, 60, 150), BIEL, CZERWONY_FL]):
        box(x + 0.15 + i * 0.22, y, z0 + h - 0.42, 0.22, 0.03, 0.42, k)


def dach_mansardowy(x, y, z0, sx, sy, h, kolor=LUPEK):
    stozek(x, y, z0, 1, 0.72, h, kolor, v=4, rot=(0, 0, math.pi / 4))
    o = bpy.context.active_object
    o.scale = (sx / 1.414, sy / 1.414, 1)


# ================================================================= POSTACIE
POSTACIE = {
    # Roman Dmowski — ciemny garnitur, melonik, wąsy, teczka z memoriałami
    "dmowski": dict(stroj="garnitur", kolor=GRAFIT, spodnie=GRAFIT, krawat=(120, 30, 40), skora=SKORA,
                    wlosy=(70, 54, 44), fryzura="lysiejace", wasy="male", broda=False, kapelusz="melonik",
                    kapelusz_kol=(30, 28, 30), okulary=False, trzyma="teczka", buty=(30, 24, 22)),
    "hanna": dict(stroj="sukienka", kolor=(40, 60, 110), spodnie=(40, 60, 110), krawat=None, skora=(244, 206, 172),
                  wlosy=(120, 76, 44), fryzura="kok", wasy=None, broda=False, kapelusz=None, okulary=False,
                  trzyma="papiery", buty=(40, 30, 28), bluzka=BIEL),
    "zamoyski": dict(stroj="garnitur", kolor=(150, 140, 120), spodnie=(110, 104, 92), krawat=(40, 50, 90),
                     skora=SKORA, wlosy=(60, 44, 34), fryzura="krotkie", wasy="male", broda=False,
                     kapelusz="cylinder", kapelusz_kol=(30, 28, 30), okulary=False, trzyma="laska", buty=(30, 24, 22)),
    "haller": dict(stroj="mundur", kolor=BLEKIT, spodnie=BLEKIT, krawat=None, skora=(232, 186, 146),
                   wlosy=(90, 80, 70), fryzura="krotkie", wasy="duze", broda=True, kapelusz="rogatywka",
                   kapelusz_kol=BLEKIT, okulary=False, trzyma="szabla", buty=(70, 46, 30)),
    "paderewski": dict(stroj="garnitur", kolor=(28, 28, 34), spodnie=(28, 28, 34), krawat=BIEL, skora=SKORA,
                       wlosy=(200, 150, 92), fryzura="bujne", wasy="male", broda=True, kapelusz=None, okulary=False,
                       trzyma="papiery", buty=(26, 22, 22)),
    "clemenceau": dict(stroj="plaszcz", kolor=(46, 44, 48), spodnie=(46, 44, 48), krawat=(30, 30, 30),
                       skora=(232, 190, 160), wlosy=(236, 236, 236), fryzura="lysiejace", wasy="sumiaste",
                       broda=False, kapelusz="melonik", kapelusz_kol=(60, 58, 54), okulary=False, trzyma="brak",
                       buty=(26, 22, 22), rekawiczki=(150, 150, 150)),
    "wilson": dict(stroj="garnitur", kolor=(34, 38, 60), spodnie=(70, 70, 76), krawat=(30, 30, 40),
                   skora=(240, 204, 176), wlosy=(170, 166, 160), fryzura="krotkie", wasy=None, broda=False,
                   kapelusz="cylinder", kapelusz_kol=(24, 24, 26), okulary=True, trzyma="brak", buty=(26, 22, 22)),
    "pilsudski": dict(stroj="mundur", kolor=FELDGRAU, spodnie=FELDGRAU, krawat=None, skora=(230, 188, 150),
                      wlosy=(100, 90, 80), fryzura="krotkie", wasy="sumiaste", broda=False, kapelusz="maciejowka",
                      kapelusz_kol=FELDGRAU, okulary=False, trzyma="szabla", buty=(40, 30, 24), brwi=True),
}


class Grupa:
    """Zbiera obiekty utworzone w bloku `with` w jedną część z punktem obrotu (staw) — do animacji w Godocie."""

    def __init__(self, nazwa, pivot, aktywna=True):
        self.nazwa, self.pivot, self.aktywna = nazwa, pivot, aktywna

    def __enter__(self):
        self.przed = set(bpy.context.scene.objects)
        return self

    def __exit__(self, *a):
        if not self.aktywna:
            return
        nowe = [o for o in bpy.context.scene.objects if o not in self.przed and o.type == "MESH"]
        polacz(nowe, self.nazwa, self.pivot)


def polacz(obiekty, nazwa, pivot):
    bpy.ops.object.select_all(action="DESELECT")
    for o in obiekty:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obiekty[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if len(obiekty) > 1:
        bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = nazwa
    o.data.name = nazwa
    bpy.context.scene.cursor.location = pivot
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.object.shade_flat()
    o.select_set(False)
    return o


CZESCI = ("noga_l", "noga_p", "reka_l", "reka_p")


def eksportuj_postac(nazwa):
    """Postać z osobnymi częściami (cialo, noga_l/p, reka_l/p) — Godot porusza nimi przy chodzeniu."""
    reszta = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in CZESCI]
    polacz(reszta, "cialo", (0, 0, 0))
    sciezka = os.path.join(MODELE, nazwa + ".glb")
    bpy.ops.export_scene.gltf(filepath=sciezka, export_format="GLB", use_selection=False, export_apply=True,
                              export_yup=True)
    print("model:", nazwa)

PRZECHODNIE = [
    dict(stroj="garnitur", kolor=(90, 80, 70), spodnie=(70, 66, 60), krawat=None, skora=SKORA, wlosy=(80, 60, 40),
         fryzura="krotkie", wasy="male", broda=False, kapelusz="kaszkiet", kapelusz_kol=(70, 66, 60),
         okulary=False, trzyma="brak", buty=(40, 30, 24)),
    dict(stroj="sukienka", kolor=(130, 60, 80), spodnie=(130, 60, 80), krawat=None, skora=(244, 206, 172),
         wlosy=(90, 60, 40), fryzura="kok", wasy=None, broda=False, kapelusz="damski", kapelusz_kol=(230, 220, 200),
         okulary=False, trzyma="brak", buty=(40, 30, 28), bluzka=(236, 226, 214)),
    dict(stroj="garnitur", kolor=(110, 90, 60), spodnie=(80, 70, 56), krawat=None, skora=(244, 206, 172),
         wlosy=(140, 100, 60), fryzura="krotkie", wasy=None, broda=False, kapelusz="kaszkiet",
         kapelusz_kol=(90, 80, 60), okulary=False, trzyma="gazety", buty=(50, 36, 26)),
    dict(stroj="mundur", kolor=BLEKIT, spodnie=BLEKIT, krawat=None, skora=(232, 190, 150), wlosy=(90, 70, 50),
         fryzura="krotkie", wasy="male", broda=False, kapelusz="rogatywka", kapelusz_kol=BLEKIT, okulary=False,
         trzyma="brak", buty=(70, 46, 30)),
    dict(stroj="garnitur", kolor=(60, 60, 70), spodnie=(60, 60, 70), krawat=(150, 30, 40), skora=SKORA,
         wlosy=(70, 54, 44), fryzura="krotkie", wasy="male", broda=False, kapelusz="kaszkiet",
         kapelusz_kol=(50, 50, 56), okulary=False, trzyma="flaga", buty=(30, 24, 22)),
    dict(stroj="garnitur", kolor=(36, 36, 44), spodnie=(36, 36, 44), krawat=(30, 30, 40), skora=(236, 200, 170),
         wlosy=(150, 140, 130), fryzura="lysiejace", wasy="male", broda=False, kapelusz=None, kapelusz_kol=None,
         okulary=False, trzyma="papiery", buty=(26, 22, 22)),
]


def m_postac(p, ox=0, oy=0, czesci=False):
    st = p["stroj"]
    sk = p["skora"]
    # nogi i buty
    wys_butow = 0.36 if st == "mundur" else 0.1
    for sx in (-0.1, 0.1):
        with Grupa("noga_l" if sx < 0 else "noga_p", (ox + sx, oy, 0.78), czesci):
            box(ox + sx, oy - 0.03, 0, 0.13, 0.24, wys_butow, p["buty"])
            if st != "sukienka":
                cyl(ox + sx, oy, wys_butow, 0.08, 0.78 - wys_butow, p["spodnie"], v=8)
    if st == "sukienka":
        stozek(ox, oy, 0.08, 0.32, 0.2, 0.72, p["kolor"], v=12)
    if st == "plaszcz":
        stozek(ox, oy, 0.3, 0.29, 0.22, 0.6, p["kolor"], v=10)
    # tułów
    gora = p.get("bluzka", p["kolor"]) if st == "sukienka" else p["kolor"]
    cyl(ox, oy, 0.76, 0.2, 0.5, gora, v=10)
    if st in ("garnitur", "plaszcz"):
        stozek(ox, oy, 0.62, 0.22, 0.2, 0.16, p["kolor"], v=10)          # poły marynarki
        box(ox, oy - 0.18, 1.0, 0.13, 0.05, 0.26, BIEL)                    # koszula
        if p["krawat"]:
            box(ox, oy - 0.205, 0.98, 0.045, 0.02, 0.26, p["krawat"])
    if st == "mundur":
        box(ox, oy, 0.86, 0.42, 0.42, 0.06, (90, 60, 34))                  # pas
        box(ox + 0.14, oy, 0.86, 0.04, 0.43, 0.4, (90, 60, 34), rot=(0, 0.6, 0))
        for z in (0.95, 1.05, 1.15):
            kula(ox, oy - 0.2, z, 0.022, ZLOTO, seg=4, ringi=3, metal=0.5)
        box(ox, oy, 1.22, 0.3, 0.3, 0.07, p["kolor"])                       # kołnierz
    # ręce
    for s in (-1, 1):
        with Grupa("reka_l" if s < 0 else "reka_p", (ox + s * 0.27, oy - 0.04, 1.22), czesci):
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.065, depth=0.5,
                                                location=(ox + s * 0.27, oy - 0.04, 0.98),
                                                rotation=(0.15, -s * 0.12, 0))
            _nadaj(bpy.context.active_object, gora)
            kula(ox + s * 0.3, oy - 0.08, 0.72, 0.065, p.get("rekawiczki", sk), seg=6, ringi=4)
            if s > 0:
                przedmiot_w_dloni(p, ox, oy)
    # głowa
    cyl(ox, oy, 1.24, 0.075, 0.08, sk, v=8)
    kula(ox, oy, 1.43, 0.18, sk, seg=10, ringi=8, skala=(1, 0.95, 1.05))
    for sx in (-0.065, 0.065):
        box(ox + sx, oy - 0.165, 1.46, 0.035, 0.02, 0.035, CZARNY)
        if p.get("brwi"):
            box(ox + sx, oy - 0.165, 1.51, 0.08, 0.03, 0.035, p["wlosy"])
    box(ox, oy - 0.18, 1.4, 0.04, 0.04, 0.06, tuple(int(c * .86) for c in sk))
    if p["okulary"]:
        for sx in (-0.065, 0.065):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.04, minor_radius=0.008, major_segments=10,
                                             minor_segments=4, location=(ox + sx, oy - 0.185, 1.465),
                                             rotation=(math.pi / 2, 0, 0))
            _nadaj(bpy.context.active_object, (40, 40, 40))
    w = p["wasy"]
    if w == "male":
        box(ox, oy - 0.165, 1.355, 0.16, 0.04, 0.035, p["wlosy"])
    elif w == "duze":
        box(ox, oy - 0.165, 1.35, 0.24, 0.05, 0.05, p["wlosy"])
    elif w == "sumiaste":
        for s in (-1, 1):
            box(ox + s * 0.07, oy - 0.165, 1.32, 0.13, 0.05, 0.06, p["wlosy"], rot=(0, s * 0.45, 0))
    if p["broda"]:
        box(ox, oy - 0.13, 1.26, 0.09, 0.08, 0.1, p["wlosy"])
    f = p["fryzura"]
    if f == "lysiejace":
        for s in (-1, 1):
            kula(ox + s * 0.15, oy + 0.03, 1.43, 0.07, p["wlosy"], seg=6, ringi=4, skala=(0.6, 1.2, 1))
        kula(ox, oy + 0.1, 1.45, 0.14, p["wlosy"], seg=8, ringi=5, skala=(1.1, 0.6, 0.8))
    elif f == "krotkie":
        kula(ox, oy + 0.02, 1.5, 0.185, p["wlosy"], seg=10, ringi=6, skala=(1.02, 1.0, 0.75))
    elif f == "bujne":
        kula(ox, oy + 0.05, 1.5, 0.26, p["wlosy"], seg=10, ringi=7, skala=(1.1, 1.0, 0.85))
    elif f == "kok":
        kula(ox, oy + 0.02, 1.5, 0.19, p["wlosy"], seg=10, ringi=6, skala=(1.02, 1.0, 0.75))
        kula(ox, oy + 0.16, 1.55, 0.09, p["wlosy"], seg=8, ringi=5)
    k = p["kapelusz"]
    c = p.get("kapelusz_kol")
    if k == "melonik":
        cyl(ox, oy, 1.56, 0.25, 0.025, c, v=14)
        kula(ox, oy, 1.58, 0.18, c, seg=12, ringi=6, skala=(1, 1, 0.8))
    elif k == "cylinder":
        cyl(ox, oy, 1.56, 0.26, 0.025, c, v=14)
        cyl(ox, oy, 1.58, 0.17, 0.32, c, v=14)
        cyl(ox, oy, 1.6, 0.175, 0.05, (90, 30, 30), v=14)
    elif k == "rogatywka":
        cyl(ox, oy, 1.55, 0.2, 0.12, c, v=10)
        box(ox, oy, 1.67, 0.32, 0.32, 0.06, c, rot=(0, 0, math.pi / 4))
        box(ox, oy - 0.2, 1.56, 0.26, 0.12, 0.03, (40, 30, 24), rot=(-0.25, 0, 0))
        kula(ox, oy - 0.2, 1.64, 0.03, (230, 230, 230), seg=6, ringi=4)       # orzełek
    elif k == "kaszkiet":
        cyl(ox, oy, 1.55, 0.2, 0.09, c, v=10)
        box(ox, oy - 0.17, 1.56, 0.3, 0.16, 0.03, c, rot=(-0.2, 0, 0))
    elif k == "damski":
        cyl(ox, oy, 1.56, 0.32, 0.025, c, v=14)
        kula(ox, oy, 1.58, 0.15, c, seg=10, ringi=5, skala=(1, 1, 0.7))
        kula(ox + 0.12, oy - 0.1, 1.66, 0.05, (200, 80, 90), seg=6, ringi=4)
    elif k == "maciejowka":
        cyl(ox, oy, 1.55, 0.2, 0.16, c, v=10)
        cyl(ox, oy, 1.7, 0.22, 0.04, c, v=10)
        box(ox, oy - 0.2, 1.56, 0.26, 0.12, 0.03, (40, 30, 24), rot=(-0.25, 0, 0))
        kula(ox, oy - 0.2, 1.64, 0.03, (230, 230, 230), seg=6, ringi=4)
    if p["trzyma"] == "szabla":
        box(ox - 0.26, oy + 0.05, 0.3, 0.03, 0.06, 0.6, (170, 170, 176), rot=(0.25, 0, 0), metal=0.6)
        box(ox - 0.26, oy - 0.02, 0.86, 0.05, 0.12, 0.05, ZLOTO)


def przedmiot_w_dloni(p, ox, oy):
    t = p["trzyma"]
    hx, hy = ox + 0.32, oy - 0.1
    if t == "teczka":
        box(hx + 0.04, hy, 0.42, 0.08, 0.38, 0.28, (110, 64, 34))
        box(hx + 0.04, hy, 0.7, 0.03, 0.14, 0.04, (80, 46, 26))
        kula(hx + 0.08, hy - 0.1, 0.62, 0.02, ZLOTO, seg=4, ringi=3)
    elif t == "papiery":
        box(hx, hy - 0.05, 0.62, 0.05, 0.24, 0.3, BIEL)
    elif t == "laska":
        cyl(hx + 0.03, hy - 0.05, 0.0, 0.02, 0.75, (60, 40, 26), v=6)
        kula(hx + 0.03, hy - 0.05, 0.76, 0.035, ZLOTO, seg=6, ringi=4)
    elif t == "gazety":
        box(hx, hy - 0.05, 0.55, 0.12, 0.3, 0.22, (236, 232, 220))
    elif t == "flaga":
        cyl(hx, hy - 0.05, 0.4, 0.015, 1.2, (90, 70, 50), v=6)
        box(hx + 0.2, hy - 0.05, 1.4, 0.38, 0.02, 0.12, BIEL)
        box(hx + 0.2, hy - 0.05, 1.28, 0.38, 0.02, 0.12, CZERWONY_FL)


# ================================================================= BUDYNKI
def kamienica_miejska(kolor, pietra=3, szer=1.9, dach=DACH, mansarda=False):
    h = pietra * 0.95 + 0.3
    box(0, 0, 0, szer, 1.9, h, kolor)
    box(0, -0.96, 0.95, szer + 0.04, 0.06, 0.08, BIEL)
    for p in range(pietra):
        okna_rzad([-0.45, 0.45] if szer < 2.5 else [-0.9, 0, 0.9], -0.95, 0.35 + p * 0.95, 0.28, 0.5)
    if mansarda:
        dach_mansardowy(0, 0, h, szer + 0.1, 2.0, 0.9, LUPEK)
        for x in (-0.45, 0.45):
            box(x, -0.7, h + 0.15, 0.22, 0.25, 0.32, BIEL)
        box(0, -0.98, h - 0.05, szer, 0.12, 0.05, (40, 40, 44))  # balkon
    else:
        dach_dwuspadowy(0, 0, h, szer + 0.08, 2.0, 0.8, dach)
    return h


def m_kwatera():
    kamienica_miejska((214, 196, 160), pietra=2, szer=1.8)
    box(0, -0.97, 0, 0.36, 0.05, 0.7, DREWNO_C)


def m_biuro():
    box(0, 0, 0, 3.6, 3.2, 2.6, BIEL)
    box(0, -1.62, 1.25, 3.7, 0.08, 0.1, TYNK_C)
    dach_dwuspadowy(0, 0, 2.6, 3.8, 3.4, 1.0, LUPEK, biodrowy=0.8)
    okna_rzad([-1.2, -0.4, 0.4, 1.2], -1.6, 1.55, 0.35, 0.6)
    okna_rzad([-1.2, 1.2], -1.6, 0.4, 0.35, 0.6)
    box(0, -1.62, 0, 0.6, 0.06, 1.05, DREWNO_C)
    box(0, -1.65, 1.08, 1.2, 0.05, 0.22, (40, 56, 100))
    flaga(1.3, -1.7, 2.6, h=1.6)


def m_redakcja():
    box(0, 0.2, 0, 3.6, 2.8, 2.8, (200, 186, 160))
    dach_dwuspadowy(0, 0.2, 2.8, 3.8, 3.0, 0.9, DACH_C)
    box(0, -1.23, 2.0, 2.8, 0.08, 0.55, (30, 30, 36))                     # szyld
    for i in range(7):
        box(-1.1 + i * 0.36, -1.28, 2.13, 0.22, 0.02, 0.28, BIEL)
    box(-0.9, -1.22, 0, 1.4, 0.06, 1.6, (60, 90, 110))                     # witryna
    box(0.9, -1.22, 0, 0.6, 0.06, 1.1, DREWNO_C)
    for i in range(3):                                                      # paczki gazet
        box(1.25, -1.6 + i * 0.05, i * 0.18, 0.5, 0.35, 0.17, (236, 232, 220))
    walec_lezacy(-0.9, -1.45, 0.25, 0.22, 0.9, (60, 60, 66))               # maszyna drukarska


def m_komitet():
    box(0, 0.3, 0, 3.4, 2.6, 2.4, (226, 210, 186))
    dach_dwuspadowy(0, 0.3, 2.4, 3.6, 2.8, 0.9, DACH)
    okna_rzad([-1.1, 1.1], -1.0, 0.9, 0.4, 0.6)
    box(0, -1.02, 0, 0.6, 0.06, 1.05, DREWNO_C)
    box(0, -1.05, 1.75, 2.6, 0.03, 0.22, BIEL)
    box(0, -1.05, 1.53, 2.6, 0.03, 0.22, CZERWONY_FL)
    box(-1.1, -1.5, 0, 1.0, 0.5, 0.75, DREWNO_J)                           # stół kwesty
    box(-1.1, -1.5, 0.75, 0.25, 0.2, 0.25, (190, 40, 40))                  # puszka
    flaga(1.3, -1.5, 0, h=2.6)


def namiot(x, y, sx, sy, h, kolor):
    dach_dwuspadowy(x, y, 0, sx, sy, h, kolor, wzdluz="y")
    box(x, y - sy / 2 - 0.01, 0, 0.35, 0.03, h * 0.6, tuple(int(c * .6) for c in kolor))


def m_werbunek():
    namiot(-0.4, 0.3, 2.4, 2.4, 1.7, (196, 184, 150))
    box(0.9, -1.2, 0, 1.2, 0.6, 0.75, DREWNO_J)
    box(0.9, -1.2, 0.75, 0.5, 0.35, 0.03, BIEL)
    box(-0.6, -1.5, 0, 0.06, 0.06, 1.4, DREWNO)
    box(-0.6, -1.53, 0.7, 0.8, 0.03, 0.7, (232, 220, 190))                 # plakat
    box(-0.6, -1.55, 1.1, 0.5, 0.02, 0.15, CZERWONY_FL)
    flaga(1.5, 0.8, 0, h=2.8)


def m_oboz():
    for x in (-1.9, 0, 1.9):
        namiot(x, 0.4, 1.6, 2.2, 1.4, (150, 150, 110))
    for x in (-1.2, 1.2):
        box(x, -1.5, 0, 0.5, 0.5, 0.45, DREWNO)
    flaga(0, -1.5, 0, h=3.2)
    for i in range(4):  # karabiny w kozłach
        box(-2.4 + i * 0.12, -1.4, 0, 0.03, 0.03, 0.9, (70, 50, 34), rot=(0, 0.25 * (-1) ** i, 0))


def m_szpital():
    namiot(0, 0.2, 3.4, 3.0, 2.0, (238, 236, 228))
    box(0, -1.32, 1.05, 3.0, 0.02, 0.18, (60, 90, 160))
    for x in (-1.2, 1.2):
        box(x, -1.75, 0.25, 0.55, 1.2, 0.08, (180, 170, 150))
        box(x, -1.75, 0.0, 0.05, 1.1, 0.25, DREWNO)


def m_knp_warszawa():
    box(0, 0, 0, 3.6, 3.4, 4.2, (230, 196, 120))
    box(0, -1.72, 1.3, 3.7, 0.08, 0.1, BIEL)
    box(0, -1.72, 2.7, 3.7, 0.08, 0.1, BIEL)
    attyka(0, -1.7, 4.2, 3.7, kolor=(220, 186, 116))
    for row in (1.6, 3.0):
        okna_rzad([-1.2, -0.4, 0.4, 1.2], -1.7, row, 0.34, 0.75)
    box(0, -1.73, 0, 0.8, 0.06, 1.15, DREWNO_C)
    cyl(0, -1.74, 1.0, 0.4, 0.06, DREWNO_C, v=12, rot=(math.pi / 2, 0, 0))
    box(-1.2, -1.74, 0.5, 0.5, 0.04, 0.35, (40, 40, 44))                   # tablica
    flaga(0.9, -1.85, 3.0, h=1.6, szer=1.0)


def m_knp_lozanna():
    box(0, 0, 0, 3.4, 3.0, 2.6, BIEL)
    dach_dwuspadowy(0, 0, 2.6, 4.4, 3.9, 1.5, DACH, wzdluz="y")
    box(0, -1.6, 1.3, 3.0, 0.5, 0.08, DREWNO)                               # balkon
    for x in (-1.4, -0.7, 0, 0.7, 1.4):
        box(x, -1.82, 1.38, 0.05, 0.05, 0.45, DREWNO_C)
    box(0, -1.82, 1.8, 3.0, 0.05, 0.05, DREWNO_C)
    okna_rzad([-1.0, 1.0], -1.5, 0.5, 0.45, 0.6)
    okna_rzad([-1.0, 0, 1.0], -1.5, 1.6, 0.35, 0.55)
    box(0, -1.52, 0, 0.55, 0.06, 1.0, DREWNO_C)
    flaga(1.6, -1.8, 0, h=3.6)


def m_kwatera_glowna():
    box(0, 0.2, 0, 5.2, 2.8, 2.8, (214, 206, 186))
    dach_mansardowy(0, 0.2, 2.8, 5.4, 3.0, 1.3, LUPEK)
    for x in (-2.6, 2.6):
        cyl(x, -0.9, 0, 0.6, 3.3, (204, 196, 176), v=10)
        stozek(x, -0.9, 3.3, 0.68, 0.0, 1.4, LUPEK, v=10)
    okna_rzad([-1.6, -0.8, 0.8, 1.6], -1.2, 0.5, 0.36, 0.75)
    okna_rzad([-1.6, -0.8, 0, 0.8, 1.6], -1.2, 1.7, 0.36, 0.7)
    box(0, -1.22, 0, 0.8, 0.06, 1.3, DREWNO_C)
    flaga(-0.8, -1.6, 0, h=3.2)
    flaga_fr(0.5, -1.6, 0, h=3.2)


def m_pozycja():
    """Okop: wał z zaokrąglonych worków z piaskiem, działo polowe, skrzynie i flaga."""
    for warstwa in range(3):
        n = 10 - warstwa
        for i in range(n):
            a = -1.0 + (i + 0.5 * (warstwa % 2)) * (2.0 / n)
            x, y = math.sin(a) * 1.45, -math.cos(a) * 1.25
            kol = WORKI if (i + warstwa) % 2 else (162, 142, 102)
            kula(x, y, 0.11 + warstwa * 0.19, 0.2, kol, seg=8, ringi=5, skala=(1.25, 0.75, 0.55))
            bpy.context.active_object.rotation_euler = (0, 0, a)
    box(0, 0.35, 0, 3.6, 1.7, 0.04, (110, 86, 58))
    walec_lezacy(0, -0.65, 0.58, 0.08, 1.3, (70, 74, 70), os_="y")
    box(0, -0.05, 0.45, 0.5, 0.6, 0.18, (70, 74, 70))
    box(0, -0.25, 0.55, 0.9, 0.06, 0.55, (90, 96, 88))            # tarcza działa
    for sx in (-0.38, 0.38):
        walec_lezacy(sx, 0.0, 0.34, 0.32, 0.07, DREWNO_C, os_="x", v=14)
    box(0, 0.75, 0.12, 0.1, 1.2, 0.08, DREWNO_C)                  # ogon lawety
    for i in range(2):
        box(1.15, 0.6 + i * 0.05, i * 0.3, 0.6, 0.4, 0.3, DREWNO)
    flaga(-1.25, 0.6, 0, h=2.4)

def m_delegacja():
    kolor = (232, 220, 194)
    box(0, 0, 0, 3.6, 3.4, 3.6, kolor)
    for z in (1.15, 2.35):
        box(0, -1.75, z, 3.6, 0.3, 0.06, (40, 40, 44))                     # balkony
    for row in (0.35, 1.45, 2.6):
        okna_rzad([-1.2, -0.4, 0.4, 1.2], -1.7, row, 0.34, 0.7)
    dach_mansardowy(0, 0, 3.6, 3.7, 3.5, 1.3, LUPEK)
    for x in (-1.0, 0, 1.0):
        box(x, -1.3, 3.8, 0.35, 0.35, 0.5, BIEL)
    box(0, -1.73, 0, 0.8, 0.06, 1.0, DREWNO_C)
    flaga(0.6, -1.95, 2.4, h=1.4, szer=0.9)


def m_memorial():
    box(0, 0.2, 0, 2.6, 0.12, 1.9, DREWNO_C)                               # tablica z mapą
    box(0, 0.12, 0.25, 2.4, 0.04, 1.5, (236, 226, 196))
    for (x, z, w, h, k) in [(-0.6, 1.0, 0.8, 0.5, (210, 120, 110)), (0.3, 1.2, 0.7, 0.4, (130, 170, 120)),
                            (0.6, 0.6, 0.6, 0.5, (200, 190, 110)), (-0.3, 0.5, 0.6, 0.4, (130, 160, 200))]:
        box(x, 0.09, z, w, 0.03, h, k)
    box(0, -0.9, 0, 1.0, 0.6, 0.9, DREWNO)                                 # pulpit
    for i in range(3):
        box(0.05 * i, -0.9, 0.9 + i * 0.05, 0.6, 0.45, 0.05, BIEL)
    flaga(1.1, -0.6, 0, h=2.2)


# ================================================================= DEKORACJE
def m_kamienica_wwa(i):
    kamienica_miejska([(214, 170, 120), (196, 140, 110), (226, 206, 150)][i], pietra=3, szer=1.95,
                      dach=[DACH, DACH_C, (150, 80, 50)][i])


def m_kamienica_paryz(i):
    kamienica_miejska([(232, 220, 194), (222, 208, 180)][i], pietra=4, szer=1.95, mansarda=True)


def m_willa(i):
    box(0, 0, 0, 1.8, 1.8, 2.0, [BIEL, (236, 222, 196)][i])
    dach_dwuspadowy(0, 0, 2.0, 2.3, 2.3, 1.1, [DACH, (110, 70, 50)][i], wzdluz="y")
    okna_rzad([-0.45, 0.45], -0.9, 0.9, 0.3, 0.45)
    box(0, -1.0, 0.85, 1.6, 0.25, 0.05, DREWNO)


def m_dom_fr(i):
    box(0, 0, 0, 1.8, 1.8, 1.6, [(206, 196, 176), (190, 176, 150)][i])
    dach_dwuspadowy(0, 0, 1.6, 2.1, 2.1, 0.9, [DACH_C, LUPEK][i])
    okna_rzad([-0.45, 0.45], -0.9, 0.6, 0.3, 0.4)


def m_zamek():
    box(0, 0, 0, 6.0, 5.0, 3.6, (214, 120, 96))
    box(0, -2.52, 1.7, 6.1, 0.08, 0.12, BIEL)
    dach_dwuspadowy(0, 0, 3.6, 6.2, 5.2, 1.6, DACH_C, biodrowy=1.5)
    for row in (0.5, 2.1):
        okna_rzad([-2.3, -1.5, -0.7, 0.7, 1.5, 2.3], -2.5, row, 0.36, 0.8)
    box(0, -2.0, 0, 1.6, 1.6, 6.0, (214, 120, 96))                         # wieża zegarowa
    cyl(0, -2.82, 4.6, 0.45, 0.05, BIEL, v=16, rot=(math.pi / 2, 0, 0))
    box(0, -2.86, 4.6, 0.04, 0.03, 0.35, CZARNY)
    stozek(0, -2.0, 6.0, 1.0, 0.2, 1.4, (60, 90, 80), v=8)
    stozek(0, -2.0, 7.4, 0.25, 0.0, 1.2, (60, 90, 80), v=8)
    kula(0, -2.0, 8.6, 0.1, ZLOTO, metal=0.6)
    box(0, -2.83, 0, 0.9, 0.06, 1.4, DREWNO_C)


def m_kolumna():
    box(0, 0, 0, 1.4, 1.4, 0.8, KAMIEN)
    box(0, 0, 0.8, 1.0, 1.0, 1.0, (176, 176, 180))
    cyl(0, 0, 1.8, 0.3, 5.2, (196, 176, 170), v=12)
    box(0, 0, 7.0, 0.8, 0.8, 0.3, KAMIEN)
    cyl(0, 0, 7.3, 0.18, 0.9, (90, 120, 100), v=8, metal=0.4)              # król z brązu
    kula(0, 0, 8.35, 0.17, (90, 120, 100), metal=0.4)
    box(0.35, -0.1, 8.0, 0.08, 0.08, 1.0, (90, 120, 100), rot=(0, 0.3, 0)) # krzyż
    box(-0.35, -0.1, 7.7, 0.5, 0.06, 0.06, (90, 120, 100))                 # szabla


def m_katedra():
    box(0, 0.6, 0, 4.0, 4.6, 4.2, (160, 154, 140))
    dach_dwuspadowy(0, 0.6, 4.2, 4.2, 4.8, 2.6, (80, 90, 96), wzdluz="y")
    box(0, -2.0, 0, 2.2, 1.8, 7.0, (170, 164, 150))
    stozek(0, -2.0, 7.0, 1.5, 0.0, 3.4, (80, 96, 96), v=8)
    cyl(0, -2.92, 3.6, 0.55, 0.05, (60, 110, 170), v=16, rot=(math.pi / 2, 0, 0))
    box(0, -2.92, 0, 1.0, 0.06, 2.0, DREWNO_C)
    for sy in (-0.6, 0.8, 2.2):
        for sx in (-2.02, 2.02):
            box(sx, sy, 1.4, 0.05, 0.5, 1.8, (60, 100, 150))


def m_wieza_eiffla():
    """Wieża Eiffla: 4 zbiegające się nogi z kratownicą, łuki, 3 tarasy i iglica."""
    br = (124, 88, 62)
    br2 = (150, 110, 78)

    def noga(sx, sy, z0, z1, r0, r1, grub):
        # słup od (r0,r0,z0) do (r1,r1,z1) w narożniku (sx, sy)
        a = Vector((sx * r0, sy * r0, z0))
        b = Vector((sx * r1, sy * r1, z1))
        d = b - a
        bpy.ops.mesh.primitive_cube_add(size=1, location=(a + b) / 2)
        o = bpy.context.active_object
        o.scale = (grub, grub, d.length)
        o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        _nadaj(o, br)

    for sx in (-1, 1):
        for sy in (-1, 1):
            for dx in (-0.25, 0.25):
                noga(sx, sy, 0, 5.0, 3.0 + dx, 1.55 + dx * 0.6, 0.22)
            for z in (1.2, 2.5, 3.8):            # kratownica między słupkami nogi
                f = z / 5.0
                r = 3.0 + (1.55 - 3.0) * f
                box(sx * r, sy * r, z, 0.7 - f * 0.25, 0.7 - f * 0.25, 0.08, br2, rot=(0, 0, math.pi / 4))
    for sx, sy, rot in [(0, -1, 0), (0, 1, 0), (-1, 0, math.pi / 2), (1, 0, math.pi / 2)]:   # łuki
        bpy.ops.mesh.primitive_torus_add(major_radius=2.05, minor_radius=0.16, major_segments=20, minor_segments=4,
                                         location=(sx * 2.5, sy * 2.5, 1.2), rotation=(math.pi / 2, 0, rot))
        o = bpy.context.active_object
        o.scale = (1, 0.75, 1)
        _nadaj(o, br)
    box(0, 0, 4.9, 4.2, 4.2, 0.4, br2)                      # 1. taras
    for z in (5.3,):
        for sx in (-1, 1):
            box(sx * 2.05, 0, z, 0.06, 4.2, 0.3, br)
            box(0, sx * 2.05, z, 4.2, 0.06, 0.3, br)
    for sx in (-1, 1):
        for sy in (-1, 1):
            noga(sx, sy, 5.3, 10.6, 1.45, 0.62, 0.18)
    for z in (6.8, 8.6):
        f = (z - 5.3) / 5.3
        r = 1.45 + (0.62 - 1.45) * f
        box(0, 0, z, r * 2 + 0.2, r * 2 + 0.2, 0.08, br2)
    box(0, 0, 10.6, 1.7, 1.7, 0.3, br2)                     # 2. taras
    for sx in (-1, 1):
        for sy in (-1, 1):
            noga(sx, sy, 10.9, 17.0, 0.62, 0.18, 0.14)
    for z in (12.5, 14.2, 15.6):
        f = (z - 10.9) / 6.1
        r = 0.62 + (0.18 - 0.62) * f
        box(0, 0, z, r * 2 + 0.12, r * 2 + 0.12, 0.06, br2)
    box(0, 0, 17.0, 0.7, 0.7, 0.5, br2)                     # szczyt
    cyl(0, 0, 17.5, 0.06, 1.8, br, v=6)
    kula(0, 0, 19.3, 0.08, (220, 60, 60), emisja=0.8)

def m_quai_dorsay():
    box(0, 0, 0, 11.4, 5.4, 4.0, (232, 220, 190))
    dach_mansardowy(0, 0, 4.0, 11.6, 5.6, 1.6, LUPEK)
    for x in [-4.8 + i * 0.8 for i in range(13)]:
        okna_rzad([x], -2.7, 0.6, 0.36, 1.0)
        okna_rzad([x], -2.7, 2.4, 0.36, 0.9)
    for x in (-1.2, -0.4, 0.4, 1.2):
        cyl(x, -2.95, 0, 0.16, 3.4, BIEL, v=10)
    box(0, -2.95, 3.4, 3.2, 0.5, 0.4, BIEL)
    v = [(-1.7, -3.2, 3.8), (1.7, -3.2, 3.8), (0, -3.2, 4.7), (-1.7, -2.7, 3.8), (1.7, -2.7, 3.8), (0, -2.7, 4.7)]
    siatka("fronton", v, [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], BIEL)
    flaga_fr(4.5, -2.9, 4.0, h=2.0)


def m_wersal():
    kol = (234, 222, 196)
    box(0, 1.5, 0, 14.0, 4.0, 4.4, kol)
    for sx in (-1, 1):
        box(sx * 5.6, -3.0, 0, 2.8, 6.0, 4.0, kol)
    box(0, 1.5, 4.4, 14.2, 4.2, 0.3, (220, 204, 170))
    attyka(0, -0.5, 4.7, 14.0, kolor=(220, 204, 170), odstep=0.9)
    for sx in (-1, 1):
        dach_mansardowy(sx * 5.6, -3.0, 4.0, 3.0, 6.2, 1.4, LUPEK)
    for x in [-6.3 + i * 0.9 for i in range(15)]:
        okna_rzad([x], -0.52, 0.5, 0.42, 1.4)
        okna_rzad([x], -0.52, 2.6, 0.42, 1.1)
    for x in (-1.4, 0, 1.4):
        cyl(x, -0.8, 0, 0.2, 4.4, BIEL, v=10)
    box(0, -0.8, 4.4, 4.0, 0.4, 0.4, ZLOTO, metal=0.5)
    box(0, -7.0, -0.02, 10, 6, 0.04, (196, 186, 160))                     # dziedziniec


def m_gora():
    stozek(0, 0, 0, 3.4, 0.0, 6.8, (150, 156, 170), v=8)
    stozek(1.2, 0.8, 0, 2.2, 0.0, 4.4, (136, 144, 156), v=7)
    stozek(0, 0, 3.4, 1.85, 0.0, 3.45, (250, 252, 255), v=8)
    stozek(1.2, 0.8, 2.4, 1.05, 0.0, 2.05, (250, 252, 255), v=7)


def m_lej():
    bpy.ops.mesh.primitive_torus_add(major_radius=0.7, minor_radius=0.25, major_segments=10, minor_segments=5,
                                     location=(0, 0, 0.02))
    o = bpy.context.active_object
    o.scale = (1, 1, 0.5)
    _nadaj(o, (96, 76, 52))
    cyl(0, 0, -0.02, 0.6, 0.04, (70, 56, 40), v=10)
    box(0.9, 0.4, 0, 0.12, 0.12, 0.7, (70, 56, 40), rot=(0.2, 0.15, 0))


def m_snopek():
    stozek(0, 0, 0, 0.3, 0.08, 0.8, (220, 190, 90), v=7)
    cyl(0, 0, 0.35, 0.18, 0.06, (180, 150, 70), v=7)


def m_latarnia():
    cyl(0, 0, 0, 0.05, 2.4, (40, 44, 40), v=6)
    box(0, 0, 2.4, 0.22, 0.22, 0.3, (250, 230, 160), emisja=0.8)
    stozek(0, 0, 2.7, 0.18, 0.0, 0.18, (40, 44, 40), v=4)



# ================================================================= POJAZDY I ŻYCIE MIASTA
def kolo(x, y, z, r, kolor=(40, 34, 30)):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.04, major_segments=14, minor_segments=4,
                                     location=(x, y, z), rotation=(0, math.pi / 2, 0))
    _nadaj(bpy.context.active_object, kolor)
    walec_lezacy(x, y, z, 0.05, 0.08, kolor, os_="x", v=6)


def kon(x, y, kolor=(110, 74, 46)):
    box(x, y, 0.75, 0.42, 1.25, 0.5, kolor)                       # tułów
    for sx in (-0.15, 0.15):
        for sy in (-0.45, 0.45):
            box(x + sx, y + sy, 0, 0.12, 0.12, 0.8, tuple(int(c * .8) for c in kolor))
    box(x, y - 0.75, 1.05, 0.22, 0.45, 0.25, kolor, rot=(0.7, 0, 0))   # szyja
    box(x, y - 0.98, 1.25, 0.2, 0.42, 0.2, kolor)                  # łeb
    box(x, y - 0.6, 1.3, 0.06, 0.4, 0.15, (40, 30, 24))            # grzywa
    box(x, y + 0.66, 0.85, 0.08, 0.1, 0.45, (40, 30, 24), rot=(-0.4, 0, 0))   # ogon


def m_dorozka():
    kon(0, -1.0)
    box(0, 1.0, 0.55, 1.0, 1.4, 0.5, (40, 40, 46))                 # nadwozie
    box(0, 1.35, 1.05, 1.0, 0.7, 0.6, (40, 40, 46))                # buda
    box(0, 0.45, 1.05, 0.5, 0.3, 0.08, (60, 50, 40))               # kozioł
    for sy in (0.5, 1.5):
        for sx in (-0.55, 0.55):
            kolo(sx, sy, 0.38, 0.38)
    box(0, -0.1, 0.6, 0.06, 1.4, 0.06, DREWNO_C)                   # dyszel
    przed = set(bpy.context.scene.objects)
    m_postac(dict(stroj="plaszcz", kolor=(50, 50, 40), spodnie=(50, 50, 40), krawat=None, skora=SKORA,
                  wlosy=(80, 60, 40), fryzura="krotkie", wasy="duze", broda=False, kapelusz="melonik",
                  kapelusz_kol=(30, 30, 30), okulary=False, trzyma="brak", buty=(30, 24, 22)), 0, 0.45)
    for o in bpy.context.scene.objects:
        if o not in przed:
            o.location.z += 0.75          # woźnica siedzi na koźle


def m_automobil():
    kol = (30, 50, 40)
    box(0, 0, 0.45, 1.3, 2.6, 0.45, kol)                           # podwozie
    box(0, -0.85, 0.9, 1.1, 0.8, 0.35, kol)                        # maska
    box(0, -1.32, 0.55, 0.9, 0.06, 0.6, (150, 150, 150), metal=0.6)   # chłodnica
    box(0, 0.45, 0.9, 1.25, 1.3, 0.35, (60, 40, 30))               # siedzenia
    box(0, 0.4, 1.7, 1.3, 1.5, 0.05, (30, 30, 30))                 # dach
    for sx in (-0.6, 0.6):
        for sy in (-0.3, 1.1):
            box(sx, sy, 0.9, 0.04, 0.04, 0.8, (30, 30, 30))
    for sx in (-0.5, 0.5):
        kula(sx, -1.33, 0.95, 0.09, (250, 240, 200), emisja=0.6)   # lampy
    for sx in (-0.7, 0.7):
        for sy in (-0.8, 0.85):
            kolo(sx, sy, 0.4, 0.4, (30, 30, 30))


def m_tramwaj():
    kon(0, -2.2, (150, 120, 90))
    box(0, 0.6, 0.35, 1.5, 3.4, 0.25, (60, 50, 40))
    box(0, 0.6, 0.6, 1.5, 3.2, 1.3, (190, 160, 80))                # wagon
    box(0, 0.6, 1.9, 1.65, 3.5, 0.12, (90, 60, 40))                # dach
    for sy in (-0.4, 0.2, 0.8, 1.4):
        for sx in (-0.76, 0.76):
            box(sx, sy, 1.1, 0.04, 0.42, 0.5, OKNO)
    box(0, -1.05, 0.6, 1.0, 0.04, 0.12, (150, 40, 40))             # tablica
    for sy in (-0.4, 1.6):
        for sx in (-0.6, 0.6):
            kolo(sx, sy, 0.3, 0.3)
    box(0, -1.4, 0.55, 0.06, 1.0, 0.06, DREWNO_C)


def m_ptak():
    kula(0, 0, 0, 0.08, (60, 60, 66), seg=6, ringi=4, skala=(1, 1.6, 0.8))
    for s in (-1, 1):
        box(s * 0.22, 0.02, 0.02, 0.36, 0.12, 0.02, (60, 60, 66), rot=(0, s * 0.35, 0))


def m_dym():
    kula(0, 0, 0, 0.35, (200, 200, 205), seg=8, ringi=5)


# ================================================================= DEKORACJE PRZERYWNIKÓW
def m_sala_lustrzana():
    """Sala Lustrzana pałacu w Wersalu: 17 okien naprzeciw 17 arkad z lustrami, złocenia, żyrandole."""
    dl, sz, wys = 34.0, 9.0, 8.0
    box(0, 0, -0.1, sz, dl, 0.1, (150, 104, 66))                   # parkiet
    for i in range(0, 34, 2):
        box(0, -dl / 2 + i + 0.5, -0.05, sz, 0.08, 0.06, (120, 80, 50))
    box(0, 0, wys, sz + 0.4, dl, 0.3, (200, 170, 110))             # sklepienie
    for i in range(8):
        box(0, -dl / 2 + 2 + i * 4.2, wys - 0.05, sz * 0.7, 3.0, 0.06,
            [(160, 120, 90), (110, 130, 170), (190, 150, 100)][i % 3])   # malowidła
    for strona, kol_wn in ((-1, (190, 214, 236)), (1, (214, 224, 236))):
        x = strona * sz / 2
        box(x + strona * 0.15, 0, 0, 0.3, dl, wys, (232, 220, 196))  # ściana
        for i in range(17):
            y = -dl / 2 + 1.0 + i * 2.0
            box(x, y, 0.6, 0.12, 1.3, 4.6, kol_wn, emisja=0.35 if strona < 0 else 0.15,
                metal=0.0 if strona < 0 else 0.6, szorstkosc=0.15)   # okno / lustro
            cyl(x, y, 4.6, 0.65, 0.12, kol_wn, v=12, rot=(0, math.pi / 2, 0), emisja=0.35 if strona < 0 else 0.15)
            box(x - strona * 0.05, y + 1.0, 0, 0.2, 0.25, 6.5, (230, 190, 90), metal=0.5)   # pilaster
    for i in range(6):                                                # żyrandole
        y = -dl / 2 + 4 + i * 5.4
        cyl(0, y, 5.2, 0.03, wys - 5.2, ZLOTO, v=6)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.6, minor_radius=0.05, major_segments=12, minor_segments=4,
                                         location=(0, y, 5.2))
        _nadaj(bpy.context.active_object, ZLOTO)
        for k in range(8):
            a = k * math.pi / 4
            kula(math.cos(a) * 0.6, y + math.sin(a) * 0.6, 5.35, 0.08, (255, 240, 190), emisja=2.0)
    box(0, 2, 0, 2.2, 6.0, 0.8, (60, 100, 70))                        # stół traktatu
    box(0, 2, 0.8, 2.3, 6.1, 0.04, (40, 80, 50))
    for i in range(3):
        box(0.2 * (i - 1), 0.5 + i * 1.6, 0.84, 0.4, 0.55, 0.02, BIEL)   # dokumenty
    for sy in range(6):
        for sx in (-1.5, 1.5):
            y = -0.4 + sy * 1.0
            box(sx, y, 0, 0.5, 0.5, 0.48, (130, 40, 40))
            box(sx + (0.22 if sx > 0 else -0.22), y, 0.48, 0.08, 0.5, 0.6, (130, 40, 40))


def m_sala_rady():
    """Salon na Quai d'Orsay, w którym obradowała Rada Dziesięciu (styczeń 1919)."""
    box(0, 0, -0.1, 12, 10, 0.1, (140, 96, 60))
    box(0, 0, 5.5, 12, 10, 0.2, (226, 214, 190))
    for x in (-6, 6):
        box(x, 0, 0, 0.2, 10, 5.5, (226, 210, 180))
    box(0, 5, 0, 12, 0.2, 5.5, (226, 210, 180))
    for x in (-3.6, 0, 3.6):
        box(x, 4.88, 1.0, 1.6, 0.06, 3.4, (190, 214, 236), emisja=0.4)   # okna
    box(0, 4.8, 3.9, 1.6, 0.1, 1.1, (230, 220, 200))                    # zegar nad kominkiem
    cyl(0, 4.72, 4.2, 0.35, 0.05, BIEL, v=16, rot=(math.pi / 2, 0, 0))
    box(0, 4.8, 0, 2.2, 0.5, 1.3, (220, 210, 196))                      # kominek
    box(0, 4.6, 0.1, 1.2, 0.1, 0.8, (40, 30, 26))
    box(0, 1.0, 0, 7.0, 2.4, 0.78, DREWNO_C)                            # stół obrad
    box(0, 1.0, 0.78, 7.1, 2.5, 0.04, (40, 80, 50))
    for x in [-3 + i * 1.2 for i in range(6)]:
        box(x, 2.6, 0, 0.5, 0.5, 0.48, (110, 40, 40))
        box(x, 2.85, 0.48, 0.5, 0.08, 0.6, (110, 40, 40))
        box(x, 1.6, 0.82, 0.35, 0.45, 0.02, BIEL)
    box(-4.8, -1.5, 0, 0.1, 0.1, 1.6, DREWNO)                           # sztaluga z mapą
    box(-4.8, -1.55, 1.2, 2.2, 0.06, 1.6, (236, 226, 196))
    for (x, z, w, h, k) in [(-5.3, 1.9, 0.7, 0.5, (210, 120, 110)), (-4.6, 2.1, 0.6, 0.6, (130, 170, 120)),
                            (-4.5, 1.5, 0.7, 0.4, (200, 190, 110))]:
        box(x, -1.6, z, w, 0.03, h, k)
    flaga_fr(5.0, 4.4, 0, h=3.2)


# ================================================================= RENDERY
TLA_PORTRETOW = {"dmowski": (190, 170, 140), "hanna": (180, 196, 214), "zamoyski": (200, 186, 160),
                 "haller": (170, 186, 210), "paderewski": (200, 176, 150), "clemenceau": (190, 196, 206),
                 "wilson": (176, 190, 200), "pilsudski": (186, 180, 160)}


def portret(nazwa):
    przygotuj_render(256, 256, False, 96)
    box(0, 1.5, -1, 6, 0.1, 6, TLA_PORTRETOW[nazwa])
    swiat((235, 225, 210), 0.8)
    slonce(rot=(1.0, 0.1, -0.5), energia=3.0)
    kamera((0.5, -2.1, 1.6), (0, 0, 1.4), obiektyw=80)
    renderuj(os.path.join(UI, "portret_%s.png" % nazwa))


def panorama():
    """Paryż 1919: delegaci przed Quai d'Orsay, w tle wieża Eiffla — tło ekranu tytułowego."""
    czysc()
    box(0, 6, -0.1, 90, 70, 0.1, (90, 140, 80))
    box(0, 2, -0.05, 30, 14, 0.06, (178, 168, 150))
    przesun(m_quai_dorsay, 0, 9)
    przesun(m_wieza_eiffla, -13, 20)
    for i, x in enumerate([-12, -9.6, 9.6, 12]):
        przesun(m_kamienica_paryz, x, 8.5, i % 2)
    for (x, y, w) in [(-18, 12, 0), (17, 13, 1), (-20, 4, 2), (19, 5, 0), (-15, 16, 1)]:
        przesun(m_drzewo, x, y, w)
    for x in (-4.5, 4.5):
        przesun(flaga, 0, 0, x, 4.5, 0, 3.6)
    for (n, x, y) in [("hanna", -3.6, -2.2), ("haller", -2.2, -1.6), ("dmowski", -0.6, -2.6),
                      ("paderewski", 0.9, -2.3), ("clemenceau", 2.6, -1.4), ("wilson", 3.9, -1.9)]:
        m_postac(POSTACIE[n], ox=x, oy=y)
    przygotuj_render(1280, 720, False, 128)
    swiat((206, 220, 236), 0.9)
    slonce(rot=(1.15, 0.1, -0.7), energia=3.4, kolor=(255, 236, 210))
    kamera((1.5, -11.5, 2.6), (0.3, 6, 3.2), obiektyw=30)
    renderuj(os.path.join(UI, "tlo_tytul.png"))


# ================================================================= MAIN
def podglad(nazwy, katalog):
    """Szybki podgląd wybranych modeli (render miniatur do wskazanego katalogu)."""
    global UI
    UI = katalog
    for n in nazwy:
        czysc()
        globals()["m_" + n]()
        scal(n)
        miniatura(n)


def main():
    if "--podglad" in ARGS:
        podglad(ARGS[ARGS.index("--podglad") + 1].split(","), ARGS[ARGS.index("--podglad") + 2])
        return
    os.makedirs(MODELE, exist_ok=True)
    os.makedirs(UI, exist_ok=True)
    budynki = {"kwatera": m_kwatera, "biuro": m_biuro, "redakcja": m_redakcja, "komitet": m_komitet,
               "werbunek": m_werbunek, "oboz": m_oboz, "szpital": m_szpital, "knp_warszawa": m_knp_warszawa,
               "knp_lozanna": m_knp_lozanna, "kwatera_glowna": m_kwatera_glowna, "pozycja": m_pozycja,
               "delegacja": m_delegacja, "memorial": m_memorial}
    for nazwa, fn in budynki.items():
        czysc()
        fn()
        eksportuj(nazwa)
        if RENDERY:
            miniatura(nazwa)
    inne = {"rusztowanie": m_rusztowanie, "skala": m_skala, "strzalka": m_strzalka, "znacznik": m_znacznik,
            "zamek": m_zamek, "kolumna": m_kolumna, "katedra": m_katedra, "wieza_eiffla": m_wieza_eiffla,
            "quai_dorsay": m_quai_dorsay, "wersal": m_wersal, "gora": m_gora, "lej": m_lej, "snopek": m_snopek,
            "latarnia": m_latarnia, "dorozka": m_dorozka, "automobil": m_automobil, "tramwaj": m_tramwaj,
            "ptak": m_ptak, "dym": m_dym, "sala_lustrzana": m_sala_lustrzana, "sala_rady": m_sala_rady}
    for w in range(3):
        inne["drzewo_%d" % w] = (lambda w=w: m_drzewo(w))
        inne["kamienica_wwa_%d" % w] = (lambda w=w: m_kamienica_wwa(w))
    for w in range(2):
        inne["kamienica_paryz_%d" % w] = (lambda w=w: m_kamienica_paryz(w))
        inne["willa_%d" % w] = (lambda w=w: m_willa(w))
        inne["dom_fr_%d" % w] = (lambda w=w: m_dom_fr(w))
    for nazwa, fn in inne.items():
        czysc()
        fn()
        eksportuj(nazwa)
    for i, p in enumerate(PRZECHODNIE):
        czysc()
        m_postac(p, czesci=True)
        eksportuj_postac("przechodzien_%d" % i)
    for nazwa, p in POSTACIE.items():
        czysc()
        m_postac(p, czesci=True)
        eksportuj_postac("postac_" + nazwa)
        if RENDERY:
            portret(nazwa)
    if RENDERY:
        panorama()
    print("GOTOWE")


main()
