#!/usr/bin/env python3
"""Synteza efektów dźwiękowych i muzyki do gry „Roman Empire” (rzym3d).

Wszystko generowane od zera: tylko numpy + moduł wave z biblioteki standardowej.
Wynik: godot/audio/*.wav — 16 bit, mono, 22050 Hz.

Efekty są krótkie i znormalizowane do ok. -1 dBFS, utwory muzyczne (ok. 50–55 s)
są zapętlalne bez szwu (nuty i pogłos „zawijają się” z końca na początek)
i znormalizowane do ok. -3 dBFS.

Instrumenty: lira/kitara (algorytm Karplusa-Stronga), aulos (podwójny piszczałkowy
instrument stroikowy — synteza addytywna), bęben ramowy (tympanon), burdon,
rogi i trąby (cornu, tuba) — synteza addytywna z jasnością zależną od obwiedni.

Uruchomienie:  python narzedzia/generuj_dzwieki.py
"""
import os
import sys
import wave

import numpy as np

CZESTO = 22050
KATALOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "godot", "audio")
SZCZYT_EFEKTY = -1.0   # dBFS
SZCZYT_MUZYKA = -3.0   # dBFS
DWA_PI = 2 * np.pi


# ---------------------------------------------------------------------------
# Narzędzia podstawowe
# ---------------------------------------------------------------------------

def czas(dl):
    """Oś czasu (s) o długości dl sekund."""
    return np.arange(int(dl * CZESTO)) / CZESTO


def zapisz_wav(nazwa, probki, szczyt_db, petla=False):
    """Normalizuje szczyt do szczyt_db i zapisuje 16-bitowy plik mono.

    Efekty (petla=False) dostają 1 ms wejścia i 5 ms wyciszenia, by nie trzaskały."""
    x = np.asarray(probki, dtype=np.float64)
    x = x - x.mean()
    if not petla:
        a, b = int(0.001 * CZESTO), int(0.005 * CZESTO)
        x[:a] *= np.linspace(0, 1, a)
        x[-b:] *= np.linspace(1, 0, b)
    m = np.max(np.abs(x))
    if m > 0:
        x = x / m * 10 ** (szczyt_db / 20)
    dane = np.round(np.clip(x, -1, 1) * 32767).astype("<i2")
    sciezka = os.path.join(KATALOG, nazwa + ".wav")
    with wave.open(sciezka, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(CZESTO)
        w.writeframes(dane.tobytes())
    return sciezka


def filtr(x, dol=None, gora=None, rzad=2):
    """Filtr pasmowy w dziedzinie częstotliwości (łagodne zbocza, faza zerowa).

    dol — górnoprzepustowy od tej częstotliwości, gora — dolnoprzepustowy.
    Działa cyklicznie (przydatne przy pętlach muzycznych)."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / CZESTO)
    g = np.ones_like(f)
    if dol:
        g *= 1 / (1 + (dol / np.maximum(f, 1e-3)) ** (2 * rzad))
    if gora:
        g *= 1 / (1 + (f / gora) ** (2 * rzad))
    return np.fft.irfft(X * g, n)


def formanty(x, szczyty):
    """Filtr formantowy: suma rezonansów (częstotliwość, szerokość, wzmocnienie)."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / CZESTO)
    g = np.zeros_like(f)
    for fc, szer, wzm in szczyty:
        g += wzm / (1 + ((f - fc) / (szer / 2)) ** 2)
    return np.fft.irfft(X * g, n)


def szum(dl, ziarno, n=None):
    """Szum biały o długości dl sekund (albo dokładnie n próbek)."""
    return np.random.default_rng(ziarno).uniform(-1, 1, n if n is not None else int(dl * CZESTO))


def obwiednia(n, atak=0.005, zanik=None, wybrzmienie=0.01):
    """Obwiednia: liniowy atak, wykładniczy zanik (stała czasowa w s), krótkie wyciszenie."""
    t = np.arange(n) / CZESTO
    e = np.minimum(1, t / max(atak, 1e-4))
    if zanik:
        e *= np.exp(-t / zanik)
    k = min(n, int(wybrzmienie * CZESTO))
    if k > 0:
        e[n - k:] *= np.linspace(1, 0, k)
    return e


def dodaj(cel, syg, start, zawijaj=False):
    """Dodaje sygnał do bufora od próbki start; przy zawijaj=True nadmiar wraca na początek."""
    start = int(start)
    L = len(cel)
    if zawijaj:
        start %= L
        poz = 0
        while poz < len(syg):
            s = (start + poz) % L
            ile = min(len(syg) - poz, L - s)
            cel[s:s + ile] += syg[poz:poz + ile]
            poz += ile
    else:
        if start >= L:
            return
        ile = min(len(syg), L - start)
        cel[start:start + ile] += syg[:ile]


def poglos(x, dl=1.6, mokry=0.25, ziarno=7, cykliczny=False, jasnosc=3500):
    """Pogłos splotowy (odpowiedź impulsowa = gasnący, przefiltrowany szum).

    cykliczny=True — splot kołowy, więc ogon pogłosu przechodzi na początek pętli."""
    t = czas(dl)
    ir = szum(dl, ziarno) * np.exp(-t / (dl / 6.5))
    ir = filtr(ir, 120, jasnosc)
    ir[: int(0.012 * CZESTO)] = 0          # krótkie opóźnienie wstępne
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-12
    if cykliczny:
        n = len(x)
        h = np.zeros(n)
        h[: min(n, len(ir))] = ir[:n]
        mok = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(h), n)
        return x + mokry * mok
    n = len(x) + len(ir)
    N = 1 << (n - 1).bit_length()
    mok = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:n]
    wynik = np.zeros(n)
    wynik[: len(x)] += x
    return wynik + mokry * mok


def wycisz_koniec(x, dl=0.05):
    k = min(len(x), int(dl * CZESTO))
    x = x.copy()
    x[len(x) - k:] *= np.linspace(1, 0, k) ** 2
    return x


