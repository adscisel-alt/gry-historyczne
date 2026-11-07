extends Node3D
## Roman Dmowski. Droga do Wersalu 3D — logika gry, świat 3D, ekonomia i fabuła.
## Każda kampania (1914–1919) toczy się na osobnej mapie: Warszawa, Lozanna, Francja, Paryż.
## Treść gry: dane/dane.json (źródło: narzedzia/dane.py). Interfejs: skrypty/interfejs.gd.

const T := 2.0
const DZIEN_SEK := 4.0
const UI_SKRYPT := preload("res://skrypty/interfejs.gd")

var D := {}
var D_mapa := {}
var R := {}                    # dane bieżącej kampanii
var stan := {}
var mapa := []
var map_w := 36
var map_h := 24
var zajete := {}
var sceny := {}
var ui
var scena := "tytul"
var nakladka := ""
var dialog = null
var wybrany := ""
var rozbiorka := false
var kompas := false
var zegar_dnia := 0.0
var t := 0.0
var yaw := 0.0
var odl := 20.0
var tryb := ""
var dzwieki := {}
var gracze_dzw := []
var muzyka: AudioStreamPlayer
var muzyka_on := true
var info_budynek := -1
var przeciaganie := false
var ruch_myszy := 0.0
var idzie := false

var teren_wezel: Node3D
var dekor_wezel: Node3D
var budynki_wezel: Node3D
var dzialki_wezel: Node3D
var npc_wezel: Node3D
var woda: MeshInstance3D
var bohater: Node3D
var npc_wezly := {}
var kamera: Camera3D
var duch: Node3D
var duch_typ := ""
var duch_mat_ok: StandardMaterial3D
var duch_mat_zle: StandardMaterial3D
var strzalka: Node3D
var znacznik: Node3D
var mat_dzialka: StandardMaterial3D
var wezly_b := []
var swiat_rozdzial := -1
const SKALA_POSTACI := 1.6
const KINO := Vector3(0, 0, -600)
var slonce: DirectionalLight3D
var srodowisko: Environment
var niebo_mat: ProceduralSkyMaterial
var zycie_wezel: Node3D
var zycie := []
var deszcz: CPUParticles3D
var faza_kroku := 0.0
var kino: Node3D
var kino_nazwa := ""
var kino_i := 0
var kino_ujecia := []
var kino_koniec := Callable()
var minigra = null
var glos: AudioStreamPlayer
var lektor_on := true
var ostatni_glos := ""
var mapa_scen := ""
var mapa_koniec := Callable()


# ===================================================================== start
func _ready() -> void:
	D = JSON.parse_string(FileAccess.get_file_as_string("res://dane/dane.json"))
	D_mapa = JSON.parse_string(FileAccess.get_file_as_string("res://dane/mapa_europy.json"))
	_otoczenie()
	kamera = Camera3D.new()
	kamera.fov = 50
	kamera.far = 500
	add_child(kamera)
	for n in ["budynki_wezel", "dzialki_wezel", "npc_wezel", "dekor_wezel", "zycie_wezel"]:
		var w := Node3D.new()
		add_child(w)
		set(n, w)
	_materialy()
	_wczytaj_dzwieki()
	_postac_bohatera()
	nowy_stan()
	zbuduj_swiat()
	ui = UI_SKRYPT.new()
	ui.g = self
	add_child(ui)
	ui.zbuduj()
	var args := OS.get_cmdline_user_args()
	if "--samotest" in args:
		_test()
		return
	if "--zrzuty" in args:
		tryb = args[args.find("--zrzuty") + 1]
		_zrzuty()
		return
	pokaz_tytul()
	muzyka.play()


func _otoczenie() -> void:
	var env := Environment.new()
	var niebo := Sky.new()
	var sm := ProceduralSkyMaterial.new()
	sm.sky_top_color = Color(0.34, 0.5, 0.78)
	sm.sky_horizon_color = Color(0.84, 0.84, 0.8)
	sm.ground_horizon_color = Color(0.55, 0.6, 0.5)
	sm.ground_bottom_color = Color(0.25, 0.32, 0.22)
	niebo.sky_material = sm
	niebo_mat = sm
	env.background_mode = Environment.BG_SKY
	env.sky = niebo
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.62, 0.68, 0.8)
	env.ambient_light_energy = 0.45
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	srodowisko = env
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sl := DirectionalLight3D.new()
	sl.rotation_degrees = Vector3(-52, -35, 0)
	sl.light_energy = 0.95
	sl.light_color = Color(1.0, 0.96, 0.88)
	sl.shadow_enabled = true
	sl.directional_shadow_max_distance = 90
	add_child(sl)
	slonce = sl


func _materialy() -> void:
	duch_mat_ok = StandardMaterial3D.new()
	duch_mat_ok.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	duch_mat_ok.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	duch_mat_ok.albedo_color = Color(0.35, 1.0, 0.35, 0.5)
	duch_mat_zle = duch_mat_ok.duplicate()
	duch_mat_zle.albedo_color = Color(1.0, 0.3, 0.25, 0.5)
	mat_dzialka = StandardMaterial3D.new()
	mat_dzialka.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat_dzialka.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat_dzialka.albedo_color = Color(1.0, 0.82, 0.25, 0.45)


func _wczytaj_dzwieki() -> void:
	for n in ["klik", "buduj", "gotowe", "moneta", "dobrze", "zle", "strona", "przedmiot", "fanfara", "blad", "rozmowa"]:
		dzwieki[n] = load("res://audio/%s.wav" % n)
	for i in 6:
		var p := AudioStreamPlayer.new()
		add_child(p)
		gracze_dzw.append(p)
	muzyka = AudioStreamPlayer.new()
	muzyka.stream = load("res://audio/muzyka.wav")
	muzyka.volume_db = -9
	muzyka.finished.connect(func(): if muzyka_on: muzyka.play())
	add_child(muzyka)
	glos = AudioStreamPlayer.new()
	add_child(glos)


# ===================================================================== lektor
func lektor(tekst: String) -> void:
	## Odtwarza nagranie lektora (audio/glos/<md5 tekstu>.ogg), jeśli istnieje.
	if tryb != "" or (tekst == ostatni_glos and glos.playing):
		return
	ostatni_glos = tekst
	glos.stop()
	if not lektor_on:
		return
	var sciezka := "res://audio/glos/%s.ogg" % tekst.md5_text()
	if ResourceLoader.exists(sciezka):
		glos.stream = load(sciezka)
		glos.play()


func ucisz_lektora() -> void:
	glos.stop()
	ostatni_glos = ""


func przelacz_lektora() -> void:
	lektor_on = not lektor_on
	if not lektor_on:
		ucisz_lektora()
	ui.toast("Lektor: " + ("włączony" if lektor_on else "wyłączony"))


# ===================================================================== mapa Europy między kampaniami
func pokaz_mape(nazwa: String, na_koniec: Callable) -> void:
	if tryb == "test":
		na_koniec.call()
		return
	mapa_scen = nazwa
	mapa_koniec = na_koniec
	scena = "mapa"
	nakladka = ""
	ui.pokaz_ekran()


func zakoncz_mape() -> void:
	ucisz_lektora()
	var cb := mapa_koniec
	mapa_koniec = Callable()
	if cb.is_valid():
		cb.call()


func dzwiek(n: String) -> void:
	if tryb != "" or not dzwieki.has(n):
		return
	for p in gracze_dzw:
		if not p.playing:
			p.stream = dzwieki[n]
			p.volume_db = -8.0 if n == "moneta" else -3.0
			p.play()
			return


func przelacz_muzyke() -> void:
	muzyka_on = not muzyka_on
	if muzyka_on:
		muzyka.play()
	else:
		muzyka.stop()


# ===================================================================== stan
func nowy_stan() -> void:
	var zas := {}
	for z in D.zasoby:
		zas[z.id] = int(z.start)
	stan = {
		"rozdzial": 1, "zasoby": zas, "ludnosc": 6.0, "pw": 0, "budynki": [], "flagi": [],
		"ekwipunek": D.start_ekwipunek.duplicate(), "karty": D.karty_startowe.duplicate(), "przeczytane": [], "karty_postaci": [],
		"zagadki": [], "dzien": 0, "prowiant": 0, "bohater": [0, 0],
	}
	_ustaw_start()


func _ustaw_start() -> void:
	var r = D.rozdzialy[str(int(stan.rozdzial))]
	stan.bohater = [(r.start[0] + 0.5) * T, (r.start[1] + 0.5) * T]


func zapisz() -> void:
	if tryb != "":
		return
	var f := FileAccess.open("user://zapis.json", FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(stan))


func ma_zapis() -> bool:
	return FileAccess.file_exists("user://zapis.json")


func wczytaj() -> void:
	var d = JSON.parse_string(FileAccess.get_file_as_string("user://zapis.json"))
	if typeof(d) != TYPE_DICTIONARY:
		return
	stan = d
	zbuduj_swiat()
	zacznij_rozdzial()


# ===================================================================== świat kampanii
func zbuduj_swiat() -> void:
	R = D.rozdzialy[str(int(stan.rozdzial))]
	mapa = []
	for wiersz in R.mapa:
		var r := []
		for i in wiersz.length():
			r.append(wiersz[i])
		mapa.append(r)
	map_h = mapa.size()
	map_w = mapa[0].size()
	if swiat_rozdzial != int(stan.rozdzial):
		swiat_rozdzial = int(stan.rozdzial)
		_zbuduj_teren()
		_dekoracje()
		_npc()
		_oswietlenie()
		_zycie_miasta()
	odswiez_swiat()


func teren_w(x: int, y: int) -> String:
	if x >= 0 and y >= 0 and x < map_w and y < map_h:
		return mapa[y][x]
	return ""


func _wyczysc(w: Node) -> void:
	for n in w.get_children():
		w.remove_child(n)
		n.free()


