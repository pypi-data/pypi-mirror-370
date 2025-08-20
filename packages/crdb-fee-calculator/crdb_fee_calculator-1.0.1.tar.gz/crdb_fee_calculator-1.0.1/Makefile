# CRDB Fee Calculator Makefile
# Verwendung: make install, make uninstall, make test

.PHONY: install uninstall test clean help

# Standardziel
all: help

# Installation
install:
	@echo "🚀 Installiere CRDB Fee Calculator..."
	@chmod +x install.sh
	@./install.sh

# Deinstallation
uninstall:
	@echo "🗑️  Deinstalliere CRDB Fee Calculator..."
	@chmod +x uninstall.sh
	@./uninstall.sh

# Test des Tools (falls Testdateien vorhanden sind)
test:
	@echo "🧪 Teste CRDB Fee Calculator..."
	@if [ -f "test_statement.xlsx" ]; then \
		echo "Teste mit test_statement.xlsx (Standard)..."; \
		crdbfee test_statement.xlsx; \
		echo ""; \
	else \
		echo "Keine Testdatei gefunden. Erstellen Sie Testdateien mit: python3 create_test_data.py"; \
	fi
	@if [ -f "test_statement_usd.xlsx" ]; then \
		echo "Teste mit test_statement_usd.xlsx (USD)..."; \
		crdbfee test_statement_usd.xlsx; \
		echo ""; \
	fi
	@if [ -f "test_statement_tzs.xlsx" ]; then \
		echo "Teste mit test_statement_tzs.xlsx (TZS)..."; \
		crdbfee test_statement_tzs.xlsx; \
	fi

# Testdateien erstellen
testdata:
	@echo "📊 Erstelle Testdateien..."
	@python3 create_test_data.py

# Aufräumen
clean:
	@echo "🧹 Räume auf..."
	@rm -f *.pyc
	@rm -rf __pycache__

# Hilfe anzeigen
help:
	@echo "CRDB Fee Calculator - Makefile"
	@echo ""
	@echo "Verfügbare Ziele:"
	@echo "  install    - Installiert das Tool"
	@echo "  uninstall  - Entfernt das Tool"
	@echo "  test       - Testet das Tool (falls Testdateien vorhanden)"
	@echo "  testdata   - Erstellt Testdateien für verschiedene Währungen"
	@echo "  clean      - Räumt temporäre Dateien auf"
	@echo "  help       - Zeigt diese Hilfe an"
	@echo ""
	@echo "Beispiele:"
	@echo "  make install"
	@echo "  make testdata"
	@echo "  make test"
	@echo "  make uninstall"

