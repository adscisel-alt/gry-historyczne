extends Node
## Główny węzeł gry: świat 3D, warstwy interfejsu, stos ekranów, kolejka zdarzeń logiki,
## zapis, dźwięki proceduralne, autotest i tryb zrzutów ekranu.
##   --autotest        przechodzi całą grę automatem (kod wyjścia 0/1)
##   --zrzuty=KATALOG  zapisuje zrzuty ekranu wszystkich lokacji i ekranów (JPG)

const Logika = preload("res://skrypty/logika.gd")
const Swiat = preload("res://skrypty/swiat.gd")
const Hud = preload("res://skrypty/hud.gd")
const Motyw = preload("res://skrypty/motyw.gd")
const Autotest = preload("res://skrypty/autotest.gd")
const Menu = preload("res://skrypty/ekrany/menu.gd")
const Karta = preload("res://skrypty/ekrany/karta.gd")
const Dialog = preload("res://skrypty/ekrany/dialog.gd")
const DamianE = preload("res://skrypty/ekrany/damian.gd")
const MitE = preload("res://skrypty/ekrany/mit.gd")
const Podsumowanie = preload("res://skrypty/ekrany/podsumowanie.gd")
const Dziennik = preload("res://skrypty/ekrany/dziennik.gd")
const Zakonczenie = preload("res://skrypty/ekrany/zakonczenie.gd")
const MINIGRY := {
	"mapa_zaborow": preload("res://skrypty/minigry/mapa.gd"),
	"manifest": preload("res://skrypty/minigry/manifest.gd"),
	"przepustki": preload("res://skrypty/minigry/przepustki.gd"),
	"kolejnosc_koszar": preload("res://skrypty/minigry/koszary.gd"),
	"swiadkowie": preload("res://skrypty/minigry/swiadkowie.gd"),
	"dyplomacja": preload("res://skrypty/minigry/dyplomacja.gd"),
	"prawa_kobiet": preload("res://skrypty/minigry/quizy.gd"),
	"wklady": preload("res://skrypty/minigry/wklady.gd"),
}
const ZAPIS := "user://zapis.json"

var logika = null
var swiat: Node3D
var warstwa_post: CanvasLayer
var hud: Control
var warstwa_hud: CanvasLayer
var korzen_nakladek: Control
var toasty: VBoxContainer
var stos: Array = []
var kolejka: Array = []
var tryb := "menu"
var wybrany := ""
var _dzwieki: Dictionary = {}
var _odtwarzacze: Array = []
var sciezka_zapisu := ZAPIS


func _ready() -> void:
	logika = Logika.new()
	swiat = Swiat.new()
	swiat.name = "Swiat"
	add_child(swiat)
	# warstwa 1: fotografia z 1918 r. (sepia, ziarno, winieta) nad światem 3D
	warstwa_post = CanvasLayer.new()
	warstwa_post.layer = 1
	var post := ColorRect.new()
	post.set_anchors_preset(Control.PRESET_FULL_RECT)
	post.size = Vector2(1280, 720)
	post.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sm := ShaderMaterial.new()
	sm.shader = load("res://shadery/post.gdshader")
	post.material = sm
	warstwa_post.add_child(post)
	add_child(warstwa_post)
	# warstwa 2: HUD lokacji
	warstwa_hud = CanvasLayer.new()
	warstwa_hud.layer = 2
	add_child(warstwa_hud)
	hud = Hud.new(self)
	warstwa_hud.add_child(hud)
	# warstwa 3: ekrany i nakładki
	var warstwa_nakladek := CanvasLayer.new()
	warstwa_nakladek.layer = 3
	add_child(warstwa_nakladek)
	korzen_nakladek = Control.new()
	korzen_nakladek.set_anchors_preset(Control.PRESET_FULL_RECT)
	korzen_nakladek.size = Vector2(1280, 720)
	korzen_nakladek.mouse_filter = Control.MOUSE_FILTER_IGNORE
	warstwa_nakladek.add_child(korzen_nakladek)
	# warstwa 4: powiadomienia
	var warstwa_toastow := CanvasLayer.new()
	warstwa_toastow.layer = 4
	add_child(warstwa_toastow)
	toasty = VBoxContainer.new()
	toasty.position = Vector2(820, 80)
	toasty.size = Vector2(440, 200)
	toasty.alignment = BoxContainer.ALIGNMENT_BEGIN
	toasty.mouse_filter = Control.MOUSE_FILTER_IGNORE
	warstwa_toastow.add_child(toasty)
	_przygotuj_dzwieki()
	_pokaz_swiat(false)
	var args := OS.get_cmdline_user_args() + OS.get_cmdline_args()
	for a in args:
		if a == "--autotest":
			sciezka_zapisu = "user://zapis_autotest.json"
			var t = Autotest.new()
			var kod: int = await t.uruchom(self)
			get_tree().quit(kod)
			return
		if a.begins_with("--zrzuty="):
			sciezka_zapisu = "user://zapis_zrzuty.json"
			await zrzuty(a.substr(9))
			get_tree().quit(0)
			return
	ustaw_baze(Menu.new(self))


