# -*- coding: utf-8 -*-
"""Zapis danych: plik JSON na dysku (Windows/Linux) albo localStorage w przeglądarce."""
import json
import os
import sys

WEB = sys.platform == "emscripten"


def _path(key):
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".config")
    d = os.path.join(base, "KronikiDamianaScisla")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, key + ".json")


def load(key, default=None):
    try:
        if WEB:
            from platform import window  # pygbag
            raw = window.localStorage.getItem("kds_" + key)
            return json.loads(raw) if raw else default
        with open(_path(key), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save(key, obj):
    try:
        raw = json.dumps(obj, ensure_ascii=False)
        if WEB:
            from platform import window
            window.localStorage.setItem("kds_" + key, raw)
            return True
        with open(_path(key), "w", encoding="utf-8") as f:
            f.write(raw)
        return True
    except Exception:
        return False


def delete(key):
    try:
        if WEB:
            from platform import window
            window.localStorage.removeItem("kds_" + key)
        elif os.path.exists(_path(key)):
            os.remove(_path(key))
    except Exception:
        pass


def location():
    return "pamięć przeglądarki" if WEB else os.path.dirname(_path("x"))
