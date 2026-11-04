"""Postacie gry: 12 historycznych (z biogramami) oraz fikcyjne.

Każda postać ma opis sylwetki-wycinanki (klucz ``wyglad``), z którego moduł
``grafika`` proceduralnie rysuje papierową sylwetkę w sepii.
"""

HISTORYCZNE = {
    "pilsudski": {
        "imie": "Józef Piłsudski",
        "lata": "1867–1935",
        "rola": "Komendant, od 11 XI 1918 Naczelny Wódz, od 22 XI Tymczasowy Naczelnik Państwa",
        "biogram": (
            "Urodził się w Zułowie na Wileńszczyźnie. Działacz PPS, zesłaniec syberyjski, "
            "twórca Związku Strzeleckiego i Legionów Polskich (1914). Gdy w 1917 r. legioniści "
            "odmówili przysięgi na wierność Niemcom (kryzys przysięgowy), został uwięziony "
            "w Magdeburgu. Zwolniony 8 XI 1918, przyjechał do Warszawy 10 XI. Rada Regencyjna "
            "przekazała mu 11 XI dowództwo wojska, a 14 XI całą władzę. Stawiał na własną armię "
            "i czyn zbrojny."
        ),
        "wklad": "zbudował armię i przejął władzę w Warszawie bez wojny domowej",
        "wyglad": {"plaszcz": 70, "czapka": "maciejowka", "zarost": "sumiaste", "wzrost": 1.0, "szabla": True},
    },
    "dmowski": {
        "imie": "Roman Dmowski",
        "lata": "1864–1939",
        "rola": "Przewodniczący Komitetu Narodowego Polskiego w Paryżu",
        "biogram": (
            "Przywódca Narodowej Demokracji, autor „Myśli nowoczesnego Polaka” (1903). "
            "Uważał, że największym zagrożeniem dla Polski są Niemcy, dlatego postawił na "
            "współpracę z państwami Ententy. Komitet Narodowy Polski, któremu przewodniczył "
            "od 1917 r., Francja, Wielka Brytania, Włochy i USA uznały za przedstawicielstwo "
            "Polaków. W 1919 r. razem z Paderewskim podpisał traktat wersalski."
        ),
        "wklad": "zdobył dla sprawy polskiej uznanie Ententy i przygotował argumenty na konferencję pokojową",
        "wyglad": {"plaszcz": 45, "czapka": "melonik", "zarost": "wasik", "binokle": True, "wzrost": 0.96, "teczka": True},
    },
    "paderewski": {
        "imie": "Ignacy Jan Paderewski",
        "lata": "1860–1941",
        "rola": "Pianista światowej sławy, przedstawiciel KNP w Stanach Zjednoczonych",
        "biogram": (
            "Jeden z najsłynniejszych pianistów świata. W czasie wojny jeździł po Ameryce, "
            "grał koncerty i przemawiał za niepodległą Polską. Miał wpływ na prezydenta "
            "Wilsona, którego 13. punkt (8 I 1918) zapowiadał niepodległą Polskę z dostępem "
            "do morza. Jego przyjazd do Poznania 26 XII 1918 poprzedził wybuch powstania "
            "wielkopolskiego. W 1919 r. premier i minister spraw zagranicznych."
        ),
        "wklad": "zjednał dla Polski Amerykę i prezydenta Wilsona",
        "wyglad": {"plaszcz": 60, "czapka": None, "fryzura": "grzywa", "zarost": "broda_mala", "wzrost": 1.02},
    },
    "daszynski": {
        "imie": "Ignacy Daszyński",
        "lata": "1866–1936",
        "rola": "Premier Tymczasowego Rządu Ludowego Republiki Polskiej (Lublin)",
        "biogram": (
            "Przywódca socjalistów w Galicji, poseł do parlamentu w Wiedniu, znakomity mówca. "
            "W nocy z 6 na 7 XI 1918 r. stanął na czele rządu w Lublinie, który ogłosił "
            "Polskę republiką ludową i zapowiedział m.in. 8-godzinny dzień pracy, reformę "
            "rolną i prawa wyborcze dla kobiet. Po przyjeździe Piłsudskiego rząd lubelski "
            "podporządkował mu się. Później m.in. marszałek Sejmu (1928–1930)."
        ),
        "wklad": "ogłosił program reform społecznych: 8 godzin pracy, prawa wyborcze kobiet, reforma rolna",
        "wyglad": {"plaszcz": 55, "czapka": "kapelusz", "zarost": "broda", "wzrost": 1.04},
    },
    "korfanty": {
        "imie": "Wojciech Korfanty",
        "lata": "1873–1939",
        "rola": "Poseł do Reichstagu, członek Komisariatu Naczelnej Rady Ludowej w Poznaniu",
        "biogram": (
            "Ślązak z Sadzawki (dziś Siemianowice Śląskie), syn górnika. Jako poseł do "
            "parlamentu niemieckiego 25 X 1918 r. zażądał w Reichstagu przyłączenia do Polski "
            "ziem zaboru pruskiego z polską ludnością. W listopadzie 1918 r. współtworzył "
            "Naczelną Radę Ludową, która przygotowywała Wielkopolskę do połączenia z Polską. "
            "W 1921 r. dyktator III powstania śląskiego."
        ),
        "wklad": "upomniał się o Wielkopolskę, Pomorze i Śląsk w samym parlamencie niemieckim",
        "wyglad": {"plaszcz": 40, "czapka": "melonik", "zarost": "sumiaste", "wzrost": 1.0, "teczka": True},
    },
    "witos": {
        "imie": "Wincenty Witos",
        "lata": "1874–1945",
        "rola": "Przewodniczący Polskiej Komisji Likwidacyjnej w Krakowie",
        "biogram": (
            "Chłop z Wierzchosławic koło Tarnowa, samouk, wójt swojej gminy i przywódca "
            "PSL „Piast”. 28 X 1918 r. stanął na czele Polskiej Komisji Likwidacyjnej, "
            "która przejęła władzę w Galicji od Austriaków. Trzykrotnie był premierem, "
            "m.in. w czasie wojny z bolszewikami w 1920 r. Przekonywał, że bez chłopów "
            "nie będzie niepodległej Polski."
        ),
        "wklad": "przejął Galicję od Austriaków i przekonał wieś, że to także jej państwo",
        "wyglad": {"plaszcz": 95, "czapka": "chlopski", "zarost": "sumiaste", "wzrost": 0.98, "sukmana": True},
    },
    "kakowski": {
        "imie": "abp Aleksander Kakowski",
        "lata": "1862–1938",
        "rola": "Arcybiskup warszawski, członek Rady Regencyjnej",
        "biogram": (
            "Od 1913 r. arcybiskup warszawski. W 1917 r. wszedł do Rady Regencyjnej — "
            "trzyosobowego organu powołanego pod okupacją niemiecką i austriacką. "
            "7 X 1918 r. Rada ogłosiła orędzie o niepodległej Polsce, a w listopadzie "
            "przekazała władzę Piłsudskiemu. W 1919 r. został kardynałem."
        ),
        "wklad": "z Radą Regencyjną przygotował urzędy i spokojnie przekazał władzę",
        "wyglad": {"plaszcz": 30, "czapka": "biretta", "sutanna": True, "krzyz": True, "wzrost": 0.97},
    },
    "lubomirski": {
        "imie": "książę Zdzisław Lubomirski",
        "lata": "1865–1943",
        "rola": "Członek Rady Regencyjnej, wcześniej prezydent Warszawy",
        "biogram": (
            "Ziemianin i społecznik, w czasie wojny prezes Komitetu Obywatelskiego, "
            "a w latach 1916–1917 prezydent Warszawy. Jako członek Rady Regencyjnej "
            "10 XI 1918 r. witał Piłsudskiego na Dworcu Wiedeńskim. Opowiadał się "
            "za szybkim przekazaniem władzy Komendantowi."
        ),
        "wklad": "jako regent przywitał Piłsudskiego i poparł przekazanie mu władzy",
        "wyglad": {"plaszcz": 50, "czapka": "cylinder", "zarost": "broda_mala", "wzrost": 1.05, "laska": True},
    },
    "ostrowski": {
        "imie": "Józef Ostrowski",
        "lata": "1850–1923",
        "rola": "Członek Rady Regencyjnej",
        "biogram": (
            "Ziemianin, polityk konserwatywny, przed wojną poseł do rosyjskiej Dumy "
            "i jeden z przywódców Koła Polskiego. W Radzie Regencyjnej odpowiadał za "
            "sprawy rządu i administracji. Najstarszy z regentów, znany z ostrożności."
        ),
        "wklad": "pilnował, by urzędy i sądy działały od pierwszego dnia państwa",
        "wyglad": {"plaszcz": 65, "czapka": None, "fryzura": "lysy", "zarost": "broda", "wzrost": 0.95, "laska": True},
    },
    "rydz": {
        "imie": "Edward Rydz-Śmigły",
        "lata": "1886–1941",
        "rola": "Komendant Główny POW, minister wojny w rządzie lubelskim",
        "biogram": (
            "Malarz z wykształcenia (studiował w Akademii Sztuk Pięknych w Krakowie), "
            "legionista. W 1918 r. kierował Polską Organizacją Wojskową, a w rządzie "
            "Daszyńskiego objął resort wojny. W 1936 r. został marszałkiem Polski."
        ),
        "wklad": "przygotował oddziały POW, które przejmowały koszary i posterunki",
        "wyglad": {"plaszcz": 75, "czapka": "wojskowa", "zarost": None, "wzrost": 1.03, "szabla": True},
    },
    "koc": {
        "imie": "Adam Koc",
        "lata": "1891–1969",
        "rola": "Komendant POW w Warszawie",
        "biogram": (
            "Legionista i oficer Polskiej Organizacji Wojskowej. 10 XI 1918 r. razem "
            "z księciem Lubomirskim powitał Piłsudskiego na dworcu. W listopadowych dniach "
            "kierował akcją rozbrajania Niemców w Warszawie. Później m.in. polityk "
            "i minister skarbu."
        ),
        "wklad": "poprowadził rozbrajanie Niemców w Warszawie",
        "wyglad": {"plaszcz": 85, "czapka": "wojskowa", "zarost": "wasik", "wzrost": 1.0},
    },
    "moraczewska": {
        "imie": "Zofia Moraczewska",
        "lata": "1873–1958",
        "rola": "Działaczka na rzecz praw kobiet, posłanka Sejmu Ustawodawczego",
        "biogram": (
            "Współtwórczyni Ligi Kobiet, organizacji, która w czasie wojny wspierała "
            "legionistów i walczyła o prawa kobiet. Żona premiera Jędrzeja Moraczewskiego. "
            "W styczniu 1919 r. jako jedna z ośmiu pierwszych kobiet została wybrana "
            "do Sejmu Ustawodawczego."
        ),
        "wklad": "walczyła o to, by kobiety współdecydowały o państwie",
        "wyglad": {"plaszcz": 80, "czapka": "damski", "suknia": True, "wzrost": 0.92},
    },
}

