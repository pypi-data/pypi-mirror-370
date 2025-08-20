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
        "infer_constraints": infer_constraints,
        "drift_radar": drift_radar,
        "export_gx_expectations": export_gx_expectations,
        "export_pydantic_model": export_pydantic_model,
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


# =====================================================================================
# Creative/Unique Capabilities
# =====================================================================================

def infer_constraints(
    df: pd.DataFrame,
    max_categories: int = 25,
    detect_patterns: bool = True,
) -> Dict[str, Any]:
    """
    Infer column-level constraints from data (schema-by-example).

    Returns a compact contract describing each column's inferred:
    - dtype, nullable, uniqueness, cardinality
    - numeric stats (min, max, mean, std)
    - categorical domain (top categories)
    - pattern hints (email/phone/date) when detect_patterns=True

    This helps auto-generate validation rules without manual specs.
    """
    df = validate_dataframe(df)

    profile: Dict[str, Any] = {
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
        "columns": {},
    }

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    for col in df.columns:
        series = df[col]
        col_info: Dict[str, Any] = {
            "dtype": str(series.dtype),
            "nullable": bool(series.isnull().any()),
            "unique": bool(series.is_unique),
            "cardinality": int(series.nunique(dropna=True)),
        }

        if col in numeric_cols:
            s = series.dropna().astype(float)
            if len(s) > 0:
                col_info.update(
                    {
                        "min": float(np.min(s)),
                        "max": float(np.max(s)),
                        "mean": float(np.mean(s)),
                        "std": float(np.std(s)),
                        "monotonic_increasing": bool(series.is_monotonic_increasing),
                        "monotonic_decreasing": bool(series.is_monotonic_decreasing),
                    }
                )
        else:
            # Categorical-like
            value_counts = series.value_counts(dropna=True)
            top_cats = value_counts.head(max_categories)
            col_info.update(
                {
                    "top_categories": top_cats.index.astype(str).tolist(),
                    "top_category_counts": top_cats.astype(int).tolist(),
                }
            )

            if detect_patterns:
                # Heuristics for common patterns
                sample = series.dropna().astype(str).head(100)
                looks_like_email = bool(sample.str.contains(r"@.+\.").mean() > 0.7) if len(sample) else False
                looks_like_phone = bool(sample.str.fullmatch(r"\+?[0-9\-().\s]{7,}").mean() > 0.7) if len(sample) else False
                looks_like_date = False
                try:
                    if len(sample) > 0:
                        ok_ratio = pd.to_datetime(sample, errors="coerce").notna().mean()
                        looks_like_date = bool(ok_ratio > 0.7)
                except Exception:
                    pass
                col_info.update(
                    {
                        "pattern_hints": {
                            "email": looks_like_email,
                            "phone": looks_like_phone,
                            "date": looks_like_date,
                        }
                    }
                )

        profile["columns"][col] = col_info

    # Lightweight overall contract
    profile["contract"] = {
        col: {
            "dtype": info["dtype"],
            "nullable": info["nullable"],
            "unique": info["unique"],
            "min": info.get("min"),
            "max": info.get("max"),
            "domain": info.get("top_categories"),
        }
        for col, info in profile["columns"].items()
    }

    return profile


