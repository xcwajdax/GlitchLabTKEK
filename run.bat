@echo off
chcp 65001 >nul
title Glitch Lab - Autoreload

echo Sprawdzanie Pythona...

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    echo Python: & py --version
    goto :check_watchdog
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo Python: & python --version
    goto :check_watchdog
)

echo BLAD: Python nie zostal znaleziony!
echo Zainstaluj: https://www.python.org/downloads/
pause
goto :end

:check_watchdog
echo Sprawdzanie watchdog...
%PYTHON_CMD% -c "import watchdog" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalowanie watchdog dla autoreload...
    %PYTHON_CMD% -m pip install watchdog
    if %errorlevel% neq 0 (
        echo BLAD: Nie udalo sie zainstalowac watchdog
        echo Uruchamianie bez autoreload...
        goto :run_normal
    )
)

echo.
echo ========================================
echo  GLITCH LAB - TRYB AUTORELOAD
echo ========================================
echo Automatyczne przeladowanie przy zmianach w plikach *.py
echo Monitorowanie rekurencyjne wszystkich folderow
echo Nacisnij Ctrl+C aby zakonczyc
echo.

echo [%time%] Uruchamianie z autoreload...
%PYTHON_CMD% -m watchdog.watchmedo auto-restart --patterns="*.py" --recursive -- %PYTHON_CMD% main.py
goto :end

:run_normal
echo [%time%] Uruchamianie Glitch Lab (bez autoreload)...
%PYTHON_CMD% main.py

:end
