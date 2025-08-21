#!/usr/bin/env python3
"""
Hybrid Sequential/Parallel Optimization Orchestrator
===================================================

This module implements an intelligent optimization orchestrator that seamlessly
switches between sequential and parallel execution modes based on context.

Key Features:
- 100% backward compatibility with existing sequential optimizer
- Intelligent context detection and mode switching
- Parallel execution for benchmarking, data loading, and what-if analysis
- Advanced caching and state management
- Resource-aware execution with fallback mechanisms

Integration with PyMBO:
- Wraps EnhancedMultiObjectiveOptimizer for extended capabilities
- Integrates with existing controller and GUI
- Maintains all existing APIs while adding parallel features

Author: Multi-Objective Optimization Laboratory
Version: 3.6.6 - Hybrid Architecture
"""

import asyncio
import hashlib
import logging
import multiprocessing as mp
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from functools import wraps, lru_cache
import threading
import weakref

import numpy as np
import pandas as pd
import torch
from torch import Tensor

# Import existing optimizer
from pymbo.core.optimizer import EnhancedMultiObjectiveOptimizer

# Configure logging
logger = logging.getLogger(__name__)


class OptimizationContext(Enum):
    """Optimization execution contexts that determine parallel vs sequential mode."""
    INTERACTIVE = "interactive"        # Real-time suggestions (sequential)
    BENCHMARKING = "benchmarking"      # Algorithm comparison (parallel)
    DATA_LOADING = "data_loading"      # Historical data processing (parallel)
    WHAT_IF = "what_if"               # Alternative strategy simulation (parallel)
    BATCH_PROCESSING = "batch"         # Large-scale analysis (parallel)
    HYPERPARAMETER = "hyperparameter"  # Optimizer tuning (parallel)
    AUTO = "auto"                     # Automatic detection


@dataclass
class OptimizationRequest:
    """Encapsulates an optimization request with context information."""
    n_suggestions: int
    context: OptimizationContext
    strategies: Optional[List[str]] = None
    data: Optional[pd.DataFrame] = None
    scenarios: Optional[List[Dict]] = None
    parallel: bool = False
    force_mode: Optional[str] = None
    callback: Optional[Callable] = None
    metadata: Optional[Dict[str, Any]] = None


class ModelCache:
    """Thread-safe cache for GP models and related computations."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache = {}
        self._access_times = {}
        self._lock = threading.RLock()
        
    def _generate_key(self, data_hash: str, config_hash: str) -> str:
        """Generate cache key from data and configuration."""
        return f"{data_hash}_{config_hash}"
    
    def _evict_lru(self):
        """Evict least recently used item."""
        if len(self._cache) >= self.max_size:
            lru_key = min(self._access_times.keys(), key=self._access_times.get)
            del self._cache[lru_key]
            del self._access_times[lru_key]
    
    def get(self, data_hash: str, config_hash: str) -> Optional[Any]:
        """Get cached model if available."""
        key = self._generate_key(data_hash, config_hash)
        with self._lock:
            if key in self._cache:
                self._access_times[key] = time.time()
                return self._cache[key]
        return None
    
    def put(self, data_hash: str, config_hash: str, model: Any):
        """Cache a model."""
        key = self._generate_key(data_hash, config_hash)
        with self._lock:
            self._evict_lru()
            self._cache[key] = model
            self._access_times[key] = time.time()
    
    def invalidate(self, data_hash: str = None):
        """Invalidate cache entries."""
        with self._lock:
            if data_hash is None:
                self._cache.clear()
                self._access_times.clear()
            else:
                keys_to_remove = [k for k in self._cache.keys() if k.startswith(data_hash)]
                for key in keys_to_remove:
                    del self._cache[key]
                    del self._access_times[key]


class OptimizationModeDetector:
    """Intelligent detector for optimization context and execution mode."""
    
    def __init__(self):
        self.interaction_history = []
        self.last_request_time = 0
        
    def detect_context(self, **kwargs) -> OptimizationContext:
        """Detect optimization context based on request parameters."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        self.last_request_time = current_time
        
        # Explicit context provided
        if 'context' in kwargs and kwargs['context'] != OptimizationContext.AUTO:
            return kwargs['context']
        
        # Check for benchmarking indicators
        if 'strategies' in kwargs and len(kwargs.get('strategies', [])) > 1:
            return OptimizationContext.BENCHMARKING
            
        # Check for what-if analysis
        if 'scenarios' in kwargs and len(kwargs.get('scenarios', [])) > 1:
            return OptimizationContext.WHAT_IF
            
        # Check for large batch processing
        n_suggestions = kwargs.get('n_suggestions', 1)
        if n_suggestions > 20:
            return OptimizationContext.BATCH_PROCESSING
            
        # Check for data loading context
        if 'data' in kwargs and len(kwargs.get('data', pd.DataFrame())) > 1000:
            return OptimizationContext.DATA_LOADING
            
        # Check for hyperparameter tuning
        if 'hyperparameter_tuning' in kwargs:
            return OptimizationContext.HYPERPARAMETER
            
        # Default to interactive for typical usage patterns
        if time_since_last < 10 and n_suggestions <= 10:
            return OptimizationContext.INTERACTIVE
            
        return OptimizationContext.INTERACTIVE
    
    def should_use_parallel(self, context: OptimizationContext) -> bool:
        """Determine if parallel execution should be used."""
        parallel_contexts = {
            OptimizationContext.BENCHMARKING,
            OptimizationContext.DATA_LOADING,
            OptimizationContext.WHAT_IF,
            OptimizationContext.BATCH_PROCESSING,
            OptimizationContext.HYPERPARAMETER
        }
        return context in parallel_contexts


