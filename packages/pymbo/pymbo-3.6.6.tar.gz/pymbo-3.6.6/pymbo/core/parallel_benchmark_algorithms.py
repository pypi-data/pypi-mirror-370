"""
Parallel Benchmark Algorithms - High-Performance Benchmarking with Multiprocessing

This module provides parallel execution of benchmark algorithms at both the
algorithm level and run level, dramatically improving benchmark performance.

Features:
- Parallel execution across different algorithms
- Parallel execution of independent runs
- Intelligent task scheduling and load balancing
- Memory-efficient multiprocessing
- Robust error handling and result aggregation

Author: Multi-Objective Optimization Laboratory
Version: 3.6.6
"""

import logging
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Optional, Any, Tuple
import time
import numpy as np

logger = logging.getLogger(__name__)

def run_single_algorithm_run(algorithm_name: str, 
                           test_function_name: str,
                           n_evaluations: int,
                           run_idx: int,
                           seed: Optional[int] = None) -> Tuple[str, int, Dict]:
    """
    Run a single algorithm run in a separate process.
    This function is called by multiprocessing workers.
    
    Args:
        algorithm_name: Name of the algorithm to run
        test_function_name: Name of the test function
        n_evaluations: Number of evaluations
        run_idx: Run index for identification
        seed: Random seed
        
    Returns:
        Tuple of (algorithm_name, run_idx, result_dict)
    """
    # Import within function for multiprocessing compatibility
    import sys
    import os
    
    # Add the pymbo path to sys.path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    try:
        from .benchmark_algorithms import get_benchmark_algorithm
        from .test_functions import get_test_function
        
        # Set up logging for this process
        logger = logging.getLogger(__name__)
        
        # Get test function
        test_function = get_test_function(test_function_name)
        
        # Get algorithm instance
        run_seed = seed + run_idx if seed is not None else None
        
        if algorithm_name == "Random Search":
            alg = get_benchmark_algorithm(algorithm_name, seed=run_seed)
        elif algorithm_name == "NSGA-II":
            alg = get_benchmark_algorithm(algorithm_name, seed=run_seed)
        else:
            alg = get_benchmark_algorithm(algorithm_name)
        
        # Run optimization
        result = alg.optimize(test_function, n_evaluations)
        
        logger.debug(f"Completed {algorithm_name} run {run_idx + 1}")
        return (algorithm_name, run_idx, result)
        
    except Exception as e:
        logger.error(f"Error in {algorithm_name} run {run_idx + 1}: {e}")
        return (algorithm_name, run_idx, {'error': str(e)})

def run_parallel_benchmark_comparison(test_function_name: str,
                                    algorithms: List[str],
                                    n_evaluations: int,
                                    n_runs: int = 10,
                                    max_workers: Optional[int] = None,
                                    parallel_mode: str = "both",
                                    seed: Optional[int] = None,
                                    progress_callback: Optional[callable] = None) -> Dict[str, Any]:
    """
    Run parallel benchmark comparison between multiple algorithms.
    
    Args:
        test_function_name: Name of test function to optimize
        algorithms: List of algorithm names to compare
        n_evaluations: Number of function evaluations per run
        n_runs: Number of independent runs for statistical significance
        max_workers: Maximum number of parallel workers
        parallel_mode: "algorithms", "runs", or "both"
        seed: Random seed for reproducibility
        progress_callback: Callback for progress updates
        
    Returns:
        Dictionary containing comparison results
    """
    if max_workers is None:
        max_workers = max(1, mp.cpu_count() - 1)
    
    logger.info(f"Starting PARALLEL benchmark comparison: {len(algorithms)} algorithms, "
               f"{n_runs} runs, {max_workers} workers, mode: {parallel_mode}")
    
    start_time = time.time()
    results = {alg: [] for alg in algorithms}
    
    if parallel_mode in ["both", "runs"] and n_runs > 1:
        # Parallel execution at run level
        results = _run_parallel_by_runs(
            test_function_name, algorithms, n_evaluations, n_runs, 
            max_workers, seed, progress_callback
        )
    elif parallel_mode == "algorithms" and len(algorithms) > 1:
        # Parallel execution at algorithm level
        results = _run_parallel_by_algorithms(
            test_function_name, algorithms, n_evaluations, n_runs,
            max_workers, seed, progress_callback
        )
    else:
        # Fallback to sequential
        logger.warning("Falling back to sequential execution")
        from .benchmark_algorithms import run_benchmark_comparison
        from .test_functions import get_test_function
        
        test_function = get_test_function(test_function_name)
        results = run_benchmark_comparison(
            test_function, algorithms, n_evaluations, n_runs, seed
        )
    
    total_time = time.time() - start_time
    logger.info(f"Parallel benchmark comparison completed in {total_time:.2f} seconds")
    
    return results

