"""
SGLBO Screening Module for Bayesian Optimization

This module implements Stochastic Gradient Line Bayesian Optimization (SGLBO)
for efficient parameter space screening before detailed optimization.

Key Components:
- ScreeningOptimizer: Main SGLBO implementation
- ParameterHandler: Parameter validation and transformation
- DesignSpaceGenerator: CCD design space generation around optima
- ScreeningResults: Results storage and analysis

Author: Screening Module for Multi-Objective Optimization Laboratory
Version: 3.6.6
"""

from .screening_optimizer import ScreeningOptimizer
from .parameter_handler import ParameterHandler
from .design_space_generator import DesignSpaceGenerator
from .screening_results import ScreeningResults

__version__ = "3.6.6"
__all__ = [
    "ScreeningOptimizer",
    "ParameterHandler", 
    "DesignSpaceGenerator",
    "ScreeningResults"
]