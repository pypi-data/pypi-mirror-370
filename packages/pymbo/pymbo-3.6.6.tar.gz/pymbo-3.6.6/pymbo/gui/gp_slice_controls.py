"""
Enhanced GP Slice Plot Control Module

This module provides an advanced graphical user interface for controlling GP Slice plot
visualizations within the PyMBO optimization framework. It implements dynamic parameter
and response selection, data series visibility controls, and seamless integration with 
the existing GUI architecture as a popout window.

Key Features:
- Dynamic parameter selection for X-axis and response selection for Y-axis
- Granular control over data series visibility (GP mean, confidence intervals, data points)
- Real-time plot updates with manual refresh functionality
- Scrollable popout window for better accessibility
- Consistent design language adherence
- DPI export functionality
- Axis range controls with auto/manual settings

Classes:
    GPSliceControlPanel: Main control panel class for GP Slice plot management
    
Functions:
    create_gp_slice_control_panel: Factory function for control panel instantiation

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


class GPSliceControlPanel:
    """
    Advanced control panel for GP Slice plot visualization management in a separate popout window.
    
    This class provides comprehensive control over GP Slice plot rendering, including
    dynamic parameter and response selection, data series visibility management, and 
    real-time plot updates. It operates as a separate window for better accessibility 
    and flexibility.
    
    Attributes:
        parent: Parent Tkinter widget
        plot_type: Type identifier for the plot ("gp_slice")
        params_config: Configuration dictionary for optimization parameters
        responses_config: Configuration dictionary for response variables
        update_callback: Callback function for plot updates
        popup_window: Separate Toplevel window for the control panel
        main_frame: Primary container frame for the control panel
        scroll_canvas: Canvas widget for scrollable content
        scroll_frame: Scrollable frame container
        x_param_var: StringVar for X-axis parameter selection
        y_response_var: StringVar for Y-axis response selection
        series_visibility: Dictionary of BooleanVar objects for series visibility
        available_parameters: List of available parameters for X-axis selection
        available_responses: List of available responses for Y-axis selection
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
        Initialize the GP Slice plot control panel in a separate popout window.
        
        Args:
            parent: Parent Tkinter widget for the control panel
            plot_type: Type identifier, should be "gp_slice"
            params_config: Dictionary containing parameter configurations
            responses_config: Dictionary containing response configurations
            update_callback: Function to call when plot updates are needed
        """
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        
        # Create separate popup window
        self.popup_window = None
        
        # GUI components
        self.main_frame = None
        self.scroll_canvas = None
        self.scroll_frame = None
        self.scrollbar = None
        
        # Control variables for dynamic axis binding
        self.x_param_var = tk.StringVar()
        self.y_response_var = tk.StringVar()
        
        # Control variables for data series visibility
        self.series_visibility = {
            'show_mean_line': tk.BooleanVar(value=True),
            'show_68_ci': tk.BooleanVar(value=True),
            'show_95_ci': tk.BooleanVar(value=True),
            'show_data_points': tk.BooleanVar(value=True),
            'show_acquisition': tk.BooleanVar(value=False),
            'show_suggested_points': tk.BooleanVar(value=False),
            'show_legend': tk.BooleanVar(value=True),
            'show_grid': tk.BooleanVar(value=True),
            'show_diagnostics': tk.BooleanVar(value=False)
        }
        
        # Export DPI control
        self.dpi_var = tk.IntVar(value=300)
        
        # Axis range controls
        self.x_min_var = tk.StringVar(value="")
        self.x_max_var = tk.StringVar(value="")
        self.x_auto_var = tk.BooleanVar(value=True)
        self.y_min_var = tk.StringVar(value="")
        self.y_max_var = tk.StringVar(value="")
        self.y_auto_var = tk.BooleanVar(value=True)
        
        # Data attributes for axis selection
        self.available_parameters = []
        self.available_responses = []
        
        # Initialize the control panel
        self._initialize_available_options()
        self._create_popup_window()
        self._setup_event_bindings()
        
        logger.info(f"Enhanced GP Slice plot control panel initialized for {plot_type}")
    
    def _initialize_available_options(self) -> None:
        """
        Initialize the lists of available parameters and responses for axis selection.
        
        This method extracts parameter and response names from their configurations
        to populate the axis selection comboboxes dynamically.
        """
        # Extract parameter names
        self.available_parameters = list(self.params_config.keys())
        
        # Extract response names
        self.available_responses = list(self.responses_config.keys())
        
        # Set default selections
        if self.available_parameters:
            self.x_param_var.set(self.available_parameters[0])
        if self.available_responses:
            self.y_response_var.set(self.available_responses[0])
        
        logger.debug(f"Initialized {len(self.available_parameters)} parameters and {len(self.available_responses)} responses for axis selection")
    
    def _create_popup_window(self) -> None:
        """
        Create the popup window for the control panel.
        
        This method creates a separate Toplevel window that houses the control panel,
        providing better accessibility and flexibility for users.
        """
        # Create the popup window
        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.title("GP Slice Plot Controls")
        self.popup_window.geometry("440x700")
        self.popup_window.resizable(True, True)
        
        # Set minimum size for responsive design
        self.popup_window.minsize(400, 600)
        
        # Configure window behavior
        self.popup_window.transient(self.parent)  # Make it stay on top of parent
        self.popup_window.protocol("WM_DELETE_WINDOW", self.hide)  # Handle close button
        
        # Initially hide the window
        self.popup_window.withdraw()
        
        # Create the control panel content
        self._create_control_panel()
    
    def _create_control_panel(self) -> None:
        """
        Create the main control panel with responsive and flexible layout.
        
        This method constructs the complete GUI hierarchy including the main frame,
        scrollable canvas, and all control widgets. It implements responsive design
        with proper scaling and viewport overflow management.
        """
        # Main container frame with material design styling
        self.main_frame = tk.Frame(
            self.popup_window, 
            bg=COLOR_SURFACE,
            relief="raised",
            bd=1
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title header with consistent design language
        self._create_title_header()
        
        # Scrollable content area
        self._create_scrollable_content()
        
        # Dynamic axis binding controls
        self._create_axis_controls()
        
        # Data series visibility controls
        self._create_visibility_controls()
        
        # Axis range controls
        self._create_axis_range_controls()
        
        # Export controls
        self._create_export_controls()
        
        # Action buttons
        self._create_action_buttons()
        
        # Configure scrollable area
        self._configure_scrolling()
    
    def _create_title_header(self):
        """Create the title header with consistent typography and styling."""
        header_frame = tk.Frame(self.main_frame, bg=COLOR_PRIMARY, height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="GP Slice Plot Controls",
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
    
    def _create_axis_controls(self) -> None:
        """
        Create dynamic axis binding controls with comboboxes.
        
        This method implements the core requirement for dynamic axis selection,
        providing comboboxes populated with available parameters and responses
        and event listeners for plot updates.
        """
        # Axis controls section
        axis_section = tk.LabelFrame(
            self.scroll_frame,
            text="Axis Configuration",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        axis_section.pack(fill=tk.X, padx=5, pady=5)
        
        # X-axis parameter selection
        x_axis_frame = tk.Frame(axis_section, bg=COLOR_SURFACE)
        x_axis_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            x_axis_frame,
            text="X-Axis (Parameter):",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.x_param_combo = ttk.Combobox(
            x_axis_frame,
            textvariable=self.x_param_var,
            values=self.available_parameters,
            state="readonly",
            width=20
        )
        self.x_param_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Y-axis response selection
        y_axis_frame = tk.Frame(axis_section, bg=COLOR_SURFACE)
        y_axis_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            y_axis_frame,
            text="Y-Axis (Response):",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.y_response_combo = ttk.Combobox(
            y_axis_frame,
            textvariable=self.y_response_var,
            values=self.available_responses,
            state="readonly",
            width=20
        )
        self.y_response_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_visibility_controls(self) -> None:
        """
        Create data series visibility controls with granular checkbox widgets.
        
        This method implements the requirement for independent modulation of
        render states for different GP slice data series components including
        GP mean prediction, confidence intervals, observed data points, and
        acquisition function.
        """
        # Visibility controls section
        visibility_section = tk.LabelFrame(
            self.scroll_frame,
            text="Data Series Visibility",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        visibility_section.pack(fill=tk.X, padx=5, pady=5)
        
        # GP mean prediction checkbox
        mean_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        mean_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            mean_frame,
            text="GP Mean Prediction",
            variable=self.series_visibility['show_mean_line'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            mean_frame,
            text="(Mean prediction curve)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # 95% Confidence interval checkbox
        ci_95_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        ci_95_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            ci_95_frame,
            text="95% Confidence Band",
            variable=self.series_visibility['show_95_ci'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            ci_95_frame,
            text="(95% uncertainty bounds)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # 68% Confidence interval checkbox
        ci_68_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        ci_68_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            ci_68_frame,
            text="68% Confidence Band",
            variable=self.series_visibility['show_68_ci'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            ci_68_frame,
            text="(68% uncertainty bounds)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Observed data points checkbox
        data_points_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        data_points_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            data_points_frame,
            text="Observed Data Points",
            variable=self.series_visibility['show_data_points'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            data_points_frame,
            text="(Training data points)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Acquisition function checkbox
        acquisition_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        acquisition_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            acquisition_frame,
            text="Acquisition Function",
            variable=self.series_visibility['show_acquisition'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            acquisition_frame,
            text="(Next point selection)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Suggested points checkbox
        suggested_points_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        suggested_points_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            suggested_points_frame,
            text="Show Suggested Points",
            variable=self.series_visibility['show_suggested_points'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            suggested_points_frame,
            text="(With dotted lines to axes)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Legend visibility checkbox
        legend_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        legend_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            legend_frame,
            text="Show Legend",
            variable=self.series_visibility['show_legend'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        # Grid visibility checkbox
        grid_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        grid_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            grid_frame,
            text="Show Grid",
            variable=self.series_visibility['show_grid'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        # Diagnostics visibility checkbox
        diagnostics_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        diagnostics_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            diagnostics_frame,
            text="Show Diagnostics",
            variable=self.series_visibility['show_diagnostics'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            diagnostics_frame,
            text="(Model quality metrics)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_axis_range_controls(self) -> None:
        """
        Create axis range controls for manual range setting or auto-scaling.
        """
        # Axis range controls section
        range_section = tk.LabelFrame(
            self.scroll_frame,
            text="Axis Range Settings",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        range_section.pack(fill=tk.X, padx=5, pady=5)
        
        # X-axis range controls
        x_range_frame = tk.Frame(range_section, bg=COLOR_SURFACE)
        x_range_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            x_range_frame,
            text="X-Axis Auto",
            variable=self.x_auto_var,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE,
            command=self._toggle_x_range_controls
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            x_range_frame,
            text="Min:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.x_min_entry = tk.Entry(
            x_range_frame,
            textvariable=self.x_min_var,
            width=8,
            font=("Arial", 9)
        )
        self.x_min_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            x_range_frame,
            text="Max:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.x_max_entry = tk.Entry(
            x_range_frame,
            textvariable=self.x_max_var,
            width=8,
            font=("Arial", 9)
        )
        self.x_max_entry.pack(side=tk.LEFT)
        
        # Y-axis range controls
        y_range_frame = tk.Frame(range_section, bg=COLOR_SURFACE)
        y_range_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            y_range_frame,
            text="Y-Axis Auto",
            variable=self.y_auto_var,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE,
            command=self._toggle_y_range_controls
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            y_range_frame,
            text="Min:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.y_min_entry = tk.Entry(
            y_range_frame,
            textvariable=self.y_min_var,
            width=8,
            font=("Arial", 9)
        )
        self.y_min_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            y_range_frame,
            text="Max:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.y_max_entry = tk.Entry(
            y_range_frame,
            textvariable=self.y_max_var,
            width=8,
            font=("Arial", 9)
        )
        self.y_max_entry.pack(side=tk.LEFT)
        
        # Initialize range control states
        self._toggle_x_range_controls()
        self._toggle_y_range_controls()
    
    def _toggle_x_range_controls(self):
        """Toggle X-axis range entry widgets based on auto checkbox."""
        if self.x_auto_var.get():
            self.x_min_entry.config(state="disabled", bg=COLOR_BACKGROUND)
            self.x_max_entry.config(state="disabled", bg=COLOR_BACKGROUND)
        else:
            self.x_min_entry.config(state="normal", bg=COLOR_SURFACE)
            self.x_max_entry.config(state="normal", bg=COLOR_SURFACE)
    
    def _toggle_y_range_controls(self):
        """Toggle Y-axis range entry widgets based on auto checkbox."""
        if self.y_auto_var.get():
            self.y_min_entry.config(state="disabled", bg=COLOR_BACKGROUND)
            self.y_max_entry.config(state="disabled", bg=COLOR_BACKGROUND)
        else:
            self.y_min_entry.config(state="normal", bg=COLOR_SURFACE)
            self.y_max_entry.config(state="normal", bg=COLOR_SURFACE)
    
    def _create_export_controls(self) -> None:
        """
        Create export controls for DPI selection and graph export functionality.
        """
        # Export controls section
        export_section = tk.LabelFrame(
            self.scroll_frame,
            text="Export Settings",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        export_section.pack(fill=tk.X, padx=5, pady=5)
        
        # DPI selection
        dpi_frame = tk.Frame(export_section, bg=COLOR_SURFACE)
        dpi_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            dpi_frame,
            text="Export DPI:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        dpi_values = [150, 300, 600, 1200]
        self.dpi_combo = ttk.Combobox(
            dpi_frame,
            textvariable=self.dpi_var,
            values=dpi_values,
            state="readonly",
            width=10
        )
        self.dpi_combo.pack(side=tk.LEFT)
        
        # Export button
        export_btn = tk.Button(
            export_section,
            text="Export Plot",
            command=self._export_plot,
            bg=COLOR_PRIMARY,
            fg=COLOR_SURFACE,
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=20,
            pady=5
        )
        export_btn.pack(pady=(10, 0))

    def _create_action_buttons(self) -> None:
        """
        Create action buttons for plot control operations.
        """
        # Action buttons section
        button_frame = tk.Frame(self.scroll_frame, bg=COLOR_SURFACE)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Refresh plot button - main button for triggering updates
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh Plot",
            command=self._refresh_plot,
            bg=COLOR_SUCCESS,
            fg=COLOR_SURFACE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=25,
            pady=8
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset to defaults button
        reset_btn = tk.Button(
            button_frame,
            text="↺ Reset Defaults",
            command=self._reset_to_defaults,
            bg=COLOR_WARNING,
            fg=COLOR_SURFACE,
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=20,
            pady=8
        )
        reset_btn.pack(side=tk.RIGHT, padx=5)

    def _configure_scrolling(self):
        """Configure the scrollable area with proper event bindings."""
        def _on_frame_configure(event):
            """Update scroll region when frame size changes."""
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        
        def _on_canvas_configure(event):
            """Update frame width when canvas size changes."""
            canvas_width = event.width
            self.scroll_canvas.itemconfig(self.canvas_frame_id, width=canvas_width)
        
        # Bind configuration events
        self.scroll_frame.bind('<Configure>', _on_frame_configure)
        self.scroll_canvas.bind('<Configure>', _on_canvas_configure)
        
        # Bind mouse wheel events for scrolling
        def _on_mousewheel(event):
            """Handle mouse wheel scrolling."""
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind mouse wheel to canvas and all child widgets
        self._bind_mousewheel_recursive(self.scroll_canvas, _on_mousewheel)
        self._bind_mousewheel_recursive(self.scroll_frame, _on_mousewheel)
    
    def _bind_mousewheel_recursive(self, widget: tk.Widget, callback: Callable) -> None:
        """
        Recursively bind mouse wheel events to a widget and all its children.
        
        Args:
            widget: The widget to bind events to
            callback: The callback function for mouse wheel events
        """
        widget.bind("<MouseWheel>", callback)
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child, callback)
    
    def _setup_event_bindings(self) -> None:
        """
        Setup event listeners - but don't auto-update, wait for refresh button.
        
        This method sets up the control panel but doesn't automatically trigger
        plot updates. Users must click the Refresh Plot button to apply changes.
        """
        # Note: We removed automatic updates to match Progress benchmark requirement
        # Users must click "Refresh Plot" to update the plot
        
        # However, we do want to automatically update the fixed value when parameters change
        # to avoid logical inconsistencies (bug fix)
        self.x_param_var.trace('w', self._on_parameter_change)
        
        # Store the previous parameter to detect changes
        self._previous_x_param = self.x_param_var.get()
    
    def _on_parameter_change(self, *args) -> None:
        """
        Handle parameter change events for the X-axis parameter selection.
        
        This method is called when the X parameter selection changes and logs
        the change for debugging purposes. The actual parameter switching logic
        is handled in the main GUI refresh callback.
        
        Args:
            *args: Variable arguments from the trace callback (not used)
        """
        try:
            current_param = self.x_param_var.get()
            previous_param = getattr(self, '_previous_x_param', '')
            
            if current_param != previous_param:
                logger.debug(f"GP Slice control panel: X parameter changed from '{previous_param}' to '{current_param}'")
                # Update the stored previous parameter
                self._previous_x_param = current_param
                
                # Note: The actual parameter switching logic (updating fixed value, etc.)
                # is handled in the main GUI's _refresh_gp_slice_plot method when the
                # user clicks the Refresh Plot button.
                
        except Exception as e:
            logger.warning(f"Error in parameter change callback: {e}")
    
    def _refresh_plot(self) -> None:
        """
        Handle the Refresh Plot button click to update the plot with current settings.
        
        This method is called when the user clicks the "Refresh Plot" button and
        triggers the plot update with all current control panel settings.
        """
        logger.info("Refreshing GP Slice plot with current settings")
        self._trigger_plot_update()
    
    def _trigger_plot_update(self) -> None:
        """
        Trigger immediate plot update using the registered callback.
        
        This method calls the update callback function if available, allowing
        the plot to be refreshed with the current control panel settings.
        """
        if self.update_callback:
            try:
                logger.info("Triggering GP Slice plot update")
                self.update_callback()
            except Exception as e:
                logger.error(f"Error calling plot update callback: {e}")
        else:
            logger.warning("No update callback registered for GP Slice plot")
    
    def _export_plot(self) -> None:
        """
        Export the current plot with specified DPI settings.
        
        This method opens a file dialog and exports the current plot
        with the DPI setting selected by the user.
        """
        from tkinter import filedialog
        
        # Get the export DPI
        dpi = self.dpi_var.get()
        
        # Open file dialog for save location
        filename = filedialog.asksaveasfilename(
            title="Export GP Slice Plot",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                # Call the export callback if available
                if hasattr(self, 'export_callback') and self.export_callback:
                    self.export_callback(filename, dpi)
                    logger.info(f"Plot exported to {filename} at {dpi} DPI")
                else:
                    logger.warning("No export callback registered")
            except Exception as e:
                logger.error(f"Error exporting plot: {e}")
                messagebox.showerror("Export Error", f"Failed to export plot: {e}")
    
    def _reset_to_defaults(self) -> None:
        """
        Reset all controls to their default values.
        
        This method restores the control panel to its initial state, including
        default parameter and response selections and visibility settings.
        """
        # Reset axis selections to defaults
        if self.available_parameters:
            self.x_param_var.set(self.available_parameters[0])
        if self.available_responses:
            self.y_response_var.set(self.available_responses[0])
        
        # Reset visibility controls to defaults
        self.series_visibility['show_mean_line'].set(True)
        self.series_visibility['show_68_ci'].set(True)
        self.series_visibility['show_95_ci'].set(True)
        self.series_visibility['show_data_points'].set(True)
        self.series_visibility['show_acquisition'].set(False)
        self.series_visibility['show_suggested_points'].set(False)
        self.series_visibility['show_legend'].set(True)
        self.series_visibility['show_grid'].set(True)
        self.series_visibility['show_diagnostics'].set(False)
        
        # Reset DPI to default
        self.dpi_var.set(300)
        
        # Reset axis ranges to auto
        self.x_auto_var.set(True)
        self.y_auto_var.set(True)
        self.x_min_var.set("")
        self.x_max_var.set("")
        self.y_min_var.set("")
        self.y_max_var.set("")
        
        # Update control states
        if hasattr(self, '_toggle_x_range_controls'):
            self._toggle_x_range_controls()
        if hasattr(self, '_toggle_y_range_controls'):
            self._toggle_y_range_controls()
        
        logger.info("GP Slice plot controls reset to defaults")
        # Don't auto-refresh, user must click refresh button
    
    def get_display_options(self) -> Dict[str, Any]:
        """
        Get current display options for integration with the plotting system.
        
        This method returns a dictionary containing all current control settings
        in a format expected by the PyMBO plotting system. It serves as the
        primary interface between the control panel and the plot generation logic.
        
        Returns:
            Dict[str, Any]: Dictionary containing current display options including:
                - x_param: Currently selected X-axis parameter
                - y_response: Currently selected Y-axis response
                - show_gp_mean: Whether to show GP mean prediction
                - show_confidence: Whether to show confidence intervals
                - show_data_points: Whether to show observed data points
                - show_acquisition: Whether to show acquisition function
                - show_legend: Whether to display the plot legend
                - export_dpi: DPI setting for plot export
        """
        options = {
            'x_param': self.x_param_var.get(),
            'y_response': self.y_response_var.get(),
            'show_mean_line': self.series_visibility['show_mean_line'].get(),
            'show_68_ci': self.series_visibility['show_68_ci'].get(),
            'show_95_ci': self.series_visibility['show_95_ci'].get(),
            'show_data_points': self.series_visibility['show_data_points'].get(),
            'show_acquisition': self.series_visibility['show_acquisition'].get(),
            'show_suggested_points': self.series_visibility['show_suggested_points'].get(),
            'show_legend': self.series_visibility['show_legend'].get(),
            'show_grid': self.series_visibility['show_grid'].get(),
            'show_diagnostics': self.series_visibility['show_diagnostics'].get(),
            'export_dpi': self.dpi_var.get()
        }
        
        logger.debug(f"Current display options: {options}")
        return options
    
    def get_axis_ranges(self) -> Dict[str, Tuple]:
        """
        Get current axis range settings for integration with the plotting system.
        
        Returns:
            Dict[str, Tuple]: Dictionary containing axis ranges where each value is a tuple of
                (min_value, max_value, is_auto) for x_axis and y_axis
        """
        def _parse_range_value(value_str: str):
            """Parse range value string to float or None."""
            if not value_str or not value_str.strip():
                return None
            try:
                return float(value_str.strip())
            except ValueError:
                return None
        
        x_min = _parse_range_value(self.x_min_var.get()) if not self.x_auto_var.get() else None
        x_max = _parse_range_value(self.x_max_var.get()) if not self.x_auto_var.get() else None
        y_min = _parse_range_value(self.y_min_var.get()) if not self.y_auto_var.get() else None
        y_max = _parse_range_value(self.y_max_var.get()) if not self.y_auto_var.get() else None
        
        ranges = {
            "x_axis": (x_min, x_max, self.x_auto_var.get()),
            "y_axis": (y_min, y_max, self.y_auto_var.get())
        }
        
        logger.debug(f"Current axis ranges: {ranges}")
        return ranges
    
    def update_available_options(self, new_params: List[str], new_responses: List[str]) -> None:
        """
        Update the available parameters and responses for axis selection.
        
        This method allows dynamic updating of the parameter and response lists when
        the optimization configuration changes.
        
        Args:
            new_params: List of new parameter names to make available
            new_responses: List of new response names to make available
        """
        self.available_parameters = new_params
        self.available_responses = new_responses
        
        # Update combobox values
        if hasattr(self, 'x_param_combo'):
            self.x_param_combo['values'] = new_params
        if hasattr(self, 'y_response_combo'):
            self.y_response_combo['values'] = new_responses
        
        # Update selections if current ones are no longer valid
        if self.x_param_var.get() not in new_params and new_params:
            self.x_param_var.set(new_params[0])
        if self.y_response_var.get() not in new_responses and new_responses:
            self.y_response_var.set(new_responses[0])
        
        logger.info(f"Updated available options: {len(new_params)} parameters, {len(new_responses)} responses")
    
    def show(self) -> None:
        """Show the popout control panel window."""
        if self.popup_window:
            self.popup_window.deiconify()  # Show the window
            self.popup_window.lift()  # Bring to front
            self.popup_window.focus_set()  # Give focus
        logger.info("GP Slice plot control panel window shown")
    
    def hide(self) -> None:
        """Hide the popout control panel window."""
        if self.popup_window:
            self.popup_window.withdraw()  # Hide the window
        logger.info("GP Slice plot control panel window hidden")
    
    def is_visible(self) -> bool:
        """Check if the control panel window is currently visible."""
        if self.popup_window is None:
            return False
        try:
            return self.popup_window.state() != 'withdrawn'
        except tk.TclError:
            return False
    
    def set_export_callback(self, callback: Callable) -> None:
        """
        Set the callback function for plot export functionality.
        
        Args:
            callback: Function to call for plot export, should accept (filename, dpi) parameters
        """
        self.export_callback = callback
        logger.debug("Export callback registered")


def create_gp_slice_control_panel(parent: tk.Widget, plot_type: str,
                                 params_config: Dict[str, Any] = None,
                                 responses_config: Dict[str, Any] = None,
                                 update_callback: Callable = None,
                                 export_callback: Callable = None) -> GPSliceControlPanel:
    """
    Factory function for creating enhanced GP Slice plot control panels in popout windows.
    
    This function serves as the primary entry point for instantiating GP Slice plot
    control panels. It creates a separate popup window with comprehensive controls
    for GP Slice plot customization.
    
    Args:
        parent: Parent Tkinter widget for the control panel
        plot_type: Type identifier for the plot (should be "gp_slice")
        params_config: Dictionary containing parameter configurations
        responses_config: Dictionary containing response configurations
        update_callback: Function to call when plot updates are needed
        export_callback: Function to call for plot export (filename, dpi) -> None
    
    Returns:
        GPSliceControlPanel: Initialized control panel instance in popup window
    
    Raises:
        Exception: If control panel creation fails
    
    Example:
        >>> control_panel = create_gp_slice_control_panel(
        ...     parent=main_window,
        ...     plot_type="gp_slice",
        ...     params_config=param_dict,
        ...     responses_config=response_dict,
        ...     update_callback=update_plot_function,
        ...     export_callback=export_plot_function
        ... )
    """
    try:
        logger.info(f"Creating enhanced GP Slice control panel for plot type: {plot_type}")
        
        control_panel = GPSliceControlPanel(
            parent=parent,
            plot_type=plot_type,
            params_config=params_config,
            responses_config=responses_config,
            update_callback=update_callback
        )
        
        # Set export callback if provided
        if export_callback:
            control_panel.set_export_callback(export_callback)
        
        logger.info("Enhanced GP Slice control panel created successfully in popup window")
        return control_panel
        
    except Exception as e:
        logger.error(f"Failed to create GP Slice control panel: {e}")
        raise