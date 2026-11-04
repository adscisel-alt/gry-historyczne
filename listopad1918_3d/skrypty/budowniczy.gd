extends RefCounted
## Proceduralne dioramy 3D wszystkich 14 lokacji.
## Każda lokacja to „pudełko teatralne”: podłoga, ściany/kulisy, rekwizyty z brył,
## tekstury generowane w kodzie i miejsca hotspotów (postaci, przedmiotów, wyjść).

const Motyw = preload("res://skrypty/motyw.gd")

var korzen: Node3D
var miejsca: Dictionary = {}          # hid -> {typ, poz, rozmiar}
var kamera := {"poz": Vector3(0, 2.5, 7.4), "cel": Vector3(0, 1.4, -2.0), "fov": 50.0}
var granice := Rect2(-5.6, -2.6, 11.2, 3.4)   # x, z, szerokość, głębokość obszaru chodzenia
var start_janka := Vector3(-4.2, 0, -0.4)
var otoczenie := {"tlo": Color(0.6, 0.55, 0.48), "ambient": Color(0.75, 0.68, 0.58), "ambient_moc": 0.55,
	"slonce_kat": Vector3(-50, -35, 0), "slonce_moc": 1.0, "slonce_kolor": Color(1.0, 0.93, 0.8), "mgla": 0.012}
var kolysanie := false

static var _materialy: Dictionary = {}
static var _tekstury: Dictionary = {}


func _init(p_korzen: Node3D) -> void:
	korzen = p_korzen


# =================================================================== kolory i materiały
static func K(v: float, cieplo: float = 1.0) -> Color:
	var t := clampf(v / 255.0, 0.0, 1.0)
	return Color(t, t * lerpf(1.0, 0.92, cieplo), t * lerpf(1.0, 0.80, cieplo))


func mat(kolor: Color, tex: Texture2D = null, skala_uv: Vector3 = Vector3.ONE, nieoswietlony: bool = false) -> StandardMaterial3D:
	var klucz := "%s|%s|%s|%s" % [kolor.to_html(), str(tex.get_instance_id()) if tex else "-", str(skala_uv), nieoswietlony]
	if _materialy.has(klucz):
		return _materialy[klucz]
	var m := StandardMaterial3D.new()
	m.albedo_color = kolor
	m.roughness = 0.9
	if tex:
		m.albedo_texture = tex
		m.uv1_scale = skala_uv
	if nieoswietlony:
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	if kolor.a < 0.99:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_materialy[klucz] = m
	return m


func _mesh(mesh: Mesh, poz: Vector3, material: Material, rot: Vector3 = Vector3.ZERO, rodzic: Node3D = null) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = material
	mi.position = poz
	mi.rotation_degrees = rot
	(rodzic if rodzic else korzen).add_child(mi)
	return mi


func box(rozmiar: Vector3, poz: Vector3, v: float, rot: Vector3 = Vector3.ZERO, tex: Texture2D = null, uv: Vector3 = Vector3.ONE) -> MeshInstance3D:
	var m := BoxMesh.new()
	m.size = rozmiar
	return _mesh(m, poz, mat(K(v), tex, uv), rot)


