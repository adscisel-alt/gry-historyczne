# -*- coding: utf-8 -*-
"""Treść gry „Kroniki Damiana Ścisła II: Rzeczpospolita” (1454–1795):
epoki, budynki, karty, technologie, pytania, postacie, zdarzenia, rozdziały."""

GAME = {
    "title": "Kroniki Damiana Ścisła II",
    "subtitle": "Rzeczpospolita • 1454–1795",
    "tagline": "Od wojny trzynastoletniej po insurekcję kościuszkowską – złoty wiek, potop i rozbiory.",
    "campaign": "Kampania: od Malborka do Racławic",
    "years": ("1454", "1795"),
    "exe": "KronikiDamianaScisla2",
    "save_dir": "KronikiDamianaScisla2",
    "storage_prefix": "kds2_",
    "window": "Kroniki Damiana Ścisła II – Rzeczpospolita 1454–1795",
    "intro_bubble": "Witaj ponownie, czytelniku! Tym razem przed nami trzy wieki Rzeczypospolitej – od złotego wieku po rozbiory.",
}

EPOCHS = [
    {"id": 0, "name": "Złoty wiek", "years": "1454–1572", "color": (160, 120, 40)},
    {"id": 1, "name": "Rzeczpospolita Obojga Narodów", "years": "1569–1648", "color": (150, 40, 50)},
    {"id": 2, "name": "Wiek wojen", "years": "1648–1699", "color": (90, 100, 140)},
    {"id": 3, "name": "Oświecenie i rozbiory", "years": "1764–1795", "color": (70, 120, 110)},
]

RES_NAMES = {"food": "Żywność", "wood": "Drewno", "stone": "Kamień", "silver": "Srebro"}
RES_ORDER = ["food", "wood", "stone", "silver"]

# ---------------------------------------------------------------- BUDYNKI
# Identyfikatory jak w części I; wygląd 3D zmienia się z epoką (renesans → bastiony → barok → klasycyzm).
BUILDINGS = {
    "pole": {"name": "Folwark", "cost": {"wood": 4}, "terrain": ["grass", "field"],
             "prod": {"food": 2}, "desc": "Dwór i pola uprawiane przez chłopów pańszczyźnianych. Zboże na chleb i na eksport."},
    "drwal": {"name": "Tartak", "cost": {"food": 3}, "terrain": ["forest"],
              "prod": {"wood": 2}, "desc": "Stawiaj w lesie. Drewno na statki, budowle i szańce."},
    "kamieniolom": {"name": "Kamieniołom", "cost": {"wood": 5, "food": 2}, "terrain": ["hills"],
                    "prod": {"stone": 2}, "desc": "Stawiaj na wzgórzach. Kamień na bastiony, kościoły i pałace."},
    "targ": {"name": "Kamienice kupieckie", "cost": {"wood": 6, "stone": 2}, "terrain": ["grass", "field", "road"],
             "prod": {"silver": 2}, "desc": "Kupcy, cechy i ratusz. Handel zbożem i suknem napełnia skarbiec."},
    "koszary": {"name": "Koszary", "cost": {"wood": 6, "food": 4}, "terrain": ["grass", "field", "road"],
                "prod": {}, "desc": "Pozwala werbować oddziały (1 werbunek na turę za każde koszary)."},
    "palisada": {"name": "Szańce z działami", "cost": {"wood": 8}, "terrain": ["grass", "field", "road", "hills"],
                 "prod": {}, "defense": 3, "req": "armaty",
                 "desc": "Ziemne wały z działami: +3 do morale w obronie i ochrona przed zagonami."},
    "kosciol": {"name": "Kolegium i drukarnia", "cost": {"wood": 6, "stone": 6}, "terrain": ["grass", "field", "road", "hills"],
                "prod": {"silver": 1}, "req": "druk",
                "desc": "Uczeni i księgi: w zagadkach usuwają jedną błędną odpowiedź."},
    "mlyn": {"name": "Młyn i browar", "cost": {"wood": 8, "stone": 2}, "terrain": ["grass", "field", "marsh"],
             "prod": {"food": 4}, "req": "folwark", "near_water": True,
             "desc": "Musi stać przy wodzie. Mąka, piwo i dochód dla dworu."},
    "zupa": {"name": "Żupa i huta", "cost": {"wood": 8, "stone": 4}, "terrain": ["hills"],
             "prod": {"silver": 4}, "req": "splaw", "desc": "Sól, żelazo i miedź spod ziemi. Na wzgórzach."},
    "zamek": {"name": "Twierdza bastionowa", "cost": {"stone": 16, "wood": 6, "silver": 6},
              "terrain": ["grass", "field", "hills"], "prod": {}, "defense": 6, "req": "bastiony",
              "radius": 4, "desc": "Nowoczesna twierdza z bastionami jak w Zamościu: +6 do morale w obronie."},
}

# premie technologii (silnik czyta je stąd, a nie z nazw na sztywno)
TECH_FX = {
    "prod": {"folwark": {"pole": {"food": 1}}, "kosy": {"pole": {"food": 1}},
             "splaw": {"targ": {"silver": 1}}, "gazety": {"targ": {"silver": 1}},
             "manufaktury": {"targ": {"silver": 2}, "zupa": {"silver": 2}},
             "ken": {"kosciol": {"silver": 2}}},
    "cheap": "astronomia",          # technologie tańsze o 25%
    "battle_hint": ["astronomia", "ken"],
    "morale": {"kartografia": 3, "konstytucja": 3},
    "halve_bad": "elekcja",
    "hand": "szkola_rycerska",
    "wagon_tactic": None,
}

# ---------------------------------------------------------------- KARTY BITEWNE
CARD_TYPES = {
    "piechota": {"name": "Piechota", "beats": "jazda", "color": (150, 60, 50)},
    "jazda": {"name": "Jazda", "beats": "lucznicy", "color": (60, 90, 150)},
    "lucznicy": {"name": "Strzelcy", "beats": "piechota", "color": (70, 120, 60)},
    "spec": {"name": "Artyleria", "beats": None, "color": (130, 100, 40)},
}

CARDS = {
    "woje": {"name": "Piechota łanowa", "type": "piechota", "power": 3, "unit": "pike", "faction": "pl",
             "cost": {"food": 3, "wood": 1}, "desc": "Chłopi z dóbr królewskich z drzewcami i tarczami."},
    "lucznicy": {"name": "Strzelcy z rusznicami", "type": "lucznicy", "power": 3, "unit": "musket", "faction": "pl",
                 "cost": {"food": 2, "wood": 3}, "desc": "Rusznica huczy głośniej niż łuk, ale ładuje się długo."},
    "konni": {"name": "Jazda kozacka", "type": "jazda", "power": 4, "unit": "horse", "faction": "pl",
              "cost": {"food": 4, "silver": 3}, "desc": "Lekka, szybka jazda z łukami i szablami."},
    "wybraniecka": {"name": "Piechota wybraniecka", "type": "piechota", "power": 6, "unit": "pike", "faction": "pl",
                    "cost": {"food": 4, "silver": 4}, "req": "wybraniecka", "desc": "Chłopi z dóbr królewskich – po jednym z 20 łanów."},
    "husaria": {"name": "Husaria", "type": "jazda", "power": 8, "unit": "hussar", "faction": "pl",
                "cost": {"food": 5, "silver": 8}, "req": "husaria", "desc": "Skrzydła, kopia i szarża, której nikt nie zapomni."},
    "muszkieterowie": {"name": "Muszkieterowie", "type": "lucznicy", "power": 6, "unit": "musket", "faction": "pl",
                       "cost": {"wood": 4, "silver": 4}, "req": "muszkiet", "desc": "Ciężki muszkiet oparty na forkiecie."},
    "dragoni": {"name": "Dragoni", "type": "lucznicy", "power": 7, "unit": "horse", "faction": "pl",
                "cost": {"food": 4, "silver": 5}, "req": "dragonia", "desc": "Piechota na koniach: dojeżdżają i strzelają."},
    "armata": {"name": "Armaty", "type": "spec", "power": 9, "unit": "cannon", "faction": "pl",
               "cost": {"stone": 6, "silver": 8}, "req": "armaty", "desc": "Spiżowe działa z ludwisarni."},
    "rakiety": {"name": "Rakiety Siemienowicza", "type": "spec", "power": 7, "unit": "cannon", "faction": "pl", "shield": 2,
                "cost": {"wood": 4, "silver": 6}, "req": "rakiety", "desc": "Świst, dym i popłoch w szeregach wroga."},
    "kosynierzy": {"name": "Kosynierzy", "type": "piechota", "power": 7, "unit": "scythe", "faction": "pl",
                   "cost": {"food": 4, "wood": 2}, "req": "kosy", "desc": "Chłopi z kosami na sztorc – postrach armat."},
    "litwini": {"name": "Chorągiew litewska", "type": "jazda", "power": 6, "unit": "horse_lt", "faction": "lt",
                "cost": {"food": 4, "silver": 4}, "req": "unia_lubelska", "desc": "Jazda Wielkiego Księstwa Litewskiego."},
    # sojusznicy w bitwach finałowych
    "zaciezni": {"name": "Zaciężni czescy", "type": "piechota", "power": 6, "unit": "pike", "faction": "cz", "cost": None,
                 "desc": "Najemnicy walczący za królewski żołd."},
    "mieszczanie": {"name": "Mieszczanie z muszkietami", "type": "lucznicy", "power": 5, "unit": "musket", "faction": "pl",
                    "cost": None, "desc": "Obywatele bronią swojego miasta."},
    "cesarscy": {"name": "Wojska cesarskie", "type": "piechota", "power": 6, "unit": "musket", "faction": "au", "cost": None,
                 "desc": "Sprzymierzeńcy z Austrii i Niemiec."},
    "chlopi": {"name": "Kosynierzy krakowscy", "type": "piechota", "power": 6, "unit": "scythe", "faction": "pl", "cost": None,
               "desc": "Chłopi spod Krakowa, którzy przyszli z kosami."},
    # wrogowie
    "e_knechci": {"name": "Knechci zakonni", "type": "piechota", "power": 6, "unit": "pike", "faction": "tz"},
    "e_rycerze_z": {"name": "Rycerze zakonni", "type": "jazda", "power": 7, "unit": "knight_t", "faction": "tz"},
    "e_kusznicy_z": {"name": "Kusznicy zakonni", "type": "lucznicy", "power": 5, "unit": "xbow", "faction": "tz"},
    "e_zaciezni_z": {"name": "Zaciężni Zakonu", "type": "piechota", "power": 6, "unit": "pike", "faction": "en"},
    "e_strzelcy_ru": {"name": "Strzelcy moskiewscy", "type": "lucznicy", "power": 6, "unit": "musket", "faction": "ru"},
    "e_jazda_ru": {"name": "Jazda bojarska", "type": "jazda", "power": 6, "unit": "horse", "faction": "ru"},
    "e_piechota_ru": {"name": "Piechota moskiewska", "type": "piechota", "power": 5, "unit": "pike", "faction": "ru"},
    "e_muszkieterowie_sv": {"name": "Muszkieterowie szwedzcy", "type": "lucznicy", "power": 7, "unit": "musket", "faction": "sv"},
    "e_rajtarzy_sv": {"name": "Rajtarzy szwedzcy", "type": "jazda", "power": 7, "unit": "horse", "faction": "sv"},
    "e_pikinierzy_sv": {"name": "Pikinierzy szwedzcy", "type": "piechota", "power": 6, "unit": "pike", "faction": "sv"},
    "e_armaty_sv": {"name": "Armaty szwedzkie", "type": "spec", "power": 8, "unit": "cannon", "faction": "sv"},
    "e_janczarzy": {"name": "Janczarzy", "type": "lucznicy", "power": 7, "unit": "musket", "faction": "tr"},
    "e_spahisi": {"name": "Spahisi", "type": "jazda", "power": 7, "unit": "horse", "faction": "tr"},
    "e_tatarzy": {"name": "Czambuł tatarski", "type": "lucznicy", "power": 6, "unit": "horse_mg", "faction": "mg"},
    "e_armaty_tr": {"name": "Działa tureckie", "type": "spec", "power": 8, "unit": "cannon", "faction": "tr"},
    "e_grenadierzy": {"name": "Grenadierzy rosyjscy", "type": "piechota", "power": 7, "unit": "musket", "faction": "rs"},
    "e_kozacy_rs": {"name": "Kozacy dońscy", "type": "jazda", "power": 6, "unit": "horse", "faction": "rs"},
    "e_strzelcy_rs": {"name": "Jegrzy rosyjscy", "type": "lucznicy", "power": 6, "unit": "musket", "faction": "rs"},
    "e_artyleria_rs": {"name": "Artyleria rosyjska", "type": "spec", "power": 8, "unit": "cannon", "faction": "rs"},
    "e_konfederaci": {"name": "Zbrojni targowiczanie", "type": "jazda", "power": 5, "unit": "horse", "faction": "en"},
}

