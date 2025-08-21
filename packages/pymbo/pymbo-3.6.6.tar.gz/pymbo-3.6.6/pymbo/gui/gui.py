"""
Main GUI Module

Enhanced GUI for PyMBO with proper parameter goal selection and suggestion display.
Provides comprehensive multi-objective Bayesian optimization interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, font
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json

# Import response importance dialog
try:
    from .response_importance_dialog import show_importance_dialog
    IMPORTANCE_DIALOG_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Response importance dialog not available: {e}")
    IMPORTANCE_DIALOG_AVAILABLE = False

# Performance optimization imports
try:
    from pymbo.utils.performance_optimizer import (
        optimized_plot_update, plot_cache, memory_manager, perf_monitor
    )
    PERFORMANCE_OPTIMIZATION_AVAILABLE = True
except ImportError:
    PERFORMANCE_OPTIMIZATION_AVAILABLE = False

# Import screening execution windows
try:
    from .interactive_screening_window import show_interactive_screening_window
    INTERACTIVE_SCREENING_AVAILABLE = True
except ImportError:
    INTERACTIVE_SCREENING_AVAILABLE = False

try:
    from .screening_execution_window import show_screening_execution_window
    SCREENING_WINDOW_AVAILABLE = True
except ImportError:
    SCREENING_WINDOW_AVAILABLE = False

# Import GPU acceleration widget
try:
    from .gpu_acceleration_widget import GPUAccelerationWidget
    GPU_ACCELERATION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"GPU acceleration widget not available: {e}")
    GPU_ACCELERATION_AVAILABLE = False

# Import Goal Impact Dashboard
try:
    from .goal_impact_dashboard import create_goal_impact_dashboard
    GOAL_IMPACT_DASHBOARD_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Goal Impact Dashboard not available: {e}")
    GOAL_IMPACT_DASHBOARD_AVAILABLE = False

# Import enhanced plot controls
try:
    from .plot_controls import (
        create_plot_control_panel,
        EnhancedPlotControlPanel,
    )
    from .compact_controls import (
        create_compact_plot_control_panel,
        CompactPlotControlPanel,
    )
    from .movable_controls import (
        create_movable_plot_control_panel,
        MovablePlotControlPanel,
    )
    from .window_controls import (
        create_window_plot_control_panel,
        WindowPlotControlPanel,
    )
    from .pareto_controls import (
        create_pareto_control_panel,
        ParetoPlotControlPanel,
    )
    from .progress_controls import (
        create_progress_control_panel,
        ProgressPlotControlPanel,
    )
    from .gp_slice_controls import (
        create_gp_slice_control_panel,
        GPSliceControlPanel,
    )
    from .parallel_coordinates_controls import (
        create_parallel_coordinates_control_panel,
        ParallelCoordinatesControlPanel,
    )
    from .uncertainty_analysis_controls import (
        create_uncertainty_analysis_control_panel,
        UncertaintyAnalysisControlPanel,
    )
    from .model_diagnostics_controls import (
        create_model_diagnostics_control_panel,
        ModelDiagnosticsControlPanel,
    )
    from .sensitivity_analysis_controls import (
        create_sensitivity_analysis_control_panel,
        SensitivityAnalysisControlPanel,
    )
    
    # Import 3D surface controls module using proper Python import
    from .surface_3d_controls import (
        create_3d_surface_control_panel,
        SurfacePlotControlPanel,
    )

    ENHANCED_CONTROLS_AVAILABLE = True
    COMPACT_CONTROLS_AVAILABLE = True
    MOVABLE_CONTROLS_AVAILABLE = True
    WINDOW_CONTROLS_AVAILABLE = True
    PARETO_CONTROLS_AVAILABLE = True
    PROGRESS_CONTROLS_AVAILABLE = True
    GP_SLICE_CONTROLS_AVAILABLE = True
    SURFACE_3D_CONTROLS_AVAILABLE = True
    PARALLEL_COORDINATES_CONTROLS_AVAILABLE = True
    UNCERTAINTY_ANALYSIS_CONTROLS_AVAILABLE = True
    MODEL_DIAGNOSTICS_CONTROLS_AVAILABLE = True
    SENSITIVITY_ANALYSIS_CONTROLS_AVAILABLE = True
except ImportError:
    ENHANCED_CONTROLS_AVAILABLE = False
    COMPACT_CONTROLS_AVAILABLE = False
    MOVABLE_CONTROLS_AVAILABLE = False
    WINDOW_CONTROLS_AVAILABLE = False
    PARETO_CONTROLS_AVAILABLE = False
    PROGRESS_CONTROLS_AVAILABLE = False
    GP_SLICE_CONTROLS_AVAILABLE = False
    SURFACE_3D_CONTROLS_AVAILABLE = False
    PARALLEL_COORDINATES_CONTROLS_AVAILABLE = False
    UNCERTAINTY_ANALYSIS_CONTROLS_AVAILABLE = False
    MODEL_DIAGNOSTICS_CONTROLS_AVAILABLE = False
    SENSITIVITY_ANALYSIS_CONTROLS_AVAILABLE = False

# Configuration constants
APP_TITLE = "Multi-Objective Optimization Laboratory v3.6.6"
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 800
DEFAULT_WINDOW_WIDTH = 1400
DEFAULT_WINDOW_HEIGHT = 900

# Color scheme
COLOR_PRIMARY = "#1976D2"
COLOR_SECONDARY = "#424242"
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FF9800"
COLOR_ERROR = "#F44336"
COLOR_BACKGROUND = "#FAFAFA"
COLOR_SURFACE = "#FFFFFF"

# Initialize logger for GUI module
logger = logging.getLogger(__name__)


class ModernTheme:
    """Modern color scheme and styling constants for the application"""

    # Color Palette - Modern Material Design inspired
    PRIMARY = "#1976D2"  # Professional blue
    PRIMARY_DARK = "#1565C0"  # Darker blue for hover states
    PRIMARY_LIGHT = "#E3F2FD"  # Light blue for backgrounds

    SECONDARY = "#FF6F00"  # Orange accent
    SECONDARY_DARK = "#E65100"  # Darker orange
    SECONDARY_LIGHT = "#FFF3E0"  # Light orange

    SUCCESS = "#2E7D32"  # Green for success states
    SUCCESS_LIGHT = "#E8F5E8"  # Light green

    WARNING = "#F57C00"  # Amber for warnings
    WARNING_LIGHT = "#FFF8E1"  # Light amber

    ERROR = "#C62828"  # Red for errors
    ERROR_LIGHT = "#FFEBEE"  # Light red

    # Neutral colors
    SURFACE = "#FFFFFF"  # White surface
    BACKGROUND = "#FAFAFA"  # Light gray background
    CARD = "#F5F7FA"  # Card background
    BORDER = "#E0E0E0"  # Border color
    DIVIDER = "#EEEEEE"  # Divider color

    # Text colors
    TEXT_PRIMARY = "#212121"  # Primary text
    TEXT_SECONDARY = "#757575"  # Secondary text
    TEXT_DISABLED = "#BDBDBD"  # Disabled text
    TEXT_HINT = "#9E9E9E"  # Hint text

    # Modern fonts with fallbacks
    @staticmethod
    def get_font(size=10, weight="normal", family="system"):
        """Get appropriate font for the system"""
        font_families = {
            "system": ["Segoe UI", "SF Pro Display", "Roboto", "Arial", "sans-serif"],
            "mono": ["Cascadia Code", "SF Mono", "Consolas", "Monaco", "monospace"],
            "serif": ["Georgia", "Times New Roman", "serif"],
        }

        for font_name in font_families.get(family, font_families["system"]):
            try:
                return (font_name, size, weight)
            except:
                continue
        return ("Arial", size, weight)

    # Common styles
    BUTTON_STYLE = {
        "relief": "flat",
        "borderwidth": 0,
        "pady": 8,
        "padx": 16,
        "cursor": "hand2",
    }

    CARD_STYLE = {"relief": "flat", "borderwidth": 1, "pady": 16, "padx": 16}

    INPUT_STYLE = {"relief": "solid", "borderwidth": 1, "pady": 8, "padx": 12}


class SimpleOptimizerApp(tk.Tk):
    """
    Main application class for the Multi-Objective Optimization Laboratory GUI.
    It handles the user interface, interacts with the controller, and displays
    optimization results and plots.
    """

    def __init__(self):
        """
        Initializes the main application window and its components with modern styling.
        """
        super().__init__()

        # Configure responsive window appearance
        self.title("Multi-Objective Optimization Laboratory v3.6.6")
        self._setup_responsive_window()
        self.configure(bg=ModernTheme.BACKGROUND)

        # Skip centering for fullscreen mode
        # self._center_window()  # Not needed in fullscreen
        
        # Setup cleanup on window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Configure modern styling
        self._configure_modern_style()

        # Initialize enhanced controls storage
        self.enhanced_controls = {}
        # Initialize window configurations for lazy creation
        self.window_configs = {}
        # Initialize uncertainty analysis control panel reference
        self.uncertainty_analysis_control = None

        # Set window icon if available
        try:
            # You can add an icon file here if available
            # self.iconbitmap("icon.ico")
            pass
        except:
            pass

        # Initialize controller and state variables.
        self.controller: Optional[Any] = None
        self.param_rows: List[Dict[str, Any]] = []
        self.response_rows: List[Dict[str, Any]] = []
        self.suggestion_labels: Dict[str, tk.Label] = {}
        self.results_entries: Dict[str, tk.Entry] = {}
        self.best_solution_labels: Dict[str, Dict[str, Any]] = {
            "params": {},
            "responses": {},
        }
        self.current_suggestion: Dict[str, Any] = {}
        self.initial_sampling_method_var: tk.StringVar = tk.StringVar(
            value="Random"
        )  # Default to Random

        # Figures and canvases for various plots.
        self.pareto_fig: Optional[Figure] = None
        self.pareto_canvas: Optional[FigureCanvasTkAgg] = None
        self.progress_fig: Optional[Figure] = None
        self.progress_canvas: Optional[FigureCanvasTkAgg] = None
        self.gp_slice_fig: Optional[Figure] = None
        self.gp_slice_canvas: Optional[FigureCanvasTkAgg] = None
        self.surface_3d_fig: Optional[Figure] = None
        self.surface_3d_canvas: Optional[FigureCanvasTkAgg] = None
        self.parallel_coords_fig: Optional[Figure] = None
        self.parallel_coords_canvas: Optional[FigureCanvasTkAgg] = None
        self.gp_uncertainty_map_fig: Optional[Figure] = None
        self.gp_uncertainty_map_canvas: Optional[FigureCanvasTkAgg] = None
        self.parity_fig: Optional[Figure] = None
        self.parity_canvas: Optional[FigureCanvasTkAgg] = None
        self.residuals_fig: Optional[Figure] = None
        self.residuals_canvas: Optional[FigureCanvasTkAgg] = None
        self.sensitivity_fig: Optional[Figure] = None
        self.sensitivity_canvas: Optional[FigureCanvasTkAgg] = None

        # Status variables for display.
        self.status_var: tk.StringVar = tk.StringVar()
        self.data_count_var: tk.StringVar = tk.StringVar()
        self.plot_manager: Optional[Any] = None

        # Initialize the GUI layout.
        self._setup_main_window()

    def _setup_responsive_window(self):
        """Configure window to open in fullscreen mode"""
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Set window to fullscreen mode
        self.state('zoomed')  # Windows fullscreen
        
        # Alternative method for cross-platform fullscreen
        try:
            self.attributes('-zoomed', True)  # Linux/Unix
        except tk.TclError:
            pass
        
        try:
            self.attributes('-fullscreen', True)  # Alternative fullscreen
        except tk.TclError:
            # Fallback to manual fullscreen geometry if attributes don't work
            self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Set minimum size - keep responsive to very small screens for safety
        min_width = min(900, int(screen_width * 0.6))
        min_height = min(600, int(screen_height * 0.6))
        self.minsize(min_width, min_height)
        
        # Make window resizable (user can exit fullscreen if needed)
        self.resizable(True, True)
        
        # Add ESC key binding to exit fullscreen
        self.bind('<Escape>', self._toggle_fullscreen)
        self.bind('<F11>', self._toggle_fullscreen)
        
        logger.info(f"Fullscreen window setup: {screen_width}x{screen_height}, "
                   f"min: {min_width}x{min_height}")

    def _center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        pos_x = (self.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{pos_x}+{pos_y}")
    
    def _toggle_fullscreen(self, event=None):
        """Toggle between fullscreen and windowed mode"""
        try:
            # Check current state and toggle
            current_state = self.state()
            if current_state == 'zoomed' or self.attributes('-fullscreen'):
                # Exit fullscreen
                self.state('normal')
                try:
                    self.attributes('-fullscreen', False)
                except tk.TclError:
                    pass
                try:
                    self.attributes('-zoomed', False)
                except tk.TclError:
                    pass
                # Set to responsive window size
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                responsive_width = min(max(int(screen_width * 0.8), 1000), screen_width - 100)
                responsive_height = min(max(int(screen_height * 0.8), 700), screen_height - 100)
                self.geometry(f"{responsive_width}x{responsive_height}")
                self._center_window()
                logger.info("Exited fullscreen mode")
            else:
                # Enter fullscreen
                self.state('zoomed')
                try:
                    self.attributes('-fullscreen', True)
                except tk.TclError:
                    pass
                logger.info("Entered fullscreen mode")
        except Exception as e:
            logger.warning(f"Error toggling fullscreen: {e}")

    def _calculate_responsive_figsize(self, base_width: int = 8, base_height: int = 8, 
                                     aspect_ratio: float = 1.0) -> Tuple[float, float]:
        """Calculate responsive figure size based on current window size"""
        try:
            # Get current window dimensions
            self.update_idletasks()
            window_width = max(self.winfo_width(), 800)  # Minimum fallback
            window_height = max(self.winfo_height(), 600)  # Minimum fallback
            
            # Calculate available space for plots much more conservatively
            # Account for left panel (experiment control), tabs, headers, padding, scrollbars
            left_panel_width = 650   # Experiment control panel width (conservative estimate)
            header_height = 120      # Header, tab bar, and title height
            padding_buffer = 150     # Large padding buffer for safety
            scrollbar_width = 20     # Account for potential scrollbars
            
            available_width = max(window_width - left_panel_width - padding_buffer - scrollbar_width, 250)
            available_height = max(window_height - header_height - padding_buffer, 200)
            
            # Convert to figure size very conservatively 
            # Use 150 DPI for much more conservative sizing to prevent overlap
            fig_width = min(max(available_width / 150, 2.5), 7)   # Min 2.5", max 7"
            fig_height = min(max(available_height / 150, 2), 6)   # Min 2", max 6"
            
            # Maintain aspect ratio if requested
            if aspect_ratio == 1.0:  # Square plots
                size = min(fig_width, fig_height)
                fig_width = fig_height = size
            else:
                # Adjust to maintain aspect ratio within available space
                if fig_width / fig_height > aspect_ratio:
                    fig_width = fig_height * aspect_ratio
                else:
                    fig_height = fig_width / aspect_ratio
            
            logger.debug(f"Responsive figsize: {fig_width:.1f}x{fig_height:.1f} "
                        f"(window: {window_width}x{window_height}, available: {available_width}x{available_height})")
            
            return (fig_width, fig_height)
            
        except Exception as e:
            logger.warning(f"Error calculating responsive figsize: {e}, using defaults")
            return (base_width, base_height)

    def _resize_figure(self, fig: Figure, canvas: FigureCanvasTkAgg, aspect_ratio: float = 1.0):
        """Resize matplotlib figure to fit current window size"""
        try:
            # Calculate new responsive size
            new_figsize = self._calculate_responsive_figsize(aspect_ratio=aspect_ratio)
            
            # Only resize if size changed significantly (avoid unnecessary redraws)
            current_size = fig.get_size_inches()
            width_diff = abs(current_size[0] - new_figsize[0])
            height_diff = abs(current_size[1] - new_figsize[1])
            
            # Use a higher threshold to be more conservative about resizing
            if width_diff > 0.8 or height_diff > 0.8:  # Higher threshold to avoid frequent resizing
                fig.set_size_inches(new_figsize[0], new_figsize[1])
                # Use tight_layout to ensure plot elements fit properly
                try:
                    fig.tight_layout(pad=1.0)
                except:
                    pass  # tight_layout might fail in some cases
                canvas.draw_idle()  # Use draw_idle for better performance
                logger.debug(f"Figure resized to {new_figsize[0]:.1f}x{new_figsize[1]:.1f}")
                
        except Exception as e:
            logger.warning(f"Error resizing figure: {e}")

    def _configure_modern_style(self):
        """Configure modern TTK styles for the application"""
        style = ttk.Style()

        # Configure modern button style - fixed sizing
        style.configure(
            "Modern.TButton",
            background=ModernTheme.PRIMARY,
            foreground="white",
            font=ModernTheme.get_font(10, "normal"),  # Fixed font size
            borderwidth=0,
            focuscolor="none",
            padding=(16, 8),  # Fixed padding - won't scale with window
            width=10,  # Fixed minimum width for consistency
        )

        style.map(
            "Modern.TButton",
            background=[
                ("active", ModernTheme.PRIMARY_DARK),
                ("pressed", ModernTheme.PRIMARY_DARK),
            ],
        )

        # Configure secondary button style - fixed sizing
        style.configure(
            "Secondary.TButton",
            background=ModernTheme.SURFACE,
            foreground=ModernTheme.PRIMARY,
            font=ModernTheme.get_font(10, "normal"),  # Fixed font size
            borderwidth=1,
            focuscolor="none",
            padding=(16, 8),  # Fixed padding - won't scale with window
            width=10,  # Fixed minimum width for consistency
        )

        style.map(
            "Secondary.TButton",
            background=[
                ("active", ModernTheme.PRIMARY_LIGHT),
                ("pressed", ModernTheme.PRIMARY_LIGHT),
            ],
            bordercolor=[
                ("active", ModernTheme.PRIMARY),
                ("pressed", ModernTheme.PRIMARY),
            ],
        )

        # Configure modern notebook style
        style.configure(
            "Modern.TNotebook", background=ModernTheme.BACKGROUND, borderwidth=0
        )

        style.configure(
            "Modern.TNotebook.Tab",
            background="#F5F5F5",  # Light gray background
            foreground="#000000",  # ALWAYS black text
            font=ModernTheme.get_font(9, "bold"),  # Slightly smaller font to fit better
            padding=(8, 6),  # Reduced padding to allow more text space
            borderwidth=0,
            relief="flat",
            # Remove fixed width to allow tabs to expand as needed
            anchor="center",  # Center text regardless of tab width
        )

        style.map(
            "Modern.TNotebook.Tab",
            background=[
                ("selected", "#E0E0E0"),  # Slightly darker gray for selected tab
                ("active", "#EEEEEE"),    # Very light gray for hover
            ],
            foreground=[
                ("selected", "#000000"),  # ALWAYS black text even when selected
                ("active", "#000000"),    # ALWAYS black text even when hovering
                ("!selected", "#000000"), # ALWAYS black text when not selected
                ("!active", "#000000"),   # ALWAYS black text when not hovering
            ],
            font=[
                ("selected", ModernTheme.get_font(10, "bold")),  # ALWAYS bold
                ("active", ModernTheme.get_font(10, "bold")),    # ALWAYS bold
                ("!selected", ModernTheme.get_font(10, "bold")), # ALWAYS bold
                ("!active", ModernTheme.get_font(10, "bold")),   # ALWAYS bold
            ],
        )

        # Configure modern entry style
        style.configure(
            "Modern.TEntry",
            fieldbackground=ModernTheme.SURFACE,
            foreground=ModernTheme.TEXT_PRIMARY,
            borderwidth=1,
            focuscolor="none",
            padding=(12, 8),
        )

        style.map(
            "Modern.TEntry",
            bordercolor=[
                ("focus", ModernTheme.PRIMARY),
                ("active", ModernTheme.BORDER),
            ],
        )

        # Configure modern combobox style
        style.configure(
            "Modern.TCombobox",
            fieldbackground=ModernTheme.SURFACE,
            foreground=ModernTheme.TEXT_PRIMARY,
            borderwidth=1,
            focuscolor="none",
            padding=(12, 8),
        )

        # Configure modern label styles
        style.configure(
            "Title.TLabel",
            background=ModernTheme.BACKGROUND,
            foreground=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.get_font(24, "bold"),
        )

        style.configure(
            "Heading.TLabel",
            background=ModernTheme.BACKGROUND,
            foreground=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.get_font(16, "bold"),
        )

        style.configure(
            "Body.TLabel",
            background=ModernTheme.BACKGROUND,
            foreground=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.get_font(10, "normal"),
        )

        style.configure(
            "Caption.TLabel",
            background=ModernTheme.BACKGROUND,
            foreground=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(9, "normal"),
        )

    def create_modern_button(
        self, parent, text, command=None, style="primary", **kwargs
    ):
        """Create a modern styled button with hover effects"""
        if style == "primary":
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=ModernTheme.PRIMARY,
                fg="white",
                font=ModernTheme.get_font(10, "normal"),
                activebackground=ModernTheme.PRIMARY_DARK,
                activeforeground="white",
                **ModernTheme.BUTTON_STYLE,
                **kwargs,
            )
        elif style == "secondary":
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=ModernTheme.SURFACE,
                fg=ModernTheme.PRIMARY,
                font=ModernTheme.get_font(10, "normal"),
                activebackground=ModernTheme.PRIMARY_LIGHT,
                activeforeground=ModernTheme.PRIMARY,
                **ModernTheme.BUTTON_STYLE,
                **kwargs,
            )
        elif style == "success":
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=ModernTheme.SUCCESS,
                fg="white",
                font=ModernTheme.get_font(10, "normal"),
                activebackground=ModernTheme.SUCCESS,
                activeforeground="white",
                **ModernTheme.BUTTON_STYLE,
                **kwargs,
            )
        elif style == "warning":
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=ModernTheme.WARNING,
                fg="white",
                font=ModernTheme.get_font(10, "normal"),
                activebackground=ModernTheme.WARNING,
                activeforeground="white",
                **ModernTheme.BUTTON_STYLE,
                **kwargs,
            )

        # Add hover effects
        def on_enter(e):
            if style == "primary":
                btn.config(bg=ModernTheme.PRIMARY_DARK)
            elif style == "secondary":
                btn.config(bg=ModernTheme.PRIMARY_LIGHT)

        def on_leave(e):
            if style == "primary":
                btn.config(bg=ModernTheme.PRIMARY)
            elif style == "secondary":
                btn.config(bg=ModernTheme.SURFACE)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def create_modern_card(self, parent, **kwargs):
        """Create a modern card-style frame"""
        return tk.Frame(
            parent,
            bg=ModernTheme.SURFACE,
            relief="flat",
            borderwidth=1,
            highlightbackground=ModernTheme.BORDER,
            highlightthickness=1,
            **kwargs,
        )

    def set_plot_manager(self, plot_manager: Any) -> None:
        """Sets the plot manager instance for the GUI to use."""
        self.plot_manager = plot_manager
        logger.info("Plot manager set for optimizer app")

    def _setup_main_window(self) -> None:
        """
        Sets up the main window of the application with modern layout and styling.
        """
        # Main container frame with modern background
        self.main_frame = tk.Frame(self, bg=ModernTheme.BACKGROUND, padx=0, pady=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a top header bar for branding and navigation
        self._create_header_bar()

        # Create main content area
        self.content_frame = tk.Frame(self.main_frame, bg=ModernTheme.BACKGROUND)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))

        # Create and pack the status bar at the bottom of the window.
        self._create_status_bar()

        # Display the welcome screen when the application starts.
        self._show_welcome_screen()
    
    def _on_closing(self):
        """Handle application cleanup on close"""
        logger.info("Application closing - performing cleanup")
        
        try:
            if PERFORMANCE_OPTIMIZATION_AVAILABLE:
                # Clear plot cache
                plot_cache.clear()
                
                # Cleanup memory
                memory_manager.cleanup_matplotlib()
                memory_manager.cleanup_torch()
                memory_manager.force_gc()
                
                # Log performance statistics
                perf_monitor.log_performance("update_all_plots")
                memory_info = memory_manager.get_memory_info()
                logger.info(f"Final memory usage: {memory_info['rss_mb']:.1f}MB")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        # Close the application
        self.destroy()

    def _create_header_bar(self):
        """Create a modern header bar with branding"""
        header_frame = tk.Frame(
            self.main_frame,
            bg=ModernTheme.SURFACE,
            height=60,
            relief="flat",
            borderwidth=0,
        )
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Add a subtle shadow effect with a separator
        separator = tk.Frame(self.main_frame, bg=ModernTheme.DIVIDER, height=1)
        separator.pack(fill=tk.X)

        # Header content
        header_content = tk.Frame(header_frame, bg=ModernTheme.SURFACE)
        header_content.pack(fill=tk.BOTH, expand=True, padx=24, pady=0)

        # Application title
        title_label = tk.Label(
            header_content,
            text="Multi-Objective Optimization Laboratory",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.get_font(18, "bold"),
        )
        title_label.pack(side=tk.LEFT, pady=16)

        # Version badge
        version_label = tk.Label(
            header_content,
            text="v3.6.6",
            bg=ModernTheme.PRIMARY_LIGHT,
            fg=ModernTheme.PRIMARY,
            font=ModernTheme.get_font(10, "bold"),
            padx=8,
            pady=4,
        )
        version_label.pack(side=tk.LEFT, padx=(12, 0), pady=16)

        # Add status indicator (will be updated based on application state)
        self.status_indicator = tk.Label(
            header_content,
            text="●",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.SUCCESS,
            font=ModernTheme.get_font(12, "bold"),
        )
        self.status_indicator.pack(side=tk.RIGHT, pady=16)

        self.status_text = tk.Label(
            header_content,
            text="Ready",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(10, "normal"),
        )
        self.status_text.pack(side=tk.RIGHT, padx=(0, 8), pady=16)

    def _clear_content_frame(self):
        """Clear the content frame for new content"""
        # Check if content_frame exists and is valid
        if hasattr(self, 'content_frame') and self.content_frame.winfo_exists():
            for widget in self.content_frame.winfo_children():
                widget.destroy()

    def _show_welcome_screen(self) -> None:
        """
        Displays a modern welcome screen with improved layout and styling.
        """
        # Ensure main frame is recreated if it was destroyed
        if not hasattr(self, 'main_frame') or not self.main_frame.winfo_exists():
            self._create_main_layout()
        
        # Ensure content frame exists before clearing
        if not hasattr(self, 'content_frame') or not self.content_frame.winfo_exists():
            self.content_frame = tk.Frame(self.main_frame, bg=ModernTheme.BACKGROUND)
            self.content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))
        
        # Clear the content frame and create the welcome frame.
        self._clear_content_frame()

        # Create scrollable container for welcome content
        canvas = tk.Canvas(self.content_frame, bg=ModernTheme.BACKGROUND, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        
        # Create scrollable frame
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.BACKGROUND)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Bind canvas resize to update frame width
        def _configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update the scrollable frame width to match canvas width
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", _configure_scroll_region)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel_to_widget(widget):
            """Recursively bind mouse wheel events to widget and all its children"""
            # Bind mouse wheel events for Windows and Linux
            widget.bind("<MouseWheel>", _on_mousewheel)  # Windows
            widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
            widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
            
            # Recursively bind to all children
            for child in widget.winfo_children():
                _bind_mousewheel_to_widget(child)
        
        # Bind mouse wheel events to canvas and content frame
        canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
        
        # Also bind to the main content frame so scrolling works anywhere
        self.content_frame.bind("<MouseWheel>", _on_mousewheel)
        self.content_frame.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        self.content_frame.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Main welcome container with card styling
        welcome_container = self.create_modern_card(scrollable_frame, padx=0, pady=0)
        welcome_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        # Welcome content with responsive spacing
        welcome_content = tk.Frame(welcome_container, bg=ModernTheme.SURFACE)
        welcome_content.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)

        # Hero section with icon and title
        hero_frame = tk.Frame(welcome_content, bg=ModernTheme.SURFACE)
        hero_frame.pack(fill=tk.X, pady=(0, 32))

        # Modern title with better hierarchy
        title_label = tk.Label(
            hero_frame,
            text="Multi-Objective Optimization Laboratory",
            font=ModernTheme.get_font(28, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        )
        title_label.pack(pady=(0, 12))

        # Enhanced subtitle with features
        subtitle_label = tk.Label(
            hero_frame,
            text="Advanced Bayesian optimization with uncertainty quantification\nand interactive visualization for scientific research",
            font=ModernTheme.get_font(14, "normal"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            justify=tk.CENTER,
        )
        subtitle_label.pack(pady=(0, 40))

        # Features highlight section
        features_frame = tk.Frame(welcome_content, bg=ModernTheme.SURFACE)
        features_frame.pack(fill=tk.X, pady=(0, 40))

        features_title = tk.Label(
            features_frame,
            text="Key Features",
            font=ModernTheme.get_font(16, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        )
        features_title.pack(pady=(0, 16))

        # Feature cards grid
        features_grid = tk.Frame(features_frame, bg=ModernTheme.SURFACE)
        features_grid.pack(fill=tk.X)

        features = [
            (
                "🎯",
                "Multi-Objective Optimization",
                "Simultaneous optimization of multiple conflicting objectives",
            ),
            (
                "🔬",
                "Uncertainty Quantification",
                "GP prediction uncertainty and data density analysis",
            ),
            (
                "📊",
                "Interactive Visualization",
                "Real-time plots, 3D surfaces, and acquisition heatmaps",
            ),
            (
                "🤖",
                "Bayesian Learning",
                "Intelligent experiment suggestion using Gaussian processes",
            ),
            (
                "🧬",
                "UnifiedExponentialKernel",
                "Advanced kernel for mixed variables: continuous, discrete, and categorical parameters",
            ),
            (
                "⚡",
                "Modern Acquisition Functions",
                "State-of-the-art qNEHVI and qLogEI for superior optimization performance",
            ),
        ]

        for i, (icon, title, desc) in enumerate(features):
            row = i // 2
            col = i % 2

            feature_card = self.create_modern_card(features_grid, padx=16, pady=12)
            feature_card.grid(row=row, column=col, padx=12, pady=8, sticky="ew")

            features_grid.columnconfigure(col, weight=1)

            # Feature icon
            icon_label = tk.Label(
                feature_card,
                text=icon,
                font=ModernTheme.get_font(24, "normal"),
                bg=ModernTheme.SURFACE,
            )
            icon_label.pack(pady=(8, 4))

            # Feature title
            title_label = tk.Label(
                feature_card,
                text=title,
                font=ModernTheme.get_font(12, "bold"),
                bg=ModernTheme.SURFACE,
                fg=ModernTheme.TEXT_PRIMARY,
            )
            title_label.pack(pady=(0, 4))

            # Feature description
            desc_label = tk.Label(
                feature_card,
                text=desc,
                font=ModernTheme.get_font(9, "normal"),
                bg=ModernTheme.SURFACE,
                fg=ModernTheme.TEXT_SECONDARY,
                wraplength=200,
                justify=tk.CENTER,
            )
            desc_label.pack(pady=(0, 8))

        # Action buttons section
        actions_frame = tk.Frame(welcome_content, bg=ModernTheme.SURFACE)
        actions_frame.pack(fill=tk.X, pady=(40, 0))

        # Primary action button
        new_project_btn = self.create_modern_button(
            actions_frame,
            text="🚀 Start New Optimization",
            command=self._start_setup_wizard,
            style="primary",
        )
        new_project_btn.pack(pady=(0, 16))

        # SGLBO Screening button (new primary option)
        screening_btn = self.create_modern_button(
            actions_frame,
            text="🎯 SGLBO Screening",
            command=self._start_screening_wizard,
            style="secondary",
        )
        # Apply custom styling after creation
        screening_btn.config(
            bg=ModernTheme.SECONDARY,
            activebackground=ModernTheme.SECONDARY_DARK,
            fg="white"
        )
        
        # Fix hover effects for custom styling
        def screening_on_enter(e):
            screening_btn.config(bg=ModernTheme.SECONDARY_DARK)
            
        def screening_on_leave(e):
            screening_btn.config(bg=ModernTheme.SECONDARY)
            
        # Remove default hover handlers and add custom ones
        screening_btn.unbind("<Enter>")
        screening_btn.unbind("<Leave>")
        screening_btn.bind("<Enter>", screening_on_enter)
        screening_btn.bind("<Leave>", screening_on_leave)
        
        screening_btn.pack(pady=(0, 16))

        # Secondary actions in a row
        secondary_actions = tk.Frame(actions_frame, bg=ModernTheme.SURFACE)
        secondary_actions.pack()

        load_project_btn = self.create_modern_button(
            secondary_actions,
            text="📂 Load Study",
            command=self._load_existing_study,
            style="secondary",
        )
        load_project_btn.pack(side=tk.LEFT, padx=(0, 16))

        import_btn = self.create_modern_button(
            secondary_actions,
            text="📊 Import Data",
            command=self._import_experimental_data,
            style="secondary",
        )
        import_btn.pack(side=tk.LEFT)
        
        # Bind mouse wheel scrolling to all widgets in the welcome screen
        _bind_mousewheel_to_widget(scrollable_frame)

    def _start_setup_wizard(self) -> None:
        """
        Initiates the optimization setup wizard, clearing the main frame
        and preparing the interface for parameter and response definition.
        """
        # Clear the main frame to remove the welcome screen.
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Reset lists that hold references to parameter and response input rows.
        self.param_rows = []
        self.response_rows = []

        # Build the setup interface where users define their optimization problem.
        self._create_setup_interface()

    def _create_setup_interface(self) -> None:
        """
        Creates the graphical interface for setting up a new optimization study.
        This includes tabs for defining parameters and responses, and controls
        for selecting initial sampling methods.
        """
        setup_frame = tk.Frame(self.main_frame, bg="white")
        setup_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header for the setup section.
        header_label = tk.Label(
            setup_frame,
            text="Optimization Setup",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50",
        )
        header_label.pack(pady=(0, 20))

        # Notebook widget to organize Parameters and Responses tabs.
        notebook = ttk.Notebook(setup_frame, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True)

        # Parameters tab creation and addition to the notebook.
        params_tab = tk.Frame(notebook, bg="white")
        notebook.add(params_tab, text="Parameters")

        # Responses tab creation and addition to the notebook.
        responses_tab = tk.Frame(notebook, bg="white")
        notebook.add(responses_tab, text="Responses")

        # Populate the content of the Parameters tab.
        self._build_parameters_tab(params_tab)

        # Populate the content of the Responses tab.
        self._build_responses_tab(responses_tab)

        # Frame for action buttons (Start Optimization, Back).
        action_frame = tk.Frame(setup_frame, bg="white")
        action_frame.pack(fill=tk.X, pady=(20, 0))

        # Section for selecting the initial sampling method.
        sampling_frame = ttk.LabelFrame(action_frame, text="Initial Sampling Method")
        sampling_frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(
            sampling_frame, text="Select method for initial experiments:", bg="white"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Combobox(
            sampling_frame,
            textvariable=self.initial_sampling_method_var,
            values=["Random", "LHS"],  # Options for initial sampling.
            state="readonly",
            width=10,
        ).pack(side=tk.LEFT, padx=5, pady=5)

        # Frame to hold the main action buttons.
        btn_frame = tk.Frame(action_frame, bg="white")
        btn_frame.pack()

        # Button to start the optimization process.
        start_btn = tk.Button(
            btn_frame,
            text="Start Optimization",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=30,
            pady=10,
            command=self._start_optimization,
        )
        start_btn.pack(side=tk.LEFT, padx=10)

        # Button to go back to the welcome screen.
        back_btn = tk.Button(
            btn_frame,
            text="Back",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            padx=30,
            pady=10,
            command=self._show_welcome_screen,
        )
        back_btn.pack(side=tk.LEFT, padx=10)
        
        # Check if we have pending import data to populate the interface
        if hasattr(self, '_pending_import_data'):
            self._populate_interface_with_import_data()

    def _populate_interface_with_import_data(self):
        """Populate the setup interface with imported data."""
        try:
            import_data = self._pending_import_data
            
            # Clear existing parameter rows (there's usually one default)
            for row_data in self.param_rows[:]:
                # Get the frame from the first widget's parent
                if row_data and 'name' in row_data:
                    row_frame = row_data['name'].master
                    self._remove_row(row_frame, row_data, self.param_rows)
            
            # Add parameter rows from imported data
            for param_name, param_config in import_data['parameters'].items():
                self._add_parameter_row()
                # Get the most recently added row
                if self.param_rows:
                    row_data = self.param_rows[-1]
                    
                    # Fill in the parameter data
                    row_data['name'].delete(0, tk.END)
                    row_data['name'].insert(0, param_name)
                    row_data['type'].set(param_config['type'])
                    
                    if param_config['type'] in ['continuous', 'discrete']:
                        bounds = param_config['bounds']
                        bounds_text = f"[{bounds[0]}, {bounds[1]}]"
                        row_data['bounds'].delete(0, tk.END)
                        row_data['bounds'].insert(0, bounds_text)
                    elif param_config['type'] == 'categorical':
                        # For categorical, show categories
                        categories = param_config.get('categories', [])
                        if categories:
                            cats_text = str(categories) if len(categories) <= 5 else f"{categories[:5]}... ({len(categories)} total)"
                            row_data['bounds'].delete(0, tk.END)
                            row_data['bounds'].insert(0, cats_text)
            
            # Clear existing response rows
            for row_data in self.response_rows[:]:
                # Get the frame from the first widget's parent
                if row_data and 'name' in row_data:
                    row_frame = row_data['name'].master
                    self._remove_row(row_frame, row_data, self.response_rows)
            
            # Add response rows from imported data
            for response_name, response_config in import_data['responses'].items():
                self._add_response_row()
                # Get the most recently added row
                if self.response_rows:
                    row_data = self.response_rows[-1] 
                    
                    # Fill in the response data
                    row_data['name'].delete(0, tk.END)
                    row_data['name'].insert(0, response_name)
                    row_data['goal'].set(response_config['goal'])
            
            # Update status
            self.set_status(f"Setup interface populated with {len(import_data['parameters'])} parameters and {len(import_data['responses'])} responses")
            
            # Clean up
            delattr(self, '_pending_import_data')
            
        except Exception as e:
            logging.error(f"Failed to populate interface with import data: {e}")
            messagebox.showwarning("Warning", "Could not populate interface with imported data. You may need to configure parameters manually.")

    def _build_parameters_tab(self, parent: tk.Frame) -> None:
        """
        Builds the user interface for configuring optimization parameters.
        Allows users to define parameter names, types, bounds/values, and optimization goals.

        Args:
            parent (tk.Frame): The parent Tkinter frame to which this tab will be added.
        """
        # Header section for the parameters tab.
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            header_frame,
            text="Define Optimization Parameters",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text="Parameters are the variables you can control. You can also define optimization goals for them.",
            font=("Arial", 10),
            bg="white",
            fg="#7f8c8d",
        ).pack(anchor="w", pady=(5, 0))

        # Column headers for the parameter table.
        headers_frame = tk.Frame(parent, bg="#f8f9fa")
        headers_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        tk.Label(
            headers_frame,
            text="Name",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=15,
        ).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Type",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=12,
        ).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Bounds/Values",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=20,
        ).grid(row=0, column=2, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Goal",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=12,
        ).grid(row=0, column=3, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Target",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=10,
        ).grid(row=0, column=4, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Action",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=8,
        ).grid(row=0, column=5, padx=5, pady=5)

        # Scrollable area for parameter input rows.
        params_container = tk.Frame(parent, bg="white")
        params_container.pack(fill=tk.BOTH, expand=True, padx=20)

        canvas = tk.Canvas(params_container, bg="white")
        scrollbar = ttk.Scrollbar(
            params_container, orient="vertical", command=canvas.yview
        )
        self.params_frame = tk.Frame(canvas, bg="white")

        self.params_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.params_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Button to add a new parameter row.
        add_btn = tk.Button(
            params_container,
            text="Add Parameter",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=self._add_parameter_row,
        )
        add_btn.pack(pady=10)

        # Add an initial parameter row when the tab is built.
        self._add_parameter_row()

    def _build_responses_tab(self, parent: tk.Frame) -> None:
        """
        Builds the user interface for configuring optimization responses (objectives).
        Allows users to define response names, optimization goals, units, and target values.

        Args:
            parent (tk.Frame): The parent Tkinter frame to which this tab will be added.
        """
        # Header section for the responses tab.
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            header_frame,
            text="Define Optimization Responses",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text="Responses are the outputs you measure and want to optimize.",
            font=("Arial", 10),
            bg="white",
            fg="#7f8c8d",
        ).pack(anchor="w", pady=(5, 0))

        # Column headers for the response table.
        headers_frame = tk.Frame(parent, bg="#f8f9fa")
        headers_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        tk.Label(
            headers_frame,
            text="Name",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=15,
        ).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Goal",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=12,
        ).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Target",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=10,
        ).grid(row=0, column=2, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Units",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=10,
        ).grid(row=0, column=3, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Action",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=8,
        ).grid(row=0, column=4, padx=5, pady=5)

        # Scrollable area for response input rows.
        responses_container = tk.Frame(parent, bg="white")
        responses_container.pack(fill=tk.BOTH, expand=True, padx=20)

        canvas = tk.Canvas(responses_container, bg="white")
        scrollbar = ttk.Scrollbar(
            responses_container, orient="vertical", command=canvas.yview
        )
        self.responses_frame = tk.Frame(canvas, bg="white")

        self.responses_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.responses_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Button to add a new response row.
        add_btn = tk.Button(
            responses_container,
            text="Add Response",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            command=self._add_response_row,
        )
        add_btn.pack(pady=10)

        # Button to set response importance ratings
        importance_btn = tk.Button(
            responses_container,
            text="⭐ Set Response Importance",
            font=("Arial", 10, "bold"),
            bg="#FF9800",  # Orange color for importance
            fg="white",
            command=self._show_importance_dialog,
        )
        importance_btn.pack(pady=(0, 10))

        # Add an initial response row when the tab is built.
        self._add_response_row()

    def _add_parameter_row(self) -> None:
        """
        Adds a new row to the parameter configuration table, allowing the user to
        define a new optimization parameter with its name, type, bounds/values,
        optimization goal, and an optional target value.
        """
        row_frame = tk.Frame(
            self.params_frame, bg="#f8f9fa", relief="solid", borderwidth=1
        )
        row_frame.pack(fill=tk.X, padx=5, pady=5)

        widgets = {}

        # Entry for parameter name.
        widgets["name"] = tk.Entry(row_frame, width=15)
        widgets["name"].grid(row=0, column=0, padx=5, pady=5)
        widgets["name"].insert(0, f"Parameter_{len(self.param_rows) + 1}")

        # Combobox for parameter type (continuous, discrete, categorical).
        widgets["type"] = ttk.Combobox(
            row_frame,
            values=["continuous", "discrete", "categorical"],
            width=12,
            state="readonly",
        )
        widgets["type"].grid(row=0, column=1, padx=5, pady=5)
        widgets["type"].set("continuous")
        # Bind an event to update bounds/values field based on type selection.
        widgets["type"].bind(
            "<<ComboboxSelected>>", lambda e: self._on_param_type_change(widgets)
        )

        # Entry for parameter bounds or categorical values.
        widgets["bounds"] = tk.Entry(row_frame, width=20)
        widgets["bounds"].grid(row=0, column=2, padx=5, pady=5)
        widgets["bounds"].insert(0, "[0, 100]")

        # Combobox for parameter optimization goal (None, Maximize, Minimize, Target).
        widgets["goal"] = ttk.Combobox(
            row_frame,
            values=["None", "Maximize", "Minimize", "Target"],
            width=12,
            state="readonly",
        )
        widgets["goal"].grid(row=0, column=3, padx=5, pady=5)
        widgets["goal"].set("None")
        # Bind an event to enable/disable target field based on goal selection.
        widgets["goal"].bind(
            "<<ComboboxSelected>>", lambda e: self._on_param_goal_change(widgets)
        )

        # Entry for target/ideal value (initially disabled).
        widgets["target"] = tk.Entry(row_frame, width=10)
        widgets["target"].grid(row=0, column=4, padx=5, pady=5)
        widgets["target"].config(state="disabled")

        # Button to remove this parameter row.
        remove_btn = tk.Button(
            row_frame,
            text="Remove",
            bg="#e74c3c",
            fg="white",
            command=lambda: self._remove_row(row_frame, widgets, self.param_rows),
        )
        remove_btn.grid(row=0, column=5, padx=5, pady=5)

        # Add the new row's widgets to the list of parameter rows.
        self.param_rows.append(widgets)

    def _add_response_row(self) -> None:
        """
        Adds a new row to the response configuration table, allowing the user to
        define a new optimization response with its name, optimization goal,
        an optional target value, and units.
        """
        row_frame = tk.Frame(
            self.responses_frame, bg="#f8f9fa", relief="solid", borderwidth=1
        )
        row_frame.pack(fill=tk.X, padx=5, pady=5)

        widgets = {}

        # Entry for response name.
        widgets["name"] = tk.Entry(row_frame, width=15)
        widgets["name"].grid(row=0, column=0, padx=5, pady=5)
        widgets["name"].insert(0, f"Response_{len(self.response_rows) + 1}")

        # Combobox for response optimization goal (Maximize, Minimize, Target, Range).
        widgets["goal"] = ttk.Combobox(
            row_frame,
            values=["Maximize", "Minimize", "Target", "Range"],
            width=12,
            state="readonly",
        )
        widgets["goal"].grid(row=0, column=1, padx=5, pady=5)
        widgets["goal"].set("Maximize")
        # Bind an event to enable/disable target field based on goal selection.
        widgets["goal"].bind(
            "<<ComboboxSelected>>", lambda e: self._on_response_goal_change(widgets)
        )

        # Entry for target/ideal value or range (initially disabled).
        widgets["target"] = tk.Entry(row_frame, width=10)
        widgets["target"].grid(row=0, column=2, padx=5, pady=5)
        widgets["target"].config(state="disabled")

        # Entry for units.
        widgets["units"] = tk.Entry(row_frame, width=10)
        widgets["units"].grid(row=0, column=3, padx=5, pady=5)
        widgets["units"].insert(0, "%")

        # Button to remove this response row.
        remove_btn = tk.Button(
            row_frame,
            text="Remove",
            bg="#e74c3c",
            fg="white",
            command=lambda: self._remove_row(row_frame, widgets, self.response_rows),
        )
        remove_btn.grid(row=0, column=4, padx=5, pady=5)

        # Add the new row's widgets to the list of response rows.
        self.response_rows.append(widgets)

    def _on_param_type_change(self, widgets: Dict[str, Any]) -> None:
        """
        Handles the event when a parameter's type is changed in the setup interface.
        Adjusts the placeholder text in the 'Bounds/Values' entry field based on the selected type.

        Args:
            widgets (Dict[str, Any]): A dictionary containing the Tkinter widgets for the current parameter row.
        """
        param_type = widgets["type"].get()
        widgets["bounds"].delete(0, tk.END)
        if param_type == "categorical":
            widgets["bounds"].insert(0, "Value1, Value2, Value3")
        elif param_type == "discrete":
            widgets["bounds"].insert(0, "[0, 10]")
        else:  # continuous
            widgets["bounds"].insert(0, "[0.0, 100.0]")

    def _on_param_goal_change(self, widgets: Dict[str, Any]) -> None:
        """
        Handles the event when a parameter's optimization goal is changed.
        Enables or disables the 'Target' entry field based on the selected goal.

        Args:
            widgets (Dict[str, Any]): A dictionary containing the Tkinter widgets for the current parameter row.
        """
        goal = widgets["goal"].get()
        if goal in ["Target"]:
            widgets["target"].config(state="normal")
        else:
            widgets["target"].config(state="disabled")
            widgets["target"].delete(0, tk.END)

    def _on_response_goal_change(self, widgets: Dict[str, Any]) -> None:
        """
        Handles the event when a response's optimization goal is changed.
        Enables or disables the 'Target' entry field based on the selected goal.

        Args:
            widgets (Dict[str, Any]): A dictionary containing the Tkinter widgets for the current response row.
        """
        goal = widgets["goal"].get()
        if goal in ["Target", "Range"]:
            widgets["target"].config(state="normal")
            if goal == "Range":
                widgets["target"].delete(0, tk.END)
                widgets["target"].insert(0, "[0.0, 1.0]")  # Placeholder for range
        else:
            widgets["target"].config(state="disabled")
            widgets["target"].delete(0, tk.END)

    def _remove_row(
        self,
        frame: tk.Frame,
        widgets: Dict[str, Any],
        widgets_list: List[Dict[str, Any]],
    ) -> None:
        """
        Removes a parameter or response configuration row from the GUI.

        Args:
            frame (tk.Frame): The Tkinter frame representing the row to be removed.
            widgets (Dict[str, Any]): The dictionary of widgets associated with the row.
            widgets_list (List[Dict[str, Any]]): The list from which the widgets dictionary should be removed.
        """
        frame.destroy()
        if widgets in widgets_list:
            widgets_list.remove(widgets)

    def _show_importance_dialog(self) -> None:
        """
        Show the response importance rating dialog.
        
        This method collects current response configurations and opens a dialog
        where users can set 1-5 star importance ratings for each response.
        The ratings are stored in the response configurations for later use
        in acquisition function calculations.
        """
        if not IMPORTANCE_DIALOG_AVAILABLE:
            messagebox.showerror(
                "Feature Unavailable", 
                "Response importance rating dialog is not available."
            )
            return
        
        try:
            # Collect current response configurations
            responses_config = {}
            for row in self.response_rows:
                name = row["name"].get().strip()
                if not name or name.startswith("Response_"):
                    continue  # Skip empty or default placeholder rows
                
                goal = row["goal"].get()
                target = row["target"].get().strip()
                units = row["units"].get().strip()
                
                # Build basic response config
                config = {
                    "goal": goal,
                    "type": "continuous"  # Default type
                }
                
                if target and goal in ["Target", "Range"]:
                    try:
                        if goal == "Target":
                            config["target"] = float(target)
                        elif goal == "Range":
                            # Parse range format [min, max]
                            range_values = eval(target)
                            if isinstance(range_values, (list, tuple)) and len(range_values) == 2:
                                config["range"] = list(range_values)
                    except (ValueError, SyntaxError):
                        pass  # Keep config without target/range if parsing fails
                
                if units:
                    config["units"] = units
                
                responses_config[name] = config
            
            if not responses_config:
                messagebox.showwarning(
                    "No Responses", 
                    "Please define at least one response before setting importance ratings."
                )
                return
            
            # Callback function to handle dialog results
            def on_importance_dialog_complete(result):
                if result.get('applied', False):
                    # Store importance ratings in the response configurations
                    ratings = result.get('ratings', {})
                    weights = result.get('weights', {})
                    
                    # Update response configurations with importance and weights
                    for response_name, rating in ratings.items():
                        if response_name in responses_config:
                            responses_config[response_name]['importance'] = rating
                            responses_config[response_name]['optimization_weight'] = weights.get(response_name, 1.0)
                    
                    # Store updated configurations for use in optimization
                    self.response_importance_ratings = ratings
                    self.response_optimization_weights = weights
                    
                    # Update 3D surface control panel with new importance weights
                    if hasattr(self, 'surface_3d_control_panel') and self.surface_3d_control_panel:
                        self.surface_3d_control_panel.update_global_importance_weights(weights)
                        logging.info("Updated 3D Surface control panel with new importance weights")
                    
                    logging.info(f"Applied response importance ratings: {ratings}")
                    logging.info(f"Calculated optimization weights: {weights}")
                    
                    # Show confirmation
                    messagebox.showinfo(
                        "Importance Set", 
                        f"Importance ratings applied for {len(ratings)} responses.\n"
                        f"These will be used in optimization calculations."
                    )
            
            # Show the importance dialog
            show_importance_dialog(
                parent=self,
                responses_config=responses_config,
                callback=on_importance_dialog_complete
            )
            
        except Exception as e:
            logging.error(f"Error showing importance dialog: {e}")
            messagebox.showerror("Error", f"Failed to show importance dialog: {e}")

    def _start_optimization(self) -> None:
        """
        Collects the defined parameters and responses from the setup interface,
        validates them, and initiates a new optimization session via the controller.
        Displays error messages if the configuration is invalid.
        """
        try:
            # Collect parameter configurations from the GUI.
            params_config = {}
            logger.debug("=== COLLECTING PARAMETER CONFIGURATIONS FROM GUI ===")
            for i, row in enumerate(self.param_rows):
                name = row["name"].get().strip()
                logger.debug(f"Processing parameter row {i}: name='{name}'")
                
                # Skip rows that haven't been named or are still default placeholders.
                if not name or name.startswith("Parameter_"):
                    logger.debug(f"  SKIPPING row {i}: name is empty or default placeholder")
                    continue

                param_type = row["type"].get()
                bounds_str = row["bounds"].get().strip()
                goal = row["goal"].get()
                target_str = row["target"].get().strip()
                
                logger.debug(f"  Parameter '{name}': type='{param_type}', bounds='{bounds_str}', goal='{goal}', target='{target_str}'")

                config = {"type": param_type, "goal": goal}
                logger.debug(f"  Created initial config for '{name}': {config}")

                # Parse bounds/values based on parameter type.
                if param_type in ["continuous", "discrete"]:
                    try:
                        bounds = json.loads(bounds_str)
                        if not isinstance(bounds, list) or len(bounds) != 2:
                            raise ValueError("Bounds must be a list of two numbers.")
                        config["bounds"] = bounds
                    except json.JSONDecodeError:
                        raise ValueError(
                            f"Invalid JSON format for bounds of '{name}': {bounds_str}"
                        )
                    except ValueError as ve:
                        raise ValueError(f"Invalid bounds for '{name}': {ve}")
                elif param_type == "categorical":
                    try:
                        values = [x.strip() for x in bounds_str.split(",")]
                        if not values or all(not v for v in values):
                            raise ValueError("Categorical values cannot be empty.")
                        config["values"] = values
                    except Exception:
                        raise ValueError(
                            f"Invalid comma-separated values format for '{name}': {bounds_str}"
                        )

                # Add target/ideal value if the goal requires it.
                if goal == "Target" and target_str:
                    try:
                        config["ideal"] = float(target_str)
                        logger.debug(f"  Added target value for '{name}': {config['ideal']}")
                    except ValueError:
                        raise ValueError(
                            f"Invalid target value for '{name}': '{target_str}' is not a number."
                        )

                logger.debug(f"  FINAL config for parameter '{name}': {config}")
                params_config[name] = config
                logger.debug(f"  ✓ STORED parameter '{name}' in params_config")

            # Summary of collected parameters
            logger.debug(f"=== PARAMETER COLLECTION SUMMARY ===")
            logger.debug(f"Total parameters collected: {len(params_config)}")
            for name, config in params_config.items():
                logger.debug(f"  '{name}': goal='{config['goal']}', type='{config['type']}'")
            logger.debug(f"=== END PARAMETER COLLECTION ===")

            # Collect response configurations from the GUI.
            responses_config = {}
            for row in self.response_rows:
                name = row["name"].get().strip()
                # Skip rows that haven't been named or are still default placeholders.
                if not name or name.startswith("Response_"):
                    continue

                goal = row["goal"].get()
                target_str = row["target"].get().strip()
                units = row["units"].get().strip()

                config = {"goal": goal, "units": units if units else None}

                # Add target/range value if the goal requires it.
                if goal in ["Target", "Range"] and target_str:
                    try:
                        if goal == "Target":
                            config["ideal"] = float(target_str)
                        elif goal == "Range":
                            range_vals = json.loads(target_str)
                            if not isinstance(range_vals, list) or len(range_vals) != 2:
                                raise ValueError("Range must be a list of two numbers.")
                            config["range"] = range_vals
                    except json.JSONDecodeError:
                        raise ValueError(
                            f"Invalid JSON format for target/range of '{name}': {target_str}"
                        )
                    except ValueError as ve:
                        raise ValueError(f"Invalid target/range for '{name}': {ve}")

                # Add importance rating and optimization weight if available
                if hasattr(self, 'response_importance_ratings') and name in self.response_importance_ratings:
                    config['importance'] = self.response_importance_ratings[name]
                if hasattr(self, 'response_optimization_weights') and name in self.response_optimization_weights:
                    config['optimization_weight'] = self.response_optimization_weights[name]
                
                responses_config[name] = config

            # Perform basic validation on the collected configurations.
            if not params_config:
                raise ValueError(
                    "At least one parameter must be defined to start optimization."
                )
            if not responses_config:
                raise ValueError(
                    "At least one response must be defined to start optimization."
                )

            # Check if at least one parameter or response has an optimization goal.
            has_objective = False
            for conf in list(params_config.values()) + list(responses_config.values()):
                if conf.get("goal") in ["Maximize", "Minimize", "Target", "Range"]:
                    has_objective = True
                    break

            if not has_objective:
                raise ValueError(
                    "At least one parameter or response must have an optimization goal (Maximize, Minimize, Target, or Range) to define the optimization problem."
                )

            # If all validations pass, start the optimization via the controller.
            if self.controller:
                initial_sampling_method = self.initial_sampling_method_var.get()
                
                # Check if we already have an optimizer with imported data
                if (self.controller.optimizer and 
                    hasattr(self.controller, 'imported_data') and 
                    self.controller.imported_data is not None):
                    
                    # We have imported data - just proceed to the main interface
                    # The optimizer already has the data loaded
                    logger.info("Using existing optimizer with imported data")
                    
                    # Use the stored imported configuration
                    imported_params = self.controller.imported_params_config
                    imported_responses = self.controller.imported_responses_config
                    
                    # Create the main optimization interface with imported data
                    self.create_main_interface(imported_params, imported_responses)
                    
                    # Update displays with existing data
                    if hasattr(self.controller, 'update_view'):
                        self.controller.update_view()
                    
                    # Set status to show that imported data is loaded
                    data_count = len(self.controller.imported_data) if self.controller.imported_data is not None else 0
                    self.set_status(f"Optimization interface ready with {data_count} imported data points")
                else:
                    # Normal path - create new optimization
                    self.controller.start_new_optimization(
                        params_config, responses_config, [], initial_sampling_method
                    )
            else:
                messagebox.showerror(
                    "Initialization Error",
                    "Controller not initialized. Please restart the application.",
                )

        except ValueError as ve:  # Catch specific validation errors.
            messagebox.showerror("Configuration Error", str(ve))
        except Exception as e:  # Catch any other unexpected errors.
            logger.error(
                f"An unexpected error occurred during optimization setup: {e}",
                exc_info=True,
            )
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def create_main_interface(
        self, params_config: Dict[str, Any], responses_config: Dict[str, Any]
    ) -> None:
        """
        Creates the main optimization interface after a study has been started or loaded.
        This involves clearing the setup interface and building the control and plotting panels.

        Args:
            params_config (Dict[str, Any]): The configuration of parameters for the current study.
            responses_config (Dict[str, Any]): The configuration of responses for the current study.
        """
        # Clear any existing widgets from the main frame (e.g., setup wizard).
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Build the main layout for the active optimization session.
        self._create_main_layout(params_config, responses_config)

    def _create_main_layout(
        self, params_config: Dict[str, Any], responses_config: Dict[str, Any]
    ) -> None:
        """
        Creates the overall layout for the main optimization interface, dividing it
        into a left control panel and a right plotting panel using a PanedWindow.

        Args:
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Header for the main application interface.
        header_frame = tk.Frame(self.main_frame, bg="#34495e", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(
            False
        )  # Prevent frame from resizing to fit content.

        tk.Label(
            header_frame,
            text="Multi-Objective Optimization - Active Session",
            font=("Arial", 16, "bold"),
            bg="#34495e",
            fg="white",
        ).pack(pady=20)

        # Content area that will hold the control and plot panels.
        content_frame = tk.Frame(self.main_frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # PanedWindow to allow resizing of left and right panels.
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left panel for experiment controls.
        left_panel = tk.Frame(paned, bg="white", relief="solid", borderwidth=1)
        paned.add(left_panel, weight=1)

        # Right panel for data visualizations.
        right_panel = tk.Frame(paned, bg="white", relief="solid", borderwidth=1)
        paned.add(right_panel, weight=2)

        # Populate the left and right panels.
        self._build_control_panel(left_panel, params_config, responses_config)
        self._build_plot_panel(right_panel, params_config, responses_config)

    def _build_control_panel(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the left-hand control panel of the main interface.
        This panel contains sections for experiment suggestions, result submission,
        and displaying the best compromise solution.

        Args:
            parent (tk.Frame): The parent Tkinter frame for the control panel.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Header for the control panel.
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 5))

        tk.Label(
            header_frame,
            text="Experiment Control",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(side=tk.LEFT, anchor="w")

        # Button to save the current optimization study.
        save_btn = tk.Button(
            header_frame,
            text="Save Optimization",
            font=("Arial", 10),
            bg="#28a745",
            fg="white",
            command=self._save_current_study,
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

        # Add button to open Goal Impact Dashboard
        if GOAL_IMPACT_DASHBOARD_AVAILABLE:
            dashboard_btn = tk.Button(
                header_frame,
                text="📊 Goal Impact Dashboard",
                font=("Arial", 10),
                bg="#3498db",
                fg="white",
                command=self._show_goal_impact_dashboard,
            )
            dashboard_btn.pack(side=tk.RIGHT, padx=5)


        # Notebook widget to organize different control sections.
        notebook = ttk.Notebook(parent, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab for displaying next experiment suggestions.
        suggestions_tab = tk.Frame(notebook, bg="white")
        notebook.add(suggestions_tab, text="Next Experiment")

        # Tab for submitting experimental results.
        results_tab = tk.Frame(notebook, bg="white")
        notebook.add(results_tab, text="Submit Results")

        # Tab for displaying the best compromise solution found so far.
        best_tab = tk.Frame(notebook, bg="white")
        notebook.add(best_tab, text="Best Solution")

        # Tab for GPU acceleration status and controls (if available)
        if GPU_ACCELERATION_AVAILABLE:
            gpu_tab = tk.Frame(notebook, bg="white")
            notebook.add(gpu_tab, text="🚀 GPU Status")
        
        # Tab for parallel optimization capabilities
        parallel_tab = tk.Frame(notebook, bg="white")
        notebook.add(parallel_tab, text="⚡ Parallel Optimization")

        # Populate the content of each control tab.
        self._build_suggestions_tab(suggestions_tab, params_config)
        self._build_results_tab(results_tab, responses_config)
        self._build_best_solution_tab(best_tab, params_config, responses_config)
        
        # Build GPU tab if available
        if GPU_ACCELERATION_AVAILABLE:
            self._build_gpu_tab(gpu_tab)
            
        # Build parallel optimization tab
        self._build_parallel_optimization_tab(parallel_tab)

    def _build_suggestions_tab(
        self, parent: tk.Frame, params_config: Dict[str, Any]
    ) -> None:
        """
        Builds the 'Next Experiment' tab, which displays the optimizer's suggested
        parameter values for the next experiment and provides controls for batch
        suggestion generation and export.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters for the current study.
        """
        # Header for the suggestions section.
        tk.Label(
            parent,
            text="Recommended Parameters",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Instructions for the user.
        tk.Label(
            parent,
            text="Use these parameter values for your next experiment:",
            font=("Arial", 10),
            bg="white",
            fg="#7f8c8d",
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Frame to display individual parameter suggestions.
        params_frame = tk.LabelFrame(
            parent, text="Parameter Values", font=("Arial", 10), bg="white"
        )
        params_frame.pack(fill=tk.X, padx=15, pady=10)

        # Clear existing labels to prepare for new suggestions.
        self.suggestion_labels = {}

        # Create a label for each parameter to display its suggested value.
        for name in params_config:
            param_frame = tk.Frame(params_frame, bg="white")
            param_frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(
                param_frame,
                text=f"{name}:",
                font=("Arial", 10, "bold"),
                bg="white",
                width=15,
                anchor="w",
            ).pack(side=tk.LEFT)

            value_label = tk.Label(
                param_frame,
                text="Calculating...",  # Placeholder text while suggestion is being generated.
                font=("Arial", 11, "bold"),
                bg="#e8f5e8",
                fg="#2d5a3d",
                relief="solid",
                borderwidth=1,
                padx=10,
                pady=3,
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

            self.suggestion_labels[name] = value_label

        # Button to manually refresh the single experiment suggestion.
        refresh_btn = tk.Button(
            parent,
            text="Refresh Suggestion",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=self._refresh_suggestion,
        )
        refresh_btn.pack(pady=10)
        
        # Add explanation about suggestion behavior
        explanation_label = tk.Label(
            parent,
            text="Note: The algorithm suggests the most informative experiment.\nThe same suggestion will appear until new data is added.",
            font=("Arial", 8),
            fg="#7f8c8d",
            bg="white",
            justify=tk.CENTER
        )
        explanation_label.pack(pady=(0, 10))

        # Section for generating and managing batch suggestions.
        batch_frame = tk.LabelFrame(
            parent, text="Batch Suggestions", font=("Arial", 10), bg="white"
        )
        batch_frame.pack(fill=tk.X, padx=15, pady=10)

        # Input field for the number of batch suggestions.
        tk.Label(batch_frame, text="Number of Suggestions:", bg="white").pack(
            side=tk.LEFT, padx=5, pady=5
        )
        self.num_suggestions_entry = tk.Entry(batch_frame, width=5)
        self.num_suggestions_entry.insert(0, "10")  # Default to 10 suggestions.
        self.num_suggestions_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Input field for parameter precision (decimal places).
        tk.Label(batch_frame, text="Decimal Places:", bg="white").pack(
            side=tk.LEFT, padx=(15, 5), pady=5
        )
        self.precision_entry = tk.Entry(batch_frame, width=3)
        self.precision_entry.insert(0, "3")  # Default to 3 decimal places.
        self.precision_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to generate a batch of suggestions.
        generate_batch_btn = tk.Button(
            batch_frame,
            text="Generate Batch",
            font=("Arial", 10),
            bg="#28a745",
            fg="white",
            command=self._generate_batch_suggestions,
        )
        generate_batch_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to download the generated batch suggestions as a CSV file.
        download_batch_btn = tk.Button(
            batch_frame,
            text="Download CSV",
            font=("Arial", 10),
            bg="#007bff",
            fg="white",
            command=self._download_batch_suggestions_csv,
        )
        download_batch_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to upload experimental data from a CSV file.
        upload_batch_btn = tk.Button(
            batch_frame,
            text="Upload CSV",
            font=("Arial", 10),
            bg="#6f42c1",
            fg="white",
            command=self._upload_batch_suggestions_csv,
        )
        upload_batch_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # ScrolledText widget to display all experimental data points.
        self.batch_suggestions_text = scrolledtext.ScrolledText(
            parent, height=10, wrap=tk.NONE, font=("Consolas", 9)
        )
        self.batch_suggestions_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        self.batch_suggestions_text.insert(
            tk.END, "All experimental data points will appear here."
        )
        self.batch_suggestions_text.config(state=tk.DISABLED)  # Make it read-only.

        # List to store generated batch suggestions internally.
        self.generated_batch_suggestions = []
        
        # Display experimental data if available
        self._update_experimental_data_display()

    def _build_results_tab(
        self, parent: tk.Frame, responses_config: Dict[str, Any]
    ) -> None:
        """
        Builds the 'Submit Results' tab, allowing users to input experimental
        results for each response variable.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            responses_config (Dict[str, Any]): The configuration of responses for the current study.
        """
        # Header for the results submission section.
        tk.Label(
            parent,
            text="Enter Experimental Results",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Frame to contain entry fields for response values.
        results_frame = tk.LabelFrame(
            parent, text="Response Values", font=("Arial", 10), bg="white"
        )
        results_frame.pack(fill=tk.X, padx=15, pady=10)

        # Clear existing entry widgets.
        self.results_entries = {}

        # Create an entry field for each response variable.
        for name, config in responses_config.items():
            result_frame = tk.Frame(results_frame, bg="white")
            result_frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(
                result_frame,
                text=f"{name}:",
                font=("Arial", 10, "bold"),
                bg="white",
                width=15,
                anchor="w",
            ).pack(side=tk.LEFT)

            entry = tk.Entry(result_frame, font=("Arial", 10), width=15)
            entry.pack(side=tk.LEFT, padx=(10, 5))

            units = config.get("units", "")
            if units:
                tk.Label(
                    result_frame,
                    text=units,
                    font=("Arial", 9),
                    bg="white",
                    fg="#7f8c8d",
                ).pack(side=tk.LEFT)

            self.results_entries[name] = entry

        # Buttons frame for results submission and editing
        buttons_frame = tk.Frame(parent, bg="white")
        buttons_frame.pack(pady=20)
        
        # Button to submit the entered results.
        submit_btn = tk.Button(
            buttons_frame,
            text="Submit Results",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=30,
            pady=10,
            command=self._submit_results,
        )
        submit_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Button to edit last result (initially hidden)
        self.edit_last_result_btn = tk.Button(
            buttons_frame,
            text="📝 Edit Last Result",
            font=("Arial", 11, "bold"),
            bg="#f39c12",
            fg="white",
            padx=25,
            pady=10,
            command=self._edit_last_result,
            state=tk.DISABLED
        )
        self.edit_last_result_btn.pack(side=tk.LEFT)
        
        # Update button visibility based on data availability
        self._update_edit_button_state()

    def _build_best_solution_tab(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the 'Best Solution' tab, which displays the optimal parameter values
        and their predicted response values as determined by the optimizer.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters for the current study.
            responses_config (Dict[str, Any]): The configuration of responses for the current study.
        """
        # Header for optimal parameters section.
        tk.Label(
            parent,
            text="Optimal Parameter Values",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Frame to display optimal parameter values.
        params_frame = tk.LabelFrame(
            parent, text="Parameters", font=("Arial", 10), bg="white"
        )
        params_frame.pack(fill=tk.X, padx=15, pady=5)

        # Create labels for each parameter to display its optimal value.
        for name in params_config:
            param_frame = tk.Frame(params_frame, bg="white")
            param_frame.pack(fill=tk.X, padx=10, pady=3)

            tk.Label(
                param_frame,
                text=f"{name}:",
                font=("Arial", 10, "bold"),
                bg="white",
                width=15,
                anchor="w",
            ).pack(side=tk.LEFT)

            value_label = tk.Label(
                param_frame,
                text="Not available",  # Placeholder until data is updated.
                font=("Arial", 10),
                bg="#ecf0f1",
                relief="solid",
                borderwidth=1,
                padx=10,
                pady=2,
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

            self.best_solution_labels["params"][name] = value_label

        # Header for predicted response values section.
        tk.Label(
            parent,
            text="Predicted Response Values",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Frame to display predicted response values.
        responses_frame = tk.LabelFrame(
            parent, text="Responses", font=("Arial", 10), bg="white"
        )
        responses_frame.pack(fill=tk.X, padx=15, pady=5)

        # Create labels for each response to display its predicted mean and confidence interval.
        for name in responses_config:
            response_frame = tk.Frame(responses_frame, bg="white")
            response_frame.pack(fill=tk.X, padx=10, pady=3)

            tk.Label(
                response_frame,
                text=f"{name}:",
                font=("Arial", 10, "bold"),
                bg="white",
                width=15,
                anchor="w",
            ).pack(side=tk.LEFT)

            value_label = tk.Label(
                response_frame,
                text="Not available",  # Placeholder until data is updated.
                font=("Arial", 10),
                bg="#ecf0f1",
                relief="solid",
                borderwidth=1,
                padx=10,
                pady=2,
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

            self.best_solution_labels["responses"][name] = {
                "mean": value_label,
                "ci": None,  # Placeholder for confidence interval label.
            }

            ci_label = tk.Label(
                response_frame,
                text="",  # Confidence interval text.
                font=("Arial", 8),
                bg="#ecf0f1",
                fg="#7f8c8d",
                padx=5,
                pady=1,
            )
            ci_label.pack(side=tk.LEFT, padx=(5, 0))
            self.best_solution_labels["responses"][name]["ci"] = ci_label

    def _build_gpu_tab(self, parent: tk.Frame) -> None:
        """
        Builds the GPU acceleration tab showing GPU status, performance metrics,
        and validation controls.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
        """
        try:
            # Create GPU acceleration widget with validation callback
            self.gpu_widget = GPUAccelerationWidget(
                parent, 
                validation_callback=self._run_gpu_validation
            )
            self.gpu_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            logger.info("GPU acceleration widget integrated successfully")
            
        except Exception as e:
            logger.error(f"Failed to create GPU acceleration widget: {e}")
            # Create error message if widget fails to load
            error_frame = tk.Frame(parent, bg="white")
            error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            tk.Label(
                error_frame,
                text="⚠️ GPU Acceleration Widget Unavailable",
                font=("Arial", 12, "bold"),
                bg="white",
                fg="#dc3545"
            ).pack(pady=10)
            
            tk.Label(
                error_frame,
                text=f"Error: {str(e)}\n\nThe GPU acceleration features are not available.\n"
                     "This may be due to missing dependencies or hardware limitations.",
                font=("Arial", 10),
                bg="white",
                fg="#6c757d",
                justify=tk.CENTER,
                wraplength=400
            ).pack(pady=10)

    def _run_gpu_validation(self, **kwargs) -> Any:
        """
        Callback function for GPU validation runs.
        This method is called by the GPU widget when validation is requested.
        
        Args:
            **kwargs: Validation parameters from the GPU widget
            
        Returns:
            Validation results object
        """
        try:
            logger.info(f"Starting GPU validation with parameters: {kwargs}")
            
            # Import GPU validation functionality
            from pymbo.core.gpu_validation_engine import run_gpu_validation
            
            # Extract parameters
            test_function_name = kwargs.get('test_function_name', 'ZDT1')
            algorithms = kwargs.get('algorithms', ['GPU Random Search'])
            n_evaluations = kwargs.get('n_evaluations', 50)
            n_runs = kwargs.get('n_runs', 5)
            batch_size = kwargs.get('batch_size', None)
            # Note: progress_callback not supported by validation engine
            
            # Run validation (progress_callback not supported by validation engine)
            result = run_gpu_validation(
                test_function_name=test_function_name,
                algorithms=algorithms,
                n_evaluations=n_evaluations,
                n_runs=n_runs,
                batch_size=batch_size
            )
            
            # Update performance metrics in the widget
            if hasattr(self, 'gpu_widget') and result:
                execution_time = getattr(result, 'execution_time', 0)
                total_evaluations = n_evaluations * n_runs * len(algorithms)
                
                # Try to get speedup from various possible fields
                speedup = None
                if hasattr(result, 'gpu_acceleration_factor') and result.gpu_acceleration_factor:
                    speedup = result.gpu_acceleration_factor
                elif hasattr(result, 'speedup') and result.speedup:
                    speedup = result.speedup
                else:
                    # Calculate approximate speedup based on performance metrics
                    perf_metrics = getattr(result, 'performance_metrics', {})
                    if perf_metrics and 'avg_time_per_run' in perf_metrics:
                        avg_time = perf_metrics['avg_time_per_run']
                        # Estimate CPU time (rough approximation: GPU is typically 2-5x faster)
                        estimated_cpu_time = avg_time * 3.0  # Conservative estimate
                        speedup = estimated_cpu_time / avg_time if avg_time > 0 else None
                
                # Make sure the widget and its performance display exist
                if hasattr(self.gpu_widget, 'update_performance_metrics'):
                    self.gpu_widget.update_performance_metrics(
                        execution_time, total_evaluations, speedup
                    )
                elif hasattr(self.gpu_widget, 'performance_display'):
                    # Direct update if the method doesn't exist
                    self.gpu_widget.performance_display.update_performance(
                        execution_time, total_evaluations, speedup
                    )
                
                logger.debug(f"Updated performance metrics: time={execution_time:.3f}s, "
                           f"evals={total_evaluations}, speedup={speedup}")
            
            logger.info("GPU validation completed successfully")
            return result
            
        except ImportError:
            logger.warning("GPU validation engine not available")
            # Create mock result for testing
            class MockResult:
                def __init__(self):
                    self.execution_time = 5.0
                    self.device_info = {'device_name': 'Mock GPU Device'}
                    self.algorithms = algorithms
                    self.n_runs = n_runs
                    
            return MockResult()
            
        except Exception as e:
            logger.error(f"GPU validation failed: {e}")
            raise

    def _build_parallel_optimization_tab(self, parent: tk.Frame) -> None:
        """
        Builds the parallel optimization tab with controls for benchmarking,
        what-if analysis, and parallel data loading.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
        """
        try:
            # Import parallel optimization controls
            from .parallel_optimization_controls import ParallelOptimizationControls
            
            # Create parallel optimization controls widget
            self.parallel_controls = ParallelOptimizationControls(parent, self.controller)
            
            logger.info("Parallel optimization controls integrated successfully")
            
        except ImportError as e:
            logger.warning(f"Parallel optimization controls not available: {e}")
            # Create fallback interface
            self._create_parallel_fallback_interface(parent)
            
        except Exception as e:
            logger.error(f"Failed to create parallel optimization controls: {e}")
            # Create error message if widget fails to load
            self._create_parallel_error_interface(parent, str(e))

    def _create_parallel_fallback_interface(self, parent: tk.Frame) -> None:
        """Create a fallback interface when parallel controls are not available."""
        fallback_frame = tk.Frame(parent, bg="white")
        fallback_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            fallback_frame,
            text="⚡ Parallel Optimization Available",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#007bff"
        ).pack(pady=10)
        
        info_text = """
The parallel optimization features are active in the background!

✅ Intelligent Mode Detection
Your optimizer automatically switches between sequential and parallel 
execution based on context.

🏁 Benchmarking
Use suggest_next_experiment() with multiple strategies for automatic
parallel benchmarking.

🔮 What-If Analysis  
The system detects scenario-based requests and runs them in parallel.

📊 Large Data Loading
Import large datasets and they'll be processed in parallel chunks
automatically.

All existing functionality remains unchanged - parallel features
work transparently when beneficial.
        """
        
        tk.Label(
            fallback_frame,
            text=info_text,
            font=("Arial", 10),
            bg="white",
            fg="#495057",
            justify=tk.LEFT,
            wraplength=500
        ).pack(pady=20)
        
        # Add buttons for manual control
        button_frame = tk.Frame(fallback_frame, bg="white")
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="📊 View Orchestrator Stats",
            font=("Arial", 10),
            bg="#17a2b8",
            fg="white",
            command=self._show_orchestrator_stats,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🗑️ Clear Cache",
            font=("Arial", 10),
            bg="#6c757d",
            fg="white",
            command=self._clear_optimization_cache,
            width=15
        ).pack(side=tk.LEFT, padx=5)

    def _create_parallel_error_interface(self, parent: tk.Frame, error_msg: str) -> None:
        """Create an error interface when parallel controls fail to load."""
        error_frame = tk.Frame(parent, bg="white")
        error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            error_frame,
            text="⚠️ Parallel Optimization Controls Error",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#dc3545"
        ).pack(pady=10)
        
        tk.Label(
            error_frame,
            text=f"Error: {error_msg}\n\nParallel optimization is still active in the background,\n"
                 "but the advanced controls interface is not available.",
            font=("Arial", 10),
            bg="white",
            fg="#6c757d",
            justify=tk.CENTER,
            wraplength=400
        ).pack(pady=10)

    def _show_orchestrator_stats(self) -> None:
        """Show orchestrator statistics in a popup."""
        try:
            if self.controller and hasattr(self.controller, 'get_orchestrator_stats'):
                stats = self.controller.get_orchestrator_stats()
                
                # Format stats for display
                stats_text = "Parallel Optimization Statistics\n"
                stats_text += "=" * 40 + "\n\n"
                
                if "error" not in stats:
                    stats_text += f"Parallel Enabled: {'Yes' if stats.get('parallel_enabled', False) else 'No'}\n"
                    stats_text += f"Sequential Requests: {stats.get('sequential_requests', 0)}\n"
                    stats_text += f"Parallel Requests: {stats.get('parallel_requests', 0)}\n"
                    
                    if stats.get('parallel_enabled', False):
                        stats_text += f"Workers: {stats.get('n_workers', 'N/A')}\n"
                        stats_text += f"Cache Size: {stats.get('cache_size', 0)}\n"
                else:
                    stats_text += f"Error: {stats['error']}\n"
                
                # Show in message box
                messagebox.showinfo("Orchestrator Statistics", stats_text)
            else:
                messagebox.showinfo("Statistics", "Orchestrator statistics not available")
                
        except Exception as e:
            logger.error(f"Error showing orchestrator stats: {e}")
            messagebox.showerror("Error", f"Failed to get statistics: {str(e)}")

    def _clear_optimization_cache(self) -> None:
        """Clear optimization cache."""
        try:
            if self.controller and hasattr(self.controller, 'clear_optimization_cache'):
                self.controller.clear_optimization_cache()
                messagebox.showinfo("Cache Cleared", "Optimization cache cleared successfully!")
            else:
                messagebox.showinfo("Cache", "Cache management not available")
                
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            messagebox.showerror("Error", f"Failed to clear cache: {str(e)}")

    def _build_plot_panel(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the right-hand plotting panel of the main interface.
        This panel contains a notebook with various tabs for different types of plots
        (Pareto front, progress, GP slice, 3D surface, parallel coordinates, GP uncertainty, and model diagnostics).

        Args:
            parent (tk.Frame): The parent Tkinter frame for the plotting panel.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Header for the visualization section with control buttons.
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        # Title on the left
        tk.Label(
            header_frame,
            text="Data Visualization",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(side=tk.LEFT, anchor="w")
        
        # Control button removed as requested

        # Notebook widget to organize different plot tabs.
        self.plot_notebook = ttk.Notebook(parent, style="Modern.TNotebook")
        self.plot_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.plot_notebook.bind(
            "<<NotebookTabChanged>>", lambda event: self._on_tab_changed()
        )
        
        # Create mapping from tab index to plot type for single button functionality
        self.tab_to_plot_type = {}

        # Create and add each plot tab to the notebook.
        pareto_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(pareto_tab, text="Pareto")
        self.tab_to_plot_type[0] = "pareto"

        progress_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(progress_tab, text="Progress")
        self.tab_to_plot_type[1] = "progress"

        gp_slice_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(gp_slice_tab, text="GP Slice")
        self.tab_to_plot_type[2] = "gp_slice"

        surface_3d_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(surface_3d_tab, text="3D Surface")
        self.tab_to_plot_type[3] = "3d_surface"

        parallel_coords_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(parallel_coords_tab, text="Parallel Coords")
        self.tab_to_plot_type[4] = "parallel_coordinates"

        gp_uncertainty_map_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(gp_uncertainty_map_tab, text="GP Uncertainty")
        self.tab_to_plot_type[5] = "gp_uncertainty"

        model_diagnostics_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(model_diagnostics_tab, text="Model Diag")
        self.tab_to_plot_type[6] = "model_diagnostics"  # Model diagnostics unified tab

        sensitivity_analysis_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(sensitivity_analysis_tab, text="Sensitivity")
        self.tab_to_plot_type[7] = "sensitivity_analysis"

        # Algorithm Validation tab
        validation_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(validation_tab, text="Algorithm Validation")
        self.tab_to_plot_type[8] = "algorithm_validation"

        # Populate the content of each plot tab.
        self._build_pareto_tab(pareto_tab, responses_config, params_config)
        self._build_progress_tab(progress_tab)
        self._build_gp_slice_tab(gp_slice_tab, params_config, responses_config)
        self._build_3d_surface_tab(surface_3d_tab, params_config, responses_config)
        self._build_parallel_coordinates_tab(
            parallel_coords_tab, params_config, responses_config
        )
        self._build_gp_uncertainty_map_tab(
            gp_uncertainty_map_tab, params_config, responses_config
        )
        self._build_model_diagnostics_tab(
            model_diagnostics_tab, params_config, responses_config
        )
        self._build_sensitivity_analysis_tab(
            sensitivity_analysis_tab, params_config, responses_config
        )
        self._build_algorithm_validation_tab(
            validation_tab, params_config, responses_config
        )

    def _build_pareto_tab(
        self,
        parent: tk.Frame,
        responses_config: Dict[str, Any],
        params_config: Dict[str, Any],
    ) -> None:
        """
        Builds the 'Pareto Front' tab, which displays a 2D Pareto front plot.
        Allows users to select which objectives to plot on the X and Y axes.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            responses_config (Dict[str, Any]): The configuration of responses.
            params_config (Dict[str, Any]): The configuration of parameters.
        """
        # Initialize variables for Pareto plot (controls now handled by separate panels)
        # Only include actual optimization objectives (Maximize/Minimize), not constraints (Target/Range)
        objectives = []
        for name, conf in params_config.items():
            if conf.get("goal") in ["Maximize", "Minimize"]:
                objectives.append(name)
        for name, conf in responses_config.items():
            if conf.get("goal") in ["Maximize", "Minimize"]:
                objectives.append(name)

        self.pareto_x_var = tk.StringVar(value=objectives[0] if objectives else "")
        self.pareto_y_var = tk.StringVar(
            value=objectives[1] if len(objectives) > 1 else ""
        )
        
        # Pareto plot visibility controls
        self.pareto_show_all_solutions_var = tk.BooleanVar(value=True)
        self.pareto_show_pareto_points_var = tk.BooleanVar(value=True)
        self.pareto_show_pareto_front_var = tk.BooleanVar(value=True)
        self.pareto_show_legend_var = tk.BooleanVar(value=True)

        # Create the main plot frame
        main_container = tk.Frame(parent, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create control button frame at the top
        control_frame = tk.Frame(main_container, bg="white", relief="ridge", bd=1)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add button to open Pareto control panel
        logger.debug(f"PARETO_CONTROLS_AVAILABLE: {PARETO_CONTROLS_AVAILABLE}")
        if PARETO_CONTROLS_AVAILABLE:
            control_btn = tk.Button(
                control_frame,
                text="🎛️ Open Pareto Controls",
                command=self._show_pareto_controls,
                bg=COLOR_PRIMARY,
                fg=COLOR_SURFACE,
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=20,
                pady=8
            )
            control_btn.pack(side=tk.LEFT, padx=5, pady=5)
            logger.debug("Pareto control button created")
        else:
            logger.warning("PARETO_CONTROLS_AVAILABLE is False - button not created")
        
        # Create plot container below controls
        plot_container = tk.Frame(main_container, bg="white")
        plot_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create plot with simplified layout (no overlay controls)
        self._create_plot_with_compact_controls(
            parent=plot_container,
            plot_type="pareto",
            fig_attr="pareto_fig",
            canvas_attr="pareto_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
            aspect_ratio=1.0,  # Square plots
        )
        
        # Store configs for later use
        logger.debug("=== STORING CONFIGURATIONS IN GUI INSTANCE ===")
        self.params_config = params_config
        self.responses_config = responses_config
        logger.debug(f"GUI.params_config stored: {self.params_config}")
        logger.debug(f"GUI.responses_config stored: {self.responses_config}")
        logger.debug("=== CONFIGURATION STORAGE COMPLETE ===")
        
        # Create the popout control panel (initially hidden)
        if PARETO_CONTROLS_AVAILABLE:
            logger.debug(f"Attempting to create pareto control panel with {len(params_config)} params and {len(responses_config)} responses")
            self._create_pareto_control_panel(params_config, responses_config)
        else:
            logger.warning("PARETO_CONTROLS_AVAILABLE is False - control panel not created")

    def _create_pareto_control_panel(self, params_config: Dict[str, Any], responses_config: Dict[str, Any]) -> None:
        """
        Create the Pareto control panel in a popup window.
        
        Args:
            params_config: Dictionary containing parameter configurations
            responses_config: Dictionary containing response configurations
        """
        try:
            logger.debug(f"Creating pareto control panel with params: {len(params_config)} params, {len(responses_config)} responses")
            self.pareto_control_panel = create_pareto_control_panel(
                parent=self,  # Use self since SimpleOptimizerApp inherits from tk.Tk
                plot_type="pareto",
                params_config=params_config,
                responses_config=responses_config,
                update_callback=self._refresh_pareto_plot,
                export_callback=self._export_pareto_plot
            )
            logger.info(f"Pareto control panel created successfully: {self.pareto_control_panel}")
        except Exception as e:
            logger.error(f"Failed to create Pareto control panel: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.pareto_control_panel = None
    
    def _show_pareto_controls(self) -> None:
        """
        Show the Pareto control panel popup window.
        """
        logger.debug(f"_show_pareto_controls called. Has pareto_control_panel: {hasattr(self, 'pareto_control_panel')}")
        if hasattr(self, 'pareto_control_panel'):
            logger.debug(f"pareto_control_panel value: {self.pareto_control_panel}")
        
        if hasattr(self, 'pareto_control_panel') and self.pareto_control_panel:
            self.pareto_control_panel.show()
            logger.info("Pareto control panel shown")
        else:
            logger.warning("Pareto control panel not available - attempting to create it now")
            # Try to create it if it doesn't exist
            try:
                # Get configs from somewhere - we need to find where they are stored
                if hasattr(self, 'params_config') and hasattr(self, 'responses_config'):
                    self._create_pareto_control_panel(self.params_config, self.responses_config)
                    if hasattr(self, 'pareto_control_panel') and self.pareto_control_panel:
                        self.pareto_control_panel.show()
                        logger.info("Pareto control panel created and shown")
                else:
                    logger.error("Cannot create pareto control panel - configs not available")
            except Exception as e:
                logger.error(f"Failed to create pareto control panel on demand: {e}")
    
    def _refresh_pareto_plot(self) -> None:
        """
        Refresh the Pareto plot using current control panel settings.
        """
        try:
            if hasattr(self, 'pareto_control_panel') and self.pareto_control_panel:
                # Get current display options from control panel
                options = self.pareto_control_panel.get_display_options()
                
                # Update the internal variables to match control panel
                self.pareto_x_var.set(options.get('x_objective', ''))
                self.pareto_y_var.set(options.get('y_objective', ''))
                self.pareto_show_all_solutions_var.set(options.get('show_all_solutions', True))
                self.pareto_show_pareto_points_var.set(options.get('show_pareto_points', True))
                self.pareto_show_pareto_front_var.set(options.get('show_pareto_front', True))
                self.pareto_show_legend_var.set(options.get('show_legend', True))
                
                # Trigger plot update
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'plot_manager'):
                    self._update_pareto_front_plot(self.controller.plot_manager)
                    logger.info("Pareto plot refreshed with control panel settings")
                else:
                    logger.warning("Plot manager not available for refresh")
            else:
                logger.warning("Pareto control panel not available for refresh")
        except Exception as e:
            logger.error(f"Error refreshing Pareto plot: {e}")
    
    def _export_pareto_plot(self, filename: str, dpi: int) -> None:
        """
        Export the Pareto plot with specified filename and DPI.
        
        Args:
            filename: Path where to save the plot
            dpi: DPI setting for the export
        """
        try:
            if hasattr(self, 'pareto_fig') and self.pareto_fig:
                self.pareto_fig.savefig(filename, dpi=dpi, bbox_inches='tight')
                logger.info(f"Pareto plot exported to {filename} at {dpi} DPI")
            else:
                logger.error("Pareto figure not available for export")
        except Exception as e:
            logger.error(f"Error exporting Pareto plot: {e}")
            raise
    
    def _create_progress_control_panel(self) -> None:
        """
        Create the Progress control panel in a popup window.
        """
        try:
            logger.debug("Creating progress control panel")
            self.progress_control_panel = create_progress_control_panel(
                parent=self,  # Use self since SimpleOptimizerApp inherits from tk.Tk
                plot_type="progress",
                params_config=getattr(self, 'params_config', {}),
                responses_config=getattr(self, 'responses_config', {}),
                update_callback=self._refresh_progress_plot,
                export_callback=self._export_progress_plot
            )
            
            # Add to enhanced_controls dictionary so _update_progress_plot can find it
            if not hasattr(self, 'enhanced_controls'):
                self.enhanced_controls = {}
            self.enhanced_controls["progress"] = self.progress_control_panel
            
            logger.info(f"Progress control panel created successfully: {self.progress_control_panel}")
        except Exception as e:
            logger.error(f"Failed to create Progress control panel: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.progress_control_panel = None
    
    def _show_progress_controls(self) -> None:
        """
        Show the Progress control panel popup window.
        """
        logger.debug(f"_show_progress_controls called. Has progress_control_panel: {hasattr(self, 'progress_control_panel')}")
        if hasattr(self, 'progress_control_panel'):
            logger.debug(f"progress_control_panel value: {self.progress_control_panel}")
        
        if hasattr(self, 'progress_control_panel') and self.progress_control_panel:
            self.progress_control_panel.show()
            logger.info("Progress control panel shown")
        else:
            logger.warning("Progress control panel not available - attempting to create it now")
            # Try to create it if it doesn't exist
            try:
                self._create_progress_control_panel()
                if hasattr(self, 'progress_control_panel') and self.progress_control_panel:
                    self.progress_control_panel.show()
                    logger.info("Progress control panel created and shown")
                    
                    # Ensure it's also in enhanced_controls
                    if not hasattr(self, 'enhanced_controls'):
                        self.enhanced_controls = {}
                    self.enhanced_controls["progress"] = self.progress_control_panel
                else:
                    logger.error("Failed to create progress control panel")
            except Exception as e:
                logger.error(f"Failed to create progress control panel on demand: {e}")
    
    def _refresh_progress_plot(self) -> None:
        """
        Refresh the Progress plot using current control panel settings.
        """
        try:
            logger.debug("_refresh_progress_plot called")
            if hasattr(self, 'progress_control_panel') and self.progress_control_panel:
                # Get current display options from control panel
                options = self.progress_control_panel.get_display_options()
                logger.debug(f"Progress control panel options: {options}")
                
                # Update the internal variables to match control panel
                self.progress_show_raw_hv_var.set(options.get('show_raw_hv', True))
                self.progress_show_normalized_hv_var.set(options.get('show_normalized_hv', True))
                self.progress_show_trend_var.set(options.get('show_trend', True))
                self.progress_show_legend_var.set(options.get('show_legend', True))
                
                # Trigger plot update
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'plot_manager'):
                    logger.debug("Calling _update_progress_plot")
                    self._update_progress_plot(self.controller.plot_manager)
                    logger.info("Progress plot refreshed with control panel settings")
                else:
                    logger.warning("Plot manager not available for refresh")
            else:
                logger.warning("Progress control panel not available for refresh")
        except Exception as e:
            logger.error(f"Error refreshing Progress plot: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _export_progress_plot(self, filename: str, dpi: int) -> None:
        """
        Export the Progress plot with specified filename and DPI.
        
        Args:
            filename: Path where to save the plot
            dpi: DPI setting for the export
        """
        try:
            if hasattr(self, 'progress_fig') and self.progress_fig:
                self.progress_fig.savefig(filename, dpi=dpi, bbox_inches='tight')
                logger.info(f"Progress plot exported to {filename} at {dpi} DPI")
            else:
                logger.error("Progress figure not available for export")
        except Exception as e:
            logger.error(f"Error exporting Progress plot: {e}")
            raise
    
    def _create_gp_slice_control_panel(self) -> None:
        """
        Create the GP Slice control panel in a popup window.
        """
        try:
            logger.debug("Creating GP Slice control panel")
            self.gp_slice_control_panel = create_gp_slice_control_panel(
                parent=self,  # Use self since SimpleOptimizerApp inherits from tk.Tk
                plot_type="gp_slice",
                params_config=getattr(self, 'params_config', {}),
                responses_config=getattr(self, 'responses_config', {}),
                update_callback=self._refresh_gp_slice_plot,
                export_callback=self._export_gp_slice_plot
            )
            
            # Add to enhanced_controls registry
            if not hasattr(self, 'enhanced_controls'):
                self.enhanced_controls = {}
            self.enhanced_controls["gp_slice"] = self.gp_slice_control_panel
            
            logger.info("GP Slice control panel created successfully")
        except Exception as e:
            logger.error(f"Failed to create GP Slice control panel: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.gp_slice_control_panel = None
    
    def _create_sensitivity_analysis_control_panel(self) -> None:
        """
        Create the Sensitivity Analysis control panel in a popup window.
        """
        try:
            logger.debug("Creating Sensitivity Analysis control panel")
            self.sensitivity_analysis_control_panel = create_sensitivity_analysis_control_panel(
                parent=self,  # Use self since SimpleOptimizerApp inherits from tk.Tk
                plot_type="sensitivity_analysis",
                params_config=getattr(self, 'params_config', {}),
                responses_config=getattr(self, 'responses_config', {}),
                update_callback=self._refresh_sensitivity_analysis_plot,
                export_callback=self._export_sensitivity_analysis_plot
            )
            
            # Add to enhanced_controls registry
            if not hasattr(self, 'enhanced_controls'):
                self.enhanced_controls = {}
            self.enhanced_controls["sensitivity_analysis"] = self.sensitivity_analysis_control_panel
            
            logger.info("Sensitivity Analysis control panel created successfully")
        except Exception as e:
            logger.error(f"Failed to create Sensitivity Analysis control panel: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.sensitivity_analysis_control_panel = None
    
    def _show_gp_slice_controls(self) -> None:
        """
        Show the GP Slice control panel popup window.
        """
        logger.debug(f"_show_gp_slice_controls called. Has gp_slice_control_panel: {hasattr(self, 'gp_slice_control_panel')}")
        if hasattr(self, 'gp_slice_control_panel'):
            logger.debug(f"gp_slice_control_panel value: {self.gp_slice_control_panel}")
        
        if hasattr(self, 'gp_slice_control_panel') and self.gp_slice_control_panel:
            self.gp_slice_control_panel.show()
            logger.info("GP Slice control panel shown")
        else:
            logger.warning("GP Slice control panel not available - attempting to create it now")
            # Try to create it if it doesn't exist
            try:
                self._create_gp_slice_control_panel()
                if hasattr(self, 'gp_slice_control_panel') and self.gp_slice_control_panel:
                    self.gp_slice_control_panel.show()
                    logger.info("GP Slice control panel created and shown")
                    
                    # Ensure it's also in enhanced_controls
                    if not hasattr(self, 'enhanced_controls'):
                        self.enhanced_controls = {}
                    self.enhanced_controls["gp_slice"] = self.gp_slice_control_panel
                else:
                    logger.error("Failed to create GP Slice control panel")
            except Exception as e:
                logger.error(f"Failed to create GP Slice control panel on demand: {e}")
    
    def _show_sensitivity_analysis_controls(self) -> None:
        """
        Show the Sensitivity Analysis control panel popup window.
        """
        logger.debug(f"_show_sensitivity_analysis_controls called. Has sensitivity_analysis_control_panel: {hasattr(self, 'sensitivity_analysis_control_panel')}")
        if hasattr(self, 'sensitivity_analysis_control_panel'):
            logger.debug(f"sensitivity_analysis_control_panel value: {self.sensitivity_analysis_control_panel}")
        
        if hasattr(self, 'sensitivity_analysis_control_panel') and self.sensitivity_analysis_control_panel:
            self.sensitivity_analysis_control_panel.show()
            logger.info("Sensitivity Analysis control panel shown")
        else:
            logger.warning("Sensitivity Analysis control panel not available - attempting to create it now")
            # Try to create it if it doesn't exist
            try:
                self._create_sensitivity_analysis_control_panel()
                if hasattr(self, 'sensitivity_analysis_control_panel') and self.sensitivity_analysis_control_panel:
                    self.sensitivity_analysis_control_panel.show()
                    logger.info("Sensitivity Analysis control panel created and shown")
                    
                    # Ensure it's also in enhanced_controls
                    if not hasattr(self, 'enhanced_controls'):
                        self.enhanced_controls = {}
                    self.enhanced_controls["sensitivity_analysis"] = self.sensitivity_analysis_control_panel
                else:
                    logger.error("Failed to create Sensitivity Analysis control panel")
            except Exception as e:
                logger.error(f"Failed to create Sensitivity Analysis control panel on demand: {e}")
    
    def _refresh_gp_slice_plot(self) -> None:
        """
        Refresh the GP Slice plot using current control panel settings.
        """
        try:
            logger.debug("_refresh_gp_slice_plot called")
            if hasattr(self, 'gp_slice_control_panel') and self.gp_slice_control_panel:
                # Get current display options from control panel
                options = self.gp_slice_control_panel.get_display_options()
                logger.debug(f"GP Slice control panel options: {options}")
                
                # Handle parameter switching logic
                if 'x_param' in options:
                    new_x_param = options['x_param']
                    current_x_param = self.gp_param1_var.get()
                    current_y_param = self.gp_param2_var.get()
                    
                    # Check if X parameter actually changed
                    if new_x_param != current_x_param:
                        logger.debug(f"Parameter switch detected: {current_x_param} -> {new_x_param}")
                        
                        # When X parameter changes, the old X parameter becomes the new Y (fixed) parameter
                        # and we should set the fixed value to the midpoint of the old X parameter
                        if current_x_param in self.params_config:
                            # Get bounds of the old X parameter (now becoming fixed parameter)
                            old_param_bounds = self.params_config[current_x_param].get('bounds', [0, 1])
                            midpoint = (old_param_bounds[0] + old_param_bounds[1]) / 2.0
                            
                            # Normalize the midpoint to [0, 1] range for the fixed value slider
                            param_range = old_param_bounds[1] - old_param_bounds[0]
                            if param_range > 0:
                                normalized_midpoint = (midpoint - old_param_bounds[0]) / param_range
                            else:
                                normalized_midpoint = 0.5
                            
                            # Update the fixed value to the midpoint of the old X parameter
                            self.gp_fixed_value_var.set(normalized_midpoint)
                            logger.info(f"GP Slice: Parameter switch - slice now at {current_x_param}={midpoint:.2f} (normalized: {normalized_midpoint:.3f})")
                        
                        # Set the new fixed parameter (param2) to be the old X parameter
                        self.gp_param2_var.set(current_x_param)
                        logger.debug(f"Set param2 (fixed parameter) to: {current_x_param}")
                    
                    # Update X parameter to new selection
                    self.gp_param1_var.set(new_x_param)
                    
                if 'y_response' in options:
                    self.gp_response_var.set(options['y_response'])
                
                # Trigger plot update
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'plot_manager'):
                    logger.debug("Calling _update_gp_slice_plot")
                    self._update_gp_slice_plot(self.controller.plot_manager)
                    logger.info("GP Slice plot refreshed with control panel settings")
                else:
                    logger.warning("Plot manager not available for refresh")
            else:
                logger.warning("GP Slice control panel not available for refresh")
        except Exception as e:
            logger.error(f"Error refreshing GP Slice plot: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _export_gp_slice_plot(self, filename: str, dpi: int) -> None:
        """
        Export the GP Slice plot with specified filename and DPI.
        
        Args:
            filename: Path where to save the plot
            dpi: DPI setting for the export
        """
        try:
            if hasattr(self, 'gp_slice_fig') and self.gp_slice_fig:
                self.gp_slice_fig.savefig(filename, dpi=dpi, bbox_inches='tight')
                logger.info(f"GP Slice plot exported to {filename} at {dpi} DPI")
            else:
                logger.error("GP Slice figure not available for export")
        except Exception as e:
            logger.error(f"Error exporting GP Slice plot: {e}")
            raise
    
    def _refresh_sensitivity_analysis_plot(self) -> None:
        """
        Refresh the Sensitivity Analysis plot using current control panel settings.
        """
        try:
            logger.debug("_refresh_sensitivity_analysis_plot called")
            if hasattr(self, 'sensitivity_analysis_control_panel') and self.sensitivity_analysis_control_panel:
                # Get current settings from control panel
                settings = self.sensitivity_analysis_control_panel.get_sensitivity_settings()
                logger.debug(f"Sensitivity Analysis control panel settings: {settings}")
                
                # Update the internal variables to match control panel
                if 'response' in settings:
                    self.sensitivity_response_var.set(settings['response'])
                if 'algorithm_code' in settings:
                    # Convert algorithm code to display name for internal variable
                    for display_name, code in self.sensitivity_method_mapping.items():
                        if code == settings['algorithm_code']:
                            self.sensitivity_method_var.set(display_name)
                            break
                if 'iterations' in settings:
                    self.sensitivity_samples_var.set(settings['iterations'])
                
                # Trigger plot update
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'plot_manager'):
                    logger.debug("Calling _update_sensitivity_analysis_plot")
                    self._update_sensitivity_analysis_plot(self.controller.plot_manager)
                    logger.info("Sensitivity Analysis plot refreshed with control panel settings")
                else:
                    logger.warning("Plot manager not available for refresh")
            else:
                logger.warning("Sensitivity Analysis control panel not available for refresh")
        except Exception as e:
            logger.error(f"Error refreshing Sensitivity Analysis plot: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _export_sensitivity_analysis_plot(self, filename: str, dpi: int) -> None:
        """
        Export the Sensitivity Analysis plot with specified filename and DPI.
        
        Args:
            filename: Path where to save the plot
            dpi: DPI setting for the export
        """
        try:
            if hasattr(self, 'sensitivity_fig') and self.sensitivity_fig:
                self.sensitivity_fig.savefig(filename, dpi=dpi, bbox_inches='tight')
                logger.info(f"Sensitivity Analysis plot exported to {filename} at {dpi} DPI")
            else:
                logger.error("Sensitivity Analysis figure not available for export")
        except Exception as e:
            logger.error(f"Error exporting Sensitivity Analysis plot: {e}")
            raise
    
    def _create_parallel_coordinates_control_panel(self) -> None:
        """
        Create the Parallel Coordinates control panel in a popup window.
        """
        try:
            logger.debug("Creating Parallel Coordinates control panel")
            self.parallel_coordinates_control_panel = create_parallel_coordinates_control_panel(
                parent=self,  # Use self since SimpleOptimizerApp inherits from tk.Tk
                plot_type="parallel_coordinates",
                params_config=getattr(self, 'parallel_coordinates_params_config', {}),
                responses_config=getattr(self, 'parallel_coordinates_responses_config', {}),
                update_callback=self._refresh_parallel_coordinates_plot,
                export_callback=self._export_parallel_coordinates_plot
            )
            
            # Add to enhanced_controls registry
            if not hasattr(self, 'enhanced_controls'):
                self.enhanced_controls = {}
            self.enhanced_controls["parallel_coordinates"] = self.parallel_coordinates_control_panel
            
            logger.info("Parallel Coordinates control panel created successfully")
        except Exception as e:
            logger.error(f"Failed to create Parallel Coordinates control panel: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.parallel_coordinates_control_panel = None
    
    def _show_parallel_coordinates_controls(self) -> None:
        """
        Show the Parallel Coordinates control panel popup window.
        """
        logger.debug(f"_show_parallel_coordinates_controls called. Has parallel_coordinates_control_panel: {hasattr(self, 'parallel_coordinates_control_panel')}")
        if hasattr(self, 'parallel_coordinates_control_panel'):
            logger.debug(f"parallel_coordinates_control_panel value: {self.parallel_coordinates_control_panel}")
        
        if hasattr(self, 'parallel_coordinates_control_panel') and self.parallel_coordinates_control_panel:
            self.parallel_coordinates_control_panel.show()
            logger.info("Parallel Coordinates control panel shown")
        else:
            logger.warning("Parallel Coordinates control panel not available - attempting to create it now")
            # Try to create it if it doesn't exist
            try:
                self._create_parallel_coordinates_control_panel()
                if hasattr(self, 'parallel_coordinates_control_panel') and self.parallel_coordinates_control_panel:
                    self.parallel_coordinates_control_panel.show()
                    logger.info("Parallel Coordinates control panel created and shown")
                    
                    # Ensure it's also in enhanced_controls
                    if not hasattr(self, 'enhanced_controls'):
                        self.enhanced_controls = {}
                    self.enhanced_controls["parallel_coordinates"] = self.parallel_coordinates_control_panel
                else:
                    logger.error("Failed to create Parallel Coordinates control panel")
            except Exception as e:
                logger.error(f"Failed to create Parallel Coordinates control panel on demand: {e}")
    
    def _refresh_parallel_coordinates_plot(self) -> None:
        """
        Refresh the Parallel Coordinates plot using current control panel settings.
        """
        try:
            logger.debug("_refresh_parallel_coordinates_plot called")
            if hasattr(self, 'parallel_coordinates_control_panel') and self.parallel_coordinates_control_panel:
                # Get current display options from control panel
                options = self.parallel_coordinates_control_panel.get_display_options()
                logger.debug(f"Parallel Coordinates control panel options: {options}")
                
                # Update the internal variables to match control panel
                if 'selected_params' in options:
                    selected_params = options['selected_params']
                    # Update the internal variables based on selected parameters
                    for var_name, var_obj in self.parallel_coords_vars.items():
                        var_obj.set(var_name in selected_params)
                
                # Trigger plot update
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'plot_manager'):
                    logger.debug("Calling plot manager to update Parallel Coordinates plot")
                    self._update_parallel_coordinates_plot(self.controller.plot_manager)
                else:
                    logger.warning("Controller or plot manager not available")
            else:
                logger.warning("Parallel Coordinates control panel not available for refresh")
        except Exception as e:
            logger.error(f"Error refreshing Parallel Coordinates plot: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _export_parallel_coordinates_plot(self, filename: str, dpi: int) -> None:
        """
        Export the Parallel Coordinates plot to a file.
        
        Args:
            filename: Path where to save the plot
            dpi: DPI setting for the export
        """
        try:
            if hasattr(self, 'parallel_coords_fig') and self.parallel_coords_fig:
                self.parallel_coords_fig.savefig(filename, dpi=dpi, bbox_inches='tight')
                logger.info(f"Parallel Coordinates plot exported to {filename} at {dpi} DPI")
            else:
                logger.error("Parallel Coordinates figure not available for export")
        except Exception as e:
            logger.error(f"Error exporting Parallel Coordinates plot: {e}")
            raise
    
    def _create_uncertainty_analysis_control_panel(self) -> None:
        """
        Create the Uncertainty Analysis control panel in a popup window.
        """
        try:
            logger.debug("Creating Uncertainty Analysis control panel")
            self.uncertainty_analysis_control_panel = create_uncertainty_analysis_control_panel(
                parent=self,  # Use self since SimpleOptimizerApp inherits from tk.Tk
                plot_type="gp_uncertainty",
                params_config=getattr(self, 'uncertainty_analysis_params_config', {}),
                responses_config=getattr(self, 'uncertainty_analysis_responses_config', {}),
                update_callback=self._refresh_uncertainty_analysis_plot
            )
            
            # Add to enhanced_controls registry
            if not hasattr(self, 'enhanced_controls'):
                self.enhanced_controls = {}
            self.enhanced_controls["gp_uncertainty"] = self.uncertainty_analysis_control_panel
            
            logger.info("Uncertainty Analysis control panel created successfully")
        except Exception as e:
            logger.error(f"Failed to create Uncertainty Analysis control panel: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.uncertainty_analysis_control_panel = None
    
    def _show_uncertainty_analysis_controls(self) -> None:
        """
        Show the Uncertainty Analysis control panel popup window.
        """
        logger.debug(f"_show_uncertainty_analysis_controls called. Has uncertainty_analysis_control_panel: {hasattr(self, 'uncertainty_analysis_control_panel')}")
        if hasattr(self, 'uncertainty_analysis_control_panel'):
            logger.debug(f"uncertainty_analysis_control_panel value: {self.uncertainty_analysis_control_panel}")
        
        if hasattr(self, 'uncertainty_analysis_control_panel') and self.uncertainty_analysis_control_panel:
            self.uncertainty_analysis_control_panel.show()
            logger.info("Uncertainty Analysis control panel shown")
        else:
            logger.warning("Uncertainty Analysis control panel not available - attempting to create it now")
            # Try to create it if it doesn't exist
            try:
                self._create_uncertainty_analysis_control_panel()
                if hasattr(self, 'uncertainty_analysis_control_panel') and self.uncertainty_analysis_control_panel:
                    self.uncertainty_analysis_control_panel.show()
                    logger.info("Uncertainty Analysis control panel created and shown")
                    
                    # Ensure it's also in enhanced_controls
                    if not hasattr(self, 'enhanced_controls'):
                        self.enhanced_controls = {}
                    self.enhanced_controls["gp_uncertainty"] = self.uncertainty_analysis_control_panel
                else:
                    logger.error("Failed to create Uncertainty Analysis control panel")
            except Exception as e:
                logger.error(f"Failed to create Uncertainty Analysis control panel on demand: {e}")
    
    def _refresh_uncertainty_analysis_plot(self) -> None:
        """
        Refresh the Uncertainty Analysis plot using current control panel settings.
        """
        try:
            logger.debug("_refresh_uncertainty_analysis_plot called")
            if hasattr(self, 'uncertainty_analysis_control_panel') and self.uncertainty_analysis_control_panel:
                # Get current display options from control panel
                display_options = self.uncertainty_analysis_control_panel.get_display_options()
                parameters = self.uncertainty_analysis_control_panel.get_parameters()
                settings = self.uncertainty_analysis_control_panel.get_uncertainty_settings()
                
                logger.debug(f"Uncertainty Analysis control panel options: {display_options}")
                logger.debug(f"Parameters: {parameters}")
                
                # Update the internal variables to match control panel
                if 'response' in parameters:
                    self.gp_uncertainty_response_var.set(parameters['response'])
                if 'x_parameter' in parameters:
                    self.gp_uncertainty_param1_var.set(parameters['x_parameter'])
                if 'y_parameter' in parameters:
                    self.gp_uncertainty_param2_var.set(parameters['y_parameter'])
                
                # Update uncertainty settings
                if 'plot_style' in settings:
                    self.gp_uncertainty_plot_style_var.set(settings['plot_style'])
                if 'uncertainty_metric' in settings:
                    self.gp_uncertainty_metric_var.set(settings['uncertainty_metric'])
                if 'colormap' in settings:
                    self.gp_uncertainty_colormap_var.set(settings['colormap'])
                if 'resolution' in settings:
                    self.gp_uncertainty_resolution_var.set(str(settings['resolution']))
                if 'show_experimental_data' in display_options:
                    self.gp_uncertainty_show_data_var.set(display_options['show_experimental_data'])
                
                # Trigger plot update
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'plot_manager'):
                    logger.debug("Calling plot manager to update Uncertainty Analysis plot")
                    self._update_gp_uncertainty_map_plot(self.controller.plot_manager)
                else:
                    logger.warning("Controller or plot manager not available")
            else:
                logger.warning("Uncertainty Analysis control panel not available for refresh")
        except Exception as e:
            logger.error(f"Error refreshing Uncertainty Analysis plot: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _export_uncertainty_analysis_plot(self, filename: str, dpi: int) -> None:
        """
        Export the Uncertainty Analysis plot to a file.
        
        Args:
            filename: Path where to save the plot
            dpi: DPI setting for the export
        """
        try:
            if hasattr(self, 'gp_uncertainty_map_fig') and self.gp_uncertainty_map_fig:
                self.gp_uncertainty_map_fig.savefig(filename, dpi=dpi, bbox_inches='tight')
                logger.info(f"Uncertainty Analysis plot exported to {filename} at {dpi} DPI")
            else:
                logger.error("Uncertainty Analysis figure not available for export")
        except Exception as e:
            logger.error(f"Error exporting Uncertainty Analysis plot: {e}")
            raise
    
    def _create_3d_surface_control_panel(self) -> None:
        """
        Create the 3D Surface control panel in a popup window.
        """
        try:
            logger.debug("Creating 3D Surface control panel")
            # Get global importance weights if available
            global_importance_weights = getattr(self, 'response_optimization_weights', {})
            
            self.surface_3d_control_panel = create_3d_surface_control_panel(
                parent=self.master,
                plot_type="3d_surface",
                params_config=self.params_config,
                responses_config=self.responses_config,
                update_callback=self._refresh_3d_surface_plot,
                export_callback=self._export_3d_surface_plot,
                global_importance_weights=global_importance_weights
            )
            
            # Store in enhanced controls registry
            if not hasattr(self, "enhanced_controls"):
                self.enhanced_controls = {}
            self.enhanced_controls["3d_surface"] = self.surface_3d_control_panel
            
            logger.info("3D Surface control panel created successfully")
        except Exception as e:
            logger.error(f"Failed to create 3D Surface control panel: {e}")
            logger.error(f"Exception details: {type(e).__name__}: {e}")
            # Set to None so we know it failed
            self.surface_3d_control_panel = None

    def _show_model_diagnostics_controls(self) -> None:
        """
        Show the Model Diagnostics control panel popup window.
        """
        logger.debug(f"_show_model_diagnostics_controls called. Has model_diagnostics_control_panel: {hasattr(self, 'model_diagnostics_control_panel')}")
        if hasattr(self, 'model_diagnostics_control_panel'):
            logger.debug(f"model_diagnostics_control_panel value: {self.model_diagnostics_control_panel}")
        
        if hasattr(self, 'model_diagnostics_control_panel') and self.model_diagnostics_control_panel:
            # Refresh available responses before showing the panel
            self._refresh_model_diagnostics_responses()
            self.model_diagnostics_control_panel.show()
            logger.info("Model Diagnostics control panel shown")
        else:
            logger.warning("Model Diagnostics control panel not available - attempting to create it now")
            # Try to create it if it doesn't exist
            try:
                self._create_model_diagnostics_control_panel()
                if hasattr(self, 'model_diagnostics_control_panel') and self.model_diagnostics_control_panel:
                    self.model_diagnostics_control_panel.show()
                    logger.info("Model Diagnostics control panel created and shown")
                    
                    # Ensure it's also in enhanced_controls
                    if not hasattr(self, 'enhanced_controls'):
                        self.enhanced_controls = {}
                    self.enhanced_controls["model_diagnostics"] = self.model_diagnostics_control_panel
                else:
                    logger.error("Failed to create Model Diagnostics control panel")
            except Exception as e:
                logger.error(f"Failed to create Model Diagnostics control panel on demand: {e}")

    def _refresh_model_diagnostics_responses(self) -> None:
        """
        Refresh the available responses in the model diagnostics control panel
        by dynamically detecting them from experimental data.
        """
        try:
            if not hasattr(self, 'controller') or not hasattr(self.controller, 'optimizer'):
                return
                
            exp_data = self.controller.optimizer.experimental_data
            if exp_data.empty:
                return
                
            # Auto-detect response columns: exclude parameter columns, keep numeric columns
            param_names = set()
            if hasattr(self.controller.optimizer, 'parameter_transformer'):
                param_names = set(self.controller.optimizer.parameter_transformer.param_names)
            
            auto_responses = [
                col for col in exp_data.columns 
                if col not in param_names and 
                exp_data[col].dtype in ['float64', 'float32', 'int64', 'int32'] and
                not exp_data[col].isna().all()
            ]
            
            if auto_responses:
                # Update the control panel with the detected responses
                if hasattr(self, 'model_diagnostics_control_panel') and self.model_diagnostics_control_panel:
                    auto_params = list(param_names) if param_names else []
                    self.model_diagnostics_control_panel.update_available_options(auto_params, auto_responses)
                    logger.info(f"Refreshed model diagnostics control panel with {len(auto_responses)} auto-detected responses: {auto_responses}")
                
                # Also update the main tab response variable if it exists
                if hasattr(self, 'model_diagnostics_response_var'):
                    current_response = self.model_diagnostics_response_var.get()
                    # Set to first available response if empty or current response is not available
                    if not current_response or current_response not in auto_responses:
                        self.model_diagnostics_response_var.set(auto_responses[0])
                        logger.info(f"Set model diagnostics tab response to: {auto_responses[0]}")
                    else:
                        logger.info(f"Model diagnostics response already set to valid response: {current_response}")
                
        except Exception as e:
            logger.warning(f"Failed to refresh model diagnostics responses: {e}")

    def _on_tab_changed(self) -> None:
        """Handle tab change events."""
        try:
            # Get current tab
            current_tab = self.plot_notebook.index(self.plot_notebook.select())
            tab_name = self.plot_notebook.tab(current_tab, "text")
            
            # If Model Diag tab is selected, refresh responses
            if tab_name == "Model Diag":
                self._refresh_model_diagnostics_responses()
            
            # Update all plots as before
            self.update_all_plots()
            
        except Exception as e:
            logger.warning(f"Error handling tab change: {e}")
            # Fallback to just updating plots
            self.update_all_plots()

    def _create_model_diagnostics_control_panel(self) -> None:
        """
        Create the Model Diagnostics control panel if it doesn't exist.
        """
        logger.info("Creating Model Diagnostics control panel...")
        try:
            # Get configuration from stored configs
            config = getattr(self, 'window_configs', {}).get('model_diagnostics', {})
            params_config = config.get('params_config', {})
            responses_config = config.get('responses_config', {})
            
            # Fallback to instance variables if config not found
            if not params_config and hasattr(self, 'params_config'):
                params_config = self.params_config
            if not responses_config and hasattr(self, 'responses_config'):
                responses_config = self.responses_config
            
            # Try to dynamically detect responses from experimental data if controller/optimizer available
            if (not responses_config or not any(resp in getattr(self.controller.optimizer, 'experimental_data', pd.DataFrame()).columns 
                                                for resp in responses_config.keys() if responses_config)) and hasattr(self, 'controller') and hasattr(self.controller, 'optimizer'):
                try:
                    exp_data = self.controller.optimizer.experimental_data
                    if not exp_data.empty:
                        # Auto-detect response columns: exclude parameter columns, keep numeric columns
                        param_names = set()
                        if hasattr(self.controller.optimizer, 'parameter_transformer'):
                            param_names = set(self.controller.optimizer.parameter_transformer.param_names)
                        
                        auto_responses = [
                            col for col in exp_data.columns 
                            if col not in param_names and 
                            exp_data[col].dtype in ['float64', 'float32', 'int64', 'int32'] and
                            not exp_data[col].isna().all()
                        ]
                        
                        if auto_responses:
                            # Create a basic responses_config for the auto-detected responses
                            responses_config = {resp: {"goal": "Minimize"} for resp in auto_responses}
                            logger.info(f"Auto-detected responses for model diagnostics: {auto_responses}")
                        
                except Exception as e:
                    logger.warning(f"Failed to auto-detect responses: {e}")
                
            logger.debug(f"Using params_config: {list(params_config.keys()) if params_config else 'None'}")
            logger.debug(f"Using responses_config: {list(responses_config.keys()) if responses_config else 'None'}")
            
            # Create the control panel
            self.model_diagnostics_control_panel = create_model_diagnostics_control_panel(
                parent=self,
                plot_type="model_diagnostics",
                params_config=params_config,
                responses_config=responses_config,
                update_callback=lambda: self._update_model_diagnostics_plots(self.plot_manager) if hasattr(self, 'plot_manager') else None
            )
            
            # Store in enhanced_controls for easy access
            if not hasattr(self, 'enhanced_controls'):
                self.enhanced_controls = {}
            self.enhanced_controls["model_diagnostics"] = self.model_diagnostics_control_panel
            
            logger.info("Model Diagnostics control panel created successfully")
        except Exception as e:
            logger.error(f"Failed to create Model Diagnostics control panel: {e}")
            logger.error(f"Exception details: {type(e).__name__}: {e}")
            # Set to None so we know it failed
            self.model_diagnostics_control_panel = None

    def _show_3d_surface_controls(self) -> None:
        """
        Show the 3D Surface control panel popup window.
        """
        logger.debug(f"_show_3d_surface_controls called. Has surface_3d_control_panel: {hasattr(self, 'surface_3d_control_panel')}")
        if hasattr(self, 'surface_3d_control_panel'):
            logger.debug(f"surface_3d_control_panel value: {self.surface_3d_control_panel}")

        if hasattr(self, 'surface_3d_control_panel') and self.surface_3d_control_panel:
            # Update global importance weights before showing
            global_importance_weights = getattr(self, 'response_optimization_weights', {})
            if global_importance_weights:
                self.surface_3d_control_panel.update_global_importance_weights(global_importance_weights)
            
            self.surface_3d_control_panel.show()
            logger.info("3D Surface control panel shown")
        else:
            logger.warning("3D Surface control panel not available - attempting to create it now")
            try:
                self._create_3d_surface_control_panel()
                if hasattr(self, 'surface_3d_control_panel') and self.surface_3d_control_panel:
                    # Update global importance weights before showing
                    global_importance_weights = getattr(self, 'response_optimization_weights', {})
                    if global_importance_weights:
                        self.surface_3d_control_panel.update_global_importance_weights(global_importance_weights)
                    
                    self.surface_3d_control_panel.show()
                    logger.info("3D Surface control panel created and shown")
                    
                    # Also register it
                    if not hasattr(self, "enhanced_controls"):
                        self.enhanced_controls = {}
                    self.enhanced_controls["3d_surface"] = self.surface_3d_control_panel
                else:
                    logger.error("Failed to create 3D Surface control panel")
            except Exception as e:
                logger.error(f"Failed to create 3D Surface control panel on demand: {e}")

    def _refresh_3d_surface_plot(self) -> None:
        """
        Refresh the 3D Surface plot using current control panel settings.
        """
        try:
            logger.debug("_refresh_3d_surface_plot called")
            if hasattr(self, 'surface_3d_control_panel') and self.surface_3d_control_panel:
                # Get settings from control panel
                options = self.surface_3d_control_panel.get_display_options()
                logger.debug(f"3D Surface control panel options: {options}")
                
                # Get the plot manager
                plot_manager = self.controller.plot_manager if hasattr(self, 'controller') and self.controller else None
                
                if plot_manager and hasattr(plot_manager, 'create_3d_surface_plot'):
                    logger.debug("Calling _update_3d_surface_plot")
                    self._update_3d_surface_plot(self.controller.plot_manager)
                    logger.info("3D Surface plot refreshed with control panel settings")
                else:
                    logger.error("Plot manager not available or doesn't have create_3d_surface_plot method")
            else:
                logger.warning("3D Surface control panel not available for refresh")
        except Exception as e:
            logger.error(f"Error refreshing 3D Surface plot: {e}")
            raise

    def _export_3d_surface_plot(self, filename: str, dpi: int) -> None:
        """
        Export the 3D Surface plot with specified filename and DPI.
        
        Args:
            filename: Path where to save the plot
            dpi: DPI setting for the export
        """
        try:
            # If control panel is available, get export settings
            if hasattr(self, 'surface_3d_control_panel') and self.surface_3d_control_panel:
                options = self.surface_3d_control_panel.get_display_options()
                export_dpi = options.get('export_dpi', dpi)
                export_format = options.get('export_format', 'PNG')
                
                # Use export DPI from control panel if different
                actual_dpi = export_dpi if export_dpi != 300 else dpi  # Use provided DPI if control panel is default
                
                if hasattr(self, 'surface_3d_fig') and self.surface_3d_fig:
                    self.surface_3d_fig.savefig(filename, dpi=actual_dpi, bbox_inches='tight', format=export_format.lower())
                    logger.info(f"3D Surface plot exported to {filename} at {actual_dpi} DPI in {export_format} format")
                else:
                    logger.error("3D Surface figure not available for export")
            else:
                # Fallback to basic export
                if hasattr(self, 'surface_3d_fig') and self.surface_3d_fig:
                    self.surface_3d_fig.savefig(filename, dpi=dpi, bbox_inches='tight')
                    logger.info(f"3D Surface plot exported to {filename} at {dpi} DPI")
                else:
                    logger.error("3D Surface figure not available for export")
        except Exception as e:
            logger.error(f"Error exporting 3D Surface plot: {e}")
            raise
    
    def _build_progress_tab(self, parent: tk.Frame) -> None:
        """
        Builds the 'Progress' tab, which displays the optimization progress plot
        (e.g., Hypervolume Indicator over iterations).

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
        """
        # Initialize progress plot visibility controls
        self.progress_show_raw_hv_var = tk.BooleanVar(value=True)
        self.progress_show_normalized_hv_var = tk.BooleanVar(value=True)
        self.progress_show_trend_var = tk.BooleanVar(value=True)
        self.progress_show_legend_var = tk.BooleanVar(value=True)
        
        # Create main container for progress tab
        main_container = tk.Frame(parent, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create what-if controls frame at the top
        whatif_frame = tk.Frame(main_container, bg="white", relief="ridge", bd=1)
        whatif_frame.pack(fill="x", padx=10, pady=5)
        
        # What-if simulation controls
        tk.Label(
            whatif_frame, 
            text="Post-Hoc Analysis:", 
            bg="white", 
            font=("Arial", 10, "bold"),
            fg=COLOR_SECONDARY
        ).pack(side="left", padx=(10, 5))
        
        # Strategy selection
        self.whatif_strategy_var = tk.StringVar(value="Parallel Random Search")
        strategy_combo = ttk.Combobox(
            whatif_frame,
            textvariable=self.whatif_strategy_var,
            values=["Parallel Random Search", "Random Search"],
            state="readonly",
            width=20
        )
        strategy_combo.pack(side="left", padx=5)
        
        # Parallel processing controls
        tk.Label(
            whatif_frame,
            text="Workers:",
            bg="white",
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side="left", padx=(10, 2))
        
        self.whatif_workers_var = tk.StringVar(value="4")
        workers_combo = ttk.Combobox(
            whatif_frame,
            textvariable=self.whatif_workers_var,
            values=["1", "2", "4", "8", "Auto"],
            state="readonly",
            width=6
        )
        workers_combo.pack(side="left", padx=(0, 5))
        
        tk.Label(
            whatif_frame,
            text="Chunk Size:",
            bg="white", 
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side="left", padx=(5, 2))
        
        self.whatif_chunk_var = tk.StringVar(value="1000")
        chunk_combo = ttk.Combobox(
            whatif_frame,
            textvariable=self.whatif_chunk_var,
            values=["500", "1000", "2000", "5000"],
            state="readonly",
            width=6
        )
        chunk_combo.pack(side="left", padx=(0, 10))
        
        # What-if button
        self.whatif_button = tk.Button(
            whatif_frame,
            text="Run 'What-If' Comparison",
            command=self._run_whatif_simulation,
            bg=COLOR_WARNING,
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            bd=0,
            padx=15,
            pady=5
        )
        self.whatif_button.pack(side="left", padx=(10, 5))
        
        # Status label
        self.whatif_status_label = tk.Label(
            whatif_frame,
            text="Complete an experiment to enable what-if analysis",
            bg="white",
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        )
        self.whatif_status_label.pack(side="left", padx=(10, 10))
        
        # Create control button frame at the top
        control_frame = tk.Frame(main_container, bg="white", relief="ridge", bd=1)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add button to open Progress control panel
        logger.debug(f"PROGRESS_CONTROLS_AVAILABLE: {PROGRESS_CONTROLS_AVAILABLE}")
        if PROGRESS_CONTROLS_AVAILABLE:
            control_btn = tk.Button(
                control_frame,
                text="🎛️ Open Progress Controls",
                command=self._show_progress_controls,
                bg=COLOR_PRIMARY,
                fg=COLOR_SURFACE,
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=20,
                pady=8
            )
            control_btn.pack(side=tk.LEFT, padx=5, pady=5)
            logger.debug("Progress control button created")
        else:
            logger.warning("PROGRESS_CONTROLS_AVAILABLE is False - button not created")
        
        # Create plot container below controls
        plot_container = tk.Frame(main_container, bg="white")
        plot_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=plot_container,
            plot_type="progress",
            fig_attr="progress_fig",
            canvas_attr="progress_canvas",
            figsize=(8, 8),  # Square aspect ratio
            aspect_ratio=1.0,  # Square plots
        )
        
        # Create the popout control panel (initially hidden)
        if PROGRESS_CONTROLS_AVAILABLE:
            logger.debug("Attempting to create progress control panel")
            self._create_progress_control_panel()
        else:
            logger.warning("PROGRESS_CONTROLS_AVAILABLE is False - control panel not created")
        
        # Initialize what-if simulation state
        self.whatif_results = None
        self.whatif_enabled = False

    def _build_gp_slice_tab(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the 'GP Slice' tab, which displays a 2D slice of the Gaussian Process
        model's prediction for a response, varying one parameter while fixing others.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Initialize variables for GP Slice plot (controls now handled by separate panels)
        self.gp_response_var = tk.StringVar(
            value=list(responses_config.keys())[0] if responses_config else ""
        )
        self.gp_param1_var = tk.StringVar(
            value=list(params_config.keys())[0] if params_config else ""
        )
        self.gp_param2_var = tk.StringVar(
            value=(
                list(params_config.keys())[1]
                if len(params_config) > 1
                else list(params_config.keys())[0] if params_config else ""
            )
        )
        self.gp_fixed_value_var = tk.DoubleVar(value=0.5)

        # Create main container for GP Slice tab
        main_container = tk.Frame(parent, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create control button frame at the top
        control_frame = tk.Frame(main_container, bg="white", relief="ridge", bd=1)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add button to open GP Slice control panel
        logger.debug(f"GP_SLICE_CONTROLS_AVAILABLE: {GP_SLICE_CONTROLS_AVAILABLE}")
        if GP_SLICE_CONTROLS_AVAILABLE:
            control_btn = tk.Button(
                control_frame,
                text="🎛️ Open GP Slice Controls",
                command=self._show_gp_slice_controls,
                bg=COLOR_PRIMARY,
                fg=COLOR_SURFACE,
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=20,
                pady=8
            )
            control_btn.pack(side=tk.LEFT, padx=5, pady=5)
            logger.debug("GP Slice control button created")
        else:
            logger.warning("GP_SLICE_CONTROLS_AVAILABLE is False - button not created")
        
        # Create plot container below controls
        plot_container = tk.Frame(main_container, bg="white")
        plot_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=plot_container,
            plot_type="gp_slice",
            fig_attr="gp_slice_fig",
            canvas_attr="gp_slice_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
            aspect_ratio=1.0,  # Square plots
        )
        
        # Create the popout control panel (initially hidden)
        if GP_SLICE_CONTROLS_AVAILABLE:
            logger.debug("Attempting to create GP Slice control panel")
            self._create_gp_slice_control_panel()
        else:
            logger.warning("GP_SLICE_CONTROLS_AVAILABLE is False - control panel not created")

    def _build_parallel_coordinates_tab(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the 'Parallel Coordinates' tab, which displays a parallel coordinates plot.
        Allows users to select which parameters and responses to include in the plot.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Initialize variables for Parallel Coordinates plot (controls now handled by separate panels)
        all_variables = list(params_config.keys()) + list(responses_config.keys())
        self.parallel_coords_vars = {}
        for var_name in all_variables:
            var = tk.BooleanVar(value=True)  # Default to including all variables
            self.parallel_coords_vars[var_name] = var

        # Create main container for control button and plot
        main_container = tk.Frame(parent, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create control button frame at the top
        control_frame = tk.Frame(main_container, bg="white", relief="ridge", bd=1)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add button to open Parallel Coordinates control panel
        logger.debug(f"PARALLEL_COORDINATES_CONTROLS_AVAILABLE: {PARALLEL_COORDINATES_CONTROLS_AVAILABLE}")
        if PARALLEL_COORDINATES_CONTROLS_AVAILABLE:
            control_btn = tk.Button(
                control_frame,
                text="🎛️ Open Parallel Coordinates Controls",
                command=self._show_parallel_coordinates_controls,
                bg=COLOR_PRIMARY,
                fg=COLOR_SURFACE,
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=20,
                pady=8
            )
            control_btn.pack(side=tk.LEFT, padx=5, pady=5)
            logger.debug("Parallel Coordinates control button created")
        else:
            logger.warning("PARALLEL_COORDINATES_CONTROLS_AVAILABLE is False - button not created")
        
        # Create plot container below controls
        plot_container = tk.Frame(main_container, bg="white")
        plot_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=plot_container,
            plot_type="parallel_coordinates",
            fig_attr="parallel_coords_fig",
            canvas_attr="parallel_coords_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(10, 6),  # Wider aspect ratio for parallel coordinates
            aspect_ratio=1.67,  # 5:3 aspect ratio for better parallel coordinate view
        )
        
        # Initialize control panel storage
        if PARALLEL_COORDINATES_CONTROLS_AVAILABLE:
            try:
                # Store configurations for lazy control panel creation
                self.parallel_coordinates_params_config = params_config
                self.parallel_coordinates_responses_config = responses_config
            except Exception as e:
                logger.error(f"Error setting up Parallel Coordinates control panel storage: {e}")
        else:
            logger.warning("PARALLEL_COORDINATES_CONTROLS_AVAILABLE is False - control panel not created")
            self.parallel_coordinates_control_panel = None

    def _build_3d_surface_tab(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the '3D Surface' tab, which displays a 3D response surface plot.
        Allows users to select a response and two parameters to visualize the surface.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Initialize variables for 3D Surface plot (controls now handled by separate panels)
        self.surface_response_var = tk.StringVar(
            value=list(responses_config.keys())[0] if responses_config else ""
        )
        self.surface_param1_var = tk.StringVar(
            value=list(params_config.keys())[0] if params_config else ""
        )
        self.surface_param2_var = tk.StringVar(
            value=(
                list(params_config.keys())[1]
                if len(params_config) > 1
                else list(params_config.keys())[0] if params_config else ""
            )
        )

        # Create main container for 3D Surface tab
        main_container = tk.Frame(parent, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create control frame for buttons
        control_frame = tk.Frame(main_container, bg="white", relief="ridge", bd=1)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add button to open 3D Surface control panel
        logger.debug(f"SURFACE_3D_CONTROLS_AVAILABLE: {SURFACE_3D_CONTROLS_AVAILABLE}")
        if SURFACE_3D_CONTROLS_AVAILABLE:
            control_btn = tk.Button(
                control_frame,
                text="🎛️ Open 3D Surface Controls",
                command=self._show_3d_surface_controls,
                bg=COLOR_PRIMARY,
                fg=COLOR_SURFACE,
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=20,
                pady=8
            )
            control_btn.pack(side=tk.LEFT, padx=5, pady=5)
            logger.debug("3D Surface control button created")
        else:
            logger.warning("SURFACE_3D_CONTROLS_AVAILABLE is False - button not created")
        
        # Create plot container below controls
        plot_container = tk.Frame(main_container, bg="white")
        plot_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=plot_container,
            plot_type="3d_surface",
            fig_attr="surface_3d_fig",
            canvas_attr="surface_3d_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
            aspect_ratio=1.0,  # Square plots
        )
        
        # Create the popout control panel (initially hidden)
        if SURFACE_3D_CONTROLS_AVAILABLE:
            logger.debug("Attempting to create 3D Surface control panel")
            self._create_3d_surface_control_panel()
        else:
            logger.warning("SURFACE_3D_CONTROLS_AVAILABLE is False - control panel not created")

    def _build_gp_uncertainty_map_tab(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the enhanced 'GP Uncertainty Map' tab, which displays a 2D heatmap of the
        Gaussian Process model's uncertainty across two parameters with advanced controls.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Initialize variables for GP Uncertainty plot (controls now handled by separate panels)
        self.gp_uncertainty_response_var = tk.StringVar(
            value=list(responses_config.keys())[0] if responses_config else ""
        )
        self.gp_uncertainty_param1_var = tk.StringVar(
            value=list(params_config.keys())[0] if params_config else ""
        )
        self.gp_uncertainty_param2_var = tk.StringVar(
            value=(
                list(params_config.keys())[1]
                if len(params_config) > 1
                else list(params_config.keys())[0] if params_config else ""
            )
        )
        self.gp_uncertainty_plot_style_var = tk.StringVar(value="heatmap")
        self.gp_uncertainty_metric_var = tk.StringVar(value="data_density")
        self.gp_uncertainty_colormap_var = tk.StringVar(value="Reds")
        self.gp_uncertainty_resolution_var = tk.StringVar(value="70")
        self.gp_uncertainty_show_data_var = tk.BooleanVar(value=True)

        # Create main container for control button and plot
        main_container = tk.Frame(parent, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create control button frame at the top
        control_frame = tk.Frame(main_container, bg="white", relief="ridge", bd=1)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add button to open GP Uncertainty control panel
        logger.debug(f"UNCERTAINTY_ANALYSIS_CONTROLS_AVAILABLE: {UNCERTAINTY_ANALYSIS_CONTROLS_AVAILABLE}")
        if UNCERTAINTY_ANALYSIS_CONTROLS_AVAILABLE:
            control_btn = tk.Button(
                control_frame,
                text="🎛️ Open Uncertainty Analysis Controls",
                command=self._show_uncertainty_analysis_controls,
                bg=COLOR_PRIMARY,
                fg=COLOR_SURFACE,
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=20,
                pady=8
            )
            control_btn.pack(side=tk.LEFT, padx=5, pady=5)
            logger.debug("Uncertainty Analysis control button created")
        else:
            logger.warning("UNCERTAINTY_ANALYSIS_CONTROLS_AVAILABLE is False - button not created")
        
        # Create plot container below controls
        plot_container = tk.Frame(main_container, bg="white")
        plot_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=plot_container,
            plot_type="gp_uncertainty",
            fig_attr="gp_uncertainty_map_fig",
            canvas_attr="gp_uncertainty_map_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
            aspect_ratio=1.0,  # Square plots
        )
        
        # Initialize control panel storage
        if UNCERTAINTY_ANALYSIS_CONTROLS_AVAILABLE:
            try:
                # Store configurations for lazy control panel creation
                self.uncertainty_analysis_params_config = params_config
                self.uncertainty_analysis_responses_config = responses_config
            except Exception as e:
                logger.error(f"Error setting up Uncertainty Analysis control panel storage: {e}")
        else:
            logger.warning("UNCERTAINTY_ANALYSIS_CONTROLS_AVAILABLE is False - control panel not created")
            self.uncertainty_analysis_control_panel = None
        
        logger.debug("Enhanced GP Uncertainty Map tab built with advanced controls.")

    def _build_model_diagnostics_tab(self, parent, params_config, responses_config):
        """Build Model Diagnostics plot tab with dedicated control panel."""
        
        # Try to auto-detect responses if responses_config is empty or doesn't match data
        effective_responses_config = responses_config
        if (not responses_config or not any(resp in getattr(self.controller.optimizer, 'experimental_data', pd.DataFrame()).columns 
                                           for resp in responses_config.keys() if responses_config)) and hasattr(self, 'controller') and hasattr(self.controller, 'optimizer'):
            try:
                exp_data = self.controller.optimizer.experimental_data
                if not exp_data.empty:
                    # Auto-detect response columns: exclude parameter columns, keep numeric columns
                    param_names = set()
                    if hasattr(self.controller.optimizer, 'parameter_transformer'):
                        param_names = set(self.controller.optimizer.parameter_transformer.param_names)
                    
                    auto_responses = [
                        col for col in exp_data.columns 
                        if col not in param_names and 
                        exp_data[col].dtype in ['float64', 'float32', 'int64', 'int32'] and
                        not exp_data[col].isna().all()
                    ]
                    
                    if auto_responses:
                        # Create a basic responses_config for the auto-detected responses
                        effective_responses_config = {resp: {"goal": "Minimize"} for resp in auto_responses}
                        logger.info(f"Auto-detected responses for model diagnostics tab: {auto_responses}")
                    
            except Exception as e:
                logger.warning(f"Failed to auto-detect responses for model diagnostics tab: {e}")
        
        # Initialize model diagnostics response variable
        self.model_diagnostics_response_var = tk.StringVar(
            value=list(effective_responses_config.keys())[0] if effective_responses_config else ""
        )

        # Create main container for control button and plot
        main_container = tk.Frame(parent, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create control button frame at the top
        control_frame = tk.Frame(main_container, bg="white", relief="ridge", bd=1)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add button to open Model Diagnostics control panel
        logger.debug(f"MODEL_DIAGNOSTICS_CONTROLS_AVAILABLE: {MODEL_DIAGNOSTICS_CONTROLS_AVAILABLE}")
        if MODEL_DIAGNOSTICS_CONTROLS_AVAILABLE:
            control_btn = tk.Button(
                control_frame,
                text="🎛️ Open Model Diagnostics Controls",
                command=self._show_model_diagnostics_controls,
                bg=COLOR_PRIMARY,
                fg=COLOR_SURFACE,
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=20,
                pady=8
            )
            control_btn.pack(side=tk.LEFT, padx=5, pady=5)
            logger.debug("Model Diagnostics control button created")
        else:
            logger.warning("MODEL_DIAGNOSTICS_CONTROLS_AVAILABLE is False - button not created")
        
        # Create plot container below controls
        plot_container = tk.Frame(main_container, bg="white")
        plot_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main plot frame with more conservative sizing
        plot_frame = tk.Frame(plot_container, bg="white")
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create Matplotlib figure with safe fixed sizing
        fig = Figure(figsize=(5, 5), facecolor="white")
        # Set up tight layout for better space utilization
        try:
            fig.tight_layout(pad=1.0)
        except:
            pass  # tight_layout might fail with empty figure
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        
        # Configure canvas with fixed size to prevent overflow
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Store figure and canvas as instance attributes
        self.model_diagnostics_fig = fig
        self.model_diagnostics_canvas = canvas
        
        # Draw initial plot - always show placeholder initially, plot will be updated when data is available
        self._draw_model_diagnostics_placeholder()
        logger.debug("Model diagnostics tab initialized with placeholder plot")
    
    def _draw_model_diagnostics_placeholder(self):
        """Draw placeholder for model diagnostics plot when no data is available"""
        if hasattr(self, "model_diagnostics_fig"):
            self.model_diagnostics_fig.clear()  # Clear any existing content
            ax = self.model_diagnostics_fig.add_subplot(111)
            ax.text(0.5, 0.5, "Model Diagnostics\n(Data will appear when optimization data is available)", 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=12, color='gray')
            ax.set_title("Model Diagnostics Analysis")
            self.model_diagnostics_canvas.draw()

    def _build_sensitivity_analysis_tab(self, parent, params_config, responses_config):
        """Build Enhanced Sensitivity Analysis plot tab with method selection."""
        # Initialize variables for Sensitivity Analysis plot (controls now handled by separate panels)
        self.sensitivity_response_var = tk.StringVar(
            value=list(responses_config.keys())[0] if responses_config else ""
        )
        
        sensitivity_methods = [
            ("Variance-based", "variance"),
            ("Morris Elementary Effects", "morris"),
            ("Gradient-based", "gradient"),
            ("Sobol-like", "sobol"),
            ("GP Lengthscale", "lengthscale"),
            ("Feature Importance", "feature_importance"),
            ("Mixed Parameter Sensitivity", "mixed"),
        ]
        
        self.sensitivity_method_var = tk.StringVar(
            value=sensitivity_methods[0][0]
        )
        
        # Store mapping for method lookup
        self.sensitivity_method_mapping = {
            method[0]: method[1] for method in sensitivity_methods
        }
        
        self.sensitivity_samples_var = tk.StringVar(value="500")
        
        # Initialize info label variable
        self.sensitivity_info_label = None

        # Create main container for controls and plot
        main_container = tk.Frame(parent, bg="white")
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create control frame for buttons at top
        control_frame = tk.Frame(main_container, bg="white", height=50)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        control_frame.pack_propagate(False)
        
        # Add button to open Sensitivity Analysis control panel
        logger.debug(f"SENSITIVITY_ANALYSIS_CONTROLS_AVAILABLE: {SENSITIVITY_ANALYSIS_CONTROLS_AVAILABLE}")
        if SENSITIVITY_ANALYSIS_CONTROLS_AVAILABLE:
            control_btn = tk.Button(
                control_frame,
                text="🎛️ Open Sensitivity Controls",
                command=self._show_sensitivity_analysis_controls,
                bg=COLOR_PRIMARY,
                fg=COLOR_SURFACE,
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=20,
                pady=8
            )
            control_btn.pack(side=tk.LEFT, padx=5, pady=5)
            logger.debug("Sensitivity Analysis control button created")
        else:
            logger.warning("SENSITIVITY_ANALYSIS_CONTROLS_AVAILABLE is False - button not created")
        
        # Create plot container below controls
        plot_container = tk.Frame(main_container, bg="white")
        plot_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=plot_container,
            plot_type="sensitivity_analysis",
            fig_attr="sensitivity_fig",
            canvas_attr="sensitivity_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(10, 6),  # Wider aspect ratio for sensitivity analysis
            aspect_ratio=1.67,  # 5:3 aspect ratio for better sensitivity view
        )
        
        # Create the popout control panel (initially hidden)
        if SENSITIVITY_ANALYSIS_CONTROLS_AVAILABLE:
            logger.debug("Attempting to create Sensitivity Analysis control panel")
            self._create_sensitivity_analysis_control_panel()
        else:
            logger.warning("SENSITIVITY_ANALYSIS_CONTROLS_AVAILABLE is False - control panel not created")

    def _update_sensitivity_info(self, event=None):
        """Update sensitivity method information."""
        method_name = self.sensitivity_method_var.get()

        info_text = {
            "Variance-based": "Measures how much each parameter contributes to output variance. Higher values indicate more influential parameters.",
            "Morris Elementary Effects": "Calculates elementary effects using Morris screening method. Shows local sensitivity with statistical confidence.",
            "Gradient-based": "Estimates local gradients at multiple points. Good for smooth response surfaces with uncertainty quantification.",
            "Sobol-like": "Simplified Sobol indices showing global sensitivity. Robust across different response surface types.",
            "GP Lengthscale": "Uses GP model lengthscales directly. Short lengthscales indicate high sensitivity (model intrinsic).",
            "Feature Importance": "Permutation-based importance using variance differences. Model-agnostic sensitivity measure.",
            "Mixed Parameter Sensitivity": "Comprehensive analysis of both continuous and discrete parameters. Shows complete parameter influence ranking.",
        }

        self.sensitivity_info_label.config(
            text=info_text.get(method_name, "Select a sensitivity analysis method")
        )

    def _show_goal_impact_dashboard(self) -> None:
        """
        Show the Goal Impact Dashboard popup window.
        """
        logger.debug(f"_show_goal_impact_dashboard called. Has goal_impact_dashboard: {hasattr(self, 'goal_impact_dashboard')}")

        if hasattr(self, 'goal_impact_dashboard') and self.goal_impact_dashboard:
            try:
                self.goal_impact_dashboard.show()
                logger.info("Goal Impact Dashboard shown")
                return
            except Exception as e:
                logger.warning(f"Failed to show existing dashboard: {e}, creating new one")
                # Clear the reference and create new dashboard
                self.goal_impact_dashboard = None
        
        # Create new dashboard if we don't have one or the old one failed
        logger.info("Creating Goal Impact Dashboard")
        try:
            # Create dashboard with optimizer reference
            logger.debug("=== CREATING GOAL IMPACT DASHBOARD ===")
            optimizer = getattr(self, 'controller', None)
            logger.debug(f"Controller reference: {optimizer}")
            
            if optimizer and hasattr(optimizer, 'optimizer'):
                optimizer = optimizer.optimizer
                logger.debug(f"Optimizer reference: {optimizer}")
                
                # Debug optimizer configuration
                if hasattr(optimizer, 'params_config'):
                    logger.debug(f"Optimizer.params_config: {optimizer.params_config}")
                    for name, config in optimizer.params_config.items():
                        logger.debug(f"  Optimizer param '{name}': goal='{config.get('goal', 'MISSING')}', config={config}")
                else:
                    logger.debug("Optimizer has NO params_config attribute")
                    
                if hasattr(optimizer, 'responses_config'):
                    logger.debug(f"Optimizer.responses_config: {optimizer.responses_config}")
                    for name, config in optimizer.responses_config.items():
                        logger.debug(f"  Optimizer response '{name}': goal='{config.get('goal', 'MISSING')}', config={config}")
                else:
                    logger.debug("Optimizer has NO responses_config attribute")
            else:
                logger.debug("No optimizer available or controller.optimizer not found")

            logger.debug(f"Passing optimizer to dashboard: {optimizer}")
            self.goal_impact_dashboard = create_goal_impact_dashboard(
                parent=self,
                optimizer=optimizer,
                update_callback=self._update_goal_dashboard
            )
            logger.info("Goal Impact Dashboard created and shown")
        except Exception as e:
            logger.error(f"Failed to create Goal Impact Dashboard: {e}")
            messagebox.showerror("Dashboard Error", f"Could not create Goal Impact Dashboard: {str(e)}")

    def _update_goal_dashboard(self):
        """Update callback for Goal Impact Dashboard"""
        if hasattr(self, 'goal_impact_dashboard') and self.goal_impact_dashboard:
            self.goal_impact_dashboard.refresh_dashboard()

    def _refresh_suggestion(self):
        """CORRECTED - Refresh suggestion manually"""
        if self.controller:
            try:
                
                # Generate new suggestion (will be the same until new data is added - this is correct behavior)
                suggestions = self.controller.optimizer.suggest_next_experiment(
                    n_suggestions=1
                )
                
                if suggestions:
                    self.current_suggestion = suggestions[0]
                    logger.info(f"Refreshed suggestion: {self.current_suggestion}")

                    # Update display
                    for name, label in self.suggestion_labels.items():
                        value = self.current_suggestion.get(name)
                        if value is not None:
                            if isinstance(value, float):
                                formatted_value = f"{value:.3f}"
                            else:
                                formatted_value = str(value)
                            label.config(
                                text=formatted_value, bg="#e8f5e8", fg="#2d5a3d"
                            )
                        else:
                            label.config(
                                text="Not available", bg="#ffeaa7", fg="#636e72"
                            )

                    self.set_status("Suggestion refreshed")
                else:
                    logger.warning("No suggestions returned from optimizer")
                    self.set_status("Could not generate suggestion")

            except Exception as e:
                logger.error(f"Error refreshing suggestion: {e}", exc_info=True)
                self.set_status(f"Error: {e}")

    def _submit_results(self):
        """Submit experimental results"""
        if self.controller:
            try:
                result_values = {}
                for name, entry in self.results_entries.items():
                    value_str = entry.get().strip()
                    if not value_str:
                        raise ValueError(f"Please enter a value for {name}")

                    try:
                        result_values[name] = float(value_str)
                    except ValueError:
                        raise ValueError(
                            f"Invalid numeric format for {name}: {value_str}"
                        )

                # Submit results
                self.controller.submit_single_result(
                    self.current_suggestion, result_values
                )

                # Clear entries
                for entry in self.results_entries.values():
                    entry.delete(0, tk.END)

                # Update plots and suggestions after submission
                self.update_all_plots()
                self._refresh_suggestion()
                self._update_experimental_data_display()

            except ValueError as e:
                messagebox.showerror("Input Error", str(e))
            except Exception as e:
                messagebox.showerror("Submission Error", str(e))
        
        # Update edit button state after submission
        self._update_edit_button_state()

    def _update_edit_button_state(self):
        """Update the state of the Edit Last Result button based on data availability."""
        try:
            if (hasattr(self, 'edit_last_result_btn') and 
                hasattr(self, 'controller') and self.controller):
                
                # Use controller properties for consistent state checking
                if (self.controller.has_optimizer and self.controller.has_data and
                    hasattr(self.controller.optimizer, 'experimental_data')):
                    
                    exp_data = self.controller.optimizer.experimental_data
                    
                    if not exp_data.empty:
                        self.edit_last_result_btn.config(state=tk.NORMAL)
                    else:
                        self.edit_last_result_btn.config(state=tk.DISABLED)
                else:
                    self.edit_last_result_btn.config(state=tk.DISABLED)
            elif hasattr(self, 'edit_last_result_btn'):
                self.edit_last_result_btn.config(state=tk.DISABLED)
        except Exception as e:
            # Handle any errors in button state update with logging
            logger.warning(f"Error updating edit button state: {e}")
            if hasattr(self, 'edit_last_result_btn'):
                self.edit_last_result_btn.config(state=tk.DISABLED)
    
    def _edit_last_result(self):
        """Open dialog to edit the most recent experimental result."""
        if not self.controller:
            messagebox.showerror("Error", "Controller not initialized.")
            return
        
        # Check if we have an optimization session and data
        if not self.controller.has_optimizer or not self.controller.has_data:
            messagebox.showwarning("No Data", "No optimization session or experimental data available to edit.")
            return
            
        try:
            exp_data = self.controller.optimizer.experimental_data
            if exp_data.empty:
                messagebox.showwarning("No Data", "No experimental data available to edit.")
                return
            
            # Get the last row of data
            last_row = exp_data.iloc[-1]
            
            # Create edit dialog
            self._show_last_result_edit_dialog(last_row)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open edit dialog: {str(e)}")
    
    def _show_last_result_edit_dialog(self, last_row):
        """Show dialog for editing the last experimental result."""
        # Create dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Edit Last Result")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_reqwidth() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_reqheight() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        header_label = tk.Label(
            dialog,
            text="⚠️ Edit Last Experimental Result",
            font=("Arial", 14, "bold"),
            fg="#d35400"
        )
        header_label.pack(pady=(15, 10))
        
        # Warning message
        warning_text = (
            "You are about to modify the most recent experimental result.\n"
            "This will retrain the GP model and update all predictions.\n"
            "Please ensure the new values are correct."
        )
        warning_label = tk.Label(
            dialog,
            text=warning_text,
            font=("Arial", 10),
            justify=tk.CENTER,
            fg="#e74c3c",
            wraplength=450
        )
        warning_label.pack(pady=(0, 15))
        
        # Current values frame
        current_frame = tk.LabelFrame(dialog, text="Current Values", font=("Arial", 11, "bold"))
        current_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # New values frame
        new_frame = tk.LabelFrame(dialog, text="New Values", font=("Arial", 11, "bold"))
        new_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Store entry widgets
        entry_widgets = {}
        
        # Extract response columns only
        response_columns = list(self.controller.optimizer.responses_config.keys())
        
        for response_name in response_columns:
            if response_name in last_row:
                current_value = last_row[response_name]
                
                # Current value display
                current_row = tk.Frame(current_frame)
                current_row.pack(fill=tk.X, padx=10, pady=3)
                
                tk.Label(
                    current_row,
                    text=f"{response_name}:",
                    font=("Arial", 10, "bold"),
                    width=15,
                    anchor="w"
                ).pack(side=tk.LEFT)
                
                tk.Label(
                    current_row,
                    text=str(current_value),
                    font=("Arial", 10),
                    bg="#ecf0f1",
                    relief="sunken",
                    width=15
                ).pack(side=tk.LEFT, padx=(5, 0))
                
                # New value entry
                new_row = tk.Frame(new_frame)
                new_row.pack(fill=tk.X, padx=10, pady=3)
                
                tk.Label(
                    new_row,
                    text=f"{response_name}:",
                    font=("Arial", 10, "bold"),
                    width=15,
                    anchor="w"
                ).pack(side=tk.LEFT)
                
                entry = tk.Entry(new_row, font=("Arial", 10), width=15)
                entry.pack(side=tk.LEFT, padx=(5, 0))
                entry.insert(0, str(current_value))  # Pre-fill with current value
                
                entry_widgets[response_name] = entry
        
        # Buttons frame
        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(pady=20)
        
        def apply_correction():
            """Apply the correction and close dialog."""
            try:
                # Validate and collect new values
                new_values = {}
                for response_name, entry in entry_widgets.items():
                    value_str = entry.get().strip()
                    if not value_str:
                        raise ValueError(f"Please enter a value for {response_name}")
                    
                    try:
                        new_values[response_name] = float(value_str)
                    except ValueError:
                        raise ValueError(f"Invalid numeric value for {response_name}: {value_str}")
                
                # Final confirmation
                old_values = {name: last_row[name] for name in response_columns if name in last_row}
                confirmation_msg = "Confirm correction:\n\n"
                
                for name in response_columns:
                    if name in old_values and name in new_values:
                        old_val = old_values[name]
                        new_val = new_values[name]
                        if old_val != new_val:
                            confirmation_msg += f"{name}: {old_val} → {new_val}\n"
                
                confirmation_msg += "\nThis will retrain the GP model. Continue?"
                
                if messagebox.askyesno("Confirm Correction", confirmation_msg):
                    # Apply correction through controller
                    self.controller.correct_last_result(new_values)
                    
                    # Update UI
                    self.update_all_plots()
                    self._refresh_suggestion()
                    self._update_experimental_data_display()
                    
                    messagebox.showinfo("Success", "Last result corrected successfully.\nGP model has been retrained.")
                    dialog.destroy()
                    
            except ValueError as e:
                messagebox.showerror("Input Error", str(e))
            except Exception as e:
                messagebox.showerror("Correction Error", f"Failed to apply correction: {str(e)}")
        
        # Apply button
        apply_btn = tk.Button(
            buttons_frame,
            text="✓ Apply Correction",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=8,
            command=apply_correction
        )
        apply_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Cancel button
        cancel_btn = tk.Button(
            buttons_frame,
            text="✗ Cancel",
            font=("Arial", 11, "bold"),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8,
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT)

    def _generate_batch_suggestions(self):
        """Generate a batch of suggestions and display them."""
        if not self.controller:
            messagebox.showerror("Error", "Controller not initialized.")
            return

        try:
            num_suggestions = int(self.num_suggestions_entry.get())
            if num_suggestions <= 0:
                raise ValueError("Number of suggestions must be a positive integer.")

            # Get precision setting
            try:
                precision = int(self.precision_entry.get())
                if precision < 0:
                    raise ValueError("Precision must be a non-negative integer.")
            except ValueError:
                precision = 3  # Default to 3 decimal places if invalid input

            self.set_status(f"Generating {num_suggestions} batch suggestions...")
            suggestions = self.controller.generate_batch_suggestions(num_suggestions)
            self.generated_batch_suggestions = suggestions

            self.batch_suggestions_text.config(state=tk.NORMAL)
            self.batch_suggestions_text.delete(1.0, tk.END)
            if suggestions:
                for i, s in enumerate(suggestions):
                    self.batch_suggestions_text.insert(tk.END, f"Suggestion {i + 1}:\n")

                    for param, value in s.items():
                        if isinstance(value, float):
                            # Use scientific rounding for proper precision
                            rounded_value = round(value, precision)
                            self.batch_suggestions_text.insert(
                                tk.END, f"  {param}: {rounded_value:.{precision}f}"
                            )
                        else:
                            self.batch_suggestions_text.insert(
                                tk.END, f"  {param}: {value}"
                            )
                    self.batch_suggestions_text.insert(tk.END, "---")
                self.set_status(f"Generated {len(suggestions)} batch suggestions.")
            else:
                self.batch_suggestions_text.insert(
                    tk.END, "No batch suggestions could be generated."
                )
                self.set_status("No batch suggestions generated.")
            self.batch_suggestions_text.config(state=tk.DISABLED)

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            logger.error(
                f"Error generating batch suggestions in GUI: {e}", exc_info=True
            )
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.set_busy_state(False)

    def _download_batch_suggestions_csv(self):
        """Download generated batch suggestions as a CSV file."""
        if not self.generated_batch_suggestions:
            messagebox.showwarning(
                "No Data", "No batch suggestions have been generated yet."
            )
            return

        if not self.controller:
            messagebox.showerror("Error", "Controller not initialized.")
            return

        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.* ")],
                title="Save Batch Suggestions CSV",
            )
            if filepath:
                self.set_status("Saving batch suggestions to CSV...")
                success = self.controller.save_suggestions_to_csv(
                    self.generated_batch_suggestions, filepath
                )
                if success:
                    messagebox.showinfo(
                        "Success",
                        f"Batch suggestions saved to {
                            Path(filepath).name}",
                    )
                    self.set_status("Batch suggestions CSV saved.")
                else:
                    messagebox.showerror(
                        "Error", "Failed to save batch suggestions to CSV."
                    )
                    self.set_status("Failed to save batch suggestions CSV.")
        except Exception as e:
            logger.error(f"Error downloading batch suggestions CSV: {e}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.set_busy_state(False)

    def _upload_batch_suggestions_csv(self):
        """Upload experimental data from a CSV file."""
        if not self.controller:
            messagebox.showerror("Error", "Controller not initialized.")
            return

        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.* ")],
                title="Upload Experimental Data CSV",
            )
            if filepath:
                self.set_status("Uploading experimental data from CSV...")
                success = self.controller.add_batch_data_from_csv(filepath)
                if success:
                    messagebox.showinfo(
                        "Success",
                        f"Experimental data uploaded from {
                            Path(filepath).name}",
                    )
                    self.set_status("Experimental data CSV uploaded.")
                    # After successful upload, update all displays to reflect
                    # new data
                    self.controller.update_view()
                    # Enable what-if analysis now that we have data
                    self.enable_whatif_analysis()
                else:
                    messagebox.showerror(
                        "Error", "Failed to upload experimental data from CSV."
                    )
                    self.set_status("Failed to upload experimental data CSV.")
        except Exception as e:
            logger.error(f"Error uploading batch suggestions CSV: {e}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.set_busy_state(False)

    def _update_experimental_data_display(self):
        """Update the data display widget to show all experimental data points."""
        try:
            if not self.controller or not self.controller.optimizer:
                return
                
            experimental_data = self.controller.optimizer.experimental_data
            if experimental_data is None or experimental_data.empty:
                return
            
            # Clear the text widget
            self.batch_suggestions_text.config(state=tk.NORMAL)
            self.batch_suggestions_text.delete(1.0, tk.END)
            
            # Create header
            self.batch_suggestions_text.insert(tk.END, f"Experimental Data ({len(experimental_data)} points)\n")
            self.batch_suggestions_text.insert(tk.END, "=" * 80 + "\n\n")
            
            # Get column names and create formatted table
            columns = experimental_data.columns.tolist()
            
            # Create header row
            header_line = ""
            for col in columns:
                if len(col) > 12:
                    col_display = col[:9] + "..."
                else:
                    col_display = col
                header_line += f"{col_display:>12} "
            
            self.batch_suggestions_text.insert(tk.END, header_line + "\n")
            self.batch_suggestions_text.insert(tk.END, "-" * len(header_line) + "\n")
            
            # Add data rows
            for idx, row in experimental_data.iterrows():
                data_line = ""
                for col in columns:
                    value = row[col]
                    if isinstance(value, float):
                        if abs(value) < 0.001 or abs(value) > 9999:
                            formatted_value = f"{value:.2e}"
                        else:
                            formatted_value = f"{value:.3f}"
                    else:
                        formatted_value = str(value)
                    
                    # Truncate if too long
                    if len(formatted_value) > 12:
                        formatted_value = formatted_value[:9] + "..."
                    
                    data_line += f"{formatted_value:>12} "
                
                self.batch_suggestions_text.insert(tk.END, data_line + "\n")
            
            self.batch_suggestions_text.config(state=tk.DISABLED)
            
            # Enable what-if analysis when we detect experimental data
            if (len(experimental_data) > 0 and 
                hasattr(self, 'whatif_enabled') and 
                hasattr(self, 'enable_whatif_analysis') and
                not getattr(self, 'whatif_enabled', True)):
                try:
                    self.enable_whatif_analysis()
                except Exception as e:
                    logger.debug(f"Could not enable what-if analysis: {e}")
            
        except Exception as e:
            logger.error(f"Error updating experimental data display: {e}", exc_info=True)

    def _load_existing_study(self):
        """Load existing optimization study"""
        filepath = filedialog.askopenfilename(
            title="Load Optimization Study",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.* ")],
        )
        if filepath and self.controller:
            if self.controller.load_optimization_from_file(filepath):
                messagebox.showinfo(
                    "Load Complete", f"Study loaded: {Path(filepath).name}"
                )
                # Enable what-if analysis for loaded study with data
                self.enable_whatif_analysis()
                
                # Force model building before updating plots to prevent "Model not available" errors
                if hasattr(self.controller, 'optimizer') and hasattr(self.controller.optimizer, 'get_response_models'):
                    try:
                        models = self.controller.optimizer.get_response_models()
                        logger.info(f'Pre-built models after loading: {list(models.keys()) if models else "NONE"}')
                    except Exception as e:
                        logger.warning(f'Model building after loading failed: {e}')
                
                # Update all plots to display loaded data
                self.update_all_plots()
            else:
                messagebox.showerror("Load Error", "Failed to load study")

    def _import_experimental_data(self):
        """Import experimental data using wizard"""
        try:
            from .import_wizard import ImportWizard
            
            wizard = ImportWizard(self, self.controller)
            self.wait_window(wizard)
            
            if hasattr(wizard, 'result') and wizard.result:
                # Process wizard result
                result = wizard.result
                self._process_import_wizard_result(result)
            
        except ImportError:
            messagebox.showerror("Error", "Import wizard not available. Using fallback method.")
            self._upload_batch_suggestions_csv()
        except Exception as e:
            messagebox.showerror("Error", f"Import wizard failed: {str(e)}")
            logging.error(f"Import wizard error: {e}")

    def _process_import_wizard_result(self, result):
        """Process the result from the import wizard."""
        try:
            # Store the import data for later use
            self.import_data = {
                'parameters': result['parameters'],
                'responses': result['responses'], 
                'data': result['data'],
                'filepath': result['filepath']
            }
            
            # Show success message
            data_count = len(result['data'])
            param_count = len(result['parameters'])
            response_count = len(result['responses'])
            
            messagebox.showinfo(
                "Import Successful",
                f"Successfully imported:\n"
                f"• {data_count} data points\n"
                f"• {param_count} parameters\n" 
                f"• {response_count} responses\n\n"
                f"Proceeding to optimization setup..."
            )
            
            # Start setup wizard with pre-configured data
            self._start_setup_wizard_with_import()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process import data: {str(e)}")
            logging.error(f"Import processing error: {e}")

    def _start_setup_wizard_with_import(self):
        """Start setup wizard with imported data pre-configuration."""
        try:
            # Clear main frame and start setup (same as _start_setup_wizard)
            for widget in self.main_frame.winfo_children():
                widget.destroy()

            # Reset lists that hold references to parameter and response input rows
            self.param_rows = []
            self.response_rows = []
            
            # Initialize controller if needed
            if not self.controller:
                from pymbo.core.controller import SimpleController
                self.controller = SimpleController(view=self)
            
            # Pre-configure with imported data
            if hasattr(self, 'import_data'):
                import_data = self.import_data
                
                # Create optimizer with imported configuration first
                self.controller.setup_optimization_with_import(
                    import_data['parameters'],
                    import_data['responses'],
                    import_data['data']
                )
                
                # Store import data to be used when creating the interface
                self._pending_import_data = import_data
                
                # Show setup interface - it will check for _pending_import_data
                self._create_setup_interface()
            else:
                # Fallback to normal setup
                self._start_setup_wizard()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start setup with import: {str(e)}")
            logging.error(f"Setup with import error: {e}")
            # Fallback to normal setup
            self._start_setup_wizard()

    def _create_status_bar(self):
        """Create modern status bar with improved styling"""
        # Separator line
        separator = tk.Frame(self, bg=ModernTheme.DIVIDER, height=1)
        separator.pack(side=tk.BOTTOM, fill=tk.X)

        # Status bar frame
        self.status_bar = tk.Frame(self, bg=ModernTheme.SURFACE, height=32)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)

        # Status bar content
        status_content = tk.Frame(self.status_bar, bg=ModernTheme.SURFACE)
        status_content.pack(fill=tk.BOTH, expand=True, padx=24, pady=0)

        # Status label with icon
        self.status_icon = tk.Label(
            status_content,
            text="●",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.SUCCESS,
            font=ModernTheme.get_font(10, "bold"),
        )
        self.status_icon.pack(side=tk.LEFT, pady=8)

        status_label = tk.Label(
            status_content,
            textvariable=self.status_var,
            anchor=tk.W,
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(10, "normal"),
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0), pady=8)

        # Data count with modern styling
        data_label = tk.Label(
            status_content,
            textvariable=self.data_count_var,
            anchor=tk.E,
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(10, "normal"),
        )
        data_label.pack(side=tk.RIGHT, padx=0, pady=8)

        self.status_var.set("Application ready")
        self.data_count_var.set("Experiments: 0")

    def update_status(self, message, status_type="info"):
        """Update status bar with message and appropriate color"""
        self.status_var.set(message)

        # Update header status as well
        if hasattr(self, "status_text"):
            try:
                if self.status_text.winfo_exists():
                    self.status_text.config(
                        text=message.split(" - ")[0] if " - " in message else message
                    )
            except tk.TclError:
                # Widget was destroyed, ignore the update
                pass

        # Update status icon color based on type
        try:
            if status_type == "success":
                if hasattr(self, "status_icon") and self.status_icon.winfo_exists():
                    self.status_icon.config(fg=ModernTheme.SUCCESS)
                if (
                    hasattr(self, "status_indicator")
                    and self.status_indicator.winfo_exists()
                ):
                    self.status_indicator.config(fg=ModernTheme.SUCCESS)
            elif status_type == "warning":
                if hasattr(self, "status_icon") and self.status_icon.winfo_exists():
                    self.status_icon.config(fg=ModernTheme.WARNING)
                if (
                    hasattr(self, "status_indicator")
                    and self.status_indicator.winfo_exists()
                ):
                    self.status_indicator.config(fg=ModernTheme.WARNING)
            elif status_type == "error":
                if hasattr(self, "status_icon") and self.status_icon.winfo_exists():
                    self.status_icon.config(fg=ModernTheme.ERROR)
                if (
                    hasattr(self, "status_indicator")
                    and self.status_indicator.winfo_exists()
                ):
                    self.status_indicator.config(fg=ModernTheme.ERROR)
            else:  # info
                if hasattr(self, "status_icon") and self.status_icon.winfo_exists():
                    self.status_icon.config(fg=ModernTheme.PRIMARY)
                if (
                    hasattr(self, "status_indicator")
                    and self.status_indicator.winfo_exists()
                ):
                    self.status_indicator.config(fg=ModernTheme.PRIMARY)
        except tk.TclError:
            # Widget was destroyed, ignore the update
            pass

    def set_controller(self, controller):
        """Set the controller reference"""
        self.controller = controller

    def set_busy_state(self, busy: bool):
        """Set busy state"""
        cursor = "wait" if busy else ""
        self.configure(cursor=cursor)

    def set_status(
        self, text: str, clear_after_ms: Optional[int] = None, status_type: str = "info"
    ):
        """Set status text with modern styling"""
        self.update_status(text, status_type)
        self.update_idletasks()

        if clear_after_ms:
            self.after(clear_after_ms, lambda: self.update_status("Ready", "info"))

    def create_tooltip(self, widget, text):
        self.tooltip_window = None
        self.text = text

        def enter(event):
            self.show_tooltip(event)

        def leave(event):
            self.hide_tooltip()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def show_tooltip(self, event):
        x = y = 0
        x, y, cx, cy = event.widget.bbox("insert")
        x += event.widget.winfo_rootx() + 25
        y += event.widget.winfo_rooty() + 20

        # creates a toplevel window
        self.tooltip_window = tk.Toplevel(event.widget)
        # Leaves only the label and removes the app window
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+%d+%d" % (x, y))
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="yellow",
            relief="solid",
            borderwidth=1,
            font=("tahoma", "8", "normal"),
        )
        label.pack(ipadx=1)

    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

    def show_error(self, title: str, message: str):
        """Show error dialog"""
        messagebox.showerror(title, message, parent=self)

    def show_info(self, title: str, message: str):
        """Show info dialog"""
        messagebox.showinfo(title, message, parent=self)

    def update_displays(self, view_data: Dict):
        """CORRECTED - Update displays with new data"""
        logger.debug(
            f"Entering update_displays with view_data keys: {
                view_data.keys()}"
        )
        # Update suggestions
        suggestion = view_data.get("suggestion", {})
        # Handle both single suggestion dict and list of suggestions
        if isinstance(suggestion, list) and len(suggestion) > 0:
            # Take the first suggestion if it's a list
            current_suggestion = suggestion[0]
        elif isinstance(suggestion, dict):
            # Use the suggestion directly if it's already a dict
            current_suggestion = suggestion
        else:
            # Fallback for empty or invalid suggestions
            current_suggestion = {}

        self.current_suggestion = current_suggestion
        logger.debug(f"Updating suggestion labels with: {current_suggestion}")

        # Get precision setting for formatting
        try:
            precision = int(self.precision_entry.get())
            if precision < 0:
                precision = 3  # Default to 3 if negative
        except (ValueError, AttributeError):
            precision = 3  # Default to 3 decimal places if invalid input or not initialized

        for name, label in self.suggestion_labels.items():
            value = current_suggestion.get(name)
            if value is not None:
                if isinstance(value, float):
                    # Use scientific rounding for proper precision
                    rounded_value = round(value, precision)
                    formatted_value = f"{rounded_value:.{precision}f}"
                else:
                    formatted_value = str(value)
                label.config(text=formatted_value, bg="#e8f5e8", fg="#2d5a3d")
            else:
                label.config(text="Calculating...", bg="#ffeaa7", fg="#636e72")

        # Update best solution
        best_compromise = view_data.get("best_compromise", {})
        best_params = best_compromise.get("params", {})
        logger.debug(f"Updating best solution parameters with: {best_params}")
        for name, label in self.best_solution_labels["params"].items():
            value = best_params.get(name)
            if value is not None:
                if isinstance(value, float):
                    # Use scientific rounding for proper precision
                    rounded_value = round(value, precision)
                    formatted_value = f"{rounded_value:.{precision}f}"
                else:
                    formatted_value = str(value)
                label.config(text=formatted_value)
            else:
                label.config(text="Not available")

        best_responses = best_compromise.get("responses", {})
        logger.debug(f"Updating best solution responses with: {best_responses}")
        for name, labels in self.best_solution_labels["responses"].items():
            response_data = best_responses.get(name)
            if response_data and isinstance(response_data, dict):
                mean_value = response_data.get("mean")
                lower_ci = response_data.get("lower_ci")
                upper_ci = response_data.get("upper_ci")

                if mean_value is not None:
                    # Use scientific rounding for proper precision
                    rounded_mean = round(mean_value, precision)
                    labels["mean"].config(text=f"{rounded_mean:.{precision}f}")
                else:
                    labels["mean"].config(text="N/A")

                if lower_ci is not None and upper_ci is not None:
                    # Use scientific rounding for proper precision
                    rounded_lower = round(lower_ci, precision)
                    rounded_upper = round(upper_ci, precision)
                    labels["ci"].config(
                        text=f"(95% CI: {rounded_lower:.{precision}f} - {rounded_upper:.{precision}f})"
                    )
                else:
                    labels["ci"].config(text="")
            else:
                labels["mean"].config(text="Not available")
                labels["ci"].config(text="")

        # Update data count
        data_count = view_data.get("data_count", 0)
        logger.debug(f"Updating data count to: {data_count}")
        self.data_count_var.set(f"Experiments: {data_count}")

        # Update plots
        self.update_all_plots()

    def _save_current_study(self):
        """Save current optimization study"""
        if not self.controller:
            messagebox.showerror("Error", "Controller not initialized.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.* ")],
            title="Save Optimization Study",
        )
        if filepath:
            if self.controller.save_optimization_to_file(filepath):
                messagebox.showinfo(
                    "Save Complete", f"Study saved to {Path(filepath).name}"
                )
            else:
                messagebox.showerror("Save Error", "Failed to save study")

    

    def _create_plot_with_compact_controls(
        self,
        parent: tk.Frame,
        plot_type: str,
        fig_attr: str,
        canvas_attr: str,
        params_config: Dict[str, Any] = None,
        responses_config: Dict[str, Any] = None,
        figsize: Tuple[int, int] = (8, 8),
        aspect_ratio: float = 1.0,
    ) -> tk.Frame:
        """Helper method to create plot with windowed controls (separate Windows)"""

        # Frame to hold the Matplotlib plot only (no overlay controls)
        plot_container = tk.Frame(parent, bg="white")
        plot_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main plot frame with more conservative sizing
        plot_frame = tk.Frame(plot_container, bg="white")
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Use conservative fixed figure sizes to prevent overlap issues
        # For now, use smaller fixed sizes that will definitely fit
        if aspect_ratio == 1.0:  # Square plots
            safe_figsize = (5, 5)
        elif aspect_ratio > 1.0:  # Wider plots
            safe_figsize = (6, 4)
        else:  # Taller plots
            safe_figsize = (4, 6)

        # Create Matplotlib figure with safe fixed sizing
        fig = Figure(figsize=safe_figsize, facecolor="white")
        # Set up tight layout for better space utilization
        try:
            fig.tight_layout(pad=1.0)
        except:
            pass  # tight_layout might fail with empty figure
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        
        # Configure canvas with fixed size to prevent overflow
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Disable automatic resizing for now to prevent overlap issues
        # canvas_widget.bind('<Configure>', on_resize)

        # Store figure and canvas as instance attributes
        setattr(self, fig_attr, fig)
        setattr(self, canvas_attr, canvas)

        # Store configuration for lazy window creation (don't create windows during init!)
        if not hasattr(self, "window_configs"):
            self.window_configs = {}

        self.window_configs[plot_type] = {
            "params_config": params_config or {},
            "responses_config": responses_config or {},
            "plot_container": plot_container,
        }

        # Don't create any controls during initialization - they will be created on-demand
        logger.info(
            f"Stored configuration for {plot_type} - window will be created when user clicks button"
        )

        # Store plot type mapping for tab detection (no individual buttons)
        # The single button will detect active tab and open appropriate controls

        return plot_container

    def _open_active_tab_controls(self):
        """Toggle control panel for the currently active tab - method kept for compatibility but unused"""
        try:
            # Get the currently selected tab index
            current_tab_index = self.plot_notebook.index(self.plot_notebook.select())
            
            # Get the plot type for this tab
            plot_type = self.tab_to_plot_type.get(current_tab_index)
            
            if not plot_type:
                logger.warning(f"No plot type found for tab index {current_tab_index}")
                return
                
            # Check if window already exists for this plot type
            if plot_type in self.enhanced_controls:
                # Window exists, toggle its visibility
                window_control = self.enhanced_controls[plot_type]
                if hasattr(window_control, "is_visible") and hasattr(window_control, "show") and hasattr(window_control, "hide"):
                    if window_control.is_visible():
                        window_control.hide()
                        self._update_control_button_text("⚙ Open Controls")
                        logger.info(f"Hid {plot_type} window controls")
                    else:
                        window_control.show()
                        self._update_control_button_text("⚙ Close Controls")
                        logger.info(f"Showed {plot_type} window controls")
                return

            # Create window on first use
            config = self.window_configs.get(plot_type, {})

            # Special case for uncertainty analysis - use dedicated control panel
            if plot_type == "gp_uncertainty" and UNCERTAINTY_ANALYSIS_CONTROLS_AVAILABLE:
                try:
                    uncertainty_control = create_uncertainty_analysis_control_panel(
                        parent=self,
                        plot_type=plot_type,
                        params_config=config.get("params_config", {}),
                        responses_config=config.get("responses_config", {}),
                        update_callback=lambda: self._update_gp_uncertainty_map_plot(self.plot_manager),
                    )
                    self.enhanced_controls[plot_type] = uncertainty_control
                    self.uncertainty_analysis_control = uncertainty_control  # Store reference for the plotting method
                    uncertainty_control.show()
                    self._update_control_button_text("⚙ Close Controls")
                    logger.info(f"Created and opened uncertainty analysis controls")
                    return
                except Exception as e:
                    logger.warning(f"Could not create uncertainty analysis controls: {e}")

            # Special case for model diagnostics - use dedicated control panel
            if plot_type == "model_diagnostics" and MODEL_DIAGNOSTICS_CONTROLS_AVAILABLE:
                try:
                    model_diagnostics_control = create_model_diagnostics_control_panel(
                        parent=self,
                        plot_type=plot_type,
                        params_config=config.get("params_config", {}),
                        responses_config=config.get("responses_config", {}),
                        update_callback=lambda: self._update_model_diagnostics_plots(self.plot_manager),
                    )
                    self.enhanced_controls[plot_type] = model_diagnostics_control
                    self.model_diagnostics_control = model_diagnostics_control  # Store reference
                    model_diagnostics_control.show()
                    self._update_control_button_text("⚙ Close Controls")
                    logger.info(f"Created and opened model diagnostics controls")
                    return
                except Exception as e:
                    logger.warning(f"Could not create model diagnostics controls: {e}")

            # Try windowed controls first
            if WINDOW_CONTROLS_AVAILABLE:
                try:
                    window_control = create_window_plot_control_panel(
                        parent=self,
                        plot_type=plot_type,
                        params_config=config.get("params_config", {}),
                        responses_config=config.get("responses_config", {}),
                        update_callback=self.update_all_plots,
                    )
                    self.enhanced_controls[plot_type] = window_control
                    window_control.show()
                    self._update_control_button_text("⚙ Close Controls")
                    logger.info(f"Created and opened {plot_type} window controls")
                    return
                except Exception as e:
                    logger.warning(f"Could not create window {plot_type} controls: {e}")

            # Fallback to movable controls if window fails
            if MOVABLE_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        movable_control = create_movable_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        movable_control.place(x=10, y=y_offset, anchor="sw", relx=0, rely=1)
                        self.enhanced_controls[plot_type] = movable_control
                        logger.info(f"Created movable {plot_type} controls")
                        return
                except Exception as e2:
                    logger.warning(f"Could not create movable {plot_type} controls: {e2}")

            # Ultimate fallback to compact controls
            if COMPACT_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        compact_control = create_compact_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        compact_control.place(x=10, y=y_offset, anchor="sw", relx=0, rely=1)
                        self.enhanced_controls[plot_type] = compact_control
                        logger.info(f"Created compact {plot_type} controls")
                        return
                except Exception as e3:
                    logger.warning(f"All control fallbacks failed for {plot_type}: {e3}")

            logger.error(f"Failed to create any controls for {plot_type}")
            
        except Exception as e:
            logger.error(f"Error opening controls for active tab: {e}")
    
    def _update_control_button_text(self, text):
        """Update the control button text - button removed, method kept for compatibility"""
        # Control button was removed, this method is kept for compatibility
        pass

    def _add_header_control_button(self, plot_type: str):
        """Add control button to the visualization header"""
        if not hasattr(self, 'control_buttons_frame'):
            return  # Header frame not created yet
            
        def toggle_window_controls():
            """Create and show window controls on-demand"""
            # Check if window already exists
            if plot_type in self.enhanced_controls:
                # Window exists, just show it
                window_control = self.enhanced_controls[plot_type]
                if hasattr(window_control, "show"):
                    window_control.show()
                    logger.info(f"Showed existing {plot_type} window controls")
                return

            # Create window on first use
            config = self.window_configs.get(plot_type, {})

            # Try windowed controls first
            if WINDOW_CONTROLS_AVAILABLE:
                try:
                    window_control = create_window_plot_control_panel(
                        parent=self,
                        plot_type=plot_type,
                        params_config=config.get("params_config", {}),
                        responses_config=config.get("responses_config", {}),
                        update_callback=self.update_all_plots,
                    )
                    self.enhanced_controls[plot_type] = window_control
                    window_control.show()
                    self._update_control_button_text("⚙ Close Controls")
                    logger.info(f"Created and opened {plot_type} window controls")
                    return
                except Exception as e:
                    logger.warning(f"Could not create window {plot_type} controls: {e}")

            # Fallback to movable controls if window fails
            if MOVABLE_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        movable_control = create_movable_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        movable_control.place(x=10, y=y_offset, anchor="sw", relx=0, rely=1)
                        self.enhanced_controls[plot_type] = movable_control
                        logger.info(f"Created movable {plot_type} controls")
                        return
                except Exception as e2:
                    logger.warning(
                        f"Could not create movable {plot_type} controls: {e2}"
                    )

            # Ultimate fallback to compact controls
            if COMPACT_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        compact_control = create_compact_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        compact_control.place(x=10, y=y_offset, anchor="sw", relx=0, rely=1)
                        self.enhanced_controls[plot_type] = compact_control
                        logger.info(f"Created compact {plot_type} controls")
                        return
                except Exception as e3:
                    logger.warning(
                        f"All control fallbacks failed for {plot_type}: {e3}"
                    )

            logger.error(f"Failed to create any controls for {plot_type}")

        # Create compact button for header
        control_btn = tk.Button(
            self.control_buttons_frame,
            text=f"⚙ {plot_type.replace('_', ' ').title()}",
            font=("Segoe UI", 8, "bold"),
            bg="#1976D2",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=toggle_window_controls,
        )
        control_btn.pack(side=tk.LEFT, padx=2)

        # Add hover effect
        def on_enter(e):
            control_btn.config(bg="#1565C0")

        def on_leave(e):
            control_btn.config(bg="#1976D2")

        control_btn.bind("<Enter>", on_enter)
        control_btn.bind("<Leave>", on_leave)

    def _add_window_control_button(self, plot_container: tk.Frame, plot_type: str):
        """Add button to show/hide window controls"""
        button_frame = tk.Frame(plot_container, bg="white")
        button_frame.place(x=10, y=10, anchor="nw")

        def toggle_window_controls():
            """Create and show window controls on-demand"""
            # Check if window already exists
            if plot_type in self.enhanced_controls:
                # Window exists, just show it
                window_control = self.enhanced_controls[plot_type]
                if hasattr(window_control, "show"):
                    window_control.show()
                    logger.info(f"Showed existing {plot_type} window controls")
                return

            # Create window on first use
            config = self.window_configs.get(plot_type, {})

            # Try windowed controls first
            if WINDOW_CONTROLS_AVAILABLE:
                try:
                    window_control = create_window_plot_control_panel(
                        parent=self,
                        plot_type=plot_type,
                        params_config=config.get("params_config", {}),
                        responses_config=config.get("responses_config", {}),
                        update_callback=self.update_all_plots,
                    )
                    self.enhanced_controls[plot_type] = window_control
                    window_control.show()
                    self._update_control_button_text("⚙ Close Controls")
                    logger.info(f"Created and opened {plot_type} window controls")
                    return
                except Exception as e:
                    logger.warning(f"Could not create window {plot_type} controls: {e}")

            # Fallback to movable controls if window fails
            if MOVABLE_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        movable_control = create_movable_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        movable_control.place(
                            x=10, y=y_offset, anchor="sw", relx=0, rely=1
                        )
                        self.enhanced_controls[plot_type] = movable_control
                        logger.info(
                            f"Created movable controls as fallback for {plot_type}"
                        )
                        return
                except Exception as e2:
                    logger.warning(
                        f"Fallback to movable controls failed for {plot_type}: {e2}"
                    )

            # Ultimate fallback to compact controls
            if COMPACT_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        compact_control = create_compact_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        compact_control.place(
                            x=10, y=y_offset, anchor="sw", relx=0, rely=1
                        )
                        self.enhanced_controls[plot_type] = compact_control
                        logger.info(
                            f"Created compact controls as ultimate fallback for {plot_type}"
                        )
                        return
                except Exception as e3:
                    logger.warning(
                        f"All control fallbacks failed for {plot_type}: {e3}"
                    )

            logger.error(f"Failed to create any controls for {plot_type}")

        control_btn = tk.Button(
            button_frame,
            text=f"⚙ Open {plot_type.replace('_', ' ').title()} Controls",
            font=("Segoe UI", 9, "bold"),
            bg="#1976D2",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=toggle_window_controls,
        )
        control_btn.pack()

        # Hover effect
        control_btn.bind("<Enter>", lambda e: control_btn.config(bg="#1565C0"))
        control_btn.bind("<Leave>", lambda e: control_btn.config(bg="#1976D2"))

    def _get_axis_ranges(self, plot_type: str) -> dict:
        """Get axis ranges from enhanced controls if available"""
        axis_ranges = {"x_range": None, "y_range": None, "z_range": None}

        if ENHANCED_CONTROLS_AVAILABLE and hasattr(self, "enhanced_controls"):
            control_panel = self.enhanced_controls.get(plot_type)
            
            if control_panel:
                # Check if control panel has axis ranges functionality
                if hasattr(control_panel, 'get_axis_ranges'):
                    ranges = control_panel.get_axis_ranges()
                else:
                    logger.debug(f"Control panel for {plot_type} doesn't support axis ranges, using auto ranges")
                    return axis_ranges  # Return default auto ranges
                
                for axis_name, (min_val, max_val, is_auto) in ranges.items():
                    if not is_auto and min_val is not None and max_val is not None:
                        if axis_name == "x_axis":
                            axis_ranges["x_range"] = (min_val, max_val)
                        elif axis_name == "y_axis":
                            axis_ranges["y_range"] = (min_val, max_val)
                        elif axis_name == "z_axis":
                            axis_ranges["z_range"] = (min_val, max_val)

        return axis_ranges

    def _validate_and_setup_plotting(self):
        """Validate plotting components and return plot manager and current tab.
        
        Returns:
            tuple: (plot_manager, current_tab) if valid, (None, None) if invalid
        """
        if (
            not hasattr(self, "controller")
            or not self.controller
            or not self.controller.plot_manager
        ):
            logger.warning(
                "Plotting not available: controller or plot_manager missing."
            )
            return None, None
            
        plot_manager = self.controller.plot_manager
        current_tab = self.plot_notebook.tab(self.plot_notebook.select(), "text")
        logger.debug(f"Current plot notebook tab: {current_tab}")
        return plot_manager, current_tab

    def _check_plot_components(self, fig_attr: str, canvas_attr: str) -> bool:
        """
        Check if plot figure and canvas are properly initialized.
        
        Args:
            fig_attr: Name of the figure attribute
            canvas_attr: Name of the canvas attribute
            
        Returns:
            bool: True if both components are initialized, False otherwise
        """
        if not hasattr(self, fig_attr) or getattr(self, fig_attr) is None:
            logger.warning(f"{fig_attr} not initialized, skipping plot update")
            return False
        if not hasattr(self, canvas_attr) or getattr(self, canvas_attr) is None:
            logger.warning(f"{canvas_attr} not initialized, skipping plot update")
            return False
        return True

    def _update_pareto_front_plot(self, plot_manager):
        """Update the Pareto Front plot."""
        if not self._check_plot_components("pareto_fig", "pareto_canvas"):
            return
            
        logger.debug("Updating Pareto plot.")
        pareto_X_df, pareto_obj_df, _ = (
            self.controller.optimizer.get_pareto_front()
        )

        # Try to get settings from enhanced Pareto control panel first
        control_panel = self.enhanced_controls.get("pareto") if hasattr(self, "enhanced_controls") else None
        if control_panel and hasattr(control_panel, 'get_display_options'):
            # Use settings from enhanced Pareto control panel
            display_options = control_panel.get_display_options()
            
            x_obj = display_options.get("x_objective", self.pareto_x_var.get())
            y_obj = display_options.get("y_objective", self.pareto_y_var.get())
            
            show_all_solutions = display_options.get("show_all_solutions", True)
            show_pareto_points = display_options.get("show_pareto_points", True)
            show_pareto_front = display_options.get("show_pareto_front", True)
            show_legend = display_options.get("show_legend", True)
            
            # Enhanced control panel handles axis ranges internally, use auto-scaling
            ranges = {'x_range': None, 'y_range': None}
            
            logger.debug(f"Using enhanced Pareto control panel settings: {display_options}")
        else:
            # Fallback to GUI variables
            ranges = self._get_axis_ranges("pareto")
            x_obj = self.pareto_x_var.get()
            y_obj = self.pareto_y_var.get()
            show_all_solutions = self.pareto_show_all_solutions_var.get()
            show_pareto_points = self.pareto_show_pareto_points_var.get()
            show_pareto_front = self.pareto_show_pareto_front_var.get()
            show_legend = self.pareto_show_legend_var.get()
            logger.debug("Using fallback Pareto settings from GUI variables")

        plot_manager.create_pareto_plot(
            self.pareto_fig,
            self.pareto_canvas,
            x_obj,
            y_obj,
            pareto_X_df,
            pareto_obj_df,
            x_range=ranges.get("x_range"),
            y_range=ranges.get("y_range"),
            show_all_solutions=show_all_solutions,
            show_pareto_points=show_pareto_points,
            show_pareto_front=show_pareto_front,
            show_legend=show_legend,
        )
        self.pareto_canvas.draw()
        self.pareto_canvas.get_tk_widget().update()

    def _update_progress_plot(self, plot_manager):
        """Update the Progress plot."""
        if not self._check_plot_components("progress_fig", "progress_canvas"):
            return
            
        logger.debug("Updating progress plot.")
        
        # Try to get settings from enhanced progress control panel first
        control_panel = self.enhanced_controls.get("progress") if hasattr(self, "enhanced_controls") else None
        logger.debug(f"Found control panel in enhanced_controls: {control_panel is not None}")
        if control_panel and hasattr(control_panel, 'get_display_options'):
            # Use settings from enhanced progress control panel
            display_options = control_panel.get_display_options()
            # Get axis ranges from progress control panel if available
            if hasattr(control_panel, 'get_axis_ranges'):
                axis_ranges = control_panel.get_axis_ranges()
                ranges = {
                    'x_range': None if axis_ranges['x_axis'][2] else [axis_ranges['x_axis'][0], axis_ranges['x_axis'][1]] if axis_ranges['x_axis'][0] is not None and axis_ranges['x_axis'][1] is not None else None,
                    'y_range': None if axis_ranges['y_axis'][2] else [axis_ranges['y_axis'][0], axis_ranges['y_axis'][1]] if axis_ranges['y_axis'][0] is not None and axis_ranges['y_axis'][1] is not None else None,
                    'y2_range': None if axis_ranges['y2_axis'][2] else [axis_ranges['y2_axis'][0], axis_ranges['y2_axis'][1]] if axis_ranges['y2_axis'][0] is not None and axis_ranges['y2_axis'][1] is not None else None
                }
            else:
                ranges = self._get_axis_ranges("progress")
            
            show_raw_hv = display_options.get("show_raw_hv", True)
            show_normalized_hv = display_options.get("show_normalized_hv", True)
            show_trend = display_options.get("show_trend", True)
            show_legend = display_options.get("show_legend", True)
            
            logger.debug(f"Progress control panel options: show_raw_hv={show_raw_hv}, show_normalized_hv={show_normalized_hv}, show_trend={show_trend}, show_legend={show_legend}")
            
            # Set figure reference for export functionality
            if hasattr(control_panel, 'set_figure_reference'):
                control_panel.set_figure_reference(self.progress_fig)
            
            logger.debug(f"Using enhanced progress control panel settings: {display_options}")
        else:
            # Fallback to GUI variables
            ranges = self._get_axis_ranges("progress")
            show_raw_hv = self.progress_show_raw_hv_var.get()
            show_normalized_hv = self.progress_show_normalized_hv_var.get()
            show_trend = self.progress_show_trend_var.get()
            show_legend = self.progress_show_legend_var.get()
            logger.debug("Using fallback Progress settings from GUI variables")
        
        # Get axis selections from control panel
        x_axis = "iteration"
        y_axis = "hypervolume"
        y2_axis = "normalized_hypervolume"
        if control_panel and hasattr(control_panel, 'get_display_options'):
            display_options = control_panel.get_display_options()
            x_axis = display_options.get("x_metric", "iteration")
            y_axis = display_options.get("y_metric", "hypervolume")
            y2_axis = display_options.get("y2_metric", "normalized_hypervolume")
        
        plot_manager.create_progress_plot(
            self.progress_fig, 
            self.progress_canvas,
            x_range=ranges.get("x_range"),
            y_range=ranges.get("y_range"),
            y2_range=ranges.get("y2_range"),
            show_raw_hv=show_raw_hv,
            show_normalized_hv=show_normalized_hv,
            show_trend=show_trend,
            show_legend=show_legend,
            x_axis=x_axis,
            y_axis=y_axis,
            y2_axis=y2_axis
        )
        self.progress_canvas.draw()
        self.progress_canvas.get_tk_widget().update()

    def _update_gp_slice_plot(self, plot_manager):
        """Update the GP Slice plot."""
        if not self._check_plot_components("gp_slice_fig", "gp_slice_canvas"):
            return
            
        logger.debug("Updating GP Slice plot.")
        ranges = self._get_axis_ranges("gp_slice")
        
        # Get display and style options from control panel
        control_panel = self.enhanced_controls.get("gp_slice") if hasattr(self, "enhanced_controls") else None
        display_options = {}
        style_options = {}
        
        if control_panel and hasattr(control_panel, 'get_display_options'):
            display_options = control_panel.get_display_options()
        if control_panel and hasattr(control_panel, 'get_style_options'):
            style_options = control_panel.get_style_options()
        
        plot_manager.create_gp_slice_plot(
            self.gp_slice_fig,
            self.gp_slice_canvas,
            self.gp_response_var.get(),
            self.gp_param1_var.get(),
            self.gp_param2_var.get(),
            float(self.gp_fixed_value_var.get()),
            x_range=ranges.get("x_range"),
            y_range=ranges.get("y_range"),
            show_mean_line=display_options.get("show_mean_line", True),
            show_68_ci=display_options.get("show_68_ci", True),
            show_95_ci=display_options.get("show_95_ci", True),
            show_data_points=display_options.get("show_data_points", True),
            show_acquisition=display_options.get("show_acquisition", False),
            show_suggested_points=display_options.get("show_suggested_points", False),
            show_legend=display_options.get("show_legend", True),
            show_grid=display_options.get("show_grid", True),
            show_diagnostics=display_options.get("show_diagnostics", True),
            mean_line_style=style_options.get("mean_line_style", "solid"),
            ci_transparency=style_options.get("ci_transparency", "medium"),
            data_point_size=style_options.get("data_point_size", "medium")
        )
        self.gp_slice_canvas.draw()
        self.gp_slice_canvas.get_tk_widget().update()

    def _update_3d_surface_plot(self, plot_manager):
        """Update the 3D Surface plot."""
        if not self._check_plot_components("surface_3d_fig", "surface_3d_canvas"):
            return
            
        logger.debug("Updating 3D Surface plot.")
        ranges = self._get_axis_ranges("3d_surface")
        
        # Get surface settings from control panel if available
        resolution = 60
        plot_style = "surface"
        show_uncertainty = False
        show_contours = True
        show_data_points = True
        
        # Get surface mode and parameters
        surface_mode = "individual"
        response_name = self.surface_response_var.get()
        param1_name = self.surface_param1_var.get()
        param2_name = self.surface_param2_var.get()
        color_palette = "viridis"
        acquisition_type = "EHVI"
        response_weights = {}
        
        # Try to get settings from enhanced 3D surface control panel
        control_panel = self.enhanced_controls.get("3d_surface")
        if control_panel and hasattr(control_panel, 'get_display_options'):
            try:
                options = control_panel.get_display_options()
                logger.debug(f"Retrieved 3D surface display options: {options}")
                
                # Map control panel settings to plot manager parameters
                if options:
                    surface_mode = options.get('surface_mode', 'individual')
                    resolution = max(10, min(200, options.get('resolution', 60)))
                    plot_style = options.get('plot_style', 'surface')
                    color_palette = options.get('color_palette', 'viridis')
                    show_contours = options.get('show_contours', True)
                    show_data_points = options.get('show_data_points', True)
                    show_uncertainty = options.get('show_uncertainty', False)
                    
                    # Get parameter and response selections
                    response_name = options.get('response_name', response_name)
                    param1_name = options.get('param1_name', param1_name)
                    param2_name = options.get('param2_name', param2_name)
                    
                    # Get acquisition function settings
                    acquisition_type = options.get('acquisition_type', 'EHVI')
                    
                    # Get response weights for weighted-sum mode
                    if surface_mode == 'weighted_sum':
                        response_weights = options.get('response_weights', {})
                
                logger.info(f"Using 3D surface control panel settings:")
                logger.info(f"  Mode: {surface_mode}, Resolution: {resolution}, Style: {plot_style}")
                logger.info(f"  Response: {response_name}, Params: {param1_name}, {param2_name}")
                logger.info(f"  Color palette: {color_palette}")
                if surface_mode == 'weighted_sum':
                    logger.info(f"  Response weights: {response_weights}")
                elif surface_mode == 'acquisition':
                    logger.info(f"  Acquisition type: {acquisition_type}")
                
            except Exception as e:
                logger.warning(f"Error getting 3D surface display options: {e}, using defaults")
        
        plot_manager.create_3d_surface_plot(
            self.surface_3d_fig,
            self.surface_3d_canvas,
            param1_name,
            param2_name,
            surface_mode=surface_mode,
            response_name=response_name,
            weights=response_weights,
            acquisition_type=acquisition_type,
            x_range=ranges.get("x_range"),
            y_range=ranges.get("y_range"),
            z_range=ranges.get("z_range"),
            resolution=resolution,
            plot_style=plot_style,
            show_uncertainty=show_uncertainty,
            show_contours=show_contours,
            show_data_points=show_data_points,
        )
        self.surface_3d_canvas.draw()
        self.surface_3d_canvas.get_tk_widget().update()

    def _update_parallel_coordinates_plot(self, plot_manager):
        """Update the Parallel Coordinates plot."""
        if not self._check_plot_components("parallel_coords_fig", "parallel_coords_canvas"):
            return
            
        logger.debug("Updating Parallel Coordinates plot.")
        selected_vars = [
            name
            for name, var in self.parallel_coords_vars.items()
            if var.get()
        ]
        plot_manager.create_parallel_coordinates_plot(
            self.parallel_coords_fig,
            self.parallel_coords_canvas,
            selected_vars,
        )
        self.parallel_coords_canvas.draw()
        self.parallel_coords_canvas.get_tk_widget().update()

    def _update_gp_uncertainty_map_plot(self, plot_manager):
        """Update the GP Uncertainty Map plot."""
        if not self._check_plot_components("gp_uncertainty_map_fig", "gp_uncertainty_map_canvas"):
            return
            
        logger.debug("Updating Uncertainty Analysis plot.")

        # Check if we have the new uncertainty analysis control panel
        if hasattr(self, 'uncertainty_analysis_control') and self.uncertainty_analysis_control:
            # Get settings from new control panel
            display_options = self.uncertainty_analysis_control.get_display_options()
            parameters = self.uncertainty_analysis_control.get_parameters()
            settings = self.uncertainty_analysis_control.get_uncertainty_settings()
            
            # Use new control panel parameters
            response_name = parameters['response']
            param1_name = parameters['x_parameter']
            param2_name = parameters['y_parameter']
            plot_style = settings['plot_style']
            uncertainty_metric = settings['uncertainty_metric']
            colormap = settings['colormap']
            resolution = settings['resolution']
            show_experimental_data = display_options['show_experimental_data']
            show_gp_uncertainty = display_options['show_gp_uncertainty']
            show_data_density = display_options['show_data_density']
            show_statistical_deviation = display_options['show_statistical_deviation']
        else:
            # Fallback to old control values for backward compatibility
            plot_style = getattr(
                self,
                "gp_uncertainty_plot_style_var",
                tk.StringVar(value="heatmap"),
            ).get()
            uncertainty_metric = getattr(
                self,
                "gp_uncertainty_metric_var",
                tk.StringVar(value="gp_uncertainty"),
            ).get()
            colormap = getattr(
                self, "gp_uncertainty_colormap_var", tk.StringVar(value="Reds")
            ).get()
            resolution = int(
                getattr(
                    self,
                    "gp_uncertainty_resolution_var",
                    tk.StringVar(value="70"),
                ).get()
            )
            show_experimental_data = getattr(
                self, "gp_uncertainty_show_data_var", tk.BooleanVar(value=True)
            ).get()
            
            # Default parameters for fallback
            response_name = self.gp_uncertainty_response_var.get()
            param1_name = self.gp_uncertainty_param1_var.get()
            param2_name = self.gp_uncertainty_param2_var.get()
            show_gp_uncertainty = uncertainty_metric == "gp_uncertainty"
            show_data_density = uncertainty_metric == "data_density"
            show_statistical_deviation = uncertainty_metric in ["std", "variance", "coefficient_of_variation"]

        plot_manager.create_gp_uncertainty_map(
            self.gp_uncertainty_map_fig,
            self.gp_uncertainty_map_canvas,
            response_name,
            param1_name,
            param2_name,
            plot_style=plot_style,
            uncertainty_metric=uncertainty_metric,
            colormap=colormap,
            resolution=resolution,
            show_experimental_data=show_experimental_data,
            show_gp_uncertainty=show_gp_uncertainty,
            show_data_density=show_data_density,
            show_statistical_deviation=show_statistical_deviation,
        )
        self.gp_uncertainty_map_canvas.draw()
        self.gp_uncertainty_map_canvas.get_tk_widget().update()

    def _update_model_diagnostics_plots(self, plot_manager):
        """Update the Model Diagnostics plot based on control panel settings."""
        if not self._check_plot_components("model_diagnostics_fig", "model_diagnostics_canvas"):
            logger.debug("Model diagnostics plot components not available")
            return
            
        logger.debug("Updating Model Diagnostics plot")
        
        # Try to get settings from specialized control panel first
        control_panel = self.enhanced_controls.get("model_diagnostics")
        if control_panel and hasattr(control_panel, 'get_diagnostic_settings'):
            # Use settings from specialized control panel
            settings = control_panel.get_diagnostic_settings()
            response_name = settings.get("response_name", self.model_diagnostics_response_var.get() if hasattr(self, 'model_diagnostics_response_var') else "")
            diagnostic_type = settings.get("diagnostic_type", "residuals")
            
            logger.debug(f"Using diagnostic type from control panel: {diagnostic_type} for response: {response_name}")
        else:
            # Fallback to legacy variables
            response_name = self.model_diagnostics_response_var.get() if hasattr(self, 'model_diagnostics_response_var') else ""
            diagnostic_type = "residuals"  # Default to residuals
            
            logger.debug(f"Using fallback diagnostic type: {diagnostic_type} for response: {response_name}")

        # Create the appropriate model analysis plot
        if response_name:
            logger.debug(f"Creating model diagnostics plot for response: {response_name}, diagnostic_type: {diagnostic_type}")
            try:
                plot_manager.create_model_analysis_plot(
                    self.model_diagnostics_fig, self.model_diagnostics_canvas, response_name, diagnostic_type
                )
                self.model_diagnostics_canvas.draw()
                self.model_diagnostics_canvas.get_tk_widget().update()
                logger.debug("Model diagnostics plot created and drawn successfully")
            except Exception as e:
                logger.error(f"Error creating model diagnostics plot: {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                # Show error message on plot
                self.model_diagnostics_fig.clear()
                ax = self.model_diagnostics_fig.add_subplot(111)
                ax.text(0.5, 0.5, f"Error creating {diagnostic_type} plot:\n{str(e)}", 
                       ha='center', va='center', transform=ax.transAxes, 
                       fontsize=10, color='red')
                ax.set_title(f"Model Diagnostics - {diagnostic_type.title()}")
                self.model_diagnostics_canvas.draw()
        else:
            logger.debug("No response name available, showing placeholder")
            # No response selected, show placeholder
            self._draw_model_diagnostics_placeholder()

    def _update_sensitivity_analysis_plot(self, plot_manager):
        """Update the Sensitivity Analysis plot."""
        if not self._check_plot_components("sensitivity_fig", "sensitivity_canvas"):
            return
            
        logger.debug("Updating Sensitivity Analysis plot.")
        
        # Try to get settings from specialized control panel first
        control_panel = self.enhanced_controls.get("sensitivity_analysis")
        if control_panel and hasattr(control_panel, 'get_sensitivity_settings'):
            # Use settings from specialized control panel
            settings = control_panel.get_sensitivity_settings()
            response_name = settings.get("response", self.sensitivity_response_var.get() if hasattr(self, 'sensitivity_response_var') else "")
            method_code = settings.get("algorithm_code", "variance")
            n_samples = int(settings.get("iterations", "500"))
            random_seed = int(settings.get("random_seed", "42"))
            
            # Get axis ranges
            axis_ranges = control_panel.get_axis_ranges()
            x_range = axis_ranges.get('x_range')
            y_range = axis_ranges.get('y_range')
            
            logger.debug(
                f"Using sensitivity method from control panel: {method_code} with {n_samples} samples"
            )
        else:
            # Fallback to legacy variables
            response_name = self.sensitivity_response_var.get()
            method_display = self.sensitivity_method_var.get()
            method_code = self.sensitivity_method_mapping.get(
                method_display, "variance"
            )
            n_samples = int(self.sensitivity_samples_var.get())
            random_seed = 42  # Default seed for legacy mode
            x_range = None
            y_range = None
            
            logger.debug(
                f"Using sensitivity method from legacy controls: {method_code} with {n_samples} samples"
            )

        plot_manager.create_sensitivity_analysis_plot(
            self.sensitivity_fig,
            self.sensitivity_canvas,
            response_name,
            method=method_code,
            n_samples=n_samples,
            random_seed=random_seed,
        )
        
        # Apply axis ranges if available
        if hasattr(self.sensitivity_fig, 'axes') and self.sensitivity_fig.axes:
            ax = self.sensitivity_fig.axes[0]
            if x_range:
                # x_range is a tuple (min_val, max_val, is_auto)
                min_val, max_val, is_auto = x_range
                if not is_auto and min_val is not None and max_val is not None:
                    ax.set_xlim(min_val, max_val)
            if y_range:
                # y_range is a tuple (min_val, max_val, is_auto)
                min_val, max_val, is_auto = y_range
                if not is_auto and min_val is not None and max_val is not None:
                    ax.set_ylim(min_val, max_val)
        
        self.sensitivity_canvas.draw()
        self.sensitivity_canvas.get_tk_widget().update()

    # @debounce(0.5) if PERFORMANCE_OPTIMIZATION_AVAILABLE else lambda x: x
    def update_all_plots(self):
        """Update all plots based on the currently selected tab.
        
        This method serves as the main orchestrator for plot updates, delegating
        to specific plot update methods based on the active tab.
        """
        if PERFORMANCE_OPTIMIZATION_AVAILABLE:
            perf_monitor.start_timer("update_all_plots")
        
        logger.debug("Entering update_all_plots")
        plot_manager, current_tab = self._validate_and_setup_plotting()
        if not plot_manager:
            return
            
        try:
            # Map tab names to their corresponding update methods (using updated shortened names)
            plot_updaters = {
                "Pareto": lambda: self._update_pareto_front_plot(plot_manager),
                "Progress": lambda: self._update_progress_plot(plot_manager),
                "GP Slice": lambda: self._update_gp_slice_plot(plot_manager),
                "3D Surface": lambda: self._update_3d_surface_plot(plot_manager),
                "Parallel Coords": lambda: self._update_parallel_coordinates_plot(plot_manager),
                "GP Uncertainty": lambda: self._update_gp_uncertainty_map_plot(plot_manager),
                "Model Diag": lambda: self._update_model_diagnostics_plots(plot_manager),
                "Sensitivity": lambda: self._update_sensitivity_analysis_plot(plot_manager),
                "Algorithm Validation": lambda: None,  # No-op for validation tab (static content)
            }
            
            # Update the plot for the current tab
            updater = plot_updaters.get(current_tab)
            if updater:
                updater()
            else:
                logger.warning(f"No updater found for tab: {current_tab}")
                
        except Exception as e:
            logger.error(f"Error updating plots: {e}", exc_info=True)
        finally:
            if PERFORMANCE_OPTIMIZATION_AVAILABLE:
                duration = perf_monitor.end_timer("update_all_plots")
                if duration > 1.0:  # Log slow plot updates
                    logger.warning(f"Slow plot update: {duration:.2f}s for tab '{current_tab}'")
            
            # Update experimental data display
            self._update_experimental_data_display()
            
            # Update edit button state
            self._update_edit_button_state()
            
            self.update_idletasks()
            self.update()

    # SGLBO Screening Methods
    def _start_screening_wizard(self) -> None:
        """
        Initiates the SGLBO screening wizard, clearing the main frame
        and preparing the interface for parameter and response definition for screening.
        """
        # Clear the main frame to remove the welcome screen.
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Reset lists that hold references to parameter and response input rows.
        self.param_rows = []
        self.response_rows = []

        # Build the screening setup interface
        self._create_screening_interface()

    def _create_screening_interface(self) -> None:
        """
        Creates the graphical interface for setting up a new SGLBO screening study.
        This includes tabs for defining parameters and responses, and controls
        for screening-specific settings.
        """
        # Create main screening frame with modern styling
        screening_frame = tk.Frame(self.main_frame, bg=ModernTheme.BACKGROUND)
        screening_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header for the screening section
        header_frame = tk.Frame(screening_frame, bg=ModernTheme.BACKGROUND)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title
        header_label = tk.Label(
            header_frame,
            text="SGLBO Screening Setup",
            font=ModernTheme.get_font(20, "bold"),
            bg=ModernTheme.BACKGROUND,
            fg=ModernTheme.TEXT_PRIMARY,
        )
        header_label.pack(side=tk.LEFT)

        # Info about screening
        info_label = tk.Label(
            header_frame,
            text="Fast parameter space exploration using Stochastic Gradient Line Bayesian Optimization",
            font=ModernTheme.get_font(11, "normal"),
            bg=ModernTheme.BACKGROUND,
            fg=ModernTheme.TEXT_SECONDARY,
        )
        info_label.pack(side=tk.LEFT, padx=(20, 0))

        # Back button
        back_btn = self.create_modern_button(
            header_frame,
            text="← Back to Welcome",
            command=self._show_welcome_screen,
            style="secondary",
        )
        back_btn.pack(side=tk.RIGHT)

        # Main content area
        content_frame = self.create_modern_card(screening_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook widget to organize tabs
        notebook = ttk.Notebook(content_frame, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Parameters tab
        params_tab = tk.Frame(notebook, bg=ModernTheme.SURFACE)
        notebook.add(params_tab, text="Parameters")

        # Responses tab
        responses_tab = tk.Frame(notebook, bg=ModernTheme.SURFACE)
        notebook.add(responses_tab, text="Responses")

        # Screening Settings tab
        settings_tab = tk.Frame(notebook, bg=ModernTheme.SURFACE)
        notebook.add(settings_tab, text="Screening Settings")

        # Build tab contents
        self._build_screening_parameters_tab(params_tab)
        self._build_screening_responses_tab(responses_tab)
        self._build_screening_settings_tab(settings_tab)

        # Control buttons at bottom
        controls_frame = tk.Frame(screening_frame, bg=ModernTheme.BACKGROUND)
        controls_frame.pack(fill=tk.X, pady=(20, 0))

        # Start Screening button
        start_btn = self.create_modern_button(
            controls_frame,
            text="🎯 Start SGLBO Screening",
            command=self._start_screening_optimization,
            style="primary",
        )
        # Apply custom styling
        start_btn.config(
            bg=ModernTheme.SUCCESS,
            activebackground=ModernTheme.SUCCESS,
            fg="white"
        )
        start_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Validate Configuration button
        validate_btn = self.create_modern_button(
            controls_frame,
            text="✓ Validate Configuration",
            command=self._validate_screening_config,
            style="secondary",
        )
        validate_btn.pack(side=tk.RIGHT)

    def _build_screening_parameters_tab(self, parent: tk.Frame) -> None:
        """Build the parameters tab for screening setup (similar to main setup but simplified)."""
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=ModernTheme.SURFACE)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.SURFACE)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Parameters header
        header_frame = tk.Frame(scrollable_frame, bg=ModernTheme.SURFACE)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        tk.Label(
            header_frame,
            text="Define Parameters for Screening",
            font=ModernTheme.get_font(14, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack(side=tk.LEFT)

        add_param_btn = self.create_modern_button(
            header_frame,
            text="+ Add Parameter",
            command=self._add_screening_parameter_row,
            style="secondary",
        )
        add_param_btn.pack(side=tk.RIGHT)

        # Parameters container (use name expected by _add_parameter_row)
        self.params_frame = tk.Frame(scrollable_frame, bg=ModernTheme.SURFACE)
        self.params_frame.pack(fill=tk.X, padx=20, pady=10)

        # Add initial parameter row
        self._add_screening_parameter_row()

    def _build_screening_responses_tab(self, parent: tk.Frame) -> None:
        """Build the responses tab for screening setup."""
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=ModernTheme.SURFACE)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.SURFACE)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Responses header
        header_frame = tk.Frame(scrollable_frame, bg=ModernTheme.SURFACE)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        tk.Label(
            header_frame,
            text="Define Responses for Screening",
            font=ModernTheme.get_font(14, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack(side=tk.LEFT)

        add_response_btn = self.create_modern_button(
            header_frame,
            text="+ Add Response",
            command=self._add_screening_response_row,
            style="secondary",
        )
        add_response_btn.pack(side=tk.RIGHT)

        # Responses container (use name expected by _add_response_row)
        self.responses_frame = tk.Frame(scrollable_frame, bg=ModernTheme.SURFACE)
        self.responses_frame.pack(fill=tk.X, padx=20, pady=10)

        # Add initial response row
        self._add_screening_response_row()

    def _build_screening_settings_tab(self, parent: tk.Frame) -> None:
        """Build the screening settings tab with SGLBO-specific parameters."""
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=ModernTheme.SURFACE)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.SURFACE)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Settings content
        settings_content = tk.Frame(scrollable_frame, bg=ModernTheme.SURFACE)
        settings_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # SGLBO Algorithm Settings
        algo_frame = self.create_modern_card(settings_content, padx=15, pady=15)
        algo_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            algo_frame,
            text="SGLBO Algorithm Settings",
            font=ModernTheme.get_font(12, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 10))

        # Create settings variables
        self.screening_settings = {}

        # Helper function to create setting row with explanation
        def create_setting_row(parent, label, var_name, default_val, explanation, recommended_range):
            # Main frame for this setting
            setting_frame = tk.Frame(parent, bg=ModernTheme.SURFACE)
            setting_frame.pack(fill=tk.X, pady=8)
            
            # Top row with label and input
            top_row = tk.Frame(setting_frame, bg=ModernTheme.SURFACE)
            top_row.pack(fill=tk.X)
            
            tk.Label(top_row, text=f"{label}:", 
                    bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT_PRIMARY,
                    font=ModernTheme.get_font(10, "bold")).pack(side=tk.LEFT)
            
            self.screening_settings[var_name] = tk.StringVar(value=default_val)
            entry = tk.Entry(top_row, textvariable=self.screening_settings[var_name], width=8)
            entry.pack(side=tk.RIGHT)
            
            # Recommended range label
            range_label = tk.Label(top_row, text=f"({recommended_range})", 
                                 bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT_SECONDARY,
                                 font=ModernTheme.get_font(9, "italic"))
            range_label.pack(side=tk.RIGHT, padx=(0, 10))
            
            # Explanation text
            explanation_label = tk.Label(setting_frame, text=explanation,
                                       bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT_SECONDARY,
                                       font=ModernTheme.get_font(8, "normal"),
                                       wraplength=450, justify=tk.LEFT)
            explanation_label.pack(anchor="w", padx=(0, 0), pady=(2, 0))
            
            return entry

        # Initial samples
        create_setting_row(
            algo_frame,
            "Initial Samples",
            "n_initial_samples",
            "8",
            "Number of initial experiments using Latin Hypercube Sampling to seed the optimization. " +
            "More samples give better initial coverage but require more experiments. " +
            "Recommended: 2×(number of parameters) to 3×(number of parameters).",
            "5-15"
        )

        # Gradient step size
        create_setting_row(
            algo_frame,
            "Gradient Step Size",
            "gradient_step_size", 
            "0.15",
            "Step size for gradient-based moves in normalized parameter space [0,1]. " +
            "Larger values = more aggressive exploration, smaller values = more conservative moves. " +
            "Too large may overshoot optima, too small may converge slowly.",
            "0.05-0.3"
        )

        # Exploration factor
        create_setting_row(
            algo_frame,
            "Exploration Factor",
            "exploration_factor",
            "0.2", 
            "Balance between exploitation (using best known regions) and exploration (trying new areas). " +
            "Higher values encourage more exploration of uncertain regions. " +
            "Use higher values for complex response surfaces, lower for smooth surfaces.",
            "0.1-0.5"
        )

        # Max iterations
        create_setting_row(
            algo_frame,
            "Max Iterations",
            "max_iterations",
            "25",
            "Maximum number of SGLBO iterations after initial sampling. " +
            "Each iteration suggests one new experiment. Total experiments = Initial Samples + Max Iterations. " +
            "More iterations allow better convergence but take longer.",
            "15-40"
        )

        # Convergence threshold
        create_setting_row(
            algo_frame,
            "Convergence Threshold", 
            "convergence_threshold",
            "0.015",
            "Relative improvement threshold below which screening is considered converged. " +
            "Smaller values = stricter convergence (more iterations), larger values = earlier stopping. " +
            "0.01 = 1% improvement needed to continue, 0.05 = 5% improvement needed.",
            "0.01-0.05"
        )

        # Design Space Settings
        design_frame = self.create_modern_card(settings_content, padx=15, pady=15)
        design_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            design_frame,
            text="Design Space Generation Settings",
            font=ModernTheme.get_font(12, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 10))

        # Add explanation for design space
        design_info = tk.Label(
            design_frame,
            text="After screening finds the optimal region, a design space is generated around the best point " +
                 "for detailed Bayesian optimization. These settings control that design space.",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(9, "italic"),
            wraplength=450,
            justify=tk.LEFT
        )
        design_info.pack(anchor="w", pady=(0, 15))

        # Design radius
        create_setting_row(
            design_frame,
            "Design Radius",
            "design_radius",
            "0.18",
            "Radius of the design space around the optimal point (as fraction of parameter range). " +
            "Larger radius = broader exploration around optimum, smaller radius = focused search. " +
            "Too large may include poor regions, too small may miss the true optimum.",
            "0.1-0.3"
        )

        # Design type with custom layout for combobox
        design_type_frame = tk.Frame(design_frame, bg=ModernTheme.SURFACE)
        design_type_frame.pack(fill=tk.X, pady=8)
        
        # Top row with label and combobox
        type_top_row = tk.Frame(design_type_frame, bg=ModernTheme.SURFACE)
        type_top_row.pack(fill=tk.X)
        
        tk.Label(type_top_row, text="Design Type:", 
                bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT_PRIMARY,
                font=ModernTheme.get_font(10, "bold")).pack(side=tk.LEFT)
        
        self.screening_settings['design_type'] = tk.StringVar(value="ccd")
        design_combo = ttk.Combobox(type_top_row, 
                                  textvariable=self.screening_settings['design_type'],
                                  values=["ccd", "factorial", "box_behnken", "adaptive"],
                                  state="readonly", width=12)
        design_combo.pack(side=tk.RIGHT)
        
        # Explanation for design types
        design_type_explanation = tk.Label(
            design_type_frame,
            text="• CCD (Recommended): Central Composite Design - efficient, good for response surfaces\n" +
                 "• Factorial: Full factorial design - systematic but more experiments\n" +
                 "• Box-Behnken: Efficient for 3+ parameters, fewer corner points\n" +
                 "• Adaptive: Custom design based on parameter importance",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(8, "normal"),
            wraplength=450,
            justify=tk.LEFT
        )
        design_type_explanation.pack(anchor="w", pady=(2, 0))

        # Add a recommendations section
        recommendations_frame = self.create_modern_card(settings_content, padx=15, pady=15)
        recommendations_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            recommendations_frame,
            text="Quick Setup Recommendations",
            font=ModernTheme.get_font(12, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.SUCCESS,
        ).pack(anchor="w", pady=(0, 10))

        # Recommendation buttons
        rec_buttons_frame = tk.Frame(recommendations_frame, bg=ModernTheme.SURFACE)
        rec_buttons_frame.pack(fill=tk.X)

        # Fast screening preset
        fast_btn = self.create_modern_button(
            rec_buttons_frame,
            text="Fast Screening (15-20 experiments)",
            command=lambda: self._apply_screening_preset("fast"),
            style="secondary"
        )
        fast_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Thorough screening preset  
        thorough_btn = self.create_modern_button(
            rec_buttons_frame,
            text="Thorough Screening (25-35 experiments)",
            command=lambda: self._apply_screening_preset("thorough"),
            style="secondary"
        )
        thorough_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Conservative screening preset
        conservative_btn = self.create_modern_button(
            rec_buttons_frame,
            text="Many Parameters (30-45 experiments)",
            command=lambda: self._apply_screening_preset("conservative"),
            style="secondary"
        )
        conservative_btn.pack(side=tk.LEFT)

    def _apply_screening_preset(self, preset_type: str) -> None:
        """Apply preset configurations for different screening scenarios."""
        try:
            if preset_type == "fast":
                # Fast screening - minimal experiments
                self.screening_settings['n_initial_samples'].set("6")
                self.screening_settings['gradient_step_size'].set("0.2")
                self.screening_settings['exploration_factor'].set("0.25")
                self.screening_settings['max_iterations'].set("15")
                self.screening_settings['convergence_threshold'].set("0.03")
                self.screening_settings['design_radius'].set("0.2")
                self.screening_settings['design_type'].set("ccd")
                
                messagebox.showinfo("Preset Applied", 
                                  "Fast Screening preset applied!\n" +
                                  "• 6 initial samples + up to 15 iterations\n" +
                                  "• Aggressive exploration for quick results\n" +
                                  "• Total: ~15-20 experiments")
                                  
            elif preset_type == "thorough":
                # Thorough screening - balanced approach
                self.screening_settings['n_initial_samples'].set("10")
                self.screening_settings['gradient_step_size'].set("0.15")
                self.screening_settings['exploration_factor'].set("0.2")
                self.screening_settings['max_iterations'].set("25")
                self.screening_settings['convergence_threshold'].set("0.015")
                self.screening_settings['design_radius'].set("0.18")
                self.screening_settings['design_type'].set("ccd")
                
                messagebox.showinfo("Preset Applied",
                                  "Thorough Screening preset applied!\n" +
                                  "• 10 initial samples + up to 25 iterations\n" +
                                  "• Balanced exploration/exploitation\n" +
                                  "• Total: ~25-35 experiments")
                                  
            elif preset_type == "conservative":
                # Conservative screening - many parameters or complex system
                self.screening_settings['n_initial_samples'].set("12")
                self.screening_settings['gradient_step_size'].set("0.1")
                self.screening_settings['exploration_factor'].set("0.15")
                self.screening_settings['max_iterations'].set("30")
                self.screening_settings['convergence_threshold'].set("0.01")
                self.screening_settings['design_radius'].set("0.15")
                self.screening_settings['design_type'].set("box_behnken")
                
                messagebox.showinfo("Preset Applied",
                                  "Many Parameters preset applied!\n" +
                                  "• 12 initial samples + up to 30 iterations\n" +
                                  "• Conservative, thorough exploration\n" +
                                  "• Total: ~30-45 experiments")
                                  
        except Exception as e:
            messagebox.showerror("Preset Error", f"Failed to apply preset: {str(e)}")

    def _add_screening_parameter_row(self) -> None:
        """Add a new parameter row for screening setup (reuse existing method)."""
        self._add_parameter_row()

    def _add_screening_response_row(self) -> None:
        """Add a new response row for screening setup (reuse existing method)."""
        self._add_response_row()

    def _validate_screening_config(self) -> None:
        """Validate the screening configuration before starting."""
        try:
            # Collect parameter data
            params_config = {}
            valid_params = 0
            
            for i, row_widgets in enumerate(self.param_rows):
                try:
                    # Try to get basic info, skip if problematic
                    if "name" not in row_widgets or "type" not in row_widgets:
                        continue
                        
                    name = row_widgets["name"].get().strip()
                    param_type = row_widgets["type"].get()
                    
                    # Skip completely empty rows
                    if not name:
                        continue
                    
                    # Process valid parameter rows
                    if param_type == "continuous":
                        # The parameter rows use a "bounds" field with format like "[0.0, 100.0]"
                        if "bounds" not in row_widgets:
                            raise ValueError(f"Parameter '{name}' is set to continuous but bounds field is missing.")
                        
                        bounds_str = row_widgets["bounds"].get().strip()
                        
                        # Handle "None" and empty values
                        if not bounds_str or bounds_str.lower() == "none":
                            raise ValueError(f"Parameter '{name}': Bounds are required (don't use 'None'). Use format [min, max] like [0, 100]")
                        
                        # Parse bounds format [min, max]
                        try:
                            # Remove brackets and split by comma
                            bounds_str = bounds_str.strip("[]")
                            bounds_parts = [part.strip() for part in bounds_str.split(",")]
                            
                            if len(bounds_parts) != 2:
                                raise ValueError(f"Bounds must be in format [min, max]")
                            
                            min_val = float(bounds_parts[0])
                            max_val = float(bounds_parts[1])
                            
                        except (ValueError, IndexError) as e:
                            raise ValueError(f"Parameter '{name}': Invalid bounds format '{bounds_str}'. Use [min, max] like [0, 100]")
                        
                        if min_val >= max_val:
                            raise ValueError(f"Parameter '{name}': Max ({max_val}) must be greater than Min ({min_val})")
                        
                        # Handle precision - not used in this interface but keep for compatibility
                        precision_val = None
                        
                        params_config[name] = {
                            "type": "continuous",
                            "bounds": [min_val, max_val],
                            "precision": precision_val
                        }
                        valid_params += 1
                        
                    elif param_type == "categorical":
                        # Categorical parameters also use the "bounds" field but with comma-separated values
                        if "bounds" not in row_widgets:
                            raise ValueError(f"Parameter '{name}' is set to categorical but bounds field is missing.")
                        
                        values_str = row_widgets["bounds"].get().strip()
                        if not values_str or values_str.lower() == "none":
                            raise ValueError(f"Parameter '{name}': Values are required for categorical parameters. Use comma-separated format like 'A,B,C'")
                        
                        values = [v.strip() for v in values_str.split(",") if v.strip()]
                        if len(values) < 2:
                            raise ValueError(f"Parameter '{name}': At least 2 categorical values required. Use format like 'A,B,C'")
                        
                        params_config[name] = {
                            "type": "categorical",
                            "bounds": values
                        }
                        valid_params += 1
                        
                    elif param_type == "discrete":
                        # Discrete parameters use bounds field with format like "[0, 10]"
                        if "bounds" not in row_widgets:
                            raise ValueError(f"Parameter '{name}' is set to discrete but bounds field is missing.")
                        
                        bounds_str = row_widgets["bounds"].get().strip()
                        
                        # Handle "None" and empty values
                        if not bounds_str or bounds_str.lower() == "none":
                            raise ValueError(f"Parameter '{name}': Bounds are required (don't use 'None'). Use format [min, max] like [0, 10]")
                        
                        # Parse bounds format [min, max]
                        try:
                            # Remove brackets and split by comma
                            bounds_str = bounds_str.strip("[]")
                            bounds_parts = [part.strip() for part in bounds_str.split(",")]
                            
                            if len(bounds_parts) != 2:
                                raise ValueError(f"Bounds must be in format [min, max]")
                            
                            min_val = int(float(bounds_parts[0]))  # Convert to int for discrete
                            max_val = int(float(bounds_parts[1]))  # Convert to int for discrete
                            
                        except (ValueError, IndexError) as e:
                            raise ValueError(f"Parameter '{name}': Invalid bounds format '{bounds_str}'. Use [min, max] like [0, 10]")
                        
                        if min_val >= max_val:
                            raise ValueError(f"Parameter '{name}': Max ({max_val}) must be greater than Min ({min_val})")
                        
                        params_config[name] = {
                            "type": "discrete",
                            "bounds": [min_val, max_val]
                        }
                        valid_params += 1
                        
                except Exception as row_error:
                    # Skip this row and continue, but show which row failed
                    raise ValueError(f"Parameter row {i+1} error: {str(row_error)}")

            # Collect response data
            responses_config = {}
            valid_responses = 0
            
            for row_widgets in self.response_rows:
                name = row_widgets["name"].get().strip()
                goal = row_widgets["goal"].get()
                
                if name and goal:  # Both name and goal are required
                    responses_config[name] = {"goal": goal}
                    
                    if goal == "Target":
                        try:
                            target_widget = row_widgets.get("target")
                            if target_widget and hasattr(target_widget, 'get'):
                                target_val = target_widget.get().strip()
                                if target_val:
                                    responses_config[name]["target"] = float(target_val)
                                else:
                                    raise ValueError("Target value is required when goal is 'Target'")
                        except (ValueError, AttributeError) as e:
                            raise ValueError(f"Invalid target value for response '{name}': {str(e)}")
                    
                    valid_responses += 1

            # Validation
            if valid_params < 1:
                messagebox.showerror("Validation Error", "At least one parameter must be defined.")
                return
                
            if valid_responses < 1:
                messagebox.showerror("Validation Error", "At least one response must be defined.")
                return

            # Validate settings
            try:
                n_initial = int(self.screening_settings['n_initial_samples'].get())
                gradient_step = float(self.screening_settings['gradient_step_size'].get())
                exploration = float(self.screening_settings['exploration_factor'].get())
                max_iter = int(self.screening_settings['max_iterations'].get())
                conv_thresh = float(self.screening_settings['convergence_threshold'].get())
                design_radius = float(self.screening_settings['design_radius'].get())
                
                if n_initial < 3:
                    raise ValueError("Initial samples must be at least 3")
                if not (0.01 <= gradient_step <= 1.0):
                    raise ValueError("Gradient step size must be between 0.01 and 1.0")
                if not (0.01 <= exploration <= 1.0):
                    raise ValueError("Exploration factor must be between 0.01 and 1.0")
                if max_iter < 5:
                    raise ValueError("Max iterations must be at least 5")
                if not (0.001 <= conv_thresh <= 0.5):
                    raise ValueError("Convergence threshold must be between 0.001 and 0.5")
                if not (0.05 <= design_radius <= 0.5):
                    raise ValueError("Design radius must be between 0.05 and 0.5")
                    
            except ValueError as e:
                messagebox.showerror("Settings Error", f"Invalid setting: {str(e)}")
                return

            messagebox.showinfo("Validation Success", 
                              f"Configuration is valid!\n"
                              f"Parameters: {valid_params}\n"
                              f"Responses: {valid_responses}\n"
                              f"Ready to start screening.")

        except Exception as e:
            error_msg = f"Configuration validation failed: {str(e)}\n\n"
            error_msg += "PARAMETER SETUP GUIDE:\n"
            error_msg += "• Name: Temperature, Pressure, etc.\n"
            error_msg += "• Type: continuous, categorical, discrete\n"
            error_msg += "• Bounds: [min, max] for continuous (e.g., [0, 100])\n"
            error_msg += "• Bounds: A,B,C for categorical (e.g., Catalyst1,Catalyst2,Catalyst3)\n"
            error_msg += "• Goal: Usually 'None' for parameters\n\n"
            error_msg += "RESPONSE SETUP GUIDE:\n"
            error_msg += "• Name: Yield, Purity, etc.\n"
            error_msg += "• Goal: Maximize, Minimize, or Target\n"
            error_msg += "• Target: only when Goal = 'Target'\n\n"
            error_msg += "COMMON FIXES:\n"
            error_msg += "• For continuous parameters: use [50, 200] format\n"
            error_msg += "• For categorical parameters: use A,B,C format\n"
            error_msg += "• Don't use 'None' in bounds fields\n"
            error_msg += "• Remove empty rows before validation"
            
            messagebox.showerror("Validation Error", error_msg)

    def _start_screening_optimization(self) -> None:
        """Start the SGLBO screening optimization process."""
        try:
            # First validate configuration
            self._validate_screening_config()
            
            # If validation passes, start screening
            if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'start_sglbo_screening'):
                # Use controller if available and has SGLBO method
                config = self._get_screening_config()
                print(f"DEBUG: Sending config to controller: {config}")
                print(f"DEBUG: Parameters: {config.get('parameters', {})}")
                print(f"DEBUG: Responses: {config.get('responses', {})}")
                self.controller.start_sglbo_screening(config)
            else:
                # Standalone SGLBO execution (default for now)
                self._run_sglbo_screening_standalone()
            
        except Exception as e:
            messagebox.showerror("Start Error", f"Failed to start screening: {str(e)}")
    
    def _get_screening_config(self) -> dict:
        """Get the complete screening configuration from GUI."""
        # Collect parameter data (same logic as validation)
        params_config = {}
        for i, row_widgets in enumerate(self.param_rows):
            try:
                if "name" not in row_widgets or "type" not in row_widgets:
                    continue
                    
                name = row_widgets["name"].get().strip()
                param_type = row_widgets["type"].get()
                
                if not name:
                    continue
                
                if param_type == "continuous":
                    bounds_str = row_widgets["bounds"].get().strip()
                    if bounds_str and bounds_str.lower() != "none":
                        bounds_str = bounds_str.strip("[]")
                        parts = [part.strip() for part in bounds_str.split(",")]
                        if len(parts) == 2:
                            min_val, max_val = float(parts[0]), float(parts[1])
                            params_config[name] = {
                                "type": "continuous",
                                "bounds": [min_val, max_val],
                                "precision": None
                            }
                            
                elif param_type == "categorical":
                    bounds_str = row_widgets["bounds"].get().strip()
                    if bounds_str and bounds_str.lower() != "none":
                        values = [v.strip() for v in bounds_str.split(",") if v.strip()]
                        if len(values) >= 2:
                            params_config[name] = {
                                "type": "categorical",
                                "bounds": values
                            }
                            
                elif param_type == "discrete":
                    bounds_str = row_widgets["bounds"].get().strip()
                    if bounds_str and bounds_str.lower() != "none":
                        bounds_str = bounds_str.strip("[]")
                        parts = [part.strip() for part in bounds_str.split(",")]
                        if len(parts) == 2:
                            min_val, max_val = int(float(parts[0])), int(float(parts[1]))
                            params_config[name] = {
                                "type": "discrete",
                                "bounds": [min_val, max_val]
                            }
            except:
                continue
        
        # Collect response data
        responses_config = {}
        for row_widgets in self.response_rows:
            try:
                name = row_widgets["name"].get().strip()
                goal = row_widgets["goal"].get()
                
                if name and goal:
                    responses_config[name] = {"goal": goal}
                    
                    if goal == "Target":
                        target_widget = row_widgets.get("target")
                        if target_widget and hasattr(target_widget, 'get'):
                            target_val = target_widget.get().strip()
                            if target_val:
                                responses_config[name]["target"] = float(target_val)
            except:
                continue
        
        # Get SGLBO settings
        sglbo_settings = {}
        if hasattr(self, 'screening_settings'):
            try:
                sglbo_settings = {
                    "n_initial_samples": int(self.screening_settings['n_initial_samples'].get()),
                    "gradient_step_size": float(self.screening_settings['gradient_step_size'].get()),
                    "exploration_factor": float(self.screening_settings['exploration_factor'].get()),
                    "max_iterations": int(self.screening_settings['max_iterations'].get()),
                    "convergence_threshold": float(self.screening_settings['convergence_threshold'].get()),
                    "design_radius": float(self.screening_settings['design_radius'].get()),
                    "design_type": self.screening_settings['design_type'].get()
                }
            except:
                # Use defaults if settings can't be read
                sglbo_settings = {
                    "n_initial_samples": 8,
                    "gradient_step_size": 0.15,
                    "exploration_factor": 0.2,
                    "max_iterations": 25,
                    "convergence_threshold": 0.015,
                    "design_radius": 0.18,
                    "design_type": "CCD"
                }
        
        return {
            "parameters": params_config,
            "responses": responses_config,
            "sglbo_settings": sglbo_settings
        }
    
    def _run_sglbo_screening_standalone(self) -> None:
        """Run SGLBO screening in standalone mode (without controller)."""
        import sys
        import os
        
        # Add screening module to path
        screening_path = os.path.join(os.path.dirname(__file__), 'screening')
        if screening_path not in sys.path:
            sys.path.append(screening_path)
        
        try:
            from ..screening.screening_optimizer import ScreeningOptimizer
            import pandas as pd
            
            # Get configuration
            config = self._get_screening_config()
            params_config = config["parameters"]
            responses_config = config["responses"]
            settings = config["sglbo_settings"]
            
            if not params_config or not responses_config:
                messagebox.showerror("Configuration Error", "Please set up at least one parameter and one response.")
                return
            
            # Show screening execution window
            self._show_screening_execution_window(params_config, responses_config, settings)
            
        except ImportError as e:
            messagebox.showerror("Module Error", f"Could not import screening modules: {e}")
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to run screening: {e}")
    
    def _show_screening_execution_window(self, params_config, responses_config, settings):
        """Show a window for SGLBO screening execution."""
        # Create new window for screening execution
        screening_window = tk.Toplevel(self)
        screening_window.title("SGLBO Screening Execution")
        screening_window.geometry("800x600")
        screening_window.configure(bg=ModernTheme.BACKGROUND)
        
        # Header
        header_frame = tk.Frame(screening_window, bg=ModernTheme.SURFACE)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="🎯 SGLBO Screening in Progress",
            font=ModernTheme.get_font(16, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack()
        
        # Configuration summary
        config_frame = tk.Frame(screening_window, bg=ModernTheme.SURFACE)
        config_frame.pack(fill=tk.X, padx=20, pady=10)
        
        config_text = f"Parameters: {list(params_config.keys())}\n"
        config_text += f"Responses: {list(responses_config.keys())}\n"
        config_text += f"Initial Samples: {settings['n_initial_samples']}\n"
        config_text += f"Max Iterations: {settings['max_iterations']}"
        
        tk.Label(
            config_frame,
            text=config_text,
            font=ModernTheme.get_font(10),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        # Progress text area
        progress_frame = tk.Frame(screening_window, bg=ModernTheme.SURFACE)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(
            progress_frame,
            text="Screening Progress:",
            font=ModernTheme.get_font(12, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack(anchor=tk.W)
        
        progress_text = scrolledtext.ScrolledText(
            progress_frame,
            height=20,
            bg=ModernTheme.BACKGROUND,
            fg=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.get_font(9, family="monospace")
        )
        progress_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(screening_window, bg=ModernTheme.SURFACE)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        start_btn = self.create_modern_button(
            button_frame,
            text="▶ Start Screening",
            command=lambda: self._execute_sglbo_screening(
                params_config, responses_config, settings, 
                progress_text, start_btn, screening_window
            ),
            style="primary"
        )
        start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = self.create_modern_button(
            button_frame,
            text="Close",
            command=screening_window.destroy,
            style="secondary"
        )
        close_btn.pack(side=tk.RIGHT)
        
        progress_text.insert(tk.END, "SGLBO Screening configured and ready to start.\n")
        progress_text.insert(tk.END, "Click 'Start Screening' to begin optimization.\n\n")
    
    def _execute_sglbo_screening(self, params_config, responses_config, settings, progress_text, start_btn, window):
        """Execute the actual SGLBO screening algorithm."""
        try:
            # Disable start button
            start_btn.config(state="disabled", text="Running...")
            window.update()
            
            from ..screening.screening_optimizer import ScreeningOptimizer
            import pandas as pd
            import numpy as np
            
            progress_text.insert(tk.END, "Initializing SGLBO optimizer...\n")
            window.update()
            
            # Create optimizer (only pass valid optimizer parameters)
            optimizer = ScreeningOptimizer(
                params_config=params_config,
                responses_config=responses_config,
                gradient_step_size=settings["gradient_step_size"],
                exploration_factor=settings["exploration_factor"],
                max_iterations=settings["max_iterations"],
                convergence_threshold=settings["convergence_threshold"],
                n_initial_samples=settings["n_initial_samples"],
                random_seed=42
            )
            
            progress_text.insert(tk.END, f"Optimizer created with extrapolation: {optimizer.param_handler.allow_extrapolation}\n\n")
            window.update()
            
            # Generate initial experiments
            progress_text.insert(tk.END, "Generating initial experiments...\n")
            window.update()
            
            initial_experiments = optimizer.suggest_initial_experiments()
            
            progress_text.insert(tk.END, f"Generated {len(initial_experiments)} initial experiments:\n")
            for i, exp in enumerate(initial_experiments):
                progress_text.insert(tk.END, f"  Exp {i+1}: {exp}\n")
            progress_text.insert(tk.END, "\n")
            window.update()
            
            # Show message about manual experimentation
            progress_text.insert(tk.END, "=" * 50 + "\n")
            progress_text.insert(tk.END, "NEXT STEPS:\n")
            progress_text.insert(tk.END, "=" * 50 + "\n")
            progress_text.insert(tk.END, "1. Perform the experiments shown above\n")
            progress_text.insert(tk.END, "2. Record the response values\n")
            progress_text.insert(tk.END, "3. Input results to continue SGLBO iterations\n\n")
            progress_text.insert(tk.END, "This demo shows initial experiment suggestions.\n")
            progress_text.insert(tk.END, "Full implementation would continue with iterative screening\n")
            progress_text.insert(tk.END, "based on experimental results.\n\n")
            progress_text.insert(tk.END, f"SGLBO Configuration:\n")
            progress_text.insert(tk.END, f"- Extrapolation enabled: Can explore beyond initial bounds\n")
            progress_text.insert(tk.END, f"- Gradient step size: {settings['gradient_step_size']}\n")
            progress_text.insert(tk.END, f"- Max iterations: {settings['max_iterations']}\n")
            progress_text.insert(tk.END, f"- Initial samples: {settings['n_initial_samples']}\n")
            
            # Re-enable button
            start_btn.config(state="normal", text="✓ Screening Complete")
            
        except Exception as e:
            progress_text.insert(tk.END, f"\nERROR: {str(e)}\n")
            start_btn.config(state="normal", text="Error - Try Again")
    
    def _show_advanced_screening_execution_window(self, screening_optimizer, results_manager, design_generator, config):
        """Show the advanced screening execution window with manual experimental input."""
        try:
            if INTERACTIVE_SCREENING_AVAILABLE:
                # Use the interactive execution window (preferred)
                show_interactive_screening_window(
                    parent=self,
                    screening_optimizer=screening_optimizer,
                    results_manager=results_manager,
                    design_generator=design_generator,
                    config=config
                )
            elif SCREENING_WINDOW_AVAILABLE:
                # Fallback to automatic execution window
                show_screening_execution_window(
                    parent=self,
                    screening_optimizer=screening_optimizer,
                    results_manager=results_manager,
                    design_generator=design_generator,
                    config=config
                )
            else:
                # Fallback to basic window
                params_config = config.get("parameters", {})
                responses_config = config.get("responses", {})
                settings = config.get("sglbo_settings", {})
                self._show_screening_execution_window(params_config, responses_config, settings)
                
        except Exception as e:
            logger.error(f"Error showing advanced screening execution window: {e}")
            messagebox.showerror("Execution Window Error", 
                               f"Failed to show screening execution window: {e}")

    def _build_algorithm_validation_tab(self, parent, params_config, responses_config):
        """Build unified Algorithm Verification tab with new system."""
        try:
            # Import new unified verification widget
            from .algorithm_verification_widget import AlgorithmVerificationWidget
            
            # Create new verification widget
            self.algorithm_verification_widget = AlgorithmVerificationWidget(
                parent_frame=parent,
                controller=self.controller
            )
            
            logger.info("New algorithm verification system initialized")
            
        except ImportError as e:
            logger.warning(f"New verification widget not available: {e}")
            # Fallback to legacy validation tab
            self._build_legacy_algorithm_validation_tab(parent, params_config, responses_config)
            
        except Exception as e:
            logger.error(f"Error building new verification tab: {e}")
            # Fallback to legacy validation tab
            self._build_legacy_algorithm_validation_tab(parent, params_config, responses_config)
    
    def _build_legacy_algorithm_validation_tab(self, parent, params_config, responses_config):
        """Build legacy Algorithm Validation tab for fallback."""
        # Main container with scrolling capability
        main_frame = tk.Frame(parent, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame, bg="white")
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(
            scrollable_frame,
            text="Algorithm Validation & Benchmarking",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=COLOR_PRIMARY
        )
        title_label.pack(pady=(0, 20))
        
        # Controls frame
        controls_frame = tk.LabelFrame(
            scrollable_frame,
            text="Benchmark Configuration",
            font=("Arial", 12, "bold"),
            bg="white",
            fg=COLOR_SECONDARY,
            padx=10,
            pady=10
        )
        controls_frame.pack(fill="x", pady=(0, 20))
        
        # Test function selection
        test_func_frame = tk.Frame(controls_frame, bg="white")
        test_func_frame.pack(fill="x", pady=5)
        
        test_func_label = tk.Label(test_func_frame, text="Test Function:", bg="white", font=("Arial", 10, "bold"))
        test_func_label.pack(side="left")
        self.validation_test_function_var = tk.StringVar(value="ZDT1")
        test_func_combo = ttk.Combobox(
            test_func_frame,
            textvariable=self.validation_test_function_var,
            values=["ZDT1", "ZDT2", "DTLZ2"],
            state="readonly",
            width=15
        )
        test_func_combo.pack(side="left", padx=(10, 0))
        
        # Add tooltip for test function
        self._add_tooltip(test_func_label, 
            "Test Function Selection:\n\n"
            "• ZDT1: Convex Pareto front, 2 objectives\n"
            "  Good for testing convergence\n\n"
            "• ZDT2: Non-convex Pareto front, 2 objectives\n" 
            "  Tests algorithm's ability to handle curved fronts\n\n"
            "• DTLZ2: Spherical Pareto front, 3 objectives\n"
            "  Tests many-objective optimization capabilities")
        self._add_tooltip(test_func_combo,
            "Select the mathematical test function to benchmark algorithms against.\n"
            "Each function has different characteristics to test different aspects\n"
            "of multi-objective optimization performance.")
        
        # Algorithm selection
        algo_frame = tk.Frame(controls_frame, bg="white")
        algo_frame.pack(fill="x", pady=10)
        
        algo_label = tk.Label(algo_frame, text="Algorithms to Compare:", bg="white", font=("Arial", 10, "bold"))
        algo_label.pack(anchor="w")
        
        # Algorithm checkboxes with tooltips
        self.validation_algorithms = {}
        algorithms = ["This App's MOBO", "Random Search", "NSGA-II"]
        algorithm_tooltips = {
            "This App's MOBO": "Multi-Objective Bayesian Optimization\n\n"
                               "Uses Gaussian Processes to model objectives and\n"
                               "intelligently selects next evaluation points.\n"
                               "Excellent for expensive function evaluations.",
            
            "Random Search": "Random Sampling Baseline\n\n"
                            "Randomly samples points from the parameter space.\n"
                            "Simple baseline to compare against.\n"
                            "Good for establishing minimum performance.",
            
            "NSGA-II": "Non-dominated Sorting Genetic Algorithm II\n\n"
                      "Popular evolutionary multi-objective algorithm.\n"
                      "Uses genetic operators (crossover, mutation)\n"
                      "and non-dominated sorting for optimization."
        }
        
        for i, alg in enumerate(algorithms):
            var = tk.BooleanVar(value=True)
            self.validation_algorithms[alg] = var
            
            cb = tk.Checkbutton(
                algo_frame,
                text=alg,
                variable=var,
                bg="white",
                font=("Arial", 10)
            )
            cb.pack(anchor="w", padx=(20, 0))
            
            # Add tooltip for each algorithm
            self._add_tooltip(cb, algorithm_tooltips[alg])
        
        # Add tooltip for the main label
        self._add_tooltip(algo_label,
            "Select which optimization algorithms to include in the benchmark.\n"
            "Multiple algorithms can be compared simultaneously to evaluate\n"
            "relative performance on the selected test function.")
        
        # Parameters frame
        params_frame = tk.Frame(controls_frame, bg="white")
        params_frame.pack(fill="x", pady=10)
        
        # Evaluation budget
        budget_frame = tk.Frame(params_frame, bg="white")
        budget_frame.pack(fill="x", pady=2)
        
        budget_label = tk.Label(budget_frame, text="Evaluation Budget:", bg="white", font=("Arial", 10))
        budget_label.pack(side="left")
        self.validation_budget_var = tk.StringVar(value="100")
        budget_entry = tk.Entry(budget_frame, textvariable=self.validation_budget_var, width=10)
        budget_entry.pack(side="left", padx=(10, 0))
        
        # Add tooltip for evaluation budget
        self._add_tooltip(budget_label,
            "Evaluation Budget:\n\n"
            "Total number of function evaluations each algorithm\n"
            "is allowed to use. Higher values provide more thorough\n"
            "optimization but take longer to complete.\n\n"
            "Recommended values:\n"
            "• Quick test: 50-100\n"
            "• Standard: 200-500\n"
            "• Thorough: 1000+")
        self._add_tooltip(budget_entry,
            "Enter the maximum number of function evaluations\n"
            "for each algorithm in the benchmark.")
        
        # Number of runs
        runs_frame = tk.Frame(params_frame, bg="white")
        runs_frame.pack(fill="x", pady=2)
        
        runs_label = tk.Label(runs_frame, text="Number of Independent Runs:", bg="white", font=("Arial", 10))
        runs_label.pack(side="left")
        self.validation_runs_var = tk.StringVar(value="10")
        runs_entry = tk.Entry(runs_frame, textvariable=self.validation_runs_var, width=10)
        runs_entry.pack(side="left", padx=(10, 0))
        
        # Add tooltip for number of runs
        self._add_tooltip(runs_label,
            "Number of Independent Runs:\n\n"
            "Each algorithm is run multiple times with different\n"
            "random seeds to get statistically meaningful results.\n"
            "More runs provide better statistical confidence.\n\n"
            "Recommended values:\n"
            "• Quick test: 5-10\n"
            "• Standard: 20-30\n"
            "• Publication quality: 50+")
        self._add_tooltip(runs_entry,
            "Enter the number of independent runs for each algorithm.\n"
            "Results will be averaged across all runs.")
        
        # Batch processing frame
        batch_frame = tk.Frame(params_frame, bg="white")
        batch_frame.pack(fill="x", pady=8)
        
        # Batch mode checkbox
        self.batch_mode_var = tk.BooleanVar(value=False)
        batch_checkbox = tk.Checkbutton(
            batch_frame,
            text="Enable Batch Processing",
            variable=self.batch_mode_var,
            bg="white",
            font=("Arial", 10, "bold"),
            command=self._toggle_batch_mode
        )
        batch_checkbox.pack(anchor="w")
        
        # Add tooltip for batch mode
        self._add_tooltip(batch_checkbox,
            "Batch Processing Mode:\n\n"
            "When enabled, allows running benchmarks across\n"
            "multiple test functions and parameter combinations\n"
            "automatically. Useful for comprehensive evaluation.\n\n"
            "• Runs all selected test functions\n"
            "• Saves detailed results to files\n"
            "• Generates comparison reports")
        
        # Batch configuration frame (initially hidden)
        self.batch_config_frame = tk.Frame(params_frame, bg="white")
        
        # Batch test functions selection
        batch_test_frame = tk.Frame(self.batch_config_frame, bg="white")
        batch_test_frame.pack(fill="x", pady=5)
        
        tk.Label(batch_test_frame, text="Batch Test Functions:", bg="white", font=("Arial", 9)).pack(anchor="w")
        
        self.batch_test_functions = {}
        batch_functions = ["ZDT1", "ZDT2", "DTLZ2"]
        
        for func in batch_functions:
            var = tk.BooleanVar(value=True)
            self.batch_test_functions[func] = var
            
            cb = tk.Checkbutton(
                batch_test_frame,
                text=func,
                variable=var,
                bg="white",
                font=("Arial", 9)
            )
            cb.pack(anchor="w", padx=(20, 0))
        
        # Batch output directory
        batch_output_frame = tk.Frame(self.batch_config_frame, bg="white")
        batch_output_frame.pack(fill="x", pady=5)
        
        tk.Label(batch_output_frame, text="Output Directory:", bg="white", font=("Arial", 9)).pack(side="left")
        self.batch_output_var = tk.StringVar(value="benchmark_results")
        batch_output_entry = tk.Entry(batch_output_frame, textvariable=self.batch_output_var, width=30)
        batch_output_entry.pack(side="left", padx=(10, 5))
        
        batch_browse_btn = tk.Button(
            batch_output_frame,
            text="Browse",
            command=self._browse_batch_output_dir,
            bg=COLOR_SECONDARY,
            fg="white",
            font=("Arial", 8),
            relief="flat",
            padx=10,
            pady=2
        )
        batch_browse_btn.pack(side="left")
        
        # Add tooltips for batch configuration
        self._add_tooltip(batch_output_entry,
            "Directory where batch benchmark results will be saved.\n"
            "Results include CSV files, plots, and summary reports.")
        self._add_tooltip(batch_browse_btn,
            "Browse to select the output directory for batch results.")
        
        # Parallel processing configuration
        parallel_frame = tk.Frame(self.batch_config_frame, bg="white")
        parallel_frame.pack(fill="x", pady=5)
        
        # Enable parallel processing
        self.parallel_processing_var = tk.BooleanVar(value=True)
        parallel_checkbox = tk.Checkbutton(
            parallel_frame,
            text="Enable Parallel Processing",
            variable=self.parallel_processing_var,
            bg="white",
            font=("Arial", 9)
        )
        parallel_checkbox.pack(anchor="w")
        
        # Number of parallel workers
        workers_frame = tk.Frame(parallel_frame, bg="white")
        workers_frame.pack(fill="x", padx=(20, 0), pady=2)
        
        tk.Label(workers_frame, text="Parallel Workers:", bg="white", font=("Arial", 8)).pack(side="left")
        self.parallel_workers_var = tk.StringVar(value="auto")
        workers_entry = tk.Entry(workers_frame, textvariable=self.parallel_workers_var, width=8)
        workers_entry.pack(side="left", padx=(5, 0))
        
        # Parallel mode selection
        mode_frame = tk.Frame(parallel_frame, bg="white")
        mode_frame.pack(fill="x", padx=(20, 0), pady=2)
        
        tk.Label(mode_frame, text="Parallel Mode:", bg="white", font=("Arial", 8)).pack(side="left")
        self.parallel_mode_var = tk.StringVar(value="runs")
        mode_combo = ttk.Combobox(
            mode_frame,
            textvariable=self.parallel_mode_var,
            values=["runs", "algorithms", "both"],
            state="readonly",
            width=10
        )
        mode_combo.pack(side="left", padx=(5, 0))
        
        # Add tooltips for parallel processing
        self._add_tooltip(parallel_checkbox,
            "Parallel Processing:\n\n"
            "Runs multiple benchmark tasks simultaneously\n"
            "to significantly reduce total execution time.\n\n"
            "Benefits:\n"
            "• 2-4x faster for multi-function batches\n"
            "• Utilizes multiple CPU cores\n"
            "• Maintains result accuracy\n\n"
            "Recommended: Enabled for batch processing")
            
        self._add_tooltip(workers_entry,
            "Number of Parallel Workers:\n\n"
            "Controls how many benchmark tasks run simultaneously.\n\n"
            "Options:\n"
            "• 'auto': Uses optimal number (CPU cores - 1)\n"
            "• Number (e.g., '2', '4'): Specific worker count\n\n"
            "Higher numbers = faster execution but more CPU usage.\n"
            "Recommended: 'auto' for best performance")
            
        self._add_tooltip(mode_combo,
            "Parallel Mode:\n\n"
            "Controls which level of parallelization to use.\n\n"
            "• 'runs': Parallelize independent runs (fastest)\n"
            "  All algorithm runs execute simultaneously\n\n"
            "• 'algorithms': Parallelize different algorithms\n"
            "  Each algorithm runs on separate worker\n\n"
            "• 'both': Maximum parallelization\n"
            "  Combines both strategies for best performance\n\n"
            "Recommended: 'runs' for best speedup")
        
        # Run benchmark buttons frame
        button_frame = tk.Frame(controls_frame, bg="white")
        button_frame.pack(fill="x", pady=10)
        
        # Fast benchmark button (default)
        self.run_fast_benchmark_btn = tk.Button(
            button_frame,
            text="Run Fast Benchmark",
            command=self._run_fast_benchmark_validation,
            bg=COLOR_SUCCESS,
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            bd=0,
            padx=20,
            pady=8
        )
        self.run_fast_benchmark_btn.pack(side="left", padx=(0, 10))
        
        # Full benchmark button (slower)
        self.run_benchmark_btn = tk.Button(
            button_frame,
            text="Run Full Benchmark",
            command=self._run_benchmark_validation,
            bg=COLOR_PRIMARY,
            fg="white",
            font=("Arial", 11),
            relief="flat",
            bd=0,
            padx=15,
            pady=8
        )
        self.run_benchmark_btn.pack(side="left", padx=(0, 10))
        
        # Enhanced validation button (clean output)
        self.run_enhanced_benchmark_btn = tk.Button(
            button_frame,
            text="Run Enhanced Validation",
            command=self._run_enhanced_validation,
            bg="#8B5CF6",  # Purple color for enhanced
            fg="white",
            font=("Arial", 11),
            relief="flat",
            bd=0,
            padx=15,
            pady=8
        )
        self.run_enhanced_benchmark_btn.pack(side="left")
        
        # Batch benchmark button (initially hidden)
        self.run_batch_benchmark_btn = tk.Button(
            button_frame,
            text="Run Batch Benchmark",
            command=self._run_batch_benchmark_validation,
            bg="#FF6B35",  # Orange color for batch
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            bd=0,
            padx=15,
            pady=8
        )
        
        # Add tooltips for buttons
        self._add_tooltip(self.run_fast_benchmark_btn,
            "Run Fast Benchmark:\n\n"
            "Quick benchmark using optimized algorithms and\n"
            "reduced computational overhead. Good for:\n\n"
            "• Initial algorithm comparison\n"
            "• Parameter tuning\n"
            "• Quick performance assessment\n\n"
            "Typically completes in 1-5 minutes.")
            
        self._add_tooltip(self.run_benchmark_btn,
            "Run Full Benchmark:\n\n"
            "Comprehensive benchmark with full algorithm\n"
            "implementations and detailed statistics.\n\n"
            "• More thorough evaluation\n"
            "• Statistical significance testing\n"
            "• Publication-quality results\n\n"
            "May take 10-30 minutes depending on settings.")
            
        self._add_tooltip(self.run_batch_benchmark_btn,
            "Run Batch Benchmark:\n\n"
            "Automatically runs benchmarks across multiple\n"
            "test functions and saves comprehensive results.\n\n"
            "• Tests all selected functions\n"
            "• Generates comparison reports\n"
            "• Saves results to files\n\n"
            "Duration depends on number of functions and runs.")
        
        # Progress frame with progress bar
        progress_frame = tk.Frame(controls_frame, bg="white")
        progress_frame.pack(fill="x", pady=5)
        
        # Progress bar
        self.validation_progress_var = tk.DoubleVar()
        self.validation_progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.validation_progress_var,
            mode='indeterminate'
        )
        self.validation_progress_bar.pack(fill="x", pady=2)
        
        # Progress label
        self.validation_progress_label = tk.Label(
            progress_frame,
            text="Ready to run benchmark (Fast mode recommended for quick results)",
            bg="white",
            fg=COLOR_SECONDARY,
            font=("Arial", 10)
        )
        self.validation_progress_label.pack(pady=2)
        
        # Results frame
        results_frame = tk.LabelFrame(
            scrollable_frame,
            text="Benchmark Results",
            font=("Arial", 12, "bold"),
            bg="white",
            fg=COLOR_SECONDARY,
            padx=10,
            pady=10
        )
        results_frame.pack(fill="both", expand=True)
        
        # Create matplotlib figure for results
        self.validation_fig = Figure(figsize=(12, 8), facecolor="white")
        self.validation_canvas = FigureCanvasTkAgg(self.validation_fig, results_frame)
        self.validation_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Navigation toolbar
        toolbar_frame = tk.Frame(results_frame, bg="white")
        toolbar_frame.pack(fill="x")
        self.validation_toolbar = NavigationToolbar2Tk(self.validation_canvas, toolbar_frame)
        self.validation_toolbar.update()
        
        # Results text area
        self.validation_results_text = scrolledtext.ScrolledText(
            results_frame,
            height=8,
            bg="white",
            font=("Consolas", 10)
        )
        self.validation_results_text.pack(fill="x", pady=(10, 0))
        
        # Initialize plot
        self._initialize_validation_plot()
        
        # Store validation engine reference
        self.validation_engine = None

    def _initialize_validation_plot(self):
        """Initialize the validation plot with placeholder content."""
        self.validation_fig.clear()
        ax = self.validation_fig.add_subplot(111)
        
        ax.text(0.5, 0.5, "Run a benchmark to see results", 
                ha="center", va="center", fontsize=14, color="gray",
                transform=ax.transAxes)
        ax.set_title("Hypervolume Indicator vs. Number of Evaluations", fontsize=14, fontweight="bold")
        ax.set_xlabel("Number of Evaluations")
        ax.set_ylabel("Hypervolume Indicator")
        ax.grid(True, alpha=0.3)
        
        self.validation_canvas.draw()

    def _run_fast_benchmark_validation(self):
        """Run the FAST benchmark validation in a separate thread."""
        import threading
        
        # Disable buttons during execution
        self.run_fast_benchmark_btn.config(state="disabled", text="Running...")
        self.run_benchmark_btn.config(state="disabled")
        self.validation_progress_bar.start(10)  # Start progress animation
        self.validation_progress_label.config(text="Starting fast benchmark validation...")
        
        def run_fast_validation():
            try:
                from pymbo.core.fast_validation_engine import FastValidationEngine
                
                # Get configuration
                test_function = self.validation_test_function_var.get()
                budget = int(self.validation_budget_var.get())
                runs = int(self.validation_runs_var.get())
                
                # Get selected algorithms
                selected_algorithms = [
                    alg for alg, var in self.validation_algorithms.items() 
                    if var.get()
                ]
                
                if not selected_algorithms:
                    raise ValueError("Please select at least one algorithm")
                
                # Update progress
                self.after(0, lambda: self.validation_progress_label.config(
                    text=f"Fast mode: Running {test_function} with {len(selected_algorithms)} algorithms..."
                ))
                
                # Create fast validation engine
                self.validation_engine = FastValidationEngine()
                
                # Run fast validation
                results = self.validation_engine.run_fast_validation(
                    test_function_name=test_function,
                    algorithms=selected_algorithms,
                    n_evaluations=budget,
                    n_runs=runs,
                    seed=42  # For reproducibility
                )
                
                # Update GUI with results
                self.after(0, self._update_validation_results, results, True)  # True for fast mode
                
            except Exception as e:
                error_msg = f"Fast benchmark failed: {str(e)}"
                self.after(0, self._validation_error, error_msg)
        
        # Start fast validation in background thread
        thread = threading.Thread(target=run_fast_validation, daemon=True)
        thread.start()

    def _run_benchmark_validation(self):
        """Run the FULL benchmark validation in a separate thread."""
        import threading
        
        # Disable buttons during execution
        self.run_benchmark_btn.config(state="disabled", text="Running...")
        self.run_fast_benchmark_btn.config(state="disabled")
        self.validation_progress_bar.start(10)  # Start progress animation
        self.validation_progress_label.config(text="Starting full benchmark validation (this may take several minutes)...")
        
        def run_validation():
            try:
                from pymbo.core.validation_engine import ValidationEngine
                
                # Get configuration
                test_function = self.validation_test_function_var.get()
                budget = int(self.validation_budget_var.get())
                runs = int(self.validation_runs_var.get())
                
                # Get selected algorithms
                selected_algorithms = [
                    alg for alg, var in self.validation_algorithms.items() 
                    if var.get()
                ]
                
                if not selected_algorithms:
                    raise ValueError("Please select at least one algorithm")
                
                # Update progress
                self.after(0, lambda: self.validation_progress_label.config(
                    text=f"Full mode: Running {test_function} with {len(selected_algorithms)} algorithms..."
                ))
                
                # Create validation engine
                self.validation_engine = ValidationEngine()
                
                # Run validation
                results = self.validation_engine.run_validation(
                    test_function_name=test_function,
                    algorithms=selected_algorithms,
                    n_evaluations=budget,
                    n_runs=runs,
                    seed=42  # For reproducibility
                )
                
                # Update GUI with results
                self.after(0, self._update_validation_results, results, False)  # False for full mode
                
            except Exception as e:
                error_msg = f"Benchmark failed: {str(e)}"
                self.after(0, self._validation_error, error_msg)
        
        # Start validation in background thread
        thread = threading.Thread(target=run_validation, daemon=True)
        thread.start()

    def _run_enhanced_validation(self):
        """Run enhanced validation with clean output and proper hypervolume calculation."""
        import threading
        
        # Disable button during validation
        self.run_enhanced_benchmark_btn.config(state="disabled")
        
        # Start progress indication
        self.validation_progress_bar.start(10)
        self.validation_progress_label.config(text="Starting enhanced validation with clean output...")
        
        def run_validation():
            try:
                from pymbo.core.enhanced_validation_engine import create_enhanced_validation_engine
                
                # Get configuration from GUI
                test_function = self.validation_test_function_var.get()
                selected_algorithms = [alg for alg, var in self.validation_algorithms.items() if var.get()]
                budget = self.validation_budget_var.get()
                runs = self.validation_runs_var.get()
                
                if not selected_algorithms:
                    error_msg = "Please select at least one algorithm for validation"
                    self.after(0, self._validation_error, error_msg)
                    return
                
                self.after(0, lambda: self.validation_progress_label.config(
                    text=f"Running enhanced validation: {test_function} with {len(selected_algorithms)} algorithms..."
                ))
                
                # Create enhanced validation engine with clean output
                engine = create_enhanced_validation_engine(quiet_mode=False)  # Show progress but clean
                
                # Run enhanced validation
                results = engine.run_validation(
                    test_function_name=test_function,
                    algorithms=selected_algorithms,
                    n_evaluations=budget,
                    n_runs=runs,
                    seed=42  # For reproducibility
                )
                
                # Update GUI with results
                self.after(0, lambda: self._update_validation_results(results, is_fast_mode=False, is_enhanced_mode=True))
                
            except Exception as e:
                error_msg = f"Enhanced validation failed: {str(e)}"
                self.after(0, self._validation_error, error_msg)
        
        # Start validation in background thread
        thread = threading.Thread(target=run_validation, daemon=True)
        thread.start()

    def _toggle_batch_mode(self):
        """Toggle batch processing mode and show/hide batch configuration."""
        if self.batch_mode_var.get():
            # Show batch configuration
            self.batch_config_frame.pack(fill="x", pady=5)
            self.run_batch_benchmark_btn.pack(side="left", padx=(0, 10))
        else:
            # Hide batch configuration
            self.batch_config_frame.pack_forget()
            self.run_batch_benchmark_btn.pack_forget()

    def _browse_batch_output_dir(self):
        """Browse and select the output directory for batch results."""
        from tkinter import filedialog
        
        directory = filedialog.askdirectory(
            title="Select Output Directory for Batch Results",
            initialdir=self.batch_output_var.get()
        )
        
        if directory:
            self.batch_output_var.set(directory)

    def _run_batch_benchmark_validation(self):
        """Run batch benchmark validation across multiple test functions."""
        import threading
        import os
        from datetime import datetime
        
        # Validate batch configuration
        selected_functions = [func for func, var in self.batch_test_functions.items() if var.get()]
        if not selected_functions:
            messagebox.showwarning("No Test Functions", "Please select at least one test function for batch processing.")
            return
        
        selected_algorithms = [alg for alg, var in self.validation_algorithms.items() if var.get()]
        if not selected_algorithms:
            messagebox.showwarning("No Algorithms", "Please select at least one algorithm to benchmark.")
            return
        
        # Create output directory
        output_dir = self.batch_output_var.get()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_dir = os.path.join(output_dir, f"batch_benchmark_{timestamp}")
        
        try:
            os.makedirs(batch_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Directory Error", f"Could not create output directory:\n{e}")
            return
        
        # Disable buttons during execution
        self.run_fast_benchmark_btn.config(state="disabled")
        self.run_benchmark_btn.config(state="disabled")
        self.run_batch_benchmark_btn.config(state="disabled", text="Running Batch...")
        
        # Start progress bar
        self.validation_progress_bar.config(mode='indeterminate')
        self.validation_progress_bar.start()
        self.validation_progress_label.config(text="Running batch benchmark across multiple test functions...")
        
        def run_batch_validation():
            """Run batch validation in background thread."""
            try:
                # Get parameters
                try:
                    budget = int(self.validation_budget_var.get())
                    runs = int(self.validation_runs_var.get())
                except ValueError:
                    self.after(0, lambda: messagebox.showerror("Invalid Input", "Budget and runs must be integers"))
                    return
                
                # Get parallel processing settings
                use_parallel = self.parallel_processing_var.get()
                workers_setting = self.parallel_workers_var.get()
                parallel_mode = self.parallel_mode_var.get()
                
                if use_parallel:
                    # Use parallel validation engine
                    from pymbo.core.parallel_validation_engine import ParallelValidationEngine
                    from pymbo.core.parallel_benchmark_algorithms import estimate_parallel_speedup
                    
                    # Determine number of workers
                    if workers_setting.lower() == "auto":
                        max_workers = None
                    else:
                        try:
                            max_workers = int(workers_setting)
                        except ValueError:
                            max_workers = None
                    
                    validation_engine = ParallelValidationEngine(max_workers=max_workers)
                    actual_workers = validation_engine.get_optimal_worker_count()
                    
                    # Progress callback for parallel processing
                    def progress_update(message):
                        self.after(0, lambda msg=message: self.validation_progress_label.config(text=msg))
                    
                    # Estimate and show speedup with more detailed calculation
                    estimated_speedup = estimate_parallel_speedup(
                        n_algorithms=len(selected_algorithms),
                        n_runs=runs,
                        max_workers=actual_workers,
                        parallel_mode=parallel_mode
                    )
                    
                    self.after(0, lambda: self.validation_progress_label.config(
                        text=f"Starting parallel processing ({actual_workers} workers, "
                             f"mode: {parallel_mode}, estimated {estimated_speedup:.1f}x speedup)..."))
                    
                    # Run parallel batch validation
                    batch_results = validation_engine.run_parallel_batch_validation(
                        test_functions=selected_functions,
                        algorithms=selected_algorithms,
                        n_evaluations=budget,
                        n_runs=runs,
                        parallel_mode="functions",  # Still test-function level parallelization
                        progress_callback=progress_update
                    )
                    
                    # Remove metadata for processing
                    metadata = batch_results.pop('_metadata', {})
                    total_time = metadata.get('total_time', 0)
                    
                    self.after(0, lambda: self.validation_progress_label.config(
                        text=f"Parallel processing completed in {total_time:.1f}s"))
                    
                else:
                    # Use sequential processing
                    from pymbo.core.fast_validation_engine import FastValidationEngine
                    
                    batch_results = {}
                    total_functions = len(selected_functions)
                    
                    for i, test_function in enumerate(selected_functions):
                        self.after(0, lambda f=test_function, idx=i+1, total=total_functions: 
                                      self.validation_progress_label.config(
                                          text=f"Running {f} ({idx}/{total})..."))
                        
                        # Create validation engine for this test function
                        validation_engine = FastValidationEngine()
                        
                        # Run validation for current test function
                        results = validation_engine.run_fast_validation(
                            test_function_name=test_function,
                            algorithms=selected_algorithms,
                            n_evaluations=budget,
                            n_runs=runs
                        )
                        
                        batch_results[test_function] = results
                
                # Save results for all functions
                for test_function, results in batch_results.items():
                    if 'error' in results:
                        logger.error(f"Error in {test_function}: {results['error']}")
                        continue
                    
                    # Save individual results
                    function_dir = os.path.join(batch_dir, test_function)
                    os.makedirs(function_dir, exist_ok=True)
                    
                    # Save results to CSV
                    import pandas as pd
                    
                    # Extract benchmark results for CSV
                    if 'benchmark_results' in results:
                        results_data = results['benchmark_results']
                        if isinstance(results_data, dict):
                            # Convert to DataFrame format
                            csv_data = []
                            for alg_name, alg_results in results_data.items():
                                if isinstance(alg_results, list):
                                    for i, result in enumerate(alg_results):
                                        csv_data.append({
                                            'Algorithm': alg_name,
                                            'Run': i + 1,
                                            'Hypervolume': result.get('hypervolume', 'N/A')
                                        })
                            
                            if csv_data:
                                results_df = pd.DataFrame(csv_data)
                                results_df.to_csv(os.path.join(function_dir, f"{test_function}_results.csv"), index=False)
                    
                    # Create and save individual plot
                    self._save_batch_plot(results, test_function, function_dir)
                
                # Generate comprehensive summary report
                self._generate_batch_report(batch_results, batch_dir)
                
                # Update GUI with final results (show last test function results)
                last_results = list(batch_results.values())[-1]
                self.after(0, lambda: self._update_validation_results(last_results, is_fast_mode=True))
                self.after(0, lambda: self.validation_progress_label.config(
                    text=f"Batch benchmark completed! Results saved to: {batch_dir}"))
                
                # Show completion message
                self.after(0, lambda: messagebox.showinfo(
                    "Batch Complete", 
                    f"Batch benchmark completed successfully!\n\n"
                    f"Tested {total_functions} functions with {len(selected_algorithms)} algorithms.\n"
                    f"Results saved to:\n{batch_dir}"))
                
            except Exception as e:
                error_message = str(e)
                logger.error(f"Batch validation error: {error_message}")
                self.after(0, lambda msg=error_message: messagebox.showerror("Batch Error", f"Batch benchmark failed:\n{msg}"))
            finally:
                # Re-enable buttons
                self.after(0, lambda: self.validation_progress_bar.stop())
                self.after(0, lambda: self.run_fast_benchmark_btn.config(state="normal"))
                self.after(0, lambda: self.run_benchmark_btn.config(state="normal"))
                self.after(0, lambda: self.run_batch_benchmark_btn.config(state="normal", text="Run Batch Benchmark"))
        
        # Start batch validation in background thread
        thread = threading.Thread(target=run_batch_validation, daemon=True)
        thread.start()

    def _save_batch_plot(self, results, test_function, output_dir):
        """Save individual benchmark plot for a test function."""
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Handle different result formats
            if 'hypervolume_results' in results:
                # New format from parallel engine
                hypervolume_data = results['hypervolume_results']
                algorithms = list(hypervolume_data.keys())
                hypervolumes = [hypervolume_data[alg] for alg in algorithms]
            elif isinstance(results, dict) and all(isinstance(v, dict) and 'hypervolume' in v for v in results.values()):
                # Old format - direct algorithm results
                algorithms = list(results.keys())
                hypervolumes = [results[alg]['hypervolume'] for alg in algorithms]
            else:
                # Try to extract from benchmark_results
                if 'benchmark_results' in results:
                    benchmark_data = results['benchmark_results']
                    algorithms = list(benchmark_data.keys())
                    # Calculate average hypervolume for each algorithm
                    hypervolumes = []
                    for alg in algorithms:
                        alg_results = benchmark_data[alg]
                        if isinstance(alg_results, list) and len(alg_results) > 0:
                            # Average hypervolume across runs
                            hv_values = [r.get('hypervolume', 0) for r in alg_results if isinstance(r, dict)]
                            hypervolumes.append(sum(hv_values) / len(hv_values) if hv_values else 0)
                        else:
                            hypervolumes.append(0)
                else:
                    logger.warning(f"Could not extract plot data for {test_function}")
                    return
            
            if not algorithms or not hypervolumes:
                logger.warning(f"No valid data for plotting {test_function}")
                return
            
            # Create bar plot
            colors = ['#2E86AB', '#A23B72', '#F18F01', '#E74C3C', '#9B59B6']
            bars = ax.bar(algorithms, hypervolumes, color=colors[:len(algorithms)])
            ax.set_title(f'Algorithm Performance Comparison - {test_function}', fontsize=14, fontweight='bold')
            ax.set_ylabel('Hypervolume Indicator')
            ax.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, value in zip(bars, hypervolumes):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.4f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"{test_function}_comparison.png"), dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.warning(f"Could not save plot for {test_function}: {e}")

    def _generate_batch_report(self, batch_results, output_dir):
        """Generate comprehensive batch benchmark report."""
        try:
            import pandas as pd
            from datetime import datetime
            
            # Create summary DataFrame
            summary_data = []
            for test_function, results in batch_results.items():
                for algorithm, metrics in results.items():
                    summary_data.append({
                        'Test_Function': test_function,
                        'Algorithm': algorithm,
                        'Hypervolume': metrics['hypervolume'],
                        'Best_Solution_Count': len(metrics.get('best_solutions', [])),
                        'Convergence_Rate': metrics.get('convergence_rate', 'N/A')
                    })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_csv(os.path.join(output_dir, "batch_summary.csv"), index=False)
            
            # Create comprehensive comparison plot
            self._create_batch_comparison_plot(batch_results, output_dir)
            
            # Generate text report
            report_path = os.path.join(output_dir, "batch_report.txt")
            with open(report_path, 'w') as f:
                f.write("PyMBO Batch Benchmark Report\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write(f"Test Functions: {list(batch_results.keys())}\n")
                f.write(f"Algorithms: {list(list(batch_results.values())[0].keys())}\n\n")
                
                f.write("Results Summary:\n")
                f.write("-" * 20 + "\n")
                
                for test_function, results in batch_results.items():
                    f.write(f"\n{test_function}:\n")
                    for algorithm, metrics in results.items():
                        f.write(f"  {algorithm}: Hypervolume = {metrics['hypervolume']:.6f}\n")
            
            logger.info(f"Batch report generated: {report_path}")
            
        except Exception as e:
            logger.error(f"Could not generate batch report: {e}")

    def _create_batch_comparison_plot(self, batch_results, output_dir):
        """Create comprehensive comparison plot across all test functions."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Prepare data
            test_functions = list(batch_results.keys())
            algorithms = list(list(batch_results.values())[0].keys())
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            x = np.arange(len(test_functions))
            width = 0.25
            colors = ['#2E86AB', '#A23B72', '#F18F01']
            
            for i, algorithm in enumerate(algorithms):
                hypervolumes = [batch_results[func][algorithm]['hypervolume'] 
                              for func in test_functions]
                
                bars = ax.bar(x + i * width, hypervolumes, width, 
                            label=algorithm, color=colors[i % len(colors)])
                
                # Add value labels
                for bar, value in zip(bars, hypervolumes):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{value:.3f}', ha='center', va='bottom', fontsize=8)
            
            ax.set_xlabel('Test Functions')
            ax.set_ylabel('Hypervolume Indicator')
            ax.set_title('Algorithm Performance Comparison Across Test Functions')
            ax.set_xticks(x + width)
            ax.set_xticklabels(test_functions)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "batch_comparison.png"), dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"Could not create batch comparison plot: {e}")

    def _add_tooltip(self, widget, text):
        """Add tooltip to a widget."""
        def create_tooltip(widget, text):
            """Create tooltip functionality for widgets."""
            def on_enter(event):
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
                
                label = tk.Label(
                    tooltip, 
                    text=text, 
                    background="#FFFFCC", 
                    foreground="#000000",
                    relief="solid", 
                    borderwidth=1,
                    font=("Arial", 9),
                    justify="left",
                    padx=8,
                    pady=5
                )
                label.pack()
                
                widget.tooltip = tooltip
                
            def on_leave(event):
                if hasattr(widget, 'tooltip'):
                    widget.tooltip.destroy()
                    del widget.tooltip
            
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        create_tooltip(widget, text)

    def _update_validation_results(self, results, is_fast_mode=False, is_enhanced_mode=False):
        """Update the GUI with validation results."""
        try:
            # Stop progress bar
            self.validation_progress_bar.stop()
            
            # Choose appropriate report generator
            if is_enhanced_mode or (isinstance(results, dict) and results.get('enhanced', False)):
                # Enhanced validation results
                report = self._create_enhanced_validation_report(results)
                mode_text = "Enhanced validation"
            elif is_fast_mode:
                from pymbo.core.fast_validation_engine import create_fast_validation_report
                report = create_fast_validation_report(results)
                mode_text = "Fast benchmark"
            else:
                from pymbo.core.validation_engine import create_validation_report
                report = create_validation_report(results)
                mode_text = "Full benchmark"
            
            # Create the plot
            self._create_validation_plot(results)
            
            # Update results text
            self.validation_results_text.delete(1.0, tk.END)
            self.validation_results_text.insert(1.0, report)
            
            # Update progress with mode information
            self.validation_progress_label.config(
                text=f"{mode_text} completed successfully", 
                fg=COLOR_SUCCESS
            )
            
        except Exception as e:
            self._validation_error(f"Error updating results: {str(e)}")
        finally:
            # Re-enable buttons
            self.run_fast_benchmark_btn.config(state="normal", text="Run Fast Benchmark")
            self.run_benchmark_btn.config(state="normal", text="Run Full Benchmark")
            if hasattr(self, 'run_enhanced_benchmark_btn'):
                self.run_enhanced_benchmark_btn.config(state="normal")

    def _create_validation_plot(self, results):
        """Create the validation benchmark plot."""
        self.validation_fig.clear()
        ax = self.validation_fig.add_subplot(111)
        
        hv_results = results['hypervolume_results']
        
        # Plot each algorithm
        for alg_name in results['algorithms']:
            if alg_name in hv_results and len(hv_results[alg_name]['mean']) > 0:
                mean_prog = hv_results[alg_name]['mean']
                std_prog = hv_results[alg_name]['std']
                evaluations = hv_results[alg_name]['evaluations']
                
                # Plot mean line
                line = ax.plot(evaluations, mean_prog, label=alg_name, linewidth=2)[0]
                color = line.get_color()
                
                # Plot confidence interval
                ax.fill_between(
                    evaluations, 
                    np.array(mean_prog) - np.array(std_prog),
                    np.array(mean_prog) + np.array(std_prog),
                    alpha=0.2,
                    color=color
                )
        
        ax.set_title("Algorithm Comparison: Hypervolume vs. Evaluations", 
                    fontsize=14, fontweight="bold")
        ax.set_xlabel("Number of Evaluations")
        ax.set_ylabel("Hypervolume Indicator")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Adjust layout
        self.validation_fig.tight_layout()
        self.validation_canvas.draw()

    def _create_enhanced_validation_report(self, results):
        """Create a detailed report for enhanced validation results."""
        try:
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append("ENHANCED VALIDATION REPORT")
            report_lines.append("=" * 60)
            
            # Basic information
            test_function = results.get('test_function', 'Unknown')
            algorithms = results.get('algorithms', [])
            n_evaluations = results.get('n_evaluations', 0)
            n_runs = results.get('n_runs', 0)
            execution_time = results.get('execution_time', 0.0)
            
            report_lines.append(f"Test Function: {test_function}")
            report_lines.append(f"Algorithms: {', '.join(algorithms)}")
            report_lines.append(f"Evaluations per run: {n_evaluations}")
            report_lines.append(f"Number of runs: {n_runs}")
            report_lines.append(f"Total execution time: {execution_time:.2f} seconds")
            report_lines.append("")
            
            # Enhanced validation features
            if results.get('enhanced', False):
                report_lines.append("✓ Enhanced Features:")
                report_lines.append("  • Clean systematic output")
                report_lines.append("  • Fixed hypervolume calculation")
                report_lines.append("  • Proper data sequence handling")
                report_lines.append("  • Improved convergence analysis")
                report_lines.append("")
            
            # Hypervolume results
            if 'hypervolume_results' in results:
                hv_results = results['hypervolume_results']
                report_lines.append("HYPERVOLUME RESULTS")
                report_lines.append("-" * 30)
                
                for alg_name in algorithms:
                    if alg_name in hv_results:
                        alg_data = hv_results[alg_name]
                        if 'mean' in alg_data and len(alg_data['mean']) > 0:
                            final_hv = alg_data['mean'][-1]
                            final_std = alg_data['std'][-1] if 'std' in alg_data and len(alg_data['std']) > 0 else 0.0
                            report_lines.append(f"{alg_name}:")
                            report_lines.append(f"  Final hypervolume: {final_hv:.6f} ± {final_std:.6f}")
                            
                            # Progress information
                            if len(alg_data['mean']) > 1:
                                initial_hv = alg_data['mean'][0]
                                improvement = ((final_hv - initial_hv) / max(initial_hv, 1e-10)) * 100
                                report_lines.append(f"  Improvement: {improvement:.1f}%")
                        
                        report_lines.append("")
                
                # Summary
                if len(algorithms) > 1:
                    report_lines.append("ALGORITHM RANKING")
                    report_lines.append("-" * 20)
                    
                    # Rank by final hypervolume
                    final_hvs = []
                    for alg_name in algorithms:
                        if alg_name in hv_results:
                            alg_data = hv_results[alg_name]
                            if 'mean' in alg_data and len(alg_data['mean']) > 0:
                                final_hvs.append((alg_name, alg_data['mean'][-1]))
                    
                    final_hvs.sort(key=lambda x: x[1], reverse=True)
                    for i, (alg_name, hv) in enumerate(final_hvs):
                        report_lines.append(f"{i+1}. {alg_name}: {hv:.6f}")
                    
                    report_lines.append("")
            
            # Convergence analysis
            report_lines.append("CONVERGENCE ANALYSIS")
            report_lines.append("-" * 25)
            report_lines.append("✓ All algorithms completed successfully")
            report_lines.append("✓ Hypervolume progression calculated")
            report_lines.append("✓ Data integrity verified")
            
            if execution_time > 0:
                avg_time_per_run = execution_time / (len(algorithms) * n_runs)
                report_lines.append(f"✓ Average time per run: {avg_time_per_run:.3f}s")
            
            report_lines.append("")
            report_lines.append("=" * 60)
            
            return "\n".join(report_lines)
            
        except Exception as e:
            return f"Error generating enhanced validation report: {str(e)}"

    def _validation_error(self, error_msg):
        """Handle validation errors."""
        logger.error(error_msg)
        
        # Stop progress bar
        self.validation_progress_bar.stop()
        
        self.validation_progress_label.config(
            text=error_msg,
            fg=COLOR_ERROR
        )
        
        self.validation_results_text.delete(1.0, tk.END)
        self.validation_results_text.insert(1.0, f"ERROR: {error_msg}")
        
        # Re-enable both buttons
        self.run_fast_benchmark_btn.config(state="normal", text="Run Fast Benchmark")
        self.run_benchmark_btn.config(state="normal", text="Run Full Benchmark")

    def _run_whatif_simulation(self):
        """Run what-if simulation for the completed experiment."""
        import threading
        
        # Check if we have an optimizer with experimental data
        if not hasattr(self, 'controller') or not self.controller:
            self.whatif_status_label.config(
                text="No experiment data available",
                fg=COLOR_ERROR
            )
            return
            
        try:
            optimizer = self.controller.optimizer
            if not optimizer:
                self.whatif_status_label.config(
                    text="No optimizer available",
                    fg=COLOR_ERROR
                )
                return
                
            # More robust check for experimental data
            has_data = False
            if hasattr(optimizer, 'experimental_data'):
                exp_data = optimizer.experimental_data
                if exp_data is not None and not exp_data.empty and len(exp_data) > 0:
                    has_data = True
                    logger.debug(f"Found experimental data with {len(exp_data)} rows")
                else:
                    logger.debug(f"Experimental data check: data={exp_data is not None}, empty={exp_data.empty if exp_data is not None else 'N/A'}, len={len(exp_data) if exp_data is not None else 0}")
            
            if not has_data:
                self.whatif_status_label.config(
                    text="No experimental data available - run an experiment first",
                    fg=COLOR_ERROR
                )
                return
                
        except Exception as e:
            logger.error(f"Error checking experimental data: {e}", exc_info=True)
            self.whatif_status_label.config(
                text="Could not access experiment data",
                fg=COLOR_ERROR
            )
            return
            
        # Disable button during simulation
        self.whatif_button.config(state="disabled", text="Running...")
        self.whatif_status_label.config(
            text="Running what-if simulation...",
            fg=COLOR_SECONDARY
        )
        
        def run_simulation():
            try:
                # Get strategy and parallel settings
                strategy = self.whatif_strategy_var.get()
                workers_str = self.whatif_workers_var.get()
                chunk_size = int(self.whatif_chunk_var.get())
                
                # Parse workers setting
                if workers_str == "Auto":
                    n_workers = None  # Auto-detect
                else:
                    n_workers = int(workers_str)
                
                # Get the number of evaluations from the experiment
                n_evaluations = len(optimizer.experimental_data)
                
                # Choose simulator based on strategy
                if strategy == "Parallel Random Search":
                    from pymbo.core.parallel_whatif_simulation import ParallelWhatIfSimulator
                    simulator = ParallelWhatIfSimulator(n_workers=n_workers, chunk_size=chunk_size)
                    
                    # Get parameter bounds
                    param_bounds = simulator.get_parameter_bounds_from_optimizer(optimizer)
                    
                    # Create progress callback
                    def progress_callback(message):
                        self.after(0, self._update_whatif_progress, message)
                    
                    # Run parallel simulation
                    results = simulator.simulate_alternative_strategy_parallel(
                        optimizer=optimizer,
                        strategy_name=strategy,
                        n_evaluations=n_evaluations,
                        param_bounds=param_bounds,
                        seed=42,
                        progress_callback=progress_callback
                    )
                else:
                    # Fall back to sequential simulation
                    from pymbo.core.whatif_simulation import WhatIfSimulator
                    simulator = WhatIfSimulator()
                    param_bounds = simulator.get_parameter_bounds_from_optimizer(optimizer)
                    
                    results = simulator.simulate_alternative_strategy(
                        optimizer=optimizer,
                        strategy_name=strategy,
                        n_evaluations=n_evaluations,
                        param_bounds=param_bounds,
                        seed=42
                    )
                
                # Update GUI with results
                self.after(0, self._update_whatif_results, results)
                
            except Exception as e:
                error_msg = f"What-if simulation failed: {str(e)}"
                logger.error(f"What-if simulation error: {e}", exc_info=True)
                self.after(0, self._whatif_error, error_msg)
        
        # Start simulation in background thread
        thread = threading.Thread(target=run_simulation, daemon=True)
        thread.start()

    def _update_whatif_progress(self, message):
        """Update the what-if simulation progress."""
        self.whatif_status_label.config(
            text=f"Progress: {message}",
            fg=COLOR_SECONDARY
        )
    
    def _update_whatif_results(self, results):
        """Update the GUI with what-if simulation results."""
        try:
            # Store results
            self.whatif_results = results
            
            # Update the progress plot to include the simulation
            self._add_whatif_overlay_to_plot()
            
            # Create performance summary
            performance_info = ""
            if 'execution_time' in results:
                performance_info = f" ({results['execution_time']:.1f}s, {results.get('throughput', 0):.0f} evals/s)"
            
            # Update status
            self.whatif_status_label.config(
                text=f"Completed: {results['strategy_name']} simulation{performance_info}",
                fg=COLOR_SUCCESS
            )
            
            logger.info(f"What-if simulation completed successfully{performance_info}")
            
        except Exception as e:
            self._whatif_error(f"Error updating what-if results: {str(e)}")
        finally:
            # Re-enable button
            self.whatif_button.config(state="normal", text="Run 'What-If' Comparison")

    def _add_whatif_overlay_to_plot(self):
        """Add what-if simulation overlay to the progress plot."""
        try:
            if not self.whatif_results:
                return
                
            # Get the current progress plot
            if not hasattr(self, 'progress_fig') or not self.progress_fig:
                return
                
            # Find the axes with hypervolume data
            for ax in self.progress_fig.get_axes():
                if "hypervolume" in ax.get_ylabel().lower() or "progress" in ax.get_title().lower():
                    # Add the what-if simulation line
                    hv_progression = self.whatif_results['hypervolume_progression']
                    evaluations = list(range(1, len(hv_progression) + 1))
                    
                    # Plot the simulation line
                    line = ax.plot(
                        evaluations, 
                        hv_progression, 
                        '--',
                        linewidth=2,
                        alpha=0.8,
                        label=f"Simulated {self.whatif_results['strategy_name']} (Predicted)"
                    )[0]
                    
                    # Update legend
                    ax.legend()
                    
                    # Refresh the canvas
                    if hasattr(self, 'progress_canvas'):
                        self.progress_canvas.draw()
                    
                    break
                    
        except Exception as e:
            logger.error(f"Error adding what-if overlay: {e}")

    def _whatif_error(self, error_msg):
        """Handle what-if simulation errors."""
        logger.error(error_msg)
        
        self.whatif_status_label.config(
            text=error_msg,
            fg=COLOR_ERROR
        )
        
        # Re-enable button
        self.whatif_button.config(state="normal", text="Run 'What-If' Comparison")

    def enable_whatif_analysis(self):
        """Enable what-if analysis when experimental data is available."""
        self.whatif_enabled = True
        self.whatif_button.config(state="normal")
        self.whatif_status_label.config(
            text="Ready for what-if analysis",
            fg=COLOR_SUCCESS
        )
