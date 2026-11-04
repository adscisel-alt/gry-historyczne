extends "res://skrypty/minigry/baza.gd"
## Rozdział 6: dyplomacja z paskami poparcia Francji, Anglii i USA.

var paski: Dictionary = {}
var wyswietlane: Dictionary = {}
var runda := 0
var przegrana := false
var paski_ui: Dictionary = {}
var procenty_ui: Dictionary = {}
var portret: TextureRect
var kto_l: Label
var runda_l: Label
var pytanie_l: Label
var odp_ui: Array = []
var b_znowu: Button


func _init(p_main) -> void:
	super(p_main)
	gid = "dyplomacja"
	tytul = "Salon dyplomatyczny — Paryż, listopad 1918"
	instrukcja = "Odpowiadaj dyplomatom. Każda odpowiedź zmienia poparcie trzech mocarstw. Na koniec każde musi mieć co najmniej %d%%. Argumenty Dmowskiego i depesza Paderewskiego bardzo pomagają!" % int(M["dyplomacja_prog"])


func buduj() -> void:
	for i in M["panstwa"].size():
		var p: String = M["panstwa"][i]
		var x := 60 + i * 400
		dodaj(Motyw.etykieta(p, 20, "plakat", Motyw.ATRAMENT, false), Rect2(x, 118, 300, 28), gra)
		var tlo := ColorRect.new()
		tlo.color = Color(0.66, 0.6, 0.5)
		dodaj(tlo, Rect2(x, 150, 340, 28), gra)
		var pasek := ColorRect.new()
		dodaj(pasek, Rect2(x, 150, 0, 28), gra)
		paski_ui[p] = pasek
		var prog := ColorRect.new()
		prog.color = Motyw.STEMPEL
		dodaj(prog, Rect2(x + 340 * float(M["dyplomacja_prog"]) / 100.0 - 1, 144, 3, 40), gra)
		var pr := Motyw.etykieta("", 18, "plakat", Motyw.ATRAMENT, false)
		dodaj(pr, Rect2(x + 348, 150, 60, 28), gra)
		procenty_ui[p] = pr
	portret = Motyw.obraz(null, Rect2())
	dodaj(portret, Rect2(60, 210, 160, 192), gra)
	kto_l = Motyw.etykieta("", 16, "plakat", Motyw.ATRAMENT, false, HORIZONTAL_ALIGNMENT_CENTER)
	dodaj(kto_l, Rect2(20, 408, 240, 24), gra)
	runda_l = Motyw.etykieta("", 16, "szeryf", Motyw.ATRAMENT_JASNY, false)
	dodaj(runda_l, Rect2(320, 206, 300, 24), gra)
	pytanie_l = Motyw.etykieta("", 26, "reka")
	dodaj(pytanie_l, Rect2(320, 234, 900, 120), gra)
	for i in 3:
		var nr := i
		var b := Motyw.przycisk_tekst("", 18, func(): odpowiedz(nr))
		dodaj(b, Rect2(320, 380 + i * 74, 920, 66), gra)
		odp_ui.append(b)
	b_znowu = Motyw.przycisk("Spróbuj jeszcze raz", 20, func(): reset())
	dodaj(b_znowu, Rect2(490, 590, 300, 50), gra)
	reset()


func reset() -> void:
	paski = {}
	for p in M["dyplomacja_start"]:
		paski[p] = int(M["dyplomacja_start"][p])
	wyswietlane = paski.duplicate()
	runda = 0
	przegrana = false
	info("")
	odswiez()


func odswiez() -> void:
	var trwa: bool = runda < M["dyplomacja_rundy"].size() and not przegrana
	for b in odp_ui:
		b.visible = trwa
	b_znowu.visible = przegrana
	portret.visible = trwa
	if trwa:
		var r: Dictionary = M["dyplomacja_rundy"][runda]
		portret.texture = Dane.tex_portret(str(r["kto"]))
		kto_l.text = Dane.imie(str(r["kto"]))
		runda_l.text = "Runda %d / %d" % [runda + 1, M["dyplomacja_rundy"].size()]
		pytanie_l.text = "„" + str(r["pytanie"]) + "”"
		for i in 3:
			odp_ui[i].get_node("Tekst").text = "%d. %s" % [i + 1, r["odpowiedzi"][i][0]]
	else:
		kto_l.text = ""
		runda_l.text = ""
		pytanie_l.text = ""


static func symuluj(wybory: Array) -> Dictionary:
	var M2: Dictionary = Dane.minigry
	var p := {}
	for k in M2["dyplomacja_start"]:
		p[k] = int(M2["dyplomacja_start"][k])
	for i in wybory.size():
		var zm: Dictionary = M2["dyplomacja_rundy"][i]["odpowiedzi"][wybory[i]][1]
		for k in zm:
			p[k] = clampi(p[k] + int(zm[k]), 0, 100)
	return p


static func najlepsze_wybory() -> Array:
	var w: Array = []
	for r in Dane.minigry["dyplomacja_rundy"]:
		var najl := 0
		var suma_najl := -999
		for i in r["odpowiedzi"].size():
			var s := 0
			for v in r["odpowiedzi"][i][1].values():
				s += int(v)
			if s > suma_najl:
				suma_najl = s
				najl = i
		w.append(najl)
	return w


func odpowiedz(i: int) -> void:
	if runda >= M["dyplomacja_rundy"].size() or przegrana:
		return
	var zm: Dictionary = M["dyplomacja_rundy"][runda]["odpowiedzi"][i][1]
	var opis: Array = []
	var suma := 0
	for p in zm:
		var d := int(zm[p])
		paski[p] = clampi(paski[p] + d, 0, 100)
		suma += d
		if d != 0:
			opis.append("%s %+d" % [p, d])
	info("Reakcja: " + (", ".join(PackedStringArray(opis)) if not opis.is_empty() else "bez zmian"), suma >= 0)
	runda += 1
	if runda >= M["dyplomacja_rundy"].size():
		var ok := true
		var slabe: Array = []
		for p in paski:
			if paski[p] < int(M["dyplomacja_prog"]):
				ok = false
				slabe.append(p)
		if ok:
			odswiez()
			wygraj()
			return
		przegrana = true
		info("Za słabe poparcie: %s. Dyplomacja to cierpliwość — spróbuj jeszcze raz." % ", ".join(PackedStringArray(slabe)), false)
	odswiez()


func _process(delta: float) -> void:
	super(delta)
	for p in paski_ui:
		wyswietlane[p] = lerpf(float(wyswietlane.get(p, 0)), float(paski.get(p, 0)), minf(1.0, delta * 5.0))
		var v: float = wyswietlane[p]
		paski_ui[p].size.x = 340.0 * v / 100.0
		paski_ui[p].color = Motyw.FIOLET if v >= float(M["dyplomacja_prog"]) else Color(0.3, 0.22, 0.15)
		procenty_ui[p].text = "%d%%" % roundi(v)


func klawisz_gry(k: int) -> void:
	if k >= KEY_1 and k <= KEY_3:
		odpowiedz(k - KEY_1)
