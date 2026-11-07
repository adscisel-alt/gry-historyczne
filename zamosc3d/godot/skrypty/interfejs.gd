extends CanvasLayer
## Interfejs gry: pasek surowców, panel celów i budowy, dialogi, okna i ekrany.

var g  # gra.gd

const C_TEKST := Color("30200f")
const C_CZERW := Color("a8282c")
const C_ZIELONY := Color("2b7a32")
const C_SZARY := Color("7a6e64")
const C_JASNY := Color("faf0d2")
const C_ZLOTY := Color("f4c848")

var korzen: Control
var motyw: Theme
var ekran: Control
var hud: Control
var okno: Control
var dialog_panel: PanelContainer
var toasty: VBoxContainer
var kompas_w: Control
var etykiety_zas := {}
var etykieta_rozdz: Label
var cele_box: VBoxContainer
var siatka_bud: GridContainer
var info: RichTextLabel
var pasek_dnia: ProgressBar
var etykieta_dnia: Label
var etykieta_rangi: Label
var przyciski_bud := {}
var podpis_celow := ""
var rozdz_siatki := -1
var najechany := ""
var otwarte := ""
var intro_tekst: RichTextLabel
var intro_znaki := 0.0
var wybrany_przedm := -1
var wybrana_karta := ""
var d_tekst: RichTextLabel
var przyciski_dolne := {}


# ===================================================================== budowa
func zbuduj() -> void:
	motyw = _motyw()
	korzen = Control.new()
	korzen.set_anchors_preset(Control.PRESET_FULL_RECT)
	korzen.mouse_filter = Control.MOUSE_FILTER_IGNORE
	korzen.theme = motyw
	add_child(korzen)
	_zbuduj_hud()
	toasty = VBoxContainer.new()
	toasty.mouse_filter = Control.MOUSE_FILTER_IGNORE
	toasty.position = Vector2(20, 64)
	toasty.size = Vector2(900, 10)
	toasty.alignment = BoxContainer.ALIGNMENT_BEGIN
	korzen.add_child(toasty)
	dialog_panel = PanelContainer.new()
	dialog_panel.visible = false
	korzen.add_child(dialog_panel)


func _sb(kolor: Color, ramka: Color, grub := 3, promien := 6, margines := 10) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = kolor
	sb.border_color = ramka
	sb.set_border_width_all(grub)
	sb.set_corner_radius_all(promien)
	sb.set_content_margin_all(margines)
	return sb


func _motyw() -> Theme:
	var th := Theme.new()
	th.default_font_size = 17
	var perg := _sb(Color("ead9ad"), Color("5a3a22"), 3, 8, 14)
	perg.shadow_size = 6
	perg.shadow_color = Color(0, 0, 0, 0.35)
	th.set_stylebox("panel", "PanelContainer", perg)
	th.set_stylebox("normal", "Button", _sb(Color("b48a5a"), Color("3c2616"), 2, 6, 6))
	th.set_stylebox("hover", "Button", _sb(Color("d0a874"), Color("3c2616"), 2, 6, 6))
	th.set_stylebox("pressed", "Button", _sb(Color("f0c860"), Color("3c2616"), 2, 6, 6))
	th.set_stylebox("disabled", "Button", _sb(Color("a89c8c"), Color("6a5e54"), 2, 6, 6))
	th.set_stylebox("focus", "Button", StyleBoxEmpty.new())
	for k in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		th.set_color(k, "Button", C_TEKST)
	th.set_color("font_disabled_color", "Button", Color("5e544c"))
	th.set_color("font_color", "Label", C_TEKST)
	th.set_color("default_color", "RichTextLabel", C_TEKST)
	th.set_stylebox("background", "ProgressBar", _sb(Color("1c120e"), Color("1c120e"), 1, 3, 0))
	th.set_stylebox("fill", "ProgressBar", _sb(C_ZLOTY, C_ZLOTY, 0, 3, 0))
	return th


func _label(tekst: String, rozmiar := 17, kolor := C_TEKST) -> Label:
	var l := Label.new()
	l.text = tekst
	l.add_theme_font_size_override("font_size", rozmiar)
	l.add_theme_color_override("font_color", kolor)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _btn(tekst: String, akcja: Callable, ikona := "", rozmiar := 17) -> Button:
	var b := Button.new()
	b.text = tekst
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_font_size_override("font_size", rozmiar)
	if ikona != "":
		b.icon = load("res://ui/%s.png" % ikona)
		b.expand_icon = false
		b.add_theme_constant_override("icon_max_width", 22)
		b.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	b.pressed.connect(akcja)
	return b


func _ikona(nazwa: String, rozmiar := 24) -> TextureRect:
	var t := TextureRect.new()
	t.texture = load("res://ui/%s.png" % nazwa)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.custom_minimum_size = Vector2(rozmiar, rozmiar)
	t.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t


