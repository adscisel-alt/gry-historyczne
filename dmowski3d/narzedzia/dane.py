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
    "nauczyciel": dict(imie="Pan Damian", rola="nauczyciel historii"),
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
        nagroda="telegram", karty=["listopad", "pilsudski"], przerywnik="listopad"),
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
              ["Porozmawiaj z prezydentem Wilsonem", "rozmowa", "wilson", 4],
              ["Ułóż mapę granic Polski (mini-gra)", "minigra", "granice", 1]],
        koniec=[["narrator", "28 czerwca 1919 r., Sala Lustrzana w Wersalu. Przedstawiciele państw podpisują "
                             "traktat pokojowy z Niemcami."],
                ["paderewski", "Panie Romanie, podpiszmy razem. To podpis za całą Polskę."],
                ["dmowski", "Po 123 latach niewoli Polska wraca na mapę Europy."],
                ["narrator", "Otrzymujesz: Pióro z Sali Lustrzanej."]],
        nagroda="pioro", karty=["traktat", "spor"], przerywnik="traktat"),
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
                 ["clemenceau", "Delegaci będą zadawać pytania. Wybieraj najlepsze argumenty — "
                                "liczą się fakty, mapy i spokój."]],
        nagroda="paczka", karty=["przemowienie"], minigra="przemowienie",
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

# ------------------------------------------------------------------ przerywniki filmowe
PRZERYWNIKI = {
    "wstep": [
        ["nauczyciel", "Dzień dobry! Jestem pan Damian, wasz nauczyciel historii. Dziś zabiorę was w podróż "
                       "do lat 1914–1919."],
        ["nauczyciel", "Przez 123 lata Polski nie było na mapie. Jej ziemie podzieliły trzy państwa: Rosja, Prusy "
                       "i Austria."],
        ["nauczyciel", "W 1914 r. wybuchła wielka wojna, a zaborcy stanęli przeciwko sobie. Polacy zobaczyli w tym "
                       "szansę na wolność."],
        ["nauczyciel", "Do niepodległości prowadziło wiele dróg. Józef Piłsudski tworzył Legiony, a Roman Dmowski "
                       "przekonywał polityków na Zachodzie."],
        ["nauczyciel", "W tej grze wcielicie się w Romana Dmowskiego. Założycie Komitet Narodowy Polski, pomożecie "
                       "stworzyć Błękitną Armię i pojedziecie na konferencję pokojową do Paryża."],
        ["nauczyciel", "Pamiętajcie: historia to nie opowieść o bohaterach bez wad. Poznacie zasługi Dmowskiego, "
                       "ale też to, za co dziś się go krytykuje."],
        ["nauczyciel", "Czytajcie Księgę Wiedzy i karty postaci, rozwiązujcie zagadki — za każdą zdobędziecie "
                       "Punkty Wiedzy. Powodzenia!"],
    ],
    "przemowienie": [
        ["narrator", "29 stycznia 1919 r., Paryż, Quai d'Orsay. Obraduje Rada Dziesięciu — przywódcy i ministrowie "
                     "zwycięskich mocarstw."],
        ["dmowski", "Panowie, Polska była przez wieki wielkim państwem. Rozbiory odebrały jej wolność, ale nie "
                    "odebrały Polakom poczucia, że są narodem."],
        ["narrator", "Dmowski mówi godzinami, na zmianę po francusku i po angielsku. Pokazuje na mapach, gdzie "
                     "mieszkają Polacy."],
        ["clemenceau", "Monsieur Dmowski zna sprawę swojego kraju lepiej niż ktokolwiek z nas."],
        ["narrator", "Rada powołuje komisję do spraw polskich. Teraz trzeba przygotować memoriały o każdej ziemi."],
    ],
    "listopad": [
        ["narrator", "11 listopada 1918 r. Niemcy podpisują rozejm. Wielka wojna dobiega końca."],
        ["narrator", "W Warszawie mieszkańcy rozbrajają niemieckich żołnierzy. Na ulicach powiewają "
                     "biało-czerwone flagi."],
        ["narrator", "Rada Regencyjna przekazuje Józefowi Piłsudskiemu dowództwo nad wojskiem."],
        ["pilsudski", "Polska jest wolna. Teraz musimy ją obronić i wywalczyć jej granice."],
        ["narrator", "Po 123 latach niewoli Polska wraca na mapę. Dziś 11 listopada to Narodowe Święto "
                     "Niepodległości."],
    ],
    "traktat": [
        ["narrator", "28 czerwca 1919 r. — dokładnie 5 lat po zamachu w Sarajewie, od którego zaczęła się wojna."],
        ["narrator", "Sala Lustrzana w Wersalu. To tu w 1871 r. ogłoszono powstanie Cesarstwa Niemieckiego. "
                     "Dziś Niemcy podpisują traktat pokojowy."],
        ["clemenceau", "Zapraszam delegację Polski do podpisania traktatu."],
        ["paderewski", "Podpisuję w imieniu Rzeczypospolitej Polskiej."],
        ["dmowski", "I ja. Po 123 latach Polska znów jest na mapie Europy."],
        ["narrator", "Traktat potwierdził niepodległość Polski i przyznał jej m.in. Wielkopolskę i większość Pomorza "
                     "z dostępem do morza."],
    ],
}

