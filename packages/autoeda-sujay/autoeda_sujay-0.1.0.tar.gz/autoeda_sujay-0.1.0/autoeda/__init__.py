"""
AutoEDA - Automated Exploratory Data Analysis Library
One function call for comprehensive data analysis
"""

from .core import analyze, AutoEDAReport

__version__ = "0.1.0"
__author__ = "Your Name"

# Make the main function available at package level
__all__ = ['analyze', 'AutoEDAReport']