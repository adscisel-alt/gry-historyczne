"""Wbudowuje obrazy velum-obrazy/NN.jpg (1024×672) w velum-rzym.html jako data-URI.

Uruchom po dodaniu lub podmianie obrazu:  python velum-obrazy/osadz.py
Obraz NN.jpg trafia do poziomu o indeksie NN (00 = poziom I). Poziomy bez pliku
używają ilustracji malowanej kodem. Opis obrazu (autor, tytuł, rok) jest w POZIOMY[].obraz.
"""
import base64, os, re

KAT = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(KAT, "..", "velum-rzym.html")

dane = []
for i in range(9):
    p = os.path.join(KAT, f"{i:02d}.jpg")
    dane.append("'data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode() + "'" if os.path.exists(p) else "null")

blok = "/*OBRAZY-START*/\nconst OBRAZY_DANE = [\n" + ",\n".join(dane) + "\n];\n/*OBRAZY-END*/"
s = open(HTML, encoding="utf-8").read()
s, n = re.subn(r"/\*OBRAZY-START\*/.*?/\*OBRAZY-END\*/", lambda m: blok, s, flags=re.S)
assert n == 1, "nie znaleziono znaczników OBRAZY-START/END"
open(HTML, "w", encoding="utf-8").write(s)
print("osadzono:", sum(d != "null" for d in dane), "obrazów;", os.path.getsize(HTML) // 1024, "KB")
