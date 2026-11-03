@echo off
REM Buduje KronikiTomkaTurby.exe (Windows 10/11). Wymaga Pythona 3.10+.
python -m pip install --upgrade pygame-ce pyinstaller
python -m PyInstaller --noconfirm KronikiTomkaTurby.spec
echo.
echo Gotowe: dist\KronikiTomkaTurby.exe
pause
