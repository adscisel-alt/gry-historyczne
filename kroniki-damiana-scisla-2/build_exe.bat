@echo off
REM Buduje KronikiDamianaScisla2.exe (Windows 10/11). Wymaga Pythona 3.10+.
python -m pip install --upgrade pygame-ce pyinstaller
python -m PyInstaller --noconfirm KronikiDamianaScisla2.spec
echo.
echo Gotowe: dist\KronikiDamianaScisla2.exe
pause
