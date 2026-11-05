# -*- coding: utf-8 -*-
"""Proceduralne dźwięki i średniowieczna melodia (bez plików audio)."""
import math
import random
import threading
from array import array

import pygame

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
        _ok = pygame.mixer.get_init() is not None
    except Exception:
        _ok = False
    if not _ok:
        return
    try:
        _sounds["click"] = _make(_tone_seq([(880, 0.04)], wave="sq", vol=0.18))
        _sounds["coin"] = _make(_tone_seq([(1320, 0.06), (1760, 0.12)], wave="tri", vol=0.3))
        _sounds["build"] = _make(_noise_hits(3, 0.07, 0.35))
        _sounds["hit"] = _make(_noise_hits(1, 0.18, 0.5, low=True))
        _sounds["good"] = _make(_tone_seq([(523, 0.1), (659, 0.1), (784, 0.22)], wave="tri", vol=0.32))
        _sounds["bad"] = _make(_tone_seq([(330, 0.15), (262, 0.3)], wave="sq", vol=0.18))
        _sounds["fanfare"] = _make(_tone_seq([(392, 0.14), (523, 0.14), (659, 0.14), (784, 0.4), (659, 0.14), (784, 0.6)],
                                             wave="sq", vol=0.2))
        _sounds["drum"] = _make(_noise_hits(4, 0.12, 0.45, low=True, gap=0.25))
    except Exception:
        pass
    threading.Thread(target=_bg_music, daemon=True).start()


_want = False


def _bg_music():
    try:
        _sounds["music"] = _make(_music())
        if _want:
            start_music()
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


def _music():
    """Melodia w skali doryckiej d (jak dawne pieśni), lutnia + burdon."""
    scale = [146.83, 164.81, 174.61, 196.0, 220.0, 246.94, 261.63, 293.66, 329.63, 349.23, 392.0]
    phrases = [
        [7, 8, 9, 8, 7, 6, 7, 4, 5, 6, 7, 6, 5, 4, 3, 4],
        [4, 5, 7, 7, 8, 7, 6, 5, 4, 5, 6, 5, 4, 3, 2, 0],
        [7, 9, 10, 9, 8, 7, 8, 9, 7, 6, 5, 6, 7, 5, 4, 4],
        [4, 3, 4, 5, 7, 6, 5, 4, 3, 4, 2, 3, 1, 2, 0, 0],
    ]
    beat = 0.28
    total = int(RATE * beat * 16 * len(phrases))
    buf = [0.0] * total
    t0 = 0
    for ph in phrases:
        for k, idx in enumerate(ph):
            f = scale[idx]
            n = int(RATE * beat * (2 if k == len(ph) - 1 else 1))
            start = t0 + int(RATE * beat * k)
            for i in range(min(n, total - start)):
                tt = i / RATE
                env = math.exp(-tt * 5.5)
                v = (math.sin(math.tau * f * tt) + 0.45 * math.sin(math.tau * 2 * f * tt) + 0.2 * math.sin(math.tau * 3 * f * tt))
                buf[start + i] += v * env * 0.16
        t0 += int(RATE * beat * 16)
    # burdon (dudy) D + A
    for i in range(total):
        tt = i / RATE
        buf[i] += 0.05 * (math.sin(math.tau * 73.42 * tt) + 0.6 * math.sin(math.tau * 110.0 * tt))
    # bęben co 2 takty
    for b in range(0, total, int(RATE * beat * 4)):
        for i in range(int(RATE * 0.15)):
            if b + i < total:
                buf[b + i] += math.sin(math.tau * 60 * i / RATE) * math.exp(-i / RATE * 25) * 0.25
    return array("h", (int(max(-1, min(1, v)) * 32767) for v in buf))


def play(name):
    if _ok and name in _sounds:
        try:
            _sounds[name].play()
        except Exception:
            pass


def start_music():
    global _music_ch, _want
    _want = True
    if _ok and music_on and "music" in _sounds and (_music_ch is None or not _music_ch.get_busy()):
        _sounds["music"].set_volume(0.55)
        _music_ch = _sounds["music"].play(loops=-1)


def toggle_music():
    global music_on
    music_on = not music_on
    if not _ok:
        return
    if music_on:
        start_music()
    elif _music_ch is not None:
        _music_ch.stop()
