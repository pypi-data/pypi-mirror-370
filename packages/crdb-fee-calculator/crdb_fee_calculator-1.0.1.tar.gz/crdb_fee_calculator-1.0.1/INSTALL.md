# Schnellinstallation CRDB Fee Calculator

## 🚀 Einfache Installation (empfohlen)

```bash
# 1. Repository klonen oder herunterladen
git clone <repository-url>
cd crdb_fee_calculator

# 2. Installation starten
chmod +x install.sh
./install.sh
```

## 📋 Alternative Installation mit Make

```bash
# Installation
make install

# Deinstallation
make uninstall

# Hilfe anzeigen
make help
```

## 🧪 Test des Tools

```bash
# Testdatei erstellen
python3 create_test_data.py

# Tool testen
crdbfee test_statement.xlsx
```

## ✅ Verwendung

Nach der Installation können Sie das Tool von überall verwenden:

```bash
crdbfee statement.xlsx
crdbfee --help
crdbfee --version
```

## 🗑️ Deinstallation

```bash
./uninstall.sh
# oder
make uninstall
```

---

**Hinweis:** Das Tool wird in `/usr/local/bin` installiert und ist damit global verfügbar.