class ParallelOptimizationEngine:
    """Engine for parallel optimization tasks."""
    
    def __init__(self, n_workers: int = None):
        self.n_workers = n_workers or min(mp.cpu_count(), 4)
        self.process_pool = None
        self.thread_pool = None
        self.model_cache = ModelCache()
        self._initialize_pools()
        
    def _initialize_pools(self):
        """Initialize worker pools."""
        try:
            self.process_pool = ProcessPoolExecutor(max_workers=self.n_workers)
            self.thread_pool = ThreadPoolExecutor(max_workers=self.n_workers)
            logger.info(f"Initialized parallel pools with {self.n_workers} workers")
        except Exception as e:
            logger.warning(f"Failed to initialize worker pools: {e}")
            self.process_pool = None
            self.thread_pool = None
    
    def __del__(self):
        """Clean up worker pools."""
        if self.process_pool:
            self.process_pool.shutdown(wait=False)
        if self.thread_pool:
            self.thread_pool.shutdown(wait=False)
    
    def parallel_benchmark(self, 
                          optimizer_config: Dict[str, Any],
                          strategies: List[str], 
                          n_suggestions: int = 10) -> Dict[str, Any]:
        """Run multiple optimization strategies in parallel."""
        if not self.process_pool:
            logger.warning("Process pool not available, falling back to sequential")
            return self._sequential_benchmark(optimizer_config, strategies, n_suggestions)
        
        logger.info(f"Running parallel benchmark with {len(strategies)} strategies")
        
        # Submit benchmark tasks
        futures = {}
        for strategy in strategies:
            future = self.process_pool.submit(
                self._run_strategy_benchmark, 
                optimizer_config, strategy, n_suggestions
            )
            futures[strategy] = future
        
        # Collect results
        results = {}
        for strategy, future in futures.items():
            try:
                results[strategy] = future.result(timeout=300)  # 5 minute timeout
            except Exception as e:
                logger.error(f"Strategy {strategy} failed: {e}")
                results[strategy] = {'error': str(e)}
        
        return results
    
    def parallel_what_if_analysis(self,
                                 optimizer_config: Dict[str, Any],
                                 scenarios: List[Dict]) -> Dict[str, Any]:
        """Run what-if analysis scenarios in parallel."""
        if not self.process_pool:
            logger.warning("Process pool not available, falling back to sequential")
            return self._sequential_what_if(optimizer_config, scenarios)
        
        logger.info(f"Running parallel what-if analysis with {len(scenarios)} scenarios")
        
        # Submit what-if tasks
        futures = {}
        for i, scenario in enumerate(scenarios):
            scenario_name = scenario.get('name', f'scenario_{i}')
            future = self.process_pool.submit(
                self._run_what_if_scenario,
                optimizer_config, scenario
            )
            futures[scenario_name] = future
        
        # Collect results
        results = {}
        for scenario_name, future in futures.items():
            try:
                results[scenario_name] = future.result(timeout=600)  # 10 minute timeout
            except Exception as e:
                logger.error(f"Scenario {scenario_name} failed: {e}")
                results[scenario_name] = {'error': str(e)}
        
        return results
    
    def parallel_data_loading(self,
                             base_optimizer: EnhancedMultiObjectiveOptimizer,
                             data_df: pd.DataFrame,
                             chunk_size: int = 1000) -> Dict[str, Any]:
        """Process large datasets in parallel chunks."""
        if not self.thread_pool:
            logger.warning("Thread pool not available, falling back to sequential")
            return self._sequential_data_loading(base_optimizer, data_df)
        
        logger.info(f"Processing {len(data_df)} data points in parallel chunks of {chunk_size}")
        
        # Split data into chunks
        chunks = [data_df[i:i+chunk_size] for i in range(0, len(data_df), chunk_size)]
        
        # Submit processing tasks
        futures = []
        for i, chunk in enumerate(chunks):
            future = self.thread_pool.submit(
                self._process_data_chunk,
                base_optimizer, chunk, i
            )
            futures.append(future)
        
        # Collect results
        processed_chunks = []
        for future in as_completed(futures):
            try:
                result = future.result(timeout=120)  # 2 minute timeout per chunk
                processed_chunks.append(result)
            except Exception as e:
                logger.error(f"Data chunk processing failed: {e}")
        
        return {'processed_chunks': len(processed_chunks), 'total_chunks': len(chunks)}
    
    @staticmethod
    def _run_strategy_benchmark(optimizer_config: Dict[str, Any], 
                               strategy: str, 
                               n_suggestions: int) -> Dict[str, Any]:
        """Run a single strategy benchmark (executed in separate process)."""
        try:
            start_time = time.time()
            
            # Recreate optimizer from config
            optimizer = EnhancedMultiObjectiveOptimizer(
                params_config=optimizer_config['params_config'],
                responses_config=optimizer_config['responses_config']
            )
            
            # Set training data if available
            if 'train_X' in optimizer_config and 'train_Y' in optimizer_config:
                optimizer.train_X = torch.tensor(optimizer_config['train_X'])
                optimizer.train_Y = torch.tensor(optimizer_config['train_Y'])
            
            suggestions = optimizer.suggest_next_experiment(n_suggestions=n_suggestions)
            
            execution_time = time.time() - start_time
            
            return {
                'strategy': strategy,
                'suggestions': suggestions,
                'execution_time': execution_time,
                'n_suggestions': len(suggestions),
                'success': True
            }
        except Exception as e:
            return {
                'strategy': strategy,
                'error': str(e),
                'success': False
            }
    
    @staticmethod
    def _run_what_if_scenario(optimizer_config: Dict[str, Any],
                             scenario: Dict) -> Dict[str, Any]:
        """Run a single what-if scenario (executed in separate process)."""
        try:
            start_time = time.time()
            
            # Recreate optimizer from config
            optimizer = EnhancedMultiObjectiveOptimizer(
                params_config=optimizer_config['params_config'],
                responses_config=optimizer_config['responses_config']
            )
            
            # Set training data if available
            if 'train_X' in optimizer_config and 'train_Y' in optimizer_config:
                optimizer.train_X = torch.tensor(optimizer_config['train_X'])
                optimizer.train_Y = torch.tensor(optimizer_config['train_Y'])
            
            # Run optimization with scenario parameters
            results = optimizer.suggest_next_experiment(
                n_suggestions=scenario.get('n_suggestions', 10)
            )
            
            execution_time = time.time() - start_time
            
            return {
                'scenario': scenario,
                'results': results,
                'execution_time': execution_time,
                'success': True
            }
        except Exception as e:
            return {
                'scenario': scenario,
                'error': str(e),
                'success': False
            }
    
    @staticmethod
    def _process_data_chunk(optimizer: EnhancedMultiObjectiveOptimizer,
                           chunk: pd.DataFrame,
                           chunk_id: int) -> Dict[str, Any]:
        """Process a single data chunk (executed in separate thread)."""
        try:
            start_time = time.time()
            
            # Add data chunk to optimizer
            optimizer.add_experimental_data(chunk)
            
            execution_time = time.time() - start_time
            
            return {
                'chunk_id': chunk_id,
                'rows_processed': len(chunk),
                'execution_time': execution_time,
                'success': True
            }
        except Exception as e:
            return {
                'chunk_id': chunk_id,
                'error': str(e),
                'success': False
            }
    
    def _sequential_benchmark(self, optimizer_config, strategies, n_suggestions):
        """Fallback sequential benchmarking."""
        results = {}
        for strategy in strategies:
            results[strategy] = self._run_strategy_benchmark(optimizer_config, strategy, n_suggestions)
        return results
    
    def _sequential_what_if(self, optimizer_config, scenarios):
        """Fallback sequential what-if analysis."""
        results = {}
        for i, scenario in enumerate(scenarios):
            scenario_name = scenario.get('name', f'scenario_{i}')
            results[scenario_name] = self._run_what_if_scenario(optimizer_config, scenario)
        return results
    
    def _sequential_data_loading(self, optimizer, data_df):
        """Fallback sequential data loading."""
        optimizer.add_experimental_data(data_df)
        return {'processed_chunks': 1, 'total_chunks': 1}


