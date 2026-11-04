extends Node3D
## Lokacja 3D: diorama + papierowe postacie + hotspoty + Janek („kliknij i idź”).

const Budowniczy = preload("res://skrypty/budowniczy.gd")

const WARSTWA_PODLOGI := 1
const WARSTWA_HOTSPOTOW := 2
const PREDKOSC := 3.2
const PIKSEL := 1.8 / 480.0   # dorosły (480 px wycinanki) ma 1,8 m

var main = null
var lid: String = ""
var b = null                     # Budowniczy
var kamera: Camera3D
var scena: Node3D
var wezly: Dictionary = {}       # hid -> Node3D (sprite/ikona/wyjście)
var ciala: Dictionary = {}       # hid -> StaticBody3D
var podswietlenia: Dictionary = {}
var janek: Sprite3D
var cel = null                   # Vector3 albo null
var oczekuje = null              # [hid, przedmiot]
var najechany: String = ""
var czas := 0.0


func buduj(p_main, p_lid: String) -> void:
	main = p_main
	lid = p_lid
	for d in get_children():
		d.queue_free()
	wezly.clear()
	ciala.clear()
	podswietlenia.clear()
	cel = null
	oczekuje = null
	najechany = ""
	scena = Node3D.new()
	scena.name = "Diorama"
	add_child(scena)
	b = Budowniczy.new(scena)
	b.call("lok_" + lid)
	_otoczenie()
	_podloga()
	_hotspoty()
	_janek()
	odswiez()


func _otoczenie() -> void:
	var o: Dictionary = b.otoczenie
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = o["tlo"]
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = o["ambient"]
	env.ambient_light_energy = o["ambient_moc"]
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.fog_enabled = true
	env.fog_light_color = Color(0.85, 0.78, 0.66)
	env.fog_density = o["mgla"]
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var slonce := DirectionalLight3D.new()
	slonce.rotation_degrees = o["slonce_kat"]
	slonce.light_energy = o["slonce_moc"]
	slonce.light_color = o["slonce_kolor"]
	slonce.shadow_enabled = true
	add_child(slonce)
	kamera = Camera3D.new()
	kamera.fov = b.kamera["fov"]
	kamera.current = true
	add_child(kamera)
	kamera.look_at_from_position(b.kamera["poz"], b.kamera["cel"], Vector3.UP)


func _podloga() -> void:
	var cialo := StaticBody3D.new()
	cialo.collision_layer = WARSTWA_PODLOGI
	cialo.collision_mask = 0
	var ksztalt := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(40, 0.2, 40)
	ksztalt.shape = box
	cialo.position = Vector3(0, -0.1, 0)
	cialo.add_child(ksztalt)
	add_child(cialo)


func _cialo(hid: String, poz: Vector3, rozmiar: Vector3) -> void:
	var cialo := StaticBody3D.new()
	cialo.collision_layer = WARSTWA_HOTSPOTOW
	cialo.collision_mask = 0
	cialo.set_meta("hid", hid)
	var ksztalt := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = rozmiar
	ksztalt.shape = box
	cialo.add_child(ksztalt)
	cialo.position = poz
	add_child(cialo)
	ciala[hid] = cialo


func sprite_postaci(pid: String, poz: Vector3) -> Sprite3D:
	var s := Sprite3D.new()
	s.texture = Dane.tex_postac(pid)
	var meta: Dictionary = Dane.grafika["postacie"][pid]
	s.pixel_size = PIKSEL
	s.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	s.shaded = false
	s.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	s.position = poz + Vector3(0, (float(meta["h"]) / 2.0 - float(meta["stopa_px"])) * PIKSEL, 0)
	s.set_meta("baza_y", s.position.y)
	add_child(s)
	# drewniana podstawka teatrzyku papierowego
	var podst := MeshInstance3D.new()
	var m := BoxMesh.new()
	m.size = Vector3(0.62, 0.05, 0.26)
	podst.mesh = m
	podst.material_override = b.mat(Budowniczy.K(70))
	podst.position = Vector3(0, -s.position.y + poz.y + 0.025, 0)
	s.add_child(podst)
	return s


func _hotspoty() -> void:
	for h in Dane.lokacje[lid]["hotspoty"]:
		var hid: String = h["id"]
		if not b.miejsca.has(hid):
			push_error("Brak miejsca 3D dla hotspotu %s w %s" % [hid, lid])
			continue
		var m: Dictionary = b.miejsca[hid]
		var poz: Vector3 = m["poz"]
		match m["typ"]:
			"postac":
				var pid: String = h["postac"]
				var s := sprite_postaci(pid, poz)
				wezly[hid] = s
				var wys := float(Dane.grafika["postacie"][pid]["wzrost_px"]) * PIKSEL
				_cialo(hid, poz + Vector3(0, wys / 2, 0), Vector3(0.9, wys + 0.1, 0.5))
			"przedmiot":
				var ik := Sprite3D.new()
				ik.texture = Dane.tex_ikona(str(h.get("przedmiot", "gazeta")))
				ik.pixel_size = 0.0055
				ik.billboard = BaseMaterial3D.BILLBOARD_ENABLED
				ik.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
				ik.shaded = false
				ik.no_depth_test = false
				var r: Vector3 = m["rozmiar"]
				ik.position = poz + Vector3(0, r.y / 2 + 0.25, 0) if r.y > 1.0 else poz
				ik.set_meta("baza_y", ik.position.y)
				add_child(ik)
				wezly[hid] = ik
				_cialo(hid, poz, r)
			"wyjscie":
				var w := Sprite3D.new()
				w.texture = Dane.tex_ui("wyjscie")
				w.pixel_size = 0.0058
				w.billboard = BaseMaterial3D.BILLBOARD_ENABLED
				w.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
				w.shaded = false
				w.flip_h = poz.x < 0
				w.position = poz
				w.set_meta("baza_y", poz.y)
				add_child(w)
				wezly[hid] = w
				_cialo(hid, poz, m["rozmiar"])
			_:
				_cialo(hid, poz, m["rozmiar"])
				var pod := MeshInstance3D.new()
				var bm := BoxMesh.new()
				bm.size = m["rozmiar"] + Vector3(0.04, 0.04, 0.04)
				pod.mesh = bm
				var mt := StandardMaterial3D.new()
				mt.albedo_color = Color(1.0, 0.95, 0.8, 0.16)
				mt.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
				mt.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
				pod.material_override = mt
				pod.position = poz
				pod.visible = false
				pod.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				add_child(pod)
				podswietlenia[hid] = pod


