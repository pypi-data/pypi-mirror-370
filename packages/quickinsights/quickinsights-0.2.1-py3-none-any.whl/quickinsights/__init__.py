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

# Import management
from ._imports import check_dependencies

# Pandas integration module
from .pandas_integration import smart_group_analysis, smart_pivot_table, intelligent_merge

# NumPy integration module
from .numpy_integration import auto_math_analysis

# Scikit-learn ML integration modules
from .ml_pipeline import auto_ml_pipeline
from .feature_selection import smart_feature_selection
from .model_selection import intelligent_model_selection
from .feature_engineering import autofe_generate_features, leakage_guard_check
from .fairness import fairness_mini_audit
from .anomaly_explain import anomaly_explain

# AutoML 2.0 & Advanced AI
from .automl_v2 import (
    intelligent_model_selection as automl_model_selection,
    auto_hyperparameter_tuning,
    explainable_ai as automl_explainable_ai,
    continuous_learning,
    meta_learning_framework
)

# Few-Shot & Zero-Shot Learning
from .few_shot import (
    few_shot_classification,
    zero_shot_prediction,
    transfer_learning,
    domain_adaptation,
    meta_learning_framework as few_shot_meta_learning
)

# Explainable AI
from .explainable_ai import (
    comprehensive_explanation,
    shap_analysis,
    decision_path_analysis,
    feature_importance_analysis,
    model_interpretability_assessment,
    contrastive_explanations,
)

# Multimodal AI
from .multimodal import (
    multimodal_fusion,
    cross_modal_analysis,
    unified_embedding
)

# Neuro-Symbolic AI
from .neuro_symbolic import (
    hybrid_reasoning,
    knowledge_graph_ai,
    logical_constraints
)

# Generative AI
from .generative import (
    synthetic_data_generation,
    ai_design_tools,
    creative_intelligence
)

# Real-Time Streaming AI
from .realtime_ai import (
    real_time_analysis,
    live_predictions,
    streaming_anomaly_detection
)

# Federated Learning
from .federated import (
    privacy_preserving_ai,
    secure_aggregation,
    distributed_learning
)

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
    get_utility_status,
    print_utility_status,
    get_available_features,
    check_dependencies,
    get_system_info,
    create_utility_report,
)



# Public API
__all__ = [
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
    "autofe_generate_features",
    "leakage_guard_check",
    "fairness_mini_audit",
    "anomaly_explain",
    
    # AutoML 2.0 & Advanced AI
    "automl_model_selection",
    "auto_hyperparameter_tuning",
    "automl_explainable_ai",
    "continuous_learning",
    "meta_learning_framework",
    
    # Few-Shot & Zero-Shot Learning
    "few_shot_classification",
    "zero_shot_prediction",
    "transfer_learning",
    "domain_adaptation",
    "few_shot_meta_learning",
    
    # Explainable AI
    "comprehensive_explanation",
    "shap_analysis",
    "decision_path_analysis",
    "feature_importance_analysis",
    "model_interpretability_assessment",
    "contrastive_explanations",
    
    # Multimodal AI
    "multimodal_fusion",
    "cross_modal_analysis",
    "unified_embedding",
    
    # Neuro-Symbolic AI
    "hybrid_reasoning",
    "knowledge_graph_ai",
    "logical_constraints",
    
    # Generative AI
    "synthetic_data_generation",
    "ai_design_tools",
    "creative_intelligence",
    
    # Real-Time Streaming AI
    "real_time_analysis",
    "live_predictions",
    "streaming_anomaly_detection",
    
    # Federated Learning
    "privacy_preserving_ai",
    "secure_aggregation",
    "distributed_learning",
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

    # Utility functions
    "get_utility_status",
    "print_utility_status",
    "get_available_features",
    "check_dependencies",
    "get_system_info",
    "create_utility_report",
]

# Version information
__version__ = "0.2.0"
__author__ = "Eren A"
__description__ = "Creative and Innovative Big Data Analysis Library"

# Avoid side effects and printing at import time
