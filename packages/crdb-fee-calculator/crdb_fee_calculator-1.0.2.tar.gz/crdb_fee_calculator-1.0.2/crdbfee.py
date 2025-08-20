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
            self.df["__details_lc"] = self.df["Details"].astype(str).str.lower()
            
            # Detect currency
            self.currency = self.detect_currency(self.df)
            
            return True
            
        except Exception as e:
            print(f"Error loading file: {e}", file=sys.stderr)
            return False
    
    def calculate_fees_and_vat(self) -> Tuple[float, float]:
        """Calculates the total amounts for fees and VAT."""
        if self.df is None:
            return 0.0, 0.0
        
        # Filter VAT and fees
        vat_df = self.df[self.df["__details_lc"].str.contains("vat", na=False)]
        fees_df = self.df[
            self.df["__details_lc"].str.contains(self.FEE_KEYWORDS, na=False) & 
            ~self.df["__details_lc"].str.contains("vat", na=False)
        ]
        
        # Calculate sums
        fees_total = fees_df["Debit"].sum(skipna=True) or 0.0
        vat_total = vat_df["Debit"].sum(skipna=True) or 0.0
        
        return fees_total, vat_total
    
    def print_results(self, fees_total: float, vat_total: float):
        """Prints the results in a nice format."""
        total_amount = fees_total + vat_total
        
        print("┌─────────────────────────────────────────┐")
        print("│           CRDB Fee Calculator           │")
        print("├─────────────────────────────────────────┤")
        print(f"│ 📊 Fees/Charges: {fees_total:>8.2f} {self.currency}")
        print(f"│ 🏛️  VAT Total:    {vat_total:>8.2f} {self.currency}")
        print("├─────────────────────────────────────────┤")
        print(f"│ 💰 Total Amount:  {total_amount:>8.2f} {self.currency}")
        print("└─────────────────────────────────────────┘")
        print(f"💱 Detected currency: {self.currency}")


def main():
    """Main function for the command line tool."""
    parser = argparse.ArgumentParser(
        description="CRDB Fee Calculator - Calculates fees and VAT from account statements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  crdbfee statement.xlsx
  crdbfee /path/to/statement.xlsx
  crdbfee --help
        """
    )
    
    parser.add_argument(
        "file",
        help="Path to Excel file with account statement"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="CRDB Fee Calculator v1.0.0"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    # Check if it's an Excel file
    if not args.file.lower().endswith(('.xlsx', '.xls')):
        print(f"Error: File '{args.file}' is not an Excel file.", file=sys.stderr)
        sys.exit(1)
    
    # Calculate fees and VAT
    calculator = CRDBFeeCalculator(args.file)
    
    if not calculator.load_data():
        sys.exit(1)
    
    fees_total, vat_total = calculator.calculate_fees_and_vat()
    calculator.print_results(fees_total, vat_total)


if __name__ == "__main__":
    main()

