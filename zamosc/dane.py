"""Treść gry: fabuła, postacie, budynki, przedmioty, Księga Wiedzy i zagadki."""
import random

MAPA_W, MAPA_H = 40, 26

# ------------------------------------------------------------------ MAPA
# '.' trawa  'T' las  'R' skały  '~' rzeka  '#' most  '"' bagno  '=' trakt


def zbuduj_mape():
    r = random.Random(1580)
    m = [["." for _ in range(MAPA_W)] for _ in range(MAPA_H)]
    for y in range(MAPA_H):
        for x in range(MAPA_W):
            las = ((x <= 5 and y <= 6) or (29 <= x <= 35 and y <= 2) or (x >= 38 and y <= 9)
                   or (32 <= x <= 35 and y >= 22) or (x <= 2 and 8 <= y <= 12) or (x >= 38 and y >= 20))
            if las and r.random() < .9:
                m[y][x] = "T"
            if (x <= 4 and y >= 21) or (x <= 1 and 15 <= y <= 18):
                m[y][x] = "R"
            if 34 <= x <= 35 and 6 <= y <= 19:
                m[y][x] = '"'
            if x in (36, 37):
                m[y][x] = "~"
    for y in range(0, 3):
        m[y][19] = m[y][20] = "="
    for x in range(33, MAPA_W):
        for y in (14, 15):
            m[y][x] = "#" if x in (36, 37) else "="
    for y in range(22, MAPA_H):
        m[y][14] = m[y][15] = "="
    for x in range(13, 20):  # oś miasta: od pałacu ku rynkowi (wschód–zachód)
        m[11][x] = "="
    return m


# Bastiony — siedmiobok wokół miasta (jak w prawdziwym Zamościu)
BASTIONY = [(26, 4), (33, 11), (30, 19), (20, 22), (10, 19), (7, 11), (14, 4)]

# Działki z planu Bernarda Morando: (typ, x, y) — lewy górny róg
DZIALKI = [("palac", 10, 10), ("rynek", 20, 9), ("ratusz", 22, 9),
           ("akademia", 14, 7), ("kolegiata", 14, 13)]
DZIALKI += [("bastion", x - 1, y - 1) for x, y in BASTIONY]
BRAMY = [("Brama Lubelska", 19, 3), ("Brama Lwowska", 31, 14), ("Brama Szczebrzeska", 14, 20)]
DZIALKI += [("brama", x, y) for _, x, y in BRAMY]

RYNEK = (20, 9, 6, 6)
START = (17, 11)

NPC = {
    "morando": dict(imie="Bernardo Morando", rola="architekt z Padwy", poz=(12, 13)),
    "hagop": dict(imie="Hagop", rola="kupiec ormiański (postać fikcyjna)", poz=(19, 13)),
    "szymonowic": dict(imie="Szymon Szymonowic", rola="poeta i uczony", poz=(17, 8)),
}

