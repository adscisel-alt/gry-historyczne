extends "res://skrypty/ekrany/ekran.gd"
## Podsumowanie ukończonego rozdziału.


func _init(p_main) -> void:
	super(p_main)
	typ = "podsumowanie"


func _ready() -> void:
	add_child(Motyw.przyciemnienie(0.65))
	var r: Dictionary = main.logika.dane_rozdzialu()
	var k := Motyw.karta(Rect2(240, 120, 800, 460))
	k.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(k)
	k.draw.connect(func(): Motyw.stempel(k, Vector2(700, 70), "ZWERYFIKOWANO", 48))
	dodaj(Motyw.etykieta("Rozdział %d ukończony" % int(r["numer"]), 36, "plakat", Motyw.ATRAMENT, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 50, 800, 50), k)
	dodaj(Motyw.etykieta(str(r["tytul"]), 28, "reka", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 104, 800, 40), k)
	dodaj(Motyw.etykieta(str(r["podsumowanie"]), 22, "szeryf", Motyw.ATRAMENT, true, HORIZONTAL_ALIGNMENT_CENTER), Rect2(60, 168, 680, 120), k)
	var l = main.logika
	var obalone := 0
	for v in l.mity.values():
		if v == true:
			obalone += 1
	dodaj(Motyw.etykieta("Fakty w dzienniku: %d / %d     Mity obalone: %d / 10     Postacie: %d / 12" % [
		l.fakty.size(), Dane.fakty.size(), obalone, l.poznani.size()], 18, "szeryf", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 320, 800, 30), k)
	dodaj(Motyw.etykieta("Gra zapisana automatycznie. ▸ kliknij", 16, "reka", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 400, 800, 26), k)


func klik_tla() -> void:
	if czas > 0.3:
		main.zdejmij(self)
		main.nastepny_rozdzial()


func klawisz(k: int) -> void:
	if k in [KEY_SPACE, KEY_ENTER]:
		klik_tla()
