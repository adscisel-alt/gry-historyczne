# -*- coding: utf-8 -*-
"""Bitwa kartami: doradzasz władcy, którą siłę wystawić przeciw odsłoniętej karcie wroga."""
import math
import random
import pygame

from . import data, gfx, ui, audio
from .modals import Scene, Quiz, W, H

CW, CH = 120, 168
ADV = 3


def card_power(cid, bonus, terrain, player):
    c = data.CARDS[cid]
    p = c["power"] + bonus
    if player:
        if terrain == "forest" and c["type"] == "lucznicy":
            p += 1
        if terrain == "field" and c["type"] == "jazda":
            p += 1
        if terrain == "grod":
            p += {"lucznicy": 2}.get(c["type"], 0)
    return p


def beats(a, b):
    return data.CARD_TYPES[data.CARDS[a]["type"]]["beats"] == data.CARDS[b]["type"]


def resolve(pc, ec, bonus, terrain):
    """Zwraca (siła gracza, siła wroga, obrażenia dla gracza, obrażenia dla wroga)."""
    P = card_power(pc, bonus, terrain, True) + (ADV if beats(pc, ec) else 0)
    E = card_power(ec, 0, terrain, False) + (ADV if beats(ec, pc) else 0)
    shield = data.CARDS[pc].get("shield", 0)
    if P > E:
        return P, E, 0, P - E + 1
    if E > P:
        return P, E, max(0, E - P + 2 - shield), 0
    return P, E, max(0, 1 - shield), 1