# Nazwy nut -> częstotliwość (A4 = 440 Hz). Zapis: C4, F#3, Bb2 …
_POLTONY = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2, "H": 2}


def nuta(nazwa):
    litera = nazwa[0].upper()
    reszta = nazwa[1:]
    przes = 0
    while reszta and reszta[0] in "#b":
        przes += 1 if reszta[0] == "#" else -1
        reszta = reszta[1:]
    oktawa = int(reszta)
    pol = _POLTONY[litera] + przes + (oktawa - 4) * 12
    return 440.0 * 2 ** (pol / 12)


# ---------------------------------------------------------------------------
# Instrumenty
# ---------------------------------------------------------------------------

def struna(f, dl, glos=0.5, czas_zaniku=1.2, jasnosc=0.6, ziarno=0):
    """Szarpana struna liry/kitary — algorytm Karplusa-Stronga (wektorowo blokami okresu)."""
    n = int(dl * CZESTO)
    p = max(2, int(round(CZESTO / f - 0.5)))
    rng = np.random.default_rng(ziarno + int(f * 10))
    pobudzenie = rng.uniform(-1, 1, p + 1)
    # miękkie szarpnięcie: wygładzenie pobudzenia (mniej jasnosci = cieplejszy dźwięk)
    for _ in range(int((1 - jasnosc) * 4)):
        pobudzenie = 0.5 * (pobudzenie + np.roll(pobudzenie, 1))
    pobudzenie -= pobudzenie.mean()
    y = np.zeros(n + p + 1)
    y[: p + 1] = pobudzenie
    g = np.exp(-p / (CZESTO * czas_zaniku))   # strata energii na jeden obieg
    k = p + 1
    while k < len(y):
        ile = min(p, len(y) - k)
        y[k:k + ile] = g * 0.5 * (y[k - p:k - p + ile] + y[k - p - 1:k - p - 1 + ile])
        k += ile
    y = y[p + 1:p + 1 + n]
    m = np.max(np.abs(y[: p * 4 + 1])) + 1e-9
    return y / m * glos * obwiednia(n, 0.002, None, 0.03)


def aulos(f, dl, glos=0.4, wybrz=0.15, ziarno=0, jasnosc=1.0):
    """Aulos — stroikowa piszczałka: nieparzyste harmoniczne, opóźnione vibrato, oddech."""
    n = int((dl + wybrz) * CZESTO)
    t = np.arange(n) / CZESTO
    vib = 1 + 0.0055 * np.sin(DWA_PI * 5.1 * t + ziarno) * np.clip((t - 0.15) / 0.35, 0, 1)
    nab = 1 - 0.012 * np.exp(-t / 0.04)          # lekkie „podjechanie” do dźwięku
    faza = DWA_PI * np.cumsum(f * vib * nab) / CZESTO
    syg = np.zeros(n)
    for k in range(1, 13):
        if k * f > 7000:
            break
        a = (1.0 if k % 2 else 0.4) / k ** (1.25 / jasnosc)
        syg += a * np.sin(k * faza)
    e = np.minimum(1, t / 0.06)
    e *= np.where(t < dl, 1.0, np.exp(-(t - dl) / (wybrz / 3)))
    e *= 1 - 0.08 * np.exp(-t / 0.5)
    oddech = filtr(szum(0, ziarno + 31, n), f * 1.5, f * 4) * 0.25
    return (syg / 1.8 + oddech) * e * glos


def traba(f, dl, glos=0.4, wybrz=0.2, jasnosc=0.8, ziarno=0, vibrato=0.004):
    """Rzymskie cornu/tuba — instrument dęty blaszany: jaśnieje wraz z głośnością."""
    n = int((dl + wybrz) * CZESTO)
    t = np.arange(n) / CZESTO
    e = np.minimum(1, t / 0.07) ** 1.5
    e *= np.where(t < dl, 1.0, np.exp(-(t - dl) / (wybrz / 3)))
    e *= 1 + 0.12 * np.exp(-((t - 0.08) / 0.05) ** 2)   # akcent ataku
    vib = 1 + vibrato * np.sin(DWA_PI * 4.6 * t + ziarno) * np.clip((t - 0.2) / 0.4, 0, 1)
    nab = 1 - 0.025 * np.exp(-t / 0.035)
    faza = DWA_PI * np.cumsum(f * vib * nab) / CZESTO
    syg = np.zeros(n)
    jas = np.clip(e, 0, 1.1) * jasnosc
    for k in range(1, 18):
        if k * f > 8000:
            break
        syg += np.sin(k * faza + 0.3 * k) * jas ** ((k - 1) * 0.55) / k ** 0.9
    return syg * e * glos / 2.2


def beben(rodzaj="dum", glos=0.5, ziarno=0, f0=None):
    """Bęben ramowy (tympanon): „dum” — niskie uderzenie w środek, „tek” — brzeg."""
    if rodzaj == "dum":
        dl = 0.6
        t = czas(dl)
        f0 = f0 or 105
        f = f0 * (0.65 + 0.35 * np.exp(-t / 0.05))
        ton_ = np.sin(DWA_PI * np.cumsum(f) / CZESTO) * np.exp(-t / 0.18)
        uderz = filtr(szum(dl, ziarno), 80, 900) * np.exp(-t / 0.025)
        x = ton_ + 0.5 * uderz
    elif rodzaj == "wojenny":
        dl = 0.9
        t = czas(dl)
        f0 = f0 or 68
        f = f0 * (0.7 + 0.3 * np.exp(-t / 0.07))
        ton_ = np.sin(DWA_PI * np.cumsum(f) / CZESTO) * np.exp(-t / 0.32)
        ton_ += 0.3 * np.sin(DWA_PI * np.cumsum(f * 1.6) / CZESTO) * np.exp(-t / 0.12)
        uderz = filtr(szum(dl, ziarno), 60, 1400) * np.exp(-t / 0.035)
        x = ton_ + 0.6 * uderz
    else:  # tek
        dl = 0.25
        t = czas(dl)
        x = filtr(szum(dl, ziarno), 1800, 6000) * np.exp(-t / 0.03)
        x += 0.35 * np.sin(DWA_PI * 420 * t) * np.exp(-t / 0.04)
    x *= obwiednia(len(x), 0.001, None, 0.02)
    return x / np.max(np.abs(x)) * glos


