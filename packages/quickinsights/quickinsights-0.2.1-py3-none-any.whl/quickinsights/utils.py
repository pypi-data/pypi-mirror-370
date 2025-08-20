"""
Utility functions for QuickInsights library.

This module serves as a coordinator for the modular utility system.
"""

import os
import sys
import time
import json
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
import numpy as np
import pandas as pd




def get_gpu_utils():
    """Get GPU-related utility functions."""
    try:
        from .acceleration import gpu_available
        return {"gpu_status": gpu_available()}
    except ImportError:
        return {"gpu_status": {"error": "GPU utilities not available"}}

def create_output_directory(output_dir: str) -> str:
    """Create output directory if it doesn't exist."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output directory created: {output_dir}")
    return output_dir

def save_results(results: Dict[str, Any], operation_name: str, output_dir: str = "./quickinsights_output") -> str:
    """Save results to JSON file with timestamp."""
    create_output_directory(output_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{operation_name}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"💾 Results saved: {filepath}")
    return filepath

def measure_execution_time(func: Callable) -> Callable:
    """Decorator to measure execution time of functions."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    return wrapper

def validate_dataframe(df: Any) -> pd.DataFrame:
    """Validate that input is a valid DataFrame."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    return df

def get_data_info(df: pd.DataFrame) -> Dict[str, Any]:
    """Get comprehensive information about a DataFrame."""
    info = {
        "shape": df.shape,
        "dtypes": df.dtypes.to_dict(),
        "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
        "missing_values": df.isnull().sum().to_dict(),
        "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
        "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=["object", "category"]).columns.tolist(),
        "datetime_columns": df.select_dtypes(include=["datetime64"]).columns.tolist(),
        "unique_counts": {col: df[col].nunique() for col in df.columns},
        "duplicate_rows": df.duplicated().sum(),
        "duplicate_percentage": (df.duplicated().sum() / len(df)) * 100,
    }
    
    # Add summary statistics for numeric columns
    if len(info["numeric_columns"]) > 0:
        numeric_df = df[info["numeric_columns"]]
        info["numeric_summary"] = {
            "mean": numeric_df.mean().to_dict(),
            "median": numeric_df.median().to_dict(),
            "std": numeric_df.std().to_dict(),
            "min": numeric_df.min().to_dict(),
            "max": numeric_df.max().to_dict(),
        }
    
    return info

def detect_outliers(df: pd.DataFrame, columns: Optional[List[str]] = None, method: str = 'iqr') -> Dict[str, Any]:
    """Detect outliers in DataFrame columns."""
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    outliers = {}
    
    for col in columns:
        if col in df.columns and df[col].dtype in ['int64', 'float64']:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_count = outlier_mask.sum()
            outlier_percentage = (outlier_count / len(df)) * 100
            
            outliers[col] = {
                'count': outlier_count,
                'percentage': outlier_percentage,
                'indices': df[outlier_mask].index.tolist(),
                'values': df[outlier_mask][col].tolist()
            }
    
    return outliers

def get_correlation_strength(corr_value: float) -> str:
    """Get correlation strength description based on correlation value."""
    abs_corr = abs(corr_value)
    
    if abs_corr >= 0.8:
        return "Çok Güçlü"
    elif abs_corr >= 0.6:
        return "Güçlü"
    elif abs_corr >= 0.4:
        return "Orta"
    elif abs_corr >= 0.2:
        return "Zayıf"
    else:
        return "Çok Zayıf"

def make_json_serializable(obj: Any) -> Any:
    """Convert numpy/pandas objects to JSON serializable format."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj


