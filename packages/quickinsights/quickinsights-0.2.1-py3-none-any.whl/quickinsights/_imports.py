"""
Centralized import management for QuickInsights library.

This module provides lazy imports and dependency checking to avoid
importing heavy libraries during package initialization.
"""

import warnings
from typing import Dict, Any, Optional

# Suppress warnings globally
warnings.filterwarnings('ignore')

# Core scientific libraries (always available)
import numpy as np
import pandas as pd

# Optional ML libraries
_ML_LIBS = {}

def get_sklearn_utils():
    """Get scikit-learn utilities if available."""
    if 'sklearn' not in _ML_LIBS:
        try:
            from sklearn.model_selection import (
                GridSearchCV, RandomizedSearchCV, cross_val_score,
                StratifiedKFold, KFold, train_test_split
            )
            from sklearn.ensemble import (
                RandomForestClassifier, RandomForestRegressor,
                GradientBoostingClassifier, GradientBoostingRegressor
            )
            from sklearn.linear_model import (
                LogisticRegression, LinearRegression,
                Ridge, Lasso, ElasticNet
            )
            from sklearn.svm import SVC, SVR
            from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
            from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
            from sklearn.naive_bayes import GaussianNB
            from sklearn.metrics import (
                accuracy_score, precision_score, recall_score, f1_score,
                mean_squared_error, r2_score, classification_report
            )
            from sklearn.preprocessing import StandardScaler, LabelEncoder
            from sklearn.feature_selection import SelectKBest, f_classif, f_regression
            from sklearn.cluster import KMeans, DBSCAN, IsolationForest
            from sklearn.decomposition import PCA
            from sklearn.metrics import silhouette_score
            
            _ML_LIBS['sklearn'] = {
                'available': True,
                'GridSearchCV': GridSearchCV,
                'RandomizedSearchCV': RandomizedSearchCV,
                'cross_val_score': cross_val_score,
                'StratifiedKFold': StratifiedKFold,
                'KFold': KFold,
                'train_test_split': train_test_split,
                'RandomForestClassifier': RandomForestClassifier,
                'RandomForestRegressor': RandomForestRegressor,
                'GradientBoostingClassifier': GradientBoostingClassifier,
                'GradientBoostingRegressor': GradientBoostingRegressor,
                'LogisticRegression': LogisticRegression,
                'LinearRegression': LinearRegression,
                'Ridge': Ridge,
                'Lasso': Lasso,
                'ElasticNet': ElasticNet,
                'SVC': SVC,
                'SVR': SVR,
                'KNeighborsClassifier': KNeighborsClassifier,
                'KNeighborsRegressor': KNeighborsRegressor,
                'DecisionTreeClassifier': DecisionTreeClassifier,
                'DecisionTreeRegressor': DecisionTreeRegressor,
                'GaussianNB': GaussianNB,
                'accuracy_score': accuracy_score,
                'precision_score': precision_score,
                'recall_score': recall_score,
                'f1_score': f1_score,
                'mean_squared_error': mean_squared_error,
                'r2_score': r2_score,
                'classification_report': classification_report,
                'StandardScaler': StandardScaler,
                'LabelEncoder': LabelEncoder,
                'SelectKBest': SelectKBest,
                'f_classif': f_classif,
                'f_regression': f_regression,
                'KMeans': KMeans,
                'DBSCAN': DBSCAN,
                'IsolationForest': IsolationForest,
                'PCA': PCA,
                'silhouette_score': silhouette_score
            }
        except ImportError:
            _ML_LIBS['sklearn'] = {'available': False}
    
    return _ML_LIBS['sklearn']

def get_torch_utils():
    """Get PyTorch utilities if available."""
    if 'torch' not in _ML_LIBS:
        try:
            import torch
            import torch.nn as nn
            import torch.optim as optim
            from torch.utils.data import DataLoader, TensorDataset
            
            _ML_LIBS['torch'] = {
                'available': True,
                'torch': torch,
                'nn': nn,
                'optim': optim,
                'DataLoader': DataLoader,
                'TensorDataset': TensorDataset
            }
        except ImportError:
            _ML_LIBS['torch'] = {'available': False}
    
    return _ML_LIBS['torch']

def get_lightgbm_utils():
    """Get LightGBM utilities if available."""
    if 'lightgbm' not in _ML_LIBS:
        try:
            import lightgbm as lgb
            _ML_LIBS['lightgbm'] = {
                'available': True,
                'lgb': lgb
            }
        except ImportError:
            _ML_LIBS['lightgbm'] = {'available': False}
    
    return _ML_LIBS['lightgbm']

