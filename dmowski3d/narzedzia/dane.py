"""Treść gry „Roman Dmowski. Droga do Wersalu 3D” — kampanie 1914–1919.

Uruchom:  python narzedzia/dane.py   ->  godot/dane/dane.json
Fakty historyczne są podane tak, jak w podręcznikach; postać Hanny jest fikcyjna.
"""
import json
import os
import random

W, H = 36, 24

# Znaki mapy: '.' trawa  'T' drzewa  '~' woda  '#' most  '=' ulica  'B' plac (bruk)
# 'K' zabudowa miejska (dekoracja)  'D' teren zajęty przez zabytek-dekorację
# '^' góry  'P' pole  'X' ziemia niczyja na froncie


def pusta(z="."):
    return [[z] * W for _ in range(H)]


def prost(m, x0, y0, x1, y1, z):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if 0 <= x < W and 0 <= y < H:
                m[y][x] = z


def mapa_warszawa():
    m = pusta()
    r = random.Random(1914)
    prost(m, 28, 0, 30, 23, "~")                       # Wisła
    for y in range(H):
        for x in range(31, W):
            if r.random() < .55:
                m[y][x] = "T"                          # nadwiślańskie łęgi na Pradze
    prost(m, 17, 1, 26, 7, "K")                        # Stare Miasto
    prost(m, 20, 3, 23, 5, "B")                        # Rynek Starego Miasta
    prost(m, 22, 8, 27, 11, "B")                       # plac Zamkowy
    prost(m, 25, 8, 27, 10, "D")                       # Zamek Królewski
    prost(m, 9, 8, 14, 11, "T")                        # Ogród Saski
    prost(m, 0, 0, 6, 4, "K")
    prost(m, 0, 20, 5, 23, "K")
    prost(m, 0, 12, 27, 12, "=")
    prost(m, 24, 12, 24, 23, "=")                      # Krakowskie Przedmieście
    prost(m, 0, 18, 27, 18, "=")                       # Aleje Jerozolimskie
    prost(m, 28, 18, 30, 18, "#")                      # most
    prost(m, 31, 18, 35, 18, "=")
    prost(m, 8, 0, 8, 11, "=")
    return m


def mapa_lozanna():
    m = pusta()
    r = random.Random(1917)
    prost(m, 0, 17, 35, 23, "~")                       # Jezioro Genewskie
    prost(m, 0, 21, 35, 23, "^")                       # Alpy na drugim brzegu
    prost(m, 0, 16, 35, 16, "=")                       # promenada
    prost(m, 12, 0, 12, 15, "=")
    prost(m, 26, 0, 26, 15, "=")
    prost(m, 0, 7, 35, 7, "=")
    prost(m, 0, 0, 4, 5, "K")
    prost(m, 14, 0, 19, 3, "K")
    prost(m, 15, 0, 17, 2, "D")                        # katedra
    prost(m, 30, 0, 35, 5, "K")
    for (x0, y0, x1, y1) in [(0, 9, 4, 14), (31, 9, 35, 14)]:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if r.random() < .75:
                    m[y][x] = "T"
    return m


def mapa_francja():
    m = pusta()
    r = random.Random(1918)
    prost(m, 0, 15, 22, 23, "P")                       # pola pszenicy
    for y in range(0, 9):
        for x in range(0, 6):
            if r.random() < .8:
                m[y][x] = "T"
    prost(m, 30, 0, 35, 23, "X")                       # ziemia niczyja
    prost(m, 0, 11, 26, 11, "=")
    prost(m, 15, 0, 15, 23, "=")
    prost(m, 18, 0, 22, 3, "K")                        # wioska
    prost(m, 7, 18, 10, 21, "K")
    return m


def mapa_paryz():
    m = pusta()
    r = random.Random(1919)
    prost(m, 0, 10, 35, 11, "~")                       # Sekwana
    prost(m, 0, 9, 35, 9, "=")
    prost(m, 0, 12, 35, 12, "=")
    for x0 in (8, 24):
        prost(m, x0, 10, x0 + 1, 11, "#")
        prost(m, x0, 0, x0 + 1, 8, "=")
        prost(m, x0, 13, x0 + 1, 23, "=")
    prost(m, 0, 0, 6, 7, "K")
    prost(m, 11, 0, 22, 3, "K")
    prost(m, 27, 0, 35, 7, "K")
    for y in range(14, 24):
        for x in range(0, 7):
            if r.random() < .45:
                m[y][x] = "T"                          # Pola Marsowe
    prost(m, 3, 16, 5, 18, "D")                        # wieża Eiffla
    prost(m, 13, 13, 18, 15, "D")                      # Quai d'Orsay
    prost(m, 18, 15, 26, 22, "B")                      # plac z mapami granic
    prost(m, 28, 16, 35, 23, "D")                      # Wersal (w oddali)
    return m


# ------------------------------------------------------------------ postacie
POSTACIE = {
    "dmowski": dict(imie="Roman Dmowski", rola="polityk i dyplomata"),
    "hanna": dict(imie="Hanna", rola="sekretarka Komitetu (postać fikcyjna)"),
    "zamoyski": dict(imie="Maurycy Zamoyski", rola="działacz Komitetu Narodowego Polskiego"),
    "haller": dict(imie="gen. Józef Haller", rola="dowódca Błękitnej Armii"),
    "paderewski": dict(imie="Ignacy Jan Paderewski", rola="pianista i premier"),
    "clemenceau": dict(imie="Georges Clemenceau", rola="premier Francji"),
    "wilson": dict(imie="Woodrow Wilson", rola="prezydent USA"),
    "pilsudski": dict(imie="Józef Piłsudski", rola="Naczelnik Państwa"),
    "narrator": dict(imie="Kronikarz", rola=""),
}

ZASOBY = [
    dict(id="fundusze", nazwa="Fundusze", ikona="fundusze", start=120),
    dict(id="poparcie", nazwa="Poparcie aliantów", ikona="poparcie", start=10),
    dict(id="prasa", nazwa="Prasa i opinia", ikona="prasa", start=10),
    dict(id="ochotnicy", nazwa="Ochotnicy", ikona="ochotnicy", start=0),
]

