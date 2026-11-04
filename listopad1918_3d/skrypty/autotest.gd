extends RefCounted
## Automatyczne testy uruchamiane poleceniem:
##   godot --headless --path . -- --autotest
## Sprawdzają dane, przechodzą grę na poziomie logiki, a potem przez prawdziwe
## sceny 3D, nakładki i minigry. Kod wyjścia 0 = wszystko w porządku.

const Logika = preload("res://skrypty/logika.gd")
const Rozmowa = preload("res://skrypty/rozmowa.gd")

var bledy: Array = []
var main = null


func sprawdz(warunek: bool, opis: String) -> void:
	if not warunek:
		bledy.append(opis)
		printerr("BŁĄD: " + opis)


# ------------------------------------------------------------------ dane
func test_dane() -> void:
	sprawdz(Dane.rozdzialy.size() == 7, "7 rozdziałów")
	sprawdz(Dane.lokacje.size() == 14, "14 lokacji")
	sprawdz(Dane.historyczne.size() == 12, "12 postaci historycznych")
	sprawdz(Dane.mity.size() == 10, "10 mitów")
	for pid in Dane.postacie:
		sprawdz(Dane.tex_postac(pid) != null, "tekstura postaci " + pid)
		sprawdz(Dane.tex_portret(pid) != null, "portret " + pid)
	for p in Dane.przedmioty:
		sprawdz(Dane.tex_ikona(p) != null, "ikona " + p)
	for n in ["papier", "papier_ciemny", "mapa", "wyjscie", "sztaluga"]:
		sprawdz(Dane.tex_ui(n) != null, "tekstura UI " + n)


# ------------------------------------------------------------------ logika
func przeprowadz_rozmowe(logika, did: String) -> Array:
	var r = Rozmowa.new(logika, did)
	var odw := {r.wezel_id: true}
	var kroki := 0
	while not r.zakonczona():
		kroki += 1
		if kroki > 200:
			sprawdz(false, "dialog się nie kończy: " + did)
			break
		var opcje: Array = r.opcje()
		if opcje.is_empty():
			r.dalej()
		else:
			var wybor := opcje.size() - 1
			for i in opcje.size():
				if not odw.has(str(opcje[i]["dalej"])):
					wybor = i
					break
			r.wybierz(wybor)
		odw[r.wezel_id] = true
	return r.odbierz_zdarzenia()


func obsluz(logika, zdarzenia: Array) -> void:
	var kolejka := zdarzenia.duplicate()
	while not kolejka.is_empty():
		var z: Array = kolejka.pop_front()
		match z[0]:
			Logika.DIALOG:
				kolejka.append_array(przeprowadz_rozmowe(logika, z[1]))
			Logika.MINIGRA:
				kolejka.append_array(logika.wygrana_minigry(z[1]))
			Logika.MIT:
				logika.odpowiedz_mit(z[1], int(Dane.mity[z[1]]["dobra"]))
			Logika.KONIEC_ROZDZIALU:
				logika.nastepny_rozdzial()


func test_logika() -> void:
	var logika = Logika.new()
	for krok in Dane.solucja:
		if logika.ukonczona:
			break
		var zd: Array
		if krok[0] == "klik":
			zd = logika.kliknij(krok[1])
		else:
			zd = logika.uzyj(krok[1], krok[2])
		obsluz(logika, zd)
	sprawdz(logika.ukonczona, "logika: gra ukończona")
	sprawdz(logika.fakty.size() == Dane.fakty.size(), "logika: wszystkie fakty (%d/%d)" % [logika.fakty.size(), Dane.fakty.size()])
	sprawdz(logika.mity.size() == 10, "logika: wszystkie mity")
	sprawdz(logika.poznani.size() == 12, "logika: wszystkie postacie")


# ------------------------------------------------------------------ uruchomienie
func uruchom(p_main) -> int:
	main = p_main
	print("== Autotest: dane ==")
	test_dane()
	print("== Autotest: logika ==")
	test_logika()
	if main != null and main.has_method("autotest_interfejsu"):
		print("== Autotest: sceny 3D i interfejs ==")
		await main.autotest_interfejsu(self)
	if bledy.is_empty():
		print("AUTOTEST OK")
		return 0
	print("AUTOTEST: %d błędów" % bledy.size())
	for b in bledy:
		print("  - " + str(b))
	return 1