def create_output_directory(output_dir: str) -> str:
    """
    Create output directory if it doesn't exist.

    Args:
        output_dir: Path to the output directory

    Returns:
        Path to the created directory
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Output directory created: {output_dir}")
    return output_dir


def get_correlation_strength(corr_value: float) -> str:
    """
    Get correlation strength description based on correlation value.

    Args:
        corr_value: Correlation coefficient value

    Returns:
        String description of correlation strength
    """
    abs_corr = abs(corr_value)

    if abs_corr >= 0.8:
        return "Çok Güçlü"
    elif abs_corr >= 0.6:
        return "Güçlü"
    elif abs_corr >= 0.4:
        return "Orta"
    elif abs_corr >= 0.2:
        return "Zayıf"
    else:
        return "Çok Zayıf"


def get_data_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get comprehensive information about a DataFrame.

    Args:
        df: DataFrame to analyze

    Returns:
        Dictionary with data information
    """
    info = {
        "shape": df.shape,
        "dtypes": df.dtypes.to_dict(),
        "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2,
        "missing_values": df.isnull().sum().to_dict(),
        "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
        "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
        "categorical_columns": df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist(),
        "datetime_columns": df.select_dtypes(include=["datetime64"]).columns.tolist(),
        "unique_counts": {col: df[col].nunique() for col in df.columns},
        "duplicate_rows": df.duplicated().sum(),
        "duplicate_percentage": (df.duplicated().sum() / len(df)) * 100,
    }

    # Add summary statistics for numeric columns
    if len(info["numeric_columns"]) > 0:
        numeric_df = df[info["numeric_columns"]]
        info["numeric_summary"] = {
            "mean": numeric_df.mean().to_dict(),
            "median": numeric_df.median().to_dict(),
            "std": numeric_df.std().to_dict(),
            "min": numeric_df.min().to_dict(),
            "max": numeric_df.max().to_dict(),
        }

    # Add value counts for categorical columns
    if len(info["categorical_columns"]) > 0:
        info["categorical_summary"] = {}
        for col in info["categorical_columns"]:
            value_counts = df[col].value_counts()
            info["categorical_summary"][col] = {
                "top_values": value_counts.head(5).to_dict(),
                "unique_count": value_counts.count(),
            }

    return info


def detect_outliers(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = "zscore",
    threshold: float = 3.0,
) -> pd.DataFrame:
    """
    Detect outliers in DataFrame columns.

    Args:
        df: DataFrame to analyze
        columns: Columns to check (None for all numeric columns)
        method: Detection method ('zscore', 'iqr')
        threshold: Threshold for outlier detection

    Returns:
        DataFrame with outlier flags
    """
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    outlier_df = df.copy()

    for col in columns:
        if col not in df.columns:
            continue

        col_data = df[col].dropna()
        if len(col_data) == 0:
                continue

        outlier_mask = pd.Series(False, index=df.index)

        if method == "zscore":
            z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
            outlier_indices = z_scores > threshold
            outlier_mask.loc[col_data[outlier_indices].index] = True

        elif method == "iqr":
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outlier_indices = (col_data < lower_bound) | (col_data > upper_bound)
            outlier_mask.loc[col_data[outlier_indices].index] = True

        outlier_df[f"{col}_outlier"] = outlier_mask

    return outlier_df


def get_all_utils() -> Dict[str, Any]:
    """
    Get all available utility functions.

    Returns:
        Dictionary containing all utility functions organized by category
    """
    utils = {}

    # Performance utilities
    utils.update(get_performance_utils())

    # Big data utilities
    utils.update(get_big_data_utils())

    # Cloud integration utilities
    utils.update(get_cloud_utils())

    # Data validation utilities
    utils.update(get_validation_utils())

    return utils