# ------------------------------------------------------------------ budynki
BUDYNKI = {
    "kwatera": dict(nazwa="Kwatera działaczy", w=1, h=1, koszt={"fundusze": 15}, czas=1, mieszk=4,
                    opis="Mieszkanie dla 4 działaczy. Działacze płacą składki i pracują w placówkach."),
    "biuro": dict(nazwa="Biuro informacyjne", w=2, h=2, koszt={"fundusze": 30}, czas=2, prod={"poparcie": 2}, rob=2,
                  opis="Pisze listy i memoriały do rządów aliantów. Daje 2 punkty poparcia dziennie."),
    "redakcja": dict(nazwa="Redakcja gazety", w=2, h=2, koszt={"fundusze": 30}, czas=2, prod={"prasa": 3}, rob=3,
                     wymog="ulica", opis="Stawiaj przy ulicy lub placu. Artykuły o sprawie polskiej: +3 prasy dziennie."),
    "komitet": dict(nazwa="Komitet pomocy", w=2, h=2, koszt={"fundusze": 25, "prasa": 5}, czas=2,
                    prod={"fundusze": 6}, rob=2, opis="Zbiera datki od Polonii i przyjaciół Polski: +6 funduszy dziennie."),
    "werbunek": dict(nazwa="Punkt werbunkowy", w=2, h=2, koszt={"fundusze": 30, "poparcie": 10}, czas=2,
                     prod={"ochotnicy": 3}, rob=2, opis="Zapisuje ochotników do polskiego wojska: +3 ochotników dziennie."),
    "oboz": dict(nazwa="Obóz szkoleniowy", w=3, h=2, koszt={"fundusze": 45, "poparcie": 15}, czas=3,
                 prod={"ochotnicy": 5}, rob=4, opis="Namioty i plac ćwiczeń dla żołnierzy: +5 ochotników dziennie."),
    "szpital": dict(nazwa="Szpital polowy", w=2, h=2, koszt={"fundusze": 30}, czas=2, prod={"poparcie": 1, "prasa": 1},
                    rob=2, opis="Opieka nad rannymi żołnierzami. Zyskuje szacunek: +1 poparcia i +1 prasy dziennie."),
    "knp_warszawa": dict(nazwa="Siedziba Komitetu Narodowego", w=2, h=2, koszt={"fundusze": 60, "prasa": 20}, czas=4,
                         zabytek=True, opis="Komitet Narodowy Polski powstał w Warszawie 25 listopada 1914 r."),
    "knp_lozanna": dict(nazwa="Siedziba KNP w Lozannie", w=2, h=2, koszt={"fundusze": 70, "prasa": 30, "poparcie": 20},
                        czas=4, zabytek=True, opis="W sierpniu 1917 r. Komitet odrodził się w Lozannie, potem w Paryżu."),
    "kwatera_glowna": dict(nazwa="Kwatera główna Armii Polskiej", w=3, h=2,
                           koszt={"fundusze": 80, "poparcie": 30, "ochotnicy": 15}, czas=4, zabytek=True,
                           opis="Dowództwo Armii Polskiej we Francji — Błękitnej Armii."),
    "pozycja": dict(nazwa="Pozycja na froncie", w=2, h=2, koszt={"ochotnicy": 20, "fundusze": 15}, czas=3,
                    zabytek=True, opis="Polscy żołnierze bronią odcinka frontu w Szampanii (1918)."),
    "delegacja": dict(nazwa="Biuro Delegacji Polskiej", w=2, h=2, koszt={"fundusze": 70, "poparcie": 40, "prasa": 30},
                      czas=4, zabytek=True, opis="Tu pracowali eksperci: geografowie, historycy, ekonomiści."),
    "sprawa_wielkopolska": dict(nazwa="Sprawa Wielkopolski", w=2, h=2, koszt={"poparcie": 35, "prasa": 25}, czas=3,
                                zabytek=True, opis="Memoriał o Wielkopolsce — ziemi, która sama się wyzwoliła."),
    "sprawa_pomorze": dict(nazwa="Sprawa Pomorza i Gdańska", w=2, h=2, koszt={"poparcie": 45, "prasa": 25}, czas=3,
                           zabytek=True, min_pw=40, opis="Memoriał o dostępie do morza. Wymaga 40 PW."),
    "sprawa_slask": dict(nazwa="Sprawa Górnego Śląska", w=2, h=2, koszt={"poparcie": 40, "prasa": 30}, czas=3,
                         zabytek=True, min_pw=55, opis="Memoriał o Śląsku. Wymaga 55 PW."),
    "sprawa_warmia": dict(nazwa="Sprawa Warmii i Mazur", w=2, h=2, koszt={"poparcie": 35, "prasa": 30}, czas=3,
                          zabytek=True, min_pw=65, opis="Memoriał o Warmii, Mazurach i Powiślu. Wymaga 65 PW."),
}
MODEL_SPRAWY = "memorial"

ZASOBY_NAZWY = {"fundusze": "funduszy", "poparcie": "poparcia", "prasa": "prasy", "ochotnicy": "ochotników",
                "pw": "PW"}

