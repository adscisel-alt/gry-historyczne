extends Node
## Tryb wieloosobowy online: przekaźnik pokoi na WebSocket.
##
## Serwer (ten sam projekt):  godot --headless --path godot -- --serwer 9080
## albo „Załóż serwer w sieci lokalnej” w wersji EXE. Klient działa także w przeglądarce
## (strona https wymaga adresu wss://, np. serwera za odwrotnym proxy z certyfikatem).
##
## Protokół (JSON):
##   klient -> serwer: {t:"utworz", imie}  {t:"dolacz", kod, imie}  {t:"wyslij", dane:{...}}  {t:"wyjdz"}
##   serwer -> klient: {t:"pokoj", kod, id, host, gracze:[{id, imie}]}  {t:"lobby", gracze, host}
##                     {t:"dane", od, dane:{...}}  {t:"blad", tekst}  {t:"wyszedl", id}
## Dane gry: {typ:"start", stan, miejsca:{id: numer_gracza}}, {typ:"stan", stan}, {typ:"czat", tekst, imie}

var g

# ----------------------------------------------------------------- serwer
var serwer: TCPServer
var polaczenia := {}        # id -> {ws, tcp, pokoj, imie}
var pokoje := {}            # kod -> {gracze: [id], host: id}
var nast_id := 1

# ----------------------------------------------------------------- klient
var ws: WebSocketPeer
var stan_ws := -1
var moj_id := 0
var kod := ""
var host := false
var gracze_lobby := []
var miejsca := {}           # id (str) -> numer gracza w grze
var imie := "Gracz"
var czat := []
var bledy := []
var lokalny_serwer := false
var _ostatni_ping := 0.0


func uruchom_serwer(port: int) -> bool:
	serwer = TCPServer.new()
	var e := serwer.listen(port)
	if e != OK:
		print("SERWER: nie można nasłuchiwać na porcie ", port, " (", e, ")")
		return false
	print("SERWER: Roman Empire – przekaźnik pokoi działa na porcie ", port)
	return true


func zatrzymaj_serwer() -> void:
	if serwer:
		serwer.stop()
	serwer = null
	polaczenia = {}
	pokoje = {}


func _process(_dt: float) -> void:
	if serwer:
		_obsluz_serwer()
	if ws:
		_obsluz_klienta()


func _obsluz_serwer() -> void:
	while serwer.is_connection_available():
		var tcp := serwer.take_connection()
		var w := WebSocketPeer.new()
		w.inbound_buffer_size = 4 * 1024 * 1024
		w.outbound_buffer_size = 4 * 1024 * 1024
		w.accept_stream(tcp)
		polaczenia[nast_id] = {"ws": w, "pokoj": "", "imie": ""}
		nast_id += 1
	for id in polaczenia.keys():
		var p: Dictionary = polaczenia[id]
		var w: WebSocketPeer = p.ws
		w.poll()
		var st := w.get_ready_state()
		if st == WebSocketPeer.STATE_OPEN:
			while w.get_available_packet_count() > 0:
				var txt := w.get_packet().get_string_from_utf8()
				var m = JSON.parse_string(txt)
				if typeof(m) == TYPE_DICTIONARY:
					_serwer_wiadomosc(id, m)
		elif st == WebSocketPeer.STATE_CLOSED:
			_serwer_rozlacz(id)


func _do(id: int, m: Dictionary) -> void:
	if polaczenia.has(id):
		var w: WebSocketPeer = polaczenia[id].ws
		if w.get_ready_state() == WebSocketPeer.STATE_OPEN:
			w.send_text(JSON.stringify(m))


func _lista(kod_: String) -> Array:
	var w := []
	for i in pokoje[kod_].gracze:
		w.append({"id": i, "imie": polaczenia[i].imie})
	return w


func _rozeslij_lobby(kod_: String) -> void:
	var m := {"t": "lobby", "gracze": _lista(kod_), "host": pokoje[kod_].host}
	for i in pokoje[kod_].gracze:
		_do(i, m)


func _nowy_kod() -> String:
	var litery := "ABCDEFGHJKLMNPRSTUWXYZ"
	while true:
		var k := ""
		for i in 4:
			k += litery[randi() % litery.length()]
		if not pokoje.has(k):
			return k
	return "RZYM"


