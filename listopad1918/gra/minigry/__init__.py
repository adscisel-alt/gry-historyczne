"""Minigry i zagadki logiczne."""
from .mapa import MapaZaborow
from .manifest import Manifest
from .przepustki import Przepustki
from .koszary import KolejnoscKoszar
from .swiadkowie import Swiadkowie
from .dyplomacja import Dyplomacja
from .quizy import PrawaKobiet, Wklady

REJESTR = {k.gid: k for k in (MapaZaborow, Manifest, Przepustki, KolejnoscKoszar, Swiadkowie, Dyplomacja, PrawaKobiet, Wklady)}