# ------------------------------------------------------------------ przedmioty
# efekt: {"mnoznik": zasób, "x": wartość} / {"koszt": x} / {"pw_dziennie": n}
PRZEDMIOTY = {
    "kompas": dict(nazwa="Kompas podróżnika", ikona="kompas", uzycie="kompas",
                   opis="Dmowski dużo podróżował: Petersburg, Londyn, Lozanna, Paryż, Waszyngton. Użyj (K), "
                        "aby zobaczyć kierunek do celu i działki do zabudowy."),
    "teczka": dict(nazwa="Teczka z memoriałami", ikona="teczka", uzycie=None, efekt={"mnoznik": "poparcie", "x": 1.25},
                   opis="Memoriał to pismo wyjaśniające sprawę politykom. Stale: poparcie +25%."),
    "datki": dict(nazwa="Datki Polonii", ikona="sakiewka", uzycie="zuzyj",
                  opis="Pieniądze zebrane przez Polaków w Ameryce. Użyj: +60 funduszy."),
    "paczka": dict(nazwa="Paczka z kraju", ikona="paczka", uzycie="zuzyj",
                   opis="Herbata, suchary i listy od rodzin. Użyj: przez 6 dni placówki pracują podwójnie."),
    "mapa": dict(nazwa="Mapa ziem polskich", ikona="mapa", uzycie="plan",
                 opis="Mapa z zaznaczonymi zaborami. Użyj, aby zobaczyć mapę kampanii."),
    "legitymacja": dict(nazwa="Legitymacja KNP", ikona="legitymacja", uzycie=None,
                        efekt={"mnoznik": "prasa", "x": 1.25},
                        opis="Dokument członka Komitetu Narodowego Polskiego. Stale: prasa +25%."),
    "nota": dict(nazwa="Nota o uznaniu Komitetu", ikona="nota", uzycie=None, efekt={"mnoznik": "fundusze", "x": 1.25},
                 opis="Francja, Wielka Brytania, Włochy i USA uznały KNP za przedstawicielstwo Polaków. "
                      "Stale: fundusze +25%."),
    "odznaka": dict(nazwa="Odznaka Błękitnej Armii", ikona="odznaka", uzycie=None,
                    efekt={"mnoznik": "ochotnicy", "x": 1.5},
                    opis="Prezent od generała Hallera. Stale: ochotnicy +50%."),
    "telegram": dict(nazwa="Telegram z 11 listopada", ikona="telegram", uzycie=None, efekt={"pw_dziennie": 1},
                     opis="Wiadomość: rozejm na froncie, Polska odzyskuje niepodległość! Stale: +1 PW dziennie."),
    "punkty": dict(nazwa="Orędzie Wilsona", ikona="dokument", uzycie=None, efekt={"koszt": 0.85},
                   opis="14 punktów prezydenta Wilsona. Punkt 13. mówi o niepodległej Polsce z dostępem do morza. "
                        "Stale: memoriały tańsze o 15%."),
    "pioro": dict(nazwa="Pióro z Sali Lustrzanej", ikona="pioro", uzycie=None,
                  opis="Pamiątka z 28 czerwca 1919 r. — dnia podpisania traktatu wersalskiego."),
}

