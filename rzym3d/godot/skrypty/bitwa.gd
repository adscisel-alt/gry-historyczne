extends Node
## Bitwa kartami w 3D: pytanie rady wojennej, potem rundy – wróg odsłania kartę,
## gracz wystawia swoją. Piechota > jazda > strzelcy > piechota (+3 za przewagę).

const PRZEWAGA := 3
const REKA := 4

var g
var aktywna := false
var faza := ""              # intro, pytanie, wybor, starcie, koniec
var b := {}                 # dane bitwy z rozdziału
var p := 0                  # gracz
var talia := []
var odrzut := []
var reka := []
var wtalia := []
var wodrzut := []
var karta_wroga := ""
var ukryta := ""
var p_hp := 20
var p_max := 20
var e_hp := 20
var e_max := 20
var bonus := 0
var stale_plus := 0
var mody := {}
var uzyte := []
var taktyki := []
var log := []
var runda := 0
var wygrana := false
var pyt_ok := 0
var pyt_all := 0
var ostatnie := {}

# 3D
var scena3d: Node3D
var moje_wezly := []
var wrogie_wezly := []
var walczacy := []
var t := 0.0
var stara_kamera := Transform3D()

# UI
var warstwa: CanvasLayer
var korzen: Control
var pasek_p: ProgressBar
var pasek_e: ProgressBar
var napis_p: Label
var napis_e: Label
var srodek: VBoxContainer
var dol: HBoxContainer
var prawa: VBoxContainer
var dziennik_l: RichTextLabel
var taktyki_box: HBoxContainer


# ===================================================================== zasady
func sila(id: String, moja: bool) -> int:
	var c: Dictionary = g.D.karty[id]
	var s: int = g.sila_karty(p if moja else -1, id)
	if moja:
		s += int(b.get("premia", {}).get(c.typ, 0))
		s += bonus + stale_plus + int(mody.get("plus", 0)) + int(mody.get("typ_plus", {}).get(c.typ, 0))
		var tr: String = b.get("teren", "pole")
		if tr == "las" and c.typ == "strzelcy":
			s += 1
		if tr == "pole" and c.typ == "jazda":
			s += 1
		if tr == "wzgorze" and c.typ == "piechota":
			s += 1
	return s


func bije(a: String, z: String) -> bool:
	return g.D.typy_kart[g.D.karty[a].typ].bije == g.D.karty[z].typ


func rozstrzygnij(moja: String, wroga: String) -> Dictionary:
	var P := sila(moja, true) + (PRZEWAGA if bije(moja, wroga) else 0)
	var es: int = g.sila_karty(-1, wroga)
	es = int(round(es * float(g.D.trudnosci[int(g.S.get("trudnosc", 1))].wrog)))
	es -= int(mody.get("wrog_minus", 0))
	if wroga == "slonie":
		es -= int(mody.get("slonie", 0))
	var E: int = maxi(0, es) + (PRZEWAGA if bije(wroga, moja) and not mody.get("bez_przewagi", false) else 0)
	var tarcza: int = int(g.D.karty[moja].get("tarcza", 0)) + int(mody.get("tarcza", 0))
	var w := {"P": P, "E": E, "dla_mnie": 0, "dla_wroga": 0}
	if P > E:
		w.dla_wroga = P - E + 1
	elif E > P:
		w.dla_mnie = maxi(0, E - P + 2 - tarcza)
	else:
		w.dla_mnie = maxi(0, 1 - tarcza)
		w.dla_wroga = 1
	return w


func przygotuj(gracz: int) -> void:
	p = gracz
	b = g.R.bitwa
	var tr: Dictionary = g.D.trudnosci[int(g.S.get("trudnosc", 1))]
	talia = g.gr(p).talia.duplicate()
	talia.shuffle()
	odrzut = []
	reka = []
	wtalia = b.wrog.duplicate()
	wtalia.shuffle()
	wodrzut = []
	p_max = 20 + 2 * g.ile_budynkow(p, "koszary", true) + mini(10, int(g.gr(p).chwala) / 20)
	p_hp = p_max
	e_max = maxi(8, int(round(float(b.morale) * tr.wrog)))
	e_hp = e_max
	bonus = 0
	stale_plus = 0
	mody = {}
	uzyte = []
	taktyki = b.taktyki.duplicate()
	if g.ma_tech(p, "testudo") and not "testudo" in taktyki:
		taktyki.append("testudo")
	log = []
	runda = 0
	wygrana = false
	pyt_ok = 0
	pyt_all = 0
	karta_wroga = ""
	ukryta = ""