# ===================================================================== HUD
func _zbuduj_hud() -> void:
	hud = Control.new()
	hud.set_anchors_preset(Control.PRESET_FULL_RECT)
	hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	korzen.add_child(hud)
	var ciemny := _sb(Color(0.15, 0.1, 0.08, 0.92), Color("f4c848"), 0, 0, 6)
	ciemny.border_width_bottom = 2
	# górny pasek
	var gora := PanelContainer.new()
	gora.add_theme_stylebox_override("panel", ciemny)
	gora.set_anchors_preset(Control.PRESET_TOP_WIDE)
	gora.custom_minimum_size.y = 44
	hud.add_child(gora)
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 6)
	gora.add_child(hb)
	for p in [["zloto", "Złoto"], ["drewno", "Drewno"], ["kamien", "Kamień"], ["cegla", "Cegła"],
			["ludnosc", "Mieszczanie"], ["robotnicy", "Praca"], ["wiedza", "Punkty Wiedzy"]]:
		var ik := _ikona("ikona_" + p[0], 28)
		ik.tooltip_text = p[1]
		hb.add_child(ik)
		var l := _label("0", 19, C_JASNY)
		l.custom_minimum_size.x = 70
		hb.add_child(l)
		etykiety_zas[p[0]] = l
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hb.add_child(spacer)
	etykieta_rozdz = _label("", 18, C_ZLOTY)
	hb.add_child(etykieta_rozdz)
	# dolny pasek
	var dol := PanelContainer.new()
	var ciemny2 := ciemny.duplicate()
	ciemny2.border_width_bottom = 0
	ciemny2.border_width_top = 2
	dol.add_theme_stylebox_override("panel", ciemny2)
	dol.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	dol.offset_top = -48
	hud.add_child(dol)
	var hd := HBoxContainer.new()
	hd.add_theme_constant_override("separation", 6)
	dol.add_child(hd)
	for p in [["Ekwipunek (I)", "ikona_sakiewka", func(): przelacz_okno("ekwipunek"), "ekwipunek"],
			["Księga (L)", "ikona_wiedza", func(): przelacz_okno("ksiega"), "ksiega"],
			["Kompas (K)", "ikona_kompas", func(): g.uzyj_przedmiotu("kompas"), "kompas"],
			["Rozbiórka", "ikona_rozbiorka", func(): g.przelacz_rozbiorke(), "rozbiorka"],
			["Pomoc (H)", "ikona_pomoc", func(): przelacz_okno("pomoc"), "pomoc"],
			["Menu", "ikona_menu", func(): przelacz_okno("menu"), "menu"]]:
		var b := _btn(p[0], p[2], p[1], 16)
		b.toggle_mode = false
		hd.add_child(b)
		przyciski_dolne[p[3]] = b
	var sp2 := Control.new()
	sp2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sp2.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hd.add_child(sp2)
	hd.add_child(_ikona("ikona_dzien", 26))
	pasek_dnia = ProgressBar.new()
	pasek_dnia.custom_minimum_size = Vector2(110, 14)
	pasek_dnia.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	pasek_dnia.show_percentage = false
	pasek_dnia.max_value = g.DZIEN_SEK
	pasek_dnia.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hd.add_child(pasek_dnia)
	etykieta_dnia = _label("Dzień 0", 16, C_JASNY)
	hd.add_child(etykieta_dnia)
	etykieta_rangi = _label("", 16, C_ZLOTY)
	etykieta_rangi.custom_minimum_size.x = 170
	etykieta_rangi.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	hd.add_child(etykieta_rangi)
	# prawy panel
	var prawy := PanelContainer.new()
	prawy.set_anchors_preset(Control.PRESET_RIGHT_WIDE)
	prawy.offset_left = -330
	prawy.offset_right = -6
	prawy.offset_top = 52
	prawy.offset_bottom = -54
	hud.add_child(prawy)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 6)
	prawy.add_child(vb)
	vb.add_child(_label("Cele rozdziału", 19, C_CZERW))
	cele_box = VBoxContainer.new()
	cele_box.add_theme_constant_override("separation", 3)
	vb.add_child(cele_box)
	vb.add_child(HSeparator.new())
	vb.add_child(_label("Budowa", 19, C_CZERW))
	siatka_bud = GridContainer.new()
	siatka_bud.columns = 5
	siatka_bud.add_theme_constant_override("h_separation", 4)
	siatka_bud.add_theme_constant_override("v_separation", 4)
	vb.add_child(siatka_bud)
	vb.add_child(HSeparator.new())
	info = RichTextLabel.new()
	info.bbcode_enabled = true
	info.fit_content = true
	info.scroll_active = false
	info.custom_minimum_size = Vector2(300, 90)
	info.size_flags_vertical = Control.SIZE_EXPAND_FILL
	info.add_theme_font_size_override("normal_font_size", 15)
	info.add_theme_font_size_override("bold_font_size", 17)
	info.mouse_filter = Control.MOUSE_FILTER_IGNORE
	vb.add_child(info)
	# kompas
	kompas_w = KompasWidget.new()
	kompas_w.g = g
	kompas_w.position = Vector2(14, 720 - 54 - 190)
	kompas_w.size = Vector2(560, 180)
	kompas_w.anchor_top = 1.0
	kompas_w.anchor_bottom = 1.0
	kompas_w.offset_top = -54 - 186
	kompas_w.offset_bottom = -54
	kompas_w.offset_left = 14
	kompas_w.offset_right = 600
	kompas_w.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.add_child(kompas_w)


