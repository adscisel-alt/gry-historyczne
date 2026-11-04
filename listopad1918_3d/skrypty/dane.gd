extends Node
## Autoload „Dane”: treść gry z dane/gra.json (eksport z wersji 2D) i tekstury.

var rozdzialy: Array = []
var lokacje: Dictionary = {}
var przedmioty: Dictionary = {}
var dialogi: Dictionary = {}
var postacie: Dictionary = {}
var historyczne: Array = []
var fakty: Dictionary = {}
var mity: Dictionary = {}
var prawa_kobiet: Dictionary = {}
var zabory: Dictionary = {}
var miasta: Dictionary = {}
var minigry: Dictionary = {}
var solucja: Array = []
var grafika: Dictionary = {}

var _tekstury: Dictionary = {}


func _init() -> void:
	var tekst := FileAccess.get_file_as_string("res://dane/gra.json")
	var d = JSON.parse_string(tekst)
	if typeof(d) != TYPE_DICTIONARY:
		push_error("Nie można wczytać dane/gra.json")
		return
	rozdzialy = d["rozdzialy"]
	lokacje = d["lokacje"]
	przedmioty = d["przedmioty"]
	dialogi = d["dialogi"]
	postacie = d["postacie"]
	historyczne = d["historyczne"]
	fakty = d["fakty"]
	mity = d["mity"]
	prawa_kobiet = d["prawa_kobiet"]
	zabory = d["zabory"]
	miasta = d["miasta"]
	minigry = d["minigry"]
	solucja = d["solucja"]
	grafika = d["grafika"]


func imie(pid: String) -> String:
	if pid == "rada":
		return "Rada Regencyjna"
	return str(postacie[pid]["imie"])


func indeks_rozdzialu(rid: String) -> int:
	for i in rozdzialy.size():
		if rozdzialy[i]["id"] == rid:
			return i
	return -1


func _tekstura(sciezka: String) -> Texture2D:
	if not _tekstury.has(sciezka):
		_tekstury[sciezka] = load(sciezka)
	return _tekstury[sciezka]


func tex_postac(pid: String) -> Texture2D:
	return _tekstura("res://zasoby/postacie/%s.png" % pid)


func tex_portret(pid: String) -> Texture2D:
	if pid == "rada":
		pid = "kakowski"
	return _tekstura("res://zasoby/portrety/%s.png" % pid)


func tex_ikona(p: String) -> Texture2D:
	return _tekstura("res://zasoby/ikony/%s.png" % p)


func tex_ui(nazwa: String) -> Texture2D:
	return _tekstura("res://zasoby/ui/%s.png" % nazwa)
