@echo off
chcp 65001 >nul
title Glitch Lab - Development Mode

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
)

echo.
echo ========================================
echo  GLITCH LAB - DEVELOPMENT MODE
echo ========================================
echo Automatyczne przeladowanie przy zmianach
echo Monitorowane pliki: *.py
echo Nacisnij Ctrl+C aby zakonczyc
echo.

%PYTHON_CMD% -c "
import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_app()
    
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.py'):
            print(f'[{time.strftime(\"%%H:%%M:%%S\")}] Zmiana w pliku: {os.path.basename(event.src_path)}')
            self.restart_app()
    
    def restart_app(self):
        if self.process:
            print('[{}] Zamykanie aplikacji...'.format(time.strftime('%%H:%%M:%%S')))
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        print('[{}] Uruchamianie Glitch Lab...'.format(time.strftime('%%H:%%M:%%S')))
        self.process = subprocess.Popen(['%PYTHON_CMD%', 'main.py'])

if __name__ == '__main__':
    handler = ReloadHandler()
    observer = Observer()
    observer.schedule(handler, '.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n[{}] Zatrzymywanie...'.format(time.strftime('%%H:%%M:%%S')))
        observer.stop()
        if handler.process:
            handler.process.terminate()
    
    observer.join()
"

:end