# ------------------------------------------------------------------ Księga Wiedzy
WIEDZA = {
    "dmowski": ("Roman Dmowski (1864–1939)",
                "Polityk, pisarz i dyplomata, urodzony na warszawskiej Pradze. Studiował nauki przyrodnicze. "
                "Był jednym z twórców obozu narodowego (Narodowej Demokracji, zwanej endecją). W czasie I wojny "
                "światowej przekonywał polityków Francji, Wielkiej Brytanii i USA, że Europa potrzebuje "
                "niepodległej Polski. W 1919 r. stał na czele polskiej delegacji na konferencji pokojowej w Paryżu."),
    "kompas": ("Kompas i strony świata",
               "Igła kompasu to mały magnes — wskazuje północ. Główne strony świata to północ, południe, wschód "
               "i zachód. Dyplomaci w podróży korzystali z map, rozkładów pociągów i kompasów."),
    "zabory": ("Polska pod zaborami",
               "Od 1795 r. Polski nie było na mapie. Jej ziemie podzieliły trzy państwa: Rosja, Prusy (później "
               "Niemcy) i Austria. Polacy przez 123 lata pielęgnowali język, historię i nadzieję na wolność."),
    "wielka_wojna": ("I wojna światowa (1914–1918)",
                     "W 1914 r. wybuchła wielka wojna. Po jednej stronie stanęły Niemcy i Austro-Węgry, po drugiej "
                     "Rosja, Francja i Wielka Brytania (ententa). Zaborcy walczyli ze sobą — to dało Polakom "
                     "szansę na odzyskanie niepodległości."),
    "orientacje": ("Dwie drogi do niepodległości",
                   "Józef Piłsudski tworzył Legiony u boku Austro-Węgier i liczył na pokonanie Rosji. Roman Dmowski "
                   "uważał, że największym zagrożeniem są Niemcy, i stawiał na Rosję, a potem na Francję i Wielką "
                   "Brytanię. Choć się spierali, obaj pracowali dla wolnej Polski."),
    "knp": ("Komitet Narodowy Polski",
            "Komitet powstał w Warszawie 25 listopada 1914 r. Kierował nim Roman Dmowski. W 1915 r. Niemcy zajęli "
            "Warszawę, więc Dmowski wyjechał na Zachód. W sierpniu 1917 r. odnowiono Komitet w Lozannie, a potem "
            "przeniesiono go do Paryża. Alianci uznali go za przedstawicielstwo Polaków."),
    "memorial": ("Memoriały i dyplomacja",
                 "Dmowski mieszkał w czasie wojny w Londynie i pisał memoriały — długie pisma dla rządów "
                 "i dziennikarzy. Tłumaczył w nich, gdzie leżą ziemie polskie i dlaczego Polska jest potrzebna "
                 "Europie. Dyplomacja to rozwiązywanie sporów rozmową, a nie wojną."),
    "akt_5_listopada": ("Akt 5 listopada 1916",
                        "Niemcy i Austro-Węgry ogłosiły utworzenie Królestwa Polskiego na ziemiach zabranych Rosji. "
                        "Chciały pozyskać polskich żołnierzy. Państwo to nie było naprawdę niepodległe, ale sprawa "
                        "polska stała się ważna dla wszystkich państw."),
    "rewolucja": ("Rewolucje w Rosji (1917)",
                  "W 1917 r. w Rosji upadł car, a potem władzę przejęli bolszewicy. Rosja wycofała się z wojny. "
                  "Dla Dmowskiego oznaczało to, że Polacy mogą prosić Francję i Wielką Brytanię o pełną "
                  "niepodległość Polski."),
    "blekitna_armia": ("Błękitna Armia",
                       "Armię Polską we Francji utworzono dekretem prezydenta Francji z 4 czerwca 1917 r. Żołnierze "
                       "nosili błękitne francuskie mundury — stąd nazwa. Wielu ochotników przybyło z Polonii "
                       "amerykańskiej. Latem 1918 r. Polacy walczyli w Szampanii, a w 1919 r. armia wróciła "
                       "do Polski."),
    "haller": ("Generał Józef Haller (1873–1960)",
               "Oficer, który przedostał się do Francji i jesienią 1918 r. objął dowództwo Armii Polskiej. "
               "Nazywano go „błękitnym generałem”. W 1920 r. dokonał zaślubin Polski z morzem w Pucku."),
    "punkt13": ("13. punkt Wilsona",
                "8 stycznia 1918 r. prezydent USA Woodrow Wilson ogłosił 14 punktów pokoju. Punkt 13. mówił, że "
                "powinno powstać niepodległe państwo polskie z wolnym i bezpiecznym dostępem do morza."),
    "paderewski": ("Ignacy Jan Paderewski (1860–1941)",
                   "Wybitny pianista, sławny na całym świecie. W czasie wojny w USA zbierał pieniądze dla Polaków "
                   "i przekonywał Amerykanów do sprawy polskiej. W 1919 r. był premierem i razem z Dmowskim "
                   "podpisał traktat wersalski."),
    "listopad": ("11 listopada 1918",
                 "11 listopada 1918 r. Niemcy podpisały rozejm i skończyła się wojna. Tego dnia Rada Regencyjna "
                 "przekazała Józefowi Piłsudskiemu dowództwo nad wojskiem. Dziś to Narodowe Święto Niepodległości."),
    "pilsudski": ("Józef Piłsudski (1867–1935)",
                  "Twórca Legionów i Naczelnik Państwa od listopada 1918 r. Zgodził się, by Komitet Narodowy "
                  "Polski i delegacja Dmowskiego reprezentowały Polskę na konferencji pokojowej. Dzięki temu "
                  "Polska mówiła w Paryżu jednym głosem."),
    "powstanie": ("Powstanie wielkopolskie",
                  "26 grudnia 1918 r. do Poznania przyjechał Paderewski. Następnego dnia, 27 grudnia, wybuchło "
                  "powstanie wielkopolskie. Powstańcy wyzwolili większość Wielkopolski — to jedno z niewielu "
                  "zwycięskich polskich powstań."),
    "konferencja": ("Konferencja pokojowa w Paryżu",
                    "18 stycznia 1919 r. w Paryżu zebrali się zwycięzcy wojny, by ustalić nowe granice Europy. "
                    "Najważniejsze decyzje podejmowali przywódcy USA, Francji, Wielkiej Brytanii i Włoch. Polskę "
                    "reprezentowali Roman Dmowski i Ignacy Jan Paderewski."),
    "przemowienie": ("Przemówienie przed Radą Dziesięciu",
                     "29 stycznia 1919 r. Dmowski przedstawił polskie postulaty przed Radą Dziesięciu. Mówił około "
                     "5 godzin, na zmianę po francusku i po angielsku, korzystając z map i liczb. Wielu słuchaczy "
                     "podziwiało jego wiedzę."),
    "wielkopolska": ("Wielkopolska",
                     "Dzięki powstaniu i decyzjom konferencji prawie cała Wielkopolska wróciła do Polski. Poznań "
                     "stał się jednym z najważniejszych polskich miast."),
    "pomorze": ("Pomorze i Wolne Miasto Gdańsk",
                "Polska otrzymała większość Pomorza Gdańskiego, czyli dostęp do Morza Bałtyckiego. Gdańsk nie "
                "wrócił do Polski — został Wolnym Miastem pod opieką Ligi Narodów."),
    "slask": ("Górny Śląsk",
              "O Górnym Śląsku miał zdecydować plebiscyt, czyli głosowanie mieszkańców (1921). Po plebiscycie "
              "i trzech powstaniach śląskich Polska otrzymała w 1922 r. część Górnego Śląska."),
    "warmia": ("Warmia, Mazury i Powiśle",
               "Tu także zorganizowano plebiscyt (1920). Większość głosujących wybrała Niemcy, a Polska otrzymała "
               "tylko kilka wsi. Plebiscyty pokazały, że granice zależały też od woli mieszkańców."),
    "traktat": ("Traktat wersalski (28 czerwca 1919)",
                "Traktat pokojowy z Niemcami podpisano w Sali Lustrzanej pałacu w Wersalu. Za Polskę podpisali "
                "Ignacy Jan Paderewski i Roman Dmowski. Traktat wszedł w życie 10 stycznia 1920 r. Tego samego dnia "
                "Polska podpisała mały traktat wersalski o ochronie mniejszości narodowych."),
    "spor": ("Spory o Romana Dmowskiego",
             "Historycy doceniają pracę Dmowskiego dla niepodległości i jego sukces w Paryżu. Krytykują jednak "
             "część jego poglądów, zwłaszcza niechęć wobec mniejszości narodowych, w tym Żydów. Dobra lekcja "
             "historii pokazuje i zasługi, i błędy."),
}
KARTY_STARTOWE = ["dmowski", "kompas", "zabory"]
KARTA_BUDYNKU = {"knp_warszawa": "knp", "kwatera_glowna": "blekitna_armia", "delegacja": "konferencja",
                 "sprawa_wielkopolska": "wielkopolska", "sprawa_pomorze": "pomorze", "sprawa_slask": "slask",
                 "sprawa_warmia": "warmia"}
RANGI = [[0, "Wolontariusz"], [25, "Sekretarz Komitetu"], [50, "Publicysta"], [85, "Dyplomata"],
         [130, "Ojciec Niepodległości"]]


def Q(pytanie, poprawna, zle, wyjasnienie):
    return dict(pytanie=pytanie, poprawna=poprawna, zle=zle, wyjasnienie=wyjasnienie)


