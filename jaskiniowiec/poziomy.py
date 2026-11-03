"""Mapy poziomów, dzieci z lekcjami, kamienie z podpowiedziami i fabuła."""

HEIGHT = 17

# Legenda mapy:
#  .  powietrze        #  skała/ziemia      =  kłoda (przeskakiwalna od dołu)
#  ^  kolce            ~  woda              i  lód (śliski)
#  D  wrota (otwiera płyta p)               G  brama (runy lub pokonany lew)
#  p  kamienna płyta   B  głaz do pchania   1-4 kamienie runiczne   X malowidło
#  ?  kamień z podpowiedzią                 K  dziecko              P  start
#  E  wyjście          T  pochodnia/totem (punkt kontrolny)
#  b  jagody  m  mięso  f  krzemień  h  zioło życia
#  z  dzik  w  wilk  v  nietoperz  k  sopel/stalaktyt  M  mamut  L  lew jaskiniowy
#  O  świecące oczy (coś obserwuje...)


def build(sections, ceiling=0):
    rows = [''] * HEIGHT
    for sec in sections:
        w = max(len(r) for r in sec)
        pad = ['.' * w] * (HEIGHT - len(sec)) + [r.ljust(w, '.') for r in sec]
        rows = [a + b for a, b in zip(rows, pad)]
    if ceiling:
        rows = ['#' * len(rows[0])] * 1 + rows[1:]
        for y in range(1, ceiling):
            rows[y] = ''.join('#' if c == '.' else c for c in rows[y])
    return rows


GROUND = '#'

# ============================================================ POZIOM 1
L1 = build([
    [  # start
        "...............bbb..........",
        "..............=====.........",
        "............................",
        ".P..?...b.b.b.........?....f",
        "############################",
        "############################",
        "############################",
    ],
    [  # wzgórze i dzik
        "..................m...........",
        "..................###.........",
        ".................#####........",
        "........z.......#######...K..T",
        "##############################",
        "##############################",
        "##############################",
    ],
    [  # rzeka z kłodami
        "........b......b......b.........",
        "......===....===....===.........",
        "................................",
        "...?...........................f",
        "#####~~~~~~~~~~~~~~~~~~~~~~#####",
        "#####~~~~~~~~~~~~~~~~~~~~~~#####",
        "################################",
    ],
    [  # głaz i wrota
        "........................#...........",
        "........................#...........",
        "........................#...........",
        "........................#...........",
        "........................#...........",
        "........................#...........",
        "........................#...........",
        "........................#...........",
        "........................#...........",
        "........................#...........",
        "...............b.b......#...........",
        "........................D...........",
        "........................D...........",
        "..?...B...............p.D..T...K....",
        "####################################",
        "####################################",
        "####################################",
    ],
    [  # wspinaczka do Zosi
        "................bhb...............",
        "...............K..................",
        "..............=====...............",
        "..................................",
        "..................................",
        ".........===......................",
        "..................................",
        "..................................",
        "....===...................b.b.....",
        "..................................",
        "........................z.........",
        "##################################",
        "##################################",
        "##################################",
    ],
    [  # wyjście
        "....................",
        "......m.............",
        ".....===............",
        "....................",
        "..z..........E......",
        "####################",
        "####################",
        "####################",
    ],
])

