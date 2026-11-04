extends "res://skrypty/ekrany/ekran.gd"
## Zakończenie: album z 12 postaciami i przesłanie „każdy wniósł co innego”.


func _init(p_main) -> void:
	super(p_main)
	typ = "zakonczenie"
	modalny = false


func _ready() -> void:
	tlo_papier(true)
	var k := Motyw.karta(Rect2(60, 26, 1160, 600))
	k.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(k)
	k.draw.connect(func(): Motyw.stempel(k, Vector2(1060, 70), "28 XI 1918", 48))
	dodaj(Motyw.etykieta("Album skończony", 44, "plakat", Motyw.ATRAMENT, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 24, 1160, 60), k)
	for i in Dane.historyczne.size():
		var pid: String = Dane.historyczne[i]
		var x := 50 + (i % 6) * 180
		var y := 96 + (i / 6) * 170
		dodaj(Motyw.obraz(Dane.tex_portret(pid), Rect2()), Rect2(x + 30, y, 100, 120), k)
		dodaj(Motyw.etykieta(str(Dane.postacie[pid]["imie"]), 13, "plakat", Motyw.ATRAMENT, true, HORIZONTAL_ALIGNMENT_CENTER), Rect2(x, y + 122, 160, 40), k)
	var tekst := ("Janek przeszedł przez cały listopad 1918 roku. Widział, że niepodległość nie spadła z nieba jednego dnia: "
		+ "Witos przejął Galicję, Rada Regencyjna przygotowała urzędy, Daszyński spisał reformy, Piłsudski zbudował wojsko i władzę, "
		+ "Dmowski i Paderewski zdobywali sojuszników, Korfanty upominał się o zabór pruski, a kobiety wywalczyły prawo głosu. "
		+ "Każdy wniósł co innego — i często się kłócili. Tak też buduje się państwo.")
	dodaj(Motyw.etykieta(tekst, 18, "szeryf", Motyw.ATRAMENT, true, HORIZONTAL_ALIGNMENT_CENTER), Rect2(70, 440, 1020, 110), k)
	var l = main.logika
	var obalone := 0
	for v in l.mity.values():
		if v == true:
			obalone += 1
	dodaj(Motyw.etykieta("Fakty: %d/%d   •   Mity obalone za pierwszym razem: %d/10   •   Postacie: %d/12" % [
		l.fakty.size(), Dane.fakty.size(), obalone, l.poznani.size()], 17, "szeryf", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER), Rect2(0, 556, 1160, 26), k)
	dodaj(Motyw.przycisk("Dziennik", 20, func(): main.otworz_dziennik()), Rect2(380, 646, 240, 50))
	dodaj(Motyw.przycisk("Menu główne", 20, func(): main.do_menu()), Rect2(660, 646, 240, 50))
	dodaj(Motyw.etykieta_fiolet("Damian: „Sprawdzaj źródła. Zawsze.”", 14), Rect2(930, 656, 0, 0))