def get_utility_status() -> Dict[str, Dict[str, bool]]:
    """
    Get status of all utility modules.

    Returns:
        Dictionary with status information for each utility category
    """
    status = {}

    # Performance status
    try:
        from .performance import (
            get_lazy_evaluation_status,
            get_caching_status,
            get_parallel_processing_status,
            get_chunked_processing_status,
            get_memory_optimization_status,
            get_jit_compilation_status,
        )

        status["performance"] = {
            "lazy_evaluation": get_lazy_evaluation_status(),
            "caching": get_caching_status(),
            "parallel_processing": get_parallel_processing_status(),
            "chunked_processing": get_chunked_processing_status(),
            "memory_optimization": get_memory_optimization_status(),
            "jit_compilation": get_jit_compilation_status(),
        }
    except ImportError:
        status["performance"] = {"error": "Module not available"}

    # Big data status
    try:
        from .big_data import (
            get_dask_status,
            get_gpu_status,
            get_memory_mapping_status,
            get_distributed_status,
        )

        status["big_data"] = {
            "dask": get_dask_status(),
            "gpu": get_gpu_status(),
            "memory_mapping": get_memory_mapping_status(),
            "distributed": get_distributed_status(),
        }
    except ImportError:
        status["big_data"] = {"error": "Module not available"}

    # Cloud integration status
    try:
        from .cloud_integration import get_aws_status, get_azure_status, get_gcp_status

        status["cloud_integration"] = {
            "aws": get_aws_status(),
            "azure": get_azure_status(),
            "gcp": get_gcp_status(),
        }
    except ImportError:
        status["cloud_integration"] = {"error": "Module not available"}

    # Data validation status
    try:
        from .data_validation import get_validation_utils

        validation_utils = get_validation_utils()
        status["data_validation"] = {
            "available_functions": list(validation_utils.keys())
        }
    except ImportError:
        status["data_validation"] = {"error": "Module not available"}

    return status


def print_utility_status() -> None:
    """
    Print the status of all utility modules.
    """
    status = get_utility_status()

    print("🚀 QuickInsights Utility Status")
    print("=" * 50)

    for category, cat_status in status.items():
        print(f"\n📊 {category.replace('_', ' ').title()}:")

        if "error" in cat_status:
            print(f"  ❌ {cat_status['error']}")
        else:
            for feature, available in cat_status.items():
                if isinstance(available, bool):
                    status_icon = "✅" if available else "❌"
                    print(f"  {status_icon} {feature.replace('_', ' ').title()}")
                elif isinstance(available, list):
                    print(
                        f"  📋 {feature.replace('_', ' ').title()}: {len(available)} functions"
                    )
                else:
                    print(f"  ℹ️  {feature.replace('_', ' ').title()}: {available}")


def get_available_features() -> Dict[str, List[str]]:
    """
    Get list of available features by category.

    Returns:
        Dictionary with available features organized by category
    """
    features = {}

    # Core features
    features["core"] = [
        "analyze",
        "get_data_info",
        "analyze_numeric",
        "analyze_categorical",
        "detect_outliers",
        "validate_dataframe",
        "summary_stats",
        "box_plots",
        "create_interactive_plots",
    ]

    # Visualization features
    features["visualization"] = ["correlation_matrix", "distribution_plots"]

    # Performance features
    try:
        from .performance import get_performance_utils

        perf_utils = get_performance_utils()
        features["performance"] = list(perf_utils.keys())
    except ImportError:
        features["performance"] = []

    # Big data features
    try:
        from .big_data import get_big_data_utils

        big_data_utils = get_big_data_utils()
        features["big_data"] = list(big_data_utils.keys())
    except ImportError:
        features["big_data"] = []

    # Cloud integration features
    try:
        from .cloud_integration import get_cloud_utils

        cloud_utils = get_cloud_utils()
        features["cloud_integration"] = list(cloud_utils.keys())
    except ImportError:
        features["cloud_integration"] = []

    # Data validation features
    try:
        from .data_validation import get_validation_utils

        validation_utils = get_validation_utils()
        features["data_validation"] = list(validation_utils.keys())
    except ImportError:
        features["data_validation"] = []

    return features


def check_dependencies() -> Dict[str, Dict[str, bool]]:
    """
    Check availability of required dependencies.

    Returns:
        Dictionary with dependency status
    """
    dependencies = {}

    # Core dependencies
    core_deps = ["pandas", "numpy", "matplotlib"]
    dependencies["core"] = {}

    for dep in core_deps:
        try:
            __import__(dep)
            dependencies["core"][dep] = True
        except ImportError:
            dependencies["core"][dep] = False

    # Optional dependencies
    optional_deps = {
        "performance": ["numba", "joblib"],
        "big_data": ["dask", "cupy"],
        "cloud": ["boto3", "azure-storage-blob", "google-cloud-storage"],
        "ml": ["scikit-learn", "scipy"],
    }

    for category, deps in optional_deps.items():
        dependencies[category] = {}
        for dep in deps:
            try:
                __import__(dep)
                dependencies[category][dep] = True
            except ImportError:
                dependencies[category][dep] = False

    return dependencies


