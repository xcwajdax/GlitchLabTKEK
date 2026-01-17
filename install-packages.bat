@echo off
chcp 65001 >nul
title Glitch Lab - Instalacja Bibliotek
color 0A

echo.
echo ⚡ GLITCH LAB - INSTALACJA BIBLIOTEK ⚡
echo =====================================
echo.

REM Sprawdź Python
echo Sprawdzanie Pythona...
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python znaleziony: 
    py --version
    set PYTHON_CMD=py
    goto :install
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python znaleziony: 
    python --version
    set PYTHON_CMD=python
    goto :install
)

echo ❌ BŁĄD: Python nie został znaleziony!
echo.
echo Zainstaluj Python z: https://www.python.org/downloads/
echo Lub użyj install.bat dla pełnej instalacji
echo.
pause
exit /b 1

:install
echo.
echo Aktualizowanie pip...
%PYTHON_CMD% -m pip install --upgrade pip

echo.
echo Instalowanie wymaganych bibliotek...
echo.

echo [1/3] Instalowanie Pillow...
%PYTHON_CMD% -m pip install Pillow
if %errorlevel% neq 0 (
    echo ❌ Błąd instalacji Pillow
    goto :error
)

echo [2/3] Instalowanie NumPy...
%PYTHON_CMD% -m pip install numpy
if %errorlevel% neq 0 (
    echo ❌ Błąd instalacji NumPy
    goto :error
)

echo [3/3] Instalowanie watchdog (opcjonalne)...
%PYTHON_CMD% -m pip install watchdog
if %errorlevel% neq 0 (
    echo ⚠ Watchdog nie został zainstalowany - auto-restart może nie działać
)

echo.
echo Sprawdzanie instalacji...
%PYTHON_CMD% -c "import PIL; print('✓ Pillow:', PIL.__version__)"
%PYTHON_CMD% -c "import numpy; print('✓ NumPy:', numpy.__version__)"
%PYTHON_CMD% -c "import tkinter; print('✓ Tkinter: dostępny')"

echo.
echo ================================
echo ✅ BIBLIOTEKI ZAINSTALOWANE!
echo ================================
echo.
echo Glitch Lab jest gotowy do uruchomienia:
echo • run.bat (zalecane)
echo • python main.py
echo.
pause
exit /b 0

:error
echo.
echo ❌ Wystąpił błąd podczas instalacji
echo Spróbuj uruchomić jako administrator lub zainstaluj ręcznie:
echo pip install Pillow numpy
echo.
pause
exit /b 1