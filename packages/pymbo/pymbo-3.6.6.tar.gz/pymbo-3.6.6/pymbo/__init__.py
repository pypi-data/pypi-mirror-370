"""
PyMBO - Python Multi-objective Bayesian Optimization

A comprehensive multi-objective Bayesian optimization framework with advanced visualization
and screening capabilities.

Modules:
    core: Core optimization algorithms and controllers
    gui: Graphical user interface components
    utils: Utility functions for plotting, reporting, and scientific calculations
    screening: SGLBO screening optimization module
"""

__version__ = "3.6.6"
__author__ = "Jakub Jagielski"

# Core imports for easy access
from .core.optimizer import EnhancedMultiObjectiveOptimizer
from .core.controller import SimpleController

__all__ = [
    "EnhancedMultiObjectiveOptimizer",
    "SimpleController",
]