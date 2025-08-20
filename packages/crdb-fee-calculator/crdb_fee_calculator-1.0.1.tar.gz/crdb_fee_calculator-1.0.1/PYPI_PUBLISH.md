# 🚀 PyPI-Veröffentlichung - CRDB Fee Calculator

Diese Anleitung erklärt, wie du das CRDB Fee Calculator Tool bei PyPI veröffentlichst.

## 📋 Voraussetzungen

1. **PyPI-Account erstellen:**
   - Gehe zu [pypi.org](https://pypi.org) und erstelle einen Account
   - Aktiviere Two-Factor Authentication (2FA)

2. **TestPyPI-Account erstellen:**
   - Gehe zu [test.pypi.org](https://test.pypi.org) und erstelle einen Account
   - Verwende den gleichen Benutzernamen wie bei PyPI

## 🔧 Lokale Entwicklungsumgebung einrichten

```bash
# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Entwicklungsabhängigkeiten installieren
pip install -r requirements-dev.txt
```

## 📦 Paket lokal testen

```bash
# Paket bauen
python -m build

# Paket installieren (zum Testen)
pip install dist/*.whl

# Testen ob es funktioniert
crdbfee --help
```

## 🧪 Bei TestPyPI testen

```bash
# Paket zu TestPyPI hochladen
python -m twine upload --repository testpypi dist/*

# Paket von TestPyPI installieren
pip install --index-url https://test.pypi.org/simple/ crdb-fee-calculator
```

## 🚀 Bei PyPI veröffentlichen

### 1. **setup.py anpassen:**
- GitHub-URL anpassen (falls nötig)
- Version anpassen (falls nötig)

### 2. **pyproject.toml anpassen:**
- GitHub-URL anpassen (falls nötig)

### 3. **Paket bauen und hochladen:**
```bash
# Alte Builds löschen
rm -rf dist/ build/ *.egg-info/

# Paket bauen
python -m build

# Paket zu PyPI hochladen
python -m twine upload dist/*
```

## 📝 Wichtige Hinweise

### **Vor der Veröffentlichung:**
- [ ] Alle URLs in setup.py und pyproject.toml anpassen
- [ ] Version überprüfen
- [ ] README.md auf Vollständigkeit prüfen
- [ ] LICENSE-Datei vorhanden
- [ ] Paket lokal testen

### **Nach der Veröffentlichung:**
- [ ] PyPI-Seite überprüfen
- [ ] Installation testen: `pip install crdb-fee-calculator`
- [ ] Funktionalität testen
- [ ] GitHub-Release erstellen

## 🔄 Updates veröffentlichen

1. **Version erhöhen** in:
   - `setup.py`
   - `pyproject.toml`
   - `crdbfee/__init__.py`

2. **Paket neu bauen und hochladen:**
```bash
rm -rf dist/ build/ *.egg-info/
python -m build
python -m twine upload dist/*
```

## 🐛 Häufige Probleme

### **"File already exists"**
- Version in allen Dateien erhöhen
- Alte Builds löschen

### **"Invalid distribution"**
- MANIFEST.in überprüfen
- Alle notwendigen Dateien sind enthalten

### **"Authentication failed"**
- PyPI-Credentials überprüfen
- 2FA korrekt eingerichtet

## 📚 Nützliche Links

- [PyPI Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Authority](https://www.pypa.io/)

## 🎯 Nächste Schritte

Nach der Veröffentlichung kannst du:
1. **GitHub Actions** für automatische Veröffentlichung einrichten
2. **Dokumentation** bei ReadTheDocs hosten
3. **Code-Qualität** mit GitHub Actions überwachen
4. **Community** aufbauen und Issues bearbeiten

Viel Erfolg bei der Veröffentlichung! 🚀
