"""Zamiana liczb, dat i skrótów na słowa z poprawną odmianą — dla lektora (Piper czyta cyfry niezręcznie).

    „11 listopada 1918 r.”   -> „jedenastego listopada tysiąc dziewięćset osiemnastego roku”
    „W 1917 r. Komitet …”    -> „W tysiąc dziewięćset siedemnastym roku Komitet …”
    „Po 123 latach”          -> „Po stu dwudziestu trzech latach”
    „13. punkt”              -> „trzynasty punkt”

Uruchom bez argumentów, aby sprawdzić przykłady:  python narzedzia/liczebniki.py
"""
import re

JEDN = ["zero", "jeden", "dwa", "trzy", "cztery", "pięć", "sześć", "siedem", "osiem", "dziewięć", "dziesięć",
        "jedenaście", "dwanaście", "trzynaście", "czternaście", "piętnaście", "szesnaście", "siedemnaście",
        "osiemnaście", "dziewiętnaście"]
DZIES = ["", "", "dwadzieścia", "trzydzieści", "czterdzieści", "pięćdziesiąt", "sześćdziesiąt", "siedemdziesiąt",
         "osiemdziesiąt", "dziewięćdziesiąt"]
SETKI = ["", "sto", "dwieście", "trzysta", "czterysta", "pięćset", "sześćset", "siedemset", "osiemset", "dziewięćset"]
# dopełniacz = miejscownik liczebników głównych („około pięciu”, „po pięciu latach”)
JEDN_D = ["zera", "jednego", "dwóch", "trzech", "czterech", "pięciu", "sześciu", "siedmiu", "ośmiu", "dziewięciu",
          "dziesięciu", "jedenastu", "dwunastu", "trzynastu", "czternastu", "piętnastu", "szesnastu", "siedemnastu",
          "osiemnastu", "dziewiętnastu"]
DZIES_D = ["", "", "dwudziestu", "trzydziestu", "czterdziestu", "pięćdziesięciu", "sześćdziesięciu",
           "siedemdziesięciu", "osiemdziesięciu", "dziewięćdziesięciu"]
SETKI_D = ["", "stu", "dwustu", "trzystu", "czterystu", "pięciuset", "sześciuset", "siedmiuset", "ośmiuset",
           "dziewięciuset"]
# porządkowe, mianownik rodzaju męskiego
PORZ = ["zerowy", "pierwszy", "drugi", "trzeci", "czwarty", "piąty", "szósty", "siódmy", "ósmy", "dziewiąty",
        "dziesiąty", "jedenasty", "dwunasty", "trzynasty", "czternasty", "piętnasty", "szesnasty", "siedemnasty",
        "osiemnasty", "dziewiętnasty"]
PORZ_DZ = ["", "", "dwudziesty", "trzydziesty", "czterdziesty", "pięćdziesiąty", "sześćdziesiąty", "siedemdziesiąty",
           "osiemdziesiąty", "dziewięćdziesiąty"]
PORZ_SET = ["", "setny", "dwusetny", "trzechsetny", "czterechsetny", "pięćsetny", "sześćsetny", "siedemsetny",
            "osiemsetny", "dziewięćsetny"]


def _tysiace(n, dop):
    if n == 1:
        return "tysiąca" if dop else "tysiąc"
    slowo = glowny(n, dop)
    if dop:
        return slowo + " tysięcy"
    return slowo + (" tysiące" if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else " tysięcy")


