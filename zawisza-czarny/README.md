# Zawisza Czarny — Mrok nad Krakowem

Strategiczna gra przygodowa w przeglądarce (HTML5 Canvas + Web Audio) dla uczniów w wieku 10–12 lat.
Ton: mroczny, ale przystępny dla dzieci. Język: polski. Działa offline i nie potrzebuje żadnych zewnętrznych plików.
Wszystkie grafiki są malowane proceduralnie, pędzlem złożonym z setek półprzezroczystych pociągnięć.
Wszystkie dźwięki są syntezowane na żywo.

**Uruchomienie:** otwórz `index.html` w przeglądarce albo wejdź na GitHub Pages: `/zawisza-czarny/`.

## Fabuła

Rok 1409. Nad Krakowem zawisł Mrok. Czarny Komtur, zdrajca wyrzucony z Zakonu (postać fikcyjna), wykradł
ze skarbca na Wawelu pięć skarbów Królestwa. Król Władysław Jagiełło wysyła po nie Zawiszę Czarnego z Garbowa.

| Rozdział | Tytuł | Miejsce | Minigra | Artefakt |
|---|---|---|---|---|
| I | Mrok nad Krakowem | Wawel → Rynek i Sukiennice | waga kupiecka (grzywny) | pieczęć majestatowa |
| II | Kopia i honor | plac turniejowy na Błoniach | gonitwa na kopie | Złota Ostroga |
| III | Mądrość Akademii | Akademia Krakowska | zamek dziejów (oś czasu 966–1400) | przywilej odnowienia Akademii (1400) |
| IV | Urwany hejnał | Kościół Mariacki | hejnał (pamięć dźwięków) | Włócznia św. Maurycego |
| V | Szczerbiec w ciemności | Smocza Jama | bitwa taktyczna z pocztem | Szczerbiec |

Epilog: Grunwald (1410), Perpignan (1415), Gołubiec (1428) i przysłowie „polegać jak na Zawiszy”.

**Lokacje (Kraków):** Wzgórze Wawelskie, Rynek i Sukiennice, Kazimierz (kuźnia), Błonia (plac turniejowy),
Akademia Krakowska, Kościół Mariacki, Smocza Jama. Do tego malowana mapa miasta z murami i Wisłą.

**Postacie poboczne (6):** brat Mikołaj (kronikarz), kupcowa Agnieszka z Sukiennic, herold Jaśko,
Stanisław ze Skarbimierza (prawdziwy rektor Akademii), hejnalista Wojciech i kowal Bartosz.
Pojawiają się też król Jagiełło, Rycerz Kruka i Czarny Komtur.

## Mechaniki

- **Strategia:** każda podróż to 1 dzień, a każdy dzień to +4 Mroku. Przy Mroku 100 gra się kończy.
  Gracz zarządza złotem, honorem, wiedzą, zdrowiem i pocztem. Odzyskany skarb zmniejsza Mrok o 12.
  Mrok cofają też świeca w kościele Mariackim, pochodnie i schwytanie szpiega.
- **Dialogi z wyborami:** wybory dają honor, złoto i wiedzę. Wplecione są w nie pytania sprawdzające.
- **Ekwipunek:** broń, zbroja, tarcza i hełm. Do tego przedmioty do zużycia i artefakty.
  Sprzęt wpływa na walki, gonitwę i bitwę.
- **System wiedzy:** Kronika z 35 kartami oznaczonymi jako FAKT, LEGENDA albo FIKCJA.
  Wiedza wyznacza rangę (od Pazia do Kronikarza Królestwa) i daje więcej rozkazów w bitwie.
  Brat Mikołaj przeprowadza próby wiedzy.
- **Minigry:** 5 opisanych w tabeli wyżej.
- **Zdarzenia w drodze:** pielgrzym, zbóje, pożar, zaraza, giermek, szpieg, kupiec, żak z zagadką i kruki.
- **Zapis gry:** automatyczny (localStorage). Po porażce można wrócić do początku rozdziału.

## Struktura projektu

```
zawisza-czarny/
  index.html        — interfejs (HUD, dialogi, okna), style, ładowanie skryptów
  js/art.js         — „malarz”: tła (11), sprite'y postaci, jeźdźcy, jednostki, portrety (11), ikony (22)
  js/audio.js       — synteza: muzyka modalna (6 motywów), burdon, wiatr i efekty (18)
  js/data.js        — treść: rozdziały, postacie, lokacje, przedmioty, Kronika, pytania, zdarzenia, dialogi
  js/minigames.js   — 5 minigier jako niezależne „sceny”
  js/game.js        — stan gry, menedżer scen, mapa strategiczna, ekwipunek, sklep, werbunek, zapis
```

Kod jest podzielony tak jak projekt w silniku gry: dane są oddzielone od logiki, każda scena ma metody
`draw` / `click` / `key` / `onExit`, a menedżer stanu (`G`) pełni rolę GameManagera.
Dzięki temu treść z `data.js` da się łatwo przenieść do innego silnika, np. Unity (jako ScriptableObjects).
Wersja w Unity nie została zbudowana, bo w środowisku, w którym powstała gra, nie było edytora Unity.