# ================================================================== stos ekranów
func gora():
	return stos.back() if not stos.is_empty() else null


func wloz(e: Control) -> void:
	stos.append(e)
	korzen_nakladek.add_child(e)


func zdejmij(e: Control) -> void:
	if e in stos:
		stos.erase(e)
		e.queue_free()
	if tryb == "lokacja":
		hud.odswiez()
		swiat.odswiez()


func ustaw_baze(e) -> void:
	for s in stos:
		s.queue_free()
	stos.clear()
	if e != null:
		wloz(e)


func _pokaz_swiat(tak: bool) -> void:
	swiat.visible = tak
	warstwa_post.visible = tak
	warstwa_hud.visible = tak
	if not tak:
		for d in swiat.get_children():
			d.queue_free()
		swiat.janek = null


func czy_swiat_aktywny() -> bool:
	return tryb == "lokacja" and stos.is_empty()


func najechany_hotspot() -> String:
	return swiat.najechany if czy_swiat_aktywny() else ""


func logika_ma_hotspot(hid: String) -> bool:
	for h in logika.hotspoty():
		if h["id"] == hid:
			return true
	return false


# ================================================================== przebieg gry
func jest_zapis() -> bool:
	return FileAccess.file_exists(sciezka_zapisu)


func zapisz() -> void:
	logika.zapisz(sciezka_zapisu)


func nowa_gra() -> void:
	logika = Logika.new()
	kolejka.clear()
	wybrany = ""
	pokaz_karte()


func kontynuuj() -> void:
	var l = Logika.new()
	if not l.wczytaj(sciezka_zapisu):
		nowa_gra()
		return
	logika = l
	kolejka.clear()
	if logika.ukonczona:
		_zakonczenie()
	else:
		pokaz_karte()


func pokaz_karte() -> void:
	tryb = "karta"
	_pokaz_swiat(false)
	ustaw_baze(Karta.new(self))


func rozpocznij_lokacje() -> void:
	if not Dane.lokacje.has(logika.lokacja) or Dane.lokacje[logika.lokacja]["rozdzial"] != logika.dane_rozdzialu()["id"]:
		logika.lokacja = str(logika.dane_rozdzialu()["start"])
	tryb = "lokacja"
	ustaw_baze(null)
	_pokaz_swiat(true)
	swiat.buduj(self, logika.lokacja)
	hud.komunikat_pelny = ""
	hud.komunikat("")
	hud.odswiez()
	zapisz()


func nastepny_rozdzial() -> void:
	var dalej: bool = logika.nastepny_rozdzial()
	zapisz()
	if dalej:
		pokaz_karte()
	else:
		_zakonczenie()


func _zakonczenie() -> void:
	tryb = "koniec"
	_pokaz_swiat(false)
	ustaw_baze(Zakonczenie.new(self))