func _odswiez_siatke() -> void:
	for c in siatka_bud.get_children():
		c.queue_free()
	przyciski_bud = {}
	for typ in g.D.dostepne[str(int(g.stan.rozdzial))]:
		var b := Button.new()
		b.focus_mode = Control.FOCUS_NONE
		b.custom_minimum_size = Vector2(58, 58)
		b.icon = load("res://ui/miniatura_%s.png" % ("dom" if typ == "rynek" else typ)) if typ != "rynek" else null
		b.expand_icon = true
		b.tooltip_text = g.bud(typ).nazwa
		if typ == "rynek":
			b.text = "Rynek"
			b.add_theme_font_size_override("font_size", 13)
		b.pressed.connect(func(): g.wybierz_budynek(typ))
		b.mouse_entered.connect(func(): najechany = typ)
		b.mouse_exited.connect(func(): if najechany == typ: najechany = "")
		siatka_bud.add_child(b)
		przyciski_bud[typ] = b
	rozdz_siatki = int(g.stan.rozdzial)


func _process(dt: float) -> void:
	if g == null:
		return
	if ekran and is_instance_valid(intro_tekst) and g.scena == "intro":
		intro_znaki += 60 * dt
		intro_tekst.visible_characters = int(intro_znaki)
	if g.nakladka == "dialog" and g.dialog != null and is_instance_valid(d_tekst):
		d_tekst.visible_characters = int(g.dialog.znaki)
	if not hud.visible:
		return
	var s = g.stan
	etykiety_zas.zloto.text = str(int(s.zasoby.zloto))
	etykiety_zas.drewno.text = str(int(s.zasoby.drewno))
	etykiety_zas.kamien.text = str(int(s.zasoby.kamien))
	etykiety_zas.cegla.text = str(int(s.zasoby.cegla))
	etykiety_zas.ludnosc.text = "%d/%d" % [int(s.ludnosc), g.pojemnosc()]
	etykiety_zas.robotnicy.text = "%d%%" % int(g.wydajnosc() * 100)
	etykiety_zas.wiedza.text = "%d PW" % int(s.pw)
	var r = g.D.rozdzialy[str(int(s.rozdzial))]
	etykieta_rozdz.text = "%s · Rozdział %d/4" % [r.lata, int(s.rozdzial)]
	pasek_dnia.value = g.zegar_dnia
	etykieta_dnia.text = "Dzień %d" % int(s.dzien)
	etykieta_rangi.text = g.ranga()
	przyciski_dolne.kompas.modulate = Color(1.3, 1.2, 0.6) if g.kompas else Color.WHITE
	przyciski_dolne.rozbiorka.modulate = Color(1.4, 0.8, 0.7) if g.rozbiorka else Color.WHITE
	if rozdz_siatki != int(s.rozdzial):
		_odswiez_siatke()
	for typ in przyciski_bud:
		var b: Button = przyciski_bud[typ]
		var zablok: bool = g.bud(typ).get("min_pw", 0) > s.pw
		b.modulate = Color(0.55, 0.5, 0.48) if (zablok or not g.stac(typ)) else Color.WHITE
		if g.wybrany == typ:
			b.modulate = Color(1.4, 1.25, 0.6)
	_odswiez_cele()
	_odswiez_info()
	kompas_w.visible = g.kompas
	kompas_w.queue_redraw()


func _odswiez_cele() -> void:
	var podpis := ""
	var stany := []
	for c in g.cele():
		var st = g.stan_celu(c)
		stany.append(st)
		podpis += "%s%d/%d;" % [c[0], st[0], st[1]]
	if podpis == podpis_celow:
		return
	podpis_celow = podpis
	for c in cele_box.get_children():
		c.queue_free()
	var cele = g.cele()
	for i in cele.size():
		var st = stany[i]
		var gotowe: bool = st[0] >= st[1]
		var hb := HBoxContainer.new()
		var kw := ColorRect.new()
		kw.custom_minimum_size = Vector2(14, 14)
		kw.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		kw.color = C_ZIELONY if gotowe else Color("fff6dc")
		hb.add_child(kw)
		var opis: String = cele[i][0] + ("" if int(st[1]) == 1 else " (%d/%d)" % [st[0], st[1]])
		var l := _label(opis, 15, C_ZIELONY if gotowe else C_TEKST)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size.x = 280
		hb.add_child(l)
		cele_box.add_child(hb)


