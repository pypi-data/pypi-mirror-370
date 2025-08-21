"""
Performance Optimization Utilities for PyMBO
Provides caching, lazy loading, and performance monitoring capabilities
"""

import time
import hashlib
import threading
import weakref
from functools import wraps, lru_cache
from typing import Any, Dict, Optional, Callable
import logging
import gc
import psutil
import numpy as np
import torch

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.start_times = {}
        self.metrics = {}
        
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.start_times[operation] = time.perf_counter()
        
    def end_timer(self, operation: str) -> float:
        """End timing and return duration"""
        if operation in self.start_times:
            duration = time.perf_counter() - self.start_times[operation]
            self.metrics[operation] = self.metrics.get(operation, []) + [duration]
            return duration
        return 0.0
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        process = psutil.Process()
        return {
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'memory_percent': process.memory_percent(),
            'cpu_percent': process.cpu_percent()
        }
    
    def log_performance(self, operation: str):
        """Log performance metrics for an operation"""
        if operation in self.metrics:
            times = self.metrics[operation]
            avg_time = np.mean(times)
            logger.debug(f"Performance: {operation} - Avg: {avg_time:.3f}s, Calls: {len(times)}")

# Global performance monitor
perf_monitor = PerformanceMonitor()

def performance_timer(func):
    """Decorator to time function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        operation = f"{func.__module__}.{func.__name__}"
        perf_monitor.start_timer(operation)
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = perf_monitor.end_timer(operation)
            if duration > 0.1:  # Log slow operations
                logger.debug(f"Slow operation: {operation} took {duration:.3f}s")
    return wrapper

class PlotCache:
    """Intelligent plot caching system"""
    
    def __init__(self, max_size: int = 50):
        self.cache = {}
        self.timestamps = {}
        self.access_times = {}
        self.max_size = max_size
        self._lock = threading.Lock()
    
    def _generate_key(self, plot_type: str, data_hash: str, params: Dict) -> str:
        """Generate cache key from plot parameters"""
        param_str = str(sorted(params.items())) if params else ""
        return f"{plot_type}_{data_hash}_{hashlib.md5(param_str.encode()).hexdigest()[:8]}"
    
    def get(self, plot_type: str, data_hash: str, params: Dict = None) -> Optional[Any]:
        """Get cached plot if available and valid"""
        with self._lock:
            key = self._generate_key(plot_type, data_hash, params or {})
            if key in self.cache:
                self.access_times[key] = time.time()
                logger.debug(f"Plot cache hit: {plot_type}")
                return self.cache[key]
            logger.debug(f"Plot cache miss: {plot_type}")
            return None
    
    def set(self, plot_type: str, data_hash: str, plot_data: Any, params: Dict = None):
        """Cache plot data"""
        with self._lock:
            key = self._generate_key(plot_type, data_hash, params or {})
            
            # Evict old entries if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            self.cache[key] = plot_data
            self.timestamps[key] = time.time()
            self.access_times[key] = time.time()
            logger.debug(f"Plot cached: {plot_type}")
    
    def _evict_oldest(self):
        """Evict least recently used cache entry"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.cache.pop(oldest_key, None)
        self.timestamps.pop(oldest_key, None)
        self.access_times.pop(oldest_key, None)
        logger.debug(f"Evicted cache entry: {oldest_key}")
    
    def clear(self):
        """Clear all cached plots"""
        with self._lock:
            self.cache.clear()
            self.timestamps.clear()
            self.access_times.clear()
            logger.debug("Plot cache cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
        }

class DataHasher:
    """Fast data hashing for cache keys"""
    
    @staticmethod
    def hash_dataframe(df) -> str:
        """Generate hash for pandas DataFrame"""
        if df is None or df.empty:
            return "empty"
        
        # Use shape and a sample of values for fast hashing
        shape_str = f"{df.shape[0]}x{df.shape[1]}"
        if df.shape[0] > 0:
            # Sample first/last rows and some values
            sample_vals = []
            for col in df.columns[:3]:  # First 3 columns only
                if len(df) > 0:
                    sample_vals.append(str(df[col].iloc[0]))
                    if len(df) > 1:
                        sample_vals.append(str(df[col].iloc[-1]))
            
            value_hash = hashlib.md5(''.join(sample_vals).encode()).hexdigest()[:8]
            return f"{shape_str}_{value_hash}"
        
        return shape_str
    
    @staticmethod
    def hash_tensor(tensor) -> str:
        """Generate hash for PyTorch tensor"""
        if tensor is None:
            return "none"
        
        shape_str = 'x'.join(map(str, tensor.shape))
        if tensor.numel() > 0:
            # Use tensor statistics for hashing
            stats = f"{tensor.mean().item():.6f}_{tensor.std().item():.6f}"
            return f"{shape_str}_{hashlib.md5(stats.encode()).hexdigest()[:8]}"
        
        return shape_str

