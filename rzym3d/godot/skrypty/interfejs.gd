extends CanvasLayer
## Interfejs budowany w kodzie: ekrany (tytuł, mapa imperium, wstęp, koniec), HUD rozgrywki,
## okna (technologie, wojsko, Księga Wiedzy, wydarzenia, zagadki) i lobby gry wieloosobowej.

var g  # gra.gd

const C_TEKST := Color("30200f")
const C_CZERW := Color("a8282c")
const C_ZIELONY := Color("2b7a32")
const C_SZARY := Color("6e6258")
const C_JASNY := Color("faf0d2")
const C_ZLOTY := Color("f4c848")
const C_FIOLET := Color("6b3fa0")
const RZYMSKIE := ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

var motyw: Theme
var korzen: Control
var ekran: Control
var hud: Control
var okno: Control
var toasty: VBoxContainer
var rada_panel: PanelContainer
var rada_tekst: Label
var otwarte := ""
var intro_rozdzial := 0
var intro_krok := 0
var _kolejka := []
var _pisze := false

# HUD
var zas_l := {}
var tura_l: Label
var epoka_l: Label
var cele_box: VBoxContainer
var bud_siatka: GridContainer
var info_l: RichTextLabel
var gracze_box: VBoxContainer
var czat_box: VBoxContainer
var czat_l: RichTextLabel
var btn_koniec: Button
var tytul_rozdz: Label


# ===================================================================== podstawy
func zbuduj() -> void:
	layer = 2    # nad interfejsem bitwy (pytanie rady wojennej)
	motyw = _motyw()
	korzen = Control.new()
	korzen.set_anchors_preset(Control.PRESET_FULL_RECT)
	korzen.mouse_filter = Control.MOUSE_FILTER_IGNORE
	korzen.theme = motyw
	add_child(korzen)
	toasty = VBoxContainer.new()
	toasty.mouse_filter = Control.MOUSE_FILTER_IGNORE
	toasty.position = Vector2(20, 60)
	toasty.size = Vector2(700, 10)
	toasty.z_index = 20


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
	var perg := _sb(Color("ecdcb0"), Color("6b2a1c"), 3, 8, 14)
	perg.shadow_size = 8
	perg.shadow_color = Color(0, 0, 0, 0.4)
	th.set_stylebox("panel", "PanelContainer", perg)
	th.set_stylebox("normal", "Button", _sb(Color("b9874f"), Color("4a2414"), 2, 6, 7))
	th.set_stylebox("hover", "Button", _sb(Color("d6a76c"), Color("4a2414"), 2, 6, 7))
	th.set_stylebox("pressed", "Button", _sb(Color("f0c860"), Color("4a2414"), 2, 6, 7))
	th.set_stylebox("disabled", "Button", _sb(Color("aa9e8e"), Color("6a5e54"), 2, 6, 7))
	th.set_stylebox("focus", "Button", StyleBoxEmpty.new())
	for k in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		th.set_color(k, "Button", C_TEKST)
	th.set_color("font_disabled_color", "Button", Color("5e544c"))
	th.set_color("font_color", "Label", C_TEKST)
	th.set_color("default_color", "RichTextLabel", C_TEKST)
	th.set_stylebox("background", "ProgressBar", _sb(Color("1c120e"), Color("1c120e"), 1, 3, 0))
	th.set_stylebox("fill", "ProgressBar", _sb(C_ZLOTY, C_ZLOTY, 0, 3, 0))
	th.set_stylebox("normal", "LineEdit", _sb(Color("fff6dc"), Color("6b2a1c"), 2, 4, 6))
	th.set_stylebox("focus", "LineEdit", _sb(Color("fffbe9"), Color("c0392b"), 2, 4, 6))
	th.set_color("font_color", "LineEdit", C_TEKST)
	th.set_stylebox("panel", "TabContainer", _sb(Color("ecdcb0"), Color("6b2a1c"), 0, 0, 8))
	th.set_color("font_selected_color", "TabContainer", C_CZERW)
	th.set_color("font_unselected_color", "TabContainer", C_TEKST)
	th.set_stylebox("tab_selected", "TabContainer", _sb(Color("ecdcb0"), Color("6b2a1c"), 2, 4, 6))
	th.set_stylebox("tab_unselected", "TabContainer", _sb(Color("c9b083"), Color("6b2a1c"), 1, 4, 6))
	th.set_stylebox("tab_hovered", "TabContainer", _sb(Color("dcc596"), Color("6b2a1c"), 1, 4, 6))
	return th


func _label(tekst: String, rozmiar := 17, kolor := C_TEKST) -> Label:
	var l := Label.new()
	l.text = tekst
	l.add_theme_font_size_override("font_size", rozmiar)
	l.add_theme_color_override("font_color", kolor)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _zawin(l: Label, szer: float) -> Label:
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size.x = szer
	return l


func _btn(tekst: String, akcja: Callable, ikona := "", rozmiar := 17) -> Button:
	var b := Button.new()
	b.text = tekst
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_font_size_override("font_size", rozmiar)
	if ikona != "" and ResourceLoader.exists("res://ui/%s.png" % ikona):
		b.icon = load("res://ui/%s.png" % ikona)
		b.expand_icon = true
		b.add_theme_constant_override("icon_max_width", 40)
	b.pressed.connect(func():
		g.dzwiek("klik")
		akcja.call())
	return b


func _obraz(sciezka: String, rozmiar: Vector2) -> Control:
	var t := TextureRect.new()
	if ResourceLoader.exists(sciezka):
		t.texture = load(sciezka)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.custom_minimum_size = rozmiar
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t


func _portret(id: String, rozmiar := 96) -> Control:
	var pc := PanelContainer.new()
	pc.add_theme_stylebox_override("panel", _sb(Color("3b2418"), C_ZLOTY, 2, 48, 2))
	pc.add_child(_obraz("res://ui/portret_%s.png" % id, Vector2(rozmiar, rozmiar)))
	return pc


func _pelny(kolor := Color("1d1411")) -> Control:
	var c := Control.new()
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	var tlo := ColorRect.new()
	tlo.color = kolor
	tlo.set_anchors_preset(Control.PRESET_FULL_RECT)
	c.add_child(tlo)
	korzen.add_child(c)
	return c


func _tlo_obraz(c: Control, sciezka: String, przyciemnienie := 0.35) -> void:
	if ResourceLoader.exists(sciezka):
		var t := TextureRect.new()
		t.texture = load(sciezka)
		t.set_anchors_preset(Control.PRESET_FULL_RECT)
		t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		c.add_child(t)
	var cien := ColorRect.new()
	cien.color = Color(0, 0, 0, przyciemnienie)
	cien.set_anchors_preset(Control.PRESET_FULL_RECT)
	c.add_child(cien)


func _cien_tekstu(l: Label, grub := 8) -> Label:
	l.add_theme_constant_override("outline_size", grub)
	l.add_theme_color_override("font_outline_color", Color(0.1, 0.05, 0.03))
	return l


func pisze() -> bool:
	var f := korzen.get_viewport().gui_get_focus_owner()
	return f is LineEdit


func toast(tekst: String) -> void:
	if toasty.get_parent() == null:
		korzen.add_child(toasty)
	var pc := PanelContainer.new()
	pc.add_theme_stylebox_override("panel", _sb(Color(0.12, 0.07, 0.05, 0.9), C_ZLOTY, 1, 6, 8))
	pc.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var l := _label(tekst, 16, C_JASNY)
	_zawin(l, 520)
	pc.add_child(l)
	toasty.add_child(pc)
	korzen.move_child(toasty, -1)
	var tw := create_tween()
	tw.tween_interval(3.2)
	tw.tween_property(pc, "modulate:a", 0.0, 0.6)
	tw.tween_callback(pc.queue_free)


# ===================================================================== ekrany
func pokaz_ekran() -> void:
	for c in korzen.get_children():
		if c != toasty:
			c.queue_free()
	ekran = null
	hud = null
	okno = null
	otwarte = ""
	rada_panel = null
	match g.scena:
		"tytul": _ekran_tytul()
		"mapa": _ekran_mapy()
		"intro": _ekran_intro()
		"gra": _zbuduj_hud()
		"bitwa": pass
		"koniec": _ekran_koniec_rozdzialu()
		"koniec_mp": _zbuduj_hud(); _ekran_koniec_mp()
		"final": _ekran_final()
		"porazka": _zbuduj_hud(); _ekran_porazki()
		"lobby": _ekran_lobby()
		"przekazanie": _zbuduj_hud(); _ekran_przekazania()
	if toasty.get_parent() == null:
		korzen.add_child(toasty)
	korzen.move_child(toasty, -1)


func _ekran_tytul() -> void:
	ekran = _pelny()
	_tlo_obraz(ekran, "res://ui/tlo_tytul.png", 0.25)
	var vb := VBoxContainer.new()
	vb.position = Vector2(70, 60)
	vb.add_theme_constant_override("separation", 6)
	ekran.add_child(vb)
	vb.add_child(_cien_tekstu(_label("KRONIKI DAMIANA ŚCISŁA · CZĘŚĆ III", 18, Color(0.85, 0.7, 1.0))))
	vb.add_child(_cien_tekstu(_label("ROMAN EMPIRE", 64, C_ZLOTY), 14))
	vb.add_child(_cien_tekstu(_label("od narodzin przez rozkwit aż po upadek", 26, C_JASNY), 10))
	vb.add_child(_cien_tekstu(_label("753 p.n.e. – 476 n.e. · %d rozdziałów · strategia turowa 3D" % g.D.rozdzialy.size(), 17, C_JASNY)))
	var sp := Control.new()
	sp.custom_minimum_size = Vector2(0, 22)
	vb.add_child(sp)
	var przyciski := VBoxContainer.new()
	przyciski.add_theme_constant_override("separation", 8)
	przyciski.custom_minimum_size = Vector2(380, 0)
	vb.add_child(przyciski)
	if g.ma_zapis():
		przyciski.add_child(_btn("Kontynuuj grę", func(): g.wczytaj(), "", 20))
	przyciski.add_child(_btn("Nowa kampania (1 gracz)", func(): _okno_trudnosci(), "", 20))
	przyciski.add_child(_btn("Wybór rozdziału", func(): _okno_rozdzialow(), "", 20))
	przyciski.add_child(_btn("Gra wieloosobowa – jeden komputer", func(): _okno_hotseat(), "", 20))
	przyciski.add_child(_btn("Gra wieloosobowa – online", func():
		g.scena = "lobby"
		pokaz_ekran(), "", 20))
	przyciski.add_child(_btn("Księga Wiedzy", func(): przelacz_okno("ksiega"), "", 20))
	if not OS.has_feature("web"):
		przyciski.add_child(_btn("Wyjście", func(): g.get_tree().quit(), "", 18))
	var st := _cien_tekstu(_label("Muzyka: M · Lektor: G · Pełny ekran: F11", 14, C_JASNY))
	st.position = Vector2(70, 680)
	ekran.add_child(st)
	var dam := _portret("damian", 120)
	dam.position = Vector2(1100, 520)
	ekran.add_child(dam)


