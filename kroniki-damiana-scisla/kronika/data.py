# -*- coding: utf-8 -*-
"""Treść gry: epoki, rozdziały, technologie, postacie, pytania, zdarzenia."""

EPOCHS = [
    {"id": 0, "name": "Epoka Plemienna", "years": "X wiek", "color": (120, 150, 70)},
    {"id": 1, "name": "Epoka Piastowska", "years": "XI–XIII wiek", "color": (170, 60, 50)},
    {"id": 2, "name": "Epoka Zamków", "years": "XIV wiek", "color": (110, 110, 130)},
    {"id": 3, "name": "Epoka Jagiellońska", "years": "XIV–XV wiek", "color": (150, 110, 40)},
]

RES_NAMES = {"food": "Żywność", "wood": "Drewno", "stone": "Kamień", "silver": "Srebro"}
RES_ORDER = ["food", "wood", "stone", "silver"]

# ---------------------------------------------------------------- BUDYNKI
# terrain: na jakich kaflach można budować; prod: produkcja na turę
BUILDINGS = {
    "pole": {"name": "Pole uprawne", "cost": {"wood": 4}, "terrain": ["grass", "field"],
             "prod": {"food": 2}, "desc": "Zboże i rzepa. Pełny spichlerz = spokojny książę."},
    "drwal": {"name": "Obóz drwali", "cost": {"food": 3}, "terrain": ["forest"],
              "prod": {"wood": 2}, "desc": "Stawiaj w lesie. Puszcza daje drewno na grody i łodzie."},
    "kamieniolom": {"name": "Kamieniołom", "cost": {"wood": 5, "food": 2}, "terrain": ["hills"],
                    "prod": {"stone": 2}, "desc": "Stawiaj na wzgórzach. Kamień na mury i kościoły."},
    "targ": {"name": "Targ", "cost": {"wood": 6, "stone": 2}, "terrain": ["grass", "field", "road"],
             "prod": {"silver": 2}, "desc": "Kupcy płacą myto i opłaty targowe. Handel to krew księstwa."},
    "koszary": {"name": "Dwór drużyny", "cost": {"wood": 6, "food": 4}, "terrain": ["grass", "field", "road"],
                "prod": {}, "desc": "Pozwala werbować wojów (1 werbunek na turę za każdy dwór)."},
    "palisada": {"name": "Palisada", "cost": {"wood": 8}, "terrain": ["grass", "field", "road", "hills"],
                 "prod": {}, "defense": 3, "req": "grod_walowy",
                 "desc": "Wał z ostrych pali: +3 do morale w obronie."},
    "kosciol": {"name": "Kościół i szkoła", "cost": {"wood": 6, "stone": 6}, "terrain": ["grass", "field", "road", "hills"],
                "prod": {"silver": 1}, "req": "pismo",
                "desc": "Mnisi znają pismo: w zagadkach usuwają jedną błędną odpowiedź."},
    "mlyn": {"name": "Młyn wodny", "cost": {"wood": 8, "stone": 2}, "terrain": ["grass", "field", "marsh"],
             "prod": {"food": 4}, "req": "mlyn", "near_water": True,
             "desc": "Musi stać przy wodzie. Koło kręci się, mąka się sypie."},
    "zupa": {"name": "Żupa solna", "cost": {"wood": 8, "stone": 4}, "terrain": ["hills"],
             "prod": {"silver": 4}, "req": "zupy", "desc": "Białe złoto spod ziemi! Sól to fortuna."},
    "zamek": {"name": "Zamek murowany", "cost": {"stone": 16, "wood": 6, "silver": 6},
              "terrain": ["grass", "field", "hills"], "prod": {}, "defense": 6, "req": "mury",
              "radius": 4, "desc": "Kamienna twierdza: +6 do morale w obronie, szerokie granice."},
}

# ---------------------------------------------------------------- KARTY BITEWNE
# type: piechota > jazda > łucznicy > piechota ; "spec" – bez przewag
CARD_TYPES = {
    "piechota": {"name": "Piechota", "beats": "jazda", "color": (150, 60, 50)},
    "jazda": {"name": "Jazda", "beats": "lucznicy", "color": (60, 90, 150)},
    "lucznicy": {"name": "Strzelcy", "beats": "piechota", "color": (70, 120, 60)},
    "spec": {"name": "Specjalna", "beats": None, "color": (130, 100, 40)},
}

CARDS = {
    # karty gracza
    "woje": {"name": "Woje z oszczepami", "type": "piechota", "power": 3, "unit": "spear", "faction": "pl",
             "cost": {"food": 3, "wood": 1}, "desc": "Chłopi z okolicznych wsi. Twardzi jak dębowe korzenie."},
    "lucznicy": {"name": "Łucznicy", "type": "lucznicy", "power": 3, "unit": "bow", "faction": "pl",
                 "cost": {"food": 2, "wood": 3}, "desc": "Strzała z cisowego łuku leci dalej niż plotka."},
    "konni": {"name": "Konni wojowie", "type": "jazda", "power": 4, "unit": "horse", "faction": "pl",
              "cost": {"food": 4, "silver": 3}, "desc": "Szybcy jak wiatr nad Gopłem."},
    "druzyna": {"name": "Drużyna książęca", "type": "piechota", "power": 6, "unit": "sword", "faction": "pl",
                "cost": {"food": 4, "silver": 5}, "req": "druzyna",
                "desc": "Pancerni wojowie księcia. Utrzymywani z jego skarbca."},
    "kusznicy": {"name": "Kusznicy", "type": "lucznicy", "power": 6, "unit": "xbow", "faction": "pl",
                 "cost": {"wood": 4, "silver": 4}, "req": "kusza", "desc": "Bełt przebija kolczugę."},
    "rycerze": {"name": "Rycerstwo", "type": "jazda", "power": 8, "unit": "knight", "faction": "pl",
                "cost": {"food": 5, "silver": 8}, "req": "rycerze", "desc": "Kopia, koń i herb na tarczy."},
    "bombarda": {"name": "Bombarda", "type": "spec", "power": 9, "unit": "cannon", "faction": "pl",
                 "cost": {"stone": 6, "silver": 8}, "req": "bombarda", "desc": "Huk! Dym! ...i trochę strachu."},
    "tabor": {"name": "Tabor wozów", "type": "spec", "power": 4, "unit": "wagon", "faction": "pl", "shield": 4,
              "cost": {"wood": 8, "food": 3}, "req": "tabor",
              "desc": "Wozy w krąg. Blokuje 4 punkty obrażeń."},
    "litwini": {"name": "Chorągiew litewska", "type": "jazda", "power": 7, "unit": "horse_lt", "faction": "lt",
                "cost": {"food": 4, "silver": 4}, "req": "dyplomacja", "desc": "Lekka jazda Witolda – mistrzowie podstępu."},
    "zaciezni": {"name": "Zaciężni", "type": "piechota", "power": 7, "unit": "pike", "faction": "pl",
                 "cost": {"silver": 9}, "req": "zaciezni", "desc": "Walczą za żołd. Płacisz – masz armię."},
    "czesi": {"name": "Posiłki czeskie", "type": "jazda", "power": 6, "unit": "horse", "faction": "cz",
              "cost": None, "desc": "Rycerze teścia Mieszka, księcia Bolesława."},
    "mieszczanie": {"name": "Straż miejska", "type": "lucznicy", "power": 5, "unit": "xbow", "faction": "pl",
                    "cost": None, "desc": "Mieszczanie bronią swoich murów."},
    "templariusze": {"name": "Templariusze i joannici", "type": "jazda", "power": 6, "unit": "knight_w", "faction": "kz",
                     "cost": None, "desc": "Rycerze zakonni, sojusznicy Henryka."},
    # karty wrogów
    "e_wieleci": {"name": "Wojowie Wichmana", "type": "piechota", "power": 5, "unit": "spear", "faction": "en"},
    "e_lucznicy": {"name": "Łucznicy wrogów", "type": "lucznicy", "power": 5, "unit": "bow", "faction": "en"},
    "e_jazda": {"name": "Jazda wroga", "type": "jazda", "power": 6, "unit": "horse", "faction": "en"},
    "e_mongol_luk": {"name": "Łucznicy konni", "type": "lucznicy", "power": 6, "unit": "horse_mg", "faction": "mg"},
    "e_mongol_ciezka": {"name": "Ciężka jazda mongolska", "type": "jazda", "power": 7, "unit": "horse_mg", "faction": "mg"},
    "e_mongol_dym": {"name": "Zasłona dymna", "type": "spec", "power": 6, "unit": "smoke", "faction": "mg"},
    "e_rozbojnicy": {"name": "Rozbójnicy", "type": "piechota", "power": 3, "unit": "spear", "faction": "en"},
    "e_kusznicy_z": {"name": "Kusznicy zakonni", "type": "lucznicy", "power": 6, "unit": "xbow", "faction": "tz"},
    "e_knechci": {"name": "Knechci", "type": "piechota", "power": 6, "unit": "pike", "faction": "tz"},
    "e_rycerze_z": {"name": "Rycerze zakonni", "type": "jazda", "power": 8, "unit": "knight_t", "faction": "tz"},
    "e_bombarda_z": {"name": "Bombardy Zakonu", "type": "spec", "power": 7, "unit": "cannon", "faction": "tz"},
    "e_wielki_mistrz": {"name": "Chorągiew Wielkiego Mistrza", "type": "jazda", "power": 10, "unit": "knight_t", "faction": "tz"},
}

