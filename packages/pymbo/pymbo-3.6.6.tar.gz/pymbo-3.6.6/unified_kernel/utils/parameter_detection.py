"""
Parameter Type Detection and Validation

Automatically detects parameter types from PyMBO configuration and validates
parameter spaces for the Unified Exponential Kernel.
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


def is_mixed_variable_problem(params_config: Dict[str, Dict[str, Any]]) -> bool:
    """
    Check if the parameter configuration contains mixed variable types.
    
    Args:
        params_config: PyMBO parameter configuration
        
    Returns:
        True if problem has mixed variable types (not all continuous)
    """
    if not params_config:
        return False
        
    types = set()
    for param_name, param_info in params_config.items():
        param_type = param_info.get('type', 'continuous')
        types.add(param_type)
    
    # Mixed if more than one type OR any non-continuous type
    return len(types) > 1 or 'continuous' not in types or len(types.difference({'continuous'})) > 0


def get_variable_type_summary(params_config: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get summary of variable types in parameter configuration.
    
    Args:
        params_config: PyMBO parameter configuration
        
    Returns:
        Dictionary with type counts and other summary info
    """
    if not params_config:
        return {'type_counts': {'continuous': 0, 'discrete': 0, 'categorical': 0}}
    
    type_counts = {'continuous': 0, 'discrete': 0, 'categorical': 0}
    
    for param_name, param_info in params_config.items():
        param_type = param_info.get('type', 'continuous')
        if param_type in type_counts:
            type_counts[param_type] += 1
    
    return {
        'type_counts': type_counts,
        'total_params': len(params_config),
        'is_mixed': is_mixed_variable_problem(params_config)
    }