func _okno_trudnosci() -> void:
	var vb := _okno("Nowa kampania", Vector2(700, 520))
	vb.add_child(_zawin(_label("Poprowadź Rzym przez 12 wieków – od chat na Palatynie po upadek Zachodu. Wybierz poziom trudności:", 17), 660))
	for i in g.D.trudnosci.size():
		var tr: Dictionary = g.D.trudnosci[i]
		vb.add_child(_btn(tr.nazwa, func():
			zamknij_okno()
			g.nowa_kampania(i), "", 19))
		vb.add_child(_zawin(_label(tr.get("opis", ""), 14, C_CZERW if i >= 2 else C_SZARY), 660))


func _okno_rozdzialow() -> void:
	var vb := _okno("Wybór rozdziału", Vector2(900, 560))
	var siatka := GridContainer.new()
	siatka.columns = 2
	siatka.add_theme_constant_override("h_separation", 10)
	siatka.add_theme_constant_override("v_separation", 8)
	vb.add_child(siatka)
	var dost: int = g.K.ukonczone.size()
	for i in g.D.rozdzialy.size():
		var r: Dictionary = g.D.rozdzialy[i]
		var wyn: Dictionary = g.K.wyniki.get(r.id, {})
		var txt := "%s. %s\n%s · %s" % [RZYMSKIE[i + 1], r.tytul, r.lata, g.D.epoki[r.epoka].nazwa]
		if not wyn.is_empty():
			txt += " · %d gw., chwała %d" % [int(wyn.gwiazdki), int(wyn.chwala)]
		var b := _btn(txt, func():
			zamknij_okno()
			g.przejdz_do_rozdzialu(i), "", 15)
		b.custom_minimum_size = Vector2(420, 58)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.disabled = i > dost and not otwarte_wszystkie
		siatka.add_child(b)
	var hb := HBoxContainer.new()
	vb.add_child(hb)
	var cb := CheckBox.new()
	cb.text = "Tryb nauczyciela: odblokuj wszystkie rozdziały"
	cb.button_pressed = otwarte_wszystkie
	cb.add_theme_color_override("font_color", C_TEKST)
	cb.toggled.connect(func(v):
		otwarte_wszystkie = v
		zamknij_okno()
		_okno_rozdzialow())
	hb.add_child(cb)


var otwarte_wszystkie := false


func _okno_hotseat() -> void:
	var vb := _okno("Gra wieloosobowa przy jednym komputerze", Vector2(760, 560))
	vb.add_child(_zawin(_label("2–4 graczy, każdy prowadzi swój ród. Gracze grają po kolei (przekazując mysz). Wygrywa ród z największą chwałą – zwycięstwo w bitwie rozdziału daje dużą premię i kończy grę po tej rundzie.", 15), 720))
	var pola := []
	var siatka := GridContainer.new()
	siatka.columns = 3
	siatka.add_theme_constant_override("h_separation", 10)
	vb.add_child(siatka)
	var domyslne := ["Ala", "Kuba", "Ola", "Staś"]
	for i in 4:
		var kol := ColorRect.new()
		kol.color = Color(g.D.rody[i].kolor)
		kol.custom_minimum_size = Vector2(24, 24)
		siatka.add_child(kol)
		var le := LineEdit.new()
		le.text = domyslne[i]
		le.custom_minimum_size = Vector2(220, 0)
		le.max_length = 16
		siatka.add_child(le)
		var cb := CheckBox.new()
		cb.text = "ród %s – gra" % g.D.rody[i].nazwa
		cb.button_pressed = i < 2
		cb.add_theme_color_override("font_color", C_TEKST)
		siatka.add_child(cb)
		pola.append([le, cb])
	vb.add_child(_label("Rozdział:", 16))
	var wybor := OptionButton.new()
	for i in g.D.rozdzialy.size():
		var r: Dictionary = g.D.rozdzialy[i]
		wybor.add_item("%s. %s (%s)" % [RZYMSKIE[i + 1], r.tytul, r.lata])
	vb.add_child(wybor)
	var trud := OptionButton.new()
	for tr in g.D.trudnosci:
		trud.add_item(tr.nazwa)
	trud.selected = 1
	vb.add_child(trud)
	vb.add_child(_btn("Rozpocznij grę", func():
		var gracze := []
		for i in 4:
			if pola[i][1].button_pressed:
				gracze.append({"imie": pola[i][0].text.strip_edges() if pola[i][0].text.strip_edges() != "" else "Gracz %d" % (i + 1), "rod": i})
		if gracze.size() < 2:
			toast("Zaznacz co najmniej 2 graczy")
			return
		zamknij_okno()
		g.moj_gracz = -1
		g.rozpocznij_rozdzial(wybor.selected, gracze, "hotseat", trud.selected), "", 20))


# ----------------------------------------------------------------- mapa imperium
var mapa_w: Control
var mapa_podpis: Label
var mapa_kroki := []
var mapa_krok := 0


func _ekran_mapy() -> void:
	ekran = _pelny(Color("1b2530"))
	var r: Dictionary = g.D.rozdzialy[g.mapa_rozdzial]
	var sc: Dictionary = r.mapa_imperium
	mapa_kroki = []
	for i in sc.trasa.size():
		mapa_kroki.append({"typ": "odcinek", "i": i, "tekst": sc.trasa[i][3]})
	for tx in sc.podpisy:
		mapa_kroki.append({"typ": "podpis", "tekst": tx})
	mapa_krok = 0
	var m := MapaImperium.new()
	m.clip_contents = true
	m.g = g
	m.sc = sc
	m.przejscie = 0.0 if sc.od != sc.do else 1.0
	var prop: float = g.M.proporcja
	var h := 548.0
	m.position = Vector2((1280 - h * prop) / 2, 62)
	m.size = Vector2(h * prop, h)
	ekran.add_child(m)
	mapa_w = m
	var rok := _cien_tekstu(_label(sc.rok, 36, C_ZLOTY), 10)
	rok.position = Vector2(24, 8)
	ekran.add_child(rok)
	var tyt := _label("Rozdział %s · %s · mapa świata rzymskiego" % [RZYMSKIE[g.mapa_rozdzial + 1], r.tytul], 19, C_JASNY)
	tyt.position = Vector2(30 + rok.get_minimum_size().x + 20, 20)
	ekran.add_child(tyt)
	var leg := HBoxContainer.new()
	leg.position = Vector2(m.position.x, m.position.y + h + 18)
	ekran.add_child(leg)
	var zr := _label(g.M.zrodlo, 12, Color(0.7, 0.72, 0.75))
	zr.position = Vector2(m.position.x, m.position.y + h + 2)
	ekran.add_child(zr)
	var panel := PanelContainer.new()
	panel.position = Vector2(140, 634)
	panel.custom_minimum_size = Vector2(1000, 76)
	ekran.add_child(panel)
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 14)
	panel.add_child(hb)
	hb.add_child(_portret("damian", 52))
	mapa_podpis = _label("", 18)
	mapa_podpis.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	mapa_podpis.custom_minimum_size.x = 700
	mapa_podpis.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb.add_child(mapa_podpis)
	hb.add_child(_btn("Dalej »", dalej_mapy, "", 18))
	hb.add_child(_btn("Pomiń", func(): g.zakoncz_mape(), "", 15))
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
		return
	if k != null and k.typ == "podpis" and mapa_w.przejscie < 1.0 and mapa_w.animuj_granice:
		mapa_w.przejscie = 1.0
		return
	mapa_krok += 1
	if mapa_krok >= mapa_kroki.size():
		g.zakoncz_mape()
	else:
		_ustaw_krok_mapy()


func _process(dt: float) -> void:
	if g == null:
		return
	if g.scena == "mapa" and is_instance_valid(mapa_w):
		if mapa_krok < mapa_kroki.size():
			var k = mapa_kroki[mapa_krok]
			if k.typ == "odcinek":
				mapa_w.postep = min(mapa_w.postep + dt / 2.8, k.i + 1.0)
		if mapa_w.animuj_granice and mapa_w.przejscie < 1.0:
			mapa_w.przejscie = min(1.0, mapa_w.przejscie + dt / 3.0)
		mapa_w.queue_redraw()
	if g.siec and g.siec.bledy.size() > 0 and g.tryb == "":
		for b in g.siec.bledy:
			toast(b)
		g.siec.bledy.clear()


