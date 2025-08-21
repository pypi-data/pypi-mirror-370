"""
Validation Engine Module - Algorithm Benchmarking and Comparison

This module provides the main validation engine for benchmarking optimization
algorithms against standard test functions. It now leverages the new parallel
validation orchestrator for intelligent execution mode switching and parallel
processing capabilities.

Classes:
    ValidationEngine: Main engine for running benchmark comparisons (Enhanced with parallel orchestrator)
    HypervolumeCalculator: Utility for calculating hypervolume indicators
    EnhancedValidationEngine: New parallel-enabled validation engine

Author: Multi-Objective Optimization Laboratory
Version: 3.6.6 - Parallel Validation Architecture
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)

try:
    from pymbo.core.hypervolume_calculator import HypervolumeCalculator as ExistingHVCalc
    EXISTING_HV_AVAILABLE = True
except ImportError:
    EXISTING_HV_AVAILABLE = False

# Import local modules
from .test_functions import get_test_function, TEST_FUNCTIONS
from .benchmark_algorithms import run_benchmark_comparison, BENCHMARK_ALGORITHMS


class HypervolumeCalculator:
    """Utility class for calculating hypervolume indicators."""
    
    def __init__(self, reference_point: Optional[np.ndarray] = None):
        """Initialize hypervolume calculator.
        
        Args:
            reference_point: Reference point for hypervolume calculation
        """
        self.reference_point = reference_point
        
    def calculate_hypervolume(self, 
                            points: np.ndarray,
                            reference_point: Optional[np.ndarray] = None) -> float:
        """Calculate hypervolume indicator.
        
        Args:
            points: Pareto front points (n_points, n_objectives)
            reference_point: Reference point (if None, uses default)
            
        Returns:
            Hypervolume value
        """
        # Convert points to numpy array if it's not already
        if not isinstance(points, np.ndarray):
            try:
                points = np.array(points)
            except:
                return 0.0
        
        # Handle empty points or wrong dimensions
        if points.size == 0:
            return 0.0
            
        if len(points.shape) == 1:
            points = points.reshape(1, -1)
            
        if len(points.shape) != 2 or points.shape[1] < 2:
            return 0.0
        
        if reference_point is None:
            reference_point = self.reference_point
            
        if reference_point is None:
            # Use default reference point (max values + 10%)
            try:
                reference_point = np.max(points, axis=0) * 1.1
            except:
                # Fallback for edge cases
                reference_point = np.ones(points.shape[1]) * 1.1
            
        # Always use the simple hypervolume calculation to avoid compatibility issues
        return self._simple_hypervolume(points, reference_point)
            
    def _simple_hypervolume(self, points: np.ndarray, reference_point: np.ndarray) -> float:
        """Simple hypervolume calculation for 2D case.
        
        Args:
            points: Pareto front points
            reference_point: Reference point
            
        Returns:
            Hypervolume approximation
        """
        if not isinstance(points, np.ndarray):
            return 0.0
            
        if points.size == 0:
            return 0.0
            
        # Ensure points is 2D array
        if len(points.shape) == 1:
            points = points.reshape(1, -1)
            
        if len(points.shape) != 2 or points.shape[1] < 2:
            return 0.0
            
        if points.shape[1] == 2:
            # For 2D, calculate area under the curve
            # First, get non-dominated points
            pareto_points = self._get_pareto_front(points)
            
            if len(pareto_points) == 0:
                return 0.0
                
            # Sort by first objective
            sorted_points = pareto_points[np.argsort(pareto_points[:, 0])]
            
            # Calculate area
            area = 0.0
            prev_x = 0.0
            
            for point in sorted_points:
                if point.size > 0 and len(point) >= 2:
                    if point[0] < reference_point[0] and point[1] < reference_point[1]:
                        width = point[0] - prev_x
                        height = reference_point[1] - point[1]
                        area += width * height
                        prev_x = point[0]
                    
            return area
        else:
            # For higher dimensions, use volume of bounding box as approximation
            pareto_points = self._get_pareto_front(points)
            if len(pareto_points) == 0:
                return 0.0
                
            # Calculate volume of bounding box
            min_vals = np.min(pareto_points, axis=0)
            max_vals = np.min([np.max(pareto_points, axis=0), reference_point], axis=0)
            
            volume = np.prod(np.maximum(0, max_vals - min_vals))
            return volume
            
    def _get_pareto_front(self, points: np.ndarray) -> np.ndarray:
        """Get non-dominated points (Pareto front).
        
        Args:
            points: Input points
            
        Returns:
            Non-dominated points
        """
        n_points = len(points)
        is_pareto = np.ones(n_points, dtype=bool)
        
        for i in range(n_points):
            for j in range(n_points):
                if i != j:
                    # Check if point i is dominated by point j
                    if np.all(points[j] <= points[i]) and np.any(points[j] < points[i]):
                        is_pareto[i] = False
                        break
                        
        return points[is_pareto]


class ValidationEngine:
    """Main validation engine for algorithm benchmarking."""
    
    def __init__(self, reference_point: Optional[np.ndarray] = None):
        """Initialize validation engine.
        
        Args:
            reference_point: Reference point for hypervolume calculation
        """
        self.hv_calculator = HypervolumeCalculator(reference_point)
        self.results = {}
        
    def run_validation(self,
                      test_function_name: str,
                      algorithms: List[str],
                      n_evaluations: int,
                      n_runs: int = 10,
                      seed: Optional[int] = None,
                      test_function_kwargs: Optional[Dict] = None) -> Dict[str, Any]:
        """Run validation benchmark.
        
        Args:
            test_function_name: Name of test function to use
            algorithms: List of algorithm names to compare
            n_evaluations: Number of function evaluations per run
            n_runs: Number of independent runs
            seed: Random seed for reproducibility
            test_function_kwargs: Additional arguments for test function
            
        Returns:
            Validation results dictionary
        """
        logger.info(f"Starting validation: {test_function_name} with {algorithms}")
        
        # Get test function
        if test_function_kwargs is None:
            test_function_kwargs = {}
        test_function = get_test_function(test_function_name, **test_function_kwargs)
        
        # Run benchmark comparison
        benchmark_results = run_benchmark_comparison(
            test_function=test_function,
            algorithms=algorithms,
            n_evaluations=n_evaluations,
            n_runs=n_runs,
            seed=seed
        )
        
        # Calculate hypervolume progression for each algorithm
        hv_results = self._calculate_hypervolume_progression(
            benchmark_results, test_function
        )
        
        # Compile final results
        validation_results = {
            'test_function': test_function_name,
            'algorithms': algorithms,
            'n_evaluations': n_evaluations,
            'n_runs': n_runs,
            'benchmark_results': benchmark_results,
            'hypervolume_results': hv_results,
            'test_function_obj': test_function
        }
        
        self.results = validation_results
        logger.info("Validation completed successfully")
        
        return validation_results
        
    def _calculate_hypervolume_progression(self,
                                         benchmark_results: Dict[str, List],
                                         test_function) -> Dict[str, Any]:
        """Calculate hypervolume progression for all algorithms.
        
        Args:
            benchmark_results: Raw benchmark results
            test_function: Test function instance
            
        Returns:
            Hypervolume progression results
        """
        logger.info("Calculating hypervolume progression")
        
        hv_results = {}
        
        # Set reference point based on test function
        if hasattr(test_function, 'get_true_pareto_front'):
            try:
                true_pf = test_function.get_true_pareto_front(100)
                reference_point = np.max(true_pf, axis=0) * 1.1
            except:
                reference_point = None
        else:
            reference_point = None
            
        for alg_name, alg_runs in benchmark_results.items():
            logger.debug(f"Processing hypervolume for {alg_name}")
            
            all_progressions = []
            
            for run_result in alg_runs:
                if 'history' in run_result:
                    progression = []
                    
                    for hist_entry in run_result['history']:
                        Y = hist_entry['Y']
                        
                        # Calculate hypervolume
                        if len(Y) > 0:
                            hv = self.hv_calculator.calculate_hypervolume(Y, reference_point)
                        else:
                            hv = 0.0
                            
                        progression.append(hv)
                        
                    all_progressions.append(progression)
                    
            if all_progressions:
                # Convert to numpy array for easier processing
                max_len = max(len(prog) for prog in all_progressions)
                
                # Pad progressions to same length and ensure all elements are numeric
                padded_progressions = []
                for prog in all_progressions:
                    # Convert to list of floats
                    numeric_prog = [float(x) if isinstance(x, (int, float, np.number)) else 0.0 for x in prog]
                    
                    if len(numeric_prog) < max_len:
                        # Pad with last value
                        last_val = numeric_prog[-1] if numeric_prog else 0.0
                        padded = numeric_prog + [last_val] * (max_len - len(numeric_prog))
                    else:
                        padded = numeric_prog
                    padded_progressions.append(padded)
                    
                progressions_array = np.array(padded_progressions, dtype=float)
                
                # Calculate statistics
                mean_progression = np.mean(progressions_array, axis=0)
                std_progression = np.std(progressions_array, axis=0)
                
                hv_results[alg_name] = {
                    'mean': mean_progression,
                    'std': std_progression,
                    'all_runs': progressions_array,
                    'evaluations': list(range(1, len(mean_progression) + 1))
                }
            else:
                logger.warning(f"No progression data for {alg_name}")
                hv_results[alg_name] = {
                    'mean': [],
                    'std': [],
                    'all_runs': [],
                    'evaluations': []
                }
                
        return hv_results
        
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics from the last validation run.
        
        Returns:
            Summary statistics dictionary
        """
        if not self.results:
            return {}
            
        summary = {
            'test_function': self.results['test_function'],
            'algorithms': self.results['algorithms'],
            'final_hypervolumes': {},
            'convergence_rates': {},
            'statistical_significance': {}
        }
        
        hv_results = self.results['hypervolume_results']
        
        for alg_name in self.results['algorithms']:
            if alg_name in hv_results:
                mean_prog = hv_results[alg_name]['mean']
                if len(mean_prog) > 0:
                    summary['final_hypervolumes'][alg_name] = {
                        'mean': float(mean_prog[-1]),
                        'std': float(hv_results[alg_name]['std'][-1])
                    }
                    
                    # Simple convergence rate (slope of last 20% of progression)
                    if len(mean_prog) > 10:
                        n_points = max(5, len(mean_prog) // 5)
                        recent_prog = mean_prog[-n_points:]
                        x = np.arange(len(recent_prog))
                        slope = np.polyfit(x, recent_prog, 1)[0]
                        summary['convergence_rates'][alg_name] = float(slope)
                        
        return summary


def create_validation_report(validation_results: Dict[str, Any]) -> str:
    """Create a text report from validation results.
    
    Args:
        validation_results: Results from ValidationEngine.run_validation()
        
    Returns:
        Formatted text report
    """
    report = []
    report.append("=" * 60)
    report.append("ALGORITHM VALIDATION REPORT")
    report.append("=" * 60)
    report.append("")
    
    # Basic information
    report.append(f"Test Function: {validation_results['test_function']}")
    report.append(f"Algorithms: {', '.join(validation_results['algorithms'])}")
    report.append(f"Evaluations per Run: {validation_results['n_evaluations']}")
    report.append(f"Number of Runs: {validation_results['n_runs']}")
    report.append("")
    
    # Final hypervolume results
    report.append("FINAL HYPERVOLUME RESULTS:")
    report.append("-" * 30)
    
    hv_results = validation_results['hypervolume_results']
    for alg_name in validation_results['algorithms']:
        if alg_name in hv_results:
            mean_prog = hv_results[alg_name]['mean']
            std_prog = hv_results[alg_name]['std']
            if len(mean_prog) > 0:
                final_mean = mean_prog[-1]
                final_std = std_prog[-1]
                report.append(f"{alg_name:20s}: {final_mean:.6f} ± {final_std:.6f}")
            else:
                report.append(f"{alg_name:20s}: No data")
        else:
            report.append(f"{alg_name:20s}: Failed")
            
    report.append("")
    report.append("=" * 60)
    
    return "\n".join(report)


# ====================================================================================
# Enhanced Validation Engine with Parallel Orchestrator
# ====================================================================================

class EnhancedValidationEngine:
    """
    Legacy enhanced validation engine - DEPRECATED.
    
    This class is maintained for backward compatibility only.
    Use the new AlgorithmVerifier for new implementations.
    """
    
    def __init__(self, 
                 enable_parallel: bool = True,
                 n_workers: Optional[int] = None,
                 reference_point: Optional[np.ndarray] = None):
        """
        Initialize the legacy enhanced validation engine.
        
        Args:
            enable_parallel: Enable parallel execution
            n_workers: Number of worker processes
            reference_point: Reference point for hypervolume calculation
        """
        logger.warning("EnhancedValidationEngine is deprecated. Use AlgorithmVerifier instead.")
        
        # Fallback to standard validation engine
        self.orchestrator = None
        self.orchestrator_available = False
        self.fallback_engine = ValidationEngine(reference_point)
        self.results = {}
    
    def run_validation(self,
                      test_function_name: str,
                      algorithms: List[str],
                      n_evaluations: int,
                      n_runs: int = 10,
                      seed: Optional[int] = None,
                      test_function_kwargs: Optional[Dict] = None,
                      parallel: bool = True) -> Dict[str, Any]:
        """
        Run validation using fallback engine (deprecated method).
        
        Args:
            test_function_name: Name of test function to use
            algorithms: List of algorithm names to compare
            n_evaluations: Number of function evaluations per run
            n_runs: Number of independent runs
            seed: Random seed for reproducibility
            test_function_kwargs: Additional arguments for test function
            parallel: Enable parallel execution (ignored)
            
        Returns:
            Validation results dictionary
        """
        logger.info("Using fallback validation engine")
        return self.fallback_engine.run_validation(
            test_function_name=test_function_name,
            algorithms=algorithms,
            n_evaluations=n_evaluations,
            n_runs=n_runs,
            seed=seed,
            test_function_kwargs=test_function_kwargs
        )
    
    def run_batch_validation(self,
                           test_functions: List[str],
                           algorithms: List[str],
                           n_evaluations: int,
                           n_runs: int = 10,
                           seed: Optional[int] = None,
                           parallel: bool = True) -> Dict[str, Any]:
        """
        Run batch validation (deprecated - use AlgorithmVerifier instead).
        """
        logger.warning("run_batch_validation is deprecated. Use AlgorithmVerifier instead.")
        
        batch_results = {}
        for test_func_name in test_functions:
            try:
                result = self.run_validation(
                    test_function_name=test_func_name,
                    algorithms=algorithms,
                    n_evaluations=n_evaluations,
                    n_runs=n_runs,
                    seed=seed
                )
                batch_results[test_func_name] = result
            except Exception as e:
                logger.error(f"Batch validation failed for {test_func_name}: {e}")
                batch_results[test_func_name] = {'error': str(e)}
        
        return {
            'batch_results': batch_results,
            'test_functions': test_functions,
            'algorithms': algorithms
        }
    
    def benchmark_strategies_quick(self,
                                 algorithms: List[str],
                                 test_function: str = "ZDT1",
                                 n_evaluations: int = 50,
                                 n_runs: int = 5) -> Dict[str, Any]:
        """
        Quick benchmarking (deprecated - use AlgorithmVerifier instead).
        """
        logger.warning("benchmark_strategies_quick is deprecated. Use AlgorithmVerifier instead.")
        
        return self.run_validation(
            test_function_name=test_function,
            algorithms=algorithms,
            n_evaluations=n_evaluations,
            n_runs=n_runs
        )
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics (deprecated)."""
        if hasattr(self.fallback_engine, 'get_summary_statistics'):
            return self.fallback_engine.get_summary_statistics()
        else:
            return {}
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics (deprecated)."""
        return {'error': 'Enhanced orchestrator not available - use AlgorithmVerifier instead'}


# Convenience function for creating enhanced validation engine
def create_enhanced_validation_engine(enable_parallel: bool = True,
                                     n_workers: Optional[int] = None) -> EnhancedValidationEngine:
    """
    Create an enhanced validation engine instance.
    
    Args:
        enable_parallel: Enable parallel execution
        n_workers: Number of worker processes
        
    Returns:
        EnhancedValidationEngine instance
    """
    return EnhancedValidationEngine(enable_parallel=enable_parallel, n_workers=n_workers)


# Export the enhanced engine as the default
DefaultValidationEngine = EnhancedValidationEngine