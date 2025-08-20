"""
CRDB Fee Calculator Package

A command line tool for calculating fees and VAT from CRDB account statements in Excel format.
"""

__version__ = "1.0.1"
__author__ = "Leon Kasdorf"
__email__ = "crdbfee@dropalias.com"

from .calculator import CRDBFeeCalculator

__all__ = ["CRDBFeeCalculator"]
