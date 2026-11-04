extends "res://skrypty/minigry/baza.gd"
## Rozdział 7: quiz o prawach wyborczych kobiet (zebranie Ligi Kobiet).

var pytanie := 0
var dobre := 0
var przegrana := false
var pyt_l: Label
var nr_l: Label
var wynik_l: Label
var odp_ui: Array = []
var b_znowu: Button


func _init(p_main) -> void:
	super(p_main)
	gid = "prawa_kobiet"
	tytul = "Zebranie Ligi Kobiet — 28 XI 1918"
	instrukcja = "Zofia Moraczewska sprawdza, czy uważałeś. Odpowiedz poprawnie na co najmniej %d z %d pytań." % [int(M["quiz_kobiet_prog"]), M["quiz_kobiet"].size()]


func buduj() -> void:
	dodaj(Motyw.obraz(Dane.tex_portret("moraczewska"), Rect2()), Rect2(70, 140, 180, 216), gra)
	wynik_l = Motyw.etykieta("", 20, "plakat", Motyw.ATRAMENT, false)
	dodaj(wynik_l, Rect2(100, 370, 200, 30), gra)
	nr_l = Motyw.etykieta("", 16, "szeryf", Motyw.ATRAMENT_JASNY, false)
	dodaj(nr_l, Rect2(320, 140, 400, 24), gra)
	pyt_l = Motyw.etykieta("", 28, "reka")
	dodaj(pyt_l, Rect2(320, 170, 880, 130), gra)
	for i in 3:
		var nr: int = i
		var b := Motyw.przycisk_tekst("", 21, func(): odpowiedz(nr), "plakat")
		dodaj(b, Rect2(320, 320 + i * 78, 820, 64), gra)
		odp_ui.append(b)
	b_znowu = Motyw.przycisk("Jeszcze raz", 20, func(): reset())
	dodaj(b_znowu, Rect2(490, 590, 300, 50), gra)
	reset()


func reset() -> void:
	pytanie = 0
	dobre = 0
	przegrana = false
	info("")
	odswiez()


func odswiez() -> void:
	wynik_l.text = "Wynik: %d" % dobre
	var trwa: bool = not przegrana and pytanie < M["quiz_kobiet"].size()
	for b in odp_ui:
		b.visible = trwa
	b_znowu.visible = przegrana
	if trwa:
		var q: Array = M["quiz_kobiet"][pytanie]
		nr_l.text = "Pytanie %d / %d" % [pytanie + 1, M["quiz_kobiet"].size()]
		pyt_l.text = str(q[0])
		for i in 3:
			odp_ui[i].get_node("Tekst").text = "%d. %s" % [i + 1, q[1][i]]
	else:
		nr_l.text = ""
		pyt_l.text = ""


func odpowiedz(i: int) -> void:
	if przegrana or pytanie >= M["quiz_kobiet"].size():
		return
	var q: Array = M["quiz_kobiet"][pytanie]
	var dobra := int(q[2])
	if i == dobra:
		dobre += 1
		info("Zgadza się! " + str(q[1][dobra]) + ".")
	else:
		info("Niestety. Poprawnie: " + str(q[1][dobra]) + ".", false)
	pytanie += 1
	if pytanie >= M["quiz_kobiet"].size():
		if dobre >= int(M["quiz_kobiet_prog"]):
			odswiez()
			wygraj()
			return
		przegrana = true
		info("Wynik %d/%d. Zajrzyj do dziennika (zakładka „Prawa kobiet”) i spróbuj jeszcze raz." % [dobre, M["quiz_kobiet"].size()], false)
	odswiez()


func klawisz_gry(k: int) -> void:
	if k >= KEY_1 and k <= KEY_3:
		odpowiedz(k - KEY_1)
