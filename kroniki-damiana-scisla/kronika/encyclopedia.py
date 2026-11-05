# -*- coding: utf-8 -*-
"""Encyklopedia kronikarza: hasła odblokowywane w trakcie gry."""
import pygame

from . import data, gfx, ui
from .modals import Scene, W, H

GLOSSARY = {
    "grod": ("Gród", "Osada otoczona wałem i palisadą, siedziba księcia lub jego urzędnika. W grodach były warsztaty, spichlerze i świątynie."),
    "plemie": ("Plemię", "Wspólnota ludzi połączonych pochodzeniem, językiem i terytorium – np. Polanie, Wiślanie, Ślężanie."),
    "danina": ("Danina", "Obowiązkowe świadczenie dla władcy – w zbożu, miodzie, skórach albo w pracy przy budowie grodów."),
    "druzyna": ("Drużyna", "Stały oddział wojów utrzymywanych przez księcia. Najbardziej zaufani i najlepiej uzbrojeni wojownicy."),
    "chrzest": ("Chrzest Polski", "W 966 r. Mieszko I przyjął chrzest. Polska weszła do kręgu kultury łacińskiej: pisma, szkół i kościołów."),
    "denar": ("Denar", "Mała srebrna moneta. Przed nią płacono siekańcami – kawałkami srebra ważonymi na wadze."),
    "arcybiskupstwo": ("Arcybiskupstwo", "Zwierzchnia jednostka Kościoła nad kilkoma biskupstwami. W 1000 r. powstało w Gnieźnie."),
    "senioryat": ("Seniorat", "Zasada z testamentu Krzywoustego: najstarszy z rodu rządzi w Krakowie i ma władzę nad młodszymi książętami."),
    "rozbicie": ("Rozbicie dzielnicowe", "Okres 1138–1320, gdy Polska była podzielona między książąt z rodu Piastów."),
    "lokacja": ("Lokacja", "Założenie miasta lub wsi na nowym prawie: wytyczenie rynku i ulic, nadanie samorządu i zwolnień z czynszu."),
    "wojt": ("Wójt", "Zarządca i sędzia w mieście lokowanym. Przewodniczył sądowi ławników."),
    "soltys": ("Sołtys", "Zarządca wsi lokowanej. Za swoją pracę dostawał więcej ziemi, karczmę lub młyn."),
    "kasztelan": ("Kasztelan", "Urzędnik zarządzający grodem i okręgiem wokół niego w imieniu władcy."),
    "zakon": ("Zakon rycerski", "Wspólnota rycerzy-zakonników, np. krzyżacy, templariusze, joannici. Łączyli śluby zakonne z walką."),
    "zupa": ("Żupa solna", "Kopalnia lub warzelnia soli należąca do władcy. Bochnia i Wieliczka dawały ogromne dochody."),
    "myto": ("Myto i cło", "Opłaty za przejazd drogą, mostem lub przez granicę. Ważne źródło dochodów władców i miast."),
    "kwarantanna": ("Kwarantanna", "Odosobnienie chorych lub przybyszów, by zatrzymać zarazę. Nazwa od włoskiego „quaranta” – czterdzieści dni."),
    "popyt": ("Popyt i podaż", "Gdy czegoś jest mało, a chętnych wielu – cena rośnie. Gdy towaru jest dużo – cena spada."),
    "inwestycja": ("Inwestycja", "Wydatek dziś, który przynosi zysk w przyszłości – jak budowa młyna czy targu."),
    "herb": ("Herb", "Znak rodu rycerskiego, malowany na tarczy i chorągwi. Całe rody nosiły ten sam herb, np. Topór czy Leliwa."),
    "statut": ("Statuty", "Spisane prawo obowiązujące w królestwie. Za Kazimierza Wielkiego powstały statuty wiślicko-piotrkowskie."),
    "unia": ("Unia", "Związek dwóch państw pod jednym władcą. W Krewie (1385) zaczął się związek Polski i Litwy."),
    "pospolite": ("Pospolite ruszenie", "Obowiązek stawienia się wszystkich rycerzy (później szlachty) do walki na wezwanie króla."),
    "rejza": ("Rejza", "Łupieżcza wyprawa wojenna, zwłaszcza krzyżacka na Litwę – krótka i szybka."),
    "tabor": ("Tabor", "Wozy z zapasami towarzyszące armii, które można ustawić w obronny krąg."),
    "pańszczyzna": ("Pańszczyzna", "Obowiązkowa, nieodpłatna praca chłopa na ziemi pana w zamian za korzystanie z gruntu."),
}

CHAPTER_TERMS = {
    0: ["grod", "plemie", "danina", "druzyna", "chrzest", "denar", "kwarantanna", "popyt"],
    6: ["arcybiskupstwo", "grod", "denar", "inwestycja"],
    7: ["senioryat", "rozbicie", "kasztelan"],
    1: ["rozbicie", "zakon", "kasztelan", "kwarantanna"],
    2: ["lokacja", "wojt", "soltys", "zupa", "myto", "inwestycja", "popyt"],
    8: ["wojt", "lokacja", "statut"],
    3: ["zakon", "herb", "statut", "pospolite"],
    4: ["unia", "rejza", "herb"],
    5: ["tabor", "pospolite", "unia", "pańszczyzna"],
}