# ------------------------------------------------------------------ mini-gra: przemówienie przed Radą Dziesięciu
PRZEMOWIENIE = [
    dict(pytajacy="Delegat francuski",
         pytanie="Delegaci mówią po francusku i po angielsku. W jakim języku pan przemówi?",
         odpowiedzi=[["Po francusku i po angielsku — na zmianę, żeby rozumieli wszyscy", 25],
                     ["Tylko po polsku — niech szukają tłumacza", 0],
                     ["Nie będę mówić, pokażę tylko mapę", 5]],
         reakcja="Dmowski znał świetnie oba języki — mógł mówić bezpośrednio do wszystkich delegatów."),
    dict(pytajacy="Delegat brytyjski", pytanie="Czy Polacy mają prawo do własnego państwa?",
         odpowiedzi=[["Polska istniała przez ponad 800 lat, aż do rozbiorów. Polacy przez cały czas zachowali "
                      "język, kulturę i wolę wolności.", 25],
                     ["Bo Polacy pięknie tańczą poloneza.", 0],
                     ["Bo tak chcę i już.", 0]],
         reakcja="Argument historyczny przekonuje — Polska nie była nowym wymysłem, tylko odradzającym się państwem."),
    dict(pytajacy="Delegat amerykański", pytanie="Gdzie powinna przebiegać granica Polski na zachodzie?",
         odpowiedzi=[["Tam, gdzie mieszka większość Polaków — mam mapy i dane ze spisów ludności.", 25],
                     ["Jak najdalej, nieważne, kto tam mieszka.", 0],
                     ["Niech zdecyduje rzut monetą.", 0]],
         reakcja="Dane i mapy to mocny argument — tak pracowali eksperci polskiej delegacji."),
    dict(pytajacy="Delegat włoski", pytanie="Po co Polsce dostęp do morza?",
         odpowiedzi=[["Wisła płynie do Bałtyku. Bez portu Polska nie mogłaby swobodnie handlować — obiecał to też "
                      "13. punkt prezydenta Wilsona.", 25],
                     ["Żeby polscy marynarze mieli gdzie pływać dla przyjemności.", 5],
                     ["Morze nie jest Polsce potrzebne.", 0]],
         reakcja="Odwołanie do 14 punktów Wilsona trafia do Amerykanów."),
    dict(pytajacy="Delegat japoński", pytanie="Czy Polacy pomogli aliantom w tej wojnie?",
         odpowiedzi=[["Tak — Armia Polska we Francji walczyła u boku aliantów, a ochotnicy przybyli nawet z Ameryki.",
                      25],
                     ["Nie, Polacy tylko czekali.", 0],
                     ["To nie ma znaczenia.", 5]],
         reakcja="Błękitna Armia generała Hallera była dowodem, że Polacy walczyli razem z aliantami."),
]