def _run_parallel_by_runs(test_function_name: str,
                         algorithms: List[str],
                         n_evaluations: int,
                         n_runs: int,
                         max_workers: int,
                         seed: Optional[int],
                         progress_callback: Optional[callable]) -> Dict[str, List]:
    """Run benchmarks with parallelization across runs."""
    results = {alg: [] for alg in algorithms}
    
    # Create all tasks (algorithm, run combinations)
    all_tasks = []
    for alg_name in algorithms:
        for run_idx in range(n_runs):
            all_tasks.append((alg_name, test_function_name, n_evaluations, run_idx, seed))
    
    total_tasks = len(all_tasks)
    completed_tasks = 0
    
    logger.info(f"Executing {total_tasks} tasks across {max_workers} workers")
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_task = {
            executor.submit(run_single_algorithm_run, *task): task 
            for task in all_tasks
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            completed_tasks += 1
            
            try:
                algorithm_name, run_idx, result = future.result()
                
                if 'error' not in result:
                    results[algorithm_name].append(result)
                else:
                    logger.error(f"Task failed: {algorithm_name} run {run_idx + 1}: {result['error']}")
                
                if progress_callback:
                    progress_callback(f"Completed {completed_tasks}/{total_tasks} runs")
                
                logger.debug(f"Completed task {completed_tasks}/{total_tasks}: {algorithm_name} run {run_idx + 1}")
                
            except Exception as e:
                algorithm_name = task[0]
                run_idx = task[3]
                logger.error(f"Error collecting result for {algorithm_name} run {run_idx + 1}: {e}")
    
    return results

def _run_parallel_by_algorithms(test_function_name: str,
                               algorithms: List[str],
                               n_evaluations: int,
                               n_runs: int,
                               max_workers: int,
                               seed: Optional[int],
                               progress_callback: Optional[callable]) -> Dict[str, List]:
    """Run benchmarks with parallelization across algorithms."""
    results = {}
    
    # Create tasks for each algorithm
    algorithm_tasks = [
        (alg, test_function_name, n_evaluations, n_runs, seed) 
        for alg in algorithms
    ]
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit algorithm tasks
        future_to_algorithm = {
            executor.submit(_run_single_algorithm_all_runs, *task): task[0]
            for task in algorithm_tasks
        }
        
        completed = 0
        total_algorithms = len(algorithms)
        
        # Collect results as they complete
        for future in as_completed(future_to_algorithm):
            algorithm_name = future_to_algorithm[future]
            completed += 1
            
            try:
                algorithm_results = future.result()
                results[algorithm_name] = algorithm_results
                
                if progress_callback:
                    progress_callback(f"Completed {algorithm_name} ({completed}/{total_algorithms})")
                
                logger.info(f"Completed algorithm {completed}/{total_algorithms}: {algorithm_name}")
                
            except Exception as e:
                logger.error(f"Error in algorithm {algorithm_name}: {e}")
                results[algorithm_name] = []
    
    return results

def _run_single_algorithm_all_runs(algorithm_name: str,
                                  test_function_name: str,
                                  n_evaluations: int,
                                  n_runs: int,
                                  seed: Optional[int]) -> List[Dict]:
    """
    Run all runs for a single algorithm in a separate process.
    """
    # Import within function for multiprocessing compatibility
    import sys
    import os
    
    # Add the pymbo path to sys.path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    try:
        from .benchmark_algorithms import get_benchmark_algorithm
        from .test_functions import get_test_function
        
        # Set up logging for this process
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {algorithm_name} with {n_runs} runs")
        
        # Get test function
        test_function = get_test_function(test_function_name)
        
        results = []
        
        for run_idx in range(n_runs):
            run_seed = seed + run_idx if seed is not None else None
            
            try:
                # Get algorithm instance
                if algorithm_name == "Random Search":
                    alg = get_benchmark_algorithm(algorithm_name, seed=run_seed)
                elif algorithm_name == "NSGA-II":
                    alg = get_benchmark_algorithm(algorithm_name, seed=run_seed)
                else:
                    alg = get_benchmark_algorithm(algorithm_name)
                
                # Run optimization
                result = alg.optimize(test_function, n_evaluations)
                results.append(result)
                
                logger.debug(f"{algorithm_name} run {run_idx + 1}/{n_runs} completed")
                
            except Exception as e:
                logger.error(f"{algorithm_name} run {run_idx + 1}/{n_runs} failed: {e}")
                continue
        
        logger.info(f"Completed {algorithm_name}: {len(results)}/{n_runs} successful runs")
        return results
        
    except Exception as e:
        logger.error(f"Error in algorithm {algorithm_name}: {e}")
        return []

def estimate_parallel_speedup(n_algorithms: int, 
                            n_runs: int, 
                            max_workers: int,
                            parallel_mode: str = "both") -> float:
    """
    Estimate the speedup factor for parallel processing.
    
    Args:
        n_algorithms: Number of algorithms
        n_runs: Number of runs per algorithm
        max_workers: Number of parallel workers
        parallel_mode: Parallelization mode
        
    Returns:
        Estimated speedup factor
    """
    total_tasks = n_algorithms * n_runs
    
    if parallel_mode == "both" or parallel_mode == "runs":
        # Can parallelize all individual runs
        theoretical_speedup = min(max_workers, total_tasks)
    elif parallel_mode == "algorithms":
        # Can only parallelize across algorithms
        theoretical_speedup = min(max_workers, n_algorithms)
    else:
        theoretical_speedup = 1.0
    
    # Account for overhead (multiprocessing has more overhead than threading)
    if theoretical_speedup > 1:
        efficiency = 0.75  # Conservative estimate
        return theoretical_speedup * efficiency
    else:
        return 1.0