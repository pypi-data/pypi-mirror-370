"""
Screening Results Management

Handles storage, analysis, and reporting of SGLBO screening optimization results.
Provides comprehensive tracking of the screening process and facilitates
transition to detailed optimization.
"""

import logging
import numpy as np
import pandas as pd
import json
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import pickle

logger = logging.getLogger(__name__)


class ScreeningResults:
    """
    Manages storage, analysis, and reporting of screening optimization results.
    Tracks the entire screening process and provides insights for next steps.
    """
    
    def __init__(
        self,
        params_config: Dict[str, Dict[str, Any]],
        responses_config: Dict[str, Dict[str, Any]]
    ):
        """
        Initialize screening results manager.
        
        Args:
            params_config: Parameter configuration
            responses_config: Response configuration
        """
        self.params_config = params_config
        self.responses_config = responses_config
        self.param_names = list(params_config.keys())
        self.response_names = list(responses_config.keys())
        
        # Results storage
        self.experimental_data = pd.DataFrame()
        self.iteration_history = []
        self.screening_metadata = {
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_experiments": 0,
            "converged": False,
            "best_parameters": None,
            "best_responses": None
        }
        
        # Analysis results
        self.parameter_importance = {}
        self.response_trends = {}
        self.optimization_recommendations = {}
        
        logger.info("Screening results manager initialized")
    
    def add_experimental_data(
        self,
        data_df: pd.DataFrame,
        iteration_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add experimental data and iteration information.
        
        Args:
            data_df: Experimental data DataFrame
            iteration_info: Information about the iteration
        """
        try:
            # Validate data format
            missing_params = set(self.param_names) - set(data_df.columns)
            if missing_params:
                raise ValueError(f"Missing parameter columns: {missing_params}")
            
            missing_responses = set(self.response_names) - set(data_df.columns)
            if missing_responses:
                logger.warning(f"Missing response columns: {missing_responses}")
            
            # Add data
            if self.experimental_data.empty:
                self.experimental_data = data_df.copy()
            else:
                self.experimental_data = pd.concat(
                    [self.experimental_data, data_df], ignore_index=True
                )
            
            # Update metadata
            self.screening_metadata["total_experiments"] = len(self.experimental_data)
            
            # Add iteration info if provided
            if iteration_info:
                iteration_record = {
                    "timestamp": datetime.now().isoformat(),
                    "data_points_added": len(data_df),
                    "total_experiments": len(self.experimental_data),
                    **iteration_info
                }
                self.iteration_history.append(iteration_record)
            
            logger.info(f"Added {len(data_df)} experimental data points. "
                       f"Total: {len(self.experimental_data)}")
            
        except Exception as e:
            logger.error(f"Error adding experimental data: {e}")
            raise
    
    def analyze_parameter_effects(self) -> Dict[str, Any]:
        """
        Analyze parameter effects on responses using correlation and sensitivity analysis.
        
        Returns:
            Dict[str, Any]: Parameter effect analysis results
        """
        try:
            if self.experimental_data.empty:
                logger.warning("No experimental data available for parameter analysis")
                return {}
            
            analysis_results = {
                "correlations": {},
                "sensitivities": {},
                "rankings": {}
            }
            
            # Calculate correlations between parameters and responses
            for response_name in self.response_names:
                if response_name not in self.experimental_data.columns:
                    continue
                
                response_correlations = {}
                response_data = self.experimental_data[response_name].dropna()
                
                if len(response_data) < 3:
                    logger.warning(f"Insufficient data for analyzing response '{response_name}'")
                    continue
                
                for param_name in self.param_names:
                    param_data = self.experimental_data[param_name]
                    param_config = self.params_config[param_name]
                    
                    # Skip categorical parameters for correlation analysis
                    if param_config["type"] == "categorical":
                        continue
                    
                    # Only analyze if both parameter and response data are available
                    valid_indices = response_data.index.intersection(param_data.index)
                    if len(valid_indices) < 3:
                        continue
                    
                    valid_param_data = param_data.loc[valid_indices]
                    valid_response_data = response_data.loc[valid_indices]
                    
                    # Calculate correlation
                    if valid_param_data.var() > 1e-8 and valid_response_data.var() > 1e-8:
                        correlation = valid_param_data.corr(valid_response_data)
                        if not np.isnan(correlation):
                            response_correlations[param_name] = float(correlation)
                
                analysis_results["correlations"][response_name] = response_correlations
                
                # Rank parameters by absolute correlation
                if response_correlations:
                    ranked_params = sorted(
                        response_correlations.items(),
                        key=lambda x: abs(x[1]),
                        reverse=True
                    )
                    analysis_results["rankings"][response_name] = [
                        {"parameter": param, "correlation": corr, "abs_correlation": abs(corr)}
                        for param, corr in ranked_params
                    ]
            
            # Calculate overall parameter importance across all responses
            param_importance_scores = {}
            for param_name in self.param_names:
                importance_score = 0.0
                response_count = 0
                
                for response_name in self.response_names:
                    if (response_name in analysis_results["correlations"] and
                        param_name in analysis_results["correlations"][response_name]):
                        
                        correlation = analysis_results["correlations"][response_name][param_name]
                        importance_score += abs(correlation)
                        response_count += 1
                
                if response_count > 0:
                    param_importance_scores[param_name] = importance_score / response_count
                else:
                    param_importance_scores[param_name] = 0.0
            
            # Rank parameters by overall importance
            overall_ranking = sorted(
                param_importance_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            analysis_results["overall_parameter_importance"] = [
                {"parameter": param, "importance_score": score}
                for param, score in overall_ranking
            ]
            
            # Store results
            self.parameter_importance = analysis_results
            
            logger.info("Parameter effects analysis completed")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing parameter effects: {e}")
            return {}
    
    def analyze_response_trends(self) -> Dict[str, Any]:
        """
        Analyze trends and performance for each response variable.
        
        Returns:
            Dict[str, Any]: Response trend analysis results
        """
        try:
            if self.experimental_data.empty:
                logger.warning("No experimental data available for trend analysis")
                return {}
            
            trend_results = {}
            
            for response_name in self.response_names:
                if response_name not in self.experimental_data.columns:
                    continue
                
                response_data = self.experimental_data[response_name].dropna()
                
                if len(response_data) < 2:
                    logger.warning(f"Insufficient data for trend analysis of '{response_name}'")
                    continue
                
                # Basic statistics
                stats = {
                    "count": len(response_data),
                    "mean": float(response_data.mean()),
                    "std": float(response_data.std()),
                    "min": float(response_data.min()),
                    "max": float(response_data.max()),
                    "range": float(response_data.max() - response_data.min())
                }
                
                # Goal-specific analysis
                response_config = self.responses_config.get(response_name, {})
                goal = response_config.get("goal", "None")
                
                if goal == "Maximize":
                    stats["best_value"] = stats["max"]
                    stats["best_index"] = int(response_data.idxmax())
                    stats["improvement_potential"] = "Higher values preferred"
                elif goal == "Minimize":
                    stats["best_value"] = stats["min"]
                    stats["best_index"] = int(response_data.idxmin())
                    stats["improvement_potential"] = "Lower values preferred"
                elif goal == "Target":
                    target_value = response_config.get("target", stats["mean"])
                    deviations = np.abs(response_data - target_value)
                    best_idx = deviations.idxmin()
                    stats["best_value"] = float(response_data.loc[best_idx])
                    stats["best_index"] = int(best_idx)
                    stats["target_value"] = float(target_value)
                    stats["best_deviation"] = float(deviations.min())
                    stats["improvement_potential"] = f"Target: {target_value}"
                
                # Trend over time (if we have iteration history)
                if len(self.iteration_history) > 1:
                    # Simple trend: compare first half vs second half
                    mid_point = len(response_data) // 2
                    if mid_point > 0:
                        first_half_mean = response_data.iloc[:mid_point].mean()
                        second_half_mean = response_data.iloc[mid_point:].mean()
                        
                        if goal == "Maximize":
                            trend_direction = "improving" if second_half_mean > first_half_mean else "declining"
                        elif goal == "Minimize":
                            trend_direction = "improving" if second_half_mean < first_half_mean else "declining"
                        else:  # Target
                            target_value = response_config.get("target", stats["mean"])
                            first_deviation = abs(first_half_mean - target_value)
                            second_deviation = abs(second_half_mean - target_value)
                            trend_direction = "improving" if second_deviation < first_deviation else "declining"
                        
                        stats["trend_direction"] = trend_direction
                        stats["first_half_mean"] = float(first_half_mean)
                        stats["second_half_mean"] = float(second_half_mean)
                
                trend_results[response_name] = stats
            
            # Store results
            self.response_trends = trend_results
            
            logger.info("Response trend analysis completed")
            return trend_results
            
        except Exception as e:
            logger.error(f"Error analyzing response trends: {e}")
            return {}
    
    def get_best_parameters(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Identify the best parameter combination and corresponding responses.
        
        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: Best parameters and responses
        """
        try:
            if self.experimental_data.empty:
                logger.warning("No experimental data available to find best parameters")
                return {}, {}
            
            # For multiple objectives, use simple weighted scoring
            # (More sophisticated methods can be implemented later)
            
            if len(self.response_names) == 1:
                # Single objective optimization
                response_name = self.response_names[0]
                response_config = self.responses_config[response_name]
                goal = response_config.get("goal", "Maximize")
                
                if goal == "Maximize":
                    best_idx = self.experimental_data[response_name].idxmax()
                elif goal == "Minimize":
                    best_idx = self.experimental_data[response_name].idxmin()
                else:  # Target
                    target_value = response_config.get("target", 0)
                    deviations = np.abs(self.experimental_data[response_name] - target_value)
                    best_idx = deviations.idxmin()
            
            else:
                # Multi-objective: composite scoring
                composite_scores = np.zeros(len(self.experimental_data))
                
                for response_name in self.response_names:
                    if response_name not in self.experimental_data.columns:
                        continue
                    
                    values = self.experimental_data[response_name].values
                    response_config = self.responses_config[response_name]
                    goal = response_config.get("goal", "Maximize")
                    
                    # Normalize values to [0, 1]
                    if values.max() - values.min() > 1e-8:
                        if goal == "Maximize":
                            normalized = (values - values.min()) / (values.max() - values.min())
                        elif goal == "Minimize":
                            normalized = (values.max() - values) / (values.max() - values.min())
                        else:  # Target
                            target_value = response_config.get("target", values.mean())
                            deviations = np.abs(values - target_value)
                            max_deviation = deviations.max()
                            if max_deviation > 1e-8:
                                normalized = 1.0 - (deviations / max_deviation)
                            else:
                                normalized = np.ones_like(values)
                    else:
                        normalized = np.ones_like(values)
                    
                    composite_scores += normalized
                
                best_idx = np.argmax(composite_scores)
            
            # Extract best parameters and responses
            best_row = self.experimental_data.iloc[best_idx]
            
            # Extract parameters with proper type conversion
            best_params = {}
            for name in self.param_names:
                raw_value = best_row[name]
                
                # Convert numpy types to Python types
                if hasattr(raw_value, 'item'):
                    raw_value = raw_value.item()
                
                # Type-specific conversion based on parameter configuration
                if name in self.params_config:
                    param_config = self.params_config[name]
                    param_type = param_config.get("type", "continuous")
                    
                    if param_type == "discrete":
                        # Ensure discrete parameters are integers
                        best_params[name] = int(round(float(raw_value)))
                    elif param_type == "continuous":
                        # Ensure continuous parameters are floats
                        best_params[name] = float(raw_value)
                    elif param_type == "categorical":
                        # Ensure categorical parameters are strings
                        best_params[name] = str(raw_value)
                    else:
                        # Fallback for unknown types
                        best_params[name] = raw_value
                else:
                    # No configuration available, use raw value
                    best_params[name] = raw_value
            
            best_responses = {
                name: best_row[name] for name in self.response_names
                if name in best_row and not pd.isna(best_row[name])
            }
            
            # Update metadata
            self.screening_metadata["best_parameters"] = best_params
            self.screening_metadata["best_responses"] = best_responses
            
            logger.info(f"Best parameters identified: {best_params}")
            return best_params, best_responses
            
        except Exception as e:
            logger.error(f"Error finding best parameters: {e}")
            return {}, {}
    
    def generate_optimization_recommendations(self) -> Dict[str, Any]:
        """
        Generate recommendations for the next optimization phase.
        
        Returns:
            Dict[str, Any]: Optimization recommendations
        """
        try:
            recommendations = {
                "screening_summary": {
                    "total_experiments": len(self.experimental_data),
                    "iterations_completed": len(self.iteration_history),
                    "converged": self.screening_metadata.get("converged", False)
                },
                "parameter_recommendations": {},
                "design_space_recommendations": {},
                "optimization_strategy": {},
                "next_steps": []
            }
            
            # Analyze parameter importance if not already done
            if not self.parameter_importance:
                self.analyze_parameter_effects()
            
            # Analyze response trends if not already done
            if not self.response_trends:
                self.analyze_response_trends()
            
            # Get best parameters
            best_params, best_responses = self.get_best_parameters()
            
            if best_params:
                # Parameter-specific recommendations
                param_recommendations = {}
                
                # Use parameter importance to suggest focus parameters
                if "overall_parameter_importance" in self.parameter_importance:
                    important_params = self.parameter_importance["overall_parameter_importance"][:3]  # Top 3
                    param_recommendations["high_importance_parameters"] = [
                        p["parameter"] for p in important_params
                    ]
                
                # Suggest design space size based on parameter variability
                param_ranges = {}
                for param_name in self.param_names:
                    values = self.experimental_data[param_name]
                    param_config = self.params_config[param_name]
                    
                    if param_config["type"] in ["continuous", "discrete"]:
                        bounds = param_config["bounds"]
                        range_explored = (values.max() - values.min()) / (bounds[1] - bounds[0])
                        param_ranges[param_name] = {
                            "range_explored": float(range_explored),
                            "recommendation": "narrow_focus" if range_explored > 0.5 else "expand_search"
                        }
                
                param_recommendations["parameter_ranges"] = param_ranges
                recommendations["parameter_recommendations"] = param_recommendations
                
                # Design space recommendations
                design_recommendations = {
                    "center_point": best_params,
                    "suggested_radius": 0.15,  # Default radius
                    "design_type": "ccd",  # Central Composite Design
                    "estimated_points": 2**len(self.param_names) + 2*len(self.param_names) + 1  # CCD formula
                }
                
                # Adjust radius based on convergence and exploration
                if self.screening_metadata.get("converged", False):
                    design_recommendations["suggested_radius"] = 0.1  # Tighter focus if converged
                else:
                    design_recommendations["suggested_radius"] = 0.2  # Broader if not converged
                
                recommendations["design_space_recommendations"] = design_recommendations
                
                # Optimization strategy
                optimization_strategy = {
                    "primary_objectives": [
                        name for name in self.response_names
                        if self.responses_config[name].get("goal") in ["Maximize", "Minimize", "Target"]
                    ],
                    "multi_objective": len(self.response_names) > 1,
                    "suggested_method": "bayesian_optimization",
                    "expected_experiments": min(50, max(20, 5 * len(self.param_names)))
                }
                
                recommendations["optimization_strategy"] = optimization_strategy
                
                # Next steps
                next_steps = [
                    "Generate design space around best parameters",
                    "Configure main Bayesian optimization software",
                    "Set up multi-objective optimization if applicable",
                    "Plan experimental validation campaign"
                ]
                
                if not self.screening_metadata.get("converged", False):
                    next_steps.insert(0, "Consider additional screening iterations")
                
                recommendations["next_steps"] = next_steps
            
            # Store recommendations
            self.optimization_recommendations = recommendations
            
            logger.info("Optimization recommendations generated")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
            return {}
    
    def export_results(self, filepath: str, format: str = "json") -> bool:
        """
        Export screening results to file.
        
        Args:
            filepath: Output file path
            format: Export format ("json", "pickle", "excel")
            
        Returns:
            bool: Success status
        """
        try:
            if format.lower() == "json":
                # Prepare JSON-serializable data
                export_data = {
                    "metadata": self.screening_metadata,
                    "params_config": self.params_config,
                    "responses_config": self.responses_config,
                    "experimental_data": self.experimental_data.to_dict(orient="records"),
                    "iteration_history": self.iteration_history,
                    "parameter_importance": self.parameter_importance,
                    "response_trends": self.response_trends,
                    "optimization_recommendations": self.optimization_recommendations
                }
                
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
            
            elif format.lower() == "pickle":
                export_data = {
                    "metadata": self.screening_metadata,
                    "params_config": self.params_config,
                    "responses_config": self.responses_config,
                    "experimental_data": self.experimental_data,
                    "iteration_history": self.iteration_history,
                    "parameter_importance": self.parameter_importance,
                    "response_trends": self.response_trends,
                    "optimization_recommendations": self.optimization_recommendations
                }
                
                with open(filepath, 'wb') as f:
                    pickle.dump(export_data, f)
            
            elif format.lower() == "excel":
                with pd.ExcelWriter(filepath) as writer:
                    # Export experimental data
                    self.experimental_data.to_excel(writer, sheet_name="Experimental_Data", index=False)
                    
                    # Export summary information
                    summary_data = []
                    summary_data.append(["Total Experiments", len(self.experimental_data)])
                    summary_data.append(["Iterations", len(self.iteration_history)])
                    summary_data.append(["Converged", self.screening_metadata.get("converged", False)])
                    
                    if self.screening_metadata.get("best_parameters"):
                        for param, value in self.screening_metadata["best_parameters"].items():
                            summary_data.append([f"Best {param}", value])
                    
                    summary_df = pd.DataFrame(summary_data, columns=["Metric", "Value"])
                    summary_df.to_excel(writer, sheet_name="Summary", index=False)
                    
                    # Export parameter importance if available
                    if "overall_parameter_importance" in self.parameter_importance:
                        importance_data = self.parameter_importance["overall_parameter_importance"]
                        importance_df = pd.DataFrame(importance_data)
                        importance_df.to_excel(writer, sheet_name="Parameter_Importance", index=False)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Results exported to {filepath} in {format} format")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            return False
    
    def load_results(self, filepath: str, format: str = "json") -> bool:
        """
        Load screening results from file.
        
        Args:
            filepath: Input file path
            format: File format ("json", "pickle", "excel")
            
        Returns:
            bool: Success status
        """
        try:
            if format.lower() == "json":
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                self.screening_metadata = data.get("metadata", {})
                self.params_config = data.get("params_config", {})
                self.responses_config = data.get("responses_config", {})
                self.experimental_data = pd.DataFrame(data.get("experimental_data", []))
                self.iteration_history = data.get("iteration_history", [])
                self.parameter_importance = data.get("parameter_importance", {})
                self.response_trends = data.get("response_trends", {})
                self.optimization_recommendations = data.get("optimization_recommendations", {})
            
            elif format.lower() == "pickle":
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
                
                for key, value in data.items():
                    setattr(self, key, value)
            
            else:
                raise ValueError(f"Unsupported load format: {format}")
            
            # Update derived attributes
            self.param_names = list(self.params_config.keys())
            self.response_names = list(self.responses_config.keys())
            
            logger.info(f"Results loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading results: {e}")
            return False
    
    def get_results_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of all screening results.
        
        Returns:
            Dict[str, Any]: Complete results summary
        """
        try:
            # Update end time
            self.screening_metadata["end_time"] = datetime.now().isoformat()
            
            # Ensure all analyses are up to date
            if not self.parameter_importance:
                self.analyze_parameter_effects()
            
            if not self.response_trends:
                self.analyze_response_trends()
            
            if not self.optimization_recommendations:
                self.generate_optimization_recommendations()
            
            best_params, best_responses = self.get_best_parameters()
            
            summary = {
                "metadata": self.screening_metadata,
                "experimental_summary": {
                    "total_experiments": len(self.experimental_data),
                    "parameters": self.param_names,
                    "responses": self.response_names,
                    "iterations": len(self.iteration_history)
                },
                "best_solution": {
                    "parameters": best_params,
                    "responses": best_responses
                },
                "parameter_analysis": self.parameter_importance,
                "response_analysis": self.response_trends,
                "recommendations": self.optimization_recommendations
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating results summary: {e}")
            return {"error": str(e)}