QUIZ_GLOWNY = {
    "zamoyski:1": Q("Które trzy państwa dokonały rozbiorów Polski?", "Rosja, Prusy i Austria",
                    ["Francja, Anglia i Hiszpania", "Szwecja, Dania i Norwegia"],
                    "Ostatni rozbiór był w 1795 r. Polska zniknęła z mapy na 123 lata."),
    "zamoyski:2": Q("Co ogłosiły Niemcy i Austro-Węgry 5 listopada 1916 r.?",
                    "Utworzenie Królestwa Polskiego, zależnego od nich",
                    ["Koniec wojny", "Pełną niepodległość Polski z Gdańskiem"],
                    "Akt 5 listopada nie dał prawdziwej niepodległości, ale sprawa polska stała się sprawą europejską."),
    "haller:3": Q("Skąd wzięła się nazwa „Błękitna Armia”?", "Od koloru francuskich mundurów",
                  ["Od koloru polskich flag", "Od jeziora, nad którym ćwiczyła"],
                  "Żołnierze nosili mundury w kolorze „horyzontalnego błękitu” armii francuskiej."),
    "paderewski:4": Q("Kiedy wybuchło powstanie wielkopolskie?", "27 grudnia 1918 r.",
                      ["11 listopada 1918 r.", "3 maja 1791 r."],
                      "Dzień wcześniej do Poznania przyjechał Paderewski, a mieszkańcy go entuzjastycznie powitali."),
    "clemenceau:4": Q("Ile czasu Dmowski przemawiał przed Radą Dziesięciu 29 stycznia 1919 r.?",
                      "Około 5 godzin, po francusku i angielsku", ["5 minut, po polsku", "Tydzień bez przerwy"],
                      "Dmowski znał świetnie języki i przedstawił sprawę polską z mapami i liczbami."),
    "wilson:4": Q("O czym mówił 13. punkt orędzia Wilsona?", "O niepodległej Polsce z dostępem do morza",
                  ["O podziale Polski", "O budowie kolei w Ameryce"],
                  "Wilson ogłosił 14 punktów 8 stycznia 1918 r."),
}

ZAGADKI = {
    "hanna": [
        Q("Ile lat Polska była pod zaborami?", "123 lata", ["13 lat", "300 lat"], "Od 1795 do 1918 r."),
        Q("Kiedy obchodzimy Narodowe Święto Niepodległości?", "11 listopada", ["3 maja", "1 września"],
          "11 listopada 1918 r. Piłsudski przejął dowództwo wojska."),
        Q("Kto podpisał traktat wersalski w imieniu Polski?", "Paderewski i Dmowski", ["Piłsudski i Haller",
          "Mickiewicz i Słowacki"], "Podpisy złożono 28 czerwca 1919 r. w Sali Lustrzanej."),
        Q("Czym jest plebiscyt?", "Głosowaniem mieszkańców, do którego państwa chcą należeć",
          ["Rodzajem armaty", "Tańcem ludowym"], "Plebiscyty odbyły się m.in. na Górnym Śląsku i Warmii."),
    ],
    "zamoyski": [
        Q("W którym mieście powstał Komitet Narodowy Polski w 1914 r.?", "W Warszawie", ["W Krakowie", "W Gdańsku"],
          "Komitet powstał 25 listopada 1914 r."),
        Q("Gdzie odnowiono Komitet Narodowy Polski w 1917 r.?", "W Lozannie (Szwajcaria)", ["W Moskwie", "W Rzymie"],
          "Z Lozanny Komitet szybko przeniósł się do Paryża."),
        Q("Co to jest memoriał?", "Pismo wyjaśniające ważną sprawę politykom", ["Pomnik ze spiżu", "Pociąg pancerny"],
          "Dmowski napisał wiele memoriałów o sprawie polskiej."),
        Q("Który kraj zajął Warszawę w sierpniu 1915 r.?", "Niemcy", ["Francja", "Szwajcaria"],
          "Wojska rosyjskie wycofały się, a Warszawa znalazła się pod okupacją niemiecką."),
    ],
    "haller": [
        Q("Z jakiego kraju przybyło wielu ochotników do Błękitnej Armii?", "Z USA (Polonia amerykańska)",
          ["Z Japonii", "Z Australii"], "Polacy mieszkający w Ameryce masowo zgłaszali się do wojska."),
        Q("Jak nazywano generała Hallera?", "Błękitnym generałem", ["Żelaznym kanclerzem", "Lwem Północy"],
          "Od koloru mundurów jego armii."),
        Q("Gdzie w 1920 r. Haller dokonał zaślubin Polski z morzem?", "W Pucku", ["W Krakowie", "W Zakopanem"],
          "Wrzucił do Bałtyku pierścień na znak, że Polska wróciła nad morze."),
    ],
    "paderewski": [
        Q("Z jakiego zawodu słynął na świecie Paderewski?", "Był pianistą i kompozytorem", ["Był lotnikiem",
          "Był piłkarzem"], "Jego koncerty gromadziły tłumy w Ameryce i Europie."),
        Q("Jaką funkcję objął Paderewski w styczniu 1919 r.?", "Premiera i ministra spraw zagranicznych",
          ["Króla Polski", "Burmistrza Paryża"], "Paderewski łączył obóz Piłsudskiego i Dmowskiego."),
    ],
    "clemenceau": [
        Q("Jak nazywał się pałac pod Paryżem, w którym podpisano traktat z Niemcami?", "Wersal",
          ["Luwr", "Buckingham"], "Podpisano go w Sali Lustrzanej."),
        Q("Co otrzymał Gdańsk na mocy traktatu wersalskiego?", "Status Wolnego Miasta", ["Status stolicy Polski",
          "Nic się nie zmieniło"], "Gdańsk był pod opieką Ligi Narodów."),
    ],
    "wilson": [
        Q("Ile punktów miało orędzie pokojowe Wilsona?", "14", ["3", "100"], "Punkt 13. dotyczył Polski."),
        Q("Jak nazywała się organizacja powołana do pilnowania pokoju po wojnie?", "Liga Narodów",
          ["NATO", "Unia Europejska"], "Ligę Narodów utworzono na mocy traktatu wersalskiego."),
    ],
}

