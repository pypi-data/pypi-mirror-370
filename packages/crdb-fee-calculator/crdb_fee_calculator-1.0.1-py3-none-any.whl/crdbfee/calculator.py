#!/usr/bin/env python3
"""
CRDB Fee Calculator - Command line tool for calculating fees and VAT
from account statements in Excel format.
"""

import pandas as pd
import argparse
import sys
import os
from pathlib import Path
from typing import Optional, Tuple


class CRDBFeeCalculator:
    """Main class for calculating fees and VAT from CRDB account statements."""
    
    FEE_KEYWORDS = "charge|commission|fee|levy|fund transfer"
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.currency = "USD"  # Default currency
        
    def find_header_row(self, df: pd.DataFrame) -> int:
        """Finds the row with column headers."""
        for i, row in df.iterrows():
            if any(isinstance(cell, str) and "date" in cell.lower() for cell in row):
                return i
        return 0
    
    def parse_amount(self, val) -> Optional[float]:
        """Parses amounts and removes thousand separators."""
        if pd.isna(val):
            return None
        val = str(val).strip()
        if val in ["", "nan", "None"]:
            return None
        # Remove thousand separators
        val = val.replace(",", "")
        try:
            return float(val)
        except:
            return None
    
    def detect_currency(self, df: pd.DataFrame) -> str:
        """Detects the currency from the data."""
        # Search for currency in column names and first rows
        currency_patterns = {
            'USD': ['usd', 'dollar', '$', 'us'],
            'TZS': ['tzs', 'shilling', 'tsh', 'tz']
        }
        
        # Search in column names
        for col in df.columns:
            col_lower = str(col).lower()
            for currency, patterns in currency_patterns.items():
                if any(pattern in col_lower for pattern in patterns):
                    return currency
        
        # Search in first data rows
        for _, row in df.head(10).iterrows():
            for cell in row:
                if pd.notna(cell):
                    cell_str = str(cell).lower()
                    for currency, patterns in currency_patterns.items():
                        if any(pattern in cell_str for pattern in patterns):
                            return currency
        
        # Search for specific currency symbols in the data
        for _, row in df.head(20).iterrows():
            for cell in row:
                if pd.notna(cell):
                    cell_str = str(cell)
                    if '$' in cell_str:
                        return 'USD'
                    elif any(symbol in cell_str for symbol in ['TSH', 'TZS', 'Sh']):
                        return 'TZS'
        
        # Fallback: Default currency
        return "USD"
    
    def load_data(self) -> bool:
        """Loads and prepares the Excel file."""
        try:
            # Load file
            df0 = pd.read_excel(self.file_path, dtype=str)
            header_idx = self.find_header_row(df0)
            
            self.df = pd.read_excel(self.file_path, skiprows=header_idx, dtype=str)
            
            # First data row as header
            self.df.columns = self.df.iloc[0]
            self.df = self.df.drop(0).reset_index(drop=True)
            
            # Standard column names (as in CRDB exports)
            self.df.columns = ["Posting Date", "Details", "Value Date", "Debit", "Credit", "Book Balance"]
            
            # Parse amounts
            self.df["Debit"] = self.df["Debit"].apply(self.parse_amount)
            self.df["Credit"] = self.df["Credit"].apply(self.parse_amount)
            self.df["Book Balance"] = self.df["Book Balance"].apply(self.parse_amount)
            
            # Detect currency
            self.currency = self.detect_currency(self.df)
            
            return True
        except Exception as e:
            print(f"❌ Fehler beim Laden der Datei: {e}")
            return False
    
    def calculate_fees(self) -> Tuple[float, float]:
        """Calculates total fees and VAT."""
        if self.df is None:
            return 0.0, 0.0
        
        total_fees = 0.0
        total_vat = 0.0
        
        for _, row in self.df.iterrows():
            details = str(row["Details"]).lower()
            
            # Check if this is a fee/charge
            if any(keyword in details for keyword in self.FEE_KEYWORDS.split("|")):
                amount = row["Debit"] or row["Credit"] or 0.0
                if amount > 0:
                    total_fees += amount
            
            # Check if this is VAT
            if "vat" in details:
                amount = row["Debit"] or row["Credit"] or 0.0
                if amount > 0:
                    total_vat += amount
        
        return total_fees, total_vat
    
    def format_amount(self, amount: float) -> str:
        """Formats amount with proper currency formatting."""
        if self.currency == "TZS":
            return f"{amount:,.2f} TZS"
        else:
            return f"{amount:,.2f} USD"
    
    def print_results(self, fees: float, vat: float):
        """Prints formatted results."""
        total = fees + vat
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    CRDB Fee Calculator                      ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║  📊  Fees/Charges:          {self.format_amount(fees):>15} ║")
        print(f"║  🏛️   VAT Total:             {self.format_amount(vat):>15} ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║  💰  Total Amount:          {self.format_amount(total):>15} ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"💱 Detected currency: {self.currency}")
    
    def run(self) -> bool:
        """Main execution method."""
        if not self.load_data():
            return False
        
        fees, vat = self.calculate_fees()
        self.print_results(fees, vat)
        return True


def main():
    """Main entry point for command line usage."""
    parser = argparse.ArgumentParser(
        description="CRDB Fee Calculator - Calculate fees and VAT from account statements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  crdbfee statement.xlsx
  crdbfee --help
  crdbfee --version
        """
    )
    
    parser.add_argument(
        "file",
        help="Excel file (.xlsx or .xls) containing CRDB account statement"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="CRDB Fee Calculator v1.0.1"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"❌ Datei nicht gefunden: {args.file}")
        sys.exit(1)
    
    # Check file extension
    if not args.file.lower().endswith(('.xlsx', '.xls')):
        print("❌ Keine Excel-Datei. Bitte verwenden Sie .xlsx oder .xls Dateien.")
        sys.exit(1)
    
    # Create calculator and run
    calculator = CRDBFeeCalculator(args.file)
    if not calculator.run():
        sys.exit(1)


if __name__ == "__main__":
    main()
