'use strict';
/* =====================================================================
   DATA — fabuła, postacie, lokacje, przedmioty, wiedza (Kronika),
   pytania, zdarzenia losowe i drzewa dialogów.
   ===================================================================== */
const D = {};

D.CHAPTERS = [
  null,
  { n: 'I', title: 'Mrok nad Krakowem', where: 'Wawel → Rynek i Sukiennice', goal: 'Stań przed królem na Wawelu, potem odnajdź na Rynku kupcową Agnieszkę.', artifact: 'pieczec' },
  { n: 'II', title: 'Kopia i honor', where: 'Plac turniejowy na Błoniach', goal: 'Pokonaj Rycerza Kruka w gonitwie i odbierz Złotą Ostrogę.', artifact: 'ostroga' },
  { n: 'III', title: 'Mądrość Akademii', where: 'Akademia Krakowska', goal: 'Pomóż rektorowi Stanisławowi otworzyć skrzynię szpiega.', artifact: 'przywilej' },
  { n: 'IV', title: 'Urwany hejnał', where: 'Kościół Mariacki', goal: 'Zagraj hejnał z Wojciechem i przegnaj kruki z wieży.', artifact: 'wlocznia' },
  { n: 'V', title: 'Szczerbiec w ciemności', where: 'Smocza Jama', goal: 'Przygotuj poczet i pokonaj Czarnego Komtura.', artifact: 'szczerbiec' },
];

D.CH = {
  zawisza: { name: 'Zawisza Czarny', role: 'rycerz z Garbowa, herbu Sulima' },
  jagiello: { name: 'Król Władysław Jagiełło', role: 'król Polski' },
  mikolaj: { name: 'Brat Mikołaj', role: 'kronikarz królewski' },
  agnieszka: { name: 'Agnieszka z Sukiennic', role: 'kupcowa sukiennicza' },
  jasko: { name: 'Herold Jaśko', role: 'herold turniejowy' },
  stanislaw: { name: 'Stanisław ze Skarbimierza', role: 'rektor Akademii Krakowskiej' },
  wojciech: { name: 'Wojciech', role: 'hejnalista z wieży Mariackiej' },
  bartosz: { name: 'Kowal Bartosz', role: 'płatnerz z Kazimierza' },
  kruk: { name: 'Rycerz Kruka', role: 'najemnik Komtura' },
  komtur: { name: 'Czarny Komtur', role: 'zdrajca w czarnym płaszczu' },
  kronika: { name: 'Kronika', role: '' },
};

D.LOC = {
  wawel: { name: 'Wzgórze Wawelskie', bg: 'wawel', x: 560, y: 520, npc: ['jagiello', 'mikolaj'], ch: 1, desc: 'Zamek królewski i katedra — serce Królestwa.' },
  rynek: { name: 'Rynek i Sukiennice', bg: 'rynek', x: 650, y: 315, npc: ['agnieszka'], ch: 1, flag: 'audiencja', desc: 'Największy plac miasta, pełen kupców — i cieni.' },
  kazimierz: { name: 'Kazimierz — kuźnia', bg: 'kazimierz', x: 830, y: 590, npc: ['bartosz'], ch: 1, flag: 'audiencja', desc: 'Kuźnia Bartosza: zbroje, broń i ludzie do pocztu.' },
  turniej: { name: 'Plac turniejowy (Błonia)', bg: 'turniej', x: 250, y: 300, npc: ['jasko'], ch: 2, desc: 'Szranki, trybuny i chorągwie rycerzy.' },
  akademia: { name: 'Akademia Krakowska', bg: 'akademia', x: 515, y: 205, npc: ['stanislaw'], ch: 3, desc: 'Biblioteka mistrzów — świece gasną tu same.' },
  mariacki: { name: 'Kościół Mariacki', bg: 'mariacki', x: 790, y: 225, npc: ['wojciech'], ch: 4, desc: 'Dwie wieże — z wyższej grany jest hejnał.' },
  smocza: { name: 'Smocza Jama', bg: 'smocza', x: 470, y: 600, npc: ['komtur'], ch: 5, desc: 'Jaskinia pod Wawelem. Tu kryje się Komtur.' },
};

/* slot: weapon/armor/shield/helm; use: zużywalne */
D.ITEMS = {
  miecz: { name: 'Miecz Zawiszy', slot: 'weapon', atk: 3, desc: 'Długi miecz rycerski — znak rozpoznawczy Zawiszy. Rycerze XV w. walczyli mieczami półtoraręcznymi, które można było chwycić jedną lub dwiema dłońmi.' },
  kolczuga: { name: 'Kolczuga', slot: 'armor', def: 1, desc: 'Pancerz z tysięcy zaplecionych żelaznych kółek. Chroni przed cięciem, gorzej przed pchnięciem.' },
  zbroja: { name: 'Czarna zbroja płytowa', slot: 'armor', def: 3, price: 40, desc: 'Zbroja ze stalowych płyt. Na początku XV w. płyty coraz częściej zastępowały kolczugę. Jedno z wyjaśnień przydomka „Czarny” to właśnie ciemna zbroja.' },
  tarcza: { name: 'Tarcza z herbem Sulima', slot: 'shield', def: 1, joust: 1, price: 15, desc: 'Tarcza z herbem Zawiszy: u góry pół czarnego orła na złocie, u dołu trzy srebrne kamienie na czerwieni.' },
  helm: { name: 'Przyłbica (basinet)', slot: 'helm', def: 1, price: 12, desc: 'Szpiczasty hełm z ruchomą zasłoną twarzy. Ostry kształt sprawiał, że ciosy się z niego ześlizgiwały.' },
  kopia: { name: 'Kopia turniejowa', joust: 1, price: 10, desc: 'Długa drewniana kopia z tępym, trójzębnym grotem zwanym koronką. Miała pękać przy uderzeniu, a nie zabijać.' },
  ziola: { name: 'Zioła lecznicze', use: 'hp', val: 35, price: 4, desc: 'Babka, krwawnik i szałwia. Klasztory prowadziły ogrody ziół — mnisi byli lekarzami średniowiecza. (+35 zdrowia)' },
  chleb: { name: 'Bochen chleba', use: 'hp', val: 15, price: 2, desc: 'Razowy chleb na zakwasie — podstawa jedzenia w średniowieczu. (+15 zdrowia)' },
  pochodnia: { name: 'Pochodnia z żywicą', use: 'mrok', val: 5, price: 7, desc: 'Ogień odpędza Mrok. Średniowieczne miasta nocą tonęły w ciemności — kto chodził bez światła, mógł być wzięty za złodzieja. (−5 Mroku)' },
  list: { name: 'List królewski', quest: true, desc: 'List z pieczęcią króla Władysława Jagiełły. Otwiera drzwi w całym Krakowie.' },
  pieczec: { name: 'Pieczęć majestatowa', art: true, desc: 'Pieczęć z wizerunkiem króla na tronie. Pieczęcią uwierzytelniano dokumenty — bez niej rozkaz króla nie był ważny.' },
  ostroga: { name: 'Złota Ostroga', art: true, desc: 'Złote ostrogi nosili tylko pasowani rycerze. Giermek miał srebrne lub żelazne.' },
  przywilej: { name: 'Przywilej odnowienia Akademii', art: true, desc: 'Dokument króla Władysława Jagiełły z 1400 r., który odnowił Akademię Krakowską.' },
  wlocznia: { name: 'Włócznia św. Maurycego', art: true, desc: 'Kopia cesarskiej włóczni, podarowana Bolesławowi Chrobremu przez cesarza Ottona III na zjeździe gnieźnieńskim w 1000 r.' },
  szczerbiec: { name: 'Szczerbiec', art: true, desc: 'Miecz koronacyjny królów Polski. Używano go przy koronacjach od 1320 r. (Władysław Łokietek).' },
};
D.ARTIFACTS = ['pieczec', 'ostroga', 'przywilej', 'wlocznia', 'szczerbiec'];