func _koszt_bb(typ: String) -> String:
	var t := ""
	var k = g.koszt(typ)
	for a in k:
		var kol := "#30200f" if g.stan.zasoby.get(a, 0) >= k[a] else "#a8282c"
		t += "[img=20x20]res://ui/ikona_%s.png[/img] [color=%s]%d[/color]   " % [a, kol, k[a]]
	return t


func _odswiez_info() -> void:
	var typ: String = najechany if najechany != "" else g.wybrany
	if typ != "":
		var d = g.bud(typ)
		info.text = "[b][color=#a8282c]%s[/color][/b]\n%s\n%s" % [d.nazwa, _koszt_bb(typ), d.opis]
	elif g.info_budynek >= 0 and g.info_budynek < g.stan.budynki.size():
		var b = g.stan.budynki[g.info_budynek]
		var d2 = g.bud(b.typ)
		var st := "Gotowe" if g.gotowy_b(b) else "W budowie (%d/%d dni)" % [b.postep, d2.czas]
		info.text = "[b][color=#a8282c]%s[/color][/b]\n%s\n%s" % [d2.nazwa, st, d2.opis]
	elif g.rozbiorka:
		info.text = "[b][color=#a8282c]Rozbiórka[/color][/b]\nKliknij budynek, aby go rozebrać (zwrot połowy surowców). Zabytków burzyć nie wolno."
	else:
		info.text = "[color=#7a6e64]Najedź na budynek, aby zobaczyć koszt. Kliknij go, a potem kliknij na mapie. Prawy przycisk myszy anuluje.[/color]"


func toast(tekst: String) -> void:
	if g.tryb == "test":
		return
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", _sb(Color(0.12, 0.08, 0.07, 0.9), C_ZLOTY, 2, 6, 6))
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	p.add_child(_label(tekst, 17, C_JASNY))
	toasty.add_child(p)
	while toasty.get_child_count() > 4:
		var stary := toasty.get_child(0)
		toasty.remove_child(stary)
		stary.queue_free()
	var tw := p.create_tween()
	tw.tween_interval(3.0)
	tw.tween_property(p, "modulate:a", 0.0, 0.5)
	tw.tween_callback(p.queue_free)


# ===================================================================== ekrany
func pokaz_ekran() -> void:
	if ekran:
		ekran.queue_free()
		ekran = null
	zamknij_okno(false)
	hud.visible = g.scena == "gra"
	toasty.visible = g.scena == "gra"
	match g.scena:
		"tytul":
			_ekran_tytul()
		"intro":
			_ekran_intro()
		"koniec":
			_ekran_koniec()


func _pelny() -> Control:
	var c := Control.new()
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	korzen.add_child(c)
	korzen.move_child(c, 0)
	return c


func _ekran_tytul() -> void:
	ekran = _pelny()
	var tlo := TextureRect.new()
	tlo.texture = load("res://ui/tlo_tytul.png")
	tlo.set_anchors_preset(Control.PRESET_FULL_RECT)
	tlo.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tlo.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	ekran.add_child(tlo)
	var vb := VBoxContainer.new()
	vb.set_anchors_preset(Control.PRESET_CENTER_TOP)
	vb.position = Vector2(-400, 26)
	vb.size = Vector2(800, 200)
	vb.alignment = BoxContainer.ALIGNMENT_CENTER
	ekran.add_child(vb)
	for p in [["Jan Zamoyski", 64], ["i Miasto Idealne 3D", 40]]:
		var l := _label(p[0], p[1], C_ZLOTY)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.add_theme_color_override("font_outline_color", Color("1c120e"))
		l.add_theme_constant_override("outline_size", 14)
		vb.add_child(l)
	var pod := _label("Strategia edukacyjna · Zamość, XVI wiek · Blender + Godot", 19, C_JASNY)
	pod.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	pod.add_theme_color_override("font_outline_color", Color("1c120e"))
	pod.add_theme_constant_override("outline_size", 8)
	vb.add_child(pod)
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_CENTER)
	panel.position = Vector2(-150, -40)
	panel.custom_minimum_size = Vector2(300, 0)
	ekran.add_child(panel)
	var m := VBoxContainer.new()
	m.add_theme_constant_override("separation", 10)
	panel.add_child(m)
	m.add_child(_btn("Nowa gra", func(): g.nowa_gra(), "", 20))
	var k := _btn("Kontynuuj", func(): g.wczytaj(), "", 20)
	k.disabled = not g.ma_zapis()
	m.add_child(k)
	m.add_child(_btn("Jak grać?", func(): przelacz_okno("pomoc"), "", 20))
	m.add_child(_btn("Wyjście", func(): get_tree().quit(), "", 20))


