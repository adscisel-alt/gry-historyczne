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
	var pozycje := []
	for z in g.D.zasoby:
		pozycje.append([z.id, z.nazwa])
	pozycje += [["dzialacze", "Działacze"], ["robotnicy", "Praca placówek"], ["wiedza", "Punkty Wiedzy"]]
	for p in pozycje:
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
	vb.add_child(_label("Cele kampanii", 19, C_CZERW))
	cele_box = VBoxContainer.new()
	cele_box.add_theme_constant_override("separation", 3)
	vb.add_child(cele_box)
	vb.add_child(HSeparator.new())
	vb.add_child(_label("Placówki", 19, C_CZERW))
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
	for typ in g.R.dostepne:
		var b := Button.new()
		b.focus_mode = Control.FOCUS_NONE
		b.custom_minimum_size = Vector2(58, 58)
		b.icon = load("res://ui/miniatura_%s.png" % g._model_budynku(typ))
		b.expand_icon = true
		b.tooltip_text = g.bud(typ).nazwa
		b.pressed.connect(func(): g.wybierz_budynek(typ))
		b.mouse_entered.connect(func(): najechany = typ)
		b.mouse_exited.connect(func(): if najechany == typ: najechany = "")
		siatka_bud.add_child(b)
		przyciski_bud[typ] = b
	rozdz_siatki = int(g.stan.rozdzial)


func _process(dt: float) -> void:
	if g == null:
		return
	_aktualizuj_mape(dt)
	if ekran and is_instance_valid(intro_tekst) and g.scena == "intro":
		intro_znaki += 60 * dt
		intro_tekst.visible_characters = int(intro_znaki)
	if g.nakladka == "dialog" and g.dialog != null and is_instance_valid(d_tekst):
		d_tekst.visible_characters = int(g.dialog.znaki)
	if not hud.visible:
		return
	var s = g.stan
	for z in g.D.zasoby:
		etykiety_zas[z.id].text = str(int(s.zasoby[z.id]))
	etykiety_zas.dzialacze.text = "%d/%d" % [int(s.ludnosc), g.pojemnosc()]
	etykiety_zas.robotnicy.text = "%d%%" % int(g.wydajnosc() * 100)
	etykiety_zas.wiedza.text = "%d PW" % int(s.pw)
	var r = g.D.rozdzialy[str(int(s.rozdzial))]
	etykieta_rozdz.text = "%s, %s · Kampania %d/%d" % [r.miejsce, r.lata, int(s.rozdzial), int(g.D.liczba_rozdzialow)]
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
		"mapa":
			_ekran_mapy()


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
	for p in [["Roman Dmowski", 64], ["Droga do Wersalu 3D", 40]]:
		var l := _label(p[0], p[1], C_ZLOTY)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.add_theme_color_override("font_outline_color", Color("1c120e"))
		l.add_theme_constant_override("outline_size", 14)
		vb.add_child(l)
	var pod := _label("Strategia edukacyjna · Polska 1914–1919 · Blender + Godot", 19, C_JASNY)
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
	var l := _label("%s · %s" % [r.miejsce, r.lata], 19, C_TEKST)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(l)
	g.lektor(r.wstep)
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
	var t := _label("Polska wraca na mapę Europy", 42, C_CZERW)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(t)
	var s = g.stan
	for linia in ["Brawo! Razem z Romanem Dmowskim przeszedłeś drogę od Warszawy 1914 do Wersalu 1919.",
			"28 czerwca 1919 r. traktat wersalski potwierdził odrodzenie Polski.",
			"Niepodległość wywalczyło wielu ludzi: politycy, żołnierze, powstańcy i zwykli obywatele.", "",
			"Dni kampanii: %d   ·   Przedmioty: %d" % [int(s.dzien), s.ekwipunek.size()],
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
	naglowek.add_child(_label(g.D.postacie[mowca].imie if g.D.postacie.has(mowca) else mowca, 24, C_CZERW))
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
		g.lektor(dl.kwestie[dl.i][1])
		var b := _btn("Dalej »  (Spacja)", func(): g.dalej_dialog(), "", 16)
		b.size_flags_horizontal = Control.SIZE_SHRINK_END
		vb.add_child(b)
	else:
		var q = dl.zagadka
		if dl.tryb == "zagadka":
			g.lektor(q.pytanie)
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
	if otwarte != "":
		g.ucisz_lektora()
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
	var vb := _okno("Ekwipunek Romana Dmowskiego", Vector2(820, 470))
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
	g.lektor(g.D.wiedza[k][1])
	g.dzwiek("strona")
	if not k in g.stan.przeczytane:
		g.stan.przeczytane.append(k)
		var zysk := 3 if "pioro" in g.stan.ekwipunek else 2
		g.stan.pw += zysk
		toast("+%d PW za przeczytanie karty!" % zysk)
	pokaz_okno("ksiega")


var ksiega_tryb := "karty"
var wybrane_wydarzenie := -1


func _okno_ksiega() -> void:
	var vb := _okno("Księga Wiedzy", Vector2(1000, 560))
	var zakladki := HBoxContainer.new()
	zakladki.alignment = BoxContainer.ALIGNMENT_CENTER
	for z in [["karty", "Karty wiedzy"], ["os", "Oś czasu 1914–1919"]]:
		var b := _btn(z[1], func(): ksiega_tryb = z[0]; g.ucisz_lektora(); pokaz_okno("ksiega"), "", 17)
		if ksiega_tryb == z[0]:
			b.modulate = Color(1.35, 1.2, 0.7)
		zakladki.add_child(b)
	vb.add_child(zakladki)
	if ksiega_tryb == "os":
		_os_czasu(vb)
		return
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 16)
	vb.add_child(hb)
	var sc := ScrollContainer.new()
	sc.custom_minimum_size = Vector2(330, 420)
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
	var vb := _okno("Mapa kampanii: %s (%s)" % [g.R.miejsce, g.R.lata], Vector2(1040, 520))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 16)
	vb.add_child(hb)
	var plan := PlanWidget.new()
	plan.g = g
	plan.custom_minimum_size = Vector2(640, 416)
	hb.add_child(plan)
	var o := _label("Każda kampania toczy się w innym miejscu: Warszawa (1914), Lozanna (1917), Francja (1918) i Paryż (1919).\n\nGranatowe pola — miejsca ważnych placówek.\nZielone — już zbudowane.\nŻółte kropki — postacie do rozmowy.\nCzerwona kropka — Ty.\nNa górze mapy jest północ (N).", 17)
	o.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	o.custom_minimum_size.x = 330
	hb.add_child(o)