func _dobierz() -> void:
	while reka.size() < REKA:
		if talia.is_empty():
			if odrzut.is_empty():
				break
			talia = odrzut
			odrzut = []
			talia.shuffle()
		reka.append(talia.pop_back())


func _wrog_dobiera() -> String:
	if wtalia.is_empty():
		wtalia = wodrzut
		wodrzut = []
		wtalia.shuffle()
	return wtalia.pop_back()


func nowa_runda() -> void:
	runda += 1
	_dobierz()
	karta_wroga = _wrog_dobiera()
	ukryta = ""
	var tr: Dictionary = g.D.trudnosci[int(g.S.get("trudnosc", 1))]
	if tr.get("sprytny", false):
		# sprytny wróg: z dwóch dobranych kart odsłania tę, która bije więcej kart w twojej ręce
		var druga := _wrog_dobiera()
		if _ile_bije(druga) > _ile_bije(karta_wroga):
			wodrzut.append(karta_wroga)
			karta_wroga = druga
		else:
			wodrzut.append(druga)
	if int(tr.ukryta) > 0 and runda > 1:
		ukryta = _wrog_dobiera()
	mody = {}
	faza = "wybor"


func _ile_bije(karta: String) -> int:
	var n := 0
	for k in reka:
		if bije(karta, k):
			n += 1
	return n


func uzyj_taktyki(id: String) -> void:
	if id in uzyte or faza != "wybor":
		return
	uzyte.append(id)
	var e: Dictionary = g.D.taktyki[id].efekt
	for k in e:
		if k == "stale_plus":
			stale_plus += int(e[k])
		elif k == "typ_plus":
			mody["typ_plus"] = e[k]
		else:
			mody[k] = e[k]
	log.append("Taktyka: %s – %s" % [g.D.taktyki[id].nazwa, g.D.taktyki[id].opis])
	g.dzwiek("rog")
	_odswiez_ui()


func zagraj(i: int) -> void:
	if faza != "wybor" or i < 0 or i >= reka.size():
		return
	var moja: String = reka[i]
	reka.remove_at(i)
	odrzut.append(moja)
	var wroga := karta_wroga
	var sprytny: bool = g.D.trudnosci[int(g.S.get("trudnosc", 1))].get("sprytny", false)
	var zamiana := randf() < 0.5
	if sprytny and ukryta != "":
		# sprytny wróg zamienia kartę tylko wtedy, gdy zakryta wypada lepiej przeciw twojej
		zamiana = rozstrzygnij(moja, ukryta).E - rozstrzygnij(moja, ukryta).P > rozstrzygnij(moja, karta_wroga).E - rozstrzygnij(moja, karta_wroga).P
	if ukryta != "" and zamiana:
		wodrzut.append(karta_wroga)
		wroga = ukryta
		log.append("Wróg zamienił kartę! Wystawia: %s" % g.D.karty[wroga].nazwa)
	elif ukryta != "":
		wodrzut.append(ukryta)
	wodrzut.append(wroga)
	var w := rozstrzygnij(moja, wroga)
	p_hp -= int(w.dla_mnie)
	e_hp -= int(w.dla_wroga)
	ostatnie = {"moja": moja, "wroga": wroga, "w": w}
	var txt := "%s (%d) vs %s (%d): " % [g.D.karty[moja].nazwa, w.P, g.D.karty[wroga].nazwa, w.E]
	if w.P > w.E:
		txt += "zwycięstwo! Wróg traci %d morale." % w.dla_wroga
	elif w.E > w.P:
		txt += "porażka – tracisz %d morale." % w.dla_mnie
	else:
		txt += "remis."
	log.append(txt)
	faza = "starcie"
	if aktywna and g.tryb != "test":
		_animuj_starcie(moja, wroga, w)
		g.dzwiek("miecz")
		_odswiez_ui()
		await get_tree().create_timer(1.6).timeout
	_po_starciu()