# ------------------------------------------------------------------ oś czasu 1914–1919 (Księga Wiedzy)
# [pozycja na osi (rok z ułamkiem), data, tytuł, opis, rodzaj: pl / sw, czy jest też na osi czasu klasy VII]
OS_CZASU = [
    [1914.49, "28 czerwca 1914", "Zamach w Sarajewie",
     "Zabójstwo austriackiego następcy tronu w Sarajewie stało się iskrą, od której wybuchła wielka wojna.", "sw", True],
    [1914.57, "28 lipca 1914", "Wybuch I wojny światowej",
     "Austro-Węgry wypowiadają wojnę Serbii. W ciągu kilku dni walczy już niemal cała Europa.", "sw", False],
    [1914.6, "6 sierpnia 1914", "Wymarsz Pierwszej Kompanii Kadrowej",
     "Strzelcy Józefa Piłsudskiego wyruszają z Krakowa. Powstają Legiony Polskie.", "pl", True],
    [1914.9, "25 listopada 1914", "Komitet Narodowy Polski",
     "W Warszawie powstaje Komitet Narodowy Polski, którym kieruje Roman Dmowski.", "pl", False],
    [1915.59, "5 sierpnia 1915", "Niemcy zajmują Warszawę",
     "Wojska rosyjskie wycofują się. Dmowski wyjeżdża na Zachód, by tam walczyć o sprawę polską.", "pl", False],
    [1916.15, "1916", "Bitwa pod Verdun",
     "Jedna z najdłuższych i najkrwawszych bitew wojny — symbol okrucieństwa walk w okopach.", "sw", True],
    [1916.85, "5 listopada 1916", "Akt 5 listopada",
     "Niemcy i Austro-Węgry zapowiadają utworzenie Królestwa Polskiego zależnego od nich.", "pl", True],
    [1917.2, "1917", "Rewolucje w Rosji",
     "Upada car, a potem władzę przejmują bolszewicy. Rosja wycofuje się z wojny.", "sw", True],
    [1917.27, "6 kwietnia 1917", "USA przystępują do wojny",
     "Stany Zjednoczone dołączają do aliantów. Prezydentem jest Woodrow Wilson.", "sw", True],
    [1917.43, "4 czerwca 1917", "Armia Polska we Francji",
     "Dekret prezydenta Francji pozwala utworzyć polskie wojsko — przyszłą Błękitną Armię.", "pl", False],
    [1917.62, "15 sierpnia 1917", "Komitet w Lozannie",
     "Dmowski odnawia w Lozannie Komitet Narodowy Polski, który wkrótce przenosi się do Paryża.", "pl", False],
    [1918.02, "8 stycznia 1918", "13. punkt Wilsona",
     "Prezydent USA zapowiada niepodległe państwo polskie z dostępem do morza.", "pl", True],
    [1918.86, "11 listopada 1918", "Odzyskanie niepodległości",
     "Koniec I wojny światowej. Józef Piłsudski przejmuje dowództwo nad wojskiem w Warszawie.", "pl", True],
    [1918.99, "27 grudnia 1918", "Powstanie wielkopolskie",
     "Wybucha zwycięskie powstanie, które przywraca Polsce większość Wielkopolski.", "pl", True],
    [1919.05, "18 stycznia 1919", "Konferencja pokojowa w Paryżu",
     "Zwycięzcy wojny zbierają się w Paryżu, by ustalić nowe granice Europy.", "sw", False],
    [1919.08, "29 stycznia 1919", "Przemówienie Dmowskiego",
     "Dmowski przedstawia polskie postulaty przed Radą Dziesięciu.", "pl", False],
    [1919.49, "28 czerwca 1919", "Traktat wersalski",
     "Podpisanie traktatu pokojowego z Niemcami. Za Polskę podpisują Paderewski i Dmowski.", "sw", True],
]
OS_CZASU_KLASA7 = "https://adscisel-alt.github.io/gry-historyczne/os-czasu-historia-7.html"

# ------------------------------------------------------------------ mapa Europy między kampaniami
# trasa: [skąd, dokąd, środek: "pociag" / "statek", podpis]
MAPY_PODROZY = {
    "start": dict(rok="1914", od="1914", do="1914", wyroznij=["German Empire", "Austro-Hungarian Empire",
                                                              "Russian Empire"],
                  miasta=["Warszawa", "Poznań", "Gdańsk", "Kraków", "Berlin", "Wiedeń", "Piotrogród"], trasa=[],
                  podpisy=["Rok 1914. Polski nie ma na mapie Europy — od 1795 r. jej ziemie należą do trzech "
                           "zaborców: Niemiec, Austro-Węgier i Rosji.",
                           "Warszawa leży w zaborze rosyjskim, Poznań i Gdańsk — w niemieckim, a Kraków — "
                           "w austriackim. Zaraz wybuchnie wielka wojna."]),
    "2": dict(rok="1915–1917", od="1914", do="1914", wyroznij=["German Empire", "Austro-Hungarian Empire",
                                                             "Russian Empire"],
              miasta=["Warszawa", "Piotrogród", "Sztokholm", "Londyn", "Paryż", "Lozanna"],
              trasa=[["Warszawa", "Piotrogród", "pociag", "Sierpień 1915: Niemcy zajmują Warszawę. Dmowski "
                                                          "wyjeżdża do Piotrogrodu."],
                     ["Piotrogród", "Sztokholm", "pociag", "Przez Skandynawię jedzie na Zachód…"],
                     ["Sztokholm", "Bergen", "pociag", "Przez Skandynawię jedzie na Zachód…"],
                     ["Bergen", "Londyn", "statek", "…i dociera do Londynu, gdzie pisze memoriały dla aliantów."],
                     ["Londyn", "Paryż", "pociag", "1917: przez Paryż jedzie do neutralnej Szwajcarii."],
                     ["Paryż", "Lozanna", "pociag", "W Lozannie odnawia Komitet Narodowy Polski."]],
              podpisy=[]),
    "3": dict(rok="1917", od="1914", do="1914", wyroznij=["France", "German Empire"],
              miasta=["Lozanna", "Paryż", "Londyn", "Warszawa"],
              trasa=[["Lozanna", "Paryż", "pociag", "Komitet przenosi się do Paryża. We Francji powstaje "
                                                    "Armia Polska — Błękitna Armia."]],
              podpisy=[]),
    "4": dict(rok="1918", od="1914", do="1920", wyroznij=["Poland"],
              miasta=["Paryż", "Warszawa", "Poznań", "Gdańsk", "Kraków"], trasa=[],
              podpisy=["Jesień 1918: zaborcy przegrywają wojnę. Upadają cesarstwa Niemiec, Austro-Węgier "
                       "i Rosji.",
                       "11 listopada 1918 r. Polska odzyskuje niepodległość! Wraca na mapę Europy po 123 latach.",
                       "Ale granice nie są jeszcze ustalone. Teraz rozstrzygnie o nich konferencja pokojowa "
                       "w Paryżu — i walki w latach 1918–1921."]),
    "koniec": dict(rok="1919–1921", od="1920", do="1920", wyroznij=["Poland"],
                   miasta=["Warszawa", "Poznań", "Gdańsk", "Kraków", "Paryż"], trasa=[],
                   podpisy=["Traktat wersalski (1919) przyznał Polsce Wielkopolskę i większość Pomorza z dostępem "
                            "do Bałtyku. Gdańsk został Wolnym Miastem.",
                            "O Górnym Śląsku oraz Warmii i Mazurach zdecydowały plebiscyty, a granicę wschodnią "
                            "ustalono dopiero w 1921 r. Mapa pokazuje stan około 1920 r."]),
}

