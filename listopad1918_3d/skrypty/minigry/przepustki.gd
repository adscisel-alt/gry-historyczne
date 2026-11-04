extends "res://skrypty/minigry/baza.gd"
## Rozdział 4: weryfikacja przepustek na peron Dworca Wiedeńskiego.

var indeks := 0
var poprawne := 0
var koniec := false
var dokument: Control
var licznik: Label
var b_tak: Button
var b_nie: Button
var b_znowu: Button


func _init(p_main) -> void:
	super(p_main)
	gid = "przepustki"
	tytul = "Bramka na peron — 10 XI 1918, godz. 6.40"
	instrukcja = "Sprawdź każdą przepustkę z zasadami komendanta Koca i listą powitalną. Przepuść albo zatrzymaj. Musisz ocenić poprawnie co najmniej %d z %d dokumentów." % [int(M["przepustki_prog"]), M["przepustki"].size()]


static func wazna(doc: Array) -> bool:
	return doc[1] == "10 XI 1918" and doc[2] in ["POW", "Rada Regencyjna"] and doc[0] in Dane.minigry["lista_powitalna"] and doc[3] == true


static func powod(doc: Array) -> String:
	if doc[1] != "10 XI 1918":
		return "zła data"
	if not doc[2] in ["POW", "Rada Regencyjna"]:
		return "niemiecka pieczęć"
	if not doc[0] in Dane.minigry["lista_powitalna"]:
		return "brak na liście"
	if doc[3] != true:
		return "brak podpisu"
	return ""


func buduj() -> void:
	var z := Motyw.karta(Rect2(40, 130, 360, 250))
	gra.add_child(z)
	dodaj(Motyw.etykieta("Zasady komendanta Koca", 18, "plakat"), Rect2(20, 14, 320, 26), z)
	for i in M["zasady_przepustek"].size():
		dodaj(Motyw.etykieta("• " + str(M["zasady_przepustek"][i]), 17), Rect2(20, 50 + i * 34, 330, 30), z)
	var l := Motyw.karta(Rect2(40, 400, 360, 250))
	gra.add_child(l)
	dodaj(Motyw.etykieta("Lista powitalna", 18, "plakat"), Rect2(20, 14, 320, 26), l)
	for i in M["lista_powitalna"].size():
		dodaj(Motyw.etykieta(str(M["lista_powitalna"][i]), 18, "reka"), Rect2(30 + (i % 2) * 160, 50 + (i / 2) * 34, 150, 30), l)
	licznik = Motyw.etykieta("", 18, "szeryf", Motyw.ATRAMENT_JASNY, false)
	dodaj(licznik, Rect2(500, 126, 600, 26), gra)
	dokument = Control.new()
	dodaj(dokument, Rect2(500, 160, 600, 380), gra)
	b_tak = Motyw.przycisk("Przepuść ✔", 22, func(): decyzja(true))
	dodaj(b_tak, Rect2(500, 560, 200, 56), gra)
	b_nie = Motyw.przycisk("Zatrzymaj ✖", 22, func(): decyzja(false))
	dodaj(b_nie, Rect2(720, 560, 200, 56), gra)
	b_znowu = Motyw.przycisk("Jeszcze raz", 22, func(): reset())
	dodaj(b_znowu, Rect2(560, 560, 300, 56), gra)
	dodaj(Motyw.etykieta("klawisze: T = przepuść, N = zatrzymaj", 14, "szeryf", Motyw.ATRAMENT_JASNY, false), Rect2(940, 580, 300, 24), gra)
	reset()


func reset() -> void:
	indeks = 0
	poprawne = 0
	koniec = false
	pokaz()


func pokaz() -> void:
	for c in dokument.get_children():
		c.queue_free()
	b_znowu.visible = koniec
	b_tak.visible = not koniec and indeks < M["przepustki"].size()
	b_nie.visible = b_tak.visible
	licznik.text = "Dokument %d / %d     Poprawnie: %d" % [mini(indeks + 1, M["przepustki"].size()), M["przepustki"].size(), poprawne]
	if indeks >= M["przepustki"].size():
		return
	var doc: Array = M["przepustki"][indeks]
	var k := Motyw.karta(Rect2(0, 0, 600, 370))
	k.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dokument.add_child(k)
	k.draw.connect(_rysuj_dokument.bind(k, doc))
	dodaj(Motyw.etykieta("PRZEPUSTKA NA PERON", 26, "plakat", Motyw.ATRAMENT, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 22, 600, 36), k)
	dodaj(Motyw.etykieta("Dworzec Wiedeński — powitanie", 16, "szeryf", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 60, 600, 24), k)
	dodaj(Motyw.etykieta("Nazwisko:", 18, "szeryf", Motyw.ATRAMENT_JASNY, false), Rect2(40, 112, 140, 30), k)
	dodaj(Motyw.etykieta(str(doc[0]), 26, "reka", Motyw.ATRAMENT, false), Rect2(180, 104, 400, 36), k)
	dodaj(Motyw.etykieta("Data:", 18, "szeryf", Motyw.ATRAMENT_JASNY, false), Rect2(40, 162, 140, 30), k)
	dodaj(Motyw.etykieta(str(doc[1]), 26, "reka", Motyw.ATRAMENT, false), Rect2(180, 154, 400, 36), k)
	dodaj(Motyw.etykieta("Podpis:", 18, "szeryf", Motyw.ATRAMENT_JASNY, false), Rect2(40, 216, 140, 30), k)
	if doc[3] != true:
		dodaj(Motyw.etykieta("……………………", 18, "szeryf", Motyw.ATRAMENT_JASNY, false), Rect2(180, 216, 300, 30), k)


func _rysuj_dokument(k: Control, doc: Array) -> void:
	var pieczec := str(doc[2])
	Motyw.stempel(k, Vector2(480, 270), pieczec.to_upper().substr(0, 16), 62, Motyw.STEMPEL if pieczec != "Generalgouvernement" else Motyw.ATRAMENT)
	if doc[3] == true:
		var pts := PackedVector2Array()
		for i in 12:
			pts.append(Vector2(190 + i * 12, 230 + (8 if i % 2 else -6)))
		k.draw_polyline(pts, Motyw.ATRAMENT, 2.0)


func decyzja(przepusc: bool) -> void:
	if koniec or indeks >= M["przepustki"].size():
		return
	var doc: Array = M["przepustki"][indeks]
	var w := wazna(doc)
	if przepusc == w:
		poprawne += 1
		info("Dobrze! " + ("Przepustka w porządku." if w else "Zatrzymana: " + powod(doc) + "."))
	else:
		info("Ups! " + ("Ta przepustka była dobra." if w else "Trzeba było zatrzymać: " + powod(doc) + "."), false)
	main.dzwiek("stempel")
	indeks += 1
	if indeks >= M["przepustki"].size():
		if poprawne >= int(M["przepustki_prog"]):
			pokaz()
			wygraj()
			return
		koniec = true
		info("Wynik %d/%d — za mało. Koc wzdycha i podaje ci stos jeszcze raz." % [poprawne, M["przepustki"].size()], false)
	pokaz()


func klawisz_gry(k: int) -> void:
	if k == KEY_T:
		decyzja(true)
	elif k == KEY_N:
		decyzja(false)
