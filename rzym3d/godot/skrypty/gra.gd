extends Node3D
## Roman Empire — od narodzin przez rozkwit aż po upadek (Kroniki Damiana Ścisła).
## Stan gry, zasady (tury, ekonomia, technologie, zagony), świat 3D z kafli, kamera, zapis
## oraz tryby specjalne: --samotest, --zrzuty <katalog>, --serwer <port>.

const T := 2.0                      # 1 pole = 2 jednostki
const UI_SKRYPT := preload("res://skrypty/interfejs.gd")
const BITWA_SKRYPT := preload("res://skrypty/bitwa.gd")
const SIEC_SKRYPT := preload("res://skrypty/siec.gd")
const ZAPIS := "user://rzym_zapis.json"
const ZAPIS_KAMPANII := "user://rzym_kampania.json"
const WERSJA := 1
const BAZA_TALII := 6
const SKALA_POSTACI := 0.62
const POLE_BITWY := Vector3(0, 0, -400)

var D := {}                         # dane.json
var M := {}                         # mapa_imperium.json
var S := {}                         # stan rozgrywki (JSON – zapis i sieć)
var R := {}                         # dane bieżącego rozdziału
var K := {}                         # postęp kampanii
var N := 24

var ui
var bitwa
var siec
var scena := "tytul"                # tytul, mapa, intro, gra, bitwa, koniec, final, lobby, przekazanie
var tryb := ""                      # "", "test", "zrzuty", "serwer"
var moj_gracz := -1                 # online: mój numer gracza; -1 = wszyscy przy jednym komputerze
var t := 0.0

# świat 3D
var swiat: Node3D
var teren_wezel: Node3D
var dekor_wezel: Node3D
var bud_wezel: Node3D
var zagon_wezel: Node3D
var granice_wezel: MeshInstance3D
var kursor: MeshInstance3D
var duch: Node3D
var duch_typ := ""
var kamera: Camera3D
var slonce: DirectionalLight3D
var srodowisko: Environment
var niebo_mat: ProceduralSkyMaterial
var woda: MeshInstance3D
var _sceny := {}
var _bud_wezly := {}
var _zag_wezly := {}
var _znajdzki_wezly := {}
var _postacie := []
var _statki := []
var mapa_hash := ""
var wlasciciel := []                # [y][x] -> numer gracza lub -1

# kamera
var cel_kam := Vector3(24, 0, 24)
var yaw := 0.0
var yaw_cel := 0.0
var odl := 30.0
var przeciaganie := false

# wybór
var wybrany := ""                   # budynek do postawienia
var najechane := Vector2i(-1, -1)

# dźwięk
var dzwieki := {}
var gracze_dzw := []
var muzyka: AudioStreamPlayer
var muzyka_on := true
var muzyka_teraz := ""
var glos: AudioStreamPlayer
var lektor_on := true
var ostatni_glos := ""

var rng := RandomNumberGenerator.new()


# ===================================================================== start
func _ready() -> void:
	rng.randomize()
	var args := OS.get_cmdline_user_args()
	if "--serwer" in args:
		tryb = "serwer"
		var port := 9080
		var i := args.find("--serwer")
		if i + 1 < args.size() and args[i + 1].is_valid_int():
			port = int(args[i + 1])
		siec = SIEC_SKRYPT.new()
		siec.g = self
		add_child(siec)
		siec.uruchom_serwer(port)
		return
	D = JSON.parse_string(FileAccess.get_file_as_string("res://dane/dane.json"))
	M = JSON.parse_string(FileAccess.get_file_as_string("res://dane/mapa_imperium.json"))
	N = int(D.n)
	var bot := ""
	if "--bot" in args:
		bot = args[args.find("--bot") + 1]
	if "--samotest" in args:
		tryb = "test"
	elif "--zrzuty" in args:
		tryb = "zrzuty"
	_otoczenie()
	_wczytaj_dzwieki()
	siec = SIEC_SKRYPT.new()
	siec.g = self
	add_child(siec)
	ui = UI_SKRYPT.new()
	ui.g = self
	add_child(ui)
	ui.zbuduj()
	bitwa = BITWA_SKRYPT.new()
	bitwa.g = self
	add_child(bitwa)
	wczytaj_kampanie()
	if bot != "":
		await get_tree().process_frame
		await test_online(bot, args[args.find("--bot") + 2], args[args.find("--bot") + 3])
		return
	if tryb == "test":
		await get_tree().process_frame
		await samotest()
		return
	if tryb == "zrzuty":
		var i := args.find("--zrzuty")
		var kat: String = args[i + 1] if i + 1 < args.size() else "user://zrzuty"
		await get_tree().process_frame
		await zrzuty(kat)
		return
	pokaz_tytul()


func _otoczenie() -> void:
	## Oświetlenie sceny: niebo proceduralne jako źródło światła otoczenia, tonemapping ACES,
	## SSAO (cień przy styku obiektów z ziemią), lekki glow i niskie, ciepłe słońce z miękkimi cieniami.
	## SSAO działa w rendererze Forward+ (wersja na komputer). W przeglądarce (GL Compatibility)
	## styk z ziemią przyciemniają miękkie cienie kontaktowe pod obiektami (_cien_kontaktowy).
	srodowisko = Environment.new()
	srodowisko.background_mode = Environment.BG_SKY
	var niebo := Sky.new()
	niebo_mat = ProceduralSkyMaterial.new()
	niebo_mat.sun_angle_max = 18.0
	niebo_mat.sun_curve = 0.12
	niebo.sky_material = niebo_mat
	niebo.radiance_size = Sky.RADIANCE_SIZE_128
	srodowisko.sky = niebo
	# światło otoczenia i odbicia z nieba
	srodowisko.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	srodowisko.ambient_light_sky_contribution = 1.0
	srodowisko.ambient_light_energy = 0.8
	srodowisko.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	# tonemapping filmowy
	srodowisko.tonemap_mode = Environment.TONE_MAPPER_ACES
	srodowisko.tonemap_exposure = 0.95
	srodowisko.tonemap_white = 6.0
	# SSAO – przyciemnienie w zagłębieniach i przy styku z ziemią
	srodowisko.ssao_enabled = true
	srodowisko.ssao_radius = 1.4
	srodowisko.ssao_intensity = 3.0
	srodowisko.ssao_power = 1.6
	srodowisko.ssao_detail = 0.6
	srodowisko.ssao_horizon = 0.06
	srodowisko.ssao_sharpness = 0.98
	srodowisko.ssao_light_affect = 0.15
	# lekki glow (blask jasnych miejsc: słońce na marmurze, woda)
	srodowisko.glow_enabled = true
	srodowisko.glow_intensity = 0.32
	srodowisko.glow_strength = 0.9
	srodowisko.glow_bloom = 0.04
	srodowisko.glow_hdr_threshold = 1.05
	srodowisko.glow_blend_mode = Environment.GLOW_BLEND_MODE_SOFTLIGHT
	srodowisko.set_glow_level(0, 0.0)
	srodowisko.set_glow_level(1, 0.6)
	srodowisko.set_glow_level(2, 1.0)
	srodowisko.set_glow_level(3, 0.6)
	# mgła odległościowa (głębokościowa) w chłodnym odcieniu – dalsze plany bledną jak na makiecie
	srodowisko.fog_enabled = true
	srodowisko.fog_mode = Environment.FOG_MODE_DEPTH
	srodowisko.fog_light_color = MGLA_KOLOR
	srodowisko.fog_light_energy = 1.0
	srodowisko.fog_density = 0.7
	srodowisko.fog_depth_curve = 1.4
	srodowisko.fog_depth_begin = 28.0
	srodowisko.fog_depth_end = 110.0
	srodowisko.fog_sun_scatter = 0.08
	srodowisko.fog_aerial_perspective = 0.0
	srodowisko.fog_sky_affect = 0.35
	var we := WorldEnvironment.new()
	we.name = "WorldEnvironment"
	we.environment = srodowisko
	add_child(we)
	# słońce: nisko nad horyzontem, ciepłe, z miękkimi cieniami
	slonce = DirectionalLight3D.new()
	slonce.name = "Slonce"
	slonce.rotation_degrees = Vector3(-32, -40, 0)
	slonce.light_color = Color(1.0, 0.85, 0.64)
	slonce.light_energy = 1.7
	slonce.light_angular_distance = 1.6      # miękkie półcienie (PCSS w Forward+)
	slonce.shadow_enabled = true
	slonce.shadow_blur = 1.6                 # rozmycie krawędzi cieni (także w przeglądarce)
	slonce.shadow_bias = 0.04
	slonce.shadow_normal_bias = 1.2
	slonce.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
	slonce.directional_shadow_blend_splits = true
	slonce.directional_shadow_max_distance = 110.0
	add_child(slonce)
	kamera = Camera3D.new()
	kamera.fov = 34
	kamera.far = 900
	# głębia ostrości (tilt-shift): ostry środek, rozmyte bliższe i dalsze plany (Forward+)
	atrybuty_kamery = CameraAttributesPractical.new()
	atrybuty_kamery.dof_blur_far_enabled = true
	atrybuty_kamery.dof_blur_near_enabled = true
	atrybuty_kamery.dof_blur_amount = 0.14
	kamera.attributes = atrybuty_kamery
	add_child(kamera)
	# w przeglądarce (GL Compatibility) Godot nie ma DOF – zastępuje go shader tilt-shift na ekranie
	if RenderingServer.get_rendering_device() == null:
		_tilt_shift_ekranowy()
	ustaw_glebie(odl)
	swiat = Node3D.new()
	add_child(swiat)
	for n in ["teren", "dekor", "budynki", "zagony"]:
		var w := Node3D.new()
		w.name = n
		swiat.add_child(w)
	teren_wezel = swiat.get_node("teren")
	dekor_wezel = swiat.get_node("dekor")
	bud_wezel = swiat.get_node("budynki")
	zagon_wezel = swiat.get_node("zagony")
	granice_wezel = MeshInstance3D.new()
	swiat.add_child(granice_wezel)
	kursor = MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(T * 0.96, T * 0.96)
	kursor.mesh = pm
	var km := StandardMaterial3D.new()
	km.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	km.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	km.albedo_color = Color(1, 0.9, 0.4, 0.35)
	km.no_depth_test = false
	kursor.material_override = km
	kursor.visible = false
	swiat.add_child(kursor)


const MGLA_KOLOR := Color(0.62, 0.71, 0.84)
var atrybuty_kamery: CameraAttributesPractical
var tilt_shift: ColorRect


func _tilt_shift_ekranowy() -> void:
	## Tilt-shift dla renderera GL Compatibility: rozmycie górnego i dolnego pasa ekranu (12 próbek po spirali).
	var warstwa := CanvasLayer.new()
	warstwa.layer = 0
	add_child(warstwa)
	tilt_shift = ColorRect.new()
	tilt_shift.set_anchors_preset(Control.PRESET_FULL_RECT)
	tilt_shift.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := Shader.new()
	sh.code = """shader_type canvas_item;
uniform sampler2D ekran : hint_screen_texture, filter_linear;
uniform float srodek = 0.5;      // wysokość ostrego pasa (0 – góra, 1 – dół)
uniform float szerokosc = 0.3;   // szerokość ostrego pasa
uniform float sila = 2.0;        // promień rozmycia na krawędziach (w pikselach × 4)
void fragment() {
	float d = abs(SCREEN_UV.y - srodek) - szerokosc * 0.5;
	float r = smoothstep(0.0, 0.42, d) * sila;
	vec4 c = texture(ekran, SCREEN_UV);
	if (r > 0.05) {
		vec4 suma = vec4(0.0);
		for (int i = 0; i < 12; i++) {
			float a = float(i) * 2.39996;
			float rr = sqrt(float(i) + 0.5) / 3.4641;
			suma += texture(ekran, SCREEN_UV + vec2(cos(a), sin(a)) * rr * SCREEN_PIXEL_SIZE * r * 4.0);
		}
		c = suma / 12.0;
	}
	COLOR = c;
}
"""
	var m := ShaderMaterial.new()
	m.shader = sh
	tilt_shift.material = m
	tilt_shift.visible = false
	warstwa.add_child(tilt_shift)


func ustaw_glebie(ogniskowa: float, srodek_ekranu := 0.5, bitwa_profil := false) -> void:
	## Głębia sceny zależna od odległości kamery od punktu, na który patrzy:
	## mgła zaczyna się tuż za nim, a ostrość obejmuje pas wokół niego (efekt makiety).
	## Profil bitwy ma szerszy pas ostrości (całe szyki) i dalszą mgłę.
	var mgla_od := 0.75
	var mgla_do := 2.6
	var ostr_dal := 1.08
	var przejscie_dal := 0.6
	var ostr_blisko := 0.86
	var przejscie_blisko := 0.22
	if bitwa_profil:
		mgla_od = 2.0
		mgla_do = 7.0
		ostr_dal = 1.7
		przejscie_dal = 1.5
		ostr_blisko = 0.45
		przejscie_blisko = 0.2
	srodowisko.fog_depth_begin = ogniskowa * mgla_od
	srodowisko.fog_depth_end = ogniskowa * mgla_do
	# GL Compatibility (przeglądarka) liczy mgłę mocniej – słabsza gęstość
	srodowisko.fog_density = 0.45 if RenderingServer.get_rendering_device() == null else 0.7
	if atrybuty_kamery:
		atrybuty_kamery.dof_blur_far_distance = ogniskowa * ostr_dal
		atrybuty_kamery.dof_blur_far_transition = ogniskowa * przejscie_dal
		atrybuty_kamery.dof_blur_near_distance = ogniskowa * ostr_blisko
		atrybuty_kamery.dof_blur_near_transition = ogniskowa * przejscie_blisko
	if tilt_shift:
		tilt_shift.visible = scena in ["gra", "bitwa", "przekazanie", "koniec_mp"]
		var m := tilt_shift.material as ShaderMaterial
		m.set_shader_parameter("srodek", srodek_ekranu)
		m.set_shader_parameter("szerokosc", 0.55 if bitwa_profil else 0.3)


func _ustaw_klimat(epoka: String) -> void:
	## Klimat epoki: kolory nieba, barwa i wysokość słońca, siła światła otoczenia.
	## [góra nieba, horyzont, kolor słońca, energia słońca, kąt słońca, energia otoczenia]
	var nieba := {
		"krolestwo": [Color(0.36, 0.56, 0.84), Color(0.86, 0.8, 0.7), Color(1.0, 0.86, 0.66), 1.35, -32.0, 0.5],
		"republika": [Color(0.34, 0.55, 0.86), Color(0.88, 0.82, 0.72), Color(1.0, 0.87, 0.68), 1.4, -34.0, 0.5],
		"cesarstwo": [Color(0.3, 0.52, 0.88), Color(0.94, 0.84, 0.68), Color(1.0, 0.84, 0.6), 1.45, -30.0, 0.52],
		"schylek": [Color(0.38, 0.38, 0.52), Color(0.93, 0.66, 0.48), Color(1.0, 0.72, 0.48), 1.3, -22.0, 0.48],
	}
	var n: Array = nieba.get(epoka, nieba.republika)
	niebo_mat.sky_top_color = n[0]
	niebo_mat.sky_horizon_color = n[1]
	niebo_mat.ground_horizon_color = n[1].darkened(0.15)
	niebo_mat.ground_bottom_color = Color(0.22, 0.24, 0.2)
	niebo_mat.sun_angle_max = 18.0
	slonce.light_color = n[2]
	slonce.light_energy = n[3]
	slonce.rotation_degrees = Vector3(n[4], -40, 0)
	srodowisko.ambient_light_energy = n[5]
	# chłodna mgła, lekko zabarwiona horyzontem epoki
	srodowisko.fog_light_color = MGLA_KOLOR.lerp(n[1], 0.18) if epoka != "schylek" else Color(0.6, 0.6, 0.76)
	_kolory_wody()
	# GL Compatibility (przeglądarka) liczy światło w zakresie LDR i nie ma SSAO – scena wychodzi
	# jaśniejsza, więc obniżamy ekspozycję i światło otoczenia, żeby wyglądała jak w Forward+.
	if RenderingServer.get_rendering_device() == null:
		srodowisko.tonemap_exposure = 0.78
		srodowisko.ambient_light_energy = n[5] * 0.75
	else:
		srodowisko.tonemap_exposure = 0.95


func _cien_kontaktowy(rodzic: Node3D, promien: float, sila := 0.45) -> void:
	## Miękka, ciemna plama pod obiektem – cień kontaktowy (działa także w przeglądarce, bez SSAO).
	if _tekstura_cienia == null:
		var gr := Gradient.new()
		gr.set_color(0, Color(0, 0, 0, 1))
		gr.set_color(1, Color(0, 0, 0, 0))
		gr.add_point(0.45, Color(0, 0, 0, 0.55))
		var gt := GradientTexture2D.new()
		gt.gradient = gr
		gt.fill = GradientTexture2D.FILL_RADIAL
		gt.fill_from = Vector2(0.5, 0.5)
		gt.fill_to = Vector2(1.0, 0.5)
		gt.width = 64
		gt.height = 64
		_tekstura_cienia = gt
	var mi := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(promien * 2, promien * 2)
	mi.mesh = pm
	var m := StandardMaterial3D.new()
	m.albedo_texture = _tekstura_cienia
	m.albedo_color = Color(0.05, 0.04, 0.03, sila)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mi.material_override = m
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.position.y = 0.015
	rodzic.add_child(mi)


var _tekstura_cienia: GradientTexture2D


func _wczytaj_dzwieki() -> void:
	for n in ["klik", "strona", "buduj", "gotowe", "moneta", "dobrze", "zle", "blad", "fanfara", "bebny", "miecz",
			"tarcza", "rog", "tlum", "tura", "odkrycie", "przedmiot"]:
		var s := "res://audio/%s.wav" % n
		if ResourceLoader.exists(s):
			dzwieki[n] = load(s)
	for i in 6:
		var p := AudioStreamPlayer.new()
		add_child(p)
		gracze_dzw.append(p)
	muzyka = AudioStreamPlayer.new()
	muzyka.volume_db = -11
	muzyka.finished.connect(func(): if muzyka_on: muzyka.play())
	add_child(muzyka)
	glos = AudioStreamPlayer.new()
	add_child(glos)


func dzwiek(n: String) -> void:
	if tryb != "" or not dzwieki.has(n):
		return
	for p in gracze_dzw:
		if not p.playing:
			p.stream = dzwieki[n]
			p.volume_db = -6.0 if n in ["moneta", "klik"] else -2.0
			p.play()
			return


func graj_muzyke(nazwa: String) -> void:
	if tryb != "" or nazwa == muzyka_teraz:
		return
	muzyka_teraz = nazwa
	var s := "res://audio/muzyka_%s.wav" % nazwa
	if not ResourceLoader.exists(s):
		return
	var st: AudioStreamWAV = load(s)
	st.loop_mode = AudioStreamWAV.LOOP_FORWARD
	st.loop_begin = 0
	st.loop_end = int(st.get_length() * st.mix_rate)
	muzyka.stream = st
	if muzyka_on:
		muzyka.play()


