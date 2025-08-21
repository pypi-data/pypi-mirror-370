"""
Algorithm Verification Widget - Clean, Unified GUI
==================================================

This module provides a clean, unified GUI widget for algorithm verification,
replacing the complex enhanced_validation_controls with a streamlined interface.

Classes:
    AlgorithmVerificationWidget: Main verification GUI widget
    VerificationConfigPanel: Configuration input panel
    VerificationProgressPanel: Progress monitoring panel  
    VerificationResultsPanel: Results display panel

Author: PyMBO Development Team
Version: 3.6.6 - Unified Verification Architecture
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import threading
import time
import logging
from typing import Dict, List, Optional, Any, Callable

logger = logging.getLogger(__name__)


class VerificationConfigPanel:
    """Configuration panel for verification parameters."""
    
    def __init__(self, parent_frame: ttk.Frame):
        """Initialize configuration panel.
        
        Args:
            parent_frame: Parent tkinter frame
        """
        self.parent_frame = parent_frame
        self.test_function_vars = {}
        self.algorithm_vars = {}
        
        self._create_config_widgets()
        self._setup_validation()
    
    def _create_config_widgets(self):
        """Create configuration widgets."""
        # Container for collapsible config
        self.config_container = ttk.Frame(self.parent_frame)
        self.config_container.pack(fill="x", padx=5, pady=5)
        
        # Collapsible header with toggle button
        self.config_header = ttk.Frame(self.config_container)
        self.config_header.pack(fill="x")
        
        self.config_expanded = tk.BooleanVar(value=True)
        self.toggle_btn = ttk.Button(
            self.config_header,
            text="🔽 Configuration (Click to collapse/expand)",
            command=self._toggle_config,
            style="Accent.TButton"
        )
        self.toggle_btn.pack(side="left", fill="x", expand=True)
        
        # Main configuration frame (collapsible)
        self.config_frame = ttk.LabelFrame(
            self.config_container,
            text="⚙️ Verification Configuration",
            padding="10"
        )
        self.config_frame.pack(fill="x", pady=(5, 0))
        
        # Create two-column layout
        left_frame = ttk.Frame(self.config_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(self.config_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Test Functions Section
        self._create_test_functions_section(left_frame)
        
        # Algorithms Section
        self._create_algorithms_section(left_frame)
        
        # Parameters Section
        self._create_parameters_section(right_frame)
        
        # Execution Options Section
        self._create_execution_options_section(right_frame)
    
    def _toggle_config(self):
        """Toggle configuration panel visibility."""
        if self.config_expanded.get():
            # Collapse
            self.config_frame.pack_forget()
            self.toggle_btn.config(text="🔽 Configuration (Click to expand)")
            self.config_expanded.set(False)
        else:
            # Expand  
            self.config_frame.pack(fill="x", pady=(5, 0))
            self.toggle_btn.config(text="🔼 Configuration (Click to collapse)")
            self.config_expanded.set(True)
    
    def _create_test_functions_section(self, parent):
        """Create test functions selection section."""
        tf_frame = ttk.LabelFrame(parent, text="📊 Test Functions", padding="5")
        tf_frame.pack(fill="x", pady=(0, 10))
        
        # Load available test functions
        test_functions = self._get_available_test_functions()
        
        # Create checkboxes with descriptions
        for i, (func_name, description) in enumerate(test_functions.items()):
            var = tk.BooleanVar(value=(func_name == "ZDT1"))  # Default ZDT1 selected
            self.test_function_vars[func_name] = var
            
            # Create frame for each function
            func_frame = ttk.Frame(tf_frame)
            func_frame.pack(fill="x", pady=1)
            
            # Checkbox
            cb = ttk.Checkbutton(func_frame, text=func_name, variable=var)
            cb.pack(side="left")
            
            # Description label
            desc_label = ttk.Label(
                func_frame, 
                text=f"- {description}",
                font=("Arial", 9),
                foreground="gray"
            )
            desc_label.pack(side="left", padx=(10, 0))
    
    def _create_algorithms_section(self, parent):
        """Create algorithms selection section."""
        alg_frame = ttk.LabelFrame(parent, text="🚀 Algorithms", padding="5")
        alg_frame.pack(fill="x", pady=(0, 10))
        
        # Available algorithms with descriptions
        algorithms = {
            "This App's MOBO": "Multi-objective Bayesian optimization (default)",
            "Random Search": "Random sampling baseline",
            "NSGA-II": "Non-dominated Sorting Genetic Algorithm II"
        }
        
        for alg_name, description in algorithms.items():
            var = tk.BooleanVar(value=True)  # All selected by default
            self.algorithm_vars[alg_name] = var
            
            # Create frame for each algorithm
            alg_frame_item = ttk.Frame(alg_frame)
            alg_frame_item.pack(fill="x", pady=1)
            
            # Checkbox
            cb = ttk.Checkbutton(alg_frame_item, text=alg_name, variable=var)
            cb.pack(side="left")
            
            # Description label
            desc_label = ttk.Label(
                alg_frame_item,
                text=f"- {description}",
                font=("Arial", 9),
                foreground="gray"
            )
            desc_label.pack(side="left", padx=(10, 0))
    
    def _create_parameters_section(self, parent):
        """Create parameters input section."""
        params_frame = ttk.LabelFrame(parent, text="📋 Parameters", padding="5")
        params_frame.pack(fill="x", pady=(0, 10))
        
        # Grid layout for parameters
        params_grid = ttk.Frame(params_frame)
        params_grid.pack(fill="x")
        
        # Evaluations per run
        ttk.Label(params_grid, text="Evaluations per run:").grid(row=0, column=0, sticky="w", pady=2)
        self.n_evaluations_var = tk.StringVar(value="100")
        eval_spinbox = ttk.Spinbox(
            params_grid,
            from_=20,
            to=1000,
            increment=20,
            textvariable=self.n_evaluations_var,
            width=10
        )
        eval_spinbox.grid(row=0, column=1, padx=(10, 0), pady=2)
        
        # Number of runs
        ttk.Label(params_grid, text="Number of runs:").grid(row=1, column=0, sticky="w", pady=2)
        self.n_runs_var = tk.StringVar(value="10")
        runs_spinbox = ttk.Spinbox(
            params_grid,
            from_=3,
            to=50,
            increment=1,
            textvariable=self.n_runs_var,
            width=10
        )
        runs_spinbox.grid(row=1, column=1, padx=(10, 0), pady=2)
        
        # Random seed
        ttk.Label(params_grid, text="Random seed (optional):").grid(row=2, column=0, sticky="w", pady=2)
        self.seed_var = tk.StringVar(value="")
        seed_entry = ttk.Entry(params_grid, textvariable=self.seed_var, width=10)
        seed_entry.grid(row=2, column=1, padx=(10, 0), pady=2)
    
    def _create_execution_options_section(self, parent):
        """Create execution options section."""
        exec_frame = ttk.LabelFrame(parent, text="⚡ Execution Options", padding="5")
        exec_frame.pack(fill="x")
        
        # Grid layout for options
        options_grid = ttk.Frame(exec_frame)
        options_grid.pack(fill="x")
        
        # Execution mode
        ttk.Label(options_grid, text="Execution mode:").grid(row=0, column=0, sticky="w", pady=2)
        self.execution_mode_var = tk.StringVar(value="Auto")
        mode_combo = ttk.Combobox(
            options_grid,
            textvariable=self.execution_mode_var,
            values=["Auto", "Parallel", "Sequential"],
            state="readonly",
            width=12
        )
        mode_combo.grid(row=0, column=1, padx=(10, 0), pady=2)
        
        # GPU acceleration
        self.gpu_acceleration_var = tk.BooleanVar(value=True)
        gpu_checkbox = ttk.Checkbutton(
            options_grid,
            text="Enable GPU acceleration",
            variable=self.gpu_acceleration_var
        )
        gpu_checkbox.grid(row=1, column=0, columnspan=2, sticky="w", pady=2)
        
        # Statistical tests
        self.statistical_tests_var = tk.BooleanVar(value=True)
        stats_checkbox = ttk.Checkbutton(
            options_grid,
            text="Perform statistical analysis",
            variable=self.statistical_tests_var
        )
        stats_checkbox.grid(row=2, column=0, columnspan=2, sticky="w", pady=2)
    
    def _get_available_test_functions(self) -> Dict[str, str]:
        """Get available test functions with descriptions."""
        # Try to get functions from test function manager
        try:
            from pymbo.core.test_function_manager import get_test_function_manager
            manager = get_test_function_manager()
            
            functions = {}
            for func_name in manager.list_functions():
                try:
                    info = manager.get_function_info(func_name)
                    functions[func_name] = info.description
                except:
                    functions[func_name] = f"{func_name} test function"
                    
            return functions
        except:
            # Fallback to hardcoded functions
            return {
                "ZDT1": "Convex Pareto front, easy convergence",
                "ZDT2": "Non-convex Pareto front",
                "DTLZ2": "Scalable multi-objective function",
                "Branin": "Single-objective function with multiple optima",
                "Hartmann6": "6-dimensional single-objective function"
            }
    
    def _setup_validation(self):
        """Setup input validation."""
        # Validate numeric inputs
        def validate_positive_int(value):
            try:
                val = int(value)
                return val > 0
            except ValueError:
                return False
        
        # Register validation functions
        vcmd_int = (self.parent_frame.register(validate_positive_int), '%P')
        
        # Apply validation (would need to store spinbox references)
        # For now, validation happens in get_config()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration from the panel.
        
        Returns:
            Configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Get selected test functions
        test_functions = [
            name for name, var in self.test_function_vars.items()
            if var.get()
        ]
        
        if not test_functions:
            raise ValueError("Please select at least one test function")
        
        # Get selected algorithms
        algorithms = [
            name for name, var in self.algorithm_vars.items()
            if var.get()
        ]
        
        if not algorithms:
            raise ValueError("Please select at least one algorithm")
        
        # Get numeric parameters
        try:
            n_evaluations = int(self.n_evaluations_var.get())
            if n_evaluations < 10:
                raise ValueError("Number of evaluations must be at least 10")
        except ValueError:
            raise ValueError("Number of evaluations must be a valid integer")
        
        try:
            n_runs = int(self.n_runs_var.get())
            if n_runs < 1:
                raise ValueError("Number of runs must be at least 1")
        except ValueError:
            raise ValueError("Number of runs must be a valid integer")
        
        # Get optional seed
        seed = None
        seed_str = self.seed_var.get().strip()
        if seed_str:
            try:
                seed = int(seed_str)
            except ValueError:
                raise ValueError("Random seed must be a valid integer")
        
        return {
            'test_functions': test_functions,
            'algorithms': algorithms,
            'n_evaluations': n_evaluations,
            'n_runs': n_runs,
            'execution_mode': self.execution_mode_var.get().lower(),
            'gpu_acceleration': self.gpu_acceleration_var.get(),
            'statistical_tests': self.statistical_tests_var.get(),
            'seed': seed
        }
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all configuration controls.
        
        Args:
            enabled: Whether to enable controls
        """
        state = "normal" if enabled else "disabled"
        
        # This would disable all child widgets
        # For brevity, showing concept - full implementation would recurse through all widgets
        def set_widget_state(widget, state):
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass  # Some widgets don't support state
            
            for child in widget.winfo_children():
                set_widget_state(child, state)
        
        set_widget_state(self.config_frame, state)