func _po_starciu() -> void:
	if e_hp <= 0 or p_hp <= 0:
		wygrana = e_hp <= 0 and p_hp > 0 or (e_hp <= 0 and p_hp <= 0 and e_hp <= p_hp)
		faza = "koniec"
		if aktywna and g.tryb != "test":
			g.dzwiek("tlum" if wygrana else "zle")
			_odswiez_ui()
		return
	nowa_runda()
	if aktywna and g.tryb != "test":
		_ustaw_szyki()
		_odswiez_ui()


func po_pytaniu(dobrze: bool) -> void:
	pyt_all += 1
	if dobrze:
		pyt_ok += 1
		bonus = 1
		p_max += 3
		p_hp += 3
		log.append("Rada wojenna natchniona! Wszystkie karty +1, morale +3.")
		g.dzwiek("dobrze")
	else:
		log.append("Rada się pogubiła… brak premii.")
		g.dzwiek("zle")
	nowa_runda()
	_odswiez_ui()


func test_zasad() -> bool:
	## Autotest: pełne bitwy wszystkich rozdziałów z prostą strategią gracza.
	var ok := true
	var ostatni: Dictionary = g.S.duplicate(true)
	for ri in g.D.rozdzialy.size():
		g.S = g.nowy_stan(ri, [{"imie": "T", "rod": 0}], "kampania", 1)
		g.R = g.D.rozdzialy[ri]
		przygotuj(0)
		po_pytaniu(true)
		var rundy := 0
		while faza != "koniec" and rundy < 200:
			rundy += 1
			# najlepsza karta przeciw odsłoniętej
			var naj := 0
			var najw := -999
			for i in reka.size():
				var w := rozstrzygnij(reka[i], karta_wroga)
				if w.P - w.E > najw:
					najw = w.P - w.E
					naj = i
			if runda == 2 and taktyki.size() > 0:
				uzyj_taktyki(taktyki[0])
			await zagraj(naj)
		if faza != "koniec":
			print("TEST_BLAD: bitwa %s nie skończyła się" % b.nazwa)
			ok = false
		print("TEST: bitwa %s – %s po %d rundach (morale %d:%d)" % [b.nazwa, "wygrana" if wygrana else "przegrana", runda, p_hp, e_hp])
	# poziom Legendarny: sprytny wróg, rozdział egipski
	g.S = g.nowy_stan(4, [{"imie": "T", "rod": 0}], "kampania", 3)
	g.R = g.D.rozdzialy[4]
	przygotuj(0)
	po_pytaniu(true)
	var rr := 0
	while faza != "koniec" and rr < 200:
		rr += 1
		await zagraj(0)
	print("TEST: Legendarny – bitwa %s – %s po %d rundach" % [b.nazwa, "wygrana" if wygrana else "przegrana", runda])
	if faza != "koniec":
		ok = false
	# przewaga typu
	g.S = ostatni
	g.R = g.D.rozdzialy[int(g.S.rozdzial)]
	if not bije("hastati", "ekwici") or bije("ekwici", "hastati"):
		ok = false
	return ok


# ===================================================================== 3D i UI
func rozpocznij() -> void:
	przygotuj(int(g.S.aktywny))
	aktywna = true
	faza = "intro"
	g.scena = "bitwa"
	g.ui.pokaz_ekran()
	g.graj_muzyke("bitwa")
	g.dzwiek("bebny")
	_zbuduj_3d()
	_zbuduj_ui()
	_odswiez_ui()


func zakoncz() -> void:
	aktywna = false
	if is_instance_valid(scena3d):
		scena3d.queue_free()
	if is_instance_valid(warstwa):
		warstwa.queue_free()
	g.scena = "gra"
	g.graj_muzyke(g.D.epoki[g.R.epoka].muzyka)
	g.ui.pokaz_ekran()


func _zakoncz_z_wynikiem() -> void:
	var w := wygrana
	zakoncz()
	g.akcja_bitwa_wynik(w, pyt_ok, pyt_all)
	g.ui.po_bitwie(w)


func pomin_pytanie(dobrze: bool) -> void:
	po_pytaniu(dobrze)