# ---------------------------------------------------------------- TECHNOLOGIE (20)
TECHS = {
    # --- Złoty wiek
    "druk": {"name": "Druk", "epoch": 0, "req": [], "cost": {"silver": 6, "food": 4},
             "effect": "Odblokowuje Kolegium i drukarnię (podpowiedzi w zagadkach).",
             "q": "W którym mieście ok. 1473 r. powstała pierwsza drukarnia na ziemiach polskich?",
             "a": ["W Krakowie", "W Gdańsku", "W Warszawie", "W Wilnie"], "ok": 0,
             "fact": "Pierwszym drukarzem w Krakowie był Kasper Straube. Później drukarze wydawali książki po polsku, "
                     "a Mikołaj Rej pisał z dumą, że „Polacy nie gęsi, iż swój język mają”."},
    "folwark": {"name": "Folwark", "epoch": 0, "req": [], "cost": {"wood": 6},
                "effect": "Folwarki dają +1 żywności. Odblokowuje Młyn i browar.",
                "q": "Czym był folwark?",
                "a": ["Gospodarstwem szlachcica produkującym zboże na sprzedaż", "Twierdzą nad granicą",
                      "Szkołą przy kościele", "Statkiem handlowym"], "ok": 0,
                "fact": "Folwarki opierały się na pańszczyźnie – darmowej pracy chłopów. Szlachta bogaciła się na eksporcie "
                        "zboża, ale chłopi tracili wolność. To ciemna strona złotego wieku."},
    "splaw": {"name": "Spław wiślany", "epoch": 0, "req": [], "cost": {"wood": 8, "food": 2},
              "effect": "Kamienice kupieckie +1 srebra. Odblokowuje Żupę i hutę.",
              "q": "Do jakiego portu spławiano Wisłą polskie zboże?",
              "a": ["Do Gdańska", "Do Wenecji", "Do Lizbony", "Do Kijowa"], "ok": 0,
              "fact": "Flisacy płynęli Wisłą na szkutach i tratwach nawet kilka tygodni. W Gdańsku zboże kupowali "
                      "Holendrzy i wieźli je dalej po całej Europie."},
    "armaty": {"name": "Ludwisarnia i armaty", "epoch": 0, "req": [], "cost": {"stone": 4, "silver": 6},
               "effect": "Odblokowuje Szańce z działami i kartę: Armaty (siła 9).",
               "q": "Który ludwisarz odlał w 1520 r. dzwon Zygmunt na Wawelu?",
               "a": ["Hans Behem", "Wit Stwosz", "Mikołaj Kopernik", "Bartolomeo Berrecci"], "ok": 0,
               "fact": "Ludwisarze odlewali z brązu i dzwony, i armaty. Dzwon Zygmunt waży niemal 10 ton i bije tylko "
                       "w najważniejsze święta."},
    "astronomia": {"name": "Astronomia Kopernika", "epoch": 0, "req": ["druk"], "cost": {"silver": 8, "food": 2},
                   "effect": "Technologie tańsze o 25% i podpowiedź w pytaniach bitewnych.",
                   "q": "Kto napisał dzieło „O obrotach sfer niebieskich” (1543)?",
                   "a": ["Mikołaj Kopernik", "Galileusz", "Jan Kochanowski", "Mikołaj Rej"], "ok": 0,
                   "fact": "Kopernik był też ekonomistą: zauważył, że gorszy pieniądz wypiera z obiegu lepszy. "
                           "Pisał o tym w traktacie o monecie."},
    # --- Rzeczpospolita Obojga Narodów
    "unia_lubelska": {"name": "Unia lubelska", "epoch": 1, "req": [], "cost": {"silver": 8, "food": 4},
                      "effect": "Odblokowuje kartę: Chorągiew litewska (siła 6).",
                      "q": "W którym roku unia lubelska utworzyła Rzeczpospolitą Obojga Narodów?",
                      "a": ["1569", "1385", "1505", "1791"], "ok": 0,
                      "fact": "Od 1569 r. Korona i Litwa miały wspólnego króla, sejm i monetę, ale osobne wojsko, skarb i urzędy."},
    "elekcja": {"name": "Wolna elekcja", "epoch": 1, "req": ["druk"], "cost": {"silver": 6, "wood": 4},
                "effect": "Złe zdarzenia losowe zabierają o połowę mniej.",
                "q": "Jak nazywano wybór króla przez całą szlachtę?",
                "a": ["Wolna elekcja", "Dziedziczenie tronu", "Koronacja papieska", "Losowanie"], "ok": 0,
                "fact": "Pierwszy król elekcyjny, Henryk Walezy, po kilku miesiącach potajemnie wyjechał do Francji, "
                        "by objąć tron po bracie."},
    "wybraniecka": {"name": "Piechota wybraniecka", "epoch": 1, "req": ["armaty"], "cost": {"silver": 6, "food": 6},
                    "effect": "Odblokowuje kartę: Piechota wybraniecka (siła 6).",
                    "q": "Który król utworzył piechotę wybraniecką (1578)?",
                    "a": ["Stefan Batory", "Zygmunt August", "Jan III Sobieski", "Kazimierz Jagiellończyk"], "ok": 0,
                    "fact": "Z każdych 20 łanów w dobrach królewskich wybierano jednego chłopa na żołnierza. Za służbę był "
                            "zwolniony z czynszu i pańszczyzny."},
    "husaria": {"name": "Husaria", "epoch": 1, "req": [], "cost": {"silver": 8, "food": 6},
                "effect": "Odblokowuje kartę: Husaria (siła 8).",
                "q": "Czym była husaria?",
                "a": ["Ciężką jazdą z długimi kopiami", "Piechotą z kosami", "Flotą wojenną", "Strażą miejską"], "ok": 0,
                "fact": "Kopie husarskie miały ponad 5 metrów i były wydrążone w środku, by ważyły mniej. "
                        "Pod Kłuszynem husaria pokonała kilkakrotnie liczniejszego wroga."},
    "bastiony": {"name": "Fortyfikacje bastionowe", "epoch": 1, "req": ["armaty"], "cost": {"stone": 10, "wood": 4},
                 "effect": "Odblokowuje Twierdzę bastionową (+6 morale w obronie).",
                 "q": "Które miasto Bernardo Morando zaprojektował dla Jana Zamoyskiego jako „miasto idealne”?",
                 "a": ["Zamość", "Gdańsk", "Lublin", "Toruń"], "ok": 0,
                 "fact": "Zamość założono w 1580 r. Jego bastionowe mury wytrzymały oblężenie Kozaków w 1648 r. "
                         "i Szwedów w 1656 r. Dziś Stare Miasto jest na liście UNESCO."},
    # --- Wiek wojen
    "muszkiet": {"name": "Muszkiet", "epoch": 2, "req": ["armaty"], "cost": {"wood": 8, "silver": 6},
                 "effect": "Odblokowuje kartę: Muszkieterowie (siła 6).",
                 "q": "Jak nazywano żołnierza z ciężką strzelbą opieraną na podpórce – forkiecie?",
                 "a": ["Muszkieter", "Husarz", "Kosynier", "Pikinier"], "ok": 0,
                 "fact": "Muszkiet strzelał dalej niż łuk, ale ładowanie trwało nawet minutę. "
                         "Dlatego muszkieterów osłaniali pikinierzy."},
    "dragonia": {"name": "Dragonia", "epoch": 2, "req": ["husaria"], "cost": {"silver": 8, "food": 4},
                 "effect": "Odblokowuje kartę: Dragoni (siła 7).",
                 "q": "Kim byli dragoni?",
                 "a": ["Piechotą przemieszczającą się konno", "Strażą królewskiej kuchni", "Marynarzami", "Rycerzami zakonnymi"], "ok": 0,
                 "fact": "Dragoni dojeżdżali na pole bitwy konno, a walczyli zwykle pieszo, z muszkietem. "
                         "Nazwa pochodzi podobno od smoka (łac. draco) na ich chorągwiach."},
    "rakiety": {"name": "Rakiety Siemienowicza", "epoch": 2, "req": ["muszkiet"], "cost": {"wood": 6, "silver": 8},
                "effect": "Odblokowuje kartę: Rakiety (siła 7, osłona 2).",
                "q": "Kto w dziele „Artis Magnae Artilleriae” (1650) opisał rakiety wielostopniowe?",
                "a": ["Kazimierz Siemienowicz", "Mikołaj Kopernik", "Jan Heweliusz", "Stefan Czarniecki"], "ok": 0,
                "fact": "Księgę Siemienowicza przetłumaczono na kilka języków. Opisane w niej rakiety wielostopniowe to "
                        "pomysł, który wykorzystuje się dziś w lotach kosmicznych."},
    "gazety": {"name": "Poczta i gazety", "epoch": 2, "req": ["druk"], "cost": {"silver": 6, "wood": 4},
               "effect": "Kamienice kupieckie +1 srebra (szybsze wieści = lepszy handel).",
               "q": "Jak nazywała się pierwsza polska gazeta (1661)?",
               "a": ["Merkuriusz Polski", "Monitor", "Kurier Warszawski", "Gazeta Krakowska"], "ok": 0,
               "fact": "Pocztę królewską założył Zygmunt August w 1558 r. – kursowała między Krakowem a Wenecją."},
    "kartografia": {"name": "Kartografia", "epoch": 2, "req": ["astronomia"], "cost": {"silver": 6, "food": 4},
                    "effect": "Znajomość terenu: +3 morale we wszystkich bitwach.",
                    "q": "Kto wydał w 1613 r. słynną mapę Wielkiego Księstwa Litewskiego?",
                    "a": ["Mikołaj Krzysztof Radziwiłł „Sierotka”", "Jan Zamoyski", "Stefan Batory", "Jan Heweliusz"], "ok": 0,
                    "fact": "Mapa Radziwiłłowska była tak dokładna, że kopiowano ją przez ponad sto lat."},
    # --- Oświecenie
    "szkola_rycerska": {"name": "Szkoła Rycerska", "epoch": 3, "req": ["dragonia"], "cost": {"silver": 10},
                        "effect": "+1 karta na ręce w bitwie.",
                        "q": "Kto założył Szkołę Rycerską w Warszawie w 1765 r.?",
                        "a": ["Stanisław August Poniatowski", "August II Mocny", "Jan III Sobieski", "Tadeusz Kościuszko"], "ok": 0,
                        "fact": "Jej absolwentem był Tadeusz Kościuszko. Szkoła uczyła nie tylko wojskowości, ale też "
                                "historii, języków i matematyki."},
    "ken": {"name": "Komisja Edukacji Narodowej", "epoch": 3, "req": ["gazety"], "cost": {"silver": 8, "food": 4},
            "effect": "Kolegia dają +2 srebra i podpowiedź w pytaniach bitewnych.",
            "q": "Jak nazywał się pierwszy w Europie państwowy urząd oświaty (1773)?",
            "a": ["Komisja Edukacji Narodowej", "Akademia Krakowska", "Szkoła Rycerska", "Collegium Nobilium"], "ok": 0,
            "fact": "KEN wydawała podręczniki po polsku i wprowadziła do szkół przyrodę, matematykę i wychowanie fizyczne."},
    "manufaktury": {"name": "Manufaktury", "epoch": 3, "req": ["splaw"], "cost": {"wood": 8, "stone": 4},
                    "effect": "Kamienice kupieckie +2 srebra, żupy i huty +2 srebra.",
                    "q": "Czym była manufaktura?",
                    "a": ["Dużym warsztatem z podziałem pracy między wielu robotników", "Rodzajem armaty",
                          "Dworem szlacheckim", "Sądem miejskim"], "ok": 0,
                    "fact": "Za Stanisława Augusta powstawały manufaktury pasów kontuszowych, fajansu i sukna. "
                            "Słynne pasy słuckie tkano z jedwabiu i złotej nici."},
    "konstytucja": {"name": "Konstytucja 3 maja", "epoch": 3, "req": ["elekcja"], "cost": {"silver": 10, "food": 4},
                    "effect": "+3 morale we wszystkich bitwach.",
                    "q": "Którego dnia uchwalono Konstytucję, pierwszą taką w Europie?",
                    "a": ["3 maja 1791", "11 listopada 1918", "15 lipca 1410", "24 marca 1794"], "ok": 0,
                    "fact": "Konstytucja zniosła liberum veto i wolną elekcję oraz wzięła chłopów „pod opiekę prawa”. "
                            "Była pierwszą nowoczesną konstytucją w Europie i drugą na świecie, po amerykańskiej."},
    "kosy": {"name": "Kosy na sztorc", "epoch": 3, "req": ["folwark"], "cost": {"wood": 6, "food": 4},
             "effect": "Odblokowuje kartę: Kosynierzy (siła 7). Folwarki +1 żywności.",
             "q": "Jak zamieniano kosę w broń kosynierów?",
             "a": ["Osadzano ostrze pionowo na drzewcu", "Wkładano ją do armaty", "Przetapiano na szablę", "Mocowano do tarczy"], "ok": 0,
             "fact": "Kosa „na sztorc” była prostą, tanią i groźną bronią. Pod Racławicami kosynierzy zdobyli rosyjskie armaty."},
}

