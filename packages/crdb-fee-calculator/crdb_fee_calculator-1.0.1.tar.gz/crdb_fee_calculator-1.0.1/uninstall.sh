#!/bin/bash

# CRDB Fee Calculator Deinstallation Script

echo "🗑️  CRDB Fee Calculator Deinstallation wird gestartet..."

INSTALL_DIR="/usr/local/bin"
TOOL_NAME="crdbfee"
VENV_DIR="./venv"

# Prüfe ob das Tool installiert ist
if [ -f "$INSTALL_DIR/$TOOL_NAME" ]; then
    echo "📁 Entferne $TOOL_NAME aus $INSTALL_DIR..."
    sudo rm "$INSTALL_DIR/$TOOL_NAME"
    
    if [ ! -f "$INSTALL_DIR/$TOOL_NAME" ]; then
        echo "✅ Tool erfolgreich entfernt!"
    else
        echo "❌ Entfernung des Tools fehlgeschlagen!"
        exit 1
    fi
else
    echo "ℹ️  Das Tool ist nicht installiert."
fi

# Entferne virtuelle Umgebung
if [ -d "$VENV_DIR" ]; then
    echo "🗑️  Entferne virtuelle Umgebung..."
    rm -rf "$VENV_DIR"
    
    if [ ! -d "$VENV_DIR" ]; then
        echo "✅ Virtuelle Umgebung erfolgreich entfernt!"
    else
        echo "❌ Entfernung der virtuellen Umgebung fehlgeschlagen!"
        exit 1
    fi
else
    echo "ℹ️  Virtuelle Umgebung nicht gefunden."
fi

echo ""
echo "🎉 Deinstallation erfolgreich abgeschlossen!"
echo "Alle CRDB Fee Calculator Dateien wurden entfernt."