# ------------------------------------------------------------------ karty postaci (tylko postacie historyczne z gry)
# fakty: [ikona, tekst]; odblokuj: ["start"] / ["flaga", nazwa] / ["kampania", numer]
def karta(imie, daty, rola, fakty, ciekawostka, odblokuj, kampania):
    tekst = "%s, %s. %s %s Ciekawostka: %s" % (imie, rola, " ".join(f[1] for f in fakty), "", ciekawostka)
    return dict(imie=imie, daty=daty, rola=rola, fakty=fakty, ciekawostka=ciekawostka, odblokuj=odblokuj,
                kampania=kampania, lektor=" ".join(tekst.split()))


KARTY_POSTACI = {
    "dmowski": karta("Roman Dmowski", "1864–1939", "polityk, pisarz i dyplomata", [
        ["kalendarz", "Urodził się 9 sierpnia 1864 r. na warszawskiej Pradze, w Kamionku."],
        ["ksiega", "Studiował nauki przyrodnicze na Uniwersytecie Warszawskim."],
        ["pioro", "Napisał książkę „Myśli nowoczesnego Polaka” (1903) i współtworzył obóz narodowy."],
        ["medal", "W 1919 r. stał na czele polskiej delegacji w Paryżu i podpisał traktat wersalski."]],
        "W 1923 r. był przez kilka tygodni ministrem spraw zagranicznych Polski.", ["start"], 1),
    "zamoyski": karta("Maurycy Zamoyski", "1871–1939", "ziemianin i dyplomata", [
        ["miejsce", "Był ordynatem zamojskim — właścicielem ogromnych dóbr, także w okolicach Zamościa."],
        ["sakiewka", "Wspierał finansowo Komitet Narodowy Polski i był jego wiceprezesem."],
        ["flaga", "W latach 1919–1924 był posłem Polski we Francji."],
        ["kalendarz", "W 1922 r. kandydował na prezydenta — przegrał z Gabrielem Narutowiczem."]],
        "Pochodził z rodu Zamoyskich, tak jak Jan Zamoyski — założyciel Zamościa z drugiej gry w tym repozytorium!",
        ["flaga", "rozm_zamoyski_1"], 1),
    "haller": karta("gen. Józef Haller", "1873–1960", "generał, dowódca Błękitnej Armii", [
        ["miejsce", "Urodził się w Jurczycach koło Krakowa."],
        ["statek", "W 1918 r. przedostał się z Rosji do Francji przez Murmańsk."],
        ["ochotnicy", "Dowodził Armią Polską we Francji, która w 1919 r. wróciła do kraju."],
        ["kotwica", "10 lutego 1920 r. w Pucku dokonał zaślubin Polski z morzem."]],
        "Nazywano go „błękitnym generałem” — od koloru mundurów jego żołnierzy.", ["flaga", "rozm_haller_3"], 3),
    "paderewski": karta("Ignacy Jan Paderewski", "1860–1941", "pianista, kompozytor i premier", [
        ["miejsce", "Urodził się w Kuryłówce na Podolu."],
        ["nuta", "Był jednym z najsłynniejszych pianistów świata; skomponował m.in. „Menuet G-dur”."],
        ["flaga", "W styczniu 1919 r. został premierem i ministrem spraw zagranicznych."],
        ["pioro", "Razem z Dmowskim podpisał 28 czerwca 1919 r. traktat wersalski."]],
        "W 1992 r. jego prochy sprowadzono z USA i złożono w archikatedrze warszawskiej.",
        ["flaga", "rozm_paderewski_4"], 4),
    "clemenceau": karta("Georges Clemenceau", "1841–1929", "premier Francji", [
        ["flaga", "Był premierem Francji w latach 1906–1909 i 1917–1920."],
        ["ksiega", "Z wykształcenia był lekarzem, pracował też jako dziennikarz."],
        ["gwiazda", "Ze względu na twardy charakter nazywano go „Tygrysem”."],
        ["medal", "Przewodniczył konferencji pokojowej w Paryżu."]],
        "W lutym 1919 r. został postrzelony w zamachu, ale szybko wrócił do obrad.",
        ["flaga", "rozm_clemenceau_4"], 4),
    "wilson": karta("Woodrow Wilson", "1856–1924", "prezydent Stanów Zjednoczonych", [
        ["flaga", "Był 28. prezydentem USA w latach 1913–1921."],
        ["ksiega", "Wcześniej był profesorem i rektorem Uniwersytetu Princeton."],
        ["dokument", "W 14 punktach (1918) zapowiedział niepodległą Polskę z dostępem do morza."],
        ["medal", "Otrzymał Pokojową Nagrodę Nobla za rok 1919."]],
        "W Poznaniu jest park jego imienia i pomnik prezydenta Wilsona.", ["flaga", "rozm_wilson_4"], 4),
    "pilsudski": karta("Józef Piłsudski", "1867–1935", "Naczelnik Państwa i marszałek", [
        ["miejsce", "Urodził się w Zułowie koło Wilna."],
        ["ochotnicy", "W 1914 r. utworzył Legiony Polskie."],
        ["flaga", "Od listopada 1918 r. był Naczelnikiem Państwa."],
        ["medal", "W 1920 r. dowodził w zwycięskiej bitwie warszawskiej."]],
        "Jego czapka-maciejówka stała się symbolem legionistów.", ["kampania", 4], 3),
}