class MapaImperium extends Control:
	var g
	var sc
	var postep := 0.0
	var przejscie := 1.0
	var animuj_granice := false
	var _cache := {}

	func _pkt(p) -> Vector2:
		return Vector2(p[0] * size.x, p[1] * size.y)

	func _wielokaty(epoka: String) -> Array:
		var klucz := epoka + str(size)
		if _cache.has(klucz):
			return _cache[klucz]
		var w := []
		for k in g.M.epoki[epoka]:
			for c in k.czesci:
				var pts := PackedVector2Array()
				for p in c:
					pts.append(_pkt(p))
				var ok := Geometry2D.triangulate_polygon(pts).size() > 0
				w.append({"n": k.n, "pts": pts, "ok": ok, "rzym": int(k.rzym)})
		_cache[klucz] = w
		return w

	func _kolor(n: String, rzym: int) -> Color:
		if rzym == 1:
			return Color(0.78, 0.2, 0.18)
		if rzym == 2:
			return Color(0.55, 0.3, 0.62)
		if n == "":
			return Color(0.84, 0.8, 0.68)
		var h := float(absi(n.hash()) % 1000) / 1000.0
		return Color(0.86, 0.8, 0.64).lerp(Color(0.72, 0.74, 0.6), h)

	func _rysuj_epoke(epoka: String, alfa: float) -> void:
		for p in _wielokaty(epoka):
			var kol := _kolor(p.n, p.rzym)
			kol.a = alfa
			if p.ok:
				draw_colored_polygon(p.pts, kol)
			var obr := Color(0.25, 0.2, 0.18, 0.6 * alfa)
			draw_polyline(p.pts + PackedVector2Array([p.pts[0]]), obr, 2.0 if p.rzym > 0 else 1.0)

	func _etykiety(epoka: String, alfa: float) -> void:
		var f := ThemeDB.fallback_font
		for k in g.M.epoki[epoka]:
			if k.etykieta == null:
				continue
			var p := _pkt(k.etykieta)
			var wyr: bool = int(k.rzym) > 0
			var rozm := 19 if wyr else 12
			var w := f.get_string_size(k.pl, HORIZONTAL_ALIGNMENT_LEFT, -1, rozm).x
			if wyr:
				draw_string_outline(f, p - Vector2(w / 2, 0), k.pl, HORIZONTAL_ALIGNMENT_LEFT, -1, rozm, 5, Color(0.1, 0.05, 0.03, alfa))
				draw_string(f, p - Vector2(w / 2, 0), k.pl, HORIZONTAL_ALIGNMENT_LEFT, -1, rozm, Color(1, 0.95, 0.85, alfa))
			else:
				draw_string(f, p - Vector2(w / 2, 0), k.pl, HORIZONTAL_ALIGNMENT_LEFT, -1, rozm, Color(0.25, 0.18, 0.12, alfa * 0.85))

	func _punkt(t: float) -> Vector2:
		var i := clampi(int(t), 0, sc.trasa.size() - 1)
		var u := clampf(t - i, 0.0, 1.0)
		var a := _pkt(g.M.miasta[sc.trasa[i][0]])
		var b := _pkt(g.M.miasta[sc.trasa[i][1]])
		var sr := (a + b) / 2 + (b - a).orthogonal().normalized() * a.distance_to(b) * 0.15
		return a.lerp(sr, u).lerp(sr.lerp(b, u), u)

	func _draw() -> void:
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.42, 0.6, 0.74))
		if sc.od == sc.do:
			_rysuj_epoke(sc.od, 1.0)
			_etykiety(sc.od, 1.0)
		else:
			_rysuj_epoke(sc.od, 1.0)
			if przejscie > 0.0:
				_rysuj_epoke(sc.do, przejscie)
			_etykiety(sc.od if przejscie < 0.5 else sc.do, abs(przejscie - 0.5) * 2)
		var f := ThemeDB.fallback_font
		if sc.trasa.size() > 0:
			var t := 0.0
			while t < postep:
				var p1 := _punkt(t)
				var p2 := _punkt(min(t + 0.012, postep))
				var morzem: bool = sc.trasa[clampi(int(t), 0, sc.trasa.size() - 1)][2] == "morzem"
				draw_line(p1, p2, Color(0.15, 0.2, 0.45) if morzem else Color(0.55, 0.08, 0.08), 3)
				t += 0.02
		for nazwa in sc.miasta:
			if not g.M.miasta.has(nazwa):
				continue
			var p := _pkt(g.M.miasta[nazwa])
			var rzym: bool = nazwa == "Rzym"
			draw_circle(p, 8.0 if rzym else 5.5, Color(0.1, 0.06, 0.04))
			draw_circle(p, 6.0 if rzym else 3.8, C_ZLOTY_M if rzym else Color(1, 0.95, 0.75))
			var rz := 17 if rzym else 14
			draw_string_outline(f, p + Vector2(8, -6), nazwa, HORIZONTAL_ALIGNMENT_LEFT, -1, rz, 4, Color(1, 1, 1, 0.85))
			draw_string(f, p + Vector2(8, -6), nazwa, HORIZONTAL_ALIGNMENT_LEFT, -1, rz, Color(0.12, 0.06, 0.04))
		if sc.trasa.size() > 0:
			var tt: float = min(postep, sc.trasa.size() - 0.001)
			var poz := _punkt(tt)
			var morzem: bool = sc.trasa[clampi(int(tt), 0, sc.trasa.size() - 1)][2] == "morzem"
			if morzem:
				# galera: kadłub, żagiel, wiosła
				draw_colored_polygon(PackedVector2Array([poz + Vector2(-16, 0), poz + Vector2(18, 0), poz + Vector2(12, 7), poz + Vector2(-12, 7)]), Color(0.45, 0.28, 0.15))
				draw_line(poz + Vector2(0, 0), poz + Vector2(0, -20), Color(0.3, 0.2, 0.1), 2)
				draw_colored_polygon(PackedVector2Array([poz + Vector2(-9, -18), poz + Vector2(9, -18), poz + Vector2(8, -4), poz + Vector2(-8, -4)]), Color(0.9, 0.3, 0.2))
				for k in 5:
					var x := -10 + k * 5
					draw_line(poz + Vector2(x, 6), poz + Vector2(x - 3 + sin(g.t * 6 + k) * 2, 12), Color(0.3, 0.2, 0.1), 1)
			else:
				# orzeł legionowy na drzewcu
				draw_line(poz + Vector2(0, 10), poz + Vector2(0, -18), Color(0.35, 0.2, 0.1), 3)
				draw_rect(Rect2(poz + Vector2(-8, -12), Vector2(16, 12)), Color(0.75, 0.12, 0.1))
				draw_colored_polygon(PackedVector2Array([poz + Vector2(-10, -22), poz + Vector2(0, -18), poz + Vector2(10, -22), poz + Vector2(0, -26)]), Color(0.95, 0.78, 0.25))
		draw_rect(Rect2(Vector2.ZERO, size), Color(0.9, 0.75, 0.4), false, 3)

	const C_ZLOTY_M := Color(0.95, 0.78, 0.25)


# ----------------------------------------------------------------- wstęp rozdziału
func _ekran_intro() -> void:
	ekran = _pelny()
	_tlo_obraz(ekran, "res://ui/tlo_tytul.png", 0.55)
	var r: Dictionary = g.D.rozdzialy[intro_rozdzial]
	intro_krok = 0
	var panel := PanelContainer.new()
	panel.position = Vector2(160, 90)
	panel.custom_minimum_size = Vector2(960, 520)
	ekran.add_child(panel)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 12)
	panel.add_child(vb)
	vb.add_child(_label("Rozdział %s · %s · %s" % [RZYMSKIE[intro_rozdzial + 1], r.lata, g.D.epoki[r.epoka].nazwa], 18, C_CZERW))
	vb.add_child(_label(r.tytul, 40, C_TEKST))
	vb.add_child(_label(r.miejsce, 17, C_SZARY))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 18)
	vb.add_child(hb)
	var lewa := VBoxContainer.new()
	lewa.add_child(_portret("damian", 150))
	lewa.add_child(_label("Damian, kronikarz", 15, C_FIOLET))
	hb.add_child(lewa)
	var tekst := _label("", 20)
	_zawin(tekst, 740)
	tekst.name = "tekst"
	hb.add_child(tekst)
	var cele := VBoxContainer.new()
	vb.add_child(cele)
	cele.add_child(_label("Zadania kroniki:", 16, C_CZERW))
	var lista := []
	for c in r.cele:
		if c.typ == "bitwa":
			lista.append("Bitwa: " + r.bitwa.nazwa)
		elif c.has("opis"):
			lista.append(c.opis)
		elif c.typ == "buduj":
			lista.append("%s × %d" % [g.D.budynki[c.co].nazwa, int(c.ile)])
		elif c.typ == "tech":
			lista.append("odkryj: " + g.D.technologie[c.co].nazwa)
	cele.add_child(_zawin(_label(" · ".join(lista), 15), 900))
	var dol := HBoxContainer.new()
	dol.alignment = BoxContainer.ALIGNMENT_END
	vb.add_child(dol)
	var b := _btn("Dalej »", func(): _intro_dalej(tekst), "", 20)
	dol.add_child(b)
	_intro_pokaz(tekst)


func _intro_pokaz(tekst: Label) -> void:
	var r: Dictionary = g.D.rozdzialy[intro_rozdzial]
	tekst.text = r.wstep[intro_krok]
	tekst.visible_ratio = 0.0
	var tw := create_tween()
	tw.tween_property(tekst, "visible_ratio", 1.0, 1.4)
	g.lektor(r.wstep[intro_krok])


func _intro_dalej(tekst: Label) -> void:
	var r: Dictionary = g.D.rozdzialy[intro_rozdzial]
	if tekst.visible_ratio < 1.0:
		tekst.visible_ratio = 1.0
		return
	intro_krok += 1
	if intro_krok >= r.wstep.size():
		g.ucisz_lektora()
		g.zacznij_po_intro(intro_rozdzial)
	else:
		_intro_pokaz(tekst)


# ===================================================================== HUD
func _zbuduj_hud() -> void:
	hud = Control.new()
	hud.set_anchors_preset(Control.PRESET_FULL_RECT)
	hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	korzen.add_child(hud)
	var ciemny := _sb(Color(0.16, 0.08, 0.06, 0.94), C_ZLOTY, 0, 0, 6)
	ciemny.border_width_bottom = 2
	var gora := PanelContainer.new()
	gora.add_theme_stylebox_override("panel", ciemny)
	gora.set_anchors_preset(Control.PRESET_TOP_WIDE)
	gora.custom_minimum_size = Vector2(0, 44)
	hud.add_child(gora)
	var gb := HBoxContainer.new()
	gb.add_theme_constant_override("separation", 18)
	gora.add_child(gb)
	zas_l = {}
	for z in ["zboze", "drewno", "kamien", "denary"]:
		var hb := HBoxContainer.new()
		hb.add_theme_constant_override("separation", 5)
		var ik := ZnakZasobu.new()
		ik.rodzaj = z
		ik.custom_minimum_size = Vector2(22, 22)
		ik.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		hb.add_child(ik)
		var l := _label("", 18, C_JASNY)
		hb.add_child(l)
		hb.tooltip_text = g.D.zasoby[z].nazwa
		hb.mouse_filter = Control.MOUSE_FILTER_PASS
		zas_l[z] = l
		gb.add_child(hb)
	for z in ["mieszkancy", "chwala"]:
		var l := _label("", 18, C_JASNY if z == "mieszkancy" else C_ZLOTY)
		zas_l[z] = l
		gb.add_child(l)
	var sp := Control.new()
	sp.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	gb.add_child(sp)
	tura_l = _label("", 18, C_ZLOTY)
	gb.add_child(tura_l)
	epoka_l = _label("", 16, C_JASNY)
	gb.add_child(epoka_l)
	# prawy panel
	var prawy := PanelContainer.new()
	prawy.add_theme_stylebox_override("panel", _sb(Color("ecdcb0"), Color("6b2a1c"), 3, 0, 10))
	prawy.position = Vector2(970, 44)
	prawy.size = Vector2(310, 676)
	prawy.anchor_left = 1.0
	prawy.anchor_right = 1.0
	prawy.anchor_bottom = 1.0
	prawy.offset_left = -310
	prawy.offset_right = 0
	prawy.offset_top = 44
	prawy.offset_bottom = 0
	hud.add_child(prawy)
	var sc := ScrollContainer.new()
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	prawy.add_child(sc)
	var pv := VBoxContainer.new()
	pv.custom_minimum_size = Vector2(284, 0)
	pv.add_theme_constant_override("separation", 6)
	sc.add_child(pv)
	tytul_rozdz = _label("", 19, C_CZERW)
	_zawin(tytul_rozdz, 280)
	pv.add_child(tytul_rozdz)
	gracze_box = VBoxContainer.new()
	pv.add_child(gracze_box)
	pv.add_child(_label("Zadania kroniki", 16, C_TEKST))
	cele_box = VBoxContainer.new()
	cele_box.add_theme_constant_override("separation", 2)
	pv.add_child(cele_box)
	pv.add_child(HSeparator.new())
	pv.add_child(_label("Budowa (kliknij, potem pole na mapie)", 14, C_SZARY))
	bud_siatka = GridContainer.new()
	bud_siatka.columns = 5
	bud_siatka.add_theme_constant_override("h_separation", 4)
	bud_siatka.add_theme_constant_override("v_separation", 4)
	pv.add_child(bud_siatka)
	info_l = RichTextLabel.new()
	info_l.bbcode_enabled = true
	info_l.fit_content = true
	info_l.custom_minimum_size = Vector2(280, 80)
	info_l.add_theme_font_size_override("normal_font_size", 14)
	info_l.add_theme_font_size_override("bold_font_size", 15)
	pv.add_child(info_l)
	czat_box = VBoxContainer.new()
	pv.add_child(czat_box)
	# dolny pasek
	var dol := HBoxContainer.new()
	dol.position = Vector2(10, 670)
	dol.add_theme_constant_override("separation", 6)
	hud.add_child(dol)
	dol.add_child(_btn("Technologie (T)", func(): przelacz_okno("technologie"), "", 16))
	dol.add_child(_btn("Wojsko (K)", func(): przelacz_okno("wojsko"), "", 16))
	dol.add_child(_btn("Księga (L)", func(): przelacz_okno("ksiega"), "", 16))
	dol.add_child(_btn("Pomoc (H)", func(): przelacz_okno("pomoc"), "", 16))
	dol.add_child(_btn("Menu", func(): przelacz_okno("menu"), "", 16))
	btn_koniec = _btn("Koniec tury »", klik_koniec_tury, "", 19)
	btn_koniec.add_theme_stylebox_override("normal", _sb(Color("4f7a35"), Color("1f3a12"), 2, 6, 8))
	btn_koniec.add_theme_stylebox_override("hover", _sb(Color("679a46"), Color("1f3a12"), 2, 6, 8))
	btn_koniec.add_theme_color_override("font_color", C_JASNY)
	btn_koniec.add_theme_color_override("font_hover_color", C_JASNY)
	dol.add_child(btn_koniec)
	# rada kronikarza
	rada_panel = PanelContainer.new()
	rada_panel.add_theme_stylebox_override("panel", _sb(Color(0.16, 0.08, 0.12, 0.9), Color("9b6fd0"), 2, 8, 8))
	rada_panel.position = Vector2(10, 590)
	rada_panel.visible = false
	hud.add_child(rada_panel)
	var rh := HBoxContainer.new()
	rh.add_theme_constant_override("separation", 8)
	rada_panel.add_child(rh)
	rh.add_child(_obraz("res://ui/portret_damian.png", Vector2(56, 56)))
	rada_tekst = _label("", 16, C_JASNY)
	_zawin(rada_tekst, 560)
	rh.add_child(rada_tekst)
	odswiez()


