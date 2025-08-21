"""
Benchmark Algorithms Module - Standard Optimization Algorithms for Comparison

This module implements standard optimization algorithms used for benchmarking
against the main MOBO algorithm. It provides a common interface for different
optimization strategies.

Classes:
    BenchmarkAlgorithm: Base class for benchmark algorithms
    RandomSearchAlgorithm: Random search implementation
    NSGAIIAlgorithm: NSGA-II algorithm implementation (using pymoo)
    MOBOAlgorithm: Wrapper for the main MOBO algorithm

Author: Multi-Objective Optimization Laboratory
Version: 3.6.6 Enhanced
"""

import numpy as np
import pandas as pd
import time
import torch
from torch import Tensor
from typing import Dict, List, Optional, Tuple, Union, Any
from abc import ABC, abstractmethod
import warnings
import logging

# Import centralized warnings configuration
from ..utils.warnings_config import configure_warnings
configure_warnings()

logger = logging.getLogger(__name__)

try:
    # Import pymoo for NSGA-II implementation
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.core.problem import Problem
    from pymoo.operators.crossover.sbx import SBX
    from pymoo.operators.mutation.pm import PM
    from pymoo.operators.sampling.rnd import FloatRandomSampling
    from pymoo.operators.selection.tournament import TournamentSelection
    from pymoo.optimize import minimize
    from pymoo.core.callback import Callback
    PYMOO_AVAILABLE = True
except ImportError:
    PYMOO_AVAILABLE = False
    logger.warning("pymoo not available - NSGA-II algorithm will be disabled")


