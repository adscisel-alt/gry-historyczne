# -*- mode: python ; coding: utf-8 -*-
# Budowanie:  pyinstaller --noconfirm KronikiTomkaTurby.spec
a = Analysis(
    ["main.py"],
    pathex=[],
    datas=[("assets/fonts", "assets/fonts")],
    hiddenimports=[],
    excludes=["tkinter", "numpy", "unittest", "pydoc"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="KronikiTomkaTurby",
    console=False,
    upx=False,
    icon="assets/icon.ico",
)
