"""
Import Data Wizard for PyMBO

This module provides a comprehensive wizard for importing CSV data into PyMBO,
including automatic parameter type detection, data validation, and configuration setup.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import logging


class ParameterTypeDetector:
    """Utility class for detecting parameter types from data."""
    
    @staticmethod
    def detect_parameter_type(series: pd.Series, column_name: str) -> Dict[str, Any]:
        """
        Detect if a parameter is continuous, discrete, or categorical.
        
        Args:
            series: Pandas series containing the parameter data
            column_name: Name of the column
            
        Returns:
            Dict containing type information and bounds/categories
        """
        # Remove NaN values for analysis
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return {"type": "continuous", "bounds": [0, 1], "note": "No valid data"}
        
        # Check if data is numeric
        if pd.api.types.is_numeric_dtype(clean_series):
            unique_values = clean_series.nunique()
            total_values = len(clean_series)
            
            # If very few unique values relative to total, likely categorical
            if unique_values <= 5 and unique_values / total_values < 0.1:
                categories = sorted(clean_series.unique().tolist())
                return {
                    "type": "categorical",
                    "categories": categories,
                    "bounds": [min(categories), max(categories)],
                    "note": f"{unique_values} unique numeric values"
                }
            
            # Check if all values are integers
            if clean_series.dtype in ['int64', 'int32'] or all(clean_series == clean_series.astype(int)):
                # If reasonable number of unique integers, treat as discrete
                if unique_values <= 20:
                    return {
                        "type": "discrete", 
                        "bounds": [int(clean_series.min()), int(clean_series.max())],
                        "unique_count": unique_values,
                        "note": f"Integer values, {unique_values} unique"
                    }
            
            # Default to continuous for numeric data
            return {
                "type": "continuous",
                "bounds": [float(clean_series.min()), float(clean_series.max())],
                "note": f"Continuous numeric, range: {clean_series.min():.3f} to {clean_series.max():.3f}"
            }
        
        else:
            # Non-numeric data - categorical
            unique_values = clean_series.nunique()
            categories = sorted(clean_series.unique().tolist())
            
            # Limit categories for display
            if len(categories) > 10:
                display_categories = categories[:10] + [f"... and {len(categories)-10} more"]
                note = f"String categorical, {unique_values} categories (showing first 10)"
            else:
                display_categories = categories
                note = f"String categorical, {unique_values} categories"
            
            return {
                "type": "categorical",
                "categories": categories,
                "display_categories": display_categories,
                "bounds": [0, len(categories)-1],  # Index bounds for categorical
                "note": note
            }


class DataValidator:
    """Utility class for validating and cleaning imported data."""
    
    @staticmethod
    def validate_data(df: pd.DataFrame, param_columns: List[str], response_columns: List[str]) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Validate data and identify problematic rows.
        
        Args:
            df: DataFrame to validate
            param_columns: List of parameter column names
            response_columns: List of response column names
            
        Returns:
            Tuple of (clean_df, list_of_issues)
        """
        issues = []
        clean_df = df.copy()
        
        # Check for missing values
        for col in param_columns + response_columns:
            if col in df.columns:
                missing_mask = df[col].isna()
                if missing_mask.any():
                    missing_indices = df[missing_mask].index.tolist()
                    issues.append({
                        "type": "missing_values",
                        "column": col,
                        "rows": missing_indices,
                        "count": len(missing_indices),
                        "message": f"Missing values in {col}"
                    })
        
        # Check for non-numeric data in parameter columns
        for col in param_columns:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='raise')
                except (ValueError, TypeError):
                    # Find non-numeric rows
                    non_numeric_mask = pd.to_numeric(df[col], errors='coerce').isna() & df[col].notna()
                    if non_numeric_mask.any():
                        non_numeric_indices = df[non_numeric_mask].index.tolist()
                        issues.append({
                            "type": "non_numeric",
                            "column": col,
                            "rows": non_numeric_indices,
                            "count": len(non_numeric_indices),
                            "message": f"Non-numeric values in parameter {col}"
                        })
        
        # Check for non-numeric data in response columns
        for col in response_columns:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='raise')
                except (ValueError, TypeError):
                    non_numeric_mask = pd.to_numeric(df[col], errors='coerce').isna() & df[col].notna()
                    if non_numeric_mask.any():
                        non_numeric_indices = df[non_numeric_mask].index.tolist()
                        issues.append({
                            "type": "non_numeric",
                            "column": col,
                            "rows": non_numeric_indices,
                            "count": len(non_numeric_indices),
                            "message": f"Non-numeric values in response {col}"
                        })
        
        return clean_df, issues


