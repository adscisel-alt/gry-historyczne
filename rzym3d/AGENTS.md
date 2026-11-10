# Kontekst projektu dla agentów AI (Claude Code, Antigravity i in.)

Gra **„Roman Empire — od narodzin przez rozkwit aż po upadek”** (seria *Kroniki Damiana Ścisła*) — edukacyjna
turowa strategia 3D o starożytnym Rzymie (753 p.n.e. – 476 n.e.) dla uczniów 10–14 lat. Język gry, kodu
i komentarzy: **polski**. Silnik: **Godot 4.3** (GDScript, renderer *Forward+* na komputer i *GL Compatibility* w przeglądarce – `rendering_method.web`; oświetlenie w `_otoczenie()`/`_ustaw_klimat()` w `gra.gd`),
modele: **Blender** (skrypt Pythona, działa w Blenderze 4.x i w module `bpy` 5.x).

Rozgrywka jak w `../kroniki-damiana-scisla/` (mapa z kafli, tury, 4 zasoby, budynki poszerzające granice,
technologie zdobywane zagadką, bitwy kartami z pytaniem rady wojennej, zagony wroga, kronikarz-doradca
Damian w fioletowym kapturze), mapy między rozdziałami jak w `../dmowski3d/` (animowana mapa basenu Morza
Śródziemnego z granicami z historical-basemaps i trasą wypraw). Dodatkowo **tryb wieloosobowy**.

## Struktura

| Ścieżka | Co to jest |
|---|---|
| `narzedzia/dane.py` | **Cała treść gry** (rozdziały, mapy kafli, budynki, technologie+zagadki, karty, pytania, postacie, encyklopedia, wydarzenia) → `godot/dane/dane.json` |
| `narzedzia/eksportuj_mape.py` | mapy imperium (historical-basemaps, GPL-3.0) → `godot/dane/mapa_imperium.json` |
| `narzedzia/generuj_dzwieki.py` | efekty i muzyka (synteza w Pythonie, numpy) → `godot/audio/*.wav` |
| `narzedzia/generuj_lektora.py` | lektor (Piper) → `godot/audio/glos/<md5>.ogg` (tylko w CI) |
| `blender/generuj_modele.py` | modele `.glb`, portrety, obrazki kart, tło tytułowe |
| `godot/skrypty/gra.gd` | stan gry, tury, ekonomia, świat 3D z kafli, kamera, zapis, tryby `--samotest`/`--zrzuty` |
| `godot/skrypty/interfejs.gd` | interfejs budowany w kodzie (HUD, okna, mapa imperium, encyklopedia) |
| `godot/skrypty/bitwa.gd` | bitwa kartami w 3D |
| `godot/skrypty/siec.gd` | multiplayer online (WebSocket, pokoje z kodem; ten sam skrypt jest serwerem: `-- --serwer 9080`) |

## Kontrakt modeli (Blender → Godot)

Układ: **1 pole mapy = 2 m** (Godot: 2 jednostki), model stoi na z=0, środek podstawy w (0,0), front na −Y Blendera
(w Godot +Z). Budynek mieści się w kwadracie 1,8 × 1,8 m i ma ≤ 3 m wysokości. Styl: low-poly, płaskie kolory
(materiały Principled bez tekstur), czytelny z góry pod kątem ~50°. Pliki w `godot/modele/<nazwa>.glb`.

- Teren/dekoracje: `cyprys`, `pinia`, `oliwka`, `dab`, `krzak`, `skala_0`, `skala_1`, `trzcina`, `gora` (stożek góry na pole), `wzgorze` (łagodne wzgórze na pole)
- Budynki (każdy 1 pole): `chata`, `domus`, `insula`, `pole`, `winnica`, `tartak`, `kamieniolom`, `targ`, `swiatynia`,
  `koszary`, `mury`, `port`, `akwedukt`, `termy`, `amfiteatr`, `kuria`, `bazylika`, `rusztowanie` (budowa w toku)
- Zabytki (dekoracje 1 pole, mogą być wyższe ≤ 5 m): `wilczyca`, `kapitol`, `koloseum`, `panteon`, `luk_triumfalny`, `kolumna_trajana`, `ruiny`
- Obozy wroga: `oboz_barbarzyncow` (namioty, ognisko, totem), `oboz_kartaginy`
- Jednostki (wys. ok. 1,7 m, figura stojąca): `legionista`, `welita` (lekki z oszczepem), `lucznik`, `ekwita` (jeździec na koniu),
  `pretorianin`, `balista`, `galijczyk`, `kartaginczyk`, `slon` (słoń bojowy z wieżyczką), `german`, `hun` (konny łucznik), `got`