FIKCYJNE = {
    "janek": {
        "imie": "Janek",
        "rola": "14-letni harcerz-łącznik z Warszawy (postać fikcyjna)",
        "wyglad": {"plaszcz": 110, "czapka": "harcerski", "wzrost": 0.78, "chusta": True},
    },
    "damian": {
        "imie": "Damian Ściseł",
        "rola": "archiwista w fioletowym kapturze, narrator i weryfikator mitów",
        "wyglad": {"plaszcz": 0, "czapka": "kaptur", "wzrost": 1.0, "fiolet": True},
    },
    "druh_staszek": {
        "imie": "druh Staszek",
        "rola": "drużynowy Janka (postać fikcyjna)",
        "wyglad": {"plaszcz": 120, "czapka": "harcerski", "wzrost": 0.9, "chusta": True},
    },
    "wozny": {
        "imie": "pan Feliks, woźny",
        "rola": "strażnik drzwi Rady Regencyjnej (postać fikcyjna)",
        "wyglad": {"plaszcz": 35, "czapka": "wojskowa", "zarost": "sumiaste", "wzrost": 0.98},
    },
    "zecer": {
        "imie": "pan Lejb Gutman, zecer",
        "rola": "zecer w lubelskiej drukarni (postać fikcyjna)",
        "wyglad": {"plaszcz": 100, "czapka": "kaszkiet", "zarost": "broda", "wzrost": 0.96, "fartuch": True},
    },
    "otto": {
        "imie": "Otto, żołnierz niemiecki",
        "rola": "członek Rady Żołnierskiej, chce wrócić do domu (postać fikcyjna)",
        "wyglad": {"plaszcz": 90, "czapka": "pikielhauba", "zarost": "wasik", "wzrost": 1.0},
    },
    "zawadzka": {
        "imie": "red. Helena Zawadzka",
        "rola": "reporterka „Kuriera” zbierająca relacje (postać fikcyjna)",
        "wyglad": {"plaszcz": 140, "czapka": "damski", "suknia": True, "wzrost": 0.93, "teczka": True},
    },
    "laroche": {
        "imie": "monsieur Laroche",
        "rola": "dyplomata francuski (postać fikcyjna)",
        "wyglad": {"plaszcz": 40, "czapka": None, "zarost": "broda_mala", "wzrost": 0.97},
    },
    "whitby": {
        "imie": "Mr. Whitby",
        "rola": "dyplomata brytyjski (postać fikcyjna)",
        "wyglad": {"plaszcz": 60, "czapka": "melonik", "zarost": "sumiaste", "wzrost": 1.06, "laska": True},
    },
    "carter": {
        "imie": "Mr. Carter",
        "rola": "dyplomata amerykański (postać fikcyjna)",
        "wyglad": {"plaszcz": 105, "czapka": "kapelusz", "zarost": None, "wzrost": 1.04},
    },
    "dorozkarz": {
        "imie": "dorożkarz Wincenty",
        "rola": "świadek (postać fikcyjna)",
        "wyglad": {"plaszcz": 50, "czapka": "kaszkiet", "zarost": "sumiaste", "wzrost": 0.97},
    },
    "przekupka": {
        "imie": "przekupka Bronisława",
        "rola": "świadek (postać fikcyjna)",
        "wyglad": {"plaszcz": 120, "czapka": "chusta_glowa", "suknia": True, "wzrost": 0.88},
    },
    "student": {
        "imie": "student Leon",
        "rola": "świadek, członek straży akademickiej (postać fikcyjna)",
        "wyglad": {"plaszcz": 70, "czapka": "studencka", "wzrost": 0.98},
    },
    "konduktorka": {
        "imie": "pani Jadwiga",
        "rola": "konduktorka tramwaju w Poznaniu (postać fikcyjna)",
        "wyglad": {"plaszcz": 60, "czapka": "kaszkiet", "suknia": True, "wzrost": 0.9},
    },
}


def wszystkie():
    d = {}
    d.update(HISTORYCZNE)
    d.update(FIKCYJNE)
    return d


def imie(pid):
    return wszystkie()[pid]["imie"]
