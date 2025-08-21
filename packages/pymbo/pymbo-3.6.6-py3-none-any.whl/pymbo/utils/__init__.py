"""
Utilities Module

Contains plotting, reporting, and scientific utility functions.
"""

from .plotting import SimplePlotManager
from .warnings_config import configure_warnings

# Configure warnings on import
configure_warnings()

__all__ = [
    "SimplePlotManager",
    "configure_warnings"
]