func _okno_menu() -> void:
	var vb := _okno("Menu", Vector2(380, 340))
	for p in [["Wróć do gry", func(): zamknij_okno()],
			["Zapisz grę", func(): g.zapisz(); toast("Gra zapisana!"); zamknij_okno()],
			["Muzyka wł./wył. (M)", func(): g.przelacz_muzyke()],
			["Lektor wł./wył. (G)", func(): g.przelacz_lektora()],
			["Menu główne", func(): g.zapisz(); g.pokaz_tytul()],
			["Wyjście z gry", func(): g.zapisz(); get_tree().quit()]]:
		vb.add_child(_btn(p[0], p[1], "", 19))


func _okno_pomoc() -> void:
	var vb := _okno("Pomoc", Vector2(760, 560))
	var linie: Array = g.D.pomoc.duplicate()
	for l in linie:
		var lab := _label(l, 17, C_CZERW if l == l.to_upper() and l != "" else C_TEKST)
		vb.add_child(lab)


# ===================================================================== przerywniki filmowe
var kino_w: Control


func odswiez_kino() -> void:
	if kino_w:
		kino_w.queue_free()
		kino_w = null
	if g.nakladka != "kino":
		hud.visible = g.scena == "gra"
		toasty.visible = hud.visible
		return
	hud.visible = false
	toasty.visible = false
	kino_w = Control.new()
	kino_w.set_anchors_preset(Control.PRESET_FULL_RECT)
	kino_w.mouse_filter = Control.MOUSE_FILTER_IGNORE
	korzen.add_child(kino_w)
	for gora in [true, false]:
		var pas := ColorRect.new()
		pas.color = Color(0, 0, 0)
		pas.mouse_filter = Control.MOUSE_FILTER_IGNORE
		pas.set_anchors_preset(Control.PRESET_TOP_WIDE if gora else Control.PRESET_BOTTOM_WIDE)
		pas.custom_minimum_size.y = 70 if gora else 170
		if not gora:
			pas.offset_top = -170
		kino_w.add_child(pas)
	var napis = g.D.przerywniki[g.kino_nazwa][g.kino_i]
	g.lektor(napis[1])
	var hb := HBoxContainer.new()
	hb.position = Vector2(60, 720 - 155)
	hb.custom_minimum_size = Vector2(1160, 140)
	hb.add_theme_constant_override("separation", 18)
	kino_w.add_child(hb)
	if ResourceLoader.exists("res://ui/portret_%s.png" % napis[0]):
		var por := TextureRect.new()
		por.texture = load("res://ui/portret_%s.png" % napis[0])
		por.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		por.custom_minimum_size = Vector2(120, 120)
		hb.add_child(por)
	var vb := VBoxContainer.new()
	vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb.add_child(vb)
	var kto: String = g.D.postacie[napis[0]].imie if g.D.postacie.has(napis[0]) else ""
	vb.add_child(_label(kto, 22, C_ZLOTY))
	var tekst := _label(napis[1], 23, C_JASNY)
	tekst.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	tekst.custom_minimum_size.x = 860
	vb.add_child(tekst)
	var b := _btn("Dalej »", func(): g.dalej_kino(), "", 18)
	b.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	hb.add_child(b)
	var tytul := _label({"przemowienie": "Paryż, 29 stycznia 1919", "listopad": "Warszawa, 11 listopada 1918",
		"traktat": "Wersal, 28 czerwca 1919"}.get(g.kino_nazwa, ""), 22, C_ZLOTY)
	tytul.position = Vector2(60, 22)
	kino_w.add_child(tytul)
	var pomin := _btn("Pomiń (Esc)", func(): g.zakoncz_kino(), "", 15)
	pomin.position = Vector2(1120, 18)
	kino_w.add_child(pomin)


