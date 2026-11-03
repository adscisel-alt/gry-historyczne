# Kroniki Tomka Turby – Doradca książąt i królów (966–1410)

Turowa strategia edukacyjna z historii Polski dla uczniów w wieku 10–14 lat (Windows 10/11, plik EXE).
Grafika to izometryczny pixel art w stylu strategii z lat 90. – **cała** generowana jest proceduralnie
w kodzie (kafle terenu, budynki, jednostki, portrety, UI). Dźwięki i średniowieczna melodia w skali
doryckiej też są syntetyzowane w kodzie, bez plików audio.

Gracz jest **Tomkiem Turbą** – wędrownym kronikarzem i doradcą w fioletowym kapturze. Nie dowodzi armią
bezpośrednio: doradza władcy, co zbudować, jaką wiedzę zdobyć i którą siłę wystawić w bitwie.

![Menu](docs/01_menu.png)
![Mapa](docs/04_mapa.png)
![Bitwa](docs/07_bitwa.png)
![Technologie](docs/06_technologie.png)

## Kampania – 6 rozdziałów, 4 epoki

| # | Epoka | Rozdział | Cel |
|---|-------|----------|-----|
| I | Plemienna | Gniezno 966–967 – „Woda i ogień” | chrzest i pismo, bitwa z Wichmanem |
| II | Piastowska | Legnica 1241 – „Burza ze Wschodu” | oblężenie: palisady, zapasy, odliczanie tur |
| III | Piastowska | Kraków 1257 – „Miasto z prawem” | lokacja na prawie magdeburskim, targi, żupy solne |
| IV | Zamków | Płowce 1331–1333 – „Mała postura, wielkie serce” | bitwa pod Płowcami, zamek Kazimierza |
| V | Jagiellońska | Krewo 1385 – „Korona i dwa narody” | dyplomacja, unia polsko-litewska |
| VI | Jagiellońska | Grunwald 1410 – „Dwa nagie miecze” | most łyżwowy, zaopatrzenie, wielka bitwa |

Rozdziały ułożone są chronologicznie (Legnica 1241 przed Płowcami 1331). Każdy zaczyna się
kroniką-intro (epicki narrator z humorem), ma własną mapę 30×30 kafli generowaną z ziarna
(rzeki, jeziora, wzgórza, puszcze, zabytki z ciekawostkami, obozy wrogów) i zaplanowane wydarzenia
fabularne z decyzjami.

## Mechaniki

- **4 zasoby**: żywność, drewno, kamień, srebro; 10 typów budynków; granice księstwa rosną z każdą budową.
  Każdy kolejny budynek tego samego typu kosztuje o 25% więcej (koszt krańcowy).
- **Drzewko 20 technologii** (po 5 na epokę) – każdą zdobywa się, rozwiązując zagadkę historyczną;
  po odkryciu pojawia się ciekawostka. Kościół i szkoła podpowiadają w zagadkach.
- **Bitwy kartami**: przed bitwą pytanie z epoki (40 pytań), potem wróg odsłania kartę, a doradca
  wybiera odpowiedź. Piechota ▶ Jazda ▶ Strzelcy ▶ Piechota (+3). Werbunek nowych kart w Dworze drużyny.
- **Zdarzenia losowe**: zaraza, najazd, poselstwo, susza, jarmark, pożar, urodzaj, kometa, wędrowny żak,
  kupcy na szlaku bursztynowym – z wyborami i lekcją ekonomii (podaż i popyt, myto, inwestycje).
- **12 postaci historycznych** z portretami, życiorysami i ciekawostkami: Mieszko I, Dobrawa, biskup Jordan,
  Henryk Pobożny, Bolesław Wstydliwy, Kinga, Władysław Łokietek, Kazimierz Wielki, Jadwiga,
  Władysław Jagiełło, Witold, Zawisza Czarny.
- Postęp zapisuje się po każdym rozdziale (`%APPDATA%\KronikiTomkaTurby\postep.json`), gwiazdki za tempo i wiedzę.

Sterowanie: mysz; strzałki/WASD lub prawy przycisk myszy – przesuwanie mapy; C – powrót do grodu;
Spacja – koniec tury; T/W/K – technologie/wojsko/postacie; M – muzyka; F11 – pełny ekran.

## Pobranie EXE

Plik `KronikiTomkaTurby.exe` buduje GitHub Actions (`.github/workflows/kroniki-exe.yml`) na Windowsie:
zakładka **Actions → „Kroniki Tomka Turby – Windows EXE” → Artifacts**. Wypchnięcie tagu `kroniki-v1.0`
publikuje też wydanie (Release) z plikiem EXE.

## Uruchomienie ze źródeł / samodzielna kompilacja

```bat
python -m pip install -r requirements.txt
python main.py
build_exe.bat
```

Gotowy plik: `dist\KronikiTomkaTurby.exe` (jeden plik, ok. 20 MB, bez instalacji).

Testy i narzędzia:

- `python tests/bot_kampania.py 3` – bot przechodzi całą kampanię (test integracyjny bez okna),
- `python main.py --screenshots zrzuty` – zapisuje zrzuty kluczowych ekranów,
- `python tools/make_icon.py` – generuje ikonę `assets/icon.ico`.

Czcionka: DejaVu Serif (licencja w `assets/fonts/LICENSE-DejaVu.txt`).