class VerificationProgressPanel:
    """Progress monitoring panel for verification runs."""
    
    def __init__(self, parent_frame: ttk.Frame):
        """Initialize progress panel.
        
        Args:
            parent_frame: Parent tkinter frame
        """
        self.parent_frame = parent_frame
        self.algorithm_progress_bars = {}
        self.algorithm_labels = {}
        self.start_time = None
        
        self._create_progress_widgets()
    
    def _create_progress_widgets(self):
        """Create progress monitoring widgets."""
        self.progress_frame = ttk.LabelFrame(
            self.parent_frame,
            text="📊 Verification Progress",
            padding="10"
        )
        self.progress_frame.pack(fill="x", padx=5, pady=5)
        
        # Overall progress section
        overall_frame = ttk.Frame(self.progress_frame)
        overall_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(overall_frame, text="Overall Progress:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        progress_row = ttk.Frame(overall_frame)
        progress_row.pack(fill="x", pady=2)
        
        self.overall_progress = ttk.Progressbar(
            progress_row,
            mode='determinate',
            length=300
        )
        self.overall_progress.pack(side="left", fill="x", expand=True)
        
        self.overall_label = ttk.Label(progress_row, text="0%", width=10)
        self.overall_label.pack(side="right", padx=(10, 0))
        
        # Status and timing info
        info_frame = ttk.Frame(self.progress_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.status_label = ttk.Label(
            info_frame,
            text="Ready to start verification",
            font=("Arial", 9)
        )
        self.status_label.pack(side="left")
        
        self.timing_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 9)
        )
        self.timing_label.pack(side="right")
        
        # Individual algorithm progress (created dynamically)
        self.algorithms_frame = ttk.Frame(self.progress_frame)
        self.algorithms_frame.pack(fill="x")
    
    def start_monitoring(self, algorithms: List[str], total_tasks: int):
        """Start progress monitoring.
        
        Args:
            algorithms: List of algorithm names
            total_tasks: Total number of tasks to complete
        """
        self.start_time = time.time()
        self.total_tasks = total_tasks
        self.completed_tasks = 0
        
        # Clear existing algorithm progress bars
        for widget in self.algorithms_frame.winfo_children():
            widget.destroy()
        
        self.algorithm_progress_bars.clear()
        self.algorithm_labels.clear()
        
        # Create progress bars for each algorithm
        if len(algorithms) > 1:  # Only show individual progress if multiple algorithms
            ttk.Label(
                self.algorithms_frame,
                text="Algorithm Progress:",
                font=("Arial", 10, "bold")
            ).pack(anchor="w", pady=(10, 5))
            
            for algorithm in algorithms:
                alg_frame = ttk.Frame(self.algorithms_frame)
                alg_frame.pack(fill="x", pady=1)
                
                # Algorithm name
                name_label = ttk.Label(alg_frame, text=f"{algorithm}:", width=20, anchor="w")
                name_label.pack(side="left")
                
                # Progress bar
                progress_bar = ttk.Progressbar(
                    alg_frame,
                    mode='determinate',
                    length=200
                )
                progress_bar.pack(side="left", padx=(5, 10), fill="x", expand=True)
                
                # Status label
                status_label = ttk.Label(alg_frame, text="Waiting...", width=15)
                status_label.pack(side="right")
                
                self.algorithm_progress_bars[algorithm] = progress_bar
                self.algorithm_labels[algorithm] = status_label
        
        # Reset overall progress
        self.overall_progress['value'] = 0
        self.overall_label.config(text="0%")
        self.status_label.config(text="Starting verification...")
        self.timing_label.config(text="")
    
    def update_progress(self, completed_tasks: int, current_task: str = ""):
        """Update overall progress.
        
        Args:
            completed_tasks: Number of completed tasks
            current_task: Description of current task
        """
        self.completed_tasks = completed_tasks
        
        # Update overall progress
        if self.total_tasks > 0:
            progress_percent = (completed_tasks / self.total_tasks) * 100
            self.overall_progress['value'] = progress_percent
            self.overall_label.config(text=f"{progress_percent:.0f}%")
        
        # Update status
        if current_task:
            self.status_label.config(text=f"Running: {current_task}")
        
        # Update timing
        if self.start_time:
            elapsed = time.time() - self.start_time
            if completed_tasks > 0:
                avg_time = elapsed / completed_tasks
                remaining = (self.total_tasks - completed_tasks) * avg_time
                eta_text = f"ETA: {int(remaining // 60):02d}:{int(remaining % 60):02d}"
            else:
                eta_text = "ETA: Calculating..."
            
            elapsed_text = f"Elapsed: {int(elapsed // 60):02d}:{int(elapsed % 60):02d}"
            self.timing_label.config(text=f"{elapsed_text} | {eta_text}")
    
    def update_algorithm_progress(self, algorithm: str, progress: float, status: str = ""):
        """Update progress for specific algorithm.
        
        Args:
            algorithm: Algorithm name
            progress: Progress as percentage (0-100)
            status: Status message
        """
        if algorithm in self.algorithm_progress_bars:
            self.algorithm_progress_bars[algorithm]['value'] = progress
            
            if status:
                self.algorithm_labels[algorithm].config(text=status)
            else:
                self.algorithm_labels[algorithm].config(text=f"{progress:.0f}%")
    
    def complete_monitoring(self, success: bool = True):
        """Complete progress monitoring.
        
        Args:
            success: Whether verification completed successfully
        """
        self.overall_progress['value'] = 100
        self.overall_label.config(text="100%")
        
        if success:
            self.status_label.config(text="✅ Verification completed successfully")
        else:
            self.status_label.config(text="❌ Verification failed or was stopped")
        
        # Mark all algorithms as complete
        for algorithm in self.algorithm_labels:
            if success:
                self.algorithm_labels[algorithm].config(text="✅ Complete")
            else:
                self.algorithm_labels[algorithm].config(text="❌ Stopped")
        
        # Final timing
        if self.start_time:
            total_time = time.time() - self.start_time
            total_text = f"Total time: {int(total_time // 60):02d}:{int(total_time % 60):02d}"
            self.timing_label.config(text=total_text)