func _zbuduj_3d() -> void:
	if is_instance_valid(scena3d):
		scena3d.queue_free()
	scena3d = Node3D.new()
	scena3d.position = g.POLE_BITWY
	g.add_child(scena3d)
	var ziemia := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(120, 80)
	ziemia.mesh = pm
	var mz := StandardMaterial3D.new()
	var kol := {"pole": Color("8fae58"), "wzgorze": Color("a39e66"), "las": Color("5f8a45"), "gory": Color("9a927f"), "rzeka": Color("86a85a")}
	mz.albedo_color = kol.get(b.get("teren", "pole"), Color("8fae58"))
	ziemia.material_override = mz
	scena3d.add_child(ziemia)
	var r := RandomNumberGenerator.new()
	r.seed = 77
	var dekor := {"las": "dab", "gory": "gora", "wzgorze": "cyprys", "pole": "krzak", "rzeka": "trzcina"}
	var m: String = dekor.get(b.get("teren", "pole"), "krzak")
	for i in 40:
		var n: Node3D = g.instancja(m if i % 3 else "pinia")
		n.position = Vector3(r.randf_range(-40, 40), 0, r.randf_range(-30, -9))
		n.scale = Vector3.ONE * (2.0 if m == "gora" else 1.0) * r.randf_range(0.8, 1.3)
		scena3d.add_child(n)
	if b.get("teren", "") == "rzeka":
		var w := MeshInstance3D.new()
		var wp := PlaneMesh.new()
		wp.size = Vector2(120, 5)
		w.mesh = wp
		w.position = Vector3(0, 0.02, -7)
		var wm := StandardMaterial3D.new()
		wm.albedo_color = Color(0.25, 0.5, 0.75)
		w.material_override = wm
		scena3d.add_child(w)
	_ustaw_szyki()
	stara_kamera = g.kamera.global_transform
	g.kamera.global_position = g.POLE_BITWY + Vector3(0, 5.5, 15)
	g.kamera.look_at(g.POLE_BITWY + Vector3(0, 2.3, 0))


func _ustaw_szyki() -> void:
	for n in moje_wezly + wrogie_wezly + walczacy:
		if is_instance_valid(n):
			n.queue_free()
	moje_wezly = []
	wrogie_wezly = []
	walczacy = []
	var moje := talia + reka + odrzut
	for i in mini(12, moje.size()):
		var n: Node3D = g.instancja(g.D.karty[moje[i]].model)
		n.position = Vector3(-4.5 - (i % 4) * 1.3, 0, -2.5 + (i / 4) * 1.5 + (i % 2) * 0.3)
		n.rotation.y = PI / 2
		g._cien_kontaktowy(n, 0.9 if g.D.karty[moje[i]].typ == "jazda" else 0.6, 0.5)
		scena3d.add_child(n)
		moje_wezly.append(n)
	var wrogie := wtalia + wodrzut + ([karta_wroga] if karta_wroga != "" else [])
	for i in mini(12, wrogie.size()):
		var n: Node3D = g.instancja(g.D.karty[wrogie[i]].model)
		n.position = Vector3(4.5 + (i % 4) * 1.3, 0, -2.5 + (i / 4) * 1.5 + (i % 2) * 0.3)
		n.rotation.y = -PI / 2
		g._cien_kontaktowy(n, 0.9 if g.D.karty[wrogie[i]].typ == "jazda" else 0.6, 0.5)
		scena3d.add_child(n)
		wrogie_wezly.append(n)
	# sztandary
	var s: Node3D = g.instancja("sztandar")
	s.position = Vector3(-8.5, 0, 0.5)
	scena3d.add_child(s)
	walczacy.append(s)


func _strzelec(karta: String) -> String:
	## Rodzaj strzelca, który zostaje na miejscu: „balista”, „luk” (łucznicy, konni łucznicy) albo „”.
	var c: Dictionary = g.D.karty[karta]
	if c.model == "balista":
		return "balista"
	if c.typ == "strzelcy" and c.model in ["lucznik", "hun"]:
		return "luk"
	return ""