# ------------------------------------------------------------------ dylematy (decyzje z konsekwencjami)
# opcja: [tekst, efekty {"fr","uk","usa" = zaufanie; zasoby; "pw"}, czy tak było w historii]
def D_(id_, kampania, dzien, data, tytul, opis, opcje, historia):
    return dict(id=id_, kampania=kampania, dzien=dzien, data=data, tytul=tytul, opis=opis, opcje=opcje,
                historia=historia)


DYLEMATY = [
    D_("strona_wojny", 1, 3, "Sierpień 1914", "Po której stronie?",
       "Wybuchła wojna. Rosja walczy z Niemcami i Austro-Węgrami. Po której stronie powinien stanąć Komitet?",
       [["Z Rosją i jej sojusznikami — Francją i Wielką Brytanią", {"fr": 8, "uk": 8, "poparcie": 10}, True],
        ["Z Austro-Węgrami przeciw Rosji, jak Legiony Piłsudskiego", {"fr": -8, "uk": -8, "prasa": 10}, False],
        ["Nie angażować się i czekać", {"fr": -3, "uk": -3, "usa": -3}, False]],
       "Dmowski uważał, że największym wrogiem Polski są Niemcy, i związał się z ententą. Piłsudski wybrał "
       "drugą drogę — Legiony u boku Austro-Węgier. Obie drogi miały swoich zwolenników."),
    D_("ewakuacja", 1, 9, "Lato 1915", "Niemcy zbliżają się do Warszawy",
       "Wojska rosyjskie się wycofują. Co zrobić z Komitetem Narodowym?",
       [["Wyjechać na Zachód i przekonywać aliantów", {"fr": 6, "uk": 6, "pw": 2}, True],
        ["Zostać w Warszawie pod okupacją niemiecką", {"fr": -5, "uk": -5, "fundusze": 20}, False],
        ["Rozwiązać Komitet", {"fr": -10, "uk": -10, "usa": -5}, False]],
       "Dmowski wyjechał przez Piotrogród na Zachód. W Londynie i Paryżu mógł swobodnie działać dla sprawy "
       "polskiej."),
    D_("akt_5_listopada", 2, 3, "5 listopada 1916", "Królestwo Polskie od Niemiec?",
       "Niemcy i Austro-Węgry ogłaszają utworzenie Królestwa Polskiego, zależnego od nich. Jak zareagować?",
       [["Wyjaśnić w prasie aliantów, że to nie jest prawdziwa niepodległość", {"fr": 6, "uk": 6, "prasa": 10},
         True],
        ["Poprzeć Królestwo — lepszy rydz niż nic", {"fr": -10, "uk": -10, "usa": -5}, False],
        ["Milczeć i przeczekać", {"fr": -3, "uk": -3}, False]],
       "Obóz Dmowskiego krytykował akt jako próbę zdobycia polskich żołnierzy przez Niemcy. Akt sprawił jednak, "
       "że sprawą polską zainteresowały się wszystkie mocarstwa."),
    D_("rewolucja", 2, 9, "1917", "Rewolucja w Rosji",
       "Car upadł, Rosja słabnie. Na kim teraz oprzeć sprawę polską?",
       [["Domagać się od Francji, Anglii i USA pełnej niepodległości Polski", {"fr": 6, "uk": 6, "usa": 8}, True],
        ["Nadal liczyć tylko na Rosję", {"fr": -5, "uk": -5, "usa": -5}, False],
        ["Poczekać, co zrobią inni", {"fr": -3, "usa": -3}, False]],
       "Po rewolucji Dmowski mógł otwarcie domagać się od Zachodu niepodległej Polski. W 1917 r. Komitet "
       "uznały Francja, Wielka Brytania, Włochy, a potem USA."),
    D_("transport", 3, 3, "1917–1918", "Ochotnicy z Ameryki",
       "Tysiące Polaków z USA chce walczyć we Francji, ale transport przez ocean kosztuje. Skąd wziąć pieniądze?",
       [["Poprosić Polonię amerykańską i Paderewskiego o zbiórkę", {"usa": 8, "fundusze": 40}, True],
        ["Poprosić Francję o pożyczkę", {"fr": 3, "fundusze": 40, "poparcie": -10}, False],
        ["Zrezygnować z ochotników z Ameryki", {"usa": -8, "ochotnicy": -10}, False]],
       "Polonia amerykańska zbierała pieniądze i werbowała ochotników. Paderewski był jednym z "
       "najważniejszych organizatorów tej pomocy."),
    D_("dowodca", 3, 9, "Październik 1918", "Kto ma dowodzić?",
       "Armia Polska we Francji rośnie. Kto powinien nią dowodzić?",
       [["Polski generał — Józef Haller", {"fr": 5, "uk": 3, "usa": 3, "ochotnicy": 10}, True],
        ["Francuski generał", {"fr": 5, "ochotnicy": -5}, False],
        ["Każdy pułk osobno, bez wspólnego dowództwa", {"fr": -6, "uk": -4, "usa": -4}, False]],
       "Jesienią 1918 r. dowództwo Armii Polskiej objął gen. Józef Haller. Polskie wojsko pod polskim dowództwem "
       "było ważnym argumentem dyplomatów."),
    D_("porozumienie", 4, 3, "Styczeń 1919", "Warszawa czy Paryż?",
       "W Warszawie rządzi Naczelnik Piłsudski, w Paryżu działa Komitet Narodowy. Kto ma reprezentować Polskę?",
       [["Porozumieć się: Paderewski premierem, Dmowski na czele delegacji w Paryżu",
         {"fr": 8, "uk": 8, "usa": 8, "poparcie": 10}, True],
        ["Nie uznawać rządu w Warszawie", {"fr": -10, "uk": -10, "usa": -10}, False],
        ["Zostawić konferencję i jechać do Warszawy", {"fr": -5, "uk": -5, "usa": -5}, False]],
       "Porozumienie Piłsudskiego z Komitetem sprawiło, że Polska mówiła w Paryżu jednym głosem. "
       "Premierem został Paderewski."),
    D_("gdansk", 4, 9, "Wiosna 1919", "Spór o Gdańsk",
       "Brytyjczycy nie chcą oddać Polsce Gdańska, w którym mieszka wielu Niemców. Co robisz?",
       [["Przyjąć kompromis: Wolne Miasto z prawami dla Polski i dostępem do morza", {"uk": 6, "usa": 4}, True],
        ["Żądać Gdańska za wszelką cenę", {"uk": -8, "fr": 3, "prasa": 5}, False],
        ["Zrezygnować z dostępu do morza", {"fr": -6, "uk": 2, "usa": -6}, False]],
       "Polska delegacja chciała Gdańska, ale musiała przyjąć kompromis: Wolne Miasto pod opieką Ligi Narodów. "
       "Polska zachowała dostęp do morza przez Pomorze."),
]
ZAUFANIE_NAZWY = {"fr": "Francja", "uk": "Wielka Brytania", "usa": "USA"}