class ImportWizard(tk.Toplevel):
    """Multi-step wizard for importing CSV data into PyMBO."""
    
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.csv_data = None
        self.csv_filepath = None
        self.column_classification = {}
        self.parameter_config = {}
        self.response_config = {}
        self.validated_data = None
        
        self.setup_ui()
        self.current_step = 0
        self.show_step(0)
        
    def setup_ui(self):
        """Setup the wizard UI."""
        self.title("Import Data Wizard")
        self.geometry("900x700")
        self.resizable(True, True)
        self.minsize(800, 600)
        
        # Make modal
        self.transient(self.parent)
        self.grab_set()
        
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ttk.Label(main_frame, text="Import Data Wizard", font=('Arial', 16, 'bold'))
        self.title_label.pack(pady=(0, 20))
        
        # Step indicator
        self.step_frame = ttk.Frame(main_frame)
        self.step_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Content frame (will hold different steps)
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.back_btn = ttk.Button(button_frame, text="← Back", command=self.go_back)
        self.back_btn.pack(side=tk.LEFT)
        
        self.next_btn = ttk.Button(button_frame, text="Next →", command=self.go_next)
        self.next_btn.pack(side=tk.RIGHT)
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Steps
        self.steps = [
            ("Select File", self.create_file_selection_step),
            ("Classify Columns", self.create_column_classification_step),
            ("Configure Parameters", self.create_parameter_config_step),
            ("Validate Data", self.create_data_validation_step),
            ("Review & Finish", self.create_review_step)
        ]
        
        self.create_step_indicator()
        
    def create_step_indicator(self):
        """Create visual step indicator."""
        for i, (step_name, _) in enumerate(self.steps):
            step_label = ttk.Label(self.step_frame, text=f"{i+1}. {step_name}")
            step_label.pack(side=tk.LEFT, padx=10)
            
    def clear_content(self):
        """Clear the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_step(self, step_index):
        """Show a specific step."""
        self.current_step = step_index
        self.clear_content()
        
        # Update button states
        self.back_btn.config(state=tk.NORMAL if step_index > 0 else tk.DISABLED)
        self.next_btn.config(text="Finish" if step_index == len(self.steps) - 1 else "Next →")
        
        # Update title
        step_name, step_func = self.steps[step_index]
        self.title_label.config(text=f"Step {step_index + 1}: {step_name}")
        
        # Create step content
        step_func()
        
    def create_file_selection_step(self):
        """Step 1: File selection."""
        ttk.Label(self.content_frame, text="Select a CSV file to import:", font=('Arial', 12)).pack(pady=10)
        
        file_frame = ttk.Frame(self.content_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state='readonly')
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(file_frame, text="Browse...", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # File info frame
        self.file_info_frame = ttk.LabelFrame(self.content_frame, text="File Information")
        self.file_info_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        if self.csv_filepath:
            self.file_path_var.set(self.csv_filepath)
            self.display_file_info()
            
    def browse_file(self):
        """Browse for CSV file."""
        filepath = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.csv_data = pd.read_csv(filepath)
                self.csv_filepath = filepath
                self.file_path_var.set(filepath)
                self.display_file_info()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read CSV file: {str(e)}")
                
    def display_file_info(self):
        """Display information about the loaded CSV file."""
        if self.csv_data is None:
            return
            
        # Clear existing info
        for widget in self.file_info_frame.winfo_children():
            widget.destroy()
            
        info_text = f"""File: {Path(self.csv_filepath).name}
Rows: {len(self.csv_data)}
Columns: {len(self.csv_data.columns)}

Columns: {', '.join(self.csv_data.columns.tolist())}