class BenchmarkAlgorithm(ABC):
    """Base class for benchmark algorithms."""
    
    def __init__(self, name: str):
        """Initialize benchmark algorithm.
        
        Args:
            name: Algorithm name for identification
        """
        self.name = name
        self.history = []
        
    @abstractmethod
    def optimize(self, 
                 test_function,
                 n_evaluations: int,
                 initial_samples: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Run optimization algorithm.
        
        Args:
            test_function: Test function to optimize
            n_evaluations: Number of function evaluations
            initial_samples: Optional initial samples to start with
            
        Returns:
            Dictionary containing optimization results
        """
        pass
        
    def reset(self):
        """Reset algorithm state."""
        self.history = []


class RandomSearchAlgorithm(BenchmarkAlgorithm):
    """Random search algorithm implementation."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize random search algorithm.
        
        Args:
            seed: Random seed for reproducibility
        """
        super().__init__("Random Search")
        self.rng = np.random.RandomState(seed)
        
    def optimize(self, 
                 test_function,
                 n_evaluations: int,
                 initial_samples: Optional[np.ndarray] = None,
                 **kwargs) -> Dict[str, Any]:
        """Run random search optimization.
        
        Args:
            test_function: Test function to optimize
            n_evaluations: Number of function evaluations
            initial_samples: Optional initial samples (not used for random search)
            
        Returns:
            Dictionary containing optimization results
        """
        self.reset()
        
        # Generate random samples
        n_vars = test_function.n_vars
        bounds = np.array(test_function.bounds)
        lower_bounds = bounds[:, 0]
        upper_bounds = bounds[:, 1]
        
        # Generate random points in the design space
        X = self.rng.uniform(
            low=lower_bounds,
            high=upper_bounds,
            size=(n_evaluations, n_vars)
        )
        
        # Evaluate all points
        Y = test_function.evaluate(X)
        
        # Store history for hypervolume calculation
        for i in range(n_evaluations):
            self.history.append({
                'X': X[:i+1].copy(),
                'Y': Y[:i+1].copy(),
                'evaluation': i + 1
            })
            
        return {
            'X': X,
            'Y': Y,
            'algorithm': self.name,
            'history': self.history
        }


class NSGAIIAlgorithm(BenchmarkAlgorithm):
    """NSGA-II algorithm implementation using pymoo."""
    
    def __init__(self, 
                 population_size: int = 100,
                 seed: Optional[int] = None):
        """Initialize NSGA-II algorithm.
        
        Args:
            population_size: Population size for NSGA-II
            seed: Random seed for reproducibility
        """
        super().__init__("NSGA-II")
        self.population_size = population_size
        self.seed = seed
        
        if not PYMOO_AVAILABLE:
            raise ImportError("pymoo is required for NSGA-II algorithm. Install with: pip install pymoo")
            
    def optimize(self, 
                 test_function,
                 n_evaluations: int,
                 initial_samples: Optional[np.ndarray] = None,
                 **kwargs) -> Dict[str, Any]:
        """Run NSGA-II optimization.
        
        Args:
            test_function: Test function to optimize
            n_evaluations: Number of function evaluations
            initial_samples: Optional initial samples (not used for NSGA-II)
            **kwargs: Additional arguments (ignored)
            
        Returns:
            Dictionary containing optimization results
        """
        self.reset()
        
        # Create pymoo problem wrapper
        class TestFunctionProblem(Problem):
            def __init__(self, test_func):
                self.test_func = test_func
                bounds = np.array(test_func.bounds)
                super().__init__(
                    n_var=test_func.n_vars,
                    n_obj=test_func.n_objectives,
                    xl=bounds[:, 0],
                    xu=bounds[:, 1]
                )
                
            def _evaluate(self, x, out, *args, **kwargs):
                out["F"] = self.test_func.evaluate(x)
                
        # Create callback to store history
        class HistoryCallback(Callback):
            def __init__(self, algorithm_instance):
                super().__init__()
                self.algorithm_instance = algorithm_instance
                self.n_eval = 0
                
            def notify(self, algorithm):
                self.n_eval = algorithm.evaluator.n_eval
                # Store current population
                X = algorithm.pop.get("X")
                F = algorithm.pop.get("F")
                
                self.algorithm_instance.history.append({
                    'X': X.copy(),
                    'Y': F.copy(),
                    'evaluation': self.n_eval
                })
                
        problem = TestFunctionProblem(test_function)
        
        # Configure NSGA-II algorithm
        algorithm = NSGA2(
            pop_size=self.population_size,
            sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.9, eta=15),
            mutation=PM(eta=20),
            eliminate_duplicates=True
        )
        
        # Create callback instance
        callback = HistoryCallback(self)
        
        # Calculate number of generations needed
        n_generations = max(1, n_evaluations // self.population_size)
        
        # Run optimization
        result = minimize(
            problem,
            algorithm,
            ("n_gen", n_generations),
            callback=callback,
            seed=self.seed,
            verbose=False
        )
        
        return {
            'X': result.X,
            'Y': result.F,
            'algorithm': self.name,
            'history': self.history,
            'result': result
        }


class MOBOAlgorithm(BenchmarkAlgorithm):
    """Wrapper for the main MOBO algorithm with enhanced efficiency."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize MOBO algorithm wrapper.
        
        Args:
            seed: Random seed for reproducible optimization
        """
        super().__init__("This App's MOBO (Enhanced)")
        self.seed = seed
        
    def optimize(self, 
                 test_function,
                 n_evaluations: int,
                 initial_samples: Optional[np.ndarray] = None,
                 gpu_acceleration: bool = True,
                 **kwargs) -> Dict[str, Any]:
        """Run MOBO optimization.
        
        Args:
            test_function: Test function to optimize
            n_evaluations: Number of function evaluations
            initial_samples: Optional initial samples
            gpu_acceleration: Whether to enable GPU acceleration (default: True)
            
        Returns:
            Dictionary containing optimization results
        """
        self.reset()
        
        try:
            from pymbo.core.optimizer import EnhancedMultiObjectiveOptimizer
            
            # Get parameter and response configurations
            params_config = test_function.get_params_config()
            responses_config = test_function.get_responses_config()
            
            # Initialize optimizer with ultra-fast validation mode for benchmarking
            optimizer = EnhancedMultiObjectiveOptimizer(
                params_config=params_config,
                responses_config=responses_config,
                general_constraints=[],
                fast_validation_mode=True,  # Enable ultra-fast mode for validation
                num_restarts=1,  # Minimal restarts for speed
                raw_samples=4,   # Ultra-minimal samples for validation speed
                max_iter=10,     # Limit acquisition optimization iterations
                max_gp_points=50  # Limit GP points for ultra-fast benchmarking
            )
            
            # Apply GPU acceleration if enabled (NEW)
            gpu_acceleration = kwargs.get('gpu_acceleration', True)  # Default enabled
            if gpu_acceleration:
                try:
                    # Import GPU acceleration modules
                    import sys
                    import os
                    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    if current_dir not in sys.path:
                        sys.path.insert(0, current_dir)
                    
                    from scripts.gpu_prediction_acceleration import patch_optimizer_with_gpu_acceleration
                    from scripts.gpu_acquisition_optimization import patch_optimizer_with_gpu_acquisition
                    
                    # Apply both GPU acceleration patches
                    prediction_success = patch_optimizer_with_gpu_acceleration(optimizer)
                    acquisition_success = patch_optimizer_with_gpu_acquisition(optimizer)
                    
                    if prediction_success and acquisition_success:
                        logger.info("🚀 GPU acceleration applied to optimizer (predictions + acquisition)")
                    elif prediction_success:
                        logger.info("🚀 GPU prediction acceleration applied to optimizer")
                    elif acquisition_success:
                        logger.info("🚀 GPU acquisition acceleration applied to optimizer") 
                    else:
                        logger.warning("⚠️ GPU acceleration failed to apply")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Could not apply GPU acceleration: {e}")
            else:
                logger.info("GPU acceleration disabled for this validation")
            
            # Generate initial samples if not provided
            if initial_samples is None:
                n_initial = min(10, max(5, n_evaluations // 10))
                initial_samples = optimizer.suggest_next_experiment(n_suggestions=n_initial)
                
                # Convert suggestions to numpy array
                param_names = list(params_config.keys())
                X_init = np.array([[s[param] for param in param_names] for s in initial_samples])
            else:
                X_init = initial_samples
                n_initial = len(X_init)
                
            # Evaluate initial samples
            Y_init = test_function.evaluate(X_init)
            
            # Create initial DataFrame for optimizer
            param_names = list(params_config.keys())
            response_names = list(responses_config.keys())
            
            data_dict = {}
            for i, param in enumerate(param_names):
                data_dict[param] = X_init[:, i]
            for i, response in enumerate(response_names):
                data_dict[response] = Y_init[:, i]
                
            initial_data = pd.DataFrame(data_dict)
            optimizer.add_experimental_data(initial_data)
            
            # Store initial history
            for i in range(n_initial):
                self.history.append({
                    'X': X_init[:i+1].copy(),
                    'Y': Y_init[:i+1].copy(),
                    'evaluation': i + 1
                })
            
            # Run iterative optimization
            X_all = X_init.copy()
            Y_all = Y_init.copy()
            
            # Run ultra-fast iterative optimization (minimal logging for speed)
            for eval_idx in range(n_initial, n_evaluations):
                # Get next suggestion (core bottleneck - optimize this!)
                suggestion = optimizer.suggest_next_experiment(n_suggestions=1)[0]
                
                # Convert to numpy array and evaluate
                x_next = np.array([[suggestion[param] for param in param_names]])
                y_next = test_function.evaluate(x_next)
                
                # Add to data arrays
                X_all = np.vstack([X_all, x_next])
                Y_all = np.vstack([Y_all, y_next])
                
                # Update optimizer with new data (minimize DataFrame operations)
                new_data_dict = {}
                for i, param in enumerate(param_names):
                    new_data_dict[param] = [x_next[0, i]]
                for i, response in enumerate(response_names):
                    new_data_dict[response] = [y_next[0, i]]
                    
                new_data = pd.DataFrame(new_data_dict)
                optimizer.add_experimental_data(new_data)
                
                # Store minimal history (only every 10 iterations to save memory/time)
                if (eval_idx + 1) % 10 == 0 or eval_idx == n_evaluations - 1:
                    self.history.append({
                        'X': X_all.copy(),
                        'Y': Y_all.copy(),
                        'evaluation': eval_idx + 1
                    })
                
                # Minimal progress reporting (only every 10 iterations)
                if (eval_idx + 1) % 10 == 0 or eval_idx == n_evaluations - 1:
                    progress_pct = ((eval_idx + 1) / n_evaluations) * 100
                    logger.debug(f"MOBO Progress: {eval_idx+1}/{n_evaluations} ({progress_pct:.0f}%)")
                
            return {
                'X': X_all,
                'Y': Y_all,
                'algorithm': self.name,
                'history': self.history,
                'optimizer': optimizer
            }
            
        except Exception as e:
            logger.error(f"MOBO optimization failed: {e}")
            # Fallback to random search
            logger.warning("Falling back to random search")
            random_alg = RandomSearchAlgorithm()
            return random_alg.optimize(test_function, n_evaluations, initial_samples)


# Available algorithms registry
BENCHMARK_ALGORITHMS = {
    "Random Search": RandomSearchAlgorithm,
    "This App's MOBO": MOBOAlgorithm,
}

if PYMOO_AVAILABLE:
    BENCHMARK_ALGORITHMS["NSGA-II"] = NSGAIIAlgorithm

# Add Parallel Branching MOBO if available
try:
    import sys
    import os
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from examples.parallel_branching_optimizer import ParallelBranchingBenchmarkAlgorithm
    BENCHMARK_ALGORITHMS["Parallel Branching MOBO"] = ParallelBranchingBenchmarkAlgorithm
    logger.info("🌳 Parallel Branching MOBO algorithm registered successfully")
except ImportError as e:
    logger.warning(f"⚠️ Parallel Branching MOBO not available: {e}")


def get_benchmark_algorithm(name: str, **kwargs) -> BenchmarkAlgorithm:
    """Get a benchmark algorithm by name.
    
    Args:
        name: Algorithm name
        **kwargs: Arguments for algorithm constructor
        
    Returns:
        Benchmark algorithm instance
        
    Raises:
        ValueError: If algorithm name is not recognized
    """
    if name not in BENCHMARK_ALGORITHMS:
        available = ", ".join(BENCHMARK_ALGORITHMS.keys())
        raise ValueError(f"Unknown algorithm '{name}'. Available: {available}")
        
    return BENCHMARK_ALGORITHMS[name](**kwargs)


def run_benchmark_comparison(test_function,
                           algorithms: List[str],
                           n_evaluations: int,
                           n_runs: int = 10,
                           seed: Optional[int] = None) -> Dict[str, Any]:
    """Run benchmark comparison between multiple algorithms.
    
    Args:
        test_function: Test function to optimize
        algorithms: List of algorithm names to compare
        n_evaluations: Number of function evaluations per run
        n_runs: Number of independent runs for statistical significance
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary containing comparison results
    """
    logger.info(f"Starting benchmark comparison with {len(algorithms)} algorithms, {n_runs} runs")
    
    results = {}
    
    for alg_name in algorithms:
        logger.info(f"Running algorithm: {alg_name}")
        results[alg_name] = []
        
        for run_idx in range(n_runs):
            run_seed = seed + run_idx if seed is not None else None
            
            # Get algorithm instance with appropriate parameters
            if alg_name == "Random Search":
                alg = get_benchmark_algorithm(alg_name, seed=run_seed)
            elif alg_name == "NSGA-II":
                alg = get_benchmark_algorithm(alg_name, seed=run_seed)
            elif alg_name == "Parallel Branching MOBO":
                alg = get_benchmark_algorithm(alg_name, seed=run_seed)
            else:
                alg = get_benchmark_algorithm(alg_name)
                
            # Run optimization
            try:
                result = alg.optimize(test_function, n_evaluations)
                results[alg_name].append(result)
                logger.debug(f"  Run {run_idx + 1}/{n_runs} completed")
            except Exception as e:
                logger.error(f"  Run {run_idx + 1}/{n_runs} failed: {e}")
                # Skip this run
                continue
                
    logger.info("Benchmark comparison completed")
    return results