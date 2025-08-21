"""
Enhanced Progress Plot Control Module

This module provides an advanced graphical user interface for controlling Progress plot
visualizations within the PyMBO optimization framework. It implements dynamic metric
selection, data series visibility controls, and seamless integration with the existing
GUI architecture as a popout window.

Key Features:
- Dynamic metric selection for X/Y axes (iterations, hypervolume, time, etc.)
- Granular control over data series visibility (raw HV, normalized HV, trends, what-if)
- Real-time plot updates with manual refresh functionality
- Scrollable popout window for better accessibility
- Consistent design language adherence
- DPI export functionality

Classes:
    ProgressPlotControlPanel: Main control panel class for Progress plot management
    
Functions:
    create_progress_control_panel: Factory function for control panel instantiation

Author: PyMBO Development Team
Version: 3.6.6 Enhanced (Popout Window)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any, Callable, List, Optional, Tuple
import threading

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


class ProgressPlotControlPanel:
    """
    Advanced control panel for Progress plot visualization management in a separate popout window.
    
    This class provides comprehensive control over Progress plot rendering, including
    dynamic metric selection, data series visibility management, and real-time plot
    updates. It operates as a separate window for better accessibility and flexibility.
    
    Attributes:
        parent: Parent Tkinter widget
        plot_type: Type identifier for the plot ("progress")
        params_config: Configuration dictionary for optimization parameters
        responses_config: Configuration dictionary for response variables
        update_callback: Callback function for plot updates
        popup_window: Separate Toplevel window for the control panel
        main_frame: Primary container frame for the control panel
        scroll_canvas: Canvas widget for scrollable content
        scroll_frame: Scrollable frame container
        x_axis_var: StringVar for X-axis selection
        y_axis_var: StringVar for Y-axis selection
        series_visibility: Dictionary of BooleanVar objects for series visibility
        available_metrics: List of available progress metrics for axis selection
        dpi_var: IntVar for export DPI selection
    """
    def __init__(self, parent: tk.Widget, plot_type: str, 
                 params_config: Dict[str, Any] = None,
                 responses_config: Dict[str, Any] = None,
                 update_callback: Callable = None):
        """
        Initialize the Progress plot control panel in a separate popout window.
        
        Args:
            parent: Parent Tkinter widget for the control panel
            plot_type: Type identifier, should be "progress"
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
        
        # Control variables for dynamic metric binding
        self.x_axis_var = tk.StringVar()
        self.y_axis_var = tk.StringVar()
        self.y2_axis_var = tk.StringVar()
        
        # Control variables for data series visibility
        self.series_visibility = {
            'show_raw_hv': tk.BooleanVar(value=True),
            'show_normalized_hv': tk.BooleanVar(value=True),
            'show_trend': tk.BooleanVar(value=True),
            'show_whatif_trend': tk.BooleanVar(value=False),
            'show_convergence_analysis': tk.BooleanVar(value=False),
            'show_legend': tk.BooleanVar(value=True)
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
        self.y2_min_var = tk.StringVar(value="")
        self.y2_max_var = tk.StringVar(value="")
        self.y2_auto_var = tk.BooleanVar(value=True)
        
        # Data attributes for metric selection
        self.available_metrics = []
        
        # Initialize the control panel
        self._initialize_progress_metrics()
        self._create_popup_window()
        self._setup_event_bindings()
        
        logger.info(f"Enhanced Progress plot control panel initialized for {plot_type}")
    
    def _initialize_progress_metrics(self) -> None:
        """
        Initialize the list of available progress metrics for axis selection.
        
        This method sets up the metrics available for progress plotting including
        iterations, hypervolume indicators, time metrics, and experiment counts.
        """
        self.available_metrics = [
            "iteration",
            "hypervolume", 
            "normalized_hypervolume",
            "execution_time",
            "n_experiments",
            "convergence_rate",
            "improvement_rate"
        ]
        
        # Set default selections
        self.x_axis_var.set("iteration")
        self.y_axis_var.set("hypervolume")
        self.y2_axis_var.set("normalized_hypervolume")
        
        logger.debug(f"Initialized {len(self.available_metrics)} progress metrics for axis selection")
    
    def _create_popup_window(self) -> None:
        """
        Create the popup window for the control panel.
        
        This method creates a separate Toplevel window that houses the control panel,
        providing better accessibility and flexibility for users.
        """
        # Create the popup window
        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.title("Progress Plot Controls")
        self.popup_window.geometry("420x650")
        self.popup_window.resizable(True, True)
        
        # Set minimum size for responsive design
        self.popup_window.minsize(380, 550)
        
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
        
        # Dynamic metric selection controls
        self._create_metric_controls()
        
        # Data series visibility controls
        self._create_visibility_controls()
        
        # Export controls
        self._create_export_controls()
        
        # Axis range controls
        self._create_axis_range_controls()
        
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
            text="Progress Plot Controls",
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
    
    def _create_metric_controls(self) -> None:
        """
        Create dynamic metric selection controls with comboboxes.
        
        This method implements the core requirement for dynamic metric selection,
        providing comboboxes populated with available progress metrics and
        event listeners for plot updates.
        """
        # Metric controls section
        metric_section = tk.LabelFrame(
            self.scroll_frame,
            text="Metric Configuration",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        metric_section.pack(fill=tk.X, padx=5, pady=5)
        
        # X-axis selection
        x_axis_frame = tk.Frame(metric_section, bg=COLOR_SURFACE)
        x_axis_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            x_axis_frame,
            text="X-Axis (Abscissa):",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.x_axis_combo = ttk.Combobox(
            x_axis_frame,
            textvariable=self.x_axis_var,
            values=self.available_metrics,
            state="readonly",
            width=20
        )
        self.x_axis_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Y-axis selection
        y_axis_frame = tk.Frame(metric_section, bg=COLOR_SURFACE)
        y_axis_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            y_axis_frame,
            text="Y-Axis (Ordinate):",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.y_axis_combo = ttk.Combobox(
            y_axis_frame,
            textvariable=self.y_axis_var,
            values=self.available_metrics,
            state="readonly",
            width=20
        )
        self.y_axis_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Y2-axis selection (second Y-axis)
        y2_axis_frame = tk.Frame(metric_section, bg=COLOR_SURFACE)
        y2_axis_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            y2_axis_frame,
            text="Y2-Axis (Right):",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.y2_axis_combo = ttk.Combobox(
            y2_axis_frame,
            textvariable=self.y2_axis_var,
            values=self.available_metrics,
            state="readonly",
            width=20
        )
        self.y2_axis_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_visibility_controls(self) -> None:
        """
        Create data series visibility controls with granular checkbox widgets.
        
        This method implements the requirement for independent modulation of
        render states for different progress data series components including raw
        hypervolume, normalized hypervolume, trend analysis, and what-if scenarios.
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
        
        # Raw hypervolume checkbox
        raw_hv_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        raw_hv_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            raw_hv_frame,
            text="Raw Hypervolume",
            variable=self.series_visibility['show_raw_hv'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            raw_hv_frame,
            text="(Actual hypervolume values)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Normalized hypervolume checkbox
        norm_hv_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        norm_hv_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            norm_hv_frame,
            text="Normalized Hypervolume",
            variable=self.series_visibility['show_normalized_hv'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            norm_hv_frame,
            text="(0-1 scaled values)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Trend analysis checkbox
        trend_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        trend_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            trend_frame,
            text="Trend Analysis",
            variable=self.series_visibility['show_trend'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            trend_frame,
            text="(Moving averages and trends)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # What-if scenarios checkbox
        whatif_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        whatif_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            whatif_frame,
            text="What-If Scenarios",
            variable=self.series_visibility['show_whatif_trend'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            whatif_frame,
            text="(Predictive projections)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Convergence analysis checkbox
        convergence_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        convergence_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            convergence_frame,
            text="Convergence Analysis",
            variable=self.series_visibility['show_convergence_analysis'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            convergence_frame,
            text="(Convergence indicators)",
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
        
        # Y1-axis range controls
        y_range_frame = tk.Frame(range_section, bg=COLOR_SURFACE)
        y_range_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            y_range_frame,
            text="Y1-Axis Auto",
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
        
        # Y2-axis range controls
        y2_range_frame = tk.Frame(range_section, bg=COLOR_SURFACE)
        y2_range_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            y2_range_frame,
            text="Y2-Axis Auto",
            variable=self.y2_auto_var,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE,
            command=self._toggle_y2_range_controls
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            y2_range_frame,
            text="Min:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.y2_min_entry = tk.Entry(
            y2_range_frame,
            textvariable=self.y2_min_var,
            width=8,
            font=("Arial", 9)
        )
        self.y2_min_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            y2_range_frame,
            text="Max:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.y2_max_entry = tk.Entry(
            y2_range_frame,
            textvariable=self.y2_max_var,
            width=8,
            font=("Arial", 9)
        )
        self.y2_max_entry.pack(side=tk.LEFT)
        
        # Initialize range control states
        self._toggle_x_range_controls()
        self._toggle_y_range_controls()
        self._toggle_y2_range_controls()
    
    def _toggle_x_range_controls(self):
        """Toggle X-axis range entry widgets based on auto checkbox."""
        if self.x_auto_var.get():
            self.x_min_entry.config(state="disabled", bg=COLOR_BACKGROUND)
            self.x_max_entry.config(state="disabled", bg=COLOR_BACKGROUND)
        else:
            self.x_min_entry.config(state="normal", bg=COLOR_SURFACE)
            self.x_max_entry.config(state="normal", bg=COLOR_SURFACE)
    
    def _toggle_y_range_controls(self):
        """Toggle Y1-axis range entry widgets based on auto checkbox."""
        if self.y_auto_var.get():
            self.y_min_entry.config(state="disabled", bg=COLOR_BACKGROUND)
            self.y_max_entry.config(state="disabled", bg=COLOR_BACKGROUND)
        else:
            self.y_min_entry.config(state="normal", bg=COLOR_SURFACE)
            self.y_max_entry.config(state="normal", bg=COLOR_SURFACE)
    
    def _toggle_y2_range_controls(self):
        """Toggle Y2-axis range entry widgets based on auto checkbox."""
        if self.y2_auto_var.get():
            self.y2_min_entry.config(state="disabled", bg=COLOR_BACKGROUND)
            self.y2_max_entry.config(state="disabled", bg=COLOR_BACKGROUND)
        else:
            self.y2_min_entry.config(state="normal", bg=COLOR_SURFACE)
            self.y2_max_entry.config(state="normal", bg=COLOR_SURFACE)
    
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
        # Note: We removed automatic updates to match Pareto benchmark requirement
        # Users must click "Refresh Plot" to update the plot
        pass
    
    def _refresh_plot(self) -> None:
        """
        Handle the Refresh Plot button click to update the plot with current settings.
        
        This method is called when the user clicks the "Refresh Plot" button and
        triggers the plot update with all current control panel settings.
        """
        logger.info("Refreshing Progress plot with current settings")
        self._trigger_plot_update()
    
    def _trigger_plot_update(self) -> None:
        """
        Trigger immediate plot update using the registered callback.
        
        This method calls the update callback function if available, allowing
        the plot to be refreshed with the current control panel settings.
        """
        if self.update_callback:
            try:
                logger.info("Triggering Progress plot update")
                self.update_callback()
            except Exception as e:
                logger.error(f"Error calling plot update callback: {e}")
        else:
            logger.warning("No update callback registered for Progress plot")
    
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
            title="Export Progress Plot",
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
        default metric selections and visibility settings.
        """
        # Reset metric selections to defaults
        self.x_axis_var.set("iteration")
        self.y_axis_var.set("hypervolume")
        
        # Reset visibility controls to defaults
        self.series_visibility['show_raw_hv'].set(True)
        self.series_visibility['show_normalized_hv'].set(True)
        self.series_visibility['show_trend'].set(True)
        self.series_visibility['show_whatif_trend'].set(False)
        self.series_visibility['show_convergence_analysis'].set(False)
        self.series_visibility['show_legend'].set(True)
        
        # Reset DPI to default
        self.dpi_var.set(300)
        
        # Reset axis ranges to auto
        self.x_auto_var.set(True)
        self.y_auto_var.set(True)
        self.y2_auto_var.set(True)
        self.x_min_var.set("")
        self.x_max_var.set("")
        self.y_min_var.set("")
        self.y_max_var.set("")
        self.y2_min_var.set("")
        self.y2_max_var.set("")
        
        # Update control states
        if hasattr(self, '_toggle_x_range_controls'):
            self._toggle_x_range_controls()
        if hasattr(self, '_toggle_y_range_controls'):
            self._toggle_y_range_controls()
        if hasattr(self, '_toggle_y2_range_controls'):
            self._toggle_y2_range_controls()
        
        logger.info("Progress plot controls reset to defaults")
        # Don't auto-refresh, user must click refresh button
    
    
    def get_display_options(self) -> Dict[str, Any]:
        """
        Get current display options for integration with the plotting system.
        
        This method returns a dictionary containing all current control settings
        in a format expected by the PyMBO plotting system. It serves as the
        primary interface between the control panel and the plot generation logic.
        
        Returns:
            Dict[str, Any]: Dictionary containing current display options including:
                - x_metric: Currently selected X-axis metric
                - y_metric: Currently selected Y-axis metric
                - show_raw_hv: Whether to show raw hypervolume
                - show_normalized_hv: Whether to show normalized hypervolume
                - show_trend: Whether to show trend analysis
                - show_whatif_trend: Whether to show what-if scenarios
                - show_convergence_analysis: Whether to show convergence analysis
                - show_legend: Whether to display the plot legend
                - export_dpi: DPI setting for plot export
        """
        options = {
            'x_metric': self.x_axis_var.get(),
            'y_metric': self.y_axis_var.get(),
            'y2_metric': self.y2_axis_var.get(),
            'show_raw_hv': self.series_visibility['show_raw_hv'].get(),
            'show_normalized_hv': self.series_visibility['show_normalized_hv'].get(),
            'show_trend': self.series_visibility['show_trend'].get(),
            'show_whatif_trend': self.series_visibility['show_whatif_trend'].get(),
            'show_convergence_analysis': self.series_visibility['show_convergence_analysis'].get(),
            'show_legend': self.series_visibility['show_legend'].get(),
            'export_dpi': self.dpi_var.get()
        }
        
        logger.debug(f"Current display options: {options}")
        return options
    
    def get_axis_ranges(self) -> Dict[str, Tuple]:
        """
        Get current axis range settings for integration with the plotting system.
        
        Returns:
            Dict[str, Tuple]: Dictionary containing axis ranges where each value is a tuple of
                (min_value, max_value, is_auto) for x_axis, y_axis, and y2_axis
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
        y2_min = _parse_range_value(self.y2_min_var.get()) if not self.y2_auto_var.get() else None
        y2_max = _parse_range_value(self.y2_max_var.get()) if not self.y2_auto_var.get() else None
        
        ranges = {
            "x_axis": (x_min, x_max, self.x_auto_var.get()),
            "y_axis": (y_min, y_max, self.y_auto_var.get()),
            "y2_axis": (y2_min, y2_max, self.y2_auto_var.get())
        }
        
        logger.debug(f"Current axis ranges: {ranges}")
        return ranges
    
    def update_available_metrics(self, new_metrics: List[str]) -> None:
        """
        Update the available metrics for axis selection.
        
        This method allows dynamic updating of the metric lists when new data
        becomes available or when the optimization configuration changes.
        
        Args:
            new_metrics: List of new metric names to make available
        """
        self.available_metrics = new_metrics
        
        # Update combobox values
        if hasattr(self, 'x_axis_combo'):
            self.x_axis_combo['values'] = new_metrics
        if hasattr(self, 'y_axis_combo'):
            self.y_axis_combo['values'] = new_metrics
        if hasattr(self, 'y2_axis_combo'):
            self.y2_axis_combo['values'] = new_metrics
        
        # Update selections if current ones are no longer valid
        if self.x_axis_var.get() not in new_metrics and new_metrics:
            self.x_axis_var.set(new_metrics[0])
        if self.y_axis_var.get() not in new_metrics and len(new_metrics) > 1:
            self.y_axis_var.set(new_metrics[1])
        if self.y2_axis_var.get() not in new_metrics and len(new_metrics) > 2:
            self.y2_axis_var.set(new_metrics[2])
        elif self.y2_axis_var.get() not in new_metrics and len(new_metrics) > 1:
            self.y2_axis_var.set(new_metrics[1])
        
        logger.info(f"Updated available metrics: {len(new_metrics)} metrics")
    
    def show(self) -> None:
        """Show the popout control panel window."""
        if self.popup_window:
            self.popup_window.deiconify()  # Show the window
            self.popup_window.lift()  # Bring to front
            self.popup_window.focus_set()  # Give focus
        logger.info("Progress plot control panel window shown")
    
    def hide(self) -> None:
        """Hide the popout control panel window."""
        if self.popup_window:
            self.popup_window.withdraw()  # Hide the window
        logger.info("Progress plot control panel window hidden")
    
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
    


def create_progress_control_panel(parent: tk.Widget, plot_type: str,
                                 params_config: Dict[str, Any] = None,
                                 responses_config: Dict[str, Any] = None,
                                 update_callback: Callable = None,
                                 export_callback: Callable = None) -> ProgressPlotControlPanel:
    """
    Factory function for creating enhanced Progress plot control panels in popout windows.
    
    This function serves as the primary entry point for instantiating Progress plot
    control panels. It creates a separate popup window with comprehensive controls
    for Progress plot customization.
    
    Args:
        parent: Parent Tkinter widget for the control panel
        plot_type: Type identifier for the plot (should be "progress")
        params_config: Dictionary containing parameter configurations
        responses_config: Dictionary containing response configurations
        update_callback: Function to call when plot updates are needed
        export_callback: Function to call for plot export (filename, dpi) -> None
    
    Returns:
        ProgressPlotControlPanel: Initialized control panel instance in popup window
    
    Raises:
        Exception: If control panel creation fails
    
    Example:
        >>> control_panel = create_progress_control_panel(
        ...     parent=main_window,
        ...     plot_type="progress",
        ...     params_config=param_dict,
        ...     responses_config=response_dict,
        ...     update_callback=update_plot_function,
        ...     export_callback=export_plot_function
        ... )
    """
    try:
        logger.info(f"Creating enhanced Progress control panel for plot type: {plot_type}")
        
        control_panel = ProgressPlotControlPanel(
            parent=parent,
            plot_type=plot_type,
            params_config=params_config,
            responses_config=responses_config,
            update_callback=update_callback
        )
        
        # Set export callback if provided
        if export_callback:
            control_panel.set_export_callback(export_callback)
        
        logger.info("Enhanced Progress control panel created successfully in popup window")
        return control_panel
        
    except Exception as e:
        logger.error(f"Failed to create Progress control panel: {e}")
        raise