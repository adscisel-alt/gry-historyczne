"""Treść edukacyjna: fakty z datami i źródłami, 10 mitów, prawa wyborcze kobiet, mapa zaborów."""

# --- FAKTY DO DZIENNIKA JANKA -------------------------------------------------
# Każdy fakt: data, treść, źródło (dokument epoki lub opracowanie).
FAKTY = {
    "pkl_krakow": {
        "data": "28 X 1918",
        "tekst": "W Krakowie powstała Polska Komisja Likwidacyjna z Wincentym Witosem na czele. "
                 "Miała „zlikwidować” władzę austriacką w Galicji i przejąć urzędy.",
        "zrodlo": "Protokoły posiedzeń PKL (Kraków 1918); W. Witos, „Moje wspomnienia”.",
    },
    "krakow_rozbrojenie": {
        "data": "31 X 1918",
        "tekst": "Polscy oficerowie i żołnierze rozbroili w Krakowie austriacką komendę garnizonu. "
                 "Żołnierze zrywali z czapek austriackie „bączki” i przypinali orzełki.",
        "zrodlo": "Relacje uczestników akcji ppor. Antoniego Stawarza; prasa krakowska z 1 XI 1918.",
    },
    "lwow_walki": {
        "data": "1 XI 1918",
        "tekst": "We Lwowie wybuchły walki polsko-ukraińskie. Miasta broniła m.in. młodzież — "
                 "nazwana później „Orlętami Lwowskimi”.",
        "zrodlo": "Prasa lwowska z listopada 1918; opracowania dziejów obrony Lwowa.",
    },
    "rr_oredzie": {
        "data": "7 X 1918",
        "tekst": "Rada Regencyjna wydała orędzie „Do Narodu Polskiego”, ogłaszając wolę "
                 "utworzenia niepodległego państwa obejmującego wszystkie ziemie polskie.",
        "zrodlo": "Orędzie Rady Regencyjnej z 7 X 1918, „Monitor Polski” 1918.",
    },
    "rr_sklad": {
        "data": "1917–1918",
        "tekst": "Radę Regencyjną tworzyli: abp Aleksander Kakowski, książę Zdzisław Lubomirski "
                 "i Józef Ostrowski. Powołano ją pod okupacją niemiecką i austriacką.",
        "zrodlo": "Patent o ustanowieniu Rady Regencyjnej, 12 IX 1917.",
    },
    "swiezynski": {
        "data": "23 X – 3 XI 1918",
        "tekst": "Rada Regencyjna powołała rząd Józefa Świeżyńskiego, a 3 XI go odwołała, "
                 "bo działał bez jej zgody. Władza w Warszawie była wtedy bardzo niepewna.",
        "zrodlo": "„Monitor Polski”, listopad 1918.",
    },
    "trl_lublin": {
        "data": "7 XI 1918",
        "tekst": "W Lublinie powstał Tymczasowy Rząd Ludowy Republiki Polskiej z Ignacym "
                 "Daszyńskim jako premierem i Edwardem Rydzem-Śmigłym jako ministrem wojny.",
        "zrodlo": "Manifest Tymczasowego Rządu Ludowego Republiki Polskiej, Lublin 7 XI 1918.",
    },
    "manifest_tresc": {
        "data": "7 XI 1918",
        "tekst": "Manifest lubelski zapowiadał: republikę, równe prawa obywateli bez różnicy płci, "
                 "8-godzinny dzień pracy, reformę rolną i zwołanie Sejmu Ustawodawczego.",
        "zrodlo": "Manifest TRL RP, druk ulotny, Lublin 1918.",
    },
    "magdeburg": {
        "data": "8 XI 1918",
        "tekst": "Niemcy zwolnili Józefa Piłsudskiego i Kazimierza Sosnkowskiego z twierdzy "
                 "w Magdeburgu, gdzie byli więzieni od lipca 1917 r.",
        "zrodlo": "K. Sosnkowski, wspomnienia; dokumenty Ministerstwa Wojny Rzeszy.",
    },
    "powrot_10xi": {
        "data": "10 XI 1918",
        "tekst": "Piłsudski przyjechał pociągiem z Berlina na Dworzec Wiedeński w Warszawie "
                 "rano 10 XI. Witali go m.in. książę Zdzisław Lubomirski i Adam Koc.",
        "zrodlo": "„Kurier Warszawski”, wydanie z 10–11 XI 1918.",
    },
    "rozbrajanie": {
        "data": "10–12 XI 1918",
        "tekst": "Członkowie POW, harcerze, studenci i byli legioniści rozbrajali Niemców "
                 "w Warszawie. Wielu niemieckich żołnierzy, zrzeszonych w Radzie Żołnierskiej, "
                 "chciało już tylko wrócić do domu.",
        "zrodlo": "Wspomnienia uczestników; prasa warszawska z 11–12 XI 1918.",
    },
    "rr_11xi": {
        "data": "11 XI 1918",
        "tekst": "Rada Regencyjna przekazała Piłsudskiemu naczelne dowództwo nad wojskiem. "
                 "Tego samego dnia w Compiègne podpisano rozejm kończący walki I wojny światowej.",
        "zrodlo": "Orędzie Rady Regencyjnej z 11 XI 1918; rozejm w Compiègne, 11 XI 1918.",
    },
    "rr_14xi": {
        "data": "14 XI 1918",
        "tekst": "Rada Regencyjna rozwiązała się i przekazała Piłsudskiemu pełnię władzy cywilnej.",
        "zrodlo": "Orędzie Rady Regencyjnej z 14 XI 1918, „Monitor Polski”.",
    },
    "telegram_16xi": {
        "data": "16 XI 1918",
        "tekst": "Piłsudski wysłał telegram do państw świata zawiadamiający o istnieniu "
                 "niepodległego Państwa Polskiego.",
        "zrodlo": "Depesza notyfikacyjna J. Piłsudskiego z 16 XI 1918.",
    },
    "knp_uznanie": {
        "data": "1917",
        "tekst": "Komitet Narodowy Polski w Paryżu (od sierpnia 1917) uznały Francja, Wielka "
                 "Brytania, Włochy i Stany Zjednoczone. KNP stworzył też Armię Polską we Francji.",
        "zrodlo": "Noty rządów Ententy do KNP, IX–XII 1917.",
    },
    "wilson_13": {
        "data": "8 I 1918",
        "tekst": "Prezydent USA Woodrow Wilson w 13. punkcie swojego orędzia zapowiedział "
                 "niepodległą Polskę z ludnością bezsprzecznie polską i wolnym dostępem do morza.",
        "zrodlo": "Orędzie W. Wilsona do Kongresu USA („14 punktów”), 8 I 1918.",
    },
    "haller": {
        "data": "1917–1919",
        "tekst": "Armia Polska we Francji, zwana „Błękitną Armią” od koloru mundurów, "
                 "walczyła po stronie Ententy. Od października 1918 dowodził nią gen. Józef Haller.",
        "zrodlo": "Dokumenty KNP; opracowania dziejów Armii Polskiej we Francji.",
    },
    "kompromis_1919": {
        "data": "I 1919",
        "tekst": "Na początku 1919 r. obozy z Warszawy i Paryża porozumiały się: Paderewski "
                 "został premierem, a Dmowski i Paderewski reprezentowali Polskę na konferencji pokojowej.",
        "zrodlo": "Akta konferencji pokojowej w Paryżu 1919.",
    },
    "korfanty_reichstag": {
        "data": "25 X 1918",
        "tekst": "Wojciech Korfanty w Reichstagu w Berlinie zażądał przyłączenia do Polski ziem "
                 "zaboru pruskiego zamieszkanych przez Polaków, także Górnego Śląska i Gdańska.",
        "zrodlo": "Stenogram posiedzenia Reichstagu z 25 X 1918.",
    },
    "nrl": {
        "data": "XI 1918",
        "tekst": "W Poznaniu ujawniła się Naczelna Rada Ludowa. Jej Komisariat tworzyli: "
                 "ks. Stanisław Adamski, Wojciech Korfanty i Adam Poszwiński.",
        "zrodlo": "Odezwy NRL, „Kurier Poznański”, listopad 1918.",
    },
    "wielkopolska": {
        "data": "27 XII 1918",
        "tekst": "Wielkopolska wciąż należała do Niemiec. Dopiero powstanie wielkopolskie "
                 "(27 XII 1918 – 16 II 1919) i traktat wersalski przyłączyły ją do Polski.",
        "zrodlo": "Traktat wersalski, 28 VI 1919; opracowania dziejów powstania wielkopolskiego.",
    },
    "naczelnik": {
        "data": "22 XI 1918",
        "tekst": "Dekret o najwyższej władzy reprezentacyjnej uczynił Piłsudskiego "
                 "Tymczasowym Naczelnikiem Państwa do czasu zebrania się Sejmu.",
        "zrodlo": "Dekret z 22 XI 1918, Dziennik Praw Państwa Polskiego nr 17, poz. 41.",
    },
    "moraczewski": {
        "data": "18 XI 1918",
        "tekst": "Powstał rząd Jędrzeja Moraczewskiego. 23 XI wprowadził 8-godzinny dzień pracy.",
        "zrodlo": "Dekret z 23 XI 1918 o 8-godzinnym dniu pracy, Dz.P.P.P. 1918.",
    },
    "dekret_wyborczy": {
        "data": "28 XI 1918",
        "tekst": "Dekret o ordynacji wyborczej: „Wyborcą do Sejmu jest każdy obywatel Państwa "
                 "bez różnicy płci, który do dnia ogłoszenia wyborów ukończył 21 lat”.",
        "zrodlo": "Dekret z 28 XI 1918, Dziennik Praw Państwa Polskiego nr 18, poz. 46, art. 1.",
    },
    "wybory_1919": {
        "data": "26 I 1919",
        "tekst": "W wyborach do Sejmu Ustawodawczego po raz pierwszy głosowały kobiety. "
                 "Do Sejmu weszło 8 posłanek.",
        "zrodlo": "Sprawozdania Sejmu Ustawodawczego 1919.",
    },
    "swieto_1937": {
        "data": "23 IV 1937",
        "tekst": "11 listopada stał się oficjalnym świętem państwowym dopiero na mocy ustawy z 1937 r. "
                 "Po wojnie zniesiony, przywrócony w 1989 r.",
        "zrodlo": "Ustawa o Święcie Niepodległości, Dz.U. 1937 nr 33, poz. 255; ustawa z 15 II 1989.",
    },
    "hymn_1927": {
        "data": "1927",
        "tekst": "„Mazurek Dąbrowskiego” został oficjalnie hymnem państwowym dopiero w 1927 r.",
        "zrodlo": "Okólnik Ministerstwa Wyznań Religijnych i Oświecenia Publicznego, 1927.",
    },
    "granice": {
        "data": "1918–1922",
        "tekst": "Granice II Rzeczypospolitej kształtowały się przez kilka lat: powstania, "
                 "wojna z bolszewikami, plebiscyty i traktaty.",
        "zrodlo": "Traktat wersalski (1919), traktat ryski (1921), podział Górnego Śląska (1922).",
    },
    "zabory": {
        "data": "1772–1795",
        "tekst": "W trzech rozbiorach Rosja, Prusy i Austria podzieliły ziemie Rzeczypospolitej. "
                 "Przez 123 lata Polacy żyli w trzech różnych państwach, z innymi prawami i walutą.",
        "zrodlo": "Traktaty rozbiorowe 1772, 1793, 1795.",
    },
}

