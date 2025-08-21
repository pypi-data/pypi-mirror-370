"""
SGLBO Screening Execution Window

Provides a real-time progress tracking window for SGLBO screening optimization.
Shows iteration progress, current best results, and allows user interaction.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import json

logger = logging.getLogger(__name__)


class ScreeningExecutionWindow:
    """
    Real-time execution window for SGLBO screening optimization.
    Provides progress tracking, results display, and user controls.
    """
    
    def __init__(self, parent, screening_optimizer, results_manager, design_generator, config):
        """
        Initialize the screening execution window.
        
        Args:
            parent: Parent window
            screening_optimizer: SGLBO screening optimizer instance
            results_manager: Screening results manager instance  
            design_generator: Design space generator instance
            config: Screening configuration dictionary
        """
        self.parent = parent
        self.screening_optimizer = screening_optimizer
        self.results_manager = results_manager
        self.design_generator = design_generator
        self.config = config
        
        # Execution state
        self.is_running = False
        self.is_paused = False
        self.current_iteration = 0
        self.total_experiments = 0
        self.execution_thread = None
        
        # Create the window
        self.window = tk.Toplevel(parent)
        self.window.title("SGLBO Screening Execution")
        self.window.geometry("800x600")
        self.window.grab_set()  # Make window modal
        
        # Setup UI
        self._setup_ui()
        
        # Start with initial experiments
        self._initialize_screening()
        
        logger.info("Screening execution window initialized")
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="SGLBO Screening Optimization", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(1, weight=1)
        
        # Progress bar
        ttk.Label(progress_frame, text="Overall Progress:").grid(row=0, column=0, sticky=tk.W)
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # Status labels
        ttk.Label(progress_frame, text="Current Iteration:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.iteration_label = ttk.Label(progress_frame, text="0")
        self.iteration_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        ttk.Label(progress_frame, text="Total Experiments:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.experiments_label = ttk.Label(progress_frame, text="0")
        self.experiments_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        ttk.Label(progress_frame, text="Status:").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.status_label = ttk.Label(progress_frame, text="Initializing...")
        self.status_label.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Current Best Results", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        results_frame.columnconfigure(1, weight=1)
        
        # Results text area
        self.results_text = tk.Text(results_frame, height=8, wrap=tk.WORD)
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        self.start_button = ttk.Button(control_frame, text="Start Screening", 
                                     command=self._start_screening)
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.pause_button = ttk.Button(control_frame, text="Pause", 
                                     command=self._pause_screening, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", 
                                    command=self._stop_screening, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5)
        
        self.export_button = ttk.Button(control_frame, text="Export Results", 
                                      command=self._export_results, state=tk.DISABLED)
        self.export_button.grid(row=0, column=3, padx=5)
        
        self.close_button = ttk.Button(control_frame, text="Close", 
                                     command=self._close_window)
        self.close_button.grid(row=0, column=4, padx=(5, 0))
        
        # Setup window close protocol
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)
    
    def _initialize_screening(self):
        """Initialize screening with configuration."""
        try:
            # Display configuration
            config_text = f"""Screening Configuration:
Parameters: {list(self.config['parameters'].keys())}
Responses: {list(self.config['responses'].keys())}
Initial Samples: {self.config['sglbo_settings'].get('n_initial_samples', 8)}
Max Iterations: {self.config['sglbo_settings'].get('max_iterations', 20)}
Gradient Step: {self.config['sglbo_settings'].get('gradient_step_size', 0.1)}
Exploration Factor: {self.config['sglbo_settings'].get('exploration_factor', 0.15)}

