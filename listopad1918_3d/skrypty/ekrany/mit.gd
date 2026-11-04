extends "res://skrypty/ekrany/ekran.gd"
## Mit czy fakt? — quiz Damiana obalający popularne mity o 1918 r.

var mid := ""
var mit: Dictionary
var odpowiedz := -1
var dobrze := false
var karta_panel: Panel
var przyciski: Array = []
var wynik_box: Control


func _init(p_main, p_mid: String) -> void:
	super(p_main)
	typ = "mit"
	mid = p_mid
	mit = Dane.mity[mid]


func _ready() -> void:
	add_child(Motyw.przyciemnienie(0.6))
	karta_panel = Motyw.karta(Rect2(160, 50, 960, 620))
	karta_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(karta_panel)
	karta_panel.draw.connect(_rysuj_stempel)
	var nr := Dane.mity.keys().find(mid) + 1
	dodaj(Motyw.etykieta_fiolet("Damian sprawdza mit nr %d z 10" % nr, 16), Rect2(36, 28, 0, 0), karta_panel)
	dodaj(Motyw.etykieta("MIT CZY FAKT?", 34, "plakat", Motyw.ATRAMENT, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 70, 960, 46), karta_panel)
	dodaj(Motyw.etykieta("„" + str(mit["mit"]) + "”", 24, "reka", Motyw.ATRAMENT, true, HORIZONTAL_ALIGNMENT_CENTER), Rect2(80, 124, 800, 110), karta_panel)
	for i in 3:
		var nr_i := i
		var b := Motyw.przycisk_tekst("%d. %s" % [i + 1, mit["opcje"][i]], 17, func(): wybierz(nr_i))
		dodaj(b, Rect2(70, 262 + i * 76, 820, 62), karta_panel)
		przyciski.append(b)
	wynik_box = Control.new()
	wynik_box.visible = false
	wynik_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dodaj(wynik_box, Rect2(0, 0, 960, 620), karta_panel)


func wybierz(i: int) -> void:
	if odpowiedz >= 0:
		return
	odpowiedz = i
	dobrze = main.logika.odpowiedz_mit(mid, i)
	main.dzwiek("stempel" if dobrze else "blad")
	for b in przyciski:
		b.visible = false
	var dobra := str(mit["opcje"][int(mit["dobra"])])
	dodaj(Motyw.etykieta("Prawda: " + dobra, 21, "plakat"), Rect2(80, 250, 680, 80), wynik_box)
	dodaj(Motyw.etykieta(str(mit["wyjasnienie"]), 19), Rect2(80, 340, 800, 160), wynik_box)
	if mit.get("fakt") != null:
		dodaj(Motyw.etykieta("Źródło: " + str(Dane.fakty[mit["fakt"]]["zrodlo"]), 15, "szeryf", Motyw.ATRAMENT_JASNY), Rect2(80, 510, 800, 50), wynik_box)
	dodaj(Motyw.etykieta("▸ kliknij, aby zapisać w dzienniku", 16, "reka", Motyw.ATRAMENT_JASNY, false), Rect2(640, 576, 300, 24), wynik_box)
	wynik_box.visible = true
	karta_panel.queue_redraw()


func _rysuj_stempel() -> void:
	if odpowiedz >= 0:
		Motyw.stempel(karta_panel, Vector2(840, 300), "OBALONY!" if dobrze else "SPRAWDŹ JESZCZE RAZ", 62,
			Motyw.STEMPEL if dobrze else Motyw.ATRAMENT_JASNY)


func klik_tla() -> void:
	if odpowiedz >= 0 and czas > 0.3:
		zamknij()


func klawisz(k: int) -> void:
	if odpowiedz < 0 and k >= KEY_1 and k <= KEY_3:
		wybierz(k - KEY_1)
	elif odpowiedz >= 0 and k in [KEY_SPACE, KEY_ENTER]:
		zamknij()
