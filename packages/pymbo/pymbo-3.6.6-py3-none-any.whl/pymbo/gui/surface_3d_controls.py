"""
Enhanced 3D Surface Plot Control Module

This module provides an advanced graphical user interface for controlling 3D surface plot
visualizations within the PyMBO optimization framework. It supports three surface modes:
1. Individual Objective Surfaces
2. Weighted-Sum (Scalarized) Surface  
3. Acquisition Function Surface

Key Features:
- Surface mode selection with dynamic control adaptation
- Parameter and response selection for axis binding
- Granular control over visualization options
- Real-time plot updates with manual refresh pattern
- Scrollable layout for viewport overflow management
- Consistent design language following GP Slice controls benchmark

Classes:
    SurfacePlotControlPanel: Main control panel class for 3D surface plot management
    
Functions:
    create_3d_surface_control_panel: Factory function for control panel instantiation

Author: PyMBO Development Team
Version: 3.6.6 Enhanced
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


class SurfacePlotControlPanel:
    """
    Advanced control panel for 3D surface plot visualization management in a separate popout window.
    
    This class provides comprehensive control over 3D surface plot rendering, including
    surface mode selection, parameter/response selection, and visualization options.
    It operates as a separate window for better accessibility and flexibility.
    
    Attributes:
        parent: Parent Tkinter widget
        plot_type: Type identifier for the plot ("3d_surface")
        params_config: Configuration dictionary for optimization parameters
        responses_config: Configuration dictionary for response variables
        update_callback: Callback function for plot updates
        popup_window: Separate Toplevel window for the control panel
        main_frame: Primary container frame for the control panel
        scroll_canvas: Canvas widget for scrollable content
        scroll_frame: Scrollable frame container
        surface_mode_var: StringVar for surface mode selection
        param1_var: StringVar for X-axis parameter selection
        param2_var: StringVar for Y-axis parameter selection
        response_var: StringVar for response selection (individual mode)
        series_visibility: Dictionary of BooleanVar objects for series visibility
        available_parameters: List of available parameters for axis selection
        available_responses: List of available responses for selection
        dpi_var: IntVar for export DPI selection
    """
    
    def __init__(self, parent: tk.Widget, plot_type: str, 
                 params_config: Dict[str, Any] = None,
                 responses_config: Dict[str, Any] = None,
                 update_callback: Callable = None,
                 global_importance_weights: Dict[str, float] = None):
        """
        Initialize the 3D surface plot control panel in a separate popout window.
        
        Args:
            parent: Parent Tkinter widget for the control panel
            plot_type: Type identifier, should be "3d_surface"
            params_config: Dictionary containing parameter configurations
            responses_config: Dictionary containing response configurations
            update_callback: Function to call when plot updates are needed
        """
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.global_importance_weights = global_importance_weights or {}
        
        # Create separate popup window
        self.popup_window = None
        
        # GUI components
        self.main_frame = None
        self.scroll_canvas = None
        self.scroll_frame = None
        self.scrollbar = None
        
        # Surface mode control
        self.surface_mode_var = tk.StringVar(value="individual")
        
        # Control variables for parameter/response binding
        self.param1_var = tk.StringVar()  # X-axis parameter
        self.param2_var = tk.StringVar()  # Y-axis parameter
        self.response_var = tk.StringVar()  # Response for individual mode
        
        # Control variables for visualization options
        self.series_visibility = {
            'show_surface': tk.BooleanVar(value=True),
            'show_uncertainty': tk.BooleanVar(value=False),
            'show_contours': tk.BooleanVar(value=True),
            'show_data_points': tk.BooleanVar(value=True),
            'show_legend': tk.BooleanVar(value=True)
        }
        
        # Plot style control
        self.plot_style_var = tk.StringVar(value="surface")
        
        # Color palette control
        self.color_palette_var = tk.StringVar(value="viridis")
        
        # Export DPI control
        self.dpi_var = tk.IntVar(value=300)
        
        # Axis range controls
        self.x_min_var = tk.StringVar(value="")
        self.x_max_var = tk.StringVar(value="")
        self.x_auto_var = tk.BooleanVar(value=True)
        self.y_min_var = tk.StringVar(value="")
        self.y_max_var = tk.StringVar(value="")
        self.y_auto_var = tk.BooleanVar(value=True)
        self.z_min_var = tk.StringVar(value="")
        self.z_max_var = tk.StringVar(value="")
        self.z_auto_var = tk.BooleanVar(value=True)
        
        # Resolution control
        self.resolution_var = tk.IntVar(value=60)
        
        # Data attributes for selection
        self.available_parameters = []
        self.available_responses = []
        
        # Dynamic control containers
        self.individual_controls_frame = None
        self.weighted_sum_controls_frame = None
        self.acquisition_controls_frame = None
        
        # Weight controls for weighted-sum mode
        self.weight_sliders = {}  # Will hold slider variables for each response
        self.weight_vars = {}     # Will hold DoubleVar objects for weights
        self.use_global_weights_var = tk.BooleanVar(value=True)  # Use global importance weights by default
        
        # Initialize the control panel
        self._initialize_available_options()
        self._create_popup_window()
        self._setup_event_bindings()
        
        logger.info(f"Enhanced 3D surface plot control panel initialized for {plot_type}")
    
    def _initialize_available_options(self) -> None:
        """
        Initialize the list of available parameters and responses for selection.
        
        This method extracts parameter and response names from configurations to populate
        the selection comboboxes dynamically.
        """
        self.available_parameters = []
        self.available_responses = []
        
        # Extract parameter names (need at least 2 for 3D surface)
        for param_name, param_config in self.params_config.items():
            if param_config.get("bounds"):  # Only parameters with bounds can be varied
                self.available_parameters.append(param_name)
        
        # Extract response names - only optimization objectives, not constraints
        for response_name, response_config in self.responses_config.items():
            if response_config.get("goal") in ["Maximize", "Minimize"]:
                self.available_responses.append(response_name)
        
        # Set default selections
        if len(self.available_parameters) >= 2:
            self.param1_var.set(self.available_parameters[0])
            self.param2_var.set(self.available_parameters[1])
        elif len(self.available_parameters) == 1:
            self.param1_var.set(self.available_parameters[0])
            self.param2_var.set(self.available_parameters[0])
        
        if self.available_responses:
            self.response_var.set(self.available_responses[0])
        
        logger.debug(f"Initialized {len(self.available_parameters)} parameters and {len(self.available_responses)} responses")
    
    def _create_popup_window(self) -> None:
        """
        Create the popup window for the control panel.
        
        This method creates a separate Toplevel window that houses the control panel,
        providing better accessibility and flexibility for users.
        """
        # Create the popup window
        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.title("3D Surface Plot Controls")
        self.popup_window.geometry("450x700")
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
        
        # Surface mode selection controls
        self._create_surface_mode_controls()
        
        # Parameter/axis selection controls
        self._create_axis_controls()
        
        # Dynamic mode-specific controls (initially shows individual controls)
        self._create_dynamic_mode_controls()
        
        # Visualization controls
        self._create_visualization_controls()
        
        # Plot style controls
        self._create_plot_style_controls()
        
        # Axis range controls
        self._create_axis_range_controls()
        
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
            text="3D Surface Plot Controls",
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
    
    def _create_surface_mode_controls(self) -> None:
        """
        Create surface mode selection controls.
        
        This is the primary control that determines which type of 3D surface to display.
        """
        # Surface mode selection section
        mode_section = tk.LabelFrame(
            self.scroll_frame,
            text="Surface Mode Selection",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        mode_section.pack(fill=tk.X, padx=5, pady=5)
        
        # Radio buttons for surface mode selection
        modes = [
            ("individual", "Individual Objective Surface", "Display surface for a single response"),
            ("weighted_sum", "Weighted-Sum (Scalarized) Surface", "Combine multiple responses with weights"),
            ("acquisition", "Acquisition Function Surface", "Show where algorithm will sample next")
        ]
        
        for mode_value, mode_text, mode_description in modes:
            mode_frame = tk.Frame(mode_section, bg=COLOR_SURFACE)
            mode_frame.pack(fill=tk.X, pady=2)
            
            # Radio button
            radio_btn = tk.Radiobutton(
                mode_frame,
                text=mode_text,
                variable=self.surface_mode_var,
                value=mode_value,
                command=self._on_surface_mode_changed,
                bg=COLOR_SURFACE,
                fg=COLOR_SECONDARY,
                font=("Arial", 9, "bold"),
                activebackground=COLOR_BACKGROUND,
                selectcolor=COLOR_SURFACE
            )
            radio_btn.pack(side=tk.LEFT, anchor="w")
            
            # Description label
            desc_label = tk.Label(
                mode_frame,
                text=f"({mode_description})",
                bg=COLOR_SURFACE,
                fg=COLOR_WARNING,
                font=("Arial", 8, "italic")
            )
            desc_label.pack(side=tk.LEFT, padx=(10, 0), anchor="w")
    
    def _create_axis_controls(self) -> None:
        """
        Create parameter selection controls for X and Y axes.
        
        These controls are common to all surface modes as they define the parameter space.
        """
        # Axis controls section
        axis_section = tk.LabelFrame(
            self.scroll_frame,
            text="Parameter Axis Configuration",
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
            text="X-Axis Parameter:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.param1_combo = ttk.Combobox(
            x_axis_frame,
            textvariable=self.param1_var,
            values=self.available_parameters,
            state="readonly",
            width=20
        )
        self.param1_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Y-axis parameter selection
        y_axis_frame = tk.Frame(axis_section, bg=COLOR_SURFACE)
        y_axis_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            y_axis_frame,
            text="Y-Axis Parameter:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.param2_combo = ttk.Combobox(
            y_axis_frame,
            textvariable=self.param2_var,
            values=self.available_parameters,
            state="readonly",
            width=20
        )
        self.param2_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_dynamic_mode_controls(self) -> None:
        """
        Create dynamic controls that change based on surface mode selection.
        
        Initially shows individual objective controls.
        """
        # Container for dynamic controls
        self.dynamic_controls_container = tk.Frame(self.scroll_frame, bg=COLOR_SURFACE)
        self.dynamic_controls_container.pack(fill=tk.X, padx=5, pady=5)
        
        # Create individual objective controls (default)
        self._create_individual_controls()
    
    def _create_individual_controls(self) -> None:
        """
        Create controls specific to individual objective surface mode.
        """
        # Clear any existing dynamic controls
        for widget in self.dynamic_controls_container.winfo_children():
            widget.destroy()
        
        # Individual objective controls section
        individual_section = tk.LabelFrame(
            self.dynamic_controls_container,
            text="Individual Objective Settings",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        individual_section.pack(fill=tk.X, pady=5)
        
        # Response selection
        response_frame = tk.Frame(individual_section, bg=COLOR_SURFACE)
        response_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            response_frame,
            text="Z-Axis Response:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.response_combo = ttk.Combobox(
            response_frame,
            textvariable=self.response_var,
            values=self.available_responses,
            state="readonly",
            width=20
        )
        self.response_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Store reference for mode switching
        self.individual_controls_frame = individual_section
    
    def _create_weighted_sum_controls(self) -> None:
        """
        Create controls specific to weighted-sum surface mode with global importance integration.
        """
        # Clear any existing dynamic controls
        for widget in self.dynamic_controls_container.winfo_children():
            widget.destroy()
        
        # Weighted-sum controls section
        weighted_section = tk.LabelFrame(
            self.dynamic_controls_container,
            text="Weighted-Sum (Scalarization) Settings",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        weighted_section.pack(fill=tk.X, pady=5)
        
        # Formula display
        formula_label = tk.Label(
            weighted_section,
            text="Surface: S(x) = w₁×μ₁(x) + w₂×μ₂(x) + w₃×μ₃(x) + ...",
            bg=COLOR_SURFACE,
            fg=COLOR_PRIMARY,
            font=("Arial", 9, "bold"),
            justify=tk.CENTER
        )
        formula_label.pack(pady=(0, 10))
        
        # Global weights option
        global_weights_frame = tk.Frame(weighted_section, bg=COLOR_SURFACE)
        global_weights_frame.pack(fill=tk.X, pady=5)
        
        use_global_check = tk.Checkbutton(
            global_weights_frame,
            text="Use Global Importance Weights (⭐ ratings)",
            variable=self.use_global_weights_var,
            command=self._on_global_weights_toggle,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9, "bold"),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        )
        use_global_check.pack(side=tk.LEFT)
        
        # Global weights status
        self.global_weights_status_label = tk.Label(
            global_weights_frame,
            text="",
            bg=COLOR_SURFACE,
            fg=COLOR_SUCCESS if self.global_importance_weights else COLOR_WARNING,
            font=("Arial", 8, "italic")
        )
        self.global_weights_status_label.pack(side=tk.LEFT, padx=(10, 0))
        self._update_global_weights_status()
        
        # Weight sliders container with scrolling
        sliders_container = tk.Frame(weighted_section, bg=COLOR_SURFACE)
        sliders_container.pack(fill=tk.X, pady=5)
        
        # Create scrollable frame for weight sliders
        canvas = tk.Canvas(sliders_container, bg=COLOR_SURFACE, height=150, highlightthickness=0)
        scrollbar = ttk.Scrollbar(sliders_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_SURFACE)
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create weight sliders for each response
        self.weight_vars = {}
        self.weight_sliders = {}
        
        for i, response_name in enumerate(self.available_responses):
            self._create_weight_slider(scrollable_frame, response_name, i)
        
        # Normalize weights button
        normalize_btn = tk.Button(
            weighted_section,
            text="⚖️ Normalize Weights",
            command=self._normalize_weights,
            bg=COLOR_PRIMARY,
            fg=COLOR_SURFACE,
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=15,
            pady=5
        )
        normalize_btn.pack(pady=(10, 0))
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Initialize weights
        self._initialize_weights()
        
        # Store reference for mode switching
        self.weighted_sum_controls_frame = weighted_section
    
    def _create_acquisition_controls(self) -> None:
        """
        Set up acquisition function mode with no additional controls.
        Uses qNEHVI acquisition function automatically.
        """
        # Clear any existing dynamic controls
        for widget in self.dynamic_controls_container.winfo_children():
            widget.destroy()
        
        # Set acquisition type to qNEHVI (stored for compatibility)
        self.acquisition_type_var = tk.StringVar(value="qNEHVI")
    
    def _create_weight_slider(self, parent: tk.Widget, response_name: str, row_index: int) -> None:
        """Create a weight slider for a single response."""
        # Row frame with alternating background
        row_frame = tk.Frame(
            parent, 
            bg=COLOR_BACKGROUND if row_index % 2 == 0 else COLOR_SURFACE,
            relief="flat",
            bd=1
        )
        row_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Response info frame
        info_frame = tk.Frame(row_frame, bg=row_frame['bg'])
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Response name and goal
        response_config = self.responses_config.get(response_name, {})
        goal = response_config.get('goal', 'Unknown')
        
        name_label = tk.Label(
            info_frame,
            text=f"{response_name}",
            bg=row_frame['bg'],
            fg=COLOR_SECONDARY,
            font=("Arial", 9, "bold"),
            width=12,
            anchor="w"
        )
        name_label.pack(side=tk.LEFT)
        
        goal_label = tk.Label(
            info_frame,
            text=f"({goal})",
            bg=row_frame['bg'],
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic"),
            width=10,
            anchor="w"
        )
        goal_label.pack(side=tk.LEFT, padx=(5, 10))
        
        # Weight variable
        weight_var = tk.DoubleVar(value=1.0 / len(self.available_responses))  # Default equal weights
        self.weight_vars[response_name] = weight_var
        
        # Weight slider
        weight_slider = tk.Scale(
            info_frame,
            from_=0.0, to=1.0,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=weight_var,
            bg=row_frame['bg'],
            fg=COLOR_SECONDARY,
            font=("Arial", 8),
            length=120,
            command=lambda val, name=response_name: self._on_weight_changed(name, val)
        )
        weight_slider.pack(side=tk.LEFT, padx=(0, 10))
        
        # Weight value display
        weight_value_label = tk.Label(
            info_frame,
            text="0.33",
            bg=row_frame['bg'],
            fg=COLOR_PRIMARY,
            font=("Arial", 8, "bold"),
            width=5,
            anchor="e"
        )
        weight_value_label.pack(side=tk.RIGHT)
        
        # Store references
        self.weight_sliders[response_name] = {
            'slider': weight_slider,
            'value_label': weight_value_label,
            'var': weight_var
        }
    
    def _update_global_weights_status(self) -> None:
        """Update the global weights status display."""
        if not hasattr(self, 'global_weights_status_label'):
            return
            
        if self.global_importance_weights:
            status_text = f"Available ({len(self.global_importance_weights)} responses)"
            self.global_weights_status_label.config(text=status_text, fg=COLOR_SUCCESS)
        else:
            status_text = "No global weights set"
            self.global_weights_status_label.config(text=status_text, fg=COLOR_WARNING)
    
    def _on_global_weights_toggle(self) -> None:
        """Handle toggle of global weights usage."""
        use_global = self.use_global_weights_var.get()
        
        if use_global and self.global_importance_weights:
            # Apply global importance weights
            for response_name, weight in self.global_importance_weights.items():
                if response_name in self.weight_vars:
                    self.weight_vars[response_name].set(weight)
                    self._update_weight_display(response_name)
        else:
            # Reset to equal weights
            equal_weight = 1.0 / len(self.available_responses) if self.available_responses else 0.0
            for response_name in self.weight_vars:
                self.weight_vars[response_name].set(equal_weight)
                self._update_weight_display(response_name)
        
        # Enable/disable sliders based on global weights usage
        state = tk.DISABLED if use_global else tk.NORMAL
        for response_name, slider_info in self.weight_sliders.items():
            slider_info['slider'].config(state=state)
    
    def _on_weight_changed(self, response_name: str, value: str) -> None:
        """Handle weight slider change."""
        self._update_weight_display(response_name)
    
    def _update_weight_display(self, response_name: str) -> None:
        """Update the weight value display for a response."""
        if response_name in self.weight_sliders:
            weight_value = self.weight_vars[response_name].get()
            self.weight_sliders[response_name]['value_label'].config(text=f"{weight_value:.2f}")
    
    def _initialize_weights(self) -> None:
        """Initialize weights based on global importance or equal distribution."""
        if self.use_global_weights_var.get() and self.global_importance_weights:
            # Use global importance weights
            for response_name, weight in self.global_importance_weights.items():
                if response_name in self.weight_vars:
                    self.weight_vars[response_name].set(weight)
        else:
            # Use equal weights
            equal_weight = 1.0 / len(self.available_responses) if self.available_responses else 0.0
            for response_name in self.weight_vars:
                self.weight_vars[response_name].set(equal_weight)
        
        # Update displays
        for response_name in self.weight_vars:
            self._update_weight_display(response_name)
    
    def _normalize_weights(self) -> None:
        """Normalize all weights to sum to 1.0."""
        total_weight = sum(var.get() for var in self.weight_vars.values())
        
        if total_weight > 0:
            for response_name, weight_var in self.weight_vars.items():
                normalized_weight = weight_var.get() / total_weight
                weight_var.set(normalized_weight)
                self._update_weight_display(response_name)
        else:
            # If all weights are 0, set equal weights
            equal_weight = 1.0 / len(self.weight_vars) if self.weight_vars else 0.0
            for response_name, weight_var in self.weight_vars.items():
                weight_var.set(equal_weight)
                self._update_weight_display(response_name)
    
    def _on_surface_mode_changed(self) -> None:
        """
        Handle surface mode selection changes.
        
        This method updates the dynamic controls based on the selected surface mode.
        """
        mode = self.surface_mode_var.get()
        logger.debug(f"Surface mode changed to: {mode}")
        
        if mode == "individual":
            self._create_individual_controls()
        elif mode == "weighted_sum":
            self._create_weighted_sum_controls()
        elif mode == "acquisition":
            self._create_acquisition_controls()
        
        # Update scroll region
        self.scroll_frame.update_idletasks()
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
    
    def _create_visualization_controls(self) -> None:
        """
        Create visualization option controls.
        """
        # Visualization controls section
        viz_section = tk.LabelFrame(
            self.scroll_frame,
            text="Visualization Options",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        viz_section.pack(fill=tk.X, padx=5, pady=5)
        
        # Surface visibility
        surface_frame = tk.Frame(viz_section, bg=COLOR_SURFACE)
        surface_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            surface_frame,
            text="Show Surface",
            variable=self.series_visibility['show_surface'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        # Uncertainty visualization
        uncertainty_frame = tk.Frame(viz_section, bg=COLOR_SURFACE)
        uncertainty_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            uncertainty_frame,
            text="Show Uncertainty Bands",
            variable=self.series_visibility['show_uncertainty'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        tk.Label(
            uncertainty_frame,
            text="(GP prediction uncertainty)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Contour projections
        contours_frame = tk.Frame(viz_section, bg=COLOR_SURFACE)
        contours_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            contours_frame,
            text="Show Contour Projections",
            variable=self.series_visibility['show_contours'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        # Experimental data points
        data_points_frame = tk.Frame(viz_section, bg=COLOR_SURFACE)
        data_points_frame.pack(fill=tk.X, pady=2)
        
        tk.Checkbutton(
            data_points_frame,
            text="Show Experimental Data Points",
            variable=self.series_visibility['show_data_points'],
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        ).pack(side=tk.LEFT)
        
        # Legend
        legend_frame = tk.Frame(viz_section, bg=COLOR_SURFACE)
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
    
    def _create_plot_style_controls(self) -> None:
        """
        Create enhanced plot style and appearance controls.
        """
        # Plot style section
        style_section = tk.LabelFrame(
            self.scroll_frame,
            text="Plot Style & Appearance",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        style_section.pack(fill=tk.X, padx=5, pady=5)
        
        # Style selection
        style_frame = tk.Frame(style_section, bg=COLOR_SURFACE)
        style_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            style_frame,
            text="Surface Style:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        style_options = ["surface", "wireframe", "contour", "surface+contour"]
        self.style_combo = ttk.Combobox(
            style_frame,
            textvariable=self.plot_style_var,
            values=style_options,
            state="readonly",
            width=15
        )
        self.style_combo.pack(side=tk.LEFT)
        
        # Color palette selection
        palette_frame = tk.Frame(style_section, bg=COLOR_SURFACE)
        palette_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            palette_frame,
            text="Color Palette:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        palette_options = [
            "viridis", "plasma", "inferno", "magma", "cividis",
            "coolwarm", "RdYlBu", "RdBu", "seismic", "jet",
            "rainbow", "hot", "cool", "spring", "summer", "autumn", "winter"
        ]
        
        self.palette_combo = ttk.Combobox(
            palette_frame,
            textvariable=self.color_palette_var,
            values=palette_options,
            state="readonly",
            width=15
        )
        self.palette_combo.pack(side=tk.LEFT)
        
        # Color palette description
        palette_descriptions = {
            "viridis": "Perceptually uniform (recommended)",
            "plasma": "High contrast purple-pink-yellow",
            "inferno": "Dark red-orange-yellow",
            "magma": "Dark purple-red-yellow",
            "cividis": "Colorblind-friendly",
            "coolwarm": "Blue-white-red diverging",
            "RdYlBu": "Red-yellow-blue diverging",
            "RdBu": "Red-blue diverging",
            "seismic": "Red-white-blue seismic",
            "jet": "Rainbow (not recommended)",
            "rainbow": "Full spectrum",
            "hot": "Black-red-yellow-white",
            "cool": "Cyan-magenta",
            "spring": "Magenta-yellow",
            "summer": "Green-yellow",
            "autumn": "Red-orange-yellow",
            "winter": "Blue-green"
        }
        
        self.palette_desc_label = tk.Label(
            style_section,
            text=palette_descriptions.get("viridis", ""),
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic"),
            justify=tk.CENTER
        )
        self.palette_desc_label.pack(pady=2)
        
        # Update description when palette changes
        def update_palette_description(*args):
            selected = self.color_palette_var.get()
            desc = palette_descriptions.get(selected, "")
            self.palette_desc_label.config(text=desc)
        
        self.color_palette_var.trace('w', update_palette_description)
        
        # Resolution control
        resolution_frame = tk.Frame(style_section, bg=COLOR_SURFACE)
        resolution_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            resolution_frame,
            text="Resolution:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        resolution_scale = tk.Scale(
            resolution_frame,
            from_=20, to=200,
            orient=tk.HORIZONTAL,
            variable=self.resolution_var,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 8),
            length=150
        )
        resolution_scale.pack(side=tk.LEFT)
        
        tk.Label(
            resolution_frame,
            text="grid points",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Resolution info
        resolution_info_label = tk.Label(
            style_section,
            text="Higher resolution provides smoother surfaces but takes longer to render",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic"),
            justify=tk.CENTER
        )
        resolution_info_label.pack(pady=2)
    
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
        self._create_single_axis_range_controls(range_section, "X", self.x_auto_var, 
                                               self.x_min_var, self.x_max_var, "_toggle_x_range_controls")
        
        # Y-axis range controls  
        self._create_single_axis_range_controls(range_section, "Y", self.y_auto_var,
                                               self.y_min_var, self.y_max_var, "_toggle_y_range_controls")
        
        # Z-axis range controls
        self._create_single_axis_range_controls(range_section, "Z", self.z_auto_var,
                                               self.z_min_var, self.z_max_var, "_toggle_z_range_controls")
    
    def _create_single_axis_range_controls(self, parent, axis_name, auto_var, min_var, max_var, toggle_method_name):
        """Create range controls for a single axis."""
        axis_frame = tk.Frame(parent, bg=COLOR_SURFACE)
        axis_frame.pack(fill=tk.X, pady=2)
        
        # Auto checkbox
        auto_check = tk.Checkbutton(
            axis_frame,
            text=f"{axis_name}-Axis Auto",
            variable=auto_var,
            command=getattr(self, toggle_method_name),
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9),
            activebackground=COLOR_BACKGROUND,
            selectcolor=COLOR_SURFACE
        )
        auto_check.pack(side=tk.LEFT)
        
        # Min entry
        tk.Label(axis_frame, text="Min:", bg=COLOR_SURFACE, fg=COLOR_SECONDARY, 
                font=("Arial", 8)).pack(side=tk.LEFT, padx=(20, 5))
        min_entry = tk.Entry(axis_frame, textvariable=min_var, width=8, font=("Arial", 8))
        min_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Max entry
        tk.Label(axis_frame, text="Max:", bg=COLOR_SURFACE, fg=COLOR_SECONDARY,
                font=("Arial", 8)).pack(side=tk.LEFT, padx=(0, 5))
        max_entry = tk.Entry(axis_frame, textvariable=max_var, width=8, font=("Arial", 8))
        max_entry.pack(side=tk.LEFT)
        
        # Store entry widgets for enable/disable
        setattr(self, f"{axis_name.lower()}_min_entry", min_entry)
        setattr(self, f"{axis_name.lower()}_max_entry", max_entry)
        
        # Initial state
        getattr(self, toggle_method_name)()
    
    def _toggle_x_range_controls(self):
        """Toggle X-axis range entry fields based on auto setting."""
        if hasattr(self, 'x_min_entry') and hasattr(self, 'x_max_entry'):
            state = tk.DISABLED if self.x_auto_var.get() else tk.NORMAL
            self.x_min_entry.config(state=state)
            self.x_max_entry.config(state=state)
    
    def _toggle_y_range_controls(self):
        """Toggle Y-axis range entry fields based on auto setting."""
        if hasattr(self, 'y_min_entry') and hasattr(self, 'y_max_entry'):
            state = tk.DISABLED if self.y_auto_var.get() else tk.NORMAL
            self.y_min_entry.config(state=state)
            self.y_max_entry.config(state=state)
    
    def _toggle_z_range_controls(self):
        """Toggle Z-axis range entry fields based on auto setting."""
        if hasattr(self, 'z_min_entry') and hasattr(self, 'z_max_entry'):
            state = tk.DISABLED if self.z_auto_var.get() else tk.NORMAL
            self.z_min_entry.config(state=state)
            self.z_max_entry.config(state=state)
    
    def _create_export_controls(self) -> None:
        """
        Create enhanced export controls for high-quality plot export.
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
        
        # Export DPI selection
        dpi_frame = tk.Frame(export_section, bg=COLOR_SURFACE)
        dpi_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            dpi_frame,
            text="Export DPI:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        dpi_values = [150, 300, 600, 1200, 2400]
        self.dpi_combo = ttk.Combobox(
            dpi_frame,
            textvariable=self.dpi_var,
            values=dpi_values,
            state="readonly",
            width=10
        )
        self.dpi_combo.pack(side=tk.LEFT)
        
        dpi_info_label = tk.Label(
            dpi_frame,
            text="(higher = better quality)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        )
        dpi_info_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Export resolution control
        export_res_frame = tk.Frame(export_section, bg=COLOR_SURFACE)
        export_res_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            export_res_frame,
            text="Export Resolution:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_resolution_var = tk.IntVar(value=100)
        export_res_scale = tk.Scale(
            export_res_frame,
            from_=50, to=300,
            orient=tk.HORIZONTAL,
            variable=self.export_resolution_var,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 8),
            length=120
        )
        export_res_scale.pack(side=tk.LEFT)
        
        tk.Label(
            export_res_frame,
            text="grid points",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        )
        export_res_label = tk.Label(
            export_res_frame,
            text="grid points (separate from display)",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic")
        )
        export_res_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Export format selection
        format_frame = tk.Frame(export_section, bg=COLOR_SURFACE)
        format_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            format_frame,
            text="Export Format:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_format_var = tk.StringVar(value="PNG")
        format_options = ["PNG", "PDF", "SVG", "JPEG", "EPS"]
        self.format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.export_format_var,
            values=format_options,
            state="readonly",
            width=10
        )
        self.format_combo.pack(side=tk.LEFT)
        
        # Export info
        export_info_label = tk.Label(
            export_section,
            text="Export resolution is independent of display resolution for optimal quality",
            bg=COLOR_SURFACE,
            fg=COLOR_WARNING,
            font=("Arial", 8, "italic"),
            justify=tk.CENTER
        )
        export_info_label.pack(pady=5)
        
        # Export button
        export_btn = tk.Button(
            export_section,
            text="📊 Export High-Quality Plot",
            command=self._export_plot,
            bg=COLOR_SUCCESS,
            fg=COLOR_SURFACE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=25,
            pady=8
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
        # Note: We don't auto-update to match GP Slice controls pattern
        # Users must click "Refresh Plot" to update the plot
        pass
    
    def _refresh_plot(self) -> None:
        """
        Handle the Refresh Plot button click to update the plot with current settings.
        
        This method is called when the user clicks the "Refresh Plot" button and
        triggers the plot update with all current control panel settings.
        """
        logger.info("Refreshing 3D surface plot with current settings")
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
            title="Export 3D Surface Plot",
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
                logger.info("Triggering 3D surface plot update")
                self.update_callback()
            except Exception as e:
                logger.error(f"Error calling plot update callback: {e}")
        else:
            logger.warning("No update callback registered for 3D surface plot")
    
    def _reset_to_defaults(self) -> None:
        """
        Reset all controls to their default values.
        
        This method restores the control panel to its initial state, including
        default mode, parameter/response selections and visualization settings.
        """
        # Reset surface mode to individual
        self.surface_mode_var.set("individual")
        self._on_surface_mode_changed()
        
        # Reset parameter selections to defaults
        if len(self.available_parameters) >= 2:
            self.param1_var.set(self.available_parameters[0])
            self.param2_var.set(self.available_parameters[1])
        
        # Reset response selection
        if self.available_responses:
            self.response_var.set(self.available_responses[0])
        
        # Reset visualization controls to defaults
        self.series_visibility['show_surface'].set(True)
        self.series_visibility['show_uncertainty'].set(False)
        self.series_visibility['show_contours'].set(True)
        self.series_visibility['show_data_points'].set(True)
        self.series_visibility['show_legend'].set(True)
        
        # Reset plot style
        self.plot_style_var.set("surface")
        
        # Reset color palette
        self.color_palette_var.set("viridis")
        
        # Reset resolution
        self.resolution_var.set(60)
        
        # Reset DPI to default
        self.dpi_var.set(300)
        
        # Reset export settings
        if hasattr(self, 'export_resolution_var'):
            self.export_resolution_var.set(100)
        if hasattr(self, 'export_format_var'):
            self.export_format_var.set("PNG")
        
        # Reset acquisition function settings (qNEHVI is set automatically in acquisition mode)
        if hasattr(self, 'acquisition_type_var'):
            self.acquisition_type_var.set("qNEHVI")
        
        # Reset axis ranges to auto
        self.x_auto_var.set(True)
        self.y_auto_var.set(True)
        self.z_auto_var.set(True)
        self.x_min_var.set("")
        self.x_max_var.set("")
        self.y_min_var.set("")
        self.y_max_var.set("")
        self.z_min_var.set("")
        self.z_max_var.set("")
        
        # Update control states
        if hasattr(self, '_toggle_x_range_controls'):
            self._toggle_x_range_controls()
        if hasattr(self, '_toggle_y_range_controls'):
            self._toggle_y_range_controls()
        if hasattr(self, '_toggle_z_range_controls'):
            self._toggle_z_range_controls()
        
        logger.info("3D surface plot controls reset to defaults")
        # Don't auto-refresh, user must click refresh button
    
    def get_display_options(self) -> Dict[str, Any]:
        """
        Get current display options for integration with the plotting system.
        
        This method returns a dictionary containing all current control settings
        in a format expected by the PyMBO plotting system. It serves as the
        primary interface between the control panel and the plot generation logic.
        
        Returns:
            Dict[str, Any]: Dictionary containing current display options including:
                - surface_mode: Selected surface mode ("individual", "weighted_sum", "acquisition")
                - param1_name: X-axis parameter name
                - param2_name: Y-axis parameter name
                - response_name: Response name (for individual mode)
                - acquisition_type: Acquisition function type (for acquisition mode)
                - plot_style: Surface plot style
                - resolution: Grid resolution
                - show_* options: Various visibility toggles
                - export_dpi: DPI setting for plot export
        """
        options = {
            'surface_mode': self.surface_mode_var.get(),
            'param1_name': self.param1_var.get(),
            'param2_name': self.param2_var.get(),
            'response_name': self.response_var.get(),
            'plot_style': self.plot_style_var.get(),
            'color_palette': self.color_palette_var.get(),
            'resolution': self.resolution_var.get(),
            'show_surface': self.series_visibility['show_surface'].get(),
            'show_uncertainty': self.series_visibility['show_uncertainty'].get(),
            'show_contours': self.series_visibility['show_contours'].get(),
            'show_data_points': self.series_visibility['show_data_points'].get(),
            'show_legend': self.series_visibility['show_legend'].get(),
            'export_dpi': self.dpi_var.get(),
            'export_resolution': getattr(self, 'export_resolution_var', tk.IntVar(value=100)).get(),
            'export_format': getattr(self, 'export_format_var', tk.StringVar(value='PNG')).get()
        }
        
        # Add acquisition type for acquisition mode (always qNEHVI)
        if self.surface_mode_var.get() == 'acquisition':
            options['acquisition_type'] = 'qNEHVI'
        else:
            options['acquisition_type'] = 'EHVI'  # Fallback for other modes
        
        # Add exploration parameter for acquisition functions (not needed for qNEHVI)
        options['exploration_factor'] = 2.0  # Default value for compatibility
        
        # Add weight information for weighted-sum mode
        if self.surface_mode_var.get() == 'weighted_sum':
            options['use_global_weights'] = self.use_global_weights_var.get()
            options['response_weights'] = {
                name: var.get() for name, var in self.weight_vars.items()
            }
            options['global_importance_weights'] = self.global_importance_weights
        
        logger.debug(f"Current display options: {options}")
        return options
    
    def get_axis_ranges(self) -> Dict[str, Tuple]:
        """
        Get current axis range settings for integration with the plotting system.
        
        Returns:
            Dict[str, Tuple]: Dictionary containing axis ranges where each value is a tuple of
                (min_value, max_value, is_auto) for x_axis, y_axis, and z_axis
        """
        def _parse_range_value(value_str: str):
            """Parse range value string to float or None."""
            if not value_str.strip():
                return None
            try:
                return float(value_str)
            except ValueError:
                return None
        
        ranges = {
            'x_range': (
                _parse_range_value(self.x_min_var.get()),
                _parse_range_value(self.x_max_var.get()),
                self.x_auto_var.get()
            ),
            'y_range': (
                _parse_range_value(self.y_min_var.get()),
                _parse_range_value(self.y_max_var.get()),
                self.y_auto_var.get()
            ),
            'z_range': (
                _parse_range_value(self.z_min_var.get()),
                _parse_range_value(self.z_max_var.get()),
                self.z_auto_var.get()
            )
        }
        
        logger.debug(f"Current axis ranges: {ranges}")
        return ranges
    
    def update_available_options(self, new_parameters: List[str], new_responses: List[str]) -> None:
        """
        Update the available parameters and responses for selection.
        
        This method allows dynamic updating of the option lists when new data
        becomes available or when the optimization configuration changes.
        
        Args:
            new_parameters: List of new parameter names to make available
            new_responses: List of new response names to make available
        """
        self.available_parameters = new_parameters
        self.available_responses = new_responses
        
        # Update combobox values
        if hasattr(self, 'param1_combo'):
            self.param1_combo['values'] = new_parameters
        if hasattr(self, 'param2_combo'):
            self.param2_combo['values'] = new_parameters
        if hasattr(self, 'response_combo'):
            self.response_combo['values'] = new_responses
        
        # Update selections if current ones are no longer valid
        if self.param1_var.get() not in new_parameters and new_parameters:
            self.param1_var.set(new_parameters[0])
        if self.param2_var.get() not in new_parameters and len(new_parameters) > 1:
            self.param2_var.set(new_parameters[1])
        if self.response_var.get() not in new_responses and new_responses:
            self.response_var.set(new_responses[0])
        
        logger.info(f"Updated available options: {len(new_parameters)} parameters, {len(new_responses)} responses")
    
    def show(self) -> None:
        """Show the popout control panel window."""
        if self.popup_window:
            self.popup_window.deiconify()  # Show the window
            self.popup_window.lift()  # Bring to front
            self.popup_window.focus_set()  # Give focus
        logger.info("3D surface plot control panel window shown")
    
    def hide(self) -> None:
        """Hide the popout control panel window."""
        if self.popup_window:
            self.popup_window.withdraw()  # Hide the window
        logger.info("3D surface plot control panel window hidden")
    
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
    
    def update_global_importance_weights(self, global_weights: Dict[str, float]) -> None:
        """
        Update the global importance weights and refresh the weighted-sum controls.
        
        Args:
            global_weights: Dictionary mapping response names to importance weights
        """
        self.global_importance_weights = global_weights or {}
        
        # Update status display if in weighted-sum mode
        if hasattr(self, 'global_weights_status_label'):
            self._update_global_weights_status()
        
        # If currently using global weights and in weighted-sum mode, update sliders
        if (self.surface_mode_var.get() == 'weighted_sum' and 
            self.use_global_weights_var.get() and 
            self.global_importance_weights):
            
            for response_name, weight in self.global_importance_weights.items():
                if response_name in self.weight_vars:
                    self.weight_vars[response_name].set(weight)
                    self._update_weight_display(response_name)
        
        logger.info(f"Updated global importance weights: {len(self.global_importance_weights)} responses")


def create_3d_surface_control_panel(parent: tk.Widget, plot_type: str,
                                   params_config: Dict[str, Any] = None,
                                   responses_config: Dict[str, Any] = None,
                                   update_callback: Callable = None,
                                   export_callback: Callable = None,
                                   global_importance_weights: Dict[str, float] = None) -> SurfacePlotControlPanel:
    """
    Factory function for creating enhanced 3D surface plot control panels in popout windows.
    
    This function serves as the primary entry point for instantiating 3D surface plot
    control panels. It creates a separate popup window with comprehensive controls
    for 3D surface plot customization including multiple surface modes.
    
    Args:
        parent: Parent Tkinter widget for the control panel
        plot_type: Type identifier for the plot (should be "3d_surface")
        params_config: Dictionary containing parameter configurations
        responses_config: Dictionary containing response configurations
        update_callback: Function to call when plot updates are needed
        export_callback: Function to call for plot export (filename, dpi) -> None
    
    Returns:
        SurfacePlotControlPanel: Initialized control panel instance in popup window
    
    Raises:
        Exception: If control panel creation fails
    
    Example:
        >>> control_panel = create_3d_surface_control_panel(
        ...     parent=main_window,
        ...     plot_type="3d_surface",
        ...     params_config=param_dict,
        ...     responses_config=response_dict,
        ...     update_callback=update_plot_function,
        ...     export_callback=export_plot_function
        ... )
    """
    try:
        logger.info(f"Creating enhanced 3D surface control panel for plot type: {plot_type}")
        
        control_panel = SurfacePlotControlPanel(
            parent=parent,
            plot_type=plot_type,
            params_config=params_config,
            responses_config=responses_config,
            update_callback=update_callback,
            global_importance_weights=global_importance_weights
        )
        
        # Set export callback if provided
        if export_callback:
            control_panel.set_export_callback(export_callback)
        
        logger.info("Enhanced 3D surface control panel created successfully in popup window")
        return control_panel
        
    except Exception as e:
        logger.error(f"Failed to create 3D surface control panel: {e}")
        raise