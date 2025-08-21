"""
Test Functions Module - GPU-Accelerated Mathematical Benchmark Functions

This module implements standard multi-objective test functions for benchmarking
optimization algorithms with GPU acceleration support. These functions are 
well-established in the literature and provide known Pareto fronts for algorithm validation.

Key Features:
- Hardware-agnostic GPU acceleration (CUDA, MPS, CPU fallback)
- Vectorized PyTorch implementations for batch evaluation
- Automatic device management and memory optimization
- Support for both NumPy and PyTorch tensor inputs
- Consistent interface across all test functions

Classes:
    TestFunction: Base class for GPU-accelerated test functions
    ZDT1: ZDT1 test function implementation with GPU support
    ZDT2: ZDT2 test function implementation with GPU support
    DTLZ2: DTLZ2 test function implementation with GPU support

Author: Multi-Objective Optimization Laboratory
Version: 3.6.6 GPU Accelerated
"""

import numpy as np
import torch
from torch import Tensor
from typing import Dict, List, Optional, Tuple, Union
from abc import ABC, abstractmethod
import warnings
import logging

# Import device management
from pymbo.core.device_manager import get_device_manager, to_device

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)


class TestFunction(ABC):
    """Base class for GPU-accelerated multi-objective test functions."""
    
    def __init__(self, n_vars: int, n_objectives: int = 2):
        """Initialize test function.
        
        Args:
            n_vars: Number of decision variables
            n_objectives: Number of objectives (default: 2)
        """
        self.n_vars = n_vars
        self.n_objectives = n_objectives
        self.bounds = self._get_bounds()
        
        # Initialize device manager for GPU acceleration
        self.device_manager = get_device_manager()
        self.device = self.device_manager.device
        
        logger.debug(f"Test function initialized on device: {self.device}")
        
    @abstractmethod
    def _get_bounds(self) -> List[Tuple[float, float]]:
        """Get variable bounds for the test function.
        
        Returns:
            List of (lower, upper) bound tuples for each variable
        """
        pass
        
    @abstractmethod
    def evaluate(self, x: Union[np.ndarray, Tensor]) -> Union[np.ndarray, Tensor]:
        """Evaluate the test function with GPU acceleration.
        
        Args:
            x: Input variables (n_points, n_vars) - NumPy array or PyTorch tensor
            
        Returns:
            Objective values (n_points, n_objectives) - same type as input
        """
        pass
    
    def _ensure_tensor(self, x: Union[np.ndarray, Tensor]) -> Tensor:
        """Convert input to PyTorch tensor on the correct device."""
        if isinstance(x, np.ndarray):
            return torch.tensor(x, dtype=torch.float64, device=self.device)
        elif isinstance(x, Tensor):
            return x.to(device=self.device, dtype=torch.float64)
        else:
            raise TypeError(f"Input must be numpy array or torch tensor, got {type(x)}")
    
    def _match_output_type(self, result: Tensor, input_type: type) -> Union[np.ndarray, Tensor]:
        """Convert output to match input type."""
        if input_type == np.ndarray:
            return result.cpu().numpy()
        else:
            return result
        
    def get_params_config(self) -> Dict:
        """Get parameter configuration for PyMBO."""
        params_config = {}
        for i in range(self.n_vars):
            params_config[f"x{i+1}"] = {
                "type": "continuous",
                "bounds": list(self.bounds[i]),
                "goal": "None"
            }
        return params_config
        
    def get_responses_config(self) -> Dict:
        """Get response configuration for PyMBO."""
        responses_config = {}
        for i in range(self.n_objectives):
            responses_config[f"f{i+1}"] = {"goal": "Minimize"}
        return responses_config