class VerificationResultsPanel:
    """Results display panel with integrated plots and statistics."""
    
    def __init__(self, parent_frame: ttk.Frame):
        """Initialize results panel.
        
        Args:
            parent_frame: Parent tkinter frame
        """
        self.parent_frame = parent_frame
        self.current_results = None
        
        self._create_results_widgets()
    
    def _create_results_widgets(self):
        """Create results display widgets."""
        self.results_frame = ttk.LabelFrame(
            self.parent_frame,
            text="📈 Verification Results",
            padding="10"
        )
        self.results_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create notebook for tabbed results
        self.results_notebook = ttk.Notebook(self.results_frame)
        self.results_notebook.pack(fill="both", expand=True)
        
        # Summary tab
        self._create_summary_tab()
        
        # Plots tab
        self._create_plots_tab()
        
        # Statistics tab
        self._create_statistics_tab()
        
        # Export controls
        self._create_export_controls()
    
    def _create_summary_tab(self):
        """Create summary results tab."""
        self.summary_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.summary_frame, text="📋 Summary")
        
        # Summary table
        self.summary_tree = ttk.Treeview(
            self.summary_frame,
            columns=("algorithm", "test_function", "final_hv", "std", "rank"),
            show="headings",
            height=10
        )
        
        # Configure columns
        self.summary_tree.heading("algorithm", text="Algorithm")
        self.summary_tree.heading("test_function", text="Test Function")
        self.summary_tree.heading("final_hv", text="Final Hypervolume")
        self.summary_tree.heading("std", text="Std Dev")
        self.summary_tree.heading("rank", text="Rank")
        
        self.summary_tree.column("algorithm", width=150)
        self.summary_tree.column("test_function", width=120)
        self.summary_tree.column("final_hv", width=120)
        self.summary_tree.column("std", width=100)
        self.summary_tree.column("rank", width=60)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(self.summary_frame, orient="vertical", command=self.summary_tree.yview)
        h_scroll = ttk.Scrollbar(self.summary_frame, orient="horizontal", command=self.summary_tree.xview)
        self.summary_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack tree and scrollbars
        self.summary_tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")
        
        # Initially show placeholder
        self._show_summary_placeholder()
    
    def _create_plots_tab(self):
        """Create plots display tab."""
        self.plots_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.plots_frame, text="📊 Plots")
        
        # Create matplotlib figure with maximum sizing for verification plots
        self.fig = Figure(figsize=(20, 16), facecolor="white", dpi=80)
        self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
        
        # Configure canvas to take maximum available space
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Make sure the frame itself can expand
        self.plots_frame.pack_propagate(False)
        
        # Toolbar with full-screen button
        toolbar_frame = ttk.Frame(self.plots_frame)
        toolbar_frame.pack(fill="x")
        
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.pack(side="left")
        
        # Full-screen plot button
        self.fullscreen_btn = ttk.Button(
            toolbar_frame,
            text="🔍 Full Screen Plots",
            command=self._open_fullscreen_plots
        )
        self.fullscreen_btn.pack(side="right", padx=(10, 0))
        
        toolbar.update()
        
        # Initially show placeholder
        self._show_plots_placeholder()
    
    def _create_statistics_tab(self):
        """Create detailed statistics tab."""
        self.statistics_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.statistics_frame, text="📊 Statistics")
        
        # Text widget for detailed statistics
        self.stats_text = tk.Text(
            self.statistics_frame,
            font=("Consolas", 10),
            wrap=tk.WORD,
            bg="#f8f9fa",
            fg="#212529"
        )
        
        stats_scroll = ttk.Scrollbar(self.statistics_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        self.stats_text.pack(side="left", fill="both", expand=True)
        stats_scroll.pack(side="right", fill="y")
        
        # Initially show placeholder
        self.stats_text.insert("1.0", "Run verification to see detailed statistics...")
        self.stats_text.config(state="disabled")
    
    def _create_export_controls(self):
        """Create export controls."""
        export_frame = ttk.Frame(self.results_frame)
        export_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(export_frame, text="Export Results:", font=("Arial", 10, "bold")).pack(side="left")
        
        self.export_json_btn = ttk.Button(
            export_frame,
            text="📄 Export JSON",
            command=self._export_json,
            state="disabled"
        )
        self.export_json_btn.pack(side="right", padx=2)
        
        self.export_csv_btn = ttk.Button(
            export_frame,
            text="📊 Export CSV",
            command=self._export_csv,
            state="disabled"
        )
        self.export_csv_btn.pack(side="right", padx=2)
    
    def _show_summary_placeholder(self):
        """Show placeholder in summary table."""
        self.summary_tree.insert("", "end", values=(
            "Run verification to see results...", "", "", "", ""
        ))
    
    def _show_plots_placeholder(self):
        """Show placeholder in plots."""
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, "Run verification to see plots",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=14, color="gray", style='italic')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.canvas.draw()
    
    def _open_fullscreen_plots(self):
        """Open plots in a full-screen window."""
        if not self.current_results:
            messagebox.showwarning("No Results", "No results to display in full screen.")
            return
        
        # Create full-screen window
        fullscreen_window = tk.Toplevel()
        fullscreen_window.title("Algorithm Verification - Full Screen Plots")
        fullscreen_window.state('zoomed')  # Maximize on Windows
        
        # Create massive figure for full screen
        fullscreen_fig = Figure(figsize=(24, 18), facecolor="white", dpi=100)
        fullscreen_canvas = FigureCanvasTkAgg(fullscreen_fig, fullscreen_window)
        fullscreen_canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add toolbar to full-screen window
        fullscreen_toolbar = NavigationToolbar2Tk(fullscreen_canvas, fullscreen_window)
        fullscreen_toolbar.update()
        
        # Recreate plots in full-screen figure
        self._create_fullscreen_plots(fullscreen_fig, self.current_results)
        fullscreen_canvas.draw()
        
        # Close button
        close_frame = ttk.Frame(fullscreen_window)
        close_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(
            close_frame, 
            text="✕ Close Full Screen", 
            command=fullscreen_window.destroy
        ).pack(side="right", padx=20)
    
    def _create_fullscreen_plots(self, fig, results):
        """Create plots optimized for full-screen display."""
        fig.clear()
        
        try:
            test_functions = list(results.hypervolume_progression.keys())
            n_plots = len(test_functions)
            
            if n_plots == 0:
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, "No results to display", 
                       ha="center", va="center", transform=ax.transAxes,
                       fontsize=24, color="gray")
                return
            
            # Optimal layout for full-screen
            if n_plots == 1:
                rows, cols = 1, 1
            elif n_plots == 2:
                rows, cols = 1, 2
            elif n_plots == 3:
                rows, cols = 1, 3
            elif n_plots == 4:
                rows, cols = 2, 2
            elif n_plots <= 6:
                rows, cols = 2, 3
            else:
                rows, cols = 3, 3
            
            for i, test_func in enumerate(test_functions):
                ax = fig.add_subplot(rows, cols, i + 1)
                
                algorithms_data = results.hypervolume_progression[test_func]
                colors = plt.cm.Set1(np.linspace(0, 1, len(algorithms_data)))
                
                for (alg_name, hv_data), color in zip(algorithms_data.items(), colors):
                    if len(hv_data['mean']) > 0:
                        evaluations = hv_data['evaluations']
                        mean_values = hv_data['mean']
                        std_values = hv_data['std']
                        
                        # Plot with larger markers for full-screen
                        ax.plot(evaluations, mean_values, label=alg_name, 
                               color=color, linewidth=3, marker='o', markersize=6)
                        
                        if len(std_values) == len(mean_values):
                            lower = np.array(mean_values) - np.array(std_values)
                            upper = np.array(mean_values) + np.array(std_values)
                            ax.fill_between(evaluations, lower, upper, alpha=0.2, color=color)
                
                # Full-screen optimized formatting
                ax.set_title(f"Hypervolume Progression - {test_func}", fontsize=20, fontweight='bold', pad=25)
                ax.set_xlabel("Function Evaluations", fontsize=16)
                ax.set_ylabel("Hypervolume", fontsize=16)
                ax.legend(fontsize=14, loc='best')
                ax.grid(True, alpha=0.3)
                ax.tick_params(axis='both', which='major', labelsize=14, pad=8)
                ax.margins(x=0.02, y=0.05)
            
            # Maximum spacing for full-screen
            fig.tight_layout(pad=6.0, w_pad=5.0, h_pad=6.0)
            
        except Exception as e:
            logger.error(f"Error creating full-screen plots: {e}")
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error displaying plots: {str(e)}", 
                   ha="center", va="center", transform=ax.transAxes,
                   fontsize=16, color="red")
    
    def display_results(self, results):
        """Display verification results.
        
        Args:
            results: VerificationResults object
        """
        self.current_results = results
        
        # Update summary table
        self._update_summary_table(results)
        
        # Update plots
        self._update_plots(results)
        
        # Update statistics
        self._update_statistics(results)
        
        # Enable export buttons
        self.export_json_btn.config(state="normal")
        self.export_csv_btn.config(state="normal")
    
    def _update_summary_table(self, results):
        """Update the summary table with results."""
        # Clear existing data
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)
        
        # Add results data
        try:
            summary_data = []
            
            for test_func, algorithms_data in results.statistical_analysis.get('final_hypervolumes', {}).items():
                for algorithm, stats in algorithms_data.items():
                    summary_data.append({
                        'algorithm': algorithm,
                        'test_function': test_func,
                        'final_hv': stats['mean'],
                        'std': stats['std'],
                    })
            
            # Sort by final hypervolume (descending)
            summary_data.sort(key=lambda x: x['final_hv'], reverse=True)
            
            # Add rank and insert into tree
            for rank, data in enumerate(summary_data, 1):
                self.summary_tree.insert("", "end", values=(
                    data['algorithm'],
                    data['test_function'],
                    f"{data['final_hv']:.6f}",
                    f"{data['std']:.6f}",
                    str(rank)
                ))
                
        except Exception as e:
            logger.error(f"Error updating summary table: {e}")
            self.summary_tree.insert("", "end", values=(
                "Error loading results", "", "", "", ""
            ))
    
    def _update_plots(self, results):
        """Update the plots with results."""
        self.fig.clear()
        
        try:
            # Create subplots based on number of test functions
            test_functions = list(results.hypervolume_progression.keys())
            n_plots = len(test_functions)
            
            if n_plots == 0:
                self._show_plots_placeholder()
                return
            
            # Determine optimal subplot layout with generous spacing
            if n_plots == 1:
                rows, cols = 1, 1
            elif n_plots == 2:
                rows, cols = 1, 2
            elif n_plots == 3:
                rows, cols = 1, 3
            elif n_plots == 4:
                rows, cols = 2, 2
            elif n_plots <= 6:
                rows, cols = 2, 3
            else:
                rows, cols = 3, 3
            
            # Hypervolume progression plots
            for i, test_func in enumerate(test_functions):
                ax = self.fig.add_subplot(rows, cols, i + 1)
                
                algorithms_data = results.hypervolume_progression[test_func]
                colors = plt.cm.Set1(np.linspace(0, 1, len(algorithms_data)))
                
                for (alg_name, hv_data), color in zip(algorithms_data.items(), colors):
                    if len(hv_data['mean']) > 0:
                        evaluations = hv_data['evaluations']
                        mean_values = hv_data['mean']
                        std_values = hv_data['std']
                        
                        # Plot mean line
                        ax.plot(evaluations, mean_values, label=alg_name, 
                               color=color, linewidth=2, marker='o', markersize=3)
                        
                        # Plot confidence interval
                        if len(std_values) == len(mean_values):
                            lower = np.array(mean_values) - np.array(std_values)
                            upper = np.array(mean_values) + np.array(std_values)
                            ax.fill_between(evaluations, lower, upper, alpha=0.2, color=color)
                
                ax.set_title(f"Hypervolume Progression - {test_func}", fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel("Function Evaluations", fontsize=14)
                ax.set_ylabel("Hypervolume", fontsize=14)
                ax.legend(fontsize=12, loc='best')
                ax.grid(True, alpha=0.3)
                
                # Improve tick formatting with better spacing
                ax.tick_params(axis='both', which='major', labelsize=12, pad=5)
                
                # Add some margin around the plot data
                ax.margins(x=0.02, y=0.05)
            
            # Adjust layout with maximum generous spacing
            self.fig.tight_layout(pad=5.0, w_pad=4.0, h_pad=5.0)
            
        except Exception as e:
            logger.error(f"Error updating plots: {e}")
            self.fig.clear()
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error displaying plots: {str(e)}", 
                    ha="center", va="center", transform=ax.transAxes,
                    fontsize=12, color="red")
        
        self.canvas.draw()
    
    def _update_statistics(self, results):
        """Update the statistics display."""
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", tk.END)
        
        try:
            stats_content = []
            stats_content.append("🔬 ALGORITHM VERIFICATION STATISTICS")
            stats_content.append("=" * 50)
            stats_content.append("")
            
            # Configuration info
            config = results.config
            stats_content.append("📋 Configuration:")
            stats_content.append(f"  Test Functions: {', '.join(config.test_functions)}")
            stats_content.append(f"  Algorithms: {', '.join(config.algorithms)}")
            stats_content.append(f"  Evaluations per run: {config.n_evaluations}")
            stats_content.append(f"  Number of runs: {config.n_runs}")
            stats_content.append(f"  Execution mode: {config.execution_mode}")
            stats_content.append("")
            
            # Execution metadata
            if results.execution_metadata:
                metadata = results.execution_metadata
                stats_content.append("⚡ Execution Summary:")
                stats_content.append(f"  Mode used: {metadata.get('execution_mode', 'Unknown')}")
                stats_content.append(f"  Total time: {metadata.get('execution_time', 0):.2f} seconds")
                stats_content.append(f"  GPU acceleration: {metadata.get('gpu_acceleration', False)}")
                stats_content.append("")
            
            # Statistical analysis
            if results.statistical_analysis:
                stats_content.append("📊 Final Results Summary:")
                stats_content.append("-" * 30)
                
                for test_func, algorithms_data in results.statistical_analysis.get('final_hypervolumes', {}).items():
                    stats_content.append(f"\n{test_func}:")
                    
                    # Sort algorithms by performance
                    sorted_algs = sorted(algorithms_data.items(), 
                                       key=lambda x: x[1]['mean'], reverse=True)
                    
                    for rank, (alg, stats) in enumerate(sorted_algs, 1):
                        stats_content.append(f"  {rank}. {alg}: {stats['mean']:.6f} ± {stats['std']:.6f}")
            
            # Add content to text widget
            content = "\n".join(stats_content)
            self.stats_text.insert("1.0", content)
            
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
            self.stats_text.insert("1.0", f"Error loading statistics: {str(e)}")
        
        self.stats_text.config(state="disabled")
    
    def _export_json(self):
        """Export results as JSON."""
        if not self.current_results:
            messagebox.showwarning("No Results", "No results to export.")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Export Results as JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.current_results.export_results(filepath, format='json')
                messagebox.showinfo("Export Complete", f"Results exported to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def _export_csv(self):
        """Export results as CSV."""
        if not self.current_results:
            messagebox.showwarning("No Results", "No results to export.")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Export Results as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.current_results.export_results(filepath, format='csv')
                messagebox.showinfo("Export Complete", f"Results exported to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")


class AlgorithmVerificationWidget:
    """Main algorithm verification widget."""
    
    def __init__(self, parent_frame: ttk.Frame, controller=None):
        """Initialize the verification widget.
        
        Args:
            parent_frame: Parent tkinter frame
            controller: Controller instance for integration
        """
        self.parent_frame = parent_frame
        self.controller = controller
        self.verification_thread = None
        self.is_running = False
        
        # Create main frame
        self.main_frame = ttk.Frame(parent_frame)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create components
        self._create_header()
        self.config_panel = VerificationConfigPanel(self.main_frame)
        self._create_control_buttons()
        self.progress_panel = VerificationProgressPanel(self.main_frame)
        self.results_panel = VerificationResultsPanel(self.main_frame)
        
        logger.info("AlgorithmVerificationWidget initialized")
    
    def _create_header(self):
        """Create header section."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", padx=5, pady=(5, 10))
        
        title_label = ttk.Label(
            header_frame,
            text="🔬 Algorithm Verification System",
            font=("Arial", 16, "bold")
        )
        title_label.pack(side="left")
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Compare optimization algorithms on benchmark test functions",
            font=("Arial", 10),
            foreground="gray"
        )
        subtitle_label.pack(side="left", padx=(20, 0))
    
    def _create_control_buttons(self):
        """Create control buttons."""
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill="x", padx=5, pady=10)
        
        # Main action buttons
        self.run_verification_btn = ttk.Button(
            controls_frame,
            text="🚀 Run Verification",
            command=self._run_verification,
            style="Accent.TButton"
        )
        self.run_verification_btn.pack(side="left", padx=(0, 10))
        
        self.quick_test_btn = ttk.Button(
            controls_frame,
            text="⚡ Quick Test",
            command=self._run_quick_test
        )
        self.quick_test_btn.pack(side="left", padx=(0, 10))
        
        # Control buttons
        self.stop_btn = ttk.Button(
            controls_frame,
            text="⏹ Stop",
            command=self._stop_verification,
            state="disabled"
        )
        self.stop_btn.pack(side="right", padx=(10, 0))
        
        self.clear_btn = ttk.Button(
            controls_frame,
            text="🗑 Clear Results",
            command=self._clear_results
        )
        self.clear_btn.pack(side="right", padx=(10, 0))
    
    def _run_verification(self):
        """Run full verification."""
        try:
            config = self.config_panel.get_config()
            self._start_verification(config, quick=False)
        except ValueError as e:
            messagebox.showerror("Configuration Error", str(e))
    
    def _run_quick_test(self):
        """Run quick test verification."""
        # Override config for quick test
        config = {
            'test_functions': ['ZDT1'],
            'algorithms': ["This App's MOBO", "Random Search"],
            'n_evaluations': 50,
            'n_runs': 3,
            'execution_mode': 'auto',
            'gpu_acceleration': True,
            'statistical_tests': True,
            'seed': 42
        }
        self._start_verification(config, quick=True)
    
    def _start_verification(self, config: Dict[str, Any], quick: bool = False):
        """Start verification with given configuration."""
        if self.is_running:
            messagebox.showwarning("Already Running", "Verification is already in progress.")
            return
        
        # Set running state
        self.is_running = True
        self._set_controls_enabled(False)
        
        # Start progress monitoring
        total_tasks = len(config['test_functions']) * len(config['algorithms'])
        self.progress_panel.start_monitoring(config['algorithms'], total_tasks)
        
        # Start verification thread
        self.verification_thread = threading.Thread(
            target=self._verification_worker,
            args=(config, quick),
            daemon=True
        )
        self.verification_thread.start()
    
    def _verification_worker(self, config: Dict[str, Any], quick: bool):
        """Worker thread for verification."""
        try:
            # Import verification engine
            from pymbo.core.algorithm_verifier import AlgorithmVerifier, VerificationConfig
            
            # Create verifier
            verifier = AlgorithmVerifier(
                gpu_acceleration=config['gpu_acceleration']
            )
            
            # Create verification config
            def progress_callback(progress, task_description):
                # Update progress in main thread
                completed_tasks = int(progress * len(config['test_functions']) * len(config['algorithms']))
                self.main_frame.after(0, 
                    lambda: self.progress_panel.update_progress(completed_tasks, task_description))
            
            verification_config = VerificationConfig(
                test_functions=config['test_functions'],
                algorithms=config['algorithms'],
                n_evaluations=config['n_evaluations'],
                n_runs=config['n_runs'],
                execution_mode=config['execution_mode'],
                gpu_acceleration=config['gpu_acceleration'],
                seed=config['seed'],
                statistical_tests=config['statistical_tests'],
                progress_callback=progress_callback
            )
            
            # Run verification
            results = verifier.verify_algorithms(verification_config)
            
            # Update GUI in main thread
            self.main_frame.after(0, lambda: self._verification_completed(results, None))
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            error_msg = str(e)  # Capture error message in local scope
            self.main_frame.after(0, lambda: self._verification_completed(None, error_msg))
    
    def _verification_completed(self, results, error):
        """Handle verification completion."""
        self.is_running = False
        self._set_controls_enabled(True)
        
        if error:
            self.progress_panel.complete_monitoring(success=False)
            messagebox.showerror("Verification Failed", f"Verification failed:\n{error}")
        else:
            self.progress_panel.complete_monitoring(success=True)
            self.results_panel.display_results(results)
            messagebox.showinfo("Verification Complete", 
                              "Algorithm verification completed successfully!\n"
                              "Check the Results tab for detailed analysis.")
    
    def _stop_verification(self):
        """Stop current verification."""
        if self.is_running:
            # Note: Proper thread termination would require more sophisticated handling
            self.is_running = False
            self.progress_panel.complete_monitoring(success=False)
            self._set_controls_enabled(True)
            messagebox.showinfo("Verification Stopped", "Verification has been stopped.")
    
    def _clear_results(self):
        """Clear current results."""
        # Clear results panel
        self.results_panel._show_summary_placeholder()
        self.results_panel._show_plots_placeholder()
        
        self.results_panel.stats_text.config(state="normal")
        self.results_panel.stats_text.delete("1.0", tk.END)
        self.results_panel.stats_text.insert("1.0", "Run verification to see detailed statistics...")
        self.results_panel.stats_text.config(state="disabled")
        
        # Disable export buttons
        self.results_panel.export_json_btn.config(state="disabled")
        self.results_panel.export_csv_btn.config(state="disabled")
        
        self.results_panel.current_results = None
    
    def _set_controls_enabled(self, enabled: bool):
        """Enable or disable control buttons."""
        state = "normal" if enabled else "disabled"
        
        self.run_verification_btn.config(state=state)
        self.quick_test_btn.config(state=state)
        self.clear_btn.config(state=state)
        
        # Stop button is opposite
        self.stop_btn.config(state="disabled" if enabled else "normal")
        
        # Configuration panel
        self.config_panel.set_enabled(enabled)