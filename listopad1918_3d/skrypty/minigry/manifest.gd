extends "res://skrypty/minigry/baza.gd"
## Rozdział 3: ułożenie manifestu lubelskiego (fałszywki do pieca).

var fragmenty: Array = []
var sloty: Array = []
var spalone: Array = []
var wybrany := -1
var zle_sloty: Dictionary = {}
var lista: VBoxContainer
var sloty_ui: Array = []
var piec: Button


func _init(p_main) -> void:
	super(p_main)
	gid = "manifest"
	tytul = "Kaszta zecerska: manifest lubelski"
	instrukcja = "Kliknij fragment, a potem miejsce w manifeście. Kolejność: kto ogłasza → ustrój → prawa obywateli → praca → ziemia → wezwanie. Dwa fałszywe zdania wrzuć do pieca."
	for i in M["manifest_fragmenty"].size():
		fragmenty.append(i)
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	for i in fragmenty.size():
		var j := rng.randi_range(0, fragmenty.size() - 1)
		var t = fragmenty[i]
		fragmenty[i] = fragmenty[j]
		fragmenty[j] = t
	for _i in M["manifest_sekcje"].size():
		sloty.append(-1)


func buduj() -> void:
	dodaj(Motyw.etykieta("Rozsypane fragmenty:", 16, "plakat", Motyw.ATRAMENT_JASNY, false), Rect2(40, 108, 400, 24), gra)
	lista = VBoxContainer.new()
	lista.add_theme_constant_override("separation", 6)
	dodaj(lista, Rect2(40, 134, 560, 460), gra)
	for i in M["manifest_sekcje"].size():
		var nr: int = i
		var b := Motyw.przycisk_tekst("", 15, func(): klik_slotu(nr), "maszyna")
		dodaj(b, Rect2(650, 132 + i * 76, 590, 68), gra)
		sloty_ui.append(b)
	piec = Motyw.przycisk("PIEC  (spalone: 0)", 20, func(): klik_pieca())
	dodaj(piec, Rect2(40, 600, 560, 56), gra)
	dodaj(Motyw.przycisk("Sprawdź i drukuj", 20, func(): sprawdz()), Rect2(900, 600, 330, 52), gra)
	odswiez()


func wolne() -> Array:
	var w: Array = []
	for f in fragmenty:
		if not f in sloty and not f in spalone:
			w.append(f)
	return w


func odswiez() -> void:
	for c in lista.get_children():
		c.queue_free()
	for f in wolne():
		var nr: int = f
		var b := Motyw.przycisk_tekst(str(M["manifest_fragmenty"][f][0]), 15, func(): wybierz(nr), "maszyna")
		b.custom_minimum_size = Vector2(560, 50)
		if f == wybrany:
			b.modulate = Color(0.85, 0.7, 1.0)
		lista.add_child(b)
	for i in sloty.size():
		var l: Label = sloty_ui[i].get_node("Tekst")
		var tekst := "%d. %s" % [i + 1, M["manifest_sekcje"][i]]
		if sloty[i] >= 0:
			tekst += "\n" + str(M["manifest_fragmenty"][sloty[i]][0])
		l.text = tekst
		sloty_ui[i].modulate = Color(1.0, 0.7, 0.65) if zle_sloty.has(i) else Color(1, 1, 1)
	piec.text = "PIEC  (spalone: %d)" % spalone.size()


func wybierz(f: int) -> void:
	wybrany = f
	odswiez()


func poloz(f: int, slot: int) -> void:
	var i := sloty.find(f)
	if i >= 0:
		sloty[i] = -1
	spalone.erase(f)
	sloty[slot] = f
	zle_sloty.erase(slot)
	wybrany = -1
	odswiez()


func spal(f: int) -> void:
	var i := sloty.find(f)
	if i >= 0:
		sloty[i] = -1
	if not f in spalone:
		spalone.append(f)
	wybrany = -1
	if M["manifest_fragmenty"][f][1] == null:
		info("Do pieca! Tego na pewno nie było w manifeście.")
	else:
		info("Hola! To zdanie było w manifeście. Kliknij piec, by je wyciągnąć.", false)
	odswiez()


func klik_slotu(i: int) -> void:
	if wybrany >= 0:
		poloz(wybrany, i)
	elif sloty[i] >= 0:
		wybrany = sloty[i]
		sloty[i] = -1
		odswiez()


func klik_pieca() -> void:
	if wybrany >= 0:
		spal(wybrany)
	elif not spalone.is_empty():
		spalone.pop_back()
		odswiez()


func sprawdz() -> bool:
	zle_sloty.clear()
	for i in sloty.size():
		var f: int = sloty[i]
		if f < 0 or M["manifest_fragmenty"][f][1] == null or int(M["manifest_fragmenty"][f][1]) != i:
			zle_sloty[i] = true
	odswiez()
	if zle_sloty.is_empty():
		main.dzwiek("stempel")
		wygraj()
		return true
	info("Coś się nie zgadza w %d miejscach. Sprawdź zaznaczone na czerwono." % zle_sloty.size(), false)
	return false