Ready to start screening optimization.
Click 'Start Screening' to begin.
"""
            self.results_text.insert(tk.END, config_text)
            self.status_label.config(text="Ready to start")
            
        except Exception as e:
            logger.error(f"Error initializing screening: {e}")
            self.status_label.config(text="Initialization error")
    
    def _start_screening(self):
        """Start the screening process."""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            
            # Update UI
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            self.progress_bar.start()
            
            # Start execution thread
            self.execution_thread = threading.Thread(target=self._run_screening_process)
            self.execution_thread.daemon = True
            self.execution_thread.start()
            
            logger.info("Screening process started")
    
    def _pause_screening(self):
        """Pause/resume the screening process."""
        if self.is_running:
            self.is_paused = not self.is_paused
            
            if self.is_paused:
                self.pause_button.config(text="Resume")
                self.status_label.config(text="Paused")
                self.progress_bar.stop()
            else:
                self.pause_button.config(text="Pause")
                self.status_label.config(text="Running")
                self.progress_bar.start()
    
    def _stop_screening(self):
        """Stop the screening process."""
        self.is_running = False
        self.is_paused = False
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="Pause")
        self.stop_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.NORMAL)
        self.progress_bar.stop()
        
        self.status_label.config(text="Stopped")
        logger.info("Screening process stopped")
    
    def _run_screening_process(self):
        """Run the screening process in a separate thread."""
        try:
            # Generate initial experiments
            self._update_status("Generating initial experiments...")
            initial_experiments = self.screening_optimizer.suggest_initial_experiments()
            
            self._update_results(f"\nGenerated {len(initial_experiments)} initial experiments:")
            for i, exp in enumerate(initial_experiments):
                if not self.is_running:
                    return
                self._update_results(f"  Experiment {i+1}: {exp}")
            
            # Simulate waiting for experimental data
            self._update_results(f"\n[SIMULATION MODE - In real use, run these experiments and import data]\n")
            
            # For demonstration, simulate experimental responses
            self._simulate_initial_experiments(initial_experiments)
            
            # Run screening iterations
            max_iterations = self.config['sglbo_settings'].get('max_iterations', 20)
            
            for iteration in range(max_iterations):
                if not self.is_running:
                    break
                
                # Handle pause
                while self.is_paused and self.is_running:
                    time.sleep(0.1)
                
                if not self.is_running:
                    break
                
                self.current_iteration = iteration + 1
                self._update_iteration_display()
                
                self._update_status(f"Running iteration {self.current_iteration}...")
                
                # Suggest next experiment
                next_experiment = self.screening_optimizer.suggest_next_experiment()
                self._update_results(f"\nIteration {self.current_iteration} - Suggested experiment: {next_experiment}")
                
                # Simulate experimental response (in real use, user would provide this)
                simulated_response = self._simulate_response(next_experiment)
                experiment_data = {**next_experiment, **simulated_response}
                
                # Add data to optimizer
                new_data_df = pd.DataFrame([experiment_data])
                self.screening_optimizer.add_experimental_data(new_data_df)
                
                # Run iteration analysis
                iteration_info = self.screening_optimizer.run_screening_iteration()
                
                # Add to results manager
                self.results_manager.add_experimental_data(new_data_df, iteration_info)
                
                # Update results display
                self._update_results(f"  Response: {simulated_response}")
                
                # Check convergence
                convergence_info = self.screening_optimizer.check_convergence()
                if convergence_info["converged"]:
                    self._update_results(f"\n*** CONVERGENCE ACHIEVED ***")
                    self._update_results(f"Reason: {convergence_info['recommendation']}")
                    break
                
                # Small delay for demonstration
                time.sleep(0.5)
            
            # Generate final results
            self._generate_final_results()
            
        except Exception as e:
            logger.error(f"Error in screening process: {e}")
            self._update_status(f"Error: {str(e)}")
        finally:
            if self.is_running:
                self._stop_screening()
    
    def _simulate_initial_experiments(self, experiments):
        """Simulate initial experimental data."""
        experimental_data = []
        
        for i, params in enumerate(experiments):
            if not self.is_running:
                return
            
            responses = self._simulate_response(params)
            experiment_data = {**params, **responses}
            experimental_data.append(experiment_data)
            
            self._update_results(f"  Results {i+1}: {responses}")
        
        # Add all initial data
        data_df = pd.DataFrame(experimental_data)
        self.screening_optimizer.add_experimental_data(data_df)
        self.results_manager.add_experimental_data(data_df)
        
        self.total_experiments = len(data_df)
        self._update_experiments_display()
    
    def _simulate_response(self, params):
        """Simulate experimental response (replace with real data in production)."""
        import numpy as np
        
        # Simple simulation based on parameter values
        temp = params.get("Temperature", 100)
        pressure = params.get("Pressure", 5)
        catalyst = params.get("Catalyst", "A")
        
        # Deterministic simulation based on parameters
        np.random.seed(hash(str(params)) % 2**32)
        
        # Simulate yield and purity
        temp_effect = -(temp - 120)**2 / 1000
        pressure_effect = -(pressure - 6)**2 / 2
        catalyst_effect = {"A": 0, "B": 10, "C": 5}.get(catalyst, 0)
        
        yield_base = 70 + temp_effect + pressure_effect + catalyst_effect
        yield_response = max(0, yield_base + np.random.normal(0, 2))
        
        purity_response = max(0, min(100, yield_response * 0.9 + np.random.normal(10, 1.5)))
        
        return {
            response_name: round(yield_response if response_name == "Yield" else purity_response, 2)
            for response_name in self.config["responses"].keys()
        }
    
    def _generate_final_results(self):
        """Generate and display final screening results."""
        try:
            self._update_status("Generating final results...")
            
            # Get best parameters
            best_params, best_responses = self.results_manager.get_best_parameters()
            
            # Generate optimization recommendations
            recommendations = self.results_manager.generate_optimization_recommendations()
            
            # Generate design space
            design_points = self.design_generator.generate_central_composite_design(
                center_point=best_params,
                design_radius=0.15
            )
            
            # Display final results
            final_results = f"""
