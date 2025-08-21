"""
Goal Impact Dashboard Module

This module provides a comprehensive dashboard for monitoring and analyzing how different
goal types (Maximize, Minimize, Target, Range) affect optimization outcomes in PyMBO.
The dashboard displays in a separate floating window with real-time goal contribution
analysis, hypervolume tracking, and objective trade-off visualization.

Key Features:
- Real-time goal contribution tracking
- Hypervolume impact analysis
- Target achievement monitoring
- Objective trade-off visualization
- Goal weight sensitivity analysis
- Performance metrics display
- Consistent GUI design with PyMBO

Classes:
    GoalImpactDashboard: Main dashboard class for goal impact analysis
    
Functions:
    create_goal_impact_dashboard: Factory function for dashboard instantiation

Author: PyMBO Development Team
Version: 3.6.6 Enhanced (Goal Impact Analysis)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import pandas as pd
from typing import Dict, Any, Callable, List, Optional, Tuple
import logging
from datetime import datetime
import threading
import time

# Import color constants from main GUI module
try:
    from .gui import (
        COLOR_PRIMARY, COLOR_SECONDARY, COLOR_SUCCESS, COLOR_WARNING, 
        COLOR_ERROR, COLOR_BACKGROUND, COLOR_SURFACE
    )
except ImportError:
    # Fallback color scheme if import fails
    COLOR_PRIMARY = "#1976D2"
    COLOR_SECONDARY = "#424242"
    COLOR_SUCCESS = "#4CAF50"
    COLOR_WARNING = "#FF9800"
    COLOR_ERROR = "#F44336"
    COLOR_BACKGROUND = "#FAFAFA"
    COLOR_SURFACE = "#FFFFFF"

logger = logging.getLogger(__name__)


class GoalImpactDashboard:
    """
    Comprehensive dashboard for analyzing goal impact in multi-objective optimization.
    
    This class provides real-time monitoring and analysis of how different goal types
    (Maximize, Minimize, Target, Range) affect optimization outcomes, including
    hypervolume contribution, objective trade-offs, and target achievement tracking.
    
    Attributes:
        parent: Parent Tkinter widget
        optimizer: PyMBO optimizer instance
        update_callback: Callback function for dashboard updates
        popup_window: Separate Toplevel window for the dashboard
        dashboard_data: Dictionary storing analysis data
        goal_contributions: Track individual goal contributions
        hypervolume_history: Track hypervolume evolution
        target_achievement: Track target goal achievement over time
    """
    
    def __init__(self, parent, optimizer=None, update_callback: Callable = None):
        """
        Initialize the Goal Impact Dashboard.
        
        Args:
            parent: Parent Tkinter widget
            optimizer: PyMBO optimizer instance
            update_callback: Optional callback for external updates
        """
        print("🔥 GOAL IMPACT DASHBOARD INITIALIZATION 🔥")
        print(f"🔥 Initializing dashboard with optimizer: {optimizer}")
        logger.debug("=== GOAL IMPACT DASHBOARD INITIALIZATION ===")
        logger.debug(f"Initializing dashboard with optimizer: {optimizer}")
        
        self.parent = parent
        self.optimizer = optimizer
        self.update_callback = update_callback
        self.popup_window = None
        
        # Debug optimizer reference at initialization
        if self.optimizer:
            print(f"🔥 Dashboard received optimizer: {type(self.optimizer)}")
            logger.debug(f"Dashboard received optimizer: {type(self.optimizer)}")
            if hasattr(self.optimizer, 'params_config'):
                print(f"🔥 Dashboard optimizer.params_config: {self.optimizer.params_config}")
                logger.debug(f"Dashboard optimizer.params_config: {self.optimizer.params_config}")
            if hasattr(self.optimizer, 'responses_config'):
                print(f"🔥 Dashboard optimizer.responses_config: {self.optimizer.responses_config}")
                logger.debug(f"Dashboard optimizer.responses_config: {self.optimizer.responses_config}")
        else:
            print("🔥 Dashboard initialized with NO optimizer")
            logger.debug("Dashboard initialized with NO optimizer")
        
        # Dashboard data storage
        self.dashboard_data = {
            'goal_contributions': {},
            'hypervolume_history': [],
            'target_achievements': {},
            'objective_evolution': {},
            'trade_off_analysis': {},
            'performance_metrics': {}
        }
        
        # Analysis settings
        self.auto_refresh = tk.BooleanVar(value=True)
        self.refresh_interval = tk.IntVar(value=5)  # seconds
        self.show_normalized = tk.BooleanVar(value=False)
        
        logger.info("Goal Impact Dashboard initialized")
    
    def create_dashboard(self):
        """Create and display the Goal Impact Dashboard window"""
        if self.popup_window is not None:
            self.show()
            return
            
        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.title("📊 Goal Impact Dashboard - PyMBO")
        self.popup_window.geometry("1200x800")
        self.popup_window.configure(bg=COLOR_BACKGROUND)
        
        # Set window icon and properties
        try:
            self.popup_window.iconbitmap(default='')
        except:
            pass
            
        self.popup_window.minsize(800, 600)
        
        # Set up window close protocol
        self.popup_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Create main layout
        self._create_header()
        self._create_main_content()
        self._create_status_bar()
        
        # Start auto-refresh if enabled
        if self.auto_refresh.get():
            self._start_auto_refresh()
        
        logger.info("Goal Impact Dashboard window created")
    
    def _on_window_close(self):
        """Handle window close event"""
        print("🔥 Dashboard window closing")
        self.close()
    
    def _create_header(self):
        """Create the dashboard header with controls"""
        header_frame = tk.Frame(self.popup_window, bg=COLOR_PRIMARY, height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="📊 Goal Impact Dashboard",
            font=("Arial", 16, "bold"),
            bg=COLOR_PRIMARY,
            fg=COLOR_SURFACE
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Control buttons frame
        controls_frame = tk.Frame(header_frame, bg=COLOR_PRIMARY)
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Refresh button
        refresh_btn = tk.Button(
            controls_frame,
            text="🔄 Refresh",
            command=self.refresh_dashboard,
            bg=COLOR_SURFACE,
            fg=COLOR_PRIMARY,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=15,
            pady=5
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Auto-refresh checkbox
        auto_refresh_cb = tk.Checkbutton(
            controls_frame,
            text="Auto-refresh",
            variable=self.auto_refresh,
            command=self._toggle_auto_refresh,
            bg=COLOR_PRIMARY,
            fg=COLOR_SURFACE,
            selectcolor=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY,
            activeforeground=COLOR_SURFACE,
            font=("Arial", 9)
        )
        auto_refresh_cb.pack(side=tk.LEFT, padx=10)
        
        # Export button
        export_btn = tk.Button(
            controls_frame,
            text="📁 Export",
            command=self.export_dashboard,
            bg=COLOR_SUCCESS,
            fg=COLOR_SURFACE,
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=15,
            pady=5
        )
        export_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_main_content(self):
        """Create the main content area with analysis panels"""
        # Create notebook for different analysis views
        self.notebook = ttk.Notebook(self.popup_window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Goal Contributions Tab
        self._create_goal_contributions_tab()
        
        # Target Achievement Tab
        self._create_target_achievement_tab()
        
        # Trade-off Analysis Tab
        self._create_tradeoff_analysis_tab()
        
        # Performance Metrics Tab
        self._create_performance_metrics_tab()
    
    def _create_goal_contributions_tab(self):
        """Create the Goal Contributions analysis tab"""
        contributions_frame = tk.Frame(self.notebook, bg=COLOR_SURFACE)
        self.notebook.add(contributions_frame, text="🎯 Goal Contributions")
        
        # Split into left controls and right visualization
        left_frame = tk.Frame(contributions_frame, bg=COLOR_SURFACE, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        right_frame = tk.Frame(contributions_frame, bg=COLOR_SURFACE)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left controls
        controls_label = tk.Label(
            left_frame,
            text="Analysis Controls",
            font=("Arial", 12, "bold"),
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY
        )
        controls_label.pack(anchor="w", pady=(0, 10))
        
        # Goal type filter
        goal_filter_frame = tk.LabelFrame(
            left_frame,
            text="Goal Types",
            font=("Arial", 10, "bold"),
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY
        )
        goal_filter_frame.pack(fill=tk.X, pady=5)
        
        self.show_maximize = tk.BooleanVar(value=True)
        self.show_minimize = tk.BooleanVar(value=True)
        self.show_target = tk.BooleanVar(value=True)
        self.show_range = tk.BooleanVar(value=True)
        
        for var, text in [(self.show_maximize, "Maximize"),
                         (self.show_minimize, "Minimize"),
                         (self.show_target, "Target"),
                         (self.show_range, "Range")]:
            cb = tk.Checkbutton(
                goal_filter_frame,
                text=text,
                variable=var,
                command=self._update_goal_contributions,
                bg=COLOR_SURFACE,
                fg=COLOR_SECONDARY
            )
            cb.pack(anchor="w", padx=5, pady=2)
        
        # Normalization option
        norm_cb = tk.Checkbutton(
            left_frame,
            text="Show Normalized Values",
            variable=self.show_normalized,
            command=self._update_goal_contributions,
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10)
        )
        norm_cb.pack(anchor="w", pady=10)
        
        # Goal statistics
        stats_frame = tk.LabelFrame(
            left_frame,
            text="Goal Statistics",
            font=("Arial", 10, "bold"),
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY
        )
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.goal_stats_text = tk.Text(
            stats_frame,
            height=8,
            width=30,
            font=("Courier", 9),
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            wrap=tk.WORD
        )
        self.goal_stats_text.pack(padx=5, pady=5)
        
        # Right visualization
        viz_label = tk.Label(
            right_frame,
            text="Goal Contribution Analysis",
            font=("Arial", 12, "bold"),
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY
        )
        viz_label.pack(anchor="w", pady=(0, 10))
        
        # Create matplotlib figure for goal contributions
        self.contrib_fig = Figure(figsize=(8, 6), facecolor=COLOR_SURFACE)
        self.contrib_canvas = FigureCanvasTkAgg(self.contrib_fig, right_frame)
        self.contrib_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        contrib_toolbar = NavigationToolbar2Tk(self.contrib_canvas, right_frame)
        contrib_toolbar.update()
    
    def _create_target_achievement_tab(self):
        """Create the Target Achievement monitoring tab"""
        target_frame = tk.Frame(self.notebook, bg=COLOR_SURFACE)
        self.notebook.add(target_frame, text="🎯 Target Achievement")
        
        # Split into controls and visualization
        control_frame = tk.Frame(target_frame, bg=COLOR_SURFACE, height=100)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        control_frame.pack_propagate(False)
        
        viz_frame = tk.Frame(target_frame, bg=COLOR_SURFACE)
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controls
        controls_label = tk.Label(
            control_frame,
            text="Target Achievement Monitoring",
            font=("Arial", 12, "bold"),
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY
        )
        controls_label.pack(anchor="w")
        
        # Target parameter selection
        target_control_frame = tk.Frame(control_frame, bg=COLOR_SURFACE)
        target_control_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            target_control_frame,
            text="Target Parameter:",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10)
        ).pack(side=tk.LEFT)
        
        self.target_param_var = tk.StringVar()
        self.target_param_combo = ttk.Combobox(
            target_control_frame,
            textvariable=self.target_param_var,
            state="readonly",
            width=20
        )
        self.target_param_combo.pack(side=tk.LEFT, padx=10)
        self.target_param_combo.bind('<<ComboboxSelected>>', self._update_target_achievement)
        
        # Tolerance setting
        tk.Label(
            target_control_frame,
            text="Tolerance (%):",
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.tolerance_var = tk.StringVar(value="5")
        tolerance_entry = tk.Entry(
            target_control_frame,
            textvariable=self.tolerance_var,
            width=8
        )
        tolerance_entry.pack(side=tk.LEFT)
        tolerance_entry.bind('<Return>', self._update_target_achievement)
        
        # Visualization
        self.target_fig = Figure(figsize=(10, 6), facecolor=COLOR_SURFACE)
        self.target_canvas = FigureCanvasTkAgg(self.target_fig, viz_frame)
        self.target_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        target_toolbar = NavigationToolbar2Tk(self.target_canvas, viz_frame)
        target_toolbar.update()
    
    def _create_tradeoff_analysis_tab(self):
        """Create the Trade-off Analysis tab"""
        tradeoff_frame = tk.Frame(self.notebook, bg=COLOR_SURFACE)
        self.notebook.add(tradeoff_frame, text="⚖️ Trade-off Analysis")
        
        # Create trade-off visualization
        tradeoff_label = tk.Label(
            tradeoff_frame,
            text="Objective Trade-off Analysis",
            font=("Arial", 12, "bold"),
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY
        )
        tradeoff_label.pack(anchor="w", padx=10, pady=10)
        
        self.tradeoff_fig = Figure(figsize=(10, 8), facecolor=COLOR_SURFACE)
        self.tradeoff_canvas = FigureCanvasTkAgg(self.tradeoff_fig, tradeoff_frame)
        self.tradeoff_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tradeoff_toolbar = NavigationToolbar2Tk(self.tradeoff_canvas, tradeoff_frame)
        tradeoff_toolbar.update()
    
    def _create_performance_metrics_tab(self):
        """Create the Performance Metrics tab"""
        metrics_frame = tk.Frame(self.notebook, bg=COLOR_SURFACE)
        self.notebook.add(metrics_frame, text="📊 Performance Metrics")
        
        # Create metrics display
        metrics_label = tk.Label(
            metrics_frame,
            text="Goal Performance Metrics",
            font=("Arial", 12, "bold"),
            bg=COLOR_SURFACE,
            fg=COLOR_SECONDARY
        )
        metrics_label.pack(anchor="w", padx=10, pady=10)
        
        # Metrics table
        metrics_table_frame = tk.Frame(metrics_frame, bg=COLOR_SURFACE)
        metrics_table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for metrics
        columns = ("Goal", "Type", "Current Value", "Best Value", "Achievement %", "Contribution")
        self.metrics_tree = ttk.Treeview(metrics_table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.metrics_tree.heading(col, text=col)
            self.metrics_tree.column(col, width=150)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(metrics_table_frame, orient=tk.VERTICAL, command=self.metrics_tree.yview)
        h_scrollbar = ttk.Scrollbar(metrics_table_frame, orient=tk.HORIZONTAL, command=self.metrics_tree.xview)
        self.metrics_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.metrics_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_status_bar(self):
        """Create the status bar at the bottom"""
        self.status_frame = tk.Frame(self.popup_window, bg=COLOR_SECONDARY, height=30)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready - Dashboard initialized",
            bg=COLOR_SECONDARY,
            fg=COLOR_SURFACE,
            font=("Arial", 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Last update time
        self.last_update_label = tk.Label(
            self.status_frame,
            text="Last update: Never",
            bg=COLOR_SECONDARY,
            fg=COLOR_SURFACE,
            font=("Arial", 9)
        )
        self.last_update_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def refresh_dashboard(self):
        """Refresh all dashboard data and visualizations"""
        try:
            print("🔥 DASHBOARD REFRESH STARTING 🔥")
            logger.debug("=== DASHBOARD REFRESH STARTING ===")
            logger.debug(f"Dashboard.optimizer: {self.optimizer}")
            self.status_label.config(text="Refreshing dashboard data...")
            
            if self.optimizer is None:
                logger.debug("❌ No optimizer connected to dashboard")
                self.status_label.config(text="No optimizer connected")
                return
            
            # Debug current optimizer state
            logger.debug(f"✓ Optimizer connected: {type(self.optimizer)}")
            if hasattr(self.optimizer, 'params_config'):
                logger.debug(f"✓ Optimizer has params_config: {len(self.optimizer.params_config)} parameters")
                for name, config in self.optimizer.params_config.items():
                    logger.debug(f"    Parameter '{name}': goal='{config.get('goal', 'MISSING')}'")
            else:
                logger.debug("❌ Optimizer missing params_config")
                
            if hasattr(self.optimizer, 'responses_config'):
                logger.debug(f"✓ Optimizer has responses_config: {len(self.optimizer.responses_config)} responses")
                for name, config in self.optimizer.responses_config.items():
                    logger.debug(f"    Response '{name}': goal='{config.get('goal', 'MISSING')}'")
            else:
                logger.debug("❌ Optimizer missing responses_config")
            
            # Update dashboard data
            logger.debug("Updating dashboard data...")
            self._update_dashboard_data()
            
            # Update all visualizations
            logger.debug("Updating goal contributions...")
            self._update_goal_contributions()
            logger.debug("Updating target achievement...")
            self._update_target_achievement()
            logger.debug("Updating tradeoff analysis...")
            self._update_tradeoff_analysis()
            logger.debug("Updating performance metrics...")
            self._update_performance_metrics()
            
            # Update status
            current_time = datetime.now().strftime("%H:%M:%S")
            self.status_label.config(text="Dashboard refreshed successfully")
            self.last_update_label.config(text=f"Last update: {current_time}")
            
        except Exception as e:
            error_msg = f"Error refreshing dashboard: {str(e)}"
            self.status_label.config(text=error_msg)
            logger.error(error_msg)
    
    def _update_dashboard_data(self):
        """Update the dashboard data from the optimizer"""
        logger.debug("=== UPDATING DASHBOARD DATA ===")
        if not self.optimizer:
            logger.debug("❌ No optimizer available for data update")
            return
        
        logger.debug(f"✓ Updating data from optimizer: {type(self.optimizer)}")
        
        try:
            # Extract goal information
            logger.debug("📊 Starting goal data extraction...")
            goals_data = self._extract_goals_data()
            logger.debug(f"📊 Goals data extraction result: {len(goals_data.get('parameters', {}))} params, {len(goals_data.get('responses', {}))} responses")
            
            # Calculate goal contributions
            self.dashboard_data['goal_contributions'] = self._calculate_goal_contributions(goals_data)
            
            # Update target achievements
            self.dashboard_data['target_achievements'] = self._calculate_target_achievements(goals_data)
            
            # Update performance metrics
            self.dashboard_data['performance_metrics'] = self._calculate_performance_metrics(goals_data)
            
        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
    
    def _extract_goals_data(self):
        """Extract goal data from optimizer configuration"""
        print("🔥 _EXTRACT_GOALS_DATA CALLED 🔥")
        goals_data = {
            'parameters': {},
            'responses': {},
            'objectives': []
        }
        
        # Extract parameter goals
        if hasattr(self.optimizer, 'params_config'):
            print(f"🔥 Found params_config with keys: {list(self.optimizer.params_config.keys())}")
            logger.debug(f"Found params_config with keys: {list(self.optimizer.params_config.keys())}")
            for name, config in self.optimizer.params_config.items():
                goal = config.get('goal', 'None')
                print(f"🔥 Parameter {name}: goal='{goal}' (type: {type(goal)})")
                logger.debug(f"Parameter {name}: goal='{goal}' (type: {type(goal)}), config={config}")
                
                # Clean up goal value (strip whitespace, handle case variations)
                if isinstance(goal, str):
                    goal = goal.strip()
                
                # Validate goal value
                valid_goals = ['Maximize', 'Minimize', 'Target', 'None']
                if goal not in valid_goals:
                    logger.warning(f"  Invalid goal '{goal}' for parameter {name}, treating as 'None'")
                    goal = 'None'
                
                logger.debug(f"  After validation - Parameter {name}: goal='{goal}'")
                
                # Include parameters with explicit optimization goals
                if goal in ['Maximize', 'Minimize', 'Target']:
                    goals_data['parameters'][name] = {
                        'goal': goal,
                        'config': config,
                        'current_values': []
                    }
                    print(f"🔥 ✅ ADDED parameter {name} with goal {goal}")
                    logger.debug(f"  ✓ ADDED parameter {name} with goal {goal}")
                else:
                    print(f"🔥 ❌ SKIPPED parameter {name} - goal is '{goal}' (not an optimization goal)")
                    logger.debug(f"  ✗ SKIPPED parameter {name} - goal is '{goal}' (not an optimization goal)")
        
        # Extract response goals
        if hasattr(self.optimizer, 'responses_config'):
            logger.debug(f"Found responses_config with keys: {list(self.optimizer.responses_config.keys())}")
            for name, config in self.optimizer.responses_config.items():
                logger.debug(f"Response {name}: config={config}")
                goal = config.get('goal', 'None')
                logger.debug(f"  Goal: {goal}")
                
                # Clean up goal value (strip whitespace, handle case variations)
                if isinstance(goal, str):
                    goal = goal.strip()
                
                # Validate goal value
                valid_goals = ['Maximize', 'Minimize', 'Target', 'Range', 'None']
                if goal not in valid_goals:
                    logger.warning(f"  Invalid goal '{goal}' for response {name}, treating as 'None'")
                    goal = 'None'
                
                # Include responses with explicit optimization goals
                if goal in ['Maximize', 'Minimize', 'Target', 'Range']:
                    goals_data['responses'][name] = {
                        'goal': goal,
                        'config': config,
                        'current_values': []
                    }
                    logger.debug(f"  ✓ ADDED response {name} with goal {goal}")
                else:
                    logger.debug(f"  ✗ SKIPPED response {name} - goal is '{goal}' (not an optimization goal)")
        
        # Extract objective names and directions
        if hasattr(self.optimizer, 'objective_names'):
            goals_data['objectives'] = list(zip(
                self.optimizer.objective_names,
                getattr(self.optimizer, 'objective_directions', [])
            ))
        
        # Extract current experimental data
        if hasattr(self.optimizer, 'experimental_data') and not self.optimizer.experimental_data.empty:
            data = self.optimizer.experimental_data
            
            # Get current values for parameters
            for name in goals_data['parameters']:
                if name in data.columns:
                    goals_data['parameters'][name]['current_values'] = data[name].tolist()
            
            # Get current values for responses
            for name in goals_data['responses']:
                if name in data.columns:
                    goals_data['responses'][name]['current_values'] = data[name].tolist()
        
        # Debug summary
        param_count = len(goals_data['parameters'])
        response_count = len(goals_data['responses'])
        logger.debug(f"=== GOALS DATA EXTRACTION SUMMARY ===")
        logger.debug(f"Goals data extracted: {param_count} parameters, {response_count} responses")
        logger.debug(f"Parameter goals: {list(goals_data['parameters'].keys())}")
        logger.debug(f"Response goals: {list(goals_data['responses'].keys())}")
        
        # Log detailed goal types for debugging
        for name, param_data in goals_data['parameters'].items():
            logger.debug(f"  Parameter '{name}': goal='{param_data['goal']}'")
        for name, response_data in goals_data['responses'].items():
            logger.debug(f"  Response '{name}': goal='{response_data['goal']}'")
        logger.debug(f"=== END SUMMARY ===")
        
        return goals_data
    
    def _calculate_goal_contributions(self, goals_data):
        """Calculate individual goal contributions to optimization"""
        contributions = {}
        
        logger.debug(f"Calculating contributions for {len(goals_data['parameters'])} parameters and {len(goals_data['responses'])} responses")
        
        # Calculate contributions based on goal type
        for category in ['parameters', 'responses']:
            logger.debug(f"Processing {category}: {list(goals_data[category].keys())}")
            for name, goal_info in goals_data[category].items():
                goal_type = goal_info['goal']
                values = goal_info['current_values']
                
                logger.debug(f"  {category} {name}: goal_type={goal_type}, values count={len(values)}")
                
                if not values:
                    logger.debug(f"  Skipping {name} - no values")
                    continue
                
                contribution = {
                    'type': goal_type,
                    'category': category,
                    'raw_contribution': 0.0,
                    'normalized_contribution': 0.0,
                    'improvement_trend': 0.0
                }
                
                if goal_type == 'Maximize':
                    contribution['raw_contribution'] = np.mean(values) if values else 0
                    contribution['improvement_trend'] = self._calculate_trend(values)
                elif goal_type == 'Minimize':
                    contribution['raw_contribution'] = -np.mean(values) if values else 0
                    contribution['improvement_trend'] = -self._calculate_trend(values)
                elif goal_type == 'Target':
                    # Handle both 'target_value' (new format) and 'ideal' (old format)
                    target_value = goal_info['config'].get('target_value') or goal_info['config'].get('ideal', 0)
                    deviations = [abs(v - target_value) for v in values]
                    contribution['raw_contribution'] = -np.mean(deviations) if deviations else 0
                    contribution['improvement_trend'] = -self._calculate_trend(deviations)
                elif goal_type == 'Range':
                    # Try different possible ways PyMBO stores ranges
                    config = goal_info['config']
                    min_val = None
                    max_val = None
                    
                    if 'min_value' in config and 'max_value' in config:
                        min_val = config['min_value']
                        max_val = config['max_value']
                    elif 'bounds' in config and len(config['bounds']) == 2:
                        min_val, max_val = config['bounds']
                    elif values:  # Fallback to data range
                        min_val = min(values)
                        max_val = max(values)
                    else:
                        min_val, max_val = 0, 1  # Default fallback
                    
                    logger.debug(f"Range for {name}: [{min_val}, {max_val}]")
                    
                    # Calculate how well values stay within range (negative penalty for violations)
                    violations = []
                    for v in values:
                        if v < min_val:
                            violations.append(min_val - v)
                        elif v > max_val:
                            violations.append(v - max_val)
                        else:
                            violations.append(0)
                    contribution['raw_contribution'] = -np.mean(violations) if violations else 0
                    contribution['improvement_trend'] = -self._calculate_trend(violations)
                    logger.debug(f"Range contribution for {name}: {contribution['raw_contribution']}")
                
                contributions[name] = contribution
        
        # Normalize contributions
        total_abs_contribution = sum(abs(c['raw_contribution']) for c in contributions.values())
        if total_abs_contribution > 0:
            for contrib in contributions.values():
                contrib['normalized_contribution'] = contrib['raw_contribution'] / total_abs_contribution
        
        return contributions
    
    def _calculate_trend(self, values):
        """Calculate improvement trend for a series of values"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend calculation
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        return coeffs[0]  # slope
    
    def _calculate_target_achievements(self, goals_data):
        """Calculate target achievement metrics"""
        achievements = {}
        
        for category in ['parameters', 'responses']:
            for name, goal_info in goals_data[category].items():
                if goal_info['goal'] == 'Target':
                    # Handle both 'target_value' (new format) and 'ideal' (old format)
                    target_value = goal_info['config'].get('target_value') or goal_info['config'].get('ideal')
                    values = goal_info['current_values']
                    
                    if target_value is not None and values:
                        # Calculate achievement percentage
                        latest_value = values[-1]
                        deviation = abs(latest_value - target_value)
                        tolerance = abs(target_value * 0.05)  # 5% default tolerance
                        
                        if tolerance > 0:
                            achievement_pct = max(0, (tolerance - deviation) / tolerance * 100)
                        else:
                            achievement_pct = 100 if deviation == 0 else 0
                        
                        achievements[name] = {
                            'target_value': target_value,
                            'current_value': latest_value,
                            'deviation': deviation,
                            'achievement_pct': achievement_pct,
                            'history': [abs(v - target_value) for v in values]
                        }
        
        return achievements
    
    def _calculate_performance_metrics(self, goals_data):
        """Calculate comprehensive performance metrics"""
        metrics = {}
        
        logger.debug("=== CALCULATING PERFORMANCE METRICS ===")
        logger.debug(f"Input goals_data: parameters={len(goals_data['parameters'])}, responses={len(goals_data['responses'])}")
        logger.debug(f"Parameters in goals_data: {list(goals_data['parameters'].keys())}")
        logger.debug(f"Responses in goals_data: {list(goals_data['responses'].keys())}")
        
        for category in ['parameters', 'responses']:
            logger.debug(f"Processing {category}: {list(goals_data[category].keys())}")
            for name, goal_info in goals_data[category].items():
                goal_type = goal_info['goal']
                values = goal_info['current_values']
                
                logger.debug(f"  {category} {name}: goal_type={goal_type}, values count={len(values)}")
                
                if not values:
                    logger.debug(f"  Skipping {name} - no values")
                    continue
                
                # Validate goal type to prevent display issues
                valid_goal_types = ['Maximize', 'Minimize', 'Target', 'Range', 'None']
                if goal_type not in valid_goal_types:
                    logger.warning(f"  Invalid goal type '{goal_type}' for {name}, defaulting to 'None'")
                    goal_type = 'None'
                
                metric = {
                    'goal_type': goal_type,
                    'category': category,
                    'current_value': values[-1] if values else 0,
                    'best_value': 0,
                    'achievement_pct': 0,
                    'contribution_score': 0
                }
                
                if goal_type == 'Maximize':
                    metric['best_value'] = max(values)
                    metric['achievement_pct'] = (values[-1] / max(values)) * 100 if max(values) > 0 else 0
                elif goal_type == 'Minimize':
                    metric['best_value'] = min(values)
                    metric['achievement_pct'] = (min(values) / values[-1]) * 100 if values[-1] > 0 else 0
                elif goal_type == 'Target':
                    # Handle both 'target_value' (new format) and 'ideal' (old format)
                    target = goal_info['config'].get('target_value') or goal_info['config'].get('ideal', 0)
                    metric['best_value'] = target
                    deviation = abs(values[-1] - target)
                    tolerance = abs(target * 0.05)
                    metric['achievement_pct'] = max(0, (tolerance - deviation) / tolerance * 100) if tolerance > 0 else 0
                elif goal_type == 'Range':
                    min_val = goal_info['config'].get('min_value', min(values) if values else 0)
                    max_val = goal_info['config'].get('max_value', max(values) if values else 0)
                    metric['best_value'] = f"[{min_val:.2f}, {max_val:.2f}]"
                    current_val = values[-1]
                    if min_val <= current_val <= max_val:
                        metric['achievement_pct'] = 100  # Within range
                    else:
                        # Calculate how close to range
                        if current_val < min_val:
                            distance = min_val - current_val
                            range_size = max_val - min_val
                        else:
                            distance = current_val - max_val
                            range_size = max_val - min_val
                        metric['achievement_pct'] = max(0, 100 - (distance / range_size * 100)) if range_size > 0 else 0
                
                metrics[name] = metric
                logger.debug(f"  Added metric for {name}: {metric}")
        
        logger.debug(f"Performance metrics calculation complete: {len(metrics)} total metrics")
        logger.debug(f"Final metrics keys: {list(metrics.keys())}")
        return metrics
    
    def _update_goal_contributions(self, event=None):
        """Update the goal contributions visualization"""
        try:
            logger.debug("Starting goal contributions update")
            self.contrib_fig.clear()
            
            contributions_data = self.dashboard_data['goal_contributions']
            logger.debug(f"Total contributions available: {len(contributions_data)}")
            logger.debug(f"Contribution keys: {list(contributions_data.keys())}")
            
            if not contributions_data:
                ax = self.contrib_fig.add_subplot(111)
                ax.text(0.5, 0.5, 'No goal contribution data available', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color=COLOR_SECONDARY)
                self.contrib_canvas.draw()
                return
            
            # Debug checkbox states
            logger.debug(f"Checkbox states: Maximize={self.show_maximize.get()}, Minimize={self.show_minimize.get()}, Target={self.show_target.get()}, Range={self.show_range.get()}")
            
            # Filter goals based on checkboxes
            filtered_contribs = {}
            for name, contrib in contributions_data.items():
                goal_type = contrib['type']
                logger.debug(f"Processing {name}: type={goal_type}, category={contrib.get('category', 'unknown')}")
                if ((goal_type == 'Maximize' and self.show_maximize.get()) or
                    (goal_type == 'Minimize' and self.show_minimize.get()) or
                    (goal_type == 'Target' and self.show_target.get()) or
                    (goal_type == 'Range' and self.show_range.get())):
                    filtered_contribs[name] = contrib
                    logger.debug(f"  INCLUDED: {name} ({goal_type})")
                else:
                    logger.debug(f"  FILTERED OUT: {name} ({goal_type})")
            
            logger.debug(f"Filtered contributions: {len(filtered_contribs)} items")
            logger.debug(f"Filtered keys: {list(filtered_contribs.keys())}")
            
            if not filtered_contribs:
                ax = self.contrib_fig.add_subplot(111)
                ax.text(0.5, 0.5, 'No goals selected for display', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color=COLOR_SECONDARY)
                self.contrib_canvas.draw()
                return
            
            # Create subplots
            ax1 = self.contrib_fig.add_subplot(211)
            ax2 = self.contrib_fig.add_subplot(212)
            
            # Prepare data
            names = list(filtered_contribs.keys())
            values_key = 'normalized_contribution' if self.show_normalized.get() else 'raw_contribution'
            contributions = [filtered_contribs[name][values_key] for name in names]
            trends = [filtered_contribs[name]['improvement_trend'] for name in names]
            
            # Color mapping
            colors = []
            for name in names:
                goal_type = filtered_contribs[name]['type']
                if goal_type == 'Maximize':
                    colors.append(COLOR_SUCCESS)
                elif goal_type == 'Minimize':
                    colors.append(COLOR_PRIMARY)
                elif goal_type == 'Target':
                    colors.append(COLOR_WARNING)
                else:
                    colors.append(COLOR_SECONDARY)
            
            # Plot 1: Goal Contributions
            bars1 = ax1.bar(names, contributions, color=colors, alpha=0.7)
            ax1.set_title('Goal Contributions to Optimization', fontweight='bold')
            ax1.set_ylabel('Normalized Contribution' if self.show_normalized.get() else 'Raw Contribution')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            
            # Add value labels above bars
            for bar, value in zip(bars1, contributions):
                height = bar.get_height()
                # Handle edge cases for positioning
                value_range = max(contributions) - min(contributions) if contributions else 0
                y_offset = value_range * 0.01 if value_range > 0 else 0.01
                text_y = height + y_offset if height >= 0 else height - y_offset
                text_va = 'bottom' if height >= 0 else 'top'
                ax1.text(bar.get_x() + bar.get_width()/2., text_y,
                        f'{value:.4f}', ha='center', va=text_va, fontsize=8, fontweight='bold')
            
            # Plot 2: Improvement Trends
            bars2 = ax2.bar(names, trends, color=colors, alpha=0.7)
            ax2.set_title('Goal Improvement Trends', fontweight='bold')
            ax2.set_ylabel('Trend Slope')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            
            # Add value labels above bars
            for bar, value in zip(bars2, trends):
                height = bar.get_height()
                # Handle negative values by placing text appropriately
                y_offset = (max(trends) - min(trends))*0.01 if max(trends) != min(trends) else 0.01
                text_y = height + y_offset if height >= 0 else height - y_offset
                text_va = 'bottom' if height >= 0 else 'top'
                ax2.text(bar.get_x() + bar.get_width()/2., text_y,
                        f'{value:.4f}', ha='center', va=text_va, fontsize=8, fontweight='bold')
            
            self.contrib_fig.tight_layout()
            self.contrib_canvas.draw()
            
            # Update statistics
            self._update_goal_statistics(filtered_contribs)
            
        except Exception as e:
            logger.error(f"Error updating goal contributions: {e}")
    
    def _update_goal_statistics(self, contributions):
        """Update the goal statistics display"""
        try:
            self.goal_stats_text.delete(1.0, tk.END)
            
            stats_text = "GOAL STATISTICS\n"
            stats_text += "=" * 20 + "\n\n"
            
            total_goals = len(contributions)
            goal_types = {}
            
            for name, contrib in contributions.items():
                goal_type = contrib['type']
                goal_types[goal_type] = goal_types.get(goal_type, 0) + 1
            
            stats_text += f"Total Goals: {total_goals}\n\n"
            
            for goal_type, count in goal_types.items():
                stats_text += f"{goal_type}: {count}\n"
            
            stats_text += "\nTOP CONTRIBUTORS:\n"
            sorted_contribs = sorted(contributions.items(), 
                                   key=lambda x: abs(x[1]['raw_contribution']), 
                                   reverse=True)
            
            for i, (name, contrib) in enumerate(sorted_contribs[:3]):
                value = contrib['raw_contribution']
                stats_text += f"{i+1}. {name}: {value:.4f}\n"
            
            self.goal_stats_text.insert(1.0, stats_text)
            
        except Exception as e:
            logger.error(f"Error updating goal statistics: {e}")
    
    def _update_target_achievement(self, event=None):
        """Update the target achievement visualization"""
        try:
            self.target_fig.clear()
            
            achievements = self.dashboard_data['target_achievements']
            if not achievements:
                ax = self.target_fig.add_subplot(111)
                ax.text(0.5, 0.5, 'No target goals defined', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color=COLOR_SECONDARY)
                self.target_canvas.draw()
                
                # Update combo box
                self.target_param_combo['values'] = []
                return
            
            # Update combo box
            target_names = list(achievements.keys())
            self.target_param_combo['values'] = target_names
            if not self.target_param_var.get() and target_names:
                self.target_param_var.set(target_names[0])
            
            selected_param = self.target_param_var.get()
            if selected_param not in achievements:
                return
            
            achievement_data = achievements[selected_param]
            
            ax = self.target_fig.add_subplot(111)
            
            # Plot deviation history
            history = achievement_data['history']
            iterations = list(range(len(history)))
            
            ax.plot(iterations, history, 'o-', color=COLOR_PRIMARY, linewidth=2, markersize=4)
            
            # Add target line
            target_value = achievement_data['target_value']
            tolerance_pct = float(self.tolerance_var.get()) / 100
            tolerance = abs(target_value * tolerance_pct)
            
            ax.axhline(y=tolerance, color=COLOR_SUCCESS, linestyle='--', alpha=0.7, 
                      label=f'Tolerance ({tolerance_pct*100}%)')
            ax.axhline(y=0, color=COLOR_WARNING, linestyle='-', alpha=0.7, 
                      label='Perfect Target')
            
            ax.set_title(f'Target Achievement: {selected_param}', fontweight='bold')
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Deviation from Target')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Add achievement percentage as text
            achievement_pct = achievement_data['achievement_pct']
            ax.text(0.02, 0.98, f'Achievement: {achievement_pct:.1f}%', 
                   transform=ax.transAxes, fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=COLOR_SUCCESS, alpha=0.7),
                   verticalalignment='top')
            
            self.target_fig.tight_layout()
            self.target_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating target achievement: {e}")
    
    def _update_tradeoff_analysis(self):
        """Update the trade-off analysis visualization"""
        try:
            self.tradeoff_fig.clear()
            
            if not self.optimizer or not hasattr(self.optimizer, 'experimental_data'):
                ax = self.tradeoff_fig.add_subplot(111)
                ax.text(0.5, 0.5, 'No experimental data available', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color=COLOR_SECONDARY)
                self.tradeoff_canvas.draw()
                return
            
            data = self.optimizer.experimental_data
            objectives = self.dashboard_data.get('goal_contributions', {})
            
            if len(objectives) < 2:
                ax = self.tradeoff_fig.add_subplot(111)
                ax.text(0.5, 0.5, 'Need at least 2 objectives for trade-off analysis', 
                       ha='center', va='center', transform=ax.transAxes,
                       fontsize=12, color=COLOR_SECONDARY)
                self.tradeoff_canvas.draw()
                return
            
            # Create scatter plot matrix for objectives
            objective_names = list(objectives.keys())[:4]  # Limit to 4 for readability
            n_obj = len(objective_names)
            
            if n_obj == 2:
                ax = self.tradeoff_fig.add_subplot(111)
                if objective_names[0] in data.columns and objective_names[1] in data.columns:
                    x_data = data[objective_names[0]]
                    y_data = data[objective_names[1]]
                    ax.scatter(x_data, y_data, alpha=0.6, s=50, color=COLOR_PRIMARY)
                    ax.set_xlabel(objective_names[0])
                    ax.set_ylabel(objective_names[1])
                    ax.set_title('Objective Trade-off Analysis', fontweight='bold')
                    ax.grid(True, alpha=0.3)
            else:
                # Multiple subplots for multiple objectives
                subplot_idx = 1
                max_subplots = 4  # 2x2 grid
                for i in range(min(n_obj-1, 3)):
                    for j in range(i+1, min(n_obj, 4)):
                        if subplot_idx > max_subplots:
                            break
                        ax = self.tradeoff_fig.add_subplot(2, 2, subplot_idx)
                        if objective_names[i] in data.columns and objective_names[j] in data.columns:
                            x_data = data[objective_names[i]]
                            y_data = data[objective_names[j]]
                            ax.scatter(x_data, y_data, alpha=0.6, s=30, color=COLOR_PRIMARY)
                            ax.set_xlabel(objective_names[i])
                            ax.set_ylabel(objective_names[j])
                            ax.grid(True, alpha=0.3)
                        subplot_idx += 1
            
            self.tradeoff_fig.tight_layout()
            self.tradeoff_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating trade-off analysis: {e}")
    
    def _update_performance_metrics(self):
        """Update the performance metrics table"""
        try:
            logger.debug("=== UPDATING PERFORMANCE METRICS TABLE ===")
            # Clear existing items
            for item in self.metrics_tree.get_children():
                self.metrics_tree.delete(item)
            
            metrics = self.dashboard_data['performance_metrics']
            contributions = self.dashboard_data['goal_contributions']
            
            logger.debug(f"📊 Performance metrics data: {len(metrics)} items")
            logger.debug(f"📊 Metrics keys: {list(metrics.keys())}")
            logger.debug(f"📊 Contributions data: {len(contributions)} items")
            logger.debug(f"📊 Contributions keys: {list(contributions.keys())}")
            
            if not metrics:
                logger.debug("❌ No performance metrics to display")
                return
            
            logger.debug("📝 Adding items to performance metrics table:")
            
            for name, metric in metrics.items():
                logger.debug(f"📋 Processing metric: {name}")
                logger.debug(f"   - category: {metric.get('category', 'unknown')}")
                logger.debug(f"   - goal_type: '{metric.get('goal_type', 'MISSING')}'")
                logger.debug(f"   - full metric: {metric}")
                
                contrib = contributions.get(name, {})
                logger.debug(f"   - contribution: {contrib}")
                
                # Handle different types of best_value (could be number or string for Range goals)
                if isinstance(metric['best_value'], str):
                    best_value_str = metric['best_value']
                else:
                    best_value_str = f"{metric['best_value']:.4f}"
                
                values = (
                    name,
                    metric['goal_type'],
                    f"{metric['current_value']:.4f}",
                    best_value_str,
                    f"{metric['achievement_pct']:.1f}%",
                    f"{contrib.get('normalized_contribution', 0):.4f}"
                )
                
                print(f"🔥 TABLE ROW ADDED: {values}")
                logger.debug(f"   ✅ TABLE ROW: {values}")
                self.metrics_tree.insert("", "end", values=values)
                
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    def _toggle_auto_refresh(self):
        """Toggle auto-refresh functionality"""
        if self.auto_refresh.get():
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()
    
    def _start_auto_refresh(self):
        """Start auto-refresh timer"""
        if hasattr(self, '_refresh_timer'):
            self.popup_window.after_cancel(self._refresh_timer)
        
        def auto_refresh():
            if self.auto_refresh.get() and self.popup_window:
                self.refresh_dashboard()
                self._refresh_timer = self.popup_window.after(
                    self.refresh_interval.get() * 1000, auto_refresh
                )
        
        self._refresh_timer = self.popup_window.after(
            self.refresh_interval.get() * 1000, auto_refresh
        )
    
    def _stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        if hasattr(self, '_refresh_timer'):
            self.popup_window.after_cancel(self._refresh_timer)
    
    def export_dashboard(self):
        """Export dashboard data and visualizations"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                title="Export Dashboard Data",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'dashboard_data': self.dashboard_data,
                    'settings': {
                        'auto_refresh': self.auto_refresh.get(),
                        'refresh_interval': self.refresh_interval.get(),
                        'show_normalized': self.show_normalized.get()
                    }
                }
                
                import json
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                self.status_label.config(text=f"Dashboard exported to {filename}")
                
        except Exception as e:
            error_msg = f"Error exporting dashboard: {str(e)}"
            self.status_label.config(text=error_msg)
            messagebox.showerror("Export Error", error_msg)
    
    def show(self):
        """Show the dashboard window"""
        if self.popup_window:
            try:
                # Check if window still exists
                self.popup_window.winfo_exists()
                self.popup_window.deiconify()
                self.popup_window.lift()
            except tk.TclError:
                # Window was destroyed, create a new one
                print("🔥 Dashboard window was destroyed, creating new one")
                self.popup_window = None
                self.create_dashboard()
    
    def hide(self):
        """Hide the dashboard window"""
        if self.popup_window:
            try:
                self.popup_window.winfo_exists()
                self.popup_window.withdraw()
            except tk.TclError:
                # Window was already destroyed
                self.popup_window = None
    
    def close(self):
        """Close the dashboard window"""
        self._stop_auto_refresh()
        if self.popup_window:
            try:
                self.popup_window.destroy()
            except tk.TclError:
                # Window was already destroyed
                pass
            finally:
                self.popup_window = None


def create_goal_impact_dashboard(parent, optimizer=None, update_callback: Callable = None):
    """
    Factory function to create a Goal Impact Dashboard.
    
    Args:
        parent: Parent Tkinter widget
        optimizer: PyMBO optimizer instance
        update_callback: Optional callback for external updates
        
    Returns:
        GoalImpactDashboard: Configured dashboard instance
    """
    dashboard = GoalImpactDashboard(parent, optimizer, update_callback)
    dashboard.create_dashboard()
    return dashboard