extends "res://skrypty/ekrany/ekran.gd"
## Karta rozdziału (pocztówka z tytułem i wstępem Damiana).


func _init(p_main) -> void:
	super(p_main)
	typ = "karta"
	modalny = false


func _ready() -> void:
	tlo_papier(true)
	var r: Dictionary = main.logika.dane_rozdzialu()
	var k := Motyw.karta(Rect2(140, 50, 1000, 620))
	add_child(k)
	k.mouse_filter = Control.MOUSE_FILTER_IGNORE
	k.draw.connect(func(): Motyw.stempel(k, Vector2(920, 80), str(r["stempel"]), 46))
	dodaj(Motyw.etykieta("ROZDZIAŁ %d z 7" % int(r["numer"]), 26, "plakat", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 44, 1000, 36), k)
	dodaj(Motyw.etykieta(str(r["tytul"]), 54, "reka", Motyw.ATRAMENT, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 90, 1000, 70), k)
	dodaj(Motyw.etykieta("%s  •  %s" % [r["daty"], r["miejsce"]], 22, "szeryf", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 168, 1000, 30), k)
	var linia := ColorRect.new()
	linia.color = Color(0.45, 0.38, 0.28)
	dodaj(linia, Rect2(120, 214, 760, 2), k)
	dodaj(Motyw.obraz(Dane.tex_portret("damian"), Rect2()), Rect2(60, 250, 150, 180), k)
	dodaj(Motyw.etykieta_fiolet("Damian Ściseł, archiwista", 15), Rect2(48, 440, 0, 0), k)
	dodaj(Motyw.etykieta(str(r["intro"]), 21), Rect2(250, 250, 690, 300), k)
	var dalej := Motyw.etykieta("kliknij, aby wejść do pocztówki", 18, "reka", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER)
	dalej.name = "Dalej"
	dodaj(dalej, Rect2(0, 560, 1000, 30), k)


func _process(delta: float) -> void:
	super(delta)
	var d = find_child("Dalej", true, false)
	if d:
		d.modulate.a = 0.55 + 0.45 * sin(czas * 3.0)


func klik_tla() -> void:
	if czas > 0.3:
		main.rozpocznij_lokacje()


func klawisz(k: int) -> void:
	if k in [KEY_ENTER, KEY_SPACE]:
		klik_tla()