func do_menu() -> void:
	if tryb == "lokacja":
		zapisz()
	kolejka.clear()
	tryb = "menu"
	_pokaz_swiat(false)
	ustaw_baze(Menu.new(self))


func otworz_dziennik() -> void:
	var g = gora()
	if g == null or g.typ != "dziennik":
		wloz(Dziennik.new(self))


func przelacz_ekran() -> void:
	if DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)


func wybierz_przedmiot(p: String) -> void:
	wybrany = "" if wybrany == p else p
	dzwiek("klik")
	hud.odswiez()


# ================================================================== zdarzenia logiki
func aktywuj(hid: String, przedmiot) -> void:
	var zd: Array
	if przedmiot != null and str(przedmiot) != "":
		zd = logika.uzyj(str(przedmiot), hid)
	else:
		zd = logika.kliknij(hid)
	wybrany = ""
	dzwiek("klik")
	obsluz(zd)


func obsluz(zd: Array) -> void:
	kolejka.append_array(zd)
	przetworz_kolejke()


func na_poczatek(zd: Array) -> void:
	var nowa := zd.duplicate()
	nowa.append_array(kolejka)
	kolejka = nowa
	przetworz_kolejke()


func przetworz_kolejke() -> void:
	var zmiana := false
	while not kolejka.is_empty() and czy_swiat_aktywny():
		var z: Array = kolejka.pop_front()
		zmiana = true
		match z[0]:
			Logika.MOW:
				hud.komunikat(str(z[1]))
			Logika.FAKT, Logika.PRZEDMIOT:
				toast(z[0], z[1])
			Logika.IDZ:
				swiat.buduj(self, str(z[1]))
				dzwiek("kartka")
				zapisz()
			Logika.DIALOG:
				wloz(Dialog.new(self, str(z[1])))
			Logika.MINIGRA:
				wloz(MINIGRY[str(z[1])].new(self))
			Logika.DAMIAN:
				wloz(DamianE.new(self, str(z[1])))
			Logika.MIT:
				wloz(MitE.new(self, str(z[1])))
			Logika.KONIEC_ROZDZIALU:
				wloz(Podsumowanie.new(self))
	if zmiana and tryb == "lokacja":
		swiat.odswiez()
		hud.odswiez()


func toast(rodzaj: String, arg: String) -> void:
	var t := ""
	if rodzaj == Logika.FAKT:
		t = "Nowy fakt w dzienniku: " + str(Dane.fakty[arg]["data"])
	else:
		t = "Do torby: " + str(Dane.przedmioty[arg]["nazwa"])
		dzwiek("kartka")
	var pc := PanelContainer.new()
	pc.add_theme_stylebox_override("panel", Motyw.styl_plaski(Color(0.94, 0.9, 0.82), Motyw.ATRAMENT_JASNY, 2, 5))
	pc.add_child(Motyw.etykieta(t, 16, "plakat", Motyw.ATRAMENT, false))
	pc.mouse_filter = Control.MOUSE_FILTER_IGNORE
	toasty.add_child(pc)
	var tw := pc.create_tween()
	tw.tween_interval(2.6)
	tw.tween_property(pc, "modulate:a", 0.0, 0.4)
	tw.tween_callback(pc.queue_free)
	if tryb == "lokacja":
		hud.odswiez()


func _process(_delta: float) -> void:
	przetworz_kolejke()


func _unhandled_input(e: InputEvent) -> void:
	if e is InputEventKey and e.pressed and not e.echo:
		if e.keycode == KEY_F11:
			przelacz_ekran()
		elif czy_swiat_aktywny():
			if e.keycode == KEY_J:
				otworz_dziennik()
			elif e.keycode == KEY_ESCAPE:
				if wybrany != "":
					wybrany = ""
					hud.odswiez()
				else:
					do_menu()
		return
	if not (e is InputEventMouseButton and e.pressed) or not czy_swiat_aktywny():
		return
	if e.position.y >= 560:
		return
	if e.button_index == MOUSE_BUTTON_LEFT:
		swiat.klik(e.position, wybrany if wybrany != "" else null)
	elif e.button_index == MOUSE_BUTTON_RIGHT:
		if wybrany != "":
			wybrany = ""
			hud.odswiez()
		else:
			var hid: String = swiat.hotspot_pod(e.position)
			if hid != "":
				hud.komunikat(str(logika.hotspot(hid).get("patrz", "")))


