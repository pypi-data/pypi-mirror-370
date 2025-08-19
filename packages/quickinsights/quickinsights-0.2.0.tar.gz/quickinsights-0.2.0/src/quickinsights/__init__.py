"""
QuickInsights - Creative and Innovative Big Data Analysis Library

A Python library that goes beyond standard data analysis libraries like NumPy and Pandas,
providing creative insights, performance optimizations, and innovative features for both
large and small datasets.

Author: Eren Ata
Version: 1.0.0
"""

# Core modules are intentionally NOT imported at package import time to avoid
# pulling heavy optional dependencies (e.g., matplotlib) during lightweight usage.
_CORE_AVAILABLE = False

# Pandas integration module
from .pandas_integration import smart_group_analysis, smart_pivot_table, intelligent_merge

# NumPy integration module
from .numpy_integration import auto_math_analysis

# Scikit-learn ML integration modules
from .ml_pipeline import auto_ml_pipeline
from .feature_selection import smart_feature_selection
from .model_selection import intelligent_model_selection

# Dask integration module for big data processing
from .dask_integration import smart_dask_analysis, distributed_compute, big_data_pipeline

# Neural-inspired pattern mining
from .neural_patterns import (
    neural_pattern_mining,
    autoencoder_anomaly_scores,
    sequence_signature_extract,
)

# Quantum-inspired utilities
from .quantum_insights import (
    quantum_superposition_sample,
    amplitude_pca,
    quantum_correlation_map,
    quantum_anneal_optimize,
)

# Holographic-style visualization helpers (lightweight, no heavy deps required)
from .holographic_viz import (
    embed_3d_projection,
    volumetric_density_plot,
    export_vr_scene_stub,
    plotly_embed_3d,
)

# Acceleration utilities (GPU/Memory)
from .acceleration import (
    gpu_available,
    get_array_backend,
    standardize_array,
    backend_dot,
    gpu_corrcoef,
    memmap_array,
    chunked_apply,
    benchmark_backend,
)

# Visualizer is intentionally NOT imported at package import time to avoid heavy deps.
_VIS_AVAILABLE = False

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
    # Pandas integration functions
    "smart_group_analysis",
    "smart_pivot_table",
    "intelligent_merge",
    # NumPy integration functions
    "auto_math_analysis",
    # Scikit-learn ML integration functions
    "auto_ml_pipeline",
    "smart_feature_selection",
    "intelligent_model_selection",
    # Dask integration functions for big data processing
    "smart_dask_analysis",
    "distributed_compute",
    "big_data_pipeline",
    # Neural-inspired
    "neural_pattern_mining",
    "autoencoder_anomaly_scores",
    "sequence_signature_extract",
    # Quantum-inspired
    "quantum_superposition_sample",
    "amplitude_pca",
    "quantum_correlation_map",
    "quantum_anneal_optimize",
    # Holographic viz
    "embed_3d_projection",
    "volumetric_density_plot",
    "export_vr_scene_stub",
    "plotly_embed_3d",
    # Acceleration
    "gpu_available",
    "get_array_backend",
    "standardize_array",
    "backend_dot",
    "gpu_corrcoef",
    "memmap_array",
    "chunked_apply",
    "benchmark_backend",
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

# Avoid side effects and printing at import time