- Postacie (wys. 1,7 m): `damian` (kronikarz w fioletowym płaszczu z kapturem, z księgą), `romulus`, `brennus`, `hannibal`, `scypion`,
  `cezar`, `wercyngetoryks`, `august`, `trajan`, `konstantyn`, `attyla`, `odoaker`, `romulus_augustulus`, `cyncynat`
- Inne: `galera` (okręt z wiosłami i żaglem, ok. 4 m długości), `sztandar` (aquila na drzewcu), `znacznik` (pierścień zaznaczenia),
  `ognisko`
- Rendery PNG (Cycles): `ui/portret_<postać>.png` 256×256 (popiersie, przezroczyste tło) dla wszystkich postaci,
  `ui/karta_<jednostka>.png` 192×192 (jednostka w 3/4, przezroczyste tło) dla wszystkich jednostek,
  `ui/budynek_<nazwa>.png` 128×128 (ikona budynku w 3/4), `ui/tlo_tytul.png` 1280×720 (panorama Forum Romanum o zachodzie),
  `ui/tlo_bitwy.png` 1280×720 (pole bitwy, bez wojsk).

## Animacja postaci

- Części: `noga_l/p`, `reka_l/p`, `glowa`, `peleryna` (postać, `CZESCI` w Blenderze); `kon_noga_lp/pp/lt/pt`, `kon_glowa`,
  `kon_ogon`, `jezdziec`; `slon_noga_*`, `slon_traba`, `slon_ucho_l/p`, `slon_ogon` (`CZESCI_RUCHOME`, nie są łączone).
- Godot: `animuj_postac(węzeł, "stoi"|"idzie"|"atak", faza, postęp_ataku)` w `gra.gd`.

## Ożywione budynki

- Detale i ruchome części dodaje `ZYCIE[nazwa]()` po `m_<nazwa>()`; `eksportuj()` nie łączy obiektów `anim_*`.
- Konwencja nazw (Godot: `_ozyw_model` / `_animuj_budynki` w `gra.gd`): `anim_obrot_x|z`, `anim_kolys`, `anim_pila`,
  `anim_mlot`, `anim_ogien` (+ światło), `anim_woda` (shader wody), `anim_lodz`; puste `dym_*` (dym, `dym_para`, `dym_fontanna`).
- Robotnik: `ludzik(x, y, rz, tunika, czynnosc, narzedzie, nazwa, s)` – ręce z narzędziem to część `anim_<czynnosc>_<nazwa>`.

## Woda i teren

- Wierzch lądu: shader `_material_terenu()`; w kolorze wierzchołków rgb = kolor typu terenu (`_kolor_terenu`),
  a = udział trawy (`WAGA_TRAWY`), uśrednione w narożnikach (`_kolor_rogu`). Siatka budowy: `odswiez_siatke_budowy()`.

- Pola `~` i `m` mają w `dane.py` wysokość stopy brzegu (-0.3); dno liczy `_dno()` z odległości od lądu, lustro wody
  to `POZIOM_WODY` (-0.18). Shader wody: `_material_wody()` (głębokość w `COLOR.r` wierzchołków powierzchni).

## Polecenia

```bash
python narzedzia/dane.py                       # treść -> godot/dane/dane.json (sprawdza spójność)
python narzedzia/eksportuj_mape.py             # mapy imperium (pip install shapely)
python narzedzia/generuj_dzwieki.py            # dźwięki i muzyka (numpy)
blender -b -P blender/generuj_modele.py        # modele i rendery (-- --bez-renderow: tylko .glb; -- --tylko slon,hun)
godot --headless --path godot -- --samotest    # autotest: oczekiwane "TEST_WYNIK: OK"
godot --path godot -- --zrzuty ../zrzuty       # zrzuty ekranu
godot --headless --path godot -- --serwer 9080 # serwer gry online (przekaźnik pokoi)
godot --headless --path godot -- --bot host ws://127.0.0.1:9080 /tmp/kod.txt   # test online: gospodarz (drugi proces: --bot gosc …)
godot --headless --path godot --export-release "Web" ../build/web/index.html
godot --headless --path godot --export-release "Windows" ../build/RomanEmpire3D.exe
```

## Zasady

- Fakty historyczne w `dane.py` mają być sprawdzone; legendy (Romulus i Remus, gęsi kapitolińskie) oznaczamy jako legendy.
- Po każdej zmianie uruchom `python narzedzia/dane.py` i autotest (`--samotest`).