func _serwer_wiadomosc(id: int, m: Dictionary) -> void:
	match str(m.get("t", "")):
		"utworz":
			var k := _nowy_kod()
			pokoje[k] = {"gracze": [id], "host": id, "gra": false}
			polaczenia[id].pokoj = k
			polaczenia[id].imie = str(m.get("imie", "Gracz")).left(20)
			_do(id, {"t": "pokoj", "kod": k, "id": id, "host": id, "gracze": _lista(k)})
		"dolacz":
			var k := str(m.get("kod", "")).to_upper().strip_edges()
			if not pokoje.has(k):
				_do(id, {"t": "blad", "tekst": "Nie ma pokoju o kodzie " + k})
				return
			if pokoje[k].gracze.size() >= 4:
				_do(id, {"t": "blad", "tekst": "Pokój jest pełny (4 graczy)"})
				return
			if pokoje[k].gra:
				_do(id, {"t": "blad", "tekst": "Gra w tym pokoju już się zaczęła"})
				return
			pokoje[k].gracze.append(id)
			polaczenia[id].pokoj = k
			polaczenia[id].imie = str(m.get("imie", "Gracz")).left(20)
			_do(id, {"t": "pokoj", "kod": k, "id": id, "host": pokoje[k].host, "gracze": _lista(k)})
			_rozeslij_lobby(k)
		"wyslij":
			var k: String = polaczenia[id].pokoj
			if not pokoje.has(k):
				return
			var dane = m.get("dane", {})
			if typeof(dane) == TYPE_DICTIONARY and dane.get("typ", "") == "start":
				pokoje[k].gra = true
			for i in pokoje[k].gracze:
				if i != id:
					_do(i, {"t": "dane", "od": id, "dane": dane})
		"wyjdz":
			_serwer_rozlacz(id)
		"ping":
			_do(id, {"t": "pong"})


func _serwer_rozlacz(id: int) -> void:
	if not polaczenia.has(id):
		return
	var k: String = polaczenia[id].pokoj
	polaczenia.erase(id)
	if pokoje.has(k):
		pokoje[k].gracze.erase(id)
		if pokoje[k].gracze.is_empty():
			pokoje.erase(k)
			return
		if pokoje[k].host == id:
			pokoje[k].host = pokoje[k].gracze[0]
		for i in pokoje[k].gracze:
			_do(i, {"t": "wyszedl", "id": id})
		_rozeslij_lobby(k)


# ===================================================================== klient
func polacz(adres: String, imie_: String) -> void:
	rozlacz()
	imie = imie_ if imie_ != "" else "Gracz"
	ws = WebSocketPeer.new()
	ws.inbound_buffer_size = 4 * 1024 * 1024
	ws.outbound_buffer_size = 4 * 1024 * 1024
	var e := ws.connect_to_url(adres)
	if e != OK:
		bledy.append("Nie można połączyć z %s" % adres)
		ws = null
	stan_ws = -1


func rozlacz() -> void:
	if ws:
		ws.close()
	ws = null
	kod = ""
	host = false
	gracze_lobby = []
	moj_id = 0


func polaczony() -> bool:
	return ws != null and ws.get_ready_state() == WebSocketPeer.STATE_OPEN


func _wyslij(m: Dictionary) -> void:
	if polaczony():
		ws.send_text(JSON.stringify(m))


var _czeka := []


func utworz_pokoj() -> void:
	_czeka.append({"t": "utworz", "imie": imie})


func dolacz(kod_: String) -> void:
	_czeka.append({"t": "dolacz", "kod": kod_, "imie": imie})


func _obsluz_klienta() -> void:
	ws.poll()
	var st := ws.get_ready_state()
	if st != stan_ws:
		stan_ws = st
		if g and g.ui and g.tryb == "":
			g.ui.odswiez_lobby()
	if st == WebSocketPeer.STATE_OPEN:
		while not _czeka.is_empty():
			_wyslij(_czeka.pop_front())
		while ws.get_available_packet_count() > 0:
			var m = JSON.parse_string(ws.get_packet().get_string_from_utf8())
			if typeof(m) == TYPE_DICTIONARY:
				_klient_wiadomosc(m)
	elif st == WebSocketPeer.STATE_CLOSED:
		var bylo := kod != ""
		ws = null
		if bylo:
			bledy.append("Połączenie z serwerem zostało przerwane")
		else:
			bledy.append("Nie udało się połączyć z serwerem")
		if g and g.ui and g.tryb == "":
			g.ui.odswiez_lobby()


func _klient_wiadomosc(m: Dictionary) -> void:
	match str(m.get("t", "")):
		"pokoj":
			kod = m.kod
			moj_id = int(m.id)
			host = int(m.host) == moj_id
			gracze_lobby = m.gracze
		"lobby":
			gracze_lobby = m.gracze
			host = int(m.host) == moj_id
		"blad":
			bledy.append(str(m.tekst))
		"wyszedl":
			_gracz_wyszedl(int(m.id))
		"dane":
			_dane(m.dane, int(m.get("od", 0)))
	if g and g.ui and g.tryb == "":
		g.ui.odswiez_lobby()


