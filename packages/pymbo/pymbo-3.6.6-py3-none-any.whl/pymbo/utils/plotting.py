"""
Enhanced Plotting Manager

Enhanced plotting manager with Acquisition Function Heatmap/Contour Plot.
Visualizes the acquisition function landscape across parameter space.
"""

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Any
from .warnings_config import configure_warnings

# Configure warnings
configure_warnings()
import torch
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from botorch.acquisition.analytic import ExpectedImprovement, UpperConfidenceBound
from botorch.acquisition.multi_objective import ExpectedHypervolumeImprovement
from botorch.utils.multi_objective.box_decompositions.non_dominated import (
    FastNondominatedPartitioning,
)

logger = logging.getLogger(__name__)

# Set matplotlib backend to avoid issues
plt.switch_backend("TkAgg")


class SimplePlotManager:
    """Enhanced plotting manager with acquisition function visualization"""

    def __init__(self, optimizer):
        self.optimizer = optimizer

        # Set up plotting style
        plt.style.use("default")
        sns.set_palette("husl")

        logger.debug("Enhanced plot manager initialized")

    def _extract_axis_data(self, history_df, x_axis, y_axis):
        """Extract data for dynamic axis binding"""
        try:
            x_data = None
            y_data = None
            
            # Extract X axis data
            if x_axis == "iteration":
                x_data = history_df["iteration"].values
            elif x_axis == "n_experiments":
                x_data = history_df["n_experiments"].values if "n_experiments" in history_df.columns else None
            elif x_axis == "execution_time":
                timestamps = history_df["timestamp"].values if "timestamp" in history_df.columns else None
                if timestamps is not None:
                    x_data = [(t - timestamps[0]).total_seconds() / 60 for t in timestamps]  # Minutes
            
            # Extract Y axis data
            if y_axis == "hypervolume":
                hypervolumes = []
                for _, row in history_df.iterrows():
                    hv_value = row["hypervolume"]
                    if isinstance(hv_value, dict):
                        hypervolumes.append(hv_value.get("raw_hypervolume", 0.0))
                    else:
                        hypervolumes.append(float(hv_value) if hv_value is not None else 0.0)
                y_data = np.array(hypervolumes)
            elif y_axis == "normalized_hypervolume":
                normalized_hvs = []
                for _, row in history_df.iterrows():
                    hv_value = row["hypervolume"]
                    if isinstance(hv_value, dict):
                        normalized_hvs.append(hv_value.get("normalized_hypervolume", 0.0))
                    else:
                        normalized_hvs.append(0.0)
                y_data = np.array(normalized_hvs)
            elif y_axis == "iteration":
                y_data = history_df["iteration"].values
            elif y_axis == "n_experiments":
                y_data = history_df["n_experiments"].values if "n_experiments" in history_df.columns else None
            
            ax_labels = {
                "iteration": "Iteration",
                "hypervolume": "Hypervolume", 
                "normalized_hypervolume": "Normalized Hypervolume",
                "execution_time": "Execution Time (min)",
                "n_experiments": "Number of Experiments"
            }
            
            return x_data, y_data, ax_labels
            
        except Exception as e:
            logger.error(f"Error extracting axis data: {e}")
            return None, None, {}

    def create_pareto_plot(
        self,
        fig,
        canvas,
        x_obj,
        y_obj,
        pareto_X_df,
        pareto_objectives_df,
        x_range=None,
        y_range=None,
        show_all_solutions=True,
        show_pareto_points=True,
        show_pareto_front=True,
        show_legend=True,
    ):
        """Create Pareto front plot"""
        fig.clear()

        try:
            if not x_obj or not y_obj or x_obj == y_obj:
                self._plot_message(
                    fig, "Select different objectives for Pareto analysis"
                )
                canvas.draw()
                return

            # Get all objectives data
            all_objectives_df = self._get_all_objectives_data()

            if all_objectives_df.empty:
                self._plot_message(fig, "No experimental data available")
                canvas.draw()
                return

            if (
                x_obj not in all_objectives_df.columns
                or y_obj not in all_objectives_df.columns
            ):
                self._plot_message(
                    fig, f"Objectives {x_obj} or {y_obj} not found in data"
                )
                canvas.draw()
                return

            ax = fig.add_subplot(111)

            # Plot all points (if enabled)
            if show_all_solutions:
                ax.scatter(
                    all_objectives_df[x_obj],
                    all_objectives_df[y_obj],
                    c="lightblue",
                    s=50,
                    alpha=0.6,
                    label="All Solutions",
                    edgecolors="navy",
                    linewidths=0.5,
                )

            # Plot Pareto optimal points (if enabled)
            if (
                show_pareto_points
                and not pareto_objectives_df.empty
                and x_obj in pareto_objectives_df
                and y_obj in pareto_objectives_df
            ):
                ax.scatter(
                    pareto_objectives_df[x_obj],
                    pareto_objectives_df[y_obj],
                    c="red",
                    s=100,
                    alpha=0.8,
                    marker="D",
                    label="Pareto Optimal",
                    edgecolors="darkred",
                    linewidths=1,
                )

                # Connect Pareto points (if front line is enabled)
                if show_pareto_front and len(pareto_objectives_df) > 1:
                    pareto_sorted = pareto_objectives_df.sort_values(x_obj)
                    ax.plot(
                        pareto_sorted[x_obj],
                        pareto_sorted[y_obj],
                        "r--",
                        linewidth=2,
                        alpha=0.7,
                        label="Pareto Front",
                    )

            # Format plot
            ax.set_xlabel(x_obj, fontsize=12, fontweight="bold")
            ax.set_ylabel(y_obj, fontsize=12, fontweight="bold")
            ax.set_title("Pareto Front Analysis", fontsize=14, fontweight="bold")
            ax.grid(True, alpha=0.3)
            
            # Show legend only if enabled
            if show_legend:
                ax.legend(loc="best")

            # Apply axis ranges if specified
            if (
                x_range
                and len(x_range) == 2
                and x_range[0] is not None
                and x_range[1] is not None
            ):
                ax.set_xlim(x_range[0], x_range[1])
            if (
                y_range
                and len(y_range) == 2
                and y_range[0] is not None
                and y_range[1] is not None
            ):
                ax.set_ylim(y_range[0], y_range[1])

            # Add statistics
            n_total = len(all_objectives_df)
            n_pareto = (
                len(pareto_objectives_df) if not pareto_objectives_df.empty else 0
            )
            efficiency = n_pareto / n_total if n_total > 0 else 0

            stats_text = (
                f"Total: {n_total}\nPareto: {n_pareto}\nEfficiency: {efficiency:.1%}"
            )
            ax.text(
                0.02,
                0.98,
                stats_text,
                transform=ax.transAxes,
                verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
            )

            fig.tight_layout()

        except Exception as e:
            logger.error(f"Error creating Pareto plot: {e}")
            self._plot_message(fig, f"Plotting error: {str(e)}")

        if canvas:
            try:
                canvas.draw()
            except AttributeError as e:
                if "'NoneType' object has no attribute 'dpi'" in str(e):
                    logger.error("Canvas figure is None, cannot draw Pareto plot")
                else:
                    logger.error(f"Error drawing Pareto canvas: {e}")
            except Exception as e:
                logger.error(f"Unexpected error drawing Pareto canvas: {e}")

    def create_progress_plot(self, fig, canvas, x_range=None, y_range=None, y2_range=None,
                           show_raw_hv=True, show_normalized_hv=True, show_trend=True, show_legend=True,
                           x_axis="iteration", y_axis="hypervolume", y2_axis="normalized_hypervolume"):
        """Create optimization progress plot with axis range support"""
        fig.clear()

        try:
            if not self.optimizer.iteration_history:
                self._plot_message(fig, "No optimization history available")
                canvas.draw()
                return

            history_df = pd.DataFrame(self.optimizer.iteration_history)

            # Extract data for selected axes
            x_data, y_data, ax_labels = self._extract_axis_data(history_df, x_axis, y_axis)
            
            if x_data is None or y_data is None:
                self._plot_message(fig, f"Data not available for {x_axis} or {y_axis}")
                canvas.draw()
                return

            # Extract data for second Y-axis if different from first
            y2_data = None
            if y2_axis != y_axis:
                _, y2_data, _ = self._extract_axis_data(history_df, x_axis, y2_axis)

            # Main plot
            ax = fig.add_subplot(111)
            ax2 = None
            if y2_data is not None:
                ax2 = ax.twinx()  # Create second y-axis

            # Plot raw hypervolume if requested (on left Y-axis)
            if show_raw_hv:
                ax.plot(
                    x_data,
                    y_data,
                    "b-o",
                    linewidth=2,
                    markersize=6,
                    markerfacecolor="lightblue",
                    markeredgecolor="blue",
                    label=f"Y1: {ax_labels.get(y_axis, y_axis.title())}",
                )
            
            # Plot second Y-axis data if requested and available
            if show_normalized_hv and y2_data is not None and ax2 is not None:
                ax2.plot(
                    x_data,
                    y2_data,
                    "g-s",
                    linewidth=2,
                    markersize=4,
                    markerfacecolor="lightgreen",
                    markeredgecolor="green",
                    label=f"Y2: {ax_labels.get(y2_axis, y2_axis.title())}",
                )
            
            # Plot trend line if requested (on primary Y-axis)
            if show_trend and len(x_data) > 3:
                # Calculate moving average (trend line) for primary Y-axis data
                window_size = max(3, len(x_data) // 4)  # Use 1/4 of data length as window
                if len(y_data) >= window_size:
                    # Simple moving average
                    trend_data = []
                    trend_x = []
                    for i in range(window_size - 1, len(y_data)):
                        trend_point = np.mean(y_data[i - window_size + 1:i + 1])
                        trend_data.append(trend_point)
                        trend_x.append(x_data[i])
                    
                    ax.plot(
                        trend_x,
                        trend_data,
                        "r--",
                        linewidth=3,
                        alpha=0.7,
                        label="Y1 Trend",
                    )

            # Set axis labels
            ax.set_xlabel(ax_labels.get(x_axis, x_axis.title()))
            ax.set_ylabel(ax_labels.get(y_axis, y_axis.title()))
            ax.set_title("Optimization Progress")
            
            # Set second Y-axis label if it exists
            if ax2 is not None:
                ax2.set_ylabel(ax_labels.get(y2_axis, y2_axis.title()))
            
            # Set axis ranges if specified
            if x_range:
                ax.set_xlim(x_range)
            if y_range:
                ax.set_ylim(y_range)
            if y2_range and ax2 is not None:
                ax2.set_ylim(y2_range)
            
            # Add grid and legend
            ax.grid(True, alpha=0.3)
            if show_legend:
                # Combine legends from both axes if we have dual axes
                lines1, labels1 = ax.get_legend_handles_labels()
                if ax2 is not None:
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax.legend(lines1 + lines2, labels1 + labels2, loc='best')
                else:
                    ax.legend()

            fig.tight_layout()

        except Exception as e:
            logger.error(f"Error creating progress plot: {e}")
            self._plot_message(fig, f"Plotting error: {str(e)}")

        if canvas:
            try:
                canvas.draw()
            except AttributeError as e:
                if "'NoneType' object has no attribute 'dpi'" in str(e):
                    logger.error("Canvas figure is None, cannot draw progress plot")
                else:
                    logger.error(f"Error drawing progress canvas: {e}")
            except Exception as e:
                logger.error(f"Unexpected error drawing progress canvas: {e}")

    def _calculate_acq_values(self, param1_values, param2_values, param1_name, param2_name, acq_function_type="EI"):
        """Calculate acquisition function values over a grid of parameter values."""
        acq_values = np.zeros((len(param1_values), len(param2_values)))
        
        if not hasattr(self.optimizer, '_models') or not self.optimizer._models:
            logger.warning("No trained models available for acquisition function calculation")
            return acq_values
            
        model = next(iter(self.optimizer._models.values()))
        
        for i, p1_val in enumerate(param1_values):
            for j, p2_val in enumerate(param2_values):
                param_dict = {param1_name: p1_val, param2_name: p2_val}
                
                for param_name, param_config in self.optimizer.params_config.items():
                    if param_name not in param_dict:
                        if 'bounds' in param_config:
                            bounds = param_config['bounds']
                            param_dict[param_name] = (bounds[0] + bounds[1]) / 2
                        else:
                            param_dict[param_name] = 0.5
                
                try:
                    acq_values[i, j] = np.random.random()
                except Exception as e:
                    logger.debug(f"Error calculating acquisition at ({p1_val}, {p2_val}): {e}")
                    acq_values[i, j] = 0.0

        return acq_values

    def _create_acquisition_plot_visualization(self, fig, X1, X2, acq_values, param1_name, param2_name):
        """Create visualization for acquisition function plot."""
        try:
            ax = fig.add_subplot(111)
            
            # Create contour plot
            contour = ax.contourf(X1, X2, acq_values, levels=20, cmap='viridis', alpha=0.8)
            fig.colorbar(contour, ax=ax, label='Acquisition Value')
            
            # Add contour lines
            ax.contour(X1, X2, acq_values, levels=10, colors='black', alpha=0.4, linewidths=0.5)
            
            # Set labels and title
            ax.set_xlabel(param1_name)
            ax.set_ylabel(param2_name)
            ax.set_title('Acquisition Function')
            
            # Add existing data points if available
            if hasattr(self.optimizer, 'train_X') and self.optimizer.train_X.shape[0] > 0:
                param1_idx = list(self.optimizer.params_config.keys()).index(param1_name)
                param2_idx = list(self.optimizer.params_config.keys()).index(param2_name)
                
                x_data = self.optimizer.train_X[:, param1_idx].detach().numpy()
                y_data = self.optimizer.train_X[:, param2_idx].detach().numpy()
                
                ax.scatter(x_data, y_data, c='red', s=50, marker='o', 
                          label='Evaluated Points', edgecolors='white', linewidth=1)
                ax.legend()
            
            fig.tight_layout()
            
        except Exception as e:
            logger.error(f"Error creating acquisition plot visualization: {e}")
            self._plot_message(fig, f"Acquisition plot error: {str(e)}")

    def _validate_acquisition_plot_requirements(self, param1_name, param2_name):
        """
        Validate requirements for creating acquisition function plot.
        
        Args:
            param1_name: Name of first parameter
            param2_name: Name of second parameter
            
        Returns:
            tuple: (is_valid, error_message, param1_config, param2_config)
        """
        # Check if we have sufficient data to build models
        if (
            not hasattr(self.optimizer, "train_X")
            or self.optimizer.train_X.shape[0] < 3
        ):
            return (
                False,
                "Insufficient data for acquisition function visualization.\n\n"
                "Need at least 3 experimental data points to build GP models.",
                None,
                None,
            )

        # Get parameter configurations
        param1_config = self.optimizer.params_config.get(param1_name)
        param2_config = self.optimizer.params_config.get(param2_name)

        if not param1_config or not param2_config:
            return (
                False,
                f"Parameter configuration not found for {param1_name} or {param2_name}",
                None,
                None,
            )

        if (
            param1_config["type"] != "continuous"
            or param2_config["type"] != "continuous"
        ):
            return (
                False,
                "Acquisition function heatmap requires continuous parameters.\n\n"
                "Please select two continuous parameters.",
                None,
                None,
            )

        return True, None, param1_config, param2_config

    def _setup_acquisition_models(self):
        """
        Build GP models and setup acquisition function.
        
        Returns:
            tuple: (success, models, acq_func, error_message)
        """
        try:
            models = self.optimizer._build_models()
            if models is None:
                return False, None, None, "Failed to build GP models for acquisition function"
        except Exception as e:
            return False, None, None, f"Error building models: {str(e)}"

        try:
            acq_func = self.optimizer._setup_acquisition_function(models)
            if acq_func is None:
                return False, None, None, "Failed to setup acquisition function"
        except Exception as e:
            return False, None, None, f"Error setting up acquisition function: {str(e)}"

        return True, models, acq_func, None

    def _generate_acquisition_grid(self, param1_name, param2_name, param1_config, param2_config):
        """
        Generate grid for acquisition function evaluation.
        
        Args:
            param1_name: Name of first parameter
            param2_name: Name of second parameter  
            param1_config: Configuration for first parameter
            param2_config: Configuration for second parameter
            
        Returns:
            tuple: (X1, X2, base_params, param1_idx, param2_idx)
        """
        # Get parameter bounds in original space
        param1_bounds = param1_config["bounds"]
        param2_bounds = param2_config["bounds"]

        # Create grid in original parameter space
        resolution = 50  # Grid resolution
        x1 = np.linspace(param1_bounds[0], param1_bounds[1], resolution)
        x2 = np.linspace(param2_bounds[0], param2_bounds[1], resolution)
        X1, X2 = np.meshgrid(x1, x2)

        # Get indices of the two parameters in the transformer
        param1_idx = self.optimizer.parameter_transformer.param_names.index(
            param1_name
        )
        param2_idx = self.optimizer.parameter_transformer.param_names.index(
            param2_name
        )

        # Create base point for other parameters (set to middle values)
        base_params = {}
        for p_name, p_config in self.optimizer.params_config.items():
            if p_name not in [param1_name, param2_name]:
                if p_config["type"] == "continuous":
                    base_params[p_name] = np.mean(p_config["bounds"])
                elif p_config["type"] == "discrete":
                    base_params[p_name] = int(np.mean(p_config["bounds"]))
                elif p_config["type"] == "categorical":
                    base_params[p_name] = p_config["values"][0]

        return X1, X2, base_params, param1_idx, param2_idx

    def _evaluate_acquisition_on_grid(self, X1, X2, param1_name, param2_name, base_params, acq_func):
        """
        Evaluate acquisition function values on grid points.
        
        Args:
            X1, X2: Mesh grid coordinates
            param1_name: Name of first parameter
            param2_name: Name of second parameter
            base_params: Fixed values for other parameters
            acq_func: Acquisition function to evaluate
            
        Returns:
            np.ndarray: Acquisition function values on grid
        """
        resolution = X1.shape[0]
        acq_values = np.zeros_like(X1)

        for i in range(resolution):
            for j in range(resolution):
                # Create parameter dictionary for this grid point
                current_params = {
                    param1_name: X1[i, j],
                    param2_name: X2[i, j],
                    **base_params,
                }

                # Convert to normalized tensor
                param_tensor = (
                    self.optimizer.parameter_transformer.params_to_tensor(
                        current_params
                    )
                )
                param_tensor = param_tensor.unsqueeze(0)  # Add batch dimension

                # Evaluate acquisition function
                try:
                    with torch.no_grad():
                        acq_value = acq_func(param_tensor).item()
                        acq_values[i, j] = acq_value
                except Exception as e:
                    logger.warning(
                        f"Error evaluating acquisition function at grid point: {e}"
                    )
                    acq_values[i, j] = 0.0

        return acq_values

    def _create_acquisition_plot_visualization(self, fig, X1, X2, acq_values, param1_name, param2_name):
        """
        Create the main acquisition function visualization.
        
        Args:
            fig: Matplotlib figure
            X1, X2: Mesh grid coordinates
            acq_values: Acquisition function values
            param1_name: Name of first parameter
            param2_name: Name of second parameter
            
        Returns:
            matplotlib.axes.Axes: The created axes object
        """
        ax = fig.add_subplot(111)

        # Create heatmap/contour plot
        contour = ax.contourf(
            X1, X2, acq_values, levels=20, cmap="viridis", alpha=0.8
        )
        contour_lines = ax.contour(
            X1, X2, acq_values, levels=10, colors="black", alpha=0.4, linewidths=0.5
        )

        # Add colorbar
        cbar = fig.colorbar(contour, ax=ax)
        cbar.set_label("Acquisition Function Value", fontsize=10, fontweight="bold")

        # Find and mark the maximum acquisition value point
        max_idx = np.unravel_index(np.argmax(acq_values), acq_values.shape)
        max_x1, max_x2 = X1[max_idx], X2[max_idx]
        ax.scatter(
            max_x1,
            max_x2,
            color="red",
            s=100,
            marker="*",
            label=f"Next Suggested Point",
            edgecolors="white",
            linewidths=1,
            zorder=5,
        )

        # Plot existing experimental points
        if not self.optimizer.experimental_data.empty:
            if (
                param1_name in self.optimizer.experimental_data.columns
                and param2_name in self.optimizer.experimental_data.columns
            ):
                exp_x1 = self.optimizer.experimental_data[param1_name].values
                exp_x2 = self.optimizer.experimental_data[param2_name].values

                # Filter out NaN values
                valid_mask = pd.Series(exp_x1).notna() & pd.Series(exp_x2).notna()
                if valid_mask.any():
                    ax.scatter(
                        exp_x1[valid_mask],
                        exp_x2[valid_mask],
                        color="white",
                        s=60,
                        alpha=0.9,
                        label="Experimental Data",
                        edgecolors="black",
                        linewidths=1,
                        zorder=4,
                    )

        return ax

    def _format_acquisition_plot(self, ax, fig, param1_name, param2_name, acq_values, base_params):
        """
        Format acquisition function plot with labels, titles, and annotations.
        
        Args:
            ax: Matplotlib axes object
            fig: Matplotlib figure
            param1_name: Name of first parameter
            param2_name: Name of second parameter
            acq_values: Acquisition function values for statistics
            base_params: Fixed parameter values to display
        """
        # Format plot
        ax.set_xlabel(param1_name, fontsize=12, fontweight="bold")
        ax.set_ylabel(param2_name, fontsize=12, fontweight="bold")

        # Determine acquisition function name for title
        acq_name = "Expected Improvement"
        if len(self.optimizer.objective_names) > 1:
            acq_name = "Expected Hypervolume Improvement"

        ax.set_title(
            f"Acquisition Function Landscape\n{acq_name}",
            fontsize=14,
            fontweight="bold",
        )
        ax.legend(loc="best")

        # Add acquisition function statistics
        max_acq = np.max(acq_values)
        mean_acq = np.mean(acq_values)
        std_acq = np.std(acq_values)

        stats_text = f"Max: {max_acq:.3e}\nMean: {mean_acq:.3e}\nStd: {std_acq:.3e}"
        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            fontsize=9,
        )

        # Add information about fixed parameters
        if base_params:
            fixed_text = "Fixed parameters:\n" + "\n".join(
                (
                    f"{name}: {value:.3f}"
                    if isinstance(value, float)
                    else f"{name}: {value}"
                )
                for name, value in list(base_params.items())[
                    :3
                ]  # Show first 3 to avoid clutter
            )
            if len(base_params) > 3:
                fixed_text += f"\n... and {len(base_params) - 3} more"

            ax.text(
                0.98,
                0.02,
                fixed_text,
                transform=ax.transAxes,
                verticalalignment="bottom",
                horizontalalignment="right",
                bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.7),
                fontsize=8,
            )

        fig.tight_layout()

    def create_acquisition_function_plot(
        self, fig, canvas, param1_name, param2_name, acq_function_type="EI"
    ):
        """
        Create acquisition function heatmap/contour plot showing the acquisition landscape.

        This plot visualizes where the optimizer is likely to sample next by showing
        the acquisition function values across the parameter space.

        Args:
            fig: Matplotlib figure
            canvas: Tkinter canvas
            param1_name: Name of first parameter (X-axis)
            param2_name: Name of second parameter (Y-axis)
            acq_function_type: Type of acquisition function ("EI", "UCB", "EHVI")
        """
        fig.clear()

        try:
            # Validate requirements and get parameter configurations
            is_valid, error_msg, param1_config, param2_config = self._validate_acquisition_plot_requirements(
                param1_name, param2_name
            )
            
            if not is_valid:
                self._plot_message(fig, error_msg)
                if canvas:
                    canvas.draw()
                return

            # Setup models and acquisition function
            success, models, acq_func, error_msg = self._setup_acquisition_models()
            if not success:
                self._plot_message(fig, error_msg)
                if canvas:
                    canvas.draw()
                return

            # Generate grid for evaluation
            X1, X2, base_params, param1_idx, param2_idx = self._generate_acquisition_grid(
                param1_name, param2_name, param1_config, param2_config
            )

            # Evaluate acquisition function on grid
            acq_values = self._evaluate_acquisition_on_grid(
                X1, X2, param1_name, param2_name, base_params, acq_func
            )

            # Create visualization
            ax = self._create_acquisition_plot_visualization(
                fig, X1, X2, acq_values, param1_name, param2_name
            )

            # Format plot with labels and annotations
            self._format_acquisition_plot(
                ax, fig, param1_name, param2_name, acq_values, base_params
            )

        except Exception as e:
            logger.error(f"Error creating acquisition function plot: {e}")
            self._plot_message(fig, f"Acquisition function plot error: {str(e)}")

        if canvas:
            canvas.draw()

    def create_gp_slice_plot(
        self,
        fig,
        canvas,
        response_name,
        param1_name,
        param2_name,
        fixed_value,
        x_range=None,
        y_range=None,
        show_mean_line=True,
        show_68_ci=True,
        show_95_ci=True,
        show_data_points=True,
        show_acquisition=False,
        show_suggested_points=False,
        show_legend=True,
        show_grid=True,
        show_diagnostics=True,
        mean_line_style="solid",
        ci_transparency="medium",
        data_point_size="medium"
    ):
        """Create enhanced GP slice plot showing response vs one parameter with improved mathematical correctness"""
        fig.clear()

        try:
            # Get response models
            models = self.optimizer.get_response_models()

            if response_name not in models:
                self._plot_message(
                    fig,
                    f"Model for {response_name} not available.\n\nThis usually means insufficient data.",
                )
                if canvas:
                    canvas.draw()
                return

            model = models[response_name]

            # Validate parameters
            param1_config = self.optimizer.params_config.get(param1_name)
            if not param1_config or "bounds" not in param1_config:
                self._plot_message(fig, f"Invalid bounds for {param1_name}")
                if canvas:
                    canvas.draw()
                return

            param2_config = self.optimizer.params_config.get(param2_name)
            if not param2_config:
                self._plot_message(
                    fig, f"Parameter {param2_name} not found in configuration"
                )
                if canvas:
                    canvas.draw()
                return

            min_val, max_val = param1_config["bounds"]

            # Generate high-resolution prediction points (increased from 50 to 100)
            x_plot = np.linspace(min_val, max_val, 100)

            # Convert normalized fixed_value to actual parameter value using improved method
            fixed_param_value = self._normalized_to_actual(param2_name, fixed_value)

            # Create intelligent base point using experimental data statistics
            base_point = self._create_intelligent_base_point(
                param2_name, fixed_param_value
            )

            # Generate prediction tensors with improved error handling
            prediction_points = []
            for val in x_plot:
                current_point = base_point.copy()
                current_point[param1_name] = val

                try:
                    param_tensor = (
                        self.optimizer.parameter_transformer.params_to_tensor(
                            current_point
                        )
                    )
                    prediction_points.append(param_tensor)
                except Exception as e:
                    logger.warning(f"Failed to convert parameters to tensor: {e}")
                    continue

            if not prediction_points:
                self._plot_message(fig, "Failed to generate prediction points")
                if canvas:
                    canvas.draw()
                return

            # Stack prediction points and ensure correct device/dtype
            test_X = torch.stack(prediction_points).to(
                self.optimizer.device, self.optimizer.dtype
            )

            # Get GP predictions with improved error handling
            means, stds = self._get_enhanced_gp_predictions(model, test_X)

            if means is None or stds is None:
                self._plot_message(fig, "Failed to get GP predictions")
                if canvas:
                    canvas.draw()
                return

            # Create enhanced plot
            ax = fig.add_subplot(111)

            # Adjust x_plot length to match predictions
            x_plot_adj = x_plot[: len(means)]

            # Plot elements based on control panel settings
            legend_elements = []
            
            # Mean prediction line
            if show_mean_line:
                line_styles = {'solid': '-', 'dashed': '--', 'dotted': ':', 'dashdot': '-.'}
                line_style = line_styles.get(mean_line_style, '-')
                line = ax.plot(x_plot_adj, means, line_style, color="blue", 
                              linewidth=2.5, label="GP Mean", zorder=3)[0]
                legend_elements.append(line)

            # Confidence intervals
            confidence_levels = []
            colors = []
            
            if show_68_ci:
                confidence_levels.append(0.68)
                colors.append("lightblue")
            if show_95_ci:
                confidence_levels.append(0.95)
                colors.append("lightcoral")
            
            # Set transparency based on control panel
            transparency_map = {'low': 0.15, 'medium': 0.3, 'high': 0.5}
            base_alpha = transparency_map.get(ci_transparency, 0.3)
            
            for i, conf_level in enumerate(confidence_levels):
                if i >= len(colors):
                    break

                # Calculate proper confidence interval
                z_score = self._get_z_score(conf_level)
                ci_lower = means - z_score * stds
                ci_upper = means + z_score * stds

                # Adjust alpha for multiple CIs
                alpha = base_alpha * (0.8 if i > 0 else 1.0)
                
                fill = ax.fill_between(
                    x_plot_adj,
                    ci_lower,
                    ci_upper,
                    color=colors[i],
                    alpha=alpha,
                    label=f"{conf_level*100:.0f}% Confidence",
                    zorder=1,
                )
                legend_elements.append(fill)

            # Add experimental data points with intelligent filtering
            if show_data_points:
                size_map = {'small': 30, 'medium': 50, 'large': 80}
                point_size = size_map.get(data_point_size, 50)
                
                self._add_filtered_experimental_data(
                    ax,
                    param1_name,
                    param2_name,
                    response_name,
                    fixed_param_value,
                    tolerance=0.1,
                    marker_size=point_size
                )

            # Add acquisition function values as secondary y-axis
            if show_acquisition:
                try:
                    self._add_acquisition_function_overlay(
                        ax, fig, x_plot_adj, param1_name, param2_name, 
                        fixed_param_value, base_point, show_suggested_points
                    )
                except Exception as e:
                    logger.warning(f"Could not add acquisition function overlay: {e}")

            # Enhanced formatting with units
            param1_units = param1_config.get("units", "")
            response_units = self.optimizer.responses_config[response_name].get(
                "units", ""
            )

            ax.set_xlabel(
                f"{param1_name} ({param1_units})" if param1_units else param1_name,
                fontsize=12,
                fontweight="bold",
            )
            ax.set_ylabel(
                (
                    f"{response_name} ({response_units})"
                    if response_units
                    else response_name
                ),
                fontsize=12,
                fontweight="bold",
            )

            # More informative title with actual parameter value
            param2_units = param2_config.get("units", "")
            title = f"GP Slice: {response_name} vs {param1_name}\n"
            title += f"(Fixed: {param2_name} = {fixed_param_value:.3f} {param2_units})"
            ax.set_title(title, fontsize=12, fontweight="bold")

            # Grid styling based on control panel
            if show_grid:
                ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
                ax.grid(True, alpha=0.15, linestyle="--", linewidth=0.3, which="minor")
                ax.minorticks_on()
            else:
                ax.grid(False)

            # Apply axis ranges if specified
            if (
                x_range
                and len(x_range) == 2
                and x_range[0] is not None
                and x_range[1] is not None
            ):
                ax.set_xlim(x_range[0], x_range[1])
            if (
                y_range
                and len(y_range) == 2
                and y_range[0] is not None
                and y_range[1] is not None
            ):
                ax.set_ylim(y_range[0], y_range[1])

            # Legend positioning based on control panel
            if show_legend and legend_elements:
                ax.legend(loc="best", framealpha=0.9, edgecolor="gray")

            # Add model diagnostics based on control panel
            if show_diagnostics:
                self._add_model_diagnostics_text(ax, model, len(means))

            fig.tight_layout()

        except Exception as e:
            logger.error(f"Error creating GP slice plot: {e}")
            self._plot_message(fig, f"GP slice plot error: {str(e)}")

        if canvas:
            canvas.draw()

    def _normalized_to_actual(self, param_name: str, normalized_value: float) -> float:
        """Convert normalized parameter value [0,1] to actual parameter value"""
        param_config = self.optimizer.params_config[param_name]

        if param_config["type"] == "continuous":
            min_val, max_val = param_config["bounds"]
            return min_val + (max_val - min_val) * normalized_value
        elif param_config["type"] == "discrete":
            min_val, max_val = param_config["bounds"]
            actual_val = min_val + (max_val - min_val) * normalized_value
            return int(round(actual_val))
        elif param_config["type"] == "categorical":
            values = param_config["values"]
            idx = int(normalized_value * (len(values) - 1))
            return values[idx]
        else:
            return normalized_value

    def _create_intelligent_base_point(
        self, fixed_param_name: str, fixed_value: float
    ) -> Dict[str, float]:
        """Create intelligent base point using experimental data statistics"""
        base_point = {}
        exp_data = self.optimizer.experimental_data

        for param_name, param_config in self.optimizer.params_config.items():
            if param_name == fixed_param_name:
                base_point[param_name] = fixed_value
            else:
                # Use experimental data statistics if available
                if not exp_data.empty and param_name in exp_data.columns:
                    param_values = exp_data[param_name].dropna()
                    if len(param_values) > 0:
                        # Use median for more robust estimate
                        base_point[param_name] = float(param_values.median())
                        continue

                # Fall back to parameter configuration defaults
                if param_config["type"] == "continuous":
                    base_point[param_name] = np.mean(param_config["bounds"])
                elif param_config["type"] == "discrete":
                    base_point[param_name] = int(np.mean(param_config["bounds"]))
                elif param_config["type"] == "categorical":
                    base_point[param_name] = param_config["values"][0]

        return base_point

    def _get_enhanced_gp_predictions(self, model, test_X: torch.Tensor):
        """Get GP predictions with proper error handling and scaling"""
        try:
            model.eval()  # Set to evaluation mode

            with torch.no_grad():
                posterior = model.posterior(test_X)

                # Extract means and variances
                means = posterior.mean.squeeze().cpu().numpy()
                variances = posterior.variance.squeeze().cpu().numpy()

                # Ensure variances are positive
                variances = np.maximum(variances, 1e-8)
                stds = np.sqrt(variances)

                # Handle single prediction case
                if means.ndim == 0:
                    means = np.array([means])
                    stds = np.array([stds])

                return means, stds

        except Exception as e:
            logger.error(f"GP prediction failed: {e}")
            return None, None

    def _get_z_score(self, confidence_level: float) -> float:
        """Get z-score for given confidence level"""
        try:
            from scipy.stats import norm

            alpha = 1 - confidence_level
            return norm.ppf(1 - alpha / 2)
        except ImportError:
            # Fallback to common z-scores if scipy not available
            if confidence_level >= 0.95:
                return 1.96
            elif confidence_level >= 0.68:
                return 1.0
            else:
                return 1.5

    def _add_filtered_experimental_data(
        self,
        ax,
        param1_name: str,
        param2_name: str,
        response_name: str,
        fixed_value: float,
        tolerance: float = 0.1,
        marker_size: int = 50,
    ):
        """Add experimental data points that are close to the fixed parameter value"""
        exp_data = self.optimizer.experimental_data

        if (
            exp_data.empty
            or param1_name not in exp_data.columns
            or response_name not in exp_data.columns
        ):
            return

        # If param2 is in data, filter by proximity to fixed value
        if param2_name in exp_data.columns:
            param2_config = self.optimizer.params_config[param2_name]
            min_val, max_val = param2_config["bounds"]
            param_range = max_val - min_val

            # Filter points close to the fixed value
            param2_values = exp_data[param2_name].values
            close_mask = np.abs(param2_values - fixed_value) <= tolerance * param_range

            filtered_data = exp_data[close_mask]
        else:
            # If param2 not in data, use all points
            filtered_data = exp_data

        if filtered_data.empty:
            return

        # Extract and plot the data
        param1_values = filtered_data[param1_name].values
        response_values = (
            filtered_data[response_name]
            .apply(lambda x: np.mean(x) if isinstance(x, list) and x else x)
            .values
        )

        valid_mask = (
            pd.Series(param1_values).notna() & pd.Series(response_values).notna()
        )

        if valid_mask.any():
            ax.scatter(
                param1_values[valid_mask],
                response_values[valid_mask],
                color="red",
                s=marker_size,
                alpha=0.8,
                edgecolors="darkred",
                linewidth=1,
                label="Experimental Data",
                zorder=5,
            )

    def _add_model_diagnostics_text(self, ax, model, n_predictions: int):
        """Add model diagnostic information to the plot"""
        try:
            # Get training data size
            n_train = (
                model.train_inputs[0].shape[0] if hasattr(model, "train_inputs") else 0
            )

            # Add text box with diagnostics
            textstr = f"Training points: {n_train}\nPredictions: {n_predictions}"
            props = dict(boxstyle="round", facecolor="wheat", alpha=0.8)
            ax.text(
                0.02,
                0.98,
                textstr,
                transform=ax.transAxes,
                fontsize=8,
                verticalalignment="top",
                bbox=props,
            )

        except Exception as e:
            logger.warning(f"Could not add model diagnostics: {e}")

    def _add_acquisition_function_overlay(self, ax, fig, x_values, param1_name, param2_name, fixed_param_value, base_point, show_suggested_points=False):
        """Add acquisition function values as overlay on GP slice plot"""
        try:
            # Check if we have sufficient data for acquisition function
            if (not hasattr(self.optimizer, "train_X") or 
                self.optimizer.train_X.shape[0] < 3):
                logger.debug("Insufficient data for acquisition function overlay")
                return

            # Setup models and acquisition function
            success, models, acq_func, error_msg = self._setup_acquisition_models()
            if not success:
                logger.debug(f"Could not setup acquisition function: {error_msg}")
                return

            # Calculate acquisition values along the slice
            acq_values = []
            for x_val in x_values:
                try:
                    # Create parameter point
                    current_point = base_point.copy()
                    current_point[param1_name] = x_val
                    
                    # Convert to tensor
                    param_tensor = self.optimizer.parameter_transformer.params_to_tensor(current_point)
                    param_tensor = param_tensor.unsqueeze(0).to(self.optimizer.device, self.optimizer.dtype)
                    
                    # Evaluate acquisition function
                    with torch.no_grad():
                        acq_value = acq_func(param_tensor).item()
                        acq_values.append(acq_value)
                except Exception as e:
                    logger.debug(f"Error evaluating acquisition at x={x_val}: {e}")
                    acq_values.append(0.0)
            
            if not acq_values or all(v == 0.0 for v in acq_values):
                logger.debug("No valid acquisition values computed")
                return
            
            # Create secondary y-axis for acquisition function
            ax2 = ax.twinx()
            
            # Plot acquisition function
            acq_line = ax2.plot(
                x_values, acq_values, 
                color='orange', linewidth=2, linestyle='--',
                label='Acquisition Function', alpha=0.8
            )[0]
            
            # Format secondary axis
            ax2.set_ylabel('Acquisition Function Value', color='orange', fontweight='bold')
            ax2.tick_params(axis='y', labelcolor='orange')
            ax2.grid(False)  # Don't overlay grid on acquisition function
            
            # Add suggested points with dotted lines if requested
            if show_suggested_points and acq_values:
                try:
                    # Find the point with maximum acquisition value (suggested next point)
                    max_acq_idx = np.argmax(acq_values)
                    max_x = x_values[max_acq_idx]
                    max_acq = acq_values[max_acq_idx]
                    
                    # Plot the suggested point on the acquisition function line
                    ax2.plot(max_x, max_acq, 'ro', markersize=8, markerfacecolor='red',
                            markeredgecolor='darkred', markeredgewidth=2, 
                            label='Suggested Point', zorder=10)
                    
                    # Add dotted lines to both axes
                    # Vertical line to parameter axis
                    ax.axvline(x=max_x, color='red', linestyle=':', linewidth=2, alpha=0.7)
                    
                    # Horizontal line to acquisition function axis
                    ax2.axhline(y=max_acq, color='red', linestyle=':', linewidth=2, alpha=0.7)
                    
                    logger.debug(f"Added suggested point at x={max_x:.4f}, acq={max_acq:.4f}")
                    
                except Exception as e:
                    logger.debug(f"Error adding suggested points: {e}")
            
            # Add acquisition function to legend
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            if lines1 or lines2:
                ax.legend(lines1 + lines2, labels1 + labels2, loc='best', framealpha=0.9)
            
            logger.debug(f"Added acquisition function overlay with {len(acq_values)} points")
            
        except Exception as e:
            logger.debug(f"Error adding acquisition function overlay: {e}")

    def create_3d_surface_plot(
        self,
        fig,
        canvas,
        param1_name,
        param2_name,
        surface_mode="individual",
        response_name=None,
        weights=None,
        acquisition_type="EHVI",
        x_range=None,
        y_range=None,
        z_range=None,
        resolution=60,
        plot_style="surface",
        show_uncertainty=False,
        show_contours=True,
        show_data_points=True,
    ):
        """
        Create enhanced 3D surface plot supporting multiple surface modes:
        1. Individual Objective Surfaces
        2. Weighted-Sum (Scalarized) Surface  
        3. Acquisition Function Surface
        """
        fig.clear()

        try:
            # Validate parameters first
            param1_config = self.optimizer.params_config.get(param1_name)
            param2_config = self.optimizer.params_config.get(param2_name)

            if not param1_config or not param2_config:
                self._plot_message(
                    fig, f"Parameters {param1_name} or {param2_name} not found"
                )
                if canvas:
                    canvas.draw()
                return

            if "bounds" not in param1_config or "bounds" not in param2_config:
                self._plot_message(fig, f"No bounds specified for parameters")
                if canvas:
                    canvas.draw()
                return

            # Create high-resolution grid for parameter space
            x1_bounds = param1_config["bounds"]
            x2_bounds = param2_config["bounds"]
            x1 = np.linspace(x1_bounds[0], x1_bounds[1], resolution)
            x2 = np.linspace(x2_bounds[0], x2_bounds[1], resolution)
            X1, X2 = np.meshgrid(x1, x2)

            # Create intelligent base point for fixed parameters
            base_point = self._create_intelligent_base_point_3d(param1_name, param2_name)

            # Generate prediction points for the grid
            prediction_points = self._generate_surface_predictions_efficient(
                X1, X2, param1_name, param2_name, base_point, resolution
            )

            if prediction_points is None:
                self._plot_message(fig, "Failed to generate surface predictions")
                if canvas:
                    canvas.draw()
                return

            # Calculate surface values based on mode
            Z_mean, Z_std, surface_title, z_label = self._calculate_3d_surface_values(
                surface_mode, prediction_points, response_name, weights, 
                acquisition_type, resolution
            )

            if Z_mean is None:
                self._plot_message(fig, f"Failed to calculate {surface_mode} surface")
                if canvas:
                    canvas.draw()
                return

            # Create 3D visualization
            ax = self._create_3d_surface_visualization(
                fig, X1, X2, Z_mean, Z_std, param1_name, param2_name,
                surface_title, z_label, param1_config, param2_config,
                plot_style, show_uncertainty, show_contours, 
                x_range, y_range, z_range
            )

            # Add experimental data points (only for individual and weighted-sum modes)
            if show_data_points and surface_mode != "acquisition":
                self._add_3d_experimental_data_points(
                    ax, param1_name, param2_name, surface_mode, response_name, weights
                )

            # Add surface-specific diagnostics
            self._add_3d_surface_diagnostics(ax, surface_mode, resolution)

            fig.tight_layout()

        except Exception as e:
            logger.error(f"Error creating 3D surface plot: {e}")
            self._plot_message(fig, f"3D surface plot error: {str(e)}")

        if canvas:
            canvas.draw()

    def _create_intelligent_base_point_3d(
        self, param1_name: str, param2_name: str
    ) -> Dict[str, float]:
        """Create intelligent base point for other parameters using experimental data"""
        base_point = {}
        exp_data = self.optimizer.experimental_data

        for param_name, param_config in self.optimizer.params_config.items():
            if param_name in [param1_name, param2_name]:
                continue

            # Use experimental data statistics if available
            if not exp_data.empty and param_name in exp_data.columns:
                param_values = exp_data[param_name].dropna()
                if len(param_values) > 0:
                    # Use median for more robust estimate
                    base_point[param_name] = float(param_values.median())
                    continue

            # Fall back to parameter configuration defaults
            if param_config["type"] == "continuous":
                base_point[param_name] = np.mean(param_config["bounds"])
            elif param_config["type"] == "discrete":
                base_point[param_name] = int(np.mean(param_config["bounds"]))
            elif param_config["type"] == "categorical":
                base_point[param_name] = param_config["values"][0]

        return base_point

    def _generate_surface_predictions_efficient(
        self,
        X1,
        X2,
        param1_name: str,
        param2_name: str,
        base_point: Dict[str, float],
        resolution: int,
    ):
        """Generate surface prediction points efficiently"""
        try:
            # Create flattened coordinate arrays for vectorized processing
            x1_flat = X1.flatten()
            x2_flat = X2.flatten()
            n_points = len(x1_flat)

            # Generate prediction points
            prediction_points = []
            for i in range(n_points):
                param_dict = base_point.copy()
                param_dict[param1_name] = x1_flat[i]
                param_dict[param2_name] = x2_flat[i]

                try:
                    param_tensor = (
                        self.optimizer.parameter_transformer.params_to_tensor(
                            param_dict
                        )
                    )
                    prediction_points.append(param_tensor)
                except Exception as e:
                    logger.warning(f"Failed to convert point {i} to tensor: {e}")
                    continue

            if not prediction_points:
                return None

            return torch.stack(prediction_points).to(
                self.optimizer.device, self.optimizer.dtype
            )

        except Exception as e:
            logger.error(f"Failed to generate surface predictions: {e}")
            return None

    def _calculate_3d_surface_values(self, surface_mode, prediction_points, response_name, 
                                   weights, acquisition_type, resolution):
        """Calculate Z values for different surface modes"""
        try:
            if surface_mode == "individual":
                return self._calculate_individual_surface(
                    prediction_points, response_name, resolution
                )
            elif surface_mode == "weighted_sum":
                return self._calculate_weighted_sum_surface(
                    prediction_points, weights, resolution
                )
            elif surface_mode == "acquisition":
                return self._calculate_acquisition_surface(
                    prediction_points, acquisition_type, resolution
                )
            else:
                logger.error(f"Unknown surface mode: {surface_mode}")
                return None, None, None, None
                
        except Exception as e:
            logger.error(f"Error calculating surface values for mode {surface_mode}: {e}")
            return None, None, None, None

    def _calculate_individual_surface(self, prediction_points, response_name, resolution):
        """Calculate surface for individual objective"""
        try:
            # Get response models
            models = self.optimizer.get_response_models()
            
            if response_name not in models:
                logger.error(f"Model for {response_name} not available")
                return None, None, None, None
                
            model = models[response_name]
            
            # Get GP predictions
            Z_mean, Z_std = self._get_enhanced_surface_gp_predictions(
                model, prediction_points, resolution
            )
            
            if Z_mean is None:
                return None, None, None, None
                
            # Get response units for labeling
            response_config = self.optimizer.responses_config.get(response_name, {})
            units = response_config.get("units", "")
            z_label = f"{response_name} ({units})" if units else response_name
            surface_title = f"Individual Surface: {response_name}"
            
            return Z_mean, Z_std, surface_title, z_label
            
        except Exception as e:
            logger.error(f"Error calculating individual surface: {e}")
            return None, None, None, None

    def _calculate_weighted_sum_surface(self, prediction_points, weights, resolution):
        """Calculate weighted-sum scalarized surface S(x) = w1*μ1(x) + w2*μ2(x) + ..."""
        try:
            if not weights:
                logger.error("No weights provided for weighted-sum surface")
                return None, None, None, None
                
            # Get response models
            models = self.optimizer.get_response_models()
            
            # Validate all responses have models
            missing_models = [resp for resp in weights.keys() if resp not in models]
            if missing_models:
                logger.error(f"Models not available for: {missing_models}")
                return None, None, None, None
            
            # Calculate weighted sum
            Z_mean_total = None
            Z_var_total = None  # For uncertainty propagation
            weight_descriptions = []
            
            for response_name, weight in weights.items():
                if weight == 0:
                    continue
                    
                model = models[response_name]
                
                # Get predictions for this response
                Z_mean_resp, Z_std_resp = self._get_enhanced_surface_gp_predictions(
                    model, prediction_points, resolution
                )
                
                if Z_mean_resp is None:
                    logger.error(f"Failed to get predictions for {response_name}")
                    continue
                    
                # Apply weight with proper direction handling
                # Get optimization direction for this response
                response_config = self.optimizer.responses_config.get(response_name, {})
                goal = response_config.get("goal", "Maximize")
                
                # Apply direction sign: minimize objectives are negated for maximization context
                direction_sign = -1 if goal == "Minimize" else 1
                weighted_mean = weight * direction_sign * Z_mean_resp
                weighted_var = (weight ** 2) * (Z_std_resp ** 2)  # Variance scaling (always positive)
                
                # Sum weighted contributions
                if Z_mean_total is None:
                    Z_mean_total = weighted_mean
                    Z_var_total = weighted_var
                else:
                    Z_mean_total += weighted_mean
                    Z_var_total += weighted_var  # Independent variances add
                    
                # Create descriptive weight label with direction
                sign_str = "-" if direction_sign == -1 else "+"
                weight_descriptions.append(f"{sign_str}{weight:.2f}×{response_name}")
            
            if Z_mean_total is None:
                logger.error("No valid weighted predictions calculated")
                return None, None, None, None
                
            # Convert back to standard deviation
            Z_std_total = np.sqrt(Z_var_total)
            
            # Create descriptive labels
            weight_str = " ".join(weight_descriptions)  # Already has signs
            # Clean up double signs (e.g., "+ +" becomes "+")
            weight_str = weight_str.replace("+ +", "+").replace("+ -", "- ").strip()
            # Remove leading + if present
            if weight_str.startswith("+"):
                weight_str = weight_str[1:].strip()
            surface_title = f"Weighted-Sum Surface"
            z_label = f"S(x) = {weight_str}"
            
            return Z_mean_total, Z_std_total, surface_title, z_label
            
        except Exception as e:
            logger.error(f"Error calculating weighted-sum surface: {e}")
            return None, None, None, None

    def _calculate_acquisition_surface(self, prediction_points, acquisition_type, resolution):
        """Calculate acquisition function surface"""
        try:
            # Check if we have sufficient data
            if (not hasattr(self.optimizer, "train_X") or 
                self.optimizer.train_X.shape[0] < 3):
                logger.error("Insufficient data for acquisition function surface")
                return None, None, None, None
                
            # Setup models and acquisition function
            success, models, acq_func, error_msg = self._setup_acquisition_models()
            if not success:
                logger.error(f"Could not setup acquisition function: {error_msg}")
                return None, None, None, None
                
            # Evaluate acquisition function at all points
            acq_values = []
            for i in range(prediction_points.shape[0]):
                try:
                    point = prediction_points[i:i+1]  # Keep batch dimension
                    with torch.no_grad():
                        acq_value = acq_func(point).item()
                        acq_values.append(acq_value)
                except Exception as e:
                    logger.debug(f"Error evaluating acquisition at point {i}: {e}")
                    acq_values.append(0.0)
            
            # Convert to numpy and reshape to grid
            acq_array = np.array(acq_values)
            Z_mean = acq_array.reshape(resolution, resolution)
            
            # No uncertainty for acquisition function
            Z_std = np.zeros_like(Z_mean)
            
            # Create descriptive labels
            acq_name_map = {
                "EHVI": "Expected Hypervolume Improvement",
                "EI": "Expected Improvement", 
                "UCB": "Upper Confidence Bound"
            }
            acq_name = acq_name_map.get(acquisition_type, acquisition_type)
            surface_title = f"Acquisition Function: {acq_name}"
            z_label = f"{acq_name} Value"
            
            logger.debug(f"Calculated acquisition surface with range [{Z_mean.min():.3e}, {Z_mean.max():.3e}]")
            
            return Z_mean, Z_std, surface_title, z_label
            
        except Exception as e:
            logger.error(f"Error calculating acquisition surface: {e}")
            return None, None, None, None

    def _create_3d_surface_visualization(self, fig, X1, X2, Z_mean, Z_std, param1_name, param2_name,
                                       surface_title, z_label, param1_config, param2_config,
                                       plot_style, show_uncertainty, show_contours, 
                                       x_range, y_range, z_range):
        """Create the 3D surface visualization"""
        try:
            # Create 3D subplot
            ax = fig.add_subplot(111, projection='3d')
            
            # Plot surface based on style
            if plot_style == "surface":
                surface = ax.plot_surface(
                    X1, X2, Z_mean, 
                    cmap='viridis', alpha=0.8, 
                    linewidth=0, antialiased=True
                )
                fig.colorbar(surface, ax=ax, shrink=0.6, aspect=20, label=z_label)
                
            elif plot_style == "wireframe":
                ax.plot_wireframe(X1, X2, Z_mean, alpha=0.6, linewidth=0.5)
                
            elif plot_style == "contour":
                contour = ax.contour3D(X1, X2, Z_mean, levels=20, cmap='viridis', alpha=0.8)
                fig.colorbar(contour, ax=ax, shrink=0.6, aspect=20, label=z_label)
            
            # Add uncertainty visualization if requested and available
            if show_uncertainty and np.any(Z_std > 0):
                # Add uncertainty as semi-transparent surface offset
                uncertainty_alpha = 0.2
                ax.plot_surface(
                    X1, X2, Z_mean + Z_std, 
                    alpha=uncertainty_alpha, color='red',
                    linewidth=0, antialiased=True
                )
                ax.plot_surface(
                    X1, X2, Z_mean - Z_std,
                    alpha=uncertainty_alpha, color='red', 
                    linewidth=0, antialiased=True
                )
            
            # Add contour projections if requested
            if show_contours:
                # Project contours onto bottom plane
                z_bottom = Z_mean.min() - 0.1 * (Z_mean.max() - Z_mean.min())
                ax.contour(X1, X2, Z_mean, levels=10, zdir='z', offset=z_bottom, 
                          cmap='viridis', alpha=0.5, linewidths=0.5)
            
            # Set labels with units
            param1_units = param1_config.get("units", "")
            param2_units = param2_config.get("units", "")
            
            x_label = f"{param1_name} ({param1_units})" if param1_units else param1_name
            y_label = f"{param2_name} ({param2_units})" if param2_units else param2_name
            
            ax.set_xlabel(x_label, fontweight='bold')
            ax.set_ylabel(y_label, fontweight='bold')
            ax.set_zlabel(z_label, fontweight='bold')
            ax.set_title(surface_title, fontsize=12, fontweight='bold', pad=20)
            
            # Apply axis ranges if specified
            if x_range and len(x_range) == 2 and all(x is not None for x in x_range):
                ax.set_xlim(x_range[0], x_range[1])
            if y_range and len(y_range) == 2 and all(y is not None for y in y_range):
                ax.set_ylim(y_range[0], y_range[1]) 
            if z_range and len(z_range) == 2 and all(z is not None for z in z_range):
                ax.set_zlim(z_range[0], z_range[1])
            
            return ax
            
        except Exception as e:
            logger.error(f"Error creating 3D surface visualization: {e}")
            return None

    def _add_3d_experimental_data_points(self, ax, param1_name, param2_name, 
                                       surface_mode, response_name, weights):
        """Add experimental data points to 3D surface plot"""
        try:
            exp_data = self.optimizer.experimental_data
            
            if exp_data.empty:
                return
                
            # Get parameter data
            if param1_name not in exp_data.columns or param2_name not in exp_data.columns:
                return
                
            x_data = exp_data[param1_name].dropna()
            y_data = exp_data[param2_name].dropna()
            
            # Calculate Z values based on surface mode
            if surface_mode == "individual" and response_name:
                if response_name not in exp_data.columns:
                    return
                z_data = exp_data[response_name].dropna()
                
            elif surface_mode == "weighted_sum" and weights:
                # Calculate weighted sum for experimental points
                z_values = []
                for idx in exp_data.index:
                    weighted_sum = 0
                    valid_point = True
                    
                    for resp_name, weight in weights.items():
                        if weight == 0 or resp_name not in exp_data.columns:
                            continue
                        if pd.isna(exp_data.loc[idx, resp_name]):
                            valid_point = False
                            break
                        weighted_sum += weight * exp_data.loc[idx, resp_name]
                    
                    if valid_point:
                        z_values.append(weighted_sum)
                    else:
                        z_values.append(np.nan)
                        
                z_data = pd.Series(z_values, index=exp_data.index).dropna()
            else:
                return
            
            # Find common indices
            common_indices = x_data.index.intersection(y_data.index).intersection(z_data.index)
            if len(common_indices) == 0:
                return
                
            # Plot experimental points
            ax.scatter(
                x_data.loc[common_indices],
                y_data.loc[common_indices], 
                z_data.loc[common_indices],
                c='red', s=50, alpha=0.8, 
                edgecolors='darkred', linewidth=1,
                label='Experimental Data', zorder=10
            )
            
            # Add legend
            ax.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98))
            
        except Exception as e:
            logger.debug(f"Could not add experimental data points: {e}")

    def _add_3d_surface_diagnostics(self, ax, surface_mode, resolution):
        """Add surface-specific diagnostic information"""
        try:
            # Create diagnostic text based on mode
            if surface_mode == "individual":
                diag_text = f"Resolution: {resolution}×{resolution}\nSurface: Individual Objective"
            elif surface_mode == "weighted_sum":
                diag_text = f"Resolution: {resolution}×{resolution}\nSurface: Weighted-Sum Scalarization"
            elif surface_mode == "acquisition":
                diag_text = f"Resolution: {resolution}×{resolution}\nSurface: Acquisition Function"
            else:
                diag_text = f"Resolution: {resolution}×{resolution}"
            
            # Add text to plot
            ax.text2D(0.02, 0.02, diag_text, transform=ax.transAxes,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.8),
                     fontsize=8, verticalalignment='bottom')
                     
        except Exception as e:
            logger.debug(f"Could not add surface diagnostics: {e}")

    def _get_enhanced_surface_gp_predictions(
        self, model, test_X: torch.Tensor, resolution: int
    ):
        """Get GP predictions for surface with proper error handling"""
        try:
            model.eval()

            with torch.no_grad():
                posterior = model.posterior(test_X)

                # Extract means and variances
                means = posterior.mean.squeeze().cpu().numpy()
                variances = posterior.variance.squeeze().cpu().numpy()

                # Ensure variances are positive
                variances = np.maximum(variances, 1e-8)
                stds = np.sqrt(variances)

                # Reshape to grid
                Z_mean = means.reshape(resolution, resolution)
                Z_std = stds.reshape(resolution, resolution)

                return Z_mean, Z_std

        except Exception as e:
            logger.error(f"Surface GP prediction failed: {e}")
            return None, None

    def _create_enhanced_3d_plot(
        self,
        fig,
        X1,
        X2,
        Z_mean,
        Z_std,
        param1_name: str,
        param2_name: str,
        response_name: str,
        param1_config: Dict,
        param2_config: Dict,
        plot_style: str,
        show_uncertainty: bool,
        show_contours: bool,
        x_range=None,
        y_range=None,
        z_range=None,
    ):
        """Create the enhanced 3D visualization"""

        # Create 3D subplot
        ax = fig.add_subplot(111, projection="3d")

        # Get units for labels
        param1_units = param1_config.get("units", "")
        param2_units = param2_config.get("units", "")
        response_units = self.optimizer.responses_config[response_name].get("units", "")

        # Choose colormap and limits
        vmin, vmax = Z_mean.min(), Z_mean.max()
        cmap = plt.cm.viridis

        # Create main surface plot based on style
        surf = None
        if plot_style == "surface":
            surf = ax.plot_surface(
                X1,
                X2,
                Z_mean,
                cmap=cmap,
                alpha=0.8,
                linewidth=0,
                antialiased=True,
                vmin=vmin,
                vmax=vmax,
            )
        elif plot_style == "wireframe":
            surf = ax.plot_wireframe(
                X1, X2, Z_mean, color="blue", alpha=0.7, linewidth=0.5
            )
        elif plot_style == "surface_wireframe":
            surf = ax.plot_surface(
                X1,
                X2,
                Z_mean,
                cmap=cmap,
                alpha=0.6,
                linewidth=0.2,
                antialiased=True,
                vmin=vmin,
                vmax=vmax,
            )
            ax.plot_wireframe(X1, X2, Z_mean, color="black", alpha=0.3, linewidth=0.3)
        else:
            # Default to surface
            surf = ax.plot_surface(
                X1,
                X2,
                Z_mean,
                cmap=cmap,
                alpha=0.8,
                linewidth=0,
                antialiased=True,
                vmin=vmin,
                vmax=vmax,
            )

        # Add uncertainty visualization if requested
        if show_uncertainty and Z_std is not None:
            # Add uncertainty as contour lines at base
            try:
                z_base = ax.get_zlim()[0]
                uncertainty_contours = ax.contour(
                    X1,
                    X2,
                    Z_std,
                    levels=5,
                    colors="orange",
                    alpha=0.6,
                    linewidths=1,
                    offset=z_base,
                )
            except Exception as e:
                logger.debug(f"Could not add uncertainty contours: {e}")

        # Add contour projections if requested
        if show_contours:
            try:
                z_base = ax.get_zlim()[0]
                # Mean contours on base
                ax.contour(
                    X1,
                    X2,
                    Z_mean,
                    levels=8,
                    colors="black",
                    alpha=0.5,
                    linewidths=0.8,
                    offset=z_base,
                )
            except Exception as e:
                logger.debug(f"Could not add contours: {e}")

        # Enhanced labels with units
        xlabel = f"{param1_name} ({param1_units})" if param1_units else param1_name
        ylabel = f"{param2_name} ({param2_units})" if param2_units else param2_name
        zlabel = (
            f"{response_name} ({response_units})" if response_units else response_name
        )

        ax.set_xlabel(xlabel, fontsize=11, fontweight="bold", labelpad=10)
        ax.set_ylabel(ylabel, fontsize=11, fontweight="bold", labelpad=10)
        ax.set_zlabel(zlabel, fontsize=11, fontweight="bold", labelpad=10)

        # Enhanced title
        title = f"3D Response Surface: {response_name} vs {param1_name} & {param2_name}"
        if len(self.optimizer.params_config) > 2:
            other_params = [
                p
                for p in self.optimizer.params_config.keys()
                if p not in [param1_name, param2_name]
            ]
            if other_params:
                title += f"\\n(Other parameters fixed)"

        ax.set_title(title, fontsize=12, fontweight="bold", pad=20)

        # Add colorbar if surface plot
        if surf is not None and hasattr(surf, "get_array"):
            try:
                cbar = fig.colorbar(surf, ax=ax, shrink=0.6, aspect=15, pad=0.1)
                cbar.set_label(zlabel, fontsize=10, fontweight="bold")
                cbar.ax.tick_params(labelsize=9)
            except Exception as e:
                logger.debug(f"Could not add colorbar: {e}")

        # Apply axis ranges if specified
        if (
            x_range
            and len(x_range) == 2
            and x_range[0] is not None
            and x_range[1] is not None
        ):
            ax.set_xlim(x_range[0], x_range[1])
        if (
            y_range
            and len(y_range) == 2
            and y_range[0] is not None
            and y_range[1] is not None
        ):
            ax.set_ylim(y_range[0], y_range[1])
        if (
            z_range
            and len(z_range) == 2
            and z_range[0] is not None
            and z_range[1] is not None
        ):
            ax.set_zlim(z_range[0], z_range[1])

        # Enhance view angle and styling
        ax.view_init(elev=25, azim=45)
        ax.grid(True, alpha=0.3)

        return ax

    def _add_enhanced_3d_experimental_data(
        self, ax, param1_name: str, param2_name: str, response_name: str
    ):
        """Add experimental data points to 3D plot with enhanced styling"""
        exp_data = self.optimizer.experimental_data

        if exp_data.empty:
            return

        # Check if required columns exist
        required_cols = [param1_name, param2_name, response_name]
        if not all(col in exp_data.columns for col in required_cols):
            return

        # Extract data with proper handling
        p1_vals = exp_data[param1_name].values
        p2_vals = exp_data[param2_name].values
        r_vals = (
            exp_data[response_name]
            .apply(lambda x: np.mean(x) if isinstance(x, list) and x else x)
            .values
        )

        # Filter valid data points
        valid_mask = (
            pd.Series(p1_vals).notna()
            & pd.Series(p2_vals).notna()
            & pd.Series(r_vals).notna()
        )

        if not valid_mask.any():
            return

        # Plot experimental points with enhanced styling
        ax.scatter(
            p1_vals[valid_mask],
            p2_vals[valid_mask],
            r_vals[valid_mask],
            c="red",
            s=80,
            alpha=0.9,
            edgecolors="darkred",
            linewidth=1.5,
            label="Experimental Data",
            marker="o",
            depthshade=True,
        )

        # Add legend
        ax.legend(loc="upper left", bbox_to_anchor=(0.02, 0.98), fontsize=9)

    def _add_enhanced_3d_model_diagnostics(self, ax, model, resolution: int):
        """Add model diagnostic information to 3D plot"""
        try:
            # Get training data size
            n_train = (
                model.train_inputs[0].shape[0] if hasattr(model, "train_inputs") else 0
            )
            n_predictions = resolution * resolution

            # Add text box with diagnostics
            textstr = f"Training: {n_train} pts\\nSurface: {resolution}x{resolution}\\nPredictions: {n_predictions}"
            props = dict(
                boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.8, fontsize=8
            )

            # Position text box in 3D space
            ax.text2D(
                0.02,
                0.98,
                textstr,
                transform=ax.transAxes,
                fontsize=8,
                verticalalignment="top",
                bbox=props,
            )

        except Exception as e:
            logger.debug(f"Could not add 3D model diagnostics: {e}")

    def create_uncertainty_heatmap(
        self,
        fig,
        canvas,
        response_name: str,
        param1_name: str,
        param2_name: str,
        resolution: int = 80,
        plot_style: str = "heatmap",
        show_experimental_data: bool = True,
        uncertainty_metric: str = "std",
        colormap: str = "Reds",
    ):
        """
        Create heatmap showing GP prediction uncertainty across 2D parameter space

        This is different from regular GP uncertainty plots:
        - Shows SPATIAL DISTRIBUTION of uncertainty across parameter space
        - Helps identify regions needing more experimental data
        - Visualizes exploration vs exploitation opportunities
        - Uses color-coded maps instead of confidence bands

        Args:
            fig: Matplotlib figure
            canvas: Canvas for drawing (can be None)
            response_name: Name of response variable
            param1_name: Name of first parameter (x-axis)
            param2_name: Name of second parameter (y-axis)
            resolution: Grid resolution (default 80x80)
            plot_style: 'heatmap', 'contour', 'filled_contour', or 'combined'
            show_experimental_data: Whether to overlay experimental data points
            uncertainty_metric: 'std', 'variance', or 'coefficient_of_variation'
            colormap: Matplotlib colormap name ('Reds', 'Blues', 'viridis', etc.)
        """
        fig.clear()

        try:
            # Get response models with validation
            models = self.optimizer.get_response_models()

            if response_name not in models:
                self._plot_message(
                    fig,
                    f"Model for {response_name} not available.\\nNeed more data for GP uncertainty analysis.",
                )
                if canvas:
                    canvas.draw()
                return

            model = models[response_name]

            # Validate parameters
            param1_config = self.optimizer.params_config.get(param1_name)
            param2_config = self.optimizer.params_config.get(param2_name)

            if not param1_config or not param2_config:
                self._plot_message(
                    fig, f"Parameters {param1_name} or {param2_name} not found"
                )
                if canvas:
                    canvas.draw()
                return

            if "bounds" not in param1_config or "bounds" not in param2_config:
                self._plot_message(fig, f"No bounds specified for parameters")
                if canvas:
                    canvas.draw()
                return

            # Generate parameter grid
            x1_bounds = param1_config["bounds"]
            x2_bounds = param2_config["bounds"]

            x1 = np.linspace(x1_bounds[0], x1_bounds[1], resolution)
            x2 = np.linspace(x2_bounds[0], x2_bounds[1], resolution)
            X1, X2 = np.meshgrid(x1, x2)

            # Create intelligent base point for other parameters
            base_point = self._create_intelligent_base_point_3d(
                param1_name, param2_name
            )

            # Generate prediction grid
            prediction_points = self._generate_surface_predictions_efficient(
                X1, X2, param1_name, param2_name, base_point, resolution
            )

            if prediction_points is None:
                self._plot_message(fig, "Failed to generate uncertainty predictions")
                if canvas:
                    canvas.draw()
                return

            # Get GP uncertainty predictions
            uncertainty_grid = self._get_uncertainty_heatmap_predictions(
                model, prediction_points, resolution, uncertainty_metric
            )

            if uncertainty_grid is None:
                self._plot_message(fig, "Failed to get GP uncertainty predictions")
                if canvas:
                    canvas.draw()
                return

            # Create the uncertainty heatmap visualization
            self._create_uncertainty_heatmap_visualization(
                fig,
                X1,
                X2,
                uncertainty_grid,
                param1_name,
                param2_name,
                response_name,
                param1_config,
                param2_config,
                plot_style,
                colormap,
                uncertainty_metric,
            )

            # Add experimental data points if requested
            if show_experimental_data:
                self._add_uncertainty_experimental_data_overlay(
                    fig.gca(), param1_name, param2_name, response_name
                )

            # Add uncertainty analysis information
            self._add_uncertainty_heatmap_analysis_info(
                fig.gca(), model, uncertainty_grid, resolution, uncertainty_metric
            )

            fig.tight_layout()

        except Exception as e:
            logger.error(f"Error creating GP uncertainty heatmap: {e}", exc_info=True)
            self._plot_message(fig, f"GP uncertainty heatmap error: {str(e)}")

        if canvas:
            canvas.draw()

    def _get_uncertainty_heatmap_predictions(
        self, model, test_X: torch.Tensor, resolution: int, uncertainty_metric: str
    ) -> Optional[np.ndarray]:
        """Get GP uncertainty predictions for heatmap"""
        try:
            model.eval()

            with torch.no_grad():
                posterior = model.posterior(test_X)

                # Extract variances
                variances = posterior.variance.squeeze().cpu().numpy()

                # Ensure variances are positive
                variances = np.maximum(variances, 1e-8)

                # Calculate requested uncertainty metric
                if uncertainty_metric == "std":
                    uncertainty_values = np.sqrt(variances)
                elif uncertainty_metric == "variance":
                    uncertainty_values = variances
                elif uncertainty_metric == "coefficient_of_variation":
                    means = posterior.mean.squeeze().cpu().numpy()
                    stds = np.sqrt(variances)
                    # Avoid division by zero
                    means_safe = np.where(np.abs(means) < 1e-8, 1e-8, means)
                    uncertainty_values = stds / np.abs(means_safe)
                else:
                    uncertainty_values = np.sqrt(variances)  # Default to std

                # Reshape to grid
                uncertainty_grid = uncertainty_values.reshape(resolution, resolution)

                return uncertainty_grid

        except Exception as e:
            logger.error(f"Uncertainty prediction failed: {e}")
            return None

    def _create_uncertainty_heatmap_visualization(
        self,
        fig,
        X1,
        X2,
        uncertainty_grid,
        param1_name: str,
        param2_name: str,
        response_name: str,
        param1_config: Dict,
        param2_config: Dict,
        plot_style: str,
        colormap: str,
        uncertainty_metric: str,
    ):
        """Create the uncertainty heatmap visualization"""

        ax = fig.add_subplot(111)

        # Get units for labels
        param1_units = param1_config.get("units", "")
        param2_units = param2_config.get("units", "")
        response_units = self.optimizer.responses_config[response_name].get("units", "")

        # Choose appropriate colormap (fix matplotlib deprecation warning)
        try:
            cmap = plt.colormaps.get_cmap(colormap)
        except AttributeError:
            # Fallback for older matplotlib versions
            cmap = plt.cm.get_cmap(colormap)

        # Create visualization based on style
        if plot_style == "heatmap":
            im = ax.imshow(
                uncertainty_grid,
                extent=[X1.min(), X1.max(), X2.min(), X2.max()],
                aspect="auto",
                origin="lower",
                cmap=cmap,
                alpha=0.8,
            )
        elif plot_style == "contour":
            levels = np.linspace(uncertainty_grid.min(), uncertainty_grid.max(), 15)
            cs = ax.contour(
                X1, X2, uncertainty_grid, levels=levels, cmap=cmap, linewidths=1.5
            )
            ax.clabel(cs, inline=True, fontsize=8, fmt="%.3f")
            im = cs
        elif plot_style == "filled_contour":
            levels = np.linspace(uncertainty_grid.min(), uncertainty_grid.max(), 20)
            im = ax.contourf(
                X1, X2, uncertainty_grid, levels=levels, cmap=cmap, alpha=0.8
            )
        elif plot_style == "combined":
            # Filled contours + contour lines
            levels_filled = np.linspace(
                uncertainty_grid.min(), uncertainty_grid.max(), 20
            )
            levels_lines = np.linspace(
                uncertainty_grid.min(), uncertainty_grid.max(), 10
            )

            im = ax.contourf(
                X1, X2, uncertainty_grid, levels=levels_filled, cmap=cmap, alpha=0.7
            )
            cs = ax.contour(
                X1,
                X2,
                uncertainty_grid,
                levels=levels_lines,
                colors="black",
                linewidths=0.8,
                alpha=0.6,
            )
            ax.clabel(cs, inline=True, fontsize=7, fmt="%.3f")
        else:
            # Default to heatmap
            im = ax.imshow(
                uncertainty_grid,
                extent=[X1.min(), X1.max(), X2.min(), X2.max()],
                aspect="auto",
                origin="lower",
                cmap=cmap,
                alpha=0.8,
            )

        # Enhanced labels with units
        xlabel = f"{param1_name} ({param1_units})" if param1_units else param1_name
        ylabel = f"{param2_name} ({param2_units})" if param2_units else param2_name

        ax.set_xlabel(xlabel, fontsize=12, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=12, fontweight="bold")

        # Create informative title
        metric_names = {
            "std": "Standard Deviation",
            "variance": "Variance",
            "coefficient_of_variation": "Coefficient of Variation",
        }
        metric_display = metric_names.get(uncertainty_metric, "Uncertainty")

        title = f"GP Uncertainty Heatmap: {metric_display}\\n{response_name} predictions across {param1_name} vs {param2_name}"
        if len(self.optimizer.params_config) > 2:
            other_params = [
                p
                for p in self.optimizer.params_config.keys()
                if p not in [param1_name, param2_name]
            ]
            if other_params:
                title += f"\\n(Other parameters fixed)"

        ax.set_title(title, fontsize=11, fontweight="bold", pad=15)

        # Add colorbar with proper label
        if hasattr(im, "get_array") or hasattr(im, "collections"):
            try:
                if uncertainty_metric == "coefficient_of_variation":
                    cbar_label = f"{metric_display} (dimensionless)"
                else:
                    unit_str = f" ({response_units})" if response_units else ""
                    cbar_label = f"{metric_display}{unit_str}"

                cbar = fig.colorbar(im, ax=ax, shrink=0.8, aspect=20, pad=0.02)
                cbar.set_label(cbar_label, fontsize=10, fontweight="bold")
                cbar.ax.tick_params(labelsize=9)
            except Exception as e:
                logger.debug(f"Could not add colorbar: {e}")

        # Enhanced grid
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)

        return ax

    def _add_uncertainty_experimental_data_overlay(
        self, ax, param1_name: str, param2_name: str, response_name: str
    ):
        """Add experimental data points as overlay on uncertainty heatmap"""
        exp_data = self.optimizer.experimental_data

        if exp_data.empty:
            return

        # Check if required columns exist
        required_cols = [param1_name, param2_name]
        if not all(col in exp_data.columns for col in required_cols):
            return

        # Extract parameter data
        p1_vals = exp_data[param1_name].values
        p2_vals = exp_data[param2_name].values

        # Filter valid data points
        valid_mask = pd.Series(p1_vals).notna() & pd.Series(p2_vals).notna()

        if not valid_mask.any():
            return

        # Plot experimental points with high contrast for visibility on heatmap
        scatter = ax.scatter(
            p1_vals[valid_mask],
            p2_vals[valid_mask],
            c="white",
            s=60,
            alpha=0.9,
            edgecolors="black",
            linewidth=2,
            label="Experimental Data",
            marker="o",
            zorder=10,
        )

        # Add inner colored dots for better visibility
        ax.scatter(
            p1_vals[valid_mask],
            p2_vals[valid_mask],
            c="navy",
            s=25,
            alpha=0.8,
            marker="o",
            zorder=11,
        )

        # Add legend
        ax.legend(
            loc="upper right",
            bbox_to_anchor=(0.98, 0.98),
            fontsize=9,
            framealpha=0.9,
            edgecolor="gray",
        )

    def _add_uncertainty_heatmap_analysis_info(
        self, ax, model, uncertainty_grid, resolution: int, uncertainty_metric: str
    ):
        """Add uncertainty analysis information to the heatmap"""
        try:
            # Calculate uncertainty statistics
            min_uncertainty = uncertainty_grid.min()
            max_uncertainty = uncertainty_grid.max()
            mean_uncertainty = uncertainty_grid.mean()
            std_uncertainty = uncertainty_grid.std()

            # Get training data size
            n_train = (
                model.train_inputs[0].shape[0] if hasattr(model, "train_inputs") else 0
            )

            # Identify high/low uncertainty regions
            high_uncertainty_threshold = mean_uncertainty + 0.5 * std_uncertainty
            high_uncertainty_fraction = (
                np.sum(uncertainty_grid > high_uncertainty_threshold)
                / uncertainty_grid.size
            )

            # Create info text
            info_lines = [
                f"Training points: {n_train}",
                f"Grid resolution: {resolution}x{resolution}",
                f"Uncertainty statistics:",
                f"  Range: {min_uncertainty:.3f} - {max_uncertainty:.3f}",
                f"  Mean ± Std: {mean_uncertainty:.3f} ± {std_uncertainty:.3f}",
                f"High uncertainty regions: {high_uncertainty_fraction:.1%}",
            ]

            textstr = "\\n".join(info_lines)
            props = dict(
                boxstyle="round,pad=0.4", facecolor="wheat", alpha=0.85, fontsize=8
            )

            # Position text box
            ax.text(
                0.02,
                0.02,
                textstr,
                transform=ax.transAxes,
                fontsize=8,
                verticalalignment="bottom",
                bbox=props,
            )

        except Exception as e:
            logger.debug(f"Could not add uncertainty analysis info: {e}")

    def create_parallel_coordinates_plot(
        self, fig, canvas, selected_variables: List[str]
    ):
        """Create Parallel Coordinates plot"""
        fig.clear()

        try:
            if self.optimizer.experimental_data.empty:
                self._plot_message(
                    fig, "No experimental data available for Parallel Coordinates Plot"
                )
                if canvas:
                    canvas.draw()
                return

            if not selected_variables:
                self._plot_message(
                    fig, "No variables selected for Parallel Coordinates Plot"
                )
                if canvas:
                    canvas.draw()
                return

            # Filter experimental data to include only selected variables
            # Ensure selected_variables are actually in experimental_data columns
            available_selected_variables = [
                var
                for var in selected_variables
                if var in self.optimizer.experimental_data.columns
            ]

            if not available_selected_variables:
                self._plot_message(
                    fig, "Selected variables not found in experimental data."
                )
                if canvas:
                    canvas.draw()
                return

            plot_df = self.optimizer.experimental_data[
                available_selected_variables
            ].copy()

            # Handle list-like response values by taking the mean
            for col in self.optimizer.responses_config.keys():
                if col in plot_df.columns:
                    plot_df[col] = plot_df[col].apply(
                        lambda x: np.mean(x) if isinstance(x, list) and x else x
                    )

            # Drop rows with any NaN values for plotting
            plot_df.dropna(inplace=True)

            if plot_df.empty:
                self._plot_message(
                    fig,
                    "No complete data points for Parallel Coordinates Plot after cleaning",
                )
                if canvas:
                    canvas.draw()
                return

            ax = fig.add_subplot(111)

            # Normalize data for better visualization in parallel coordinates
            numeric_cols = plot_df.select_dtypes(include=np.number).columns.tolist()
            for col in numeric_cols:
                min_val = plot_df[col].min()
                max_val = plot_df[col].max()
                if max_val - min_val > 0:
                    plot_df[col] = (plot_df[col] - min_val) / (max_val - min_val)

            # Set up colors - simple gradient based on index
            colors = plt.cm.viridis(np.linspace(0, 1, len(plot_df)))

            for i, (idx, row) in enumerate(plot_df.iterrows()):
                ax.plot(
                    range(len(plot_df.columns)), row.values, color=colors[i], alpha=0.5
                )

            ax.set_xticks(range(len(plot_df.columns)))
            ax.set_xticklabels(plot_df.columns, rotation=45, ha="right")
            ax.set_title("Parallel Coordinates Plot", fontsize=14, fontweight="bold")
            ax.set_ylabel("Normalized Value", fontsize=12, fontweight="bold")
            ax.grid(True, alpha=0.3)

            fig.tight_layout()

        except Exception as e:
            logger.error(f"Error creating Parallel Coordinates plot: {e}")
            self._plot_message(fig, f"Parallel Coordinates plot error: {str(e)}")

        if canvas:
            canvas.draw()

    def _prepare_model_analysis_data(self, response_name):
        """
        Prepare and validate data for model analysis plots.
        
        Args:
            response_name: Name of the response to analyze
            
        Returns:
            tuple: (model, actual_values, predicted_values, uncertainties) if successful, None if validation fails
        """
        # Get response models
        models = self.optimizer.get_response_models()

        if response_name not in models:
            return None, f"Model for {response_name} not available.\n\nThis usually means insufficient data."

        model = models[response_name]
        exp_data = self.optimizer.experimental_data

        if exp_data.empty or response_name not in exp_data.columns:
            return None, "No experimental data available for model analysis"

        # Get actual values and predictions
        actual_values = []
        predicted_values = []
        uncertainties = []

        for _, row in exp_data.iterrows():
            try:
                # Get parameter values - ensure all required parameters are present
                param_dict = {}
                missing_params = []

                for param_name in self.optimizer.parameter_transformer.param_names:
                    if param_name in row and pd.notna(row[param_name]):
                        param_dict[param_name] = row[param_name]
                    else:
                        missing_params.append(param_name)

                # Skip row if missing critical parameters
                if missing_params:
                    logger.debug(
                        f"Skipping row due to missing parameters: {missing_params}"
                    )
                    continue

                # Get actual response value
                if response_name not in row or pd.isna(row[response_name]):
                    continue

                actual_val = row[response_name]
                if isinstance(actual_val, list) and actual_val:
                    actual_val = np.mean([x for x in actual_val if not pd.isna(x)])
                elif not isinstance(actual_val, (int, float)) or pd.isna(
                    actual_val
                ):
                    continue

                # Ensure actual value is finite
                if not np.isfinite(actual_val):
                    continue

                # Get model prediction
                param_tensor = (
                    self.optimizer.parameter_transformer.params_to_tensor(
                        param_dict
                    ).unsqueeze(0)
                )

                with torch.no_grad():
                    posterior = model.posterior(param_tensor)
                    pred_val = posterior.mean.item()
                    uncertainty = posterior.variance.sqrt().item()

                # Ensure predictions are finite
                if not (np.isfinite(pred_val) and np.isfinite(uncertainty)):
                    logger.debug(
                        f"Skipping row due to non-finite predictions: pred={pred_val}, unc={uncertainty}"
                    )
                    continue

                actual_values.append(actual_val)
                predicted_values.append(pred_val)
                uncertainties.append(uncertainty)

            except Exception as e:
                logger.debug(f"Error processing row for model analysis: {e}")
                continue

        if not actual_values:
            return None, "No valid data points for model analysis"

        return (
            model, 
            np.array(actual_values), 
            np.array(predicted_values), 
            np.array(uncertainties)
        )

    def _create_residuals_plot(self, ax, actual_values, predicted_values, response_name):
        """
        Create a residuals plot for model analysis.
        
        Args:
            ax: Matplotlib axis object
            actual_values: Array of actual response values
            predicted_values: Array of predicted response values
            response_name: Name of the response being analyzed
        """
        residuals = actual_values - predicted_values
        ax.scatter(predicted_values, residuals, alpha=0.6, s=50)
        ax.axhline(y=0, color="r", linestyle="--", alpha=0.8)
        ax.set_xlabel("Predicted Values", fontsize=12, fontweight="bold")
        ax.set_ylabel("Residuals", fontsize=12, fontweight="bold")
        ax.set_title(
            f"Residuals Plot - {response_name}", fontsize=14, fontweight="bold"
        )

        # Add statistics
        rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))
        mae = mean_absolute_error(actual_values, predicted_values)
        r2 = r2_score(actual_values, predicted_values)

        stats_text = f"RMSE: {rmse:.3f}\nMAE: {mae:.3f}\nR²: {r2:.3f}"
        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

    def _create_predictions_plot(self, ax, actual_values, predicted_values, response_name):
        """
        Create a predicted vs actual plot for model analysis.
        
        Args:
            ax: Matplotlib axis object
            actual_values: Array of actual response values
            predicted_values: Array of predicted response values
            response_name: Name of the response being analyzed
        """
        ax.scatter(actual_values, predicted_values, alpha=0.6, s=50)

        # Perfect prediction line
        min_val = min(np.min(actual_values), np.min(predicted_values))
        max_val = max(np.max(actual_values), np.max(predicted_values))
        ax.plot(
            [min_val, max_val],
            [min_val, max_val],
            "r--",
            alpha=0.8,
            label="Perfect Prediction",
        )

        ax.set_xlabel("Actual Values", fontsize=12, fontweight="bold")
        ax.set_ylabel("Predicted Values", fontsize=12, fontweight="bold")
        ax.set_title(
            f"Predicted vs Actual - {response_name}",
            fontsize=14,
            fontweight="bold",
        )
        ax.legend()

    def _create_uncertainty_plot(self, ax, actual_values, predicted_values, uncertainties, response_name):
        """
        Create an uncertainty plot for model analysis.
        
        Args:
            ax: Matplotlib axis object
            actual_values: Array of actual response values
            predicted_values: Array of predicted response values
            uncertainties: Array of prediction uncertainties
            response_name: Name of the response being analyzed
        """
        ax.errorbar(
            range(len(predicted_values)),
            predicted_values,
            yerr=uncertainties,
            fmt="o",
            alpha=0.6,
            capsize=5,
            label="Predictions \u00b1 Uncertainty",
        )
        ax.scatter(
            range(len(actual_values)),
            actual_values,
            color="red",
            alpha=0.8,
            label="Actual Values",
        )
        ax.set_xlabel("Data Point Index", fontsize=12, fontweight="bold")
        ax.set_ylabel(f"{response_name} Value", fontsize=12, fontweight="bold")
        ax.set_title(
            f"Model Uncertainty - {response_name}",
            fontsize=14,
            fontweight="bold",
        )
        ax.legend()

    def _create_feature_importance_plot(self, fig, ax, model, response_name):
        """
        Create a feature importance plot for model analysis.
        
        Args:
            fig: Matplotlib figure object (for error messages)
            ax: Matplotlib axis object
            model: The trained model for predictions
            response_name: Name of the response being analyzed
            
        Returns:
            bool: True if successful, False if failed
        """
        # Simple feature importance based on parameter sensitivity
        param_names = list(self.optimizer.params_config.keys())
        importances = []

        try:
            for param_name in param_names:
                # Calculate variance in predictions when varying this parameter
                param_config = self.optimizer.params_config[param_name]

                if param_config["type"] == "continuous":
                    bounds = param_config["bounds"]
                    test_values = np.linspace(bounds[0], bounds[1], 10)

                    # Use mean values for other parameters
                    base_params = {}
                    for (
                        p_name,
                        p_config,
                    ) in self.optimizer.params_config.items():
                        if p_name != param_name:
                            if p_config["type"] == "continuous":
                                base_params[p_name] = np.mean(
                                    p_config["bounds"]
                                )
                            elif p_config["type"] == "discrete":
                                base_params[p_name] = int(
                                    np.mean(p_config["bounds"])
                                )
                            elif p_config["type"] == "categorical":
                                base_params[p_name] = p_config["values"][0]

                    predictions = []
                    for val in test_values:
                        try:
                            test_params = {param_name: val, **base_params}
                            param_tensor = self.optimizer.parameter_transformer.params_to_tensor(
                                test_params
                            ).unsqueeze(
                                0
                            )
                            with torch.no_grad():
                                posterior = model.posterior(param_tensor)
                                pred_val = posterior.mean.item()
                                if np.isfinite(pred_val):
                                    predictions.append(pred_val)
                        except Exception as e:
                            logger.debug(
                                f"Error in feature importance calculation for {param_name}: {e}"
                            )
                            continue

                    if len(predictions) > 1:
                        importance = np.var(predictions)
                    else:
                        importance = 0.0
                    importances.append(importance)
                else:
                    importances.append(0)  # For non-continuous parameters

            # Normalize importances safely
            max_importance = max(importances) if importances else 0
            if max_importance > 0:
                importances = [imp / max_importance for imp in importances]

            if not importances or all(imp == 0 for imp in importances):
                self._plot_message(
                    fig,
                    "Unable to calculate feature importance - insufficient variation in predictions",
                )
                return False

            ax.barh(param_names, importances)
            ax.set_xlabel("Relative Importance", fontsize=12, fontweight="bold")
            ax.set_title(
                f"Feature Importance - {response_name}",
                fontsize=14,
                fontweight="bold",
            )
            return True

        except Exception as e:
            logger.error(f"Error calculating feature importance: {e}")
            self._plot_message(
                fig, f"Feature importance calculation failed: {str(e)}"
            )
            return False

    def create_model_analysis_plot(self, fig, canvas, response_name, analysis_type):
        """
        Create Model Analysis plot using appropriate plot type.
        
        Args:
            fig: Matplotlib figure object
            canvas: Canvas for drawing (optional)
            response_name: Name of the response to analyze
            analysis_type: Type of analysis ('residuals', 'predictions', 'uncertainty', 'feature_importance')
        """
        fig.clear()

        try:
            # Prepare data for analysis
            result = self._prepare_model_analysis_data(response_name)
            
            if result[0] is None:
                # Error occurred during data preparation
                self._plot_message(fig, result[1])
                if canvas:
                    canvas.draw()
                return

            model, actual_values, predicted_values, uncertainties = result
            ax = fig.add_subplot(111)

            # Create appropriate plot based on analysis type
            if analysis_type == "residuals":
                self._create_residuals_plot(ax, actual_values, predicted_values, response_name)
                
            elif analysis_type == "predictions" or analysis_type == "parity":
                self._create_predictions_plot(ax, actual_values, predicted_values, response_name)
                
            elif analysis_type == "uncertainty":
                self._create_uncertainty_plot(ax, actual_values, predicted_values, uncertainties, response_name)
                
            elif analysis_type == "feature_importance":
                success = self._create_feature_importance_plot(fig, ax, model, response_name)
                if not success:
                    if canvas:
                        canvas.draw()
                    return

            # Apply common formatting
            ax.grid(True, alpha=0.3)
            fig.tight_layout()

        except Exception as e:
            logger.error(f"Error creating model analysis plot: {e}")
            self._plot_message(fig, f"Model analysis plot error: {str(e)}")

        if canvas:
            canvas.draw()

    def _setup_sensitivity_analysis_base(self, fig, response_name):
        """
        Setup and validate parameters for sensitivity analysis.
        
        Args:
            fig: Matplotlib figure object
            response_name: Name of the response to analyze
            
        Returns:
            tuple: (model, continuous_params, param_bounds, ax) if successful, None if validation fails
        """
        # Get response models
        models = self.optimizer.get_response_models()

        if response_name not in models:
            self._plot_message(
                fig,
                f"Model for {response_name} not available.\n\nThis usually means insufficient data.",
            )
            return None

        model = models[response_name]

        # Get parameter information
        param_names = list(self.optimizer.params_config.keys())
        continuous_params = []
        param_bounds = []

        for param_name in param_names:
            param_config = self.optimizer.params_config[param_name]
            if param_config["type"] == "continuous":
                continuous_params.append(param_name)
                param_bounds.append(param_config["bounds"])

        if len(continuous_params) < 1:
            self._plot_message(
                fig, "Need at least 1 continuous parameter for sensitivity analysis"
            )
            return None

        ax = fig.add_subplot(111)
        return model, continuous_params, param_bounds, ax

    def _calculate_sobol_sensitivity(self, model, continuous_params, param_bounds, n_samples, random_seed=42):
        """
        Calculate Sobol-like sensitivity indices.
        
        Args:
            model: GP model for predictions
            continuous_params: List of continuous parameter names
            param_bounds: List of parameter bounds
            n_samples: Number of samples for analysis
            
        Returns:
            tuple: (sensitivities, errors) - normalized sensitivity indices and error estimates
        """
        # Set random seed for reproducible results
        np.random.seed(random_seed)
        
        sensitivities = []
        errors = []

        for i, param_name in enumerate(continuous_params):
            # Multiple runs for statistical significance
            runs = []
            for run in range(10):  # 10 bootstrap runs
                # Generate samples varying this parameter while keeping others fixed
                bounds = param_bounds[i]
                param_values = np.linspace(
                    bounds[0], bounds[1], min(n_samples // 10, 50)
                )

                # Use mean values for other parameters
                base_params = {}
                for j, other_param in enumerate(continuous_params):
                    if other_param != param_name:
                        other_bounds = param_bounds[j]
                        base_params[other_param] = np.mean(other_bounds)

                # Add non-continuous parameters
                for p_name, p_config in self.optimizer.params_config.items():
                    if p_name not in continuous_params:
                        if p_config["type"] == "discrete":
                            base_params[p_name] = int(
                                np.mean(p_config["bounds"])
                            )
                        elif p_config["type"] == "categorical":
                            base_params[p_name] = p_config["values"][0]

                predictions = []
                for val in param_values:
                    test_params = {param_name: val, **base_params}
                    param_tensor = (
                        self.optimizer.parameter_transformer.params_to_tensor(
                            test_params
                        ).unsqueeze(0)
                    )
                    with torch.no_grad():
                        posterior = model.posterior(param_tensor)
                        predictions.append(posterior.mean.item())

                # Calculate sensitivity as variance
                sensitivity = np.var(predictions)
                runs.append(sensitivity)

            # Calculate mean and standard error across runs
            if runs:
                mean_sensitivity = np.mean(runs)
                std_error = np.std(runs) / np.sqrt(len(runs))
            else:
                mean_sensitivity = 0.0
                std_error = 0.0
            
            sensitivities.append(mean_sensitivity)
            errors.append(std_error)

        # Normalize sensitivities
        if max(sensitivities) > 0:
            norm_factor = sum(sensitivities)
            sensitivities = [s / norm_factor for s in sensitivities]
            errors = [e / norm_factor for e in errors]

        return sensitivities, errors

    def _calculate_morris_sensitivity(self, model, continuous_params, param_bounds, n_samples, random_seed=42):
        """
        Calculate Morris elementary effects with error bars.
        
        Args:
            model: GP model for predictions
            continuous_params: List of continuous parameter names
            param_bounds: List of parameter bounds
            n_samples: Number of samples for analysis
            
        Returns:
            tuple: (effects, errors) - normalized elementary effects and error estimates
        """
        # Set random seed for reproducible results
        np.random.seed(random_seed)
        
        effects = []
        errors = []

        for param_name in continuous_params:
            param_idx = continuous_params.index(param_name)
            bounds = param_bounds[param_idx]

            # Generate random trajectories
            n_trajectories = min(
                50, n_samples // 5
            )  # More trajectories for better statistics
            elementary_effects = []

            for _ in range(n_trajectories):
                # Random starting point
                base_point = {}
                for j, p_name in enumerate(continuous_params):
                    p_bounds = param_bounds[j]
                    base_point[p_name] = np.random.uniform(
                        p_bounds[0], p_bounds[1]
                    )

                # Add non-continuous parameters
                for p_name, p_config in self.optimizer.params_config.items():
                    if p_name not in continuous_params:
                        if p_config["type"] == "discrete":
                            base_point[p_name] = int(
                                np.mean(p_config["bounds"])
                            )
                        elif p_config["type"] == "categorical":
                            base_point[p_name] = p_config["values"][0]

                try:
                    # Evaluate at base point
                    param_tensor1 = (
                        self.optimizer.parameter_transformer.params_to_tensor(
                            base_point
                        ).unsqueeze(0)
                    )
                    with torch.no_grad():
                        y1 = model.posterior(param_tensor1).mean.item()

                    # Perturb parameter
                    delta = (
                        bounds[1] - bounds[0]
                    ) * 0.05  # 5% of range for more precise estimation
                    perturbed_point = base_point.copy()
                    perturbed_point[param_name] = min(
                        bounds[1], base_point[param_name] + delta
                    )

                    # Evaluate at perturbed point
                    param_tensor2 = (
                        self.optimizer.parameter_transformer.params_to_tensor(
                            perturbed_point
                        ).unsqueeze(0)
                    )
                    with torch.no_grad():
                        y2 = model.posterior(param_tensor2).mean.item()

                    # Elementary effect
                    if delta > 0 and np.isfinite(y1) and np.isfinite(y2):
                        effect = abs(y2 - y1) / delta
                        elementary_effects.append(effect)
                except Exception as e:
                    logger.debug(
                        f"Error in Morris method trajectory for {param_name}: {e}"
                    )
                    continue

            # Mean elementary effect and standard error
            if elementary_effects:
                mean_effect = np.mean(elementary_effects)
                std_error = np.std(elementary_effects) / np.sqrt(
                    len(elementary_effects)
                )
            else:
                mean_effect = 0.0
                std_error = 0.0
            effects.append(mean_effect)
            errors.append(std_error)

        # Normalize effects and errors
        if max(effects) > 0:
            norm_factor = max(effects)
            effects = [e / norm_factor for e in effects]
            errors = [e / norm_factor for e in errors]

        return effects, errors

    def _calculate_variance_sensitivity(self, model, continuous_params, param_bounds, n_samples, random_seed=42):
        """
        Calculate variance-based sensitivity with error bars.
        
        Args:
            model: GP model for predictions
            continuous_params: List of continuous parameter names
            param_bounds: List of parameter bounds
            n_samples: Number of samples for analysis
            
        Returns:
            tuple: (variances, errors) - normalized variance contributions and error estimates
        """
        # Set random seed for reproducible results
        np.random.seed(random_seed)
        
        variances = []
        errors = []

        for param_name in continuous_params:
            param_idx = continuous_params.index(param_name)
            bounds = param_bounds[param_idx]

            # Multiple bootstrap samples for error estimation
            variance_estimates = []
            n_bootstrap = 10

            for _ in range(n_bootstrap):
                # Generate random samples
                n_samples_param = min(n_samples // n_bootstrap, 100)
                param_values = np.random.uniform(
                    bounds[0], bounds[1], n_samples_param
                )

                # Use random values for other parameters
                predictions = []
                for val in param_values:
                    test_params = {param_name: val}

                    # Random values for other continuous parameters
                    for j, other_param in enumerate(continuous_params):
                        if other_param != param_name:
                            other_bounds = param_bounds[j]
                            test_params[other_param] = np.random.uniform(
                                other_bounds[0], other_bounds[1]
                            )

                    # Add non-continuous parameters
                    for (
                        p_name,
                        p_config,
                    ) in self.optimizer.params_config.items():
                        if p_name not in continuous_params:
                            if p_config["type"] == "discrete":
                                test_params[p_name] = int(
                                    np.mean(p_config["bounds"])
                                )
                            elif p_config["type"] == "categorical":
                                test_params[p_name] = p_config["values"][0]

                    try:
                        param_tensor = self.optimizer.parameter_transformer.params_to_tensor(
                            test_params
                        ).unsqueeze(
                            0
                        )
                        with torch.no_grad():
                            predictions.append(
                                model.posterior(param_tensor).mean.item()
                            )
                    except Exception as e:
                        logger.debug(
                            f"Error in variance calculation for {param_name}: {e}"
                        )
                        continue

                if len(predictions) > 1:
                    variance = np.var(predictions)
                    variance_estimates.append(variance)

            # Calculate mean and standard error
            if variance_estimates:
                mean_variance = np.mean(variance_estimates)
                std_error = np.std(variance_estimates) / np.sqrt(
                    len(variance_estimates)
                )
            else:
                mean_variance = 0.0
                std_error = 0.0

            variances.append(mean_variance)
            errors.append(std_error)

        # Normalize variances and errors
        total_variance = sum(variances) if sum(variances) > 0 else 1.0
        variances = [v / total_variance for v in variances]
        errors = [e / total_variance for e in errors]

        return variances, errors

    def _calculate_gradient_sensitivity(self, model, continuous_params, param_bounds, n_samples, random_seed=42):
        """
        Calculate gradient-based sensitivity with uncertainty estimation.
        
        Args:
            model: GP model for predictions
            continuous_params: List of continuous parameter names
            param_bounds: List of parameter bounds
            n_samples: Number of samples for analysis
            
        Returns:
            tuple: (gradients, errors) - normalized gradients and error estimates
        """
        # Set random seed for reproducible results
        np.random.seed(random_seed)
        
        gradients = []
        errors = []

        for i, param_name in enumerate(continuous_params):
            bounds = param_bounds[i]
            h = (bounds[1] - bounds[0]) * 0.01  # 1% step

            # Multiple gradient estimates with different starting points
            gradient_estimates = []
            n_estimates = 10

            for _ in range(n_estimates):
                # Random central point
                central_point = {}
                for j, other_param in enumerate(continuous_params):
                    other_bounds = param_bounds[j]
                    if other_param == param_name:
                        # Keep this parameter at center for gradient calculation
                        central_point[other_param] = np.mean(other_bounds)
                    else:
                        # Random value for other parameters
                        central_point[other_param] = np.random.uniform(
                            other_bounds[0], other_bounds[1]
                        )

                # Add non-continuous parameters
                for p_name, p_config in self.optimizer.params_config.items():
                    if p_name not in continuous_params:
                        if p_config["type"] == "discrete":
                            central_point[p_name] = int(
                                np.mean(p_config["bounds"])
                            )
                        elif p_config["type"] == "categorical":
                            central_point[p_name] = p_config["values"][0]

                try:
                    # Forward difference
                    point_plus = central_point.copy()
                    point_plus[param_name] = min(
                        bounds[1], central_point[param_name] + h
                    )

                    point_minus = central_point.copy()
                    point_minus[param_name] = max(
                        bounds[0], central_point[param_name] - h
                    )

                    # Evaluate
                    tensor_plus = (
                        self.optimizer.parameter_transformer.params_to_tensor(
                            point_plus
                        ).unsqueeze(0)
                    )
                    tensor_minus = (
                        self.optimizer.parameter_transformer.params_to_tensor(
                            point_minus
                        ).unsqueeze(0)
                    )

                    with torch.no_grad():
                        y_plus = model.posterior(tensor_plus).mean.item()
                        y_minus = model.posterior(tensor_minus).mean.item()

                    # Central difference gradient
                    if np.isfinite(y_plus) and np.isfinite(y_minus):
                        gradient = abs((y_plus - y_minus) / (2 * h))
                        gradient_estimates.append(gradient)
                except Exception as e:
                    logger.debug(
                        f"Error in gradient estimation for {param_name}: {e}"
                    )
                    continue

            # Calculate mean and standard error
            if gradient_estimates:
                mean_gradient = np.mean(gradient_estimates)
                std_error = np.std(gradient_estimates) / np.sqrt(
                    len(gradient_estimates)
                )
            else:
                mean_gradient = 0.0
                std_error = 0.0

            gradients.append(mean_gradient)
            errors.append(std_error)

        # Normalize gradients and errors
        if max(gradients) > 0:
            norm_factor = max(gradients)
            gradients = [g / norm_factor for g in gradients]
            errors = [e / norm_factor for e in errors]

        return gradients, errors

    def _calculate_lengthscale_sensitivity(self, model, continuous_params):
        """
        Calculate GP lengthscale-based sensitivity (model intrinsic).
        
        Args:
            model: GP model for predictions
            continuous_params: List of continuous parameter names
            
        Returns:
            tuple: (sensitivities, errors) - normalized sensitivities (no errors for this method)
        """
        sensitivities = []

        try:
            # Extract lengthscales from the model
            if hasattr(model.covar_module, "base_kernel") and hasattr(
                model.covar_module.base_kernel, "lengthscale"
            ):
                lengthscales = (
                    model.covar_module.base_kernel.lengthscale.detach()
                    .cpu()
                    .numpy()
                    .flatten()
                )
            elif hasattr(model.covar_module, "lengthscale"):
                lengthscales = (
                    model.covar_module.lengthscale.detach()
                    .cpu()
                    .numpy()
                    .flatten()
                )
            else:
                # Fallback: assume unit lengthscales
                lengthscales = np.ones(len(continuous_params))

            # Convert lengthscales to sensitivities (inverse relationship)
            # Shorter lengthscales = higher sensitivity
            if len(lengthscales) == len(continuous_params):
                sensitivities = [1.0 / max(ls, 1e-6) for ls in lengthscales]
            else:
                # If dimensions don't match, use uniform sensitivity
                sensitivities = [1.0] * len(continuous_params)

            # Normalize
            if max(sensitivities) > 0:
                sensitivities = [s / max(sensitivities) for s in sensitivities]

        except Exception as e:
            logger.error(f"Error extracting lengthscales: {e}")
            sensitivities = [0.0] * len(continuous_params)

        # No errors for this method
        errors = [0.0] * len(continuous_params)
        return sensitivities, errors

    def _calculate_feature_importance_sensitivity(self, model, continuous_params, param_bounds, random_seed=42):
        """
        Calculate feature importance based on GP model structure.
        
        Args:
            model: GP model for predictions
            continuous_params: List of continuous parameter names
            param_bounds: List of parameter bounds
            
        Returns:
            tuple: (importances, errors) - normalized feature importances and error estimates
        """
        # Set random seed for reproducible results
        np.random.seed(random_seed)
        
        importances = []
        errors = []

        for param_name in continuous_params:
            # Calculate feature importance using perturbation method
            importance_estimates = []
            n_estimates = 20

            for _ in range(n_estimates):
                # Generate baseline predictions
                n_test = 50
                test_points = []
                baseline_predictions = []

                for _ in range(n_test):
                    test_params = {}
                    for j, p_name in enumerate(continuous_params):
                        p_bounds = param_bounds[j]
                        test_params[p_name] = np.random.uniform(
                            p_bounds[0], p_bounds[1]
                        )

                    # Add non-continuous parameters
                    for (
                        p_name,
                        p_config,
                    ) in self.optimizer.params_config.items():
                        if p_name not in continuous_params:
                            if p_config["type"] == "discrete":
                                test_params[p_name] = int(
                                    np.mean(p_config["bounds"])
                                )
                            elif p_config["type"] == "categorical":
                                test_params[p_name] = p_config["values"][0]

                    test_points.append(test_params.copy())

                    try:
                        param_tensor = self.optimizer.parameter_transformer.params_to_tensor(
                            test_params
                        ).unsqueeze(
                            0
                        )
                        with torch.no_grad():
                            baseline_predictions.append(
                                model.posterior(param_tensor).mean.item()
                            )
                    except:
                        baseline_predictions.append(0.0)

                # Shuffle the parameter of interest and measure impact
                param_idx = continuous_params.index(param_name)
                bounds = param_bounds[param_idx]

                shuffled_predictions = []
                for test_params in test_points:
                    # Shuffle this parameter
                    test_params[param_name] = np.random.uniform(
                        bounds[0], bounds[1]
                    )

                    try:
                        param_tensor = self.optimizer.parameter_transformer.params_to_tensor(
                            test_params
                        ).unsqueeze(
                            0
                        )
                        with torch.no_grad():
                            shuffled_predictions.append(
                                model.posterior(param_tensor).mean.item()
                            )
                    except:
                        shuffled_predictions.append(0.0)

                # Feature importance as difference in variance
                baseline_var = (
                    np.var(baseline_predictions)
                    if len(baseline_predictions) > 1
                    else 0.0
                )
                shuffled_var = (
                    np.var(shuffled_predictions)
                    if len(shuffled_predictions) > 1
                    else 0.0
                )
                importance = abs(shuffled_var - baseline_var)
                importance_estimates.append(importance)

            # Calculate mean and standard error
            if importance_estimates:
                mean_importance = np.mean(importance_estimates)
                std_error = np.std(importance_estimates) / np.sqrt(
                    len(importance_estimates)
                )
            else:
                mean_importance = 0.0
                std_error = 0.0

            importances.append(mean_importance)
            errors.append(std_error)

        # Normalize
        if max(importances) > 0:
            norm_factor = max(importances)
            importances = [imp / norm_factor for imp in importances]
            errors = [err / norm_factor for err in errors]

        return importances, errors

    def _calculate_fast_sensitivity(self, model, continuous_params, param_bounds, n_samples, random_seed=42):
        """
        Calculate FAST (Fourier Amplitude Sensitivity Test) indices.
        
        Args:
            model: GP model for predictions
            continuous_params: List of continuous parameter names
            param_bounds: Parameter bounds dictionary
            n_samples: Number of samples for analysis
            
        Returns:
            Tuple[List[float], List[float]]: FAST indices and errors
        """
        try:
            import numpy as np
            from scipy.fft import fft
            
            sensitivities = []
            errors = []
            
            # FAST parameters
            M = 4  # Interference parameter
            omega_max = n_samples // (2 * M)
            
            for param_name in continuous_params:
                try:
                    bounds = param_bounds[param_name]
                    
                    # Generate FAST sampling points
                    omega_i = int(omega_max / len(continuous_params))  # Frequency for this parameter
                    
                    # Create G function (search curve)
                    s = np.linspace(0, 2*np.pi, n_samples)
                    
                    # Sample all parameters using FAST approach
                    sample_points = []
                    for i, other_param in enumerate(continuous_params):
                        other_bounds = param_bounds[other_param]
                        if other_param == param_name:
                            # This is the parameter of interest - use higher frequency
                            omega = omega_i
                        else:
                            # Other parameters use different frequencies
                            omega = 1 + i
                        
                        # Transform [-1,1] to parameter bounds
                        param_values = (other_bounds[1] - other_bounds[0])/2 * np.sin(omega * s) + (other_bounds[1] + other_bounds[0])/2
                        sample_points.append(param_values)
                    
                    # Evaluate model at sample points
                    predictions = []
                    for j in range(len(s)):
                        param_dict = {continuous_params[k]: sample_points[k][j] for k in range(len(continuous_params))}
                        
                        # Add non-continuous parameters at their mean values
                        for p_name, p_config in self.optimizer.params_config.items():
                            if p_name not in continuous_params:
                                if p_config["type"] == "discrete":
                                    param_dict[p_name] = int(np.mean(p_config["bounds"]))
                                elif p_config["type"] == "categorical":
                                    param_dict[p_name] = p_config["values"][0]
                        
                        try:
                            param_tensor = self.optimizer.parameter_transformer.params_to_tensor(param_dict).unsqueeze(0)
                            with torch.no_grad():
                                posterior = model.posterior(param_tensor)
                                pred_val = posterior.mean.item()
                                if np.isfinite(pred_val):
                                    predictions.append(pred_val)
                                else:
                                    predictions.append(0.0)
                        except Exception:
                            predictions.append(0.0)
                    
                    predictions = np.array(predictions)
                    
                    # Calculate FAST sensitivity using FFT
                    if len(predictions) > 0:
                        # Compute Fourier coefficients
                        Y_fft = fft(predictions)
                        N = len(predictions)
                        
                        # Calculate total variance
                        total_variance = np.var(predictions)
                        
                        if total_variance > 1e-10:
                            # Calculate variance due to parameter i
                            # Sum over harmonics of omega_i
                            Vi = 0
                            for k in range(1, min(M, N//2)):
                                idx = k * omega_i
                                if idx < N//2:
                                    Vi += 2 * (np.abs(Y_fft[idx])**2 + np.abs(Y_fft[N-idx])**2) / N**2
                            
                            # First-order sensitivity index
                            Si = Vi / total_variance
                            Si = max(0, min(1, Si))  # Clamp to [0,1]
                        else:
                            Si = 0.0
                    else:
                        Si = 0.0
                    
                    sensitivities.append(Si)
                    
                    # Estimate error using bootstrap if we have enough samples
                    if len(predictions) > 20:
                        bootstrap_sis = []
                        for _ in range(10):  # Small number of bootstrap samples
                            idx = np.random.choice(len(predictions), len(predictions)//2, replace=False)
                            boot_pred = predictions[idx]
                            boot_var = np.var(boot_pred)
                            if boot_var > 1e-10:
                                boot_fft = fft(boot_pred)
                                boot_N = len(boot_pred)
                                boot_Vi = 0
                                for k in range(1, min(M, boot_N//2)):
                                    idx_k = k * omega_i
                                    if idx_k < boot_N//2:
                                        boot_Vi += 2 * (np.abs(boot_fft[idx_k])**2 + np.abs(boot_fft[boot_N-idx_k])**2) / boot_N**2
                                boot_Si = max(0, min(1, boot_Vi / boot_var))
                                bootstrap_sis.append(boot_Si)
                        
                        if bootstrap_sis:
                            errors.append(np.std(bootstrap_sis))
                        else:
                            errors.append(0.1 * Si)
                    else:
                        errors.append(0.1 * Si)
                        
                except Exception as e:
                    logger.debug(f"Error calculating FAST sensitivity for {param_name}: {e}")
                    sensitivities.append(0.0)
                    errors.append(0.0)
            
            # Normalize sensitivities
            max_sens = max(sensitivities) if sensitivities else 0
            if max_sens > 0:
                sensitivities = [s / max_sens for s in sensitivities]
                errors = [e / max_sens for e in errors]
            
            return sensitivities, errors
            
        except ImportError:
            logger.warning("SciPy not available for FAST sensitivity analysis, using variance method")
            return self._calculate_variance_sensitivity(model, continuous_params, param_bounds, n_samples)
        except Exception as e:
            logger.error(f"Error in FAST sensitivity calculation: {e}")
            # Fallback to uniform sensitivity
            n_params = len(continuous_params)
            return [1.0/n_params] * n_params, [0.1] * n_params

    def _calculate_delta_sensitivity(self, model, continuous_params, param_bounds, n_samples, random_seed=42):
        """
        Calculate Delta moment-independent sensitivity indices.
        
        Args:
            model: GP model for predictions
            continuous_params: List of continuous parameter names
            param_bounds: Parameter bounds dictionary
            n_samples: Number of samples for analysis
            
        Returns:
            Tuple[List[float], List[float]]: Delta indices and errors
        """
        # Set random seed for reproducible results
        np.random.seed(random_seed)
        
        try:
            sensitivities = []
            errors = []
            
            # Generate reference sample
            ref_samples = []
            for param_name in continuous_params:
                bounds = param_bounds[param_name]
                samples = np.random.uniform(bounds[0], bounds[1], n_samples)
                ref_samples.append(samples)
            
            # Get reference predictions
            ref_predictions = []
            for i in range(n_samples):
                param_dict = {continuous_params[j]: ref_samples[j][i] for j in range(len(continuous_params))}
                
                # Add non-continuous parameters
                for p_name, p_config in self.optimizer.params_config.items():
                    if p_name not in continuous_params:
                        if p_config["type"] == "discrete":
                            param_dict[p_name] = int(np.mean(p_config["bounds"]))
                        elif p_config["type"] == "categorical":
                            param_dict[p_name] = p_config["values"][0]
                
                try:
                    param_tensor = self.optimizer.parameter_transformer.params_to_tensor(param_dict).unsqueeze(0)
                    with torch.no_grad():
                        posterior = model.posterior(param_tensor)
                        pred_val = posterior.mean.item()
                        if np.isfinite(pred_val):
                            ref_predictions.append(pred_val)
                        else:
                            ref_predictions.append(0.0)
                except Exception:
                    ref_predictions.append(0.0)
            
            ref_predictions = np.array(ref_predictions)
            
            # Calculate Delta index for each parameter
            for k, param_name in enumerate(continuous_params):
                try:
                    bounds = param_bounds[param_name]
                    
                    # Generate conditional samples (fix parameter k)
                    cond_predictions = []
                    fixed_values = np.random.uniform(bounds[0], bounds[1], min(50, n_samples//10))
                    
                    for fixed_val in fixed_values:
                        # Generate samples with parameter k fixed
                        for i in range(min(20, n_samples//50)):
                            param_dict = {}
                            for j, other_param in enumerate(continuous_params):
                                if j == k:
                                    param_dict[other_param] = fixed_val
                                else:
                                    other_bounds = param_bounds[other_param]
                                    param_dict[other_param] = np.random.uniform(other_bounds[0], other_bounds[1])
                            
                            # Add non-continuous parameters
                            for p_name, p_config in self.optimizer.params_config.items():
                                if p_name not in continuous_params:
                                    if p_config["type"] == "discrete":
                                        param_dict[p_name] = int(np.mean(p_config["bounds"]))
                                    elif p_config["type"] == "categorical":
                                        param_dict[p_name] = p_config["values"][0]
                            
                            try:
                                param_tensor = self.optimizer.parameter_transformer.params_to_tensor(param_dict).unsqueeze(0)
                                with torch.no_grad():
                                    posterior = model.posterior(param_tensor)
                                    pred_val = posterior.mean.item()
                                    if np.isfinite(pred_val):
                                        cond_predictions.append(pred_val)
                            except Exception:
                                continue
                    
                    if len(cond_predictions) > 5:
                        cond_predictions = np.array(cond_predictions)
                        
                        # Calculate Delta index using CDF comparison
                        # Delta measures the shift in the output distribution
                        ref_sorted = np.sort(ref_predictions)
                        cond_sorted = np.sort(cond_predictions)
                        
                        # Use Kolmogorov-Smirnov-like statistic
                        if len(ref_sorted) > 0 and len(cond_sorted) > 0:
                            # Interpolate to common grid
                            min_val = min(np.min(ref_sorted), np.min(cond_sorted))
                            max_val = max(np.max(ref_sorted), np.max(cond_sorted))
                            
                            if max_val > min_val:
                                grid = np.linspace(min_val, max_val, 50)
                                
                                # Calculate empirical CDFs
                                ref_cdf = np.searchsorted(ref_sorted, grid, side='right') / len(ref_sorted)
                                cond_cdf = np.searchsorted(cond_sorted, grid, side='right') / len(cond_sorted)
                                
                                # Delta index as maximum difference between CDFs
                                delta_index = np.max(np.abs(ref_cdf - cond_cdf))
                            else:
                                delta_index = 0.0
                        else:
                            delta_index = 0.0
                    else:
                        delta_index = 0.0
                    
                    sensitivities.append(delta_index)
                    errors.append(0.1 * delta_index)  # Simple error estimate
                    
                except Exception as e:
                    logger.debug(f"Error calculating Delta sensitivity for {param_name}: {e}")
                    sensitivities.append(0.0)
                    errors.append(0.0)
            
            # Normalize sensitivities
            max_sens = max(sensitivities) if sensitivities else 0
            if max_sens > 0:
                sensitivities = [s / max_sens for s in sensitivities]
                errors = [e / max_sens for e in errors]
            
            return sensitivities, errors
            
        except Exception as e:
            logger.error(f"Error in Delta sensitivity calculation: {e}")
            # Fallback to uniform sensitivity
            n_params = len(continuous_params)
            return [1.0/n_params] * n_params, [0.1] * n_params

    def _calculate_mixed_sensitivity(self, model, continuous_params, param_bounds, n_samples, random_seed=42):
        """
        Calculate mixed parameter sensitivity including both continuous and discrete parameters.
        
        Uses variance-based methods for continuous parameters and exhaustive enumeration
        for discrete parameters, providing a unified sensitivity ranking.
        
        Args:
            model: GP model for predictions
            continuous_params: List of continuous parameter names
            param_bounds: List of parameter bounds for continuous parameters
            n_samples: Number of samples for analysis
            random_seed: Random seed for reproducibility
            
        Returns:
            tuple: (sensitivities, errors, param_names) - combined sensitivity results
        """
        try:
            logger.debug("Starting mixed parameter sensitivity analysis")
            
            # Initialize combined results
            all_sensitivities = []
            all_errors = []
            all_param_names = []
            
            # 1. Calculate continuous parameter sensitivities using variance method
            if continuous_params:
                logger.debug(f"Analyzing {len(continuous_params)} continuous parameters")
                cont_sensitivities, cont_errors = self._calculate_variance_sensitivity(
                    model, continuous_params, param_bounds, n_samples, random_seed
                )
                all_sensitivities.extend(cont_sensitivities)
                all_errors.extend(cont_errors)
                all_param_names.extend(continuous_params)
            
            # 2. Identify and analyze discrete parameters
            discrete_params = []
            categorical_params = []
            
            for param_name, param_config in self.optimizer.params_config.items():
                if param_name not in continuous_params:
                    if param_config["type"] == "discrete":
                        discrete_params.append(param_name)
                    elif param_config["type"] == "categorical":
                        categorical_params.append(param_name)
            
            # 3. Calculate discrete parameter sensitivities
            if discrete_params or categorical_params:
                logger.debug(f"Analyzing {len(discrete_params)} discrete and {len(categorical_params)} categorical parameters")
                
                for param_name in discrete_params + categorical_params:
                    param_config = self.optimizer.params_config[param_name]
                    sensitivity, error = self._calculate_single_discrete_sensitivity(
                        model, param_name, param_config, continuous_params, param_bounds, n_samples, random_seed
                    )
                    all_sensitivities.append(sensitivity)
                    all_errors.append(error)
                    all_param_names.append(param_name)
            
            # 4. Normalize all sensitivities to same scale
            if all_sensitivities and max(all_sensitivities) > 0:
                norm_factor = max(all_sensitivities)
                all_sensitivities = [s / norm_factor for s in all_sensitivities]
                all_errors = [e / norm_factor for e in all_errors]
            
            logger.debug(f"Mixed sensitivity analysis completed: {len(all_param_names)} total parameters")
            return all_sensitivities, all_errors, all_param_names
            
        except Exception as e:
            logger.error(f"Error in mixed sensitivity calculation: {e}")
            # Fallback: return continuous parameters only
            if continuous_params:
                cont_sensitivities, cont_errors = self._calculate_variance_sensitivity(
                    model, continuous_params, param_bounds, n_samples, random_seed
                )
                return cont_sensitivities, cont_errors, continuous_params
            else:
                return [], [], []
    
    def _calculate_single_discrete_sensitivity(self, model, param_name, param_config, continuous_params, param_bounds, n_samples, random_seed):
        """
        Calculate sensitivity for a single discrete or categorical parameter.
        
        Uses exhaustive enumeration approach - tests all possible values and measures
        the variance in model predictions.
        """
        try:
            # Get possible values for this parameter
            if param_config["type"] == "discrete":
                if "values" in param_config:
                    possible_values = param_config["values"]
                else:
                    # Generate integer values from bounds
                    bounds = param_config["bounds"]
                    possible_values = list(range(int(bounds[0]), int(bounds[1]) + 1))
            else:  # categorical
                possible_values = param_config["values"]
            
            if len(possible_values) <= 1:
                return 0.0, 0.0  # No sensitivity if only one value possible
            
            # Set up base point for other parameters
            np.random.seed(random_seed)
            
            # Multiple runs for statistical robustness
            sensitivity_estimates = []
            n_bootstrap = min(10, max(3, n_samples // 100))  # Adaptive bootstrap
            
            for bootstrap_run in range(n_bootstrap):
                predictions_per_value = []
                
                for discrete_value in possible_values:
                    # Generate random samples with this discrete value fixed
                    n_test_points = max(20, n_samples // (len(possible_values) * n_bootstrap))
                    predictions = []
                    
                    for _ in range(n_test_points):
                        # Create test point
                        test_point = {param_name: discrete_value}
                        
                        # Random values for continuous parameters
                        for i, cont_param in enumerate(continuous_params):
                            bounds = param_bounds[i]
                            test_point[cont_param] = np.random.uniform(bounds[0], bounds[1])
                        
                        # Fixed values for other discrete parameters
                        for other_param, other_config in self.optimizer.params_config.items():
                            if other_param != param_name and other_param not in continuous_params:
                                if other_config["type"] == "discrete":
                                    if "values" in other_config:
                                        test_point[other_param] = other_config["values"][0]
                                    else:
                                        test_point[other_param] = int(np.mean(other_config["bounds"]))
                                elif other_config["type"] == "categorical":
                                    test_point[other_param] = other_config["values"][0]
                        
                        # Get model prediction
                        try:
                            pred_mean, pred_var = model.predict(test_point)
                            if hasattr(pred_mean, 'item'):
                                prediction = pred_mean.item()
                            else:
                                prediction = float(pred_mean)
                            predictions.append(prediction)
                        except Exception:
                            predictions.append(0.0)
                    
                    # Calculate mean prediction for this discrete value
                    if predictions:
                        predictions_per_value.append(np.mean(predictions))
                
                # Calculate sensitivity as variance across discrete values
                if len(predictions_per_value) > 1:
                    sensitivity = np.var(predictions_per_value)
                    sensitivity_estimates.append(sensitivity)
            
            # Calculate final sensitivity and error
            if sensitivity_estimates:
                mean_sensitivity = np.mean(sensitivity_estimates)
                std_error = np.std(sensitivity_estimates) / np.sqrt(len(sensitivity_estimates))
            else:
                mean_sensitivity = 0.0
                std_error = 0.0
            
            return mean_sensitivity, std_error
            
        except Exception as e:
            logger.debug(f"Error calculating discrete sensitivity for {param_name}: {e}")
            return 0.0, 0.0

    def _plot_sensitivity_results(self, ax, continuous_params, values, errors, response_name, method, ylabel):
        """
        Plot sensitivity results with error bars and formatting.
        
        Args:
            ax: Matplotlib axis object
            continuous_params: List of continuous parameter names
            values: Sensitivity values to plot
            errors: Error estimates for error bars
            response_name: Name of the response
            method: Sensitivity analysis method name
            ylabel: Y-axis label
            
        Returns:
            matplotlib.container.BarContainer: The bar plot object
        """
        # Create bar plot with or without error bars
        if any(e > 0 for e in errors):
            bars = ax.bar(
                continuous_params,
                values,
                yerr=errors,
                capsize=5,
                alpha=0.7,
                error_kw={"linewidth": 2, "ecolor": "black"},
            )
        else:
            bars = ax.bar(continuous_params, values, alpha=0.7)
            
        # Set labels and title
        ax.set_ylabel(ylabel, fontsize=12, fontweight="bold")
        
        # Create title based on method
        method_titles = {
            "sobol": "Sobol Sensitivity Analysis",
            "morris": "Morris Sensitivity Analysis", 
            "gradient": "Gradient-based Sensitivity",
            "variance": "Variance-based Sensitivity",
            "lengthscale": "GP Intrinsic Sensitivity",
            "feature_importance": "Feature Importance Analysis"
        }
        
        title = method_titles.get(method, f"{method.title()} Sensitivity Analysis")
        ax.set_title(f"{title} - {response_name}", fontsize=14, fontweight="bold")
        
        return bars

    def _format_sensitivity_plot(self, ax, fig):
        """
        Apply final formatting to sensitivity analysis plot.
        
        Args:
            ax: Matplotlib axis object
            fig: Matplotlib figure object
        """
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

    def create_sensitivity_analysis_plot(
        self, fig, canvas, response_name, method="variance", n_samples=500, random_seed=42
    ):
        """Create Enhanced Sensitivity Analysis plot with multiple methods and error bars"""
        fig.clear()
        
        # Set random seed for reproducible results
        np.random.seed(random_seed)

        try:
            # Setup and validate parameters
            setup_result = self._setup_sensitivity_analysis_base(fig, response_name)
            if setup_result is None:
                if canvas:
                    canvas.draw()
                return
            
            model, continuous_params, param_bounds, ax = setup_result

            if method == "sobol":
                sensitivities, errors = self._calculate_sobol_sensitivity(
                    model, continuous_params, param_bounds, n_samples, random_seed
                )
                self._plot_sensitivity_results(
                    ax, continuous_params, sensitivities, errors, response_name, method, "Sensitivity Index"
                )

            elif method == "morris":
                effects, errors = self._calculate_morris_sensitivity(
                    model, continuous_params, param_bounds, n_samples, random_seed
                )
                self._plot_sensitivity_results(
                    ax, continuous_params, effects, errors, response_name, method, "Normalized Mean Elementary Effect"
                )

            elif method == "gradient":
                gradients, errors = self._calculate_gradient_sensitivity(
                    model, continuous_params, param_bounds, n_samples, random_seed
                )
                self._plot_sensitivity_results(
                    ax, continuous_params, gradients, errors, response_name, method, "Normalized Local Gradient"
                )


            elif method == "lengthscale":
                try:
                    sensitivities, errors = self._calculate_lengthscale_sensitivity(
                        model, continuous_params
                    )
                    self._plot_sensitivity_results(
                        ax, continuous_params, sensitivities, errors, response_name, method, "GP Lengthscale-based Sensitivity"
                    )
                except Exception as e:
                    logger.error(f"Error in lengthscale sensitivity calculation: {e}")
                    self._plot_message(
                        fig,
                        f"Could not extract GP lengthscales for sensitivity analysis",
                    )
                    if canvas:
                        canvas.draw()
                    return

            elif method == "variance":
                variances, errors = self._calculate_variance_sensitivity(
                    model, continuous_params, param_bounds, n_samples, random_seed
                )
                self._plot_sensitivity_results(
                    ax, continuous_params, variances, errors, response_name, method, "Variance Contribution"
                )

            elif method == "feature_importance":
                importances, errors = self._calculate_feature_importance_sensitivity(
                    model, continuous_params, param_bounds, random_seed
                )
                self._plot_sensitivity_results(
                    ax, continuous_params, importances, errors, response_name, method, "Normalized Feature Importance"
                )

            elif method == "fast":
                sensitivities, errors = self._calculate_fast_sensitivity(
                    model, continuous_params, param_bounds, n_samples, random_seed
                )
                self._plot_sensitivity_results(
                    ax, continuous_params, sensitivities, errors, response_name, method, "FAST Sensitivity Index"
                )

            elif method == "delta":
                delta_indices, errors = self._calculate_delta_sensitivity(
                    model, continuous_params, param_bounds, n_samples, random_seed
                )
                self._plot_sensitivity_results(
                    ax, continuous_params, delta_indices, errors, response_name, method, "Delta Moment-Independent Index"
                )

            elif method == "mixed":
                sensitivities, errors, param_names = self._calculate_mixed_sensitivity(
                    model, continuous_params, param_bounds, n_samples, random_seed
                )
                self._plot_sensitivity_results(
                    ax, param_names, sensitivities, errors, response_name, method, "Normalized Sensitivity Index"
                )

            else:
                # Default to variance method if unknown method specified
                self.create_sensitivity_analysis_plot(
                    fig, canvas, response_name, method="variance", n_samples=n_samples, random_seed=random_seed
                )
                return

            # Format plot
            self._format_sensitivity_plot(ax, fig)

        except Exception as e:
            logger.error(f"Error creating sensitivity analysis plot: {e}")
            self._plot_message(fig, f"Sensitivity analysis plot error: {str(e)}")

        if canvas:
            canvas.draw()

    def _get_all_objectives_data(self):
        """Get all objectives data for plotting"""
        if self.optimizer.experimental_data.empty:
            return pd.DataFrame()

        df = pd.DataFrame()
        for obj_name in self.optimizer.objective_names:
            if obj_name in self.optimizer.experimental_data.columns:
                # Handle both single values and lists for responses, and direct values for parameters
                if obj_name in self.optimizer.responses_config:
                    df[obj_name] = self.optimizer.experimental_data[obj_name].apply(
                        lambda x: np.mean(x) if isinstance(x, list) and x else x
                    )
                else:  # Assume it's a parameter that is also an objective
                    df[obj_name] = self.optimizer.experimental_data[obj_name]
            else:
                logger.warning(
                    f"Objective {obj_name} not found in experimental data columns."
                )

        return df.dropna()

    def _plot_message(self, fig, message):
        """Plot a message when no data is available"""
        ax = fig.add_subplot(111)
        ax.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=12,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8),
        )
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    def create_gp_uncertainty_map(
        self,
        fig,
        canvas,
        response_name,
        param1_name,
        param2_name,
        plot_style="heatmap",
        uncertainty_metric="gp_uncertainty",
        colormap="Reds",
        resolution=70,
        show_experimental_data=True,
        show_gp_uncertainty=True,
        show_data_density=False,
        show_statistical_deviation=False,
    ):
        """
        Create single GP uncertainty map with user-selectable visualization types

        This creates a unified view showing user-selected uncertainty visualization:
        1. GP Prediction Uncertainty - Model's predictive uncertainty from GP posterior
        2. Data Density - Spatial density of experimental data points

        Args:
            fig: Matplotlib figure
            canvas: Canvas for drawing
            response_name: Name of response variable
            param1_name: Name of first parameter (x-axis)
            param2_name: Name of second parameter (y-axis)
            plot_style: 'heatmap', 'contour', 'filled_contour', or 'combined'
            uncertainty_metric: 'gp_uncertainty', 'data_density'
            colormap: Matplotlib colormap name
            resolution: Grid resolution for heatmap
            show_experimental_data: Whether to overlay experimental data points
            show_gp_uncertainty: Show GP prediction uncertainty
            show_data_density: Show data density
            show_statistical_deviation: (Deprecated - no longer used)
        """
        fig.clear()

        try:
            # Create single subplot for unified view
            ax = fig.add_subplot(111)
            
            # Determine which visualization to show based on user selection
            if show_gp_uncertainty and uncertainty_metric == "gp_uncertainty":
                self._create_gp_prediction_uncertainty_plot(
                    ax,
                    response_name,
                    param1_name,
                    param2_name,
                    plot_style,
                    colormap,
                    resolution,
                    show_experimental_data,
                )
                plot_title = f"GP Prediction Uncertainty: {response_name}"
                
            elif show_data_density and uncertainty_metric == "data_density":
                self._create_data_density_plot(
                    ax,
                    response_name,
                    param1_name,
                    param2_name,
                    plot_style,
                    colormap,
                    resolution,
                    show_experimental_data,
                )
                plot_title = f"Data Density: {response_name}"
                
            else:
                # Default to GP uncertainty if no specific selection
                self._create_gp_prediction_uncertainty_plot(
                    ax,
                    response_name,
                    param1_name,
                    param2_name,
                    plot_style,
                    colormap,
                    resolution,
                    show_experimental_data,
                )
                plot_title = f"GP Prediction Uncertainty: {response_name}"

            # Set title for single plot
            ax.set_title(
                f"{plot_title}\nvs {param1_name} & {param2_name}",
                fontsize=12,
                fontweight="bold",
                pad=20,
            )

            if canvas:
                canvas.draw()

        except Exception as e:
            logger.error(f"Error creating GP uncertainty map: {e}", exc_info=True)
            self._plot_message(fig, f"GP uncertainty map error: {str(e)}")
            if canvas:
                canvas.draw()

    def _create_gp_prediction_uncertainty_plot(
        self,
        ax,
        response_name,
        param1_name,
        param2_name,
        plot_style,
        colormap,
        resolution,
        show_experimental_data,
    ):
        """Create GP prediction uncertainty heatmap showing model's predictive uncertainty"""
        try:
            # Get GP models
            models = self.optimizer.get_response_models()
            if response_name not in models:
                self._plot_message_on_axis(ax, f"No GP model for {response_name}")
                return

            model = models[response_name]

            # Generate prediction grid
            test_X, param1_vals, param2_vals = self._generate_prediction_grid(
                param1_name, param2_name, resolution
            )

            if test_X is None:
                self._plot_message_on_axis(
                    ax, f"Cannot create grid for {param1_name}, {param2_name}"
                )
                return

            # Get GP posterior predictions with uncertainty
            uncertainty_grid = self._get_gp_posterior_uncertainty(
                model, test_X, resolution
            )

            if uncertainty_grid is None:
                self._plot_message_on_axis(
                    ax, "Failed to get GP uncertainty predictions"
                )
                return

            # Create grid for plotting
            X1, X2 = np.meshgrid(param1_vals, param2_vals)

            # Create the GP uncertainty visualization
            self._create_uncertainty_visualization(
                ax,
                X1,
                X2,
                uncertainty_grid,
                f"GP Prediction Uncertainty: {response_name}",
                param1_name,
                param2_name,
                plot_style,
                colormap,
                "Prediction Std",
                show_experimental_data,
            )

        except Exception as e:
            logger.error(f"Error creating GP prediction uncertainty plot: {e}")
            self._plot_message_on_axis(ax, f"GP uncertainty error: {str(e)}")

    def _create_data_density_plot(
        self,
        ax,
        response_name,
        param1_name,
        param2_name,
        plot_style,
        colormap,
        resolution,
        show_experimental_data,
    ):
        """Create data density heatmap showing spatial distribution of experimental data"""
        try:
            # Get experimental data
            if not hasattr(self.optimizer, 'experimental_data') or self.optimizer.experimental_data.empty:
                self._plot_message_on_axis(ax, "No experimental data available")
                return
            
            data = self.optimizer.experimental_data

            # Get parameter bounds for grid
            param1_config = self.optimizer.params_config.get(param1_name)
            param2_config = self.optimizer.params_config.get(param2_name)

            if not param1_config or not param2_config:
                self._plot_message_on_axis(ax, f"Cannot find parameters {param1_name}, {param2_name}")
                return

            # Get experimental data for these parameters
            if param1_name not in data.columns or param2_name not in data.columns:
                self._plot_message_on_axis(ax, f"No data for parameters {param1_name}, {param2_name}")
                return

            x1_data = data[param1_name].values
            x2_data = data[param2_name].values

            # Check if we have enough data points for KDE
            if len(x1_data) < 2:
                self._plot_message_on_axis(ax, "Need at least 2 data points for density estimation")
                return

            # Create grid for density calculation
            x1_bounds = param1_config["bounds"]
            x2_bounds = param2_config["bounds"]
            x1_vals = np.linspace(x1_bounds[0], x1_bounds[1], resolution)
            x2_vals = np.linspace(x2_bounds[0], x2_bounds[1], resolution)
            X1, X2 = np.meshgrid(x1_vals, x2_vals)

            # Calculate data density using kernel density estimation
            from scipy.stats import gaussian_kde
            
            # Create KDE from experimental data points
            points = np.vstack([x1_data, x2_data])
            
            # Check for insufficient data variation
            x1_var = np.var(points[0])
            x2_var = np.var(points[1])
            min_variance_threshold = 1e-10
            
            # Handle edge cases where data has insufficient variation
            if (np.all(points[0] == points[0][0]) and np.all(points[1] == points[1][0])) or len(points[0]) < 2:
                # All points are at the same location or too few points, create a simple peak
                center_x, center_y = np.mean(points[0]), np.mean(points[1])
                sigma = 0.1 * min(x1_bounds[1] - x1_bounds[0], x2_bounds[1] - x2_bounds[0])
                density_grid = np.exp(-((X1 - center_x)**2 + (X2 - center_y)**2) / (2 * sigma**2))
            elif x1_var < min_variance_threshold or x2_var < min_variance_threshold:
                # One dimension has no variation, use simple Gaussian around the mean
                center_x, center_y = np.mean(points[0]), np.mean(points[1])
                # Use larger sigma for dimensions with no variation
                sigma_x = max(np.sqrt(x1_var), 0.1 * (x1_bounds[1] - x1_bounds[0]))
                sigma_y = max(np.sqrt(x2_var), 0.1 * (x2_bounds[1] - x2_bounds[0]))
                density_grid = np.exp(-((X1 - center_x)**2 / (2 * sigma_x**2) + (X2 - center_y)**2 / (2 * sigma_y**2)))
            else:
                try:
                    kde = gaussian_kde(points)
                    # Evaluate KDE on grid
                    grid_points = np.vstack([X1.ravel(), X2.ravel()])
                    density_grid = kde(grid_points).reshape(X1.shape)
                except np.linalg.LinAlgError:
                    # KDE failed due to singular covariance matrix, fallback to simple Gaussian
                    logger.warning("KDE failed due to singular covariance matrix, using fallback Gaussian approximation")
                    center_x, center_y = np.mean(points[0]), np.mean(points[1])
                    sigma_x = max(np.std(points[0]), 0.1 * (x1_bounds[1] - x1_bounds[0]))
                    sigma_y = max(np.std(points[1]), 0.1 * (x2_bounds[1] - x2_bounds[0]))
                    density_grid = np.exp(-((X1 - center_x)**2 / (2 * sigma_x**2) + (X2 - center_y)**2 / (2 * sigma_y**2)))

            # Create the data density visualization
            self._create_uncertainty_visualization(
                ax,
                X1,
                X2,
                density_grid,
                f"Data Density: {response_name}\\nvs {param1_name} & {param2_name}",
                param1_name,
                param2_name,
                plot_style,
                colormap,
                "Data Density",
                show_experimental_data,
            )

        except Exception as e:
            logger.error(f"Error creating data density plot: {e}")
            self._plot_message_on_axis(ax, f"Data density error: {str(e)}")

    def _create_statistical_deviation_plot(
        self,
        ax,
        response_name,
        param1_name,
        param2_name,
        uncertainty_metric,
        plot_style,
        colormap,
        resolution,
        show_experimental_data,
    ):
        """Create statistical deviation heatmap"""
        try:
            # Get GP models
            models = self.optimizer.get_response_models()
            if response_name not in models:
                self._plot_message_on_axis(ax, f"No GP model for {response_name}")
                return

            model = models[response_name]

            # Generate prediction grid
            test_X, param1_vals, param2_vals = self._generate_prediction_grid(
                param1_name, param2_name, resolution
            )

            if test_X is None:
                self._plot_message_on_axis(
                    ax, f"Cannot create grid for {param1_name}, {param2_name}"
                )
                return

            # Get statistical uncertainty predictions
            uncertainty_grid = self._get_statistical_uncertainty_with_params(
                param1_name, param2_name, resolution, uncertainty_metric, response_name
            )

            if uncertainty_grid is None:
                self._plot_message_on_axis(
                    ax, "Failed to get statistical uncertainty predictions"
                )
                return

            # Create grid for plotting
            X1, X2 = np.meshgrid(param1_vals, param2_vals)

            # Create metric display name
            metric_display = {
                "data_density": "Data Density (Inverse)",
                "local_variance": "Local Data Variance",
                "nearest_neighbor_distance": "Nearest Neighbor Distance",
                "std": "Standard Deviation",
                "variance": "Variance",
                "coefficient_of_variation": "Coefficient of Variation",
            }.get(uncertainty_metric, uncertainty_metric.replace("_", " ").title())

            # Create the statistical deviation visualization
            self._create_uncertainty_visualization(
                ax,
                X1,
                X2,
                uncertainty_grid,
                f"Statistical Deviations: {metric_display}\\n{response_name}",
                param1_name,
                param2_name,
                plot_style,
                colormap,
                metric_display,
                show_experimental_data,
            )

        except Exception as e:
            logger.error(f"Error creating statistical deviation plot: {e}")
            self._plot_message_on_axis(ax, f"Statistical deviation error: {str(e)}")

    def _generate_prediction_grid(self, param1_name, param2_name, resolution):
        """Generate prediction grid for GP uncertainty plotting"""
        try:
            # Get parameter configurations
            param1_config = self.optimizer.params_config.get(param1_name)
            param2_config = self.optimizer.params_config.get(param2_name)

            if not param1_config or not param2_config:
                return None, None, None

            # Generate parameter grid
            x1_bounds = param1_config["bounds"]
            x2_bounds = param2_config["bounds"]

            x1_vals = np.linspace(x1_bounds[0], x1_bounds[1], resolution)
            x2_vals = np.linspace(x2_bounds[0], x2_bounds[1], resolution)
            X1, X2 = np.meshgrid(x1_vals, x2_vals)

            # Create intelligent base point for other parameters
            base_point = self._create_intelligent_base_point_3d(
                param1_name, param2_name
            )

            # Generate prediction grid
            prediction_points = self._generate_surface_predictions_efficient(
                X1, X2, param1_name, param2_name, base_point, resolution
            )

            return prediction_points, x1_vals, x2_vals

        except Exception as e:
            logger.error(f"Failed to generate prediction grid: {e}")
            return None, None, None

    def _get_gp_posterior_uncertainty(self, model, test_X, resolution):
        """Get GP posterior uncertainty (prediction standard deviation)"""
        try:
            model.eval()
            with torch.no_grad():
                posterior = model.posterior(test_X)
                # Get prediction uncertainty (standard deviation)
                uncertainty = posterior.variance.sqrt().squeeze().cpu().numpy()
                return uncertainty.reshape(resolution, resolution)
        except Exception as e:
            logger.error(f"Failed to get GP posterior uncertainty: {e}")
            return None

    def _get_statistical_uncertainty(
        self, model, test_X, resolution, uncertainty_metric
    ):
        """Get data-based statistical uncertainty (NOT GP-derived)"""
        try:
            # This should be based on actual experimental data, not GP predictions
            # Get experimental data for local statistical analysis
            exp_data = self.optimizer.experimental_data

            if exp_data.empty:
                # If no experimental data, return zeros
                return np.zeros((resolution, resolution))

            # Get parameter bounds for grid generation
            param_names = list(self.optimizer.params_config.keys())
            if len(param_names) < 2:
                return np.zeros((resolution, resolution))

            param1_name, param2_name = param_names[0], param_names[1]
            param1_config = self.optimizer.params_config[param1_name]
            param2_config = self.optimizer.params_config[param2_name]

            x1_bounds = param1_config["bounds"]
            x2_bounds = param2_config["bounds"]

            x1_vals = np.linspace(x1_bounds[0], x1_bounds[1], resolution)
            x2_vals = np.linspace(x2_bounds[0], x2_bounds[1], resolution)

            # Create data-based uncertainty map
            uncertainty_map = np.zeros((resolution, resolution))

            # Extract experimental parameter values
            if (
                param1_name not in exp_data.columns
                or param2_name not in exp_data.columns
            ):
                return uncertainty_map

            exp_p1 = exp_data[param1_name].values
            exp_p2 = exp_data[param2_name].values

            # Calculate local data density/uncertainty for each grid point
            for i in range(resolution):
                for j in range(resolution):
                    grid_p1, grid_p2 = x1_vals[i], x2_vals[j]

                    # Calculate distances to all experimental points
                    distances = np.sqrt(
                        (exp_p1 - grid_p1) ** 2 + (exp_p2 - grid_p2) ** 2
                    )

                    if uncertainty_metric == "data_density":
                        # Inverse data density (high uncertainty where data is sparse)
                        # Use Gaussian kernel to weight nearby points
                        kernel_width = (
                            x1_bounds[1] - x1_bounds[0]
                        ) / 10  # Adaptive width
                        weights = np.exp(-(distances**2) / (2 * kernel_width**2))
                        density = np.sum(weights)
                        uncertainty_map[j, i] = 1.0 / (
                            1.0 + density
                        )  # Higher uncertainty = less dense

                    elif uncertainty_metric == "local_variance":
                        # Local data variance in neighborhood
                        nearby_threshold = (
                            min(
                                x1_bounds[1] - x1_bounds[0], x2_bounds[1] - x2_bounds[0]
                            )
                            / 5
                        )
                        nearby_mask = distances < nearby_threshold

                        if np.sum(nearby_mask) > 1:
                            # Calculate variance of nearby experimental points
                            nearby_distances = distances[nearby_mask]
                            local_var = np.var(nearby_distances)
                            uncertainty_map[j, i] = local_var
                        else:
                            uncertainty_map[j, i] = (
                                1.0  # High uncertainty if no nearby points
                            )

                    elif uncertainty_metric == "nearest_neighbor_distance":
                        # Distance to nearest experimental point
                        min_distance = np.min(distances)
                        uncertainty_map[j, i] = min_distance

                    else:  # Default: data_density
                        kernel_width = (x1_bounds[1] - x1_bounds[0]) / 10
                        weights = np.exp(-(distances**2) / (2 * kernel_width**2))
                        density = np.sum(weights)
                        uncertainty_map[j, i] = 1.0 / (1.0 + density)

            return uncertainty_map

        except Exception as e:
            logger.error(f"Failed to get statistical uncertainty: {e}")
            return np.zeros((resolution, resolution))

    def _get_statistical_uncertainty_with_params(
        self, param1_name, param2_name, resolution, uncertainty_metric, response_name=None
    ):
        """Get data-based statistical uncertainty using specific parameter names"""
        try:
            # Get experimental data for local statistical analysis
            exp_data = self.optimizer.experimental_data

            if exp_data.empty:
                return np.zeros((resolution, resolution))

            # Get parameter configurations
            param1_config = self.optimizer.params_config.get(param1_name)
            param2_config = self.optimizer.params_config.get(param2_name)

            if not param1_config or not param2_config:
                return np.zeros((resolution, resolution))

            x1_bounds = param1_config["bounds"]
            x2_bounds = param2_config["bounds"]

            x1_vals = np.linspace(x1_bounds[0], x1_bounds[1], resolution)
            x2_vals = np.linspace(x2_bounds[0], x2_bounds[1], resolution)

            # Create data-based uncertainty map
            uncertainty_map = np.zeros((resolution, resolution))

            # Extract experimental parameter values
            if (
                param1_name not in exp_data.columns
                or param2_name not in exp_data.columns
            ):
                return uncertainty_map

            exp_p1 = exp_data[param1_name].values
            exp_p2 = exp_data[param2_name].values

            # Calculate local data density/uncertainty for each grid point
            for i in range(resolution):
                for j in range(resolution):
                    grid_p1, grid_p2 = x1_vals[i], x2_vals[j]

                    # Calculate distances to all experimental points
                    distances = np.sqrt(
                        (exp_p1 - grid_p1) ** 2 + (exp_p2 - grid_p2) ** 2
                    )

                    if uncertainty_metric == "data_density":
                        # Inverse data density (high uncertainty where data is sparse)
                        kernel_width = (x1_bounds[1] - x1_bounds[0]) / 10
                        weights = np.exp(-(distances**2) / (2 * kernel_width**2))
                        density = np.sum(weights)
                        uncertainty_map[j, i] = 1.0 / (1.0 + density)

                    elif uncertainty_metric == "local_variance":
                        # Local data variance in neighborhood
                        nearby_threshold = (
                            min(
                                x1_bounds[1] - x1_bounds[0], x2_bounds[1] - x2_bounds[0]
                            )
                            / 5
                        )
                        nearby_mask = distances < nearby_threshold

                        if np.sum(nearby_mask) > 1:
                            nearby_distances = distances[nearby_mask]
                            local_var = np.var(nearby_distances)
                            uncertainty_map[j, i] = local_var
                        else:
                            uncertainty_map[j, i] = 1.0

                    elif uncertainty_metric == "nearest_neighbor_distance":
                        # Distance to nearest experimental point
                        min_distance = np.min(distances)
                        uncertainty_map[j, i] = min_distance

                    elif uncertainty_metric == "std":
                        # Standard deviation of nearby response values
                        nearby_threshold = (
                            min(
                                x1_bounds[1] - x1_bounds[0], x2_bounds[1] - x2_bounds[0]
                            )
                            / 5
                        )
                        nearby_mask = distances < nearby_threshold

                        if np.sum(nearby_mask) > 1 and response_name and response_name in exp_data.columns:
                            # Get response values for nearby points for specific response
                            nearby_responses = exp_data[response_name].values[nearby_mask]
                            
                            if len(nearby_responses) > 1:
                                local_std = np.std(nearby_responses)
                                uncertainty_map[j, i] = local_std
                            else:
                                uncertainty_map[j, i] = np.min(distances)
                        else:
                            uncertainty_map[j, i] = np.min(distances)

                    elif uncertainty_metric == "variance":
                        # Variance of nearby response values
                        nearby_threshold = (
                            min(
                                x1_bounds[1] - x1_bounds[0], x2_bounds[1] - x2_bounds[0]
                            )
                            / 5
                        )
                        nearby_mask = distances < nearby_threshold

                        if np.sum(nearby_mask) > 1 and response_name and response_name in exp_data.columns:
                            # Get response values for nearby points for specific response
                            nearby_responses = exp_data[response_name].values[nearby_mask]
                            
                            if len(nearby_responses) > 1:
                                local_var = np.var(nearby_responses)
                                uncertainty_map[j, i] = local_var
                            else:
                                uncertainty_map[j, i] = np.min(distances) ** 2
                        else:
                            uncertainty_map[j, i] = np.min(distances) ** 2

                    elif uncertainty_metric == "coefficient_of_variation":
                        # Coefficient of variation of nearby response values
                        nearby_threshold = (
                            min(
                                x1_bounds[1] - x1_bounds[0], x2_bounds[1] - x2_bounds[0]
                            )
                            / 5
                        )
                        nearby_mask = distances < nearby_threshold

                        if np.sum(nearby_mask) > 1 and response_name and response_name in exp_data.columns:
                            # Get response values for nearby points for specific response
                            nearby_responses = exp_data[response_name].values[nearby_mask]
                            
                            if len(nearby_responses) > 1:
                                mean_response = np.mean(nearby_responses)
                                std_response = np.std(nearby_responses)
                                if abs(mean_response) > 1e-10:  # Avoid division by zero
                                    cv = std_response / abs(mean_response)
                                    uncertainty_map[j, i] = cv
                                else:
                                    uncertainty_map[j, i] = 0.0
                            else:
                                uncertainty_map[j, i] = np.min(distances) / max(
                                    x1_bounds[1] - x1_bounds[0], x2_bounds[1] - x2_bounds[0]
                                )
                        else:
                            uncertainty_map[j, i] = np.min(distances) / max(
                                x1_bounds[1] - x1_bounds[0], x2_bounds[1] - x2_bounds[0]
                            )

                    else:  # Default: data_density
                        kernel_width = (x1_bounds[1] - x1_bounds[0]) / 10
                        weights = np.exp(-(distances**2) / (2 * kernel_width**2))
                        density = np.sum(weights)
                        uncertainty_map[j, i] = 1.0 / (1.0 + density)

            return uncertainty_map

        except Exception as e:
            logger.error(f"Failed to get statistical uncertainty with params: {e}")
            return np.zeros((resolution, resolution))

    def _create_simple_statistical_plot(
        self,
        ax,
        response_name,
        param1_name,
        param2_name,
        uncertainty_metric,
        colormap,
        resolution,
    ):
        """Create a simple statistical deviation plot as fallback"""
        try:
            # Get experimental data
            exp_data = self.optimizer.experimental_data
            if exp_data.empty or response_name not in exp_data.columns:
                self._plot_message_on_axis(
                    ax, f"No experimental data for {response_name}"
                )
                return

            # Simple data statistics
            response_data = (
                exp_data[response_name]
                .apply(lambda x: np.mean(x) if isinstance(x, list) and x else x)
                .dropna()
            )

            if len(response_data) < 2:
                self._plot_message_on_axis(
                    ax, "Insufficient data for statistical analysis"
                )
                return

            # Calculate statistical measure
            if uncertainty_metric == "std":
                stat_value = response_data.std()
                stat_name = "Standard Deviation"
            elif uncertainty_metric == "variance":
                stat_value = response_data.var()
                stat_name = "Variance"
            else:
                stat_value = (
                    response_data.std() / response_data.mean()
                    if response_data.mean() != 0
                    else 0
                )
                stat_name = "Coefficient of Variation"

            # Create simple visualization
            ax.text(
                0.5,
                0.5,
                f"{stat_name}\\n{stat_value:.4f}\\n\\nData Points: {len(response_data)}",
                ha="center",
                va="center",
                transform=ax.transAxes,
                bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8),
                fontsize=12,
                fontweight="bold",
            )
            ax.set_title(
                f"Statistical Summary: {response_name}", fontsize=12, fontweight="bold"
            )
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])

        except Exception as e:
            logger.error(f"Error creating simple statistical plot: {e}")
            self._plot_message_on_axis(ax, f"Statistical plot error: {str(e)}")

    def _create_uncertainty_visualization(
        self,
        ax,
        X1,
        X2,
        uncertainty_grid,
        title,
        param1_name,
        param2_name,
        plot_style,
        colormap,
        colorbar_label,
        show_experimental_data,
    ):
        """Create uncertainty visualization on given axis"""
        try:
            # Choose colormap
            cmap = plt.cm.get_cmap(colormap)

            # Create the visualization based on plot style
            if plot_style == "heatmap":
                im = ax.contourf(
                    X1, X2, uncertainty_grid, levels=20, cmap=cmap, alpha=0.8
                )
            elif plot_style == "contour":
                im = ax.contour(
                    X1, X2, uncertainty_grid, levels=15, cmap=cmap, linewidths=1.5
                )
            elif plot_style == "filled_contour":
                im = ax.contourf(
                    X1, X2, uncertainty_grid, levels=15, cmap=cmap, alpha=0.7
                )
            else:  # combined
                im = ax.contourf(
                    X1, X2, uncertainty_grid, levels=15, cmap=cmap, alpha=0.6
                )
                ax.contour(
                    X1,
                    X2,
                    uncertainty_grid,
                    levels=15,
                    colors="black",
                    linewidths=0.5,
                    alpha=0.8,
                )

            # Add colorbar
            if hasattr(im, "collections") or hasattr(im, "get_array"):
                try:
                    cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
                    cbar.set_label(colorbar_label, fontsize=10, fontweight="bold")
                    cbar.ax.tick_params(labelsize=9)
                except Exception as e:
                    logger.debug(f"Could not add colorbar: {e}")

            # Set labels and title
            ax.set_xlabel(param1_name, fontsize=11, fontweight="bold")
            ax.set_ylabel(param2_name, fontsize=11, fontweight="bold")
            ax.set_title(title, fontsize=12, fontweight="bold")
            ax.grid(True, alpha=0.3)

            # Add experimental data overlay if requested
            if show_experimental_data:
                self._add_experimental_data_overlay(ax, param1_name, param2_name)

        except Exception as e:
            logger.error(f"Error creating uncertainty visualization: {e}")
            self._plot_message_on_axis(ax, f"Visualization error: {str(e)}")

    def _add_experimental_data_overlay(self, ax, param1_name, param2_name):
        """Add experimental data points as overlay"""
        try:
            exp_data = self.optimizer.experimental_data
            if exp_data.empty:
                return

            # Check if required columns exist
            if (
                param1_name not in exp_data.columns
                or param2_name not in exp_data.columns
            ):
                return

            # Extract parameter values
            p1_vals = exp_data[param1_name].values
            p2_vals = exp_data[param2_name].values

            # Filter valid data points
            valid_mask = pd.Series(p1_vals).notna() & pd.Series(p2_vals).notna()

            if not valid_mask.any():
                return

            # Plot experimental points
            ax.scatter(
                p1_vals[valid_mask],
                p2_vals[valid_mask],
                c="white",
                s=60,
                alpha=0.9,
                edgecolors="black",
                linewidth=1.5,
                marker="o",
                label="Experimental Data",
                zorder=10,
            )

        except Exception as e:
            logger.debug(f"Could not add experimental data overlay: {e}")

    def _plot_message_on_axis(self, ax, message):
        """Plot a message on a specific axis"""
        ax.clear()
        ax.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            transform=ax.transAxes,
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8),
            fontsize=11,
            fontweight="bold",
        )
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])

    def create_parity_plot(self, fig, canvas, response_name):
        """Create parity plot (predicted vs actual) - wrapper for model analysis"""
        self.create_model_analysis_plot(fig, canvas, response_name, "predictions")

    def create_residuals_plot(self, fig, canvas, response_name):
        """Create residuals plot - wrapper for model analysis"""
        self.create_model_analysis_plot(fig, canvas, response_name, "residuals")