# ------------------------------------------------------------------ gazeta „Kurier Wolności” (fikcyjna gazeta gry)
GAZETY = {
    "k1": dict(data="2 sierpnia 1914", tytul="WOJNA W EUROPIE!",
               podtytul="Niemcy wypowiedziały wojnę Rosji. Zaborcy Polski stają przeciwko sobie.",
               tekst="Polacy z trzech zaborów muszą służyć w trzech różnych armiach. Czy wojna zaborców otworzy "
                     "drogę do wolnej Polski? Politycy z Warszawy i Krakowa spierają się, po której stronie "
                     "stanąć.", obraz="ilustracja_dmowski"),
    "k2": dict(data="sierpień 1917", tytul="KOMITET NARODOWY W LOZANNIE",
               podtytul="Roman Dmowski na czele. Komitet przeniesie się do Paryża.",
               tekst="Po rewolucji w Rosji sprawa polska staje się ważna dla Francji i Wielkiej Brytanii. Komitet "
                     "chce mówić w imieniu wszystkich Polaków i zabiega o uznanie aliantów.",
               obraz="ilustracja_zamoyski"),
    "k3": dict(data="czerwiec 1917", tytul="POWSTAJE ARMIA POLSKA!",
               podtytul="Prezydent Francji podpisał dekret. Ochotnicy płyną z Ameryki.",
               tekst="Żołnierze dostaną błękitne francuskie mundury. W obozach szkoleniowych ćwiczą Polacy z Francji, "
                     "z Ameryki i z niewoli.", obraz="ilustracja_haller"),
    "k4": dict(data="styczeń 1919", tytul="KONFERENCJA POKOJOWA W PARYŻU",
               podtytul="Zwycięzcy wojny zdecydują o nowych granicach Europy.",
               tekst="Polskę reprezentują Roman Dmowski i premier Ignacy Jan Paderewski. Najważniejsze pytania: "
                     "gdzie przebiegnie granica z Niemcami i czy Polska dostanie dostęp do morza?",
               obraz="ilustracja_clemenceau"),
    "przemowienie": dict(data="30 stycznia 1919", tytul="POLAK PRZED RADĄ DZIESIĘCIU",
                         podtytul="Roman Dmowski przez kilka godzin przedstawiał sprawę polską.",
                         tekst="Delegat mówił na zmianę po francusku i po angielsku, posługując się mapami i danymi. "
                               "Rada powołała komisję do spraw polskich.", obraz="ilustracja_dmowski"),
    "traktat": dict(data="29 czerwca 1919", tytul="TRAKTAT PODPISANY W WERSALU!",
                    podtytul="Polska znów na mapie Europy. Za Polskę podpisali Paderewski i Dmowski.",
                    tekst="Traktat przyznaje Polsce Wielkopolskę i większość Pomorza z dostępem do morza. Gdańsk "
                          "będzie Wolnym Miastem, a o Górnym Śląsku i Warmii zdecydują plebiscyty.",
                    obraz="ilustracja_paderewski"),
}

