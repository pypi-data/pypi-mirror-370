"""
Data validation utilities for QuickInsights.

This module provides utilities for validating and cleaning data including:
- Data type validation
- Data quality checks
- Schema validation
- Data cleaning utilities
"""

import re
from typing import Any, Dict, List, Optional, Union, Tuple
import numpy as np
import pandas as pd


def get_validation_utils():
    """Lazy import for validation utilities."""
    return {
        "validate_dataframe": validate_dataframe,
        "validate_column_types": validate_column_types,
        "check_data_quality": check_data_quality,
        "clean_data": clean_data,
        "validate_schema": validate_schema,
        "detect_anomalies": detect_anomalies,
    }


def validate_dataframe(df: Any) -> pd.DataFrame:
    """
    Validate that input is a valid DataFrame.

    Args:
        df: Input to validate

    Returns:
        Validated DataFrame

    Raises:
        TypeError: If input is not a DataFrame
        ValueError: If DataFrame is empty
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if df.empty:
        raise ValueError("DataFrame cannot be empty")

    return df


def validate_column_types(
    df: pd.DataFrame,
    expected_types: Dict[str, Union[str, type, List[Union[str, type]]]],
) -> Dict[str, List[str]]:
    """
    Validate DataFrame column types against expected types.

    Args:
        df: DataFrame to validate
        expected_types: Dictionary mapping column names to expected types

    Returns:
        Dictionary with validation results
    """
    validation_results = {
        "valid_columns": [],
        "invalid_columns": [],
        "type_mismatches": [],
    }

    for col_name, expected_type in expected_types.items():
        if col_name not in df.columns:
            validation_results["invalid_columns"].append(col_name)
            continue

        actual_type = df[col_name].dtype

        # Handle multiple expected types
        if isinstance(expected_type, list):
            if actual_type in expected_type:
                validation_results["valid_columns"].append(col_name)
            else:
                validation_results["type_mismatches"].append(
                    {
                        "column": col_name,
                        "expected": expected_type,
                        "actual": actual_type,
                    }
                )
        else:
            if actual_type == expected_type:
                validation_results["valid_columns"].append(col_name)
            else:
                validation_results["type_mismatches"].append(
                    {
                        "column": col_name,
                        "expected": expected_type,
                        "actual": actual_type,
                    }
                )

    return validation_results


def check_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Comprehensive data quality check.

    Args:
        df: DataFrame to check

    Returns:
        Dictionary with quality metrics
    """
    quality_report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": {},
        "duplicate_rows": 0,
        "data_types": {},
        "unique_values": {},
        "value_ranges": {},
        "quality_score": 0.0,
    }

    # Missing values
    missing_counts = df.isnull().sum()
    quality_report["missing_values"] = missing_counts.to_dict()

    # Duplicate rows
    quality_report["duplicate_rows"] = df.duplicated().sum()

    # Data types
    quality_report["data_types"] = df.dtypes.to_dict()

    # Unique values per column
    for col in df.columns:
        quality_report["unique_values"][col] = df[col].nunique()

    # Value ranges for numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        quality_report["value_ranges"][col] = {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "mean": float(df[col].mean()),
            "std": float(df[col].std()),
        }

    # Calculate quality score
    total_cells = len(df) * len(df.columns)
    missing_cells = sum(missing_counts)
    duplicate_penalty = quality_report["duplicate_rows"] * len(df.columns)

    quality_score = max(
        0, (total_cells - missing_cells - duplicate_penalty) / total_cells
    )
    quality_report["quality_score"] = quality_score

    return quality_report


def clean_data(
    df: pd.DataFrame,
    remove_duplicates: bool = True,
    fill_missing: bool = True,
    remove_outliers: bool = False,
    outlier_threshold: float = 3.0,
) -> pd.DataFrame:
    """
    Clean DataFrame by removing duplicates, filling missing values, etc.

    Args:
        df: DataFrame to clean
        remove_duplicates: Whether to remove duplicate rows
        fill_missing: Whether to fill missing values
        remove_outliers: Whether to remove outliers
        outlier_threshold: Z-score threshold for outlier detection

    Returns:
        Cleaned DataFrame
    """
    cleaned_df = df.copy()

    # Remove duplicates
    if remove_duplicates:
        initial_rows = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        removed_duplicates = initial_rows - len(cleaned_df)
        if removed_duplicates > 0:
            print(f"Removed {removed_duplicates} duplicate rows")

    # Fill missing values
    if fill_missing:
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype in ["object", "category"]:
                # For categorical columns, fill with mode
                mode_value = cleaned_df[col].mode()
                if not mode_value.empty:
                    cleaned_df[col] = cleaned_df[col].fillna(mode_value.iloc[0])
            elif cleaned_df[col].dtype in ["int64", "float64"]:
                # For numeric columns, fill with median
                median_value = cleaned_df[col].median()
                cleaned_df[col] = cleaned_df[col].fillna(median_value)

    # Remove outliers
    if remove_outliers:
        numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            z_scores = np.abs(
                (cleaned_df[col] - cleaned_df[col].mean()) / cleaned_df[col].std()
            )
            outlier_mask = z_scores > outlier_threshold
            initial_rows = len(cleaned_df)
            cleaned_df = cleaned_df[~outlier_mask]
            removed_outliers = initial_rows - len(cleaned_df)
            if removed_outliers > 0:
                print(f"Removed {removed_outliers} outliers from column '{col}'")

    return cleaned_df