class ZDT1(TestFunction):
    """ZDT1 test function.
    
    A bi-objective test function with:
    - n_vars decision variables (typically 30)
    - 2 objectives
    - Convex Pareto front
    """
    
    def __init__(self, n_vars: int = 30):
        """Initialize ZDT1 function.
        
        Args:
            n_vars: Number of decision variables (default: 30)
        """
        super().__init__(n_vars, n_objectives=2)
        
    def _get_bounds(self) -> List[Tuple[float, float]]:
        """Get bounds: [0, 1] for all variables."""
        return [(0.0, 1.0) for _ in range(self.n_vars)]
        
    def evaluate(self, x: Union[np.ndarray, Tensor]) -> Union[np.ndarray, Tensor]:
        """Evaluate ZDT1 function with GPU acceleration.
        
        f1(x) = x1
        g(x) = 1 + 9 * sum(x2:xn) / (n-1)
        f2(x) = g(x) * (1 - sqrt(f1(x)/g(x)))
        
        Args:
            x: Input variables (n_points, n_vars)
            
        Returns:
            Objective values (n_points, 2)
        """
        input_type = type(x)
        
        # Convert to tensor and move to device
        x_tensor = self._ensure_tensor(x)
        
        # Ensure 2D input
        if x_tensor.dim() == 1:
            x_tensor = x_tensor.unsqueeze(0)
        
        # GPU-accelerated evaluation using PyTorch
        f1 = x_tensor[:, 0]
        
        if self.n_vars > 1:
            g = 1 + 9 * torch.sum(x_tensor[:, 1:], dim=1) / (self.n_vars - 1)
        else:
            g = torch.ones_like(f1)
            
        # Add small epsilon to prevent division by zero
        epsilon = 1e-10
        f2 = g * (1 - torch.sqrt(torch.clamp(f1 / (g + epsilon), min=epsilon)))
        
        result = torch.stack([f1, f2], dim=1)
        
        # Return in same format as input
        return self._match_output_type(result, input_type)
        
    def get_true_pareto_front(self, n_points: int = 100) -> np.ndarray:
        """Get the true Pareto front for ZDT1.
        
        Args:
            n_points: Number of points on the Pareto front
            
        Returns:
            Pareto front points (n_points, 2)
        """
        f1 = np.linspace(0, 1, n_points)
        f2 = 1 - np.sqrt(f1)
        return np.column_stack([f1, f2])


class ZDT2(TestFunction):
    """ZDT2 test function.
    
    A bi-objective test function with:
    - n_vars decision variables (typically 30)
    - 2 objectives
    - Non-convex Pareto front
    """
    
    def __init__(self, n_vars: int = 30):
        """Initialize ZDT2 function.
        
        Args:
            n_vars: Number of decision variables (default: 30)
        """
        super().__init__(n_vars, n_objectives=2)
        
    def _get_bounds(self) -> List[Tuple[float, float]]:
        """Get bounds: [0, 1] for all variables."""
        return [(0.0, 1.0) for _ in range(self.n_vars)]
        
    def evaluate(self, x: Union[np.ndarray, Tensor]) -> Union[np.ndarray, Tensor]:
        """Evaluate ZDT2 function.
        
        f1(x) = x1
        g(x) = 1 + 9 * sum(x2:xn) / (n-1)
        f2(x) = g(x) * (1 - (f1(x)/g(x))^2)
        
        Args:
            x: Input variables (n_points, n_vars)
            
        Returns:
            Objective values (n_points, 2)
        """
        if isinstance(x, np.ndarray):
            return self._evaluate_numpy(x)
        else:
            return self._evaluate_torch(x)
            
    def _evaluate_numpy(self, x: np.ndarray) -> np.ndarray:
        """NumPy implementation."""
        f1 = x[:, 0]
        
        if self.n_vars > 1:
            g = 1 + 9 * np.sum(x[:, 1:], axis=1) / (self.n_vars - 1)
        else:
            g = np.ones_like(f1)
            
        f2 = g * (1 - (f1 / g) ** 2)
        
        return np.column_stack([f1, f2])
        
    def _evaluate_torch(self, x: Tensor) -> Tensor:
        """PyTorch implementation."""
        f1 = x[:, 0]
        
        if self.n_vars > 1:
            g = 1 + 9 * torch.sum(x[:, 1:], dim=1) / (self.n_vars - 1)
        else:
            g = torch.ones_like(f1)
            
        f2 = g * (1 - (f1 / g) ** 2)
        
        return torch.stack([f1, f2], dim=1)
        
    def get_true_pareto_front(self, n_points: int = 100) -> np.ndarray:
        """Get the true Pareto front for ZDT2.
        
        Args:
            n_points: Number of points on the Pareto front
            
        Returns:
            Pareto front points (n_points, 2)
        """
        f1 = np.linspace(0, 1, n_points)
        f2 = 1 - f1 ** 2
        return np.column_stack([f1, f2])


