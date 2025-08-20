#!/bin/bash

# CRDB Fee Calculator Installation Script
# Dieses Skript installiert das crdbfee Tool auf Linux-Systemen

set -e

echo "🚀 CRDB Fee Calculator Installation wird gestartet..."

# Prüfe ob Python 3 installiert ist
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 ist nicht installiert. Bitte installieren Sie Python 3 zuerst."
    exit 1
fi

# Prüfe Python Version (mindestens 3.7)
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
    echo "❌ Python 3.7 oder höher ist erforderlich. Gefunden: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION gefunden"

# Prüfe ob venv verfügbar ist
if ! python3 -c "import venv" &> /dev/null; then
    echo "❌ python3-venv ist nicht installiert. Installiere es..."
    sudo apt update
    sudo apt install -y python3-venv
fi

echo "✅ python3-venv verfügbar"

# Erstelle virtuelle Umgebung
VENV_DIR="./venv"
echo "🔧 Erstelle virtuelle Umgebung in $VENV_DIR..."
python3 -m venv "$VENV_DIR"

# Aktiviere virtuelle Umgebung
echo "📦 Aktiviere virtuelle Umgebung und installiere Abhängigkeiten..."
source "$VENV_DIR/bin/activate"

# Upgrade pip in der virtuellen Umgebung
pip install --upgrade pip

# Installiere Abhängigkeiten
echo "📦 Installiere Python-Abhängigkeiten..."
pip install -r requirements.txt

# Erstelle Installationsverzeichnis
INSTALL_DIR="/usr/local/bin"
echo "📁 Installiere in $INSTALL_DIR..."

# Erstelle ein Wrapper-Skript, das die virtuelle Umgebung aktiviert
WRAPPER_SCRIPT="$INSTALL_DIR/crdbfee"
CURRENT_DIR=$(pwd)
sudo tee "$WRAPPER_SCRIPT" > /dev/null << EOF
#!/bin/bash
# Wrapper für crdbfee mit virtueller Umgebung
VENV_PATH="$CURRENT_DIR/venv"
if [ -f "\$VENV_PATH/bin/activate" ]; then
    source "\$VENV_PATH/bin/activate"
    exec "\$VENV_PATH/bin/python" "\$VENV_PATH/crdbfee.py" "\$@"
else
    echo "❌ Virtuelle Umgebung nicht gefunden in \$VENV_PATH"
    echo "Bitte führen Sie das Installationsskript erneut aus."
    exit 1
fi
EOF

# Mache es ausführbar
sudo chmod +x "$WRAPPER_SCRIPT"

# Kopiere das Hauptskript in die virtuelle Umgebung
cp crdbfee.py "$VENV_DIR/"

# Prüfe ob die Installation erfolgreich war
if [ -f "$WRAPPER_SCRIPT" ]; then
    echo "✅ Installation erfolgreich!"
    echo ""
    echo "🎉 Das crdbfee Tool wurde erfolgreich installiert!"
    echo ""
    echo "Verwendung:"
    echo "  crdbfee statement.xlsx"
    echo "  crdbfee --help"
    echo ""
    echo "Das Tool ist jetzt von überall verfügbar."
    echo ""
    echo "💡 Hinweis: Die virtuelle Umgebung befindet sich in $VENV_DIR"
    echo "   Löschen Sie diesen Ordner nicht, da das Tool darauf angewiesen ist."
else
    echo "❌ Installation fehlgeschlagen!"
    exit 1
fi

