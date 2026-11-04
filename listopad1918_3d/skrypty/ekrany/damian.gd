extends "res://skrypty/ekrany/ekran.gd"
## Komentarz narratora — Damiana Ściseła.

var tresc := ""


func _init(p_main, p_tresc: String) -> void:
	super(p_main)
	typ = "damian"
	tresc = p_tresc


func _ready() -> void:
	add_child(Motyw.przyciemnienie(0.4))
	var k := Motyw.karta(Rect2(190, 150, 900, 300))
	k.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(k)
	dodaj(Motyw.obraz(Dane.tex_portret("damian"), Rect2()), Rect2(30, 30, 140, 168), k)
	dodaj(Motyw.etykieta_fiolet("Damian Ściseł weryfikuje", 15), Rect2(190, 26, 0, 0), k)
	dodaj(Motyw.etykieta(tresc, 21), Rect2(190, 66, 680, 200), k)
	dodaj(Motyw.etykieta("▸ dalej", 16, "reka", Motyw.ATRAMENT_JASNY, false), Rect2(800, 262, 90, 24), k)


func klik_tla() -> void:
	if czas > 0.2:
		zamknij()


func klawisz(k: int) -> void:
	if k in [KEY_SPACE, KEY_ENTER, KEY_ESCAPE]:
		klik_tla()