# ------------------------------------------------------------------ kampanie
DOSTEPNE_WSZYSTKIE = ["kwatera", "biuro", "redakcja", "komitet"]
ROZDZIALY = {
    1: dict(
        tytul="Kampania I: Komitet w Warszawie", lata="1914–1915", miejsce="Warszawa", mapa=mapa_warszawa(),
        styl="kamienica_wwa", start=[19, 13],
        npc={"zamoyski": [17, 14], "hanna": [22, 13]},
        dzialki=[["knp_warszawa", 19, 15, 0]],
        dekor=[["zamek", 26, 9.5, 0, 1.0], ["kolumna", 23.5, 9.5, 0, 1.0]],
        dostepne=DOSTEPNE_WSZYSTKIE + ["knp_warszawa"],
        wstep="Sierpień 1914 roku. Wybucha wielka wojna. Trzej zaborcy — Rosja, Niemcy i Austro-Węgry — walczą "
              "ze sobą, a Polacy służą w obcych armiach i muszą strzelać do siebie nawzajem.\n\n"
              "Roman Dmowski, polityk z Warszawy, uważa, że to szansa: jeśli Niemcy przegrają, Polska może się "
              "odrodzić. Trzeba zjednoczyć Polaków i zdobyć przyjaciół dla sprawy polskiej.\n\n"
              "Twoje zadanie: założyć w Warszawie Komitet Narodowy Polski.",
        cele=[["Porozmawiaj z Maurycym Zamoyskim", "rozmowa", "zamoyski", 1],
              ["Zbuduj 3 kwatery działaczy", "buduj", "kwatera", 3],
              ["Zbuduj redakcję gazety przy ulicy", "buduj", "redakcja", 1],
              ["Zbuduj komitet pomocy", "buduj", "komitet", 1],
              ["Otwórz Siedzibę Komitetu Narodowego", "buduj", "knp_warszawa", 1],
              ["Zbierz 40 punktów poparcia", "zasob", "poparcie", 40]],
        koniec=[["narrator", "25 listopada 1914 r. w Warszawie powstał Komitet Narodowy Polski."],
                ["narrator", "W sierpniu 1915 r. wojska niemieckie zajęły Warszawę. Dmowski wyjechał na Zachód, "
                             "by tam walczyć o sprawę polską — piórem i słowem."],
                ["dmowski", "Pojadę do Londynu. Muszę przekonać Anglików i Francuzów, że Europa potrzebuje Polski."],
                ["narrator", "Otrzymujesz: Legitymację KNP. Prasa +25%."]],
        nagroda="legitymacja", karty=["knp", "orientacje"]),
    2: dict(
        tytul="Kampania II: Dyplomata w Lozannie", lata="1915–1917", miejsce="Lozanna (Szwajcaria)",
        mapa=mapa_lozanna(), styl="willa", start=[19, 7],
        npc={"zamoyski": [16, 10], "hanna": [22, 9]},
        dzialki=[["knp_lozanna", 18, 10, 0]],
        dekor=[["katedra", 16, 1.5, 0, 1.0]],
        dostepne=DOSTEPNE_WSZYSTKIE + ["knp_lozanna"],
        wstep="Dmowski mieszka teraz w Londynie. Pisze memoriały, spotyka się z politykami i dziennikarzami. "
              "Wyjaśnia im, gdzie leżą ziemie polskie i dlaczego wolna Polska zapewni pokój w Europie.\n\n"
              "W 1917 r. wszystko się zmienia: w Rosji wybucha rewolucja, a Stany Zjednoczone przystępują do wojny. "
              "W sierpniu 1917 r. w neutralnej Szwajcarii, w Lozannie, Dmowski odnawia Komitet Narodowy Polski.\n\n"
              "Zdobądź poparcie aliantów, by uznali Komitet za głos Polaków!",
        cele=[["Porozmawiaj z Maurycym Zamoyskim", "rozmowa", "zamoyski", 2],
              ["Zbuduj 2 biura informacyjne", "buduj", "biuro", 2],
              ["Zbuduj 2 redakcje gazet", "buduj", "redakcja", 2],
              ["Otwórz Siedzibę KNP w Lozannie", "buduj", "knp_lozanna", 1],
              ["Zbierz 80 punktów poparcia", "zasob", "poparcie", 80],
              ["Zdobądź 40 Punktów Wiedzy", "wiedza", None, 40]],
        koniec=[["narrator", "Komitet przeniósł się z Lozanny do Paryża. Jesienią 1917 r. Francja, Wielka Brytania, "
                             "Włochy, a potem USA uznały go za przedstawicielstwo Polaków."],
                ["zamoyski", "Panie Romanie, mamy to! Polska znów ma głos wśród narodów."],
                ["narrator", "Otrzymujesz: Notę o uznaniu Komitetu. Fundusze +25%."]],
        nagroda="nota", karty=["rewolucja", "memorial"]),
    3: dict(
        tytul="Kampania III: Błękitna Armia", lata="1917–1918", miejsce="Francja",
        mapa=mapa_francja(), styl="dom_fr", start=[12, 12],
        npc={"haller": [13, 9], "hanna": [7, 12], "zamoyski": [17, 13]},
        dzialki=[["kwatera_glowna", 8, 7, 0], ["pozycja", 27, 3, 1.5708], ["pozycja", 27, 9, 1.5708],
                 ["pozycja", 27, 16, 1.5708]],
        dekor=[],
        dostepne=DOSTEPNE_WSZYSTKIE + ["werbunek", "oboz", "szpital", "kwatera_glowna", "pozycja"],
        wstep="Polska potrzebuje własnego wojska, które będzie walczyć po stronie aliantów. Dekretem z 4 czerwca "
              "1917 r. Francja zgodziła się na utworzenie Armii Polskiej. Ochotnicy przybywają z Ameryki, z Francji "
              "i z niewoli.\n\n"
              "Żołnierze dostają błękitne francuskie mundury. Latem 1918 r. Polacy walczą w Szampanii, a jesienią "
              "dowództwo obejmuje generał Józef Haller.\n\n"
              "Zbuduj obóz, zbierz ochotników i obsadź trzy pozycje na froncie!",
        cele=[["Porozmawiaj z generałem Hallerem", "rozmowa", "haller", 3],
              ["Zbuduj 2 punkty werbunkowe", "buduj", "werbunek", 2],
              ["Zbuduj obóz szkoleniowy", "buduj", "oboz", 1],
              ["Zbuduj szpital polowy", "buduj", "szpital", 1],
              ["Otwórz Kwaterę główną Armii Polskiej", "buduj", "kwatera_glowna", 1],
              ["Obsadź 3 pozycje na froncie", "buduj", "pozycja", 3]],
        koniec=[["narrator", "11 listopada 1918 r. Niemcy podpisały rozejm. Wojna się skończyła!"],
                ["pilsudski", "Telegram z Warszawy: przejąłem dowództwo nad wojskiem. Polska jest wolna! "
                              "Teraz trzeba wywalczyć jej granice."],
                ["haller", "Moi żołnierze są gotowi wrócić do Ojczyzny. Panie Dmowski — teraz pana kolej: Paryż!"],
                ["narrator", "Otrzymujesz: Telegram z 11 listopada. Codziennie +1 Punkt Wiedzy."]],
        nagroda="telegram", karty=["listopad", "pilsudski"]),
    4: dict(
        tytul="Kampania IV: Konferencja w Paryżu", lata="1919", miejsce="Paryż i Wersal",
        mapa=mapa_paryz(), styl="kamienica_paryz", start=[13, 7],
        npc={"paderewski": [11, 6], "hanna": [17, 6], "clemenceau": [12, 13], "wilson": [22, 13]},
        dzialki=[["delegacja", 14, 4, 0], ["sprawa_wielkopolska", 19, 16, 0], ["sprawa_pomorze", 23, 16, 0],
                 ["sprawa_slask", 19, 19, 0], ["sprawa_warmia", 23, 19, 0]],
        dekor=[["wieza_eiffla", 4.5, 17.5, 0, 1.0], ["quai_dorsay", 16, 14.5, 0, 1.0],
               ["wersal", 32, 20, 0, 1.0]],
        dostepne=DOSTEPNE_WSZYSTKIE + ["delegacja", "sprawa_wielkopolska", "sprawa_pomorze", "sprawa_slask",
                                       "sprawa_warmia"],
        wstep="18 stycznia 1919 r. w Paryżu rozpoczyna się konferencja pokojowa. Zwycięzcy wojny będą rysować nowe "
              "granice Europy.\n\n"
              "Piłsudski i Komitet Narodowy porozumieli się: Paderewski zostaje premierem, a Dmowski stoi na czele "
              "delegacji w Paryżu. Polska mówi jednym głosem!\n\n"
              "Przygotuj memoriały o każdej ziemi polskiej, wygłoś przemówienie przed Radą Dziesięciu "
              "i doprowadź do podpisania traktatu.",
        cele=[["Porozmawiaj z premierem Paderewskim", "rozmowa", "paderewski", 4],
              ["Otwórz Biuro Delegacji Polskiej", "buduj", "delegacja", 1],
              ["Wygłoś przemówienie przed Radą Dziesięciu (Clemenceau)", "rozmowa", "clemenceau", 4],
              ["Przygotuj memoriał o Wielkopolsce", "buduj", "sprawa_wielkopolska", 1],
              ["Przygotuj memoriał o Pomorzu i Gdańsku", "buduj", "sprawa_pomorze", 1],
              ["Przygotuj memoriał o Górnym Śląsku", "buduj", "sprawa_slask", 1],
              ["Przygotuj memoriał o Warmii i Mazurach", "buduj", "sprawa_warmia", 1],
              ["Porozmawiaj z prezydentem Wilsonem", "rozmowa", "wilson", 4]],
        koniec=[["narrator", "28 czerwca 1919 r., Sala Lustrzana w Wersalu. Przedstawiciele państw podpisują "
                             "traktat pokojowy z Niemcami."],
                ["paderewski", "Panie Romanie, podpiszmy razem. To podpis za całą Polskę."],
                ["dmowski", "Po 123 latach niewoli Polska wraca na mapę Europy."],
                ["narrator", "Otrzymujesz: Pióro z Sali Lustrzanej."]],
        nagroda="pioro", karty=["traktat", "spor"]),
}