func _animuj_starcie(moja: String, wroga: String, w: Dictionary) -> void:
	## Starcie w 3D: piechota i jazda biegną do siebie; balista i łucznicy zostają na miejscu i strzelają.
	var a: Node3D = g.instancja(g.D.karty[moja].model)
	a.position = Vector3(-3.5, 0, 1.5)
	a.rotation.y = PI / 2
	a.scale = Vector3.ONE * 1.3
	scena3d.add_child(a)
	var z: Node3D = g.instancja(g.D.karty[wroga].model)
	z.position = Vector3(3.5, 0, 1.5)
	z.rotation.y = -PI / 2
	z.scale = Vector3.ONE * 1.3
	scena3d.add_child(z)
	walczacy.append_array([a, z])
	var sa := _strzelec(moja)
	var sz := _strzelec(wroga)
	# miejsca, w których dojdzie do starcia
	var cel_a := -0.7
	var cel_z := 0.7
	if sa != "" and sz != "":
		cel_a = -3.8
		cel_z = 3.8
	elif sa != "":
		cel_a = -3.8
		cel_z = -1.6
	elif sz != "":
		cel_a = 1.6
		cel_z = 3.8
	var T := 0.7 if sa == "" and sz == "" else 1.0       # chwila trafienia / zwarcia
	var tw := create_tween().set_parallel(true)
	for para in [[a, cel_a, sa], [z, cel_z, sz]]:
		var u: Node3D = para[0]
		u.set_meta("start", t)
		if para[2] == "":
			u.set_meta("stan", "idzie")
			tw.tween_property(u, "position:x", para[1], T - 0.1).set_trans(Tween.TRANS_QUAD)
		else:
			u.position.x = para[1]
			u.set_meta("stan", "atak")
			u.set_meta("strzelec", para[2])
			if para[2] == "balista":
				u.set_meta("start", t + T - 0.47)    # bełt doleci dokładnie w chwili trafienia
			else:
				u.set_meta("start", t + T - 0.98)    # strzała zwolniona 0.38 s przed trafieniem
	# pociski: bełt albo strzała w przeciwnika + salwa łuczników z szeregu
	for para in [[a, z, sa, cel_z, 1.0], [z, a, sz, cel_a, -1.0]]:
		var strz: Node3D = para[0]
		var rodzaj: String = para[2]
		if rodzaj == "":
			continue
		var cel_x: float = para[3]
		var kier: float = para[4]
		var tp := create_tween()
		if rodzaj == "balista":
			tp.tween_interval(T - 0.45)
			tp.tween_callback(func():
				if is_instance_valid(strz) and is_instance_valid(scena3d):
					g.dzwiek("miecz")
					g.lot_belta(scena3d, strz.global_position + Vector3(0.9 * kier, 1.25, 0), scena3d.global_position + Vector3(cel_x, 1.1, 1.5), 0.45))
		else:
			tp.tween_interval(T - 0.4)
			tp.tween_callback(func():
				if not is_instance_valid(strz) or not is_instance_valid(scena3d):
					return
				g.dzwiek("klik")
				var skad: Vector3 = strz.get_meta("grot", strz.global_position + Vector3(0.5 * kier, 1.5, 0))
				g.lot_strzaly(scena3d, skad, scena3d.global_position + Vector3(cel_x, 1.0, 1.5), 0.4)
				# salwa z szeregu: strzały spadają wokół celu i wbijają się w ziemię
				var szereg: Array = moje_wezly if kier > 0 else wrogie_wezly
				var r := RandomNumberGenerator.new()
				for k in 5:
					var zrodlo: Vector3 = scena3d.global_position + Vector3(-5.0 * kier, 1.6, r.randf_range(-2.0, 1.5))
					if not szereg.is_empty():
						var u = szereg[r.randi_range(0, szereg.size() - 1)]
						if is_instance_valid(u):
							zrodlo = u.global_position + Vector3(0, 1.6, 0)
					var dokad := scena3d.global_position + Vector3(cel_x + r.randf_range(-1.0, 1.0), 0.0, 1.5 + r.randf_range(-1.2, 1.2))
					var s: Node3D = g.lot_strzaly(scena3d, zrodlo, dokad, r.randf_range(0.45, 0.6), true)
					walczacy.append(s))
	var tw2 := create_tween()
	tw2.tween_interval(T)
	tw2.tween_callback(func():
		for u in [a, z]:
			if is_instance_valid(u) and not u.has_meta("strzelec"):
				u.set_meta("stan", "atak")
				u.set_meta("start", t)
		g.dzwiek("tarcza")
		var przegrany: Node3D = z if w.P > w.E else (a if w.E > w.P else null)
		if przegrany:
			var t3 := create_tween()
			t3.tween_property(przegrany, "rotation:z", (PI / 2.2) * (1 if przegrany == z else -1), 0.4)
		var miejsce := (cel_a + cel_z) / 2.0
		if sa != "" and sz == "":
			miejsce = cel_z
		elif sz != "" and sa == "":
			miejsce = cel_a
		_pyl_bitwy(Vector3(miejsce, 0.5, 1.5)))