func przelacz_muzyke() -> void:
	muzyka_on = not muzyka_on
	if muzyka_on:
		muzyka.play()
	else:
		muzyka.stop()
	ui.toast("Muzyka: " + ("włączona" if muzyka_on else "wyłączona"))


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
	if glos:
		glos.stop()
	ostatni_glos = ""


func przelacz_lektora() -> void:
	lektor_on = not lektor_on
	if not lektor_on:
		ucisz_lektora()
	ui.toast("Lektor: " + ("włączony" if lektor_on else "wyłączony"))


# ===================================================================== kampania i zapis
func wczytaj_kampanie() -> void:
	K = {"ukonczone": [], "wyniki": {}, "trudnosc": 1, "imie": "Damian"}
	if FileAccess.file_exists(ZAPIS_KAMPANII) and tryb == "":
		var d = JSON.parse_string(FileAccess.get_file_as_string(ZAPIS_KAMPANII))
		if typeof(d) == TYPE_DICTIONARY:
			K.merge(d, true)


func zapisz_kampanie() -> void:
	if tryb != "":
		return
	var f := FileAccess.open(ZAPIS_KAMPANII, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(K))


func zapisz() -> void:
	if tryb != "" or S.is_empty() or S.tryb == "online":
		return
	var f := FileAccess.open(ZAPIS, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(S))


func ma_zapis() -> bool:
	return FileAccess.file_exists(ZAPIS)


func wczytaj() -> bool:
	if not ma_zapis():
		return false
	var d = JSON.parse_string(FileAccess.get_file_as_string(ZAPIS))
	if typeof(d) != TYPE_DICTIONARY or int(d.get("wersja", 0)) != WERSJA:
		return false
	ustaw_stan(d)
	moj_gracz = -1
	scena = "gra"
	ui.pokaz_ekran()
	return true


func ustaw_stan(nowy: Dictionary) -> void:
	## Przyjmuje stan (z zapisu albo z sieci) i odświeża świat.
	var inny_rozdzial: bool = S.is_empty() or int(S.get("rozdzial", -1)) != int(nowy.rozdzial)
	S = nowy
	R = D.rozdzialy[int(S.rozdzial)]
	if inny_rozdzial or str(S.mapa.hash()) != mapa_hash:
		zbuduj_swiat()
	else:
		odswiez_swiat()


# ===================================================================== nowa rozgrywka
func nowy_stan(rozdzial: int, gracze: Array, tryb_gry: String, trudnosc := 1) -> Dictionary:
	## gracze: [{imie, rod}] – 1 gracz w kampanii, 2–4 w trybie wieloosobowym.
	var r: Dictionary = D.rozdzialy[rozdzial]
	var tr: Dictionary = D.trudnosci[trudnosc]
	var st := {
		"wersja": WERSJA, "rozdzial": rozdzial, "tura": 1, "tryb": tryb_gry, "trudnosc": trudnosc,
		"aktywny": 0, "mapa": r.mapa.duplicate(), "budynki": [], "zagony": [], "znalezione": [],
		"pytania_uzyte": [], "dziennik": [], "koniec": false, "zwyciezca": -1, "nr_zagonu": 0,
	}
	var lista := []
	for i in gracze.size():
		var gr: Dictionary = gracze[i]
		var zas := {}
		for k in r.zasoby:
			zas[k] = int(round(r.zasoby[k] * tr.zasoby))
		var techy: Array = r.get("techy_start", []).duplicate()
		lista.append({
			"imie": gr.imie, "rod": int(gr.rod), "zasoby": zas, "techy": techy, "talia": r.talia.duplicate(),
			"chwala": 0, "cele_ok": [], "bitwa": false, "wydarzenia": [], "inflacja": int(r.get("inflacja", 0)),
			"rekrut": 0, "przechwyt": 0, "glod": false, "stat": {"pyt_ok": 0, "pyt_all": 0, "budowy": 0, "bitwy": 0},
			"techy_proby": {}, "start": r.start[i], "odlaczony": false, "obrona": 0,
		})
		var x: int = r.start[i][0]
		var y: int = r.start[i][1]
		var typ := "chata" if r.epoka == "krolestwo" else "domus"
		st.budynki.append({"typ": typ, "x": x, "y": y, "wl": i, "gotowy": true, "siedziba": true})
	st["gracze"] = lista
	return st


func rozpocznij_rozdzial(rozdzial: int, gracze: Array, tryb_gry: String, trudnosc := 1) -> void:
	S = nowy_stan(rozdzial, gracze, tryb_gry, trudnosc)
	R = D.rozdzialy[rozdzial]
	zbuduj_swiat()
	scena = "gra"
	if tryb == "":
		zapisz()
		ui.pokaz_ekran()
		_po_rozpoczeciu_tury()


func nowa_kampania(trudnosc: int) -> void:
	K = {"ukonczone": [], "wyniki": {}, "trudnosc": trudnosc, "imie": "Damian"}
	zapisz_kampanie()
	przejdz_do_rozdzialu(0)


func przejdz_do_rozdzialu(i: int) -> void:
	## Mapa imperium -> wstęp kronikarza -> rozgrywka.
	R = D.rozdzialy[i]
	var start := func():
		scena = "intro"
		ui.intro_rozdzial = i
		ui.pokaz_ekran()
	pokaz_mape(i, start)


func zacznij_po_intro(i: int) -> void:
	rozpocznij_rozdzial(i, [{"imie": "Damian", "rod": 0}], "kampania", int(K.get("trudnosc", 1)))


# ===================================================================== mapa imperium
var mapa_rozdzial := 0
var mapa_koniec := Callable()


func pokaz_mape(rozdzial: int, na_koniec: Callable) -> void:
	if tryb == "test":
		na_koniec.call()
		return
	mapa_rozdzial = rozdzial
	mapa_koniec = na_koniec
	scena = "mapa"
	graj_muzyke("menu")
	ui.pokaz_ekran()


func zakoncz_mape() -> void:
	ucisz_lektora()
	var cb := mapa_koniec
	mapa_koniec = Callable()
	if cb.is_valid():
		cb.call()


func pokaz_tytul() -> void:
	scena = "tytul"
	S = {}
	_wyczysc(swiat.get_node("teren"))
	graj_muzyke("menu")
	_kamera_tytulowa()
	ui.pokaz_ekran()


func _kamera_tytulowa() -> void:
	kamera.position = Vector3(0, 6, 20)
	kamera.look_at(Vector3(0, 2, 0))


# ===================================================================== pomocnicze zasad
func gr(p := -1) -> Dictionary:
	return S.gracze[S.aktywny if p < 0 else p]


func moja_tura() -> bool:
	if S.is_empty():
		return false
	if S.tryb == "online":
		return int(S.aktywny) == moj_gracz
	return true


func teren(x: int, y: int) -> String:
	if x < 0 or y < 0 or x >= N or y >= N:
		return ""
	return S.mapa[y][x]


func ma_tech(p: int, id: String) -> bool:
	return id in gr(p).techy


func budynek_na(x: int, y: int) -> int:
	for i in S.budynki.size():
		var b = S.budynki[i]
		if int(b.x) == x and int(b.y) == y:
			return i
	return -1


func ile_budynkow(p: int, typ: String, tylko_gotowe := false) -> int:
	var n := 0
	for b in S.budynki:
		if int(b.wl) == p and b.typ == typ and (b.gotowy or not tylko_gotowe):
			n += 1
	return n


func zajete_dekoracja(x: int, y: int) -> bool:
	for z in R.zabytki:
		if int(z[0]) == x and int(z[1]) == y:
			return true
	for o in R.obozy:
		if absi(int(o[0]) - x) <= 1 and absi(int(o[1]) - y) <= 1:
			return true
	return false


func przelicz_wlasnosc() -> void:
	## Pole należy do gracza z najbliższym budynkiem (zasięg 2, siedziba 3). Remis = niczyje.
	wlasciciel = []
	for y in N:
		var w := []
		w.resize(N)
		w.fill(-1)
		wlasciciel.append(w)
	var najb := []
	for y in N:
		var w := []
		w.resize(N)
		w.fill(99)
		najb.append(w)
	for b in S.budynki:
		var zas := 3 if b.get("siedziba", false) else 2
		var bx: int = int(b.x)
		var by: int = int(b.y)
		var p: int = int(b.wl)
		for y in range(by - zas, by + zas + 1):
			for x in range(bx - zas, bx + zas + 1):
				if x < 0 or y < 0 or x >= N or y >= N:
					continue
				var d: int = maxi(absi(x - bx), absi(y - by))
				if d < najb[y][x]:
					najb[y][x] = d
					wlasciciel[y][x] = p
				elif d == najb[y][x] and wlasciciel[y][x] != p:
					wlasciciel[y][x] = -2
	for y in N:
		for x in N:
			if wlasciciel[y][x] == -2:
				wlasciciel[y][x] = -1


func wlasc(x: int, y: int) -> int:
	if wlasciciel.is_empty() or x < 0 or y < 0 or x >= N or y >= N:
		return -1
	return wlasciciel[y][x]


func mnoznik_inflacji(p: int) -> float:
	return 1.0 + 0.3 * float(gr(p).inflacja)


func koszt_budynku(p: int, typ: String) -> Dictionary:
	var b: Dictionary = D.budynki[typ]
	var n := ile_budynkow(p, typ)
	var k := {}
	for z in b.koszt:
		var v: float = float(b.koszt[z]) * pow(1.25, n)
		if z == "kamien" and ma_tech(p, "beton"):
			v *= 0.8
		if z == "denary":
			v *= mnoznik_inflacji(p)
		k[z] = int(ceil(v))
	return k


func koszt_karty(p: int, id: String) -> Dictionary:
	var c: Dictionary = D.karty[id]
	var k := {}
	for z in c.get("koszt", {}):
		var v: float = float(c.koszt[z])
		if z == "denary":
			v *= mnoznik_inflacji(p)
		k[z] = int(ceil(v))
	return k


func koszt_techu(p: int, id: String) -> Dictionary:
	var c: Dictionary = D.technologie[id]
	var k := {}
	for z in c.koszt:
		var v: float = float(c.koszt[z])
		if z == "denary":
			v *= mnoznik_inflacji(p)
		k[z] = int(ceil(v))
	return k


func stac(p: int, koszt: Dictionary) -> bool:
	for z in koszt:
		if int(gr(p).zasoby.get(z, 0)) < int(koszt[z]):
			return false
	return true


func zaplac(p: int, koszt: Dictionary, mnoznik := 1.0) -> void:
	for z in koszt:
		gr(p).zasoby[z] = maxi(0, int(gr(p).zasoby[z]) - int(ceil(koszt[z] * mnoznik)))


func koszt_tekst(koszt: Dictionary) -> String:
	var s := []
	for z in koszt:
		s.append("%d %s" % [koszt[z], D.zasoby[z].nazwa.to_lower()])
	return ", ".join(s) if s.size() > 0 else "za darmo"


func dostepny_budynek(p: int, typ: String) -> Array:
	## [czy_dostępny, powód]
	var b: Dictionary = D.budynki[typ]
	if not R.epoka in b.epoki:
		return [false, "Nie w tej epoce"]
	if b.has("wymaga") and not ma_tech(p, b.wymaga):
		return [false, "Wymaga: " + D.technologie[b.wymaga].nazwa]
	if b.has("limit") and ile_budynkow(p, typ) >= int(b.limit):
		return [false, "Tylko %d" % int(b.limit)]
	return [true, ""]


func lista_budynkow() -> Array:
	var w := []
	for typ in D.budynki:
		if R.epoka in D.budynki[typ].epoki:
			w.append(typ)
	return w


func moze_budowac(p: int, typ: String, x: int, y: int) -> Array:
	## [bool, powód]
	var dost := dostepny_budynek(p, typ)
	if not dost[0]:
		return dost
	var b: Dictionary = D.budynki[typ]
	var tr := teren(x, y)
	if tr == "":
		return [false, "Poza mapą"]
	if wlasc(x, y) != p:
		return [false, "To nie twoja ziemia – buduj w granicach (żółta linia)"]
	if budynek_na(x, y) >= 0 or zajete_dekoracja(x, y) or zagon_na(x, y) >= 0:
		return [false, "Pole zajęte"]
	if not tr in str(b.teren):
		return [false, "Zły teren: %s (potrzeba: %s)" % [D.teren[tr].nazwa, _nazwy_terenow(str(b.teren))]]
	if b.has("obok"):
		var ok := false
		for dy in [-1, 0, 1]:
			for dx in [-1, 0, 1]:
				if (dx != 0 or dy != 0) and teren(x + dx, y + dy) in str(b.obok):
					ok = true
		if not ok:
			return [false, "Musi stać obok: " + _nazwy_terenow(str(b.obok))]
	if not stac(p, koszt_budynku(p, typ)):
		return [false, "Brak surowców: " + koszt_tekst(koszt_budynku(p, typ))]
	return [true, ""]


func _nazwy_terenow(znaki: String) -> String:
	var w := []
	for c in znaki:
		if D.teren.has(c):
			w.append(D.teren[c].nazwa.to_lower())
	return ", ".join(w)


# ===================================================================== akcje gracza
func akcja_buduj(typ: String, x: int, y: int) -> bool:
	var p: int = S.aktywny
	var m := moze_budowac(p, typ, x, y)
	if not m[0]:
		ui.toast(m[1])
		dzwiek("blad")
		return false
	zaplac(p, koszt_budynku(p, typ))
	S.budynki.append({"typ": typ, "x": x, "y": y, "wl": p, "gotowy": false})
	gr(p).stat.budowy += 1
	dzwiek("buduj")
	_sprawdz_znajdzki(p)
	po_akcji()
	return true


func akcja_rozbierz(x: int, y: int) -> void:
	var i := budynek_na(x, y)
	if i < 0 or int(S.budynki[i].wl) != S.aktywny or S.budynki[i].get("siedziba", false):
		return
	S.budynki.remove_at(i)
	po_akcji()


func akcja_tech(id: String, dobrze: bool) -> void:
	## Wynik zagadki technologicznej: dobrze – technologia zdobyta, źle – strata połowy kosztu.
	var p: int = S.aktywny
	var k := koszt_techu(p, id)
	if dobrze:
		zaplac(p, k)
		gr(p).techy.append(id)
		gr(p).chwala += 3
		gr(p).stat.pyt_ok += 1
		_efekt_techu(p, id)
		dziennik("%s: odkrycie – %s" % [gr(p).imie, D.technologie[id].nazwa])
	else:
		zaplac(p, k, 0.5)
		gr(p).techy_proby[id] = int(S.tura)
	gr(p).stat.pyt_all += 1
	po_akcji()


func _efekt_techu(p: int, id: String) -> void:
	var e: String = D.technologie[id].efekt
	if e == "osusz":
		for y in N:
			var w: String = S.mapa[y]
			S.mapa[y] = w.replace("b", ".")
	elif e == "solidus":
		gr(p).inflacja = 0


func mozna_tech(p: int, id: String) -> Array:
	var tch: Dictionary = D.technologie[id]
	if ma_tech(p, id):
		return [false, "Już znasz"]
	if int(gr(p).techy_proby.get(id, -1)) == int(S.tura):
		return [false, "Spróbuj w następnej turze"]
	if not stac(p, koszt_techu(p, id)):
		return [false, "Brak: " + koszt_tekst(koszt_techu(p, id))]
	return [true, ""]


func lista_techow() -> Array:
	## Technologie bieżącej i wcześniejszych epok.
	var kol := ["krolestwo", "republika", "cesarstwo", "schylek"]
	var e := kol.find(R.epoka)
	var w := []
	for id in D.technologie:
		if kol.find(D.technologie[id].epoka) <= e:
			w.append(id)
	return w


func karty_do_werbunku(p: int) -> Array:
	var w := []
	for id in D.karty:
		var c: Dictionary = D.karty[id]
		if c.frakcja != "rzym" or not R.epoka in c.get("epoki", []):
			continue
		if c.has("wymaga") and not ma_tech(p, c.wymaga):
			continue
		w.append(id)
	return w


func limit_werbunku(p: int) -> int:
	return ile_budynkow(p, "koszary", true) + (1 if ma_tech(p, "tetrarchia") else 0)


func akcja_werbuj(id: String) -> bool:
	var p: int = S.aktywny
	if int(gr(p).rekrut) >= limit_werbunku(p):
		ui.toast("Brak wolnych koszar w tej turze (zbuduj koszary)")
		dzwiek("blad")
		return false
	var k := koszt_karty(p, id)
	if not stac(p, k):
		ui.toast("Brak surowców: " + koszt_tekst(k))
		dzwiek("blad")
		return false
	zaplac(p, k)
	gr(p).talia.append(id)
	gr(p).rekrut += 1
	dzwiek("tarcza")
	po_akcji()
	return true


func akcja_zwolnij(i: int) -> void:
	var p: int = S.aktywny
	if gr(p).talia.size() <= 3:
		ui.toast("Musisz mieć przynajmniej 3 oddziały")
		return
	gr(p).talia.remove_at(i)
	po_akcji()


func akcja_wydarzenie(id: String, opcja: int) -> void:
	var p: int = S.aktywny
	var op: Dictionary = D.wydarzenia[id].opcje[opcja]
	_zastosuj_efekt(p, op.efekt)
	gr(p).wydarzenia.append(id)
	if op.get("historia", false):
		gr(p).chwala += 1
	dziennik("%s: %s – %s" % [gr(p).imie, D.wydarzenia[id].tytul, op.tekst])
	po_akcji()


func _zastosuj_efekt(p: int, e: Dictionary) -> void:
	for k in e:
		var v = e[k]
		if D.zasoby.has(k):
			gr(p).zasoby[k] = maxi(0, int(gr(p).zasoby[k]) + int(v))
		elif k == "chwala":
			gr(p).chwala = maxi(0, int(gr(p).chwala) + int(v))
		elif k == "karta":
			gr(p).talia.append(v)
		elif k == "inflacja":
			if not ma_tech(p, "solidus"):
				gr(p).inflacja += int(v)
		elif k == "obrona":
			gr(p).obrona += int(v)
		elif k == "ludnosc":
			gr(p)["ludnosc_mod"] = int(gr(p).get("ludnosc_mod", 0)) + int(v)
		elif k == "wrog":
			# sąsiedzi się zbroją – kolejny zagon wcześniej
			_wyslij_zagon(int(v))


func akcja_znajdzka(x: int, y: int) -> void:
	var p: int = S.aktywny
	var klucz := "%d,%d" % [x, y]
	if klucz in S.znalezione:
		return
	for z in R.znajdzki:
		if int(z[0]) == x and int(z[1]) == y:
			S.znalezione.append(klucz)
			gr(p).chwala += 3
			dzwiek("przedmiot")
			ui.pokaz_znajdzke(z[2])
			po_akcji()
			return