ROZMOWY = {
    "zamoyski:1": dict(
        kwestie=[["zamoyski", "Panie Romanie! Wojna podzieliła Polaków — jedni walczą dla cara, inni dla cesarza."],
                 ["dmowski", "Dlatego potrzebujemy organizacji, która będzie mówić w imieniu wszystkich Polaków."],
                 ["zamoyski", "Pomogę sfinansować Komitet. Ale potrzebujemy ludzi, gazety i pieniędzy."],
                 ["dmowski", "Zaczniemy od kwater dla działaczy i redakcji. Słowo drukowane ma wielką siłę."],
                 ["zamoyski", "A teraz sprawdzę, czy pamięta pan, skąd wzięła się nasza niewola..."]],
        nagroda="teczka", karty=["wielka_wojna"],
        po=[["zamoyski", "Redakcję stawiaj przy ulicy. Siedzibę Komitetu pokaże kompas (K)."]]),
    "zamoyski:2": dict(
        kwestie=[["zamoyski", "Witam w Lozannie! Szwajcaria jest neutralna — tu mogą spotykać się Polacy z całej "
                              "Europy."],
                 ["dmowski", "W Londynie napisałem kolejny memoriał. Anglicy zaczynają rozumieć sprawę polską."],
                 ["zamoyski", "A Niemcy próbują nas przekupić obietnicami. Pamięta pan, co stało się w listopadzie "
                              "1916 roku?"]],
        nagroda="mapa", karty=["akt_5_listopada"],
        po=[["zamoyski", "Biura informacyjne zdobędą nam poparcie rządów. Czytaj też Księgę Wiedzy (L)!"]]),
    "haller:3": dict(
        kwestie=[["haller", "Melduję się, panie prezesie! Generał Józef Haller."],
                 ["dmowski", "Generale, Armia Polska we Francji to nasz najważniejszy argument. Alianci zobaczą, "
                             "że Polacy walczą razem z nimi."],
                 ["haller", "Potrzebujemy punktów werbunkowych, obozu i szpitala. Ochotnicy płyną z Ameryki!"],
                 ["haller", "Ale najpierw pytanie: wie pan, czemu mówią na nas „Błękitna Armia”?"]],
        nagroda="odznaka", karty=["haller"],
        po=[["haller", "Pozycje na froncie są na wschodzie — kompas (K) wskaże drogę."]]),
    "paderewski:4": dict(
        kwestie=[["paderewski", "Romanie! Przyjechałem prosto z Warszawy. Jestem teraz premierem."],
                 ["dmowski", "Ignacy, cieszę się. Razem z Naczelnikiem Piłsudskim pokazaliśmy, że umiemy się "
                             "porozumieć."],
                 ["paderewski", "W Wielkopolsce Polacy sami wywalczyli wolność. Wiesz, kiedy to się zaczęło?"]],
        nagroda="datki", karty=["paderewski", "powstanie"],
        po=[["paderewski", "Memoriały o granicach przygotuj na placu z mapami. Każdy wymaga wiedzy (PW)."]]),
    "clemenceau:4": dict(
        kwestie=[["clemenceau", "Monsieur Dmowski, Rada Dziesięciu czeka. Ma pan głos."],
                 ["dmowski", "Panowie, Polska była przez wieki tarczą Europy. Pokażę wam na mapie, gdzie mieszkają "
                             "Polacy, i wyjaśnię, dlaczego wolna Polska jest potrzebna dla trwałego pokoju."],
                 ["narrator", "29 stycznia 1919 r. Dmowski mówi godzinami, na zmianę po francusku i po angielsku."],
                 ["clemenceau", "Impressionnant! Ale zanim zdecydujemy — powiedz mi, jak długo pan mówił?"]],
        nagroda="paczka", karty=["przemowienie"],
        po=[["clemenceau", "Przygotujcie memoriały o każdej spornej ziemi. Rada je rozpatrzy."]]),
    "wilson:4": dict(
        kwestie=[["wilson", "Mister Dmowski, I remember you. Spotkaliśmy się w Ameryce w 1918 roku."],
                 ["dmowski", "Panie prezydencie, Pana orędzie dało Polakom wielką nadzieję."],
                 ["wilson", "Every nation deserves freedom. Czy pamiętasz, co obiecywał mój 13. punkt?"]],
        nagroda="punkty", karty=["punkt13"],
        po=[["wilson", "Liga Narodów będzie strzec pokoju. Good luck!"]]),
}