class Battle(Scene):
    def __init__(self, app, world, name, enemy_deck, enemy_morale, defense=False, terrain="field",
                 allies=(), intro="", on_end=None, siege=False):
        super().__init__(app)
        self.w = world
        self.name = name
        self.terrain = terrain
        self.defense = defense
        self.siege = siege
        self.on_end = on_end
        self.intro = intro
        self.deck = list(world.deck) + list(allies)
        random.shuffle(self.deck)
        self.discard = []
        self.edeck = list(enemy_deck)
        random.shuffle(self.edeck)
        self.ediscard = []
        self.hand_size = 4 + (1 if "zaciezni" in world.techs else 0)
        self.hand = []
        self.p_max = 20 + world.defense_bonus(defense)
        self.p_hp = self.p_max
        self.e_max = enemy_morale
        self.e_hp = enemy_morale
        self.bonus = 0
        self.ecard = None
        self.played = None
        self.phase = "intro"
        self.anim = 0.0
        self.log = []
        self.result = None
        self.shake = 0.0
        self.floats = []
        self.hover = -1
        self.round = 0
        self.last = None
        world.morale_bonus = 0
        self.bg = self._make_bg()
        self.buttons = [ui.Button((W // 2 - 110, 420, 220, 46), "Do boju! ▶", self.start_question, key=pygame.K_SPACE)]
        audio.play("drum")

    # ------------------------------------------------------------ tło
    def _make_bg(self):
        s = pygame.Surface((W, H))
        r = random.Random(len(self.name))
        top, bot = ((70, 40, 40), (190, 110, 70)) if self.siege else ((90, 130, 180), (210, 200, 160))
        for y in range(H):
            s.fill(gfx.mix(top, bot, min(1, y / 420)), (0, y, W, 1))
        # wzgórza
        for layer, (col, base) in enumerate([((90, 110, 80), 380), ((70, 100, 60), 430), ((60, 90, 50), 480)]):
            pts = [(0, H)]
            for x in range(0, W + 40, 40):
                pts.append((x, base + math.sin(x / 130 + layer * 2) * 22 + r.randint(-8, 8)))
            pts.append((W, H))
            pygame.draw.polygon(s, col, pts)
        if self.terrain == "forest":
            for i in range(26):
                t = gfx.tree(i % 3)
                s.blit(t, (r.randint(0, W - 40), r.randint(390, 440)))
        if self.terrain == "grod":
            wall = (120, 84, 50)
            for x in range(0, 360, 10):
                pygame.draw.rect(s, wall, (x, 380 + (x % 20 == 0) * -6, 9, 140))
                pygame.draw.polygon(s, gfx.shade(wall, 1.2), [(x, 380 + (x % 20 == 0) * -6), (x + 9, 380 + (x % 20 == 0) * -6), (x + 4, 368 + (x % 20 == 0) * -6)])
        # armie w oddali
        for i in range(18):
            u = gfx.unit_big(random.choice(["spear", "bow", "horse"]), "pl", 2)
            s.blit(u, (40 + i * 18 + (i % 3) * 5, 470 + (i % 2) * 18))
        efac = data.CARDS[self.edeck[0]]["faction"]
        for i in range(18):
            u = pygame.transform.flip(gfx.unit_big(random.choice(["spear", "horse", "xbow"]) if efac != "mg" else "horse_mg",
                                                   efac if efac in gfx.FACTION else "en", 2), True, False)
            s.blit(u, (W - 90 - i * 18 - (i % 3) * 5, 470 + (i % 2) * 18))
        v = pygame.Surface((W, H), pygame.SRCALPHA)
        v.fill((20, 10, 0, 70))
        s.blit(v, (0, 0))
        return s

    # ------------------------------------------------------------ przebieg
    def start_question(self):
        self.buttons = []
        q, ans, ok = random.choice(data.QUESTIONS[self.w.epoch])
        hints = 1 if "akademia" in self.w.techs else 0
        self.app.push(Quiz(self.app, "Pytanie rady wojennej", q, ans, ok, self.after_question, hints))

    def after_question(self, good):
        self.w.stats["quiz_all"] += 1
        if good:
            self.w.stats["quiz_ok"] += 1
            self.bonus = 1
            self.p_hp = min(self.p_max + 3, self.p_hp + 3)
            self.p_max += 3
            self.log.append("Natchnienie! Wszystkie karty +1, morale +3.")
        else:
            self.log.append("Rada się pogubiła... brak premii.")
        self.next_round()

    def draw_cards(self):
        while len(self.hand) < self.hand_size:
            if not self.deck:
                if not self.discard:
                    break
                self.deck, self.discard = self.discard, []
                random.shuffle(self.deck)
            self.hand.append(self.deck.pop())

    def next_round(self):
        self.round += 1
        self.draw_cards()
        if not self.edeck:
            self.edeck, self.ediscard = self.ediscard, []
            random.shuffle(self.edeck)
        self.ecard = self.edeck.pop()
        self.played = None
        self.phase = "choose"
        self.anim = 0.0

    def play(self, i):
        if self.phase != "choose" or i >= len(self.hand):
            return
        self.played = self.hand.pop(i)
        P, E, dp, de = resolve(self.played, self.ecard, self.bonus, self.terrain)
        self.last = (P, E, dp, de)
        self.phase = "resolve"
        self.anim = 0.0
        audio.play("hit")

    def apply_result(self):
        P, E, dp, de = self.last
        self.p_hp -= dp
        self.e_hp -= de
        pn, en = data.CARDS[self.played]["name"], data.CARDS[self.ecard]["name"]
        if de and not dp:
            self.log.append(f"{pn} ({P}) pokonali: {en} ({E}). Wróg −{de}.")
            self.floats.append(["−%d" % de, W - 260, 120, (250, 230, 120), 0])
        elif dp and not de:
            self.log.append(f"{en} ({E}) przełamali: {pn} ({P}). My −{dp}.")
            self.floats.append(["−%d" % dp, 260, 120, (250, 120, 100), 0])
            self.shake = 0.35
        else:
            self.log.append(f"Remis {P}:{E}. Obie strony tracą siły.")
        self.log = self.log[-6:]
        self.discard.append(self.played)
        self.ediscard.append(self.ecard)
        if self.e_hp <= 0 or self.p_hp <= 0:
            self.phase = "end"
            self.result = self.e_hp <= 0 and self.p_hp > 0 or (self.e_hp <= 0 and self.p_hp <= 0 and self.e_hp < self.p_hp)
            if self.e_hp <= 0 and self.p_hp <= 0 and self.e_hp == self.p_hp:
                self.result = True
            audio.play("fanfare" if self.result else "bad")
            self.buttons = [ui.Button((W // 2 - 100, 430, 200, 46), "Dalej ▶", self.finish, key=pygame.K_SPACE)]
        else:
            self.next_round()

    def finish(self):
        self.w.stats["battles"] += 1
        self.app.pop()
        if self.on_end:
            self.on_end(bool(self.result))

    # ------------------------------------------------------------ porady
    def advice(self):
        if self.phase != "choose" or not self.ecard:
            return "Kronikarz liczy chorągwie i ostrzy pióro..."
        et = data.CARDS[self.ecard]["type"]
        if et == "jazda":
            s = "Wróg wystawia jazdę! Piechota z długą bronią zatrzyma konie (+3)."
        elif et == "lucznicy":
            s = "Strzelcy wroga! Szybka jazda dopadnie ich, nim zdążą naciągnąć cięciwy (+3)."
        elif et == "piechota":
            s = "Piechota wroga! Nasi strzelcy zasypią ich gradem strzał (+3)."
        else:
            s = "Uwaga, coś niezwykłego! Tu liczy się czysta siła – wystaw najsilniejszą kartę."
        if self.p_hp < self.p_max * 0.35:
            s += " Morale słabnie – nie ryzykujmy!"
        return s

    # ------------------------------------------------------------ zdarzenia
    def hand_rects(self):
        n = len(self.hand)
        gap = 14
        tot = n * CW + (n - 1) * gap
        x0 = W // 2 - tot // 2
        return [pygame.Rect(x0 + i * (CW + gap), H - CH - 16 - (14 if i == self.hover else 0), CW, CH) for i in range(n)]

    def handle(self, ev):
        if super().handle(ev):
            return True
        if self.phase == "choose":
            if ev.type == pygame.MOUSEMOTION:
                self.hover = -1
                for i, r in enumerate(self.hand_rects()):
                    if r.collidepoint(ev.pos):
                        self.hover = i
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, r in enumerate(self.hand_rects()):
                    if r.collidepoint(ev.pos):
                        self.play(i)
                        return True
            elif ev.type == pygame.KEYDOWN and pygame.K_1 <= ev.key <= pygame.K_6:
                self.play(ev.key - pygame.K_1)
        return True

    def update(self, dt):
        self.anim += dt
        self.shake = max(0, self.shake - dt)
        for f in self.floats:
            f[4] += dt
            f[2] -= dt * 40
        self.floats = [f for f in self.floats if f[4] < 1.4]
        if self.phase == "resolve" and self.anim > 1.3:
            self.apply_result()

    # ------------------------------------------------------------ rysowanie
    def bar(self, surf, x, y, w, hp, mx, label, col, flip=False):
        pygame.draw.rect(surf, (30, 20, 10), (x - 3, y - 3, w + 6, 30))
        fw = int(w * max(0, hp) / max(1, mx))
        pygame.draw.rect(surf, (60, 40, 30), (x, y, w, 24))
        pygame.draw.rect(surf, col, (x + (w - fw if flip else 0), y, fw, 24))
        pygame.draw.rect(surf, gfx.shade(col, 1.4), (x + (w - fw if flip else 0), y, fw, 4))
        ui.draw_text(surf, f"{label}: {max(0, hp)}/{mx}", (x + w // 2, y + 2), 16, ui.CREAM, True, center=True, shadow=(0, 0, 0))

    def card(self, surf, cid, pos, power=None, glow=None):
        img = gfx.card_face(cid)
        x, y = pos
        if glow:
            pygame.draw.rect(surf, glow, (x - 4, y - 4, CW + 8, CH + 8), border_radius=4)
        surf.blit(img, (x, y))
        c = data.CARDS[cid]
        ui.draw_text(surf, data.CARD_TYPES[c["type"]]["name"], (x + CW // 2, y + 9), 13, ui.CREAM, True, center=True)
        ui.draw_text(surf, c["name"], (x + CW // 2, y + 110), 12, ui.INK, True, center=True, width=CW - 10)
        pw = power if power is not None else c["power"]
        pygame.draw.circle(surf, (60, 36, 18), (x + CW - 16, y + CH - 18), 15)
        pygame.draw.circle(surf, ui.GOLD, (x + CW - 16, y + CH - 18), 13)
        ui.draw_text(surf, str(pw), (x + CW - 16, y + CH - 29), 18, ui.INK, True, center=True)
        if c.get("shield"):
            surf.blit(gfx.icon("shield", 2), (x + 8, y + CH - 32))

    def draw(self, surf):
        ox = int(math.sin(self.anim * 60) * 6 * self.shake / 0.35) if self.shake else 0
        surf.blit(self.bg, (ox, 0))
        if self.siege and self.p_hp < self.p_max * 0.5:
            v = pygame.Surface((W, H), pygame.SRCALPHA)
            v.fill((120, 0, 0, int(40 + 30 * math.sin(self.anim * 4))))
            surf.blit(v, (0, 0))
        top = gfx.panel(W, 58, 3, dark=True)
        surf.blit(top, (0, 0))
        ui.draw_text(surf, self.name, (W // 2, 14), 24, ui.GOLD, True, center=True)
        self.bar(surf, 30, 76, 360, self.p_hp, self.p_max, "Morale naszych", (190, 50, 50))
        self.bar(surf, W - 390, 76, 360, self.e_hp, self.e_max, "Morale wroga", (90, 90, 100), flip=True)
        # trójkąt przewag
        tri = pygame.Rect(W - 300, 120, 270, 92)
        pygame.draw.rect(surf, (40, 28, 18), tri)
        pygame.draw.rect(surf, ui.GOLD, tri, 1)
        ui.draw_text(surf, "Kto kogo pokonuje (+3):", (tri.x + 10, tri.y + 6), 13, ui.GOLD, True)
        ui.draw_text(surf, "Piechota ▶ Jazda", (tri.x + 10, tri.y + 28), 13, ui.CREAM)
        ui.draw_text(surf, "Jazda ▶ Strzelcy", (tri.x + 10, tri.y + 46), 13, ui.CREAM)
        ui.draw_text(surf, "Strzelcy ▶ Piechota", (tri.x + 10, tri.y + 64), 13, ui.CREAM)
        # porada Tomka
        adv = pygame.Rect(20, 120, 330, 170)
        surf.blit(gfx.panel(adv.w, adv.h, 9), adv.topleft)
        surf.blit(gfx.portrait(data.TOMEK["p"], 2), (adv.x + 12, adv.y + 12))
        ui.draw_text(surf, "Rada kronikarza", (adv.x + 86, adv.y + 14), 15, ui.PURPLE, True)
        ui.draw_text(surf, self.advice(), (adv.x + 86, adv.y + 38), 14, ui.INK, width=adv.w - 100)
        # dziennik
        lg = pygame.Rect(W - 300, 222, 270, 150)
        pygame.draw.rect(surf, (40, 28, 18), lg)
        y = lg.y + 6
        for ln in self.log[-5:]:
            y = ui.draw_text(surf, ln, (lg.x + 8, y), 12, ui.CREAM, width=lg.w - 16)
        if self.phase == "intro":
            box = pygame.Rect(W // 2 - 330, 130, 660, 270)
            surf.blit(gfx.panel(box.w, box.h, 4), box.topleft)
            ui.draw_text(surf, self.name, (box.centerx, box.y + 20), 22, ui.RED, True, center=True)
            ui.draw_text(surf, self.intro or "Wróg stoi naprzeciw. Kronikarz szepcze radę władcy...", (box.x + 30, box.y + 62), 16, ui.INK, width=box.w - 60)
            ui.draw_text(surf, f"Nasze morale: {self.p_max} (z umocnień i technologii)   •   Morale wroga: {self.e_max}",
                         (box.centerx, box.bottom - 40), 14, ui.INK_SOFT, True, center=True)
        # karta wroga
        if self.ecard and self.phase in ("choose", "resolve", "end"):
            ex, ey = W // 2 - CW // 2, 90
            if self.phase == "resolve":
                ex = int(W // 2 + 10)
            ui.draw_text(surf, "Wróg wystawia:", (W // 2, 66 + 0), 14, ui.CREAM, True, center=True, shadow=(0, 0, 0))
            self.card(surf, self.ecard, (ex, ey), glow=(160, 40, 40))
        if self.phase == "resolve" and self.played:
            t = min(1, self.anim / 0.4)
            px_, py_ = int(W // 2 - CW - 10), int(H - CH - 16 + (90 - (H - CH - 16)) * t)
            P, E, dp, de = self.last
            self.card(surf, self.played, (px_, py_), power=None, glow=(60, 140, 60))
            if self.anim > 0.45:
                ui.draw_text(surf, f"{P}  :  {E}", (W // 2, 270), 40, ui.GOLD, True, center=True, shadow=(0, 0, 0))
                if beats(self.played, self.ecard):
                    ui.draw_text(surf, "Przewaga typu! +3", (W // 2, 320), 18, (160, 240, 160), True, center=True, shadow=(0, 0, 0))
                elif beats(self.ecard, self.played):
                    ui.draw_text(surf, "Wróg ma przewagę typu! +3", (W // 2, 320), 18, (250, 150, 130), True, center=True, shadow=(0, 0, 0))
        if self.phase == "choose":
            ui.draw_text(surf, "Doradź władcy: którą kartę wystawić? (kliknij lub 1–%d)" % len(self.hand),
                         (W // 2, H - CH - 58), 17, ui.CREAM, True, center=True, shadow=(0, 0, 0))
            for i, (cid, r) in enumerate(zip(self.hand, self.hand_rects())):
                pw = card_power(cid, self.bonus, self.terrain, True)
                glow = None
                if self.ecard and beats(cid, self.ecard):
                    glow = (90, 200, 90)
                self.card(surf, cid, r.topleft, power=pw, glow=glow)
            ui.draw_text(surf, f"Talia: {len(self.deck)}  •  Odrzucone: {len(self.discard)}", (20, H - 26), 13, ui.CREAM, shadow=(0, 0, 0))
        if self.phase == "end":
            box = pygame.Rect(W // 2 - 300, 250, 600, 240)
            surf.blit(gfx.panel(box.w, box.h, 6), box.topleft)
            if self.result:
                ui.draw_text(surf, "ZWYCIĘSTWO!", (box.centerx, box.y + 30), 34, ui.GREEN, True, center=True)
                ui.draw_text(surf, "Kronikarz zapisuje: „Dobra rada i męstwo przeważyły szalę.”", (box.x + 30, box.y + 90), 16, ui.INK, width=box.w - 60)
            else:
                ui.draw_text(surf, "PORAŻKA", (box.centerx, box.y + 30), 34, ui.RED, True, center=True)
                ui.draw_text(surf, "Wojsko się cofa. „Nawet najlepszym zdarzają się złe dni” – pociesza kronikarz.", (box.x + 30, box.y + 90), 16, ui.INK, width=box.w - 60)
        for f in self.floats:
            ui.draw_text(surf, f[0], (int(f[1]), int(f[2])), 36, f[3], True, center=True, shadow=(0, 0, 0))
        for b in self.buttons:
            b.draw(surf)
