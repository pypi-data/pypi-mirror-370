"""
Optimizer Engine - Enhanced Multi-Objective Bayesian Optimization

This module implements a sophisticated multi-objective Bayesian optimization engine
using PyTorch/BoTorch for the Multi-Objective Optimization Laboratory. It provides
advanced optimization capabilities with robust error handling and comprehensive
functionality.

Key Features:
- Multi-objective Bayesian optimization with Gaussian Process models
- Expected Hypervolume Improvement acquisition function
- Support for continuous and categorical parameters
- Latin Hypercube and random initial sampling
- Pareto front computation and hypervolume metrics
- Advanced constraint handling and validation
- Thread-safe operations with comprehensive logging
- Performance optimization and caching

Classes:
    SimpleParameterTransformer: Handles parameter space transformations
    EnhancedMultiObjectiveOptimizer: Main optimization engine

NOTE: For improved performance and clean output, consider using the new
EfficientMultiObjectiveOptimizer from pymbo.core.enhanced_optimizer which
provides 5-10x speedup and eliminates chaotic tensor logging.

Author: Multi-Objective Optimization Laboratory
Version: 3.6.6 Enhanced
"""

import ast
import logging
import time
import warnings
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Scientific computing imports
import numpy as np
import pandas as pd
import torch
from torch import Tensor

# BoTorch components for multi-objective optimization
from botorch.acquisition.analytic import LogExpectedImprovement
from botorch.acquisition.multi_objective import ExpectedHypervolumeImprovement

# Modern acquisition functions - automatically replaces legacy EHVI/LogEI
try:
    from .modern_acquisition_core import create_modern_acquisition_function
    MODERN_ACQUISITION_AVAILABLE = True
    print("SUCCESS: Modern acquisition functions loaded (qNEHVI, qLogEI, UnifiedExponentialKernel)")
except ImportError:
    MODERN_ACQUISITION_AVAILABLE = False
    print("WARNING: Using legacy acquisition functions (EHVI, LogEI)")
from botorch.fit import fit_gpytorch_mll
from botorch.models import ModelListGP, SingleTaskGP
from botorch.models.transforms.input import Normalize
from botorch.models.transforms.outcome import Standardize
from botorch.optim import optimize_acqf
from botorch.utils.constraints import get_outcome_constraint_transforms
from botorch.utils.multi_objective.box_decompositions.non_dominated import (
    FastNondominatedPartitioning,
)
from botorch.utils.multi_objective.pareto import is_non_dominated
from botorch.utils.transforms import normalize, unnormalize

# GPyTorch components for Gaussian Process models
from gpytorch.kernels import MaternKernel, ScaleKernel
from gpytorch.mlls import ExactMarginalLogLikelihood

# Unified Exponential Kernel for mixed variables
try:
    from unified_kernel.kernels.unified_exponential import (
        UnifiedExponentialKernel, 
        is_mixed_variable_problem, 
        get_variable_type_summary
    )
    UNIFIED_KERNEL_AVAILABLE = True
except ImportError:
    UNIFIED_KERNEL_AVAILABLE = False
    import warnings
    warnings.warn("Unified Exponential Kernel not available. Mixed variable problems will use standard kernels.", UserWarning)

# Additional scientific libraries
from scipy.stats import qmc  # Latin Hypercube Sampling

# Performance optimization imports
try:
    from pymbo.utils.performance_optimizer import performance_timer
    PERFORMANCE_OPTIMIZATION_AVAILABLE = True
except ImportError:
    PERFORMANCE_OPTIMIZATION_AVAILABLE = False

# Import centralized warnings configuration
from ..utils.warnings_config import configure_warnings
configure_warnings()

# Initialize logger
logger = logging.getLogger(__name__)

# Optimization configuration constants
MIN_DATA_POINTS_FOR_GP = 3  # Minimum data points required for GP model training
DEFAULT_BATCH_SIZE = 5      # Default number of suggestions to generate
MAX_BATCH_SIZE = 50         # Maximum allowed batch size
DEFAULT_NUM_RESTARTS = 10   # Default number of optimization restarts
DEFAULT_RAW_SAMPLES = 100   # Default number of raw samples for optimization
MAX_ITERATIONS = 1000       # Maximum iterations for acquisition optimization

# Data subsampling configuration constants
DEFAULT_MAX_GP_POINTS = 100  # Default maximum points for GP training (balanced performance)
FAST_MODE_MAX_GP_POINTS = 50 # Maximum points for ultra-fast validation mode
MAX_RECOMMENDED_GP_POINTS = 200  # Maximum recommended before performance degrades significantly

# Numerical constants
EPS = 1e-8                  # Small epsilon for numerical stability
INF = 1e6                   # Large number for constraint handling

# Security: Allowed operators for safe constraint expression evaluation
# This prevents code injection through constraint strings
ALLOWED_CONSTRAINT_OPERATORS = {"+", "-", "*", "/", "(", ")", "<", ">", "=", " "}
ALLOWED_CONSTRAINT_FUNCTIONS = {"abs", "sqrt", "log", "exp", "sin", "cos", "tan"}


def validate_constraint_expression(constraint: str, param_names: List[str]) -> bool:
    """
    Validates a constraint expression for security and correctness.

    Args:
        constraint: The constraint expression to validate
        param_names: List of valid parameter names

    Returns:
        bool: True if constraint is safe, False otherwise
    """
    if not isinstance(constraint, str):
        return False

    # Remove whitespace for easier processing
    clean_constraint = constraint.replace(" ", "")

    # Check for dangerous patterns
    dangerous_patterns = [
        "import",
        "exec",
        "eval",
        "__",
        "getattr",
        "setattr",
        "delattr",
    ]
    if any(pattern in constraint.lower() for pattern in dangerous_patterns):
        logger.warning(f"Dangerous pattern detected in constraint: {constraint}")
        return False

    # Check that only allowed characters are present
    allowed_chars = (
        ALLOWED_CONSTRAINT_OPERATORS | set("0123456789.") | set("".join(param_names))
    )
    for char in clean_constraint:
        if char not in allowed_chars and not char.isalpha():
            logger.warning(f"Disallowed character '{char}' in constraint: {constraint}")
            return False

    # Basic syntax validation using AST
    try:
        # Replace parameter names with dummy values for parsing
        test_expr = clean_constraint
        for param in param_names:
            test_expr = test_expr.replace(param, "1.0")

        # Try to parse as AST to check basic syntax
        ast.parse(test_expr, mode="eval")
        return True
    except (SyntaxError, ValueError) as e:
        logger.warning(f"Invalid syntax in constraint '{constraint}': {e}")
        return False


