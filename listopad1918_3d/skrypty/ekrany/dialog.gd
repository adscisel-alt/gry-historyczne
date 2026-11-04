extends "res://skrypty/ekrany/ekran.gd"
## Drzewko dialogowe: portret, imię, tekst pisany „maszyną”, opcje 1–4.

const Rozmowa = preload("res://skrypty/rozmowa.gd")
const LOGIKA = preload("res://skrypty/logika.gd")

var rozmowa = null
var zebrane: Array = []
var portret: TextureRect
var imie: Label
var lata: Label
var tekst: Label
var opcje_box: VBoxContainer
var wskazowka: Label
var t_tekst := 0.0
var _ostatnie_znaki := 0


func _init(p_main, did: String) -> void:
	super(p_main)
	typ = "dialog"
	rozmowa = Rozmowa.new(main.logika, did)


func _ready() -> void:
	add_child(Motyw.przyciemnienie(0.45))
	var cien := ColorRect.new()
	cien.color = Color(0.06, 0.04, 0.02, 0.9)
	dodaj(cien, Rect2(30, 372, 1232, 340))
	var panel := Panel.new()
	panel.add_theme_stylebox_override("panel", Motyw.styl_papieru())
	dodaj(panel, Rect2(24, 364, 1228, 336))
	portret = Motyw.obraz(null, Rect2())
	dodaj(portret, Rect2(26, 22, 180, 216), panel)
	imie = Motyw.etykieta("", 17, "plakat", Motyw.ATRAMENT, false, HORIZONTAL_ALIGNMENT_CENTER)
	dodaj(imie, Rect2(0, 248, 232, 26), panel)
	lata = Motyw.etykieta("", 15, "szeryf", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER)
	dodaj(lata, Rect2(0, 276, 232, 24), panel)
	tekst = Motyw.etykieta("", 21)
	dodaj(tekst, Rect2(240, 22, 960, 170), panel)
	opcje_box = VBoxContainer.new()
	opcje_box.add_theme_constant_override("separation", 4)
	dodaj(opcje_box, Rect2(232, 190, 980, 140), panel)
	wskazowka = Motyw.etykieta("▸ kliknij lub naciśnij spację", 16, "reka", Motyw.ATRAMENT_JASNY, false)
	dodaj(wskazowka, Rect2(960, 300, 260, 26), panel)
	_nowy_wezel()


func _nowy_wezel() -> void:
	t_tekst = 0.0
	zebrane.append_array(rozmowa.odbierz_zdarzenia())
	var reszta: Array = []
	for z in zebrane:
		if z[0] == LOGIKA.FAKT or z[0] == LOGIKA.PRZEDMIOT:
			main.toast(z[0], z[1])
		else:
			reszta.append(z)
	zebrane = reszta
	if rozmowa.zakonczona():
		main.zdejmij(self)
		main.na_poczatek(zebrane)
		return
	var w: Dictionary = rozmowa.wezel()
	var kto := str(w.get("kto", "janek"))
	portret.texture = Dane.tex_portret(kto)
	imie.text = Dane.imie(kto)
	lata.text = str(Dane.postacie[kto].get("lata", "")) if kto in Dane.historyczne else ""
	tekst.text = str(w["tekst"])
	tekst.visible_characters = 0
	for c in opcje_box.get_children():
		c.queue_free()
	opcje_box.visible = false
	wskazowka.visible = false
	var opcje: Array = rozmowa.opcje()
	for i in opcje.size():
		var b := Button.new()
		b.text = "%d. %s" % [i + 1, opcje[i]["tekst"]]
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.flat = true
		b.add_theme_font_override("font", Motyw.czcionka("szeryf"))
		b.add_theme_font_size_override("font_size", 19)
		b.add_theme_color_override("font_color", Color(0.3, 0.22, 0.15))
		b.add_theme_color_override("font_hover_color", Motyw.ATRAMENT)
		b.add_theme_stylebox_override("hover", Motyw.styl_plaski(Color(0.83, 0.77, 0.64), Color(0, 0, 0, 0), 0, 4))
		b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		var nr: int = i
		b.pressed.connect(func(): wybierz(nr))
		opcje_box.add_child(b)


func pelny_tekst() -> bool:
	return t_tekst * 90.0 >= tekst.text.length()


func wybierz(i: int) -> void:
	if not pelny_tekst() or rozmowa.zakonczona():
		return
	main.dzwiek("klik")
	rozmowa.wybierz(i)
	_nowy_wezel()


func dalej() -> void:
	if not rozmowa.opcje().is_empty():
		return
	rozmowa.dalej()
	_nowy_wezel()


func _process(delta: float) -> void:
	super(delta)
	if rozmowa.zakonczona():
		return
	t_tekst += delta
	var n := int(t_tekst * 90.0)
	if pelny_tekst():
		tekst.visible_characters = -1
		opcje_box.visible = true
		wskazowka.visible = rozmowa.opcje().is_empty()
	else:
		tekst.visible_characters = n
		if n / 6 != _ostatnie_znaki / 6:
			main.dzwiek("maszyna")
		_ostatnie_znaki = n


func klik_tla() -> void:
	if not pelny_tekst():
		t_tekst = 999.0
	elif rozmowa.opcje().is_empty():
		dalej()


func klawisz(k: int) -> void:
	if k >= KEY_1 and k <= KEY_9:
		var i := k - KEY_1
		if pelny_tekst() and i < rozmowa.opcje().size():
			wybierz(i)
	elif k in [KEY_SPACE, KEY_ENTER]:
		klik_tla()
