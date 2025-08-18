"""
QuickInsights - Creative and Innovative Big Data Analysis Library

A Python library that goes beyond standard data analysis libraries like NumPy and Pandas,
providing creative insights, performance optimizations, and innovative features for both
large and small datasets.

Author: Eren Ata
Version: 1.0.0
"""

# Core modules
from .core import (
    analyze,
    get_data_info,
    analyze_numeric,
    analyze_categorical,
    detect_outliers,
    validate_dataframe,
    summary_stats,
    box_plots,
    create_interactive_plots,
)

from .visualizer import correlation_matrix, distribution_plots

# Utility modules with lazy loading
from .utils import (
    get_performance_utils,
    get_big_data_utils,
    get_gpu_utils,
    get_cloud_utils,
    get_validation_utils,
    get_all_utils,
    get_utility_status,
    print_utility_status,
    get_available_features,
    check_dependencies,
    get_system_info,
    create_utility_report,
)

# New modular utilities
from .performance import (
    lazy_evaluate,
    cache_result,
    parallel_process,
    chunked_process,
    memory_optimize,
    performance_profile,
    benchmark_function,
)

from .big_data import (
    process_large_file,
    stream_data,
    get_dask_status,
    get_gpu_status,
    get_memory_mapping_status,
    get_distributed_status,
    estimate_memory_usage,
    get_system_memory_info,
    check_memory_constraints,
)

from .cloud_integration import (
    get_aws_status,
    get_azure_status,
    get_gcp_status,
    upload_to_cloud,
    download_from_cloud,
    list_cloud_files,
    process_cloud_data,
)

from .data_validation import (
    validate_column_types,
    check_data_quality,
    clean_data,
    validate_schema,
    detect_anomalies,
    validate_email_format,
    validate_phone_format,
    validate_date_format,
)

# Public API
__all__ = [
    # Core analysis functions
    "analyze",
    "get_data_info",
    "analyze_numeric",
    "analyze_categorical",
    "detect_outliers",
    "validate_dataframe",
    "summary_stats",
    "box_plots",
    "create_interactive_plots",
    # Visualization functions
    "correlation_matrix",
    "distribution_plots",
    # Utility functions
    "get_performance_utils",
    "get_big_data_utils",
    "get_gpu_utils",
    "get_cloud_utils",
    "get_validation_utils",
    "get_all_utils",
    "get_utility_status",
    "print_utility_status",
    "get_available_features",
    "check_dependencies",
    "get_system_info",
    "create_utility_report",
    # Performance utilities
    "lazy_evaluate",
    "cache_result",
    "parallel_process",
    "chunked_process",
    "memory_optimize",
    "performance_profile",
    "benchmark_function",
    # Big data utilities
    "process_large_file",
    "stream_data",
    "get_dask_status",
    "get_gpu_status",
    "get_memory_mapping_status",
    "get_distributed_status",
    "estimate_memory_usage",
    "get_system_memory_info",
    "check_memory_constraints",
    # Cloud integration utilities
    "get_aws_status",
    "get_azure_status",
    "get_gcp_status",
    "upload_to_cloud",
    "download_from_cloud",
    "list_cloud_files",
    "process_cloud_data",
    # Data validation utilities
    "validate_column_types",
    "check_data_quality",
    "clean_data",
    "validate_schema",
    "detect_anomalies",
    "validate_email_format",
    "validate_phone_format",
    "validate_date_format",
]

# Version information
__version__ = "1.0.0"
__author__ = "Eren A"
__description__ = "Creative and Innovative Big Data Analysis Library"

# Initialize utility status on import
try:
    from .utils import print_utility_status

    print("🚀 QuickInsights loaded successfully!")
    print("📊 Use print_utility_status() to see available features")
except ImportError as e:
    print(f"⚠️  Warning: Some utilities may not be available: {e}")