# --- 10 MITÓW --------------------------------------------------------------------
# Każdy mit to quiz Damiana: twierdzenie, trzy odpowiedzi „co naprawdę”, poprawna, wyjaśnienie.
MITY = {
    "m_jeden_dzien": {
        "mit": "Polska odzyskała niepodległość jednego dnia — 11 listopada 1918 r.",
        "opcje": [
            "Tak, 11 listopada o 11:00 ogłoszono to z balkonu Zamku.",
            "Nie — to był proces trwający tygodnie, a granice ustalały się do 1922 r.",
            "Nie — stało się to dopiero w 1920 r. po Bitwie Warszawskiej.",
        ],
        "dobra": 1,
        "wyjasnienie": "Od orędzia Rady Regencyjnej (7 X), przez Kraków (31 X), Lublin (7 XI), "
                       "Warszawę (10–14 XI) aż po dekrety z końca listopada — państwo rodziło się "
                       "krok po kroku. 11 XI to symboliczna data.",
        "fakt": "granice",
    },
    "m_swieto": {
        "mit": "11 listopada świętowano od samego 1918 roku.",
        "opcje": [
            "Tak, od 1918 r. był to dzień wolny.",
            "Nie — oficjalne święto ustanowiono ustawą w 1937 r.",
            "Nie — święto wymyślono dopiero w 1989 r.",
        ],
        "dobra": 1,
        "wyjasnienie": "Rocznice obchodzono wcześniej, ale ustawowe Święto Niepodległości "
                       "wprowadzono w 1937 r. Po II wojnie je zniesiono i przywrócono w 1989 r.",
        "fakt": "swieto_1937",
    },
    "m_sam_pilsudski": {
        "mit": "Niepodległość wywalczył jeden człowiek — Józef Piłsudski.",
        "opcje": [
            "Tak, inni politycy tylko mu przeszkadzali.",
            "Nie — złożyła się na nią praca wielu ludzi z różnych obozów i z trzech zaborów.",
            "Nie — niepodległość podarowała Polsce Francja.",
        ],
        "dobra": 1,
        "wyjasnienie": "Piłsudski był kluczowy w Warszawie, ale bez dyplomacji Dmowskiego "
                       "i Paderewskiego, programu Daszyńskiego, pracy Korfantego czy Witosa "
                       "i decyzji Rady Regencyjnej byłoby znacznie trudniej.",
        "fakt": None,
    },
    "m_przyjazd_11": {
        "mit": "Piłsudski przyjechał do Warszawy 11 listopada.",
        "opcje": [
            "Przyjechał 10 listopada rano pociągiem z Berlina.",
            "Przyjechał 11 listopada samochodem z Krakowa.",
            "Przyleciał samolotem 9 listopada.",
        ],
        "dobra": 0,
        "wyjasnienie": "Pociąg z Berlina dotarł na Dworzec Wiedeński rano 10 listopada. "
                       "11 listopada Rada Regencyjna przekazała mu dowództwo wojska.",
        "fakt": "powrot_10xi",
    },
    "m_rr_zdrajcy": {
        "mit": "Rada Regencyjna była tylko marionetką okupantów i nic nie zrobiła dla niepodległości.",
        "opcje": [
            "Prawda — nigdy nie mówiła o niepodległości.",
            "To uproszczenie — powstała z woli okupantów, ale ogłosiła niepodległość 7 X i pokojowo oddała władzę.",
            "Rada Regencyjna nie istniała, to wymysł powieściopisarzy.",
        ],
        "dobra": 1,
        "wyjasnienie": "Krytycy wskazywali, że regentów powołali Niemcy i Austriacy. Obrońcy — "
                       "że Rada zbudowała urzędy, sądy i szkolnictwo, a potem bez konfliktu "
                       "przekazała władzę. Obie oceny opierają się na faktach.",
        "fakt": "rr_oredzie",
    },
    "m_kobiety": {
        "mit": "Kobiety w Polsce dostały prawo głosu dopiero po II wojnie światowej.",
        "opcje": [
            "Prawda — pierwszy raz głosowały w 1946 r.",
            "Nie — dekret z 28 XI 1918 dał im pełne prawa wyborcze, wcześniej niż np. we Francji.",
            "Nie — głosowały już w XVIII wieku na sejmikach.",
        ],
        "dobra": 1,
        "wyjasnienie": "Polki głosowały w wyborach 26 I 1919. Francuzki — dopiero w 1945 r., "
                       "Amerykanki w całym kraju od 1920 r., Brytyjki na równi z mężczyznami od 1928 r.",
        "fakt": "dekret_wyborczy",
    },
    "m_rozbrojenie_krwawe": {
        "mit": "Niemców wypędzono z Warszawy w wielkiej, krwawej bitwie.",
        "opcje": [
            "Tak, walki trwały miesiąc i zniszczyły miasto.",
            "Nie — było kilka starć, ale większość Niemców oddała broń i wyjechała na podstawie porozumienia.",
            "Nie — Niemcy wyjechali jeszcze w 1917 r.",
        ],
        "dobra": 1,
        "wyjasnienie": "Zdarzały się strzelaniny i ofiary, ale Piłsudski porozumiał się "
                       "z niemiecką Radą Żołnierską. Garnizon został ewakuowany w ciągu kilku dni.",
        "fakt": "rozbrajanie",
    },
    "m_dmowski_przeciw": {
        "mit": "Dmowski i Piłsudski chcieli zupełnie innych rzeczy — jeden był za niepodległością, drugi przeciw.",
        "opcje": [
            "Obaj chcieli niepodległości, ale wybrali inne drogi i innych sojuszników.",
            "Dmowski chciał, by Polska została częścią Rosji na zawsze.",
            "Piłsudski chciał, by Polska była częścią Niemiec.",
        ],
        "dobra": 0,
        "wyjasnienie": "Dmowski uważał za głównego wroga Niemcy i stawiał na Ententę. Piłsudski "
                       "najpierw walczył u boku Austrii przeciw Rosji, a potem zerwał z państwami "
                       "centralnymi. Cel był wspólny, strategie — różne.",
        "fakt": "knp_uznanie",
    },
    "m_wielkopolska": {
        "mit": "W listopadzie 1918 r. Poznań i Wielkopolska od razu stały się częścią Polski.",
        "opcje": [
            "Tak, Niemcy oddali je 11 listopada.",
            "Nie — należały do Niemiec do powstania wielkopolskiego i traktatu wersalskiego.",
            "Nie — Wielkopolska nigdy nie wróciła do Polski.",
        ],
        "dobra": 1,
        "wyjasnienie": "Rozejm z 11 XI nie zmienił granic Niemiec. Powstanie wybuchło 27 XII 1918, "
                       "a ostatecznie granicę potwierdził traktat wersalski z 28 VI 1919.",
        "fakt": "wielkopolska",
    },
    "m_hymn": {
        "mit": "„Mazurek Dąbrowskiego” był oficjalnym hymnem od pierwszego dnia niepodległości.",
        "opcje": [
            "Tak, ustawa z 11 XI 1918 to ustaliła.",
            "Nie — był popularny, ale oficjalnym hymnem został w 1927 r.",
            "Nie — hymnem była „Rota” aż do 1989 r.",
        ],
        "dobra": 1,
        "wyjasnienie": "W 1918 r. śpiewano „Mazurka”, „Rotę”, „Boże coś Polskę” i „Pierwszą "
                       "Brygadę”. Spór o hymn rozstrzygnięto w 1927 r.",
        "fakt": "hymn_1927",
    },
}

