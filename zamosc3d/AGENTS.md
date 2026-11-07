# Kontekst projektu dla agentów AI (Antigravity, Claude Code i in.)

Gra **„Jan Zamoyski i Miasto Idealne 3D”** — edukacyjna strategia 3D (budowa renesansowego Zamościa, 1580–1605)
dla dzieci 10–12 lat. Język gry, kodu i komentarzy: **polski**. Silnik: **Godot 4.3** (GDScript, renderer
*GL Compatibility*), modele: **Blender 4.x** (skrypt Pythona). Wersja 2D tej gry: `../zamosc/` (Python + Pygame).

## Struktura

| Ścieżka | Co to jest |
|---|---|
| `blender/generuj_modele.py` | Generuje wszystkie modele `.glb`, portrety, miniatury i tło tytułowe (Cycles) |
| `narzedzia/eksportuj_dane.py` | Eksportuje treść gry z `../zamosc/dane.py` do `godot/dane/dane.json` |
| `godot/project.godot` | Projekt Godota (otwórz w edytorze Godot 4.3+) |
| `godot/skrypty/gra.gd` | Świat 3D, ekonomia, budowa, rozmowy, kompas, zapis gry, tryby `--zrzuty` i `--samotest` |
| `godot/skrypty/interfejs.gd` | Cały interfejs budowany w kodzie (HUD, dialogi, okna, ekrany) |
| `godot/dane/dane.json` | Fabuła, zagadki, Księga Wiedzy, budynki, mapa — **nie edytuj ręcznie**, zmieniaj `../zamosc/dane.py` |
| `godot/modele/`, `godot/ui/` | Wygenerowane przez Blendera (nie edytuj ręcznie — zmień skrypt i wygeneruj ponownie) |
| `godot/audio/` | Dźwięki i muzyka (z wersji 2D, generowane kodem) |

## Polecenia

```bash
# 1. treść gry -> JSON
python narzedzia/eksportuj_dane.py
# 2. modele i rendery (Blender w tle; --bez-renderow = tylko .glb, szybko)
blender -b -P blender/generuj_modele.py
# 3. autotest: przejście wszystkich 4 rozdziałów (oczekiwane: "TEST_WYNIK: OK")
godot --headless --path godot -- --samotest
# 4. zrzuty ekranu (potrzebny ekran / Xvfb)
godot --path godot -- --zrzuty ../zrzuty
# 5. eksport EXE dla Windows (wymaga szablonów eksportu 4.3)
godot --headless --path godot --export-release "Windows" ../build/ZamoyskiMiastoIdealne3D.exe
```

## Zasady

- Układ: 1 pole mapy = 2 m (`T` w `gra.gd`). Mapa 40 × 26 pól; oś X = wschód, oś Z = południe.
- Modele w Blenderze: podstawa na z=0, środek w (0,0), fasada w stronę −Y (w Godocie: +Z, południe).
- Po zmianie treści zawsze uruchom autotest (`--samotest`) — musi wypisać `TEST_WYNIK: OK`.
- Fakty historyczne w `dane.py` są sprawdzone; nie dopisuj dat ani faktów bez źródła.
  Hagop to postać fikcyjna i gra o tym informuje.