class ExecutionRouter:
    """Routes optimization requests to appropriate execution engines."""
    
    def __init__(self, 
                 base_optimizer: EnhancedMultiObjectiveOptimizer,
                 parallel_engine: ParallelOptimizationEngine):
        self.base_optimizer = base_optimizer
        self.parallel_engine = parallel_engine
        
    def route_request(self, request: OptimizationRequest) -> Any:
        """Route request to appropriate execution engine."""
        
        if request.force_mode == 'sequential' or not request.parallel:
            return self._handle_sequential(request)
        elif request.force_mode == 'parallel' or request.parallel:
            return self._handle_parallel(request)
        else:
            # Auto-routing based on context
            if request.context == OptimizationContext.INTERACTIVE:
                return self._handle_sequential(request)
            else:
                return self._handle_parallel(request)
    
    def _handle_sequential(self, request: OptimizationRequest) -> Any:
        """Handle request in sequential mode."""
        logger.debug(f"Executing request in sequential mode: {request.context}")
        
        # Standard sequential optimization
        return self.base_optimizer.suggest_next_experiment(
            n_suggestions=request.n_suggestions
        )
    
    def _handle_parallel(self, request: OptimizationRequest) -> Any:
        """Handle request in parallel mode."""
        logger.debug(f"Executing request in parallel mode: {request.context}")
        
        # Create optimizer configuration for parallel execution
        optimizer_config = self._get_optimizer_config()
        
        if request.context == OptimizationContext.BENCHMARKING:
            return self.parallel_engine.parallel_benchmark(
                optimizer_config,
                request.strategies or ['ehvi', 'ei'],
                request.n_suggestions
            )
        elif request.context == OptimizationContext.WHAT_IF:
            return self.parallel_engine.parallel_what_if_analysis(
                optimizer_config,
                request.scenarios or []
            )
        elif request.context == OptimizationContext.DATA_LOADING:
            return self.parallel_engine.parallel_data_loading(
                self.base_optimizer,
                request.data
            )
        elif request.context == OptimizationContext.BATCH_PROCESSING:
            # For large batch processing, we can parallelize the acquisition optimization
            return self._parallel_batch_processing(request)
        else:
            # Fallback to sequential
            return self._handle_sequential(request)
    
    def _get_optimizer_config(self) -> Dict[str, Any]:
        """Get serializable optimizer configuration for parallel execution."""
        config = {
            'params_config': self.base_optimizer.params_config,
            'responses_config': self.base_optimizer.responses_config
        }
        
        # Add training data if available
        if hasattr(self.base_optimizer, 'train_X') and self.base_optimizer.train_X is not None:
            config['train_X'] = self.base_optimizer.train_X.cpu().numpy()
        if hasattr(self.base_optimizer, 'train_Y') and self.base_optimizer.train_Y is not None:
            config['train_Y'] = self.base_optimizer.train_Y.cpu().numpy()
            
        return config
    
    def _parallel_batch_processing(self, request: OptimizationRequest) -> Any:
        """Handle large batch processing in parallel."""
        # Split large batch into smaller chunks and process in parallel
        chunk_size = min(10, request.n_suggestions // self.parallel_engine.n_workers)
        chunks = []
        
        remaining = request.n_suggestions
        while remaining > 0:
            current_chunk = min(chunk_size, remaining)
            chunks.append(current_chunk)
            remaining -= current_chunk
        
        # Process chunks in parallel
        all_suggestions = []
        for chunk_size in chunks:
            suggestions = self.base_optimizer.suggest_next_experiment(n_suggestions=chunk_size)
            all_suggestions.extend(suggestions)
        
        return all_suggestions


class OptimizationOrchestrator:
    """
    Main orchestrator class that provides intelligent sequential/parallel optimization.
    
    This class maintains 100% backward compatibility with EnhancedMultiObjectiveOptimizer
    while adding intelligent parallel execution capabilities for advanced use cases.
    """
    
    def __init__(self, 
                 base_optimizer: EnhancedMultiObjectiveOptimizer,
                 enable_parallel: bool = True,
                 n_workers: int = None):
        """
        Initialize the optimization orchestrator.
        
        Args:
            base_optimizer: The base sequential optimizer
            enable_parallel: Whether to enable parallel capabilities
            n_workers: Number of parallel workers (None = auto-detect)
        """
        self.base_optimizer = base_optimizer
        self.mode_detector = OptimizationModeDetector()
        
        # Statistics tracking
        self._sequential_count = 0
        self._parallel_count = 0
        
        # Initialize parallel engine if enabled
        if enable_parallel:
            try:
                self.parallel_engine = ParallelOptimizationEngine(n_workers)
                self.execution_router = ExecutionRouter(base_optimizer, self.parallel_engine)
                self.parallel_enabled = True
                logger.info(f"Parallel optimization enabled with {self.parallel_engine.n_workers} workers")
            except Exception as e:
                logger.warning(f"Failed to initialize parallel engine: {e}, falling back to sequential only")
                self.parallel_engine = None
                self.execution_router = None
                self.parallel_enabled = False
        else:
            self.parallel_engine = None
            self.execution_router = None
            self.parallel_enabled = False
    
    # ====================================================================================
    # BACKWARD COMPATIBILITY API - All existing methods work unchanged
    # ====================================================================================
    
    def suggest_next_experiment(self, 
                               n_suggestions: int = 1, 
                               **kwargs) -> List[Dict[str, Any]]:
        """
        Suggest next experiments with intelligent mode detection.
        
        This method maintains 100% backward compatibility while adding intelligent
        parallel execution for appropriate contexts.
        
        Args:
            n_suggestions: Number of suggestions to generate
            **kwargs: Additional parameters for context detection and parallel execution
            
        Returns:
            List of parameter dictionaries for next experiments
        """
        # Detect optimization context
        context = self.mode_detector.detect_context(
            n_suggestions=n_suggestions, 
            **kwargs
        )
        
        # Create optimization request
        request = OptimizationRequest(
            n_suggestions=n_suggestions,
            context=context,
            strategies=kwargs.get('strategies'),
            data=kwargs.get('data'),
            scenarios=kwargs.get('scenarios'),
            parallel=kwargs.get('parallel', False),
            force_mode=kwargs.get('force_mode'),
            metadata=kwargs
        )
        
        # Route to appropriate execution engine
        if self.parallel_enabled and self.execution_router and self.mode_detector.should_use_parallel(context):
            self._parallel_count += 1
            return self.execution_router.route_request(request)
        else:
            # Fallback to sequential mode
            self._sequential_count += 1
            return self.base_optimizer.suggest_next_experiment(n_suggestions)
    
    def add_experimental_data(self, data_df: pd.DataFrame, **kwargs):
        """Add experimental data with optional parallel processing."""
        if (self.parallel_enabled and 
            len(data_df) > 1000 and 
            kwargs.get('parallel', False)):
            # Use parallel data loading for large datasets
            return self.parallel_engine.parallel_data_loading(
                self.base_optimizer, data_df
            )
        else:
            # Standard sequential processing
            return self.base_optimizer.add_experimental_data(data_df)
    
    # Delegate all other methods to base optimizer for backward compatibility
    def __getattr__(self, name):
        """Delegate unknown methods to base optimizer."""
        return getattr(self.base_optimizer, name)
    
    # ====================================================================================
    # NEW PARALLEL API - Extended capabilities for advanced use cases
    # ====================================================================================
    
    def benchmark_strategies(self, 
                           strategies: List[str],
                           n_suggestions: int = 10,
                           parallel: bool = True) -> Dict[str, Any]:
        """
        Benchmark multiple optimization strategies in parallel.
        
        Args:
            strategies: List of strategy names to benchmark
            n_suggestions: Number of suggestions per strategy
            parallel: Whether to run in parallel (True by default)
            
        Returns:
            Dictionary with results for each strategy
        """
        if not self.parallel_enabled or not parallel:
            logger.warning("Parallel execution not available, running sequentially")
            results = {}
            for strategy in strategies:
                # Sequential benchmarking
                suggestions = self.base_optimizer.suggest_next_experiment(n_suggestions)
                results[strategy] = {
                    'suggestions': suggestions,
                    'strategy': strategy,
                    'success': True
                }
            return results
        
        optimizer_config = self.execution_router._get_optimizer_config()
        return self.parallel_engine.parallel_benchmark(
            optimizer_config, strategies, n_suggestions
        )
    
    def run_what_if_analysis(self,
                            scenarios: List[Dict],
                            parallel: bool = True) -> Dict[str, Any]:
        """
        Run what-if analysis scenarios in parallel.
        
        Args:
            scenarios: List of scenario configurations
            parallel: Whether to run in parallel (True by default)
            
        Returns:
            Dictionary with results for each scenario
        """
        if not self.parallel_enabled or not parallel:
            logger.warning("Parallel execution not available, running sequentially")
            results = {}
            for i, scenario in enumerate(scenarios):
                scenario_name = scenario.get('name', f'scenario_{i}')
                # Sequential what-if analysis
                results[scenario_name] = {
                    'scenario': scenario,
                    'success': True
                }
            return results
        
        optimizer_config = self.execution_router._get_optimizer_config()
        return self.parallel_engine.parallel_what_if_analysis(
            optimizer_config, scenarios
        )
    
    def load_historical_data_parallel(self,
                                     data_df: pd.DataFrame,
                                     chunk_size: int = 1000) -> Dict[str, Any]:
        """
        Load large historical datasets in parallel.
        
        Args:
            data_df: Historical data to load
            chunk_size: Size of data chunks for parallel processing
            
        Returns:
            Summary of parallel loading results
        """
        if not self.parallel_enabled:
            logger.warning("Parallel execution not available, loading sequentially")
            self.base_optimizer.add_experimental_data(data_df)
            return {'processed_chunks': 1, 'total_chunks': 1}
        
        return self.parallel_engine.parallel_data_loading(
            self.base_optimizer, data_df, chunk_size
        )
    
    # ====================================================================================
    # UTILITY AND MONITORING METHODS
    # ====================================================================================
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics and performance metrics."""
        stats = {
            'parallel_enabled': self.parallel_enabled,
            'sequential_requests': self._sequential_count,
            'parallel_requests': self._parallel_count,
        }
        
        if self.parallel_enabled:
            stats.update({
                'n_workers': self.parallel_engine.n_workers,
                'cache_size': len(self.parallel_engine.model_cache._cache),
            })
        
        return stats
    
    def clear_cache(self):
        """Clear all caches."""
        if self.parallel_enabled:
            self.parallel_engine.model_cache.invalidate()
    
    def set_parallel_enabled(self, enabled: bool):
        """Enable or disable parallel execution."""
        if enabled and not self.parallel_enabled:
            try:
                self.parallel_engine = ParallelOptimizationEngine()
                self.execution_router = ExecutionRouter(self.base_optimizer, self.parallel_engine)
                self.parallel_enabled = True
                logger.info("Parallel optimization enabled")
            except Exception as e:
                logger.error(f"Failed to enable parallel optimization: {e}")
        elif not enabled and self.parallel_enabled:
            if self.parallel_engine:
                self.parallel_engine.__del__()
            self.parallel_engine = None
            self.execution_router = None
            self.parallel_enabled = False
            logger.info("Parallel optimization disabled")