# ================================================================== dźwięki proceduralne
func _wav(probki: PackedFloat32Array) -> AudioStreamWAV:
	var dane := PackedByteArray()
	dane.resize(probki.size() * 2)
	for i in probki.size():
		dane.encode_s16(i * 2, int(clampf(probki[i], -1.0, 1.0) * 32000.0))
	var w := AudioStreamWAV.new()
	w.format = AudioStreamWAV.FORMAT_16_BITS
	w.mix_rate = 22050
	w.stereo = false
	w.data = dane
	return w


func _ton(nuty: Array, glosnosc: float) -> AudioStreamWAV:
	var p := PackedFloat32Array()
	for n in nuty:
		var ile := int(22050 * float(n[1]))
		for i in ile:
			var obw := minf(1.0, i / 200.0) * maxf(0.0, 1.0 - float(i) / ile)
			p.append(glosnosc * obw * sin(TAU * float(n[0]) * i / 22050.0))
	return _wav(p)


func _szum(czas: float, glosnosc: float, niski: bool) -> AudioStreamWAV:
	var rng := RandomNumberGenerator.new()
	rng.seed = 4
	var p := PackedFloat32Array()
	var ile := int(22050 * czas)
	var poprz := 0.0
	for i in ile:
		var v := rng.randf_range(-1.0, 1.0)
		if niski:
			poprz = poprz * 0.9 + v * 0.1
			v = poprz * 3.0
		p.append(glosnosc * maxf(0.0, 1.0 - float(i) / ile) * clampf(v, -1.0, 1.0))
	return _wav(p)


func _przygotuj_dzwieki() -> void:
	_dzwieki = {
		"klik": _ton([[880, 0.03]], 0.25),
		"maszyna": _szum(0.025, 0.25, false),
		"stempel": _szum(0.09, 0.5, true),
		"sukces": _ton([[523, 0.12], [659, 0.12], [784, 0.22]], 0.3),
		"blad": _ton([[220, 0.12], [180, 0.2]], 0.3),
		"kartka": _szum(0.12, 0.15, false),
	}
	for i in 4:
		var o := AudioStreamPlayer.new()
		add_child(o)
		_odtwarzacze.append(o)


func dzwiek(nazwa: String) -> void:
	if not _dzwieki.has(nazwa):
		return
	for o in _odtwarzacze:
		if not o.playing:
			o.stream = _dzwieki[nazwa]
			o.play()
			return


