"""
Simple Controller - Enhanced MVC Controller for Multi-Objective Optimization

This module implements the controller component of the MVC pattern for the
Multi-Objective Optimization Laboratory. It manages the interaction between
the GUI (view) and the optimization engine (model), handling user input,
optimization flow, and data management.

Key Features:
- Multi-objective Bayesian optimization control
- Real-time experiment data management
- Plotting and visualization coordination
- File I/O for optimization sessions
- Enhanced error handling and logging
- Thread-safe operation management

Classes:
    SimpleController: Main controller class implementing MVC pattern
"""

import logging
import pickle
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Local imports
try:
    from ..utils.scientific_utilities import scientific_validator
except ImportError:
    scientific_validator = None

logger = logging.getLogger(__name__)


class SimpleController:
    """
    Enhanced MVC Controller for Multi-Objective Optimization Application.
    
    This controller implements the MVC pattern, mediating between the GUI (view)
    and the optimization engine (model). It handles user interactions, manages
    optimization workflow, coordinates plotting, and maintains application state.
    
    Key Responsibilities:
    - Initialize and configure optimization sessions
    - Generate experiment suggestions using Bayesian optimization
    - Process experimental results and update models
    - Coordinate real-time plotting and visualization updates
    - Manage file I/O for saving/loading optimization sessions
    - Handle batch operations and data import/export
    - Provide thread-safe operation management
    
    Attributes:
        view: The GUI component that this controller manages
        optimizer: The optimization engine instance (EnhancedMultiObjectiveOptimizer)
        plot_manager: Manages plotting functionalities and visualizations
    """

    def __init__(self, view: Any) -> None:
        """
        Initialize the SimpleController with the provided view component.

        Args:
            view: The GUI view component that implements the required interface methods:
                  - set_busy_state(bool): Update UI busy state
                  - show_error(title, message): Display error messages
                  - create_main_interface(params, responses): Build main UI
                  - set_status(message): Update status bar
                  - update_displays(data): Update display elements
                  - set_plot_manager(manager): Set plotting manager
        
        Raises:
            TypeError: If view doesn't implement required interface methods
        """
        # Validate view interface
        required_methods = ['set_busy_state', 'show_error', 'set_status']
        missing_methods = [method for method in required_methods 
                          if not hasattr(view, method)]
        if missing_methods:
            raise TypeError(f"View missing required methods: {missing_methods}")
            
        self.view = view
        self.optimizer: Optional[Any] = None
        self.plot_manager: Optional[Any] = None


        # State management
        self._is_busy: bool = False
        self._last_update_time: float = 0.0
        self._optimization_start_time: Optional[datetime] = None
        self._thread_lock = threading.Lock()  # For thread-safe operations

        logger.debug("Controller initialized successfully")

    @property
    def is_busy(self) -> bool:
        """Check if controller is currently processing operations.
        
        Returns:
            bool: True if controller is busy, False otherwise
        """
        with self._thread_lock:
            return self._is_busy

    def _set_busy(self, busy: bool) -> None:
        """Set busy state and update UI with thread safety.
        
        Args:
            busy: True to set busy state, False to clear it
        """
        with self._thread_lock:
            self._is_busy = busy
            
        # Update UI in main thread
        try:
            self.view.set_busy_state(busy)
            status = "Processing..." if busy else "Ready"
            self.view.set_status(status)
        except Exception as e:
            logger.warning(f"Failed to update UI busy state: {e}")
            
    @property
    def has_optimizer(self) -> bool:
        """Check if optimizer is initialized and ready.
        
        Returns:
            bool: True if optimizer is available, False otherwise
        """
        return self.optimizer is not None
        
    @property 
    def has_data(self) -> bool:
        """Check if optimization has experimental data.
        
        Returns:
            bool: True if data exists, False otherwise
        """
        if not self.has_optimizer:
            return False
        try:
            # Check if experimental_data exists and is not empty
            return (hasattr(self.optimizer, 'experimental_data') and 
                    self.optimizer.experimental_data is not None and
                    not self.optimizer.experimental_data.empty)
        except Exception:
            return False

    def start_new_optimization(
        self,
        params_config: Dict[str, Dict[str, Any]],
        responses_config: Dict[str, Dict[str, Any]],
        general_constraints: List[str],
        initial_sampling_method: str = "random",
    ) -> None:
        """
        Initializes a new multi-objective optimization session.

        Args:
            params_config (Dict[str, Dict[str, Any]]): Configuration for the input parameters.
            responses_config (Dict[str, Dict[str, Any]]): Configuration for the response variables (objectives).
            general_constraints (List[str]): A list of string representations of general constraints.
            initial_sampling_method (str): The method to use for generating initial experimental
                                           suggestions when there is insufficient data.
                                           Defaults to "random", can be "LHS" for Latin Hypercube Sampling.
        Raises:
            ValueError: If the optimization configuration is invalid.
            Exception: For any other errors during the optimization setup.
        """
        try:
            self._set_busy(True)

            logger.info("Starting new optimization with corrected controller")
            logger.info(f"Parameters: {list(params_config.keys())}")
            logger.info(f"Responses: {list(responses_config.keys())}")

            # Enhanced validation of the provided optimization configuration.
            self._validate_optimization_config(params_config, responses_config)

            # Dynamically import the EnhancedMultiObjectiveOptimizer to avoid circular dependencies
            # and ensure the latest version is used.
            from .optimizer import EnhancedMultiObjectiveOptimizer
            from .orchestrator import OptimizationOrchestrator

            # Create a new optimizer instance with the provided configurations.
            base_optimizer = EnhancedMultiObjectiveOptimizer(
                params_config=params_config,
                responses_config=responses_config,
                general_constraints=general_constraints,
                initial_sampling_method=initial_sampling_method,
            )

            # Wrap with intelligent orchestrator for hybrid sequential/parallel capabilities
            self.optimizer = OptimizationOrchestrator(
                base_optimizer=base_optimizer,
                enable_parallel=True,  # Enable parallel capabilities by default
                n_workers=None  # Auto-detect number of workers
            )
            logger.info("Hybrid orchestrator created successfully with parallel capabilities")
            self.view.set_status("Optimization ready")

            # Initialize the plotting manager
            try:
                from ..utils.plotting import SimplePlotManager

                self.plot_manager = SimplePlotManager(self.optimizer)
                logger.debug("Plot manager initialized")
                if hasattr(self.view, "set_plot_manager"):
                    self.view.set_plot_manager(self.plot_manager)
            except ImportError:
                logger.warning(
                    "Plotting module not available. Plotting functionalities will be limited."
                )
                self.plot_manager = None

            # Create the main user interface if the view supports it.
            if hasattr(self.view, "create_main_interface"):
                self.view.create_main_interface(params_config, responses_config)
                logger.info("Main interface created")

            # Generate the very first suggestion for the user to start experiments.
            initial_suggestion = self._generate_initial_suggestion()

            # Schedule an initial update of the view to display the first suggestion and status.
            self._schedule_view_update(initial_suggestion=initial_suggestion)

            if hasattr(self.view, "set_status"):
                self.view.set_status(
                    "Optimization ready - First experiment suggestion generated"
                )

            logger.info("Optimization setup completed successfully")

        except Exception as e:
            logger.error(f"Failed to start optimization: {e}", exc_info=True)
            if hasattr(self.view, "show_error"):
                self.view.show_error("Setup Error", f"Configuration error: {str(e)}")
        finally:
            self._set_busy(False)

    def setup_optimization_with_import(
        self,
        params_config: Dict[str, Dict[str, Any]],
        responses_config: Dict[str, Dict[str, Any]],
        data: pd.DataFrame,
        general_constraints: List[str] = None,
        initial_sampling_method: str = "random",
    ) -> None:
        """
        Initialize optimization with imported CSV data.
        
        Args:
            params_config: Parameter configuration from import wizard
            responses_config: Response configuration from import wizard
            data: Imported and validated DataFrame
            general_constraints: List of constraints (optional)
            initial_sampling_method: Sampling method for additional suggestions
        """
        try:
            self._set_busy(True)
            
            logger.info("Setting up optimization with imported data")
            logger.info(f"Imported data shape: {data.shape}")
            logger.info(f"Parameters: {list(params_config.keys())}")
            logger.info(f"Responses: {list(responses_config.keys())}")
            
            # Set default constraints if none provided
            if general_constraints is None:
                general_constraints = []
            
            # Validate the configuration
            self._validate_optimization_config(params_config, responses_config)
            
            # Create optimizer with imported configuration
            from .optimizer import EnhancedMultiObjectiveOptimizer
            from .orchestrator import OptimizationOrchestrator
            
            base_optimizer = EnhancedMultiObjectiveOptimizer(
                params_config=params_config,
                responses_config=responses_config,
                general_constraints=general_constraints,
                initial_sampling_method=initial_sampling_method,
            )
            
            # Wrap with intelligent orchestrator for hybrid sequential/parallel capabilities
            self.optimizer = OptimizationOrchestrator(
                base_optimizer=base_optimizer,
                enable_parallel=True,
                n_workers=None
            )
            
            logger.info("Hybrid orchestrator created with imported configuration")
            
            # Load the imported data as baseline using Option 1 approach
            logger.info(f"Loading {len(data)} data points as baseline (Option 1: single baseline iteration)")
            
            # Add all data points at once to establish baseline (iteration 0)
            self.optimizer.add_experimental_data(data, is_optimization_result=False)
            
            logger.info(f"Successfully established baseline from {len(data)} data points (baseline HV: {self.optimizer.baseline_hypervolume:.6f})")
            
            # Initialize plotting manager
            try:
                from ..utils.plotting import SimplePlotManager
                self.plot_manager = SimplePlotManager(self.optimizer)
                logger.debug("Plot manager initialized")
                if hasattr(self.view, "set_plot_manager"):
                    self.view.set_plot_manager(self.plot_manager)
            except ImportError:
                logger.warning("Plot manager unavailable - continuing without plotting")
                self.plot_manager = None
            
            # Store imported data for reference
            self.imported_data = data
            self.imported_params_config = params_config
            self.imported_responses_config = responses_config
            
            # Update view status
            self.view.set_status(f"Optimization ready with {len(data)} imported data points")
            
            logger.info("Import-based optimization setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup optimization with import: {e}", exc_info=True)
            if hasattr(self.view, "show_error"):
                self.view.show_error("Import Setup Error", f"Failed to setup with imported data: {str(e)}")
            raise
        finally:
            self._set_busy(False)

    def _generate_initial_suggestion(self) -> Dict[str, Any]:
        """
        Generates the very first experiment suggestion when a new optimization starts.
        This suggestion is typically generated by the optimizer's initial sampling method.

        Returns:
            Dict[str, Any]: A dictionary representing the initial suggested parameter
                            combination. Returns an empty dictionary if no suggestion
                            can be generated.
        """
        try:
            logger.info("Generating initial suggestion...")
            # Request one suggestion from the optimizer.
            suggestions = self.optimizer.suggest_next_experiment(n_suggestions=1)

            if suggestions:
                logger.info(f"Initial suggestion generated: {suggestions[0]}")
                return suggestions[0]
            else:
                logger.warning("No initial suggestion generated by the optimizer.")
                return {}
        except Exception as e:
            logger.error(f"Error generating initial suggestion: {e}", exc_info=True)
            return {}

    def generate_batch_suggestions(self, num_suggestions: int) -> List[Dict[str, Any]]:
        """
        Generates a batch of `num_suggestions` best parameter combinations
        using the optimizer.

        Args:
            num_suggestions (int): The number of suggestions to generate.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a suggested
                                  parameter combination. Returns an empty list if the
                                  optimizer is not initialized or an error occurs.
        """
        if not self.optimizer:
            logger.warning(
                "Optimizer not initialized. Cannot generate batch suggestions."
            )
            if hasattr(self.view, "show_warning"):
                self.view.show_warning(
                    "Optimizer Not Ready", "Please start or load an optimization first."
                )
            return []

        try:
            self._set_busy(True)
            logger.info(f"Generating {num_suggestions} batch suggestions...")

            # Use standard Bayesian optimization suggestions
            suggestions = self.optimizer.suggest_next_experiment(
                n_suggestions=num_suggestions
            )
            logger.info(
                f"Generated {len(suggestions)} Bayesian optimization suggestions."
            )
            return suggestions
        except Exception as e:
            logger.error(f"Error generating batch suggestions: {e}", exc_info=True)
            if hasattr(self.view, "show_error"):
                self.view.show_error(
                    "Batch Suggestion Error",
                    f"Failed to generate batch suggestions: {e}",
                )
            return []
        finally:
            self._set_busy(False)

    def submit_single_result(
        self, current_suggestion: Dict[str, Any], result_values: Dict[str, float]
    ) -> None:
        """
        Submits the experimental results for a single experiment to the optimizer.
        This method combines the parameters of the experiment with its measured
        response values, adds them to the optimizer's data, and triggers a view update.

        Args:
            current_suggestion (Dict[str, Any]): A dictionary of the parameter values
                                                 for the experiment that was just run.
            result_values (Dict[str, float]): A dictionary of the measured response
                                             values for the experiment.

        Raises:
            ValueError: If `current_suggestion` or `result_values` are empty or invalid.
            TypeError: If input types are incorrect.
            Exception: For any other errors during result submission.
        """
        try:
            logger.debug("Entering submit_single_result")
            self._set_busy(True)

            logger.info(f"Submitting results: {result_values}")

            # Enhanced input validation
            if not isinstance(current_suggestion, dict):
                raise TypeError("Current suggestion must be a dictionary.")
            if not isinstance(result_values, dict):
                raise TypeError("Result values must be a dictionary.")

            if not current_suggestion:
                raise ValueError("Current suggestion cannot be empty.")
            if not result_values:
                raise ValueError("Result values cannot be empty.")

            # Validate that result values are numeric and finite
            for key, value in result_values.items():
                if not isinstance(value, (int, float)):
                    raise TypeError(
                        f"Result value for '{key}' must be numeric, got {type(value).__name__}"
                    )
                if not np.isfinite(value):
                    raise ValueError(
                        f"Result value for '{key}' must be finite, got {value}"
                    )

            # Validate that current suggestion contains expected parameters
            if self.optimizer:
                expected_params = set(self.optimizer.params_config.keys())
                provided_params = set(current_suggestion.keys())

                missing_params = expected_params - provided_params
                if missing_params:
                    raise ValueError(f"Missing required parameters: {missing_params}")

                extra_params = provided_params - expected_params
                if extra_params:
                    logger.warning(f"Unexpected parameters provided: {extra_params}")

            # Combine the parameter suggestion and the experimental results into a single record.
            data_record = {**current_suggestion, **result_values}

            # Validate that we don't have parameter/response name conflicts
            param_names = set(current_suggestion.keys())
            response_names = set(result_values.keys())
            conflicts = param_names & response_names
            if conflicts:
                raise ValueError(f"Parameter and response names conflict: {conflicts}")

            # Convert the single record into a Pandas DataFrame, as expected by the optimizer.
            data_df = pd.DataFrame([data_record])

            logger.info(f"Created data record: {data_record}")

            # Add experimental data using standard Bayesian optimization
            if self.optimizer:
                self.optimizer.add_experimental_data(data_df)
                logger.debug(
                    f"Experimental data added. Total experiments: {len(self.optimizer.experimental_data)}"
                )

                logger.info(
                    f"Successfully submitted results for experiment {len(self.optimizer.experimental_data)}"
                )

                if hasattr(self.view, "show_info"):
                    self.view.show_info(
                        "Success", "Results submitted and models updated!"
                    )

                # Schedule a view update to reflect the new data and updated models.
                logger.debug("Calling update_view from submit_single_result")
                self._schedule_view_update()
            else:
                logger.error("Optimizer not initialized. Cannot submit results.")
                if hasattr(self.view, "show_error"):
                    self.view.show_error(
                        "Error", "Optimizer not initialized. Cannot submit results."
                    )

        except (ValueError, TypeError) as e:
            logger.error(f"Input validation error: {e}")
            if hasattr(self.view, "show_error"):
                self.view.show_error("Input Error", f"Invalid input: {e}")
        except Exception as e:
            logger.error(f"Failed to submit results: {e}", exc_info=True)
            if hasattr(self.view, "show_error"):
                self.view.show_error("Error", f"Failed to submit results: {e}")
        finally:
            self._set_busy(False)  # Ensure busy state is reset even if an error occurs.

    def _schedule_view_update(
        self, initial_suggestion: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Schedules a view update to ensure GUI responsiveness.
        It uses Tkinter's `after` method to delay the `update_view` call,
        allowing the GUI to process other events before updating displays.

        Args:
            initial_suggestion (Optional[Dict[str, Any]]): An optional initial
                                                            suggestion to pass to
                                                            `update_view`.
        """
        if hasattr(self.view, "after") and hasattr(self.view, "update_displays"):
            # Schedule the update_displays call after a short delay (e.g., 100ms)
            # This gives the GUI a chance to fully render before updating labels
            self.view.after(100, lambda: self.update_view(initial_suggestion))
        else:
            # Fallback if after or update_displays is not available (e.g., in tests or non-GUI environments)
            self.update_view(initial_suggestion)

    def _validate_optimization_config(
        self,
        params_config: Dict[str, Dict[str, Any]],
        responses_config: Dict[str, Dict[str, Any]],
    ) -> None:
        """
        Validates the provided optimization configuration to ensure it meets the
        minimum requirements for starting an optimization session.

        Args:
            params_config (Dict[str, Dict[str, Any]]): Configuration for the input parameters.
            responses_config (Dict[str, Dict[str, Any]]): Configuration for the response variables.

        Raises:
            ValueError: If the configuration is invalid (e.g., no parameters, no responses,
                        or no optimization goals defined).
        """
        if not params_config:
            raise ValueError("At least one parameter must be defined.")

        if not responses_config:
            raise ValueError("At least one response must be defined.")

        # Check for at least one objective with a defined optimization goal.
        has_objective = False
        # Combine parameter and response configurations for checking goals.
        all_configs = list(params_config.values()) + list(responses_config.values())

        for conf in all_configs:
            goal = conf.get("goal", "None")
            if goal in ["Maximize", "Minimize", "Target", "Range"]:
                has_objective = True
                logger.info(f"Found optimization goal: {goal}")
                break

        if not has_objective:
            raise ValueError(
                "At least one parameter or response must have an optimization goal (Maximize, Minimize, Target, or Range)."
            )

    def update_view(self, initial_suggestion: Optional[Dict[str, Any]] = None) -> None:
        """
        Updates the graphical user interface (GUI) with the current state of the
        optimization. This includes displaying the next suggested experiment,
        the best compromise solution, Pareto front data, and updating plots.

        Args:
            initial_suggestion (Optional[Dict[str, Any]]): An optional initial
                                                            suggestion to display.
                                                            Used primarily during
                                                            the initial setup.
        """
        logger.debug("Entering update_view")
        if not self.optimizer:
            logger.warning(
                "Update view called but no optimizer available. Skipping update."
            )
            return

        if self._is_busy:
            logger.debug("Skipping view update while controller is busy.")
            return

        try:
            start_time = time.time()

            if hasattr(self.view, "set_status"):
                self.view.set_status("Updating displays...")

            # Get the current number of experimental data points.
            data_count = len(self.optimizer.experimental_data)

            logger.info(f"Updating view with {data_count} experiments.")

            # Handle the case where no experimental data has been added yet.
            if data_count == 0:
                self._handle_no_data_case(initial_suggestion)
                return

            # Generate the next suggestion for the user.
            # If an initial suggestion is provided, use that; otherwise, generate a new one.
            suggestion = (
                initial_suggestion
                if initial_suggestion is not None
                else self._generate_suggestion_safely()
            )
            logger.info(f"Generated suggestion for view: {suggestion}")

            # Retrieve Pareto front data.
            pareto_X, pareto_obj, pareto_indices = self._get_pareto_data_safely()

            # Retrieve the best compromise solution.
            best_params, best_preds = self._get_best_solution_safely()

            # Prepare a dictionary of data to pass to the view for updating.
            view_data = {
                "suggestion": suggestion,
                "best_compromise": {
                    "params": best_params,
                    "responses": best_preds,
                },
                "pareto_front": {
                    "pareto_X_df": pareto_X,
                    "pareto_objectives_df": pareto_obj,
                },
                "data_count": data_count,
            }

            logger.info(f"Prepared view data with suggestion: {suggestion}")

            # Update the main display components of the view.
            if hasattr(self.view, "update_displays"):
                logger.debug(
                    f"Calling view.update_displays with data_count={data_count}"
                )
                self.view.update_displays(view_data)
                logger.info("View displays updated.")

            # Update all plots managed by the plot manager.
            if hasattr(self.view, "update_all_plots"):
                logger.debug("Calling view.update_all_plots")
                self.view.update_all_plots()
                logger.info("Plots updated.")

            update_time = time.time() - start_time

            if hasattr(self.view, "set_status"):
                self.view.set_status("View update completed.")
            logger.info(f"View update completed in {update_time:.3f}s.")

        except Exception as e:
            logger.error(f"Error updating view: {e}", exc_info=True)
            if hasattr(self.view, "show_error"):
                self.view.show_error("Display Error", f"Failed to update displays: {e}")

    def _handle_no_data_case(self, initial_suggestion: Optional[Dict[str, Any]] = None):
        """CORRECTED - Handle case when no experimental data is available"""
        logger.info("Handling no data case - generating initial suggestion")
        suggestion = (
            initial_suggestion
            if initial_suggestion is not None
            else self._generate_suggestion_safely()
        )

        logger.info(f"Generated initial suggestion: {suggestion}")

        view_data = {
            "suggestion": suggestion,
            "best_compromise": {"params": {}, "responses": {}},
            "pareto_front": {
                "pareto_X_df": pd.DataFrame(),
                "pareto_objectives_df": pd.DataFrame(),
            },
            "data_count": 0,
        }

        if hasattr(self.view, "update_displays"):
            self.view.update_displays(view_data)
        if hasattr(self.view, "set_status"):
            self.view.set_status("Ready for first experiment")

    def _generate_suggestion_safely(self) -> Dict[str, Any]:
        """CORRECTED - Generate next experiment suggestion with error handling"""
        try:
            logger.info("Generating suggestion safely...")
            suggestions = self.optimizer.suggest_next_experiment(n_suggestions=1)

            if suggestions:
                suggestion = suggestions[0]
                logger.info(f"Generated suggestion: {suggestion}")
                return suggestion
            else:
                logger.warning("No suggestions generated")
                return {}
        except Exception as e:
            logger.error(f"Error generating suggestion: {e}", exc_info=True)
            return {}

    def _get_pareto_data_safely(self) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
        """Get Pareto front data with error handling"""
        try:
            return self.optimizer.get_pareto_front()
        except Exception as e:
            logger.error(f"Error getting Pareto front: {e}")
            return pd.DataFrame(), pd.DataFrame(), np.array([])

    def _get_best_solution_safely(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Get best compromise solution with error handling"""
        try:
            return self.optimizer.get_best_compromise_solution()
        except Exception as e:
            logger.error(f"Error getting best solution: {e}")
            return {}, {}

    # File operations
    def save_optimization_to_file(self, filepath: Union[str, Path]) -> bool:
        """Save optimization state to file"""
        try:
            filepath = Path(filepath)

            # Calculate current hypervolume data for preservation
            try:
                current_hypervolume = self.optimizer._calculate_hypervolume()
                hypervolume_summary = self.optimizer.get_optimization_progress_summary()
                convergence_data = self.optimizer.check_hypervolume_convergence()
            except Exception as e:
                logger.warning(f"Could not calculate hypervolume data for save: {e}")
                current_hypervolume = {}
                hypervolume_summary = {}
                convergence_data = {}

            save_data = {
                "params_config": self.optimizer.params_config,
                "responses_config": self.optimizer.responses_config,
                "general_constraints": self.optimizer.general_constraints,
                "experimental_data": self.optimizer.experimental_data.to_dict(
                    "records"
                ),
                "iteration_history": self.optimizer.iteration_history,
                "hypervolume_data": {
                    "current_hypervolume": current_hypervolume,
                    "progress_summary": hypervolume_summary,
                    "convergence_analysis": convergence_data,
                    "calculation_timestamp": datetime.now().isoformat(),
                },
                "metadata": {
                    "save_timestamp": datetime.now().isoformat(),
                    "version": "3.6.6",  # Increment version for constraint implementation
                    "has_hypervolume_cache": True,
                },
            }

            with open(filepath, "wb") as f:
                pickle.dump(save_data, f, protocol=pickle.HIGHEST_PROTOCOL)

            logger.info(f"Optimization saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save optimization: {e}")
            return False

    def save_suggestions_to_csv(
        self, suggestions: List[Dict[str, Any]], filepath: Union[str, Path]
    ) -> bool:
        """Save a list of suggestions to a CSV file."""
        if not suggestions:
            logger.warning("No suggestions to save to CSV.")
            return False

        try:
            filepath = Path(filepath)
            suggestions_df = pd.DataFrame(suggestions)

            # Ensure all parameter columns are present, even if empty for some
            # suggestions
            all_param_names = list(self.optimizer.params_config.keys())
            for param_name in all_param_names:
                if param_name not in suggestions_df.columns:
                    # Add missing parameter columns as NaN
                    suggestions_df[param_name] = np.nan

            # Add response columns with NaN values
            all_response_names = list(self.optimizer.responses_config.keys())
            for response_name in all_response_names:
                if response_name not in suggestions_df.columns:
                    suggestions_df[response_name] = np.nan

            # Reorder columns to have parameters first, then responses
            ordered_columns = all_param_names + all_response_names
            suggestions_df = suggestions_df[ordered_columns]

            suggestions_df.to_csv(filepath, index=False)
            logger.info(f"Suggestions saved to CSV: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving suggestions to CSV: {e}", exc_info=True)
            if hasattr(self.view, "show_error"):
                self.view.show_error(
                    "CSV Export Error", f"Failed to save suggestions to CSV: {e}"
                )
            return False

    def load_optimization_from_file(self, filepath: Union[str, Path]) -> bool:
        """Load optimization state from file"""
        try:
            filepath = Path(filepath)

            with open(filepath, "rb") as f:
                save_data = pickle.load(f)

            # Import optimizer here to avoid issues
            from .optimizer import EnhancedMultiObjectiveOptimizer
            from .orchestrator import OptimizationOrchestrator

            # Create new base optimizer
            base_optimizer = EnhancedMultiObjectiveOptimizer(
                params_config=save_data["params_config"],
                responses_config=save_data["responses_config"],
                general_constraints=save_data["general_constraints"],
            )
            
            # Wrap with intelligent orchestrator for hybrid sequential/parallel capabilities
            self.optimizer = OptimizationOrchestrator(
                base_optimizer=base_optimizer,
                enable_parallel=True,
                n_workers=None
            )

            # Check if we have cached hypervolume data to avoid recalculation
            has_hypervolume_cache = save_data.get("metadata", {}).get(
                "has_hypervolume_cache", False
            )
            cached_hypervolume_data = save_data.get("hypervolume_data", {})

            # Restore experimental data
            if save_data["experimental_data"]:
                # Temporarily store the full experimental data
                full_experimental_data = pd.DataFrame(save_data["experimental_data"])

                if has_hypervolume_cache and save_data.get("iteration_history"):
                    # We have cached hypervolume data, restore directly without recalculation
                    logger.info(
                        "Loading with cached hypervolume data - skipping recalculation"
                    )
                    self.optimizer.experimental_data = full_experimental_data
                    self.optimizer.iteration_history = save_data["iteration_history"]

                    # Store cached hypervolume data in optimizer for quick access
                    if hasattr(self.optimizer, "set_cached_hypervolume_data"):
                        self.optimizer.set_cached_hypervolume_data(
                            cached_hypervolume_data
                        )

                    logger.info(
                        f"Loaded {len(full_experimental_data)} experiments with cached hypervolume data"
                    )
                else:
                    # No cache or old format, recalculate by adding data incrementally
                    logger.info(
                        "No hypervolume cache found - recalculating hypervolume for each iteration"
                    )
                    # Clear optimizer's experimental data and iteration history to re-add incrementally
                    self.optimizer.experimental_data = pd.DataFrame()
                    self.optimizer.iteration_history = []

                    for index, row in full_experimental_data.iterrows():
                        # Add each row individually to trigger hypervolume calculation for each step
                        self.optimizer.add_experimental_data(
                            pd.DataFrame([row.to_dict()])
                        )

            # Reinitialize plotting after loading
            try:
                from ..utils.plotting import SimplePlotManager

                self.plot_manager = SimplePlotManager(self.optimizer)
                logger.info("Plot manager reinitialized after loading.")
                logger.info("Loaded optimization using standard Bayesian optimization")
            except ImportError as ie:
                logger.warning(
                    f"No plotting modules available after loading: {ie}. Plotting functionalities will be limited."
                )
                self.plot_manager = None

            # Update view's plot manager reference
            if hasattr(self.view, "set_plot_manager") and self.plot_manager:
                self.view.set_plot_manager(self.plot_manager)
                logger.info("Plot manager reference updated in view")

            # Create main interface with loaded configs
            if hasattr(self.view, "create_main_interface"):
                self.view.create_main_interface(
                    save_data["params_config"], save_data["responses_config"]
                )
                logger.info("Main interface recreated after loading")

            # Update status after loading
            if hasattr(self.view, "set_status"):
                data_count = (
                    len(self.optimizer.experimental_data)
                    if hasattr(self.optimizer, "experimental_data")
                    else 0
                )
                self.view.set_status(f"Loaded optimization ({data_count} experiments)")

            # Update view
            self._schedule_view_update()

            logger.info(f"Optimization loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to load optimization: {e}")
            return False

    def add_batch_data_from_csv(self, filepath: Union[str, Path]) -> bool:
        """Add batch experimental data from CSV file with enhanced validation"""
        try:
            filepath = Path(filepath)
            data_df = pd.read_csv(filepath)

            # Validate data structure
            required_params = set(self.optimizer.params_config.keys())
            required_responses = set(self.optimizer.responses_config.keys())
            available_cols = set(data_df.columns)

            if not required_params.issubset(available_cols):
                missing = required_params - available_cols
                raise ValueError(f"Missing required parameter columns: {missing}")

            # Check for at least one response column
            available_responses = required_responses.intersection(available_cols)
            if not available_responses:
                raise ValueError(
                    f"No response columns found. Expected one of: {required_responses}"
                )

            # Enhanced data validation and type conversion
            logger.info(f"Validating and converting data types for {len(data_df)} rows")

            # Clean and validate parameter columns
            for param_name in required_params:
                if param_name in data_df.columns:
                    # Convert to numeric, coerce errors to NaN
                    data_df[param_name] = pd.to_numeric(
                        data_df[param_name], errors="coerce"
                    )

                    # Check for NaN values
                    nan_count = data_df[param_name].isna().sum()
                    if nan_count > 0:
                        logger.warning(
                            f"Parameter '{param_name}' has {nan_count} non-numeric values converted to NaN"
                        )

                    # Validate parameter bounds if specified
                    param_config = self.optimizer.params_config[param_name]
                    if "bounds" in param_config:
                        min_val, max_val = param_config["bounds"]
                        out_of_bounds = (
                            (data_df[param_name] < min_val)
                            | (data_df[param_name] > max_val)
                        ).sum()
                        if out_of_bounds > 0:
                            logger.warning(
                                f"Parameter '{param_name}' has {out_of_bounds} values outside bounds [{min_val}, {max_val}]"
                            )

            # Clean and validate response columns
            for response_name in available_responses:
                if response_name in data_df.columns:
                    # Handle potential list/dict values in responses (flatten if needed)
                    if data_df[response_name].dtype == "object":
                        # Check if any values are lists or dicts
                        sample_values = data_df[response_name].dropna().iloc[:5]
                        has_complex_values = any(
                            isinstance(val, (list, dict)) for val in sample_values
                        )

                        if has_complex_values:
                            logger.info(
                                f"Response '{response_name}' contains complex values, attempting to flatten"
                            )
                            # Flatten complex values - take mean of lists, extract single values from dicts
                            data_df[response_name] = data_df[response_name].apply(
                                lambda x: (
                                    np.mean(x)
                                    if isinstance(x, list) and x
                                    else (
                                        list(x.values())[0]
                                        if isinstance(x, dict) and x
                                        else x
                                    )
                                )
                            )

                    # Convert to numeric
                    data_df[response_name] = pd.to_numeric(
                        data_df[response_name], errors="coerce"
                    )

                    # Check for NaN values
                    nan_count = data_df[response_name].isna().sum()
                    if nan_count > 0:
                        logger.warning(
                            f"Response '{response_name}' has {nan_count} non-numeric values converted to NaN"
                        )

            # Remove rows with any NaN values in critical columns
            critical_columns = list(required_params) + list(available_responses)
            initial_rows = len(data_df)
            data_df = data_df.dropna(subset=critical_columns)
            final_rows = len(data_df)

            if final_rows < initial_rows:
                logger.warning(
                    f"Removed {initial_rows - final_rows} rows with missing/invalid data"
                )

            if final_rows == 0:
                raise ValueError("No valid data rows remaining after cleaning")

            # Final validation - ensure all values are proper numeric types
            for col in critical_columns:
                if col in data_df.columns:
                    if not pd.api.types.is_numeric_dtype(data_df[col]):
                        raise ValueError(
                            f"Column '{col}' contains non-numeric data after conversion"
                        )

            logger.info(f"Data validation complete. Processing {final_rows} clean rows")

            # Add data to optimizer
            self.optimizer.add_experimental_data(data_df)

            # Update view
            self.update_view()

            logger.info(
                f"Successfully imported {final_rows} experiments from {filepath}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to import batch data: {e}", exc_info=True)
            if hasattr(self.view, "show_error"):
                self.view.show_error("Import Error", f"Failed to import data: {e}")
            return False

    def start_sglbo_screening(self, config: Dict[str, Any]) -> None:
        """
        Start SGLBO screening optimization with the provided configuration.
        
        Args:
            config: Dictionary containing parameters, responses, and SGLBO settings
        """
        try:
            self._set_busy(True)
            logger.info("Starting SGLBO screening optimization")
            
            # Extract configuration
            params_config = config.get("parameters", {})
            responses_config = config.get("responses", {})
            sglbo_settings = config.get("sglbo_settings", {
                "gradient_step_size": 0.1,
                "exploration_factor": 0.15,
                "max_iterations": 20,
                "convergence_threshold": 0.02,
                "n_initial_samples": 8,
                "random_seed": None
            })
            
            if not params_config or not responses_config:
                raise ValueError("Invalid configuration: missing parameters or responses")
            
            logger.info(f"SGLBO Config: {len(params_config)} parameters, {len(responses_config)} responses")
            
            # Import screening modules
            from ..screening.screening_optimizer import ScreeningOptimizer
            from ..screening.screening_results import ScreeningResults
            from ..screening.design_space_generator import DesignSpaceGenerator
            from ..screening.parameter_handler import ParameterHandler
            
            # Initialize screening optimizer
            self.screening_optimizer = ScreeningOptimizer(
                params_config=params_config,
                responses_config=responses_config,
                gradient_step_size=sglbo_settings.get("gradient_step_size", 0.1),
                exploration_factor=sglbo_settings.get("exploration_factor", 0.15),
                max_iterations=sglbo_settings.get("max_iterations", 20),
                convergence_threshold=sglbo_settings.get("convergence_threshold", 0.02),
                n_initial_samples=sglbo_settings.get("n_initial_samples", 8),
                random_seed=sglbo_settings.get("random_seed")
            )
            
            # Initialize results manager
            self.screening_results = ScreeningResults(params_config, responses_config)
            
            # Initialize parameter handler and design generator
            param_handler = ParameterHandler(params_config, allow_extrapolation=True)
            self.design_generator = DesignSpaceGenerator(param_handler)
            
            # Update view status
            if hasattr(self.view, "set_status"):
                self.view.set_status("SGLBO screening optimizer initialized")
            
            # Show screening execution window if available
            if hasattr(self.view, '_show_advanced_screening_execution_window'):
                self.view._show_advanced_screening_execution_window(
                    screening_optimizer=self.screening_optimizer,
                    results_manager=self.screening_results,
                    design_generator=self.design_generator,
                    config=config
                )
            else:
                # Run basic screening process
                self._run_basic_screening_process(config)
                
        except Exception as e:
            logger.error(f"Failed to start SGLBO screening: {e}", exc_info=True)
            if hasattr(self.view, "show_error"):
                self.view.show_error(
                    "SGLBO Screening Error", 
                    f"Failed to start SGLBO screening: {e}"
                )
        finally:
            self._set_busy(False)
    
    def _run_basic_screening_process(self, config: Dict[str, Any]) -> None:
        """
        Run basic screening process without advanced GUI.
        
        Args:
            config: Screening configuration
        """
        try:
            logger.info("Running basic SGLBO screening process")
            
            # Generate initial experiments
            initial_experiments = self.screening_optimizer.suggest_initial_experiments()
            logger.info(f"Generated {len(initial_experiments)} initial experiments")
            
            # For demonstration, we'll simulate the first few experiments
            # In real usage, these would come from actual experiments
            if hasattr(self.view, 'show_info'):
                message = f"""SGLBO Screening Started Successfully!

Configuration:
- Parameters: {len(config['parameters'])}
- Responses: {len(config['responses'])}
- Initial experiments: {len(initial_experiments)}

Next Steps:
1. Run the initial {len(initial_experiments)} experiments
2. Add results using batch data import
3. Continue screening iterations
4. Generate design space for detailed optimization

The screening optimizer is now ready to accept experimental data."""
                
                self.view.show_info("SGLBO Screening Ready", message)
            
            # Update status
            if hasattr(self.view, "set_status"):
                self.view.set_status(f"SGLBO screening ready - {len(initial_experiments)} initial experiments generated")
                
        except Exception as e:
            logger.error(f"Error in basic screening process: {e}")
            raise
    
    # ====================================================================================
    # NEW PARALLEL OPTIMIZATION CAPABILITIES
    # ====================================================================================
    
    def benchmark_optimization_strategies(self, 
                                        strategies: List[str],
                                        n_suggestions: int = 10,
                                        parallel: bool = True) -> Dict[str, Any]:
        """
        Benchmark multiple optimization strategies in parallel.
        
        Args:
            strategies: List of strategy names to benchmark ('ehvi', 'ei', 'random', etc.)
            n_suggestions: Number of suggestions per strategy
            parallel: Whether to run in parallel (True by default)
            
        Returns:
            Dictionary with benchmark results for each strategy
        """
        if not self.has_optimizer:
            raise ValueError("No optimizer initialized. Please create an optimization session first.")
        
        try:
            self._set_busy(True)
            self.view.set_status("Running strategy benchmarking...")
            
            logger.info(f"Benchmarking {len(strategies)} strategies with {n_suggestions} suggestions each")
            
            # Use orchestrator's benchmarking capability
            results = self.optimizer.benchmark_strategies(
                strategies=strategies,
                n_suggestions=n_suggestions,
                parallel=parallel
            )
            
            logger.info(f"Benchmarking completed for {len(results)} strategies")
            self.view.set_status("Strategy benchmarking completed")
            
            return results
            
        except Exception as e:
            error_msg = f"Error in strategy benchmarking: {str(e)}"
            logger.error(error_msg)
            self.view.show_error("Benchmarking Error", error_msg)
            raise
        finally:
            self._set_busy(False)
    
    def run_what_if_analysis(self,
                            scenarios: List[Dict],
                            parallel: bool = True) -> Dict[str, Any]:
        """
        Run what-if analysis scenarios in parallel.
        
        Args:
            scenarios: List of scenario configurations
            parallel: Whether to run in parallel (True by default)
            
        Returns:
            Dictionary with results for each scenario
        """
        if not self.has_optimizer:
            raise ValueError("No optimizer initialized. Please create an optimization session first.")
        
        try:
            self._set_busy(True)
            self.view.set_status("Running what-if analysis...")
            
            logger.info(f"Running what-if analysis with {len(scenarios)} scenarios")
            
            # Use orchestrator's what-if analysis capability
            results = self.optimizer.run_what_if_analysis(
                scenarios=scenarios,
                parallel=parallel
            )
            
            logger.info(f"What-if analysis completed for {len(results)} scenarios")
            self.view.set_status("What-if analysis completed")
            
            return results
            
        except Exception as e:
            error_msg = f"Error in what-if analysis: {str(e)}"
            logger.error(error_msg)
            self.view.show_error("What-if Analysis Error", error_msg)
            raise
        finally:
            self._set_busy(False)
    
    def load_large_dataset_parallel(self,
                                   data_df: pd.DataFrame,
                                   chunk_size: int = 1000) -> Dict[str, Any]:
        """
        Load large historical datasets in parallel for faster processing.
        
        Args:
            data_df: Historical data to load
            chunk_size: Size of data chunks for parallel processing
            
        Returns:
            Summary of parallel loading results
        """
        if not self.has_optimizer:
            raise ValueError("No optimizer initialized. Please create an optimization session first.")
        
        try:
            self._set_busy(True)
            self.view.set_status(f"Loading {len(data_df)} data points in parallel...")
            
            logger.info(f"Loading large dataset with {len(data_df)} points in parallel")
            
            # Use orchestrator's parallel data loading capability
            results = self.optimizer.load_historical_data_parallel(
                data_df=data_df,
                chunk_size=chunk_size
            )
            
            logger.info(f"Parallel data loading completed: {results}")
            self.view.set_status("Large dataset loaded successfully")
            
            # Update displays after loading
            if hasattr(self.view, 'update_displays'):
                self.view.update_displays(self.optimizer.base_optimizer)
            
            return results
            
        except Exception as e:
            error_msg = f"Error in parallel data loading: {str(e)}"
            logger.error(error_msg)
            self.view.show_error("Data Loading Error", error_msg)
            raise
        finally:
            self._set_busy(False)
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics from the optimization orchestrator.
        
        Returns:
            Dictionary with performance and usage statistics
        """
        if not self.has_optimizer:
            return {"error": "No optimizer initialized"}
        
        try:
            if hasattr(self.optimizer, 'get_execution_stats'):
                stats = self.optimizer.get_execution_stats()
                logger.info(f"Orchestrator stats: {stats}")
                return stats
            else:
                return {"error": "Orchestrator not available"}
        except Exception as e:
            logger.error(f"Error getting orchestrator stats: {e}")
            return {"error": str(e)}
    
    def set_parallel_optimization_enabled(self, enabled: bool):
        """
        Enable or disable parallel optimization capabilities.
        
        Args:
            enabled: True to enable parallel optimization, False to disable
        """
        if not self.has_optimizer:
            logger.warning("No optimizer initialized, cannot change parallel settings")
            return
        
        try:
            if hasattr(self.optimizer, 'set_parallel_enabled'):
                self.optimizer.set_parallel_enabled(enabled)
                status = "enabled" if enabled else "disabled"
                logger.info(f"Parallel optimization {status}")
                self.view.set_status(f"Parallel optimization {status}")
            else:
                logger.warning("Orchestrator not available, cannot change parallel settings")
        except Exception as e:
            logger.error(f"Error changing parallel settings: {e}")
            self.view.show_error("Settings Error", f"Failed to change parallel settings: {str(e)}")
    
    def clear_optimization_cache(self):
        """Clear all optimization caches to free memory."""
        if not self.has_optimizer:
            logger.warning("No optimizer initialized, cannot clear cache")
            return
        
        try:
            if hasattr(self.optimizer, 'clear_cache'):
                self.optimizer.clear_cache()
                logger.info("Optimization cache cleared")
                self.view.set_status("Cache cleared")
            else:
                logger.warning("Orchestrator not available, cannot clear cache")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            self.view.show_error("Cache Error", f"Failed to clear cache: {str(e)}")
    
    # ====================================================================================
    # ENHANCED VALIDATION CAPABILITIES
    # ====================================================================================
    
    def run_enhanced_validation(self, 
                               test_functions: List[str],
                               algorithms: List[str],
                               n_evaluations: int,
                               n_runs: int = 10,
                               parallel: bool = True) -> Dict[str, Any]:
        """
        Run unified algorithm verification with new system.
        
        Args:
            test_functions: List of test function names
            algorithms: List of algorithm names
            n_evaluations: Number of evaluations per run
            n_runs: Number of independent runs
            parallel: Enable parallel execution
            
        Returns:
            Verification results
        """
        try:
            self._set_busy(True)
            self.view.set_status("Running algorithm verification...")
            
            logger.info(f"Starting algorithm verification: {len(test_functions)} test functions, "
                       f"{len(algorithms)} algorithms, {n_runs} runs each")
            
            # Import new unified verification engine
            from .algorithm_verifier import AlgorithmVerifier, VerificationConfig
            
            # Create verifier
            verifier = AlgorithmVerifier(gpu_acceleration=True)
            
            # Create configuration
            config = VerificationConfig(
                test_functions=test_functions,
                algorithms=algorithms,
                n_evaluations=n_evaluations,
                n_runs=n_runs,
                execution_mode="parallel" if parallel else "sequential",
                gpu_acceleration=True,
                statistical_tests=True
            )
            
            # Run verification
            results = verifier.verify_algorithms(config)
            
            logger.info("Enhanced validation completed successfully")
            self.view.set_status("Enhanced validation completed")
            
            return results
            
        except Exception as e:
            error_msg = f"Error in enhanced validation: {str(e)}"
            logger.error(error_msg)
            self.view.show_error("Validation Error", error_msg)
            raise
        finally:
            self._set_busy(False)
    
    def run_quick_validation_test(self, 
                                algorithms: List[str] = None,
                                test_function: str = "ZDT1",
                                n_evaluations: int = 50,
                                n_runs: int = 5) -> Dict[str, Any]:
        """
        Run a quick validation test for testing and demonstration.
        
        Args:
            algorithms: List of algorithm names (defaults to all available)
            test_function: Test function name
            n_evaluations: Number of evaluations per run
            n_runs: Number of runs
            
        Returns:
            Quick validation results
        """
        if algorithms is None:
            algorithms = ["This App's MOBO", "Random Search"]
        
        try:
            self._set_busy(True)
            self.view.set_status("Running quick validation test...")
            
            logger.info(f"Starting quick validation test with {algorithms}")
            
            # Import new unified verification engine
            from .algorithm_verifier import AlgorithmVerifier
            
            # Create verifier
            verifier = AlgorithmVerifier(gpu_acceleration=True)
            
            # Run quick test
            results = verifier.quick_verification(
                test_function=test_function,
                algorithms=algorithms,
                n_evaluations=n_evaluations,
                n_runs=n_runs
            )
            
            logger.info("Quick validation test completed")
            self.view.set_status("Quick validation completed")
            
            return results
            
        except Exception as e:
            error_msg = f"Error in quick validation: {str(e)}"
            logger.error(error_msg)
            self.view.show_error("Quick Validation Error", error_msg)
            raise
        finally:
            self._set_busy(False)
    
    def get_validation_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics from validation engine.
        
        Returns:
            Validation execution statistics
        """
        try:
            # Import and create validation engine
            from .validation_engine import EnhancedValidationEngine
            validation_engine = EnhancedValidationEngine()
            
            return validation_engine.get_execution_stats()
            
        except Exception as e:
            logger.error(f"Error getting validation stats: {e}")
            return {'error': str(e)}
    
    def export_validation_results(self, results: Dict[str, Any], file_path: str) -> bool:
        """
        Export validation results to file.
        
        Args:
            results: Validation results dictionary
            file_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            from pathlib import Path
            
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Export results
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Validation results exported to {file_path}")
            self.view.set_status(f"Results exported to {Path(file_path).name}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error exporting validation results: {str(e)}"
            logger.error(error_msg)
            self.view.show_error("Export Error", error_msg)
            return False

    def correct_last_result(self, new_values: Dict[str, float]) -> bool:
        """
        Correct the last experimental result for sequential Bayesian optimization.
        
        This method implements Solution 1: Last Result Correction as described in
        academic literature for handling data entry errors in sequential optimization.
        It only allows correction of the most recent result to maintain scientific
        integrity while addressing practical data entry issues.
        
        Args:
            new_values: Dictionary mapping column names to corrected values
            
        Returns:
            True if correction successful, False otherwise
            
        Raises:
            ValueError: If no experimental data exists or correction is invalid
        """
        try:
            with self._thread_lock:
                # Validate prerequisites
                if not self.has_optimizer or not self.has_data:
                    raise ValueError("No optimization session or experimental data available")
                
                if len(self.optimizer.experimental_data) == 0:
                    raise ValueError("No experimental data to correct")
                
                # Get current data
                experimental_data = self.optimizer.experimental_data.copy()
                original_last_row = experimental_data.iloc[-1].copy()
                
                # Validate correction values
                for column, value in new_values.items():
                    if column not in experimental_data.columns:
                        raise ValueError(f"Column '{column}' not found in experimental data")
                    
                    if not isinstance(value, (int, float)) or np.isnan(value) or np.isinf(value):
                        raise ValueError(f"Invalid value for '{column}': {value}")
                
                # Log the correction operation for audit trail
                logger.info(f"Last Result Correction initiated:")
                logger.info(f"Original values: {original_last_row[list(new_values.keys())].to_dict()}")
                logger.info(f"Corrected values: {new_values}")
                
                # Apply corrections to the last row
                for column, value in new_values.items():
                    experimental_data.iloc[-1, experimental_data.columns.get_loc(column)] = value
                
                # Validate the corrected data scientifically
                corrected_row = experimental_data.iloc[-1]
                
                # Check for reasonable parameter bounds (with robust attribute access)
                try:
                    # Try to get parameter names through different possible attributes
                    if hasattr(self.optimizer, 'parameter_names'):
                        param_names = self.optimizer.parameter_names
                    elif hasattr(self.optimizer, 'base_optimizer') and hasattr(self.optimizer.base_optimizer, 'parameter_names'):
                        param_names = self.optimizer.base_optimizer.parameter_names
                    else:
                        # Fallback: infer from experimental data columns
                        param_names = [col for col in experimental_data.columns if col not in self.optimizer.objective_names]
                    
                    # Try to get parameter config through different possible attributes
                    if hasattr(self.optimizer, 'params_config'):
                        params_config = self.optimizer.params_config
                    elif hasattr(self.optimizer, 'base_optimizer') and hasattr(self.optimizer.base_optimizer, 'params_config'):
                        params_config = self.optimizer.base_optimizer.params_config
                    else:
                        params_config = {}
                        logger.warning("Parameter config not found, skipping bounds validation")
                    
                    # Validate parameter bounds if config is available
                    for param_name in param_names:
                        if param_name in new_values and param_name in params_config:
                            param_config = params_config[param_name]
                            value = corrected_row[param_name]
                            
                            if param_config['type'] in ['continuous', 'integer']:
                                if not (param_config['bounds'][0] <= value <= param_config['bounds'][1]):
                                    raise ValueError(f"Corrected value {value} for '{param_name}' outside bounds {param_config['bounds']}")
                            
                            elif param_config['type'] == 'categorical':
                                if value not in param_config['choices']:
                                    raise ValueError(f"Corrected value '{value}' for '{param_name}' not in choices {param_config['choices']}")
                
                except Exception as validation_error:
                    logger.warning(f"Parameter validation failed: {validation_error}. Proceeding without bounds check.")
                
                # Update optimizer's experimental data
                self.optimizer.experimental_data = experimental_data
                
                # Clear existing models to force retraining on next suggestion
                try:
                    # Clear model caches to ensure fresh training with corrected data
                    if hasattr(self.optimizer, 'models'):
                        self.optimizer.models = {}
                    elif hasattr(self.optimizer, 'base_optimizer') and hasattr(self.optimizer.base_optimizer, 'models'):
                        self.optimizer.base_optimizer.models = {}
                    
                    # Clear training data caches to force reload
                    train_attrs = ['train_X', 'train_Y', '_train_X', '_train_Y', 'fitted_models']
                    for attr in train_attrs:
                        if hasattr(self.optimizer, attr):
                            setattr(self.optimizer, attr, None)
                        elif hasattr(self.optimizer, 'base_optimizer') and hasattr(self.optimizer.base_optimizer, attr):
                            setattr(self.optimizer.base_optimizer, attr, None)
                    
                    logger.info("GP models cleared successfully - will retrain with corrected data on next suggestion")
                    
                except Exception as model_error:
                    logger.debug(f"Model clearing failed: {model_error}. Models will still retrain on next suggestion.")
                
                # Update plot manager if available
                if self.plot_manager:
                    try:
                        self.plot_manager.optimizer = self.optimizer
                        logger.info("Plot manager updated with corrected data")
                    except Exception as plot_error:
                        logger.warning(f"Plot manager update failed: {plot_error}")
                
                # Update view status
                correction_summary = ', '.join([f"{col}: {orig:.4f} → {new:.4f}" 
                                              for col, new in new_values.items() 
                                              for orig in [original_last_row[col]]])
                
                self.view.set_status(f"Last result corrected: {correction_summary}")
                
                logger.info("Last result correction completed successfully")
                return True
                
        except Exception as e:
            error_msg = f"Error correcting last result: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if hasattr(self.view, "show_error"):
                self.view.show_error("Correction Error", error_msg)
            
            return False