func _zbuduj_teren() -> void:
	if teren_wezel:
		remove_child(teren_wezel)
		teren_wezel.free()
	teren_wezel = Node3D.new()
	add_child(teren_wezel)
	var kolory := {".": Color(0.37, 0.6, 0.29), "T": Color(0.27, 0.48, 0.25), "~": Color(0.2, 0.28, 0.4),
		"#": Color(0.45, 0.42, 0.4), "=": Color(0.5, 0.48, 0.46), "B": Color(0.66, 0.62, 0.56),
		"K": Color(0.5, 0.48, 0.46), "D": Color(0.66, 0.62, 0.56), "^": Color(0.42, 0.44, 0.42),
		"P": Color(0.78, 0.68, 0.34), "X": Color(0.46, 0.37, 0.27)}
	var wys := {".": 0.0, "T": 0.0, "~": -0.5, "#": 0.1, "=": 0.015, "B": 0.03, "K": 0.03, "D": 0.03,
		"^": 0.0, "P": 0.0, "X": -0.03}
	if int(stan.rozdzial) == 3:
		kolory["="] = Color(0.66, 0.55, 0.38)
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	var pud := BoxMesh.new()
	pud.size = Vector3(T, 0.5, T)
	var m := StandardMaterial3D.new()
	m.vertex_color_use_as_albedo = true
	m.roughness = 0.95
	pud.material = m
	mm.mesh = pud
	mm.instance_count = map_w * map_h
	var rng := RandomNumberGenerator.new()
	rng.seed = 1918 + int(stan.rozdzial)
	for y in map_h:
		for x in map_w:
			var c: String = mapa[y][x]
			var i := y * map_w + x
			mm.set_instance_transform(i, Transform3D(Basis(), Vector3((x + 0.5) * T, wys.get(c, 0.0) - 0.25, (y + 0.5) * T)))
			var k: Color = kolory.get(c, kolory["."])
			var v := rng.randf_range(-0.03, 0.03)
			if c in ["B", "D"] and (x + y) % 2 == 0:
				v -= 0.04
			mm.set_instance_color(i, Color(k.r + v, k.g + v * 1.2, k.b + v))
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	teren_wezel.add_child(mmi)
	woda = MeshInstance3D.new()
	var pl := PlaneMesh.new()
	pl.size = Vector2(map_w * T, map_h * T)
	pl.subdivide_width = map_w
	pl.subdivide_depth = map_h
	woda.mesh = pl
	var sh := Shader.new()
	sh.code = """shader_type spatial;
render_mode cull_disabled;
void vertex() { VERTEX.y += sin(TIME * 1.6 + VERTEX.z * 0.9 + VERTEX.x) * 0.04; }
void fragment() {
	float f = sin(TIME * 2.0 + UV.y * 90.0 + UV.x * 40.0) * 0.5 + 0.5;
	ALBEDO = mix(vec3(0.10, 0.28, 0.55), vec3(0.32, 0.55, 0.85), f * 0.45);
	ROUGHNESS = 0.12; METALLIC = 0.15; SPECULAR = 0.7;
}"""
	var smat := ShaderMaterial.new()
	smat.shader = sh
	woda.material_override = smat
	woda.position = Vector3(map_w * T / 2, -0.15, map_h * T / 2)
	teren_wezel.add_child(woda)


func _dekoracje() -> void:
	_wyczysc(dekor_wezel)
	var rng := RandomNumberGenerator.new()
	rng.seed = 1919 + int(stan.rozdzial)
	var styl: String = R.styl
	var warianty := 3 if styl == "kamienica_wwa" else 2
	for y in map_h:
		for x in map_w:
			var c: String = mapa[y][x]
			var p := Vector3((x + 0.5) * T, 0, (y + 0.5) * T)
			var d: Node3D = null
			if c == "T":
				d = instancja("drzewo_%d" % rng.randi_range(0, 2))
				d.position = p + Vector3(rng.randf_range(-0.4, 0.4), 0, rng.randf_range(-0.4, 0.4))
				d.rotation.y = rng.randf() * TAU
				d.scale = Vector3.ONE * rng.randf_range(1.3, 1.8)
			elif c == "K":
				d = instancja("%s_%d" % [styl, rng.randi_range(0, warianty - 1)])
				d.position = p
				d.rotation.y = _obrot_do_ulicy(x, y)
				d.scale = Vector3(1, rng.randf_range(0.85, 1.25), 1)
			elif c == "^" and (x + y * 3) % 4 == 0:
				d = instancja("gora")
				d.position = p
				d.scale = Vector3.ONE * rng.randf_range(1.0, 1.7)
			elif c == "X" and rng.randf() < 0.18:
				d = instancja("lej")
				d.position = p
				d.rotation.y = rng.randf() * TAU
			elif c == "P" and rng.randf() < 0.12:
				d = instancja("snopek")
				d.position = p + Vector3(rng.randf_range(-0.5, 0.5), 0, rng.randf_range(-0.5, 0.5))
			elif c == "=" and int(stan.rozdzial) != 3 and (x * 7 + y * 3) % 11 == 0:
				d = instancja("latarnia")
				d.position = p + Vector3(0.8, 0, 0.8)
			if d:
				dekor_wezel.add_child(d)
	for dk in R.dekor:
		var m := instancja(dk[0])
		m.position = Vector3(dk[1] * T, 0, dk[2] * T)
		m.rotation.y = dk[3]
		m.scale = Vector3.ONE * dk[4]
		dekor_wezel.add_child(m)
		var nazwy := {"zamek": "Zamek Królewski", "kolumna": "Kolumna Zygmunta", "katedra": "Katedra w Lozannie",
			"wieza_eiffla": "Wieża Eiffla", "quai_dorsay": "Quai d'Orsay — Rada Dziesięciu", "wersal": "Pałac w Wersalu"}
		if nazwy.has(dk[0]):
			var l := etykieta(nazwy[dk[0]], 44, Color(1, 0.95, 0.8))
			l.position = m.position + Vector3(0, {"wieza_eiffla": 19.0, "zamek": 10.0, "kolumna": 9.5, "katedra": 11.5, "quai_dorsay": 8.5}.get(dk[0], 7.0), 0)
			dekor_wezel.add_child(l)
	var ziemia := MeshInstance3D.new()
	var pl := PlaneMesh.new()
	pl.size = Vector2(400, 400)
	ziemia.mesh = pl
	var mz := StandardMaterial3D.new()
	mz.albedo_color = Color(0.3, 0.5, 0.25) if int(stan.rozdzial) != 2 else Color(0.2, 0.32, 0.5)
	ziemia.material_override = mz
	ziemia.position = Vector3(map_w * T / 2, -0.4, map_h * T / 2)
	dekor_wezel.add_child(ziemia)
	for i in 120:
		var a := rng.randf() * TAU
		var r := rng.randf_range(48, 85)
		var pp := Vector3(map_w * T / 2 + cos(a) * r * 1.2, -0.3, map_h * T / 2 + sin(a) * r)
		if pp.x > -2 and pp.x < map_w * T + 2 and pp.z > -2 and pp.z < map_h * T + 2:
			continue
		var dd := instancja("gora" if int(stan.rozdzial) == 2 and sin(a) > 0.3 else "drzewo_%d" % rng.randi_range(0, 2))
		dd.position = pp
		dd.scale = Vector3.ONE * rng.randf_range(1.6, 2.4)
		dekor_wezel.add_child(dd)


func _obrot_do_ulicy(x: int, y: int) -> float:
	for kier in [[0, 1, 0.0], [1, 0, PI / 2], [-1, 0, -PI / 2], [0, -1, PI]]:
		var c := teren_w(x + kier[0], y + kier[1])
		if c in ["=", "B", "."]:
			return kier[2]
	return 0.0


func instancja(nazwa: String) -> Node3D:
	if not sceny.has(nazwa):
		sceny[nazwa] = load("res://modele/%s.glb" % nazwa)
	return sceny[nazwa].instantiate()


func etykieta(tekst: String, rozmiar := 48, kolor := Color.WHITE) -> Label3D:
	var l := Label3D.new()
	l.text = tekst
	l.font_size = rozmiar
	l.pixel_size = 0.01
	l.modulate = kolor
	l.outline_size = 12
	l.outline_modulate = Color(0.1, 0.06, 0.04)
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.no_depth_test = true
	return l


# ===================================================================== postacie
func _postac_bohatera() -> void:
	bohater = Node3D.new()
	var m := instancja("postac_dmowski")
	m.name = "model"
	m.scale = Vector3.ONE * SKALA_POSTACI
	bohater.add_child(m)
	add_child(bohater)
	strzalka = instancja("strzalka")
	strzalka.scale = Vector3.ONE * 1.6
	add_child(strzalka)
	znacznik = instancja("znacznik")
	znacznik.scale = Vector3.ONE * 1.4
	add_child(znacznik)


func _npc() -> void:
	_wyczysc(npc_wezel)
	npc_wezly = {}
	for k in R.npc:
		var n := Node3D.new()
		var mm := instancja("postac_" + k)
		mm.name = "model"
		mm.scale = Vector3.ONE * SKALA_POSTACI
		n.add_child(mm)
		var poz = R.npc[k]
		n.position = Vector3((poz[0] + 0.5) * T, 0, (poz[1] + 0.5) * T)
		var imie := etykieta(D.postacie[k].imie, 46, Color(1, 0.95, 0.8))
		imie.position.y = 3.35
		n.add_child(imie)
		var wyk := etykieta("!", 120, Color(1, 0.82, 0.2))
		wyk.name = "wykrzyknik"
		wyk.position.y = 4.2
		n.add_child(wyk)
		var e := etykieta("[E] rozmowa", 40, Color(1, 1, 1))
		e.name = "podpowiedz"
		e.position.y = 2.95
		n.add_child(e)
		npc_wezel.add_child(n)
		npc_wezly[k] = n


# ===================================================================== budynki
func bud(typ: String) -> Dictionary:
	return D.budynki[typ]


func gotowy_b(b: Dictionary) -> bool:
	return b.postep >= bud(b.typ).czas


func ile_gotowych(typ: String) -> int:
	var n := 0
	for b in stan.budynki:
		if b.typ == typ and gotowy_b(b):
			n += 1
	return n


func dzialki_typu(typ: String) -> Array:
	var w := []
	for dz in R.dzialki:
		if dz[0] == typ:
			w.append(Vector2i(dz[1], dz[2]))
	return w


func obrot_dzialki(typ: String, x: int, y: int) -> float:
	for dz in R.dzialki:
		if dz[0] == typ and int(dz[1]) == x and int(dz[2]) == y:
			return dz[3]
	return 0.0


func dzialka_zajeta(typ: String, x: int, y: int) -> bool:
	for b in stan.budynki:
		if b.typ == typ and int(b.x) == x and int(b.y) == y:
			return true
	return false


func zarezerwowane() -> Dictionary:
	var rez := {}
	for dz in R.dzialki:
		if dzialka_zajeta(dz[0], dz[1], dz[2]):
			continue
		var d := bud(dz[0])
		for yy in range(dz[2], dz[2] + int(d.h)):
			for xx in range(dz[1], dz[1] + int(d.w)):
				rez[Vector2i(xx, yy)] = true
	return rez


func przelicz_zajete() -> void:
	zajete = {}
	for i in stan.budynki.size():
		var b = stan.budynki[i]
		var d := bud(b.typ)
		for y in range(int(b.y), int(b.y) + int(d.h)):
			for x in range(int(b.x), int(b.x) + int(d.w)):
				zajete[Vector2i(x, y)] = i


func efekt(rodzaj: String, zasob := "") -> float:
	## Łączny efekt przedmiotów z ekwipunku: mnożnik zasobu, mnożnik kosztu lub PW dziennie.
	var w := 0.0 if rodzaj == "pw_dziennie" else 1.0
	for p in stan.ekwipunek:
		var e = D.przedmioty[p].get("efekt")
		if e == null:
			continue
		if rodzaj == "mnoznik" and e.get("mnoznik", "") == zasob:
			w *= e.x
		elif rodzaj == "koszt" and e.has("koszt"):
			w *= e.koszt
		elif rodzaj == "pw_dziennie" and e.has("pw_dziennie"):
			w += e.pw_dziennie
	return w


