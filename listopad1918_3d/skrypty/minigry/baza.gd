extends "res://skrypty/ekrany/ekran.gd"
## Baza minigier: tytuł, instrukcja, „Wróć”, pasek komunikatu, ekran sukcesu.

var gid := ""
var tytul := ""
var instrukcja := ""
var wygrana := false
var _czas_wygranej := 0.0
var _komunikat: Label
var _komunikat_panel: PanelContainer
var _sukces: Control
var gra: Control          # kontener na elementy konkretnej minigry
var M: Dictionary         # Dane.minigry


func _init(p_main) -> void:
	super(p_main)
	typ = "minigra"
	modalny = false
	M = Dane.minigry


func _ready() -> void:
	tlo_papier(true)
	dodaj(Motyw.etykieta(tytul, 30, "plakat", Motyw.ATRAMENT, false), Rect2(40, 14, 1060, 40))
	dodaj(Motyw.etykieta(instrukcja, 16, "szeryf", Motyw.ATRAMENT_JASNY), Rect2(40, 56, 1060, 60))
	gra = Control.new()
	gra.mouse_filter = Control.MOUSE_FILTER_PASS
	dodaj(gra, Rect2(0, 0, 1280, 720))
	_komunikat_panel = PanelContainer.new()
	_komunikat_panel.add_theme_stylebox_override("panel", Motyw.styl_plaski(Color(0.93, 0.9, 0.82)))
	_komunikat = Motyw.etykieta("", 17)
	_komunikat_panel.add_child(_komunikat)
	_komunikat_panel.visible = false
	dodaj(_komunikat_panel, Rect2(40, 664, 1200, 44))
	dodaj(Motyw.przycisk("Wróć", 18, func(): anuluj()), Rect2(1110, 16, 150, 44))
	buduj()


func buduj() -> void:
	pass


func info(t: String, dobry: bool = true) -> void:
	_komunikat.text = t
	_komunikat_panel.visible = t != ""
	_komunikat_panel.add_theme_stylebox_override("panel", Motyw.styl_plaski(Color(0.93, 0.9, 0.82), Motyw.ATRAMENT_JASNY if dobry else Motyw.STEMPEL, 2))
	main.dzwiek("klik" if dobry else "blad")


func wygraj() -> void:
	if wygrana:
		return
	wygrana = true
	_czas_wygranej = czas
	main.dzwiek("sukces")
	_sukces = Control.new()
	_sukces.set_anchors_preset(Control.PRESET_FULL_RECT)
	_sukces.size = Vector2(1280, 720)
	_sukces.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_sukces.add_child(Motyw.przyciemnienie(0.45))
	(_sukces.get_child(0) as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
	var k := Motyw.karta(Rect2(390, 230, 500, 240))
	k.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_sukces.add_child(k)
	k.draw.connect(func(): Motyw.stempel(k, Vector2(250, 150), "ZALICZONE", 54))
	dodaj(Motyw.etykieta("Udało się!", 44, "plakat", Motyw.ATRAMENT, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 30, 500, 60), k)
	dodaj(Motyw.etykieta("▸ kliknij, aby wrócić do pocztówki", 16, "reka", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 200, 500, 26), k)
	add_child(_sukces)


func zakoncz() -> void:
	main.zdejmij(self)
	main.na_poczatek(main.logika.wygrana_minigry(gid))


func anuluj() -> void:
	main.zdejmij(self)


func _input(e: InputEvent) -> void:
	if wygrana and na_wierzchu() and czas - _czas_wygranej > 0.4:
		if (e is InputEventMouseButton and e.pressed) or (e is InputEventKey and e.pressed and e.keycode in [KEY_SPACE, KEY_ENTER]):
			get_viewport().set_input_as_handled()
			zakoncz()


func klawisz(k: int) -> void:
	if k == KEY_ESCAPE and not wygrana:
		anuluj()
	else:
		klawisz_gry(k)


func klawisz_gry(_k: int) -> void:
	pass
