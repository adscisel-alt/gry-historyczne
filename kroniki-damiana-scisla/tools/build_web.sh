#!/usr/bin/env bash
# Buduje wersję przeglądarkową gry (pygbag → WebAssembly). Wynik: web_build/kroniki-damiana-scisla/build/web/
# Wymaga: pip install pygbag  (oraz dostępu do sieci – pygbag pobiera środowisko uruchomieniowe z CDN).
set -euo pipefail
cd "$(dirname "$0")/.."
STAGE=web_build/kroniki-damiana-scisla
rm -rf web_build
mkdir -p "$STAGE/assets"
cp main.py "$STAGE/"
cp -r kronika "$STAGE/"
cp -r assets/fonts assets/3d assets/audio "$STAGE/assets/"
if [ -d assets/voice ]; then cp -r assets/voice "$STAGE/assets/"; fi
find "$STAGE" -name "__pycache__" -prune -exec rm -rf {} +
python -m pygbag --build --title "Kroniki Damiana Ścisła" "$STAGE"
ls -la "$STAGE/build/web"
