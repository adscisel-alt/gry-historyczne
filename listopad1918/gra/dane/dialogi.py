"""Drzewka dialogowe.

Węzeł: {"kto": postać, "tekst": ..., "opcje": [{"tekst", "dalej", "efekty", "gdy"}],
        "dalej": węzeł (gdy brak opcji), "efekty": [...] (przy wejściu),
        "jesli": [{"gdy": [...], "dalej": ...}] (przekierowanie przy wejściu)}.
"dalej": "koniec" zamyka rozmowę.
"""

DIALOGI = {
    # ================================================================ ROZDZIAŁ 1
    "d_damian_start": {"start": "a", "wezly": {
        "a": {"kto": "damian", "tekst": "O, jesteś! Janek, prawda? Harcerz, łącznik, 14 lat, z Warszawy. "
                                         "Tak napisano w twojej teczce. Ja jestem Damian Ściseł. Pilnuję tu pocztówek z 1918 roku.",
              "opcje": [
                  {"tekst": "Dlaczego ma pan fioletowy kaptur?", "dalej": "kaptur"},
                  {"tekst": "Jakich pocztówek?", "dalej": "pocztowki"},
              ]},
        "kaptur": {"kto": "damian", "tekst": "Bo w archiwum wszystko jest brązowe. Gdybym nosił brąz, pomyliłbyś mnie z szafą. "
                                              "A poważnie: fiolet to kolor weryfikacji. Ja sprawdzam, co jest faktem, a co mitem.",
                   "dalej": "pocztowki"},
        "pocztowki": {"kto": "damian", "tekst": "Każda pocztówka to jeden dzień jesieni 1918 roku. Jak włożysz ją do stereoskopu, "
                                                 "trafisz do środka. Zobaczysz, jak rodzi się państwo — nie w jeden dzień, tylko w cały miesiąc.",
                      "opcje": [
                          {"tekst": "Jak to „nie w jeden dzień”? Przecież 11 listopada…", "dalej": "mit"},
                          {"tekst": "Brzmi jak przygoda. Gdzie zaczynamy?", "dalej": "start"},
                      ]},
        "mit": {"kto": "damian", "tekst": "Ha! Pierwszy mit złapany. Wrócimy do niego na końcu rozdziału. "
                                           "Na razie zapamiętaj: historia rzadko trzyma się kalendarza ze szkolnej akademii.",
                "dalej": "start"},
        "start": {"kto": "damian", "tekst": "Zaczynamy od Krakowa. Weź lupę z półki, wyjmij pocztówkę z szuflady "
                                             "i włóż ją do stereoskopu. Instrukcja obsługi historii, wersja 1918.",
                  "efekty": ["flag:rozmowa_damian"], "dalej": "koniec"},
    }},
    "d_witos": {"start": "a", "wezly": {
        "a": {"kto": "witos", "tekst": "A ty skąd, chłopcze? Z Warszawy? Kawał drogi. Tu, w Krakowie, Austriacy właśnie się pakują. "
                                        "Jestem Witos, z Wierzchosławic. Przewodniczę Polskiej Komisji Likwidacyjnej.",
              "opcje": [
                  {"tekst": "Likwidacyjnej? Co pan likwiduje?", "dalej": "likw"},
                  {"tekst": "Pan jest chłopem i rządzi Krakowem?", "dalej": "chlop"},
              ]},
        "likw": {"kto": "witos", "tekst": "Władzę austriacką! Przejmujemy urzędy, pocztę, kolej, żeby ludzie mieli co jeść "
                                           "i żeby był porządek. Nie każda rewolucja musi mieć barykady. Czasem wystarczy pieczątka.",
                 "efekty": ["fakt:pkl_krakow"], "dalej": "zabory"},
        "chlop": {"kto": "witos", "tekst": "Chłopów jest w Polsce najwięcej. Jak wieś nie uwierzy, że to jej państwo, "
                                            "to nic z tego nie będzie. Ja uczyłem się sam, przy lampie naftowej. Da się.",
                  "dalej": "zabory"},
        "zabory": {"kto": "witos", "tekst": "Ale powiedz mi, warszawiaku: czy ty w ogóle wiesz, gdzie leżą nasze ziemie? "
                                             "Ktoś zerwał nazwy miast z mapy na słupie. Popraw ją, to pogadamy dalej.",
                   "efekty": ["flag:rozmowa_witos"], "dalej": "koniec"},
    }},
    "d_witos_mapa": {"start": "a", "wezly": {
        "a": {"kto": "witos", "tekst": "No proszę! Kraków, Lwów i Przemyśl u Austriaków, Poznań i Gdańsk u Prusaków, "
                                        "Warszawa, Lublin i Wilno u Rosjan. Trzy różne prawa, trzy waluty, trzy armie. "
                                        "A teraz trzeba z tego zszyć jedno państwo.",
              "dalej": "b"},
        "b": {"kto": "witos", "tekst": "Masz, weź orzełka. Żołnierze przypinają je zamiast austriackich bączków. "
                                        "I wracaj do Warszawy — tam się dopiero zacznie.",
              "efekty": ["daj:orzelek"], "dalej": "koniec"},
    }},
    # ================================================================ ROZDZIAŁ 2
    "d_staszek": {"start": "a", "wezly": {
        "a": {"kto": "druh_staszek", "tekst": "Czuwaj, Janek! Mam zadanie. Ten meldunek musi trafić do Rady Regencyjnej. "
                                               "Do rąk własnych regentów, nie woźnego.",
              "opcje": [
                  {"tekst": "Czuwaj! A kto w ogóle jest w tej Radzie?", "dalej": "rr"},
                  {"tekst": "Co jest w kopercie?", "dalej": "koperta"},
              ]},
        "rr": {"kto": "druh_staszek", "tekst": "Arcybiskup Kakowski, książę Lubomirski i pan Ostrowski. Jedni mówią, że to "
                                                "ludzie Niemców, inni, że budują nam państwo. Sam ich zapytaj — po to jesteś łącznikiem.",
               "dalej": "zadanie"},
        "koperta": {"kto": "druh_staszek", "tekst": "Gdybym wiedział, to nie byłaby tajemnica. Łącznik nie czyta, łącznik doręcza.",
                    "dalej": "zadanie"},
        "zadanie": {"kto": "druh_staszek", "tekst": "Weź opaskę z haka. Bez niej woźny cię nie wpuści. Powodzenia!",
                    "efekty": ["daj:meldunek", "flag:misja_rr"], "dalej": "koniec"},
    }},
    "d_regenci": {"start": "a", "wezly": {
        "a": {"kto": "kakowski", "tekst": "Witaj, synu. Rada Regencyjna obraduje, ale łącznika zawsze wysłuchamy. "
                                           "Czego chcesz się dowiedzieć?",
              "opcje": [
                  {"tekst": "Czy Rada Regencyjna chce niepodległej Polski?", "dalej": "niep"},
                  {"tekst": "Ludzie mówią, że słuchacie Niemców. To prawda?", "dalej": "niemcy"},
                  {"tekst": "Co będzie, gdy przyjdzie Piłsudski?", "dalej": "pilsudski"},
                  {"tekst": "Dziękuję, nie przeszkadzam.", "dalej": "koniec"},
              ]},
        "niep": {"kto": "kakowski", "tekst": "7 października ogłosiliśmy orędzie do Narodu Polskiego: chcemy niepodległego państwa "
                                              "ze wszystkich ziem polskich i z dostępem do morza. Mamy już sądy, szkoły i urzędników.",
                 "efekty": ["fakt:rr_oredzie", "fakt:rr_sklad"], "dalej": "a"},
        "niemcy": {"kto": "kakowski", "tekst": "Powołali nas okupanci, to prawda. Krytycy mają tu rację. Ale my używamy "
                                                "tej władzy, żeby przygotować polskie urzędy. Oceni nas historia — i pewnie oceni różnie.",
                   "dalej": "a"},
        "pilsudski": {"kto": "kakowski", "tekst": "Jeśli wróci, a Bóg da, że wróci, trzeba będzie mądrze przekazać władzę. "
                                                   "Bez rozlewu krwi i bez wojny między Polakami. Książę Lubomirski myśli podobnie.",
                      "dalej": "a"},
    }},
    "d_lubomirski": {"start": "a", "wezly": {
        "a": {"kto": "lubomirski", "tekst": "Meldunek od harcerzy… Patrzcie państwo: POW donosi, że Niemcy w Warszawie "
                                             "tracą ducha, a ich żołnierze zakładają rady jak w Rosji. Ciekawe czasy, młody człowieku.",
              "opcje": [
                  {"tekst": "Czy to dobrze, że Niemcy tracą ducha?", "dalej": "b"},
                  {"tekst": "Czy mogę dostać coś na pamiątkę?", "dalej": "c"},
              ]},
        "b": {"kto": "lubomirski", "tekst": "Dobrze — jeśli nie zaczną strzelać ze strachu. Wojsko bez rozkazów to jak dorożka "
                                             "bez woźnicy. Dlatego potrzebujemy kogoś, kogo żołnierze posłuchają.",
              "dalej": "c"},
        "c": {"kto": "lubomirski", "tekst": "Weź odpis naszego orędzia z 7 października. Pokazuj go tym, którzy mówią, "
                                             "że Rada nic nie zrobiła. A potem jedź do Lublina — tam podobno powstaje jakiś rząd. "
                                             "Kolejny! W tym tygodniu rządów jest więcej niż tramwajów.",
              "efekty": ["daj:odpis_oredzia", "fakt:rr_oredzie"], "dalej": "koniec"},
    }},
    "d_lubomirski_powt": {"start": "a", "wezly": {
        "a": {"kto": "lubomirski", "tekst": "Pozdrów Lublin. I pamiętaj: każdy obóz uważa, że to on ma rację. Czasem wszyscy trochę mają.",
              "dalej": "koniec"},
    }},
    "d_ostrowski": {"start": "a", "wezly": {
        "a": {"kto": "ostrowski", "tekst": "Państwo, chłopcze, to nie tylko flagi. To urzędnik, który rano otworzy biuro, "
                                            "sędzia, który wyda wyrok, i nauczyciel, który zacznie lekcję po polsku.",
              "opcje": [
                  {"tekst": "A to wszystko już działa?", "dalej": "b"},
                  {"tekst": "Brzmi nudno.", "dalej": "c"},
              ]},
        "b": {"kto": "ostrowski", "tekst": "Od roku tworzymy polskie sądy i szkoły. Gdy przyjdzie dzień przekazania władzy, "
                                            "nowy rząd nie zacznie od zera.",
              "efekty": ["fakt:rr_sklad"], "dalej": "koniec"},
        "c": {"kto": "ostrowski", "tekst": "Nudne rzeczy trzymają świat w całości. Spróbuj żyć bez poczty przez tydzień.",
              "dalej": "koniec"},
    }},
    # ================================================================ ROZDZIAŁ 3
    "d_daszynski": {"start": "a", "wezly": {
        "a": {"kto": "daszynski", "tekst": "Kto to? Harcerz z Warszawy? Świetnie, potrzebuję szybkich nóg! "
                                            "Jestem Daszyński. Dziś w nocy ogłaszamy Tymczasowy Rząd Ludowy Republiki Polskiej.",
              "opcje": [
                  {"tekst": "Republiki? A nie królestwa?", "dalej": "rep"},
                  {"tekst": "Co chcecie zmienić?", "dalej": "program"},
              ]},
        "rep": {"kto": "daszynski", "tekst": "Żadnych królów! Państwo ma należeć do ludu — do robotników, chłopów, inteligencji. "
                                              "Rada Regencyjna w Warszawie? Szanujemy ich pracę, ale ich władza pochodzi od okupantów.",
                "dalej": "program"},
        "program": {"kto": "daszynski", "tekst": "Osiem godzin pracy zamiast dwunastu. Ziemia dla tych, którzy na niej pracują. "
                                                  "I prawa wyborcze dla wszystkich — także dla kobiet! Konserwatyści mówią, że za szybko. "
                                                  "My mówimy: i tak za późno.",
                    "opcje": [
                        {"tekst": "Dlaczego jedni mówią „za szybko”?", "dalej": "szybko"},
                        {"tekst": "W czym mogę pomóc?", "dalej": "zlecenie"},
                    ]},
        "szybko": {"kto": "daszynski", "tekst": "Bo boją się chaosu i rewolucji jak w Rosji. Mają do tego prawo — w Rosji "
                                                 "bolszewicy właśnie pokazali, jak to może się skończyć. My chcemy reform, nie terroru.",
                   "dalej": "zlecenie"},
        "zlecenie": {"kto": "daszynski", "tekst": "Leć do drukarni za rogiem. Zecer ma rozsypany tekst manifestu. "
                                                   "Pomóż mu go złożyć — i przynieś mi pierwszą odbitkę!",
                     "efekty": ["flag:zlecenie_daszynski"], "dalej": "koniec"},
    }},
    "d_daszynski_koniec": {"start": "a", "wezly": {
        "a": {"kto": "daszynski", "tekst": "Jest! „Lud polski!” — tak zaczynamy. Republika, równe prawa bez różnicy płci, "
                                            "osiem godzin pracy, reforma rolna, Sejm Ustawodawczy. Pięknie złożone, chłopcze.",
              "dalej": "b"},
        "b": {"kto": "daszynski", "tekst": "Zobaczysz — kiedy przyjedzie Piłsudski, oddamy mu władzę. Nie chodzi o to, kto rządzi, "
                                            "tylko żeby Polska była sprawiedliwa. Jak to mówią w Galicji: lepszy wspólny rząd niż trzy osobne kłótnie.",
              "efekty": ["flag:manifest_oddany"], "dalej": "koniec"},
    }},
    "d_rydz": {"start": "a", "wezly": {
        "a": {"kto": "rydz", "tekst": "Rydz-Śmigły, komendant POW. W tym rządzie jestem ministrem wojny. "
                                       "Wojny, której nikt nie chce, ale na którą trzeba być gotowym.",
              "opcje": [
                  {"tekst": "Co to jest POW?", "dalej": "pow"},
                  {"tekst": "Podobno pan maluje?", "dalej": "maluje"},
              ]},
        "pow": {"kto": "rydz", "tekst": "Polska Organizacja Wojskowa. Tajna armia Piłsudskiego. Nauczyciele, studenci, robotnicy, "
                                         "harcerze. W dzień zwykli ludzie, w nocy — żołnierze. Wkrótce będziemy rozbrajać okupantów.",
                "dalej": "koniec"},
        "maluje": {"kto": "rydz", "tekst": "Studiowałem malarstwo w Krakowie. Wolę pędzel od karabinu, ale pędzlem Niemców nie rozbroisz. "
                                            "Chociaż… gdyby pomalować im koszary na biało-czerwono?",
                   "dalej": "pow"},
    }},
    "d_zecer": {"start": "a", "wezly": {
        "a": {"kto": "zecer", "tekst": "Oj, panie harcerzu, katastrofa! Mówcy dyktowali, kartki pofrunęły, a ja mam rozsypany "
                                        "manifest. Do tego ktoś podrzucił dwa fałszywe zdania. Trzeba to złożyć po kolei.",
              "opcje": [
                  {"tekst": "Pomogę! Jak się składa manifest?", "dalej": "jak"},
                  {"tekst": "A jaki hymn wydrukować na dole?", "dalej": "hymn"},
              ]},
        "hymn": {"kto": "zecer", "tekst": "Hymn? Jedni śpiewają „Mazurka”, drudzy „Rotę”, trzeci „Boże, coś Polskę”. "
                                           "Nikt jeszcze nie zdecydował, który jest oficjalny. Zostawmy miejsce na później.",
                 "efekty": ["fakt:hymn_1927"], "dalej": "jak"},
        "jak": {"kto": "zecer", "tekst": "Zasada stara jak druk: najpierw kto mówi, potem czym jest państwo, potem prawa ludzi, "
                                          "praca, ziemia, a na końcu wezwanie. Fałszywki — do pieca! Kaszta jest tam.",
                "efekty": ["flag:rozmowa_zecer"], "dalej": "koniec"},
    }},
    # ================================================================ ROZDZIAŁ 4
    "d_pilsudski": {"start": "a", "wezly": {
        "a": {"kto": "pilsudski", "tekst": "Harcerz w pociągu z Berlina? Niemcy wypuszczają ze swoich więzień dziwnych ludzi. "
                                            "Siadaj, chłopcze. Herbaty nie mam. Kawy też nie. Mam tylko czas do Warszawy.",
              "opcje": [
                  {"tekst": "Jak było w Magdeburgu?", "dalej": "magd"},
                  {"tekst": "Co pan zrobi w Warszawie?", "dalej": "plan"},
                  {"tekst": "Czy pan się zgadza z Dmowskim?", "dalej": "dmowski"},
              ]},
        "magd": {"kto": "pilsudski", "tekst": "Nudno. Ponad rok w twierdzy, z Sosnkowskim i szachami. Niemcy zamknęli mnie, "
                                               "bo moi legioniści nie chcieli przysięgać wierności cesarzowi. Wypuścili 8 listopada, "
                                               "bo im się cesarstwo rozpada.",
                 "efekty": ["fakt:magdeburg"], "dalej": "a2"},
        "plan": {"kto": "pilsudski", "tekst": "Najpierw wojsko. Państwo bez armii to obietnica, nie państwo. Potem rząd, "
                                               "w którym zmieszczą się różni ludzie. I żeby Niemcy wyjechali do domu bez wojny w mieście.",
                 "dalej": "a2"},
        "dmowski": {"kto": "pilsudski", "tekst": "Dmowski uważa, że głównym wrogiem są Niemcy, ja — że Rosja. Obaj chcemy Polski, "
                                                  "tylko inaczej liczymy na mapie. Może i dobrze, że jest nas dwóch: on w Paryżu, ja tutaj.",
                    "dalej": "a2"},
        "a2": {"kto": "pilsudski", "tekst": "Coś jeszcze, chłopcze? Za oknem już polskie pola.",
               "opcje": [
                   {"tekst": "Jak było w Magdeburgu?", "dalej": "magd", "gdy": ["!fakt:magdeburg"]},
                   {"tekst": "Co pan zrobi w Warszawie?", "dalej": "plan"},
                   {"tekst": "Czy pan się zgadza z Dmowskim?", "dalej": "dmowski"},
                   {"tekst": "Nie, dziękuję. Niech pan odpocznie.", "dalej": "koniec_r"},
               ]},
        "koniec_r": {"kto": "pilsudski", "tekst": "Ty też. Jutro… to znaczy dziś… będzie długi dzień. Sprawdź rozkład — o której będziemy?",
                     "efekty": ["flag:rozmowa_pilsudski"], "dalej": "koniec"},
    }},
    "d_koc": {"start": "a", "wezly": {
        "a": {"kto": "koc", "tekst": "Harcerz! Doskonale. Jestem Koc, komendant POW w Warszawie. Komendant zaraz wysiądzie, "
                                      "a przy bramce na peron tłum. Wpuszczamy tylko tych, którzy mają prawo tam być.",
              "dalej": "b"},
        "b": {"kto": "koc", "tekst": "Zasady: data 10 XI 1918, pieczęć POW albo Rady Regencyjnej, nazwisko z listy powitalnej, "
                                      "podpis. Niemieckie przepustki dziś nie działają. Fałszerzy zatrzymuj — grzecznie!",
              "efekty": ["flag:rozmowa_koc"], "dalej": "koniec"},
    }},
    "d_lubomirski_dworzec": {"start": "a", "wezly": {
        "a": {"kto": "lubomirski", "tekst": "Znowu ty! Łącznik od orędzia. Właśnie przywitałem Komendanta w imieniu Rady Regencyjnej. "
                                             "Mróz, mgła, a on mówi jakby nic: „Dzień dobry, panowie”.",
              "dalej": "b"},
        "b": {"kto": "lubomirski", "tekst": "Jutro Rada przekaże mu dowództwo nad wojskiem. Wiem, że niektórzy w Radzie się wahają. "
                                             "Ale lepiej oddać władzę mądrze, niż czekać, aż ktoś ją wyrwie.",
              "efekty": ["flag:powitanie_ok", "fakt:powrot_10xi"], "dalej": "koniec"},
    }},
    # ================================================================ ROZDZIAŁ 5
    "d_koc_plan": {"start": "a", "wezly": {
        "a": {"kto": "koc", "tekst": "Janek, dziś w nocy rozbrajamy Niemców. Pięć punktów w mieście. Kolejność jest kluczowa — "
                                      "jeden błąd i ktoś zacznie strzelać. Ułóż plan na stole. Wskazówki masz na marginesie.",
              "dalej": "koniec"},
    }},
    "d_otto": {"start": "a", "wezly": {
        "a": {"kto": "otto", "tekst": "Halt! Stój! Kto idzie? …Kind? Dziecko? Was willst du? Czego chcesz?",
              "opcje": [
                  {"tekst": "(spokojnie) Dobry wieczór. Chcę tylko porozmawiać.", "dalej": "b"},
                  {"tekst": "(krzyk) Ręce do góry, jesteś otoczony!", "dalej": "b_zle", "efekty": ["napiecie:+1"]},
              ]},
        "b_zle": {"kto": "otto", "tekst": "Was?! Otoczony?! (Karabin drży mu w rękach. Z okna koszar wychyla się ktoś drugi.)",
                  "jesli": [{"gdy": ["napiecie>=2"], "dalej": "przewin"}],
                  "opcje": [
                      {"tekst": "Przepraszam! Żart. Głupi żart. Chcę tylko porozmawiać.", "dalej": "b"},
                      {"tekst": "(jeszcze głośniej) Polacy, naprzód!", "dalej": "b_zle", "efekty": ["napiecie:+1"]},
                  ]},
        "b": {"kto": "otto", "tekst": "Rozmawiać… Gut. Jestem Otto. Z Lipska. Cztery lata wojny. Nasza Rada Żołnierska mówi: "
                                       "cesarz uciekł, wojna skończona. Ale oficer mówi: broni nie oddawać.",
              "opcje": [
                  {"tekst": "Nasz Komendant umówił się z waszą Radą Żołnierską. Wyjedziecie bezpiecznie.", "dalej": "c"},
                  {"tekst": "Jak nie oddasz broni, będzie źle.", "dalej": "c_zle", "efekty": ["napiecie:+1"]},
              ]},
        "c_zle": {"kto": "otto", "tekst": "Grozisz mi? Mnie? Ja przeżyłem Verdun! (Słychać szczęk zamka karabinu za bramą.)",
                  "jesli": [{"gdy": ["napiecie>=2"], "dalej": "przewin"}],
                  "opcje": [
                      {"tekst": "Nie grożę. Chcę, żebyś wrócił do Lipska żywy.", "dalej": "c"},
                      {"tekst": "Tak, grożę!", "dalej": "c_zle", "efekty": ["napiecie:+1"]},
                  ]},
        "c": {"kto": "otto", "tekst": "Do domu… Pociągiem? A jak oddam karabin, kto mi zagwarantuje, że nikt nie strzeli mi w plecy?",
              "opcje": [
                  {"tekst": "Dworzec już jest pod naszą opieką. Pociągi do Niemiec odjeżdżają co kilka godzin.", "dalej": "d"},
                  {"tekst": "Nikt. Musisz zaryzykować.", "dalej": "d_zle", "efekty": ["napiecie:+1"]},
              ]},
        "d_zle": {"kto": "otto", "tekst": "Zaryzykować… Ryzykowałem cztery lata! (Otto cofa się pod bramę. Napięcie rośnie.)",
                  "jesli": [{"gdy": ["napiecie>=2"], "dalej": "przewin"}],
                  "opcje": [
                      {"tekst": "Przepraszam. Dworzec jest nasz, pociągi czekają. Słowo harcerza.", "dalej": "d"},
                  ]},
        "d": {"kto": "otto", "tekst": "Słowo harcerza… Mój młodszy brat też jest w Wandervogel. To jak wasi harcerze. "
                                       "(Długa cisza.) Gut. Bitte. Proszę. Weź go. Tylko powiedz swoim, żeby nie strzelali.",
              "dalej": "e"},
        "e": {"kto": "koc", "tekst": "Spokojnie, panowie, spokojnie! Broń na wóz, żołnierze na dworzec. Janek — ani jednego strzału. "
                                      "Wiesz, ilu ludzi dziś przeżyło, bo ktoś mówił, a nie krzyczał?",
              "efekty": ["flag:rozbrojenie_ok", "napiecie:0"], "dalej": "koniec"},
        "przewin": {"kto": "damian", "tekst": "STOP! Przewijam pocztówkę. Uff. W prawdziwej historii zdarzały się strzelaniny "
                                               "z powodu jednego nerwowego krzyku. Spróbujmy jeszcze raz — tym razem spokojniej.",
                    "efekty": ["napiecie:0"], "dalej": "a"},
    }},
    "d_zawadzka": {"start": "a", "wezly": {
        "a": {"kto": "zawadzka", "tekst": "Harcerz! Ty byłeś na dworcu, prawda? Piszę artykuł o ostatnich dniach, a moi świadkowie "
                                           "opowiadają cuda. Pomóż mi oddzielić fakty od bajek.",
              "dalej": "b"},
        "b": {"kto": "zawadzka", "tekst": "Wysłucham ich jeszcze raz. Ty wskaż, kto mówi nieprawdę, i pokaż dowód z twojej torby. "
                                           "Bez dowodu to tylko słowo przeciw słowu.",
              "efekty": ["flag:rozmowa_zawadzka"], "dalej": "koniec"},
    }},
    # ================================================================ ROZDZIAŁ 6
    "d_dmowski": {"start": "a", "wezly": {
        "a": {"kto": "dmowski", "tekst": "Polski harcerz w Paryżu? To się nazywa propaganda wizualna. Roman Dmowski, "
                                          "Komitet Narodowy Polski. Siadaj, ale niczego nie ruszaj — to mapy na konferencję pokojową.",
              "opcje": [
                  {"tekst": "Dlaczego pan działa w Paryżu, a nie w Polsce?", "dalej": "paryz"},
                  {"tekst": "Co pan myśli o Piłsudskim?", "dalej": "pilsudski"},
                  {"tekst": "Na czym polega pana plan?", "dalej": "plan"},
              ]},
        "paryz": {"kto": "dmowski", "tekst": "Bo tu zapadną decyzje o granicach. Wojnę wygrała Ententa: Francja, Anglia i Ameryka. "
                                              "Kto chce mieć granice, musi mieć przyjaciół przy stole. Francja, Anglia, Włochy i USA "
                                              "uznały nasz Komitet. Mamy też własną armię we Francji — Błękitną Armię.",
                  "efekty": ["fakt:knp_uznanie", "fakt:haller"], "dalej": "a2"},
        "pilsudski": {"kto": "dmowski", "tekst": "Piłsudski walczył u boku Austrii, a ja zawsze uważałem, że największe zagrożenie to Niemcy. "
                                                  "Mamy różne drogi. Ale jeśli Polska ma przetrwać, Warszawa i Paryż muszą się dogadać. "
                                                  "Powtórz mu to, jeśli go spotkasz.",
                      "dalej": "a2"},
        "plan": {"kto": "dmowski", "tekst": "Przekonać aliantów, że silna Polska to zapora między Niemcami a Rosją. "
                                             "I że należą się nam ziemie, gdzie mieszkają Polacy — także Wielkopolska, Pomorze z Gdańskiem i Śląsk.",
                 "dalej": "a2"},
        "a2": {"kto": "dmowski", "tekst": "Masz jeszcze pytania? Mam mało czasu i dużo map.",
               "opcje": [
                   {"tekst": "Dlaczego pan działa w Paryżu?", "dalej": "paryz", "gdy": ["!fakt:knp_uznanie"]},
                   {"tekst": "Co pan myśli o Piłsudskim?", "dalej": "pilsudski"},
                   {"tekst": "Na czym polega pana plan?", "dalej": "plan"},
                   {"tekst": "Pomogę w salonie dyplomatów!", "dalej": "salon"},
               ]},
        "salon": {"kto": "dmowski", "tekst": "Dobrze. Ale najpierw porozmawiaj z Paderewskim — on zna Amerykanów lepiej niż ja. "
                                              "Tylko nie mów mu, że pochwaliłem jego koncerty. Zrobi się nieznośny.",
                  "efekty": ["flag:rozmowa_dmowski"], "dalej": "koniec"},
    }},
    "d_paderewski": {"start": "a", "wezly": {
        "a": {"kto": "damian", "tekst": "Uwaga, wtrącam się! Paderewski w listopadzie 1918 r. był jeszcze w Ameryce. "
                                         "Z Dmowskim spotka się w Paryżu dopiero na konferencji pokojowej w 1919 r. "
                                         "Dlatego rozmawiasz z nim przez pocztówkę z Nowego Jorku. Archiwista wszystko widzi.",
              "dalej": "b"},
        "b": {"kto": "paderewski", "tekst": "Halo? Słychać mnie? Ach, harcerz! Ignacy Jan Paderewski. Gram Chopina dla Amerykanów, "
                                             "a między koncertami przekonuję ich, że Polska musi być wolna.",
              "opcje": [
                  {"tekst": "Muzyką można zrobić politykę?", "dalej": "muzyka"},
                  {"tekst": "Zna pan prezydenta Wilsona?", "dalej": "wilson"},
              ]},
        "muzyka": {"kto": "paderewski", "tekst": "Muzyka otwiera drzwi. Kiedy sala wstaje po koncercie, mogę powiedzieć dwa zdania o Polsce "
                                                  "i nikt nie wychodzi. Zebrałem też pieniądze dla głodujących w kraju.",
                   "dalej": "wilson"},
        "wilson": {"kto": "paderewski", "tekst": "Rozmawiałem z nim wiele razy. W styczniu ogłosił swoje 14 punktów — trzynasty mówi "
                                                  "o niepodległej Polsce z wolnym dostępem do morza. Ładniejszej melodii nie słyszałem.",
                   "efekty": ["fakt:wilson_13"], "dalej": "c"},
        "c": {"kto": "paderewski", "tekst": "Weź tę depeszę z argumentami dla Amerykanów. I pozdrów Dmowskiego. Kłócimy się czasem, "
                                             "ale to jak duet — dwóch pianistów przy jednym fortepianie. Ciasno, ale da się grać.",
              "efekty": ["daj:depesza", "flag:rozmowa_paderewski"], "dalej": "koniec"},
    }},
    # ================================================================ ROZDZIAŁ 7
    "d_korfanty": {"start": "a", "wezly": {
        "a": {"kto": "korfanty", "tekst": "Szczęść Boże! Wojciech Korfanty, Ślązak, a teraz trochę poznaniak. "
                                           "25 października powiedziałem w Reichstagu w Berlinie, że ziemie polskie zaboru pruskiego mają wrócić do Polski.",
              "opcje": [
                  {"tekst": "I co na to Niemcy?", "dalej": "niemcy"},
                  {"tekst": "Czyli Poznań już jest w Polsce?", "dalej": "poznan"},
              ]},
        "niemcy": {"kto": "korfanty", "tekst": "Krzyczeli! Ktoś wołał, że jestem zdrajcą. A ja tylko przypomniałem im 13. punkt "
                                                "Wilsona, który sami przyjęli. Poseł musi mówić prawdę, nawet gdy sala gwiżdże.",
                   "efekty": ["fakt:korfanty_reichstag"], "dalej": "poznan"},
        "poznan": {"kto": "korfanty", "tekst": "Jeszcze nie! Rozejm zakończył walki, ale nie zmienił granic. Tu wciąż rządzą Niemcy. "
                                                "Naczelna Rada Ludowa przygotowuje Wielkopolskę — sejm dzielnicowy, straż ludową, szkoły.",
                   "opcje": [
                       {"tekst": "Dlaczego nie zrobicie tego od razu, jak w Warszawie?", "dalej": "czekanie"},
                       {"tekst": "Co mam przekazać do Warszawy?", "dalej": "przekaz"},
                   ]},
        "czekanie": {"kto": "korfanty", "tekst": "Bo tu Niemców jest dużo, a ich państwo wciąż działa. Jedni mówią: czekajmy na "
                                                  "konferencję pokojową. Inni: chwyćmy za broń. Za miesiąc się okaże, kto miał rację.",
                     "dalej": "przekaz"},
        "przekaz": {"kto": "korfanty", "tekst": "Powiedz, że Wielkopolska, Pomorze i Śląsk też chcą być w Polsce. I żeby o nas nie "
                                                 "zapomnieli przy stole w Paryżu. A teraz leć — w Warszawie dzieje się coś ważnego dla połowy ludzkości.",
                    "efekty": ["flag:rozmowa_korfanty", "fakt:nrl"], "dalej": "koniec"},
    }},
    "d_moraczewska": {"start": "a", "wezly": {
        "a": {"kto": "moraczewska", "tekst": "Harcerz! Wchodź, wchodź. Zofia Moraczewska, Liga Kobiet. Właśnie przynieśli dekret "
                                              "o ordynacji wyborczej. Przeczytaj artykuł pierwszy. Na głos!",
              "dalej": "b"},
        "b": {"kto": "janek", "tekst": "„Wyborcą do Sejmu jest każdy obywatel Państwa bez różnicy płci, który do dnia ogłoszenia "
                                        "wyborów ukończył 21 lat”. Bez różnicy płci… czyli moja mama też będzie głosować?",
              "dalej": "c"},
        "c": {"kto": "moraczewska", "tekst": "Mama, babcia, siostra, kiedy skończy 21 lat. I mogą kandydować do Sejmu! "
                                              "Walczyłyśmy o to latami. Niektórzy panowie wciąż kręcą nosem, ale dekret podpisał Naczelnik "
                                              "i premier — mój mąż, nawiasem mówiąc. W domu mieliśmy długie rozmowy.",
              "opcje": [
                  {"tekst": "Dlaczego niektórzy byli przeciw?", "dalej": "przeciw"},
                  {"tekst": "Czy w innych krajach kobiety już głosują?", "dalej": "swiat"},
              ]},
        "przeciw": {"kto": "moraczewska", "tekst": "Mówili, że kobiety nie znają się na polityce. A kto prowadził sklepy, szpitale "
                                                    "i tramwaje przez cztery lata wojny? Kto szył mundury i ukrywał broń POW?",
                    "dalej": "quiz"},
        "swiat": {"kto": "moraczewska", "tekst": "W Nowej Zelandii od 1893, w Finlandii od 1906. Ale Francuzki, Szwajcarki — jeszcze nie. "
                                                  "Jesteśmy przed wieloma starymi demokracjami!",
                  "dalej": "quiz"},
        "quiz": {"kto": "moraczewska", "tekst": "Sprawdzę, czy uważałeś. Zadam ci kilka pytań — jak na zebraniu Ligi. Kliknij mnie, gdy będziesz gotów.",
                 "efekty": ["flag:rozmowa_moraczewska", "daj:dekret", "fakt:dekret_wyborczy"], "dalej": "koniec"},
    }},
}