def dzwon(f, dl, glos=0.5, czesciowe=(1, 2.0, 3.0, 4.2, 5.4), zaniki=None, ziarno=0):
    """Dzwonek/gong: suma niecałkowitych składowych z różnymi czasami zaniku."""
    t = czas(dl)
    x = np.zeros_like(t)
    zaniki = zaniki or [dl / (1 + 0.8 * i) for i in range(len(czesciowe))]
    for i, (r, z) in enumerate(zip(czesciowe, zaniki)):
        x += np.sin(DWA_PI * f * r * t + ziarno + i) * np.exp(-t / z) / (1 + i * 0.6)
    return x * obwiednia(len(t), 0.002, None, 0.05) * glos / 2


# ---------------------------------------------------------------------------
# Efekty dźwiękowe
# ---------------------------------------------------------------------------

def efekt_klik():
    t = czas(0.07)
    x = np.sin(DWA_PI * 1900 * t) * np.exp(-t / 0.008)
    x += 0.5 * np.sin(DWA_PI * 950 * t) * np.exp(-t / 0.012)
    x += 0.4 * filtr(szum(0.07, 1), 2500, 8000) * np.exp(-t / 0.003)
    return x * obwiednia(len(t), 0.0005, None, 0.01)


def efekt_strona():
    dl = 0.42
    t = czas(dl)
    x = filtr(szum(dl, 2), 900, 6500)
    # szelest: nieregularne drobne trzaski papieru
    rng = np.random.default_rng(3)
    trzaski = np.repeat(rng.uniform(0.4, 1.0, int(dl * 180) + 1), CZESTO // 180 + 1)[: len(t)]
    trzaski = np.convolve(trzaski, np.ones(40) / 40, "same")
    kopula = np.sin(np.pi * np.clip(t / dl, 0, 1)) ** 1.5 * (1 + 0.6 * np.exp(-((t - 0.28) / 0.05) ** 2))
    x *= kopula * trzaski
    x += 0.4 * filtr(szum(dl, 4), 200, 1200) * np.exp(-((t - 0.3) / 0.04) ** 2)  # „klap” na końcu
    return x * obwiednia(len(t), 0.01, None, 0.04)


def uderzenie_dluta(ziarno, wys=1.0):
    dl = 0.32
    t = czas(dl)
    x = filtr(szum(dl, ziarno), 1200, 7000) * np.exp(-t / 0.012)
    for f, z in ((2150, 0.05), (3420, 0.035), (4980, 0.025), (1310, 0.07)):
        x += 0.35 * np.sin(DWA_PI * f * wys * t + ziarno) * np.exp(-t / z)
    x += 0.6 * np.sin(DWA_PI * 140 * t) * np.exp(-t / 0.04)          # głuchy odgłos kamienia
    x += 0.3 * filtr(szum(dl, ziarno + 9), 100, 600) * np.exp(-t / 0.03)
    return x


def efekt_buduj():
    out = np.zeros(int(1.0 * CZESTO))
    for i, (st, g, w) in enumerate(((0.0, 1.0, 1.0), (0.3, 0.85, 1.03), (0.6, 1.0, 0.97))):
        dodaj(out, uderzenie_dluta(10 + i, w) * g, st * CZESTO)
    # drobny gruz osypujący się po uderzeniach
    t = czas(1.0)
    gruz = filtr(szum(1.0, 20), 2500, 8000) * (np.random.default_rng(21).random(len(t)) > 0.997)
    out += 0.6 * np.convolve(gruz, np.exp(-np.arange(80) / 15), "same") * np.exp(-t / 0.6)
    return wycisz_koniec(poglos(out, 0.5, 0.12)[: len(out)], 0.1)


def efekt_gotowe():
    out = np.zeros(int(1.45 * CZESTO))
    for i, n in enumerate(["C6", "E6", "G6", "C7"]):
        dodaj(out, dzwon(nuta(n), 1.3 - i * 0.1, 0.5, (1, 2.0, 3.01, 4.17), [0.9, 0.4, 0.25, 0.15], i),
              i * 0.09 * CZESTO)
    dodaj(out, struna(nuta("C5"), 1.2, 0.35, 1.0, 0.7, 1), 0.27 * CZESTO)
    dodaj(out, struna(nuta("G4"), 1.2, 0.3, 1.0, 0.7, 2), 0.27 * CZESTO)
    return wycisz_koniec(poglos(out, 1.0, 0.18)[: len(out)], 0.25)


def efekt_moneta():
    out = np.zeros(int(0.7 * CZESTO))
    rng = np.random.default_rng(5)
    for i, st in enumerate([0.0, 0.07, 0.13, 0.22, 0.3, 0.41]):
        f = rng.uniform(2300, 3300)
        t = czas(0.35)
        x = np.zeros_like(t)
        for r, z in ((1, 0.12), (1.47, 0.08), (2.09, 0.06), (2.76, 0.04)):
            x += np.sin(DWA_PI * f * r * t + rng.uniform(0, 6)) * np.exp(-t / z) / r
        x += 0.5 * filtr(szum(0.35, 40 + i), 3000, 9000) * np.exp(-t / 0.004)
        dodaj(out, x * (1.0 - i * 0.1), st * CZESTO)
    return wycisz_koniec(poglos(out, 0.4, 0.1)[: len(out)], 0.1)


def efekt_dobrze():
    out = np.zeros(int(1.0 * CZESTO))
    for i, n in enumerate(["C5", "E5", "G5", "C6"]):
        dodaj(out, struna(nuta(n), 0.9, 0.6, 0.9, 0.8, i), i * 0.075 * CZESTO)
        dodaj(out, dzwon(nuta(n) * 2, 0.5, 0.12, (1, 2.0, 3.0), [0.3, 0.15, 0.1], i), i * 0.075 * CZESTO)
    return wycisz_koniec(poglos(out, 0.8, 0.2)[: len(out)], 0.2)


def efekt_zle():
    dl = 0.55
    t = czas(dl)
    x = np.zeros_like(t)
    for f in (98, 103.5):
        faza = DWA_PI * f * t
        x += np.sign(np.sin(faza)) * 0.5 + 0.5 * np.sin(2 * faza)
    x = filtr(x, 60, 900)
    x *= obwiednia(len(t), 0.01, None, 0.12) * (1 - 0.3 * (t / dl))
    return x


def efekt_blad():
    out = np.zeros(int(0.5 * CZESTO))
    for i, (n, st) in enumerate((("E4", 0.0), ("C4", 0.14))):
        t = czas(0.32)
        x = np.sin(DWA_PI * nuta(n) * t) + 0.25 * np.sin(DWA_PI * 2 * nuta(n) * t)
        dodaj(out, x * obwiednia(len(t), 0.015, 0.12, 0.05), st * CZESTO)
    return wycisz_koniec(poglos(out, 0.5, 0.15)[: len(out)], 0.08)


def efekt_fanfara():
    """Fanfara na cornu — tylko dźwięki szeregu harmonicznego (instrument bez wentyli)."""
    out = np.zeros(int(2.5 * CZESTO))
    melodia = [("G3", 0.0, 0.16), ("C4", 0.18, 0.16), ("E4", 0.36, 0.16), ("G4", 0.54, 0.38),
               ("E4", 0.95, 0.12), ("G4", 1.09, 0.12), ("C5", 1.23, 0.9)]
    for i, (n, st, d) in enumerate(melodia):
        dodaj(out, traba(nuta(n), d, 0.6, 0.18, 0.85, i), st * CZESTO)
    # druga trąba i tuba w akordzie końcowym
    dodaj(out, traba(nuta("G4"), 0.9, 0.42, 0.2, 0.75, 11), 1.23 * CZESTO)
    dodaj(out, traba(nuta("E4"), 0.9, 0.32, 0.2, 0.7, 12), 1.23 * CZESTO)
    dodaj(out, traba(nuta("C3"), 1.0, 0.45, 0.2, 0.6, 13), 1.23 * CZESTO)
    dodaj(out, traba(nuta("C3"), 0.5, 0.35, 0.1, 0.6, 14), 0.0)
    return wycisz_koniec(poglos(out, 1.4, 0.22)[: len(out)], 0.15)


def efekt_bebny():
    out = np.zeros(int(2.0 * CZESTO))
    uderzenia = [(0.0, 1.0, 66), (0.28, 0.6, 72), (0.5, 0.95, 62), (0.78, 0.6, 72),
                 (1.0, 0.8, 66), (1.12, 0.55, 70), (1.24, 0.65, 70), (1.36, 0.75, 70), (1.5, 1.0, 58)]
    for i, (st, g, f0) in enumerate(uderzenia):
        dodaj(out, beben("wojenny", g, i, f0), st * CZESTO)
        if g > 0.9:
            dodaj(out, beben("tek", 0.25, 50 + i), st * CZESTO)
    return wycisz_koniec(poglos(out, 1.2, 0.2)[: len(out)], 0.15)


def efekt_miecz():
    dl = 0.85
    t = czas(dl)
    x = 0.9 * filtr(szum(dl, 60), 2000, 9000) * np.exp(-t / 0.006)
    for f, z, a in ((1730, 0.35, 0.6), (2690, 0.28, 0.5), (3870, 0.22, 0.45), (5210, 0.16, 0.35),
                    (6440, 0.1, 0.25), (2705, 0.3, 0.35)):         # bliskie pary -> dudnienie metalu
        x += a * np.sin(DWA_PI * f * t + f) * np.exp(-t / z)
    zgrzyt = filtr(szum(dl, 61), 3000, 7000) * np.exp(-((t - 0.05) / 0.04) ** 2) * 0.3
    x += zgrzyt
    return wycisz_koniec(poglos(x * obwiednia(len(t), 0.0005), 0.6, 0.12)[: len(t)], 0.15)


def efekt_tarcza():
    dl = 0.45
    t = czas(dl)
    f = 95 * (0.6 + 0.4 * np.exp(-t / 0.03))
    x = np.sin(DWA_PI * np.cumsum(f) / CZESTO) * np.exp(-t / 0.09)
    x += 0.7 * filtr(szum(dl, 70), 100, 900) * np.exp(-t / 0.035)     # drewno i skóra
    x += 0.12 * np.sin(DWA_PI * 610 * t) * np.exp(-t / 0.08)           # brązowy umbo
    return wycisz_koniec(poglos(x * obwiednia(len(t), 0.001), 0.4, 0.1)[: len(t)], 0.08)


def efekt_rog():
    """Róg barbarzyńców — niski, chropowaty, z podciągnięciem wysokości."""
    dl = 2.1
    t = czas(dl)
    f0 = nuta("G2")
    zmiana = 0.93 + 0.07 * np.clip(t / 0.35, 0, 1) ** 0.7 - 0.035 * np.clip((t - 1.5) / 0.5, 0, 1) ** 2
    x = np.zeros_like(t)
    for wsp, gl in ((1.0, 1.0), (1.004, 0.6), (0.5, 0.25)):
        faza = DWA_PI * np.cumsum(f0 * wsp * zmiana) / CZESTO
        for k in range(1, 16):
            x += gl * np.sin(k * faza + k) / k ** 0.8
    x = filtr(x, 40, 1400)
    x *= 1 + 0.08 * np.sin(DWA_PI * 6.5 * t)                     # chropowatość
    x += 0.04 * filtr(szum(dl, 80), 300, 2500)
    e = np.minimum(1, t / 0.25) * np.clip((dl - t) / 0.45, 0, 1)
    return wycisz_koniec(poglos(x * e, 1.8, 0.3, jasnosc=2000)[: len(t)], 0.2)


def efekt_tlum():
    """Wiwatujący tłum: wiele głosów (szereg harmoniczny przez formanty) + szum oddechów."""
    dl = 2.2
    t = czas(dl)
    rng = np.random.default_rng(90)
    glosy = np.zeros_like(t)
    for i in range(36):
        f0 = rng.uniform(130, 330)
        st = rng.uniform(0, 0.6)
        dl_g = rng.uniform(0.6, 1.5)
        glisa = 1 + rng.uniform(0.05, 0.25) * np.clip((t - st) / dl_g, 0, 1)
        faza = DWA_PI * np.cumsum(f0 * glisa * (1 + 0.01 * np.sin(DWA_PI * 6 * t + i))) / CZESTO
        g = np.zeros_like(t)
        for k in range(1, int(3500 / f0)):
            g += np.sin(k * faza) / k
        okno = np.clip((t - st) / 0.12, 0, 1) * np.clip((st + dl_g - t) / 0.3, 0, 1)
        glosy += g * okno * rng.uniform(0.4, 1.0)
    glosy = formanty(glosy, [(750, 400, 1.0), (1250, 500, 0.7), (2600, 700, 0.35)])
    oddech = filtr(szum(dl, 91), 300, 4000)
    mod = np.convolve(np.random.default_rng(92).uniform(0.5, 1, len(t)), np.ones(900) / 900, "same")
    x = glosy / np.max(np.abs(glosy)) + 0.6 * oddech * mod
    e = np.clip(t / 0.35, 0, 1) ** 1.5 * np.clip((dl - t) / 0.8, 0, 1)
    return wycisz_koniec(poglos(x * e, 1.2, 0.25)[: len(t)], 0.1)


def efekt_tura():
    """Koniec tury: miękki gong z dudnieniem."""
    out = dzwon(196, 1.5, 1.0, (1, 1.003, 1.52, 2.01, 2.76, 3.42), [1.2, 1.2, 0.6, 0.5, 0.3, 0.2])
    t = czas(1.5)
    out[: len(t)] *= np.minimum(1, t / 0.012)                  # miękka pałka
    out += 0.15 * filtr(szum(1.5, 100), 80, 400) * np.exp(-t / 0.03)
    return wycisz_koniec(poglos(out, 1.0, 0.15)[: len(t)], 0.35)


def efekt_odkrycie():
    """Odkrycie technologii: glissando na lirze w skali doryckiej w górę."""
    out = np.zeros(int(1.45 * CZESTO))
    skala = ["D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5", "D6"]
    for i, n in enumerate(skala):
        dodaj(out, struna(nuta(n), 1.0, 0.45 + 0.03 * i, 0.8, 0.75, i), i * 0.055 * CZESTO)
    for n in ("D5", "A5", "D6"):
        dodaj(out, dzwon(nuta(n), 0.7, 0.12, (1, 2.0, 3.0), [0.5, 0.25, 0.15]), 0.72 * CZESTO)
    return wycisz_koniec(poglos(out, 1.2, 0.25)[: len(out)], 0.25)


def efekt_przedmiot():
    out = np.zeros(int(0.42 * CZESTO))
    for i, (n, st) in enumerate((("A5", 0.0), ("E6", 0.07))):
        dodaj(out, struna(nuta(n), 0.35, 0.5, 0.5, 0.85, i), st * CZESTO)
        dodaj(out, dzwon(nuta(n), 0.3, 0.25, (1, 2.0, 3.0), [0.15, 0.08, 0.05]), st * CZESTO)
    return wycisz_koniec(poglos(out, 0.4, 0.12)[: len(out)], 0.06)


EFEKTY = {
    "klik": efekt_klik, "strona": efekt_strona, "buduj": efekt_buduj, "gotowe": efekt_gotowe,
    "moneta": efekt_moneta, "dobrze": efekt_dobrze, "zle": efekt_zle, "blad": efekt_blad,
    "fanfara": efekt_fanfara, "bebny": efekt_bebny, "miecz": efekt_miecz, "tarcza": efekt_tarcza,
    "rog": efekt_rog, "tlum": efekt_tlum, "tura": efekt_tura, "odkrycie": efekt_odkrycie,
    "przedmiot": efekt_przedmiot,
}


# ---------------------------------------------------------------------------
# Muzyka — silnik pętli
# ---------------------------------------------------------------------------

class Utwor:
    """Bufor pętli o długości dokładnie takty × metrum × próbki na miarę.

    Każde zdarzenie wykraczające poza koniec wraca na początek, a pogłos jest
    splotem kołowym — dzięki temu koniec płynnie przechodzi w początek."""

    def __init__(self, bpm, metrum, takty):
        self.miara = int(round(CZESTO * 60 / bpm))
        self.metrum = metrum
        self.takty = takty
        self.miary = metrum * takty
        self.bufor = np.zeros(self.miary * self.miara)

    def poz(self, miara):
        return int(round(miara * self.miara))

    def dodaj(self, syg, miara):
        dodaj(self.bufor, syg, self.poz(miara), zawijaj=True)

    def sek(self, miary):
        return miary * self.miara / CZESTO

    def melodia(self, zapis, instrument, glos=0.4, legato=0.95, **kw):
        """zapis: 'D5:2 E5:1 R:1 | …' — nuta:długość w miarach (R = pauza)."""
        tokeny = zapis.replace("|", " ").split()
        m = 0.0
        for i, tok in enumerate(tokeny):
            n, d = tok.split(":")
            d = float(d)
            if n != "R":
                self.dodaj(instrument(nuta(n), self.sek(d) * legato, glos, ziarno=i, **kw), m)
            m += d
        assert abs(m - self.miary) < 1e-6, f"melodia ma {m} miar, a utwór {self.miary}"

    def arpeggio(self, akordy, wzor, glos=0.3, czas_zaniku=1.4, jasnosc=0.6, lista_glos=None):
        """Lira: akordy — lista (po jednym na takt) napisów 'D3 F3 A3';
        wzor — lista (miara_w_takcie, indeks_nuty, przesunięcie_oktawy, [mnożnik głośności])."""
        assert len(akordy) == self.takty
        for t_i, akord in enumerate(akordy):
            if not akord:
                continue
            nuty = akord.split()
            for j, el in enumerate(wzor):
                mm, idx, okt = el[:3]
                g = el[3] if len(el) > 3 else 1.0
                if idx >= len(nuty):
                    continue
                f = nuta(nuty[idx]) * 2 ** okt
                dl = min(3.0, czas_zaniku * 2.2)
                self.dodaj(struna(f, dl, glos * g, czas_zaniku, jasnosc, t_i * 31 + j),
                           t_i * self.metrum + mm)

    def bebny(self, wzor, glos=0.3, pomin=()):
        """wzor: lista (miara_w_takcie, rodzaj, głośność) powtarzana w każdym takcie."""
        for t_i in range(self.takty):
            if t_i in pomin:
                continue
            for j, (mm, rodzaj, g) in enumerate(wzor):
                self.dodaj(beben(rodzaj, glos * g, t_i * 17 + j), t_i * self.metrum + mm)

    def burdon(self, nuty, glos=0.12, oddech=0.25):
        """Burdon: częstotliwości dopasowane tak, by w pętli mieściła się całkowita liczba okresów."""
        L = len(self.bufor)
        t = np.arange(L) / CZESTO
        dl = L / CZESTO
        cykle_lfo = max(1, round(dl / 7))
        lfo = 1 - oddech + oddech * (0.5 + 0.5 * np.sin(DWA_PI * cykle_lfo * t / dl))
        for i, n in enumerate(nuty.split()):
            f = round(nuta(n) * dl) / dl
            x = np.zeros(L)
            for k, a in ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.15), (5, 0.1)):
                x += a * np.sin(DWA_PI * f * k * t + i * 1.3 + k)
            self.bufor += x * glos * lfo / (1 + i * 0.4)

    def pady(self, akordy, glos=0.15, jasnosc=0.5, okt=0):
        """Długie dźwięki tuby/rogów na każdy akord (pierwsza i druga nuta akordu)."""
        for t_i, akord in enumerate(akordy):
            if not akord:
                continue
            nuty = akord.split()[:2]
            for j, n in enumerate(nuty):
                self.dodaj(traba(nuta(n) * 2 ** okt, self.sek(self.metrum) * 0.98, glos / (1 + j * 0.5),
                                 0.4, jasnosc, t_i * 7 + j, vibrato=0.002), t_i * self.metrum)

    def gotowe(self, pogl=2.2, mokry=0.3):
        x = poglos(self.bufor, pogl, mokry, ziarno=11, cykliczny=True, jasnosc=3000)
        return filtr(x, 35, 7500, rzad=1)


