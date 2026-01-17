@echo off
chcp 65001 >nul
title Glitch Lab

echo Sprawdzanie Pythona...

py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python: & py --version
    echo.
    echo Uruchamianie Glitch Lab...
    py main.py
    goto :end
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python: & python --version
    echo.
    echo Uruchamianie Glitch Lab...
    python main.py
    goto :end
)

echo BLAD: Python nie zostal znaleziony!
echo Zainstaluj: https://www.python.org/downloads/
pause

:end