def get_xgboost_utils():
    """Get XGBoost utilities if available."""
    if 'xgboost' not in _ML_LIBS:
        try:
            import xgboost as xgb
            _ML_LIBS['xgboost'] = {
                'available': True,
                'xgb': xgb
            }
        except ImportError:
            _ML_LIBS['xgboost'] = {'available': False}
    
    return _ML_LIBS['xgboost']

def get_shap_utils():
    """Get SHAP utilities if available."""
    if 'shap' not in _ML_LIBS:
        try:
            import shap
            _ML_LIBS['shap'] = {
                'available': True,
                'shap': shap
            }
        except ImportError:
            _ML_LIBS['shap'] = {'available': False}
    
    return _ML_LIBS['shap']

def get_scipy_utils():
    """Get SciPy utilities if available."""
    if 'scipy' not in _ML_LIBS:
        try:
            from scipy import stats
            _ML_LIBS['scipy'] = {
                'available': True,
                'stats': stats
            }
        except ImportError:
            _ML_LIBS['scipy'] = {'available': False}
    
    return _ML_LIBS['scipy']

def get_dask_utils():
    """Get Dask utilities if available."""
    if 'dask' not in _ML_LIBS:
        try:
            import dask.dataframe as dd
            import dask.array as da
            from dask.distributed import Client
            
            _ML_LIBS['dask'] = {
                'available': True,
                'dd': dd,
                'da': da,
                'Client': Client
            }
        except ImportError:
            _ML_LIBS['dask'] = {'available': False}
    
    return _ML_LIBS['dask']

def get_cupy_utils():
    """Get CuPy utilities if available."""
    if 'cupy' not in _ML_LIBS:
        try:
            import cupy as cp
            _ML_LIBS['cupy'] = {
                'available': True,
                'cp': cp
            }
        except ImportError:
            _ML_LIBS['cupy'] = {'available': False}
    
    return _ML_LIBS['cupy']

def get_qiskit_utils():
    """Get Qiskit utilities if available."""
    if 'qiskit' not in _ML_LIBS:
        try:
            from qiskit import QuantumCircuit, Aer, execute
            from qiskit.quantum_info import Statevector
            from qiskit.algorithms.optimizers import SPSA
            
            _ML_LIBS['qiskit'] = {
                'available': True,
                'QuantumCircuit': QuantumCircuit,
                'Aer': Aer,
                'execute': execute,
                'Statevector': Statevector,
                'SPSA': SPSA
            }
        except ImportError:
            _ML_LIBS['qiskit'] = {'available': False}
    
    return _ML_LIBS['qiskit']

def get_plotting_utils():
    """Get plotting utilities if available."""
    if 'plotting' not in _ML_LIBS:
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            import plotly.graph_objects as go
            import plotly.express as px
            
            _ML_LIBS['plotting'] = {
                'available': True,
                'plt': plt,
                'sns': sns,
                'go': go,
                'px': px
            }
        except ImportError:
            _ML_LIBS['plotting'] = {'available': False}
    
    return _ML_LIBS['plotting']

def get_cloud_utils():
    """Get cloud utilities if available."""
    if 'cloud' not in _ML_LIBS:
        cloud_utils = {}
        
        try:
            import boto3
            cloud_utils['boto3'] = boto3
        except ImportError:
            pass
        
        try:
            from azure.storage.blob import BlobServiceClient
            cloud_utils['azure'] = BlobServiceClient
        except ImportError:
            pass
        
        try:
            from google.cloud import storage
            cloud_utils['gcp'] = storage
        except ImportError:
            pass
        
        _ML_LIBS['cloud'] = {
            'available': len(cloud_utils) > 0,
            'utils': cloud_utils
        }
    
    return _ML_LIBS['cloud']

def get_profiling_utils():
    """Get profiling utilities if available."""
    if 'profiling' not in _ML_LIBS:
        try:
            import psutil
            _ML_LIBS['profiling'] = {
                'available': True,
                'psutil': psutil
            }
        except ImportError:
            _ML_LIBS['profiling'] = {'available': False}
    
    return _ML_LIBS['profiling']

# Convenience function to check all dependencies
def check_dependencies() -> Dict[str, bool]:
    """Check availability of all optional dependencies."""
    deps = {}
    deps['sklearn'] = get_sklearn_utils()['available']
    deps['torch'] = get_torch_utils()['available']
    deps['lightgbm'] = get_lightgbm_utils()['available']
    deps['xgboost'] = get_xgboost_utils()['available']
    deps['shap'] = get_shap_utils()['available']
    deps['scipy'] = get_scipy_utils()['available']
    deps['dask'] = get_dask_utils()['available']
    deps['cupy'] = get_cupy_utils()['available']
    deps['qiskit'] = get_qiskit_utils()['available']
    deps['plotting'] = get_plotting_utils()['available']
    deps['cloud'] = get_cloud_utils()['available']
    deps['profiling'] = get_profiling_utils()['available']
    
    return deps