# ============================================================ POZIOM 2
L2 = build([
    [  # start i sople
        ".........##########.......",
        "..........k..k..k.........",
        "..........................",
        "..........................",
        ".P..?.......b..b..b..?....",
        "####################iiiiii",
        "####################iiiiii",
        "##########################",
    ],
    [  # wilk i Staś
        "..............ffff............",
        "..............iiii............",
        "..............................",
        "......w..................K...T",
        "iiiiiiii######################",
        "iiiiiiii######################",
        "##############################",
    ],
    [  # mamut nad kolcami
        "........................................",
        "......b....b....b....b....b....b........",
        "?.......................................",
        "###.................................####",
        "###.M...............................####",
        "###^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^####",
        "########################################",
        "########################################",
    ],
    [  # głaz spada z półki, wrota, Hania
        "..............................#.........",
        "..............................#.........",
        "..............................#.........",
        "..............................#.........",
        "..............................#.........",
        "..............................#.........",
        "..............................#.........",
        "..............................#.........",
        "..............................#.........",
        "..............................#.........",
        ".........B....................#.........",
        "....#######...................D.........",
        "....#######...................D.........",
        "T.?.#######..................pD...K.....",
        "iiiiiiiiiiii####################iiiiiiii",
        "iiiiiiiiiiii####################iiiiiiii",
        "########################################",
    ],
    [  # wataha i Antek wysoko
        "....................K...............",
        ".............===..=====.............",
        "...........................f........",
        "..........................===.......",
        "........===.........................",
        "................................h...",
        "...............................===..",
        "...===..............................",
        "....................................",
        "....................w.......w.......",
        "####################################",
        "####################################",
        "####################################",
    ],
    [  # wyjście
        "..######..........",
        "...k..k...........",
        "..................",
        "..................",
        "..........w...E...",
        "##################",
        "##################",
        "##################",
    ],
])

# ============================================================ POZIOM 3
L3 = build([
    [  # wejście do jaskini
        "............................",
        "...............v......k.....",
        "............................",
        "............................",
        "............................",
        "............................",
        "............................",
        "............................",
        "............................",
        "..........................f.",
        "..........=====.............",
        "............................",
        ".P.T..?.........b.b.b.......",
        "############################",
        "############################",
        "############################",
    ],
    [  # podziemne jezioro, oczy w ciemności, Ignaś
        "..............................",
        "..........v...........k.......",
        "..............................",
        "..............................",
        "..............................",
        "..............................",
        "......................O.......",
        "..............................",
        "..............................",
        "......b.......b.......b.......",
        ".....===.....===.....===......",
        "..............................",
        ".?.........................K..",
        "####~~~~~~~~~~~~~~~~~~~~~#####",
        "####~~~~~~~~~~~~~~~~~~~~~#####",
        "##############################",
    ],
    [  # zagadka run
        "..........................................#....",
        "..........................................#....",
        "..........................................#....",
        "..........................................#....",
        "..........................................#....",
        "..........................................#....",
        "..........................................#....",
        "..........................................#....",
        "..........................................#....",
        ".....X....................................#....",
        "..........................................G....",
        "..........................................G....",
        "T..?.......1......2......3......4.........G..K.",
        "###############################################",
        "###############################################",
        "###############################################",
    ],
    [  # wspinaczka nad przepaścią, Tosia
        "........................................",
        "..........k..........v.............k....",
        "...................h....................",
        "....................K...................",
        "..................====..................",
        "........................................",
        "........................................",
        ".............===.........===............",
        "......................................O.",
        "........................................",
        "........===.................===.........",
        "........................................",
        "T.................................b.b...",
        "#######.........##########......########",
        "#######.........##########......########",
        "#######.........##########......########",
    ],
    [  # wyjście
        "..................",
        "...v..............",
        "..................",
        "..................",
        "..................",
        "..................",
        "..................",
        "..................",
        "..................",
        "..................",
        "..................",
        "..................",
        "...........E......",
        "##################",
        "##################",
        "##################",
    ],
], ceiling=2)

# ============================================================ POZIOM 4
L4 = build([
    [  # podejście
        "..............................",
        "..............................",
        "..............................",
        "...................bbb........",
        "..................=====.......",
        "..............................",
        ".P..?.....w.........w.....T...",
        "######^^######..######..######",
        "##############..######..######",
        "##############..######..######",
    ],
    [  # przepaść
        ".........m................",
        "........===...............",
        "..........................",
        "...===........===.........",
        "..........................",
        ".....................h..T.",
        "#..................#######",
        "#..................#######",
        "#..................#######",
    ],
    [  # arena lwa
        "..................................#.....",
        "..................................#.....",
        "..................................#.....",
        "..................................#.....",
        "..................................#.....",
        "..................................#.....",
        "..................................#.....",
        "..................................#.....",
        "..................................#.....",
        "..................................#.....",
        ".?................................#.....",
        "####....====............====......G.....",
        "####..............................G.....",
        "####..........................L...G..K..",
        "########################################",
        "########################################",
        "########################################",
    ],
    [  # wyjście
        "................",
        "................",
        "................",
        "...b.b.b...E....",
        "################",
        "################",
        "################",
    ],
])


