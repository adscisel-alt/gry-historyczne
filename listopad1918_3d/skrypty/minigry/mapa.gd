extends "res://skrypty/minigry/baza.gd"
## Rozdział 1: przypisz miasta do trzech zaborów.

const MAPA := Rect2(40, 130, 760, 520)
var miasta: Array = []
var umieszczone: Array = []
var wybrane := ""
var bledy := 0
var wielokaty: Dictionary = {}
var rys: Control
var przyciski: Dictionary = {}
var bledy_l: Label


func _init(p_main) -> void:
	super(p_main)
	gid = "mapa_zaborow"
	tytul = "Mapa trzech zaborów"
	instrukcja = "Ktoś zerwał nazwy miast. Kliknij miasto na liście, a potem zabór na mapie, w którym leżało w 1914 r. Rosja na wschodzie, Prusy na zachodzie i północy, Austria na południu."
	miasta = Dane.miasta.keys()
	var rng := RandomNumberGenerator.new()
	rng.seed = 31
	for i in miasta.size():
		var j := rng.randi_range(0, miasta.size() - 1)
		var t = miasta[i]
		miasta[i] = miasta[j]
		miasta[j] = t
	var sx := MAPA.size.x / (27.4 - 13.8)
	var sy := MAPA.size.y / (55.6 - 48.1)
	for k in Dane.zabory:
		var pts := PackedVector2Array()
		for p in Dane.zabory[k]["punkty"]:
			pts.append(rzut(p[0], p[1], sx, sy))
		wielokaty[k] = pts


func rzut(lon: float, lat: float, sx: float, sy: float) -> Vector2:
	return Vector2(MAPA.position.x + (lon - 13.8) * sx, MAPA.position.y + (55.6 - lat) * sy)


func buduj() -> void:
	rys = Control.new()
	rys.mouse_filter = Control.MOUSE_FILTER_STOP
	dodaj(rys, MAPA, gra)
	rys.draw.connect(_rysuj)
	rys.gui_input.connect(_klik_mapy)
	for i in miasta.size():
		var m: String = miasta[i]
		var b := Motyw.przycisk(m, 20, func(): wybierz(m))
		dodaj(b, Rect2(840, 132 + i * 54, 240, 46), gra)
		przyciski[m] = b
	bledy_l = Motyw.etykieta("Błędy: 0", 18, "szeryf", Motyw.ATRAMENT_JASNY, false)
	dodaj(bledy_l, Rect2(1100, 140, 150, 30), gra)


func wybierz(m: String) -> void:
	if m in umieszczone:
		return
	wybrane = m
	for k in przyciski:
		przyciski[k].modulate = Color(1, 1, 1) if k != m else Color(0.85, 0.7, 1.0)


func zabor_w_punkcie(p: Vector2) -> String:
	for k in wielokaty:
		if Geometry2D.is_point_in_polygon(p, wielokaty[k]):
			return k
	return ""


func umiesc(miasto: String, zabor: String) -> bool:
	if miasto in umieszczone:
		return true
	var poprawny: String = Dane.miasta[miasto][1]
	if zabor == poprawny:
		umieszczone.append(miasto)
		wybrane = ""
		przyciski[miasto].disabled = true
		przyciski[miasto].text = "✔ " + miasto
		przyciski[miasto].modulate = Color(1, 1, 1)
		info("Dobrze! %s leżał w zaborze %s." % [miasto, str(Dane.zabory[zabor]["nazwa"]).split(" ")[1]])
		rys.queue_redraw()
		if umieszczone.size() == miasta.size():
			wygraj()
		return true
	bledy += 1
	bledy_l.text = "Błędy: %d" % bledy
	var podp := {"rosyjski": "Pomyśl o carskiej Rosji…", "pruski": "Pomyśl o królestwie Prus…", "austriacki": "Pomyśl o cesarstwie Austrii…"}
	info("Nie tym razem. %s — %s" % [miasto, podp[poprawny]], false)
	return false


func _klik_mapy(e: InputEvent) -> void:
	if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT and wybrane != "":
		var z := zabor_w_punkcie(e.position + MAPA.position)
		if z != "":
			umiesc(wybrane, z)


func _process(delta: float) -> void:
	super(delta)
	if rys:
		rys.queue_redraw()


func _rysuj() -> void:
	var o := -MAPA.position
	rys.draw_rect(Rect2(Vector2.ZERO, MAPA.size), Color(0.86, 0.81, 0.7))
	var mysz := rys.get_local_mouse_position() + MAPA.position
	var pod := zabor_w_punkcie(mysz) if wybrane != "" else ""
	for k in wielokaty:
		var pts := PackedVector2Array()
		for p in wielokaty[k]:
			pts.append(p + o)
		var t := float(Dane.zabory[k]["ton"]) / 255.0
		rys.draw_colored_polygon(pts, Color(t, t * 0.93, t * 0.8))
		var zamk := pts.duplicate()
		zamk.append(pts[0])
		rys.draw_polyline(zamk, Motyw.FIOLET if k == pod else Color(0.15, 0.1, 0.06), 4.0 if k == pod else 2.0)
	var f := Motyw.czcionka("plakat")
	var etyk := {"rosyjski": Vector2(23.6, 53.0), "pruski": Vector2(16.2, 53.6), "austriacki": Vector2(22.6, 49.55)}
	var sx := MAPA.size.x / (27.4 - 13.8)
	var sy := MAPA.size.y / (55.6 - 48.1)
	for k in etyk:
		var p := rzut(etyk[k].x, etyk[k].y, sx, sy) + o
		var n := str(Dane.zabory[k]["nazwa"]).to_upper()
		var w := f.get_string_size(n, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		rys.draw_string(f, p - Vector2(w / 2, 0), n, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0.12, 0.08, 0.05))
	for m in umieszczone:
		var ll: Array = Dane.miasta[m][0]
		var p := rzut(ll[0], ll[1], sx, sy) + o
		rys.draw_circle(p, 6, Color(0.1, 0.07, 0.04))
		rys.draw_string(Motyw.czcionka(), p + Vector2(9, -6), m, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0.1, 0.07, 0.04))
	rys.draw_rect(Rect2(Vector2.ZERO, MAPA.size), Color(0.15, 0.1, 0.06), false, 3.0)