# ---------------------------------------------------------------- PYTANIA (po 32 na epokę)
QUESTIONS = {
    0: [
        ("W którym roku wybuchła wojna trzynastoletnia z Zakonem?", ["1454", "1410", "1525", "1569"], 0),
        ("Jaki pokój zakończył wojnę trzynastoletnią w 1466 roku?", ["Drugi pokój toruński", "Pokój w Oliwie", "Pokój w Kaliszu", "Rozejm w Jamie Zapolskim"], 0),
        ("Jaką krainę nad morzem Polska odzyskała w 1466 roku?", ["Pomorze Gdańskie", "Śląsk", "Inflanty", "Podole"], 0),
        ("Który król prowadził wojnę trzynastoletnią?", ["Kazimierz Jagiellończyk", "Zygmunt Stary", "Stefan Batory", "Władysław Jagiełło"], 0),
        ("Jak nazywał się sojusz miast i szlachty pruskiej przeciw Zakonowi?", ["Związek Pruski", "Hanza", "Konfederacja barska", "Związek Jaszczurczy"], 0),
        ("Kto dowodził zwycięską armią polską pod Świecinem w 1462 roku?", ["Piotr Dunin", "Jan Zamoyski", "Stefan Czarniecki", "Jan Tarnowski"], 0),
        ("W jaki sposób Polacy zdobyli Malbork w 1457 roku?", ["Odkupili go od zaciężnych Zakonu", "Zburzyli mury armatami", "Wykopali tunel", "Dostali go w posagu"], 0),
        ("Kogo nazywano „matką królów”?", ["Elżbietę Rakuszankę", "Bonę Sforzę", "Annę Jagiellonkę", "Barbarę Radziwiłłównę"], 0),
        ("Który syn Kazimierza Jagiellończyka został ogłoszony świętym?", ["Kazimierz", "Zygmunt", "Aleksander", "Jan Olbracht"], 0),
        ("Kto złożył hołd pruski w 1525 roku?", ["Albrecht Hohenzollern", "Ulrich von Jungingen", "Iwan Groźny", "Henryk Walezy"], 0),
        ("Gdzie odbył się hołd pruski?", ["Na Rynku w Krakowie", "W Malborku", "W Gdańsku", "Na Wawelu w katedrze"], 0),
        ("Kim była Bona Sforza?", ["Włoską księżniczką, żoną Zygmunta Starego", "Królową Szwecji", "Matką Kopernika", "Żoną Batorego"], 0),
        ("W jakim stylu zbudowano Kaplicę Zygmuntowską na Wawelu?", ["Renesansowym", "Gotyckim", "Romańskim", "Barokowym"], 0),
        ("Kto napisał „Krótką rozprawę między trzema osobami, Panem, Wójtem a Plebanem”?", ["Mikołaj Rej", "Jan Kochanowski", "Ignacy Krasicki", "Adam Mickiewicz"], 0),
        ("Kto napisał „Treny” po śmierci córki Urszulki?", ["Jan Kochanowski", "Mikołaj Rej", "Mikołaj Kopernik", "Jan Długosz"], 0),
        ("W którym mieście urodził się Mikołaj Kopernik?", ["W Toruniu", "W Krakowie", "W Gdańsku", "We Fromborku"], 0),
        ("Co według Kopernika znajduje się w środku układu planet?", ["Słońce", "Ziemia", "Księżyc", "Gwiazda Polarna"], 0),
        ("Jaki zamek przed Krzyżakami bronił Kopernik w latach 1520–1521?", ["Zamek w Olsztynie", "Malbork", "Wawel", "Zamek w Lublinie"], 0),
        ("Co oznaczała konstytucja „Nihil novi” z 1505 roku?", ["Nic nowego bez zgody sejmu", "Nowy podatek od soli", "Zakaz druku książek", "Nowy herb Polski"], 0),
        ("Z jakich dwóch izb składał się sejm walny?", ["Z senatu i izby poselskiej", "Z sądu i rady miejskiej", "Z hetmanów i biskupów", "Z kupców i rzemieślników"], 0),
        ("Kto był ostatnim królem z dynastii Jagiellonów?", ["Zygmunt August", "Stefan Batory", "Zygmunt Stary", "Henryk Walezy"], 0),
        ("Jak nazywał się ruch odnowy Kościoła w XVI wieku zapoczątkowany przez Marcina Lutra?", ["Reformacja", "Oświecenie", "Renesans", "Sarmatyzm"], 0),
        ("Dlaczego Rzeczpospolitą nazywano „państwem bez stosów”?", ["Panowała w niej tolerancja religijna", "Nie było w niej lasów", "Zakazano palenia ognisk", "Nie budowano zamków"], 0),
        ("Co gwarantowała konfederacja warszawska z 1573 roku?", ["Pokój między wyznaniami", "Niskie podatki", "Wolność handlu zbożem", "Budowę floty"], 0),
        ("Jakie zboże najczęściej sprzedawano za granicę przez Gdańsk?", ["Żyto", "Ryż", "Kukurydzę", "Ziemniaki"], 0),
        ("Kim był flisak?", ["Człowiekiem spławiającym towary rzeką", "Strażnikiem zamku", "Pisarzem królewskim", "Kowalem"], 0),
        ("W którym roku odbył się hołd pruski?", ["1525", "1466", "1569", "1410"], 0),
        ("Jak nazywał się słynny dzwon odlany w 1520 roku dla katedry na Wawelu?", ["Zygmunt", "Jagiellon", "Kazimierz", "Wawel"], 0),
        ("Kim była szlachta?", ["Stanem posiadającym ziemię i prawa polityczne", "Mieszkańcami miast", "Duchowieństwem", "Chłopami pańszczyźnianymi"], 0),
        ("Który władca założył pocztę królewską w 1558 roku?", ["Zygmunt August", "Kazimierz Jagiellończyk", "Jan III Sobieski", "Stanisław August"], 0),
        ("Jak nazywano dwór i gospodarstwo szlacheckie produkujące zboże?", ["Folwark", "Gród", "Faktoria", "Kolegium"], 0),
        ("Która włoska królowa sprowadziła do Polski wiele warzyw, nazywanych potem „włoszczyzną”?", ["Bona Sforza", "Elżbieta Rakuszanka", "Ludwika Maria", "Maria Kazimiera"], 0),
    ],
    1: [
        ("Jakie państwa połączyła unia lubelska w 1569 roku?", ["Koronę Polską i Wielkie Księstwo Litewskie", "Polskę i Szwecję", "Polskę i Węgry", "Litwę i Moskwę"], 0),
        ("W którym roku odbyła się pierwsza wolna elekcja?", ["1573", "1569", "1505", "1610"], 0),
        ("Kto był pierwszym królem elekcyjnym?", ["Henryk Walezy", "Stefan Batory", "Zygmunt III Waza", "Zygmunt August"], 0),
        ("Dlaczego Henryk Walezy potajemnie wyjechał z Polski?", ["Aby objąć tron Francji", "Bo przegrał wojnę", "Bo nie lubił zimy", "Aby wziąć ślub w Hiszpanii"], 0),
        ("Czym były artykuły henrykowskie?", ["Zasadami ustroju, które musiał zaprzysiąc każdy król", "Prawem morskim", "Spisem podatków", "Kroniką Polski"], 0),
        ("Jak nazywano osobiste zobowiązania nowo wybranego króla?", ["Pacta conventa", "Nihil novi", "Liberum veto", "Dagome iudex"], 0),
        ("Który król elekcyjny poślubił Annę Jagiellonkę?", ["Stefan Batory", "Henryk Walezy", "Zygmunt III Waza", "Jan III Sobieski"], 0),
        ("Skąd pochodził Stefan Batory?", ["Z Siedmiogrodu na Węgrzech", "Ze Szwecji", "Z Francji", "Z Litwy"], 0),
        ("Jaką ważną twierdzę zdobył Batory w 1579 roku?", ["Połock", "Moskwę", "Smoleńsk", "Kijów"], 0),
        ("Jakie miasto oblegał Batory w latach 1581–1582?", ["Psków", "Gdańsk", "Ryga", "Nowogród"], 0),
        ("Jak zakończyła się wojna Batorego z Moskwą w 1582 roku?", ["Rozejmem w Jamie Zapolskim", "Pokojem toruńskim", "Pokojem w Oliwie", "Unią w Krewie"], 0),
        ("Z którym carem walczył Stefan Batory?", ["Z Iwanem IV Groźnym", "Z Piotrem Wielkim", "Z Borysem Godunowem", "Z Katarzyną II"], 0),
        ("Kto był hetmanem i kanclerzem, założycielem Zamościa?", ["Jan Zamoyski", "Stanisław Żółkiewski", "Jan Karol Chodkiewicz", "Stefan Czarniecki"], 0),
        ("Jaką uczelnię założył Jan Zamoyski w 1594 roku?", ["Akademię Zamojską", "Akademię Krakowską", "Szkołę Rycerską", "Uniwersytet Wileński"], 0),
        ("Który król przeniósł swoją siedzibę z Krakowa do Warszawy?", ["Zygmunt III Waza", "Stefan Batory", "Zygmunt August", "Jan III Sobieski"], 0),
        ("Kogo upamiętnia kolumna na placu Zamkowym w Warszawie?", ["Zygmunta III Wazę", "Jana III Sobieskiego", "Stefana Batorego", "Tadeusza Kościuszkę"], 0),
        ("W którym roku rozegrała się bitwa pod Kłuszynem?", ["1610", "1683", "1655", "1579"], 0),
        ("Kto dowodził wojskiem polskim pod Kłuszynem?", ["Stanisław Żółkiewski", "Jan III Sobieski", "Stefan Batory", "Kazimierz Pułaski"], 0),
        ("W których latach Polacy stacjonowali na Kremlu w Moskwie?", ["1610–1612", "1572–1574", "1655–1660", "1768–1772"], 0),
        ("Z kim Polacy walczyli pod Kircholmem w 1605 roku?", ["Ze Szwedami", "Z Turkami", "Z Krzyżakami", "Z Tatarami"], 0),
        ("Kto dowodził zwycięską husarią pod Kircholmem?", ["Jan Karol Chodkiewicz", "Stanisław Żółkiewski", "Jan Zamoyski", "Stefan Czarniecki"], 0),
        ("Z jakim wrogiem toczono bitwę pod Chocimiem w 1621 roku?", ["Z Turkami", "Ze Szwedami", "Z Moskwą", "Z Prusami"], 0),
        ("Pod jaką miejscowością zginął hetman Żółkiewski w 1620 roku?", ["Pod Cecorą", "Pod Grunwaldem", "Pod Wiedniem", "Pod Racławicami"], 0),
        ("Jak nazywano stałe wojsko chroniące kresy, opłacane z części dochodów króla?", ["Wojsko kwarciane", "Pospolite ruszenie", "Gwardia piesza", "Straż miejska"], 0),
        ("Gdzie znajdowała się Sicz Zaporoska?", ["Za porohami Dniepru", "Nad Bałtykiem", "W Tatrach", "Nad Wisłą w Krakowie"], 0),
        ("Czym był rejestr kozacki?", ["Listą Kozaków służących za żołd króla", "Mapą Ukrainy", "Księgą podatków", "Kroniką Kozaków"], 0),
        ("Jaką długą broń miał husarz do pierwszego uderzenia?", ["Kopię", "Muszkiet", "Kosę", "Halabardę"], 0),
        ("Kto był królem w czasie bitwy pod Kłuszynem?", ["Zygmunt III Waza", "Stefan Batory", "Władysław IV", "Jan Kazimierz"], 0),
        ("Co postanowiła unia brzeska z 1596 roku?", ["Połączenie części prawosławnych z Kościołem katolickim", "Połączenie Polski z Litwą", "Pokój ze Szwecją", "Założenie Zamościa"], 0),
        ("Co oznaczało słowo „Obojga” w nazwie Rzeczpospolita Obojga Narodów?", ["Polaków i Litwinów", "Szlachtę i chłopów", "Kraków i Warszawę", "Króla i sejm"], 0),
        ("Jak nazywał się architekt Zamościa?", ["Bernardo Morando", "Bartolomeo Berrecci", "Wit Stwosz", "Tylman z Gameren"], 0),
        ("Który hetman zginął w 1621 roku w obozie pod Chocimiem?", ["Jan Karol Chodkiewicz", "Stanisław Żółkiewski", "Jan Zamoyski", "Stefan Czarniecki"], 0),
    ],
    2: [
        ("W którym roku wybuchło powstanie Chmielnickiego?", ["1648", "1655", "1683", "1610"], 0),
        ("Kto przewodził powstaniu kozackiemu w 1648 roku?", ["Bohdan Chmielnicki", "Iwan Mazepa", "Stefan Czarniecki", "Piotr Konaszewicz"], 0),
        ("W którym roku zaczął się potop szwedzki?", ["1655", "1648", "1683", "1700"], 0),
        ("Kto dowodził obroną Jasnej Góry w 1655 roku?", ["Przeor Augustyn Kordecki", "Stefan Czarniecki", "Jan Kazimierz", "Jan Sobieski"], 0),
        ("Ile mniej więcej trwało oblężenie Jasnej Góry w 1655 roku?", ["Około 40 dni", "Dwa dni", "Trzy lata", "Jeden rok"], 0),
        ("Który król złożył śluby lwowskie w 1656 roku?", ["Jan Kazimierz", "Zygmunt III Waza", "Jan III Sobieski", "Władysław IV"], 0),
        ("Kto prowadził wojnę szarpaną ze Szwedami podczas potopu?", ["Stefan Czarniecki", "Jan Zamoyski", "Kazimierz Pułaski", "Tadeusz Kościuszko"], 0),
        ("W jakiej pieśni pojawia się Czarniecki, który „do Poznania” wracał „przez morze”?", ["W Mazurku Dąbrowskiego", "W Bogurodzicy", "W Rocie", "W Gaude Mater"], 0),
        ("Co postanowiły traktaty welawsko-bydgoskie (1657)?", ["Prusy Książęce przestały być lennem Polski", "Polska odzyskała Inflanty", "Szwecja oddała Gdańsk", "Powstała unia z Litwą"], 0),
        ("Jaki pokój zakończył potop szwedzki w 1660 roku?", ["Pokój w Oliwie", "Pokój toruński", "Pokój w Karłowicach", "Rozejm w Andruszowie"], 0),
        ("W którym roku po raz pierwszy zerwano sejm przez liberum veto?", ["1652", "1569", "1791", "1505"], 0),
        ("Co oznaczało liberum veto?", ["Jeden poseł mógł zerwać sejm", "Wolny wybór króla", "Prawo do rokoszu", "Zakaz wojen"], 0),
        ("Kto dowodził zwycięstwem pod Chocimiem w 1673 roku?", ["Hetman Jan Sobieski", "Stefan Czarniecki", "Jan Zamoyski", "Kazimierz Pułaski"], 0),
        ("W którym roku miała miejsce odsiecz wiedeńska?", ["1683", "1673", "1610", "1655"], 0),
        ("Kto dowodził armią turecką pod Wiedniem?", ["Wielki wezyr Kara Mustafa", "Sułtan Sulejman", "Chan Dżanibek", "Iwan Mazepa"], 0),
        ("Stolicą jakiego państwa był Wiedeń?", ["Austrii (Cesarstwa)", "Węgier", "Czech", "Turcji"], 0),
        ("Jak nazywa się barokowa rezydencja Jana III Sobieskiego pod Warszawą?", ["Wilanów", "Łazienki", "Wawel", "Niepołomice"], 0),
        ("Jak Sobieski opisał papieżowi zwycięstwo pod Wiedniem?", ["Przybyliśmy, zobaczyliśmy, a Bóg zwyciężył", "Przybyłem, zobaczyłem, zwyciężyłem", "Jeszcze Polska nie zginęła", "Polacy nie gęsi"], 0),
        ("Jak nazywa się styl w sztuce XVII wieku, pełen przepychu i złoceń?", ["Barok", "Gotyk", "Renesans", "Klasycyzm"], 0),
        ("Jaką twierdzę Polska odzyskała pokojem w Karłowicach (1699)?", ["Kamieniec Podolski", "Malbork", "Smoleńsk", "Rygę"], 0),
        ("Komu Rzeczpospolita oddała Kamieniec Podolski w 1672 roku?", ["Turcji", "Szwecji", "Moskwie", "Prusom"], 0),
        ("Który bohater powieści Sienkiewicza bronił Kamieńca Podolskiego?", ["Pan Wołodyjowski", "Kmicic", "Skrzetuski", "Zagłoba"], 0),
        ("Kto napisał „Trylogię” (Ogniem i mieczem, Potop, Pan Wołodyjowski)?", ["Henryk Sienkiewicz", "Adam Mickiewicz", "Bolesław Prus", "Juliusz Słowacki"], 0),
        ("Jak nazywał się długi, wierzchni strój szlachecki?", ["Kontusz", "Toga", "Frak", "Kubrak rycerski"], 0),
        ("Jak nazywano przekonanie szlachty, że pochodzi od starożytnego ludu Sarmatów?", ["Sarmatyzm", "Oświecenie", "Pozytywizm", "Romantyzm"], 0),
        ("Na czym polegała elekcja viritim?", ["Każdy szlachcic mógł osobiście głosować", "Głosowali tylko senatorowie", "Króla wybierał papież", "Króla losowano"], 0),
        ("Gdzie odbywały się wolne elekcje?", ["Na Woli pod Warszawą", "Na Wawelu", "W Gnieźnie", "W Lublinie"], 0),
        ("Kto był ostatnim królem z dynastii Wazów?", ["Jan Kazimierz", "Zygmunt III", "Władysław IV", "Michał Korybut"], 0),
        ("W którym roku Jan Kazimierz abdykował?", ["1668", "1655", "1683", "1610"], 0),
        ("Kto został królem po abdykacji Jana Kazimierza?", ["Michał Korybut Wiśniowiecki", "Jan III Sobieski", "August II Mocny", "Stefan Batory"], 0),
        ("Jak nazywał się szwedzki król, który najechał Polskę w 1655 roku?", ["Karol X Gustaw", "Gustaw Adolf", "Karol XII", "Eryk XIV"], 0),
        ("Jaką broń najbardziej ceniła sobie szlachta w XVII wieku?", ["Szablę", "Kuszę", "Proca", "Topór kamienny"], 0),
    ],
    3: [
        ("Jaki przydomek miał król August II z dynastii Wettynów?", ["Mocny", "Wielki", "Śmiały", "Chrobry"], 0),
        ("W jakich latach toczyła się wielka wojna północna?", ["1700–1721", "1655–1660", "1768–1772", "1454–1466"], 0),
        ("Dlaczego sejm z 1717 roku nazwano niemym?", ["Posłowie nie mogli zabierać głosu", "Obradował w nocy", "Odbył się w kościele", "Nikt na niego nie przyszedł"], 0),
        ("Kto był ostatnim królem Rzeczypospolitej?", ["Stanisław August Poniatowski", "August III Sas", "Jan III Sobieski", "Stanisław Leszczyński"], 0),
        ("W którym roku Stanisław August został królem?", ["1764", "1791", "1795", "1733"], 0),
        ("W którym roku zawiązano konfederację barską?", ["1768", "1772", "1791", "1794"], 0),
        ("W jakim mieście zawiązano konfederację barską?", ["W Barze na Podolu", "W Krakowie", "W Warszawie", "W Wilnie"], 0),
        ("Gdzie zginął Kazimierz Pułaski w 1779 roku?", ["Pod Savannah w Ameryce", "Pod Racławicami", "W Częstochowie", "W Paryżu"], 0),
        ("W którym roku dokonano pierwszego rozbioru Polski?", ["1772", "1793", "1795", "1764"], 0),
        ("Które państwa dokonały rozbiorów Polski?", ["Rosja, Prusy i Austria", "Szwecja, Dania i Prusy", "Turcja, Rosja i Węgry", "Francja, Austria i Rosja"], 0),
        ("W którym roku powołano Komisję Edukacji Narodowej?", ["1773", "1791", "1765", "1795"], 0),
        ("Czym były „obiady czwartkowe” u Stanisława Augusta?", ["Spotkaniami uczonych, poetów i artystów", "Ucztami dla wojska", "Sejmikami szlachty", "Jarmarkami"], 0),
        ("W których latach obradował Sejm Wielki (Czteroletni)?", ["1788–1792", "1764–1768", "1772–1776", "1794–1798"], 0),
        ("Co zniosła Konstytucja 3 maja?", ["Liberum veto i wolną elekcję", "Szlachtę", "Wojsko", "Akademię Krakowską"], 0),
        ("Który ksiądz był jednym z twórców Konstytucji 3 maja?", ["Hugo Kołłątaj", "Augustyn Kordecki", "Piotr Skarga", "Ignacy Krasicki"], 0),
        ("Jak nazywano magnatów, którzy w 1792 roku wezwali Rosję przeciw Konstytucji?", ["Targowiczanie", "Barzanie", "Kosynierzy", "Reformatorzy"], 0),
        ("W którym roku dokonano drugiego rozbioru Polski?", ["1793", "1772", "1795", "1791"], 0),
        ("Gdzie Tadeusz Kościuszko złożył przysięgę 24 marca 1794 roku?", ["Na Rynku w Krakowie", "W Warszawie na Zamku", "W Wilnie", "Pod Racławicami"], 0),
        ("Kiedy odbyła się bitwa pod Racławicami?", ["4 kwietnia 1794", "3 maja 1791", "15 lipca 1410", "12 września 1683"], 0),
        ("Co zdobył pod Racławicami Bartosz Głowacki?", ["Rosyjską armatę", "Sztandar Szwedów", "Klucze do Warszawy", "Koronę cara"], 0),
        ("Co dawał chłopom uniwersał połaniecki?", ["Wolność osobistą i zmniejszenie pańszczyzny", "Szlachectwo", "Prawo wyboru króla", "Zwolnienie z wojska"], 0),
        ("Co stało się z Kościuszką w bitwie pod Maciejowicami?", ["Został ranny i wzięty do niewoli", "Zwyciężył", "Uciekł do Francji", "Został królem"], 0),
        ("Który rosyjski generał dowodził rzezią Pragi w 1794 roku?", ["Aleksander Suworow", "Grigorij Potiomkin", "Michaił Kutuzow", "Piotr Rumiancew"], 0),
        ("W którym roku dokonano trzeciego rozbioru Polski?", ["1795", "1793", "1772", "1807"], 0),
        ("W jakiej wojnie walczył Kościuszko, zanim wrócił do Polski?", ["W wojnie o niepodległość Stanów Zjednoczonych", "W wojnie trzynastoletniej", "W potopie szwedzkim", "W wojnie o Wiedeń"], 0),
        ("W jakim mieście można dziś zobaczyć Panoramę Racławicką?", ["We Wrocławiu", "W Krakowie", "W Warszawie", "W Racławicach"], 0),
        ("W którym roku powstał Mazurek Dąbrowskiego?", ["1797", "1791", "1683", "1918"], 0),
        ("W którym roku założono w Warszawie Teatr Narodowy?", ["1765", "1683", "1795", "1569"], 0),
        ("Jak nazywa się klasycystyczna rezydencja Stanisława Augusta w Warszawie?", ["Łazienki Królewskie", "Wilanów", "Wawel", "Zamek w Malborku"], 0),
        ("Do czego nawiązywał klasycyzm?", ["Do sztuki starożytnej Grecji i Rzymu", "Do sztuki Egiptu", "Do gotyku", "Do sztuki japońskiej"], 0),
        ("Jak nazywało się czasopismo oświeceniowe wydawane od 1765 roku?", ["Monitor", "Merkuriusz Polski", "Kurier", "Głos Ludu"], 0),
        ("Kto napisał „Bajki i przypowieści”?", ["Ignacy Krasicki", "Jan Kochanowski", "Mikołaj Rej", "Adam Naruszewicz"], 0),
    ],
}


