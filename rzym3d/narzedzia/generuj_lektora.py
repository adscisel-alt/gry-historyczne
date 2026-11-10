"""Lektor: nagrywa wszystkie teksty gry „Roman Empire” polskimi głosami syntezatora Piper (offline).

Wymaga: pip install piper-tts  oraz ffmpeg. Głosy pobiera z rhasspy/piper-voices (Hugging Face).
Wynik: godot/audio/glos/<md5 tekstu>.ogg — gra odtwarza plik, jeśli istnieje (bez nich działa bez lektora).
Nagrania nie trafiają do repozytorium — powstają w GitHub Actions.

    python narzedzia/generuj_lektora.py                 # głosy z Hugging Face
    python narzedzia/generuj_lektora.py --model a.onnx  # jeden lokalny głos dla wszystkich (test)
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import wave

TU = os.path.dirname(os.path.abspath(__file__))
DANE = os.path.join(TU, "..", "godot", "dane", "dane.json")
WYJSCIE = os.path.join(TU, "..", "godot", "audio", "glos")
BAZA = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/{n}/{q}/{v}"

GLOSY = {
    "damian": ("pl_PL-darkman-medium", 1.0),
    "narrator": ("pl_PL-mc_speech-medium", 1.05),
}


def kwestie(d):
    """Wszystkie teksty czytane przez lektora: (mówca, tekst)."""
    w = []
    for r in d["rozdzialy"]:
        w += [("damian", t) for t in r["wstep"]]
        w.append(("narrator", r["koniec"]))
        w += [("narrator", r["bitwa"]["opis"]), ("narrator", r["bitwa"]["po"])]
        w += [("narrator", t[3]) for t in r["mapa_imperium"]["trasa"]]
        w += [("narrator", t) for t in r["mapa_imperium"]["podpisy"]]
        w += [("narrator", z[4]) for z in r["zabytki"]]
    w += [("damian", t) for t in d["rady"]]
    w += [("narrator", t["p"]) for t in d["technologie"].values()]
    w += [("narrator", q["p"]) for q in d["pytania"]]
    for wd in d["wydarzenia"].values():
        w += [("narrator", wd["opis"]), ("narrator", wd["komentarz"])]
    w += [("narrator", l["opis"]) for l in d["losowe"]]
    w += [("narrator", z["opis"]) for z in d["znajdzki"].values()]
    w += [("narrator", e["tekst"]) for e in d["encyklopedia"]]
    w.append(("narrator", d["final"]))
    widziane, wynik = set(), []
    for mowca, tekst in w:
        if tekst not in widziane:
            widziane.add(tekst)
            wynik.append((mowca, tekst))
    return wynik


def oczysc(t):
    t = t.replace("—", ",").replace("„", "").replace("”", "").replace("…", ".").replace("×", " razy ")
    t = re.sub(r"(\d+)–(\d+)", r"\1 do \2", t).replace("–", ",")
    t = t.replace("p.n.e.", "przed naszą erą").replace("n.e.", "naszej ery").replace("SPQR", "Es Pe Ku Er")
    t = re.sub(r"\b(\d+) w\.", r"\1 wieku", t)
    for rz, sl in (("VIII w.", "ósmym wieku"), ("III w.", "trzecim wieku"), ("II w.", "drugim wieku"), ("IV w.", "czwartym wieku"),
                   ("V w.", "piątym wieku"), ("XII tablic", "dwunastu tablic"), ("III wieku", "trzeciego wieku")):
        t = t.replace(rz, sl)
    return re.sub(r"\s+", " ", t).strip()


def pobierz_glos(nazwa, cache):
    _, kto, jakosc = nazwa.split("-")
    os.makedirs(cache, exist_ok=True)
    for ext in (".onnx", ".onnx.json"):
        cel = os.path.join(cache, nazwa + ext)
        if not os.path.exists(cel):
            print("pobieram", nazwa + ext, flush=True)
            urllib.request.urlretrieve(BAZA.format(n=kto, q=jakosc, v=nazwa + ext), cel)
    return os.path.join(cache, nazwa + ".onnx")


def syntezuj(glos, tekst, sciezka_wav, tempo):
    with wave.open(sciezka_wav, "wb") as wf:
        try:
            from piper import SynthesisConfig
            glos.synthesize_wav(tekst, wf, syn_config=SynthesisConfig(length_scale=tempo))
        except ImportError:
            glos.synthesize(tekst, wf, length_scale=tempo)


def main():
    from piper import PiperVoice
    d = json.load(open(DANE, encoding="utf-8"))
    os.makedirs(WYJSCIE, exist_ok=True)
    lokalny = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else None
    cache = os.path.join(tempfile.gettempdir(), "piper_voices")
    zaladowane = {}
    lista = kwestie(d)
    nowe = 0
    for mowca, tekst in lista:
        klucz = hashlib.md5(tekst.encode("utf-8")).hexdigest()   # = String.md5_text() w Godocie
        ogg = os.path.join(WYJSCIE, klucz + ".ogg")
        if os.path.exists(ogg):
            continue
        nazwa, tempo = GLOSY.get(mowca, GLOSY["narrator"])
        model = lokalny or pobierz_glos(nazwa, cache)
        if model not in zaladowane:
            zaladowane[model] = PiperVoice.load(model)
        wav = os.path.join(tempfile.gettempdir(), klucz + ".wav")
        syntezuj(zaladowane[model], oczysc(tekst), wav, tempo)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", wav, "-ac", "1", "-c:a", "libvorbis", "-q:a", "3",
                        ogg], check=True)
        os.remove(wav)
        nowe += 1
    print("Lektor: %d kwestii (%d nowych) w %s" % (len(lista), nowe, os.path.normpath(WYJSCIE)))


if __name__ == "__main__":
    main()
