@echo off
chcp 65001 >nul
title Glitch Lab - Instalator
color 0A

echo.
echo ⚡ GLITCH LAB - INSTALATOR ⚡
echo ================================
echo.

REM Sprawdź czy Python jest już zainstalowany
echo [1/4] Sprawdzanie Pythona...
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python już zainstalowany: 
    py --version
    goto :check_pip
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python już zainstalowany: 
    python --version
    goto :check_pip
)

echo ⚠ Python nie znaleziony. Rozpoczynam instalację...
echo.

REM Pobierz i zainstaluj Python
echo [2/4] Pobieranie Python 3.11...
if not exist "python-installer.exe" (
    echo Pobieranie Python 3.11.9 (64-bit)...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'}"
    if %errorlevel% neq 0 (
        echo ❌ BŁĄD: Nie udało się pobrać Pythona
        echo Sprawdź połączenie internetowe lub pobierz ręcznie z:
        echo https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo Instalowanie Pythona...
echo UWAGA: Instalator Pythona otworzy się w osobnym oknie
echo Upewnij się, że zaznaczysz "Add Python to PATH"!
echo.
pause

python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
if %errorlevel% neq 0 (
    echo ❌ BŁĄD: Instalacja Pythona nie powiodła się
    echo Spróbuj zainstalować ręcznie z: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python zainstalowany pomyślnie
echo Odświeżanie zmiennych środowiskowych...
call refreshenv >nul 2>&1

REM Sprawdź pip
:check_pip
echo.
echo [3/4] Sprawdzanie pip...
py -m pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ pip dostępny
    set PYTHON_CMD=py
    goto :install_packages
)

python -m pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ pip dostępny
    set PYTHON_CMD=python
    goto :install_packages
)

echo ❌ BŁĄD: pip nie został znaleziony
echo Spróbuj ponownie uruchomić instalator lub zainstaluj pip ręcznie
pause
exit /b 1

:install_packages
echo.
echo [4/4] Instalowanie wymaganych bibliotek...
echo Instalowanie Pillow (PIL)...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install Pillow
if %errorlevel% neq 0 (
    echo ❌ BŁĄD: Nie udało się zainstalować Pillow
    pause
    exit /b 1
)

echo Instalowanie NumPy...
%PYTHON_CMD% -m pip install numpy
if %errorlevel% neq 0 (
    echo ❌ BŁĄD: Nie udało się zainstalować NumPy
    pause
    exit /b 1
)

echo Instalowanie watchdog (opcjonalne - dla auto-restart)...
%PYTHON_CMD% -m pip install watchdog
if %errorlevel% neq 0 (
    echo ⚠ Watchdog nie został zainstalowany - auto-restart może nie działać
)

REM Sprawdź czy wszystko działa
echo.
echo Sprawdzanie instalacji...
%PYTHON_CMD% -c "import PIL; print('✓ Pillow:', PIL.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Problem z Pillow
    goto :error
)

%PYTHON_CMD% -c "import numpy; print('✓ NumPy:', numpy.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Problem z NumPy
    goto :error
)

%PYTHON_CMD% -c "import tkinter; print('✓ Tkinter: dostępny')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Problem z Tkinter
    goto :error
)

REM Usuń plik instalatora Pythona
if exist "python-installer.exe" (
    del "python-installer.exe" >nul 2>&1
)

echo.
echo ================================
echo ✅ INSTALACJA ZAKOŃCZONA POMYŚLNIE!
echo ================================
echo.
echo Wszystkie wymagane komponenty zostały zainstalowane:
echo • Python %PYTHON_CMD%
echo • Pillow (PIL) - przetwarzanie obrazów
echo • NumPy - operacje na tablicach
echo • Tkinter - interfejs graficzny
echo.
echo Możesz teraz uruchomić Glitch Lab używając:
echo • run.bat (zalecane)
echo • python main.py
echo.
echo Naciśnij dowolny klawisz aby zamknąć...
pause >nul
exit /b 0

:error
echo.
echo ================================
echo ❌ BŁĄD INSTALACJI
echo ================================
echo.
echo Wystąpił problem podczas instalacji.
echo Spróbuj:
echo 1. Uruchomić instalator jako administrator
echo 2. Sprawdzić połączenie internetowe
echo 3. Zainstalować komponenty ręcznie:
echo    pip install Pillow numpy
echo.
pause
exit /b 1