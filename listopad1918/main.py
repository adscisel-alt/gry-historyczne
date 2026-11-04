"""Listopad 1918 — Pocztówki z niepodległości. Uruchomienie: python main.py

Opcje:
  --autotest   przechodzi całą grę automatem (logika) i kończy z kodem 0/1
"""
import sys


def main():
    if sys.stdout is None:  # tryb --windowed (EXE bez konsoli)
        import os
        sys.stdout = sys.stderr = open(os.devnull, "w")
    if "--autotest" in sys.argv:
        from gra.automat import autotest
        sys.exit(0 if autotest() else 1)
    from gra.aplikacja import Aplikacja
    Aplikacja().uruchom()


if __name__ == "__main__":
    main()
