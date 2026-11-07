# Gry Historyczne

Grywalne osie czasu i gry edukacyjne z historii, publikowane na GitHub Pages:
https://adscisel-alt.github.io/gry-historyczne/

- `os-czasu-etap-szkolny.html` — oś etapu szkolnego konkursu kuratoryjnego (starożytność–1797):
  5 trybów gry, teksty źródłowe, Pracownia map z 10 interaktywnymi mapami
- `os-czasu-konkurs.html` — trening konkursowy, pełna historia Polski 966–2004
- `os-czasu-historia-7.html` — klasa VII (1815–1939)
- `os-czasu-historia-6.html` — klasa VI (1450–1815)
- `forum-romanum.html` — wirtualny spacer 3D po Forum Romanum (three.js w `vendor/`)
- `cyberdetektyw.html` — „Damian Teacher: Cyberdetektyw”, klockowa gra RPG 3D o zasadach bezpieczeństwa
  w internecie dla klas VI–VIII (Szkoła Mentis): 9 spraw z quizami i słowniczkiem PL–EN (m.in. AI, deepfake,
  uzależnienie od ekranu), 12 złotych kłódek z poradami, finał z Phisherem i certyfikat do druku
- `zamosc/` — „Jan Zamoyski i Miasto Idealne”, gra strategiczna pixel-art (Python + Pygame) dla 10–12 lat,
  kompilowana do `ZamoyskiMiastoIdealne.exe` (Windows) przez `.github/workflows/zamosc-exe.yml`
- `zamosc3d/` — „Jan Zamoyski i Miasto Idealne 3D”: ta sama gra w 3D (modele z Blendera, silnik Godot 4.3),
  eksport do `ZamoyskiMiastoIdealne3D.exe` przez `.github/workflows/zamosc3d-exe.yml`
- `dmowski3d/` — „Roman Dmowski. Droga do Wersalu 3D”: strategia 3D o latach 1914–1919 (4 kampanie: Warszawa,
  Lozanna, Błękitna Armia we Francji, konferencja w Paryżu), Blender + Godot 4.3, eksport do
  `DmowskiDrogaDoWersalu3D.exe` przez `.github/workflows/dmowski3d-exe.yml`

Wszystkie strony są samowystarczalne (działają offline, bez zależności sieciowych).
Deploy: `.github/workflows/pages.yml` publikuje główną gałąź przy każdym pushu.