func _pyl_bitwy(poz: Vector3) -> void:
	var cz := CPUParticles3D.new()
	cz.one_shot = true
	cz.amount = 30
	cz.lifetime = 0.8
	cz.explosiveness = 0.95
	cz.spread = 80
	cz.initial_velocity_min = 2
	cz.initial_velocity_max = 4
	var sm := SphereMesh.new()
	sm.radius = 0.1
	sm.height = 0.2
	cz.mesh = sm
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(0.85, 0.75, 0.55)
	cz.material_override = m
	cz.position = poz
	scena3d.add_child(cz)
	cz.emitting = true


func _process(dt: float) -> void:
	if not aktywna:
		return
	t += dt
	for n in moje_wezly + wrogie_wezly:
		if is_instance_valid(n):
			g.animuj_postac(n, "stoi", t)
	for n in walczacy:
		if is_instance_valid(n) and n.has_meta("stan"):
			var st: String = n.get_meta("stan")
			var od: float = t - float(n.get_meta("start", t))
			if st == "atak":
				var dl := 0.55
				match String(n.get_meta("strzelec", "")):
					"balista": dl = 2.2
					"luk": dl = 1.2
				g.animuj_postac(n, "atak", 0.0, clampf(od / dl, 0.0, 1.0))
			else:
				g.animuj_postac(n, st, t * 9.0)
	if is_instance_valid(g.kamera):
		g.kamera.global_position = g.POLE_BITWY + Vector3(sin(t * 0.15) * 1.5, 5.5, 15)
		g.kamera.look_at(g.POLE_BITWY + Vector3(0, 2.3, 0))
		g.ustaw_glebie(15.0, 0.62, true)


# ----------------------------------------------------------------- interfejs bitwy
func _zbuduj_ui() -> void:
	if is_instance_valid(warstwa):
		warstwa.queue_free()
	warstwa = CanvasLayer.new()
	warstwa.layer = 1
	add_child(warstwa)
	korzen = Control.new()
	korzen.set_anchors_preset(Control.PRESET_FULL_RECT)
	korzen.mouse_filter = Control.MOUSE_FILTER_IGNORE
	korzen.theme = g.ui.motyw
	warstwa.add_child(korzen)
	var u = g.ui
	# góra: morale
	var gora := HBoxContainer.new()
	gora.set_anchors_preset(Control.PRESET_TOP_WIDE)
	gora.offset_left = 20
	gora.offset_right = -20
	gora.offset_top = 10
	gora.add_theme_constant_override("separation", 30)
	korzen.add_child(gora)
	var lewa := VBoxContainer.new()
	lewa.custom_minimum_size = Vector2(440, 0)
	gora.add_child(lewa)
	napis_p = u._label("", 20, u.C_JASNY)
	napis_p.add_theme_constant_override("outline_size", 8)
	napis_p.add_theme_color_override("font_outline_color", Color(0.1, 0.06, 0.04))
	lewa.add_child(napis_p)
	pasek_p = ProgressBar.new()
	pasek_p.custom_minimum_size = Vector2(0, 22)
	pasek_p.show_percentage = false
	pasek_p.add_theme_stylebox_override("fill", u._sb(Color("c0392b"), Color("c0392b"), 0, 3, 0))
	lewa.add_child(pasek_p)
	var tyt: Label = u._label("%s · %s" % [b.nazwa, b.rok], 24, u.C_ZLOTY)
	tyt.add_theme_constant_override("outline_size", 10)
	tyt.add_theme_color_override("font_outline_color", Color(0.1, 0.06, 0.04))
	tyt.set_anchors_preset(Control.PRESET_TOP_WIDE)
	tyt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	tyt.offset_top = 54
	korzen.add_child(tyt)
	var odstep := Control.new()
	odstep.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	gora.add_child(odstep)
	var prawy := VBoxContainer.new()
	prawy.custom_minimum_size = Vector2(440, 0)
	gora.add_child(prawy)
	napis_e = u._label("", 20, u.C_JASNY)
	napis_e.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	napis_e.add_theme_constant_override("outline_size", 8)
	napis_e.add_theme_color_override("font_outline_color", Color(0.1, 0.06, 0.04))
	prawy.add_child(napis_e)
	pasek_e = ProgressBar.new()
	pasek_e.custom_minimum_size = Vector2(0, 22)
	pasek_e.show_percentage = false
	pasek_e.fill_mode = ProgressBar.FILL_END_TO_BEGIN
	pasek_e.add_theme_stylebox_override("fill", u._sb(Color(g.D.frakcje[b.frakcja].kolor), Color("222"), 0, 3, 0))
	prawy.add_child(pasek_e)
	# środek: komunikaty / przyciski
	srodek = VBoxContainer.new()
	srodek.position = Vector2(290, 92)
	srodek.custom_minimum_size = Vector2(700, 0)
	srodek.alignment = BoxContainer.ALIGNMENT_BEGIN
	korzen.add_child(srodek)
	# dół: karty w ręce
	dol = HBoxContainer.new()
	dol.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	dol.offset_top = -250
	dol.offset_bottom = -10
	dol.alignment = BoxContainer.ALIGNMENT_CENTER
	dol.add_theme_constant_override("separation", 12)
	korzen.add_child(dol)