LEVELS = [
    dict(
        name="Dolina Wisły",
        subtitle="Rozdział I",
        theme='valley',
        map=L1,
        music='adventure',
        kids=[
            dict(name="Ola", hair=(120, 70, 30), tunic=(200, 120, 60), girl=True,
                 hello="Panie Damianie! Uciekłam z obozu za tym rykiem... Chcę zrobić sobie nóż, ale ten kamień się nie łupie!",
                 q="Z jakiego kamienia robimy najlepsze ostre narzędzia?",
                 a=["Z krzemienia", "Z piaskowca", "Z bursztynu"], ok=0,
                 why="Krzemień pęka na cienkie, bardzo ostre odłupki. Robimy z niego noże, skrobacze i groty oszczepów."),
            dict(name="Kuba", hair=(40, 30, 24), tunic=(150, 110, 70), girl=False,
                 hello="Zamknąłem się tu przed dzikiem! Burczy mi w brzuchu... Gdzie znajdę jedzenie?",
                 q="Skąd ludzie paleolitu brali jedzenie?",
                 a=["Uprawiali zboże na polach", "Polowali, łowili ryby i zbierali rośliny", "Hodowali krowy w zagrodach"], ok=1,
                 why="W paleolicie byliśmy łowcami i zbieraczami. Rolnictwo i hodowla pojawiły się dopiero w neolicie."),
            dict(name="Zosia", hair=(220, 90, 40), tunic=(110, 150, 80), girl=True,
                 hello="Weszłam tak wysoko, żeby zobaczyć, dokąd poszło plemię. Czemu my ciągle się przenosimy?",
                 q="Dlaczego plemię paleolitu często zmieniało miejsce obozu?",
                 a=["Bo wędrowało za zwierzętami i porami roku", "Bo nie lubiło sąsiadów", "Bo budowało nowe zamki"], ok=0,
                 why="Byliśmy koczownikami: szliśmy tam, gdzie wędrowały stada i gdzie dojrzewały rośliny."),
        ],
        hints=[
            "STEROWANIE: strzałki lub A/D – chodzenie, SPACJA/W – skok (przytrzymaj, by skoczyć wyżej), E – rozmowa i czytanie.",
            "X lub J – zamach maczugą. Szare krzemienie zbieraj i rzucaj klawiszem C lub K.",
            "Ciekawostka: dinozaury wyginęły 66 milionów lat przed pojawieniem się ludzi. Żaden jaskiniowiec ich nie widział!",
            "Głaz można pchać. Połóż go na kamiennej płycie, a wrota się otworzą. Klawisz R ustawia głazy z powrotem.",
        ],
        rune_order=None,
    ),
    dict(
        name="Lodowe Wzgórza",
        subtitle="Rozdział II",
        theme='ice',
        map=L2,
        music='adventure',
        kids=[
            dict(name="Staś", hair=(240, 220, 160), tunic=(120, 130, 170), girl=False,
                 hello="Bbbrr... Zamarzam! Tropiłem mamuta i zgubiłem drogę. Jak wy, dorośli, wytrzymujecie ten mróz?",
                 q="Jak ludzie epoki lodowcowej chronili się przed mrozem?",
                 a=["Nosili ubrania ze skór i futer zwierząt", "Nosili wełniane swetry z owczej wełny", "Chowali się w metalowych domach"], ok=0,
                 why="Szyliśmy ubrania ze skór i futer, a w obozach paliliśmy ogień. Owce udomowiono dopiero w neolicie."),
            dict(name="Hania", hair=(90, 50, 30), tunic=(170, 80, 80), girl=True,
                 hello="Rozdarłam futro o skały... Mama mówi, że trzeba je zszyć, ale czym?",
                 q="Z czego ludzie paleolitu robili igły do szycia?",
                 a=["Z żelaza", "Z kości lub poroża", "Z brązu"], ok=1,
                 why="Igły z kości i poroża, z wywierconym uszkiem, to jeden z największych wynalazków paleolitu. Metale poznano tysiące lat później."),
            dict(name="Antek", hair=(30, 24, 20), tunic=(190, 160, 90), girl=False,
                 hello="Widziałem stąd stado mamutów! Gdybyśmy jednego upolowali, co byśmy z nim zrobili?",
                 q="Do czego plemię wykorzystywało upolowanego mamuta?",
                 a=["Tylko do jedzenia mięsa", "Do jazdy wierzchem", "Mięso, skóry, kości i kły – nic się nie marnowało"], ok=2,
                 why="Z mamuta mieliśmy jedzenie, skóry na ubrania, kości na szałasy i opał, a z kłów robiliśmy narzędzia i ozdoby."),
        ],
        hints=[
            "Uważaj na sople – spadają, kiedy przechodzisz pod nimi.",
            "Lód jest śliski! Pomyśl o hamowaniu, zanim skoczysz.",
            "Mamuty są łagodne. Wskocz na grzbiet, a przeniesie cię nad kolcami.",
            "Ciekawostka: w Krakowie, na stanowisku Spadzista, archeolodzy znaleźli kości kilkudziesięciu mamutów!",
        ],
        rune_order=None,
    ),
    dict(
        name="Jaskinia Ciemna",
        subtitle="Rozdział III",
        theme='cave',
        map=L3,
        music='cave',
        kids=[
            dict(name="Ignaś", hair=(160, 100, 50), tunic=(100, 120, 90), girl=False,
                 hello="Panie Damianie... tu jest tak ciemno... Coś na mnie patrzyło z wody! Jak rozpalić ogień?",
                 q="Jak ludzie paleolitu rozpalali ogień?",
                 a=["Zapałkami z kieszeni", "Uderzając krzemieniem o piryt albo trąc drewno", "Czekali, aż piorun trafi w drzewo, bo inaczej się nie da"], ok=1,
                 why="Iskry z krzemienia uderzanego o piryt, albo żar z tarcia patyków, zapalały suchą hubę. Zapałki wymyślono 200 lat temu."),
            dict(name="Marysia", hair=(60, 40, 30), tunic=(200, 150, 90), girl=True,
                 hello="Ktoś namalował tu zwierzęta! Też chcę malować na ścianie. Ale czym?",
                 q="Czym malowano obrazy na ścianach jaskiń?",
                 a=["Ochrą, węglem drzewnym i tłuszczem", "Farbą z puszki", "Flamastrami"], ok=0,
                 why="Czerwona i żółta ochra (glinka z żelazem) oraz czarny węgiel drzewny, zmieszane z tłuszczem lub wodą. Malowano palcami, pędzelkami z sierści i rozdmuchując barwnik."),
            dict(name="Tosia", hair=(240, 200, 120), tunic=(140, 90, 150), girl=True,
                 hello="Znalazłam zakrzywiony kawałek kła! Wujek mówi, że w Jaskini Obłazowej był taki, co wracał do rzucającego...",
                 q="W Jaskini Obłazowej w Polsce znaleziono jeden z najstarszych bumerangów świata. Z czego go zrobiono?",
                 a=["Z dębowego drewna", "Z brązu", "Z kła mamuta"], ok=2,
                 why="Bumerang z Jaskini Obłazowej w Tatrach wycięto z kła mamuta ponad 30 tysięcy lat temu!"),
        ],
        hints=[
            "Ciemno choć oko wykol... Dotknij pochodni, by ją zapalić. Oświetli drogę i zapamięta twoje miejsce.",
            "Ciekawostka: Jaskinia Ciemna w Ojcowie to jedno z najstarszych stanowisk w Polsce. Mieszkali tu neandertalczycy.",
            "Malowidło na ścianie zdradza kolejność. Podejdź, naciśnij E, a potem uderz maczugą runiczne kamienie w tej samej kolejności.",
        ],
        rune_order=[3, 1, 4, 2],
    ),
    dict(
        name="Legowisko Lwa",
        subtitle="Rozdział IV",
        theme='lair',
        map=L4,
        music='adventure',
        kids=[
            dict(name="Franek", hair=(200, 150, 80), tunic=(170, 120, 70), girl=False,
                 hello="Panie Damianie! Uratowałem żar Ognia Pierwszego, mam go w pojemniku z hubą! Ale... jak właściwie nazywa się nasza epoka?",
                 q="Jak nazywa się starsza epoka kamienia, w której żyje plemię?",
                 a=["Neolit", "Paleolit", "Epoka brązu"], ok=1,
                 why="Paleolit: od greckiego 'palaios' (stary) i 'lithos' (kamień). To najdłuższy okres w dziejach ludzkości!"),
        ],
        hints=[
            "Ciekawostka: lwy jaskiniowe wyginęły około 14 tysięcy lat temu. Znamy je z kości i malowideł naskalnych.",
            "To legowisko lwa jaskiniowego! Nie stawaj mu na drodze – skacz na kłody. Gdy wpadnie na skałę, jest oszołomiony: wtedy uderz maczugą!",
        ],
        rune_order=None,
    ),
]