# ===================================================================== mini-gra: przemówienie
var mini_w: Control


func odswiez_przemowienie() -> void:
	if mini_w:
		mini_w.queue_free()
		mini_w = null
	var m = g.minigra
	if m == null or g.nakladka != "przemowienie":
		return
	mini_w = Control.new()
	mini_w.set_anchors_preset(Control.PRESET_FULL_RECT)
	korzen.add_child(mini_w)
	var cien := ColorRect.new()
	cien.color = Color(0.04, 0.02, 0.06, 0.6)
	cien.set_anchors_preset(Control.PRESET_FULL_RECT)
	mini_w.add_child(cien)
	var p := PanelContainer.new()
	p.position = Vector2(170, 60)
	p.custom_minimum_size = Vector2(940, 560)
	mini_w.add_child(p)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 12)
	p.add_child(vb)
	var t := _label("Przemówienie przed Radą Dziesięciu", 30, C_CZERW)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(t)
	var hm := HBoxContainer.new()
	hm.add_child(_label("Przekonanie Rady:  ", 18))
	var pb := ProgressBar.new()
	pb.max_value = 125
	pb.value = m.punkty
	pb.show_percentage = false
	pb.custom_minimum_size = Vector2(600, 22)
	pb.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	hm.add_child(pb)
	hm.add_child(_label("  %d / 125" % m.punkty, 18))
	vb.add_child(hm)
	var rundy: Array = g.D.przemowienie
	if m.stan == "wynik":
		var gw: int = g.gwiazdki()
		var hs := HBoxContainer.new()
		hs.alignment = BoxContainer.ALIGNMENT_CENTER
		for i in 3:
			var s := _label("★", 72, C_ZLOTY if i < gw else Color(0.6, 0.55, 0.5))
			s.add_theme_color_override("font_outline_color", Color("3c2616"))
			s.add_theme_constant_override("outline_size", 8)
			hs.add_child(s)
		vb.add_child(hs)
		var opis := _label(["", "Rada słuchała uprzejmie, ale nie dała się w pełni przekonać.",
			"Dobre przemówienie! Wielu delegatów kiwa głowami.",
			"Wspaniale! Delegaci wstają i gratulują znajomości sprawy."][gw], 22)
		opis.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		opis.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		vb.add_child(opis)
		var info := _label("Prawdziwe przemówienie Dmowskiego 29 stycznia 1919 r. trwało około 5 godzin. Mówił na zmianę po francusku i po angielsku, korzystając z map i danych.", 18, C_SZARY)
		info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		info.custom_minimum_size.x = 880
		vb.add_child(info)
		var b := _btn("Zakończ przemówienie »", func(): g.dalej_przemowienie(), "", 20)
		b.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		vb.add_child(b)
		return
	var r = rundy[m.runda]
	if m.stan == "pytanie":
		g.lektor(r.pytanie)
	vb.add_child(_label("Pytanie %d/%d — %s" % [m.runda + 1, rundy.size(), r.pytajacy], 18, C_SZARY))
	var q := _label(r.pytanie, 23)
	q.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	q.custom_minimum_size.x = 880
	vb.add_child(q)
	if m.stan == "pytanie":
		vb.add_child(_label("Wybierz najlepszy argument (1, 2, 3):", 17, C_SZARY))
		for i in 3:
			var odp = r.odpowiedzi[m.kolejnosc[i]]
			var b := _btn("%d.  %s" % [i + 1, odp[0]], func(): g.wybierz_argument(i), "", 18)
			b.alignment = HORIZONTAL_ALIGNMENT_LEFT
			b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			b.custom_minimum_size = Vector2(880, 52)
			vb.add_child(b)
	else:
		var dobre: bool = m.ostatnie >= 20
		vb.add_child(_label("Oklaski! Trafny argument." if dobre else "Delegaci kręcą głowami…", 24,
			C_ZIELONY if dobre else C_CZERW))
		var re := _label(r.reakcja, 19)
		re.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		re.custom_minimum_size.x = 880
		vb.add_child(re)
		var b2 := _btn("Następne pytanie »" if m.runda + 1 < rundy.size() else "Podsumowanie »", func(): g.dalej_przemowienie(), "", 20)
		b2.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		vb.add_child(b2)


