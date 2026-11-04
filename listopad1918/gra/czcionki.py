"""Czcionki z polskimi znakami — systemowe (Windows) z bezpiecznym zapasem."""
import pygame

RODZINY = {
    # nazwa: (lista czcionek systemowych, pogrubienie, kursywa)
    "szeryf": ("georgia,cambria,timesnewroman,dejavuserif,liberationserif,freeserif", False, False),
    "plakat": ("bookmanoldstyle,georgia,cambria,dejavuserif,liberationserif,freeserif", True, False),
    "reka": ("segoescript,inkfree,georgia,dejavuserif,freeserif", False, True),
    "maszyna": ("couriernew,courier,dejavusansmono,liberationmono,freemono", False, False),
}

_cache = {}


def f(rodzina, rozmiar):
    klucz = (rodzina, rozmiar)
    if klucz in _cache:
        return _cache[klucz]
    if not pygame.font.get_init():
        pygame.font.init()
    nazwy, bold, italic = RODZINY.get(rodzina, RODZINY["szeryf"])
    try:
        font = pygame.font.SysFont(nazwy, rozmiar, bold=bold, italic=italic)
    except Exception:  # brak fontconfig itp.
        font = None
    if font is None:
        font = pygame.font.Font(None, int(rozmiar * 1.3))
        font.set_bold(bold)
    _cache[klucz] = font
    return font


def zawin(tekst, czcionka, szerokosc):
    """Dzieli tekst na wiersze mieszczące się w danej szerokości."""
    wiersze = []
    for akapit in tekst.split("\n"):
        slowa = akapit.split(" ")
        biezacy = ""
        for s in slowa:
            proba = (biezacy + " " + s).strip()
            if czcionka.size(proba)[0] <= szerokosc or not biezacy:
                biezacy = proba
            else:
                wiersze.append(biezacy)
                biezacy = s
        wiersze.append(biezacy)
    return wiersze
