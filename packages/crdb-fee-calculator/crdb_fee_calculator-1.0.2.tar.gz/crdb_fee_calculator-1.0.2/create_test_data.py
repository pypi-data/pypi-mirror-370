#!/usr/bin/env python3
"""
Erstellt eine Test-Excel-Datei für den CRDB Fee Calculator
"""

import pandas as pd
import numpy as np

def create_test_statement():
    """Erstellt eine Test-Kontoauszug-Datei."""
    
    # Beispieldaten
    data = {
        'Posting Date': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
        'Details': [
            'Bank Transfer Fee',
            'VAT on Commission',
            'Account Maintenance Charge',
            'Wire Transfer Fee',
            'VAT on Bank Charges'
        ],
        'Value Date': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
        'Debit': [25.00, 5.00, 15.00, 30.00, 6.00],
        'Credit': [0, 0, 0, 0, 0],
        'Book Balance': [1000.00, 995.00, 980.00, 950.00, 944.00]
    }
    
    # DataFrame erstellen
    df = pd.DataFrame(data)
    
    # In Excel-Datei speichern
    filename = 'test_statement.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Testdatei '{filename}' wurde erstellt!")
    print(f"📊 Enthält {len(data['Posting Date'])} Transaktionen")
    print(f"💰 Erwartete Fees: {sum(data['Debit'][::2])} (ohne VAT)")
    print(f"🏛️  Erwarteter VAT: {sum(data['Debit'][1::2])}")
    print(f"💱 Währung: USD (Standard)")
    print(f"")
    print(f"Sie können das Tool jetzt testen mit:")
    print(f"  crdbfee {filename}")


def create_test_statement_tzs():
    """Erstellt eine Test-Kontoauszug-Datei mit TZS Währung."""
    
    # Beispieldaten in TZS
    data = {
        'Posting Date': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
        'Details': [
            'Bank Transfer Fee TZS',
            'VAT on Commission TZS',
            'Account Maintenance Charge TZS',
            'Wire Transfer Fee TZS',
            'VAT on Bank Charges TZS'
        ],
        'Value Date': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
        'Debit': [25000.00, 5000.00, 15000.00, 30000.00, 6000.00],
        'Credit': [0, 0, 0, 0, 0],
        'Book Balance': [1000000.00, 995000.00, 980000.00, 950000.00, 944000.00]
    }
    
    # DataFrame erstellen
    df = pd.DataFrame(data)
    
    # In Excel-Datei speichern
    filename = 'test_statement_tzs.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Testdatei '{filename}' (TZS) wurde erstellt!")
    print(f"📊 Enthält {len(data['Posting Date'])} Transaktionen")
    print(f"💰 Erwartete Fees: {sum(data['Debit'][::2]):,} TZS (ohne VAT)")
    print(f"🏛️  Erwarteter VAT: {sum(data['Debit'][1::2]):,} TZS")
    print(f"💱 Währung: TZS (Tanzania Shilling)")
    print(f"")
    print(f"Sie können das Tool jetzt testen mit:")
    print(f"  crdbfee {filename}")


def create_test_statement_usd():
    """Erstellt eine Test-Kontoauszug-Datei mit USD Währung."""
    
    # Beispieldaten in USD
    data = {
        'Posting Date': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
        'Details': [
            'Bank Transfer Fee USD',
            'VAT on Commission USD',
            'Account Maintenance Charge USD',
            'Wire Transfer Fee USD',
            'VAT on Bank Charges USD'
        ],
        'Value Date': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
        'Debit': [25.00, 5.00, 15.00, 30.00, 6.00],
        'Credit': [0, 0, 0, 0, 0],
        'Book Balance': [1000.00, 995.00, 980.00, 950.00, 944.00]
    }
    
    # DataFrame erstellen
    df = pd.DataFrame(data)
    
    # In Excel-Datei speichern
    filename = 'test_statement_usd.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"✅ Testdatei '{filename}' (USD) wurde erstellt!")
    print(f"📊 Enthält {len(data['Posting Date'])} Transaktionen")
    print(f"💰 Erwartete Fees: {sum(data['Debit'][::2])} USD (ohne VAT)")
    print(f"🏛️  Erwarteter VAT: {sum(data['Debit'][1::2])} USD")
    print(f"💱 Währung: USD (US Dollar)")
    print(f"")
    print(f"Sie können das Tool jetzt testen mit:")
    print(f"  crdbfee {filename}")

if __name__ == "__main__":
    print("🧪 CRDB Fee Calculator - Testdateien erstellen")
    print("=" * 50)
    print()
    
    # Alle Testdateien erstellen
    create_test_statement()
    print()
    create_test_statement_usd()
    print()
    create_test_statement_tzs()
    print()
    
    print("🎉 Alle Testdateien wurden erstellt!")
    print()
    print("📋 Verfügbare Testdateien:")
    print("  • test_statement.xlsx      (Standard)")
    print("  • test_statement_usd.xlsx  (USD)")
    print("  • test_statement_tzs.xlsx  (TZS)")
    print()
    print("🧪 Testen Sie das Tool mit verschiedenen Währungen:")
    print("  crdbfee test_statement.xlsx")
    print("  crdbfee test_statement_usd.xlsx")
    print("  crdbfee test_statement_tzs.xlsx")

