# -*- coding: utf-8 -*-
"""Kroniki Damiana Ścisła II: Rzeczpospolita – strategia turowa z historii Polski 1454–1795.

Uruchomienie:  python main.py
Zrzuty ekranu: python main.py --screenshots katalog
Przeglądarka:  pygbag (patrz README) – ten sam plik, pętla asyncio.
"""
import asyncio
import sys

import pygame  # noqa: F401 – pygbag pobiera biblioteki według importów w main.py


def _web_report(tb):
    """W przeglądarce: wypisz błąd do konsoli JS (widoczny w narzędziach deweloperskich i w teście)."""
    try:
        from platform import window
        window.console.log("KRONIKI:TRACEBACK\n" + tb)
        window.document.title = "KRONIKI:ERROR"
    except Exception:
        pass


async def main():
    try:
        from kronika.app import App
        await App().run_async()
    except Exception:
        import traceback
        tb = traceback.format_exc()
        print(tb)
        _web_report(tb)


if __name__ == "__main__":
    if sys.platform == "emscripten":
        asyncio.run(main())
    else:
        from kronika.app import main as cli_main
        cli_main()