func koszt(typ: String) -> Dictionary:
	var k := {}
	var mn := efekt("koszt") if typ.begins_with("sprawa_") else 1.0
	for a in bud(typ).koszt:
		k[a] = int(ceil(float(bud(typ).koszt[a]) * mn))
	return k


func stac(typ: String) -> bool:
	var k := koszt(typ)
	for a in k:
		if stan.zasoby.get(a, 0) < k[a]:
			return false
	return true


func moze_budowac(typ: String, tx: int, ty: int) -> Array:
	var d := bud(typ)
	if d.get("min_pw", 0) > stan.pw:
		return [false, "Potrzeba %d Punktów Wiedzy!" % d.min_pw]
	if d.get("zabytek", false):
		if not Vector2i(tx, ty) in dzialki_typu(typ):
			return [false, "To miejsce jest gdzie indziej — użyj kompasu (K)!"]
		if dzialka_zajeta(typ, tx, ty):
			return [false, "Ta działka jest już zajęta."]
		for y in range(ty, ty + int(d.h)):
			for x in range(tx, tx + int(d.w)):
				if zajete.has(Vector2i(x, y)):
					return [false, "Coś stoi na działce — rozbierz to."]
		if not stac(typ):
			return [false, "Brakuje zasobów."]
		return [true, ""]
	var rez := zarezerwowane()
	var sasiedzi := {}
	for y in range(ty, ty + int(d.h)):
		for x in range(tx, tx + int(d.w)):
			var c := teren_w(x, y)
			if c == "":
				return [false, "Poza mapą."]
			if zajete.has(Vector2i(x, y)):
				return [false, "Tu już coś stoi."]
			if rez.has(Vector2i(x, y)):
				return [false, "To działka zarezerwowana — zostaw ją."]
			if not c in [".", "P"]:
				return [false, "Tu nie można budować (ulica, woda, drzewa lub zabudowa)."]
			for dy in [-1, 0, 1]:
				for dx in [-1, 0, 1]:
					sasiedzi[teren_w(x + dx, y + dy)] = true
	if d.get("wymog", "") == "ulica" and not sasiedzi.has("=") and not sasiedzi.has("B"):
		return [false, "Redakcja musi stać przy ulicy lub placu."]
	if not stac(typ):
		return [false, "Brakuje zasobów."]
	return [true, ""]


func postaw(typ: String, tx: int, ty: int) -> void:
	var k := koszt(typ)
	for a in k:
		stan.zasoby[a] -= k[a]
	stan.budynki.append({"typ": typ, "x": tx, "y": ty, "postep": 0, "wariant": randi() % 3})
	odswiez_swiat()
	dzwiek("buduj")
	var d := bud(typ)
	pyl(Vector3((tx + d.w / 2.0) * T, 0.5, (ty + d.h / 2.0) * T), Color(0.78, 0.68, 0.5))


func rozbierz(i: int) -> void:
	var b = stan.budynki[i]
	if bud(b.typ).get("zabytek", false):
		ui.toast("Tej placówki nie można rozebrać!")
		dzwiek("blad")
		return
	for a in bud(b.typ).koszt:
		stan.zasoby[a] += int(bud(b.typ).koszt[a]) / 2
	stan.budynki.remove_at(i)
	info_budynek = -1
	odswiez_swiat()
	dzwiek("buduj")
	ui.toast("Rozebrano — odzyskano połowę zasobów.")


func odswiez_swiat() -> void:
	przelicz_zajete()
	_wyczysc(budynki_wezel)
	wezly_b = []
	for i in stan.budynki.size():
		wezly_b.append(_wezel_budynku(stan.budynki[i]))
	_odswiez_dzialki()


func _model_budynku(typ: String) -> String:
	return D.model_sprawy if typ.begins_with("sprawa_") else typ


func _wezel_budynku(b: Dictionary) -> Node3D:
	var d := bud(b.typ)
	var w := int(d.w)
	var h := int(d.h)
	var n := Node3D.new()
	budynki_wezel.add_child(n)
	n.position = Vector3((b.x + w / 2.0) * T, 0, (b.y + h / 2.0) * T)
	var model := instancja(_model_budynku(b.typ))
	model.rotation.y = obrot_dzialki(b.typ, int(b.x), int(b.y))
	model.name = "model"
	n.add_child(model)
	if b.typ.begins_with("sprawa_"):
		var l := etykieta(d.nazwa, 40, Color(1, 0.92, 0.6))
		l.position.y = 3.2
		n.add_child(l)
	if not gotowy_b(b):
		var r := instancja("rusztowanie")
		r.name = "rusztowanie"
		r.scale = Vector3(w, 1.3, h)
		n.add_child(r)
	_aktualizuj_wezel(n, b)
	return n


func _aktualizuj_wezel(n: Node3D, b: Dictionary) -> void:
	var model: Node3D = n.get_node("model")
	if gotowy_b(b):
		model.scale = Vector3.ONE
		if n.has_node("rusztowanie"):
			n.get_node("rusztowanie").queue_free()
	else:
		model.scale = Vector3(1, max(0.06, float(b.postep) / float(bud(b.typ).czas)), 1)


func _odswiez_dzialki() -> void:
	_wyczysc(dzialki_wezel)
	if not kompas:
		return
	for dz in R.dzialki:
		var typ: String = dz[0]
		if dzialka_zajeta(typ, dz[1], dz[2]):
			continue
		var d := bud(typ)
		var mi := MeshInstance3D.new()
		var bm := BoxMesh.new()
		bm.size = Vector3(d.w * T - 0.2, 0.12, d.h * T - 0.2)
		mi.mesh = bm
		mi.material_override = mat_dzialka
		mi.position = Vector3((dz[1] + d.w / 2.0) * T, 0.08, (dz[2] + d.h / 2.0) * T)
		dzialki_wezel.add_child(mi)
		var l := etykieta(d.nazwa, 40, Color(1, 0.9, 0.5))
		l.position = mi.position + Vector3(0, 1.4, 0)
		dzialki_wezel.add_child(l)


# ===================================================================== ekonomia
func pojemnosc() -> int:
	var p := 8
	for b in stan.budynki:
		if gotowy_b(b):
			p += int(bud(b.typ).get("mieszk", 0))
	return p


func potrzebni() -> int:
	var p := 0
	for b in stan.budynki:
		if gotowy_b(b):
			p += int(bud(b.typ).get("rob", 0))
	return p


func wydajnosc() -> float:
	var p := potrzebni()
	return 1.0 if p == 0 else min(1.0, stan.ludnosc / p)


func nowy_dzien() -> void:
	stan.dzien += 1
	var wyd := wydajnosc() * (2.0 if stan.prowiant > 0 else 1.0)
	if stan.prowiant > 0:
		stan.prowiant -= 1
	var zmiana := false
	for i in stan.budynki.size():
		var b = stan.budynki[i]
		var d := bud(b.typ)
		if not gotowy_b(b):
			b.postep += 1
			if i < wezly_b.size():
				_aktualizuj_wezel(wezly_b[i], b)
			if gotowy_b(b):
				_ukonczono(b)
				zmiana = true
			continue
		var prod = d.get("prod", {})
		for zas in prod:
			var ile := int(round(prod[zas] * wyd * efekt("mnoznik", zas)))
			stan.zasoby[zas] += ile
			if ile > 0 and i < wezly_b.size():
				napis(wezly_b[i].position + Vector3(0, 4, 0), "+%d %s" % [ile, D.zasoby_nazwy[zas]], Color(1, 0.97, 0.8))
	var skladki := int(stan.ludnosc * 0.5 * efekt("mnoznik", "fundusze"))
	stan.zasoby.fundusze += skladki
	stan.pw += int(efekt("pw_dziennie"))
	var cap := pojemnosc()
	stan.ludnosc = min(cap, stan.ludnosc + 2) if stan.ludnosc < cap else float(cap)
	if skladki > 0:
		dzwiek("moneta")
	if zmiana:
		odswiez_swiat()


func _ukonczono(b: Dictionary) -> void:
	var d := bud(b.typ)
	dzwiek("gotowe")
	var poz := Vector3((b.x + d.w / 2.0) * T, 1.0, (b.y + d.h / 2.0) * T)
	pyl(poz, Color(1, 0.92, 0.6))
	ui.toast("Gotowe: %s!" % d.nazwa)
	if d.get("zabytek", false):
		stan.pw += 5
		napis(poz + Vector3(0, 4, 0), "+5 PW", Color(1, 0.8, 0.25))
	var karta = D.karta_budynku.get(b.typ, "")
	if karta != "":
		odkryj(karta)


func odkryj(karta: String) -> void:
	if not karta in stan.karty:
		stan.karty.append(karta)
		ui.toast("Nowa karta w Księdze Wiedzy: %s (L)" % D.wiedza[karta][0])
		dzwiek("strona")


func daj_przedmiot(p: String) -> void:
	stan.ekwipunek.append(p)
	ui.toast("Nowy przedmiot: %s (I)" % D.przedmioty[p].nazwa)
	dzwiek("przedmiot")


func napis(poz: Vector3, tekst: String, kolor: Color) -> void:
	if tryb == "test":
		return
	var l := etykieta(tekst, 44, kolor)
	l.position = poz
	add_child(l)
	var tw := l.create_tween()
	tw.set_parallel()
	tw.tween_property(l, "position", poz + Vector3(0, 2, 0), 1.6)
	tw.tween_property(l, "modulate:a", 0.0, 1.6)
	tw.chain().tween_callback(l.queue_free)


func pyl(poz: Vector3, kolor: Color) -> void:
	if tryb == "test":
		return
	var p := CPUParticles3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(0.18, 0.18, 0.18)
	var m := StandardMaterial3D.new()
	m.albedo_color = kolor
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	bm.material = m
	p.mesh = bm
	p.one_shot = true
	p.amount = 28
	p.lifetime = 1.0
	p.explosiveness = 0.9
	p.direction = Vector3.UP
	p.spread = 70
	p.initial_velocity_min = 3
	p.initial_velocity_max = 6
	p.position = poz
	add_child(p)
	p.emitting = true
	get_tree().create_timer(2.0).timeout.connect(p.queue_free)


# ===================================================================== cele
func cele() -> Array:
	return R.cele


func stan_celu(c: Array) -> Array:
	var typ: String = c[1]
	var par = c[2]
	var ile := int(c[3])
	match typ:
		"rozmowa":
			return [1 if ("rozm_%s_%d" % [par, ile]) in stan.flagi else 0, 1]
		"buduj":
			return [min(ile, ile_gotowych(par)), ile]
		"wiedza":
			return [min(ile, int(stan.pw)), ile]
		"zasob":
			return [min(ile, int(stan.zasoby.get(par, 0))), ile]
	return [0, 1]