func _sprawdz_znajdzki(p: int) -> void:
	pass


func akcja_bitwa_wynik(wygrana: bool, pyt_ok: int, pyt_all: int) -> void:
	var p: int = S.aktywny
	gr(p).stat.bitwy += 1
	gr(p).stat.pyt_ok += pyt_ok
	gr(p).stat.pyt_all += pyt_all
	if wygrana:
		gr(p).bitwa = true
		gr(p).chwala += 15
		dziennik("%s wygrywa: %s!" % [gr(p).imie, R.bitwa.nazwa])
		if S.tryb != "kampania" and int(S.zwyciezca) < 0:
			S.zwyciezca = p
			gr(p).chwala += 10
	else:
		gr(p).chwala = maxi(0, int(gr(p).chwala) - 5)
		gr(p)["bitwa_tura"] = int(S.tura)
	po_akcji()


func mozna_bitwe(p: int) -> Array:
	if gr(p).bitwa:
		return [false, "Bitwa wygrana!"]
	for c in R.cele:
		if c.typ != "bitwa" and not stan_celu(p, c)[0]:
			return [false, "Najpierw wykonaj pozostałe zadania"]
	if int(gr(p).get("bitwa_tura", -1)) == int(S.tura):
		return [false, "Wojsko odpoczywa – spróbuj w następnej turze"]
	return [true, ""]


# ===================================================================== zagony wroga
func zagon_na(x: int, y: int) -> int:
	for i in S.zagony.size():
		if int(S.zagony[i].x) == x and int(S.zagony[i].y) == y:
			return i
	return -1


func _wyslij_zagon(dodatkowa_sila := 0) -> void:
	if R.obozy.is_empty():
		return
	var o: Array = R.obozy[int(S.nr_zagonu) % R.obozy.size()]
	S.nr_zagonu = int(S.nr_zagonu) + 1
	var tr: Dictionary = D.trudnosci[int(S.trudnosc)]
	var sila := int(round((float(R.zagony.sila) + int(S.tura) / 10 + dodatkowa_sila) * tr.wrog))
	var x: int = int(o[0])
	var y: int = int(o[1]) + 2
	if teren(x, y) in ["", "m", "g"]:
		y = int(o[1])
	S.zagony.append({"x": x, "y": y, "sila": sila, "model": R.zagony.model, "nazwa": R.zagony.nazwa, "id": int(S.nr_zagonu)})
	dziennik("%s wyrusza z obozu (siła %d)!" % [R.zagony.nazwa, sila])


func _cel_zagonu(z: Dictionary) -> Vector2i:
	var najl := Vector2i(-1, -1)
	var dmin := 9999
	for b in S.budynki:
		var d: int = maxi(absi(int(b.x) - int(z.x)), absi(int(b.y) - int(z.y)))
		if d < dmin:
			dmin = d
			najl = Vector2i(int(b.x), int(b.y))
	return najl


func _krok_zagonu(z: Dictionary) -> Vector2i:
	var cel := _cel_zagonu(z)
	if cel.x < 0:
		return Vector2i(int(z.x), int(z.y))
	var najl := Vector2i(int(z.x), int(z.y))
	var dmin := 99999.0
	for dy in [-1, 0, 1]:
		for dx in [-1, 0, 1]:
			if dx == 0 and dy == 0:
				continue
			var nx: int = int(z.x) + dx
			var ny: int = int(z.y) + dy
			var tr := teren(nx, ny)
			if tr in ["", "m", "g"]:
				continue
			var d := Vector2(nx - cel.x, ny - cel.y).length() + (0.6 if tr == "~" else 0.0)
			if d < dmin:
				dmin = d
				najl = Vector2i(nx, ny)
	return najl


func chroniony(x: int, y: int, p: int) -> bool:
	var zas := 3 if ma_tech(p, "limes") else 2
	zas += int(gr(p).obrona)
	for b in S.budynki:
		if b.typ == "mury" and b.gotowy and int(b.wl) == p and maxi(absi(int(b.x) - x), absi(int(b.y) - y)) <= zas:
			return true
	return false


func _ruch_zagonow() -> void:
	var kom := []
	var i := 0
	while i < S.zagony.size():
		var z: Dictionary = S.zagony[i]
		var krok := 2 if R.zagony.model in ["hun", "ekwita"] else 1
		var usuniety := false
		for k in krok:
			var nast := _krok_zagonu(z)
			var bi := budynek_na(nast.x, nast.y)
			if bi >= 0:
				var b: Dictionary = S.budynki[bi]
				var p: int = int(b.wl)
				if chroniony(nast.x, nast.y, p):
					gr(p).chwala += 2
					kom.append([p, "Mury odparły zagon: %s! +2 chwały" % z.nazwa])
				elif b.get("siedziba", false):
					var strata := mini(int(gr(p).zasoby.denary), 6)
					gr(p).zasoby.denary -= strata
					gr(p).zasoby.zboze = maxi(0, int(gr(p).zasoby.zboze) - 4)
					kom.append([p, "%s splądrował twoją siedzibę: –%d denarów, –4 zboża!" % [z.nazwa, strata]])
				else:
					S.budynki.remove_at(bi)
					kom.append([p, "%s spalił budynek: %s!" % [z.nazwa, D.budynki[b.typ].nazwa]])
				S.zagony.remove_at(i)
				usuniety = true
				break
			z.x = nast.x
			z.y = nast.y
		if not usuniety:
			i += 1
	for k in kom:
		dziennik(k[1])
		S.dziennik.append({"dla": k[0], "tekst": k[1]})


func przechwyc(i: int) -> Dictionary:
	## Szybka potyczka z zagonem. Zwraca {wygrana, moja, wroga}.
	var p: int = S.aktywny
	var z: Dictionary = S.zagony[i]
	var sily := []
	for c in gr(p).talia:
		sily.append(sila_karty(p, c))
	sily.sort()
	sily.reverse()
	var najl := 0
	for j in mini(3, sily.size()):
		najl += sily[j]
	var moja: int = int(round(najl / 3.0)) + rng.randi_range(1, 6)
	var wroga: int = int(z.sila) + rng.randi_range(1, 6)
	var wynik := {"wygrana": moja >= wroga, "moja": moja, "wroga": wroga}
	gr(p).przechwyt = int(gr(p).przechwyt) + 1
	if wynik.wygrana:
		S.zagony.remove_at(i)
		gr(p).zasoby.denary += 3
		gr(p).chwala += 2
		dzwiek("miecz")
	else:
		if gr(p).talia.size() > 3:
			gr(p).talia.remove_at(rng.randi_range(0, gr(p).talia.size() - 1))
		dzwiek("zle")
	po_akcji()
	return wynik


func sila_karty(p: int, id: String) -> int:
	var c: Dictionary = D.karty[id]
	var s: int = int(c.sila)
	if c.frakcja == "rzym" and p >= 0:
		if c.typ == "piechota" and ma_tech(p, "falanga"):
			s += 1
		if id == "legionisci" and ma_tech(p, "reforma_mariusza"):
			s += 1
	return s


# ===================================================================== ekonomia
func produkcja(p: int) -> Dictionary:
	var w := {"zboze": 0, "drewno": 0, "kamien": 0, "denary": 0, "chwala": 0, "mieszkancy": 0, "prac": 0, "eff": 1.0, "jedzenie": 0}
	var akw := ile_budynkow(p, "akwedukt", true)
	var surowe := {"zboze": 0.0, "drewno": 0.0, "kamien": 0.0, "denary": 0.0}
	var miesz := 0.0
	for b in S.budynki:
		if int(b.wl) != p or not b.gotowy:
			continue
		var d: Dictionary = D.budynki[b.typ]
		miesz += float(d.get("mieszkancy", 0)) * (1.0 + 0.25 * akw)
		w.prac += int(d.get("prac", 0))
		w.chwala += int(d.get("chwala", 0))
		for z in d.daje:
			surowe[z] += float(d.daje[z])
		var tr := teren(int(b.x), int(b.y))
		for z in d.get("premia_na", {}).get(tr, {}):
			surowe[z] += float(d.premia_na[tr][z])
		for zn in d.get("premia_obok", {}):
			var obok := false
			for dy in [-1, 0, 1]:
				for dx in [-1, 0, 1]:
					if teren(int(b.x) + dx, int(b.y) + dy) == zn:
						obok = true
			if obok:
				for z in d.premia_obok[zn]:
					surowe[z] += float(d.premia_obok[zn][z])
		if b.typ == "pole":
			surowe.zboze += (1.0 if ma_tech(p, "kalendarz_numy") else 0.0) + (1.0 if ma_tech(p, "kalendarz_julianski") else 0.0)
		if b.typ == "targ" and ma_tech(p, "drogi"):
			surowe.denary += 1.0
		if b.typ == "port" and ma_tech(p, "corvus"):
			surowe.denary += 1.0
		if b.typ == "kuria" and ma_tech(p, "prawo_rzymskie"):
			surowe.denary += 1.0
	miesz += float(gr(p).get("ludnosc_mod", 0))
	w.mieszkancy = maxi(0, int(miesz))
	if w.prac > 0:
		w.eff = clampf(float(w.mieszkancy) / float(w.prac), 0.25, 1.0)
	if gr(p).get("glod", false):
		w.eff *= 0.5
	for z in surowe:
		w[z] = int(floor(surowe[z] * w.eff + 0.001))
	w.chwala += (1 if ma_tech(p, "prawo12") else 0) + (1 if ma_tech(p, "prawo_rzymskie") else 0)
	var baza := BAZA_TALII + (2 if ma_tech(p, "reforma_mariusza") else 0)
	w.jedzenie = int(ceil(w.mieszkancy / 5.0)) + maxi(0, gr(p).talia.size() - baza)
	return w


func _koniec_tury_gracza(p: int) -> void:
	# ukończenie budów
	for b in S.budynki:
		if int(b.wl) == p and not b.gotowy:
			b.gotowy = true
			gr(p).chwala += 1
	var w := produkcja(p)
	for z in ["zboze", "drewno", "kamien", "denary"]:
		gr(p).zasoby[z] = int(gr(p).zasoby[z]) + int(w[z])
	gr(p).chwala += int(w.chwala)
	gr(p).zasoby.zboze = int(gr(p).zasoby.zboze) - int(w.jedzenie)
	gr(p).glod = false
	if int(gr(p).zasoby.zboze) < 0:
		gr(p).zasoby.zboze = 0
		gr(p).glod = true
		var baza := BAZA_TALII + (2 if ma_tech(p, "reforma_mariusza") else 0)
		if gr(p).talia.size() > baza:
			gr(p).talia.pop_back()
			S.dziennik.append({"dla": p, "tekst": "Głód! Jeden oddział zdezerterował, a budynki pracują wolniej."})
		else:
			S.dziennik.append({"dla": p, "tekst": "Głód! Budynki pracują o połowę wolniej. Zbuduj pola!"})
	gr(p).rekrut = 0
	gr(p).przechwyt = 0
	_aktualizuj_cele(p)


func _aktualizuj_cele(p: int) -> void:
	for i in R.cele.size():
		var c: Dictionary = R.cele[i]
		if i in gr(p).cele_ok:
			continue
		if _cel_spelniony(p, c):
			gr(p).cele_ok.append(i)
			gr(p).chwala += 5


func _cel_spelniony(p: int, c: Dictionary) -> bool:
	match c.typ:
		"buduj":
			return ile_budynkow(p, c.co, true) >= int(c.ile)
		"tech":
			return ma_tech(p, c.co)
		"zasob":
			return int(gr(p).zasoby[c.co]) >= int(c.ile)
		"chwala":
			return int(gr(p).chwala) >= int(c.ile)
		"bitwa":
			return gr(p).bitwa
	return false


func stan_celu(p: int, c: Dictionary) -> Array:
	## [zrobione, opis z postępem]
	var i: int = R.cele.find(c)
	var ok: bool = (i in gr(p).cele_ok) or _cel_spelniony(p, c)
	var op: String = c.get("opis", "")
	match c.typ:
		"buduj":
			if op == "":
				op = "Zbuduj: %s" % D.budynki[c.co].nazwa
			op += " (%d/%d)" % [mini(ile_budynkow(p, c.co, true), int(c.ile)), int(c.ile)]
		"tech":
			if op == "":
				op = "Odkryj: %s" % D.technologie[c.co].nazwa
		"zasob":
			if op == "":
				op = "Zgromadź: %s" % D.zasoby[c.co].nazwa
			op += " (%d/%d)" % [mini(int(gr(p).zasoby[c.co]), int(c.ile)), int(c.ile)] if not ok else ""
		"chwala":
			op += " (%d/%d)" % [mini(int(gr(p).chwala), int(c.ile)), int(c.ile)] if not ok else ""
		"bitwa":
			op = "Bitwa: %s (%s)" % [R.bitwa.nazwa, R.bitwa.rok]
	return [ok, op]


func rozdzial_ukonczony(p: int) -> bool:
	for c in R.cele:
		if not stan_celu(p, c)[0]:
			return false
	return true


func akcja_koniec_tury() -> void:
	if S.koniec:
		return
	var p: int = S.aktywny
	_koniec_tury_gracza(p)
	dzwiek("tura")
	# kampania: rozdział ukończony
	if S.tryb == "kampania" and rozdzial_ukonczony(p):
		_zakoncz_rozdzial()
		return
	# następny gracz
	var nast: int = (p + 1) % S.gracze.size()
	if nast == 0:
		_nowa_runda()
	S.aktywny = nast
	if S.koniec:
		po_akcji()
		_pokaz_koniec()
		return
	po_akcji(true)
	_po_rozpoczeciu_tury()


func _nowa_runda() -> void:
	S.tura = int(S.tura) + 1
	_ruch_zagonow()
	var tr: Dictionary = D.trudnosci[int(S.trudnosc)]
	var od: int = int(round(float(R.zagony.od) * tr.zagony))
	var co: int = maxi(3, int(round(float(R.zagony.co) * tr.zagony)))
	if int(S.tura) >= od and (int(S.tura) - od) % co == 0:
		_wyslij_zagon()
	# koniec gry wieloosobowej: limit tur albo ktoś wygrał bitwę i runda się domknęła
	if S.tryb != "kampania":
		if int(S.zwyciezca) >= 0 or int(S.tura) > int(R.tury):
			S.koniec = true
	elif int(S.tura) > int(R.tury) + 10:
		pass


func _po_rozpoczeciu_tury() -> void:
	## Początek tury aktywnego gracza: wiadomości, wydarzenia (dylematy), losowe zdarzenia.
	if tryb != "" or S.is_empty() or S.koniec:
		return
	if not moja_tura():
		ui.pokaz_ekran()
		return
	var p: int = S.aktywny
	if gr(p).odlaczony:
		akcja_koniec_tury()
		return
	if S.tryb == "hotseat":
		scena = "przekazanie"
		ui.pokaz_ekran()
		return
	_rozpocznij_ture_gracza()


func _rozpocznij_ture_gracza() -> void:
	var p: int = S.aktywny
	scena = "gra"
	ui.pokaz_ekran()
	_kamera_na_siedzibe(p)
	var kolejka := []
	for d in S.dziennik:
		if typeof(d) == TYPE_DICTIONARY and int(d.dla) == p:
			kolejka.append({"typ": "wiadomosc", "tekst": d.tekst})
	var nowy := []
	for d in S.dziennik:
		if not (typeof(d) == TYPE_DICTIONARY and int(d.dla) == p):
			nowy.append(d)
	S.dziennik = nowy
	# dylematy z rozdziału: w turze 3 i 12
	var wyd: Array = R.wydarzenia
	for j in wyd.size():
		var tura_wyd := 3 if j == 0 else 11
		if int(S.tura) >= tura_wyd and not wyd[j] in gr(p).wydarzenia:
			kolejka.append({"typ": "wydarzenie", "id": wyd[j]})
			break
	# zdarzenie losowe
	if int(S.tura) > 3 and rng.randf() < 0.18:
		var l: Dictionary = D.losowe[rng.randi_range(0, D.losowe.size() - 1)]
		_zastosuj_efekt(p, l.efekt)
		kolejka.append({"typ": "losowe", "dane": l})
	ui.kolejka_okien(kolejka)
	if R.cele.size() > 0 and int(S.tura) == 1 and S.tryb == "kampania":
		ui.rada(D.rady[0])


func _zakoncz_rozdzial() -> void:
	var p: int = 0
	var wynik := {"chwala": int(gr(p).chwala), "tury": int(S.tura), "gwiazdki": gwiazdki()}
	var id: String = R.id
	var stary: Dictionary = K.wyniki.get(id, {})
	if stary.is_empty() or int(stary.chwala) < wynik.chwala:
		K.wyniki[id] = wynik
	if not id in K.ukonczone:
		K.ukonczone.append(id)
	zapisz_kampanie()
	S.koniec = true
	if FileAccess.file_exists(ZAPIS) and tryb == "":
		DirAccess.remove_absolute(ProjectSettings.globalize_path(ZAPIS))
	scena = "koniec"
	dzwiek("fanfara")
	ui.pokaz_ekran()


func gwiazdki() -> int:
	var t_: int = int(S.tura)
	var lim: int = int(R.tury)
	if t_ <= int(lim * 0.7):
		return 3
	if t_ <= lim:
		return 2
	return 1


func _pokaz_koniec() -> void:
	scena = "koniec_mp"
	dzwiek("fanfara")
	ui.pokaz_ekran()


func ranking() -> Array:
	var w := []
	for i in S.gracze.size():
		w.append([int(S.gracze[i].chwala) + int(S.gracze[i].cele_ok.size()) * 0, i])
	w.sort()
	w.reverse()
	return w


func dalej_po_rozdziale() -> void:
	var i: int = int(S.rozdzial)
	S = {}
	if i + 1 >= D.rozdzialy.size():
		scena = "final"
		graj_muzyke("upadek")
		ui.pokaz_ekran()
	else:
		przejdz_do_rozdzialu(i + 1)


func dziennik(tekst: String) -> void:
	S.dziennik.append(tekst)
	if S.dziennik.size() > 60:
		S.dziennik.pop_front()


func po_akcji(nowa_tura := false) -> void:
	## Po każdej zmianie stanu: cele, świat, interfejs, zapis, wysłanie stanu w sieci.
	if S.is_empty():
		return
	_aktualizuj_cele(int(S.aktywny))
	if tryb == "test":
		przelicz_wlasnosc()
		return
	if str(S.mapa.hash()) != mapa_hash:
		zbuduj_swiat()
	else:
		odswiez_swiat()
	ui.odswiez()
	zapisz()
	if S.tryb == "online":
		siec.wyslij_stan(S)


func moj_gracz_tymczasowo(nr: int) -> void:
	## Host kończy turę rozłączonego gracza.
	if S.is_empty() or int(S.aktywny) != nr:
		return
	var stary := moj_gracz
	moj_gracz = nr
	akcja_koniec_tury()
	moj_gracz = stary