def rozwin(akordy_tekst):
    """'Dm Dm C G' -> lista napisów z nutami (oktawa 3), pomocniczo dla akordów."""
    slownik = {
        "Dm": "D3 A3 F3 D4", "D": "D3 A3 F#3 D4", "C": "C3 G3 E3 C4", "G": "G2 D3 B3 G3",
        "F": "F2 C3 A3 F3", "Am": "A2 E3 C4 A3", "Em": "E3 B3 G3 E4", "Bb": "Bb2 F3 D4 Bb3",
        "A": "A2 E3 C#4 A3", "Gm": "G2 D3 Bb3 G3", "E": "E3 B3 G#3 E4",
    }
    return [slownik[a] if a != "-" else "" for a in akordy_tekst.split()]


def muzyka_menu():
    """Majestatyczna, powolna — D dorycki, aulos nad lirą i tubami."""
    u = Utwor(63, 4, 14)
    ak = rozwin("Dm Dm C G Dm F C Am Dm G F C Am Dm")
    u.burdon("D2 A2", 0.06)
    u.arpeggio(ak, [(0, 0, 0, 1.0), (1, 1, 0, 0.6), (1.5, 2, 0, 0.5), (2, 3, 0, 0.7), (3, 2, 0, 0.5)],
               0.3, 1.6, 0.55)
    u.pady(ak, 0.09, 0.45, okt=-1)
    u.bebny([(0, "dum", 1.0), (2, "dum", 0.5), (3.5, "tek", 0.3)], 0.22)
    u.melodia("R:4 | D5:2 E5:1 F5:1 | G5:3 F5:1 | D5:2 B4:2 | A4:4 | C5:2 D5:1 F5:1 | E5:2 G5:2 | "
              "E5:4 | F5:2 E5:1 D5:1 | B4:2 D5:2 | C5:2 A4:1 C5:1 | E5:2 C5:2 | A4:3 G4:1 | D5:4",
              aulos, 0.22, 0.97)
    return u.gotowe(2.6, 0.32)


