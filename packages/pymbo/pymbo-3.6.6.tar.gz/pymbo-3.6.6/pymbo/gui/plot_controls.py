"""
Plot Controls Module
Basic implementation of plot control panels for the GUI
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


class EnhancedPlotControlPanel:
    """Basic implementation of enhanced plot control panel"""
    
    def __init__(self, parent, plot_type: str, params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.window = None
        self.axis_ranges = {}
        
        # Initialize default axis ranges
        self.axis_ranges = {
            'x_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'x_max': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_max': {'var': tk.StringVar(value='auto'), 'auto': True}
        }
        
        logger.info(f"Enhanced plot control panel created for {plot_type}")
    
    def create_window(self):
        """Create the control panel window"""
        if self.window is not None:
            self.show()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"{self.plot_type.replace('_', ' ').title()} Controls")
        self.window.geometry("300x400")
        
        # Create main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"{self.plot_type.replace('_', ' ').title()} Controls", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Axis range controls
        self._create_axis_controls(main_frame)
        
        # Plot options
        self._create_plot_options(main_frame)
        
        # Action buttons
        self._create_action_buttons(main_frame)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        logger.info(f"Control window created for {self.plot_type}")
    
    def _create_axis_controls(self, parent):
        """Create axis range control widgets"""
        axis_frame = ttk.LabelFrame(parent, text="Axis Ranges")
        axis_frame.pack(fill=tk.X, pady=(0, 10))
        
        # X-axis controls
        x_frame = ttk.Frame(axis_frame)
        x_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(x_frame, text="X-axis:").pack(side=tk.LEFT)
        ttk.Label(x_frame, text="Min:").pack(side=tk.LEFT, padx=(10, 0))
        x_min_entry = ttk.Entry(x_frame, textvariable=self.axis_ranges['x_min']['var'], width=8)
        x_min_entry.pack(side=tk.LEFT, padx=(5, 10))
        # x_min_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # x_min_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        ttk.Label(x_frame, text="Max:").pack(side=tk.LEFT)
        x_max_entry = ttk.Entry(x_frame, textvariable=self.axis_ranges['x_max']['var'], width=8)
        x_max_entry.pack(side=tk.LEFT, padx=(5, 0))
        # x_max_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # x_max_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        # Y-axis controls
        y_frame = ttk.Frame(axis_frame)
        y_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(y_frame, text="Y-axis:").pack(side=tk.LEFT)
        ttk.Label(y_frame, text="Min:").pack(side=tk.LEFT, padx=(10, 0))
        y_min_entry = ttk.Entry(y_frame, textvariable=self.axis_ranges['y_min']['var'], width=8)
        y_min_entry.pack(side=tk.LEFT, padx=(5, 10))
        # y_min_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # y_min_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        ttk.Label(y_frame, text="Max:").pack(side=tk.LEFT)
        y_max_entry = ttk.Entry(y_frame, textvariable=self.axis_ranges['y_max']['var'], width=8)
        y_max_entry.pack(side=tk.LEFT, padx=(5, 0))
        # y_max_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # y_max_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        # Auto scale button
        auto_button = ttk.Button(axis_frame, text="Auto Scale", command=self._auto_scale)
        auto_button.pack(pady=5)
    
    def _create_plot_options(self, parent):
        """Create plot-specific option controls"""
        options_frame = ttk.LabelFrame(parent, text="Plot Options")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Generic options - can be extended per plot type
        ttk.Label(options_frame, text="Plot options will be added here").pack(pady=10)
    
    def _create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        refresh_button = ttk.Button(button_frame, text="Refresh Plot", command=self._refresh_plot)
        refresh_button.pack(side=tk.LEFT, padx=(0, 5))
        
        close_button = ttk.Button(button_frame, text="Close", command=self.hide)
        close_button.pack(side=tk.RIGHT)
    
    def _on_axis_change(self, event=None):
        """Handle axis range changes - update plot immediately"""
        logger.info(f"Axis range changed for {self.plot_type}")
        # Update auto flags based on current values
        for axis_key in self.axis_ranges:
            value = self.axis_ranges[axis_key]['var'].get()
            self.axis_ranges[axis_key]['auto'] = value.lower() == 'auto'
        
        # Trigger plot update
        self._refresh_plot()
    
    def _auto_scale(self):
        """Reset axis ranges to auto and refresh plot"""
        for axis in self.axis_ranges:
            self.axis_ranges[axis]['var'].set('auto')
            self.axis_ranges[axis]['auto'] = True
        logger.info(f"Auto scale applied for {self.plot_type}")
        # Immediately refresh plot
        self._refresh_plot()
    
    def _refresh_plot(self):
        """Refresh the plot with current settings"""
        logger.info(f"Plot refresh requested for {self.plot_type}")
        if self.update_callback:
            try:
                self.update_callback()
                logger.info(f"Update callback executed for {self.plot_type}")
            except Exception as e:
                logger.error(f"Error calling update callback for {self.plot_type}: {e}")
        else:
            logger.warning(f"No update callback available for {self.plot_type}")
    
    def show(self):
        """Show the control panel window"""
        if self.window is None:
            self.create_window()
        self.window.deiconify()
        self.window.lift()
        logger.info(f"Control panel shown for {self.plot_type}")
    
    def hide(self):
        """Hide the control panel window"""
        if self.window:
            self.window.withdraw()
        logger.info(f"Control panel hidden for {self.plot_type}")
    
    def get_axis_ranges(self):
        """Get current axis range settings"""
        ranges = {}
        
        # Map internal axis names to the format expected by main GUI
        axis_mapping = {
            'x_min': 'x_axis',
            'x_max': 'x_axis', 
            'y_min': 'y_axis',
            'y_max': 'y_axis'
        }
        
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


def create_plot_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                             responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> EnhancedPlotControlPanel:
    """Factory function to create a plot control panel"""
    try:
        control_panel = EnhancedPlotControlPanel(parent, plot_type, params_config, responses_config, update_callback)
        logger.info(f"Created plot control panel for {plot_type}")
        return control_panel
    except Exception as e:
        logger.error(f"Error creating plot control panel for {plot_type}: {e}")
        raise