class DTLZ2(TestFunction):
    """DTLZ2 test function.
    
    A scalable multi-objective test function with:
    - n_vars decision variables
    - n_objectives objectives (default: 3)
    - Spherical Pareto front
    """
    
    def __init__(self, n_vars: int = 12, n_objectives: int = 3):
        """Initialize DTLZ2 function.
        
        Args:
            n_vars: Number of decision variables (default: 12)
            n_objectives: Number of objectives (default: 3)
        """
        if n_vars < n_objectives - 1:
            raise ValueError(f"n_vars ({n_vars}) must be >= n_objectives - 1 ({n_objectives - 1})")
        super().__init__(n_vars, n_objectives)
        
    def _get_bounds(self) -> List[Tuple[float, float]]:
        """Get bounds: [0, 1] for all variables."""
        return [(0.0, 1.0) for _ in range(self.n_vars)]
        
    def evaluate(self, x: Union[np.ndarray, Tensor]) -> Union[np.ndarray, Tensor]:
        """Evaluate DTLZ2 function.
        
        Args:
            x: Input variables (n_points, n_vars)
            
        Returns:
            Objective values (n_points, n_objectives)
        """
        if isinstance(x, np.ndarray):
            return self._evaluate_numpy(x)
        else:
            return self._evaluate_torch(x)
            
    def _evaluate_numpy(self, x: np.ndarray) -> np.ndarray:
        """NumPy implementation."""
        M = self.n_objectives
        k = self.n_vars - M + 1
        
        # Split variables
        x_m = x[:, :M-1]  # First M-1 variables
        x_k = x[:, M-1:]  # Last k variables
        
        # Compute g function
        g = np.sum((x_k - 0.5) ** 2, axis=1)
        
        # Compute objectives
        objectives = []
        for i in range(M):
            if i == 0:
                f_i = (1 + g) * np.prod(np.cos(x_m * np.pi / 2), axis=1)
            elif i < M - 1:
                f_i = (1 + g) * np.prod(np.cos(x_m[:, :M-1-i] * np.pi / 2), axis=1) * np.sin(x_m[:, M-1-i] * np.pi / 2)
            else:  # Last objective
                f_i = (1 + g) * np.sin(x_m[:, 0] * np.pi / 2)
            objectives.append(f_i)
            
        return np.column_stack(objectives)
        
    def _evaluate_torch(self, x: Tensor) -> Tensor:
        """PyTorch implementation."""
        M = self.n_objectives
        k = self.n_vars - M + 1
        
        # Split variables
        x_m = x[:, :M-1]  # First M-1 variables
        x_k = x[:, M-1:]  # Last k variables
        
        # Compute g function
        g = torch.sum((x_k - 0.5) ** 2, dim=1)
        
        # Compute objectives
        objectives = []
        for i in range(M):
            if i == 0:
                f_i = (1 + g) * torch.prod(torch.cos(x_m * np.pi / 2), dim=1)
            elif i < M - 1:
                f_i = (1 + g) * torch.prod(torch.cos(x_m[:, :M-1-i] * np.pi / 2), dim=1) * torch.sin(x_m[:, M-1-i] * np.pi / 2)
            else:  # Last objective
                f_i = (1 + g) * torch.sin(x_m[:, 0] * np.pi / 2)
            objectives.append(f_i)
            
        return torch.stack(objectives, dim=1)