def pick_question(epoch, used):
    """Losuje pytanie z epoki, którego jeszcze nie było (used – zbiór treści pytań)."""
    import random as _r
    pool = [q for q in QUESTIONS[epoch] if q[0] not in used]
    if not pool:
        for q in QUESTIONS[epoch]:
            used.discard(q[0])
        pool = list(QUESTIONS[epoch])
    q = _r.choice(pool)
    used.add(q[0])
    return q


# ---------------------------------------------------------------- POSTACIE (15)
CHARACTERS = {
    "kazimierz_j": {"name": "Kazimierz Jagiellończyk", "title": "Król Polski", "years": "1427–1492",
                    "p": {"hair": (110, 75, 45), "beard": None, "head": "crown_b", "cloth": (150, 30, 40), "bg": (90, 80, 60)},
                    "bio": "Syn Władysława Jagiełły. Poparł Związek Pruski i po wojnie trzynastoletniej odzyskał Pomorze Gdańskie.",
                    "fact": "Jego synowie zasiadali na tronach Polski, Litwy, Czech i Węgier – dlatego żonę Elżbietę nazywano „matką królów”."},
    "kopernik": {"name": "Mikołaj Kopernik", "title": "Astronom i administrator", "years": "1473–1543",
                 "p": {"hair": (70, 50, 35), "beard": None, "head": "beret", "cloth": (130, 40, 40), "bg": (40, 50, 90)},
                 "bio": "Twórca teorii heliocentrycznej. Był też lekarzem, ekonomistą i zarządcą dóbr warmińskich.",
                 "fact": "W latach 1520–1521 przygotował obronę zamku w Olsztynie przed wojskami Zakonu."},
    "zygmunt": {"name": "Zygmunt Stary", "title": "Król Polski", "years": "1467–1548",
                "p": {"hair": (200, 200, 200), "beard": None, "head": "crown_b", "cloth": (110, 40, 120), "bg": (110, 90, 50)},
                "bio": "Król złotego wieku. Przyjął hołd pruski w 1525 r. i przebudował Wawel w stylu renesansowym.",
                "fact": "Dzwon Zygmunt na Wawelu nosi jego imię."},
    "bona": {"name": "Bona Sforza", "title": "Królowa Polski", "years": "1494–1557",
             "p": {"hair": (60, 40, 30), "beard": None, "head": "veil_dark", "cloth": (40, 40, 45), "bg": (120, 90, 60)},
             "bio": "Włoska księżniczka z Mediolanu, żona Zygmunta Starego. Zręcznie zarządzała majątkiem i dobrami królewskimi.",
             "fact": "Tradycja mówi, że to ona rozpowszechniła w Polsce warzywa – stąd nazwa „włoszczyzna”."},
    "batory": {"name": "Stefan Batory", "title": "Król elekcyjny", "years": "1533–1586",
               "p": {"hair": (60, 45, 35), "beard": "full", "head": "kolpak", "cloth": (150, 40, 40), "bg": (70, 60, 90)},
               "bio": "Książę Siedmiogrodu wybrany na króla Polski. Zwycięsko walczył z Moskwą i odzyskał Inflanty.",
               "fact": "Założył Akademię Wileńską (1579), dziś Uniwersytet Wileński."},
    "zamoyski": {"name": "Jan Zamoyski", "title": "Kanclerz i hetman", "years": "1542–1605",
                 "p": {"hair": (50, 40, 30), "beard": "short", "head": "kolpak", "cloth": (60, 90, 140), "bg": (90, 110, 80)},
                 "bio": "Najbliższy współpracownik Batorego. Założył Zamość i Akademię Zamojską.",
                 "fact": "Mówił: „Takie będą Rzeczypospolite, jakie ich młodzieży chowanie”."},
    "zolkiewski": {"name": "Stanisław Żółkiewski", "title": "Hetman", "years": "1547–1620",
                   "p": {"hair": (200, 200, 195), "beard": "full", "head": "kolpak", "cloth": (110, 70, 40), "bg": (80, 70, 60)},
                   "bio": "Zwycięzca spod Kłuszyna (1610). Zginął pod Cecorą, walcząc z Turkami.",
                   "fact": "Pod Kłuszynem jego wojsko pokonało armię kilkakrotnie liczniejszą."},
    "kordecki": {"name": "Augustyn Kordecki", "title": "Przeor Jasnej Góry", "years": "1603–1673",
                 "p": {"hair": (90, 70, 50), "beard": "short", "head": "habit", "cloth": (235, 233, 225), "bg": (90, 90, 110)},
                 "bio": "Paulin, przeor klasztoru na Jasnej Górze. Zorganizował obronę przed Szwedami w 1655 r.",
                 "fact": "Obrona Jasnej Góry podniosła ducha w całym kraju i stała się początkiem walki z potopem."},
    "czarniecki": {"name": "Stefan Czarniecki", "title": "Hetman polny", "years": "1599–1665",
                   "p": {"hair": (60, 50, 40), "beard": "mustache_big", "head": "kolpak", "cloth": (140, 30, 30), "bg": (60, 80, 70)},
                   "bio": "Mistrz wojny szarpanej ze Szwedami podczas potopu. Walczył też z Kozakami i Moskwą.",
                   "fact": "Jest jedynym bohaterem dawnej Rzeczypospolitej wymienionym w polskim hymnie."},
    "sobieski": {"name": "Jan III Sobieski", "title": "Król Polski", "years": "1629–1696",
                 "p": {"hair": (50, 40, 35), "beard": "mustache_big", "head": "crown_b", "cloth": (170, 40, 40), "bg": (100, 70, 50)},
                 "bio": "Zwycięzca spod Chocimia (1673) i Wiednia (1683). Nazywany „Lwem Lechistanu”.",
                 "fact": "Pisał piękne listy do żony Marysieńki – zachowało się ich kilkaset."},
    "pulaski": {"name": "Kazimierz Pułaski", "title": "Konfederat barski", "years": "1745–1779",
                "p": {"hair": (70, 50, 35), "beard": "mustache", "head": "rogatywka", "cloth": (60, 70, 130), "bg": (110, 80, 60)},
                "bio": "Jeden z wodzów konfederacji barskiej, obrońca Jasnej Góry (1771). Później bohater wojny o niepodległość USA.",
                "fact": "Nazywany jest „ojcem amerykańskiej kawalerii”."},
    "poniatowski": {"name": "Stanisław August", "title": "Ostatni król", "years": "1732–1798",
                    "p": {"hair": (230, 230, 225), "beard": None, "head": "wig", "cloth": (80, 60, 130), "bg": (90, 110, 130)},
                    "bio": "Król-mecenas sztuki i nauki. Założył Szkołę Rycerską, popierał KEN i Konstytucję 3 maja.",
                    "fact": "W Łazienkach urządzał „obiady czwartkowe” dla poetów i uczonych."},
    "kollataj": {"name": "Hugo Kołłątaj", "title": "Ksiądz i reformator", "years": "1750–1812",
                 "p": {"hair": (110, 80, 60), "beard": None, "head": "collar", "cloth": (30, 30, 35), "bg": (100, 100, 80)},
                 "bio": "Reformator Akademii Krakowskiej, jeden z autorów Konstytucji 3 maja i uczestnik insurekcji.",
                 "fact": "Grupę jego współpracowników nazywano „Kuźnicą Kołłątajowską”."},
    "kosciuszko": {"name": "Tadeusz Kościuszko", "title": "Naczelnik insurekcji", "years": "1746–1817",
                   "p": {"hair": (120, 80, 50), "beard": None, "head": "none", "cloth": (220, 215, 200), "bg": (70, 100, 70)},
                   "bio": "Bohater dwóch narodów: Polski i USA. W 1794 r. stanął na czele powstania.",
                   "fact": "Pod Racławicami założył chłopską sukmanę na znak, że walczy cały naród."},
    "glowacki": {"name": "Bartosz Głowacki", "title": "Kosynier", "years": "ok. 1758–1794",
                 "p": {"hair": (160, 110, 60), "beard": None, "head": "kapelusz", "cloth": (225, 220, 205), "bg": (90, 120, 80)},
                 "bio": "Chłop spod Krakowa. Pod Racławicami zgasił czapką lont rosyjskiej armaty i ją zdobył.",
                 "fact": "Za odwagę Kościuszko mianował go chorążym i nadał mu wolność."},
}

HERO = {"name": "Damian Ściseł", "title": "Kronikarz i doradca", "years": "wędrowny",
        "p": {"hair": (222, 184, 96), "beard": None, "head": "hood", "cloth": (110, 50, 150), "bg": (60, 50, 80)}}

