# Kontekst projektu dla agentów AI (Antigravity, Claude Code i in.)

Gra **„Roman Dmowski. Droga do Wersalu 3D”** — edukacyjna strategia 3D o drodze Polski do niepodległości
(1914–1919) dla dzieci 10–12 lat. Język gry, kodu i komentarzy: **polski**. Silnik: **Godot 4.3** (GDScript,
renderer *GL Compatibility*), modele: **Blender 4.x** (skrypt Pythona). Silnik gry wywodzi się z `../zamosc3d/`.

## Struktura

| Ścieżka | Co to jest |
|---|---|
| `narzedzia/dane.py` | **Cała treść gry**: 4 kampanie, mapy, postacie, budynki, przedmioty, Księga Wiedzy, zagadki → `godot/dane/dane.json` |
| `narzedzia/generuj_ikony_i_dzwieki.py` | Ikony 16×16 i dźwięki/muzyka (korzysta z `../zamosc/narzedzia/generuj_zasoby.py`) |
| `blender/generuj_modele.py` | Modele `.glb` (postacie, placówki, zabytki), portrety, miniatury, tło tytułowe (Cycles) |
| `godot/skrypty/gra.gd` | Świat 3D, mapa kampanii, ekonomia, budowa, rozmowy, kompas, zapis, tryby `--zrzuty` i `--samotest` |
| `godot/skrypty/interfejs.gd` | Interfejs budowany w kodzie (HUD, dialogi, okna, ekrany) |

## Polecenia

```bash
python narzedzia/dane.py                         # treść -> JSON (sprawdza też spójność map)
python narzedzia/generuj_ikony_i_dzwieki.py      # ikony i dźwięki
blender -b -P blender/generuj_modele.py          # modele i rendery (-- --bez-renderow: tylko .glb)
godot --headless --path godot -- --samotest      # autotest: oczekiwane "TEST_WYNIK: OK"
godot --path godot -- --zrzuty ../zrzuty         # 11 zrzutów ekranu
godot --headless --path godot --export-release "Windows" ../build/DmowskiDrogaDoWersalu3D.exe
```

## Jak dodać kampanię lub budynek

- Kampania: nowy wpis w `ROZDZIALY` (mapa z funkcji `mapa_*`, `npc`, `dzialki`, `dekor`, `cele`, `wstep`, `koniec`),
  rozmowy w `ROZMOWY` pod kluczem `"postac:numer_kampanii"`.
- Budynek: wpis w `BUDYNKI` + funkcja `m_<nazwa>` w `blender/generuj_modele.py` (dodaj ją do słownika w `main()`).
- Mapa: 36 × 24 pól, 1 pole = 2 m; znaki opisane na górze `dane.py`.

## Zasady

- Fakty historyczne w `dane.py` są sprawdzone; nie dopisuj dat ani faktów bez źródła.
- Gra ma pokazywać historię rzetelnie: także rolę Piłsudskiego, Paderewskiego, Hallera i powstańców,
  oraz to, że część poglądów Dmowskiego jest dziś krytykowana (karta „Spory o Romana Dmowskiego”).
- Hanna to postać fikcyjna i gra o tym informuje.
- Po każdej zmianie uruchom autotest (`--samotest`).
