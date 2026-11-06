# -*- coding: utf-8 -*-
"""Dźwięki i muzyka.

Wszystko jest syntetyzowane kodem (tools/make_audio.py zapisuje to do assets/audio/*.ogg).
Gra najpierw wczytuje gotowe pliki OGG (szybki start, działa też w przeglądarce),
a gdy ich brak – syntetyzuje dźwięki na miejscu.
"""
import math
import os
import random
import sys
import threading
from array import array

import pygame

WEB = sys.platform == "emscripten"
_AUDIO_DIR = os.path.join(getattr(sys, "_MEIPASS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")),
                          "assets", "audio")

RATE = 22050
_sounds = {}
_ok = False
music_on = True
_music_ch = None


def init():
    global _ok
    try:
        pygame.mixer.pre_init(RATE, -16, 1, 512)
        pygame.mixer.init(RATE, -16, 1, 512)
        pygame.mixer.set_num_channels(8)
        _ok = pygame.mixer.get_init() is not None
    except Exception:
        _ok = False
    if not _ok:
        return
    if os.path.isdir(_AUDIO_DIR):
        for fn in os.listdir(_AUDIO_DIR):
            if fn.endswith(".ogg"):
                try:
                    _sounds[fn[:-4]] = pygame.mixer.Sound(os.path.join(_AUDIO_DIR, fn))
                except Exception:
                    pass
        if "music" in _sounds:
            return
    _synth_sfx()
    if not WEB:
        threading.Thread(target=_bg_music, daemon=True).start()


SFX = {}


def _synth_sfx():
    for name, fn in sfx_generators().items():
        try:
            _sounds[name] = _make(fn())
        except Exception:
            pass


def sfx_generators():
    return {
        "click": lambda: _tone_seq([(880, 0.04)], wave="sq", vol=0.18),
        "coin": lambda: _tone_seq([(1320, 0.06), (1760, 0.12)], wave="tri", vol=0.3),
        "build": lambda: _noise_hits(3, 0.07, 0.35),
        "hit": lambda: _noise_hits(1, 0.18, 0.5, low=True),
        "good": lambda: _tone_seq([(523, 0.1), (659, 0.1), (784, 0.22)], wave="tri", vol=0.32),
        "bad": lambda: _tone_seq([(330, 0.15), (262, 0.3)], wave="sq", vol=0.18),
        "fanfare": lambda: _tone_seq([(392, 0.14), (523, 0.14), (659, 0.14), (784, 0.4), (659, 0.14), (784, 0.6)],
                                     wave="sq", vol=0.2),
        "drum": lambda: _noise_hits(4, 0.12, 0.45, low=True, gap=0.25),
    }


_want = "music"
_current = None


def _bg_music():
    try:
        for name, fn in music_generators().items():
            _sounds[name] = _make(fn())
            if _want == name:
                start_music(name)
    except Exception:
        pass


def _make(samples):
    return pygame.mixer.Sound(buffer=samples.tobytes())


def _osc(wave, ph):
    if wave == "sq":
        return 1.0 if (ph % 1.0) < 0.5 else -1.0
    if wave == "tri":
        p = ph % 1.0
        return 4 * p - 1 if p < 0.5 else 3 - 4 * p
    return math.sin(ph * math.tau)


def _tone_seq(notes, wave="sin", vol=0.3):
    out = array("h")
    for f, d in notes:
        n = int(RATE * d)
        for i in range(n):
            env = min(1.0, i / 200) * (1 - i / n) ** 1.5
            out.append(int(32767 * vol * env * _osc(wave, f * i / RATE)))
    return out


def _noise_hits(count, dur, vol, low=False, gap=0.09):
    r = random.Random(3)
    out = array("h")
    prev = 0.0
    for _ in range(count):
        n = int(RATE * dur)
        for i in range(n):
            env = (1 - i / n) ** 3
            x = r.uniform(-1, 1)
            if low:
                prev = prev * 0.92 + x * 0.08
                x = prev * 6 + math.sin(i / RATE * math.tau * 70) * 0.6
            out.append(int(max(-1, min(1, x * vol * env)) * 32767))
        out.extend([0] * int(RATE * gap))
    return out


# skala dorycka d (dawne pieśni) – indeksy w melodiach
SCALE = [146.83, 164.81, 174.61, 196.0, 220.0, 246.94, 261.63, 293.66, 329.63, 349.23, 392.0, 440.0]

