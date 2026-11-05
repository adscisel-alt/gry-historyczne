# -*- coding: utf-8 -*-
"""Syntetyzuje dźwięki i muzykę gry i zapisuje je jako assets/audio/*.ogg (wymaga ffmpeg)."""
import os
import subprocess
import sys
import tempfile
import wave

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kronika import audio  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "audio")


def write(name, samples):
    os.makedirs(OUT, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        path = tmp.name
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(audio.RATE)
        w.writeframes(samples.tobytes())
    dst = os.path.join(OUT, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-c:a", "libvorbis", "-q:a", "3", dst], check=True)
    os.remove(path)
    print("zapisano", dst)


if __name__ == "__main__":
    for name, fn in audio.sfx_generators().items():
        write(name, fn())
    for name, fn in audio.music_generators().items():
        write(name, fn())