func odswiez() -> void:
	if hud == null or not is_instance_valid(hud) or g.S.is_empty():
		return
	var p: int = g.S.aktywny
	var pokaz: int = p if g.moj_gracz < 0 else g.moj_gracz
	var gr: Dictionary = g.gr(pokaz)
	var w: Dictionary = g.produkcja(pokaz)
	for z in ["zboze", "drewno", "kamien", "denary"]:
		var netto: int = int(w[z]) - (int(w.jedzenie) if z == "zboze" else 0)
		zas_l[z].text = "%d (%s%d)" % [int(gr.zasoby[z]), "+" if netto >= 0 else "", netto]
		zas_l[z].add_theme_color_override("font_color", C_JASNY if netto >= 0 else Color("ff8a70"))
	zas_l.mieszkancy.text = "Mieszkańcy %d/%d" % [int(w.mieszkancy), int(w.prac)]
	zas_l.mieszkancy.add_theme_color_override("font_color", C_JASNY if w.eff >= 1.0 else Color("ff8a70"))
	zas_l.chwala.text = "Chwała %d" % int(gr.chwala)
	tura_l.text = "Tura %d/%d" % [int(g.S.tura), int(g.R.tury)]
	var lim: int = g.limit_tur()
	if lim > 0:
		tura_l.text += " · limit %d" % lim
		tura_l.add_theme_color_override("font_color", Color("ff8a70") if int(g.S.tura) > lim - 4 else C_ZLOTY)
	epoka_l.text = "%s · %s" % [g.D.epoki[g.R.epoka].nazwa, g.R.lata]
	tytul_rozdz.text = "%s. %s" % [RZYMSKIE[int(g.S.rozdzial) + 1], g.R.tytul]
	if gr.inflacja > 0:
		epoka_l.text += " · inflacja ×%.1f" % g.mnoznik_inflacji(pokaz)
	# gracze
	for c in gracze_box.get_children():
		c.queue_free()
	if g.S.gracze.size() > 1:
		for i in g.S.gracze.size():
			var gi: Dictionary = g.S.gracze[i]
			var hb := HBoxContainer.new()
			var kol := ColorRect.new()
			kol.color = Color(g.D.rody[int(gi.rod)].kolor)
			kol.custom_minimum_size = Vector2(16, 16)
			kol.size_flags_vertical = Control.SIZE_SHRINK_CENTER
			hb.add_child(kol)
			var txt := "%s%s (%s) – chwała %d" % ["» " if i == p else "", gi.imie, g.D.rody[int(gi.rod)].nazwa, int(gi.chwala)]
			if gi.get("odlaczony", false):
				txt += " [rozłączony]"
			if i == g.moj_gracz:
				txt += " – Ty"
			hb.add_child(_label(txt, 14, C_CZERW if i == p else C_TEKST))
			gracze_box.add_child(hb)
	# cele
	for c in cele_box.get_children():
		c.queue_free()
	for c in g.R.cele:
		var st: Array = g.stan_celu(pokaz, c)
		var hb := HBoxContainer.new()
		var zn := _label("[x]" if st[0] else "[  ]", 14, C_ZIELONY if st[0] else C_SZARY)
		zn.custom_minimum_size.x = 26
		hb.add_child(zn)
		var l := _label(st[1], 14, C_ZIELONY if st[0] else C_TEKST)
		_zawin(l, 250 if c.typ != "bitwa" else 170)
		hb.add_child(l)
		if c.typ == "bitwa" and not st[0]:
			var mb: Array = g.mozna_bitwe(pokaz)
			var b := _btn("Do boju!", func(): _start_bitwy(), "", 14)
			b.disabled = not mb[0] or not g.moja_tura()
			b.tooltip_text = mb[1]
			hb.add_child(b)
		cele_box.add_child(hb)
	# budynki
	for c in bud_siatka.get_children():
		c.queue_free()
	for typ in g.lista_budynkow():
		var d: Dictionary = g.D.budynki[typ]
		var b := Button.new()
		b.focus_mode = Control.FOCUS_NONE
		b.custom_minimum_size = Vector2(52, 52)
		var ik := "res://ui/budynek_%s.png" % typ
		if ResourceLoader.exists(ik):
			b.icon = load(ik)
			b.expand_icon = true
		else:
			b.text = d.nazwa.left(3)
		var dost: Array = g.dostepny_budynek(pokaz, typ)
		var stac: bool = g.stac(pokaz, g.koszt_budynku(pokaz, typ))
		b.disabled = not dost[0] or not g.moja_tura()
		if not stac and dost[0]:
			b.modulate = Color(1, 0.75, 0.7)
		if g.wybrany == typ:
			b.add_theme_stylebox_override("normal", _sb(Color("f0c860"), Color("a8282c"), 3, 6, 4))
		b.tooltip_text = "%s – %s\nKoszt: %s%s" % [d.nazwa, d.opis, g.koszt_tekst(g.koszt_budynku(pokaz, typ)), ("\n" + dost[1]) if not dost[0] else ""]
		b.pressed.connect(func(): g.wybierz_budynek(typ); odswiez())
		b.mouse_entered.connect(func(): _info_typu(typ))
		bud_siatka.add_child(b)
	btn_koniec.disabled = not g.moja_tura()
	btn_koniec.text = "Koniec tury »" if g.moja_tura() else "Tura: %s" % g.gr(p).imie
	odswiez_czat()


func _info_typu(typ: String) -> void:
	var p: int = g.S.aktywny if g.moj_gracz < 0 else g.moj_gracz
	var d: Dictionary = g.D.budynki[typ]
	var t := "[b]%s[/b]\n%s\n[color=#a8282c]Koszt: %s[/color]" % [d.nazwa, d.opis, g.koszt_tekst(g.koszt_budynku(p, typ))]
	var teren := []
	for c in str(d.teren):
		teren.append(g.D.teren[c].nazwa.to_lower())
	t += "\nTeren: " + ", ".join(teren)
	if d.has("obok"):
		t += " (obok: %s)" % g._nazwy_terenow(str(d.obok))
	var dost: Array = g.dostepny_budynek(p, typ)
	if not dost[0]:
		t += "\n[color=#a8282c]%s[/color]" % dost[1]
	info_l.text = t


func najechane_pole(pole: Vector2i) -> void:
	if info_l == null or not is_instance_valid(info_l) or g.wybrany != "":
		if g.wybrany != "" and info_l and is_instance_valid(info_l):
			var m: Array = g.moze_budowac(g.S.aktywny, g.wybrany, pole.x, pole.y)
			_info_typu(g.wybrany)
			info_l.text += "\n" + ("[color=#2b7a32]Można tu budować (LPM). Shift – kilka naraz.[/color]" if m[0] else "[color=#a8282c]%s[/color]" % m[1])
		return
	var tr: String = g.teren(pole.x, pole.y)
	if tr == "":
		return
	var t := "[b]%s[/b] (%d, %d)" % [g.D.teren[tr].nazwa, pole.x, pole.y]
	var w: int = g.wlasc(pole.x, pole.y)
	if w >= 0:
		t += " – ziemia: %s" % g.gr(w).imie
	var bi: int = g.budynek_na(pole.x, pole.y)
	if bi >= 0:
		var b: Dictionary = g.S.budynki[bi]
		t += "\n%s%s" % [g.D.budynki[b.typ].nazwa, "" if b.gotowy else " (w budowie – gotowy w następnej turze)"]
	var zi: int = g.zagon_na(pole.x, pole.y)
	if zi >= 0:
		t += "\n[color=#a8282c]%s – siła %d. Kliknij, aby przechwycić.[/color]" % [g.S.zagony[zi].nazwa, int(g.S.zagony[zi].sila)]
	info_l.text = t


func info_budynku(bi: int) -> void:
	var b: Dictionary = g.S.budynki[bi]
	var d: Dictionary = g.D.budynki[b.typ]
	var vb := _okno(d.nazwa, Vector2(520, 300))
	var hb := HBoxContainer.new()
	vb.add_child(hb)
	hb.add_child(_obraz("res://ui/budynek_%s.png" % b.typ, Vector2(110, 110)))
	hb.add_child(_zawin(_label(d.opis + ("\n\n(W budowie – będzie gotowy w następnej turze.)" if not b.gotowy else ""), 16), 360))
	if int(b.wl) == g.S.aktywny and not b.get("siedziba", false) and g.moja_tura():
		vb.add_child(_btn("Rozbierz (bez zwrotu kosztów)", func():
			g.akcja_rozbierz(int(b.x), int(b.y))
			zamknij_okno(), "", 15))


