// Kopiuje grę (jeden plik HTML z katalogu głównego repozytorium) do paczki Electron.
const fs = require('fs');
const path = require('path');
const zrodlo = path.join(__dirname, '..', 'damian-kapelusz-szyfrow.html');
const cel = path.join(__dirname, 'gra');
fs.mkdirSync(cel, { recursive: true });
fs.copyFileSync(zrodlo, path.join(cel, 'index.html'));
console.log('Skopiowano grę do', cel);