func _ekran_intro() -> void:
	ekran = _pelny()
	var cien := ColorRect.new()
	cien.color = Color(0.05, 0.03, 0.02, 0.35)
	cien.set_anchors_preset(Control.PRESET_FULL_RECT)
	ekran.add_child(cien)
	var r = g.D.rozdzialy[str(int(g.stan.rozdzial))]
	var panel := PanelContainer.new()
	panel.position = Vector2(190, 70)
	panel.custom_minimum_size = Vector2(900, 0)
	ekran.add_child(panel)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	panel.add_child(vb)
	var t := _label(r.tytul, 40, C_CZERW)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(t)
	var l := _label(r.lata, 19, C_TEKST)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(l)
	intro_tekst = RichTextLabel.new()
	intro_tekst.text = r.wstep
	intro_tekst.fit_content = true
	intro_tekst.custom_minimum_size = Vector2(860, 260)
	intro_tekst.add_theme_font_size_override("normal_font_size", 20)
	intro_tekst.visible_characters = 0
	intro_znaki = 0.0
	vb.add_child(intro_tekst)
	var b := _btn("Zaczynamy!", klik_intro, "ikona_kompas", 20)
	b.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	vb.add_child(b)


func intro_pelny() -> void:
	intro_znaki = 99999
	if is_instance_valid(intro_tekst):
		intro_tekst.visible_characters = -1


func klik_intro() -> void:
	var dl: int = g.D.rozdzialy[str(int(g.stan.rozdzial))].wstep.length()
	if intro_znaki < dl:
		intro_pelny()
	else:
		g.dzwiek("klik")
		g.wejdz_do_gry()


func _ekran_koniec() -> void:
	ekran = _pelny()
	var cien := ColorRect.new()
	cien.color = Color(0.05, 0.03, 0.08, 0.4)
	cien.set_anchors_preset(Control.PRESET_FULL_RECT)
	ekran.add_child(cien)
	var panel := PanelContainer.new()
	panel.position = Vector2(240, 90)
	panel.custom_minimum_size = Vector2(800, 0)
	ekran.add_child(panel)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	panel.add_child(vb)
	var t := _label("Zamość — Perła Renesansu", 42, C_CZERW)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(t)
	var s = g.stan
	for linia in ["Brawo! Razem z Janem Zamoyskim zbudowałeś miasto idealne.",
			"Zamoyski zmarł w 1605 r., ale jego miasto przetrwało wieki.",
			"W 1992 r. Stare Miasto w Zamościu wpisano na listę UNESCO.", "",
			"Budowli: %d   ·   Mieszczan: %d   ·   Dni budowy: %d" % [s.budynki.size(), int(s.ludnosc), int(s.dzien)],
			"Punkty Wiedzy: %d   ·   Karty Księgi: %d/%d" % [int(s.pw), s.przeczytane.size(), g.D.wiedza.size()]]:
		var l := _label(linia, 20)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		vb.add_child(l)
	var rg := _label("Twoja ranga: " + g.ranga(), 24, C_CZERW)
	rg.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(rg)
	var b := _btn("Menu główne", func(): g.zapisz(); g.pokaz_tytul(), "", 20)
	b.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	vb.add_child(b)


# ===================================================================== dialog
func odswiez_dialog() -> void:
	for c in dialog_panel.get_children():
		dialog_panel.remove_child(c)
		c.queue_free()
	var dl = g.dialog
	dialog_panel.visible = dl != null
	if dl == null:
		return
	var quiz: bool = dl.tryb != "tekst"
	dialog_panel.position = Vector2(20, 720 - (330 if quiz else 236) - 56)
	dialog_panel.size = Vector2(910, 0)
	dialog_panel.custom_minimum_size = Vector2(910, 320 if quiz else 226)
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 16)
	dialog_panel.add_child(hb)
	var mowca: String = dl.kwestie[min(dl.i, dl.kwestie.size() - 1)][0] if dl.kwestie.size() > 0 else "narrator"
	var portret := TextureRect.new()
	portret.custom_minimum_size = Vector2(170, 170)
	portret.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	portret.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	portret.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	if ResourceLoader.exists("res://ui/portret_%s.png" % mowca):
		portret.texture = load("res://ui/portret_%s.png" % mowca)
	else:
		portret.texture = load("res://ui/ikona_ksiega.png")
		portret.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	hb.add_child(portret)
	var vb := VBoxContainer.new()
	vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vb.add_theme_constant_override("separation", 8)
	hb.add_child(vb)
	var naglowek := HBoxContainer.new()
	naglowek.add_child(_label(g.D.nazwy_postaci.get(mowca, mowca), 24, C_CZERW))
	if quiz:
		naglowek.add_child(_label("   ZAGADKA", 19, C_ZIELONY))
	vb.add_child(naglowek)
	d_tekst = null
	if dl.tryb == "tekst":
		d_tekst = RichTextLabel.new()
		d_tekst.text = dl.kwestie[dl.i][1]
		d_tekst.fit_content = true
		d_tekst.custom_minimum_size = Vector2(680, 110)
		d_tekst.add_theme_font_size_override("normal_font_size", 20)
		d_tekst.visible_characters = int(dl.znaki)
		d_tekst.mouse_filter = Control.MOUSE_FILTER_IGNORE
		vb.add_child(d_tekst)
		var b := _btn("Dalej »  (Spacja)", func(): g.dalej_dialog(), "", 16)
		b.size_flags_horizontal = Control.SIZE_SHRINK_END
		vb.add_child(b)
	else:
		var q = dl.zagadka
		var p := _label(q.pytanie, 20)
		p.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		p.custom_minimum_size.x = 680
		vb.add_child(p)
		if dl.tryb == "zagadka":
			for i in dl.odp.size():
				var b := _btn("%d.  %s" % [i + 1, dl.odp[i]], func(): g.odpowiedz(i), "", 18)
				b.alignment = HORIZONTAL_ALIGNMENT_LEFT
				b.disabled = i in dl.zle
				vb.add_child(b)
			if dl.zle.size() > 0:
				vb.add_child(_label("Nie tym razem — spróbuj jeszcze raz!", 17, C_CZERW))
		else:
			vb.add_child(_label("Brawo! Dobra odpowiedź: " + q.poprawna, 19, C_ZIELONY))
			var w := _label(q.wyjasnienie, 18)
			w.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			w.custom_minimum_size.x = 680
			vb.add_child(w)
			var b2 := _btn("Dalej »", func(): g.zamknij_dialog(), "", 18)
			b2.size_flags_horizontal = Control.SIZE_SHRINK_END
			vb.add_child(b2)


