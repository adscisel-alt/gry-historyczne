# -*- coding: utf-8 -*-
"""Lektor: czyta kroniki rozdziałów, zakończenia i finał głosem syntezatora Piper (offline, polski głos).

Wymaga: pip install piper-tts  oraz ffmpeg. Głos pobiera z repozytorium rhasspy/piper-voices (Hugging Face).
Wynik: assets/voice/*.ogg  (gra odtwarza je w ekranach kroniki; bez tych plików gra działa bez lektora).

python tools/make_voice.py [--voice pl_PL-darkman-medium]
"""
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from kronika import data  # noqa: E402

OUT = os.path.join(HERE, "..", "assets", "voice")
VOICE = sys.argv[sys.argv.index("--voice") + 1] if "--voice" in sys.argv else "pl_PL-darkman-medium"
BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/{n}/{q}/{v}"


def fetch_voice(cache):
    lang, name, quality = VOICE.split("-")
    os.makedirs(cache, exist_ok=True)
    paths = []
    for ext in (".onnx", ".onnx.json"):
        dst = os.path.join(cache, VOICE + ext)
        if not os.path.exists(dst):
            url = BASE.format(n=name, q=quality, v=VOICE + ext)
            print("pobieram", url, flush=True)
            urllib.request.urlretrieve(url, dst)
        paths.append(dst)
    return paths[0]


def clean(text):
    t = text.replace("–", ",").replace("„", "").replace("”", "").replace("“", "")
    t = t.replace("…", ".").replace("...", ".")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def synth(voice, text, wav_path):
    try:
        with wave.open(wav_path, "wb") as wf:
            voice.synthesize_wav(text, wf)          # piper-tts >= 1.3
    except AttributeError:
        with wave.open(wav_path, "wb") as wf:
            voice.synthesize(text, wf)              # starsze piper-tts


def main():
    from piper import PiperVoice
    model = fetch_voice(os.path.join(tempfile.gettempdir(), "piper_voices"))
    voice = PiperVoice.load(model)
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for ch in data.CHAPTERS:
        jobs.append((f"kronika_{ch['id']}", ch["title"].split(": ", 1)[-1] + ". " + " ".join(ch["chronicle"])))
        jobs.append((f"zwyciestwo_{ch['id']}", ch["victory"]))
    jobs.append(("zakonczenie", " ".join(data.ENDING)))
    total = 0.0
    for name, text in jobs:
        wav = os.path.join(tempfile.gettempdir(), name + ".wav")
        synth(voice, clean(text), wav)
        with wave.open(wav) as w:
            dur = w.getnframes() / w.getframerate()
        total += dur
        dst = os.path.join(OUT, name + ".ogg")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-ac", "1", "-ar", "22050",
                        "-c:a", "libvorbis", "-q:a", "1", dst], check=True)
        os.remove(wav)
        print(f"zapisano {dst}  ({dur:.0f} s)", flush=True)
    print(f"Lektor gotowy: {len(jobs)} nagrań, łącznie {total / 60:.1f} min")
    if len(jobs) < 19 or total < 120:
        sys.exit("BŁĄD: za mało nagrań lektora")


if __name__ == "__main__":
    main()