# ------------------------------------------------------------------ BUDYNKI
BUDYNKI = {
    "dom": dict(nazwa="Dom mieszczański", w=1, h=1, koszt={"zloto": 15, "drewno": 10}, czas=1,
                mieszk=5, opis="Drewniany dom dla 5 mieszczan. Mieszczanie płacą podatki."),
    "tartak": dict(nazwa="Tartak", w=2, h=2, koszt={"zloto": 25, "drewno": 10}, czas=2,
                   prod={"drewno": 5}, rob=3, wymog="las", opis="Stawiaj przy lesie. Daje 5 drewna na dzień."),
    "kamieniolom": dict(nazwa="Kamieniołom", w=2, h=2, koszt={"zloto": 30, "drewno": 15}, czas=2,
                        prod={"kamien": 4}, rob=4, wymog="skala", opis="Stawiaj przy skałach. Daje 4 kamienie na dzień."),
    "cegielnia": dict(nazwa="Cegielnia", w=2, h=2, koszt={"zloto": 35, "drewno": 15, "kamien": 10}, czas=2,
                      prod={"cegla": 4}, rob=4, wymog="woda",
                      opis="Glinę kopie się nad wodą lub bagnem. Daje 4 cegły na dzień."),
    "kamienica": dict(nazwa="Kamienica", w=2, h=2, koszt={"zloto": 30, "drewno": 10, "kamien": 10, "cegla": 15},
                      czas=3, mieszk=10, handel=3, opis="Murowany dom kupca z podcieniami. 10 mieszczan i handel."),
    "kram": dict(nazwa="Kram kupiecki", w=1, h=1, koszt={"zloto": 10, "drewno": 5}, czas=1, handel=3,
                 wymog="bruk", opis="Stragan na bruku Rynku. Daje 3 zł zysku z handlu na dzień."),
    "palac": dict(nazwa="Pałac Zamoyskich", w=3, h=2, koszt={"zloto": 80, "drewno": 40, "kamien": 30}, czas=4,
                  zabytek=True, opis="Siedziba rodu Zamoyskich — „głowa” miasta, na zachodnim krańcu osi."),
    "rynek": dict(nazwa="Rynek Wielki", w=6, h=6, koszt={"zloto": 40, "kamien": 40}, czas=3, zabytek=True,
                  opis="Wybrukowany plac 100 × 100 m — serce handlu i życia miasta."),
    "ratusz": dict(nazwa="Ratusz", w=2, h=2, koszt={"zloto": 80, "drewno": 30, "kamien": 30, "cegla": 40}, czas=4,
                   zabytek=True, handel=5, opis="Siedziba rady miejskiej z wysoką wieżą. Wymaga gotowego Rynku."),
    "kolegiata": dict(nazwa="Kolegiata", w=2, h=3, koszt={"zloto": 90, "drewno": 30, "kamien": 40, "cegla": 50},
                      czas=5, zabytek=True, min_pw=35, opis="Renesansowa świątynia (dziś katedra). Wymaga 35 PW."),
    "akademia": dict(nazwa="Akademia Zamojska", w=3, h=2, koszt={"zloto": 90, "drewno": 40, "kamien": 30, "cegla": 50},
                     czas=5, zabytek=True, min_pw=50, prod={"pw": 1},
                     opis="Uczelnia założona w 1594 r. Daje 1 PW dziennie. Wymaga 50 PW."),
    "bastion": dict(nazwa="Bastion", w=2, h=2, koszt={"zloto": 25, "kamien": 30, "cegla": 15}, czas=3, zabytek=True,
                    opis="Wysunięte, pięcioboczne umocnienie. Twierdza ma ich 7."),
    "brama": dict(nazwa="Brama miejska", w=2, h=2, koszt={"zloto": 30, "kamien": 25, "cegla": 20}, czas=3,
                  zabytek=True, opis="Wjazd do miasta na trakcie. Są 3: Lubelska, Lwowska, Szczebrzeska."),
}

DOSTEPNE = {
    1: ["dom", "tartak", "kamieniolom", "palac"],
    2: ["dom", "tartak", "kamieniolom", "palac", "cegielnia", "rynek", "ratusz", "kamienica", "kram"],
    3: ["dom", "tartak", "kamieniolom", "palac", "cegielnia", "rynek", "ratusz", "kamienica", "kram",
        "kolegiata", "akademia"],
    4: ["dom", "tartak", "kamieniolom", "palac", "cegielnia", "rynek", "ratusz", "kamienica", "kram",
        "kolegiata", "akademia", "bastion", "brama"],
}

ZASOBY_NAZWY = {"zloto": "złoto", "drewno": "drewno", "kamien": "kamień", "cegla": "cegła", "pw": "PW"}