class ParameterTypeDetector:
    """
    Detects and validates parameter types from PyMBO configuration format.
    
    Supports three variable types:
    - continuous: Real-valued parameters with bounds
    - discrete: Integer-valued parameters with bounds  
    - categorical: Discrete choice parameters with string/numeric values
    """
    
    def __init__(self, params_config: Dict[str, Dict[str, Any]]):
        """
        Initialize detector with PyMBO parameter configuration.
        
        Args:
            params_config: PyMBO format parameter configuration
                          e.g., {"temp": {"type": "continuous", "bounds": [0, 100]}}
        """
        self.params_config = params_config
        self.param_names = list(params_config.keys())
        self.n_params = len(self.param_names)
        
        # Validate configuration
        self._validate_config()
        
        # Detect variable types and organize indices
        self.variable_info = self._analyze_variable_types()
        
        logger.info(f"Detected {self.n_params} parameters: "
                   f"{self.variable_info['n_continuous']} continuous, "
                   f"{self.variable_info['n_discrete']} discrete, "
                   f"{self.variable_info['n_categorical']} categorical")
    
    def _validate_config(self) -> None:
        """Validate parameter configuration for completeness and correctness."""
        if not isinstance(self.params_config, dict) or not self.params_config:
            raise ValueError("params_config must be a non-empty dictionary")
        
        valid_types = ['continuous', 'discrete', 'categorical']
        
        for param_name, config in self.params_config.items():
            if not isinstance(config, dict):
                raise ValueError(f"Parameter '{param_name}' config must be a dictionary")
            
            # Check required fields
            if 'type' not in config:
                raise ValueError(f"Parameter '{param_name}' missing required 'type' field")
            
            param_type = config['type']
            if param_type not in valid_types:
                raise ValueError(f"Parameter '{param_name}' type must be one of {valid_types}")
            
            # Validate bounds/values based on type
            if param_type in ['continuous', 'discrete']:
                if 'bounds' not in config:
                    raise ValueError(f"Parameter '{param_name}' missing required 'bounds' field")
                
                bounds = config['bounds']
                if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
                    raise ValueError(f"Parameter '{param_name}' bounds must be [min, max]")
                
                if not all(isinstance(b, (int, float)) for b in bounds):
                    raise ValueError(f"Parameter '{param_name}' bounds must be numeric")
                
                if bounds[0] >= bounds[1]:
                    raise ValueError(f"Parameter '{param_name}' min bound must be < max bound")
            
            elif param_type == 'categorical':
                # Check for both 'bounds' and 'values' (PyMBO format compatibility)
                if 'values' in config:
                    values_key = 'values'
                elif 'bounds' in config:
                    values_key = 'bounds'
                else:
                    raise ValueError(f"Categorical parameter '{param_name}' missing 'values' or 'bounds'")
                
                values = config[values_key]
                if not isinstance(values, (list, tuple)) or len(values) < 2:
                    raise ValueError(f"Categorical parameter '{param_name}' must have at least 2 values")
    
    def _analyze_variable_types(self) -> Dict[str, Any]:
        """
        Analyze parameter configuration and organize by variable type.
        
        Returns:
            Dictionary with variable type information and indices
        """
        continuous_indices = []
        discrete_indices = []
        categorical_indices = []
        
        continuous_params = []
        discrete_params = []
        categorical_params = []
        
        for i, (param_name, config) in enumerate(self.params_config.items()):
            param_type = config['type']
            
            if param_type == 'continuous':
                continuous_indices.append(i)
                continuous_params.append(param_name)
            elif param_type == 'discrete':
                discrete_indices.append(i)
                discrete_params.append(param_name)
            elif param_type == 'categorical':
                categorical_indices.append(i)
                categorical_params.append(param_name)
        
        return {
            'continuous_indices': continuous_indices,
            'discrete_indices': discrete_indices,
            'categorical_indices': categorical_indices,
            'continuous_params': continuous_params,
            'discrete_params': discrete_params,
            'categorical_params': categorical_params,
            'n_continuous': len(continuous_indices),
            'n_discrete': len(discrete_indices),
            'n_categorical': len(categorical_indices),
            'has_continuous': len(continuous_indices) > 0,
            'has_discrete': len(discrete_indices) > 0,
            'has_categorical': len(categorical_indices) > 0,
            'is_mixed': (len(continuous_indices) > 0) + (len(discrete_indices) > 0) + (len(categorical_indices) > 0) > 1
        }
    
    def get_variable_type_map(self) -> Dict[int, str]:
        """
        Get mapping from parameter index to variable type.
        
        Returns:
            Dict mapping parameter index to type string
        """
        type_map = {}
        for i, (param_name, config) in enumerate(self.params_config.items()):
            type_map[i] = config['type']
        return type_map
    
    def get_bounds_by_type(self) -> Dict[str, List[Tuple[float, float]]]:
        """
        Get parameter bounds organized by variable type.
        
        Returns:
            Dictionary with bounds for each variable type
        """
        bounds = {
            'continuous': [],
            'discrete': [],
            'categorical': []
        }
        
        for param_name, config in self.params_config.items():
            param_type = config['type']
            
            if param_type in ['continuous', 'discrete']:
                param_bounds = config['bounds']
                bounds[param_type].append((float(param_bounds[0]), float(param_bounds[1])))
            elif param_type == 'categorical':
                # For categorical, get values using flexible key
                if 'values' in config:
                    values_key = 'values'
                elif 'bounds' in config:
                    values_key = 'bounds'
                else:
                    values_key = 'values'  # Default fallback
                values = config[values_key]
                bounds[param_type].append((0.0, float(len(values) - 1)))
        
        return bounds
    
    def get_categorical_mappings(self) -> Dict[int, Dict[Any, int]]:
        """
        Get categorical value mappings for categorical parameters.
        
        Returns:
            Dict mapping parameter index to value->index mapping
        """
        mappings = {}
        
        for i, (param_name, config) in enumerate(self.params_config.items()):
            if config['type'] == 'categorical':
                if 'values' in config:
                    values_key = 'values'
                elif 'bounds' in config:
                    values_key = 'bounds'
                else:
                    values_key = 'values'
                values = config[values_key]
                mappings[i] = {value: idx for idx, value in enumerate(values)}
        
        return mappings
    
    def split_tensor_by_type(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Split parameter tensor into continuous, discrete, and categorical parts.
        
        Args:
            X: Parameter tensor of shape (n_samples, n_params)
        
        Returns:
            Tuple of (continuous_X, discrete_X, categorical_X)
        """
        if X.shape[1] != self.n_params:
            raise ValueError(f"Expected {self.n_params} parameters, got {X.shape[1]}")
        
        continuous_X = X[:, self.variable_info['continuous_indices']] if self.variable_info['continuous_indices'] else np.empty((X.shape[0], 0))
        discrete_X = X[:, self.variable_info['discrete_indices']] if self.variable_info['discrete_indices'] else np.empty((X.shape[0], 0))
        categorical_X = X[:, self.variable_info['categorical_indices']] if self.variable_info['categorical_indices'] else np.empty((X.shape[0], 0))
        
        return continuous_X, discrete_X, categorical_X
    
    def validate_parameter_values(self, param_dict: Dict[str, Any]) -> bool:
        """
        Validate parameter values against configuration.
        
        Args:
            param_dict: Dictionary of parameter values
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check all parameters are present
            missing = set(self.param_names) - set(param_dict.keys())
            if missing:
                logger.warning(f"Missing parameters: {missing}")
                return False
            
            # Validate each parameter
            for param_name, value in param_dict.items():
                if param_name not in self.params_config:
                    logger.warning(f"Unknown parameter: {param_name}")
                    return False
                
                config = self.params_config[param_name]
                param_type = config['type']
                
                if param_type == 'continuous':
                    if not isinstance(value, (int, float)):
                        logger.warning(f"Parameter '{param_name}' must be numeric")
                        return False
                    bounds = config['bounds']
                    if not (bounds[0] <= value <= bounds[1]):
                        logger.warning(f"Parameter '{param_name}' value {value} outside bounds {bounds}")
                        return False
                
                elif param_type == 'discrete':
                    if not isinstance(value, (int, float)):
                        logger.warning(f"Parameter '{param_name}' must be numeric")
                        return False
                    bounds = config['bounds']
                    if not (bounds[0] <= value <= bounds[1]):
                        logger.warning(f"Parameter '{param_name}' value {value} outside bounds {bounds}")
                        return False
                
                elif param_type == 'categorical':
                    if 'values' in config:
                        values_key = 'values'
                    elif 'bounds' in config:
                        values_key = 'bounds'
                    else:
                        values_key = 'values'
                    valid_values = config[values_key]
                    if value not in valid_values:
                        logger.warning(f"Parameter '{param_name}' value '{value}' not in {valid_values}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating parameters: {e}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of parameter type detection results.
        
        Returns:
            Summary dictionary with parameter type information
        """
        return {
            'total_parameters': self.n_params,
            'parameter_names': self.param_names,
            'variable_types': {name: config['type'] for name, config in self.params_config.items()},
            'type_counts': {
                'continuous': self.variable_info['n_continuous'],
                'discrete': self.variable_info['n_discrete'],
                'categorical': self.variable_info['n_categorical']
            },
            'is_mixed_variable': self.variable_info['is_mixed'],
            'type_indices': {
                'continuous': self.variable_info['continuous_indices'],
                'discrete': self.variable_info['discrete_indices'],
                'categorical': self.variable_info['categorical_indices']
            }
        }