func rada(tekst: String) -> void:
	if rada_panel == null or not is_instance_valid(rada_panel):
		toast(tekst)
		return
	rada_panel.visible = true
	rada_tekst.text = "Damian radzi: " + tekst
	g.lektor(tekst)
	var tw := create_tween()
	rada_panel.modulate.a = 1.0
	tw.tween_interval(7.0)
	tw.tween_property(rada_panel, "modulate:a", 0.0, 0.8)
	tw.tween_callback(func(): if is_instance_valid(rada_panel): rada_panel.visible = false)


func klik_koniec_tury() -> void:
	if not g.moja_tura() or g.scena != "gra" or okno != null:
		return
	g.anuluj_wybor()
	g.akcja_koniec_tury()


func _start_bitwy() -> void:
	if not g.mozna_bitwe(g.S.aktywny)[0]:
		return
	zamknij_okno(false)
	g.bitwa.rozpocznij()


func po_bitwie(wygrana: bool) -> void:
	if wygrana and g.S.tryb == "kampania" and g.rozdzial_ukonczony(0):
		g.akcja_koniec_tury()
	elif wygrana:
		toast("Zwycięstwo! +15 chwały" + (" i +10 za pierwsze zwycięstwo – gra skończy się po tej rundzie." if g.S.tryb != "kampania" and int(g.S.zwyciezca) == g.S.aktywny else ""))


# ----------------------------------------------------------------- czat (online)
func odswiez_czat() -> void:
	if czat_box == null or not is_instance_valid(czat_box) or g.S.is_empty() or g.S.tryb != "online":
		return
	if czat_box.get_child_count() == 0:
		czat_box.add_child(_label("Czat", 15))
		czat_l = RichTextLabel.new()
		czat_l.custom_minimum_size = Vector2(280, 110)
		czat_l.scroll_following = true
		czat_l.add_theme_font_size_override("normal_font_size", 13)
		czat_box.add_child(czat_l)
		var le := LineEdit.new()
		le.placeholder_text = "Napisz i Enter…"
		le.text_submitted.connect(func(tx):
			g.siec.wyslij_czat(tx)
			le.text = ""
			le.release_focus()
			odswiez_czat())
		czat_box.add_child(le)
	if czat_l:
		czat_l.text = "\n".join(g.siec.czat.slice(maxi(0, g.siec.czat.size() - 30)))


# ===================================================================== okna
func _okno(tytul: String, rozmiar: Vector2) -> VBoxContainer:
	zamknij_okno(false)
	okno = Control.new()
	okno.set_anchors_preset(Control.PRESET_FULL_RECT)
	korzen.add_child(okno)
	var cien := ColorRect.new()
	cien.color = Color(0, 0, 0, 0.45)
	cien.set_anchors_preset(Control.PRESET_FULL_RECT)
	okno.add_child(cien)
	var panel := PanelContainer.new()
	panel.custom_minimum_size = rozmiar
	panel.position = (Vector2(1280, 720) - rozmiar) / 2
	okno.add_child(panel)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	panel.add_child(vb)
	var hb := HBoxContainer.new()
	vb.add_child(hb)
	var t := _label(tytul, 24, C_CZERW)
	t.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb.add_child(t)
	hb.add_child(_btn("Zamknij", func(): zamknij_okno(), "", 15))
	if toasty.get_parent() == korzen:
		korzen.move_child(toasty, -1)
	g.dzwiek("strona")
	return vb


func zamknij_okno(dzw := true) -> void:
	if okno and is_instance_valid(okno):
		okno.queue_free()
	okno = null
	otwarte = ""
	if dzw:
		_nastepne_z_kolejki()


func zamknij_wszystko() -> void:
	_kolejka = []
	zamknij_okno(false)


func przelacz_okno(nazwa: String) -> void:
	if otwarte == nazwa:
		zamknij_okno()
		return
	match nazwa:
		"technologie": _okno_technologii()
		"wojsko": _okno_wojska()
		"ksiega": _okno_ksiegi()
		"pomoc": _okno_pomocy()
		"menu": _okno_menu()
	otwarte = nazwa


func _scroll(vb: VBoxContainer, wys: float) -> VBoxContainer:
	var sc := ScrollContainer.new()
	sc.custom_minimum_size = Vector2(0, wys)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	vb.add_child(sc)
	var w := VBoxContainer.new()
	w.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	w.add_theme_constant_override("separation", 6)
	sc.add_child(w)
	return w


func _okno_technologii() -> void:
	if g.S.is_empty():
		return
	var vb := _okno("Technologie – wiedza Rzymu", Vector2(1000, 600))
	vb.add_child(_label("Każdą technologię zdobywa się zagadką. Zła odpowiedź kosztuje połowę ceny – spróbujesz w kolejnej turze.", 15, C_SZARY))
	var lista := _scroll(vb, 500)
	var p: int = g.S.aktywny
	var siatka := GridContainer.new()
	siatka.columns = 2
	siatka.add_theme_constant_override("h_separation", 10)
	siatka.add_theme_constant_override("v_separation", 8)
	lista.add_child(siatka)
	for id in g.lista_techow():
		var tch: Dictionary = g.D.technologie[id]
		var pc := PanelContainer.new()
		var zna: bool = g.ma_tech(p, id)
		pc.add_theme_stylebox_override("panel", _sb(Color("d9efc8") if zna else Color("f6ead0"), Color("6b2a1c"), 1, 6, 8))
		pc.custom_minimum_size = Vector2(470, 0)
		var v := VBoxContainer.new()
		pc.add_child(v)
		var hb := HBoxContainer.new()
		v.add_child(hb)
		var n := _label("%s  (%s)" % [tch.nazwa, g.D.epoki[tch.epoka].nazwa], 17, C_ZIELONY if zna else C_TEKST)
		n.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		hb.add_child(n)
		if zna:
			hb.add_child(_label("odkryta", 14, C_ZIELONY))
		else:
			var m: Array = g.mozna_tech(p, id)
			var b := _btn("Zagadka » " + g.koszt_tekst(g.koszt_techu(p, id)), func(): zagadka_techu(id), "", 13)
			b.disabled = not m[0] or not g.moja_tura()
			b.tooltip_text = m[1]
			hb.add_child(b)
		v.add_child(_zawin(_label(tch.opis, 14), 440))
		siatka.add_child(pc)


func zagadka_techu(id: String) -> void:
	var tch: Dictionary = g.D.technologie[id]
	var hints: int = int(g.D.trudnosci[int(g.S.trudnosc)].podpowiedzi) + (1 if g.ma_tech(g.S.aktywny, "pismo") else 0)
	quiz("Zagadka: " + tch.nazwa, tch.p, tch.o, int(tch.d), hints, func(ok):
		g.akcja_tech(id, ok)
		if ok:
			g.dzwiek("odkrycie")
		return "Ciekawostka: " + tch.ciekawostka if ok else "Nie tym razem. Zapłacono połowę kosztu – spróbuj w następnej turze.")


func quiz(tytul: String, pytanie: String, odp: Array, dobra: int, podpowiedzi: int, po: Callable) -> void:
	## Pytanie z 4 odpowiedziami (pomieszanymi). po(ok) zwraca tekst komentarza (lub null).
	var vb := _okno(tytul, Vector2(760, 440))
	vb.add_child(_zawin(_label(pytanie, 21), 720))
	g.lektor(pytanie)
	var kolej := range(odp.size())
	kolej.shuffle()
	var usun := []
	if podpowiedzi > 0:
		var zle := []
		for i in odp.size():
			if i != dobra:
				zle.append(i)
		zle.shuffle()
		usun = zle.slice(0, mini(podpowiedzi, 2))
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	vb.add_child(box)
	var kom := _label("", 16)
	_zawin(kom, 720)
	var przyciski := []
	for i in kolej:
		var b := _btn(odp[i], func(): pass, "", 17)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		if i in usun:
			b.disabled = true
			b.text += "  (podpowiedź: to nie to)"
		przyciski.append([b, i])
		box.add_child(b)
	for para in przyciski:
		var b: Button = para[0]
		var i: int = para[1]
		b.pressed.connect(func():
			for q in przyciski:
				q[0].disabled = true
				if q[1] == dobra:
					q[0].add_theme_stylebox_override("disabled", _sb(Color("9fd38a"), Color("2b7a32"), 2, 6, 7))
			var ok := i == dobra
			if not ok:
				b.add_theme_stylebox_override("disabled", _sb(Color("e8a090"), Color("a8282c"), 2, 6, 7))
			g.dzwiek("dobrze" if ok else "zle")
			var t = po.call(ok)
			kom.text = ("Dobrze! " if ok else "Niestety. ") + (str(t) if t != null else "")
			kom.add_theme_color_override("font_color", C_ZIELONY if ok else C_CZERW)
			var dalej := _btn("Dalej »", func(): zamknij_okno(), "", 17)
			vb.add_child(dalej))
	vb.add_child(kom)


func pytanie_rady(cb: Callable, podpowiedzi: int) -> void:
	var epoka: String = g.R.epoka
	var pula := []
	for i in g.D.pytania.size():
		if g.D.pytania[i].e == epoka and not i in g.S.pytania_uzyte:
			pula.append(i)
	if pula.is_empty():
		for i in g.D.pytania.size():
			if g.D.pytania[i].e == epoka:
				pula.append(i)
	var i: int = pula[randi() % pula.size()]
	g.S.pytania_uzyte.append(i)
	var q: Dictionary = g.D.pytania[i]
	quiz("Pytanie rady wojennej", q.p, q.o, int(q.d), podpowiedzi, func(ok):
		_po_quizie_rady = cb.bind(ok)
		return "Wszystkie karty +1, morale +3!" if ok else "Poprawna odpowiedź: " + q.o[int(q.d)])
	if okno:
		okno.z_index = 10
		okno.tree_exited.connect(func():
			if _po_quizie_rady.is_valid():
				var c := _po_quizie_rady
				_po_quizie_rady = Callable()
				c.call())


var _po_quizie_rady := Callable()


func _okno_wojska() -> void:
	if g.S.is_empty():
		return
	var p: int = g.S.aktywny
	var vb := _okno("Wojsko – talia kart", Vector2(1040, 620))
	var baza: int = g.BAZA_TALII + (2 if g.ma_tech(p, "reforma_mariusza") else 0)
	vb.add_child(_zawin(_label("Twoja talia: %d kart (bez kosztów do %d; każdy oddział ponad to zjada 1 zboże na turę). Werbunek: %d/%d w tej turze (1 na każde gotowe koszary)." % [g.gr(p).talia.size(), baza, int(g.gr(p).rekrut), g.limit_werbunku(p)], 15), 1000))
	vb.add_child(_label("Piechota bije jazdę, jazda bije strzelców, strzelcy biją piechotę (+3).", 15, C_SZARY))
	var lista := _scroll(vb, 520)
	lista.add_child(_label("Twoje oddziały (kliknij, by zwolnić):", 16, C_CZERW))
	var talia := HFlowContainer.new()
	talia.add_theme_constant_override("h_separation", 6)
	talia.add_theme_constant_override("v_separation", 6)
	lista.add_child(talia)
	for i in g.gr(p).talia.size():
		var id: String = g.gr(p).talia[i]
		talia.add_child(_mini_karta(id, p, "Zwolnij", func():
			g.akcja_zwolnij(i)
			_okno_wojska()
			otwarte = "wojsko"))
	lista.add_child(_label("Werbunek:", 16, C_CZERW))
	var wer := HFlowContainer.new()
	wer.add_theme_constant_override("h_separation", 6)
	wer.add_theme_constant_override("v_separation", 6)
	lista.add_child(wer)
	for id in g.karty_do_werbunku(p):
		wer.add_child(_mini_karta(id, p, "Werbuj: " + g.koszt_tekst(g.koszt_karty(p, id)), func():
			if g.akcja_werbuj(id):
				_okno_wojska()
				otwarte = "wojsko"))


