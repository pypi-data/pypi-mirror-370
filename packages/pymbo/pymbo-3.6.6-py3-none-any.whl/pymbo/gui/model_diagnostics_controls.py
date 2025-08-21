"""
Enhanced Model Diagnostics Control Module

This module provides an advanced graphical user interface for controlling Model 
Diagnostics plot visualizations within the PyMBO optimization framework. It implements 
dynamic diagnostic tool selection, response parameter controls, and seamless integration with 
the existing GUI architecture as a popout window.

Key Features:
- Dynamic diagnostic tool selection (Residuals, Parity, Uncertainty, Feature Importance)
- Response parameter selection for analysis target
- Granular control over plot appearance (style, colormap, resolution)
- Real-time plot updates with manual refresh functionality
- Scrollable popout window for better accessibility
- Consistent design language adherence
- DPI export functionality
- Axis range controls with auto/manual settings

Classes:
    ModelDiagnosticsControlPanel: Main control panel class for Model Diagnostics plot management
    
Functions:
    create_model_diagnostics_control_panel: Factory function for control panel instantiation

Author: PyMBO Development Team
Version: 3.6.6 Enhanced (Popout Window)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Callable, List, Optional, Tuple

# Import color constants from main GUI module
try:
    from .gui import (
        COLOR_PRIMARY, COLOR_SECONDARY, COLOR_SUCCESS, COLOR_WARNING, 
        COLOR_ERROR, COLOR_BACKGROUND, COLOR_SURFACE
    )
except ImportError:
    # Fallback color scheme if import fails
    COLOR_PRIMARY = "#1976D2"
    COLOR_SECONDARY = "#424242"
    COLOR_SUCCESS = "#4CAF50"
    COLOR_WARNING = "#FF9800"
    COLOR_ERROR = "#F44336"
    COLOR_BACKGROUND = "#FAFAFA"
    COLOR_SURFACE = "#FFFFFF"

logger = logging.getLogger(__name__)


class ModelDiagnosticsControlPanel:
    """
    Advanced control panel for Model Diagnostics plot visualization management in a separate popout window.
    
    This class provides comprehensive control over Model Diagnostics plot rendering, including
    dynamic diagnostic tool selection, response parameter selection, and display options management. 
    It operates as a separate window for better accessibility and flexibility.
    
    Attributes:
        parent: Parent Tkinter widget
        plot_type: Type identifier for the plot ("model_diagnostics")
        params_config: Configuration dictionary for optimization parameters
        responses_config: Configuration dictionary for response variables
        update_callback: Callback function for plot updates
        popup_window: Separate Toplevel window for the control panel
        main_frame: Primary container frame for the control panel
        scroll_canvas: Canvas widget for scrollable content
        scroll_frame: Scrollable frame container
        diagnostic_type_var: StringVar for diagnostic tool selection
        response_var: StringVar for response parameter selection
        display_options: Dictionary of BooleanVar objects for display controls
        available_parameters: List of available parameters
        available_responses: List of available responses for analysis
        dpi_var: IntVar for export DPI selection
        x_min_var: StringVar for X-axis minimum value
        x_max_var: StringVar for X-axis maximum value
        x_auto_var: BooleanVar for X-axis auto-scaling
        y_min_var: StringVar for Y-axis minimum value
        y_max_var: StringVar for Y-axis maximum value
        y_auto_var: BooleanVar for Y-axis auto-scaling
    """
    def __init__(self, parent: tk.Widget, plot_type: str, 
                 params_config: Dict[str, Any] = None,
                 responses_config: Dict[str, Any] = None,
                 update_callback: Callable = None):
        """
        Initialize the Model Diagnostics plot control panel in a separate popout window.
        
        Args:
            parent: Parent Tkinter widget for the control panel
            plot_type: Type identifier, should be "model_diagnostics"
            params_config: Dictionary containing parameter configurations
            responses_config: Dictionary containing response configurations
            update_callback: Function to call when plot updates are needed
        """
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        
        # Initialize window references
        self.popup_window = None
        self.main_frame = None
        self.scroll_canvas = None
        self.scroll_frame = None
        
        # Initialize available options
        self._initialize_available_options()
        
        # Initialize control variables
        self._initialize_control_variables()
        
        # Window is created but not shown initially
        self._create_popup_window()
        
        logger.info(f"Model Diagnostics control panel initialized for plot type: {plot_type}")
    
    def _initialize_available_options(self) -> None:
        """Initialize available parameter and response options from configuration."""
        self.available_parameters = list(self.params_config.keys()) if self.params_config else []
        self.available_responses = list(self.responses_config.keys()) if self.responses_config else []
        
        logger.debug(f"Available parameters: {self.available_parameters}")
        logger.debug(f"Available responses: {self.available_responses}")
    
    def _initialize_control_variables(self) -> None:
        """Initialize all Tkinter control variables with default values."""
        
        # Diagnostic tool selection
        self.diagnostic_type_var = tk.StringVar(value="residuals")
        
        # Response selection 
        default_response = self.available_responses[0] if self.available_responses else ""
        self.response_var = tk.StringVar(value=default_response)
        
        # Display options
        self.display_options = {
            'show_data_points': tk.BooleanVar(value=True),
            'show_reference_line': tk.BooleanVar(value=True),
            'show_statistics': tk.BooleanVar(value=True),
            'show_uncertainty_bands': tk.BooleanVar(value=False),
            'show_grid': tk.BooleanVar(value=True)
        }
        
        # Axis range controls
        self.x_min_var = tk.StringVar(value="auto")
        self.x_max_var = tk.StringVar(value="auto")
        self.x_auto_var = tk.BooleanVar(value=True)
        self.y_min_var = tk.StringVar(value="auto")
        self.y_max_var = tk.StringVar(value="auto")
        self.y_auto_var = tk.BooleanVar(value=True)
        
        # Export settings
        self.dpi_var = tk.IntVar(value=300)
        
        # Advanced settings
        self.point_size_var = tk.DoubleVar(value=50)
        self.point_alpha_var = tk.DoubleVar(value=0.7)
        self.point_color_var = tk.StringVar(value="blue")
        self.reference_line_style_var = tk.StringVar(value="dashed")
        self.reference_line_color_var = tk.StringVar(value="red")
        self.stats_position_var = tk.StringVar(value="upper_left")
        self.confidence_level_var = tk.DoubleVar(value=0.95)
        self.importance_threshold_var = tk.DoubleVar(value=0.01)
        self.max_features_var = tk.IntVar(value=10)
        
        logger.debug("Control variables initialized with default values")
    
    def _create_popup_window(self) -> None:
        """Create the popup window with proper styling and layout."""
        if self.popup_window is not None:
            return
            
        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.title("🎛️ Model Diagnostics Controls")
        self.popup_window.geometry("520x800")
        self.popup_window.minsize(480, 600)
        self.popup_window.configure(bg=COLOR_BACKGROUND)
        
        # Set window icon and properties
        self.popup_window.transient(self.parent)
        
        # Create main frame with styling
        self.main_frame = tk.Frame(self.popup_window, bg=COLOR_SURFACE, padx=20, pady=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create title header
        self._create_title_header()
        
        # Create scrollable content area
        self._create_scrollable_content()
        
        # Create control sections
        self._create_diagnostic_controls()
        self._create_visibility_controls() 
        self._create_axis_range_controls()
        self._create_export_controls()
        
        # Create action buttons
        self._create_action_buttons()
        
        # Configure scrolling
        self._configure_scrolling()
        
        # Setup event bindings
        self._setup_event_bindings()
        
        # Initially hide the window
        self.popup_window.withdraw()
        
        logger.info("Model Diagnostics popup window created successfully")
    
    def _create_title_header(self):
        """Create the title header with consistent typography and styling."""
        header_frame = tk.Frame(self.main_frame, bg=COLOR_PRIMARY, height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Model Diagnostics Controls",
            bg=COLOR_PRIMARY,
            fg=COLOR_SURFACE,
            font=("Arial", 12, "bold")
        )
        title_label.pack(expand=True)
    
    def _create_scrollable_content(self) -> None:
        """
        Create the scrollable content area with proper viewport management.
        """
        # Canvas and scrollbar for scrollable content
        canvas_frame = tk.Frame(self.main_frame, bg=COLOR_SURFACE)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.scroll_canvas = tk.Canvas(
            canvas_frame,
            bg=COLOR_SURFACE,
            highlightthickness=0
        )
        
        self.scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=self.scroll_canvas.yview
        )
        
        self.scroll_frame = tk.Frame(self.scroll_canvas, bg=COLOR_SURFACE)
        
        # Pack scrollbar and canvas
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure canvas scrolling
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas_frame_id = self.scroll_canvas.create_window(
            (0, 0), 
            window=self.scroll_frame, 
            anchor="nw"
        )
    
    def _create_diagnostic_controls(self) -> None:
        """Create diagnostic tool selection controls."""
        # Diagnostic Tool Selection Frame
        diag_frame = tk.LabelFrame(
            self.scroll_frame,
            text="Diagnostic Tool Selection",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        diag_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Diagnostic options
        diagnostic_options = [
            ("residuals", "Residuals Plot", "Analysis of prediction errors"),
            ("parity", "Parity Plot", "Predicted vs Actual comparison"),
            ("uncertainty", "Uncertainty Analysis", "Prediction confidence visualization"),
            ("feature_importance", "Feature Importance", "Parameter sensitivity analysis")
        ]
        
        for value, text, desc in diagnostic_options:
            option_frame = tk.Frame(diag_frame, bg=COLOR_SURFACE)
            option_frame.pack(fill=tk.X, pady=2)
            
            tk.Radiobutton(
                option_frame,
                text=text,
                variable=self.diagnostic_type_var,
                value=value,
                bg=COLOR_SURFACE,
                fg=COLOR_SECONDARY,
                font=("Arial", 9),
                activebackground=COLOR_BACKGROUND,
                selectcolor=COLOR_SURFACE
            ).pack(side=tk.LEFT)
            
            tk.Label(
                option_frame,
                text=f"({desc})",
                bg=COLOR_SURFACE,
                fg=COLOR_WARNING,
                font=("Arial", 8, "italic")
            ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Response Selection
        response_frame = tk.Frame(diag_frame, bg=COLOR_SURFACE)
        response_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            response_frame,
            text="Response:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.response_combo = ttk.Combobox(
            response_frame,
            textvariable=self.response_var,
            values=self.available_responses,
            state="readonly",
            width=20
        )
        self.response_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Data availability info
        self.data_info_frame = tk.Frame(diag_frame, bg=COLOR_SURFACE)
        self.data_info_frame.pack(fill=tk.X, pady=(5, 0))
        
        if not self.available_responses:
            tk.Label(
                self.data_info_frame,
                text="⚠ No optimization data loaded. Import data to enable model diagnostics.",
                bg=COLOR_SURFACE,
                fg=COLOR_WARNING,
                font=("Arial", 8, "italic"),
                wraplength=400
            ).pack(anchor=tk.W)
    
    def _create_visibility_controls(self) -> None:
        """Create display options and visibility controls."""
        vis_frame = tk.LabelFrame(
            self.scroll_frame,
            text="Display Options",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        vis_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Display checkboxes
        display_options = [
            ('show_data_points', "Show Data Points", "Display individual data points"),
            ('show_reference_line', "Show Reference Line", "Display reference/ideal line"),
            ('show_statistics', "Show Statistics", "Display statistical metrics"),
            ('show_uncertainty_bands', "Show Uncertainty Bands", "Display prediction uncertainty"),
            ('show_grid', "Show Grid", "Display grid lines")
        ]
        
        for key, text, desc in display_options:
            option_frame = tk.Frame(vis_frame, bg=COLOR_SURFACE)
            option_frame.pack(fill=tk.X, pady=2)
            
            tk.Checkbutton(
                option_frame,
                text=text,
                variable=self.display_options[key],
                bg=COLOR_SURFACE,
                fg=COLOR_SECONDARY,
                font=("Arial", 9),
                activebackground=COLOR_BACKGROUND,
                selectcolor=COLOR_SURFACE
            ).pack(side=tk.LEFT)
            
            tk.Label(
                option_frame,
                text=f"({desc})",
                bg=COLOR_SURFACE,
                fg=COLOR_WARNING,
                font=("Arial", 8, "italic")
            ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Style Settings Frame (simplified to match benchmark pattern)
        style_frame = tk.Frame(vis_frame, bg=COLOR_SURFACE)
        style_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Point styling - simplified to match benchmark
        point_frame = tk.Frame(style_frame, bg=COLOR_SURFACE)
        point_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            point_frame,
            text="Point Size:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        point_scale = tk.Scale(
            point_frame,
            from_=10, to=200,
            variable=self.point_size_var,
            orient=tk.HORIZONTAL,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 8),
            highlightthickness=0,
            length=100
        )
        point_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_axis_range_controls(self) -> None:
        """Create axis range control section."""
        axis_frame = tk.LabelFrame(
            self.scroll_frame,
            text="Axis Range Controls",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        axis_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # X-axis section (matching benchmark style)
        x_frame = tk.Frame(axis_frame, bg=COLOR_SURFACE)
        x_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            x_frame,
            text="X-Axis Range:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(anchor=tk.W)
        
        x_entry_frame = tk.Frame(x_frame, bg=COLOR_SURFACE)
        x_entry_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            x_entry_frame,
            text="Min:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 8)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.x_min_entry = tk.Entry(
            x_entry_frame,
            textvariable=self.x_min_var,
            width=8,
            font=("Arial", 8)
        )
        self.x_min_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            x_entry_frame,
            text="Max:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 8)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.x_max_entry = tk.Entry(
            x_entry_frame,
            textvariable=self.x_max_var,
            width=8,
            font=("Arial", 8)
        )
        self.x_max_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Checkbutton(
            x_entry_frame,
            text="Auto",
            variable=self.x_auto_var,
            command=self._toggle_x_range_controls,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 8),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        # Y-axis section
        y_frame = tk.Frame(axis_frame, bg=COLOR_SURFACE)
        y_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            y_frame,
            text="Y-Axis Range:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(anchor=tk.W)
        
        y_entry_frame = tk.Frame(y_frame, bg=COLOR_SURFACE)
        y_entry_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            y_entry_frame,
            text="Min:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 8)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.y_min_entry = tk.Entry(
            y_entry_frame,
            textvariable=self.y_min_var,
            width=8,
            font=("Arial", 8)
        )
        self.y_min_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            y_entry_frame,
            text="Max:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 8)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.y_max_entry = tk.Entry(
            y_entry_frame,
            textvariable=self.y_max_var,
            width=8,
            font=("Arial", 8)
        )
        self.y_max_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Checkbutton(
            y_entry_frame,
            text="Auto",
            variable=self.y_auto_var,
            command=self._toggle_y_range_controls,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 8),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
    
    def _toggle_x_range_controls(self):
        """Toggle X-axis range entry controls based on auto-scale checkbox."""
        if self.x_auto_var.get():
            self.x_min_entry.config(state="disabled")
            self.x_max_entry.config(state="disabled")
            self.x_min_var.set("auto")
            self.x_max_var.set("auto")
        else:
            self.x_min_entry.config(state="normal")
            self.x_max_entry.config(state="normal")
    
    def _toggle_y_range_controls(self):
        """Toggle Y-axis range entry controls based on auto-scale checkbox."""
        if self.y_auto_var.get():
            self.y_min_entry.config(state="disabled")
            self.y_max_entry.config(state="disabled")
            self.y_min_var.set("auto")
            self.y_max_var.set("auto")
        else:
            self.y_min_entry.config(state="normal")
            self.y_max_entry.config(state="normal")
    
    def _create_export_controls(self) -> None:
        """Create export control section."""
        export_frame = tk.LabelFrame(
            self.scroll_frame,
            text="Export Settings",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        export_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # DPI selection
        dpi_frame = tk.Frame(export_frame, bg=COLOR_SURFACE)
        dpi_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            dpi_frame,
            text="Export DPI:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        dpi_combo = ttk.Combobox(
            dpi_frame,
            textvariable=self.dpi_var,
            values=[150, 300, 600, 1200],
            state="readonly",
            width=8
        )
        dpi_combo.pack(side=tk.LEFT)
        
        # Export button frame
        export_btn_frame = tk.Frame(export_frame, bg=COLOR_SURFACE)
        export_btn_frame.pack(fill=tk.X, pady=5)
        
        export_btn = tk.Button(
            export_btn_frame,
            text="Export Plot",
            bg=COLOR_SUCCESS,
            fg=COLOR_SURFACE,
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=15,
            pady=5,
            command=self._export_plot
        )
        export_btn.pack()
    
    def _create_action_buttons(self) -> None:
        """Create action button section at the bottom of the main frame."""
        button_frame = tk.Frame(self.main_frame, bg=COLOR_PRIMARY, height=50)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        button_frame.pack_propagate(False)
        
        # Refresh button
        refresh_btn = tk.Button(
            button_frame,
            text="Refresh Plot",
            bg=COLOR_SURFACE,
            fg=COLOR_PRIMARY,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            command=self._refresh_plot
        )
        refresh_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            bg=COLOR_ERROR,
            fg=COLOR_SURFACE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            command=self.hide
        )
        close_btn.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def _configure_scrolling(self):
        """Configure canvas scrolling behavior."""
        def _on_frame_configure(event):
            """Update scroll region when frame size changes."""
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        
        def _on_canvas_configure(event):
            """Update frame width when canvas size changes."""
            canvas_width = event.width
            self.scroll_canvas.itemconfig(self.canvas_frame_id, width=canvas_width)
        
        def _on_mousewheel(event):
            """Handle mouse wheel scrolling."""
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind events
        self.scroll_frame.bind("<Configure>", _on_frame_configure)
        self.scroll_canvas.bind("<Configure>", _on_canvas_configure)
        
        # Bind mouse wheel to canvas and all child widgets
        self._bind_mousewheel_recursive(self.scroll_canvas, _on_mousewheel)
        self._bind_mousewheel_recursive(self.scroll_frame, _on_mousewheel)
    
    def _bind_mousewheel_recursive(self, widget: tk.Widget, callback: Callable) -> None:
        """Recursively bind mousewheel events to widget and all children."""
        widget.bind("<MouseWheel>", callback)
        widget.bind("<Button-4>", lambda e: callback(type('', (), {'delta': 120})()))
        widget.bind("<Button-5>", lambda e: callback(type('', (), {'delta': -120})()))
        
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child, callback)
    
    def _setup_event_bindings(self) -> None:
        """Setup event bindings for window management."""
        self.popup_window.protocol("WM_DELETE_WINDOW", self.hide)
        
        # Focus management
        self.popup_window.bind("<FocusIn>", lambda e: self.popup_window.lift())
    
    def _refresh_plot(self) -> None:
        """Refresh the plot with current settings (manual update only)."""
        # Check if we have data available
        if not self.available_responses:
            messagebox.showwarning(
                "No Data Available", 
                "No optimization data is loaded.\n\n"
                "To use model diagnostics:\n"
                "1. Load experimental data via File → Import Data\n"
                "2. Run optimization to generate models\n"
                "3. Return to this tab to analyze results"
            )
            return
            
        if not self.response_var.get():
            messagebox.showwarning(
                "No Response Selected", 
                "Please select a response variable from the dropdown to analyze."
            )
            return
        
        if self.update_callback:
            try:
                self.update_callback()
                logger.info("Plot refreshed successfully")
            except Exception as e:
                logger.error(f"Error refreshing plot: {e}")
                # Provide more helpful error message
                error_msg = str(e)
                if "No valid data" in error_msg or "not available" in error_msg:
                    messagebox.showwarning(
                        "Data Not Available", 
                        f"Cannot create model diagnostics plot:\n\n{error_msg}\n\n"
                        "This usually means:\n"
                        "• No optimization has been run yet\n"
                        "• Insufficient data points for modeling\n"
                        "• Selected response has no valid data"
                    )
                else:
                    messagebox.showerror("Refresh Error", f"Failed to refresh plot: {error_msg}")
        else:
            messagebox.showwarning(
                "No Update Callback", 
                "Plot update functionality is not available.\n"
                "This may indicate a GUI initialization issue."
            )
    
    def _export_plot(self) -> None:
        """Export the current plot with selected DPI."""
        logger.info(f"Export plot requested with DPI: {self.dpi_var.get()}")
        # Export functionality would be implemented by the parent GUI
        messagebox.showinfo("Export", f"Export plot functionality with DPI {self.dpi_var.get()}")
    
    def get_display_options(self) -> Dict[str, Any]:
        """
        Get current display options configuration.
        
        Returns:
            Dictionary containing all current display option settings
        """
        options = {
            'diagnostic_type': self.diagnostic_type_var.get(),
            'response_name': self.response_var.get(),
            'point_size': self.point_size_var.get(),
            'point_alpha': self.point_alpha_var.get(),
            'point_color': self.point_color_var.get(),
            'reference_line_style': self.reference_line_style_var.get(),
            'reference_line_color': self.reference_line_color_var.get(),
            'stats_position': self.stats_position_var.get(),
            'confidence_level': self.confidence_level_var.get(),
            'importance_threshold': self.importance_threshold_var.get(),
            'max_features': self.max_features_var.get()
        }
        
        # Add display options
        for key, var in self.display_options.items():
            options[key] = var.get()
        
        return options
    
    def get_axis_ranges(self) -> Dict[str, Tuple]:
        """
        Get current axis range settings.
        
        Returns:
            Dictionary containing axis range tuples (min, max, is_auto)
        """
        ranges = {}
        
        # X-axis range
        x_auto = self.x_auto_var.get()
        if x_auto:
            ranges['x_axis'] = (None, None, True)
        else:
            try:
                x_min = float(self.x_min_var.get()) if self.x_min_var.get() != "auto" else None
                x_max = float(self.x_max_var.get()) if self.x_max_var.get() != "auto" else None
                ranges['x_axis'] = (x_min, x_max, False)
            except ValueError:
                ranges['x_axis'] = (None, None, True)
        
        # Y-axis range  
        y_auto = self.y_auto_var.get()
        if y_auto:
            ranges['y_axis'] = (None, None, True)
        else:
            try:
                y_min = float(self.y_min_var.get()) if self.y_min_var.get() != "auto" else None
                y_max = float(self.y_max_var.get()) if self.y_max_var.get() != "auto" else None
                ranges['y_axis'] = (y_min, y_max, False)
            except ValueError:
                ranges['y_axis'] = (None, None, True)
        
        return ranges
    
    def get_diagnostic_settings(self) -> Dict[str, Any]:
        """
        Get current diagnostic settings for the GUI update method.
        
        Returns:
            Dictionary containing diagnostic type and response name
        """
        return {
            'diagnostic_type': self.diagnostic_type_var.get(),
            'response_name': self.response_var.get()
        }
    
    def update_available_options(self, new_params: List[str], new_responses: List[str]) -> None:
        """
        Update available parameter and response options.
        
        Args:
            new_params: List of new parameter names
            new_responses: List of new response names
        """
        self.available_parameters = new_params
        self.available_responses = new_responses
        
        # Update combobox values
        if hasattr(self, 'response_combo'):
            self.response_combo['values'] = new_responses
            if new_responses and self.response_var.get() not in new_responses:
                self.response_var.set(new_responses[0])
        
        # Update data availability message
        if hasattr(self, 'data_info_frame'):
            # Clear existing messages
            for widget in self.data_info_frame.winfo_children():
                widget.destroy()
            
            if not new_responses:
                tk.Label(
                    self.data_info_frame,
                    text="⚠ No optimization data loaded. Import data to enable model diagnostics.",
                    bg=COLOR_SURFACE,
                    fg=COLOR_WARNING,
                    font=("Arial", 8, "italic"),
                    wraplength=400
                ).pack(anchor=tk.W)
            else:
                tk.Label(
                    self.data_info_frame,
                    text=f"✓ Data available: {len(new_responses)} responses, {len(new_params)} parameters",
                    bg=COLOR_SURFACE,
                    fg=COLOR_SUCCESS,
                    font=("Arial", 8, "italic")
                ).pack(anchor=tk.W)
        
        logger.info(f"Updated available options - Parameters: {len(new_params)}, Responses: {len(new_responses)}")
    
    def show(self) -> None:
        """Show the control panel window."""
        if self.popup_window is None:
            self._create_popup_window()
        
        self.popup_window.deiconify()
        self.popup_window.lift()
        self.popup_window.focus_force()
        
        # Center the window
        self.popup_window.update_idletasks()
        x = (self.popup_window.winfo_screenwidth() // 2) - (self.popup_window.winfo_width() // 2)
        y = (self.popup_window.winfo_screenheight() // 2) - (self.popup_window.winfo_height() // 2)
        self.popup_window.geometry(f"+{x}+{y}")
        
        logger.info("Model Diagnostics control panel shown")
    
    def hide(self) -> None:
        """Hide the control panel window."""
        if self.popup_window:
            self.popup_window.withdraw()
        logger.info("Model Diagnostics control panel hidden")
    
    def is_visible(self) -> bool:
        """
        Check if the control panel window is currently visible.
        
        Returns:
            True if window is visible, False otherwise
        """
        if self.popup_window is None:
            return False
        
        try:
            return self.popup_window.winfo_viewable()
        except tk.TclError:
            return False
    
    def set_export_callback(self, callback: Callable) -> None:
        """
        Set callback function for plot export.
        
        Args:
            callback: Function to call for plot export
        """
        self.export_callback = callback
        logger.info("Export callback set for Model Diagnostics controls")


def create_model_diagnostics_control_panel(parent: tk.Widget, plot_type: str, 
                                          params_config: Dict[str, Any] = None, 
                                          responses_config: Dict[str, Any] = None, 
                                          update_callback: Callable = None) -> ModelDiagnosticsControlPanel:
    """
    Factory function to create a Model Diagnostics control panel.
    
    Args:
        parent: Parent Tkinter widget
        plot_type: Type identifier for the plot
        params_config: Parameter configuration dictionary
        responses_config: Response configuration dictionary  
        update_callback: Callback function for plot updates
        
    Returns:
        Configured ModelDiagnosticsControlPanel instance
    """
    logger.info(f"Creating Model Diagnostics control panel for plot type: {plot_type}")
    return ModelDiagnosticsControlPanel(parent, plot_type, params_config, responses_config, update_callback)