# ------------------------------------------------------------------ PRZEDMIOTY
PRZEDMIOTY = {
    "kompas": dict(nazwa="Kompas Zamoyskiego", ikona="kompas", uzycie="kompas",
                   opis="Mosiężny kompas z Padwy. Igła to mały magnes — zawsze wskazuje północ. "
                        "Użyj (klawisz K), by pokazać kierunek do celu i działki z planu."),
    "sakiewka": dict(nazwa="Sakiewka dukatów", ikona="sakiewka", uzycie="zuzyj",
                     opis="Dar od króla Stefana Batorego na budowę miasta. Użyj: +60 zł."),
    "prowiant": dict(nazwa="Kosz z prowiantem", ikona="chleb", uzycie="zuzyj",
                     opis="Chleb, ser i miód dla robotników. Użyj: przez 6 dni warsztaty pracują podwójnie."),
    "plan": dict(nazwa="Plan miasta Morando", ikona="plan", uzycie="plan",
                 opis="Rysunek całego miasta: pałac, rynek, akademia, kolegiata i 7 bastionów. "
                      "Użyj, by obejrzeć plan."),
    "przywilej": dict(nazwa="Przywilej lokacyjny", ikona="przywilej", uzycie=None,
                      opis="Dokument z 3 kwietnia 1580 r. z pieczęcią. Daje miastu prawa. Stale: podatki +25%."),
    "waga": dict(nazwa="Waga kupiecka", ikona="waga", uzycie=None,
                 opis="Prezent od Hagopa. Uczciwa waga to podstawa handlu. Stale: zysk z handlu +50%."),
    "cyrkiel": dict(nazwa="Cyrkiel architekta", ikona="cyrkiel", uzycie=None,
                    opis="Cyrkiel Morando do kreślenia łuków i okręgów. Stale: budowle tańsze o 15%."),
    "pioro": dict(nazwa="Gęsie pióro poety", ikona="pioro", uzycie=None,
                  opis="Pióro Szymonowica. Stale: każda nowa karta w Księdze daje 3 PW zamiast 2."),
    "ksiega": dict(nazwa="Księga Akademii", ikona="ksiega", uzycie=None,
                   opis="Statut Akademii Zamojskiej. Stale: +1 PW każdego dnia."),
    "klucze": dict(nazwa="Klucze do bram", ikona="klucze", uzycie=None,
                   opis="Klucze do bram Lubelskiej, Lwowskiej i Szczebrzeskiej. Twierdza jest gotowa!"),
}

