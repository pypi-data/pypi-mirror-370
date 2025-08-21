#!/usr/bin/env python3
"""
Parallel Optimization Controls
=============================

This module provides GUI controls for the new parallel optimization capabilities
in PyMBO. It allows users to access benchmarking, what-if analysis, and parallel
data loading features through an intuitive interface.

Key Features:
- Strategy benchmarking controls
- What-if analysis scenario builder
- Parallel data loading options
- Performance monitoring and statistics
- Cache management controls

Author: Multi-Objective Optimization Laboratory
Version: 3.6.6 - Hybrid Architecture
"""

import logging
import threading
from typing import Any, Dict, List, Optional, Tuple
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

logger = logging.getLogger(__name__)


class ParallelOptimizationControls:
    """GUI controls for parallel optimization capabilities."""
    
    def __init__(self, parent_frame: ttk.Frame, controller: Any):
        """
        Initialize parallel optimization controls.
        
        Args:
            parent_frame: Parent tkinter frame
            controller: Controller instance with orchestrator
        """
        self.parent_frame = parent_frame
        self.controller = controller
        
        # Create main frame
        self.main_frame = ttk.LabelFrame(
            parent_frame, 
            text="🚀 Parallel Optimization", 
            padding="10"
        )
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Initialize GUI components
        self._create_widgets()
        self._setup_layout()
        
        logger.info("Parallel optimization controls initialized")
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        
        # ====================================================================================
        # Strategy Benchmarking Section
        # ====================================================================================
        
        self.benchmark_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Strategy Benchmarking", 
            padding="5"
        )
        
        # Strategy selection
        ttk.Label(self.benchmark_frame, text="Strategies to Compare:").pack(anchor="w")
        self.strategy_frame = ttk.Frame(self.benchmark_frame)
        self.strategy_frame.pack(fill="x", pady=5)
        
        # Strategy checkboxes
        self.strategy_vars = {}
        strategies = [
            ("EHVI", "ehvi", "Expected Hypervolume Improvement"),
            ("EI", "ei", "Expected Improvement"),
            ("Random", "random", "Random sampling baseline"),
            ("Weighted", "weighted", "Weighted scalarization")
        ]
        
        for display_name, strategy_key, tooltip in strategies:
            var = tk.BooleanVar(value=True if strategy_key in ["ehvi", "ei"] else False)
            self.strategy_vars[strategy_key] = var
            
            cb = ttk.Checkbutton(
                self.strategy_frame, 
                text=display_name, 
                variable=var
            )
            cb.pack(side="left", padx=5)
            
            # Add tooltip (simplified version)
            self._add_tooltip(cb, tooltip)
        
        # Number of suggestions
        suggestion_frame = ttk.Frame(self.benchmark_frame)
        suggestion_frame.pack(fill="x", pady=5)
        
        ttk.Label(suggestion_frame, text="Suggestions per strategy:").pack(side="left")
        self.n_suggestions_var = tk.StringVar(value="10")
        suggestions_spinbox = ttk.Spinbox(
            suggestion_frame,
            from_=1,
            to=100,
            textvariable=self.n_suggestions_var,
            width=10
        )
        suggestions_spinbox.pack(side="left", padx=5)
        
        # Parallel execution checkbox
        self.parallel_benchmark_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.benchmark_frame,
            text="Run in parallel (faster)",
            variable=self.parallel_benchmark_var
        ).pack(anchor="w", pady=5)
        
        # Benchmark button
        self.benchmark_button = ttk.Button(
            self.benchmark_frame,
            text="🏁 Run Benchmark",
            command=self._run_benchmark
        )
        self.benchmark_button.pack(pady=5)
        
        # ====================================================================================
        # What-If Analysis Section
        # ====================================================================================
        
        self.whatif_frame = ttk.LabelFrame(
            self.main_frame, 
            text="What-If Analysis", 
            padding="5"
        )
        
        # Scenario builder
        ttk.Label(self.whatif_frame, text="Analysis Scenarios:").pack(anchor="w")
        
        # Scenario listbox with scrollbar
        scenario_list_frame = ttk.Frame(self.whatif_frame)
        scenario_list_frame.pack(fill="both", expand=True, pady=5)
        
        self.scenario_listbox = tk.Listbox(scenario_list_frame, height=4)
        scenario_scrollbar = ttk.Scrollbar(scenario_list_frame, orient="vertical")
        self.scenario_listbox.config(yscrollcommand=scenario_scrollbar.set)
        scenario_scrollbar.config(command=self.scenario_listbox.yview)
        
        self.scenario_listbox.pack(side="left", fill="both", expand=True)
        scenario_scrollbar.pack(side="right", fill="y")
        
        # Default scenarios
        default_scenarios = [
            "Conservative (5 suggestions, EI strategy)",
            "Aggressive (15 suggestions, EHVI strategy)",
            "Random Baseline (10 suggestions, Random strategy)"
        ]
        for scenario in default_scenarios:
            self.scenario_listbox.insert(tk.END, scenario)
        
        # Scenario control buttons
        scenario_button_frame = ttk.Frame(self.whatif_frame)
        scenario_button_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            scenario_button_frame,
            text="Add Scenario",
            command=self._add_scenario
        ).pack(side="left", padx=2)
        
        ttk.Button(
            scenario_button_frame,
            text="Remove Selected",
            command=self._remove_scenario
        ).pack(side="left", padx=2)
        
        # What-if execution controls
        self.parallel_whatif_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.whatif_frame,
            text="Run scenarios in parallel",
            variable=self.parallel_whatif_var
        ).pack(anchor="w", pady=5)
        
        self.whatif_button = ttk.Button(
            self.whatif_frame,
            text="🔮 Run What-If Analysis",
            command=self._run_whatif
        )
        self.whatif_button.pack(pady=5)
        
        # ====================================================================================
        # Parallel Data Loading Section
        # ====================================================================================
        
        self.data_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Parallel Data Loading", 
            padding="5"
        )
        
        # Chunk size setting
        chunk_frame = ttk.Frame(self.data_frame)
        chunk_frame.pack(fill="x", pady=5)
        
        ttk.Label(chunk_frame, text="Chunk size for parallel processing:").pack(side="left")
        self.chunk_size_var = tk.StringVar(value="1000")
        chunk_spinbox = ttk.Spinbox(
            chunk_frame,
            from_=100,
            to=10000,
            increment=100,
            textvariable=self.chunk_size_var,
            width=10
        )
        chunk_spinbox.pack(side="left", padx=5)
        
        # Load data button
        self.load_data_button = ttk.Button(
            self.data_frame,
            text="📊 Load Large Dataset (Parallel)",
            command=self._load_large_dataset
        )
        self.load_data_button.pack(pady=5)
        
        # ====================================================================================
        # Performance Monitoring Section
        # ====================================================================================
        
        self.perf_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Performance & Settings", 
            padding="5"
        )
        
        # Statistics display
        self.stats_text = tk.Text(self.perf_frame, height=4, width=50)
        self.stats_text.pack(fill="both", expand=True, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(self.perf_frame)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(
            button_frame,
            text="📊 Update Stats",
            command=self._update_stats
        ).pack(side="left", padx=2)
        
        ttk.Button(
            button_frame,
            text="🗑️ Clear Cache",
            command=self._clear_cache
        ).pack(side="left", padx=2)
        
        # Parallel enable/disable
        self.parallel_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            self.perf_frame,
            text="Enable parallel optimization",
            variable=self.parallel_enabled_var,
            command=self._toggle_parallel
        ).pack(anchor="w", pady=5)
        
        # Results display area
        self.results_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Results", 
            padding="5"
        )
        
        self.results_text = tk.Text(self.results_frame, height=8, width=60)
        results_scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical")
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        results_scrollbar.config(command=self.results_text.yview)
        
        self.results_text.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
    
    def _setup_layout(self):
        """Setup the layout of all widgets."""
        self.benchmark_frame.pack(fill="x", pady=5)
        self.whatif_frame.pack(fill="x", pady=5)
        self.data_frame.pack(fill="x", pady=5)
        self.perf_frame.pack(fill="x", pady=5)
        self.results_frame.pack(fill="both", expand=True, pady=5)
        
        # Initialize stats
        self._update_stats()
    
    def _add_tooltip(self, widget, text):
        """Add a simple tooltip to a widget."""
        def enter(event):
            # Simple tooltip implementation - could be enhanced
            pass
        
        def leave(event):
            pass
        
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
    
    def _run_benchmark(self):
        """Run strategy benchmarking."""
        try:
            # Get selected strategies
            selected_strategies = [
                strategy for strategy, var in self.strategy_vars.items() 
                if var.get()
            ]
            
            if not selected_strategies:
                messagebox.showwarning("No Strategies", "Please select at least one strategy to benchmark.")
                return
            
            # Get parameters
            try:
                n_suggestions = int(self.n_suggestions_var.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Number of suggestions must be an integer.")
                return
            
            parallel = self.parallel_benchmark_var.get()
            
            # Show progress
            self._log_result(f"Starting benchmark: {selected_strategies} with {n_suggestions} suggestions each")
            self._log_result("This may take a few minutes...")
            
            # Run in separate thread
            thread = threading.Thread(
                target=self._run_benchmark_thread,
                args=(selected_strategies, n_suggestions, parallel)
            )
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error starting benchmark: {e}")
            messagebox.showerror("Benchmark Error", f"Failed to start benchmark: {str(e)}")
    
    def _run_benchmark_thread(self, strategies, n_suggestions, parallel):
        """Run benchmarking in separate thread."""
        try:
            # Disable button during execution
            self.benchmark_button.config(state="disabled")
            
            # Run benchmark
            results = self.controller.benchmark_optimization_strategies(
                strategies=strategies,
                n_suggestions=n_suggestions,
                parallel=parallel
            )
            
            # Display results
            self._display_benchmark_results(results)
            
        except Exception as e:
            logger.error(f"Benchmark thread error: {e}")
            self._log_result(f"❌ Benchmark failed: {str(e)}")
        finally:
            # Re-enable button
            self.benchmark_button.config(state="normal")
    
    def _run_whatif(self):
        """Run what-if analysis."""
        try:
            # Get scenarios from listbox
            scenarios = []
            for i in range(self.scenario_listbox.size()):
                scenario_text = self.scenario_listbox.get(i)
                
                # Parse scenario text (simplified)
                if "Conservative" in scenario_text:
                    scenarios.append({
                        'name': 'conservative',
                        'n_suggestions': 5,
                        'strategy': 'ei'
                    })
                elif "Aggressive" in scenario_text:
                    scenarios.append({
                        'name': 'aggressive',
                        'n_suggestions': 15,
                        'strategy': 'ehvi'
                    })
                elif "Random" in scenario_text:
                    scenarios.append({
                        'name': 'random_baseline',
                        'n_suggestions': 10,
                        'strategy': 'random'
                    })
            
            if not scenarios:
                messagebox.showwarning("No Scenarios", "Please add at least one scenario.")
                return
            
            parallel = self.parallel_whatif_var.get()
            
            # Show progress
            self._log_result(f"Starting what-if analysis with {len(scenarios)} scenarios")
            
            # Run in separate thread
            thread = threading.Thread(
                target=self._run_whatif_thread,
                args=(scenarios, parallel)
            )
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error starting what-if analysis: {e}")
            messagebox.showerror("What-If Error", f"Failed to start what-if analysis: {str(e)}")
    
    def _run_whatif_thread(self, scenarios, parallel):
        """Run what-if analysis in separate thread."""
        try:
            # Disable button during execution
            self.whatif_button.config(state="disabled")
            
            # Run what-if analysis
            results = self.controller.run_what_if_analysis(
                scenarios=scenarios,
                parallel=parallel
            )
            
            # Display results
            self._display_whatif_results(results)
            
        except Exception as e:
            logger.error(f"What-if thread error: {e}")
            self._log_result(f"❌ What-if analysis failed: {str(e)}")
        finally:
            # Re-enable button
            self.whatif_button.config(state="normal")
    
    def _load_large_dataset(self):
        """Load a large dataset in parallel."""
        try:
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title="Select Large Dataset",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("Excel files", "*.xlsx"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # Get chunk size
            try:
                chunk_size = int(self.chunk_size_var.get())
            except ValueError:
                messagebox.showerror("Invalid Input", "Chunk size must be an integer.")
                return
            
            # Show progress
            self._log_result(f"Loading dataset: {file_path}")
            self._log_result(f"Using chunk size: {chunk_size}")
            
            # Run in separate thread
            thread = threading.Thread(
                target=self._load_dataset_thread,
                args=(file_path, chunk_size)
            )
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            messagebox.showerror("Loading Error", f"Failed to load dataset: {str(e)}")
    
    def _load_dataset_thread(self, file_path, chunk_size):
        """Load dataset in separate thread."""
        try:
            # Disable button during execution
            self.load_data_button.config(state="disabled")
            
            # Load data
            if file_path.endswith('.csv'):
                data_df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                data_df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            # Load in parallel
            results = self.controller.load_large_dataset_parallel(
                data_df=data_df,
                chunk_size=chunk_size
            )
            
            # Display results
            self._log_result(f"✅ Dataset loaded successfully!")
            self._log_result(f"Processed {results.get('processed_chunks', 0)} chunks")
            self._log_result(f"Total rows: {len(data_df)}")
            
        except Exception as e:
            logger.error(f"Dataset loading thread error: {e}")
            self._log_result(f"❌ Dataset loading failed: {str(e)}")
        finally:
            # Re-enable button
            self.load_data_button.config(state="normal")
    
    def _add_scenario(self):
        """Add a new scenario."""
        # Simple dialog for adding scenarios
        scenario_name = tk.simpledialog.askstring(
            "Add Scenario",
            "Enter scenario description:"
        )
        if scenario_name:
            self.scenario_listbox.insert(tk.END, scenario_name)
    
    def _remove_scenario(self):
        """Remove selected scenario."""
        selection = self.scenario_listbox.curselection()
        if selection:
            self.scenario_listbox.delete(selection[0])
    
    def _update_stats(self):
        """Update performance statistics."""
        try:
            stats = self.controller.get_orchestrator_stats()
            
            # Format stats
            stats_text = "Parallel Optimization Statistics\n"
            stats_text += "=" * 35 + "\n"
            
            if "error" not in stats:
                stats_text += f"Parallel Enabled: {'Yes' if stats.get('parallel_enabled', False) else 'No'}\n"
                stats_text += f"Sequential Requests: {stats.get('sequential_requests', 0)}\n"
                stats_text += f"Parallel Requests: {stats.get('parallel_requests', 0)}\n"
                
                if stats.get('parallel_enabled', False):
                    stats_text += f"Workers: {stats.get('n_workers', 'N/A')}\n"
                    stats_text += f"Cache Size: {stats.get('cache_size', 0)}\n"
            else:
                stats_text += f"Error: {stats['error']}\n"
            
            # Update display
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, f"Error updating stats: {str(e)}")
    
    def _clear_cache(self):
        """Clear optimization cache."""
        try:
            self.controller.clear_optimization_cache()
            self._log_result("✅ Cache cleared successfully")
            self._update_stats()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            self._log_result(f"❌ Failed to clear cache: {str(e)}")
    
    def _toggle_parallel(self):
        """Toggle parallel optimization."""
        try:
            enabled = self.parallel_enabled_var.get()
            self.controller.set_parallel_optimization_enabled(enabled)
            status = "enabled" if enabled else "disabled"
            self._log_result(f"✅ Parallel optimization {status}")
            self._update_stats()
        except Exception as e:
            logger.error(f"Error toggling parallel: {e}")
            self._log_result(f"❌ Failed to toggle parallel: {str(e)}")
    
    def _display_benchmark_results(self, results):
        """Display benchmarking results."""
        self._log_result("\n🏁 BENCHMARK RESULTS")
        self._log_result("=" * 50)
        
        for strategy, result in results.items():
            if result.get('success', False):
                self._log_result(f"✅ {strategy.upper()}:")
                self._log_result(f"   Suggestions: {result.get('n_suggestions', 'N/A')}")
                self._log_result(f"   Time: {result.get('execution_time', 'N/A'):.2f}s")
            else:
                self._log_result(f"❌ {strategy.upper()}: {result.get('error', 'Unknown error')}")
        
        self._log_result("")
    
    def _display_whatif_results(self, results):
        """Display what-if analysis results."""
        self._log_result("\n🔮 WHAT-IF ANALYSIS RESULTS")
        self._log_result("=" * 50)
        
        for scenario_name, result in results.items():
            if result.get('success', False):
                self._log_result(f"✅ {scenario_name.upper()}:")
                self._log_result(f"   Time: {result.get('execution_time', 'N/A'):.2f}s")
            else:
                self._log_result(f"❌ {scenario_name.upper()}: {result.get('error', 'Unknown error')}")
        
        self._log_result("")
    
    def _log_result(self, message):
        """Log a result message to the results display."""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.results_text.update()


# Import check for tkinter dialogs
try:
    import tkinter.simpledialog as tk_simpledialog
    tk.simpledialog = tk_simpledialog
except ImportError:
    logger.warning("tkinter.simpledialog not available")