def drift_radar(
    base_df: pd.DataFrame,
    current_df: pd.DataFrame,
    bins: int = 10,
    top_k_categories: int = 20,
    segment_by: Optional[str] = None,
    psi_thresholds: Tuple[float, float] = (0.25, 0.5),
    parallel: bool = True,
    max_workers: Optional[int] = None,
    sample_rows: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Detect schema and distribution drift between a baseline dataset and a current dataset.

    - Numeric: PSI (Population Stability Index), KS-test (if SciPy available)
    - Categorical: PSI over top-K categories, unseen/vanished category tracking

    Returns per-column drift metrics and overall risk level.
    """
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed

    t0 = time.time()

    base_df = validate_dataframe(base_df)
    current_df = validate_dataframe(current_df)

    # Optional sampling for performance on very large datasets
    if sample_rows is not None:
        if len(base_df) > sample_rows:
            base_df = base_df.sample(n=sample_rows, random_state=42)
        if len(current_df) > sample_rows:
            current_df = current_df.sample(n=sample_rows, random_state=42)

    results: Dict[str, Any] = {
        "n_base": int(len(base_df)),
        "n_current": int(len(current_df)),
        "columns": {},
        "overall_risk": "low",
        "alerts": [],
    }

    # Optional stats
    try:
        from scipy import stats  # type: ignore
        SCIPY = True
    except Exception:
        SCIPY = False

    def _psi(expected: np.ndarray, actual: np.ndarray) -> float:
        # Add epsilon to avoid log(0)
        eps = 1e-12
        expected = np.clip(expected, eps, 1)
        actual = np.clip(actual, eps, 1)
        return float(np.sum((actual - expected) * np.log(actual / expected)))

    def _jsd(p: np.ndarray, q: np.ndarray) -> float:
        eps = 1e-12
        p = np.clip(p, eps, 1)
        q = np.clip(q, eps, 1)
        p = p / p.sum()
        q = q / q.sum()
        m = 0.5 * (p + q)
        kl_pm = np.sum(p * np.log(p / m))
        kl_qm = np.sum(q * np.log(q / m))
        return float(0.5 * (kl_pm + kl_qm))

    numeric_cols = list(
        set(base_df.select_dtypes(include=[np.number]).columns).intersection(
            set(current_df.select_dtypes(include=[np.number]).columns)
        )
    )
    cat_cols = list(
        set(base_df.select_dtypes(exclude=[np.number]).columns).intersection(
            set(current_df.select_dtypes(exclude=[np.number]).columns)
        )
    )

    def _numeric_task(col: str):
        base = base_df[col].dropna().to_numpy()
        curr = current_df[col].dropna().to_numpy()
        if len(base) == 0 or len(curr) == 0:
            return col, None
        try:
            q = np.linspace(0, 1, bins + 1)
            edges = np.unique(np.quantile(base, q))
            if len(edges) < 2:
                return col, None
            base_hist, _ = np.histogram(base, bins=edges)
            curr_hist, _ = np.histogram(curr, bins=edges)
            base_p = base_hist / max(1, base_hist.sum())
            curr_p = curr_hist / max(1, curr_hist.sum())
            psi = _psi(base_p, curr_p)
            jsd = _jsd(base_p, curr_p)
        except Exception:
            psi = float("nan")
            jsd = float("nan")
        ks_pvalue = None
        if SCIPY:
            try:
                ks_stat, ks_pvalue = stats.ks_2samp(base, curr)  # type: ignore
                ks_pvalue = float(ks_pvalue)
            except Exception:
                ks_pvalue = None
        return col, {
            "type": "numeric",
            "psi": float(psi) if psi == psi else None,
            "jsd": float(jsd) if jsd == jsd else None,
            "ks_pvalue": ks_pvalue,
        }

    # Numeric drift (possibly parallel)
    if parallel and len(numeric_cols) > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(_numeric_task, col) for col in numeric_cols]
            for fut in as_completed(futures):
                col, val = fut.result()
                if val is not None:
                    results["columns"][col] = val
    else:
        for col in numeric_cols:
            col, val = _numeric_task(col)
            if val is not None:
                results["columns"][col] = val

    def _categorical_task(col: str):
        base_counts = base_df[col].value_counts(dropna=True).head(top_k_categories)
        curr_counts = current_df[col].value_counts(dropna=True).head(top_k_categories)
        all_keys = sorted(set(base_counts.index.astype(str)).union(set(curr_counts.index.astype(str))))
        base_vec = np.array([base_counts.get(k, 0) for k in all_keys], dtype=float)
        curr_vec = np.array([curr_counts.get(k, 0) for k in all_keys], dtype=float)
        if base_vec.sum() == 0 or curr_vec.sum() == 0:
            return col, None
        base_p = base_vec / base_vec.sum()
        curr_p = curr_vec / curr_vec.sum()
        psi = _psi(base_p, curr_p)
        jsd = _jsd(base_p, curr_p)
        unseen = [k for k in all_keys if base_counts.get(k, 0) == 0 and curr_counts.get(k, 0) > 0]
        vanished = [k for k in all_keys if base_counts.get(k, 0) > 0 and curr_counts.get(k, 0) == 0]
        return col, {
            "type": "categorical",
            "psi": float(psi),
            "jsd": float(jsd),
            "unseen_categories": unseen,
            "vanished_categories": vanished,
        }

    if parallel and len(cat_cols) > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(_categorical_task, col) for col in cat_cols]
            for fut in as_completed(futures):
                col, val = fut.result()
                if val is not None:
                    results["columns"][col] = val
    else:
        for col in cat_cols:
            col, val = _categorical_task(col)
            if val is not None:
                results["columns"][col] = val

    # Overall risk heuristic
    psis = [v.get("psi") for v in results["columns"].values() if v.get("psi") is not None]
    max_psi = max(psis) if psis else 0.0
    low_t, high_t = psi_thresholds
    if max_psi >= high_t:
        results["overall_risk"] = "high"
    elif max_psi >= low_t:
        results["overall_risk"] = "medium"
    else:
        results["overall_risk"] = "low"

    # Populate alerts for high PSI columns
    for col, info in results["columns"].items():
        psi_val = info.get("psi")
        if psi_val is None:
            continue
        jsd_val = info.get("jsd") or 0.0
        ks_p = info.get("ks_pvalue")
        if psi_val >= high_t or jsd_val >= 0.25 or (ks_p is not None and ks_p < 0.01):
            results["alerts"].append({
                "level": "high", "column": col, "psi": float(psi_val), "jsd": float(jsd_val), "ks_pvalue": ks_p
            })
        elif psi_val >= low_t or jsd_val >= 0.15 or (ks_p is not None and ks_p < 0.05):
            results["alerts"].append({
                "level": "medium", "column": col, "psi": float(psi_val), "jsd": float(jsd_val), "ks_pvalue": ks_p
            })

    # Optional segment analysis
    if segment_by is not None and segment_by in base_df.columns and segment_by in current_df.columns:
        results["segments"] = {}
        base_vals = set(base_df[segment_by].dropna().astype(str))
        curr_vals = set(current_df[segment_by].dropna().astype(str))
        common_vals = sorted(base_vals.intersection(curr_vals))
        for val in common_vals[:50]:  # safety cap
            b_seg = base_df[base_df[segment_by].astype(str) == val]
            c_seg = current_df[current_df[segment_by].astype(str) == val]
            seg_res = drift_radar(
                b_seg, c_seg, bins=bins, top_k_categories=top_k_categories, segment_by=None, psi_thresholds=psi_thresholds
            )
            results["segments"][val] = {
                "overall_risk": seg_res.get("overall_risk"),
                "max_psi": max([v.get("psi") or 0 for v in seg_res.get("columns", {}).values()] or [0.0]),
            }
            # Bubble up severe alerts
            for al in seg_res.get("alerts", []):
                if al.get("level") == "high":
                    results["alerts"].append({"level": "high", "segment_value": val, **al})

    results["timing_sec"] = round(time.time() - t0, 6)
    return results


def export_gx_expectations(
    df_or_profile: Union[pd.DataFrame, Dict[str, Any]],
    suite_name: str = "quickinsights_expectations",
    save_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a minimal Great Expectations-style expectation suite from an inferred contract.

    Note: No runtime dependency on GE; returns a JSON-serializable dict compatible with GE schema.
    """
    if isinstance(df_or_profile, pd.DataFrame):
        profile = infer_constraints(df_or_profile)
    else:
        profile = df_or_profile

    contract = profile.get("contract", {})
    expectations: List[Dict[str, Any]] = []

    for col, info in contract.items():
        # Nullable
        if not info.get("nullable", True):
            expectations.append({
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": col},
            })
        # Unique
        if info.get("unique", False):
            expectations.append({
                "expectation_type": "expect_column_values_to_be_unique",
                "kwargs": {"column": col},
            })
        # Domain
        domain = info.get("domain")
        if domain:
            expectations.append({
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {"column": col, "value_set": domain},
            })
        # Numeric ranges
        if info.get("min") is not None:
            expectations.append({
                "expectation_type": "expect_column_min_to_be_between",
                "kwargs": {"column": col, "min_value": info.get("min"), "max_value": None},
            })
        if info.get("max") is not None:
            expectations.append({
                "expectation_type": "expect_column_max_to_be_between",
                "kwargs": {"column": col, "min_value": None, "max_value": info.get("max")},
            })
        # Dtype as a soft expectation (GE type names vary across backends)
        dtype = info.get("dtype")
        if dtype:
            expectations.append({
                "expectation_type": "expect_column_values_to_be_of_type",
                "kwargs": {"column": col, "type_": str(dtype)},
            })

    suite = {
        "expectation_suite_name": suite_name,
        "expectations": expectations,
        "meta": {"created_by": "quickinsights", "source": "infer_constraints"},
    }

    if save_path:
        import json, os
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(suite, f, indent=2)

    return suite


def export_pydantic_model(
    df_or_profile: Union[pd.DataFrame, Dict[str, Any]],
    model_name: str = "QuickInsightsModel",
    include_defaults: bool = False,
) -> str:
    """
    Generate a Pydantic BaseModel source string from an inferred contract.

    Returns Python code as a string. The caller can write it to a `.py` file.
    """
    if isinstance(df_or_profile, pd.DataFrame):
        profile = infer_constraints(df_or_profile)
    else:
        profile = df_or_profile

    contract = profile.get("contract", {})

    def map_dtype(dtype_str: str) -> str:
        ds = str(dtype_str).lower()
        if any(k in ds for k in ["int", "int64", "int32"]):
            return "int"
        if any(k in ds for k in ["float", "float64", "float32", "double"]):
            return "float"
        if "bool" in ds:
            return "bool"
        return "str"

    lines: List[str] = []
    lines.append("from pydantic import BaseModel, Field")
    lines.append("from typing import Optional")
    lines.append("")
    lines.append(f"class {model_name}(BaseModel):")
    if not contract:
        lines.append("    pass")
    else:
        for col, info in contract.items():
            py_type = map_dtype(info.get("dtype", "str"))
            nullable = bool(info.get("nullable", True))
            type_expr = f"Optional[{py_type}]" if nullable else py_type
            field_args: List[str] = []
            if info.get("min") is not None:
                field_args.append(f"ge={info.get('min')}")
            if info.get("max") is not None:
                field_args.append(f"le={info.get('max')}")
            if info.get("domain"):
                # store domain in description for now
                field_args.append(f"description='domain={info.get('domain')}'")
            field_str = ", ".join(field_args)
            default = "None" if (nullable or include_defaults) else "..."
            if field_str:
                lines.append(f"    {col}: {type_expr} = Field({default}, {field_str})")
            else:
                lines.append(f"    {col}: {type_expr} = {default}")

    return "\n".join(lines)
