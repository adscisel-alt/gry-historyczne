extends "res://skrypty/minigry/baza.gd"
## Finał: kto co wniósł do niepodległości? Połącz osoby z ich wkładem.

var osoby: Array = []
var wklady: Array = []
var poprawne: Dictionary = {}
var pary: Dictionary = {}
var wybrana := ""
var osoby_ui: Dictionary = {}
var wklady_ui: Dictionary = {}
var linie: Control


func _init(p_main) -> void:
	super(p_main)
	gid = "wklady"
	tytul = "Album Damiana: kto co wniósł?"
	instrukcja = "Każdy wniósł do niepodległości co innego. Kliknij osobę po lewej, a potem jej wkład po prawej. Gdy połączysz wszystkie pary, album będzie kompletny."
	for para in M["wklady"]:
		osoby.append(str(para[0]))
		wklady.append(str(para[1]))
		poprawne[str(para[0])] = str(para[1])
	var rng := RandomNumberGenerator.new()
	rng.seed = 1918
	for i in wklady.size():
		var j := rng.randi_range(0, wklady.size() - 1)
		var t = wklady[i]
		wklady[i] = wklady[j]
		wklady[j] = t


func buduj() -> void:
	linie = Control.new()
	linie.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dodaj(linie, Rect2(0, 0, 1280, 720), gra)
	linie.draw.connect(_rysuj_linie)
	for i in osoby.size():
		var o: String = osoby[i]
		var b := Motyw.przycisk(Dane.imie(o), 19, func(): wybierz(o))
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.add_theme_constant_override("h_separation", 12)
		b.icon = Dane.tex_portret(o)
		b.expand_icon = true
		b.add_theme_constant_override("icon_max_width", 44)
		dodaj(b, Rect2(40, 122 + i * 66, 420, 60), gra)
		osoby_ui[o] = b
	for i in wklady.size():
		var w: String = wklady[i]
		var b := Motyw.przycisk_tekst(w, 18, func(): polacz_wybrana(w))
		dodaj(b, Rect2(640, 122 + i * 66, 600, 60), gra)
		wklady_ui[w] = b


func wybierz(o: String) -> void:
	if pary.has(o):
		return
	wybrana = o
	for k in osoby_ui:
		osoby_ui[k].modulate = Color(0.85, 0.7, 1.0) if k == o else Color(1, 1, 1)


func polacz_wybrana(w: String) -> void:
	if wybrana != "" and not w in pary.values():
		polacz(wybrana, w)


func polacz(osoba: String, wklad: String) -> bool:
	if poprawne[osoba] == wklad:
		pary[osoba] = wklad
		wybrana = ""
		osoby_ui[osoba].disabled = true
		osoby_ui[osoba].modulate = Color(1, 1, 1)
		wklady_ui[wklad].disabled = true
		info("Tak! %s — %s." % [Dane.imie(osoba), wklad.to_lower()])
		linie.queue_redraw()
		if pary.size() == osoby.size():
			wygraj()
		return true
	info("To raczej nie %s. Pomyśl, gdzie spotkałeś tę osobę." % Dane.imie(osoba), false)
	return false


func _rysuj_linie() -> void:
	for o in pary:
		var a: Control = osoby_ui[o]
		var b: Control = wklady_ui[pary[o]]
		linie.draw_line(a.position + Vector2(a.size.x, a.size.y / 2), b.position + Vector2(0, b.size.y / 2), Motyw.FIOLET, 3.0)