func odebrano_stan(nowy: Dictionary) -> void:
	## Stan z sieci (inny gracz wykonał ruch).
	var bylo_moje := moja_tura()
	var stara_tura: int = int(S.get("aktywny", -1)) if not S.is_empty() else -1
	ustaw_stan(nowy)
	if scena in ["lobby", "tytul", "mapa", "intro"]:
		scena = "gra"
		ui.pokaz_ekran()
		_kamera_na_siedzibe(maxi(moj_gracz, 0))
	if S.koniec:
		_pokaz_koniec()
		return
	ui.odswiez()
	if siec.host and gr().get("odlaczony", false):
		moj_gracz_tymczasowo(int(S.aktywny))
		return
	if moja_tura() and (not bylo_moje or stara_tura != int(S.aktywny)):
		dzwiek("tura")
		_rozpocznij_ture_gracza()


# ===================================================================== świat 3D
func pozycja(x: float, y: float) -> Vector3:
	return Vector3((x + 0.5) * T, wysokosc(int(x), int(y)), (y + 0.5) * T)


func wysokosc(x: int, y: int) -> float:
	var c := teren(x, y)
	if c == "":
		return 0.0
	return float(D.teren[c].h)


func _wyczysc(w: Node) -> void:
	for c in w.get_children():
		c.queue_free()


func scena_modelu(nazwa: String) -> PackedScene:
	if _sceny.has(nazwa):
		return _sceny[nazwa]
	var s := "res://modele/%s.glb" % nazwa
	var ps: PackedScene = load(s) if ResourceLoader.exists(s) else null
	_sceny[nazwa] = ps
	return ps


func instancja(nazwa: String) -> Node3D:
	var ps := scena_modelu(nazwa)
	if ps:
		return ps.instantiate()
	# model zastępczy (gdy brak pliku)
	var mi := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(1.2, 1.2, 1.2)
	mi.mesh = bm
	mi.position.y = 0.6
	var n := Node3D.new()
	n.add_child(mi)
	return n


func etykieta(tekst: String, rozmiar := 64, kolor := Color.WHITE) -> Label3D:
	var l := Label3D.new()
	l.text = tekst
	l.font_size = rozmiar
	l.pixel_size = 0.006
	l.modulate = kolor
	l.outline_size = 14
	l.outline_modulate = Color(0.1, 0.06, 0.04, 0.9)
	l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.no_depth_test = true
	l.render_priority = 5
	return l


func zbuduj_swiat() -> void:
	if S.is_empty():
		return
	R = D.rozdzialy[int(S.rozdzial)]
	mapa_hash = str(S.mapa.hash())
	_ustaw_klimat(R.epoka)
	graj_muzyke(D.epoki[R.epoka].muzyka)
	for w in [teren_wezel, dekor_wezel, bud_wezel, zagon_wezel]:
		_wyczysc(w)
	_bud_wezly = {}
	_zag_wezly = {}
	_znajdzki_wezly = {}
	_postacie = []
	_statki = []
	_animowane = []
	_animuj_nowe = false
	_zbuduj_teren()
	_dekoracje()
	odswiez_swiat()
	_animuj_nowe = true


const POZIOM_WODY := -0.18     # lustro wody (ląd ma 0, plaża -0.05, stopa skarpy brzegu -0.3)
const STOPA_BRZEGU := -0.3
const PODZIAL_WODY := 4         # siatka dna i wody: 4 × 4 na pole
var _dno_cache := {}
var woda_mat: ShaderMaterial


func _woda(c: String) -> bool:
	return c == "~" or c == "m"


func _odl_do_ladu(px: float, pz: float) -> float:
	## Odległość punktu (współrzędne świata) od najbliższego pola lądu (w metrach).
	var tx := int(floor(px / T))
	var tz := int(floor(pz / T))
	var najl := 99.0
	for dz in range(-3, 4):
		for dx in range(-3, 4):
			var c := teren(tx + dx, tz + dz)
			if c == "" or _woda(c):
				continue
			var x0 := (tx + dx) * T
			var z0 := (tz + dz) * T
			var ox := maxf(maxf(x0 - px, px - (x0 + T)), 0.0)
			var oz := maxf(maxf(z0 - pz, pz - (z0 + T)), 0.0)
			najl = minf(najl, sqrt(ox * ox + oz * oz))
	return najl


func _dno(px: float, pz: float, morze: bool) -> float:
	## Wysokość dna w punkcie: przy brzegu płytko (stopa skarpy), dalej coraz głębiej.
	var klucz := Vector3i(int(round(px * 8)), int(round(pz * 8)), 1 if morze else 0)
	if _dno_cache.has(klucz):
		return _dno_cache[klucz]
	var d := _odl_do_ladu(px, pz)
	var h: float
	if morze:
		h = STOPA_BRZEGU - smoothstep(0.0, 5.0, d) * 1.25
	else:
		h = STOPA_BRZEGU - smoothstep(0.0, 1.5, d) * 0.7
	_dno_cache[klucz] = h
	return h


func _zbuduj_teren() -> void:
	_dno_cache = {}
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var sw := SurfaceTool.new()      # powierzchnia wody (głębokość w kolorze wierzchołka)
	sw.begin(Mesh.PRIMITIVE_TRIANGLES)
	var jest_woda := false
	var r := RandomNumberGenerator.new()
	r.seed = 7
	var ile_morza := 0
	for y in N:
		for x in N:
			var c := teren(x, y)
			var h := wysokosc(x, y)
			var kol := _kolor_terenu(c)
			var x0 := x * T
			var z0 := y * T
			if _woda(c):
				jest_woda = true
				if c == "m":
					ile_morza += 1
				_dno_i_woda(st, sw, x, y, c == "m")
			else:
				_wierzch_pola(st, x, y, h)
			# ściany boczne między polami o różnej wysokości (brzegi koryta, skarpy wzgórz)
			for kier in [Vector2i(1, 0), Vector2i(0, 1), Vector2i(-1, 0), Vector2i(0, -1)]:
				var nx: int = x + kier.x
				var ny: int = y + kier.y
				var hn := wysokosc(nx, ny) if teren(nx, ny) != "" else -1.6
				if _woda(c) and teren(nx, ny) != "":
					continue
				if hn >= h and not _woda(c):
					continue
				var bok := kol.darkened(0.3)
				bok.a = 0.0
				if not _woda(c) and _woda(teren(nx, ny)):
					bok = Color(0.52, 0.44, 0.32, 0.0)     # ziemista skarpa brzegu
				var a: Vector3
				var b: Vector3
				if kier == Vector2i(1, 0):
					a = Vector3(x0 + T, 0, z0 + T); b = Vector3(x0 + T, 0, z0)
				elif kier == Vector2i(-1, 0):
					a = Vector3(x0, 0, z0); b = Vector3(x0, 0, z0 + T)
				elif kier == Vector2i(0, 1):
					a = Vector3(x0, 0, z0 + T); b = Vector3(x0 + T, 0, z0 + T)
				else:
					a = Vector3(x0 + T, 0, z0); b = Vector3(x0, 0, z0)
				var ha := h
				var hb := h
				if _woda(c):
					ha = _dno(a.x, a.z, c == "m")
					hb = _dno(b.x, b.z, c == "m")
					bok = Color(0.2, 0.24, 0.22, 0.0)
				_quad(st, Vector3(a.x, ha, a.z), Vector3(b.x, hb, b.z), Vector3(b.x, hn, b.z), Vector3(a.x, hn, a.z), bok, Vector3(kier.x, 0, kier.y))
	st.generate_normals()
	var mi := MeshInstance3D.new()
	mi.mesh = st.commit()
	mi.material_override = _material_terenu()
	teren_wezel.add_child(mi)
	siatka_budowy = MeshInstance3D.new()
	siatka_budowy.visible = false
	siatka_budowy.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	teren_wezel.add_child(siatka_budowy)
	# morze poza mapą (rama), żeby wybrzeże nie kończyło się urwiskiem
	var morska := ile_morza > 30
	if morska:
		var rama := 160.0
		var w := N * T
		for q in [Rect2(-rama, -rama, w + 2 * rama, rama), Rect2(-rama, w, w + 2 * rama, rama), Rect2(-rama, 0, rama, w), Rect2(w, 0, rama, w)]:
			var qq: Rect2 = q
			_quad_wody(sw, qq.position.x, qq.position.y, qq.end.x, qq.end.y, 1.0, 1.0, 1.0, 1.0)
	if jest_woda or morska:
		woda = MeshInstance3D.new()
		woda.mesh = sw.commit()
		woda.material_override = _material_wody()
		woda.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		teren_wezel.add_child(woda)
	# podstawa pod mapą (żeby nie było widać pustki)
	var pod := MeshInstance3D.new()
	var pm2 := PlaneMesh.new()
	pm2.size = Vector2(N * T + 400, N * T + 400)
	pod.mesh = pm2
	pod.position = Vector3(N * T / 2, -1.6, N * T / 2)
	var pmat := StandardMaterial3D.new()
	if morska:
		pmat.albedo_color = Color("1f3a40")
	else:
		pmat.albedo_color = Color("2b4a2a") if R.epoka != "schylek" else Color("3a3a2e")
	pod.material_override = pmat
	teren_wezel.add_child(pod)


# ----------------------------------------------------------------- teren: tekstura zamiast szachownicy
# Wierzch pól rysuje shader: trawa w dwóch odcieniach, plamy ziemi i ścieżki mieszane szumem.
# Typy terenu (droga, plaża, wzgórze, bagno…) wtapiają się miękko: kolor i „waga trawy” liczone są
# w narożnikach pól jako średnia sąsiadów na tej samej wysokości (brak twardych krawędzi i szachownicy).
const WAGA_TRAWY := {".": 1.0, "l": 0.8, "o": 0.8, "w": 0.32, "g": 0.0, "p": 0.0, "d": 0.0, "b": 0.3, "~": 0.0, "m": 0.0}
var siatka_budowy: MeshInstance3D
var _mat_terenu: ShaderMaterial


func _kolor_terenu(c: String) -> Color:
	match c:
		"l": return Color("4f6e36")        # ściółka pod drzewami
		"o": return Color("a3a066")        # sucha ziemia gaju
		"w": return Color("b3a46a")        # piaszczyste wzgórze
		"b": return Color("5e7a4c")
	return Color(D.teren[c].kolor)


func _kolor_rogu(cx: int, cy: int, h: float) -> Color:
	## Średni kolor (rgb) i waga trawy (a) pól stykających się w narożniku i leżących na tej samej wysokości.
	var suma := Color(0, 0, 0, 0)
	var n := 0
	for t in [Vector2i(cx - 1, cy - 1), Vector2i(cx, cy - 1), Vector2i(cx - 1, cy), Vector2i(cx, cy)]:
		var c := teren(t.x, t.y)
		if c == "" or _woda(c) or absf(wysokosc(t.x, t.y) - h) > 0.01:
			continue
		var k := _kolor_terenu(c)
		suma += Color(k.r, k.g, k.b, WAGA_TRAWY.get(c, 0.0))
		n += 1
	return suma / maxf(n, 1)


func _wierzch_pola(st: SurfaceTool, x: int, y: int, h: float) -> void:
	var x0 := x * T
	var z0 := y * T
	var pts := [Vector3(x0, h, z0), Vector3(x0 + T, h, z0), Vector3(x0 + T, h, z0 + T), Vector3(x0, h, z0 + T)]
	var kol := [_kolor_rogu(x, y, h), _kolor_rogu(x + 1, y, h), _kolor_rogu(x + 1, y + 1, h), _kolor_rogu(x, y + 1, h)]
	for i in [0, 1, 2, 0, 2, 3]:
		st.set_color(kol[i])
		st.set_normal(Vector3.UP)
		st.add_vertex(pts[i])


func _szum_tekstura(ziarno: int, czest: float, rozmiar := 256) -> NoiseTexture2D:
	var t := NoiseTexture2D.new()
	t.width = rozmiar
	t.height = rozmiar
	t.seamless = true
	var fn := FastNoiseLite.new()
	fn.seed = ziarno
	fn.frequency = czest
	fn.fractal_octaves = 4
	t.noise = fn
	return t


func _material_terenu() -> ShaderMaterial:
	if _mat_terenu == null:
		var sh := Shader.new()
		sh.code = """shader_type spatial;
render_mode diffuse_burley;

uniform sampler2D szum : filter_linear_mipmap, repeat_enable;      // duże plamy
uniform sampler2D szum_drobny : filter_linear_mipmap, repeat_enable; // źdźbła, grudki
uniform vec3 trawa_jasna : source_color = vec3(0.50, 0.68, 0.31);
uniform vec3 trawa_ciemna : source_color = vec3(0.34, 0.53, 0.22);
uniform vec3 ziemia : source_color = vec3(0.45, 0.35, 0.22);
uniform vec3 sciezka : source_color = vec3(0.62, 0.53, 0.37);
uniform float ile_ziemi = 0.62;     // próg plam ziemi (mniej = więcej ziemi)
uniform float ile_sciezek = 1.0;

varying vec3 swiat;

void vertex() {
	swiat = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 p = swiat.xz;
	float n1 = texture(szum, p * 0.018).r;
	float n2 = texture(szum, p * 0.055 + vec2(0.37, 0.71)).r;
	float d = texture(szum_drobny, p * 0.45).r;
	float d2 = texture(szum_drobny, p * 1.7 + vec2(0.2, 0.6)).r;
	// trawa: dwa odcienie mieszane dużym szumem + drobne źdźbła
	vec3 trawa = mix(trawa_ciemna, trawa_jasna, smoothstep(0.3, 0.72, n1 + (d - 0.5) * 0.25));
	trawa *= 0.88 + 0.22 * d2;
	// plamy ziemi
	float plama = smoothstep(ile_ziemi, ile_ziemi + 0.06, n2 * 0.75 + n1 * 0.25 + (d - 0.5) * 0.12);
	vec3 kolor = mix(trawa, ziemia * (0.85 + 0.25 * d2), plama * 0.85);
	// ścieżki: wąskie „grzbiety” szumu, wydeptane i poszarpane
	float g = abs(texture(szum, p * 0.016 + vec2(0.13, 0.52)).r - 0.5);
	float gdzie = smoothstep(0.5, 0.6, texture(szum, p * 0.009 + vec2(0.61, 0.27)).r);   // ścieżki tylko w części mapy
	float sc = (1.0 - smoothstep(0.006, 0.014 + (d - 0.5) * 0.006, g)) * gdzie * ile_sciezek;
	kolor = mix(kolor, sciezka * (0.88 + 0.2 * d2), sc * 0.85);
	// typ terenu z wierzchołków (drogi, plaże, wzgórza…) – granica poszarpana szumem
	vec3 typ = pow(COLOR.rgb, vec3(2.2)) * (0.9 + 0.18 * d2);
	float waga = smoothstep(0.32, 0.68, COLOR.a + (n2 - 0.5) * 0.5 + (d - 0.5) * 0.2);
	ALBEDO = mix(typ, kolor, waga);
	ROUGHNESS = 0.95;
}
"""
		_mat_terenu = ShaderMaterial.new()
		_mat_terenu.shader = sh
		_mat_terenu.set_shader_parameter("szum", _szum_tekstura(31, 0.012, 512))
		_mat_terenu.set_shader_parameter("szum_drobny", _szum_tekstura(57, 0.05))
	# klimat epoki: późne cesarstwo ma bardziej suchą, płową trawę i więcej wydeptanej ziemi
	var sucho: bool = R.get("epoka", "") == "schylek"
	_mat_terenu.set_shader_parameter("trawa_jasna", Color(0.58, 0.64, 0.33) if sucho else Color(0.5, 0.68, 0.31))
	_mat_terenu.set_shader_parameter("trawa_ciemna", Color(0.4, 0.5, 0.24) if sucho else Color(0.34, 0.53, 0.22))
	_mat_terenu.set_shader_parameter("ile_ziemi", 0.66 if sucho else 0.72)
	return _mat_terenu


func odswiez_siatke_budowy() -> void:
	## Półprzezroczysta siatka pól tylko w trybie budowy; pola, na których można postawić wybrany
	## budynek, są podświetlone na zielono.
	if siatka_budowy == null:
		return
	siatka_budowy.visible = wybrany != "" and not S.is_empty()
	if not siatka_budowy.visible:
		return
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var g := 0.045
	var linia := Color(1, 1, 1, 0.28)
	var dobre := Color(0.35, 1.0, 0.35, 0.22)
	for y in N:
		for x in N:
			var c := teren(x, y)
			if c == "" or _woda(c):
				continue
			var h := wysokosc(x, y) + 0.035
			var x0 := x * T
			var z0 := y * T
			if moze_budowac(S.aktywny, wybrany, x, y)[0]:
				_quad(st, Vector3(x0 + g, h, z0 + g), Vector3(x0 + T - g, h, z0 + g), Vector3(x0 + T - g, h, z0 + T - g), Vector3(x0 + g, h, z0 + T - g), dobre, Vector3.UP)
			# obrys pola (cienkie paski przy krawędziach)
			_quad(st, Vector3(x0, h, z0), Vector3(x0 + T, h, z0), Vector3(x0 + T, h, z0 + g), Vector3(x0, h, z0 + g), linia, Vector3.UP)
			_quad(st, Vector3(x0, h, z0 + g), Vector3(x0 + g, h, z0 + g), Vector3(x0 + g, h, z0 + T), Vector3(x0, h, z0 + T), linia, Vector3.UP)
	siatka_budowy.mesh = st.commit()
	var m := StandardMaterial3D.new()
	m.vertex_color_use_as_albedo = true
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	siatka_budowy.material_override = m


func _dno_i_woda(st: SurfaceTool, sw: SurfaceTool, x: int, y: int, morze: bool) -> void:
	## Pole wody: dno (siatka 4 × 4, opadające od brzegu) i powierzchnia z głębokością w wierzchołkach.
	var k := T / PODZIAL_WODY
	for j in PODZIAL_WODY:
		for i in PODZIAL_WODY:
			var xa := x * T + i * k
			var za := y * T + j * k
			var xb := xa + k
			var zb := za + k
			var h00 := _dno(xa, za, morze)
			var h10 := _dno(xb, za, morze)
			var h11 := _dno(xb, zb, morze)
			var h01 := _dno(xa, zb, morze)
			var pts := [Vector3(xa, h00, za), Vector3(xb, h10, za), Vector3(xb, h11, zb), Vector3(xa, h01, zb)]
			for idx in [0, 1, 2, 0, 2, 3]:
				var p: Vector3 = pts[idx]
				# dno: przy brzegu piasek i muł, w głębi ciemniej
				var g := clampf((STOPA_BRZEGU - p.y) / 1.2, 0.0, 1.0)
				var kd := Color(0.56, 0.5, 0.36).lerp(Color(0.16, 0.24, 0.26), g)
				kd.a = 0.0
				st.set_color(kd)
				st.set_normal(Vector3.UP)
				st.add_vertex(p)
			_quad_wody(sw, xa, za, xb, zb, _gl(h00), _gl(h10), _gl(h11), _gl(h01))