# ------------------------------------------------------------------ KSIĘGA WIEDZY
WIEDZA = {
    "zamoyski": ("Jan Zamoyski (1542–1605)",
                 "Szlachcic, polityk i wódz. Był kanclerzem wielkim koronnym (od 1578 r.) i hetmanem wielkim "
                 "koronnym (od 1581 r.) — jednym z najważniejszych ludzi w Rzeczypospolitej. Studiował w Paryżu, "
                 "Strasburgu i Padwie, gdzie wybrano go nawet rektorem uniwersytetu. Kochał naukę i sztukę."),
    "kompas": ("Kompas i strony świata",
               "Igła kompasu to mały magnes, który ustawia się w kierunku północy. Główne strony świata to "
               "północ (N), południe (S), wschód (E) i zachód (W). Na mapach północ jest zwykle na górze. "
               "Kompas pomagał mierniczym wytyczać proste ulice nowych miast."),
    "renesans": ("Renesans",
                 "Renesans (odrodzenie) to epoka w sztuce i nauce w XV–XVI wieku. Ludzie podziwiali starożytnych "
                 "Greków i Rzymian. Architekci dbali o symetrię, harmonię i proporcje. Renesans narodził się we "
                 "Włoszech, a do Polski przybył m.in. dzięki włoskim artystom."),
    "morando": ("Bernardo Morando",
                "Architekt z Padwy w Republice Weneckiej. Zamoyski zaprosił go, by zaprojektował całe miasto. "
                "Morando kierował budową Zamościa przez ok. 20 lat — zaprojektował pałac, ratusz, kolegiatę "
                "i fortyfikacje. Zmarł w Zamościu ok. 1600 r."),
    "miasto_idealne": ("Miasto idealne",
                       "Renesansowi uczeni marzyli o mieście idealnym — zaplanowanym od początku do końca, "
                       "z prostymi ulicami, rynkiem w centrum i murami dookoła. Mówi się, że plan Zamościa "
                       "przypomina sylwetkę człowieka: pałac to głowa, główna ulica to kręgosłup, "
                       "a Akademia i Kolegiata to płuca."),
    "palac": ("Pałac Zamoyskich",
              "Rezydencja założyciela miasta, zbudowana według projektu Morando na zachodnim końcu głównej osi "
              "miasta. Z okien pałacu widać było prostą drogę aż do Rynku. Później pałac wielokrotnie "
              "przebudowywano."),
    "lokacja": ("Przywilej lokacyjny (1580)",
                "Lokacja to założenie miasta zgodnie z prawem. 3 kwietnia 1580 r. Jan Zamoyski wystawił "
                "przywilej lokacyjny dla Zamościa, a król Stefan Batory potwierdził prawa miejskie. Odtąd "
                "mieszkańcy mogli handlować, wybierać władze i budować domy."),
    "magdeburskie": ("Prawo magdeburskie",
                     "Wiele polskich miast lokowano na prawie magdeburskim (z niemieckiego miasta Magdeburg). "
                     "Dawało ono miastu samorząd: radę miejską z burmistrzem, własny sąd (ławę) i prawo "
                     "do organizowania targów."),
    "cegla": ("Cegła i kamień",
              "Cegłę robi się z gliny wymieszanej z wodą, formuje w drewnianych formach, suszy i wypala w piecu. "
              "Domy murowane z cegły i kamienia nie paliły się tak łatwo jak drewniane. W Zamościu "
              "budowano głównie z cegły, a zdobienia wykonywano z kamienia."),
    "rynek": ("Rynek Wielki",
              "Serce Zamościa to kwadratowy plac o boku około 100 metrów. Z każdego boku wychodzą po dwie "
              "ulice. Wokół Rynku stoją kamienice z podcieniami. Odbywały się tu targi, jarmarki "
              "i uroczystości."),
    "ratusz": ("Ratusz",
               "W ratuszu obradowała rada miejska i sąd. Zamojski ratusz zbudowano w latach 1591–1600. "
               "Ma wieżę wysoką na 52 metry, a słynne wachlarzowe schody dobudowano w XVIII wieku. "
               "Ciekawostka: ratusz nie stoi na środku Rynku, tylko przy jego północnej pierzei, by nie "
               "zasłaniać widoku z pałacu."),
    "podcienia": ("Podcienia i attyki",
                  "Podcienia to zadaszone przejścia z łukami (arkadami) na parterze kamienic. Chroniły kupców "
                  "i klientów przed deszczem i słońcem. Attyka to ozdobna ścianka nad gzymsem, która zasłania "
                  "dach — typowa ozdoba polskiego renesansu."),
    "ormianie": ("Miasto wielu narodów",
                 "Zamoyski zapraszał do miasta kupców i rzemieślników z różnych stron. W 1585 r. przywilej "
                 "otrzymali Ormianie, w 1588 r. — Żydzi sefardyjscy. Mieszkali tu też Grecy, Włosi, Szkoci "
                 "i Niemcy. Kolorowe kamienice ormiańskie zdobią Rynek do dziś."),
    "kolegiata": ("Kolegiata",
                  "Świątynię zbudowano w latach 1587–1598 według projektu Morando. Jest jednym z najpiękniejszych "
                  "renesansowych kościołów w Polsce. Od 1992 r. jest katedrą. Pochowano w niej Jana Zamoyskiego."),
    "akademia": ("Akademia Zamojska",
                 "Założona w 1594 r. przez Jana Zamoyskiego. Była trzecią uczelnią w Rzeczypospolitej — "
                 "po Akademii Krakowskiej i Wileńskiej. Uczono tu prawa, filozofii, medycyny i języków. "
                 "Zamoyski mówił, że państwo zależy od wychowania młodzieży."),
    "szymonowic": ("Szymon Szymonowic (1558–1629)",
                   "Poeta i uczony, przyjaciel Zamoyskiego. Pomagał stworzyć Akademię Zamojską i zapraszał "
                   "do niej profesorów. Jest autorem „Sielanek” — wierszy o życiu na wsi. Nazywano go "
                   "„polskim Pindarem”."),
    "bastion": ("Bastion",
                "Bastion to wysunięte przed mur umocnienie o kształcie pięciokąta. Dzięki niemu obrońcy mogli "
                "strzelać do wroga z boku i nie było „martwych pól”, w których napastnik mógłby się ukryć. "
                "Taki system nazywa się fortyfikacją bastionową (włoską)."),
    "bramy": ("Bramy miejskie",
              "Do Zamościa prowadziły trzy bramy, nazwane od miast, do których wiodły drogi: Lubelska, "
              "Lwowska i Szczebrzeska. Bramy zamykano na noc, a strażnicy pobierali opłaty od kupców."),
    "twierdza": ("Twierdza nie do zdobycia",
                 "Zamość był jedną z najsilniejszych twierdz Rzeczypospolitej. W 1648 r. oparł się wojskom "
                 "Kozaków Bohdana Chmielnickiego, a w 1656 r. — Szwedom podczas potopu. Twierdzę otaczały "
                 "wały, 7 bastionów i fosa."),
    "unesco": ("Zamość dziś",
               "W 1992 r. Stare Miasto w Zamościu wpisano na Listę Światowego Dziedzictwa UNESCO. Nazywa się "
               "je „Perłą Renesansu” i „Padwą Północy”. Możesz je odwiedzić — Rynek, ratusz i kamienice "
               "ormiańskie wyglądają podobnie jak 400 lat temu!"),
}
KARTY_STARTOWE = ["zamoyski", "kompas", "renesans"]
KARTA_BUDYNKU = {"palac": "palac", "rynek": "rynek", "ratusz": "ratusz", "cegielnia": "cegla",
                 "kolegiata": "kolegiata", "akademia": "akademia", "brama": "bramy"}

