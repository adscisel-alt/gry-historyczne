"""Dane minigier i zagadek logicznych oraz efekty zwycięstwa."""

# Efekty po wygranej (język efektów jak w rozdzialy.py).
WYGRANA = {
    "mapa_zaborow": ["flag:mapa_ok", "fakt:zabory", "dialog:d_witos_mapa"],
    "manifest": ["flag:manifest_ok", "fakt:manifest_tresc",
                 "damian:Zwróć uwagę na prawa wyborcze kobiet w manifeście. Za trzy tygodnie wrócimy do tego tematu — tym razem w prawie, nie tylko w obietnicy."],
    "przepustki": ["flag:przepustki_ok",
                   "damian:Peron gotowy. Za chwilę wysiądzie Komendant. Książę Lubomirski już poprawia cylinder."],
    "kolejnosc_koszar": ["flag:kolejnosc_ok", "zabierz:plan_koszar",
                         "damian:Ta kolejność to zagadka, nie dokładna kronika — ale logika jest prawdziwa: najpierw łączność, potem broń, a dopiero na końcu największy garnizon."],
    "swiadkowie": ["flag:swiadkowie_ok"],
    "dyplomacja": ["flag:dyplomacja_ok",
                   "damian:Brawo, dyplomato! W prawdziwej historii nie poszło tak szybko: Polska musiała czekać na konferencję pokojową w 1919 r. i spór o to, kto ją reprezentuje."],
    "prawa_kobiet": ["flag:quiz_kobiet_ok", "fakt:wybory_1919",
                     "damian:Zajrzyj do dziennika — jest tam strona o prawach wyborczych kobiet i porównanie z innymi krajami. A teraz chodź do mnie, czas złożyć album."],
    "wklady": ["flag:wklady_ok", "mit:m_kobiety", "mit:m_hymn", "mit:m_sam_pilsudski", "koniec_rozdzialu"],
}

# ---------------------------------------------------------------- MANIFEST (rozdział 3)
MANIFEST_SEKCJE = ["Kto ogłasza", "Ustrój państwa", "Prawa obywateli", "Praca", "Ziemia", "Wezwanie"]
MANIFEST_FRAGMENTY = [
    # (tekst, sekcja_index lub None dla fałszywki)
    ("Lud polski! Ogłaszamy powstanie Tymczasowego Rządu Ludowego Republiki Polskiej.", 0),
    ("Państwo Polskie, obejmujące wszystkie ziemie zamieszkałe przez lud polski, będzie republiką ludową.", 1),
    ("Wszyscy obywatele, bez różnicy płci, mają równe prawa polityczne i prawo wyborcze od 21 lat.", 2),
    ("Wprowadzamy 8-godzinny dzień pracy w przemyśle, rzemiośle i handlu.", 3),
    ("Wielka własność ziemska zostanie przejęta i przekazana ludowi pracującemu.", 4),
    ("Wzywamy lud do zwołania Sejmu Ustawodawczego jeszcze w tym roku. Niech żyje Polska!", 5),
    ("Przywracamy władzę króla i przywileje szlachty.", None),
    ("Prawo wyborcze przysługuje tylko właścicielom kamienic.", None),
]

# ---------------------------------------------------------------- KOLEJNOŚĆ KOSZAR (rozdział 5)
KOSZARY_PUNKTY = ["Telegraf", "Magazyn broni", "Dworzec", "Koszary Mirowskie", "Cytadela"]
KOSZARY_WSKAZOWKI = [
    "1. Najpierw łączność: zajmij telegraf, zanim ktoś wezwie posiłki.",
    "2. Magazyn broni — zaraz po telegrafie. Z bronią łatwiej przekonywać.",
    "3. Dworzec przed Koszarami Mirowskimi — Niemcy muszą mieć jak wyjechać, zanim oddadzą broń.",
    "4. Cytadela na samym końcu — to największy garnizon.",
]
KOSZARY_ROZWIAZANIE = ["Telegraf", "Magazyn broni", "Dworzec", "Koszary Mirowskie", "Cytadela"]


def sprawdz_koszary(kolejnosc):
    """Zwraca listę numerów złamanych wskazówek (pusta = poprawnie)."""
    bledy = []
    if len(kolejnosc) != 5 or sorted(kolejnosc) != sorted(KOSZARY_PUNKTY):
        return [0]
    poz = {p: i for i, p in enumerate(kolejnosc)}
    if poz["Telegraf"] != 0:
        bledy.append(1)
    if poz["Magazyn broni"] != poz["Telegraf"] + 1:
        bledy.append(2)
    if not poz["Dworzec"] < poz["Koszary Mirowskie"]:
        bledy.append(3)
    if poz["Cytadela"] != 4:
        bledy.append(4)
    return bledy


