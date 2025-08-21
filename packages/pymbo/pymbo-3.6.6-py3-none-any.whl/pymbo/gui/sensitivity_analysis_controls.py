"""
Enhanced Sensitivity Analysis Plot Control Module

This module provides an advanced graphical user interface for controlling Sensitivity Analysis
plot visualizations within the PyMBO optimization framework. It implements dynamic method
and response selection, algorithm parameter controls, and seamless integration with 
the existing GUI architecture as a popout window.

Key Features:
- Dynamic sensitivity method selection with 6 different algorithms
- Response selection for analysis target
- Algorithm parameter controls (iterations, random seed)
- Real-time plot updates with manual refresh functionality
- Scrollable popout window for better accessibility
- Consistent design language adherence
- DPI export functionality
- Axis range controls with auto/manual settings

Classes:
    SensitivityAnalysisControlPanel: Main control panel class for Sensitivity Analysis plot management
    
Functions:
    create_sensitivity_analysis_control_panel: Factory function for control panel instantiation

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


class SensitivityAnalysisControlPanel:
    """
    Advanced control panel for Sensitivity Analysis plot visualization management in a separate popout window.
    
    This class provides comprehensive control over Sensitivity Analysis plot rendering, including
    dynamic method and response selection, algorithm parameter management, and 
    real-time plot updates. It operates as a separate window for better accessibility 
    and flexibility.
    
    Attributes:
        parent: Parent Tkinter widget
        plot_type: Type identifier for the plot ("sensitivity_analysis")
        params_config: Configuration dictionary for optimization parameters
        responses_config: Configuration dictionary for response variables
        update_callback: Callback function for plot updates
        popup_window: Separate Toplevel window for the control panel
        main_frame: Primary container frame for the control panel
        scroll_canvas: Canvas widget for scrollable content
        scroll_frame: Scrollable frame container
        response_var: StringVar for response selection
        algorithm_var: StringVar for sensitivity method selection
        iterations_var: StringVar for number of samples/iterations
        random_seed_var: StringVar for random seed control
        available_responses: List of available responses for analysis
        available_methods: List of available sensitivity analysis methods
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
        Initialize the Sensitivity Analysis plot control panel in a separate popout window.
        
        Args:
            parent: Parent Tkinter widget for the control panel
            plot_type: Type identifier, should be "sensitivity_analysis"
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
        
        # Control variables for analysis settings
        self.response_var = tk.StringVar()
        self.algorithm_var = tk.StringVar()
        self.iterations_var = tk.StringVar(value="500")
        self.random_seed_var = tk.StringVar(value="42")
        
        # Export DPI control
        self.dpi_var = tk.IntVar(value=300)
        
        # Axis range controls
        self.x_min_var = tk.StringVar(value="")
        self.x_max_var = tk.StringVar(value="")
        self.x_auto_var = tk.BooleanVar(value=True)
        self.y_min_var = tk.StringVar(value="")
        self.y_max_var = tk.StringVar(value="")
        self.y_auto_var = tk.BooleanVar(value=True)
        
        # Data attributes for selection options
        self.available_responses = []
        self.available_methods = [
            ("Variance-based", "variance"),
            ("Morris Elementary Effects", "morris"),
            ("Gradient-based", "gradient"),
            ("Sobol-like", "sobol"),
            ("GP Lengthscale", "lengthscale"),
            ("Feature Importance", "feature_importance"),
            ("Mixed Parameter Sensitivity", "mixed")
        ]
        
        # Info label for method descriptions
        self.method_info_label = None
        
        # Initialize the control panel
        self._initialize_available_options()
        self._create_popup_window()
        self._setup_event_bindings()
        
        logger.info(f"Enhanced Sensitivity Analysis plot control panel initialized for {plot_type}")
    
    def _initialize_available_options(self) -> None:
        """
        Initialize the lists of available responses for analysis selection.
        
        This method extracts response names from their configurations
        to populate the response selection combobox dynamically.
        """
        # Extract response names
        self.available_responses = list(self.responses_config.keys())
        
        # Set default selections
        if self.available_responses:
            self.response_var.set(self.available_responses[0])
        if self.available_methods:
            self.algorithm_var.set(self.available_methods[0][0])  # Display name
        
        logger.debug(f"Initialized {len(self.available_responses)} responses for sensitivity analysis")
    
    def _create_popup_window(self) -> None:
        """
        Create the popup window for the control panel.
        
        This method creates a separate Toplevel window that houses the control panel,
        providing better accessibility and flexibility for users.
        """
        # Create the popup window
        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.title("Sensitivity Analysis Plot Controls")
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
        
        # Analysis configuration controls
        self._create_analysis_controls()
        
        # Method information display
        self._create_method_info()
        
        # Algorithm parameter controls
        self._create_parameter_controls()
        
        # Axis range controls
        self._create_axis_range_controls()
        
        # Export controls
        self._create_export_controls()
        
        # Action buttons
        self._create_action_buttons()
        
        # Configure scrollable area
        self._configure_scrolling()
        
        # Update method info initially
        self._update_method_info()
    
    def _create_title_header(self):
        """Create the title header with consistent typography and styling."""
        header_frame = tk.Frame(self.main_frame, bg=COLOR_PRIMARY, height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="Sensitivity Analysis Controls",
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
    
    def _create_analysis_controls(self) -> None:
        """
        Create analysis configuration controls with response and method selection.
        
        This method implements the core requirement for dynamic response and method selection,
        providing comboboxes populated with available responses and sensitivity methods
        and event listeners for plot updates.
        """
        # Analysis controls section
        analysis_section = tk.LabelFrame(
            self.scroll_frame,
            text="Analysis Configuration",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        analysis_section.pack(fill=tk.X, padx=5, pady=5)
        
        # Response selection
        response_frame = tk.Frame(analysis_section, bg=COLOR_SURFACE)
        response_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            response_frame,
            text="Response Variable:",
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
        
        # Sensitivity method selection
        method_frame = tk.Frame(analysis_section, bg=COLOR_SURFACE)
        method_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            method_frame,
            text="Sensitivity Method:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        method_names = [method[0] for method in self.available_methods]
        self.method_combo = ttk.Combobox(
            method_frame,
            textvariable=self.algorithm_var,
            values=method_names,
            state="readonly",
            width=25
        )
        self.method_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind method selection change to update info
        self.method_combo.bind('<<ComboboxSelected>>', lambda e: self._update_method_info())
    
    def _create_method_info(self) -> None:
        """
        Create method information display section.
        """
        # Method info section
        info_section = tk.LabelFrame(
            self.scroll_frame,
            text="Method Information",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        info_section.pack(fill=tk.X, padx=5, pady=5)
        
        self.method_info_label = tk.Label(
            info_section,
            text="Select a sensitivity analysis method to see details",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 9),
            wraplength=400,
            justify=tk.LEFT
        )
        self.method_info_label.pack(fill=tk.X, pady=5)
    
    def _create_parameter_controls(self) -> None:
        """
        Create algorithm parameter controls for iterations and random seed.
        """
        # Parameter controls section
        param_section = tk.LabelFrame(
            self.scroll_frame,
            text="Algorithm Parameters",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        param_section.pack(fill=tk.X, padx=5, pady=5)
        
        # Iterations control
        iter_frame = tk.Frame(param_section, bg=COLOR_SURFACE)
        iter_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            iter_frame,
            text="Iterations/Samples:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.iterations_entry = tk.Entry(
            iter_frame,
            textvariable=self.iterations_var,
            width=10,
            font=("Arial", 9)
        )
        self.iterations_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(
            iter_frame,
            text="(50-5000)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT)
        
        # Random seed control
        seed_frame = tk.Frame(param_section, bg=COLOR_SURFACE)
        seed_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            seed_frame,
            text="Random Seed:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.seed_entry = tk.Entry(
            seed_frame,
            textvariable=self.random_seed_var,
            width=10,
            font=("Arial", 9)
        )
        self.seed_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(
            seed_frame,
            text="(for reproducibility)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT)
    
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
        # Note: We removed automatic updates to match benchmark requirement
        # Users must click "Refresh Plot" to update the plot
        pass
    
    def _update_method_info(self):
        """Update the method information display based on selected method."""
        if not self.method_info_label:
            return
            
        method_name = self.algorithm_var.get()
        
        info_text = {
            "Variance-based": "Measures how much each parameter contributes to output variance. Higher values indicate more influential parameters. Fast computation, good for initial screening.",
            
            "Morris Elementary Effects": "Calculates elementary effects using Morris screening method. Shows local sensitivity with statistical confidence intervals. Robust for non-linear responses.",
            
            "Gradient-based": "Estimates local gradients at multiple points using finite differences. Good for smooth response surfaces with uncertainty quantification. Shows direction of influence.",
            
            "Sobol-like": "Simplified Sobol indices showing global sensitivity. Measures main effects and interaction importance. Robust across different response surface types.",
            
            "GP Lengthscale": "Uses GP model lengthscales directly as sensitivity indicators. Short lengthscales indicate high sensitivity. Model-intrinsic method, very fast computation.",
            
            "Feature Importance": "Permutation-based importance using prediction variance differences. Model-agnostic sensitivity measure. Good for non-parametric analysis.",
            
            "Mixed Parameter Sensitivity": "Comprehensive analysis of both continuous and discrete parameters. Uses variance-based methods for continuous parameters and exhaustive enumeration for discrete parameters. Shows complete parameter influence ranking."
        }
        
        self.method_info_label.config(
            text=info_text.get(method_name, "Select a sensitivity analysis method to see details")
        )
    
    def _refresh_plot(self) -> None:
        """
        Handle the Refresh Plot button click to update the plot with current settings.
        
        This method is called when the user clicks the "Refresh Plot" button and
        triggers the plot update with all current control panel settings.
        """
        logger.info("Refreshing Sensitivity Analysis plot with current settings")
        self._trigger_plot_update()
    
    def _trigger_plot_update(self) -> None:
        """
        Trigger immediate plot update using the registered callback.
        
        This method calls the update callback function if available, allowing
        the plot to be refreshed with the current control panel settings.
        """
        if self.update_callback:
            try:
                logger.info("Triggering Sensitivity Analysis plot update")
                self.update_callback()
            except Exception as e:
                logger.error(f"Error calling plot update callback: {e}")
        else:
            logger.warning("No update callback registered for Sensitivity Analysis plot")
    
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
            title="Export Sensitivity Analysis Plot",
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
        default response and method selections and parameter settings.
        """
        # Reset selections to defaults
        if self.available_responses:
            self.response_var.set(self.available_responses[0])
        if self.available_methods:
            self.algorithm_var.set(self.available_methods[0][0])
        
        # Reset algorithm parameters to defaults
        self.iterations_var.set("500")
        self.random_seed_var.set("42")
        
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
        
        # Update method info
        self._update_method_info()
        
        logger.info("Sensitivity Analysis plot controls reset to defaults")
        # Don't auto-refresh, user must click refresh button
    
    def get_sensitivity_settings(self) -> Dict[str, Any]:
        """
        Get current sensitivity analysis settings for integration with the plotting system.
        
        This method returns a dictionary containing all current control settings
        in a format expected by the PyMBO plotting system. It serves as the
        primary interface between the control panel and the plot generation logic.
        
        Returns:
            Dict[str, Any]: Dictionary containing current sensitivity settings including:
                - response: Currently selected response variable
                - algorithm_code: Currently selected sensitivity method code
                - iterations: Number of samples/iterations
                - random_seed: Random seed for reproducibility
        """
        # Convert display name to algorithm code
        method_mapping = {method[0]: method[1] for method in self.available_methods}
        algorithm_code = method_mapping.get(self.algorithm_var.get(), "variance")
        
        settings = {
            'response': self.response_var.get(),
            'algorithm_code': algorithm_code,
            'iterations': self.iterations_var.get(),
            'random_seed': self.random_seed_var.get()
        }
        
        logger.debug(f"Current sensitivity settings: {settings}")
        return settings
    
    def get_axis_ranges(self) -> Dict[str, Tuple]:
        """
        Get current axis range settings for integration with the plotting system.
        
        Returns:
            Dict[str, Tuple]: Dictionary containing axis ranges where each value is a tuple of
                (min_value, max_value, is_auto) for x_range and y_range
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
            "x_range": (x_min, x_max, self.x_auto_var.get()),
            "y_range": (y_min, y_max, self.y_auto_var.get())
        }
        
        logger.debug(f"Current axis ranges: {ranges}")
        return ranges
    
    def update_available_options(self, new_responses: List[str]) -> None:
        """
        Update the available responses for analysis selection.
        
        This method allows dynamic updating of the response list when
        the optimization configuration changes.
        
        Args:
            new_responses: List of new response names to make available
        """
        self.available_responses = new_responses
        
        # Update combobox values
        if hasattr(self, 'response_combo'):
            self.response_combo['values'] = new_responses
        
        # Update selection if current one is no longer valid
        if self.response_var.get() not in new_responses and new_responses:
            self.response_var.set(new_responses[0])
        
        logger.info(f"Updated available responses: {len(new_responses)} responses")
    
    def show(self) -> None:
        """Show the popout control panel window."""
        if self.popup_window:
            self.popup_window.deiconify()  # Show the window
            self.popup_window.lift()  # Bring to front
            self.popup_window.focus_set()  # Give focus
        logger.info("Sensitivity Analysis plot control panel window shown")
    
    def hide(self) -> None:
        """Hide the popout control panel window."""
        if self.popup_window:
            self.popup_window.withdraw()  # Hide the window
        logger.info("Sensitivity Analysis plot control panel window hidden")
    
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


def create_sensitivity_analysis_control_panel(parent: tk.Widget, plot_type: str,
                                             params_config: Dict[str, Any] = None,
                                             responses_config: Dict[str, Any] = None,
                                             update_callback: Callable = None,
                                             export_callback: Callable = None) -> SensitivityAnalysisControlPanel:
    """
    Factory function for creating enhanced Sensitivity Analysis plot control panels in popout windows.
    
    This function serves as the primary entry point for instantiating Sensitivity Analysis plot
    control panels. It creates a separate popup window with comprehensive controls
    for Sensitivity Analysis plot customization.
    
    Args:
        parent: Parent Tkinter widget for the control panel
        plot_type: Type identifier for the plot (should be "sensitivity_analysis")
        params_config: Dictionary containing parameter configurations
        responses_config: Dictionary containing response configurations
        update_callback: Function to call when plot updates are needed
        export_callback: Function to call for plot export (filename, dpi) -> None
    
    Returns:
        SensitivityAnalysisControlPanel: Initialized control panel instance in popup window
    
    Raises:
        Exception: If control panel creation fails
    
    Example:
        >>> control_panel = create_sensitivity_analysis_control_panel(
        ...     parent=main_window,
        ...     plot_type="sensitivity_analysis",
        ...     params_config=param_dict,
        ...     responses_config=response_dict,
        ...     update_callback=update_plot_function,
        ...     export_callback=export_plot_function
        ... )
    """
    try:
        logger.info(f"Creating enhanced Sensitivity Analysis control panel for plot type: {plot_type}")
        
        control_panel = SensitivityAnalysisControlPanel(
            parent=parent,
            plot_type=plot_type,
            params_config=params_config,
            responses_config=responses_config,
            update_callback=update_callback
        )
        
        # Set export callback if provided
        if export_callback:
            control_panel.set_export_callback(export_callback)
        
        logger.info("Enhanced Sensitivity Analysis control panel created successfully in popup window")
        return control_panel
        
    except Exception as e:
        logger.error(f"Failed to create Sensitivity Analysis control panel: {e}")
        raise