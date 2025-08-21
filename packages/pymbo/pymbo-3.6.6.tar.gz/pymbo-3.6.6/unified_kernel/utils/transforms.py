"""
Parameter Transformation Utilities

Handles transformation between PyMBO parameter dictionaries and normalized
tensor representations for the Unified Exponential Kernel.
"""

import torch
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union
import logging

try:
    from .parameter_detection import ParameterTypeDetector
except ImportError:
    # Handle direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from parameter_detection import ParameterTypeDetector

logger = logging.getLogger(__name__)


class ParameterTransformer:
    """
    Transforms parameters between PyMBO format and normalized tensor format.
    
    Handles normalization and denormalization for all variable types while
    maintaining compatibility with PyMBO's parameter handling.
    """
    
    def __init__(self, params_config: Dict[str, Dict[str, Any]]):
        """
        Initialize transformer with parameter configuration.
        
        Args:
            params_config: PyMBO parameter configuration dictionary
        """
        self.detector = ParameterTypeDetector(params_config)
        self.params_config = params_config
        self.param_names = self.detector.param_names
        self.variable_info = self.detector.variable_info
        
        # Setup transformation mappings
        self._setup_bounds()
        self._setup_categorical_mappings()
        
        logger.debug(f"ParameterTransformer initialized for {self.detector.n_params} parameters")
    
    def _setup_bounds(self):
        """Setup bounds for normalization."""
        self.bounds = []
        
        for name, config in self.params_config.items():
            param_type = config['type']
            
            if param_type in ['continuous', 'discrete']:
                bounds = config['bounds']
                self.bounds.append([float(bounds[0]), float(bounds[1])])
            elif param_type == 'categorical':
                # For categorical, bounds represent index range
                values_key = 'bounds' if 'bounds' in config else 'values'
                values = config[values_key]
                self.bounds.append([0.0, float(len(values) - 1)])
        
        self.bounds_array = np.array(self.bounds)
    
    def _setup_categorical_mappings(self):
        """Setup categorical value mappings."""
        self.categorical_mappings = {}
        self.reverse_categorical_mappings = {}
        
        for i, (name, config) in enumerate(self.params_config.items()):
            if config['type'] == 'categorical':
                values_key = 'bounds' if 'bounds' in config else 'values'
                values = config[values_key]
                
                # Forward mapping: value -> index
                self.categorical_mappings[i] = {value: idx for idx, value in enumerate(values)}
                
                # Reverse mapping: index -> value
                self.reverse_categorical_mappings[i] = {idx: value for idx, value in enumerate(values)}
    
    def params_to_tensor(self, params_dict: Dict[str, Any], 
                        normalize: bool = True) -> torch.Tensor:
        """
        Convert parameter dictionary to tensor representation.
        
        Args:
            params_dict: Dictionary of parameter values
            normalize: Whether to normalize to [0, 1] range
        
        Returns:
            Parameter tensor of shape (n_params,)
        """
        try:
            values = np.zeros(self.detector.n_params)
            
            for i, param_name in enumerate(self.param_names):
                if param_name not in params_dict:
                    logger.warning(f"Parameter '{param_name}' not found in input, using 0.0")
                    values[i] = 0.0
                    continue
                
                value = params_dict[param_name]
                config = self.params_config[param_name]
                param_type = config['type']
                
                if param_type == 'continuous':
                    values[i] = float(value)
                    
                elif param_type == 'discrete':
                    values[i] = float(value)
                    
                elif param_type == 'categorical':
                    # Map categorical value to index
                    if i in self.categorical_mappings and value in self.categorical_mappings[i]:
                        values[i] = float(self.categorical_mappings[i][value])
                    else:
                        logger.warning(f"Unknown categorical value '{value}' for parameter '{param_name}', using 0")
                        values[i] = 0.0
                
                # Normalize if requested
                if normalize:
                    bounds = self.bounds[i]
                    range_val = bounds[1] - bounds[0]
                    if range_val > 0:
                        values[i] = (values[i] - bounds[0]) / range_val
                    else:
                        values[i] = 0.0
            
            return torch.tensor(values, dtype=torch.float64)
            
        except Exception as e:
            logger.error(f"Error converting params to tensor: {e}")
            return torch.zeros(self.detector.n_params, dtype=torch.float64)
    
    def tensor_to_params(self, tensor: torch.Tensor, 
                        denormalize: bool = True) -> Dict[str, Any]:
        """
        Convert tensor representation back to parameter dictionary.
        
        Args:
            tensor: Parameter tensor of shape (n_params,)
            denormalize: Whether to denormalize from [0, 1] range
        
        Returns:
            Dictionary of parameter values
        """
        try:
            if tensor.shape[0] != self.detector.n_params:
                raise ValueError(f"Expected tensor with {self.detector.n_params} elements, got {tensor.shape[0]}")
            
            values = tensor.detach().cpu().numpy()
            params_dict = {}
            
            for i, param_name in enumerate(self.param_names):
                value = values[i]
                config = self.params_config[param_name]
                param_type = config['type']
                
                # Denormalize if requested
                if denormalize:
                    bounds = self.bounds[i]
                    value = bounds[0] + value * (bounds[1] - bounds[0])
                
                if param_type == 'continuous':
                    # Apply precision if specified
                    if 'precision' in config and config['precision'] is not None:
                        value = round(value, config['precision'])
                    params_dict[param_name] = float(value)
                    
                elif param_type == 'discrete':
                    # Round to nearest integer and clamp to bounds
                    bounds = config['bounds'] if not denormalize else [bounds[0] for bounds in self.bounds_array[[i]]][0]
                    if denormalize:
                        bounds = config['bounds']
                    value = int(round(value))
                    value = max(bounds[0], min(bounds[1], value))
                    params_dict[param_name] = value
                    
                elif param_type == 'categorical':
                    # Map index back to categorical value
                    values_key = 'bounds' if 'bounds' in config else 'values'
                    valid_values = config[values_key]
                    
                    if denormalize:
                        # Value is in [0, len(values)-1] range
                        idx = int(round(value))
                    else:
                        # Value is already an index
                        idx = int(round(value))
                    
                    # Clamp to valid range
                    idx = max(0, min(len(valid_values) - 1, idx))
                    
                    if i in self.reverse_categorical_mappings and idx in self.reverse_categorical_mappings[i]:
                        params_dict[param_name] = self.reverse_categorical_mappings[i][idx]
                    else:
                        # Fallback to direct indexing
                        params_dict[param_name] = valid_values[idx]
            
            return params_dict
            
        except Exception as e:
            logger.error(f"Error converting tensor to params: {e}")
            return {name: 0 for name in self.param_names}
    
    def batch_params_to_tensor(self, params_list: List[Dict[str, Any]], 
                             normalize: bool = True) -> torch.Tensor:
        """
        Convert list of parameter dictionaries to batch tensor.
        
        Args:
            params_list: List of parameter dictionaries
            normalize: Whether to normalize to [0, 1] range
        
        Returns:
            Parameter tensor of shape (batch_size, n_params)
        """
        batch_tensors = []
        
        for params_dict in params_list:
            tensor = self.params_to_tensor(params_dict, normalize=normalize)
            batch_tensors.append(tensor)
        
        return torch.stack(batch_tensors, dim=0)
    
    def batch_tensor_to_params(self, tensor: torch.Tensor, 
                             denormalize: bool = True) -> List[Dict[str, Any]]:
        """
        Convert batch tensor to list of parameter dictionaries.
        
        Args:
            tensor: Parameter tensor of shape (batch_size, n_params)
            denormalize: Whether to denormalize from [0, 1] range
        
        Returns:
            List of parameter dictionaries
        """
        params_list = []
        
        for i in range(tensor.shape[0]):
            params_dict = self.tensor_to_params(tensor[i], denormalize=denormalize)
            params_list.append(params_dict)
        
        return params_list
    
    def normalize_tensor(self, tensor: torch.Tensor) -> torch.Tensor:
        """
        Normalize tensor values to [0, 1] range.
        
        Args:
            tensor: Unnormalized parameter tensor
        
        Returns:
            Normalized tensor
        """
        values = tensor.detach().cpu().numpy()
        normalized = np.zeros_like(values)
        
        for i in range(len(values)):
            bounds = self.bounds[i]
            range_val = bounds[1] - bounds[0]
            if range_val > 0:
                normalized[i] = (values[i] - bounds[0]) / range_val
            else:
                normalized[i] = 0.0
        
        return torch.tensor(normalized, dtype=tensor.dtype, device=tensor.device)
    
    def denormalize_tensor(self, tensor: torch.Tensor) -> torch.Tensor:
        """
        Denormalize tensor values from [0, 1] range.
        
        Args:
            tensor: Normalized parameter tensor
        
        Returns:
            Denormalized tensor
        """
        values = tensor.detach().cpu().numpy()
        denormalized = np.zeros_like(values)
        
        for i in range(len(values)):
            bounds = self.bounds[i]
            denormalized[i] = bounds[0] + values[i] * (bounds[1] - bounds[0])
        
        return torch.tensor(denormalized, dtype=tensor.dtype, device=tensor.device)
    
    def get_bounds_tensor(self, device: torch.device = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get parameter bounds as tensors.
        
        Args:
            device: Target device for tensors
        
        Returns:
            Tuple of (lower_bounds, upper_bounds) tensors
        """
        device = device or torch.device('cpu')
        
        lower_bounds = torch.tensor([bounds[0] for bounds in self.bounds], 
                                   dtype=torch.float64, device=device)
        upper_bounds = torch.tensor([bounds[1] for bounds in self.bounds], 
                                   dtype=torch.float64, device=device)
        
        return lower_bounds, upper_bounds
    
    def validate_tensor(self, tensor: torch.Tensor, normalized: bool = True) -> bool:
        """
        Validate that tensor values are within expected bounds.
        
        Args:
            tensor: Parameter tensor to validate
            normalized: Whether tensor is in normalized [0, 1] space
        
        Returns:
            True if valid, False otherwise
        """
        try:
            values = tensor.detach().cpu().numpy()
            
            if normalized:
                # Check [0, 1] bounds for normalized values
                return np.all((values >= -1e-6) & (values <= 1 + 1e-6))
            else:
                # Check parameter-specific bounds
                for i, value in enumerate(values):
                    bounds = self.bounds[i]
                    if not (bounds[0] - 1e-6 <= value <= bounds[1] + 1e-6):
                        return False
                return True
            
        except Exception as e:
            logger.error(f"Error validating tensor: {e}")
            return False
    
    def get_parameter_info(self) -> Dict[str, Any]:
        """
        Get information about parameter transformation setup.
        
        Returns:
            Dictionary with transformation information
        """
        return {
            'param_names': self.param_names,
            'bounds': self.bounds,
            'categorical_mappings': self.categorical_mappings,
            'variable_info': self.variable_info,
            'n_parameters': self.detector.n_params
        }