def glowny(n, dop=False):
    """Liczebnik główny; dop=True — forma dopełniacza/miejscownika."""
    if n < 20:
        return (JEDN_D if dop else JEDN)[n]
    czesci = []
    if n >= 1000:
        czesci.append(_tysiace(n // 1000, dop))
        n %= 1000
    if n >= 100:
        czesci.append((SETKI_D if dop else SETKI)[n // 100])
        n %= 100
    if n >= 20:
        czesci.append((DZIES_D if dop else DZIES)[n // 10])
        n %= 10
    if n:
        czesci.append((JEDN_D if dop else JEDN)[n])
    return " ".join(czesci)


def _odmien(slowo, przypadek):
    """Odmiana przymiotnikowa liczebnika porządkowego: m (mianownik), d (dopełniacz), n (miejscownik/narzędnik)."""
    if przypadek == "m":
        return slowo
    rdzen = slowo[:-1]
    if slowo.endswith("i"):                       # drugi, trzeci
        return slowo + ("ego" if przypadek == "d" else "m")
    return rdzen + ("ego" if przypadek == "d" else "ym")


def porzadkowy(n, przypadek="m"):
    """Liczebnik porządkowy rodzaju męskiego, np. 1918 -> „tysiąc dziewięćset osiemnasty”."""
    czesci = []
    if n >= 1000:
        if n % 1000 == 0:
            return _odmien(("" if n == 1000 else glowny(n // 1000)[:-1] + "u") + "tysięczny", przypadek)
        czesci.append(_tysiace(n // 1000, False))
        n %= 1000
    if n >= 100:
        if n % 100 == 0:
            return " ".join(czesci + [_odmien(PORZ_SET[n // 100], przypadek)])
        czesci.append(SETKI[n // 100])
        n %= 100
    if n >= 20:
        czesci.append(_odmien(PORZ_DZ[n // 10], przypadek))
        n %= 10
        if n:
            czesci.append(_odmien(PORZ[n], przypadek))
    elif n:
        czesci.append(_odmien(PORZ[n], przypadek))
    return " ".join(czesci)


MIESIACE = ("styczeń stycznia styczniu luty lutego lutym marzec marca marcu kwiecień kwietnia kwietniu maj maja maju "
            "czerwiec czerwca czerwcu lipiec lipca lipcu sierpień sierpnia sierpniu wrzesień września wrześniu "
            "październik października październiku listopad listopada listopadzie grudzień grudnia grudniu "
            "wiosna wiosną lato latem jesień jesienią zima zimą początku końcu połowie").split()
MIES_DOP = "stycznia lutego marca kwietnia maja czerwca lipca sierpnia września października listopada grudnia".split()
PRZYIMKI_DOP = {"od", "do", "około", "ponad", "z", "ze", "bez", "blisko", "niespełna", "dla", "u", "spod", "sprzed",
                "według", "wokół", "koło"}
PRZYIMKI_MIEJ = {"w", "we", "po", "o", "przy", "na"}
DUZA = "A-ZĄĆĘŁŃÓŚŹŻ"
NAZWY_WLASNE = set("Polska Polski Polsce Polacy Niemcy Francja Wielka Rosja Austro-Węgry Komitet Armia Dmowski "
                   "Piłsudski Paderewski Haller Wilson Clemenceau Paryż Warszawa Poznań Gdańsk".split())
ROK = r"(1[0-9]{3}|20[0-9]{2})"
R_SKROT = r"(?P<r>\s*r\.|\s+roku)?"


def _przyrostek(tekst, koniec, m_r):
    """„r.” -> „roku”. Kropka skrótu kończy też zdanie, jeśli dalej jest koniec tekstu albo wielka litera
    (chyba że to nazwa własna, np. „W 1915 r. Niemcy zajęli…”)."""
    if m_r and m_r.strip() == "r.":
        reszta = tekst[koniec:]
        nast = re.match(r"\s+([" + DUZA + r"„][\w-]*)", reszta)
        if not reszta.strip() or (nast and nast.group(1) not in NAZWY_WLASNE):
            return " roku."
    return " roku"


def slownie(tekst):
    t = re.sub(r"(^|[.!?]\s+)(?=\d)", "\\1\x01", tekst)      # znacznik: zdanie zaczyna się od liczby
    # zakresy lat: „1914–1919” -> „od tysiąc dziewięćset czternastego do tysiąc dziewięćset dziewiętnastego”
    t = re.sub(r"\b" + ROK + r"\s*[–-]\s*" + ROK + r"\b(\s*r\.)?",
               lambda m: "od %s do %s" % (porzadkowy(int(m.group(1)), "d"), porzadkowy(int(m.group(2)), "d")), t)
    # pełne daty: „11 listopada 1918 r.”, „27 grudnia”
    wzor = re.compile(r"\b([0-3]?\d)\s+(" + "|".join(MIES_DOP) + r")(?:\s+" + ROK + R_SKROT + r")?")

    def data(m):
        w = porzadkowy(int(m.group(1)), "d") + " " + m.group(2)
        if m.group(3):
            w += " " + porzadkowy(int(m.group(3)), "d") + _przyrostek(t, m.end(), m.group("r"))
        return w
    t = wzor.sub(data, t)
    # rok po nazwie miesiąca lub pory roku: „w sierpniu 1915 r.”, „Jesień 1918:”
    t = re.sub(r"\b(" + "|".join(MIESIACE) + r")\s+" + ROK + R_SKROT,
               lambda m: m.group(1) + " " + porzadkowy(int(m.group(2)), "d") + _przyrostek(t, m.end(), m.group("r")),
               t, flags=re.IGNORECASE)
    # „rok 1914” -> „rok tysiąc dziewięćset czternasty”
    t = re.sub(r"\b([Rr]ok)\s+" + ROK + r"\b", lambda m: m.group(1) + " " + porzadkowy(int(m.group(2))), t)
    # przyimek + rok: „w 1917 r.” (miejscownik), „od 1795 r.” (dopełniacz)
    def z_przyimkiem(m):
        p = m.group(1)
        przyp = "n" if p.lower() in PRZYIMKI_MIEJ else "d"
        return p + " " + porzadkowy(int(m.group(2)), przyp) + _przyrostek(t, m.end(), m.group("r"))
    t = re.sub(r"\b(" + "|".join(sorted(PRZYIMKI_MIEJ | PRZYIMKI_DOP, key=len, reverse=True)) + r")\s+" + ROK + R_SKROT
               + r"(?![\d%])", z_przyimkiem, t, flags=re.IGNORECASE)
    # rok w nawiasie: „(1918)” -> „, w roku tysiąc dziewięćset osiemnastym,”
    t = re.sub(r"\s*\(" + ROK + r"\)", lambda m: ", w roku %s," % porzadkowy(int(m.group(1)), "n"), t)
    # pozostałe lata z „r.”
    t = re.sub(r"\b" + ROK + r"(?P<r>\s*r\.|\s+roku)",
               lambda m: porzadkowy(int(m.group(1)), "d") + _przyrostek(t, m.end(), m.group("r")), t)
    # samotny rok: „Warszawa, 1914.” -> „rok tysiąc dziewięćset czternasty”
    t = re.sub(r"(?<![\d,])\b" + ROK + r"\b(?![\d,%])", lambda m: "rok " + porzadkowy(int(m.group(1))), t)
    # liczebniki porządkowe z kropką: „13. punkt”, „28. prezydentem”
    def porz(m):
        slowo = m.group(2)
        przyp = "n" if re.search(r"(em|ym|im)$", slowo) else "m"
        return porzadkowy(int(m.group(1)), przyp) + " " + slowo
    t = re.sub(r"\b(\d{1,3})\.\s+([a-ząćęłńóśźż]\w*)", porz, t)
    # procenty i plusy
    t = re.sub(r"\+\s*(\d+)\s*%", lambda m: "plus " + glowny(int(m.group(1))) + " procent", t)
    t = re.sub(r"(\d+)\s*%", lambda m: glowny(int(m.group(1))) + " procent", t)
    t = re.sub(r"\+\s*(\d+)", lambda m: "plus " + m.group(1), t)
    # jednostki
    t = re.sub(r"(\d+)\s*km\b", lambda m: m.group(1) + " " + _kilometry(int(m.group(1)), t, m.start()), t)

    # pozostałe liczby główne — dopełniacz/miejscownik po przyimku lub przed rzeczownikiem na -ach
    def glowna(m):
        n = int(m.group(2))
        przed = m.group(1)
        po = t2[m.end():m.end() + 20]
        dop = przed.strip().lower() in PRZYIMKI_DOP - {"do", "z", "ze"} or re.match(r"\s+\w+ach\b", po)
        return przed + glowny(n, bool(dop))
    t2 = t
    t = re.sub(r"(\b\w+\s+|^|\W)(\d+)(?!\d)", glowna, t)
    t = re.sub(r"\s+,", ",", re.sub(r",\s*([.?!:;])", r"\1", re.sub(r",\s*,", ",", t)))
    # wielka litera na początku zdania, które zaczynało się od liczby
    return re.sub("\x01(.)", lambda m: m.group(1).upper(), t).replace("\x01", "")


def _kilometry(n, tekst, poz):
    przed = tekst[max(0, poz - 12):poz].split()
    if przed and przed[-1].lower() in PRZYIMKI_DOP:
        return "kilometrów"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return "kilometry"
    return "kilometr" if n == 1 else "kilometrów"


PRZYKLADY = [
    ("11 listopada 1918 r. Polska odzyskuje niepodległość.",
     "Jedenastego listopada tysiąc dziewięćset osiemnastego roku Polska odzyskuje niepodległość."),
    ("W 1917 r. Komitet uznały mocarstwa.", "W tysiąc dziewięćset siedemnastym roku Komitet uznały mocarstwa."),
    ("Od 1795 r. Polski nie było.", "Od tysiąc siedemset dziewięćdziesiątego piątego roku Polski nie było."),
    ("dopiero w 1921 r. Mapa pokazuje stan około 1920 r.", "dopiero w tysiąc dziewięćset dwudziestym pierwszym "
     "roku. Mapa pokazuje stan około tysiąc dziewięćset dwudziestego roku."),
    ("Po 123 latach niewoli", "Po stu dwudziestu trzech latach niewoli"),
    ("Przez 123 lata Polski nie było", "Przez sto dwadzieścia trzy lata Polski nie było"),
    ("Czy pamiętasz, co obiecywał mój 13. punkt?", "Czy pamiętasz, co obiecywał mój trzynasty punkt?"),
    ("Był 28. prezydentem USA", "Był dwudziestym ósmym prezydentem USA"),
    ("w latach 1919–1924 był posłem", "w latach od tysiąc dziewięćset dziewiętnastego do tysiąc dziewięćset "
                                     "dwudziestego czwartego był posłem"),
    ("Mówił około 5 godzin", "Mówił około pięciu godzin"),
    ("leży około 20 km od centrum", "leży około dwudziestu kilometrów od centrum"),
    ("W sierpniu 1915 r. wojska niemieckie", "W sierpniu tysiąc dziewięćset piętnastego roku wojska niemieckie"),
    ("Sierpień 1914 roku. Wybucha wojna", "Sierpień tysiąc dziewięćset czternastego roku. Wybucha wojna"),
    ("Rok 1914. Polski nie ma", "Rok tysiąc dziewięćset czternasty. Polski nie ma"),
    ("Traktat wersalski (1919) przyznał Polsce", "Traktat wersalski, w roku tysiąc dziewięćset dziewiętnastym, "
                                                 "przyznał Polsce"),
    ("Kiedy powstał Komitet w 1914 r.?", "Kiedy powstał Komitet w tysiąc dziewięćset czternastym roku?"),
    ("Prasa +25%.", "Prasa plus dwadzieścia pięć procent."),
    ("W 14 punktach zapowiedział", "W czternastu punktach zapowiedział"),
    ("jest 357 luster.", "jest trzysta pięćdziesiąt siedem luster."),
    ("Następnego dnia, 27 grudnia, wybuchło", "Następnego dnia, dwudziestego siódmego grudnia, wybuchło"),
    ("Warszawa, 1914. Trzeba działać", "Warszawa, rok tysiąc dziewięćset czternasty. Trzeba działać"),
    ("Urodził się 9 sierpnia 1864 r. pod Warszawą", "Urodził się dziewiątego sierpnia tysiąc osiemset "
                                                    "sześćdziesiątego czwartego roku pod Warszawą"),
]


if __name__ == "__main__":
    zle = 0
    for wej, ocz in PRZYKLADY:
        wyn = slownie(wej)
        if wyn != ocz:
            zle += 1
            print("ŹLE:", wej, "\n  jest:   ", wyn, "\n  powinno:", ocz)
    print("liczebniki: %d/%d dobrze" % (len(PRZYKLADY) - zle, len(PRZYKLADY)))