# ===================================================================== okna
func przelacz_okno(nazwa: String) -> void:
	if otwarte == nazwa:
		zamknij_okno()
	else:
		pokaz_okno(nazwa)
	g.dzwiek("strona" if nazwa == "ksiega" else "klik")


func zamknij_okno(dzw := true) -> void:
	if okno:
		okno.queue_free()
		okno = null
	otwarte = ""
	if g.nakladka != "dialog":
		g.nakladka = ""


func odswiez_okno() -> void:
	if otwarte != "":
		pokaz_okno(otwarte)
	elif okno:
		zamknij_okno()


func _okno(tytul: String, rozmiar: Vector2) -> VBoxContainer:
	if okno:
		okno.queue_free()
	okno = Control.new()
	okno.set_anchors_preset(Control.PRESET_FULL_RECT)
	korzen.add_child(okno)
	var cien := ColorRect.new()
	cien.color = Color(0.04, 0.02, 0.06, 0.55)
	cien.set_anchors_preset(Control.PRESET_FULL_RECT)
	okno.add_child(cien)
	var p := PanelContainer.new()
	p.position = (Vector2(1280, 720) - rozmiar) / 2
	p.custom_minimum_size = rozmiar
	okno.add_child(p)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	p.add_child(vb)
	var hb := HBoxContainer.new()
	var t := _label(tytul, 26, C_CZERW)
	t.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hb.add_child(t)
	hb.add_child(_btn("✕", func(): zamknij_okno(), "", 18))
	vb.add_child(hb)
	return vb


func pokaz_okno(nazwa: String) -> void:
	otwarte = nazwa
	if g.scena == "gra":
		g.nakladka = nazwa
	match nazwa:
		"ekwipunek":
			_okno_ekwipunek()
		"ksiega":
			_okno_ksiega()
		"plan":
			_okno_plan()
		"menu":
			_okno_menu()
		"pomoc":
			_okno_pomoc()


func wybierz_przedmiot(i: int) -> void:
	wybrany_przedm = i
	pokaz_okno("ekwipunek")


