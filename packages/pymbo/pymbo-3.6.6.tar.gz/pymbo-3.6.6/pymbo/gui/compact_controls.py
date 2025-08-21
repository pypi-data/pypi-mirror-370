"""
Compact Controls Module
Compact implementation of plot control panels that can be embedded in the main interface
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class CompactPlotControlPanel:
    """Compact plot control panel that can be embedded in the main interface"""
    
    def __init__(self, parent, plot_type: str, params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.control_frame = None
        self.axis_ranges = {}
        
        # Initialize default axis ranges
        self.axis_ranges = {
            'x_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'x_max': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_max': {'var': tk.StringVar(value='auto'), 'auto': True}
        }
        
        self.create_controls()
        logger.info(f"Compact plot control panel created for {plot_type}")
    
    def create_controls(self):
        """Create the compact control panel"""
        # Main control frame with border
        self.control_frame = tk.Frame(self.parent, bg='lightgray', relief='raised', bd=2)
        
        # Title bar
        title_frame = tk.Frame(self.control_frame, bg='darkgray')
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, text=f"{self.plot_type.replace('_', ' ').title()}", 
                              bg='darkgray', fg='white', font=('Arial', 8, 'bold'))
        title_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Close button
        close_btn = tk.Button(title_frame, text='×', command=self.hide, 
                             bg='darkgray', fg='white', bd=0, font=('Arial', 8))
        close_btn.pack(side=tk.RIGHT, padx=2)
        
        # Content frame
        content_frame = tk.Frame(self.control_frame, bg='lightgray')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Compact axis controls
        self._create_compact_axis_controls(content_frame)
        
        # Action buttons
        self._create_compact_buttons(content_frame)
    
    def _create_compact_axis_controls(self, parent):
        """Create compact axis range controls"""
        # X-axis row
        x_frame = tk.Frame(parent, bg='lightgray')
        x_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(x_frame, text="X:", bg='lightgray', font=('Arial', 7)).pack(side=tk.LEFT)
        x_min_entry = tk.Entry(x_frame, textvariable=self.axis_ranges['x_min']['var'], 
                              width=6, font=('Arial', 7))
        x_min_entry.pack(side=tk.LEFT, padx=2)
        # x_min_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # x_min_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        tk.Label(x_frame, text="to", bg='lightgray', font=('Arial', 7)).pack(side=tk.LEFT)
        x_max_entry = tk.Entry(x_frame, textvariable=self.axis_ranges['x_max']['var'], 
                              width=6, font=('Arial', 7))
        x_max_entry.pack(side=tk.LEFT, padx=2)
        # x_max_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # x_max_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        # Y-axis row
        y_frame = tk.Frame(parent, bg='lightgray')
        y_frame.pack(fill=tk.X, pady=1)
        
        tk.Label(y_frame, text="Y:", bg='lightgray', font=('Arial', 7)).pack(side=tk.LEFT)
        y_min_entry = tk.Entry(y_frame, textvariable=self.axis_ranges['y_min']['var'], 
                              width=6, font=('Arial', 7))
        y_min_entry.pack(side=tk.LEFT, padx=2)
        # y_min_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # y_min_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        tk.Label(y_frame, text="to", bg='lightgray', font=('Arial', 7)).pack(side=tk.LEFT)
        y_max_entry = tk.Entry(y_frame, textvariable=self.axis_ranges['y_max']['var'], 
                              width=6, font=('Arial', 7))
        y_max_entry.pack(side=tk.LEFT, padx=2)
        # y_max_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # y_max_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
    
    def _create_compact_buttons(self, parent):
        """Create compact action buttons"""
        button_frame = tk.Frame(parent, bg='lightgray')
        button_frame.pack(fill=tk.X, pady=2)
        
        auto_btn = tk.Button(button_frame, text="Auto", command=self._auto_scale,
                            font=('Arial', 7), width=6)
        auto_btn.pack(side=tk.LEFT, padx=1)
        
        refresh_btn = tk.Button(button_frame, text="Refresh", command=self._refresh_plot,
                               font=('Arial', 7), width=6)
        refresh_btn.pack(side=tk.RIGHT, padx=1)
    
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
        """Reset axis ranges to auto"""
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
        """Show the compact control panel"""
        if self.control_frame:
            self.control_frame.place(x=10, y=10, width=180, height=100)
        logger.info(f"Compact control panel shown for {self.plot_type}")
    
    def hide(self):
        """Hide the compact control panel"""
        if self.control_frame:
            self.control_frame.place_forget()
        logger.info(f"Compact control panel hidden for {self.plot_type}")
    
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


def create_compact_plot_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                     responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> CompactPlotControlPanel:
    """Factory function to create a compact plot control panel"""
    try:
        # For complex plots like 3D Surface and GP Uncertainty, redirect to window controls
        # since compact controls would be too cramped for all the options
        if plot_type == 'surface_3d' or '3d' in plot_type.lower() or 'surface' in plot_type.lower():
            try:
                from .surface_3d_controls import create_surface_3d_control_panel
                logger.info(f"Using specialized 3D Surface controls instead of compact for {plot_type}")
                return create_surface_3d_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("3D Surface controls not available, using standard compact controls")
        
        elif plot_type == 'gp_uncertainty' or 'uncertainty' in plot_type.lower():
            try:
                from .gp_uncertainty_controls import create_gp_uncertainty_control_panel
                logger.info(f"Using specialized GP Uncertainty controls instead of compact for {plot_type}")
                return create_gp_uncertainty_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("GP Uncertainty controls not available, using standard compact controls")
        
        elif plot_type == 'sensitivity_analysis' or 'sensitivity' in plot_type.lower():
            try:
                from .sensitivity_analysis_controls import create_sensitivity_analysis_control_panel
                logger.info(f"Using specialized Sensitivity Analysis controls instead of compact for {plot_type}")
                return create_sensitivity_analysis_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("Sensitivity Analysis controls not available, using standard compact controls")
        
        # Default to standard compact controls for other plot types
        control_panel = CompactPlotControlPanel(parent, plot_type, params_config, responses_config, update_callback)
        logger.info(f"Created compact plot control panel for {plot_type}")
        return control_panel
    except Exception as e:
        logger.error(f"Error creating compact plot control panel for {plot_type}: {e}")
        raise