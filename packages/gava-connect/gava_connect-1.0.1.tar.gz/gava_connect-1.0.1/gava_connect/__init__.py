"""
GavaConnect - Kenya Revenue Authority API Client

A Python package for simplified access to Kenya Revenue Authority (KRA) API.
"""

from .kra_client import KRAGavaConnect, TaxObligationType, KRAMethodsProvider

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "KRAGavaConnect",
    "TaxObligationType", 
    "KRAMethodsProvider"
]