# ------------------------------------------------------------------ mini-gra: granice Polski
GRANICE = dict(
    kategorie=[["polska", "Do Polski — traktat wersalski (1919)"],
               ["wolne_miasto", "Wolne Miasto pod opieką Ligi Narodów"],
               ["plebiscyt", "Plebiscyt — zdecydują mieszkańcy"]],
    regiony=[["wielkopolska", "Wielkopolska", "Poznań", "polska",
              "Po zwycięskim powstaniu wielkopolskim traktat przyznał Polsce niemal całą Wielkopolskę."],
             ["pomorze", "Pomorze Gdańskie", "Toruń", "polska",
              "Polska otrzymała większość Pomorza, a z nim dostęp do Bałtyku."],
             ["gdansk", "Gdańsk", "Gdańsk", "wolne_miasto",
              "Gdańsk został Wolnym Miastem pod opieką Ligi Narodów, z prawami dla Polski."],
             ["slask", "Górny Śląsk", "Katowice", "plebiscyt",
              "Plebiscyt odbył się w 1921 r. Po powstaniach śląskich Polska otrzymała część regionu (1922)."],
             ["warmia", "Warmia i Mazury", "Olsztyn", "plebiscyt",
              "W plebiscycie w 1920 r. większość głosujących wybrała Niemcy."]],
)

# ------------------------------------------------------------------ znajdźki (3 na każdej mapie)
ZNAJDZKI = {
    "1": [["pocztowka", 22, 9, "Pocztówka z placu Zamkowego",
           "Kolumna Zygmunta stoi na placu Zamkowym od 1644 r. — to najstarszy świecki pomnik Warszawy."],
          ["gazeta", 4, 15, "Gazeta z sierpnia 1914",
           "28 lipca 1914 r. Austro-Węgry wypowiedziały wojnę Serbii. Kilka dni później walczyła już cała Europa."],
          ["bilet", 33, 18, "Bilet tramwajowy",
           "Od 1908 r. po Warszawie jeździły tramwaje elektryczne; wcześniej ciągnęły je konie."]],
    "2": [["pocztowka", 2, 8, "Pocztówka znad Jeziora Genewskiego",
           "Lozanna leży nad Jeziorem Genewskim, w Szwajcarii, która w czasie wojny była neutralna."],
          ["bilet", 13, 16, "Bilet Londyn–Paryż",
           "W czasie wojny podróż z Londynu do Paryża wymagała przeprawy statkiem przez kanał La Manche."],
          ["list", 30, 15, "List do Komitetu",
           "Polacy z całego świata pisali do Komitetu Narodowego z prośbami o pomoc i z ofertami wsparcia."]],
    "3": [["plakat", 3, 12, "Plakat werbunkowy",
           "Plakaty zachęcały Polaków w Ameryce do wstępowania do Armii Polskiej we Francji."],
          ["helm", 29, 6, "Hełm wzoru Adriana",
           "Żołnierze armii francuskiej i Błękitnej Armii nosili stalowe hełmy wzoru Adriana."],
          ["list", 25, 20, "List z frontu",
           "Żołnierze pisali listy do rodzin; poczta polowa dostarczała je mimo walk."]],
    "4": [["zaproszenie", 7, 13, "Przepustka na konferencję",
           "W konferencji pokojowej w Paryżu uczestniczyły delegacje kilkudziesięciu państw."],
          ["bilet", 34, 13, "Bilet do Wersalu",
           "Pałac w Wersalu leży około 20 km od centrum Paryża."],
          ["pioro", 20, 6, "Kałamarz delegacji",
           "W Sali Lustrzanej, gdzie podpisano traktat, jest 357 luster."]],
}