func _okno_ekwipunek() -> void:
	var vb := _okno("Ekwipunek Jana Zamoyskiego", Vector2(820, 470))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 20)
	vb.add_child(hb)
	var gr := GridContainer.new()
	gr.columns = 5
	gr.add_theme_constant_override("h_separation", 8)
	gr.add_theme_constant_override("v_separation", 8)
	hb.add_child(gr)
	var ekw = g.stan.ekwipunek
	for i in 10:
		var b := Button.new()
		b.focus_mode = Control.FOCUS_NONE
		b.custom_minimum_size = Vector2(80, 80)
		if i < ekw.size():
			b.icon = load("res://ui/ikona_%s.png" % g.D.przedmioty[ekw[i]].ikona)
			b.expand_icon = true
			b.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			b.tooltip_text = g.D.przedmioty[ekw[i]].nazwa
			b.pressed.connect(func(): wybierz_przedmiot(i); g.dzwiek("klik"))
			if i == wybrany_przedm:
				b.modulate = Color(1.4, 1.25, 0.6)
		else:
			b.disabled = true
		gr.add_child(b)
	var opis := VBoxContainer.new()
	opis.custom_minimum_size.x = 330
	opis.add_theme_constant_override("separation", 8)
	hb.add_child(opis)
	if wybrany_przedm >= 0 and wybrany_przedm < ekw.size():
		var p: String = ekw[wybrany_przedm]
		var d = g.D.przedmioty[p]
		var ik := _ikona("ikona_" + d.ikona, 72)
		opis.add_child(ik)
		var n := _label(d.nazwa, 22, C_CZERW)
		opis.add_child(n)
		var o := _label(d.opis, 17)
		o.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		o.custom_minimum_size.x = 320
		opis.add_child(o)
		if d.uzycie != null:
			opis.add_child(_btn("Użyj", func(): g.uzyj_przedmiotu(p), "", 19))
	else:
		var o2 := _label("Kliknij przedmiot, aby przeczytać jego opis. Nowe przedmioty zdobywasz za rozmowy i ukończone rozdziały.", 17, C_SZARY)
		o2.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		o2.custom_minimum_size.x = 320
		opis.add_child(o2)
	vb.add_child(HSeparator.new())
	vb.add_child(_label("Punkty Wiedzy: %d   ·   Ranga: %s   ·   Karty Księgi: %d/%d przeczytanych" % [
		int(g.stan.pw), g.ranga(), g.stan.przeczytane.size(), g.D.wiedza.size()], 18))


func czytaj_karte(k: String) -> void:
	wybrana_karta = k
	g.dzwiek("strona")
	if not k in g.stan.przeczytane:
		g.stan.przeczytane.append(k)
		var zysk := 3 if "pioro" in g.stan.ekwipunek else 2
		g.stan.pw += zysk
		toast("+%d PW za przeczytanie karty!" % zysk)
	pokaz_okno("ksiega")


func _okno_ksiega() -> void:
	var vb := _okno("Księga Wiedzy", Vector2(1000, 540))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 16)
	vb.add_child(hb)
	var sc := ScrollContainer.new()
	sc.custom_minimum_size = Vector2(330, 440)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	hb.add_child(sc)
	var lista := VBoxContainer.new()
	lista.custom_minimum_size.x = 310
	sc.add_child(lista)
	var ukryte := 0
	for k in g.D.wiedza_kolejnosc:
		if not k in g.stan.karty:
			ukryte += 1
			continue
		var tytul: String = g.D.wiedza[k][0]
		if not k in g.stan.przeczytane:
			tytul += "   ★ nowa!"
		var b := _btn(tytul, func(): czytaj_karte(k), "", 15)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		if k == wybrana_karta:
			b.modulate = Color(1.3, 1.2, 0.7)
		lista.add_child(b)
	if ukryte:
		lista.add_child(_label("Do odkrycia: %d kart" % ukryte, 15, C_SZARY))
	hb.add_child(VSeparator.new())
	var prawa := VBoxContainer.new()
	prawa.custom_minimum_size.x = 600
	hb.add_child(prawa)
	if wybrana_karta != "":
		prawa.add_child(_label(g.D.wiedza[wybrana_karta][0], 26, C_CZERW))
		var o := _label(g.D.wiedza[wybrana_karta][1], 19)
		o.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		o.custom_minimum_size.x = 590
		prawa.add_child(o)
	else:
		var o2 := _label("Wybierz kartę z listy. Każda nowo przeczytana karta daje Punkty Wiedzy! Nowe karty odkrywasz, budując zabytki i rozmawiając z postaciami.", 19, C_SZARY)
		o2.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		o2.custom_minimum_size.x = 590
		prawa.add_child(o2)


func _okno_plan() -> void:
	var vb := _okno("Plan miasta Bernarda Morando", Vector2(1040, 520))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 16)
	vb.add_child(hb)
	var plan := PlanWidget.new()
	plan.g = g
	plan.custom_minimum_size = Vector2(640, 416)
	hb.add_child(plan)
	var o := _label("Plan Zamościa przypomina człowieka: pałac to głowa, główna ulica to kręgosłup, a Akademia i Kolegiata to płuca. Rynek jest sercem handlu.\n\nGranatowe pola — do zbudowania.\nZielone — zbudowane.\nCzerwona kropka — Ty.\nCzerwona linia — wały między 7 bastionami.\nNa górze planu jest północ (N).", 17)
	o.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	o.custom_minimum_size.x = 330
	hb.add_child(o)


func _okno_menu() -> void:
	var vb := _okno("Menu", Vector2(380, 340))
	for p in [["Wróć do gry", func(): zamknij_okno()],
			["Zapisz grę", func(): g.zapisz(); toast("Gra zapisana!"); zamknij_okno()],
			["Muzyka wł./wył. (M)", func(): g.przelacz_muzyke()],
			["Menu główne", func(): g.zapisz(); g.pokaz_tytul()],
			["Wyjście z gry", func(): g.zapisz(); get_tree().quit()]]:
		vb.add_child(_btn(p[0], p[1], "", 19))