# ================================================================== autotest interfejsu
func _rozwiaz_minigre(t, mg) -> void:
	var M: Dictionary = Dane.minigry
	match mg.gid:
		"mapa_zaborow":
			t.sprawdz(not mg.umiesc("Kraków", "pruski"), "mapa: błędne przypisanie odrzucone")
			for m in mg.miasta.duplicate():
				mg.umiesc(m, str(Dane.miasta[m][1]))
		"manifest":
			t.sprawdz(not mg.sprawdz(), "manifest: pusty nie przechodzi")
			for f in M["manifest_fragmenty"].size():
				if M["manifest_fragmenty"][f][1] == null:
					mg.spal(f)
				else:
					mg.poloz(f, int(M["manifest_fragmenty"][f][1]))
			t.sprawdz(mg.sprawdz(), "manifest: poprawny przechodzi")
		"przepustki":
			for doc in M["przepustki"]:
				mg.decyzja(mg.wazna(doc))
		"kolejnosc_koszar":
			var odwrotnie: Array = M["koszary_punkty"].duplicate()
			odwrotnie.reverse()
			for p in odwrotnie:
				mg.dodaj_punkt(p)
			t.sprawdz(not mg.sprawdz() and mg.napiecie == 1, "koszary: zła kolejność podnosi napięcie")
			mg.plan = []
			for p in M["koszary_rozwiazanie"]:
				mg.dodaj_punkt(p)
			mg.sprawdz()
		"swiadkowie":
			for r in M["swiadkowie"]:
				t.sprawdz(mg.wskaz(int(r["falszywe"])), "świadkowie: wskazanie")
				t.sprawdz(mg.pokaz_dowod(str(r["dowod"])), "świadkowie: dowód " + str(r["dowod"]))
				mg.nastepna()
		"dyplomacja":
			for w in mg.najlepsze_wybory():
				mg.odpowiedz(w)
		"prawa_kobiet":
			for q in M["quiz_kobiet"]:
				mg.odpowiedz(int(q[2]))
		"wklady":
			for para in M["wklady"]:
				mg.polacz(str(para[0]), str(para[1]))
	t.sprawdz(mg.wygrana, "minigra wygrana: " + mg.gid)


func autotest_interfejsu(t) -> void:
	# 1) każda lokacja buduje się w 3D i ma wszystkie hotspoty
	tryb = "lokacja"
	_pokaz_swiat(true)
	for lid in Dane.lokacje:
		logika.lokacja = lid
		swiat.buduj(self, lid)
		for h in Dane.lokacje[lid]["hotspoty"]:
			t.sprawdz(swiat.ciala.has(h["id"]), "3D: hotspot %s w %s" % [h["id"], lid])
		await get_tree().process_frame
	print("  14 lokacji 3D zbudowanych")
	# 2) klik myszą w hotspot → raycast → Janek idzie → akcja
	nowa_gra()
	rozpocznij_lokacje()
	await get_tree().physics_frame
	await get_tree().physics_frame
	var cel: Vector3 = swiat.ciala["mapa_sciana"].position
	var ekran := swiat.kamera.unproject_position(cel)
	t.sprawdz(swiat.hotspot_pod(ekran) == "mapa_sciana", "raycast trafia w mapę na ścianie")
	swiat.klik(ekran, null)
	for _i in 400:
		await get_tree().process_frame
		if "zabory" in logika.fakty:
			break
	t.sprawdz("zabory" in logika.fakty, "Janek doszedł do mapy i ją obejrzał")
	# 3) pełne przejście gry przez prawdziwe ekrany
	nowa_gra()
	var kroki: Array = Dane.solucja.duplicate()
	var minigry := {}
	var lokacje := {}
	var odw := {}
	var ostatni_dialog = null
	for _i in 5000:
		await get_tree().process_frame
		if tryb == "koniec":
			break
		var g = gora()
		if g == null and tryb == "lokacja":
			lokacje[logika.lokacja] = true
			if kroki.is_empty():
				break
			var k: Array = kroki.pop_front()
			var hid: String = k[1] if k[0] == "klik" else k[2]
			t.sprawdz(swiat.widoczny(hid), "widoczny hotspot " + hid)
			if k[0] == "klik":
				aktywuj(hid, null)
			else:
				aktywuj(hid, k[1])
			if kroki.size() % 17 == 0:
				otworz_dziennik()
				var dz = gora()
				for z in 5:
					dz.pokaz(z)
					await get_tree().process_frame
				dz.zamknij()
			continue
		if g == null:
			continue
		g.czas = 5.0
		match g.typ:
			"karta", "damian", "podsumowanie":
				g.klik_tla()
			"mit":
				g.wybierz(int(g.mit["dobra"]))
				g.klik_tla()
			"dialog":
				if g != ostatni_dialog:
					ostatni_dialog = g
					odw = {}
				g.t_tekst = 999.0
				if g.rozmowa.zakonczona():
					continue
				odw[g.rozmowa.wezel_id] = true
				var opcje: Array = g.rozmowa.opcje()
				if opcje.is_empty():
					g.dalej()
				else:
					var wybor := opcje.size() - 1
					for i in opcje.size():
						if not odw.has(str(opcje[i]["dalej"])):
							wybor = i
							break
					g.wybierz(wybor)
			"minigra":
				if not g.wygrana:
					minigry[g.gid] = true
					_rozwiaz_minigre(t, g)
				g.zakoncz()
			"dziennik":
				g.zamknij()
	t.sprawdz(tryb == "koniec", "interfejs: dotarto do zakończenia (tryb=%s)" % tryb)
	t.sprawdz(logika.ukonczona, "interfejs: gra ukończona")
	t.sprawdz(lokacje.size() == 14, "interfejs: odwiedzono 14 lokacji (%d)" % lokacje.size())
	t.sprawdz(minigry.size() == 8, "interfejs: zaliczono 8 minigier (%d)" % minigry.size())
	t.sprawdz(jest_zapis(), "zapis gry istnieje")
	otworz_dziennik()
	for z in 5:
		gora().pokaz(z)
		await get_tree().process_frame
	print("  przejście przez interfejs: %d faktów, %d mitów, %d postaci" % [logika.fakty.size(), logika.mity.size(), logika.poznani.size()])