LUZNE = {
    "hanna": [["hanna", "Jestem Hanna, sekretarka Komitetu. Pilnuję, by każdy list trafił do adresata."]],
    "zamoyski": [["zamoyski", "Polska odrodzi się dzięki pracy wielu ludzi — nie tylko polityków."]],
    "haller": [["haller", "Żołnierze ćwiczą od świtu. Wkrótce wrócimy do Polski!"]],
    "paderewski": [["paderewski", "Muzyka łączy ludzi. Dyplomacja też powinna."]],
    "clemenceau": [["clemenceau", "Pokój jest trudniejszy do wygrania niż wojna."]],
    "wilson": [["wilson", "Open diplomacy — dyplomacja powinna być jawna."]],
}

POMOC = [
    "STEROWANIE",
    "WASD / strzałki — chodzenie · Q / R lub prawy przycisk myszy — obrót kamery",
    "Kółko myszy — przybliżanie i oddalanie kamery",
    "E lub Spacja — rozmowa z postacią (podejdź blisko)",
    "Lewy przycisk myszy — wybór i stawianie placówki · Prawy — anuluj",
    "K — kompas   I — ekwipunek   L — Księga Wiedzy   M — muzyka   F11 — pełny ekran",
    "",
    "JAK GRAĆ",
    "Każda kampania toczy się w innym mieście — wykonuj cele z panelu po prawej.",
    "Co dzień (pasek na dole) placówki dają fundusze, poparcie, prasę i ochotników.",
    "Placówki potrzebują działaczy — buduj kwatery!",
    "Złote działki pokaże kompas (K). Czytaj Księgę Wiedzy i rozwiązuj zagadki postaci,",
    "aby zdobywać Punkty Wiedzy (PW) — memoriały o granicach wymagają wiedzy.",
]


def main():
    wynik = dict(
        tytul="Roman Dmowski. Droga do Wersalu 3D",
        postacie=POSTACIE, zasoby=ZASOBY, budynki=BUDYNKI, model_sprawy=MODEL_SPRAWY, zasoby_nazwy=ZASOBY_NAZWY,
        przedmioty=PRZEDMIOTY, wiedza={k: list(v) for k, v in WIEDZA.items()}, wiedza_kolejnosc=list(WIEDZA),
        karty_startowe=KARTY_STARTOWE, karta_budynku=KARTA_BUDYNKU, rangi=RANGI, quiz_glowny=QUIZ_GLOWNY,
        zagadki=ZAGADKI, rozmowy=ROZMOWY, luzne=LUZNE, pomoc=POMOC, start_ekwipunek=["kompas", "datki", "paczka"],
        rozdzialy={str(k): dict(v, mapa=["".join(w) for w in v["mapa"]]) for k, v in ROZDZIALY.items()},
        liczba_rozdzialow=len(ROZDZIALY),
    )
    # kontrola spójności map
    for k, r in ROZDZIALY.items():
        mapa = r["mapa"]
        for typ, x, y, _ in r["dzialki"]:
            b = BUDYNKI[typ]
            for yy in range(y, y + b["h"]):
                for xx in range(x, x + b["w"]):
                    assert mapa[yy][xx] in ".PB=", (k, typ, xx, yy, mapa[yy][xx])
        for n, (x, y) in r["npc"].items():
            assert mapa[y][x] in ".PB=#", (k, n, mapa[y][x])
        assert mapa[r["start"][1]][r["start"][0]] in ".PB=", (k, "start")
    tu = os.path.dirname(os.path.abspath(__file__))
    cel = os.path.join(tu, "..", "godot", "dane", "dane.json")
    os.makedirs(os.path.dirname(cel), exist_ok=True)
    with open(cel, "w", encoding="utf-8") as f:
        json.dump(wynik, f, ensure_ascii=False, indent=1)
    print("Zapisano", os.path.normpath(cel))


if __name__ == "__main__":
    main()
