extends "res://skrypty/minigry/baza.gd"
## Rozdział 5: wskaż sprzeczne zeznanie i udowodnij je przedmiotem z torby.

var runda := 0
var wskazane := -1
var po_rundzie := false
var pytanie_l: Label
var zeznania_ui: Array = []
var torba: GridContainer
var dalej_l: Label


func _init(p_main) -> void:
	super(p_main)
	gid = "swiadkowie"
	tytul = "Redakcja „Kuriera”: kto mówi nieprawdę?"
	instrukcja = "Przeczytaj zeznania. Kliknij to, które jest sprzeczne z faktami, a potem przedmiot z torby, który to udowadnia. Damian powtarza: plotka to nie dowód!"


func dane_rundy() -> Dictionary:
	return M["swiadkowie"][runda]


func buduj() -> void:
	pytanie_l = Motyw.etykieta("", 22, "plakat", Motyw.ATRAMENT, false)
	dodaj(pytanie_l, Rect2(40, 118, 1000, 30), gra)
	for i in 3:
		var nr := i
		var b := Motyw.przycisk("", 18, func(): wskaz(nr))
		dodaj(b, Rect2(40, 160 + i * 124, 820, 112), gra)
		var por := Motyw.obraz(null, Rect2(8, 8, 80, 96))
		b.add_child(por)
		var kto := Motyw.etykieta("", 16, "plakat", Motyw.ATRAMENT_JASNY, false)
		kto.position = Vector2(100, 8)
		kto.mouse_filter = Control.MOUSE_FILTER_IGNORE
		b.add_child(kto)
		var t := Motyw.etykieta("", 18, "reka")
		t.position = Vector2(100, 32)
		t.size = Vector2(700, 76)
		t.mouse_filter = Control.MOUSE_FILTER_IGNORE
		b.add_child(t)
		zeznania_ui.append([b, por, kto, t])
	dodaj(Motyw.etykieta("Twoja torba (dowody):", 16, "plakat", Motyw.ATRAMENT_JASNY, false), Rect2(900, 160, 340, 24), gra)
	torba = GridContainer.new()
	torba.columns = 3
	torba.add_theme_constant_override("h_separation", 10)
	torba.add_theme_constant_override("v_separation", 10)
	dodaj(torba, Rect2(900, 192, 340, 400), gra)
	for p in main.logika.ekwipunek:
		var prz: String = p
		var b := Button.new()
		b.custom_minimum_size = Vector2(104, 104)
		b.icon = Dane.tex_ikona(prz)
		b.expand_icon = true
		b.tooltip_text = str(Dane.przedmioty[prz]["nazwa"])
		b.add_theme_stylebox_override("normal", Motyw.styl_plaski(Color(0.78, 0.71, 0.58)))
		b.add_theme_stylebox_override("hover", Motyw.styl_plaski(Color(0.88, 0.82, 0.7), Motyw.ATRAMENT, 3))
		b.pressed.connect(func(): pokaz_dowod(prz))
		torba.add_child(b)
	dalej_l = Motyw.etykieta("▸ kliknij gdziekolwiek, aby przejść dalej", 18, "reka", Motyw.ATRAMENT_JASNY, false, HORIZONTAL_ALIGNMENT_CENTER)
	dodaj(dalej_l, Rect2(0, 620, 1280, 30), gra)
	odswiez()


func odswiez() -> void:
	var d := dane_rundy()
	pytanie_l.text = "Runda %d / %d — %s" % [runda + 1, M["swiadkowie"].size(), d["pytanie"]]
	for i in 3:
		var z: Array = d["zeznania"][i]
		var ui: Array = zeznania_ui[i]
		ui[1].texture = Dane.tex_portret(str(z[0]))
		ui[2].text = Dane.imie(str(z[0]))
		ui[3].text = "„" + str(z[1]) + "”"
		ui[0].modulate = Color(0.88, 0.75, 1.0) if i == wskazane else Color(1, 1, 1)
	dalej_l.visible = po_rundzie


func wskaz(i: int) -> bool:
	if po_rundzie:
		nastepna()
		return false
	if i != int(dane_rundy()["falszywe"]):
		wskazane = -1
		info("Hmm, to zeznanie zgadza się z tym, co wiemy. Szukaj dalej.", false)
		odswiez()
		return false
	wskazane = i
	info("Dobrze — to brzmi podejrzanie. Teraz pokaż dowód z torby.")
	odswiez()
	return true


func pokaz_dowod(p: String) -> bool:
	if po_rundzie:
		nastepna()
		return false
	if wskazane < 0:
		info("Najpierw wskaż fałszywe zeznanie.", false)
		return false
	if p == str(dane_rundy()["dowod"]):
		po_rundzie = true
		info(str(dane_rundy()["wyjasnienie"]))
		main.dzwiek("stempel")
		odswiez()
		return true
	info("%s niczego tu nie dowodzi. Poszukaj innego dowodu." % Dane.przedmioty[p]["nazwa"], false)
	return false


func nastepna() -> void:
	po_rundzie = false
	wskazane = -1
	runda += 1
	info("")
	if runda >= M["swiadkowie"].size():
		runda = M["swiadkowie"].size() - 1
		wygraj()
	odswiez()


func klik_tla() -> void:
	if po_rundzie:
		nastepna()