def muzyka_krolestwo():
    """Pasterska — G miksolidyjski, metrum 3/4, aulos jak fujarka pasterza."""
    u = Utwor(92, 3, 28)
    ak = rozwin("G G F G C G F G G C F C G F Dm G G G F G C C G F Am Dm F G")
    u.burdon("G2 D3", 0.05)
    u.arpeggio(ak, [(0, 0, 0, 1.0), (1, 1, 0, 0.55), (1.5, 2, 0, 0.45), (2, 3, 0, 0.6)], 0.28, 1.2, 0.6)
    u.bebny([(0, "dum", 0.8), (2, "tek", 0.4)], 0.2)
    u.melodia("R:3 | R:3 | D5:1 E5:1 F5:1 | G5:2 D5:1 | E5:1.5 D5:0.5 C5:1 | D5:3 | C5:1 A4:1 F4:1 | G4:3 | "
              "B4:1 C5:1 D5:1 | E5:2 C5:1 | F5:1 E5:1 C5:1 | E5:2 R:1 | D5:1 B4:1 G4:1 | A4:1.5 C5:0.5 A4:1 | "
              "F4:2 A4:1 | G4:3 | G5:1 F5:1 E5:1 | D5:2 B4:1 | C5:1 D5:1 A4:1 | G4:2 B4:1 | C5:2 E5:1 | "
              "G5:2 E5:1 | D5:1 E5:1 F5:1 | A5:2 F5:1 | E5:1 C5:1 A4:1 | D5:2 R:1 | C5:1 A4:1 F4:1 | G4:3",
              aulos, 0.2, 0.92, jasnosc=1.2)
    return u.gotowe(1.8, 0.28)


