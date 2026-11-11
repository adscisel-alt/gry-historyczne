"""Blender: generuje modele 3D i rendery gry „Roman Empire — od narodzin przez rozkwit aż po upadek”.

Uruchom (z katalogu rzym3d):
    blender -b -P blender/generuj_modele.py
albo modułem bpy (Blender 5.x w Pythonie):
    python blender/generuj_modele.py
Opcje po „--”:
    --bez-renderow     tylko modele .glb (bez portretów, kart, ikon budynków i teł)
    --tylko a,b,c      tylko wymienione pozycje (nazwy modeli; także tlo_tytul, tlo_bitwy, ikona)

Wynik: godot/modele/*.glb, godot/ui/portret_*.png, godot/ui/karta_*.png, godot/ui/budynek_*.png,
       godot/ui/tlo_tytul.png, godot/ui/tlo_bitwy.png, godot/icon.png
Układ (AGENTS.md, „Kontrakt modeli”): 1 pole mapy = 2 m, model stoi na z=0, środek podstawy w (0,0),
front na -Y. Budynek mieści się w kwadracie 1,8 × 1,8 m i ma ≤ 3 m wysokości.
Narzędzia pomocnicze (box, cyl, kula, mat...) jak w dmowski3d/blender/generuj_modele.py.
"""
import math
import os
import sys
import time

import bpy  # najpierw bpy: w module bpy dopiero on udostępnia bmesh
import bmesh
from mathutils import Matrix, Vector

TU = os.path.dirname(os.path.abspath(__file__))
GODOT = os.path.normpath(os.path.join(TU, "..", "godot"))
MODELE = os.path.join(GODOT, "modele")
UI = os.path.join(GODOT, "ui")
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDERY = "--bez-renderow" not in ARGS
TYLKO = set(ARGS[ARGS.index("--tylko") + 1].split(",")) if "--tylko" in ARGS else None


def chce(nazwa):
    return TYLKO is None or nazwa in TYLKO


# ----------------------------------------------------------------- kolory (sRGB)
TERAKOTA = (198, 92, 54)
TERAKOTA_C = (160, 66, 40)
MARMUR = (242, 238, 228)
MARMUR_C = (212, 206, 194)
TRAWERTYN = (222, 208, 174)
TRAWERTYN_C = (188, 172, 138)
TYNK = (240, 230, 206)
CEGLA = (178, 88, 60)
CEGLA_J = (206, 124, 86)
DREWNO = (128, 84, 48)
DREWNO_J = (176, 128, 80)
DREWNO_C = (88, 56, 32)
STRZECHA = (204, 172, 96)
STRZECHA_C = (162, 128, 68)
GLINA = (176, 140, 98)
ZIEMIA = (132, 98, 64)
ZIEMIA_J = (160, 124, 84)
PIASEK = (218, 196, 146)
KAMIEN = (150, 148, 142)
KAMIEN_C = (110, 106, 102)
KAMIEN_J = (186, 182, 172)
WODA = (64, 128, 176)
OTWOR = (44, 34, 30)
OKNO = (40, 36, 44)
ZLOTO = (232, 182, 58)
BRAZ = (186, 128, 62)
BRAZ_C = (120, 86, 50)
STAL = (172, 176, 184)
STAL_C = (120, 124, 132)
ZIELEN = (78, 136, 64)
ZIELEN_C = (44, 92, 52)
TRAWA = (112, 156, 72)
LISCIE_OL = (128, 146, 96)
CZERWIEN = (176, 34, 38)
CZERWIEN_C = (130, 26, 30)
PURPURA = (118, 28, 92)
FIOLET = (104, 58, 156)
FIOLET_C = (74, 40, 116)
BIEL = (246, 242, 232)
KREM = (232, 216, 180)
CZARNY = (26, 20, 24)
SKORA = (236, 190, 150)
SKORA_J = (244, 206, 172)
SKORA_C = (196, 146, 104)
SANDAL = (110, 70, 40)
FUTRO = (124, 100, 74)
FUTRO_J = (170, 150, 120)
NIEBIESKI = (52, 84, 150)
ZOLTY = (240, 196, 60)

_mat = {}


def lin(c):
    return tuple((v / 255) ** 2.2 for v in c)


def mat(kolor, emisja=0.0, metal=0.0, szorstkosc=0.85):
    klucz = (kolor, emisja, metal, szorstkosc)
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
    m.diffuse_color = (*lin(kolor), 1)
    _mat[klucz] = m
    return m


def metal_kw(kolor):
    return dict(metal=0.55, szorstkosc=0.4) if kolor in (ZLOTO, BRAZ, STAL) else {}


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


def walec_lezacy(x, y, z, r, dl, kolor, os_="x", v=10, **kw):
    rot = (0, math.pi / 2, 0) if os_ == "x" else (math.pi / 2, 0, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=dl, location=(x, y, z), rotation=rot)
    return _nadaj(bpy.context.active_object, kolor, **kw)


def stozek(x, y, z0, r1, r2, h, kolor, v=12, rot=(0, 0, 0), **kw):
    bpy.ops.mesh.primitive_cone_add(vertices=v, radius1=r1, radius2=r2, depth=h, location=(x, y, z0 + h / 2),
                                    rotation=rot)
    return _nadaj(bpy.context.active_object, kolor, **kw)


def kula(x, y, z, r, kolor, seg=10, ringi=7, skala=(1, 1, 1), **kw):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=ringi, radius=r, location=(x, y, z))
    o = bpy.context.active_object
    o.scale = skala
    return _nadaj(o, kolor, **kw)


def ikosfera(x, y, z, r, kolor, skala=(1, 1, 1), pod=1, **kw):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=pod, radius=r, location=(x, y, z))
    o = bpy.context.active_object
    o.scale = skala
    return _nadaj(o, kolor, **kw)


def torus(x, y, z, R, r, kolor, rot=(0, 0, 0), seg=16, mseg=6, **kw):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=seg, minor_segments=mseg,
                                     location=(x, y, z), rotation=rot)
    return _nadaj(bpy.context.active_object, kolor, **kw)


def walec(a, b, r, kolor, v=8, r2=None, **kw):
    """Walec (albo stożek ścięty, gdy r2) od punktu a do punktu b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=d.length, location=(a + b) / 2)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=v, radius1=r, radius2=r2, depth=d.length, location=(a + b) / 2)
    o = bpy.context.active_object
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return _nadaj(o, kolor, **kw)


def belka(a, b, sx, sy, kolor, **kw):
    """Prostopadłościan od punktu a do b (przekrój sx × sy)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cube_add(size=1, location=(a + b) / 2)
    o = bpy.context.active_object
    o.scale = (sx, sy, d.length)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return _nadaj(o, kolor, **kw)


def siatka(nazwa, verts, faces, kolor, **kw):
    me = bpy.data.meshes.new(nazwa)
    me.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()
    o = bpy.data.objects.new(nazwa, me)
    bpy.context.collection.objects.link(o)
    return _nadaj(o, kolor, **kw)


def dach_dwuspadowy(x, y, z0, sx, sy, h, kolor, wzdluz="x", biodrowy=0.0):
    """Dach z kalenicą wzdłuż osi X (lub Y). biodrowy>0 skraca kalenicę (dach czterospadowy)."""
    a, b = sx / 2, sy / 2
    if wzdluz == "x":
        k = max(0.0, a - biodrowy)
        v = [(-a, -b, 0), (a, -b, 0), (a, b, 0), (-a, b, 0), (-k, 0, h), (k, 0, h)]
        f = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
    else:
        k = max(0.0, b - biodrowy)
        v = [(-a, -b, 0), (a, -b, 0), (a, b, 0), (-a, b, 0), (0, -k, h), (0, k, h)]
        f = [(1, 2, 5, 4), (3, 0, 4, 5), (0, 1, 4), (2, 3, 5), (0, 3, 2, 1)]
    return siatka("dach", [(vx + x, vy + y, vz + z0) for vx, vy, vz in v], f, kolor)


def fronton(x, y_front, z0, szer, h, kolor, gl=0.06):
    """Trójkątny tympanon (front świątyni) w płaszczyźnie XZ, od y_front w głąb (+Y)."""
    a = szer / 2
    v = [(x - a, y_front, z0), (x + a, y_front, z0), (x, y_front, z0 + h),
         (x - a, y_front + gl, z0), (x + a, y_front + gl, z0), (x, y_front + gl, z0 + h)]
    f = [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    return siatka("fronton", v, f, kolor)


def graniastoslup(punkty, z0, h, kolor):
    n = len(punkty)
    v = [(px, py, z0) for px, py in punkty] + [(px, py, z0 + h) for px, py in punkty]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        f.append((i, j, n + j, n + i))
    return siatka("gr", v, f, kolor)


def profil_xz(punkty, gl, kolor, x=0.0, y=0.0, rz=0.0, z=0.0, **kw):
    """Wielokąt w płaszczyźnie XZ wyciągnięty na głębokość gl (wzdłuż Y), potem obrócony o rz i przesunięty."""
    n = len(punkty)
    v = [(px, -gl / 2, pz) for px, pz in punkty] + [(px, gl / 2, pz) for px, pz in punkty]
    f = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
    for i in range(n):
        j = (i + 1) % n
        f.append((i, j, n + j, n + i))
    o = siatka("profil", v, f, kolor, **kw)
    o.location = (x, y, z)
    o.rotation_euler = (0, 0, rz)
    return o


def sciana_lukowa(x0, x1, z0, z1, otwory, gl, kolor, x=0.0, y=0.0, rz=0.0, seg=7):
    """Ściana od x0 do x1 i od z0 do z1 z łukowymi otworami [(środek_x, szerokość, wysokość_wezgłowia)]."""
    pkt = [(x0, z0)]
    for cx, w, zs in sorted(otwory):
        r = w / 2
        pkt += [(cx - r, z0), (cx - r, zs)]
        for k in range(1, seg):
            t = math.pi - k * math.pi / seg
            pkt.append((cx + r * math.cos(t), zs + r * math.sin(t)))
        pkt += [(cx + r, zs), (cx + r, z0)]
    pkt += [(x1, z0), (x1, z1), (x0, z1)]
    return profil_xz(pkt, gl, kolor, x, y, rz)


def arkada(x0, x1, z0, z1, n, zs, gl, kolor, x=0.0, y=0.0, rz=0.0, filar=None):
    """Rząd n jednakowych łuków między x0 a x1."""
    dl = x1 - x0
    filar = filar if filar is not None else dl / n * 0.28
    w = (dl - (n + 1) * filar) / n
    otwory = [(x0 + filar + w / 2 + i * (w + filar), w, zs) for i in range(n)]
    return sciana_lukowa(x0, x1, z0, z1, otwory, gl, kolor, x, y, rz)


def kopula(x, y, z0, r, kolor, seg=16, ringi=6, skala_z=1.0, **kw):
    """Półkula (zamknięta od spodu)."""
    v, f = [], []
    for i in range(ringi):
        phi = i / ringi * math.pi / 2
        for j in range(seg):
            a = 2 * math.pi * j / seg
            v.append((x + r * math.cos(phi) * math.cos(a), y + r * math.cos(phi) * math.sin(a),
                      z0 + r * math.sin(phi) * skala_z))
    szczyt = len(v)
    v.append((x, y, z0 + r * skala_z))
    for i in range(ringi - 1):
        for j in range(seg):
            j1 = (j + 1) % seg
            f.append((i * seg + j, i * seg + j1, (i + 1) * seg + j1, (i + 1) * seg + j))
    for j in range(seg):
        f.append(((ringi - 1) * seg + j, (ringi - 1) * seg + (j + 1) % seg, szczyt))
    f.append(tuple(range(seg - 1, -1, -1)))
    return siatka("kopula", v, f, kolor, **kw)


def pierscien(x, y, z0, h, rx1, ry1, rx2, ry2, kolor, n=24, **kw):
    """Pierścień eliptyczny: zewnętrzne półosie rx1, ry1, wewnętrzne rx2, ry2."""
    v = []
    for rx, ry, z in ((rx1, ry1, z0), (rx1, ry1, z0 + h), (rx2, ry2, z0 + h), (rx2, ry2, z0)):
        for j in range(n):
            a = 2 * math.pi * j / n
            v.append((x + rx * math.cos(a), y + ry * math.sin(a), z))
    f = []
    for k in range(4):
        k1 = (k + 1) % 4
        for j in range(n):
            j1 = (j + 1) % n
            f.append((k * n + j, k * n + j1, k1 * n + j1, k1 * n + j))
    return siatka("pierscien", v, f, kolor, **kw)


def kolumna(x, y, z0, h, r, kolor=MARMUR, kapitel=None):
    kapitel = kapitel or kolor
    box(x, y, z0, r * 2.6, r * 2.6, h * 0.06, kolor)
    cyl(x, y, z0 + h * 0.06, r, h * 0.86, kolor, v=10)
    box(x, y, z0 + h * 0.92, r * 2.7, r * 2.7, h * 0.08, kapitel)


def kadlub(dl, szer, wys, kolor, x=0.0, y=0.0, z0=0.0):
    """Kadłub łodzi wzdłuż osi Y (dziób na -Y), stępka na z0."""
    przekroje = [(-1.0, 0.04, 1.45), (-0.86, 0.42, 1.15), (-0.6, 0.86, 1.0), (-0.2, 1.0, 0.97),
                 (0.3, 1.0, 0.97), (0.65, 0.84, 1.03), (0.88, 0.4, 1.22), (1.0, 0.04, 1.55)]
    v = []
    for t, wf, hf in przekroje:
        yy = y + t * dl / 2
        w = szer / 2 * wf
        H = z0 + wys * hf
        zk = z0 + wys * 0.5 * max(0.0, abs(t) - 0.6) / 0.4
        for px, pz in ((-w, H), (-0.82 * w, z0 + wys * 0.45), (0, zk), (0.82 * w, z0 + wys * 0.45), (w, H)):
            v.append((x + px, yy, max(pz, zk)))
    n = 5
    f = []
    for i in range(len(przekroje) - 1):
        for j in range(n):
            j1 = (j + 1) % n
            f.append((i * n + j, i * n + j1, (i + 1) * n + j1, (i + 1) * n + j))
    f.append(tuple(range(n - 1, -1, -1)))
    k = (len(przekroje) - 1) * n
    f.append(tuple(range(k, k + n)))
    return siatka("kadlub", v, f, kolor)


def napis(tekst, x, y, z, rozmiar, kolor, gl=0.02, **kw):
    """Napis 3D (zamieniony na siatkę) zwrócony frontem na -Y."""
    cu = bpy.data.curves.new("napis", "FONT")
    cu.body = tekst
    cu.size = rozmiar
    cu.extrude = gl
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    o = bpy.data.objects.new("napis", cu)
    bpy.context.collection.objects.link(o)
    o.location = (x, y, z)
    o.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.view_layer.objects.active
    o.select_set(False)
    return _nadaj(o, kolor, **kw)


def wstaw(fn, x=0.0, y=0.0, z=0.0, s=1.0, rz=0.0, a=()):
    """Wywołuje fn(*a) i przesuwa/obraca/skaluje wszystkie nowo utworzone obiekty."""
    przed = set(bpy.context.scene.objects)
    fn(*a)
    bpy.context.view_layer.update()        # inaczej matrix_world nie zawiera świeżo ustawionej skali
    M = Matrix.Translation((x, y, z)) @ Matrix.Rotation(rz, 4, "Z") @ Matrix.Scale(s, 4)
    for o in bpy.context.scene.objects:
        if o not in przed:
            o.matrix_world = M @ o.matrix_world


_tekstury_szumu = {}


def czysc():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mat.clear()
    _tekstury_szumu.clear()


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
    at = o.data.attributes.get("gladki")
    if at is not None:                                  # części oznaczone gladki() – cieniowanie gładkie
        for i, poly in enumerate(o.data.polygons):
            if at.data[i].value:
                poly.use_smooth = True
    o.select_set(False)
    return o


def gladki(o):
    """Oznacza obiekt do gładkiego cieniowania (twarz, kaptur, fałdy) – przetrwa łączenie w polacz()."""
    me = o.data
    at = me.attributes.get("gladki") or me.attributes.new("gladki", "BOOLEAN", "FACE")
    for d in at.data:
        d.value = True
    return o


def faldy(o, n=7, amp=0.06, z_od=-1.0):
    """Pionowe fałdy szaty: promień wierzchołków moduluje sinus kąta (rośnie ku dołowi)."""
    me = o.data
    zs = [v.co.z for v in me.vertices]
    zmin, zmax = min(zs), max(zs)
    for v in me.vertices:
        a = math.atan2(v.co.y, v.co.x)
        t = 1.0 - (v.co.z - zmin) / max(zmax - zmin, 1e-4)
        if v.co.z < z_od and z_od > -0.99:
            continue
        f = 1.0 + amp * t * (math.sin(a * n) + 0.4 * math.sin(a * n * 2 + 1.3))
        v.co.x *= f
        v.co.y *= f


def zapisz_glb(nazwa):
    sciezka = os.path.join(MODELE, nazwa + ".glb")
    bpy.ops.export_scene.gltf(filepath=sciezka, export_format="GLB", use_selection=False, export_apply=True,
                              export_yup=True)
    print("model:", nazwa)


CZESCI_RUCHOME = ("anim_", "kon_", "slon_", "jezdziec", "balista_", "sciana_", "strzecha")


# ----------------------------------------------------------------- fazowanie krawędzi i wypalony AO
def fazuj(o, szer=0.012):
    """Bevel na ostrych krawędziach – krawędzie łapią światło (low-poly, 1 segment)."""
    m = o.modifiers.new("faza", "BEVEL")
    m.width = szer
    m.segments = 1
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(35)
    m.use_clamp_overlap = True
    m.harden_normals = False
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.ops.object.modifier_apply(modifier=m.name)
    o.select_set(False)


def _swiat_ao(zasieg):
    sc = bpy.context.scene
    if sc.world is None:
        sc.world = bpy.data.worlds.new("swiat_ao")
    sc.world.light_settings.distance = zasieg
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24
    try:
        sc.cycles.use_denoising = False
    except Exception:
        pass


def _ziemia_pod():
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -0.001))
    return bpy.context.active_object


def warianty_gn(o, ziarno, sila=0.12, skala=(1.0, 1.0, 1.0)):
    """Geometry Nodes: deformacja szumem 4D (W = ziarno) i nierówna skala – każdy wariant ma inną sylwetkę."""
    ng = bpy.data.node_groups.new("warianty_%d" % ziarno, "GeometryNodeTree")
    ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes
    we = N.new("NodeGroupInput")
    wy = N.new("NodeGroupOutput")
    poz = N.new("GeometryNodeInputPosition")
    szum = N.new("ShaderNodeTexNoise")
    szum.noise_dimensions = "4D"
    szum.inputs["W"].default_value = ziarno * 1.37
    szum.inputs["Scale"].default_value = 1.6
    szum.inputs["Detail"].default_value = 1.0
    odejm = N.new("ShaderNodeVectorMath")
    odejm.operation = "SUBTRACT"
    odejm.inputs[1].default_value = (0.5, 0.5, 0.5)
    mnoz = N.new("ShaderNodeVectorMath")
    mnoz.operation = "SCALE"
    mnoz.inputs["Scale"].default_value = sila * 2.0
    # wysokość wpływu: przy ziemi (z ≈ 0) bez deformacji – drzewo nie odrywa się od podłoża
    sep = N.new("ShaderNodeSeparateXYZ")
    mapz = N.new("ShaderNodeMapRange")
    mapz.inputs["From Min"].default_value = 0.0
    mapz.inputs["From Max"].default_value = 0.6
    mnoz2 = N.new("ShaderNodeVectorMath")
    mnoz2.operation = "SCALE"
    ustaw = N.new("GeometryNodeSetPosition")
    trans = N.new("GeometryNodeTransform")
    trans.inputs["Scale"].default_value = skala
    L = ng.links
    L.new(poz.outputs["Position"], szum.inputs["Vector"])
    L.new(szum.outputs["Color"], odejm.inputs[0])
    L.new(odejm.outputs["Vector"], mnoz.inputs[0])
    L.new(poz.outputs["Position"], sep.inputs[0])
    L.new(sep.outputs["Z"], mapz.inputs["Value"])
    L.new(mnoz.outputs["Vector"], mnoz2.inputs[0])
    L.new(mapz.outputs["Result"], mnoz2.inputs["Scale"])
    L.new(we.outputs[0], ustaw.inputs["Geometry"])
    L.new(mnoz2.outputs["Vector"], ustaw.inputs["Offset"])
    L.new(ustaw.outputs["Geometry"], trans.inputs["Geometry"])
    L.new(trans.outputs["Geometry"], wy.inputs[0])
    m = o.modifiers.new("warianty", "NODES")
    m.node_group = ng
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.ops.object.modifier_apply(modifier=m.name)
    o.select_set(False)


def wypal_teksture(o, rozmiar=512, zasieg=0.6, sila=0.75):
    """Wypala kolor materiałów pomnożony przez ambient occlusion do jednej tekstury (Smart UV).
    Model dostaje jeden materiał z tą teksturą – w glTF/Godot widać miękkie cienie w zakamarkach
    i przy styku z ziemią."""
    _swiat_ao(zasieg)
    ziemia = _ziemia_pod()
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.012)
    bpy.ops.object.mode_set(mode="OBJECT")
    obrazy = {}
    for rodzaj in ("DIFFUSE", "AO"):
        img = bpy.data.images.new("%s_%s" % (o.name, rodzaj), rozmiar, rozmiar, alpha=False, float_buffer=True)
        for m in o.data.materials:
            if m is None:
                continue
            m.use_nodes = True
            nt = m.node_tree
            n = nt.nodes.get("cel_wypalania") or nt.nodes.new("ShaderNodeTexImage")
            n.name = "cel_wypalania"
            n.image = img
            nt.nodes.active = n
        if rodzaj == "DIFFUSE":
            bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4, use_clear=True)
        else:
            bpy.ops.object.bake(type="AO", margin=4, use_clear=True)
        obrazy[rodzaj] = img
    import numpy as np
    kol = np.array(obrazy["DIFFUSE"].pixels[:], dtype=np.float32).reshape(-1, 4)
    ao = np.array(obrazy["AO"].pixels[:], dtype=np.float32).reshape(-1, 4)[:, :1]
    wynik = kol.copy()
    wynik[:, :3] = kol[:, :3] * (1.0 - sila + sila * ao)
    wynik[:, 3] = 1.0
    gotowy = bpy.data.images.new(o.name + "_tekstura", rozmiar, rozmiar, alpha=False)
    gotowy.colorspace_settings.name = "sRGB"
    # piksele float (liniowe) -> sRGB dla obrazu 8-bitowego
    lin_ = np.clip(wynik[:, :3], 0, 1)
    srgb = np.where(lin_ <= 0.0031308, lin_ * 12.92, 1.055 * np.power(lin_, 1 / 2.4) - 0.055)
    wynik[:, :3] = srgb
    gotowy.pixels[:] = wynik.ravel()
    gotowy.pack()
    m = bpy.data.materials.new(o.name + "_wypalony")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.82
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = gotowy
    nt.links.new(tx.outputs["Color"], bsdf.inputs["Base Color"])
    o.data.materials.clear()
    o.data.materials.append(m)
    bpy.data.objects.remove(ziemia)
    for im in obrazy.values():
        bpy.data.images.remove(im)


def ao_wierzcholki(o, zasieg=0.5, sila=0.6):
    """AO wypalony do kolorów wierzchołków i pomnożony przez gradient „Col” (drzewa, skały)."""
    me = o.data
    if "Col" not in me.color_attributes:
        return
    _swiat_ao(zasieg)
    ziemia = _ziemia_pod()
    me.color_attributes.new("AO", "BYTE_COLOR", "POINT")
    me.color_attributes.active_color = me.color_attributes["AO"]
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.bake(type="AO", target="VERTEX_COLORS")
    kol, ao = me.color_attributes["Col"], me.color_attributes["AO"]
    for i in range(len(kol.data)):
        a = ao.data[i].color[0]
        c = kol.data[i].color
        f = 1.0 - sila + sila * a
        kol.data[i].color = (c[0] * f, c[1] * f, c[2] * f, 1.0)
    me.color_attributes.remove(me.color_attributes["AO"])
    me.color_attributes.active_color = me.color_attributes["Col"]
    bpy.data.objects.remove(ziemia)


def eksportuj(nazwa):
    """Jeden obiekt siatki z punktem zaczepienia w (0,0,0). Części „anim_*” (koła, flagi, narzędzia, ogień,
    woda…) i puste punkty „dym_*” zostają osobnymi węzłami – Godot je animuje (gra.gd, _ozyw_model)."""
    polacz([o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.startswith(CZESCI_RUCHOME)],
           nazwa, (0, 0, 0))
    zapisz_glb(nazwa)


OSOBNE = ("cieciwa",)        # obiekty, które zostają osobnymi węzłami (np. cięciwa – Godot rysuje ją sam)


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
        nowe = [o for o in bpy.context.scene.objects if o not in self.przed and o.type == "MESH"
                and not o.name.startswith(OSOBNE)]
        polacz(nowe, self.nazwa, self.pivot)


CZESCI = ("noga_l", "noga_p", "reka_l", "reka_p", "glowa", "peleryna")


def eksportuj_postac(nazwa):
    """Postać z osobnymi częściami (cialo, noga_l/p, reka_l/p) — Godot porusza nimi przy chodzeniu."""
    reszta = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in CZESCI
              and not o.name.startswith(OSOBNE)]
    polacz(reszta, "cialo", (0, 0, 0))
    zapisz_glb(nazwa)


# ================================================================= TEREN I DEKORACJE
# ----------------------------------------------------------------- drzewa (low-poly z charakterem)
# Korona: kilka brył różnej wielkości, przesuniętych asymetrycznie, zlanych voxel-remeshem w jedną,
# z lekkim displace szumem i decymacją (zostaje low-poly). Pień: wygięta, zwężająca się rura
# z poszerzeniem przy ziemi i konarami wchodzącymi w koronę. Kolory w vertex colors (atrybut „Col”):
# ciemniejszy spód, jaśniejsza góra korony. Godot dodaje losowy odcień dla każdego egzemplarza.
import random as _random



def mat_vc():
    """Materiał biorący kolor z atrybutu wierzchołków „Col” (eksportowany do glTF jako COLOR_0)."""
    if "vc" in _mat:
        return _mat["vc"]
    m = bpy.data.materials.new("drzewo_vc")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.88
    ca = nt.nodes.new("ShaderNodeVertexColor")
    ca.layer_name = "Col"
    nt.links.new(ca.outputs["Color"], p.inputs["Base Color"])
    m.diffuse_color = (0.3, 0.5, 0.25, 1)
    _mat["vc"] = m
    return m


def _koloruj(o, dol, gora, z0=None, z1=None, szum=0.06, ziarno=1):
    """Gradient pionowy w vertex colors (sRGB dol -> gora) z drobnym losowym szumem."""
    me = o.data
    if "Col" not in me.color_attributes:
        me.color_attributes.new("Col", "BYTE_COLOR", "POINT")
    attr = me.color_attributes["Col"]
    zs = [(o.matrix_world @ v.co).z for v in me.vertices]
    z0 = min(zs) if z0 is None else z0
    z1 = max(zs) if z1 is None else z1
    r = _random.Random(ziarno)
    d, g = Vector(lin(dol)), Vector(lin(gora))
    for i, z in enumerate(zs):
        t = max(0.0, min(1.0, (z - z0) / max(z1 - z0, 1e-4)))
        t = t * t * (3 - 2 * t)
        c = d.lerp(g, t) * (1.0 + r.uniform(-szum, szum))
        attr.data[i].color = (c.x, c.y, c.z, 1.0)
    me.materials.clear()
    me.materials.append(mat_vc())
    return o


def _zastosuj(o, mod):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    o.select_set(False)


