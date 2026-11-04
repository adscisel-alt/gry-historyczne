extends RefCounted
## Wspólny wygląd interfejsu: papier, sepia, czcionki z polskimi znakami, fabryki kontrolek.

const ATRAMENT := Color(0.17, 0.12, 0.08)
const ATRAMENT_JASNY := Color(0.38, 0.30, 0.22)
const PAPIER := Color(0.91, 0.86, 0.75)
const PAPIER_CIEMNY := Color(0.78, 0.71, 0.58)
const FIOLET := Color(0.44, 0.24, 0.59)
const STEMPEL := Color(0.59, 0.20, 0.15)

static var _czcionki: Dictionary = {}


static func czcionka(rodzaj: String = "szeryf") -> Font:
	if _czcionki.has(rodzaj):
		return _czcionki[rodzaj]
	var f := SystemFont.new()
	match rodzaj:
		"plakat":
			f.font_names = PackedStringArray(["Bookman Old Style", "Georgia", "Cambria", "DejaVu Serif", "Liberation Serif"])
			f.font_weight = 700
		"reka":
			f.font_names = PackedStringArray(["Segoe Script", "Ink Free", "Georgia", "DejaVu Serif"])
			f.font_italic = true
		"maszyna":
			f.font_names = PackedStringArray(["Courier New", "DejaVu Sans Mono", "Liberation Mono"])
		_:
			f.font_names = PackedStringArray(["Georgia", "Cambria", "Times New Roman", "DejaVu Serif", "Liberation Serif"])
	_czcionki[rodzaj] = f
	return f


static func styl_papieru(ciemny: bool = false, ramka: Color = ATRAMENT_JASNY, grubosc: int = 2) -> StyleBox:
	var sb := StyleBoxTexture.new()
	sb.texture = Dane.tex_ui("papier_ciemny" if ciemny else "papier")
	sb.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_TILE
	sb.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_TILE
	sb.content_margin_left = 14
	sb.content_margin_right = 14
	sb.content_margin_top = 10
	sb.content_margin_bottom = 10
	return sb


static func styl_plaski(kolor: Color, ramka: Color = ATRAMENT_JASNY, grubosc: int = 2, promien: int = 5) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = kolor
	sb.border_color = ramka
	sb.set_border_width_all(grubosc)
	sb.set_corner_radius_all(promien)
	sb.content_margin_left = 12
	sb.content_margin_right = 12
	sb.content_margin_top = 6
	sb.content_margin_bottom = 6
	sb.shadow_color = Color(0.08, 0.05, 0.03, 0.55)
	sb.shadow_size = 0
	sb.shadow_offset = Vector2(4, 4)
	return sb