RANGI = [(0, "Giermek"), (25, "Uczeń architekta"), (50, "Czeladnik budowniczy"),
         (85, "Mistrz budowniczy"), (130, "Mecenas Renesansu")]


def ranga(pw):
    wynik = RANGI[0][1]
    for prog, nazwa in RANGI:
        if pw >= prog:
            wynik = nazwa
    return wynik


# ------------------------------------------------------------------ ZAGADKI
def Q(pytanie, poprawna, zle, wyjasnienie):
    return dict(pytanie=pytanie, poprawna=poprawna, zle=zle, wyjasnienie=wyjasnienie)


QUIZ_GLOWNY = {
    ("morando", 1): Q("Jak nazywa się epoka, w której podziwiano starożytnych Greków i Rzymian, a artyści dbali "
                      "o symetrię i proporcje?", "Renesans", ["Średniowiecze", "Epoka kamienia"],
                      "Renesans znaczy „odrodzenie” — odrodzenie sztuki starożytnej."),
    ("hagop", 2): Q("Do czego służyły podcienia na parterze kamienic?",
                    "Chroniły kupców i klientów przed deszczem i słońcem",
                    ["Trzymano w nich krowy", "Były to więzienne lochy"],
                    "Pod arkadami podcieni handlowano nawet w ulewę!"),
    ("szymonowic", 3): Q("W którym roku Jan Zamoyski założył Akademię Zamojską?", "1594", ["1410", "1791"],
                         "Akademię założono w 1594 r. — rok 1410 to bitwa pod Grunwaldem."),
    ("morando", 4): Q("Dlaczego bastiony mają kształt wysuniętego pięciokąta?",
                      "Aby obrońcy mogli strzelać do wroga z boku",
                      ["Bo tak było najtaniej", "Żeby ładnie wyglądały z lotu ptaka"],
                      "Z boków bastionu widać cały mur — wróg nie ma gdzie się ukryć."),
}

ZAGADKI = {
    "morando": [
        Q("Z jakiego miasta pochodził architekt Bernardo Morando?", "Z Padwy (Włochy)", ["Z Krakowa", "Z Paryża"],
          "Morando przybył z Padwy w Republice Weneckiej."),
        Q("Z czym często porównuje się plan Zamościa?", "Z sylwetką człowieka", ["Z rybą", "Z koroną"],
          "Pałac to głowa, główna ulica — kręgosłup, a Akademia i Kolegiata — płuca."),
        Q("Która strona świata leży naprzeciw północy?", "Południe", ["Wschód", "Zachód"],
          "Północ i południe są naprzeciw siebie, tak samo wschód i zachód."),
        Q("Po której stronie świata wschodzi Słońce?", "Na wschodzie", ["Na zachodzie", "Na północy"],
          "Słońce wschodzi na wschodzie, a zachodzi na zachodzie."),
    ],
    "hagop": [
        Q("Czym jest attyka?", "Ozdobną ścianką nad gzymsem, zasłaniającą dach", ["Rodzajem piwnicy", "Wozem kupieckim"],
          "Attyki to znak rozpoznawczy polskiego renesansu."),
        Q("Jaki kształt ma Rynek Wielki w Zamościu?", "Kwadrat o boku ok. 100 m", ["Koło", "Trójkąt"],
          "Rynek to kwadrat 100 × 100 metrów."),
        Q("Jakie słynne schody ma zamojski ratusz?", "Wachlarzowe", ["Ruchome", "Sznurowe"],
          "Wachlarzowe schody dobudowano w XVIII wieku."),
        Q("Kto osiedlał się w Zamościu obok Polaków?", "Ormianie, Żydzi, Grecy, Włosi i Szkoci",
          ["Tylko Polacy", "Wikingowie"], "Zamość był miastem wielu narodów i religii."),
        Q("Z czego robi się cegłę?", "Z wypalonej gliny", ["Z roztopionego piasku", "Z drewna"],
          "Glinę formuje się, suszy i wypala w piecu."),
    ],
    "szymonowic": [
        Q("Jaki urząd pełnił Jan Zamoyski?", "Kanclerza i hetmana wielkiego koronnego", ["Króla Polski", "Papieża"],
          "Kanclerz kierował sprawami państwa, a hetman — wojskiem."),
        Q("W którym mieście Zamoyski był rektorem uniwersytetu?", "W Padwie", ["W Oksfordzie", "W Pradze"],
          "Młody Zamoyski był rektorem w Padwie w 1563 r."),
        Q("Którą z kolei uczelnią w Rzeczypospolitej była Akademia Zamojska?", "Trzecią",
          ["Pierwszą", "Dziesiątą"], "Wcześniej powstały Akademia Krakowska i Wileńska."),
        Q("Jak nazywa się słynny zbiór wierszy Szymonowica?", "Sielanki", ["Treny", "Pan Tadeusz"],
          "„Treny” napisał Jan Kochanowski, a „Pana Tadeusza” — Adam Mickiewicz."),
        Q("Który król potwierdził prawa miejskie Zamościa?", "Stefan Batory", ["Bolesław Chrobry", "Jan III Sobieski"],
          "Stefan Batory panował w latach 1576–1586, a Zamoyski był jego kanclerzem."),
    ],
}

