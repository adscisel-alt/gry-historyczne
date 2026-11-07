@echo off
REM Buduje ZamoyskiMiastoIdealne.exe na Windows 11 (wymaga Pythona 3.10+)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
python narzedzia\generuj_zasoby.py
python -m PyInstaller --noconfirm zamosc.spec
echo.
echo Gotowe: dist\ZamoyskiMiastoIdealne.exe
pause