func _gl(dno: float) -> float:
	return clampf((POZIOM_WODY - dno) / 1.2, 0.0, 1.0)


func _quad_wody(sw: SurfaceTool, xa: float, za: float, xb: float, zb: float, g00: float, g10: float, g11: float, g01: float) -> void:
	var pts := [Vector3(xa, POZIOM_WODY, za), Vector3(xb, POZIOM_WODY, za), Vector3(xb, POZIOM_WODY, zb), Vector3(xa, POZIOM_WODY, zb)]
	var gl := [g00, g10, g11, g01]
	for idx in [0, 1, 2, 0, 2, 3]:
		sw.set_color(Color(gl[idx], 0, 0, 1))
		sw.set_normal(Vector3.UP)
		sw.set_uv(Vector2(pts[idx].x, pts[idx].z))
		sw.add_vertex(pts[idx])


func _material_wody() -> ShaderMaterial:
	## Woda: przezroczystość i kolor zależne od głębokości, dwie przewijane normal mapy (fale),
	## piana przy brzegu, fresnel z odbiciem nieba i odbicia otoczenia (radiance nieba).
	if woda_mat:
		_kolory_wody()
		return woda_mat
	var sh := Shader.new()
	sh.code = """shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_back, specular_schlick_ggx;

uniform vec3 kolor_plytki : source_color = vec3(0.22, 0.55, 0.6);
uniform vec3 kolor_glebi : source_color = vec3(0.05, 0.20, 0.33);
uniform vec3 kolor_nieba : source_color = vec3(0.78, 0.84, 0.90);
uniform vec3 kolor_piany : source_color = vec3(0.96, 0.97, 0.95);
uniform sampler2D fale_a : hint_normal, filter_linear_mipmap, repeat_enable;
uniform sampler2D fale_b : hint_normal, filter_linear_mipmap, repeat_enable;
uniform sampler2D szum : filter_linear_mipmap, repeat_enable;
uniform vec2 przeplyw = vec2(0.018, 0.03);
uniform float sila_fal = 0.4;
uniform float pas_piany = 0.16;
uniform float jasnosc = 1.0;
uniform float glebia_wymuszona = -1.0;   // >= 0: stała głębokość (woda w budynkach)        // Forward+ oświetla wodę mocniej niż GL Compatibility

varying vec3 swiat;

void vertex() {
	swiat = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	// delikatne kołysanie lustra wody (mniejsze przy brzegu)
	float g = glebia_wymuszona >= 0.0 ? glebia_wymuszona : COLOR.r;
	VERTEX.y += (sin(swiat.x * 0.9 + TIME * 1.4) + cos(swiat.z * 0.8 + TIME * 1.1)) * 0.012 * g;
}

void fragment() {
	float g = glebia_wymuszona >= 0.0 ? glebia_wymuszona : COLOR.r;   // 0 – brzeg, 1 – głęboko
	vec2 uv = swiat.xz;
	// dwie normal mapy przewijane w różnych kierunkach i skalach = fale
	vec3 na = texture(fale_a, uv * 0.085 + TIME * przeplyw).rgb;
	vec3 nb = texture(fale_b, uv * 0.13 + vec2(-TIME * przeplyw.y, TIME * przeplyw.x) * 0.8).rgb;
	NORMAL_MAP = normalize(na + nb - 1.0) * 0.5 + 0.5;
	NORMAL_MAP_DEPTH = sila_fal;
	// kolor: płycizna turkusowa, głębia granatowa
	vec3 woda = mix(kolor_plytki, kolor_glebi, smoothstep(0.05, 0.85, g));
	// fresnel: pod małym kątem woda odbija niebo
	float fres = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 4.0);
	woda = mix(woda, kolor_nieba, clamp(fres * 0.6, 0.0, 0.5));
	// piana przy brzegu: pas płytkiej wody poszarpany szumem, pulsujący jak fala przyboju
	float s = texture(szum, uv * 0.42 + vec2(TIME * 0.025, -TIME * 0.018)).r;
	float s2 = texture(szum, uv * 0.9 - vec2(TIME * 0.04, TIME * 0.03)).r;
	float pas = 1.0 - smoothstep(pas_piany * 0.3, pas_piany, g + (s - 0.5) * 0.12);
	float przybuj = 0.5 + 0.5 * sin(TIME * 1.6 - g * 40.0 + s * 4.0);
	float piana = clamp(pas * smoothstep(0.35, 0.65, s2 * 0.6 + przybuj * 0.5), 0.0, 1.0);
	piana = max(piana, (1.0 - smoothstep(0.0, pas_piany * 0.45, g)) * 0.85);
	ALBEDO = mix(woda * jasnosc, kolor_piany, piana);
	// przezroczystość zależna od głębokości: przy brzegu widać dno
	ALPHA = clamp(mix(0.38, 0.94, smoothstep(0.0, 0.7, g)) + piana * 0.6 + fres * 0.15, 0.0, 1.0);
	ROUGHNESS = mix(0.2, 0.7, piana);
	METALLIC = 0.0;
	SPECULAR = 0.28;
}
"""
	woda_mat = ShaderMaterial.new()
	woda_mat.shader = sh
	woda_mat.set_shader_parameter("fale_a", _normal_mapa(11, 0.022))
	woda_mat.set_shader_parameter("fale_b", _normal_mapa(23, 0.035))
	var sz := NoiseTexture2D.new()
	sz.width = 256
	sz.height = 256
	sz.seamless = true
	var fn := FastNoiseLite.new()
	fn.seed = 5
	fn.frequency = 0.03
	fn.fractal_octaves = 3
	sz.noise = fn
	woda_mat.set_shader_parameter("szum", sz)
	woda_mat.set_shader_parameter("jasnosc", 1.0 if RenderingServer.get_rendering_device() == null else 0.55)
	_kolory_wody()
	return woda_mat


func _normal_mapa(ziarno: int, czestotliwosc: float) -> NoiseTexture2D:
	var t := NoiseTexture2D.new()
	t.width = 256
	t.height = 256
	t.seamless = true
	t.as_normal_map = true
	t.bump_strength = 5.0
	var fn := FastNoiseLite.new()
	fn.seed = ziarno
	fn.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	fn.frequency = czestotliwosc
	fn.fractal_octaves = 3
	t.noise = fn
	return t


func _kolory_wody() -> void:
	## Odbicie nieba w kolorze horyzontu epoki (zmierzch późnego cesarstwa zabarwia wodę).
	if woda_mat and niebo_mat:
		woda_mat.set_shader_parameter("kolor_nieba", niebo_mat.sky_horizon_color.lerp(niebo_mat.sky_top_color, 0.35))


func _quad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, kol: Color, n: Vector3) -> void:
	for v in [a, b, c, a, c, d]:
		st.set_color(kol)
		st.set_normal(n)
		st.add_vertex(v)


const DRZEWA := ["dab", "pinia", "cyprys", "oliwka", "krzak"]


func _rozsiej(model: String, transformy: Array) -> void:
	## Wiele kopii modelu jako MultiMesh (las, góry) – szybkie także w przeglądarce.
	if transformy.is_empty():
		return
	var wzor := instancja(model)
	var siatki := []
	_zbierz_siatki(wzor, Transform3D.IDENTITY, siatki)
	wzor.free()
	# drzewa: każdy egzemplarz dostaje własny odcień (cieplejszy/chłodniejszy, jaśniejszy/ciemniejszy);
	# kolor instancji mnoży się z gradientem z vertex colors modelu
	var odcienie := []
	if model in DRZEWA:
		var r := RandomNumberGenerator.new()
		r.seed = model.hash() + int(S.get("rozdzial", 0))
		for i in transformy.size():
			var o := r.randf_range(-1.0, 1.0)            # -1 chłodniej/sino, +1 cieplej/żółtawo
			var j := r.randf_range(0.84, 1.12)           # jasność
			odcienie.append(Color(j * (1.0 + 0.11 * o), j * (1.0 + 0.03 * o), j * (1.0 - 0.14 * o)))
	for s in siatki:
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = not odcienie.is_empty()
		mm.mesh = s[0]
		mm.instance_count = transformy.size()
		for i in transformy.size():
			mm.set_instance_transform(i, transformy[i] * s[1])
			if mm.use_colors:
				mm.set_instance_color(i, odcienie[i])
		var mmi := MultiMeshInstance3D.new()
		mmi.multimesh = mm
		if s[2]:
			mmi.material_override = s[2]
		dekor_wezel.add_child(mmi)


func _zbierz_siatki(n: Node, tr: Transform3D, wynik: Array) -> void:
	var t2 := tr
	if n is Node3D:
		t2 = tr * (n as Node3D).transform
	if n is MeshInstance3D and (n as MeshInstance3D).mesh:
		wynik.append([(n as MeshInstance3D).mesh, t2, (n as MeshInstance3D).material_override])
	for c in n.get_children():
		_zbierz_siatki(c, t2, wynik)


func _dekoracje() -> void:
	var r := RandomNumberGenerator.new()
	r.seed = 1234 + int(S.rozdzial)
	var drzewa := {"dab": [], "pinia": [], "cyprys": [], "oliwka": [], "krzak": [], "skala_0": [], "skala_1": [], "gora": [], "trzcina": []}
	# skład lasu: Italia i Afryka – pinie, cyprysy, dęby, oliwki; Galia, Dacja, północ – głównie dęby
	var rodzaje := ["pinia", "cyprys", "dab", "pinia", "dab", "cyprys", "oliwka"]
	if R.id in ["alezja", "upadek", "dacja"]:
		rodzaje = ["dab", "dab", "dab", "pinia", "dab", "krzak"]
	for y in N:
		for x in N:
			var c := teren(x, y)
			var baza := pozycja(x, y)
			if zajete_dekoracja(x, y):
				continue
			match c:
				"l":
					for k in 3:
						var off := Vector3(r.randf_range(-0.65, 0.65), 0, r.randf_range(-0.65, 0.65))
						var s := r.randf_range(0.75, 1.15)
						var sk := Vector3(s * r.randf_range(0.9, 1.1), s * r.randf_range(0.9, 1.12), s * r.randf_range(0.9, 1.1))
						var pochyl := Basis(Vector3(1, 0, 0), r.randf_range(-0.05, 0.05)) * Basis(Vector3(0, 0, 1), r.randf_range(-0.05, 0.05))
						drzewa[rodzaje[r.randi_range(0, rodzaje.size() - 1)]].append(Transform3D(pochyl * Basis(Vector3.UP, r.randf() * TAU).scaled(sk), baza + off))
				"o":
					for k in 2:
						var off := Vector3(r.randf_range(-0.55, 0.55), 0, r.randf_range(-0.55, 0.55))
						drzewa.oliwka.append(Transform3D(Basis(Vector3.UP, r.randf() * TAU) * 0.85, baza + off))
				"g":
					drzewa.gora.append(Transform3D(Basis(Vector3.UP, r.randf() * TAU) * r.randf_range(0.9, 1.2), baza))
				"w":
					if r.randf() < 0.3:
						drzewa["skala_%d" % r.randi_range(0, 1)].append(Transform3D(Basis(Vector3.UP, r.randf() * TAU) * 0.6, baza + Vector3(r.randf_range(-0.5, 0.5), 0, r.randf_range(-0.5, 0.5))))
					if r.randf() < 0.2:
						drzewa.cyprys.append(Transform3D(Basis.IDENTITY * 0.8, baza + Vector3(0.6, 0, 0.5)))
				"b":
					for k in 2:
						drzewa.trzcina.append(Transform3D(Basis(Vector3.UP, r.randf() * TAU) * 0.8, baza + Vector3(r.randf_range(-0.5, 0.5), 0, r.randf_range(-0.5, 0.5))))
				".":
					if r.randf() < 0.05:
						drzewa.krzak.append(Transform3D(Basis(Vector3.UP, r.randf() * TAU) * 0.7, baza + Vector3(r.randf_range(-0.6, 0.6), 0, r.randf_range(-0.6, 0.6))))
	for m in drzewa:
		_rozsiej(m, drzewa[m])
	# podpisy geograficzne
	for p in R.podpisy:
		var l := etykieta(p[2], 72, Color(1, 0.95, 0.8))
		l.position = pozycja(p[0], p[1]) + Vector3(0, 2.2, 0)
		l.no_depth_test = false
		dekor_wezel.add_child(l)
	# zabytki
	for z in R.zabytki:
		var n := instancja(z[2])
		n.position = pozycja(z[0], z[1])
		_cien_kontaktowy(n, 1.35, 0.5)
		dekor_wezel.add_child(n)
		var l := etykieta(z[3], 52, Color(1, 0.86, 0.45))
		l.position = n.position + Vector3(0, 4.2, 0)
		dekor_wezel.add_child(l)
	# obozy wroga
	for o in R.obozy:
		var n := instancja("oboz_kartaginy" if o[2] == "kartaginczyk" else "oboz_barbarzyncow")
		n.position = pozycja(o[0], o[1])
		_cien_kontaktowy(n, 1.3, 0.45)
		dekor_wezel.add_child(n)
		var w := instancja(o[2])
		w.position = n.position + Vector3(1.2, 0, 1.0)
		w.scale = Vector3.ONE * SKALA_POSTACI
		_cien_kontaktowy(w, 0.6, 0.5)
		dekor_wezel.add_child(w)
		_postacie.append(w)
		var l := etykieta(o[3], 56, Color(1, 0.55, 0.45))
		l.position = n.position + Vector3(0, 3.4, 0)
		dekor_wezel.add_child(l)
	# kronikarz Damian i dowódca przy siedzibie pierwszego gracza
	var s0: Array = R.start[0]
	var dam := instancja("damian")
	dam.position = pozycja(s0[0], s0[1]) + Vector3(-1.3, 0, 1.4)
	dam.scale = Vector3.ONE * SKALA_POSTACI
	dam.rotation.y = 0.5
	_cien_kontaktowy(dam, 0.6, 0.5)
	dam.set_meta("postac", "damian")
	dekor_wezel.add_child(dam)
	_postacie.append(dam)
	var dl := etykieta("Damian (kronikarz)", 40, Color(0.85, 0.7, 1.0))
	dl.position = dam.position + Vector3(0, 1.6, 0)
	dekor_wezel.add_child(dl)
	var dow: String = R.bitwa.dowodca
	if dow == "cyncynat" or dow in ["romulus", "scypion", "cezar", "august", "trajan", "konstantyn"]:
		var h := instancja(dow)
		h.position = pozycja(s0[0], s0[1]) + Vector3(1.4, 0, 1.3)
		h.scale = Vector3.ONE * SKALA_POSTACI
		h.rotation.y = -0.4
		_cien_kontaktowy(h, 0.6, 0.5)
		dekor_wezel.add_child(h)
		_postacie.append(h)
		var hl := etykieta(D.postacie[dow].imie, 40, Color(1, 0.9, 0.6))
		hl.position = h.position + Vector3(0, 1.6, 0)
		dekor_wezel.add_child(hl)
	# statki na morzu
	var morze := []
	for y in N:
		for x in N:
			if teren(x, y) == "m":
				morze.append(Vector2i(x, y))
	if morze.size() > 20:
		for k in 2:
			var s := instancja("galera")
			var p0: Vector2i = morze[r.randi_range(0, morze.size() - 1)]
			s.position = pozycja(p0.x, p0.y) + Vector3(0, 0.05, 0)
			s.scale = Vector3.ONE * 0.6
			s.set_meta("start", s.position)
			s.set_meta("faza", r.randf() * TAU)
			dekor_wezel.add_child(s)
			_statki.append(s)


func odswiez_swiat() -> void:
	if S.is_empty():
		return
	przelicz_wlasnosc()
	# budynki
	var widziane := {}
	for b in S.budynki:
		var klucz := "%d,%d,%s,%s" % [int(b.x), int(b.y), b.typ, str(b.gotowy)]
		widziane[klucz] = true
		if _bud_wezly.has(klucz):
			continue
		var n := Node3D.new()
		n.position = pozycja(int(b.x), int(b.y))
		var model := instancja(b.typ if b.gotowy else "rusztowanie")
		n.add_child(model)
		_ozyw_model(model)
		if _animuj_nowe and tryb == "" and scena == "gra":
			# nowy budynek wyrasta z ziemi, rusztowanie „wskakuje” na plac budowy
			var tw := model.create_tween()
			if b.gotowy:
				model.scale = Vector3(1, 0.02, 1)
				tw.tween_property(model, "scale", Vector3.ONE, 0.8).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
			else:
				model.scale = Vector3.ONE * 0.3
				tw.tween_property(model, "scale", Vector3.ONE, 0.6).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
		# podstawa w kolorze rodu
		var krag := MeshInstance3D.new()
		var cm := CylinderMesh.new()
		cm.top_radius = 0.95
		cm.bottom_radius = 0.95
		cm.height = 0.04
		cm.radial_segments = 20
		krag.mesh = cm
		krag.position.y = 0.02
		if b.gotowy:
			_cien_kontaktowy(n, 1.05, 0.5)
		var km := StandardMaterial3D.new()
		km.albedo_color = Color(D.rody[int(gr(int(b.wl)).rod)].kolor)
		km.albedo_color.a = 0.55
		km.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		km.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		krag.material_override = km
		n.add_child(krag)
		bud_wezel.add_child(n)
		_bud_wezly[klucz] = n
		if tryb == "" and b.gotowy and scena == "gra":
			_pyl(n.position)
	for k in _bud_wezly.keys():
		if not widziane.has(k):
			_bud_wezly[k].queue_free()
			_bud_wezly.erase(k)
	# zagony
	var zw := {}
	for z in S.zagony:
		var id := str(z.id)
		zw[id] = true
		if not _zag_wezly.has(id):
			var n := Node3D.new()
			for k in 3:
				var u := instancja(z.model)
				u.scale = Vector3.ONE * SKALA_POSTACI
				u.position = Vector3((k - 1) * 0.55, 0, (k % 2) * 0.4)
				_cien_kontaktowy(u, 0.75 if z.model in ["hun", "ekwita"] else 0.55, 0.5)
				n.add_child(u)
			var l := etykieta("%s (siła %d)" % [z.nazwa, int(z.sila)], 44, Color(1, 0.5, 0.4))
			l.position.y = 1.7
			l.name = "etykieta"
			n.add_child(l)
			n.position = pozycja(int(z.x), int(z.y))
			zagon_wezel.add_child(n)
			_zag_wezly[id] = n
		var cel := pozycja(int(z.x), int(z.y))
		_zag_wezly[id].set_meta("cel", cel)
	for k in _zag_wezly.keys():
		if not zw.has(k):
			_zag_wezly[k].queue_free()
			_zag_wezly.erase(k)
	# znajdźki (błyszczące pierścienie)
	for z in R.znajdzki:
		var klucz := "%d,%d" % [int(z[0]), int(z[1])]
		if klucz in S.znalezione:
			if _znajdzki_wezly.has(klucz):
				_znajdzki_wezly[klucz].queue_free()
				_znajdzki_wezly.erase(klucz)
			continue
		if _znajdzki_wezly.has(klucz):
			continue
		var n := instancja("znacznik")
		n.position = pozycja(int(z[0]), int(z[1])) + Vector3(0, 0.1, 0)
		n.scale = Vector3.ONE * 0.7
		dekor_wezel.add_child(n)
		_znajdzki_wezly[klucz] = n
	_rysuj_granice()
	odswiez_siatke_budowy()


