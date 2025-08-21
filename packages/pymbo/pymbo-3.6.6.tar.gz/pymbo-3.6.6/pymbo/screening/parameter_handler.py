"""
Parameter Handler for SGLBO Screening Module

Handles parameter validation, transformation, and constraint checking
for the screening optimization process.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional, Union
from scipy.stats import qmc

logger = logging.getLogger(__name__)


class ParameterHandler:
    """
    Handles parameter validation, transformation, and sampling for screening optimization.
    Compatible with the main software's parameter configuration format.
    """
    
    def __init__(self, params_config: Dict[str, Dict[str, Any]], allow_extrapolation: bool = True):
        """
        Initialize parameter handler with configuration.
        
        Args:
            params_config: Dictionary with parameter configurations matching main software format
                          e.g., {"Temperature": {"type": "continuous", "bounds": [25, 200]}}
            allow_extrapolation: If True, allows parameter suggestions beyond initial bounds
                               when gradient suggests better regions (default: True for screening)
        """
        self.params_config = params_config
        self.param_names = list(params_config.keys())
        self.n_params = len(self.param_names)
        self.allow_extrapolation = allow_extrapolation
        
        # Store original bounds for reference
        self.original_bounds = {}
        for param_name, config in params_config.items():
            if config["type"] in ["continuous", "discrete"]:
                self.original_bounds[param_name] = config["bounds"].copy()
        
        # Dynamic bounds that can expand during optimization
        self.current_bounds = {}
        
        # Validate configuration
        self._validate_config()
        
        # Setup parameter bounds and transformations
        self._setup_bounds()
        
        logger.info(f"Parameter handler initialized for {self.n_params} parameters: {self.param_names}")
        logger.info(f"Extrapolation beyond initial bounds: {'Enabled' if allow_extrapolation else 'Disabled'}")
    
    def _validate_config(self) -> None:
        """Validate parameter configuration for completeness and correctness."""
        if not isinstance(self.params_config, dict) or not self.params_config:
            raise ValueError("params_config must be a non-empty dictionary")
        
        valid_types = ['continuous', 'categorical', 'discrete']
        
        for param_name, config in self.params_config.items():
            if not isinstance(config, dict):
                raise ValueError(f"Parameter '{param_name}' config must be a dictionary")
            
            # Check required fields
            if 'type' not in config:
                raise ValueError(f"Parameter '{param_name}' missing required 'type' field")
            
            param_type = config['type']
            if param_type not in valid_types:
                raise ValueError(f"Parameter '{param_name}' type must be one of {valid_types}")
            
            if 'bounds' not in config:
                raise ValueError(f"Parameter '{param_name}' missing required 'bounds' field")
            
            bounds = config['bounds']
            if param_type in ['continuous', 'discrete']:
                if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
                    raise ValueError(f"Parameter '{param_name}' bounds must be [min, max]")
                if not all(isinstance(b, (int, float)) for b in bounds):
                    raise ValueError(f"Parameter '{param_name}' bounds must be numeric")
                if bounds[0] >= bounds[1]:
                    raise ValueError(f"Parameter '{param_name}' min bound must be < max bound")
            elif param_type == 'categorical':
                if not isinstance(bounds, (list, tuple)) or len(bounds) < 2:
                    raise ValueError(f"Categorical parameter '{param_name}' must have at least 2 values")
    
    def _setup_bounds(self) -> None:
        """Setup normalized bounds and categorical mappings."""
        self.bounds = []
        self.categorical_mappings = {}
        self.reverse_categorical_mappings = {}
        
        for i, (name, config) in enumerate(self.params_config.items()):
            param_type = config["type"]
            
            if param_type in ["continuous", "discrete"]:
                bounds = config["bounds"]
                self.bounds.append([float(bounds[0]), float(bounds[1])])
            elif param_type == "categorical":
                values = config["bounds"]  # For categorical, bounds contains the values
                self.categorical_mappings[i] = {v: j for j, v in enumerate(values)}
                self.reverse_categorical_mappings[i] = {j: v for j, v in enumerate(values)}
                self.bounds.append([0.0, float(len(values) - 1)])
        
        self.bounds_array = np.array(self.bounds)
        logger.debug(f"Parameter bounds setup: {self.bounds}")
    
    def validate_parameter_dict(self, params_dict: Dict[str, Any]) -> bool:
        """
        Validate a parameter dictionary against the configuration.
        
        Args:
            params_dict: Dictionary of parameter values to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check all required parameters are present
            missing_params = set(self.param_names) - set(params_dict.keys())
            if missing_params:
                logger.warning(f"Missing parameters: {missing_params}")
                return False
            
            # Check each parameter value
            for param_name, value in params_dict.items():
                if param_name not in self.params_config:
                    logger.warning(f"Unknown parameter: {param_name}")
                    return False
                
                config = self.params_config[param_name]
                param_type = config["type"]
                bounds = config["bounds"]
                
                if param_type == "continuous":
                    if not isinstance(value, (int, float)):
                        logger.warning(f"Parameter '{param_name}' must be numeric, got {type(value)}")
                        return False
                    if not (bounds[0] <= value <= bounds[1]):
                        logger.warning(f"Parameter '{param_name}' value {value} outside bounds {bounds}")
                        return False
                
                elif param_type == "discrete":
                    if not isinstance(value, (int, float)):
                        logger.warning(f"Parameter '{param_name}' must be numeric, got {type(value)}")
                        return False
                    if not (bounds[0] <= value <= bounds[1]):
                        logger.warning(f"Parameter '{param_name}' value {value} outside bounds {bounds}")
                        return False
                
                elif param_type == "categorical":
                    if value not in bounds:
                        logger.warning(f"Parameter '{param_name}' value '{value}' not in allowed values {bounds}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating parameter dictionary: {e}")
            return False
    
    def params_to_normalized(self, params_dict: Dict[str, Any]) -> np.ndarray:
        """
        Convert parameter dictionary to normalized array [0, 1].
        
        Args:
            params_dict: Dictionary of parameter values
            
        Returns:
            np.ndarray: Normalized parameter values
        """
        try:
            normalized = np.zeros(self.n_params)
            
            for i, param_name in enumerate(self.param_names):
                if param_name not in params_dict:
                    logger.warning(f"Parameter '{param_name}' not found, using 0.0")
                    normalized[i] = 0.0
                    continue
                
                value = params_dict[param_name]
                config = self.params_config[param_name]
                param_type = config["type"]
                bounds = self.bounds[i]
                
                if param_type in ["continuous", "discrete"]:
                    # Normalize to [0, 1]
                    normalized[i] = (float(value) - bounds[0]) / (bounds[1] - bounds[0])
                elif param_type == "categorical":
                    # Map categorical to index, then normalize
                    if i in self.categorical_mappings and value in self.categorical_mappings[i]:
                        idx = self.categorical_mappings[i][value]
                        normalized[i] = idx / (bounds[1] - bounds[0]) if bounds[1] > bounds[0] else 0.0
                    else:
                        normalized[i] = 0.0
                
                # For screening with extrapolation, don't clamp - allow values outside [0,1]
                if not self.allow_extrapolation:
                    normalized[i] = np.clip(normalized[i], 0.0, 1.0)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error converting params to normalized: {e}")
            return np.zeros(self.n_params)
    
    def normalized_to_params(self, normalized: np.ndarray) -> Dict[str, Any]:
        """
        Convert normalized array back to parameter dictionary.
        
        Args:
            normalized: Normalized parameter values (can be outside [0,1] if extrapolation enabled)
            
        Returns:
            Dict[str, Any]: Parameter dictionary
        """
        try:
            # Only clip if extrapolation is disabled
            if not self.allow_extrapolation:
                normalized = np.clip(normalized, 0.0, 1.0)
            
            params_dict = {}
            
            # Update dynamic bounds based on actual values encountered
            self._update_dynamic_bounds(normalized)
            
            for i, param_name in enumerate(self.param_names):
                value = normalized[i]
                config = self.params_config[param_name]
                param_type = config["type"]
                bounds = self.bounds[i]
                
                if param_type == "continuous":
                    # Denormalize allowing extrapolation beyond original bounds
                    actual_value = bounds[0] + value * (bounds[1] - bounds[0])
                    # Apply precision if specified
                    if "precision" in config and config["precision"] is not None:
                        actual_value = round(actual_value, config["precision"])
                    params_dict[param_name] = actual_value
                
                elif param_type == "discrete":
                    # Denormalize and round to integer (allow extrapolation)
                    actual_value = int(round(bounds[0] + value * (bounds[1] - bounds[0])))
                    params_dict[param_name] = actual_value
                
                elif param_type == "categorical":
                    # Categorical parameters cannot extrapolate - constrain to valid values
                    values_list = config["bounds"]
                    idx = int(round(value * (len(values_list) - 1)))
                    idx = max(0, min(idx, len(values_list) - 1))  # Always constrain categorical
                    params_dict[param_name] = values_list[idx]
            
            return params_dict
            
        except Exception as e:
            logger.error(f"Error converting normalized to params: {e}")
            return {name: 0 for name in self.param_names}
    
    def _update_dynamic_bounds(self, normalized: np.ndarray) -> None:
        """
        Update dynamic bounds based on encountered parameter values.
        This allows the parameter space to expand during optimization.
        
        Args:
            normalized: Current normalized parameter values
        """
        if not self.allow_extrapolation:
            return
            
        for i, param_name in enumerate(self.param_names):
            config = self.params_config[param_name]
            if config["type"] not in ["continuous", "discrete"]:
                continue
                
            value = normalized[i]
            original_bounds = self.original_bounds[param_name]
            original_range = original_bounds[1] - original_bounds[0]
            
            # Calculate actual parameter value
            actual_value = original_bounds[0] + value * original_range
            
            # Update current bounds if needed
            if param_name not in self.current_bounds:
                self.current_bounds[param_name] = original_bounds.copy()
            
            current_min, current_max = self.current_bounds[param_name]
            
            # Expand bounds if actual value is outside current bounds
            if actual_value < current_min:
                self.current_bounds[param_name][0] = actual_value
                logger.info(f"Expanded {param_name} lower bound to {actual_value:.3f} (was {current_min:.3f})")
            elif actual_value > current_max:
                self.current_bounds[param_name][1] = actual_value
                logger.info(f"Expanded {param_name} upper bound to {actual_value:.3f} (was {current_max:.3f})")
    
    def get_exploration_summary(self) -> Dict[str, Any]:
        """
        Get summary of parameter space exploration including extrapolation.
        
        Returns:
            Dict containing exploration statistics
        """
        summary = {
            "original_bounds": self.original_bounds.copy(),
            "current_bounds": self.current_bounds.copy(),
            "extrapolation_enabled": self.allow_extrapolation,
            "expanded_parameters": []
        }
        
        for param_name in self.original_bounds:
            original = self.original_bounds[param_name]
            current = self.current_bounds.get(param_name, original)
            
            if current[0] < original[0] or current[1] > original[1]:
                expansion_info = {
                    "parameter": param_name,
                    "original_range": original,
                    "expanded_range": current,
                    "lower_expansion": max(0, original[0] - current[0]),
                    "upper_expansion": max(0, current[1] - original[1])
                }
                summary["expanded_parameters"].append(expansion_info)
        
        return summary
    
    def generate_latin_hypercube_samples(self, n_samples: int, seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate Latin Hypercube samples in the parameter space.
        
        Args:
            n_samples: Number of samples to generate
            seed: Random seed for reproducibility
            
        Returns:
            List[Dict[str, Any]]: List of parameter dictionaries
        """
        try:
            if seed is not None:
                np.random.seed(seed)
            
            # Generate LHS samples in normalized space
            sampler = qmc.LatinHypercube(d=self.n_params, seed=seed)
            lhs_samples = sampler.random(n=n_samples)
            
            # Convert to parameter dictionaries
            samples = []
            for i in range(n_samples):
                sample_normalized = lhs_samples[i]
                param_dict = self.normalized_to_params(sample_normalized)
                samples.append(param_dict)
            
            logger.info(f"Generated {len(samples)} Latin Hypercube samples")
            return samples
            
        except Exception as e:
            logger.error(f"Error generating Latin Hypercube samples: {e}")
            return []
    
    def generate_random_samples(self, n_samples: int, seed: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate random samples in the parameter space.
        
        Args:
            n_samples: Number of samples to generate
            seed: Random seed for reproducibility
            
        Returns:
            List[Dict[str, Any]]: List of parameter dictionaries
        """
        try:
            if seed is not None:
                np.random.seed(seed)
            
            samples = []
            for _ in range(n_samples):
                # Generate random values in [0, 1]
                random_normalized = np.random.random(self.n_params)
                param_dict = self.normalized_to_params(random_normalized)
                samples.append(param_dict)
            
            logger.info(f"Generated {len(samples)} random samples")
            return samples
            
        except Exception as e:
            logger.error(f"Error generating random samples: {e}")
            return []
    
    def calculate_parameter_distance(self, params1: Dict[str, Any], params2: Dict[str, Any]) -> float:
        """
        Calculate normalized Euclidean distance between two parameter sets.
        
        Args:
            params1, params2: Parameter dictionaries to compare
            
        Returns:
            float: Normalized distance [0, 1]
        """
        try:
            norm1 = self.params_to_normalized(params1)
            norm2 = self.params_to_normalized(params2)
            
            distance = np.linalg.norm(norm1 - norm2) / np.sqrt(self.n_params)
            return float(distance)
            
        except Exception as e:
            logger.error(f"Error calculating parameter distance: {e}")
            return 0.0
    
    def get_parameter_bounds_for_optimization(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get parameter bounds in format suitable for optimization algorithms.
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: Lower bounds, upper bounds
        """
        lower_bounds = np.array([bounds[0] for bounds in self.bounds])
        upper_bounds = np.array([bounds[1] for bounds in self.bounds])
        return lower_bounds, upper_bounds
    
    def get_parameter_info(self) -> pd.DataFrame:
        """
        Get summary information about all parameters.
        
        Returns:
            pd.DataFrame: Parameter information table
        """
        info_data = []
        
        for name, config in self.params_config.items():
            param_type = config["type"]
            bounds = config["bounds"]
            
            if param_type in ["continuous", "discrete"]:
                range_str = f"[{bounds[0]}, {bounds[1]}]"
            else:  # categorical
                range_str = f"{len(bounds)} values: {bounds[:3]}{'...' if len(bounds) > 3 else ''}"
            
            info_data.append({
                "Parameter": name,
                "Type": param_type,
                "Range": range_str,
                "Precision": config.get("precision", "N/A")
            })
        
        return pd.DataFrame(info_data)