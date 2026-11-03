# -*- mode: python ; coding: utf-8 -*-
# Budowanie:  pyinstaller zamosc.spec   ->  dist/ZamoyskiMiastoIdealne.exe
import sys

a = Analysis(
    ["main.py"],
    pathex=[],
    datas=[("assets", "assets")],
    hiddenimports=[],
    excludes=["tkinter", "numpy"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ZamoyskiMiastoIdealne",
    console=False,
    icon="assets/ikona.ico" if sys.platform == "win32" else None,
    upx=False,
)