# ---------------------------------------------------------------- ZDARZENIA LOSOWE
EVENTS = [
    {"id": "zaraza", "title": "Morowe powietrze!", "icon": "plague",
     "text": "Do miasta dotarła dżuma. Lekarze w maskach z długimi dziobami krążą po ulicach. Damian notuje: "
             "„Kwarantanna – odosobnienie chorych przez czterdzieści dni – to najlepsza broń przeciw zarazie.”",
     "choices": [
         ("Zamknąć bramy i odizolować chorych", {"food": -4, "silver": -3}, "Zaraza wygasła szybciej niż w sąsiednich miastach."),
         ("Udawać, że nic się nie dzieje", {"food": -10, "silver": -5}, "Choroba zabrała wielu ludzi. Pola stoją puste."),
     ]},
    {"id": "czambul", "title": "Czambuł tatarski!", "icon": "raid",
     "text": "Na horyzoncie tumany kurzu – to szybki oddział Tatarów. Porywają ludzi i bydło. Trzeba działać od razu!",
     "choices": [
         ("Zapłacić okup (8 srebra)", {"silver": -8}, "Tatarzy zawrócili w step."),
         ("Doradzić pościg!", {"battle": ["e_tatarzy", "e_tatarzy", "e_jazda_ru"]}, ""),
     ]},
    {"id": "poselstwo", "title": "Poselstwo z zagranicy", "icon": "envoy",
     "text": "Posłowie z Wenecji i Francji przybyli z darami i propozycją handlu. Dyplomacja to wymiana, nie tylko ukłony.",
     "choices": [
         ("Wydać ucztę (−6 żywności)", {"food": -6, "silver": 10}, "Posłowie zachwyceni! Zostawili skrzynię dukatów."),
         ("Przyjąć dary i odprawić", {"silver": 4}, "Posłowie wyjechali chłodno, ale dary zostały."),
     ]},
    {"id": "sejmik", "title": "Sejmik szlachecki", "icon": "scholar",
     "text": "Szlachta zjechała na sejmik i żąda zwolnienia z podatków na wojsko. „Złota wolność!” – krzyczą. "
             "Damian szepcze: „Bez podatków nie ma armii. Bez armii nie ma wolności”.",
     "choices": [
         ("Przekonać ich mową (pytanie z historii)", {"quiz": 6}, ""),
         ("Ustąpić szlachcie (−6 srebra)", {"silver": -6}, "Szlachta wiwatuje, skarbiec płacze."),
     ]},
    {"id": "susza", "title": "Susza", "icon": "sun",
     "text": "Zboże usycha na polach. Ceny chleba rosną z dnia na dzień – bo podaż mała, a popyt ogromny.",
     "choices": [
         ("Otworzyć spichlerze (−8 żywności)", {"food": -8}, "Głodu nie było. Ludzie zapamiętają twoją hojność."),
         ("Kupić zboże w Gdańsku (−8 srebra)", {"silver": -8, "food": 2}, "Drogo, ale bezpiecznie."),
     ]},
    {"id": "jarmark", "title": "Jarmark dominikański w Gdańsku", "icon": "market",
     "text": "Na wielki jarmark zjechali kupcy z Holandii i Anglii. Płacą dobrze za zboże i drewno.",
     "choices": [
         ("Sprzedać 10 drewna za 8 srebra", {"wood": -10, "silver": 8}, "Holendrzy kupili drewno na maszty."),
         ("Sprzedać 12 żywności za 9 srebra", {"food": -12, "silver": 9}, "Zboże popłynęło do Amsterdamu."),
         ("Tylko popatrzeć", {}, "Damian kupił sobie nowy kałamarz. Za swoje."),
     ]},
    {"id": "moneta", "title": "Psucie monety", "icon": "amber",
     "text": "Mennica proponuje bić monety z mniejszą ilością srebra. „Zarobimy od razu!” – mówi mincerz. "
             "Damian przypomina Kopernika: „Zły pieniądz wypiera dobry, a ceny rosną”.",
     "choices": [
         ("Psuć monetę (+10 srebra teraz, −6 żywności)", {"silver": 10, "food": -6}, "Ceny skoczyły w górę. Ludzie narzekają na drożyznę."),
         ("Utrzymać dobrą monetę", {"silver": 2}, "Kupcy chętniej handlują – ufają twoim monetom."),
     ]},
    {"id": "pozar", "title": "Pożar przedmieścia", "icon": "fire",
     "text": "Ogień przeskakuje z dachu na dach drewnianych domów. Trzeba wybrać, co ratować.",
     "choices": [
         ("Ratować spichlerze", {"wood": -8}, "Zboże ocalało, spłonął skład drewna."),
         ("Ratować skład drewna", {"food": -8}, "Drewno ocalało, ale część zapasów przepadła."),
     ]},
    {"id": "kometa", "title": "Kometa nad Rzecząpospolitą", "icon": "comet",
     "text": "Na niebie świeci gwiazda z ogonem. Ludzie boją się wojny i zarazy. Astronomowie spokojnie mierzą jej drogę.",
     "choices": [
         ("Wezwać astronomów do kolegium (−4 srebra)", {"silver": -4, "morale": 2}, "Uczeni wyjaśnili zjawisko. Ludzie się uspokoili (+2 morale)."),
         ("Zignorować", {}, "Kometa poleciała dalej. Plotki zostały."),
     ]},
    {"id": "urodzaj", "title": "Urodzaj", "icon": "wheat",
     "text": "Zbiory wyjątkowo obfite! Ale wszyscy mają dużo zboża, więc w Gdańsku płacą za nie mniej.",
     "choices": [
         ("Zostawić w spichlerzach", {"food": 12}, "Spichlerze pełne po dach."),
         ("Spławić część do Gdańska", {"food": 4, "silver": 5}, "Zarobek mniejszy niż w chudym roku – taka jest ekonomia."),
     ]},
]

CARDS["wegrzy"] = {"name": "Piechota węgierska", "type": "piechota", "power": 6, "unit": "pike", "faction": "cz", "cost": None,
                   "desc": "Doborowi piechurzy, których Batory sprowadził z Siedmiogrodu."}

