"""
Warnings Configuration Module

Centralized configuration for warnings suppression across PyMBO.
Provides consistent warning handling for better user experience.
"""

import warnings


def configure_warnings():
    """Configure standard warnings suppression for PyMBO."""
    # Core ML/optimization library warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="botorch")
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="botorch")
    warnings.filterwarnings("ignore", category=UserWarning, module="gpytorch")
    warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
    warnings.filterwarnings("ignore", category=UserWarning, module="pymoo")
    
    # General warnings that clutter output
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)


# Configure warnings on import
configure_warnings()