extends Control
## Interfejs lokacji: podpis pocztówki, etykieta pod myszą, panel z komunikatem i torbą.

const Motyw = preload("res://skrypty/motyw.gd")

var main = null
var podpis: Label
var rozdzial_etykieta: PanelContainer
var kto: Label
var tresc: Label
var sloty: Array = []
var etykieta_myszy: PanelContainer
var etykieta_myszy_tekst: Label
var ikona_kursora: TextureRect
var komunikat_t := 0.0
var komunikat_pelny := ""


func _init(p_main) -> void:
	main = p_main
	set_anchors_preset(Control.PRESET_FULL_RECT)
	size = Vector2(1280, 720)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _ready() -> void:
	# podpis pocztówki
	var pp := PanelContainer.new()
	pp.add_theme_stylebox_override("panel", Motyw.styl_plaski(Color(0.93, 0.89, 0.8), Motyw.ATRAMENT_JASNY, 1, 3))
	pp.position = Vector2(36, 12)
	podpis = Motyw.etykieta("", 20, "reka", Motyw.ATRAMENT, false)
	pp.add_child(podpis)
	pp.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(pp)
	rozdzial_etykieta = Motyw.etykieta_fiolet("", 14)
	rozdzial_etykieta.position = Vector2(36, 54)
	rozdzial_etykieta.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(rozdzial_etykieta)
	# dolny panel
	var panel := Panel.new()
	panel.add_theme_stylebox_override("panel", Motyw.styl_papieru(true))
	panel.position = Vector2(0, 560)
	panel.size = Vector2(1280, 160)
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(panel)
	var linia := ColorRect.new()
	linia.color = Motyw.ATRAMENT
	linia.position = Vector2(0, 0)
	linia.size = Vector2(1280, 4)
	panel.add_child(linia)
	kto = Motyw.etykieta("Janek", 17, "plakat", Motyw.ATRAMENT_JASNY, false)
	kto.position = Vector2(24, 12)
	panel.add_child(kto)
	tresc = Motyw.etykieta("", 17)
	tresc.position = Vector2(24, 36)
	tresc.size = Vector2(370, 120)
	panel.add_child(tresc)
	for i in 10:
		var slot := Button.new()
		slot.position = Vector2(420 + (i % 5) * 120, 14 + (i / 5) * 70)
		slot.size = Vector2(110, 64)
		slot.add_theme_stylebox_override("normal", Motyw.styl_plaski(Color(0.73, 0.66, 0.54), Color(0.48, 0.4, 0.3), 2, 6))
		slot.add_theme_stylebox_override("hover", Motyw.styl_plaski(Color(0.8, 0.73, 0.6), Motyw.ATRAMENT, 2, 6))
		slot.add_theme_stylebox_override("pressed", Motyw.styl_plaski(Color(0.8, 0.73, 0.6), Motyw.FIOLET, 4, 6))
		slot.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		slot.expand_icon = true
		slot.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
		slot.add_theme_constant_override("icon_max_width", 52)
		slot.tooltip_text = ""
		var nr: int = i
		slot.gui_input.connect(func(e): _slot_input(nr, e))
		panel.add_child(slot)
		sloty.append(slot)
	var b1 := Motyw.przycisk("Dziennik [J]", 20, func(): main.otworz_dziennik())
	b1.position = Vector2(1040, 20)
	b1.size = Vector2(220, 50)
	panel.add_child(b1)
	var b2 := Motyw.przycisk("Menu [Esc]", 20, func(): main.do_menu())
	b2.position = Vector2(1040, 86)
	b2.size = Vector2(220, 50)
	panel.add_child(b2)
	# etykieta pod myszą
	etykieta_myszy = PanelContainer.new()
	etykieta_myszy.add_theme_stylebox_override("panel", Motyw.styl_plaski(Color(0.93, 0.9, 0.82), Motyw.ATRAMENT, 2, 4))
	etykieta_myszy_tekst = Motyw.etykieta("", 18, "plakat", Motyw.ATRAMENT, false)
	etykieta_myszy.add_child(etykieta_myszy_tekst)
	etykieta_myszy.mouse_filter = Control.MOUSE_FILTER_IGNORE
	etykieta_myszy.visible = false
	add_child(etykieta_myszy)
	ikona_kursora = TextureRect.new()
	ikona_kursora.size = Vector2(44, 44)
	ikona_kursora.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	ikona_kursora.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(ikona_kursora)
	odswiez()