func _okno_pomoc() -> void:
	var vb := _okno("Pomoc", Vector2(760, 560))
	var linie: Array = g.D.pomoc.duplicate()
	linie[1] = "WASD / strzałki — chodzenie · Q / R lub prawy przycisk myszy — obrót kamery"
	linie.insert(2, "Kółko myszy — przybliżanie i oddalanie kamery")
	for l in linie:
		var lab := _label(l, 17, C_CZERW if l == l.to_upper() and l != "" else C_TEKST)
		vb.add_child(lab)


# ===================================================================== widżety rysowane
class KompasWidget extends Control:
	var g
	var roza: Texture2D = preload("res://ui/roza.png")

	func _draw() -> void:
		if g == null:
			return
		var c := Vector2(80, 96)
		var obrot: float = g.yaw
		draw_circle(c, 78, Color(0.1, 0.06, 0.04, 0.55))
		draw_set_transform(c, -obrot, Vector2(2.6, 2.6))
		draw_texture(roza, -roza.get_size() / 2)
		draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)
		var cel = g.cel_kompasu()
		var hp: Vector3 = g.bohater.position
		var kat := 0.0
		var linia: String = cel[1]
		if cel[0] != null:
			var d: Vector3 = cel[0] - hp
			var namiar := atan2(d.x, -d.z)
			kat = namiar - obrot
			var kroki := int(Vector2(d.x, d.z).length() / g.T)
			linia = "%s — %s, %s" % [cel[1], g.kierunek_slownie(d.x, d.z), g.kroki_slownie(kroki)] if kroki > 0 else cel[1] + " — jesteś na miejscu!"
		else:
			kat = -obrot + sin(g.t * 2) * 0.15
		var kier := Vector2(sin(kat), -cos(kat))
		var bok := Vector2(kier.y, -kier.x) * 7
		draw_colored_polygon(PackedVector2Array([c + kier * 52, c + bok, c - bok]), Color(0.8, 0.12, 0.15))
		draw_colored_polygon(PackedVector2Array([c - kier * 38, c + bok, c - bok]), Color(0.16, 0.22, 0.48))
		draw_circle(c, 5, Color(0.95, 0.78, 0.28))
		var f := ThemeDB.fallback_font
		var szer := f.get_string_size(linia, HORIZONTAL_ALIGNMENT_LEFT, -1, 19).x
		var r := Rect2(Vector2(170, 112), Vector2(szer + 24, 34))
		draw_rect(r, Color(0.12, 0.08, 0.07, 0.9))
		draw_rect(r, Color("f4c848"), false, 2)
		draw_string(f, r.position + Vector2(12, 24), linia, HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color("faf0d2"))


class PlanWidget extends Control:
	var g

	func _draw() -> void:
		var D = g.D
		var s := 16.0
		var kolory := {".": Color(0.62, 0.72, 0.5), "T": Color(0.42, 0.56, 0.38), "R": Color(0.62, 0.62, 0.6),
			"\"": Color(0.58, 0.62, 0.48), "=": Color(0.8, 0.7, 0.52), "B": Color(0.78, 0.74, 0.68),
			"#": Color(0.6, 0.45, 0.3), "~": Color(0.42, 0.58, 0.78)}
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.95, 0.88, 0.7))
		for y in int(D.mapa_h):
			for x in int(D.mapa_w):
				draw_rect(Rect2(x * s, y * s, s, s), kolory[g.mapa[y][x]].lerp(Color(0.96, 0.88, 0.7), 0.35))
		var pk := PackedVector2Array()
		for b in D.bastiony:
			pk.append(Vector2(b[0], b[1]) * s)
		pk.append(pk[0])
		draw_polyline(pk, Color(0.55, 0.2, 0.15), 3)
		for dz in D.dzialki:
			var d = g.bud(dz[0])
			var r := Rect2(dz[1] * s, dz[2] * s, d.w * s, d.h * s)
			var kol := Color(0.16, 0.48, 0.2) if g.dzialka_zajeta(dz[0], dz[1], dz[2]) else Color(0.16, 0.22, 0.5)
			draw_rect(r, kol, dz[0] != "rynek")
			if dz[0] == "rynek":
				draw_rect(r, kol, false, 2)
		var f := ThemeDB.fallback_font
		for e in [["głowa", 8.6, 9.6], ["płuco", 13.6, 6.6], ["płuco", 13.0, 17.3], ["kręgosłup", 13.0, 12.6], ["serce", 21.5, 16.2]]:
			draw_string(f, Vector2(e[1], e[2]) * s, e[0], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0.66, 0.12, 0.14))
		var hp: Vector3 = g.bohater.position / g.T * s
		draw_circle(Vector2(hp.x, hp.z), 6, Color(0.9, 0.1, 0.1))
		draw_string(f, Vector2(size.x - 30, 24), "N", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(0.66, 0.12, 0.14))
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.2, 0.12, 0.08), false, 2)