# --- PRAWA WYBORCZE KOBIET -------------------------------------------------------
PRAWA_KOBIET = {
    "tytul": "Prawa wyborcze kobiet w 1918 r.",
    "akapity": [
        "28 listopada 1918 r. Józef Piłsudski i premier Jędrzej Moraczewski podpisali dekret "
        "o ordynacji wyborczej. Art. 1: „Wyborcą do Sejmu jest każdy obywatel Państwa bez "
        "różnicy płci, który do dnia ogłoszenia wyborów ukończył 21 lat”.",
        "Kobiety mogły nie tylko głosować (czynne prawo wyborcze), ale też kandydować "
        "(bierne prawo wyborcze).",
        "Wybory do Sejmu Ustawodawczego odbyły się 26 stycznia 1919 r. Wybrano 8 posłanek, "
        "m.in. Gabrielę Balicką, Irenę Kosmowską, Zofię Moraczewską i Franciszkę Wilczkowiakową.",
        "Do tej chwili prowadziły długie starania m.in. Ligi Kobiet oraz zjazdów kobiet polskich. "
        "Postulat praw wyborczych dla kobiet znalazł się też w manifeście lubelskim z 7 XI 1918.",
    ],
    "porownanie": [
        ("Nowa Zelandia", 1893),
        ("Finlandia", 1906),
        ("Polska", 1918),
        ("USA (cały kraj)", 1920),
        ("Wielka Brytania (na równi z mężczyznami)", 1928),
        ("Francja", 1944),
        ("Szwajcaria", 1971),
    ],
    "zrodlo": "Dekret z 28 XI 1918 o ordynacji wyborczej do Sejmu Ustawodawczego, Dz.P.P.P. nr 18, poz. 46.",
}