func _rysuj_granice() -> void:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var g := 0.09
	var jest := false
	for y in N:
		for x in N:
			var p := wlasc(x, y)
			if p < 0:
				continue
			var kol := Color(D.rody[int(gr(p).rod)].kolor).lightened(0.25)
			if S.tryb == "kampania":
				kol = Color(1, 0.85, 0.3)
			var h := maxf(wysokosc(x, y), 0.0) + 0.06
			var x0 := x * T
			var z0 := y * T
			for kier in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
				if wlasc(x + kier.x, y + kier.y) == p:
					continue
				jest = true
				var a: Vector3
				var b: Vector3
				if kier == Vector2i(1, 0):
					a = Vector3(x0 + T - g, h, z0); b = Vector3(x0 + T, h, z0 + T)
				elif kier == Vector2i(-1, 0):
					a = Vector3(x0, h, z0); b = Vector3(x0 + g, h, z0 + T)
				elif kier == Vector2i(0, 1):
					a = Vector3(x0, h, z0 + T - g); b = Vector3(x0 + T, h, z0 + T)
				else:
					a = Vector3(x0, h, z0); b = Vector3(x0 + T, h, z0 + g)
				_quad(st, Vector3(a.x, h, a.z), Vector3(b.x, h, a.z), Vector3(b.x, h, b.z), Vector3(a.x, h, b.z), kol, Vector3.UP)
	if not jest:
		granice_wezel.mesh = null
		return
	granice_wezel.mesh = st.commit()
	var m := StandardMaterial3D.new()
	m.vertex_color_use_as_albedo = true
	m.vertex_color_is_srgb = true
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	granice_wezel.material_override = m


func _pyl(poz: Vector3) -> void:
	var cz := CPUParticles3D.new()
	cz.one_shot = true
	cz.amount = 24
	cz.lifetime = 0.9
	cz.explosiveness = 0.9
	cz.direction = Vector3.UP
	cz.spread = 70
	cz.initial_velocity_min = 1.5
	cz.initial_velocity_max = 3.0
	cz.gravity = Vector3(0, -3, 0)
	var sm := SphereMesh.new()
	sm.radius = 0.12
	sm.height = 0.24
	cz.mesh = sm
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(0.85, 0.78, 0.6)
	cz.material_override = m
	cz.position = poz + Vector3(0, 0.3, 0)
	add_child(cz)
	cz.emitting = true
	get_tree().create_timer(1.5).timeout.connect(cz.queue_free)


func _kamera_na_siedzibe(p: int) -> void:
	if S.is_empty() or p < 0 or p >= S.gracze.size():
		return
	var s: Array = gr(p).start
	cel_kam = pozycja(s[0], s[1])
	cel_kam.y = 0


func _process(dt: float) -> void:
	t += dt
	if tryb == "serwer":
		return
	if scena in ["gra", "przekazanie", "koniec_mp"] and not S.is_empty():
		_steruj_kamera(dt)
		_animuj(dt)
	elif scena == "tytul" or scena == "intro":
		pass


func _steruj_kamera(dt: float) -> void:
	var ruch := Vector3.ZERO
	if not ui.pisze():
		if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
			ruch.z -= 1
		if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
			ruch.z += 1
		if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
			ruch.x -= 1
		if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
			ruch.x += 1
	if ruch != Vector3.ZERO:
		cel_kam += ruch.normalized().rotated(Vector3.UP, yaw) * dt * odl * 0.9
	cel_kam.x = clampf(cel_kam.x, 0, N * T)
	cel_kam.z = clampf(cel_kam.z, 0, N * T)
	yaw = lerp_angle(yaw, yaw_cel, minf(1.0, dt * 6))
	var pitch := deg_to_rad(52)
	var off := Vector3(sin(yaw), 0, cos(yaw)) * cos(pitch) * odl + Vector3.UP * sin(pitch) * odl
	kamera.position = kamera.position.lerp(cel_kam + off, minf(1.0, dt * 8))
	kamera.look_at(kamera.position - off, Vector3.UP)
	ustaw_glebie(odl)


# ----------------------------------------------------------------- ożywione budynki
# Części modeli z Blendera nazwane „anim_<rodzaj>_…” są animowane, a puste punkty „dym_…” dymią:
#   anim_obrot_x (koło dźwigu), anim_obrot_z (żuraw), anim_kolys (flagi, markizy, kłosy, pranie),
#   anim_pila (piłowanie), anim_mlot (młot, kilof, miecz), anim_ogien (ogień + światło),
#   anim_woda (woda na shaderze), anim_lodz (kołysanie łodzi).
var _animowane := []
var _animuj_nowe := true
var _mat_wody_budynku: ShaderMaterial
var _mat_dymu: StandardMaterial3D


func _ozyw_model(model: Node) -> void:
	if tryb == "test":
		return
	var r := RandomNumberGenerator.new()
	for c in model.find_children("*", "", true, false):
		var nm := String(c.name)
		if nm.begins_with("dym_") and c is Node3D:
			_dodaj_dym(c as Node3D, nm)
		if not nm.begins_with("anim_") or not (c is Node3D):
			continue
		var n := c as Node3D
		var rodzaj := nm.split("_")[1]
		var amp := 0.1
		if "flaga" in nm:
			amp = 0.35
		elif "sztandar" in nm or "pranie" in nm:
			amp = 0.2
		elif "markiza" in nm:
			amp = 0.05
		elif "klosy" in nm:
			amp = 0.09
		elif "strach" in nm or "ladunek" in nm:
			amp = 0.06
		elif "tracz" in nm or "kupiec" in nm or "pomocnik" in nm:
			amp = 0.15
		_animowane.append({"n": n, "rodzaj": rodzaj, "nazwa": nm, "baza": n.transform, "f": r.randf() * TAU, "amp": amp})
		if rodzaj == "woda" and n is MeshInstance3D:
			if _mat_wody_budynku == null:
				_mat_wody_budynku = _material_wody().duplicate()
				_mat_wody_budynku.set_shader_parameter("glebia_wymuszona", 0.35)
				_mat_wody_budynku.set_shader_parameter("pas_piany", 0.0)
			(n as MeshInstance3D).material_override = _mat_wody_budynku
		elif rodzaj == "ogien" and _ile_swiatel() < MAKS_SWIATEL:
			var sw := OmniLight3D.new()
			sw.light_color = Color(1.0, 0.62, 0.28)
			sw.light_energy = 0.9
			sw.omni_range = 1.4
			sw.shadow_enabled = false
			sw.position = Vector3(0, 0.15, 0)
			n.add_child(sw)
			_animowane.append({"n": sw, "rodzaj": "swiatlo", "nazwa": "", "baza": sw.transform, "f": r.randf() * TAU, "amp": 0.9})


const MAKS_SWIATEL := 12      # światła od ognia (w WebGL każde kosztuje osobny przebieg)


func _ile_swiatel() -> int:
	var n := 0
	for a in _animowane:
		if a.rodzaj == "swiatlo" and is_instance_valid(a.n):
			n += 1
	return n


func _dodaj_dym(punkt: Node3D, nazwa: String) -> void:
	var cz := CPUParticles3D.new()
	var woda := "fontanna" in nazwa
	var para := "para" in nazwa
	cz.amount = 14 if woda else 9
	cz.lifetime = 0.9 if woda else 3.4
	cz.preprocess = 3.0
	cz.local_coords = false
	cz.direction = Vector3.UP
	cz.spread = 14 if woda else 10
	cz.initial_velocity_min = 0.9 if woda else 0.22
	cz.initial_velocity_max = 1.2 if woda else 0.4
	cz.gravity = Vector3(0, -3.0, 0) if woda else Vector3(0.1, 0.04, 0.05)    # lekki wiatr
	var sm := SphereMesh.new()
	sm.radius = 0.02 if woda else 0.11
	sm.height = sm.radius * 2
	sm.radial_segments = 6
	sm.rings = 4
	cz.mesh = sm
	var krzywa := Curve.new()
	krzywa.add_point(Vector2(0, 0.45 if not woda else 1.0))
	krzywa.add_point(Vector2(1, 1.7 if not woda else 0.6))
	cz.scale_amount_curve = krzywa
	var g := Gradient.new()
	if woda:
		g.set_color(0, Color(0.75, 0.88, 1.0, 0.85))
		g.set_color(1, Color(0.75, 0.88, 1.0, 0.0))
	else:
		var k := Color(0.95, 0.95, 0.95) if para else Color(0.72, 0.72, 0.74)
		g.set_color(0, Color(k, 0.0))
		g.add_point(0.15, Color(k, 0.55 if not para else 0.35))
		g.set_color(g.get_point_count() - 1, Color(k.lightened(0.15), 0.0))
	cz.color_ramp = g
	if _mat_dymu == null:
		_mat_dymu = StandardMaterial3D.new()
		_mat_dymu.vertex_color_use_as_albedo = true
		_mat_dymu.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		_mat_dymu.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	cz.material_override = _mat_dymu
	cz.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	punkt.add_child(cz)


func _animuj_budynki() -> void:
	var i := 0
	while i < _animowane.size():
		var a: Dictionary = _animowane[i]
		if not is_instance_valid(a.n):
			_animowane.remove_at(i)
			continue
		var n: Node3D = a.n
		var b: Transform3D = a.baza
		var f: float = a.f
		match a.rodzaj:
			"obrot":
				if a.nazwa.begins_with("anim_obrot_z"):
					n.transform = Transform3D(b.basis * Basis(Vector3.UP, sin(t * 0.35 + f) * 0.9), b.origin)
				else:
					n.transform = Transform3D(b.basis * Basis(Vector3.RIGHT, t * 1.3), b.origin)
			"kolys":
				if "flaga" in a.nazwa:
					n.transform = Transform3D(b.basis * Basis(Vector3.UP, sin(t * 2.6 + f) * a.amp + sin(t * 6.3 + f) * 0.08), b.origin)
				else:
					var w := Basis(Vector3.RIGHT, sin(t * 1.6 + f) * a.amp) * Basis(Vector3.BACK, sin(t * 1.1 + f * 1.7) * a.amp * 0.6)
					n.transform = Transform3D(b.basis * w, b.origin)
			"pila":
				n.transform = Transform3D(b.basis, b.origin + b.basis.y.normalized() * sin(t * 7.0 + f) * 0.06)
			"mlot":
				var uderzenie := pow(absf(sin(t * 2.3 + f)), 3.0)
				n.transform = Transform3D(b.basis * Basis(Vector3.RIGHT, uderzenie * 1.1), b.origin)
			"ogien":
				var s := 1.0 + 0.16 * sin(t * 13.0 + f) + 0.1 * sin(t * 7.3 + f * 2.0)
				n.transform = Transform3D(b.basis.scaled(Vector3(1.0 / s, s, 1.0 / s)), b.origin)
			"swiatlo":
				(n as OmniLight3D).light_energy = a.amp * (0.85 + 0.15 * sin(t * 11.0 + f) + 0.08 * sin(t * 23.0 + f))
			"lodz":
				n.transform = Transform3D(b.basis * Basis(Vector3.BACK, sin(t * 1.3 + f) * 0.06), b.origin + Vector3(0, sin(t * 1.7 + f) * 0.025, 0))
		i += 1


func _animuj(dt: float) -> void:
	_animuj_budynki()
	for id in _zag_wezly:
		var n: Node3D = _zag_wezly[id]
		var cel: Vector3 = n.get_meta("cel", n.position)
		var idzie := n.position.distance_to(cel) > 0.05
		n.position = n.position.move_toward(cel, dt * 2.5)
		if idzie:
			n.look_at(Vector3(cel.x, n.position.y, cel.z), Vector3.UP, true)
		for u in n.get_children():
			if u is Node3D and u.name != "etykieta":
				animuj_postac(u, "idzie" if idzie else "stoi", t * 7.0 + u.position.x)
	for p in _postacie:
		if is_instance_valid(p):
			animuj_postac(p, "stoi", t)
	for s in _statki:
		var st: Vector3 = s.get_meta("start")
		var f: float = s.get_meta("faza")
		s.position = st + Vector3(sin(t * 0.1 + f) * 3.0, sin(t * 1.3 + f) * 0.05 - 0.15, cos(t * 0.1 + f) * 2.0)
		s.rotation.y = -t * 0.1 - f + PI
	for k in _znajdzki_wezly:
		var n: Node3D = _znajdzki_wezly[k]
		n.rotation.y = t * 1.5
		n.position.y = pozycja(int(k.split(",")[0]), int(k.split(",")[1])).y + 0.15 + sin(t * 3) * 0.08
	if kursor.visible and wybrany != "":
		pass


# ----------------------------------------------------------------- animacja postaci i jednostek
# Części z Blendera: noga_l/p, reka_l/p, glowa, peleryna (piechota i postacie); kon_noga_lp/pp/lt/pt, kon_glowa,
# kon_ogon, jezdziec (jazda); slon_noga_*, slon_traba, slon_ucho_l/p, slon_ogon (słoń).
# Stany: „stoi” (oddech, rozglądanie się, peleryna na wietrze), „idzie” (marsz / galop), „atak” (cios mieczem).
const CZESCI_POSTACI := ["noga_l", "noga_p", "reka_l", "reka_p", "glowa", "peleryna", "kon_noga_lp", "kon_noga_pp",
	"kon_noga_lt", "kon_noga_pt", "kon_glowa", "kon_ogon", "jezdziec", "slon_noga_lp", "slon_noga_pp", "slon_noga_lt",
	"slon_noga_pt", "slon_traba", "slon_ucho_l", "slon_ucho_p", "slon_ogon", "balista_ramie_l", "balista_ramie_p",
	"balista_suwak", "balista_belt", "balista_kolowrot", "cieciwa_luku"]


func _czesci_postaci(n: Node) -> Dictionary:
	if n.has_meta("czesci"):
		return n.get_meta("czesci")
	var d := {}
	for c in n.find_children("*", "Node3D", true, false):
		var nm := String(c.name)
		if nm in CZESCI_POSTACI:
			d[nm] = [c, (c as Node3D).transform]
	n.set_meta("czesci", d)
	n.set_meta("faza0", randf() * TAU)
	return d


func _obroc(d: Dictionary, k: String, b: Basis, przesun := Vector3.ZERO) -> void:
	if not d.has(k):
		return
	var baza: Transform3D = d[k][1]
	(d[k][0] as Node3D).transform = Transform3D(baza.basis * b, baza.origin + przesun)


func animuj_postac(n: Node, stan: String, faza: float, postep_ataku := 0.0) -> void:
	## faza – kąt cyklu kroku; postep_ataku 0..1 – przebieg ciosu w stanie „atak”.
	var d := _czesci_postaci(n)
	if d.is_empty():
		return
	var f0: float = n.get_meta("faza0", 0.0)
	var ruch := stan == "idzie"
	var X := Vector3.RIGHT
	var Y := Vector3.UP
	var Z := Vector3.BACK
	# --- piechota i postacie
	if d.has("noga_l"):
		var amp := 0.55 if ruch else 0.0
		_obroc(d, "noga_l", Basis(X, sin(faza) * amp))
		_obroc(d, "noga_p", Basis(X, -sin(faza) * amp))
		var oddech := sin(t * 1.6 + f0)
		if stan == "atak" and d.has("cieciwa_luku"):
			pass    # łucznik: ręce prowadzi _animuj_lucznika
		elif stan == "atak":
			# zamach i cios: ręka z bronią wznosi się, potem tnie w dół; tarcza wysunięta
			var k := sin(clampf(postep_ataku, 0.0, 1.0) * PI)
			var ciecie := -2.0 * k + 0.9 * smoothstep(0.55, 1.0, postep_ataku)
			_obroc(d, "reka_p", Basis(X, ciecie))
			_obroc(d, "reka_l", Basis(X, -0.5 * k) * Basis(Z, 0.2 * k))
		else:
			var r := -sin(faza) * 0.5 if ruch else oddech * 0.04
			_obroc(d, "reka_l", Basis(X, -r))
			_obroc(d, "reka_p", Basis(X, r))
		# głowa: przy marszu lekkie kiwanie, w spoczynku rozglądanie się
		if ruch:
			_obroc(d, "glowa", Basis(X, sin(faza * 2.0) * 0.05))
		else:
			var rozglad := sin(t * 0.37 + f0) * 0.45 * smoothstep(0.2, 0.8, absf(sin(t * 0.21 + f0 * 0.5)))
			_obroc(d, "glowa", Basis(Y, rozglad) * Basis(X, oddech * 0.03))
		# peleryna: przy marszu rozwiana, w spoczynku faluje na wietrze
		var pel := (0.28 + sin(faza * 2.0) * 0.08) if ruch else (0.06 + sin(t * 1.9 + f0) * 0.05)
		_obroc(d, "peleryna", Basis(X, -pel) * Basis(Z, sin(t * 1.3 + f0) * 0.04))
	# --- koń: galop lub spokojne przestępowanie
	if d.has("kon_noga_lp"):
		var g := faza * 1.3
		var amp_k := 0.6 if ruch else 0.0
		_obroc(d, "kon_noga_lp", Basis(X, sin(g) * amp_k))
		_obroc(d, "kon_noga_pp", Basis(X, sin(g + 0.6) * amp_k))
		_obroc(d, "kon_noga_lt", Basis(X, sin(g + PI) * amp_k))
		_obroc(d, "kon_noga_pt", Basis(X, sin(g + PI + 0.6) * amp_k))
		var glowa_k := sin(g * 2.0) * 0.12 if ruch else sin(t * 0.6 + f0) * 0.08 + maxf(0.0, sin(t * 0.17 + f0)) * 0.25
		_obroc(d, "kon_glowa", Basis(X, glowa_k))
		_obroc(d, "kon_ogon", Basis(X, 0.15 + sin(t * 2.1 + f0) * 0.1) * Basis(Z, sin(t * 1.4 + f0) * 0.25))
		_obroc(d, "jezdziec", Basis.IDENTITY, Vector3(0, absf(sin(g)) * 0.07 if ruch else sin(t * 1.6 + f0) * 0.006, 0))
	# --- słoń: ciężki krok, wachlujące uszy, kołysząca się trąba
	if d.has("slon_noga_lp"):
		var g2 := faza * 0.7
		var amp_s := 0.3 if ruch else 0.0
		_obroc(d, "slon_noga_lp", Basis(X, sin(g2) * amp_s))
		_obroc(d, "slon_noga_pt", Basis(X, sin(g2) * amp_s))
		_obroc(d, "slon_noga_pp", Basis(X, -sin(g2) * amp_s))
		_obroc(d, "slon_noga_lt", Basis(X, -sin(g2) * amp_s))
		_obroc(d, "slon_traba", Basis(X, sin(t * 0.9 + f0) * 0.22 - 0.05) * Basis(Z, sin(t * 0.55 + f0) * 0.18))
		var ucho := 0.15 + sin(t * 1.4 + f0) * 0.22
		_obroc(d, "slon_ucho_l", Basis(Y, -ucho))
		_obroc(d, "slon_ucho_p", Basis(Y, ucho))
		_obroc(d, "slon_ogon", Basis(Z, sin(t * 2.4 + f0) * 0.35))
	# łucznik: naciąganie łuku, celowanie, strzał (cięciwa i nałożona strzała rysowane w grze)
	if d.has("cieciwa_luku"):
		_animuj_lucznika(n, d, stan, postep_ataku)
	# balista: naciągnięta w spoczynku; w ataku strzał, przeładowanie (suwak, kołowrót, cięciwy)
	if d.has("balista_ramie_l"):
		_animuj_baliste(n, d, stan, postep_ataku)
	# Damian pisze w kronice (pióro w lewej dłoni)
	if n.get_meta("postac", "") == "damian" and not ruch and d.has("reka_l"):
		_obroc(d, "reka_l", Basis(X, -0.35 + sin(t * 7.0) * 0.05) * Basis(Z, sin(t * 3.1) * 0.08))