# ---------------------------------------------------------------- TECHNOLOGIE (20)
TECHS = {
    # --- Epoka Plemienna
    "radlo": {"name": "Radło", "epoch": 0, "req": [], "cost": {"wood": 6},
              "effect": "Pola dają +1 żywności.",
              "q": "Do czego służyło radło?",
              "a": ["Do spulchniania ziemi przed siewem", "Do mielenia zboża", "Do łowienia ryb", "Do kucia mieczy"], "ok": 0,
              "fact": "Radło nie odwracało skiby jak późniejszy pług – tylko rozrywało glebę. Ciągnęły je woły, "
                      "a Słowianie używali go od wieków. Lepsze narzędzia = więcej chleba = większe grody."},
    "grod_walowy": {"name": "Gród wałowy", "epoch": 0, "req": [], "cost": {"wood": 8, "food": 4},
                    "effect": "+2 morale w bitwach. Odblokowuje Palisadę.",
                    "q": "Z czego Słowianie budowali wały grodów?",
                    "a": ["Z drewnianych skrzyń wypełnionych ziemią i kamieniami", "Z marmuru", "Z rzymskiej cegły", "Z lodu"], "ok": 0,
                    "fact": "Wały grodów w Gnieźnie czy Poznaniu miały nawet ok. 10 metrów wysokości. Drewniane "
                            "skrzynie (tzw. konstrukcja przekładkowa i skrzyniowa) wypełniano ziemią – taki wał trudno było spalić."},
    "pismo": {"name": "Chrzest i pismo", "epoch": 0, "req": [], "cost": {"silver": 6, "food": 4},
              "effect": "Odblokowuje Kościół i szkołę (podpowiedzi w zagadkach).",
              "q": "W którym roku Mieszko I przyjął chrzest?",
              "a": ["966", "1000", "1025", "1410"], "ok": 0,
              "fact": "Razem z chrztem przybyli duchowni, a z nimi pismo łacińskie. W 968 r. powstało biskupstwo "
                      "w Poznaniu, a pierwszym biskupem został Jordan. Książę mógł odtąd prowadzić listy i dokumenty jak władcy Europy."},
    "denar": {"name": "Denar", "epoch": 0, "req": [], "cost": {"silver": 4, "stone": 2},
              "effect": "Targi dają +1 srebra.",
              "q": "Jak nazywała się srebrna moneta bita przez pierwszych Piastów?",
              "a": ["Denar", "Euro", "Złotówka", "Talar"], "ok": 0,
              "fact": "Zanim pojawiły się monety, płacono siekańcami – kawałkami pociętej srebrnej biżuterii i monet, "
                      "ważonymi na wadze. Na denarze Bolesława Chrobrego widnieje napis PRINCES POLONIE – jedno z "
                      "najstarszych użyć nazwy Polski! Pieniądz ułatwia wymianę: nie trzeba nosić krowy na targ."},
    "druzyna": {"name": "Drużyna książęca", "epoch": 0, "req": ["grod_walowy"], "cost": {"silver": 6, "food": 6},
                "effect": "Odblokowuje kartę: Drużyna książęca (siła 6).",
                "q": "Ilu pancernych wojów miał Mieszko I według kupca Ibrahima ibn Jakuba?",
                "a": ["3000", "30", "300 000", "12"], "ok": 0,
                "fact": "Ibrahim ibn Jakub, kupiec z Hiszpanii, zapisał, że książę daje wojom broń, konie i ubrania, "
                        "a gdy któremuś urodzi się dziecko – dostaje na nie utrzymanie. Drużyna była droga, ale wierna!"},
    # --- Epoka Piastowska
    "trojpolowka": {"name": "Trójpolówka", "epoch": 1, "req": ["radlo"], "cost": {"wood": 6, "food": 6},
                    "effect": "Pola dają kolejne +1 żywności.",
                    "q": "Na czym polegała trójpolówka?",
                    "a": ["Ziemię dzielono na 3 części: zboże ozime, jare i ugór", "Każdy chłop miał trzy pola",
                          "Orano pole trzy razy dziennie", "Sadzono tylko trzy rośliny"], "ok": 0,
                    "fact": "Ugór odpoczywał przez rok, a pasące się na nim bydło użyźniało go nawozem. Co roku części "
                            "się zmieniały. Dzięki temu ziemia nie jałowiała, a plony rosły."},
    "mlyn": {"name": "Młyn wodny", "epoch": 1, "req": ["radlo"], "cost": {"wood": 8, "stone": 4},
             "effect": "Odblokowuje Młyn wodny (+4 żywności, przy wodzie).",
             "q": "Co napędzało koło młyna wodnego?",
             "a": ["Płynąca woda rzeki lub potoku", "Wiatr", "Para", "Koty w kołowrotku"], "ok": 0,
             "fact": "Młyn był maszyną, która zastępowała pracę wielu ludzi z żarnami. Za zmielenie zboża młynarz "
                     "pobierał opłatę – miarkę mąki. Dlatego młyny były bardzo dochodowe."},
    "kusza": {"name": "Kusza", "epoch": 1, "req": ["druzyna"], "cost": {"wood": 8, "silver": 6},
              "effect": "Odblokowuje kartę: Kusznicy (siła 6).",
              "q": "Czym kusza różniła się od łuku?",
              "a": ["Napiętą cięciwę zaczepiano na zamku, więc można było spokojnie celować",
                    "Strzelała kamieniami jak proca", "Nie potrzebowała pocisków", "Była większa od konia"], "ok": 0,
              "fact": "Sobór laterański w 1139 r. próbował zakazać używania kusz przeciw chrześcijanom, bo uważano je "
                      "za zbyt groźne. Nikt się tym zakazem specjalnie nie przejął."},
    "prawo_magd": {"name": "Prawo magdeburskie", "epoch": 1, "req": ["denar"], "cost": {"silver": 8, "wood": 6},
                   "effect": "Targi dają kolejne +2 srebra.",
                   "q": "Co otrzymywało miasto lokowane na prawie magdeburskim?",
                   "a": ["Samorząd: radę miejską, wójta i własny sąd", "Własnego króla",
                         "Zwolnienie z podatków na zawsze", "Prawo do wypowiadania wojen"], "ok": 0,
                   "fact": "Przy lokacji Krakowa w 1257 r. wytyczono Rynek o boku ok. 200 metrów – jeden z największych "
                           "placów średniowiecznej Europy. Ulice biegły od niego jak linie w zeszycie w kratkę."},
    "zupy": {"name": "Żupy solne", "epoch": 1, "req": ["denar"], "cost": {"wood": 8, "silver": 6},
             "effect": "Odblokowuje Żupę solną (+4 srebra, na wzgórzach).",
             "q": "Gdzie wydobywano sól w średniowiecznej Małopolsce?",
             "a": ["W Bochni i Wieliczce", "W Gdańsku i na Helu", "W Zakopanem", "W Gnieźnie"], "ok": 0,
             "fact": "Legenda mówi, że księżniczka Kinga wrzuciła pierścień do węgierskiej kopalni, a odnalazł się "
                     "w pierwszej bryle soli wykopanej w Polsce. Za Kazimierza Wielkiego zyski z żup dawały "
                     "nawet ok. jednej trzeciej dochodów króla!"},
    # --- Epoka Zamków
    "mury": {"name": "Mury kamienne", "epoch": 2, "req": ["grod_walowy"], "cost": {"stone": 10, "wood": 4},
             "effect": "Odblokowuje Zamek murowany (+6 morale w obronie).",
             "q": "O którym królu mówiono, że „zastał Polskę drewnianą, a zostawił murowaną”?",
             "a": ["Kazimierz Wielki", "Mieszko I", "Bolesław Krzywousty", "Władysław Jagiełło"], "ok": 0,
             "fact": "Za Kazimierza Wielkiego zbudowano lub umocniono kilkadziesiąt zamków i otoczono murami wiele "
                     "miast. Część z nich do dziś stoi na Szlaku Orlich Gniazd."},
    "cegla": {"name": "Cegła i gotyk", "epoch": 2, "req": ["mury"], "cost": {"stone": 8, "food": 4},
              "effect": "Kamieniołomy dają +1 kamienia, a pożary są mniej groźne.",
              "q": "Jaki styl budowli z wysokimi, ostrymi łukami rozpowszechnił się w XIV wieku?",
              "a": ["Gotyk", "Barok", "Secesja", "Styl kosmiczny"], "ok": 0,
              "fact": "Zamek w Malborku, zbudowany przez Krzyżaków, to największy ceglany zamek na świecie. "
                      "Ceglane gotyckie kościoły stoją w Toruniu, Gdańsku i Krakowie (Kościół Mariacki)."},
    "akademia": {"name": "Akademia Krakowska", "epoch": 2, "req": ["pismo", "prawo_magd"], "cost": {"silver": 10, "food": 4},
                 "effect": "Technologie tańsze o 25%. Podpowiedź także w pytaniach bitewnych.",
                 "q": "Kto założył Akademię Krakowską w 1364 roku?",
                 "a": ["Kazimierz Wielki", "Mieszko I", "Henryk Pobożny", "Bolesław Chrobry"], "ok": 0,
                 "fact": "Królowa Jadwiga zapisała swoje klejnoty na odnowienie uczelni, a Władysław Jagiełło "
                         "odnowił ją w 1400 r. Później studiował tu Mikołaj Kopernik. Dziś to Uniwersytet Jagielloński."},
    "statut": {"name": "Statuty prawa", "epoch": 2, "req": ["pismo"], "cost": {"silver": 6, "wood": 4},
               "effect": "Złe zdarzenia losowe zabierają o połowę mniej.",
               "q": "Co spisano w statutach wiślicko-piotrkowskich Kazimierza Wielkiego?",
               "a": ["Prawa obowiązujące w królestwie", "Przepisy kulinarne", "Spis wszystkich krów", "Mapy nieba"], "ok": 0,
               "fact": "Spisane prawo oznaczało, że sędzia nie mógł wymyślać wyroków „z głowy”. Kazimierza nazywano "
                       "też „królem chłopów”, bo – jak pisał kronikarz – bronił ich przed krzywdą."},
    "rycerze": {"name": "Ciężka jazda rycerska", "epoch": 2, "req": ["druzyna"], "cost": {"silver": 8, "food": 6},
                "effect": "Odblokowuje kartę: Rycerstwo (siła 8).",
                "q": "Jak nazywał się znak rodowy rycerza, malowany np. na tarczy?",
                "a": ["Herb", "Logo", "Pieczątka", "Kokarda"], "ok": 0,
                "fact": "Polskie rody rycerskie miały herby i zawołania – okrzyki bojowe. Herby takie jak Topór, Leliwa "
                        "czy Nałęcz nosiły całe rody, a nie tylko jedna rodzina."},
    # --- Epoka Jagiellońska
    "bombarda": {"name": "Bombarda", "epoch": 3, "req": ["mury"], "cost": {"stone": 8, "silver": 10},
                 "effect": "Odblokowuje kartę: Bombarda (siła 9).",
                 "q": "Co było niezbędne do wystrzału z bombardy?",
                 "a": ["Proch strzelniczy", "Cięciwa", "Para wodna", "Sprężyna z zegara"], "ok": 0,
                 "fact": "Pod Grunwaldem Krzyżacy ustawili bombardy, ale deszcz zamoczył proch i oddali tylko "
                         "kilka mało groźnych strzałów. Wynalazek miał jednak przyszłość – i to głośną."},
    "tabor": {"name": "Tabor wozowy", "epoch": 3, "req": ["rycerze"], "cost": {"wood": 10, "food": 4},
              "effect": "Odblokowuje kartę: Tabor wozów (pochłania 4 obrażenia).",
              "q": "Czym był tabor w średniowiecznym wojsku?",
              "a": ["Wozami z zapasami, które ustawiano w obronny krąg", "Rodzajem hełmu", "Sztandarem króla", "Okrzykiem bojowym"], "ok": 0,
              "fact": "Mistrzami taboru byli czescy husyci – ich wozy spinano łańcuchami w ruchome twierdze. "
                      "Wielka armia potrzebuje jedzenia: bez taboru nawet najdzielniejsi rycerze szybko zgłodnieją."},
    "dyplomacja": {"name": "Unia i dyplomacja", "epoch": 3, "req": ["statut"], "cost": {"silver": 10, "food": 4},
                   "effect": "Odblokowuje kartę: Chorągiew litewska (siła 7). Poselstwa przynoszą więcej.",
                   "q": "Kogo poślubiła królowa Jadwiga zgodnie z ustaleniami w Krewie?",
                   "a": ["Władysława Jagiełłę", "Wilhelma Habsburga", "Ulricha von Jungingena", "Bolesława Chrobrego"], "ok": 0,
                   "fact": "W Krewie (1385) Jagiełło obiecał przyjąć chrzest wraz z Litwą i połączyć swoje ziemie z Koroną. "
                           "Tak zaczął się związek dwóch narodów, który przetrwał ponad 400 lat."},
    "most": {"name": "Most łyżwowy", "epoch": 3, "req": ["mlyn"], "cost": {"wood": 12, "stone": 2},
             "effect": "Armia szybciej maszeruje: +3 morale we wszystkich bitwach.",
             "q": "Jak armia Jagiełły przeprawiła się przez Wisłę w 1410 roku?",
             "a": ["Po moście łyżwowym zbudowanym wcześniej w puszczy", "Wpław, trzymając konie za ogony",
                   "Poczekała, aż rzeka zamarznie", "Każdy rycerz przeskoczył o tyczce"], "ok": 0,
             "fact": "Most zbudowano zimą w lasach niedaleko Kozienic, spławiono Wisłą i złożono pod Czerwińskiem "
                     "w kilka dni. Krzyżacy nie spodziewali się przeprawy w tym miejscu – logistyka wygrywa wojny!"},
    "zaciezni": {"name": "Wojska zaciężne", "epoch": 3, "req": ["prawo_magd"], "cost": {"silver": 12},
                 "effect": "Odblokowuje kartę: Zaciężni (siła 7) i +1 karta na ręce w bitwie.",
                 "q": "Kim byli żołnierze zaciężni?",
                 "a": ["Wojownikami walczącymi za żołd, czyli zapłatę", "Mnichami", "Kupcami z Hanzy", "Sokolnikami"], "ok": 0,
                 "fact": "Słowo „żołnierz” pochodzi właśnie od „żołdu”. Armia zaciężna była sprawna, ale droga – "
                         "władca musiał mieć pełny skarbiec, więc dobra gospodarka to także siła wojska."},
}