def muzyka_republika():
    """Dostojna, miarowa — A dorycki, równy krok bębna, lira ósemkami."""
    u = Utwor(80, 4, 18)
    ak = ["A2 E3 C4 A3", "A2 E3 C4 A3", "G2 D3 B3 G3", "D3 A3 F#3 D4", "A2 E3 C4 A3", "C3 G3 E3 C4",
          "G2 D3 B3 G3", "E3 B3 G3 E4", "F2 C3 A3 F3", "C3 G3 E3 C4", "G2 D3 B3 G3", "A2 E3 C4 A3",
          "D3 A3 F#3 D4", "A2 E3 C4 A3", "C3 G3 E3 C4", "G2 D3 B3 G3", "E3 B3 G3 E4", "A2 E3 C4 A3"]
    u.burdon("A1 E2", 0.06, 0.15)
    u.arpeggio(ak, [(0, 0, 0, 1.0), (0.5, 1, 0, 0.5), (1, 2, 0, 0.6), (1.5, 1, 0, 0.45), (2, 3, 0, 0.7),
                    (2.5, 1, 0, 0.45), (3, 2, 0, 0.6), (3.5, 1, 0, 0.45)], 0.24, 0.9, 0.55)
    u.pady(ak, 0.07, 0.4, okt=-1)
    u.bebny([(0, "dum", 1.0), (1, "tek", 0.35), (2, "dum", 0.7), (3, "tek", 0.35)], 0.22)
    u.melodia("R:4 | R:4 | B4:2 D5:1 B4:1 | A4:2 F#4:2 | E5:3 D5:1 | C5:2 E5:2 | D5:2 B4:1 G4:1 | B4:4 | "
              "A4:2 C5:1 F5:1 | E5:2 G5:2 | D5:1.5 E5:0.5 D5:1 B4:1 | A4:4 | F#5:2 E5:1 D5:1 | E5:2 C5:2 | "
              "G5:2 E5:1 C5:1 | D5:2 B4:1 D5:1 | B4:3 G#4:1 | A4:4",
              aulos, 0.2, 0.93)
    return u.gotowe(2.2, 0.28)


