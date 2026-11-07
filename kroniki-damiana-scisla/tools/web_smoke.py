# -*- coding: utf-8 -*-
"""Test dymny wersji przeglądarkowej: otwiera grę w Chromium, klika start, robi zrzut i szuka błędów Pythona.

python tools/web_smoke.py <katalog build/web> <plik_zrzutu.png>
"""
import http.server
import socketserver
import sys
import threading
import time
from functools import partial

from playwright.sync_api import sync_playwright

root, shot = sys.argv[1], sys.argv[2]
handler = partial(http.server.SimpleHTTPRequestHandler, directory=root)
httpd = socketserver.TCPServer(("127.0.0.1", 8123), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

errors, logs = [], []
with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    page = b.new_page(viewport={"width": 1280, "height": 760})
    page.on("console", lambda m: logs.append(m.text))
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto("http://127.0.0.1:8123/index.html")
    t0 = time.time()
    clicked = False
    while time.time() - t0 < 150:
        page.wait_for_timeout(3000)
        page.mouse.click(640, 380)
        page.keyboard.press("Space")
        clicked = True
        try:
            title = page.title()
        except Exception:
            title = ""
        if "KRONIKI:ERROR" in title:
            break
        if "KRONIKI:MENU" in title:
            logs.append("KRONIKI:MENU (tytuł strony)")
        joined = "\n".join(logs)
        if "Traceback" in joined:
            break
        if "KRONIKI:MENU" in joined:
            page.wait_for_timeout(6000)
            # przejdź do kampanii i wybierz rozdział I – sprawdza też kolejne ekrany
            page.mouse.click(230, 395)
            page.wait_for_timeout(2500)
            page.screenshot(path=shot.replace(".png", "_kampania.png"))
            break
        # menu gry narysowane? sprawdź, czy płótno ma treść (nie jednolity kolor)
        ok = page.evaluate("""() => {
            const c = document.querySelector('canvas'); if (!c) return false;
            try { const g = c.getContext('2d'); } catch(e) {}
            return c.width >= 640;
        }""")
    page.wait_for_timeout(500)
    page.screenshot(path=shot)
    try:
        body = page.evaluate("() => document.body.innerText")
    except Exception as e:
        body = f"(brak: {e})"
    b.close()
httpd.shutdown()
tb = [l for l in logs if "Traceback" in l or "Error" in l]
print("Ostatnie logi konsoli:")
for l in logs[-25:]:
    print("  ", l[:300])
if errors:
    print("Błędy strony:", errors[:5])
for l in logs:
    if "KRONIKI:TRACEBACK" in l:
        print(l)
if any("Traceback" in l or "TRACEBACK" in l for l in logs):
    print("BŁĄD: wyjątek Pythona w przeglądarce")
    sys.exit(1)
print("---- tekst strony (terminal pygbag) ----")
print(body[-3000:])
print("----")
if "Traceback" in body:
    print("BŁĄD: wyjątek Pythona w przeglądarce (terminal)")
    sys.exit(1)
if not any("KRONIKI:MENU" in l for l in logs):
    print("BŁĄD: gra nie narysowała menu w ciągu 150 s")
    sys.exit(1)
from PIL import Image
im = Image.open(shot).convert("RGB")
colors = len(set(im.crop((100, 100, 1180, 660)).getdata()))
print("Liczba kolorów na zrzucie:", colors)
if colors < 400:
    print("BŁĄD: zrzut wygląda na pusty ekran")
    sys.exit(1)
print("OK – gra uruchomiła się w przeglądarce")
