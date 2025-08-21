"""
Hypervolume Calculator - Optimized Hypervolume Computation Module

This module provides a specialized, performance-optimized hypervolume calculation
system for multi-objective Bayesian optimization. It separates the computationally
intensive hypervolume operations from the main optimizer for better performance
and maintainability.

Key Features:
- Adaptive reference point calculation
- Cached hypervolume computations
- Convergence analysis based on hypervolume trends
- Thread-safe hypervolume operations
- Memory-efficient computation strategies

Classes:
    HypervolumeCalculator: Main hypervolume computation engine
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
from botorch.utils.multi_objective.box_decompositions.non_dominated import (
    FastNondominatedPartitioning,
)

logger = logging.getLogger(__name__)


class HypervolumeCalculator:
    """
    Specialized hypervolume calculation engine with performance optimizations.
    
    This class handles all hypervolume-related computations including reference
    point calculation, hypervolume computation, convergence analysis, and caching
    for improved performance.
    """
    
    def __init__(self, device: torch.device = None, dtype: torch.dtype = torch.double):
        """
        Initialize the hypervolume calculator.
        
        Args:
            device: PyTorch device for computations
            dtype: Data type for tensor operations
        """
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = dtype
        self._cache = {}
        self._lock = threading.Lock()
        
        logger.info(f"HypervolumeCalculator initialized on {self.device}")
    
    def calculate_adaptive_reference_point(self, clean_Y: torch.Tensor) -> torch.Tensor:
        """
        Calculates an adaptive reference point based on the data range for better
        hypervolume calculation across different problem scales.

        Args:
            clean_Y: Clean objective values tensor (finite values only)

        Returns:
            torch.Tensor: Adaptive reference point
        """
        try:
            min_observed_Y = clean_Y.min(dim=0)[0]
            max_observed_Y = clean_Y.max(dim=0)[0]

            # Calculate data range for each objective
            data_range = max_observed_Y - min_observed_Y

            # Use adaptive offset: minimum of 10% of data range or 1.0
            # This scales better for problems with different objective magnitudes
            adaptive_offset = torch.maximum(
                data_range * 0.1, torch.ones_like(data_range) * 0.1
            )

            # Ensure minimum offset for very small ranges
            adaptive_offset = torch.maximum(
                adaptive_offset, torch.ones_like(data_range) * 0.01
            )

            ref_point = min_observed_Y - adaptive_offset

            # Ensure the reference point does not contain NaNs
            ref_point = torch.nan_to_num(ref_point, nan=-1.0)

            logger.debug(f"Adaptive offset: {adaptive_offset}")
            logger.debug(f"Data range: {data_range}")

            return ref_point
            
        except Exception as e:
            logger.error(f"Error calculating adaptive reference point: {e}")
            # Return a safe fallback reference point
            return torch.full((clean_Y.shape[1],), -1.0, device=self.device, dtype=self.dtype)
    
    def calculate_hypervolume(self, train_Y: torch.Tensor, objective_names: List[str]) -> Dict[str, float]:
        """
        Calculates the Hypervolume Indicator (HVI) for the current set of observed
        objective values with caching and performance optimizations.

        Args:
            train_Y: Training objective values tensor
            objective_names: List of objective names

        Returns:
            Dict[str, float]: Dictionary containing hypervolume metrics
        """
        default_result = {
            "raw_hypervolume": 0.0,
            "normalized_hypervolume": 0.0,
            "reference_point_adaptive": True,
            "data_points_used": 0,
        }

        try:
            # Check cache first
            cache_key = self._generate_cache_key(train_Y)
            with self._lock:
                if cache_key in self._cache:
                    logger.debug("Using cached hypervolume result")
                    return self._cache[cache_key]

            # Hypervolume is meaningful for at least two objectives
            if len(objective_names) < 2 or train_Y.shape[0] == 0:
                logger.debug("Hypervolume calculation skipped: Less than 2 objectives or no data")
                return default_result

            # Filter out rows containing NaN values
            finite_mask = torch.isfinite(train_Y).all(dim=1)
            if not finite_mask.any():
                logger.debug("Hypervolume calculation skipped: No finite data points")
                return default_result

            clean_Y = train_Y[finite_mask]

            if clean_Y.shape[0] < 2:
                logger.debug(f"Hypervolume calculation skipped: Less than 2 clean data points ({clean_Y.shape[0]})")
                return default_result

            logger.debug(f"clean_Y shape: {clean_Y.shape}")
            logger.debug(f"clean_Y min: {clean_Y.min(dim=0)[0]}, max: {clean_Y.max(dim=0)[0]}")

            # Calculate adaptive reference point
            ref_point = self.calculate_adaptive_reference_point(clean_Y)

            # Calculate hypervolume using BoTorch's FastNondominatedPartitioning
            try:
                logger.debug(f"Adaptive ref point for HVI: {ref_point}")
                partitioning = FastNondominatedPartitioning(
                    ref_point=ref_point, Y=clean_Y
                )
                raw_hypervolume = partitioning.compute_hypervolume().item()

                # Calculate normalized hypervolume for better interpretability
                max_observed_Y = clean_Y.max(dim=0)[0]
                theoretical_max_volume = torch.prod(max_observed_Y - ref_point)

                # Avoid division by zero
                if theoretical_max_volume.item() > 1e-12:
                    normalized_hypervolume = raw_hypervolume / theoretical_max_volume.item()
                else:
                    normalized_hypervolume = 0.0

                # Ensure normalized hypervolume is between 0 and 1
                normalized_hypervolume = max(0.0, min(1.0, normalized_hypervolume))

                result = {
                    "raw_hypervolume": raw_hypervolume,
                    "normalized_hypervolume": normalized_hypervolume,
                    "reference_point_adaptive": True,
                    "data_points_used": clean_Y.shape[0],
                }

                # Cache the result
                with self._lock:
                    self._cache[cache_key] = result

                logger.debug(f"Raw hypervolume: {raw_hypervolume}")
                logger.debug(f"Normalized hypervolume: {normalized_hypervolume}")
                logger.debug(f"Theoretical max volume: {theoretical_max_volume.item()}")

                return result

            except Exception as e:
                logger.warning(f"Hypervolume calculation failed (FastNondominatedPartitioning): {e}")
                return default_result

        except Exception as e:
            logger.error(f"Error in calculate_hypervolume: {e}", exc_info=True)
            return default_result
    
    def check_hypervolume_convergence(
        self, 
        iteration_history: List[Dict[str, Any]], 
        window_size: int = 5, 
        threshold: float = 0.01, 
        use_normalized: bool = True
    ) -> Dict[str, Any]:
        """
        Checks for hypervolume-based convergence using a sliding window approach.

        Args:
            iteration_history: List of iteration history records
            window_size: Number of recent iterations to consider for convergence
            threshold: Relative change threshold below which we consider convergence
            use_normalized: Whether to use normalized hypervolume for convergence check

        Returns:
            Dict containing convergence status, metrics, and recommendations
        """
        convergence_result = {
            "converged": False,
            "progress_stagnant": False,
            "iterations_stable": 0,
            "relative_improvement": 0.0,
            "recommendation": "continue",
            "confidence": "low",
        }

        try:
            if len(iteration_history) < window_size:
                convergence_result["recommendation"] = "continue - insufficient data"
                return convergence_result

            # Extract hypervolume values from recent iterations
            hv_key = "normalized_hypervolume" if use_normalized else "hypervolume"

            # Handle both old format (float) and new format (dict)
            recent_hvs = []
            for iteration in iteration_history[-window_size:]:
                hv_value = iteration.get("hypervolume", 0.0)
                if isinstance(hv_value, dict):
                    recent_hvs.append(hv_value.get(hv_key, 0.0))
                else:
                    # Legacy format - use raw value
                    recent_hvs.append(hv_value)

            if not recent_hvs or all(hv == 0.0 for hv in recent_hvs):
                convergence_result["recommendation"] = "continue - no valid hypervolume data"
                return convergence_result

            # Calculate relative improvement
            max_hv = max(recent_hvs)
            min_hv = min(recent_hvs)

            if max_hv > 1e-12:
                relative_improvement = (max_hv - min_hv) / max_hv
            else:
                relative_improvement = 0.0

            convergence_result["relative_improvement"] = relative_improvement

            # Check for convergence
            if relative_improvement < threshold:
                convergence_result["converged"] = True
                convergence_result["iterations_stable"] = window_size
                convergence_result["confidence"] = "high" if window_size >= 10 else "medium"

                # Additional check: is hypervolume actually improving over longer period?
                if len(iteration_history) >= window_size * 2:
                    earlier_hvs = []
                    for iteration in iteration_history[-(window_size * 2) : -window_size]:
                        hv_value = iteration.get("hypervolume", 0.0)
                        if isinstance(hv_value, dict):
                            earlier_hvs.append(hv_value.get(hv_key, 0.0))
                        else:
                            earlier_hvs.append(hv_value)

                    if earlier_hvs and max(earlier_hvs) > 1e-12:
                        long_term_improvement = (max(recent_hvs) - max(earlier_hvs)) / max(earlier_hvs)

                        if long_term_improvement < threshold / 2:
                            convergence_result["progress_stagnant"] = True
                            convergence_result["recommendation"] = "consider_stopping"
                        else:
                            convergence_result["recommendation"] = "continue_cautiously"
                    else:
                        convergence_result["recommendation"] = "continue_cautiously"
                else:
                    convergence_result["recommendation"] = "continue_cautiously"
            else:
                convergence_result["recommendation"] = "continue"

            # Calculate trend
            if len(recent_hvs) >= 3:
                # Simple linear trend analysis
                x = list(range(len(recent_hvs)))
                n = len(recent_hvs)
                sum_x = sum(x)
                sum_y = sum(recent_hvs)
                sum_xy = sum(xi * yi for xi, yi in zip(x, recent_hvs))
                sum_x2 = sum(xi * xi for xi in x)

                if n * sum_x2 - sum_x * sum_x != 0:
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                    convergence_result["trend_slope"] = slope

                    if slope < -threshold / 10:
                        convergence_result["recommendation"] = "investigate_degradation"

            logger.debug(f"Convergence check: {convergence_result}")
            return convergence_result

        except Exception as e:
            logger.error(f"Error in convergence check: {e}", exc_info=True)
            convergence_result["recommendation"] = "continue - error in analysis"
            return convergence_result
    
    def get_optimization_progress_summary(
        self, 
        iteration_history: List[Dict[str, Any]], 
        experimental_data_count: int
    ) -> Dict[str, Any]:
        """
        Provides a comprehensive summary of optimization progress including
        hypervolume trends, convergence status, and recommendations.

        Args:
            iteration_history: List of iteration history records
            experimental_data_count: Number of experimental data points

        Returns:
            Dict containing detailed progress analysis
        """
        summary = {
            "total_iterations": len(iteration_history),
            "total_experiments": experimental_data_count,
            "current_hypervolume": None,
            "hypervolume_trend": "unknown",
            "convergence_status": "unknown",
            "efficiency_metrics": {},
            "recommendations": [],
        }

        try:
            if not iteration_history:
                summary["recommendations"].append("Start optimization by adding experimental data")
                return summary

            # Get current hypervolume
            latest_iteration = iteration_history[-1]
            hv_value = latest_iteration.get("hypervolume", 0.0)

            if isinstance(hv_value, dict):
                summary["current_hypervolume"] = {
                    "raw": hv_value.get("raw_hypervolume", 0.0),
                    "normalized": hv_value.get("normalized_hypervolume", 0.0),
                    "data_points_used": hv_value.get("data_points_used", 0),
                }
            else:
                summary["current_hypervolume"] = {"raw": hv_value, "normalized": None}

            # Analyze trend over recent iterations
            if len(iteration_history) >= 3:
                recent_iterations = min(10, len(iteration_history))
                recent_hvs = []

                for iteration in iteration_history[-recent_iterations:]:
                    hv_val = iteration.get("hypervolume", 0.0)
                    if isinstance(hv_val, dict):
                        recent_hvs.append(hv_val.get("raw_hypervolume", 0.0))
                    else:
                        recent_hvs.append(hv_val)

                if len(recent_hvs) >= 3 and max(recent_hvs) > 1e-12:
                    first_third = sum(recent_hvs[: len(recent_hvs) // 3]) / (len(recent_hvs) // 3)
                    last_third = sum(recent_hvs[-len(recent_hvs) // 3 :]) / (len(recent_hvs) // 3)

                    relative_change = (last_third - first_third) / max(first_third, 1e-12)

                    if relative_change > 0.05:
                        summary["hypervolume_trend"] = "improving"
                    elif relative_change > -0.02:
                        summary["hypervolume_trend"] = "stable"
                    else:
                        summary["hypervolume_trend"] = "declining"

            # Check convergence
            convergence_result = self.check_hypervolume_convergence(iteration_history)
            summary["convergence_status"] = convergence_result["recommendation"]
            summary["convergence_details"] = convergence_result

            # Calculate efficiency metrics
            if len(iteration_history) > 1:
                # Hypervolume per experiment efficiency
                current_hv = summary["current_hypervolume"]["raw"] if summary["current_hypervolume"] else 0.0
                experiments_count = experimental_data_count

                if experiments_count > 0:
                    summary["efficiency_metrics"]["hv_per_experiment"] = current_hv / experiments_count

                # Rate of improvement
                if len(iteration_history) >= 5:
                    early_hv = iteration_history[min(4, len(iteration_history) - 1)].get("hypervolume", 0.0)
                    if isinstance(early_hv, dict):
                        early_hv = early_hv.get("raw_hypervolume", 0.0)

                    if early_hv > 1e-12:
                        improvement_rate = (current_hv - early_hv) / early_hv
                        summary["efficiency_metrics"]["improvement_rate"] = improvement_rate

            # Generate recommendations
            if summary["hypervolume_trend"] == "declining":
                summary["recommendations"].append("Check for overfitting or data quality issues")
            elif summary["hypervolume_trend"] == "stable" and len(iteration_history) > 10:
                summary["recommendations"].append("Consider exploring different regions of parameter space")
            elif convergence_result["converged"]:
                summary["recommendations"].append("Optimization may have converged - consider validation experiments")
            else:
                summary["recommendations"].append("Continue optimization - good progress being made")

            return summary

        except Exception as e:
            logger.error(f"Error generating progress summary: {e}", exc_info=True)
            summary["recommendations"].append("Error in progress analysis - continue with caution")
            return summary
    
    def _generate_cache_key(self, train_Y: torch.Tensor) -> str:
        """Generate a cache key for hypervolume computation results."""
        try:
            # Use tensor hash for caching
            return f"hv_{hash(train_Y.cpu().numpy().tobytes())}"
        except Exception:
            # Fallback to timestamp-based key
            return f"hv_{int(time.time() * 1000000)}"
    
    def clear_cache(self) -> None:
        """Clear the hypervolume computation cache."""
        with self._lock:
            self._cache.clear()
        logger.debug("Hypervolume cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about the hypervolume cache."""
        with self._lock:
            return {
                "cache_size": len(self._cache),
                "cache_hits": getattr(self, '_cache_hits', 0),
                "cache_misses": getattr(self, '_cache_misses', 0)
            }