=== SCREENING COMPLETED ===

Best Parameters Found:
{self._format_dict(best_params)}

Best Responses:
{self._format_dict(best_responses)}

Total Experiments: {len(self.screening_optimizer.experimental_data)}
Iterations Completed: {self.current_iteration}

Next Steps:
1. Generated {len(design_points)} design points for detailed optimization
2. Ready to transition to main Bayesian optimization
3. Use 'Export Results' to save complete screening data

Screening optimization completed successfully!
"""
            self._update_results(final_results)
            self._update_status("Completed successfully")
            
        except Exception as e:
            logger.error(f"Error generating final results: {e}")
            self._update_results(f"\nError generating final results: {e}")
    
    def _format_dict(self, d):
        """Format dictionary for display."""
        if not d:
            return "  None"
        
        lines = []
        for key, value in d.items():
            if isinstance(value, float):
                lines.append(f"  {key}: {value:.3f}")
            else:
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)
    
    def _update_status(self, status_text):
        """Update status label thread-safely."""
        self.window.after(0, lambda: self.status_label.config(text=status_text))
    
    def _update_results(self, text):
        """Update results text area thread-safely."""
        def update():
            self.results_text.insert(tk.END, text + "\n")
            self.results_text.see(tk.END)
        
        self.window.after(0, update)
    
    def _update_iteration_display(self):
        """Update iteration counter display."""
        self.window.after(0, lambda: self.iteration_label.config(text=str(self.current_iteration)))
    
    def _update_experiments_display(self):
        """Update experiments counter display."""
        self.total_experiments = len(self.screening_optimizer.experimental_data)
        self.window.after(0, lambda: self.experiments_label.config(text=str(self.total_experiments)))
    
    def _export_results(self):
        """Export screening results to file."""
        try:
            # Ask user for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("Excel files", "*.xlsx"),
                    ("All files", "*.*")
                ],
                title="Export Screening Results"
            )
            
            if file_path:
                # Determine format from extension
                if file_path.endswith('.xlsx'):
                    format_type = "excel"
                else:
                    format_type = "json"
                
                # Export results
                success = self.results_manager.export_results(file_path, format=format_type)
                
                if success:
                    messagebox.showinfo("Export Successful", 
                                      f"Results exported successfully to:\\n{file_path}")
                else:
                    messagebox.showerror("Export Failed", 
                                       "Failed to export results. Check the log for details.")
                    
        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            messagebox.showerror("Export Error", f"Error exporting results: {e}")
    
    def _close_window(self):
        """Close the execution window."""
        if self.is_running:
            if messagebox.askyesno("Confirm Close", 
                                 "Screening is still running. Are you sure you want to close?"):
                self._stop_screening()
                self.window.destroy()
        else:
            self.window.destroy()


def show_screening_execution_window(parent, screening_optimizer, results_manager, design_generator, config):
    """
    Show the screening execution window.
    
    Args:
        parent: Parent window
        screening_optimizer: SGLBO screening optimizer instance
        results_manager: Screening results manager instance  
        design_generator: Design space generator instance
        config: Screening configuration dictionary
    """
    return ScreeningExecutionWindow(parent, screening_optimizer, results_manager, design_generator, config)