# ---------------------------------------------------------------- PYTANIA BITEWNE
QUESTIONS = {
    0: [
        ("Od którego plemienia wzięła się nazwa Polski?", ["Polan", "Wiślan", "Ślężan", "Pomorzan"], 0),
        ("Kim była Dobrawa?", ["Czeską księżniczką, żoną Mieszka I", "Królową Węgier", "Siostrą Ottona III", "Kupcową z Wolina"], 0),
        ("Kto opisał państwo Mieszka I w X wieku?", ["Ibrahim ibn Jakub", "Marco Polo", "Krzysztof Kolumb", "Jan Długosz"], 0),
        ("Z którym jeziorem wiąże się legenda o Popielu i myszach?", ["Gopłem", "Śniardwami", "Morskim Okiem", "Wigrami"], 0),
        ("Która rzeka przepływa przez Poznań?", ["Warta", "Wisła", "Odra", "Bug"], 0),
        ("Kto był pierwszym koronowanym królem Polski (1025)?", ["Bolesław Chrobry", "Mieszko I", "Popiel", "Kazimierz Wielki"], 0),
        ("Czyje relikwie spoczęły w Gnieźnie i ściągnęły tam cesarza w roku 1000?", ["Świętego Wojciecha", "Świętego Mikołaja", "Świętego Floriana", "Świętej Barbary"], 0),
        ("Czym był gród?", ["Osadą otoczoną wałem i palisadą", "Kamiennym pałacem", "Rodzajem łodzi", "Polem bitwy"], 0),
        ("Jak nazywało się miasto, które było jedną z głównych siedzib Mieszka I?", ["Gniezno", "Warszawa", "Lublin", "Białystok"], 0),
        ("Kim był założyciel dynastii według legendy – oracz, którego gościli wędrowcy?", ["Piast Kołodziej", "Lech", "Krak", "Popiel"], 0),
    ],
    1: [
        ("Kto podzielił Polskę między synów w 1138 roku?", ["Bolesław Krzywousty", "Mieszko I", "Kazimierz Wielki", "Henryk Brodaty"], 0),
        ("Kto sprowadził Krzyżaków do Polski w 1226 roku?", ["Konrad Mazowiecki", "Henryk Pobożny", "Bolesław Wstydliwy", "Władysław Łokietek"], 0),
        ("Z jakim najazdem wiąże się legenda o przerwanym hejnale mariackim?", ["Najazdem Tatarów", "Najazdem Wikingów", "Najazdem Rzymian", "Najazdem Szwedów"], 0),
        ("W którym roku stoczono bitwę pod Legnicą?", ["1241", "1410", "966", "1525"], 0),
        ("Co oznaczała lokacja miasta?", ["Założenie go lub nadanie mu nowego prawa", "Zburzenie murów", "Przeniesienie stolicy", "Spis ludności"], 0),
        ("Kim był sołtys we wsi lokowanej?", ["Zarządcą i sędzią wsi", "Piekarzem", "Biskupem", "Najemnym rycerzem"], 0),
        ("Jak nazywał się główny plac miasta, na którym odbywał się handel?", ["Rynek", "Forum", "Agora", "Arena"], 0),
        ("Która rzeka przepływa przez Kraków?", ["Wisła", "Warta", "Odra", "Noteć"], 0),
        ("Co to jest cło?", ["Opłata za przewóz towarów przez granicę lub miasto", "Rodzaj zbroi", "Święto plonów", "Nazwa monety"], 0),
        ("Kogo nazywano Wstydliwym?", ["Bolesława V, męża Kingi", "Mieszka I", "Henryka Pobożnego", "Krzyżackiego mistrza"], 0),
    ],
    2: [
        ("W którym roku odbyła się bitwa pod Płowcami?", ["1331", "1410", "966", "1241"], 0),
        ("Kto koronował się w 1320 roku i zjednoczył większość ziem polskich?", ["Władysław Łokietek", "Mieszko II", "Bolesław Śmiały", "Jagiełło"], 0),
        ("Jak nazywała się główna twierdza Krzyżaków?", ["Malbork", "Wawel", "Biskupin", "Krewo"], 0),
        ("Kto był ostatnim królem z dynastii Piastów?", ["Kazimierz Wielki", "Władysław Łokietek", "Bolesław Wstydliwy", "Ludwik Węgierski"], 0),
        ("Jak nazywa się szlak zamków na Jurze Krakowsko-Częstochowskiej?", ["Szlak Orlich Gniazd", "Szlak Bursztynowy", "Szlak Jedwabny", "Szlak Piastowski Morski"], 0),
        ("Czym była fosa?", ["Rowem z wodą wokół murów", "Wieżą strażniczą", "Bramą zamku", "Zbroją konia"], 0),
        ("Jak nazywa się główna, najwyższa wieża obronna zamku?", ["Donżon (stołp)", "Krużganek", "Kaplica", "Spiżarnia"], 0),
        ("Gdzie odbyła się słynna uczta u Wierzynka (1364)?", ["W Krakowie", "W Gdańsku", "W Wilnie", "W Rzymie"], 0),
        ("Jakie przezwisko miał Władysław, bo był niskiego wzrostu?", ["Łokietek", "Krzywousty", "Śmiały", "Laskonogi"], 0),
        ("Kogo Łokietek wysłał z pola bitwy pod Płowcami, by był bezpieczny?", ["Syna Kazimierza", "Biskupa", "Kucharza", "Konia"], 0),
    ],
    3: [
        ("W którym roku zawarto unię w Krewie?", ["1385", "1410", "1569", "1025"], 0),
        ("Kiedy rozegrała się bitwa pod Grunwaldem?", ["15 lipca 1410", "1 września 1939", "14 kwietnia 966", "9 kwietnia 1241"], 0),
        ("Kto był wielkim mistrzem krzyżackim pod Grunwaldem?", ["Ulrich von Jungingen", "Konrad Mazowiecki", "Hermann von Salza", "Witold"], 0),
        ("Jaką pieśń śpiewało rycerstwo przed bitwą pod Grunwaldem?", ["Bogurodzicę", "Mazurek Dąbrowskiego", "Rotę", "Sto lat"], 0),
        ("Co posłowie krzyżaccy przynieśli Jagielle przed bitwą?", ["Dwa nagie miecze", "Dwa złote puchary", "Mapę Malborka", "Klucze do Torunia"], 0),
        ("Jaki pokój zakończył wojnę z Zakonem w 1411 roku?", ["Pierwszy pokój toruński", "Pokój westfalski", "Pokój w Kaliszu", "Pokój ryski"], 0),
        ("Kim był Witold dla Jagiełły?", ["Jego bratem stryjecznym i wielkim księciem litewskim", "Jego ojcem", "Krzyżackim posłem", "Węgierskim królem"], 0),
        ("Co znaczy powiedzenie „polegać jak na Zawiszy”?", ["Można komuś całkowicie zaufać", "Ktoś jest bardzo leniwy", "Ktoś jest głodny", "Ktoś zgubił miecz"], 0),
        ("Kogo koronowano na „króla Polski” w 1384 roku, choć była dziewczyną?", ["Jadwigę Andegaweńską", "Kingę", "Dobrawę", "Elżbietę Łokietkównę"], 0),
        ("Jaki kraj połączył się z Polską unią w 1385 roku?", ["Wielkie Księstwo Litewskie", "Węgry", "Czechy", "Szwecja"], 0),
    ],
}