/* Kronika — karty wiedzy. tag: FAKT / LEGENDA / FIKCJA */
D.FACTS = {
  zawisza: { tag: 'FAKT', t: 'Zawisza Czarny z Garbowa', x: 'Żył ok. 1370–1428, herbu Sulima. Jeden z najsłynniejszych rycerzy średniowiecznej Europy. Przydomek „Czarny” mógł pochodzić od czarnych włosów albo ciemnej zbroi — historycy nie są tego pewni.' },
  sulima: { tag: 'FAKT', t: 'Herb Sulima', x: 'Tarcza podzielona poziomo: w górnym, złotym polu pół czarnego orła, w dolnym, czerwonym — trzy srebrne kamienie. Herb mówił, z jakiego rodu pochodzi rycerz, bo w hełmie nie było widać twarzy.' },
  polegaj: { tag: 'FAKT', t: '„Polegać jak na Zawiszy”', x: 'Przysłowie, które przetrwało do dziś. Znaczy: można komuś całkowicie zaufać. Zawisza słynął z dotrzymywania słowa.' },
  jagiello: { tag: 'FAKT', t: 'Władysław II Jagiełło', x: 'Wielki książę litewski, od 1386 r. król Polski. Został mężem królowej Jadwigi po unii w Krewie (1385), która połączyła Polskę i Litwę.' },
  sredniowiecze: { tag: 'FAKT', t: 'Ramy średniowiecza', x: 'Średniowiecze to umownie czas od upadku cesarstwa zachodniorzymskiego (476 r.) do odkrycia Ameryki przez Kolumba (1492 r.) — prawie tysiąc lat.' },
  koronacje: { tag: 'FAKT', t: 'Koronacje na Wawelu', x: 'Od koronacji Władysława Łokietka w 1320 r. królów Polski koronowano w katedrze na Wawelu. Kraków był stolicą Królestwa.' },
  magdeburg: { tag: 'FAKT', t: 'Lokacja Krakowa (1257)', x: 'Książę Bolesław Wstydliwy nadał Krakowi prawo magdeburskie. Miasto dostało wtedy regularny układ ulic i ogromny Rynek — ok. 200 × 200 m, jeden z największych w Europie.' },
  sukiennice: { tag: 'FAKT', t: 'Sukiennice', x: 'Hala targowa pośrodku Rynku, gdzie handlowano suknem (tkaniną wełnianą). W XIV w. zbudowano tu murowaną gotycką halę. Znana dziś ozdobna attyka powstała dopiero w XVI w.' },
  grzywna: { tag: 'FAKT', t: 'Grzywna', x: 'Jednostka wagi srebra i jednostka rozliczeniowa. Grzywna krakowska ważyła ok. 200 g srebra; w czasach Jagiełły liczono ją jako 48 groszy.' },
  sol: { tag: 'FAKT', t: 'Sól z Wieliczki i Bochni', x: 'Kopalnie soli (żupy krakowskie) należały do króla i przynosiły ogromne dochody. Sól była cenna — konserwowano nią mięso i ryby.' },
  hanza: { tag: 'FAKT', t: 'Kraków w Hanzie', x: 'W XIV w. Kraków należał do Hanzy — związku miast kupieckich, które wspólnie dbały o bezpieczny handel od Bałtyku po Flandrię.' },
  wierzynek: { tag: 'LEGENDA', t: 'Uczta u Wierzynka', x: 'W 1364 r. w Krakowie odbył się zjazd monarchów (to fakt). Tradycja mówi, że bogaty mieszczanin Mikołaj Wierzynek wydał dla nich słynną ucztę.' },
  turniej: { tag: 'FAKT', t: 'Gonitwa na kopie', x: 'Najsłynniejsza konkurencja turnieju. Rycerze pędzili na siebie z kopiami; celem było trafić w tarczę lub hełm, skruszyć kopię albo zrzucić rywala z siodła. Bariera (szranki) oddzielała konie.' },
  herold: { tag: 'FAKT', t: 'Herold', x: 'Znawca herbów i zasad rycerskich. Ogłaszał zawodników, pilnował reguł turnieju i liczył punkty. Bez herolda nie było turnieju.' },
  pasowanie: { tag: 'FAKT', t: 'Pasowanie na rycerza', x: 'Uroczystość, w której giermek stawał się rycerzem: uderzenie mieczem płazem w ramię, przypasanie miecza i ostróg. Złote ostrogi były znakiem rycerza.' },
  giermek: { tag: 'FAKT', t: 'Paź — giermek — rycerz', x: 'Chłopiec z rodu rycerskiego zaczynał jako paź, potem jako giermek nosił broń rycerza, dbał o konia i uczył się walki. Dopiero potem mógł zostać pasowany.' },
  perpignan: { tag: 'FAKT', t: 'Turniej w Perpignan (1415)', x: 'Według kronik Zawisza pokonał tam w pojedynku słynnego rycerza z Aragonii — wysadził go z siodła jednym uderzeniem kopii.' },
  akademia: { tag: 'FAKT', t: 'Akademia Krakowska', x: 'Założona w 1364 r. przez Kazimierza Wielkiego — pierwszy uniwersytet w Polsce. W 1400 r. odnowiona przez Władysława Jagiełłę. Dziś to Uniwersytet Jagielloński.' },
  jadwiga: { tag: 'FAKT', t: 'Klejnoty królowej Jadwigi', x: 'Królowa Jadwiga (zm. 1399) przekazała swoje klejnoty na odnowienie Akademii. Dzięki temu uczelnia mogła znów działać.' },
  skarbimierz: { tag: 'FAKT', t: 'Stanisław ze Skarbimierza', x: 'Pierwszy rektor odnowionej Akademii. W kazaniu „O wojnach sprawiedliwych” uczył, że wojna jest sprawiedliwa tylko wtedy, gdy broni się przed krzywdą — a nie gdy chce się grabić.' },
  hejnal: { tag: 'FAKT', t: 'Hejnał mariacki', x: 'Melodia grana na trąbce z wyższej wieży kościoła Mariackiego, kolejno na cztery strony świata. Dawniej był sygnałem otwarcia i zamknięcia bram oraz ostrzeżeniem przed ogniem i wrogiem.' },
  hejnal_leg: { tag: 'LEGENDA', t: 'Urwany hejnał', x: 'Legenda mówi, że hejnalista ostrzegał miasto przed najazdem Tatarów i zginął od strzały w gardło. Dlatego melodia urywa się w połowie.' },
  wieze: { tag: 'LEGENDA', t: 'Dwie wieże Mariackie', x: 'Wieże mają różną wysokość: wyższa (ok. 82 m) była strażnicą miasta, niższa — dzwonnicą. Legenda mówi o dwóch braciach budowniczych, z których jeden z zazdrości zabił drugiego.' },
  wlocznia: { tag: 'FAKT', t: 'Zjazd gnieźnieński (1000)', x: 'Cesarz Otton III przybył do Gniezna, do grobu św. Wojciecha. Podarował Bolesławowi Chrobremu kopię Włóczni św. Maurycego. Włócznia jest do dziś w skarbcu katedry wawelskiej.' },
  szczerbiec: { tag: 'FAKT', t: 'Szczerbiec', x: 'Miecz koronacyjny polskich królów. Legenda mówi, że Bolesław Chrobry wyszczerbił go o Złotą Bramę w Kijowie. Naprawdę miecz wykonano w XII lub XIII w.' },
  smok: { tag: 'LEGENDA', t: 'Smok Wawelski', x: 'Pod Wawelem w jaskini miał żyć smok. Najstarszą wersję legendy spisał biskup Wincenty Kadłubek (ok. 1200 r.). Późniejsza opowieść mówi o szewczyku Skubie i owcy wypchanej siarką.' },
  krzyzacy: { tag: 'FAKT', t: 'Zakon krzyżacki', x: 'W 1226 r. książę Konrad Mazowiecki sprowadził Krzyżaków do walki z Prusami. Zakon zbudował silne państwo i stał się wrogiem Polski i Litwy. Komtur zarządzał zamkiem i okręgiem zakonu.' },
  grunwald: { tag: 'FAKT', t: 'Bitwa pod Grunwaldem', x: '15 lipca 1410 r. wojska polsko-litewskie pod wodzą Jagiełły pokonały Krzyżaków. Zawisza Czarny walczył w tej bitwie w pierwszym szeregu.' },
  golubac: { tag: 'FAKT', t: 'Śmierć pod Gołubcem (1428)', x: 'Zawisza zginął nad Dunajem pod Gołubcem, walcząc z Turkami. Osłaniał odwrót wojsk króla Zygmunta Luksemburskiego i nie chciał uciec bez swoich ludzi.' },
  kazimierz: { tag: 'FAKT', t: 'Miasto Kazimierz', x: 'Osobne miasto założone w 1335 r. przez Kazimierza Wielkiego, oddzielone od Krakowa odnogą Wisły. Dziś to dzielnica Krakowa.' },
  platnerz: { tag: 'FAKT', t: 'Płatnerze i cechy', x: 'Płatnerz wykuwał zbroje płytowe. Rzemieślnicy łączyli się w cechy, które pilnowały jakości wyrobów, cen i szkolenia czeladników.' },
  kusza: { tag: 'FAKT', t: 'Kusza', x: 'Broń strzelająca krótkimi pociskami — bełtami. Strzelała wolniej niż łuk, ale mogła przebić pancerz. Kusznicy bronili murów miejskich.' },
  pozar: { tag: 'FAKT', t: 'Pożary w mieście', x: 'Większość domów była drewniana, więc pożary były wielką klęską średniowiecznych miast. Mieszczanie musieli mieć wiadra, a strażnicy nocą wypatrywali ognia.' },
  dzuma: { tag: 'FAKT', t: 'Czarna śmierć', x: 'W połowie XIV w. epidemia dżumy zabiła w Europie około jednej trzeciej ludzi. Polska ucierpiała mniej niż wiele innych krajów.' },
  fikcja: { tag: 'FIKCJA', t: 'Czarny Komtur i Mrok', x: 'Czarny Komtur, Rycerz Kruka i klątwa Mroku zostały wymyślone na potrzeby tej gry. Prawdziwe skarby Królestwa nigdy nie zostały tak skradzione.' },
};