# ================================================================== zrzuty ekranu (CI)
func _zrzut(katalog: String, nazwa: String, klatki: int = 12) -> void:
	for _i in klatki:
		await get_tree().process_frame
	var img := get_viewport().get_texture().get_image()
	img.resize(960, 540, Image.INTERPOLATE_BILINEAR)
	img.save_jpg(katalog.path_join(nazwa + ".jpg"), 0.82)
	print("zrzut: " + nazwa)


func zrzuty(katalog: String) -> void:
	DirAccess.make_dir_recursive_absolute(katalog)
	ustaw_baze(Menu.new(self))
	await _zrzut(katalog, "00_menu")
	nowa_gra()
	await _zrzut(katalog, "01_karta")
	var nr := 2
	for lid in Dane.lokacje:
		logika.rozdzial = Dane.indeks_rozdzialu(str(Dane.lokacje[lid]["rozdzial"]))
		logika.lokacja = lid
		rozpocznij_lokacje()
		for hid in swiat.wezly:
			swiat.wezly[hid].visible = true
		if lid == "krakow_rynek":
			logika.ekwipunek = ["lupa", "orzelek", "opaska"]
			hud.komunikat("Witos: Słup z mapą stoi tam, chłopcze. Pokaż, co wiesz o zaborach.")
			hud.odswiez()
		await _zrzut(katalog, "%02d_%s" % [nr, lid], 20)
		nr += 1
	logika.lokacja = "krakow_rynek"
	logika.rozdzial = 0
	rozpocznij_lokacje()
	wloz(Dialog.new(self, "d_witos"))
	await _zrzut(katalog, "20_dialog", 60)
	ustaw_baze(null)
	wloz(MitE.new(self, "m_kobiety"))
	gora().wybierz(1)
	await _zrzut(katalog, "21_mit")
	ustaw_baze(null)
	var nr_mg := 30
	logika.ekwipunek = ["lupa", "orzelek", "opaska", "odpis_oredzia", "rozklad_jazdy"]
	for gid in MINIGRY:
		wloz(MINIGRY[gid].new(self))
		await _zrzut(katalog, "%02d_mg_%s" % [nr_mg, gid])
		ustaw_baze(null)
		nr_mg += 1
	logika.fakty = Dane.fakty.keys()
	logika.poznani = Dane.historyczne.duplicate()
	for m in Dane.mity:
		logika.mity[m] = true
	for z in 5:
		otworz_dziennik()
		gora().pokaz(z)
		await _zrzut(katalog, "4%d_dziennik" % z)
		ustaw_baze(null)
	_zakonczenie()
	await _zrzut(katalog, "50_zakonczenie")
