"""
Test Function Manager - Centralized Test Function Registry
=========================================================

This module provides centralized management of test functions for algorithm
verification, including metadata, reference points, and utility functions.

Classes:
    TestFunctionInfo: Information container for test functions
    TestFunctionManager: Centralized test function registry and manager

Author: PyMBO Development Team
Version: 3.6.6 - Unified Verification Architecture
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TestFunctionInfo:
    """Information container for a test function."""
    
    name: str
    display_name: str
    description: str
    n_objectives: int
    n_variables: int
    bounds: List[Tuple[float, float]]
    known_optimum: Optional[float] = None
    reference_point: Optional[np.ndarray] = None
    difficulty: str = "medium"  # easy, medium, hard
    category: str = "general"  # general, multi-modal, constrained, etc.
    has_true_pareto_front: bool = False
    
    def __post_init__(self):
        """Post-initialization validation."""
        if self.n_variables != len(self.bounds):
            raise ValueError(f"Number of variables ({self.n_variables}) doesn't match bounds length ({len(self.bounds)})")
        
        if self.reference_point is not None:
            if len(self.reference_point) != self.n_objectives:
                raise ValueError(f"Reference point dimension ({len(self.reference_point)}) doesn't match number of objectives ({self.n_objectives})")


class TestFunctionManager:
    """Centralized manager for test functions."""
    
    def __init__(self):
        """Initialize the test function manager."""
        self.functions = {}
        self.function_info = {}
        self._register_default_functions()
        
        logger.info(f"TestFunctionManager initialized with {len(self.functions)} functions")
    
    def _register_default_functions(self):
        """Register default test functions."""
        # Always register basic functions first as fallback
        self._register_basic_functions()
        
        # Then try to import and register additional functions
        try:
            from .test_functions import get_test_function, TEST_FUNCTIONS
            self._import_existing_functions(get_test_function, TEST_FUNCTIONS)
        except ImportError as e:
            logger.warning(f"Could not import existing test functions: {e}")
        
        logger.info(f"Registered {len(self.functions)} test functions")
    
    def _import_existing_functions(self, get_test_function, test_functions_dict):
        """Import existing test functions from the current system."""
        imported_count = 0
        for func_name in test_functions_dict.keys():
            # Skip if we already have this function from basic functions
            if func_name in self.functions:
                continue
                
            try:
                func = get_test_function(func_name)
                info = self._create_function_info(func_name, func)
                self.register_function(func_name, func, info)
                imported_count += 1
            except Exception as e:
                logger.debug(f"Failed to import test function {func_name}: {e}")
        
        if imported_count > 0:
            logger.info(f"Successfully imported {imported_count} additional test functions")
    
    def _create_function_info(self, name: str, func) -> TestFunctionInfo:
        """Create TestFunctionInfo from existing function."""
        # Extract information from function attributes
        display_name = getattr(func, 'display_name', name.replace('_', ' ').title())
        description = getattr(func, 'description', f"{name} test function")
        n_objectives = getattr(func, 'n_objectives', 2)
        n_variables = getattr(func, 'n_variables', 2)
        
        # Get bounds - ensure they match n_variables
        bounds = getattr(func, 'bounds', None)
        if bounds is None or len(bounds) != n_variables:
            # Create default bounds matching n_variables
            if hasattr(func, 'bounds') and func.bounds:
                # Use the pattern from existing bounds but match length
                first_bound = func.bounds[0] if func.bounds else (0.0, 1.0)
                bounds = [first_bound] * n_variables
            else:
                # Default bounds
                bounds = [(0.0, 1.0)] * n_variables
        
        # Reference point
        reference_point = getattr(func, 'reference_point', None)
        if reference_point is None:
            reference_point = self._compute_default_reference_point(name, n_objectives)
        
        # Categorize function
        difficulty, category = self._categorize_function(name)
        
        # Check for true Pareto front
        has_true_pf = hasattr(func, 'get_true_pareto_front')
        
        return TestFunctionInfo(
            name=name,
            display_name=display_name,
            description=description,
            n_objectives=n_objectives,
            n_variables=n_variables,
            bounds=bounds,
            reference_point=reference_point,
            difficulty=difficulty,
            category=category,
            has_true_pareto_front=has_true_pf
        )
    
    def _compute_default_reference_point(self, name: str, n_objectives: int) -> np.ndarray:
        """Compute default reference point based on function name and objectives."""
        # Common reference points for well-known functions
        reference_points = {
            'ZDT1': np.array([1.1, 1.1]),
            'ZDT2': np.array([1.1, 1.1]),
            'ZDT3': np.array([1.1, 1.1]),
            'ZDT4': np.array([1.1, 1.1]),
            'ZDT6': np.array([1.1, 1.1]),
            'DTLZ1': np.array([0.6] * n_objectives),
            'DTLZ2': np.array([1.2] * n_objectives),
            'DTLZ3': np.array([1.2] * n_objectives),
            'DTLZ4': np.array([1.2] * n_objectives),
            'DTLZ5': np.array([1.2] * n_objectives),
            'DTLZ6': np.array([1.2] * n_objectives),
            'DTLZ7': np.array([1.1] + [21.0] * (n_objectives - 1)),
            'Branin': np.array([400.0]),
            'Hartmann3': np.array([0.0]),
            'Hartmann6': np.array([0.0]),
            'Rosenbrock': np.array([100.0]),
            'Ackley': np.array([20.0])
        }
        
        if name in reference_points:
            ref_point = reference_points[name]
            # Ensure correct dimension
            if len(ref_point) == n_objectives:
                return ref_point
            elif len(ref_point) == 1 and n_objectives > 1:
                return np.array([ref_point[0]] * n_objectives)
        
        # Default reference point
        return np.array([1.1] * n_objectives)
    
    def _categorize_function(self, name: str) -> Tuple[str, str]:
        """Categorize function by difficulty and type."""
        # Difficulty classification
        easy_functions = ['ZDT1', 'ZDT2', 'DTLZ1', 'DTLZ2', 'Branin']
        hard_functions = ['ZDT4', 'DTLZ3', 'DTLZ7', 'Hartmann6', 'Ackley']
        
        if name in easy_functions:
            difficulty = "easy"
        elif name in hard_functions:
            difficulty = "hard"
        else:
            difficulty = "medium"
        
        # Category classification
        multi_modal = ['ZDT4', 'DTLZ3', 'Ackley', 'Rastrigin']
        constrained = ['DTLZ7']
        single_objective = ['Branin', 'Hartmann3', 'Hartmann6', 'Rosenbrock', 'Ackley']
        
        if name in multi_modal:
            category = "multi-modal"
        elif name in constrained:
            category = "constrained"
        elif name in single_objective:
            category = "single-objective"
        else:
            category = "multi-objective"
        
        return difficulty, category
    
    def _register_basic_functions(self):
        """Register basic test functions as fallback."""
        # Simple 2D test functions for fallback
        basic_functions = {
            'ZDT1': self._create_zdt1(),
            'Sphere': self._create_sphere(),
            'Rosenbrock': self._create_rosenbrock()
        }
        
        for name, (func, info) in basic_functions.items():
            self.register_function(name, func, info)
    
    def _create_zdt1(self):
        """Create ZDT1 test function."""
        class ZDT1:
            def __init__(self):
                self.n_objectives = 2
                self.n_variables = 30
                self.bounds = [(0.0, 1.0)] * 30
                self.display_name = "ZDT1"
                self.description = "ZDT1 multi-objective test function"
                self.reference_point = np.array([1.1, 1.1])
            
            def __call__(self, x):
                x = np.asarray(x)
                if x.ndim == 1:
                    x = x.reshape(1, -1)
                
                f1 = x[:, 0]
                g = 1 + 9 * np.sum(x[:, 1:], axis=1) / (x.shape[1] - 1)
                f2 = g * (1 - np.sqrt(f1 / g))
                
                return np.column_stack([f1, f2])
            
            def get_true_pareto_front(self, n_points=100):
                x1 = np.linspace(0, 1, n_points)
                x2 = 1 - np.sqrt(x1)
                return np.column_stack([x1, x2])
        
        func = ZDT1()
        info = TestFunctionInfo(
            name="ZDT1",
            display_name="ZDT1",
            description="ZDT1 multi-objective test function - convex Pareto front",
            n_objectives=2,
            n_variables=30,
            bounds=[(0.0, 1.0)] * 30,
            reference_point=np.array([1.1, 1.1]),
            difficulty="easy",
            category="multi-objective",
            has_true_pareto_front=True
        )
        
        return func, info
    
    def _create_sphere(self):
        """Create Sphere test function."""
        class Sphere:
            def __init__(self):
                self.n_objectives = 1
                self.n_variables = 2
                self.bounds = [(-5.0, 5.0)] * 2
                self.display_name = "Sphere"
                self.description = "Sphere function"
                self.reference_point = np.array([25.0])
                self.known_optimum = 0.0
            
            def __call__(self, x):
                x = np.asarray(x)
                if x.ndim == 1:
                    x = x.reshape(1, -1)
                return np.sum(x**2, axis=1).reshape(-1, 1)
        
        func = Sphere()
        info = TestFunctionInfo(
            name="Sphere",
            display_name="Sphere Function",
            description="Simple quadratic function - global optimum at origin",
            n_objectives=1,
            n_variables=2,
            bounds=[(-5.0, 5.0)] * 2,
            known_optimum=0.0,
            reference_point=np.array([25.0]),
            difficulty="easy",
            category="single-objective"
        )
        
        return func, info
    
    def _create_rosenbrock(self):
        """Create Rosenbrock test function."""
        class Rosenbrock:
            def __init__(self):
                self.n_objectives = 1
                self.n_variables = 2
                self.bounds = [(-2.0, 2.0)] * 2
                self.display_name = "Rosenbrock"
                self.description = "Rosenbrock function"
                self.reference_point = np.array([100.0])
                self.known_optimum = 0.0
            
            def __call__(self, x):
                x = np.asarray(x)
                if x.ndim == 1:
                    x = x.reshape(1, -1)
                
                result = []
                for row in x:
                    val = 100 * (row[1] - row[0]**2)**2 + (1 - row[0])**2
                    result.append(val)
                
                return np.array(result).reshape(-1, 1)
        
        func = Rosenbrock()
        info = TestFunctionInfo(
            name="Rosenbrock",
            display_name="Rosenbrock Function",
            description="Rosenbrock function - banana-shaped valley",
            n_objectives=1,
            n_variables=2,
            bounds=[(-2.0, 2.0)] * 2,
            known_optimum=0.0,
            reference_point=np.array([100.0]),
            difficulty="medium",
            category="single-objective"
        )
        
        return func, info
    
    def register_function(self, name: str, function: Any, info: TestFunctionInfo):
        """Register a new test function.
        
        Args:
            name: Function name (used as key)
            function: Callable test function
            info: Function information
        """
        self.functions[name] = function
        self.function_info[name] = info
        logger.debug(f"Registered test function: {name}")
    
    def get_function(self, name: str):
        """Get a test function by name.
        
        Args:
            name: Function name
            
        Returns:
            Test function instance
            
        Raises:
            KeyError: If function not found
        """
        if name not in self.functions:
            raise KeyError(f"Test function '{name}' not found. Available: {list(self.functions.keys())}")
        
        return self.functions[name]
    
    def get_function_info(self, name: str) -> TestFunctionInfo:
        """Get information for a test function.
        
        Args:
            name: Function name
            
        Returns:
            Function information
            
        Raises:
            KeyError: If function not found
        """
        if name not in self.function_info:
            raise KeyError(f"Test function '{name}' not found.")
        
        return self.function_info[name]
    
    def list_functions(self) -> List[str]:
        """Get list of available function names.
        
        Returns:
            List of function names
        """
        return list(self.functions.keys())
    
    def list_functions_by_category(self, category: str) -> List[str]:
        """Get functions by category.
        
        Args:
            category: Function category
            
        Returns:
            List of function names in category
        """
        return [name for name, info in self.function_info.items() 
                if info.category == category]
    
    def list_functions_by_difficulty(self, difficulty: str) -> List[str]:
        """Get functions by difficulty.
        
        Args:
            difficulty: Function difficulty (easy, medium, hard)
            
        Returns:
            List of function names with specified difficulty
        """
        return [name for name, info in self.function_info.items() 
                if info.difficulty == difficulty]
    
    def get_multi_objective_functions(self) -> List[str]:
        """Get list of multi-objective functions.
        
        Returns:
            List of multi-objective function names
        """
        return [name for name, info in self.function_info.items() 
                if info.n_objectives > 1]
    
    def get_single_objective_functions(self) -> List[str]:
        """Get list of single-objective functions.
        
        Returns:
            List of single-objective function names
        """
        return [name for name, info in self.function_info.items() 
                if info.n_objectives == 1]
    
    def get_functions_with_true_pareto_front(self) -> List[str]:
        """Get functions that have analytical Pareto fronts.
        
        Returns:
            List of function names with true Pareto fronts
        """
        return [name for name, info in self.function_info.items() 
                if info.has_true_pareto_front]
    
    def get_recommended_functions(self, purpose: str = "general") -> List[str]:
        """Get recommended functions for specific purposes.
        
        Args:
            purpose: Purpose of verification (general, quick, comprehensive, demo)
            
        Returns:
            List of recommended function names
        """
        if purpose == "quick":
            # Fast functions for quick testing
            return ["ZDT1", "Sphere"]
        elif purpose == "demo":
            # Good functions for demonstration
            return ["ZDT1", "ZDT2", "Branin"]
        elif purpose == "comprehensive":
            # Comprehensive test suite
            mo_functions = self.get_multi_objective_functions()[:3]
            so_functions = self.get_single_objective_functions()[:2]
            return mo_functions + so_functions
        else:  # general
            # General purpose selection
            return ["ZDT1", "ZDT2", "Sphere", "Rosenbrock"]
    
    def validate_function_compatibility(self, function_name: str, algorithm_info: Dict) -> bool:
        """Validate if a function is compatible with an algorithm.
        
        Args:
            function_name: Name of test function
            algorithm_info: Algorithm information dictionary
            
        Returns:
            True if compatible, False otherwise
        """
        try:
            func_info = self.get_function_info(function_name)
            
            # Check objective compatibility
            if 'supports_multi_objective' in algorithm_info:
                if func_info.n_objectives > 1 and not algorithm_info['supports_multi_objective']:
                    return False
            
            # Check constraint compatibility
            if func_info.category == "constrained":
                if not algorithm_info.get('supports_constraints', False):
                    return False
            
            # Check variable bounds compatibility
            if 'requires_bounded' in algorithm_info:
                if algorithm_info['requires_bounded'] and any(
                    bound[0] == -np.inf or bound[1] == np.inf 
                    for bound in func_info.bounds
                ):
                    return False
            
            return True
            
        except KeyError:
            return False
    
    def get_reference_point(self, function_name: str) -> np.ndarray:
        """Get reference point for hypervolume calculation.
        
        Args:
            function_name: Name of test function
            
        Returns:
            Reference point array
        """
        info = self.get_function_info(function_name)
        return info.reference_point.copy()
    
    def compute_adaptive_reference_point(self, function_name: str, sample_points: np.ndarray) -> np.ndarray:
        """Compute adaptive reference point based on sample data.
        
        Args:
            function_name: Name of test function
            sample_points: Sample objective values
            
        Returns:
            Adaptive reference point
        """
        info = self.get_function_info(function_name)
        
        if sample_points.size == 0:
            return info.reference_point.copy()
        
        # Compute reference point as max values + 10% margin
        max_vals = np.max(sample_points, axis=0)
        adaptive_ref = max_vals * 1.1
        
        # Ensure it's at least as large as the default reference point
        default_ref = info.reference_point
        final_ref = np.maximum(adaptive_ref, default_ref)
        
        return final_ref


# Global instance for easy access
_global_manager = None

def get_test_function_manager() -> TestFunctionManager:
    """Get the global test function manager instance.
    
    Returns:
        TestFunctionManager instance
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = TestFunctionManager()
    return _global_manager