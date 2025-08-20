#!/usr/bin/env python3
"""
NLTK data setup utilities for simpleKG package.
"""

import os
import nltk
from pathlib import Path


def ensure_nltk_data():
    """
    Ensure required NLTK data is downloaded.
    Downloads punkt_tab if not already present.
    """
    try:
        # Try to find punkt_tab data
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        # If not found, download it
        print("Downloading NLTK punkt_tab data...")
        try:
            nltk.download('punkt_tab', quiet=True)
            print("NLTK punkt_tab data downloaded successfully.")
        except Exception as e:
            print(f"Warning: Failed to download NLTK punkt_tab data: {e}")
            print("You may need to run: nltk.download('punkt_tab') manually")


def check_nltk_data():
    """
    Check if required NLTK data is available.
    Returns True if available, False otherwise.
    """
    try:
        nltk.data.find('tokenizers/punkt_tab')
        return True
    except LookupError:
        return False


# Auto-download on import (optional)
def auto_setup():
    """
    Automatically set up NLTK data when imported.
    """
    if not check_nltk_data():
        ensure_nltk_data()


if __name__ == "__main__":
    ensure_nltk_data()
