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
- `damian-kapelusz-szyfrow.html` — „Damian Ściseł i Kapelusz Szyfrów”, przygodówka point & click w stylu klasycznych
  gier z Płaskiego Świata: haker-czarodziej w fioletowym kapeluszu tropi oszusta, który podszywa się pod niego
  (deepfake). 6 lokacji, 6 zagadek (phishing, smocze hasło, prywatność, 2FA, wykrywanie deepfake'a, odzyskiwanie
  konta), 9 zaklęć bezpieczeństwa, podpowiedzi Sowy i dyplom na koniec. Grafika i dźwięk generowane kodem.
  - **Windows (.exe):** katalog `windows/` to paczka Electron; workflow `windows-exe.yml` buduje przenośny plik
    `Damian-Kapelusz-Szyfrow.exe` (artefakt przebiegu + wydanie `gra-windows`). Lokalnie: `cd windows && npm install && npm run exe`.

Wszystkie strony są samowystarczalne (działają offline, bez zależności sieciowych).
Deploy: `.github/workflows/pages.yml` publikuje główną gałąź przy każdym pushu.