class LazyLoader:
    """Lazy loading for expensive operations"""
    
    def __init__(self, loader_func: Callable, *args, **kwargs):
        self.loader_func = loader_func
        self.args = args
        self.kwargs = kwargs
        self._value = None
        self._loaded = False
        self._lock = threading.Lock()
    
    def get(self):
        """Get the loaded value, loading if necessary"""
        if not self._loaded:
            with self._lock:
                if not self._loaded:  # Double-check locking
                    logger.debug(f"Lazy loading: {self.loader_func.__name__}")
                    self._value = self.loader_func(*self.args, **self.kwargs)
                    self._loaded = True
        return self._value
    
    def is_loaded(self) -> bool:
        """Check if value has been loaded"""
        return self._loaded
    
    def reset(self):
        """Reset the lazy loader"""
        with self._lock:
            self._value = None
            self._loaded = False

class MemoryManager:
    """Enhanced memory management utilities with intelligent optimization"""
    
    def __init__(self):
        self.memory_threshold = 0.8  # 80% memory usage threshold
        self.cleanup_callbacks = []
        self.monitoring_enabled = False
        self._monitoring_thread = None
        
    def add_cleanup_callback(self, callback: Callable):
        """Add a callback function for memory cleanup"""
        self.cleanup_callbacks.append(callback)
        
    def remove_cleanup_callback(self, callback: Callable):
        """Remove a callback function"""
        if callback in self.cleanup_callbacks:
            self.cleanup_callbacks.remove(callback)
    
    def start_monitoring(self, interval: float = 10.0):
        """Start automatic memory monitoring"""
        if not self.monitoring_enabled:
            self.monitoring_enabled = True
            self._monitoring_thread = threading.Thread(
                target=self._memory_monitor_loop, 
                args=(interval,), 
                daemon=True
            )
            self._monitoring_thread.start()
            logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop automatic memory monitoring"""
        self.monitoring_enabled = False
        if self._monitoring_thread:
            self._monitoring_thread.join()
        logger.info("Memory monitoring stopped")
    
    def _memory_monitor_loop(self, interval: float):
        """Memory monitoring loop"""
        while self.monitoring_enabled:
            try:
                memory_info = self.get_memory_info()
                if memory_info['percent'] > self.memory_threshold * 100:
                    logger.warning(f"High memory usage detected: {memory_info['percent']:.1f}%")
                    self.intelligent_cleanup()
                
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in memory monitoring: {e}")
                time.sleep(interval)
    
    def intelligent_cleanup(self):
        """Perform intelligent memory cleanup based on usage patterns"""
        initial_memory = self.get_memory_info()
        logger.info(f"Starting intelligent cleanup. Current memory: {initial_memory['percent']:.1f}%")
        
        # Step 1: Force garbage collection
        collected = self.force_gc()
        
        # Step 2: Clean up matplotlib figures
        self.cleanup_matplotlib()
        
        # Step 3: Clean up PyTorch cache
        self.cleanup_torch()
        
        # Step 4: Run custom cleanup callbacks
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in cleanup callback: {e}")
        
        # Step 5: Second garbage collection pass
        self.force_gc()
        
        final_memory = self.get_memory_info()
        memory_saved = initial_memory['percent'] - final_memory['percent']
        logger.info(f"Cleanup completed. Memory saved: {memory_saved:.1f}%, Current: {final_memory['percent']:.1f}%")
    
    @staticmethod
    def cleanup_matplotlib():
        """Clean up matplotlib figures to free memory"""
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
            # Also clear the figure registry
            import matplotlib._pylab_helpers
            matplotlib._pylab_helpers.Gcf.destroy_all()
            gc.collect()
            logger.debug("Matplotlib figures cleaned up")
        except ImportError:
            pass
        except Exception as e:
            logger.error(f"Error cleaning matplotlib: {e}")
    
    @staticmethod
    def cleanup_torch():
        """Clean up PyTorch tensors and cache"""
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            
            # Clear tensor cache
            if hasattr(torch, '_C') and hasattr(torch._C, '_cuda_clearCublasWorkspaces'):
                torch._C._cuda_clearCublasWorkspaces()
            
            gc.collect()
            logger.debug("PyTorch cache cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning PyTorch cache: {e}")
    
    @staticmethod
    def cleanup_numpy():
        """Clean up NumPy temporary arrays"""
        try:
            # Force cleanup of temporary arrays
            import numpy as np
            if hasattr(np, '_NoValue'):
                # Clear any cached temporary arrays
                pass
            gc.collect()
            logger.debug("NumPy cleanup completed")
        except Exception as e:
            logger.error(f"Error cleaning NumPy: {e}")
    
    @staticmethod
    def force_gc():
        """Force comprehensive garbage collection"""
        collected = 0
        for generation in range(3):  # Clean all generations
            collected += gc.collect(generation)
        
        # Also force cleanup of weak references
        import weakref
        if hasattr(weakref, '_remove_dead_weakref'):
            # This is an internal function, use with caution
            pass
        
        logger.debug(f"Garbage collection freed {collected} objects")
        return collected
    
    @staticmethod
    def get_memory_info() -> Dict[str, float]:
        """Get detailed memory information"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            virtual_memory = psutil.virtual_memory()
            
            # Additional GPU memory info if available
            gpu_memory = {}
            if torch.cuda.is_available():
                try:
                    gpu_memory = {
                        'gpu_allocated_mb': torch.cuda.memory_allocated() / 1024 / 1024,
                        'gpu_cached_mb': torch.cuda.memory_reserved() / 1024 / 1024,
                        'gpu_total_mb': torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
                    }
                except Exception:
                    pass
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': process.memory_percent(),
                'available_mb': virtual_memory.available / 1024 / 1024,
                'total_mb': virtual_memory.total / 1024 / 1024,
                'used_mb': virtual_memory.used / 1024 / 1024,
                **gpu_memory
            }
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {'error': str(e)}