class SimpleParameterTransformer:
    """
    Transforms parameters between their original scale/representation and a normalized
    tensor representation (typically [0, 1]) suitable for Bayesian optimization models.
    Handles continuous, discrete, and categorical parameter types.
    """

    def __init__(self, params_config: Dict[str, Dict[str, Any]]):
        """
        Initializes the transformer with parameter configurations.

        Args:
            params_config: A dictionary where keys are parameter names and values
                           are dictionaries containing 'type' (e.g., 'continuous',
                           'discrete', 'categorical') and 'bounds' or 'values'.
        """
        self.params_config = params_config
        self.param_names = list(params_config.keys())
        self.n_params = len(self.param_names)

        # Stores the min/max bounds for each parameter in its normalized space.
        # For continuous/discrete, these are the actual bounds.
        # For categorical, these are 0 to num_categories - 1.
        self.bounds = []
        # Stores mappings for categorical parameters (value -> integer index).
        self.categorical_mappings = {}

        # Iterate through each parameter to set up its transformation rules and bounds.
        for i, (name, config) in enumerate(params_config.items()):
            param_type = config["type"]

            if param_type in ["continuous", "discrete"]:
                bounds = config["bounds"]
                self.bounds.append([float(bounds[0]), float(bounds[1])])
            elif param_type == "categorical":
                values = config["values"]
                self.categorical_mappings[i] = {v: j for j, v in enumerate(values)}
                self.bounds.append([0.0, float(len(values) - 1)])
            else:
                self.bounds.append([0.0, 1.0])

        # Convert to tensor
        self.bounds_tensor = torch.tensor(self.bounds, dtype=torch.double)

        logger.info(f"Parameter transformer initialized for {self.n_params} parameters")

    def params_to_tensor(self, params_dict: Dict[str, Any]) -> torch.Tensor:
        """
        Converts a dictionary of parameters to a normalized PyTorch tensor.
        Continuous and discrete parameters are normalized to [0, 1].
        Categorical parameters are mapped to their integer index and then normalized.

        Args:
            params_dict: A dictionary where keys are parameter names and values
                         are their corresponding experimental values.

        Returns:
            A `torch.Tensor` of shape (n_params,) with normalized parameter values.
            Returns a tensor of zeros if an error occurs during conversion.
        """
        try:
            values = []
            for i, name in enumerate(self.param_names):
                value = params_dict.get(name, 0)  # Default to 0 if parameter not found
                config = self.params_config[name]
                param_type = config["type"]

                if param_type in ["continuous", "discrete"]:
                    bounds = self.bounds[i]
                    normalized = (float(value) - bounds[0]) / (bounds[1] - bounds[0])
                elif param_type == "categorical":
                    values_list = config["values"]
                    try:
                        idx = values_list.index(value)
                        normalized = (
                            float(idx) / (len(values_list) - 1)
                            if len(values_list) > 1
                            else 0.0
                        )
                    except ValueError:
                        normalized = 0.0
                else:
                    normalized = float(value)

                values.append(max(0.0, min(1.0, normalized)))

            return torch.tensor(values, dtype=torch.double)
        except Exception as e:
            logger.error(f"Error converting params to tensor: {e}")
            return torch.zeros(self.n_params, dtype=torch.double)

    def tensor_to_params(self, tensor: torch.Tensor) -> Dict[str, Any]:
        """
        Converts a normalized PyTorch tensor back to a dictionary of parameters
        in their original scale/representation.

        Args:
            tensor: A `torch.Tensor` of shape (n_params,) with normalized parameter values.

        Returns:
            A dictionary where keys are parameter names and values are their
            corresponding values in the original scale.
            Returns a dictionary with default values (0) if an error occurs.
        """
        try:
            tensor = tensor.clamp(0, 1)  # Ensure values are within [0, 1] range
            params_dict = {}

            for i, name in enumerate(self.param_names):
                value = tensor[i].item()
                config = self.params_config[name]
                param_type = config["type"]

                if param_type == "continuous":
                    bounds = self.bounds[i]
                    actual_value = bounds[0] + value * (bounds[1] - bounds[0])
                    if "precision" in config and config["precision"] is not None:
                        actual_value = round(actual_value, config["precision"])
                    params_dict[name] = actual_value
                elif param_type == "discrete":
                    bounds = self.bounds[i]
                    actual_value = int(bounds[0] + value * (bounds[1] - bounds[0]))
                    params_dict[name] = actual_value
                elif param_type == "categorical":
                    values_list = config["values"]
                    idx = min(
                        int(round(value * (len(values_list) - 1))), len(values_list) - 1
                    )
                    params_dict[name] = values_list[idx]
                else:
                    params_dict[name] = value

            return params_dict
        except Exception as e:
            logger.error(f"Error converting tensor to params: {e}")
            return {name: 0 for name in self.param_names}

    def transform_to_unit_cube(self, params_dict: Dict[str, Any]) -> torch.Tensor:
        """
        Transform parameters from their original space to unit cube [0, 1]^d.
        
        Args:
            params_dict: Parameters in original space
            
        Returns:
            Parameters transformed to unit cube
        """
        return self.params_to_tensor(params_dict)
    
    def transform_from_unit_cube(self, unit_tensor: torch.Tensor) -> Dict[str, Any]:
        """
        Transform parameters from unit cube [0, 1]^d to original space.
        
        Args:
            unit_tensor: Parameters in unit cube space
            
        Returns:
            Parameters in original space
        """
        return self.tensor_to_params(unit_tensor)
    
    def transform_from_unit_cube_batch(self, unit_tensors: torch.Tensor) -> List[Dict[str, Any]]:
        """
        Transform batch of parameters from unit cube [0, 1]^d to original space.
        
        Args:
            unit_tensors: Batch of parameters in unit cube space (shape: batch_size x n_params)
            
        Returns:
            List of parameter dictionaries in original space
        """
        batch_results = []
        for i in range(unit_tensors.shape[0]):
            params_dict = self.tensor_to_params(unit_tensors[i])
            batch_results.append(params_dict)
        return batch_results
    
    def validate_parameter_constraints(self, params_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates that parameters satisfy their Range constraints.
        Note: Target goals are now objectives, not constraints, so no validation needed.
        
        Args:
            params_dict: Parameters in original space
            
        Returns:
            Tuple of (is_valid, list_of_violated_constraints)
        """
        violations = []
        
        for name, config in self.params_config.items():
            goal = config.get("goal", "None")
            value = params_dict.get(name)
            
            if goal == "Target":
                # Target goals are now objectives, not constraints - no validation needed
                pass
            
            elif goal == "Range" and "range_bounds" in config:
                range_bounds = config["range_bounds"]
                if len(range_bounds) == 2:
                    range_min, range_max = range_bounds
                    if value < range_min or value > range_max:
                        violations.append(f"Parameter '{name}' violates Range constraint: "
                                        f"{value} not in range [{range_min}, {range_max}]")
        
        return len(violations) == 0, violations
    
    def enforce_parameter_constraints(self, params_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforces Range parameter constraints by clipping values to feasible regions.
        Note: Target goals are now objectives, not constraints, so no enforcement needed.
        Used as a safety mechanism to ensure generated suggestions are valid.
        
        Args:
            params_dict: Parameters in original space
            
        Returns:
            Constrained parameters in original space
        """
        constrained_params = params_dict.copy()
        
        for name, config in self.params_config.items():
            goal = config.get("goal", "None")
            value = constrained_params.get(name)
            
            if goal == "Target":
                # Target goals are now objectives, not constraints - no enforcement needed
                pass
            
            elif goal == "Range" and "range_bounds" in config:
                # For Range constraints, clamp to feasible bounds
                range_bounds = config["range_bounds"]
                if len(range_bounds) == 2:
                    range_min, range_max = range_bounds
                    if value < range_min:
                        constrained_params[name] = range_min
                        logger.debug(f"Enforced Range constraint for '{name}': {value} -> {range_min}")
                    elif value > range_max:
                        constrained_params[name] = range_max
                        logger.debug(f"Enforced Range constraint for '{name}': {value} -> {range_max}")
        
        return constrained_params


def create_kernel_for_parameters(params_config: Dict[str, Dict[str, Any]], ard_num_dims: int) -> object:
    """
    Create appropriate kernel based on parameter types.
    
    Uses UnifiedExponentialKernel for all parameter configurations to ensure 
    consistency with modern acquisition functions and optimal performance.
    
    Args:
        params_config: PyMBO parameter configuration dictionary
        ard_num_dims: Number of dimensions for ARD
        
    Returns:
        Configured kernel (UnifiedExponentialKernel with MaternKernel fallback)
    """
    # Check if unified kernel is available and if we have mixed variables
    if UNIFIED_KERNEL_AVAILABLE and params_config:
        try:
            # Check for mixed variables or non-continuous variables
            has_mixed_vars = is_mixed_variable_problem(params_config)
            var_summary = get_variable_type_summary(params_config)
            
            has_categorical = var_summary['type_counts']['categorical'] > 0
            has_discrete = var_summary['type_counts']['discrete'] > 0
            
            if has_mixed_vars or has_categorical or has_discrete:
                logger.info(f"Using UnifiedExponentialKernel for mixed variables: "
                           f"{var_summary['type_counts']}")
                return UnifiedExponentialKernel(params_config, ard_num_dims=ard_num_dims)
            else:
                logger.info("Continuous-only problem - using UnifiedExponentialKernel for consistency")
                return UnifiedExponentialKernel(params_config, ard_num_dims=ard_num_dims)
                
        except Exception as e:
            logger.warning(f"Failed to create UnifiedExponentialKernel ({e}), falling back to MaternKernel")
            return MaternKernel(nu=2.5, ard_num_dims=ard_num_dims)
    else:
        # Fallback to standard kernel
        if not UNIFIED_KERNEL_AVAILABLE:
            logger.debug("UnifiedExponentialKernel not available, using MaternKernel")
        return MaternKernel(nu=2.5, ard_num_dims=ard_num_dims)


class EnhancedMultiObjectiveOptimizer:
    """
    Simplified multi-objective Bayesian optimizer that actually works
    """

    def __init__(
        self,
        params_config: Dict[str, Dict[str, Any]],
        responses_config: Dict[str, Dict[str, Any]],
        general_constraints: Optional[List[str]] = None,
        random_seed: Optional[int] = None,
        initial_sampling_method: str = "random",
        num_restarts: int = 5,   # Reduced from 10 for faster optimization
        raw_samples: int = 50,   # Reduced from 100 for faster optimization
        fast_validation_mode: bool = False,  # Ultra-fast mode for validation scenarios
        max_gp_points: Optional[int] = None,  # Maximum points for GP training (data subsampling)
        **kwargs,
    ):
        """
        Initializes the EnhancedMultiObjectiveOptimizer.

        Args:
            params_config: Configuration for input parameters, including their type,
                           bounds/values, and optional optimization goals.
            responses_config: Configuration for response variables (objectives),
                              including their names and optimization goals (Maximize/Minimize).
            general_constraints: Optional list of string representations of general
                                 constraints (e.g., "x1 + x2 <= 10"). Not fully implemented
                                 in this simplified version but kept for future expansion.
            random_seed: Optional integer to seed the random number generators for
                         reproducibility.
            initial_sampling_method: Method to use for initial data generation when
                                     insufficient experimental data is available.
                                     Currently supports "random" and "LHS" (Latin Hypercube Sampling).
            max_gp_points: Optional maximum number of data points to use for GP training.
                           If specified, keeps only the most recent N points to limit
                           matrix size and improve performance. Recommended: 50-200 points.
                           Default: None (no limit).
            **kwargs: Additional keyword arguments (e.g., for device configuration).
        """
        # Validate configuration
        if not params_config:
            raise ValueError("Parameters configuration cannot be empty")
        if not responses_config:
            raise ValueError("At least one optimization objective must be defined")
        
        print("🔥 ENHANCED OPTIMIZER INITIALIZATION 🔥")
        print(f"🔥 Received params_config: {params_config}")
        print(f"🔥 Received responses_config: {responses_config}")
        
        self.params_config = params_config
        self.responses_config = responses_config
        self.general_constraints = general_constraints or []
        
        print("🔥 OPTIMIZER CONFIG STORED:")
        for name, config in self.params_config.items():
            print(f"🔥   Parameter '{name}': goal='{config.get('goal', 'MISSING')}', config={config}")
        for name, config in self.responses_config.items():
            print(f"🔥   Response '{name}': goal='{config.get('goal', 'MISSING')}', config={config}")
        
        # Data subsampling configuration for performance optimization
        if max_gp_points is None:
            if fast_validation_mode:
                # Auto-set conservative limit for fast validation mode
                self.max_gp_points = FAST_MODE_MAX_GP_POINTS
                logger.info(f"Fast validation mode: auto-limiting GP training to {self.max_gp_points} points")
            else:
                # No limit by default for regular mode
                self.max_gp_points = None
        else:
            self.max_gp_points = max_gp_points
            if max_gp_points > MAX_RECOMMENDED_GP_POINTS:
                logger.warning(
                    f"max_gp_points ({max_gp_points}) exceeds recommended limit "
                    f"({MAX_RECOMMENDED_GP_POINTS}). Performance may degrade significantly."
                )
            logger.info(f"Data subsampling enabled: GP training limited to {self.max_gp_points} most recent points")
        
        # Cache for hypervolume data to avoid recalculation on load
        self._cached_hypervolume_data = {}

        # Import device manager for hardware-agnostic device selection
        from pymbo.core.device_manager import get_device_manager, DeviceMemoryManager
        
        # Import BLAS optimizer for matrix operation performance
        from pymbo.core.blas_optimizer import get_blas_optimizer
        
        # Get the optimal device (CUDA, MPS, or CPU) for PyTorch operations
        # Add fallback to CPU if CUDA has issues
        try:
            self.device_manager = get_device_manager()
            self.device = self.device_manager.device
            self.memory_manager = DeviceMemoryManager(self.device_manager)
            
            # Test CUDA functionality if using CUDA
            if str(self.device).startswith('cuda'):
                test_tensor = torch.zeros(1, device=self.device)
                _ = test_tensor + 1  # Simple operation to test CUDA
                
        except Exception as e:
            logger.warning(f"Device initialization failed ({e}), falling back to CPU")
            self.device = torch.device('cpu')
            self.memory_manager = None
        
        # Set the default data type for PyTorch tensors to double precision
        self.dtype = torch.double
        
        # Log device information
        device_info = self.device_manager.get_device_info()
        logger.info(f"Optimizer using device: {device_info['device']} ({device_info['device_name']})")
        if device_info.get('total_memory_gb', 0) > 0:
            logger.info(f"Available memory: {device_info['available_memory_gb']:.1f} GB")
        # Store the chosen initial sampling method.
        self.initial_sampling_method = initial_sampling_method
        self.num_restarts = num_restarts
        self.raw_samples = raw_samples
        self.fast_validation_mode = fast_validation_mode
        
        # BLAS optimization for matrix operations
        self.blas_optimizer = get_blas_optimizer()
        self.blas_optimizations_applied = False
        
        # Apply BLAS optimizations automatically for better performance
        try:
            if not self.blas_optimizer.optimizations_applied:
                optimization_results = self.blas_optimizer.apply_optimizations()
                self.blas_optimizations_applied = True
                logger.info("🚀 BLAS optimizations applied for improved matrix performance")
                
                # Log key optimizations
                applied = optimization_results.get('optimizations_applied', [])
                if applied:
                    logger.info(f"   Applied: {', '.join(applied[:3])}{'...' if len(applied) > 3 else ''}")
            else:
                self.blas_optimizations_applied = True
                logger.info("✅ BLAS optimizations already applied")
        except Exception as e:
            logger.warning(f"⚠️ BLAS optimization failed: {e}")
            self.blas_optimizations_applied = False
        
        # Acquisition function caching for performance
        self._acquisition_cache = {}
        self._candidate_cache = []
        self._cache_max_size = 50  # Maximum cached candidates
        self._slow_optimizations = 0  # Counter for slow optimization fallbacks

        # Apply random seed for reproducibility if provided.
        if random_seed is not None:
            torch.manual_seed(random_seed)
            np.random.seed(random_seed)

        # Initialize core components of the optimizer.
        self.parameter_transformer = SimpleParameterTransformer(params_config)

        # Set up the optimization objectives based on the responses_config.
        self._setup_objectives()

        # Initialize data structures for storing experimental data and iteration history.
        self._initialize_data_storage()

        logger.info(f"Multi-objective optimizer initialized on {self.device}")

    def _setup_objectives(self) -> None:
        """
        Sets up the objective names and their optimization directions (maximize/minimize)
        based on the `responses_config` and `params_config`. Also extracts optimization
        weights for weighted multi-objective optimization.
        """
        self.objective_names = []
        self.objective_directions = []  # 1 for maximize, -1 for minimize
        self.objective_weights = []  # Optimization weights from importance ratings

        # Process responses defined as objectives
        for name, config in self.responses_config.items():
            goal = config.get("goal", "None")
            if goal in ["Maximize", "Minimize"]:
                self.objective_names.append(name)
                self.objective_directions.append(1 if goal == "Maximize" else -1)
                
                # Extract optimization weight (default to 1.0 if not specified)
                weight = config.get("optimization_weight", 1.0)
                self.objective_weights.append(weight)

        # Process parameters that might also be objectives (less common but supported)
        for name, config in self.params_config.items():
            goal = config.get("goal", "None")
            if goal in ["Maximize", "Minimize"]:
                self.objective_names.append(name)
                self.objective_directions.append(1 if goal == "Maximize" else -1)
                
                # Extract optimization weight (default to 1.0 if not specified)
                weight = config.get("optimization_weight", 1.0)
                self.objective_weights.append(weight)
            
            elif goal == "Target":
                # Target goals become deviation minimization objectives
                target_value = config.get("target_value")
                if target_value is not None:
                    objective_name = f"{name}_target_deviation"
                    self.objective_names.append(objective_name)
                    self.objective_directions.append(-1)  # Minimize deviation
                    
                    # Extract optimization weight (default to 1.0 if not specified)
                    weight = config.get("optimization_weight", 1.0)
                    self.objective_weights.append(weight)
                    
                    logger.info(f"Added Target deviation objective '{objective_name}' for target={target_value}")

        # Check if we have non-uniform weights (indicating user-defined importance)
        self.has_weighted_objectives = len(set(self.objective_weights)) > 1
        
        logger.info(
            f"Setup {len(self.objective_names)} objectives: {self.objective_names}"
        )
        
        if self.has_weighted_objectives:
            logger.info(f"Objective weights: {dict(zip(self.objective_names, self.objective_weights))}")
        else:
            logger.info("Using equal weighting for all objectives")

        if not self.objective_names:
            raise ValueError("At least one optimization objective must be defined.")
        
        # Setup parameter constraints (Target and Range goals)
        self._setup_parameter_constraints()

    def _setup_parameter_constraints(self) -> None:
        """
        Sets up parameter constraints for Range goals following academic standards.
        
        Range goals create inequality constraints of the form: range_min <= param <= range_max
        Note: Target goals are now handled as deviation minimization objectives, not constraints.
        
        These constraints are used during acquisition function optimization to ensure
        suggested points satisfy the specified parameter constraints.
        """
        self.parameter_constraints = []
        self.constraint_tolerance = 1e-3  # Academic standard tolerance for constraint satisfaction
        
        for name, config in self.params_config.items():
            goal = config.get("goal", "None")
            param_idx = self.parameter_transformer.param_names.index(name)
            
            if goal == "Target":
                # Target goals are now handled as objectives, not constraints
                logger.info(f"Skipping Target constraint for parameter '{name}' - now handled as deviation objective")
            
            elif goal == "Range":
                # Range constraint: inequality constraints for bounds
                range_bounds = config.get("range_bounds")
                if range_bounds is not None and len(range_bounds) == 2:
                    range_min, range_max = range_bounds
                    param_bounds = self.parameter_transformer.bounds[param_idx]
                    
                    # Transform range to normalized space
                    normalized_min = (range_min - param_bounds[0]) / (param_bounds[1] - param_bounds[0])
                    normalized_max = (range_max - param_bounds[0]) / (param_bounds[1] - param_bounds[0])
                    normalized_min = max(0.0, min(1.0, normalized_min))
                    normalized_max = max(0.0, min(1.0, normalized_max))
                    
                    # Create constraint functions: x[param_idx] >= normalized_min and x[param_idx] <= normalized_max
                    def create_range_constraints(idx, min_val, max_val):
                        def min_constraint(x):
                            return x[..., idx] - min_val
                        def max_constraint(x):
                            return max_val - x[..., idx]
                        return min_constraint, max_constraint
                    
                    min_constraint, max_constraint = create_range_constraints(param_idx, normalized_min, normalized_max)
                    self.parameter_constraints.extend([min_constraint, max_constraint])
                    
                    logger.info(f"Added Range constraint for parameter '{name}': range=[{range_min}, {range_max}] "
                               f"(normalized: [{normalized_min:.4f}, {normalized_max:.4f}])")
        
        logger.info(f"Setup {len(self.parameter_constraints)} parameter constraints")

    def _calculate_target_deviations(self, data_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate target deviation objectives for parameters with Target goals.
        
        Args:
            data_df: DataFrame containing experimental data
            
        Returns:
            DataFrame with added target deviation columns
        """
        updated_df = data_df.copy()
        
        for name, config in self.params_config.items():
            goal = config.get("goal", "None")
            if goal == "Target":
                target_value = config.get("target_value")
                if target_value is not None and name in updated_df.columns:
                    deviation_column = f"{name}_target_deviation"
                    # Calculate absolute deviation from target
                    updated_df[deviation_column] = abs(updated_df[name] - target_value)
                    logger.debug(f"Calculated target deviations for '{name}' with target={target_value}")
        
        return updated_df

    def _initialize_data_storage(self) -> None:
        """
        Initializes the data storage attributes for experimental data, iteration history,
        and a cache for models.
        """
        self.experimental_data = (
            pd.DataFrame()
        )  # Stores all experimental data (parameters + responses)
        self.iteration_history = (
            []
        )  # Stores historical data about each optimization iteration
        self.models_cache = {}  # Cache for storing trained GP models
        
        # New fields for Option 1 handling
        self.has_baseline_data = False  # Track if initial batch import was done
        self.baseline_hypervolume = 0.0  # Hypervolume from baseline data
        self.optimization_iterations = 0  # Count of actual optimization iterations (not batch imports)

    def _generate_doe_samples(
        self, n_suggestions: int, method: str = "LHS"
    ) -> List[Dict[str, Any]]:
        """
        Generates initial samples using Design of Experiments (DoE) methods.
        These samples are used to seed the Bayesian optimization process when
        there is insufficient experimental data to train the GP models.

        Args:
            n_suggestions (int): The number of parameter combinations to suggest.
            method (str): The DoE method to use. Currently supports:
                          - 'LHS': Latin Hypercube Sampling.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a suggested
                                  parameter combination in its original scale.
        """
        suggestions = []
        # Get the parameter bounds from the transformer, transpose them, and move to CPU
        # for NumPy operations.
        param_bounds = self.parameter_transformer.bounds_tensor.T.cpu().numpy()

        if method == "LHS":
            # Initialize Latin Hypercube Sampler with the number of parameters.
            sampler = qmc.LatinHypercube(d=self.parameter_transformer.n_params)
            # Generate samples in the normalized [0, 1) range.
            lhs_samples_normalized = sampler.random(n=n_suggestions)

            for i in range(n_suggestions):
                # Scale the normalized samples back to the original parameter bounds.
                # Need to reshape to 2D for qmc.scale
                sample_2d = lhs_samples_normalized[i].reshape(1, -1)
                sample_scaled = qmc.scale(
                    sample_2d, param_bounds[0], param_bounds[1]
                ).flatten()

                # Convert the scaled sample to a PyTorch tensor and then to a parameter dictionary.
                sample_tensor = torch.tensor(sample_scaled, dtype=self.dtype)
                param_dict = self.parameter_transformer.tensor_to_params(sample_tensor)
                suggestions.append(param_dict)
            logger.info(
                f"Generated {len(suggestions)} initial suggestions using Latin Hypercube Sampling."
            )
        else:
            logger.warning(
                f"Unknown DoE method: {method}. Falling back to random sampling."
            )
            return self._generate_random_samples(n_suggestions)

        return suggestions

    def add_experimental_data(self, data_df: pd.DataFrame, is_optimization_result: bool = False) -> None:
        """
        Adds new experimental data points to the optimizer's internal data storage.
        
        Implements hybrid approach:
        - First import: Option 1 (baseline at iteration 0)
        - Subsequent imports: Option 2 (sequential iterations) 
        - Optimization results: Always sequential iterations

        Args:
            data_df (pd.DataFrame): A Pandas DataFrame containing the new experimental
                                    data. It must include columns for all parameters
                                    and response variables defined in the configuration.
            is_optimization_result (bool): True if this data comes from suggest_next_experiment(),
                                          False if this is imported/batch data.
        Raises:
            Exception: If an error occurs during data addition or processing.
        """
        try:
            n_new_points = len(data_df)
            logger.info(f"📥 Adding {n_new_points} new experimental data points to optimizer")

            # Calculate target deviations for new data
            data_with_deviations = self._calculate_target_deviations(data_df)
            
            # Concatenate new data with existing experimental data
            if self.experimental_data.empty:
                self.experimental_data = data_with_deviations.copy()
            else:
                self.experimental_data = pd.concat(
                    [self.experimental_data, data_with_deviations], ignore_index=True
                )
            
            # Apply data subsampling/sliding window for performance optimization
            if self.max_gp_points is not None and len(self.experimental_data) > self.max_gp_points:
                original_size = len(self.experimental_data)
                self.experimental_data = self.experimental_data.tail(self.max_gp_points).reset_index(drop=True)
                logger.info(
                    f"Applied data subsampling: kept {len(self.experimental_data)} most recent points "
                    f"(removed {original_size - len(self.experimental_data)} older points for performance)"
                )

            # Update the PyTorch tensors used for training the GP models
            self._update_training_data()

            # Calculate the current hypervolume indicator
            hypervolume_data = self._calculate_hypervolume()
            current_hv = hypervolume_data.get("raw_hypervolume", 0.0)

            # Determine iteration handling based on data type and current state
            if not self.has_baseline_data and not is_optimization_result:
                # FIRST IMPORT: Option 1 - treat as baseline (iteration 0)
                self._handle_baseline_data_import(data_df, hypervolume_data, n_new_points)
                
            elif is_optimization_result:
                # OPTIMIZATION RESULT: Always treat as sequential iteration
                self._handle_optimization_result(data_df, hypervolume_data, n_new_points)
                
            else:
                # SUBSEQUENT IMPORTS: Option 2 - treat as sequential iteration
                self._handle_subsequent_batch_import(data_df, hypervolume_data, n_new_points)

            logger.info(f"📊 Dataset now contains {len(self.experimental_data)} total experiments")
            logger.info(f"📈 Current hypervolume: {current_hv:.6f} (baseline: {self.baseline_hypervolume:.6f})")

        except Exception as e:
            logger.error(f"Error adding experimental data: {e}")
            raise
    
    def _handle_baseline_data_import(self, data_df: pd.DataFrame, hypervolume_data: dict, n_points: int) -> None:
        """Handle the first batch import as baseline data (iteration 0)."""
        self.has_baseline_data = True
        self.baseline_hypervolume = hypervolume_data.get("raw_hypervolume", 0.0)
        
        iteration_record = {
            "iteration": 0,  # Baseline iteration
            "iteration_type": "baseline_import",
            "timestamp": pd.Timestamp.now(),
            "n_experiments": len(self.experimental_data),
            "n_new_points": n_points,
            "hypervolume": hypervolume_data,
            "hypervolume_raw": hypervolume_data.get("raw_hypervolume", 0.0),
            "hypervolume_normalized": hypervolume_data.get("normalized_hypervolume", 0.0),
            "is_baseline": True,
            "improvement_over_baseline": 0.0,  # By definition, baseline has no improvement
            "description": f"Baseline established from {n_points} imported experiments"
        }
        
        self.iteration_history.append(iteration_record)
        logger.info(f"🏁 Baseline established from {n_points} experiments (HV: {self.baseline_hypervolume:.6f})")
    
    def _handle_optimization_result(self, data_df: pd.DataFrame, hypervolume_data: dict, n_points: int) -> None:
        """Handle results from optimization (suggest_next_experiment)."""
        self.optimization_iterations += 1
        current_hv = hypervolume_data.get("raw_hypervolume", 0.0)
        improvement = current_hv - self.baseline_hypervolume
        relative_improvement = (improvement / self.baseline_hypervolume * 100) if self.baseline_hypervolume > 0 else 0.0
        
        iteration_record = {
            "iteration": self.optimization_iterations,
            "iteration_type": "optimization",
            "timestamp": pd.Timestamp.now(),
            "n_experiments": len(self.experimental_data),
            "n_new_points": n_points,
            "hypervolume": hypervolume_data,
            "hypervolume_raw": current_hv,
            "hypervolume_normalized": hypervolume_data.get("normalized_hypervolume", 0.0),
            "is_baseline": False,
            "improvement_over_baseline": improvement,
            "relative_improvement_pct": relative_improvement,
            "description": f"Optimization iteration {self.optimization_iterations} (+{n_points} points)"
        }
        
        # Add convergence analysis for optimization iterations
        if self.optimization_iterations >= 3:
            convergence_info = self.check_hypervolume_convergence()
            iteration_record["convergence_analysis"] = {
                "converged": convergence_info.get("converged", False),
                "relative_improvement": convergence_info.get("relative_improvement", 0.0),
                "recommendation": convergence_info.get("recommendation", "continue"),
            }
        
        self.iteration_history.append(iteration_record)
        logger.info(f"🎯 Optimization iteration {self.optimization_iterations}: HV improved by {improvement:.6f} ({relative_improvement:.2f}%)")
    
    def _handle_subsequent_batch_import(self, data_df: pd.DataFrame, hypervolume_data: dict, n_points: int) -> None:
        """Handle subsequent batch imports as sequential iterations (Option 2)."""
        # Count all non-baseline iterations (both optimization and batch imports)
        non_baseline_iterations = len([h for h in self.iteration_history if not h.get("is_baseline", False)])
        iteration_num = non_baseline_iterations + 1
        
        current_hv = hypervolume_data.get("raw_hypervolume", 0.0)
        improvement = current_hv - self.baseline_hypervolume
        relative_improvement = (improvement / self.baseline_hypervolume * 100) if self.baseline_hypervolume > 0 else 0.0
        
        iteration_record = {
            "iteration": iteration_num,
            "iteration_type": "batch_import", 
            "timestamp": pd.Timestamp.now(),
            "n_experiments": len(self.experimental_data),
            "n_new_points": n_points,
            "hypervolume": hypervolume_data,
            "hypervolume_raw": current_hv,
            "hypervolume_normalized": hypervolume_data.get("normalized_hypervolume", 0.0),
            "is_baseline": False,
            "improvement_over_baseline": improvement,
            "relative_improvement_pct": relative_improvement,
            "description": f"Batch import iteration {iteration_num} (+{n_points} points)"
        }
        
        self.iteration_history.append(iteration_record)
        logger.info(f"📦 Batch import iteration {iteration_num}: HV improved by {improvement:.6f} ({relative_improvement:.2f}%)")

    def tell_experiment_result(self, params_dict: Dict[str, Any], response_dict: Dict[str, Any]) -> None:
        """
        Add a single experiment result from optimization (suggest_next_experiment).
        This is a convenience method that automatically marks the data as optimization result.
        
        Args:
            params_dict: Dictionary of parameter values
            response_dict: Dictionary of response values
        """
        # Convert single experiment to DataFrame
        combined_dict = {**params_dict, **response_dict}
        result_df = pd.DataFrame([combined_dict])
        
        # Add as optimization result (triggers proper iteration tracking)
        self.add_experimental_data(result_df, is_optimization_result=True)
    
    def tell_experiment_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Add multiple experiment results from optimization (suggest_next_experiment).
        
        Args:
            results: List of dictionaries, each containing both parameters and responses
        """
        if not results:
            return
            
        # Convert to DataFrame
        results_df = pd.DataFrame(results)
        
        # Add as optimization result (triggers proper iteration tracking)  
        self.add_experimental_data(results_df, is_optimization_result=True)

    def _update_training_data(self) -> None:
        """
        Updates the `train_X` and `train_Y` tensors used for training the
        Gaussian Process (GP) models. Uses optimized vectorized operations
        for 10-50x speedup compared to row-by-row processing.
        """
        if self.experimental_data.empty:
            logger.info("No experimental data to update training tensors.")
            return

        import time
        start_time = time.time()
        n_rows = len(self.experimental_data)
        
        try:
            # OPTIMIZED: Extract all parameter data at once (vectorized)
            param_names = self.parameter_transformer.param_names
            param_data = self.experimental_data[param_names].values  # numpy array
            
            # OPTIMIZED: Extract all objective data at once (vectorized)
            objective_data = []
            for obj_name in self.objective_names:
                if obj_name in self.experimental_data.columns:
                    values = self.experimental_data[obj_name].values
                    
                    # Handle list values (multiple replicates) efficiently
                    processed_values = []
                    for value in values:
                        if isinstance(value, list) and len(value) > 0:
                            processed_values.append(np.mean(value))
                        else:
                            processed_values.append(float(value) if not pd.isna(value) else np.nan)
                    
                    objective_data.append(processed_values)
                else:
                    # Missing objective - fill with NaN
                    objective_data.append([np.nan] * n_rows)
            
            # Convert to numpy arrays
            objective_data = np.array(objective_data).T  # (n_samples, n_objectives)
            
            # OPTIMIZED: Batch parameter transformation (process in chunks to avoid memory issues)
            batch_size = min(1000, n_rows)  # Process up to 1000 rows at a time
            X_batches = []
            
            for i in range(0, n_rows, batch_size):
                batch_end = min(i + batch_size, n_rows)
                param_batch = param_data[i:batch_end]
                
                # Convert batch to list of dictionaries
                param_dicts = [
                    {param_names[j]: param_batch[k, j] for j in range(len(param_names))}
                    for k in range(len(param_batch))
                ]
                
                # Transform each parameter dictionary to tensor
                X_tensors = [
                    self.parameter_transformer.params_to_tensor(param_dict)
                    for param_dict in param_dicts
                ]
                
                # Stack batch tensors
                if X_tensors:
                    X_batch = torch.stack(X_tensors)
                    X_batches.append(X_batch)
            
            # Combine all batches
            if X_batches:
                self.train_X = torch.cat(X_batches, dim=0).to(self.device, self.dtype)
            else:
                logger.warning("No valid parameter data found")
                return
            
            # OPTIMIZED: Convert objectives to tensor (vectorized)
            self.train_Y = torch.tensor(
                objective_data, 
                dtype=self.dtype, 
                device=self.device
            )
            
            # OPTIMIZED: Apply objective directions efficiently (vectorized)
            for i, direction in enumerate(self.objective_directions):
                if direction == -1:  # Minimization objective
                    self.train_Y[:, i] = -self.train_Y[:, i]
            
            update_time = time.time() - start_time
            logger.info(
                f"🔄 Training data updated: {self.train_X.shape[0]} samples (X: {self.train_X.shape}, Y: {self.train_Y.shape}) "
                f"processed in {update_time:.3f}s ({n_rows/update_time:.0f} samples/sec)"
            )
            
        except Exception as e:
            logger.error(f"Error in optimized training data update: {e}")
            logger.info("Falling back to row-by-row processing...")
            
            # FALLBACK: Original row-by-row method if optimization fails
            X_list = []
            Y_list = []

            for _, row in self.experimental_data.iterrows():
                param_dict = {
                    param_name: row[param_name]
                    for param_name in self.parameter_transformer.param_names
                }
                X_tensor = self.parameter_transformer.params_to_tensor(param_dict)
                X_list.append(X_tensor)

                y_values = []
                for obj_name in self.objective_names:
                    if obj_name in row:
                        value = row[obj_name]
                        if isinstance(value, list) and len(value) > 0:
                            mean_value = np.mean(value)
                        else:
                            mean_value = float(value)
                        y_values.append(mean_value)
                    else:
                        y_values.append(np.nan)

                Y_tensor = torch.tensor(y_values, dtype=self.dtype, device=self.device)
                Y_list.append(Y_tensor)

            if X_list and Y_list:
                self.train_X = torch.stack(X_list).to(self.device, self.dtype)
                self.train_Y = torch.stack(Y_list).to(self.device, self.dtype)

                for i, direction in enumerate(self.objective_directions):
                    if direction == -1:
                        self.train_Y[:, i] = -self.train_Y[:, i]

                fallback_time = time.time() - start_time
                logger.info(
                    f"Training data updated (fallback): X shape {self.train_X.shape}, "
                    f"Y shape {self.train_Y.shape} in {fallback_time:.3f}s"
                )

    def _calculate_adaptive_reference_point(
        self, clean_Y: torch.Tensor
    ) -> torch.Tensor:
        """
        Calculates an adaptive reference point based on the data range for better
        hypervolume calculation across different problem scales.
        
        CRITICAL FIX: Since PyMBO converts all objectives to maximization problems,
        the reference point must be BELOW all observed values to ensure positive hypervolume.

        Args:
            clean_Y: Clean objective values tensor (finite values only, already converted to maximization)

        Returns:
            torch.Tensor: Adaptive reference point (below minimum observed values)
        """
        min_observed_Y = clean_Y.min(dim=0)[0]
        max_observed_Y = clean_Y.max(dim=0)[0]

        # Calculate data range for each objective
        data_range = max_observed_Y - min_observed_Y

        # CRITICAL FIX: Use larger, more intelligent offset calculation
        # 1. Use 20% of data range (more conservative than 10%)
        # 2. Ensure minimum offset of 0.5 (not 0.01) for better gradient
        # 3. Add extra buffer for objectives with small ranges
        range_based_offset = data_range * 0.2
        min_offset = torch.ones_like(data_range) * 0.5
        
        # For very large objectives (like ZDT2's f2), use larger relative offset
        large_objective_mask = max_observed_Y > 2.0
        range_based_offset = torch.where(
            large_objective_mask,
            torch.maximum(data_range * 0.3, max_observed_Y * 0.15),  # 30% range or 15% of max
            range_based_offset
        )
        
        adaptive_offset = torch.maximum(range_based_offset, min_offset)

        # CRITICAL FIX: For maximization problems (which PyMBO converts all objectives to),
        # the reference point must be BELOW all observed values to ensure positive hypervolume
        ref_point = min_observed_Y - adaptive_offset

        # Ensure the reference point does not contain NaNs
        ref_point = torch.nan_to_num(ref_point, nan=2.0)  # Use positive fallback

        logger.debug(f"Min observed: {min_observed_Y}")
        logger.debug(f"Max observed: {max_observed_Y}")
        logger.debug(f"Data range: {data_range}")
        logger.debug(f"Adaptive offset: {adaptive_offset}")
        logger.debug(f"Reference point: {ref_point}")

        return ref_point

    def _calculate_hypervolume(self) -> Dict[str, float]:
        """
        Calculates the Hypervolume Indicator (HVI) for the current set of observed
        objective values. HVI is a common metric for multi-objective optimization
        progress, representing the volume of the objective space dominated by the
        Pareto front and bounded by a reference point.

        Returns:
            Dict[str, float]: Dictionary containing 'raw_hypervolume', 'normalized_hypervolume',
                             and 'reference_point_info'. Returns dict with 0.0 values if there are
                             insufficient data points, no objectives, or if calculation fails.
        """
        default_result = {
            "raw_hypervolume": 0.0,
            "normalized_hypervolume": 0.0,
            "reference_point_adaptive": True,
            "data_points_used": 0,
        }

        try:
            # Hypervolume is meaningful for at least two objectives.
            if len(self.objective_names) < 2 or not hasattr(self, "train_Y"):
                logger.debug(
                    "Hypervolume calculation skipped: Less than 2 objectives or no training data."
                )
                return default_result

            Y = self.train_Y
            if Y.shape[0] == 0:
                logger.debug(
                    "Hypervolume calculation skipped: No data points in train_Y."
                )
                return default_result

            # Filter out rows containing NaN values, as they cannot be used for HVI calculation.
            # Move to CPU to avoid CUDA memory issues
            Y_cpu = Y.cpu() if Y.is_cuda else Y
            finite_mask = torch.isfinite(Y_cpu).all(dim=1)
            if not finite_mask.any():
                logger.debug("Hypervolume calculation skipped: No finite data points.")
                return default_result

            clean_Y = Y_cpu[finite_mask]

            if clean_Y.shape[0] < 2:
                logger.debug(
                    f"Hypervolume calculation skipped: Less than 2 clean data points ({clean_Y.shape[0]}) for HVI."
                )
                return default_result

            logger.debug(f"clean_Y shape: {clean_Y.shape}")
            logger.debug(
                f"clean_Y min: {clean_Y.min(dim=0)[0]}, max: {clean_Y.max(dim=0)[0]}"
            )

            # Calculate adaptive reference point
            ref_point = self._calculate_adaptive_reference_point(clean_Y)

            # Calculate hypervolume using BoTorch's FastNondominatedPartitioning.
            try:
                logger.debug(f"Adaptive ref point for HVI: {ref_point}")
                partitioning = FastNondominatedPartitioning(
                    ref_point=ref_point, Y=clean_Y
                )
                raw_hypervolume = partitioning.compute_hypervolume().item()

                # Calculate normalized hypervolume for better interpretability
                max_observed_Y = clean_Y.max(dim=0)[0]
                theoretical_max_volume = torch.prod(max_observed_Y - ref_point)

                # Avoid division by zero
                if theoretical_max_volume.item() > 1e-12:
                    normalized_hypervolume = (
                        raw_hypervolume / theoretical_max_volume.item()
                    )
                else:
                    normalized_hypervolume = 0.0

                # Ensure normalized hypervolume is between 0 and 1
                normalized_hypervolume = max(0.0, min(1.0, normalized_hypervolume))

                result = {
                    "raw_hypervolume": raw_hypervolume,
                    "normalized_hypervolume": normalized_hypervolume,
                    "reference_point_adaptive": True,
                    "data_points_used": clean_Y.shape[0],
                }

                logger.debug(f"Raw hypervolume: {raw_hypervolume}")
                logger.debug(f"Normalized hypervolume: {normalized_hypervolume}")
                logger.debug(f"Theoretical max volume: {theoretical_max_volume.item()}")

                return result

            except Exception as e:
                logger.warning(
                    f"Hypervolume calculation failed (FastNondominatedPartitioning): {e}"
                )
                return default_result

        except Exception as e:
            logger.error(f"Error in _calculate_hypervolume: {e}", exc_info=True)
            return default_result

    def _calculate_hypervolume_legacy(self) -> float:
        """
        Legacy method that returns only the raw hypervolume for backward compatibility.
        This maintains compatibility with existing code that expects a float return.

        Returns:
            float: Raw hypervolume value
        """
        hv_result = self._calculate_hypervolume()
        return hv_result["raw_hypervolume"]

    def check_hypervolume_convergence(
        self, window_size: int = 5, threshold: float = 0.01, use_normalized: bool = True
    ) -> Dict[str, Any]:
        """
        Checks for hypervolume-based convergence using a sliding window approach.
        Only considers optimization iterations for convergence analysis (excludes baseline and batch imports).

        Args:
            window_size: Number of recent optimization iterations to consider for convergence
            threshold: Relative change threshold below which we consider convergence
            use_normalized: Whether to use normalized hypervolume for convergence check

        Returns:
            Dict containing convergence status, metrics, and recommendations
        """
        convergence_result = {
            "converged": False,
            "progress_stagnant": False,
            "iterations_stable": 0,
            "relative_improvement": 0.0,
            "recommendation": "continue",
            "confidence": "low",
        }

        try:
            # Filter to only optimization iterations (exclude baseline and batch imports)
            optimization_iterations = [
                h for h in self.iteration_history 
                if h.get("iteration_type") == "optimization"
            ]
            
            if len(optimization_iterations) < window_size:
                convergence_result["recommendation"] = "continue - insufficient optimization data"
                convergence_result["note"] = f"Need {window_size - len(optimization_iterations)} more optimization iterations"
                return convergence_result

            # Extract hypervolume values from recent optimization iterations
            hv_key = "normalized_hypervolume" if use_normalized else "hypervolume"

            # Handle both old format (float) and new format (dict) for recent optimization iterations
            recent_hvs = []
            for iteration in optimization_iterations[-window_size:]:
                hv_value = iteration.get("hypervolume", 0.0)
                if isinstance(hv_value, dict):
                    recent_hvs.append(hv_value.get(hv_key, 0.0))
                else:
                    # Legacy format - use raw value
                    recent_hvs.append(hv_value)

            if not recent_hvs or all(hv == 0.0 for hv in recent_hvs):
                convergence_result["recommendation"] = (
                    "continue - no valid hypervolume data"
                )
                return convergence_result

            # Calculate relative improvement
            max_hv = max(recent_hvs)
            min_hv = min(recent_hvs)

            if max_hv > 1e-12:
                relative_improvement = (max_hv - min_hv) / max_hv
            else:
                relative_improvement = 0.0

            convergence_result["relative_improvement"] = relative_improvement

            # Check for convergence
            if relative_improvement < threshold:
                convergence_result["converged"] = True
                convergence_result["iterations_stable"] = window_size
                convergence_result["confidence"] = (
                    "high" if window_size >= 10 else "medium"
                )

                # Additional check: is hypervolume actually improving over longer period?
                if len(optimization_iterations) >= window_size * 2:
                    earlier_hvs = []
                    for iteration in optimization_iterations[
                        -(window_size * 2) : -window_size
                    ]:
                        hv_value = iteration.get("hypervolume", 0.0)
                        if isinstance(hv_value, dict):
                            earlier_hvs.append(hv_value.get(hv_key, 0.0))
                        else:
                            earlier_hvs.append(hv_value)

                    if earlier_hvs and max(earlier_hvs) > 1e-12:
                        long_term_improvement = (
                            max(recent_hvs) - max(earlier_hvs)
                        ) / max(earlier_hvs)

                        if long_term_improvement < threshold / 2:
                            convergence_result["progress_stagnant"] = True
                            convergence_result["recommendation"] = "consider_stopping"
                        else:
                            convergence_result["recommendation"] = "continue_cautiously"
                    else:
                        convergence_result["recommendation"] = "continue_cautiously"
                else:
                    convergence_result["recommendation"] = "continue_cautiously"
            else:
                convergence_result["recommendation"] = "continue"

            # Calculate trend
            if len(recent_hvs) >= 3:
                # Simple linear trend analysis
                x = list(range(len(recent_hvs)))
                n = len(recent_hvs)
                sum_x = sum(x)
                sum_y = sum(recent_hvs)
                sum_xy = sum(xi * yi for xi, yi in zip(x, recent_hvs))
                sum_x2 = sum(xi * xi for xi in x)

                if n * sum_x2 - sum_x * sum_x != 0:
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    convergence_result["trend_slope"] = slope

                    if slope < -threshold / 10:
                        convergence_result["recommendation"] = "investigate_degradation"

            logger.debug(f"Convergence check: {convergence_result}")
            return convergence_result

        except Exception as e:
            logger.error(f"Error in convergence check: {e}", exc_info=True)
            convergence_result["recommendation"] = "continue - error in analysis"
            return convergence_result

    def get_optimization_progress_summary(self) -> Dict[str, Any]:
        """
        Provides a comprehensive summary of optimization progress including
        hypervolume trends, convergence status, and recommendations.
        Uses the hybrid approach: distinguishes baseline data from optimization progress.

        Returns:
            Dict containing detailed progress analysis
        """
        # Separate different types of iterations
        baseline_iterations = [h for h in self.iteration_history if h.get("is_baseline", False)]
        optimization_iterations = [h for h in self.iteration_history if h.get("iteration_type") == "optimization"]
        batch_import_iterations = [h for h in self.iteration_history if h.get("iteration_type") == "batch_import"]
        
        summary = {
            "total_iterations": len(self.iteration_history),
            "baseline_iterations": len(baseline_iterations),
            "optimization_iterations": len(optimization_iterations), 
            "batch_import_iterations": len(batch_import_iterations),
            "total_experiments": (
                len(self.experimental_data) if hasattr(self, "experimental_data") else 0
            ),
            "baseline_hypervolume": self.baseline_hypervolume,
            "current_hypervolume": None,
            "improvement_over_baseline": 0.0,
            "hypervolume_trend": "unknown",
            "convergence_status": "unknown",
            "efficiency_metrics": {},
            "recommendations": [],
        }

        try:
            if not self.iteration_history:
                summary["recommendations"].append(
                    "Start optimization by adding experimental data"
                )
                return summary

            # Get current hypervolume
            latest_iteration = self.iteration_history[-1]
            hv_value = latest_iteration.get("hypervolume", 0.0)

            if isinstance(hv_value, dict):
                summary["current_hypervolume"] = {
                    "raw": hv_value.get("raw_hypervolume", 0.0),
                    "normalized": hv_value.get("normalized_hypervolume", 0.0),
                    "data_points_used": hv_value.get("data_points_used", 0),
                }
            else:
                summary["current_hypervolume"] = {"raw": hv_value, "normalized": None}

            # Analyze trend over recent iterations
            if len(self.iteration_history) >= 3:
                recent_iterations = min(10, len(self.iteration_history))
                recent_hvs = []

                for iteration in self.iteration_history[-recent_iterations:]:
                    hv_val = iteration.get("hypervolume", 0.0)
                    if isinstance(hv_val, dict):
                        recent_hvs.append(hv_val.get("raw_hypervolume", 0.0))
                    else:
                        recent_hvs.append(hv_val)

                if len(recent_hvs) >= 3 and max(recent_hvs) > 1e-12:
                    first_third = sum(recent_hvs[: len(recent_hvs) // 3]) / (
                        len(recent_hvs) // 3
                    )
                    last_third = sum(recent_hvs[-len(recent_hvs) // 3 :]) / (
                        len(recent_hvs) // 3
                    )

                    relative_change = (last_third - first_third) / max(
                        first_third, 1e-12
                    )

                    if relative_change > 0.05:
                        summary["hypervolume_trend"] = "improving"
                    elif relative_change > -0.02:
                        summary["hypervolume_trend"] = "stable"
                    else:
                        summary["hypervolume_trend"] = "declining"

            # Check convergence
            convergence_result = self.check_hypervolume_convergence()
            summary["convergence_status"] = convergence_result["recommendation"]
            summary["convergence_details"] = convergence_result

            # Calculate efficiency metrics
            if len(self.iteration_history) > 1:
                # Hypervolume per experiment efficiency
                current_hv = (
                    summary["current_hypervolume"]["raw"]
                    if summary["current_hypervolume"]
                    else 0.0
                )
                experiments_count = summary["total_experiments"]

                if experiments_count > 0:
                    summary["efficiency_metrics"]["hv_per_experiment"] = (
                        current_hv / experiments_count
                    )

                # Rate of improvement
                if len(self.iteration_history) >= 5:
                    early_hv = self.iteration_history[
                        min(4, len(self.iteration_history) - 1)
                    ].get("hypervolume", 0.0)
                    if isinstance(early_hv, dict):
                        early_hv = early_hv.get("raw_hypervolume", 0.0)

                    if early_hv > 1e-12:
                        improvement_rate = (current_hv - early_hv) / early_hv
                        summary["efficiency_metrics"][
                            "improvement_rate"
                        ] = improvement_rate

            # Generate recommendations
            if summary["hypervolume_trend"] == "declining":
                summary["recommendations"].append(
                    "Check for overfitting or data quality issues"
                )
            elif (
                summary["hypervolume_trend"] == "stable"
                and len(self.iteration_history) > 10
            ):
                summary["recommendations"].append(
                    "Consider exploring different regions of parameter space"
                )
            elif convergence_result["converged"]:
                summary["recommendations"].append(
                    "Optimization may have converged - consider validation experiments"
                )
            else:
                summary["recommendations"].append(
                    "Continue optimization - good progress being made"
                )

            return summary

        except Exception as e:
            logger.error(f"Error generating progress summary: {e}", exc_info=True)
            summary["recommendations"].append(
                "Error in progress analysis - continue with caution"
            )
            return summary

    def get_cached_hypervolume_data(self) -> Dict[str, Any]:
        """Get cached hypervolume data if available, otherwise calculate fresh"""
        if self._cached_hypervolume_data:
            logger.info("Using cached hypervolume data")
            return self._cached_hypervolume_data
        else:
            logger.info("No cached hypervolume data found, calculating fresh")
            try:
                current_hv = self._calculate_hypervolume()
                progress_summary = self.get_optimization_progress_summary()
                convergence_data = self.check_hypervolume_convergence()

                return {
                    "current_hypervolume": current_hv,
                    "progress_summary": progress_summary,
                    "convergence_analysis": convergence_data,
                    "calculation_timestamp": pd.Timestamp.now().isoformat(),
                }
            except Exception as e:
                logger.error(f"Error calculating hypervolume data: {e}")
                return {}

    def set_cached_hypervolume_data(self, cached_data: Dict[str, Any]):
        """Set cached hypervolume data (used when loading from file)"""
        self._cached_hypervolume_data = cached_data
        logger.info("Cached hypervolume data has been set")

    @performance_timer if PERFORMANCE_OPTIMIZATION_AVAILABLE else lambda x: x
    def suggest_next_experiment(self, n_suggestions: int = 1) -> List[Dict[str, Any]]:
        """
        Generates suggestions for the next set of experiments using Bayesian optimization.
        If insufficient data is available, it falls back to initial sampling methods
        (e.g., random or Latin Hypercube Sampling).

        Args:
            n_suggestions (int): The number of parameter combinations to suggest.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a suggested
                                  parameter combination in its original scale.
        """
        try:
            # Ensure training data is updated if experimental data exists but tensors don't
            if (
                not hasattr(self, "train_X") or not hasattr(self, "train_Y")
            ) and not self.experimental_data.empty:
                logger.info("Updating training data tensors from experimental data")
                self._update_training_data()

            # Check if there's enough data to train the Gaussian Process models.
            if (
                not hasattr(self, "train_X")
                or not hasattr(self, "train_Y")
                or self.train_X.shape[0] < MIN_DATA_POINTS_FOR_GP
            ):
                logger.info("Insufficient data for GP. Using initial sampling method.")
                if self.initial_sampling_method == "LHS":
                    return self._generate_doe_samples(n_suggestions, method="LHS")
                else:
                    return self._generate_random_samples(n_suggestions)

            # Build the Gaussian Process models based on the current experimental data.
            models = self._build_models()
            if models is None:
                logger.warning("Could not build models. Using random sampling.")
                return self._generate_random_samples(n_suggestions)

            # Set up the acquisition function (e.g., Expected Hypervolume Improvement for MOO,
            # Expected Improvement for SOO).
            acq_func = self._setup_acquisition_function(models)
            if acq_func is None:
                logger.warning(
                    "Could not set up acquisition function. Using random sampling."
                )
                return self._generate_random_samples(n_suggestions)

            # Optimize the acquisition function to find the next best experimental points.
            suggestions = self._optimize_acquisition_function(acq_func, n_suggestions)

            logger.info(f"🎯 Generated {len(suggestions)} new experiment suggestions using Bayesian optimization")
            return suggestions

        except Exception as e:
            logger.error(f"Error in suggest_next_experiment: {e}", exc_info=True)
            # Fallback to random sampling in case of any unexpected error.
            return self._generate_random_samples(n_suggestions)

    def _cache_candidates(self, candidates: torch.Tensor, optimization_time: float):
        """Cache optimization candidates for potential reuse."""
        try:
            # Store candidates with metadata
            cache_entry = {
                'candidates': candidates.clone().detach(),
                'timestamp': time.time(),
                'optimization_time': optimization_time,
                'data_size': len(self.experimental_data) if hasattr(self, 'experimental_data') and not self.experimental_data.empty else 0
            }
            
            self._candidate_cache.append(cache_entry)
            
            # Maintain cache size limit
            if len(self._candidate_cache) > self._cache_max_size:
                self._candidate_cache.pop(0)  # Remove oldest entry
                
            logger.debug(f"Cached {len(candidates)} candidates (cache size: {len(self._candidate_cache)})")
            
        except Exception as e:
            logger.debug(f"Failed to cache candidates: {e}")

    def _try_cached_candidates(self, n_suggestions: int, current_data_size: int) -> Optional[List[Dict[str, Any]]]:
        """Try to reuse cached candidates if optimization is taking too long."""
        try:
            if not self._candidate_cache:
                return None
                
            # Find candidates from similar data sizes (within 50% range or any if few options)
            suitable_entries = []
            for entry in self._candidate_cache:
                if current_data_size <= 1:
                    # For very small datasets, any cache entry is suitable
                    suitable_entries.append(entry)
                else:
                    data_size_diff = abs(entry['data_size'] - current_data_size) / max(current_data_size, 1)
                    if data_size_diff <= 0.5:  # Within 50% of current data size (more lenient)
                        suitable_entries.append(entry)
            
            # If no suitable entries with size matching, use any available entry
            if not suitable_entries and len(self._candidate_cache) > 0:
                suitable_entries = list(self._candidate_cache)
                logger.debug("Using any available cached candidates (no size match)")
                
            # Use the most recent suitable entry
            best_entry = max(suitable_entries, key=lambda x: x['timestamp'])
            cached_candidates = best_entry['candidates']
            
            # Select random subset if we have more than needed
            if len(cached_candidates) >= n_suggestions:
                indices = torch.randperm(len(cached_candidates))[:n_suggestions]
                selected_candidates = cached_candidates[indices]
            else:
                selected_candidates = cached_candidates
                
            # Convert to parameter dictionaries
            suggestions = []
            for i in range(len(selected_candidates)):
                param_dict = self.parameter_transformer.tensor_to_params(selected_candidates[i])
                suggestions.append(param_dict)
            
            logger.info(f"🔄 Using {len(suggestions)} cached candidates (saved optimization time)")
            return suggestions
            
        except Exception as e:
            logger.debug(f"Failed to use cached candidates: {e}")
            return None

    def _generate_random_samples(self, n_suggestions: int) -> List[Dict[str, Any]]:
        """
        Generates random samples in the parameter space. This is used as a fallback
        or for initial data generation when more sophisticated methods are not applicable.

        Args:
            n_suggestions (int): The number of random samples to generate.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a randomly
                                  generated parameter combination.
        """
        suggestions = []
        max_attempts = n_suggestions * 10  # Limit attempts to prevent infinite loops
        attempts = 0

        while len(suggestions) < n_suggestions and attempts < max_attempts:
            # Generate a random sample in the normalized [0, 1] space for each parameter.
            sample = torch.rand(
                len(self.parameter_transformer.param_names), dtype=self.dtype
            )
            # Convert the normalized sample back to the original parameter dictionary.
            param_dict = self.parameter_transformer.tensor_to_params(sample)

            # Check for uniqueness to avoid duplicate suggestions.
            is_unique = True
            for existing in suggestions:
                if self._are_params_similar(param_dict, existing):
                    is_unique = False
                    break

            if is_unique:
                suggestions.append(param_dict)

            attempts += 1

        logger.debug(f"Generated {len(suggestions)} random suggestions.")
        return suggestions

    def _are_params_similar(
        self, params1: Dict[str, Any], params2: Dict[str, Any], rtol: float = 1e-3
    ) -> bool:
        """
        Compares two sets of parameters to determine if they are similar within a
        given relative tolerance. This is used to avoid suggesting duplicate experiments.

        Args:
            params1 (Dict[str, Any]): The first dictionary of parameters.
            params2 (Dict[str, Any]): The second dictionary of parameters.
            rtol (float): The relative tolerance for comparing numerical values.

        Returns:
            bool: True if the parameter sets are similar, False otherwise.
        """
        # Check if all keys in params1 are present in params2 and vice-versa
        if set(params1.keys()) != set(params2.keys()):
            return False

        for key in params1:
            val1, val2 = params1[key], params2[key]

            # Compare numerical values using numpy.isclose for tolerance.
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                if not np.isclose(val1, val2, rtol=rtol):
                    return False
            # For non-numerical values, perform exact comparison.
            elif val1 != val2:
                return False

        return True

    def _build_models(self) -> Optional[ModelListGP]:
        """
        Builds and fits Gaussian Process (GP) models for each objective.
        A `SingleTaskGP` model is created for each objective, and then all
        models are combined into a `ModelListGP`.

        Returns:
            Optional[ModelListGP]: A `ModelListGP` containing the fitted GP models,
                                   or None if models cannot be built (e.g., insufficient data).
        """
        try:
            # Check if training data exists
            if not hasattr(self, "train_X") or not hasattr(self, "train_Y"):
                logger.warning("No training data available for model building.")
                return None

            if self.train_X.shape[0] == 0 or self.train_Y.shape[0] == 0:
                logger.warning("Empty training data for model building.")
                return None

            models = []

            for i, obj_name in enumerate(self.objective_names):
                if i >= self.train_Y.shape[1]:
                    logger.warning(
                        f"Objective index {i} exceeds training data dimensions for {obj_name}"
                    )
                    continue

                Y_obj = self.train_Y[:, i]

                # Filter out non-finite (NaN or Inf) values for the current objective.
                finite_mask = torch.isfinite(Y_obj)
                if finite_mask.sum() < MIN_DATA_POINTS_FOR_GP:
                    logger.warning(
                        f"Insufficient finite data points ({finite_mask.sum()}) for objective {obj_name}. Skipping model building for this objective."
                    )
                    continue

                X_filtered = self.train_X[finite_mask]
                Y_filtered = Y_obj[finite_mask].unsqueeze(
                    -1
                )  # Add a feature dimension for BoTorch.

                # Initialize a SingleTaskGP model.
                # - `MaternKernel` with nu=2.5 is a common choice for smooth functions.
                # - `ScaleKernel` scales the output of the Matern kernel.
                # - `Normalize` input transform normalizes input features to [0, 1].
                # - `Standardize` outcome transform standardizes output features to zero mean and unit variance.
                # Create appropriate kernel based on parameter types (mixed variables support)
                base_kernel = create_kernel_for_parameters(self.params_config, X_filtered.shape[-1])
                covar_module = ScaleKernel(base_kernel)
                
                model = SingleTaskGP(
                    train_X=X_filtered,
                    train_Y=Y_filtered,
                    covar_module=covar_module,
                    input_transform=Normalize(d=X_filtered.shape[-1]),
                    outcome_transform=Standardize(m=1),
                )

                # Fit the GP model by optimizing the marginal log-likelihood.
                mll = ExactMarginalLogLikelihood(model.likelihood, model)
                
                # Apply optimized GP fitting with Cholesky decomposition preference
                try:
                    # Use optimized fitting with potential Cholesky acceleration
                    self._fit_gp_model_optimized(mll)
                except Exception as e:
                    logger.warning(f"Optimized GP fitting failed ({e}), falling back to standard fitting")
                    fit_gpytorch_mll(mll)

                models.append(model)

            if not models:
                logger.warning("No GP models could be built for any objective.")
                return None

            # Validate that we have models for all objectives
            if len(models) != len(self.objective_names):
                logger.error(f"Model count mismatch: built {len(models)} models for {len(self.objective_names)} objectives")
                logger.error(f"Objectives: {self.objective_names}")
                logger.error("This can cause dimension mismatches in acquisition functions")
                return None

            # Return a ModelListGP if multiple objectives, or the single model if only one.
            logger.debug(f"Successfully built {len(models)} models for objectives: {self.objective_names}")
            return ModelListGP(*models) if len(models) > 1 else models[0]

        except Exception as e:
            logger.error(f"Error building models: {e}", exc_info=True)
            return None

    def _setup_acquisition_function(
        self, models: Union[SingleTaskGP, ModelListGP]
    ) -> Optional[Union[LogExpectedImprovement, ExpectedHypervolumeImprovement]]:
        """
        Sets up the appropriate acquisition function based on the number of objectives and weights.
        
        Modern version automatically uses:
        - qLogEI for single-objective optimization (improved numerical stability)
        - qNEHVI for multi-objective optimization (2024 state-of-the-art)
        - UnifiedExponentialKernel for mixed variable types (continuous, discrete, categorical)
        
        Falls back to legacy EHVI/LogEI if modern methods are unavailable.

        Args:
            models (Union[SingleTaskGP, ModelListGP]): The fitted GP model(s).

        Returns:
            Modern acquisition function (qNEHVI/qLogEI) or legacy fallback.
        """
        try:
            if not hasattr(self, "train_Y") or self.train_Y.shape[0] == 0:
                logger.warning(
                    "No training data available to set up acquisition function."
                )
                return None
            
            # Try modern acquisition functions first
            if MODERN_ACQUISITION_AVAILABLE:
                try:
                    # Extract parameter configuration for UnifiedExponentialKernel
                    params_config = getattr(self, 'parameters', None)
                    if not params_config and hasattr(self, 'parameter_transformer'):
                        # Try to reconstruct params_config from parameter_transformer
                        param_names = getattr(self.parameter_transformer, 'param_names', [])
                        params_config = {}
                        for name in param_names:
                            # Default to continuous for safety if we can't determine type
                            params_config[name] = {'type': 'continuous', 'bounds': [0, 1]}
                    
                    # Create modern acquisition function
                    logger.info("Attempting to create modern acquisition function (qNEHVI/qLogEI)")
                    modern_acq = create_modern_acquisition_function(
                        train_X=self.train_X,
                        train_Y=self.train_Y,
                        objective_names=self.objective_names,
                        params_config=params_config
                    )
                    
                    if modern_acq is not None:
                        logger.info(f"SUCCESS: Created modern acquisition function: {type(modern_acq).__name__}")
                        return modern_acq
                    else:
                        logger.warning("Modern acquisition function creation failed, falling back to legacy")
                        
                except Exception as e:
                    logger.warning(f"Modern acquisition function failed: {e}, falling back to legacy")
            
            # Fall back to legacy acquisition functions
            logger.info("Using legacy acquisition functions (EHVI/LogEI)")

            if len(self.objective_names) > 1:
                # Multi-objective optimization
                if hasattr(self, 'has_weighted_objectives') and self.has_weighted_objectives:
                    # Use weighted scalarization approach for weighted objectives
                    logger.info("Using weighted scalarization for multi-objective optimization with importance weights")
                    return self._setup_weighted_scalarization_acquisition(models)
                else:
                    # Use EHVI for standard Pareto optimization
                    finite_mask = torch.isfinite(self.train_Y).all(dim=1)
                if not finite_mask.any():
                    logger.warning("No finite data points for EHVI calculation.")
                    return None
                clean_Y = self.train_Y[finite_mask]

                if clean_Y.shape[0] == 0:
                    logger.warning("No clean data points for EHVI calculation.")
                    return None

                # Use the same adaptive reference point calculation as in hypervolume calculation
                # This ensures consistency between hypervolume measurement and acquisition optimization
                ref_point = self._calculate_adaptive_reference_point(clean_Y)

                logger.debug(f"Ref point for HVI: {ref_point}")
                logger.debug(f"Clean Y shape: {clean_Y.shape}")
                logger.debug(f"Ref point shape: {ref_point.shape}")
                
                # Validate dimensions before creating acquisition function
                if ref_point.shape[0] != clean_Y.shape[1]:
                    logger.error(f"Dimension mismatch: ref_point has {ref_point.shape[0]} dimensions, "
                               f"but clean_Y has {clean_Y.shape[1]} objectives")
                    return None
                
                try:
                    partitioning = FastNondominatedPartitioning(
                        ref_point=ref_point, Y=clean_Y
                    )
                    
                    # Additional validation for model compatibility
                    if isinstance(models, ModelListGP):
                        expected_outputs = len(models.models)
                    else:
                        expected_outputs = models.num_outputs if hasattr(models, 'num_outputs') else 1
                    
                    if expected_outputs != clean_Y.shape[1]:
                        logger.error(f"Model outputs ({expected_outputs}) don't match data objectives ({clean_Y.shape[1]})")
                        return None
                    
                    ehvi = ExpectedHypervolumeImprovement(
                        model=models,
                        ref_point=ref_point.tolist(),
                        partitioning=partitioning,
                    )
                    
                    # Test the acquisition function with a dummy input to catch dimension issues early
                    try:
                        test_input = torch.randn(1, len(self.parameter_transformer.param_names), 
                                               dtype=self.dtype, device=self.device)
                        test_output = ehvi(test_input)
                        logger.debug(f"EHVI test successful: output shape {test_output.shape}")
                        return ehvi
                    except Exception as test_e:
                        logger.error(f"EHVI test failed with test input: {test_e}")
                        logger.error(f"Test input shape: {test_input.shape}")
                        logger.error(f"Expected parameters: {len(self.parameter_transformer.param_names)}")
                        
                        # Try fallback to simpler acquisition function for multi-objective
                        logger.warning("Attempting fallback to scalarized Expected Improvement")
                        try:
                            # Use a simple weighted scalarization as fallback
                            return self._create_scalarized_ei_fallback(models, clean_Y)
                        except Exception as fallback_e:
                            logger.error(f"Fallback acquisition function also failed: {fallback_e}")
                            return None
                except Exception as e:
                    logger.error(
                        f"Error creating EHVI acquisition function: {e}"
                    )
                    logger.error(f"Model type: {type(models)}")
                    logger.error(f"Clean Y shape: {clean_Y.shape}")
                    logger.error(f"Ref point: {ref_point}")
                    return None
            else:
                # Single objective: use EI
                finite_Y = self.train_Y[torch.isfinite(self.train_Y)]
                if finite_Y.numel() == 0:
                    logger.warning("No finite data points for EI calculation.")
                    return None

                # best_f is the maximum observed value in the transformed space
                # (which is correct for both maximization and minimization after negation)
                best_f = finite_Y.max()
                # If models is a SingleTaskGP, use it directly; otherwise, use models.models[0]
                if isinstance(models, SingleTaskGP):
                    return LogExpectedImprovement(model=models, best_f=best_f)
                else:
                    return LogExpectedImprovement(model=models.models[0], best_f=best_f)

        except Exception as e:
            logger.error(f"Error setting up acquisition function: {e}", exc_info=True)
            return None

    def _create_scalarized_ei_fallback(self, models, clean_Y):
        """
        Creates a fallback scalarized Expected Improvement acquisition function
        when EHVI fails due to dimension mismatches.
        
        Args:
            models: The GP models
            clean_Y: Clean training objectives
            
        Returns:
            A scalarized acquisition function or None if it fails
        """
        try:
            from botorch.acquisition.multi_objective import qExpectedImprovement
            from botorch.utils.multi_objective.scalarization import get_chebyshev_scalarization
            
            # Create equal weights for all objectives (could be made configurable)
            weights = torch.ones(clean_Y.shape[1], dtype=self.dtype, device=self.device) / clean_Y.shape[1]
            
            # Use Chebyshev scalarization
            transform = get_chebyshev_scalarization(weights=weights, Y=clean_Y)
            
            # Create scalarized EI
            scalarized_ei = qExpectedImprovement(
                model=models,
                objective=transform,
                best_f=transform(clean_Y).max(),
            )
            
            # Test the fallback acquisition function
            test_input = torch.randn(1, len(self.parameter_transformer.param_names), 
                                   dtype=self.dtype, device=self.device)
            test_output = scalarized_ei(test_input)
            logger.info(f"Scalarized EI fallback successful: output shape {test_output.shape}")
            
            return scalarized_ei
            
        except Exception as e:
            logger.error(f"Failed to create scalarized EI fallback: {e}")
            return None

    def _setup_weighted_scalarization_acquisition(self, models):
        """
        Sets up a weighted scalarization acquisition function for multi-objective optimization
        with user-defined importance weights.
        
        This method creates a single-objective acquisition function by combining multiple
        objectives using the importance weights from the 5-star rating system. The weighted
        sum is: f_scalar(x) = w1 * f1(x) + w2 * f2(x) + ... where wi are the normalized weights.
        
        Args:
            models: The fitted GP model(s)
            
        Returns:
            LogExpectedImprovement acquisition function for the weighted scalarized objective
        """
        try:
            # Create weighted scalarized GP model
            from botorch.models.transforms.outcome import WeightedSumTransform
            from torch import tensor
            
            if not hasattr(self, "train_Y") or self.train_Y.shape[0] == 0:
                logger.warning("No training data available for weighted scalarization.")
                return None
                
            # Prepare weights tensor
            weights_tensor = tensor(
                self.objective_weights, 
                dtype=self.dtype, 
                device=self.device
            ).unsqueeze(0)  # Shape: (1, num_objectives)
            
            # Apply objective directions (maximize/minimize) to weights
            # For minimize objectives, we need negative weights since we're maximizing the scalarization
            direction_adjusted_weights = []
            for i, (weight, direction) in enumerate(zip(self.objective_weights, self.objective_directions)):
                # Direction: 1 for maximize, -1 for minimize
                # For scalarization, we want to maximize the weighted sum
                # So minimize objectives need negative contribution
                adjusted_weight = weight * direction
                direction_adjusted_weights.append(adjusted_weight)
            
            weights_tensor = tensor(
                direction_adjusted_weights,
                dtype=self.dtype,
                device=self.device
            ).unsqueeze(0)
            
            logger.info(f"Weighted scalarization weights: {direction_adjusted_weights}")
            
            # Create weighted sum transform
            weighted_transform = WeightedSumTransform(weights=weights_tensor)
            
            # Apply transform to create single-objective model
            if isinstance(models, ModelListGP):
                # For ModelListGP, we need to create a single model with weighted outputs
                from botorch.models.model_list_gp_regression import ModelListGP
                from botorch.models.transforms.outcome import ChainedOutcomeTransform
                
                # Create a new single-task GP with weighted transform
                from botorch.models import SingleTaskGP
                
                # Get training data
                finite_mask = torch.isfinite(self.train_Y).all(dim=1)
                clean_X = self.train_X[finite_mask]
                clean_Y = self.train_Y[finite_mask]
                
                # Apply weighting to training targets
                weighted_Y = weighted_transform(clean_Y.unsqueeze(-1)).squeeze(-1)  # Remove extra dims
                
                # Create single-task GP with weighted targets
                weighted_model = SingleTaskGP(
                    train_X=clean_X,
                    train_Y=weighted_Y,
                    outcome_transform=Standardize(m=1)  # Single output now
                )
                
                # Fit the weighted model
                from botorch.fit import fit_gpytorch_mll
                from gpytorch.mlls import ExactMarginalLogLikelihood
                
                mll = ExactMarginalLogLikelihood(weighted_model.likelihood, weighted_model)
                fit_gpytorch_mll(mll)
                
            else:
                # Single model case - apply transform
                weighted_model = models
                # Note: This case is less common for multi-objective
                
            # Create Expected Improvement acquisition function for the weighted objective
            # Find the best observed value for the weighted objective
            finite_mask = torch.isfinite(self.train_Y).all(dim=1)
            clean_Y = self.train_Y[finite_mask]
            
            if clean_Y.shape[0] == 0:
                logger.warning("No clean data points for weighted scalarization.")
                return None
                
            # Apply weighting to find best observed weighted value
            weighted_observed = weighted_transform(clean_Y.unsqueeze(-1)).squeeze(-1)
            best_f = weighted_observed.max().item()
            
            logger.info(f"Best observed weighted value: {best_f}")
            
            # Create Expected Improvement acquisition function
            from botorch.acquisition.analytic import ExpectedImprovement
            
            ei = ExpectedImprovement(
                model=weighted_model,
                best_f=best_f
            )
            
            # Test the acquisition function
            try:
                test_input = torch.randn(
                    1, len(self.parameter_transformer.param_names),
                    dtype=self.dtype, device=self.device
                )
                test_output = ei(test_input)
                logger.info(f"Weighted EI test successful: output shape {test_output.shape}")
                return ei
            except Exception as test_e:
                logger.error(f"Weighted EI test failed: {test_e}")
                return None
                
        except Exception as e:
            logger.error(f"Error setting up weighted scalarization acquisition: {e}", exc_info=True)
            return None

    def _optimize_acquisition_function(
        self,
        acq_func: Union[LogExpectedImprovement, ExpectedHypervolumeImprovement],
        n_suggestions: int,
    ) -> List[Dict[str, Any]]:
        """
        Optimizes the acquisition function to find the next set of suggested experimental
        points. This involves using a multi-start optimization approach to find the
        global optimum of the acquisition function.

        Args:
            acq_func (Union[LogExpectedImprovement, ExpectedHypervolumeImprovement]): The
                       initialized acquisition function to be optimized.
            n_suggestions (int): The number of suggested points to generate.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a suggested
                                  parameter combination in its original scale.
        """
        try:
            # Define the bounds for the optimization of the acquisition function.
            # These are typically the normalized [0, 1] bounds of the parameter space.
            bounds = torch.stack(
                [
                    torch.zeros(
                        len(self.parameter_transformer.param_names), dtype=self.dtype
                    ),
                    torch.ones(
                        len(self.parameter_transformer.param_names), dtype=self.dtype
                    ),
                ]
            ).to(self.device)

            # Adaptive optimization parameters based on dataset size and interactive use
            n_data = len(self.experimental_data) if hasattr(self, 'experimental_data') and not self.experimental_data.empty else 0
            
            if self.fast_validation_mode:
                # Ultra-fast mode for validation scenarios: minimal optimization for speed
                adaptive_restarts = 1
                adaptive_raw_samples = 2  # Ultra-aggressive for validation speed
                logger.debug(f"🚀 Ultra-fast validation mode: {adaptive_restarts} restarts, {adaptive_raw_samples} samples")
            elif n_data < 20:
                # Early exploration: prioritize speed over exhaustive search
                adaptive_restarts = min(2, self.num_restarts)  # Reduced from 3
                adaptive_raw_samples = min(12, self.raw_samples)  # Reduced from 20
                logger.debug(f"Using fast optimization for early exploration: {adaptive_restarts} restarts, {adaptive_raw_samples} samples")
            elif n_data < 100:
                # Medium exploration: balanced approach
                adaptive_restarts = min(3, self.num_restarts)  # Reduced from 4
                adaptive_raw_samples = min(20, self.raw_samples)  # Reduced from 30
                logger.debug(f"Using balanced optimization: {adaptive_restarts} restarts, {adaptive_raw_samples} samples")
            else:
                # Large datasets: use full optimization for better suggestions
                adaptive_restarts = self.num_restarts
                adaptive_raw_samples = self.raw_samples
                logger.debug(f"Using full optimization: {adaptive_restarts} restarts, {adaptive_raw_samples} samples")
            
            # Optimize the acquisition function using `optimize_acqf` from BoTorch.
            # `q` specifies the number of points to optimize for (batch size).
            # `num_restarts` and `raw_samples` control the multi-start optimization process.
            
            # Time-based adaptive optimization with fallback
            start_time = time.time()
            max_optimization_time = 1.0 if self.fast_validation_mode else 10.0  # Ultra-aggressive timeout for validation
            n_data = len(self.experimental_data) if hasattr(self, 'experimental_data') and not self.experimental_data.empty else 0
            
            # Check if we can use cached candidates in fast mode for very recent similar scenarios
            if self.fast_validation_mode and hasattr(self, '_slow_optimizations') and self._slow_optimizations >= 2:
                cached_suggestions = self._try_cached_candidates(n_suggestions, n_data)
                if cached_suggestions is not None:
                    return cached_suggestions
            
            # Ultra-aggressive fallback for validation: skip acquisition optimization after first few slow runs
            if self.fast_validation_mode and hasattr(self, '_slow_optimizations') and self._slow_optimizations >= 1:
                logger.debug("🚀 Ultra-fast validation mode: using random sampling fallback")
                return self._generate_random_samples(n_suggestions)
            
            try:
                # Try regular optimization with parameter constraints (Windows doesn't support SIGALRM timeout)
                # Include parameter constraints if any are defined
                optimization_kwargs = {
                    "acq_function": acq_func,
                    "bounds": bounds,
                    "q": n_suggestions,
                    "num_restarts": adaptive_restarts,
                    "raw_samples": adaptive_raw_samples,
                }
                
                # Add parameter constraints if defined (Target/Range goals)
                if hasattr(self, 'parameter_constraints') and self.parameter_constraints:
                    optimization_kwargs["inequality_constraints"] = self.parameter_constraints
                    logger.debug(f"Using {len(self.parameter_constraints)} parameter constraints in acquisition optimization")
                
                candidates, _ = optimize_acqf(**optimization_kwargs)
                
                optimization_time = time.time() - start_time
                if optimization_time > max_optimization_time:
                    logger.warning(f"Acquisition optimization took {optimization_time:.2f}s (target: {max_optimization_time}s)")
                    if self.fast_validation_mode:
                        self._slow_optimizations += 1
                        logger.debug(f"Slow optimization count: {self._slow_optimizations}")
                    
            except Exception as e:
                logger.warning(f"Acquisition optimization failed: {e}")
                logger.info("Falling back to minimal optimization settings")
                # Emergency fallback: use absolute minimum settings with constraints if available
                fallback_kwargs = {
                    "acq_function": acq_func,
                    "bounds": bounds,
                    "q": n_suggestions,
                    "num_restarts": 1,
                    "raw_samples": 2,
                }
                
                # Include constraints in fallback if they exist
                if hasattr(self, 'parameter_constraints') and self.parameter_constraints:
                    fallback_kwargs["inequality_constraints"] = self.parameter_constraints
                    logger.debug("Using parameter constraints in fallback optimization")
                
                candidates, _ = optimize_acqf(**fallback_kwargs)
                optimization_time = time.time() - start_time

            suggestions = []
            for i in range(candidates.shape[0]):
                # Convert the normalized candidate tensor back to a parameter dictionary.
                param_dict = self.parameter_transformer.tensor_to_params(candidates[i])
                
                # Validate and enforce parameter constraints if defined
                if hasattr(self, 'parameter_constraints') and self.parameter_constraints:
                    is_valid, violations = self.parameter_transformer.validate_parameter_constraints(param_dict)
                    if not is_valid:
                        logger.debug(f"Constraint violations detected: {violations}")
                        param_dict = self.parameter_transformer.enforce_parameter_constraints(param_dict)
                        logger.debug("Applied constraint enforcement to suggestion")
                
                suggestions.append(param_dict)

            # Cache successful candidates for potential reuse
            self._cache_candidates(candidates, optimization_time)
            
            # Ensure we don't return more suggestions than requested
            if len(suggestions) > n_suggestions:
                suggestions = suggestions[:n_suggestions]
                logger.warning(f"Generated {len(candidates)} candidates but only returning {n_suggestions} as requested")
            
            logger.info(
                f"Successfully optimized acquisition function and generated {len(suggestions)} candidates."
            )
            return suggestions

        except Exception as e:
            logger.error(f"Error optimizing acquisition function: {e}", exc_info=True)
            # Fallback to random sampling in case of any unexpected error.
            return self._generate_random_samples(n_suggestions)

    def get_pareto_front(self) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
        """
        Identifies and returns the Pareto front from the observed experimental data.
        The Pareto front consists of non-dominated solutions, meaning no other solution
        is better in all objectives.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
                - A DataFrame of parameters corresponding to the Pareto front.
                - A DataFrame of objective values corresponding to the Pareto front.
                - A NumPy array of original indices of the Pareto optimal points in the
                  `experimental_data` DataFrame.
                Returns empty DataFrames and array if no data or no finite data points.
        """
        try:
            if (
                not hasattr(self, "train_Y")
                or not hasattr(self, "train_X")
                or self.train_Y.shape[0] == 0
            ):
                logger.debug("No training data available to determine Pareto front.")
                return pd.DataFrame(), pd.DataFrame(), np.array([])

            # Filter out rows containing NaN values in objectives.
            finite_mask = torch.isfinite(self.train_Y).all(dim=1)
            if not finite_mask.any():
                logger.debug("No finite data points to determine Pareto front.")
                return pd.DataFrame(), pd.DataFrame(), np.array([])

            clean_Y = self.train_Y[finite_mask]  # Filtered objective values
            clean_X = self.train_X[finite_mask]  # Filtered parameter values
            clean_indices = torch.where(finite_mask)[
                0
            ]  # Original indices of finite points

            # Use BoTorch's `is_non_dominated` to find Pareto optimal points.
            pareto_mask = is_non_dominated(clean_Y)
            pareto_Y = clean_Y[pareto_mask]  # Objective values on the Pareto front
            pareto_X = clean_X[pareto_mask]  # Parameter values on the Pareto front
            pareto_indices = clean_indices[
                pareto_mask
            ]  # Original indices of Pareto points

            # Convert objective values back to their original scale (undo negation for minimization).
            pareto_Y_original = pareto_Y.clone()
            for i, direction in enumerate(self.objective_directions):
                if (
                    direction == -1
                ):  # If objective was minimized, negate back to original scale.
                    pareto_Y_original[:, i] = -pareto_Y_original[:, i]

            # Create Pandas DataFrames for the Pareto front parameters and objectives.
            pareto_X_df = pd.DataFrame(
                pareto_X.cpu().numpy(), columns=self.parameter_transformer.param_names
            )

            pareto_obj_df = pd.DataFrame(
                pareto_Y_original.cpu().numpy(), columns=self.objective_names
            )

            logger.debug(f"Found {len(pareto_X_df)} points on the Pareto front.")
            return pareto_X_df, pareto_obj_df, pareto_indices.cpu().numpy()

        except Exception as e:
            logger.error(f"Error getting Pareto front: {e}", exc_info=True)
            return pd.DataFrame(), pd.DataFrame(), np.array([])

    def get_best_compromise_solution(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Estimates the best optimal parameter combination and its predicted responses.
        This is achieved by generating the next suggested experiment (which is optimized
        by the acquisition function) and then predicting the responses for that point
        using the trained Gaussian Process models.

        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]:
                - A dictionary representing the best predicted parameter combination.
                - A dictionary representing the predicted responses (mean and 95% CI)
                  for the best parameter combination.
                Returns empty dictionaries if no suggestions can be generated or
                predictions fail.
        """
        try:
            # Get the next suggested experiment from the optimizer.
            # This point is already optimized to be "best" in terms of the acquisition function.
            suggestions = self.suggest_next_experiment(n_suggestions=1)

            if not suggestions:
                logger.warning("No suggestions generated for best compromise solution.")
                return {}, {}

            best_predicted_params = suggestions[0]

            # Predict the responses at this suggested parameter combination.
            predicted_responses = self.predict_responses_at(best_predicted_params)

            logger.info("Successfully estimated best compromise solution.")
            return best_predicted_params, predicted_responses

        except Exception as e:
            logger.error(
                f"Error estimating best compromise solution: {e}", exc_info=True
            )
            return {}, {}

    def predict_responses_at(
        self, param_dict: Dict[str, Any]
    ) -> Dict[str, Dict[str, float]]:
        """
        Predicts the mean and 95% confidence interval for each objective at a given
        parameter combination using the trained Gaussian Process models.

        Args:
            param_dict (Dict[str, Any]): A dictionary representing the parameter
                                         combination for which to make predictions.

        Returns:
            Dict[str, Dict[str, float]]: A dictionary where keys are objective names
                                        and values are dictionaries containing 'mean',
                                        'lower_ci', and 'upper_ci' for that objective.
                                        Returns an empty dictionary if models cannot be
                                        built or prediction fails.
        """
        try:
            # Build or retrieve the GP models.
            models = self._build_models()
            if not models:
                logger.warning("Cannot predict responses: No models available.")
                return {}

            # Convert the input parameter dictionary to a normalized tensor.
            param_tensor = self.parameter_transformer.params_to_tensor(param_dict)
            X_test = param_tensor.unsqueeze(0).to(self.device, self.dtype)  # Add a batch dimension and move to device

            predictions = {}
            # Iterate through each objective to get its prediction.
            for i, obj_name in enumerate(self.objective_names):
                # Handle both SingleTaskGP (single objective) and ModelListGP (multiple objectives)
                if hasattr(models, 'models'):
                    # Multiple objectives - ModelListGP
                    if i < len(models.models):
                        model = models.models[i]
                    else:
                        continue
                else:
                    # Single objective - SingleTaskGP
                    if i == 0:
                        model = models
                    else:
                        continue
                
                with torch.no_grad():  # Disable gradient calculations for inference.
                    posterior = model.posterior(X_test)
                    mean = posterior.mean.item()
                    std = posterior.variance.sqrt().item()

                    # Calculate 95% confidence interval using a Z-score of 1.96
                    # for a normal distribution.
                    z_score = 1.96
                    lower_ci = mean - z_score * std
                    upper_ci = mean + z_score * std

                    # Undo negation for minimization objectives to return values
                    # in their original scale.
                    if self.objective_directions[i] == -1:
                        mean = -mean
                        # Negate and swap CIs to maintain lower/upper order.
                        lower_ci, upper_ci = -upper_ci, -lower_ci

                    predictions[obj_name] = {
                        "mean": mean,
                        "lower_ci": lower_ci,
                        "upper_ci": upper_ci,
                    }

            logger.info(f"Successfully predicted responses for {param_dict}.")
            return predictions

        except Exception as e:
            logger.error(f"Error predicting responses: {e}", exc_info=True)
            return {}

    def get_response_models(self) -> Dict[str, SingleTaskGP]:
        """
        Builds and returns individual `SingleTaskGP` models for each response variable
        (objective or non-objective response) based on the current experimental data.
        These models can be used for plotting or further analysis of individual responses.

        Returns:
            Dict[str, SingleTaskGP]: A dictionary where keys are response names and values
                                    are the fitted `SingleTaskGP` models for those responses.
                                    Returns an empty dictionary if no models can be built.
        """
        try:
            # Debug logging to diagnose loading issues
            logger.debug(f'get_response_models() called')
            logger.debug(f'experimental_data shape: {self.experimental_data.shape if hasattr(self, "experimental_data") and not self.experimental_data.empty else "EMPTY"}')
            if hasattr(self, 'experimental_data') and not self.experimental_data.empty:
                logger.debug(f'experimental_data columns: {list(self.experimental_data.columns)}')
            logger.debug(f'responses_config keys: {list(self.responses_config.keys()) if self.responses_config else "NONE"}')
            logger.debug(f'parameter_transformer available: {hasattr(self, "parameter_transformer")}')
            models_dict = {}

            # Get candidate response names - try config first, then auto-detect from data
            candidate_responses = list(self.responses_config.keys()) if self.responses_config else []
            
            # If no responses found in config or config responses don't exist in data, auto-detect
            if not candidate_responses or not any(resp in self.experimental_data.columns for resp in candidate_responses):
                logger.debug("Auto-detecting response columns from experimental data")
                # Auto-detect responses: exclude parameter columns, keep numeric columns
                param_names = set(self.parameter_transformer.param_names) if hasattr(self, 'parameter_transformer') else set()
                candidate_responses = [
                    col for col in self.experimental_data.columns 
                    if col not in param_names and 
                    self.experimental_data[col].dtype in ['float64', 'float32', 'int64', 'int32'] and
                    not self.experimental_data[col].isna().all()
                ]
                logger.info(f"Auto-detected response columns: {candidate_responses}")

            # Iterate through each candidate response
            for response_name in candidate_responses:
                # Ensure the response data exists in the experimental data.
                if response_name not in self.experimental_data.columns:
                    logger.debug(
                        f"Response '{response_name}' not found in experimental data. Skipping model building."
                    )
                    continue

                X_data = []  # List to store parameter tensors for this response
                Y_data = []  # List to store response values for this response

                for _, row in self.experimental_data.iterrows():
                    # Extract parameter values for the current row.
                    param_dict = {
                        param_name: row[param_name]
                        for param_name in self.parameter_transformer.param_names
                    }

                    if response_name in row:
                        response_value = row[response_name]
                        # Handle cases where the response might be a list (e.g., multiple replicates).
                        if isinstance(response_value, list) and len(response_value) > 0:
                            mean_value = np.mean(response_value)
                        else:
                            mean_value = float(response_value)

                        # Only include finite (non-NaN) response values for model training.
                        if not np.isnan(mean_value):
                            X_tensor = self.parameter_transformer.params_to_tensor(
                                param_dict
                            )
                            X_data.append(X_tensor)
                            Y_data.append(mean_value)

                # Build a GP model only if sufficient data points are available for this response.
                logger.debug(f'Response {response_name}: {len(Y_data)} data points (need {MIN_DATA_POINTS_FOR_GP})')
                if len(Y_data) >= MIN_DATA_POINTS_FOR_GP:
                    X_tensor = torch.stack(X_data).to(self.device, self.dtype)
                    Y_tensor = torch.tensor(
                        Y_data, dtype=self.dtype, device=self.device
                    ).unsqueeze(
                        -1
                    )  # Add feature dimension.

                    # Initialize and fit a SingleTaskGP model for this response.
                    # Create appropriate kernel based on parameter types (mixed variables support)
                    base_kernel = create_kernel_for_parameters(self.params_config, X_tensor.shape[-1])
                    
                    model = SingleTaskGP(
                        train_X=X_tensor,
                        train_Y=Y_tensor,
                        covar_module=ScaleKernel(base_kernel),
                        input_transform=Normalize(d=X_tensor.shape[-1]),
                        outcome_transform=Standardize(m=1),
                    )

                    mll = ExactMarginalLogLikelihood(model.likelihood, model)
                    fit_gpytorch_mll(mll)

                    models_dict[response_name] = model
                    logger.debug(
                        f"Successfully built GP model for response: {response_name}"
                    )
                else:
                    logger.warning(
                        f"Insufficient data points ({len(Y_data)}) for response '{response_name}'. Skipping model building."
                    )

            return models_dict

        except Exception as e:
            logger.error(f"Error building response models: {e}", exc_info=True)
            return {}

    def get_predicted_values(self, response_name: str) -> np.ndarray:
        """
        Returns the predicted mean values for a given response based on the current
        experimental data and the fitted Gaussian Process model for that response.

        Args:
            response_name (str): The name of the response variable for which to get
                                 predicted values.

        Returns:
            np.ndarray: A NumPy array containing the predicted mean values for the
                        specified response at the observed experimental points.
                        Returns an empty array if no model is available or prediction fails.
        """
        try:
            models = self.get_response_models()
            model = models.get(response_name)

            if (
                model is None
                or not hasattr(self, "train_X")
                or self.train_X.shape[0] == 0
            ):
                logger.warning(
                    f"Cannot get predicted values for {response_name}: No model or training data available."
                )
                return np.array([])

            with torch.no_grad():
                # Predict the mean of the posterior distribution at the training points.
                posterior = model.posterior(model.train_inputs[0])
                mean = posterior.mean.squeeze().cpu().numpy()

                # Undo negation if the objective was minimized to return original scale.
                if response_name in self.objective_names:
                    obj_idx = self.objective_names.index(response_name)
                    if self.objective_directions[obj_idx] == -1:
                        mean = -mean

            logger.debug(
                f"Successfully retrieved predicted values for {response_name}."
            )
            return mean
        except Exception as e:
            logger.error(
                f"Error getting predicted values for {response_name}: {e}",
                exc_info=True,
            )
            return np.array([])

    def get_feature_importances(self, response_name: str) -> Dict[str, float]:
        """
        Extracts feature importances (inverse lengthscales) from the GP model for a given response.
        """
        try:
            models = self.get_response_models()
            model = models.get(response_name)

            if (
                model is None
                or not hasattr(model.covar_module, "base_kernel")
                or not hasattr(model.covar_module.base_kernel, "lengthscale")
            ):
                logger.warning(
                    f"Model for {response_name} does not have lengthscales for sensitivity analysis."
                )
                return {}

            # Lengthscales are typically inverse to importance: smaller lengthscale means more important feature
            # We take the inverse to represent importance
            lengthscales = (
                model.covar_module.base_kernel.lengthscale.squeeze()
                .detach()
                .cpu()
                .numpy()
            )

            # Handle input transforms if present
            if hasattr(model, "input_transform") and model.input_transform is not None:
                # If input is normalized, lengthscales are in normalized space.
                # For sensitivity, we care about relative importance, so direct inverse is usually fine.
                # If parameters have different scales, this might need more
                # sophisticated handling.
                pass

            importances = 1.0 / lengthscales

            # Normalize importances to sum to 1 for better interpretability
            total_importance = np.sum(importances)
            if total_importance > 0:
                importances = importances / total_importance

            feature_importances = {}
            for i, param_name in enumerate(self.parameter_transformer.param_names):
                feature_importances[param_name] = float(importances[i])  # Ensure JSON serializable

            return feature_importances
        except Exception as e:
            logger.error(f"Error getting feature importances for {response_name}: {e}")
            return {}
    
    def get_data_subsampling_info(self) -> Dict[str, Any]:
        """
        Returns information about the data subsampling configuration and current state.
        
        Returns:
            Dictionary containing subsampling configuration and statistics
        """
        info = {
            'subsampling_enabled': self.max_gp_points is not None,
            'max_gp_points': self.max_gp_points,
            'current_data_points': len(self.experimental_data) if hasattr(self, 'experimental_data') else 0,
            'recommended_limits': {
                'fast_mode': FAST_MODE_MAX_GP_POINTS,
                'default': DEFAULT_MAX_GP_POINTS,
                'maximum_recommended': MAX_RECOMMENDED_GP_POINTS
            }
        }
        
        if self.max_gp_points is not None and hasattr(self, 'experimental_data'):
            current_points = len(self.experimental_data)
            info.update({
                'is_at_limit': current_points >= self.max_gp_points,
                'utilization_percentage': (current_points / self.max_gp_points) * 100,
                'points_until_limit': max(0, self.max_gp_points - current_points)
            })
        
        return info
    
    def _fit_gp_model_optimized(self, mll):
        """
        Fit GP model with optimized matrix operations using Cholesky decomposition
        when possible for symmetric positive definite covariance matrices.
        
        Args:
            mll: Marginal log likelihood object from GPyTorch
        """
        import time
        start_time = time.time()
        
        try:
            # Standard GPyTorch fitting with optimizations
            # GPyTorch automatically uses Cholesky decomposition for SPD matrices
            fit_gpytorch_mll(mll)
            
            fit_time = time.time() - start_time
            
            # Log performance for monitoring
            n_data = mll.model.train_targets.shape[0] if hasattr(mll.model, 'train_targets') else 0
            if fit_time > 1.0:  # Log slow fits
                logger.debug(f"GP fitting took {fit_time:.3f}s for {n_data} data points")
            
        except Exception as e:
            logger.error(f"Optimized GP fitting failed: {e}")
            raise
    
    def get_matrix_performance_info(self) -> Dict[str, Any]:
        """
        Get information about matrix operation performance and BLAS backend.
        
        Returns:
            Dictionary with performance and backend information
        """
        info = {
            'blas_optimizations_applied': self.blas_optimizations_applied,
            'backend_info': {},
            'performance_recommendations': []
        }
        
        try:
            if hasattr(self, 'blas_optimizer'):
                info['backend_info'] = self.blas_optimizer._get_backend_info()
                info['performance_recommendations'] = self.blas_optimizer.get_optimization_recommendations()
            
            # Add data subsampling info if available
            if hasattr(self, 'max_gp_points'):
                subsampling_info = self.get_data_subsampling_info()
                info['data_subsampling'] = subsampling_info
            
            return info
            
        except Exception as e:
            logger.warning(f"Could not get matrix performance info: {e}")
            info['error'] = str(e)
            return info
    
