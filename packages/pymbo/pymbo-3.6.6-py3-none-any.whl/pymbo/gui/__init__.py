"""
GUI Module

Contains all graphical user interface components.
"""

from .gui import SimpleOptimizerApp

# Optional screening windows (graceful imports)
try:
    from .interactive_screening_window import show_interactive_screening_window
    from .screening_execution_window import ScreeningExecutionWindow
    __all__ = [
        "SimpleOptimizerApp",
        "show_interactive_screening_window", 
        "ScreeningExecutionWindow"
    ]
except ImportError:
    __all__ = ["SimpleOptimizerApp"]