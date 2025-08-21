"""
Distance Functions for Mixed Variable Types

Implementation of distance functions for continuous, discrete, and categorical
variables used in the Unified Exponential Kernel.

Mathematical formulation:
- Continuous: d_cont(x, x') = (x - x')² / ℓ²
- Discrete: d_disc(x, x') = |x - x'| / ℓ  
- Categorical: d_cat(x, x') = 0 if same, θ if different
"""

import torch
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DistanceFunctions:
    """
    Collection of distance functions for different variable types in the
    Unified Exponential Kernel.
    """
    
    @staticmethod
    def continuous_distance(x1: torch.Tensor, x2: torch.Tensor, 
                          lengthscales: torch.Tensor) -> torch.Tensor:
        """
        Compute squared exponential distance for continuous variables.
        
        Formula: d_cont(x, x') = (x - x')² / ℓ²
        
        Args:
            x1: First set of continuous variables (n1, d_cont)
            x2: Second set of continuous variables (n2, d_cont)
            lengthscales: Lengthscale parameters (d_cont,)
        
        Returns:
            Distance tensor (n1, n2)
        """
        if x1.shape[1] != x2.shape[1]:
            raise ValueError("x1 and x2 must have same number of continuous dimensions")
        
        if x1.shape[1] != lengthscales.shape[0]:
            raise ValueError("Number of lengthscales must match number of continuous dimensions")
        
        # Ensure lengthscales are positive
        lengthscales = torch.clamp(lengthscales, min=1e-6)
        
        # Compute pairwise squared differences
        # x1: (n1, 1, d_cont), x2: (1, n2, d_cont) -> (n1, n2, d_cont)
        diff = x1.unsqueeze(1) - x2.unsqueeze(0)
        
        # Scale by lengthscales and square
        scaled_diff = diff / lengthscales.unsqueeze(0).unsqueeze(0)
        squared_scaled_diff = scaled_diff ** 2
        
        # Sum over continuous dimensions
        distance = squared_scaled_diff.sum(dim=-1)
        
        return distance
    
    @staticmethod
    def discrete_distance(x1: torch.Tensor, x2: torch.Tensor,
                         lengthscales: torch.Tensor) -> torch.Tensor:
        """
        Compute L1 distance for discrete variables.
        
        Formula: d_disc(x, x') = |x - x'| / ℓ
        
        Args:
            x1: First set of discrete variables (n1, d_disc)
            x2: Second set of discrete variables (n2, d_disc)
            lengthscales: Lengthscale parameters (d_disc,)
        
        Returns:
            Distance tensor (n1, n2)
        """
        if x1.shape[1] != x2.shape[1]:
            raise ValueError("x1 and x2 must have same number of discrete dimensions")
        
        if x1.shape[1] != lengthscales.shape[0]:
            raise ValueError("Number of lengthscales must match number of discrete dimensions")
        
        # Ensure lengthscales are positive
        lengthscales = torch.clamp(lengthscales, min=1e-6)
        
        # Compute pairwise absolute differences
        # x1: (n1, 1, d_disc), x2: (1, n2, d_disc) -> (n1, n2, d_disc)
        diff = x1.unsqueeze(1) - x2.unsqueeze(0)
        abs_diff = torch.abs(diff)
        
        # Scale by lengthscales
        scaled_diff = abs_diff / lengthscales.unsqueeze(0).unsqueeze(0)
        
        # Sum over discrete dimensions
        distance = scaled_diff.sum(dim=-1)
        
        return distance
    
    @staticmethod
    def categorical_distance(x1: torch.Tensor, x2: torch.Tensor,
                           theta: torch.Tensor) -> torch.Tensor:
        """
        Compute binary distance for categorical variables.
        
        Formula: d_cat(x, x') = 0 if same, θ if different
        
        Args:
            x1: First set of categorical variables (n1, d_cat)
            x2: Second set of categorical variables (n2, d_cat)
            theta: Dissimilarity parameters (d_cat,)
        
        Returns:
            Distance tensor (n1, n2)
        """
        if x1.shape[1] != x2.shape[1]:
            raise ValueError("x1 and x2 must have same number of categorical dimensions")
        
        if x1.shape[1] != theta.shape[0]:
            raise ValueError("Number of theta parameters must match number of categorical dimensions")
        
        # Ensure theta parameters are positive
        theta = torch.clamp(theta, min=1e-6)
        
        # Compute pairwise equality
        # x1: (n1, 1, d_cat), x2: (1, n2, d_cat) -> (n1, n2, d_cat)
        equal = (x1.unsqueeze(1) == x2.unsqueeze(0)).float()
        
        # Apply theta for different categories (1 - equal gives 1 for different, 0 for same)
        different = 1.0 - equal
        weighted_different = different * theta.unsqueeze(0).unsqueeze(0)
        
        # Sum over categorical dimensions
        distance = weighted_different.sum(dim=-1)
        
        return distance
    
    @staticmethod
    def hamming_distance(x1: torch.Tensor, x2: torch.Tensor) -> torch.Tensor:
        """
        Compute standard Hamming distance for categorical variables.
        
        Formula: d_hamming(x, x') = (1/d) * Σ I(x_i ≠ x'_i)
        
        Args:
            x1: First set of categorical variables (n1, d_cat)
            x2: Second set of categorical variables (n2, d_cat)
        
        Returns:
            Distance tensor (n1, n2) with values in [0, 1]
        """
        if x1.shape[1] != x2.shape[1]:
            raise ValueError("x1 and x2 must have same number of categorical dimensions")
        
        if x1.shape[1] == 0:
            return torch.zeros(x1.shape[0], x2.shape[0])
        
        # Compute pairwise inequality
        # x1: (n1, 1, d_cat), x2: (1, n2, d_cat) -> (n1, n2, d_cat)
        different = (x1.unsqueeze(1) != x2.unsqueeze(0)).float()
        
        # Average over categorical dimensions
        hamming_dist = different.mean(dim=-1)
        
        return hamming_dist