# ------------------------------------------------------------------ ROZDZIAŁY
# Cel: (opis, typ, parametr, liczba)
ROZDZIALY = {
    1: dict(
        tytul="Rozdział I: Kompas i plan", lata="Wiosna 1580 r.",
        wstep="Wiosna 1580 roku. Kanclerz Jan Zamoyski stoi na zielonych łąkach nad rzeką Topornicą. "
              "W dłoni ściska swój ulubiony kompas, przywieziony ze studiów w Padwie.\n\n"
              "— Właśnie tutaj — mówi — zbudujemy miasto idealne! Miasto nauki, handlu i odwagi.\n\n"
              "Pomoże mu włoski architekt Bernardo Morando. Najpierw trzeba zdobyć drewno i kamień, "
              "postawić domy dla pierwszych osadników i wznieść pałac — „głowę” miasta.",
        cele=[("Porozmawiaj z architektem Morando", "rozmowa", "morando", 1),
              ("Zbuduj tartak przy lesie", "buduj", "tartak", 1),
              ("Zbuduj kamieniołom przy skałach", "buduj", "kamieniolom", 1),
              ("Zbuduj 4 domy mieszczańskie", "buduj", "dom", 4),
              ("Wznieś Pałac Zamoyskich", "buduj", "palac", 1)],
        koniec=[("narrator", "3 kwietnia 1580 roku Jan Zamoyski wystawił przywilej lokacyjny. Król Stefan Batory "
                             "potwierdził prawa nowego miasta."),
                ("zamoyski", "Nazwiemy je Zamość — od nazwiska mego rodu. Niech rośnie i kwitnie!"),
                ("narrator", "Otrzymujesz: Przywilej lokacyjny. Podatki rosną o 25%.")],
        nagroda="przywilej", karty=["lokacja", "magdeburskie"]),
    2: dict(
        tytul="Rozdział II: Rynek Wielki", lata="Lata 1580–1600",
        wstep="Wieść o nowym mieście szybko się rozchodzi. Do Zamościa ciągną kupcy z różnych stron: "
              "Ormianie ze Lwowa, Grecy, Włosi i Szkoci.\n\n"
              "Każde miasto potrzebuje serca. Morando wyrysował kwadratowy Rynek Wielki, a przy nim ratusz. "
              "Wokół Rynku staną kolorowe kamienice z podcieniami. Potrzebna będzie cegła — glinę znajdziesz "
              "nad wodą i na bagnach.",
        cele=[("Porozmawiaj z kupcem Hagopem", "rozmowa", "hagop", 2),
              ("Zbuduj cegielnię przy wodzie lub bagnie", "buduj", "cegielnia", 1),
              ("Wybrukuj Rynek Wielki", "buduj", "rynek", 1),
              ("Zbuduj 4 kamienice przy Rynku", "przy_rynku", "kamienica", 4),
              ("Postaw 2 kramy na Rynku", "buduj", "kram", 2),
              ("Wznieś Ratusz", "buduj", "ratusz", 1)],
        koniec=[("morando", "Signore Zamoyski, Rynek jest piękniejszy niż w niejednym włoskim mieście!"),
                ("morando", "Proszę, przyjmij mój cyrkiel. Niech pomaga ci kreślić kolejne budowle."),
                ("narrator", "Otrzymujesz: Cyrkiel architekta. Budowle są tańsze o 15%.")],
        nagroda="cyrkiel", karty=[]),
    3: dict(
        tytul="Rozdział III: Akademia i Kolegiata", lata="Lata 1587–1600",
        wstep="Miasto tętni handlem, ale Zamoyski marzy o czymś więcej.\n\n"
              "— Takie będą Rzeczypospolite, jakie ich młodzieży chowanie — powtarza kanclerz. "
              "Czyli: przyszłość państwa zależy od tego, jak wychowamy i wykształcimy młodych ludzi.\n\n"
              "Przyjaciel Zamoyskiego, poeta Szymon Szymonowic, pomoże założyć Akademię. Obok stanie "
              "wspaniała Kolegiata. Aby je zbudować, musisz zdobyć dużo Punktów Wiedzy!",
        cele=[("Porozmawiaj z poetą Szymonowicem", "rozmowa", "szymonowic", 3),
              ("Zbuduj Kolegiatę (wymaga 35 PW)", "buduj", "kolegiata", 1),
              ("Załóż Akademię Zamojską (wymaga 50 PW)", "buduj", "akademia", 1),
              ("Zdobądź 75 Punktów Wiedzy", "wiedza", None, 75)],
        koniec=[("szymonowic", "Pierwsi studenci już przybyli! Będą uczyć się prawa, medycyny i poezji."),
                ("zamoyski", "Oto prawdziwy skarb miasta — mądrzy ludzie."),
                ("narrator", "Otrzymujesz: Księgę Akademii. Codziennie +1 Punkt Wiedzy.")],
        nagroda="ksiega", karty=[]),
    4: dict(
        tytul="Rozdział IV: Twierdza nie do zdobycia", lata="Lata 1587–1605",
        wstep="Rzeczpospolita toczy wojny, a bogate miasto musi umieć się bronić. Hetman Zamoyski "
              "zna się na wojnie jak mało kto.\n\n"
              "Morando zaprojektował nowoczesną twierdzę: siedem bastionów połączonych wałami "
              "i trzy bramy na traktach do Lublina, Lwowa i Szczebrzeszyna. Użyj kompasu, aby odnaleźć "
              "wszystkie działki dookoła miasta!",
        cele=[("Porozmawiaj z Morando o fortyfikacjach", "rozmowa", "morando", 4),
              ("Zbuduj 7 bastionów", "buduj", "bastion", 7),
              ("Zbuduj 3 bramy miejskie", "buduj", "brama", 3)],
        koniec=[("narrator", "Twierdza Zamość jest gotowa. Jej mury oprą się Kozakom w 1648 r. i Szwedom w 1656 r."),
                ("zamoyski", "Zbudowaliśmy miasto nauki, handlu i odwagi. Dziękuję wam, przyjaciele!"),
                ("narrator", "Otrzymujesz: Klucze do bram miasta.")],
        nagroda="klucze", karty=["twierdza"]),
}