# ---------------------------------------------------------------- POSTACIE (12)
# portret: skóra, włosy, broda, nakrycie głowy, strój, tło
CHARACTERS = {
    "mieszko": {"name": "Mieszko I", "title": "Książę Polan", "years": "ok. 930–992",
                "p": {"hair": (90, 60, 30), "beard": "full", "head": "circlet", "cloth": (150, 40, 40), "bg": (70, 90, 60)},
                "bio": "Pierwszy historyczny władca Polski. W 966 r. przyjął chrzest, a jego państwo weszło do rodziny "
                       "chrześcijańskiej Europy. Zręczny wojownik i jeszcze zręczniejszy polityk.",
                "fact": "Około 991 r. powstał dokument „Dagome iudex”, w którym Mieszko oddał swoje państwo pod opiekę papieża."},
    "dobrawa": {"name": "Dobrawa", "title": "Księżna z Czech", "years": "ok. 940–977",
                "p": {"hair": (110, 70, 35), "beard": None, "head": "veil", "cloth": (60, 80, 150), "bg": (90, 70, 110)},
                "bio": "Czeska księżniczka, córka Bolesława I. Jej ślub z Mieszkiem (965) przypieczętował sojusz z Czechami "
                       "i przyniósł chrzest.",
                "fact": "Według Galla Anonima to Dobrawa przekonała Mieszka do odrzucenia pogaństwa. Była matką Bolesława Chrobrego."},
    "jordan": {"name": "Biskup Jordan", "title": "Pierwszy biskup", "years": "zm. 982/984",
               "p": {"hair": (120, 110, 100), "beard": None, "head": "mitre", "cloth": (230, 225, 210), "bg": (120, 100, 60)},
               "bio": "Duchowny, który przybył do kraju Polan, by nauczać nowej wiary. Od 968 r. biskup w Poznaniu.",
               "fact": "Jordan był pierwszym biskupem na ziemiach polskich – z nim zaczęła się tu historia szkół i ksiąg."},
    "henryk": {"name": "Henryk II Pobożny", "title": "Książę śląski", "years": "ok. 1196–1241",
               "p": {"hair": (140, 100, 50), "beard": "short", "head": "helmet", "cloth": (180, 160, 60), "bg": (100, 60, 50)},
               "bio": "Książę Śląska i Krakowa, syn św. Jadwigi Śląskiej. Stanął do walki z najazdem mongolskim w 1241 r.",
               "fact": "Zginął pod Legnicą 9 kwietnia 1241 r. Jego ciało rozpoznała matka – po sześciu palcach u stopy."},
    "boleslaw": {"name": "Bolesław V Wstydliwy", "title": "Książę krakowski", "years": "1226–1279",
                 "p": {"hair": (180, 140, 70), "beard": None, "head": "crown_s", "cloth": (130, 40, 90), "bg": (60, 80, 110)},
                 "bio": "Książę krakowski i sandomierski. W 1257 r. nadał Krakowowi prawo magdeburskie.",
                 "fact": "Przydomek „Wstydliwy” zawdzięcza pobożnemu życiu. Za jego rządów Kraków dwa razy łupili Mongołowie – i dwa razy się odbudował."},
    "kinga": {"name": "Kinga", "title": "Księżna, patronka górników", "years": "1234–1292",
              "p": {"hair": (200, 160, 80), "beard": None, "head": "crown_veil", "cloth": (240, 240, 235), "bg": (80, 110, 130)},
              "bio": "Węgierska królewna, żona Bolesława Wstydliwego. Wniosła bogaty posag i dbała o rozwój żup solnych.",
              "fact": "W kopalni w Wieliczce jest wykuta w soli Kaplica św. Kingi – podłoga, żyrandole i rzeźby są z soli!"},
    "lokietek": {"name": "Władysław Łokietek", "title": "Król Polski", "years": "1260/61–1333",
                 "p": {"hair": (70, 50, 40), "beard": "full", "head": "crown_b", "cloth": (160, 30, 30), "bg": (80, 80, 90)},
                 "bio": "Niski wzrostem, wielki uporem. Zjednoczył ziemie polskie i koronował się w 1320 r. w Krakowie.",
                 "fact": "Według legendy ukrywał się przed wrogami w jaskini pod Ojcowem, a pająk zasnuł wejście pajęczyną."},
    "kazimierz": {"name": "Kazimierz Wielki", "title": "Król budowniczy", "years": "1310–1370",
                  "p": {"hair": (60, 40, 30), "beard": "long", "head": "crown_b", "cloth": (90, 50, 140), "bg": (100, 90, 60)},
                  "bio": "Ostatni z Piastów na tronie. Budował zamki, miasta i spisał prawa; założył Akademię Krakowską (1364).",
                  "fact": "Jako jedyny polski król nosi przydomek „Wielki” nadany za mądre rządy, a nie za wojny."},
    "jadwiga": {"name": "Jadwiga", "title": "Król Polski", "years": "1373/74–1399",
                "p": {"hair": (220, 180, 90), "beard": None, "head": "crown_s", "cloth": (40, 70, 150), "bg": (120, 90, 120)},
                "bio": "Koronowana w 1384 r. na „króla” Polski. Zgodziła się na małżeństwo z Jagiełłą, by połączyć Polskę i Litwę.",
                "fact": "Ofiarowała swoje klejnoty na odnowienie Akademii Krakowskiej. Jest świętą Kościoła katolickiego."},
    "jagiello": {"name": "Władysław Jagiełło", "title": "Król Polski, książę Litwy", "years": "ok. 1362–1434",
                 "p": {"hair": (60, 45, 35), "beard": "short", "head": "crown_b", "cloth": (150, 30, 30), "bg": (60, 90, 70)},
                 "bio": "Wielki książę litewski, od 1386 r. król Polski. Zwycięzca spod Grunwaldu.",
                 "fact": "Podobno nie pił wina ani miodu – tylko wodę – i uwielbiał słuchać śpiewu słowików w lesie. Rządził 48 lat!"},
    "witold": {"name": "Witold", "title": "Wielki książę litewski", "years": "ok. 1350–1430",
               "p": {"hair": (90, 70, 50), "beard": "mustache", "head": "fur", "cloth": (40, 110, 70), "bg": (110, 70, 50)},
               "bio": "Brat stryjeczny Jagiełły. Pod Grunwaldem dowodził skrzydłem litewskim.",
               "fact": "Pozorowany odwrót Litwinów pod Grunwaldem do dziś budzi spory: ucieczka czy podstęp wojenny?"},
    "zawisza": {"name": "Zawisza Czarny", "title": "Rycerz z Garbowa", "years": "ok. 1370–1428",
                "p": {"hair": (25, 20, 20), "beard": "short", "head": "none", "cloth": (30, 30, 35), "bg": (130, 50, 40)},
                "bio": "Najsłynniejszy polski rycerz, herbu Sulima. Zwycięzca wielu turniejów, dyplomata i wierny sługa króla.",
                "fact": "Przydomek „Czarny” wziął się prawdopodobnie od czarnych włosów lub czarnej zbroi."},
}