def muzyka_cesarstwo():
    """Wspaniała, triumfalna — D jońsko-miksolidyjski, melodia na cornu, tuby, bębny."""
    u = Utwor(88, 4, 20)
    ak = ["D3 A3 F#3 D4", "D3 A3 F#3 D4", "G2 D3 B3 G3", "D3 A3 F#3 D4", "C3 G3 E3 C4", "G2 D3 B3 G3",
          "A2 E3 C#4 A3", "D3 A3 F#3 D4", "D3 A3 F#3 D4", "G2 D3 B3 G3", "C3 G3 E3 C4", "D3 A3 F#3 D4",
          "B2 F#3 D4 B3", "G2 D3 B3 G3", "A2 E3 C#4 A3", "A2 E3 C#4 A3", "D3 A3 F#3 D4", "C3 G3 E3 C4",
          "G2 D3 B3 G3", "A2 E3 C#4 A3"]
    u.burdon("D2 A2", 0.05, 0.1)
    u.arpeggio(ak, [(0, 0, 0, 1.0), (0.5, 1, 0, 0.5), (1, 2, 0, 0.6), (1.5, 3, 0, 0.5), (2, 2, 1, 0.5),
                    (2.5, 3, 0, 0.5), (3, 2, 0, 0.6), (3.5, 1, 0, 0.45)], 0.2, 1.0, 0.65)
    u.pady(ak, 0.13, 0.55, okt=0)
    u.bebny([(0, "dum", 1.0), (1, "tek", 0.4), (1.5, "tek", 0.25), (2, "dum", 0.8), (3, "tek", 0.4),
             (3.5, "dum", 0.45)], 0.26)
    u.melodia("A4:1 D5:1 F#5:1 A5:1 | A5:3 F#5:1 | G5:2 B5:1 G5:1 | F#5:2 D5:2 | E5:2 G5:1 E5:1 | "
              "D5:1 B4:1 G4:2 | A4:2 C#5:1 E5:1 | D5:4 | F#5:1.5 E5:0.5 D5:1 F#5:1 | G5:2 D5:2 | "
              "E5:2 G5:1 C5:1 | A5:3 R:1 | F#5:2 D5:1 B4:1 | D5:2 G5:2 | E5:2 C#5:1 A4:1 | E5:4 | "
              "F#5:1 A5:1 F#5:1 D5:1 | E5:2 C5:2 | D5:2 B4:2 | A4:3 R:1",
              traba, 0.24, 0.94, jasnosc=0.7)
    return u.gotowe(2.4, 0.3)


