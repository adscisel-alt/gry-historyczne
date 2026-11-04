extends Control
## Baza ekranów i nakładek: pełny ekran, dostęp do main, obsługa „na wierzchu”.

const Motyw = preload("res://skrypty/motyw.gd")

var main = null
var typ := ""
var czas := 0.0
var modalny := true      # rysowany nad lokacją (true) czy pełny ekran (false)


func _init(p_main) -> void:
	main = p_main
	set_anchors_preset(Control.PRESET_FULL_RECT)
	size = Vector2(1280, 720)
	mouse_filter = Control.MOUSE_FILTER_STOP


func _process(delta: float) -> void:
	czas += delta


func na_wierzchu() -> bool:
	return main.gora() == self


func zamknij() -> void:
	main.zdejmij(self)


func tlo_papier(ciemny: bool = false) -> void:
	var t := TextureRect.new()
	t.texture = Dane.tex_ui("papier_ciemny" if ciemny else "papier")
	t.stretch_mode = TextureRect.STRETCH_TILE
	t.set_anchors_preset(Control.PRESET_FULL_RECT)
	t.size = Vector2(1280, 720)
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(t)


func dodaj(c: Control, rect: Rect2, rodzic: Control = null) -> Control:
	c.position = rect.position
	if rect.size != Vector2.ZERO:
		c.size = rect.size
	(rodzic if rodzic else self).add_child(c)
	return c


func _gui_input(e: InputEvent) -> void:
	if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT and na_wierzchu():
		klik_tla()
		accept_event()


func _unhandled_key_input(e: InputEvent) -> void:
	if e is InputEventKey and e.pressed and not e.echo and na_wierzchu():
		klawisz(e.keycode)


func klik_tla() -> void:
	pass


func klawisz(_k: int) -> void:
	pass