func _slot_input(i: int, e: InputEvent) -> void:
	if not (e is InputEventMouseButton and e.pressed):
		return
	var eq: Array = main.logika.ekwipunek
	if i >= eq.size():
		return
	if e.button_index == MOUSE_BUTTON_LEFT:
		main.wybierz_przedmiot(eq[i])
	elif e.button_index == MOUSE_BUTTON_RIGHT:
		var p: Dictionary = Dane.przedmioty[eq[i]]
		komunikat(str(p["nazwa"]) + ": " + str(p["opis"]))
	odswiez()


func komunikat(t: String) -> void:
	komunikat_pelny = t
	komunikat_t = 0.0
	var i := t.find(": ")
	if i > 0 and i < 28:
		kto.text = t.substr(0, i)
		tresc.text = t.substr(i + 2)
	else:
		kto.text = "Janek"
		tresc.text = t
	tresc.visible_characters = 0


func odswiez() -> void:
	var lok: Dictionary = main.logika.dane_lokacji()
	podpis.text = "%s  •  %s" % [lok["nazwa"], lok["data"]]
	var r: Dictionary = main.logika.dane_rozdzialu()
	(rozdzial_etykieta.get_child(0) as Label).text = "Rozdział %d: %s" % [int(r["numer"]), r["tytul"]]
	var eq: Array = main.logika.ekwipunek
	for i in sloty.size():
		var s: Button = sloty[i]
		if i < eq.size():
			s.icon = Dane.tex_ikona(eq[i])
			s.tooltip_text = str(Dane.przedmioty[eq[i]]["nazwa"])
			s.button_pressed = false
			var wyb: bool = main.wybrany == eq[i]
			s.add_theme_stylebox_override("normal", Motyw.styl_plaski(Color(0.8, 0.73, 0.6), Motyw.FIOLET if wyb else Color(0.48, 0.4, 0.3), 4 if wyb else 2, 6))
		else:
			s.icon = null
			s.tooltip_text = ""
			s.add_theme_stylebox_override("normal", Motyw.styl_plaski(Color(0.73, 0.66, 0.54), Color(0.48, 0.4, 0.3), 2, 6))
	if tresc.text == "" and komunikat_pelny == "":
		kto.text = ""
		tresc.text = "Lewy przycisk: działaj • prawy: oglądaj. Kliknij przedmiot w torbie, a potem cel, by go użyć."
		tresc.visible_characters = -1


func _process(delta: float) -> void:
	komunikat_t += delta
	if komunikat_pelny != "":
		var n := int(komunikat_t * 70)
		tresc.visible_characters = -1 if n >= tresc.text.length() else n
	var mysz := get_viewport().get_mouse_position()
	var hid: String = main.najechany_hotspot()
	if hid != "" and mysz.y < 560:
		var h: Dictionary = main.logika.hotspot(hid) if main.logika_ma_hotspot(hid) else {}
		if not h.is_empty():
			var t: String = h["nazwa"]
			if main.wybrany != "":
				t = "Użyj: %s → %s" % [Dane.przedmioty[main.wybrany]["nazwa"], h["nazwa"]]
			etykieta_myszy_tekst.text = t
			etykieta_myszy.visible = true
			etykieta_myszy.reset_size()
			var w := etykieta_myszy.size.x
			etykieta_myszy.position = Vector2(clampf(mysz.x - w / 2, 10, 1270 - w), maxf(40, mysz.y - 52))
		else:
			etykieta_myszy.visible = false
	else:
		etykieta_myszy.visible = false
	if main.wybrany != "":
		ikona_kursora.texture = Dane.tex_ikona(main.wybrany)
		ikona_kursora.position = mysz + Vector2(12, 12)
		ikona_kursora.visible = true
	else:
		ikona_kursora.visible = false
