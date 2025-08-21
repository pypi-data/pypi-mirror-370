# src/kertash/__init__.py
"""
Kertash - Simple hash analyzer & cracker

Crack the hash using wordlists indonesian and rockyou.txt
"""

from .core import crack, crack_file, analyze, analyze_file

__all__ = ["crack", "crack_file", "analyze", "analyze_file"]
__version__ = "0.1.1"
