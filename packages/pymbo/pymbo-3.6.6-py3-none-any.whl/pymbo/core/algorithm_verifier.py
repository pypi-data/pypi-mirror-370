"""
Algorithm Verifier - Unified Validation Engine
=============================================

This module provides a single, unified validation engine for algorithm benchmarking
and verification in PyMBO. It replaces all previous validation engines with a clean,
efficient, and well-designed system.

Classes:
    AlgorithmVerifier: Main unified verification engine
    VerificationConfig: Configuration for verification runs
    VerificationResults: Standardized results container

Author: PyMBO Development Team
Version: 3.6.6 - Unified Verification Architecture
"""

import numpy as np
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp

logger = logging.getLogger(__name__)


@dataclass
class VerificationConfig:
    """Configuration for algorithm verification runs."""
    
    test_functions: List[str]
    algorithms: List[str]
    n_evaluations: int
    n_runs: int
    execution_mode: str = "auto"  # auto, parallel, sequential
    gpu_acceleration: bool = True
    n_workers: Optional[int] = None
    seed: Optional[int] = None
    progress_callback: Optional[Callable] = None
    statistical_tests: bool = True
    export_raw_data: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.test_functions:
            raise ValueError("At least one test function must be specified")
        if not self.algorithms:
            raise ValueError("At least one algorithm must be specified")
        if self.n_evaluations < 10:
            raise ValueError("n_evaluations must be at least 10")
        if self.n_runs < 1:
            raise ValueError("n_runs must be at least 1")
        if self.execution_mode not in ["auto", "parallel", "sequential"]:
            raise ValueError("execution_mode must be 'auto', 'parallel', or 'sequential'")