func rozdzial_ukonczony() -> bool:
	for c in cele():
		var s := stan_celu(c)
		if s[0] < s[1]:
			return false
	return true


func cel_kompasu() -> Array:
	var hp := Vector2(stan.bohater[0], stan.bohater[1])
	for c in cele():
		var s := stan_celu(c)
		if s[0] >= s[1]:
			continue
		var typ: String = c[1]
		var par = c[2]
		if typ == "rozmowa":
			var p = R.npc[par]
			return [Vector3((p[0] + 0.5) * T, 0, (p[1] + 0.5) * T), D.postacie[par].imie]
		if typ == "buduj" and bud(par).get("zabytek", false):
			var najl = null
			var dmin := INF
			for v in dzialki_typu(par):
				if dzialka_zajeta(par, v.x, v.y):
					continue
				var dd := hp.distance_to(Vector2(v) * T)
				if dd < dmin:
					dmin = dd
					najl = v
			if najl == null:
				continue
			var d := bud(par)
			return [Vector3((najl.x + d.w / 2.0) * T, 0, (najl.y + d.h / 2.0) * T), d.nazwa]
		if typ == "buduj":
			return [null, "%s — postaw na wolnej trawie" % bud(par).nazwa]
		if typ == "wiedza":
			return [null, "Czytaj Księgę (L) i rozwiązuj zagadki"]
		if typ == "zasob":
			return [null, "Zbieraj: %s — buduj placówki" % D.zasoby_nazwy[par]]
	return [null, "Wszystkie cele wykonane!"]


func kierunek_slownie(dx: float, dz: float) -> String:
	var kat := fposmod(rad_to_deg(atan2(-dz, dx)), 360.0)
	var nazwy := ["na wschód", "na północny wschód", "na północ", "na północny zachód",
		"na zachód", "na południowy zachód", "na południe", "na południowy wschód"]
	return nazwy[int((kat + 22.5) / 45.0) % 8]


func kroki_slownie(n: int) -> String:
	if n == 1:
		return "1 krok"
	if n % 10 in [2, 3, 4] and not n % 100 in [12, 13, 14]:
		return "%d kroki" % n
	return "%d kroków" % n


func ranga() -> String:
	var w := ""
	for r in D.rangi:
		if stan.pw >= r[0]:
			w = r[1]
	return w


# ===================================================================== rozmowy
func npc_obok() -> String:
	var hp := Vector2(stan.bohater[0], stan.bohater[1])
	for k in npc_wezly:
		var p: Vector3 = npc_wezly[k].position
		if hp.distance_to(Vector2(p.x, p.z)) < 3.2:
			return k
	return ""


func rozmawiaj(npc: String) -> void:
	var rozd := int(stan.rozdzial)
	var flaga := "rozm_%s_%d" % [npc, rozd]
	var klucz := "%s:%d" % [npc, rozd]
	dzwiek("rozmowa")
	if D.rozmowy.has(klucz) and not flaga in stan.flagi:
		var r = D.rozmowy[klucz]
		var q = D.quiz_glowny.get(klucz)
		var koniec := func():
			stan.flagi.append(flaga)
			daj_przedmiot(r.nagroda)
			for k in r.karty:
				odkryj(k)
		if r.has("minigra"):
			var po_minigrze := func():
				koniec.call()
				pokaz_przerywnik(r.minigra, Callable())
			otworz_dialog(r.kwestie, null, func(): rozpocznij_przemowienie(po_minigrze))
			return
		otworz_dialog(r.kwestie, q, koniec, func(pierwsza): pw_za_zagadke(pierwsza, 5))
		return
	var pula = D.zagadki.get(npc, [])
	for i in pula.size():
		var id := "%s:%d" % [npc, i]
		if not id in stan.zagadki:
			var dobrze := func(pierwsza):
				stan.zagadki.append(id)
				pw_za_zagadke(pierwsza, 3)
			otworz_dialog([[npc, "Mam dla pana zagadkę! Za dobrą odpowiedź dostanie pan Punkty Wiedzy."]], pula[i],
				Callable(), dobrze)
			return
	var kw: Array = D.luzne[npc].duplicate()
	if D.rozmowy.has(klucz):
		kw += D.rozmowy[klucz].po
	otworz_dialog(kw)


func pw_za_zagadke(pierwsza: bool, ile: int) -> void:
	var zysk := ile if pierwsza else max(1, ile / 2)
	stan.pw += zysk
	napis(bohater.position + Vector3(0, 3.2, 0), "+%d PW" % zysk, Color(1, 0.8, 0.25))


func otworz_dialog(kwestie: Array, zagadka = null, na_koniec := Callable(), na_dobrze := Callable()) -> void:
	var odp := []
	if zagadka != null:
		odp = [zagadka.poprawna] + zagadka.zle
		odp.shuffle()
	dialog = {"kwestie": kwestie, "i": 0, "znaki": 0.0, "zagadka": zagadka, "odp": odp, "zle": [],
		"proby": 0, "tryb": "tekst", "na_koniec": na_koniec, "na_dobrze": na_dobrze}
	nakladka = "dialog"
	ui.odswiez_dialog()


func dalej_dialog() -> void:
	if dialog == null:
		return
	if dialog.tryb == "tekst":
		var tekst: String = dialog.kwestie[dialog.i][1] if dialog.i < dialog.kwestie.size() else ""
		if dialog.znaki < tekst.length():
			dialog.znaki = tekst.length()
			return
		dialog.i += 1
		dialog.znaki = 0.0
		if dialog.i >= dialog.kwestie.size():
			if dialog.zagadka != null:
				dialog.tryb = "zagadka"
			else:
				zamknij_dialog()
				return
		ui.odswiez_dialog()
	elif dialog.tryb == "wynik":
		zamknij_dialog()


func odpowiedz(idx: int) -> void:
	if dialog == null or dialog.tryb != "zagadka" or idx in dialog.zle:
		return
	if dialog.odp[idx] == dialog.zagadka.poprawna:
		dzwiek("dobrze")
		dialog.tryb = "wynik"
		if dialog.na_dobrze.is_valid():
			dialog.na_dobrze.call(dialog.proby == 0)
	else:
		dzwiek("zle")
		dialog.zle.append(idx)
		dialog.proby += 1
	ui.odswiez_dialog()


func zamknij_dialog() -> void:
	ucisz_lektora()
	var dl = dialog
	dialog = null
	nakladka = ""
	ui.odswiez_dialog()
	if dl != null and dl.na_koniec.is_valid():
		dl.na_koniec.call()


# ===================================================================== sceny
func pokaz_tytul() -> void:
	scena = "tytul"
	nakladka = ""
	ui.pokaz_ekran()


func nowa_gra() -> void:
	nowy_stan()
	zbuduj_swiat()
	scena = "wstep"
	ui.pokaz_ekran()
	pokaz_przerywnik("wstep", func(): pokaz_mape("start", zacznij_rozdzial))


func powtorz_wstep() -> void:
	scena = "wstep"
	ui.pokaz_ekran()
	pokaz_przerywnik("wstep", pokaz_tytul)


func karta_odblokowana(id: String) -> bool:
	var o: Array = D.karty_postaci[id].odblokuj
	match o[0]:
		"start":
			return true
		"flaga":
			return o[1] in stan.flagi
		"kampania":
			return int(stan.rozdzial) >= int(o[1]) or scena == "koniec"
	return false


func czytaj_karte_postaci(id: String) -> void:
	lektor(D.karty_postaci[id].lektor)
	if not stan.has("karty_postaci"):
		stan["karty_postaci"] = []
	if not id in stan.karty_postaci:
		stan.karty_postaci.append(id)
		stan.pw += 2
		ui.toast("+2 PW za poznanie postaci: %s" % D.karty_postaci[id].imie)


func zacznij_rozdzial() -> void:
	scena = "intro"
	nakladka = ""
	wybrany = ""
	rozbiorka = false
	_ustaw_ducha()
	_odswiez_dzialki()
	zapisz()
	ui.pokaz_ekran()


func wejdz_do_gry() -> void:
	scena = "gra"
	zegar_dnia = 0.0
	ui.pokaz_ekran()
	if int(stan.rozdzial) == 1 and not "powitanie" in stan.flagi:
		stan.flagi.append("powitanie")
		otworz_dialog(D.powitanie)


func zakoncz_rozdzial() -> void:
	dzwiek("fanfara")
	var dalej := func():
		daj_przedmiot(R.nagroda)
		for k in R.karty:
			odkryj(k)
		if int(stan.rozdzial) >= int(D.liczba_rozdzialow):
			pokaz_mape("koniec", func():
				scena = "koniec"
				zapisz()
				ui.pokaz_ekran())
		else:
			stan.rozdzial = int(stan.rozdzial) + 1
			stan.budynki = []
			stan.zasoby.fundusze += 60
			stan.ludnosc = 6.0
			_ustaw_start()
			zbuduj_swiat()
			pokaz_mape(str(int(stan.rozdzial)), zacznij_rozdzial)
	if R.has("przerywnik"):
		pokaz_przerywnik(R.przerywnik, func(): otworz_dialog(R.koniec, null, dalej))
	else:
		otworz_dialog(R.koniec, null, dalej)


func uzyj_przedmiotu(p: String) -> void:
	var u = D.przedmioty[p].uzycie
	if u == "kompas":
		kompas = not kompas
		_odswiez_dzialki()
		nakladka = ""
		ui.odswiez_okno()
		dzwiek("klik")
	elif u == "plan":
		ui.pokaz_okno("plan")
		dzwiek("strona")
	elif u == "zuzyj":
		stan.ekwipunek.erase(p)
		if p == "datki":
			stan.zasoby.fundusze += 60
			ui.toast("+60 funduszy!")
			dzwiek("moneta")
		elif p == "paczka":
			stan.prowiant += 6
			ui.toast("Przez 6 dni placówki pracują podwójnie!")
			dzwiek("przedmiot")
		ui.pokaz_okno("ekwipunek")


func wybierz_budynek(typ: String) -> void:
	wybrany = "" if wybrany == typ else typ
	rozbiorka = false
	info_budynek = -1
	_ustaw_ducha()
	dzwiek("klik")


func przelacz_rozbiorke() -> void:
	rozbiorka = not rozbiorka
	wybrany = ""
	_ustaw_ducha()
	dzwiek("klik")


# ===================================================================== duch budowy
func _ustaw_ducha() -> void:
	if duch_typ == wybrany and duch != null:
		return
	if duch:
		duch.queue_free()
		duch = null
	duch_typ = wybrany
	if wybrany == "":
		return
	duch = Node3D.new()
	var d := bud(wybrany)
	var m := instancja(_model_budynku(wybrany))
	m.name = "model"
	duch.add_child(m)
	var pole := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(d.w * T, 0.1, d.h * T)
	pole.mesh = bm
	pole.position.y = 0.06
	duch.add_child(pole)
	add_child(duch)


