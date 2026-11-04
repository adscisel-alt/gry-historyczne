extends "res://skrypty/ekrany/ekran.gd"
## Menu główne.


func _init(p_main) -> void:
	super(p_main)
	typ = "menu"
	modalny = false


func _ready() -> void:
	tlo_papier(true)
	var rng := RandomNumberGenerator.new()
	rng.seed = 1918
	var postacie: Array = Dane.historyczne.duplicate()
	for i in postacie.size():
		var j := rng.randi_range(0, postacie.size() - 1)
		var tmp = postacie[i]
		postacie[i] = postacie[j]
		postacie[j] = tmp
	for i in postacie.size():
		var tex := Dane.tex_postac(postacie[i])
		var h := tex.get_height() * 0.42
		dodaj(Motyw.obraz(tex, Rect2(20 + i * 82, 720 - h + 10, tex.get_width() * 0.42, h)), Rect2(20 + i * 82, 720 - h + 10, tex.get_width() * 0.42, h))
	var dam := Dane.tex_postac("damian")
	dodaj(Motyw.obraz(dam, Rect2()), Rect2(1110, 330, dam.get_width() * 0.62, dam.get_height() * 0.62))
	var k := Motyw.karta(Rect2(300, 40, 680, 260))
	add_child(k)
	k.draw.connect(func(): Motyw.stempel(k, Vector2(620, 205), "WARSZAWA 1918", 44))
	dodaj(Motyw.etykieta("LISTOPAD 1918", 64, "plakat", Motyw.ATRAMENT, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 40, 680, 80), k)
	dodaj(Motyw.etykieta("Pocztówki z niepodległości", 30, "reka", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 118, 680, 40), k)
	dodaj(Motyw.etykieta("przygodówka 3D w 7 rozdziałach • 31 X – 28 XI 1918", 18, "szeryf", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 166, 680, 30), k)
	dodaj(Motyw.etykieta("Gra edukacyjna dla 11–15 lat. Janek i Damian Ściseł to postacie fikcyjne.", 14, "szeryf", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 212, 680, 24), k)
	var opcje := [["Nowa gra", func(): main.nowa_gra()]]
	if main.jest_zapis():
		opcje.append(["Kontynuuj", func(): main.kontynuuj()])
	opcje.append(["Pełny ekran (F11)", func(): main.przelacz_ekran()])
	opcje.append(["Wyjście", func(): main.get_tree().quit()])
	for i in opcje.size():
		dodaj(Motyw.przycisk(opcje[i][0], 22, opcje[i][1]), Rect2(490, 318 + i * 58, 300, 48))


func klawisz(k: int) -> void:
	if k == KEY_ENTER:
		main.nowa_gra()