/* pytania brata Mikołaja i zdarzeń */
D.QUIZ = [
  { q: 'Od jakiego wydarzenia umownie liczymy początek średniowiecza?', a: ['Upadek cesarstwa zachodniorzymskiego (476)', 'Chrzest Polski (966)', 'Bitwa pod Grunwaldem (1410)'], ok: 0, f: 'sredniowiecze' },
  { q: 'Jaki herb nosił Zawisza Czarny?', a: ['Leliwa', 'Sulima', 'Topór'], ok: 1, f: 'sulima' },
  { q: 'Gdzie od 1320 r. koronowano królów Polski?', a: ['W kościele Mariackim', 'W Gnieźnie', 'W katedrze na Wawelu'], ok: 2, f: 'koronacje' },
  { q: 'Jak nazywa się miecz koronacyjny polskich królów?', a: ['Szczerbiec', 'Koncerz', 'Ekskalibur'], ok: 0, f: 'szczerbiec' },
  { q: 'Kim był herold?', a: ['Kucharzem na zamku', 'Znawcą herbów i sędzią turnieju', 'Strażnikiem bramy'], ok: 1, f: 'herold' },
  { q: 'Kto odnowił Akademię Krakowską w 1400 r.?', a: ['Kazimierz Wielki', 'Mieszko I', 'Władysław Jagiełło'], ok: 2, f: 'akademia' },
  { q: 'Kiedy odbyła się bitwa pod Grunwaldem?', a: ['15 lipca 1410 r.', '1 września 1385 r.', '11 listopada 1428 r.'], ok: 0, f: 'grunwald' },
  { q: 'Co znaczy „polegać jak na Zawiszy”?', a: ['Bać się kogoś', 'Całkowicie komuś ufać', 'Szybko biegać'], ok: 1, f: 'polegaj' },
  { q: 'Czym były Sukiennice?', a: ['Halą targową, gdzie handlowano suknem', 'Zamkiem króla', 'Szkołą rycerską'], ok: 0, f: 'sukiennice' },
  { q: 'Kto sprowadził Krzyżaków do Polski w 1226 r.?', a: ['Bolesław Chrobry', 'Konrad Mazowiecki', 'Kazimierz Wielki'], ok: 1, f: 'krzyzacy' },
  { q: 'Kim był giermek?', a: ['Kupcem z Flandrii', 'Młodym pomocnikiem rycerza, który uczył się walki', 'Trębaczem z wieży'], ok: 1, f: 'giermek' },
  { q: 'Kto założył miasto Kazimierz w 1335 r.?', a: ['Kazimierz Wielki', 'Kazimierz Odnowiciel', 'Władysław Łokietek'], ok: 0, f: 'kazimierz' },
  { q: 'Czym strzelała kusza?', a: ['Kamieniami', 'Bełtami', 'Kulami ołowianymi'], ok: 1, f: 'kusza' },
  { q: 'W którym roku zawarto unię w Krewie?', a: ['1385', '1410', '1569'], ok: 0, f: 'jagiello' },
  { q: 'Na jakim prawie lokowano Kraków w 1257 r.?', a: ['Rzymskim', 'Magdeburskim', 'Mazowieckim'], ok: 1, f: 'magdeburg' },
  { q: 'Z której wieży kościoła Mariackiego grany jest hejnał?', a: ['Z niższej', 'Z wyższej', 'Z wieży ratuszowej'], ok: 1, f: 'hejnal' },
  { q: 'Co podarował Otton III Bolesławowi Chrobremu w 1000 r.?', a: ['Kopię Włóczni św. Maurycego', 'Szczerbiec', 'Złotą koronę z Kijowa'], ok: 0, f: 'wlocznia' },
  { q: 'Kto spisał najstarszą wersję legendy o smoku wawelskim?', a: ['Jan Długosz', 'Wincenty Kadłubek', 'Gall Anonim'], ok: 1, f: 'smok' },
];

