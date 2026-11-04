extends RefCounted
## Logika gry (port z wersji 2D): stan, warunki, efekty, rozmowy, zapis.
## Zdarzenia dla prezentacji to tablice [rodzaj, argument].

const IDZ := "idz"
const DIALOG := "dialog"
const MINIGRA := "minigra"
const DAMIAN := "damian"
const MOW := "mow"
const MIT := "mit"
const KONIEC_ROZDZIALU := "koniec_rozdzialu"
const PRZEDMIOT := "przedmiot"
const FAKT := "fakt"

var flagi: Dictionary = {}
var ekwipunek: Array = []
var fakty: Array = []
var mity: Dictionary = {}      # id -> true/false/null
var poznani: Array = []
var rozdzial: int = 0
var lokacja: String = ""
var napiecie: int = 0
var ukonczona: bool = false


func _init() -> void:
	lokacja = str(Dane.rozdzialy[0]["start"])


# ------------------------------------------------------------------ warunki
func warunek(w: String) -> bool:
	var neg := w.begins_with("!")
	if neg:
		w = w.substr(1)
	var wynik := false
	if w.begins_with("napiecie>="):
		wynik = napiecie >= int(w.split(">=")[1])
	else:
		var i := w.find(":")
		var rodzaj := w.substr(0, i)
		var arg := w.substr(i + 1)
		match rodzaj:
			"flag":
				wynik = flagi.has(arg)
			"ma":
				wynik = arg in ekwipunek
			"fakt":
				wynik = arg in fakty
			"poznal":
				wynik = arg in poznani
			_:
				push_error("Nieznany warunek: " + w)
	return not wynik if neg else wynik


func warunki(lista) -> bool:
	if lista == null:
		return true
	for w in lista:
		if not warunek(str(w)):
			return false
	return true


# ------------------------------------------------------------------ efekty
func efekt(e: String) -> Array:
	var i := e.find(":")
	var rodzaj: String = e if i < 0 else e.substr(0, i)
	var arg: String = "" if i < 0 else e.substr(i + 1)
	var zd: Array = []
	match rodzaj:
		"flag":
			flagi[arg] = true
		"unflag":
			flagi.erase(arg)
		"daj":
			if not arg in ekwipunek:
				ekwipunek.append(arg)
				zd.append([PRZEDMIOT, arg])
		"zabierz":
			ekwipunek.erase(arg)
		"fakt":
			if not arg in fakty:
				fakty.append(arg)
				zd.append([FAKT, arg])
		"mit":
			if not mity.has(arg):
				mity[arg] = null
				zd.append([MIT, arg])
		"poznaj":
			if not arg in poznani:
				poznani.append(arg)
		"idz":
			lokacja = arg
			zd.append([IDZ, arg])
		"dialog":
			zd.append([DIALOG, arg])
		"minigra":
			zd.append([MINIGRA, arg])
		"damian":
			zd.append([DAMIAN, arg])
		"napiecie":
			if arg.begins_with("+"):
				napiecie += int(arg.substr(1))
			else:
				napiecie = int(arg)
		"koniec_rozdzialu":
			zd.append([KONIEC_ROZDZIALU, str(Dane.rozdzialy[rozdzial]["id"])])
		_:
			push_error("Nieznany efekt: " + e)
	return zd


func efekty(lista) -> Array:
	var zd: Array = []
	if lista == null:
		return zd
	for e in lista:
		zd.append_array(efekt(str(e)))
	return zd


# ------------------------------------------------------------------ mity i rozdziały
func odpowiedz_mit(mid: String, indeks: int) -> bool:
	var mit: Dictionary = Dane.mity[mid]
	var dobrze := indeks == int(mit["dobra"])
	mity[mid] = dobrze
	if mit.get("fakt") != null and not mit["fakt"] in fakty:
		fakty.append(mit["fakt"])
	return dobrze


func nastepny_rozdzial() -> bool:
	flagi["ukonczono_" + str(Dane.rozdzialy[rozdzial]["id"])] = true
	if rozdzial + 1 >= Dane.rozdzialy.size():
		ukonczona = true
		return false
	rozdzial += 1
	lokacja = str(Dane.rozdzialy[rozdzial]["start"])
	napiecie = 0
	return true


func dane_rozdzialu() -> Dictionary:
	return Dane.rozdzialy[rozdzial]


func dane_lokacji() -> Dictionary:
	return Dane.lokacje[lokacja]


# ------------------------------------------------------------------ hotspoty
func hotspoty() -> Array:
	var wynik: Array = []
	for h in Dane.lokacje[lokacja]["hotspoty"]:
		if warunki(h.get("widoczny")):
			wynik.append(h)
	return wynik


func hotspot(hid: String) -> Dictionary:
	for h in hotspoty():
		if h["id"] == hid:
			return h
	push_error("Brak widocznego hotspotu %s w %s" % [hid, lokacja])
	return {}


func _wykonaj(akcje) -> Array:
	for a in akcje:
		if warunki(a.get("gdy")):
			var zd: Array = []
			if a.get("mow"):
				zd.append([MOW, a["mow"]])
			zd.append_array(efekty(a.get("efekty")))
			return zd
	return []


func kliknij(hid: String) -> Array:
	var h := hotspot(hid)
	if h.is_empty():
		return []
	var zd := _wykonaj(h.get("akcje", []))
	if zd.is_empty():
		zd = [[MOW, h.get("patrz", "Nic ciekawego.")]]
	return zd


func uzyj(przedmiot: String, hid: String) -> Array:
	var h := hotspot(hid)
	if h.is_empty():
		return []
	if not przedmiot in ekwipunek:
		return [[MOW, "Nie mam tego przy sobie."]]
	var uz: Dictionary = h.get("uzyj", {})
	if uz.has(przedmiot):
		var zd := _wykonaj(uz[przedmiot])
		if not zd.is_empty():
			return zd
	return [[MOW, "%s i %s? To chyba nie tak." % [Dane.przedmioty[przedmiot]["nazwa"], h["nazwa"]]]]


func wygrana_minigry(gid: String) -> Array:
	return efekty(Dane.minigry["wygrana"][gid])


# ------------------------------------------------------------------ zapis
func do_slownika() -> Dictionary:
	return {"flagi": flagi.keys(), "ekwipunek": ekwipunek, "fakty": fakty, "mity": mity,
		"poznani": poznani, "rozdzial": rozdzial, "lokacja": lokacja, "ukonczona": ukonczona}


func ze_slownika(d: Dictionary) -> void:
	flagi = {}
	for f in d.get("flagi", []):
		flagi[str(f)] = true
	ekwipunek = d.get("ekwipunek", []).duplicate()
	fakty = d.get("fakty", []).duplicate()
	mity = d.get("mity", {}).duplicate()
	poznani = d.get("poznani", []).duplicate()
	rozdzial = int(d.get("rozdzial", 0))
	lokacja = str(d.get("lokacja", Dane.rozdzialy[rozdzial]["start"]))
	ukonczona = bool(d.get("ukonczona", false))


func zapisz(sciezka: String) -> void:
	var f := FileAccess.open(sciezka, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(do_slownika(), " "))


func wczytaj(sciezka: String) -> bool:
	if not FileAccess.file_exists(sciezka):
		return false
	var d = JSON.parse_string(FileAccess.get_file_as_string(sciezka))
	if typeof(d) != TYPE_DICTIONARY:
		return false
	ze_slownika(d)
	return true