# --- MAPA TRZECH ZABORÓW (uproszczona, długość/szerokość geograficzna) -----------
ZABORY = {
    "rosyjski": {
        "nazwa": "zabór rosyjski",
        "ton": 175,
        "punkty": [(22.8, 54.4), (26.5, 55.2), (27.0, 52.0), (24.2, 50.7), (23.0, 50.4), (21.7, 50.6),
                   (20.4, 50.2), (19.2, 50.3), (18.3, 51.3), (17.9, 51.6), (18.2, 52.4), (18.8, 52.9),
                   (19.3, 53.0), (20.0, 53.2), (21.0, 53.2), (22.8, 53.9)],
    },
    "pruski": {
        "nazwa": "zabór pruski",
        "ton": 120,
        "punkty": [(14.3, 53.9), (16.0, 54.5), (18.5, 54.8), (20.0, 54.9), (22.8, 54.4), (22.8, 53.9),
                   (21.0, 53.2), (20.0, 53.2), (19.3, 53.0), (18.8, 52.9), (18.2, 52.4), (17.9, 51.6),
                   (18.3, 51.3), (19.2, 50.3), (18.9, 50.0), (18.3, 50.0), (17.5, 50.3), (16.5, 50.2),
                   (15.0, 50.9), (14.6, 51.5), (14.6, 52.6)],
    },
    "austriacki": {
        "nazwa": "zabór austriacki",
        "ton": 210,
        "punkty": [(19.2, 50.3), (20.4, 50.2), (21.7, 50.6), (23.0, 50.4), (24.2, 50.7), (26.2, 49.6),
                   (25.9, 48.3), (24.5, 48.6), (23.0, 49.0), (22.0, 49.2), (20.5, 49.2), (19.5, 49.4),
                   (18.8, 49.5), (18.3, 49.9), (18.9, 50.0)],
    },
}

MIASTA = {
    "Warszawa": ((21.01, 52.23), "rosyjski"),
    "Lublin": ((22.57, 51.25), "rosyjski"),
    "Wilno": ((25.28, 54.69), "rosyjski"),
    "Poznań": ((16.93, 52.41), "pruski"),
    "Gdańsk": ((18.65, 54.35), "pruski"),
    "Bydgoszcz": ((18.00, 53.12), "pruski"),
    "Kraków": ((19.94, 50.06), "austriacki"),
    "Lwów": ((24.03, 49.84), "austriacki"),
    "Przemyśl": ((22.77, 49.78), "austriacki"),
}


def rzut(lon, lat, ox=0, oy=0, sx=44.0, sy=66.0):
    """Prosta projekcja geograficzna na płaszczyznę mapy."""
    return (ox + (lon - 13.8) * sx, oy + (55.6 - lat) * sy)


def punkt_w_wielokacie(x, y, pts):
    wewn = False
    n = len(pts)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            wewn = not wewn
        j = i
    return wewn
