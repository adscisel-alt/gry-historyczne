@echo off
REM Budowanie gry "Listopad 1918" do pliku EXE na Windows 11.
REM Wymaga Pythona 3.10+ (python.org, zaznacz "Add to PATH").
cd /d "%~dp0"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt || goto blad
python build_exe.py || goto blad
echo.
echo Gotowe! Plik: dist\Listopad1918.exe
pause
exit /b 0
:blad
echo Cos poszlo nie tak. Sprawdz komunikaty powyzej.
pause
exit /b 1