# ------------------------------------------------------------------ odznaki (osiągnięcia)
OSIAGNIECIA = [
    ["kampania_1", "Komitet założony", "Ukończ kampanię I.", "medal"],
    ["mowca", "Mówca Rady", "Zdobądź 3 gwiazdki w przemówieniu przed Radą Dziesięciu.", "gwiazda"],
    ["kartograf", "Kartograf", "Ułóż mapę granic bez żadnego błędu.", "mapa"],
    ["zbieracz", "Zbieracz pamiątek", "Znajdź wszystkie 12 pamiątek ukrytych na mapach.", "sakiewka"],
    ["mol", "Mól książkowy", "Przeczytaj wszystkie karty Księgi Wiedzy.", "ksiega"],
    ["postacie", "Znawca postaci", "Poznaj wszystkie karty postaci.", "teczka"],
    ["dyplomata", "Ulubieniec aliantów", "Miej co najmniej 70 zaufania Francji, Wielkiej Brytanii i USA.", "flaga"],
    ["sladami", "Śladami Dmowskiego", "Podejmij wszystkie 8 decyzji tak jak w historii.", "pioro"],
    ["wlasna_droga", "Własna droga", "Podejmij co najmniej 3 decyzje inaczej niż w historii.", "kompas"],
    ["budowniczy", "Budowniczy", "Zbuduj łącznie 25 placówek.", "kalendarz"],
    ["zagadki", "Mistrz zagadek", "Rozwiąż wszystkie zagadki postaci.", "dokument"],
    ["niepodlegla", "Niepodległa!", "Ukończ grę.", "odznaka"],
]

POWITANIE = [
    ["dmowski", "Warszawa, 1914. Trzeba działać — Polacy potrzebują wspólnego głosu."],
    ["hanna", "Panie Romanie, jestem Hanna. Będę panu pomagać we wszystkich kampaniach!"],
    ["narrator", "Chodź klawiszami WASD lub strzałkami. Kamerę obracasz klawiszami Q i R albo prawym "
                 "przyciskiem myszy, a kółkiem przybliżasz."],
    ["narrator", "Podejdź do postaci z wykrzyknikiem i wciśnij E. Kompas (K) wskaże kierunek do celu. "
                 "Lektora włączasz i wyłączasz klawiszem G."],
]

POMOC = [
    "STEROWANIE",
    "WASD / strzałki — chodzenie · Q / R lub prawy przycisk myszy — obrót kamery",
    "Kółko myszy — przybliżanie i oddalanie kamery",
    "E lub Spacja — rozmowa z postacią (podejdź blisko)",
    "Lewy przycisk myszy — wybór i stawianie placówki · Prawy — anuluj",
    "K — kompas   I — ekwipunek   L — Księga Wiedzy (i oś czasu)   G — lektor   M — muzyka   F11 — pełny ekran",
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
        zagadki=ZAGADKI, rozmowy=ROZMOWY, przerywniki=PRZERYWNIKI, przemowienie=PRZEMOWIENIE,
        os_czasu=OS_CZASU, os_czasu_klasa7=OS_CZASU_KLASA7, mapy_podrozy=MAPY_PODROZY, powitanie=POWITANIE,
        karty_postaci=KARTY_POSTACI, dylematy=DYLEMATY, zaufanie_nazwy=ZAUFANIE_NAZWY, gazety=GAZETY,
        granice=GRANICE, znajdzki=ZNAJDZKI, osiagniecia=OSIAGNIECIA, luzne=LUZNE, pomoc=POMOC, start_ekwipunek=["kompas", "datki", "paczka"],
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
        zajete = {(xx, yy) for typ, x, y, _ in r["dzialki"] for yy in range(y, y + BUDYNKI[typ]["h"])
                  for xx in range(x, x + BUDYNKI[typ]["w"])}
        for z in ZNAJDZKI[str(k)]:
            assert mapa[z[2]][z[1]] in ".PB=#" and (z[1], z[2]) not in zajete, (k, z[3], mapa[z[2]][z[1]])
    tu = os.path.dirname(os.path.abspath(__file__))
    cel = os.path.join(tu, "..", "godot", "dane", "dane.json")
    os.makedirs(os.path.dirname(cel), exist_ok=True)
    with open(cel, "w", encoding="utf-8") as f:
        json.dump(wynik, f, ensure_ascii=False, indent=1)
    print("Zapisano", os.path.normpath(cel))


if __name__ == "__main__":
    main()
