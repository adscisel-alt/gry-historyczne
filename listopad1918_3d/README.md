# Listopad 1918 — wersja 3D (Godot)

Ta sama przygodówka co w `../listopad1918/`, przeniesiona do 3D w silniku **Godot 4.3+**:
każda z 14 lokacji to **diorama z papierowych wycinanek** — pudełko teatralne z brył,
tekstur i świateł, w którym postacie stoją na drewnianych podstawkach. Na obraz nałożony
jest shader „fotografii z 1918 r.” (sepia, ziarno, rysy kliszy, winieta, migotanie);
w kolorze zostaje tylko fioletowy kaptur Damiana Ściseła.

* Sterowanie „kliknij i idź”: klikasz miejsce lub obiekt, Janek sam tam podchodzi.
  Lewy przycisk — działaj, prawy — oglądaj, przedmiot z torby + cel — użyj, J — dziennik, F11 — pełny ekran.
* Fabuła, dialogi, 29 faktów ze źródłami, 10 mitów, 12 biogramów i 8 minigier są
  **wspólne z wersją 2D** (eksport do `dane/gra.json`).
* Grafika jest generowana kodem: wycinanki i portrety eksportuje `narzedzia/eksport.py`
  z wersji 2D, a dioramy budują się w `skrypty/budowniczy.gd`.

## Pobranie gotowej gry (Windows)

https://github.com/adscisel-alt/gry-historyczne/releases/download/listopad1918-3d-latest/Listopad1918_3D.exe

## Otwarcie w Godocie

1. Godot 4.3 lub nowszy → *Import* → wskaż `listopad1918_3d/project.godot`.
2. F5 uruchamia grę. Eksport: *Project → Export → Windows Desktop* (szablony eksportu Godota).

## Autotest i CI

```bash
godot --headless --path . -- --autotest
```

Autotest sprawdza dane, przechodzi całą grę na poziomie logiki, buduje wszystkie 14 dioram,
sprawdza klik myszą (promień → hotspot → Janek idzie → akcja), a potem przechodzi grę
przez prawdziwe ekrany: karty, dialogi, mity, dziennik i wszystkie 8 minigier.
Workflow `.github/workflows/listopad1918-3d.yml` uruchamia autotest, robi zrzuty ekranu
(`zrzuty/`), eksportuje EXE, sprawdza go na Windows i publikuje jako Release.

## Struktura

```
project.godot, main.tscn       projekt (renderer Compatibility — działa też na starszych komputerach)
dane/gra.json                  treść gry (z wersji 2D)
zasoby/                        wycinanki, portrety, ikony, papier, mapa (PNG z wersji 2D)
shadery/post.gdshader          sepia, ziarno, rysy, winieta (fiolet zostaje w kolorze)
skrypty/logika.gd, rozmowa.gd  logika gry i dialogów
skrypty/budowniczy.gd          proceduralne dioramy 14 lokacji
skrypty/swiat.gd               scena 3D, kamera, hotspoty, chód Janka
skrypty/hud.gd, motyw.gd       interfejs
skrypty/ekrany/                menu, karty, dialogi, Damian, mity, dziennik, zakończenie
skrypty/minigry/               8 minigier
skrypty/main.gd, autotest.gd   pętla gry, kolejka zdarzeń, zapis, dźwięki, autotest, zrzuty
narzedzia/eksport.py           eksport treści i grafik z wersji 2D
```