THEMES = {
    # menu: lutnia i burdon
    "music": {"beat": 0.28, "inst": "lute", "drum": 4, "drone": (73.42, 110.0), "phrases": [
        [7, 8, 9, 8, 7, 6, 7, 4, 5, 6, 7, 6, 5, 4, 3, 4],
        [4, 5, 7, 7, 8, 7, 6, 5, 4, 5, 6, 5, 4, 3, 2, 0],
        [7, 9, 10, 9, 8, 7, 8, 9, 7, 6, 5, 6, 7, 5, 4, 4],
        [4, 3, 4, 5, 7, 6, 5, 4, 3, 4, 2, 3, 1, 2, 0, 0]]},
    # Epoka Plemienna: piszczałka pasterska i bęben ramowy
    "music_0": {"beat": 0.32, "inst": "flute", "drum": 2, "drone": (73.42,), "phrases": [
        [4, 7, 7, 8, 7, 4, 3, 4, 4, 7, 9, 8, 7, 7, 4, 4],
        [8, 9, 11, 9, 8, 7, 8, 7, 4, 3, 4, 7, 4, 3, 0, 0],
        [4, 7, 7, 8, 7, 4, 3, 4, 7, 8, 9, 8, 7, 4, 3, 4],
        [3, 4, 3, 0, 3, 4, 7, 4, 3, 0, 3, 2, 0, 0, 0, 0]]},
    # Epoka Piastowska: chorał przy organach
    "music_1": {"beat": 0.42, "inst": "organ", "drum": 0, "drone": (73.42, 110.0), "phrases": [
        [0, 2, 3, 4, 4, 3, 4, 7, 7, 6, 4, 3, 4, 3, 2, 0],
        [4, 7, 7, 8, 7, 6, 4, 4, 3, 4, 6, 4, 3, 2, 0, 0],
        [7, 8, 9, 8, 7, 7, 6, 4, 6, 7, 6, 4, 3, 4, 3, 2],
        [3, 4, 3, 2, 0, 2, 3, 4, 3, 2, 1, 0, 0, 0, 0, 0]]},
    # Epoka Zamków: żywa estampida, lutnia i tamburyn
    "music_2": {"beat": 0.2, "inst": "lute", "drum": 1, "drone": (73.42, 110.0), "phrases": [
        [7, 7, 9, 7, 8, 9, 10, 9, 8, 7, 8, 9, 7, 6, 5, 4],
        [7, 7, 9, 7, 8, 9, 10, 9, 11, 10, 9, 8, 7, 8, 7, 7],
        [4, 5, 6, 7, 6, 5, 4, 3, 4, 5, 6, 5, 4, 3, 2, 0],
        [4, 5, 6, 7, 8, 9, 10, 9, 8, 7, 6, 5, 4, 3, 4, 4]]},
    # Epoka Jagiellońska: uroczyste trąby i kotły
    "music_3": {"beat": 0.3, "inst": "brass", "drum": 2, "drone": (73.42, 110.0, 146.83), "phrases": [
        [4, 4, 7, 7, 8, 7, 6, 7, 4, 4, 7, 8, 9, 8, 7, 7],
        [9, 9, 10, 9, 8, 7, 8, 9, 7, 6, 4, 6, 7, 6, 4, 4],
        [4, 4, 7, 7, 8, 7, 6, 7, 9, 10, 11, 10, 9, 8, 7, 7],
        [7, 6, 4, 3, 4, 6, 7, 6, 4, 3, 2, 3, 4, 4, 4, 4]]},
}


def _voice(inst, f, tt):
    if inst == "flute":
        env = min(1, tt * 20) * math.exp(-tt * 1.8)
        vib = math.sin(math.tau * 5 * tt) * 0.004
        return (math.sin(math.tau * f * 2 * tt * (1 + vib)) + 0.15 * math.sin(math.tau * 4 * f * tt)) * env * 0.9
    if inst == "organ":
        env = min(1, tt * 6) * math.exp(-tt * 0.9)
        return (math.sin(math.tau * f * tt) + 0.5 * math.sin(math.tau * 2 * f * tt) + 0.3 * math.sin(math.tau * 3 * f * tt)
                + 0.2 * math.sin(math.tau * 4 * f * tt)) * env * 0.6
    if inst == "brass":
        env = min(1, tt * 14) * math.exp(-tt * 1.6)
        v = 0.0
        for h in range(1, 6):
            v += math.sin(math.tau * h * f * tt) / h
        return v * env * 0.7
    env = math.exp(-tt * 5.5)   # lutnia
    return (math.sin(math.tau * f * tt) + 0.45 * math.sin(math.tau * 2 * f * tt) + 0.2 * math.sin(math.tau * 3 * f * tt)) * env