func _material_ducha(n: Node, m: Material) -> void:
	if n is MeshInstance3D:
		n.material_override = m
	for c in n.get_children():
		_material_ducha(c, m)


func pole_pod_mysza():
	var mp := get_viewport().get_mouse_position()
	var o := kamera.project_ray_origin(mp)
	var kier := kamera.project_ray_normal(mp)
	if abs(kier.y) < 0.001:
		return null
	var s := -o.y / kier.y
	if s < 0:
		return null
	var p := o + kier * s
	return Vector2i(floori(p.x / T), floori(p.z / T))


func pozycja_ducha():
	var k = pole_pod_mysza()
	if k == null or wybrany == "":
		return null
	var d := bud(wybrany)
	if d.get("zabytek", false):
		for v in dzialki_typu(wybrany):
			if k.x >= v.x - 1 and k.x <= v.x + int(d.w) and k.y >= v.y - 1 and k.y <= v.y + int(d.h):
				return v
	return Vector2i(k.x - (int(d.w) - 1) / 2, k.y - (int(d.h) - 1) / 2)


# ===================================================================== wejście
func _unhandled_input(e: InputEvent) -> void:
	if e is InputEventKey and e.pressed and not e.echo:
		_klawisz(e.keycode)
	elif e is InputEventMouseButton:
		if scena != "gra" or nakladka != "":
			return
		if e.button_index == MOUSE_BUTTON_WHEEL_UP and e.pressed:
			odl = clampf(odl - 1.5, 8, 42)
		elif e.button_index == MOUSE_BUTTON_WHEEL_DOWN and e.pressed:
			odl = clampf(odl + 1.5, 8, 42)
		elif e.button_index == MOUSE_BUTTON_RIGHT:
			if e.pressed:
				przeciaganie = true
				ruch_myszy = 0.0
			else:
				przeciaganie = false
				if ruch_myszy < 6:
					wybrany = ""
					rozbiorka = false
					_ustaw_ducha()
		elif e.button_index == MOUSE_BUTTON_LEFT and e.pressed:
			_klik_swiat()
	elif e is InputEventMouseMotion and przeciaganie:
		yaw -= e.relative.x * 0.008
		ruch_myszy += e.relative.length()


func _klawisz(k: int) -> void:
	if k == KEY_F11:
		var tryb_okna := DisplayServer.window_get_mode()
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if tryb_okna == DisplayServer.WINDOW_MODE_FULLSCREEN else DisplayServer.WINDOW_MODE_FULLSCREEN)
		return
	if k == KEY_M:
		przelacz_muzyke()
		return
	if k == KEY_G:
		przelacz_lektora()
		return
	if scena == "mapa":
		if k in [KEY_SPACE, KEY_ENTER, KEY_E]:
			ui.dalej_mapy()
		elif k == KEY_ESCAPE:
			zakoncz_mape()
		return
	if scena == "tytul":
		if k == KEY_ENTER:
			nowa_gra()
		return
	if scena == "intro":
		if k in [KEY_SPACE, KEY_ENTER, KEY_E]:
			ui.klik_intro()
		return
	if scena != "gra":
		return
	if nakladka == "kino":
		if k in [KEY_SPACE, KEY_ENTER, KEY_E]:
			dalej_kino()
		elif k == KEY_ESCAPE:
			zakoncz_kino()
		return
	if nakladka == "przemowienie":
		if k in [KEY_1, KEY_2, KEY_3]:
			wybierz_argument(k - KEY_1)
		elif k in [KEY_SPACE, KEY_ENTER]:
			dalej_przemowienie()
		return
	if nakladka == "dialog":
		if k in [KEY_SPACE, KEY_ENTER, KEY_E]:
			dalej_dialog()
		elif dialog != null and dialog.tryb == "zagadka" and k in [KEY_1, KEY_2, KEY_3]:
			odpowiedz(k - KEY_1)
		return
	if k == KEY_ESCAPE:
		if nakladka != "":
			ui.zamknij_okno()
		elif wybrany != "" or rozbiorka:
			wybrany = ""
			rozbiorka = false
			_ustaw_ducha()
		else:
			ui.pokaz_okno("menu")
		return
	match k:
		KEY_I:
			ui.przelacz_okno("ekwipunek")
		KEY_L:
			ui.przelacz_okno("ksiega")
		KEY_H:
			ui.przelacz_okno("pomoc")
		KEY_K:
			if nakladka == "":
				uzyj_przedmiotu("kompas")
		KEY_E, KEY_SPACE, KEY_ENTER:
			if nakladka == "":
				var n := npc_obok()
				if n != "":
					rozmawiaj(n)


func _klik_swiat() -> void:
	if wybrany != "":
		var p = pozycja_ducha()
		if p != null:
			var w := moze_budowac(wybrany, p.x, p.y)
			if w[0]:
				postaw(wybrany, p.x, p.y)
				if bud(wybrany).get("zabytek", false) or not stac(wybrany):
					wybrany = ""
					_ustaw_ducha()
			else:
				ui.toast(w[1])
				dzwiek("blad")
		return
	var k = pole_pod_mysza()
	if k == null:
		return
	if rozbiorka:
		if zajete.has(k):
			rozbierz(zajete[k])
		return
	var n := npc_obok()
	if n != "":
		var np: Vector3 = npc_wezly[n].position
		if Vector2(k).distance_to(Vector2(np.x, np.z) / T) < 1.6:
			rozmawiaj(n)
			return
	info_budynek = zajete.get(k, -1)


# ===================================================================== pętla
func _process(dt: float) -> void:
	t += dt
	muzyka.volume_db = lerpf(muzyka.volume_db, -20.0 if glos.playing else -9.0, min(1.0, dt * 3))
	if nakladka == "kino":
		_kamera_kino(dt)
		return
	_aktualizuj_zycie(dt)
	_aktualizuj_kamere(dt)
	_aktualizuj_postacie()
	_aktualizuj_kompas()
	if duch:
		var p = pozycja_ducha()
		duch.visible = p != null
		if p != null:
			var d := bud(wybrany)
			duch.position = Vector3((p.x + d.w / 2.0) * T, 0, (p.y + d.h / 2.0) * T)
			duch.get_node("model").rotation.y = obrot_dzialki(wybrany, p.x, p.y)
			_material_ducha(duch, duch_mat_ok if moze_budowac(wybrany, p.x, p.y)[0] else duch_mat_zle)
	mat_dzialka.albedo_color.a = 0.3 + 0.2 * sin(t * 4.0)
	if scena != "gra":
		return
	if nakladka == "dialog":
		dialog.znaki += 55 * dt
		return
	if nakladka != "":
		return
	_ruch_bohatera(dt)
	zegar_dnia += dt
	if zegar_dnia >= DZIEN_SEK:
		zegar_dnia -= DZIEN_SEK
		nowy_dzien()
	if rozdzial_ukonczony():
		zakoncz_rozdzial()


func _ruch_bohatera(dt: float) -> void:
	var ix := Input.get_axis("ui_left", "ui_right")
	var iy := Input.get_axis("ui_up", "ui_down")
	if Input.is_physical_key_pressed(KEY_A):
		ix -= 1
	if Input.is_physical_key_pressed(KEY_D):
		ix += 1
	if Input.is_physical_key_pressed(KEY_W):
		iy -= 1
	if Input.is_physical_key_pressed(KEY_S):
		iy += 1
	if Input.is_physical_key_pressed(KEY_Q):
		yaw += 1.8 * dt
	if Input.is_physical_key_pressed(KEY_R):
		yaw -= 1.8 * dt
	var v := Vector2(clampf(ix, -1, 1), clampf(iy, -1, 1))
	idzie = v.length() > 0.1
	if not idzie:
		return
	v = v.normalized()
	var przod := Vector3(-sin(yaw), 0, -cos(yaw))
	var prawo := Vector3(cos(yaw), 0, -sin(yaw))
	var ruch := (prawo * v.x - przod * v.y) * 6.0 * dt
	var hp := Vector2(stan.bohater[0], stan.bohater[1])
	var nx := hp.x + ruch.x
	if _przechodnie(nx, hp.y):
		hp.x = nx
	var nz := hp.y + ruch.z
	if _przechodnie(hp.x, nz):
		hp.y = nz
	stan.bohater = [hp.x, hp.y]
	bohater.rotation.y = lerp_angle(bohater.rotation.y, atan2(ruch.x, ruch.z), 0.25)


func _przechodnie(x: float, z: float) -> bool:
	if x < 0.4 or z < 0.4 or x > map_w * T - 0.4 or z > map_h * T - 0.4:
		return false
	return not teren_w(floori(x / T), floori(z / T)) in ["~", "K", "D", "^"]


func _aktualizuj_postacie() -> void:
	bohater.position = Vector3(stan.bohater[0], 0, stan.bohater[1])
	var m: Node3D = bohater.get_node("model")
	if idzie and scena == "gra" and nakladka == "":
		faza_kroku += get_process_delta_time() * 10.0
		m.position.y = abs(sin(faza_kroku)) * 0.06
		animuj(m, faza_kroku, 1.0)
	else:
		m.position.y = 0
		animuj(m, t * 1.5, 0.08)
	var obok := npc_obok() if scena == "gra" and nakladka == "" else ""
	for k in npc_wezly:
		var n: Node3D = npc_wezly[k]
		var mm: Node3D = n.get_node("model")
		animuj(mm, t * 1.6 + k.length(), 0.1)
		var hp := bohater.position - n.position
		if hp.length() < 8:
			n.rotation.y = lerp_angle(n.rotation.y, atan2(hp.x, hp.z), 0.08)
		var klucz := "%s:%d" % [k, int(stan.rozdzial)]
		var wyk: Label3D = n.get_node("wykrzyknik")
		wyk.visible = D.rozmowy.has(klucz) and not ("rozm_%s_%d" % [k, int(stan.rozdzial)]) in stan.flagi
		wyk.position.y = 4.2 + sin(t * 5) * 0.15
		n.get_node("podpowiedz").visible = obok == k


func _aktualizuj_kamere(dt: float) -> void:
	var cel: Vector3
	var d := odl
	var pochyl := deg_to_rad(52)
	if scena == "gra":
		cel = bohater.position + Vector3(0, 1.0, 0)
	else:
		yaw += dt * 0.08
		cel = Vector3(map_w * T / 2, 0, map_h * T / 2)
		d = 44.0
		pochyl = deg_to_rad(38)
	var poz := cel + Vector3(sin(yaw), 0, cos(yaw)) * d * cos(pochyl) + Vector3(0, d * sin(pochyl), 0)
	kamera.position = kamera.position.lerp(poz, 1.0 if tryb != "" else min(1.0, dt * 8))
	kamera.look_at(cel)


