"""
Neutrophils Classifier Application - Frontend GUI Package

This package contains the PyQt5-based frontend application that consumes
the neutrophils-core library for scientific processing and AI model operations.
"""

def main():
    """Entry point for the application when installed via setup.py"""
    from .main import main as app_main
    app_main()