First few rows:"""
        
        ttk.Label(self.file_info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=10)
        
        # Show preview in a text widget
        preview_frame = ttk.Frame(self.file_info_frame)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        preview_text = tk.Text(preview_frame, height=10, wrap=tk.NONE)
        preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        v_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_text.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        preview_text.config(yscrollcommand=v_scroll.set)
        
        h_scroll = ttk.Scrollbar(self.file_info_frame, orient=tk.HORIZONTAL, command=preview_text.xview)
        h_scroll.pack(fill=tk.X, padx=10)
        preview_text.config(xscrollcommand=h_scroll.set)
        
        # Insert preview data
        preview_data = self.csv_data.head(10).to_string()
        preview_text.insert(tk.END, preview_data)
        preview_text.config(state=tk.DISABLED)
        
    def create_column_classification_step(self):
        """Step 2: Column classification."""
        if self.csv_data is None:
            ttk.Label(self.content_frame, text="No CSV file loaded. Please go back and select a file.").pack()
            return
            
        ttk.Label(self.content_frame, text="Classify each column as Parameter, Response, or Ignore:", 
                 font=('Arial', 12)).pack(pady=10)
        
        # Create scrollable frame
        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Column classification widgets
        self.column_vars = {}
        
        # Header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header_frame, text="Column Name", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, anchor=tk.W, padx=(0, 150))
        ttk.Label(header_frame, text="Type", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, anchor=tk.W, padx=(0, 100))
        ttk.Label(header_frame, text="Sample Values", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, anchor=tk.W)
        
        for col in self.csv_data.columns:
            col_frame = ttk.Frame(scrollable_frame)
            col_frame.pack(fill=tk.X, padx=10, pady=2)
            
            # Column name
            ttk.Label(col_frame, text=col, width=20).pack(side=tk.LEFT, anchor=tk.W)
            
            # Classification dropdown
            classification_var = tk.StringVar(value="Parameter")
            self.column_vars[col] = classification_var
            
            classification_combo = ttk.Combobox(col_frame, textvariable=classification_var,
                                              values=["Parameter", "Response", "Ignore"],
                                              state="readonly", width=12)
            classification_combo.pack(side=tk.LEFT, padx=(10, 20))
            
            # Sample values
            sample_values = self.csv_data[col].dropna().head(3).tolist()
            sample_text = ", ".join(str(v)[:20] for v in sample_values)
            if len(sample_text) > 60:
                sample_text = sample_text[:57] + "..."
                
            ttk.Label(col_frame, text=sample_text, width=30).pack(side=tk.LEFT, anchor=tk.W)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_parameter_config_step(self):
        """Step 3: Parameter configuration."""
        if not self.column_vars:
            ttk.Label(self.content_frame, text="Please complete column classification first.").pack()
            return
            
        # Extract parameter and response columns
        param_columns = [col for col, var in self.column_vars.items() if var.get() == "Parameter"]
        response_columns = [col for col, var in self.column_vars.items() if var.get() == "Response"]
        
        if not param_columns and not response_columns:
            ttk.Label(self.content_frame, text="Please select at least one Parameter or Response column.").pack()
            return
            
        ttk.Label(self.content_frame, text="Configure Parameters and Responses:", 
                 font=('Arial', 12)).pack(pady=10)
        
        # Create notebook for parameters and responses
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        if param_columns:
            param_frame = ttk.Frame(notebook)
            notebook.add(param_frame, text=f"Parameters ({len(param_columns)})")
            self.create_parameter_config_tab(param_frame, param_columns)
            
        if response_columns:
            response_frame = ttk.Frame(notebook)
            notebook.add(response_frame, text=f"Responses ({len(response_columns)})")
            self.create_response_config_tab(response_frame, response_columns)
            
    def create_parameter_config_tab(self, parent, param_columns):
        """Create parameter configuration tab."""
        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.param_config_vars = {}
        
        for col in param_columns:
            # Detect parameter type
            param_info = ParameterTypeDetector.detect_parameter_type(self.csv_data[col], col)
            
            col_frame = ttk.LabelFrame(scrollable_frame, text=col)
            col_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Type selection
            type_frame = ttk.Frame(col_frame)
            type_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(type_frame, text="Type:").pack(side=tk.LEFT)
            
            type_var = tk.StringVar(value=param_info["type"])
            type_combo = ttk.Combobox(type_frame, textvariable=type_var,
                                    values=["continuous", "discrete", "categorical"],
                                    state="readonly", width=12)
            type_combo.pack(side=tk.LEFT, padx=(10, 20))
            
            # Bounds/categories frame
            bounds_frame = ttk.Frame(col_frame)
            bounds_frame.pack(fill=tk.X, padx=10, pady=5)
            
            if param_info["type"] in ["continuous", "discrete"]:
                ttk.Label(bounds_frame, text="Min:").pack(side=tk.LEFT)
                min_var = tk.StringVar(value=str(param_info["bounds"][0]))
                min_entry = ttk.Entry(bounds_frame, textvariable=min_var, width=10)
                min_entry.pack(side=tk.LEFT, padx=(5, 20))
                
                ttk.Label(bounds_frame, text="Max:").pack(side=tk.LEFT)
                max_var = tk.StringVar(value=str(param_info["bounds"][1]))
                max_entry = ttk.Entry(bounds_frame, textvariable=max_var, width=10)
                max_entry.pack(side=tk.LEFT, padx=(5, 0))
                
                # Goal selection for parameters
                goal_frame = ttk.Frame(col_frame)
                goal_frame.pack(fill=tk.X, padx=10, pady=5)
                
                ttk.Label(goal_frame, text="Goal:").pack(side=tk.LEFT)
                
                param_goal_var = tk.StringVar(value="None")
                param_goal_combo = ttk.Combobox(goal_frame, textvariable=param_goal_var,
                                              values=["None", "Maximize", "Minimize", "Target", "Range"],
                                              state="readonly", width=12)
                param_goal_combo.pack(side=tk.LEFT, padx=(10, 20))
                
                # Target value entry (initially disabled)
                ttk.Label(goal_frame, text="Target:").pack(side=tk.LEFT)
                param_target_var = tk.StringVar()
                param_target_entry = ttk.Entry(goal_frame, textvariable=param_target_var, width=10, state="disabled")
                param_target_entry.pack(side=tk.LEFT, padx=(5, 0))
                
                # Bind goal change to enable/disable target entry
                def on_param_goal_change(event, target_entry=param_target_entry, goal_var=param_goal_var):
                    if goal_var.get() in ["Target", "Range"]:
                        target_entry.config(state="normal")
                    else:
                        target_entry.config(state="disabled")
                        
                param_goal_combo.bind("<<ComboboxSelected>>", on_param_goal_change)
                
                self.param_config_vars[col] = {
                    "type": type_var,
                    "min": min_var,
                    "max": max_var,
                    "goal": param_goal_var,
                    "target": param_target_var,
                    "info": param_info
                }
            else:
                # Categorical
                ttk.Label(bounds_frame, text="Categories:").pack(side=tk.LEFT)
                cats_text = ", ".join(str(c) for c in param_info.get("display_categories", param_info.get("categories", [])))
                ttk.Label(bounds_frame, text=cats_text, width=50, anchor=tk.W).pack(side=tk.LEFT, padx=(5, 0))
                
                # Goal selection for categorical parameters
                goal_frame = ttk.Frame(col_frame)
                goal_frame.pack(fill=tk.X, padx=10, pady=5)
                
                ttk.Label(goal_frame, text="Goal:").pack(side=tk.LEFT)
                
                param_goal_var = tk.StringVar(value="None")
                param_goal_combo = ttk.Combobox(goal_frame, textvariable=param_goal_var,
                                              values=["None", "Maximize", "Minimize", "Target", "Range"],
                                              state="readonly", width=12)
                param_goal_combo.pack(side=tk.LEFT, padx=(10, 20))
                
                # Target value entry (initially disabled)
                ttk.Label(goal_frame, text="Target:").pack(side=tk.LEFT)
                param_target_var = tk.StringVar()
                param_target_entry = ttk.Entry(goal_frame, textvariable=param_target_var, width=10, state="disabled")
                param_target_entry.pack(side=tk.LEFT, padx=(5, 0))
                
                # Bind goal change to enable/disable target entry
                def on_param_goal_change(event, target_entry=param_target_entry, goal_var=param_goal_var):
                    if goal_var.get() in ["Target", "Range"]:
                        target_entry.config(state="normal")
                    else:
                        target_entry.config(state="disabled")
                        
                param_goal_combo.bind("<<ComboboxSelected>>", on_param_goal_change)
                
                self.param_config_vars[col] = {
                    "type": type_var,
                    "categories": param_info["categories"],
                    "goal": param_goal_var,
                    "target": param_target_var,
                    "info": param_info
                }
            
            # Info label
            ttk.Label(col_frame, text=param_info["note"], font=('Arial', 9), 
                     foreground='gray').pack(anchor=tk.W, padx=10, pady=(0, 10))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_response_config_tab(self, parent, response_columns):
        """Create response configuration tab."""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.response_config_vars = {}
        
        for col in response_columns:
            col_frame = ttk.LabelFrame(scrollable_frame, text=col)
            col_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Goal selection
            goal_frame = ttk.Frame(col_frame)
            goal_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Label(goal_frame, text="Goal:").pack(side=tk.LEFT)
            
            goal_var = tk.StringVar(value="Maximize")
            goal_combo = ttk.Combobox(goal_frame, textvariable=goal_var,
                                    values=["Maximize", "Minimize", "Target", "Range"],
                                    state="readonly", width=12)
            goal_combo.pack(side=tk.LEFT, padx=(10, 0))
            
            self.response_config_vars[col] = {"goal": goal_var}
            
            # Data range info
            col_data = self.csv_data[col].dropna()
            if len(col_data) > 0:
                range_text = f"Range: {col_data.min():.3f} to {col_data.max():.3f}"
                ttk.Label(col_frame, text=range_text, font=('Arial', 9), 
                         foreground='gray').pack(anchor=tk.W, padx=10, pady=(0, 10))
        
        canvas.pack(side="left", fill="both", expand=True) 
        scrollbar.pack(side="right", fill="y")
        
    def create_data_validation_step(self):
        """Step 4: Data validation."""
        ttk.Label(self.content_frame, text="Data Validation", font=('Arial', 12)).pack(pady=10)
        
        # Get current configuration
        param_columns = [col for col, var in self.column_vars.items() if var.get() == "Parameter"]
        response_columns = [col for col, var in self.column_vars.items() if var.get() == "Response"]
        
        # Validate data
        clean_data, issues = DataValidator.validate_data(self.csv_data, param_columns, response_columns)
        
        if not issues:
            ttk.Label(self.content_frame, text="✅ No data validation issues found!", 
                     font=('Arial', 12), foreground='green').pack(pady=20)
            self.validated_data = clean_data
        else:
            ttk.Label(self.content_frame, text=f"⚠️ Found {len(issues)} validation issues:", 
                     font=('Arial', 12), foreground='orange').pack(pady=10)
            
            # Issues frame
            issues_frame = ttk.LabelFrame(self.content_frame, text="Issues Found")
            issues_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            # Create scrollable text
            text_frame = ttk.Frame(issues_frame)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            issues_text = tk.Text(text_frame, height=15, wrap=tk.WORD)
            issues_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=issues_text.yview)
            issues_text.configure(yscrollcommand=issues_scrollbar.set)
            
            for issue in issues:
                issues_text.insert(tk.END, f"• {issue['message']}: {issue['count']} rows\n")
                issues_text.insert(tk.END, f"  Affected rows: {issue['rows'][:10]}{'...' if len(issue['rows']) > 10 else ''}\n\n")
            
            issues_text.config(state=tk.DISABLED)
            issues_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            issues_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Action buttons
            action_frame = ttk.Frame(self.content_frame)
            action_frame.pack(fill=tk.X, pady=10)
            
            ttk.Button(action_frame, text="Delete Problem Rows", 
                      command=lambda: self.handle_data_issues(issues, "delete")).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(action_frame, text="Edit Problem Rows", 
                      command=lambda: self.handle_data_issues(issues, "edit")).pack(side=tk.LEFT)
        
    def handle_data_issues(self, issues, action):
        """Handle data validation issues."""
        if action == "delete":
            # Delete problematic rows
            rows_to_delete = set()
            for issue in issues:
                rows_to_delete.update(issue['rows'])
            
            if messagebox.askyesno("Confirm Deletion", 
                                  f"Delete {len(rows_to_delete)} problematic rows?"):
                self.validated_data = self.csv_data.drop(index=list(rows_to_delete)).reset_index(drop=True)
                messagebox.showinfo("Success", f"Deleted {len(rows_to_delete)} rows.")
                self.show_step(self.current_step)  # Refresh
                
        elif action == "edit":
            # Open edit dialog
            self.open_data_editor(issues)
            
    def open_data_editor(self, issues):
        """Open data editor for problematic rows."""
        editor = DataEditor(self, self.csv_data, issues)
        self.wait_window(editor)
        
        if hasattr(editor, 'edited_data'):
            self.validated_data = editor.edited_data
            self.show_step(self.current_step)  # Refresh
        
    def create_review_step(self):
        """Step 5: Review and finish."""
        ttk.Label(self.content_frame, text="Review Configuration", font=('Arial', 12)).pack(pady=10)
        
        # Create notebook for review
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Parameters tab
        param_frame = ttk.Frame(notebook)
        notebook.add(param_frame, text="Parameters")
        
        param_text = tk.Text(param_frame, height=10, wrap=tk.WORD)
        param_scroll = ttk.Scrollbar(param_frame, orient=tk.VERTICAL, command=param_text.yview)
        param_text.configure(yscrollcommand=param_scroll.set)
        
        # Generate parameter configuration
        for col, config in getattr(self, 'param_config_vars', {}).items():
            param_text.insert(tk.END, f"Parameter: {col}\n")
            param_text.insert(tk.END, f"  Type: {config['type'].get()}\n")
            if config['type'].get() in ['continuous', 'discrete']:
                param_text.insert(tk.END, f"  Range: {config['min'].get()} to {config['max'].get()}\n")
            else:
                param_text.insert(tk.END, f"  Categories: {len(config.get('categories', []))} values\n")
            param_text.insert(tk.END, "\n")
        
        param_text.config(state=tk.DISABLED)
        param_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        param_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Responses tab
        response_frame = ttk.Frame(notebook)
        notebook.add(response_frame, text="Responses")
        
        response_text = tk.Text(response_frame, height=10, wrap=tk.WORD)
        response_scroll = ttk.Scrollbar(response_frame, orient=tk.VERTICAL, command=response_text.yview)
        response_text.configure(yscrollcommand=response_scroll.set)
        
        for col, config in getattr(self, 'response_config_vars', {}).items():
            response_text.insert(tk.END, f"Response: {col}\n")
            response_text.insert(tk.END, f"  Goal: {config['goal'].get()}\n\n")
        
        response_text.config(state=tk.DISABLED)
        response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        response_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Data summary
        data_frame = ttk.Frame(notebook)
        notebook.add(data_frame, text="Data Summary")
        
        if self.validated_data is not None:
            summary_text = f"""Original data: {len(self.csv_data)} rows
