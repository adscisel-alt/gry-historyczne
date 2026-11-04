"""Automatyczny gracz: przechodzi całą grę na poziomie logiki.

Używany przez testy oraz przez opcję ``--autotest`` gotowego pliku EXE.
"""
from .stan import Gra, Zdarzenie
from .dane import fakty as F
from .dane import minigry_dane as MD

# Solucja: kolejne kroki w każdej lokacji ("klik", hotspot) albo ("uzyj", przedmiot, hotspot).
SOLUCJA = [
    ("klik", "damian"), ("klik", "mapa_sciana"), ("klik", "polka"), ("klik", "szuflada"),
    ("uzyj", "pocztowka_krakow", "stereoskop"),
    ("klik", "witos"), ("klik", "mariacki"), ("klik", "gazeciarz"), ("klik", "slup"), ("klik", "powrot"),
    # r2
    ("klik", "staszek"), ("klik", "hak"), ("klik", "stol"), ("klik", "drzwi"),
    ("klik", "wozny"), ("uzyj", "opaska", "wozny"), ("klik", "kakowski"), ("klik", "ostrowski"),
    ("uzyj", "meldunek", "lubomirski"), ("klik", "do_lublina"),
    # r3
    ("klik", "daszynski"), ("klik", "rydz"), ("klik", "do_drukarni"), ("klik", "zecer"), ("klik", "kaszta"),
    ("klik", "prasa"), ("klik", "do_palacu"), ("uzyj", "odbitka_manifestu", "daszynski"), ("klik", "pocztowka_dalej"),
    # r4
    ("klik", "okno_wagon"), ("klik", "siedzenie"), ("klik", "pilsudski"), ("klik", "wysiadka"),
    ("klik", "koc"), ("klik", "bramka"), ("klik", "lubomirski_dw"), ("klik", "dalej_dworzec"),
    # r5
    ("klik", "koc_k"), ("klik", "stol_plan"), ("klik", "otto"), ("klik", "na_plac"),
    ("klik", "zawadzka"), ("klik", "zawadzka"), ("klik", "do_paryza"),
    # r6
    ("klik", "telegraf"), ("klik", "dmowski"), ("klik", "paderewski"), ("klik", "do_salonu"),
    ("klik", "carter"), ("klik", "do_poznania"),
    # r7
    ("klik", "kiosk"), ("klik", "korfanty"), ("klik", "do_warszawy"),
    ("klik", "plakat"), ("klik", "moraczewska"), ("klik", "moraczewska"), ("klik", "damian_final"),
]


def rozwiaz_minigre(gid, stan):
    """Zwraca True, jeśli automat potrafi rozwiązać minigrę (sprawdza poprawność danych)."""
    if gid == "mapa_zaborow":
        return all(F.punkt_w_wielokacie(*poz, F.ZABORY[z]["punkty"]) for poz, z in F.MIASTA.values())
    if gid == "manifest":
        sekcje = sorted(i for _, i in MD.MANIFEST_FRAGMENTY if i is not None)
        return sekcje == list(range(len(MD.MANIFEST_SEKCJE)))
    if gid == "przepustki":
        return sum(1 for d in MD.PRZEPUSTKI if MD.przepustka_wazna(d) in (True, False)) >= MD.PRZEPUSTKI_PROG
    if gid == "kolejnosc_koszar":
        return MD.sprawdz_koszary(MD.KOSZARY_ROZWIAZANIE) == []
    if gid == "swiadkowie":
        return all(r["dowod"] in stan.ekwipunek for r in MD.SWIADKOWIE_RUNDY)
    if gid == "dyplomacja":
        return MD.dyplomacja_wygrana(symuluj_najlepsza_dyplomacje()[1])
    if gid == "prawa_kobiet":
        return len(MD.QUIZ_KOBIET) >= MD.QUIZ_KOBIET_PROG
    if gid == "wklady":
        return len(MD.WKLADY) == len({p for p, _ in MD.WKLADY})
    raise KeyError(gid)


def symuluj_najlepsza_dyplomacje():
    wybory = []
    for runda in MD.DYPLOMACJA_RUNDY:
        najl = max(range(len(runda["odpowiedzi"])), key=lambda i: sum(runda["odpowiedzi"][i][1].values()))
        wybory.append(najl)
    return wybory, MD.symuluj_dyplomacje(wybory)


def przeprowadz_rozmowe(gra, did, log):
    r = gra.rozmowa(did)
    odwiedzone = {r.wezel_id}
    kroki = 0
    while not r.zakonczona:
        kroki += 1
        if kroki > 200:
            raise RuntimeError("Dialog %s się nie kończy" % did)
        opcje = r.opcje()
        if not opcje:
            r.dalej()
        else:
            wybor = None
            for i, o in enumerate(opcje):
                if o["dalej"] not in odwiedzone:
                    wybor = i
                    break
            if wybor is None:
                wybor = len(opcje) - 1
            r.wybierz(wybor)
        odwiedzone.add(r.wezel_id)
    log.append("dialog " + did)
    return r.odbierz_zdarzenia()


def obsluz(gra, zdarzenia, log):
    kolejka = list(zdarzenia)
    while kolejka:
        rodzaj, arg = kolejka.pop(0)
        if rodzaj == Zdarzenie.DIALOG:
            kolejka.extend(przeprowadz_rozmowe(gra, arg, log))
        elif rodzaj == Zdarzenie.MINIGRA:
            if not rozwiaz_minigre(arg, gra.stan):
                raise RuntimeError("Minigra %s nierozwiązywalna" % arg)
            log.append("minigra " + arg)
            kolejka.extend(gra.wygrana_minigry(arg))
        elif rodzaj == Zdarzenie.MIT:
            gra.stan.odpowiedz_mit(arg, F.MITY[arg]["dobra"])
            log.append("mit " + arg)
        elif rodzaj == Zdarzenie.KONIEC_ROZDZIALU:
            log.append("koniec " + arg)
            gra.stan.nastepny_rozdzial()


def przejdz_gre():
    """Przechodzi grę od początku do końca. Zwraca (gra, log)."""
    gra = Gra()
    log = []
    for krok in SOLUCJA:
        if gra.stan.ukonczona:
            break
        if krok[0] == "klik":
            zd = gra.kliknij(krok[1])
        else:
            zd = gra.uzyj(krok[1], krok[2])
        log.append("%s @ %s" % ("/".join(krok[1:]), gra.stan.lokacja))
        obsluz(gra, zd, log)
    return gra, log


def autotest():
    gra, log = przejdz_gre()
    ok = gra.stan.ukonczona
    print("Autotest logiki: %s (%d kroków, %d faktów, %d mitów, %d postaci)" % (
        "OK" if ok else "BŁĄD", len(log), len(gra.stan.fakty), len(gra.stan.mity), len(gra.stan.poznani)))
    return ok
