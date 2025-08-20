#!/usr/bin/env python3
"""
Setup script for CRDB Fee Calculator
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="crdb-fee-calculator",
    version="1.0.1",
    author="Leon Kasdorf",
    author_email="crdbfee@dropalias.com",
    description="A command line tool for calculating fees and VAT from CRDB account statements in Excel format",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/crdb_fee_calculator",  # Bitte deine GitHub-URL eintragen
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "crdbfee=crdbfee:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="crdb, fees, vat, excel, banking, tanzania, accounting",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/crdb_fee_calculator/issues",
        "Source": "https://github.com/yourusername/crdb_fee_calculator",
        "Documentation": "https://github.com/yourusername/crdb_fee_calculator#readme",
    },
)
