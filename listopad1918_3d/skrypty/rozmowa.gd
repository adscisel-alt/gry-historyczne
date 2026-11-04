extends RefCounted
## Przebieg jednego drzewka dialogowego (port z wersji 2D).

var logika
var did: String
var dane: Dictionary
var wezel_id: String = ""
var zdarzenia: Array = []


func _init(p_logika, p_did: String) -> void:
	logika = p_logika
	did = p_did
	dane = Dane.dialogi[did]
	przejdz(str(dane["start"]))


func wezel() -> Dictionary:
	return dane["wezly"][wezel_id]


func zakonczona() -> bool:
	return wezel_id == "koniec"


func przejdz(wid: String) -> void:
	for _i in 20:
		if wid == "koniec":
			wezel_id = "koniec"
			return
		var w: Dictionary = dane["wezly"][wid]
		var przekierowanie := ""
		for j in w.get("jesli", []):
			if logika.warunki(j["gdy"]):
				przekierowanie = str(j["dalej"])
				break
		if przekierowanie != "":
			wid = przekierowanie
			continue
		wezel_id = wid
		var kto := str(w.get("kto", ""))
		if kto in Dane.historyczne:
			logika.efekt("poznaj:" + kto)
		zdarzenia.append_array(logika.efekty(w.get("efekty")))
		return
	push_error("Zapętlone przekierowania w dialogu " + did)


func opcje() -> Array:
	if zakonczona():
		return []
	var wynik: Array = []
	for o in wezel().get("opcje", []):
		if logika.warunki(o.get("gdy")):
			wynik.append(o)
	return wynik


func wybierz(i: int) -> void:
	var o: Dictionary = opcje()[i]
	zdarzenia.append_array(logika.efekty(o.get("efekty")))
	przejdz(str(o["dalej"]))


func dalej() -> void:
	if not opcje().is_empty():
		return
	przejdz(str(wezel().get("dalej", "koniec")))


func odbierz_zdarzenia() -> Array:
	var z := zdarzenia
	zdarzenia = []
	return z
