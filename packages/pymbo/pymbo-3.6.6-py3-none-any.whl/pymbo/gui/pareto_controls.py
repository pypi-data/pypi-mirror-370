"""
Enhanced Pareto Plot Control Module

This module provides an advanced graphical user interface for controlling Pareto plot
visualizations within the PyMBO optimization framework. It implements dynamic axis
binding, data series visibility controls, and seamless integration with the existing
GUI architecture.

Key Features:
- Dynamic axis selection via comboboxes populated from data attributes
- Granular control over data series visibility (non-dominated, dominated, frontier)
- Real-time plot updates with asynchronous event handling
- Scrollable layout for viewport overflow management
- Consistent design language adherence

Classes:
    ParetoPlotControlPanel: Main control panel class for Pareto plot management
    
Functions:
    create_pareto_control_panel: Factory function for control panel instantiation

Author: PyMBO Development Team
Version: 3.6.6 Enhanced
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


class ParetoPlotControlPanel:
    """
    Advanced control panel for Pareto plot visualization management in a separate popout window.
    
    This class provides comprehensive control over Pareto plot rendering, including
    dynamic axis selection, data series visibility management, and real-time plot
    updates. It operates as a separate window for better accessibility and flexibility.
    
    Attributes:
        parent: Parent Tkinter widget
        plot_type: Type identifier for the plot ("pareto")
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
        available_columns: List of available data columns for axis selection
        dpi_var: IntVar for export DPI selection
    """
    
    def __init__(self, parent: tk.Widget, plot_type: str, 
                 params_config: Dict[str, Any] = None,
                 responses_config: Dict[str, Any] = None,
                 update_callback: Callable = None):
        """
        Initialize the Pareto plot control panel in a separate popout window.
        
        Args:
            parent: Parent Tkinter widget for the control panel
            plot_type: Type identifier, should be "pareto"
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
        self.x_axis_var = tk.StringVar()
        self.y_axis_var = tk.StringVar()
        
        # Control variables for data series visibility
        self.series_visibility = {
            'show_non_dominated': tk.BooleanVar(value=True),
            'show_dominated': tk.BooleanVar(value=True),
            'show_pareto_frontier': tk.BooleanVar(value=True),
            'show_additional_points': tk.BooleanVar(value=False),
            'show_legend': tk.BooleanVar(value=True)
        }
        
        # Export DPI control
        self.dpi_var = tk.IntVar(value=300)
        
        # Data attributes for axis selection
        self.available_columns = []
        
        # Initialize the control panel
        self._initialize_data_columns()
        self._create_popup_window()
        self._setup_event_bindings()
        
        logger.info(f"Enhanced Pareto plot control panel initialized for {plot_type}")
    
    def _initialize_data_columns(self) -> None:
        """
        Initialize the list of available data columns for axis selection.
        
        This method extracts column names from both parameter and response
        configurations to populate the axis selection comboboxes dynamically.
        """
        self.available_columns = []
        
        # Extract parameter columns - only optimization objectives, not constraints
        for param_name, param_config in self.params_config.items():
            if param_config.get("goal") in ["Maximize", "Minimize"]:
                self.available_columns.append(param_name)
        
        # Extract response columns - only optimization objectives, not constraints
        for response_name, response_config in self.responses_config.items():
            if response_config.get("goal") in ["Maximize", "Minimize"]:
                self.available_columns.append(response_name)
        
        # Set default selections
        if len(self.available_columns) >= 2:
            self.x_axis_var.set(self.available_columns[0])
            self.y_axis_var.set(self.available_columns[1])
        elif len(self.available_columns) == 1:
            self.x_axis_var.set(self.available_columns[0])
            self.y_axis_var.set(self.available_columns[0])
        
        logger.debug(f"Initialized {len(self.available_columns)} data columns for axis selection")
    
    def _create_popup_window(self) -> None:
        """
        Create the popup window for the control panel.
        
        This method creates a separate Toplevel window that houses the control panel,
        providing better accessibility and flexibility for users.
        """
        # Create the popup window
        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.title("Pareto Front Plot Controls")
        self.popup_window.geometry("400x600")
        self.popup_window.resizable(True, True)
        
        # Set minimum size for responsive design
        self.popup_window.minsize(350, 500)
        
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
        
        # Export controls
        self._create_export_controls()
        
        # Action buttons
        self._create_action_buttons()
        
        # Configure scrollable area
        self._configure_scrolling()
    
    def _create_title_header(self) -> None:
        """
        Create the title header with consistent typography and styling.
        """
        header_frame = tk.Frame(self.main_frame, bg=COLOR_PRIMARY, height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Pareto Plot Controls",
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
        providing comboboxes populated with available data attributes and
        event listeners for asynchronous plot updates.
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
        
        # X-axis selection
        x_axis_frame = tk.Frame(axis_section, bg=COLOR_SURFACE)
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
            values=self.available_columns,
            state="readonly",
            width=20
        )
        self.x_axis_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Y-axis selection
        y_axis_frame = tk.Frame(axis_section, bg=COLOR_SURFACE)
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
            values=self.available_columns,
            state="readonly",
            width=20
        )
        self.y_axis_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_visibility_controls(self) -> None:
        """
        Create data series visibility controls with granular checkbox widgets.
        
        This method implements the requirement for independent modulation of
        render states for different data series components including non-dominated
        solutions, Pareto frontier approximation, and dominated solution space.
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
        
        # Non-dominated solutions checkbox
        non_dominated_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        non_dominated_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            non_dominated_frame,
            text="Non-dominated Solutions",
            variable=self.series_visibility['show_non_dominated'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            non_dominated_frame,
            text="(Pareto optimal points)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Dominated solutions checkbox
        dominated_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        dominated_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            dominated_frame,
            text="Dominated Solution Space",
            variable=self.series_visibility['show_dominated'],
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
        
        # Pareto frontier checkbox
        frontier_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        frontier_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            frontier_frame,
            text="Pareto Frontier Approximation",
            variable=self.series_visibility['show_pareto_frontier'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            frontier_frame,
            text="(Interpolated boundary)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Additional points checkbox
        additional_frame = tk.Frame(visibility_section, bg=COLOR_SURFACE)
        additional_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            additional_frame,
            text="Additional Points",
            variable=self.series_visibility['show_additional_points'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            additional_frame,
            text="(Custom data points)",
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
    
    def _configure_scrolling(self) -> None:
        """
        Configure the scrollable area with proper event bindings.
        """
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
        # Note: We removed automatic updates to match requirement #7
        # Users must click "Refresh Plot" to update the plot
        pass
    
    def _refresh_plot(self) -> None:
        """
        Handle the Refresh Plot button click to update the plot with current settings.
        
        This method is called when the user clicks the "Refresh Plot" button and
        triggers the plot update with all current control panel settings.
        """
        logger.info("Refreshing Pareto plot with current settings")
        self._trigger_plot_update()
    
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
            title="Export Pareto Plot",
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
    
    def _trigger_plot_update(self) -> None:
        """
        Trigger immediate plot update using the registered callback.
        
        This method calls the update callback function if available, allowing
        the plot to be refreshed with the current control panel settings.
        """
        if self.update_callback:
            try:
                logger.info("Triggering Pareto plot update")
                self.update_callback()
            except Exception as e:
                logger.error(f"Error calling plot update callback: {e}")
        else:
            logger.warning("No update callback registered for Pareto plot")
    
    def _reset_to_defaults(self) -> None:
        """
        Reset all controls to their default values.
        
        This method restores the control panel to its initial state, including
        default axis selections and visibility settings.
        """
        # Reset axis selections to defaults
        if len(self.available_columns) >= 2:
            self.x_axis_var.set(self.available_columns[0])
            self.y_axis_var.set(self.available_columns[1])
        
        # Reset visibility controls to defaults
        self.series_visibility['show_non_dominated'].set(True)
        self.series_visibility['show_dominated'].set(True)
        self.series_visibility['show_pareto_frontier'].set(True)
        self.series_visibility['show_additional_points'].set(False)
        self.series_visibility['show_legend'].set(True)
        
        # Reset DPI to default
        self.dpi_var.set(300)
        
        logger.info("Pareto plot controls reset to defaults")
        # Don't auto-refresh, user must click refresh button
    
    def get_display_options(self) -> Dict[str, Any]:
        """
        Get current display options for integration with the plotting system.
        
        This method returns a dictionary containing all current control settings
        in a format expected by the PyMBO plotting system. It serves as the
        primary interface between the control panel and the plot generation logic.
        
        Returns:
            Dict[str, Any]: Dictionary containing current display options including:
                - x_objective: Currently selected X-axis variable
                - y_objective: Currently selected Y-axis variable
                - show_all_solutions: Whether to show dominated solutions
                - show_pareto_points: Whether to show non-dominated points
                - show_pareto_front: Whether to show Pareto frontier line
                - show_additional_points: Whether to show additional custom points
                - show_legend: Whether to display the plot legend
                - export_dpi: DPI setting for plot export
        """
        options = {
            'x_objective': self.x_axis_var.get(),
            'y_objective': self.y_axis_var.get(),
            'show_all_solutions': self.series_visibility['show_dominated'].get(),
            'show_pareto_points': self.series_visibility['show_non_dominated'].get(),
            'show_pareto_front': self.series_visibility['show_pareto_frontier'].get(),
            'show_additional_points': self.series_visibility['show_additional_points'].get(),
            'show_legend': self.series_visibility['show_legend'].get(),
            'export_dpi': self.dpi_var.get()
        }
        
        logger.debug(f"Current display options: {options}")
        return options
    
    def update_available_columns(self, new_columns: List[str]) -> None:
        """
        Update the available columns for axis selection.
        
        This method allows dynamic updating of the column lists when new data
        becomes available or when the optimization configuration changes.
        
        Args:
            new_columns: List of new column names to make available
        """
        self.available_columns = new_columns
        
        # Update combobox values
        if hasattr(self, 'x_axis_combo'):
            self.x_axis_combo['values'] = new_columns
        if hasattr(self, 'y_axis_combo'):
            self.y_axis_combo['values'] = new_columns
        
        # Update selections if current ones are no longer valid
        if self.x_axis_var.get() not in new_columns and new_columns:
            self.x_axis_var.set(new_columns[0])
        if self.y_axis_var.get() not in new_columns and len(new_columns) > 1:
            self.y_axis_var.set(new_columns[1])
        
        logger.info(f"Updated available columns: {len(new_columns)} columns")
    
    def show(self) -> None:
        """Show the popout control panel window."""
        if self.popup_window:
            self.popup_window.deiconify()  # Show the window
            self.popup_window.lift()  # Bring to front
            self.popup_window.focus_set()  # Give focus
        logger.info("Pareto plot control panel window shown")
    
    def hide(self) -> None:
        """Hide the popout control panel window."""
        if self.popup_window:
            self.popup_window.withdraw()  # Hide the window
        logger.info("Pareto plot control panel window hidden")
    
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


def create_pareto_control_panel(parent: tk.Widget, plot_type: str,
                               params_config: Dict[str, Any] = None,
                               responses_config: Dict[str, Any] = None,
                               update_callback: Callable = None,
                               export_callback: Callable = None) -> ParetoPlotControlPanel:
    """
    Factory function for creating enhanced Pareto plot control panels in popout windows.
    
    This function serves as the primary entry point for instantiating Pareto plot
    control panels. It creates a separate popup window with comprehensive controls
    for Pareto plot customization.
    
    Args:
        parent: Parent Tkinter widget for the control panel
        plot_type: Type identifier for the plot (should be "pareto")
        params_config: Dictionary containing parameter configurations
        responses_config: Dictionary containing response configurations
        update_callback: Function to call when plot updates are needed
        export_callback: Function to call for plot export (filename, dpi) -> None
    
    Returns:
        ParetoPlotControlPanel: Initialized control panel instance in popup window
    
    Raises:
        Exception: If control panel creation fails
    
    Example:
        >>> control_panel = create_pareto_control_panel(
        ...     parent=main_window,
        ...     plot_type="pareto",
        ...     params_config=param_dict,
        ...     responses_config=response_dict,
        ...     update_callback=update_plot_function,
        ...     export_callback=export_plot_function
        ... )
    """
    try:
        logger.info(f"Creating enhanced Pareto control panel for plot type: {plot_type}")
        
        control_panel = ParetoPlotControlPanel(
            parent=parent,
            plot_type=plot_type,
            params_config=params_config,
            responses_config=responses_config,
            update_callback=update_callback
        )
        
        # Set export callback if provided
        if export_callback:
            control_panel.set_export_callback(export_callback)
        
        logger.info("Enhanced Pareto control panel created successfully in popup window")
        return control_panel
        
    except Exception as e:
        logger.error(f"Failed to create Pareto control panel: {e}")
        raise