Final data: {len(self.validated_data)} rows
Data file: {Path(self.csv_filepath).name}

The data will be loaded into the optimizer when you proceed to the main interface."""
        else:
            summary_text = "Data validation not completed."
            
        ttk.Label(data_frame, text=summary_text, justify=tk.LEFT).pack(padx=20, pady=20)
        
    def go_back(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
            
    def go_next(self):
        """Go to next step or finish."""
        if self.current_step < len(self.steps) - 1:
            if self.validate_current_step():
                self.show_step(self.current_step + 1)
        else:
            self.finish_wizard()
            
    def validate_current_step(self):
        """Validate current step before proceeding."""
        if self.current_step == 0:  # File selection
            if self.csv_data is None:
                messagebox.showerror("Error", "Please select a CSV file.")
                return False
                
        elif self.current_step == 1:  # Column classification
            param_cols = [col for col, var in self.column_vars.items() if var.get() == "Parameter"]
            response_cols = [col for col, var in self.column_vars.items() if var.get() == "Response"]
            
            if not param_cols and not response_cols:
                messagebox.showerror("Error", "Please select at least one Parameter or Response column.")
                return False
                
        elif self.current_step == 2:  # Parameter configuration
            # Validate bounds
            for col, config in getattr(self, 'param_config_vars', {}).items():
                if config['type'].get() in ['continuous', 'discrete']:
                    try:
                        min_val = float(config['min'].get())
                        max_val = float(config['max'].get())
                        if min_val >= max_val:
                            messagebox.showerror("Error", f"Invalid bounds for {col}: min must be less than max.")
                            return False
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid numeric bounds for {col}.")
                        return False
                        
        return True
        
    def finish_wizard(self):
        """Finish the wizard and return configuration."""
        try:
            print("🔥 IMPORT WIZARD FINISHING 🔥")
            
            # Build parameter configuration
            self.parameter_config = {}
            print(f"🔥 param_config_vars: {getattr(self, 'param_config_vars', {})}")
            for col, config in getattr(self, 'param_config_vars', {}).items():
                param_type = config['type'].get()
                param_goal = config.get('goal', tk.StringVar(value="None")).get()
                param_target = config.get('target', tk.StringVar()).get().strip()
                print(f"🔥 Parameter '{col}': type={param_type}, goal='{param_goal}', target='{param_target}', config={config}")
                
                if param_type in ['continuous', 'discrete']:
                    param_config = {
                        "type": param_type,
                        "bounds": [float(config['min'].get()), float(config['max'].get())],
                        "goal": param_goal
                    }
                    
                    # Add target/range value if specified
                    if param_goal == "Target" and param_target:
                        try:
                            param_config["target_value"] = float(param_target)
                        except ValueError:
                            print(f"🔥 Warning: Invalid target value '{param_target}' for parameter '{col}'")
                    elif param_goal == "Range" and param_target:
                        try:
                            # Parse range format like "min,max" or "[min,max]"
                            range_str = param_target.strip('[]')
                            if ',' in range_str:
                                min_val, max_val = [float(x.strip()) for x in range_str.split(',')]
                                param_config["min_value"] = min_val
                                param_config["max_value"] = max_val
                            else:
                                print(f"🔥 Warning: Invalid range format '{param_target}' for parameter '{col}'")
                        except ValueError:
                            print(f"🔥 Warning: Invalid range value '{param_target}' for parameter '{col}'")
                    
                    self.parameter_config[col] = param_config
                    print(f"🔥 Created parameter config for '{col}': {self.parameter_config[col]}")
                else:
                    param_config = {
                        "type": "categorical", 
                        "categories": config['categories'],
                        "bounds": [0, len(config['categories']) - 1],
                        "goal": param_goal
                    }
                    
                    # Add target value for categorical parameters if specified
                    if param_goal == "Target" and param_target:
                        if param_target in config['categories']:
                            param_config["target_value"] = param_target
                        else:
                            print(f"🔥 Warning: Target value '{param_target}' not in categories for parameter '{col}'")
                    
                    self.parameter_config[col] = param_config
                    print(f"🔥 Created categorical parameter config for '{col}': {self.parameter_config[col]}")
            
            # Build response configuration
            self.response_config = {}
            print(f"🔥 response_config_vars: {getattr(self, 'response_config_vars', {})}")
            for col, config in getattr(self, 'response_config_vars', {}).items():
                goal = config['goal'].get()
                self.response_config[col] = {
                    "goal": goal
                }
                print(f"🔥 Response '{col}': goal='{goal}', config={self.response_config[col]}")
            
            # Store final data
            if self.validated_data is None:
                self.validated_data = self.csv_data
                
            self.result = {
                "parameters": self.parameter_config,
                "responses": self.response_config,
                "data": self.validated_data,
                "filepath": self.csv_filepath
            }
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete wizard: {str(e)}")
            logging.error(f"Import wizard error: {e}")
            
    def cancel(self):
        """Cancel the wizard."""
        if messagebox.askyesno("Cancel", "Are you sure you want to cancel the import?"):
            self.result = None
            self.destroy()


class DataEditor(tk.Toplevel):
    """Dialog for editing problematic data rows."""
    
    def __init__(self, parent, data, issues):
        super().__init__(parent)
        self.parent = parent
        self.data = data.copy()
        self.issues = issues
        self.edited_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the data editor UI."""
        self.title("Edit Problematic Data")
        self.geometry("800x500")
        self.transient(self.parent)
        self.grab_set()
        
        # Instructions
        ttk.Label(self, text="Edit or delete problematic rows:", font=('Arial', 12)).pack(pady=10)
        
        # Create treeview for data editing
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Get problematic rows
        problem_rows = set()
        for issue in self.issues:
            problem_rows.update(issue['rows'])
        problem_rows = sorted(list(problem_rows))
        
        # Treeview
        columns = ["Row"] + list(self.data.columns)
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Insert problematic rows
        for row_idx in problem_rows:
            row_data = [str(row_idx)] + [str(self.data.iloc[row_idx][col]) for col in self.data.columns]
            self.tree.insert("", tk.END, values=row_data, tags=("problem",))
        
        # Style problematic rows
        self.tree.tag_configure("problem", background="#ffeeee")
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=20, padx=20)
        
        ttk.Button(button_frame, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Button(button_frame, text="Save Changes", command=self.save_changes).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        
    def edit_selected(self):
        """Edit selected row."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a row to edit.")
            return
            
        item = selection[0]
        values = self.tree.item(item, 'values')
        row_idx = int(values[0])
        
        # Open edit dialog
        EditRowDialog(self, self.data, row_idx, self.update_tree_row)
        
    def update_tree_row(self, row_idx, new_values):
        """Update tree row with new values."""
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if int(values[0]) == row_idx:
                updated_values = [str(row_idx)] + [str(v) for v in new_values]
                self.tree.item(item, values=updated_values)
                break
                
    def delete_selected(self):
        """Delete selected rows."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select rows to delete.")
            return
            
        if messagebox.askyesno("Confirm", f"Delete {len(selection)} selected rows?"):
            rows_to_delete = []
            for item in selection:
                values = self.tree.item(item, 'values')
                rows_to_delete.append(int(values[0]))
                self.tree.delete(item)
                
            self.data = self.data.drop(index=rows_to_delete)
            
    def save_changes(self):
        """Save changes and close."""
        self.edited_data = self.data.reset_index(drop=True)
        self.destroy()
        
    def cancel(self):
        """Cancel editing."""
        self.destroy()