func _aktualizuj_kompas() -> void:
	strzalka.visible = false
	znacznik.visible = false
	if not (kompas and scena == "gra"):
		return
	var c := cel_kompasu()
	if c[0] == null:
		return
	var cel: Vector3 = c[0]
	strzalka.visible = true
	strzalka.position = bohater.position + Vector3(0, 3.3 + sin(t * 3) * 0.1, 0)
	var kier := Vector3(cel.x, strzalka.position.y, cel.z)
	if kier.distance_to(strzalka.position) > 0.5:
		strzalka.look_at(kier)
	znacznik.visible = true
	znacznik.position = cel + Vector3(0, 0.1, 0)
	znacznik.rotation.y = t
	var s := 1.3 + sin(t * 4) * 0.15
	znacznik.scale = Vector3(s, s, s)


# ===================================================================== animacja postaci
func animuj(model: Node3D, faza: float, sila: float) -> void:
	## Postacie z Blendera mają osobne części: noga_l, noga_p, reka_l, reka_p (punkt obrotu w stawie).
	if not model.has_meta("czesci"):
		var cz := {}
		for n in ["noga_l", "noga_p", "reka_l", "reka_p"]:
			var w := model.find_child(n, true, false)
			if w:
				cz[n] = w
		model.set_meta("czesci", cz)
	var cz: Dictionary = model.get_meta("czesci")
	var s := sin(faza)
	if cz.has("noga_l"):
		cz.noga_l.rotation.x = s * 0.6 * sila
		cz.noga_p.rotation.x = -s * 0.6 * sila
	if cz.has("reka_l"):
		cz.reka_p.rotation.x = s * 0.5 * sila
		if not model.has_meta("gest"):
			cz.reka_l.rotation.x = -s * 0.5 * sila


# ===================================================================== światło i pogoda kampanii
func _oswietlenie() -> void:
	var r := int(stan.rozdzial)
	var u := {
		1: [Vector3(-46, -35, 0), 0.95, Color(1, 0.92, 0.8), Color(0.62, 0.66, 0.76), 0.45, Color(0.36, 0.5, 0.74), Color(0.86, 0.82, 0.74), 0.002],
		2: [Vector3(-55, -20, 0), 1.05, Color(1, 0.98, 0.93), Color(0.6, 0.68, 0.82), 0.5, Color(0.22, 0.48, 0.9), Color(0.8, 0.86, 0.92), 0.0015],
		3: [Vector3(-60, -30, 0), 0.55, Color(0.86, 0.88, 0.94), Color(0.7, 0.72, 0.78), 0.75, Color(0.5, 0.53, 0.58), Color(0.7, 0.72, 0.74), 0.012],
		4: [Vector3(-26, -62, 0), 1.0, Color(1, 0.82, 0.6), Color(0.72, 0.64, 0.62), 0.45, Color(0.34, 0.44, 0.74), Color(1, 0.8, 0.62), 0.003],
	}.get(r)
	slonce.rotation_degrees = u[0]
	slonce.light_energy = u[1]
	slonce.light_color = u[2]
	srodowisko.ambient_light_color = u[3]
	srodowisko.ambient_light_energy = u[4]
	niebo_mat.sky_top_color = u[5]
	niebo_mat.sky_horizon_color = u[6]
	srodowisko.fog_enabled = true
	srodowisko.fog_light_color = u[6].lerp(Color(0.8, 0.8, 0.82), 0.5)
	srodowisko.fog_density = u[7]


# ===================================================================== życie miasta
func _zycie_miasta() -> void:
	_wyczysc(zycie_wezel)
	zycie = []
	deszcz = null
	var rng := RandomNumberGenerator.new()
	rng.seed = 1100 + int(stan.rozdzial)
	var r := int(stan.rozdzial)
	var ulice := []
	for y in map_h:
		for x in map_w:
			if mapa[y][x] in ["=", "B"]:
				ulice.append(Vector2i(x, y))
	var modele_pieszych: Array = {1: [0, 1, 2, 0], 2: [0, 1, 5, 1], 3: [3, 3, 3, 0], 4: [1, 2, 5, 5]}[r]
	for i in 14:
		if ulice.is_empty():
			break
		var start: Vector2i = ulice[rng.randi_range(0, ulice.size() - 1)]
		var w := Node3D.new()
		var m := instancja("przechodzien_%d" % modele_pieszych[i % modele_pieszych.size()])
		m.name = "model"
		m.scale = Vector3.ONE * SKALA_POSTACI * rng.randf_range(0.92, 1.05)
		w.add_child(m)
		w.position = Vector3((start.x + 0.5) * T, 0, (start.y + 0.5) * T)
		zycie_wezel.add_child(w)
		zycie.append({"typ": "pieszy", "w": w, "pole": start, "cel": w.position, "kier": Vector2i(1, 0),
			"v": rng.randf_range(1.2, 1.9), "faza": rng.randf() * TAU})
	# pojazdy jeżdżą po długich prostych ulicach
	var pojazdy: Array = {1: ["tramwaj", "dorozka"], 2: ["dorozka", "automobil"], 3: ["automobil"], 4: ["automobil", "dorozka", "automobil"]}[r]
	var trasy := _trasy()
	for i in min(pojazdy.size(), trasy.size()):
		var tr: Array = trasy[i]
		var w := instancja(pojazdy[i])
		w.scale = Vector3.ONE * 1.3
		zycie_wezel.add_child(w)
		zycie.append({"typ": "pojazd", "w": w, "a": tr[0], "b": tr[1], "s": rng.randf(), "v": 3.2, "kier": 1})
	# dym z kominów
	if r != 2:
		var licz := 0
		for y in map_h:
			for x in map_w:
				if mapa[y][x] == "K" and (x * 5 + y * 3) % 9 == 0 and licz < 14:
					licz += 1
					zycie_wezel.add_child(_dym(Vector3((x + 0.5) * T + 0.4, 5.2, (y + 0.5) * T)))
	# ptaki
	for i in 6:
		var p := instancja("ptak")
		p.scale = Vector3.ONE * 2.2
		zycie_wezel.add_child(p)
		zycie.append({"typ": "ptak", "w": p, "r": rng.randf_range(14, 26), "h": rng.randf_range(12, 18),
			"f": rng.randf() * TAU, "v": rng.randf_range(0.15, 0.3)})
	if r == 3:
		deszcz = _deszcz()
		zycie_wezel.add_child(deszcz)


func _trasy() -> Array:
	var trasy := []
	for y in map_h:
		var run := 0
		for x in map_w + 1:
			if x < map_w and mapa[y][x] in ["=", "#"]:
				run += 1
			else:
				if run >= 14:
					trasy.append([Vector3((x - run + 0.5) * T, 0, (y + 0.5) * T + 0.5), Vector3((x - 0.5) * T, 0, (y + 0.5) * T + 0.5)])
				run = 0
	for x in map_w:
		var run2 := 0
		for y in map_h + 1:
			if y < map_h and mapa[y][x] in ["=", "#"]:
				run2 += 1
			else:
				if run2 >= 14:
					trasy.append([Vector3((x + 0.5) * T - 0.5, 0, (y - run2 + 0.5) * T), Vector3((x + 0.5) * T - 0.5, 0, (y - 0.5) * T)])
				run2 = 0
	return trasy


func _dym(poz: Vector3) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	var sm := SphereMesh.new()
	sm.radius = 0.35
	sm.height = 0.7
	sm.radial_segments = 8
	sm.rings = 4
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(0.8, 0.8, 0.82, 0.55)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	sm.material = m
	p.mesh = sm
	p.amount = 8
	p.lifetime = 4.0
	p.direction = Vector3.UP
	p.spread = 12
	p.gravity = Vector3(0.4, 0.6, 0)
	p.initial_velocity_min = 0.6
	p.initial_velocity_max = 1.0
	p.scale_amount_min = 0.6
	p.scale_amount_max = 1.6
	p.position = poz
	return p


func _deszcz() -> CPUParticles3D:
	var p := CPUParticles3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(0.03, 0.7, 0.03)
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(0.75, 0.82, 0.95, 0.5)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	bm.material = m
	p.mesh = bm
	p.amount = 700
	p.lifetime = 1.0
	p.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	p.emission_box_extents = Vector3(26, 0.5, 26)
	p.direction = Vector3.DOWN
	p.spread = 3
	p.gravity = Vector3(0, -30, 0)
	p.initial_velocity_min = 8
	p.initial_velocity_max = 10
	p.local_coords = false
	return p


func _aktualizuj_zycie(dt: float) -> void:
	for z in zycie:
		var w: Node3D = z.w
		match z.typ:
			"pieszy":
				var d: Vector3 = z.cel - w.position
				if d.length() < 0.1:
					z.pole = _nastepne_pole(z.pole, z.kier)
					var nowy: Vector2i = z.pole
					z.kier = nowy - Vector2i(floori(w.position.x / T), floori(w.position.z / T))
					z.cel = Vector3((nowy.x + 0.5) * T + randf_range(-0.4, 0.4), 0, (nowy.y + 0.5) * T + randf_range(-0.4, 0.4))
				else:
					w.position += d.normalized() * min(d.length(), z.v * dt)
					w.rotation.y = lerp_angle(w.rotation.y, atan2(d.x, d.z), 0.2)
				z.faza += dt * z.v * 5.5
				animuj(w.get_node("model"), z.faza, 0.9)
			"pojazd":
				var dl: float = z.a.distance_to(z.b)
				z.s += z.kier * z.v * dt / dl
				if z.s > 1.0 or z.s < 0.0:
					z.kier = -z.kier
					z.s = clampf(z.s, 0.0, 1.0)
				var kier: Vector3 = (z.b - z.a) * z.kier
				var bok := Vector3(kier.z, 0, -kier.x).normalized() * 0.6
				w.position = z.a.lerp(z.b, z.s) + bok
				w.rotation.y = atan2(kier.x, kier.z)
			"ptak":
				z.f += z.v * dt
				var c := Vector3(map_w * T / 2, 0, map_h * T / 2)
				w.position = c + Vector3(cos(z.f) * z.r, z.h + sin(z.f * 3) * 0.6, sin(z.f) * z.r)
				w.rotation.y = -z.f
				w.scale.x = 2.2 * (0.6 + 0.4 * abs(sin(t * 8 + z.r)))
	if deszcz:
		deszcz.position = Vector3(kamera.position.x, 18, kamera.position.z - 8)


func _nastepne_pole(p: Vector2i, kier: Vector2i) -> Vector2i:
	var opcje := []
	for d in [kier, Vector2i(kier.y, kier.x), Vector2i(-kier.y, -kier.x), Vector2i(1, 0), Vector2i(0, 1), Vector2i(-1, 0), Vector2i(0, -1)]:
		var n: Vector2i = p + d
		if teren_w(n.x, n.y) in ["=", "B"] and d != Vector2i.ZERO:
			opcje.append(n)
	if opcje.is_empty():
		return p
	if randf() < 0.7:
		return opcje[0]
	return opcje[randi() % opcje.size()]