/* zdarzenia w drodze */
D.EVENTS = [
  { id: 'pielgrzym', t: 'Na moście przez fosę siedzi stary pielgrzym. Wraca z grobu św. Jakuba w Composteli — tysiące kilometrów pieszo. Prosi o kawałek chleba.', c: [
    { t: 'Daj mu chleb (−1 chleb)', cond: s => G.has('chleb'), fx: { honor: 3 }, take: 'chleb', r: 'Pielgrzym błogosławi cię. — Niech światło prowadzi cię przez Mrok, rycerzu.' },
    { t: 'Daj mu 3 grosze (−3 zł)', cond: s => s.gold >= 3, fx: { gold: -3, honor: 2 }, r: 'Starzec kłania się nisko. W średniowieczu pielgrzymki były bardzo popularne — wierzono, że przynoszą odpuszczenie win.' },
    { t: 'Przejdź obojętnie', fx: { honor: -1 }, r: 'Za plecami słyszysz tylko krakanie kruków.' }] },
  { id: 'zbojcy', t: 'W ciemnym zaułku zastępuje ci drogę trzech zbirów z pałkami. — Myto za przejście, panie rycerzu!', c: [
    { t: 'Dobądź miecza!', fx: { gold: 8, honor: 1 }, fight: 18, r: 'Stal błyska w mroku. Zbóje uciekają, gubiąc sakiewkę.' },
    { t: '„Jestem Zawisza Czarny!” (wymaga 20 honoru)', cond: s => s.honor >= 20, fx: { honor: 2 }, r: 'Na dźwięk twojego imienia zbóje bledną i pierzchają. Sława bywa ostrzejsza od miecza.' },
    { t: 'Zapłać 5 zł', cond: s => s.gold >= 5, fx: { gold: -5, honor: -2 }, r: 'Rechot zbirów niesie się po zaułku.' }] },
  { id: 'pozar', t: 'Nad dachami unosi się łuna! Pali się drewniany dom przy ulicy Szewskiej. Ludzie biegają z wiadrami.', fact: 'pozar', c: [
    { t: 'Pomóż gasić ogień', fx: { honor: 4, hp: -10, mrok: -2 }, r: 'Do świtu nosisz wiadra. Ogień nie przeskoczył na sąsiednie domy. Mieszczanie nie zapomną twojej pomocy.' },
    { t: 'Nie masz czasu — idziesz dalej', fx: { honor: -2 }, r: 'Za plecami słyszysz krzyki i trzask belek.' }] },
  { id: 'dzuma', t: 'Przy furcie klasztoru mnich rozdaje zupę. — Ludzie szepczą, że Mrok przyniesie zarazę, jak czarna śmierć za czasów ich dziadów… — mówi cicho.', fact: 'dzuma', c: [
    { t: 'Oddaj zioła dla chorych (−1 zioła)', cond: s => G.has('ziola'), take: 'ziola', fx: { honor: 3, wiedza: 1 }, r: 'Mnich dziękuje. — Klasztorny ogród już nie rodzi. Twoje zioła uratują czyjeś życie.' },
    { t: 'Podziękuj i ruszaj dalej', fx: {}, r: 'Mnich kreśli znak krzyża w powietrzu.' }] },
  { id: 'giermek', t: 'Chudy chłopak w za dużym kaftanie biegnie za tobą. — Panie! Jestem Maciek, syn kowala. Chcę zostać giermkiem! Umiem czyścić zbroję i kochać konie!', fact: 'giermek', c: [
    { t: 'Przyjmij go do pocztu', fx: { honor: 1 }, army: { piechur: 1 }, r: 'Maciek aż podskakuje z radości. Paź, giermek, rycerz — tak zaczynał każdy rycerz.' },
    { t: 'Odeślij go do domu — to zbyt niebezpieczne', fx: { honor: 1 }, r: '— Wrócę, gdy będę starszy! — woła chłopak.' }] },
  { id: 'szpieg', t: 'Ktoś idzie za tobą od kilku ulic. Postać w czarnym kapturze, z piórem kruka przy pasie.', c: [
    { t: 'Zaczaj się i schwytaj go', fx: { gold: 6, mrok: -4 }, fight: 12, r: 'Szpieg Komtura upuszcza sakiewkę i ucieka. Mrok nieco rzednie.' },
    { t: 'Udawaj, że go nie widzisz', fx: { mrok: 3 }, r: 'Postać znika w mgle. Wieczorem kruki krakają głośniej.' }] },
  { id: 'kupiec', t: 'Wędrowny kupiec z Węgier rozkłada towar na wozie. — Zioła z gór, panie! Dwa pęczki za pięć groszy!', c: [
    { t: 'Kup 2 zioła (−5 zł)', cond: s => s.gold >= 5, fx: { gold: -5 }, give: ['ziola', 'ziola'], r: 'Kupiec zawija zioła w płótno. Kraków leżał na szlaku handlowym z Węgier nad Bałtyk.' },
    { t: 'Podziękuj', fx: {}, r: 'Kupiec wzrusza ramionami i zaciąga plandekę.' }] },
  { id: 'mnich', t: 'Młody żak z Akademii zaczepia cię przy kościele. — Rycerzu, założyłem się z kolegą! Rozstrzygnij spór:', quiz: true },
  { id: 'kruki', t: 'Stado kruków obsiada dachy wokół ciebie. Patrzą zielonymi oczami. Jeden zrywa się i rzuca prosto na twoją twarz!', c: [
    { t: 'Osłoń się tarczą', cond: s => s.eq.shield, fx: { honor: 1 }, r: 'Kruk odbija się od tarczy z herbem Sulima i odlatuje z wrzaskiem.' },
    { t: 'Odpędź go mieczem', fx: { hp: -6 }, r: 'Zdążył drapnąć cię szponami. Kruki Komtura są coraz śmielsze.' }] },
];

