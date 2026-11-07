"""Lektor: nagrywa wszystkie kwestie gry polskimi głosami syntezatora Piper (offline).

Wymaga: pip install piper-tts  oraz ffmpeg. Głosy pobiera z rhasspy/piper-voices (Hugging Face).
Wynik: godot/audio/glos/<md5 tekstu>.ogg — gra odtwarza plik, jeśli istnieje (bez nich działa bez lektora).

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

# głos i tempo (length_scale: >1 wolniej) dla każdej postaci
GLOSY = {
    "dmowski": ("pl_PL-darkman-medium", 1.0),
    "hanna": ("pl_PL-gosia-medium", 1.0),
    "narrator": ("pl_PL-mc_speech-medium", 1.05),
    "zamoyski": ("pl_PL-mc_speech-medium", 1.1),
    "haller": ("pl_PL-darkman-medium", 0.95),
    "paderewski": ("pl_PL-mc_speech-medium", 0.95),
    "clemenceau": ("pl_PL-darkman-medium", 1.15),
    "wilson": ("pl_PL-mc_speech-medium", 1.0),
    "pilsudski": ("pl_PL-darkman-medium", 1.1),
}


def kwestie(d):
    """Wszystkie teksty czytane przez lektora: (mówca, tekst)."""
    w = []
    for r in d["rozmowy"].values():
        w += [tuple(k) for k in r["kwestie"] + r["po"]]
    for lista in d["luzne"].values():
        w += [tuple(k) for k in lista]
    for r in d["rozdzialy"].values():
        w += [tuple(k) for k in r["koniec"]]
        w.append(("narrator", r["wstep"]))
    for lista in d["przerywniki"].values():
        w += [tuple(k) for k in lista]
    w += [tuple(k) for k in d["powitanie"]]
    for klucz, q in d["quiz_glowny"].items():
        w.append((klucz.split(":")[0], q["pytanie"]))
    for npc, lista in d["zagadki"].items():
        w.append((npc, "Mam dla pana zagadkę! Za dobrą odpowiedź dostanie pan Punkty Wiedzy."))
        w += [(npc, q["pytanie"]) for q in lista]
    w += [("narrator", r["pytanie"]) for r in d["przemowienie"]]
    w += [("narrator", v[1]) for v in d["wiedza"].values()]
    w += [("narrator", e[3]) for e in d["os_czasu"]]
    for m in d["mapy_podrozy"].values():
        w += [("narrator", t) for t in m["podpisy"]]
        w += [("narrator", t[3]) for t in m["trasa"]]
    widziane, wynik = set(), []
    for mowca, tekst in w:
        if tekst not in widziane:
            widziane.add(tekst)
            wynik.append((mowca, tekst))
    return wynik


def oczysc(t):
    t = t.replace("—", ",").replace("–", " do ").replace("„", "").replace("”", "").replace("…", ".")
    t = re.sub(r"(\d{4})–(\d{4})", r"\1 do \2", t)
    t = t.replace("PW", "Punktów Wiedzy").replace("KNP", "Ka En Pe").replace("USA", "U Es A")
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
