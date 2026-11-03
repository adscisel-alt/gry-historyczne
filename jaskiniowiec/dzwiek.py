"""Syntezowane efekty dźwiękowe i muzyka (bez zewnętrznych plików)."""
import array
import math
import random
import threading
import pygame

RATE = 22050


class Audio:
    def __init__(self):
        self.ok = False
        self.muted = False
        self.sfx = {}
        self.music = {}
        self.current = None
        self.channel = None
        try:
            pygame.mixer.pre_init(RATE, -16, 2, 512)
            pygame.mixer.init()
            freq, _fmt, ch = pygame.mixer.get_init()
            self.rate = freq
            self.channels = ch
            pygame.mixer.set_num_channels(16)
            self.ok = True
        except Exception:
            self.ok = False
            return
        self._make_sfx()
        self.wanted = None
        threading.Thread(target=self._make_music, daemon=True).start()

    # -------------------------------------------------------------- narzędzia
    def _sound(self, samples, vol=0.5):
        out = array.array('h')
        ch = self.channels
        for v in samples:
            iv = int(max(-1.0, min(1.0, v * vol)) * 32000)
            out.append(iv)
            if ch == 2:
                out.append(iv)
        return pygame.mixer.Sound(buffer=out.tobytes())

    def _tone(self, f0, f1, dur, wave='sine', decay=3.0, noise=0.0):
        n = int(self.rate * dur)
        res = []
        ph = 0.0
        rnd = random.random
        for i in range(n):
            t = i / n
            f = f0 + (f1 - f0) * t
            ph += f / self.rate
            if wave == 'sine':
                v = math.sin(ph * math.tau)
            elif wave == 'square':
                v = 1.0 if (ph % 1) < 0.5 else -1.0
            elif wave == 'saw':
                v = 2 * (ph % 1) - 1
            else:
                v = 0
            if noise:
                v = v * (1 - noise) + (rnd() * 2 - 1) * noise
            env = math.exp(-decay * t) * min(1.0, i / 60)
            res.append(v * env)
        return res

    def _make_sfx(self):
        s = self._sound
        tn = self._tone
        self.sfx['jump'] = s(tn(280, 620, 0.13, 'square', 4), 0.18)
        self.sfx['swing'] = s(tn(500, 200, 0.12, 'sine', 3, noise=0.8), 0.35)
        self.sfx['hit'] = s(tn(180, 60, 0.15, 'square', 6, noise=0.5), 0.4)
        self.sfx['collect'] = s(tn(880, 880, 0.06, 'sine', 1) + tn(1320, 1320, 0.1, 'sine', 4), 0.35)
        self.sfx['hurt'] = s(tn(420, 140, 0.3, 'saw', 3), 0.3)
        self.sfx['throw'] = s(tn(700, 300, 0.09, 'sine', 3, noise=0.6), 0.25)
        notes = []
        for f in (523, 659, 784, 1046):
            notes += tn(f, f, 0.1, 'square', 2)
        self.sfx['correct'] = s(notes, 0.2)
        self.sfx['wrong'] = s(tn(200, 180, 0.18, 'square', 1) + tn(150, 130, 0.3, 'square', 2), 0.2)
        self.sfx['roar'] = s(self._roar(1.3), 0.6)
        self.sfx['growl'] = s(self._roar(1.0, 70), 0.45)
        self.sfx['door'] = s(tn(60, 40, 0.7, 'saw', 2, noise=0.7), 0.4)
        self.sfx['torch'] = s(tn(300, 900, 0.35, 'sine', 3, noise=0.9), 0.35)
        self.sfx['rune'] = s(tn(660, 660, 0.6, 'sine', 5) , 0.35)
        self.sfx['crack'] = s(tn(900, 300, 0.12, 'square', 8, noise=0.7), 0.3)
        self.sfx['stomp'] = s(tn(300, 90, 0.12, 'square', 6), 0.3)
        self.sfx['life'] = s(tn(523, 1046, 0.3, 'square', 2), 0.2)
        self.sfx['talk'] = s(tn(600, 700, 0.05, 'square', 3), 0.12)
        self.sfx['splash'] = s(tn(400, 100, 0.4, 'sine', 4, noise=0.85), 0.4)

    def _roar(self, dur, base=110):
        n = int(self.rate * dur)
        out = []
        ph = 0
        for i in range(n):
            t = i / n
            f = base * (1.2 - 0.5 * t) + 15 * math.sin(i / 300)
            ph += f / self.rate
            v = (2 * (ph % 1) - 1) * 0.6 + (random.random() * 2 - 1) * 0.4
            env = min(1, t * 8) * (1 - t) ** 0.8
            out.append(v * env * (0.7 + 0.3 * math.sin(i / 120)))
        return out

    # -------------------------------------------------------------- muzyka
    def _make_music(self):
        try:
            self.music['adventure'] = self._sound(self._song_adventure(), 0.55)
            self._maybe_start()
            self.music['cave'] = self._sound(self._song_cave(), 0.6)
            self._maybe_start()
            self.music['boss'] = self._sound(self._song_boss(), 0.55)
            self._maybe_start()
        except Exception:
            pass

    def _render(self, beats, bpm, voices):
        """voices: lista funkcji f(t_w_sekundach, beat_float) -> wartość."""
        dur = beats * 60 / bpm
        n = int(self.rate * dur)
        out = [0.0] * n
        for v in voices:
            v(out, bpm)
        return out

    def _add_note(self, out, start, dur, freq, kind, vol):
        r = self.rate
        i0 = int(start * r)
        n = int(dur * r)
        ph = 0.0
        for i in range(n):
            j = i0 + i
            if j >= len(out):
                j -= len(out)
            t = i / r
            if kind == 'flute':
                ph += freq * (1 + 0.006 * math.sin(t * 30)) / r
                v = math.sin(ph * math.tau) + 0.25 * math.sin(ph * 2 * math.tau)
                env = min(1, t * 25) * math.exp(-t * 1.5)
            elif kind == 'bass':
                ph += freq / r
                v = math.sin(ph * math.tau) + 0.3 * math.sin(ph * 3 * math.tau)
                env = min(1, t * 80) * math.exp(-t * 3)
            elif kind == 'kick':
                f = freq * (1 + 3 * math.exp(-t * 40))
                ph += f / r
                v = math.sin(ph * math.tau)
                env = math.exp(-t * 14)
            elif kind == 'tom':
                f = freq * (1 + 0.6 * math.exp(-t * 20))
                ph += f / r
                v = math.sin(ph * math.tau) * 0.8 + (random.random() * 2 - 1) * 0.2
                env = math.exp(-t * 10)
            elif kind == 'shaker':
                v = random.random() * 2 - 1
                env = math.exp(-t * 60)
            elif kind == 'bell':
                ph += freq / r
                v = math.sin(ph * math.tau) + 0.4 * math.sin(ph * 2.7 * math.tau)
                env = math.exp(-t * 3)
            elif kind == 'drone':
                ph += freq / r
                v = math.sin(ph * math.tau) + 0.5 * math.sin(ph * 1.5 * math.tau)
                env = min(1, t * 2, (dur - t) * 2)
            else:
                v, env = 0, 0
            out[j] += v * env * vol

    def _song_adventure(self):
        bpm = 112
        beat = 60 / bpm
        bars = 8
        n = int(self.rate * bars * 4 * beat)
        out = [0.0] * n
        A = 220.0
        scale = [0, 3, 5, 7, 10, 12, 15]
        rnd = random.Random(42)
        roots = [0, 0, -5, -2, 0, 0, -7, -5]
        for b in range(bars):
            for q in range(4):
                t = (b * 4 + q) * beat
                if q in (0, 2):
                    self._add_note(out, t, 0.3, 55, 'kick', 0.5)
                else:
                    self._add_note(out, t, 0.2, 150, 'tom', 0.25)
                self._add_note(out, t + beat / 2, 0.2, 200, 'tom', 0.15)
                self._add_note(out, t + beat / 4, 0.05, 0, 'shaker', 0.06)
                self._add_note(out, t + 3 * beat / 4, 0.05, 0, 'shaker', 0.06)
            rf = A / 2 * 2 ** (roots[b] / 12)
            self._add_note(out, b * 4 * beat, beat * 1.5, rf, 'bass', 0.28)
            self._add_note(out, (b * 4 + 2) * beat, beat * 1.5, rf, 'bass', 0.22)
        phrase = []
        for i in range(16):
            phrase.append((rnd.choice(scale), rnd.choice((0.5, 1, 1, 0.5, 1.5))))
        t = 0.0
        k = 0
        while t < bars * 4 * beat - beat:
            st, ln = phrase[k % len(phrase)]
            if k >= len(phrase):
                st = st + (2 if k % 5 == 0 else 0)
            f = A * 2 ** (st / 12)
            self._add_note(out, t, ln * beat * 1.1, f, 'flute', 0.22)
            t += ln * beat
            k += 1
        return self._norm(out)

    def _song_cave(self):
        bpm = 64
        beat = 60 / bpm
        beats = 32
        n = int(self.rate * beats * beat)
        out = [0.0] * n
        self._add_note(out, 0, beats * beat, 55, 'drone', 0.25)
        self._add_note(out, beats * beat / 2, beats * beat / 2, 58.3, 'drone', 0.12)
        rnd = random.Random(7)
        for b in range(beats):
            t = b * beat
            if b % 2 == 0:
                self._add_note(out, t, 0.3, 45, 'kick', 0.4)
                self._add_note(out, t + 0.22, 0.3, 45, 'kick', 0.25)
            if rnd.random() < 0.3:
                self._add_note(out, t + rnd.random() * beat, 1.2,
                               rnd.choice((880, 1046, 1174, 1318)), 'bell', 0.07)
        return self._norm(out)

    def _song_boss(self):
        bpm = 150
        beat = 60 / bpm
        bars = 8
        n = int(self.rate * bars * 4 * beat)
        out = [0.0] * n
        roots = [0, 0, 1, 0, 0, 0, 3, 1]
        for b in range(bars):
            for q in range(8):
                t = (b * 4 + q / 2) * beat
                if q % 2 == 0:
                    self._add_note(out, t, 0.25, 50, 'kick', 0.45)
                if q in (2, 6):
                    self._add_note(out, t, 0.2, 180, 'tom', 0.35)
                self._add_note(out, t, 0.05, 0, 'shaker', 0.05)
                f = 55 * 2 ** (roots[b] / 12) * (2 if q in (3, 7) else 1)
                self._add_note(out, t, beat * 0.45, f, 'bass', 0.25)
            if b % 2 == 1:
                self._add_note(out, (b * 4 + 2) * beat, beat * 2, 440 * 2 ** (roots[b] / 12), 'flute', 0.12)
        return self._norm(out)

    def _norm(self, out):
        m = max(1e-6, max(abs(v) for v in out))
        k = 0.9 / m
        return [v * k for v in out]

    # -------------------------------------------------------------- API
    def play(self, name):
        if self.ok and not self.muted and name in self.sfx:
            self.sfx[name].play()

    def play_music(self, name):
        if not self.ok:
            return
        self.wanted = name
        self._maybe_start()

    def _maybe_start(self):
        name = self.wanted
        if name == self.current or name not in self.music:
            return
        if self.channel:
            self.channel.fadeout(400)
        self.current = name
        self.channel = self.music[name].play(loops=-1, fade_ms=800)
        if self.channel:
            self.channel.set_volume(0 if self.muted else 0.55)

    def stop_music(self):
        self.wanted = None
        if self.ok and self.channel:
            self.channel.fadeout(600)
        self.current = None

    def toggle_mute(self):
        self.muted = not self.muted
        if self.channel:
            self.channel.set_volume(0 if self.muted else 0.55)
