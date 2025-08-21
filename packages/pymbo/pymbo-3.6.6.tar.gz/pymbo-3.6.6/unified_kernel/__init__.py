"""
Unified Exponential Kernel for Mixed Variables

A GPyTorch-compatible kernel implementation that handles continuous, discrete, 
and categorical variables in a principled way for Bayesian optimization.

Author: Claude Code Assistant
Created: 2025-08-18
"""

from .kernels.unified_exponential import UnifiedExponentialKernel
from .utils.parameter_detection import ParameterTypeDetector, is_mixed_variable_problem, get_variable_type_summary
from .utils.transforms import ParameterTransformer

__version__ = "0.1.0"
__all__ = [
    "UnifiedExponentialKernel",
    "ParameterTypeDetector", 
    "ParameterTransformer",
    "is_mixed_variable_problem",
    "get_variable_type_summary"
]