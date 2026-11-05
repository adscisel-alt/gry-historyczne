# -*- mode: python ; coding: utf-8 -*-
# Budowanie:  pyinstaller --noconfirm KronikiDamianaScisla.spec
a = Analysis(
    ["main.py"],
    pathex=[],
    datas=[("assets/fonts", "assets/fonts"), ("assets/3d", "assets/3d")],
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
    name="KronikiDamianaScisla",
    console=False,
    upx=False,
    icon="assets/icon.ico",
)