# ------------------------------------------------------------------ ROZMOWY
# Główna rozmowa w danym rozdziale: kwestie, zagadka, nagroda, karty wiedzy
ROZMOWY = {
    ("morando", 1): dict(
        kwestie=[("morando", "Buongiorno, panie kanclerzu! Jestem Bernardo Morando, architekt z Padwy."),
                 ("zamoyski", "Witaj, mistrzu! Chcę tu zbudować miasto idealne — takie jak w traktatach "
                              "włoskich uczonych."),
                 ("morando", "Narysowałem plan. Pałac stanie na zachodzie, a od niego prosta ulica "
                             "poprowadzi na wschód, do Rynku. Jak głowa i kręgosłup człowieka!"),
                 ("morando", "Twój kompas pomoże nam wytyczyć proste ulice. Wciśnij K, a pokaże ci kierunek "
                             "i wszystkie działki z mojego planu."),
                 ("morando", "Ale najpierw zagadka — sprawdzę, czy znasz ducha naszych czasów!")],
        nagroda="plan", karty=["morando", "miasto_idealne"],
        po=[("morando", "Zbuduj tartak przy lesie i kamieniołom przy skałach. Potem domy i pałac!")]),
    ("hagop", 2): dict(
        kwestie=[("hagop", "Barew dzez! To po ormiańsku „dzień dobry”. Jestem Hagop, kupiec ze Lwowa."),
                 ("hagop", "Sprzedaję jedwab, przyprawy i dywany ze Wschodu. Słyszałem, że w Zamościu "
                           "kupcy mogą się osiedlać!"),
                 ("zamoyski", "Tak! Każdy uczciwy kupiec i rzemieślnik jest tu mile widziany."),
                 ("hagop", "Zbuduj więc kamienice przy Rynku — z podcieniami i attyką. Ale powiedz mi..."),
                 ],
        nagroda="waga", karty=["podcienia", "ormianie"],
        po=[("hagop", "Postaw kamienice tuż przy brzegu Rynku, a kramy na samym bruku.")]),
    ("szymonowic", 3): dict(
        kwestie=[("szymonowic", "Witaj, Janie! Przywiozłem listy od profesorów z Krakowa."),
                 ("zamoyski", "Szymonie, przyjacielu! Czy zgodzą się uczyć w naszej Akademii?"),
                 ("szymonowic", "Zgodzą się, jeśli Akademia będzie miała piękny gmach i dobrą bibliotekę."),
                 ("szymonowic", "Uczniowie nauczą się tu łaciny, greki, prawa, medycyny i matematyki."),
                 ("szymonowic", "Sprawdźmy, czy pamiętasz najważniejszą datę...")],
        nagroda="pioro", karty=["szymonowic"],
        po=[("szymonowic", "Czytaj Księgę Wiedzy (L) i rozwiązuj moje zagadki, a zdobędziesz Punkty Wiedzy!")]),
    ("morando", 4): dict(
        kwestie=[("morando", "Panie hetmanie, czas pomyśleć o obronie. Zaprojektowałem twierdzę bastionową."),
                 ("morando", "Siedem bastionów otoczy miasto jak siedmioramienna gwiazda. Między nimi "
                             "usypiemy wały, a dookoła będzie fosa i bagna."),
                 ("zamoyski", "A bramy? Kupcy muszą przecież wjeżdżać do miasta."),
                 ("morando", "Trzy bramy: Lubelska na północy, Lwowska na wschodzie i Szczebrzeska "
                             "na południu. Kompas pokaże ci, gdzie je postawić."),
                 ("morando", "Powiedz mi, panie hetmanie...")],
        nagroda="prowiant", karty=["bastion"],
        po=[("morando", "Bastiony stawiaj na złotych działkach dookoła miasta. Wciśnij K!")]),
}