# ----------------------------------------------------------------- balista
const BALISTA_KONIEC := Vector3(0.33, 0.0, -0.23)   # koniec ramienia względem osi wiązki (prawe; lewe – lustrzane)
const BALISTA_ZWOLNIONA := 0.75                      # kąt ramion po strzale (rad)


func _koniec_ramienia(d: Dictionary, k: String, kat: float) -> Vector3:
	var baza: Transform3D = d[k][1]
	var znak := -1.0 if k.ends_with("_l") else 1.0
	return baza.origin + Basis(Vector3.UP, kat) * Vector3(BALISTA_KONIEC.x * znak, 0, BALISTA_KONIEC.z)


func _animuj_baliste(n: Node, d: Dictionary, stan: String, p: float) -> void:
	## Przebieg strzału (p 0..1): zwolnienie ramion (0–0.08), suwak jedzie po cięciwę (0.08–0.35),
	## kołowrót ciągnie suwak z cięciwą i napina ramiona (0.35–0.95), nowy bełt na łożu (> 0.95).
	var nap := 1.0
	var wys := 0.0
	var belt := true
	var kolo := 0.0
	if stan == "atak":
		if p < 0.08:
			nap = 1.0 - p / 0.08
			belt = p < 0.01
		elif p < 0.35:
			nap = 0.0
			wys = (p - 0.08) / 0.27
			belt = false
		elif p < 0.95:
			var q := (p - 0.35) / 0.6
			nap = q
			wys = 1.0 - q
			belt = false
			kolo = q * TAU * 3.0
	var kat := lerpf(BALISTA_ZWOLNIONA, 0.0, nap)
	# lewe ramię obraca się o +kąt, prawe o –kąt: końce wychylają się do przodu (+Z) i na zewnątrz
	_obroc(d, "balista_ramie_l", Basis(Vector3.UP, kat))
	_obroc(d, "balista_ramie_p", Basis(Vector3.UP, -kat))
	var tl := _koniec_ramienia(d, "balista_ramie_l", kat)
	var tp := _koniec_ramienia(d, "balista_ramie_p", -kat)
	var srodek_zwolniony := (_koniec_ramienia(d, "balista_ramie_l", BALISTA_ZWOLNIONA) + _koniec_ramienia(d, "balista_ramie_p", -BALISTA_ZWOLNIONA)) / 2.0
	var zaczep: Vector3 = (d["balista_suwak"][1] as Transform3D).origin
	var przes := Vector3(0, 0, wys * (srodek_zwolniony.z - zaczep.z))
	_obroc(d, "balista_suwak", Basis.IDENTITY, przes)
	_obroc(d, "balista_belt", Basis.IDENTITY, przes)
	(d["balista_belt"][0] as Node3D).visible = belt
	_obroc(d, "balista_kolowrot", Basis(Vector3.RIGHT, kolo))
	# cięciwa: od końców ramion do zaczepu (naciągnięta) albo prosto między ramionami (po strzale)
	var sr := ((tl + tp) / 2.0).lerp(zaczep + przes, nap)
	var linki: Array = n.get_meta("cieciwy", [])
	if linki.is_empty():
		var korzen: Node3D = (d["balista_suwak"][0] as Node3D).get_parent()
		var m := StandardMaterial3D.new()
		m.albedo_color = Color(0.88, 0.84, 0.72)
		for i in 2:
			var mi := MeshInstance3D.new()
			var cm := CylinderMesh.new()
			cm.top_radius = 0.009
			cm.bottom_radius = 0.009
			cm.height = 1.0
			cm.radial_segments = 4
			cm.rings = 1
			mi.mesh = cm
			mi.material_override = m
			korzen.add_child(mi)
			linki.append(mi)
		n.set_meta("cieciwy", linki)
	_linka(linki[0], tl, sr)
	_linka(linki[1], tp, sr)


func _linka(mi: MeshInstance3D, a: Vector3, b: Vector3) -> void:
	var y := b - a
	if y.length() < 0.001:
		return
	var x := y.cross(Vector3.UP if absf(y.normalized().y) < 0.9 else Vector3.RIGHT).normalized()
	var z := x.cross(y.normalized())
	mi.transform = Transform3D(Basis(x, y, z), (a + b) / 2.0)


# ----------------------------------------------------------------- łucznik
const DLON_PRAWA := Vector3(0.28, 0.9, 0.26)    # prawa dłoń w spoczynku (współrzędne modelu, Godot)


func _cieciwa_konce(d: Dictionary) -> Array:
	## Końce łuku w układzie lewej ręki (liczone raz z siatki cięciwy z Blendera).
	var cie: MeshInstance3D = d["cieciwa_luku"][0]
	if cie.has_meta("konce"):
		return cie.get_meta("konce")
	var bb := cie.mesh.get_aabb()
	var os_ := 0
	for i in 3:
		if bb.size[i] > bb.size[os_]:
			os_ = i
	var sr := bb.get_center()
	var pol := Vector3.ZERO
	pol[os_] = bb.size[os_] / 2.0
	var tr: Transform3D = d["cieciwa_luku"][1]
	var reka: Transform3D = d["reka_l"][1]
	var w := [reka.affine_inverse() * (tr * (sr - pol)), reka.affine_inverse() * (tr * (sr + pol))]
	cie.set_meta("konce", w)
	cie.visible = false
	return w


func _animuj_lucznika(n: Node, d: Dictionary, stan: String, p: float) -> void:
	## Przebieg (p 0..1): naciąganie ze strzałą (0–0.42), celowanie (–0.5), strzał (0.5–0.54), powrót (–0.9).
	var nap := 0.0
	var poza := 0.0
	var nalozona := false
	if stan == "atak":
		if p < 0.42:
			nap = smoothstep(0.0, 0.42, p)
			poza = nap
			nalozona = true
		elif p < 0.5:
			nap = 1.0
			poza = 1.0
			nalozona = true
		elif p < 0.54:
			nap = 1.0 - (p - 0.5) / 0.04
			poza = 1.0
		else:
			poza = 1.0 - smoothstep(0.54, 0.9, p)
		# łuk wysunięty do celu, prawa dłoń ciągnie cięciwę pod brodę
		_obroc(d, "reka_l", Basis(Vector3.RIGHT, -0.75 * poza) * Basis(Vector3.BACK, -0.25 * poza))
		_obroc(d, "reka_p", Basis(Vector3.RIGHT, -0.95 * poza) * Basis(Vector3.UP, 0.55 * poza))
		_obroc(d, "glowa", Basis(Vector3.UP, 0.25 * poza))
	var konce := _cieciwa_konce(d)
	var rl: Transform3D = (d["reka_l"][0] as Node3D).transform
	var rp: Transform3D = (d["reka_p"][0] as Node3D).transform
	var g1: Vector3 = rl * konce[0]
	var g2: Vector3 = rl * konce[1]
	var prosto := (g1 + g2) / 2.0
	var dlon: Vector3 = rp * ((d["reka_p"][1] as Transform3D).affine_inverse() * DLON_PRAWA)
	var sr := prosto.lerp(dlon, nap * 0.85)
	var linki: Array = n.get_meta("cieciwy", [])
	var korzen: Node3D = (d["reka_l"][0] as Node3D).get_parent()
	if linki.is_empty():
		var m := StandardMaterial3D.new()
		m.albedo_color = Color(0.9, 0.86, 0.74)
		for i in 3:
			var mi := MeshInstance3D.new()
			var cm := CylinderMesh.new()
			cm.top_radius = 0.006 if i < 2 else 0.011
			cm.bottom_radius = cm.top_radius
			cm.height = 1.0
			cm.radial_segments = 4
			cm.rings = 1
			mi.mesh = cm
			var mm := m
			if i == 2:                                  # nałożona strzała
				mm = StandardMaterial3D.new()
				mm.albedo_color = Color(0.7, 0.52, 0.3)
			mi.material_override = mm
			korzen.add_child(mi)
			linki.append(mi)
		n.set_meta("cieciwy", linki)
	_linka(linki[0], g1, sr)
	_linka(linki[1], g2, sr)
	var strzala: MeshInstance3D = linki[2]
	strzala.visible = nalozona and nap > 0.05
	if strzala.visible:
		var kier := (prosto - sr).normalized()
		if kier.length() < 0.5:
			kier = Vector3.BACK
		_linka(strzala, sr, sr + kier * 0.78)
	n.set_meta("grot", korzen.global_transform * (prosto + (prosto - sr).normalized() * 0.3))


# ----------------------------------------------------------------- pociski
func _pocisk(rodzic: Node3D, skad: Vector3, dokad: Vector3, czas: float, rodzaj: String, wysokosc: float, wbij := false) -> Node3D:
	## Strzała albo bełt lecący łukiem; wbity zostaje w ziemi (ustawiony pod kątem lotu).
	var belt := rodzaj == "belt"
	var b := Node3D.new()
	var drzewce := MeshInstance3D.new()
	var cm := CylinderMesh.new()
	cm.top_radius = 0.018 if belt else 0.01
	cm.bottom_radius = cm.top_radius
	cm.height = 1.1 if belt else 0.8
	drzewce.mesh = cm
	drzewce.rotation.x = PI / 2
	var md := StandardMaterial3D.new()
	md.albedo_color = Color(0.72, 0.55, 0.34)
	drzewce.material_override = md
	b.add_child(drzewce)
	var grot := MeshInstance3D.new()
	var gm := CylinderMesh.new()
	gm.top_radius = 0.0
	gm.bottom_radius = 0.04 if belt else 0.025
	gm.height = 0.14 if belt else 0.09
	grot.mesh = gm
	grot.rotation.x = -PI / 2
	grot.position.z = -cm.height / 2 - 0.04
	var mg := StandardMaterial3D.new()
	mg.albedo_color = Color(0.7, 0.72, 0.76)
	mg.metallic = 0.6
	grot.material_override = mg
	b.add_child(grot)
	if not belt:                                        # lotki strzały
		for k in 3:
			var l := MeshInstance3D.new()
			var lm := BoxMesh.new()
			lm.size = Vector3(0.005, 0.05, 0.12)
			l.mesh = lm
			l.position = Vector3(0, 0, cm.height / 2 - 0.08)
			l.rotation.z = k * TAU / 3
			var ml := StandardMaterial3D.new()
			ml.albedo_color = Color(0.92, 0.9, 0.86) if k else Color(0.75, 0.15, 0.15)
			l.material_override = ml
			b.add_child(l)
	rodzic.add_child(b)
	b.global_position = skad
	var tor := func(u: float) -> Vector3:
		return skad.lerp(dokad, u) + Vector3.UP * sin(u * PI) * wysokosc
	var tw := b.create_tween()
	tw.tween_method(func(u: float):
		var p: Vector3 = tor.call(u)
		var nast: Vector3 = tor.call(minf(u + 0.04, 1.0) if u < 0.96 else 1.0)
		if u >= 0.96:
			nast = p + (p - tor.call(u - 0.04))
		b.global_position = p
		if nast.distance_to(p) > 0.001:
			b.look_at(nast, Vector3.UP), 0.0, 1.0, czas)
	tw.tween_callback(func():
		if not wbij:
			b.queue_free()
		else:
			b.global_position -= b.global_transform.basis.z * 0.15)     # grot wbija się w ziemię
	return b


func lot_belta(rodzic: Node3D, skad: Vector3, dokad: Vector3, czas := 0.4) -> void:
	_pocisk(rodzic, skad, dokad, czas, "belt", 0.6)
	get_tree().create_timer(czas).timeout.connect(func(): dzwiek("tarcza"))


func lot_strzaly(rodzic: Node3D, skad: Vector3, dokad: Vector3, czas := 0.45, wbij := false) -> Node3D:
	return _pocisk(rodzic, skad, dokad, czas, "strzala", 1.4, wbij)


func _krok(n: Node, faza: float, amp: float) -> void:
	## Zgodność wsteczna: marsz (amp > 0.2) albo spoczynek.
	animuj_postac(n, "idzie" if amp > 0.2 else "stoi", faza)


# ===================================================================== wejście
func pole_pod_myszka(pm: Vector2) -> Vector2i:
	var o := kamera.project_ray_origin(pm)
	var d := kamera.project_ray_normal(pm)
	if absf(d.y) < 0.001:
		return Vector2i(-1, -1)
	# dwa przybliżenia wysokości terenu
	var h := 0.0
	var wyn := Vector2i(-1, -1)
	for k in 3:
		var tt := (h - o.y) / d.y
		var p := o + d * tt
		wyn = Vector2i(int(floor(p.x / T)), int(floor(p.z / T)))
		if teren(wyn.x, wyn.y) == "":
			return Vector2i(-1, -1)
		h = maxf(wysokosc(wyn.x, wyn.y), POZIOM_WODY)
	return wyn


func _unhandled_input(e: InputEvent) -> void:
	if tryb == "serwer" or S.is_empty() or scena != "gra":
		return
	if e is InputEventMouseButton:
		var mb := e as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_WHEEL_UP and mb.pressed:
			odl = clampf(odl - 2.0, 10.0, 60.0)
		elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN and mb.pressed:
			odl = clampf(odl + 2.0, 10.0, 60.0)
		elif mb.button_index == MOUSE_BUTTON_RIGHT:
			if mb.pressed:
				if wybrany != "":
					anuluj_wybor()
				przeciaganie = mb.pressed
			else:
				przeciaganie = false
		elif mb.button_index == MOUSE_BUTTON_LEFT and mb.pressed:
			klik_pola(pole_pod_myszka(mb.position))
	elif e is InputEventMouseMotion:
		var mm := e as InputEventMouseMotion
		if przeciaganie:
			cel_kam -= Vector3(mm.relative.x, 0, mm.relative.y).rotated(Vector3.UP, yaw) * odl * 0.0022
		najedz(pole_pod_myszka(mm.position))
	elif e is InputEventKey and e.pressed and not e.echo:
		match e.keycode:
			KEY_Q:
				yaw_cel -= PI / 4
			KEY_E:
				yaw_cel += PI / 4
			KEY_SPACE:
				if moja_tura():
					ui.klik_koniec_tury()
			KEY_ESCAPE:
				anuluj_wybor()
			KEY_C:
				_kamera_na_siedzibe(maxi(S.aktywny if moj_gracz < 0 else moj_gracz, 0))
			KEY_T:
				ui.przelacz_okno("technologie")
			KEY_K:
				ui.przelacz_okno("wojsko")
			KEY_L:
				ui.przelacz_okno("ksiega")
			KEY_M:
				przelacz_muzyke()
			KEY_G:
				przelacz_lektora()
			KEY_H:
				ui.przelacz_okno("pomoc")
			KEY_F11:
				var okno := get_window()
				okno.mode = Window.MODE_WINDOWED if okno.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN


func wybierz_budynek(typ: String) -> void:
	if not moja_tura():
		return
	wybrany = typ
	if is_instance_valid(duch):
		duch.queue_free()
	duch = instancja(typ)
	duch_typ = typ
	_przezroczysty(duch)
	swiat.add_child(duch)
	duch.visible = false
	odswiez_siatke_budowy()
	dzwiek("klik")


func _przezroczysty(n: Node) -> void:
	if n is MeshInstance3D:
		var m := StandardMaterial3D.new()
		m.albedo_color = Color(0.5, 1.0, 0.5, 0.55)
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		(n as MeshInstance3D).material_override = m
	for c in n.get_children():
		_przezroczysty(c)


func anuluj_wybor() -> void:
	wybrany = ""
	if is_instance_valid(duch):
		duch.queue_free()
	duch = null
	odswiez_siatke_budowy()
	ui.odswiez()


func najedz(pole: Vector2i) -> void:
	najechane = pole
	if pole.x < 0:
		kursor.visible = false
		if is_instance_valid(duch):
			duch.visible = false
		return
	kursor.visible = true
	kursor.position = pozycja(pole.x, pole.y) + Vector3(0, 0.07, 0)
	kursor.position.y = maxf(kursor.position.y, POZIOM_WODY + 0.05)
	var km: StandardMaterial3D = kursor.material_override
	if wybrany != "":
		var ok: bool = moze_budowac(S.aktywny, wybrany, pole.x, pole.y)[0]
		km.albedo_color = Color(0.3, 1, 0.3, 0.4) if ok else Color(1, 0.25, 0.2, 0.45)
		if is_instance_valid(duch):
			duch.visible = true
			duch.position = pozycja(pole.x, pole.y)
			_koloruj_ducha(duch, ok)
	else:
		km.albedo_color = Color(1, 0.9, 0.4, 0.3)
	ui.najechane_pole(pole)


func _koloruj_ducha(n: Node, ok: bool) -> void:
	if n is MeshInstance3D and n.material_override:
		(n.material_override as StandardMaterial3D).albedo_color = Color(0.5, 1.0, 0.5, 0.55) if ok else Color(1, 0.4, 0.35, 0.55)
	for c in n.get_children():
		_koloruj_ducha(c, ok)