# ===================================================================== oś czasu 1914–1919
func wybierz_wydarzenie(i: int) -> void:
	wybrane_wydarzenie = i
	g.dzwiek("klik")
	g.lektor(g.D.os_czasu[i][3])
	pokaz_okno("ksiega")


func _os_czasu(vb: VBoxContainer) -> void:
	var os := OsCzasuWidget.new()
	os.g = g
	os.ui = self
	os.wybrane = wybrane_wydarzenie
	os.custom_minimum_size = Vector2(960, 250)
	vb.add_child(os)
	var opis := PanelContainer.new()
	opis.add_theme_stylebox_override("panel", _sb(Color("f6ecd0"), Color("b89a6a"), 2, 6, 10))
	opis.custom_minimum_size = Vector2(960, 120)
	vb.add_child(opis)
	var ov := VBoxContainer.new()
	opis.add_child(ov)
	if wybrane_wydarzenie >= 0:
		var e = g.D.os_czasu[wybrane_wydarzenie]
		ov.add_child(_label("%s — %s" % [e[1], e[2]], 22, C_CZERW if e[4] == "pl" else Color("2c4a8a")))
		var t := _label(e[3], 18)
		t.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		t.custom_minimum_size.x = 930
		ov.add_child(t)
		if e[5]:
			ov.add_child(_label("To wydarzenie znajdziesz też na osi czasu klasy VII.", 15, C_SZARY))
	else:
		ov.add_child(_label("Kliknij kropkę na osi, aby przeczytać o wydarzeniu. Czerwone — historia Polski, niebieskie — historia świata. Złota ramka — wydarzenia z kampanii, które już przeszedłeś.", 17, C_SZARY))
		ov.get_child(0).autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		ov.get_child(0).custom_minimum_size.x = 930
	var hb := HBoxContainer.new()
	hb.alignment = BoxContainer.ALIGNMENT_CENTER
	hb.add_child(_btn("Otwórz pełną oś czasu klasy VII (1815–1939) w przeglądarce", func(): OS.shell_open(g.D.os_czasu_klasa7), "ikona_wiedza", 16))
	vb.add_child(hb)


