"""
Movable Controls Module
Movable implementation of plot control panels that can be dragged around the interface
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class MovablePlotControlPanel:
    """Movable plot control panel that can be dragged around the interface"""
    
    def __init__(self, parent, plot_type: str, params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.control_frame = None
        self.axis_ranges = {}
        
        # Variables for dragging
        self.start_x = 0
        self.start_y = 0
        
        # Initialize default axis ranges
        self.axis_ranges = {
            'x_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'x_max': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_max': {'var': tk.StringVar(value='auto'), 'auto': True}
        }
        
        self.create_controls()
        logger.info(f"Movable plot control panel created for {plot_type}")
    
    def create_controls(self):
        """Create the movable control panel"""
        # Main control frame with border
        self.control_frame = tk.Frame(self.parent, bg='lightsteelblue', relief='raised', bd=2)
        
        # Title bar (draggable)
        self.title_frame = tk.Frame(self.control_frame, bg='steelblue', cursor='fleur')
        self.title_frame.pack(fill=tk.X)
        
        # Bind drag events to title frame
        self.title_frame.bind('<Button-1>', self.start_drag)
        self.title_frame.bind('<B1-Motion>', self.do_drag)
        
        title_label = tk.Label(self.title_frame, text=f"📊 {self.plot_type.replace('_', ' ').title()}", 
                              bg='steelblue', fg='white', font=('Arial', 8, 'bold'))
        title_label.pack(side=tk.LEFT, padx=5, pady=2)
        title_label.bind('<Button-1>', self.start_drag)
        title_label.bind('<B1-Motion>', self.do_drag)
        
        # Close button
        close_btn = tk.Button(self.title_frame, text='×', command=self.hide, 
                             bg='steelblue', fg='white', bd=0, font=('Arial', 8))
        close_btn.pack(side=tk.RIGHT, padx=2)
        
        # Content frame
        content_frame = tk.Frame(self.control_frame, bg='lightsteelblue')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Axis controls
        self._create_movable_axis_controls(content_frame)
        
        # Action buttons
        self._create_movable_buttons(content_frame)
    
    def _create_movable_axis_controls(self, parent):
        """Create axis range controls for movable panel"""
        # Axis controls frame
        axis_frame = tk.LabelFrame(parent, text="Axis Ranges", bg='lightsteelblue', 
                                  font=('Arial', 7))
        axis_frame.pack(fill=tk.X, pady=2)
        
        # X-axis controls
        x_frame = tk.Frame(axis_frame, bg='lightsteelblue')
        x_frame.pack(fill=tk.X, padx=3, pady=1)
        
        tk.Label(x_frame, text="X:", bg='lightsteelblue', font=('Arial', 7)).pack(side=tk.LEFT)
        x_min_entry = tk.Entry(x_frame, textvariable=self.axis_ranges['x_min']['var'], 
                              width=8, font=('Arial', 7))
        x_min_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(x_frame, text="to", bg='lightsteelblue', font=('Arial', 7)).pack(side=tk.LEFT)
        x_max_entry = tk.Entry(x_frame, textvariable=self.axis_ranges['x_max']['var'], 
                              width=8, font=('Arial', 7))
        x_max_entry.pack(side=tk.LEFT, padx=2)
        
        # Y-axis controls
        y_frame = tk.Frame(axis_frame, bg='lightsteelblue')
        y_frame.pack(fill=tk.X, padx=3, pady=1)
        
        tk.Label(y_frame, text="Y:", bg='lightsteelblue', font=('Arial', 7)).pack(side=tk.LEFT)
        y_min_entry = tk.Entry(y_frame, textvariable=self.axis_ranges['y_min']['var'], 
                              width=8, font=('Arial', 7))
        y_min_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(y_frame, text="to", bg='lightsteelblue', font=('Arial', 7)).pack(side=tk.LEFT)
        y_max_entry = tk.Entry(y_frame, textvariable=self.axis_ranges['y_max']['var'], 
                              width=8, font=('Arial', 7))
        y_max_entry.pack(side=tk.LEFT, padx=2)
    
    def _create_movable_buttons(self, parent):
        """Create action buttons for movable panel"""
        button_frame = tk.Frame(parent, bg='lightsteelblue')
        button_frame.pack(fill=tk.X, pady=3)
        
        auto_btn = tk.Button(button_frame, text="Auto Scale", command=self._auto_scale,
                            font=('Arial', 7), width=10)
        auto_btn.pack(side=tk.LEFT, padx=2)
        
        refresh_btn = tk.Button(button_frame, text="Refresh", command=self._refresh_plot,
                               font=('Arial', 7), width=8)
        refresh_btn.pack(side=tk.RIGHT, padx=2)
    
    def start_drag(self, event):
        """Start dragging the panel"""
        self.start_x = event.x
        self.start_y = event.y
    
    def do_drag(self, event):
        """Handle dragging the panel"""
        if self.control_frame:
            x = self.control_frame.winfo_x() + (event.x - self.start_x)
            y = self.control_frame.winfo_y() + (event.y - self.start_y)
            self.control_frame.place(x=x, y=y)
    
    def _auto_scale(self):
        """Reset axis ranges to auto"""
        for axis in self.axis_ranges:
            self.axis_ranges[axis]['var'].set('auto')
            self.axis_ranges[axis]['auto'] = True
        logger.info(f"Auto scale applied for {self.plot_type}")
    
    def _refresh_plot(self):
        """Refresh the plot with current settings"""
        logger.info(f"Plot refresh requested for {self.plot_type}")
        if self.update_callback:
            try:
                self.update_callback()
                logger.info(f"Update callback executed for {self.plot_type}")
            except Exception as e:
                logger.error(f"Error calling update callback for {self.plot_type}: {e}")
    
    def show(self):
        """Show the movable control panel"""
        if self.control_frame:
            self.control_frame.place(x=50, y=50, width=200, height=120)
        logger.info(f"Movable control panel shown for {self.plot_type}")
    
    def hide(self):
        """Hide the movable control panel"""
        if self.control_frame:
            self.control_frame.place_forget()
        logger.info(f"Movable control panel hidden for {self.plot_type}")
    
    def place(self, **kwargs):
        """Place the control frame"""
        if self.control_frame:
            self.control_frame.place(**kwargs)
    
    def get_axis_ranges(self):
        """Get current axis range settings"""
        ranges = {}
        
        # Collect min/max values for each axis
        x_min_val, x_max_val, x_auto = self._get_axis_value('x_min')
        y_min_val, y_max_val, y_auto = self._get_axis_value('y_min')
        
        # Format for main GUI expectation: (min_val, max_val, is_auto)
        ranges['x_axis'] = (x_min_val, x_max_val, x_auto)
        ranges['y_axis'] = (y_min_val, y_max_val, y_auto)
        
        return ranges
    
    def _get_axis_value(self, axis_key):
        """Helper to get axis values and determine if auto"""
        if axis_key.endswith('_min'):
            base_axis = axis_key[:-4]  # Remove '_min'
            min_value = self.axis_ranges[f'{base_axis}_min']['var'].get()
            max_value = self.axis_ranges[f'{base_axis}_max']['var'].get()
            
            min_auto = min_value.lower() == 'auto'
            max_auto = max_value.lower() == 'auto'
            is_auto = min_auto or max_auto
            
            try:
                min_val = None if min_auto else float(min_value)
                max_val = None if max_auto else float(max_value)
            except ValueError:
                min_val = max_val = None
                is_auto = True
                
            return min_val, max_val, is_auto
        return None, None, True


def create_movable_plot_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                     responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> MovablePlotControlPanel:
    """Factory function to create a movable plot control panel"""
    try:
        # For complex plots like 3D Surface and GP Uncertainty, redirect to window controls
        # since movable controls would be too cramped for all the options
        if plot_type == 'surface_3d' or '3d' in plot_type.lower() or 'surface' in plot_type.lower():
            try:
                from .surface_3d_controls import create_surface_3d_control_panel
                logger.info(f"Using specialized 3D Surface controls instead of movable for {plot_type}")
                return create_surface_3d_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("3D Surface controls not available, using standard movable controls")
        
        elif plot_type == 'gp_uncertainty' or 'uncertainty' in plot_type.lower():
            try:
                from .gp_uncertainty_controls import create_gp_uncertainty_control_panel
                logger.info(f"Using specialized GP Uncertainty controls instead of movable for {plot_type}")
                return create_gp_uncertainty_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("GP Uncertainty controls not available, using standard movable controls")
        
        elif plot_type == 'sensitivity_analysis' or 'sensitivity' in plot_type.lower():
            try:
                from .sensitivity_analysis_controls import create_sensitivity_analysis_control_panel
                logger.info(f"Using specialized Sensitivity Analysis controls instead of movable for {plot_type}")
                return create_sensitivity_analysis_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("Sensitivity Analysis controls not available, using standard movable controls")
        
        # Default to standard movable controls for other plot types
        control_panel = MovablePlotControlPanel(parent, plot_type, params_config, responses_config, update_callback)
        logger.info(f"Created movable plot control panel for {plot_type}")
        return control_panel
    except Exception as e:
        logger.error(f"Error creating movable plot control panel for {plot_type}: {e}")
        raise