func _gracz_wyszedl(id: int) -> void:
	if g == null or g.S.is_empty() or g.S.get("tryb", "") != "online":
		return
	var nr = miejsca.get(str(id), -1)
	if int(nr) >= 0:
		g.S.gracze[int(nr)].odlaczony = true
		czat.append("— %s opuścił grę —" % g.S.gracze[int(nr)].imie)
		# host (lub nowy host) przejmuje turę rozłączonego gracza
		if host and int(g.S.aktywny) == int(nr):
			g.moj_gracz_tymczasowo(int(nr))


func _dane(d, od: int) -> void:
	if typeof(d) != TYPE_DICTIONARY:
		return
	match str(d.get("typ", "")):
		"start":
			miejsca = d.miejsca
			g.moj_gracz = int(miejsca.get(str(moj_id), 0))
			g.odebrano_stan(d.stan)
		"stan":
			g.odebrano_stan(d.stan)
		"czat":
			czat.append("%s: %s" % [d.get("imie", "?"), d.get("tekst", "")])
			if g.ui:
				g.ui.odswiez_czat()


func rozpocznij_gre(rozdzial: int, trudnosc: int) -> void:
	## Host rozdaje miejsca i wysyła stan początkowy.
	var gracze := []
	miejsca = {}
	for i in gracze_lobby.size():
		gracze.append({"imie": gracze_lobby[i].imie, "rod": i})
		miejsca[str(int(gracze_lobby[i].id))] = i
	var st: Dictionary = g.nowy_stan(rozdzial, gracze, "online", trudnosc)
	g.moj_gracz = int(miejsca[str(moj_id)])
	_wyslij({"t": "wyslij", "dane": {"typ": "start", "stan": st, "miejsca": miejsca}})
	g.odebrano_stan(st)


func wyslij_stan(st: Dictionary) -> void:
	_wyslij({"t": "wyslij", "dane": {"typ": "stan", "stan": st}})


func wyslij_czat(tekst: String) -> void:
	if tekst.strip_edges() == "":
		return
	czat.append("%s: %s" % [imie, tekst])
	_wyslij({"t": "wyslij", "dane": {"typ": "czat", "tekst": tekst.left(200), "imie": imie}})


func uruchom_lokalny_serwer(port: int) -> bool:
	if OS.has_feature("web"):
		return false
	lokalny_serwer = uruchom_serwer(port)
	return lokalny_serwer


func adresy_lokalne() -> Array:
	var w := []
	for a in IP.get_local_addresses():
		if a.count(".") == 3 and not a.begins_with("127.") and not a.begins_with("169.254"):
			w.append(a)
	return w


# ===================================================================== autotest sieci
func samotest() -> bool:
	## Serwer + dwóch klientów (WebSocketPeer) w jednym procesie.
	var port := 19080 + randi() % 500
	if not uruchom_serwer(port):
		return false
	var a := WebSocketPeer.new()
	var b := WebSocketPeer.new()
	a.connect_to_url("ws://127.0.0.1:%d" % port)
	b.connect_to_url("ws://127.0.0.1:%d" % port)
	var odebrane_a := []
	var odebrane_b := []
	var krok := 0
	var kod_ := ""
	for i in 600:
		await get_tree().process_frame
		a.poll()
		b.poll()
		while a.get_available_packet_count() > 0:
			odebrane_a.append(JSON.parse_string(a.get_packet().get_string_from_utf8()))
		while b.get_available_packet_count() > 0:
			odebrane_b.append(JSON.parse_string(b.get_packet().get_string_from_utf8()))
		if krok == 0 and a.get_ready_state() == WebSocketPeer.STATE_OPEN and b.get_ready_state() == WebSocketPeer.STATE_OPEN:
			a.send_text(JSON.stringify({"t": "utworz", "imie": "Ala"}))
			krok = 1
		elif krok == 1 and odebrane_a.size() > 0:
			kod_ = odebrane_a[0].kod
			b.send_text(JSON.stringify({"t": "dolacz", "kod": kod_, "imie": "Kuba"}))
			krok = 2
		elif krok == 2 and odebrane_b.size() > 0:
			var st: Dictionary = g.nowy_stan(0, [{"imie": "Ala", "rod": 0}, {"imie": "Kuba", "rod": 1}], "online", 1)
			a.send_text(JSON.stringify({"t": "wyslij", "dane": {"typ": "stan", "stan": st}}))
			krok = 3
		elif krok == 3:
			for m in odebrane_b:
				if m.t == "dane" and m.dane.typ == "stan" and m.dane.stan.gracze.size() == 2:
					krok = 4
		if krok == 4:
			break
	print("TEST: sieć – pokój ", kod_, ", krok ", krok)
	a.close()
	b.close()
	zatrzymaj_serwer()
	return krok == 4
