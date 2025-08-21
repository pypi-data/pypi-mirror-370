"""
Design Space Generator for SGLBO Screening Module

Generates design spaces around optimal points using Central Composite Design (CCD)
and other design of experiments methodologies. This creates parameter combinations
for detailed optimization around the best points found during screening.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from itertools import product
from scipy.stats import norm

from .parameter_handler import ParameterHandler

logger = logging.getLogger(__name__)


class DesignSpaceGenerator:
    """
    Generates design spaces around optimal points found during screening.
    Supports Central Composite Design (CCD), Full Factorial, and custom designs.
    """
    
    def __init__(self, param_handler: ParameterHandler):
        """
        Initialize design space generator.
        
        Args:
            param_handler: Parameter handler for transformations and validation
        """
        self.param_handler = param_handler
        self.n_params = param_handler.n_params
        self.param_names = param_handler.param_names
        
        logger.info(f"Design space generator initialized for {self.n_params} parameters")
    
    def generate_central_composite_design(
        self,
        center_point: Dict[str, Any],
        design_radius: float = 0.2,
        include_center: bool = True,
        include_axial: bool = True,
        include_factorial: bool = True,
        alpha: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate Central Composite Design (CCD) around a center point.
        
        Args:
            center_point: Center point parameters
            design_radius: Radius of design space (as fraction of parameter range)
            include_center: Whether to include center point
            include_axial: Whether to include axial (star) points
            include_factorial: Whether to include factorial corner points
            alpha: Distance of axial points (auto-calculated if None)
            
        Returns:
            List[Dict[str, Any]]: List of parameter dictionaries forming the design
        """
        try:
            logger.info(f"Generating CCD around center point: {center_point}")
            
            # Validate center point
            if not self.param_handler.validate_parameter_dict(center_point):
                raise ValueError("Invalid center point parameters")
            
            # Convert center point to normalized space
            center_normalized = self.param_handler.params_to_normalized(center_point)
            
            design_points = []
            
            # Calculate alpha (axial distance) if not provided
            if alpha is None:
                # For rotatable design: alpha = (2^k)^(1/4) where k is number of parameters
                alpha = (2 ** self.n_params) ** 0.25
            
            # Scale alpha by design radius
            alpha = alpha * design_radius
            
            # 1. Center point
            if include_center:
                design_points.append(center_normalized.copy())
                logger.debug("Added center point to design")
            
            # 2. Factorial points (corners of hypercube)
            if include_factorial:
                factorial_levels = [-1, 1]  # Low and high levels
                factorial_combinations = list(product(factorial_levels, repeat=self.n_params))
                
                for combination in factorial_combinations:
                    factorial_point = center_normalized.copy()
                    for i, level in enumerate(combination):
                        # Scale by design radius and apply (allow extrapolation for screening)
                        delta = level * design_radius
                        factorial_point[i] = factorial_point[i] + delta
                    
                    design_points.append(factorial_point)
                
                logger.debug(f"Added {len(factorial_combinations)} factorial points to design")
            
            # 3. Axial (star) points
            if include_axial:
                for i in range(self.n_params):
                    # Positive axial point (allow extrapolation for screening)
                    axial_pos = center_normalized.copy()
                    axial_pos[i] = axial_pos[i] + alpha
                    design_points.append(axial_pos)
                    
                    # Negative axial point (allow extrapolation for screening)
                    axial_neg = center_normalized.copy()
                    axial_neg[i] = axial_neg[i] - alpha
                    design_points.append(axial_neg)
                
                logger.debug(f"Added {2 * self.n_params} axial points to design")
            
            # Convert all points back to parameter space
            design_params = []
            for point_normalized in design_points:
                param_dict = self.param_handler.normalized_to_params(point_normalized)
                design_params.append(param_dict)
            
            logger.info(f"Generated CCD with {len(design_params)} points")
            return design_params
            
        except Exception as e:
            logger.error(f"Error generating CCD: {e}")
            return []
    
    def generate_full_factorial_design(
        self,
        center_point: Dict[str, Any],
        design_radius: float = 0.2,
        levels_per_factor: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate full factorial design around a center point.
        
        Args:
            center_point: Center point parameters
            design_radius: Radius of design space
            levels_per_factor: Number of levels per parameter
            
        Returns:
            List[Dict[str, Any]]: List of parameter dictionaries
        """
        try:
            logger.info(f"Generating full factorial design with {levels_per_factor} levels per factor")
            
            # Validate center point
            if not self.param_handler.validate_parameter_dict(center_point):
                raise ValueError("Invalid center point parameters")
            
            # Convert center point to normalized space
            center_normalized = self.param_handler.params_to_normalized(center_point)
            
            # Generate levels for each parameter
            levels = np.linspace(-design_radius, design_radius, levels_per_factor)
            
            # Generate all combinations
            level_combinations = list(product(levels, repeat=self.n_params))
            
            design_points = []
            for combination in level_combinations:
                factorial_point = center_normalized.copy()
                for i, delta in enumerate(combination):
                    factorial_point[i] = factorial_point[i] + delta  # Allow extrapolation
                design_points.append(factorial_point)
            
            # Convert back to parameter space
            design_params = []
            for point_normalized in design_points:
                param_dict = self.param_handler.normalized_to_params(point_normalized)
                design_params.append(param_dict)
            
            logger.info(f"Generated full factorial design with {len(design_params)} points")
            return design_params
            
        except Exception as e:
            logger.error(f"Error generating full factorial design: {e}")
            return []
    
    def generate_box_behnken_design(
        self,
        center_point: Dict[str, Any],
        design_radius: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        Generate Box-Behnken design around a center point.
        Efficient for response surface modeling with fewer points than CCD.
        
        Args:
            center_point: Center point parameters
            design_radius: Radius of design space
            
        Returns:
            List[Dict[str, Any]]: List of parameter dictionaries
        """
        try:
            logger.info("Generating Box-Behnken design")
            
            if self.n_params < 3:
                logger.warning("Box-Behnken design requires at least 3 parameters, using CCD instead")
                return self.generate_central_composite_design(center_point, design_radius)
            
            # Validate center point
            if not self.param_handler.validate_parameter_dict(center_point):
                raise ValueError("Invalid center point parameters")
            
            # Convert center point to normalized space
            center_normalized = self.param_handler.params_to_normalized(center_point)
            
            design_points = []
            
            # Add center point
            design_points.append(center_normalized.copy())
            
            # Generate Box-Behnken points
            # For each pair of parameters, create a 2^2 factorial while keeping others at center
            for i in range(self.n_params):
                for j in range(i + 1, self.n_params):
                    # Four combinations for parameters i and j
                    combinations = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                    
                    for combo in combinations:
                        bb_point = center_normalized.copy()
                        bb_point[i] = bb_point[i] + combo[0] * design_radius  # Allow extrapolation
                        bb_point[j] = bb_point[j] + combo[1] * design_radius  # Allow extrapolation
                        design_points.append(bb_point)
            
            # Convert back to parameter space
            design_params = []
            for point_normalized in design_points:
                param_dict = self.param_handler.normalized_to_params(point_normalized)
                design_params.append(param_dict)
            
            logger.info(f"Generated Box-Behnken design with {len(design_params)} points")
            return design_params
            
        except Exception as e:
            logger.error(f"Error generating Box-Behnken design: {e}")
            return []
    
    def generate_adaptive_design(
        self,
        center_point: Dict[str, Any],
        design_radius: float = 0.2,
        target_points: int = 20,
        uncertainty_weights: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate adaptive design space that considers parameter importance and uncertainty.
        
        Args:
            center_point: Center point parameters
            design_radius: Base radius of design space
            target_points: Target number of design points
            uncertainty_weights: Weights for parameter importance (higher = more exploration)
            
        Returns:
            List[Dict[str, Any]]: List of parameter dictionaries
        """
        try:
            logger.info(f"Generating adaptive design with {target_points} target points")
            
            # Validate center point
            if not self.param_handler.validate_parameter_dict(center_point):
                raise ValueError("Invalid center point parameters")
            
            # Convert center point to normalized space
            center_normalized = self.param_handler.params_to_normalized(center_point)
            
            # Set default uncertainty weights if not provided
            if uncertainty_weights is None:
                uncertainty_weights = {name: 1.0 for name in self.param_names}
            
            design_points = []
            
            # Always include center point
            design_points.append(center_normalized.copy())
            
            # Generate points using importance-weighted sampling
            points_needed = target_points - 1  # Subtract center point
            
            for _ in range(points_needed):
                # Generate candidate point
                candidate = center_normalized.copy()
                
                for i, param_name in enumerate(self.param_names):
                    weight = uncertainty_weights.get(param_name, 1.0)
                    
                    # Sample offset with importance weighting
                    # Higher weight = larger potential offset
                    offset_std = design_radius * weight
                    offset = np.random.normal(0, offset_std)
                    
                    candidate[i] = candidate[i] + offset  # Allow extrapolation for screening
                
                design_points.append(candidate)
            
            # Remove duplicates (approximately)
            unique_points = []
            for point in design_points:
                is_duplicate = False
                for existing in unique_points:
                    if np.linalg.norm(point - existing) < 0.01:  # Tolerance for duplicates
                        is_duplicate = True
                        break
                if not is_duplicate:
                    unique_points.append(point)
            
            # Convert back to parameter space
            design_params = []
            for point_normalized in unique_points:
                param_dict = self.param_handler.normalized_to_params(point_normalized)
                design_params.append(param_dict)
            
            logger.info(f"Generated adaptive design with {len(design_params)} unique points")
            return design_params
            
        except Exception as e:
            logger.error(f"Error generating adaptive design: {e}")
            return []
    
    def generate_multi_center_design(
        self,
        center_points: List[Dict[str, Any]],
        design_radius: float = 0.15,
        points_per_center: int = 15,
        design_type: str = "ccd"
    ) -> List[Dict[str, Any]]:
        """
        Generate design space around multiple center points (e.g., multiple local optima).
        
        Args:
            center_points: List of center point parameters
            design_radius: Radius around each center
            points_per_center: Number of points per center
            design_type: Type of design ("ccd", "factorial", "adaptive")
            
        Returns:
            List[Dict[str, Any]]: Combined list of parameter dictionaries
        """
        try:
            logger.info(f"Generating multi-center design around {len(center_points)} centers")
            
            all_design_points = []
            
            for i, center_point in enumerate(center_points):
                logger.debug(f"Generating design around center point {i + 1}")
                
                if design_type == "ccd":
                    center_design = self.generate_central_composite_design(
                        center_point, design_radius
                    )
                elif design_type == "factorial":
                    center_design = self.generate_full_factorial_design(
                        center_point, design_radius, levels_per_factor=3
                    )
                elif design_type == "adaptive":
                    center_design = self.generate_adaptive_design(
                        center_point, design_radius, target_points=points_per_center
                    )
                else:
                    logger.warning(f"Unknown design type '{design_type}', using CCD")
                    center_design = self.generate_central_composite_design(
                        center_point, design_radius
                    )
                
                all_design_points.extend(center_design)
            
            # Remove approximate duplicates across all centers
            unique_points = []
            for point in all_design_points:
                is_duplicate = False
                point_normalized = self.param_handler.params_to_normalized(point)
                
                for existing in unique_points:
                    existing_normalized = self.param_handler.params_to_normalized(existing)
                    if np.linalg.norm(point_normalized - existing_normalized) < 0.02:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_points.append(point)
            
            logger.info(f"Generated multi-center design with {len(unique_points)} unique points")
            return unique_points
            
        except Exception as e:
            logger.error(f"Error generating multi-center design: {e}")
            return []
    
    def optimize_design_spacing(
        self,
        design_points: List[Dict[str, Any]],
        min_distance: float = 0.05
    ) -> List[Dict[str, Any]]:
        """
        Optimize design point spacing to ensure minimum distance between points.
        
        Args:
            design_points: Initial design points
            min_distance: Minimum normalized distance between points
            
        Returns:
            List[Dict[str, Any]]: Optimized design points
        """
        try:
            logger.info(f"Optimizing spacing for {len(design_points)} design points")
            
            if len(design_points) <= 1:
                return design_points
            
            # Convert to normalized space for distance calculations
            normalized_points = [
                self.param_handler.params_to_normalized(point) for point in design_points
            ]
            
            optimized_points = []
            
            for i, point in enumerate(normalized_points):
                # Check distance to all previously accepted points
                too_close = False
                for accepted_point in optimized_points:
                    distance = np.linalg.norm(point - accepted_point)
                    if distance < min_distance:
                        too_close = True
                        break
                
                if not too_close:
                    optimized_points.append(point)
                else:
                    # Try to adjust the point to maintain minimum distance
                    adjusted_point = point.copy()
                    max_attempts = 10
                    
                    for attempt in range(max_attempts):
                        # Add small random perturbation (allow extrapolation)
                        perturbation = np.random.normal(0, 0.01, len(point))
                        adjusted_point = point + perturbation
                        
                        # Check if adjusted point maintains minimum distance
                        valid = True
                        for accepted_point in optimized_points:
                            distance = np.linalg.norm(adjusted_point - accepted_point)
                            if distance < min_distance:
                                valid = False
                                break
                        
                        if valid:
                            optimized_points.append(adjusted_point)
                            break
                    
                    # If adjustment failed, skip this point
                    if attempt == max_attempts - 1:
                        logger.debug(f"Could not adjust point {i} to maintain minimum distance")
            
            # Convert back to parameter space
            optimized_design = []
            for point_normalized in optimized_points:
                param_dict = self.param_handler.normalized_to_params(point_normalized)
                optimized_design.append(param_dict)
            
            logger.info(f"Optimized design contains {len(optimized_design)} points "
                       f"(removed {len(design_points) - len(optimized_design)} points)")
            
            return optimized_design
            
        except Exception as e:
            logger.error(f"Error optimizing design spacing: {e}")
            return design_points
    
    def get_design_summary(self, design_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics for a design space.
        
        Args:
            design_points: List of design points
            
        Returns:
            Dict[str, Any]: Design summary information
        """
        try:
            if not design_points:
                return {"n_points": 0, "error": "No design points provided"}
            
            # Convert to DataFrame for easier analysis
            design_df = pd.DataFrame(design_points)
            
            summary = {
                "n_points": len(design_points),
                "parameter_coverage": {},
                "design_efficiency": {},
                "space_filling": {}
            }
            
            # Parameter coverage statistics
            for param_name in self.param_names:
                if param_name in design_df.columns:
                    values = design_df[param_name]
                    param_config = self.param_handler.params_config[param_name]
                    
                    if param_config["type"] in ["continuous", "discrete"]:
                        bounds = param_config["bounds"]
                        range_coverage = (values.max() - values.min()) / (bounds[1] - bounds[0])
                        
                        summary["parameter_coverage"][param_name] = {
                            "min": float(values.min()),
                            "max": float(values.max()),
                            "mean": float(values.mean()),
                            "std": float(values.std()),
                            "range_coverage": float(range_coverage)
                        }
                    else:
                        # Categorical - coverage is fraction of unique values
                        unique_values = values.unique()
                        range_coverage = len(unique_values) / len(param_config["bounds"])
                        
                        summary["parameter_coverage"][param_name] = {
                            "unique_values": list(unique_values),
                            "num_unique": len(unique_values),
                            "total_possible": len(param_config["bounds"]),
                            "range_coverage": float(range_coverage)
                        }
            
            # Calculate space-filling metrics
            normalized_points = np.array([
                self.param_handler.params_to_normalized(point) for point in design_points
            ])
            
            if len(normalized_points) > 1:
                # Minimum distance between points
                min_distances = []
                for i in range(len(normalized_points)):
                    distances = [
                        np.linalg.norm(normalized_points[i] - normalized_points[j])
                        for j in range(len(normalized_points)) if i != j
                    ]
                    min_distances.append(min(distances))
                
                summary["space_filling"] = {
                    "min_distance": float(min(min_distances)),
                    "max_distance": float(max(min_distances)),
                    "mean_min_distance": float(np.mean(min_distances)),
                    "uniformity_score": float(np.std(min_distances))  # Lower is more uniform
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating design summary: {e}")
            return {"error": str(e)}