func klik_pola(pole: Vector2i) -> void:
	if pole.x < 0 or not moja_tura():
		return
	if wybrany != "":
		if akcja_buduj(wybrany, pole.x, pole.y):
			if not Input.is_key_pressed(KEY_SHIFT):
				anuluj_wybor()
		return
	var zi := zagon_na(pole.x, pole.y)
	if zi >= 0:
		ui.okno_przechwytu(zi)
		return
	for z in R.znajdzki:
		if int(z[0]) == pole.x and int(z[1]) == pole.y and not ("%d,%d" % [pole.x, pole.y]) in S.znalezione:
			if wlasc(pole.x, pole.y) == S.aktywny:
				akcja_znajdzka(pole.x, pole.y)
			else:
				ui.toast("Coś tu błyszczy… Poszerz granice, żeby to zbadać.")
			return
	for z in R.zabytki:
		if int(z[0]) == pole.x and int(z[1]) == pole.y:
			ui.okno_info(z[3], z[4], z[2])
			return
	var s0: Array = R.start[0]
	if pole == Vector2i(s0[0], s0[1] + 1) or pole == Vector2i(s0[0] - 1, s0[1] + 1):
		ui.rada(D.rady[rng.randi_range(0, D.rady.size() - 1)])
		return
	var bi := budynek_na(pole.x, pole.y)
	if bi >= 0:
		ui.info_budynku(bi)


# ===================================================================== autotest
func _ok(warunek: bool, opis: String) -> bool:
	if not warunek:
		print("TEST_BLAD: ", opis)
	return warunek


func _znajdz_pole(p: int, typ: String) -> Vector2i:
	przelicz_wlasnosc()
	for y in N:
		for x in N:
			var m := moze_budowac(p, typ, x, y)
			if m[0]:
				return Vector2i(x, y)
	return Vector2i(-1, -1)


func _rozszerz(p: int) -> void:
	## Test: stawia chaty/domy na skraju terytorium, by poszerzyć granice.
	przelicz_wlasnosc()
	var dom := "chata" if R.epoka == "krolestwo" else "domus"
	gr(p).zasoby.drewno += 20
	gr(p).zasoby.kamien += 20
	for y in N:
		for x in N:
			if moze_budowac(p, dom, x, y)[0] and (x + y) % 3 == 0:
				akcja_buduj(dom, x, y)
				przelicz_wlasnosc()
				return


func samotest() -> void:
	var ok := true
	print("TEST: start, rozdziałów: ", D.rozdzialy.size())
	for ri in D.rozdzialy.size():
		rozpocznij_rozdzial(ri, [{"imie": "Test", "rod": 0}], "kampania", 1)
		var p := 0
		var r: Dictionary = R
		for proba in 40:
			gr(p).zasoby = {"zboze": 400, "drewno": 400, "kamien": 400, "denary": 400}
			var wszystkie := true
			for c in r.cele:
				if c.typ == "buduj" and ile_budynkow(p, c.co) < int(c.ile):
					wszystkie = false
					var pole := _znajdz_pole(p, c.co)
					if pole.x >= 0:
						akcja_buduj(c.co, pole.x, pole.y)
					else:
						_rozszerz(p)
				elif c.typ == "tech" and not ma_tech(p, c.co):
					wszystkie = false
					# wymagane technologie (np. budynki)
					akcja_tech(c.co, true)
			for typ in D.budynki:
				var b: Dictionary = D.budynki[typ]
				if b.has("wymaga") and not ma_tech(p, b.wymaga) and r.epoka in b.epoki:
					for c in r.cele:
						if c.typ == "buduj" and c.co == typ:
							akcja_tech(b.wymaga, true)
			akcja_koniec_tury()
			if S.koniec:
				break
			gr(p).chwala += 10
			if mozna_bitwe(p)[0]:
				akcja_bitwa_wynik(true, 1, 1)
				akcja_koniec_tury()
				break
			if wszystkie:
				continue
		ok = _ok(K.ukonczone.has(r.id), "rozdział %s nieukończony (tura %d, cele %s)" % [r.id, int(S.tura), str(gr(0).cele_ok)]) and ok
		print("TEST: rozdział %d %s – tura %d, chwała %d, budynków %d" % [ri + 1, r.id, int(S.tura), int(gr(0).chwala), S.budynki.size()])
	# zagony i mury
	rozpocznij_rozdzial(1, [{"imie": "A", "rod": 0}, {"imie": "B", "rod": 1}], "hotseat", 1)
	ok = _ok(S.gracze.size() == 2, "hotseat: 2 graczy") and ok
	for i in 12:
		akcja_koniec_tury()
	ok = _ok(int(S.tura) == 7, "hotseat: tura 7, jest %d" % int(S.tura)) and ok
	_wyslij_zagon()
	ok = _ok(S.zagony.size() >= 1, "zagon wysłany") and ok
	for i in 40:
		_ruch_zagonow()
	ok = _ok(S.zagony.size() == 0, "zagon dotarł do celu") and ok
	# zapis/odczyt JSON
	var tekst := JSON.stringify(S)
	var odczyt = JSON.parse_string(tekst)
	ok = _ok(typeof(odczyt) == TYPE_DICTIONARY and odczyt.gracze.size() == 2, "JSON stanu") and ok
	ustaw_stan(odczyt)
	akcja_koniec_tury()
	ok = _ok(int(S.aktywny) == 1, "po wczytaniu aktywny gracz 1") and ok
	# bitwa – pełna symulacja zasad
	var wynik_b = await bitwa.test_zasad()
	ok = _ok(wynik_b, "zasady bitwy") and ok
	# sieć: serwer + 2 klientów w jednym procesie
	var wynik_s = await siec.samotest()
	ok = _ok(wynik_s, "sieć (serwer pokoi i 2 klientów)") and ok
	print("TEST_WYNIK: ", "OK" if ok else "BLAD")
	get_tree().quit(0 if ok else 1)


func test_online(rola: String, adres: String, plik_kodu: String) -> void:
	## Test dwóch prawdziwych gier online: --bot host|gosc ws://adres plik_z_kodem
	muzyka_on = false
	lektor_on = false
	siec.polacz(adres, "Bot-" + rola)
	if rola == "host":
		siec.utworz_pokoj()
		while siec.kod == "":
			await get_tree().process_frame
		var f := FileAccess.open(plik_kodu, FileAccess.WRITE)
		f.store_string(siec.kod)
		f.close()
		while siec.gracze_lobby.size() < 2:
			await get_tree().process_frame
		siec.rozpocznij_gre(1, 1)
	else:
		while not FileAccess.file_exists(plik_kodu):
			await get_tree().create_timer(0.2).timeout
		await get_tree().create_timer(0.3).timeout
		siec.dolacz(FileAccess.get_file_as_string(plik_kodu).strip_edges())
	var limit := 0.0
	var moje_tury := 0
	while limit < 60.0:
		await get_tree().create_timer(0.25).timeout
		limit += 0.25
		if S.is_empty() or S.get("tryb", "") != "online":
			continue
		if int(S.tura) >= 4:
			print("BOT_%s_OK tura %d, budynków %d, gracze %d" % [rola, int(S.tura), S.budynki.size(), S.gracze.size()])
			get_tree().quit(0)
			return
		if moja_tura():
			ui.zamknij_wszystko()
			var pole := _znajdz_pole(moj_gracz, "pole")
			if pole.x >= 0:
				akcja_buduj("pole", pole.x, pole.y)
			moje_tury += 1
			akcja_koniec_tury()
	print("BOT_%s_BLAD tura %s" % [rola, str(S.get("tura", -1))])
	get_tree().quit(1)


# ===================================================================== zrzuty ekranu
func _zrzut(kat: String, nazwa: String) -> void:
	for i in 6:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(kat.path_join(nazwa + ".png"))
	print("ZRZUT: ", nazwa)


func zrzuty(kat: String) -> void:
	DirAccess.make_dir_recursive_absolute(kat)
	tryb = ""
	muzyka_on = false
	lektor_on = false
	pokaz_tytul()
	await get_tree().create_timer(0.5).timeout
	await _zrzut(kat, "01_tytul")
	pokaz_mape(2, func(): pass)
	await get_tree().create_timer(4.5).timeout
	await _zrzut(kat, "02_mapa_imperium")
	scena = "intro"
	ui.intro_rozdzial = 0
	ui.pokaz_ekran()
	await get_tree().create_timer(2.0).timeout
	await _zrzut(kat, "03_wstep")
	for ri in [0, 4, 6]:
		rozpocznij_rozdzial(ri, [{"imie": "Damian", "rod": 0}], "kampania", 1)
		gr(0).zasoby = {"zboze": 200, "drewno": 200, "kamien": 200, "denary": 200}
		var plan := ["pole", "pole", "tartak", "kamieniolom", "targ", "swiatynia", "mury", "koszary", "domus", "chata", "chata", "winnica", "akwedukt", "termy", "amfiteatr", "bazylika", "insula"]
		for tch in ["luk", "beton", "hypokaustum", "chrzescijanstwo"]:
			if R.epoka in ["cesarstwo", "schylek"] and not ma_tech(0, tch):
				gr(0).techy.append(tch)
		for k in 3:
			for typ in plan:
				var pole := _znajdz_pole(0, typ)
				if pole.x >= 0:
					akcja_buduj(typ, pole.x, pole.y)
			akcja_koniec_tury()
			ui.zamknij_wszystko()
		_wyslij_zagon()
		_ruch_zagonow()
		_ruch_zagonow()
		odswiez_swiat()
		_kamera_na_siedzibe(0)
		kamera.position = cel_kam + Vector3(0, 30, 20)
		ui.zamknij_wszystko()
		scena = "gra"
		ui.pokaz_ekran()
		await get_tree().create_timer(1.2).timeout
		await _zrzut(kat, "04_rozdzial_%d_%s" % [ri + 1, R.id])
	wybierz_budynek("domus")
	najedz(Vector2i(int(R.start[0][0]) + 2, int(R.start[0][1]) + 2))
	await _zrzut(kat, "05_budowa")
	anuluj_wybor()
	ui.przelacz_okno("technologie")
	await _zrzut(kat, "06_technologie")
	ui.zamknij_wszystko()
	ui.zagadka_techu("solidus")
	await _zrzut(kat, "07_zagadka")
	ui.zamknij_wszystko()
	ui.przelacz_okno("wojsko")
	await _zrzut(kat, "08_wojsko")
	ui.zamknij_wszystko()
	ui.pokaz_wydarzenie("moneta")
	await _zrzut(kat, "09_wydarzenie")
	ui.zamknij_wszystko()
	ui.przelacz_okno("ksiega")
	await _zrzut(kat, "10_ksiega")
	ui.zamknij_wszystko()
	bitwa.rozpocznij()
	await get_tree().create_timer(1.0).timeout
	await _zrzut(kat, "11_bitwa_start")
	bitwa.faza = "pytanie"
	ui.pytanie_rady(func(ok): pass, 1)
	await _zrzut(kat, "11b_bitwa_pytanie")
	ui.zamknij_okno(false)
	bitwa.pomin_pytanie(true)
	await get_tree().create_timer(0.8).timeout
	await _zrzut(kat, "12_bitwa_karty")
	bitwa.reka[0] = "balista"
	Engine.time_scale = 0.1          # zwolnione tempo, żeby złapać bełt w locie
	bitwa.zagraj(0)
	await get_tree().create_timer(0.3).timeout
	await _zrzut(kat, "13b_bitwa_belt")
	Engine.time_scale = 1.0
	await get_tree().create_timer(1.0).timeout
	# łucznicy strzelają z miejsca do nadbiegającej piechoty wroga (zwolnione tempo)
	var czekaj := 0
	while bitwa.faza != "wybor" and czekaj < 400:
		await get_tree().process_frame
		czekaj += 1
	bitwa.reka[0] = "lucznicy"
	bitwa.karta_wroga = "maksencjusz_pretorianie"
	bitwa.ukryta = ""
	Engine.time_scale = 0.1
	bitwa.zagraj(0)
	await get_tree().create_timer(0.42).timeout
	await _zrzut(kat, "13c_lucznik_naciaga")
	await get_tree().create_timer(0.2).timeout
	await _zrzut(kat, "13d_strzaly")
	Engine.time_scale = 1.0
	await get_tree().create_timer(1.0).timeout
	await _zrzut(kat, "13_bitwa_starcie")
	bitwa.zakoncz()
	rozpocznij_rozdzial(3, [{"imie": "Ala", "rod": 0}, {"imie": "Kuba", "rod": 1}, {"imie": "Ola", "rod": 2}], "hotseat", 1)
	for k in 6:
		var p: int = S.aktywny
		for typ in ["pole", "tartak", "koszary", "mury"]:
			gr(p).zasoby = {"zboze": 50, "drewno": 50, "kamien": 50, "denary": 50}
			var pole := _znajdz_pole(p, typ)
			if pole.x >= 0:
				akcja_buduj(typ, pole.x, pole.y)
		akcja_koniec_tury()
		ui.zamknij_wszystko()
	scena = "gra"
	ui.pokaz_ekran()
	cel_kam = Vector3(N, 0, N)
	odl = 50
	await get_tree().create_timer(1.2).timeout
	await _zrzut(kat, "14_wieloosobowa")
	scena = "lobby"
	ui.pokaz_ekran()
	await _zrzut(kat, "15_lobby")
	scena = "final"
	ui.pokaz_ekran()
	await get_tree().create_timer(1.0).timeout
	await _zrzut(kat, "16_final")
	# woda: wybrzeże pod Zamą i zbliżenie na koryto Tybru
	for ujecie in [[2, Vector2(7, 9), 26.0, "17_woda_wybrzeze"], [0, Vector2(7.5, 13), 14.0, "18_woda_tyber"]]:
		rozpocznij_rozdzial(ujecie[0], [{"imie": "Damian", "rod": 0}], "kampania", 1)
		ui.zamknij_wszystko()
		scena = "gra"
		ui.pokaz_ekran()
		cel_kam = Vector3(ujecie[1].x * T, 0, ujecie[1].y * T)
		odl = ujecie[2]
		yaw_cel = 0.6
		yaw = 0.6
		kamera.position = cel_kam + Vector3(0, 30, 20)
		await get_tree().create_timer(2.5).timeout
		await _zrzut(kat, ujecie[3])
	# ożywione budynki z bliska: dwie klatki, żeby widać było ruch (budynki stawiane bezpośrednio wokół siedziby)
	rozpocznij_rozdzial(4, [{"imie": "Damian", "rod": 0}], "kampania", 1)
	var s0 := Vector2i(int(R.start[0][0]), int(R.start[0][1]))
	var plan := ["tartak", "targ", "koszary", "kamieniolom", "pole", "swiatynia", "mury", "termy", "insula", "winnica", "kuria", "chata", "rusztowanie"]
	var k := 0
	for dy in range(-2, 3):
		for dx in range(-2, 3):
			if k >= plan.size() or (dx == 0 and dy == 0) or (dx == -1 and dy == 1):
				continue
			var x := s0.x + dx
			var y := s0.y + dy
			if teren(x, y) in ["", "~", "m", "g"] or budynek_na(x, y) >= 0 or zajete_dekoracja(x, y):
				continue
			var typ: String = plan[k]
			S.budynki.append({"typ": "domus" if typ == "rusztowanie" else typ, "x": x, "y": y, "wl": 0, "gotowy": typ != "rusztowanie"})
			k += 1
	zbuduj_swiat()
	ui.zamknij_wszystko()
	scena = "gra"
	ui.pokaz_ekran()
	cel_kam = pozycja(s0.x, s0.y)
	cel_kam.y = 0
	odl = 17.0
	yaw_cel = -0.4
	yaw = -0.4
	kamera.position = cel_kam + Vector3(0, 20, 12)
	await get_tree().create_timer(3.0).timeout
	await _zrzut(kat, "19_budynki_a")
	await get_tree().create_timer(0.45).timeout
	await _zrzut(kat, "19_budynki_b")
	# galeria ruchu postaci i jednostek (marsz, galop, słoń, peleryna, pisanie, cios)
	var scenka := Node3D.new()
	scenka.position = POLE_BITWY + Vector3(0, 0, 40)
	add_child(scenka)
	var ziemia := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(40, 20)
	ziemia.mesh = pm
	ziemia.material_override = _material_terenu()
	scenka.add_child(ziemia)
	var obsada := [["legionista", "idzie"], ["ekwita", "idzie"], ["slon", "idzie"], ["cezar", "stoi"], ["damian", "stoi"], ["galijczyk", "atak"], ["hun", "idzie"], ["balista", "atak"]]
	var aktorzy := []
	for i in obsada.size():
		var u := instancja(obsada[i][0])
		u.position = Vector3(-6.3 + i * 1.8, 0, 0)
		u.rotation.y = -0.5 if obsada[i][1] != "atak" else 0.3
		if obsada[i][0] == "damian":
			u.set_meta("postac", "damian")
		scenka.add_child(u)
		aktorzy.append([u, obsada[i][1]])
	scena = "galeria"
	ui.pokaz_ekran()
	kamera.position = scenka.position + Vector3(0, 3.0, 12.5)
	kamera.look_at(scenka.position + Vector3(0, 1.1, 0))
	ustaw_glebie(11.5, 0.5, true)
	for klatka in ["20_ruch_a", "20_ruch_b", "20_ruch_c"]:
		var t0 := t
		while t - t0 < {"20_ruch_a": 0.6, "20_ruch_b": 0.35, "20_ruch_c": 0.9}[klatka]:
			for ak in aktorzy:
				var cykl := fmod(t * 0.45, 1.0) if ak[0].name.begins_with("balista") or ak[0].has_node("balista_suwak") else fmod(t * 1.2, 1.0)
				animuj_postac(ak[0], ak[1], t * 7.0, cykl if ak[1] == "atak" else 0.0)
			await get_tree().process_frame
		await _zrzut(kat, klatka)
	# balista z bliska w czterech fazach: naciągnięta, po strzale, suwak po cięciwę, przeładowanie
	var bal := instancja("balista")
	bal.position = Vector3(0, 0, 0)
	bal.rotation.y = -0.9
	scenka.add_child(bal)
	for ak in aktorzy:
		ak[0].visible = false
	kamera.position = scenka.position + Vector3(2.6, 2.3, 3.4)
	kamera.look_at(scenka.position + Vector3(0, 0.75, 0))
	ustaw_glebie(4.8, 0.5, true)
	for faza in [["21_balista_1_naciagnieta", "stoi", 0.0], ["21_balista_2_strzal", "atak", 0.06], ["21_balista_3_suwak", "atak", 0.3], ["21_balista_4_przeladowanie", "atak", 0.7]]:
		animuj_postac(bal, faza[1], 0.0, faza[2])
		await _zrzut(kat, faza[0])
	# łucznik z bliska: spoczynek, naciąganie, pełne naciągnięcie ze strzałą
	bal.visible = false
	var luc := instancja("lucznik")
	luc.rotation.y = -1.2
	scenka.add_child(luc)
	kamera.position = scenka.position + Vector3(1.2, 1.6, 2.9)
	kamera.look_at(scenka.position + Vector3(0, 1.05, 0))
	for faza in [["22_lucznik_1_spoczynek", "stoi", 0.0], ["22_lucznik_2_naciaga", "atak", 0.25], ["22_lucznik_3_pelne", "atak", 0.46]]:
		animuj_postac(luc, faza[1], 0.0, faza[2])
		await _zrzut(kat, faza[0])
	get_tree().quit()
