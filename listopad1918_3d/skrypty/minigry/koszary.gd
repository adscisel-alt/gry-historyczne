extends "res://skrypty/minigry/baza.gd"
## Rozdział 5: kolejność przejmowania punktów w mieście — zagadka logiczna z paskiem napięcia.

const MAX_NAPIECIE := 3
const POZYCJE := {"Telegraf": Vector2(150, 130), "Magazyn broni": Vector2(290, 290), "Dworzec": Vector2(80, 340),
	"Koszary Mirowskie": Vector2(240, 200), "Cytadela": Vector2(380, 40)}

var punkty: Array = []
var plan: Array = []
var napiecie := 0
var zlamane: Array = []
var szkic: Control
var przyciski_p: Dictionary = {}
var plan_ui: Array = []
var wskazowki_ui: Array = []
var paski: Array = []


func _init(p_main) -> void:
	super(p_main)
	gid = "kolejnosc_koszar"
	tytul = "Plan akcji POW — noc z 10 na 11 listopada"
	instrukcja = "Ułóż kolejność przejmowania pięciu punktów tak, by spełnić wszystkie wskazówki. Kliknij punkt, by dodać go do planu; kliknij pozycję w planie, by ją usunąć. Każda błędna próba podnosi napięcie!"
	punkty = M["koszary_punkty"].duplicate()
	var rng := RandomNumberGenerator.new()
	rng.seed = 11
	for i in punkty.size():
		var j := rng.randi_range(0, punkty.size() - 1)
		var t = punkty[i]
		punkty[i] = punkty[j]
		punkty[j] = t


static func sprawdz_kolejnosc(kolejnosc: Array) -> Array:
	var bledy: Array = []
	if kolejnosc.size() != 5:
		return [0]
	var poz := {}
	for i in kolejnosc.size():
		poz[kolejnosc[i]] = i
	if poz.size() != 5:
		return [0]
	if poz["Telegraf"] != 0:
		bledy.append(1)
	if poz["Magazyn broni"] != poz["Telegraf"] + 1:
		bledy.append(2)
	if not poz["Dworzec"] < poz["Koszary Mirowskie"]:
		bledy.append(3)
	if poz["Cytadela"] != 4:
		bledy.append(4)
	return bledy


func buduj() -> void:
	szkic = Motyw.karta(Rect2(40, 130, 480, 400))
	gra.add_child(szkic)
	szkic.draw.connect(_rysuj_szkic)
	dodaj(Motyw.etykieta("Wskazówki na marginesie:", 16, "plakat"), Rect2(40, 540, 600, 22), gra)
	for i in M["koszary_wskazowki"].size():
		var l := Motyw.etykieta(str(M["koszary_wskazowki"][i]), 15, "reka")
		dodaj(l, Rect2(40, 562 + i * 24, 820, 22), gra)
		wskazowki_ui.append(l)
	dodaj(Motyw.etykieta("Punkty w mieście", 16, "plakat", Motyw.ATRAMENT_JASNY, false), Rect2(560, 110, 300, 24), gra)
	for i in punkty.size():
		var p: String = punkty[i]
		var b := Motyw.przycisk(p, 19, func(): dodaj_punkt(p))
		dodaj(b, Rect2(560, 140 + i * 60, 300, 50), gra)
		przyciski_p[p] = b
	dodaj(Motyw.etykieta("Twój plan", 16, "plakat", Motyw.ATRAMENT_JASNY, false), Rect2(900, 110, 300, 24), gra)
	for i in 5:
		var nr: int = i
		var b := Motyw.przycisk("%d." % (i + 1), 20, func(): usun(nr))
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		dodaj(b, Rect2(900, 140 + i * 60, 340, 50), gra)
		plan_ui.append(b)
	dodaj(Motyw.etykieta("NAPIĘCIE", 16, "plakat"), Rect2(560, 455, 100, 24), gra)
	for k in MAX_NAPIECIE:
		var c := ColorRect.new()
		dodaj(c, Rect2(660 + k * 70, 452, 60, 24), gra)
		paski.append(c)
	dodaj(Motyw.przycisk("Zatwierdź plan", 20, func(): sprawdz()), Rect2(900, 470, 300, 50), gra)
	odswiez()


func odswiez() -> void:
	for p in przyciski_p:
		przyciski_p[p].disabled = p in plan
	for i in 5:
		plan_ui[i].text = "%d.  %s" % [i + 1, plan[i] if i < plan.size() else ""]
	for k in paski.size():
		paski[k].color = Motyw.STEMPEL if k < napiecie else Color(0.75, 0.69, 0.58)
	for i in wskazowki_ui.size():
		wskazowki_ui[i].add_theme_color_override("font_color", Motyw.STEMPEL if (i + 1) in zlamane else Motyw.ATRAMENT)
	if szkic:
		szkic.queue_redraw()


func dodaj_punkt(p: String) -> void:
	if not p in plan and plan.size() < 5:
		plan.append(p)
		main.dzwiek("klik")
		odswiez()


func usun(i: int) -> void:
	if i < plan.size():
		plan.remove_at(i)
		odswiez()


func sprawdz() -> bool:
	if plan.size() < 5:
		info("Plan musi mieć wszystkie pięć punktów.", false)
		return false
	zlamane = sprawdz_kolejnosc(plan)
	if zlamane.is_empty():
		odswiez()
		wygraj()
		return true
	napiecie += 1
	if napiecie >= MAX_NAPIECIE:
		napiecie = 0
		plan = []
		zlamane = []
		info("Damian: STOP, przewijam! Za dużo nerwów, ktoś mógłby zacząć strzelać. Ułóż plan od nowa — spokojnie.", false)
	else:
		var t: Array = []
		for z in zlamane:
			t.append(str(z))
		info("Wskazówki złamane: %s. Napięcie rośnie…" % ", ".join(PackedStringArray(t)), false)
	odswiez()
	return false


func _rysuj_szkic() -> void:
	szkic.draw_line(Vector2(430, 10), Vector2(340, 390), Color(0.5, 0.43, 0.33), 22)
	szkic.draw_string(Motyw.czcionka("reka"), Vector2(400, 200), "Wisła", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0.93, 0.88, 0.78))
	for odc in [[Vector2(40, 170), Vector2(420, 170)], [Vector2(210, 20), Vector2(210, 390)], [Vector2(40, 320), Vector2(360, 320)]]:
		szkic.draw_line(odc[0], odc[1], Color(0.66, 0.59, 0.48), 6)
	var f := Motyw.czcionka("plakat")
	for nazwa in POZYCJE:
		var p: Vector2 = POZYCJE[nazwa] + Vector2(0, 20)
		var nr := plan.find(nazwa) + 1
		szkic.draw_circle(p, 16, Motyw.FIOLET if nr > 0 else Color(0.16, 0.1, 0.06))
		szkic.draw_string(f, p + Vector2(-5, 6), str(nr) if nr > 0 else "?", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0.95, 0.92, 0.85))
		szkic.draw_string(f, p + Vector2(20, -6), nazwa, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color(0.12, 0.08, 0.05))