def validate_schema(
    df: pd.DataFrame, schema: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validate DataFrame against a schema definition.

    Args:
        df: DataFrame to validate
        schema: Schema definition with column constraints

    Returns:
        Dictionary with validation results
    """
    validation_results = {"valid": True, "errors": [], "warnings": []}

    for col_name, col_schema in schema.items():
        if col_name not in df.columns:
            validation_results["errors"].append(
                f"Required column '{col_name}' not found"
            )
            validation_results["valid"] = False
            continue

        col_data = df[col_name]

        # Check data type
        if "dtype" in col_schema:
            expected_dtype = col_schema["dtype"]
            if col_data.dtype != expected_dtype:
                validation_results["errors"].append(
                    f"Column '{col_name}' has type {col_data.dtype}, expected {expected_dtype}"
                )
                validation_results["valid"] = False

        # Check required (no missing values)
        if col_schema.get("required", False):
            if col_data.isnull().any():
                validation_results["errors"].append(
                    f"Required column '{col_name}' contains missing values"
                )
                validation_results["valid"] = False

        # Check unique constraint
        if col_schema.get("unique", False):
            if not col_data.is_unique:
                validation_results["errors"].append(
                    f"Column '{col_name}' must be unique but contains duplicates"
                )
                validation_results["valid"] = False

        # Check value range for numeric columns
        if "min_value" in col_schema and col_data.dtype in ["int64", "float64"]:
            if col_data.min() < col_schema["min_value"]:
                validation_results["warnings"].append(
                    f"Column '{col_name}' contains values below minimum {col_schema['min_value']}"
                )

        if "max_value" in col_schema and col_data.dtype in ["int64", "float64"]:
            if col_data.max() > col_schema["max_value"]:
                validation_results["warnings"].append(
                    f"Column '{col_name}' contains values above maximum {col_schema['max_value']}"
                )

        # Check pattern for string columns
        if "pattern" in col_schema and col_data.dtype == "object":
            pattern = re.compile(col_schema["pattern"])
            invalid_values = col_data[
                ~col_data.astype(str).str.match(pattern, na=False)
            ]
            if len(invalid_values) > 0:
                validation_results["warnings"].append(
                    f"Column '{col_name}' contains values that don't match pattern {col_schema['pattern']}"
                )

    return validation_results


def detect_anomalies(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = "zscore",
    threshold: float = 3.0,
) -> Dict[str, Any]:
    """
    Detect anomalies in DataFrame columns.

    Args:
        df: DataFrame to analyze
        columns: Columns to check (None for all numeric columns)
        method: Detection method ('zscore', 'iqr', 'isolation_forest')
        threshold: Threshold for anomaly detection

    Returns:
        Dictionary with anomaly detection results
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    anomaly_results = {
        "method": method,
        "threshold": threshold,
        "columns": {},
        "total_anomalies": 0,
    }

    for col in columns:
        if col not in df.columns:
            continue

        col_data = df[col].dropna()
        if len(col_data) == 0:
            continue

        anomalies = []

        if method == "zscore":
            z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
            anomaly_indices = z_scores > threshold
            anomalies = col_data[anomaly_indices].index.tolist()

        elif method == "iqr":
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            anomaly_indices = (col_data < lower_bound) | (col_data > upper_bound)
            anomalies = col_data[anomaly_indices].index.tolist()

        elif method == "isolation_forest":
            try:
                from sklearn.ensemble import IsolationForest

                # Reshape data for sklearn
                X = col_data.values.reshape(-1, 1)

                # Fit isolation forest
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                predictions = iso_forest.fit_predict(X)

                # -1 indicates anomalies
                anomaly_indices = predictions == -1
                anomalies = col_data[anomaly_indices].index.tolist()

            except ImportError:
                anomaly_results["warnings"] = [
                    "scikit-learn not available for isolation forest method"
                ]
                continue

        anomaly_results["columns"][col] = {
            "anomaly_indices": anomalies,
            "anomaly_count": len(anomalies),
            "anomaly_percentage": (len(anomalies) / len(col_data)) * 100,
        }

        anomaly_results["total_anomalies"] += len(anomalies)

    return anomaly_results


def validate_email_format(series: pd.Series) -> pd.Series:
    """
    Validate email format in a pandas Series.

    Args:
        series: Series containing email addresses

    Returns:
        Boolean Series indicating valid emails
    """
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return series.astype(str).str.match(email_pattern, na=False)


def validate_phone_format(series: pd.Series, country_code: str = "US") -> pd.Series:
    """
    Validate phone number format in a pandas Series.

    Args:
        series: Series containing phone numbers
        country_code: Country code for phone validation

    Returns:
        Boolean Series indicating valid phone numbers
    """
    if country_code == "US":
        phone_pattern = (
            r"^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$"
        )
    else:
        # Generic international pattern
        phone_pattern = r"^\+?[1-9]\d{1,14}$"

    return series.astype(str).str.match(phone_pattern, na=False)


def validate_date_format(series: pd.Series, date_format: str = "%Y-%m-%d") -> pd.Series:
    """
    Validate date format in a pandas Series.

    Args:
        series: Series containing dates
        date_format: Expected date format

    Returns:
        Boolean Series indicating valid dates
    """

    def is_valid_date(date_str):
        try:
            pd.to_datetime(date_str, format=date_format)
            return True
        except (ValueError, TypeError):
            return False

    return series.astype(str).apply(is_valid_date)
