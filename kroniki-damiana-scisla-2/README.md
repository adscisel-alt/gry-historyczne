# Kroniki Damiana Ścisła II: Rzeczpospolita (1454–1795)

Druga część turowej strategii edukacyjnej z historii Polski dla uczniów w wieku 10–14 lat – **na Windows (EXE)
i w przeglądarce**. Ta sama mechanika co w części I ([`../kroniki-damiana-scisla`](../kroniki-damiana-scisla)),
nowa epoka: od wojny trzynastoletniej i złotego wieku, przez husarię, potop i odsiecz wiedeńską, po Konstytucję
3 maja, insurekcję kościuszkowską i rozbiory.

Gracz jest znów **Damianem Ściseł** – kronikarzem i doradcą w fioletowym kapturze, który radzi królom, hetmanom
i naczelnikom.

## Kampania – 9 rozdziałów (6 głównych + 3 dodatkowe)

| Lata | Epoka | Rozdział | Cel |
|------|-------|----------|-----|
| 1454–1466 | Złoty wiek | Wojna o morze – wojna trzynastoletnia | skarb na żołd, wykup Malborka, bitwa pod Świecinem |
| 1520–1521 | Złoty wiek | *dodatkowy:* Astronom na murach | Kopernik broni zamku w Olsztynie (oblężenie) |
| 1579–1582 | Czasy Batorego i Wazów | Wyprawy Batorego | piechota wybraniecka, Połock, Wielkie Łuki |
| 1610 | Czasy Batorego i Wazów | *dodatkowy:* Husaria pod Kłuszynem | Żółkiewski i szarża husarii |
| 1655–1656 | Wiek wojen | Potop | Jasna Góra, wojna szarpana Czarnieckiego, Warka |
| 1683 | Wiek wojen | Skrzydła nad Wiedniem | zaopatrzenie, czambuł tatarski, odsiecz Wiednia |
| 1768–1772 | Oświecenie i rozbiory | Konfederaci | Pułaski broni Jasnej Góry (oblężenie), I rozbiór |
| 1788–1792 | Oświecenie i rozbiory | *dodatkowy:* Konstytucja 3 maja | KEN, Sejm Wielki, targowiczanie |
| 1794 | Oświecenie i rozbiory | Kosy na sztorc | przysięga Kościuszki, kosynierzy pod Racławicami |

## Co nowego względem części I

- **Budynki zmieniają styl z epoką** (render 3D w Blenderze): siedziba władcy to kolejno renesansowy zamek
  z krużgankami i attyką, ratusz z wieżą jak w Zamościu, barokowy pałac z miedzianymi hełmami jak Wilanów
  i klasycystyczny pałac z portykiem nad stawem jak Łazienki. Kamienice, koszary, kolegia, folwarki (dwór
  z gankiem) i twierdze bastionowe także mają cztery odmiany.
- **Nowe jednostki**: husaria ze skrzydłami i skórą lamparta, muszkieterowie, dragoni, armaty, rakiety
  Siemienowicza, kosynierzy; wrogowie: Zakon, Moskwa, Szwedzi, Turcy i Tatarzy, Rosja XVIII w.
- **20 nowych technologii** z zagadkami (druk, folwark, spław wiślany, astronomia Kopernika, unia lubelska,
  wolna elekcja, husaria, bastiony, muszkiet, gazety, KEN, manufaktury, Konstytucja 3 maja, kosy na sztorc…).
- **128 pytań**, **15 postaci** z popiersiami 3D (Kazimierz Jagiellończyk, Kopernik, Bona Sforza, Batory,
  Zamoyski, Żółkiewski, Kordecki, Czarniecki, Sobieski, Pułaski, Stanisław August, Kołłątaj, Kościuszko,
  Głowacki…), 27 pojęć w encyklopedii, nowe zdarzenia (sejmik szlachecki, psucie monety i prawo Kopernika,
  jarmark dominikański, czambuł tatarski).
- **Muzyka epok**: pawana, galiarda, barokowy klawesyn i polonez.
- Mapy z geografią: Wisła i Nogat, Dźwina, Pilica, Dunaj, Warta, Łyna.

Mechaniki (zagony, utrzymanie wojska, dowódcy i taktyki, ukryta karta wroga, poziomy trudności, dziennik
nauki z dyplomem i CSV, zapis w dowolnym momencie, lektor) działają tak samo jak w części I. Postęp zapisuje
się osobno (`%APPDATA%\KronikiDamianaScisla2\`). Przycisk **„Nowa kronika (wyczyść postęp)”** w menu głównym
usuwa postęp (np. dla kolejnego ucznia), zostawiając ustawienia.

## Pobranie i uruchomienie

- EXE: GitHub Actions → „Kroniki Damiana Ścisła II – Windows EXE” → Artifacts.
- Przeglądarka: po scaleniu do `main` – `…/gry-historyczne/kroniki-damiana-scisla-2/graj/`.
- Ze źródeł: `python -m pip install -r requirements.txt`, `python main.py`, kompilacja: `build_exe.bat`.

Narzędzia: `python tests/bot_kampania.py` (bot przechodzi kampanię), `python main.py --screenshots zrzuty`,
`python tools/blender/render_sprites.py` (grafika 3D części II; kafle, drzewa i tła bitew pochodzą z części I),
`python tools/make_audio.py`, `python tools/make_voice.py`, `bash tools/build_web.sh`.

Silnik jest kopią silnika części I z parametryzacją: tytuł, katalog zapisów i premie technologii
pochodzą z `kronika/data.py` (`GAME`, `TECH_FX`).