LUZNE = {
    "morando": [("morando", "Bella! Miasto rośnie jak na moim rysunku.")],
    "hagop": [("hagop", "Dobry kupiec zawsze wie, gdzie jest Rynek. A ty masz kompas!")],
    "szymonowic": [("szymonowic", "Piszę nowe wiersze — sielanki o życiu na wsi.")],
}

NAZWY_POSTACI = {"zamoyski": "Jan Zamoyski", "morando": "Bernardo Morando", "hagop": "Hagop",
                 "szymonowic": "Szymon Szymonowic", "narrator": "Kronikarz"}

POMOC = [
    "STEROWANIE",
    "Strzałki / WASD — chodzenie Zamoyskim",
    "E lub Spacja — rozmowa z postacią (podejdź blisko)",
    "Lewy przycisk myszy — wybór i stawianie budynku",
    "Prawy przycisk / Esc — anuluj budowę",
    "K — kompas   I — ekwipunek   L — Księga Wiedzy",
    "M — muzyka wł./wył.   F11 — pełny ekran",
    "",
    "JAK GRAĆ",
    "Wykonuj cele rozdziału z panelu po prawej stronie.",
    "Co dzień targowy (pasek na dole) budynki dają surowce,",
    "a mieszczanie płacą podatki w złocie.",
    "Warsztaty potrzebują robotników — buduj domy!",
    "Złote działki z planu Morando pokaże ci kompas (K).",
    "Czytaj karty Księgi Wiedzy i rozwiązuj zagadki postaci,",
    "aby zdobywać Punkty Wiedzy (PW) i wyższe rangi.",
]