class HypervolumeCalculator:
    """Efficient hypervolume calculation with GPU support."""
    
    def __init__(self, use_gpu: bool = True):
        """Initialize hypervolume calculator.
        
        Args:
            use_gpu: Whether to use GPU acceleration if available
        """
        self.use_gpu = use_gpu
        self._gpu_available = self._check_gpu_availability()
        
    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available."""
        if not self.use_gpu:
            return False
            
        try:
            import cupy as cp
            # Test basic GPU operation
            test_array = cp.array([1, 2, 3])
            _ = cp.sum(test_array)
            return True
        except (ImportError, Exception):
            return False
    
    def calculate_hypervolume(self, 
                            points: np.ndarray,
                            reference_point: Optional[np.ndarray] = None) -> float:
        """Calculate hypervolume indicator efficiently.
        
        Args:
            points: Pareto front points (n_points, n_objectives)
            reference_point: Reference point for hypervolume calculation
            
        Returns:
            Hypervolume value
        """
        # Input validation and preprocessing
        points = self._preprocess_points(points)
        if points.size == 0:
            return 0.0
            
        # Set reference point
        if reference_point is None:
            reference_point = self._compute_reference_point(points)
        
        # Use GPU implementation if available
        if self._gpu_available:
            return self._gpu_hypervolume(points, reference_point)
        else:
            return self._cpu_hypervolume(points, reference_point)
    
    def _preprocess_points(self, points: np.ndarray) -> np.ndarray:
        """Preprocess points for hypervolume calculation."""
        if not isinstance(points, np.ndarray):
            try:
                points = np.array(points, dtype=float)
            except:
                return np.array([])
        
        # Handle empty or invalid points
        if points.size == 0:
            return np.array([])
            
        # Ensure 2D array
        if len(points.shape) == 1:
            points = points.reshape(1, -1)
            
        # Filter out invalid points
        valid_mask = ~(np.isnan(points).any(axis=1) | np.isinf(points).any(axis=1))
        points = points[valid_mask]
        
        return points
    
    def _compute_reference_point(self, points: np.ndarray) -> np.ndarray:
        """Compute appropriate reference point."""
        if points.size == 0:
            return np.array([1.1, 1.1])
            
        # Use max values + 10% margin
        max_vals = np.max(points, axis=0)
        return max_vals * 1.1
    
    def _gpu_hypervolume(self, points: np.ndarray, reference_point: np.ndarray) -> float:
        """GPU-accelerated hypervolume calculation."""
        try:
            import cupy as cp
            
            # Transfer data to GPU
            gpu_points = cp.array(points)
            gpu_ref = cp.array(reference_point)
            
            # Get non-dominated points
            pareto_points = self._gpu_pareto_front(gpu_points)
            
            if len(pareto_points) == 0:
                return 0.0
            
            # Calculate hypervolume based on dimensionality
            if pareto_points.shape[1] == 2:
                hv = self._gpu_hypervolume_2d(pareto_points, gpu_ref)
            else:
                hv = self._gpu_hypervolume_nd(pareto_points, gpu_ref)
            
            return float(cp.asnumpy(hv))
            
        except Exception as e:
            logger.warning(f"GPU hypervolume calculation failed: {e}. Falling back to CPU.")
            return self._cpu_hypervolume(points, reference_point)
    
    def _cpu_hypervolume(self, points: np.ndarray, reference_point: np.ndarray) -> float:
        """CPU hypervolume calculation."""
        # Get non-dominated points
        pareto_points = self._cpu_pareto_front(points)
        
        if len(pareto_points) == 0:
            return 0.0
        
        # Calculate hypervolume based on dimensionality
        if pareto_points.shape[1] == 2:
            return self._cpu_hypervolume_2d(pareto_points, reference_point)
        else:
            return self._cpu_hypervolume_nd(pareto_points, reference_point)
    
    def _cpu_pareto_front(self, points: np.ndarray) -> np.ndarray:
        """Extract Pareto front using CPU."""
        n_points = len(points)
        is_pareto = np.ones(n_points, dtype=bool)
        
        for i in range(n_points):
            for j in range(n_points):
                if i != j and is_pareto[i]:
                    # Check if point i is dominated by point j
                    if np.all(points[j] <= points[i]) and np.any(points[j] < points[i]):
                        is_pareto[i] = False
                        break
        
        return points[is_pareto]
    
    def _gpu_pareto_front(self, points):
        """Extract Pareto front using GPU."""
        import cupy as cp
        
        n_points = len(points)
        is_pareto = cp.ones(n_points, dtype=bool)
        
        # Vectorized dominance check
        for i in range(n_points):
            if is_pareto[i]:
                # Check if point i is dominated by any other point
                dominated = cp.all(points <= points[i], axis=1) & cp.any(points < points[i], axis=1)
                dominated[i] = False  # Don't compare point with itself
                if cp.any(dominated):
                    is_pareto[i] = False
        
        return points[is_pareto]
    
    def _cpu_hypervolume_2d(self, pareto_points: np.ndarray, reference_point: np.ndarray) -> float:
        """Calculate 2D hypervolume using CPU."""
        # Sort points by first objective
        sorted_points = pareto_points[np.argsort(pareto_points[:, 0])]
        
        area = 0.0
        prev_x = 0.0
        
        for point in sorted_points:
            if point[0] < reference_point[0] and point[1] < reference_point[1]:
                width = point[0] - prev_x
                height = reference_point[1] - point[1]
                area += width * height
                prev_x = point[0]
        
        return area
    
    def _gpu_hypervolume_2d(self, pareto_points, reference_point):
        """Calculate 2D hypervolume using GPU."""
        import cupy as cp
        
        # Sort points by first objective
        sorted_indices = cp.argsort(pareto_points[:, 0])
        sorted_points = pareto_points[sorted_indices]
        
        # Vectorized area calculation
        valid_mask = (sorted_points[:, 0] < reference_point[0]) & (sorted_points[:, 1] < reference_point[1])
        valid_points = sorted_points[valid_mask]
        
        if len(valid_points) == 0:
            return 0.0
        
        # Calculate widths and heights
        widths = cp.diff(cp.concatenate([[0], valid_points[:, 0]]))
        heights = reference_point[1] - valid_points[:, 1]
        
        area = cp.sum(widths * heights)
        return area
    
    def _cpu_hypervolume_nd(self, pareto_points: np.ndarray, reference_point: np.ndarray) -> float:
        """Calculate n-dimensional hypervolume approximation using CPU."""
        # Simple bounding box approximation for higher dimensions
        min_vals = np.min(pareto_points, axis=0)
        max_vals = np.minimum(np.max(pareto_points, axis=0), reference_point)
        
        volume = np.prod(np.maximum(0, max_vals - min_vals))
        return volume
    
    def _gpu_hypervolume_nd(self, pareto_points, reference_point):
        """Calculate n-dimensional hypervolume approximation using GPU."""
        import cupy as cp
        
        # Simple bounding box approximation for higher dimensions
        min_vals = cp.min(pareto_points, axis=0)
        max_vals = cp.minimum(cp.max(pareto_points, axis=0), reference_point)
        
        volume = cp.prod(cp.maximum(0, max_vals - min_vals))
        return volume


class VerificationResults:
    """Container for verification results with analysis capabilities."""
    
    def __init__(self, config: VerificationConfig):
        """Initialize results container.
        
        Args:
            config: Verification configuration
        """
        self.config = config
        self.raw_results = {}
        self.hypervolume_progression = {}
        self.statistical_analysis = {}
        self.execution_metadata = {}
        self.performance_metrics = {}
        
    def add_algorithm_results(self, 
                            test_function: str,
                            algorithm: str,
                            results: List[Dict[str, Any]]):
        """Add results for a specific algorithm and test function.
        
        Args:
            test_function: Test function name
            algorithm: Algorithm name  
            results: List of run results
        """
        if test_function not in self.raw_results:
            self.raw_results[test_function] = {}
        self.raw_results[test_function][algorithm] = results
    
    def calculate_hypervolume_progression(self, hv_calculator: HypervolumeCalculator):
        """Calculate hypervolume progression for all results.
        
        Args:
            hv_calculator: Hypervolume calculator instance
        """
        logger.info("Calculating hypervolume progression")
        
        for test_func, algorithms_data in self.raw_results.items():
            self.hypervolume_progression[test_func] = {}
            
            for algorithm, runs in algorithms_data.items():
                progressions = []
                
                for run_data in runs:
                    if 'history' in run_data and run_data['history']:
                        progression = []
                        for entry in run_data['history']:
                            if 'Y' in entry and len(entry['Y']) > 0:
                                hv = hv_calculator.calculate_hypervolume(entry['Y'])
                                progression.append(hv)
                            else:
                                progression.append(0.0)
                        progressions.append(progression)
                
                if progressions:
                    # Standardize progression lengths
                    max_len = max(len(prog) for prog in progressions)
                    standardized_progressions = []
                    
                    for prog in progressions:
                        if len(prog) < max_len:
                            # Extend with last value
                            extended = prog + [prog[-1]] * (max_len - len(prog))
                        else:
                            extended = prog
                        standardized_progressions.append(extended)
                    
                    progressions_array = np.array(standardized_progressions)
                    
                    self.hypervolume_progression[test_func][algorithm] = {
                        'mean': np.mean(progressions_array, axis=0),
                        'std': np.std(progressions_array, axis=0),
                        'all_runs': progressions_array,
                        'evaluations': list(range(1, max_len + 1))
                    }
                else:
                    self.hypervolume_progression[test_func][algorithm] = {
                        'mean': np.array([]),
                        'std': np.array([]),
                        'all_runs': np.array([]),
                        'evaluations': []
                    }
    
    def perform_statistical_analysis(self):
        """Perform statistical analysis on results."""
        logger.info("Performing statistical analysis")
        
        self.statistical_analysis = {
            'final_hypervolumes': {},
            'convergence_analysis': {},
            'algorithm_rankings': {},
            'success_rates': {}
        }
        
        # Analyze final hypervolumes
        for test_func, algorithms_data in self.hypervolume_progression.items():
            self.statistical_analysis['final_hypervolumes'][test_func] = {}
            final_hvs = {}
            
            for algorithm, hv_data in algorithms_data.items():
                if len(hv_data['mean']) > 0:
                    final_mean = hv_data['mean'][-1]
                    final_std = hv_data['std'][-1]
                    
                    self.statistical_analysis['final_hypervolumes'][test_func][algorithm] = {
                        'mean': final_mean,
                        'std': final_std,
                        'runs': len(hv_data['all_runs'])
                    }
                    final_hvs[algorithm] = final_mean
            
            # Rank algorithms by final hypervolume
            if final_hvs:
                ranked = sorted(final_hvs.items(), key=lambda x: x[1], reverse=True)
                self.statistical_analysis['algorithm_rankings'][test_func] = [alg for alg, _ in ranked]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of verification results.
        
        Returns:
            Summary dictionary
        """
        return {
            'config': {
                'test_functions': self.config.test_functions,
                'algorithms': self.config.algorithms,
                'n_evaluations': self.config.n_evaluations,
                'n_runs': self.config.n_runs,
                'execution_mode': self.config.execution_mode
            },
            'execution_metadata': self.execution_metadata,
            'statistical_analysis': self.statistical_analysis,
            'hypervolume_progression': self.hypervolume_progression,
            'performance_metrics': self.performance_metrics
        }
    
    def export_results(self, filepath: str, format: str = 'json'):
        """Export results to file.
        
        Args:
            filepath: Output file path
            format: Export format ('json', 'csv', 'xlsx')
        """
        import json
        
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(self.get_summary(), f, indent=2, default=str)
        elif format == 'csv':
            # Export statistical summary as CSV
            import pandas as pd
            
            summary_data = []
            for test_func, algorithms_data in self.statistical_analysis['final_hypervolumes'].items():
                for algorithm, stats in algorithms_data.items():
                    summary_data.append({
                        'test_function': test_func,
                        'algorithm': algorithm,
                        'final_hypervolume_mean': stats['mean'],
                        'final_hypervolume_std': stats['std'],
                        'n_runs': stats['runs']
                    })
            
            df = pd.DataFrame(summary_data)
            df.to_csv(filepath, index=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")


class AlgorithmVerifier:
    """Unified algorithm verification engine."""
    
    def __init__(self, gpu_acceleration: bool = True, n_workers: Optional[int] = None):
        """Initialize the algorithm verifier.
        
        Args:
            gpu_acceleration: Enable GPU acceleration
            n_workers: Number of worker processes for parallel execution
        """
        self.gpu_acceleration = gpu_acceleration
        self.n_workers = n_workers or max(1, mp.cpu_count() - 1)
        self.hv_calculator = HypervolumeCalculator(use_gpu=gpu_acceleration)
        
        # Import core modules
        self._load_core_modules()
        
        logger.info(f"AlgorithmVerifier initialized - GPU: {gpu_acceleration}, Workers: {self.n_workers}")
    
    def _load_core_modules(self):
        """Load required core modules."""
        try:
            from .test_functions import get_test_function, TEST_FUNCTIONS
            from .benchmark_algorithms import run_benchmark_comparison, BENCHMARK_ALGORITHMS
            
            self.get_test_function = get_test_function
            self.TEST_FUNCTIONS = TEST_FUNCTIONS
            self.run_benchmark_comparison = run_benchmark_comparison
            self.BENCHMARK_ALGORITHMS = BENCHMARK_ALGORITHMS
            
        except ImportError as e:
            logger.error(f"Failed to load core modules: {e}")
            raise
    
    def verify_algorithms(self, config: VerificationConfig) -> VerificationResults:
        """Run algorithm verification with given configuration.
        
        Args:
            config: Verification configuration
            
        Returns:
            Verification results
        """
        logger.info(f"Starting algorithm verification: {len(config.test_functions)} test functions, "
                   f"{len(config.algorithms)} algorithms, {config.n_runs} runs each")
        
        start_time = time.time()
        results = VerificationResults(config)
        
        # Set execution mode
        execution_mode = self._determine_execution_mode(config)
        
        try:
            if execution_mode == "parallel":
                self._run_parallel_verification(config, results)
            else:
                self._run_sequential_verification(config, results)
            
            # Calculate hypervolume progression
            results.calculate_hypervolume_progression(self.hv_calculator)
            
            # Perform statistical analysis
            if config.statistical_tests:
                results.perform_statistical_analysis()
            
            # Record execution metadata
            execution_time = time.time() - start_time
            results.execution_metadata = {
                'execution_mode': execution_mode,
                'execution_time': execution_time,
                'gpu_acceleration': self.gpu_acceleration,
                'n_workers': self.n_workers,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"Verification completed in {execution_time:.2f}s")
            return results
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            raise
    
    def _determine_execution_mode(self, config: VerificationConfig) -> str:
        """Determine optimal execution mode."""
        if config.execution_mode == "sequential":
            return "sequential"
        elif config.execution_mode == "parallel":
            return "parallel"
        else:  # auto
            # Auto-determine based on workload
            total_runs = len(config.test_functions) * len(config.algorithms) * config.n_runs
            if total_runs > 20 and self.n_workers > 1:
                return "parallel"
            else:
                return "sequential"
    
    def _run_sequential_verification(self, config: VerificationConfig, results: VerificationResults):
        """Run verification sequentially."""
        logger.info("Running sequential verification")
        
        total_tasks = len(config.test_functions) * len(config.algorithms)
        completed_tasks = 0
        
        for test_func_name in config.test_functions:
            test_function = self.get_test_function(test_func_name)
            
            for algorithm in config.algorithms:
                logger.debug(f"Running {algorithm} on {test_func_name}")
                
                try:
                    # Run benchmark comparison
                    algorithm_results = self.run_benchmark_comparison(
                        test_function=test_function,
                        algorithms=[algorithm],
                        n_evaluations=config.n_evaluations,
                        n_runs=config.n_runs,
                        seed=config.seed
                    )
                    
                    # Store results
                    if algorithm in algorithm_results:
                        results.add_algorithm_results(
                            test_func_name, algorithm, algorithm_results[algorithm]
                        )
                    
                except Exception as e:
                    logger.error(f"Failed to run {algorithm} on {test_func_name}: {e}")
                    results.add_algorithm_results(test_func_name, algorithm, [])
                
                completed_tasks += 1
                
                # Progress callback
                if config.progress_callback:
                    progress = completed_tasks / total_tasks
                    config.progress_callback(progress, f"{algorithm} on {test_func_name}")
    
    def _run_parallel_verification(self, config: VerificationConfig, results: VerificationResults):
        """Run verification in parallel."""
        logger.info(f"Running parallel verification with {self.n_workers} workers")
        
        # Prepare tasks
        tasks = []
        for test_func_name in config.test_functions:
            for algorithm in config.algorithms:
                tasks.append((test_func_name, algorithm))
        
        completed_tasks = 0
        total_tasks = len(tasks)
        
        # Execute tasks in parallel
        with ThreadPoolExecutor(max_workers=self.n_workers) as executor:
            # Submit all tasks
            future_to_task = {}
            for test_func_name, algorithm in tasks:
                future = executor.submit(
                    self._run_single_verification_task,
                    test_func_name, algorithm, config
                )
                future_to_task[future] = (test_func_name, algorithm)
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                test_func_name, algorithm = future_to_task[future]
                
                try:
                    task_results = future.result()
                    results.add_algorithm_results(test_func_name, algorithm, task_results)
                    
                except Exception as e:
                    logger.error(f"Parallel task failed ({algorithm} on {test_func_name}): {e}")
                    results.add_algorithm_results(test_func_name, algorithm, [])
                
                completed_tasks += 1
                
                # Progress callback
                if config.progress_callback:
                    progress = completed_tasks / total_tasks
                    config.progress_callback(progress, f"{algorithm} on {test_func_name}")
    
    def _run_single_verification_task(self, 
                                    test_func_name: str,
                                    algorithm: str,
                                    config: VerificationConfig) -> List[Dict[str, Any]]:
        """Run a single verification task.
        
        Args:
            test_func_name: Test function name
            algorithm: Algorithm name
            config: Verification configuration
            
        Returns:
            List of run results
        """
        test_function = self.get_test_function(test_func_name)
        
        algorithm_results = self.run_benchmark_comparison(
            test_function=test_function,
            algorithms=[algorithm],
            n_evaluations=config.n_evaluations,
            n_runs=config.n_runs,
            seed=config.seed
        )
        
        return algorithm_results.get(algorithm, [])
    
    def quick_verification(self, 
                         test_function: str = "ZDT1",
                         algorithms: List[str] = None,
                         n_evaluations: int = 50,
                         n_runs: int = 5) -> VerificationResults:
        """Run a quick verification for testing purposes.
        
        Args:
            test_function: Test function name
            algorithms: List of algorithms (default: ["This App's MOBO", "Random Search"])
            n_evaluations: Number of evaluations per run
            n_runs: Number of runs
            
        Returns:
            Verification results
        """
        if algorithms is None:
            algorithms = ["This App's MOBO", "Random Search"]
        
        config = VerificationConfig(
            test_functions=[test_function],
            algorithms=algorithms,
            n_evaluations=n_evaluations,
            n_runs=n_runs,
            execution_mode="auto",
            gpu_acceleration=self.gpu_acceleration
        )
        
        return self.verify_algorithms(config)