class OsCzasuWidget extends Control:
	var g
	var ui
	var wybrane := -1
	const POCZ := 1914.0
	const KON := 1920.0

	func _x(rok: float) -> float:
		return 30 + (rok - POCZ) / (KON - POCZ) * (size.x - 60)

	var _poziomy := []

	func _poz(i: int) -> Vector2:
		if _poziomy.size() != g.D.os_czasu.size():
			_rozmiesc()
		var e = g.D.os_czasu[i]
		return Vector2(_x(e[0]), size.y / 2 + _poziomy[i] * 36)

	func _rozmiesc() -> void:
		## Każde wydarzenie dostaje poziom (nad lub pod osią), na którym jego podpis się nie nakłada.
		var f := ThemeDB.fallback_font
		var koniec_poziomu := {}
		_poziomy = []
		for e in g.D.os_czasu:
			var x := _x(e[0])
			var pol: float = min(f.get_string_size(e[2], HORIZONTAL_ALIGNMENT_LEFT, -1, 13).x, 150.0) / 2 + 6
			var wybrany := 1
			for p in [-1, 1, -2, 2, -3, 3]:
				if koniec_poziomu.get(p, -1000.0) < x - pol:
					wybrany = p
					break
			koniec_poziomu[wybrany] = x + pol
			_poziomy.append(wybrany)

	func _koniec_kampanii() -> float:
		return [1915.7, 1917.7, 1919.0, 1920.0][clampi(int(g.stan.rozdzial) - 1, 0, 3)] if g.scena == "gra" else 1920.0

	func _draw() -> void:
		var f := ThemeDB.fallback_font
		var y0 := size.y / 2
		draw_rect(Rect2(Vector2.ZERO, size), Color("f6ecd0"))
		draw_line(Vector2(20, y0), Vector2(size.x - 20, y0), Color("5a3a22"), 4)
		for rok in range(1914, 1921):
			var x := _x(rok)
			draw_line(Vector2(x, y0 - 10), Vector2(x, y0 + 10), Color("5a3a22"), 3)
			draw_string(f, Vector2(x - 18, y0 + 30 if rok % 2 else y0 - 18), str(rok), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("5a3a22"))
		draw_rect(Rect2(_x(1914.58), y0 - 4, _x(1918.86) - _x(1914.58), 8), Color(0.55, 0.3, 0.25, 0.5))
		var granica := _koniec_kampanii()
		for i in g.D.os_czasu.size():
			var e = g.D.os_czasu[i]
			var p := _poz(i)
			draw_line(Vector2(p.x, y0), p, Color(0.4, 0.3, 0.2, 0.6), 1)
			var kol := Color("c0303a") if e[4] == "pl" else Color("2c4a8a")
			if e[0] > granica:
				kol = kol.lerp(Color(0.8, 0.78, 0.72), 0.55)
			else:
				draw_circle(p, 11, Color("f0c040"))
			if i == wybrane:
				draw_circle(p, 14, Color(0.1, 0.1, 0.1))
			draw_circle(p, 8, kol)
			var tytul: String = e[2]
			while f.get_string_size(tytul, HORIZONTAL_ALIGNMENT_LEFT, -1, 13).x > 150:
				tytul = tytul.substr(0, tytul.length() - 2) + "…"
			var w := f.get_string_size(tytul, HORIZONTAL_ALIGNMENT_LEFT, -1, 13).x
			draw_string(f, p + Vector2(-w / 2, -14 if p.y < y0 else 26), tytul, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("30200f"))

	func _gui_input(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			var najl := -1
			var dmin := 18.0
			for i in g.D.os_czasu.size():
				var d := _poz(i).distance_to(e.position)
				if d < dmin:
					dmin = d
					najl = i
			if najl >= 0:
				ui.wybierz_wydarzenie(najl)


# ===================================================================== mapa Europy między kampaniami
var mapa_w: Control
var mapa_podpis: Label
var mapa_krok := 0
var mapa_kroki := []


func _ekran_mapy() -> void:
	ekran = _pelny()
	var tlo := ColorRect.new()
	tlo.color = Color("1f2a33")
	tlo.set_anchors_preset(Control.PRESET_FULL_RECT)
	ekran.add_child(tlo)
	var sc = g.D.mapy_podrozy[g.mapa_scen]
	mapa_kroki = []
	for i in sc.trasa.size():
		mapa_kroki.append({"typ": "odcinek", "i": i, "tekst": sc.trasa[i][3]})
	for t in sc.podpisy:
		mapa_kroki.append({"typ": "podpis", "tekst": t})
	mapa_krok = 0
	var m := MapaPodrozy.new()
	m.clip_contents = true
	m.g = g
	m.sc = sc
	m.przejscie = 0.0 if sc.od != sc.do else 1.0
	var prop: float = g.D_mapa.proporcja
	m.position = Vector2((1280 - 560 * prop) / 2, 64)
	m.size = Vector2(560 * prop, 560)
	ekran.add_child(m)
	mapa_w = m
	var rok := _label(sc.rok, 40, C_ZLOTY)
	rok.position = Vector2(30, 6)
	rok.add_theme_color_override("font_outline_color", Color("1c120e"))
	rok.add_theme_constant_override("outline_size", 10)
	ekran.add_child(rok)
	var tyt := _label("Podróż Romana Dmowskiego · mapa Europy", 20, C_JASNY)
	tyt.position = Vector2(30 + rok.get_minimum_size().x + 20, 22)
	ekran.add_child(tyt)
	var panel := PanelContainer.new()
	panel.position = Vector2(140, 630)
	panel.custom_minimum_size = Vector2(1000, 80)
	ekran.add_child(panel)
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 14)
	panel.add_child(hb)
	mapa_podpis = _label("", 19)
	mapa_podpis.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	mapa_podpis.custom_minimum_size.x = 760
	mapa_podpis.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb.add_child(mapa_podpis)
	hb.add_child(_btn("Dalej »", dalej_mapy, "", 18))
	hb.add_child(_btn("Pomiń", func(): g.zakoncz_mape(), "", 15))
	var zr := _label(g.D_mapa.zrodlo, 12, Color(0.7, 0.72, 0.75))
	zr.position = Vector2(m.position.x, m.position.y + m.size.y + 2)
	ekran.add_child(zr)
	_ustaw_krok_mapy()