func _karta_ui(id: String, wroga: bool, zakryta := false, i := -1) -> Control:
	var u = g.ui
	var c: Dictionary = g.D.karty[id] if id != "" else {}
	var pc := PanelContainer.new()
	var kol := Color("f1e2b8") if not wroga else Color("e6cfc8")
	pc.add_theme_stylebox_override("panel", u._sb(kol, Color("5a3a22") if not wroga else Color(g.D.frakcje[b.frakcja].kolor), 3, 8, 6))
	pc.custom_minimum_size = Vector2(150, 220) if not wroga else Vector2(140, 180)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 2)
	pc.add_child(vb)
	if zakryta:
		var l: Label = u._label("?", 80, Color("5a3a22"))
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.custom_minimum_size = Vector2(0, 150)
		l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		vb.add_child(l)
		vb.add_child(u._label("karta zakryta", 13))
		return pc
	var tex_s := "res://ui/karta_%s.png" % c.model
	if ResourceLoader.exists(tex_s):
		var tr := TextureRect.new()
		tr.texture = load(tex_s)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.custom_minimum_size = Vector2(130, 110)
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		vb.add_child(tr)
	var n: Label = u._label(c.nazwa, 14)
	n.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	n.custom_minimum_size = Vector2(136, 0)
	n.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(n)
	var typ: Dictionary = g.D.typy_kart[c.typ]
	var s := sila(id, true) if not wroga else int(round(g.sila_karty(-1, id) * float(g.D.trudnosci[int(g.S.get("trudnosc", 1))].wrog)))
	var info: Label = u._label("%s · siła %d%s" % [typ.nazwa, s, (" · tarcza %d" % int(c.tarcza)) if c.has("tarcza") else ""], 15, u.C_CZERW)
	info.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(info)
	if not wroga and karta_wroga != "" and faza == "wybor":
		var w := rozstrzygnij(id, karta_wroga)
		var pr := ""
		if bije(id, karta_wroga):
			pr = "» przewaga +3!"
		elif bije(karta_wroga, id):
			pr = "« wróg ma przewagę"
		if pr != "":
			var l: Label = u._label(pr, 13, u.C_ZIELONY if bije(id, karta_wroga) else u.C_CZERW)
			l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			vb.add_child(l)
	if i >= 0:
		pc.mouse_filter = Control.MOUSE_FILTER_STOP
		pc.gui_input.connect(func(e):
			if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
				zagraj(i))
		pc.mouse_entered.connect(func(): pc.modulate = Color(1.1, 1.1, 0.9))
		pc.mouse_exited.connect(func(): pc.modulate = Color.WHITE)
		pc.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	return pc


