"""
SGLBO Screening Optimizer

Implements Stochastic Gradient Line Bayesian Optimization (SGLBO) for efficient
parameter space screening. This is a lightweight screening method that combines
gradient information with Bayesian optimization for fast exploration.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Union
from scipy.optimize import minimize
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern, WhiteKernel
import warnings

from .parameter_handler import ParameterHandler

# Suppress sklearn warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

logger = logging.getLogger(__name__)


class ScreeningOptimizer:
    """
    SGLBO (Stochastic Gradient Line Bayesian Optimization) implementation
    for efficient parameter space screening.
    
    This optimizer performs fast, low-resolution exploration to identify
    promising regions before detailed optimization with the main BO software.
    """
    
    def __init__(
        self,
        params_config: Dict[str, Dict[str, Any]],
        responses_config: Dict[str, Dict[str, Any]],
        gradient_step_size: float = 0.1,
        exploration_factor: float = 0.1, 
        max_iterations: int = 50,
        convergence_threshold: float = 0.01,
        n_initial_samples: int = 5,
        random_seed: Optional[int] = None
    ):
        """
        Initialize SGLBO screening optimizer.
        
        Args:
            params_config: Parameter configuration matching main software format
            responses_config: Response configuration with optimization goals
            gradient_step_size: Step size for gradient-based moves
            exploration_factor: Balance between exploitation and exploration
            max_iterations: Maximum screening iterations
            convergence_threshold: Convergence criterion for screening
            n_initial_samples: Number of initial LHS samples
            random_seed: Random seed for reproducibility
        """
        self.params_config = params_config
        self.responses_config = responses_config
        self.gradient_step_size = gradient_step_size
        self.exploration_factor = exploration_factor
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        self.n_initial_samples = n_initial_samples
        
        # Initialize random seed
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Initialize parameter handler with extrapolation enabled for screening
        self.param_handler = ParameterHandler(params_config, allow_extrapolation=True)
        
        # Setup objectives from responses config
        self._setup_objectives()
        
        # Initialize data storage
        self.experimental_data = pd.DataFrame()
        self.iteration_history = []
        self.gp_models = {}
        self.current_best_params = None
        self.current_best_response = None
        self.converged = False
        
        logger.info(f"SGLBO Screening Optimizer initialized with {len(self.objective_names)} objectives")
    
    def _setup_objectives(self) -> None:
        """Setup optimization objectives from responses configuration."""
        self.objective_names = []
        self.objective_directions = []  # 1 for maximize, -1 for minimize
        self.target_values = {}
        
        for name, config in self.responses_config.items():
            goal = config.get("goal", "None")
            
            if goal == "Maximize":
                self.objective_names.append(name)
                self.objective_directions.append(1)
            elif goal == "Minimize":
                self.objective_names.append(name)
                self.objective_directions.append(-1)
            elif goal == "Target":
                self.objective_names.append(name)
                self.objective_directions.append(0)  # Special case for target
                if "target" in config:
                    self.target_values[name] = config["target"]
                else:
                    logger.warning(f"Target goal for '{name}' missing target value")
        
        if not self.objective_names:
            raise ValueError("At least one optimization objective must be defined")
    
    def add_experimental_data(self, data_df: pd.DataFrame) -> None:
        """
        Add experimental data to the screening optimizer.
        
        Args:
            data_df: DataFrame with parameter and response data
        """
        try:
            logger.info(f"Adding {len(data_df)} experimental data points to screening")
            
            # Validate data
            for param_name in self.param_handler.param_names:
                if param_name not in data_df.columns:
                    raise ValueError(f"Parameter '{param_name}' not found in data")
            
            for obj_name in self.objective_names:
                if obj_name not in data_df.columns:
                    raise ValueError(f"Objective '{obj_name}' not found in data")
            
            # Add data
            if self.experimental_data.empty:
                self.experimental_data = data_df.copy()
            else:
                self.experimental_data = pd.concat([self.experimental_data, data_df], ignore_index=True)
            
            # Update GP models
            self._update_gp_models()
            
            # Update best solution
            self._update_best_solution()
            
            logger.info(f"Total experimental data points: {len(self.experimental_data)}")
            
        except Exception as e:
            logger.error(f"Error adding experimental data: {e}")
            raise
    
    def _update_gp_models(self) -> None:
        """Update Gaussian Process models for each objective."""
        try:
            if len(self.experimental_data) < 3:
                logger.debug("Insufficient data for GP models")
                return
            
            # Prepare training data
            X_train = []
            for _, row in self.experimental_data.iterrows():
                param_dict = {name: row[name] for name in self.param_handler.param_names}
                X_normalized = self.param_handler.params_to_normalized(param_dict)
                X_train.append(X_normalized)
            
            X_train = np.array(X_train)
            
            # Build GP model for each objective
            for obj_name in self.objective_names:
                if obj_name not in self.experimental_data.columns:
                    continue
                
                y_train = self.experimental_data[obj_name].values
                
                # Handle missing values
                valid_mask = ~pd.isna(y_train)
                if np.sum(valid_mask) < 3:
                    logger.warning(f"Insufficient valid data for objective '{obj_name}'")
                    continue
                
                X_valid = X_train[valid_mask]
                y_valid = y_train[valid_mask]
                
                # Create GP model
                kernel = Matern(length_scale=0.5, nu=2.5) + WhiteKernel(noise_level=0.01)
                
                gp = GaussianProcessRegressor(
                    kernel=kernel,
                    n_restarts_optimizer=5,
                    alpha=1e-6,
                    normalize_y=True
                )
                
                try:
                    gp.fit(X_valid, y_valid)
                    self.gp_models[obj_name] = gp
                    logger.debug(f"GP model updated for objective '{obj_name}'")
                except Exception as e:
                    logger.warning(f"Failed to fit GP model for '{obj_name}': {e}")
            
        except Exception as e:
            logger.error(f"Error updating GP models: {e}")
    
    def _update_best_solution(self) -> None:
        """Update the current best solution based on objectives."""
        try:
            if self.experimental_data.empty:
                return
            
            # For single objective, find best directly
            if len(self.objective_names) == 1:
                obj_name = self.objective_names[0]
                direction = self.objective_directions[0]
                
                if direction == 1:  # Maximize
                    best_idx = self.experimental_data[obj_name].idxmax()
                elif direction == -1:  # Minimize
                    best_idx = self.experimental_data[obj_name].idxmin()
                else:  # Target
                    target_val = self.target_values.get(obj_name, 0)
                    deviations = np.abs(self.experimental_data[obj_name] - target_val)
                    best_idx = deviations.idxmin()
                
                best_row = self.experimental_data.loc[best_idx]
                self.current_best_params = {name: best_row[name] for name in self.param_handler.param_names}
                self.current_best_response = best_row[obj_name]
            
            else:
                # For multiple objectives, use simple weighted sum approach
                # (More sophisticated methods can be added later)
                composite_scores = np.zeros(len(self.experimental_data))
                
                for i, obj_name in enumerate(self.objective_names):
                    values = self.experimental_data[obj_name].values
                    direction = self.objective_directions[i]
                    
                    if direction == 1:  # Maximize
                        normalized_values = (values - values.min()) / (values.max() - values.min() + 1e-8)
                    elif direction == -1:  # Minimize
                        normalized_values = (values.max() - values) / (values.max() - values.min() + 1e-8)
                    else:  # Target
                        target_val = self.target_values.get(obj_name, values.mean())
                        deviations = np.abs(values - target_val)
                        normalized_values = 1.0 / (1.0 + deviations / (deviations.max() + 1e-8))
                    
                    composite_scores += normalized_values
                
                best_idx = np.argmax(composite_scores)
                best_row = self.experimental_data.iloc[best_idx]
                self.current_best_params = {name: best_row[name] for name in self.param_handler.param_names}
                self.current_best_response = composite_scores[best_idx]
            
            logger.debug(f"Best solution updated: {self.current_best_params}")
            
        except Exception as e:
            logger.error(f"Error updating best solution: {e}")
    
    def suggest_initial_experiments(self, n_suggestions: int = None) -> List[Dict[str, Any]]:
        """
        Suggest initial experiments using Latin Hypercube Sampling.
        
        Args:
            n_suggestions: Number of suggestions (uses n_initial_samples if None)
            
        Returns:
            List[Dict[str, Any]]: List of parameter dictionaries
        """
        if n_suggestions is None:
            n_suggestions = self.n_initial_samples
        
        logger.info(f"Generating {n_suggestions} initial experiment suggestions using LHS")
        return self.param_handler.generate_latin_hypercube_samples(n_suggestions)
    
    def _calculate_gradient(self, params_normalized: np.ndarray, obj_name: str) -> np.ndarray:
        """
        Calculate numerical gradient of the objective function at given parameters.
        
        Args:
            params_normalized: Parameter values in normalized space
            obj_name: Objective name to calculate gradient for
            
        Returns:
            np.ndarray: Gradient vector
        """
        try:
            if obj_name not in self.gp_models:
                logger.warning(f"No GP model available for objective '{obj_name}'")
                return np.zeros_like(params_normalized)
            
            gp_model = self.gp_models[obj_name]
            gradient = np.zeros_like(params_normalized)
            h = 1e-6  # Small step for numerical gradient
            
            # Calculate numerical gradient
            for i in range(len(params_normalized)):
                params_plus = params_normalized.copy()
                params_minus = params_normalized.copy()
                
                params_plus[i] = min(1.0, params_plus[i] + h)
                params_minus[i] = max(0.0, params_minus[i] - h)
                
                # Predict at both points
                pred_plus, _ = gp_model.predict([params_plus], return_std=True)
                pred_minus, _ = gp_model.predict([params_minus], return_std=True)
                
                # Calculate gradient component
                gradient[i] = (pred_plus[0] - pred_minus[0]) / (params_plus[i] - params_minus[i] + 1e-8)
            
            # Apply objective direction
            direction = self.objective_directions[self.objective_names.index(obj_name)]
            if direction == -1:  # Minimize -> negate gradient for ascent
                gradient = -gradient
            elif direction == 0:  # Target -> gradient toward target
                current_pred, _ = gp_model.predict([params_normalized], return_std=True)
                target_val = self.target_values.get(obj_name, current_pred[0])
                if current_pred[0] > target_val:
                    gradient = -gradient
            
            return gradient
            
        except Exception as e:
            logger.error(f"Error calculating gradient for '{obj_name}': {e}")
            return np.zeros_like(params_normalized)
    
    def _calculate_acquisition_function(self, params_normalized: np.ndarray) -> float:
        """
        Calculate acquisition function value (Upper Confidence Bound).
        
        Args:
            params_normalized: Parameter values in normalized space
            
        Returns:
            float: Acquisition function value
        """
        try:
            if not self.gp_models:
                return 0.0
            
            total_acquisition = 0.0
            
            for obj_name in self.objective_names:
                if obj_name not in self.gp_models:
                    continue
                
                gp_model = self.gp_models[obj_name]
                
                # Predict mean and standard deviation
                mean, std = gp_model.predict([params_normalized], return_std=True)
                mean = mean[0]
                std = std[0]
                
                # Upper Confidence Bound acquisition function
                acquisition = mean + self.exploration_factor * std
                
                # Apply objective direction
                direction = self.objective_directions[self.objective_names.index(obj_name)]
                if direction == -1:  # Minimize
                    acquisition = -acquisition
                elif direction == 0:  # Target
                    target_val = self.target_values.get(obj_name, mean)
                    acquisition = -abs(mean - target_val) + self.exploration_factor * std
                
                total_acquisition += acquisition
            
            return total_acquisition / len(self.gp_models)
            
        except Exception as e:
            logger.error(f"Error calculating acquisition function: {e}")
            return 0.0
    
    def _sglbo_step(self, current_params_normalized: np.ndarray) -> np.ndarray:
        """
        Perform one SGLBO step combining gradient information with Bayesian optimization.
        
        Args:
            current_params_normalized: Current parameter values in normalized space
            
        Returns:
            np.ndarray: New parameter values in normalized space
        """
        try:
            # Calculate composite gradient from all objectives
            composite_gradient = np.zeros_like(current_params_normalized)
            
            for obj_name in self.objective_names:
                if obj_name in self.gp_models:
                    gradient = self._calculate_gradient(current_params_normalized, obj_name)
                    composite_gradient += gradient
            
            # Normalize gradient
            gradient_norm = np.linalg.norm(composite_gradient)
            if gradient_norm > 1e-8:
                composite_gradient = composite_gradient / gradient_norm
            
            # Gradient-based candidate (allow extrapolation beyond [0,1] for screening)
            gradient_candidate = current_params_normalized + self.gradient_step_size * composite_gradient
            # Don't clip for screening - extrapolation enabled by parameter handler
            
            # Random exploration candidate
            random_candidate = np.random.random(len(current_params_normalized))
            
            # Evaluate both candidates using acquisition function
            gradient_acq = self._calculate_acquisition_function(gradient_candidate)
            random_acq = self._calculate_acquisition_function(random_candidate)
            
            # Choose best candidate
            if gradient_acq >= random_acq:
                next_params = gradient_candidate
                logger.debug("Selected gradient-based candidate")
            else:
                next_params = random_candidate
                logger.debug("Selected random exploration candidate")
            
            return next_params
            
        except Exception as e:
            logger.error(f"Error in SGLBO step: {e}")
            return current_params_normalized
    
    def suggest_next_experiment(self) -> Dict[str, Any]:
        """
        Suggest the next experiment using SGLBO.
        
        Returns:
            Dict[str, Any]: Parameter dictionary for next experiment
        """
        try:
            # If insufficient data, use initial sampling
            if len(self.experimental_data) < self.n_initial_samples:
                remaining = self.n_initial_samples - len(self.experimental_data)
                suggestions = self.suggest_initial_experiments(remaining)
                if suggestions:
                    logger.info("Using initial sampling - insufficient data for SGLBO")
                    return suggestions[0]
            
            # Use current best as starting point, or random if no best available
            if self.current_best_params is not None:
                current_normalized = self.param_handler.params_to_normalized(self.current_best_params)
            else:
                current_normalized = np.random.random(self.param_handler.n_params)
            
            # Perform SGLBO step
            next_normalized = self._sglbo_step(current_normalized)
            
            # Convert back to parameter dictionary
            next_params = self.param_handler.normalized_to_params(next_normalized)
            
            logger.info("Generated SGLBO-based experiment suggestion")
            return next_params
            
        except Exception as e:
            logger.error(f"Error suggesting next experiment: {e}")
            # Fallback to random sampling
            random_samples = self.param_handler.generate_random_samples(1)
            return random_samples[0] if random_samples else {}
    
    def check_convergence(self) -> Dict[str, Any]:
        """
        Check if the screening process has converged.
        
        Returns:
            Dict[str, Any]: Convergence status and metrics
        """
        convergence_info = {
            "converged": False,
            "iterations": len(self.iteration_history),
            "improvement": 0.0,
            "recommendation": "continue"
        }
        
        try:
            if len(self.iteration_history) < 3:
                convergence_info["recommendation"] = "continue - insufficient iterations"
                return convergence_info
            
            # Check improvement over recent iterations
            recent_window = min(5, len(self.iteration_history))
            recent_scores = [iter_data.get("best_score", 0) for iter_data in self.iteration_history[-recent_window:]]
            
            if len(recent_scores) >= 2:
                max_score = max(recent_scores)
                min_score = min(recent_scores)
                
                if max_score > 1e-8:
                    relative_improvement = (max_score - min_score) / max_score
                    convergence_info["improvement"] = relative_improvement
                    
                    if relative_improvement < self.convergence_threshold:
                        convergence_info["converged"] = True
                        convergence_info["recommendation"] = "converged - proceed to design space generation"
                        self.converged = True
                    else:
                        convergence_info["recommendation"] = "continue - still improving"
            
            # Check maximum iterations
            if len(self.iteration_history) >= self.max_iterations:
                convergence_info["converged"] = True
                convergence_info["recommendation"] = "max iterations reached - proceed to design space generation"
                self.converged = True
            
            return convergence_info
            
        except Exception as e:
            logger.error(f"Error checking convergence: {e}")
            convergence_info["recommendation"] = "continue - error in convergence check"
            return convergence_info
    
    def get_screening_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the screening optimization results.
        
        Returns:
            Dict[str, Any]: Screening summary information
        """
        summary = {
            "total_experiments": len(self.experimental_data),
            "iterations_completed": len(self.iteration_history),
            "converged": self.converged,
            "best_parameters": self.current_best_params,
            "best_response": self.current_best_response,
            "objectives": self.objective_names,
            "parameter_ranges": {}
        }
        
        try:
            # Add parameter ranges explored
            if not self.experimental_data.empty:
                for param_name in self.param_handler.param_names:
                    values = self.experimental_data[param_name]
                    param_config = self.params_config[param_name]
                    
                    if param_config["type"] == "categorical":
                        # For categorical parameters, show unique values
                        unique_values = values.unique().tolist()
                        summary["parameter_ranges"][param_name] = {
                            "type": "categorical",
                            "values_explored": unique_values,
                            "count": len(unique_values)
                        }
                    else:
                        # For continuous/discrete parameters, show numerical stats
                        summary["parameter_ranges"][param_name] = {
                            "type": param_config["type"],
                            "min": float(values.min()),
                            "max": float(values.max()),
                            "mean": float(values.mean()),
                            "std": float(values.std())
                        }
            
            # Add objective performance
            if not self.experimental_data.empty:
                summary["objective_performance"] = {}
                for obj_name in self.objective_names:
                    if obj_name in self.experimental_data.columns:
                        values = self.experimental_data[obj_name]
                        summary["objective_performance"][obj_name] = {
                            "min": float(values.min()),
                            "max": float(values.max()),
                            "mean": float(values.mean()),
                            "std": float(values.std()),
                            "best": float(values.max() if self.objective_directions[self.objective_names.index(obj_name)] == 1 else values.min())
                        }
            
            # Add parameter space exploration summary
            summary["parameter_space_exploration"] = self.param_handler.get_exploration_summary()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating screening summary: {e}")
            # Still add parameter space exploration even on error
            try:
                summary["parameter_space_exploration"] = self.param_handler.get_exploration_summary()
            except:
                summary["parameter_space_exploration"] = {"expanded_parameters": [], "extrapolation_enabled": True}
            return summary
    
    def run_screening_iteration(self) -> Dict[str, Any]:
        """
        Run one complete screening iteration (suggest -> wait for data -> analyze).
        This method is called after experimental data has been added.
        
        Returns:
            Dict[str, Any]: Iteration results and status
        """
        try:
            iteration_num = len(self.iteration_history) + 1
            
            # Record iteration data
            iteration_data = {
                "iteration": iteration_num,
                "total_experiments": len(self.experimental_data),
                "best_params": self.current_best_params,
                "best_score": self.current_best_response,
                "models_available": list(self.gp_models.keys()),
                "convergence": self.check_convergence()
            }
            
            self.iteration_history.append(iteration_data)
            
            logger.info(f"Screening iteration {iteration_num} completed")
            return iteration_data
            
        except Exception as e:
            logger.error(f"Error in screening iteration: {e}")
            return {"error": str(e)}