static func etykieta(tekst: String, rozmiar: int = 20, rodzaj: String = "szeryf", kolor: Color = ATRAMENT,
		zawijaj: bool = true, wyrownanie: int = HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := Label.new()
	l.text = tekst
	l.add_theme_font_override("font", czcionka(rodzaj))
	l.add_theme_font_size_override("font_size", rozmiar)
	l.add_theme_color_override("font_color", kolor)
	l.horizontal_alignment = wyrownanie
	if zawijaj:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return l


static func przycisk(tekst: String, rozmiar: int = 20, akcja: Callable = Callable()) -> Button:
	var b := Button.new()
	b.text = tekst
	b.add_theme_font_override("font", czcionka("plakat"))
	b.add_theme_font_size_override("font_size", rozmiar)
	for stan in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color"]:
		b.add_theme_color_override(stan, ATRAMENT)
	b.add_theme_color_override("font_disabled_color", Color(0.45, 0.40, 0.33))
	var normalny := styl_plaski(PAPIER)
	normalny.shadow_size = 1
	var nad := styl_plaski(Color(0.96, 0.92, 0.82), ATRAMENT, 3)
	nad.shadow_size = 1
	var wylaczony := styl_plaski(Color(0.70, 0.64, 0.54))
	b.add_theme_stylebox_override("normal", normalny)
	b.add_theme_stylebox_override("hover", nad)
	b.add_theme_stylebox_override("pressed", nad)
	b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	b.add_theme_stylebox_override("disabled", wylaczony)
	if akcja.is_valid():
		b.pressed.connect(akcja)
	return b


static func karta(rect: Rect2) -> Panel:
	## Kremowa pocztówka z ząbkowaną ramką (rysowaną w _draw nakładki) i cieniem.
	var p := Panel.new()
	var sb := StyleBoxTexture.new()
	sb.texture = Dane.tex_ui("papier")
	sb.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_TILE
	sb.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_TILE
	p.add_theme_stylebox_override("panel", sb)
	p.position = rect.position
	p.size = rect.size
	p.draw.connect(func(): rysuj_zabki(p))
	return p


static func rysuj_zabki(c: Control) -> void:
	var w := c.size.x
	var h := c.size.y
	var krok := 14.0
	var kol := Color(0.14, 0.09, 0.06)
	var x := 0.0
	while x < w:
		c.draw_circle(Vector2(x + krok / 2, 0), 4, kol)
		c.draw_circle(Vector2(x + krok / 2, h), 4, kol)
		x += krok
	var y := 0.0
	while y < h:
		c.draw_circle(Vector2(0, y + krok / 2), 4, kol)
		c.draw_circle(Vector2(w, y + krok / 2), 4, kol)
		y += krok
	c.draw_rect(Rect2(8, 8, w - 16, h - 16), Color(0.45, 0.37, 0.27, 0.8), false, 1.0)


static func stempel(c: CanvasItem, srodek: Vector2, napis: String, r: float = 46.0, kolor: Color = STEMPEL) -> void:
	var k := Color(kolor, 0.7)
	c.draw_set_transform(srodek, deg_to_rad(-14), Vector2.ONE)
	c.draw_arc(Vector2.ZERO, r, 0, TAU, 48, k, 3.0)
	c.draw_arc(Vector2.ZERO, r - 8, 0, TAU, 48, k, 1.0)
	var f := czcionka("plakat")
	var rozm := 13
	var szer := f.get_string_size(napis, HORIZONTAL_ALIGNMENT_LEFT, -1, rozm).x
	c.draw_string(f, Vector2(-szer / 2, 5), napis, HORIZONTAL_ALIGNMENT_LEFT, -1, rozm, k)
	c.draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)


static func etykieta_fiolet(tekst: String, rozmiar: int = 15) -> PanelContainer:
	var pc := PanelContainer.new()
	var sb := styl_plaski(FIOLET, FIOLET, 0, 6)
	sb.content_margin_top = 3
	sb.content_margin_bottom = 3
	pc.add_theme_stylebox_override("panel", sb)
	pc.add_child(etykieta(tekst, rozmiar, "plakat", Color(0.98, 0.95, 1.0), false))
	return pc


static func przyciemnienie(alfa: float = 0.55) -> ColorRect:
	var c := ColorRect.new()
	c.color = Color(0.08, 0.05, 0.02, alfa)
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	c.mouse_filter = Control.MOUSE_FILTER_STOP
	return c


static func obraz(tex: Texture2D, rect: Rect2) -> TextureRect:
	var t := TextureRect.new()
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.texture = tex
	t.position = rect.position
	t.size = rect.size
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t


static func umiesc(c: Control, rect: Rect2) -> Control:
	c.position = rect.position
	c.size = rect.size
	return c


static func przycisk_tekst(tekst: String, rozmiar: int = 18, akcja: Callable = Callable(), rodzaj: String = "szeryf") -> Button:
	## Przycisk z zawijanym tekstem (dłuższe odpowiedzi w quizach i minigrach).
	var b := przycisk("", rozmiar, akcja)
	var l := etykieta(tekst, rozmiar, rodzaj, ATRAMENT, true)
	l.set_anchors_preset(Control.PRESET_FULL_RECT)
	l.offset_left = 14
	l.offset_right = -14
	l.offset_top = 4
	l.offset_bottom = -4
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.name = "Tekst"
	b.add_child(l)
	return b