func _mini_karta(id: String, p: int, akcja_tekst: String, akcja: Callable) -> Control:
	var c: Dictionary = g.D.karty[id]
	var pc := PanelContainer.new()
	pc.add_theme_stylebox_override("panel", _sb(Color("f6ead0"), Color("6b2a1c"), 1, 6, 6))
	pc.custom_minimum_size = Vector2(158, 0)
	var v := VBoxContainer.new()
	pc.add_child(v)
	v.add_child(_obraz("res://ui/karta_%s.png" % c.model, Vector2(140, 80)))
	v.add_child(_zawin(_label(c.nazwa, 14), 146))
	v.add_child(_label("%s · siła %d%s" % [g.D.typy_kart[c.typ].nazwa, g.sila_karty(p, id), (" · tarcza %d" % int(c.tarcza)) if c.has("tarcza") else ""], 13, C_CZERW))
	var b := _btn(akcja_tekst, akcja, "", 12)
	b.disabled = not g.moja_tura()
	b.tooltip_text = c.get("opis", "")
	v.add_child(b)
	return pc


func okno_przechwytu(zi: int) -> void:
	var z: Dictionary = g.S.zagony[zi]
	var p: int = g.S.aktywny
	var vb := _okno("Przechwycić zagon?", Vector2(560, 300))
	vb.add_child(_zawin(_label("%s (siła %d) maszeruje na twoje ziemie i spali najbliższy budynek, chyba że chronią go mury." % [z.nazwa, int(z.sila)], 17), 520))
	vb.add_child(_zawin(_label("Potyczka: średnia 3 najsilniejszych kart + rzut kostką kontra siła zagonu + rzut. Przegrana kosztuje 1 oddział.", 14, C_SZARY), 520))
	var b := _btn("Do ataku!", func():
		var w: Dictionary = g.przechwyc(zi)
		zamknij_okno(false)
		toast(("Zwycięstwo! %d : %d. Zagon rozbity, +3 denary, +2 chwały." if w.wygrana else "Porażka %d : %d. Straciliśmy oddział, zagon idzie dalej.") % [w.moja, w.wroga]), "", 18)
	b.disabled = int(g.gr(p).przechwyt) >= 1 or not g.moja_tura() or g.wlasc(int(z.x), int(z.y)) != p and _odl_do_ziem(z, p) > 1
	if int(g.gr(p).przechwyt) >= 1:
		b.tooltip_text = "Jedna potyczka na turę"
	elif b.disabled:
		b.tooltip_text = "Zagon musi być na twoich ziemiach lub tuż przy nich"
	vb.add_child(b)


func _odl_do_ziem(z: Dictionary, p: int) -> int:
	var najl := 99
	for y in range(int(z.y) - 2, int(z.y) + 3):
		for x in range(int(z.x) - 2, int(z.x) + 3):
			if g.wlasc(x, y) == p:
				najl = mini(najl, maxi(absi(x - int(z.x)), absi(y - int(z.y))))
	return najl


func pokaz_znajdzke(id: String) -> void:
	var z: Dictionary = g.D.znajdzki[id]
	var vb := _okno("Znalezisko: " + z.nazwa, Vector2(520, 240))
	vb.add_child(_zawin(_label(z.opis, 18), 480))
	vb.add_child(_label("+3 chwały", 16, C_ZIELONY))
	g.lektor(z.opis)


func okno_info(tytul: String, tekst: String, model := "") -> void:
	var vb := _okno(tytul, Vector2(560, 260))
	vb.add_child(_zawin(_label(tekst, 18), 520))
	g.lektor(tekst)


# ----------------------------------------------------------------- wydarzenia
func kolejka_okien(lista: Array) -> void:
	_kolejka = lista.duplicate()
	if okno == null:
		_nastepne_z_kolejki()


func _nastepne_z_kolejki() -> void:
	if _kolejka.is_empty() or g.scena != "gra":
		return
	var k: Dictionary = _kolejka.pop_front()
	match k.typ:
		"wiadomosc":
			var vb := _okno("Wieści z prowincji", Vector2(520, 220))
			vb.add_child(_zawin(_label(k.tekst, 18), 480))
		"wydarzenie":
			pokaz_wydarzenie(k.id)
		"losowe":
			var l: Dictionary = k.dane
			var vb := _okno(l.tytul, Vector2(600, 300))
			vb.add_child(_zawin(_label(l.opis, 18), 560))
			var ef := []
			for z in l.efekt:
				if g.D.zasoby.has(z):
					ef.append("%s%d %s" % ["+" if int(l.efekt[z]) > 0 else "", int(l.efekt[z]), g.D.zasoby[z].nazwa.to_lower()])
			vb.add_child(_label(", ".join(ef), 16, C_CZERW))
			vb.add_child(_zawin(_label("Lekcja kronikarza: " + l.lekcja, 15, C_FIOLET), 560))
			g.lektor(l.opis)


func pokaz_wydarzenie(id: String) -> void:
	var w: Dictionary = g.D.wydarzenia[id]
	var vb := _okno("%s (%s)" % [w.tytul, w.rok], Vector2(820, 520))
	vb.add_child(_zawin(_label(w.opis, 18), 780))
	g.lektor(w.opis)
	var p: int = g.S.aktywny
	var senat: bool = g.ile_budynkow(p, "kuria", true) > 0
	vb.add_child(_label("Co doradzasz?" + ("  (Senat w kurii podpowiada, co wybrali Rzymianie)" if senat else ""), 16, C_CZERW))
	for i in w.opcje.size():
		var op: Dictionary = w.opcje[i]
		var ef := []
		for z in op.efekt:
			var v = op.efekt[z]
			if g.D.zasoby.has(z):
				ef.append("%s%d %s" % ["+" if int(v) > 0 else "", int(v), g.D.zasoby[z].nazwa.to_lower()])
			elif z == "chwala":
				ef.append("%s%d chwały" % ["+" if int(v) > 0 else "", int(v)])
			elif z == "karta":
				ef.append("oddział: " + g.D.karty[v].nazwa)
			elif z == "inflacja":
				ef.append("inflacja rośnie!")
			elif z == "ludnosc":
				ef.append("%s%d mieszkańców" % ["+" if int(v) > 0 else "", int(v)])
			elif z == "wrog":
				ef.append("wróg się zbroi")
			elif z == "obrona":
				ef.append("mury chronią szerzej")
		var tx: String = op.tekst + "\n(" + ", ".join(ef) + ")"
		if senat and op.get("historia", false):
			tx += "  – tak wybrali Rzymianie"
		var b := _btn(tx, func():
			if not g.moja_tura():
				return
			g.akcja_wydarzenie(id, i)
			_komentarz_wydarzenia(id, i), "", 15)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		b.custom_minimum_size = Vector2(780, 0)
		vb.add_child(b)
	# okno musi zostać wybrane
	vb.get_child(0).get_child(1).visible = false


func _komentarz_wydarzenia(id: String, i: int) -> void:
	var w: Dictionary = g.D.wydarzenia[id]
	var op: Dictionary = w.opcje[i]
	var vb := _okno("Co było naprawdę?", Vector2(760, 360))
	vb.add_child(_label("Twój wybór jest zgodny z historią! +1 chwały" if op.get("historia", false) else "Rzymianie postąpili inaczej – ale historia mogła potoczyć się różnie.", 17, C_ZIELONY if op.get("historia", false) else C_CZERW))
	vb.add_child(_zawin(_label(w.komentarz, 17), 720))
	g.lektor(w.komentarz)


# ----------------------------------------------------------------- Księga Wiedzy
var ksiega_kat := "pojęcia"


func _dostepny_rozdzial() -> int:
	if not g.S.is_empty():
		return maxi(int(g.S.rozdzial) + 1, g.K.ukonczone.size() + 1)
	return g.K.ukonczone.size() + 1


func _okno_ksiegi() -> void:
	var vb := _okno("Księga Wiedzy kronikarza", Vector2(1100, 640))
	var tabs := TabContainer.new()
	tabs.custom_minimum_size = Vector2(1060, 560)
	vb.add_child(tabs)
	var dost := _dostepny_rozdzial()
	if otwarte_wszystkie:
		dost = 99
	# hasła
	for kat in ["pojęcia", "miejsca", "ludzie", "ludy", "wojsko", "wynalazki"]:
		var sc := ScrollContainer.new()
		sc.name = kat.capitalize()
		sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		tabs.add_child(sc)
		var v := VBoxContainer.new()
		v.add_theme_constant_override("separation", 8)
		sc.add_child(v)
		for e in g.D.encyklopedia:
			if e.kat != kat:
				continue
			var pc := PanelContainer.new()
			pc.add_theme_stylebox_override("panel", _sb(Color("f6ead0"), Color("b48a5a"), 1, 6, 8))
			var vv := VBoxContainer.new()
			pc.add_child(vv)
			if int(e.od) <= dost:
				var hb := HBoxContainer.new()
				var h := _label(e.haslo, 18, C_CZERW)
				h.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				hb.add_child(h)
				hb.add_child(_btn("Czytaj", func(): g.lektor(e.tekst), "", 12))
				vv.add_child(hb)
				vv.add_child(_zawin(_label(e.tekst, 15), 1000))
			else:
				vv.add_child(_label("??? – odblokujesz w rozdziale %s" % RZYMSKIE[int(e.od)], 15, C_SZARY))
			v.add_child(pc)
	# postacie
	var sc2 := ScrollContainer.new()
	sc2.name = "Postacie"
	sc2.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	tabs.add_child(sc2)
	var v2 := VBoxContainer.new()
	v2.add_theme_constant_override("separation", 8)
	sc2.add_child(v2)
	var od := {"damian": 1, "romulus": 1, "cyncynat": 2, "brennus": 2, "hannibal": 3, "scypion": 3, "cezar": 4,
		"wercyngetoryks": 4, "kleopatra": 5, "antoniusz": 5, "august": 6, "trajan": 7, "konstantyn": 8, "attyla": 9,
		"odoaker": 9, "romulus_augustulus": 9}
	for id in g.D.postacie:
		var ps: Dictionary = g.D.postacie[id]
		var pc := PanelContainer.new()
		pc.add_theme_stylebox_override("panel", _sb(Color("f6ead0"), Color("b48a5a"), 1, 6, 8))
		var hb := HBoxContainer.new()
		hb.add_theme_constant_override("separation", 12)
		pc.add_child(hb)
		if int(od.get(id, 1)) <= dost:
			hb.add_child(_portret(id, 110))
			var vv := VBoxContainer.new()
			hb.add_child(vv)
			vv.add_child(_label("%s · %s" % [ps.imie, ps.lata], 19, C_CZERW))
			vv.add_child(_label(ps.rola, 15, C_FIOLET))
			vv.add_child(_zawin(_label(ps.opis, 15), 860))
			for f in ps.fakty:
				vv.add_child(_zawin(_label("• " + f, 14), 860))
			vv.add_child(_zawin(_label("Ciekawostka: " + ps.ciekawostka, 14, C_ZIELONY), 860))
		else:
			hb.add_child(_label("??? – postać pojawi się w rozdziale %s" % RZYMSKIE[int(od.get(id, 1))], 15, C_SZARY))
		v2.add_child(pc)
	# oś czasu
	var sc3 := ScrollContainer.new()
	sc3.name = "Oś czasu"
	tabs.add_child(sc3)
	var v3 := VBoxContainer.new()
	sc3.add_child(v3)
	for i in g.D.rozdzialy.size():
		var r: Dictionary = g.D.rozdzialy[i]
		var hb := HBoxContainer.new()
		var rok := _label(r.lata, 16, Color(g.D.epoki[r.epoka].kolor).darkened(0.3))
		rok.custom_minimum_size.x = 210
		hb.add_child(rok)
		hb.add_child(_zawin(_label("%s – %s. %s" % [r.tytul, r.bitwa.nazwa + " (" + r.bitwa.rok + ")", r.koniec if i + 1 <= dost else ""], 15), 820))
		v3.add_child(hb)
	v3.add_child(_zawin(_label("Epoki: Królestwo (753–509 p.n.e.) · Republika (509–27 p.n.e.) · Cesarstwo (27 p.n.e.–284 n.e.) · Późne cesarstwo (284–476 n.e.). Cesarstwo wschodnie trwało do 1453 r.", 15, C_SZARY), 1020))