HERO = {"name": "Damian Ściseł", "title": "Kronikarz i doradca", "years": "wędrowny",
         "p": {"hair": (222, 184, 96), "beard": None, "head": "hood", "cloth": (110, 50, 150), "bg": (60, 50, 80)}}

# ---------------------------------------------------------------- ZDARZENIA LOSOWE
# efekty: dict zasobów; "card": dodaj kartę; "battle": [talia wroga]; "morale": bonus do następnej bitwy
EVENTS = [
    {"id": "zaraza", "title": "Zaraza w podgrodziu!", "icon": "plague",
     "text": "Ludzie kaszlą i gorączkują. Medyk rozkłada ręce, wróżka rozkłada karty, a Damian rozkłada kronikę: "
             "„W dawnych wiekach chorych oddzielano od zdrowych – to się nazywa kwarantanna, od włoskiego "
             "»quaranta«, czyli czterdzieści dni.”",
     "choices": [
         ("Odizolować chorych, palić zbutwiałe słomy", {"food": -4, "wood": -3}, "Mądrze! Zaraza wygasła szybko."),
         ("Nic nie robić, „samo przejdzie”", {"food": -10, "silver": -4}, "Nie przeszło. Choroba zabrała wielu ludzi i plony."),
     ]},
    {"id": "najazd", "title": "Najazd łupieżców!", "icon": "raid",
     "text": "Zza lasu wypadła banda zbrojnych. Chcą srebra – albo walki. Książę patrzy na ciebie, kronikarzu.",
     "choices": [
         ("Zapłacić okup (8 srebra)", {"silver": -8}, "Łupieżcy odjechali. Skarbiec lżejszy, ale nikt nie zginął."),
         ("Doradzić walkę!", {"battle": ["e_rozbojnicy", "e_rozbojnicy", "e_lucznicy", "e_jazda"]}, ""),
     ]},
    {"id": "poselstwo", "title": "Poselstwo z dalekiego kraju", "icon": "envoy",
     "text": "Do grodu przybyli posłowie w futrach i jedwabiach. Przywieźli dary i propozycję przyjaźni. "
             "Wypada się zrewanżować – dyplomacja to wymiana, nie tylko uśmiechy.",
     "choices": [
         ("Ugościć ich hojnie (−6 żywności)", {"food": -6, "silver": 10}, "Posłowie zachwyceni! Zostawili szkatułę srebra."),
         ("Przyjąć dary i odprawić", {"silver": 4}, "Posłowie wyjechali nieco urażeni, ale dary zostały."),
     ]},
    {"id": "susza", "title": "Susza", "icon": "sun",
     "text": "Od tygodni ani kropli deszczu. Zboże żółknie na pniu. Damian przypomina: „Zapasy w spichlerzu "
             "to jak oszczędności w skarbonce – ratują w złych czasach.”",
     "choices": [
         ("Rozdać ludziom zapasy ze spichlerza", {"food": -8}, "Ludzie przetrwali i są ci wdzięczni."),
         ("Kupić zboże od kupców (−8 srebra)", {"silver": -8, "food": 2}, "Kupcy podnieśli ceny – bo popyt wielki – ale głodu nie było."),
     ]},
    {"id": "jarmark", "title": "Wielki jarmark", "icon": "market",
     "text": "Do grodu zjechali kupcy z całej okolicy! Za drewno płacą srebrem, bo w ich stronach lasów mało. "
             "Gdy czegoś jest mało, a chętnych wielu – cena rośnie.",
     "choices": [
         ("Sprzedać 10 drewna za 8 srebra", {"wood": -10, "silver": 8}, "Udany handel! Kronikarz notuje: „Podaż i popyt – zapamiętać.”"),
         ("Kupić żywność: 6 srebra za 12 żywności", {"silver": -6, "food": 12}, "Spichlerz pełny, kupcy zadowoleni."),
         ("Tylko pooglądać", {}, "Damian kupił sobie nowe gęsie pióro. Za swoje."),
     ]},
    {"id": "pozar", "title": "Pożar!", "icon": "fire",
     "text": "Ktoś przewrócił kaganek na słomę. Drewniane chaty płoną jak hubka! Trzeba ratować, co się da.",
     "choices": [
         ("Ratować spichlerz", {"wood": -8}, "Żywność ocalała, ale spłonęło sporo drewna."),
         ("Ratować skład drewna", {"food": -8}, "Drewno ocalało, ale część zapasów żywności przepadła."),
     ]},
    {"id": "urodzaj", "title": "Urodzaj!", "icon": "wheat",
     "text": "Pola uginają się od kłosów. Wszyscy mają dużo zboża... więc kupcy dają za nie mniej niż zwykle.",
     "choices": [
         ("Zebrać wszystko do spichlerza", {"food": 12}, "Spichlerz pęka w szwach!"),
         ("Sprzedać nadwyżkę tanio", {"food": 4, "silver": 5}, "Zarobek mniejszy niż w chudym roku – taka jest ekonomia."),
     ]},
    {"id": "kometa", "title": "Kometa na niebie", "icon": "comet",
     "text": "Nad grodem pojawiła się gwiazda z ogonem. Ludzie szepczą o złej wróżbie. Damian spokojnie notuje "
             "datę: „Komety wracają jak dłużnicy – rzadko, ale regularnie.”",
     "choices": [
         ("Uspokoić ludzi (rozdać 4 żywności)", {"food": -4, "morale": 2}, "Lud odetchnął. Wojowie pójdą do bitwy pewniej (+2 morale)."),
         ("Zignorować", {}, "Kometa sobie poleciała. Plotki zostały."),
     ]},
    {"id": "zak", "title": "Wędrowny żak", "icon": "scholar",
     "text": "Do grodu przyszedł wędrowny student z torbą pełną ksiąg. Proponuje zakład: jeśli odpowiesz na jego "
             "pytanie, odda ci swoje oszczędności.",
     "choices": [
         ("Przyjąć wyzwanie!", {"quiz": 6}, ""),
         ("Poczęstować go obiadem", {"food": -2, "stone": 4}, "W podzięce wskazał miejsce z dobrym kamieniem."),
     ]},
    {"id": "kupcy", "title": "Kupcy na szlaku bursztynowym", "icon": "amber",
     "text": "Przez twoje ziemie ciągnie karawana z bursztynem znad morza na południe. Można pobrać myto – "
             "opłatę za przejazd – albo zaprosić kupców, by tu zostali.",
     "choices": [
         ("Pobrać myto (+6 srebra)", {"silver": 6}, "Skarbiec brzęczy."),
         ("Zwolnić z myta, niech się osiedlą (+2 kamienia, +8 żywności)", {"stone": 2, "food": 8},
          "Kupcy obiecali wracać. Dobra opinia to też kapitał!"),
     ]},
]