class EditRowDialog(tk.Toplevel):
    """Dialog for editing a single row."""
    
    def __init__(self, parent, data, row_idx, callback):
        super().__init__(parent)
        self.parent = parent
        self.data = data
        self.row_idx = row_idx
        self.callback = callback
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the edit row UI."""
        self.title(f"Edit Row {self.row_idx}")
        self.geometry("500x400")
        self.transient(self.parent)
        self.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text=f"Edit values for row {self.row_idx}:", font=('Arial', 12)).pack(pady=(0, 20))
        
        # Create entry widgets for each column
        self.entry_vars = {}
        
        for col in self.data.columns:
            row_frame = ttk.Frame(main_frame)
            row_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(row_frame, text=f"{col}:", width=20).pack(side=tk.LEFT)
            
            var = tk.StringVar(value=str(self.data.iloc[self.row_idx][col]))
            self.entry_vars[col] = var
            
            entry = ttk.Entry(row_frame, textvariable=var, width=30)
            entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)
        
    def save(self):
        """Save the edited values."""
        try:
            new_values = []
            for col in self.data.columns:
                value = self.entry_vars[col].get()
                # Try to convert to appropriate type
                if pd.api.types.is_numeric_dtype(self.data[col]):
                    value = pd.to_numeric(value, errors='coerce')
                new_values.append(value)
                self.data.iloc[self.row_idx, self.data.columns.get_loc(col)] = value
                
            self.callback(self.row_idx, new_values)
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")