func _okno_pomocy() -> void:
	var vb := _okno("Jak grać", Vector2(900, 580))
	var tekst := """Jesteś doradcą władców Rzymu – a kronikarz Damian pomaga ci radami.
• Buduj w granicach swoich ziem (żółta lub kolorowa linia). Każdy budynek poszerza granice o 2 pola.
• Budynek stawiasz w jednej turze, działa od następnej. Każdy kolejny tego samego typu kosztuje 25% więcej.
• Mieszkańcy (chaty, domy, insule) obsługują budynki. Gdy ich brakuje, produkcja spada.
• Mieszkańcy i wojsko jedzą zboże. Głód spowalnia pracę i powoduje dezercję.
• Technologie zdobywasz, odpowiadając na zagadki. Zła odpowiedź = połowa kosztu przepada.
• Zagony wroga wychodzą z obozów i palą budynki. Mury chronią w promieniu 2 pól; zagon możesz też przechwycić (kliknij go).
• Gdy wykonasz pozostałe zadania, kliknij „Do boju!”. Bitwa: najpierw pytanie rady wojennej, potem karty.
  Piechota bije jazdę, jazda bije strzelców, strzelcy biją piechotę (+3). Taktyki można użyć raz w bitwie.
• Chwała to twój wynik. Dają ją świątynie, termy, amfiteatry, odkrycia, wydarzenia zgodne z historią i zwycięstwa.

Sterowanie: WASD/strzałki lub prawy przycisk myszy – przesuwanie mapy, kółko – przybliżenie, Q/E – obrót,
C – powrót do siedziby, Spacja – koniec tury, T – technologie, K – wojsko, L – Księga, M – muzyka, G – lektor, F11 – pełny ekran.

Gra wieloosobowa: przy jednym komputerze gracze grają po kolei; online – jeden gracz zakłada pokój (kod 4 liter), reszta dołącza."""
	vb.add_child(_zawin(_label(tekst, 16), 860))


func _okno_menu() -> void:
	var vb := _okno("Menu", Vector2(420, 360))
	vb.add_child(_btn("Wróć do gry", func(): zamknij_okno(), "", 18))
	vb.add_child(_btn("Muzyka wł./wył. (M)", func(): g.przelacz_muzyke(), "", 16))
	vb.add_child(_btn("Lektor wł./wył. (G)", func(): g.przelacz_lektora(), "", 16))
	if not g.S.is_empty() and g.S.tryb == "kampania":
		vb.add_child(_btn("Zacznij rozdział od nowa", func():
			zamknij_okno(false)
			g.rozpocznij_rozdzial(int(g.S.rozdzial), [{"imie": "Damian", "rod": 0}], "kampania", int(g.S.trudnosc)), "", 16))
	vb.add_child(_btn("Menu główne (gra jest zapisana)", func():
		zamknij_okno(false)
		if not g.S.is_empty() and g.S.tryb == "online":
			g.siec.rozlacz()
		g.pokaz_tytul(), "", 16))


# ===================================================================== ekrany końcowe
func _gwiazdy(n: int) -> Control:
	var gw := Gwiazdy.new()
	gw.ile = n
	gw.custom_minimum_size = Vector2(170, 52)
	return gw


class Gwiazdy extends Control:
	var ile := 0

	func _draw() -> void:
		for i in 3:
			var c := Vector2(28 + i * 56, 26)
			var pts := PackedVector2Array()
			for k in 10:
				var r := 24.0 if k % 2 == 0 else 10.0
				var a := -PI / 2 + k * PI / 5
				pts.append(c + Vector2(cos(a), sin(a)) * r)
			draw_colored_polygon(pts, Color(0.96, 0.78, 0.2) if i < ile else Color(0.5, 0.45, 0.4, 0.6))
			draw_polyline(pts + PackedVector2Array([pts[0]]), Color(0.3, 0.18, 0.08), 2)


class ZnakZasobu extends Control:
	var rodzaj := ""

	func _draw() -> void:
		var s := size
		var c := s / 2
		match rodzaj:
			"zboze":
				draw_line(Vector2(c.x, s.y), Vector2(c.x, 3), Color(0.95, 0.8, 0.3), 2)
				for k in 4:
					draw_circle(Vector2(c.x - 3, 5 + k * 4), 2.5, Color(0.95, 0.78, 0.3))
					draw_circle(Vector2(c.x + 3, 6 + k * 4), 2.5, Color(0.95, 0.78, 0.3))
			"drewno":
				draw_rect(Rect2(2, c.y - 4, s.x - 4, 8), Color(0.62, 0.42, 0.22))
				draw_circle(Vector2(s.x - 4, c.y), 4, Color(0.85, 0.66, 0.4))
			"kamien":
				draw_colored_polygon(PackedVector2Array([Vector2(2, s.y - 3), Vector2(6, 6), Vector2(14, 3), Vector2(s.x - 2, 10), Vector2(s.x - 3, s.y - 3)]), Color(0.72, 0.72, 0.7))
			"denary":
				draw_circle(c, s.x / 2 - 1, Color(0.6, 0.45, 0.1))
				draw_circle(c, s.x / 2 - 3, Color(0.96, 0.82, 0.35))


func _ekran_koniec_rozdzialu() -> void:
	ekran = _pelny()
	_tlo_obraz(ekran, "res://ui/tlo_tytul.png", 0.6)
	var r: Dictionary = g.R
	var wyn: Dictionary = g.K.wyniki.get(r.id, {})
	var panel := PanelContainer.new()
	panel.position = Vector2(190, 70)
	panel.custom_minimum_size = Vector2(900, 560)
	ekran.add_child(panel)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 12)
	panel.add_child(vb)
	vb.add_child(_label("Rozdział %s ukończony!" % RZYMSKIE[int(g.D.rozdzialy.find(r)) + 1], 18, C_CZERW))
	vb.add_child(_label(r.tytul, 38))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 16)
	vb.add_child(hb)
	hb.add_child(_portret("damian", 120))
	var kr := _label("Kronika zapisuje: " + r.koniec, 19)
	_zawin(kr, 720)
	hb.add_child(kr)
	g.lektor(r.koniec)
	vb.add_child(_gwiazdy(int(g.gwiazdki())))
	var st: Dictionary = g.gr(0).stat
	vb.add_child(_label("Chwała: %d · Tury: %d/%d · Budowy: %d · Pytania: %d/%d dobrze" % [int(g.gr(0).chwala), int(g.S.tura), int(r.tury), int(st.budowy), int(st.pyt_ok), int(st.pyt_all)], 18))
	if not wyn.is_empty():
		vb.add_child(_label("Najlepszy wynik: chwała %d" % int(wyn.chwala), 15, C_SZARY))
	var dol := HBoxContainer.new()
	dol.alignment = BoxContainer.ALIGNMENT_END
	vb.add_child(dol)
	dol.add_child(_btn("Menu główne", func(): g.pokaz_tytul(), "", 16))
	dol.add_child(_btn("Dalej – następna epoka »", func(): g.dalej_po_rozdziale(), "", 20))


func _ekran_koniec_mp() -> void:
	var vb := _okno("Koniec gry – ranking rodów", Vector2(700, 460))
	vb.get_child(0).get_child(1).visible = false
	var rk: Array = g.ranking()
	var miejsce := 1
	for para in rk:
		var gi: Dictionary = g.S.gracze[para[1]]
		var hb := HBoxContainer.new()
		var kol := ColorRect.new()
		kol.color = Color(g.D.rody[int(gi.rod)].kolor)
		kol.custom_minimum_size = Vector2(24, 24)
		hb.add_child(kol)
		hb.add_child(_label("%d. %s (ród %s) – chwała %d · zadania %d/%d%s" % [miejsce, gi.imie, g.D.rody[int(gi.rod)].nazwa, int(gi.chwala), gi.cele_ok.size(), g.R.cele.size(), " · zwycięzca bitwy!" if gi.bitwa else ""], 18 if miejsce == 1 else 16, C_CZERW if miejsce == 1 else C_TEKST))
		vb.add_child(hb)
		miejsce += 1
	var zw: Dictionary = g.S.gracze[rk[0][1]]
	vb.add_child(_zawin(_label("Senat i Lud Rzymski ogłaszają: ród %s zdobywa największą chwałę! %s otrzymuje tytuł Ojca Ojczyzny (pater patriae)." % [g.D.rody[int(zw.rod)].nazwa, zw.imie], 18, C_ZIELONY), 660))
	vb.add_child(_btn("Menu główne", func():
		if g.S.tryb == "online":
			g.siec.rozlacz()
		g.pokaz_tytul(), "", 18))