func _janek() -> void:
	janek = sprite_postaci("janek", b.start_janka)
	janek.name = "Janek"


func odswiez() -> void:
	## Widoczność hotspotów zgodnie ze stanem gry.
	var widoczne := {}
	for h in main.logika.hotspoty():
		widoczne[h["id"]] = true
	for hid in ciala:
		var w := widoczne.has(hid)
		ciala[hid].collision_layer = WARSTWA_HOTSPOTOW if w else 0
		if wezly.has(hid):
			wezly[hid].visible = w


func widoczny(hid: String) -> bool:
	return ciala.has(hid) and ciala[hid].collision_layer != 0


func poz_janka() -> Vector3:
	return janek.position * Vector3(1, 0, 1)


# ------------------------------------------------------------------ wejście
func promien(poz_ekranu: Vector2, maska: int) -> Dictionary:
	var od := kamera.project_ray_origin(poz_ekranu)
	var do_ := od + kamera.project_ray_normal(poz_ekranu) * 80.0
	var q := PhysicsRayQueryParameters3D.create(od, do_, maska)
	return get_world_3d().direct_space_state.intersect_ray(q)


func hotspot_pod(poz_ekranu: Vector2) -> String:
	var r := promien(poz_ekranu, WARSTWA_HOTSPOTOW)
	if r.is_empty():
		return ""
	return str(r["collider"].get_meta("hid"))


func _ogranicz(p: Vector3) -> Vector3:
	var g: Rect2 = b.granice
	return Vector3(clampf(p.x, g.position.x, g.end.x), 0, clampf(p.z, g.position.y, g.end.y))


func klik(poz_ekranu: Vector2, przedmiot) -> void:
	var hid := hotspot_pod(poz_ekranu)
	if hid != "":
		var c: Vector3 = ciala[hid].position
		var cel_p := Vector3(c.x, 0, c.z + 0.9)
		if b.miejsca[hid]["typ"] == "postac":
			cel_p.x += -1.0 if c.x > janek.position.x else 1.0
			cel_p.z = c.z + 0.3
		cel = _ogranicz(cel_p)
		oczekuje = [hid, przedmiot]
		return
	var r := promien(poz_ekranu, WARSTWA_PODLOGI)
	if not r.is_empty():
		cel = _ogranicz(r["position"])
		oczekuje = null


func _process(delta: float) -> void:
	if janek == null:
		return
	czas += delta
	# oddech postaci, kołysanie ikon i wyjść
	for hid in wezly:
		var n: Node3D = wezly[hid]
		if n.has_meta("baza_y"):
			var typ: String = b.miejsca[hid]["typ"]
			if typ == "postac":
				n.scale = Vector3(1, 1.0 + sin(czas * 1.7 + n.position.x) * 0.008, 1)
			else:
				n.position.y = float(n.get_meta("baza_y")) + sin(czas * 2.5 + n.position.x) * 0.06
	if b.kolysanie:
		scena.rotation_degrees.z = sin(czas * 3.1) * 0.25
		scena.position.y = sin(czas * 7.3) * 0.006
	# chód Janka
	if cel != null:
		var p := poz_janka()
		var d: Vector3 = cel - p
		var krok := PREDKOSC * delta
		if d.length() <= krok:
			_ustaw_janka(cel)
			cel = null
			janek.rotation_degrees.z = 0
			if oczekuje != null:
				var o: Array = oczekuje
				oczekuje = null
				if widoczny(o[0]):
					main.aktywuj(o[0], o[1])
		else:
			if absf(d.x) > 0.01:
				janek.flip_h = d.x < 0
			_ustaw_janka(p + d.normalized() * krok)
			janek.rotation_degrees.z = sin(czas * 14.0) * 4.0
			janek.position.y = float(janek.get_meta("baza_y")) + absf(sin(czas * 14.0)) * 0.05
	# podświetlenie pod myszą
	if main.czy_swiat_aktywny():
		var mysz := get_viewport().get_mouse_position()
		var nowy := hotspot_pod(mysz) if mysz.y < 560 else ""
		if nowy != najechany:
			if podswietlenia.has(najechany):
				podswietlenia[najechany].visible = false
			if wezly.has(najechany) and wezly[najechany] is Sprite3D:
				wezly[najechany].modulate = Color.WHITE
			najechany = nowy
			if podswietlenia.has(najechany):
				podswietlenia[najechany].visible = true
			if wezly.has(najechany) and wezly[najechany] is Sprite3D:
				wezly[najechany].modulate = Color(1.15, 1.1, 1.0)


func _ustaw_janka(p: Vector3) -> void:
	janek.position = Vector3(p.x, float(janek.get_meta("baza_y")), p.z)


func zakonczony_ruch() -> bool:
	return cel == null
