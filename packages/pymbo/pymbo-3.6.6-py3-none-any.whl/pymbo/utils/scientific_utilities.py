"""
scientific_utilities.py

Minimal utilities for scientific validation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class ScientificValidator:
    """Minimal scientific data validator"""

    def validate_experimental_data(
        self, data: pd.DataFrame, params_config: Dict, responses_config: Dict
    ) -> Dict[str, Any]:
        """Validate experimental data"""
        try:
            validation_report = {
                "valid": True,
                "warnings": [],
                "errors": [],
                "data_quality": "Good",
                "n_experiments": len(data),
                "completeness": 1.0,
            }

            # Basic validation
            if data.empty:
                validation_report["valid"] = False
                validation_report["errors"].append("No experimental data provided")
                return validation_report

            # Check for required columns
            missing_params = [p for p in params_config.keys() if p not in data.columns]
            missing_responses = [
                r for r in responses_config.keys() if r not in data.columns
            ]

            if missing_params:
                validation_report["warnings"].append(
                    f"Missing parameters: {missing_params}"
                )
            if missing_responses:
                validation_report["warnings"].append(
                    f"Missing responses: {missing_responses}"
                )

            # Check for NaN values
            nan_count = data.isnull().sum().sum()
            if nan_count > 0:
                validation_report["warnings"].append(f"Found {nan_count} NaN values")
                validation_report["completeness"] = 1.0 - (
                    nan_count / (len(data) * len(data.columns))
                )

            # Add basic descriptive statistics
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                descriptive_stats = {}
                for col in numeric_columns:
                    col_data = data[col].dropna()
                    if len(col_data) > 0:
                        descriptive_stats[col] = {
                            "mean": float(col_data.mean()),
                            "std": float(col_data.std()) if len(col_data) > 1 else 0.0,
                            "min": float(col_data.min()),
                            "max": float(col_data.max()),
                            "count": int(len(col_data))
                        }
                validation_report["descriptive_statistics"] = descriptive_stats

            # Add outlier detection (simple IQR method)
            outlier_counts = {}
            for col in numeric_columns:
                col_data = data[col].dropna()
                if len(col_data) > 4:  # Need at least 5 points for IQR
                    Q1 = col_data.quantile(0.25)
                    Q3 = col_data.quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                    outlier_counts[col] = len(outliers)
                else:
                    outlier_counts[col] = 0
            validation_report["outlier_counts"] = outlier_counts

            return validation_report

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation failed: {str(e)}"],
                "warnings": [],
                "data_quality": "Poor",
                "n_experiments": 0,
                "completeness": 0.0,
            }


# Create global instance
scientific_validator = ScientificValidator()
