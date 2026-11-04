extends "res://skrypty/ekrany/ekran.gd"
## Dziennik Janka: fakty ze źródłami, mity, biogramy, mapa zaborów, prawa kobiet.

const ZAKLADKI := ["Fakty", "Mity", "Postacie", "Mapa zaborów", "Prawa kobiet"]

var zakladka := 0
var przewijanie: ScrollContainer
var tresc: VBoxContainer
var przyciski_zakl: Array = []


func _init(p_main) -> void:
	super(p_main)
	typ = "dziennik"


func _ready() -> void:
	add_child(Motyw.przyciemnienie(0.75))
	var ramka := ColorRect.new()
	ramka.color = Color(0.25, 0.17, 0.1)
	dodaj(ramka, Rect2(50, 70, 1180, 630))
	var kartka := Panel.new()
	kartka.add_theme_stylebox_override("panel", Motyw.styl_papieru())
	dodaj(kartka, Rect2(60, 80, 1160, 610))
	dodaj(Motyw.etykieta("Dziennik Janka", 18, "reka", Color(0.93, 0.88, 0.78), false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 2, 1280, 30))
	for i in ZAKLADKI.size():
		var nr := i
		var b := Motyw.przycisk(ZAKLADKI[i], 18, func(): pokaz(nr))
		dodaj(b, Rect2(90 + i * 190, 30, 180, 44))
		przyciski_zakl.append(b)
	dodaj(Motyw.przycisk("Zamknij", 18, func(): zamknij()), Rect2(1080, 30, 120, 44))
	przewijanie = ScrollContainer.new()
	przewijanie.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	dodaj(przewijanie, Rect2(80, 96, 1120, 580))
	tresc = VBoxContainer.new()
	tresc.custom_minimum_size = Vector2(1090, 0)
	tresc.add_theme_constant_override("separation", 14)
	przewijanie.add_child(tresc)
	pokaz(0)


func pokaz(i: int) -> void:
	zakladka = i
	for k in przyciski_zakl.size():
		przyciski_zakl[k].modulate = Color(1, 1, 1) if k == i else Color(0.8, 0.76, 0.7)
	for c in tresc.get_children():
		c.queue_free()
	if i == 0:
		_fakty()
	elif i == 1:
		_mity()
	elif i == 2:
		_postacie()
	elif i == 3:
		_mapa()
	else:
		_kobiety()
	przewijanie.scroll_vertical = 0


func _dodaj(c: Control) -> void:
	tresc.add_child(c)


func _wpis(naglowek: String, tekst: String, przypis: String = "") -> void:
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 2)
	v.add_child(Motyw.etykieta(naglowek, 18, "plakat"))
	v.add_child(Motyw.etykieta(tekst, 17))
	if przypis != "":
		v.add_child(Motyw.etykieta(przypis, 14, "szeryf", Motyw.ATRAMENT_JASNY))
	_dodaj(v)


func _fakty() -> void:
	var l = main.logika
	if l.fakty.is_empty():
		_dodaj(Motyw.etykieta("Jeszcze pusto. Klikaj, oglądaj i rozmawiaj — fakty same tu trafią.", 19, "szeryf", Motyw.ATRAMENT_JASNY))
	for fid in l.fakty:
		var f: Dictionary = Dane.fakty[fid]
		_wpis(str(f["data"]), str(f["tekst"]), "Źródło: " + str(f["zrodlo"]))


func _mity() -> void:
	var l = main.logika
	for mid in Dane.mity:
		var m: Dictionary = Dane.mity[mid]
		if l.mity.has(mid):
			var ok: bool = l.mity[mid] == true
			_wpis("MIT: " + str(m["mit"]), ("✔ " if ok else "") + "PRAWDA: " + str(m["opcje"][int(m["dobra"])]), str(m["wyjasnienie"]))
		else:
			_dodaj(Motyw.etykieta("??? — mit jeszcze nie sprawdzony", 17, "reka", Motyw.ATRAMENT_JASNY))


func _postacie() -> void:
	var l = main.logika
	for pid in Dane.historyczne:
		var p: Dictionary = Dane.postacie[pid]
		if pid in l.poznani:
			var h := HBoxContainer.new()
			h.add_theme_constant_override("separation", 16)
			var por := TextureRect.new()
			por.texture = Dane.tex_portret(pid)
			por.custom_minimum_size = Vector2(110, 132)
			por.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			por.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			h.add_child(por)
			var v := VBoxContainer.new()
			v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			v.add_child(Motyw.etykieta("%s (%s)" % [p["imie"], p["lata"]], 19, "plakat"))
			v.add_child(Motyw.etykieta(str(p["rola"]), 15, "reka", Motyw.ATRAMENT_JASNY))
			v.add_child(Motyw.etykieta(str(p["biogram"]), 16))
			v.add_child(Motyw.etykieta("Wkład: " + str(p["wklad"]), 15, "plakat", Motyw.FIOLET))
			h.add_child(v)
			_dodaj(h)
		else:
			_dodaj(Motyw.etykieta("??? — postać jeszcze niepoznana", 17, "reka", Motyw.ATRAMENT_JASNY))


func _mapa() -> void:
	var t := TextureRect.new()
	t.texture = Dane.tex_ui("mapa")
	t.custom_minimum_size = Vector2(1060, 520)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_dodaj(t)
	_dodaj(Motyw.etykieta("Ziemie polskie pod zaborami (uproszczenie, granice z 1914 r.). Rosja — wschód, Prusy — zachód i północ, Austria — południe.", 16, "reka", Motyw.ATRAMENT_JASNY, true, HORIZONTAL_ALIGNMENT_CENTER))


func _kobiety() -> void:
	var pk: Dictionary = Dane.prawa_kobiet
	_dodaj(Motyw.etykieta(str(pk["tytul"]), 24, "plakat"))
	for a in pk["akapity"]:
		_dodaj(Motyw.etykieta(str(a), 17))
	_dodaj(Motyw.etykieta("Od kiedy kobiety głosują?", 19, "plakat"))
	for wpis in pk["porownanie"]:
		var h := HBoxContainer.new()
		var kraj := Motyw.etykieta(str(wpis[0]), 16, "szeryf", Motyw.ATRAMENT, false)
		kraj.custom_minimum_size = Vector2(330, 24)
		h.add_child(kraj)
		var pasek := ColorRect.new()
		pasek.color = Motyw.FIOLET if str(wpis[0]) == "Polska" else Color(0.35, 0.27, 0.2)
		pasek.custom_minimum_size = Vector2((int(wpis[1]) - 1880) * 6, 22)
		h.add_child(pasek)
		h.add_child(Motyw.etykieta("  " + str(int(wpis[1])), 16, "plakat", Motyw.ATRAMENT, false))
		_dodaj(h)
	_dodaj(Motyw.etykieta("Źródło: " + str(pk["zrodlo"]), 14, "szeryf", Motyw.ATRAMENT_JASNY))


func klawisz(k: int) -> void:
	if k in [KEY_ESCAPE, KEY_J]:
		zamknij()
	elif k == KEY_TAB:
		pokaz((zakladka + 1) % ZAKLADKI.size())