/* koszty pocztu */
D.ARMY = {
  piechur: { name: 'Piechur z włócznią', price: 6, hp: 6, atk: 2, rng: 1, desc: 'Solidny i tani. Zatrzymuje wroga.' },
  kusznik: { name: 'Kusznik', price: 9, hp: 4, atk: 2, rng: 3, desc: 'Strzela na 3 pola. Nie idzie dalej niż 3. kolumna.' },
  rycerz: { name: 'Rycerz kopijnik', price: 16, hp: 10, atk: 3, rng: 1, honor: 15, desc: 'Najsilniejszy. Służy tylko rycerzowi z honorem (15+).' },
};

/* ---------------- DIALOGI ----------------
   węzeł: { s: mówca, t: tekst, c: [wybory], next, on:{...} }
   wybór: { t, to, fx, fact, item, take, flag, act, ok(true/false = pytanie), cond, end } */
D.DLG = {
  jagiello: {
    start: s => s.flags.audiencja ? (s.artifacts.length >= 4 ? 'koniec' : 'znow') : 'a1',
    a1: { s: 'jagiello', t: 'Zawiszo z Garbowa… Dobrze, że przybyłeś. Od siedmiu nocy nad Krakowem wisi Mrok. Świece gasną same, kruki siadają na dachach, a ludzie szepczą o klątwie.', next: 'a2' },
    a2: { s: 'jagiello', t: 'Ze skarbca na Wawelu zniknęło pięć skarbów Królestwa: pieczęć majestatowa, Złota Ostroga, przywilej Akademii, Włócznia świętego Maurycego… i Szczerbiec.', c: [
      { t: 'Kto ośmielił się okraść króla?', to: 'a3' },
      { t: 'Czym jest Szczerbiec, Najjaśniejszy Panie?', to: 'a2b', fact: 'szczerbiec' }] },
    a2b: { s: 'jagiello', t: 'To miecz, którym od czasów Łokietka koronuje się królów Polski. Mówią, że Chrobry wyszczerbił go o Złotą Bramę w Kijowie. Bez niego żaden król nie zostanie koronowany.', fact: 'koronacje', next: 'a3' },
    a3: { s: 'jagiello', t: 'Zdrajca w czarnym płaszczu. Ludzie zwą go Czarnym Komturem — wyrzucono go nawet z Zakonu Krzyżackiego. Rozproszył skarby po mieście i ukrył je pod strażą swoich sług. Póki są w jego rękach, Mrok gęstnieje.', fact: 'krzyzacy', c: [
      { t: 'Odnajdę je, choćbym miał zejść do samej Smoczej Jamy.', to: 'a4', fx: { honor: 2 } },
      { t: 'Ile mam czasu?', to: 'a3b' }] },
    a3b: { s: 'jagiello', t: 'Każdy dzień zgęszcza Mrok. Gdy pochłonie całe miasto, nie będzie czego ratować. Ale każdy odzyskany skarb rozprasza go. Działaj mądrze — czas to twój najcenniejszy oręż.', next: 'a4' },
    a4: { s: 'jagiello', t: 'Wiem, że na tobie można polegać jak na Zawiszy… — król uśmiecha się blado. — Weź ten list z moją pieczęcią i sakiewkę. Otworzą ci drzwi w całym mieście.', fact: 'polegaj', item: 'list', fx: { gold: 20 }, next: 'a5' },
    a5: { s: 'jagiello', t: 'Zacznij od Rynku. Kupcowa Agnieszka z Sukiennic widziała nocą ludzi Komtura. Brat Mikołaj, mój kronikarz, czeka obok — pomoże ci zrozumieć to, co zobaczysz. A na Kazimierzu kowal Bartosz uzbroi ciebie i twój poczet.', fact: 'jagiello', flag: 'audiencja', end: true },
    znow: { s: 'jagiello', t: 'Mrok wciąż wisi nad miastem, Zawiszo. Ale słyszę, że kruki boją się twojego imienia. Nie ustawaj.', c: [
      { t: 'Opowiedz mi o Litwie, panie.', to: 'litwa' },
      { t: 'Wracam do pracy, Najjaśniejszy Panie.', end: true }] },
    litwa: { s: 'jagiello', t: 'Byłem wielkim księciem litewskim. W Krewie w 1385 roku przyrzekłem przyjąć chrzest i połączyć Litwę z Polską. Rok później poślubiłem królową Jadwigę. Razem jesteśmy silniejsi niż Zakon.', fact: 'jagiello', end: true },
    koniec: { s: 'jagiello', t: 'Cztery skarby wróciły do skarbca! Został tylko Szczerbiec. Kruki zbierają się nad Smoczą Jamą. Daję ci dwóch strażników z zamkowej załogi — weź ich ze sobą.', on: { flagOnce: 'straz', army: { piechur: 2 } }, end: true },
  },
  mikolaj: {
    start: s => 'm1',
    m1: { s: 'mikolaj', t: s => `Pokój z tobą, rycerzu. Zapisuję wszystko, co dzieje się w Królestwie. ${s.chapter <= 5 ? 'Teraz: ' + D.CHAPTERS[s.chapter].goal : ''}`, c: [
      { t: 'Opowiedz o Zawiszy z Garbowa — o mnie samym, z kronik.', to: 'o_zaw', fact: 'zawisza' },
      { t: 'Czym jest średniowiecze?', to: 'o_sr', fact: 'sredniowiecze' },
      { t: 'Kim są Krzyżacy?', to: 'o_krz', fact: 'krzyzacy' },
      { t: 'Poddaj mnie próbie wiedzy (raz na rozdział).', act: 'quiz', cond: s => !s.flags['quiz' + s.chapter] },
      { t: 'Bywaj, bracie.', end: true }] },
    o_zaw: { s: 'mikolaj', t: 'Kroniki mówią, że jesteś najwierniejszym rycerzem Królestwa. Twój herb to Sulima. Ludzie mówią „polegać jak na Zawiszy”, gdy ktoś jest godny zaufania. Nie zawiedź tego przysłowia.', fact: 'sulima', next: 'm1' },
    o_sr: { s: 'mikolaj', t: 'Uczeni z przyszłości nazwą nasze czasy średniowieczem — wiekami średnimi, między starożytnością a nowymi czasami. Od upadku Rzymu w 476 roku do wyprawy Kolumba w 1492. Prawie tysiąc lat!', next: 'm1' },
    o_krz: { s: 'mikolaj', t: 'Zakon Najświętszej Maryi Panny Domu Niemieckiego. Książę Konrad Mazowiecki sprowadził ich w 1226 roku do walki z Prusami. Zbudowali potężne państwo z zamkami, a teraz zagrażają nam i Litwie. Każdym zamkiem rządzi komtur.', next: 'm1' },
  },
  agnieszka: {
    start: s => s.flags.pieczec ? 'po' : 'a1',
    a1: { s: 'agnieszka', t: 'Cicho, rycerzu… kruki słuchają. — Kupcowa rozgląda się nerwowo. — Czy ty jesteś ten Czarny z Garbowa?', c: [
      { t: 'Tak. Przysyła mnie król. (pokaż list)', cond: s => G.has('list'), to: 'a2', fx: { honor: 1 } },
      { t: 'Kim jesteś, pani?', to: 'a1b' }] },
    a1b: { s: 'agnieszka', t: 'Agnieszka, wdowa po kupcu. Handluję suknem z Flandrii — tam, w Sukiennicach, tej wielkiej hali pośrodku Rynku. Kraków to bogate miasto, rycerzu. Należymy do Hanzy, związku miast kupieckich.', fact: 'sukiennice', on: { fact: 'hanza' }, next: 'a2' },
    a2: { s: 'agnieszka', t: 'Trzy noce temu ludzie w kapturach przynieśli do hali trzy worki. Mówili, że to sól z Wieliczki. Ale jeden z nich… zadzwonił jak metal, gdy go rzucili.', c: [
      { t: 'Sól z Wieliczki?', to: 'sol', fact: 'sol' },
      { t: 'Pokaż mi te worki.', to: 'a3' }] },
    sol: { s: 'agnieszka', t: 'Najcenniejszy towar Królestwa! Kopalnie w Wieliczce i Bochni należą do króla. Solą konserwuje się mięso i ryby na zimę. Za beczkę soli można kupić konia.', next: 'a3' },
    a3: { s: 'agnieszka', t: 'Na każdym worku napisano, ile waży — w grzywnach. Uczciwy kupiec waży towar na miejskiej wadze. Jeśli któryś worek waży inaczej, niż napisano — w nim ukryto skarb!', fact: 'grzywna', c: [
      { t: 'Zważę je.', act: 'waga' },
      { t: 'Przyjdę później.', end: true }] },
    wygrana: { s: 'agnieszka', t: 'Pieczęć majestatowa króla! Patrz — król na tronie, z berłem i jabłkiem. Bez tej pieczęci żaden królewski dokument nie jest ważny. Chcę ci się odwdzięczyć — weź 15 grzywien… to znaczy groszy!', c: [
      { t: 'Przyjmuję z wdzięcznością.', fx: { gold: 15 }, to: 'w2' },
      { t: 'Rycerz nie bierze zapłaty za obowiązek.', fx: { honor: 3 }, to: 'w2' }] },
    w2: { s: 'agnieszka', t: 'Jeszcze jedno. Jeden z kapturników uciekł w stronę Błoni. Krzyczał coś o turnieju i o Rycerzu Kruka. Uważaj na siebie.', end: true },
    po: { s: 'agnieszka', t: 'Na Rynku znów płoną latarnie. Dziękuję ci, rycerzu. Czego potrzebujesz?', c: [
      { t: 'Opowiedz o uczcie u Wierzynka.', to: 'wierz', fact: 'wierzynek' },
      { t: 'Jak duży jest Rynek?', to: 'ryn', fact: 'magdeburg' },
      { t: 'Bywaj, pani.', end: true }] },
    wierz: { s: 'agnieszka', t: 'Było to w 1364 roku. Do Krakowa zjechali cesarz i królowie. Mówią, że mieszczanin Mikołaj Wierzynek wydał dla nich ucztę tak wspaniałą, że opowiada się o niej do dziś!', next: 'po' },
    ryn: { s: 'agnieszka', t: 'Około dwustu kroków w każdą stronę — ogromny! Wyznaczono go w 1257 roku, gdy książę Bolesław Wstydliwy nadał miastu prawo magdeburskie. Ulice biegną prosto jak u szachownicy.', next: 'po' },
  },
  jasko: {
    start: s => s.flags.ostroga ? 'po' : (s.flags.zasady ? 'gotow' : 'j1'),
    j1: { s: 'jasko', t: 'Hej, hej! Kto wjeżdża w szranki? — Herold w pstrokatym kaftanie mierzy cię wzrokiem. — Ach! Pół czarnego orła na złocie, trzy srebrne kamienie na czerwieni… Herb Sulima! Zawisza z Garbowa!', fact: 'herold', on: { fact: 'sulima' }, next: 'j2' },
    j2: { s: 'jasko', t: 'Zły czas na turnieje, rycerzu. Rycerz Kruka, najemnik Komtura, wyzwał całe miasto. Na jego kopii wisi Złota Ostroga z królewskiego skarbca. Kto go pokona — odbierze ją.', c: [
      { t: 'Przyjmuję wyzwanie!', to: 'j3' },
      { t: 'Na czym polega gonitwa?', to: 'zas', fact: 'turniej' }] },
    zas: { s: 'jasko', t: 'Dwóch rycerzy pędzi na siebie po obu stronach szranek — tej drewnianej bariery. Trafienie kopią w tarczę to punkt. Trafienie w hełm — dwa. Kto zrzuci rywala z siodła, wygrywa od razu!', next: 'j3' },
    j3: { s: 'jasko', t: 'Najpierw muszę sprawdzić, czy znasz zasady. Herold pilnuje honoru szranek. Powiedz mi: w co NIE wolno celować kopią?', c: [
      { t: 'W konia przeciwnika.', ok: true, to: 'j4' },
      { t: 'W tarczę przeciwnika.', ok: false, to: 'j3z' },
      { t: 'W hełm przeciwnika.', ok: false, to: 'j3z' }] },
    j3z: { s: 'jasko', t: 'Nie, nie! Tarcza i hełm to właściwe cele. Zranienie konia to hańba — taki rycerz zostaje wyrzucony z turnieju! Zapamiętaj to.', next: 'j4' },
    j4: { s: 'jasko', t: s => G.has('kopia') ? 'Widzę, że masz własną kopię turniejową. Dobrze! Trenuj, a gdy będziesz gotów — wjedź w szranki.' : 'Weź tę kopię turniejową — jesionową, z tępym grotem zwanym koronką. Ma pęknąć na tarczy, a nie przebić człowieka. Gdy będziesz gotów — wjedź w szranki.', on: { flag: 'zasady', giveOnce: 'kopia' }, next: 'gotow' },
    gotow: { s: 'jasko', t: 'Rycerz Kruka czeka po drugiej stronie szranek. Tłum milknie. Wiatr szarpie chorągwie.', c: [
      { t: 'Do szranek! (gonitwa)', act: 'joust' },
      { t: 'Jeszcze nie — muszę się przygotować.', end: true }] },
    wygrana: { s: 'jasko', t: 'Rycerz Kruka leży w błocie! Złota Ostroga należy do ciebie! Wiesz, że złote ostrogi nosi tylko pasowany rycerz? Giermek dostaje je dopiero przy pasowaniu.', fact: 'pasowanie', next: 'kruk' },
    kruk: { s: 'kruk', t: 'Khh… Wygrałeś, Sulimczyku. Ale Komtur ma szpiega w Akademii… wśród ksiąg… Już tam szuka twojej zguby…', end: true },
    po: { s: 'jasko', t: 'Jeszcze dziś opowiadają o twojej gonitwie! Kto wie, może kiedyś wygrasz turniej na drugim końcu Europy?', c: [
      { t: 'Kto wie… (posłuchaj przepowiedni herolda)', to: 'perp', fact: 'perpignan' },
      { t: 'Bywaj, heroldzie.', end: true }] },
    perp: { s: 'jasko', t: 'Śniło mi się, że w dalekim Perpignan, przy granicy hiszpańskiej, wysadzasz z siodła słynnego rycerza z Aragonii — jednym uderzeniem! Kroniki zapiszą to w roku 1415.', end: true },
  },
  stanislaw: {
    start: s => s.flags.przywilej ? 'po' : 's1',
    s1: { s: 'stanislaw', t: 'Wejdź, rycerzu, ale ostrożnie — od trzech nocy świece gasną tu same. — Starszy mężczyzna w czerwonym birecie podnosi lampę. — Jestem Stanisław ze Skarbimierza, rektor tej Akademii.', c: [
      { t: 'Szukam szpiega Komtura.', to: 's2' }] },
    s2: { s: 'stanislaw', t: 'Był tu. Udawał żaka. Ale zanim powiem więcej — sprawdzę, czy rycerz szanuje wiedzę. Kto założył naszą Akademię?', c: [
      { t: 'Kazimierz Wielki, w 1364 roku.', ok: true, to: 's3' },
      { t: 'Bolesław Chrobry.', ok: false, to: 's2z' },
      { t: 'Król Władysław Jagiełło.', ok: false, to: 's2y' }] },
    s2z: { s: 'stanislaw', t: 'Chrobry żył ponad trzysta lat wcześniej! Akademię założył Kazimierz Wielki w 1364 roku. Był to pierwszy uniwersytet w Królestwie.', next: 's3' },
    s2y: { s: 'stanislaw', t: 'Prawie! Jagiełło ją odnowił, w roku 1400. Ale założył ją Kazimierz Wielki w 1364 roku.', next: 's3' },
    s3: { s: 'stanislaw', t: 'Po śmierci Kazimierza Akademia podupadła. Królowa Jadwiga oddała swoje klejnoty, by mogła się odrodzić. A teraz szpieg wykradł przywilej odnowienia i zamknął go w skrzyni z „zamkiem dziejów”.', fact: 'akademia', on: { fact: 'jadwiga' }, next: 's4' },
    s4: { s: 'stanislaw', t: 'Zamek otworzy tylko ten, kto ułoży wydarzenia w porządku czasu. Szpieg kpił, że rycerze umieją tylko machać mieczem…', c: [
      { t: 'Rycerz bez wiedzy jest jak miecz bez ostrza. Pokaż skrzynię.', fx: { honor: 1 }, act: 'timeline' },
      { t: 'Mistrzu, czy wojna z Zakonem jest sprawiedliwa?', to: 'just', fact: 'skarbimierz' }] },
    just: { s: 'stanislaw', t: 'Napisałem o tym kazanie. Wojna jest sprawiedliwa tylko wtedy, gdy bronimy się przed krzywdą — a nie gdy chcemy grabić. Nawet wobec pogan trzeba zachować prawo. Zapamiętaj to, gdy staniesz do bitwy.', c: [
      { t: 'Mądre słowa, mistrzu. Zapamiętam.', fx: { wiedza: 2 }, to: 's4' }] },
    wygrana: { s: 'stanislaw', t: 'Przywilej króla z roku 1400! Akademia ocalona! Ale spójrz — szpieg zostawił w skrzyni liścik: „Gdy hejnał zamilknie, Mrok zapanuje”. Spiesz do kościoła Mariackiego!', end: true },
    po: { s: 'stanislaw', t: 'Studenci znów czytają przy świecach, które nie gasną. Wiedza to światło, rycerzu.', c: [
      { t: 'Czego uczą się tu żacy?', to: 'nauka' },
      { t: 'Bywaj, mistrzu.', end: true }] },
    nauka: { s: 'stanislaw', t: 'Najpierw sztuk wyzwolonych: gramatyki, retoryki, logiki, arytmetyki, geometrii, astronomii i muzyki. Potem prawa, medycyny albo teologii. Wszystko po łacinie!', fx: { wiedza: 1 }, end: true },
  },
  wojciech: {
    start: s => s.flags.wlocznia ? 'po' : 'w1',
    w1: { s: 'wojciech', t: 'Rycerzu! — Młody trębacz wybiega z cienia, ściskając trąbkę. — Od trzech nocy nie mogę zagrać hejnału. Kruki Komtura obsiadły wieżę… a na samym szczycie coś lśni w ich gnieździe.', fact: 'hejnal', next: 'w2' },
    w2: { s: 'wojciech', t: 'Gram z wyższej wieży, na cztery strony świata. A wiesz, czemu hejnał urywa się w połowie?', c: [
      { t: 'Hejnalistę trafiła tatarska strzała — tak mówi legenda.', ok: true, to: 'w3', fact: 'hejnal_leg' },
      { t: 'Bo trębacz zapomniał dalszej części.', ok: false, to: 'w2z' }] },
    w2z: { s: 'wojciech', t: 'Ha! Nie. Legenda mówi, że hejnalista ostrzegał przed Tatarami i strzała przeszyła mu gardło. Na jego pamiątkę melodia urywa się w tym samym miejscu.', fact: 'hejnal_leg', next: 'w3' },
    w3: { s: 'wojciech', t: 'Dlaczego wieże są różne? Wyższa to strażnica miasta, niższa — dzwonnica kościoła. Ale ludzie mówią o dwóch braciach… Mniejsza o to! Kruki boją się tylko prawdziwego hejnału. Powtarzaj dźwięki, które ci zagram!', fact: 'wieze', c: [
      { t: 'Daj trąbkę. (hejnał)', act: 'hejnal' },
      { t: 'Wrócę później.', end: true }] },
    wygrana: { s: 'wojciech', t: 'Kruki odlatują! Patrz — w ich gnieździe… Włócznia świętego Maurycego! Ta, którą cesarz Otton podarował Chrobremu w Gnieźnie!', fact: 'wlocznia', next: 'w5' },
    w5: { s: 'wojciech', t: 'Kruki lecą nad Wisłę — prosto ku Smoczej Jamie pod Wawelem. Tam jest Komtur, rycerzu. Zbierz poczet u Bartosza, zanim zejdziesz w ciemność!', fact: 'smok', end: true },
    po: { s: 'wojciech', t: 'Hejnał znów brzmi nad Krakowem co godzinę! Dziękuję, rycerzu.', end: true },
  },
  bartosz: {
    start: s => 'b1',
    b1: { s: 'bartosz', t: 'Kowal ociera pot z czoła. — Zbroja? Miecz? A może ludzi ci trzeba? Na Kazimierzu jest wielu chętnych do służby — za uczciwy żołd.', c: [
      { t: 'Pokaż swoje wyroby. (sklep)', act: 'shop' },
      { t: 'Potrzebuję ludzi do pocztu. (werbunek)', act: 'recruit' },
      { t: 'Czym jest Kazimierz?', to: 'kaz', fact: 'kazimierz' },
      { t: 'Jak powstaje zbroja?', to: 'zbr', fact: 'platnerz' },
      { t: 'Bywaj, mistrzu.', end: true }] },
    kaz: { s: 'bartosz', t: 'Osobne miasto, założone przez Kazimierza Wielkiego w 1335 roku! Mamy własny ratusz, rynek i mury. Od Krakowa dzieli nas odnoga Wisły.', next: 'b1' },
    zbr: { s: 'bartosz', t: 'Płatnerz kuje każdą płytę osobno — na naramiennik, napierśnik, nagolenniki. Potem hartuje w wodzie i poleruje. Nasz cech pilnuje, by nikt nie sprzedawał bubli! Nad zbroją pracuje się tygodniami.', next: 'b1' },
  },
  komtur: {
    start: s => 'k1',
    k1: { s: 'komtur', t: 'Ach… Zawisza. Rycerz, na którym wszyscy polegają. — Głos odbija się echem od skał. — Wiesz, czym jest Mrok? To strach ludzi. Im dłużej się boją, tym jestem silniejszy.', fact: 'fikcja', c: [
      { t: 'Oddaj Szczerbiec, a odejdziesz żywy.', fx: { honor: 2 }, to: 'k3' },
      { t: 'Dlaczego zdradziłeś?', to: 'k2' }] },
    k2: { s: 'komtur', t: 'Zakon dał mi zamek i władzę. A potem mi ją odebrał. Teraz wezmę sobie całe Królestwo! A ty? Co dał ci twój król? Honor? Honorem nie nakarmisz konia.', c: [
      { t: 'Honor jest wart więcej niż złoto.', fx: { honor: 2 }, to: 'k3' },
      { t: 'Dość słów.', to: 'k3' }] },
    k3: { s: 'komtur', t: s => `Zatem walcz! Moi ludzie czekają w ciemności. — Z mroku wyłaniają się najemnicy. Twój poczet: ${G.armyCount()} ludzi.`, c: [
      { t: 'Za Kraków! Za Królestwo! (bitwa)', act: 'battle' },
      { t: 'Wycofaj się i przygotuj lepiej.', end: true }] },
  },
};

/* epilog */
D.EPILOG = [
  'Gdy Szczerbiec wrócił do skarbca na Wawelu, Mrok rozwiał się jak poranna mgła nad Wisłą. Kruki odleciały. Nad Krakowem znów zabrzmiał hejnał.',
  'Rok później, 15 lipca 1410 r., Zawisza Czarny walczył pod Grunwaldem w pierwszym szeregu. Wojska Jagiełły pokonały Krzyżaków.',
  'W 1415 r. w Perpignan wysadził z siodła słynnego rycerza z Aragonii. Służył jako poseł królów i bywał na soborze w Konstancji.',
  'Zginął w 1428 r. pod Gołubcem nad Dunajem. Osłaniał odwrót wojsk przed Turkami — nie chciał uciec bez swoich ludzi.',
  'Do dziś mówimy: „polegać jak na Zawiszy”.',
];