# ---------------------------------------------------------------- ROZDZIAŁY
CHAPTERS = [
    {
        "id": 0, "epoch": 0, "year": "1454–1466", "place": "Prusy i Malbork",
        "title": "Rozdział I: Wojna o morze",
        "chronicle": [
            "Roku Pańskiego 1454. Miasta pruskie – Gdańsk, Toruń, Elbląg – mają dość rządów Zakonu Krzyżackiego. "
            "Związek Pruski wypowiada posłuszeństwo wielkiemu mistrzowi i prosi króla Kazimierza Jagiellończyka o przyłączenie do Korony.",
            "Król się zgadza. Zaczyna się wojna, która potrwa... no, sami policzcie: od 1454 do 1466. Ja, Damian Ściseł, w tym samym "
            "fioletowym kapturze (trochę wyblakłym po czterdziestu latach od Grunwaldu) znów zostaję królewskim doradcą.",
            "To będzie wojna pieniędzy. Obie strony płacą zaciężnym żołnierzom, a kto pierwszy zbankrutuje, ten przegra. "
            "A krzyżaccy najemnicy w Malborku już od dawna nie widzieli żołdu...",
            "Zadanie: napełnić skarbiec, odlać armaty, przejąć Malbork i rozbić siły Zakonu pod Świecinem.",
        ],
        "map": {"seed": 1454, "lakes": [], "river": [], "forest": 0.24, "hills": 0.06, "capital": (14, 14),
                "landmarks": [((0, 0), "Toruń", "Tu w 1466 r. podpisano drugi pokój toruński. W Toruniu urodził się też Mikołaj Kopernik (1473)."),
                              ((0, 0), "Gdańsk", "Największy port Rzeczypospolitej. Gdańszczanie hojnie finansowali wojnę z Zakonem.")],
                "camps": [((0, 0), "malbork", "Zaciężni w Malborku", ["e_zaciezni_z", "e_zaciezni_z", "e_kusznicy_z", "e_rycerze_z"])]},
        "start_res": {"food": 22, "wood": 22, "stone": 6, "silver": 14},
        "start_deck": ["woje", "woje", "woje", "lucznicy", "lucznicy", "konni"],
        "turns": 30,
        "objectives": [("tech", "armaty"), ("build", "koszary", 2), ("res", "silver", 40), ("camp", "malbork"), ("final",)],
        "final": {"name": "Bitwa pod Świecinem (1462)", "enemy_morale": 32, "defense": False, "terrain": "forest",
                  "deck": ["e_knechci", "e_rycerze_z", "e_zaciezni_z", "e_kusznicy_z", "e_rycerze_z", "e_knechci", "e_zaciezni_z"],
                  "allies": ["zaciezni", "zaciezni"],
                  "intro": "Wrzesień 1462. Piotr Dunin ustawia tabor i strzelców w szyku. Rycerze Zakonu szarżują... prosto na nasze wozy."},
        "dialogue_start": [("kazimierz_j", "Kronikarzu, mam ludzi i mam rację. Brakuje mi tylko pieniędzy. Dużo pieniędzy."),
                           ("damian", "Wasza Królewska Mość, w tej wojnie dukat jest groźniejszy niż miecz. Zacznijmy od kupców i podatków.")],
        "scripted": {5: ("decision", "Posłowie Gdańska proponują pożyczkę na wojnę w zamian za przywileje handlowe.",
                         [("Przyjąć (+14 srebra, −4 żywności)", {"silver": 14, "food": -4}, "Gdańsk dostał przywileje, a król – pieniądze na żołd."),
                          ("Odmówić", {"wood": 4}, "Damian kiwa głową: „Dług jak ciasto – lubi rosnąć”.")]),
                     9: ("decision", "Zaciężni w Malborku piszą: „Zakon nie płaci nam od lat. Sprzedamy zamek temu, kto zapłaci”.",
                         [("Wykupić Malbork (−20 srebra)", {"silver": -20, "beat_camp": "malbork"}, "W czerwcu 1457 r. król wjechał do Malborka – bez jednego wystrzału!"),
                          ("Spróbować zdobyć go siłą", {}, "Mury Malborka są grube... Kliknij obóz na mapie, gdy będziesz gotów.")]),
                     15: ("kazimierz_j", "Piotr Dunin z Prawkowic zebrał zaciężnych. Pod Świecinem rozstrzygnie się wojna!")},
        "victory": "Pod Świecinem Piotr Dunin rozbił wojska Zakonu. W 1466 r. drugi pokój toruński oddał Koronie Pomorze Gdańskie, "
                   "ziemię chełmińską, Malbork i Warmię. Polska znów sięgnęła Bałtyku. Notuję: „Wojny wygrywa ten, kto ma pełny skarbiec i cierpliwość”.",
    },
    {
        "id": 1, "epoch": 1, "year": "1579–1582", "place": "Połock i Wielkie Łuki",
        "title": "Rozdział II: Wyprawy Batorego",
        "chronicle": [
            "Roku 1579. Na tron wybrano Stefana Batorego – księcia Siedmiogrodu, który po polsku mówił słabo, za to wojował "
            "znakomicie. Car Iwan Groźny zajął większość Inflant i nie zamierza ich oddać.",
            "Batory reformuje wojsko: tworzy piechotę wybraniecką, sprowadza armaty i węgierską piechotę. Kanclerz Jan Zamoyski "
            "pilnuje skarbu, map i... kronikarza, żeby nie zgubił się w puszczy.",
            "Pierwszy cel: Połock nad Dźwiną – twierdza, która zamyka drogę na wschód. Potem Wielkie Łuki. "
            "Z każdą milą od domu rośnie problem: czym nakarmić armię?",
            "Zadanie: zreformować wojsko, zdobyć Połock i rozstrzygnąć kampanię pod Wielkimi Łukami.",
        ],
        "map": {"seed": 1579, "lakes": [], "river": [], "forest": 0.34, "hills": 0.07, "capital": (14, 14),
                "landmarks": [((0, 0), "Psków", "Batory oblegał Psków w latach 1581–1582. Miasta nie zdobył, ale car zgodził się na rozejm w Jamie Zapolskim."),
                              ((0, 0), "Wilno", "W 1579 r. Batory założył tu Akademię Wileńską – dziś Uniwersytet Wileński.")],
                "camps": [((0, 0), "polock", "Twierdza Połock", ["e_strzelcy_ru", "e_piechota_ru", "e_jazda_ru", "e_strzelcy_ru"])]},
        "start_res": {"food": 24, "wood": 24, "stone": 10, "silver": 16},
        "start_deck": ["woje", "woje", "lucznicy", "lucznicy", "konni", "konni"],
        "turns": 30,
        "objectives": [("tech", "wybraniecka"), ("tech", "husaria"), ("build", "koszary", 2), ("camp", "polock"), ("final",)],
        "final": {"name": "Oblężenie Wielkich Łuk (1580)", "enemy_morale": 34, "defense": False, "terrain": "field",
                  "deck": ["e_strzelcy_ru", "e_piechota_ru", "e_jazda_ru", "e_strzelcy_ru", "e_jazda_ru", "e_piechota_ru", "e_strzelcy_ru"],
                  "allies": ["wegrzy", "wegrzy"],
                  "intro": "Drewniane mury Wielkich Łuk. Węgierscy piechurzy Batorego podkładają ogień, armaty biją bez przerwy. Kanclerz Zamoyski czeka na sygnał."},
        "dialogue_start": [("batory", "Kronikarzu, wojnę wygrywa się przed bitwą: drogami, mostami i chlebem dla żołnierzy."),
                           ("zamoyski", "A ja dopilnuję, żeby szlachta zapłaciła podatki na tę wojnę. Co nie będzie łatwe."),
                           ("damian", "Zapiszę to sobie: „Król, który myśli o zaopatrzeniu, to król, który wraca do domu”.")],
        "scripted": {6: ("decision", "Sejm waha się, czy uchwalić podatki na wojnę.",
                         [("Przekonać posłów listami Zamoyskiego (−4 srebra)", {"silver": 10, "food": -4}, "Sejm uchwalił pobór. Skarbiec zadzwonił."),
                          ("Pożyczyć od magnatów", {"silver": 6, "morale": -1}, "Magnaci pożyczyli... ale będą o tym przypominać.")]),
                     12: ("batory", "Połock stoi przed nami. Zbudujmy mosty na Dźwinie i ruszajmy!"),
                     20: ("zamoyski", "Zwiadowcy donoszą: Wielkie Łuki są słabo bronione. To nasza szansa.")},
        "victory": "Zdobyliśmy Połock i Wielkie Łuki, a długie oblężenie Pskowa zmusiło cara do rozmów. W 1582 r. rozejm "
                   "w Jamie Zapolskim oddał Rzeczypospolitej Inflanty i Połock. Notuję: „Batory – król, który zawsze miał plan”.",
    },
    {
        "id": 2, "epoch": 2, "year": "1655–1656", "place": "Jasna Góra i Warka",
        "title": "Rozdział III: Potop",
        "chronicle": [
            "Roku 1655. Z północy nadciąga potop – armia szwedzkiego króla Karola X Gustawa. Wielu magnatów przechodzi na stronę "
            "Szwedów, król Jan Kazimierz ucieka na Śląsk. Wydaje się, że Rzeczpospolita zniknie.",
            "Ale na Jasnej Górze przeor Augustyn Kordecki zamyka bramy i mówi Szwedom: „Nie!”. Oblężenie trwa około czterdziestu dni... "
            "i kończy się klęską oblegających. Cały kraj budzi się do walki.",
            "Hetman Stefan Czarniecki prowadzi wojnę szarpaną: szybkie ataki, zasadzki i znikanie w lasach. Damian prowadzi kronikę "
            "– i czasem musi pisać w siodle.",
            "Zadanie: wesprzeć Jasną Górę, przygotować muszkieterów i rozbić Szwedów pod Warką.",
        ],
        "map": {"seed": 1655, "lakes": [], "river": [], "forest": 0.32, "hills": 0.1, "capital": (14, 14),
                "landmarks": [((0, 0), "Jasna Góra", "Klasztor paulinów w Częstochowie. Obrona z 1655 r. stała się symbolem oporu przeciw potopowi."),
                              ((0, 0), "Warka", "7 kwietnia 1656 r. Czarniecki pokonał tu Szwedów. Polacy zdobyli tabor i wielu jeńców.")],
                "camps": [((0, 0), "czestochowa", "Szwedzi pod Jasną Górą", ["e_muszkieterowie_sv", "e_pikinierzy_sv", "e_armaty_sv", "e_rajtarzy_sv"])]},
        "start_res": {"food": 24, "wood": 22, "stone": 12, "silver": 14},
        "start_deck": ["woje", "lucznicy", "konni", "konni", "husaria", "lucznicy"],
        "turns": 30,
        "objectives": [("tech", "muszkiet"), ("res", "food", 35), ("camp", "czestochowa"), ("final",)],
        "final": {"name": "Bitwa pod Warką (1656)", "enemy_morale": 34, "defense": False, "terrain": "forest",
                  "deck": ["e_rajtarzy_sv", "e_muszkieterowie_sv", "e_pikinierzy_sv", "e_rajtarzy_sv", "e_armaty_sv", "e_muszkieterowie_sv"],
                  "allies": ["mieszczanie"],
                  "intro": "Wiosna 1656. Szwedzki oddział przeprawia się przez Pilicę. Czarniecki uderza, zanim zdążą się ustawić!"},
        "dialogue_start": [("kordecki", "Kronikarzu, mury mamy słabe, ale wiarę mocną. Nie oddamy klasztoru."),
                           ("czarniecki", "Ja nie będę czekał za murami. Uderzę tam, gdzie Szwed się nie spodziewa – i zniknę."),
                           ("damian", "Zapisuję: wojna szarpana. Szwed ma armaty, my mamy lasy, konie i zaskoczenie.")],
        "scripted": {5: ("decision", "Magnat przysyła list: „Przejdź na stronę Szwedów, a zachowasz majątek”.",
                         [("Odrzucić zdradę", {"morale": 2}, "Wiadomość o odmowie rozniosła się po okolicy. Ludzie wierzą w zwycięstwo (+2 morale)."),
                          ("Udawać zgodę, by zyskać na czasie (+8 srebra)", {"silver": 8, "food": -4}, "Szwedzi zapłacili za obietnicę... której nie dotrzymamy.")]),
                     11: ("kordecki", "Szwedzi ustawiają działa pod klasztorem! Pomóżcie nam przerwać oblężenie!"),
                     18: ("czarniecki", "Szwedzki oddział idzie wzdłuż Pilicy. Przygotujcie zasadzkę pod Warką.")},
        "victory": "Jasna Góra się obroniła, a pod Warką Czarniecki rozbił Szwedów. Potop się cofał, a w 1660 r. pokój w Oliwie "
                   "zakończył wojnę. Notuję: „Kraj ocalili ludzie, którzy w najczarniejszej godzinie powiedzieli: nie”.",
    },
    {
        "id": 3, "epoch": 2, "year": "1683", "place": "Wiedeń",
        "title": "Rozdział IV: Skrzydła nad Wiedniem",
        "chronicle": [
            "Roku 1683. Ogromna armia turecka wielkiego wezyra Kara Mustafy oblega Wiedeń, stolicę cesarza. Jeśli miasto padnie, "
            "droga do serca Europy stanie otworem.",
            "Cesarz i papież proszą o pomoc Jana III Sobieskiego – zwycięzcę spod Chocimia. Król wyrusza z Krakowa na czele "
            "husarii, a ja z nim, z kałamarzem przywiązanym do siodła.",
            "Droga jest długa. Armię trzeba wyżywić, konie podkuć, a po drodze uważać na tatarskie czambuły. "
            "12 września ze wzgórza Kahlenberg zobaczymy obóz turecki – tysiące namiotów.",
            "Zadanie: przygotować husarię i zaopatrzenie, rozbić czambuł tatarski i poprowadzić odsiecz Wiednia.",
        ],
        "map": {"seed": 1683, "lakes": [], "river": [], "forest": 0.26, "hills": 0.16, "capital": (14, 14),
                "landmarks": [((0, 0), "Kahlenberg", "Wzgórze nad Wiedniem. Stąd 12 września 1683 r. wojska sprzymierzone ruszyły do ataku."),
                              ((0, 0), "Wiedeń", "Stolica cesarstwa. Po bitwie Sobieski wjechał do miasta witany jak wybawca.")],
                "camps": [((0, 0), "czambul", "Czambuł tatarski", ["e_tatarzy", "e_tatarzy", "e_spahisi", "e_tatarzy"])]},
        "start_res": {"food": 28, "wood": 24, "stone": 12, "silver": 18},
        "start_deck": ["woje", "lucznicy", "konni", "husaria", "muszkieterowie", "dragoni"],
        "turns": 30,
        "objectives": [("tech", "husaria"), ("build", "koszary", 2), ("res", "food", 50), ("camp", "czambul"), ("final",)],
        "final": {"name": "Bitwa pod Wiedniem (12 IX 1683)", "enemy_morale": 46, "defense": False, "terrain": "field",
                  "deck": ["e_janczarzy", "e_spahisi", "e_armaty_tr", "e_tatarzy", "e_janczarzy", "e_spahisi", "e_janczarzy", "e_armaty_tr"],
                  "allies": ["cesarscy", "cesarscy"],
                  "intro": "Popołudnie, 12 września. Ze wzgórz zjeżdża husaria – szum skrzydeł, las kopii. To będzie największa szarża jazdy w dziejach."},
        "dialogue_start": [("sobieski", "Kronikarzu, piszę do mojej Marysieńki co wieczór. Ty pisz kronikę – oboje będziemy mieli co opowiadać."),
                           ("damian", "Najjaśniejszy Panie, armia maszeruje na żołądku. Najpierw zapasy, potem szarża!")],
        "scripted": {6: ("decision", "Cesarscy posłowie proszą: „Szybciej, Wiedeń ledwo się trzyma!”",
                         [("Wymusić marsz (−8 żywności, +6 srebra od cesarza)", {"food": -8, "silver": 6}, "Wojsko maszeruje dzień i noc."),
                          ("Marsz spokojny, zapasy pełne (+6 żywności)", {"food": 6}, "Konie wypoczęte, ale Wiedeń czeka...")]),
                     12: ("sobieski", "Tatarzy grasują na naszych drogach zaopatrzenia. Rozbijcie ich czambuł!"),
                     22: ("sobieski", "Widzę Wiedeń z Kahlenbergu. Jutro uderzamy – niech Bóg nam sprzyja.")},
        "victory": "Husaria przełamała obóz turecki, a Kara Mustafa uciekł, porzucając namioty i skarby. Sobieski napisał do "
                   "papieża: „Przybyliśmy, zobaczyliśmy, a Bóg zwyciężył”. Notuję: „Skrzydła nad Wiedniem – tego Europa nie zapomni”.",
    },
    {
        "id": 4, "epoch": 3, "year": "1768–1772", "place": "Jasna Góra",
        "title": "Rozdział V: Konfederaci",
        "chronicle": [
            "Roku 1768. Rosyjski ambasador rządzi w Warszawie jak u siebie, a sejm uchwala to, co każe caryca Katarzyna. "
            "W miasteczku Bar na Podolu szlachta zawiązuje konfederację: „Za wiarę i wolność!”",
            "Konfederaci nie mają wielkiej armii, ale mają odwagę. Najzdolniejszy z nich to młody Kazimierz Pułaski – "
            "mistrz szybkich rajdów konnych.",
            "W 1770 r. Pułaski zajmuje Jasną Górę i zamienia klasztor w twierdzę. Rosjanie nadciągają z armatami. "
            "Znowu Jasna Góra, znowu oblężenie. Historia lubi się powtarzać – kronikarz też.",
            "Zadanie: umocnić Jasną Górę, zgromadzić zapasy i odeprzeć szturm Rosjan.",
        ],
        "map": {"seed": 1768, "lakes": [], "river": [], "forest": 0.28, "hills": 0.14, "capital": (14, 14),
                "landmarks": [((0, 0), "Bar na Podolu", "Tu 29 lutego 1768 r. zawiązano konfederację barską."),
                              ((0, 0), "Lanckorona", "W 1771 r. konfederaci przegrali tu bitwę z wojskami gen. Suworowa.")],
                "camps": [((0, 0), "garnizon", "Garnizon rosyjski", ["e_grenadierzy", "e_kozacy_rs", "e_strzelcy_rs", "e_grenadierzy"])]},
        "start_res": {"food": 24, "wood": 24, "stone": 12, "silver": 14},
        "start_deck": ["woje", "lucznicy", "konni", "konni", "dragoni", "muszkieterowie"],
        "turns": 18, "siege_turn": 16,
        "objectives": [("tech", "bastiony"), ("build", "palisada", 2), ("res", "food", 30), ("final",)],
        "final": {"name": "Obrona Jasnej Góry (1771)", "enemy_morale": 40, "defense": True, "terrain": "grod",
                  "deck": ["e_grenadierzy", "e_artyleria_rs", "e_kozacy_rs", "e_grenadierzy", "e_strzelcy_rs", "e_artyleria_rs"],
                  "allies": ["mieszczanie", "mieszczanie"],
                  "intro": "Styczeń 1771. Generał Drewicz każe szturmować mury klasztoru. Pułaski krąży po wałach i dodaje obrońcom odwagi."},
        "dialogue_start": [("pulaski", "Kronikarzu, nie mamy wielkiej armii, ale mamy mury i ludzi, którzy wiedzą, o co walczą."),
                           ("damian", "Panie Pułaski, mury trzeba wzmocnić szańcami, a spichlerze napełnić. Oblężenie wygrywa cierpliwość.")],
        "scripted": {5: ("decision", "Francja przysyła oficerów i pieniądze dla konfederatów.",
                         [("Przyjąć oficerów (+8 srebra, +karta Dragoni)", {"silver": 8, "card": "dragoni"}, "Francuscy inżynierowie pomagają budować szańce."),
                          ("Polegać na sobie (+6 drewna)", {"wood": 6}, "Konfederaci tną drzewo na palisady.")]),
                     10: ("pulaski", "Rosjanie zajmują okoliczne wsie. Szturm nastąpi wkrótce!"),
                     14: ("damian", "Do szturmu zostały 2 tury! Wszyscy na mury!")},
        "victory": "Jasna Góra odparła szturm Rosjan. Konfederacja przetrwała jeszcze rok, ale w 1772 r. Rosja, Prusy i Austria "
                   "dokonały pierwszego rozbioru Polski. Notuję z bólem: „Odwaga nie wystarczy, gdy sąsiedzi są silni, a państwo słabe”.",
    },
    {
        "id": 5, "epoch": 3, "year": "1794", "place": "Kraków i Racławice",
        "title": "Rozdział VI: Kosy na sztorc",
        "chronicle": [
            "Roku 1794. Po drugim rozbiorze Rzeczpospolita jest okrojona i zależna od Rosji. Konstytucja 3 maja została obalona. "
            "24 marca na Rynku w Krakowie Tadeusz Kościuszko składa przysięgę: zaczyna się insurekcja.",
            "Kościuszko wie, że szlachta nie wystarczy. Wzywa chłopów – tych, którzy nigdy nie mieli prawa głosu. "
            "Przychodzą z kosami osadzonymi na sztorc.",
            "Pod Racławicami stoją rosyjskie armaty. Kronikarz patrzy na kosynierów w białych sukmanach i myśli: "
            "tego jeszcze w tej kronice nie było.",
            "Zadanie: uzbroić kosynierów, wyżywić wojsko i zwyciężyć pod Racławicami.",
        ],
        "map": {"seed": 1794, "lakes": [], "river": [], "forest": 0.22, "hills": 0.14, "capital": (14, 14),
                "landmarks": [((0, 0), "Rynek krakowski", "Tu 24 marca 1794 r. Kościuszko złożył przysięgę na wierność narodowi."),
                              ((0, 0), "Racławice", "4 kwietnia 1794 r. kosynierzy zdobyli tu rosyjskie armaty. Dziś bitwę upamiętnia Panorama Racławicka.")],
                "camps": [((0, 0), "podjazd", "Podjazd rosyjski", ["e_kozacy_rs", "e_grenadierzy", "e_strzelcy_rs", "e_kozacy_rs"])]},
        "start_res": {"food": 26, "wood": 24, "stone": 10, "silver": 14},
        "start_deck": ["woje", "woje", "lucznicy", "konni", "muszkieterowie", "dragoni"],
        "turns": 30,
        "objectives": [("tech", "kosy"), ("build", "koszary", 2), ("res", "food", 40), ("camp", "podjazd"), ("final",)],
        "final": {"name": "Bitwa pod Racławicami (4 IV 1794)", "enemy_morale": 40, "defense": False, "terrain": "field",
                  "deck": ["e_artyleria_rs", "e_grenadierzy", "e_kozacy_rs", "e_strzelcy_rs", "e_artyleria_rs", "e_grenadierzy", "e_kozacy_rs"],
                  "allies": ["chlopi", "chlopi"],
                  "intro": "Kościuszko w chłopskiej sukmanie wskazuje wzgórze z armatami: „Chłopcy, bierzcie mi te armaty!” Kosynierzy ruszają biegiem."},
        "dialogue_start": [("kosciuszko", "Kronikarzu, ojczyzna to nie tylko szlachta. To każdy, kto chce o nią walczyć."),
                           ("kollataj", "Napiszemy uniwersał, który da chłopom wolność osobistą. Niech wiedzą, za co walczą."),
                           ("glowacki", "Moja kosa jest ostra, panie kronikarzu. Niech no tylko zobaczę te armaty!"),
                           ("damian", "Notuję każde słowo. Ta kronika musi to zapamiętać.")],
        "scripted": {5: ("decision", "Mieszczanie Krakowa oferują srebrne naczynia na rzecz powstania.",
                         [("Przyjąć dar (+10 srebra)", {"silver": 10}, "Mennica bije monety powstańcze."),
                          ("Poprosić o zboże zamiast srebra (+12 żywności)", {"food": 12}, "Wozy z chlebem ruszają do obozu.")]),
                     12: ("kosciuszko", "Korpus generała Tormasowa idzie na Kraków. Spotkamy go pod Racławicami."),
                     20: ("glowacki", "Kosy wyklepane, sukmany założone. Czekamy na rozkaz!")},
        "victory": "Pod Racławicami kosynierzy zdobyli rosyjskie armaty – Bartosz Głowacki zgasił czapką lont jednej z nich. "
                   "Zwycięstwo dało nadzieję, ale jesienią powstanie upadło, a w 1795 r. trzeci rozbiór wymazał Polskę z mapy. "
                   "Notuję: „Państwo można rozebrać. Narodu – nie”.",
    },
    # ---------------------------------------------------------------- dodatkowe
    {
        "id": 6, "epoch": 0, "year": "1520–1521", "place": "Olsztyn", "bonus": True, "after": 0,
        "title": "Rozdział dodatkowy: Astronom na murach",
        "chronicle": [
            "Roku 1520. Wielki mistrz Albrecht Hohenzollern prowadzi ostatnią wojnę Zakonu z Polską. Jego wojska palą Warmię "
            "i podchodzą pod Olsztyn.",
            "Zamkiem zarządza... astronom! Mikołaj Kopernik, kanonik warmiński, odkłada przyrządy do mierzenia gwiazd i bierze się "
            "za mierzenie zapasów prochu i zboża.",
            "Damian pomaga mu liczyć – jedna kreska dla każdego worka mąki, dwie dla każdej beczki prochu. Krzyżacy są coraz bliżej.",
            "Zadanie: umocnić zamek w Olsztynie, zebrać zapasy i odeprzeć szturm.",
        ],
        "map": {"seed": 1520, "lakes": [], "river": [], "forest": 0.32, "hills": 0.06, "capital": (14, 14),
                "landmarks": [((0, 0), "Frombork", "Tu Kopernik spędził większość życia i napisał „O obrotach sfer niebieskich”."),
                              ((0, 0), "Królewiec", "Siedziba Albrechta. Po hołdzie pruskim (1525) stał się stolicą Prus Książęcych.")],
                "camps": [((0, 0), "zakonni", "Obóz wojsk Zakonu", ["e_knechci", "e_zaciezni_z", "e_kusznicy_z", "e_rycerze_z"])]},
        "start_res": {"food": 22, "wood": 22, "stone": 8, "silver": 12},
        "start_deck": ["woje", "woje", "lucznicy", "lucznicy", "konni", "konni"],
        "turns": 18, "siege_turn": 15,
        "objectives": [("tech", "armaty"), ("build", "palisada", 2), ("res", "food", 30), ("final",)],
        "final": {"name": "Obrona Olsztyna (1521)", "enemy_morale": 36, "defense": True, "terrain": "grod",
                  "deck": ["e_knechci", "e_zaciezni_z", "e_kusznicy_z", "e_rycerze_z", "e_knechci", "e_zaciezni_z"],
                  "allies": ["mieszczanie", "mieszczanie"],
                  "intro": "Styczeń 1521. Krzyżacy podchodzą pod mury z drabinami. Kopernik patrzy na nich z wieży – tak jak patrzył na gwiazdy: spokojnie i dokładnie."},
        "dialogue_start": [("kopernik", "Kronikarzu, policzmy wszystko: ludzi, proch, zboże. Liczby nie kłamią – tak jak gwiazdy."),
                           ("damian", "Doktorze Mikołaju, a czy gwiazdy powiedzą nam, kiedy przyjdą Krzyżacy?"),
                           ("kopernik", "Gwiazdy nie. Ale zwiadowcy – owszem.")],
        "scripted": {6: ("decision", "Król Zygmunt Stary pyta, czy przysłać posiłki do Olsztyna.",
                         [("Poprosić o żołnierzy (+karta: Piechota łanowa)", {"card": "woje"}, "Przybył oddział piechoty."),
                          ("Poprosić o proch i zboże (+8 żywności, +4 kamienia)", {"food": 8, "stone": 4}, "Wozy z zapasami wjechały na zamek.")]),
                     13: ("damian", "Krzyżacy pod miastem! Do szturmu zostały 2 tury!")},
        "victory": "Olsztyn się obronił. Wojna wkrótce się skończyła, a w 1525 r. Albrecht złożył na Rynku w Krakowie hołd "
                   "królowi Zygmuntowi Staremu. Zakon w Prusach przestał istnieć. Notuję: „Astronom obronił zamek – czego to ludzie nie potrafią!”",
    },
    {
        "id": 7, "epoch": 1, "year": "1610", "place": "Kłuszyn", "bonus": True, "after": 1,
        "title": "Rozdział dodatkowy: Husaria pod Kłuszynem",
        "chronicle": [
            "Roku 1610. Wojska Zygmunta III Wazy oblegają Smoleńsk. Na odsiecz idzie wielka armia moskiewska z zaciężnymi "
            "żołnierzami ze Szwecji, Francji i Szkocji.",
            "Hetman Stanisław Żółkiewski ma kilka razy mniej ludzi. Postanawia zaatakować pierwszy – nocnym marszem przez las.",
            "Damian jedzie obok husarzy. Skrzydła szumią na wietrze, a hetman spokojnie wydaje rozkazy. Pod wioską Kłuszyn "
            "zaczyna świtać...",
            "Zadanie: przygotować husarię, zdobyć szańce pod Carowem-Zajmiszczem i wygrać bitwę pod Kłuszynem.",
        ],
        "map": {"seed": 1610, "lakes": [], "river": [], "forest": 0.36, "hills": 0.06, "capital": (14, 14),
                "landmarks": [((0, 0), "Smoleńsk", "Twierdza oblegana przez Zygmunta III. Poddała się w 1611 r."),
                              ((0, 0), "Kreml", "Po Kłuszynie Polacy weszli do Moskwy i stacjonowali na Kremlu do 1612 r.")],
                "camps": [((0, 0), "carowo", "Szańce pod Carowem", ["e_strzelcy_ru", "e_piechota_ru", "e_strzelcy_ru", "e_jazda_ru"])]},
        "start_res": {"food": 24, "wood": 22, "stone": 10, "silver": 14},
        "start_deck": ["woje", "lucznicy", "konni", "konni", "husaria", "wybraniecka"],
        "turns": 26,
        "objectives": [("tech", "husaria"), ("build", "koszary", 2), ("res", "silver", 35), ("camp", "carowo"), ("final",)],
        "final": {"name": "Bitwa pod Kłuszynem (4 VII 1610)", "enemy_morale": 42, "defense": False, "terrain": "field",
                  "deck": ["e_jazda_ru", "e_strzelcy_ru", "e_piechota_ru", "e_muszkieterowie_sv", "e_rajtarzy_sv", "e_jazda_ru", "e_strzelcy_ru"],
                  "allies": [],
                  "intro": "Świt 4 lipca. Husaria szarżuje raz po raz – niektóre chorągwie nawet po osiem, dziesięć razy. Płoty na polu utrudniają atak..."},
        "dialogue_start": [("zolkiewski", "Kronikarzu, nie liczy się, ilu ich jest. Liczy się, kto uderzy pierwszy i kto wytrwa dłużej."),
                           ("damian", "Panie hetmanie, zapisuję: odwaga plus dobre zaopatrzenie. W tej kolejności czy odwrotnie?")],
        "scripted": {7: ("decision", "Zaciężni cudzoziemcy z armii wroga przysyłają posła: chcą negocjować.",
                         [("Obiecać im żołd (−8 srebra)", {"silver": -8, "morale": 3}, "Część najemników nie stanie do walki (+3 morale)."),
                          ("Nie negocjować", {"wood": 4}, "Hetman wzrusza ramionami: „Pokonamy wszystkich”.")]),
                     16: ("zolkiewski", "Nocny marsz przez las. O świcie uderzamy pod Kłuszynem.")},
        "victory": "Pod Kłuszynem husaria rozbiła kilkakrotnie liczniejszą armię. Część cudzoziemskich najemników przeszła na "
                   "stronę Polaków. Notuję: „Żółkiewski pokazał, że mistrzostwo wygrywa z liczbą”.",
    },
    {
        "id": 8, "epoch": 3, "year": "1788–1792", "place": "Warszawa", "bonus": True, "after": 4,
        "title": "Rozdział dodatkowy: Konstytucja 3 maja",
        "chronicle": [
            "Roku 1788. Po pierwszym rozbiorze przyszedł czas na naprawę państwa. W Warszawie zbiera się Sejm Wielki, "
            "zwany Czteroletnim, bo obraduje aż do 1792 r.",
            "Król Stanisław August, ksiądz Hugo Kołłątaj i ich przyjaciele piszą w tajemnicy nową ustawę zasadniczą. "
            "Damian dyskretnie przynosi atrament.",
            "3 maja 1791 r. posłowie przyjmują Konstytucję. Znosi liberum veto i wolną elekcję, wzmacnia miasta i bierze chłopów "
            "pod opiekę prawa. Ale przeciwnicy już szukają pomocy w Petersburgu...",
            "Zadanie: zbudować szkoły i drukarnie, napełnić skarbiec, uchwalić Konstytucję i przeciwstawić się targowiczanom.",
        ],
        "map": {"seed": 1791, "lakes": [], "river": [], "forest": 0.2, "hills": 0.06, "capital": (14, 14),
                "landmarks": [((0, 0), "Zamek Królewski", "W Sali Senatorskiej Zamku Królewskiego uchwalono Konstytucję 3 maja."),
                              ((0, 0), "Łazienki Królewskie", "Letnia rezydencja Stanisława Augusta, perła klasycyzmu.")],
                "camps": [((0, 0), "targowica", "Konfederaci targowiccy", ["e_konfederaci", "e_kozacy_rs", "e_grenadierzy", "e_konfederaci"])]},
        "start_res": {"food": 26, "wood": 24, "stone": 12, "silver": 18},
        "start_deck": ["woje", "lucznicy", "konni", "muszkieterowie", "dragoni", "husaria"],
        "turns": 26,
        "objectives": [("tech", "ken"), ("tech", "konstytucja"), ("build", "kosciol", 2), ("res", "silver", 50), ("camp", "targowica")],
        "final": None,
        "dialogue_start": [("poniatowski", "Kronikarzu, państwo jest jak zegar: jeśli jedno kółko się zatnie, staje cały mechanizm. Naprawmy go."),
                           ("kollataj", "Bez szkół i podatków żadna konstytucja nie przetrwa. Zacznijmy od edukacji."),
                           ("damian", "A ja zapiszę każdy artykuł. Ładnym pismem – to ważny dokument!")],
        "scripted": {6: ("decision", "Szlachta pyta, czy mieszczanie mają dostać prawo kupowania ziemi i wstępu do urzędów.",
                         [("Tak – wzmocnić miasta (+10 srebra)", {"silver": 10}, "Prawo o miastach uchwalono. Kupcy wiwatują."),
                          ("Nie – zostawić stare zwyczaje (+4 żywności)", {"food": 4}, "Szlachta zadowolona, miasta rozczarowane.")]),
                     14: ("poniatowski", "Przeciwnicy Konstytucji zawiązali konfederację w Targowicy i wezwali Rosjan!")},
        "victory": "Konstytucję 3 maja uchwalono i Polacy świętują ten dzień do dziś. Targowica i rosyjska interwencja obaliły ją "
                   "po roku, ale pamięć o niej przetrwała rozbiory. Notuję: „Dobre prawo jest jak ziarno – wyrośnie, nawet jeśli długo czeka”.",
    },
]