# ===================================================================== przerywniki filmowe
func pokaz_przerywnik(nazwa: String, na_koniec: Callable) -> void:
	if tryb == "test":
		if na_koniec.is_valid():
			na_koniec.call()
		return
	kino_nazwa = nazwa
	kino_i = 0
	kino_koniec = na_koniec
	if kino:
		kino.queue_free()
	kino = Node3D.new()
	kino.position = KINO
	add_child(kino)
	slonce.shadow_enabled = false
	match nazwa:
		"wstep":
			_kino_model("klasa", Vector3.ZERO, 0)
			_kino_postac("postac_nauczyciel", Vector3(0.3, 0, -1.9), Vector3(0.3, 0, 4), true)
			_kino_swiatlo(Vector3(0, 3.2, 0))
			_kino_swiatlo(Vector3(0, 3.2, -3))
			kino_ujecia = [[Vector3(0, 2.3, 5.2), Vector3(0, 1.3, -3)], [Vector3(0.8, 1.8, 0.4), Vector3(0.3, 1.55, -1.9)],
				[Vector3(1.4, 1.7, -1.2), Vector3(0, 1.5, -4.4)], [Vector3(-0.6, 1.8, 0.6), Vector3(0.3, 1.55, -1.9)],
				[Vector3(2.4, 2.2, 3.0), Vector3(0, 1.2, -2.5)], [Vector3(0.5, 1.75, -0.2), Vector3(0.3, 1.6, -1.9)],
				[Vector3(0, 2.6, 6.0), Vector3(0, 1.3, -3)]]
		"przemowienie":
			_kino_model("sala_rady", Vector3.ZERO, 0)
			_kino_postac("postac_dmowski", Vector3(-3.6, 0, 1.2), Vector3(0, 0, -1.5), true)
			_kino_postac("postac_clemenceau", Vector3(-1.2, 0, -2.6), Vector3(-3.6, 0, 1.2))
			_kino_postac("postac_wilson", Vector3(1.2, 0, -2.6), Vector3(-3.6, 0, 1.2))
			_kino_postac("przechodzien_5", Vector3(3.2, 0, -2.6), Vector3(-3.6, 0, 1.2))
			_kino_postac("przechodzien_5", Vector3(-3.0, 0, -2.4), Vector3(-3.6, 0, 1.2))
			_kino_swiatlo(Vector3(0, 4.5, 0))
			kino_ujecia = [[Vector3(0, 3.8, 7.5), Vector3(0, 1.0, -1)], [Vector3(-2.0, 2.0, 3.6), Vector3(-3.6, 1.6, 1.2)],
				[Vector3(1.6, 3.0, 4.2), Vector3(-4.6, 1.6, 1.5)], [Vector3(-0.6, 2.0, -0.2), Vector3(-1.2, 1.6, -2.6)],
				[Vector3(0, 5.0, 8.5), Vector3(0, 1.0, -2)]]
		"listopad":
			var ziemia := MeshInstance3D.new()
			var bm := BoxMesh.new()
			bm.size = Vector3(80, 0.1, 80)
			var mz := StandardMaterial3D.new()
			mz.albedo_color = Color(0.6, 0.57, 0.53)
			bm.material = mz
			ziemia.mesh = bm
			ziemia.position.y = -0.05
			kino.add_child(ziemia)
			_kino_model("zamek", Vector3(0, 0, -13), 0)
			_kino_model("kolumna", Vector3(-7, 0, -6), 0)
			for i in 9:
				_kino_model("kamienica_wwa_%d" % (i % 3), Vector3(-15, 0, -14 + i * 3.2), PI / 2)
				_kino_model("kamienica_wwa_%d" % ((i + 1) % 3), Vector3(15, 0, -14 + i * 3.2), -PI / 2)
			var rng := RandomNumberGenerator.new()
			rng.seed = 1111
			for i in 28:
				var nr: int = [4, 4, 0, 1, 3, 4, 2][i % 7]
				var p := Vector3(rng.randf_range(-8, 8), 0, rng.randf_range(-3, 5))
				_kino_postac("przechodzien_%d" % nr, p, Vector3(0, 0, -8) + Vector3(rng.randf_range(-2, 2), 0, 0))
			_kino_postac("postac_pilsudski", Vector3(0, 0, -6.5), Vector3(0, 0, 4))
			kino_ujecia = [[Vector3(0, 7, 17), Vector3(0, 2, -6)], [Vector3(7, 2.4, 5), Vector3(0, 1.5, 0)],
				[Vector3(-4, 2.2, -1.5), Vector3(0, 1.8, -8)], [Vector3(0, 2.0, -3.6), Vector3(0, 1.7, -6.5)],
				[Vector3(0, 13, 22), Vector3(0, 2, -8)]]
		"traktat":
			_kino_model("sala_lustrzana", Vector3.ZERO, 0)
			_kino_postac("postac_paderewski", Vector3(-1.7, 0, -1.4), Vector3(0, 0, -1.4), true)
			_kino_postac("postac_dmowski", Vector3(-1.7, 0, -0.1), Vector3(0, 0, -0.1))
			_kino_postac("postac_clemenceau", Vector3(0, 0, -5.8), Vector3(0, 0, 0))
			_kino_postac("postac_wilson", Vector3(1.7, 0, -3.2), Vector3(0, 0, -3.2))
			_kino_postac("przechodzien_5", Vector3(1.7, 0, -1.6), Vector3(0, 0, -1.6))
			_kino_postac("przechodzien_5", Vector3(1.7, 0, 0.0), Vector3(0, 0, 0))
			var rng2 := RandomNumberGenerator.new()
			rng2.seed = 1919
			for i in 14:
				var p2 := Vector3(rng2.randf_range(-3.5, 3.5), 0, rng2.randf_range(4, 12))
				_kino_postac("przechodzien_5", p2, Vector3(0, 0, -2))
			for z in [-12.0, -4.0, 4.0, 12.0]:
				_kino_swiatlo(Vector3(0, 5.5, z))
			kino_ujecia = [[Vector3(0, 3.4, 16), Vector3(0, 2.6, -10)], [Vector3(2.5, 3.6, 8), Vector3(-1.5, 1.2, -3)],
				[Vector3(0, 2.4, -8.0), Vector3(0, 1.4, -1)], [Vector3(0.7, 2.3, -1.4), Vector3(-1.7, 1.6, -1.4)],
				[Vector3(0.7, 2.3, -0.1), Vector3(-1.7, 1.6, -0.1)], [Vector3(3.8, 6.0, 11), Vector3(0, 1.0, -3)]]
	nakladka = "kino"
	kamera.position = KINO + kino_ujecia[0][0]
	kamera.look_at(KINO + kino_ujecia[0][1])
	ui.odswiez_kino()


func _kino_model(nazwa: String, poz: Vector3, rot: float) -> void:
	var m := instancja(nazwa)
	m.position = poz
	m.rotation.y = rot
	kino.add_child(m)


func _kino_postac(nazwa: String, poz: Vector3, patrzy_na: Vector3, gest := false) -> void:
	var m := instancja(nazwa)
	m.position = poz
	var d := patrzy_na - poz
	m.rotation.y = atan2(d.x, d.z)
	kino.add_child(m)
	if gest:
		m.set_meta("gest", true)
		var r := m.find_child("reka_l", true, false)
		if r:
			r.rotation.x = -1.3


func _kino_swiatlo(poz: Vector3) -> void:
	var l := OmniLight3D.new()
	l.position = poz
	l.omni_range = 18
	l.light_energy = 1.2
	l.light_color = Color(1, 0.9, 0.75)
	kino.add_child(l)


func dalej_kino() -> void:
	if nakladka != "kino":
		return
	kino_i += 1
	if kino_i >= D.przerywniki[kino_nazwa].size():
		zakoncz_kino()
	else:
		ui.odswiez_kino()


func zakoncz_kino() -> void:
	ucisz_lektora()
	nakladka = ""
	slonce.shadow_enabled = true
	if kino:
		kino.queue_free()
		kino = null
	ui.odswiez_kino()
	var cb := kino_koniec
	kino_koniec = Callable()
	if cb.is_valid():
		cb.call()


func _kamera_kino(dt: float) -> void:
	var u: Array = kino_ujecia[min(kino_i, kino_ujecia.size() - 1)]
	var dryf := Vector3(sin(t * 0.3) * 0.25, 0, cos(t * 0.25) * 0.2)
	var cel_poz: Vector3 = KINO + u[0] + dryf
	kamera.position = kamera.position.lerp(cel_poz, 1.0 if tryb != "" else min(1.0, dt * 1.2))
	var patrz: Vector3 = KINO + u[1]
	var obecny := -kamera.global_transform.basis.z
	var docelowy := (patrz - kamera.position).normalized()
	kamera.look_at(kamera.position + obecny.lerp(docelowy, 1.0 if tryb != "" else min(1.0, dt * 2.0)))


# ===================================================================== mini-gra: przemówienie
func rozpocznij_przemowienie(na_koniec: Callable) -> void:
	minigra = {"runda": 0, "punkty": 0, "stan": "pytanie", "kolejnosc": [], "ostatnie": 0, "koniec": na_koniec}
	_tasuj_odpowiedzi()
	if tryb == "test":
		minigra.punkty = 125
		zakoncz_przemowienie()
		return
	nakladka = "przemowienie"
	ui.odswiez_przemowienie()


func _tasuj_odpowiedzi() -> void:
	var k := [0, 1, 2]
	k.shuffle()
	minigra.kolejnosc = k


func wybierz_argument(i: int) -> void:
	if minigra == null or minigra.stan != "pytanie":
		return
	var runda = D.przemowienie[minigra.runda]
	var pkt := int(runda.odpowiedzi[minigra.kolejnosc[i]][1])
	minigra.punkty += pkt
	minigra.ostatnie = pkt
	minigra.stan = "reakcja"
	dzwiek("dobrze" if pkt >= 20 else "zle")
	ui.odswiez_przemowienie()


func dalej_przemowienie() -> void:
	if minigra == null:
		return
	if minigra.stan == "reakcja":
		minigra.runda += 1
		if minigra.runda >= D.przemowienie.size():
			minigra.stan = "wynik"
			dzwiek("fanfara")
		else:
			minigra.stan = "pytanie"
			_tasuj_odpowiedzi()
		ui.odswiez_przemowienie()
	elif minigra.stan == "wynik":
		zakoncz_przemowienie()


func gwiazdki() -> int:
	var p: int = minigra.punkty if minigra != null else 0
	return 3 if p >= 100 else (2 if p >= 70 else 1)


