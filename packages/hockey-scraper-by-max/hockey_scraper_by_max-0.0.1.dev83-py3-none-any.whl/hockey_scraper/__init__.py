"""
Hockey Scraper - A comprehensive Python package for scraping hockey data.

This package provides modern, efficient tools for collecting NHL data with
built-in ESPN integration for enhanced data quality and coverage.
"""

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development installs
    __version__ = "0.1.0-dev"

__author__ = "Max Tixador"
__email__ = "maxtixador@gmail.com"

# Main package imports
from . import src

__all__ = ["src", "__version__", "__author__", "__email__"]