class BatchProcessor:
    """Process large datasets in batches to manage memory"""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
    
    def process_dataframe(self, df, process_func: Callable, **kwargs):
        """Process DataFrame in batches"""
        if len(df) <= self.batch_size:
            return process_func(df, **kwargs)
        
        results = []
        for i in range(0, len(df), self.batch_size):
            batch = df.iloc[i:i + self.batch_size]
            result = process_func(batch, **kwargs)
            results.append(result)
            
            # Optional memory cleanup between batches
            if i % (self.batch_size * 5) == 0:
                gc.collect()
        
        # Combine results
        if results and hasattr(results[0], 'concat'):
            return type(results[0]).concat(results)
        return results

# Global instances
plot_cache = PlotCache()
memory_manager = MemoryManager()
data_hasher = DataHasher()

# Start memory monitoring by default
memory_manager.start_monitoring()

def optimized_plot_update(plot_func):
    """Decorator for optimized plot updates with caching"""
    @wraps(plot_func)
    def wrapper(self, *args, **kwargs):
        # Generate cache key from data
        data_hash = "default"
        if hasattr(self, 'experimental_data') and self.experimental_data is not None:
            data_hash = data_hasher.hash_dataframe(self.experimental_data)
        
        plot_type = plot_func.__name__
        cached_plot = plot_cache.get(plot_type, data_hash, kwargs)
        
        if cached_plot is not None:
            logger.debug(f"Using cached plot: {plot_type}")
            return cached_plot
        
        # Generate new plot
        logger.debug(f"Generating new plot: {plot_type}")
        result = plot_func(self, *args, **kwargs)
        
        # Cache the result
        plot_cache.set(plot_type, data_hash, result, kwargs)
        
        return result
    
    return wrapper

def debounce(wait_time: float):
    """Debounce decorator to prevent excessive function calls"""
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_called[0] >= wait_time:
                last_called[0] = now
                return func(*args, **kwargs)
            else:
                logger.debug(f"Debounced call to {func.__name__}")
        
        return wrapper
    return decorator

# Export main optimization utilities
__all__ = [
    'PerformanceMonitor', 'PlotCache', 'DataHasher', 'LazyLoader',
    'MemoryManager', 'BatchProcessor', 'performance_timer',
    'optimized_plot_update', 'debounce', 'plot_cache', 'memory_manager',
    'data_hasher', 'perf_monitor'
]