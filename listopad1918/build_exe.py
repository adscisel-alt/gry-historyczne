"""Budowanie pliku EXE (Windows 11) PyInstallerem.

Użycie (w katalogu listopad1918):
    pip install -r requirements.txt
    python build_exe.py            # wynik: dist/Listopad1918.exe
    python build_exe.py --bez-testow

Skrypt najpierw uruchamia testy automatyczne, potem generuje ikonę
(proceduralnie, z orzełka z gry) i pakuje grę w jeden plik.
"""
import os
import subprocess
import sys

TUTAJ = os.path.dirname(os.path.abspath(__file__))


def ikona():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    sys.path.insert(0, TUTAJ)
    from gra import grafika as G
    from gra.config import sep
    s = pygame.Surface((256, 256), pygame.SRCALPHA)
    pygame.draw.rect(s, sep(225), (8, 8, 240, 240), border_radius=24)
    pygame.draw.rect(s, sep(40), (8, 8, 240, 240), 8, border_radius=24)
    orz = pygame.transform.smoothscale(G.ikona("orzelek", 64), (200, 200))
    s.blit(orz, (28, 24))
    png = os.path.join(TUTAJ, "build", "ikona.png")
    os.makedirs(os.path.dirname(png), exist_ok=True)
    pygame.image.save(s, png)
    pygame.quit()
    try:
        from PIL import Image
        ico = png[:-4] + ".ico"
        Image.open(png).save(ico, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        return ico
    except ImportError:
        return None


def main():
    os.chdir(TUTAJ)
    if "--bez-testow" not in sys.argv:
        print("== Testy automatyczne ==")
        wynik = subprocess.call([sys.executable, "-m", "pytest", "-q", "tests"])
        if wynik != 0:
            sys.exit("Testy nie przeszły — przerywam budowanie.")
    print("== Ikona ==")
    ico = ikona()
    print("== PyInstaller ==")
    import PyInstaller.__main__
    argumenty = [
        "main.py",
        "--name", "Listopad1918",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--collect-submodules", "gra",
    ]
    if ico:
        argumenty += ["--icon", ico]
    PyInstaller.__main__.run(argumenty)
    nazwa = "Listopad1918.exe" if os.name == "nt" else "Listopad1918"
    print("\nGotowe: " + os.path.join(TUTAJ, "dist", nazwa))


if __name__ == "__main__":
    main()