func boxk(rozmiar: Vector3, poz: Vector3, kolor: Color, rot: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var m := BoxMesh.new()
	m.size = rozmiar
	return _mesh(m, poz, mat(kolor), rot)


func cyl(r: float, h: float, poz: Vector3, v: float, segmenty: int = 16, r_gora: float = -1.0, rot: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var m := CylinderMesh.new()
	m.bottom_radius = r
	m.top_radius = r if r_gora < 0 else r_gora
	m.height = h
	m.radial_segments = segmenty
	m.rings = 1
	return _mesh(m, poz, mat(K(v)), rot)


func kula(r: float, poz: Vector3, v: float, kolor_alfa: float = 1.0) -> MeshInstance3D:
	var m := SphereMesh.new()
	m.radius = r
	m.height = r * 2
	m.radial_segments = 12
	m.rings = 6
	var k := K(v)
	k.a = kolor_alfa
	return _mesh(m, poz, mat(k), Vector3.ZERO)


func pryzma(rozmiar: Vector3, poz: Vector3, v: float, rot: Vector3 = Vector3.ZERO) -> MeshInstance3D:
	var m := PrismMesh.new()
	m.size = rozmiar
	return _mesh(m, poz, mat(K(v)), rot)


func obraz(tex: Texture2D, rozmiar: Vector2, poz: Vector3, rot: Vector3 = Vector3.ZERO, nieoswietlony: bool = false) -> MeshInstance3D:
	var m := QuadMesh.new()
	m.size = rozmiar
	var material := mat(Color.WHITE, tex, Vector3.ONE, nieoswietlony)
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	return _mesh(m, poz, material, rot)


func napis(tekst: String, poz: Vector3, rozmiar: int = 48, v: float = 30, rodzaj: String = "plakat", rot: Vector3 = Vector3.ZERO) -> Label3D:
	var l := Label3D.new()
	l.text = tekst
	l.font = Motyw.czcionka(rodzaj)
	l.font_size = rozmiar
	l.pixel_size = 0.004
	l.modulate = K(v)
	l.outline_size = 0
	l.position = poz
	l.rotation_degrees = rot
	l.double_sided = false
	korzen.add_child(l)
	return l


func swiatlo(poz: Vector3, moc: float = 1.2, zasieg: float = 6.0, kolor: Color = Color(1.0, 0.85, 0.6)) -> OmniLight3D:
	var o := OmniLight3D.new()
	o.position = poz
	o.light_energy = moc
	o.omni_range = zasieg
	o.light_color = kolor
	korzen.add_child(o)
	return o


# =================================================================== tekstury generowane w kodzie
static func _tex(klucz: String, img: Image) -> Texture2D:
	var t := ImageTexture.create_from_image(img)
	_tekstury[klucz] = t
	return t


static func _szum(img: Image, sila: float, seed_: int) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_
	for y in img.get_height():
		for x in img.get_width():
			var c := img.get_pixel(x, y)
			var d := rng.randf_range(-sila, sila)
			img.set_pixel(x, y, Color(clampf(c.r + d, 0, 1), clampf(c.g + d, 0, 1), clampf(c.b + d, 0, 1), c.a))


static func tex_deski(v: float = 120) -> Texture2D:
	var klucz := "deski%d" % int(v)
	if _tekstury.has(klucz):
		return _tekstury[klucz]
	var img := Image.create(128, 128, false, Image.FORMAT_RGBA8)
	img.fill(K(v))
	var rng := RandomNumberGenerator.new()
	rng.seed = 5
	for i in 8:
		img.fill_rect(Rect2i(0, i * 16, 128, 16), K(v + rng.randf_range(-14, 14)))
		img.fill_rect(Rect2i(0, i * 16, 128, 1), K(v - 45))
		img.fill_rect(Rect2i(rng.randi_range(0, 120), i * 16, 1, 16), K(v - 40))
	_szum(img, 0.03, 2)
	return _tex(klucz, img)


static func tex_bruk(v: float = 125) -> Texture2D:
	var klucz := "bruk%d" % int(v)
	if _tekstury.has(klucz):
		return _tekstury[klucz]
	var img := Image.create(128, 128, false, Image.FORMAT_RGBA8)
	img.fill(K(v - 55))
	var rng := RandomNumberGenerator.new()
	rng.seed = 9
	for r in 8:
		var off := 8 if r % 2 else 0
		for k in 8:
			var x := k * 16 + off
			img.fill_rect(Rect2i(x % 128 + 1, r * 16 + 1, 14, 14), K(v + rng.randf_range(-22, 20)))
	_szum(img, 0.04, 3)
	return _tex(klucz, img)


static func tex_cegla(v: float = 110) -> Texture2D:
	var klucz := "cegla%d" % int(v)
	if _tekstury.has(klucz):
		return _tekstury[klucz]
	var img := Image.create(128, 128, false, Image.FORMAT_RGBA8)
	img.fill(K(v + 45))
	var rng := RandomNumberGenerator.new()
	rng.seed = 4
	for r in 16:
		var off := 8 if r % 2 else 0
		for k in 9:
			img.fill_rect(Rect2i(k * 16 - off + 1, r * 8 + 1, 14, 6), K(v + rng.randf_range(-15, 15)))
	_szum(img, 0.03, 6)
	return _tex(klucz, img)


static func tex_tapeta(v: float = 170) -> Texture2D:
	var klucz := "tapeta%d" % int(v)
	if _tekstury.has(klucz):
		return _tekstury[klucz]
	var img := Image.create(128, 128, false, Image.FORMAT_RGBA8)
	img.fill(K(v))
	for x in range(0, 128, 16):
		img.fill_rect(Rect2i(x, 0, 3, 128), K(v - 18))
		for y in range(8, 128, 32):
			img.fill_rect(Rect2i(x + 7, y, 3, 3), K(v - 25))
	_szum(img, 0.025, 7)
	return _tex(klucz, img)


static func tex_fasada(v: float, kolumny: int, rzedy: int, seed_: int, noc: bool = false) -> Texture2D:
	var klucz := "fasada%d_%d_%d_%d_%s" % [int(v), kolumny, rzedy, seed_, noc]
	if _tekstury.has(klucz):
		return _tekstury[klucz]
	var w := 64 * kolumny
	var h := 80 * rzedy + 40
	var img := Image.create(w, h, false, Image.FORMAT_RGBA8)
	img.fill(K(v))
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_
	img.fill_rect(Rect2i(0, 0, w, 8), K(v + 30))
	for r in rzedy:
		img.fill_rect(Rect2i(0, 18 + r * 80 + 66, w, 4), K(v + 22))
		for k in kolumny:
			var x := k * 64 + 18
			var y := 18 + r * 80
			var jasne := rng.randf() < (0.35 if noc else 0.2)
			var kol := K(235) if jasne and noc else (K(205) if jasne else K(48))
			img.fill_rect(Rect2i(x - 3, y - 3, 34, 56), K(v + 25))
			img.fill_rect(Rect2i(x, y, 28, 50), kol)
			img.fill_rect(Rect2i(x + 13, y, 2, 50), K(v - 10))
			img.fill_rect(Rect2i(x, y + 18, 28, 2), K(v - 10))
	img.fill_rect(Rect2i(w / 2 - 14, h - 44, 28, 44), K(40))
	_szum(img, 0.03, seed_)
	return _tex(klucz, img)


static func tex_niebo(gora: float, dol: float, noc: bool = false) -> Texture2D:
	var klucz := "niebo%d_%d_%s" % [int(gora), int(dol), noc]
	if _tekstury.has(klucz):
		return _tekstury[klucz]
	var img := Image.create(64, 128, false, Image.FORMAT_RGBA8)
	for y in 128:
		img.fill_rect(Rect2i(0, y, 64, 1), K(lerpf(gora, dol, y / 127.0)))
	var rng := RandomNumberGenerator.new()
	rng.seed = 12
	if noc:
		for _i in 60:
			img.set_pixel(rng.randi_range(0, 63), rng.randi_range(0, 70), K(235))
	else:
		for _i in 7:
			var cx := rng.randi_range(0, 63)
			var cy := rng.randi_range(10, 60)
			for _j in 6:
				var rr := rng.randi_range(3, 8)
				var ox := cx + rng.randi_range(-8, 8)
				var oy := cy + rng.randi_range(-2, 2)
				for yy in range(-rr, rr):
					for xx in range(-rr * 2, rr * 2):
						if xx * xx / 4.0 + yy * yy <= rr * rr:
							var px := (ox + xx + 64) % 64
							var py := clampi(oy + yy, 0, 127)
							img.set_pixel(px, py, img.get_pixel(px, py).lerp(K(240), 0.35))
	return _tex(klucz, img)


# =================================================================== rejestracja hotspotów
func postac(hid: String, x: float, z: float) -> void:
	miejsca[hid] = {"typ": "postac", "poz": Vector3(x, 0, z)}


func obiekt(hid: String, poz: Vector3, rozmiar: Vector3) -> void:
	miejsca[hid] = {"typ": "obiekt", "poz": poz, "rozmiar": rozmiar}


func przedmiot(hid: String, poz: Vector3, rozmiar: Vector3 = Vector3(0.7, 0.7, 0.7)) -> void:
	miejsca[hid] = {"typ": "przedmiot", "poz": poz, "rozmiar": rozmiar}


func wyjscie(hid: String, prawa: bool = true) -> void:
	var x := 5.25 if prawa else -5.25
	miejsca[hid] = {"typ": "wyjscie", "poz": Vector3(x, 1.25, 0.1), "rozmiar": Vector3(1.4, 1.1, 0.6)}


# =================================================================== elementy złożone
func pokoj(v_sciany: float = 150, v_podlogi: float = 110, tex_scian: Texture2D = null, glebokosc: float = 6.0, wysokosc: float = 4.4) -> void:
	var podloga := tex_deski(v_podlogi)
	box(Vector3(13.6, 0.2, glebokosc + 2.0), Vector3(0, -0.1, -glebokosc / 2 + 0.6), 255, Vector3.ZERO, podloga, Vector3(6, 4, 1))
	var t := tex_scian if tex_scian else tex_tapeta(v_sciany)
	box(Vector3(13.6, wysokosc, 0.2), Vector3(0, wysokosc / 2, -glebokosc - 0.1), 255, Vector3.ZERO, t, Vector3(7, 2.5, 1))
	for s in [-1, 1]:
		box(Vector3(0.2, wysokosc, glebokosc + 2.0), Vector3(s * 6.8, wysokosc / 2, -glebokosc / 2 + 0.6), v_sciany - 25, Vector3.ZERO, t, Vector3(4, 2.5, 1))
	# lamperia i listwy
	box(Vector3(13.4, 1.1, 0.06), Vector3(0, 0.55, -glebokosc + 0.03), v_sciany - 55)
	box(Vector3(13.4, 0.08, 0.1), Vector3(0, 1.12, -glebokosc + 0.06), v_sciany - 20)
	# cokół dioramy (drewniana podstawa „pudełka”)
	box(Vector3(14.4, 0.6, glebokosc + 2.6), Vector3(0, -0.5, -glebokosc / 2 + 0.6), 45, Vector3.ZERO, tex_deski(70), Vector3(6, 1, 1))


func plener(v_ziemi: float = 125, niebo_gora: float = 225, niebo_dol: float = 185, noc: bool = false) -> void:
	box(Vector3(40, 0.2, 26), Vector3(0, -0.1, -8), 255, Vector3.ZERO, tex_bruk(v_ziemi), Vector3(20, 13, 1))
	obraz(tex_niebo(niebo_gora, niebo_dol, noc), Vector2(80, 30), Vector3(0, 12, -20), Vector3.ZERO, true)
	box(Vector3(14.4, 0.6, 9.0), Vector3(0, -0.5, -2.0), 45, Vector3.ZERO, tex_deski(70), Vector3(6, 1, 1))


func okno(poz: Vector3, w: float, h: float, jasnosc: float = 225, noc: bool = false) -> void:
	box(Vector3(w + 0.24, h + 0.24, 0.08), poz, 70)
	var szyba := K(50 if noc else jasnosc)
	var mi := boxk(Vector3(w, h, 0.04), poz + Vector3(0, 0, 0.05), szyba)
	mi.material_override = mat(szyba, null, Vector3.ONE, true)
	box(Vector3(0.07, h, 0.06), poz + Vector3(0, 0, 0.09), 80)
	box(Vector3(w, 0.07, 0.06), poz + Vector3(0, h / 6, 0.09), 80)
	box(Vector3(w + 0.5, 0.08, 0.25), poz + Vector3(0, -h / 2 - 0.1, 0.12), 200)
	if noc:
		for i in 5:
			kula(0.03, poz + Vector3(-w / 2 + 0.2 + i * w / 5.5, -h / 4 + (i % 2) * 0.2, 0.08), 240)


func regal(poz: Vector3, w: float, h: float, seed_: int = 1) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_
	box(Vector3(w, h, 0.5), poz + Vector3(0, h / 2, 0), 60)
	var polki := int(h / 0.62)
	for p in polki:
		var py := 0.1 + p * (h - 0.1) / polki
		box(Vector3(w - 0.08, 0.05, 0.46), poz + Vector3(0, py, 0.04), 80)
		var x := -w / 2 + 0.1
		while x < w / 2 - 0.12:
			var bw := rng.randf_range(0.05, 0.12)
			var bh := rng.randf_range(0.32, 0.5)
			box(Vector3(bw, bh, 0.34), poz + Vector3(x + bw / 2, py + bh / 2 + 0.03, 0.06), rng.randf_range(60, 210))
			x += bw + 0.01


func stol(poz: Vector3, w: float, d: float, h: float = 0.95, v: float = 85) -> void:
	box(Vector3(w, 0.08, d), poz + Vector3(0, h, 0), v + 10)
	for sx in [-1, 1]:
		for sz in [-1, 1]:
			box(Vector3(0.08, h, 0.08), poz + Vector3(sx * (w / 2 - 0.08), h / 2, sz * (d / 2 - 0.08)), v - 20)


func papiery(poz: Vector3, n: int, seed_: int = 2) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_
	for i in n:
		box(Vector3(0.32, 0.01, 0.42), poz + Vector3(rng.randf_range(-0.5, 0.5), 0.01 + i * 0.004, rng.randf_range(-0.2, 0.2)),
			rng.randf_range(210, 240), Vector3(0, rng.randf_range(-30, 30), 0))


func lawka(poz: Vector3, w: float = 2.0) -> void:
	box(Vector3(w, 0.07, 0.45), poz + Vector3(0, 0.48, 0), 80)
	box(Vector3(w, 0.5, 0.06), poz + Vector3(0, 0.8, -0.2), 80)
	for sx in [-1, 1]:
		box(Vector3(0.07, 0.48, 0.4), poz + Vector3(sx * (w / 2 - 0.1), 0.24, 0), 50)


func drzwi(poz: Vector3, w: float = 1.1, h: float = 2.3, v: float = 75, rot_y: float = 0.0) -> void:
	box(Vector3(w + 0.2, h + 0.15, 0.08), poz + Vector3(0, h / 2, 0), v - 30, Vector3(0, rot_y, 0))
	box(Vector3(w, h, 0.1), poz + Vector3(0, h / 2, 0.02), v, Vector3(0, rot_y, 0))
	kula(0.05, poz + Vector3(w * 0.35, h / 2, 0.1), 220)


func latarnia(poz: Vector3, swieci: bool = false) -> void:
	cyl(0.06, 3.4, poz + Vector3(0, 1.7, 0), 35, 8)
	cyl(0.16, 0.3, poz + Vector3(0, 0.15, 0), 35, 8)
	var klosz := cyl(0.2, 0.42, poz + Vector3(0, 3.6, 0), 230 if swieci else 190, 6, 0.14)
	if swieci:
		klosz.material_override = mat(K(250), null, Vector3.ONE, true)
		swiatlo(poz + Vector3(0, 3.5, 0.3), 1.6, 7.0)
	cyl(0.26, 0.2, poz + Vector3(0, 3.9, 0), 30, 6, 0.02)


func drzewo(poz: Vector3, h: float, seed_: int) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_
	cyl(0.14, h * 0.55, poz + Vector3(0, h * 0.27, 0), 55, 8, 0.1)
	for _i in 9:
		kula(rng.randf_range(h * 0.13, h * 0.22), poz + Vector3(rng.randf_range(-h * 0.22, h * 0.22),
			h * 0.62 + rng.randf_range(-h * 0.15, h * 0.2), rng.randf_range(-h * 0.15, h * 0.15)), rng.randf_range(70, 105))


func flaga_pl(poz: Vector3, w: float = 1.0, maszt: float = 2.6) -> void:
	cyl(0.03, maszt, poz + Vector3(0, maszt / 2, 0), 40, 6)
	boxk(Vector3(w, w * 0.3, 0.02), poz + Vector3(w / 2 + 0.03, maszt - w * 0.15, 0), Color(0.95, 0.94, 0.9))
	boxk(Vector3(w, w * 0.3, 0.02), poz + Vector3(w / 2 + 0.03, maszt - w * 0.45, 0), Color(0.75, 0.12, 0.15))


func kamienica(poz: Vector3, w: float, h: float, d: float, v: float, seed_: int, noc: bool = false) -> void:
	box(Vector3(w, h, d), poz + Vector3(0, h / 2, 0), v - 20)
	var kol := maxi(2, int(w / 1.0))
	var rz := maxi(2, int((h - 0.6) / 1.25))
	obraz(tex_fasada(v, kol, rz, seed_, noc), Vector2(w, h), poz + Vector3(0, h / 2, d / 2 + 0.01))
	pryzma(Vector3(w + 0.3, 1.0, d + 0.3), poz + Vector3(0, h + 0.5, 0), v - 70)
	box(Vector3(0.3, 0.8, 0.3), poz + Vector3(w * 0.25, h + 0.9, 0), v - 80)


func tlum(n: int, x0: float, x1: float, z0: float, z1: float, seed_: int, skala: float = 0.75) -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_
	var ludzie := ["dorozkarz", "przekupka", "student", "konduktorka", "druh_staszek", "zawadzka", "carter", "whitby"]
	for _i in n:
		var pid: String = ludzie[rng.randi_range(0, ludzie.size() - 1)]
		var s := Sprite3D.new()
		s.texture = Dane.tex_postac(pid)
		var meta: Dictionary = Dane.grafika["postacie"][pid]
		var ps := 1.8 / 480.0 * skala
		s.pixel_size = ps
		s.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
		s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		s.modulate = Color(0.62, 0.58, 0.52)
		s.flip_h = rng.randf() < 0.5
		s.position = Vector3(rng.randf_range(x0, x1), (float(meta["h"]) / 2.0 - float(meta["stopa_px"])) * ps, rng.randf_range(z0, z1))
		korzen.add_child(s)


# =================================================================== LOKACJE
func lok_archiwum() -> void:
	otoczenie["ambient_moc"] = 0.35
	otoczenie["slonce_moc"] = 0.35
	otoczenie["tlo"] = Color(0.2, 0.15, 0.1)
	pokoj(95, 95, tex_tapeta(105))
	regal(Vector3(-5.3, 0, -5.4), 2.4, 3.8, 1)
	regal(Vector3(5.1, 0, -5.4), 2.6, 1.9, 2)
	# mapa zaborów na ścianie
	box(Vector3(2.5, 1.7, 0.06), Vector3(4.9, 3.15, -5.95), 40)
	obraz(Dane.tex_ui("mapa"), Vector2(2.3, 1.45), Vector3(4.9, 3.15, -5.9))
	obiekt("mapa_sciana", Vector3(4.9, 3.15, -5.8), Vector3(2.5, 1.7, 0.4))
	# półka z lupą
	box(Vector3(1.6, 0.06, 0.4), Vector3(-2.4, 1.7, -5.78), 70)
	przedmiot("polka", Vector3(-2.4, 2.0, -5.6))
	# biurko z szufladami
	box(Vector3(2.6, 1.0, 1.1), Vector3(0, 0.5, -3.9), 85, Vector3.ZERO, tex_deski(110))
	for i in 3:
		box(Vector3(1.7, 0.24, 0.04), Vector3(0, 0.22 + i * 0.28, -3.33), 115)
		box(Vector3(0.18, 0.05, 0.05), Vector3(0, 0.25 + i * 0.28, -3.3), 210)
	obiekt("szuflada", Vector3(0, 0.55, -3.3), Vector3(2.0, 1.1, 0.6))
	papiery(Vector3(-0.5, 1.0, -3.9), 5, 3)
	# lampa biurkowa
	cyl(0.08, 0.6, Vector3(0.8, 1.3, -4.1), 50, 8)
	cyl(0.28, 0.25, Vector3(0.8, 1.65, -4.1), 70, 12, 0.1)
	swiatlo(Vector3(0.8, 1.5, -3.6), 2.2, 6.0)
	# stereoskop na statywie
	cyl(0.04, 1.1, Vector3(1.9, 0.55, -2.9), 45, 6)
	box(Vector3(0.6, 0.35, 0.45), Vector3(1.9, 1.25, -2.9), 90)
	cyl(0.09, 0.1, Vector3(1.78, 1.27, -2.65), 25, 12, -1, Vector3(90, 0, 0))
	cyl(0.09, 0.1, Vector3(2.02, 1.27, -2.65), 25, 12, -1, Vector3(90, 0, 0))
	box(Vector3(0.05, 0.5, 0.36), Vector3(1.9, 1.3, -3.2), 215)
	obiekt("stereoskop", Vector3(1.9, 1.0, -2.9), Vector3(0.9, 1.4, 0.8))
	# stosy teczek
	for i in 6:
		box(Vector3(0.9, 0.09, 0.6), Vector3(-3.6, 0.05 + i * 0.1, -3.3), 150 + i * 12, Vector3(0, i * 7, 0))
	napis("ARCHIWUM", Vector3(-5.3, 4.0, -5.1), 64, 210)
	postac("damian", 3.7, -1.8)
	start_janka = Vector3(-4.0, 0, -0.4)


func lok_krakow_rynek() -> void:
	plener(130, 228, 190)
	# Sukiennice
	box(Vector3(8.0, 4.0, 3.0), Vector3(-6.2, 2.0, -9.0), 185)
	for i in 7:
		box(Vector3(0.75, 1.6, 0.1), Vector3(-9.6 + i * 1.15, 0.8, -7.46), 45)
	for i in 16:
		pryzma(Vector3(0.3, 0.6, 0.3), Vector3(-10.0 + i * 0.52, 4.3, -7.6), 205)
	pryzma(Vector3(8.2, 1.0, 3.2), Vector3(-6.2, 4.5, -9.0), 105)
	flaga_pl(Vector3(-6.2, 5.0, -8.0), 1.1, 2.2)
	obiekt("sukiennice", Vector3(-6.0, 2.4, -7.2), Vector3(7.5, 4.8, 0.6))
	# kamienice w tle
	var rng := RandomNumberGenerator.new()
	rng.seed = 31
	for i in 6:
		kamienica(Vector3(-1.4 + i * 1.9, 0, -12.0), 1.85, rng.randf_range(5.0, 6.6), 2.0, rng.randf_range(140, 170), 40 + i)
	# Kościół Mariacki — dwie nierówne wieże
	box(Vector3(4.6, 8.0, 5.0), Vector3(7.0, 4.0, -11.0), 95, Vector3.ZERO, tex_cegla(95), Vector3(3, 5, 1))
	pryzma(Vector3(4.8, 2.6, 5.2), Vector3(7.0, 9.3, -11.0), 75)
	box(Vector3(1.6, 13.0, 1.6), Vector3(5.2, 6.5, -8.6), 88, Vector3.ZERO, tex_cegla(90), Vector3(1, 6, 1))
	cyl(1.0, 3.4, Vector3(5.2, 14.7, -8.6), 60, 8, 0.0)
	for dx in [-0.7, 0.7]:
		cyl(0.18, 1.4, Vector3(5.2 + dx, 13.7, -8.6 + dx * 0.4), 60, 6, 0.0)
	box(Vector3(1.5, 11.0, 1.5), Vector3(8.8, 5.5, -8.6), 88, Vector3.ZERO, tex_cegla(90), Vector3(1, 5, 1))
	kula(0.85, Vector3(8.8, 11.4, -8.6), 60)
	cyl(0.05, 1.2, Vector3(8.8, 12.6, -8.6), 60, 6)
	for wy in [3.0, 6.0, 9.0]:
		box(Vector3(0.5, 1.2, 0.05), Vector3(5.2, wy, -7.78), 35)
		box(Vector3(0.5, 1.2, 0.05), Vector3(8.8, wy * 0.9, -7.83), 35)
	box(Vector3(1.4, 4.0, 0.05), Vector3(7.0, 3.6, -8.48), 40)
	obiekt("mariacki", Vector3(7.0, 5.0, -8.2), Vector3(5.6, 10.0, 1.0))
	# słup ogłoszeniowy
	cyl(0.45, 2.9, Vector3(-1.7, 1.45, -2.8), 165, 18)
	cyl(0.58, 0.18, Vector3(-1.7, 2.95, -2.8), 110, 18)
	cyl(0.5, 0.5, Vector3(-1.7, 3.3, -2.8), 90, 18, 0.0)
	for i in 3:
		box(Vector3(0.55, 0.62, 0.02), Vector3(-1.7, 0.75 + i * 0.75, -2.34), 225 - i * 18, Vector3(0, 0, (i - 1) * 4))
	obiekt("slup", Vector3(-1.7, 1.5, -2.8), Vector3(1.2, 3.4, 1.2))
	# ławka z gazetą
	lawka(Vector3(0.7, 0, -2.6), 1.8)
	przedmiot("gazeciarz", Vector3(0.7, 0.9, -2.5))
	latarnia(Vector3(3.7, 0, -3.2))
	tlum(14, -4.0, 4.5, -7.0, -5.0, 8, 0.8)
	postac("witos", 2.2, -1.5)
	wyjscie("powrot")


func lok_harcowka() -> void:
	pokoj(165, 115, tex_deski(160))
	okno(Vector3(0.6, 2.4, -5.92), 2.0, 1.7, 230)
	# hak z opaską
	box(Vector3(0.3, 0.06, 0.12), Vector3(-3.0, 2.2, -5.92), 50)
	przedmiot("hak", Vector3(-3.0, 1.9, -5.7))
	# stół z gazetami
	stol(Vector3(-1.0, 0, -3.5), 2.2, 1.2)
	papiery(Vector3(-1.0, 1.0, -3.5), 6, 5)
	obiekt("stol", Vector3(-1.0, 0.6, -3.5), Vector3(2.4, 1.3, 1.4))
	# proporzec z lilijką
	cyl(0.03, 2.8, Vector3(3.6, 1.4, -5.6), 45, 6)
	pryzma(Vector3(0.9, 1.6, 0.03), Vector3(4.1, 2.5, -5.6), 225, Vector3(0, 0, -90))
	pryzma(Vector3(0.12, 0.45, 0.02), Vector3(3.95, 2.62, -5.57), 70)
	kula(0.09, Vector3(3.82, 2.5, -5.57), 70)
	kula(0.09, Vector3(4.08, 2.5, -5.57), 70)
	box(Vector3(0.32, 0.05, 0.02), Vector3(3.95, 2.38, -5.57), 70)
	obiekt("lilijka", Vector3(4.0, 2.4, -5.5), Vector3(1.6, 1.8, 0.4))
	# tablica węzłów i plakat
	box(Vector3(1.6, 1.1, 0.05), Vector3(-5.2, 2.4, -5.93), 90)
	napis("WĘZŁY", Vector3(-5.2, 2.75, -5.89), 40, 225)
	for i in 3:
		cyl(0.12, 0.02, Vector3(-5.7 + i * 0.5, 2.3, -5.88), 220, 12, -1, Vector3(90, 0, 0))
	box(Vector3(1.3, 1.7, 0.03), Vector3(2.0, 2.5, -5.93), 225)
	napis("CZUWAJ!", Vector3(2.0, 3.05, -5.9), 54, 35)
	lawka(Vector3(-4.0, 0, -4.6), 2.4)
	lawka(Vector3(3.6, 0, -4.6), 2.4)
	drzwi(Vector3(6.68, 0, -1.8), 1.1, 2.3, 80, -90)
	postac("staszek", 1.4, -1.7)
	wyjscie("drzwi")


func lok_rr_siedziba() -> void:
	otoczenie["ambient_moc"] = 0.6
	pokoj(190, 125, tex_tapeta(190), 6.0, 4.8)
	for x in [-5.6, -2.2, 2.2, 5.6]:
		box(Vector3(0.5, 4.6, 0.2), Vector3(x, 2.3, -5.9), 210)
	okno(Vector3(-3.9, 2.7, -5.92), 1.6, 2.4, 228)
	okno(Vector3(3.9, 2.7, -5.92), 1.6, 2.4, 228)
	# jaśniejszy prostokąt po portrecie cesarza
	box(Vector3(1.4, 1.3, 0.02), Vector3(0, 3.1, -5.98), 215)
	cyl(0.02, 0.5, Vector3(0, 4.0, -5.97), 120, 4, -1, Vector3(0, 0, 0))
	obiekt("portret", Vector3(0, 3.1, -5.85), Vector3(1.6, 1.5, 0.4))
	# żyrandol
	cyl(0.02, 1.2, Vector3(0, 4.2, -3.0), 60, 4)
	cyl(0.7, 0.18, Vector3(0, 3.55, -3.0), 150, 16, 0.4)
	for i in 8:
		var a := i * TAU / 8
		kula(0.07, Vector3(cos(a) * 0.65, 3.45, -3.0 + sin(a) * 0.65), 250)
	swiatlo(Vector3(0, 3.2, -3.0), 1.4, 8.0)
	# dywan i stół obrad
	box(Vector3(7.0, 0.02, 4.0), Vector3(0, 0.01, -2.8), 95)
	box(Vector3(6.6, 0.02, 3.6), Vector3(0, 0.02, -2.8), 125)
	stol(Vector3(0.8, 0, -4.3), 4.8, 1.2, 0.9, 75)
	papiery(Vector3(0.8, 0.95, -4.3), 8, 7)
	for i in 4:
		box(Vector3(0.5, 1.1, 0.5), Vector3(-1.0 + i * 1.2, 0.55, -5.1), 70)
	drzwi(Vector3(-6.68, 0, -2.4), 1.4, 2.8, 95, 90)
	postac("wozny", -3.2, -1.3)
	postac("kakowski", -0.2, -2.6)
	postac("lubomirski", 1.8, -2.6)
	postac("ostrowski", 3.6, -2.4)
	wyjscie("do_lublina")


func lok_lublin_palac() -> void:
	otoczenie["ambient_moc"] = 0.3
	otoczenie["slonce_moc"] = 0.2
	otoczenie["tlo"] = Color(0.12, 0.1, 0.08)
	pokoj(120, 85, tex_tapeta(125))
	okno(Vector3(-4.4, 2.4, -5.92), 1.8, 2.2, 50, true)
	obiekt("okno", Vector3(-4.4, 2.4, -5.8), Vector3(2.0, 2.4, 0.4))
	regal(Vector3(-1.9, 0, -5.4), 2.2, 2.6, 4)
	stol(Vector3(1.2, 0, -3.8), 3.2, 1.2, 0.9, 75)
	papiery(Vector3(1.2, 0.95, -3.8), 9, 8)
	for x in [0.1, 2.3]:
		cyl(0.04, 0.35, Vector3(x, 1.12, -3.8), 235, 8)
		var plomien := kula(0.05, Vector3(x, 1.34, -3.8), 250)
		plomien.material_override = mat(K(255), null, Vector3.ONE, true)
		swiatlo(Vector3(x, 1.5, -3.5), 1.5, 4.5)
	box(Vector3(1.6, 2.0, 0.03), Vector3(3.8, 2.6, -5.93), 222)
	napis("REPUBLIKA", Vector3(3.8, 3.35, -5.9), 44, 35)
	for i in 5:
		box(Vector3(1.2, 0.03, 0.01), Vector3(3.7, 2.9 - i * 0.28, -5.9), 140)
	drzwi(Vector3(6.68, 0, -2.0), 1.1, 2.3, 70, -90)
	postac("daszynski", 0.5, -1.9)
	postac("rydz", 2.9, -2.0)
	wyjscie("do_drukarni")
	wyjscie("pocztowka_dalej", false)
	start_janka = Vector3(-3.4, 0, -0.4)


func lok_lublin_drukarnia() -> void:
	otoczenie["ambient_moc"] = 0.45
	pokoj(110, 80, tex_cegla(105))
	box(Vector3(0.8, 1.1, 0.02), Vector3(-5.4, 2.6, -5.97), 205)
	napis("MĄKA", Vector3(-5.4, 3.0, -5.94), 34, 40)
	box(Vector3(0.8, 1.0, 0.02), Vector3(-4.4, 2.5, -5.97), 215)
	napis("NAFTA", Vector3(-4.4, 2.85, -5.94), 34, 40)
	obiekt("plakaty", Vector3(-4.9, 2.6, -5.8), Vector3(2.0, 1.4, 0.4))
	# sznurek z odbitkami
	box(Vector3(9.0, 0.015, 0.015), Vector3(0.8, 3.7, -5.4), 60)
	for i in 10:
		box(Vector3(0.45, 0.62, 0.01), Vector3(-3.0 + i * 0.85, 3.35, -5.4), 232)
	# kaszta zecerska
	box(Vector3(2.0, 1.0, 1.0), Vector3(-2.3, 0.5, -3.6), 80, Vector3.ZERO, tex_deski(90))
	var rng := RandomNumberGenerator.new()
	rng.seed = 3
	for r in 4:
		for k in 8:
			box(Vector3(0.2, 0.03, 0.2), Vector3(-3.1 + k * 0.23, 1.02 + r * 0.02, -3.95 + r * 0.24), rng.randf_range(40, 80), Vector3(-10, 0, 0))
	obiekt("kaszta", Vector3(-2.3, 0.8, -3.6), Vector3(2.2, 1.6, 1.2))
	# prasa drukarska
	box(Vector3(1.8, 0.4, 1.3), Vector3(0.9, 0.2, -3.9), 40)
	for sx in [-1, 1]:
		box(Vector3(0.16, 2.2, 0.2), Vector3(0.9 + sx * 0.7, 1.3, -3.9), 45)
	box(Vector3(1.8, 0.3, 0.5), Vector3(0.9, 2.4, -3.9), 45)
	box(Vector3(1.3, 0.12, 1.0), Vector3(0.9, 0.9, -3.9), 90)
	var kolo := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = 0.5
	torus.outer_radius = 0.6
	kolo.mesh = torus
	kolo.material_override = mat(K(35))
	kolo.position = Vector3(2.05, 1.5, -3.6)
	kolo.rotation_degrees = Vector3(0, 0, 90)
	korzen.add_child(kolo)
	for k in 4:
		box(Vector3(0.05, 1.1, 0.05), Vector3(2.05, 1.5, -3.6), 35, Vector3(k * 45, 0, 0))
	obiekt("prasa", Vector3(0.9, 1.3, -3.9), Vector3(2.4, 2.8, 1.5))
	swiatlo(Vector3(0.0, 3.5, -2.5), 1.3, 8.0)
	postac("zecer", 2.9, -1.9)
	wyjscie("do_palacu", false)
	start_janka = Vector3(-3.6, 0, -0.4)


func lok_wagon() -> void:
	otoczenie["ambient_moc"] = 0.3
	otoczenie["slonce_moc"] = 0.15
	otoczenie["tlo"] = Color(0.1, 0.08, 0.06)
	kolysanie = true
	pokoj(115, 70, tex_deski(105), 4.2, 3.4)
	for x in [-3.6, 0.3, 4.0]:
		okno(Vector3(x, 2.0, -4.12), 2.0, 1.3, 50, true)
		kula(0.12, Vector3(x + 0.6, 2.4, -4.05), 240)
	obiekt("okno_wagon", Vector3(0.3, 2.0, -4.0), Vector3(2.2, 1.5, 0.4))
	# półki bagażowe
	box(Vector3(13.0, 0.05, 0.6), Vector3(0, 3.0, -3.8), 55)
	for x in range(-6, 7):
		box(Vector3(0.03, 0.3, 0.03), Vector3(x, 2.85, -3.55), 55)
	box(Vector3(0.8, 0.4, 0.5), Vector3(-2.5, 3.25, -3.8), 140)
	box(Vector3(0.6, 0.35, 0.45), Vector3(2.4, 3.22, -3.8), 170)
	# ławki
	for bx in [-2.2, 2.6]:
		box(Vector3(3.2, 0.5, 1.0), Vector3(bx, 0.25, -3.4), 85, Vector3.ZERO, tex_deski(100))
		box(Vector3(3.2, 1.0, 0.2), Vector3(bx, 1.0, -3.95), 90, Vector3.ZERO, tex_deski(100))
	przedmiot("siedzenie", Vector3(-2.2, 0.75, -3.2))
	drzwi(Vector3(6.68, 0, -1.6), 1.0, 2.4, 75, -90)
	napis("WARSZAWA →", Vector3(5.6, 3.0, -4.0), 40, 225)
	swiatlo(Vector3(0, 2.9, -2.0), 1.0, 7.0)
	postac("pilsudski", 1.3, -1.9)
	wyjscie("wysiadka")
	kamera["poz"] = Vector3(0, 2.3, 6.6)


func lok_dworzec() -> void:
	plener(105, 205, 170)
	otoczenie["mgla"] = 0.03
	# peron
	box(Vector3(20, 0.3, 5), Vector3(0, 0.0, -1.5), 120, Vector3.ZERO, tex_bruk(140), Vector3(10, 3, 1))
	box(Vector3(20, 0.06, 0.25), Vector3(0, 0.16, -4.0), 215)
	# lokomotywa i wagon
	cyl(0.95, 5.0, Vector3(-6.0, 1.9, -6.2), 40, 16, -1, Vector3(0, 0, 90))
	box(Vector3(2.0, 2.8, 2.2), Vector3(-2.6, 2.2, -6.2), 50)
	box(Vector3(0.6, 0.6, 0.05), Vector3(-2.6, 2.8, -5.08), 210)
	cyl(0.3, 1.3, Vector3(-7.4, 3.4, -6.2), 35, 10)
	for i in 4:
		cyl(0.6, 0.2, Vector3(-7.6 + i * 1.4, 0.75, -5.05), 25, 16, -1, Vector3(90, 0, 0))
	for i in 10:
		var para := kula(0.5 + i * 0.18, Vector3(-7.4 + i * 0.5, 4.3 + i * 0.5, -6.6 - i * 0.2), 240, 0.55 - i * 0.04)
		para.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	box(Vector3(8.0, 2.8, 2.4), Vector3(3.8, 1.9, -6.4), 60, Vector3.ZERO, tex_fasada(80, 8, 2, 5, false), Vector3(1, 1, 1))
	# stalowe łuki hali
	for i in 6:
		var x := -9.0 + i * 3.6
		box(Vector3(0.25, 6.0, 0.25), Vector3(x, 3.0, -8.0), 45)
		box(Vector3(0.25, 0.25, 9.0), Vector3(x, 6.0, -4.0), 45, Vector3(12, 0, 0))
	box(Vector3(22, 0.1, 9.5), Vector3(0, 6.5, -4.0), 200, Vector3(12, 0, 0))
	# zegar
	box(Vector3(0.2, 3.6, 0.2), Vector3(0.6, 1.8, -3.2), 45)
	cyl(0.55, 0.12, Vector3(0.6, 4.0, -3.2), 230, 24, -1, Vector3(90, 0, 0))
	box(Vector3(0.05, 0.42, 0.02), Vector3(0.6, 4.15, -3.12), 30)
	box(Vector3(0.32, 0.05, 0.02), Vector3(0.45, 4.0, -3.12), 30)
	obiekt("zegar", Vector3(0.6, 4.0, -3.1), Vector3(1.3, 1.3, 0.4))
	# bramka na peron
	for sx in [-1, 1]:
		box(Vector3(0.12, 2.6, 0.12), Vector3(-2.4 + sx * 0.95, 1.3, -2.8), 45)
	box(Vector3(2.1, 0.3, 0.12), Vector3(-2.4, 2.6, -2.8), 45)
	napis("PERRON", Vector3(-2.4, 2.6, -2.72), 36, 230)
	for k in 9:
		box(Vector3(0.03, 1.2, 0.03), Vector3(-3.2 + k * 0.2, 0.75, -2.8), 60)
	box(Vector3(1.9, 0.05, 0.05), Vector3(-2.4, 1.35, -2.8), 60)
	obiekt("bramka", Vector3(-2.4, 1.3, -2.8), Vector3(2.2, 2.8, 0.7))
	tlum(16, -4.0, 5.0, -4.6, -3.6, 21, 0.85)
	flaga_pl(Vector3(5.6, 0, -3.8), 0.9, 3.2)
	postac("koc", 1.8, -1.9)
	postac("lubomirski_dw", 3.5, -2.1)
	wyjscie("dalej_dworzec")


func lok_koszary() -> void:
	plener(90, 70, 115, true)
	otoczenie["tlo"] = Color(0.15, 0.13, 0.12)
	otoczenie["ambient_moc"] = 0.35
	otoczenie["slonce_moc"] = 0.3
	otoczenie["slonce_kolor"] = Color(0.75, 0.8, 0.9)
	kula(0.9, Vector3(-8.0, 9.0, -19.0), 245).material_override = mat(K(250), null, Vector3.ONE, true)
	# mur koszar
	box(Vector3(26, 5.0, 1.0), Vector3(0, 2.5, -7.5), 255, Vector3.ZERO, tex_cegla(95), Vector3(13, 3, 1))
	for x in [-8.0, -5.5, -3.0, 4.5, 7.0, 9.5]:
		var jasne := absf(x) < 5.0
		box(Vector3(0.9, 1.3, 0.05), Vector3(x, 3.0, -6.97), 220 if jasne else 40)
	# brama
	box(Vector3(3.6, 5.6, 1.2), Vector3(0.6, 2.8, -7.2), 65)
	box(Vector3(2.4, 3.6, 0.1), Vector3(0.6, 1.8, -6.58), 30)
	for k in 9:
		box(Vector3(0.05, 3.4, 0.05), Vector3(-0.4 + k * 0.25, 1.8, -6.5), 70)
	box(Vector3(0.9, 0.6, 0.05), Vector3(0.6, 4.6, -6.57), 40)
	box(Vector3(1.4, 0.32, 0.02), Vector3(0.6, 4.05, -6.55), 232)
	napis("Wojsko Polskie", Vector3(0.6, 4.05, -6.53), 26, 30, "reka")
	obiekt("brama", Vector3(0.6, 2.4, -6.5), Vector3(3.2, 4.4, 0.6))
	# budka wartownika
	for k in 6:
		box(Vector3(1.0, 0.4, 1.0), Vector3(4.6, 0.2 + k * 0.4, -4.6), 220 if k % 2 else 60)
	pryzma(Vector3(1.2, 0.6, 1.2), Vector3(4.6, 2.7, -4.6), 50)
	# stół sztabowy
	stol(Vector3(-1.6, 0, -3.0), 2.0, 1.1, 0.9, 70)
	box(Vector3(1.6, 0.01, 0.9), Vector3(-1.6, 0.95, -3.0), 225)
	obiekt("stol_plan", Vector3(-1.6, 0.6, -3.0), Vector3(2.2, 1.3, 1.3))
	latarnia(Vector3(-4.8, 0, -4.0), true)
	latarnia(Vector3(3.2, 0, -5.0), true)
	postac("koc_k", -3.6, -1.6)
	postac("otto", 2.7, -2.6)
	wyjscie("na_plac")


func lok_plac_saski() -> void:
	plener(140, 225, 185)
	# Pałac Saski z kolumnadą
	kamienica(Vector3(-7.5, 0, -12.0), 5.0, 6.0, 2.5, 175, 60)
	kamienica(Vector3(2.5, 0, -12.0), 5.0, 6.0, 2.5, 175, 61)
	box(Vector3(5.2, 6.4, 3.0), Vector3(-2.5, 3.2, -12.0), 190)
	box(Vector3(5.6, 0.7, 2.2), Vector3(-2.5, 6.3, -9.6), 195)
	for i in 9:
		cyl(0.2, 5.9, Vector3(-4.7 + i * 0.55, 2.95, -9.6), 228, 12)
	flaga_pl(Vector3(-2.5, 6.6, -10.5), 1.2, 2.6)
	obiekt("palac_saski", Vector3(-2.5, 3.0, -9.2), Vector3(11.0, 6.0, 1.0))
	for i in 4:
		drzewo(Vector3(4.8 + i * 1.8, 0, -8.0 - (i % 2)), 4.4, 70 + i)
	latarnia(Vector3(3.6, 0, -3.6))
	# dorożka
	box(Vector3(1.6, 1.0, 1.0), Vector3(-5.2, 1.2, -3.8), 45)
	box(Vector3(1.0, 0.8, 1.0), Vector3(-5.4, 2.0, -3.8), 40)
	for sx in [-0.6, 0.6]:
		cyl(0.45, 0.08, Vector3(-5.2 + sx, 0.45, -3.25), 30, 14, -1, Vector3(90, 0, 0))
	tlum(14, -4.5, 5.0, -7.5, -5.5, 33, 0.8)
	postac("zawadzka", 0.2, -2.0)
	postac("dorozkarz", -3.6, -1.7)
	postac("przekupka", -1.8, -2.4)
	postac("student", 2.4, -1.8)
	wyjscie("do_paryza")
	start_janka = Vector3(-4.6, 0, -0.2)


func lok_paryz_knp() -> void:
	otoczenie["ambient_moc"] = 0.6
	# ściana z oknem (otwór) i wieżą Eiffla za nim
	var t := tex_tapeta(175)
	box(Vector3(13.6, 0.2, 8.0), Vector3(0, -0.1, -2.4), 255, Vector3.ZERO, tex_deski(105), Vector3(6, 4, 1))
	box(Vector3(14.4, 0.6, 8.6), Vector3(0, -0.5, -2.4), 45, Vector3.ZERO, tex_deski(70), Vector3(6, 1, 1))
	box(Vector3(8.6, 4.4, 0.2), Vector3(2.5, 2.2, -6.1), 255, Vector3.ZERO, t, Vector3(5, 2.5, 1))
	box(Vector3(2.4, 4.4, 0.2), Vector3(-5.6, 2.2, -6.1), 255, Vector3.ZERO, t, Vector3(1.5, 2.5, 1))
	box(Vector3(2.6, 1.2, 0.2), Vector3(-3.1, 0.6, -6.1), 255, Vector3.ZERO, t, Vector3(1.5, 1, 1))
	box(Vector3(2.6, 0.7, 0.2), Vector3(-3.1, 4.05, -6.1), 255, Vector3.ZERO, t, Vector3(1.5, 1, 1))
	for s in [-1, 1]:
		box(Vector3(0.2, 4.4, 8.0), Vector3(s * 6.8, 2.2, -2.4), 150, Vector3.ZERO, t, Vector3(4, 2.5, 1))
	box(Vector3(2.6, 0.1, 0.4), Vector3(-3.1, 1.2, -6.0), 210)
	box(Vector3(0.08, 2.5, 0.08), Vector3(-3.1, 2.45, -6.05), 70)
	obraz(tex_niebo(232, 205), Vector2(30, 14), Vector3(-3, 5, -16), Vector3.ZERO, true)
	# wieża Eiffla — stożkowe segmenty
	cyl(1.6, 3.0, Vector3(-3.4, 1.5, -13.0), 55, 4, 0.9, Vector3(0, 45, 0))
	cyl(0.9, 3.4, Vector3(-3.4, 4.7, -13.0), 55, 4, 0.35, Vector3(0, 45, 0))
	cyl(0.35, 4.0, Vector3(-3.4, 8.4, -13.0), 55, 4, 0.06, Vector3(0, 45, 0))
	box(Vector3(2.4, 0.12, 2.4), Vector3(-3.4, 3.0, -13.0), 55, Vector3(0, 45, 0))
	obiekt("wieza", Vector3(-3.1, 2.5, -6.0), Vector3(2.6, 2.6, 0.4))
	regal(Vector3(-0.6, 0, -5.5), 2.2, 3.2, 6)
	stol(Vector3(-1.4, 0, -3.6), 2.6, 1.2, 0.9, 70)
	papiery(Vector3(-1.4, 0.95, -3.6), 7, 9)
	# telegraf
	stol(Vector3(1.5, 0, -3.5), 1.2, 0.8, 0.85, 75)
	box(Vector3(0.6, 0.3, 0.4), Vector3(1.5, 1.05, -3.5), 60)
	cyl(0.14, 0.12, Vector3(1.3, 1.27, -3.5), 200, 12)
	box(Vector3(0.12, 0.6, 0.02), Vector3(1.85, 1.2, -3.5), 230, Vector3(0, 0, -20))
	obiekt("telegraf", Vector3(1.5, 0.9, -3.5), Vector3(1.4, 1.5, 1.0))
	# sztaluga z wielką pocztówką z Nowego Jorku
	for sx in [-0.7, 0.7]:
		box(Vector3(0.07, 3.2, 0.07), Vector3(3.8 + sx, 1.6, -4.0), 55, Vector3(0, 0, -sx * 12))
	box(Vector3(0.07, 3.0, 0.07), Vector3(3.8, 1.5, -4.35), 55, Vector3(15, 0, 0))
	obraz(Dane.tex_ui("sztaluga"), Vector2(2.2, 2.55), Vector3(3.8, 2.15, -3.93))
	napis("COMITÉ NATIONAL POLONAIS", Vector3(2.5, 4.0, -5.98), 52, 55)
	drzwi(Vector3(6.68, 0, -2.0), 1.2, 2.5, 85, -90)
	postac("dmowski", -1.3, -1.9)
	postac("paderewski", 3.8, -3.4)
	wyjscie("do_salonu")


func lok_paryz_salon() -> void:
	otoczenie["ambient_moc"] = 0.75
	pokoj(200, 130, tex_tapeta(205), 6.0, 4.8)
	for x in [-2.6, 3.0]:
		box(Vector3(1.6, 2.9, 0.08), Vector3(x, 2.4, -5.95), 150)
		var lustro := boxk(Vector3(1.3, 2.6, 0.04), Vector3(x, 2.4, -5.9), K(232))
		lustro.material_override = mat(K(232), null, Vector3.ONE, true)
	cyl(0.02, 1.2, Vector3(0.2, 4.2, -3.0), 60, 4)
	cyl(0.8, 0.2, Vector3(0.2, 3.5, -3.0), 160, 16, 0.45)
	for i in 10:
		var a := i * TAU / 10
		kula(0.07, Vector3(0.2 + cos(a) * 0.75, 3.4, -3.0 + sin(a) * 0.75), 250)
	swiatlo(Vector3(0.2, 3.2, -3.0), 1.6, 9.0)
	# flagi Francji, Wielkiej Brytanii i USA
	var fx := -5.4
	for i in 3:
		cyl(0.03, 2.8, Vector3(fx + i * 0.55, 1.4, -5.3 + i * 0.2), 40, 6)
	for j in 3:
		boxk(Vector3(0.25, 0.5, 0.02), Vector3(fx + 0.15 + j * 0.25, 2.5, -5.28), [Color(0.1, 0.2, 0.55), Color(0.95, 0.95, 0.95), Color(0.8, 0.1, 0.15)][j])
	boxk(Vector3(0.75, 0.5, 0.02), Vector3(fx + 0.93, 2.5, -5.08), Color(0.1, 0.15, 0.45))
	boxk(Vector3(0.75, 0.1, 0.025), Vector3(fx + 0.93, 2.5, -5.07), Color(0.85, 0.1, 0.15))
	boxk(Vector3(0.1, 0.5, 0.025), Vector3(fx + 0.93, 2.5, -5.07), Color(0.85, 0.1, 0.15))
	for k in 7:
		boxk(Vector3(0.75, 0.07, 0.02), Vector3(fx + 1.48, 2.28 + k * 0.07, -4.88), Color(0.8, 0.1, 0.15) if k % 2 == 0 else Color(0.95, 0.95, 0.95))
	boxk(Vector3(0.32, 0.25, 0.025), Vector3(fx + 1.27, 2.62, -4.87), Color(0.1, 0.15, 0.45))
	obiekt("flagi", Vector3(-4.3, 2.3, -5.0), Vector3(2.2, 1.4, 0.8))
	# okrągły stół
	cyl(1.6, 0.08, Vector3(0.2, 0.95, -3.4), 110, 24)
	cyl(0.15, 0.95, Vector3(0.2, 0.47, -3.4), 70, 8)
	papiery(Vector3(0.2, 1.0, -3.4), 5, 11)
	postac("laroche", -2.4, -1.8)
	postac("whitby", 0.2, -2.2)
	postac("carter", 2.6, -1.9)
	wyjscie("do_poznania")


func lok_poznan_bazar() -> void:
	plener(125, 222, 182)
	# Hotel Bazar
	box(Vector3(9.0, 6.4, 3.0), Vector3(4.6, 3.2, -11.5), 165)
	obraz(tex_fasada(170, 9, 4, 77), Vector2(9.0, 6.4), Vector3(4.6, 3.2, -9.99))
	box(Vector3(9.2, 0.3, 3.2), Vector3(4.6, 6.5, -11.5), 130)
	napis("BAZAR", Vector3(4.6, 5.9, -9.95), 80, 232)
	flaga_pl(Vector3(2.2, 3.2, -9.9), 0.8, 1.5)
	# niemiecki szyld
	box(Vector3(3.2, 0.7, 0.08), Vector3(4.6, 4.6, -6.6), 230)
	box(Vector3(0.06, 4.3, 0.06), Vector3(3.2, 2.15, -6.6), 45)
	box(Vector3(0.06, 4.3, 0.06), Vector3(6.0, 2.15, -6.6), 45)
	napis("KÖNIGLICHE POLIZEI", Vector3(4.6, 4.65, -6.55), 40, 30)
	napis("jeszcze", Vector3(5.6, 4.4, -6.54), 30, 90, "reka")
	obiekt("szyld", Vector3(4.6, 4.6, -6.5), Vector3(3.4, 0.9, 0.4))
	for i in 3:
		kamienica(Vector3(-8.8 + i * 2.6, 0, -11.5), 2.5, 5.5 + i * 0.5, 2.0, 140 + i * 10, 80 + i)
	# tory i tramwaj
	for z in [-4.0, -5.0]:
		box(Vector3(30, 0.04, 0.08), Vector3(0, 0.02, z), 60)
	box(Vector3(4.2, 2.1, 1.5), Vector3(-4.3, 1.4, -4.5), 200)
	box(Vector3(4.4, 0.2, 1.6), Vector3(-4.3, 2.55, -4.5), 80)
	for i in 5:
		box(Vector3(0.6, 0.7, 0.05), Vector3(-5.9 + i * 0.8, 1.8, -3.73), 55)
	napis("6", Vector3(-2.5, 1.0, -3.73), 90, 30)
	box(Vector3(0.05, 1.0, 0.05), Vector3(-4.3, 3.1, -4.5), 40, Vector3(0, 0, 25))
	for sx in [-1.3, 1.3]:
		cyl(0.3, 0.1, Vector3(-4.3 + sx, 0.3, -3.72), 30, 12, -1, Vector3(90, 0, 0))
	# kiosk
	cyl(0.7, 2.2, Vector3(-0.8, 1.1, -3.2), 120, 8)
	cyl(0.9, 0.6, Vector3(-0.8, 2.5, -3.2), 70, 8, 0.0)
	for i in 3:
		box(Vector3(0.28, 0.4, 0.02), Vector3(-1.1 + i * 0.3, 1.4, -2.52), 230 - i * 15)
	przedmiot("kiosk", Vector3(-0.8, 1.2, -3.0), Vector3(1.6, 2.4, 1.6))
	tlum(10, -3.0, 6.0, -8.0, -6.0, 55, 0.8)
	postac("konduktorka", -2.9, -1.6)
	postac("korfanty", 1.4, -1.9)
	wyjscie("do_warszawy")


func lok_warszawa_lokal() -> void:
	otoczenie["ambient_moc"] = 0.65
	pokoj(190, 115, tex_tapeta(195))
	okno(Vector3(3.8, 2.5, -5.92), 2.0, 2.2, 232)
	# plakat Ligi Kobiet z wagą
	box(Vector3(2.2, 2.8, 0.03), Vector3(-4.2, 2.4, -5.94), 225)
	napis("OBYWATELKI!", Vector3(-4.2, 3.5, -5.9), 50, 30)
	napis("WASZ GŁOS", Vector3(-4.2, 3.1, -5.9), 44, 40)
	napis("MA WAGĘ", Vector3(-4.2, 2.8, -5.9), 44, 40)
	box(Vector3(0.05, 0.9, 0.02), Vector3(-4.2, 2.05, -5.9), 40)
	box(Vector3(1.0, 0.04, 0.02), Vector3(-4.2, 2.45, -5.9), 40)
	for sx in [-0.5, 0.5]:
		box(Vector3(0.35, 0.05, 0.02), Vector3(-4.2 + sx, 2.15, -5.9), 40)
	napis("Liga Kobiet", Vector3(-4.2, 1.35, -5.9), 36, 70, "reka")
	obiekt("plakat", Vector3(-4.2, 2.4, -5.8), Vector3(2.4, 3.0, 0.4))
	# urna
	box(Vector3(0.9, 0.9, 0.9), Vector3(-1.6, 0.45, -3.2), 100, Vector3.ZERO, tex_deski(110))
	box(Vector3(1.0, 0.1, 1.0), Vector3(-1.6, 0.95, -3.2), 130)
	box(Vector3(0.4, 0.02, 0.06), Vector3(-1.6, 1.01, -3.2), 25)
	obiekt("urna", Vector3(-1.6, 0.6, -3.2), Vector3(1.2, 1.3, 1.2))
	stol(Vector3(1.6, 0, -4.2), 3.0, 1.2, 0.9, 80)
	papiery(Vector3(1.6, 0.95, -4.2), 8, 13)
	for i in 3:
		box(Vector3(0.5, 1.0, 0.5), Vector3(0.6 + i * 1.0, 0.5, -5.1), 75)
	box(Vector3(1.3, 1.6, 0.03), Vector3(0.6, 2.8, -5.94), 228)
	napis("28 XI 1918", Vector3(0.6, 3.3, -5.9), 44, 35)
	swiatlo(Vector3(0.5, 3.6, -2.5), 1.2, 9.0)
	postac("moraczewska", 0.6, -2.0)
	postac("damian_final", 3.4, -2.0)
