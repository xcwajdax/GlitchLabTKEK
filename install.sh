#!/bin/bash

# Glitch Lab - Instalator dla Linux/macOS
# Automatyczna instalacja Python i wymaganych bibliotek

set -e

echo "⚡ GLITCH LAB - INSTALATOR ⚡"
echo "================================"
echo

# Kolory dla lepszej czytelności
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funkcja do wyświetlania kolorowych komunikatów
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Wykryj system operacyjny
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    print_error "Nieobsługiwany system operacyjny: $OSTYPE"
    exit 1
fi

print_info "Wykryto system: $OS"
echo

# Sprawdź czy Python jest zainstalowany
echo "[1/4] Sprawdzanie Pythona..."

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_status "Python znaleziony: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        print_status "Python znaleziony: $PYTHON_VERSION"
        PYTHON_CMD="python"
    else
        print_error "Znaleziono Python 2. Wymagany jest Python 3."
        PYTHON_CMD=""
    fi
fi

# Instaluj Python jeśli nie znaleziono
if [ -z "$PYTHON_CMD" ]; then
    echo
    echo "[2/4] Instalowanie Pythona..."
    
    if [ "$OS" == "linux" ]; then
        # Wykryj dystrybucję Linux
        if command -v apt-get &> /dev/null; then
            print_info "Instalowanie Python przez apt (Ubuntu/Debian)..."
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-tk
            PYTHON_CMD="python3"
        elif command -v yum &> /dev/null; then
            print_info "Instalowanie Python przez yum (CentOS/RHEL)..."
            sudo yum install -y python3 python3-pip tkinter
            PYTHON_CMD="python3"
        elif command -v dnf &> /dev/null; then
            print_info "Instalowanie Python przez dnf (Fedora)..."
            sudo dnf install -y python3 python3-pip python3-tkinter
            PYTHON_CMD="python3"
        elif command -v pacman &> /dev/null; then
            print_info "Instalowanie Python przez pacman (Arch Linux)..."
            sudo pacman -S python python-pip tk
            PYTHON_CMD="python3"
        else
            print_error "Nieobsługiwany menedżer pakietów. Zainstaluj Python 3 ręcznie."
            exit 1
        fi
    elif [ "$OS" == "macos" ]; then
        if command -v brew &> /dev/null; then
            print_info "Instalowanie Python przez Homebrew..."
            brew install python-tk
            PYTHON_CMD="python3"
        else
            print_error "Homebrew nie znaleziony. Zainstaluj Python z https://www.python.org/downloads/"
            print_info "Lub zainstaluj Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    fi
    
    # Sprawdź czy instalacja się powiodła
    if ! command -v $PYTHON_CMD &> /dev/null; then
        print_error "Instalacja Pythona nie powiodła się"
        exit 1
    fi
    
    print_status "Python zainstalowany pomyślnie"
fi

echo
echo "[3/4] Sprawdzanie pip..."

# Sprawdź pip
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_info "Instalowanie pip..."
    if [ "$OS" == "linux" ]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-pip
        fi
    elif [ "$OS" == "macos" ]; then
        curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        $PYTHON_CMD get-pip.py
        rm get-pip.py
    fi
fi

if $PYTHON_CMD -m pip --version &> /dev/null; then
    print_status "pip dostępny"
else
    print_error "pip nie został znaleziony"
    exit 1
fi

echo
echo "[4/4] Instalowanie wymaganych bibliotek..."

# Aktualizuj pip
print_info "Aktualizowanie pip..."
$PYTHON_CMD -m pip install --upgrade pip

# Instaluj biblioteki
print_info "Instalowanie Pillow..."
$PYTHON_CMD -m pip install Pillow
if [ $? -ne 0 ]; then
    print_error "Nie udało się zainstalować Pillow"
    exit 1
fi

print_info "Instalowanie NumPy..."
$PYTHON_CMD -m pip install numpy
if [ $? -ne 0 ]; then
    print_error "Nie udało się zainstalować NumPy"
    exit 1
fi

print_info "Instalowanie watchdog (opcjonalne)..."
$PYTHON_CMD -m pip install watchdog
if [ $? -ne 0 ]; then
    print_warning "Watchdog nie został zainstalowany - auto-restart może nie działać"
fi

echo
echo "Sprawdzanie instalacji..."
$PYTHON_CMD -c "import PIL; print('✓ Pillow:', PIL.__version__)" 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Problem z Pillow"
    exit 1
fi

$PYTHON_CMD -c "import numpy; print('✓ NumPy:', numpy.__version__)" 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Problem z NumPy"
    exit 1
fi

$PYTHON_CMD -c "import tkinter; print('✓ Tkinter: dostępny')" 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "Problem z Tkinter"
    exit 1
fi

echo
echo "================================"
echo -e "${GREEN}✅ INSTALACJA ZAKOŃCZONA POMYŚLNIE!${NC}"
echo "================================"
echo
echo "Wszystkie wymagane komponenty zostały zainstalowane:"
echo "• Python ($PYTHON_CMD)"
echo "• Pillow (PIL) - przetwarzanie obrazów"
echo "• NumPy - operacje na tablicach"
echo "• Tkinter - interfejs graficzny"
echo
echo "Możesz teraz uruchomić Glitch Lab używając:"
echo "• $PYTHON_CMD main.py"
echo
echo "Naciśnij Enter aby zamknąć..."
read