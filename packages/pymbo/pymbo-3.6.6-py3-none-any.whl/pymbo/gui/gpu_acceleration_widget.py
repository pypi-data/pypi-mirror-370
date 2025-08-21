"""
GPU Acceleration Widget for PyMBO GUI

This module provides a widget for displaying GPU acceleration status,
device information, and GPU-specific optimization controls within the
main PyMBO GUI interface.

Key Features:
- Real-time device detection and status display
- GPU memory usage monitoring
- Performance metrics display
- GPU-accelerated validation controls
- Hardware compatibility information
- Automatic device switching options

Classes:
    GPUAccelerationWidget: Main GPU status and control widget
    GPUStatusIndicator: Device status indicator component
    GPUMemoryMonitor: Memory usage monitoring component
    GPUPerformanceDisplay: Performance metrics display
    GPUValidationControls: GPU-accelerated validation controls

Author: Multi-Objective Optimization Laboratory
Version: 3.6.6 GPU Accelerated
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

# Color scheme for GPU widget
GPU_COLORS = {
    'nvidia_green': '#76B900',
    'apple_blue': '#007AFF', 
    'cpu_gray': '#6C757D',
    'success': '#28A745',
    'warning': '#FFC107',
    'error': '#DC3545',
    'background': '#F8F9FA',
    'text': '#212529'
}


class GPUStatusIndicator(tk.Frame):
    """Device status indicator showing current GPU/CPU status."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=GPU_COLORS['background'], **kwargs)
        self.device_info = {}
        self.status_var = tk.StringVar(value="Detecting...")
        self.device_var = tk.StringVar(value="Unknown")
        self._shutdown_flag = threading.Event()
        
        self._create_status_display()
        self._start_status_monitoring()
    
    def _create_status_display(self):
        """Create the status display components."""
        # Status indicator circle
        self.status_canvas = tk.Canvas(self, width=20, height=20, 
                                     bg=GPU_COLORS['background'], 
                                     highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status circle (will be colored based on device type)
        self.status_circle = self.status_canvas.create_oval(2, 2, 18, 18, 
                                                          fill=GPU_COLORS['cpu_gray'],
                                                          outline='white', width=2)
        
        # Device info label
        info_frame = tk.Frame(self, bg=GPU_COLORS['background'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Device name
        self.device_label = tk.Label(info_frame,
                                   textvariable=self.device_var,
                                   font=('Arial', 10, 'bold'),
                                   bg=GPU_COLORS['background'],
                                   fg=GPU_COLORS['text'])
        self.device_label.pack(anchor='w')
        
        # Status text
        self.status_label = tk.Label(info_frame,
                                   textvariable=self.status_var,
                                   font=('Arial', 9),
                                   bg=GPU_COLORS['background'],
                                   fg=GPU_COLORS['text'])
        self.status_label.pack(anchor='w')
    
    def _start_status_monitoring(self):
        """Start background thread for status monitoring."""
        def monitor_status():
            while not self._shutdown_flag.is_set():
                try:
                    self._update_device_status()
                    # Use wait instead of sleep to allow interruption
                    if self._shutdown_flag.wait(5.0):  # Update every 5 seconds
                        break
                except Exception as e:
                    logger.error(f"GPU status monitoring error: {e}")
                    if self._shutdown_flag.wait(10.0):  # Wait longer if error occurs
                        break
        
        thread = threading.Thread(target=monitor_status, daemon=True)
        thread.start()
    
    def _update_device_status(self):
        """Update device status information."""
        try:
            from pymbo.core.device_manager import get_device_info
            self.device_info = get_device_info()
            
            device_type = self.device_info.get('device_type', 'cpu')
            device_name = self.device_info.get('device_name', 'Unknown Device')
            
            # Update device name
            self.device_var.set(device_name)
            
            # Update status and color based on device type
            if device_type == 'cuda':
                color = GPU_COLORS['nvidia_green']
                status = f"GPU Accelerated (CUDA)"
                if 'total_memory_gb' in self.device_info:
                    memory_gb = self.device_info['total_memory_gb']
                    status += f" - {memory_gb:.1f}GB"
            elif device_type == 'mps':
                color = GPU_COLORS['apple_blue']
                status = f"GPU Accelerated (Metal)"
            else:
                color = GPU_COLORS['cpu_gray']
                status = "CPU Mode"
                if 'cores' in self.device_info:
                    cores = self.device_info['cores']
                    status += f" - {cores} cores"
            
            # Update UI in main thread
            self.after(0, lambda: self._update_ui(color, status))
            
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            self.after(0, lambda: self._update_ui(GPU_COLORS['error'], "Detection Error"))
    
    def _update_ui(self, color: str, status: str):
        """Update UI elements in main thread."""
        try:
            # Check if widget still exists before updating
            if hasattr(self, 'status_canvas') and self.status_canvas.winfo_exists():
                self.status_canvas.itemconfig(self.status_circle, fill=color)
            if hasattr(self, 'status_var'):
                self.status_var.set(status)
        except tk.TclError:
            # Widget has been destroyed during shutdown - silently ignore
            pass
        except Exception as e:
            logger.debug(f"GPU status UI update failed (likely during shutdown): {e}")
    
    def destroy(self):
        """Clean shutdown of monitoring thread."""
        self._shutdown_flag.set()
        super().destroy()


class GPUMemoryMonitor(tk.Frame):
    """Memory usage monitoring component."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=GPU_COLORS['background'], **kwargs)
        self.memory_info = {}
        self._shutdown_flag = threading.Event()
        
        self._create_memory_display()
        self._start_memory_monitoring()
    
    def _create_memory_display(self):
        """Create memory monitoring display."""
        # Title
        title_label = tk.Label(self, text="Memory Usage",
                             font=('Arial', 10, 'bold'),
                             bg=GPU_COLORS['background'],
                             fg=GPU_COLORS['text'])
        title_label.pack(anchor='w')
        
        # Memory info frame
        self.memory_frame = tk.Frame(self, bg=GPU_COLORS['background'])
        self.memory_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Memory labels (will be populated by monitoring thread)
        self.memory_labels = {}
    
    def _start_memory_monitoring(self):
        """Start background thread for memory monitoring."""
        def monitor_memory():
            while not self._shutdown_flag.is_set():
                try:
                    self._update_memory_info()
                    # Use wait instead of sleep to allow interruption
                    if self._shutdown_flag.wait(3.0):  # Update every 3 seconds
                        break
                except Exception as e:
                    logger.error(f"Memory monitoring error: {e}")
                    if self._shutdown_flag.wait(10.0):  # Wait longer if error occurs
                        break
        
        thread = threading.Thread(target=monitor_memory, daemon=True)
        thread.start()
    
    def _update_memory_info(self):
        """Update memory usage information."""
        try:
            from pymbo.core.device_manager import get_memory_usage
            self.memory_info = get_memory_usage()
            
            # Update UI in main thread
            self.after(0, self._update_memory_ui)
            
        except Exception as e:
            logger.info(f"💾 GPU memory monitoring temporarily unavailable (GUI thread issue): {e}")
    
    def _update_memory_ui(self):
        """Update memory display in main thread."""
        try:
            # Clear existing labels
            for label in self.memory_labels.values():
                label.destroy()
            self.memory_labels.clear()
            
            # Debug: Check if we have memory info
            if not self.memory_info:
                logger.debug("No memory info available for UI update")
                return
                
            # Create new labels based on available memory info
            row = 0
            for key, value in self.memory_info.items():
                if isinstance(value, (int, float)):
                    # Improved formatting for different value types
                    if 'gb' in key.lower():
                        # Show more precision for small GB values
                        if value < 0.1:
                            text = f"{key.replace('_', ' ').title()}: {value*1000:.1f} MB"
                        else:
                            text = f"{key.replace('_', ' ').title()}: {value:.2f} GB"
                    elif 'percent' in key.lower():
                        text = f"{key.replace('_', ' ').title()}: {value:.1f}%"
                    else:
                        text = f"{key.replace('_', ' ').title()}: {value}"
                    
                    try:
                        label = tk.Label(self.memory_frame, text=text,
                                       font=('Arial', 9),
                                       bg=GPU_COLORS['background'],
                                       fg=GPU_COLORS['text'])
                        label.grid(row=row, column=0, sticky='w', pady=1)
                        self.memory_labels[key] = label
                        row += 1
                        logger.debug(f"Created memory label: {key} = {text}")
                    except Exception as label_error:
                        logger.error(f"Failed to create label for {key}: {label_error}")
                        
        except tk.TclError:
            # Widget has been destroyed during shutdown - silently ignore
            pass
        except Exception as e:
            logger.debug(f"Memory UI update failed (likely during shutdown): {e}")
    
    def destroy(self):
        """Clean shutdown of monitoring thread."""
        self._shutdown_flag.set()
        super().destroy()


class GPUPerformanceDisplay(tk.Frame):
    """Performance metrics display component."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=GPU_COLORS['background'], **kwargs)
        self.performance_history = []
        self.max_history = 10
        
        self._create_performance_display()
    
    def _create_performance_display(self):
        """Create performance metrics display."""
        # Title
        title_label = tk.Label(self, text="Performance Metrics",
                             font=('Arial', 10, 'bold'),
                             bg=GPU_COLORS['background'],
                             fg=GPU_COLORS['text'])
        title_label.pack(anchor='w')
        
        # Metrics frame
        metrics_frame = tk.Frame(self, bg=GPU_COLORS['background'])
        metrics_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Performance labels
        self.avg_time_var = tk.StringVar(value="Avg Evaluation Time: N/A")
        self.throughput_var = tk.StringVar(value="Throughput: N/A")
        self.speedup_var = tk.StringVar(value="GPU Speedup: N/A")
        
        tk.Label(metrics_frame, textvariable=self.avg_time_var,
                font=('Arial', 9), bg=GPU_COLORS['background'],
                fg=GPU_COLORS['text']).pack(anchor='w')
        
        tk.Label(metrics_frame, textvariable=self.throughput_var,
                font=('Arial', 9), bg=GPU_COLORS['background'],
                fg=GPU_COLORS['text']).pack(anchor='w')
        
        tk.Label(metrics_frame, textvariable=self.speedup_var,
                font=('Arial', 9), bg=GPU_COLORS['background'],
                fg=GPU_COLORS['text']).pack(anchor='w')
    
    def update_performance(self, execution_time: float, n_evaluations: int, 
                         speedup: Optional[float] = None):
        """Update performance metrics with new data."""
        try:
            # Add to performance history
            if execution_time > 0 and n_evaluations > 0:
                eval_time = execution_time / n_evaluations
                throughput = n_evaluations / execution_time
                
                self.performance_history.append({
                    'eval_time': eval_time,
                    'throughput': throughput,
                    'speedup': speedup
                })
                
                # Keep only recent history
                if len(self.performance_history) > self.max_history:
                    self.performance_history = self.performance_history[-self.max_history:]
                
                # Calculate averages
                avg_eval_time = sum(h['eval_time'] for h in self.performance_history) / len(self.performance_history)
                avg_throughput = sum(h['throughput'] for h in self.performance_history) / len(self.performance_history)
                
                # Update display
                self.avg_time_var.set(f"Avg Evaluation Time: {avg_eval_time*1000:.2f} ms")
                self.throughput_var.set(f"Throughput: {avg_throughput:.1f} eval/sec")
                
                if speedup is not None:
                    self.speedup_var.set(f"GPU Speedup: {speedup:.1f}x")
                    
        except Exception as e:
            logger.error(f"Failed to update performance metrics: {e}")


class GPUValidationControls(tk.Frame):
    """GPU-accelerated validation controls."""
    
    def __init__(self, parent, validation_callback: Optional[Callable] = None, **kwargs):
        super().__init__(parent, bg=GPU_COLORS['background'], **kwargs)
        self.validation_callback = validation_callback
        
        self._create_validation_controls()
    
    def _create_validation_controls(self):
        """Create GPU validation control interface."""
        # Title
        title_frame = tk.Frame(self, bg=GPU_COLORS['background'])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(title_frame, text="GPU Validation",
                font=('Arial', 11, 'bold'),
                bg=GPU_COLORS['background'],
                fg=GPU_COLORS['text']).pack(side=tk.LEFT)
        
        # Settings frame
        settings_frame = tk.LabelFrame(self, text="Settings", 
                                     font=('Arial', 9),
                                     bg=GPU_COLORS['background'])
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Test function selection
        tk.Label(settings_frame, text="Test Function:",
                font=('Arial', 9), bg=GPU_COLORS['background']).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        
        self.test_func_var = tk.StringVar(value="ZDT1")
        test_func_combo = ttk.Combobox(settings_frame, textvariable=self.test_func_var,
                                     values=["ZDT1", "ZDT2", "DTLZ2"], state="readonly", width=10)
        test_func_combo.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Algorithm selection
        tk.Label(settings_frame, text="Algorithms:",
                font=('Arial', 9), bg=GPU_COLORS['background']).grid(row=1, column=0, sticky='w', padx=5, pady=2)
        
        # Algorithm checkboxes
        alg_frame = tk.Frame(settings_frame, bg=GPU_COLORS['background'])
        alg_frame.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        self.algorithm_vars = {}
        algorithms = ["GPU Random Search", "This App's GPU MOBO", "GPU NSGA-II"]
        
        for i, alg in enumerate(algorithms):
            var = tk.BooleanVar(value=(i < 2))  # Enable first two by default
            self.algorithm_vars[alg] = var
            
            cb = tk.Checkbutton(alg_frame, text=alg, variable=var,
                              font=('Arial', 8), bg=GPU_COLORS['background'])
            cb.pack(anchor='w')
        
        # Evaluation parameters
        param_frame = tk.Frame(settings_frame, bg=GPU_COLORS['background'])
        param_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        tk.Label(param_frame, text="Evaluations:",
                font=('Arial', 9), bg=GPU_COLORS['background']).grid(row=0, column=0, sticky='w')
        
        self.n_evals_var = tk.StringVar(value="50")
        tk.Entry(param_frame, textvariable=self.n_evals_var, width=8).grid(row=0, column=1, padx=5)
        
        tk.Label(param_frame, text="Runs:",
                font=('Arial', 9), bg=GPU_COLORS['background']).grid(row=0, column=2, sticky='w', padx=(10, 0))
        
        self.n_runs_var = tk.StringVar(value="5")
        tk.Entry(param_frame, textvariable=self.n_runs_var, width=8).grid(row=0, column=3, padx=5)
        
        # Batch size (GPU-specific)
        tk.Label(param_frame, text="Batch Size:",
                font=('Arial', 9), bg=GPU_COLORS['background']).grid(row=1, column=0, sticky='w')
        
        self.batch_size_var = tk.StringVar(value="Auto")
        batch_combo = ttk.Combobox(param_frame, textvariable=self.batch_size_var,
                                 values=["Auto", "16", "32", "64", "128", "256"], width=8)
        batch_combo.grid(row=1, column=1, padx=5, pady=2)
        
        # Control buttons
        button_frame = tk.Frame(self, bg=GPU_COLORS['background'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Run GPU Validation button
        self.run_button = tk.Button(button_frame, text="🚀 Run GPU Validation",
                                  font=('Arial', 10, 'bold'),
                                  bg=GPU_COLORS['success'], fg='white',
                                  command=self._run_gpu_validation)
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(button_frame, variable=self.progress_var,
                                          maximum=100, length=200)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(button_frame, textvariable=self.status_var,
                font=('Arial', 9), bg=GPU_COLORS['background']).pack(side=tk.RIGHT)
    
    def _run_gpu_validation(self):
        """Run GPU validation in background thread."""
        if self.validation_callback:
            # Get selected algorithms
            selected_algorithms = [alg for alg, var in self.algorithm_vars.items() if var.get()]
            
            if not selected_algorithms:
                messagebox.showwarning("No Algorithms", "Please select at least one algorithm to compare.")
                return
            
            # Get parameters
            try:
                n_evaluations = int(self.n_evals_var.get())
                n_runs = int(self.n_runs_var.get())
                batch_size = None if self.batch_size_var.get() == "Auto" else int(self.batch_size_var.get())
            except ValueError:
                messagebox.showerror("Invalid Parameters", "Please enter valid numeric values for evaluations and runs.")
                return
            
            # Disable button during execution
            self.run_button.config(state='disabled')
            self.status_var.set("Running GPU validation...")
            self.progress_var.set(0)
            
            # Run in background thread
            def run_validation():
                try:
                    # Simulate progress updates since validation engine doesn't support callbacks
                    import threading
                    import time
                    
                    def simulate_progress():
                        total_steps = n_evaluations * n_runs * len(selected_algorithms)
                        estimated_time = total_steps * 0.1  # Rough estimate: 0.1s per evaluation
                        step_time = estimated_time / 10  # 10 progress updates
                        
                        for i in range(11):  # 0% to 100%
                            progress = i * 10
                            self.after(0, lambda p=progress: self.progress_var.set(p))
                            if i < 10:  # Don't sleep after the last update
                                time.sleep(step_time)
                    
                    # Start progress simulation in separate thread
                    progress_thread = threading.Thread(target=simulate_progress, daemon=True)
                    progress_thread.start()
                    
                    result = self.validation_callback(
                        test_function_name=self.test_func_var.get(),
                        algorithms=selected_algorithms,
                        n_evaluations=n_evaluations,
                        n_runs=n_runs,
                        batch_size=batch_size
                    )
                    
                    # Update UI in main thread
                    self.after(0, lambda: self._validation_completed(result))
                    
                except Exception as e:
                    logger.error(f"GPU validation failed: {e}")
                    error_msg = str(e)  # Capture error message before lambda
                    self.after(0, lambda: self._validation_failed(error_msg))
            
            thread = threading.Thread(target=run_validation, daemon=True)
            thread.start()
    
    def _update_progress(self, progress: float):
        """Update progress bar (called from background thread)."""
        self.after(0, lambda: self.progress_var.set(progress))
    
    def _validation_completed(self, result):
        """Handle validation completion."""
        self.run_button.config(state='normal')
        self.status_var.set("Validation completed")
        self.progress_var.set(100)
        
        # Show results summary
        execution_time = result.execution_time
        device_name = result.device_info.get('device_name', 'Unknown')
        
        messagebox.showinfo("GPU Validation Complete", 
                          f"Validation completed successfully!\n\n"
                          f"Device: {device_name}\n"
                          f"Execution Time: {execution_time:.2f} seconds\n"
                          f"Algorithms: {len(result.algorithms)}\n"
                          f"Total Runs: {result.n_runs}")
    
    def _validation_failed(self, error_msg: str):
        """Handle validation failure."""
        self.run_button.config(state='normal')
        self.status_var.set("Validation failed")
        self.progress_var.set(0)
        
        messagebox.showerror("GPU Validation Failed", 
                           f"Validation failed with error:\n\n{error_msg}")


class GPUAccelerationWidget(tk.Frame):
    """Main GPU acceleration widget combining all components."""
    
    def __init__(self, parent, validation_callback: Optional[Callable] = None, **kwargs):
        super().__init__(parent, bg=GPU_COLORS['background'], relief='raised', bd=1, **kwargs)
        self.validation_callback = validation_callback
        
        self._create_widget()
    
    def _create_widget(self):
        """Create the complete GPU acceleration widget."""
        # Main title
        title_frame = tk.Frame(self, bg=GPU_COLORS['background'])
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(title_frame, text="🚀 GPU Acceleration",
                font=('Arial', 12, 'bold'),
                bg=GPU_COLORS['background'],
                fg=GPU_COLORS['text']).pack(side=tk.LEFT)
        
        # Create notebook for different sections
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status tab
        status_frame = tk.Frame(notebook, bg=GPU_COLORS['background'])
        notebook.add(status_frame, text="Status")
        
        # Status indicator
        self.status_indicator = GPUStatusIndicator(status_frame)
        self.status_indicator.pack(fill=tk.X, padx=10, pady=10)
        
        # Memory monitor
        self.memory_monitor = GPUMemoryMonitor(status_frame)
        self.memory_monitor.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Performance tab
        performance_frame = tk.Frame(notebook, bg=GPU_COLORS['background'])
        notebook.add(performance_frame, text="Performance")
        
        # Performance display
        self.performance_display = GPUPerformanceDisplay(performance_frame)
        self.performance_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Validation tab
        validation_frame = tk.Frame(notebook, bg=GPU_COLORS['background'])
        notebook.add(validation_frame, text="GPU Validation")
        
        # Validation controls
        self.validation_controls = GPUValidationControls(validation_frame, self.validation_callback)
        self.validation_controls.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def update_performance_metrics(self, execution_time: float, n_evaluations: int, 
                                 speedup: Optional[float] = None):
        """Update performance metrics display."""
        if hasattr(self, 'performance_display'):
            self.performance_display.update_performance(execution_time, n_evaluations, speedup)
    
    def set_validation_callback(self, callback: Callable):
        """Set the validation callback function."""
        self.validation_callback = callback
        if hasattr(self, 'validation_controls'):
            self.validation_controls.validation_callback = callback