def _bryly_korony(bryly, voxel=0.1, szum=0.07, skala_szumu=0.35, cel_scian=260, ziarno=1):
    """bryly: [(x, y, z, r, (sx, sy, sz))] -> jedna zlana, poszarpana bryła korony (low-poly)."""
    bpy.ops.object.select_all(action="DESELECT")
    obiekty = []
    for (x, y, z, r, sk) in bryly:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=(x, y, z))
        o = bpy.context.active_object
        o.scale = sk
        obiekty.append(o)
    for o in obiekty:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obiekty[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.select_set(False)
    # zlanie brył w jedną (voxel remesh = „union” bez artefaktów na stykach)
    rm = o.modifiers.new("zlanie", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = voxel
    _zastosuj(o, rm)
    # lekki displace szumem – nieregularna sylwetka
    klucz = (round(skala_szumu, 3), ziarno)
    if klucz not in _tekstury_szumu:
        t = bpy.data.textures.new("szum_%d" % len(_tekstury_szumu), "CLOUDS")
        t.noise_scale = skala_szumu
        t.noise_depth = 1
        _tekstury_szumu[klucz] = t
    ds = o.modifiers.new("szum", "DISPLACE")
    ds.texture = _tekstury_szumu[klucz]
    ds.texture_coords = "OBJECT"
    ds.strength = szum
    ds.mid_level = 0.5
    _zastosuj(o, ds)
    # z powrotem low-poly
    n = len(o.data.polygons)
    if n > cel_scian:
        dc = o.modifiers.new("lowpoly", "DECIMATE")
        dc.ratio = cel_scian / n
        _zastosuj(o, dc)
    return o


def _rura(punkty, promienie, v=7, nazwa="pien"):
    """Wygięta, zwężająca się rura (pień, konar) przez kolejne punkty; zamknięta u góry."""
    bm = bmesh.new()
    pkt = [Vector(p) for p in punkty]
    pierscienie = []
    for i, (p, r) in enumerate(zip(pkt, promienie)):
        kier = (pkt[min(i + 1, len(pkt) - 1)] - pkt[max(i - 1, 0)]).normalized()
        a = kier.orthogonal().normalized()
        b = kier.cross(a).normalized()
        pier = []
        for k in range(v):
            ang = 2 * math.pi * k / v
            pier.append(bm.verts.new(p + (a * math.cos(ang) + b * math.sin(ang)) * r))
        pierscienie.append(pier)
    for i in range(len(pierscienie) - 1):
        for k in range(v):
            p0, p1 = pierscienie[i], pierscienie[i + 1]
            bm.faces.new((p0[k], p0[(k + 1) % v], p1[(k + 1) % v], p1[k]))
    bm.faces.new(pierscienie[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nazwa)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nazwa, me)
    bpy.context.collection.objects.link(o)
    return o


def _pien(os_, r0, r1, poszerzenie=1.6, v=7):
    """Pień wzdłuż łamanej `os_`: zwęża się od r0 do r1, przy ziemi poszerzony (korzenie)."""
    n = len(os_)
    promienie = []
    for i in range(n):
        t = i / (n - 1)
        r = r0 + (r1 - r0) * t
        if i == 0:
            r *= poszerzenie
        elif i == 1:
            r *= 1.0 + (poszerzenie - 1.0) * 0.3
        promienie.append(r)
    return _rura(os_, promienie, v=v)


def _luk(a, b, wygiecie, n=5):
    """Łamana od a do b wygięta bokiem o wektor `wygiecie` (największe w połowie)."""
    a, b, w = Vector(a), Vector(b), Vector(wygiecie)
    return [a.lerp(b, i / (n - 1)) + w * math.sin(math.pi * i / (n - 1)) for i in range(n)]


KORA = ((78, 56, 40), (126, 98, 72))
KORA_OL = ((86, 78, 64), (150, 140, 120))


def m_pinia(ziarno=3):
    """Pinia: wysoki, goły, lekko wygięty pień i płaska, parasolowata korona."""
    r = _random.Random(ziarno)
    os_ = _luk((0, 0, 0), (0.2, 0.05, 1.9), (0.18, 0.0, 0.0), n=6)
    _koloruj(_pien(os_, 0.1, 0.055, poszerzenie=1.7), *KORA, ziarno=ziarno)
    # konary rozchodzące się w koronę
    szczyt = Vector(os_[-1])
    for kat in (0.3, 2.4, 4.3):
        k = szczyt + Vector((math.cos(kat) * 0.6, math.sin(kat) * 0.6, 0.3))
        _koloruj(_rura(_luk(szczyt - Vector((0, 0, 0.12)), k, (0, 0, 0.08), n=4), [0.05, 0.042, 0.034, 0.026], v=5),
                 *KORA, ziarno=ziarno + 1)
    bryly = [(0.2, 0.05, 2.32, 0.6, (1.6, 1.45, 0.26))]
    for i in range(6):
        kat = i * 1.05 + r.uniform(-0.25, 0.25)
        d = r.uniform(0.5, 0.72)
        bryly.append((0.2 + math.cos(kat) * d, 0.05 + math.sin(kat) * d, 2.28 + r.uniform(-0.05, 0.08),
                      r.uniform(0.3, 0.4), (1.35, 1.3, 0.36)))
    k = _bryly_korony(bryly, voxel=0.08, szum=0.06, skala_szumu=0.3, cel_scian=280, ziarno=ziarno)
    _koloruj(k, (30, 60, 34), (104, 146, 72), ziarno=ziarno)


def m_cyprys(ziarno=5):
    """Cyprys: wąskie, nieregularne wrzeciono (nie idealny stożek)."""
    r = _random.Random(ziarno)
    _koloruj(_pien(_luk((0, 0, 0), (0.02, 0, 0.5), (0.02, 0, 0), n=3), 0.07, 0.05, poszerzenie=1.5, v=6), *KORA, ziarno=ziarno)
    bryly = []
    z = 0.42
    for i in range(6):
        t = i / 5
        rr = 0.3 * (1.0 - 0.55 * t) * r.uniform(0.85, 1.12)
        bryly.append((r.uniform(-0.05, 0.05), r.uniform(-0.05, 0.05), z + rr * 1.1, rr, (1.0, r.uniform(0.85, 1.05), 1.7)))
        z += rr * 1.15
    bryly.append((0.02, 0.0, z + 0.12, 0.08, (1, 1, 2.2)))       # szpic
    k = _bryly_korony(bryly, voxel=0.07, szum=0.06, skala_szumu=0.22, cel_scian=220, ziarno=ziarno)
    _koloruj(k, (22, 48, 30), (74, 118, 62), ziarno=ziarno)


def m_oliwka(x=0, y=0, s=1.0, ziarno=7):
    """Oliwka: niski, poskręcany pień (dwa splecione) i szeroka, srebrzystozielona korona."""
    r = _random.Random(ziarno)
    przed = set(bpy.context.scene.objects)
    # jeden gruby, poskręcany i pochylony pień, który nisko się rozwidla
    pts = [(0.0, 0.0, 0.0), (0.06, 0.03, 0.12), (0.02, 0.07, 0.24), (0.1, 0.04, 0.36), (0.07, -0.02, 0.48), (0.14, 0.0, 0.6)]
    _koloruj(_pien(pts, 0.11, 0.065, poszerzenie=1.6, v=7), *KORA_OL, ziarno=ziarno)
    odnoga = [(0.04, 0.05, 0.22), (-0.06, 0.1, 0.34), (-0.04, 0.05, 0.46), (-0.14, 0.08, 0.6)]
    _koloruj(_rura(odnoga, [0.07, 0.06, 0.05, 0.04], v=6), *KORA_OL, ziarno=ziarno + 1)
    for kat in (0.6, 2.7, 4.6):
        a = Vector((0, 0, 0.58))
        b = a + Vector((math.cos(kat) * 0.45, math.sin(kat) * 0.45, 0.3))
        _koloruj(_rura(_luk(a, b, (0, 0, 0.06), n=4), [0.045, 0.038, 0.03, 0.022], v=5), *KORA_OL, ziarno=ziarno)
    bryly = [(0.08, 0.0, 0.98, 0.45, (1.5, 1.3, 0.48))]
    for i in range(5):
        kat = i * 1.3 + r.uniform(-0.4, 0.4)
        d = r.uniform(0.42, 0.62)
        bryly.append((0.08 + math.cos(kat) * d, math.sin(kat) * d, 0.92 + r.uniform(-0.08, 0.12), r.uniform(0.22, 0.32), (1.25, 1.15, 0.7)))
    k = _bryly_korony(bryly, voxel=0.075, szum=0.08, skala_szumu=0.22, cel_scian=260, ziarno=ziarno)
    _koloruj(k, (62, 92, 50), (140, 166, 104), ziarno=ziarno)
    # owoce
    for (dx, dy, dz) in [(0.25, -0.45, 0.85), (-0.3, -0.35, 0.82), (0.5, -0.15, 0.95)]:
        kula(dx, dy, dz, 0.035, (60, 70, 50), seg=5, ringi=3)
    if (x, y, s) != (0, 0, 1.0):
        bpy.context.view_layer.update()
        M = Matrix.Translation((x, y, 0)) @ Matrix.Scale(s, 4)
        for o in bpy.context.scene.objects:
            if o not in przed:
                o.matrix_world = M @ o.matrix_world


def m_dab(ziarno=11):
    """Dąb: masywny, szeroki pień z konarami i kilka „pięter” listowia."""
    r = _random.Random(ziarno)
    os_ = _luk((0, 0, 0), (0.06, 0.02, 1.05), (0.07, 0.03, 0), n=5)
    _koloruj(_pien(os_, 0.2, 0.12, poszerzenie=1.75, v=8), *KORA, ziarno=ziarno)
    for kat, wys, dl in ((0.2, 0.75, 0.62), (2.3, 0.85, 0.58), (4.2, 0.95, 0.5)):
        a = Vector((0.04, 0.0, wys))
        b = a + Vector((math.cos(kat) * dl, math.sin(kat) * dl, 0.55))
        _koloruj(_rura(_luk(a, b, (0, 0, 0.1), n=4), [0.085, 0.07, 0.055, 0.04], v=6), *KORA, ziarno=ziarno)
    bryly = []
    # dolne piętro – szerokie
    for i in range(4):
        kat = i * 1.57 + r.uniform(-0.3, 0.3)
        bryly.append((math.cos(kat) * 0.48, math.sin(kat) * 0.45, 1.45 + r.uniform(-0.08, 0.08), r.uniform(0.42, 0.52), (1.15, 1.1, 0.78)))
    # środkowe i górne piętro – mniejsze, przesunięte asymetrycznie
    for i in range(3):
        kat = i * 2.1 + 0.5 + r.uniform(-0.3, 0.3)
        bryly.append((0.05 + math.cos(kat) * 0.3, math.sin(kat) * 0.28, 1.95 + r.uniform(-0.05, 0.05), r.uniform(0.36, 0.42), (1.15, 1.1, 0.75)))
    bryly.append((-0.08, 0.06, 2.28, 0.3, (1.2, 1.1, 0.7)))
    k = _bryly_korony(bryly, voxel=0.1, szum=0.09, skala_szumu=0.3, cel_scian=320, ziarno=ziarno)
    _koloruj(k, (32, 64, 30), (118, 162, 76), ziarno=ziarno)


def m_krzak(ziarno=13):
    r = _random.Random(ziarno)
    bryly = [(0, 0, 0.22, 0.3, (1.25, 1.05, 0.8))]
    for i in range(3):
        kat = i * 2.1 + r.uniform(-0.4, 0.4)
        bryly.append((math.cos(kat) * 0.24, math.sin(kat) * 0.22, 0.18, r.uniform(0.17, 0.23), (1, 1, 0.9)))
    k = _bryly_korony(bryly, voxel=0.06, szum=0.05, skala_szumu=0.18, cel_scian=120, ziarno=ziarno)
    _koloruj(k, (46, 82, 40), (104, 150, 72), z0=0.0, ziarno=ziarno)
    for (x, y) in [(0.1, -0.28), (-0.15, -0.22)]:
        kula(x, y, 0.3, 0.035, (200, 60, 60), seg=5, ringi=3)


def m_skala_0(ziarno=21):
    """Głaz: kilka brył zlanych w jedną, poszarpanych szumem (warianty: ziarno)."""
    r = _random.Random(ziarno)
    bryly = [(0, 0, 0.3, 0.55, (1.25, 1.0, 0.7))]
    for i in range(r.randint(2, 3)):
        a = r.uniform(0, 6.28)
        bryly.append((math.cos(a) * 0.45, math.sin(a) * 0.4, 0.2, r.uniform(0.25, 0.38), (1.1, 1.0, 0.8)))
    k = _bryly_korony(bryly, voxel=0.07, szum=0.09, skala_szumu=0.25, cel_scian=160, ziarno=ziarno)
    _koloruj(k, (104, 92, 76), (150, 150, 112), z0=0.0, ziarno=ziarno)


def m_skala_1(ziarno=23):
    """Skałka z kępą trawy."""
    r = _random.Random(ziarno)
    bryly = [(0, 0.1, 0.55, 0.5, (0.95, 0.85, 1.25)), (0.42, -0.2, 0.3, 0.38, (1, 1, 0.8)),
             (-0.42, -0.22, 0.2, r.uniform(0.25, 0.32), (1.2, 1, 0.7))]
    k = _bryly_korony(bryly, voxel=0.07, szum=0.1, skala_szumu=0.22, cel_scian=180, ziarno=ziarno)
    _koloruj(k, (100, 88, 72), (146, 148, 108), z0=0.0, ziarno=ziarno)
    kp = _bryly_korony([(-0.25, -0.45, 0.05, 0.18, (1.5, 1, 0.5))], voxel=0.05, szum=0.04, cel_scian=60, ziarno=ziarno)
    _koloruj(kp, (60, 100, 50), (110, 150, 70), z0=0.0, ziarno=ziarno)


def m_klif(ziarno=31):
    """Skalne urwisko do krawędzi wzgórza (wzdłuż osi X, lico na -Y): kanciaste warstwy tufu i trawertynu,
    zlane voxel-remeshem, lekko poszarpane szumem; na koronie pas trawy."""
    r = _random.Random(ziarno)
    bpy.ops.object.select_all(action="DESELECT")
    bloki = []
    z = 0.0
    warstwa = 0
    while z < 1.0:                                                            # poziome ławice skały
        h = r.uniform(0.22, 0.34)
        x = -1.0
        while x < 1.0:
            w = r.uniform(0.3, 0.55)
            gl = r.uniform(0.32, 0.46) - warstwa * 0.04
            o = box(x + w / 2, r.uniform(-0.06, 0.06) + warstwa * 0.05, z, w * 1.02, gl, h * r.uniform(0.9, 1.1),
                    KAMIEN, rot=(0, r.uniform(-0.06, 0.06), r.uniform(-0.08, 0.08)))
            bloki.append(o)
            x += w * 0.92
        z += h * 0.92
        warstwa += 1
    for o in bloki:
        o.select_set(True)
    bpy.context.view_layer.objects.active = bloki[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.join()
    k = bpy.context.view_layer.objects.active
    k.select_set(False)
    rm = k.modifiers.new("zlanie", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = 0.05
    _zastosuj(k, rm)
    t = bpy.data.textures.new("klif_szum_%d" % ziarno, "CLOUDS")
    t.noise_scale = 0.2
    ds = k.modifiers.new("szum", "DISPLACE")
    ds.texture = t
    ds.texture_coords = "OBJECT"
    ds.strength = 0.06
    _zastosuj(k, ds)
    dc = k.modifiers.new("lowpoly", "DECIMATE")
    dc.decimate_type = "DISSOLVE"                                             # płaskie lica zostają płaskie
    dc.angle_limit = math.radians(8)
    _zastosuj(k, dc)
    tr = k.modifiers.new("tri", "TRIANGULATE")
    _zastosuj(k, tr)
    _koloruj(k, (100, 84, 66), (180, 162, 128), z0=0.0, ziarno=ziarno, szum=0.14)
    gora_ = max(v.co.z for v in k.data.vertices)
    kp = _bryly_korony([(0.0, 0.18, gora_ - 0.08, 0.5, (2.1, 0.7, 0.22))], voxel=0.06, szum=0.04,
                       cel_scian=70, ziarno=ziarno)                          # trawa na koronie urwiska
    _koloruj(kp, (70, 110, 52), (118, 158, 74), ziarno=ziarno)


def m_trzcina(ziarno=41):
    """Kępa trzciny (bez podstawy – stoi w płytkiej wodzie albo na brzegu): łodygi i brązowe kolby."""
    r = _random.Random(ziarno)
    for i in range(r.randint(16, 22)):
        a = r.uniform(0, 6.28)
        rr = r.uniform(0.05, 0.42)
        x, y = rr * math.cos(a), rr * math.sin(a)
        h = r.uniform(0.75, 1.35)
        nx, ny = r.uniform(-0.18, 0.18), r.uniform(-0.18, 0.18)
        walec((x, y, -0.15), (x + nx, y + ny, h), 0.016, (96, 140, 64) if i % 3 else (130, 150, 70), v=4)
        if i % 3 == 0:
            walec((x + nx * 0.92, y + ny * 0.92, h - 0.2), (x + nx, y + ny, h - 0.02), 0.035, (110, 72, 40), v=5)
        if i % 4 == 0:                                                        # liście
            belka((x, y, 0.2), (x + nx * 2.5, y + ny * 2.5, 0.75), 0.05, 0.008, (110, 150, 70))
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH"]:
        brazowe = o.data.materials and o.data.materials[0].name.startswith("m_6e4828")
        _koloruj(o, (70, 46, 26) if brazowe else (58, 88, 42), (120, 80, 46) if brazowe else (146, 172, 86),
                 z0=-0.15, z1=1.3, ziarno=ziarno)


def m_gora():
    stozek(0, 0, 0, 0.95, 0.15, 2.6, (128, 118, 104), v=7, rot=(0, 0, 0.3))
    stozek(0.35, 0.3, 0, 0.6, 0.1, 1.7, (110, 102, 92), v=6)
    stozek(-0.4, 0.25, 0, 0.55, 0.12, 1.3, (140, 128, 112), v=6)
    stozek(0, 0, 1.95, 0.42, 0.0, 0.85, (244, 244, 248), v=7, rot=(0, 0, 0.3))
    stozek(0, 0, 0, 0.98, 0.7, 0.35, (96, 132, 70), v=9)


def m_wzgorze():
    kopula(0, 0, 0, 0.98, (108, 152, 74), seg=14, ringi=5, skala_z=0.42)
    kopula(0.25, 0.2, 0.25, 0.45, (122, 164, 82), seg=10, ringi=4, skala_z=0.5)
    ikosfera(-0.45, -0.3, 0.2, 0.14, KAMIEN)
    ikosfera(0.5, -0.35, 0.15, 0.14, (80, 128, 60))


# ================================================================= BUDYNKI (≤ 1,8 × 1,8 × 3 m)
def dym(x, y, z, nazwa="dym"):
    """Pusty punkt – w Godocie powstaje tu dym (cząsteczki)."""
    o = bpy.data.objects.new(nazwa, None)
    o.location = (x, y, z)
    bpy.context.collection.objects.link(o)
    return o


def flaga(x, y, z0, h, kolor, nazwa, szer=0.3):
    """Maszt z flagą powiewającą na wietrze (anim_kolys_flaga…)."""
    cyl(x, y, z0, 0.015, h, DREWNO_C, v=5)
    kula(x, y, z0 + h + 0.02, 0.025, ZLOTO, seg=5, ringi=3, metal=0.6)
    with Grupa("anim_kolys_flaga_" + nazwa, (x, y, z0 + h)):
        box(x + szer / 2, y, z0 + h - 0.2, szer, 0.012, 0.18, kolor)
        box(x + szer * 0.85, y, z0 + h - 0.2, szer * 0.3, 0.014, 0.05, ZLOTO)


def _ludzik(tunika, czynnosc, narzedzie, nazwa):
    """Mały robotnik (ok. 0,75 m) zwrócony na -Y; ręce z narzędziem to część anim_<czynnosc>_<nazwa>."""
    for sx in (-1, 1):
        box(sx * 0.055, 0, 0, 0.075, 0.08, 0.3, SKORA_C)                     # nogi
        box(sx * 0.055, -0.02, 0, 0.08, 0.11, 0.035, DREWNO_C)               # sandały
    box(0, 0, 0.28, 0.24, 0.14, 0.3, tunika)                                  # tunika
    box(0, 0, 0.4, 0.25, 0.15, 0.03, DREWNO_C)                                # pas
    kula(0, 0, 0.66, 0.085, SKORA, seg=8, ringi=6)                            # głowa
    kula(0, 0.015, 0.7, 0.083, (90, 60, 36), seg=8, ringi=5, skala=(1, 1, 0.6))  # włosy
    with Grupa("anim_%s_%s" % (czynnosc, nazwa), (0, 0, 0.54)):
        for sx in (-1, 1):
            belka((sx * 0.14, 0, 0.55), (sx * 0.06, -0.17, 0.44), 0.06, 0.06, tunika)
            kula(sx * 0.06, -0.18, 0.43, 0.035, SKORA, seg=6, ringi=4)
        if narzedzie == "mlot":
            belka((0, -0.19, 0.42), (0, -0.2, 0.72), 0.025, 0.025, DREWNO_C)
            box(0, -0.2, 0.7, 0.14, 0.06, 0.06, STAL)
        elif narzedzie == "kilof":
            belka((0, -0.19, 0.42), (0, -0.2, 0.74), 0.025, 0.025, DREWNO_C)
            belka((-0.12, -0.24, 0.7), (0.12, -0.16, 0.74), 0.03, 0.03, STAL)
        elif narzedzie == "miecz":
            box(0, -0.19, 0.42, 0.06, 0.03, 0.03, ZLOTO)
            belka((0, -0.19, 0.44), (0, -0.21, 0.78), 0.035, 0.012, STAL)
        elif narzedzie == "kosz":
            cyl(0, -0.22, 0.34, 0.08, 0.1, STRZECHA_C, v=8)
            for k in range(3):
                kula(-0.03 + k * 0.03, -0.22, 0.45, 0.025, (96, 40, 90), seg=5, ringi=3)


def ludzik(x, y, rz=0.0, tunika=(150, 70, 50), czynnosc="mlot", narzedzie="mlot", nazwa="robotnik", s=1.0):
    wstaw(_ludzik, x, y, 0, s, rz, a=(tunika, czynnosc, narzedzie, nazwa))


def baza(sx, sy, kolor, h=0.04):
    box(0, 0, 0, sx, sy, h, kolor)


def _normal_mapa(nazwa, wzor, rozmiar=256, sila=2.0):
    """Normal mapa z mapy wysokości (numpy): wzor(u, v) -> wysokość 0..1."""
    import numpy as np
    u, v = np.meshgrid(np.linspace(0, 1, rozmiar, endpoint=False), np.linspace(0, 1, rozmiar, endpoint=False))
    h = wzor(u, v).astype(np.float32)
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * sila
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * sila
    n = np.stack([-dx, -dy, np.ones_like(h)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    px = np.concatenate([n * 0.5 + 0.5, np.ones((rozmiar, rozmiar, 1), np.float32)], -1)
    img = bpy.data.images.new(nazwa, rozmiar, rozmiar, alpha=False)
    img.colorspace_settings.name = "Non-Color"
    img.pixels[:] = px.ravel()
    img.pack()
    return img


def _kolor_mapa(nazwa, wzor, rozmiar=256):
    import numpy as np
    u, v = np.meshgrid(np.linspace(0, 1, rozmiar, endpoint=False), np.linspace(0, 1, rozmiar, endpoint=False))
    rgb = wzor(u, v).astype(np.float32)
    px = np.concatenate([rgb, np.ones((rozmiar, rozmiar, 1), np.float32)], -1)
    img = bpy.data.images.new(nazwa, rozmiar, rozmiar, alpha=False)
    img.pixels[:] = px.ravel()
    img.pack()
    return img


def mat_teksturowy(nazwa, kolor_img, normal_img, sila_normalnej=1.0, szorstkosc=0.9):
    m = bpy.data.materials.new(nazwa)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = szorstkosc
    tk = nt.nodes.new("ShaderNodeTexImage")
    tk.image = kolor_img
    nt.links.new(tk.outputs["Color"], bsdf.inputs["Base Color"])
    tn = nt.nodes.new("ShaderNodeTexImage")
    tn.image = normal_img
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = sila_normalnej
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def _szum2d(u, v, czest, ziarno=0):
    import numpy as np
    r = np.random.default_rng(ziarno)
    w = np.zeros_like(u)
    for k in range(4):
        fx, fy = r.uniform(0.6, 1.4, 2) * czest * (2 ** k)
        fx, fy = round(fx), round(fy)                                         # całkowite – szum się zapętla
        w += np.sin(2 * np.pi * (u * fx + r.uniform())) * np.sin(2 * np.pi * (v * fy + r.uniform())) / (2 ** k)
    return w * 0.5 + 0.5


def m_chata():
    """Chata z Palatynu (VIII w. p.n.e.): ściana z plecionki oblepionej gliną (normal mapa), strzecha
    z warstw słomy (normal mapa źdźbeł), żerdzie dachu wystające nad kalenicą, płot, amfory, palenisko
    i wydeptana ziemia wokół."""
    import numpy as np
    # wydeptana ziemia: nieregularny placek z jaśniejszą ścieżką do wejścia
    r = _random.Random(5)
    pts = []
    for i in range(14):
        a = i * 2 * math.pi / 14
        rr = 0.86 + r.uniform(-0.06, 0.04)
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    graniastoslup(pts, 0.0, 0.035, ZIEMIA_J)
    graniastoslup([(-0.22, -0.55), (0.22, -0.55), (0.3, -0.9), (-0.3, -0.9)], 0.0, 0.038, (190, 158, 112))
    for (x, y, rr) in [(-0.62, 0.35, 0.12), (0.55, 0.52, 0.09), (-0.2, 0.72, 0.1)]:
        cyl(x, y, 0.0, rr, 0.04, (150, 116, 80), v=7)                         # ciemniejsze plamy błota
    # ściana: plecionka z gliną
    tex_g = _kolor_mapa("glina_kolor", lambda u, v: np.stack([
        0.48 + 0.1 * _szum2d(u, v, 6, 1), 0.36 + 0.08 * _szum2d(u, v, 6, 1), 0.24 + 0.05 * _szum2d(u, v, 6, 2)], -1) ** 2.2)
    nrm_g = _normal_mapa("glina_normal", lambda u, v: 0.55 * np.abs(np.sin(np.pi * (u * 24 + 0.5 * np.round(v * 8) % 2)))
                         * (0.6 + 0.4 * np.abs(np.sin(np.pi * v * 8))) + 0.45 * _szum2d(u, v, 10, 3), sila=6.0)
    with Grupa("sciana_chaty", (0, 0, 0)):
        cyl(0, 0, 0.03, 0.62, 0.78, KREM, v=16)
    sc = bpy.data.objects["sciana_chaty"]
    sc.data.materials.clear()
    sc.data.materials.append(mat_teksturowy("glina", tex_g, nrm_g, 1.0))
    for i in range(12):                                                       # słupy nośne wtopione w ścianę
        a = i * 2 * math.pi / 12
        cyl(0.63 * math.cos(a), 0.63 * math.sin(a), 0.03, 0.035, 0.82, DREWNO_C, v=5)
    # strzecha: kilka warstw słomy, każda z postrzępionym brzegiem
    tex_s = _kolor_mapa("sloma_kolor", lambda u, v: np.stack([
        0.78 + 0.12 * _szum2d(u * 3, v, 30, 4), 0.64 + 0.1 * _szum2d(u * 3, v, 30, 4), 0.34 + 0.06 * _szum2d(u, v, 20, 5)], -1) ** 2.2)
    nrm_s = _normal_mapa("sloma_normal", lambda u, v: np.abs(np.sin(np.pi * u * 90 + 3 * _szum2d(u, v, 8, 6)))
                         * 0.7 + 0.3 * _szum2d(u, v, 30, 7), sila=5.0)
    with Grupa("strzecha", (0, 0, 0.8)):
        for k, (r0, r1, z0, h) in enumerate([(0.95, 0.72, 0.76, 0.26), (0.76, 0.52, 0.98, 0.28),
                                             (0.56, 0.3, 1.22, 0.3), (0.34, 0.08, 1.48, 0.32)]):
            st = stozek(0, 0, z0, r0, r1, h, STRZECHA, v=18)
            # postrzępiony okap: wierzchołki dolnego pierścienia losowo opuszczone
            for vtx in st.data.vertices:
                if vtx.co.z < 0:
                    vtx.co.z -= r.uniform(0.0, 0.05)
                    vtx.co.x *= 1.0 + r.uniform(-0.03, 0.04)
                    vtx.co.y *= 1.0 + r.uniform(-0.03, 0.04)
        stozek(0, 0, 1.78, 0.1, 0.03, 0.12, STRZECHA_C, v=8)
    sz = bpy.data.objects["strzecha"]
    sz.data.materials.clear()
    sz.data.materials.append(mat_teksturowy("slomа", tex_s, nrm_s, 1.2))
    # żerdzie dachu wystające nad kalenicą (krzyżują się jak w chatach z Palatynu) i wiązania
    for a in (0.4, 1.9, 3.5, 5.0):
        walec((0.5 * math.cos(a), 0.5 * math.sin(a), 1.05), (-0.08 * math.cos(a), -0.08 * math.sin(a), 2.05), 0.022, DREWNO_C, v=5)
    for z, rr in ((0.92, 0.88), (1.16, 0.66)):
        torus(0, 0, z, rr, 0.012, DREWNO_C, seg=20, mseg=3)                   # powrósła ściskające słomę
    # wejście z daszkiem
    box(0, -0.6, 0.03, 0.36, 0.12, 0.62, OTWOR)
    box(0, -0.68, 0.03, 0.48, 0.16, 0.04, DREWNO_C)
    for s_ in (-1, 1):
        cyl(s_ * 0.24, -0.74, 0.03, 0.035, 0.84, DREWNO, v=6)
    box(0, -0.76, 0.82, 0.62, 0.3, 0.06, STRZECHA_C, rot=(-0.3, 0, 0))
    # amfory, dzban, ławka, drewno na opał
    for (x, y, h) in [(0.62, -0.5, 0.26), (0.72, -0.32, 0.22)]:
        cyl(x, y, 0.03, 0.08, h * 0.7, TERAKOTA_C, v=10)
        kula(x, y, 0.03 + h * 0.7, 0.08, TERAKOTA_C, seg=10, ringi=5, skala=(1, 1, 0.8))
        cyl(x, y, 0.03 + h * 0.75, 0.03, h * 0.35, TERAKOTA, v=8)
        for s_ in (-1, 1):
            torus(x + s_ * 0.06, y, 0.03 + h * 0.85, 0.035, 0.01, TERAKOTA_C, rot=(math.pi / 2, 0, 0), seg=8, mseg=3)
    box(0.0, 0.78, 0.03, 0.5, 0.14, 0.16, DREWNO)                             # ławka
    for k in range(4):
        walec_lezacy(-0.72, 0.25 + k * 0.03, 0.06 + (k % 2) * 0.07, 0.04, 0.4, DREWNO_J, os_="y", v=6)


def m_domus():
    """Domus: dom z atrium — białe ściany, czerwone dachówki spadające do środka (compluvium)."""
    baza(1.8, 1.8, TRAWERTYN_C)
    box(0, 0, 0.04, 1.6, 1.6, 0.85, TYNK)
    box(0, 0, 0.04, 1.62, 1.62, 0.18, (196, 92, 70))                          # cokół pompejański
    # dach pierścieniowy: okap 0.84, kalenica 0.55, krawędź compluvium 0.25
    a1, a2, a3 = 0.86, 0.55, 0.24
    z1, z2, z3 = 0.89, 1.3, 1.08
    v = []
    for a, z in ((a1, z1), (a2, z2), (a3, z3), (a3, z1), ):
        v += [(-a, -a, z), (a, -a, z), (a, a, z), (-a, a, z)]
    f = []
    for k in range(3):
        for j in range(4):
            j1 = (j + 1) % 4
            f.append((k * 4 + j, k * 4 + j1, (k + 1) * 4 + j1, (k + 1) * 4 + j))
    for j in range(4):
        j1 = (j + 1) % 4
        f.append((12 + j, 12 + j1, j1, j))
    siatka("dach", v, f, TERAKOTA)
    for k in range(-3, 4):                                                    # rzędy dachówek
        box(k * 0.22, -0.7, 0.98, 0.04, 0.32, 0.04, TERAKOTA_C, rot=(-0.95, 0, 0))
    with Grupa("anim_woda_impluvium", (0, 0, 0.92)):
        box(0, 0, 0.89, 0.5, 0.5, 0.04, WODA, emisja=0.0)                     # impluvium
    box(0, 0, 0.89, 0.56, 0.56, 0.02, MARMUR)
    # front: drzwi (fauces) i dwa sklepiki (tabernae)
    box(0, -0.81, 0.04, 0.32, 0.04, 0.6, DREWNO_C)
    for s in (-1, 1):
        box(s * 0.2, -0.82, 0.04, 0.06, 0.06, 0.66, MARMUR)
        box(s * 0.55, -0.81, 0.04, 0.34, 0.04, 0.5, OTWOR)
        box(s * 0.55, -0.83, 0.54, 0.4, 0.05, 0.05, DREWNO)
    box(0, -0.83, 0.7, 0.46, 0.05, 0.06, MARMUR)
    for s in (-1, 1):                                                         # okienka bocznych ścian
        box(s * 0.81, 0.3, 0.6, 0.04, 0.14, 0.12, OKNO)
    cyl(0.6, 0.6, 0.89, 0.16, 0.02, TRAWA, v=8)


def m_insula():
    """Insula: trzypiętrowa kamienica z cegły, sklepiki na parterze, drewniany balkon."""
    baza(1.8, 1.8, TRAWERTYN_C)
    h = 2.4
    box(0, 0.05, 0.04, 1.6, 1.5, h, CEGLA)
    for z in (0.82, 1.58):
        box(0, 0.05, z, 1.63, 1.53, 0.05, CEGLA_J)
    for i, x in enumerate((-0.52, 0, 0.52)):                                  # sklepiki z łukami
        sciana_lukowa(-0.2, 0.2, 0.04, 0.78, [(0, 0.3, 0.48)], 0.04, CEGLA_J, x=x, y=-0.71)
        box(x, -0.7, 0.04, 0.3, 0.03, 0.6, OTWOR)
    for p in range(2):                                                        # okna pięter
        for x in (-0.52, -0.17, 0.17, 0.52):
            box(x, -0.71, 1.05 + p * 0.76, 0.16, 0.04, 0.28, OKNO)
        for y in (-0.3, 0.3):
            for s in (-1, 1):
                box(s * 0.81, y, 1.05 + p * 0.76, 0.04, 0.16, 0.28, OKNO)
    box(0, -0.8, 0.86, 1.4, 0.2, 0.05, DREWNO)                                # balkon
    for x in (-0.65, -0.3, 0.05, 0.4, 0.65):
        box(x, -0.88, 0.91, 0.03, 0.03, 0.3, DREWNO_C)
    box(0, -0.88, 1.2, 1.4, 0.03, 0.03, DREWNO_C)
    for x in (-0.65, 0.65):
        box(x, -0.87, 0.04, 0.05, 0.05, 0.82, DREWNO_C)
    dach_dwuspadowy(0, 0.05, h + 0.04, 1.76, 1.66, 0.42, TERAKOTA, biodrowy=0.5)
    box(0.35, 0.3, h + 0.2, 0.14, 0.14, 0.28, CEGLA_J)                        # komin
    for x in (-0.3, 0.3):                                                     # donice
        box(x, -0.84, 1.21, 0.2, 0.08, 0.08, TERAKOTA_C)
        kula(x, -0.84, 1.33, 0.07, ZIELEN, seg=6, ringi=4)


def m_pole():
    """Pole pszenicy z bruzdami i snopkami."""
    box(0, 0, 0, 1.8, 1.8, 0.05, ZIEMIA)
    for i in range(7):
        y = -0.78 + i * 0.26
        box(0, y, 0.05, 1.72, 0.08, 0.04, ZIEMIA_J)                           # bruzda
        if i < 6:
            with Grupa("anim_kolys_klosy_%d" % i, (0, y, 0.09)):
                for j in range(9):
                    x = -0.76 + j * 0.19
                    if i == 0 and j > 5:
                        continue
                    stozek(x, y, 0.09, 0.07, 0.04, 0.32, (226, 190, 84) if (i + j) % 3 else (206, 168, 66), v=5)
                    kula(x, y, 0.42, 0.045, (236, 206, 110), seg=5, ringi=3, skala=(1, 1, 1.6))
    for x in (0.5, 0.75):                                                     # snopki
        stozek(x, -0.78, 0.05, 0.1, 0.03, 0.4, (226, 190, 84), v=6)
        torus(x, -0.78, 0.22, 0.075, 0.015, DREWNO_J, seg=8, mseg=4)
    box(-0.88, 0, 0.05, 0.04, 1.8, 0.08, DREWNO_C)


def m_winnica():
    """Winnica: rzędy winorośli na palikach z gronami i drzewo oliwne."""
    box(0, 0, 0, 1.8, 1.8, 0.05, ZIEMIA_J)
    for i, y in enumerate((-0.6, -0.15, 0.3)):
        for x in (-0.8, -0.2, 0.4):
            box(x, y, 0.05, 0.04, 0.04, 0.75, DREWNO_C)
        box(-0.2, y, 0.65, 1.24, 0.015, 0.015, DREWNO_C)
        for k in range(5):
            x = -0.7 + k * 0.25
            ikosfera(x, y, 0.55, 0.16, (70, 128, 56) if k % 2 else (86, 144, 62), skala=(1.2, 0.8, 0.9))
            kula(x + 0.05, y - 0.12, 0.42, 0.05, (96, 40, 90), seg=6, ringi=4, skala=(1, 1, 1.4))
    m_oliwka(0.42, 0.56, 0.75)
    cyl(0.62, -0.62, 0.05, 0.1, 0.22, TERAKOTA_C, v=8)                        # amfora i kosz
    stozek(0.62, -0.62, 0.27, 0.1, 0.03, 0.12, TERAKOTA_C, v=8)
    cyl(0.35, -0.75, 0.05, 0.12, 0.14, STRZECHA_C, v=8)
    for k in range(4):
        kula(0.33 + 0.04 * k, -0.75, 0.21, 0.04, (96, 40, 90), seg=5, ringi=3)


def m_tartak():
    """Tartak: stos bali, kozioł z belką, mała szopa, pień z siekierą."""
    baza(1.8, 1.8, ZIEMIA_J)
    for rzad, n in enumerate((4, 3, 2)):
        for k in range(n):
            x = -0.55 + (k + rzad * 0.5) * 0.22
            walec_lezacy(x, -0.4, 0.14 + rzad * 0.19, 0.1, 0.8, DREWNO_J if (k + rzad) % 2 else DREWNO,
                         os_="y", v=8)
            walec_lezacy(x, -0.8, 0.14 + rzad * 0.19, 0.085, 0.01, (220, 180, 120), os_="y", v=8)
    for s in (-1, 1):                                                         # kozioł
        for t in (-1, 1):
            belka((0.45 + s * 0.1, -0.42 + t * 0.32, 0.04), (0.45 - s * 0.03, -0.42 + t * 0.32, 0.55), 0.04,
                  0.04, DREWNO_C)
    walec_lezacy(0.45, -0.42, 0.58, 0.09, 0.84, DREWNO_J, os_="y", v=8)
    with Grupa("anim_pila", (0.45, -0.6, 0.6)):                              # piła w ruchu
        box(0.45, -0.6, 0.48, 0.02, 0.02, 0.4, STAL)
        box(0.45, -0.6, 0.86, 0.3, 0.03, 0.03, DREWNO_C)
        for sx in (-1, 1):                                                    # ręce tracza na rączce
            belka((0.45 + sx * 0.12, -0.72, 0.62), (0.45 + sx * 0.12, -0.62, 0.86), 0.035, 0.035, SKORA)
    # szopa
    for x in (-0.8, 0.0):
        for y in (0.25, 0.85):
            box(x, y, 0.04, 0.06, 0.06, 1.1 if y > 0.5 else 0.85, DREWNO_C)
    box(-0.4, 0.85, 0.04, 0.85, 0.05, 1.05, DREWNO)
    box(-0.4, 0.52, 0.92, 1.0, 0.68, 0.05, TERAKOTA, rot=(-0.3, 0, 0))
    for k in range(3):
        walec_lezacy(-0.4, 0.62, 0.14 + k * 0.17, 0.08, 0.75, DREWNO_J, os_="x", v=7)
    cyl(0.5, 0.45, 0.04, 0.17, 0.3, DREWNO, v=10)                             # pień z siekierą
    cyl(0.5, 0.45, 0.34, 0.17, 0.005, (220, 180, 120), v=10)
    belka((0.5, 0.45, 0.34), (0.68, 0.45, 0.66), 0.03, 0.03, DREWNO_C)
    box(0.5, 0.45, 0.32, 0.12, 0.02, 0.1, STAL, rot=(0, -0.5, 0))
    for k in range(5):
        box(0.1 + k * 0.05, 0.05 + (k % 2) * 0.08, 0.04, 0.06, 0.02, 0.04, DREWNO_J, rot=(0, 0, k))


def m_kamieniolom():
    """Kamieniołom: ściana skalna, ciosane bloki marmuru i trawertynu, dźwig."""
    baza(1.8, 1.8, (196, 188, 170))
    box(0, 0.6, 0.04, 1.8, 0.6, 1.1, KAMIEN_J)                                # ściana skalna (stopnie)
    box(-0.25, 0.4, 0.04, 1.1, 0.3, 0.6, (204, 200, 190))
    ikosfera(-0.6, 0.6, 1.2, 0.3, KAMIEN, skala=(1, 0.7, 0.6))
    ikosfera(0.45, 0.62, 1.15, 0.36, KAMIEN_C, skala=(1.2, 0.6, 0.5))
    ikosfera(0.15, 0.62, 1.25, 0.25, KAMIEN_J)
    for (x, y, sx, sy, sz, k) in [(-0.5, -0.3, 0.4, 0.3, 0.3, MARMUR), (-0.5, -0.3 + 0.0, 0.3, 0.25, 0.25, MARMUR_C),
                                  (0.1, -0.55, 0.35, 0.35, 0.3, TRAWERTYN), (-0.05, -0.15, 0.3, 0.25, 0.25, MARMUR),
                                  (0.55, -0.6, 0.3, 0.3, 0.28, MARMUR_C)]:
        box(x, y, 0.04, sx, sy, sz, k)
    box(-0.5, -0.3, 0.34, 0.32, 0.26, 0.22, MARMUR_C)
    box(0.1, -0.55, 0.34, 0.25, 0.25, 0.2, MARMUR)
    # dźwig (trójnóg z kołem)
    for (x, y) in [(0.45, 0.05), (0.75, 0.05), (0.6, -0.25)]:
        belka((x, y, 0.04), (0.6, -0.05, 1.3), 0.05, 0.05, DREWNO_C)
    belka((0.6, -0.05, 1.3), (0.2, -0.3, 1.45), 0.04, 0.04, DREWNO)
    walec((0.2, -0.3, 1.45), (0.2, -0.3, 0.6), 0.008, (200, 180, 140), v=4)
    box(0.2, -0.3, 0.45, 0.2, 0.2, 0.15, MARMUR)
    with Grupa("anim_obrot_x_kolo", (0.6, 0.06, 0.4)):                       # koło deptakowe dźwigu
        walec_lezacy(0.6, 0.06, 0.4, 0.22, 0.06, DREWNO, os_="x", v=12)
        for k in range(4):
            a = k * math.pi / 4
            belka((0.63, 0.06 + math.cos(a) * 0.2, 0.4 + math.sin(a) * 0.2),
                  (0.63, 0.06 - math.cos(a) * 0.2, 0.4 - math.sin(a) * 0.2), 0.025, 0.025, DREWNO_C)
    for k in range(4):                                                        # narzędzia i odłamki
        box(-0.2 + k * 0.1, -0.75, 0.04, 0.08, 0.06, 0.05, MARMUR_C, rot=(0, 0, k))
    belka((-0.75, -0.7, 0.04), (-0.7, -0.6, 0.5), 0.025, 0.025, DREWNO_C)
    box(-0.7, -0.6, 0.45, 0.12, 0.03, 0.05, STAL)


def stragan(x, y, kolor, towar):
    for sx in (-0.25, 0.25):
        for sy in (-0.18, 0.18):
            box(x + sx, y + sy, 0.04, 0.04, 0.04, 0.95 if sy > 0 else 0.8, DREWNO_C)
    box(x, y, 0.45, 0.6, 0.42, 0.06, DREWNO)
    box(x, y + 0.02, 0.04, 0.58, 0.38, 0.41, DREWNO_J)
    with Grupa("anim_kolys_markiza_%d_%d" % (int(x * 10 + 10), int(y * 10 + 10)), (x, y + 0.2, 0.95)):
        for i in range(6):                                                    # pasiasta markiza
            box(x - 0.29 + i * 0.116 + 0.058, y - 0.02, 0.86, 0.116, 0.62, 0.025, kolor if i % 2 else BIEL,
                rot=(-0.38, 0, 0))
        for i in range(5):
            box(x - 0.24 + i * 0.12, y - 0.3, 0.69, 0.1, 0.02, 0.07, kolor if i % 2 else BIEL)
    for i in range(4):
        tx = x - 0.2 + i * 0.13
        if towar == "owoce":
            kula(tx, y - 0.05, 0.56, 0.05, [(230, 120, 40), (200, 40, 40), (120, 170, 60), (240, 200, 60)][i],
                 seg=6, ringi=4)
        elif towar == "amfory":
            cyl(tx, y + 0.02, 0.51, 0.045, 0.12, TERAKOTA_C, v=8)
            stozek(tx, y + 0.02, 0.63, 0.045, 0.015, 0.06, TERAKOTA_C, v=8)
        elif towar == "chleb":
            kula(tx, y - 0.03, 0.54, 0.055, (196, 140, 70), seg=8, ringi=4, skala=(1, 1, 0.55))
        else:
            box(tx, y - 0.02, 0.51, 0.1, 0.18, 0.04, [CZERWIEN, NIEBIESKI, ZOLTY, (60, 120, 70)][i])


def m_targ():
    """Targ (macellum): kramy z pasiastymi markizami, amfory, kosze."""
    baza(1.8, 1.8, (200, 190, 170))
    for i in range(4):
        for j in range(4):
            box(-0.675 + i * 0.45, -0.675 + j * 0.45, 0.04, 0.43, 0.43, 0.01, (186, 176, 156))
    stragan(-0.45, -0.35, CZERWIEN, "owoce")
    stragan(0.45, -0.35, (60, 100, 170), "amfory")
    stragan(-0.45, 0.5, (60, 130, 70), "chleb")
    stragan(0.45, 0.5, (220, 170, 40), "tkaniny")
    for (x, y) in [(-0.8, -0.75), (-0.68, -0.8), (0.0, 0.05)]:
        cyl(x, y, 0.04, 0.07, 0.2, TERAKOTA_C, v=8)
        stozek(x, y, 0.24, 0.07, 0.02, 0.1, TERAKOTA_C, v=8)
    cyl(0.75, -0.75, 0.04, 0.1, 0.12, STRZECHA_C, v=8)
    for k in range(3):
        kula(0.72 + k * 0.03, -0.75, 0.18, 0.04, (230, 120, 40), seg=5, ringi=3)
    cyl(0, 0.05, 0.04, 0.16, 0.18, MARMUR_C, v=10)                            # fontanna
    with Grupa("anim_woda_fontanna", (0, 0.05, 0.22)):
        cyl(0, 0.05, 0.2, 0.13, 0.02, WODA, v=10)
    dym(0, 0.05, 0.3, "dym_fontanna")


def swiatynia_bryla(kolor_dach=TERAKOTA, kolor=MARMUR, kolumny_kol=MARMUR, szer=1.35, gl=1.75, h_kol=1.15):
    """Świątynia rzymska: podium ze schodami, kolumnada (pronaos), cella, dach dwuspadowy z tympanonem."""
    yf = -gl / 2
    box(0, 0.05, 0, szer, gl - 0.1, 0.38, TRAWERTYN)                         # podium
    for i in range(5):                                                        # schody
        box(0, yf + 0.03 + i * 0.05, 0, szer * 0.62 + i * 0.006, 0.1, 0.38 - i * 0.076, MARMUR_C)
    for i in range(2):
        box(0, yf + 0.07 + i * 0.04, 0, szer * 0.62 + 0.04 + i * 0.006, 0.05, 0.09, MARMUR)
    z0 = 0.38
    box(0, 0.25, z0, szer * 0.78, gl * 0.62, h_kol, kolor)                    # cella
    box(0, -0.01 + 0.25 - gl * 0.31, z0, 0.26, 0.03, h_kol * 0.7, (150, 104, 54))
    n = 4
    for i in range(n):                                                        # kolumny frontu
        x = -szer / 2 + 0.12 + i * (szer - 0.24) / (n - 1)
        for y in (yf + 0.38, yf + 0.68):
            kolumna(x, y, z0, h_kol, 0.065, kolumny_kol)
    for s in (-1, 1):                                                         # półkolumny boczne
        for k in range(3):
            cyl(s * szer * 0.39, 0.05 + k * 0.35, z0, 0.05, h_kol, kolor, v=8)
    ze = z0 + h_kol
    box(0, 0.03, ze, szer + 0.04, gl - 0.6, 0.14, kolor)                     # belkowanie
    box(0, 0.03, ze + 0.04, szer + 0.06, gl - 0.58, 0.03, MARMUR_C)
    dach_dwuspadowy(0, 0.03, ze + 0.14, szer + 0.14, gl - 0.5, 0.38, kolor_dach, wzdluz="y")
    fronton(0, 0.03 - (gl - 0.5) / 2 - 0.012, ze + 0.14, szer + 0.14, 0.38, kolor, gl=0.05)
    fronton(0, 0.03 - (gl - 0.5) / 2 - 0.03, ze + 0.16, szer * 0.72, 0.25, MARMUR_C, gl=0.02)
    kula(0, 0.03 - (gl - 0.5) / 2, ze + 0.56, 0.05, ZLOTO, seg=6, ringi=4, metal=0.6)


def m_swiatynia():
    swiatynia_bryla()
    box(0.55, -0.82, 0, 0.18, 0.12, 0.18, MARMUR)                             # ołtarz
    with Grupa("anim_ogien_oltarz", (0.55, -0.82, 0.18)):
        stozek(0.55, -0.82, 0.18, 0.06, 0.0, 0.16, (255, 150, 40), v=6, emisja=3.0)
        stozek(0.57, -0.81, 0.18, 0.035, 0.0, 0.11, (255, 220, 90), v=5, emisja=4.0)
    dym(0.55, -0.82, 0.4, "dym_kadzidlo")


def namiot(x, y, sx, sy, h, kolor, wzdluz="y"):
    dach_dwuspadowy(x, y, 0, sx, sy, h, kolor, wzdluz=wzdluz)
    if wzdluz == "y":
        box(x, y - sy / 2 - 0.005, 0, sx * 0.25, 0.02, h * 0.6, tuple(int(c * .55) for c in kolor))


_wexillum_nr = [0]


def wexillum(x, y, z0, h=1.5, kolor=CZERWIEN, napis_=True):
    cyl(x, y, z0, 0.02, h, DREWNO_C, v=6)
    box(x, y, z0 + h - 0.12, 0.34, 0.02, 0.02, DREWNO_C)
    _wexillum_nr[0] += 1
    with Grupa("anim_kolys_sztandar_%d" % _wexillum_nr[0], (x, y, z0 + h - 0.12)):
        box(x, y, z0 + h - 0.5, 0.3, 0.02, 0.38, kolor)
        for k in range(3):
            box(x - 0.1 + k * 0.1, y, z0 + h - 0.56, 0.02, 0.015, 0.07, ZLOTO)
        if napis_:
            box(x, y - 0.012, z0 + h - 0.36, 0.2, 0.01, 0.07, ZLOTO)
    kula(x, y, z0 + h + 0.03, 0.04, ZLOTO, seg=6, ringi=4, metal=0.6)


def m_koszary():
    """Castra: kwadrat palisady z bramą, namioty skórzane (papiliones), sztandar."""
    baza(1.8, 1.8, (170, 150, 110))
    pale = [-0.82 + i * 0.0911 for i in range(19)]
    for p in pale:                                                            # palisada
        h = 0.5 + 0.03 * (round(p / 0.0911) % 2)
        cyl(p, 0.82, 0.04, 0.035, h, DREWNO, v=5)
        cyl(-0.82, p, 0.04, 0.035, h, DREWNO, v=5)
        cyl(0.82, p, 0.04, 0.035, h, DREWNO, v=5)
        if abs(p) >= 0.2:                                                     # brama we froncie
            cyl(p, -0.82, 0.04, 0.035, h, DREWNO, v=5)
    for s in (-1, 1):
        box(s * 0.24, -0.82, 0.04, 0.12, 0.12, 0.85, DREWNO_C)               # wieżyczki bramy
        box(s * 0.24, -0.82, 0.89, 0.2, 0.2, 0.05, DREWNO)
    box(0, -0.82, 0.75, 0.6, 0.06, 0.06, DREWNO_C)
    for (x, y) in [(-0.45, 0.4), (0.0, 0.4), (0.45, 0.4), (-0.45, -0.15)]:
        namiot(x, y, 0.32, 0.5, 0.36, (200, 176, 130))
    box(0.4, -0.25, 0.04, 0.45, 0.3, 0.3, DREWNO_J)                          # namiot dowódcy / skrzynie
    namiot(0.4, -0.25, 0.5, 0.36, 0.42, (220, 210, 190))
    wexillum(0.0, -0.3, 0.04, 1.55)
    for k in range(3):                                                        # tarcze przy namiocie
        box(-0.15 + k * 0.08, 0.05, 0.04, 0.07, 0.02, 0.22, CZERWIEN, rot=(-0.2, 0, 0))


def blanki(x0, x1, y, z, gl, kolor, szer=0.12, odstep=0.22, h=0.14):
    n = int((x1 - x0) / odstep)
    for i in range(n + 1):
        box(x0 + i * (x1 - x0) / n, y, z, szer, gl, h, kolor)


def m_mury():
    """Odcinek murów (wzdłuż osi X) z blankami i małą basztą."""
    gl = 0.45
    box(0, 0, 0, 1.8, gl, 1.2, TRAWERTYN)
    box(0, 0, 0, 1.8, gl + 0.04, 0.2, TRAWERTYN_C)
    for z in (0.45, 0.8):
        box(0, -gl / 2 - 0.005, z, 1.8, 0.01, 0.025, TRAWERTYN_C)
    blanki(-0.84, 0.84, -gl / 2 + 0.06, 1.2, 0.1, TRAWERTYN, odstep=0.21)
    blanki(-0.84, 0.84, gl / 2 - 0.06, 1.2, 0.1, TRAWERTYN, odstep=0.21)
    box(0, 0.0, 0, 0.64, 0.7, 1.75, TRAWERTYN_C)                              # baszta
    box(0, 0.0, 1.75, 0.72, 0.78, 0.08, TRAWERTYN)
    for sx in (-1, 0, 1):
        for sy in (-1, 1):
            box(sx * 0.3, sy * 0.33, 1.83, 0.12, 0.12, 0.16, TRAWERTYN)
            box(sy * 0.33, sx * 0.3, 1.83, 0.12, 0.12, 0.16, TRAWERTYN)
    for z in (0.7, 1.3):
        box(0, -0.355, z, 0.05, 0.02, 0.2, OTWOR)                             # strzelnice
    dach_dwuspadowy(0, 0, 1.99, 0.5, 0.5, 0.35, TERAKOTA, biodrowy=0.25)


def m_port():
    """Port: nabrzeże z kamienia, drewniane molo nad wodą, łódka, skrzynie i amfory."""
    with Grupa("anim_woda_port", (0, -0.35, 0.02)):
        box(0, -0.35, 0, 1.8, 1.1, 0.02, WODA)
    box(0, 0.55, 0, 1.8, 0.7, 0.22, TRAWERTYN)
    for x in (-0.6, 0, 0.6):
        box(x, 0.2, 0.0, 0.58, 0.02, 0.2, TRAWERTYN_C)
    for y in (-0.7, -0.35, 0.0):                                              # molo na palach
        for x in (-0.05, 0.35):
            cyl(x, y, 0, 0.04, 0.22, DREWNO_C, v=6)
    for k in range(9):
        box(0.15, 0.15 - k * 0.11, 0.2, 0.52, 0.1, 0.03, DREWNO_J if k % 2 else DREWNO)
    cyl(0.38, -0.8, 0.0, 0.05, 0.32, DREWNO_C, v=6)                           # pachołek
    with Grupa("anim_lodz", (-0.45, -0.42, 0.0)):                            # łódka kołysze się na wodzie
        kadlub(0.95, 0.32, 0.18, DREWNO, x=-0.45, y=-0.42)
        for k in range(3):
            box(-0.45, -0.55 + k * 0.15, 0.1, 0.28, 0.03, 0.02, DREWNO_J)
        walec((-0.45, -0.3, 0.12), (-0.45, -0.3, 0.9), 0.02, DREWNO_C, v=5)
        box(-0.45, -0.31, 0.45, 0.4, 0.02, 0.4, KREM)
    for (x, y, s) in [(-0.6, 0.6, 0.24), (-0.32, 0.6, 0.2), (-0.47, 0.6, 0.18)]:
        box(x, y, 0.22 + (0.24 if s == 0.18 else 0), s, s, s, DREWNO_J)
    for k in range(4):                                                        # amfory
        x = 0.4 + k * 0.12
        cyl(x, 0.55, 0.22, 0.05, 0.16, TERAKOTA_C, v=8)
        stozek(x, 0.55, 0.38, 0.05, 0.015, 0.08, TERAKOTA_C, v=8)
        stozek(x, 0.55, 0.12 + 0.1, 0.0, 0.05, 0.0001, TERAKOTA_C, v=6)
    walec((0.1, 0.42, 0.25), (0.35, -0.6, 0.23), 0.012, (200, 180, 140), v=4)  # lina


def m_akwedukt():
    """Akwedukt: odcinek dwukondygnacyjnych arkad wzdłuż osi X, na górze kanał (specus)."""
    arkada(-0.9, 0.9, 0.0, 1.35, 3, 0.95, 0.36, TRAWERTYN)
    box(0, 0, 1.3, 1.8, 0.4, 0.07, TRAWERTYN_C)
    arkada(-0.9, 0.9, 1.37, 2.25, 6, 2.0, 0.3, TRAWERTYN)
    box(0, 0, 2.25, 1.8, 0.34, 0.08, TRAWERTYN_C)
    box(0, 0, 2.33, 1.8, 0.3, 0.26, TRAWERTYN)                                # kanał
    box(0, 0, 2.59, 1.8, 0.34, 0.05, TRAWERTYN_C)
    box(0, -0.11, 2.36, 1.79, 0.02, 0.2, (180, 168, 140))
    for x in (-0.9, -0.3, 0.3, 0.9):                                          # podstawy filarów
        box(max(-0.78, min(0.78, x)), 0, 0, 0.24, 0.42, 0.12, TRAWERTYN_C)


def m_termy():
    """Termy: ceglana hala z kopułą, skrzydła z dachówką, wielkie okna i basen."""
    baza(1.8, 1.8, TRAWERTYN_C)
    box(0, 0.25, 0.04, 1.1, 1.0, 1.1, CEGLA_J)                                # hala centralna
    cyl(0, 0.25, 1.14, 0.48, 0.16, CEGLA_J, v=16)
    kopula(0, 0.25, 1.3, 0.48, (214, 200, 176), seg=16, ringi=6)
    cyl(0, 0.25, 1.75, 0.09, 0.06, MARMUR_C, v=10)
    for s in (-1, 1):                                                         # skrzydła
        box(s * 0.68, 0.25, 0.04, 0.4, 0.85, 0.72, CEGLA)
        dach_dwuspadowy(s * 0.67, 0.25, 0.76, 0.44, 0.92, 0.26, TERAKOTA, wzdluz="y")
        for y in (0.05, 0.45):
            box(s * 0.885, y, 0.3, 0.02, 0.12, 0.3, OKNO)
    sciana_lukowa(-0.55, 0.55, 0.04, 1.1, [(-0.3, 0.26, 0.55), (0.0, 0.26, 0.55), (0.3, 0.26, 0.55)], 0.06,
                  CEGLA_J, y=-0.25)
    for x in (-0.3, 0.0, 0.3):
        box(x, -0.22, 0.04, 0.26, 0.02, 0.62, (120, 160, 190))                # szklenie / światło
    for x in (-0.48, -0.15, 0.15, 0.48):                                      # portyk
        kolumna(x, -0.42, 0.04, 0.75, 0.04, MARMUR)
    box(0, -0.38, 0.79, 1.15, 0.2, 0.08, MARMUR)
    # basen (natatio)
    box(0, -0.72, 0.04, 1.5, 0.32, 0.06, MARMUR_C)
    with Grupa("anim_woda_basen", (0, -0.72, 0.11)):
        box(0, -0.72, 0.06, 1.38, 0.24, 0.05, (90, 170, 200))
    for x in (-0.82, 0.82):
        cyl(x, -0.72, 0.04, 0.05, 0.2, MARMUR_C, v=8)


def amfiteatr_bryla(rx, ry, kondygnacje, h_kond, n, attyka=0.0, ruina=None, kolor=TRAWERTYN, gl=0.1):
    """Eliptyczny amfiteatr z arkadami na każdej kondygnacji i widownią w środku."""
    def punkt(a, rx_, ry_):
        return Vector((rx_ * math.cos(a), ry_ * math.sin(a), 0))
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = 2 * math.pi * (i + 1) / n
        p0, p1 = punkt(a0, rx, ry), punkt(a1, rx, ry)
        d = p1 - p0
        sr = (p0 + p1) / 2
        rz = math.atan2(d.y, d.x)
        dl = d.length + 0.01
        nk = kondygnacje if ruina is None else ruina(i)
        for k in range(nk):
            z0 = k * h_kond
            arkada(-dl / 2, dl / 2, z0, z0 + h_kond, 1, z0 + h_kond * 0.5, gl, kolor, x=sr.x, y=sr.y, rz=rz,
                   filar=dl * 0.22)
        if nk == kondygnacje and attyka:
            sciana = profil_xz([(-dl / 2, 0), (dl / 2, 0), (dl / 2, attyka), (-dl / 2, attyka)], gl, kolor,
                               x=sr.x, y=sr.y, rz=rz)
            sciana.location.z = nk * h_kond
            box(sr.x, sr.y, nk * h_kond + attyka * 0.45, 0.06, 0.02, 0.1, OTWOR, rot=(0, 0, rz))
        if nk:
            cz = profil_xz([(-dl / 2, 0), (dl / 2, 0), (dl / 2, 0.03), (-dl / 2, 0.03)], gl + 0.03, TRAWERTYN_C,
                           x=sr.x, y=sr.y, rz=rz)
            cz.location.z = 0.0
    # widownia (cavea) schodkami w dół do areny
    stopnie = 5
    htop = kondygnacje * h_kond * 0.85
    for s in range(stopnie):
        f1 = 1 - s / stopnie * 0.55
        f2 = 1 - (s + 1) / stopnie * 0.55
        pierscien(0, 0, 0, htop * (1 - s / stopnie) + 0.02, rx * f1 - gl / 2, ry * f1 - gl / 2,
                  rx * f2 - gl / 2, ry * f2 - gl / 2, MARMUR_C if s % 2 else KAMIEN_J, n=n)
    fa = 0.45 - 0.0
    cyl(0, 0, 0, 1.0, 0.04, PIASEK, v=24).scale = (rx * fa, ry * fa, 1)      # arena


def m_amfiteatr():
    baza(1.8, 1.8, TRAWERTYN_C, h=0.02)
    amfiteatr_bryla(0.82, 0.68, 2, 0.45, 16, attyka=0.15)
    for s in (-1, 1):                                                         # bramy wejściowe
        box(s * 0.83, 0, 0, 0.1, 0.2, 0.4, OTWOR)
    wexillum(0.0, 0.75, 1.05, 0.6, kolor=CZERWIEN, napis_=False)


def m_kuria():
    """Kuria (Curia Julia): wysoki ceglany budynek z tympanonem, schodami i brązowymi drzwiami."""
    baza(1.8, 1.8, TRAWERTYN_C)
    box(0, 0.15, 0.04, 1.3, 1.4, 2.2, CEGLA)
    box(0, -0.555, 0.04, 1.32, 0.02, 0.9, (226, 214, 190))                   # tynk imitujący marmur
    for s in (-1, 1):
        box(s * 0.66, 0.15, 0.04, 0.02, 1.42, 0.9, (226, 214, 190))
    for i in range(4):                                                        # schody
        box(0, -0.62 - i * 0.07, 0.04, 0.7 + i * 0.006, 0.14, 0.24 - i * 0.06, MARMUR_C)
    box(0, -0.57, 0.04, 0.38, 0.03, 0.82, BRAZ_C, metal=0.4)                  # drzwi z brązu
    for z in (0.3, 0.6):
        box(0, -0.59, 0.04 + z, 0.36, 0.01, 0.02, BRAZ, metal=0.6)
    for x in (-0.35, 0, 0.35):                                                # trzy okna
        box(x, -0.56, 1.45, 0.24, 0.02, 0.42, OKNO)
        box(x, -0.565, 1.42, 0.3, 0.02, 0.04, MARMUR_C)
    box(0, -0.565, 0.98, 1.32, 0.03, 0.06, MARMUR_C)
    box(0, 0.15, 2.24, 1.38, 1.48, 0.08, MARMUR_C)                            # gzyms
    dach_dwuspadowy(0, 0.15, 2.32, 1.4, 1.5, 0.45, TERAKOTA, wzdluz="y")
    fronton(0, 0.15 - 0.762, 2.32, 1.4, 0.45, CEGLA_J, gl=0.04)
    fronton(0, 0.15 - 0.785, 2.37, 1.0, 0.3, (226, 214, 190), gl=0.02)
    kula(0, -0.6, 2.8, 0.05, ZLOTO, seg=6, ringi=4, metal=0.6)
    for s in (-1, 1):
        box(s * 0.62, -0.58, 2.32, 0.08, 0.08, 0.12, ZLOTO, metal=0.5)


def m_bazylika():
    """Bazylika wczesnochrześcijańska: wysoka nawa, niższe nawy boczne, apsyda i krzyż."""
    baza(1.8, 1.8, TRAWERTYN_C)
    box(0, -0.05, 0.04, 0.6, 1.4, 1.7, (226, 206, 170))                       # nawa główna
    dach_dwuspadowy(0, -0.05, 1.74, 0.7, 1.45, 0.32, TERAKOTA, wzdluz="y")
    for s in (-1, 1):                                                         # nawy boczne
        box(s * 0.5, -0.05, 0.04, 0.42, 1.3, 1.0, (214, 192, 156))
        box(s * 0.5, -0.05, 1.04, 0.5, 1.36, 0.06, TERAKOTA, rot=(0, s * 0.35, 0))
        for k in range(4):
            y = -0.55 + k * 0.33
            box(s * 0.305, y, 1.25, 0.02, 0.1, 0.25, OKNO)                    # okna clerestorium
            box(s * 0.715, y, 0.45, 0.02, 0.1, 0.3, OKNO)
    cyl(0, 0.56, 0.04, 0.3, 1.2, (214, 192, 156), v=16)                      # apsyda
    stozek(0, 0.56, 1.24, 0.33, 0.02, 0.32, TERAKOTA, v=16)
    box(0, -0.75, 0.04, 1.2, 0.16, 0.85, (206, 184, 150))                     # narteks
    for x in (-0.4, -0.13, 0.13, 0.4):
        cyl(x, -0.84, 0.04, 0.035, 0.78, MARMUR, v=8)
    box(0, -0.84, 0.04, 0.22, 0.02, 0.55, DREWNO_C)
    box(0, -0.72, 0.89, 1.24, 0.24, 0.05, TERAKOTA)
    sciana_lukowa(-0.12, 0.12, 1.1, 1.5, [(0, 0.16, 1.28)], 0.02, OTWOR, y=-0.76)
    box(0, -0.75, 1.15, 0.12, 0.02, 0.18, (240, 200, 90), emisja=0.4)       # okno fasady
    box(0, -0.78, 2.04, 0.05, 0.05, 0.45, ZLOTO, metal=0.5)                   # krzyż
    box(0, -0.78, 2.3, 0.26, 0.05, 0.05, ZLOTO, metal=0.5)


def m_rusztowanie():
    """Rusztowanie: budowa w toku — drewniane słupy, pomosty, drabina, mury do połowy, kozioł z bloczkiem."""
    baza(1.8, 1.8, ZIEMIA_J)
    box(0, 0.25, 0.04, 1.2, 0.9, 0.7, TRAWERTYN)
    box(-0.3, 0.25, 0.74, 0.6, 0.9, 0.3, TRAWERTYN)
    for sx in (-0.75, 0, 0.75):
        for sy in (-0.4, 0.85):
            box(sx, sy, 0.04, 0.06, 0.06, 1.9, DREWNO_J)
    for z in (0.6, 1.2, 1.8):
        for sy in (-0.4, 0.85):
            box(0, sy, z, 1.56, 0.05, 0.05, DREWNO)
        box(0, -0.4, z - 0.03, 1.56, 0.3, 0.04, DREWNO_J)
    for sy in (-0.4, 0.85):
        belka((-0.75, sy, 0.1), (0, sy, 1.15), 0.035, 0.035, DREWNO)
        belka((0, sy, 0.65), (0.75, sy, 1.75), 0.035, 0.035, DREWNO)
    belka((0.86, -0.55, 0.04), (0.86, -0.45, 1.25), 0.03, 0.03, DREWNO_C)    # drabina
    belka((0.66, -0.55, 0.04), (0.66, -0.45, 1.25), 0.03, 0.03, DREWNO_C)
    for k in range(6):
        box(0.76, -0.55 + k * 0.018, 0.2 + k * 0.19, 0.2, 0.025, 0.025, DREWNO_C)
    for (x, y) in [(-0.6, -0.75), (-0.32, -0.75), (-0.46, -0.75)]:
        box(x, y, 0.04 + (0.2 if x == -0.46 else 0), 0.26, 0.24, 0.2, TRAWERTYN)
    walec((0.2, -0.4, 1.83), (0.2, -0.4, 2.4), 0.03, DREWNO_C, v=6)           # bloczek
    belka((0.2, -0.4, 2.4), (0.2, -0.75, 2.3), 0.03, 0.03, DREWNO_C)


# ----------------------------------------------------------------- ożywienie budynków: detale i ruchome części
def zycie_chata():
    dym(0, 0, 1.92, "dym_strzecha")
    with Grupa("anim_ogien_palenisko", (-0.55, -0.62, 0.05)):                 # palenisko przed chatą
        stozek(-0.55, -0.62, 0.05, 0.07, 0.0, 0.18, (255, 140, 30), v=6, emisja=3.0)
        stozek(-0.53, -0.61, 0.05, 0.04, 0.0, 0.12, (255, 210, 80), v=5, emisja=4.0)
    for i in range(7):
        a = i * 2 * math.pi / 7
        ikosfera(-0.55 + 0.12 * math.cos(a), -0.62 + 0.12 * math.sin(a), 0.05, 0.035, KAMIEN)
    for k in range(7):                                                        # płot z wikliny
        cyl(0.2 + k * 0.1, 0.78, 0.04, 0.015, 0.3, DREWNO_C, v=4)
    box(0.5, 0.78, 0.22, 0.62, 0.02, 0.08, STRZECHA_C)
    ludzik(-0.3, -0.78, -2.06, (176, 150, 110), "mlot", "mlot", "rzemieslnik", 0.85)


def zycie_domus():
    box(-0.55, 0.55, 1.1, 0.12, 0.12, 0.32, TRAWERTYN_C)                       # komin kuchni
    dym(-0.55, 0.55, 1.45, "dym_kuchnia")
    for (x, y) in [(0.75, -0.78), (-0.75, -0.78)]:                            # donice z oleandrem
        cyl(x, y, 0.04, 0.06, 0.1, TERAKOTA_C, v=8)
        kula(x, y, 0.2, 0.07, (60, 120, 60), seg=6, ringi=4)
        kula(x + 0.03, y - 0.03, 0.25, 0.025, (230, 120, 160), seg=5, ringi=3)


def zycie_insula():
    dym(0.35, 0.3, 2.95, "dym_komin")
    with Grupa("anim_kolys_pranie", (0, -0.9, 1.2)):                         # pranie na balkonie
        for k, kol in enumerate([(220, 70, 60), (240, 236, 220), (80, 110, 180), (230, 190, 70)]):
            box(-0.45 + k * 0.28, -0.9, 1.06, 0.16, 0.012, 0.14, kol)
    for s_ in (-1, 1):                                                        # markizy sklepików
        box(s_ * 0.52, -0.82, 0.72, 0.3, 0.16, 0.02, (196, 160, 90), rot=(-0.4, 0, 0))


def zycie_pole():
    with Grupa("anim_kolys_strach", (0.7, 0.55, 0.05)):                       # strach na wróble
        belka((0.7, 0.55, 0.05), (0.7, 0.55, 0.85), 0.03, 0.03, DREWNO_C)
        belka((0.5, 0.55, 0.65), (0.9, 0.55, 0.65), 0.025, 0.025, DREWNO_C)
        box(0.7, 0.55, 0.45, 0.2, 0.08, 0.26, (150, 120, 80))
        kula(0.7, 0.55, 0.82, 0.07, STRZECHA, seg=6, ringi=4)
        stozek(0.7, 0.55, 0.86, 0.11, 0.02, 0.09, STRZECHA_C, v=8)


def zycie_winnica():
    ludzik(-0.45, -0.85, math.pi, (120, 140, 90), "mlot", "kosz", "winiarz", 0.85)


def zycie_tartak():
    ludzik(0.45, -0.82, math.pi, (140, 90, 60), "kolys", None, "tracz", 0.9)
    dym(-0.75, 0.15, 0.3, "dym_ognisko")


def zycie_kamieniolom():
    ludzik(-0.05, -0.5, math.pi - 0.3, (170, 150, 120), "mlot", "kilof", "kamieniarz", 0.9)
    ludzik(-0.78, -0.3, math.pi / 2, (150, 80, 60), "mlot", "mlot", "ciosacz", 0.85)


def zycie_targ():
    ludzik(-0.1, -0.78, 0.0, (60, 100, 170), "kolys", None, "kupiec", 0.85)


def zycie_koszary():
    cyl(-0.55, -0.45, 0.04, 0.04, 0.6, DREWNO_C, v=6)                         # palus – słup do ćwiczeń
    ludzik(-0.55, -0.22, 0.0, CZERWIEN, "mlot", "miecz", "legionista", 0.9)
    with Grupa("anim_ogien_pochodnia", (-0.2, -0.86, 0.95)):
        stozek(-0.2, -0.86, 0.95, 0.04, 0.0, 0.12, (255, 160, 40), v=5, emisja=3.5)


def zycie_mury():
    flaga(0.22, -0.2, 2.1, 0.55, CZERWIEN, "baszta")
    for x in (-0.6, 0.6):
        with Grupa("anim_ogien_pochodnia_%d" % int(x * 10 + 10), (x, -0.27, 1.0)):
            stozek(x, -0.27, 1.0, 0.035, 0.0, 0.11, (255, 160, 40), v=5, emisja=3.5)
        box(x, -0.25, 0.92, 0.03, 0.05, 0.1, DREWNO_C)


def zycie_port():
    cyl(0.7, 0.45, 0.22, 0.05, 1.2, DREWNO_C, v=6)                            # żuraw portowy
    with Grupa("anim_obrot_z_zuraw", (0.7, 0.45, 1.4)):
        belka((0.7, 0.45, 1.4), (0.2, -0.05, 1.6), 0.04, 0.04, DREWNO)
        walec((0.2, -0.05, 1.6), (0.2, -0.05, 0.85), 0.006, (200, 180, 140), v=4)
        box(0.2, -0.05, 0.72, 0.14, 0.14, 0.13, (180, 150, 100))
    flaga(0.85, 0.85, 0.22, 0.9, (60, 100, 170), "port", szer=0.22)


def zycie_akwedukt():
    with Grupa("anim_woda_kanal", (0, 0, 2.66)):
        box(0, 0, 2.64, 1.78, 0.18, 0.02, WODA)


def zycie_termy():
    box(0.55, 0.78, 0.04, 0.16, 0.16, 1.45, CEGLA)                            # komin pieca (praefurnium)
    dym(0.55, 0.78, 1.55, "dym_piec")
    dym(0, -0.72, 0.15, "dym_para")


def zycie_amfiteatr():
    for i, a in enumerate((0.6, 2.2, 3.8, 5.3)):
        flaga(0.8 * math.cos(a), 0.66 * math.sin(a), 0.9, 0.45, (220, 180, 60) if i % 2 else CZERWIEN, "velarium_%d" % i, szer=0.18)


def zycie_kuria():
    for s_ in (-1, 1):
        flaga(s_ * 0.5, -0.75, 0.04, 1.25, CZERWIEN, "spqr_%d" % (s_ + 1), szer=0.22)


def zycie_bazylika():
    for s_ in (-1, 1):
        with Grupa("anim_ogien_lampa_%d" % (s_ + 1), (s_ * 0.27, -0.9, 0.62)):
            stozek(s_ * 0.27, -0.9, 0.62, 0.025, 0.0, 0.08, (255, 190, 70), v=5, emisja=4.0)
        box(s_ * 0.27, -0.9, 0.5, 0.06, 0.06, 0.12, BRAZ_C, metal=0.4)


def zycie_rusztowanie():
    ludzik(-0.25, -0.4, math.pi, (170, 150, 120), "mlot", "mlot", "murarz", 0.85)
    ludzik(0.45, -0.75, 0.4, (140, 90, 60), "kolys", None, "pomocnik", 0.85)
    with Grupa("anim_kolys_ladunek", (0.2, -0.75, 2.3)):
        walec((0.2, -0.75, 2.3), (0.2, -0.75, 0.5), 0.006, (200, 180, 140), v=4)
        box(0.2, -0.75, 0.35, 0.2, 0.2, 0.15, TRAWERTYN)


ZYCIE = {"chata": zycie_chata, "domus": zycie_domus, "insula": zycie_insula, "pole": zycie_pole,
         "winnica": zycie_winnica, "tartak": zycie_tartak, "kamieniolom": zycie_kamieniolom, "targ": zycie_targ,
         "koszary": zycie_koszary, "mury": zycie_mury, "port": zycie_port, "akwedukt": zycie_akwedukt,
         "termy": zycie_termy, "amfiteatr": zycie_amfiteatr, "kuria": zycie_kuria, "bazylika": zycie_bazylika,
         "rusztowanie": zycie_rusztowanie}


# ================================================================= ZABYTKI (1 pole, ≤ 5 m)
def m_wilczyca():
    """Wilczyca kapitolińska karmiąca Romulusa i Remusa, na marmurowym cokole (legenda)."""
    box(0, 0, 0, 1.3, 0.75, 0.15, MARMUR_C)
    box(0, 0, 0.15, 1.15, 0.6, 0.75, MARMUR)
    box(0, -0.31, 0.35, 0.7, 0.02, 0.3, BRAZ_C, metal=0.4)                    # tablica
    napis("SPQR", 0, -0.33, 0.5, 0.17, ZLOTO, gl=0.01, metal=0.6, szorstkosc=0.4)
    box(0, 0, 0.9, 1.2, 0.65, 0.06, MARMUR_C)
    WB = (110, 78, 42)
    z = 0.96
    kula(0.05, 0, z + 0.5, 0.2, WB, seg=12, ringi=8, skala=(2.2, 0.9, 0.95), metal=0.5, szorstkosc=0.45)
    kula(-0.28, 0, z + 0.54, 0.19, WB, seg=10, ringi=7, skala=(1.2, 1, 1.1), metal=0.5, szorstkosc=0.45)
    for (x, y) in [(-0.3, -0.1), (-0.3, 0.1), (0.38, -0.1), (0.38, 0.1)]:
        walec((x, y, z), (x * 0.95, y, z + 0.45), 0.045, WB, v=6, metal=0.5, szorstkosc=0.45)
    walec((-0.4, -0.03, z + 0.62), (-0.52, -0.1, z + 0.78), 0.1, WB, v=8, metal=0.5, szorstkosc=0.45)   # szyja
    kula(-0.55, -0.13, z + 0.82, 0.11, WB, seg=10, ringi=6, metal=0.5, szorstkosc=0.45)                 # głowa
    walec((-0.58, -0.17, z + 0.8), (-0.72, -0.32, z + 0.76), 0.06, WB, v=6, r2=0.03, metal=0.5,
          szorstkosc=0.45)                                                    # pysk
    for s in (-1, 1):
        stozek(-0.53 + s * 0.05, -0.1 + s * 0.05, z + 0.89, 0.04, 0.0, 0.1, WB, v=4, metal=0.5)
        kula(-0.62, -0.19 + s * 0.04, z + 0.86, 0.015, CZARNY, seg=4, ringi=3)
    for k in range(4):                                                        # grzywa
        kula(-0.3 + k * 0.06, 0, z + 0.72 - k * 0.02, 0.06, (96, 66, 34), seg=5, ringi=3, skala=(1, 1.3, 0.6))
    walec((0.48, 0, z + 0.55), (0.62, 0, z + 0.3), 0.04, WB, v=6, r2=0.02, metal=0.5)                   # ogon
    for k in range(4):                                                        # sutki
        kula(-0.05 + k * 0.1, -0.03, z + 0.33, 0.025, WB, seg=5, ringi=3, metal=0.5)
    BL = (172, 130, 74)
    for (x, ss) in [(-0.06, 1), (0.22, -1)]:                                  # bliźnięta
        kula(x, -0.08, z + 0.1, 0.08, BL, seg=8, ringi=6, skala=(1, 1, 1.2), metal=0.4, szorstkosc=0.5)
        kula(x + ss * 0.02, -0.1, z + 0.24, 0.065, BL, seg=8, ringi=6, metal=0.4, szorstkosc=0.5)
        walec((x, -0.1, z + 0.12), (x - ss * 0.05, -0.12, z + 0.3), 0.022, BL, v=5, metal=0.4)
        walec((x, -0.12, z + 0.02), (x + ss * 0.1, -0.2, z + 0.03), 0.025, BL, v=5, metal=0.4)


def m_kapitol():
    """Wzgórze Kapitolińskie: skała z zielenią i świątynia Jowisza Kapitolińskiego na szczycie."""
    stozek(0, 0, 0, 0.88, 0.8, 1.0, (150, 136, 112), v=9)
    for (x, y, z, r, k) in [(-0.6, -0.5, 0.4, 0.4, KAMIEN), (0.65, -0.45, 0.35, 0.38, KAMIEN_C),
                            (0.6, 0.55, 0.5, 0.4, (150, 136, 112)), (-0.55, 0.6, 0.45, 0.42, KAMIEN_C),
                            (0.0, -0.75, 0.25, 0.3, KAMIEN_J)]:
        ikosfera(x * 0.9, y * 0.9, z, r * 0.85, k, skala=(1, 1, 0.9))
    for (x, y) in [(-0.72, -0.2), (0.72, 0.2), (0.3, -0.68)]:
        ikosfera(x, y, 0.75, 0.18, (70, 120, 58))
    kula(-0.6, 0.6, 1.05, 0.12, (40, 86, 50), seg=6, ringi=5, skala=(1, 1, 2.5))   # cyprysy
    kula(0.65, 0.55, 1.05, 0.12, (40, 86, 50), seg=6, ringi=5, skala=(1, 1, 2.5))
    box(0, 0, 0.98, 1.6, 1.6, 0.04, TRAWERTYN_C)
    for i in range(6):                                                        # schody na stoku
        box(0, -0.9 + i * 0.075, 0.0, 0.4, 0.075, 0.18 + i * 0.16, TRAWERTYN)
    wstaw(swiatynia_bryla, z=1.02, s=0.88, a=(ZLOTO, MARMUR, MARMUR, 1.5, 1.7, 1.25))


def m_koloseum():
    """Koloseum w miniaturze: trzy kondygnacje arkad i attyka, z jednej strony częściowo zrujnowane."""
    def ruina(i):
        # segmenty 9..13 (od strony -X/-Y) mają obniżony wierzch — jak dzisiejsza ruina
        return {11: 2, 12: 1, 13: 1, 14: 2, 15: 2}.get(i, 3)
    amfiteatr_bryla(0.83, 0.72, 3, 0.5, 20, attyka=0.32, ruina=ruina, gl=0.12)
    for (x, y, s) in [(-0.4, -0.8, 0.12), (-0.25, -0.82, 0.09), (-0.55, -0.74, 0.1)]:
        box(x, y, 0, s * 1.5, s, s, TRAWERTYN_C, rot=(0, 0, x * 3))


def m_panteon():
    """Panteon: rotunda z kopułą i oculusem, portyk z ośmioma kolumnami i tympanonem."""
    baza(1.8, 1.8, TRAWERTYN_C)
    cyl(0, 0.21, 0.04, 0.67, 0.95, (218, 206, 182), v=24)
    cyl(0, 0.21, 0.6, 0.68, 0.04, MARMUR_C, v=24)
    for k in range(3):                                                        # stopnie kopuły
        cyl(0, 0.21, 0.99 + k * 0.07, 0.68 - k * 0.06, 0.07, (200, 196, 190), v=24)
    kopula(0, 0.21, 1.15, 0.57, (172, 176, 180), seg=24, ringi=7, skala_z=0.85)
    cyl(0, 0.21, 1.6, 0.11, 0.05, (60, 56, 56), v=12)                         # oculus
    box(0, -0.35, 0.04, 0.9, 0.5, 1.15, (218, 206, 182))                      # blok pośredni
    box(0, -0.6, 0.04, 1.3, 0.55, 0.1, MARMUR_C)                              # portyk
    for x in [-0.56 + i * 0.16 for i in range(8)]:
        kolumna(x, -0.8, 0.14, 0.8, 0.045, (190, 180, 170), kapitel=MARMUR)
    for x in (-0.56, -0.24, 0.24, 0.56):
        kolumna(x, -0.53, 0.14, 0.8, 0.045, (190, 180, 170), kapitel=MARMUR)
    box(0, -0.6, 0.94, 1.32, 0.56, 0.14, MARMUR)
    napis("M·AGRIPPA", 0, -0.885, 1.01, 0.07, BRAZ_C, gl=0.005)
    dach_dwuspadowy(0, -0.58, 1.08, 1.36, 0.6, 0.32, (150, 154, 160), wzdluz="x")
    fronton(0, -0.892, 1.08, 1.36, 0.32, MARMUR, gl=0.6)


def m_luk_triumfalny():
    """Łuk triumfalny (jak łuk Konstantyna): trzy przejścia, kolumny, attyka z inskrypcją i kwadryga."""
    sciana_lukowa(-0.9, 0.9, 0.0, 2.1, [(-0.58, 0.28, 0.62), (0.0, 0.5, 1.0), (0.58, 0.28, 0.62)], 0.6, MARMUR)
    box(0, 0, 0, 1.8, 0.64, 0.12, MARMUR_C)
    for x in (-0.8, -0.32, 0.32, 0.8):                                      # kolumny przed fasadą
        for y in (-0.36, 0.36):
            box(x, y, 0.0, 0.14, 0.14, 0.35, MARMUR_C)
            cyl(x, y, 0.35, 0.05, 1.45, (200, 170, 140), v=10)
            box(x, y, 1.8, 0.14, 0.14, 0.1, MARMUR)
            box(x, y - 0.0, 2.1, 0.12, 0.12, 0.05, MARMUR_C)
            kula(x, y, 2.25, 0.06, MARMUR_C, seg=6, ringi=4, skala=(1, 1, 1.6))   # posągi Daków
    box(0, 0, 1.9, 1.8, 0.66, 0.2, MARMUR_C)
    box(0, 0, 2.1, 1.8, 0.6, 0.62, MARMUR)                                    # attyka
    box(0, -0.31, 2.18, 0.8, 0.02, 0.46, (196, 186, 170))
    napis("SPQR", 0, -0.33, 2.41, 0.2, BRAZ_C, gl=0.01, metal=0.4)
    for x in (-0.6, 0.6):                                                     # płaskorzeźby
        box(x, -0.31, 2.25, 0.32, 0.02, 0.3, (214, 206, 190))
        cyl(x, -0.31, 1.15, 0.12, 0.02, (214, 206, 190), v=12, rot=(math.pi / 2, 0, 0))
    box(0, 0, 2.72, 1.8, 0.64, 0.06, MARMUR_C)
    # kwadryga ze złoconego brązu
    box(0, 0.05, 2.78, 0.3, 0.2, 0.2, ZLOTO, metal=0.6, szorstkosc=0.4)
    kula(0, 0.1, 3.08, 0.06, ZLOTO, metal=0.6)
    walec((0, 0.1, 2.95), (0, 0.1, 3.05), 0.05, ZLOTO, metal=0.6)
    for x in (-0.24, -0.08, 0.08, 0.24):
        kula(x, -0.2, 2.98, 0.07, ZLOTO, seg=8, ringi=5, skala=(0.7, 1.8, 0.9), metal=0.6, szorstkosc=0.4)
        walec((x, -0.3, 3.0), (x, -0.36, 3.15), 0.035, ZLOTO, v=6, metal=0.6)
        for dy in (-0.3, -0.1):
            walec((x, dy, 2.92), (x, dy - 0.03, 2.78), 0.015, ZLOTO, v=4, metal=0.6)


def m_kolumna_trajana():
    """Kolumna Trajana: cokół z drzwiami, trzon ze spiralnym fryzem, na szczycie posąg z brązu."""
    box(0, 0, 0, 1.0, 1.0, 0.12, MARMUR_C)
    box(0, 0, 0.12, 0.86, 0.86, 0.85, MARMUR)
    box(0, -0.435, 0.12, 0.2, 0.02, 0.4, OTWOR)
    box(0, -0.435, 0.6, 0.5, 0.02, 0.22, (214, 206, 190))
    for s in (-1, 1):
        kula(s * 0.33, -0.44, 0.3, 0.06, ZLOTO, seg=6, ringi=4, metal=0.6)     # orły na rogach
    box(0, 0, 0.97, 0.92, 0.92, 0.08, MARMUR_C)
    torus(0, 0, 1.08, 0.24, 0.05, MARMUR_C, seg=16)                         # wieniec laurowy u podstawy
    cyl(0, 0, 1.05, 0.23, 3.3, (232, 226, 212), v=16)
    N = 64
    for i in range(N):                                                        # spiralny fryz
        t = i / N
        a = t * 2 * math.pi * 6
        z = 1.15 + t * 3.1
        box(0.235 * math.cos(a), 0.235 * math.sin(a), z, 0.03, 0.13, 0.1, (210, 198, 176), rot=(0, 0, a))
    box(0, 0, 4.35, 0.6, 0.6, 0.12, MARMUR_C)
    cyl(0, 0, 4.47, 0.16, 0.08, MARMUR, v=12)
    BR = (90, 110, 92)
    cyl(0, 0, 4.55, 0.08, 0.25, BR, v=8, metal=0.4)                           # posąg
    kula(0, 0, 4.86, 0.065, BR, seg=8, ringi=5, metal=0.4)
    walec((0.05, 0, 4.75), (0.15, -0.05, 4.95), 0.02, BR, v=5, metal=0.4)


def m_ruiny():
    """Ruiny forum: złamane kolumny, fragment belkowania, leżące bębny i bloki, trawa."""
    box(0, 0.1, 0, 1.6, 1.2, 0.12, TRAWERTYN_C)
    box(-0.2, 0.3, 0.12, 1.1, 0.7, 0.08, TRAWERTYN)
    for (x, y, h) in [(-0.55, 0.45, 1.6), (-0.15, 0.45, 1.6), (0.25, 0.45, 1.05), (0.6, 0.45, 0.45)]:
        cyl(x, y, 0.2, 0.08, h, MARMUR, v=10)
        box(x, y, 0.2, 0.2, 0.2, 0.06, MARMUR_C)
        if h > 1.5:
            box(x, y, 0.2 + h, 0.22, 0.22, 0.08, MARMUR_C)
        else:
            cyl(x, y, 0.2 + h, 0.08, 0.06, MARMUR_C, v=10, rot=(0.3, 0.2, 0))
    box(-0.35, 0.45, 1.88, 0.75, 0.22, 0.22, MARMUR)                          # belkowanie na 2 kolumnach
    box(-0.35, 0.45, 2.1, 0.8, 0.25, 0.06, MARMUR_C)
    for (x, y, rz) in [(0.25, -0.35, 0.3), (-0.4, -0.45, -0.2)]:
        walec((x - 0.25 * math.cos(rz), y - 0.25 * math.sin(rz), 0.08),
              (x + 0.25 * math.cos(rz), y + 0.25 * math.sin(rz), 0.08), 0.08, MARMUR_C, v=10)
    for (x, y) in [(0.65, -0.1), (0.75, -0.55), (-0.75, -0.1)]:
        box(x, y, 0, 0.22, 0.18, 0.16, TRAWERTYN, rot=(0, 0, x))
    box(0.35, 0.0, 0.0, 0.45, 0.2, 0.14, MARMUR, rot=(0, 0.1, 0.4))           # spadły fragment gzymsu
    for (x, y) in [(-0.7, -0.72), (0.0, -0.7), (0.5, 0.75), (-0.78, 0.65), (0.78, 0.2)]:
        stozek(x, y, 0, 0.1, 0.0, 0.16, TRAWA, v=5)


# ================================================================= OBOZY WROGA
def m_ognisko(x=0, y=0, s=1.0):
    for i in range(9):
        a = i * 2 * math.pi / 9
        ikosfera(x + 0.26 * s * math.cos(a), y + 0.26 * s * math.sin(a), 0.05 * s, 0.07 * s, KAMIEN)
    for k in range(3):
        a = k * math.pi / 3
        walec((x - 0.2 * s * math.cos(a), y - 0.2 * s * math.sin(a), 0.03 * s),
              (x + 0.2 * s * math.cos(a), y + 0.2 * s * math.sin(a), 0.1 * s), 0.035 * s, DREWNO_C, v=6)
    stozek(x, y, 0.06 * s, 0.14 * s, 0.0, 0.35 * s, (255, 140, 30), v=6, emisja=3.0)
    stozek(x + 0.05 * s, y, 0.06 * s, 0.08 * s, 0.0, 0.25 * s, (255, 210, 80), v=5, emisja=4.0)
    stozek(x - 0.05 * s, y + 0.03 * s, 0.06 * s, 0.07 * s, 0.0, 0.2 * s, (255, 100, 30), v=5, emisja=3.0)


def m_oboz_barbarzyncow():
    """Obóz barbarzyńców: namioty ze skór, ognisko, totem z czaszką i rogami."""
    baza(1.8, 1.8, (130, 116, 80))
    for (x, y, r, h, k) in [(-0.45, 0.4, 0.42, 1.0, FUTRO), (0.45, 0.45, 0.36, 0.85, (150, 120, 84))]:
        stozek(x, y, 0.04, r, 0.02, h, k, v=8)
        for j in range(3):
            a = j * 2.1
            walec((x, y, 0.04 + h - 0.1), (x + 0.1 * math.cos(a), y + 0.1 * math.sin(a), 0.04 + h + 0.25), 0.02,
                  DREWNO_C, v=4)
        box(x, y - r * 0.85, 0.04, 0.16, 0.02, h * 0.45, (60, 44, 30), rot=(-0.35, 0, 0))
        box(x + 0.05, y - r * 0.6, 0.3, r * 0.6, 0.02, 0.06, (200, 60, 40), rot=(-0.4, 0, 0))
    m_ognisko(0.0, -0.3, 0.9)
    for (x, y) in [(-0.35, -0.55), (0.4, -0.5)]:                              # pnie do siedzenia
        walec_lezacy(x, y, 0.1, 0.07, 0.4, DREWNO, os_="x", v=7)
    # totem
    cyl(0.6, -0.15, 0.04, 0.07, 1.5, DREWNO, v=7)
    for z, k in ((0.9, CZERWIEN_C), (1.15, (220, 190, 120)), (1.35, (60, 80, 120))):
        cyl(0.6, -0.15, z, 0.08, 0.06, k, v=7)
    kula(0.6, -0.17, 1.6, 0.1, (236, 228, 206), seg=8, ringi=6, skala=(0.9, 1.1, 1))   # czaszka
    for s in (-1, 1):
        kula(0.6 + s * 0.04, -0.26, 1.62, 0.025, CZARNY, seg=4, ringi=3)
        walec((0.6 + s * 0.08, -0.15, 1.65), (0.6 + s * 0.22, -0.15, 1.8), 0.03, (236, 228, 206), v=6, r2=0.005)
    for k in range(3):
        box(0.6, -0.24, 1.0 + k * 0.08, 0.03, 0.02, 0.18, (150, 40, 30))
    for (x, y) in [(-0.8, -0.75), (-0.7, -0.8), (0.8, 0.8)]:                  # zaostrzone pale
        stozek(x, y, 0.04, 0.04, 0.0, 0.5, DREWNO, v=5)
    for (x, s) in [(-0.85, 1), (-0.72, 0)]:                                   # tarcze
        cyl(x, 0.0, 0.25, 0.16, 0.03, (90, 110, 60) if s else (140, 60, 40), v=10,
            rot=(math.pi / 2 - 0.3, 0, math.pi / 2))


def palma(x, y, h=1.4):
    for k in range(4):
        z0, z1 = k * h / 4, (k + 1) * h / 4
        walec((x + 0.03 * k * k * 0.3, y, z0), (x + 0.03 * (k + 1) ** 2 * 0.3, y, z1), 0.06 - k * 0.006,
              (140, 110, 74) if k % 2 else (120, 94, 62), v=6)
    tx = x + 0.03 * 16 * 0.3
    for j in range(7):
        a = j * 2 * math.pi / 7
        belka((tx, y, h), (tx + 0.45 * math.cos(a), y + 0.45 * math.sin(a), h - 0.2), 0.12, 0.015,
              (64, 130, 58) if j % 2 else (82, 148, 66))
    kula(tx, y, h, 0.06, (110, 80, 50), seg=6, ringi=4)


def znak_tanit(x, y, z, s=1.0, kolor=ZLOTO):
    stozek(x, y, z, 0.1 * s, 0.02 * s, 0.2 * s, kolor, v=4, metal=0.5)
    box(x, y, z + 0.19 * s, 0.24 * s, 0.03 * s, 0.03 * s, kolor, metal=0.5)
    kula(x, y, z + 0.29 * s, 0.07 * s, kolor, seg=8, ringi=5, metal=0.5)


def m_oboz_kartaginy():
    """Obóz kartagiński: pasiaste namioty, palma, sztandar ze znakiem Tanit, amfory i okrągłe tarcze."""
    baza(1.8, 1.8, (206, 182, 130))
    for (x, y, k) in [(-0.45, 0.35, PURPURA), (0.4, 0.45, (230, 220, 196))]:
        namiot(x, y, 0.55, 0.7, 0.55, k)
        box(x, y - 0.36, 0.5, 0.06, 0.03, 0.08, ZLOTO)
    palma(0.25, -0.3, 1.4)
    cyl(-0.3, -0.2, 0.04, 0.025, 1.6, DREWNO_C, v=6)                          # sztandar
    box(-0.3, -0.2, 1.1, 0.34, 0.02, 0.3, PURPURA)
    znak_tanit(-0.3, -0.22, 1.66, 0.8)
    for k in range(4):                                                        # amfory
        x = -0.75 + k * 0.1
        cyl(x, -0.6, 0.04, 0.05, 0.18, TERAKOTA_C, v=8)
        stozek(x, -0.6, 0.22, 0.05, 0.015, 0.08, TERAKOTA_C, v=8)
    for (x, y) in [(0.45, -0.65), (0.65, -0.65)]:                             # tarcze
        cyl(x, y, 0.25, 0.18, 0.03, BRAZ, v=12, rot=(math.pi / 2 - 0.25, 0, 0), metal=0.5, szorstkosc=0.4)
        kula(x, y - 0.06, 0.26, 0.04, ZLOTO, seg=6, ringi=4)
    m_ognisko(-0.35, -0.65, 0.6)


# ================================================================= POSTACIE I JEDNOSTKI
DOMYSLNE = dict(skora=SKORA, wlosy=(70, 50, 36), fryzura="krotkie", broda=None, wasy=None, stroj="tunika",
                tunika=CZERWIEN, spodnie=None, krata=None, buty=SANDAL, zbroja=None, zbroja_kol=STAL,
                plaszcz=None, helm=None, helm_kol=STAL, grzebien=None, poprzeczny=False, wieniec=None,
                diadem=False, tarcza=None, tarcza_kol=CZERWIEN, tarcza_detal=ZOLTY, bron=None, lewa=None,
                torkwes=False, opaska=False, toga=BIEL, toga_pas=None, kaptur=None, szarfa=None, kolczan=False,
                mlody=False, pioro=False)

POSTACIE = {
    # Damian Ścisły — kronikarz serii, fioletowy płaszcz z kapturem, księga
    "damian": dict(stroj="kaptur", kaptur=FIOLET, tunika=KREM, spodnie=(86, 64, 52), buty=(70, 46, 30),
                   wlosy=(120, 80, 44), bron="ksiega", skora=SKORA_J, pioro=True, realny=True),
    # Romulus (legenda) — wojownik-założyciel: brązowy hełm, napierśnik, włócznia
    "romulus": dict(tunika=(150, 56, 40), zbroja="miesniowa", zbroja_kol=BRAZ, plaszcz=(120, 40, 30),
                    helm="brazowy", helm_kol=BRAZ, grzebien=CZERWIEN, broda="krotka", wlosy=(80, 54, 36),
                    bron="wlocznia", tarcza="okragla", tarcza_kol=BRAZ, tarcza_detal=ZLOTO),
    # Brennus — wódz Galów (390 p.n.e.)
    "brennus": dict(stroj="spodnie", tunika=(66, 116, 72), spodnie=(150, 112, 60), krata=(96, 64, 40),
                    buty=(80, 56, 36), wlosy=(206, 160, 92), fryzura="dlugie", wasy="galijskie",
                    helm="galijski", helm_kol=BRAZ, torkwes=True, bron="miecz", tarcza="owalna",
                    tarcza_kol=(140, 50, 36), tarcza_detal=ZLOTO, plaszcz=(170, 110, 50)),
    # Hannibal — wódz Kartaginy, po 217 p.n.e. stracił wzrok w jednym oku
    "hannibal": dict(skora=SKORA_C, wlosy=(36, 28, 26), broda="krotka", opaska=True, tunika=(130, 30, 60),
                     zbroja="miesniowa", zbroja_kol=ZLOTO, plaszcz=PURPURA, bron="miecz"),
    # Scypion Afrykański — rzymski wódz spod Zamy
    "scypion": dict(tunika=CZERWIEN, zbroja="miesniowa", zbroja_kol=BRAZ, plaszcz=CZERWIEN, helm="brazowy",
                    helm_kol=BRAZ, grzebien=BIEL, wlosy=(90, 64, 44), bron="gladius"),
    # Juliusz Cezar — toga z purpurowym pasem, wieniec laurowy, czerwony płaszcz
    "cezar": dict(stroj="toga", toga_pas=PURPURA, wieniec=(150, 170, 60), fryzura="lysy", wlosy=(90, 72, 56),
                  plaszcz=CZERWIEN, bron="zwoj", skora=(232, 192, 156)),
    # Wercyngetoryks — wódz Galów spod Alezji
    "wercyngetoryks": dict(stroj="spodnie", tunika=(46, 76, 130), spodnie=(176, 48, 44), krata=(226, 190, 110),
                           buty=(80, 56, 36), wlosy=(214, 172, 96), fryzura="dlugie", wasy="galijskie",
                           torkwes=True, plaszcz=(54, 110, 64), bron="miecz", tarcza="owalna",
                           tarcza_kol=(60, 110, 64), tarcza_detal=BRAZ),
    # Oktawian August — pierwszy cesarz: toga z purpurą, wieniec, berło z orłem
    # Kleopatra VII — ostatnia królowa Egiptu: lniana suknia ze złotym pasem, diadem, czarne włosy
    "kleopatra": dict(stroj="toga", toga=(242, 236, 220), toga_pas=ZLOTO, diadem=True, fryzura="dlugie",
                      wlosy=(18, 14, 14), skora=(222, 178, 134), bron="berlo", torkwes=True, plaszcz=(40, 70, 140)),
    # Marek Antoniusz — wódz w napierśniku, z purpurowym płaszczem i krótką brodą
    "antoniusz": dict(tunika=CZERWIEN, zbroja="miesniowa", zbroja_kol=ZLOTO, plaszcz=PURPURA, broda="krotka",
                      wlosy=(60, 40, 30), fryzura="loki", bron="miecz"),
    "august": dict(stroj="toga", toga_pas=PURPURA, wieniec=(150, 170, 60), fryzura="loki", wlosy=(120, 84, 50),
                   bron="berlo", skora=SKORA_J),
    # Trajan — cesarz-żołnierz: napierśnik, purpurowy płaszcz, wieniec
    "trajan": dict(tunika=CZERWIEN, zbroja="miesniowa", zbroja_kol=(196, 160, 90), plaszcz=PURPURA,
                   wieniec=(150, 170, 60), fryzura="loki", wlosy=(110, 100, 92), bron="gladius"),
    # Konstantyn Wielki — złoty napierśnik, purpurowy płaszcz, diadem, labarum z Chi-Rho
    "konstantyn": dict(tunika=BIEL, zbroja="miesniowa", zbroja_kol=ZLOTO, plaszcz=PURPURA, diadem=True,
                       wlosy=(80, 60, 44), bron="labarum"),
    # Attyla — wódz Hunów: futrzana czapka, kaftan, wąsy i broda
    "attyla": dict(stroj="kaftan", tunika=(118, 74, 42), spodnie=(70, 60, 50), buty=(60, 40, 28),
                   skora=(214, 172, 124), wlosy=(30, 26, 24), broda="krotka", wasy="galijskie", helm="futrzany",
                   helm_kol=FUTRO, bron="miecz"),
    # Odoaker — germański wódz, który w 476 r. złożył z tronu ostatniego cesarza
    "odoaker": dict(stroj="spodnie", tunika=(130, 44, 34), spodnie=(96, 84, 64), zbroja="kolczuga",
                    plaszcz=(56, 80, 130), helm="stozkowy", wlosy=(176, 124, 64), fryzura="dlugie",
                    broda="dluga", bron="miecz", buty=(70, 50, 34)),
    # Romulus Augustulus — ostatni cesarz zachodniorzymski, chłopiec
    "romulus_augustulus": dict(stroj="toga", toga_pas=PURPURA, diadem=True, wlosy=(214, 176, 100),
                               skora=SKORA_J, mlody=True, bron="brak"),
    # Cyncynat — rolnik, który porzucił pług, by ocalić Rzym, i wrócił na pole
    "cyncynat": dict(tunika=(140, 108, 70), szarfa=(232, 222, 200), broda="krotka", fryzura="lysy",
                     wlosy=(176, 170, 160), bron="motyka", skora=(222, 172, 128)),
}

JEDNOSTKI_PIESZE = {
    "legionista": dict(tunika=CZERWIEN, zbroja="segmentata", helm="galea", tarcza="scutum", bron="pilum"),
    "welita": dict(tunika=(196, 160, 112), helm="wilk", helm_kol=(122, 104, 86), tarcza="okragla",
                   tarcza_kol=(150, 96, 56), tarcza_detal=BRAZ, bron="oszczep"),
    "lucznik": dict(tunika=(84, 112, 70), zbroja="kolczuga", helm="stozkowy", lewa="luk", bron="strzala",
                    kolczan=True, skora=(214, 170, 124)),
    "pretorianin": dict(tunika=(150, 30, 40), zbroja="miesniowa", zbroja_kol=STAL, plaszcz=(120, 30, 90),
                        helm="galea", grzebien=CZERWIEN, tarcza="scutum", tarcza_kol=(96, 40, 116),
                        tarcza_detal=ZLOTO, bron="gladius"),
    "galijczyk": dict(stroj="spodnie", tunika=(96, 124, 62), spodnie=(150, 112, 60), krata=(176, 48, 44),
                      buty=(80, 56, 36), wlosy=(214, 176, 100), fryzura="dlugie", wasy="galijskie", torkwes=True,
                      bron="miecz", tarcza="owalna", tarcza_kol=(150, 60, 40), tarcza_detal=BRAZ),
    "kartaginczyk": dict(skora=SKORA_C, wlosy=(36, 28, 26), broda="krotka", tunika=(140, 32, 70),
                         zbroja="lniana", zbroja_kol=(236, 228, 206), helm="brazowy", helm_kol=BRAZ,
                         grzebien=CZARNY, tarcza="okragla", tarcza_kol=(230, 220, 196), tarcza_detal=PURPURA,
                         bron="wlocznia"),
    "german": dict(stroj="spodnie", tunika=(120, 96, 64), spodnie=(96, 86, 66), zbroja="futro",
                   zbroja_kol=FUTRO_J, wlosy=(206, 160, 92), fryzura="wezel", broda="krotka", buty=(80, 56, 36),
                   tarcza="okragla", tarcza_kol=(70, 104, 64), tarcza_detal=(200, 60, 40), bron="wlocznia"),
    # Egipt Ptolemeuszy: włócznik (machimos) w lnianym pancerzu z owalną tarczą i łucznik nubijski
    "egipcjanin": dict(skora=SKORA_C, wlosy=(26, 22, 20), tunika=(238, 232, 214), zbroja="lniana",
                       zbroja_kol=(232, 214, 160), plaszcz=(40, 70, 130), tarcza="owalna", tarcza_kol=(212, 170, 70),
                       tarcza_detal=(40, 80, 150), bron="wlocznia", torkwes=True, opaska=False),
    "nubijczyk": dict(skora=(112, 72, 50), wlosy=(24, 18, 16), tunika=(226, 206, 150), lewa="luk", bron="strzala",
                      kolczan=True, torkwes=True),
    "got": dict(stroj="spodnie", tunika=(60, 86, 130), spodnie=(84, 74, 60), zbroja="kolczuga", helm="stozkowy",
                plaszcz=(140, 40, 34), wlosy=(176, 124, 64), fryzura="dlugie", broda="dluga", buty=(70, 50, 34),
                tarcza="okragla", tarcza_kol=(150, 40, 36), tarcza_detal=(236, 228, 206), bron="miecz"),
}

JEZDZCY = {
    "ekwita": dict(tunika=CZERWIEN, zbroja="kolczuga", helm="galea", grzebien=(236, 236, 230), plaszcz=CZERWIEN,
                   tarcza="owalna", tarcza_kol=NIEBIESKI, tarcza_detal=ZLOTO, bron="wlocznia"),
    "hun": dict(stroj="kaftan", tunika=(96, 112, 120), spodnie=(84, 70, 54), buty=(60, 40, 28),
                skora=(214, 172, 124), wlosy=(30, 26, 24), wasy="galijskie", helm="futrzany", helm_kol=FUTRO,
                lewa="luk", kolczan=True, bron="brak"),
}


def tarcza_scutum(x, y, z0, kolor, detal, rz):
    """Prostokątna wygięta tarcza legionisty z obrzeżem, umbem i żółtymi pasami."""
    R, A, h, t = 0.42, 0.68, 0.95, 0.03

    def luk_(R_, A_, dy, z_a, z_b, kol):
        n = 7
        v = []
        for (rr, zz) in ((R_, z_a), (R_, z_b), (R_ - t, z_b), (R_ - t, z_a)):
            for i in range(n + 1):
                a = -A_ + 2 * A_ * i / n
                v.append((rr * math.sin(a), -rr * math.cos(a) + R + dy, zz))
        f = []
        m = n + 1
        for k in range(4):
            k1 = (k + 1) % 4
            for i in range(n):
                f.append((k * m + i, k * m + i + 1, k1 * m + i + 1, k1 * m + i))
        f.append((0, m, 2 * m, 3 * m))
        f.append((n, 3 * m + n, 2 * m + n, m + n))
        o = siatka("scutum", v, f, kol)
        o.location = (x, y, z0)
        o.rotation_euler = (0, 0, rz)
        return o
    luk_(R + 0.004, A + 0.03, -0.004, -0.02, h + 0.02, detal)                 # obrzeże
    luk_(R, A, -0.012, 0.0, h, kolor)
    c, s_ = math.cos(rz), math.sin(rz)

    def lok(px, py, pz):
        return (x + px * c - py * s_, y + px * s_ + py * c, z0 + pz)
    kula(*lok(0, -0.03, h / 2), 0.08, detal, seg=8, ringi=5, skala=(1, 0.6, 1), metal=0.5)
    for (pz, w) in ((h * 0.5, 0.5),):
        b = box(*lok(0, -0.022, pz - 0.02), w, 0.02, 0.04, detal)
        b.rotation_euler = (0, 0, rz)
    b = box(*lok(0, -0.022, 0.08), 0.04, 0.02, h - 0.16, detal)
    b.rotation_euler = (0, 0, rz)
    for s in (-1, 1):                                                         # „skrzydła”
        for k in range(2):
            b = box(*lok(s * 0.14, -0.026, h * 0.5 + (0.13 if k else -0.17)), 0.12, 0.02, 0.03, detal)
            b.rotation_euler = (0, s * (0.5 if k else -0.5), rz)


def tarcza_okragla(x, y, z, r, kolor, detal, rz):
    o = cyl(x, y, z, r, 0.035, kolor, v=16, rot=(math.pi / 2, 0, rz), **metal_kw(kolor))
    o.location = (x, y, z)
    torus(x, y, z, r, 0.02, detal, rot=(math.pi / 2, 0, rz), seg=16, mseg=4, **metal_kw(detal))
    dx, dy = math.sin(rz) * 0.03, -math.cos(rz) * 0.03
    kula(x + dx, y + dy, z, r * 0.25, detal, seg=8, ringi=5, skala=(1, 1, 1), **metal_kw(detal))


def tarcza_owalna(x, y, z, kolor, detal, rz, rx=0.26, rz_=0.5):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1, depth=0.035, location=(x, y, z),
                                        rotation=(math.pi / 2, 0, rz))
    o = bpy.context.active_object
    o.scale = (rx, rz_, 1)
    _nadaj(o, kolor)
    dx, dy = math.sin(rz), -math.cos(rz)
    belka((x + dx * 0.02, y + dy * 0.02, z - rz_ * 0.9), (x + dx * 0.02, y + dy * 0.02, z + rz_ * 0.9), 0.04, 0.02,
          detal)
    kula(x + dx * 0.03, y + dy * 0.03, z, 0.07, detal, seg=8, ringi=5, skala=(1, 1, 1.3), **metal_kw(detal))


def luk_bron(x, y, z, kolor=DREWNO_C, osobna_cieciwa=False):
    """Łuk refleksyjny w dłoni; z osobną cięciwą (węzeł „cieciwa_luku”) Godot animuje naciąganie."""
    pkt = []
    for i in range(7):
        t = -math.pi / 2 + i * math.pi / 6
        pkt.append((x, y - 0.14 * math.cos(t), z + 0.55 * math.sin(t)))
    for a, b in zip(pkt, pkt[1:]):
        walec(a, b, 0.018, kolor, v=5)
    for k in (0, -1):                                                         # rogowe końce łuku
        kula(*pkt[k], 0.024, (210, 196, 160), seg=5, ringi=3)
    box(x, y - 0.14, z, 0.045, 0.05, 0.12, (120, 74, 40))                     # owijka uchwytu
    c = walec(pkt[0], pkt[-1], 0.005, (230, 220, 190), v=3)
    if osobna_cieciwa:
        c.name = "cieciwa_luku"


def przedmiot_prawy(p, hx, hy, hz):
    """Broń/przedmiot w prawej (+X) dłoni."""
    t = p["bron"]
    if t == "gladius":
        belka((hx, hy - 0.02, hz + 0.02), (hx + 0.03, hy - 0.42, hz + 0.16), 0.05, 0.014, STAL, metal=0.6,
              szorstkosc=0.3)
        belka((hx, hy + 0.02, hz - 0.02), (hx, hy - 0.04, hz + 0.03), 0.11, 0.03, BRAZ, metal=0.5)
        kula(hx, hy + 0.05, hz - 0.05, 0.03, BRAZ, seg=6, ringi=4, metal=0.5)
    elif t == "miecz":
        belka((hx, hy - 0.02, hz + 0.02), (hx + 0.05, hy - 0.62, hz + 0.24), 0.05, 0.014, STAL, metal=0.6,
              szorstkosc=0.3)
        belka((hx, hy + 0.02, hz - 0.02), (hx, hy - 0.04, hz + 0.04), 0.16, 0.03, BRAZ_C)
        kula(hx, hy + 0.06, hz - 0.06, 0.035, BRAZ, seg=6, ringi=4, metal=0.5)
    elif t in ("pilum", "wlocznia", "oszczep"):
        z0, z1 = {"pilum": (0.08, 1.55), "wlocznia": (0.05, 1.9), "oszczep": (0.35, 1.6)}[t]
        cyl(hx, hy, z0, 0.02 if t != "oszczep" else 0.016, z1 - z0, DREWNO_J, v=6)
        if t == "pilum":
            cyl(hx, hy, z1 - 0.04, 0.03, 0.06, STAL_C, v=6)
            cyl(hx, hy, z1, 0.008, 0.35, STAL, v=4, metal=0.6)
            stozek(hx, hy, z1 + 0.35, 0.025, 0.0, 0.07, STAL, v=4, metal=0.6)
        else:
            stozek(hx, hy, z1, 0.04, 0.0, 0.18, STAL, v=4, metal=0.6, szorstkosc=0.3)
    elif t == "strzala":
        walec((hx, hy + 0.05, hz - 0.15), (hx, hy - 0.1, hz + 0.45), 0.008, DREWNO_J, v=4)
        stozek(hx, hy - 0.11, hz + 0.45, 0.02, 0, 0.05, STAL, v=4)
    elif t == "ksiega" and p.get("realny"):
        r = (0.25, 0, 0)
        box(hx, hy - 0.02, hz - 0.12, 0.23, 0.075, 0.3, (96, 36, 48), rot=r)                  # okładka
        box(hx + 0.004, hy - 0.024, hz - 0.115, 0.215, 0.064, 0.282, (236, 226, 196), rot=r)   # karty
        for zz in (-0.25, -0.01):
            for xx in (-0.1, 0.1):
                box(hx + xx, hy - 0.06, hz + zz * 0.95, 0.03, 0.01, 0.03, ZLOTO, rot=r, metal=0.6)   # okucia rogów
        box(hx, hy - 0.062, hz - 0.12, 0.07, 0.008, 0.08, ZLOTO, rot=r, metal=0.6)          # medalion
        kula(hx, hy - 0.068, hz - 0.12, 0.016, (150, 40, 60), seg=8, ringi=5, szorstkosc=0.2)
        box(hx + 0.12, hy - 0.02, hz - 0.12, 0.03, 0.06, 0.03, BRAZ, rot=r, metal=0.5)        # zapięcie
        walec((hx - 0.02, hy - 0.06, hz + 0.02), (hx - 0.03, hy - 0.08, hz - 0.2), 0.004, (160, 30, 40), v=4)  # zakładka
    elif t == "ksiega":
        box(hx, hy - 0.02, hz - 0.12, 0.22, 0.07, 0.28, (110, 40, 60), rot=(0.25, 0, 0))
        box(hx, hy - 0.03, hz - 0.115, 0.205, 0.075, 0.25, KREM, rot=(0.25, 0, 0))
        box(hx + 0.0, hy - 0.072, hz - 0.08, 0.06, 0.01, 0.06, ZLOTO, rot=(0.25, 0, 0))
    elif t == "zwoj":
        walec_lezacy(hx - 0.02, hy - 0.04, hz, 0.04, 0.26, KREM, os_="x", v=8)
        for s in (-1, 1):
            walec_lezacy(hx - 0.02 + s * 0.14, hy - 0.04, hz, 0.022, 0.04, DREWNO_C, os_="x", v=6)
    elif t == "berlo":
        cyl(hx, hy, hz - 0.2, 0.018, 0.85, (236, 228, 206), v=6)
        kula(hx, hy, hz + 0.67, 0.04, ZLOTO, seg=6, ringi=4, metal=0.6)
        orzel(hx, hy, hz + 0.76, 0.35)
    elif t == "labarum":
        cyl(hx, hy, 0.05, 0.022, 2.0, (150, 110, 60), v=6)
        box(hx, hy, 1.82, 0.5, 0.03, 0.03, (150, 110, 60))
        box(hx, hy, 1.4, 0.44, 0.02, 0.42, PURPURA)
        for k in range(3):
            box(hx - 0.15 + k * 0.15, hy - 0.012, 1.45, 0.08, 0.01, 0.08, ZLOTO)
        torus(hx, hy, 2.0, 0.1, 0.014, ZLOTO, rot=(math.pi / 2, 0, 0), seg=14, mseg=4, metal=0.6)
        box(hx, hy, 1.9, 0.02, 0.02, 0.2, ZLOTO, rot=(0, 0.7, 0), metal=0.6)  # X
        box(hx, hy, 1.9, 0.02, 0.02, 0.2, ZLOTO, rot=(0, -0.7, 0), metal=0.6)
        box(hx, hy, 1.92, 0.02, 0.02, 0.2, ZLOTO, metal=0.6)                  # P
        torus(hx + 0.035, hy, 2.08, 0.035, 0.01, ZLOTO, rot=(math.pi / 2, 0, 0), seg=10, mseg=4, metal=0.6)
    elif t == "motyka":
        cyl(hx, hy, 0.15, 0.018, 1.05, DREWNO_J, v=6)
        box(hx, hy - 0.08, 0.06, 0.12, 0.18, 0.02, STAL_C, rot=(0.9, 0, 0))


# ----------------------------------------------------------------- realistyczna postać (kronikarz Damian)
def _mix(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def _szata_kronikarza(p, ox, oy):
    """Wełniany płaszcz z fałdami, spodnia tunika, pas ze sznura z węzłem, sakiewka, kałamarz z rogu,
    torba na ramieniu ze zwojem."""
    kol = p["kaptur"]
    ciemny = _mix(kol, (20, 10, 30), 0.35)
    jasny = _mix(kol, (255, 255, 255), 0.12)
    # płaszcz: stożek z fałdami, rozcięty z przodu (widać tunikę)
    plaszcz = stozek(ox, oy, 0.05, 0.34, 0.2, 1.16, kol, v=28)
    faldy(plaszcz, n=9, amp=0.09)
    gladki(plaszcz)
    tun = stozek(ox, oy - 0.05, 0.05, 0.29, 0.15, 1.08, p["tunika"], v=20)     # tunika pod spodem (w rozcięciu)
    gladki(tun)
    for s_ in (-1, 1):                                                       # poły płaszcza z obszyciem
        b = box(ox + s_ * 0.09, oy - 0.27, 0.08, 0.05, 0.04, 1.0, jasny, rot=(-0.095, 0, s_ * 0.15))
        gladki(b)
        box(ox + s_ * 0.115, oy - 0.29, 0.08, 0.012, 0.02, 1.0, ZLOTO, rot=(-0.095, 0, s_ * 0.15), metal=0.4)
    for z in (0.12, 0.2):                                                    # brzeg płaszcza
        torus(ox, oy, z, 0.31 - z * 0.15, 0.012, ciemny, seg=28, mseg=4)
    # pas ze sznura, węzeł i zwisające końce
    torus(ox, oy, 0.8, 0.215, 0.022, (176, 150, 104), seg=24, mseg=6)
    kula(ox + 0.07, oy - 0.21, 0.8, 0.035, (176, 150, 104), seg=8, ringi=6)
    for dx, dl in ((0.06, 0.32), (0.09, 0.26)):
        walec((ox + dx, oy - 0.215, 0.79), (ox + dx + 0.02, oy - 0.24, 0.79 - dl), 0.012, (176, 150, 104), v=5)
        kula(ox + dx + 0.02, oy - 0.24, 0.79 - dl, 0.018, (150, 124, 84), seg=6, ringi=4)
    # sakiewka i kałamarz z rogu przy pasie
    kula(ox - 0.17, oy - 0.13, 0.69, 0.06, (120, 80, 50), seg=10, ringi=7, skala=(1, 0.75, 1.2))
    torus(ox - 0.17, oy - 0.13, 0.75, 0.035, 0.008, (90, 60, 36), seg=10, mseg=3)
    walec((ox - 0.2, oy - 0.02, 0.76), (ox - 0.24, oy + 0.02, 0.6), 0.03, (220, 200, 160), v=8, r2=0.015)
    cyl(ox - 0.2, oy - 0.02, 0.76, 0.034, 0.025, CZARNY, v=8)
    # torba na ramieniu (pas przez pierś) ze zwojem
    belka((ox - 0.17, oy - 0.08, 1.17), (ox + 0.2, oy - 0.1, 0.62), 0.05, 0.02, (110, 72, 42))
    box(ox + 0.25, oy + 0.02, 0.5, 0.1, 0.24, 0.22, (124, 84, 50))
    box(ox + 0.25, oy + 0.02, 0.66, 0.11, 0.25, 0.05, (104, 68, 40), rot=(0.25, 0, 0))
    walec_lezacy(ox + 0.25, oy + 0.02, 0.76, 0.03, 0.2, KREM, os_="y", v=8)
    for k in (-1, 1):
        cyl(ox + 0.25, oy + 0.02 + k * 0.1, 0.74, 0.04, 0.012, (150, 110, 60), v=8, rot=(math.pi / 2, 0, 0))
    # zapinka płaszcza pod szyją
    kula(ox, oy - 0.2, 1.16, 0.04, ZLOTO, seg=10, ringi=6, metal=0.6)
    kula(ox, oy - 0.235, 1.16, 0.02, (120, 40, 140), seg=6, ringi=4, szorstkosc=0.2)


def _glowa_realna(p, ox, oy):
    """Twarz o łagodnych bryłach: czaszka, żuchwa, kości policzkowe, oczy (białko, tęczówka, źrenica, powieka),
    nos z grzbietem i nozdrzami, dwubarwne usta, brwi, kilkudniowy zarost, kosmyki spod kaptura i kaptur
    z obszyciem okalającym twarz."""
    sk = p["skora"]
    wl = p["wlosy"]
    cien = _mix(sk, (120, 70, 60), 0.25)
    z = 1.43
    gladki(cyl(ox, oy, 1.2, 0.07, 0.13, sk, v=12))                                         # szyja
    gladki(kula(ox, oy, z, 0.165, sk, seg=24, ringi=16, skala=(0.92, 0.98, 1.12)))      # czaszka
    gladki(kula(ox, oy - 0.045, z - 0.085, 0.12, sk, seg=18, ringi=12, skala=(0.95, 0.85, 0.8)))  # żuchwa
    for s_ in (-1, 1):
        gladki(kula(ox + s_ * 0.075, oy - 0.12, z - 0.02, 0.05, sk, seg=12, ringi=8, skala=(1, 0.7, 0.8)))  # policzki
    # zarost na brodzie i policzkach
    gladki(kula(ox, oy - 0.05, z - 0.1, 0.123, _mix(sk, wl, 0.32), seg=18, ringi=12, skala=(0.96, 0.86, 0.72)))
    # oczy
    for s_ in (-1, 1):
        x = ox + s_ * 0.058
        gladki(kula(x, oy - 0.135, z + 0.015, 0.028, (244, 240, 232), seg=12, ringi=8, skala=(1.1, 0.6, 0.8)))
        gladki(kula(x, oy - 0.152, z + 0.014, 0.0145, (80, 110, 74), seg=10, ringi=6, skala=(1, 0.5, 1)))
        kula(x, oy - 0.159, z + 0.014, 0.0072, CZARNY, seg=8, ringi=5, skala=(1, 0.5, 1))
        kula(x + 0.004, oy - 0.162, z + 0.02, 0.003, (255, 255, 255), seg=5, ringi=3, emisja=1.5)   # błysk
        gladki(kula(x, oy - 0.128, z + 0.03, 0.031, sk, seg=12, ringi=8, skala=(1.15, 0.55, 0.45)))  # powieka
        b = belka((x - s_ * 0.03, oy - 0.15, z + 0.058), (x + s_ * 0.035, oy - 0.142, z + 0.05), 0.018, 0.014,
                  _mix(wl, (0, 0, 0), 0.25))                                                       # brew
        gladki(b)
        gladki(kula(ox + s_ * 0.155, oy + 0.0, z, 0.035, sk, seg=10, ringi=8, skala=(0.45, 0.9, 1.35)))  # ucho
    # nos: grzbiet, czubek, skrzydełka
    gladki(walec((ox, oy - 0.15, z + 0.035), (ox, oy - 0.185, z - 0.035), 0.022, sk, v=10, r2=0.026))
    gladki(kula(ox, oy - 0.183, z - 0.04, 0.026, sk, seg=12, ringi=8))
    for s_ in (-1, 1):
        gladki(kula(ox + s_ * 0.022, oy - 0.17, z - 0.045, 0.016, cien, seg=8, ringi=6))
    # usta
    gladki(kula(ox, oy - 0.16, z - 0.085, 0.034, (172, 92, 84), seg=12, ringi=8, skala=(1.3, 0.45, 0.32)))
    gladki(kula(ox, oy - 0.158, z - 0.1, 0.03, (190, 108, 98), seg=12, ringi=8, skala=(1.2, 0.5, 0.4)))
    # kosmyki włosów spod kaptura
    gladki(kula(ox, oy - 0.07, z + 0.11, 0.14, wl, seg=18, ringi=10, skala=(1.0, 0.75, 0.42)))   # grzywka
    for k in range(5):
        x = ox - 0.08 + k * 0.04
        gladki(kula(x, oy - 0.13, z + 0.085 - 0.006 * abs(k - 2), 0.03, wl, seg=8, ringi=6, skala=(0.8, 0.6, 1.2)))
    # kaptur: obszerny, okalający twarz, z obszyciem i opadający na plecy
    kol = p["kaptur"]
    ciemny = _mix(kol, (20, 10, 30), 0.45)
    gladki(kula(ox, oy + 0.11, z + 0.03, 0.185, ciemny, seg=20, ringi=14, skala=(1.0, 0.9, 1.08)))  # cień w kapturze
    kap = kula(ox, oy + 0.1, z + 0.04, 0.235, kol, seg=28, ringi=18, skala=(1.0, 1.0, 1.08))
    # otwór na twarz: usuwamy ściany z przodu kaptura w obrębie elipsy
    bm = bmesh.new()
    bm.from_mesh(kap.data)
    usun = [f for f in bm.faces if all(v.co.y < -0.06 and (v.co.x / 0.16) ** 2 + ((v.co.z + 0.03) / 0.17) ** 2 < 1.0
                                      for v in f.verts)]
    bmesh.ops.delete(bm, geom=usun, context="FACES")
    bm.to_mesh(kap.data)
    bm.free()
    gladki(kap)
    obs = torus(ox, oy - 0.1, z + 0.0, 0.17, 0.024, _mix(kol, (255, 255, 255), 0.18), rot=(math.pi / 2, 0, 0),
                seg=24, mseg=6)
    obs.scale = (0.98, 1.0, 1.22)
    gladki(obs)
    gladki(walec((ox, oy + 0.28, z + 0.06), (ox, oy + 0.36, z - 0.2), 0.09, kol, v=12, r2=0.03))      # szpic
    gladki(kula(ox, oy + 0.1, 1.17, 0.24, kol, seg=20, ringi=12, skala=(1.1, 0.75, 0.42)))             # kołnierz


def m_postac(p, ox=0.0, oy=0.0, czesci=False, siedzi=False):
    d = dict(DOMYSLNE)
    d.update(p)
    p = d
    st = p["stroj"]
    sk = p["skora"]
    dlugie_szaty = st in ("toga", "kaptur")
    noga_kol = p["spodnie"] if p["spodnie"] else sk
    # ---------------------------------------------------------- nogi
    for sx in (-0.1, 0.1):
        with Grupa("noga_l" if sx < 0 else "noga_p", (ox + sx, oy, 0.78), czesci):
            if siedzi:
                biodro = (ox + sx * 1.1, oy, 0.78)
                kolano = (ox + sx * 2.6, oy - 0.3, 0.72)
                stopa = (ox + sx * 2.8, oy - 0.24, 0.3)
                walec(biodro, kolano, 0.085, noga_kol, v=8)
                walec(kolano, stopa, 0.075, noga_kol, v=8)
                box(stopa[0], stopa[1] - 0.05, 0.24, 0.12, 0.22, 0.09, p["buty"])
            else:
                box(ox + sx, oy - 0.03, 0, 0.13, 0.24, 0.09, p["buty"])
                cyl(ox + sx, oy, 0.06, 0.07 if not p["spodnie"] else 0.085, 0.72, noga_kol, v=8)
                if not p["spodnie"]:
                    cyl(ox + sx, oy, 0.12, 0.074, 0.03, p["buty"], v=8)          # rzemienie sandałów
                    cyl(ox + sx, oy, 0.22, 0.072, 0.03, p["buty"], v=8)
                elif p["krata"]:
                    for z in (0.24, 0.44, 0.64):
                        cyl(ox + sx, oy, z, 0.088, 0.06, p["krata"], v=8)
                    for k in range(4):
                        a = k * math.pi / 2 + 0.4
                        box(ox + sx + 0.086 * math.cos(a), oy + 0.086 * math.sin(a), 0.1, 0.03, 0.03, 0.68,
                            p["krata"], rot=(0, 0, a))
                else:
                    cyl(ox + sx, oy, 0.1, 0.09, 0.14, p["buty"], v=8)          # owijacze / buty
    # ---------------------------------------------------------- szaty i tułów
    tk = p["tunika"]
    if st == "toga":
        stozek(ox, oy, 0.05, 0.3, 0.21, 0.8, p["toga"], v=12)
        if p["toga_pas"]:
            cyl(ox, oy, 0.05, 0.305, 0.06, p["toga_pas"], v=12)
        cyl(ox, oy, 0.76, 0.2, 0.5, p["toga"], v=10)
        th = -0.6
        box(ox, oy - 0.19, 0.7, 0.18, 0.05, 0.58, MARMUR_C if p["toga"] == BIEL else
            tuple(int(c * .9) for c in p["toga"]), rot=(0, th, 0))
        if p["toga_pas"]:
            box(ox + 0.085 * math.cos(th), oy - 0.205, 0.7 - 0.085 * math.sin(th), 0.04, 0.03,
                0.58, p["toga_pas"], rot=(0, th, 0))
        box(ox - 0.12, oy + 0.0, 1.05, 0.2, 0.44, 0.2, p["toga"], rot=(0.0, 0.0, 0.0))   # fałd na lewym ramieniu
        kula(ox - 0.17, oy, 1.18, 0.12, p["toga"], seg=8, ringi=5, skala=(1, 1.6, 0.8))
    elif st == "kaptur" and p.get("realny"):
        _szata_kronikarza(p, ox, oy)
    elif st == "kaptur":
        kol = p["kaptur"]
        stozek(ox, oy, 0.06, 0.33, 0.21, 1.17, kol, v=12)
        box(ox, oy - 0.275, 0.12, 0.12, 0.03, 0.95, p["tunika"], rot=(-0.095, 0, 0))
        box(ox, oy - 0.25, 0.8, 0.42, 0.04, 0.05, FIOLET_C, rot=(-0.095, 0, 0))   # pas
        kula(ox + 0.12, oy - 0.2, 1.17, 0.035, ZLOTO, seg=6, ringi=4, metal=0.6)  # zapinka
    else:
        dl = 0.32 if st != "kaftan" else 0.48
        stozek(ox, oy, 0.8 - dl, 0.25, 0.2, dl, tk, v=12)                     # spódnica tuniki
        cyl(ox, oy, 0.76, 0.2, 0.5, tk, v=10)
        if st == "kaftan":
            cyl(ox, oy, 0.8 - dl - 0.01, 0.255, 0.06, FUTRO_J, v=12)
            box(ox, oy - 0.2, 0.32, 0.06, 0.04, 0.94, FUTRO_J, rot=(-0.05, 0, 0))
            box(ox, oy, 0.8, 0.43, 0.43, 0.05, (90, 60, 34))
    if p["szarfa"]:
        th = -0.6
        box(ox, oy - 0.19, 0.7, 0.18, 0.05, 0.58, p["szarfa"], rot=(0, th, 0))
        kula(ox - 0.17, oy, 1.18, 0.12, p["szarfa"], seg=8, ringi=5, skala=(1, 1.6, 0.8))
    zb, zk = p["zbroja"], p["zbroja_kol"]
    if zb == "segmentata":
        for i, z in enumerate((0.86, 0.95, 1.04, 1.13)):
            cyl(ox, oy, z, 0.215, 0.075, STAL if i % 2 == 0 else (190, 194, 200), v=10, metal=0.5, szorstkosc=0.4)
        for s in (-1, 1):
            kula(ox + s * 0.16, oy, 1.2, 0.1, STAL, seg=8, ringi=5, skala=(1.3, 1.2, 0.6), metal=0.5)
        box(ox, oy, 0.78, 0.44, 0.44, 0.07, (96, 64, 36))
        for k in range(5):                                                    # fartuch z rzemieni
            box(ox - 0.08 + k * 0.04, oy - 0.21, 0.5, 0.025, 0.02, 0.28, (96, 64, 36))
            kula(ox - 0.08 + k * 0.04, oy - 0.215, 0.5, 0.014, BRAZ, seg=4, ringi=3)
    elif zb in ("miesniowa", "lniana"):
        cyl(ox, oy, 0.74, 0.215, 0.5, zk, v=12, **metal_kw(zk))
        kula(ox, oy - 0.12, 1.05, 0.12, zk, seg=8, ringi=5, skala=(1.4, 0.8, 0.6), **metal_kw(zk))
        for k in range(12):                                                   # pteruges
            a = k * 2 * math.pi / 12
            box(ox + 0.215 * math.cos(a), oy + 0.215 * math.sin(a), 0.5, 0.07, 0.02, 0.25,
                zk if (zb == "lniana" or k % 2) else (220, 210, 190), rot=(0, 0, a + math.pi / 2))
        if zb == "lniana":
            for s in (-1, 1):
                box(ox + s * 0.14, oy, 1.18, 0.16, 0.42, 0.06, zk)
        box(ox, oy, 0.74, 0.45, 0.45, 0.05, (110, 70, 40))
    elif zb == "kolczuga":
        cyl(ox, oy, 0.74, 0.215, 0.5, STAL_C, v=10, metal=0.4, szorstkosc=0.6)
        stozek(ox, oy, 0.46, 0.26, 0.215, 0.3, STAL_C, v=12, metal=0.4, szorstkosc=0.6)
        for s in (-1, 1):
            kula(ox + s * 0.17, oy, 1.18, 0.1, STAL_C, seg=8, ringi=5, skala=(1.2, 1.2, 0.6), metal=0.4)
        box(ox, oy, 0.8, 0.45, 0.45, 0.05, (96, 64, 36))
    elif zb == "futro":
        cyl(ox, oy, 0.92, 0.225, 0.32, zk, v=8)
        for s in (-1, 1):
            ikosfera(ox + s * 0.17, oy, 1.2, 0.12, zk, skala=(1.1, 1.2, 0.7))
        box(ox, oy, 0.78, 0.43, 0.43, 0.06, (90, 60, 34))
    if p["plaszcz"]:
        with Grupa("peleryna", (ox, oy + 0.2, 1.22), czesci):
            box(ox, oy + 0.22, 0.32, 0.46, 0.05, 0.9, p["plaszcz"], rot=(0.12, 0, 0))
            box(ox, oy + 0.255, 0.3, 0.47, 0.012, 0.05, tuple(int(c * 0.75) for c in p["plaszcz"]), rot=(0.12, 0, 0))
        box(ox, oy + 0.05, 1.18, 0.48, 0.36, 0.07, p["plaszcz"])
        kula(ox + 0.15, oy - 0.17, 1.2, 0.035, ZLOTO, seg=6, ringi=4, metal=0.6)
    # pas z bronią boczną i sakiewką
    if p["bron"] in ("gladius", "pilum", "miecz") and zb in ("segmentata", "kolczuga", "miesniowa"):
        box(ox + 0.25, oy + 0.03, 0.5, 0.06, 0.045, 0.36, (96, 62, 36), rot=(0, 0.28, 0))     # pochwa gladiusa
        box(ox + 0.29, oy + 0.03, 0.35, 0.065, 0.05, 0.05, BRAZ, rot=(0, 0.28, 0), metal=0.5)
        kula(ox + 0.2, oy + 0.03, 0.73, 0.035, BRAZ, seg=6, ringi=4, metal=0.5)               # głowica
        box(ox - 0.23, oy - 0.04, 0.6, 0.05, 0.035, 0.18, BRAZ_C, rot=(0, -0.2, 0), metal=0.3)  # pugio
    elif st in ("tunika", "kaftan") and not zb:
        kula(ox + 0.19, oy - 0.12, 0.72, 0.055, (130, 90, 56), seg=6, ringi=4, skala=(1, 0.7, 1.1))  # sakiewka
    if st == "toga" and (p["wieniec"] or p["diadem"]):
        torus(ox, oy, 1.2, 0.13, 0.012, ZLOTO, seg=12, mseg=4, metal=0.6)                    # złoty łańcuch
    if p["kolczan"]:
        walec((ox + 0.1, oy + 0.22, 0.7), (ox - 0.12, oy + 0.24, 1.3), 0.06, (120, 74, 40), v=8)
        for k in range(3):
            walec((ox - 0.1 - k * 0.02, oy + 0.24, 1.25), (ox - 0.14 - k * 0.025, oy + 0.24, 1.42), 0.008,
                  DREWNO_J, v=4)
            kula(ox - 0.14 - k * 0.025, oy + 0.24, 1.43, 0.022, BIEL, seg=4, ringi=3)
    # ---------------------------------------------------------- ręce
    rekaw_krotki = st in ("tunika",) and zb not in ("kolczuga",)
    rekaw_kol = {"toga": p["toga"], "kaptur": p["kaptur"], "kaftan": tk}.get(st, tk)
    if zb == "kolczuga":
        rekaw_kol = STAL_C
    for s in (-1, 1):
        bark = (ox + s * 0.26, oy - 0.0, 1.2)
        prawa = s > 0
        zgiete = prawa and p["bron"] in ("ksiega", "zwoj", "gladius", "miecz", "strzala")
        if zgiete:
            lokiec = (ox + s * 0.3, oy + 0.0, 0.94)
            dlon = (ox + s * 0.28, oy - 0.26, 0.9)
        else:
            lokiec = (ox + s * 0.3, oy - 0.02, 0.96)
            dlon = (ox + s * 0.31, oy - 0.08, 0.73)
        if not prawa and p["lewa"] == "luk":
            lokiec = (ox - 0.31, oy - 0.1, 0.98)
            dlon = (ox - 0.32, oy - 0.3, 0.92)
        with Grupa("reka_p" if prawa else "reka_l", bark, czesci):
            if p.get("realny"):                                              # szerokie, miękkie rękawy płaszcza
                gladki(kula(*bark, 0.09, rekaw_kol, seg=14, ringi=10))
                gladki(walec(bark, lokiec, 0.085, rekaw_kol, v=14, r2=0.09))
                gladki(walec(lokiec, Vector(lokiec).lerp(Vector(dlon), 0.8), 0.09, rekaw_kol, v=14, r2=0.075))
                torus(*Vector(lokiec).lerp(Vector(dlon), 0.8), 0.072, 0.012, _mix(rekaw_kol, (255, 255, 255), 0.18),
                      seg=16, mseg=4, rot=(Vector(dlon) - Vector(lokiec)).to_track_quat("Z", "Y").to_euler())
            else:
                walec(bark, lokiec, 0.07, rekaw_kol, v=6)
                walec(lokiec, dlon, 0.06, sk if rekaw_krotki else rekaw_kol, v=6)
            if not rekaw_krotki and st in ("kaftan",):
                walec(Vector(lokiec).lerp(Vector(dlon), 0.75), dlon, 0.066, FUTRO_J, v=6)
            kula(*dlon, 0.06, sk, seg=6, ringi=4)
            if prawa:
                if p["bron"] in ("pilum", "wlocznia", "oszczep", "labarum", "motyka"):
                    przedmiot_prawy(p, dlon[0] + 0.01, dlon[1] - 0.02, dlon[2])
                elif p["bron"] not in (None, "brak"):
                    przedmiot_prawy(p, *dlon)
            else:
                t = p["tarcza"]
                if t == "scutum":
                    tarcza_scutum(ox - 0.33, oy - 0.2, 0.33, p["tarcza_kol"], p["tarcza_detal"], -0.55)
                elif t == "okragla":
                    r = 0.22 if p["helm"] == "wilk" else 0.3
                    tarcza_okragla(ox - 0.36, oy - 0.16, 0.85, r, p["tarcza_kol"], p["tarcza_detal"], -0.5)
                elif t == "owalna":
                    tarcza_owalna(ox - 0.36, oy - 0.16, 0.82, p["tarcza_kol"], p["tarcza_detal"], -0.5)
                if p["lewa"] == "luk":
                    luk_bron(dlon[0], dlon[1] - 0.02, dlon[2], osobna_cieciwa=czesci)
                if p["pioro"]:                                                # gęsie pióro kronikarza
                    walec(dlon, (dlon[0] + 0.03, dlon[1] - 0.08, dlon[2] + 0.22), 0.012, BIEL, v=4)
                    box(dlon[0] + 0.02, dlon[1] - 0.06, dlon[2] + 0.16, 0.012, 0.05, 0.12, BIEL, rot=(-0.35, 0, 0))
    # ---------------------------------------------------------- głowa
    if p.get("realny"):
        with Grupa("glowa", (ox, oy, 1.24), czesci):
            _glowa_realna(p, ox, oy)
    with Grupa("glowa", (ox, oy, 1.24), czesci and not p.get("realny")):
      if not p.get("realny"):
        wl = p["wlosy"]
        cyl(ox, oy, 1.22, 0.075, 0.1, sk, v=8)
        kula(ox, oy, 1.43, 0.18, sk, seg=12, ringi=8, skala=(1, 0.95, 1.05))
        for sx in (-0.065, 0.065):
            box(ox + sx, oy - 0.165, 1.46, 0.035, 0.02, 0.04, CZARNY)
            box(ox + sx, oy - 0.162, 1.51, 0.07, 0.02, 0.025, tuple(int(c * 0.8) for c in wl))   # brwi
        for s in (-1, 1):
            kula(ox + s * 0.175, oy + 0.01, 1.43, 0.035, sk, seg=6, ringi=4, skala=(0.6, 1, 1.3))  # uszy
        box(ox, oy - 0.18, 1.39, 0.045, 0.05, 0.08, tuple(int(c * .88) for c in sk))          # nos
        box(ox, oy - 0.162, 1.33, 0.07, 0.02, 0.016, (150, 70, 60))                            # usta
        if p["opaska"]:
            box(ox - 0.065, oy - 0.175, 1.455, 0.09, 0.02, 0.075, CZARNY)
            box(ox - 0.02, oy - 0.168, 1.5, 0.3, 0.02, 0.016, CZARNY, rot=(0, -0.45, 0))
        w = p["wasy"]
        if w == "galijskie":
            box(ox, oy - 0.172, 1.355, 0.14, 0.04, 0.035, wl)
            for s in (-1, 1):
                box(ox + s * 0.075, oy - 0.165, 1.28, 0.035, 0.035, 0.1, wl, rot=(0, s * 0.15, 0))
        b = p["broda"]
        if b in ("krotka", "dluga"):
            kula(ox, oy - 0.035, 1.33, 0.165, wl, seg=10, ringi=6, skala=(1.06, 0.95, 0.78))
            if b == "dluga":
                kula(ox, oy - 0.1, 1.2, 0.12, wl, seg=8, ringi=6, skala=(1.0, 0.7, 1.3))
            box(ox, oy - 0.19, 1.335, 0.075, 0.02, 0.02, (120, 54, 50))           # usta na brodzie
            if not w:
                box(ox, oy - 0.183, 1.36, 0.14, 0.03, 0.03, wl)
        if p["stroj"] != "kaptur" and p["helm"] not in ("futrzany", "wilk"):
            f = p["fryzura"]
            if f in ("krotkie", "loki", "dlugie", "wezel"):
                kula(ox, oy + 0.02, 1.5, 0.188, wl, seg=12, ringi=6, skala=(1.02, 1.0, 0.75))
            if f == "loki":
                for k in range(5):
                    kula(ox - 0.1 + k * 0.05, oy - 0.15, 1.55, 0.035, wl, seg=5, ringi=3)
            if f == "lysy":
                for s in (-1, 1):
                    kula(ox + s * 0.15, oy + 0.03, 1.45, 0.07, wl, seg=6, ringi=4, skala=(0.6, 1.2, 1))
                kula(ox, oy + 0.1, 1.47, 0.14, wl, seg=8, ringi=5, skala=(1.1, 0.6, 0.8))
            if f == "dlugie":
                box(ox, oy + 0.1, 1.15, 0.34, 0.14, 0.38, wl)
                for s in (-1, 1):
                    box(ox + s * 0.165, oy - 0.02, 1.22, 0.06, 0.18, 0.3, wl)
            if f == "wezel":
                box(ox, oy + 0.1, 1.28, 0.3, 0.12, 0.22, wl)
                kula(ox + 0.15, oy + 0.02, 1.6, 0.07, wl, seg=8, ringi=5)
        if p["mlody"]:
            pass
        # ---------------------------------------------------------- nakrycia głowy
        h, hk = p["helm"], p["helm_kol"]
        if st == "kaptur":
            kol = p["kaptur"]
            kula(ox, oy + 0.02, 1.53, 0.17, wl, seg=10, ringi=6, skala=(1.0, 1.0, 0.6))  # grzywka pod kapturem
            kula(ox, oy + 0.07, 1.46, 0.22, kol, seg=14, ringi=9, skala=(1.0, 1.0, 1.08))
            stozek(ox, oy + 0.18, 1.55, 0.09, 0.0, 0.2, kol, v=6, rot=(0.6, 0, 0))
            box(ox, oy + 0.12, 1.12, 0.46, 0.2, 0.18, kol)                       # kaptur opada na plecy
        elif h in ("galea", "brazowy", "galijski"):
            kula(ox, oy + 0.01, 1.49, 0.2, hk, seg=12, ringi=7, skala=(1.0, 1.02, 0.85), **metal_kw(hk))
            cyl(ox, oy + 0.0, 1.47, 0.205, 0.04, hk, v=12, **metal_kw(hk))
            box(ox, oy + 0.17, 1.3, 0.34, 0.08, 0.18, hk, rot=(0.35, 0, 0), **metal_kw(hk))   # osłona karku
            if h != "galijski":
                box(ox, oy - 0.19, 1.55, 0.3, 0.06, 0.03, hk, rot=(-0.3, 0, 0), **metal_kw(hk))  # daszek
                for s in (-1, 1):
                    box(ox + s * 0.17, oy - 0.08, 1.3, 0.035, 0.13, 0.17, hk, rot=(0, -s * 0.12, 0), **metal_kw(hk))
            kula(ox, oy + 0.01, 1.67, 0.035, hk, seg=6, ringi=4, **metal_kw(hk))
            if p["grzebien"]:
                box(ox, oy + 0.01, 1.66, 0.04, 0.04, 0.06, hk, **metal_kw(hk))
                skala = (1.0, 0.16, 0.5) if p["poprzeczny"] else (0.16, 1.0, 0.5)
                kula(ox, oy + 0.03, 1.72, 0.21, p["grzebien"], seg=12, ringi=7, skala=skala)
        elif h == "stozkowy":
            stozek(ox, oy, 1.48, 0.2, 0.02, 0.28, hk, v=8, metal=0.5, szorstkosc=0.4)
            cyl(ox, oy, 1.46, 0.205, 0.05, BRAZ, v=8, metal=0.5)
            box(ox, oy - 0.2, 1.36, 0.035, 0.03, 0.14, hk, metal=0.5)            # nosal
        elif h == "futrzany":
            cyl(ox, oy, 1.44, 0.215, 0.12, hk, v=10)
            stozek(ox, oy, 1.56, 0.17, 0.02, 0.2, CZERWIEN_C, v=8)
            kula(ox, oy, 1.76, 0.03, ZLOTO, seg=6, ringi=4)
            for s in (-1, 1):
                box(ox + s * 0.18, oy, 1.3, 0.06, 0.14, 0.16, hk)               # nauszniki
        elif h == "wilk":
            kula(ox, oy + 0.03, 1.5, 0.205, hk, seg=10, ringi=7, skala=(1.02, 1.05, 0.8))
            walec((ox, oy - 0.1, 1.62), (ox, oy - 0.3, 1.58), 0.07, hk, v=6, r2=0.035)   # pysk
            kula(ox, oy - 0.31, 1.58, 0.025, CZARNY, seg=4, ringi=3)
            for s in (-1, 1):
                stozek(ox + s * 0.1, oy + 0.0, 1.62, 0.05, 0.0, 0.1, hk, v=4)
                kula(ox + s * 0.05, oy - 0.2, 1.64, 0.015, (200, 170, 60), seg=4, ringi=3)
            box(ox, oy + 0.18, 0.9, 0.34, 0.05, 0.55, hk, rot=(0.08, 0, 0))     # skóra na plecach
            for s in (-1, 1):
                walec((ox + s * 0.15, oy - 0.14, 1.22), (ox + s * 0.1, oy - 0.2, 1.05), 0.03, hk, v=5)
        if p["wieniec"]:
            kz = p["wieniec"]
            torus(ox, oy + 0.01, 1.55, 0.175, 0.022, kz, seg=16, mseg=4)
            for k in range(14):
                a = k * 2 * math.pi / 14
                if 1.1 < a < 2.0:
                    continue
                kula(ox + 0.18 * math.cos(a), oy + 0.01 + 0.18 * math.sin(a), 1.57, 0.03,
                     ZLOTO if k % 2 else (110, 150, 50), seg=4, ringi=3, skala=(1, 1, 0.5), metal=0.3)
        if p["diadem"]:
            torus(ox, oy + 0.01, 1.53, 0.18, 0.018, ZLOTO, seg=16, mseg=4, metal=0.6, szorstkosc=0.35)
            kula(ox, oy - 0.18, 1.55, 0.03, (40, 120, 200), seg=6, ringi=4, szorstkosc=0.2)
            for s in (-1, 1):
                kula(ox + s * 0.1, oy - 0.15, 1.54, 0.02, (200, 40, 60), seg=4, ringi=3)
    if p["torkwes"]:
        torus(ox, oy, 1.24, 0.1, 0.02, ZLOTO, seg=12, mseg=4, metal=0.6, szorstkosc=0.35)


def orzel(x, y, z, s=1.0, kolor=ZLOTO, skrzydla=True):
    """Orzeł legionowy (aquila) z rozpostartymi skrzydłami, frontem na -Y."""
    kw = dict(metal=0.6, szorstkosc=0.35)
    ciemne = tuple(int(c * 0.78) for c in kolor)
    kula(x, y, z, 0.12 * s, kolor, seg=10, ringi=7, skala=(0.85, 0.75, 1.3), **kw)
    kula(x, y - 0.06 * s, z + 0.04 * s, 0.08 * s, ciemne, seg=8, ringi=5, skala=(1, 0.6, 1.2), **kw)  # pierś
    kula(x + 0.02 * s, y - 0.02 * s, z + 0.2 * s, 0.075 * s, kolor, seg=10, ringi=7, **kw)           # głowa
    walec((x + 0.07 * s, y - 0.03 * s, z + 0.21 * s), (x + 0.15 * s, y - 0.03 * s, z + 0.16 * s), 0.03 * s,
          kolor, v=6, r2=0.004, **kw)                                                               # dziób
    kula(x + 0.05 * s, y - 0.08 * s, z + 0.22 * s, 0.012 * s, CZARNY, seg=4, ringi=3)
    if skrzydla:
        pioro = [(0.05, 0.12), (0.12, 0.3), (0.22, 0.44), (0.34, 0.53), (0.47, 0.57), (0.42, 0.46), (0.52, 0.43),
                 (0.45, 0.34), (0.52, 0.28), (0.43, 0.21), (0.47, 0.13), (0.37, 0.08), (0.37, 0.0), (0.25, 0.0),
                 (0.12, -0.05)]
        pokrywy = [(0.06, 0.1), (0.14, 0.27), (0.24, 0.37), (0.31, 0.3), (0.27, 0.18), (0.17, 0.05)]
        for sx in (-1, 1):
            profil_xz([(sx * px * s, pz * s) for px, pz in pioro], 0.03 * s, kolor, x=x, y=y + 0.01 * s, z=z, **kw)
            profil_xz([(sx * px * s, pz * s) for px, pz in pokrywy], 0.03 * s, ciemne, x=x, y=y - 0.01 * s, z=z,
                      **kw)
            for k in range(3):                                                # lotki
                belka((x + sx * (0.2 + 0.08 * k) * s, y - 0.012 * s, z + (0.12 + 0.03 * k) * s),
                      (x + sx * (0.32 + 0.06 * k) * s, y - 0.012 * s, z + (0.38 + 0.04 * k) * s),
                      0.012 * s, 0.03 * s, ciemne, **kw)
    for k in (-1, 0, 1):
        belka((x, y, z - 0.08 * s), (x + k * 0.07 * s, y, z - 0.26 * s), 0.05 * s, 0.02 * s, kolor, **kw)
    box(x, y, z - 0.2 * s, 0.3 * s, 0.05 * s, 0.04 * s, kolor, **kw)        # piorun w szponach
    for sx in (-1, 1):
        box(x + sx * 0.15 * s, y, z - 0.23 * s, 0.04 * s, 0.04 * s, 0.1 * s, kolor, rot=(0, sx * 0.6, 0), **kw)


def kon(kolor=(120, 80, 50), grzywa=(60, 40, 28), czaprak=CZERWIEN, s=1.0):
    """Koń frontem na -Y z ruchomymi częściami: kon_noga_lp/pp/lt/pt, kon_glowa, kon_ogon (galop w Godocie)."""
    kula(0, 0.05, 1.0 * s, 0.3 * s, kolor, seg=12, ringi=8, skala=(0.9, 2.05, 1.0))
    for nazwa, (x, y) in (("lp", (-0.14, -0.4)), ("pp", (0.14, -0.4)), ("lt", (-0.14, 0.48)), ("pt", (0.14, 0.48))):
        with Grupa("kon_noga_" + nazwa, (x * s, y * s, 0.9 * s)):
            walec((x * s, y * s, 0.5 * s), (x * s, y * s, 0.92 * s), 0.07 * s, kolor, v=6, r2=0.055 * s)   # udo
            walec((x * s, y * s, 0.06 * s), (x * s, y * s, 0.5 * s), 0.045 * s, kolor, v=6)              # nadpęcie
            cyl(x * s, y * s, 0.2 * s, 0.05 * s, 0.06 * s, tuple(int(c * 0.8) for c in kolor), v=6)     # staw
            cyl(x * s, y * s, 0, 0.062 * s, 0.08 * s, CZARNY, v=6)                                     # kopyto
    with Grupa("kon_glowa", (0, -0.42 * s, 1.12 * s)):
        walec((0, -0.42 * s, 1.08 * s), (0, -0.68 * s, 1.52 * s), 0.14 * s, kolor, v=8, r2=0.1 * s)
        walec((0, -0.66 * s, 1.6 * s), (0, -0.98 * s, 1.38 * s), 0.1 * s, kolor, v=8, r2=0.07 * s)
        kula(0, -0.7 * s, 1.58 * s, 0.11 * s, kolor, seg=8, ringi=6)
        kula(0, -0.98 * s, 1.37 * s, 0.07 * s, tuple(int(c * 0.75) for c in kolor), seg=6, ringi=4)  # chrapy
        for sx in (-1, 1):
            stozek(sx * 0.05 * s, -0.66 * s, 1.66 * s, 0.03 * s, 0.0, 0.1 * s, kolor, v=4)
            kula(sx * 0.075 * s, -0.8 * s, 1.55 * s, 0.018 * s, CZARNY, seg=4, ringi=3)
        belka((0, -0.38 * s, 1.25 * s), (0, -0.66 * s, 1.7 * s), 0.05 * s, 0.1 * s, grzywa)
        torus(0, -0.86 * s, 1.47 * s, 0.075 * s, 0.012 * s, (60, 40, 30), seg=8, mseg=3, rot=(0.9, 0, 0))  # uzda
        walec((0, -0.95 * s, 1.42 * s), (0, -0.25 * s, 1.35 * s), 0.008 * s, (60, 40, 30), v=3)    # wodze
    with Grupa("kon_ogon", (0, 0.62 * s, 1.15 * s)):
        walec((0, 0.62 * s, 1.15 * s), (0, 0.8 * s, 0.6 * s), 0.06 * s, grzywa, v=6, r2=0.03 * s)
    box(0, 0.05 * s, 1.18 * s, 0.62 * s, 0.55 * s, 0.14 * s, czaprak)
    box(0, 0.05 * s, 1.17 * s, 0.64 * s, 0.57 * s, 0.03 * s, ZLOTO)
    for sx in (-1, 1):                                                        # strzemiona-pętle i frędzle czapraka
        for k in range(4):
            box(sx * 0.32 * s, (-0.15 + k * 0.1) * s, 1.06 * s, 0.015 * s, 0.03 * s, 0.08 * s, ZLOTO)


def m_jezdziec(p, kol_konia, czaprak):
    kon(kol_konia, czaprak=czaprak)
    with Grupa("jezdziec", (0, 0.08, 1.2)):                                  # jeździec kołysze się w siodle
        wstaw(m_postac, z=0.55, y=0.08, a=(p, 0.0, 0.0, False, True))


def m_ekwita():
    m_jezdziec(JEZDZCY["ekwita"], (120, 80, 50), CZERWIEN)


def m_hun():
    m_jezdziec(JEZDZCY["hun"], (150, 130, 104), (90, 70, 50))


def m_slon():
    """Słoń bojowy z wieżyczką i kornakiem (jedna bryła), frontem na -Y."""
    SL = (136, 130, 128)
    kula(0, 0.1, 1.3, 0.6, SL, seg=14, ringi=9, skala=(0.85, 1.3, 0.85))
    for nazwa, (x, y) in (("lp", (-0.3, -0.35)), ("pp", (0.3, -0.35)), ("lt", (-0.3, 0.55)), ("pt", (0.3, 0.55))):
        with Grupa("slon_noga_" + nazwa, (x, y, 1.0)):
            cyl(x, y, 0.0, 0.17, 1.05, SL, v=8)
            cyl(x, y, 0.0, 0.18, 0.06, (200, 196, 186), v=8)
            for k in range(3):                                                # paznokcie
                kula(x - 0.08 + k * 0.08, y - 0.16, 0.05, 0.035, (220, 214, 200), seg=5, ringi=3)
    kula(0, -0.75, 1.6, 0.36, SL, seg=12, ringi=8, skala=(0.95, 0.9, 1.05))
    for s in (-1, 1):                                                         # uszy
        with Grupa("slon_ucho_" + ("l" if s < 0 else "p"), (s * 0.3, -0.7, 1.62)):
            kula(s * 0.36, -0.62, 1.6, 0.32, (124, 118, 116), seg=10, ringi=6, skala=(0.25, 0.8, 1.0))
        kula(s * 0.16, -1.05, 1.68, 0.03, CZARNY, seg=4, ringi=3)
        walec((s * 0.14, -1.0, 1.35), (s * 0.18, -1.32, 1.42), 0.045, (246, 240, 224), v=6, r2=0.012)  # ciosy
    pkt = [(0, -1.02, 1.5), (0, -1.15, 1.2), (0, -1.18, 0.85), (0, -1.1, 0.55), (0, -1.2, 0.35)]
    with Grupa("slon_traba", (0, -1.02, 1.5)):
        for i, (a, b) in enumerate(zip(pkt, pkt[1:])):                       # trąba
            walec(a, b, 0.13 - i * 0.022, SL, v=8, r2=0.11 - i * 0.022)
            cyl(b[0], b[1], b[2] - 0.02, 0.115 - i * 0.022, 0.03, (120, 114, 112), v=8)   # fałdy skóry
    with Grupa("slon_ogon", (0, 0.85, 1.35)):
        walec((0, 0.85, 1.35), (0, 1.0, 0.8), 0.04, SL, v=5, r2=0.015)         # ogon
        kula(0, 1.0, 0.78, 0.04, CZARNY, seg=5, ringi=3, skala=(1, 1, 1.6))
    box(0, 0.15, 1.72, 1.05, 1.1, 0.12, CZERWIEN)                             # czaprak
    for s in (-1, 1):
        box(s * 0.53, 0.15, 1.1, 0.04, 0.95, 0.65, CZERWIEN)
        box(s * 0.55, 0.15, 1.1, 0.03, 0.97, 0.06, ZLOTO)
        znak_tanit(s * 0.56, 0.15, 1.25, 0.9)
    # wieżyczka
    box(0, 0.25, 1.84, 0.82, 0.82, 0.08, DREWNO_C)
    for sx in (-1, 1):
        box(sx * 0.39, 0.25, 1.92, 0.05, 0.82, 0.38, DREWNO)
        box(0, 0.25 + sx * 0.39, 1.92, 0.82, 0.05, 0.38, DREWNO)
    for (x, y) in [(-0.39, -0.14), (0.39, -0.14), (-0.39, 0.64), (0.39, 0.64), (0, -0.14), (-0.39, 0.25)]:
        box(x, y, 2.3, 0.14, 0.14, 0.12, DREWNO_J)
    for k in range(3):                                                        # tarcze na burtach
        tarcza_okragla(-0.25 + k * 0.25, -0.17, 2.1, 0.11, BRAZ, ZLOTO, 0.0)
    for k in range(2):                                                        # włócznie w wieżyczce
        walec((-0.15 + k * 0.3, 0.3, 1.9), (-0.2 + k * 0.4, 0.2, 2.9), 0.015, DREWNO_J, v=4)
        stozek(-0.2 + k * 0.4, 0.2, 2.9, 0.03, 0.0, 0.12, STAL, v=4)
    # kornak na karku
    cyl(0, -0.72, 1.85, 0.12, 0.3, (220, 210, 190), v=8)
    kula(0, -0.72, 2.25, 0.1, SKORA_C, seg=8, ringi=6)
    torus(0, -0.72, 2.3, 0.09, 0.03, BIEL, seg=10, mseg=4)


def m_balista():
    """Balista (skorpion) na trójnogu, naciągnięta i gotowa do strzału. Ruchome części (Godot):
    balista_ramie_l/p (ramiona w wiązkach ścięgien), balista_suwak (suwak z zaczepem), balista_belt (bełt),
    balista_kolowrot (kołowrót z korbami). Cięciwy rysuje gra między końcami ramion a zaczepem."""
    for a in (0.0, 2.1, 4.2):
        belka((0, 0, 0.7), (0.5 * math.sin(a), -0.5 * math.cos(a) + 0.1, 0.0), 0.06, 0.06, DREWNO_C)
        kula(0.5 * math.sin(a), -0.5 * math.cos(a) + 0.1, 0.02, 0.05, BRAZ_C, seg=5, ringi=3, metal=0.3)   # okucia stóp
    cyl(0, 0.0, 0.62, 0.08, 0.16, DREWNO, v=8)
    box(0, 0.05, 0.78, 0.14, 1.3, 0.1, DREWNO_J)                              # łoże
    for s_ in (-1, 1):
        box(s_ * 0.075, 0.05, 0.85, 0.02, 1.25, 0.04, DREWNO_C)               # prowadnice suwaka
        for k in range(5):                                                    # zapadki (zębatka)
            box(s_ * 0.085, 0.1 + k * 0.1, 0.89, 0.025, 0.03, 0.03, BRAZ, metal=0.5)
    box(0, -0.48, 0.82, 0.6, 0.14, 0.4, DREWNO)                               # rama skrętna
    for s_ in (-1, 1):
        cyl(s_ * 0.17, -0.48, 0.78, 0.07, 0.5, (90, 66, 40), v=8)              # wiązki ścięgien
        cyl(s_ * 0.17, -0.48, 1.24, 0.09, 0.05, BRAZ, v=8, metal=0.5)
        cyl(s_ * 0.17, -0.48, 0.74, 0.09, 0.05, BRAZ, v=8, metal=0.5)
        for z in (0.82, 1.18):                                                # klucze napinające
            box(s_ * 0.17, -0.48, z + 0.03, 0.2, 0.025, 0.025, BRAZ_C, metal=0.4)
        with Grupa("balista_ramie_" + ("l" if s_ < 0 else "p"), (s_ * 0.17, -0.48, 1.0)):
            belka((s_ * 0.17, -0.48, 1.0), (s_ * 0.5, -0.25, 1.0), 0.05, 0.05, DREWNO_C)
            cyl(s_ * 0.5, -0.25, 0.97, 0.03, 0.06, BRAZ, v=6, metal=0.5)        # okucie końca ramienia
    with Grupa("balista_suwak", (0, 0.32, 0.93)):                           # suwak z zaczepem
        box(0, 0.36, 0.86, 0.13, 0.16, 0.06, DREWNO)
        box(0, 0.3, 0.92, 0.05, 0.04, 0.06, BRAZ, metal=0.5)
        walec((0, 0.44, 0.9), (0, 0.6, 0.88), 0.012, (200, 180, 140), v=4)     # lina do kołowrotu
    with Grupa("balista_belt", (0, 0.32, 0.95)):                            # bełt
        walec((0, 0.3, 0.95), (0, -0.85, 0.97), 0.015, DREWNO_J, v=5)
        stozek(0, -0.85, 0.97, 0.03, 0, 0.12, STAL, v=4, rot=(math.pi / 2, 0, 0))
        for k in range(3):                                                    # lotki
            a = k * 2 * math.pi / 3
            box(0.025 * math.cos(a), 0.22, 0.95 + 0.025 * math.sin(a), 0.01, 0.12, 0.04, BIEL, rot=(0, a, 0))
    with Grupa("balista_kolowrot", (0, 0.6, 0.86)):                         # kołowrót z korbami
        walec_lezacy(0, 0.6, 0.86, 0.06, 0.3, DREWNO, os_="x", v=8)
        for sx in (-1, 1):
            box(sx * 0.17, 0.6, 0.86, 0.03, 0.03, 0.24, DREWNO_C)
            box(sx * 0.17, 0.6, 0.86, 0.03, 0.24, 0.03, DREWNO_C)
    box(0, -0.56, 0.82, 0.62, 0.02, 0.4, BRAZ_C, metal=0.3)                  # tarcza ochronna
    box(0, -0.575, 0.97, 0.06, 0.02, 0.08, OTWOR)                            # okienko celownicze
    cyl(0.35, 0.35, 0.0, 0.1, 0.25, STRZECHA_C, v=8)                          # kosz z zapasowymi bełtami
    for k in range(4):
        walec((0.32 + k * 0.02, 0.33, 0.1), (0.3 + k * 0.025, 0.36, 0.48), 0.01, DREWNO_J, v=4)


# ================================================================= INNE
def m_galera():
    """Galera (trirema) ok. 4 m: kadłub, taran, wiosła, maszt z żaglem, oko na dziobie, tarcze na burtach."""
    kadlub(4.0, 0.9, 0.55, (110, 70, 40))
    box(0, 0, 0.5, 0.78, 2.6, 0.04, DREWNO_J)                                 # pokład
    for s in (-1, 1):
        box(s * 0.4, 0, 0.4, 0.04, 2.6, 0.06, CZERWIEN_C)                     # pas burty
        kula(s * 0.08, -1.92, 0.55, 0.05, BIEL, seg=6, ringi=4, skala=(0.4, 1, 1))   # oko
        kula(s * 0.09, -1.93, 0.55, 0.025, CZARNY, seg=4, ringi=3, skala=(0.4, 1, 1))
        for k in range(11):
            y = -1.25 + k * 0.25
            belka((s * 0.42, y, 0.38), (s * 1.15, y - 0.05, 0.02), 0.03, 0.03, DREWNO_J)
            box(s * 1.15, y - 0.05, 0.0, 0.03, 0.1, 0.04, DREWNO_J)
        for k in range(6):
            tarcza_okragla(s * 0.44, -0.9 + k * 0.36, 0.64, 0.12, [CZERWIEN, (230, 220, 196), NIEBIESKI][k % 3],
                           ZLOTO, s * math.pi / 2)
    walec((0, -2.0, 0.08), (0, -2.35, 0.08), 0.08, BRAZ, v=6, r2=0.02, metal=0.5)   # taran
    walec((0, 2.0, 0.85), (0, 2.25, 1.25), 0.06, (110, 70, 40), v=6, r2=0.03)        # aplustre
    walec((0, 2.25, 1.25), (0, 2.1, 1.45), 0.03, (110, 70, 40), v=6)
    box(0, 1.35, 0.52, 0.6, 0.6, 0.3, DREWNO)                                 # nadbudówka rufowa
    box(0, 1.35, 0.82, 0.66, 0.66, 0.04, CZERWIEN_C)
    for s in (-1, 1):                                                         # wiosła sterowe
        belka((s * 0.38, 1.7, 0.6), (s * 0.5, 2.0, 0.0), 0.04, 0.04, DREWNO_C)
    cyl(0, -0.1, 0.5, 0.05, 2.3, DREWNO_C, v=8)                               # maszt
    walec_lezacy(0, -0.1, 2.6, 0.03, 1.8, DREWNO_C, os_="x", v=6)
    for k in range(5):                                                        # żagiel w pasy
        box(0, -0.12, 1.4 + k * 0.24, 1.7 - k * 0.0, 0.03, 0.24,
            (232, 222, 196) if k % 2 else (176, 50, 44))
    orzel(0, -0.14, 1.95, 0.6, kolor=ZLOTO, skrzydla=True)
    for s in (-1, 1):
        walec((s * 0.85, -0.12, 2.6), (s * 0.35, -1.8, 0.6), 0.006, (60, 50, 40), v=3)
    walec((0, -0.1, 2.75), (0, -0.1, 2.95), 0.01, DREWNO_C, v=4)
    box(0.08, -0.1, 2.85, 0.16, 0.01, 0.08, CZERWIEN)


def m_sztandar():
    """Sztandar legionu: aquila na drzewcu z tabliczką SPQR."""
    cyl(0, 0, 0, 0.03, 2.2, DREWNO_C, v=8)
    stozek(0, 0, 0, 0.0, 0.03, 0.1, STAL, v=6)
    box(0, 0, 1.45, 0.4, 0.03, 0.03, ZLOTO, metal=0.6)
    box(0, -0.0, 1.17, 0.36, 0.03, 0.26, CZERWIEN)
    napis("SPQR", 0, -0.018, 1.3, 0.11, ZLOTO, gl=0.008, metal=0.6, szorstkosc=0.4)
    for s in (-1, 1):
        cyl(s * 0.17, 0, 1.08, 0.012, 0.37, ZLOTO, v=4, metal=0.6)
    torus(0, 0, 1.85, 0.25, 0.025, (120, 150, 50), rot=(math.pi / 2, 0, 0), seg=18, mseg=4)   # wieniec
    cyl(0, 0, 2.2, 0.08, 0.05, ZLOTO, v=8, metal=0.6)
    orzel(0, 0, 2.43, 0.9)


def m_znacznik():
    torus(0, 0, 0.05, 0.9, 0.07, (255, 214, 80), seg=32, mseg=6, emisja=1.5)


# ================================================================= RENDERY (Cycles)
def przygotuj_render(w, h, przezroczyste=True, probki=24, odbicia=3):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = probki
    sc.cycles.max_bounces = odbicia
    sc.cycles.use_adaptive_sampling = True
    try:
        sc.cycles.use_denoising = True
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:  # nie każda kompilacja Blendera ma OpenImageDenoise
        sc.cycles.use_denoising = False
    sc.cycles.filter_width = 1.5
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = przezroczyste
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if przezroczyste else "RGB"


def swiat(kolor, sila=1.0):
    w = bpy.data.worlds.new("swiat")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*lin(kolor), 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = sila
    bpy.context.scene.world = w


def niebo_gradient(dol, gora, sila=1.0, srodek=None):
    """Tło świata: gradient od horyzontu (dol) do zenitu (gora), opcjonalnie z kolorem pośrednim."""
    w = bpy.data.worlds.new("niebo")
    w.use_nodes = True
    nt = w.node_tree
    tlo = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], tlo.inputs[0])
    el = ramp.color_ramp.elements
    el[0].position = 0.0
    el[0].color = (*lin(dol), 1)
    el[1].position = 0.55
    el[1].color = (*lin(gora), 1)
    if srodek:
        e = el.new(0.12)
        e.color = (*lin(srodek), 1)
    tlo.inputs[1].default_value = sila
    bpy.context.scene.world = w


def slonce(rot=(0.9, 0.2, -0.6), energia=3.5, kolor=(255, 246, 228), kat=0.1):
    l = bpy.data.lights.new("slonce", "SUN")
    l.energy = energia
    l.color = lin(kolor)
    l.angle = kat
    o = bpy.data.objects.new("slonce", l)
    o.rotation_euler = rot
    bpy.context.collection.objects.link(o)


def kamera(poz, cel, orto=None, obiektyw=50):
    c = bpy.data.cameras.new("kam")
    c.clip_end = 500
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


def kadruj(kier, margines=1.12):
    """Kamera ortograficzna patrząca w kierunku kier, kadrująca wszystkie siatki w scenie."""
    pkt = []
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            pkt += [o.matrix_world @ v.co for v in o.data.vertices]
    rot = Vector(kier).normalized().to_track_quat("-Z", "Y")
    odw = rot.inverted()
    lok = [odw @ p for p in pkt]
    xs, ys, zs = [p.x for p in lok], [p.y for p in lok], [p.z for p in lok]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    rozm = max(max(xs) - min(xs), max(ys) - min(ys)) * margines
    poz = rot @ Vector((cx, cy, max(zs) + 20))
    c = bpy.data.cameras.new("kam")
    c.type = "ORTHO"
    c.ortho_scale = rozm
    c.clip_end = 200
    o = bpy.data.objects.new("kam", c)
    bpy.context.collection.objects.link(o)
    o.location = poz
    o.rotation_euler = rot.to_euler()
    bpy.context.scene.camera = o


def renderuj(sciezka):
    bpy.context.scene.render.filepath = sciezka
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print("render: %s (%.1f s)" % (os.path.basename(sciezka), time.time() - t))


def ikona_budynku(nazwa):
    przygotuj_render(128, 128, True, 32)
    swiat((210, 220, 236), 1.0)
    slonce(rot=(0.85, 0.15, -0.65), energia=3.6)
    kadruj((-0.6, 1.0, -0.78), 1.06)
    renderuj(os.path.join(UI, "budynek_%s.png" % nazwa))


def karta(nazwa):
    przygotuj_render(192, 192, True, 32)
    swiat((214, 222, 236), 1.0)
    slonce(rot=(0.85, -0.1, 0.55), energia=3.6)
    kadruj((1.0, 0.75, -0.6) if nazwa in ("ekwita", "hun", "slon") else (0.6, 1.0, -0.55), 1.08)
    renderuj(os.path.join(UI, "karta_%s.png" % nazwa))


def portret(nazwa):
    przygotuj_render(256, 256, True, 64)
    swiat((226, 222, 214), 0.75)
    slonce(rot=(0.95, 0.15, -0.45), energia=3.0)
    sw = bpy.data.lights.new("kontur", "AREA")                # światło konturowe zza postaci
    sw.energy = 120
    sw.size = 1.5
    sw.color = (1.0, 0.9, 0.75)
    ob = bpy.data.objects.new("kontur", sw)
    ob.location = (-0.9, 1.6, 2.2)
    ob.rotation_euler = Vector((0.0, 0.0, 1.4) ) - Vector(ob.location)
    ob.rotation_euler = (Vector((0.0, 0.0, 1.4)) - Vector(ob.location)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(ob)
    kamera((0.42, -2.3, 1.5), (0.0, 0.0, 1.38), obiektyw=88)
    renderuj(os.path.join(UI, "portret_%s.png" % nazwa))


# ================================================================= TŁA
def cyprys_w(x, y, s=1.0):
    wstaw(m_cyprys, x, y, 0, s)


def kolumnada(x0, x1, y, z0, h, n, kolor=MARMUR, gl=0.6):
    for i in range(n):
        kolumna(x0 + i * (x1 - x0) / (n - 1), y, z0, h, h * 0.055, kolor)
    box((x0 + x1) / 2, y + gl / 2 - 0.1, z0 + h, abs(x1 - x0) + h * 0.15, gl, h * 0.12, kolor)


def tlo_tytul():
    """Forum Romanum o zachodzie słońca: świątynie, kolumnady, łuk, w oddali Koloseum, cyprysy i pinie."""
    czysc()
    box(0, 30, -0.2, 300, 300, 0.2, (150, 136, 96))
    box(0, 20, -0.15, 30, 80, 0.17, (196, 180, 150))                          # plac forum (bruk)
    for i in range(36):
        box(0, -6 + i * 2.2, 0.0, 30, 0.06, 0.03, (176, 160, 130))
    # lewa strona (fronty na +X, do placu): świątynie Saturna i Kastora, bazylika Julia
    wstaw(swiatynia_bryla, -9.5, 3, 0, 4.4, math.pi / 2)
    wstaw(swiatynia_bryla, -10.5, 13, 0, 4.8, math.pi / 2, a=(TERAKOTA, MARMUR, (226, 220, 206), 1.35, 1.75, 1.3))
    for i in range(10):
        kolumna(-8.0, 21 + i * 1.6, 0, 4.0, 0.22, TRAWERTYN)
    box(-8.0, 28.2, 4.0, 1.0, 15.4, 0.6, TRAWERTYN)
    box(-10.5, 28.2, 0, 4, 15, 4.6, (226, 206, 170))
    dach_dwuspadowy(-10.0, 28.2, 4.6, 5, 15.6, 1.4, TERAKOTA, wzdluz="y")
    # prawa strona (fronty na -X): kuria, świątynia, okrągła świątynia Westy
    wstaw(m_kuria, 10.0, 4, 0, 3.4, -math.pi / 2)
    wstaw(swiatynia_bryla, 10.5, 15, 0, 4.4, -math.pi / 2)
    cyl(8.0, 26, 0, 2.2, 0.6, MARMUR_C, v=24)
    for i in range(14):
        a = i * 2 * math.pi / 14
        kolumna(8.0 + 1.9 * math.cos(a), 26 + 1.9 * math.sin(a), 0.6, 3.0, 0.14)
    cyl(8.0, 26, 3.6, 2.15, 0.4, MARMUR, v=24)
    stozek(8.0, 26, 4.0, 2.25, 0.3, 1.2, (190, 150, 90), v=24)
    # oś: łuk triumfalny i Koloseum w oddali
    wstaw(m_luk_triumfalny, 0, 32, 0, 3.0)
    wstaw(m_koloseum, 4, 72, 0, 15)
    # kolumny honorowe z orłami
    for x in (-4.5, 4.5):
        box(x, 1, 0, 1.0, 1.0, 1.2, MARMUR_C)
        cyl(x, 1, 1.2, 0.3, 5.5, MARMUR, v=12)
        box(x, 1, 6.7, 0.75, 0.75, 0.3, MARMUR_C)
        orzel(x, 1, 7.45, 1.6)
    # wzgórza (Palatyn, Eskwilin) i drzewa
    kopula(-30, 60, 0, 22, (96, 104, 70), seg=20, ringi=6, skala_z=0.38)
    kopula(32, 78, 0, 26, (100, 108, 72), seg=20, ringi=6, skala_z=0.3)
    kopula(-5, 125, 0, 40, (112, 112, 96), seg=20, ringi=6, skala_z=0.22)
    for (x, y, s) in [(-14, 6, 2.4), (-14.5, 10, 2.8), (14.5, 9, 2.6), (14, 21, 2.8), (-14, 21, 2.6),
                      (-17, 40, 3.4), (17, 44, 3.2), (-20, 52, 4), (22, 55, 3.6), (-8, 54, 3.0), (12, 50, 3.0),
                      (-3.5, 44, 2.6), (6, 46, 2.8)]:
        cyprys_w(x, y, s)
    for (x, y, s) in [(-16, 30, 2.6), (17, 33, 2.8), (-25, 46, 3.4), (27, 48, 3.2), (-11, 64, 3.2)]:
        wstaw(m_pinia, x, y, 0, s)
    for (x, y) in [(-2.5, 8), (2.8, 14), (-3.2, 20)]:                         # kamienne ławy
        box(x, y, 0, 1.4, 0.5, 0.45, MARMUR_C)
    kula(-60, 160, 6, 9, (255, 214, 140), seg=16, ringi=10, emisja=6.0)      # tarcza słońca
    przygotuj_render(1280, 720, False, 48, odbicia=4)
    niebo_gradient((255, 170, 96), (66, 70, 128), 1.0, srodek=(236, 128, 96))
    slonce(rot=(1.3, 0.0, -2.3), energia=3.4, kolor=(255, 186, 116), kat=0.05)
    slonce(rot=(0.9, 0.0, 0.5), energia=0.6, kolor=(170, 170, 230))
    kamera((0.0, -15.0, 2.6), (0.5, 30, 6.0), obiektyw=24)
    renderuj(os.path.join(UI, "tlo_tytul.png"))


def tlo_bitwy():
    """Puste pole bitwy: łąka, łagodne wzgórza, lasek, droga, w oddali rzymski obóz na wzgórzu."""
    czysc()
    box(0, 50, -0.2, 400, 400, 0.2, (122, 156, 78))
    for (x, y, r, h, k) in [(-38, 70, 30, 0.3, (106, 142, 70)), (40, 80, 34, 0.28, (114, 150, 74)),
                            (0, 140, 70, 0.22, (120, 140, 100)), (-80, 120, 50, 0.3, (110, 132, 96)),
                            (70, 130, 50, 0.32, (116, 136, 98)), (22, 46, 14, 0.25, (118, 160, 76))]:
        kopula(x, y, 0, r, k, seg=24, ringi=6, skala_z=h)
    for i in range(70):                                                       # kępy trawy i kwiaty
        x = -26 + (i * 37) % 52
        y = -4 + (i * 53) % 44
        ikosfera(x, y, 0.0, 0.35 + (i % 3) * 0.12, (100, 140, 64) if i % 2 else (134, 168, 84),
                 skala=(1.4, 1, 0.5))
    for (x, y) in [(-24, 30), (-21, 33), (-26, 36), (-19, 38), (-29, 28), (26, 26), (29, 30), (24, 33)]:
        wstaw(m_dab, x, y, 0, 2.4 + (x % 3) * 0.3)
    for (x, y) in [(-15, 46), (-13, 48), (31, 40), (34, 42), (15, 60)]:
        cyprys_w(x, y, 3.0)
    for i in range(30):                                                       # droga
        box(-6 + i * 0.6, -6 + i * 3.4, 0.0, 3.0, 3.6, 0.04 + 0.006 * (i % 2), (184, 164, 120),
            rot=(0, 0, -0.17))
    # obóz rzymski na wzgórzu
    wstaw(m_koszary, 22, 46, 3.2, 4.0)
    for (x, y) in [(-6, 10), (7, 16), (-12, 20)]:
        wstaw(m_skala_0, x, y, 0, 1.0)
    for (x, y, z, s) in [(-40, 160, 40, 1.0), (10, 170, 46, 1.3), (60, 150, 38, 0.9), (-80, 140, 48, 1.1)]:
        for k in range(5):
            ikosfera(x + k * 6 * s, y, z + (k % 2) * 2 * s, (8 - abs(k - 2) * 2) * s, (250, 248, 246),
                     skala=(1.4, 1, 0.55))
    przygotuj_render(1280, 720, False, 32, odbicia=3)
    niebo_gradient((214, 226, 236), (92, 140, 210), 1.0)
    slonce(rot=(0.95, 0.15, -0.75), energia=3.6, kolor=(255, 244, 222))
    kamera((0.0, -12.0, 3.6), (0.0, 40, 1.8), obiektyw=28)
    renderuj(os.path.join(UI, "tlo_bitwy.png"))


def ikona():
    """Ikona gry: złoty orzeł SPQR w wieńcu laurowym na purpurowo-czerwonym tle."""
    czysc()
    cyl(0, 0.2, 0.0, 1.0, 0.1, CZERWIEN_C, v=48, rot=(math.pi / 2, 0, 0))
    torus(0, 0.12, 0.0, 0.98, 0.05, ZLOTO, rot=(math.pi / 2, 0, 0), seg=48, mseg=6, metal=0.6, szorstkosc=0.35)
    for k in range(26):                                                       # wieniec laurowy
        a = math.pi * (-0.42 + 0.84 * (k % 13) / 12) + (0 if k < 13 else math.pi)
        a = -math.pi / 2 + (1 if k < 13 else -1) * (0.35 + 2.4 * (k % 13) / 12)
        x, z = 0.78 * math.cos(a), 0.78 * math.sin(a)
        kula(x, 0.05, z, 0.075, (110, 150, 50) if k % 2 else (150, 176, 60), seg=6, ringi=4,
             skala=(1, 0.4, 2.0)).rotation_euler = (0, -a, 0)
    orzel(0, -0.05, 0.02, 1.55)
    box(0, -0.02, -0.66, 0.95, 0.06, 0.32, CZERWIEN)
    box(0, -0.0, -0.68, 1.03, 0.05, 0.38, ZLOTO, metal=0.6, szorstkosc=0.35)
    napis("SPQR", 0, -0.06, -0.5, 0.26, ZLOTO, gl=0.02, metal=0.6, szorstkosc=0.35)
    przygotuj_render(256, 256, True, 48)
    swiat((226, 220, 210), 0.9)
    slonce(rot=(1.1, 0.3, -0.4), energia=3.4)
    kamera((0, -6, 0), (0, 0, 0), orto=2.12)
    renderuj(os.path.join(GODOT, "icon.png"))


# ================================================================= MAIN
def m_faros():
    """Latarnia Faros w Aleksandrii (skala makiety ≤ 5 m): kwadratowa podstawa, ośmioboczne piętro, okrągła
    latarnia z ogniem i posągiem na szczycie, na kamiennym molo."""
    box(0, 0, 0, 1.8, 1.8, 0.12, KAMIEN)
    box(0, 0, 0.12, 1.3, 1.3, 0.25, TRAWERTYN_C)
    for s_ in (-1, 1):
        box(s_ * 0.55, 0, 0.37, 0.12, 1.2, 0.1, TRAWERTYN)                       # blanki tarasu
        box(0, s_ * 0.55, 0.37, 1.2, 0.12, 0.1, TRAWERTYN)
    stozek(0, 0, 0.37, 0.52, 0.42, 1.9, TRAWERTYN, v=4, rot=(0, 0, math.pi / 4))   # wieża (kwadratowa)
    for z in (0.8, 1.3, 1.8):
        for k in range(4):
            a = k * math.pi / 2
            box(0.43 * math.cos(a) * (1 - (z - 0.37) * 0.05), 0.43 * math.sin(a) * (1 - (z - 0.37) * 0.05), z,
                0.08 if k % 2 else 0.02, 0.02 if k % 2 else 0.08, 0.16, OKNO)
    box(0, 0, 2.27, 0.92, 0.92, 0.08, MARMUR)
    cyl(0, 0, 2.35, 0.3, 1.0, MARMUR, v=8)                                       # piętro ośmioboczne
    cyl(0, 0, 3.35, 0.34, 0.06, MARMUR_C, v=8)
    cyl(0, 0, 3.41, 0.2, 0.6, TRAWERTYN, v=12)                                   # latarnia
    for k in range(8):
        a = k * math.pi / 4
        cyl(0.2 * math.cos(a), 0.2 * math.sin(a), 3.41, 0.025, 0.55, MARMUR, v=5)
    with Grupa("anim_ogien_faros", (0, 0, 3.5)):
        stozek(0, 0, 3.45, 0.14, 0.0, 0.4, (255, 150, 40), v=6, emisja=3.5)
        stozek(0.03, 0.02, 3.45, 0.08, 0.0, 0.28, (255, 220, 90), v=5, emisja=4.5)
    cyl(0, 0, 4.01, 0.22, 0.05, MARMUR_C, v=12)
    cyl(0, 0, 4.06, 0.05, 0.4, BRAZ, v=6, metal=0.5)                              # posąg Posejdona (zarys)
    kula(0, 0, 4.5, 0.07, BRAZ, seg=8, ringi=5, metal=0.5)
    walec((0.05, 0, 4.3), (0.18, 0, 4.62), 0.012, BRAZ, v=4, metal=0.5)


def m_palma(ziarno=51):
    """Palma daktylowa: lekko wygięty pień z łuskami i pióropusz liści."""
    r = _random.Random(ziarno)
    h = r.uniform(1.8, 2.4)
    lean = r.uniform(0.15, 0.35)
    pts = [(lean * (k / 6) ** 2, 0, h * k / 6) for k in range(7)]
    pien = _pien(pts, 0.08, 0.055, poszerzenie=1.4, v=7)
    _koloruj(pien, (110, 84, 56), (150, 120, 82), ziarno=ziarno)
    szczyt = pts[-1]
    liscie = []
    for j in range(9):
        a = j * 2 * math.pi / 9 + r.uniform(-0.2, 0.2)
        d = r.uniform(0.7, 0.95)
        kon_ = (szczyt[0] + d * math.cos(a), szczyt[1] + d * math.sin(a), szczyt[2] - r.uniform(0.25, 0.45))
        sr = ((szczyt[0] + kon_[0]) / 2, (szczyt[1] + kon_[1]) / 2, szczyt[2] + 0.12)
        liscie.append(belka(szczyt, sr, 0.16, 0.012, ZIELEN))
        liscie.append(belka(sr, kon_, 0.11, 0.012, ZIELEN))
    bpy.ops.object.select_all(action="DESELECT")
    for o in liscie:
        o.select_set(True)
    bpy.context.view_layer.objects.active = liscie[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.join()
    k = bpy.context.view_layer.objects.active
    _koloruj(k, (50, 96, 42), (110, 158, 70), ziarno=ziarno)
    kula(szczyt[0], 0, szczyt[2] - 0.05, 0.09, (150, 100, 50), seg=6, ringi=4)       # daktyle


TEREN_WARIANTY = {"cyprys": (m_cyprys, 5), "pinia": (m_pinia, 3), "oliwka": (m_oliwka, 7), "dab": (m_dab, 11),
                  "krzak": (m_krzak, 13), "skala_0": (m_skala_0, 21), "skala_1": (m_skala_1, 23),
                  "trzcina": (m_trzcina, 41), "klif": (m_klif, 31), "palma": (m_palma, 51)}
ILE_WARIANTOW = 4
BEZ_WYPALANIA = ("rusztowanie",)
TEREN = {"cyprys": m_cyprys, "pinia": m_pinia, "oliwka": m_oliwka, "dab": m_dab, "krzak": m_krzak,
         "skala_0": m_skala_0, "skala_1": m_skala_1, "trzcina": m_trzcina, "gora": m_gora, "wzgorze": m_wzgorze,
         "klif": m_klif, "palma": m_palma}
BUDYNKI = {"chata": m_chata, "domus": m_domus, "insula": m_insula, "pole": m_pole, "winnica": m_winnica,
           "tartak": m_tartak, "kamieniolom": m_kamieniolom, "targ": m_targ, "swiatynia": m_swiatynia,
           "koszary": m_koszary, "mury": m_mury, "port": m_port, "akwedukt": m_akwedukt, "termy": m_termy,
           "amfiteatr": m_amfiteatr, "kuria": m_kuria, "bazylika": m_bazylika, "rusztowanie": m_rusztowanie}
ZABYTKI = {"wilczyca": m_wilczyca, "kapitol": m_kapitol, "koloseum": m_koloseum, "panteon": m_panteon,
           "luk_triumfalny": m_luk_triumfalny, "kolumna_trajana": m_kolumna_trajana, "ruiny": m_ruiny,
           "faros": m_faros}
OBOZY = {"oboz_barbarzyncow": m_oboz_barbarzyncow, "oboz_kartaginy": m_oboz_kartaginy}
INNE = {"galera": m_galera, "sztandar": m_sztandar, "znacznik": m_znacznik, "ognisko": m_ognisko}
JEDNOSTKI = ["legionista", "welita", "lucznik", "ekwita", "pretorianin", "balista", "galijczyk", "kartaginczyk",
             "slon", "german", "hun", "got", "egipcjanin", "nubijczyk"]
JEDNOSTKI_BRYLY = {"ekwita": m_ekwita, "hun": m_hun, "slon": m_slon, "balista": m_balista}


def eksportuj_wypalony(nazwa):
    """Budynek: łączenie, fazowanie krawędzi (bevel) i wypalenie koloru z AO do tekstury."""
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.startswith(CZESCI_RUCHOME)]
    o = polacz(obs, nazwa, (0, 0, 0))
    fazuj(o, 0.012)
    wypal_teksture(o, 512 if nazwa in BUDYNKI else 768, zasieg=0.45, sila=0.85)
    zapisz_glb(nazwa)


def eksportuj_warianty(nazwa):
    """Roślinność i skały: ILE_WARIANTOW wersji (inne ziarno budowy + deformacja Geometry Nodes), AO w kolorach
    wierzchołków. Pliki <nazwa>_0..N-1.glb, a <nazwa>.glb = wariant 0 (zgodność wsteczna)."""
    fn, ziarno0 = TEREN_WARIANTY[nazwa]
    for w in range(ILE_WARIANTOW):
        czysc()
        fn(ziarno=ziarno0 + w * 101)
        obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        o = polacz(obs, "%s_%d" % (nazwa, w), (0, 0, 0))
        if w > 0:
            r = _random.Random(ziarno0 * 7 + w)
            warianty_gn(o, ziarno0 + w, sila=0.07 if nazwa in ("klif", "trzcina") else 0.1,
                        skala=(r.uniform(0.88, 1.12), r.uniform(0.88, 1.12), r.uniform(0.9, 1.15)))
        if nazwa.startswith(("skala", "klif")):
            fazuj(o, 0.02)
        ao_wierzcholki(o, zasieg=0.5 if nazwa != "trzcina" else 0.25, sila=0.75)
        zapisz_glb("%s_%d" % (nazwa, w))
        if w == 0:
            zapisz_glb(nazwa)


def podglad(katalog):
    """--podglad KATALOG: szybkie podglądy 3/4 (256×256) wybranych (--tylko) modeli — do sprawdzania wyglądu."""
    os.makedirs(katalog, exist_ok=True)
    wszystkie = {}
    for grupa in (TEREN, BUDYNKI, ZABYTKI, OBOZY, INNE, JEDNOSTKI_BRYLY):
        wszystkie.update(grupa)
    for n, p in list(JEDNOSTKI_PIESZE.items()) + list(POSTACIE.items()):
        wszystkie[n] = (lambda p=p: m_postac(p))
    for nazwa, fn in wszystkie.items():
        if not chce(nazwa):
            continue
        czysc()
        _wexillum_nr[0] = 0
        fn()
        if nazwa in ZYCIE:
            ZYCIE[nazwa]()
        przygotuj_render(256, 256, True, 16)
        swiat((210, 220, 236), 1.0)
        slonce(rot=(0.85, 0.15, -0.65), energia=3.6)
        kadruj((-0.6, 1.0, -0.78), 1.06)
        renderuj(os.path.join(katalog, nazwa + ".png"))


def main():
    start = time.time()
    if "--podglad" in ARGS:
        podglad(ARGS[ARGS.index("--podglad") + 1])
        return
    os.makedirs(MODELE, exist_ok=True)
    os.makedirs(UI, exist_ok=True)
    for grupa in (TEREN, BUDYNKI, ZABYTKI, OBOZY, INNE):
        for nazwa, fn in grupa.items():
            if not chce(nazwa):
                continue
            if nazwa in TEREN_WARIANTY:
                eksportuj_warianty(nazwa)
                continue
            czysc()
            _wexillum_nr[0] = 0
            fn()
            if grupa is BUDYNKI and nazwa in ZYCIE:
                ZYCIE[nazwa]()
            if grupa in (BUDYNKI, ZABYTKI, OBOZY) and nazwa not in BEZ_WYPALANIA:
                eksportuj_wypalony(nazwa)
            else:
                eksportuj(nazwa)
            if RENDERY and grupa is BUDYNKI and nazwa != "rusztowanie":
                ikona_budynku(nazwa)
    for nazwa in JEDNOSTKI:
        if not chce(nazwa):
            continue
        czysc()
        if nazwa in JEDNOSTKI_BRYLY:
            JEDNOSTKI_BRYLY[nazwa]()
            eksportuj(nazwa)
        else:
            m_postac(JEDNOSTKI_PIESZE[nazwa], czesci=True)
            eksportuj_postac(nazwa)
        if RENDERY:
            karta(nazwa)
    for nazwa, p in POSTACIE.items():
        if not chce(nazwa):
            continue
        czysc()
        m_postac(p, czesci=True)
        eksportuj_postac(nazwa)
        if RENDERY:
            portret(nazwa)
    if RENDERY:
        if chce("tlo_tytul"):
            tlo_tytul()
        if chce("tlo_bitwy"):
            tlo_bitwy()
        if chce("ikona"):
            ikona()
    print("GOTOWE (%.0f s)" % (time.time() - start))


main()