STORY_INTRO = [
    ('camp', "Dwadzieścia tysięcy lat temu dolinę Wisły skuwał lód epoki lodowcowej. Plemię Mentis przetrwało dzięki jednemu skarbowi: Ogniowi Pierwszemu – żarowi, który nigdy nie gasł."),
    ('camp', "Damian był nauczycielem plemienia. Uczył dzieci łupać krzemień, tropić zwierzęta i malować na ścianach jaskiń."),
    ('dark', "Aż pewnej nocy z ciemności dobiegł ryk. Coś przewróciło ognisko. Ogień zgasł... a rano w obozie nie było dzieci."),
    ('tracks', "Na szronie zostały tylko ślady wielkich łap i małych stóp. Dzieci pobiegły w noc za bestią, chcąc być dzielnymi łowcami. Ale nie wiedzą jeszcze, jak przetrwać."),
    ('promise', "Damian chwycił maczugę. Musi odnaleźć dzieci, nauczyć je wszystkiego, co wie – i odzyskać Ogień Pierwszy, zanim nadejdzie Wielki Mróz."),
]

STORY_BETWEEN = [
    [('tracks', "Dzieci szepczą, że w nocy widziały w krzakach dwa świecące punkty. Ślady łap prowadzą na Lodowe Wzgórza..."),],
    [('dark', "Ślady znikają w Jaskini Ciemnej. Starszyzna mówi, że kto wszedł tam bez ognia, ten nie wrócił. Damian ma tylko krzemień... i odwagę."),],
    [('painting', "Na ścianie jaskini Damian zobaczył świeże malowidło: wielki kot, płomień i gromadka dzieci. Ktoś z plemienia był tu przed nim! To lew jaskiniowy – a ostatnie dziecko jest w jego legowisku."),],
]

STORY_END = [
    ('end', "Lew uciekł w góry. Franek oddał Damianowi pojemnik z żarem. Z jednej iskry znów zapłonęło ognisko plemienia Mentis."),
    ('end', "Tej nocy Damian namalował na ścianie jaskini całą przygodę: lwa, ogień i dziesięcioro dzielnych dzieci."),
    ('end', "Takie malowidła archeolodzy odnajdują do dziś. Dzięki nim wiemy, jak żyli ludzie paleolitu. KONIEC – dziękujemy za grę!"),
]
