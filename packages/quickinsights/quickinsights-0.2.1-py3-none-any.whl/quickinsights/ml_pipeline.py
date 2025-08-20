"""
ML Pipeline Integration Module
Focused on automated machine learning pipeline creation
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
import time
import os

class MLPipelineIntegration:
    """Machine Learning Pipeline Integration for QuickInsights"""
    
    def __init__(self):
        self.pipeline_history = []
        self.performance_metrics = {}
    
    def auto_ml_pipeline(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        task_type: str = 'auto',
        test_size: float = 0.2,
        random_state: int = 42,
        save_results: bool = False,
        output_dir: str = "./quickinsights_output"
    ) -> Dict[str, Any]:
        """
        Create automated ML pipeline with intelligent preprocessing
        
        Args:
            X: Feature matrix
            y: Target variable
            task_type: 'classification', 'regression', or 'auto'
            test_size: Test set size ratio
            random_state: Random seed
            save_results: Save results to files
            output_dir: Output directory
            
        Returns:
            Dictionary with pipeline results and metrics
        """
        start_time = time.time()
        
        try:
            # Auto-detect task type
            if task_type == 'auto':
                task_type = self._detect_task_type(y)
            
            # Create intelligent pipeline
            pipeline = self._create_intelligent_pipeline(X, y, task_type)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            # Fit and evaluate pipeline
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            
            # Calculate metrics
            metrics = self._calculate_pipeline_metrics(y_test, y_pred, task_type)
            
            # Performance tracking
            execution_time = time.time() - start_time
            self.performance_metrics['execution_time'] = execution_time
            
            results = {
                'pipeline': pipeline,
                'task_type': task_type,
                'metrics': metrics,
                'performance': {
                    'execution_time': execution_time,
                    'training_samples': len(X_train),
                    'test_samples': len(X_test)
                },
                'data_info': {
                    'features': X.shape[1],
                    'samples': X.shape[0],
                    'target_distribution': self._get_target_distribution(y)
                }
            }
            
            # Save results if requested
            if save_results:
                self._save_pipeline_results(results, output_dir)
            
            return results
            
        except Exception as e:
            return {
                'error': str(e),
                'task_type': task_type,
                'execution_time': time.time() - start_time
            }
    
    def _detect_task_type(self, y: Union[np.ndarray, pd.Series]) -> str:
        """Auto-detect if task is classification or regression"""
        unique_values = len(np.unique(y))
        if unique_values <= 20:  # Threshold for classification
            return 'classification'
        return 'regression'
    
    def _create_intelligent_pipeline(self, X: Union[np.ndarray, pd.DataFrame], 
                                   y: Union[np.ndarray, pd.Series], 
                                   task_type: str) -> Pipeline:
        """Create intelligent preprocessing pipeline"""
        steps = []
        
        # Add preprocessing steps based on data characteristics
        if isinstance(X, pd.DataFrame):
            # Handle categorical columns
            categorical_cols = X.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                steps.append(('label_encoder', LabelEncoder()))
        
        # Add scaling for numerical data
        steps.append(('scaler', StandardScaler()))
        
        # Add model based on task type
        if task_type == 'classification':
            from sklearn.linear_model import LogisticRegression
            steps.append(('classifier', LogisticRegression(random_state=42, max_iter=1000)))
        else:
            from sklearn.linear_model import LinearRegression
            steps.append(('regressor', LinearRegression()))
        
        # Create pipeline
        return Pipeline(steps)
    
    def _calculate_pipeline_metrics(self, y_true: Union[np.ndarray, pd.Series], 
                                  y_pred: Union[np.ndarray, pd.Series], 
                                  task_type: str) -> Dict[str, Any]:
        """Calculate appropriate metrics for the task type"""
        if task_type == 'classification':
            return {
                'accuracy': accuracy_score(y_true, y_pred),
                'classification_report': classification_report(y_true, y_pred, output_dict=True)
            }
        else:  # regression
            from sklearn.metrics import mean_squared_error, r2_score
            return {
                'mse': mean_squared_error(y_true, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'r2': r2_score(y_true, y_pred)
            }
    
    def _get_target_distribution(self, y: Union[np.ndarray, pd.Series]) -> Dict[str, Any]:
        """Get target variable distribution information"""
        if len(np.unique(y)) <= 20:  # Classification
            unique, counts = np.unique(y, return_counts=True)
            # Convert numpy types to Python types for JSON serialization
            return {str(int(k)): int(v) for k, v in zip(unique, counts)}
        else:  # Regression
            return {
                'min': float(np.min(y)),
                'max': float(np.max(y)),
                'mean': float(np.mean(y)),
                'std': float(np.std(y))
            }
    
    def _save_pipeline_results(self, results: Dict[str, Any], output_dir: str):
        """Save pipeline results to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save pipeline info
        pipeline_info = {
            'task_type': results['task_type'],
            'metrics': results['metrics'],
            'performance': results['performance'],
            'data_info': results['data_info']
        }
        
        # Save as JSON
        import json
        with open(f"{output_dir}/ml_pipeline_results.json", 'w') as f:
            json.dump(pipeline_info, f, indent=2, default=str)

# Convenience function
def auto_ml_pipeline(*args, **kwargs):
    """Convenience function for auto_ml_pipeline"""
    ml_pipeline = MLPipelineIntegration()
    return ml_pipeline.auto_ml_pipeline(*args, **kwargs)
