"""
University-specific implementations.

This package contains concrete implementations of the UniversityProvider
interface for each supported university.
"""

from .base import BaseUniversityProvider
from .uottawa import UOttawaProvider
from .carleton import CarletonProvider

__all__ = [
    "BaseUniversityProvider",
    "UOttawaProvider",
    "CarletonProvider",
]