ENDING = [
    "Tak kończy się druga kronika Damiana Ścisła – kronika Rzeczypospolitej.",
    "Od wojny trzynastoletniej i złotego wieku, przez husarię pod Kłuszynem i Wiedniem, potop i konfederacje, "
    "aż po Konstytucję 3 maja i kosy Racławic – przeszliśmy prawie trzysta pięćdziesiąt lat.",
    "W 1795 roku Rzeczpospolita zniknęła z mapy Europy. Ale już w 1797 roku legioniści we Włoszech zaśpiewali: "
    "„Jeszcze Polska nie zginęła, kiedy my żyjemy”.",
    "Damian zamyka kronikę, poprawia fioletowy kaptur i patrzy w przyszłość. Ta historia jeszcze się nie skończyła...",
]

# ---------------------------------------------------------------- TAKTYKI I DOWÓDCY
TACTICS = {
    "wykup": {"name": "Żołd dla zaciężnych", "effect": "reinforce", "desc": "Dobierasz 2 dodatkowe karty.",
              "fact": "W wojnie trzynastoletniej obie strony walczyły głównie wojskami zaciężnymi – i ciągle brakowało im pieniędzy."},
    "tabor_dunina": {"name": "Tabor Dunina", "effect": "wagons", "desc": "W tej rundzie blokujesz 5 obrażeń.",
                     "fact": "Pod Świecinem Piotr Dunin ustawił tabor, o który rozbiły się ataki rycerzy Zakonu."},
    "wegrzy_szturm": {"name": "Szturm piechoty węgierskiej", "effect": "ambush", "desc": "W tej rundzie nasza karta +3.",
                      "fact": "Batory sprowadził doborową piechotę węgierską, która podpalała drewniane mury twierdz."},
    "kule_zarowe": {"name": "Kule żarowe", "effect": "volley", "desc": "Wróg −3 morale, a nasi strzelcy +2.",
                    "fact": "Batory kazał strzelać kulami żarowymi – rozgrzanymi do czerwoności – które podpalały drewniane mury moskiewskich twierdz."},
    "partyzantka": {"name": "Wojna szarpana", "effect": "ambush", "desc": "W tej rundzie nasza karta +3.",
                    "fact": "Czarniecki atakował Szwedów z zaskoczenia i znikał, zanim zdążyli się ustawić do bitwy."},
    "przeprawa": {"name": "Atak na przeprawie", "effect": "retreat", "desc": "Wróg w nieładzie: jego karta −4.",
                  "fact": "Pod Warką Szwedzi zostali zaatakowani podczas przeprawy przez Pilicę."},
    "szarza": {"name": "Szarża husarii", "effect": "hymn", "desc": "Morale +4, a nasza karta w tej rundzie +2.",
               "fact": "Pod Wiedniem ruszyło do szarży około 20 tysięcy jeźdźców – jedna z największych szarż w historii."},
    "kahlenberg": {"name": "Uderzenie z Kahlenbergu", "effect": "fog", "desc": "Wróg traci przewagę typu, a my +1.",
                   "fact": "Turcy nie spodziewali się, że sprzymierzeni zejdą prosto ze stromych, zalesionych wzgórz."},
    "mury_klasztoru": {"name": "Ogień z murów", "effect": "volley", "desc": "Wróg −3 morale, a nasi strzelcy +2.",
                       "fact": "Obrońcy Jasnej Góry w 1771 r. odpierali szturmy ogniem z murów i bastionów."},
    "wypad": {"name": "Nocny wypad", "effect": "sortie", "desc": "Wróg traci od razu 5 morale.",
              "fact": "Pułaski słynął z błyskawicznych rajdów konnych i nocnych ataków."},
    "kosy_na_armaty": {"name": "Kosynierzy na armaty!", "effect": "fog", "desc": "Wróg traci przewagę typu, a my +1.",
                       "fact": "Pod Racławicami kosynierzy biegiem dopadli armat, zanim artylerzyści zdążyli je przeładować."},
    "przysiega": {"name": "Przysięga Kościuszki", "effect": "hymn", "desc": "Morale +4, a nasza karta w tej rundzie +2.",
                  "fact": "„Ja, Tadeusz Kościuszko, przysięgam w obliczu Boga całemu narodowi polskiemu...” – Kraków, 24 marca 1794."},
    "wycieczka": {"name": "Wycieczka z zamku", "effect": "sortie", "desc": "Wróg traci od razu 5 morale.",
                  "fact": "Obrońcy zamków robili wypady, by palić drabiny i machiny oblężnicze wroga."},
    "proch_kopernika": {"name": "Zapasy policzone", "effect": "wagons", "desc": "W tej rundzie blokujesz 5 obrażeń.",
                        "fact": "Kopernik sporządził dokładne spisy zapasów i uzbrojenia zamku w Olsztynie."},
    "las": {"name": "Nocny marsz przez las", "effect": "fog", "desc": "Wróg traci przewagę typu, a my +1.",
            "fact": "Żółkiewski zaskoczył wroga, maszerując nocą przez las pod Kłuszyn."},
    "najemnicy": {"name": "Najemnicy zmieniają stronę", "effect": "retreat", "desc": "Wróg słabnie: jego karta −4.",
                  "fact": "Pod Kłuszynem część cudzoziemskich najemników armii wroga przestała walczyć i przeszła do Polaków."},
    "sejm": {"name": "Uchwała sejmu", "effect": "reinforce", "desc": "Dobierasz 2 dodatkowe karty.",
             "fact": "Sejm Czteroletni uchwalił powiększenie armii do 100 tysięcy żołnierzy – choć nigdy jej tak nie rozbudowano."},
}

