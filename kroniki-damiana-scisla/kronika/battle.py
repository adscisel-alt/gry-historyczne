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


def player_power(pc, bonus, terrain, mods=None):
    """Siła karty gracza z premiami terenu, dowódcy i taktyk (bez przewagi typu)."""
    m = mods or {}
    t = data.CARDS[pc]["type"]
    return (card_power(pc, bonus, terrain, True) + m.get("type_bonus", {}).get(t, 0)
            + m.get("plus", 0) + m.get("type_plus", {}).get(t, 0))


def resolve(pc, ec, bonus, terrain, mods=None):
    """Zwraca (siła gracza, siła wroga, obrażenia dla gracza, obrażenia dla wroga)."""
    m = mods or {}
    P = player_power(pc, bonus, terrain, m) + (ADV if beats(pc, ec) else 0)
    E = max(0, card_power(ec, 0, terrain, False) - m.get("e_minus", 0)) + (ADV if beats(ec, pc) and not m.get("no_adv") else 0)
    shield = data.CARDS[pc].get("shield", 0) + m.get("shield", 0)
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
        from .world import DIFF
        diff = DIFF[getattr(world, "diff", 1)]
        self.cmd = data.COMMANDERS.get(world.idx, {"who": None, "desc": "", "type_bonus": {}, "morale": 0, "tactics": []})
        self.p_max = 20 + world.defense_bonus(defense) + self.cmd.get("morale", 0)
        self.p_hp = self.p_max
        self.e_max = enemy_morale = max(6, int(round(enemy_morale * diff["enemy"])))
        self.e_hp = enemy_morale
        self.hidden_p = diff["hidden"]
        self.ehidden = None
        self.revealed_hidden = False
        self.tactics = list(self.cmd.get("tactics", [])) + (["tabor"] if "tabor" in world.techs else [])
        self.used_tactics = set()
        self.rmods = {}
        self.tactic_hover = None
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
        bg3d = gfx.asset(f"battle_{self.terrain}")
        if bg3d:
            s.blit(pygame.transform.smoothscale(bg3d, (W, H)), (0, 0))
        else:
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
        q, ans, ok = data.pick_question(self.w.epoch, self.app.used_q)
        from .world import DIFF
        hints = (1 if "akademia" in self.w.techs else 0) + DIFF[getattr(self.w, "diff", 1)]["hints"]
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
        self.ehidden = None
        if self.hidden_p > 0:
            if not self.edeck and self.ediscard:
                self.edeck, self.ediscard = self.ediscard, []
                random.shuffle(self.edeck)
            if self.edeck:
                self.ehidden = self.edeck.pop()
        self.revealed_hidden = False
        self.played = None
        self.rmods = self.base_mods()
        self.phase = "choose"
        self.anim = 0.0
        self.make_tactic_buttons()

    # ------------------------------------------------------------ dowódca i taktyki
    def base_mods(self):
        m = {"type_bonus": dict(self.cmd.get("type_bonus", {})), "plus": 0, "type_plus": {}, "e_minus": 0, "shield": 0}
        if self.cmd.get("stubborn") and self.p_hp < self.p_max * 0.5:
            m["plus"] += self.cmd["stubborn"]
        return m

    def make_tactic_buttons(self):
        self.buttons = []
        for i, tid in enumerate(self.tactics):
            t = data.TACTICS[tid]
            used = tid in self.used_tactics
            b = ui.Button((24, 316 + i * 44, 320, 38), ("✓ " if used else "") + t["name"],
                          lambda tid=tid: self.use_tactic(tid), 14, enabled=not used and self.phase == "choose",
                          color=(110, 60, 140))
            b.tid = tid
            self.buttons.append(b)

    def use_tactic(self, tid):
        if self.phase != "choose" or tid in self.used_tactics:
            return
        self.used_tactics.add(tid)
        t = data.TACTICS[tid]
        if hasattr(self.app, "unlock"):
            self.app.unlock("taktyki", tid, t["name"])
        e = t["effect"]
        m = self.rmods
        if e == "reinforce":
            for _ in range(2):
                if not self.deck and self.discard:
                    self.deck, self.discard = self.discard, []
                    random.shuffle(self.deck)
                if self.deck:
                    self.hand.append(self.deck.pop())
        elif e == "ambush":
            m["plus"] += 3
        elif e == "sortie":
            self.e_hp -= 5
            self.floats.append(["−5", W - 260, 120, (250, 230, 120), 0])
        elif e == "volley":
            self.e_hp -= 3
            m["type_plus"]["lucznicy"] = m["type_plus"].get("lucznicy", 0) + 2
            self.floats.append(["−3", W - 260, 120, (250, 230, 120), 0])
        elif e == "fog":
            m["no_adv"] = True
            m["plus"] += 1
        elif e == "hymn":
            self.p_max += 4
            self.p_hp += 4
            m["plus"] += 2
        elif e == "retreat":
            m["e_minus"] += 4
        elif e == "wagons":
            m["shield"] += 5
        audio.play("good")
        self.log.append(f"Taktyka: {t['name']}! {t['desc']}")
        self.log = self.log[-6:]
        if self.e_hp <= 0:
            self.e_hp = 0
            self.phase = "end"
            self.result = True
            audio.play("fanfare")
            self.buttons = [ui.Button((W // 2 - 100, 430, 200, 46), "Dalej ▶", self.finish, key=pygame.K_SPACE)]
            return
        self.make_tactic_buttons()

    def play(self, i):
        if self.phase != "choose" or i >= len(self.hand):
            return
        self.played = self.hand.pop(i)
        if self.ehidden is not None and random.random() < self.hidden_p:
            self.edeck.insert(0, self.ecard)
            self.ecard, self.ehidden = self.ehidden, None
            self.revealed_hidden = True
        elif self.ehidden is not None:
            self.edeck.insert(0, self.ehidden)
            self.ehidden = None
        self.buttons = []
        P, E, dp, de = resolve(self.played, self.ecard, self.bonus, self.terrain, self.rmods)
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
        if self.ehidden is not None:
            s += f" Uwaga: druga chorągiew wroga jest ukryta (zagra ją z szansą ok. {int(self.hidden_p * 100)}%)."
        if self.p_hp < self.p_max * 0.35:
            s += " Morale słabnie – nie ryzykujmy!"
        if self.tactic_hover:
            t = data.TACTICS[self.tactic_hover]
            s = f"{t['name']}: {t['desc']} Ciekawostka: {t['fact']}"
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
        if ev.type == pygame.MOUSEMOTION:
            self.tactic_hover = next((b.tid for b in self.buttons if hasattr(b, "tid") and b.rect.collidepoint(ev.pos)), None)
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
        # porada Damiana
        if self.cmd.get("who"):
            c = data.CHARACTERS[self.cmd["who"]]
            surf.blit(gfx.portrait(c["p"], 1), (30, 108))
            ui.draw_text(surf, f"Dowódca: {c['name']}", (70, 108), 13, ui.GOLD, True, shadow=(0, 0, 0))
            ui.draw_text(surf, self.cmd["desc"], (70, 124), 12, ui.CREAM, shadow=(0, 0, 0))
        adv = pygame.Rect(20, 148, 330, 160)
        surf.blit(gfx.panel(adv.w, adv.h, 9), adv.topleft)
        surf.blit(gfx.portrait(data.HERO["p"], 2), (adv.x + 12, adv.y + 12))
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
            ui.draw_text(surf, f"Nasze morale: {self.p_max} (umocnienia, technologie, dowódca)   •   Morale wroga: {self.e_max}",
                         (box.centerx, box.bottom - 40), 14, ui.INK_SOFT, True, center=True)
            if self.tactics:
                ui.draw_text(surf, "Taktyki do użycia raz w bitwie: " + ", ".join(data.TACTICS[t]["name"] for t in self.tactics),
                             (box.centerx, box.bottom - 66), 13, ui.PURPLE, True, center=True)
        # karta wroga
        if self.ecard and self.phase in ("choose", "resolve", "end"):
            ex, ey = W // 2 - CW // 2, 90
            if self.phase == "resolve":
                ex = int(W // 2 + 10)
            ui.draw_text(surf, "Wróg wystawia:", (W // 2, 66 + 0), 14, ui.CREAM, True, center=True, shadow=(0, 0, 0))
            self.card(surf, self.ecard, (ex, ey), glow=(160, 40, 40))
            if self.phase == "choose" and self.ehidden is not None:
                hx = ex + CW + 16
                back = pygame.Rect(hx, ey, CW, CH)
                pygame.draw.rect(surf, (60, 30, 30), back, border_radius=4)
                pygame.draw.rect(surf, ui.GOLD, back, 3, border_radius=4)
                for k in range(0, CH, 12):
                    pygame.draw.line(surf, (90, 46, 40), (hx + 4, ey + k), (hx + CW - 4, ey + k))
                ui.draw_text(surf, "?", (back.centerx, back.y + 44), 56, ui.GOLD, True, center=True)
                ui.draw_text(surf, "ukryta", (back.centerx, back.bottom - 34), 13, ui.CREAM, True, center=True)
            if self.phase == "resolve" and self.revealed_hidden and self.anim > 0.2:
                ui.draw_text(surf, "Wróg zagrał ukrytą chorągiew!", (W // 2 + 70, ey + CH + 6), 15, (255, 170, 140), True,
                             center=True, shadow=(0, 0, 0))
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
                pw = player_power(cid, self.bonus, self.terrain, self.rmods)
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
