# -*- coding: utf-8 -*-
"""Udostępnianie plików graczowi: zapis do Dokumentów (Windows) albo pobranie w przeglądarce."""
import base64
import os
import sys

WEB = sys.platform == "emscripten"


def documents_dir():
    for base in (os.environ.get("USERPROFILE"), os.path.expanduser("~")):
        if base:
            for sub in ("Documents", "Dokumenty"):
                d = os.path.join(base, sub)
                if os.path.isdir(d):
                    return d
    return os.path.expanduser("~")


def offer(filename, data, mime):
    """Zwraca komunikat dla gracza, gdzie znajdzie plik."""
    if WEB:
        try:
            from platform import window
            b64 = base64.b64encode(data).decode("ascii")
            window.eval(
                "(function(){const a=document.createElement('a');"
                f"a.href='data:{mime};base64,{b64}';a.download='{filename}';"
                "document.body.appendChild(a);a.click();a.remove();})()")
            return f"Plik „{filename}” został pobrany przez przeglądarkę (folder Pobrane)."
        except Exception as e:  # pragma: no cover
            return f"Nie udało się pobrać pliku: {e}"
    folder = os.path.join(documents_dir(), "Kroniki Damiana Scisla")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(data)
    return f"Zapisano plik:\n{path}"