# ---------------------------------------------------------------- ROZDZIAŁY / MISJE
# objectives: ("build", typ, n) ("res", zasób, n) ("tech", id) ("camp", id_obozu) ("final",)
CHAPTERS = [
    {
        "id": 0, "epoch": 0, "year": "966–967", "place": "Gniezno",
        "title": "Rozdział I: Woda i ogień",
        "chronicle": [
            "Roku Pańskiego 966. Nad Wartą i Gopłem szumią puszcze, a w grodach Polan trzaskają ogniska. "
            "Książę Mieszko z rodu Piastów patrzy na zachód, gdzie potężne Cesarstwo zerka chciwie na słowiańskie ziemie.",
            "Ja, Damian Ściseł, wędrowny kronikarz w fioletowym kapturze (tak, fioletowym – zielone były wyprzedane "
            "na jarmarku), zostałem doradcą księcia. Mam gęsie pióro, kałamarz i niezłomną wiarę, że dobra rada "
            "jest warta więcej niż sto toporów. No, może osiemdziesiąt.",
            "Do Gniezna przybyła czeska księżniczka Dobrawa. Wraz z nią – nowa wiara, pismo i sojusznicy. "
            "Ale na północnym zachodzie czai się Wichman, saski awanturnik, który zbiera wojowników przeciw księciu...",
            "Zadanie: wzmocnić księstwo, przyjąć chrzest i pismo, a gdy przyjdzie czas – odeprzeć Wichmana.",
        ],
        "map": {"seed": 966, "lakes": [(8, 20, 3), (22, 9, 2), (17, 25, 2)], "river": [(0, 14), (6, 15), (12, 13), (19, 14), (25, 18), (29, 19)],
                "forest": 0.30, "hills": 0.06, "capital": (14, 17),
                "landmarks": [((9, 18), "Ostrów Lednicki", "Wyspa na jeziorze Lednica z grodem i kaplicą. Być może tu właśnie odbył się chrzest Mieszka – historycy wciąż się spierają, bo wskazuje się też Gniezno, Poznań, a nawet Ratyzbonę."),
                              ((20, 22), "Wzgórze Lecha", "Legenda mówi, że Lech zobaczył tu orła w gnieździe na tle zachodzącego słońca. Stąd nazwa Gniezna i biały orzeł w herbie.")],
                "camps": [((4, 4), "wichman", "Obóz Wichmana", ["e_wieleci", "e_wieleci", "e_lucznicy", "e_jazda", "e_wieleci"])]},
        "start_res": {"food": 18, "wood": 20, "stone": 4, "silver": 8},
        "start_deck": ["woje", "woje", "woje", "lucznicy", "lucznicy", "konni"],
        "turns": 30,
        "objectives": [("build", "pole", 3), ("tech", "pismo"), ("build", "kosciol", 1), ("res", "silver", 15), ("final",)],
        "final": {"name": "Bitwa z Wichmanem (967)", "enemy_morale": 30, "defense": False, "terrain": "forest",
                  "deck": ["e_wieleci", "e_wieleci", "e_lucznicy", "e_jazda", "e_wieleci", "e_jazda", "e_lucznicy"],
                  "allies": ["czesi", "czesi"],
                  "intro": "Rok 967. Wichman wyruszył na czele Wolinian. Mieszko ma po swojej stronie jazdę czeską – dar teścia, "
                           "księcia Bolesława. Kronika drży w moich dłoniach... a może to tylko wiatr."},
        "dialogue_start": [("mieszko", "Kronikarzu! Mówią, że znasz litery i liczby. Pomóż mi zbudować państwo, którego nie złamie żaden Wichman."),
                           ("dobrawa", "Chrzest otworzy nam drzwi do Europy, mężu. A pismo pozwoli zapisać nasze prawa i nasze dzieje."),
                           ("damian", "Moja rada: najpierw chleb, potem książki, a na końcu miecze. Pusty brzuch nie przeczyta ani litery!")],
        "scripted": {3: ("jordan", "Przybyłem z księgami i świecami. Gdy poznacie tajemnicę pisma, zbudujcie kościół – nauczę w nim chłopców czytać."),
                     8: ("decision", "Dobrawa proponuje, by zaprosić rzemieślników z Czech.",
                         [("Zaprosić (−6 srebra, +10 drewna, +4 kamienia)", {"silver": -6, "wood": 10, "stone": 4}, "Czescy cieśle już stukają siekierami!"),
                          ("Polegać na swoich", {"food": 4}, "Miejscowi zapracowali na dodatkową miskę kaszy.")]),
                     14: ("mieszko", "Zwiadowcy donoszą: Wichman zbiera ludzi. Musimy być gotowi!")},
        "victory": "Wichman poległ, a Mieszko – jak zapisał kronikarz Widukind – posłał jego broń cesarzowi. "
                   "Księstwo Polan stało się państwem, z którym liczy się Europa. W kronice stawiam pierwszą wielką inicjałę: "
                   "„Tu zaczyna się Polska”.",
    },
    {
        "id": 1, "epoch": 1, "year": "1241", "place": "Legnica",
        "title": "Rozdział II: Burza ze Wschodu",
        "chronicle": [
            "Roku 1241. Polska podzielona na dzielnice, każda ze swoim księciem – jak tort pokrojony na zbyt wiele "
            "kawałków. A ze wschodu nadciąga burza: Mongołowie, których w Europie zwą Tatarami.",
            "Spalili Sandomierz, złupili Kraków. Mówią, że trębacz z wieży mariackiej zginął od strzały w pół hejnału – "
            "dlatego do dziś hejnał urywa się nagle.",
            "Książę Henryk Pobożny zbiera rycerstwo pod Legnicą. Ja zaś mam zadanie trudniejsze niż miecz: przygotować "
            "gród na oblężenie. Wały, zapasy, łucznicy na murach. Czas ucieka... tur zostało niewiele.",
            "Zadanie: umocnić gród palisadami, zgromadzić zapasy i wytrzymać oblężenie.",
        ],
        "map": {"seed": 1241, "lakes": [(23, 6, 2)], "river": [(29, 3), (22, 8), (17, 13), (15, 18), (10, 24), (6, 29)],
                "forest": 0.26, "hills": 0.10, "capital": (12, 14),
                "landmarks": [((21, 19), "Legnickie Pole", "Tu 9 kwietnia 1241 r. rycerstwo Henryka Pobożnego starło się z Mongołami. Henryk zginął, ale Mongołowie wkrótce zawrócili na Węgry."),
                              ((5, 9), "Klasztor w Trzebnicy", "Ufundował go Henryk Brodaty na prośbę żony, św. Jadwigi Śląskiej – matki Henryka Pobożnego.")],
                "camps": [((26, 24), "zwiad", "Zwiad mongolski", ["e_mongol_luk", "e_mongol_luk", "e_mongol_dym", "e_mongol_ciezka"])]},
        "start_res": {"food": 20, "wood": 22, "stone": 6, "silver": 10},
        "start_deck": ["woje", "woje", "lucznicy", "lucznicy", "konni", "konni"],
        "turns": 18, "siege_turn": 16,
        "objectives": [("tech", "grod_walowy"), ("build", "palisada", 2), ("res", "food", 30), ("final",)],
        "final": {"name": "Oblężenie grodu legnickiego", "enemy_morale": 40, "defense": True, "terrain": "grod",
                  "deck": ["e_mongol_luk", "e_mongol_ciezka", "e_mongol_dym", "e_mongol_luk", "e_mongol_ciezka", "e_mongol_luk", "e_mongol_dym"],
                  "allies": ["templariusze", "mieszczanie"],
                  "intro": "Ziemia drży od kopyt. Tumany kurzu, dziwne chorągwie i dym, który gryzie w oczy. "
                           "Mongołowie otoczyli gród! Na blankach stoją mieszczanie z łukami. Teraz albo nigdy..."},
        "dialogue_start": [("henryk", "Kronikarzu, ja poprowadzę rycerstwo w pole. Ty zostań w grodzie i dopilnuj, by wytrzymał – cokolwiek się stanie."),
                           ("damian", "Wasza Miłość, wróg strzela z konia w pełnym galopie i udaje ucieczkę, by wciągnąć nas w zasadzkę. Nie dajmy się nabrać!"),
                           ("henryk", "Zapisz to w kronice. I módl się, by przyszłe pokolenia czytały o nas z dumą.")],
        "scripted": {4: ("henryk", "Ze wschodu dochodzą złe wieści: Kraków płonie. Do oblężenia zostało niewiele czasu!"),
                     9: ("decision", "Uciekinierzy ze wsi proszą o schronienie w grodzie.",
                         [("Przyjąć wszystkich (−6 żywności, +karta: Woje)", {"food": -6, "card": "woje"}, "Każde ręce do obrony się przydadzą."),
                          ("Odesłać ich do lasu", {"food": 2}, "Zapasów starczy na dłużej... ale serce kronikarza ciąży.")]),
                     12: ("henryk", "Ruszam pod Legnickie Pole. Jeśli nie wrócę... gród musi przetrwać."),
                     14: ("damian", "Gońcy donoszą: książę Henryk poległ. Mongołowie idą na gród! Do oblężenia zostały 2 tury!")},
        "victory": "Gród legnicki nie został zdobyty! Mongołowie, nie mogąc sforsować umocnień, odjechali na Węgry. "
                   "Książę Henryk zginął w bitwie, lecz jego poświęcenie zatrzymało najeźdźców. W kronice zapisuję: "
                   "„Mury to nie tylko kamienie – to ludzie, którzy na nich stoją.”",
    },
    {
        "id": 2, "epoch": 1, "year": "1257", "place": "Kraków",
        "title": "Rozdział III: Miasto z prawem",
        "chronicle": [
            "Roku 1257. Kraków podnosi się z popiołów po najeździe. Książę Bolesław Wstydliwy ma śmiały plan: "
            "zbudować miasto od nowa, z prostymi ulicami i wielkim rynkiem – na prawie magdeburskim.",
            "To znaczy, że mieszczanie sami wybiorą radę, będą mieli własny sąd i wójta. Książę zaś dostanie podatki "
            "i czynsze. Wszyscy zyskują – to właśnie ekonomia, mili moi czytelnicy!",
            "Księżna Kinga ma swoje plany: sól. Biała, słona, warta fortunę. A gdzieś w lasach czają się zbójcy, "
            "którym marzą się kupieckie wozy...",
            "Zadanie: lokować miasto, rozbudować handel i żupy solne, pomnożyć skarb.",
        ],
        "map": {"seed": 1257, "lakes": [], "river": [(0, 18), (7, 17), (13, 19), (18, 17), (24, 20), (29, 22)],
                "forest": 0.22, "hills": 0.14, "capital": (14, 14),
                "landmarks": [((15, 18), "Wawel", "Wapienne wzgórze nad Wisłą – siedziba książąt i królów. Pod nim jaskinia, w której według legendy mieszkał smok."),
                              ((24, 10), "Wieliczka", "Tu w XIII w. zaczęto wydobywać sól kamienną. Kopalnia działa do dziś i jest na liście UNESCO.")],
                "camps": [((4, 26), "zbojcy", "Kryjówka zbójców", ["e_rozbojnicy", "e_rozbojnicy", "e_lucznicy", "e_rozbojnicy", "e_jazda"])]},
        "start_res": {"food": 24, "wood": 24, "stone": 10, "silver": 14},
        "start_deck": ["woje", "woje", "lucznicy", "lucznicy", "konni", "konni"],
        "turns": 30,
        "objectives": [("tech", "prawo_magd"), ("build", "targ", 3), ("tech", "zupy"), ("build", "zupa", 1), ("res", "silver", 70), ("camp", "zbojcy")],
        "final": None,
        "dialogue_start": [("boleslaw", "Kronikarzu, policz mi dobrze: ile kupców, tyle srebra. Ile srebra, tyle murów."),
                           ("kinga", "A ja przywiozłam z Węgier górników. Szukajcie soli na wzgórzach!"),
                           ("damian", "Lokacja miasta to jak budowa mrowiska: każdy ma swoje miejsce, a razem dźwigają więcej.")],
        "scripted": {5: ("decision", "Kupcy z Wrocławia pytają, czy mogą osiedlić się przy rynku.",
                         [("Tak, zwolnić ich na 5 lat z czynszu (−4 srebra teraz)", {"silver": -4, "food": 6, "wood": 6}, "Wolnizna przyciąga osadników – miasto rośnie!"),
                          ("Tak, ale od razu pobrać opłatę", {"silver": 6}, "Kupcy płacą, ale kręcą nosami.")]),
                     10: ("kinga", "Górnicy znaleźli w bryle soli... mój pierścień! To znak – tu musi powstać żupa!"),
                     18: ("boleslaw", "Zbójcy napadają kupców na traktach. Trzeba ich przepędzić, bo handel zamrze.")},
        "victory": "5 czerwca 1257 r. książę wystawił przywilej lokacyjny. Wójtowie Gedko, Jakub i Dytmar wytyczyli rynek, "
                   "kupcy rozłożyli kramy, a z żup popłynęło srebro. W kronice notuję: „Miasto bez praw to tłum. "
                   "Miasto z prawem to wspólnota.”",
    },
    {
        "id": 3, "epoch": 2, "year": "1331–1333", "place": "Płowce",
        "title": "Rozdział IV: Mała postura, wielkie serce",
        "chronicle": [
            "Roku 1331. Król Władysław Łokietek – niski jak łokieć, uparty jak dąb – zjednoczył kraj. "
            "Ale Zakon Krzyżacki zajął Pomorze Gdańskie i pustoszy Kujawy.",
            "Rycerze w białych płaszczach z czarnymi krzyżami są świetnie uzbrojeni i jeszcze lepiej zorganizowani. "
            "Do walki z nimi trzeba czegoś więcej niż odwagi: kusz, koni i dobrej rady.",
            "Młody królewicz Kazimierz patrzy na ojca z podziwem. Kiedyś zbuduje Polskę murowaną. Ale najpierw – "
            "Płowce. Rozdzielona armia krzyżacka wchodzi prosto w nasz zasięg...",
            "Zadanie: przygotować wojsko, rozbić podjazd krzyżacki, wygrać pod Płowcami i wznieść zamek.",
        ],
        "map": {"seed": 1331, "lakes": [(6, 6, 2), (24, 24, 2)], "river": [(0, 8), (8, 10), (14, 9), (20, 12), (29, 11)],
                "forest": 0.20, "hills": 0.10, "capital": (16, 18),
                "landmarks": [((11, 21), "Brześć Kujawski", "Gród na Kujawach, ojcowizna Łokietka. Kujawy to żyzne ziemie – „spichlerz” Polski."),
                              ((22, 15), "Pole pod Płowcami", "27 września 1331 r. Polacy zaatakowali część armii krzyżackiej. Bitwa nie zakończyła wojny, ale dodała ducha całemu królestwu.")],
                "camps": [((25, 4), "podjazd", "Podjazd krzyżacki", ["e_knechci", "e_kusznicy_z", "e_rycerze_z", "e_knechci"])]},
        "start_res": {"food": 26, "wood": 24, "stone": 12, "silver": 16},
        "start_deck": ["woje", "woje", "lucznicy", "konni", "konni", "druzyna"],
        "turns": 30,
        "objectives": [("build", "koszary", 2), ("tech", "kusza"), ("camp", "podjazd"), ("final",), ("tech", "mury"), ("build", "zamek", 1)],
        "final": {"name": "Bitwa pod Płowcami (1331)", "enemy_morale": 34, "defense": False, "terrain": "field",
                  "deck": ["e_rycerze_z", "e_knechci", "e_kusznicy_z", "e_rycerze_z", "e_knechci", "e_kusznicy_z", "e_rycerze_z"],
                  "allies": [],
                  "intro": "Mgła nad Kujawami. Krzyżacka armia rozdzieliła się – tylna straż maszeruje sama. "
                           "Łokietek unosi miecz. Królewicza Kazimierza odesłano w bezpieczne miejsce. Do boju!"},
        "dialogue_start": [("lokietek", "Mały jestem, kronikarzu, ale jak się zaprę – nie ruszy mnie cały Zakon!"),
                           ("kazimierz", "Ojcze, a gdy wygramy – czy będę mógł budować? Zamki, miasta, szkoły...?"),
                           ("damian", "Królewiczu, kto buduje mury, ten nie musi ciągle wojować. Zapiszę to sobie – i wam.")],
        "scripted": {6: ("decision", "Mieszczanie z Krakowa oferują pożyczkę na wojnę.",
                         [("Przyjąć (+12 srebra, −4 żywności na ucztę dla wierzycieli)", {"silver": 12, "food": -4}, "Pożyczka przyjęta. Kronikarz pilnuje, by ją oddać!"),
                          ("Odmówić – nie lubimy długów", {"wood": 4}, "Damian kiwa głową: „Dług jak ciasto – lubi rosnąć.”")]),
                     12: ("lokietek", "Krzyżacy palą wsie na Kujawach! Ich podjazd stoi na północy – rozbijcie go!"),
                     20: ("kazimierz", "Kronikarzu, gdy będę królem, otoczę kraj murami. Już kreślę plany zamku!")},
        "victory": "Pod Płowcami rycerstwo Łokietka pokazało, że Krzyżaków można pokonać. Dwa lata później królem został "
                   "Kazimierz. Wznosi zamki, mury, mosty. Notuję w kronice: „Zastał Polskę drewnianą, a zostawi murowaną.”",
    },
    {
        "id": 4, "epoch": 3, "year": "1384–1386", "place": "Krewo i Kraków",
        "title": "Rozdział V: Korona i dwa narody",
        "chronicle": [
            "Roku 1384. Na Wawelu koronowano Jadwigę – i to nie na królową, lecz na „króla Polski”! "
            "Ma dziesięć lat, potem jedenaście... a cały kraj czeka, kogo poślubi.",
            "Jej narzeczony z dzieciństwa, Wilhelm Habsburg, przyjechał do Krakowa. Legenda mówi, że Jadwiga chciała "
            "rąbać toporem bramę, by do niego dotrzeć! Ale panowie polscy mają inny plan: Litwa.",
            "Wielki książę Jagiełło włada ogromnym krajem od Bałtyku po Ukrainę. Jeśli przyjmie chrzest i poślubi Jadwigę, "
            "powstanie potęga, przed którą zadrży sam Zakon. Do Krewa ruszają posłowie – a ja z nimi.",
            "Zadanie: zgromadzić dary, poznać sztukę dyplomacji, zbudować kościół dla Litwy i obronić pogranicze.",
        ],
        "map": {"seed": 1385, "lakes": [(6, 10, 3), (20, 5, 2), (24, 20, 3), (10, 24, 2)], "river": [(0, 20), (9, 18), (16, 21), (22, 15), (29, 13)],
                "forest": 0.38, "hills": 0.08, "capital": (15, 13),
                "landmarks": [((20, 10), "Zamek w Krewie", "Tu 14 sierpnia 1385 r. Jagiełło wystawił akt, w którym obiecał przyjęcie chrztu, poślubienie Jadwigi i połączenie Litwy z Koroną."),
                              ((8, 16), "Wilno", "Stolica Litwy. W 1387 r. Jagiełło ochrzcił tu Litwinów i ustanowił biskupstwo.")],
                "camps": [((27, 27), "rejza", "Rejza krzyżacka", ["e_knechci", "e_kusznicy_z", "e_rycerze_z", "e_knechci", "e_rycerze_z", "e_kusznicy_z", "e_rycerze_z"])]},
        "start_res": {"food": 26, "wood": 26, "stone": 12, "silver": 18},
        "start_deck": ["woje", "lucznicy", "konni", "druzyna", "druzyna", "kusznicy"],
        "turns": 30,
        "objectives": [("tech", "dyplomacja"), ("res", "silver", 70), ("build", "kosciol", 2), ("res", "food", 40), ("camp", "rejza")],
        "final": None,
        "dialogue_start": [("jadwiga", "Kronikarzu, serce moje płacze, ale rozum mówi: dla dobra królestwa trzeba czasem wybrać trudniejszą drogę."),
                           ("jagiello", "Przyjmę chrzest i dam Litwie nową drogę. Ale Zakon nie będzie zachwycony – oj, nie będzie."),
                           ("witold", "Bracie, pilnuj granic. Krzyżacy już ostrzą miecze."),
                           ("damian", "Mili moi, dyplomacja to sztuka mówienia „tak” tak, by nikt nie usłyszał „nie”. Zaczynamy!")],
        "scripted": {4: ("decision", "Wilhelm Habsburg żąda zwrotu kosztów podróży... i przeprosin.",
                         [("Zapłacić 6 srebra, niech jedzie w spokoju", {"silver": -6, "morale": 2}, "Wilhelm odjechał. Bez awantury."),
                          ("Odmówić", {"wood": -2}, "Wilhelm odjechał. Z awanturą. Ktoś zostawił w bramie ślad topora...")]),
                     10: ("witold", "Krzyżacka rejza grabi pograniczne wsie. Rozbijcie ją, a Litwa zobaczy, że sojusz się opłaca!"),
                     16: ("jadwiga", "Za nasze srebro sprowadzimy księgi i kapłanów. Litwa otrzyma kościoły i szkoły.")},
        "victory": "W 1386 r. Jagiełło przyjął chrzest jako Władysław, poślubił Jadwigę i został królem Polski. Rok później "
                   "ochrzcił Litwę. W kronice zapisuję: „Dwa narody, jedna droga. Teraz drży Malbork.”",
    },
    {
        "id": 5, "epoch": 3, "year": "1410", "place": "Grunwald",
        "title": "Rozdział VI: Dwa nagie miecze",
        "chronicle": [
            "Roku 1410. Wielka wojna z Zakonem! Król Władysław Jagiełło i wielki książę Witold zbierają armię, "
            "jakiej ta część świata jeszcze nie widziała: Polacy, Litwini, Rusini, Tatarzy, Czesi...",
            "By zaskoczyć Krzyżaków, wojsko przeprawia się przez Wisłę pod Czerwińskiem po moście łyżwowym – "
            "zbudowanym w tajemnicy w puszczy. Kronikarz pędzi za taborem z kałamarzem w zębach.",
            "15 lipca. Upał. Pola między Grunwaldem a Stębarkiem. Krzyżacy czekają w szyku. Król słucha mszy, "
            "a rycerstwo śpiewa Bogurodzicę. Wtedy przybywają heroldowie z dwoma nagimi mieczami...",
            "Zadanie: zaopatrzyć armię, opanować technikę wojenną i poprowadzić radę wojenną pod Grunwaldem.",
        ],
        "map": {"seed": 1410, "lakes": [(5, 6, 2), (25, 8, 3), (8, 25, 2)], "river": [(0, 26), (8, 23), (15, 25), (22, 23), (29, 24)],
                "forest": 0.30, "hills": 0.07, "capital": (13, 13),
                "landmarks": [((18, 17), "Pola Grunwaldu", "Tu stoczono jedną z największych bitew średniowiecznej Europy. Dziś co roku odbywa się tu inscenizacja."),
                              ((6, 20), "Czerwińsk", "Przeprawa przez Wisłę po moście łyżwowym (30 czerwca – 2 lipca 1410 r.).")],
                "camps": [((24, 4), "dabrowno", "Gród Dąbrówno", ["e_knechci", "e_kusznicy_z", "e_knechci", "e_bombarda_z", "e_rycerze_z", "e_rycerze_z", "e_kusznicy_z"])]},
        "start_res": {"food": 30, "wood": 30, "stone": 14, "silver": 22},
        "start_deck": ["woje", "lucznicy", "konni", "druzyna", "kusznicy", "rycerze", "rycerze"],
        "turns": 32,
        "objectives": [("tech", "most"), ("build", "koszary", 2), ("res", "food", 70), ("camp", "dabrowno"), ("final",)],
        "final": {"name": "Bitwa pod Grunwaldem (15 VII 1410)", "enemy_morale": 50, "defense": False, "terrain": "field",
                  "deck": ["e_rycerze_z", "e_kusznicy_z", "e_bombarda_z", "e_knechci", "e_rycerze_z", "e_wielki_mistrz",
                           "e_knechci", "e_rycerze_z", "e_kusznicy_z", "e_wielki_mistrz"],
                  "allies": ["litwini", "litwini"],
                  "intro": "Heroldowie wbijają w ziemię dwa nagie miecze: „Wielki Mistrz przesyła je na pomoc, byście się nie "
                           "ukrywali w lasach!” Król odpowiada spokojnie: „Mieczów mamy dość, ale i te przyjmuję.” Zaczyna się..."},
        "dialogue_start": [("jagiello", "Kronikarzu, wojna to przede wszystkim chleb, wozy i mosty. Rycerze sami przyjdą."),
                           ("witold", "Moje chorągwie są szybkie. Jeśli trzeba, udamy ucieczkę i wrócimy, gdy wróg się rozproszy."),
                           ("zawisza", "Daj mi tylko pole i przeciwnika, a resztę zrobi kopia."),
                           ("damian", "„Polegać jak na Zawiszy” – zapiszę to. Myślę, że to powiedzenie przetrwa wieki.")],
        "scripted": {5: ("decision", "Witold proponuje zebrać zapasy z litewskich ziem.",
                         [("Zgoda (+12 żywności, −4 srebra)", {"food": 12, "silver": -4}, "Wozy z kaszą i solonym mięsem ciągną do taboru."),
                          ("Kupić u kupców gdańskich... (−10 srebra, +16 żywności)", {"silver": -10, "food": 16}, "Drogo, ale dużo.")]),
                     12: ("zawisza", "Krzyżacka załoga w Dąbrównie zagradza drogę. Zdobądźmy gród!"),
                     22: ("jagiello", "Wywiadowcy widzą chorągwie Zakonu na polach pod Grunwaldem. Wkrótce rozstrzygnięcie.")},
        "victory": "Wielki Mistrz Ulrich von Jungingen poległ, a armia Zakonu została rozbita. 51 krzyżackich chorągwi "
                   "zawisło w katedrze na Wawelu. Kronikę zamykam z drżeniem pióra: „Od Gniezna do Grunwaldu – "
                   "długa droga. Ale przeszliśmy ją razem.”",
    },
]

ENDING = [
    "Tak kończy się kronika Damiana Ścisła, doradcy książąt i królów.",
    "Od drewnianych grodów Polan, przez rozbite dzielnice i lokowane miasta, po murowane zamki i potęgę Jagiellonów – "
    "przeszliśmy prawie pięćset lat historii.",
    "Pamiętaj, czytelniku: państwo budują nie tylko miecze. Budują je pola i młyny, targi i prawa, szkoły i mądre rady.",
    "A kronikarz? Odkłada pióro, poprawia fioletowy kaptur i rusza w dalszą drogę. Kto wie, może spotkamy się w następnej epoce...",
]
