# Listopad 1918 — Pocztówki z niepodległości

Przygodówka point-and-click w stylu gier z lat 90 (Python + Pygame), w 7 rozdziałach.
Grafika jest w całości proceduralna i stylizowana na pocztówki i fotografie z 1918 r.:
sepia, ziarno filmu, rysy kliszy, winieta, papierowe wycinanki z cieniem.

* **Bohater:** Janek, 14-letni harcerz-łącznik z Warszawy (postać fikcyjna).
* **Narrator:** Damian Ściseł, archiwista w fioletowym kapturze (jedyny kolor w sepii),
  który weryfikuje mity o 1918 r.
* **Grupa docelowa:** 11–15 lat, język polski. Racje każdego obozu przedstawione neutralnie.

## Rozdziały i lokacje (7 / 14)

| # | Rozdział | Daty | Lokacje | Zagadka / minigra |
|---|----------|------|---------|-------------------|
| 1 | Pocztówka z archiwum | 31 X – 1 XI | Archiwum, Kraków – Rynek | mapa trzech zaborów |
| 2 | Warszawa czeka | 3–6 XI | Harcówka, siedziba Rady Regencyjnej | przedmioty + dialogi z regentami |
| 3 | Lubelska noc | 6–7 XI | Pałac Lubomirskich, drukarnia | ułożenie manifestu |
| 4 | Pociąg z Berlina | 8–10 XI | Wagon, Dworzec Wiedeński | weryfikacja przepustek |
| 5 | Karabiny na bruku | 10–14 XI | Koszary Mirowskie, Plac Saski | kolejność przejmowania punktów, rozbrajanie z paskiem napięcia, sprzeczności w relacjach świadków |
| 6 | Paryż, aleja dyplomacji | 13–16 XI | Biuro KNP, salon dyplomatyczny | dyplomacja z paskami poparcia Francja / Anglia / USA |
| 7 | Głos każdego | 14–28 XI | Poznań – Hotel Bazar, lokal Ligi Kobiet | quiz o prawach wyborczych kobiet, finał „kto co wniósł” |

**12 postaci historycznych z biogramami:** Piłsudski, Dmowski, Paderewski, Daszyński, Korfanty,
Witos, abp Kakowski, ks. Lubomirski, Ostrowski, Rydz-Śmigły, Adam Koc, Zofia Moraczewska.

**Dziennik Janka** (klawisz J): fakty z datami i źródłami (29), 10 obalanych mitów,
biogramy, mapa trzech zaborów, strona o prawach wyborczych kobiet z porównaniem krajów.

> Uczciwość historyczna: Paderewski w listopadzie 1918 r. był jeszcze w USA, więc w grze
> rozmawia z Jankiem „przez pocztówkę z Nowego Jorku”, a Damian wyjaśnia to wprost.
> Kolejność w zagadce koszar to łamigłówka, nie kronika — Damian też to zaznacza.

## Sterowanie

Lewy przycisk – działaj / rozmawiaj / idź • prawy – oglądaj • klik w przedmiot w torbie,
potem w cel – użyj • J – dziennik • Esc – menu • F11 – pełny ekran • 1–4 – opcje dialogu.
Gra zapisuje się automatycznie (`%APPDATA%\Listopad1918\zapis.json`).

## Uruchomienie i budowanie EXE

```bash
pip install -r requirements.txt
python main.py
```

Windows 11 – plik EXE: uruchom `build_exe.bat` (albo `python build_exe.py`). Skrypt
najpierw puszcza testy, generuje ikonę i pakuje grę PyInstallerem do `dist\Listopad1918.exe`.
Workflow `.github/workflows/listopad1918-exe.yml` buduje EXE na `windows-latest`,
sprawdza go (`Listopad1918.exe --autotest`) i udostępnia jako artefakt.

## Testy

```bash
python -m pytest -q tests
```

Testy (bez okna) sprawdzają spójność danych (lokacje, hotspoty, dialogi, przedmioty, fakty),
jednoznaczność zagadek, sepię teł, zapis/odczyt oraz **przechodzą całą grę** – raz na poziomie
logiki i raz przez prawdziwe sceny interfejsu (karty, lokacje, dialogi, wszystkie minigry, mity, dziennik).

## Struktura

```
main.py                 start gry (opcja --autotest)
gra/stan.py             logika: warunki, efekty, dialogi, zapis (niezależna od grafiki)
gra/grafika.py          proceduralne tła, wycinanki, ikony, ramki pocztówek, ziarno
gra/sceny.py            menu, karty rozdziałów, lokacje, dialogi, mity, dziennik, finał
gra/minigry/            8 minigier
gra/dane/               rozdziały, lokacje, dialogi, postacie, fakty i mity
gra/automat.py          solucja + automatyczny gracz
tests/test_gra.py       testy automatyczne
```