def landmarks():
    out = {}
    for ch in data.CHAPTERS:
        for (pos, name, text) in ch["map"].get("landmarks", []):
            out[name] = (name, text)
    return out


TABS = [("pojecia", "Pojęcia"), ("miejsca", "Miejsca"), ("wynalazki", "Wynalazki"), ("taktyki", "Taktyki")]


def entries(kind):
    if kind == "pojecia":
        return {k: v for k, v in GLOSSARY.items()}
    if kind == "miejsca":
        return landmarks()
    if kind == "wynalazki":
        return {k: (t["name"], f"{t['fact']}\n\nW grze: {t['effect']}") for k, t in data.TECHS.items()}
    if kind == "taktyki":
        return {k: (t["name"], f"{t['fact']}\n\nW bitwie: {t['desc']}") for k, t in data.TACTICS.items()}
    return {}


def total_counts(save):
    enc = save.get("encyklopedia", {})
    got = sum(len(set(enc.get(k, [])) & set(entries(k))) for k, _ in TABS)
    return got, sum(len(entries(k)) for k, _ in TABS)


class EncyclopediaScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.tab = "pojecia"
        self.sel = None
        self.scroll = 0
        self.make()

    def make(self):
        self.buttons = [ui.Button((W - 200, H - 58, 180, 44), "◀ Wróć", self.app.pop, key=pygame.K_ESCAPE)]
        enc = self.app.save.get("encyklopedia", {})
        for i, (k, label) in enumerate(TABS):
            n = len(set(enc.get(k, [])) & set(entries(k)))
            self.buttons.append(ui.Button((30 + i * 210, 70, 200, 40), f"{label} {n}/{len(entries(k))}",
                                          lambda k=k: self.set_tab(k), 15,
                                          color=(100, 50, 140) if k == self.tab else (110, 90, 70)))
        self.buttons.append(ui.Button((30 + 4 * 210, 70, 200, 40), "Postacie", self.gallery, 15))

    def gallery(self):
        from .scenes import GalleryScene
        self.app.push(GalleryScene(self.app))

    def set_tab(self, k):
        self.tab, self.sel, self.scroll = k, None, 0
        self.make()

    def items(self):
        e = entries(self.tab)
        got = set(self.app.save.get("encyklopedia", {}).get(self.tab, []))
        return sorted([(k, v, k in got) for k, v in e.items()], key=lambda it: not it[2])

    def rows(self):
        return [pygame.Rect(30, 126 + i * 30 - self.scroll, 380, 28) for i in range(len(self.items()))]

    def handle(self, ev):
        if super().handle(ev):
            return True
        if ev.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, min(max(0, len(self.items()) * 30 - 480), self.scroll - ev.y * 30))
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for (k, v, ok), r in zip(self.items(), self.rows()):
                if r.collidepoint(ev.pos) and 120 <= r.y <= H - 90 and ok:
                    self.sel = k
        return True

    def draw(self, surf):
        surf.blit(gfx.parchment(W, H, 333), (0, 0))
        gfx.frame(surf, pygame.Rect(8, 8, W - 16, H - 16))
        got, tot = total_counts(self.app.save)
        ui.draw_text(surf, f"Encyklopedia kronikarza – odkryte hasła: {got}/{tot}", (W // 2, 22), 26, ui.RED, True, center=True)
        surf.set_clip(pygame.Rect(20, 120, 400, H - 210))
        for (k, v, ok), r in zip(self.items(), self.rows()):
            col = (240, 228, 196) if k != self.sel else (220, 200, 240)
            pygame.draw.rect(surf, col, r)
            pygame.draw.rect(surf, (150, 120, 80), r, 1)
            ui.draw_text(surf, v[0] if ok else "??? (jeszcze nieodkryte)", (r.x + 10, r.y + 5), 14,
                         ui.INK if ok else (150, 135, 115), ok)
        surf.set_clip(None)
        box = pygame.Rect(440, 120, W - 470, H - 200)
        surf.blit(gfx.panel(box.w, box.h, 44), box.topleft)
        if self.sel:
            name, text = entries(self.tab)[self.sel]
            ui.draw_text(surf, name, (box.x + 30, box.y + 24), 24, ui.PURPLE, True)
            ui.draw_text(surf, text, (box.x + 30, box.y + 70), 17, ui.INK, width=box.w - 60, line_h=25)
        else:
            ui.draw_text(surf, "Kliknij odkryte hasło po lewej.", (box.x + 30, box.y + 24), 18, ui.INK_SOFT, True)
            ui.draw_text(surf, "Hasła odkrywasz, grając: pojęcia – rozpoczynając rozdziały, miejsca – czytając o zabytkach "
                               "na mapie, wynalazki – rozwiązując zagadki technologii, taktyki – używając ich w bitwach.",
                         (box.x + 30, box.y + 64), 16, ui.INK, width=box.w - 60, line_h=24)
        for b in self.buttons:
            b.draw(surf)