class Sphere(TestFunction):
    """Sphere test function.
    
    A simple single-objective test function with:
    - n_vars decision variables (typically 2-10) 
    - 1 objective: f(x) = sum(x_i^2)
    - Global minimum at x = [0, 0, ..., 0] with f(x) = 0
    """
    
    def __init__(self, n_vars: int = 2):
        """Initialize Sphere function.
        
        Args:
            n_vars: Number of decision variables (default: 2)
        """
        super().__init__(n_vars, n_objectives=1)
        
    def _get_bounds(self) -> List[Tuple[float, float]]:
        """Get bounds: [-5.12, 5.12] for all variables."""
        return [(-5.12, 5.12) for _ in range(self.n_vars)]
        
    def evaluate(self, x: Union[np.ndarray, Tensor]) -> Union[np.ndarray, Tensor]:
        """Evaluate Sphere function.
        
        f(x) = sum(x_i^2)
        
        Args:
            x: Input variables (n_points, n_vars)
            
        Returns:
            Objective values (n_points, 1)
        """
        if isinstance(x, np.ndarray):
            return self._evaluate_numpy(x)
        else:
            return self._evaluate_torch(x)
            
    def _evaluate_numpy(self, x: np.ndarray) -> np.ndarray:
        """NumPy implementation."""
        f = np.sum(x ** 2, axis=1, keepdims=True)
        return f
        
    def _evaluate_torch(self, x: Tensor) -> Tensor:
        """PyTorch implementation."""
        f = torch.sum(x ** 2, dim=1, keepdim=True)
        return f
    
    def get_responses_config(self) -> Dict:
        """Get response configuration for PyMBO."""
        return {"f1": {"goal": "Minimize"}}


class Rosenbrock(TestFunction):
    """Rosenbrock test function.
    
    A classic single-objective test function with:
    - n_vars decision variables (typically 2-10)
    - 1 objective: f(x) = sum(100*(x_{i+1} - x_i^2)^2 + (1 - x_i)^2)
    - Global minimum at x = [1, 1, ..., 1] with f(x) = 0
    - Known for having a narrow curved valley
    """
    
    def __init__(self, n_vars: int = 2):
        """Initialize Rosenbrock function.
        
        Args:
            n_vars: Number of decision variables (default: 2)
        """
        super().__init__(n_vars, n_objectives=1)
        
    def _get_bounds(self) -> List[Tuple[float, float]]:
        """Get bounds: [-5, 10] for all variables."""
        return [(-5.0, 10.0) for _ in range(self.n_vars)]
        
    def evaluate(self, x: Union[np.ndarray, Tensor]) -> Union[np.ndarray, Tensor]:
        """Evaluate Rosenbrock function.
        
        f(x) = sum(100*(x_{i+1} - x_i^2)^2 + (1 - x_i)^2) for i = 1 to n-1
        
        Args:
            x: Input variables (n_points, n_vars)
            
        Returns:
            Objective values (n_points, 1)
        """
        if isinstance(x, np.ndarray):
            return self._evaluate_numpy(x)
        else:
            return self._evaluate_torch(x)
            
    def _evaluate_numpy(self, x: np.ndarray) -> np.ndarray:
        """NumPy implementation."""
        if x.shape[1] < 2:
            raise ValueError("Rosenbrock function requires at least 2 variables")
            
        f = np.zeros((x.shape[0], 1))
        for i in range(x.shape[1] - 1):
            f[:, 0] += 100 * (x[:, i+1] - x[:, i]**2)**2 + (1 - x[:, i])**2
        return f
        
    def _evaluate_torch(self, x: Tensor) -> Tensor:
        """PyTorch implementation."""
        if x.shape[1] < 2:
            raise ValueError("Rosenbrock function requires at least 2 variables")
            
        f = torch.zeros(x.shape[0], 1, dtype=x.dtype, device=x.device)
        for i in range(x.shape[1] - 1):
            f[:, 0] += 100 * (x[:, i+1] - x[:, i]**2)**2 + (1 - x[:, i])**2
        return f
    
    def get_responses_config(self) -> Dict:
        """Get response configuration for PyMBO."""
        return {"f1": {"goal": "Minimize"}}


# Available test functions registry
TEST_FUNCTIONS = {
    "ZDT1": ZDT1,
    "ZDT2": ZDT2, 
    "DTLZ2": DTLZ2,
    "Sphere": Sphere,
    "Rosenbrock": Rosenbrock,
}


def get_test_function(name: str, **kwargs) -> TestFunction:
    """Get a test function by name.
    
    Args:
        name: Test function name
        **kwargs: Arguments for test function constructor
        
    Returns:
        Test function instance
        
    Raises:
        ValueError: If test function name is not recognized
    """
    if name not in TEST_FUNCTIONS:
        available = ", ".join(TEST_FUNCTIONS.keys())
        raise ValueError(f"Unknown test function '{name}'. Available: {available}")
        
    return TEST_FUNCTIONS[name](**kwargs)