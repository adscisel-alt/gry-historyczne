# -*- coding: utf-8 -*-
"""Kroniki Damiana Ścisła – strategia turowa z historii Polski 966–1410.

Uruchomienie:  python main.py
Zrzuty ekranu: python main.py --screenshots katalog
Przeglądarka:  pygbag (patrz README) – ten sam plik, pętla asyncio.
"""
import asyncio
import sys

from kronika.app import App, main as cli_main


async def main():
    await App().run_async()


if __name__ == "__main__":
    if sys.platform == "emscripten":
        asyncio.run(main())
    else:
        cli_main()