func _ustaw_krok_mapy() -> void:
	if mapa_krok >= mapa_kroki.size():
		return
	var k = mapa_kroki[mapa_krok]
	mapa_podpis.text = k.tekst
	g.lektor(k.tekst)
	if k.typ == "podpis" and mapa_w.przejscie < 1.0:
		mapa_w.animuj_granice = true


func dalej_mapy() -> void:
	if g.scena != "mapa" or mapa_w == null:
		return
	var k = mapa_kroki[mapa_krok] if mapa_krok < mapa_kroki.size() else null
	if k != null and k.typ == "odcinek" and mapa_w.postep < k.i + 1:
		mapa_w.postep = k.i + 1
	if k != null and k.typ == "podpis" and mapa_w.przejscie < 1.0 and mapa_w.animuj_granice:
		mapa_w.przejscie = 1.0
		return
	mapa_krok += 1
	if mapa_krok >= mapa_kroki.size():
		g.zakoncz_mape()
	else:
		_ustaw_krok_mapy()


func _aktualizuj_mape(dt: float) -> void:
	if g.scena != "mapa" or mapa_w == null or not is_instance_valid(mapa_w):
		return
	if mapa_krok < mapa_kroki.size():
		var k = mapa_kroki[mapa_krok]
		if k.typ == "odcinek":
			mapa_w.postep = min(mapa_w.postep + dt / 2.6, k.i + 1.0)
			# kolejny odcinek tej samej podróży rusza sam
			if mapa_w.postep >= k.i + 1.0 and mapa_krok + 1 < mapa_kroki.size() and mapa_kroki[mapa_krok + 1].typ == "odcinek":
				mapa_krok += 1
				if mapa_kroki[mapa_krok].tekst != k.tekst:
					_ustaw_krok_mapy()
	if mapa_w.animuj_granice and mapa_w.przejscie < 1.0:
		mapa_w.przejscie = min(1.0, mapa_w.przejscie + dt / 3.5)
	mapa_w.queue_redraw()


