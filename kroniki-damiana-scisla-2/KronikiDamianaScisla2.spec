# -*- mode: python ; coding: utf-8 -*-
# Budowanie:  pyinstaller --noconfirm KronikiDamianaScisla2.spec
import os

datas = [("assets/fonts", "assets/fonts"), ("assets/3d", "assets/3d"), ("assets/audio", "assets/audio")]
if os.path.isdir("assets/voice"):
    datas.append(("assets/voice", "assets/voice"))   # lektor (tools/make_voice.py)

a = Analysis(
    ["main.py"],
    pathex=[],
    datas=datas,
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
    name="KronikiDamianaScisla2",
    console=False,
    upx=False,
    icon="assets/icon.ico",
)