# ---------------------------------------------------------------- PRZEPUSTKI (rozdział 4)
LISTA_POWITALNA = ["Lubomirski", "Koc", "Sosnkowski", "Stamirowski", "Walewska", "Kowalska", "Zawadzka", "Wiśniewski"]
ZASADY_PRZEPUSTEK = [
    "Data: 10 XI 1918",
    "Pieczęć: POW lub Rada Regencyjna",
    "Nazwisko z listy powitalnej",
    "Podpis musi być",
]
# Dokumenty: (nazwisko, data, pieczęć, podpis). Ułożone tak, by każda zasada miała swój „haczyk”.
PRZEPUSTKI = [
    ("Zawadzka", "10 XI 1918", "POW", True),
    ("Kowalska", "10 XI 1918", "Rada Regencyjna", True),
    ("Müller", "10 XI 1918", "Generalgouvernement", True),
    ("Wiśniewski", "9 XI 1918", "POW", True),
    ("Stamirowski", "10 XI 1918", "POW", True),
    ("Walewska", "10 XI 1918", "Rada Regencyjna", False),
    ("Kwiatkowski", "10 XI 1918", "POW", True),
    ("Kowalska", "10 XI 1918", "POW", True),
]


def przepustka_wazna(doc):
    nazwisko, data, pieczec, podpis = doc
    return (data == "10 XI 1918" and pieczec in ("POW", "Rada Regencyjna")
            and nazwisko in LISTA_POWITALNA and podpis)


def powod_odrzucenia(doc):
    nazwisko, data, pieczec, podpis = doc
    if data != "10 XI 1918":
        return "zła data"
    if pieczec not in ("POW", "Rada Regencyjna"):
        return "niemiecka pieczęć"
    if nazwisko not in LISTA_POWITALNA:
        return "brak na liście"
    if not podpis:
        return "brak podpisu"
    return ""


PRZEPUSTKI_PROG = 6  # ile trzeba ocenić poprawnie z 8

# ---------------------------------------------------------------- ŚWIADKOWIE (rozdział 5)
SWIADKOWIE_RUNDY = [
    {
        "pytanie": "O przyjeździe Komendanta do Warszawy:",
        "zeznania": [
            ("dorozkarz", "Widziałem tłum na Dworcu Wiedeńskim. Komendant miał maciejówkę i szary płaszcz."),
            ("przekupka", "Przyjechał 11 listopada wieczorem, wszyscy wiedzą! Od razu wyszedł na balkon i ogłosił niepodległość."),
            ("student", "Witał go książę Lubomirski z Rady Regencyjnej i komendant Koc z POW."),
        ],
        "falszywe": 1,
        "dowod": "rozklad_jazdy",
        "wyjasnienie": "Rozkład jazdy: przyjazd 10 XI 1918 o 7.00. Żadnego balkonu — niepodległość nie miała jednego ogłoszenia.",
    },
    {
        "pytanie": "O Radzie Regencyjnej:",
        "zeznania": [
            ("student", "Rada Regencyjna przekazała Komendantowi dowództwo nad wojskiem 11 listopada."),
            ("dorozkarz", "Ci regenci nigdy nawet słowem nie wspomnieli o niepodległej Polsce. Siedzieli cicho jak myszy."),
            ("przekupka", "Arcybiskup Kakowski był jednym z regentów, sama go widziałam w karecie."),
        ],
        "falszywe": 1,
        "dowod": "odpis_oredzia",
        "wyjasnienie": "Orędzie z 7 X 1918: Rada Regencyjna ogłosiła wolę utworzenia niepodległego państwa.",
    },
    {
        "pytanie": "O rozbrajaniu Niemców:",
        "zeznania": [
            ("przekupka", "Niemcy oddawali karabiny za bochenek chleba, jeden to nawet za obwarzanek."),
            ("student", "W Krakowie Austriaków rozbrojono już 31 października, przed Warszawą."),
            ("dorozkarz", "Polska władza zaczęła się w Krakowie dopiero w grudniu, po Warszawie."),
        ],
        "falszywe": 2,
        "dowod": "orzelek",
        "wyjasnienie": "Orzełek z Krakowa, 31 X 1918 — Kraków był pierwszy. (A obwarzanek? Barwna plotka, ale ich nie da się sprawdzić — dobry reporter zaznaczy to jako „podobno”.)",
    },
]