class MapaPodrozy extends Control:
	var g
	var sc
	var postep := 0.0
	var przejscie := 1.0
	var animuj_granice := false
	var _cache := {}
	const KOLORY := {"German Empire": Color(0.56, 0.62, 0.78), "Austro-Hungarian Empire": Color(0.9, 0.78, 0.42),
		"Russian Empire": Color(0.56, 0.72, 0.5), "Poland": Color(0.88, 0.2, 0.25), "France": Color(0.55, 0.66, 0.9)}

	func _pkt(p) -> Vector2:
		return Vector2(p[0] * size.x, p[1] * size.y)

	func _wielokaty(epoka: String) -> Array:
		var klucz := epoka + str(size)
		if _cache.has(klucz):
			return _cache[klucz]
		var w := []
		for k in g.D_mapa[epoka]:
			for c in k.czesci:
				var pts := PackedVector2Array()
				for p in c:
					pts.append(_pkt(p))
				var ok := Geometry2D.triangulate_polygon(pts).size() > 0
				w.append({"n": k.n, "pts": pts, "ok": ok})
		_cache[klucz] = w
		return w

	func _kolor(n: String) -> Color:
		if n in sc.wyroznij and KOLORY.has(n):
			return KOLORY[n]
		var h := float(n.hash() % 1000) / 1000.0
		return Color(0.86, 0.82, 0.72).lerp(Color(0.78, 0.76, 0.7), h)

	func _rysuj_epoke(epoka: String, alfa: float) -> void:
		for p in _wielokaty(epoka):
			var kol := _kolor(p.n)
			kol.a = alfa
			if p.ok:
				draw_colored_polygon(p.pts, kol)
			var obr := Color(0.25, 0.2, 0.18, 0.7 * alfa)
			draw_polyline(p.pts + PackedVector2Array([p.pts[0]]), obr, 1.2 if p.n != "Poland" else 2.5)

	func _etykiety(epoka: String, alfa: float) -> void:
		var f := ThemeDB.fallback_font
		for k in g.D_mapa[epoka]:
			if k.etykieta == null:
				continue
			var p := _pkt(k.etykieta)
			var wyr: bool = k.n in sc.wyroznij
			var rozm := 20 if wyr else 13
			var w := f.get_string_size(k.pl, HORIZONTAL_ALIGNMENT_LEFT, -1, rozm).x
			var kol := Color(0.15, 0.1, 0.08, alfa) if not wyr else Color(1, 1, 1, alfa)
			if wyr:
				draw_string_outline(f, p - Vector2(w / 2, 0), k.pl, HORIZONTAL_ALIGNMENT_LEFT, -1, rozm, 5, Color(0.1, 0.06, 0.04, alfa))
			draw_string(f, p - Vector2(w / 2, 0), k.pl, HORIZONTAL_ALIGNMENT_LEFT, -1, rozm, kol)

	func _punkt_trasy(t: float) -> Vector2:
		var i := clampi(int(t), 0, sc.trasa.size() - 1)
		var u := clampf(t - i, 0.0, 1.0)
		var a := _pkt(g.D_mapa.miasta[sc.trasa[i][0]])
		var b := _pkt(g.D_mapa.miasta[sc.trasa[i][1]])
		var srodek := (a + b) / 2 + (b - a).orthogonal().normalized() * a.distance_to(b) * 0.12
		return a.lerp(srodek, u).lerp(srodek.lerp(b, u), u)

	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.56, 0.7, 0.82))
		if sc.od == sc.do:
			_rysuj_epoke(sc.od, 1.0)
			_etykiety(sc.od, 1.0)
		else:
			_rysuj_epoke(sc.od, 1.0)
			if przejscie > 0.0:
				_rysuj_epoke(sc.do, przejscie)
			_etykiety(sc.od if przejscie < 0.5 else sc.do, abs(przejscie - 0.5) * 2)
		var f := ThemeDB.fallback_font
		# trasa
		if sc.trasa.size() > 0:
			var krok := 0.02
			var t := 0.0
			while t < postep:
				var p1 := _punkt_trasy(t)
				var p2 := _punkt_trasy(min(t + krok * 0.6, postep))
				draw_line(p1, p2, Color(0.55, 0.12, 0.12), 3)
				t += krok
		# miasta
		for nazwa in sc.miasta:
			var p := _pkt(g.D_mapa.miasta[nazwa])
			draw_circle(p, 6, Color(0.1, 0.08, 0.06))
			draw_circle(p, 4, Color(1, 0.92, 0.6))
			draw_string_outline(f, p + Vector2(8, -6), nazwa, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, 4, Color(1, 1, 1, 0.9))
			draw_string(f, p + Vector2(8, -6), nazwa, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0.1, 0.06, 0.04))
		# pojazd
		if sc.trasa.size() > 0:
			var tt: float = min(postep, sc.trasa.size() - 0.001)
			var poz := _punkt_trasy(tt)
			var dalej := _punkt_trasy(min(tt + 0.02, sc.trasa.size() - 0.0001))
			var kier := 1.0 if dalej.x >= poz.x else -1.0
			var statek: bool = sc.trasa[clampi(int(tt), 0, sc.trasa.size() - 1)][2] == "statek"
			for i in 4:
				var faza := fmod(g.t * 1.5 + i * 0.25, 1.0)
				draw_circle(poz + Vector2(-kier * (6 + faza * 22), -16 - faza * 14), 3 + faza * 5, Color(0.9, 0.9, 0.92, 0.7 * (1.0 - faza)))
			if statek:
				draw_colored_polygon(PackedVector2Array([poz + Vector2(-16, 0), poz + Vector2(16, 0), poz + Vector2(11, 8), poz + Vector2(-11, 8)]), Color(0.2, 0.2, 0.25))
				draw_rect(Rect2(poz + Vector2(-8, -8), Vector2(14, 8)), Color(0.95, 0.95, 0.9))
				draw_rect(Rect2(poz + Vector2(-2, -15), Vector2(5, 8)), Color(0.75, 0.2, 0.2))
			else:
				draw_rect(Rect2(poz + Vector2(-14, -9), Vector2(20, 9)), Color(0.15, 0.15, 0.18))
				draw_rect(Rect2(poz + Vector2(kier * 2 - 2, -15), Vector2(9, 15) * Vector2(1, 1)), Color(0.55, 0.12, 0.12))
				draw_rect(Rect2(poz + Vector2(-kier * 10 - 2, -14), Vector2(4, 6)), Color(0.15, 0.15, 0.18))
				for dx in [-10, -2, 6]:
					draw_circle(poz + Vector2(dx, 1), 3.5, Color(0.1, 0.1, 0.1))
				draw_line(poz + Vector2(-14, 4), poz + Vector2(10, 4), Color(0.8, 0.7, 0.3), 1)
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.9, 0.8, 0.5), false, 3)


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
		var s := 16.0
		var kolory := {".": Color(0.62, 0.72, 0.5), "T": Color(0.42, 0.56, 0.38), "~": Color(0.42, 0.58, 0.78),
			"#": Color(0.6, 0.55, 0.5), "=": Color(0.8, 0.76, 0.68), "B": Color(0.84, 0.8, 0.72),
			"K": Color(0.7, 0.55, 0.45), "D": Color(0.66, 0.4, 0.36), "^": Color(0.6, 0.62, 0.66),
			"P": Color(0.9, 0.8, 0.45), "X": Color(0.55, 0.44, 0.32)}
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.95, 0.88, 0.7))
		for y in g.map_h:
			for x in g.map_w:
				draw_rect(Rect2(x * s, y * s, s, s), kolory.get(g.mapa[y][x], kolory["."]).lerp(Color(0.96, 0.88, 0.7), 0.3))
		for dz in g.R.dzialki:
			var d = g.bud(dz[0])
			var kol := Color(0.16, 0.48, 0.2) if g.dzialka_zajeta(dz[0], dz[1], dz[2]) else Color(0.16, 0.22, 0.5)
			draw_rect(Rect2(dz[1] * s, dz[2] * s, d.w * s, d.h * s), kol)
		var f := ThemeDB.fallback_font
		for k in g.R.npc:
			var p = g.R.npc[k]
			var c := Vector2(p[0] + 0.5, p[1] + 0.5) * s
			draw_circle(c, 5, Color(0.95, 0.75, 0.15))
			draw_string(f, c + Vector2(7, 5), g.D.postacie[k].imie, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color(0.2, 0.12, 0.08))
		var hp: Vector3 = g.bohater.position / g.T * s
		draw_circle(Vector2(hp.x, hp.z), 6, Color(0.9, 0.1, 0.1))
		draw_string(f, Vector2(size.x - 30, 24), "N", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(0.66, 0.12, 0.14))
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.2, 0.12, 0.08), false, 2)