def muzyka_upadek():
    """Melancholijna, oszczędna — E frygijski, powolna, z długimi pauzami."""
    u = Utwor(60, 4, 13)
    ak = ["E3 B3 G3 E4", "F2 C3 A3 F3", "E3 B3 G3 E4", "D3 A3 F3 D4", "A2 E3 C4 A3", "F2 C3 A3 F3",
          "E3 B3 G3 E4", "", "A2 E3 C4 A3", "G2 D3 B3 G3", "F2 C3 A3 F3", "D3 A3 F3 D4", "E3 B3 G3 E4"]
    u.burdon("E2 B2", 0.07, 0.35)
    u.arpeggio(ak, [(0, 0, 0, 0.9), (1.5, 2, 0, 0.5), (2.5, 3, 0, 0.55)], 0.3, 2.0, 0.4)
    u.bebny([(0, "dum", 0.6)], 0.16, pomin=(1, 2, 3, 5, 6, 7, 9, 10, 11))
    u.melodia("R:4 | R:4 | B4:2 C5:1 B4:1 | A4:4 | R:2 C5:1 D5:1 | E5:3 D5:1 | C5:1 B4:1 A4:2 | B4:4 | "
              "R:4 | G4:2 A4:1 B4:1 | C5:2 A4:1 F4:1 | F4:2 E4:2 | E4:4",
              aulos, 0.2, 0.95, jasnosc=0.8)
    return u.gotowe(3.0, 0.38)


def muzyka_bitwa():
    """Napięta, napędzająca — D frygijski, ósemki bębnów wojennych, niskie tuby."""
    u = Utwor(120, 4, 26)
    ak = []
    for blok in ("D2 A2", "D2 A2", "Eb2 Bb2", "D2 A2", "D2 A2", "C2 G2", "Bb1 F2", "C2 G2"):
        ak.append(blok)
    ak = (ak * 4)[: 26]
    u.burdon("D2", 0.07, 0.1)
    # niskie ostinato tub: rytm „dum – dum-dum – dum” na każdy takt
    for t_i, akord in enumerate(ak):
        r = akord.split()[0]
        for mm, d, g in ((0, 0.9, 1.0), (1.5, 0.4, 0.7), (2, 0.9, 0.85), (3, 0.4, 0.6), (3.5, 0.4, 0.7)):
            u.dodaj(traba(nuta(r), u.sek(d), 0.3 * g, 0.12, 0.55, t_i * 5, vibrato=0.0), t_i * 4 + mm)
            u.dodaj(traba(nuta(r) * 2, u.sek(d), 0.12 * g, 0.12, 0.5, t_i * 5 + 1, vibrato=0.0), t_i * 4 + mm)
    u.bebny([(0, "wojenny", 1.0), (0.5, "tek", 0.35), (1, "dum", 0.6), (1.5, "tek", 0.35),
             (2, "wojenny", 0.85), (2.5, "dum", 0.5), (3, "tek", 0.45), (3.5, "tek", 0.35)], 0.3)
    # nerwowe szarpnięcia liry w wysokim rejestrze
    lira = [("D4 A4 D5 Eb5" if "Eb" in a else "D4 A4 D5 F5") for a in ak]
    u.arpeggio(lira, [(0.5, 2, 0, 0.6), (1.75, 3, 0, 0.5), (2.5, 2, 0, 0.6), (3.25, 1, 0, 0.5)], 0.12, 0.5, 0.7)
    u.melodia("R:4 | R:4 | R:4 | R:4 | D4:2 Eb4:1 F4:1 | G4:2 F4:1 Eb4:1 | D4:4 | R:4 | "
              "A4:2 Bb4:1 A4:1 | G4:2 F4:2 | Eb4:3 D4:1 | D4:4 | R:4 | R:4 | R:4 | R:4 | "
              "F4:2 G4:1 A4:1 | Bb4:2 A4:2 | G4:1 F4:1 Eb4:2 | D4:4 | C4:2 D4:2 | Eb4:2 D4:2 | D4:4 | R:4 | "
              "R:4 | R:4",
              traba, 0.2, 0.95, jasnosc=0.75)
    return u.gotowe(1.6, 0.22)


MUZYKA = {
    "muzyka_menu": muzyka_menu, "muzyka_krolestwo": muzyka_krolestwo,
    "muzyka_republika": muzyka_republika, "muzyka_cesarstwo": muzyka_cesarstwo,
    "muzyka_upadek": muzyka_upadek, "muzyka_bitwa": muzyka_bitwa,
}


# ---------------------------------------------------------------------------
# Główny program
# ---------------------------------------------------------------------------

def opis(sciezka):
    with wave.open(sciezka, "rb") as w:
        n = w.getnframes()
        dane = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float64)
    szczyt = 20 * np.log10(np.max(np.abs(dane)) / 32768 + 1e-12)
    rms = 20 * np.log10(np.sqrt(np.mean((dane / 32768) ** 2)) + 1e-12)
    szew = abs(dane[-1] - dane[0]) / 32768   # skok na styku pętli (istotny dla muzyki)
    return n / CZESTO, os.path.getsize(sciezka), szczyt, rms, szew


def main():
    os.makedirs(KATALOG, exist_ok=True)
    wybrane = set(sys.argv[1:])
    wiersze = []
    for slownik, szczyt in ((EFEKTY, SZCZYT_EFEKTY), (MUZYKA, SZCZYT_MUZYKA)):
        for nazwa, fun in slownik.items():
            if wybrane and nazwa not in wybrane:
                continue
            sciezka = zapisz_wav(nazwa, fun(), szczyt, petla=slownik is MUZYKA)
            wiersze.append((nazwa, *opis(sciezka)))
            print(f"  zapisano {nazwa}.wav", flush=True)
    print(f"\n{'plik':<22}{'czas [s]':>9}{'rozmiar':>11}{'szczyt dBFS':>13}{'RMS dBFS':>10}{'szew':>8}")
    suma = 0
    for nazwa, dl, rozm, szczyt, rms, szew in wiersze:
        suma += rozm
        print(f"{nazwa + '.wav':<22}{dl:9.2f}{rozm / 1024:9.0f} kB{szczyt:13.2f}{rms:10.1f}{szew:8.3f}")
    print(f"{'RAZEM':<22}{'':>9}{suma / 1024 / 1024:8.2f} MB")


if __name__ == "__main__":
    main()