def get_system_info() -> Dict[str, Any]:
    """
    Get system information and capabilities.

    Returns:
        Dictionary with system information
    """
    import platform
    import psutil

    info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "cpu_count": psutil.cpu_count(),
        "memory_total_gb": psutil.virtual_memory().total / (1024**3),
        "memory_available_gb": psutil.virtual_memory().available / (1024**3),
        "disk_usage": {},
    }

    # Disk usage for current directory
    try:
        disk_usage = psutil.disk_usage(".")
        info["disk_usage"] = {
            "total_gb": disk_usage.total / (1024**3),
            "used_gb": disk_usage.used / (1024**3),
            "free_gb": disk_usage.free / (1024**3),
        }
    except Exception:
        info["disk_usage"] = {"error": "Unable to get disk usage"}

    return info


def create_utility_report() -> str:
    """
    Create a comprehensive utility report.

    Returns:
        Formatted report string
    """
    report = []
    report.append("🚀 QuickInsights Comprehensive Utility Report")
    report.append("=" * 60)

    # System information
    try:
        sys_info = get_system_info()
        report.append(f"\n💻 System Information:")
        report.append(f"  Platform: {sys_info['platform']}")
        report.append(f"  Python: {sys_info['python_version'].split()[0]}")
        report.append(f"  CPU Cores: {sys_info['cpu_count']}")
        report.append(
            f"  Memory: {sys_info['memory_total_gb']:.1f} GB total, {sys_info['memory_available_gb']:.1f} GB available"
        )

        if "error" not in sys_info["disk_usage"]:
            disk = sys_info["disk_usage"]
            report.append(
                f"  Disk: {disk['total_gb']:.1f} GB total, {disk['free_gb']:.1f} GB free"
            )
    except Exception as e:
        report.append(f"  ❌ Error getting system info: {e}")

    # Dependencies
    try:
        deps = check_dependencies()
        report.append(f"\n📦 Dependencies:")

        for category, cat_deps in deps.items():
            report.append(f"  {category.title()}:")
            for dep, available in cat_deps.items():
                status = "✅" if available else "❌"
                report.append(f"    {status} {dep}")
    except Exception as e:
        report.append(f"  ❌ Error checking dependencies: {e}")

    # Available features
    try:
        features = get_available_features()
        report.append(f"\n🔧 Available Features:")

        for category, cat_features in features.items():
            report.append(f"  {category.title()}: {len(cat_features)} functions")
            if len(cat_features) <= 5:  # Show all if few
                for feature in cat_features:
                    report.append(f"    • {feature}")
            else:  # Show first few if many
                for feature in cat_features[:3]:
                    report.append(f"    • {feature}")
                report.append(f"    ... and {len(cat_features) - 3} more")
    except Exception as e:
        report.append(f"  ❌ Error getting features: {e}")

    # Utility status
    try:
        status = get_utility_status()
        report.append(f"\n📊 Utility Status:")

        for category, cat_status in status.items():
            if "error" not in cat_status:
                available_count = sum(
                    1 for v in cat_status.values() if isinstance(v, bool) and v
                )
                total_count = sum(1 for v in cat_status.values() if isinstance(v, bool))
                report.append(
                    f"  {category.replace('_', ' ').title()}: {available_count}/{total_count} available"
                )
            else:
                report.append(
                    f"  {category.replace('_', ' ').title()}: ❌ {cat_status['error']}"
                )
    except Exception as e:
        report.append(f"  ❌ Error getting utility status: {e}")

    return "\n".join(report)