func zakoncz_przemowienie() -> void:
	var g := gwiazdki()
	stan.pw += g * 3
	stan.zasoby.poparcie += minigra.punkty / 2
	ui.toast("Przemówienie: %s  (+%d PW, +%d poparcia)" % ["★".repeat(g), g * 3, minigra.punkty / 2])
	var cb: Callable = minigra.koniec
	minigra = null
	nakladka = ""
	ui.odswiez_przemowienie()
	if cb.is_valid():
		cb.call()


# ===================================================================== zrzuty i test
func klatki(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func zrob(nazwa: String) -> void:
	await klatki(3)
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(tryb.path_join(nazwa + ".png"))
	print("zrzut: ", nazwa)


func _przejdz_do(rozdzial: int) -> void:
	stan.rozdzial = rozdzial
	stan.budynki = []
	stan.ludnosc = 8.0
	_ustaw_start()
	zbuduj_swiat()


func _zrzuty() -> void:
	DirAccess.make_dir_recursive_absolute(tryb)
	pokaz_tytul()
	await klatki(10)
	await zrob("01_tytul")
	pokaz_mape("2", Callable())
	ui.mapa_krok = 3
	ui._ustaw_krok_mapy()
	ui.mapa_w.postep = 3.45
	await zrob("02a_mapa_podroz")
	pokaz_mape("4", Callable())
	ui.mapa_krok = 1
	ui._ustaw_krok_mapy()
	ui.mapa_w.przejscie = 1.0
	await zrob("02b_mapa_1918")
	nowa_gra()
	kino_i = 1
	ui.odswiez_kino()
	await zrob("02w_wstep_nauczyciela")
	zakoncz_kino()
	await zrob("02c_mapa_1914")
	zakoncz_mape()
	ui.intro_pelny()
	await zrob("02_kampania1")
	# Kampania I — Warszawa, Komitet w budowie
	stan.flagi = ["powitanie", "rozm_zamoyski_1"]
	stan.ekwipunek = ["kompas", "teczka", "datki", "paczka"]
	stan.pw = 22
	stan.zasoby = {"fundusze": 146, "poparcie": 28, "prasa": 34, "ochotnicy": 0}
	stan.ludnosc = 18.0
	for b in [["kwatera", 13, 14], ["kwatera", 14, 14], ["kwatera", 13, 16], ["redakcja", 21, 13],
			["komitet", 15, 19], ["knp_warszawa", 19, 15]]:
		stan.budynki.append({"typ": b[0], "x": b[1], "y": b[2], "postep": 9 if b[0] != "knp_warszawa" else 2, "wariant": 0})
	odswiez_swiat()
	scena = "gra"
	ui.pokaz_ekran()
	stan.bohater = [19.0 * T, 13.6 * T]
	yaw = 0.5
	odl = 30
	kompas = true
	_odswiez_dzialki()
	await zrob("03_warszawa")
	kompas = false
	_odswiez_dzialki()
	odl = 16
	yaw = -0.4
	rozmawiaj("hanna")
	dialog.znaki = 999
	dalej_dialog()
	await zrob("04_zagadka")
	zamknij_dialog()
	# Kampania II — Lozanna
	_przejdz_do(2)
	stan.budynki = [{"typ": "biuro", "x": 14, "y": 9, "postep": 9, "wariant": 0},
		{"typ": "redakcja", "x": 22, "y": 8, "postep": 9, "wariant": 0},
		{"typ": "kwatera", "x": 6, "y": 9, "postep": 9, "wariant": 0},
		{"typ": "knp_lozanna", "x": 18, "y": 10, "postep": 9, "wariant": 0}]
	odswiez_swiat()
	stan.bohater = [19.5 * T, 13.5 * T]
	yaw = 0.2
	odl = 32
	await zrob("05_lozanna")
	# Kampania III — Błękitna Armia
	_przejdz_do(3)
	stan.ekwipunek = ["kompas", "teczka", "mapa", "legitymacja", "nota", "odznaka"]
	stan.budynki = [{"typ": "kwatera_glowna", "x": 8, "y": 7, "postep": 9, "wariant": 0},
		{"typ": "oboz", "x": 17, "y": 6, "postep": 9, "wariant": 0},
		{"typ": "werbunek", "x": 10, "y": 13, "postep": 9, "wariant": 0},
		{"typ": "szpital", "x": 22, "y": 13, "postep": 9, "wariant": 0},
		{"typ": "pozycja", "x": 27, "y": 3, "postep": 9, "wariant": 0},
		{"typ": "pozycja", "x": 27, "y": 9, "postep": 1, "wariant": 0}]
	odswiez_swiat()
	stan.bohater = [22.0 * T, 10.5 * T]
	yaw = -0.5
	odl = 34
	kompas = true
	_odswiez_dzialki()
	await zrob("06_blekitna_armia")
	kompas = false
	_odswiez_dzialki()
	rozmawiaj("haller")
	for i in 3:
		dialog.znaki = 999
		dalej_dialog()
	dialog.znaki = 999
	ui.odswiez_dialog()
	await zrob("07_haller")
	zamknij_dialog()
	# Kampania IV — Paryż
	_przejdz_do(4)
	stan.pw = 70
	for k in ["knp", "orientacje", "wielka_wojna", "akt_5_listopada", "rewolucja", "memorial", "blekitna_armia",
			"listopad", "pilsudski", "paderewski", "powstanie", "konferencja", "przemowienie"]:
		if not k in stan.karty:
			stan.karty.append(k)
	stan.przeczytane = ["dmowski", "kompas", "zabory", "knp", "orientacje", "wielka_wojna", "haller"]
	stan.budynki = [{"typ": "delegacja", "x": 14, "y": 4, "postep": 9, "wariant": 0},
		{"typ": "sprawa_wielkopolska", "x": 19, "y": 16, "postep": 9, "wariant": 0},
		{"typ": "sprawa_pomorze", "x": 23, "y": 16, "postep": 9, "wariant": 0},
		{"typ": "sprawa_slask", "x": 19, "y": 19, "postep": 1, "wariant": 0}]
	odswiez_swiat()
	stan.bohater = [17.0 * T, 12.5 * T]
	yaw = 0.35
	odl = 36
	await zrob("08_paryz")
	ui.pokaz_okno("ekwipunek")
	ui.wybierz_przedmiot(3)
	await zrob("09_ekwipunek")
	ui.pokaz_okno("ksiega")
	ui.czytaj_karte("przemowienie")
	await zrob("10_ksiega")
	ui.ksiega_tryb = "os"
	ui.wybrane_wydarzenie = 15
	ui.pokaz_okno("ksiega")
	await zrob("10b_os_czasu")
	ui.ksiega_tryb = "postacie"
	stan.flagi += ["rozm_haller_3", "rozm_paderewski_4"]
	ui.wybrana_postac = "paderewski"
	ui.pokaz_okno("ksiega")
	await zrob("10c_karta_postaci")
	ui.ksiega_tryb = "karty"
	ui.zamknij_okno()
	rozpocznij_przemowienie(Callable())
	minigra.runda = 1
	minigra.punkty = 25
	ui.odswiez_przemowienie()
	await zrob("12_przemowienie_minigra")
	minigra.punkty = 125
	minigra.stan = "wynik"
	ui.odswiez_przemowienie()
	await zrob("13_przemowienie_wynik")
	minigra = null
	nakladka = ""
	ui.odswiez_przemowienie()
	for k in [["przemowienie", 1, "14_kino_rada"], ["listopad", 0, "15_kino_11_listopada"], ["traktat", 3, "16_kino_sala_lustrzana"]]:
		pokaz_przerywnik(k[0], Callable())
		kino_i = k[1]
		ui.odswiez_kino()
		await zrob(k[2])
		zakoncz_kino()
	scena = "koniec"
	stan.przeczytane = D.wiedza_kolejnosc.slice(0, 20)
	ui.pokaz_ekran()
	await zrob("11_koniec")
	get_tree().quit()


func _test() -> void:
	## Automatyczne przejście wszystkich kampanii (oczekiwane: TEST_WYNIK: OK).
	tryb = "test"
	nowa_gra()
	wejdz_do_gry()
	var dni := 0
	var starty := {}
	while scena != "koniec" and dni < 3000:
		if scena == "intro":
			starty[int(stan.rozdzial)] = dni
			wejdz_do_gry()
		_test_dialogi()
		for c in cele():
			var s := stan_celu(c)
			if s[0] >= s[1]:
				continue
			if c[1] == "rozmowa":
				rozmawiaj(c[2])
				_test_dialogi()
			elif c[1] == "buduj":
				var p = _test_miejsce(c[2])
				if p != null:
					postaw(c[2], p.x, p.y)
		for k in stan.karty:
			if not k in stan.przeczytane:
				stan.przeczytane.append(k)
				stan.pw += 2
		if stan.ludnosc >= pojemnosc() - 2 and stac("kwatera"):
			var pk = _test_miejsce("kwatera")
			if pk != null:
				postaw("kwatera", pk.x, pk.y)
		var dost: Array = R.dostepne
		for para in [["biuro", "poparcie"], ["redakcja", "prasa"], ["komitet", "fundusze"], ["werbunek", "ochotnicy"]]:
			var ile := 0
			for b in stan.budynki:
				if b.typ == para[0]:
					ile += 1
			if para[0] in dost and stan.zasoby[para[1]] < 60 and wydajnosc() >= 1.0 and stac(para[0]) and ile < 3:
				var pw = _test_miejsce(para[0])
				if pw != null:
					postaw(para[0], pw.x, pw.y)
		if dni % 5 == 0:
			for n in R.npc:
				rozmawiaj(n)
				_test_dialogi()
		for p in ["datki", "paczka"]:
			if p in stan.ekwipunek:
				uzyj_przedmiotu(p)
				ui.zamknij_okno()
		nowy_dzien()
		dni += 1
		if rozdzial_ukonczony() and nakladka == "":
			zakoncz_rozdzial()
		_test_dialogi()
	print("TEST scena=%s dni=%d starty=%s PW=%d ekwipunek=%s zasoby=%s" % [scena, dni, str(starty), stan.pw, str(stan.ekwipunek), str(stan.zasoby)])
	if scena != "koniec":
		for c in cele():
			print("  cel: ", c[0], " ", stan_celu(c))
	print("TEST_WYNIK: ", "OK" if scena == "koniec" else "BLAD")
	get_tree().quit(0 if scena == "koniec" else 1)


func _test_dialogi() -> void:
	var licznik := 0
	while nakladka == "dialog" and licznik < 100:
		licznik += 1
		if dialog.tryb == "zagadka":
			odpowiedz(dialog.odp.find(dialog.zagadka.poprawna))
		else:
			dialog.znaki = 9999
			dalej_dialog()


func _test_miejsce(typ: String):
	var d := bud(typ)
	if d.get("zabytek", false):
		for v in dzialki_typu(typ):
			if moze_budowac(typ, v.x, v.y)[0]:
				return v
		return null
	for y in map_h:
		for x in map_w:
			if moze_budowac(typ, x, y)[0]:
				return Vector2i(x, y)
	return null