def _music(theme="music"):
    th = THEMES[theme]
    beat, inst, phrases = th["beat"], th["inst"], th["phrases"]
    total = int(RATE * beat * 16 * len(phrases))
    buf = [0.0] * total
    t0 = 0
    for ph in phrases:
        for k, idx in enumerate(ph):
            if k and ph[k - 1] == idx and inst in ("organ",):
                continue
            f = SCALE[idx]
            n = int(RATE * beat * (3 if k == len(ph) - 1 else 2))
            start = t0 + int(RATE * beat * k)
            for i in range(min(n, total - start)):
                buf[start + i] += _voice(inst, f, i / RATE) * 0.16
        t0 += int(RATE * beat * 16)
    for i in range(total):
        tt = i / RATE
        buf[i] += 0.04 * sum(math.sin(math.tau * d * tt) * (0.6 ** j) for j, d in enumerate(th["drone"]))
    if th["drum"]:
        step = int(RATE * beat * th["drum"])
        r = random.Random(5)
        for k, b in enumerate(range(0, total, step)):
            low = k % 2 == 0 or th["drum"] > 1
            for i in range(int(RATE * 0.15)):
                if b + i < total:
                    if low:
                        buf[b + i] += math.sin(math.tau * 60 * i / RATE) * math.exp(-i / RATE * 25) * 0.25
                    else:
                        buf[b + i] += r.uniform(-1, 1) * math.exp(-i / RATE * 40) * 0.08
    return array("h", (int(max(-1, min(1, v)) * 32767) for v in buf))


def music_generators():
    return {name: (lambda name=name: _music(name)) for name in THEMES}


def play(name):
    if _ok and name in _sounds:
        try:
            _sounds[name].play()
        except Exception:
            pass


def start_music(track=None):
    """Włącza (lub zmienia) ścieżkę muzyczną: 'music' – menu, 'music_0'..'music_3' – epoki."""
    global _music_ch, _want, _current
    track = track or _want or "music"
    _want = track
    if not (_ok and music_on):
        return
    if track not in _sounds:
        track = "music" if "music" in _sounds else None
        if not track:
            return
    if _current == track and _music_ch is not None and _music_ch.get_busy():
        return
    if _music_ch is not None:
        try:
            _music_ch.fadeout(400)
        except Exception:
            pass
    _sounds[track].set_volume(0.5)
    _music_ch = _sounds[track].play(loops=-1, fade_ms=600)
    _current = track


def toggle_music():
    global music_on, _current
    music_on = not music_on
    if not _ok:
        return
    if music_on:
        _current = None
        start_music()
    elif _music_ch is not None:
        _music_ch.stop()


# ---------------------------------------------------------------- lektor
_VOICE_DIR = os.path.join(os.path.dirname(_AUDIO_DIR), "voice")
voice_on = True
_voice_ch = None


def has_voice(name):
    return os.path.exists(os.path.join(_VOICE_DIR, name + ".ogg"))


def play_voice(name):
    """Odtwarza nagranie lektora (jeśli jest) i ścisza muzykę na czas czytania."""
    global _voice_ch
    stop_voice()
    if not (_ok and voice_on and has_voice(name)):
        return False
    try:
        snd = pygame.mixer.Sound(os.path.join(_VOICE_DIR, name + ".ogg"))
        _voice_ch = pygame.mixer.Channel(7)
        _voice_ch.play(snd)
        if _music_ch is not None:
            _music_ch.set_volume(0.35)
        return True
    except Exception:
        return False


def stop_voice():
    global _voice_ch
    if _voice_ch is not None:
        try:
            _voice_ch.stop()
        except Exception:
            pass
        _voice_ch = None
    if _music_ch is not None:
        try:
            _music_ch.set_volume(1.0)
        except Exception:
            pass


def voice_busy():
    return _voice_ch is not None and _voice_ch.get_busy()