func _odswiez_ui() -> void:
	if not aktywna or not is_instance_valid(korzen):
		return
	var u = g.ui
	napis_p.text = "Rzym (%s) – morale %d/%d" % [g.D.dowodcy[b.dowodca], maxi(p_hp, 0), p_max]
	napis_e.text = "%s – morale %d/%d" % [g.D.frakcje[b.frakcja].nazwa, maxi(e_hp, 0), e_max]
	pasek_p.max_value = p_max
	pasek_p.value = maxi(p_hp, 0)
	pasek_e.max_value = e_max
	pasek_e.value = maxi(e_hp, 0)
	for c in srodek.get_children():
		c.queue_free()
	for c in dol.get_children():
		c.queue_free()
	var panel := PanelContainer.new()
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	panel.add_child(vb)
	srodek.add_child(panel)
	match faza:
		"intro":
			var op: Label = u._label(b.opis, 18)
			op.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			op.custom_minimum_size = Vector2(560, 0)
			vb.add_child(op)
			g.lektor(b.opis)
			var dw := "Dowódca: %s. Premia: " % g.D.dowodcy[b.dowodca]
			var pr := []
			for k in b.get("premia", {}):
				pr.append("%s +%d" % [g.D.typy_kart[k].nazwa.to_lower(), int(b.premia[k])])
			vb.add_child(u._label(dw + ", ".join(pr), 15, u.C_ZIELONY))
			vb.add_child(u._label("Zasada: piechota » jazda » strzelcy » piechota (+3 za przewagę)", 15, u.C_SZARY))
			var hb := HBoxContainer.new()
			hb.alignment = BoxContainer.ALIGNMENT_CENTER
			hb.add_child(u._btn("Pytanie rady wojennej »", func():
				faza = "pytanie"
				var hints: int = int(g.D.trudnosci[int(g.S.get("trudnosc", 1))].podpowiedzi) + (1 if g.ma_tech(p, "pismo") else 0)
				g.ui.pytanie_rady(func(ok): po_pytaniu(ok), hints), "", 20))
			vb.add_child(hb)
		"pytanie":
			vb.add_child(u._label("Rada wojenna obraduje…", 18))
		"wybor", "starcie":
			var hb := HBoxContainer.new()
			hb.add_theme_constant_override("separation", 14)
			vb.add_child(hb)
			var opis := VBoxContainer.new()
			hb.add_child(opis)
			opis.add_child(u._label("Runda %d · wróg wystawia:" % runda, 17, u.C_CZERW))
			if faza == "wybor":
				opis.add_child(u._label("Wybierz kartę z ręki (na dole).", 15))
			for l in log.slice(maxi(0, log.size() - 3)):
				var ll: Label = u._label(l, 14, u.C_SZARY)
				ll.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
				ll.custom_minimum_size = Vector2(300, 0)
				opis.add_child(ll)
			if faza == "wybor":
				hb.add_child(_karta_ui(karta_wroga, true))
				if ukryta != "":
					hb.add_child(_karta_ui(ukryta, true, true))
			else:
				hb.add_child(_karta_ui(ostatnie.wroga, true))
			# taktyki
			if faza == "wybor":
				var tb := HBoxContainer.new()
				tb.add_theme_constant_override("separation", 6)
				vb.add_child(tb)
				tb.add_child(u._label("Taktyki (raz w bitwie):", 14))
				for id in taktyki:
					var bt: Button = u._btn(g.D.taktyki[id].nazwa, func(): uzyj_taktyki(id), "", 14)
					bt.tooltip_text = g.D.taktyki[id].opis
					bt.disabled = id in uzyte
					tb.add_child(bt)
				for i in reka.size():
					dol.add_child(_karta_ui(reka[i], false, false, i))
		"koniec":
			var tt: Label = u._label("ZWYCIĘSTWO!" if wygrana else "Porażka…", 34, u.C_ZIELONY if wygrana else u.C_CZERW)
			tt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			vb.add_child(tt)
			var po: Label = u._label(b.po if wygrana else "Wojsko musi odpocząć. Wzmocnij armię (koszary, technologie) i spróbuj w następnej turze.", 17)
			po.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			po.custom_minimum_size = Vector2(560, 0)
			vb.add_child(po)
			if wygrana:
				g.lektor(b.po)
			var hb := HBoxContainer.new()
			hb.alignment = BoxContainer.ALIGNMENT_CENTER
			hb.add_child(u._btn("Dalej »", _zakoncz_z_wynikiem, "", 20))
			vb.add_child(hb)