class UnifiedDistanceComputer:
    """
    Computes unified distance for mixed variable types in the Unified Exponential Kernel.
    
    Formula: d_total(x, x') = Σ w_j * d_j(x_j, x'_j)
    where d_j is the appropriate distance function for variable type j.
    """
    
    def __init__(self, variable_indices: dict, device: torch.device = None):
        """
        Initialize distance computer with variable type information.
        
        Args:
            variable_indices: Dictionary with 'continuous_indices', 'discrete_indices', 
                            'categorical_indices' lists
            device: Torch device for computations
        """
        self.continuous_indices = variable_indices.get('continuous_indices', [])
        self.discrete_indices = variable_indices.get('discrete_indices', [])
        self.categorical_indices = variable_indices.get('categorical_indices', [])
        
        self.n_continuous = len(self.continuous_indices)
        self.n_discrete = len(self.discrete_indices)
        self.n_categorical = len(self.categorical_indices)
        
        self.device = device or torch.device('cpu')
        
        logger.debug(f"UnifiedDistanceComputer initialized: "
                    f"{self.n_continuous} continuous, {self.n_discrete} discrete, "
                    f"{self.n_categorical} categorical variables")
    
    def compute_distance(self, x1: torch.Tensor, x2: torch.Tensor,
                        weights: torch.Tensor,
                        continuous_lengthscales: Optional[torch.Tensor] = None,
                        discrete_lengthscales: Optional[torch.Tensor] = None,
                        categorical_theta: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Compute unified distance between two sets of points.
        
        Args:
            x1: First set of points (n1, d_total)
            x2: Second set of points (n2, d_total)
            weights: Weight parameters for each variable (d_total,)
            continuous_lengthscales: Lengthscales for continuous variables (d_cont,)
            discrete_lengthscales: Lengthscales for discrete variables (d_disc,)
            categorical_theta: Theta parameters for categorical variables (d_cat,)
        
        Returns:
            Total distance tensor (n1, n2)
        """
        if x1.shape[1] != x2.shape[1]:
            raise ValueError("x1 and x2 must have same number of dimensions")
        
        total_distance = torch.zeros(x1.shape[0], x2.shape[0], device=self.device)
        
        # Continuous variables
        if self.n_continuous > 0:
            if continuous_lengthscales is None:
                raise ValueError("continuous_lengthscales required for continuous variables")
            
            x1_cont = x1[:, self.continuous_indices]
            x2_cont = x2[:, self.continuous_indices]
            weights_cont = weights[self.continuous_indices]
            
            cont_dist = DistanceFunctions.continuous_distance(
                x1_cont, x2_cont, continuous_lengthscales
            )
            
            # Apply weights
            weighted_cont_dist = (weights_cont.unsqueeze(0).unsqueeze(0) * 
                                cont_dist.unsqueeze(-1)).sum(dim=-1)
            total_distance += weighted_cont_dist
        
        # Discrete variables
        if self.n_discrete > 0:
            if discrete_lengthscales is None:
                raise ValueError("discrete_lengthscales required for discrete variables")
            
            x1_disc = x1[:, self.discrete_indices]
            x2_disc = x2[:, self.discrete_indices]
            weights_disc = weights[self.discrete_indices]
            
            disc_dist = DistanceFunctions.discrete_distance(
                x1_disc, x2_disc, discrete_lengthscales
            )
            
            # Apply weights
            weighted_disc_dist = (weights_disc.unsqueeze(0).unsqueeze(0) * 
                                disc_dist.unsqueeze(-1)).sum(dim=-1)
            total_distance += weighted_disc_dist
        
        # Categorical variables
        if self.n_categorical > 0:
            if categorical_theta is None:
                raise ValueError("categorical_theta required for categorical variables")
            
            x1_cat = x1[:, self.categorical_indices]
            x2_cat = x2[:, self.categorical_indices]
            weights_cat = weights[self.categorical_indices]
            
            cat_dist = DistanceFunctions.categorical_distance(
                x1_cat, x2_cat, categorical_theta
            )
            
            # Apply weights
            weighted_cat_dist = (weights_cat.unsqueeze(0).unsqueeze(0) * 
                               cat_dist.unsqueeze(-1)).sum(dim=-1)
            total_distance += weighted_cat_dist
        
        return total_distance
    
    def compute_distance_components(self, x1: torch.Tensor, x2: torch.Tensor,
                                  weights: torch.Tensor,
                                  continuous_lengthscales: Optional[torch.Tensor] = None,
                                  discrete_lengthscales: Optional[torch.Tensor] = None,
                                  categorical_theta: Optional[torch.Tensor] = None) -> dict:
        """
        Compute distance components separately for analysis.
        
        Returns:
            Dictionary with distance components for each variable type
        """
        components = {}
        
        # Continuous component
        if self.n_continuous > 0 and continuous_lengthscales is not None:
            x1_cont = x1[:, self.continuous_indices]
            x2_cont = x2[:, self.continuous_indices]
            weights_cont = weights[self.continuous_indices]
            
            cont_dist = DistanceFunctions.continuous_distance(
                x1_cont, x2_cont, continuous_lengthscales
            )
            components['continuous'] = (weights_cont.unsqueeze(0).unsqueeze(0) * 
                                      cont_dist.unsqueeze(-1)).sum(dim=-1)
        else:
            components['continuous'] = torch.zeros(x1.shape[0], x2.shape[0], device=self.device)
        
        # Discrete component
        if self.n_discrete > 0 and discrete_lengthscales is not None:
            x1_disc = x1[:, self.discrete_indices]
            x2_disc = x2[:, self.discrete_indices]
            weights_disc = weights[self.discrete_indices]
            
            disc_dist = DistanceFunctions.discrete_distance(
                x1_disc, x2_disc, discrete_lengthscales
            )
            components['discrete'] = (weights_disc.unsqueeze(0).unsqueeze(0) * 
                                    disc_dist.unsqueeze(-1)).sum(dim=-1)
        else:
            components['discrete'] = torch.zeros(x1.shape[0], x2.shape[0], device=self.device)
        
        # Categorical component
        if self.n_categorical > 0 and categorical_theta is not None:
            x1_cat = x1[:, self.categorical_indices]
            x2_cat = x2[:, self.categorical_indices]
            weights_cat = weights[self.categorical_indices]
            
            cat_dist = DistanceFunctions.categorical_distance(
                x1_cat, x2_cat, categorical_theta
            )
            components['categorical'] = (weights_cat.unsqueeze(0).unsqueeze(0) * 
                                       cat_dist.unsqueeze(-1)).sum(dim=-1)
        else:
            components['categorical'] = torch.zeros(x1.shape[0], x2.shape[0], device=self.device)
        
        components['total'] = (components['continuous'] + 
                             components['discrete'] + 
                             components['categorical'])
        
        return components