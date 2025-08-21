"""
Window Controls Module
Separate window implementation of plot control panels
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class WindowPlotControlPanel:
    """Plot control panel in a separate window"""
    
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
        
        logger.info(f"Window plot control panel created for {plot_type}")
    
    def create_window(self):
        """Create the control panel window"""
        if self.window is not None:
            self.show()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎛️ {self.plot_type.replace('_', ' ').title()} Controls")
        self.window.geometry("350x600")
        self.window.resizable(False, False)
        
        # Set window icon (if available)
        try:
            self.window.iconbitmap(default='')
        except:
            pass
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Check if we have an enhanced control to embed
        if hasattr(self, 'enhanced_control'):
            try:
                # Create the enhanced control and embed it directly
                self.embedded_control = self.enhanced_control(
                    parent=main_frame,
                    plot_type=self.plot_type,
                    params_config=self.params_config,
                    responses_config=self.responses_config,
                    update_callback=self.update_callback
                )
                logger.info(f"Successfully embedded enhanced {self.plot_type} control")
                return
            except Exception as e:
                logger.warning(f"Failed to embed enhanced control, using standard window controls: {e}")
        
        # Title with icon (standard controls)
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text=f"📊 {self.plot_type.replace('_', ' ').title()} Controls", 
                               font=('Arial', 14, 'bold'))
        title_label.pack()
        
        # Create notebook for organized controls
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Axis tab
        axis_tab = ttk.Frame(notebook)
        notebook.add(axis_tab, text="Axis Settings")
        self._create_window_axis_controls(axis_tab)
        
        # Appearance tab
        appearance_tab = ttk.Frame(notebook)
        notebook.add(appearance_tab, text="Appearance")
        self._create_appearance_controls(appearance_tab)
        
        # Export tab
        export_tab = ttk.Frame(notebook)
        notebook.add(export_tab, text="Export")
        self._create_export_controls(export_tab)
        
        # Action buttons
        self._create_window_buttons(main_frame)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        logger.info(f"Control window created for {self.plot_type}")
    
    def _create_window_axis_controls(self, parent):
        """Create comprehensive axis range controls"""
        # X-axis section
        x_frame = ttk.LabelFrame(parent, text="X-Axis Configuration")
        x_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # X-axis range
        x_range_frame = ttk.Frame(x_frame)
        x_range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(x_range_frame, text="Range:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Label(x_range_frame, text="Min:").grid(row=0, column=1, sticky='w')
        x_min_entry = ttk.Entry(x_range_frame, textvariable=self.axis_ranges['x_min']['var'], width=12)
        x_min_entry.grid(row=0, column=2, padx=(5, 10), sticky='ew')
        # x_min_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # x_min_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        ttk.Label(x_range_frame, text="Max:").grid(row=0, column=3, sticky='w')
        x_max_entry = ttk.Entry(x_range_frame, textvariable=self.axis_ranges['x_max']['var'], width=12)
        x_max_entry.grid(row=0, column=4, padx=(5, 0), sticky='ew')
        # x_max_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # x_max_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        x_range_frame.columnconfigure(2, weight=1)
        x_range_frame.columnconfigure(4, weight=1)
        
        # Y-axis section
        y_frame = ttk.LabelFrame(parent, text="Y-Axis Configuration")
        y_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Y-axis range  
        y_range_frame = ttk.Frame(y_frame)
        y_range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(y_range_frame, text="Range:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Label(y_range_frame, text="Min:").grid(row=0, column=1, sticky='w')
        y_min_entry = ttk.Entry(y_range_frame, textvariable=self.axis_ranges['y_min']['var'], width=12)
        y_min_entry.grid(row=0, column=2, padx=(5, 10), sticky='ew')
        # y_min_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # y_min_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        ttk.Label(y_range_frame, text="Max:").grid(row=0, column=3, sticky='w')
        y_max_entry = ttk.Entry(y_range_frame, textvariable=self.axis_ranges['y_max']['var'], width=12)
        y_max_entry.grid(row=0, column=4, padx=(5, 0), sticky='ew')
        # y_max_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # y_max_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        y_range_frame.columnconfigure(2, weight=1)
        y_range_frame.columnconfigure(4, weight=1)
        
        # Auto scale section
        auto_frame = ttk.Frame(parent)
        auto_frame.pack(fill=tk.X, padx=10, pady=10)
        
        auto_button = ttk.Button(auto_frame, text="🔄 Auto Scale Both Axes", 
                                command=self._auto_scale, style='Accent.TButton')
        auto_button.pack()
    
    def _create_appearance_controls(self, parent):
        """Create appearance control options"""
        # Grid options
        grid_frame = ttk.LabelFrame(parent, text="Grid Options")
        grid_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.show_grid_var = tk.BooleanVar(value=True)
        grid_check = ttk.Checkbutton(grid_frame, text="Show Grid", 
                                    variable=self.show_grid_var,
                                    )
        grid_check.pack(anchor='w', padx=10, pady=5)
        
        # Legend options
        legend_frame = ttk.LabelFrame(parent, text="Legend Options")
        legend_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.show_legend_var = tk.BooleanVar(value=True)
        legend_check = ttk.Checkbutton(legend_frame, text="Show Legend", 
                                      variable=self.show_legend_var,
                                      )
        legend_check.pack(anchor='w', padx=10, pady=5)
        
        # Color scheme
        color_frame = ttk.LabelFrame(parent, text="Color Scheme")
        color_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.color_scheme_var = tk.StringVar(value="default")
        ttk.Radiobutton(color_frame, text="Default", variable=self.color_scheme_var, 
                       value="default").pack(anchor='w', padx=10, pady=2)
        ttk.Radiobutton(color_frame, text="Colorblind Friendly", variable=self.color_scheme_var, 
                       value="colorblind").pack(anchor='w', padx=10, pady=2)
        ttk.Radiobutton(color_frame, text="High Contrast", variable=self.color_scheme_var, 
                       value="high_contrast").pack(anchor='w', padx=10, pady=2)
    
    def _create_export_controls(self, parent):
        """Create export control options"""
        export_frame = ttk.LabelFrame(parent, text="Export Settings")
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # DPI settings
        dpi_frame = ttk.Frame(export_frame)
        dpi_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dpi_frame, text="Resolution (DPI):").pack(side=tk.LEFT)
        self.dpi_var = tk.StringVar(value="300")
        dpi_combo = ttk.Combobox(dpi_frame, textvariable=self.dpi_var, 
                                values=["150", "300", "600", "1200"], width=10)
        dpi_combo.pack(side=tk.RIGHT)
        
        # Format settings
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="PNG")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                   values=["PNG", "PDF", "SVG", "JPG"], width=10)
        format_combo.pack(side=tk.RIGHT)
        
        # Export button
        export_btn = ttk.Button(export_frame, text="💾 Export Plot", 
                               command=self._export_plot)
        export_btn.pack(pady=10)
    
    def _create_window_buttons(self, parent):
        """Create action buttons for window"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Left side buttons
        refresh_button = ttk.Button(button_frame, text="🔄 Refresh Plot", 
                                   command=self._refresh_plot, style='Accent.TButton')
        refresh_button.pack(side=tk.LEFT)
        
        apply_button = ttk.Button(button_frame, text="✓ Apply Settings", 
                                 command=self._apply_settings)
        apply_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Right side buttons
        close_button = ttk.Button(button_frame, text="✕ Close", command=self.hide)
        close_button.pack(side=tk.RIGHT)
        
        reset_button = ttk.Button(button_frame, text="↺ Reset", command=self._reset_settings)
        reset_button.pack(side=tk.RIGHT, padx=(0, 5))
    
    def _on_axis_change(self, event=None):
        """Handle axis range changes - update plot immediately"""
        logger.info(f"Axis range changed for {self.plot_type}")
        # Update auto flags based on current values
        for axis_key in self.axis_ranges:
            value = self.axis_ranges[axis_key]['var'].get()
            self.axis_ranges[axis_key]['auto'] = value.lower() == 'auto'
        
        # Trigger plot update
        self._refresh_plot()
    
    def _on_appearance_change(self):
        """Handle appearance changes - update plot appearance immediately"""
        logger.info(f"Appearance changed for {self.plot_type}")
        logger.info(f"Grid: {self.show_grid_var.get()}, Legend: {self.show_legend_var.get()}, Color: {self.color_scheme_var.get()}")
        
        try:
            # Apply appearance changes to the current figure
            self._apply_appearance_settings()
            
            # Ensure changes are immediately visible
            self._refresh_plot_canvas_only()
            
            # Additional safety check - if canvas refresh didn't work, force full refresh
            # We check this by seeing if we can get the figure
            figure = self._get_current_figure()
            if figure:
                # Ensure the figure updates are flushed to the GUI
                import matplotlib.pyplot as plt
                plt.draw()
                
        except Exception as e:
            logger.error(f"Error in appearance change handler for {self.plot_type}: {e}")
            # If there's any error, fall back to full plot refresh
            self._refresh_plot()
    
    def _apply_appearance_settings(self):
        """Apply current appearance settings to the plot figure"""
        try:
            # Find the current figure for this plot type
            figure = self._get_current_figure()
            if not figure:
                logger.warning(f"Could not find figure for {self.plot_type}")
                return
            
            # Get all axes in the figure
            axes = figure.get_axes()
            if not axes:
                logger.warning(f"No axes found in figure for {self.plot_type}")
                return
            
            # Apply settings to all axes
            for ax in axes:
                # Store current axis limits to prevent shifting
                current_xlim = ax.get_xlim()
                current_ylim = ax.get_ylim()
                
                # Grid settings - preserve tick locations to prevent shifting
                if self.show_grid_var.get():
                    # Apply grid with consistent formatting
                    ax.grid(True, alpha=0.7, linestyle='-', linewidth=0.8, 
                           which='major', axis='both')
                    # Ensure minor grid aligns properly
                    ax.minorticks_on()
                    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5, 
                           which='minor', axis='both')
                else:
                    ax.grid(False, which='both')
                
                # Restore axis limits to prevent grid shifting the view
                ax.set_xlim(current_xlim)
                ax.set_ylim(current_ylim)
                
                # Refresh tick parameters without changing positions
                ax.tick_params(which='major', length=6, width=1, direction='out')
                ax.tick_params(which='minor', length=3, width=0.8, direction='out')
                
                # Legend settings
                legend = ax.get_legend()
                if legend:
                    legend.set_visible(self.show_legend_var.get())
                
                # Color scheme settings
                self._apply_color_scheme(ax)
            
            # Force figure to redraw with new settings
            figure.canvas.draw_idle()
            logger.info(f"Applied appearance settings to {self.plot_type}")
            
        except Exception as e:
            logger.error(f"Error applying appearance settings for {self.plot_type}: {e}")
    
    def _apply_color_scheme(self, ax):
        """Apply color scheme to the axes"""
        color_scheme = self.color_scheme_var.get()
        
        try:
            if color_scheme == "high_contrast":
                # High contrast: black background, white text
                ax.set_facecolor('black')
                ax.tick_params(colors='white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.title.set_color('white')
                # Change line colors to high contrast
                for line in ax.get_lines():
                    if hasattr(line, 'set_color'):
                        line.set_color('white')
                        
            elif color_scheme == "colorblind":
                # Colorblind friendly palette
                import matplotlib.pyplot as plt
                colorblind_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
                ax.set_prop_cycle('color', colorblind_colors)
                
            else:  # default
                # Reset to default matplotlib style
                ax.set_facecolor('white')
                ax.tick_params(colors='black')
                ax.xaxis.label.set_color('black')
                ax.yaxis.label.set_color('black')
                ax.title.set_color('black')
                
        except Exception as e:
            logger.warning(f"Could not apply color scheme {color_scheme}: {e}")
    
    def _get_current_figure(self):
        """Get the current matplotlib figure for this plot type"""
        try:
            # Try to find the figure in the main GUI
            parent_gui = self.parent
            fig_attr_name = f"{self.plot_type}_fig"
            
            if hasattr(parent_gui, fig_attr_name):
                return getattr(parent_gui, fig_attr_name)
            
            # Fallback: try to get current figure
            import matplotlib.pyplot as plt
            return plt.gcf()
            
        except Exception as e:
            logger.error(f"Error getting figure for {self.plot_type}: {e}")
            return None
    
    def _refresh_plot_canvas_only(self):
        """Refresh only the canvas without regenerating the plot data"""
        try:
            # Find the canvas for this plot type
            parent_gui = self.parent
            canvas_attr_name = f"{self.plot_type}_canvas"
            
            if hasattr(parent_gui, canvas_attr_name):
                canvas = getattr(parent_gui, canvas_attr_name)
                if canvas and hasattr(canvas, 'draw'):
                    # Use draw_idle() for better performance and fewer redraw conflicts
                    canvas.draw_idle()
                    # Force immediate update of the Tkinter widget
                    canvas.get_tk_widget().update_idletasks()
                    canvas.get_tk_widget().update()
                    logger.info(f"Canvas refreshed for {self.plot_type}")
                    return
            
            # Try alternative canvas naming patterns
            alt_canvas_names = [
                f"{self.plot_type}_plot_canvas",
                f"canvas_{self.plot_type}",
                "plot_canvas",
                "canvas"
            ]
            
            for alt_name in alt_canvas_names:
                if hasattr(parent_gui, alt_name):
                    canvas = getattr(parent_gui, alt_name)
                    if canvas and hasattr(canvas, 'draw'):
                        canvas.draw_idle()
                        canvas.get_tk_widget().update_idletasks()
                        canvas.get_tk_widget().update()
                        logger.info(f"Canvas refreshed for {self.plot_type} using {alt_name}")
                        return
            
            # Fallback: try to get figure and force redraw
            figure = self._get_current_figure()
            if figure and hasattr(figure, 'canvas'):
                figure.canvas.draw_idle()
                logger.info(f"Figure canvas refreshed for {self.plot_type}")
                return
            
            # Last resort: full plot refresh
            logger.warning(f"Could not find canvas for {self.plot_type}, falling back to full refresh")
            self._refresh_plot()
            
        except Exception as e:
            logger.error(f"Error refreshing canvas for {self.plot_type}: {e}")
            # Fallback to full refresh
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
        
        # Debug: Log current axis ranges
        ranges = self.get_axis_ranges()
        logger.info(f"Current axis ranges for {self.plot_type}: {ranges}")
        
        if self.update_callback:
            try:
                self.update_callback()
                logger.info(f"Update callback executed for {self.plot_type}")
            except Exception as e:
                logger.error(f"Error calling update callback for {self.plot_type}: {e}")
        else:
            logger.warning(f"No update callback available for {self.plot_type}")
    
    def _apply_settings(self):
        """Apply current settings to the plot"""
        logger.info(f"Settings applied for {self.plot_type}")
        if self.update_callback:
            try:
                self.update_callback()
                logger.info(f"Settings applied and plot updated for {self.plot_type}")
            except Exception as e:
                logger.error(f"Error applying settings for {self.plot_type}: {e}")
    
    def _reset_settings(self):
        """Reset all settings to defaults"""
        self._auto_scale()
        self.show_grid_var.set(True)
        self.show_legend_var.set(True)
        self.color_scheme_var.set("default")
        self.dpi_var.set("300")
        self.format_var.set("PNG")
        logger.info(f"Settings reset for {self.plot_type}")
    
    def _export_plot(self):
        """Export the plot with current settings"""
        from tkinter import filedialog, messagebox
        import matplotlib.pyplot as plt
        
        try:
            format_ext = self.format_var.get().lower()
            dpi_value = int(self.dpi_var.get())
            
            # Get filename from user
            filename = filedialog.asksaveasfilename(
                title=f"Export {self.plot_type.replace('_', ' ').title()} Plot",
                defaultextension=f".{format_ext}",
                filetypes=[
                    (f"{format_ext.upper()} files", f"*.{format_ext}"),
                    ("All files", "*.*")
                ]
            )
            
            if not filename:
                return  # User cancelled
            
            # Try to find the current figure for this plot type
            figure = None
            parent_gui = self.parent
            
            # Look for the figure in the main GUI
            fig_attr_name = f"{self.plot_type}_fig"
            if hasattr(parent_gui, fig_attr_name):
                figure = getattr(parent_gui, fig_attr_name)
            
            if figure is None:
                # Fallback: try to get current figure
                figure = plt.gcf()
            
            if figure:
                # Save the figure
                figure.savefig(filename, format=format_ext, dpi=dpi_value, 
                             bbox_inches='tight', facecolor='white')
                
                messagebox.showinfo("Export Successful", 
                                  f"Plot exported successfully to:\n{filename}")
                logger.info(f"Plot exported to {filename} "
                           f"(Format: {format_ext}, DPI: {dpi_value})")
            else:
                messagebox.showerror("Export Error", 
                                   "Could not find the plot to export. "
                                   "Please ensure the plot is currently displayed.")
                logger.error(f"Could not find figure to export for {self.plot_type}")
                
        except Exception as e:
            error_msg = f"Failed to export plot: {str(e)}"
            messagebox.showerror("Export Error", error_msg)
            logger.error(f"Export error for {self.plot_type}: {e}")
    
    def show(self):
        """Show the control panel window"""
        if self.window is None:
            self.create_window()
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        logger.info(f"Control window shown for {self.plot_type}")
    
    def hide(self):
        """Hide the control panel window"""
        if self.window:
            self.window.withdraw()
        logger.info(f"Control window hidden for {self.plot_type}")
    
    def _on_window_close(self):
        """Handle window close event"""
        self.hide()
        # Notify parent GUI to update button text
        if hasattr(self.parent, '_update_control_button_text'):
            self.parent._update_control_button_text("⚙ Open Controls")
    
    def is_visible(self):
        """Check if the control panel window is currently visible"""
        if self.window is None:
            return False
        try:
            return self.window.state() == 'normal'
        except tk.TclError:
            return False
    
    def get_axis_ranges(self):
        """Get current axis range settings"""
        # Delegate to embedded control if available
        if hasattr(self, 'embedded_control') and hasattr(self.embedded_control, 'get_axis_ranges'):
            return self.embedded_control.get_axis_ranges()
        
        # Standard window control behavior
        ranges = {}
        
        # Collect min/max values for each axis
        x_min_val, x_max_val, x_auto = self._get_axis_value('x_min')
        y_min_val, y_max_val, y_auto = self._get_axis_value('y_min')
        
        # Format for main GUI expectation: (min_val, max_val, is_auto)
        ranges['x_axis'] = (x_min_val, x_max_val, x_auto)
        ranges['y_axis'] = (y_min_val, y_max_val, y_auto)
        
        return ranges
    
    def get_display_options(self):
        """Get current display options"""
        # Delegate to embedded control if available
        if hasattr(self, 'embedded_control') and hasattr(self.embedded_control, 'get_display_options'):
            return self.embedded_control.get_display_options()
        
        # Standard window control behavior - return empty dict
        return {}
    
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


def create_window_plot_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                    responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> WindowPlotControlPanel:
    """Factory function to create a window plot control panel"""
    try:
        # Check for specialized plot types
        if plot_type == 'surface_3d' or '3d' in plot_type.lower() or 'surface' in plot_type.lower():
            try:
                from .surface_3d_controls import create_surface_3d_control_panel
                return create_surface_3d_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("3D Surface controls not available, using standard controls")
        
        elif plot_type == 'gp_uncertainty' or 'uncertainty' in plot_type.lower():
            try:
                from .gp_uncertainty_controls import create_gp_uncertainty_control_panel
                return create_gp_uncertainty_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("GP Uncertainty controls not available, using standard controls")
        
        elif plot_type == 'parallel_coordinates':
            try:
                from .parallel_coordinates_controls import create_parallel_coordinates_control_panel
                return create_parallel_coordinates_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("Parallel coordinates controls not available, using standard controls")
        
        elif plot_type == 'sensitivity_analysis' or 'sensitivity' in plot_type.lower():
            try:
                from .sensitivity_analysis_controls import create_sensitivity_analysis_control_panel
                logger.info(f"Using specialized Sensitivity Analysis controls instead of window for {plot_type}")
                return create_sensitivity_analysis_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("Sensitivity Analysis controls not available, using standard window controls")
        
        elif plot_type == 'pareto':
            try:
                from .pareto_controls import create_pareto_control_panel
                logger.info(f"Using specialized Pareto controls in window for {plot_type}")
                # Create window wrapper for enhanced Pareto controls
                window_wrapper = WindowPlotControlPanel(parent, plot_type, params_config, responses_config, update_callback)
                window_wrapper.enhanced_control = create_pareto_control_panel
                return window_wrapper
            except ImportError:
                logger.warning("Pareto controls not available, using standard window controls")
        
        elif plot_type == 'progress':
            try:
                from .progress_controls import create_progress_control_panel
                logger.info(f"Using specialized Progress controls in window for {plot_type}")
                # Create window wrapper for enhanced Progress controls
                window_wrapper = WindowPlotControlPanel(parent, plot_type, params_config, responses_config, update_callback)
                window_wrapper.enhanced_control = create_progress_control_panel
                return window_wrapper
            except ImportError:
                logger.warning("Progress controls not available, using standard window controls")
        
        elif plot_type == 'gp_slice':
            try:
                from .gp_slice_controls import create_gp_slice_control_panel
                logger.info(f"Using specialized GP slice controls for {plot_type}")
                return create_gp_slice_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("GP slice controls not available, using standard window controls")
        
        # Default to standard window controls
        control_panel = WindowPlotControlPanel(parent, plot_type, params_config, responses_config, update_callback)
        logger.info(f"Created window plot control panel for {plot_type}")
        return control_panel
    except Exception as e:
        logger.error(f"Error creating window plot control panel for {plot_type}: {e}")
        raise