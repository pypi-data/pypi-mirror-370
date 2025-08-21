"""
Unified Exponential Kernel for Mixed Variables

A GPyTorch-compatible kernel implementation that handles continuous, discrete, 
and categorical variables using a unified exponential formulation.

Mathematical formulation:
k(x, x') = σ² * exp(-Σ w_j * d_j(x_j, x'_j))

where d_j(x_j, x'_j) is the appropriate distance function for variable type j.
"""

import torch
import gpytorch
from typing import Dict, List, Any, Optional, Tuple
import logging
import warnings

try:
    from ..utils.parameter_detection import ParameterTypeDetector
    from .distance_functions import UnifiedDistanceComputer
except ImportError:
    # Handle direct execution - adjust path properly
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    from utils.parameter_detection import ParameterTypeDetector
    sys.path.insert(0, current_dir)
    from distance_functions import UnifiedDistanceComputer

logger = logging.getLogger(__name__)


class UnifiedExponentialKernel(gpytorch.kernels.Kernel):
    """
    Unified Exponential Kernel for mixed variable types (continuous, discrete, categorical).
    
    This kernel extends the exponential kernel formulation to handle mixed variable types
    in a principled way, providing a drop-in replacement for standard kernels in PyMBO
    while properly handling categorical and discrete variables.
    
    The kernel computes:
    k(x, x') = σ² * exp(-Σ w_j * d_j(x_j, x'_j))
    
    where:
    - σ² is the output variance (handled by ScaleKernel wrapper)
    - w_j are learnable weights for each parameter
    - d_j(x_j, x'_j) is the distance function for parameter j based on its type:
      * Continuous: (x_j - x'_j)² / ℓ_j²
      * Discrete: |x_j - x'_j| / ℓ_j
      * Categorical: 0 if same, θ_j if different
    """
    
    has_lengthscale = True
    
    def __init__(self, params_config: Dict[str, Dict[str, Any]], 
                 ard_num_dims: Optional[int] = None,
                 eps: float = 1e-6,
                 **kwargs):
        """
        Initialize Unified Exponential Kernel.
        
        Args:
            params_config: PyMBO parameter configuration dictionary
            ard_num_dims: Number of dimensions (should match total parameters)
            eps: Small value to prevent numerical issues
            **kwargs: Additional arguments passed to parent kernel
        """
        # Detect parameter types
        self.detector = ParameterTypeDetector(params_config)
        self.params_config = params_config
        self.variable_info = self.detector.variable_info
        
        # Validate dimensions
        total_dims = self.detector.n_params
        if ard_num_dims is not None and ard_num_dims != total_dims:
            warnings.warn(f"ard_num_dims ({ard_num_dims}) doesn't match detected parameters ({total_dims}). "
                         f"Using {total_dims}.")
        
        # Initialize parent with correct dimensions
        super().__init__(ard_num_dims=total_dims, **kwargs)
        
        self.eps = eps
        
        # Initialize distance computer
        self.distance_computer = UnifiedDistanceComputer(
            self.variable_info, 
            device=self.device if hasattr(self, 'device') else torch.device('cpu')
        )
        
        # Register hyperparameters
        self._register_hyperparameters()
        
        logger.info(f"UnifiedExponentialKernel initialized with {total_dims} parameters: "
                   f"{self.variable_info['n_continuous']} continuous, "
                   f"{self.variable_info['n_discrete']} discrete, "
                   f"{self.variable_info['n_categorical']} categorical")
    
    def _register_hyperparameters(self):
        """Register learnable hyperparameters for the kernel."""
        total_dims = self.detector.n_params
        
        # Weights for each parameter (initialize to 1.0)
        self.register_parameter(
            name="raw_weights",
            parameter=torch.nn.Parameter(torch.ones(total_dims))
        )
        
        # Lengthscales for continuous variables
        if self.variable_info['n_continuous'] > 0:
            self.register_parameter(
                name="raw_continuous_lengthscales",
                parameter=torch.nn.Parameter(torch.ones(self.variable_info['n_continuous']))
            )
        
        # Lengthscales for discrete variables
        if self.variable_info['n_discrete'] > 0:
            self.register_parameter(
                name="raw_discrete_lengthscales", 
                parameter=torch.nn.Parameter(torch.ones(self.variable_info['n_discrete']))
            )
        
        # Theta parameters for categorical variables
        if self.variable_info['n_categorical'] > 0:
            self.register_parameter(
                name="raw_categorical_theta",
                parameter=torch.nn.Parameter(torch.ones(self.variable_info['n_categorical']))
            )
        
        # Register a lengthscale property for compatibility with PyMBO plotting
        # This combines all lengthscale-like parameters into one tensor
        self._create_combined_lengthscale()
    
    def _create_combined_lengthscale(self):
        """Create combined lengthscale property for PyMBO compatibility."""
        # This property will be dynamically computed in the lengthscale property
        pass
    
    @property
    def weights(self) -> torch.Tensor:
        """Get positive weights using softplus transformation."""
        return torch.nn.functional.softplus(self.raw_weights) + self.eps
    
    @property
    def continuous_lengthscales(self) -> Optional[torch.Tensor]:
        """Get positive continuous lengthscales using softplus transformation."""
        if self.variable_info['n_continuous'] > 0:
            return torch.nn.functional.softplus(self.raw_continuous_lengthscales) + self.eps
        return None
    
    @property
    def discrete_lengthscales(self) -> Optional[torch.Tensor]:
        """Get positive discrete lengthscales using softplus transformation."""
        if self.variable_info['n_discrete'] > 0:
            return torch.nn.functional.softplus(self.raw_discrete_lengthscales) + self.eps
        return None
    
    @property
    def categorical_theta(self) -> Optional[torch.Tensor]:
        """Get positive categorical theta parameters using softplus transformation."""
        if self.variable_info['n_categorical'] > 0:
            return torch.nn.functional.softplus(self.raw_categorical_theta) + self.eps
        return None
    
    @property
    def lengthscale(self) -> torch.Tensor:
        """
        Combined lengthscale property for PyMBO compatibility.
        
        Returns a tensor with effective lengthscales for all parameters,
        allowing PyMBO's plotting and analysis code to work unchanged.
        """
        combined_lengthscales = []
        
        # Add continuous lengthscales
        if self.continuous_lengthscales is not None:
            combined_lengthscales.extend(self.continuous_lengthscales.tolist())
        
        # Add discrete lengthscales
        if self.discrete_lengthscales is not None:
            combined_lengthscales.extend(self.discrete_lengthscales.tolist())
        
        # Add effective lengthscales for categorical variables
        if self.categorical_theta is not None:
            # Convert theta to effective lengthscale: larger theta means smaller effective lengthscale
            effective_cat_lengthscales = 1.0 / (self.categorical_theta + self.eps)
            combined_lengthscales.extend(effective_cat_lengthscales.tolist())
        
        return torch.tensor(combined_lengthscales, device=self.raw_weights.device)
    
    def forward(self, x1: torch.Tensor, x2: torch.Tensor, diag: bool = False, **params) -> torch.Tensor:
        """
        Forward pass of the kernel.
        
        Args:
            x1: First input tensor (n1, d) or (batch_size, n1, d)
            x2: Second input tensor (n2, d) or (batch_size, n2, d)
            diag: If True, return only diagonal elements
            **params: Additional parameters
        
        Returns:
            Covariance tensor (n1, n2) or (n1,) if diag=True
            For batched inputs: (batch_size, n1, n2) or (batch_size, n1) if diag=True
        """
        original_batch_shape = None
        
        # Handle batched inputs (common in BoTorch/GPyTorch with qNEHVI)
        if x1.dim() == 3 and x2.dim() == 3:
            # Batched inputs: (batch_size, n_points, n_features)
            batch_size_1, n_points_1, n_features = x1.shape
            batch_size_2, n_points_2, _ = x2.shape
            
            # Store original batch shape for output reconstruction
            original_batch_shape = (batch_size_1, n_points_1, n_points_2)
            
            if batch_size_1 == batch_size_2:
                if batch_size_1 == 1:
                    # Single batch - squeeze out batch dimension
                    x1 = x1.squeeze(0)  # (n_points, n_features)
                    x2 = x2.squeeze(0)  # (n_points, n_features)
                    logger.debug(f"Single batch inputs: x1 {batch_size_1,n_points_1,n_features} -> {x1.shape}, x2 {batch_size_2,n_points_2,n_features} -> {x2.shape}")
                else:
                    # Multi-batch case: process batch by batch
                    batch_results = []
                    for b in range(batch_size_1):
                        x1_batch = x1[b]  # (n_points_1, n_features)
                        x2_batch = x2[b]  # (n_points_2, n_features)
                        batch_result = self._compute_covariance_2d(x1_batch, x2_batch, diag)
                        batch_results.append(batch_result)
                    
                    # Stack results back into batch dimension
                    result = torch.stack(batch_results, dim=0)
                    logger.debug(f"Multi-batch computation: {batch_size_1} batches -> {result.shape}")
                    return result
            else:
                raise ValueError(f"Batch size mismatch: x1.shape={x1.shape}, x2.shape={x2.shape}")
                
        elif x1.dim() == 1:
            x1 = x1.unsqueeze(0)
        elif x2.dim() == 1:
            x2 = x2.unsqueeze(0)
        elif x1.dim() != 2 or x2.dim() != 2:
            raise ValueError(f"Unsupported tensor dimensions: x1.shape={x1.shape}, x2.shape={x2.shape}")
        
        # Compute covariance for 2D tensors
        result = self._compute_covariance_2d(x1, x2, diag)
        
        # Reconstruct batch dimension if needed
        if original_batch_shape is not None and original_batch_shape[0] == 1:
            if diag:
                result = result.unsqueeze(0)  # (1, n_points)
            else:
                result = result.unsqueeze(0)  # (1, n_points_1, n_points_2)
            logger.debug(f"Reconstructed batch dimension: {result.shape}")
        
        return result
    
    def _compute_covariance_2d(self, x1: torch.Tensor, x2: torch.Tensor, diag: bool = False) -> torch.Tensor:
        """
        Compute covariance for 2D input tensors.
        
        Args:
            x1: First input tensor (n1, d)
            x2: Second input tensor (n2, d)
            diag: If True, return only diagonal elements
        
        Returns:
            Covariance tensor (n1, n2) or (n1,) if diag=True
        """
        if x1.shape[1] != x2.shape[1]:
            raise ValueError("x1 and x2 must have the same number of features")
        
        if x1.shape[1] != self.detector.n_params:
            raise ValueError(f"Expected {self.detector.n_params} features, got {x1.shape[1]}")
        
        # Ensure tensors are on the correct device
        device = self.raw_weights.device
        x1 = x1.to(device)
        x2 = x2.to(device)
        
        if diag:
            # For diagonal computation, x1 and x2 should have the same number of points
            if x1.shape[0] != x2.shape[0]:
                raise ValueError("For diagonal computation, x1 and x2 must have the same number of points")
            
            # Compute distances only for diagonal elements
            distances = self._compute_diagonal_distances(x1, x2)
        else:
            # Compute full distance matrix
            distances = self.distance_computer.compute_distance(
                x1, x2,
                self.weights,
                self.continuous_lengthscales,
                self.discrete_lengthscales,
                self.categorical_theta
            )
        
        # Apply exponential to get covariance
        covariance = torch.exp(-distances)
        
        return covariance
    
    def _compute_diagonal_distances(self, x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """
        Compute distances for diagonal elements only (more efficient for diag=True).
        
        Args:
            x1: First input tensor (n, d)
            x2: Second input tensor (n, d)
        
        Returns:
            Distance tensor (n,)
        """
        n_points = x1.shape[0]
        device = x1.device
        
        total_distance = torch.zeros(n_points, device=device)
        
        # Continuous variables
        if self.variable_info['n_continuous'] > 0:
            cont_indices = self.variable_info['continuous_indices']
            x1_cont = x1[:, cont_indices]
            x2_cont = x2[:, cont_indices]
            weights_cont = self.weights[cont_indices]
            lengthscales_cont = self.continuous_lengthscales
            
            # Element-wise squared difference
            diff_cont = (x1_cont - x2_cont) / lengthscales_cont
            weighted_dist_cont = weights_cont * (diff_cont ** 2)
            total_distance += weighted_dist_cont.sum(dim=1)
        
        # Discrete variables
        if self.variable_info['n_discrete'] > 0:
            disc_indices = self.variable_info['discrete_indices']
            x1_disc = x1[:, disc_indices]
            x2_disc = x2[:, disc_indices]
            weights_disc = self.weights[disc_indices]
            lengthscales_disc = self.discrete_lengthscales
            
            # Element-wise absolute difference
            diff_disc = torch.abs(x1_disc - x2_disc) / lengthscales_disc
            weighted_dist_disc = weights_disc * diff_disc
            total_distance += weighted_dist_disc.sum(dim=1)
        
        # Categorical variables
        if self.variable_info['n_categorical'] > 0:
            cat_indices = self.variable_info['categorical_indices']
            x1_cat = x1[:, cat_indices]
            x2_cat = x2[:, cat_indices]
            weights_cat = self.weights[cat_indices]
            theta_cat = self.categorical_theta
            
            # Element-wise inequality
            different_cat = (x1_cat != x2_cat).float()
            weighted_dist_cat = weights_cat * theta_cat * different_cat
            total_distance += weighted_dist_cat.sum(dim=1)
        
        return total_distance
    
    def num_outputs_per_input(self, x1: torch.Tensor, x2: torch.Tensor) -> int:
        """Return number of outputs per input (always 1 for covariance kernels)."""
        return 1
    
    
    def get_hyperparameter_summary(self) -> Dict[str, Any]:
        """
        Get summary of current hyperparameter values.
        
        Returns:
            Dictionary with hyperparameter information
        """
        summary = {
            'weights': self.weights.detach().cpu().numpy().tolist(),
            'total_parameters': self.detector.n_params,
            'variable_info': self.variable_info
        }
        
        if self.continuous_lengthscales is not None:
            summary['continuous_lengthscales'] = self.continuous_lengthscales.detach().cpu().numpy().tolist()
        
        if self.discrete_lengthscales is not None:
            summary['discrete_lengthscales'] = self.discrete_lengthscales.detach().cpu().numpy().tolist()
        
        if self.categorical_theta is not None:
            summary['categorical_theta'] = self.categorical_theta.detach().cpu().numpy().tolist()
        
        summary['combined_lengthscale'] = self.lengthscale.detach().cpu().numpy().tolist()
        
        return summary
    
    def analyze_parameter_importance(self) -> Dict[str, float]:
        """
        Analyze parameter importance based on kernel hyperparameters.
        
        Returns:
            Dictionary mapping parameter names to importance scores
        """
        weights = self.weights.detach().cpu().numpy()
        combined_lengthscales = self.lengthscale.detach().cpu().numpy()
        
        # Importance is inversely related to effective lengthscale, weighted by parameter weight
        importance_scores = weights / (combined_lengthscales + self.eps)
        
        # Normalize to sum to 1
        importance_scores = importance_scores / importance_scores.sum()
        
        return {name: float(score) for name, score in zip(self.detector.param_names, importance_scores)}
    
    def __repr__(self) -> str:
        return (f"UnifiedExponentialKernel("
                f"params={self.detector.n_params}, "
                f"continuous={self.variable_info['n_continuous']}, "
                f"discrete={self.variable_info['n_discrete']}, "
                f"categorical={self.variable_info['n_categorical']})")


# Compatibility functions for integration with PyMBO

def create_unified_kernel_from_config(params_config: Dict[str, Dict[str, Any]], 
                                    ard_num_dims: Optional[int] = None) -> UnifiedExponentialKernel:
    """
    Factory function to create UnifiedExponentialKernel from PyMBO config.
    
    Args:
        params_config: PyMBO parameter configuration
        ard_num_dims: Number of dimensions (auto-detected if None)
    
    Returns:
        Configured UnifiedExponentialKernel instance
    """
    return UnifiedExponentialKernel(params_config, ard_num_dims=ard_num_dims)


def is_mixed_variable_problem(params_config: Dict[str, Dict[str, Any]]) -> bool:
    """
    Check if parameter configuration represents a mixed variable problem.
    
    Args:
        params_config: PyMBO parameter configuration
    
    Returns:
        True if problem has multiple variable types
    """
    detector = ParameterTypeDetector(params_config)
    return detector.variable_info['is_mixed']


def get_variable_type_summary(params_config: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get summary of variable types in parameter configuration.
    
    Args:
        params_config: PyMBO parameter configuration
    
    Returns:
        Summary of variable types and counts
    """
    detector = ParameterTypeDetector(params_config)
    return detector.get_summary()