@echo off
REM Buduje KronikiDamianaScisla.exe (Windows 10/11). Wymaga Pythona 3.10+.
python -m pip install --upgrade pygame-ce pyinstaller
python -m PyInstaller --noconfirm KronikiDamianaScisla.spec
echo.
echo Gotowe: dist\KronikiDamianaScisla.exe
pause