COMMANDERS = {
    0: {"who": "kazimierz_j", "desc": "Piechota +1", "type_bonus": {"piechota": 1}, "morale": 0, "tactics": ["wykup", "tabor_dunina"]},
    1: {"who": "batory", "desc": "Piechota +1, jazda +1", "type_bonus": {"piechota": 1, "jazda": 1}, "morale": 0, "tactics": ["wegrzy_szturm", "kule_zarowe"]},
    2: {"who": "czarniecki", "desc": "Jazda +2", "type_bonus": {"jazda": 2}, "morale": 0, "tactics": ["partyzantka", "przeprawa"]},
    3: {"who": "sobieski", "desc": "Jazda +2, morale +3", "type_bonus": {"jazda": 2}, "morale": 3, "tactics": ["szarza", "kahlenberg"]},
    4: {"who": "pulaski", "desc": "Strzelcy +1, morale +2", "type_bonus": {"lucznicy": 1}, "morale": 2, "tactics": ["mury_klasztoru", "wypad"]},
    5: {"who": "kosciuszko", "desc": "Piechota +2", "type_bonus": {"piechota": 2}, "morale": 0, "tactics": ["kosy_na_armaty", "przysiega"]},
    6: {"who": "kopernik", "desc": "Strzelcy +1, morale +2", "type_bonus": {"lucznicy": 1}, "morale": 2, "tactics": ["wycieczka", "proch_kopernika"]},
    7: {"who": "zolkiewski", "desc": "Jazda +2", "type_bonus": {"jazda": 2}, "morale": 0, "tactics": ["las", "najemnicy"]},
    8: {"who": "poniatowski", "desc": "Morale +3", "type_bonus": {}, "morale": 3, "tactics": ["sejm", "przysiega"]},
}

RAIDS = {
    0: {"start": 7, "every": 7, "name": "Rajd zaciężnych Zakonu", "faction": "tz", "unit": "knight_t", "deck": ["e_zaciezni_z", "e_kusznicy_z", "e_rycerze_z"]},
    1: {"start": 6, "every": 6, "name": "Podjazd moskiewski", "faction": "ru", "unit": "horse", "deck": ["e_jazda_ru", "e_strzelcy_ru", "e_jazda_ru"]},
    2: {"start": 5, "every": 5, "name": "Rajtarzy szwedzcy", "faction": "sv", "unit": "horse", "deck": ["e_rajtarzy_sv", "e_muszkieterowie_sv", "e_rajtarzy_sv"]},
    3: {"start": 5, "every": 5, "name": "Czambuł tatarski", "faction": "mg", "unit": "horse_mg", "deck": ["e_tatarzy", "e_tatarzy", "e_spahisi"]},
    4: {"start": 5, "every": 4, "name": "Oddział rosyjski", "faction": "rs", "unit": "musket", "deck": ["e_grenadierzy", "e_kozacy_rs", "e_strzelcy_rs"]},
    5: {"start": 6, "every": 6, "name": "Podjazd kozaków dońskich", "faction": "rs", "unit": "horse", "deck": ["e_kozacy_rs", "e_kozacy_rs", "e_strzelcy_rs"]},
    6: {"start": 5, "every": 4, "name": "Rajd krzyżacki", "faction": "tz", "unit": "knight_t", "deck": ["e_knechci", "e_kusznicy_z", "e_rycerze_z"]},
    7: {"start": 6, "every": 6, "name": "Podjazd moskiewski", "faction": "ru", "unit": "horse", "deck": ["e_jazda_ru", "e_strzelcy_ru", "e_piechota_ru"]},
    8: {"start": 8, "every": 7, "name": "Zbrojni targowiczanie", "faction": "en", "unit": "horse", "deck": ["e_konfederaci", "e_kozacy_rs", "e_konfederaci"]},
}

CHRONO = [0, 6, 1, 7, 2, 3, 4, 8, 5]   # kolejność chronologiczna na ekranie kampanii
MAIN = [0, 1, 2, 3, 4, 5]

# ---------------------------------------------------------------- GEOGRAFIA MAP
def geo(e, s):
    """(wschód, południe) w zakresie -1..1 → współrzędne kafla mapy 30x30."""
    sx, sy = e * 0.92, 1 + s * 0.92
    x = round(29 * (sy + sx) / 2)
    y = round(29 * (sy - sx) / 2)
    return (max(0, min(29, x)), max(0, min(29, y)))


GEOGRAPHY = {
    0: {"capital": (-.35, .15), "river": [(0, 1), (-.05, .4), (.05, -.2), (-.1, -.6), (-.25, -1)],
        "river2": [(.03, -.3), (.4, -.6), (.6, -1)], "lakes": [(.6, .45, 1)],
        "landmarks": [(-.1, .85), (-.4, -.85)], "camps": [(.45, -.6)],
        "labels": [((.12, .3), "Wisła"), ((.52, -.78), "Nogat")]},
    6: {"capital": (-.14, .05), "river": [(.1, 1), (0, .3), (.06, -.3), (-.05, -1)],
        "lakes": [(-.5, .3, 2), (.5, .5, 2), (-.42, -.5, 1), (.58, -.3, 1)],
        "landmarks": [(-.6, -.85), (.32, -.92)], "camps": [(.45, -.6)],
        "labels": [((.14, .62), "Łyna")]},
    1: {"capital": (-.3, .3), "river": [(-1, -.15), (-.3, -.25), (.3, -.1), (1, -.3)],
        "lakes": [(.5, .5, 2), (-.6, -.7, 1)], "landmarks": [(.6, -.8), (-.8, .6)], "camps": [(.35, -.32)],
        "labels": [((-.55, -.35), "Dźwina")]},
    7: {"capital": (-.6, .2), "river": [(-1, .75), (0, .62), (1, .78)], "lakes": [(.3, .35, 1)],
        "landmarks": [(-.85, -.6), (.85, .2)], "camps": [(.12, -.3)], "labels": []},
    2: {"capital": (0, -.12), "river": [(-1, .35), (-.3, .25), (.3, .38), (.66, .3)],
        "river2": [(.75, -1), (.68, 0), (.72, 1)], "lakes": [],
        "landmarks": [(-.75, .72), (.42, .22)], "camps": [(-.62, .52)],
        "labels": [((-.42, .16), "Pilica"), ((.84, -.5), "Wisła")]},
    3: {"capital": (-.55, .12), "river": [(-1, -.55), (-.2, -.42), (.4, -.2), (1, -.35)], "lakes": [],
        "landmarks": [(-.4, -.15), (.42, 0)], "camps": [(.7, .6)],
        "labels": [((-.5, -.62), "Dunaj")]},
    4: {"capital": (.12, .05), "river": [(-.2, 1), (-.1, .3), (.05, -.3), (0, -1)], "lakes": [(.55, -.4, 1)],
        "landmarks": [(.85, .75), (.4, .85)], "camps": [(-.7, -.6)],
        "labels": [((-.05, -.55), "Warta")]},
    8: {"capital": (-.06, -.04), "river": [(.2, 1), (.1, .3), (.2, -.3), (.1, -1)], "lakes": [],
        "landmarks": [(-.15, -.22), (-.06, .42)], "camps": [(.8, .8)],
        "labels": [((.3, -.55), "Wisła")]},
    5: {"capital": (0, .42), "river": [(-1, .6), (-.3, .56), (.1, .72), (1, .66)], "lakes": [],
        "landmarks": [(.12, .3), (.05, -.55)], "camps": [(.75, -.5)],
        "labels": [((-.55, .5), "Wisła")]},
}


def _apply_geography():
    for idx, g in GEOGRAPHY.items():
        m = CHAPTERS[idx]["map"]
        m["capital"] = geo(*g["capital"])
        m["river"] = [geo(*p) for p in g["river"]]
        if g.get("river2"):
            m["river2"] = [geo(*p) for p in g["river2"]]
        m["lakes"] = [geo(e, s) + (r,) for (e, s, r) in g["lakes"]]
        m["labels"] = [(geo(*p), t) for p, t in g["labels"]]
        m["landmarks"] = [(geo(*p),) + tuple(l[1:]) for p, l in zip(g["landmarks"], m["landmarks"])]
        m["camps"] = [(geo(*p),) + tuple(c[1:]) for p, c in zip(g["camps"], m["camps"])]


_apply_geography()

# ---------------------------------------------------------------- ENCYKLOPEDIA: POJĘCIA
GLOSSARY = {
    "szlachta": ("Szlachta", "Stan uprzywilejowany: posiadał ziemię, wybierał posłów na sejm i – od 1573 r. – króla."),
    "folwark": ("Folwark", "Gospodarstwo szlacheckie nastawione na produkcję zboża na sprzedaż, oparte na pańszczyźnie."),
    "panszczyzna": ("Pańszczyzna", "Darmowa praca chłopa na ziemi pana. W XVI–XVIII w. rosła nawet do kilku dni w tygodniu."),
    "flisak": ("Flisak", "Człowiek spławiający zboże i drewno Wisłą do Gdańska na szkutach i tratwach."),
    "sejm": ("Sejm walny", "Zgromadzenie króla, senatu i izby poselskiej. Uchwalał podatki i prawa."),
    "nihil_novi": ("Nihil novi", "Konstytucja z 1505 r.: „nic nowego” w prawie bez zgody senatu i posłów."),
    "renesans": ("Renesans", "Odrodzenie zainteresowania kulturą starożytną. W Polsce jego symbolem jest Kaplica Zygmuntowska."),
    "reformacja": ("Reformacja", "Ruch odnowy Kościoła w XVI w. Powstały wtedy Kościoły protestanckie."),
    "tolerancja": ("Tolerancja", "Szacunek dla innych wyznań. Konfederacja warszawska (1573) gwarantowała pokój religijny."),
    "elekcja": ("Wolna elekcja", "Wybór króla przez szlachtę. Pierwsza odbyła się w 1573 r."),
    "pacta": ("Pacta conventa", "Osobiste zobowiązania króla elekcyjnego wobec szlachty."),
    "husaria": ("Husaria", "Ciężka jazda z długimi kopiami, słynąca ze skrzydeł i miażdżących szarż."),
    "hetman": ("Hetman", "Najwyższy dowódca wojska: hetman wielki i jego zastępca – hetman polny."),
    "unia_lubelska": ("Unia lubelska", "Umowa z 1569 r., która z Korony i Litwy utworzyła Rzeczpospolitą Obojga Narodów."),
    "bastion": ("Bastion", "Wysunięta część muru twierdzy w kształcie grotu, z której ostrzeliwano wroga z boku."),
    "barok": ("Barok", "Styl XVII w.: złocenia, kopuły, dramatyczne rzeźby. Przykład – pałac w Wilanowie."),
    "liberum_veto": ("Liberum veto", "Prawo jednego posła do zerwania sejmu. Paraliżowało państwo od 1652 r."),
    "sarmatyzm": ("Sarmatyzm", "Przekonanie szlachty, że pochodzi od starożytnych Sarmatów, i związany z tym styl życia."),
    "konfederacja": ("Konfederacja", "Związek szlachty zawiązany w określonym celu, np. konfederacja barska (1768)."),
    "rozbiory": ("Rozbiory", "Podział ziem Rzeczypospolitej przez Rosję, Prusy i Austrię w latach 1772, 1793 i 1795."),
    "klasycyzm": ("Klasycyzm", "Styl XVIII w. wzorowany na antyku: kolumny, trójkątne frontony, prostota. Przykład – Łazienki."),
    "oswiecenie": ("Oświecenie", "Epoka wiary w rozum, naukę i edukację. W Polsce – KEN, Konstytucja 3 maja, „Monitor”."),
    "manufaktura": ("Manufaktura", "Duży zakład z ręczną pracą i podziałem zadań między wielu robotników."),
    "insurekcja": ("Insurekcja", "Powstanie zbrojne. Insurekcja kościuszkowska wybuchła w 1794 r."),
    "kosynier": ("Kosynier", "Chłop-żołnierz uzbrojony w kosę osadzoną pionowo na drzewcu."),
    "popyt": ("Popyt i podaż", "Gdy towaru jest mało, a chętnych wielu – cena rośnie. Gdy towaru dużo – spada."),
    "pieniadz": ("Prawo Kopernika", "„Zły pieniądz wypiera z obiegu lepszy” – ludzie chowają dobre monety, a płacą gorszymi."),
}

CHAPTER_TERMS = {
    0: ["szlachta", "sejm", "nihil_novi", "popyt", "flisak"],
    6: ["renesans", "folwark", "panszczyzna", "pieniadz"],
    1: ["elekcja", "pacta", "unia_lubelska", "hetman", "bastion", "tolerancja"],
    7: ["husaria", "hetman", "reformacja"],
    2: ["barok", "liberum_veto", "sarmatyzm"],
    3: ["husaria", "barok", "sarmatyzm"],
    4: ["konfederacja", "rozbiory", "oswiecenie"],
    8: ["klasycyzm", "oswiecenie", "manufaktura"],
    5: ["insurekcja", "kosynier", "rozbiory"],
}

# ---------------------------------------------------------------- PRZERYWNIKI FILMOWE (Blender)
CUTSCENES = {
    0: [("cut_swiecino_1", "Wrzesień 1462. Pod Świecinem Piotr Dunin ustawia wozy taboru. Rycerze Zakonu jeszcze nie wiedzą, "
                           "że ich szarża rozbije się o tę drewnianą ścianę.")],
    1: [("cut_luki_1", "Rok 1580. Drewniane mury Wielkich Łuk płoną od kul żarowych. Węgierscy piechurzy czekają na znak króla.")],
    2: [("cut_warka_1", "Kwiecień 1656. Szwedzi przeprawiają się przez Pilicę, nie wiedząc, że w lesie czeka Czarniecki.")],
    3: [("cut_wieden_1", "12 września 1683. Ze wzgórz pod Wiedniem zjeżdża husaria. Szum skrzydeł, las kopii, a przed nimi – tysiące namiotów."),
        ("cut_wieden_2", "„Przybyliśmy, zobaczyliśmy, a Bóg zwyciężył” – napisze wieczorem król Jan III Sobieski.")],
    4: [("cut_jasna_1", "Zima 1771. Rosyjskie działa ustawione pod Jasną Górą. Na wałach klasztoru konfederaci Pułaskiego.")],
    5: [("cut_raclawice_1", "4 kwietnia 1794. „Chłopcy, bierzcie mi te armaty!” Kosynierzy w białych sukmanach ruszają pod górę.")],
    6: [("cut_olsztyn_1", "Styczeń 1521. Zamek w Olsztynie, śnieg na wałach. Na wieży stoi Mikołaj Kopernik i liczy chorągwie wroga.")],
    7: [("cut_kluszyn_1", "Świt 4 lipca 1610. Husaria Żółkiewskiego rusza do szarży przez pola pod Kłuszynem.")],
}