func _ekran_porazki() -> void:
	var vb := _okno("Kronika przerwana", Vector2(680, 360))
	vb.get_child(0).get_child(1).visible = false
	vb.add_child(_zawin(_label("Czas minął – na tym poziomie trudności rozdział trzeba ukończyć do tury %d. Senat odwołał cię z urzędu, a kronikarz Damian zamknął księgę… na razie." % g.limit_tur(), 18), 640))
	vb.add_child(_zawin(_label("Rada kronikarza: wcześniej buduj koszary i pola, odkrywaj potrzebne technologie i nie odkładaj bitwy na koniec.", 15, C_FIOLET), 640))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 12)
	vb.add_child(hb)
	hb.add_child(_btn("Spróbuj ponownie", func():
		zamknij_okno(false)
		g.rozpocznij_rozdzial(int(g.S.rozdzial), [{"imie": "Damian", "rod": 0}], "kampania", int(g.S.trudnosc)), "", 19))
	hb.add_child(_btn("Menu główne", func(): g.pokaz_tytul(), "", 17))


func _ekran_final() -> void:
	ekran = _pelny(Color("140d0b"))
	_tlo_obraz(ekran, "res://ui/tlo_tytul.png", 0.72)
	var vb := VBoxContainer.new()
	vb.position = Vector2(140, 50)
	vb.add_theme_constant_override("separation", 12)
	ekran.add_child(vb)
	vb.add_child(_cien_tekstu(_label("476 n.e. – koniec cesarstwa zachodniego", 34, C_ZLOTY), 10))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 16)
	vb.add_child(hb)
	hb.add_child(_portret("romulus_augustulus", 110))
	hb.add_child(_portret("odoaker", 110))
	var t := _label(g.D.final, 19, C_JASNY)
	_zawin(t, 760)
	hb.add_child(t)
	var dz := _label("Rzym żyje w nas: alfabet łaciński, kalendarz z lipcem i sierpniem, prawo („umów należy dotrzymywać”), słowa senat, republika, kandydat, akwedukt; drogi, łuki i kopuły; języki włoski, hiszpański, francuski, portugalski i rumuński.", 18, C_JASNY)
	_zawin(dz, 1000)
	vb.add_child(_cien_tekstu(dz, 6))
	var suma := 0
	var gw := 0
	for id in g.K.wyniki:
		suma += int(g.K.wyniki[id].chwala)
		gw += int(g.K.wyniki[id].gwiazdki)
	vb.add_child(_cien_tekstu(_label("Twoja kronika: %d/%d rozdziałów · chwała łącznie %d · gwiazdki %d/%d" % [g.K.ukonczone.size(), g.D.rozdzialy.size(), suma, gw, g.D.rozdzialy.size() * 3], 22, C_ZLOTY), 8))
	vb.add_child(_cien_tekstu(_label(_tytul_honorowy(suma), 26, Color(0.85, 0.7, 1.0)), 8))
	var dol := HBoxContainer.new()
	vb.add_child(dol)
	dol.add_child(_btn("Księga Wiedzy", func(): przelacz_okno("ksiega"), "", 18))
	dol.add_child(_btn("Menu główne", func(): g.pokaz_tytul(), "", 18))
	g.lektor(t.text)


func _tytul_honorowy(suma: int) -> String:
	if suma >= 1200:
		return "Tytuł: Pater Patriae – Ojciec Ojczyzny"
	if suma >= 800:
		return "Tytuł: Konsul i triumfator"
	if suma >= 400:
		return "Tytuł: Senator"
	return "Tytuł: Obywatel rzymski"


func _ekran_przekazania() -> void:
	var p: int = g.S.aktywny
	var gi: Dictionary = g.gr(p)
	var c := Control.new()
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	korzen.add_child(c)
	var cien := ColorRect.new()
	cien.color = Color(0.05, 0.03, 0.02, 0.85)
	cien.set_anchors_preset(Control.PRESET_FULL_RECT)
	c.add_child(cien)
	var panel := PanelContainer.new()
	panel.position = Vector2(390, 200)
	panel.custom_minimum_size = Vector2(500, 260)
	panel.add_theme_stylebox_override("panel", _sb(Color("ecdcb0"), Color(g.D.rody[int(gi.rod)].kolor), 6, 10, 18))
	c.add_child(panel)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 12)
	panel.add_child(vb)
	vb.add_child(_label("Tura %d" % int(g.S.tura), 18, C_SZARY))
	vb.add_child(_label("Teraz gra: %s" % gi.imie, 32, C_CZERW))
	vb.add_child(_label("Ród %s – %s" % [g.D.rody[int(gi.rod)].nazwa, g.D.rody[int(gi.rod)].haslo], 17))
	vb.add_child(_label("Chwała: %d" % int(gi.chwala), 17, C_ZIELONY))
	vb.add_child(_btn("Zaczynam turę »", func(): g._rozpocznij_ture_gracza(), "", 20))


# ===================================================================== lobby online
var lobby_vb: VBoxContainer
var adres_le: LineEdit
var imie_le: LineEdit
var kod_le: LineEdit
var lobby_rozdz: OptionButton
var lobby_trud: OptionButton


func _ekran_lobby() -> void:
	ekran = _pelny()
	_tlo_obraz(ekran, "res://ui/tlo_tytul.png", 0.6)
	var panel := PanelContainer.new()
	panel.position = Vector2(170, 50)
	panel.custom_minimum_size = Vector2(940, 620)
	ekran.add_child(panel)
	lobby_vb = VBoxContainer.new()
	lobby_vb.add_theme_constant_override("separation", 8)
	panel.add_child(lobby_vb)
	var hb := HBoxContainer.new()
	lobby_vb.add_child(hb)
	var tl := _label("Gra wieloosobowa online", 28, C_CZERW)
	tl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb.add_child(tl)
	hb.add_child(_btn("Wróć", func():
		g.siec.rozlacz()
		g.pokaz_tytul(), "", 16))
	lobby_vb.add_child(_zawin(_label("Jeden gracz zakłada pokój i podaje innym jego kod (4 litery). Wszyscy łączą się z tym samym serwerem gry. Serwer uruchomisz poleceniem: godot --headless --path godot -- --serwer 9080 albo przyciskiem poniżej (wersja na Windows/Linux). W przeglądarce (https) potrzebny jest adres wss://.", 14, C_SZARY), 900))
	var siatka := GridContainer.new()
	siatka.columns = 2
	lobby_vb.add_child(siatka)
	siatka.add_child(_label("Twoje imię:", 16))
	imie_le = LineEdit.new()
	imie_le.text = g.siec.imie if g.siec.imie != "Gracz" else ""
	imie_le.placeholder_text = "np. Ala"
	imie_le.max_length = 16
	imie_le.custom_minimum_size = Vector2(300, 0)
	siatka.add_child(imie_le)
	siatka.add_child(_label("Adres serwera:", 16))
	adres_le = LineEdit.new()
	adres_le.text = _domyslny_adres()
	adres_le.custom_minimum_size = Vector2(420, 0)
	siatka.add_child(adres_le)
	var pod := VBoxContainer.new()
	pod.name = "stan"
	lobby_vb.add_child(pod)
	odswiez_lobby()


func _domyslny_adres() -> String:
	if OS.has_feature("web"):
		var host = JavaScriptBridge.eval("window.location.hostname", true)
		var prot = JavaScriptBridge.eval("window.location.protocol", true)
		if str(host) in ["localhost", "127.0.0.1", ""]:
			return "ws://localhost:9080"
		return ("wss://" if str(prot) == "https:" else "ws://") + str(host) + ":9080"
	return "ws://localhost:9080"


func odswiez_lobby() -> void:
	if g.scena != "lobby" or lobby_vb == null or not is_instance_valid(lobby_vb):
		return
	var pod: VBoxContainer = lobby_vb.get_node("stan")
	for c in pod.get_children():
		c.queue_free()
	var s = g.siec
	if s.kod == "":
		var hb := HBoxContainer.new()
		hb.add_theme_constant_override("separation", 8)
		pod.add_child(hb)
		hb.add_child(_btn("Załóż pokój", func():
			s.polacz(adres_le.text.strip_edges(), imie_le.text.strip_edges())
			s.utworz_pokoj(), "", 18))
		kod_le = LineEdit.new()
		kod_le.placeholder_text = "KOD"
		kod_le.max_length = 4
		kod_le.custom_minimum_size = Vector2(90, 0)
		hb.add_child(kod_le)
		hb.add_child(_btn("Dołącz", func():
			if kod_le.text.strip_edges().length() != 4:
				toast("Wpisz 4-literowy kod pokoju")
				return
			s.polacz(adres_le.text.strip_edges(), imie_le.text.strip_edges())
			s.dolacz(kod_le.text.strip_edges().to_upper()), "", 18))
		if not OS.has_feature("web"):
			hb.add_child(_btn("Uruchom serwer na tym komputerze", func():
				if s.serwer == null and not s.uruchom_lokalny_serwer(9080):
					toast("Nie udało się uruchomić serwera (port 9080 zajęty?)")
					return
				adres_le.text = "ws://localhost:9080"
				var ad: Array = s.adresy_lokalne()
				toast("Serwer działa! Inni w tej samej sieci wpisują: ws://%s:9080" % (ad[0] if ad.size() > 0 else "TWOJ-IP"))
				odswiez_lobby(), "", 15))
		if s.serwer != null:
			var ad: Array = s.adresy_lokalne()
			pod.add_child(_label("Serwer działa na tym komputerze. Adres dla innych: ws://%s:9080" % (ad[0] if ad.size() > 0 else "?"), 15, C_ZIELONY))
		if s.ws != null:
			pod.add_child(_label("Łączenie z serwerem…", 15, C_SZARY))
		return
	pod.add_child(_label("Pokój: %s" % s.kod, 30, C_CZERW))
	pod.add_child(_label("Podaj ten kod innym graczom. Gracze (2–4):", 15))
	for i in s.gracze_lobby.size():
		var gl: Dictionary = s.gracze_lobby[i]
		var hb := HBoxContainer.new()
		var kol := ColorRect.new()
		kol.color = Color(g.D.rody[i].kolor)
		kol.custom_minimum_size = Vector2(20, 20)
		hb.add_child(kol)
		hb.add_child(_label("%s – ród %s%s" % [gl.imie, g.D.rody[i].nazwa, " (Ty)" if int(gl.id) == s.moj_id else ""], 17))
		pod.add_child(hb)
	if s.host:
		lobby_rozdz = OptionButton.new()
		for i in g.D.rozdzialy.size():
			var r: Dictionary = g.D.rozdzialy[i]
			lobby_rozdz.add_item("%s. %s (%s)" % [RZYMSKIE[i + 1], r.tytul, r.lata])
		pod.add_child(lobby_rozdz)
		lobby_trud = OptionButton.new()
		for tr in g.D.trudnosci:
			lobby_trud.add_item(tr.nazwa)
		lobby_trud.selected = 1
		pod.add_child(lobby_trud)
		var b := _btn("Rozpocznij grę »", func():
			s.rozpocznij_gre(lobby_rozdz.selected, lobby_trud.selected), "", 20)
		b.disabled = s.gracze_lobby.size() < 2
		pod.add_child(b)
	else:
		pod.add_child(_label("Czekamy, aż gospodarz pokoju rozpocznie grę…", 16, C_SZARY))