# ---------------------------------------------------------------- DYPLOMACJA (rozdział 6)
PANSTWA = ["Francja", "Anglia", "USA"]
DYPLOMACJA_START = {"Francja": 35, "Anglia": 30, "USA": 30}
DYPLOMACJA_PROG = 50
DYPLOMACJA_RUNDY = [
    {
        "kto": "laroche",
        "pytanie": "Dlaczego Francja ma wspierać Polskę?",
        "odpowiedzi": [
            ("Silna Polska na wschód od Niemiec to wasz sojusznik i zapora przed niemieckim odwetem. (argument Dmowskiego)",
             {"Francja": 20, "Anglia": 0, "USA": 5}),
            ("Polacy walczą u waszego boku w Błękitnej Armii we Francji.", {"Francja": 15, "Anglia": 5, "USA": 5}),
            ("Bo i tak weźmiemy, co chcemy, z wami albo bez was!", {"Francja": -10, "Anglia": -15, "USA": -10}),
        ],
    },
    {
        "kto": "whitby",
        "pytanie": "Londyn obawia się zbyt wielkiej Polski i chaosu na wschodzie. Co pan na to?",
        "odpowiedzi": [
            ("Granice ustali konferencja pokojowa — według tego, gdzie mieszkają Polacy.", {"Francja": 0, "Anglia": 20, "USA": 10}),
            ("Polska musi być ogromna, od morza do morza, i już!", {"Francja": 5, "Anglia": -15, "USA": -10}),
            ("W Warszawie jest już władza i wojsko, które pilnuje porządku. (telegram Piłsudskiego z 16 XI)",
             {"Francja": -5, "Anglia": 10, "USA": 5}),
        ],
    },
    {
        "kto": "carter",
        "pytanie": "President Wilson mówił o 13. punkcie. Co on właściwie znaczy?",
        "odpowiedzi": [
            ("Niepodległa Polska z ludnością bezsprzecznie polską i wolnym dostępem do morza. (depesza Paderewskiego)",
             {"Francja": 5, "Anglia": 5, "USA": 20}),
            ("Że Polska dostanie wszystkie ziemie sprzed rozbiorów z 1772 roku.", {"Francja": 0, "Anglia": -10, "USA": -10}),
            ("Że Paderewski zagra w Białym Domu Chopina.", {"Francja": 0, "Anglia": 0, "USA": 5}),
        ],
    },
    {
        "kto": "laroche",
        "pytanie": "Kto mówi w imieniu Polski: Komitet w Paryżu czy rząd w Warszawie?",
        "odpowiedzi": [
            ("Tylko Komitet Narodowy Polski — to jego uznaliście.", {"Francja": 10, "Anglia": -5, "USA": 0}),
            ("Tylko rząd w Warszawie — tam jest wojsko.", {"Francja": -10, "Anglia": 5, "USA": 0}),
            ("Paryż i Warszawa muszą się porozumieć. Wspólna delegacja będzie silniejsza.", {"Francja": 10, "Anglia": 10, "USA": 10}),
        ],
    },
    {
        "kto": "whitby",
        "pytanie": "Czy nowa Polska zadba o prawa mniejszości — Żydów, Ukraińców, Niemców?",
        "odpowiedzi": [
            ("Tak. Wszyscy obywatele mają być równi wobec prawa.", {"Francja": 10, "Anglia": 10, "USA": 10}),
            ("To nie wasza sprawa.", {"Francja": -10, "Anglia": -10, "USA": -10}),
            ("Pomyślimy o tym później.", {"Francja": 0, "Anglia": -5, "USA": -5}),
        ],
    },
]


def symuluj_dyplomacje(wybory):
    paski = dict(DYPLOMACJA_START)
    for runda, w in zip(DYPLOMACJA_RUNDY, wybory):
        for p, d in runda["odpowiedzi"][w][1].items():
            paski[p] = max(0, min(100, paski[p] + d))
    return paski


def dyplomacja_wygrana(paski):
    return all(v >= DYPLOMACJA_PROG for v in paski.values())


# ---------------------------------------------------------------- MAPA ZABORÓW (rozdział 1)
# Dane geograficzne są w fakty.py (ZABORY, MIASTA).

# ---------------------------------------------------------------- PRAWA KOBIET (rozdział 7)
QUIZ_KOBIET = [
    ("Od ilu lat można było głosować według dekretu z 28 XI 1918?", ["18 lat", "21 lat", "30 lat"], 1),
    ("Czy kobiety mogły też kandydować do Sejmu?", ["Tak, miały bierne prawo wyborcze", "Nie, tylko głosować", "Tylko wdowy"], 0),
    ("Ile kobiet weszło do Sejmu Ustawodawczego w 1919 r.?", ["Żadna", "8", "100"], 1),
    ("W którym kraju kobiety uzyskały prawa wyborcze PÓŹNIEJ niż w Polsce?", ["Nowa Zelandia (1893)", "Finlandia (1906)", "Francja (1944)"], 2),
    ("Kiedy Polki po raz pierwszy głosowały w wyborach do Sejmu?", ["26 I 1919", "11 XI 1918", "3 V 1791"], 0),
]
QUIZ_KOBIET_PROG = 4

# ---------------------------------------------------------------- FINAŁ: KTO CO WNIÓSŁ
WKLADY = [
    ("pilsudski", "Wojsko i przejęcie władzy w Warszawie"),
    ("dmowski", "Uznanie Ententy i Komitet Narodowy w Paryżu"),
    ("paderewski", "Poparcie Ameryki i prezydenta Wilsona"),
    ("daszynski", "Program reform: 8 godzin pracy, prawa kobiet"),
    ("korfanty", "Upomnienie się o ziemie zaboru pruskiego w Reichstagu"),
    ("witos", "Przejęcie Galicji i głos polskiej wsi"),
    ("rada", "Orędzie z 7 X i pokojowe przekazanie władzy"),
    ("moraczewska", "Walka o prawa wyborcze kobiet"),
]
