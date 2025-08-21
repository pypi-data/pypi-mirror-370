"""
Enhanced Parallel Coordinates Plot Control Module

This module provides an advanced graphical user interface for controlling Parallel 
Coordinates plot visualizations within the PyMBO optimization framework. It implements 
dynamic parameter selection, data series visibility controls, and seamless integration 
with the existing GUI architecture as a popout window.

Key Features:
- Dynamic parameter selection for axes configuration
- Granular control over data series visibility (Pareto points, dominated points, lines)
- Real-time plot updates with manual refresh functionality
- Scrollable popout window for better accessibility
- Consistent design language adherence
- DPI export functionality
- Color and styling controls

Classes:
    ParallelCoordinatesControlPanel: Main control panel class for Parallel Coordinates plot management
    
Functions:
    create_parallel_coordinates_control_panel: Factory function for control panel instantiation

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


class ParallelCoordinatesControlPanel:
    """
    Advanced control panel for Parallel Coordinates plot visualization management in a separate popout window.
    
    This class provides comprehensive control over Parallel Coordinates plot rendering, including
    dynamic parameter selection, data series visibility management, and real-time plot updates. 
    It operates as a separate window for better accessibility and flexibility.
    
    Attributes:
        parent: Parent Tkinter widget
        plot_type: Type identifier for the plot ("parallel_coordinates")
        params_config: Configuration dictionary for optimization parameters
        responses_config: Configuration dictionary for response variables
        update_callback: Callback function for plot updates
        popup_window: Separate Toplevel window for the control panel
        main_frame: Primary container frame for the control panel
        scroll_canvas: Canvas widget for scrollable content
        scroll_frame: Scrollable frame container
        selected_params: List of BooleanVar objects for parameter selection
        series_visibility: Dictionary of BooleanVar objects for series visibility
        available_parameters: List of available parameters for axis selection
        available_responses: List of available responses for axis selection
        dpi_var: IntVar for export DPI selection
        color_scheme_var: StringVar for color scheme selection
        line_width_var: DoubleVar for line width setting
        alpha_var: DoubleVar for transparency setting
    """
    def __init__(self, parent: tk.Widget, plot_type: str, 
                 params_config: Dict[str, Any] = None,
                 responses_config: Dict[str, Any] = None,
                 update_callback: Callable = None):
        """
        Initialize the Parallel Coordinates plot control panel in a separate popout window.
        
        Args:
            parent: Parent Tkinter widget for the control panel
            plot_type: Type identifier, should be "parallel_coordinates"
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
        
        # Control variables for parameter selection
        self.selected_params = {}
        
        # Control variables for data series visibility
        self.series_visibility = {
            'show_pareto_points': tk.BooleanVar(value=True),
            'show_dominated_points': tk.BooleanVar(value=True),
            'show_lines': tk.BooleanVar(value=True),
            'show_legend': tk.BooleanVar(value=True),
            'show_grid': tk.BooleanVar(value=True),
            'show_axis_labels': tk.BooleanVar(value=True),
            'show_values_on_hover': tk.BooleanVar(value=True),
            'highlight_selected': tk.BooleanVar(value=False)
        }
        
        # Styling controls
        self.color_scheme_var = tk.StringVar(value="default")
        self.line_width_var = tk.DoubleVar(value=1.0)
        self.alpha_var = tk.DoubleVar(value=0.7)
        
        # Export DPI control
        self.dpi_var = tk.IntVar(value=300)
        
        # Data attributes for parameter selection
        self.available_parameters = []
        self.available_responses = []
        
        # Initialize the control panel
        self._initialize_available_options()
        self._create_popup_window()
        self._setup_event_bindings()
        
        logger.info(f"Enhanced Parallel Coordinates plot control panel initialized for {plot_type}")
    
    def _initialize_available_options(self) -> None:
        """
        Initialize the lists of available parameters and responses for axis selection.
        
        This method extracts parameter and response names from their configurations
        to populate the parameter selection checkboxes dynamically.
        """
        # Extract parameter names
        self.available_parameters = list(self.params_config.keys())
        
        # Extract response names
        self.available_responses = list(self.responses_config.keys())
        
        # Initialize parameter selection variables (all selected by default)
        for param in self.available_parameters:
            self.selected_params[param] = tk.BooleanVar(value=True)
        
        # Also add responses as selectable axes
        for response in self.available_responses:
            self.selected_params[response] = tk.BooleanVar(value=True)
        
        logger.debug(f"Initialized {len(self.available_parameters)} parameters and {len(self.available_responses)} responses for axis selection")
    
    def _create_popup_window(self) -> None:
        """
        Create the popup window for the control panel.
        
        This method creates a separate Toplevel window that houses the control panel,
        providing better accessibility and flexibility for users.
        """
        # Create the popup window
        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.title("Parallel Coordinates Plot Controls")
        self.popup_window.geometry("460x750")
        self.popup_window.resizable(True, True)
        
        # Set minimum size for responsive design
        self.popup_window.minsize(420, 650)
        
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
        
        # Parameter selection controls
        self._create_parameter_controls()
        
        # Data series visibility controls
        self._create_visibility_controls()
        
        # Styling controls
        self._create_styling_controls()
        
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
            text="Parallel Coordinates Plot Controls",
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
    
    def _create_parameter_controls(self) -> None:
        """
        Create parameter selection controls with checkboxes for each parameter/response.
        
        This method implements the core requirement for dynamic axis selection,
        providing checkboxes for each available parameter and response that can
        be included in the parallel coordinates plot.
        """
        # Parameter selection section
        param_section = tk.LabelFrame(
            self.scroll_frame,
            text="Axis Selection",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        param_section.pack(fill=tk.X, padx=5, pady=5)
        
        # Parameters subsection
        if self.available_parameters:
            param_label = tk.Label(
                param_section,
                text="Parameters:",
                bg=COLOR_SURFACE,
                fg=COLOR_SECONDARY,
                font=("Arial", 9, "bold")
            )
            param_label.pack(anchor=tk.W, pady=(0, 5))
            
            for param in self.available_parameters:
                param_frame = tk.Frame(param_section, bg=COLOR_SURFACE)
                param_frame.pack(fill=tk.X, pady=1)
                
                tk.Checkbutton(
                    param_frame,
                    text=param,
                    variable=self.selected_params[param],
                    bg=COLOR_SURFACE,
                    fg=COLOR_SECONDARY,
                    font=("Arial", 9),
                    activebackground=COLOR_BACKGROUND,
                    selectcolor=COLOR_SURFACE
                ).pack(side=tk.LEFT)
        
        # Responses subsection
        if self.available_responses:
            response_label = tk.Label(
                param_section,
                text="Responses:",
                bg=COLOR_SURFACE,
                fg=COLOR_SECONDARY,
                font=("Arial", 9, "bold")
            )
            response_label.pack(anchor=tk.W, pady=(10, 5))
            
            for response in self.available_responses:
                response_frame = tk.Frame(param_section, bg=COLOR_SURFACE)
                response_frame.pack(fill=tk.X, pady=1)
                
                tk.Checkbutton(
                    response_frame,
                    text=response,
                    variable=self.selected_params[response],
                    bg=COLOR_SURFACE,
                    fg=COLOR_SECONDARY,
                    font=("Arial", 9),
                    activebackground=COLOR_BACKGROUND,
                    selectcolor=COLOR_SURFACE
                ).pack(side=tk.LEFT)
        
        # Select all/none buttons
        button_frame = tk.Frame(param_section, bg=COLOR_SURFACE)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        select_all_btn = tk.Button(
            button_frame,
            text="Select All",
            command=self._select_all_params,
            bg=COLOR_SUCCESS,
            fg=COLOR_SURFACE,
            font=("Arial", 8, "bold"),
            relief="flat",
            padx=10,
            pady=3
        )
        select_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        select_none_btn = tk.Button(
            button_frame,
            text="Select None",
            command=self._select_none_params,
            bg=COLOR_WARNING,
            fg=COLOR_SURFACE,
            font=("Arial", 8, "bold"),
            relief="flat",
            padx=10,
            pady=3
        )
        select_none_btn.pack(side=tk.LEFT)
    
    def _create_visibility_controls(self) -> None:
        """
        Create data series visibility controls with granular checkbox widgets.
        
        This method implements the requirement for independent modulation of
        render states for different parallel coordinates data series components.
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
        
        # Pareto points checkbox
        pareto_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        pareto_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            pareto_frame,
            text="Pareto Optimal Points",
            variable=self.series_visibility['show_pareto_points'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            pareto_frame,
            text="(Non-dominated solutions)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Dominated points checkbox
        dominated_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        dominated_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            dominated_frame,
            text="Dominated Points",
            variable=self.series_visibility['show_dominated_points'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            dominated_frame,
            text="(Suboptimal solutions)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Lines checkbox
        lines_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        lines_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            lines_frame,
            text="Connection Lines",
            variable=self.series_visibility['show_lines'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            lines_frame,
            text="(Lines connecting axes)",
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
        
        # Axis labels checkbox
        labels_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        labels_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            labels_frame,
            text="Show Axis Labels",
            variable=self.series_visibility['show_axis_labels'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        # Hover values checkbox
        hover_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        hover_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            hover_frame,
            text="Show Values on Hover",
            variable=self.series_visibility['show_values_on_hover'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        # Highlight selected checkbox
        highlight_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        highlight_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            highlight_frame,
            text="Highlight Selected",
            variable=self.series_visibility['highlight_selected'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            highlight_frame,
            text="(Emphasize clicked lines)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
    
    def _create_styling_controls(self) -> None:
        """
        Create styling controls for color scheme, line width, and transparency.
        """
        # Styling controls section
        style_section = tk.LabelFrame(
            self.scroll_frame,
            text="Styling Options",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        style_section.pack(fill=tk.X, padx=5, pady=5)
        
        # Color scheme selection
        color_frame = tk.Frame(style_section, bg=COLOR_SURFACE)
        color_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            color_frame,
            text="Color Scheme:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        color_schemes = ["default", "viridis", "plasma", "coolwarm", "rainbow"]
        self.color_combo = ttk.Combobox(
            color_frame,
            textvariable=self.color_scheme_var,
            values=color_schemes,
            state="readonly",
            width=15
        )
        self.color_combo.pack(side=tk.LEFT)
        
        # Line width control
        width_frame = tk.Frame(style_section, bg=COLOR_SURFACE)
        width_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            width_frame,
            text="Line Width:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.width_scale = tk.Scale(
            width_frame,
            from_=0.5,
            to=5.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.line_width_var,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            highlightthickness=0,
            length=150
        )
        self.width_scale.pack(side=tk.LEFT)
        
        # Alpha (transparency) control
        alpha_frame = tk.Frame(style_section, bg=COLOR_SURFACE)
        alpha_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            alpha_frame,
            text="Transparency:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.alpha_scale = tk.Scale(
            alpha_frame,
            from_=0.1,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=self.alpha_var,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            highlightthickness=0,
            length=150
        )
        self.alpha_scale.pack(side=tk.LEFT)
    
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
        pass
    
    def _select_all_params(self) -> None:
        """Select all parameters for inclusion in the plot."""
        for param_var in self.selected_params.values():
            param_var.set(True)
        logger.debug("Selected all parameters for parallel coordinates plot")
    
    def _select_none_params(self) -> None:
        """Deselect all parameters from the plot."""
        for param_var in self.selected_params.values():
            param_var.set(False)
        logger.debug("Deselected all parameters for parallel coordinates plot")
    
    def _refresh_plot(self) -> None:
        """
        Handle the Refresh Plot button click to update the plot with current settings.
        
        This method is called when the user clicks the "Refresh Plot" button and
        triggers the plot update with all current control panel settings.
        """
        logger.info("Refreshing Parallel Coordinates plot with current settings")
        self._trigger_plot_update()
    
    def _trigger_plot_update(self) -> None:
        """
        Trigger immediate plot update using the registered callback.
        
        This method calls the update callback function if available, allowing
        the plot to be refreshed with the current control panel settings.
        """
        if self.update_callback:
            try:
                logger.info("Triggering Parallel Coordinates plot update")
                self.update_callback()
            except Exception as e:
                logger.error(f"Error calling plot update callback: {e}")
        else:
            logger.warning("No update callback registered for Parallel Coordinates plot")
    
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
            title="Export Parallel Coordinates Plot",
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
        default parameter selections and visibility settings.
        """
        # Reset parameter selections to all selected
        for param_var in self.selected_params.values():
            param_var.set(True)
        
        # Reset visibility controls to defaults
        self.series_visibility['show_pareto_points'].set(True)
        self.series_visibility['show_dominated_points'].set(True)
        self.series_visibility['show_lines'].set(True)
        self.series_visibility['show_legend'].set(True)
        self.series_visibility['show_grid'].set(True)
        self.series_visibility['show_axis_labels'].set(True)
        self.series_visibility['show_values_on_hover'].set(True)
        self.series_visibility['highlight_selected'].set(False)
        
        # Reset styling controls
        self.color_scheme_var.set("default")
        self.line_width_var.set(1.0)
        self.alpha_var.set(0.7)
        
        # Reset DPI to default
        self.dpi_var.set(300)
        
        logger.info("Parallel Coordinates plot controls reset to defaults")
        # Don't auto-refresh, user must click refresh button
    
    def get_display_options(self) -> Dict[str, Any]:
        """
        Get current display options for integration with the plotting system.
        
        This method returns a dictionary containing all current control settings
        in a format expected by the PyMBO plotting system. It serves as the
        primary interface between the control panel and the plot generation logic.
        
        Returns:
            Dict[str, Any]: Dictionary containing current display options including:
                - selected_params: List of selected parameter names
                - show_pareto_points: Whether to show Pareto optimal points
                - show_dominated_points: Whether to show dominated points
                - show_lines: Whether to show connection lines
                - show_legend: Whether to display the plot legend
                - color_scheme: Selected color scheme
                - line_width: Line width setting
                - alpha: Transparency setting
                - export_dpi: DPI setting for plot export
        """
        # Get selected parameters
        selected_param_names = [
            param for param, var in self.selected_params.items() 
            if var.get()
        ]
        
        options = {
            'selected_params': selected_param_names,
            'show_pareto_points': self.series_visibility['show_pareto_points'].get(),
            'show_dominated_points': self.series_visibility['show_dominated_points'].get(),
            'show_lines': self.series_visibility['show_lines'].get(),
            'show_legend': self.series_visibility['show_legend'].get(),
            'show_grid': self.series_visibility['show_grid'].get(),
            'show_axis_labels': self.series_visibility['show_axis_labels'].get(),
            'show_values_on_hover': self.series_visibility['show_values_on_hover'].get(),
            'highlight_selected': self.series_visibility['highlight_selected'].get(),
            'color_scheme': self.color_scheme_var.get(),
            'line_width': self.line_width_var.get(),
            'alpha': self.alpha_var.get(),
            'export_dpi': self.dpi_var.get()
        }
        
        logger.debug(f"Current display options: {options}")
        return options
    
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
        
        # Clear old parameter variables
        self.selected_params.clear()
        
        # Initialize new parameter selection variables
        for param in new_params:
            self.selected_params[param] = tk.BooleanVar(value=True)
        for response in new_responses:
            self.selected_params[response] = tk.BooleanVar(value=True)
        
        # Recreate the parameter controls if they exist
        if hasattr(self, 'scroll_frame') and self.scroll_frame:
            # Note: In a full implementation, you would recreate the parameter checkboxes
            # For now, we just update the internal data structures
            pass
        
        logger.info(f"Updated available options: {len(new_params)} parameters, {len(new_responses)} responses")
    
    def show(self) -> None:
        """Show the popout control panel window."""
        if self.popup_window:
            self.popup_window.deiconify()  # Show the window
            self.popup_window.lift()  # Bring to front
            self.popup_window.focus_set()  # Give focus
        logger.info("Parallel Coordinates plot control panel window shown")
    
    def hide(self) -> None:
        """Hide the popout control panel window."""
        if self.popup_window:
            self.popup_window.withdraw()  # Hide the window
        logger.info("Parallel Coordinates plot control panel window hidden")
    
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


def create_parallel_coordinates_control_panel(parent: tk.Widget, plot_type: str,
                                             params_config: Dict[str, Any] = None,
                                             responses_config: Dict[str, Any] = None,
                                             update_callback: Callable = None,
                                             export_callback: Callable = None) -> ParallelCoordinatesControlPanel:
    """
    Factory function for creating enhanced Parallel Coordinates plot control panels in popout windows.
    
    This function serves as the primary entry point for instantiating Parallel Coordinates plot
    control panels. It creates a separate popup window with comprehensive controls
    for Parallel Coordinates plot customization.
    
    Args:
        parent: Parent Tkinter widget for the control panel
        plot_type: Type identifier for the plot (should be "parallel_coordinates")
        params_config: Dictionary containing parameter configurations
        responses_config: Dictionary containing response configurations
        update_callback: Function to call when plot updates are needed
        export_callback: Function to call for plot export (filename, dpi) -> None
    
    Returns:
        ParallelCoordinatesControlPanel: Initialized control panel instance in popup window
    
    Raises:
        Exception: If control panel creation fails
    
    Example:
        >>> control_panel = create_parallel_coordinates_control_panel(
        ...     parent=main_window,
        ...     plot_type="parallel_coordinates",
        ...     params_config=param_dict,
        ...     responses_config=response_dict,
        ...     update_callback=update_plot_function,
        ...     export_callback=export_plot_function
        ... )
    """
    try:
        logger.info(f"Creating enhanced Parallel Coordinates control panel for plot type: {plot_type}")
        
        control_panel = ParallelCoordinatesControlPanel(
            parent=parent,
            plot_type=plot_type,
            params_config=params_config,
            responses_config=responses_config,
            update_callback=update_callback
        )
        
        # Set export callback if provided
        if export_callback:
            control_panel.set_export_callback(export_callback)
        
        logger.info("Enhanced Parallel Coordinates control panel created successfully in popup window")
        return control_panel
        
    except Exception as e:
        logger.error(f"Failed to create Parallel Coordinates control panel: {e}")
        raise